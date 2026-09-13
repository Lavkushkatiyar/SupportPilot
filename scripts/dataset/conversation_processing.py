from pathlib import Path

import polars as pl

from scripts.dataset.construct_conversation import ConversationBuilder

DATASET_PATH = Path("data/raw/twcs.csv")
BRAND = "AppleSupport"

PROCESSED_DATA_PATH = Path("data/processed/apple_support_conversations.parquet")


def main() -> None:
    df = pl.read_csv(DATASET_PATH)

    tweet_lookup = ConversationBuilder.build_tweet_lookup(df)

    apple_support_tweet_ids = ConversationBuilder.get_apple_support_tweet_ids(df)

    conversation_roots = ConversationBuilder.get_conversation_roots(
        tweet_ids=apple_support_tweet_ids,
        tweet_lookup=tweet_lookup,
    )

    print(f"AppleSupport tweets: {len(apple_support_tweet_ids)}")
    print(f"Unique conversation roots: {len(conversation_roots)}")

    child_lookup = ConversationBuilder.build_child_lookup(df)

    conversations = ConversationBuilder.reconstruct_all_conversations(
        conversation_roots=conversation_roots,
        tweet_lookup=tweet_lookup,
        child_lookup=child_lookup,
    )

    print(f"Reconstructed conversations: {len(conversations)}")

    conversation_lengths = [len(conversation) for conversation in conversations]

    print(f"Shortest conversation: {min(conversation_lengths)} turns")
    print(f"Longest conversation: {max(conversation_lengths)} turns")
    print(
        f"Average conversation length: "
        f"{sum(conversation_lengths) / len(conversation_lengths):.2f} turns"
    )

    valid_conversations = [
        conversation
        for conversation in conversations
        if ConversationBuilder.is_valid_conversation(
            conversation,
            BRAND,
        )
    ]

    print(f"Total conversations: {len(conversations)}")
    print(f"Valid conversations: {len(valid_conversations)}")

    processed_df = ConversationBuilder.flatten_conversations(valid_conversations)

    print(processed_df.head())
    print(f"Processed rows: {processed_df.height}")
    print(f"Processed conversations: {processed_df['conversation_id'].n_unique()}")
    processed_df = ConversationBuilder.flatten_conversations(valid_conversations)
    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    processed_df.write_parquet(PROCESSED_DATA_PATH)

    print(f"Processed dataset saved to: {PROCESSED_DATA_PATH}")
    loaded_df = pl.read_parquet(PROCESSED_DATA_PATH)

    print(f"Loaded rows: {loaded_df.height}")

    print(f"Loaded conversations: {loaded_df['conversation_id'].n_unique()}")


if __name__ == "__main__":
    main()
