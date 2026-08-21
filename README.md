
# CredResolve Data Analyst Assignment

## Project Overview

This project analyzes a multi-table collections and recovery dataset and builds a reproducible account-centric analytical layer for recovery performance analysis.

The project focuses on data quality, entity relationships, duplicate handling, temporal consistency, reproducible cleaning, validation, and recovery analytics.

## Analytical Approach

The project uses `account_id` as the canonical analytical entity.

`borrower_id` is retained as a secondary relationship attribute because borrower identity analysis identified significant attribute conflicts.

Operational event tables remain available at their original event-level grain.

## Project Workflow

### Phase 1: Dataset Inventory

The raw datasets were systematically profiled to identify:

- dataset sizes
- schemas
- primary-key candidates
- identifier fields
- foreign-key relationships
- categorical fields
- monetary fields
- temporal fields
- data-quality issues
- table grain

### Phase 2: Data Quality and Cleaning

The analysis covered:

- exact duplicate detection
- non-exact duplicate detection
- borrower identity conflicts
- account-borrower relationships
- agent identity variability
- missing identifiers
- temporal consistency
- timezone variability
- disposition-code analysis

The raw data was preserved without modification.

Cleaning transformations were applied to a separate analytical layer.

### Phase 3: Cleaned Analytical Layer

The cleaned layer contains the operational datasets required for analysis.

Cleaning rules include:

- removal of confirmed exact duplicates
- preservation of non-exact conflicting records
- explicit quality flags
- retention of missing identifiers
- retention of temporal inconsistencies with flags
- no fabricated identifier values

### Phase 4: Validation

The final cleaned layer passed:

**49 validation checks**

**49 passed**

**0 failed**

Validation covers:

- expected row counts
- duplicate removal
- unique event identifiers
- account relationships
- quality flags
- cleaned-layer integrity

### Phase 5: Recovery Analysis

Recovery analysis covers:

- portfolio recovery
- collection activity
- contact-to-payment conversion
- channel performance
- risk-segment recovery
- DPD recovery
- payment-method performance
- operational findings
- business recommendations

## Key Results

Portfolio outstanding amount:

**10,489,035,343.00**

Successful recovered amount:

**1,315,583,964.64**

Observed recovery rate:

**12.54%**

Accounts:

**30,000**

Successful payments:

**17,534**

Calls:

**90,079**

Answered calls:

**17,896**

Promises to pay:

**18,000**

Kept promises:

**4,489**

Field visits:

**25,000**

SMS events:

**45,000**

WhatsApp events:

**60,000**

### Recovery Findings

The strongest observed DPD recovery rate is the **31-60 DPD** band at approximately **13.20%**.

The **1-30 DPD** band has the lowest observed recovery rate among the analyzed DPD bands at approximately **12.30%**.

The highest observed recovery-rate risk segment is **MEDIUM** at approximately **12.58%**.

The lowest is **NPA** at approximately **12.50%**.

NACH generated the largest observed successful-payment amount among the analyzed payment methods.

### Contact and Payment

13,535 accounts had an answered call.

6,050 accounts had both an answered call and a successful payment.

The answered-call to payment rate was approximately **44.70%**.

7,234 paid accounts did not have an answered call.

Therefore, successful payment cannot be attributed solely to voice contact.

## Important Data-Quality Findings

Borrower identity quality is a significant limitation.

Borrower attributes show substantial conflicts across:

- name
- phone
- email
- city
- state
- timestamps

The project therefore avoids treating borrower identity as a fully reliable analytical key.

Calls also contain non-exact duplicate records involving differences in `agent_id` and `event_at`.

Account status history contains timing inconsistencies between event and recorded timestamps.

These records are retained and flagged rather than silently deleted.

## Cleaning Principles

The project follows these principles:

1. Raw data is preserved.
2. Cleaning is performed on copies.
3. Exact duplicates are removed only when unambiguous.
4. Non-exact conflicts are retained.
5. Missing identifiers are flagged.
6. No identifiers are fabricated.
7. Temporal inconsistencies are retained and flagged.
8. Validation is performed after cleaning.
9. Analytical conclusions explicitly acknowledge data-quality limitations.

## Repository Structure

```text
CredResolve_Data_Analyst/
|
├── data/
│   ├── raw/
│   ├── staging/
│   ├── clean/
│   ├── cleaned/
│   └── golden/
|
├── reports/
│   ├── final_report.md
│   ├── final_cleaned_layer_validation.csv
│   ├── cleaning_decisions.md
│   ├── recovery_summary.csv
│   ├── channel_performance.csv
│   ├── recovery_funnel.csv
│   ├── recovery_by_risk.csv
│   ├── recovery_by_dpd.csv
│   ├── payment_method_performance.csv
│   └── ...
|
├── src/
│   ├── dataset_inventory.py
│   ├── duplicate_profile.py
│   ├── cleaning_pipeline.py
│   ├── clean_payments.py
│   ├── clean_calls.py
│   ├── clean_borrowers.py
│   ├── final_cleaned_layer_validation.py
│   ├── recovery_analysis.py
│   ├── recovery_funnel_analysis.py
│   ├── final_recovery_analysis.py
│   └── build_final_report.py
|
├── reports/
├── requirements.txt
├── README.md
└── .gitignore