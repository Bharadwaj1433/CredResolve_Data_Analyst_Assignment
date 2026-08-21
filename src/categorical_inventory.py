from pathlib import Path
import pandas as pd
from pandas.api.types import is_string_dtype

RAW_DIR = Path("data/raw")

excluded_columns = {
    "borrower_id",
    "account_id",
    "agent_id",
    "employee_code",
    "vendor_id",
    "vendor_account_id",
    "session_id",
    "device_id",
    "history_id",
    "call_id",
    "attempt_id",
    "disposition_id",
    "campaign_id",
    "complaint_id",
    "target_id",
    "visit_id",
    "payment_id",
    "payment_reference",
    "ptp_id",
    "sms_event_id",
    "whatsapp_event_id",
    "message_id",
    "provider_id",
    "name",
    "phone",
    "email",
    "event_at",
    "recorded_at",
    "opened_at",
    "created_at",
    "updated_at",
    "joined_at",
    "login_at",
    "logout_at",
    "start_at",
    "end_at",
    "target_date",
    "scheduled_at",
    "resolution_at",
    "promised_date"
}

records = []

for file_path in sorted(RAW_DIR.glob("*.csv")):
    if file_path.stem == "data_dictionary":
        continue

    df = pd.read_csv(file_path)

    for column in df.columns:
        if column in excluded_columns:
            continue

        if is_string_dtype(df[column]):
            series = df[column]
            value_counts = series.value_counts(dropna=False)

            records.append({
                "dataset": file_path.stem,
                "column": column,
                "dtype": str(series.dtype),
                "non_null": int(series.notna().sum()),
                "nulls": int(series.isna().sum()),
                "unique_values": int(series.nunique(dropna=True)),
                "top_values": str(value_counts.head(5).to_dict())
            })

result = pd.DataFrame(records)

print(result.to_string(index=False))

result.to_csv(
    "reports/categorical_inventory.csv",
    index=False
)

print("\nCategorical inventory saved to reports/categorical_inventory.csv")
