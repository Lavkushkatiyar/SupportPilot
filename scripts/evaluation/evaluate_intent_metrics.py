from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[2]

PREDICTIONS_PATH = ROOT / "data/evaluation/intent_predictions.csv"
GOLDEN_SET_PATH = ROOT / "data/evaluation/golden_set_annotations.csv"
MISMATCHES_PATH = ROOT / "data/evaluation/prediction_mismatches.csv"


def main():
    predictions = pl.read_csv(PREDICTIONS_PATH)
    golden_set = pl.read_csv(GOLDEN_SET_PATH)

    # Keep the human annotation and its notes alongside the model prediction.
    golden_columns = [
        "tweet_id",
        "text",
        "intent",
        "annotation_notes",
        "annotation_confidence",
        "review_status",
    ]

    golden_set = golden_set.select(
        [column for column in golden_columns if column in golden_set.columns]
    )

    results = predictions.join(golden_set, on="tweet_id", how="left")

    # Normalize the legacy label if it appears in either file.
    results = results.with_columns(
        pl.col("expected_intent")
        .replace({"unknown_insufficient_context": "unknown_or_insufficient_context"})
        .alias("expected_intent"),
        pl.col("intent")
        .replace({"unknown_insufficient_context": "unknown_or_insufficient_context"})
        .alias("intent"),
    )

    # Compare the model prediction against the V2 human annotation.
    mismatches = (
        results.filter(pl.col("predicted_intent") != pl.col("intent"))
        .select(
            "tweet_id",
            "text",
            pl.col("intent").alias("golden_set_intent"),
            "annotation_notes",
            "annotation_confidence",
            "review_status",
            pl.col("predicted_intent").alias("classifier_intent"),
            "confidence",
            "rationale",
        )
        .with_columns(pl.lit("").alias("manual_review"))
    )

    MISMATCHES_PATH.parent.mkdir(parents=True, exist_ok=True)
    mismatches.write_csv(MISMATCHES_PATH)

    total = results.height
    correct = results.filter(pl.col("predicted_intent") == pl.col("intent")).height

    print(f"Total messages: {total}")
    print(f"Exact matches: {correct}")
    print(f"Mismatches: {mismatches.height}")

    if total:
        print(f"Exact-match accuracy: {correct / total:.1%}")

    print(f"Mismatch file saved to: {MISMATCHES_PATH}")


if __name__ == "__main__":
    main()
