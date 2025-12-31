-- ============================================================================
-- Mesa 24/7 Backend Challenge - SQL Queries
-- ============================================================================
-- Author: Jordy Dev Villanueva
-- Description: Raw SQL queries demonstrating SQL proficiency beyond ORM
-- ============================================================================

-- ============================================================================
-- QUERY 1: All Restaurant Balances (Aggregation)
-- ============================================================================
-- Description: Calculate available balance for all restaurants in a given currency
-- Returns: restaurant_id, available_balance, last_event_at
-- Use case: Dashboard showing all restaurant balances
-- ============================================================================

SELECT
    l.restaurant_id,
    l.currency,
    COALESCE(SUM(l.amount), 0) AS available_balance,
    MAX(l.created_at) AS last_event_at,
    COUNT(l.id) AS total_transactions
FROM
    ledger_entries l
WHERE
    l.currency = 'PEN'  -- Parameter: currency code
GROUP BY
    l.restaurant_id, l.currency
HAVING
    COALESCE(SUM(l.amount), 0) > 0  -- Only show restaurants with positive balance
ORDER BY
    available_balance DESC;

-- Example output:
-- restaurant_id | currency | available_balance | last_event_at | total_transactions
-- res_003       | PEN      | 85000            | 2025-12-30    | 42
-- res_001       | PEN      | 72000            | 2025-12-30    | 38


-- ============================================================================
-- QUERY 2: Top 10 Restaurants by Net Revenue (Last 7 Days)
-- ============================================================================
-- Description: Calculate net revenue (charges - fees - refunds) for last 7 days
-- Returns: restaurant_id, net_amount, charge_count, refund_count, fee_total
-- Use case: Performance report for recent activity
-- Definition: Net = SUM(CHARGE) + SUM(FEE) + SUM(REFUND)
--             (FEE and REFUND are already negative in ledger)
-- ============================================================================

WITH date_filtered_entries AS (
    SELECT
        restaurant_id,
        entry_type,
        amount,
        created_at
    FROM
        ledger_entries
    WHERE
        created_at >= CURRENT_DATE - INTERVAL '7 days'
        AND currency = 'PEN'
),
restaurant_stats AS (
    SELECT
        restaurant_id,
        SUM(amount) AS net_amount,
        COUNT(CASE WHEN entry_type = 'charge' THEN 1 END) AS charge_count,
        COUNT(CASE WHEN entry_type = 'refund' THEN 1 END) AS refund_count,
        ABS(SUM(CASE WHEN entry_type = 'fee' THEN amount ELSE 0 END)) AS fee_total,
        SUM(CASE WHEN entry_type = 'charge' THEN amount ELSE 0 END) AS gross_sales
    FROM
        date_filtered_entries
    GROUP BY
        restaurant_id
)
SELECT
    restaurant_id,
    net_amount,
    gross_sales,
    fee_total,
    charge_count,
    refund_count,
    ROUND((net_amount::NUMERIC / NULLIF(gross_sales, 0) * 100), 2) AS net_margin_pct
FROM
    restaurant_stats
WHERE
    net_amount > 0
ORDER BY
    net_amount DESC
LIMIT 10;

-- Example output:
-- restaurant_id | net_amount | gross_sales | fee_total | charge_count | refund_count | net_margin_pct
-- res_003       | 45500      | 50000       | 2500      | 15           | 1            | 91.00
-- res_001       | 38200      | 42000       | 2100      | 12           | 2            | 90.95


-- ============================================================================
-- QUERY 3: Payout Eligibility (Filter + Anti-Join)
-- ============================================================================
-- Description: Find restaurants eligible for payout that don't have existing payout
-- Returns: restaurant_id, available_balance, eligible_for_payout
-- Use case: Batch payout generation query
-- Requirements:
--   - available_balance >= min_amount (e.g., 5000 cents = $50)
--   - NO existing payout for specified as_of_date
-- ============================================================================

WITH restaurant_balances AS (
    SELECT
        restaurant_id,
        currency,
        SUM(amount) AS available_balance
    FROM
        ledger_entries
    WHERE
        currency = 'PEN'  -- Parameter: currency
    GROUP BY
        restaurant_id, currency
),
existing_payouts AS (
    SELECT DISTINCT
        restaurant_id,
        currency
    FROM
        payouts
    WHERE
        as_of_date = '2025-12-30'  -- Parameter: as_of_date
        AND currency = 'PEN'  -- Parameter: currency
)
SELECT
    rb.restaurant_id,
    rb.currency,
    rb.available_balance,
    rb.available_balance >= 5000 AS meets_minimum,  -- Parameter: min_amount
    ep.restaurant_id IS NULL AS no_existing_payout,
    CASE
        WHEN rb.available_balance >= 5000 AND ep.restaurant_id IS NULL
        THEN 'ELIGIBLE'
        ELSE 'NOT_ELIGIBLE'
    END AS eligibility_status
FROM
    restaurant_balances rb
LEFT JOIN
    existing_payouts ep
    ON rb.restaurant_id = ep.restaurant_id
    AND rb.currency = ep.currency
WHERE
    rb.available_balance >= 5000  -- Only show restaurants with sufficient balance
ORDER BY
    rb.available_balance DESC;

