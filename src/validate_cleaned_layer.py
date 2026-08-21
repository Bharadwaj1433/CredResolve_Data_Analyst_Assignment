import pandas as pd
from pathlib import Path

clean_path = Path("data/cleaned")

tables = [
    "accounts",
    "borrowers",
    "agents",
    "agent_sessions",
    "campaigns",
    "daily_targeting",
    "call_attempts",
    "call_dispositions",
    "complaints",
    "field_visits",
    "payments",
    "promises_to_pay",
    "sms_events",
    "whatsapp_events",
    "account_status_history",
    "vendor_telephony",
    "calls"
]

results = []

for table in tables:
    path = clean_path / f"{table}.csv"
    df = pd.read_csv(path)

    results.append({
        "dataset": table,
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "total_nulls": int(df.isna().sum().sum())
    })

result = pd.DataFrame(results)

result.to_csv(
    "reports/cleaned_layer_validation.csv",
    index=False
)

print(result.to_string(index=False))
print("Report:", "reports/cleaned_layer_validation.csv")
