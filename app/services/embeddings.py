import math
from functools import lru_cache

from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384


class EmbeddingServices:
    @staticmethod
    @lru_cache(maxsize=1)
    def get_embeddings_model() -> SentenceTransformer:
        """Load and reuse the embedding model."""
        return SentenceTransformer(MODEL_NAME)

    @staticmethod
    def generate_embeddings(text: str) -> list[float]:
        """Generate and validate a text embedding."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string.")

        model = EmbeddingServices.get_embeddings_model()
        vector = model.encode(text, convert_to_numpy=True)

        if vector.shape != (EMBEDDING_DIMENSIONS,):
            raise ValueError(
                f"Expected {EMBEDDING_DIMENSIONS} dimensions, received {vector.shape}."
            )

        embedding = [float(value) for value in vector]

        if not all(math.isfinite(value) for value in embedding):
            raise ValueError("Embedding contains non-finite values.")

        return embedding
