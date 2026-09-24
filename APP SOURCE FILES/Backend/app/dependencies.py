from typing import Generator
from app.services.retrieval_service import RetrievalService
from app.services.gemini_service import GeminiService
from app.services.conversation_service import ConversationService
from app.services.document_service import DocumentService
from app.services.eligibility_service import EligibilityService
from app.services.rag_service import RAGService
from app.services.voice_service import VoiceService

# Singletons initialization for high efficiency across FastAPI requests
retrieval_service = RetrievalService()
gemini_service = GeminiService()
conversation_service = ConversationService()
document_service = DocumentService(retrieval_service=retrieval_service)
eligibility_service = EligibilityService(retrieval_service=retrieval_service, gemini_service=gemini_service)
rag_service = RAGService(
    retrieval_service=retrieval_service,
    gemini_service=gemini_service,
    conversation_service=conversation_service,
    document_service=document_service
)
voice_service = VoiceService()

def get_retrieval_service() -> RetrievalService:
    return retrieval_service

def get_gemini_service() -> GeminiService:
    return gemini_service

def get_conversation_service() -> ConversationService:
    return conversation_service

def get_document_service() -> DocumentService:
    return document_service

def get_eligibility_service() -> EligibilityService:
    return eligibility_service

def get_rag_service() -> RAGService:
    return rag_service

def get_voice_service() -> VoiceService:
    return voice_service
