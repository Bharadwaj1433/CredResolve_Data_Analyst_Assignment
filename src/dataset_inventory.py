from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
REPORTS_DIR = Path("reports")

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

records = []
schema_records = []

for file_path in sorted(RAW_DIR.glob("*.csv")):
    df = pd.read_csv(file_path)

    records.append({
        "dataset": file_path.stem,
        "rows": len(df),
        "columns": len(df.columns),
        "file_size_bytes": file_path.stat().st_size
    })

    for column in df.columns:
        schema_records.append({
            "dataset": file_path.stem,
            "column": column,
            "dtype": str(df[column].dtype)
        })

inventory = pd.DataFrame(records)
schema = pd.DataFrame(schema_records)

inventory.to_csv(REPORTS_DIR / "dataset_inventory.csv", index=False)
schema.to_csv(REPORTS_DIR / "schema_inventory.csv", index=False)

print("Dataset inventory saved to reports/dataset_inventory.csv")
print("Schema inventory saved to reports/schema_inventory.csv")
