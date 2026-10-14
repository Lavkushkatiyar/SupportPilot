from app.services.embeddings import EmbeddingServices


def test_generate_embeddings() -> None:
    text = "I lost my iphone"

    embedding = EmbeddingServices.generate_embeddings(text)
    assert len(embedding) == 384
    assert all(type(value) is float for value in embedding)
