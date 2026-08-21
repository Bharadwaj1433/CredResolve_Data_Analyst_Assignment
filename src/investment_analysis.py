import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path("data/cleaned")
REPORTS = Path("reports")

accounts = pd.read_csv(BASE / "accounts.csv")
payments = pd.read_csv(BASE / "payments.csv")
calls = pd.read_csv(BASE / "calls.csv")
campaigns = pd.read_csv(BASE / "campaigns.csv")

successful = payments[
    payments["payment_status"].astype(str).str.upper().eq("SUCCESS")
].copy()

total_recovered = successful["amount"].sum()

account_payment = (
    successful.groupby("account_id")
    .agg(
        recovered_amount=("amount", "sum"),
        successful_payments=("payment_id", "count")
    )
    .reset_index()
)

accounts = accounts.merge(
    account_payment,
    on="account_id",
    how="left"
)

accounts["recovered_amount"] = accounts["recovered_amount"].fillna(0)

accounts["paying"] = (
    accounts["recovered_amount"] > 0
).astype(int)

answered = (
    calls.assign(
        answered=calls["call_status"]
        .astype(str)
        .str.upper()
        .isin(["ANSWERED", "CONNECTED", "SUCCESS"])
    )
    .groupby("account_id")["answered"]
    .any()
)

accounts["answered"] = (
    accounts["account_id"]
    .map(answered)
    .fillna(False)
    .astype(int)
)

channel = pd.read_csv(
    REPORTS / "channel_performance.csv"
)

channel = channel.sort_values(
    "success_rate_pct",
    ascending=False
)

best_channel = channel.iloc[0]

answered_accounts = int(
    accounts["answered"].sum()
)

unanswered_accounts = int(
    len(accounts) - answered_accounts
)

observed_treatment_rate = (
    accounts.loc[
        accounts["answered"] == 1,
        "paying"
    ].mean()
)

observed_control_rate = (
    accounts.loc[
        accounts["answered"] == 0,
        "paying"
    ].mean()
)

observed_difference = (
    observed_treatment_rate
    - observed_control_rate
)

investment = 100_000_000

base_lift = 0.0076

downside_lift = 0.0038

upside_lift = 0.0152

average_recovery_per_paying_account = (
    successful["amount"].sum()
    / successful["account_id"].nunique()
)

scenarios = pd.DataFrame([
    {
        "scenario": "Downside",
        "assumed_incremental_payment_rate": downside_lift,
        "eligible_accounts": unanswered_accounts,
        "incremental_accounts_recovered": unanswered_accounts * downside_lift,
        "average_recovery_per_incremental_account": average_recovery_per_paying_account,
        "incremental_recovery": unanswered_accounts * downside_lift * average_recovery_per_paying_account,
        "investment": investment
    },
    {
        "scenario": "Base",
        "assumed_incremental_payment_rate": base_lift,
        "eligible_accounts": unanswered_accounts,
        "incremental_accounts_recovered": unanswered_accounts * base_lift,
        "average_recovery_per_incremental_account": average_recovery_per_paying_account,
        "incremental_recovery": unanswered_accounts * base_lift * average_recovery_per_paying_account,
        "investment": investment
    },
    {
        "scenario": "Upside",
        "assumed_incremental_payment_rate": upside_lift,
        "eligible_accounts": unanswered_accounts,
        "incremental_accounts_recovered": unanswered_accounts * upside_lift,
        "average_recovery_per_incremental_account": average_recovery_per_paying_account,
        "incremental_recovery": unanswered_accounts * upside_lift * average_recovery_per_paying_account,
        "investment": investment
    }
])

scenarios["net_value"] = (
    scenarios["incremental_recovery"]
    - scenarios["investment"]
)

scenarios["roi_pct"] = (
    scenarios["net_value"]
    / scenarios["investment"]
    * 100
)

scenarios["benefit_cost_ratio"] = (
    scenarios["incremental_recovery"]
    / scenarios["investment"]
)

break_even_accounts = (
    investment
    / average_recovery_per_paying_account
)

break_even_rate = (
    break_even_accounts
    / unanswered_accounts
)

