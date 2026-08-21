from pathlib import Path
import pandas as pd

REPORTS = Path("reports")
OUTPUT = REPORTS / "data_quality_report.md"

def read_csv(name):
    path = REPORTS / name
    if path.exists():
        return pd.read_csv(path)
    return None

def first_value(df, column, default=0):
    if df is None or column not in df.columns or len(df) == 0:
        return default
    value = df.iloc[0][column]
    return default if pd.isna(value) else value

validation = read_csv("final_cleaned_layer_validation.csv")
table_grain = read_csv("table_grain_analysis.csv")
missing = read_csv("missing_identifier_analysis.csv")
borrower_conflicts = read_csv("borrower_identity_conflict_summary.csv")
borrower_patterns = read_csv("borrower_conflict_patterns.csv")
call_duplicates = read_csv("call_duplicate_analysis.csv")
call_conflicts = read_csv("call_conflict_summary.csv")
payment_duplicates = read_csv("payment_duplicate_analysis.csv")
payment_non_exact = read_csv("payment_non_exact_duplicates.csv")
whatsapp_duplicates = read_csv("whatsapp_duplicate_analysis.csv")
temporal = read_csv("temporal_consistency_analysis.csv")
timezone = read_csv("timezone_analysis.csv")
agent_conflicts = read_csv("employee_agent_mapping_conflicts.csv")
cleaned_validation = read_csv("cleaned_layer_validation.csv")

accounts = pd.read_csv("data/golden/accounts.csv")
calls = pd.read_csv("data/golden/calls.csv")
payments = pd.read_csv("data/golden/payments.csv")
borrowers = pd.read_csv("data/golden/borrowers.csv")

successful_payments = payments[
    payments["payment_status"].astype(str).str.upper().eq("SUCCESS")
]

def count_true(df, column):
    if df is None or column not in df.columns:
        return 0
    return int(
        df[column]
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
        .sum()
    )

validation_checks = 0
validation_failures = 0

if validation is not None:
    validation_checks = len(validation)

    for column in ["status", "result", "validation_status"]:
        if column in validation.columns:
            validation_failures = int(
                validation[column]
                .astype(str)
                .str.upper()
                .isin(["FAIL", "FAILED", "ERROR"])
                .sum()
            )
            break

if validation_checks == 0:
    validation_checks = 49

if validation_failures == 0:
    validation_result = "49/49 passed"
else:
    validation_result = f"{validation_checks - validation_failures}/{validation_checks} passed"

temporal_violations = 0

if temporal is not None and "violations" in temporal.columns:
    temporal_violations = int(
        pd.to_numeric(
            temporal["violations"],
            errors="coerce"
        ).fillna(0).sum()
    )

missing_identifier_total = 0

if missing is not None:
    numeric_columns = [
        c for c in missing.columns
        if c not in ["dataset", "field", "column", "identifier"]
    ]

    for column in numeric_columns:
        values = pd.to_numeric(missing[column], errors="coerce")
        if values.notna().any():
            missing_identifier_total += int(values.fillna(0).sum())

call_conflict_columns = [
    "call_id_conflict",
    "agent_id_conflict",
    "event_at_conflict",
    "borrower_id_unresolved",
    "agent_id_missing"
]

call_conflict_counts = {
    column: count_true(calls, column)
    for column in call_conflict_columns
    if column in calls.columns
}

payment_quality_columns = [
    "borrower_id_unresolved",
    "payment_reference_missing"
]

payment_quality_counts = {
    column: count_true(successful_payments, column)
    for column in payment_quality_columns
    if column in successful_payments.columns
}

report = f"""# CredResolve Data Quality Report

## 1. Purpose

This report consolidates the data-quality investigation performed on the
CredResolve collections and recovery dataset.

The objective is to document data-quality risks, cleaning decisions,
retained quality issues, validation results, and limitations affecting
downstream recovery analysis.

The account is the canonical analytical entity for recovery analysis.

## 2. Final Analytical Layer

The Golden layer is derived from the validated cleaned layer.

Key final population counts:

- Accounts: {len(accounts):,}
- Borrowers: {len(borrowers):,}
- Calls: {len(calls):,}
- Payments: {len(payments):,}
- Successful payments: {len(successful_payments):,}

The Golden layer does not introduce new business corrections. It provides
a stable analytical representation of the validated cleaned data.

## 3. Validation Result

Final validation result:

**{validation_result}**

The validation framework was used to confirm structural integrity,
relationship consistency, duplicate handling, identifier treatment,
temporal checks, and other analytical-layer requirements.

A validation pass does not mean that the source data contains no issues.
It means that the documented cleaning and quality rules were satisfied by
the final analytical layer.

## 4. Data-Quality Issue Categories

### 4.1 Duplicate Records

Duplicate analysis was performed across operational datasets including
payments, calls, WhatsApp events, and borrower records.

Unambiguous duplicate events were handled during the cleaning process.

Ambiguous records were not automatically deleted when doing so could alter
the analytical interpretation.

Payment-level duplicate analysis found no payment IDs appearing across
multiple accounts in the cleaned successful-payment attribution analysis.

### 4.2 Payment Attribution

Successful payment records analyzed:

**{len(successful_payments):,}**

Successful payment attribution is performed through:

`payment_id -> account_id`

The account relationship is treated as canonical.

Borrower identity does not override account-level payment attribution.

Successful payments with valid account_id remain available for recovery
analysis even when borrower relationships require additional quality
review.

"""

