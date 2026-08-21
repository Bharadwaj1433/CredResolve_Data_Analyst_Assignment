import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell("""# CredResolve Data Analyst Assignment

## Analytical Investigation

This notebook presents the consolidated analytical investigation performed on the validated Golden layer.

The analysis covers portfolio recovery, operational performance, data quality, forensic findings, statistical limitations, the reported 11% improvement, counterfactual comparison, and the ₹10 Cr investment decision.
"""))

cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path("../data/golden")
REPORTS = Path("../reports")

accounts = pd.read_csv(BASE / "accounts.csv")
payments = pd.read_csv(BASE / "payments.csv")
calls = pd.read_csv(BASE / "calls.csv")

successful_payments = payments[
    payments["payment_status"].astype(str).str.upper().eq("SUCCESS")
].copy()

print("Accounts:", len(accounts))
print("Calls:", len(calls))
print("Payments:", len(payments))
print("Successful payments:", len(successful_payments))
"""))

cells.append(nbf.v4.new_markdown_cell("""## 1. Portfolio Recovery

The account is the canonical analytical entity. Recovery is based on successful payments attributed through `account_id`.
"""))

cells.append(nbf.v4.new_code_cell("""recovered_amount = successful_payments["amount"].sum()
outstanding_amount = accounts["outstanding_amount"].sum()

recovery_rate = recovered_amount / outstanding_amount * 100

portfolio_summary = pd.DataFrame({
    "metric": [
        "Accounts",
        "Outstanding amount",
        "Successful payment amount",
        "Successful payments",
        "Observed recovery rate"
    ],
    "value": [
        len(accounts),
        outstanding_amount,
        recovered_amount,
        len(successful_payments),
        recovery_rate
    ]
})

portfolio_summary
"""))

cells.append(nbf.v4.new_markdown_cell("""## 2. Data Quality and Validation

The cleaned analytical layer passed 49 of 49 validation checks.

Cleaning decisions were designed to remove unambiguous duplication while retaining ambiguous records with explicit quality flags.
"""))

cells.append(nbf.v4.new_code_cell("""validation = pd.read_csv(
    REPORTS / "final_cleaned_layer_validation.csv"
)

validation.head()
"""))

cells.append(nbf.v4.new_markdown_cell("""## 3. Monthly Performance

Monthly activity is descriptive because historical eligible outstanding-balance denominators are unavailable.

Therefore recovered amount is not presented as a historical recovery-rate measure.
"""))

cells.append(nbf.v4.new_code_cell("""monthly = pd.read_csv(
    REPORTS / "monthly_performance.csv"
)

monthly[[
    "month",
    "recovered_amount",
    "successful_payments",
    "calls",
    "answered_calls",
    "answer_rate_pct",
    "recovered_per_call"
]]
"""))

cells.append(nbf.v4.new_markdown_cell("""## 4. Portfolio Drivers

Recovery varies across DPD, risk, account status, and loan type.

These differences are descriptive and do not establish causality.
"""))

cells.append(nbf.v4.new_code_cell("""driver_summary = pd.read_csv(
    REPORTS / "driver_summary.csv"
)

driver_summary
"""))

cells.append(nbf.v4.new_code_cell("""for name in [
    "recovery_by_dpd.csv",
    "recovery_by_risk.csv",
    "recovery_by_account_status.csv",
    "recovery_by_loan_type.csv"
]:
    print("\\n", name)
    display(pd.read_csv(REPORTS / name))
"""))

cells.append(nbf.v4.new_markdown_cell("""## 5. Channel and Campaign Performance

Observed channel and campaign differences are used as operational hypotheses.

They are not interpreted as causal effects because portfolio mix, contact selection, agent allocation, and other confounders remain relevant.
"""))

cells.append(nbf.v4.new_code_cell("""channel = pd.read_csv(
    REPORTS / "channel_performance.csv"
)

campaign = pd.read_csv(
    REPORTS / "campaign_recovery_performance.csv"
)

