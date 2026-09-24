from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.models.document_models import DocumentUploadResponse, SchemeMatchRequest, SchemeMatchResponse
from app.dependencies import get_document_service, get_eligibility_service
from app.services.document_service import DocumentService
from app.services.eligibility_service import EligibilityService

router = APIRouter(prefix="/api/documents", tags=["Flow B: Temporary Document Analysis & Matching"])

@router.post("/upload", response_model=DocumentUploadResponse, summary="Upload temporary personal document for Gemini profile extraction")
async def upload_temporary_document(
    file: UploadFile = File(...),
    doc_service: DocumentService = Depends(get_document_service)
) -> DocumentUploadResponse:
    """
    Flow B: Uploads a temporary personal document (PDF, JPG, PNG, TXT).
    CRITICAL RULE: Uploaded documents are treated as temporary context for the current session and are NEVER added to the permanent FAISS scheme index.
    Extracts visible profile fields using Gemini and returns them for user confirmation.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided in upload request."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    # Enforce maximum 10MB limit
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum limit of 10MB."
        )

    try:
        doc_info = doc_service.process_temporary_user_document(file_bytes, file.filename)
        raw_text = doc_info.get("text", "").strip()
        extracted_preview = raw_text[:500] if raw_text else "Document uploaded and parsed."
        return DocumentUploadResponse(
            document_id=doc_info["document_id"],
            filename=doc_info["filename"],
            pages_extracted=doc_info["pages_extracted"],
            chunks_count=doc_info["chunks_count"],
            extracted_preview=extracted_preview,
            extracted_profile=doc_info.get("extracted_profile"),
            message="Document analyzed with Gemini. Please review and confirm your extracted profile.",
            is_temporary=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process uploaded document: {str(e)}"
        )

@router.post("/match", response_model=SchemeMatchResponse, summary="Match user-confirmed profile against permanent scheme corpus")
def match_confirmed_profile(
    request: SchemeMatchRequest,
    eligibility_service: EligibilityService = Depends(get_eligibility_service)
) -> SchemeMatchResponse:
    """
    Flow B: Accepts the final user-confirmed profile dictionary, retrieves relevant eligibility rules
    from the permanent 156 health scheme corpus, and performs Gemini scheme matching.
    """
    if not request.confirmed_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmed profile dictionary cannot be empty."
        )

    try:
        return eligibility_service.match_confirmed_profile(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to match profile against scheme corpus: {str(e)}"
        )
