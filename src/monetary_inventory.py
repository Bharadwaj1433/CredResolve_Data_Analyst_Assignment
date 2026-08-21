from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")

monetary_columns = {
    "accounts": [
        "principal_amount",
        "outstanding_amount"
    ],
    "payments": [
        "amount"
    ],
    "promises_to_pay": [
        "promised_amount"
    ]
}

records = []

for dataset, columns in monetary_columns.items():
    file_path = RAW_DIR / f"{dataset}.csv"
    df = pd.read_csv(file_path)

    for column in columns:
        series = pd.to_numeric(df[column], errors="coerce")

        records.append({
            "dataset": dataset,
            "column": column,
            "dtype": str(df[column].dtype),
            "non_null": int(series.notna().sum()),
            "nulls": int(series.isna().sum()),
            "unique_values": int(series.nunique(dropna=True)),
            "minimum": series.min(),
            "maximum": series.max(),
            "mean": series.mean(),
            "zero_values": int((series == 0).sum()),
            "negative_values": int((series < 0).sum())
        })

result = pd.DataFrame(records)

print(result.to_string(index=False))

result.to_csv(
    "reports/monetary_inventory.csv",
    index=False
)

print("\nMonetary inventory saved to reports/monetary_inventory.csv")