recommendation = pd.DataFrame([
    {
        "recommended_investment": "Targeted contactability and collections optimization",
        "investment_amount": investment,
        "priority_channel": best_channel["channel"],
        "observed_best_channel_success_rate_pct": best_channel["success_rate_pct"],
        "answered_accounts": answered_accounts,
        "unanswered_accounts": unanswered_accounts,
        "observed_answered_vs_unanswered_payment_difference_pct_points": observed_difference * 100,
        "base_assumed_incremental_payment_rate": base_lift,
        "break_even_incremental_accounts": break_even_accounts,
        "break_even_incremental_rate_pct": break_even_rate * 100,
        "decision": "Proceed only as a controlled pilot with measurable holdout",
        "confidence": "Moderate-to-low"
    }
])

recommendation.to_csv(
    REPORTS / "investment_recommendation.csv",
    index=False
)

scenarios.to_csv(
    REPORTS / "investment_scenarios.csv",
    index=False
)

best_channel_name = str(best_channel["channel"])

base_recovery = scenarios.loc[
    scenarios["scenario"] == "Base",
    "incremental_recovery"
].iloc[0]

base_roi = scenarios.loc[
    scenarios["scenario"] == "Base",
    "roi_pct"
].iloc[0]

break_even_value = (
    break_even_rate * 100
)

findings = f"""# ₹10 Cr Investment Recommendation

## Recommended Investment

The recommended use of the ₹10 crore investment is targeted collections
and contactability optimization, implemented through a controlled pilot
rather than an immediate full-scale rollout.

The available evidence identifies {best_channel_name} as the strongest
observed channel in the current channel-performance analysis.

The recommendation is therefore to invest in improving contact selection,
channel allocation, agent execution, and measurement around the strongest
observed channel while maintaining a holdout group.

## Current Evidence

Accounts with answered calls: {answered_accounts:,}

Accounts without answered calls: {unanswered_accounts:,}

Observed payment rate difference between answered-call and non-answered-call
accounts: {observed_difference * 100:+.2f} percentage points.

This difference is observational and is not treated as causal.

## Investment Scenarios

Downside, base, and upside scenarios are provided in
investment_scenarios.csv.

The base scenario assumes an incremental payment-account rate of
{base_lift * 100:.2f} percentage points.

Estimated base incremental recovery:
₹{base_recovery:,.2f}

Estimated base ROI:
{base_roi:.2f}%

## Break-Even

The investment requires approximately
{break_even_accounts:,.0f} additional paying accounts to recover
₹10 crore at the observed average recovery per paying account.

This corresponds to approximately
{break_even_value:.2f}% of currently non-answered accounts.

## Decision

Do not commit the full ₹10 crore immediately based on the current evidence.

Deploy the investment through a controlled pilot with a treatment group and
predefined holdout group.

Scale only if incremental recovery exceeds the break-even threshold after
controlling for portfolio mix, DPD, risk, campaign, channel, agent,
attribution timing, and eligible balance.

## Key Assumptions

The scenario analysis assumes that incremental paying accounts generate
recovery similar to the observed average recovery per paying account.

The scenario assumptions are not causal estimates.

Historical eligible balances are unavailable, so the analysis cannot
independently validate the reported 11% recovery improvement.

The investment model should therefore be treated as a decision framework,
not a guaranteed financial forecast.

## Downside Risk

The investment may fail to generate incremental recovery if the observed
answered-call association is primarily caused by selection effects.

Other risks include portfolio deterioration, contactability changes,
campaign mix changes, agent allocation changes, attribution-window effects,
and incomplete measurement.

## Final Recommendation

Approve a measured pilot rather than an unconditional ₹10 crore rollout.

Use randomized or strongly controlled treatment and holdout assignment,
predefine the recovery attribution window, measure eligible balance,
and require positive incremental recovery above the break-even threshold
before scaling.
"""

(REPORTS / "investment_analysis_findings.md").write_text(
    findings,
    encoding="utf-8"
)

print("Investment analysis completed")
print("reports/investment_analysis_findings.md")
