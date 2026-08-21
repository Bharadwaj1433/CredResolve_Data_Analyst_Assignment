import pandas as pd
from pathlib import Path

data_path = Path("data/cleaned")
report_path = Path("reports")

accounts = pd.read_csv(data_path / "accounts.csv")
calls = pd.read_csv(data_path / "calls.csv")
payments = pd.read_csv(data_path / "payments.csv")

payments["amount"] = pd.to_numeric(payments["amount"], errors="coerce")

successful = payments[
    payments["payment_status"].eq("SUCCESS")
].copy()

payment_by_account = (
    successful.groupby("account_id", as_index=False)
    .agg(
        recovered_amount=("amount", "sum"),
        successful_payment_count=("payment_id", "count")
    )
)

account_base = accounts[
    [
        "account_id",
        "outstanding_amount",
        "dpd",
        "risk_segment",
        "loan_type",
        "status"
    ]
].copy()

account_base = account_base.merge(
    payment_by_account,
    on="account_id",
    how="left"
)

account_base["recovered_amount"] = (
    account_base["recovered_amount"].fillna(0)
)

account_base["successful_payment_count"] = (
    account_base["successful_payment_count"].fillna(0)
)

account_base["recovery_rate_pct"] = (
    account_base["recovered_amount"]
    / account_base["outstanding_amount"]
    * 100
)

account_base["recovery_rate_pct"] = (
    account_base["recovery_rate_pct"]
    .replace([float("inf"), -float("inf")], 0)
    .fillna(0)
)

def summarize(column):
    result = (
        account_base.groupby(column, dropna=False)
        .agg(
            accounts=("account_id", "nunique"),
            outstanding_amount=("outstanding_amount", "sum"),
            recovered_amount=("recovered_amount", "sum"),
            accounts_with_payment=(
                "recovered_amount",
                lambda x: (x > 0).sum()
            ),
            successful_payment_count=(
                "successful_payment_count",
                "sum"
            )
        )
        .reset_index()
    )

    result["recovery_rate_pct"] = (
        result["recovered_amount"]
        / result["outstanding_amount"]
        * 100
    )

    result["payment_account_rate_pct"] = (
        result["accounts_with_payment"]
        / result["accounts"]
        * 100
    )

    return result.sort_values(
        "recovery_rate_pct",
        ascending=False
    )

risk = summarize("risk_segment")
risk.to_csv(
    report_path / "recovery_by_risk.csv",
    index=False
)

loan = summarize("loan_type")
loan.to_csv(
    report_path / "recovery_by_loan_type.csv",
    index=False
)

status = summarize("status")
status.to_csv(
    report_path / "recovery_by_account_status.csv",
    index=False
)

account_base["dpd_band"] = pd.cut(
    account_base["dpd"],
    bins=[-1, 0, 30, 60, 90, 180, float("inf")],
    labels=[
        "0",
        "1-30",
        "31-60",
        "61-90",
        "91-180",
        "181+"
    ]
)

dpd = summarize("dpd_band")
dpd.to_csv(
    report_path / "recovery_by_dpd.csv",
    index=False
)

payment_method = (
    successful.groupby("payment_method", dropna=False)
    .agg(
        successful_payments=("payment_id", "count"),
        recovered_amount=("amount", "sum"),
        accounts=("account_id", "nunique")
    )
    .reset_index()
)

payment_method["average_payment"] = (
    payment_method["recovered_amount"]
    / payment_method["successful_payments"]
)

payment_method = payment_method.sort_values(
    "recovered_amount",
    ascending=False
)

payment_method.to_csv(
    report_path / "payment_method_performance.csv",
    index=False
)

contacted_accounts = set(
    calls.loc[
        calls["call_status"].eq("ANSWERED"),
        "account_id"
    ]
)

paid_accounts = set(
    successful["account_id"]
)

contacted_and_paid = len(
    contacted_accounts.intersection(paid_accounts)
)

contacted_count = len(contacted_accounts)

contact_to_payment_rate = (
    contacted_and_paid / contacted_count * 100
    if contacted_count
    else 0
)

