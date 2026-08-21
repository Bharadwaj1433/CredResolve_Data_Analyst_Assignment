# Forensic Analysis Findings

## Payment Attribution

Successful payment records analyzed: 17,534.
Accounts with successful payments: 13,284.
Successful payments missing payment references: 254.

Payment attribution should be performed at account level because account_id
is the canonical analytical entity.

## Vendor Performance

Vendor-level call performance is available for comparative analysis.
Vendor differences should not be interpreted as causal without controlling
for campaign, portfolio, channel, and agent mix.

## Calling Time

Call answer rates vary by hour and should be evaluated before selecting
calling windows for operational changes.

## Attempt Frequency

Payment conversion varies across attempt-frequency bands.
Higher attempt counts should not automatically be interpreted as better
performance because accounts receiving more attempts may be systematically
harder or easier to recover.

## Conclusion

The forensic evidence supports further investigation of attribution,
vendor, calling-time, and attempt-frequency effects.
These relationships are observational and should not be treated as causal
without cohort or controlled analysis.