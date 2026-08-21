# CredResolve Data Quality Report

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

- Accounts: 30,000
- Borrowers: 30,000
- Calls: 90,079
- Payments: 25,000
- Successful payments: 17,534

The Golden layer does not introduce new business corrections. It provides
a stable analytical representation of the validated cleaned data.

## 3. Validation Result

Final validation result:

**49/49 passed**

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

**17,534**

Successful payment attribution is performed through:

`payment_id -> account_id`

The account relationship is treated as canonical.

Borrower identity does not override account-level payment attribution.

Successful payments with valid account_id remain available for recovery
analysis even when borrower relationships require additional quality
review.

- borrower_id_unresolved: 1,453 successful payment records flagged
- payment_reference_missing: 254 successful payment records flagged


### 4.3 Call-Level Quality

The cleaned call population contains 90,079 call records.

- call_id_conflict: 158 records flagged
- agent_id_conflict: 136 records flagged
- event_at_conflict: 22 records flagged
- borrower_id_unresolved: 7,368 records flagged
- agent_id_missing: 1,827 records flagged


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

- recorded_after_event: 60000 rows checked, 29809 violations
- scheduled_after_event: 25000 rows checked, 0 violations
- promised_before_event: 18000 rows checked, 0 violations
- resolution_before_event: 8000 rows checked, 0 violations


Total temporal violations reported by the temporal analysis:
**29,809**

These findings are treated as temporal-quality evidence rather than
automatically interpreted as business errors.

### 4.7 Timezone Quality

Timezone distributions were explicitly profiled across the operational
datasets.

- accounts: UTC=10,096, Asia/Kolkata=9,981, Asia/Dubai=9,923
- calls: Asia/Kolkata=30,485, Asia/Dubai=30,464, UTC=30,401
- agent_sessions: Asia/Kolkata=7,506, UTC=7,494
- vendor_telephony: UTC=8, Asia/Kolkata=7


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
