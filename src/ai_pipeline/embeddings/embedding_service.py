"""
FREE embedding service using sentence-transformers.
No API key. No cost. Runs locally.
"""
from sentence_transformers import SentenceTransformer
from typing import List
from src.config.settings import get_settings
from src.utils.logger import app_logger as logger


class EmbeddingService:
    """Generate embeddings locally for FREE."""

    def __init__(self):
        settings = get_settings()
        self.model_name = settings.embedding_model

        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded! Dimension: {self.dimension}")

    def generate(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for list of texts."""
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            show_progress_bar=len(texts) > 5,
            batch_size=32,
            normalize_embeddings=True,
        )

        logger.info(f"Generated {len(embeddings)} embeddings (cost: $0.00)")
        return embeddings.tolist()

    def generate_single(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()