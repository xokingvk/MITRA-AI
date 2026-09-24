from fastapi import APIRouter, Depends, HTTPException, status
from app.models.chat_models import ChatRequest, ChatResponse
from app.dependencies import get_chat_service
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api", tags=["Multilingual Gemini Chat"])

@router.post("/chat", response_model=ChatResponse, summary="Send text query to MITRA AI Gemini")
def chat_endpoint(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """
    Main text chat endpoint for MITRA AI using Google Gemini.
    Processes user query in requested language (en, hi, ta, te, kn, ml, mr, bn, gu),
    and returns grounded, structured answers with safety guardrails.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message field cannot be empty."
        )

    try:
        response = chat_service.process_chat_message(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your query: {str(e)}"
        )
