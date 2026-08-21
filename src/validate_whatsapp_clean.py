import pandas as pd

df = pd.read_csv("data/cleaned/whatsapp_events.csv")

print("Rows:", len(df))
print("Unique event IDs:", df["whatsapp_event_id"].nunique())
print("Duplicate event IDs:", df["whatsapp_event_id"].duplicated().sum())
print("Missing event IDs:", df["whatsapp_event_id"].isna().sum())
print("Output:", "data/cleaned/whatsapp_events.csv")
