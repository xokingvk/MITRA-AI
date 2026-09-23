import os
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader
from app.utils.text_utils import chunk_words
from app.core.exceptions import DocumentProcessingError

def extract_pdf_pages(pdf_path: str) -> List[Dict[str, Any]]:
    """Extracts text page-by-page from a PDF file preserving page metadata."""
    path = Path(pdf_path)
    if not path.is_file():
        raise DocumentProcessingError(f"PDF file not found at path: {pdf_path}")

    try:
        reader = PdfReader(str(path))
        pages_data = []
        for page_num, page in enumerate(reader.pages, start=1):
            extracted_text = (page.extract_text() or "").strip()
            if extracted_text:
                pages_data.append({
                    "source": path.name,
                    "page": page_num,
                    "text": extracted_text
                })
        return pages_data
    except Exception as e:
        raise DocumentProcessingError(f"Failed to process PDF file {path.name}: {str(e)}")

def process_pdf_into_chunks(pdf_path: str, chunk_size: int = 180, overlap: int = 35) -> List[Dict[str, Any]]:
    """Extracts pages and chunks them into structured metadata dictionaries."""
    pages = extract_pdf_pages(pdf_path)
    chunks = []
    for page in pages:
        page_chunks = chunk_words(page["text"], chunk_size=chunk_size, overlap=overlap)
        for idx, text_chunk in enumerate(page_chunks):
            chunks.append({
                "chunk_id": f"{page['page']}-{idx}",
                "source": page["source"],
                "page": page["page"],
                "text": text_chunk
            })
    return chunks
