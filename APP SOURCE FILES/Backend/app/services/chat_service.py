import logging
from typing import Dict, Any, List
from app.models.chat_models import ChatRequest, ChatResponse, SourceReference
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
        if intent in ["greeting", "medical_safety"]:
            static_answer = ScopeService.get_static_response(intent, lang_code)
            self.conversation_service.add_turn(conversation_id, "user", user_message)
            self.conversation_service.add_turn(conversation_id, "assistant", static_answer)
            return ChatResponse(
                answer=static_answer,
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
            answer = self.gemini_service.generate_chat_response(
                question=user_message,
                language_code=lang_code,
                history_text=history_text,
                temp_context=temp_context_str
            )
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            answer = (
                f"I am ready to assist with government health schemes. "
                f"[Note: Configure GEMINI_API_KEY in backend environment to enable full real-time Gemini generation]."
            )

        # 5. Record turn in conversation memory
        self.conversation_service.add_turn(conversation_id, "user", user_message)
        self.conversation_service.add_turn(conversation_id, "assistant", answer)

        return ChatResponse(
            answer=answer,
            language=lang_code,
            sources=sources,
            conversation_id=conversation_id,
            intent=intent,
            disclaimer=DISCLAIMERS.get(lang_code, DISCLAIMERS["en"])
        )
