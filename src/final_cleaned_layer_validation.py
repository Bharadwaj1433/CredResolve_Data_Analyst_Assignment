import pandas as pd
from pathlib import Path

path = Path("data/cleaned")

checks = []

def add_check(name, actual, expected):
    checks.append({
        "check": name,
        "actual": actual,
        "expected": expected,
        "status": "PASS" if actual == expected else "FAIL"
    })

tables = {
    "accounts": 30000,
    "borrowers": 30000,
    "agents": 30000,
    "agent_sessions": 15000,
    "campaigns": 120,
    "daily_targeting": 45000,
    "call_attempts": 120000,
    "call_dispositions": 35000,
    "complaints": 8000,
    "field_visits": 25000,
    "payments": 25000,
    "promises_to_pay": 18000,
    "sms_events": 45000,
    "whatsapp_events": 60000,
    "account_status_history": 60000,
    "vendor_telephony": 15,
    "calls": 90079
}

for table, expected_rows in tables.items():
    df = pd.read_csv(path / f"{table}.csv")

    add_check(
        f"{table}_row_count",
        len(df),
        expected_rows
    )

    add_check(
        f"{table}_exact_duplicates",
        int(df.duplicated().sum()),
        0
    )

for table, column in [
    ("payments", "payment_id"),
    ("whatsapp_events", "whatsapp_event_id"),
    ("calls", "call_id")
]:
    df = pd.read_csv(path / f"{table}.csv")

    add_check(
        f"{table}_unique_{column}",
        df[column].nunique(),
        25000 if table == "payments"
        else 60000 if table == "whatsapp_events"
        else 90000
    )

for table in [
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
]:
    df = pd.read_csv(path / f"{table}.csv")

    add_check(
        f"{table}_missing_account_id",
        int(df["account_id"].isna().sum()),
        0
    )

calls = pd.read_csv(path / "calls.csv")

add_check(
    "call_quality_flags",
    int(
        all(
            column in calls.columns
            for column in [
                "call_id_conflict",
                "agent_id_conflict",
                "event_at_conflict"
            ]
        )
    ),
    1
)

status = pd.read_csv(path / "account_status_history.csv")

add_check(
    "status_timing_flag",
    int("recorded_before_event" in status.columns),
    1
)

result = pd.DataFrame(checks)

result.to_csv(
    "reports/final_cleaned_layer_validation.csv",
    index=False
)

print(result.to_string(index=False))

failed = result[result["status"] == "FAIL"]

print("Total checks:", len(result))
print("Passed:", len(result[result["status"] == "PASS"]))
print("Failed:", len(failed))
print("Report:", "reports/final_cleaned_layer_validation.csv")
