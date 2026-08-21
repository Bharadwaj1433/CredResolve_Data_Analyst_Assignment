import pandas as pd
from pathlib import Path

data_path = Path("data/cleaned")

checks = {
    "calls": ["agent_id"],
    "call_attempts": ["vendor_id"],
    "payments": ["payment_reference"],
    "accounts": ["borrower_id"]
}

for table, columns in checks.items():
    path = data_path / f"{table}.csv"
    df = pd.read_csv(path)

    for column in columns:
        if column in df.columns:
            flag = f"{column}_missing"
            df[flag] = df[column].isna()

            print(
                table,
                column,
                "missing:",
                int(df[flag].sum())
            )

    df.to_csv(path, index=False)

print("Missing identifier flags added")
