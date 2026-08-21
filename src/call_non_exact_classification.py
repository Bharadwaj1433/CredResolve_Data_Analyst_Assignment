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

results = []

for call_id, group in duplicates.groupby("call_id"):
    unique = group[comparison_columns].nunique(dropna=False)

    if unique.gt(1).any():
        results.append({
            "call_id": call_id,
            "rows": len(group),
            "event_at_conflict": unique["event_at"] > 1,
            "agent_id_conflict": unique["agent_id"] > 1,
            "account_id_conflict": unique["account_id"] > 1,
            "borrower_id_conflict": unique["borrower_id"] > 1,
            "campaign_id_conflict": unique["campaign_id"] > 1,
            "direction_conflict": unique["direction"] > 1,
            "vendor_id_conflict": unique["vendor_id"] > 1,
            "call_status_conflict": unique["call_status"] > 1,
            "duration_conflict": unique["duration_sec"] > 1,
            "timezone_conflict": unique["timezone"] > 1
        })

result = pd.DataFrame(results)

summary = pd.DataFrame({
    "conflict_type": [
        "event_at",
        "agent_id",
        "account_id",
        "borrower_id",
        "campaign_id",
        "direction",
        "vendor_id",
        "call_status",
        "duration_sec",
        "timezone"
    ],
    "groups": [
        result["event_at_conflict"].sum(),
        result["agent_id_conflict"].sum(),
        result["account_id_conflict"].sum(),
        result["borrower_id_conflict"].sum(),
        result["campaign_id_conflict"].sum(),
        result["direction_conflict"].sum(),
        result["vendor_id_conflict"].sum(),
        result["call_status_conflict"].sum(),
        result["duration_conflict"].sum(),
        result["timezone_conflict"].sum()
    ]
})

summary.to_csv(
    "reports/call_conflict_summary.csv",
    index=False
)

result.to_csv(
    "reports/call_non_exact_classification.csv",
    index=False
)

print(summary.to_string(index=False))
print("Report:", "reports/call_conflict_summary.csv")
