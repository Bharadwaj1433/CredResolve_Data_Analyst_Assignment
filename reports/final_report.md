# CredResolve Data Analyst Assignment

## 1. Executive Summary

This project analyzes a multi-table collections and recovery dataset with an account-centric analytical approach.

The final cleaned analytical layer contains 30,000 accounts and supports recovery, collections activity, data-quality, and operational performance analysis.

The portfolio contains an observed outstanding amount of 10,489,035,343.00. Successful payments contribute 1,315,583,964.64, producing an observed recovery rate of 12.54%.

The analysis identified substantial borrower identity conflicts, duplicate operational events, missing identifiers, call-level conflicts, and temporal inconsistencies. These issues were not hidden through aggressive deletion. Instead, records were cleaned where duplication was unambiguous and retained with explicit quality flags where ambiguity could affect analytical interpretation.

The final cleaned layer passed all 49 validation checks with 0 failures.

The strongest observed DPD recovery rate occurs in the 31-60 DPD band at 13.20%, while the 1-30 DPD band has the lowest observed recovery rate at 12.30% among the analyzed bands.

## 2. Project Objective

The objective is to transform raw collections data into a reliable analytical layer and use that layer to understand recovery performance.

The work focuses on:

- data inventory and structural profiling
- entity and identity analysis
- duplicate detection
- relationship validation
- temporal consistency
- missing identifier analysis
- reproducible cleaning
- final validation
- recovery performance analysis
- operational recommendations

The analytical entity is the account.

account_id is treated as the canonical analytical identifier for recovery analysis, while borrower_id is retained as a secondary relationship attribute because borrower identity quality is inconsistent.

## 3. Dataset Overview

The project contains operational datasets covering:

- accounts
- borrowers
- agents
- agent sessions
- campaigns
- daily targeting
- calls
- call attempts
- call dispositions
- payments
- promises to pay
- complaints
- field visits
- SMS events
- WhatsApp events
- account status history
- vendor telephony

The cleaned layer preserves the structure required for event-level and account-level analysis.

The raw data remains unchanged.

## 4. Analytical Grain

The analysis established that tables have different grains.

Examples include:

- accounts at account level
- borrowers at borrower-record level
- calls at call-event level
- payments at payment-event level
- account status history at account-status-event level

The project therefore avoids treating all tables as if they had the same grain.

Account-level recovery analysis aggregates operational events to account_id.

Event identifiers remain available for event-level analysis.

## 5. Data Quality Assessment

The initial profiling identified several major data-quality themes.

### Duplicate Records

Payments contained 500 duplicate payment identifier groups.

WhatsApp events contained 600 duplicate event groups.

Calls contained 1,350 duplicate call identifier groups.

Borrower records contained exact duplicate rows.

The cleaning process distinguishes between exact duplicates and non-exact duplicates rather than deleting records solely because an identifier appears more than once.

### Missing Identifiers

Missing identifiers were identified in:

- account borrower relationships
- call agent relationships
- call attempt vendor relationships
- payment references

Missing values were retained and converted into explicit quality flags.

No identifier values were fabricated.

### Borrower Identity Quality

Borrower identity resolution showed substantial attribute variability.

The borrower conflict analysis found that:

- name conflicts affect 8,518 borrower IDs at the highest observed conflicting attribute rate
- five identity fields conflict for 68.51% of borrower IDs in the analyzed pattern

Because of this, borrower identity was not treated as a fully reliable analytical key.

### Account-Borrower Relationships

Account-level relationship analysis showed that operational records can associate the same account with multiple borrower identifiers.

This is why account-level analysis uses account_id as the canonical analytical entity.

## 6. Duplicate Resolution

### Payments

Exact payment duplicates were removed.

The 14 non-exact payment groups differed because one duplicate contained a populated payment reference while the other contained a missing reference.

The populated reference was retained.

The final payments table contains 25,000 records and 25,000 unique payment IDs.

### WhatsApp

WhatsApp duplicate events were exact duplicates.

One record per whatsapp_event_id was retained.

The cleaned table contains 60,000 unique WhatsApp events.

### Calls

Calls contained 1,350 duplicate call groups.

1,271 groups were exact duplicates and were reduced.

79 call IDs contained non-exact records.

The non-exact groups primarily involved differences in:

- gent_id
- event_at

These records were retained rather than arbitrarily deleted.

Conflict flags were added.

## 7. Temporal Consistency

Timestamp validation found that all analyzed datasets contained valid timestamp values.

However, account status history contained timing inconsistencies between event and recorded timestamps.

The analysis identified 29,809 records where 
ecorded_at occurred before event_at.

