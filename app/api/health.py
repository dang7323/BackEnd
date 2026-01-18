from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.head("")
def health_check():
    return {
        "status": "ok"
    }