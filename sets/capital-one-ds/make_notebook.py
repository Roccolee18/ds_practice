"""Builds practice_exam.ipynb."""
import os
import nbformat as nbf

HERE = os.path.dirname(os.path.abspath(__file__))
nb = nbf.v4.new_notebook()
C = []


def md(s):
    C.append(nbf.v4.new_markdown_cell(s.strip("\n")))


def code(s):
    C.append(nbf.v4.new_code_cell(s.strip("\n")))


# ==========================================================================
md(r"""
# Capital One — Data Scientist (Associate / New Grad) Practice Assessment

**Budget: 80 minutes.** Set a timer and do not stop it. Finishing everything is not the goal;
producing correct, defensible work under time pressure is.

| Section | Tasks | Budget | Why it's here |
|---|---|---|---|
| 1 — pandas | P1–P4 | 20 min | Data collection & processing: the messy-extract-to-clean-table loop |
| 2 — SQL | S1–S5 | 30 min | Window functions, CTEs, self-joins on a card portfolio |
| 3 — Applied ML | M1–M4 | 30 min | Leakage, honest validation, and a business-cost decision |

### Rules that make this useful

1. **One pass, no going back.** When a section's budget is up, move on even if it's unfinished.
2. **Docs are allowed. Answers are not.** pandas/sklearn/SQLite docs are fine — that mirrors the real thing.
   Do not look at `SOLUTIONS.md` until the timer stops.
3. **Run `check(...)` as you go.** It tells you *that* something is wrong and roughly where, without
   giving away the answer. Treat a FAIL like a failing hidden test in the real assessment: reread the
   spec, find your own bug.
4. **Answer shapes are specified exactly.** Column names, sort order and rounding are part of the task,
   the same way they are when a hidden test is grading you.
5. **M4 is written, not coded.** Do not skip it. At Capital One the open-ended reasoning carries as much
   weight as the code, and it is the part people prepare least.

### Scoring yourself

Run `score()` at the end. Rough calibration for this set:

- **≥ 85%** with time to spare — you're in good shape.
- **65–85%** — competitive; find your slow section and drill it.
- **< 65%** — you have a specific gap, not a general one. The per-section breakdown will name it.

---
""")

md(r"""
## Setup

Run this once. It locates the problem set on its own, so this notebook works both in place and as a
copy under `attempts/`.
""")

code(r'''
import os, sys, sqlite3, time
import numpy as np
import pandas as pd

pd.set_option("display.width", 170)
pd.set_option("display.max_columns", 40)
pd.set_option("display.float_format", lambda v: f"{v:,.4f}")

SET_NAME = "capital-one-ds"

def _find_set_root(name):
    """Works whether this notebook sits in the set folder or in attempts/."""
    start = os.path.abspath("")
    # already inside the set folder (or a child of it)?
    p = start
    while True:
        if all(os.path.exists(os.path.join(p, f)) for f in ("grader.py", "make_key.py")):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            break
        p = parent
    # otherwise walk up to the repo root and look under sets/
    p = start
    while True:
        cand = os.path.join(p, "sets", name)
        if os.path.isdir(cand):
            return cand
        parent = os.path.dirname(p)
        if parent == p:
            break
        p = parent
    raise RuntimeError(
        f"Could not find the '{name}' problem set. Open this notebook from inside the repo "
        f"(either sets/{name}/ or attempts/<date>-{name}/)."
    )

SET_ROOT = _find_set_root(SET_NAME)
DATA = os.path.join(SET_ROOT, "data")
if SET_ROOT not in sys.path:
    sys.path.insert(0, SET_ROOT)

if not os.path.isdir(DATA):
    raise RuntimeError(f"No data yet. Run:  {os.path.join(SET_ROOT, 'bootstrap.sh')}")

CON = sqlite3.connect(os.path.join(DATA, "warehouse.db"))

def q(sql: str) -> pd.DataFrame:
    """Run SQL against the warehouse and return a DataFrame."""
    if not sql.strip():
        print("(empty query -- write your SQL between the triple quotes)")
        return pd.DataFrame()
    return pd.read_sql_query(sql, CON)

from grader import check, score

_T0 = time.time()
def elapsed(label=""):
    print(f"[{(time.time() - _T0) / 60:5.1f} min] {label}")

with open(os.path.join(DATA, "SEED")) as _f:
    SEED = _f.read().strip()

print(f"set:   {SET_ROOT}")
print(f"seed:  {SEED}   <- record this in your NOTES.md")
print("tables:", q("SELECT name FROM sqlite_master WHERE type='table'").name.tolist())
elapsed("timer started")
''')

