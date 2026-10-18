from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.historical_case import HistoricalCase
from app.services.retrieval.embeddings import EmbeddingServices

BATCH_SIZE = 1


def main() -> None:
    suceed = 0

    with SessionLocal() as session:
        cases = session.scalars(
            select(HistoricalCase).where(HistoricalCase.embedding.is_(None))
        ).all()

        for start in range(0, len(cases), BATCH_SIZE):
            batches = cases[start : start + BATCH_SIZE]
            updates = []

            for case in batches:
                try:
                    emebedding = EmbeddingServices.generate_embeddings(
                        case.customer_message
                    )

                    updates.append({"id": case.id, "embedding": emebedding})

                    print(emebedding, "embedding in the backfill")

                except Exception as e:
                    print("Embedding failed for", case.id, case.customer_message, e)

            for update_case in updates:
                case = session.get(HistoricalCase, update_case["id"])

                if case is not None:
                    case.embedding = update_case["embedding"]
                    suceed += 1

        session.commit()

    print(f"Embeddings saved: {suceed}")


if __name__ == "__main__":
    main()
