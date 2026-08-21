from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")

key_columns = {
    "agents": "agent_id",
    "borrowers": "borrower_id",
    "calls": "call_id",
    "payments": "payment_id",
    "whatsapp_events": "whatsapp_event_id"
}

records = []

for dataset, key in key_columns.items():
    file_path = RAW_DIR / f"{dataset}.csv"
    df = pd.read_csv(file_path)

    duplicate_mask = df[key].duplicated(keep=False)
    duplicates = df[duplicate_mask].copy()

    if duplicates.empty:
        continue

    grouped = duplicates.groupby(key, dropna=False)

    for key_value, group in grouped:
        row_hashes = pd.util.hash_pandas_object(
            group,
            index=False
        )

        exact_duplicate = row_hashes.nunique() == 1

        records.append({
            "dataset": dataset,
            "key_column": key,
            "key_value": key_value,
            "rows_with_key": len(group),
            "unique_row_hashes": int(row_hashes.nunique()),
            "exact_duplicate_group": bool(exact_duplicate)
        })

result = pd.DataFrame(records)

print(result.to_string(index=False))

result.to_csv(
    "reports/duplicate_profile.csv",
    index=False
)

print("\nDuplicate profile saved to reports/duplicate_profile.csv")

if not result.empty:
    print("\nSUMMARY")
    print(
        result.groupby(
            ["dataset", "exact_duplicate_group"]
        ).size()
    )