# ==========================================================================
# SECTION 1
# ==========================================================================
md(r"""
---
# Section 1 — pandas  ·  budget 20 minutes

You are handed a raw extract of 2025 card transactions plus two reference files.

| file | grain | notes |
|---|---|---|
| `data/transactions_raw.csv` | one row per transaction | **raw system extract — it is dirty** |
| `data/accounts.csv` | one row per card account | `account_id`, `customer_id`, `product`, `open_date`, `credit_limit`, `apr`, `status` |
| `data/customers.csv` | one row per customer | `customer_id`, `signup_date`, `state`, `age`, `segment`, `annual_income`, `credit_score_at_signup` |

A customer can hold more than one account. Every transaction in the extract falls in calendar 2025.

Start by looking at the raw file before you write anything.
""")

code(r'''
raw = pd.read_csv(f"{DATA}/transactions_raw.csv")
print(raw.shape)
print(raw.dtypes)
raw.head(8)
''')

# ---- P1
md(r"""
### P1 — Clean the extract  *(~6 min)*

Three things are wrong with `transactions_raw.csv`:

- **`amount` is text**, with inconsistent formatting: `1234.56`, `$1,234.56`, `1,234.56`,
  values padded with whitespace, and **accounting-style negatives for refunds**, e.g. `($45.20)`
  means −45.20.
- **`merchant_category` has inconsistent casing and stray whitespace** (`Groceries`, `groceries `,
  `GROCERIES` are the same category). Some values are genuinely missing — leave those missing.
- **The extract contains fully duplicated rows** (every column identical, including `transaction_id`).

Produce a cleaned frame where `amount` is a float, `merchant_category` is lowercase and stripped,
`txn_ts` is a datetime, and exact duplicate rows are gone.

**Assign `p1` as a dict with exactly these keys:**

| key | type | meaning |
|---|---|---|
| `n_rows` | int | rows remaining after dropping exact duplicates |
| `n_categories` | int | distinct **non-null** normalized categories |
| `net_amount` | float | sum of all cleaned amounts (purchases **and** refunds), rounded to 2dp |
| `refund_count` | int | rows with a negative amount |

Keep your cleaned frame in a variable — P2, P3 and P4 all build on it.
""")
code(r'''
# --- P1 ---


p1 = {
    "n_rows": None,
    "n_categories": None,
    "net_amount": None,
    "refund_count": None,
}
check("P1", p1)
''')

# ---- P2
md(r"""
### P2 — Spend by segment and product  *(~5 min)*

Using the **cleaned** transactions joined to `accounts` and `customers`, and counting
**purchases only** (`amount > 0`; refunds are excluded entirely):

For each `(segment, product)` pair compute
- `n_accounts` — distinct accounts with at least one purchase,
- `total_spend` — sum of purchase amounts, rounded to 2dp,
- `spend_per_account` — `total_spend / n_accounts`, rounded to 2dp.

**Assign `p2` as a DataFrame** with columns `["segment", "product", "n_accounts", "total_spend",
"spend_per_account"]`, sorted by `segment` then `product` ascending, with a clean `RangeIndex`.
""")
code(r'''
# --- P2 ---


p2 = None
check("P2", p2)
''')

