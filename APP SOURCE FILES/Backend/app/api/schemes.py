from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from app.models.scheme_models import EligibilityCriteriaRequest, EligibilityGuidanceResponse
from app.dependencies import get_eligibility_service, get_retrieval_service
from app.services.eligibility_service import EligibilityService
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/api/schemes", tags=["Health Schemes & Eligibility"])

@router.get("", summary="Get indexed health schemes summary")
def get_schemes_summary(
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
) -> Dict[str, Any]:
    """Returns summary statistics and metadata of indexed health schemes."""
    if not retrieval_service.is_loaded():
        retrieval_service.load_index()

    chunks = retrieval_service.chunks
    distinct_sources = sorted(list(set(c.get("source", "health_schemes.pdf") for c in chunks)))

    return {
        "status": "active",
        "total_indexed_chunks": len(chunks),
        "source_documents": distinct_sources,
        "supported_languages": [
            "English (en)", "Hindi (hi)", "Tamil (ta)", "Telugu (te)",
            "Kannada (kn)", "Malayalam (ml)", "Marathi (mr)", "Bengali (bn)", "Gujarati (gu)"
        ]
    }

@router.post("/eligibility", response_model=EligibilityGuidanceResponse, summary="Evaluate health scheme eligibility criteria")
def evaluate_eligibility_endpoint(
    request: EligibilityCriteriaRequest,
    eligibility_service: EligibilityService = Depends(get_eligibility_service)
) -> EligibilityGuidanceResponse:
    """
    Evaluates user profile criteria (age, state, income, category, disability, gender)
    against retrieved scheme criteria and returns grounded guidance.
    """
    try:
        response = eligibility_service.evaluate_eligibility(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eligibility evaluation failed: {str(e)}"
        )
