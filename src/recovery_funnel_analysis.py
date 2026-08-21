import pandas as pd
from pathlib import Path

data_path = Path("data/cleaned")
report_path = Path("reports")

accounts = pd.read_csv(data_path / "accounts.csv")
calls = pd.read_csv(data_path / "calls.csv")
payments = pd.read_csv(data_path / "payments.csv")
ptp = pd.read_csv(data_path / "promises_to_pay.csv")
campaigns = pd.read_csv(data_path / "campaigns.csv")

payments["amount"] = pd.to_numeric(payments["amount"], errors="coerce")

successful = payments[payments["payment_status"].eq("SUCCESS")].copy()

account_payment = (
    successful.groupby("account_id", as_index=False)
    .agg(
        successful_payment_amount=("amount", "sum"),
        successful_payment_count=("payment_id", "count")
    )
)

account_ptp = (
    ptp.groupby("account_id", as_index=False)
    .agg(
        ptp_count=("ptp_id", "count"),
        kept_ptp_count=("status", lambda x: (x == "KEPT").sum())
    )
)

account_calls = (
    calls.groupby("account_id", as_index=False)
    .agg(
        call_count=("call_id", "count"),
        answered_call_count=("call_status", lambda x: (x == "ANSWERED").sum())
    )
)

account_funnel = accounts[
    ["account_id", "outstanding_amount"]
].copy()

account_funnel = account_funnel.merge(
    account_payment,
    on="account_id",
    how="left"
)

account_funnel = account_funnel.merge(
    account_ptp,
    on="account_id",
    how="left"
)

account_funnel = account_funnel.merge(
    account_calls,
    on="account_id",
    how="left"
)

numeric_columns = [
    "successful_payment_amount",
    "successful_payment_count",
    "ptp_count",
    "kept_ptp_count",
    "call_count",
    "answered_call_count"
]

account_funnel[numeric_columns] = account_funnel[numeric_columns].fillna(0)

account_funnel["has_successful_payment"] = (
    account_funnel["successful_payment_amount"] > 0
)

account_funnel["has_ptp"] = (
    account_funnel["ptp_count"] > 0
)

account_funnel["has_kept_ptp"] = (
    account_funnel["kept_ptp_count"] > 0
)

account_funnel["has_answered_call"] = (
    account_funnel["answered_call_count"] > 0
)

funnel = pd.DataFrame([
    {
        "stage": "accounts",
        "accounts": len(account_funnel)
    },
    {
        "stage": "accounts_with_calls",
        "accounts": int((account_funnel["call_count"] > 0).sum())
    },
    {
        "stage": "accounts_with_answered_calls",
        "accounts": int(account_funnel["has_answered_call"].sum())
    },
    {
        "stage": "accounts_with_ptp",
        "accounts": int(account_funnel["has_ptp"].sum())
    },
    {
        "stage": "accounts_with_kept_ptp",
        "accounts": int(account_funnel["has_kept_ptp"].sum())
    },
    {
        "stage": "accounts_with_successful_payment",
        "accounts": int(account_funnel["has_successful_payment"].sum())
    }
])

funnel["conversion_from_accounts_pct"] = (
    funnel["accounts"] / len(account_funnel) * 100
)

funnel.to_csv(
    report_path / "recovery_funnel.csv",
    index=False
)

account_funnel["payment_to_outstanding_pct"] = (
    account_funnel["successful_payment_amount"]
    / account_funnel["outstanding_amount"]
    * 100
)

account_funnel["payment_to_outstanding_pct"] = (
    account_funnel["payment_to_outstanding_pct"]
    .replace([float("inf"), -float("inf")], 0)
    .fillna(0)
)

account_funnel[
    [
        "account_id",
        "outstanding_amount",
        "successful_payment_amount",
        "successful_payment_count",
        "call_count",
        "answered_call_count",
        "ptp_count",
        "kept_ptp_count",
        "has_successful_payment",
        "payment_to_outstanding_pct"
    ]
].to_csv(
    report_path / "account_recovery_profile.csv",
    index=False
)

campaign_calls = (
    calls.merge(
        campaigns[
            ["campaign_id", "campaign_name", "channel", "strategy_version"]
        ],
        on="campaign_id",
        how="left"
    )
)

campaign_accounts = (
    campaign_calls[
        ["campaign_id", "account_id"]
    ]
    .drop_duplicates()
)

campaign_accounts = campaign_accounts.merge(
    account_payment[
        ["account_id", "successful_payment_amount"]
    ],
    on="account_id",
    how="left"
)

campaign_accounts["successful_payment_amount"] = (
    campaign_accounts["successful_payment_amount"].fillna(0)
)

campaign_performance = (
    campaign_calls.groupby(
        [
            "campaign_id",
            "campaign_name",
            "channel",
            "strategy_version"
        ],
        dropna=False
    )
    .agg(
        call_volume=("call_id", "count"),
        answered_calls=(
            "call_status",
            lambda x: (x == "ANSWERED").sum()
        ),
        unique_accounts=("account_id", "nunique")
    )
    .reset_index()
)

campaign_payment = (
    campaign_accounts.groupby(
        "campaign_id",
        as_index=False
    )
    .agg(
        accounts_with_successful_payment=(
            "successful_payment_amount",
            lambda x: (x > 0).sum()
        ),
        successful_payment_amount=(
            "successful_payment_amount",
            "sum"
        )
    )
)

campaign_performance = campaign_performance.merge(
    campaign_payment,
    on="campaign_id",
    how="left"
)

campaign_performance[
    [
        "accounts_with_successful_payment",
        "successful_payment_amount"
    ]
] = campaign_performance[
    [
        "accounts_with_successful_payment",
        "successful_payment_amount"
    ]
].fillna(0)

campaign_performance["answer_rate_pct"] = (
    campaign_performance["answered_calls"]
    / campaign_performance["call_volume"]
    * 100
)

campaign_performance["payment_account_rate_pct"] = (
    campaign_performance["accounts_with_successful_payment"]
    / campaign_performance["unique_accounts"]
    * 100
)

campaign_performance["payment_per_call"] = (
    campaign_performance["successful_payment_amount"]
    / campaign_performance["call_volume"]
)

campaign_performance = campaign_performance.sort_values(
    "successful_payment_amount",
    ascending=False
)

campaign_performance.to_csv(
    report_path / "campaign_recovery_performance.csv",
    index=False
)

print("Recovery funnel created")
print("Account recovery profile created")
print("Campaign recovery performance created")
