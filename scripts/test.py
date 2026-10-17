from pathlib import Path

import pandas as pd

path = Path("data/evaluation/golden_set_annotations.csv")

if path.exists():
    df = pd.read_csv(path)

    print(f"File: {path}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Duplicate rows: {df.duplicated().sum()}")
    print(f"\nMissing values:\n{df.isna().sum()}")
    print(f"\nSample records:\n{df.head(5).to_string(index=False)}")
else:
    print(f"Missing file: {path}")
