import pandas as pd

input_path = "data/raw/whatsapp_events.csv"
output_path = "reports/whatsapp_duplicate_analysis.csv"

df = pd.read_csv(input_path)

grouped = (
    df.groupby("whatsapp_event_id", dropna=False)
    .agg(
        rows=("whatsapp_event_id", "size"),
        account_id_unique=("account_id", "nunique"),
        borrower_id_unique=("borrower_id", "nunique"),
        event_at_unique=("event_at", "nunique"),
        message_id_unique=("message_id", "nunique"),
        event_type_unique=("event_type", "nunique"),
        template_code_unique=("template_code", "nunique"),
        provider_id_unique=("provider_id", "nunique")
    )
    .reset_index()
)

duplicate_groups = grouped[grouped["rows"] > 1].copy()

columns = [
    "account_id_unique",
    "borrower_id_unique",
    "event_at_unique",
    "message_id_unique",
    "event_type_unique",
    "template_code_unique",
    "provider_id_unique"
]

duplicate_groups["difference_count"] = (
    duplicate_groups[columns].gt(1).sum(axis=1)
)

duplicate_groups["exact_duplicate"] = (
    duplicate_groups["difference_count"] == 0
)

duplicate_groups.to_csv(output_path, index=False)

print("Duplicate WhatsApp groups:", len(duplicate_groups))
print("Exact duplicate groups:", duplicate_groups["exact_duplicate"].sum())
print("Non-exact duplicate groups:", (~duplicate_groups["exact_duplicate"]).sum())
print("Rows involved:", duplicate_groups["rows"].sum())
print("Report:")
print(output_path)
