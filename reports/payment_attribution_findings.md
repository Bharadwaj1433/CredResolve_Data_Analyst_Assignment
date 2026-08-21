# Payment Attribution Analysis

## Canonical Attribution Rule

Account-level analysis uses account_id as the canonical analytical entity.
A payment is attributed to an account using its recorded account_id.
Borrower_id is treated as a secondary relationship attribute and does not
override the account relationship.

## Attribution Coverage

Successful payment records: 17,534.
Successful payment amount: 1,315,583,964.64.
Successfully attributed records: 17,534.
Successfully attributed amount: 1,315,583,964.64.
Successful-record attribution coverage: 100.00%.
Successful-amount attribution coverage: 100.00%.

## Payment Reference

Successful payments missing payment_reference: 254.

Missing payment_reference is retained as a data-quality issue.
It does not invalidate account-level attribution when account_id is valid.

## Borrower Relationship

Successful payments with unresolved borrower relationships: 1,453.

Unresolved borrower relationships do not cause the payment to be removed
from account-level recovery analysis.

## Duplicate / Multi-account Conflicts

Payment IDs appearing more than once: 0.
Payment IDs linked to multiple accounts: 0.

The cleaned payment layer contains one record per payment_id.
Any multi-account payment conflict would require separate investigation
before using borrower-level attribution.

## Golden Attribution Decision

For recovery analysis, the accepted attribution path is:

payment_id -> account_id

account_id is the canonical analytical entity.
Borrower_id remains available for secondary identity analysis.

Successful payments with valid account_id are included in recovery analysis.
Records with unresolved borrower relationships are retained because the
account relationship remains analytically usable.

## Conclusion

Payment attribution is sufficiently defined for account-level recovery analysis.
The remaining payment-reference and borrower-relationship issues are explicitly
flagged rather than silently corrected.