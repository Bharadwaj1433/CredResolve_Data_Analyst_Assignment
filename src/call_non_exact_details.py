import pandas as pd

df = pd.read_csv("data/raw/calls.csv")

counts = df.groupby("call_id").size()
duplicate_ids = counts[counts > 1].index

duplicates = df[df["call_id"].isin(duplicate_ids)].copy()

comparison_columns = [
    "account_id",
    "borrower_id",
    "event_at",
    "agent_id",
    "campaign_id",
    "direction",
    "vendor_id",
    "call_status",
    "duration_sec",
    "timezone"
]

non_exact = []

for call_id, group in duplicates.groupby("call_id"):
    if group[comparison_columns].drop_duplicates().shape[0] > 1:
        non_exact.append(group)

result = pd.concat(non_exact, ignore_index=True)

result.to_csv(
    "reports/call_non_exact_duplicates.csv",
    index=False
)

print("Non-exact call groups:", result["call_id"].nunique())
print("Rows involved:", len(result))
print("Report:", "reports/call_non_exact_duplicates.csv")
print(result.to_string(index=False))
