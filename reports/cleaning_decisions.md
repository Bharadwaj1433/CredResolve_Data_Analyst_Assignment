# Cleaning Decisions

## Analytical Entity

Account-level analysis uses account_id as the canonical analytical entity.

Borrower_id is retained as a reference attribute because borrower records contain duplicate and conflicting identity attributes.

## Raw Data

Raw CSV files are preserved without modification.

All transformations are applied to the cleaned analytical layer.

## Exact Duplicates

Exact duplicate rows are removed from the cleaned analytical layer after duplicate analysis confirms that the records contain no conflicting values.

## Payments

Payment records contain 500 duplicate payment_id groups.

486 groups contain fully identical duplicate rows.

14 groups differ only because one record contains a payment_reference while the duplicate has a missing payment_reference.

The populated payment_reference record is retained.

The resulting cleaned payments table contains 25,000 rows and 25,000 unique payment IDs.

Payment status is retained because SUCCESS, FAILED, PENDING, and REVERSED have different analytical meanings.

## WhatsApp Events

WhatsApp events contain 600 duplicate event groups.

The duplicates are exact duplicates.

One record per whatsapp_event_id is retained.

The cleaned table contains 60,000 rows and 60,000 unique event IDs.

## Calls

Calls contain 1,350 duplicate call_id groups.

1,271 groups are exact duplicates and are reduced to one record.

79 call IDs contain non-exact records.

68 groups contain agent_id differences.

11 groups contain event_at differences.

Non-exact call records are retained rather than arbitrarily deleted.

Conflict flags are added for call_id_conflict, agent_id_conflict, and event_at_conflict.

## Borrower Relationships

Borrower relationships are not treated as fully reliable.

Borrower IDs appearing in operational tables but absent from the borrower master are flagged using borrower_id_unresolved.

These records are retained.

Exact duplicate borrower master rows are removed.

Conflicting borrower attributes are preserved for later identity-resolution analysis.

## Missing Identifiers

Missing identifiers are retained and explicitly flagged.

The cleaned layer contains flags for missing agent_id, vendor_id, payment_reference, and borrower_id where applicable.

No identifier values are fabricated.

## Temporal Data

Timestamp fields are converted to datetime-compatible values during cleaning.

Event and recording timestamps are retained separately.

Account status history contains timing inconsistencies between event_at and recorded_at.

These records are retained and flagged rather than deleted.

## Canonical Analytical Rule

The cleaned analytical layer is account-centric.

Account_id is used as the primary entity for recovery activity analysis.

Borrower_id is treated as a secondary attribute with explicit quality flags.

Event-level identifiers remain available for event-level analysis.

## Validation

The final cleaned-layer validation contains 49 checks.

All 49 checks passed and no validation checks failed.

## Data Integrity

The raw data files remain unchanged. All cleaning transformations were applied to copies in the cleaned analytical layer.

The cleaning transformations used to produce the current cleaned layer are represented by scripts stored under src.