# ---- P3
md(r"""
### P3 — Trailing-30-day velocity flag  *(~6 min)*

Fraud and credit-line teams watch **spend velocity against the line**, not single transactions.

Definition, precisely:
1. Keep purchases only (`amount > 0`).
2. Roll each account's purchases up to a **daily total**.
3. For each account, on every day that account had a purchase, compute the **trailing 30-day
   purchase total**: the window is the 30 calendar days ending on and including that day.
4. An account is **flagged** on the first day where that trailing total **exceeds its `credit_limit`**.

**Assign `p3` as a dict:**

| key | type | meaning |
|---|---|---|
| `n_accounts_flagged` | int | accounts flagged at least once in 2025 |
| `n_flagged_in_q1` | int | of those, how many were **first** flagged before 2025-04-01 |
| `max_trailing30_ratio` | float | the largest `trailing_30_day_total / credit_limit` seen across all accounts and days, rounded to 2dp |

*Hint if you're stuck on mechanics: `df.set_index(date_col).groupby(key)[value].rolling("30D").sum()`.*
""")
code(r'''
# --- P3 ---


p3 = {
    "n_accounts_flagged": None,
    "n_flagged_in_q1": None,
    "max_trailing30_ratio": None,
}
check("P3", p3)
''')

# ---- P4
md(r"""
### P4 — Share-of-wallet concentration  *(~3 min)*

Aggregate to the **customer** level (a customer's accounts combine). Use purchases only
(`amount > 0`) **with a non-null category**.

- A customer is **eligible** if they have **at least 20** such purchases.
- For each eligible customer, compute the share of their total purchase spend that falls in their
  single largest category (break ties alphabetically by category name).
- A customer is **concentrated** if that top share is **≥ 0.35**.

**Assign `p4` as a dict:**

| key | type | meaning |
|---|---|---|
| `n_eligible` | int | eligible customers |
| `n_concentrated` | int | eligible customers with top share ≥ 0.35 |
| `top_category` | str | the category that is the #1 category for the most eligible customers (lowercase) |
| `mean_top_share` | float | mean top-category share across eligible customers, rounded to 4dp |
""")
code(r'''
# --- P4 ---


p4 = {
    "n_eligible": None,
    "n_concentrated": None,
    "top_category": None,
    "mean_top_share": None,
}
check("P4", p4)
''')

code(r'''
elapsed("end of Section 1 -- target was 20 min")
''')

# ==========================================================================
# SECTION 2
# ==========================================================================
md(r"""
---
# Section 2 — SQL  ·  budget 30 minutes

`data/warehouse.db` is SQLite. Unlike the CSVs it is **already clean and typed** — this section is
about query logic, not string surgery.

| table | grain | columns |
|---|---|---|
| `customers` | customer | `customer_id, signup_date, state, age, segment, annual_income, credit_score_at_signup` |
| `accounts` | account | `account_id, customer_id, product, open_date, credit_limit, apr, status` |
| `transactions` | transaction | `transaction_id, account_id, txn_ts, amount, merchant_category, merchant_id, channel, is_disputed` |
| `statements` | account × month | `statement_id, account_id, statement_month, statement_balance, min_payment_due, payment_made, days_past_due` |

Notes that matter:

- `status` ∈ `{'open', 'closed', 'charged_off'}`.
- `merchant_category` is stored in canonical mixed case here (`'Groceries'`), and can be `NULL`.
- Dates are ISO text: `txn_ts` is `'YYYY-MM-DD HH:MM:SS'`, `statement_month` is the **first of the
  month**, `'YYYY-MM-01'`. `strftime`, `date(x, '+1 month')` and plain string comparison all work.
- `days_past_due` ∈ `{0, 30, 60, 90, 120}`. An account stops producing statements once it hits 120.
- SQLite 3.45 — window functions, CTEs and `FILTER` are all available.

Write each answer as a **single SQL statement** and run it with the `q(...)` helper.
""")

