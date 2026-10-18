import pytest
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.historical_case import HistoricalCase
from app.services.retrieval.retrieval import RetrievalServices


@pytest.mark.integration
def test_retrieves_relevant_battery_cases() -> None:
    customer_message = "My iPhone battery drains very quickly after updating to iOS 11."

    with SessionLocal() as session:
        cases = RetrievalServices.retrieve_similar_cases(
            session=session,
            customer_message=customer_message,
            limit=5,
        )

        assert len(cases) == 5

        # Every returned case must have an embedding.
        assert all(case.embedding is not None for case in cases)

        # At least one result should discuss battery degradation.
        battery_terms = ("battery", "drain", "drained", "power")

        assert any(
            any(term in case.customer_message.lower() for term in battery_terms)
            for case in cases
        )


@pytest.mark.integration
def test_exact_message_retrieves_original_case() -> None:
    customer_message = (
        "Experiencing some serious battery degradation issues "
        "with iOS 11.0.2 on iPhone 7. @115858 @AppleSupport "
        "#ios1102 #iphone7"
    )

    with SessionLocal() as session:
        expected_case = session.scalars(
            select(HistoricalCase).where(
                HistoricalCase.customer_message == customer_message
            )
        ).first()

        assert expected_case is not None
        assert expected_case.embedding is not None

        cases = RetrievalServices.retrieve_similar_cases(
            session=session,
            customer_message=customer_message,
            limit=5,
        )

        assert cases
        assert cases[0].id == expected_case.id