These records were retained and explicitly flagged because deletion would remove potentially useful operational history.

## 8. Timezone Analysis

The dataset contains multiple timezone values, including:

- UTC
- Asia/Kolkata
- Asia/Dubai

Timezone information is therefore preserved rather than normalized into an assumed single business timezone without evidence.

## 9. Cleaning Methodology

The cleaning process follows these principles:

1. preserve raw data
2. clean copies rather than raw files
3. remove only unambiguous exact duplicates
4. retain non-exact conflicts
5. add explicit quality flags
6. never fabricate identifiers
7. retain temporal inconsistencies with flags
8. validate the resulting analytical layer

The cleaning process is implemented through reproducible Python scripts under src.

## 10. Validation

The final validation performed 49 checks.

Passed checks: 49

Failed checks: 0

The validation covered:

- expected row counts
- exact duplicate removal
- unique event identifiers
- missing account relationships
- quality flags
- cleaned-layer integrity

The result is a reproducible cleaned analytical layer.

## 11. Recovery Portfolio

The portfolio contains:

- 30,000 accounts
- 10,489,035,343.00 outstanding amount
- 1,315,583,964.64 successful recovered amount
- 17,534 successful payments
- 25,000 total payment records

The observed recovery rate is 12.54%.

This is treated as an observed portfolio metric rather than a causal estimate.

## 12. Collections Activity

The cleaned data contains:

- 90,079 calls
- 17,896 answered calls
- 18,000 promises to pay
- 4,489 kept promises
- 25,000 field visits
- 45,000 SMS events
- 60,000 WhatsApp events

The gap between total PTPs and kept PTPs indicates that promise creation alone should not be treated as recovery success.

## 13. Contact-to-Payment Funnel

Accounts with an answered call: 13,535

Accounts with a successful payment: 13,284

Accounts with both an answered call and successful payment: 6,050

Answered-call to payment rate: 44.70%

Paid accounts without an answered call: 7,234

The final number is important because it demonstrates that successful payments cannot automatically be attributed to voice contact.

The analysis therefore avoids making unsupported causal claims about channels.

## 14. Channel Performance

The observable channel-success analysis shows:

| Channel | Activity | Successful Outcomes | Observable Success Rate |
|---|---:|---:|---:|
| WHATSAPP | 60,000 | 29,919 | 49.87% |\n| SMS | 45,000 | 11,219 | 24.93% |\n| VOICE | 90,079 | 17,896 | 19.87% |\n| FIELD | 25,000 | 4,205 | 16.82% |\n
The highest observable channel-success rate is WHATSAPP at 49.87%.

These rates are not treated as monetary recovery rates because each channel has a different observable outcome definition.

## 15. Risk Segment Recovery

| Risk Segment | Accounts | Outstanding | Recovered | Recovery Rate |
|---|---:|---:|---:|---:|
| MEDIUM | 7,533 | 2,628,179,457.23 | 330,510,083.85 | 12.58% |\n| LOW | 7,513 | 2,633,311,095.86 | 330,857,833.09 | 12.56% |\n| HIGH | 7,552 | 2,646,182,591.51 | 331,598,234.29 | 12.53% |\n| NPA | 7,402 | 2,581,362,198.40 | 322,617,813.41 | 12.50% |\n
The highest observed recovery rate is in the MEDIUM segment at 12.58%.

The lowest observed recovery rate is in the NPA segment at 12.50%.

The differences are relatively small, so risk segment alone should not determine collection strategy.

## 16. DPD Recovery

| DPD Band | Accounts | Outstanding | Recovered | Recovery Rate |
|---|---:|---:|---:|---:|
| 31-60 | 5,514 | 1,914,490,301.17 | 252,777,083.08 | 13.20% |\n| 61-90 | 5,468 | 1,895,868,396.28 | 238,735,656.37 | 12.59% |\n| 91-180 | 5,453 | 1,896,357,498.83 | 235,069,503.41 | 12.40% |\n| 0 | 2,685 | 948,218,629.01 | 117,461,931.08 | 12.39% |\n| 1-30 | 10,880 | 3,834,100,517.71 | 471,539,790.70 | 12.30% |\n
The 31-60 DPD band has the highest observed recovery rate at 13.20%.

The 1-30 DPD band has the lowest observed recovery rate at 12.30% among the analyzed DPD bands.

This suggests that collection treatment should consider delinquency stage rather than applying a single strategy across all accounts.

## 17. Payment Method Performance

