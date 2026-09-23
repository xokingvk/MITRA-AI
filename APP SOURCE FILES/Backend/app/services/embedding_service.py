import logging
import gc
import numpy as np
from typing import Optional, List
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance.model = None
            cls._instance._is_loading = False
        return cls._instance

    def is_model_loaded(self) -> bool:
        """Returns True if the embedding model weights are loaded in memory."""
        return self.model is not None

    def _get_model(self):
        """Lazily loads the SentenceTransformer model on first query/encode call."""
        if self.model is None:
            logger.info(f"Lazily loading embedding model: {settings.EMBEDDING_MODEL_NAME}...")
            try:
                import torch
                # Limit PyTorch CPU threads to minimize RAM and CPU thread pool overhead
                torch.set_num_threads(1)
                if hasattr(torch, "set_num_interop_threads"):
                    try:
                        torch.set_num_interop_threads(1)
                    except Exception:
                        pass
            except ImportError:
                pass

            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info("Embedding model successfully loaded into memory.")
        return self.model

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encodes a list of text strings into normalized L2 embeddings."""
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        model = self._get_model()
        
        try:
            import torch
            with torch.no_grad():
                embeddings = model.encode(
                    texts,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False
                )
        except Exception:
            embeddings = model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )

        return embeddings.astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        """Encodes a single query string into a 2D float32 numpy array."""
        return self.encode([query])
