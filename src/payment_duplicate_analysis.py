import pandas as pd

input_path = "data/raw/payments.csv"
output_path = "reports/payment_duplicate_analysis.csv"

df = pd.read_csv(input_path)

grouped = (
    df.groupby("payment_id", dropna=False)
    .agg(
        rows=("payment_id", "size"),
        account_id_unique=("account_id", "nunique"),
        borrower_id_unique=("borrower_id", "nunique"),
        amount_unique=("amount", "nunique"),
        payment_status_unique=("payment_status", "nunique"),
        event_at_unique=("event_at", "nunique"),
        method_unique=("payment_method", "nunique"),
    )
    .reset_index()
)

duplicate_groups = grouped[grouped["rows"] > 1].copy()

duplicate_groups["exact_duplicate"] = (
    (duplicate_groups["account_id_unique"] == 1)
    & (duplicate_groups["borrower_id_unique"] == 1)
    & (duplicate_groups["amount_unique"] == 1)
    & (duplicate_groups["payment_status_unique"] == 1)
    & (duplicate_groups["event_at_unique"] == 1)
    & (duplicate_groups["method_unique"] == 1)
)

duplicate_groups["difference_count"] = (
    (duplicate_groups["account_id_unique"] > 1).astype(int)
    + (duplicate_groups["borrower_id_unique"] > 1).astype(int)
    + (duplicate_groups["amount_unique"] > 1).astype(int)
    + (duplicate_groups["payment_status_unique"] > 1).astype(int)
    + (duplicate_groups["event_at_unique"] > 1).astype(int)
    + (duplicate_groups["method_unique"] > 1).astype(int)
)

duplicate_groups.to_csv(output_path, index=False)

print("Duplicate payment groups:", len(duplicate_groups))
print("Exact duplicate groups:", duplicate_groups["exact_duplicate"].sum())
print("Non-exact duplicate groups:", (~duplicate_groups["exact_duplicate"]).sum())
print("Rows involved:", duplicate_groups["rows"].sum())
print("Report:")
print(output_path)
