import pandas as pd

input_path = "data/raw/call_dispositions.csv"
output_path = "reports/disposition_code_analysis.csv"

df = pd.read_csv(input_path)

combination = (
    df.groupby(
        ["disposition_version", "disposition_code"],
        dropna=False
    )
    .size()
    .reset_index(name="row_count")
    .sort_values(
        ["disposition_version", "disposition_code"]
    )
)

combination.to_csv(
    output_path,
    index=False
)

print("Disposition versions:")
print(df["disposition_version"].value_counts())

print("\nDisposition codes:")
print(df["disposition_code"].value_counts())

print("\nVersion and code combinations:")
print(combination.to_string(index=False))

print("\nReport:")
print(output_path)
