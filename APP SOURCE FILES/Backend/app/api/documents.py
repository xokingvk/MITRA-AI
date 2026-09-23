from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.models.document_models import DocumentUploadResponse
from app.dependencies import get_document_service
from app.services.document_service import DocumentService

router = APIRouter(prefix="/api/documents", tags=["Temporary Document Upload"])

@router.post("/upload", response_model=DocumentUploadResponse, summary="Upload temporary personal document for context")
async def upload_temporary_document(
    file: UploadFile = File(...),
    doc_service: DocumentService = Depends(get_document_service)
) -> DocumentUploadResponse:
    """
    Uploads a temporary personal supporting document (e.g. Income certificate, Age proof, Caste certificate).
    CRITICAL RULE: Uploaded documents are treated as temporary context for the current session and are NEVER added to the permanent FAISS scheme index.
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

        doc_info = doc_service.process_temporary_user_document(file_bytes, file.filename)
        raw_text = doc_info.get("text", "").strip()
        extracted_preview = raw_text[:500] if raw_text else "Document uploaded and parsed (no readable text extracted)."
        return DocumentUploadResponse(
            document_id=doc_info["document_id"],
            filename=doc_info["filename"],
            pages_extracted=doc_info["pages_extracted"],
            chunks_count=doc_info["chunks_count"],
            extracted_preview=extracted_preview,
            message="Document uploaded successfully and parsed as temporary session context.",
            is_temporary=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process uploaded document: {str(e)}"
        )
