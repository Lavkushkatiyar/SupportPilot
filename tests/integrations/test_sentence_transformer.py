import math

from sentence_transformers import SentenceTransformer


def test_sentence_transformer_generates_valid_embedding() -> None:
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    embedding = model.encode(
        "My iPhone freezes after the latest iOS update.",
        convert_to_numpy=True,
    )

    assert embedding.shape == (384,)
    assert all(math.isfinite(float(value)) for value in embedding)
