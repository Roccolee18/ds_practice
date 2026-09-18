# SQL drill solutions

Don't open this until you've attempted the drill.

For each one: read it once, then **break it** — delete a clause, predict what changes, run it, look.
Then close this file and write the query from memory. The notes below say what each drill is really
testing.

---

## D01 — SELECT / WHERE / ORDER BY / LIMIT

```sql
SELECT account_id, product, credit_limit
FROM accounts
WHERE product = 'Venture' AND credit_limit >= 2600
ORDER BY credit_limit DESC, account_id ASC
LIMIT 10
```

Returns **10 rows × 3 columns**.

Nothing hidden here. `LIMIT` runs *after* `ORDER BY`, so the sort decides which 10 you get. The second sort key makes the result deterministic — without it, ties could come back in any order and a grader would fail you intermittently.

---

## D02 — COUNT / AVG with GROUP BY

```sql
SELECT product,
       COUNT(*) AS n_accounts,
       ROUND(AVG(credit_limit), 2) AS avg_limit,
       ROUND(AVG(apr), 2) AS avg_apr
FROM accounts
GROUP BY product
ORDER BY n_accounts DESC
```

Returns **4 rows × 4 columns**.

`COUNT(*)` counts rows; `COUNT(col)` skips NULLs. They differ the moment a column has missing values, and interviewers ask. `ROUND(AVG(x), 2)` not `AVG(ROUND(x, 2))` — round the result, not the inputs.

---

## D03 — GROUP BY + HAVING

```sql
SELECT state, COUNT(*) AS n_customers
FROM customers
GROUP BY state
HAVING COUNT(*) >= 250
ORDER BY n_customers DESC, state ASC
```

Returns **5 rows × 2 columns**.

`WHERE` filters rows before grouping and cannot see `COUNT(*)`. `HAVING` filters groups after. Writing `WHERE COUNT(*) >= 250` is a hard error — worth triggering once so you recognize the message.

---

## D04 — integer division -- the 1.0 * trap

```sql
SELECT segment,
       COUNT(*) AS n_customers,
       SUM(CASE WHEN annual_income IS NULL THEN 1 ELSE 0 END) AS n_missing_income,
       ROUND(1.0 * SUM(CASE WHEN annual_income IS NULL THEN 1 ELSE 0 END)
             / COUNT(*), 4) AS pct_missing
FROM customers
GROUP BY segment
ORDER BY pct_missing DESC, segment ASC
```

Returns **4 rows × 4 columns**.

**The `1.0 *` is the whole drill.** `SUM(...)/COUNT(*)` is integer ÷ integer, which truncates to 0 in SQLite, Postgres and MySQL alike. `CAST(... AS REAL)` works too. Delete the `1.0 *` and watch every percentage collapse to zero — then you'll never forget it.

---

## D05 — two-table JOIN + GROUP BY

```sql
SELECT c.segment,
       COUNT(*) AS n_accounts,
       ROUND(AVG(a.credit_limit), 2) AS avg_limit
FROM accounts a
JOIN customers c ON c.customer_id = a.customer_id
GROUP BY c.segment
ORDER BY avg_limit DESC
```

Returns **4 rows × 3 columns**.

The grouping key lives on one table and the measure on another, so you must join before you can group. Note `COUNT(*)` here counts account rows because `accounts` is the left table and each account appears once.

---

## D06 — three-table JOIN

```sql
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
```

Returns **8 rows × 4 columns**.

Chain joins through the key that connects them: transactions → accounts (on `account_id`) → customers (on `customer_id`). There is no direct link from transactions to customers. Put the `amount > 0` filter in `WHERE` — it's a row filter, not a group filter.

---

## D07 — LEFT JOIN + IS NULL (anti-join)

```sql
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
```

Returns **4 rows × 2 columns**.

Two lessons. **Anti-join**: LEFT JOIN then `WHERE right.key IS NULL` keeps exactly the rows with no match. **Fan-out**: joining `statements` straight onto `customers` produces one row per statement, so `COUNT(*)` counts statements, not customers — collapse the right side to one row per customer with `SELECT DISTINCT` first. `NOT EXISTS` is an equally good spelling and often reads better.

---

## D08 — conditional aggregation with CASE WHEN

```sql
SELECT a.product,
       COUNT(*) AS n_accounts,
       SUM(CASE WHEN a.status = 'open'        THEN 1 ELSE 0 END) AS n_open,
       SUM(CASE WHEN a.status = 'closed'      THEN 1 ELSE 0 END) AS n_closed,
       SUM(CASE WHEN a.status = 'charged_off' THEN 1 ELSE 0 END) AS n_charged_off
FROM accounts a
GROUP BY a.product
ORDER BY a.product ASC
```

Returns **4 rows × 5 columns**.

`SUM(CASE WHEN cond THEN 1 ELSE 0 END)` pivots rows into columns. This is the most reusable aggregation idiom in SQL — conditional counts, conditional sums, rate numerators. `COUNT(*) FILTER (WHERE cond)` is cleaner where supported (SQLite 3.30+, Postgres) but `CASE` runs everywhere.

---