md(r"""
### S1 — Charge-off rate by segment and product  *(~4 min)*

For each `(segment, product)` combination **with at least 50 accounts**, return one row:

`segment, product, n_accounts, n_charged_off, charge_off_rate`

where `charge_off_rate = n_charged_off / n_accounts` **rounded to 4dp**, and `n_charged_off` counts
accounts with `status = 'charged_off'`.

Order by `charge_off_rate` **descending**, then `segment` ascending, then `product` ascending.
""")
code(r'''
# --- S1 ---
s1 = q("""

""")
check("S1", s1)
''')

md(r"""
### S2 — Everyone's #1 spending category  *(~7 min)*

Using 2025 transactions where `amount > 0` and `merchant_category IS NOT NULL`:

For each customer, find the merchant category they spent the most in (ties broken **alphabetically**
by category name). Then return, **per category**, how many customers have it as their #1:

`merchant_category, n_customers`

Order by `n_customers` descending, then `merchant_category` ascending.

**Use a window function.** A correlated subquery that happens to produce the same numbers is not what
the question is testing — this is exactly the pattern (`ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`)
that shows up in nearly every data-scientist SQL screen.
""")
code(r'''
# --- S2 ---
s2 = q("""

""")
check("S2", s2)
''')

md(r"""
### S3 — Month-over-month portfolio spend  *(~5 min)*

For calendar 2025, total **purchase** spend (`amount > 0`) across the whole portfolio by month:

`month, total_spend, mom_pct_change`

- `month` formatted `'YYYY-MM'`
- `total_spend` rounded to 2dp
- `mom_pct_change` = `100 * (this_month - prev_month) / prev_month`, rounded to 2dp, and
  **NULL for January** (no prior month)

Order by `month` ascending.
""")
code(r'''
# --- S3 ---
s3 = q("""

""")
check("S3", s3)
''')

md(r"""
### S4 — The 30→60 roll rate  *(~8 min)*

The single most-used credit risk metric: of the accounts that were 30 days past due this month,
what fraction got *worse* next month?

For each `statement_month` from 2025-01 through 2025-11:

- `n_30dpd` — accounts with `days_past_due = 30` in that month
- `n_rolled` — of those, how many had `days_past_due >= 60` in the **immediately following calendar
  month**. An account with no statement in the following month counts as **not** rolled.
- `roll_rate` = `n_rolled / n_30dpd`, rounded to 4dp

Return `month, n_30dpd, n_rolled, roll_rate` with `month` formatted `'YYYY-MM'`, excluding any month
where `n_30dpd = 0`, ordered by `month` ascending.
""")
code(r'''
# --- S4 ---
s4 = q("""

""")
check("S4", s4)
''')

md(r"""
### S5 — Consecutive delinquency streaks  *(stretch, ~6 min)*

A customer is **delinquent in month M** if **any** of their accounts has `days_past_due > 0` in that
statement month.

For each customer, find the length of their **longest run of consecutive calendar months** in 2025
during which they were delinquent. Return only customers whose longest run is **3 or more**:

`customer_id, longest_streak`

Order by `longest_streak` descending, then `customer_id` ascending.

*This is the "gaps and islands" problem. If you've never seen it: number the delinquent months per
customer with `ROW_NUMBER()`, then note that within a consecutive run, `month - row_number` is
constant. Group on that constant.*

If you are past 30 minutes, skip this and move to Section 3. Come back to it afterwards.
""")
code(r'''
# --- S5 ---
s5 = q("""

""")
check("S5", s5)
''')

code(r'''
elapsed("end of Section 2 -- target was 50 min cumulative")
''')