-- Example output:
-- restaurant_id | currency | available_balance | meets_minimum | no_existing_payout | eligibility_status
-- res_003       | PEN      | 85000            | true          | true               | ELIGIBLE
-- res_001       | PEN      | 72000            | true          | false              | NOT_ELIGIBLE


-- ============================================================================
-- QUERY 4: Data Integrity Check (Anomaly Detection)
-- ============================================================================
-- Description: Comprehensive data integrity checks across all tables
-- Returns: check_type, entity_id, issue_description, severity
-- Use case: Daily data quality monitoring and alerting
-- Checks:
--   1. Payouts with amount <= 0
--   2. Ledger entries with orphaned references
--   3. Duplicate processor events (should be impossible with unique constraint)
--   4. Restaurants with negative balance
--   5. Payouts without corresponding reserve entries
-- ============================================================================

-- Check 1: Payouts with invalid amounts
SELECT
    'INVALID_PAYOUT_AMOUNT' AS check_type,
    payout_id AS entity_id,
    'Payout amount is <= 0' AS issue_description,
    'HIGH' AS severity,
    amount AS detail_value
FROM
    payouts
WHERE
    amount <= 0

UNION ALL

-- Check 2: Negative restaurant balances (shouldn't happen in production)
SELECT
    'NEGATIVE_BALANCE' AS check_type,
    restaurant_id AS entity_id,
    'Restaurant has negative balance' AS issue_description,
    'CRITICAL' AS severity,
    SUM(amount) AS detail_value
FROM
    ledger_entries
GROUP BY
    restaurant_id, currency
HAVING
    SUM(amount) < 0

UNION ALL

-- Check 3: Duplicate event IDs (should be caught by unique constraint)
SELECT
    'DUPLICATE_EVENT_ID' AS check_type,
    event_id AS entity_id,
    'Multiple processor events with same event_id' AS issue_description,
    'CRITICAL' AS severity,
    COUNT(*) AS detail_value
FROM
    processor_events
GROUP BY
    event_id
HAVING
    COUNT(*) > 1

UNION ALL

-- Check 4: Orphaned ledger entries (reference non-existent processor events)
SELECT
    'ORPHANED_LEDGER_ENTRY' AS check_type,
    l.id::TEXT AS entity_id,
    'Ledger entry references non-existent processor event' AS issue_description,
    'MEDIUM' AS severity,
    NULL AS detail_value
FROM
    ledger_entries l
WHERE
    l.reference_type = 'processor_event'
    AND NOT EXISTS (
        SELECT 1
        FROM processor_events pe
        WHERE pe.event_id = l.reference_id
    )
LIMIT 100  -- Limit to avoid huge result set

UNION ALL

-- Check 5: Payouts without corresponding PAYOUT_RESERVE ledger entry
SELECT
    'MISSING_PAYOUT_RESERVE' AS check_type,
    p.payout_id AS entity_id,
    'Payout created but no PAYOUT_RESERVE ledger entry found' AS issue_description,
    'HIGH' AS severity,
    p.amount AS detail_value
FROM
    payouts p
WHERE
    p.status = 'created'
    AND NOT EXISTS (
        SELECT 1
        FROM ledger_entries l
        WHERE l.reference_type = 'payout'
          AND l.reference_id = p.payout_id
          AND l.entry_type = 'payout_reserve'
    )

ORDER BY
    severity DESC, check_type;

-- Example output (no issues):
-- check_type | entity_id | issue_description | severity | detail_value
-- (empty result set = all checks passed)

-- Example output (with issues):
-- check_type           | entity_id  | issue_description                    | severity  | detail_value
-- NEGATIVE_BALANCE     | res_999    | Restaurant has negative balance      | CRITICAL  | -5000
-- DUPLICATE_EVENT_ID   | evt_123    | Multiple events with same ID         | CRITICAL  | 2


-- ============================================================================
-- BONUS QUERY: Payout History with Items Breakdown
-- ============================================================================
-- Description: Get detailed payout history with line item breakdown
-- Returns: Complete payout information including all calculation items
-- Use case: Payout reconciliation and audit trail
-- ============================================================================

SELECT
    p.payout_id,
    p.restaurant_id,
    p.currency,
    p.amount AS total_amount,
    p.status,
    p.as_of_date,
    p.created_at,
    p.paid_at,
    json_agg(
        json_build_object(
            'item_type', pi.item_type,
            'amount', pi.amount
        ) ORDER BY pi.created_at
    ) AS breakdown_items
FROM
    payouts p
LEFT JOIN
    payout_items pi ON p.id = pi.payout_id
WHERE
    p.restaurant_id = 'res_001'  -- Parameter: restaurant_id
    AND p.currency = 'PEN'  -- Parameter: currency
GROUP BY
    p.id, p.payout_id, p.restaurant_id, p.currency, p.amount,
    p.status, p.as_of_date, p.created_at, p.paid_at
ORDER BY
    p.as_of_date DESC, p.created_at DESC
LIMIT 20;

-- Example output:
-- payout_id | restaurant_id | currency | total_amount | status | as_of_date | breakdown_items
-- po_abc123 | res_001       | PEN      | 45000       | paid   | 2025-12-30 | [{"item_type":"gross_sales","amount":50000},{"item_type":"fees","amount":-5000}]
