import pandas as pd
from pathlib import Path

raw_path = Path("data/raw")
clean_path = Path("data/cleaned")
clean_path.mkdir(parents=True, exist_ok=True)

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
    "vendor_telephony"
]

timestamp_columns = {
    "accounts": ["opened_at"],
    "borrowers": ["created_at", "updated_at"],
    "agents": ["joined_at", "updated_at"],
    "agent_sessions": ["login_at", "logout_at"],
    "campaigns": ["start_at", "end_at"],
    "daily_targeting": ["target_date"],
    "call_attempts": ["event_at"],
    "call_dispositions": ["event_at"],
    "complaints": ["event_at", "resolution_at"],
    "field_visits": ["event_at", "scheduled_at"],
    "payments": ["event_at"],
    "promises_to_pay": ["event_at", "promised_date"],
    "sms_events": ["event_at"],
    "whatsapp_events": ["event_at"],
    "account_status_history": ["event_at", "recorded_at"],
    "vendor_telephony": []
}

for table in tables:
    source = raw_path / f"{table}.csv"
    target = clean_path / f"{table}.csv"

    df = pd.read_csv(source)

    for column in timestamp_columns.get(table, []):
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    df.to_csv(
        target,
        index=False
    )

    print(table, len(df))

print("Cleaned files created:", len(tables))
print("Output directory:", clean_path)
