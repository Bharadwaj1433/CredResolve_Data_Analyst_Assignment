import pandas as pd
from pathlib import Path

BASE = Path("data/cleaned")
REPORTS = Path("reports")

accounts = pd.read_csv(BASE / "accounts.csv")
payments = pd.read_csv(BASE / "payments.csv")
calls = pd.read_csv(BASE / "calls.csv")

payments["event_at"] = pd.to_datetime(payments["event_at"], errors="coerce")
calls["event_at"] = pd.to_datetime(calls["event_at"], errors="coerce")

successful = payments[
    payments["payment_status"].astype(str).str.upper().eq("SUCCESS")
].copy()

successful["month"] = successful["event_at"].dt.to_period("M").astype(str)

accounts["dpd_band"] = pd.cut(
    accounts["dpd"],
    bins=[-1, 0, 30, 60, 90, 180, float("inf")],
    labels=["0", "1-30", "31-60", "61-90", "91-180", "181+"]
)

dimensions = [
    "risk_segment",
    "dpd_band",
    "status",
    "loan_type"
]

rows = []

for dimension in dimensions:
    portfolio = (
        accounts.groupby(dimension, dropna=False)
        .agg(
            accounts=("account_id", "nunique"),
            outstanding_amount=("outstanding_amount", "sum")
        )
        .reset_index()
    )

    paid = successful.merge(
        accounts[["account_id", dimension]],
        on="account_id",
        how="left"
    )

    recovery = (
        paid.groupby(dimension, dropna=False)
        .agg(
            recovered_amount=("amount", "sum"),
            paying_accounts=("account_id", "nunique"),
            successful_payments=("payment_id", "nunique")
        )
        .reset_index()
    )

    result = portfolio.merge(
        recovery,
        on=dimension,
        how="left"
    )

    result["recovered_amount"] = result["recovered_amount"].fillna(0)
    result["paying_accounts"] = result["paying_accounts"].fillna(0)
    result["successful_payments"] = result["successful_payments"].fillna(0)

    result["recovery_rate_pct"] = (
        result["recovered_amount"]
        / result["outstanding_amount"].replace(0, pd.NA)
        * 100
    )

    result["dimension"] = dimension

    rows.append(result)

mix = pd.concat(rows, ignore_index=True)

mix.to_csv(
    REPORTS / "statistical_investigation.csv",
    index=False
)

monthly = (
    successful.groupby("month")
    .agg(
        recovered_amount=("amount", "sum"),
        paying_accounts=("account_id", "nunique"),
        successful_payments=("payment_id", "nunique")
    )
    .reset_index()
)

monthly["recovered_per_paying_account"] = (
    monthly["recovered_amount"]
    / monthly["paying_accounts"].replace(0, pd.NA)
)

monthly["recovered_per_successful_payment"] = (
    monthly["recovered_amount"]
    / monthly["successful_payments"].replace(0, pd.NA)
)

monthly.to_csv(
    REPORTS / "statistical_monthly_summary.csv",
    index=False
)

calls["month"] = calls["event_at"].dt.to_period("M").astype(str)

if "answered_flag" in calls.columns:
    monthly_calls = (
        calls.groupby("month")
        .agg(
            calls=("call_id", "nunique"),
            answered_calls=("answered_flag", "sum"),
            accounts_contacted=("account_id", "nunique")
        )
        .reset_index()
    )

    monthly_calls["answer_rate_pct"] = (
        monthly_calls["answered_calls"]
        / monthly_calls["calls"].replace(0, pd.NA)
        * 100
    )

    monthly_calls.to_csv(
        REPORTS / "statistical_contact_summary.csv",
        index=False
    )

lines = [
    "# Statistical Investigation Findings",
    "",
    "## Portfolio Mix",
    "",
    "Recovery performance differs across risk, DPD, account-status, and loan-type segments.",
    "Therefore aggregate recovery can change when the composition of the handled portfolio changes.",
    "",
    "## Cohort Effects",
    "",
    "The available data does not provide historical monthly eligible balances for comparable cohorts.",
    "A controlled before-and-after cohort recovery rate therefore cannot be reconstructed.",
    "",
    "## Selection Bias",
    "",
    "Accounts receiving calls, PTPs, or other interventions are not necessarily a random sample of the portfolio.",
    "Higher activity may reflect accounts that were easier or harder to recover.",
    "",
    "## Survivorship Bias",
    "",
    "Accounts remaining active in later periods may differ systematically from accounts resolved earlier.",
    "The current data does not provide sufficient historical snapshots to fully reconstruct this effect.",
    "",
    "## Simpson's Paradox",
    "",
    "Aggregate recovery can differ from segment-level recovery because the portfolio mix changes.",
    "Segment-level analysis is therefore required before interpreting aggregate movement.",
    "",
    "## Attribution Window",
    "",
    "A payment occurring after a call or other intervention does not by itself prove that the intervention caused the payment.",
    "A validated attribution window is required for causal interpretation.",
    "",
    "## Time-Series Effects",
    "",
    "Monthly activity contains boundary-period effects.",
    "The first observed month has extremely low activity and the final observed month is substantially lower than preceding months.",
    "These periods should not be interpreted as clean evidence of operational deterioration or improvement.",
    "",
    "## Conclusion",
    "",
    "The available evidence does not establish a causal 11% improvement.",
    "The reported improvement remains unverified because portfolio mix, cohort comparability, selection, survivorship, attribution timing, and historical denominators are not sufficiently controlled."
]

(REPORTS / "statistical_investigation_findings.md").write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print("Statistical investigation completed")
print("Reports:")
print("reports/statistical_investigation.csv")
print("reports/statistical_monthly_summary.csv")
print("reports/statistical_investigation_findings.md")
