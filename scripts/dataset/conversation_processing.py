from pathlib import Path

import polars as pl

DATASET_PATH = Path("data/raw/twcs.csv")
BRAND = "AppleSupport"


def main() -> None:
    df = pl.read_csv(DATASET_PATH)

    conversation_columns = [
        "tweet_id",
        "author_id",
        "inbound",
        "created_at",
        "text",
        "response_tweet_id",
        "in_response_to_tweet_id",
    ]

    # AppleSupport tweets
    apple_support = df.filter(pl.col("author_id") == BRAND).select(conversation_columns)

    # All tweets used as a lookup table for parent relationships
    tweets = df.select(conversation_columns)

    # Attach the parent tweet to each AppleSupport tweet
    apple_support_with_parent = apple_support.join(
        tweets,
        left_on="in_response_to_tweet_id",
        right_on="tweet_id",
        how="left",
        suffix="_parent",
    )
    print(
        f" parent tweet to each AppleSupport tweet: {apple_support_with_parent.height}"
    )
    # Build the complete reply graph: parent -> child
    reply_edges = df.filter(pl.col("in_response_to_tweet_id").is_not_null()).select(
        [
            pl.col("in_response_to_tweet_id").alias("parent_tweet_id"),
            pl.col("tweet_id").alias("child_tweet_id"),
        ]
    )

    # Keep only edges where AppleSupport is the child
    apple_support_edges = (
        reply_edges.join(
            df.select(
                [
                    pl.col("tweet_id"),
                    pl.col("author_id"),
                    pl.col("inbound"),
                ]
            ),
            left_on="child_tweet_id",
            right_on="tweet_id",
            how="inner",
        )
        .filter(pl.col("author_id") == BRAND)
        .select(
            [
                "parent_tweet_id",
                "child_tweet_id",
            ]
        )
    )

    # Find tweets that directly reply to AppleSupport
    apple_support_continuations = reply_edges.join(
        apple_support.select("tweet_id"),
        left_on="parent_tweet_id",
        right_on="tweet_id",
        how="inner",
    )

    print(f"Tweets replying to AppleSupport: {apple_support_continuations.height}")

    # Validate the direction of those replies
    apple_support_continuations_with_author = apple_support_continuations.join(
        df.select(
            [
                pl.col("tweet_id"),
                pl.col("author_id"),
                pl.col("inbound"),
                pl.col("text"),
            ]
        ),
        left_on="child_tweet_id",
        right_on="tweet_id",
        how="inner",
    )

    print("\nReplies to AppleSupport by direction:")
    print(apple_support_continuations_with_author.group_by("inbound").len())

    # Find the next level of conversation after an AppleSupport reply
    conversation_edges = apple_support_edges.join(
        reply_edges,
        left_on="child_tweet_id",
        right_on="parent_tweet_id",
        how="left",
        suffix="_next",
    )

    # Validate the direction of those continuations
    conversation_continuations = conversation_edges.join(
        df.select(
            [
                pl.col("tweet_id"),
                pl.col("author_id"),
                pl.col("inbound"),
            ]
        ),
        left_on="child_tweet_id_next",
        right_on="tweet_id",
        how="inner",
    )

    print("\nAppleSupport conversation continuation directions:")
    print(conversation_continuations.group_by("inbound").len())


if __name__ == "__main__":
    main()
