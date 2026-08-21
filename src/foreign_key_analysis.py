from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")

relationships = [
    ("accounts", "borrower_id", "borrowers", "borrower_id"),
    ("agent_sessions", "agent_id", "agents", "agent_id"),
    ("daily_targeting", "account_id", "accounts", "account_id"),
    ("daily_targeting", "campaign_id", "campaigns", "campaign_id"),
    ("calls", "account_id", "accounts", "account_id"),
    ("calls", "borrower_id", "borrowers", "borrower_id"),
    ("calls", "agent_id", "agents", "agent_id"),
    ("calls", "campaign_id", "campaigns", "campaign_id"),
    ("call_attempts", "account_id", "accounts", "account_id"),
    ("call_attempts", "borrower_id", "borrowers", "borrower_id"),
    ("call_attempts", "call_id", "calls", "call_id"),
    ("call_attempts", "agent_id", "agents", "agent_id"),
    ("call_dispositions", "account_id", "accounts", "account_id"),
    ("call_dispositions", "borrower_id", "borrowers", "borrower_id"),
    ("call_dispositions", "call_id", "calls", "call_id"),
    ("call_dispositions", "agent_id", "agents", "agent_id"),
    ("whatsapp_events", "account_id", "accounts", "account_id"),
    ("whatsapp_events", "borrower_id", "borrowers", "borrower_id"),
    ("sms_events", "account_id", "accounts", "account_id"),
    ("sms_events", "borrower_id", "borrowers", "borrower_id"),
    ("field_visits", "account_id", "accounts", "account_id"),
    ("field_visits", "borrower_id", "borrowers", "borrower_id"),
    ("field_visits", "agent_id", "agents", "agent_id"),
    ("promises_to_pay", "account_id", "accounts", "account_id"),
    ("promises_to_pay", "borrower_id", "borrowers", "borrower_id"),
    ("promises_to_pay", "agent_id", "agents", "agent_id"),
    ("payments", "account_id", "accounts", "account_id"),
    ("payments", "borrower_id", "borrowers", "borrower_id"),
    ("complaints", "account_id", "accounts", "account_id"),
    ("complaints", "borrower_id", "borrowers", "borrower_id"),
    ("account_status_history", "account_id", "accounts", "account_id"),
    ("account_status_history", "borrower_id", "borrowers", "borrower_id"),
    ("agents", "vendor_id", "vendor_telephony", "vendor_id"),
]

results = []

cache = {}

for child_table, child_column, parent_table, parent_column in relationships:
    if parent_table not in cache:
        parent_df = pd.read_csv(RAW_DIR / f"{parent_table}.csv")
        cache[parent_table] = set(
            parent_df[parent_column].dropna().astype(str)
        )

    child_df = pd.read_csv(RAW_DIR / f"{child_table}.csv")

    child_values = child_df[child_column].dropna().astype(str)

    orphan_count = (~child_values.isin(cache[parent_table])).sum()

    results.append({
        "child_table": child_table,
        "child_column": child_column,
        "parent_table": parent_table,
        "parent_column": parent_column,
        "child_non_null_values": len(child_values),
        "orphan_values": int(orphan_count),
        "orphan_pct": round(
            orphan_count / len(child_values) * 100, 2
        ) if len(child_values) else 0
    })

result = pd.DataFrame(results)

print(result.to_string(index=False))

result.to_csv(
    "reports/foreign_key_analysis.csv",
    index=False
)

print("\nForeign key analysis saved to reports/foreign_key_analysis.csv")
