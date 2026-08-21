import pandas as pd
from pathlib import Path

data_path = Path("data/raw")
report_path = Path("reports/borrower_identity_conflict_summary.csv")

df = pd.read_csv(data_path / "borrowers.csv")

grouped = (
    df.groupby("borrower_id", dropna=False)
    .agg(
        rows=("borrower_id", "size"),
        name_unique=("name", "nunique"),
        phone_unique=("phone", "nunique"),
        email_unique=("email", "nunique"),
        city_unique=("city", "nunique"),
        state_unique=("state", "nunique"),
        created_at_unique=("created_at", "nunique"),
        updated_at_unique=("updated_at", "nunique")
    )
    .reset_index()
)

summary = pd.DataFrame({
    "attribute": [
        "name",
        "phone",
        "email",
        "city",
        "state",
        "created_at",
        "updated_at"
    ],
    "borrower_ids_with_conflict": [
        (grouped["name_unique"] > 1).sum(),
        (grouped["phone_unique"] > 1).sum(),
        (grouped["email_unique"] > 1).sum(),
        (grouped["city_unique"] > 1).sum(),
        (grouped["state_unique"] > 1).sum(),
        (grouped["created_at_unique"] > 1).sum(),
        (grouped["updated_at_unique"] > 1).sum()
    ]
})

summary["percentage_of_borrower_ids"] = (
    summary["borrower_ids_with_conflict"]
    / len(grouped)
    * 100
).round(2)

summary.to_csv(
    report_path,
    index=False
)

print(summary.to_string(index=False))
print("Report:", report_path)