uncontacted_paid = len(
    paid_accounts.difference(contacted_accounts)
)

funnel = pd.DataFrame([
    {
        "metric": "accounts",
        "value": len(account_base)
    },
    {
        "metric": "accounts_with_answered_call",
        "value": contacted_count
    },
    {
        "metric": "accounts_with_successful_payment",
        "value": len(paid_accounts)
    },
    {
        "metric": "answered_accounts_with_payment",
        "value": contacted_and_paid
    },
    {
        "metric": "answered_to_payment_rate_pct",
        "value": contact_to_payment_rate
    },
    {
        "metric": "paid_accounts_without_answered_call",
        "value": uncontacted_paid
    }
])

funnel.to_csv(
    report_path / "contact_to_payment_funnel.csv",
    index=False
)

overall_outstanding = account_base["outstanding_amount"].sum()
overall_recovered = account_base["recovered_amount"].sum()

top_risk = risk.iloc[0]
lowest_risk = risk.iloc[-1]

top_dpd = dpd.iloc[0]
lowest_dpd = dpd.iloc[-1]

top_loan = loan.iloc[0]
top_status = status.iloc[0]

findings = f"""# Recovery Performance Findings

## Portfolio

Accounts: {len(account_base):,}

Outstanding amount: {overall_outstanding:,.2f}

Successful recovered amount: {overall_recovered:,.2f}

Overall recovery rate: {overall_recovered / overall_outstanding * 100:.2f}%

## Contact Conversion

Accounts with answered calls: {contacted_count:,}

Accounts with successful payment: {len(paid_accounts):,}

Answered accounts that also paid: {contacted_and_paid:,}

Answered-call to payment rate: {contact_to_payment_rate:.2f}%

Paid accounts without an answered call: {uncontacted_paid:,}

## Risk Segments

Highest recovery-rate segment: {top_risk["risk_segment"]}

Highest segment recovery rate: {top_risk["recovery_rate_pct"]:.2f}%

Lowest recovery-rate segment: {lowest_risk["risk_segment"]}

Lowest segment recovery rate: {lowest_risk["recovery_rate_pct"]:.2f}%

## DPD

Highest recovery-rate DPD band: {top_dpd["dpd_band"]}

Recovery rate: {top_dpd["recovery_rate_pct"]:.2f}%

Lowest recovery-rate DPD band: {lowest_dpd["dpd_band"]}

Recovery rate: {lowest_dpd["recovery_rate_pct"]:.2f}%

## Loan Type

Highest recovery-rate loan type: {top_loan["loan_type"]}

Recovery rate: {top_loan["recovery_rate_pct"]:.2f}%

## Account Status

Highest recovery-rate account status: {top_status["status"]}

Recovery rate: {top_status["recovery_rate_pct"]:.2f}%

## Interpretation

Recovery performance varies across portfolio segments.

Answered contact is an important operational stage, but contact should not be treated as causal proof of payment.

Successful payment amount is used as the recovery measure.

Borrower-level attribution remains subject to the previously identified borrower identity quality issues.

Campaign-level monetary attribution is not treated as causal because multiple campaigns can touch the same account.

## Recommended Actions

Prioritize segments with high outstanding balances and below-average recovery.

Use DPD-based treatment strategies instead of applying one collection approach across all accounts.

Use successful payment behavior to identify accounts where digital payment follow-up can be emphasized.

Investigate accounts with repeated contact but no successful payment as a separate operational queue.

Retain quality flags in downstream reporting so data-quality limitations remain visible.
"""

(report_path / "final_recovery_findings.md").write_text(
    findings
)

print("Final recovery analysis completed")
print("Reports:")
print("reports/recovery_by_risk.csv")
print("reports/recovery_by_loan_type.csv")
print("reports/recovery_by_account_status.csv")
print("reports/recovery_by_dpd.csv")
print("reports/payment_method_performance.csv")
print("reports/contact_to_payment_funnel.csv")
print("reports/final_recovery_findings.md")
