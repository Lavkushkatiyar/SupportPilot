from pathlib import Path

import polars as pl

DATASET = Path("data/processed/apple_support_conversations.parquet")
to_write = Path("data/processed/new.json")


def load_customer_messages(dataset_path: Path) -> pl.DataFrame:
    return (
        pl.scan_parquet(dataset_path)
        .filter(pl.col("inbound"))
        .select(
            [
                "conversation_id",
                "turn_index",
                "tweet_id",
                "created_at",
                "text",
            ]
        )
        .filter(pl.col("text").is_not_null())
        .filter(pl.col("text").str.len_chars() > 0)
        .collect()
    )


def show_dataset_summary(df: pl.DataFrame) -> None:
    print("\n=== CUSTOMER MESSAGE SUMMARY ===")
    print(f"Customer messages: {df.height:,}")
    print(f"Conversations: {df['conversation_id'].n_unique():,}")

    print("\n=== SAMPLE CUSTOMER MESSAGES ===")
    print(df.select(["conversation_id", "turn_index", "text"]).head(50))


def main() -> None:
    df = load_customer_messages(DATASET)
    show_dataset_summary(df)
    df.write_json(to_write)


if __name__ == "__main__":
    main()
