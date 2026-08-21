import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path("data/cleaned")
REPORTS = Path("reports")

accounts = pd.read_csv(BASE / "accounts.csv")
payments = pd.read_csv(BASE / "payments.csv")
calls = pd.read_csv(BASE / "calls.csv")
agents = pd.read_csv(BASE / "agents.csv")
campaigns = pd.read_csv(BASE / "campaigns.csv")


successful = payments[
    payments["payment_status"].astype(str).str.upper().eq("SUCCESS")
].copy()

payment_by_account = (
    successful.groupby("account_id")
    .agg(
        recovered_amount=("amount", "sum"),
        successful_payments=("payment_id", "count")
    )
    .reset_index()
)

account_base = accounts.merge(
    payment_by_account,
    on="account_id",
    how="left"
)

account_base["recovered_amount"] = (
    account_base["recovered_amount"].fillna(0)
)

account_base["successful_payments"] = (
    account_base["successful_payments"].fillna(0)
)

account_base["paying_account"] = (
    account_base["successful_payments"] > 0
)


def segment_analysis(df, dimension, output_name):
    temp = (
        df.groupby(dimension, dropna=False)
        .agg(
            accounts=("account_id", "nunique"),
            outstanding_amount=("outstanding_amount", "sum"),
            recovered_amount=("recovered_amount", "sum"),
            successful_payments=("successful_payments", "sum"),
            paying_accounts=("paying_account", "sum")
        )
        .reset_index()
    )

    temp["recovery_rate_pct"] = np.where(
        temp["outstanding_amount"] > 0,
        temp["recovered_amount"]
        / temp["outstanding_amount"]
        * 100,
        np.nan
    )

    temp["payment_account_rate_pct"] = np.where(
        temp["accounts"] > 0,
        temp["paying_accounts"]
        / temp["accounts"]
        * 100,
        np.nan
    )

    temp.to_csv(REPORTS / output_name, index=False)

    return temp


risk = segment_analysis(
    account_base,
    "risk_segment",
    "driver_risk.csv"
)

status = segment_analysis(
    account_base,
    "status",
    "driver_status.csv"
)

loan = segment_analysis(
    account_base,
    "loan_type",
    "driver_loan_type.csv"
)

# -----------------------------
# DPD bands
# -----------------------------

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

account_base["dpd_band"] = account_base["dpd"].apply(dpd_band)

dpd = segment_analysis(
    account_base,
    "dpd_band",
    "driver_dpd.csv"
)


agent_calls = (
    calls.groupby("agent_id")
    .agg(
        calls=("call_id", "count"),
        answered_calls=(
            "call_status",
            lambda x: x.astype(str).str.upper().isin(
                ["ANSWERED", "CONNECTED", "SUCCESS"]
            ).sum()
        ),
        unique_accounts=("account_id", "nunique")
    )
    .reset_index()
)

agent_payment = (
    calls[["agent_id", "account_id"]]
    .drop_duplicates()
    .merge(
        payment_by_account,
        on="account_id",
        how="left"
    )
)

agent_payment["recovered_amount"] = (
    agent_payment["recovered_amount"].fillna(0)
)

agent_performance = agent_calls.merge(
    agent_payment.groupby("agent_id")
    .agg(
        accounts_with_payment=("recovered_amount", lambda x: (x > 0).sum()),
        recovered_amount=("recovered_amount", "sum")
    )
    .reset_index(),
    on="agent_id",
    how="left"
)

agent_performance["answer_rate_pct"] = np.where(
    agent_performance["calls"] > 0,
    agent_performance["answered_calls"]
    / agent_performance["calls"]
    * 100,
    np.nan
)

agent_performance["payment_account_rate_pct"] = np.where(
    agent_performance["unique_accounts"] > 0,
    agent_performance["accounts_with_payment"]
    / agent_performance["unique_accounts"]
    * 100,
    np.nan
)

agent_performance = agent_performance.merge(
    agents[
        [
            "agent_id",
            "employee_code",
            "vendor_id",
            "team",
            "status",
            "joined_at"
        ]
    ],
    on="agent_id",
    how="left"
)

agent_performance["joined_at"] = pd.to_datetime(
    agent_performance["joined_at"],
    errors="coerce"
)

agent_performance["tenure_days"] = (
    pd.Timestamp("2026-08-31")
    - agent_performance["joined_at"]
).dt.days

agent_performance["tenure_band"] = pd.cut(
    agent_performance["tenure_days"],
    bins=[-1, 90, 180, 365, 100000],
    labels=["0-90d", "91-180d", "181-365d", "366d+"]
)

agent_performance["eligible_for_ranking"] = (
    agent_performance["calls"] >= 50
)

agent_performance.sort_values(
    ["eligible_for_ranking", "payment_account_rate_pct"],
    ascending=[False, False]
).to_csv(
    REPORTS / "driver_agent_performance.csv",
    index=False
)



