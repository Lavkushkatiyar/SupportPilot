import csv
import random
import re
from pathlib import Path

import polars as pl

SEED = 42
TARGET_SIZE = 200
SAMPLES_PER_INTENT = 8
MULTI_INTENT_SAMPLES = 40
DIFFICULT_SAMPLES = 30

ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = ROOT / "data/processed/apple_support_conversations.parquet"

# Keep the existing annotated golden set safe.
OUTPUT_PATH = ROOT / "data/evaluation/golden_set_candidates_v2.csv"

INTENT_KEYWORDS = {
    "software_update_issue": (r"\b(ios|macos|update|updating|upgrade|downgrade)\b"),
    "battery_and_charging": (r"\b(battery|charging|charger|charge|drain)\b"),
    "device_hardware_issue": (r"\b(screen|speaker|camera|broken|hardware|overheat)\b"),
    "icloud_backup_data": (
        r"\b(icloud|backup|restore|deleted|lost data|missing data)\b"
    ),
    "apple_id_account_security": (
        r"\b(apple id|password|account|locked out|hacked|login)\b"
    ),
    "app_store_purchase_billing": (
        r"\b(app store|refund|purchase|subscription|billing|payment)\b"
    ),
    "connectivity_and_communication": (
        r"\b(wifi|wi-fi|bluetooth|cellular|imessage|facetime|calls)\b"
    ),
    "settings_and_how_to": (r"\b(settings|how to|how do i|configure|enable|disable)\b"),
    "other_or_out_of_scope": (
        r"\b(shipping|delivery|stock|return policy|repair status|"
        r"support agent|wait time|customer service)\b"
    ),
}

PATTERNS = {
    intent: re.compile(pattern, re.IGNORECASE)
    for intent, pattern in INTENT_KEYWORDS.items()
}

FIELDS = [
    "tweet_id",
    "conversation_id",
    "turn_index",
    "created_at",
    "text",
    "sampling_group",
    "candidate_intents",
    "intent",
    "annotation_notes",
    "escalation_decision",
    "escalation_reason",
]


def load_messages() -> list[dict]:
    """Load valid inbound messages and remove duplicate tweet IDs."""
    return (
        pl.read_parquet(INPUT_PATH)
        .filter(pl.col("inbound") & pl.col("text").is_not_null())
        .filter(pl.col("text").str.strip_chars().str.len_chars() > 0)
        .unique(subset=["tweet_id"], keep="first")
        .select(
            "tweet_id",
            "conversation_id",
            "turn_index",
            "created_at",
            "text",
        )
        .to_dicts()
    )


def find_intents(text: str) -> list[str]:
    """Find keyword-based candidate intents; these are not final labels."""
    return [intent for intent, pattern in PATTERNS.items() if pattern.search(text)]


def prepare_messages(messages: list[dict]) -> list[dict]:
    """Attach candidate-intent hints to every message."""
    for message in messages:
        message["candidate_intents"] = find_intents(message["text"])

    return messages


def create_candidate_row(message: dict, group: str) -> dict:
    """Create an unannotated golden-set candidate row."""
    return {
        "tweet_id": message["tweet_id"],
        "conversation_id": message["conversation_id"],
        "turn_index": message["turn_index"],
        "created_at": message["created_at"],
        "text": message["text"],
        "sampling_group": group,
        "candidate_intents": "|".join(message["candidate_intents"]),
        "intent": "",
        "annotation_notes": "",
        "escalation_decision": "",
        "escalation_reason": "",
    }


def add_samples(
    candidates: list[dict],
    count: int,
    group: str,
    selected: list[dict],
    selected_tweet_ids: set,
    selected_conversation_ids: set,
) -> int:
    """Add unique messages without selecting multiple turns per conversation."""
    added = 0

    for message in candidates:
        tweet_id = message["tweet_id"]
        conversation_id = message["conversation_id"]

        if tweet_id in selected_tweet_ids:
            continue

        if conversation_id in selected_conversation_ids:
            continue

        selected_tweet_ids.add(tweet_id)
        selected_conversation_ids.add(conversation_id)
        selected.append(create_candidate_row(message, group))
        added += 1

        if added >= count:
            break

    return added


def select_candidates(messages: list[dict]) -> list[dict]:
    """Select intent-focused, overlapping, difficult, and random examples."""
    rng = random.Random(SEED)
    rng.shuffle(messages)

    selected = []
    selected_tweet_ids = set()
    selected_conversation_ids = set()

    def add(candidates: list[dict], count: int, group: str) -> None:
        add_samples(
            candidates=candidates,
            count=count,
            group=group,
            selected=selected,
            selected_tweet_ids=selected_tweet_ids,
            selected_conversation_ids=selected_conversation_ids,
        )

    # Sample messages containing keywords associated with each supported intent.
    for intent in INTENT_KEYWORDS:
        candidates = [
            message for message in messages if intent in message["candidate_intents"]
        ]
        add(candidates, SAMPLES_PER_INTENT, f"candidate:{intent}")

    # Messages with keywords associated with multiple intents.
    overlapping = [
        message for message in messages if len(message["candidate_intents"]) >= 2
    ]
    add(overlapping, MULTI_INTENT_SAMPLES, "multi_intent_candidate")

    # Short messages and messages without keyword matches.
    difficult = [
        message
        for message in messages
        if len(message["text"].split()) <= 4 or not message["candidate_intents"]
    ]
    add(difficult, DIFFICULT_SAMPLES, "short_or_unmatched")

    # Fill remaining places with other messages.
    add(messages, TARGET_SIZE - len(selected), "random")

    return selected


def write_candidates(candidates: list[dict]) -> None:
    """Write candidate rows to a CSV file."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(candidates)


def main() -> None:
    messages = load_messages()
    prepare_messages(messages)
    candidates = select_candidates(messages)
    write_candidates(candidates)

    print(f"Customer messages available: {len(messages)}")
    print(f"Golden-set candidates exported: {len(candidates)}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
