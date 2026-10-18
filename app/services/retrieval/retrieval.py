from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.historical_case import HistoricalCase
from app.services.retrieval.embeddings import EmbeddingServices


class RetrievalServices:
    @staticmethod
    def retrieve_similar_cases(
        session: Session, customer_message: str, limit: int = 5
    ) -> list[HistoricalCase]:
        query_embedding = EmbeddingServices.generate_embeddings(customer_message)

        query = (
            select(HistoricalCase)
            .where(HistoricalCase.embedding.is_not(None))
            .order_by(HistoricalCase.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        return list(session.scalars(query))
