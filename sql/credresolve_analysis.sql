PRAGMA threads=4;

CREATE OR REPLACE VIEW golden_accounts AS
SELECT * FROM read_csv_auto('data/golden/accounts.csv', HEADER=TRUE);

CREATE OR REPLACE VIEW golden_payments AS
SELECT * FROM read_csv_auto('data/golden/payments.csv', HEADER=TRUE);

CREATE OR REPLACE VIEW golden_campaigns AS
SELECT * FROM read_csv_auto('data/golden/campaigns.csv', HEADER=TRUE);

CREATE OR REPLACE VIEW golden_calls AS
SELECT
    c.*,
    ca.campaign_name,
    ca.channel,
    ca.strategy_version
FROM read_csv_auto('data/golden/calls.csv', HEADER=TRUE) c
LEFT JOIN golden_campaigns ca
    ON c.campaign_id = ca.campaign_id;

CREATE OR REPLACE VIEW golden_ptps AS
SELECT * FROM read_csv_auto('data/golden/promises_to_pay.csv', HEADER=TRUE);

CREATE OR REPLACE VIEW golden_account_recovery AS
SELECT
    a.account_id,
    a.loan_type,
    a.outstanding_amount,
    a.dpd,
    CASE
        WHEN a.dpd = 0 THEN '0'
        WHEN a.dpd BETWEEN 1 AND 30 THEN '1-30'
        WHEN a.dpd BETWEEN 31 AND 60 THEN '31-60'
        WHEN a.dpd BETWEEN 61 AND 90 THEN '61-90'
        WHEN a.dpd BETWEEN 91 AND 180 THEN '91-180'
        ELSE '181+'
    END AS dpd_band,
    a.risk_segment,
    a.status,
    COALESCE(SUM(
        CASE
            WHEN UPPER(p.payment_status) = 'SUCCESS'
            THEN p.amount
            ELSE 0
        END
    ), 0) AS recovered_amount,
    COUNT(
        CASE
            WHEN UPPER(p.payment_status) = 'SUCCESS'
            THEN p.payment_id
        END
    ) AS successful_payments
FROM golden_accounts a
LEFT JOIN golden_payments p
    ON a.account_id = p.account_id
GROUP BY
    a.account_id,
    a.loan_type,
    a.outstanding_amount,
    a.dpd,
    a.risk_segment,
    a.status;

SELECT
    COUNT(*) AS accounts,
    SUM(outstanding_amount) AS outstanding_amount,
    SUM(recovered_amount) AS recovered_amount,
    SUM(recovered_amount)
        / NULLIF(SUM(outstanding_amount), 0) * 100
        AS recovery_rate_pct
FROM golden_account_recovery;

SELECT
    risk_segment,
    COUNT(*) AS accounts,
    SUM(outstanding_amount) AS outstanding_amount,
    SUM(recovered_amount) AS recovered_amount,
    SUM(recovered_amount)
        / NULLIF(SUM(outstanding_amount), 0) * 100
        AS recovery_rate_pct
FROM golden_account_recovery
GROUP BY risk_segment
ORDER BY recovery_rate_pct DESC;

SELECT
    dpd_band,
    COUNT(*) AS accounts,
    SUM(outstanding_amount) AS outstanding_amount,
    SUM(recovered_amount) AS recovered_amount,
    SUM(recovered_amount)
        / NULLIF(SUM(outstanding_amount), 0) * 100
        AS recovery_rate_pct
FROM golden_account_recovery
GROUP BY dpd_band
ORDER BY recovery_rate_pct DESC;

SELECT
    status,
    COUNT(*) AS accounts,
    SUM(outstanding_amount) AS outstanding_amount,
    SUM(recovered_amount) AS recovered_amount,
    SUM(recovered_amount)
        / NULLIF(SUM(outstanding_amount), 0) * 100
        AS recovery_rate_pct
FROM golden_account_recovery
GROUP BY status
ORDER BY recovery_rate_pct DESC;

