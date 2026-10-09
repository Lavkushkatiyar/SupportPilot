from __future__ import annotations

import argparse
from pathlib import Path
from uuid import uuid4

import polars as pl
from sqlalchemy import text

from app.db.session import SessionLocal

DEFAULT_DATASET = Path("data/processed/apple_support_conversations.parquet")


def load_dataset(dataset_path: Path, limit: int) -> pl.DataFrame:
    return (
        pl.scan_parquet(dataset_path)
        .select(
            [
                "conversation_id",
                "turn_index",
                "tweet_id",
                "author_id",
                "inbound",
                "created_at",
                "text",
            ]
        )
        .head(limit)
        .collect()
    )


def insert_data(df: pl.DataFrame) -> None:
    records = df.to_dicts()

    conversations = [
        {
            "id": uuid4(),
            "source_id": source_id,
        }
        for source_id in df["conversation_id"].unique().to_list()
    ]

    with SessionLocal.begin() as session:
        session.execute(
            text("""
                INSERT INTO conversations (id, source_id, created_at)
                VALUES (:id, :source_id, CURRENT_TIMESTAMP)
                ON CONFLICT (source_id) DO NOTHING
            """),
            conversations,
        )

        conversation_ids = (
            session.execute(
                text(
                    """
                    SELECT id, source_id
                    FROM conversations
                    WHERE source_id = ANY(:source_ids)
                    """
                ),
                {"source_ids": [record["source_id"] for record in conversations]},
            )
            .mappings()
            .all()
        )

        id_by_source = {row["source_id"]: row["id"] for row in conversation_ids}

        messages = [
            {
                "id": uuid4(),
                "conversation_id": id_by_source[record["conversation_id"]],
                "tweet_id": record["tweet_id"],
                "author_id": record["author_id"],
                "turn_index": record["turn_index"],
                "inbound": record["inbound"],
                "created_at": record["created_at"],
                "text": record["text"],
            }
            for record in records
        ]

        session.execute(
            text(
                """
                INSERT INTO messages (
                    id, 
                    conversation_id,
                    tweet_id,
                    author_id,
                    turn_index,
                    inbound,
                    created_at,
                    text
                )
                VALUES (
                    :id,
                    :conversation_id,
                    :tweet_id,
                    :author_id,
                    :turn_index,
                    :inbound,
                    :created_at,
                    :text
                )
                ON CONFLICT (tweet_id) DO NOTHING
                """
            ),
            messages,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load processed support conversations into PostgreSQL."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1_000,
        help="Maximum number of messages to load.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.limit <= 0:
        raise ValueError("--limit must be greater than zero.")

    df = load_dataset(args.dataset, args.limit)

    if df.is_empty():
        raise ValueError("The processed dataset contains no records.")

    insert_data(df)

    print(
        f"Loaded {len(df)} messages from "
        f"{df['conversation_id'].n_unique()} conversations."
    )


if __name__ == "__main__":
    main()
