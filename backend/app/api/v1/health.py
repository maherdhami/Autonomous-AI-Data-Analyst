from fastapi import APIRouter
from app.schemas.common import ResponseModel, HealthResponse
from app.core.config import settings
from app.core.firebase import get_firestore_client

router = APIRouter()

@router.get("/health", response_model=ResponseModel[HealthResponse])
async def health_check():
    db = get_firestore_client()
    return ResponseModel(
        success=True,
        message="System healthy",
        data=HealthResponse(
            status="healthy",
            version=settings.VERSION,
            environment=settings.ENVIRONMENT,
            firebase_connected=db is not None
        )
    )

@router.get("/status", response_model=ResponseModel[dict])
async def status_check():
    return ResponseModel(
        success=True,
        message="Service operational",
        data={
            "service": settings.PROJECT_NAME,
            "status": "online",
            "groq_configured": bool(settings.effective_groq_key)
        }
    )