SELECT
    loan_type,
    COUNT(*) AS accounts,
    SUM(outstanding_amount) AS outstanding_amount,
    SUM(recovered_amount) AS recovered_amount,
    SUM(recovered_amount)
        / NULLIF(SUM(outstanding_amount), 0) * 100
        AS recovery_rate_pct
FROM golden_account_recovery
GROUP BY loan_type
ORDER BY recovery_rate_pct DESC;

SELECT
    DATE_TRUNC(
        'month',
        TRY_CAST(event_at AS TIMESTAMP)
    ) AS month,
    COUNT(*) AS calls,
    COUNT(DISTINCT account_id) AS unique_call_accounts,
    COUNT(
        DISTINCT CASE
            WHEN UPPER(call_status)
                IN ('ANSWERED','CONNECTED','SUCCESS')
            THEN account_id
        END
    ) AS answered_accounts
FROM golden_calls
GROUP BY 1
ORDER BY 1;

SELECT
    channel,
    COUNT(*) AS activity,
    COUNT(
        CASE
            WHEN UPPER(call_status)
                IN ('ANSWERED','CONNECTED','SUCCESS')
            THEN 1
        END
    ) AS answered_calls,
    COUNT(
        CASE
            WHEN UPPER(call_status)
                IN ('ANSWERED','CONNECTED','SUCCESS')
            THEN 1
        END
    ) * 100.0 / NULLIF(COUNT(*), 0)
        AS answer_rate_pct
FROM golden_calls
GROUP BY channel
ORDER BY answer_rate_pct DESC;

SELECT
    campaign_id,
    campaign_name,
    channel,
    strategy_version,
    COUNT(*) AS call_volume,
    COUNT(
        CASE
            WHEN UPPER(call_status)
                IN ('ANSWERED','CONNECTED','SUCCESS')
            THEN 1
        END
    ) AS answered_calls,
    COUNT(
        CASE
            WHEN UPPER(call_status)
                IN ('ANSWERED','CONNECTED','SUCCESS')
            THEN 1
        END
    ) * 100.0 / NULLIF(COUNT(*), 0)
        AS answer_rate_pct
FROM golden_calls
GROUP BY
    campaign_id,
    campaign_name,
    channel,
    strategy_version
ORDER BY answer_rate_pct DESC;

SELECT
    account_id,
    COUNT(*) AS successful_payments,
    SUM(amount) AS recovered_amount
FROM golden_payments
WHERE UPPER(payment_status) = 'SUCCESS'
GROUP BY account_id
ORDER BY recovered_amount DESC;

WITH answered_accounts AS (
    SELECT DISTINCT account_id
    FROM golden_calls
    WHERE UPPER(call_status)
        IN ('ANSWERED','CONNECTED','SUCCESS')
),
paying_accounts AS (
    SELECT DISTINCT account_id
    FROM golden_payments
    WHERE UPPER(payment_status) = 'SUCCESS'
)
SELECT
    COUNT(*) AS answered_accounts,
    COUNT(pa.account_id) AS answered_accounts_with_payment,
    COUNT(pa.account_id) * 100.0
        / NULLIF(COUNT(*), 0)
        AS answered_to_payment_rate_pct
FROM answered_accounts aa
LEFT JOIN paying_accounts pa
    ON aa.account_id = pa.account_id;

SELECT
    COUNT(*) AS ptps,
    COUNT(DISTINCT account_id) AS ptp_accounts
FROM golden_ptps;

SELECT
    agent_id,
    COUNT(*) AS calls,
    COUNT(DISTINCT account_id) AS unique_accounts,
    COUNT(
        CASE
            WHEN UPPER(call_status)
                IN ('ANSWERED','CONNECTED','SUCCESS')
            THEN 1
        END
    ) AS answered_calls
FROM golden_calls
GROUP BY agent_id
HAVING COUNT(*) >= 50
ORDER BY answered_calls DESC;

SELECT
    vendor_id,
    COUNT(*) AS calls,
    COUNT(DISTINCT agent_id) AS agents,
    COUNT(
        CASE
            WHEN UPPER(call_status)
                IN ('ANSWERED','CONNECTED','SUCCESS')
            THEN 1
        END
    ) AS answered_calls