# ==========================================================================
# SECTION 3
# ==========================================================================
md(r"""
---
# Section 3 — Applied machine learning  ·  budget 30 minutes

`data/credit_applications.csv` — 20,000 credit card applications from 2023-01 through 2024-12, one row
per application, with the outcome observed 12 months after booking.

**Target:** `default_12m` (1 = went 90+ days past due or charged off within 12 months).

| column | meaning |
|---|---|
| `application_id` | identifier |
| `app_date` | date the application was submitted |
| `requested_product`, `channel` | product applied for; acquisition channel |
| `applicant_age`, `state`, `zip3` | applicant demographics / geography |
| `fico_score` | bureau score at application |
| `annual_income` | stated income (**has missing values**) |
| `dti_ratio` | debt-to-income at application |
| `employment_length_years` | years at current employer (**uses `-1` as an "unknown" sentinel**) |
| `num_inquiries_6m` | credit inquiries in the prior 6 months |
| `revolving_utilization` | revolving utilization (**uses `999` as a bad-data sentinel**) |
| `delinq_2yrs` | delinquencies in the prior 2 years |
| `home_ownership` | RENT / MORTGAGE / OWN / OTHER (**has missing values**) |
| `requested_amount` | credit line requested |
| `assigned_credit_limit` | line actually assigned at underwriting |
| `post_orig_30dpd_count` | count of 30-day delinquencies **after the account was opened** |
| `recovery_amount_usd` | dollars recovered by collections |
| `default_12m` | **target** |

**Read that table carefully before you write any code.** Some of those columns are not legitimate
model inputs, and noticing which ones is the single highest-signal thing you do in this section.
""")

code(r'''
apps = pd.read_csv(f"{DATA}/credit_applications.csv", parse_dates=["app_date"])
print(apps.shape, "| default rate:", round(apps.default_12m.mean(), 4))
apps.head()
''')

md(r"""
### M1 — A defensible baseline  *(~12 min)*

Build a model you would be willing to defend in a model-risk review.

1. **Drop any feature that would not be knowable at the moment the application is decided.**
2. Handle the coded-missing sentinels (`employment_length_years == -1`, `revolving_utilization == 999`)
   — they are *not* legitimate values.
3. Split **by time**: train on `app_date < '2024-07-01'`, test on `app_date >= '2024-07-01'`.
4. Fit any classifier you like, with preprocessing inside a `Pipeline` (so nothing leaks from test
   into train).
5. Score on the test set with **both** ROC-AUC and PR-AUC (average precision). The positive class is
   ~8% — know why you want both.

**Assign `m1` as a dict:**

| key | type |
|---|---|
| `excluded_features` | list[str] — the columns you dropped as not-available-at-decision |
| `test_roc_auc` | float |
| `test_pr_auc` | float |
| `n_train`, `n_test` | int |

Keep your fitted pipeline and the test-set predicted probabilities — M3 needs them.
""")
code(r'''
# --- M1 ---


m1 = {
    "excluded_features": [],
    "test_roc_auc": None,
    "test_pr_auc": None,
    "n_train": None,
    "n_test": None,
}
check("M1", m1)
''')

md(r"""
### M2 — What does a random split cost you?  *(~6 min)*

Refit **the identical pipeline** on a random stratified split with the same test-set size and
`random_state=42`, and compare its ROC-AUC to your honest time-based number.

**Assign `m2`:**

| key | type |
|---|---|
| `random_split_roc_auc` | float |
| `time_split_roc_auc` | float (your M1 number) |
| `optimism` | float — `random - time`, rounded to 4dp |

Then look at the gap and be ready to say, in M4, *why* it exists. It is not an accident of this
dataset — something specific happened in the second half of 2024.
""")
code(r'''
# --- M2 ---


m2 = {
    "random_split_roc_auc": None,
    "time_split_roc_auc": None,
    "optimism": None,
}
check("M2", m2)
''')

