import json
import logging
from typing import Dict, Any, List
from app.models.scheme_models import EligibilityCriteriaRequest, EligibilityGuidanceResponse, SchemeMatchItem as OldSchemeMatchItem
from app.models.document_models import SchemeMatchRequest, SchemeMatchResponse, SchemeMatchItem
from app.services.gemini_service import GeminiService
from app.core.language_config import resolve_language, DISCLAIMERS

logger = logging.getLogger(__name__)

class EligibilityService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    def match_confirmed_profile(self, request: SchemeMatchRequest) -> SchemeMatchResponse:
        """Flow B: Evaluates user-confirmed profile against Indian health schemes via Gemini."""
        profile = request.confirmed_profile or {}
        lang_info = resolve_language(request.language or "en")
        lang_code = lang_info["code"]

        raw_matches = self.gemini_service.match_confirmed_profile(profile, lang_code)
        
        match_items: List[SchemeMatchItem] = []
        for item in raw_matches:
            if isinstance(item, dict) and "scheme_name" in item:
                match_items.append(
                    SchemeMatchItem(
                        scheme_name=item.get("scheme_name", "Health Scheme"),
                        eligibility_status=item.get("eligibility_status", "Potentially eligible"),
                        why_it_matches=item.get("why_it_matches", "Matches confirmed demographic factors."),
                        key_benefits=item.get("key_benefits", "Financial assistance and hospital care coverage."),
                        required_documents=item.get("required_documents", ["Aadhaar Card", "Ration Card"]),
                        source_document=item.get("source_document", "National Health Schemes Directory"),
                        page=item.get("page", 1)
                    )
                )

        guidance_text = (
            f"Based on your confirmed details, {len(match_items)} relevant government health welfare programs were evaluated. "
            f"Please verify exact enrollment guidelines at your nearest primary health center or official government portal."
        )

        return SchemeMatchResponse(
            confirmed_profile=profile,
            matching_schemes=match_items,
            guidance_notes=guidance_text,
            disclaimer=DISCLAIMERS.get(lang_code, DISCLAIMERS["en"])
        )

    def evaluate_eligibility(self, request: EligibilityCriteriaRequest) -> EligibilityGuidanceResponse:
        """Legacy evaluation endpoint compatibility."""
        profile_dict = {
            "age": request.age,
            "state": request.state,
            "annual_income": request.annual_income,
            "category": request.category,
            "disability_status": request.disability_status,
            "gender": request.gender
        }
        match_resp = self.match_confirmed_profile(
            SchemeMatchRequest(confirmed_profile=profile_dict, language=request.language)
        )
        
        legacy_items = [
            OldSchemeMatchItem(
                scheme_name=m.scheme_name,
                description=m.key_benefits or "",
                eligibility_notes=m.why_it_matches,
                required_documents=m.required_documents or [],
                source_document=m.source_document or "",
                page=m.page or 1
            )
            for m in match_resp.matching_schemes
        ]

        return EligibilityGuidanceResponse(
            user_profile=profile_dict,
            matching_schemes=legacy_items,
            guidance_notes=match_resp.guidance_notes,
            missing_information=[],
            disclaimer=match_resp.disclaimer
        )
