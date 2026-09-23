import logging
from typing import Dict, Any, List
from app.models.chat_models import ChatRequest, ChatResponse, SourceReference
from app.services.retrieval_service import RetrievalService
from app.services.gemini_service import GeminiService
from app.services.scope_service import ScopeService
from app.services.conversation_service import ConversationService
from app.services.document_service import DocumentService
from app.core.language_config import resolve_language, DISCLAIMERS
from app.utils.source_utils import format_context_for_prompt

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        gemini_service: GeminiService,
        conversation_service: ConversationService,
        document_service: DocumentService
    ):
        self.retrieval_service = retrieval_service
        self.gemini_service = gemini_service
        self.conversation_service = conversation_service
        self.document_service = document_service

    def process_chat_message(self, request: ChatRequest) -> ChatResponse:
        """Master execution pipeline for incoming text chat messages."""
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

        sources: List[SourceReference] = []

        # 2. Static response handling for non-RAG intents
        if intent in ["greeting", "medical_safety", "out_of_scope"]:
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

        # 3. RAG Document Retrieval for health scheme queries & follow-ups
        retrieved_chunks = self.retrieval_service.retrieve(user_message)
        context_str = format_context_for_prompt(retrieved_chunks)

        # Temporary document context if attached
        temp_context_str = ""
        if request.temp_document_id:
            temp_context_str = self.document_service.get_temporary_document_context(request.temp_document_id)

        # Build source references list
        for chunk in retrieved_chunks:
            sources.append(
                SourceReference(
                    document=chunk.get("source", "health_schemes.pdf"),
                    page=chunk.get("page", 1),
                    score=chunk.get("score"),
                    snippet=chunk.get("text", "")[:120] + "..."
                )
            )

        # 4. Gemini Response Generation
        if not retrieved_chunks and not temp_context_str:
            answer = (
                "I could not find specific information about that in the official health scheme documentation. "
                "Please ask about available schemes, eligibility criteria, or required certificates."
                if lang_code == "en"
                else ScopeService.get_static_response("out_of_scope", lang_code)
            )
        else:
            try:
                answer = self.gemini_service.generate_rag_response(
                    question=user_message,
                    language_code=lang_code,
                    context=context_str,
                    history_text=history_text,
                    temp_context=temp_context_str
                )
            except Exception as e:
                logger.error(f"Error in Gemini response generation: {str(e)}")
                # Fallback grounded message if Gemini API key is missing or encounters errors
                answer = (
                    f"Based on the official documentation (Page {sources[0].page if sources else 1}), "
                    f"relevant scheme information was retrieved. [Note: Configure GEMINI_API_KEY in .env for full AI response synthesis]."
                )

        # 5. Record turn in memory store
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