md(r"""
### M3 — Turn the score into a decision  *(~7 min)*

A model with good AUC is worth nothing until someone picks a cutoff. Per approved application, over
12 months:

- an applicant who **does not** default contributes **+\$240**
- an applicant who **does** default costs **−\$1,650**
- a **declined** application contributes **\$0**

Using your **M1 test-set predicted probabilities**, approve when `predicted_probability < t`. Sweep
`t` over a fine grid and find the profit-maximizing cutoff.

**Assign `m3`:**

| key | type | meaning |
|---|---|---|
| `best_threshold` | float | the profit-maximizing `t`, 3dp (**not graded** — it depends on your model's calibration) |
| `expected_profit_per_app` | float | total profit at that cutoff ÷ number of test applications, 2dp |
| `approval_rate_at_best` | float | share of test applications approved at that cutoff, 4dp |
| `profit_at_approve_all` | float | profit per application if you approved everyone, 2dp |

Compare the last two numbers before you move on. That difference is the entire business case for the
model, and it is the number an interviewer will ask you to state out loud.
""")
code(r'''
# --- M3 ---


m3 = {
    "best_threshold": None,
    "expected_profit_per_app": None,
    "approval_rate_at_best": None,
    "profit_at_approve_all": None,
}
check("M3", m3)
''')

md(r"""
### M4 — The written section  *(~5 min, no code)*

This is not filler. Capital One is a regulated lender, and the open-ended reasoning is weighted at
least as heavily as the code. Write **3–5 sentences each** — specific, not generic. Aim for the level
of detail you would give a skeptical manager, not a textbook.

Fill in the strings below, then grade yourself against the rubric at the end of `SOLUTIONS.md`.
""")
code(r'''
# --- M4 --- (replace each empty string; 3-5 sentences each)

m4 = {

"leakage": """
Which columns did you exclude, and how did you know? Describe the general test you would apply to a
dataset you had never seen before to find this class of problem.
""",

"model_choice": """
You get one model in production for a credit decision at a regulated lender. Logistic regression on
binned/WOE features, or gradient boosting? Pick one and defend it. Name the concrete cost of what you
gave up.
""",

"imbalance": """
The positive class is about 8%. What did you actually do about it, what metric did you steer on, and
name one commonly recommended technique you deliberately did NOT use and why.
""",

"fairness": """
`applicant_age` and `zip3` are both in the file. What is your position on using them in a credit
underwriting model, and what would you do if a permitted variable turned out to be highly correlated
with a protected characteristic?
""",

"monitoring": """
The model ships. What do you monitor, at what cadence, and what specifically triggers a retrain or a
rollback? Note the one thing you cannot measure for 12 months and how you cope in the meantime.
""",

"next_step": """
You get 30 more minutes. What is the single highest-value thing you add, and why that over the
alternatives?
""",

}

for k, v in m4.items():
    n = len(v.split())
    print(f"{k:14s} {n:4d} words {'  <-- still the prompt text?' if n > 45 else ''}")
''')

code(r'''
elapsed("end of Section 3 -- target was 80 min cumulative")
score()
''')

md(r"""
---
## After the timer stops

1. Note your per-section score from `score()`.
2. Open `SOLUTIONS.md`. Read the worked solution for **everything**, including what you got right —
   the commentary explains *why* the intended approach is the one to reach for under time pressure,
   and flags the trap each task is built around.
3. Grade M4 yourself against the rubric at the end.
4. Re-run any task you failed **from scratch**, not by patching your old cell. The skill being built
   is getting it right the first time.

### Logging this attempt

1. Fill in `NOTES.md` next to this notebook — seed, elapsed time, per-section score, M4 rubric total.
2. Add a row to `PROGRESS.md` at the repo root.
3. Commit: `git add -A && git commit -m "attempt: capital-one-ds #N — 78% (SQL 60%)"`

Save this notebook **with its outputs intact** — the `check()` results are the record of what you
actually did, and they're what you'll diff against next time.

To re-sit later with different numbers: `./bootstrap.sh 12345` in the set folder, then
`./new-attempt.sh capital-one-ds` from the repo root.
""")

nb["cells"] = C
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11"},
}
out = os.path.join(HERE, "practice_exam.ipynb")
nbf.write(nb, out)
print(f"wrote {out} ({len(C)} cells)")
