from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")

candidate_keys = {
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

results = []

for dataset, key in candidate_keys.items():
    file_path = RAW_DIR / f"{dataset}.csv"
    df = pd.read_csv(file_path)

    total_rows = len(df)
    null_count = df[key].isna().sum()
    unique_count = df[key].nunique(dropna=True)
    duplicate_rows = total_rows - unique_count - null_count

    uniqueness_pct = (
        unique_count / (total_rows - null_count) * 100
        if total_rows - null_count > 0
        else 0
    )

    results.append({
        "dataset": dataset,
        "candidate_key": key,
        "rows": total_rows,
        "unique_values": unique_count,
        "null_values": null_count,
        "duplicate_key_rows": duplicate_rows,
        "uniqueness_pct": round(uniqueness_pct, 2)
    })

result = pd.DataFrame(results)

print(result.to_string(index=False))

result.to_csv(
    "reports/primary_key_analysis.csv",
    index=False
)

print("\nPrimary key analysis saved to reports/primary_key_analysis.csv")
