from pathlib import Path

import polars as pl

DATASET = Path("data/processed/apple_support_conversations.parquet")


INTENT_KEYWORDS = {
    "software_update_issue": [
        "ios",
        "update",
        "upgrade",
        "install",
        "ios 11",
        "macos",
    ],
    "battery_and_charging": [
        "battery",
        "charge",
        "charging",
        "charger",
        "drain",
    ],
    "device_hardware_issue": [
        "screen",
        "button",
        "speaker",
        "microphone",
        "mic",
        "stuck",
        "broken",
        "won't turn on",
        "wont turn on",
        "unresponsive",
    ],
    "icloud_backup_data": [
        "icloud",
        "backup",
        "back up",
        "restore",
        "photos disappeared",
        "messages disappeared",
        "lost my photos",
        "lost my files",
    ],
    "apple_id_account_security": [
        "apple id",
        "password",
        "locked",
        "hacked",
        "hack",
        "security",
        "stolen",
        "two factor",
        "2 factor",
    ],
    "app_store_purchase_billing": [
        "app store",
        "purchase",
        "refund",
        "subscription",
        "charged",
        "billing",
        "download apps",
        "update apps",
    ],
    "connectivity_and_communication": [
        "wifi",
        "wi-fi",
        "bluetooth",
        "cellular",
        "calls",
        "call",
        "imessage",
        "facetime",
        "internet",
        "connect",
    ],
    "app_or_media_issue": [
        "app",
        "spotify",
        "music",
        "itunes",
        "email",
        "song",
        "video",
    ],
    "settings_and_how_to": [
        "how do",
        "how can",
        "how to",
        "is there a way",
        "can i",
        "why does",
        "setting",
        "settings",
        "airplane mode",
        "brightness",
    ],
}


def load_customer_messages(dataset_path: Path) -> pl.DataFrame:
    return (
        pl.scan_parquet(dataset_path)
        .filter(pl.col("inbound"))
        .select(["conversation_id", "text"])
        .filter(pl.col("text").is_not_null())
        .filter(pl.col("text").str.len_chars() > 0)
        .collect()
    )


def classify_by_keywords(text: str) -> list[str]:
    text_lower = text.lower()

    intents = []

    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                intents.append(intent)
                break

    return intents


def analyze(df: pl.DataFrame) -> None:
    results: list[dict[str, object]] = []

    for row in df.iter_rows(named=True):
        intents = classify_by_keywords(row["text"])

        results.append(
            {
                "conversation_id": row["conversation_id"],
                "text": row["text"],
                "matched_intents": ", ".join(intents) if intents else "unmatched",
            }
        )

    result_df = pl.DataFrame(results)

    print("\n=== TAXONOMY KEYWORD ANALYSIS ===")
    print(f"Customer messages: {df.height:,}")

    print("\n=== MATCH COUNTS ===")

    for intent in INTENT_KEYWORDS:
        count = result_df.filter(pl.col("matched_intents").str.contains(intent)).height

        print(f"{intent}: {count:,}")

    unmatched = result_df.filter(pl.col("matched_intents") == "unmatched").height

    print(f"unmatched: {unmatched:,}")

    print("\n=== MULTIPLE INTENT MATCHES ===")

    multiple = result_df.filter(pl.col("matched_intents").str.contains(","))

    print(f"Messages matching multiple intents: {multiple.height:,}")

    print("\n=== SAMPLE UNMATCHED ===")
    print(result_df.filter(pl.col("matched_intents") == "unmatched").head(20))

    print("\n=== SAMPLE MULTIPLE MATCHES ===")
    print(multiple.head(20))


def main() -> None:
    df = load_customer_messages(DATASET)
    analyze(df)


if __name__ == "__main__":
    main()
