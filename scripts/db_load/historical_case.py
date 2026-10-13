from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models.conversation import Conversation
from app.models.historical_case import HistoricalCase
from app.models.message import Message


def build_case(
    conversation: Conversation, messages: list[Message]
) -> dict[str, object] | None:
    customer_messages = [
        message.text.strip()
        for message in messages
        if message.inbound and message.text.strip()
    ]
    support_responses = [
        message.text.strip()
        for message in messages
        if not message.inbound and message.text.strip()
    ]
    if not customer_messages or not support_responses:
        return None
    return {
        "conversation_id": conversation.id,
        "customer_message": customer_messages[0],
        "support_response": "\n".join(support_responses),
        "resolution": "Outcome not recorded",
    }


def main() -> None:
    created = 0
    skipped = 0
    print("started")
    with SessionLocal.begin() as session:
        conversations = session.scalars(
            select(Conversation).options(selectinload(Conversation.messages))
        ).all()

        existing_ids = set(
            session.scalars(select(HistoricalCase.conversation_id)).all()
        )
        for conversation in conversations:
            if conversation.id in existing_ids:
                skipped += 1
                continue
            message = sorted(
                conversation.messages, key=lambda message: message.turn_index
            )
            case_data = build_case(conversation, message)
            if case_data is None:
                skipped += 1
                continue
            session.add(
                HistoricalCase(
                    **case_data,
                    created_at=conversation.created_at,
                )
            )
            created += 1

    print(f"Historical cases created: {created}")
    print(f"Conversations skipped: {skipped}")


if __name__ == "__main__":
    main()