## D09 — date handling with strftime

```sql
SELECT strftime('%Y-%m', txn_ts) AS month,
       COUNT(*) AS n_txns,
       ROUND(SUM(amount), 2) AS total_amount
FROM transactions
WHERE amount > 0
GROUP BY 1
ORDER BY 1
```

Returns **12 rows × 3 columns**.

`strftime('%Y-%m', ts)` in SQLite; `DATE_TRUNC('month', ts)` in Postgres; `DATE_FORMAT` in MySQL. Know that these differ by engine and say so out loud if you're unsure which you're on — that reads as competence, not ignorance. `GROUP BY 1` refers to the first select item, which saves repeating the expression.

---

## D10 — COUNT(DISTINCT ...)

```sql
SELECT merchant_category,
       COUNT(*) AS n_txns,
       COUNT(DISTINCT account_id) AS n_accounts,
       COUNT(DISTINCT merchant_id) AS n_merchants
FROM transactions
WHERE amount > 0 AND merchant_category IS NOT NULL
GROUP BY merchant_category
ORDER BY n_txns DESC, merchant_category ASC
```

Returns **12 rows × 4 columns**.

`COUNT(DISTINCT col)` inside an aggregate is the thing to have ready. The gap between `n_txns` and `n_accounts` is the interesting number: it tells you transactions per account, which is the kind of derived read an interviewer wants you to volunteer.

---

## D11 — subquery in WHERE

```sql
SELECT segment, COUNT(*) AS n_customers
FROM customers
WHERE credit_score_at_signup > (SELECT AVG(credit_score_at_signup) FROM customers)
GROUP BY segment
ORDER BY n_customers DESC, segment ASC
```

Returns **4 rows × 2 columns**.

A scalar subquery — one value — can sit anywhere a literal can. It's evaluated once, not per row. Note it computes the average over *all* customers, not per segment; if you wanted per-segment you'd need a correlated subquery or a window function, which is a meaningfully harder query.

---

## D12 — CTE (WITH ...)

```sql
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
```

Returns **4 rows × 3 columns**.

**Aggregate, then aggregate again.** Sum to the account level in the CTE, then average those sums. You cannot do this in one pass — `AVG(SUM(x))` is not valid. This two-level shape is most of real analytics SQL, and the CTE is what makes it readable.

---

## D13 — ROW_NUMBER -- top N per group

```sql
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
```

Returns **12 rows × 4 columns**.

**The pattern to memorize.** Three steps: rank inside a CTE with `ROW_NUMBER() OVER (PARTITION BY group ORDER BY measure DESC)`, then filter `WHERE rn <= N`. You cannot filter on a window function in the same `SELECT` that defines it — that's why the CTE is mandatory, not stylistic.

---

## D14 — RANK vs ROW_NUMBER on ties

```sql
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
```

Returns **15 rows × 5 columns**.

`ROW_NUMBER` never repeats. `RANK` repeats on ties and then skips (1,2,2,4). `DENSE_RANK` repeats without skipping (1,2,2,3). Use `ROW_NUMBER` when you need exactly one winner, `RANK` when genuine ties should all count. Adding a tiebreaker column to the `ORDER BY` makes `ROW_NUMBER` deterministic — without one, the same query can return different rows on different runs.

---

## D15 — LAG -- period over period

```sql
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
```

Returns **12 rows × 4 columns**.

`LAG(col) OVER (ORDER BY month)` reaches backward one row. The January NULL falls out automatically — never write a `CASE WHEN month = 'first month'` special case. And aggregate to one row per month **before** you lag: window functions run over result rows, so the months must exist first.

---

## D16 — LEAD with a next-period guard

```sql
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
```

Returns **11 rows × 3 columns**.

`LEAD` is `LAG` forward. The guard `next_month = date(statement_month, '+1 month')` is the part people drop: `LEAD` returns the next *statement*, which equals the next *calendar month* only when the history has no gaps. A self-join on `date(a.month, '+1 month')` also works, but it's an inner join, so accounts with no following statement vanish from the denominator.

---

## D17 — running total with a window frame

```sql
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
```

Returns **12 rows × 3 columns**.

An `OVER` clause with `ORDER BY` plus a frame turns any aggregate into a running one. `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` is the explicit spelling of a cumulative total. Leaving the frame out usually gives you the same answer via the default `RANGE` frame — but the defaults bite on ties, so be explicit.

---

## D18 — gaps and islands -- consecutive streaks

```sql
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
```

Returns **12 rows × 2 columns**.

**Gaps and islands.** Number each account's active months with `ROW_NUMBER()`. Inside a consecutive run, `month - row_number` is constant, so subtracting `rn` months from each date yields one synthetic key per island. Group on it, count, then take each account's `MAX`. Once you've seen it, it's 90 seconds. If you haven't, you'll burn a whole SQL budget reinventing it — which is exactly why it's the last drill.

---

## Next

When D13–D18 are automatic — written cold, no peeking, under 3 minutes each — re-sit **Section 2 of
the timed exam**. The drills tell you which pattern to use; the exam makes you work that out for
yourself, which is the harder and more transferable half.
