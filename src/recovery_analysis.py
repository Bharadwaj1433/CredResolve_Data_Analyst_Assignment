import pandas as pd
from pathlib import Path

data_path = Path("data/cleaned")
report_path = Path("reports")

accounts = pd.read_csv(data_path / "accounts.csv")
calls = pd.read_csv(data_path / "calls.csv")
payments = pd.read_csv(data_path / "payments.csv")
ptp = pd.read_csv(data_path / "promises_to_pay.csv")
field = pd.read_csv(data_path / "field_visits.csv")
sms = pd.read_csv(data_path / "sms_events.csv")
whatsapp = pd.read_csv(data_path / "whatsapp_events.csv")
campaigns = pd.read_csv(data_path / "campaigns.csv")

accounts["event_at"] = pd.to_datetime(accounts["opened_at"], errors="coerce")
calls["event_at"] = pd.to_datetime(calls["event_at"], errors="coerce")
payments["event_at"] = pd.to_datetime(payments["event_at"], errors="coerce")
ptp["event_at"] = pd.to_datetime(ptp["event_at"], errors="coerce")
field["event_at"] = pd.to_datetime(field["event_at"], errors="coerce")
sms["event_at"] = pd.to_datetime(sms["event_at"], errors="coerce")
whatsapp["event_at"] = pd.to_datetime(whatsapp["event_at"], errors="coerce")

payments["amount"] = pd.to_numeric(payments["amount"], errors="coerce")

successful_payments = payments[
    payments["payment_status"].eq("SUCCESS")
].copy()

total_outstanding = accounts["outstanding_amount"].sum()
total_paid = successful_payments["amount"].sum()

recovery_rate = (
    total_paid / total_outstanding * 100
    if total_outstanding else 0
)

summary = pd.DataFrame([
    {
        "metric": "accounts",
        "value": len(accounts)
    },
    {
        "metric": "total_outstanding_amount",
        "value": total_outstanding
    },
    {
        "metric": "successful_payment_amount",
        "value": total_paid
    },
    {
        "metric": "recovery_rate_pct",
        "value": recovery_rate
    },
    {
        "metric": "successful_payments",
        "value": len(successful_payments)
    },
    {
        "metric": "total_payment_records",
        "value": len(payments)
    },
    {
        "metric": "calls",
        "value": len(calls)
    },
    {
        "metric": "answered_calls",
        "value": int(calls["call_status"].eq("ANSWERED").sum())
    },
    {
        "metric": "ptps",
        "value": len(ptp)
    },
    {
        "metric": "ptps_kept",
        "value": int(ptp["status"].eq("KEPT").sum())
    },
    {
        "metric": "field_visits",
        "value": len(field)
    },
    {
        "metric": "sms_events",
        "value": len(sms)
    },
    {
        "metric": "whatsapp_events",
        "value": len(whatsapp)
    }
])

summary.to_csv(
    report_path / "recovery_summary.csv",
    index=False
)

channel_rows = []

channel_rows.append({
    "channel": "VOICE",
    "activity": len(calls),
    "successful_outcomes": int(calls["call_status"].eq("ANSWERED").sum()),
    "success_rate_pct": calls["call_status"].eq("ANSWERED").mean() * 100
})

channel_rows.append({
    "channel": "FIELD",
    "activity": len(field),
    "successful_outcomes": int(field["outcome"].eq("CONTACTED").sum()),
    "success_rate_pct": field["outcome"].eq("CONTACTED").mean() * 100
})

channel_rows.append({
    "channel": "SMS",
    "activity": len(sms),
    "successful_outcomes": int(sms["event_type"].eq("DELIVERED").sum()),
    "success_rate_pct": sms["event_type"].eq("DELIVERED").mean() * 100
})

channel_rows.append({
    "channel": "WHATSAPP",
    "activity": len(whatsapp),
    "successful_outcomes": int(
        whatsapp["event_type"].isin(["READ", "REPLIED", "PAYMENT_CLICK"]).sum()
    ),
    "success_rate_pct": whatsapp["event_type"].isin(
        ["READ", "REPLIED", "PAYMENT_CLICK"]
    ).mean() * 100
})

channel_performance = pd.DataFrame(channel_rows)

channel_performance = channel_performance.sort_values(
    "success_rate_pct",
    ascending=False
)

channel_performance.to_csv(
    report_path / "channel_performance.csv",
    index=False
)

campaign_performance = (
    calls.merge(
        campaigns[
            ["campaign_id", "campaign_name", "channel", "strategy_version"]
        ],
        on="campaign_id",
        how="left"
    )
    .groupby(
        ["campaign_id", "campaign_name", "channel", "strategy_version"],
        dropna=False
    )
    .agg(
        call_volume=("call_id", "size"),
        answered_calls=("call_status", lambda x: (x == "ANSWERED").sum())
    )
    .reset_index()
)

campaign_performance["answer_rate_pct"] = (
    campaign_performance["answered_calls"]
    / campaign_performance["call_volume"]
    * 100
)

campaign_performance = campaign_performance.sort_values(
    "answer_rate_pct",
    ascending=False
)

campaign_performance.to_csv(
    report_path / "campaign_performance.csv",
    index=False
)

top_channel = channel_performance.iloc[0]

top_campaign = campaign_performance.iloc[0]

findings = f"""# Recovery Analysis Findings

## Portfolio

Total accounts: {len(accounts):,}

Total outstanding amount: {total_outstanding:,.2f}

Successful payment amount: {total_paid:,.2f}

Portfolio recovery rate: {recovery_rate:.2f}%

## Channel Performance

Highest observed channel success rate: {top_channel["channel"]}

Channel success rate: {top_channel["success_rate_pct"]:.2f}%

## Campaign Performance

Highest observed campaign answer rate: {top_campaign["campaign_name"]}

Campaign channel: {top_campaign["channel"]}

Campaign answer rate: {top_campaign["answer_rate_pct"]:.2f}%

## Operational Activity

Calls: {len(calls):,}

Answered calls: {int(calls["call_status"].eq("ANSWERED").sum()):,}

Promises to pay: {len(ptp):,}

Kept promises: {int(ptp["status"].eq("KEPT").sum()):,}

Field visits: {len(field):,}

SMS events: {len(sms):,}

WhatsApp events: {len(whatsapp):,}

## Analytical Notes

Payment recovery uses SUCCESS payment records only.

Channel performance is based on channel-specific observable outcomes.

Campaign performance is based on call answer rate.

Borrower identity conflicts and unresolved borrower relationships are excluded from being treated as reliable borrower-level attribution.

These results should be interpreted as operational performance indicators rather than causal estimates.
"""

(report_path / "recovery_findings.md").write_text(findings)

print("Recovery analysis completed")
print("Reports:")
print("reports/recovery_summary.csv")
print("reports/channel_performance.csv")
print("reports/campaign_performance.csv")
print("reports/recovery_findings.md")
