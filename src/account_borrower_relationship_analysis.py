import pandas as pd
from pathlib import Path

data_path = Path("data/raw")
report_path = Path("reports/account_borrower_relationship_analysis.csv")

tables = [
    "calls",
    "call_attempts",
    "call_dispositions",
    "payments",
    "promises_to_pay",
    "complaints",
    "field_visits",
    "sms_events",
    "whatsapp_events",
    "account_status_history"
]

results = []

for table in tables:
    df = pd.read_csv(data_path / f"{table}.csv")

    grouped = (
        df.groupby("account_id", dropna=False)
        .agg(
            borrower_id_unique=("borrower_id", "nunique"),
            rows=("account_id", "size")
        )
        .reset_index()
    )

    results.append({
        "dataset": table,
        "accounts_checked": len(grouped),
        "accounts_with_multiple_borrower_ids": (
            grouped["borrower_id_unique"] > 1
        ).sum(),
        "accounts_with_missing_borrower_id": (
            grouped["borrower_id_unique"] == 0
        ).sum()
    })

result = pd.DataFrame(results)

result.to_csv(
    report_path,
    index=False
)

print(result.to_string(index=False))
print("Report:", report_path)
