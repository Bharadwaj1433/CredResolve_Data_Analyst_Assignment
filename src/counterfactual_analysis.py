import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path("data/cleaned")
REPORTS = Path("reports")

accounts = pd.read_csv(BASE / "accounts.csv")
payments = pd.read_csv(BASE / "payments.csv")
calls = pd.read_csv(BASE / "calls.csv")

successful = payments[
    payments["payment_status"].astype(str).str.upper().eq("SUCCESS")
].copy()

payment_outcomes = (
    successful.groupby("account_id")
    .agg(
        recovered_amount=("amount", "sum"),
        successful_payments=("payment_id", "count")
    )
    .reset_index()
)

accounts = accounts.merge(
    payment_outcomes,
    on="account_id",
    how="left"
)

accounts["recovered_amount"] = accounts["recovered_amount"].fillna(0)
accounts["successful_payments"] = accounts["successful_payments"].fillna(0)

accounts["paid"] = (
    accounts["successful_payments"] > 0
).astype(int)

def dpd_band(x):
    if pd.isna(x):
        return "UNKNOWN"
    if x == 0:
        return "0"
    if x <= 30:
        return "1-30"
    if x <= 60:
        return "31-60"
    if x <= 90:
        return "61-90"
    return "91-180+"

accounts["dpd_band"] = accounts["dpd"].apply(dpd_band)

answered_status = (
    calls.assign(
        answered=calls["call_status"]
        .astype(str)
        .str.upper()
        .isin(["ANSWERED", "CONNECTED", "SUCCESS"])
    )
    .groupby("account_id")["answered"]
    .any()
    .reset_index()
)

answered_status["treatment"] = answered_status["answered"].astype(int)

accounts = accounts.merge(
    answered_status[["account_id", "treatment"]],
    on="account_id",
    how="left"
)

accounts["treatment"] = accounts["treatment"].fillna(0).astype(int)

accounts["match_stratum"] = (
    accounts["dpd_band"].astype(str)
    + "|"
    + accounts["risk_segment"].astype(str)
    + "|"
    + accounts["status"].astype(str)
    + "|"
    + accounts["loan_type"].astype(str)
)

stratum_summary = (
    accounts.groupby(
        ["match_stratum", "treatment"]
    )
    .agg(
        accounts=("account_id", "nunique"),
        paying_accounts=("paid", "sum"),
        recovered_amount=("recovered_amount", "sum"),
        outstanding_amount=("outstanding_amount", "sum")
    )
    .reset_index()
)

stratum_summary["payment_rate_pct"] = (
    stratum_summary["paying_accounts"]
    / stratum_summary["accounts"]
    * 100
)

treatment_summary = (
    accounts.groupby("treatment")
    .agg(
        accounts=("account_id", "nunique"),
        paying_accounts=("paid", "sum"),
        recovered_amount=("recovered_amount", "sum"),
        outstanding_amount=("outstanding_amount", "sum")
    )
    .reset_index()
)

treatment_summary["payment_rate_pct"] = (
    treatment_summary["paying_accounts"]
    / treatment_summary["accounts"]
    * 100
)

treatment_summary["recovery_rate_pct"] = np.where(
    treatment_summary["outstanding_amount"] > 0,
    treatment_summary["recovered_amount"]
    / treatment_summary["outstanding_amount"]
    * 100,
    np.nan
)

matched = (
    stratum_summary
    .pivot(
        index="match_stratum",
        columns="treatment",
        values=["accounts", "paying_accounts", "recovered_amount", "outstanding_amount"]
    )
    .reset_index()
)

matched.columns = [
    "_".join([str(x) for x in col if str(x) != ""])
    if isinstance(col, tuple)
    else str(col)
    for col in matched.columns
]

matched = matched.rename(
    columns={
        "accounts_0": "control_accounts",
        "accounts_1": "treatment_accounts",
        "paying_accounts_0": "control_paying_accounts",
        "paying_accounts_1": "treatment_paying_accounts",
        "recovered_amount_0": "control_recovered_amount",
        "recovered_amount_1": "treatment_recovered_amount",
        "outstanding_amount_0": "control_outstanding_amount",
        "outstanding_amount_1": "treatment_outstanding_amount"
    }
)

matched = matched.dropna(
    subset=["control_accounts", "treatment_accounts"]
)

matched["control_payment_rate_pct"] = (
    matched["control_paying_accounts"]
    / matched["control_accounts"]
    * 100
)

