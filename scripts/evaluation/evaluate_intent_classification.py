from pathlib import Path

import polars as pl

from app.services.intent_classifier import IntentClassifier

ROOT = Path(__file__).resolve().parents[2]

GOLDEN_SET_PATH = ROOT / "data/evaluation/golden_set_annotations_v3.csv"


def load_golden_set() -> pl.DataFrame:
    if not GOLDEN_SET_PATH.is_file():
        raise FileNotFoundError(f"Golden set not found: {GOLDEN_SET_PATH}")

    dataset = pl.read_csv(GOLDEN_SET_PATH)
    return dataset


def create_intent_predication():
    dataset = load_golden_set()
    print(len(dataset))
    classifier = IntentClassifier()
    predictions = []
    count = 0

    for row in dataset.iter_rows(named=True):
        result = classifier.classify(row["text"])

        predictions.append(
            {
                "tweet_id": row["tweet_id"],
                "expected_intent": row["intent"],
                "predicted_intent": result.intent.value,
                "confidence": result.confidence,
                "rationale": result.rationale,
            }
        )
        count = count + 1
        print("Predicated intent ", count)

    pl.DataFrame(predictions).write_csv("data/evaluation/intent_predictions.csv")

    print(f"Saved {len(predictions)} predictions.")


if __name__ == "__main__":
    create_intent_predication()
