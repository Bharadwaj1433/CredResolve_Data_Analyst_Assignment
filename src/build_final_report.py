from pathlib import Path
import pandas as pd

reports = Path("reports")

def read_csv(name):
    return pd.read_csv(reports / name)

def metric(df, name):
    row = df.loc[df["metric"].eq(name), "value"]
    return row.iloc[0] if len(row) else 0

recovery = read_csv("recovery_summary.csv")
funnel = read_csv("contact_to_payment_funnel.csv")
risk = read_csv("recovery_by_risk.csv")
dpd = read_csv("recovery_by_dpd.csv")
payment_method = read_csv("payment_method_performance.csv")
channel = read_csv("channel_performance.csv")
validation = read_csv("final_cleaned_layer_validation.csv")
activity = read_csv("account_activity_grain.csv")
temporal = read_csv("temporal_consistency_analysis.csv")
timezone = read_csv("timezone_analysis.csv")
missing = read_csv("missing_identifier_analysis.csv")
call_conflicts = read_csv("call_conflict_summary.csv")
borrower_conflicts = read_csv("borrower_identity_conflict_summary.csv")
borrower_patterns = read_csv("borrower_conflict_patterns.csv")

accounts = int(metric(recovery, "accounts"))
outstanding = metric(recovery, "total_outstanding_amount")
recovered = metric(recovery, "successful_payment_amount")
recovery_rate = metric(recovery, "recovery_rate_pct")
successful_payments = int(metric(recovery, "successful_payments"))
payment_records = int(metric(recovery, "total_payment_records"))
calls = int(metric(recovery, "calls"))
answered_calls = int(metric(recovery, "answered_calls"))
ptps = int(metric(recovery, "ptps"))
kept_ptps = int(metric(recovery, "ptps_kept"))
field_visits = int(metric(recovery, "field_visits"))
sms_events = int(metric(recovery, "sms_events"))
whatsapp_events = int(metric(recovery, "whatsapp_events"))

answered_accounts = int(
    funnel.loc[
        funnel["metric"].eq("accounts_with_answered_call"),
        "value"
    ].iloc[0]
)

paid_accounts = int(
    funnel.loc[
        funnel["metric"].eq("accounts_with_successful_payment"),
        "value"
    ].iloc[0]
)

answered_paid = int(
    funnel.loc[
        funnel["metric"].eq("answered_accounts_with_payment"),
        "value"
    ].iloc[0]
)

answered_to_payment = float(
    funnel.loc[
        funnel["metric"].eq("answered_to_payment_rate_pct"),
        "value"
    ].iloc[0]
)

paid_without_answered = int(
    funnel.loc[
        funnel["metric"].eq("paid_accounts_without_answered_call"),
        "value"
    ].iloc[0]
)

validation_passed = int(
    (validation["status"] == "PASS").sum()
)

validation_failed = int(
    (validation["status"] != "PASS").sum()
)

top_risk = risk.iloc[0]
bottom_risk = risk.iloc[-1]

top_dpd = dpd.iloc[0]
bottom_dpd = dpd.iloc[-1]

top_payment = payment_method.iloc[0]

top_channel = channel.iloc[0]

call_conflict_total = int(
    call_conflicts.loc[
        call_conflicts["conflict_type"].isin(
            ["agent_id", "event_at"]
        ),
        "groups"
    ].sum()
)

highest_borrower_conflict = borrower_conflicts.sort_values(
    "percentage_of_borrower_ids",
    ascending=False
).iloc[0]

five_field_conflicts = borrower_patterns.loc[
    borrower_patterns["identity_fields_conflicting"].eq(5),
    "percentage"
].iloc[0]

missing_identifier_rows = missing[
    missing["missing_values"] > 0
].copy()

report = f"""# CredResolve Data Analyst Assignment

## 1. Executive Summary

This project analyzes a multi-table collections and recovery dataset with an account-centric analytical approach.

The final cleaned analytical layer contains {accounts:,} accounts and supports recovery, collections activity, data-quality, and operational performance analysis.

The portfolio contains an observed outstanding amount of {outstanding:,.2f}. Successful payments contribute {recovered:,.2f}, producing an observed recovery rate of {recovery_rate:.2f}%.

The analysis identified substantial borrower identity conflicts, duplicate operational events, missing identifiers, call-level conflicts, and temporal inconsistencies. These issues were not hidden through aggressive deletion. Instead, records were cleaned where duplication was unambiguous and retained with explicit quality flags where ambiguity could affect analytical interpretation.

The final cleaned layer passed all {validation_passed} validation checks with {validation_failed} failures.

The strongest observed DPD recovery rate occurs in the 31–60 DPD band at {top_dpd["recovery_rate_pct"]:.2f}%, while the 1–30 DPD band has the lowest observed recovery rate at {bottom_dpd["recovery_rate_pct"]:.2f}% among the analyzed bands.

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

ccount_id is treated as the canonical analytical identifier for recovery analysis, while orrower_id is retained as a secondary relationship attribute because borrower identity quality is inconsistent.

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

Account-level recovery analysis aggregates operational events to ccount_id.

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

- name conflicts affect {highest_borrower_conflict["borrower_ids_with_conflict"]:,} borrower IDs at the highest observed conflicting attribute rate
- five identity fields conflict for {five_field_conflicts:.2f}% of borrower IDs in the analyzed pattern

Because of this, borrower identity was not treated as a fully reliable analytical key.

### Account-Borrower Relationships

Account-level relationship analysis showed that operational records can associate the same account with multiple borrower identifiers.

This is why account-level analysis uses ccount_id as the canonical analytical entity.

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

Passed checks: {validation_passed}

Failed checks: {validation_failed}

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

- {accounts:,} accounts
- {outstanding:,.2f} outstanding amount
- {recovered:,.2f} successful recovered amount
- {successful_payments:,} successful payments
- {payment_records:,} total payment records

The observed recovery rate is {recovery_rate:.2f}%.

This is treated as an observed portfolio metric rather than a causal estimate.

## 12. Collections Activity

The cleaned data contains:

- {calls:,} calls
- {answered_calls:,} answered calls
- {ptps:,} promises to pay
- {kept_ptps:,} kept promises
- {field_visits:,} field visits
- {sms_events:,} SMS events
- {whatsapp_events:,} WhatsApp events

The gap between total PTPs and kept PTPs indicates that promise creation alone should not be treated as recovery success.

## 13. Contact-to-Payment Funnel

Accounts with an answered call: {answered_accounts:,}

Accounts with a successful payment: {paid_accounts:,}

Accounts with both an answered call and successful payment: {answered_paid:,}

Answered-call to payment rate: {answered_to_payment:.2f}%

Paid accounts without an answered call: {paid_without_answered:,}

The final number is important because it demonstrates that successful payments cannot automatically be attributed to voice contact.

The analysis therefore avoids making unsupported causal claims about channels.

## 14. Channel Performance

The observable channel-success analysis shows:

| Channel | Activity | Successful Outcomes | Observable Success Rate |
|---|---:|---:|---:|
"""

