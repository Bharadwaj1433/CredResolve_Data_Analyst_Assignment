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

exact_groups = 0
non_exact_groups = 0
rows_exact = 0
rows_non_exact = 0

for call_id, group in duplicates.groupby("call_id"):
    if group[comparison_columns].drop_duplicates().shape[0] == 1:
        exact_groups += 1
        rows_exact += len(group) - 1
    else:
        non_exact_groups += 1
        rows_non_exact += len(group)

print("Duplicate call groups:", len(duplicate_ids))
print("Exact duplicate groups:", exact_groups)
print("Rows removable as exact duplicates:", rows_exact)
print("Non-exact duplicate groups:", non_exact_groups)
print("Rows in non-exact groups:", rows_non_exact)

duplicates.to_csv(
    "reports/call_duplicate_groups.csv",
    index=False
)

print("Report:", "reports/call_duplicate_groups.csv")