FROM golden_calls
GROUP BY vendor_id
ORDER BY answered_calls DESC;

SELECT
    EXTRACT(
        HOUR FROM TRY_CAST(event_at AS TIMESTAMP)
    ) AS event_hour,
    COUNT(*) AS calls,
    COUNT(
        CASE
            WHEN UPPER(call_status)
                IN ('ANSWERED','CONNECTED','SUCCESS')
            THEN 1
        END
    ) AS answered_calls,
    COUNT(
        CASE
            WHEN UPPER(call_status)
                IN ('ANSWERED','CONNECTED','SUCCESS')
            THEN 1
        END
    ) * 100.0 / NULLIF(COUNT(*), 0)
        AS answer_rate_pct
FROM golden_calls
GROUP BY 1
ORDER BY 1;

WITH attempts AS (
    SELECT
        account_id,
        COUNT(*) AS attempt_count
    FROM golden_calls
    GROUP BY account_id
),
paying AS (
    SELECT DISTINCT account_id
    FROM golden_payments
    WHERE UPPER(payment_status) = 'SUCCESS'
)
SELECT
    CASE
        WHEN attempt_count = 1 THEN '1'
        WHEN attempt_count = 2 THEN '2'
        WHEN attempt_count = 3 THEN '3'
        WHEN attempt_count BETWEEN 4 AND 5 THEN '4-5'
        WHEN attempt_count BETWEEN 6 AND 10 THEN '6-10'
        ELSE '11+'
    END AS attempt_band,
    COUNT(*) AS accounts,
    COUNT(p.account_id) AS paying_accounts,
    COUNT(p.account_id) * 100.0
        / NULLIF(COUNT(*), 0)
        AS payment_account_rate_pct
FROM attempts a
LEFT JOIN paying p
    ON a.account_id = p.account_id
GROUP BY 1
ORDER BY
    CASE attempt_band
        WHEN '1' THEN 1
        WHEN '2' THEN 2
        WHEN '3' THEN 3
        WHEN '4-5' THEN 4
        WHEN '6-10' THEN 5
        ELSE 6
    END;

WITH answered_accounts AS (
    SELECT DISTINCT account_id
    FROM golden_calls
    WHERE UPPER(call_status)
        IN ('ANSWERED','CONNECTED','SUCCESS')
),
paying_accounts AS (
    SELECT DISTINCT account_id
    FROM golden_payments
    WHERE UPPER(payment_status) = 'SUCCESS'
)
SELECT
    CASE
        WHEN a.account_id IN (
            SELECT account_id
            FROM answered_accounts
        )
        THEN 'TREATMENT'
        ELSE 'CONTROL'
    END AS group_type,
    COUNT(*) AS accounts,
    COUNT(pa.account_id) AS paying_accounts,
    COUNT(pa.account_id) * 100.0
        / NULLIF(COUNT(*), 0)
        AS payment_rate_pct
FROM golden_accounts a
LEFT JOIN paying_accounts pa
    ON a.account_id = pa.account_id
GROUP BY 1;

SELECT
    COUNT(*) AS total_calls,
    COUNT(
        CASE
            WHEN COALESCE(call_id_conflict, FALSE)
            THEN 1
        END
    ) AS call_id_conflicts,
    COUNT(
        CASE
            WHEN COALESCE(agent_id_conflict, FALSE)
            THEN 1
        END
    ) AS agent_id_conflicts,
    COUNT(
        CASE
            WHEN COALESCE(event_at_conflict, FALSE)
            THEN 1
        END
    ) AS event_time_conflicts,
    COUNT(
        CASE
            WHEN COALESCE(agent_id_missing, FALSE)
            THEN 1
        END
    ) AS missing_agent_ids
FROM golden_calls;

SELECT
    COUNT(*) AS accounts,
    SUM(principal_amount) AS principal_amount,
    SUM(outstanding_amount) AS outstanding_amount,
    AVG(dpd) AS average_dpd
FROM golden_accounts;

SELECT
    'UNVERIFIED' AS reported_11_percent_improvement_status,
    'Historical eligible monthly balance denominator unavailable'
        AS primary_limitation;
