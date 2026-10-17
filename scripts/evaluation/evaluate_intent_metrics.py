from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[2]

PREDICTIONS_PATH = ROOT / "data/evaluation/intent_predictions.csv"
GOLDEN_SET_PATH = ROOT / "data/evaluation/golden_set_annotations.csv"
MISMATCHES_PATH = ROOT / "data/evaluation/prediction_mismatches.csv"


def main():
    predictions = pl.read_csv(PREDICTIONS_PATH)
    golden_set = pl.read_csv(GOLDEN_SET_PATH).select("tweet_id", "text")

    results = predictions.join(golden_set, on="tweet_id", how="left")

    # Normalize the old label name before comparing.
    results = results.with_columns(
        pl.col("expected_intent")
        .replace({"unknown_insufficient_context": "unknown_or_insufficient_context"})
        .alias("expected_intent"),
    )

    correct = results.filter(pl.col("expected_intent") == pl.col("predicted_intent"))

    mismatches = (
        results.filter(pl.col("expected_intent") != pl.col("predicted_intent"))
        .select(
            "tweet_id",
            "text",
            "expected_intent",
            "predicted_intent",
            "confidence",
            "rationale",
        )
        .with_columns(pl.lit("").alias("manual_review"))
    )

    total = results.height
    correct_count = correct.height

    print(f"Total messages: {total}")
    print(f"Correct predictions: {correct_count}")
    print(f"Incorrect or different labels: {mismatches.height}")
    print(f"Exact-match accuracy: {correct_count / total:.1%}")

    MISMATCHES_PATH.parent.mkdir(parents=True, exist_ok=True)
    mismatches.write_csv(MISMATCHES_PATH)

    print(f"\nReview different predictions in: {MISMATCHES_PATH}")


if __name__ == "__main__":
    main()