tenure = (
    agent_performance
    .groupby("tenure_band", observed=False)
    .agg(
        agents=("agent_id", "nunique"),
        calls=("calls", "sum"),
        answered_calls=("answered_calls", "sum"),
        unique_accounts=("unique_accounts", "sum"),
        accounts_with_payment=("accounts_with_payment", "sum"),
        recovered_amount=("recovered_amount", "sum")
    )
    .reset_index()
)

tenure["answer_rate_pct"] = np.where(
    tenure["calls"] > 0,
    tenure["answered_calls"] / tenure["calls"] * 100,
    np.nan
)

tenure["payment_account_rate_pct"] = np.where(
    tenure["unique_accounts"] > 0,
    tenure["accounts_with_payment"]
    / tenure["unique_accounts"]
    * 100,
    np.nan
)

tenure.to_csv(
    REPORTS / "driver_agent_tenure.csv",
    index=False
)



call_campaign = calls.merge(
    campaigns[
        [
            "campaign_id",
            "campaign_name",
            "channel",
            "strategy_version"
        ]
    ],
    on="campaign_id",
    how="left",
    suffixes=("", "_campaign")
)

campaign = (
    call_campaign.groupby(
        [
            "campaign_id",
            "campaign_name",
            "channel",
            "strategy_version"
        ],
        dropna=False
    )
    .agg(
        calls=("call_id", "count"),
        unique_accounts=("account_id", "nunique"),
        answered_calls=(
            "call_status",
            lambda x: x.astype(str).str.upper().isin(
                ["ANSWERED", "CONNECTED", "SUCCESS"]
            ).sum()
        )
    )
    .reset_index()
)

campaign["answer_rate_pct"] = np.where(
    campaign["calls"] > 0,
    campaign["answered_calls"]
    / campaign["calls"]
    * 100,
    np.nan
)

campaign.to_csv(
    REPORTS / "driver_campaign_performance.csv",
    index=False
)

channel = (
    call_campaign.groupby("channel", dropna=False)
    .agg(
        calls=("call_id", "count"),
        unique_accounts=("account_id", "nunique"),
        answered_calls=(
            "call_status",
            lambda x: x.astype(str).str.upper().isin(
                ["ANSWERED", "CONNECTED", "SUCCESS"]
            ).sum()
        )
    )
    .reset_index()
)

channel["answer_rate_pct"] = np.where(
    channel["calls"] > 0,
    channel["answered_calls"]
    / channel["calls"]
    * 100,
    np.nan
)

channel.to_csv(
    REPORTS / "driver_channel_performance.csv",
    index=False
)



vendor = (
    calls.groupby("vendor_id", dropna=False)
    .agg(
        calls=("call_id", "count"),
        unique_accounts=("account_id", "nunique"),
        unique_agents=("agent_id", "nunique"),
        answered_calls=(
            "call_status",
            lambda x: x.astype(str).str.upper().isin(
                ["ANSWERED", "CONNECTED", "SUCCESS"]
            ).sum()
        )
    )
    .reset_index()
)

vendor["answer_rate_pct"] = np.where(
    vendor["calls"] > 0,
    vendor["answered_calls"]
    / vendor["calls"]
    * 100,
    np.nan
)

vendor.to_csv(
    REPORTS / "driver_vendor_performance.csv",
    index=False
)


calls["event_at"] = pd.to_datetime(
    calls["event_at"],
    errors="coerce"
)

calls["hour"] = calls["event_at"].dt.hour

calling_time = (
    calls.groupby("hour")
    .agg(
        calls=("call_id", "count"),
        unique_accounts=("account_id", "nunique"),
        answered_calls=(
            "call_status",
            lambda x: x.astype(str).str.upper().isin(
                ["ANSWERED", "CONNECTED", "SUCCESS"]
            ).sum()
        )
    )
    .reset_index()
)

calling_time["answer_rate_pct"] = np.where(
    calling_time["calls"] > 0,
    calling_time["answered_calls"]
    / calling_time["calls"]
    * 100,
    np.nan
)

calling_time.to_csv(
    REPORTS / "driver_calling_time.csv",
    index=False
)



attempt_counts = (
    calls.groupby("account_id")
    .size()
    .reset_index(name="attempt_count")
)

attempt_counts["attempt_band"] = pd.cut(
    attempt_counts["attempt_count"],
    bins=[0, 1, 2, 3, 5, 10, float("inf")],
    labels=["1", "2", "3", "4-5", "6-10", "11+"]
)

attempt = attempt_counts.merge(
    payment_by_account[["account_id"]],
    on="account_id",
    how="left",
    indicator=True
)

attempt["paid"] = (
    attempt["_merge"] == "both"
)

attempt_summary = (
    attempt.groupby("attempt_band", observed=False)
    .agg(
        accounts=("account_id", "nunique"),
        paying_accounts=("paid", "sum")
    )
    .reset_index()
)

