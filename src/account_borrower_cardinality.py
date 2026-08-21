import pandas as pd
from pathlib import Path

data_path = Path("data/raw")
report_path = Path("reports/account_borrower_cardinality.csv")

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
        df.groupby("account_id", dropna=False)["borrower_id"]
        .nunique()
        .reset_index(name="borrower_id_count")
    )

    distribution = (
        grouped["borrower_id_count"]
        .value_counts()
        .sort_index()
    )

    for borrower_count, account_count in distribution.items():
        results.append({
            "dataset": table,
            "borrower_id_count": int(borrower_count),
            "account_count": int(account_count)
        })

result = pd.DataFrame(results)

result.to_csv(
    report_path,
    index=False
)

print(result.to_string(index=False))
print("Report:", report_path)
