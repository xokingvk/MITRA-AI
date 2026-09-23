import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import faiss

from app.config import settings
from app.services.embedding_service import EmbeddingService
from app.core.exceptions import VectorStoreError
from app.utils.source_utils import deduplicate_sources

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self, vector_store_dir: Optional[str] = None):
        self.vector_store_dir = Path(vector_store_dir or settings.VECTOR_STORE_PATH)
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_path = self.vector_store_dir / "faiss_index.bin"
        self.metadata_path = self.vector_store_dir / "metadata.json"
        
        self.embedding_service = EmbeddingService()
        self.index: Optional[faiss.IndexFlatIP] = None
        self.chunks: List[Dict[str, Any]] = []

    def is_loaded(self) -> bool:
        """Returns True if the FAISS index and metadata are loaded into memory."""
        return self.index is not None and self.index.ntotal > 0 and len(self.chunks) > 0

    def load_index(self) -> bool:
        """Loads persistent FAISS index and metadata from disk if available."""
        if not self.index_path.exists() or not self.metadata_path.exists():
            logger.warning(f"Vector store files not found in {self.vector_store_dir}")
            return False

        try:
            logger.info(f"Loading FAISS index from {self.index_path}")
            self.index = faiss.read_index(str(self.index_path))
            
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
                
            logger.info(f"Successfully loaded FAISS index with {self.index.ntotal} vectors and {len(self.chunks)} metadata items.")
            return True
        except Exception as e:
            logger.error(f"Error loading FAISS index: {str(e)}")
            raise VectorStoreError(f"Failed to load FAISS index: {str(e)}")

    def build_index(self, chunks: List[Dict[str, Any]]) -> int:
        """Builds a new FAISS index from chunks and persists it to disk."""
        if not chunks:
            raise VectorStoreError("Cannot build vector store with empty chunks list.")

        try:
            texts = [c["text"] for c in chunks]
            logger.info(f"Generating embeddings for {len(texts)} chunks...")
            embeddings = self.embedding_service.encode(texts)

            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)
            index.add(embeddings)

            self.index = index
            self.chunks = chunks

            # Save to disk
            faiss.write_index(index, str(self.index_path))
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(chunks, f, ensure_ascii=False, indent=2)

            logger.info(f"FAISS index saved to {self.index_path} with {index.ntotal} vectors.")
            return index.ntotal
        except Exception as e:
            logger.error(f"Failed to build vector index: {str(e)}")
            raise VectorStoreError(f"Failed to build vector index: {str(e)}")

    def retrieve(self, query: str, top_k: Optional[int] = None, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Retrieves top-k matching chunks for a query from the loaded FAISS index."""
        if not self.is_loaded():
            loaded = self.load_index()
            if not loaded:
                logger.warning("Retrieval attempted on unloaded vector index with no saved index files.")
                return []

        top_k = top_k or settings.RAG_TOP_K
        threshold = threshold if threshold is not None else settings.RAG_SCORE_THRESHOLD

        try:
            query_vector = self.embedding_service.encode_query(query)
            scores, indices = self.index.search(query_vector, top_k)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self.chunks):
                    continue
                score_val = float(score)
                if score_val < threshold:
                    continue

                item = self.chunks[int(idx)].copy()
                item["score"] = round(score_val, 4)
                results.append(item)

            return deduplicate_sources(results)
        except Exception as e:
            logger.error(f"Error executing vector retrieval query: {str(e)}")
            raise VectorStoreError(f"Vector search failed: {str(e)}")
