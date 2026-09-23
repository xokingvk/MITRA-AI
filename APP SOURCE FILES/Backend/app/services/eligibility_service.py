import logging
from typing import Dict, Any, List
from app.models.scheme_models import EligibilityCriteriaRequest, EligibilityGuidanceResponse, SchemeMatchItem
from app.services.retrieval_service import RetrievalService
from app.services.gemini_service import GeminiService
from app.core.language_config import resolve_language, DISCLAIMERS

logger = logging.getLogger(__name__)

class EligibilityService:
    def __init__(self, retrieval_service: RetrievalService, gemini_service: GeminiService):
        self.retrieval_service = retrieval_service
        self.gemini_service = gemini_service

    def evaluate_eligibility(self, request: EligibilityCriteriaRequest) -> EligibilityGuidanceResponse:
        """Evaluates health scheme eligibility based on retrieved official context."""
        lang_info = resolve_language(request.language)
        lang_code = lang_info["code"]
        lang_name = lang_info["name"]

        # Build search query from profile fields
        query_parts = ["government health schemes eligibility criteria"]
        if request.age is not None:
            query_parts.append(f"age {request.age} years")
        if request.state:
            query_parts.append(f"state {request.state}")
        if request.annual_income is not None:
            query_parts.append(f"income Rs {request.annual_income} BPL EWS")
        if request.category:
            query_parts.append(f"category {request.category}")
        if request.disability_status:
            query_parts.append("disability PwD healthcare benefits")
        if request.gender:
            query_parts.append(f"gender {request.gender} women maternity")

        search_query = " ".join(query_parts)
        retrieved_chunks = self.retrieval_service.retrieve(search_query, top_k=6)

        # Identify missing profile fields to help the user
        missing_fields = []
        if request.age is None:
            missing_fields.append("Age")
        if not request.state:
            missing_fields.append("State of Residence")
        if request.annual_income is None:
            missing_fields.append("Annual Household Income")
        if not request.category:
            missing_fields.append("Category (SC/ST/OBC/General)")

        # Prepare matching items from retrieved RAG sources
        scheme_items: List[SchemeMatchItem] = []
        seen_schemes = set()

        for chunk in retrieved_chunks:
            source_file = chunk.get("source", "health_schemes.pdf")
            page_num = chunk.get("page", 1)
            text_snippet = chunk.get("text", "")
            
            # Simple title extraction heuristics from chunk
            first_line = text_snippet.split(".")[0][:80]
            scheme_title = first_line if len(first_line) > 10 else f"Health Scheme (Page {page_num})"
            
            if scheme_title not in seen_schemes:
                seen_schemes.add(scheme_title)
                scheme_items.append(
                    SchemeMatchItem(
                        scheme_name=scheme_title,
                        description=text_snippet[:150] + "...",
                        eligibility_notes="Extracted from official document chunk for matching criteria.",
                        required_documents=["Aadhaar Card", "Ration Card / Income Certificate"],
                        source_document=source_file,
                        page=page_num
                    )
                )

        # Build guidance notes via Gemini if configured
        guidance_text = ""
        if self.gemini_service.is_configured() and retrieved_chunks:
            context_text = "\n\n".join(c.get("text", "") for c in retrieved_chunks)
            prompt = (
                f"User Profile: Age={request.age}, State={request.state}, Income={request.annual_income}, "
                f"Category={request.category}, Disability={request.disability_status}, Gender={request.gender}.\n\n"
                f"Retrieved Official Context:\n{context_text}\n\n"
                f"In simple {lang_name}, explain which government health schemes the user may be eligible for "
                f"based STRICTLY on the context. Mention required documents if specified in the text. "
                f"Explicitly state that final approval depends on official government verification."
            )
            try:
                guidance_text = self.gemini_service.generate_rag_response(
                    question=prompt,
                    language_code=lang_code,
                    context=context_text
                )
            except Exception as e:
                logger.warning(f"Failed to generate Gemini eligibility guidance: {str(e)}")
                guidance_text = f"Based on retrieved documentation, relevant scheme details were found on pages " + \
                                ", ".join(str(c.get("page")) for c in retrieved_chunks[:3]) + "."
        else:
            guidance_text = "Please refer to the matching schemes listed below from the official documentation."

        user_profile_summary = {
            "age": request.age,
            "state": request.state,
            "annual_income": request.annual_income,
            "category": request.category,
            "disability_status": request.disability_status,
            "gender": request.gender
        }

        return EligibilityGuidanceResponse(
            user_profile=user_profile_summary,
            matching_schemes=scheme_items[:4],
            guidance_notes=guidance_text,
            missing_information=missing_fields,
            disclaimer=DISCLAIMERS.get(lang_code, DISCLAIMERS["en"])
        )
