import os
import uuid
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from app.config import settings
from app.utils.pdf_utils import process_pdf_into_chunks, extract_pdf_pages
from app.services.retrieval_service import RetrievalService
from app.core.prompts import DOCUMENT_EXTRACTION_PROMPT
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, retrieval_service: RetrievalService, gemini_service: Optional[Any] = None):
        self.retrieval_service = retrieval_service
        self.gemini_service = gemini_service
        self.perm_dir = Path(settings.PERMANENT_DOCUMENT_PATH)
        self.temp_dir = Path(settings.TEMPORARY_DOCUMENT_PATH)
        
        self.perm_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Ephemeral temporary document store: document_id -> text content & profile
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

    def extract_structured_profile(self, text_content: str) -> Dict[str, Any]:
        """Extracts structured profile JSON using Gemini or text parsing fallback."""
        default_profile = {
            "name": None,
            "age": None,
            "date_of_birth": None,
            "gender": None,
            "address": None,
            "state": None,
            "district": None,
            "annual_income": None,
            "occupation": None,
            "disability_status": None,
            "disability_percentage": None,
            "pregnancy_status": None,
            "marital_status": None,
            "family_info": None,
            "document_type": None,
            "document_number": None,
            "summary": "Document parsed."
        }

        if not text_content or not text_content.strip():
            return default_profile

        if self.gemini_service and self.gemini_service.is_configured():
            try:
                prompt = DOCUMENT_EXTRACTION_PROMPT + text_content[:4000]
                raw_response = self.gemini_service.generate_rag_response(
                    question=prompt,
                    language_code="en",
                    context=""
                )
                
                # Parse JSON block from Gemini output
                cleaned_json = raw_response.strip()
                if "```json" in cleaned_json:
                    cleaned_json = cleaned_json.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned_json:
                    cleaned_json = cleaned_json.split("```")[1].split("```")[0].strip()

                parsed = json.loads(cleaned_json)
                if isinstance(parsed, dict):
                    # Merge with default structure
                    for k in default_profile:
                        if k in parsed:
                            default_profile[k] = parsed[k]
                    return default_profile
            except Exception as e:
                logger.warning(f"Gemini structured extraction notice ({str(e)}), falling back to regex extraction.")

        # Heuristic fallback parsing if Gemini is unavailable
        lowered = text_content.lower()
        if "patta" in lowered or "land" in lowered:
            default_profile["document_type"] = "Land Ownership Document"
        elif "aadhaar" in lowered or "uidai" in lowered:
            default_profile["document_type"] = "Aadhaar Card"
        elif "income" in lowered or "salary" in lowered:
            default_profile["document_type"] = "Income Certificate"

        return default_profile

    def process_temporary_user_document(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Processes a temporary personal document (PDF, JPG, JPEG, PNG, TXT).
        CRITICAL RULE: Uploaded user documents are ephemerally stored and NEVER ingested into the permanent FAISS scheme index.
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

            if filename.lower().endswith(".pdf"):
                pages = extract_pdf_pages(str(file_path))
                pages_count = max(len(pages), 1)
                extracted_text = "\n\n".join(p.get("text", "") for p in pages if p.get("text"))
                chunks = process_pdf_into_chunks(str(file_path))
                chunks_count = max(len(chunks), 1)
            elif filename.lower().endswith((".jpg", ".jpeg", ".png")):
                extracted_text = f"Scanned Image Document: {filename} uploaded for analysis."
            else:
                extracted_text = file_bytes.decode("utf-8", errors="ignore")

            # Perform structured profile extraction via Gemini
            extracted_profile = self.extract_structured_profile(extracted_text)

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
            logger.info(f"Temporary user document processed (ID: {doc_id}, File: {filename}). Permanent RAG index UNCHANGED.")
            return doc_info

        except Exception as e:
            logger.error(f"Failed to process temporary document {filename}: {str(e)}")
            raise DocumentProcessingError(f"Temporary document processing failed: {str(e)}")

    def get_temporary_document_context(self, doc_id: str) -> str:
        """Retrieves ephemeral text context for a temporary uploaded document."""
        if not doc_id or doc_id not in self.temp_docs_cache:
            return ""
        return self.temp_docs_cache[doc_id].get("text", "")
