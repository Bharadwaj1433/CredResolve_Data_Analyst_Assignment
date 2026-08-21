import pandas as pd
from pathlib import Path

BASE = Path("data/cleaned")
REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)

def load(name):
    return pd.read_csv(BASE / f"{name}.csv")

accounts = load("accounts")
calls = load("calls")
payments = load("payments")
ptp = load("promises_to_pay")
field_visits = load("field_visits")
sms = load("sms_events")
whatsapp = load("whatsapp_events")

# -------------------------------------------------------------------
# Date preparation
# -------------------------------------------------------------------

accounts["opened_at"] = pd.to_datetime(accounts["opened_at"], errors="coerce")

calls["event_at"] = pd.to_datetime(calls["event_at"], errors="coerce")
payments["event_at"] = pd.to_datetime(payments["event_at"], errors="coerce")
ptp["event_at"] = pd.to_datetime(ptp["event_at"], errors="coerce")
field_visits["event_at"] = pd.to_datetime(field_visits["event_at"], errors="coerce")
sms["event_at"] = pd.to_datetime(sms["event_at"], errors="coerce")
whatsapp["event_at"] = pd.to_datetime(whatsapp["event_at"], errors="coerce")

# -------------------------------------------------------------------
# Determine actual observation period from available activity data
# -------------------------------------------------------------------

dates = pd.concat(
    [
        calls["event_at"],
        payments["event_at"],
        ptp["event_at"],
        field_visits["event_at"],
        sms["event_at"],
        whatsapp["event_at"],
    ],
    ignore_index=True,
).dropna()

start_month = dates.min().to_period("M")
end_month = dates.max().to_period("M")

months = pd.period_range(start_month, end_month, freq="M")

# -------------------------------------------------------------------
# Monthly base
# -------------------------------------------------------------------

monthly = pd.DataFrame({"month": months.astype(str)})

# -------------------------------------------------------------------
# Accounts
# -------------------------------------------------------------------

account_month = (
    accounts.dropna(subset=["opened_at"])
    .assign(month=accounts["opened_at"].dt.to_period("M").astype(str))
    .groupby("month")
    .agg(
        new_accounts=("account_id", "nunique"),
        new_portfolio_principal=("principal_amount", "sum"),
        new_portfolio_outstanding=("outstanding_amount", "sum"),
    )
    .reset_index()
)

monthly = monthly.merge(account_month, on="month", how="left")

# -------------------------------------------------------------------
# Payments
# -------------------------------------------------------------------

successful = payments[
    payments["payment_status"].astype(str).str.upper().eq("SUCCESS")
].copy()

payment_month = (
    payments.assign(month=payments["event_at"].dt.to_period("M").astype(str))
    .groupby("month")
    .agg(
        payment_records=("payment_id", "nunique"),
        payment_amount=("amount", "sum"),
    )
    .reset_index()
)

successful_month = (
    successful.assign(month=successful["event_at"].dt.to_period("M").astype(str))
    .groupby("month")
    .agg(
        successful_payments=("payment_id", "nunique"),
        recovered_amount=("amount", "sum"),
        accounts_with_successful_payment=("account_id", "nunique"),
    )
    .reset_index()
)

monthly = monthly.merge(payment_month, on="month", how="left")
monthly = monthly.merge(successful_month, on="month", how="left")

# -------------------------------------------------------------------
# Calls
# -------------------------------------------------------------------

answered_statuses = {
    "ANSWERED",
    "CONNECTED",
    "RPC",
    "RIGHT_PARTY_CONTACT",
}

calls["call_status_norm"] = (
    calls["call_status"].astype(str).str.upper().str.strip()
)

calls["answered_flag"] = calls["call_status_norm"].isin(answered_statuses)

call_month = (
    calls.assign(month=calls["event_at"].dt.to_period("M").astype(str))
    .groupby("month")
    .agg(
        calls=("call_id", "count"),
        unique_call_accounts=("account_id", "nunique"),
        answered_calls=("answered_flag", "sum"),
        answered_accounts=("account_id", lambda x: x[calls.loc[x.index, "answered_flag"]].nunique()),
    )
    .reset_index()
)

monthly = monthly.merge(call_month, on="month", how="left")

# -------------------------------------------------------------------
# PTP
# -------------------------------------------------------------------

ptp_month = (
    ptp.assign(month=ptp["event_at"].dt.to_period("M").astype(str))
    .groupby("month")
    .agg(
        ptps=("ptp_id", "nunique"),
        ptp_accounts=("account_id", "nunique"),
    )
    .reset_index()
)

monthly = monthly.merge(ptp_month, on="month", how="left")

if "ptp_status" in ptp.columns:
    kept_statuses = {
        "KEPT",
        "PAID",
        "SUCCESS",
        "FULFILLED",
        "COMPLETED",
    }

    ptp["ptp_status_norm"] = (
        ptp["ptp_status"].astype(str).str.upper().str.strip()
    )

    kept = ptp[ptp["ptp_status_norm"].isin(kept_statuses)]

    kept_month = (
        kept.assign(month=kept["event_at"].dt.to_period("M").astype(str))
        .groupby("month")
        .agg(ptps_kept=("ptp_id", "nunique"))
        .reset_index()
    )

    monthly = monthly.merge(kept_month, on="month", how="left")
else:
    monthly["ptps_kept"] = 0

# -------------------------------------------------------------------
# Field visits
# -------------------------------------------------------------------

field_month = (
    field_visits.assign(month=field_visits["event_at"].dt.to_period("M").astype(str))
    .groupby("month")
    .agg(
        field_visits=("visit_id", "nunique"),
        field_visit_accounts=("account_id", "nunique"),
    )
    .reset_index()
)

