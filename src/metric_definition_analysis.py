import pandas as pd
from pathlib import Path

BASE = Path("data/cleaned")
REPORTS = Path("reports")

accounts = pd.read_csv(BASE / "accounts.csv")
calls = pd.read_csv(BASE / "calls.csv")
payments = pd.read_csv(BASE / "payments.csv")
ptp = pd.read_csv(BASE / "promises_to_pay.csv")

successful = payments[
    payments["payment_status"].astype(str).str.upper().eq("SUCCESS")
].copy()

rows = [
    {
        "metric": "recovery_rate",
        "numerator": "successful payment amount",
        "denominator": "eligible outstanding amount",
        "available": "PARTIAL",
        "current_measurement": "Available at portfolio level",
        "limitation": "Historical monthly eligible outstanding balance is unavailable"
    },
    {
        "metric": "contact_rate",
        "numerator": "accounts with answered calls",
        "denominator": "accounts attempted",
        "available": "YES",
        "current_measurement": "Can be calculated from calls",
        "limitation": "Answered-call status depends on operational call-status semantics"
    },
    {
        "metric": "RPC",
        "numerator": "accounts with right-party contact",
        "denominator": "accounts contacted",
        "available": "NO",
        "current_measurement": "No validated RPC definition exists in current analysis",
        "limitation": "Requires reliable right-party-contact classification"
    },
    {
        "metric": "PTP_rate",
        "numerator": "accounts with PTP",
        "denominator": "accounts contacted or eligible accounts",
        "available": "PARTIAL",
        "current_measurement": "PTP records are available",
        "limitation": "Business denominator must be explicitly defined"
    },
    {
        "metric": "PTP_kept_rate",
        "numerator": "kept PTPs",
        "denominator": "PTPs",
        "available": "PARTIAL",
        "current_measurement": "PTP records exist",
        "limitation": "Kept-status semantics require validated disposition/payment linkage"
    },
    {
        "metric": "recovery_per_account",
        "numerator": "successful payment amount",
        "denominator": "accounts",
        "available": "YES",
        "current_measurement": "Can be calculated",
        "limitation": "Not equivalent to recovery rate"
    },
    {
        "metric": "recovery_per_call",
        "numerator": "successful payment amount",
        "denominator": "calls",
        "available": "YES",
        "current_measurement": "Can be calculated",
        "limitation": "Does not prove call causality"
    },
    {
        "metric": "recovery_per_answered_call",
        "numerator": "successful payment amount",
        "denominator": "answered calls",
        "available": "YES",
        "current_measurement": "Can be calculated",
        "limitation": "Does not establish causal attribution"
    }
]

analysis = pd.DataFrame(rows)

portfolio_outstanding = accounts["outstanding_amount"].sum()
recovered_amount = successful["amount"].sum()
account_count = accounts["account_id"].nunique()
payment_count = successful["payment_id"].nunique()

answered_statuses = {
    "ANSWERED",
    "CONNECTED",
    "RPC",
    "RIGHT_PARTY_CONTACT"
}

calls["call_status_norm"] = (
    calls["call_status"].astype(str).str.upper().str.strip()
)

answered = calls[
    calls["call_status_norm"].isin(answered_statuses)
]

answered_accounts = answered["account_id"].nunique()

metrics = pd.DataFrame([
    {
        "metric": "portfolio_recovery_rate",
        "value": recovered_amount / portfolio_outstanding * 100,
        "numerator": recovered_amount,
        "denominator": portfolio_outstanding,
        "interpretation": "Portfolio-level observed rate only"
    },
    {
        "metric": "recovery_per_account",
        "value": recovered_amount / account_count,
        "numerator": recovered_amount,
        "denominator": account_count,
        "interpretation": "Descriptive recovery efficiency"
    },
    {
        "metric": "recovery_per_successful_payment",
        "value": recovered_amount / payment_count,
        "numerator": recovered_amount,
        "denominator": payment_count,
        "interpretation": "Average successful payment"
    },
    {
        "metric": "answered_account_rate",
        "value": answered_accounts / account_count * 100,
        "numerator": answered_accounts,
        "denominator": account_count,
        "interpretation": "Portfolio contact coverage"
    }
])

analysis.to_csv(
    REPORTS / "metric_definition_analysis.csv",
    index=False
)

metrics.to_csv(
    REPORTS / "metric_definition_metrics.csv",
    index=False
)

findings = f"""# Metric Definition Analysis

## Portfolio Metrics

Accounts: {account_count:,}

Outstanding amount: {portfolio_outstanding:,.2f}

Successful payment amount: {recovered_amount:,.2f}

Successful payments: {payment_count:,}

Observed portfolio recovery rate:
{recovered_amount / portfolio_outstanding * 100:.2f}%

Answered accounts:
{answered_accounts:,}

Answered-account coverage:
{answered_accounts / account_count * 100:.2f}%

## 11% Improvement Assessment

The available data does not currently provide sufficient evidence to
validate an 11% improvement in true recovery rate over time.

The main limitation is the absence of historical monthly eligible
outstanding-balance denominators.

Recovered amount can be compared across months, but recovered amount
alone is not a normalized recovery-rate measure.

Metrics such as recovery per account, recovery per call, and
recovery per answered call can be calculated, but they measure
different concepts and cannot be substituted for recovery rate.

RPC cannot currently be reported as a validated metric because a
reliable right-party-contact classification has not yet been established.

PTP rate and PTP kept rate require explicit denominator and status
definitions before being used for an improvement claim.

## Conclusion

The reported 11% improvement should currently be classified as
UNVERIFIED.

Before accepting the claim, the analysis must control for:
- historical eligible balance
- portfolio mix
- DPD mix
- campaign mix
- channel mix
- contact selection
- attribution window
- time-period completeness
"""

(REPORTS / "metric_definition_findings.md").write_text(
    findings,
    encoding="utf-8"
)

print("Metric definition analysis completed")
print("Reports:")
print("reports/metric_definition_analysis.csv")
print("reports/metric_definition_metrics.csv")
print("reports/metric_definition_findings.md")
