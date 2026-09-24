import json
import logging
from typing import Dict, Any, List
from app.models.scheme_models import EligibilityCriteriaRequest, EligibilityGuidanceResponse, SchemeMatchItem as OldSchemeMatchItem
from app.models.document_models import SchemeMatchRequest, SchemeMatchResponse, SchemeMatchItem
from app.services.retrieval_service import RetrievalService
from app.services.gemini_service import GeminiService
from app.core.prompts import SCHEME_MATCHING_PROMPT
from app.core.language_config import resolve_language, DISCLAIMERS

logger = logging.getLogger(__name__)

class EligibilityService:
    def __init__(self, retrieval_service: RetrievalService, gemini_service: GeminiService):
        self.retrieval_service = retrieval_service
        self.gemini_service = gemini_service

    def match_confirmed_profile(self, request: SchemeMatchRequest) -> SchemeMatchResponse:
        """Flow B: Matches a user-confirmed profile dictionary against the permanent health scheme corpus via Gemini."""
        profile = request.confirmed_profile or {}
        lang_info = resolve_language(request.language or "en")
        lang_code = lang_info["code"]

        # Build RAG query from non-null profile attributes
        query_terms = ["government health scheme eligibility criteria"]
        for k, v in profile.items():
            if v is not None and v != "" and k != "summary":
                query_terms.append(f"{k} {v}")

        search_query = " ".join(query_terms)
        retrieved_chunks = self.retrieval_service.retrieve(search_query, top_k=6)
        context_text = "\n\n".join(
            f"Source: {c.get('source', 'health_schemes.pdf')} (Page {c.get('page', 1)})\nText: {c.get('text', '')}"
            for c in retrieved_chunks
        )

        match_items: List[SchemeMatchItem] = []
        guidance_text = "Based on your confirmed profile information, matching health schemes were retrieved."

        if self.gemini_service.is_configured() and retrieved_chunks:
            try:
                prompt = SCHEME_MATCHING_PROMPT.format(
                    user_profile_json=json.dumps(profile, indent=2),
                    scheme_context=context_text
                )
                raw_response = self.gemini_service.generate_rag_response(
                    question=prompt,
                    language_code=lang_code,
                    context=context_text
                )

                # Parse JSON array output from Gemini
                cleaned_json = raw_response.strip()
                if "```json" in cleaned_json:
                    cleaned_json = cleaned_json.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned_json:
                    cleaned_json = cleaned_json.split("```")[1].split("```")[0].strip()

                parsed_schemes = json.loads(cleaned_json)
                if isinstance(parsed_schemes, list):
                    for item in parsed_schemes:
                        if isinstance(item, dict) and "scheme_name" in item:
                            match_items.append(
                                SchemeMatchItem(
                                    scheme_name=item.get("scheme_name", "Health Scheme"),
                                    eligibility_status=item.get("eligibility_status", "Potentially eligible"),
                                    why_it_matches=item.get("why_it_matches", "Matches provided user parameters."),
                                    key_benefits=item.get("key_benefits", "Financial assistance & hospital coverage."),
                                    required_documents=item.get("required_documents", ["Aadhaar Card", "Ration Card"]),
                                    source_document=item.get("source_document", "MITRA_AI_156_Health_Schemes_Programs.pdf"),
                                    page=item.get("page", 1)
                                )
                            )
            except Exception as e:
                logger.warning(f"Gemini scheme matching fallback ({str(e)}). Using RAG chunk fallback.")

        # Fallback if Gemini matching failed or returned empty
        if not match_items and retrieved_chunks:
            seen = set()
            for chunk in retrieved_chunks:
                source_file = chunk.get("source", "health_schemes.pdf")
                page_num = chunk.get("page", 1)
                text_snippet = chunk.get("text", "")
                first_line = text_snippet.split(".")[0][:80]
                scheme_title = first_line if len(first_line) > 10 else f"Health Scheme (Page {page_num})"
                if scheme_title not in seen:
                    seen.add(scheme_title)
                    match_items.append(
                        SchemeMatchItem(
                            scheme_name=scheme_title,
                            eligibility_status="Potentially eligible",
                            why_it_matches="Matches search criteria in official health scheme corpus.",
                            key_benefits=text_snippet[:150] + "...",
                            required_documents=["Aadhaar Card", "Income Certificate"],
                            source_document=source_file,
                            page=page_num
                        )
                    )

        return SchemeMatchResponse(
            confirmed_profile=profile,
            matching_schemes=match_items[:5],
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
