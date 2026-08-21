import pandas as pd
from pathlib import Path

data_path = Path("data/raw")
report_path = Path("reports/temporal_consistency_analysis.csv")

results = []

status = pd.read_csv(data_path / "account_status_history.csv")

status["event_at"] = pd.to_datetime(
    status["event_at"],
    errors="coerce"
)

status["recorded_at"] = pd.to_datetime(
    status["recorded_at"],
    errors="coerce"
)

status_late = (
    status["recorded_at"] > status["event_at"]
).sum()

results.append({
    "dataset": "account_status_history",
    "check": "recorded_after_event",
    "rows_checked": len(status),
    "violations": int(status_late)
})

field_visits = pd.read_csv(data_path / "field_visits.csv")

field_visits["event_at"] = pd.to_datetime(
    field_visits["event_at"],
    errors="coerce"
)

field_visits["scheduled_at"] = pd.to_datetime(
    field_visits["scheduled_at"],
    errors="coerce"
)

scheduled_after_event = (
    field_visits["scheduled_at"].notna()
    & (field_visits["scheduled_at"] > field_visits["event_at"])
).sum()

results.append({
    "dataset": "field_visits",
    "check": "scheduled_after_event",
    "rows_checked": len(field_visits),
    "violations": int(scheduled_after_event)
})

ptp = pd.read_csv(data_path / "promises_to_pay.csv")

ptp["event_at"] = pd.to_datetime(
    ptp["event_at"],
    errors="coerce"
)

ptp["promised_date"] = pd.to_datetime(
    ptp["promised_date"],
    errors="coerce"
)

promised_before_event = (
    ptp["promised_date"] < ptp["event_at"]
).sum()

results.append({
    "dataset": "promises_to_pay",
    "check": "promised_before_event",
    "rows_checked": len(ptp),
    "violations": int(promised_before_event)
})

complaints = pd.read_csv(data_path / "complaints.csv")

complaints["event_at"] = pd.to_datetime(
    complaints["event_at"],
    errors="coerce"
)

complaints["resolution_at"] = pd.to_datetime(
    complaints["resolution_at"],
    errors="coerce"
)

resolution_before_event = (
    complaints["resolution_at"] < complaints["event_at"]
).sum()

results.append({
    "dataset": "complaints",
    "check": "resolution_before_event",
    "rows_checked": len(complaints),
    "violations": int(resolution_before_event)
})

result = pd.DataFrame(results)

result.to_csv(
    report_path,
    index=False
)

print(result.to_string(index=False))
print("Report:", report_path)
