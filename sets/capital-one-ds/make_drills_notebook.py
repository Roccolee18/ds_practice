"""Builds sql_drills.ipynb from drills_sql.py."""
import os
import nbformat as nbf
import drills_sql as D

HERE = os.path.dirname(os.path.abspath(__file__))
C = []
md = lambda s: C.append(nbf.v4.new_markdown_cell(s.strip("\n")))
code = lambda s: C.append(nbf.v4.new_code_cell(s.strip("\n")))

PROMPTS = {
"D01": """Return the 10 **Venture** accounts with a credit limit of **2600 or more**.

Columns: `account_id, product, credit_limit`. Order by `credit_limit` descending, then
`account_id` ascending. Cap the output at 10 rows.""",

"D02": """One row per card product: how many accounts, the average credit limit, and the average APR.

Columns: `product, n_accounts, avg_limit, avg_apr`. Both averages rounded to 2dp.
Order by `n_accounts` descending.""",

"D03": """States with **at least 250 customers**.

Columns: `state, n_customers`. Order by `n_customers` descending, then `state` ascending.

> The filter is on a group total, not on a row. That decides which keyword you need.""",

"D04": """Per segment: how many customers, how many are missing `annual_income`, and what share
that is.

Columns: `segment, n_customers, n_missing_income, pct_missing`. `pct_missing` rounded to 4dp.
Order by `pct_missing` descending, then `segment` ascending.

> If your percentages all come out as 0, you've hit the single most common SQL bug there is.""",

"D05": """Account counts and average credit limit **by customer segment** — the segment lives on
`customers`, the limit on `accounts`.

Columns: `segment, n_accounts, avg_limit`. `avg_limit` rounded to 2dp.
Order by `avg_limit` descending.""",

"D06": """Purchase counts and totals by customer segment **and** transaction channel. Purchases only
(`amount > 0`).

Columns: `segment, channel, n_txns, total_amount`. `total_amount` rounded to 2dp.
Order by `segment` ascending, then `channel` ascending.

> Three tables. Chain the joins: transactions → accounts → customers.""",

"D07": """Per segment, how many customers have **never** had a delinquent statement
(`days_past_due > 0` on any of their accounts, in any month).

Columns: `segment, n_never_delinquent`. Order by `n_never_delinquent` descending,
then `segment` ascending.

> This is an **anti-join**: rows on the left with no match on the right. Build the set of
> delinquent customers first, LEFT JOIN to it, and keep the rows where the match is NULL.
> Careful — joining `statements` directly to `customers` fans out (one row per statement) and
> inflates every count. Collapse to one row per customer before you join.""",

"D08": """One row per product, with account status broken out into columns.

Columns: `product, n_accounts, n_open, n_closed, n_charged_off`. Order by `product` ascending.

> Pivoting rows into columns. `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` — this is the single most
> reusable aggregation idiom in SQL.""",

"D09": """Monthly purchase volume for 2025 (`amount > 0`).

Columns: `month` formatted `'YYYY-MM'`, `n_txns`, `total_amount` rounded to 2dp.
Order by `month` ascending.

> `strftime('%Y-%m', txn_ts)` in SQLite.""",

"D10": """Per merchant category (non-null), the number of purchases, the number of **distinct
accounts**, and the number of **distinct merchants**.

Columns: `merchant_category, n_txns, n_accounts, n_merchants`.
Order by `n_txns` descending, then `merchant_category` ascending.""",

"D11": """Customers whose `credit_score_at_signup` is **above the overall average**, counted by segment.

Columns: `segment, n_customers`. Order by `n_customers` descending, then `segment` ascending.

> The average is a single value, so a scalar subquery in the WHERE clause does it.""",

"D12": """Average total 2025 purchase spend per account, by product.

Columns: `product, n_accounts, avg_spend`. `avg_spend` rounded to 2dp.
Order by `avg_spend` descending.

> Two levels of aggregation: sum to the account first, then average those sums. A CTE makes this
> readable — and this shape (aggregate, then aggregate again) is most of real analytics SQL.""",

"D13": """The **3 highest-limit accounts within each product**.

Columns: `product, account_id, credit_limit, rn` (the rank, 1–3). Ties broken by `account_id`
ascending. Order by `product` ascending, then `rn` ascending.

> The top-N-per-group pattern. `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` in a CTE,
> then filter on the rank. **Memorize this one** — it appears in almost every SQL screen.""",

"D14": """Customer counts by state, with three different ranking functions side by side so you can see
how they differ on ties.

Columns: `state, n_customers, row_num, rnk, dense_rnk`.
- `row_num` = `ROW_NUMBER()` ordered by `n_customers` DESC then `state` ASC
- `rnk` = `RANK()` ordered by `n_customers` DESC only
- `dense_rnk` = `DENSE_RANK()` ordered by `n_customers` DESC only

Order by `n_customers` descending, then `state` ascending.

> Look hard at the output. Where two states tie, `RANK` repeats the number and then skips;
> `DENSE_RANK` repeats without skipping; `ROW_NUMBER` never repeats. Knowing which to reach for
> is a standard verbal question.""",

"D15": """Total payments received per statement month, with the prior month alongside and the change.

Columns: `month` (`'YYYY-MM'`), `total_paid` (2dp), `prev_paid`, `change` (2dp).
Order by `month` ascending. January's `prev_paid` and `change` are NULL.

> `LAG(col) OVER (ORDER BY month)`. Aggregate to one row per month **first** — a window function
> operates on result rows, so the months have to exist before you can lag across them.""",

"D16": """Of the accounts delinquent in a given month, how many **cured** (returned to
`days_past_due = 0`) the following calendar month?

Columns: `month` (`'YYYY-MM'`), `n_current` (accounts with `days_past_due > 0` that month),
`n_cured`. Cover 2025-01 through 2025-11. Order by `month` ascending.

> `LEAD` is `LAG` pointing forward. The catch: `LEAD` gives you the next *statement row*, which is
> only the next *calendar month* if the account's history has no gaps — so guard on
> `next_month = date(statement_month, '+1 month')`.""",

"D17": """Monthly purchase spend for 2025 with a **cumulative running total**.

Columns: `month` (`'YYYY-MM'`), `spend` (2dp), `running_total` (2dp).
Order by `month` ascending.

> `SUM(spend) OVER (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`.
> An `OVER` clause with an `ORDER BY` and a frame turns any aggregate into a running one.""",

"D18": """For each account, find the **longest run of consecutive calendar months in which it had at
least one purchase**. Then report the distribution: how many accounts have each longest-streak value.

Columns: `longest_streak, n_accounts`. Order by `longest_streak` ascending.

> **Gaps and islands.** Number each account's active months with `ROW_NUMBER()`. Within a
> consecutive run, `month - row_number` is constant — so `date(month, '-' || rn || ' months')`
> gives one key per island. Group on it, count, then take each account's MAX.
>
> This is the capstone. If you can write it cold, S5 in the timed exam is the same problem.""",
}

