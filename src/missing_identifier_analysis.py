import pandas as pd
from pathlib import Path

data_path = Path("data/raw")
report_path = Path("reports/missing_identifier_analysis.csv")

identifier_columns = {
    "borrowers": ["borrower_id"],
    "accounts": ["account_id", "borrower_id"],
    "agents": ["agent_id", "employee_code", "vendor_id"],
    "agent_sessions": ["session_id", "agent_id", "device_id"],
    "calls": [
        "call_id",
        "account_id",
        "borrower_id",
        "agent_id",
        "campaign_id",
        "vendor_id"
    ],
    "call_attempts": [
        "attempt_id",
        "account_id",
        "borrower_id",
        "call_id",
        "agent_id",
        "vendor_id"
    ],
    "call_dispositions": [
        "disposition_id",
        "account_id",
        "borrower_id",
        "call_id",
        "agent_id"
    ],
    "whatsapp_events": [
        "whatsapp_event_id",
        "account_id",
        "borrower_id",
        "message_id",
        "provider_id"
    ],
    "sms_events": [
        "sms_event_id",
        "account_id",
        "borrower_id",
        "message_id",
        "provider_id"
    ],
    "field_visits": [
        "visit_id",
        "account_id",
        "borrower_id",
        "agent_id"
    ],
    "promises_to_pay": [
        "ptp_id",
        "account_id",
        "borrower_id",
        "agent_id"
    ],
    "payments": [
        "payment_id",
        "account_id",
        "borrower_id",
        "payment_reference",
        "provider_id"
    ],
    "complaints": [
        "complaint_id",
        "account_id",
        "borrower_id"
    ],
    "account_status_history": [
        "history_id",
        "account_id",
        "borrower_id"
    ],
    "daily_targeting": [
        "target_id",
        "account_id",
        "campaign_id"
    ],
    "campaigns": ["campaign_id"],
    "vendor_telephony": ["vendor_id", "vendor_account_id"]
}

results = []

for dataset, columns in identifier_columns.items():
    path = data_path / f"{dataset}.csv"

    if not path.exists():
        continue

    df = pd.read_csv(path)

    for column in columns:
        if column not in df.columns:
            continue

        null_count = df[column].isna().sum()
        empty_count = (
            df[column]
            .astype("string")
            .str.strip()
            .eq("")
            .sum()
        )

        missing_count = null_count + empty_count

        results.append({
            "dataset": dataset,
            "column": column,
            "rows": len(df),
            "missing_values": int(missing_count),
            "missing_pct": round(
                missing_count / len(df) * 100,
                2
            )
        })

result = pd.DataFrame(results)

result = result.sort_values(
    ["missing_values", "dataset", "column"],
    ascending=[False, True, True]
)

result.to_csv(
    report_path,
    index=False
)

print(result.to_string(index=False))
print("Report:", report_path)
