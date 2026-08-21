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

        if (
            name.endswith("_id")
            or name.endswith("_code")
            or "reference" in name
            or "employee" in name
            or "message_id" in name
            or "device_id" in name
        ):
            records.append({
                "dataset": file_path.stem,
                "column": column,
                "dtype": str(df[column].dtype),
                "rows": len(df),
                "non_null": int(df[column].notna().sum()),
                "nulls": int(df[column].isna().sum()),
                "unique_values": int(df[column].nunique(dropna=True))
            })

result = pd.DataFrame(records)

print(result.to_string(index=False))

result.to_csv(
    "reports/id_inventory.csv",
    index=False
)

print("\nID inventory saved to reports/id_inventory.csv")
