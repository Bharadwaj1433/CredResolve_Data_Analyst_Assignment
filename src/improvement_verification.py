import pandas as pd
from pathlib import Path

BASE = Path("data/cleaned")
REPORTS = Path("reports")

accounts = pd.read_csv(BASE / "accounts.csv")
payments = pd.read_csv(BASE / "payments.csv")

accounts["opened_at"] = pd.to_datetime(accounts["opened_at"], errors="coerce")
payments["event_at"] = pd.to_datetime(payments["event_at"], errors="coerce")

successful = payments[
    payments["payment_status"].astype(str).str.upper().eq("SUCCESS")
].copy()

successful["month"] = successful["event_at"].dt.to_period("M").astype(str)

account_month = (
    successful.groupby("month")
    .agg(
        recovered_amount=("amount", "sum"),
        successful_payment_count=("payment_id", "nunique"),
        paying_accounts=("account_id", "nunique")
    )
    .reset_index()
)

accounts["dpd_band"] = pd.cut(
    accounts["dpd"],
    bins=[-1, 0, 30, 60, 90, 180, float("inf")],
    labels=["0", "1-30", "31-60", "61-90", "91-180", "181+"]
)

mix_dimensions = [
    "risk_segment",
    "dpd_band",
    "status",
    "loan_type"
]

results = []

for dimension in mix_dimensions:

    if dimension not in accounts.columns:
        continue

    portfolio = (
        accounts.groupby(dimension, dropna=False)
        .agg(
            accounts=("account_id", "nunique"),
            outstanding_amount=("outstanding_amount", "sum")
        )
        .reset_index()
    )

    portfolio["portfolio_share_pct"] = (
        portfolio["outstanding_amount"]
        / portfolio["outstanding_amount"].sum()
        * 100
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
            successful_payments=("payment_id", "nunique"),
            paying_accounts=("account_id", "nunique")
        )
        .reset_index()
    )

    result = portfolio.merge(
        recovery,
        on=dimension,
        how="left"
    )

    result["recovered_amount"] = result["recovered_amount"].fillna(0)
    result["successful_payments"] = result["successful_payments"].fillna(0)
    result["paying_accounts"] = result["paying_accounts"].fillna(0)

    result["observed_recovery_rate_pct"] = (
        result["recovered_amount"]
        / result["outstanding_amount"].replace(0, pd.NA)
        * 100
    )

    result["dimension"] = dimension

    results.append(result)

mix_analysis = pd.concat(results, ignore_index=True)

mix_analysis.to_csv(
    REPORTS / "improvement_verification.csv",
    index=False
)

overall_recovered = successful["amount"].sum()
overall_outstanding = accounts["outstanding_amount"].sum()

overall_rate = (
    overall_recovered
    / overall_outstanding
    * 100
)

first_month = successful["month"].min()
last_month = successful["month"].max()

first_recovery = (
    successful.loc[
        successful["month"] == first_month,
        "amount"
    ].sum()
)

last_recovery = (
    successful.loc[
        successful["month"] == last_month,
        "amount"
    ].sum()
)

lines = []

lines.append("# Improvement Verification")
lines.append("")
lines.append(
    f"Observed successful-payment period: {first_month} to {last_month}."
)
lines.append("")
lines.append(
    f"Observed portfolio recovery rate using the current outstanding "
    f"denominator: {overall_rate:.2f}%."
)
lines.append("")
lines.append("## Portfolio Mix Findings")
lines.append("")
lines.append(
    "Recovery performance differs across portfolio segments."
)
lines.append(
    "These differences demonstrate that changes in portfolio composition "
    "can affect aggregate recovery without requiring an operational "
    "performance improvement."
)
lines.append("")
lines.append(
    "The available data does not provide historical monthly outstanding "
    "balances by cohort. Therefore a true monthly mix-adjusted recovery "
    "rate cannot be reconstructed."
)
lines.append("")
lines.append("## 11% Improvement Assessment")
lines.append("")
lines.append(
    "The 11% improvement remains UNVERIFIED."
)
lines.append("")
lines.append(
    "The current data supports descriptive comparison of recovery amounts "
    "and segment-level recovery performance, but it does not support a "
    "causal or mix-adjusted claim that recovery improved by 11%."
)
lines.append("")
lines.append(
    "A valid verification would require time-specific eligible balances "
    "and comparable cohorts across the before and after periods."
)
lines.append("")
lines.append("## Required Controls")
lines.append("")
lines.append("- Historical eligible outstanding balance")
lines.append("- DPD composition")
lines.append("- Risk composition")
lines.append("- Account-status composition")
lines.append("- Loan-type composition")
lines.append("- Campaign composition")
lines.append("- Channel composition")
lines.append("- Contact selection")
lines.append("- Attribution window")
lines.append("")
lines.append("## Decision")
lines.append("")
lines.append(
    "Do not present the 11% improvement as a proven causal result."
)
lines.append(
    "Present it as an unverified reported claim until the missing "
    "historical denominators and controls are available."
)

(REPORTS / "improvement_verification_findings.md").write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print("Improvement verification completed")
print("Reports:")
print("reports/improvement_verification.csv")
print("reports/improvement_verification_findings.md")
