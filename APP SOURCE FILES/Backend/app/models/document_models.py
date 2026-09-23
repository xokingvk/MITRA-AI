from pydantic import BaseModel, Field
from typing import List, Optional

class DocumentChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier, e.g. page_no-chunk_no")
    source: str = Field(..., description="Document filename")
    page: int = Field(..., description="Page number")
    text: str = Field(..., description="Extracted text chunk")

class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="Unique ID assigned to the temporary uploaded document")
    filename: str = Field(..., description="Original filename")
    pages_extracted: int = Field(..., description="Number of pages extracted")
    chunks_count: int = Field(..., description="Number of text chunks generated")
    message: str = Field(..., description="Upload confirmation message")
    is_temporary: bool = Field(True, description="Indicates document is stored in temporary context")

class IngestionResponse(BaseModel):
    status: str = Field("success", description="Status of permanent RAG ingestion")
    documents_processed: List[str] = Field(..., description="List of processed document filenames")
    total_pages: int = Field(..., description="Total pages ingested across documents")
    total_chunks: int = Field(..., description="Total text chunks indexed in FAISS")
    index_path: str = Field(..., description="Saved vector store index path")