matched["treatment_payment_rate_pct"] = (
    matched["treatment_paying_accounts"]
    / matched["treatment_accounts"]
    * 100
)

matched["payment_rate_difference_pct_points"] = (
    matched["treatment_payment_rate_pct"]
    - matched["control_payment_rate_pct"]
)

matched["control_recovery_rate_pct"] = np.where(
    matched["control_outstanding_amount"] > 0,
    matched["control_recovered_amount"]
    / matched["control_outstanding_amount"]
    * 100,
    np.nan
)

matched["treatment_recovery_rate_pct"] = np.where(
    matched["treatment_outstanding_amount"] > 0,
    matched["treatment_recovered_amount"]
    / matched["treatment_outstanding_amount"]
    * 100,
    np.nan
)

matched["recovery_rate_difference_pct_points"] = (
    matched["treatment_recovery_rate_pct"]
    - matched["control_recovery_rate_pct"]
)

weighted_control_rate = (
    matched["control_paying_accounts"].sum()
    / matched["control_accounts"].sum()
    * 100
)

weighted_treatment_rate = (
    matched["treatment_paying_accounts"].sum()
    / matched["treatment_accounts"].sum()
    * 100
)

weighted_difference = (
    weighted_treatment_rate
    - weighted_control_rate
)

overall = pd.DataFrame([
    {
        "treatment_definition": "Account with at least one answered call",
        "control_definition": "Account without an answered call",
        "treatment_accounts": int(
            treatment_summary.loc[
                treatment_summary["treatment"] == 1,
                "accounts"
            ].iloc[0]
        ),
        "control_accounts": int(
            treatment_summary.loc[
                treatment_summary["treatment"] == 0,
                "accounts"
            ].iloc[0]
        ),
        "treatment_payment_rate_pct": weighted_treatment_rate,
        "control_payment_rate_pct": weighted_control_rate,
        "observed_payment_rate_difference_pct_points": weighted_difference,
        "matched_strata": len(matched),
        "interpretation": "Observational comparison only"
    }
])

treatment_summary.to_csv(
    REPORTS / "counterfactual_treatment_control.csv",
    index=False
)

matched.to_csv(
    REPORTS / "counterfactual_matched_comparison.csv",
    index=False
)

overall.to_csv(
    REPORTS / "counterfactual_estimate.csv",
    index=False
)

findings = f"""# Counterfactual Analysis

## Design

The analysis uses an observational treatment and comparison framework.

Treatment accounts are accounts with at least one answered call.

Comparison accounts are accounts without an answered call.

Accounts are compared within strata defined by DPD band, risk segment,
account status, and loan type.

## Observed Comparison

Treatment accounts: {overall["treatment_accounts"].iloc[0]:,.0f}

Comparison accounts: {overall["control_accounts"].iloc[0]:,.0f}

Treatment payment-account rate: {weighted_treatment_rate:.2f}%

Comparison payment-account rate: {weighted_control_rate:.2f}%

Observed difference: {weighted_difference:+.2f} percentage points.

Matched strata: {len(matched):,.0f}

## Interpretation

The treatment group has a higher or lower observed payment rate than the
comparison group after restricting the comparison to common portfolio
strata.

This difference is an observational association and must not be interpreted
as a causal treatment effect.

Accounts receiving answered calls were selected operationally and may differ
from accounts without answered calls in unobserved characteristics,
collection priority, contactability, agent allocation, campaign exposure,
and timing.

## Counterfactual Limitation

The supplied data does not contain randomized treatment assignment or a
validated untreated control cohort.

The analysis therefore cannot establish what recovery would have occurred
for treated accounts in the absence of answered calls.

It also cannot establish that answered calls caused the observed payment
difference.

## 11% Improvement Assessment

The counterfactual analysis does not validate the reported 11% improvement.

The strongest defensible conclusion is that answered-call accounts and
non-answered-call accounts exhibit an observable difference in payment
outcomes after portfolio-stratum comparison.

A causal estimate would require stronger identification, such as randomized
assignment, a valid natural experiment, or sufficiently detailed
time-dependent treatment and control cohorts.

## Decision

Do not report the observed treatment-control difference as incremental
recovery caused by calling.

Use it as an observational benchmark for future controlled testing.
"""

(REPORTS / "counterfactual_analysis_findings.md").write_text(
    findings,
    encoding="utf-8"
)

print("Counterfactual analysis completed")
print("reports/counterfactual_analysis_findings.md")
