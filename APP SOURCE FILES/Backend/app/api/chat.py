from fastapi import APIRouter, Depends, HTTPException, status
from app.models.chat_models import ChatRequest, ChatResponse
from app.dependencies import get_rag_service
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api", tags=["Multilingual RAG Chat"])

@router.post("/chat", response_model=ChatResponse, summary="Send text query to MITRA AI RAG")
def chat_endpoint(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> ChatResponse:
    """
    Main text chat endpoint for MITRA AI.
    Processes user query in requested language (en, hi, ta, te, kn, ml, mr, bn, gu),
    retrieves grounded health scheme facts, and returns structured answer with sources.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message field cannot be empty."
        )

    try:
        response = rag_service.process_chat_message(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your query: {str(e)}"
        )