monthly = monthly.merge(field_month, on="month", how="left")

# -------------------------------------------------------------------
# SMS
# -------------------------------------------------------------------

sms_month = (
    sms.assign(month=sms["event_at"].dt.to_period("M").astype(str))
    .groupby("month")
    .agg(
        sms_events=("sms_event_id", "nunique"),
        sms_accounts=("account_id", "nunique"),
    )
    .reset_index()
)

monthly = monthly.merge(sms_month, on="month", how="left")

# -------------------------------------------------------------------
# WhatsApp
# -------------------------------------------------------------------

whatsapp_month = (
    whatsapp.assign(month=whatsapp["event_at"].dt.to_period("M").astype(str))
    .groupby("month")
    .agg(
        whatsapp_events=("whatsapp_event_id", "nunique"),
        whatsapp_accounts=("account_id", "nunique"),
    )
    .reset_index()
)

monthly = monthly.merge(whatsapp_month, on="month", how="left")

# -------------------------------------------------------------------
# Fill missing numeric values
# -------------------------------------------------------------------

numeric_columns = monthly.select_dtypes(include="number").columns

monthly[numeric_columns] = monthly[numeric_columns].fillna(0)

# -------------------------------------------------------------------
# Derived performance metrics
# -------------------------------------------------------------------

monthly["answer_rate_pct"] = (
    monthly["answered_calls"]
    / monthly["calls"].replace(0, pd.NA)
    * 100
)

monthly["ptp_kept_rate_pct"] = (
    monthly["ptps_kept"]
    / monthly["ptps"].replace(0, pd.NA)
    * 100
)

monthly["recovered_per_successful_payment"] = (
    monthly["recovered_amount"]
    / monthly["successful_payments"].replace(0, pd.NA)
)

monthly["recovered_per_call"] = (
    monthly["recovered_amount"]
    / monthly["calls"].replace(0, pd.NA)
)

monthly["recovered_per_answered_call"] = (
    monthly["recovered_amount"]
    / monthly["answered_calls"].replace(0, pd.NA)
)

monthly["payment_rate_from_answered_accounts_pct"] = (
    monthly["accounts_with_successful_payment"]
    / monthly["answered_accounts"].replace(0, pd.NA)
    * 100
)

# -------------------------------------------------------------------
# Important analytical warning:
# Current outstanding_amount is NOT a historical monthly denominator.
# Therefore do not label monthly recovered_amount / outstanding_amount
# as a true historical recovery rate.
# -------------------------------------------------------------------

monthly["monthly_recovery_rate_warning"] = (
    "Historical outstanding denominator unavailable; "
    "use recovered_amount trend rather than treating current "
    "outstanding_amount as historical monthly recovery denominator."
)

# -------------------------------------------------------------------
# Sort and round
# -------------------------------------------------------------------

monthly = monthly.sort_values("month").reset_index(drop=True)

for column in monthly.select_dtypes(include="number").columns:
    monthly[column] = monthly[column].round(4)

# -------------------------------------------------------------------
# Save main report
# -------------------------------------------------------------------

output = REPORTS / "monthly_performance.csv"
monthly.to_csv(output, index=False)

# -------------------------------------------------------------------
# Findings
# -------------------------------------------------------------------

highest_recovery_month = monthly.loc[
    monthly["recovered_amount"].idxmax()
]

highest_answer_rate_month = monthly.loc[
    monthly["answer_rate_pct"].idxmax()
]

highest_payment_month = monthly.loc[
    monthly["successful_payments"].idxmax()
]

first_month = monthly.iloc[0]
last_month = monthly.iloc[-1]

findings = f"""# Monthly Performance Findings

## Observation Period

Observed activity period:
- Start: {start_month}
- End: {end_month}
- Months analyzed: {len(monthly)}

## Recovery

Highest monthly recovered amount:
- Month: {highest_recovery_month["month"]}
- Recovered amount: {highest_recovery_month["recovered_amount"]:,.2f}

First observed month recovered amount:
- {first_month["recovered_amount"]:,.2f}

Last observed month recovered amount:
- {last_month["recovered_amount"]:,.2f}

## Contact Performance

Highest answer rate:
- Month: {highest_answer_rate_month["month"]}
- Answer rate: {highest_answer_rate_month["answer_rate_pct"]:.2f}%

First observed month answer rate:
- {first_month["answer_rate_pct"]:.2f}%

Last observed month answer rate:
- {last_month["answer_rate_pct"]:.2f}%

## Payment Performance

Highest successful-payment count:
- Month: {highest_payment_month["month"]}
- Successful payments: {highest_payment_month["successful_payments"]:.0f}

First observed month successful payments:
- {first_month["successful_payments"]:.0f}

Last observed month successful payments:
- {last_month["successful_payments"]:.0f}

## Analytical Warning

A true monthly recovery rate requires a historical outstanding balance
or eligible-balance denominator for each month.

The accounts table contains an outstanding_amount field, but using the
current account-level outstanding amount as a historical monthly
denominator would create a misleading metric.

Therefore this analysis emphasizes:
- recovered amount
- successful payment count
- answer rate
- PTP activity
- PTP kept rate
- payment conversion
- recovery per call
- recovery per answered call

The reported 11% improvement must not be validated from this table alone.
Additional attribution, denominator, cohort, and portfolio-mix analysis
is required.
"""

(REPORTS / "monthly_performance_findings.md").write_text(
    findings,
    encoding="utf-8"
)

print("Monthly performance analysis completed")
print(f"Observation period: {start_month} to {end_month}")
print(f"Months analyzed: {len(monthly)}")
print("Reports:")
print("reports/monthly_performance.csv")
print("reports/monthly_performance_findings.md")
