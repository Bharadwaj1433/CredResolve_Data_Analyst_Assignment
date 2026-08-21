import pandas as pd
from pathlib import Path

data_path = Path("data/raw")
report_path = Path("reports/account_temporal_consistency.csv")

accounts = pd.read_csv(data_path / "accounts.csv")
accounts["opened_at"] = pd.to_datetime(accounts["opened_at"], errors="coerce")

event_tables = {
    "calls": "event_at",
    "payments": "event_at",
    "promises_to_pay": "event_at",
    "complaints": "event_at",
    "field_visits": "event_at",
    "sms_events": "event_at",
    "whatsapp_events": "event_at",
    "account_status_history": "event_at"
}

results = []

for table, timestamp_column in event_tables.items():
    path = data_path / f"{table}.csv"

    if not path.exists():
        continue

    df = pd.read_csv(path)

    if "account_id" not in df.columns or timestamp_column not in df.columns:
        continue

    df[timestamp_column] = pd.to_datetime(
        df[timestamp_column],
        errors="coerce"
    )

    merged = df[
        ["account_id", timestamp_column]
    ].merge(
        accounts[["account_id", "opened_at"]],
        on="account_id",
        how="left"
    )

    before_opening = (
        merged[timestamp_column].notna()
        & merged["opened_at"].notna()
        & (merged[timestamp_column] < merged["opened_at"])
    ).sum()

    missing_account = merged["opened_at"].isna().sum()

    results.append({
        "dataset": table,
        "rows": len(merged),
        "valid_timestamps": int(
            merged[timestamp_column].notna().sum()
        ),
        "events_before_account_opening": int(before_opening),
        "events_with_unmatched_account": int(missing_account)
    })

result = pd.DataFrame(results)

report_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

result.to_csv(
    report_path,
    index=False
)

print(result.to_string(index=False))
print("Report:", report_path)
