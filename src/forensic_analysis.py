import pandas as pd
from pathlib import Path

BASE = Path("data/cleaned")
REPORTS = Path("reports")

accounts = pd.read_csv(BASE / "accounts.csv")
payments = pd.read_csv(BASE / "payments.csv")
calls = pd.read_csv(BASE / "calls.csv")
attempts = pd.read_csv(BASE / "call_attempts.csv")
vendors = pd.read_csv(BASE / "vendor_telephony.csv")

payments["event_at"] = pd.to_datetime(payments["event_at"], errors="coerce")
calls["event_at"] = pd.to_datetime(calls["event_at"], errors="coerce")
attempts["event_at"] = pd.to_datetime(attempts["event_at"], errors="coerce")

successful = payments[
    payments["payment_status"].astype(str).str.upper().eq("SUCCESS")
].copy()

payment_checks = pd.DataFrame([
    {
        "check": "successful_payment_records",
        "value": successful["payment_id"].nunique(),
        "interpretation": "Successful payment records available for attribution analysis"
    },
    {
        "check": "successful_payment_accounts",
        "value": successful["account_id"].nunique(),
        "interpretation": "Accounts receiving successful payments"
    },
    {
        "check": "missing_payment_reference_successful",
        "value": successful["payment_reference"].isna().sum(),
        "interpretation": "Successful payments without payment reference"
    },
    {
        "check": "unresolved_borrower_successful",
        "value": successful["borrower_id_unresolved"].sum()
        if "borrower_id_unresolved" in successful.columns else 0,
        "interpretation": "Successful payments with unresolved borrower relationship"
    }
])

payment_checks.to_csv(
    REPORTS / "forensic_payment_attribution.csv",
    index=False
)

if "vendor_id" in calls.columns:
    vendor_call = (
        calls.groupby("vendor_id", dropna=False)
        .agg(
            calls=("call_id", "nunique"),
            answered_calls=("answered_flag", "sum")
            if "answered_flag" in calls.columns
            else ("call_id", "count")
        )
        .reset_index()
    )

    if "answered_flag" in calls.columns:
        vendor_call["answer_rate_pct"] = (
            vendor_call["answered_calls"]
            / vendor_call["calls"].replace(0, pd.NA)
            * 100
        )
else:
    vendor_call = pd.DataFrame()

vendor_call.to_csv(
    REPORTS / "forensic_vendor_performance.csv",
    index=False
)

calls["hour"] = calls["event_at"].dt.hour

time_analysis = (
    calls.groupby("hour", dropna=False)
    .agg(
        calls=("call_id", "nunique"),
        answered_calls=("answered_flag", "sum")
        if "answered_flag" in calls.columns
        else ("call_id", "count")
    )
    .reset_index()
)

if "answered_flag" in calls.columns:
    time_analysis["answer_rate_pct"] = (
        time_analysis["answered_calls"]
        / time_analysis["calls"].replace(0, pd.NA)
        * 100
    )

time_analysis.to_csv(
    REPORTS / "forensic_calling_time.csv",
    index=False
)

attempt_analysis = (
    attempts.groupby("account_id", dropna=False)
    .agg(
        call_attempts=("account_id", "size")
    )
    .reset_index()
)

payment_accounts = set(successful["account_id"].dropna())

attempt_analysis["successful_payment"] = (
    attempt_analysis["account_id"].isin(payment_accounts)
)

attempt_analysis["attempt_band"] = pd.cut(
    attempt_analysis["call_attempts"],
    bins=[0, 1, 2, 3, 5, 10, float("inf")],
    labels=["1", "2", "3", "4-5", "6-10", "11+"]
)

attempt_summary = (
    attempt_analysis.groupby("attempt_band", observed=True)
    .agg(
        accounts=("account_id", "nunique"),
        paying_accounts=("successful_payment", "sum")
    )
    .reset_index()
)

attempt_summary["payment_account_rate_pct"] = (
    attempt_summary["paying_accounts"]
    / attempt_summary["accounts"].replace(0, pd.NA)
    * 100
)

attempt_summary.to_csv(
    REPORTS / "forensic_attempt_frequency.csv",
    index=False
)

lines = [
    "# Forensic Analysis Findings",
    "",
    "## Payment Attribution",
    "",
    f"Successful payment records analyzed: {successful['payment_id'].nunique():,}.",
    f"Accounts with successful payments: {successful['account_id'].nunique():,}.",
    f"Successful payments missing payment references: {successful['payment_reference'].isna().sum():,}.",
    "",
    "Payment attribution should be performed at account level because account_id",
    "is the canonical analytical entity.",
    "",
    "## Vendor Performance",
    "",
    "Vendor-level call performance is available for comparative analysis.",
    "Vendor differences should not be interpreted as causal without controlling",
    "for campaign, portfolio, channel, and agent mix.",
    "",
    "## Calling Time",
    "",
    "Call answer rates vary by hour and should be evaluated before selecting",
    "calling windows for operational changes.",
    "",
    "## Attempt Frequency",
    "",
    "Payment conversion varies across attempt-frequency bands.",
    "Higher attempt counts should not automatically be interpreted as better",
    "performance because accounts receiving more attempts may be systematically",
    "harder or easier to recover.",
    "",
    "## Conclusion",
    "",
    "The forensic evidence supports further investigation of attribution,",
    "vendor, calling-time, and attempt-frequency effects.",
    "These relationships are observational and should not be treated as causal",
    "without cohort or controlled analysis."
]

(REPORTS / "forensic_analysis_findings.md").write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print("Forensic analysis completed")
print("Reports:")
print("reports/forensic_payment_attribution.csv")
print("reports/forensic_vendor_performance.csv")
print("reports/forensic_calling_time.csv")
print("reports/forensic_attempt_frequency.csv")
print("reports/forensic_analysis_findings.md")
