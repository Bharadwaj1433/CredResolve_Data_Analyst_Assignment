# Performance Change Analysis

Observation period: 2025-12 to 2026-08.

## Boundary-Month Warning

The first observed month is 2025-12 and the last observed month is 2026-08.
These boundary months must not automatically be interpreted as complete operational months. Large changes at the beginning or end of the observation window may reflect partial-period coverage.

## First vs Last Observed Month

- recovered_amount: 0.00 -> 47,109,695.31; percentage change not reported because the first value is zero or unavailable.
- successful_payments: 0.00 -> 616.00; percentage change not reported because the first value is zero or unavailable.
- calls: 1.00 -> 3,211.00; +321000.00%.
- answered_calls: 0.00 -> 630.00; percentage change not reported because the first value is zero or unavailable.
- answer_rate_pct: 0.00 -> 19.62; percentage change not reported because the first value is zero or unavailable.
- ptps: 0.00 -> 685.00; percentage change not reported because the first value is zero or unavailable.
- ptps_kept: 0.00 -> 0.00; percentage change not reported because the first value is zero or unavailable.
- ptp_kept_rate_pct: nan -> 0.00; percentage change not reported because the first value is zero or unavailable.
- recovered_per_call: 0.00 -> 14,671.35; percentage change not reported because the first value is zero or unavailable.
- recovered_per_answered_call: nan -> 74,777.29; percentage change not reported because the first value is zero or unavailable.

## Largest Meaningful Monthly Movements

- recovered_amount: largest increase in 2026-03 (+11.03%), largest decrease in 2026-08 (-74.84%).
- successful_payments: largest increase in 2026-03 (+11.29%), largest decrease in 2026-08 (-74.76%).
- calls: largest increase in 2026-01 (+1269700.00%), largest decrease in 2026-08 (-74.48%).
- answered_calls: largest increase in 2026-03 (+12.62%), largest decrease in 2026-08 (-74.11%).
- answer_rate_pct: largest increase in 2026-05 (+5.37%), largest decrease in 2026-07 (-5.22%).
- ptps: largest increase in 2026-03 (+13.02%), largest decrease in 2026-08 (-73.91%).
- recovered_per_call: largest increase in 2026-07 (+2.87%), largest decrease in 2026-04 (-2.76%).
- recovered_per_answered_call: largest increase in 2026-07 (+8.54%), largest decrease in 2026-05 (-4.04%).

## Interpretation

The observed monthly series shows substantial changes in activity volume across the observation window.
However, the extreme December-to-January increase and July-to-August decline should not be interpreted as causal business-performance changes without first establishing whether the boundary months represent complete periods.
The first observed month contains extremely low activity, while the final observed month also has substantially lower activity than preceding months.
Therefore, boundary-period effects are a material analytical risk and must be separated from genuine operational changes.

## Important Limitation

A true historical recovery rate requires a time-specific eligible outstanding balance denominator.
The current account-level outstanding_amount field should not be reused as a historical monthly denominator.
Consequently, recovered amount and activity trends are treated as descriptive evidence rather than proof of an improvement in true recovery efficiency.

## Next Required Investigation

The next analysis should test portfolio mix, DPD mix, campaign, channel, and denominator effects before attributing the observed monthly changes to operational performance.