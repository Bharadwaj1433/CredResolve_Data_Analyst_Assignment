from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")

key_columns = {
    "account_status_history": "history_id",
    "accounts": "account_id",
    "agent_sessions": "session_id",
    "agents": "agent_id",
    "borrowers": "borrower_id",
    "call_attempts": "attempt_id",
    "call_dispositions": "disposition_id",
    "calls": "call_id",
    "campaigns": "campaign_id",
    "complaints": "complaint_id",
    "daily_targeting": "target_id",
    "field_visits": "visit_id",
    "payments": "payment_id",
    "promises_to_pay": "ptp_id",
    "sms_events": "sms_event_id",
    "vendor_telephony": "vendor_id",
    "whatsapp_events": "whatsapp_event_id"
}

records = []

for dataset, key in key_columns.items():
    file_path = RAW_DIR / f"{dataset}.csv"
    df = pd.read_csv(file_path)

    counts = df[key].value_counts(dropna=False)

    records.append({
        "dataset": dataset,
        "rows": len(df),
        "candidate_key": key,
        "unique_key_values": int(df[key].nunique(dropna=True)),
        "min_rows_per_key": int(counts.min()),
        "max_rows_per_key": int(counts.max()),
        "average_rows_per_key": round(counts.mean(), 4),
        "duplicate_key_groups": int((counts > 1).sum())
    })

result = pd.DataFrame(records)

print(result.to_string(index=False))

result.to_csv(
    "reports/table_grain_analysis.csv",
    index=False
)

print("\nTable grain analysis saved to reports/table_grain_analysis.csv")
