# Driver Analysis Findings

## Available Portfolio Drivers

The supplied data supports analysis of DPD, risk segment, account status,
loan type, agent, agent tenure, campaign, channel, vendor, calling time,
attempt frequency, and borrower relationship quality.

## Unavailable Dimensions

Client, geography, and language fields are not present in the supplied
cleaned datasets. These dimensions are therefore not analyzed and no
values are inferred.

## Portfolio Drivers

Recovery performance varies across DPD, risk, account status, loan type,
and borrower relationship quality.
These differences identify portfolio segments with different observed
outcomes but do not establish causality.

## Agent and Tenure

Agent-level performance is available from call activity.
Agent rankings should be restricted to agents with sufficient activity
because low-volume agents can produce unstable rates.

Agent tenure is derived from joined_at relative to the end of the
observation period.
Tenure differences are observational and do not establish that tenure
causes better or worse recovery performance.

## Campaign and Channel

Campaign and channel performance varies across the portfolio.
Campaign and channel comparisons must be interpreted alongside portfolio
mix, agent allocation, vendor allocation, and contact selection.

## Vendor

Vendor performance is available for comparison.
The observed agent-vendor relationship is highly variable, so vendor
differences should not be interpreted as independent causal effects.

## Calling Time

Calling-time performance varies by observed event hour.
Because calls contain multiple timezones, raw event hours should not be
interpreted as equivalent local calling hours without timezone normalization.

## Attempt Frequency

Payment conversion varies across attempt-frequency bands.
The relationship is subject to selection bias because attempt frequency
is not randomly assigned.

## Decision Use

Observed driver differences should be treated as hypotheses for controlled
testing or cohort analysis rather than causal explanations.

## 11% Improvement Claim

Driver variation provides plausible descriptive explanations for changes
in aggregate recovery performance, but it does not independently validate
the reported 11% improvement.

The improvement remains unverified because historical eligible balances,
cohort comparability, selection, attribution timing, and portfolio mix
cannot be fully controlled with the supplied data.