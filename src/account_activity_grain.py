import pandas as pd
from pathlib import Path

data_path = Path("data/raw")
report_path = Path("reports/account_activity_grain.csv")

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

    results.append({
        "dataset": table,
        "rows": len(df),
        "unique_accounts": df["account_id"].nunique(),
        "rows_per_account": round(
            len(df) / df["account_id"].nunique(),
            3
        ),
        "missing_account_id": int(
            df["account_id"].isna().sum()
        )
    })

result = pd.DataFrame(results)

result.to_csv(
    report_path,
    index=False
)

print(result.to_string(index=False))
print("Report:", report_path)
