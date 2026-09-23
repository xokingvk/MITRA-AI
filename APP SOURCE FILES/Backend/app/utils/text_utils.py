import re

def clean_text(text: str) -> str:
    """Cleans whitespace and normalizes raw text extracted from documents."""
    if not text:
        return ""
    # Replace multiple whitespace characters (tabs, newlines, spaces) with a single space
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned

def chunk_words(text: str, chunk_size: int = 180, overlap: int = 35) -> list[str]:
    """
    Splits text into overlapping word chunks.
    chunk_size: target words per chunk
    overlap: word overlap between consecutive chunks
    """
    cleaned = clean_text(text)
    words = cleaned.split()
    if not words:
        return []
    
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks
