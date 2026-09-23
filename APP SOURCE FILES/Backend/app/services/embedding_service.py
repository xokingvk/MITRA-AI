import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
            cls._instance.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        return cls._instance

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encodes a list of text strings into normalized L2 embeddings."""
        if not texts:
            return np.empty((0, 384), dtype=np.float32)
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings.astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        """Encodes a single query string into a 2D float32 numpy array."""
        return self.encode([query])