attempt_summary["payment_account_rate_pct"] = (
    attempt_summary["paying_accounts"]
    / attempt_summary["accounts"]
    * 100
)

attempt_summary.to_csv(
    REPORTS / "driver_attempt_frequency.csv",
    index=False
)


borrower = account_base.copy()

borrower["borrower_quality"] = np.select(
    [
        borrower["borrower_id_missing"].fillna(False),
        borrower["borrower_id_unresolved"].fillna(False)
    ],
    [
        "missing",
        "unresolved"
    ],
    default="resolved"
)

borrower_summary = segment_analysis(
    borrower,
    "borrower_quality",
    "driver_borrower_quality.csv"
)

summary_rows = []

driver_tables = {
    "risk_segment": risk,
    "dpd_band": dpd,
    "status": status,
    "loan_type": loan,
    "borrower_quality": borrower_summary
}

for driver_name, table in driver_tables.items():

    valid = table.dropna(
        subset=["recovery_rate_pct"]
    )

    if valid.empty:
        continue

    best = valid.loc[
        valid["recovery_rate_pct"].idxmax()
    ]

    worst = valid.loc[
        valid["recovery_rate_pct"].idxmin()
    ]

    summary_rows.append({
        "driver": driver_name,
        "best_segment": str(best.iloc[0]),
        "best_recovery_rate_pct": best["recovery_rate_pct"],
        "worst_segment": str(worst.iloc[0]),
        "worst_recovery_rate_pct": worst["recovery_rate_pct"]
    })

driver_summary = pd.DataFrame(summary_rows)

driver_summary.to_csv(
    REPORTS / "driver_summary.csv",
    index=False
)


lines = [
    "# Driver Analysis Findings",
    "",
    "## Available Portfolio Drivers",
    "",
    "The supplied data supports analysis of DPD, risk segment, account status,",
    "loan type, agent, agent tenure, campaign, channel, vendor, calling time,",
    "attempt frequency, and borrower relationship quality.",
    "",
    "## Unavailable Dimensions",
    "",
    "Client, geography, and language fields are not present in the supplied",
    "cleaned datasets. These dimensions are therefore not analyzed and no",
    "values are inferred.",
    "",
    "## Portfolio Drivers",
    "",
    "Recovery performance varies across DPD, risk, account status, loan type,",
    "and borrower relationship quality.",
    "These differences identify portfolio segments with different observed",
    "outcomes but do not establish causality.",
    "",
    "## Agent and Tenure",
    "",
    "Agent-level performance is available from call activity.",
    "Agent rankings should be restricted to agents with sufficient activity",
    "because low-volume agents can produce unstable rates.",
    "",
    "Agent tenure is derived from joined_at relative to the end of the",
    "observation period.",
    "Tenure differences are observational and do not establish that tenure",
    "causes better or worse recovery performance.",
    "",
    "## Campaign and Channel",
    "",
    "Campaign and channel performance varies across the portfolio.",
    "Campaign and channel comparisons must be interpreted alongside portfolio",
    "mix, agent allocation, vendor allocation, and contact selection.",
    "",
    "## Vendor",
    "",
    "Vendor performance is available for comparison.",
    "The observed agent-vendor relationship is highly variable, so vendor",
    "differences should not be interpreted as independent causal effects.",
    "",
    "## Calling Time",
    "",
    "Calling-time performance varies by observed event hour.",
    "Because calls contain multiple timezones, raw event hours should not be",
    "interpreted as equivalent local calling hours without timezone normalization.",
    "",
    "## Attempt Frequency",
    "",
    "Payment conversion varies across attempt-frequency bands.",
    "The relationship is subject to selection bias because attempt frequency",
    "is not randomly assigned.",
    "",
    "## Decision Use",
    "",
    "Observed driver differences should be treated as hypotheses for controlled",
    "testing or cohort analysis rather than causal explanations.",
    "",
    "## 11% Improvement Claim",
    "",
    "Driver variation provides plausible descriptive explanations for changes",
    "in aggregate recovery performance, but it does not independently validate",
    "the reported 11% improvement.",
    "",
    "The improvement remains unverified because historical eligible balances,",
    "cohort comparability, selection, attribution timing, and portfolio mix",
    "cannot be fully controlled with the supplied data."
]

(REPORTS / "driver_analysis_findings.md").write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print("Driver analysis completed")
print("Reports:")
print("reports/driver_summary.csv")
print("reports/driver_risk.csv")
print("reports/driver_dpd.csv")
print("reports/driver_status.csv")
print("reports/driver_loan_type.csv")
print("reports/driver_agent_performance.csv")
print("reports/driver_agent_tenure.csv")
print("reports/driver_campaign_performance.csv")
print("reports/driver_channel_performance.csv")
print("reports/driver_vendor_performance.csv")
print("reports/driver_calling_time.csv")
print("reports/driver_attempt_frequency.csv")
print("reports/driver_borrower_quality.csv")
print("reports/driver_analysis_findings.md")
