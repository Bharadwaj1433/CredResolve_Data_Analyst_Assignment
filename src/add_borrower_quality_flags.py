import pandas as pd
from pathlib import Path

data_path = Path("data/cleaned")

borrowers = pd.read_csv(
    data_path / "borrowers.csv",
    usecols=["borrower_id"]
)

valid_borrowers = set(
    borrowers["borrower_id"].dropna()
)

tables = [
    "accounts",
    "calls",
    "call_attempts",
    "call_dispositions",
    "whatsapp_events",
    "sms_events",
    "field_visits",
    "promises_to_pay",
    "payments",
    "complaints",
    "account_status_history"
]

for table in tables:
    path = data_path / f"{table}.csv"
    df = pd.read_csv(path)

    if "borrower_id" not in df.columns:
        continue

    df["borrower_id_unresolved"] = (
        df["borrower_id"].notna()
        & ~df["borrower_id"].isin(valid_borrowers)
    )

    df.to_csv(path, index=False)

    print(
        table,
        "unresolved:",
        int(df["borrower_id_unresolved"].sum())
    )

print("Borrower relationship flags added")
