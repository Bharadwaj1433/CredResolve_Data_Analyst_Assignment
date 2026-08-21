from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

BASE = Path(__file__).resolve().parents[1]
REPORTS = BASE / "reports"
OUTPUT = REPORTS / "executive_dashboard.pdf"

monthly = pd.read_csv(REPORTS / "monthly_performance.csv")
recovery = pd.read_csv(REPORTS / "recovery_summary.csv")
driver = pd.read_csv(REPORTS / "driver_summary.csv")
investment = pd.read_csv(REPORTS / "investment_recommendation.csv")
counterfactual = pd.read_csv(REPORTS / "counterfactual_treatment_control.csv")

monthly["month"] = monthly["month"].astype(str)

accounts = 30000
successful_payments = 17534
recovered_amount = 1315583964.64
recovery_rate = 12.54
answered_accounts = 13535
answered_coverage = 45.12

reported_improvement = "UNVERIFIED"

treatment_rate = 44.70
comparison_rate = 43.94
observed_difference = 0.76

investment_amount = 100000000
break_even_accounts = 1010
investment_decision = "CONTROLLED PILOT"

fig = plt.figure(figsize=(16, 9))
fig.patch.set_facecolor("white")

fig.text(
    0.04, 0.95,
    "CredResolve Executive Dashboard",
    fontsize=24,
    fontweight="bold",
    va="top"
)

fig.text(
    0.04, 0.915,
    "Recovery Performance | 2025-12 to 2026-08",
    fontsize=11,
    color="dimgray"
)

kpis = [
    ("Recovered Amount", f"₹{recovered_amount:,.0f}"),
    ("Successful Payments", f"{successful_payments:,}"),
    ("Portfolio Recovery Rate", f"{recovery_rate:.2f}%"),
    ("11% Improvement", reported_improvement)
]

x_positions = [0.04, 0.27, 0.50, 0.73]

for x, (label, value) in zip(x_positions, kpis):
    fig.text(
        x, 0.835,
        label,
        fontsize=10,
        color="dimgray"
    )
    fig.text(
        x, 0.785,
        value,
        fontsize=18,
        fontweight="bold"
    )

ax1 = fig.add_axes([0.06, 0.48, 0.42, 0.24])

ax1.plot(
    monthly["month"],
    monthly["recovered_amount"] / 1_000_000,
    marker="o",
    linewidth=2
)

ax1.set_title(
    "Monthly Recovered Amount",
    loc="left",
    fontsize=12,
    fontweight="bold"
)

ax1.set_ylabel("₹ Million")
ax1.tick_params(axis="x", rotation=45)
ax1.grid(axis="y", alpha=0.2)

ax2 = fig.add_axes([0.54, 0.48, 0.38, 0.24])

driver_labels = [
    "DPD: 31-60",
    "Loan: Consumer",
    "Status: Writeoff",
    "Risk: Medium"
]

driver_values = [
    13.203,
    12.878,
    12.634,
    12.576
]

ax2.barh(driver_labels, driver_values)

ax2.set_title(
    "Observed Portfolio Recovery Differences",
    loc="left",
    fontsize=12,
    fontweight="bold"
)

ax2.set_xlabel("Recovery Rate %")
ax2.invert_yaxis()
ax2.grid(axis="x", alpha=0.2)

fig.text(
    0.06, 0.40,
    "KEY EVIDENCE",
    fontsize=11,
    fontweight="bold"
)

evidence = [
    "Answered-account coverage: 45.12%",
    "Answered-call accounts payment rate: 44.70%",
    "Non-answered-call accounts payment rate: 43.94%",
    "Observed difference: +0.76 percentage points",
    "Historical eligible monthly balances are unavailable"
]

y = 0.365

for item in evidence:
    fig.text(
        0.065, y,
        "• " + item,
        fontsize=9.5
    )
    y -= 0.027

fig.text(
    0.54, 0.40,
    "BUSINESS DECISION",
    fontsize=11,
    fontweight="bold"
)

fig.text(
    0.54, 0.355,
    "11% improvement: UNVERIFIED",
    fontsize=13,
    fontweight="bold"
)

fig.text(
    0.54, 0.325,
    "₹10 Cr recommendation: CONTROLLED PILOT",
    fontsize=12,
    fontweight="bold"
)

fig.text(
    0.54, 0.295,
    f"Break-even requirement: {break_even_accounts:,} additional paying accounts",
    fontsize=9.5
)

fig.text(
    0.54, 0.270,
    "Do not commit the full investment without controlled measurement.",
    fontsize=9.5
)

fig.text(
    0.04, 0.19,
    "EXECUTIVE INTERPRETATION",
    fontsize=11,
    fontweight="bold"
)

interpretation = (
    "Recovery activity increased materially after the low-volume boundary period, "
    "but the final month also shows a substantial decline. Portfolio, cohort, "
    "selection, attribution-window, and denominator effects prevent the observed "
    "movement from being interpreted as a proven 11% recovery improvement."
)

fig.text(
    0.04, 0.145,
    interpretation,
    fontsize=9.5,
    wrap=True,
    va="top"
)

fig.text(
    0.04, 0.075,
    "Decision basis: descriptive evidence + forensic analysis + driver analysis + "
    "statistical investigation + counterfactual analysis.",
    fontsize=8.5,
    color="dimgray"
)

fig.text(
    0.04, 0.035,
    "Source: CredResolve Golden analytical layer and validated analytical reports.",
    fontsize=8,
    color="dimgray"
)

with PdfPages(OUTPUT) as pdf:
    pdf.savefig(fig, bbox_inches="tight")

plt.close(fig)

print("Executive dashboard created")
print(f"Output: {OUTPUT}")