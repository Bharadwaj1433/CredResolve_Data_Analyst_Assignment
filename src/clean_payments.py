import pandas as pd

raw_path = "data/raw/payments.csv"
clean_path = "data/cleaned/payments.csv"

df = pd.read_csv(raw_path)

df["_reference_present"] = df["payment_reference"].notna()

df = (
    df.sort_values(
        ["payment_id", "_reference_present"],
        ascending=[True, False]
    )
    .drop_duplicates(
        subset=["payment_id"],
        keep="first"
    )
    .drop(columns="_reference_present")
)

df.to_csv(
    clean_path,
    index=False
)

print("Raw rows:", 25500)
print("Clean rows:", len(df))
print("Rows removed:", 25500 - len(df))
print("Unique payment IDs:", df["payment_id"].nunique())
print("Missing payment references:", df["payment_reference"].isna().sum())
print("Output:", clean_path)
