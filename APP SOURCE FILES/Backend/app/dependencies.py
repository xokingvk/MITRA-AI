from typing import Generator
from app.services.gemini_service import GeminiService
from app.services.conversation_service import ConversationService
from app.services.document_service import DocumentService
from app.services.eligibility_service import EligibilityService
from app.services.chat_service import ChatService
from app.services.voice_service import VoiceService

# Singletons initialization for high efficiency across FastAPI requests
gemini_service = GeminiService()
conversation_service = ConversationService()
document_service = DocumentService(gemini_service=gemini_service)
eligibility_service = EligibilityService(gemini_service=gemini_service)
chat_service = ChatService(
    gemini_service=gemini_service,
    conversation_service=conversation_service,
    document_service=document_service
)
voice_service = VoiceService()

def get_gemini_service() -> GeminiService:
    return gemini_service

def get_conversation_service() -> ConversationService:
    return conversation_service

def get_document_service() -> DocumentService:
    return document_service

def get_eligibility_service() -> EligibilityService:
    return eligibility_service

def get_chat_service() -> ChatService:
    return chat_service

def get_voice_service() -> VoiceService:
    return voice_service
