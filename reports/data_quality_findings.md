# Initial Data Quality Findings

## Dataset Structure

The package contains 17 operational datasets and one data dictionary. The raw inventory contains 18 CSV files including data_dictionary.csv.

## Duplicate and Non-Unique Identifiers

- agents.agent_id: 30,000 rows and 1,000 unique values.
- borrowers.borrower_id: 30,600 rows and 11,015 unique values.
- calls.call_id: 91,350 rows and 90,000 unique values.
- payments.payment_id: 25,500 rows and 25,000 unique values.
- whatsapp_events.whatsapp_event_id: 60,600 rows and 60,000 unique values.

These fields require grain and duplication analysis before being treated as unique record identifiers.

## Referential Integrity

The account-based relationships tested against accounts are structurally consistent with zero observed orphan values.

Borrower-based relationships show systematic orphan values:

- accounts.borrower_id: 8.32%
- calls.borrower_id: 8.16%
- call_attempts.borrower_id: 8.15%
- call_dispositions.borrower_id: 7.82%
- whatsapp_events.borrower_id: 8.13%
- sms_events.borrower_id: 8.40%
- field_visits.borrower_id: 8.38%
- promises_to_pay.borrower_id: 8.02%
- payments.borrower_id: 8.15%
- complaints.borrower_id: 8.66%
- account_status_history.borrower_id: 8.36%

Borrower-level joins therefore require additional investigation before being treated as fully reliable.

## Missing Values

Observed missing values include:

- accounts.borrower_id: 455
- calls.agent_id: 1,827
- call_attempts.vendor_id: 2,400
- payments.payment_reference: 382
- field_visits.scheduled_at: 250

## Temporal Data

Temporal fields are currently represented as strings when loaded from the raw CSV files.

The dataset includes event, creation, update, recording, scheduling, resolution, campaign start/end, and promised-date fields.

Timezone fields include UTC, Asia/Kolkata, and Asia/Dubai.

Timestamp normalization should therefore be handled explicitly during the data preparation phase.

## Identifier Complexity

The datasets contain multiple identifier systems including entity IDs, event IDs, employee codes, vendor IDs, provider IDs, message IDs, and payment references.

Identifier resolution should be performed before analytical joins where necessary.

## Versioned Definitions

The datasets contain schema and business-definition version fields including schema_version, strategy_version, and disposition_version.

Call disposition analysis must account for legacy and versioned disposition definitions.

## Payment Semantics

Payment records contain SUCCESS, FAILED, PENDING, and REVERSED statuses.

Recovery calculations should therefore use an explicitly defined treatment of payment status rather than summing all payment rows indiscriminately.

## Initial Analytical Risk

The primary risks identified during inventory are:

1. Non-unique entity and event identifiers.
2. Borrower-level referential-integrity gaps.
3. Missing identifiers and timestamps.
4. Multiple timestamp and timezone representations.
5. Multiple identifier systems.
6. Versioned business definitions.
7. Payment-event duplication and status semantics.

No raw records have been deleted or modified during the inventory phase.
