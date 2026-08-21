from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

agents = pd.read_csv(RAW_DIR / "agents.csv")

print("Rows:", len(agents))
print("Unique agent IDs:", agents["agent_id"].nunique())
print("Unique employee codes:", agents["employee_code"].nunique())

columns = [
    "employee_code",
    "agent_name",
    "vendor_id",
    "team",
    "status",
    "joined_at",
    "updated_at"
]

records = []

for agent_id, group in agents.groupby("agent_id"):
    record = {
        "agent_id": agent_id,
        "rows": len(group)
    }

    for column in columns:
        record[f"{column}_unique"] = group[column].nunique(dropna=False)

    records.append(record)

variability = pd.DataFrame(records)

print("\nAgent attribute variability:")

for column in columns:
    unique_column = f"{column}_unique"
    affected = (variability[unique_column] > 1).sum()
    print(column, affected)

variability.to_csv(
    REPORT_DIR / "agent_identity_variability.csv",
    index=False
)

employee_mapping = (
    agents.groupby("employee_code")["agent_id"]
    .nunique()
    .reset_index(name="agent_id_count")
)

multiple_agents = employee_mapping[
    employee_mapping["agent_id_count"] > 1
]

print("\nEmployee codes linked to multiple agent IDs:")
print(len(multiple_agents))

multiple_agents.to_csv(
    REPORT_DIR / "employee_agent_mapping_conflicts.csv",
    index=False
)

print("\nReports:")
print("reports/agent_identity_variability.csv")
print("reports/employee_agent_mapping_conflicts.csv")
