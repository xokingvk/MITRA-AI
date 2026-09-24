from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.config import settings
from app.dependencies import get_gemini_service
from app.services.gemini_service import GeminiService

router = APIRouter(tags=["Health & Status"])

@router.get("/", summary="Root API Index")
def root_endpoint() -> Dict[str, str]:
    return {
        "title": settings.APP_NAME,
        "status": "running",
        "docs_url": "/docs",
        "health_check": "/health"
    }

@router.get("/health", summary="Application Health Check")
def health_check(
    gemini_svc: GeminiService = Depends(get_gemini_service)
) -> Dict[str, Any]:
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "architecture": "gemini-only",
        "gemini_api_configured": gemini_svc.is_configured(),
        "gemini_model": settings.GEMINI_MODEL,
        "supported_languages": [
            "en", "hi", "ta", "te", "kn", "ml", "mr", "bn", "gu"
        ]
    }
