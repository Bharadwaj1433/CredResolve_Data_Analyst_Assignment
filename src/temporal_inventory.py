from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")

records = []

for file_path in sorted(RAW_DIR.glob("*.csv")):
    if file_path.stem == "data_dictionary":
        continue

    df = pd.read_csv(file_path)

    for column in df.columns:
        name = column.lower()

        if any(term in name for term in [
            "date",
            "time",
            "timestamp",
            "event_at",
            "created_at",
            "updated_at",
            "opened_at",
            "joined_at",
            "login_at",
            "logout_at",
            "recorded_at",
            "scheduled_at",
            "resolution_at",
            "start_at",
            "end_at"
        ]):
            records.append({
                "dataset": file_path.stem,
                "column": column,
                "dtype": str(df[column].dtype),
                "non_null": int(df[column].notna().sum()),
                "nulls": int(df[column].isna().sum()),
                "sample_value": df[column].dropna().iloc[0]
                if df[column].notna().any()
                else None
            })

result = pd.DataFrame(records)

print(result.to_string(index=False))

result.to_csv(
    "reports/temporal_inventory.csv",
    index=False
)

print("\nTemporal inventory saved to reports/temporal_inventory.csv")
