import pandas as pd
from pathlib import Path

data_path = Path("data/raw")
report_path = Path("reports/borrower_identity_resolution.csv")

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

grouped["conflicting_attributes"] = (
    (grouped["name_unique"] > 1).astype(int)
    + (grouped["phone_unique"] > 1).astype(int)
    + (grouped["email_unique"] > 1).astype(int)
    + (grouped["city_unique"] > 1).astype(int)
    + (grouped["state_unique"] > 1).astype(int)
    + (grouped["created_at_unique"] > 1).astype(int)
    + (grouped["updated_at_unique"] > 1).astype(int)
)

grouped["identity_class"] = "single_stable_record"

grouped.loc[
    (grouped["rows"] > 1) &
    (grouped["conflicting_attributes"] == 0),
    "identity_class"
] = "multiple_identical_records"

grouped.loc[
    grouped["conflicting_attributes"] > 0,
    "identity_class"
] = "attribute_conflict"

grouped.to_csv(
    report_path,
    index=False
)

print("Borrower IDs:", len(grouped))
print("Single stable records:", (grouped["identity_class"] == "single_stable_record").sum())
print("Multiple identical records:", (grouped["identity_class"] == "multiple_identical_records").sum())
print("Attribute conflicts:", (grouped["identity_class"] == "attribute_conflict").sum())
print("Report:", report_path)
