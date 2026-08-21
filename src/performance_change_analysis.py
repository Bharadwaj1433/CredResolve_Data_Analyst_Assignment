import pandas as pd
from pathlib import Path

REPORTS = Path("reports")

monthly = pd.read_csv(REPORTS / "monthly_performance.csv")

monthly["month"] = pd.to_datetime(
    monthly["month"],
    format="%Y-%m"
)

monthly = monthly.sort_values("month").reset_index(drop=True)

monthly["observation_position"] = "FULL_PERIOD"

if len(monthly) >= 1:
    monthly.loc[0, "observation_position"] = "FIRST_OBSERVED_MONTH"

if len(monthly) >= 2:
    monthly.loc[len(monthly) - 1, "observation_position"] = "LAST_OBSERVED_MONTH"



metrics = [
    "recovered_amount",
    "successful_payments",
    "calls",
    "answered_calls",
    "answer_rate_pct",
    "ptps",
    "ptps_kept",
    "ptp_kept_rate_pct",
    "recovered_per_call",
    "recovered_per_answered_call",
]

available_metrics = [
    metric for metric in metrics
    if metric in monthly.columns
]


change = monthly[
    ["month", "observation_position"] + available_metrics
].copy()

for metric in available_metrics:

    change[f"{metric}_mom_abs"] = change[metric].diff()

    previous = change[metric].shift(1)


    change[f"{metric}_mom_pct"] = (
        (change[metric] - previous)
        / previous.replace(0, pd.NA)
        * 100
    )

    change[f"{metric}_mom_pct"] = (
        change[f"{metric}_mom_pct"]
        .replace([float("inf"), float("-inf")], pd.NA)
    )

first = monthly.iloc[0]
last = monthly.iloc[-1]

overall_rows = []

for metric in available_metrics:

    first_value = first[metric]
    last_value = last[metric]

    if pd.isna(first_value) or pd.isna(last_value):
        pct_change = pd.NA

    elif first_value == 0:
        pct_change = pd.NA

    else:
        pct_change = (
            (last_value - first_value)
            / first_value
            * 100
        )

    overall_rows.append({
        "metric": metric,
        "first_month": first["month"].strftime("%Y-%m"),
        "last_month": last["month"].strftime("%Y-%m"),
        "first_value": first_value,
        "last_value": last_value,
        "overall_change_abs": last_value - first_value,
        "overall_change_pct": pct_change,
    })

overall_summary = pd.DataFrame(overall_rows)

movement_rows = []

for metric in available_metrics:

    pct_col = f"{metric}_mom_pct"
    abs_col = f"{metric}_mom_abs"

    temp = change[
        ["month", pct_col, abs_col]
    ].dropna()

    if temp.empty:
        continue

    largest_increase = temp.loc[
        temp[pct_col].idxmax()
    ]

    largest_decrease = temp.loc[
        temp[pct_col].idxmin()
    ]

    movement_rows.append({
        "metric": metric,

        "largest_increase_month":
            largest_increase["month"].strftime("%Y-%m"),

        "largest_increase_abs":
            largest_increase[abs_col],

        "largest_increase_pct":
            largest_increase[pct_col],

        "largest_decrease_month":
            largest_decrease["month"].strftime("%Y-%m"),

        "largest_decrease_abs":
            largest_decrease[abs_col],

        "largest_decrease_pct":
            largest_decrease[pct_col],
    })

movement_summary = pd.DataFrame(movement_rows)

trend = monthly[
    ["month"] + available_metrics
].copy()

for metric in available_metrics:
    trend[f"{metric}_3m_avg"] = (
        trend[metric]
        .rolling(window=3, min_periods=3)
        .mean()
    )

change["month"] = change["month"].dt.strftime("%Y-%m")
trend["month"] = trend["month"].dt.strftime("%Y-%m")

change.to_csv(
    REPORTS / "monthly_performance_changes.csv",
    index=False
)

movement_summary.to_csv(
    REPORTS / "performance_movement_summary.csv",
    index=False
)

overall_summary.to_csv(
    REPORTS / "performance_first_vs_last.csv",
    index=False
)

trend.to_csv(
    REPORTS / "performance_rolling_trends.csv",
    index=False
)

lines = []

lines.append("# Performance Change Analysis")
lines.append("")
lines.append(
    f"Observation period: "
    f"{first['month'].strftime('%Y-%m')} to "
    f"{last['month'].strftime('%Y-%m')}."
)
lines.append("")

lines.append("## Boundary-Month Warning")
lines.append("")
lines.append(
    f"The first observed month is "
    f"{first['month'].strftime('%Y-%m')} and the last observed month is "
    f"{last['month'].strftime('%Y-%m')}."
)
lines.append(
    "These boundary months must not automatically be interpreted as "
    "complete operational months. Large changes at the beginning or "
    "end of the observation window may reflect partial-period coverage."
)
lines.append("")

lines.append("## First vs Last Observed Month")
lines.append("")

for _, row in overall_summary.iterrows():

    pct = row["overall_change_pct"]

    if pd.isna(pct):
        lines.append(
            f"- {row['metric']}: "
            f"{row['first_value']:,.2f} -> "
            f"{row['last_value']:,.2f}; "
            f"percentage change not reported because the first value "
            f"is zero or unavailable."
        )
    else:
        lines.append(
            f"- {row['metric']}: "
            f"{row['first_value']:,.2f} -> "
            f"{row['last_value']:,.2f}; "
            f"{pct:+.2f}%."
        )

lines.append("")

lines.append("## Largest Meaningful Monthly Movements")
lines.append("")

for _, row in movement_summary.iterrows():

    lines.append(
        f"- {row['metric']}: "
        f"largest increase in {row['largest_increase_month']} "
        f"({row['largest_increase_pct']:+.2f}%), "
        f"largest decrease in {row['largest_decrease_month']} "
        f"({row['largest_decrease_pct']:+.2f}%)."
    )

lines.append("")

lines.append("## Interpretation")
lines.append("")

lines.append(
    "The observed monthly series shows substantial changes in activity "
    "volume across the observation window."
)

lines.append(
    "However, the extreme December-to-January increase and "
    "July-to-August decline should not be interpreted as causal "
    "business-performance changes without first establishing whether "
    "the boundary months represent complete periods."
)

lines.append(
    "The first observed month contains extremely low activity, while "
    "the final observed month also has substantially lower activity "
    "than preceding months."
)

lines.append(
    "Therefore, boundary-period effects are a material analytical "
    "risk and must be separated from genuine operational changes."
)

lines.append("")

lines.append("## Important Limitation")
lines.append("")

lines.append(
    "A true historical recovery rate requires a time-specific "
    "eligible outstanding balance denominator."
)

lines.append(
    "The current account-level outstanding_amount field should not "
    "be reused as a historical monthly denominator."
)

lines.append(
    "Consequently, recovered amount and activity trends are treated "
    "as descriptive evidence rather than proof of an improvement in "
    "true recovery efficiency."
)

lines.append("")

lines.append("## Next Required Investigation")
lines.append("")

lines.append(
    "The next analysis should test portfolio mix, DPD mix, campaign, "
    "channel, and denominator effects before attributing the observed "
    "monthly changes to operational performance."
)

(REPORTS / "performance_change_findings.md").write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print("Performance change analysis completed")
print("Boundary months explicitly flagged")
print("Infinite percentage changes excluded")
print("Reports:")
print("reports/monthly_performance_changes.csv")
print("reports/performance_movement_summary.csv")
print("reports/performance_first_vs_last.csv")
print("reports/performance_rolling_trends.csv")
print("reports/performance_change_findings.md")
