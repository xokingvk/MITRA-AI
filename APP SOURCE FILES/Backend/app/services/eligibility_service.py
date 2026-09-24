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

        gemini_result = self.gemini_service.match_confirmed_profile(profile, lang_code)
        
        raw_matches = gemini_result.get("matching_schemes", []) if isinstance(gemini_result, dict) else (gemini_result if isinstance(gemini_result, list) else [])
        missing_info = gemini_result.get("missing_information", []) if isinstance(gemini_result, dict) else []
        guidance_text = gemini_result.get("guidance_notes", "") if isinstance(gemini_result, dict) else ""

        match_items: List[SchemeMatchItem] = []
        for item in raw_matches:
            if isinstance(item, dict) and "scheme_name" in item:
                match_items.append(
                    SchemeMatchItem(
                        scheme_name=item.get("scheme_name", "Health Scheme"),
                        short_description=item.get("short_description", "Government healthcare welfare program."),
                        eligibility_status=item.get("eligibility_status", "Potentially relevant"),
                        why_it_matches=item.get("why_it_matches", "Matches confirmed demographic factors."),
                        key_benefits=item.get("key_benefits", "Financial assistance and hospital care coverage."),
                        required_documents=item.get("required_documents", ["Aadhaar Card"]),
                        source_document=item.get("source_document", "National Health Schemes Directory"),
                        page=item.get("page", 1)
                    )
                )

        if not guidance_text:
            if match_items:
                guidance_text = (
                    f"Based on your confirmed details, {len(match_items)} government health welfare program(s) may be relevant to you. "
                    f"Please verify exact enrollment guidelines at your nearest primary health center or official government portal."
                )
            else:
                guidance_text = "More information is needed to identify schemes that may be relevant to you."

        return SchemeMatchResponse(
            confirmed_profile=profile,
            matching_schemes=match_items,
            missing_information=missing_info,
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
            "pregnancy_status": request.pregnancy_status,
            "gender": request.gender,
            "occupation": request.occupation
        }
        match_resp = self.match_confirmed_profile(
            SchemeMatchRequest(confirmed_profile=profile_dict, language=request.language)
        )
        
        legacy_items = [
            OldSchemeMatchItem(
                scheme_name=m.scheme_name,
                description=m.short_description or m.key_benefits or "",
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
            missing_information=match_resp.missing_information,
            disclaimer=match_resp.disclaimer
        )
