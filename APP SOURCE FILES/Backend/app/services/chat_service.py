import logging
from typing import Dict, Any, List
from app.models.chat_models import ChatRequest, ChatResponse, MatchedSchemeCard, SourceReference
from app.services.gemini_service import GeminiService
from app.services.scope_service import ScopeService
from app.services.conversation_service import ConversationService
from app.services.document_service import DocumentService
from app.core.language_config import resolve_language, DISCLAIMERS

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(
        self,
        gemini_service: GeminiService,
        conversation_service: ConversationService,
        document_service: DocumentService
    ):
        self.gemini_service = gemini_service
        self.conversation_service = conversation_service
        self.document_service = document_service

    def process_chat_message(self, request: ChatRequest) -> ChatResponse:
        """Processes incoming user question via Gemini and conversation memory."""
        user_message = request.message.strip()
        lang_info = resolve_language(request.language)
        lang_code = lang_info["code"]

        # Session memory handling
        conversation_id = request.conversation_id or self.conversation_service.create_session()
        history_text = self.conversation_service.format_history_text(conversation_id)
        has_history = bool(history_text)

        # 1. Intent Classification
        intent = ScopeService.classify_intent(user_message, has_conversation_context=has_history)
        logger.info(f"Chat message intent: '{intent}' (Lang: '{lang_code}', Session: '{conversation_id}')")

        # 2. Static quick response for pure greetings or emergency safety
        if intent in ["greeting", "medical_safety", "out_of_scope"]:
            static_answer = ScopeService.get_static_response(intent, lang_code)
            if static_answer:
                self.conversation_service.add_turn(conversation_id, "user", user_message)
                self.conversation_service.add_turn(conversation_id, "assistant", static_answer)
                return ChatResponse(
                    answer=static_answer,
                    voice_answer=static_answer,
                    matched_schemes=[],
                    needs_more_information=[],
                    language=lang_code,
                    sources=[],
                    conversation_id=conversation_id,
                    intent=intent,
                    disclaimer=DISCLAIMERS.get(lang_code, DISCLAIMERS["en"])
                )

        # 3. Temporary document context if attached
        temp_context_str = ""
        if request.temp_document_id:
            temp_context_str = self.document_service.get_temporary_document_context(request.temp_document_id)

        # 4. Generate answer using Google Gemini
        sources: List[SourceReference] = []
        try:
            gemini_result = self.gemini_service.generate_chat_response(
                question=user_message,
                language_code=lang_code,
                history_text=history_text,
                temp_context=temp_context_str
            )
            
            answer_text = gemini_result.get("answer", "")
            voice_text = gemini_result.get("voice_answer", "")
            raw_schemes = gemini_result.get("matched_schemes", [])
            needs_more_info = gemini_result.get("needs_more_information", [])

            scheme_cards = []
            for sc in raw_schemes:
                if isinstance(sc, dict) and "name" in sc:
                    scheme_cards.append(
                        MatchedSchemeCard(
                            name=sc.get("name", "Health Scheme"),
                            short_description=sc.get("short_description", "Government healthcare assistance program."),
                            reason=sc.get("reason"),
                            eligibility=sc.get("eligibility"),
                            benefits=sc.get("benefits"),
                            documents=sc.get("documents", [])
                        )
                    )

        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            answer_text = (
                "Based on what you shared, some government health schemes may be relevant to you.\n\n"
                "Here are the schemes that may be relevant:\n\n"
                "1. Ayushman Bharat PM-JAY\n"
                "Cashless hospitalization up to ₹5 Lakh per family per year for secondary and tertiary healthcare.\n\n"
                "You can select a scheme to see its eligibility, benefits and required documents."
            )
            voice_text = "I found schemes that may be relevant to you. You can see them on the screen."
            scheme_cards = []
            needs_more_info = ["Annual household income", "State of residence"]

        # 5. Record turn in conversation memory
        self.conversation_service.add_turn(conversation_id, "user", user_message)
        self.conversation_service.add_turn(conversation_id, "assistant", answer_text)

        return ChatResponse(
            answer=answer_text,
            voice_answer=voice_text,
            matched_schemes=scheme_cards,
            needs_more_information=needs_more_info,
            language=lang_code,
            sources=sources,
            conversation_id=conversation_id,
            intent=intent,
            disclaimer=DISCLAIMERS.get(lang_code, DISCLAIMERS["en"])
        )
