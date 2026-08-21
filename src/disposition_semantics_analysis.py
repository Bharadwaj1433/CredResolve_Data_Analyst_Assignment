import pandas as pd

dispositions = pd.read_csv("data/raw/call_dispositions.csv")
calls = pd.read_csv("data/raw/calls.csv")
attempts = pd.read_csv("data/raw/call_attempts.csv")

merged_calls = dispositions.merge(
    calls[
        [
            "call_id",
            "call_status",
            "direction",
            "duration_sec"
        ]
    ],
    on="call_id",
    how="left"
)

call_status_summary = (
    merged_calls.groupby(
        [
            "disposition_version",
            "disposition_code",
            "call_status"
        ],
        dropna=False
    )
    .size()
    .reset_index(name="row_count")
    .sort_values(
        [
            "disposition_version",
            "disposition_code",
            "row_count"
        ],
        ascending=[True, True, False]
    )
)

attempt_summary = (
    attempts.groupby(
        ["call_id", "attempt_status"],
        dropna=False
    )
    .size()
    .reset_index(name="attempt_rows")
)

attempt_summary = (
    attempt_summary.groupby(
        ["call_id"],
        dropna=False
    )["attempt_status"]
    .agg(lambda values: ", ".join(sorted(set(values))))
    .reset_index()
)

merged_attempts = dispositions.merge(
    attempt_summary,
    on="call_id",
    how="left"
)

attempt_status_summary = (
    merged_attempts.groupby(
        [
            "disposition_version",
            "disposition_code",
            "attempt_status"
        ],
        dropna=False
    )
    .size()
    .reset_index(name="row_count")
)

call_status_summary.to_csv(
    "reports/disposition_call_status_summary.csv",
    index=False
)

attempt_status_summary.to_csv(
    "reports/disposition_attempt_status_summary.csv",
    index=False
)

print("Disposition rows:", len(dispositions))
print("Disposition codes:", dispositions["disposition_code"].nunique())
print("Disposition versions:", dispositions["disposition_version"].nunique())

print("\nCall status relationships:")
print(call_status_summary.to_string(index=False))

print("\nAttempt status relationships:")
print(attempt_status_summary.to_string(index=False))

print("\nReports:")
print("reports/disposition_call_status_summary.csv")
print("reports/disposition_attempt_status_summary.csv")
