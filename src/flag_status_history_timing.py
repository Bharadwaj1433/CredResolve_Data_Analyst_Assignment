import pandas as pd

path = "data/cleaned/account_status_history.csv"

df = pd.read_csv(path)

df["event_at"] = pd.to_datetime(
    df["event_at"],
    errors="coerce"
)

df["recorded_at"] = pd.to_datetime(
    df["recorded_at"],
    errors="coerce"
)

df["recorded_before_event"] = (
    df["recorded_at"] < df["event_at"]
)

df.to_csv(
    path,
    index=False
)

print("Rows:", len(df))
print("Recorded before event:", int(df["recorded_before_event"].sum()))
print("Valid event timestamps:", int(df["event_at"].notna().sum()))
print("Valid recorded timestamps:", int(df["recorded_at"].notna().sum()))
print("Output:", path)