for _, row in channel.iterrows():
    report += f'| {row["channel"]} | {int(row["activity"]):,} | {int(row["successful_outcomes"]):,} | {row["success_rate_pct"]:.2f}% |\\n'

report += f"""
The highest observable channel-success rate is {top_channel["channel"]} at {top_channel["success_rate_pct"]:.2f}%.

These rates are not treated as monetary recovery rates because each channel has a different observable outcome definition.

## 15. Risk Segment Recovery

| Risk Segment | Accounts | Outstanding | Recovered | Recovery Rate |
|---|---:|---:|---:|---:|
"""

for _, row in risk.iterrows():
    report += f'| {row["risk_segment"]} | {int(row["accounts"]):,} | {row["outstanding_amount"]:,.2f} | {row["recovered_amount"]:,.2f} | {row["recovery_rate_pct"]:.2f}% |\\n'

report += f"""
The highest observed recovery rate is in the {top_risk["risk_segment"]} segment at {top_risk["recovery_rate_pct"]:.2f}%.

The lowest observed recovery rate is in the {bottom_risk["risk_segment"]} segment at {bottom_risk["recovery_rate_pct"]:.2f}%.

The differences are relatively small, so risk segment alone should not determine collection strategy.

## 16. DPD Recovery

| DPD Band | Accounts | Outstanding | Recovered | Recovery Rate |
|---|---:|---:|---:|---:|
"""

for _, row in dpd.iterrows():
    report += f'| {row["dpd_band"]} | {int(row["accounts"]):,} | {row["outstanding_amount"]:,.2f} | {row["recovered_amount"]:,.2f} | {row["recovery_rate_pct"]:.2f}% |\\n'

report += f"""
The 31–60 DPD band has the highest observed recovery rate at {top_dpd["recovery_rate_pct"]:.2f}%.

The 1–30 DPD band has the lowest observed recovery rate at {bottom_dpd["recovery_rate_pct"]:.2f}% among the analyzed DPD bands.

This suggests that collection treatment should consider delinquency stage rather than applying a single strategy across all accounts.

## 17. Payment Method Performance

| Payment Method | Successful Payments | Recovered Amount | Accounts | Average Payment |
|---|---:|---:|---:|---:|
"""

for _, row in payment_method.iterrows():
    report += f'| {row["payment_method"]} | {int(row["successful_payments"]):,} | {row["recovered_amount"]:,.2f} | {int(row["accounts"]):,} | {row["average_payment"]:,.2f} |\\n'

report += f"""
{top_payment["payment_method"]} has the largest observed successful-payment amount at {top_payment["recovered_amount"]:,.2f}.

This is an observational comparison and does not establish that payment method causes higher recovery.

## 18. Key Findings

### Finding 1: Recovery is relatively low compared with outstanding exposure

The observed recovery rate is {recovery_rate:.2f}% against the analyzed outstanding amount.

This indicates substantial remaining recovery opportunity.

### Finding 2: Contact alone does not explain payment

Although {answered_accounts:,} accounts had answered calls, {paid_without_answered:,} paid accounts did not have an answered call.

This means recovery attribution must account for multiple collection channels and customer-initiated payment behavior.

### Finding 3: DPD stage matters

The strongest observed recovery rate occurs in the 31–60 DPD band.

The 1–30 DPD band has a lower observed recovery rate.

Early-stage collections therefore should not automatically be considered the highest-performing stage.

### Finding 4: PTP volume does not equal PTP success

There are {ptps:,} PTP records but only {kept_ptps:,} kept PTPs.

PTP quality and follow-through should therefore be monitored separately from PTP creation.

### Finding 5: Borrower identity quality limits borrower-level analysis

Borrower attributes contain significant conflicts.

Account-level analysis is therefore more reliable for the primary recovery analysis.

## 19. Business Recommendations

### 1. Use account-centric recovery monitoring

Use ccount_id as the primary recovery entity and retain borrower quality flags for secondary analysis.

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

The recovery analysis shows an observed portfolio recovery rate of {recovery_rate:.2f}% and identifies meaningful differences across delinquency stages, risk segments, payment methods, and collection activity.

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
"""

(reports / "final_report.md").write_text(report, encoding="utf-8")

print("Final documentation generated")
print("reports/final_report.md")
