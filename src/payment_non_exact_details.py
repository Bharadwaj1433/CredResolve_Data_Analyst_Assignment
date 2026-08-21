import pandas as pd

df = pd.read_csv("data/raw/payments.csv")

counts = df.groupby("payment_id").size()
duplicate_ids = counts[counts > 1].index

duplicates = df[df["payment_id"].isin(duplicate_ids)].copy()

comparison_columns = [
    "account_id",
    "borrower_id",
    "event_at",
    "amount",
    "payment_status",
    "payment_method",
    "payment_reference",
    "provider_id"
]

groups = []

for payment_id, group in duplicates.groupby("payment_id"):
    if group[comparison_columns].nunique(dropna=False).gt(1).any():
        groups.append(group)

result = pd.concat(groups, ignore_index=True)

result.to_csv(
    "reports/payment_non_exact_duplicates.csv",
    index=False
)

print("Non-exact payment groups:", result["payment_id"].nunique())
print("Rows involved:", len(result))
print("Report:", "reports/payment_non_exact_duplicates.csv")
print(result.to_string(index=False))
