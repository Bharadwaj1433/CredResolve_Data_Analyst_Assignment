import pandas as pd
from pathlib import Path

CLEANED = Path("data/cleaned")
GOLDEN = Path("data/golden")
REPORTS = Path("reports")

GOLDEN.mkdir(parents=True, exist_ok=True)

tables = [
    "accounts.csv",
    "account_status_history.csv",
    "agents.csv",
    "agent_sessions.csv",
    "borrowers.csv",
    "calls.csv",
    "call_attempts.csv",
    "call_dispositions.csv",
    "campaigns.csv",
    "complaints.csv",
    "daily_targeting.csv",
    "field_visits.csv",
    "payments.csv",
    "promises_to_pay.csv",
    "sms_events.csv",
    "vendor_telephony.csv",
    "whatsapp_events.csv"
]

summary = []

for table in tables:
    source = CLEANED / table
    destination = GOLDEN / table

    df = pd.read_csv(source)

    df.to_csv(
        destination,
        index=False,
        encoding="utf-8"
    )

    summary.append({
        "table": table,
        "rows": len(df),
        "columns": len(df.columns),
        "source": str(source),
        "golden": str(destination)
    })

summary_df = pd.DataFrame(summary)

summary_df.to_csv(
    REPORTS / "golden_layer_summary.csv",
    index=False,
    encoding="utf-8"
)

decisions = """# Golden Layer Decisions

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
"""

(REPORTS / "golden_layer_decisions.md").write_text(
    decisions,
    encoding="utf-8"
)

print("Golden layer completed")
print("reports/golden_layer_summary.csv")
print("reports/golden_layer_decisions.md")
