from datetime import UTC, datetime, timedelta
from pathlib import Path

import polars as pl

OUTPUT_PATH = Path("data/ci/synthetic_conversations.parquet")


def create_dataset() -> pl.DataFrame:
    base_time = datetime(2026, 1, 1, tzinfo=UTC)

    records = [
        {
            "conversation_id": 900001,
            "turn_index": 0,
            "tweet_id": 900000000000000001,
            "author_id": 10001,
            "inbound": True,
            "created_at": base_time,
            "text": "My Apple device will not connect to Wi-Fi.",
        },
        {
            "conversation_id": 900001,
            "turn_index": 1,
            "tweet_id": 900000000000000002,
            "author_id": 10002,
            "inbound": False,
            "created_at": base_time + timedelta(minutes=2),
            "text": "Please restart your device and router.",
        },
        {
            "conversation_id": 900001,
            "turn_index": 2,
            "tweet_id": 900000000000000003,
            "author_id": 10001,
            "inbound": True,
            "created_at": base_time + timedelta(minutes=5),
            "text": "Restarting the router fixed the connection.",
        },
        {
            "conversation_id": 900002,
            "turn_index": 0,
            "tweet_id": 900000000000000004,
            "author_id": 10003,
            "inbound": True,
            "created_at": base_time + timedelta(hours=1),
            "text": "I cannot update my device software.",
        },
        {
            "conversation_id": 900002,
            "turn_index": 1,
            "tweet_id": 900000000000000005,
            "author_id": 10002,
            "inbound": False,
            "created_at": base_time + timedelta(hours=1, minutes=3),
            "text": "Check your available storage and internet connection.",
        },
    ]

    return pl.DataFrame(
        records,
        schema={
            "conversation_id": pl.Int64,
            "turn_index": pl.Int64,
            "tweet_id": pl.Int64,
            "author_id": pl.Int64,
            "inbound": pl.Boolean,
            "created_at": pl.Datetime("us", "UTC"),
            "text": pl.String,
        },
    )


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    dataset = create_dataset()
    dataset.write_parquet(OUTPUT_PATH)

    print(f"Created {len(dataset)} synthetic messages at {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
