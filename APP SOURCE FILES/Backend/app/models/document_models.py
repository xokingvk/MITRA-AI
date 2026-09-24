from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

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
    extracted_preview: Optional[str] = Field(None, description="Preview of extracted text content")
    extracted_profile: Optional[Dict[str, Any]] = Field(None, description="Structured profile fields extracted from document")
    message: str = Field(..., description="Upload confirmation message")
    is_temporary: bool = Field(True, description="Indicates document is stored in temporary context")

class SchemeMatchRequest(BaseModel):
    confirmed_profile: Dict[str, Any] = Field(..., description="User-confirmed profile dictionary")
    language: Optional[str] = Field("en", description="Target response language")

class SchemeMatchItem(BaseModel):
    scheme_name: str = Field(..., description="Name of matched health scheme")
    short_description: Optional[str] = Field(None, description="One or two sentence simple description")
    eligibility_status: str = Field(..., description="Potentially relevant | Eligible | Not enough information | Not eligible")
    why_it_matches: str = Field(..., description="Detailed explanation of eligibility match/relevance")
    key_benefits: Optional[str] = Field(None, description="Summary of key health/financial benefits")
    required_documents: Optional[List[str]] = Field(default_factory=list, description="Documents required for application")
    source_document: Optional[str] = Field(None, description="Source PDF filename in RAG corpus")
    page: Optional[int] = Field(None, description="Page number in RAG corpus")

class SchemeMatchResponse(BaseModel):
    confirmed_profile: Dict[str, Any] = Field(..., description="Confirmed user profile used for matching")
    matching_schemes: List[SchemeMatchItem] = Field(default_factory=list, description="List of scheme match results")
    missing_information: List[str] = Field(default_factory=list, description="Information missing for complete scheme matching")
    guidance_notes: str = Field(..., description="Overall guidance notes from Gemini")
    disclaimer: str = Field(..., description="Official verification disclaimer")

class IngestionResponse(BaseModel):
    status: str = Field("success", description="Status of permanent RAG ingestion")
    documents_processed: List[str] = Field(..., description="List of processed document filenames")
    total_pages: int = Field(..., description="Total pages ingested across documents")
    total_chunks: int = Field(..., description="Total text chunks indexed in FAISS")
    index_path: str = Field(..., description="Saved vector store index path")
