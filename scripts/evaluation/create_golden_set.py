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
OUTPUT_PATH = ROOT / "data/evaluation/golden_set_annotations.csv"

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
    "app_or_media_issue": (r"\b(app|song|music|itunes|email|spotify|video)\b"),
    "app_store_purchase_billing": (
        r"\b(app store|refund|purchase|subscription|billing|payment)\b"
    ),
    "connectivity_and_communication": (
        r"\b(wifi|wi-fi|bluetooth|cellular|imessage|facetime|calls)\b"
    ),
    "settings_and_how_to": (r"\b(settings|how to|how do i|configure|enable|disable)\b"),
}

PATTERNS = {
    intent: re.compile(pattern, re.IGNORECASE)
    for intent, pattern in INTENT_KEYWORDS.items()
}


def find_intents(text: str) -> list[str]:
    intents = []

    for intent, pattern in PATTERNS.items():
        if pattern.search(text):
            intents.append(intent)

    return intents


def main() -> None:
    rng = random.Random(SEED)

    messages = (
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

    for message in messages:
        message["candidate_intents"] = find_intents(message["text"])

    rng.shuffle(messages)

    selected = []
    selected_tweet_ids = set()
    selected_conversation_ids = set()

    def add_samples(candidates: list[dict], count: int, group: str) -> None:
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

            selected.append(
                {
                    "tweet_id": tweet_id,
                    "conversation_id": conversation_id,
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
            )

            added += 1

            if added == count:
                break

    # Find candidate examples for each existing intent.
    for intent in INTENT_KEYWORDS:
        candidates = [
            message for message in messages if intent in message["candidate_intents"]
        ]
        add_samples(candidates, SAMPLES_PER_INTENT, f"candidate:{intent}")

    # Find messages whose wording may match multiple intents.
    overlapping = [
        message for message in messages if len(message["candidate_intents"]) >= 2
    ]
    add_samples(overlapping, MULTI_INTENT_SAMPLES, "multi_intent_candidate")

    # Include very short messages and messages with no keyword matches.
    difficult = [
        message
        for message in messages
        if len(message["text"].split()) <= 4 or not message["candidate_intents"]
    ]
    add_samples(difficult, DIFFICULT_SAMPLES, "short_or_unmatched")

    # Fill the remaining places with a reproducible random sample.
    add_samples(messages, TARGET_SIZE - len(selected), "random")

    fields = [
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

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(selected)

    print(f"Customer messages available: {len(messages)}")
    print(f"Golden-set candidates exported: {len(selected)}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
