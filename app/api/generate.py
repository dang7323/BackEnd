# --- 데이터 모델 정의 ---
import os
from http.client import HTTPException
from typing import Optional
from fastapi import APIRouter
from google import genai
from pydantic import BaseModel
from tavily import TavilyClient


router = APIRouter(
    prefix="/ai",
    tags=["Health"]
)



class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 3


class SearchResponse(BaseModel):
    query: str
    summary: str


# --- 비즈니스 로직 함수 ---
def get_search_and_summarize(query: str, max_results: int):
    # 1. Tavily 검색
    try:
        tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
        search_result = tavily_client.search(
            query=query,
            search_depth="basic",
            max_results=max_results
        )
        context_text = "\n\n".join([r['content'] for r in search_result['results']])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tavily Search Error: {e}")

    # 2. Gemini 요약
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        prompt = f"""
        당신은 정보를 종합하여 명확하게 설명해주는 AI 어시스턴트입니다.
        아래 [검색 결과]를 바탕으로 사용자의 질문에 답변해주세요.
        - 내용은 이해하기 쉽게 요약할 것.
        - 한국어로 답변할 것.

        질문: {query}
        ---
        [검색 결과]
        {context_text}
        """

        response = client.models.generate_content(
            model="models/gemini-2.5-flash",  # 모델명 확인 필요
            contents=prompt
        )
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API Error: {e}")


# --- API 엔드포인트 ---
@router.post("/generate", response_model=SearchResponse)
async def ask_question(request: SearchRequest):
    """
    사용자의 질문을 받아 웹 검색 후 요약된 답변을 반환합니다.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    summary = get_search_and_summarize(request.query, request.max_results)

    return SearchResponse(
        query=request.query,
        summary=summary
    )