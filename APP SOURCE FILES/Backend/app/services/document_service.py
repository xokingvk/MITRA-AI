import os
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from app.config import settings
from app.utils.pdf_utils import extract_pdf_pages
from app.services.gemini_service import GeminiService
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini_service = gemini_service
        self.temp_dir = Path(settings.TEMPORARY_DOCUMENT_PATH)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Ephemeral session cache: document_id -> text content & extracted profile
        self.temp_docs_cache: Dict[str, Dict[str, Any]] = {}

    def process_temporary_user_document(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Processes a temporary personal document (PDF, JPG, JPEG, PNG, TXT).
        Extracts visible profile data using Gemini vision/text understanding.
        """
        valid_exts = (".pdf", ".txt", ".jpg", ".jpeg", ".png")
        if not filename.lower().endswith(valid_exts):
            raise DocumentProcessingError(f"Unsupported file format. Allowed formats: PDF, JPG, JPEG, PNG, TXT.")

        doc_id = str(uuid.uuid4())
        file_path = self.temp_dir / f"{doc_id}_{filename}"

        try:
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            extracted_text = ""
            pages_count = 1
            chunks_count = 1
            mime_type = "text/plain"

            if filename.lower().endswith(".pdf"):
                mime_type = "application/pdf"
                pages = extract_pdf_pages(str(file_path))
                pages_count = max(len(pages), 1)
                extracted_text = "\n\n".join(p.get("text", "") for p in pages if p.get("text"))
            elif filename.lower().endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
                extracted_text = f"Uploaded image document: {filename}"
            elif filename.lower().endswith(".png"):
                mime_type = "image/png"
                extracted_text = f"Uploaded image document: {filename}"
            else:
                mime_type = "text/plain"
                extracted_text = file_bytes.decode("utf-8", errors="ignore")

            # Extract structured profile via Gemini
            extracted_profile = {}
            if self.gemini_service:
                extracted_profile = self.gemini_service.extract_profile_from_document(
                    file_bytes=file_bytes,
                    filename=filename,
                    mime_type=mime_type,
                    text_content=extracted_text
                )

            doc_info = {
                "document_id": doc_id,
                "filename": filename,
                "file_path": str(file_path),
                "pages_extracted": pages_count,
                "chunks_count": chunks_count,
                "text": extracted_text,
                "extracted_profile": extracted_profile,
                "is_temporary": True
            }

            self.temp_docs_cache[doc_id] = doc_info
            logger.info(f"Temporary user document processed successfully (ID: {doc_id}, File: {filename}).")
            return doc_info

        except Exception as e:
            logger.error(f"Failed to process temporary document {filename}: {str(e)}")
            raise DocumentProcessingError(f"Temporary document processing failed: {str(e)}")

    def get_temporary_document_context(self, doc_id: str) -> str:
        """Retrieves ephemeral text context for a temporary uploaded document."""
        if not doc_id or doc_id not in self.temp_docs_cache:
            return ""
        return self.temp_docs_cache[doc_id].get("text", "")
