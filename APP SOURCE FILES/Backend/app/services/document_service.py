import os
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

from app.config import settings
from app.utils.pdf_utils import process_pdf_into_chunks, extract_pdf_pages
from app.services.retrieval_service import RetrievalService
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, retrieval_service: RetrievalService):
        self.retrieval_service = retrieval_service
        self.perm_dir = Path(settings.PERMANENT_DOCUMENT_PATH)
        self.temp_dir = Path(settings.TEMPORARY_DOCUMENT_PATH)
        
        self.perm_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Ephemeral temporary document store: document_id -> text content
        self.temp_docs_cache: Dict[str, Dict[str, Any]] = {}

    def ingest_permanent_documents(self) -> Tuple[List[str], int, int]:
        """Scans permanent_documents directory, processes PDFs, builds FAISS index."""
        pdf_files = list(self.perm_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.perm_dir}")
            return [], 0, 0

        all_chunks = []
        total_pages = 0
        processed_files = []

        for pdf_path in pdf_files:
            logger.info(f"Ingesting permanent document: {pdf_path.name}")
            try:
                pages = extract_pdf_pages(str(pdf_path))
                total_pages += len(pages)
                
                chunks = process_pdf_into_chunks(str(pdf_path))
                all_chunks.extend(chunks)
                processed_files.append(pdf_path.name)
            except Exception as e:
                logger.error(f"Error processing document {pdf_path.name}: {str(e)}")

        if not all_chunks:
            raise DocumentProcessingError("No valid text could be extracted from permanent documents.")

        logger.info(f"Building vector store for {len(all_chunks)} total chunks across {len(processed_files)} files...")
        vector_count = self.retrieval_service.build_index(all_chunks)

        return processed_files, total_pages, vector_count

    def process_temporary_user_document(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Processes a temporary personal document (income certificate, age proof, etc.).
        CRITICAL RULE: Temporary documents are stored ephemerally and NEVER appended to permanent FAISS index.
        """
        if not filename.lower().endswith((".pdf", ".txt")):
            raise DocumentProcessingError("Only PDF and TXT temporary documents are currently supported.")

        doc_id = str(uuid.uuid4())
        file_path = self.temp_dir / f"{doc_id}_{filename}"

        try:
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            extracted_text = ""
            pages_count = 1
            chunks_count = 0

            if filename.lower().endswith(".pdf"):
                pages = extract_pdf_pages(str(file_path))
                pages_count = len(pages)
                extracted_text = "\n\n".join(p["text"] for p in pages)
                chunks = process_pdf_into_chunks(str(file_path))
                chunks_count = len(chunks)
            else:
                extracted_text = file_bytes.decode("utf-8", errors="ignore")
                chunks_count = 1

            doc_info = {
                "document_id": doc_id,
                "filename": filename,
                "file_path": str(file_path),
                "pages_extracted": pages_count,
                "chunks_count": chunks_count,
                "text": extracted_text,
                "is_temporary": True
            }

            self.temp_docs_cache[doc_id] = doc_info
            logger.info(f"Temporary document processed (ID: {doc_id}, File: {filename}). Permanent index UNCHANGED.")
            return doc_info

        except Exception as e:
            logger.error(f"Failed to process temporary document {filename}: {str(e)}")
            raise DocumentProcessingError(f"Temporary document processing failed: {str(e)}")

    def get_temporary_document_context(self, doc_id: str) -> str:
        """Retrieves ephemeral text context for a temporary uploaded document."""
        if not doc_id or doc_id not in self.temp_docs_cache:
            return ""
        return self.temp_docs_cache[doc_id].get("text", "")