md(r"""
# SQL drills — graduated, 18 problems

Each drill trains **one** pattern and builds on the one before it. Work top to bottom; skipping
ahead won't work, because D13–D18 assume the earlier ones are automatic.

**Total: ~95 minutes if you already know the material. Budget 2–3× that the first time through.**

| | drills | patterns |
|---|---|---|
| **Warm-up** | D01–D04 | `WHERE` · `GROUP BY` · `HAVING` · the integer-division trap |
| **Joins** | D05–D08 | two-table · three-table · anti-join · conditional aggregation |
| **Working with data** | D09–D12 | dates · `COUNT(DISTINCT)` · subqueries · CTEs |
| **Windows** | D13–D18 | `ROW_NUMBER` · `RANK` · `LAG` · `LEAD` · running totals · gaps-and-islands |

### How to use these — this matters more than the problems

For anything you can't write cold in 2 minutes:

1. **Attempt for 2 minutes.** Write whatever you've got, even if it's broken.
2. **Read the solution once.** Don't type while looking.
3. **Break it.** Delete a clause, predict what changes, run it, check. Three or four per query.
4. **Close the solution and write it from memory.** Stuck for 60 seconds? Peek at *one line*,
   close it, start over from the top.
5. **Repeat 4 until it's clean with no peeking.**
6. **Next day, write it again cold.**

Step 6 does more than steps 1–5 combined. One spaced rewrite beats three same-day repetitions.

The reference solutions are in `DRILLS_SOLUTIONS.md` — same rule as the exam, don't open it until
you've attempted.
""")

code(r'''
import os, sys, sqlite3, time
import pandas as pd

SET_NAME = "capital-one-ds"

def _find_set_root(name):
    start = os.path.abspath("")
    p = start
    while True:
        if all(os.path.exists(os.path.join(p, f)) for f in ("grader.py", "make_key.py")):
            return p
        parent = os.path.dirname(p)
        if parent == p: break
        p = parent
    p = start
    while True:
        cand = os.path.join(p, "sets", name)
        if os.path.isdir(cand): return cand
        parent = os.path.dirname(p)
        if parent == p: break
        p = parent
    raise RuntimeError(f"Could not find the '{name}' problem set.")

SET_ROOT = _find_set_root(SET_NAME)
DATA = os.path.join(SET_ROOT, "data")
if SET_ROOT not in sys.path:
    sys.path.insert(0, SET_ROOT)
if not os.path.isdir(DATA):
    raise RuntimeError(f"No data yet. Run:  {os.path.join(SET_ROOT, 'bootstrap.sh')}")

CON = sqlite3.connect(os.path.join(DATA, "warehouse.db"))

def q(sql):
    if not sql.strip():
        print("(empty query -- write your SQL between the triple quotes)")
        return pd.DataFrame()
    return pd.read_sql_query(sql, CON)

from grader import check, score

pd.set_option("display.width", 170)
pd.set_option("display.max_columns", 40)

print("tables:", q("SELECT name FROM sqlite_master WHERE type='table'").name.tolist())
print("\nschema reminder:")
for t in ["customers", "accounts", "transactions", "statements"]:
    cols = q(f"PRAGMA table_info({t})").name.tolist()
    print(f"  {t:13s} {', '.join(cols)}")
''')

SECTIONS = {
    "D01": "## Warm-up — `WHERE`, `GROUP BY`, `HAVING`",
    "D05": "## Joins",
    "D09": "## Dates, distinct counts, subqueries, CTEs",
    "D13": "## Window functions",
}

for did, pattern, minutes, _ in D.DRILLS:
    if did in SECTIONS:
        md("---\n" + SECTIONS[did])
    md(f"### {did} — {pattern}  ·  ~{minutes} min\n\n{PROMPTS[did]}")
    var = did.lower()
    code(f'# --- {did} ---\n{var} = q("""\n\n""")\ncheck("{did}", {var})')

md(r"""
---
## Done

```python
score()
```

Anything below 100% goes back through the read → break → close → rewrite loop, and gets rewritten
cold the next day.

When D13–D18 are automatic, re-sit **Section 2 of the timed exam** cold. That's the real test of
whether this transferred — the drills tell you the pattern, the exam makes you recognize it.
""")
code("score()")

nb = nbf.v4.new_notebook()
nb["cells"] = C
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11"},
}
out = os.path.join(HERE, "sql_drills.ipynb")
nbf.write(nb, out)
print(f"wrote {out} ({len(C)} cells)")