display(channel)
display(campaign.head(20))
"""))

cells.append(nbf.v4.new_markdown_cell("""## 6. Forensic Analysis

The forensic investigation covered payment attribution, vendor performance, calling time, and attempt frequency.

Payment attribution is sufficiently defined at account level through:

`payment_id -> account_id`

Successful payment attribution coverage is 100% for the cleaned successful-payment population.
"""))

cells.append(nbf.v4.new_code_cell("""forensic = pd.read_csv(
    REPORTS / "forensic_attempt_frequency.csv"
)

vendor = pd.read_csv(
    REPORTS / "forensic_vendor_performance.csv"
)

calling_time = pd.read_csv(
    REPORTS / "forensic_calling_time.csv"
)

display(forensic)
display(vendor)
display(calling_time)
"""))

cells.append(nbf.v4.new_markdown_cell("""## 7. Statistical Investigation

The analysis identified portfolio-mix effects, selection bias, survivorship concerns, attribution-window limitations, Simpson's-paradox risk, and boundary-period effects.

These limitations prevent a causal interpretation of aggregate recovery movement.
"""))

cells.append(nbf.v4.new_code_cell("""print(
    (REPORTS / "statistical_investigation_findings.md").read_text(
        encoding="utf-8"
    )
)
"""))

cells.append(nbf.v4.new_markdown_cell("""## 8. Reported 11% Improvement

The reported 11% improvement is classified as **UNVERIFIED**.

The principal limitation is the absence of historical eligible outstanding-balance denominators.

The available data supports descriptive recovery comparisons but does not establish a causal or mix-adjusted 11% improvement.
"""))

cells.append(nbf.v4.new_code_cell("""verification = pd.read_csv(
    REPORTS / "improvement_verification.csv"
)

verification
"""))

cells.append(nbf.v4.new_markdown_cell("""## 9. Counterfactual Benchmark

Answered-call accounts are treated as the observational treatment group and accounts without answered calls as the comparison group.

The observed difference is a benchmark, not a causal treatment effect.
"""))

cells.append(nbf.v4.new_code_cell("""counterfactual = pd.read_csv(
    REPORTS / "counterfactual_analysis.csv"
) if (REPORTS / "counterfactual_analysis.csv").exists() else None

if counterfactual is not None:
    display(counterfactual)
else:
    print(
        (REPORTS / "counterfactual_analysis_findings.md").read_text(
            encoding="utf-8"
        )
    )
"""))

cells.append(nbf.v4.new_markdown_cell("""## 10. ₹10 Cr Investment Decision

The recommended approach is a controlled collections and contactability optimization pilot rather than an unconditional ₹10 Cr rollout.

The observed evidence is insufficient to justify assuming the reported 11% improvement.
"""))

cells.append(nbf.v4.new_code_cell("""investment = pd.read_csv(
    REPORTS / "investment_scenarios.csv"
)

recommendation = pd.read_csv(
    REPORTS / "investment_recommendation.csv"
)

display(investment)
display(recommendation)
"""))

cells.append(nbf.v4.new_markdown_cell("""## Final Conclusion

The portfolio shows measurable recovery activity and meaningful variation across operational and portfolio dimensions.

However, the reported 11% improvement cannot be independently validated from the supplied data because historical eligible balances and sufficiently controlled cohorts are unavailable.

The recommended business decision is therefore a controlled pilot with a predefined holdout, explicit attribution window, eligible-balance measurement, and a break-even threshold before scaling.

The analysis distinguishes observed relationships from causal claims and avoids presenting unverified improvement as fact.
"""))

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "name": "python"
    }
}

Path("notebooks").mkdir(exist_ok=True)

with open(
    "notebooks/credresolve_analysis.ipynb",
    "w",
    encoding="utf-8"
) as f:
    nbf.write(nb, f)

print("Analysis notebook created")
print("notebooks/credresolve_analysis.ipynb")
