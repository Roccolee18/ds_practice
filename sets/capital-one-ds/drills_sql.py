"""
Reference solutions for the graduated SQL drill bank (D01-D18).

Each drill targets ONE pattern and builds on the one before it. D18 is the same
gaps-and-islands pattern as S5 in the timed exam -- by the time you reach it you
should have every piece already.
"""
import os
import sqlite3
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# (id, pattern, minutes, sql)
DRILLS = [

("D01", "SELECT / WHERE / ORDER BY / LIMIT", 2, """
SELECT account_id, product, credit_limit
FROM accounts
WHERE product = 'Venture' AND credit_limit >= 2600
ORDER BY credit_limit DESC, account_id ASC
LIMIT 10
"""),

("D02", "COUNT / AVG with GROUP BY", 3, """
SELECT product,
       COUNT(*) AS n_accounts,
       ROUND(AVG(credit_limit), 2) AS avg_limit,
       ROUND(AVG(apr), 2) AS avg_apr
FROM accounts
GROUP BY product
ORDER BY n_accounts DESC
"""),

("D03", "GROUP BY + HAVING", 3, """
SELECT state, COUNT(*) AS n_customers
FROM customers
GROUP BY state
HAVING COUNT(*) >= 250
ORDER BY n_customers DESC, state ASC
"""),

("D04", "integer division -- the 1.0 * trap", 4, """
SELECT segment,
       COUNT(*) AS n_customers,
       SUM(CASE WHEN annual_income IS NULL THEN 1 ELSE 0 END) AS n_missing_income,
       ROUND(1.0 * SUM(CASE WHEN annual_income IS NULL THEN 1 ELSE 0 END)
             / COUNT(*), 4) AS pct_missing
FROM customers
GROUP BY segment
ORDER BY pct_missing DESC, segment ASC
"""),

("D05", "two-table JOIN + GROUP BY", 4, """
SELECT c.segment,
       COUNT(*) AS n_accounts,
       ROUND(AVG(a.credit_limit), 2) AS avg_limit
FROM accounts a
JOIN customers c ON c.customer_id = a.customer_id
GROUP BY c.segment
ORDER BY avg_limit DESC
"""),

("D06", "three-table JOIN", 5, """
SELECT c.segment,
       t.channel,
       COUNT(*) AS n_txns,
       ROUND(SUM(t.amount), 2) AS total_amount
FROM transactions t
JOIN accounts  a ON a.account_id  = t.account_id
JOIN customers c ON c.customer_id = a.customer_id
WHERE t.amount > 0
GROUP BY c.segment, t.channel
ORDER BY c.segment ASC, t.channel ASC
"""),

("D07", "LEFT JOIN + IS NULL (anti-join)", 6, """
SELECT c.segment, COUNT(*) AS n_never_delinquent
FROM customers c
LEFT JOIN (
    SELECT DISTINCT a.customer_id
    FROM accounts a
    JOIN statements s ON s.account_id = a.account_id
    WHERE s.days_past_due > 0
) d ON d.customer_id = c.customer_id
WHERE d.customer_id IS NULL
GROUP BY c.segment
ORDER BY n_never_delinquent DESC, c.segment ASC
"""),

("D08", "conditional aggregation with CASE WHEN", 5, """
SELECT a.product,
       COUNT(*) AS n_accounts,
       SUM(CASE WHEN a.status = 'open'        THEN 1 ELSE 0 END) AS n_open,
       SUM(CASE WHEN a.status = 'closed'      THEN 1 ELSE 0 END) AS n_closed,
       SUM(CASE WHEN a.status = 'charged_off' THEN 1 ELSE 0 END) AS n_charged_off
FROM accounts a
GROUP BY a.product
ORDER BY a.product ASC
"""),

("D09", "date handling with strftime", 4, """
SELECT strftime('%Y-%m', txn_ts) AS month,
       COUNT(*) AS n_txns,
       ROUND(SUM(amount), 2) AS total_amount
FROM transactions
WHERE amount > 0
GROUP BY 1
ORDER BY 1
"""),

("D10", "COUNT(DISTINCT ...)", 4, """
SELECT merchant_category,
       COUNT(*) AS n_txns,
       COUNT(DISTINCT account_id) AS n_accounts,
       COUNT(DISTINCT merchant_id) AS n_merchants
FROM transactions
WHERE amount > 0 AND merchant_category IS NOT NULL
GROUP BY merchant_category
ORDER BY n_txns DESC, merchant_category ASC
"""),

("D11", "subquery in WHERE", 5, """
SELECT segment, COUNT(*) AS n_customers
FROM customers
WHERE credit_score_at_signup > (SELECT AVG(credit_score_at_signup) FROM customers)
GROUP BY segment
ORDER BY n_customers DESC, segment ASC
"""),

("D12", "CTE (WITH ...)", 5, """
WITH acct_spend AS (
    SELECT account_id, SUM(amount) AS spend
    FROM transactions
    WHERE amount > 0
    GROUP BY account_id
)
SELECT a.product,
       COUNT(*) AS n_accounts,
       ROUND(AVG(s.spend), 2) AS avg_spend
FROM acct_spend s
JOIN accounts a ON a.account_id = s.account_id
GROUP BY a.product
ORDER BY avg_spend DESC
"""),

("D13", "ROW_NUMBER -- top N per group", 7, """
WITH ranked AS (
    SELECT a.product,
           a.account_id,
           a.credit_limit,
           ROW_NUMBER() OVER (PARTITION BY a.product
                              ORDER BY a.credit_limit DESC, a.account_id ASC) AS rn
    FROM accounts a
)
SELECT product, account_id, credit_limit, rn
FROM ranked
WHERE rn <= 3
ORDER BY product ASC, rn ASC
"""),

("D14", "RANK vs ROW_NUMBER on ties", 6, """
WITH by_state AS (
    SELECT state, COUNT(*) AS n_customers
    FROM customers
    GROUP BY state
)
SELECT state,
       n_customers,
       ROW_NUMBER() OVER (ORDER BY n_customers DESC, state ASC) AS row_num,
       RANK()       OVER (ORDER BY n_customers DESC)            AS rnk,
       DENSE_RANK() OVER (ORDER BY n_customers DESC)            AS dense_rnk
FROM by_state
ORDER BY n_customers DESC, state ASC
"""),

("D15", "LAG -- period over period", 7, """
WITH monthly AS (
    SELECT strftime('%Y-%m', statement_month) AS month,
           COUNT(*) AS n_statements,
           ROUND(SUM(payment_made), 2) AS total_paid
    FROM statements
    GROUP BY 1
)
SELECT month,
       total_paid,
       LAG(total_paid) OVER (ORDER BY month) AS prev_paid,
       ROUND(total_paid - LAG(total_paid) OVER (ORDER BY month), 2) AS change
FROM monthly
ORDER BY month
"""),

("D16", "LEAD with a next-period guard", 8, """
WITH nxt AS (
    SELECT account_id,
           statement_month,
           days_past_due,
           LEAD(days_past_due)   OVER (PARTITION BY account_id ORDER BY statement_month) AS next_dpd,
           LEAD(statement_month) OVER (PARTITION BY account_id ORDER BY statement_month) AS next_month
    FROM statements
)
SELECT strftime('%Y-%m', statement_month) AS month,
       COUNT(*) AS n_current,
       SUM(CASE WHEN next_month = date(statement_month, '+1 month')
                 AND next_dpd = 0 THEN 1 ELSE 0 END) AS n_cured
FROM nxt
WHERE days_past_due > 0
  AND statement_month < '2025-12-01'
GROUP BY 1
ORDER BY 1
"""),

("D17", "running total with a window frame", 7, """
WITH monthly AS (
    SELECT strftime('%Y-%m', txn_ts) AS month,
           ROUND(SUM(amount), 2) AS spend
    FROM transactions
    WHERE amount > 0
    GROUP BY 1
)
SELECT month,
       spend,
       ROUND(SUM(spend) OVER (ORDER BY month
                              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total
FROM monthly
ORDER BY month
"""),

("D18", "gaps and islands -- consecutive streaks", 10, """
WITH active AS (
    SELECT DISTINCT account_id, strftime('%Y-%m-01', txn_ts) AS month
    FROM transactions
    WHERE amount > 0
),
numbered AS (
    SELECT account_id,
           month,
           ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY month) AS rn
    FROM active
),
islands AS (
    SELECT account_id,
           date(month, '-' || rn || ' months') AS island,
           COUNT(*) AS streak
    FROM numbered
    GROUP BY account_id, island
)
SELECT streak AS longest_streak, COUNT(*) AS n_accounts
FROM (
    SELECT account_id, MAX(streak) AS streak
    FROM islands
    GROUP BY account_id
)
GROUP BY streak
ORDER BY longest_streak ASC
"""),
]

SQL = {d[0]: d[3] for d in DRILLS}
META = {d[0]: {"pattern": d[1], "minutes": d[2]} for d in DRILLS}


def run(key):
    con = sqlite3.connect(f"{DATA}/warehouse.db")
    try:
        return pd.read_sql_query(SQL[key], con)
    finally:
        con.close()


if __name__ == "__main__":
    total = 0
    for k, meta in META.items():
        d = run(k)
        total += meta["minutes"]
        print(f"{k}  {meta['minutes']:>2}m  {str(d.shape):>10}  {meta['pattern']}")
        if d.shape[0] > 30:
            print(f"      !! {d.shape[0]} rows -- too big for a drill")
    print(f"\ntotal drill time: {total} min")
