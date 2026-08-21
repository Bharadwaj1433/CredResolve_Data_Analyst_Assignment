import pandas as pd
from pathlib import Path

data_path = Path("data/raw")
report_path = Path("reports/account_borrower_identity_analysis.csv")

accounts = pd.read_csv(data_path / "accounts.csv")
borrowers = pd.read_csv(data_path / "borrowers.csv")

merged = accounts.merge(
    borrowers,
    on="borrower_id",
    how="left",
    suffixes=("_account", "_borrower")
)

grouped = (
    merged.groupby("account_id", dropna=False)
    .agg(
        borrower_id_unique=("borrower_id", "nunique"),
        name_unique=("name", "nunique"),
        phone_unique=("phone", "nunique"),
        email_unique=("email", "nunique"),
        city_unique=("city", "nunique"),
        state_unique=("state", "nunique"),
        borrower_rows=("borrower_id", "size")
    )
    .reset_index()
)

grouped["identity_conflict"] = (
    (grouped["name_unique"] > 1)
    | (grouped["phone_unique"] > 1)
    | (grouped["email_unique"] > 1)
    | (grouped["city_unique"] > 1)
    | (grouped["state_unique"] > 1)
)

grouped.to_csv(
    report_path,
    index=False
)

print("Accounts:", len(grouped))
print("Accounts with multiple borrower IDs:", (grouped["borrower_id_unique"] > 1).sum())
print("Accounts with identity conflicts:", grouped["identity_conflict"].sum())
print("Accounts with no borrower match:", grouped["borrower_rows"].eq(0).sum())
print("Report:", report_path)
