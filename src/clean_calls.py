import pandas as pd

raw_path = "data/raw/calls.csv"
clean_path = "data/cleaned/calls.csv"

df = pd.read_csv(raw_path)

df["_agent_present"] = df["agent_id"].notna()

df = (
    df.sort_values(
        ["call_id", "_agent_present"],
        ascending=[True, False]
    )
    .drop_duplicates(
        subset=[
            "call_id",
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
        ],
        keep="first"
    )
    .drop(columns="_agent_present")
)

df.to_csv(
    clean_path,
    index=False
)

print("Raw rows:", 91350)
print("Clean rows:", len(df))
print("Rows removed:", 91350 - len(df))
print("Unique call IDs:", df["call_id"].nunique())
print("Duplicate call IDs:", df["call_id"].duplicated().sum())
print("Output:", clean_path)