| Payment Method | Successful Payments | Recovered Amount | Accounts | Average Payment |
|---|---:|---:|---:|---:|
| NACH | 3,600 | 271,212,741.81 | 3,380 | 75,336.87 |\n| NETBANKING | 3,527 | 266,285,325.82 | 3,322 | 75,499.10 |\n| CARD | 3,560 | 264,614,778.60 | 3,360 | 74,329.99 |\n| UPI | 3,413 | 257,610,970.86 | 3,217 | 75,479.34 |\n| CASH | 3,434 | 255,860,147.55 | 3,254 | 74,507.91 |\n
NACH has the largest observed successful-payment amount at 271,212,741.81.

This is an observational comparison and does not establish that payment method causes higher recovery.

## 18. Key Findings

### Finding 1: Recovery is relatively low compared with outstanding exposure

The observed recovery rate is 12.54% against the analyzed outstanding amount.

This indicates substantial remaining recovery opportunity.

### Finding 2: Contact alone does not explain payment

Although 13,535 accounts had answered calls, 7,234 paid accounts did not have an answered call.

This means recovery attribution must account for multiple collection channels and customer-initiated payment behavior.

### Finding 3: DPD stage matters

The strongest observed recovery rate occurs in the 31-60 DPD band.

The 1-30 DPD band has a lower observed recovery rate.

Early-stage collections therefore should not automatically be considered the highest-performing stage.

### Finding 4: PTP volume does not equal PTP success

There are 18,000 PTP records but only 4,489 kept PTPs.

PTP quality and follow-through should therefore be monitored separately from PTP creation.

### Finding 5: Borrower identity quality limits borrower-level analysis

Borrower attributes contain significant conflicts.

Account-level analysis is therefore more reliable for the primary recovery analysis.

## 19. Business Recommendations

### 1. Use account-centric recovery monitoring

Use account_id as the primary recovery entity and retain borrower quality flags for secondary analysis.

### 2. Build DPD-specific collection strategies

Create separate treatment strategies for different DPD bands rather than applying one generic workflow.

### 3. Focus on the conversion gap

Monitor accounts that receive collection activity but do not produce successful payments.

These accounts represent a more actionable operational queue than raw activity volume alone.

### 4. Improve PTP follow-through

Track kept PTP rate as a core KPI.

A high number of PTPs without corresponding payments should trigger follow-up treatment.

### 5. Use channel metrics carefully

Channel engagement should be evaluated against actual payment outcomes wherever reliable attribution is available.

Message delivery or call answer rates should not be presented as direct recovery rates.

### 6. Preserve data-quality transparency

Downstream dashboards and reports should retain quality flags rather than silently removing uncertain records.

### 7. Prioritize by exposure as well as recovery rate

A segment with a slightly lower recovery rate may still represent the largest recovery opportunity if it has substantially greater outstanding exposure.

## 20. Limitations

The analysis is observational.

It does not establish causal relationships between collection actions and payments.

Campaign-level monetary attribution is not treated as causal because multiple campaigns can touch the same account.

Borrower-level attribution is affected by identity conflicts.

Channel success rates are based on channel-specific observable outcomes and should not be directly interpreted as comparable monetary recovery rates.

The overall recovery rate assumes that the outstanding amount and successful payment amounts are comparable for the analytical period.

## 21. Reproducibility

The project is structured so that analysis can be reproduced through Python scripts.

Raw files remain outside the Git repository.

The cleaned analytical layer is generated from the raw data through scripts in src.

Analytical outputs are stored under 
eports.

The final validation confirms that the cleaned layer satisfies the expected structural and quality checks.

## 22. Final Conclusion

The project successfully converts a noisy multi-table collections dataset into a validated account-centric analytical layer.

The cleaning strategy deliberately distinguishes between safe corrections and ambiguous operational records.

Exact duplicates are removed where appropriate, while non-exact conflicts, missing identifiers, borrower identity problems, and temporal inconsistencies are retained with explicit quality flags.

The resulting analytical layer passes all 49 validation checks.

The recovery analysis shows an observed portfolio recovery rate of 12.54% and identifies meaningful differences across delinquency stages, risk segments, payment methods, and collection activity.

The strongest next operational opportunity is not simply increasing contact volume. It is improving conversion from collection activity to successful payment, strengthening PTP follow-through, and using DPD- and exposure-aware treatment strategies while preserving data-quality transparency.

## Appendix: Project Outputs

The analysis produces the following major report groups:

- dataset inventory
- schema and relationship analysis
- duplicate analysis
- identity resolution
- temporal consistency
- missing identifier analysis
- cleaned-layer validation
- recovery summary
- channel performance
- risk performance
- DPD performance
- payment-method performance
- contact-to-payment funnel
- cleaning decisions
- final recovery findings

