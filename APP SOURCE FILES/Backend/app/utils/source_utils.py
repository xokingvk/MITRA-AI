from typing import List, Dict, Any

def deduplicate_sources(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicates retrieved chunks based on source file, page number, and chunk ID."""
    seen = set()
    deduped = []
    for item in results:
        key = (item.get("source"), item.get("page"), item.get("chunk_id"))
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped

def format_context_for_prompt(results: List[Dict[str, Any]]) -> str:
    """Formats retrieved document chunks into a structured string for Gemini context."""
    if not results:
        return "[No reliable context found]"
    
    formatted_blocks = []
    for item in results:
        block = (
            f"[SOURCE DOCUMENT: {item.get('source', 'Unknown')}]\n"
            f"[PAGE: {item.get('page', 'N/A')}]\n"
            f"Content: {item.get('text', '')}"
        )
        formatted_blocks.append(block)
    
    return "\n\n".join(formatted_blocks)
