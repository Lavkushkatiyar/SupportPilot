from pathlib import Path

import polars as pl

DATASET_PATH = Path("data/raw/twcs.csv")
BRAND = "AppleSupport"


class ConversationBuilder:
    @staticmethod
    def reconstruct_conversation(
        tweet_id: int,
        tweet_lookup: dict[int, dict],
    ) -> list[dict]:
        conversation = ConversationBuilder._walk_to_root(tweet_id, tweet_lookup)
        conversation.reverse()
        return conversation

    @staticmethod
    def find_root_tweet(
        tweet_id: int,
        tweet_lookup: dict[int, dict],
    ) -> int | None:
        """Find the root tweet ID for a conversation thread."""

        conversation = ConversationBuilder._walk_to_root(
            tweet_id=tweet_id,
            tweet_lookup=tweet_lookup,
        )

        if not conversation:
            return None

        return conversation[-1]["tweet_id"]

    @staticmethod
    def build_tweet_lookup(df: pl.DataFrame) -> dict[int, dict]:
        """Build a tweet lookup indexed by tweet ID."""

        return {
            row["tweet_id"]: row
            for row in df.select(
                [
                    "tweet_id",
                    "author_id",
                    "inbound",
                    "created_at",
                    "text",
                    "in_response_to_tweet_id",
                ]
            ).to_dicts()
        }

    @staticmethod
    def _walk_to_root(
        tweet_id: int,
        tweet_lookup: dict[int, dict],
    ) -> list[dict]:
        conversation = []
        visited = set()
        current_tweet_id = tweet_id

        while current_tweet_id is not None:
            if current_tweet_id in visited:
                break

            visited.add(current_tweet_id)

            tweet = tweet_lookup.get(current_tweet_id)

            if tweet is None:
                break

            conversation.append(tweet)
            current_tweet_id = tweet["in_response_to_tweet_id"]

        return conversation

    @staticmethod
    def get_apple_support_tweet_ids(df: pl.DataFrame) -> list[int]:
        """Return tweet IDs authored by AppleSupport."""

        return (
            df.filter(pl.col("author_id") == BRAND)
            .select("tweet_id")
            .to_series()
            .to_list()
        )

    @staticmethod
    def get_conversation_roots(
        tweet_ids: list[int],
        tweet_lookup: dict[int, dict],
    ) -> set[int]:
        """Find unique conversation roots for the given tweets."""
        root_tweet_ids = set()

        for tweet_id in tweet_ids:
            root_tweet_id = ConversationBuilder.find_root_tweet(
                tweet_id,
                tweet_lookup,
            )

            if root_tweet_id is not None:
                root_tweet_ids.add(root_tweet_id)

        return root_tweet_ids

    @staticmethod
    def build_child_lookup(df: pl.DataFrame) -> dict[int, int]:
        """Build a parent-to-child lookup for conversation traversal."""

        response_df = (
            df.select(
                "tweet_id",
                "in_response_to_tweet_id",
            )
            .filter(pl.col("in_response_to_tweet_id").is_not_null())
            .to_dicts()
        )

        response_map = {}

        for row in response_df:
            response_map[row["in_response_to_tweet_id"]] = row["tweet_id"]

        return response_map

    @staticmethod
    def reconstruct_forward_conversation(
        root_tweet_id: int,
        tweet_lookup: dict[int, dict],
        child_lookup: dict[int, int],
    ) -> list[dict]:
        """Reconstruct a conversation from root to the latest child."""

        conversation = []
        current_tweet_id = root_tweet_id
        visited = set()

        while current_tweet_id is not None:
            if current_tweet_id in visited:
                break

            visited.add(current_tweet_id)

            tweet = tweet_lookup.get(current_tweet_id)

            if tweet is None:
                break

            conversation.append(tweet)

            current_tweet_id = child_lookup.get(current_tweet_id)

        return conversation

    @staticmethod
    def reconstruct_all_conversations(
        conversation_roots: set[int],
        tweet_lookup: dict[int, dict],
        child_lookup: dict[int, int],
    ) -> list[list[dict]]:
        """Reconstruct all conversations from their root tweets."""

        conversations = []

        for root_tweet_id in conversation_roots:
            conversation = ConversationBuilder.reconstruct_forward_conversation(
                root_tweet_id=root_tweet_id,
                tweet_lookup=tweet_lookup,
                child_lookup=child_lookup,
            )

            if conversation:
                conversations.append(conversation)

        return conversations

    @staticmethod
    def is_valid_conversation(
        conversation: list[dict],
        brand: str,
    ) -> bool:
        """Return whether a conversation is usable for the support pipeline."""

        has_brand = any(tweet["author_id"] == brand for tweet in conversation)

        has_customer = any(tweet["inbound"] for tweet in conversation)

        has_support = any(not tweet["inbound"] for tweet in conversation)

        has_text = any(
            tweet["text"] and tweet["text"].strip() for tweet in conversation
        )

        return has_brand and has_customer and has_support and has_text

    @staticmethod
    def flatten_conversations(
        conversations: list[list[dict]],
    ) -> pl.DataFrame:
        """Flatten reconstructed conversations into a tabular dataset."""

        rows = []

        for conversation in conversations:
            if not conversation:
                continue

            conversation_id = conversation[0]["tweet_id"]

            for turn_index, tweet in enumerate(conversation):
                rows.append(
                    {
                        "conversation_id": conversation_id,
                        "turn_index": turn_index,
                        "tweet_id": tweet["tweet_id"],
                        "author_id": tweet["author_id"],
                        "inbound": tweet["inbound"],
                        "created_at": tweet["created_at"],
                        "text": tweet["text"],
                    }
                )

        return pl.DataFrame(rows)
