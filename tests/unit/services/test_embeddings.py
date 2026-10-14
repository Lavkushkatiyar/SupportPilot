import pytest
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.historical_case import HistoricalCase
from app.services.embeddings import EmbeddingServices


def test_generate_embeddings() -> None:
    text = "I lost my iphone"

    embedding = EmbeddingServices.generate_embeddings(text)
    assert len(embedding) == 384
    assert all(type(value) is float for value in embedding)


@pytest.mark.integration
def test_embedding():
    with SessionLocal() as session:
        case = session.scalars(select(HistoricalCase)).first()

        assert case is not None, "No historical case found"

        case_embedding = case.embedding

        assert case_embedding is not None, "Embedding is missing"
        assert len(case_embedding) == 384
