from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

borrowers = pd.read_csv(RAW_DIR / "borrowers.csv")

print("Rows:", len(borrowers))
print("Unique borrower IDs:", borrowers["borrower_id"].nunique())

rows_per_borrower = (
    borrowers.groupby("borrower_id")
    .size()
    .reset_index(name="row_count")
)

print("\nRows per borrower:")
print(rows_per_borrower["row_count"].value_counts().sort_index())

identity_columns = [
    column for column in borrowers.columns
    if column != "borrower_id"
]

records = []

for borrower_id, group in borrowers.groupby("borrower_id"):
    record = {
        "borrower_id": borrower_id,
        "rows": len(group)
    }

    for column in identity_columns:
        record[f"{column}_unique"] = group[column].nunique(dropna=False)

    records.append(record)

variability = pd.DataFrame(records)

print("\nAttribute conflicts:")

for column in identity_columns:
    unique_column = f"{column}_unique"
    affected = (variability[unique_column] > 1).sum()

    if affected:
        print(column, affected)

variability.to_csv(
    REPORT_DIR / "borrower_identity_variability.csv",
    index=False
)

conflict_columns = [
    f"{column}_unique"
    for column in identity_columns
]

conflict_mask = variability[conflict_columns].gt(1).any(axis=1)

conflicting_ids = variability.loc[
    conflict_mask,
    "borrower_id"
].head(20)

print("\nConflicting borrower examples:")

for borrower_id in conflicting_ids:
    print("\nBorrower:", borrower_id)
    print(
        borrowers[
            borrowers["borrower_id"] == borrower_id
        ].to_string(index=False)
    )

operational_tables = [
    "accounts",
    "calls",
    "call_attempts",
    "call_dispositions",
    "whatsapp_events",
    "sms_events",
    "field_visits",
    "promises_to_pay",
    "payments",
    "complaints",
    "account_status_history"
]

borrower_master_ids = set(
    borrowers["borrower_id"].dropna().astype(str)
)

orphan_records = []

for table in operational_tables:
    path = RAW_DIR / f"{table}.csv"

    if not path.exists():
        continue

    df = pd.read_csv(path)

    if "borrower_id" not in df.columns:
        continue

    values = df["borrower_id"].dropna().astype(str)
    orphan_mask = ~values.isin(borrower_master_ids)

    orphan_records.append({
        "dataset": table,
        "non_null_borrower_ids": len(values),
        "orphan_borrower_ids": int(orphan_mask.sum()),
        "orphan_pct": round(orphan_mask.mean() * 100, 2)
    })

orphan_report = pd.DataFrame(orphan_records)

print("\nOrphan borrower summary:")
print(orphan_report.to_string(index=False))

orphan_report.to_csv(
    REPORT_DIR / "borrower_orphan_analysis.csv",
    index=False
)

print("\nReports:")
print("reports/borrower_identity_variability.csv")
print("reports/borrower_orphan_analysis.csv")