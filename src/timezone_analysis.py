import pandas as pd
from pathlib import Path

data_path = Path("data/raw")
report_path = Path("reports/timezone_analysis.csv")

tables = {
    "accounts": "timezone",
    "calls": "timezone",
    "agent_sessions": "timezone",
    "vendor_telephony": "timezone"
}

results = []

for table, column in tables.items():
    df = pd.read_csv(data_path / f"{table}.csv")

    counts = (
        df[column]
        .value_counts(dropna=False)
        .reset_index()
    )

    counts.columns = [column, "row_count"]

    for _, row in counts.iterrows():
        results.append({
            "dataset": table,
            "timezone": row[column],
            "row_count": int(row["row_count"])
        })

result = pd.DataFrame(results)

result.to_csv(
    report_path,
    index=False
)

print(result.to_string(index=False))
print("Report:", report_path)
