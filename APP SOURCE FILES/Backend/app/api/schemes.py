from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from app.models.scheme_models import EligibilityCriteriaRequest, EligibilityGuidanceResponse
from app.dependencies import get_eligibility_service
from app.services.eligibility_service import EligibilityService

router = APIRouter(prefix="/api/schemes", tags=["Health Schemes & Eligibility"])

@router.get("", summary="Get available health schemes directory summary")
def get_schemes_summary() -> Dict[str, Any]:
    """Returns summary statistics of available Indian health schemes."""
    return {
        "status": "active",
        "schemes_coverage": "All Central & State Health Welfare Programs",
        "primary_schemes": [
            "Ayushman Bharat - PM-JAY",
            "AB-PMJAY Senior Citizen 70+ Coverage",
            "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
            "Janani Suraksha Yojana (JSY)",
            "Rashtriya Arogya Nidhi (RAN)",
            "State Chief Minister Health Assurance Schemes"
        ],
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
    against health scheme criteria using Gemini reasoning.
    """
    try:
        response = eligibility_service.evaluate_eligibility(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eligibility evaluation failed: {str(e)}"
        )
