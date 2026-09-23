from fastapi import APIRouter, Depends, HTTPException, status
from app.models.document_models import IngestionResponse
from app.dependencies import get_document_service
from app.services.document_service import DocumentService
from app.config import settings

router = APIRouter(prefix="/api/rag", tags=["Permanent RAG Ingestion"])

@router.post("/ingest", response_model=IngestionResponse, summary="Ingest permanent health scheme PDFs into FAISS index")
def ingest_permanent_documents(
    doc_service: DocumentService = Depends(get_document_service)
) -> IngestionResponse:
    """
    Triggers text extraction, page chunking, sentence transformer embedding,
    and FAISS index creation for all official health scheme PDFs in data/permanent_documents.
    """
    try:
        processed_files, total_pages, total_chunks = doc_service.ingest_permanent_documents()
        return IngestionResponse(
            status="success",
            documents_processed=processed_files,
            total_pages=total_pages,
            total_chunks=total_chunks,
            index_path=f"{settings.VECTOR_STORE_PATH}/faiss_index.bin"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Permanent RAG ingestion failed: {str(e)}"
        )
