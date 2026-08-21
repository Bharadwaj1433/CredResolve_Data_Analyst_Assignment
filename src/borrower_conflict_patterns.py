import pandas as pd
from pathlib import Path

data_path = Path("data/raw")
report_path = Path("reports/borrower_conflict_patterns.csv")

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

grouped["identity_fields_conflicting"] = (
    (grouped["name_unique"] > 1).astype(int)
    + (grouped["phone_unique"] > 1).astype(int)
    + (grouped["email_unique"] > 1).astype(int)
    + (grouped["city_unique"] > 1).astype(int)
    + (grouped["state_unique"] > 1).astype(int)
)

pattern = (
    grouped[grouped["identity_fields_conflicting"] > 0]
    .groupby("identity_fields_conflicting")
    .size()
    .reset_index(name="borrower_id_count")
)

pattern["percentage"] = (
    pattern["borrower_id_count"]
    / len(grouped)
    * 100
).round(2)

pattern.to_csv(
    report_path,
    index=False
)

print(pattern.to_string(index=False))
print("Report:", report_path)
