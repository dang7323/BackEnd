from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.generate import router as ai_router
from app.api.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    docs_url="/docs",
    redoc_url="/redoc"
)
# CORS 설정
origins = [
    "http://localhost:5173",    # 로컬 Vite/React 기본 주소
    "http://127.0.0.1:5173",
    "https://frontend-ljx5.onrender.com", # 나중에 배포할 프론트엔드 주소도 미리 추가
]

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router)
app.include_router(ai_router)


@app.get("/")
def root():
    return {
        "message": "FastAPI is running"
    }