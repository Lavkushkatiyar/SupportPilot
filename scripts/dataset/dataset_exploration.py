from pathlib import Path

import polars as pl

DATASET_PATH = Path("data/raw/twcs.csv")


def main() -> None:
    df = pl.read_csv(DATASET_PATH)

    print(f"Rows: {df.height}")
    print(f"Columns: {df.columns}")

    print("\nSchema:")
    print(df.schema)

    print("\nFirst 5 rows:")
    print(df.head(5))

    print("\nInbound distribution:")
    print(df.group_by("inbound").len())

    print("\nTweets without a parent:")
    print(df.filter(pl.col("in_response_to_tweet_id").is_null()).height)

    print("\nTweets with a parent:")
    print(df.filter(pl.col("in_response_to_tweet_id").is_not_null()).height)


if __name__ == "__main__":
    main()
