import pandas as pd

df = pd.read_csv("data/raw/borrowers.csv")

duplicate_rows = df[df.duplicated(keep=False)].copy()

print("Exact duplicate rows:", len(duplicate_rows))
print("Borrower IDs involved:", duplicate_rows["borrower_id"].nunique())

duplicate_rows.to_csv(
    "reports/borrower_exact_duplicates.csv",
    index=False
)

print("Report:", "reports/borrower_exact_duplicates.csv")
