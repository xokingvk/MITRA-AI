import logging
import gc
import numpy as np
import threading
from typing import Optional, List
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EmbeddingService, cls).__new__(cls)
                    cls._instance.model = None
                    cls._instance._is_loading = False
        return cls._instance

    def is_model_loaded(self) -> bool:
        """Returns True if the embedding model weights are loaded in memory."""
        return self.model is not None

    def load_model(self):
        """Eagerly loads the SentenceTransformer embedding model into RAM."""
        if self.model is None:
            with self._lock:
                if self.model is None:
                    logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}...")
                    try:
                        import torch
                        torch.set_num_threads(1)
                        if hasattr(torch, "set_num_interop_threads"):
                            try:
                                torch.set_num_interop_threads(1)
                            except Exception:
                                pass
                    except ImportError:
                        pass

                    from sentence_transformers import SentenceTransformer
                    try:
                        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME, local_files_only=True)
                    except Exception:
                        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
                    logger.info("Embedding model loaded successfully.")
        return self.model

    def _get_model(self):
        """Returns loaded embedding model or loads it if not already initialized."""
        return self.load_model()

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
