from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[2]

PREDICTIONS_PATH = ROOT / "data/evaluation/intent_predictions.csv"
GOLDEN_SET_PATH = ROOT / "data/evaluation/golden_set_annotations_v3.csv"
MISMATCHES_PATH = ROOT / "data/evaluation/prediction_mismatches.csv"

UNKNOWN_LABELS = {
    "unknown_insufficient_context",
    "unknown_or_insufficient_context",
    "other_or_out_of_scope",
}

COMBINED_LABEL = "unknown_or_out_of_scope"


def normalize_label(column: str) -> pl.Expr:
    """Normalize legacy labels and merge unknown/out-of-scope."""
    return (
        pl.when(pl.col(column).is_in(list(UNKNOWN_LABELS)))
        .then(pl.lit(COMBINED_LABEL))
        .otherwise(pl.col(column))
    )


def main():
    predictions = pl.read_csv(PREDICTIONS_PATH)
    golden_set = pl.read_csv(GOLDEN_SET_PATH)

    golden_columns = [
        "tweet_id",
        "text",
        "intent",
        "annotation_rationale",
        "annotation_confidence",
        "review_status",
    ]

    golden_set = golden_set.select(
        [column for column in golden_columns if column in golden_set.columns]
    )

    results = predictions.join(
        golden_set,
        on="tweet_id",
        how="left",
    )

    results = results.with_columns(
        normalize_label("intent").alias("golden_set_intent"),
        normalize_label("predicted_intent").alias("classifier_intent"),
    )

    valid_results = results.filter(
        pl.col("golden_set_intent").is_not_null()
        & pl.col("classifier_intent").is_not_null()
    )

    mismatches = (
        valid_results.filter(pl.col("golden_set_intent") != pl.col("classifier_intent"))
        .select(
            "tweet_id",
            "text",
            "golden_set_intent",
            "annotation_rationale",
            "annotation_confidence",
            "review_status",
            "classifier_intent",
            "confidence",
            "rationale",
        )
        .with_columns(pl.lit("").alias("manual_review"))
    )

    MISMATCHES_PATH.parent.mkdir(parents=True, exist_ok=True)
    mismatches.write_csv(MISMATCHES_PATH)

    total = valid_results.height
    correct = total - mismatches.height

    print(f"Total prediction rows: {predictions.height}")
    print(f"Rows with valid labels: {total}")
    print(f"Rows excluded from scoring: {results.height - total}")
    print(f"Correct after combining categories: {correct}")
    print(f"Remaining mismatches: {mismatches.height}")

    if total:
        print(f"Combined-category accuracy: {correct / total:.1%}")

    print(f"Mismatch file saved to: {MISMATCHES_PATH}")


if __name__ == "__main__":
    main()
