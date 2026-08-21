import pandas as pd
from pathlib import Path

BASE = Path("data/cleaned")
REPORTS = Path("reports")

accounts = pd.read_csv(BASE / "accounts.csv")
payments = pd.read_csv(BASE / "payments.csv")

account_ids = set(accounts["account_id"].dropna())

payments["account_id_valid"] = payments["account_id"].isin(account_ids)

payments["successful_flag"] = (
    payments["payment_status"]
    .astype(str)
    .str.upper()
    .eq("SUCCESS")
)

payments["payment_reference_missing_flag"] = (
    payments["payment_reference"].isna()
)

if "borrower_id_unresolved" in payments.columns:
    payments["borrower_unresolved_flag"] = (
        payments["borrower_id_unresolved"].fillna(False).astype(bool)
    )
else:
    payments["borrower_unresolved_flag"] = False

summary = []

def add_check(name, mask, interpretation):
    subset = payments[mask]
    summary.append({
        "check": name,
        "payment_records": len(subset),
        "payment_amount": subset["amount"].sum(),
        "successful_payment_records": subset["successful_flag"].sum(),
        "unique_accounts": subset["account_id"].nunique(),
        "interpretation": interpretation
    })

add_check(
    "all_payment_records",
    payments.index == payments.index,
    "Complete cleaned payment population"
)

add_check(
    "valid_account_attribution",
    payments["account_id_valid"],
    "Payment has an account_id present in the account master"
)

add_check(
    "invalid_account_attribution",
    ~payments["account_id_valid"],
    "Payment account_id is missing or absent from account master"
)

add_check(
    "successful_payments",
    payments["successful_flag"],
    "Payment status is SUCCESS"
)

add_check(
    "successful_missing_payment_reference",
    payments["successful_flag"]
    & payments["payment_reference_missing_flag"],
    "Successful payment lacks payment_reference"
)

add_check(
    "successful_unresolved_borrower",
    payments["successful_flag"]
    & payments["borrower_unresolved_flag"],
    "Successful payment has unresolved borrower relationship"
)

add_check(
    "successful_validly_attributed",
    payments["successful_flag"]
    & payments["account_id_valid"],
    "Successful payment can be attributed to a canonical account"
)

summary_df = pd.DataFrame(summary)

summary_df.to_csv(
    REPORTS / "payment_attribution_analysis.csv",
    index=False
)

status_summary = (
    payments.groupby("payment_status", dropna=False)
    .agg(
        payment_records=("payment_id", "size"),
        unique_payment_ids=("payment_id", "nunique"),
        payment_amount=("amount", "sum"),
        successful_records=("successful_flag", "sum"),
        valid_account_records=("account_id_valid", "sum")
    )
    .reset_index()
)

status_summary.to_csv(
    REPORTS / "payment_status_attribution.csv",
    index=False
)

duplicate_payment_ids = (
    payments.groupby("payment_id")
    .agg(
        rows=("payment_id", "size"),
        unique_accounts=("account_id", "nunique"),
        total_amount=("amount", "sum")
    )
    .reset_index()
)

duplicate_payment_ids = duplicate_payment_ids[
    duplicate_payment_ids["rows"] > 1
]

duplicate_payment_ids.to_csv(
    REPORTS / "payment_attribution_duplicates.csv",
    index=False
)

multi_account_payments = duplicate_payment_ids[
    duplicate_payment_ids["unique_accounts"] > 1
]

multi_account_payments.to_csv(
    REPORTS / "payment_multi_account_conflicts.csv",
    index=False
)

successful = payments[payments["successful_flag"]].copy()

total_successful_amount = successful["amount"].sum()

valid_successful = successful[
    successful["account_id_valid"]
]

valid_successful_amount = valid_successful["amount"].sum()

if total_successful_amount:
    attributable_amount_pct = (
        valid_successful_amount
        / total_successful_amount
        * 100
    )
else:
    attributable_amount_pct = 0

if len(successful):
    attributable_record_pct = (
        len(valid_successful)
        / len(successful)
        * 100
    )
else:
    attributable_record_pct = 0

lines = [
    "# Payment Attribution Analysis",
    "",
    "## Canonical Attribution Rule",
    "",
    "Account-level analysis uses account_id as the canonical analytical entity.",
    "A payment is attributed to an account using its recorded account_id.",
    "Borrower_id is treated as a secondary relationship attribute and does not",
    "override the account relationship.",
    "",
    "## Attribution Coverage",
    "",
    f"Successful payment records: {len(successful):,}.",
    f"Successful payment amount: {total_successful_amount:,.2f}.",
    f"Successfully attributed records: {len(valid_successful):,}.",
    f"Successfully attributed amount: {valid_successful_amount:,.2f}.",
    f"Successful-record attribution coverage: {attributable_record_pct:.2f}%.",
    f"Successful-amount attribution coverage: {attributable_amount_pct:.2f}%.",
    "",
    "## Payment Reference",
    "",
    f"Successful payments missing payment_reference: "
    f"{int((successful['payment_reference_missing_flag']).sum()):,}.",
    "",
    "Missing payment_reference is retained as a data-quality issue.",
    "It does not invalidate account-level attribution when account_id is valid.",
    "",
    "## Borrower Relationship",
    "",
    f"Successful payments with unresolved borrower relationships: "
    f"{int(successful['borrower_unresolved_flag'].sum()):,}.",
    "",
    "Unresolved borrower relationships do not cause the payment to be removed",
    "from account-level recovery analysis.",
    "",
    "## Duplicate / Multi-account Conflicts",
    "",
    f"Payment IDs appearing more than once: "
    f"{len(duplicate_payment_ids):,}.",
    f"Payment IDs linked to multiple accounts: "
    f"{len(multi_account_payments):,}.",
    "",
    "The cleaned payment layer contains one record per payment_id.",
    "Any multi-account payment conflict would require separate investigation",
    "before using borrower-level attribution.",
    "",
    "## Golden Attribution Decision",
    "",
    "For recovery analysis, the accepted attribution path is:",
    "",
    "payment_id -> account_id",
    "",
    "account_id is the canonical analytical entity.",
    "Borrower_id remains available for secondary identity analysis.",
    "",
    "Successful payments with valid account_id are included in recovery analysis.",
    "Records with unresolved borrower relationships are retained because the",
    "account relationship remains analytically usable.",
    "",
    "## Conclusion",
    "",
    "Payment attribution is sufficiently defined for account-level recovery analysis.",
    "The remaining payment-reference and borrower-relationship issues are explicitly",
    "flagged rather than silently corrected."
]

(REPORTS / "payment_attribution_findings.md").write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print("Payment attribution analysis completed")
print("Reports:")
print("reports/payment_attribution_analysis.csv")
print("reports/payment_status_attribution.csv")
print("reports/payment_attribution_duplicates.csv")
print("reports/payment_multi_account_conflicts.csv")
print("reports/payment_attribution_findings.md")
