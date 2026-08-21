# Golden Layer Decisions

## Analytical Entity

account_id is the canonical analytical entity for recovery analysis.

## Payment Attribution

The accepted account-level attribution path is:

payment_id -> account_id

Successful payments with valid account_id remain in the analytical layer.

borrower_id is retained as a secondary relationship attribute and does not
override account-level attribution.

## Borrower Identity

Borrower identity issues are retained through explicit quality indicators.
Unresolved borrower relationships are not silently reassigned.

## Duplicate Handling

Unambiguous duplicate operational records were handled during the cleaned
layer process.

Ambiguous records were retained with explicit quality information where
deletion could change analytical interpretation.

## Missing Identifiers

Missing identifiers are retained with quality flags where the record remains
analytically usable.

## Temporal Data

Temporal inconsistencies identified during validation are retained with their
quality context unless the record was unambiguously invalid or duplicated.

## Golden Layer Principle

The golden layer is derived from the validated cleaned layer.

No new business correction is introduced at this stage.

The purpose of the golden layer is to provide a stable, reproducible,
account-centric analytical source for downstream recovery analysis.

## Validation

The cleaned analytical layer previously passed 49 of 49 validation checks.

The golden layer is a controlled representation of that validated layer.