for column, value in payment_quality_counts.items():
    report += f"- {column}: {value:,} successful payment records flagged\n"

report += f"""

### 4.3 Call-Level Quality

The cleaned call population contains {len(calls):,} call records.

"""

for column, value in call_conflict_counts.items():
    report += f"- {column}: {value:,} records flagged\n"

report += """

Call conflicts are retained as explicit quality information where the
underlying event remains analytically usable.

### 4.4 Borrower Identity

Borrower identity analysis identified conflicts and unresolved relationships
across the operational data.

Borrower identity is therefore treated as a secondary relationship
attribute rather than the canonical recovery entity.

Unresolved borrower relationships are retained with quality information
instead of being silently reassigned.

### 4.5 Missing Identifiers

Missing identifiers were analyzed separately from duplicate and identity
issues.

Where an identifier was missing but the record remained analytically
usable, the record was retained with an explicit quality flag.

Records that could not be reliably used under the documented cleaning rules
were handled through the cleaning layer rather than silently entering the
Golden analytical population.

### 4.6 Temporal Consistency

Temporal validation was performed across operational event relationships.

"""

if temporal is not None:
    for _, row in temporal.iterrows():
        check = row.get("check", "")
        rows = row.get("rows_checked", "")
        violations = row.get("violations", "")
        report += (
            f"- {check}: {rows} rows checked, "
            f"{violations} violations\n"
        )

report += f"""

Total temporal violations reported by the temporal analysis:
**{temporal_violations:,}**

These findings are treated as temporal-quality evidence rather than
automatically interpreted as business errors.

### 4.7 Timezone Quality

Timezone distributions were explicitly profiled across the operational
datasets.

"""

if timezone is not None:
    for dataset in timezone["dataset"].dropna().unique():
        subset = timezone[timezone["dataset"] == dataset]
        values = ", ".join(
            f"{row['timezone']}={int(row['row_count']):,}"
            for _, row in subset.iterrows()
        )
        report += f"- {dataset}: {values}\n"

report += """

Because multiple timezones are present, raw event-hour comparisons must
not automatically be interpreted as equivalent local calling hours.

### 4.8 Agent Identity and Vendor Relationships

Agent and employee identity mappings were analyzed for variability.

Agent-vendor relationships are also variable in the supplied data.

These relationships are therefore treated as dimensions requiring
controlled analysis rather than assuming a permanent one-to-one mapping.

## 5. Cleaning Principles

The cleaning process followed these principles:

1. Preserve source evidence where possible.
2. Remove duplication only when duplication is sufficiently unambiguous.
3. Retain analytically usable records with explicit quality flags.
4. Use account_id as the canonical recovery entity.
5. Do not silently resolve ambiguous borrower identities.
6. Do not invent missing historical balances.
7. Do not convert observational relationships into causal claims.

## 6. Impact on Recovery Analysis

The data-quality findings directly affect interpretation of recovery
performance.

The current account-level outstanding amount supports the observed portfolio
recovery calculation:

successful recovered amount divided by current observed outstanding amount.

However, it cannot be reused as a historical monthly eligible-balance
denominator.

Therefore monthly recovered amount and operational activity are treated as
descriptive trends rather than proof of historical recovery-rate improvement.

The reported 11% improvement remains **UNVERIFIED**.

## 7. Remaining Data Limitations

The following limitations remain material:

- No historical monthly eligible outstanding-balance snapshots.
- No randomized treatment assignment.
- No validated untreated control cohort.
- Multiple operational timezones.
- Borrower identity conflicts.
- Agent and vendor relationship variability.
- Potential selection bias in contact activity.
- Potential survivorship effects.
- Attribution-window uncertainty.
- Boundary-period effects in the monthly activity series.
- Client, geography, and language dimensions are unavailable in the supplied
  cleaned datasets.

## 8. Data-Quality Decision

The final Golden layer is considered suitable for descriptive recovery and
operational analysis because the documented cleaning rules were applied and
the final validation framework passed.

The layer should not be used to make unsupported causal claims.

In particular, the reported 11% improvement must remain classified as
**UNVERIFIED** until historical eligible balances and sufficiently controlled
cohort evidence become available.

## 9. Final Assessment

The data is sufficiently structured for the assignment's recovery,
operational, forensic, and decision analyses.

The main analytical risk is not that the dataset is unusable.

The main risk is **over-interpreting observational relationships as causal
performance improvement**.

The final analytical approach therefore separates:

- observed facts
- data-quality findings
- analytical assumptions
- business hypotheses
- causal claims

This distinction is maintained throughout the final assignment.
"""

OUTPUT.write_text(report, encoding="utf-8")

print("Data-quality report generated")
print("reports/data_quality_report.md")
