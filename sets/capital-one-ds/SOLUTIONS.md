# Answer key & commentary

Don't open this until your timer has stopped.

Read the commentary even for the tasks you got right — each one is built around a specific trap, and
the notes say which. Reference numbers are from the bundled dataset; if you regenerated the data with
a new seed, your numbers will differ but the code is unchanged.

---

# Section 1 — pandas

## Shared cleaning step

Everything in Section 1 runs off one cleaned frame. Build it once.

```python
def parse_amount(s: pd.Series) -> pd.Series:
    t = s.astype("string").str.strip()
    neg = t.str.startswith("(") & t.str.endswith(")")     # ($45.20) means -45.20
    t = t.str.replace(r"[()$,\s]", "", regex=True)
    out = pd.to_numeric(t, errors="coerce")
    return out.where(~neg, -out).astype("float64")

tx = pd.read_csv(f"{DATA}/transactions_raw.csv")
tx = tx.drop_duplicates()
tx["amount"] = parse_amount(tx["amount"])
tx["merchant_category"] = (tx["merchant_category"].astype("string")
                             .str.strip().str.lower())
tx["txn_ts"] = pd.to_datetime(tx["txn_ts"])
```

**Order matters.** `drop_duplicates()` goes first, while every column is still raw text — it is a
cheap exact-match dedupe at that point. If you parse first and dedupe after, you get the same answer
here but you've done the expensive work on rows you were about to throw away, and on a real extract
you'd risk two rows that parsed to the same float from different raw text collapsing into one.

**The regex is the whole task.** `[()$,\s]` strips parentheses, dollar signs, thousands separators
and padding in one pass. The `neg` mask has to be computed *before* you strip the parentheses —
that's the ordering bug that costs people this question. A naive
`float(s.replace("$","").replace(",",""))` turns `($45.20)` into `NaN`, and `errors="coerce"`
silently hides it. That is exactly why the task asks for `refund_count`: it's a tripwire.

## P1

```python
p1 = {
    "n_rows":        int(len(tx)),
    "n_categories":  int(tx["merchant_category"].dropna().nunique()),
    "net_amount":    float(round(tx["amount"].sum(), 2)),
    "refund_count":  int((tx["amount"] < 0).sum()),
}
```

Reference: `{'n_rows': 112437, 'n_categories': 12, 'net_amount': 8253043.46, 'refund_count': 3381}`

**Traps.** Without dedupe you get 113,111 rows. Without case/whitespace normalization
`nunique()` returns 48 instead of 12 — three casing variants plus a whitespace-padded one per
category. Without the accounting-negative handling `refund_count` comes out around 1,344 instead of
3,381, and `net_amount` is inflated by roughly \$140k. Each of the four keys catches a different one
of those mistakes; that's deliberate, and it's how hidden tests are usually designed.

**Don't do this:** `tx.drop_duplicates(subset="transaction_id")`. It gives the right answer here by
luck. Deduping on the key alone silently keeps one of two *genuinely different* rows that share an
ID, which is a data-quality bug you want to surface, not hide. Dedupe on all columns; then, if
duplicate IDs remain, that's a finding you report.

## P2

```python
acc = pd.read_csv(f"{DATA}/accounts.csv")
cus = pd.read_csv(f"{DATA}/customers.csv")

pur = tx[tx["amount"] > 0]
m = (pur.merge(acc[["account_id", "customer_id", "product"]], on="account_id", how="inner")
        .merge(cus[["customer_id", "segment"]], on="customer_id", how="inner"))

p2 = (m.groupby(["segment", "product"], as_index=False)
        .agg(n_accounts=("account_id", "nunique"),
             total_spend=("amount", "sum")))
p2["total_spend"] = p2["total_spend"].round(2)
p2["spend_per_account"] = (p2["total_spend"] / p2["n_accounts"]).round(2)
p2 = p2.sort_values(["segment", "product"]).reset_index(drop=True)
```

Reference (16 rows):

| segment | product | n_accounts | total_spend | spend_per_account |
|---|---|---|---|---|
| Affluent | PlatinumSecured | 14 | 55,566.43 | 3,969.03 |
| Affluent | Quicksilver | 265 | 984,011.10 | 3,713.25 |
| Affluent | Savor | 170 | 635,439.89 | 3,737.88 |
| Affluent | Venture | 497 | 1,859,770.00 | 3,741.99 |
| Mass | PlatinumSecured | 315 | 413,047.16 | 1,311.26 |
| Mass | Quicksilver | 1147 | 1,463,703.54 | 1,276.11 |
| Mass | Savor | 724 | 927,624.76 | 1,281.25 |
| Mass | Venture | 491 | 625,948.75 | 1,274.84 |
| SmallBusiness | PlatinumSecured | 23 | 45,862.46 | 1,994.02 |
| SmallBusiness | Quicksilver | 203 | 425,793.70 | 2,097.51 |
| SmallBusiness | Savor | 98 | 205,072.24 | 2,092.57 |
| SmallBusiness | Venture | 176 | 367,102.26 | 2,085.81 |
| Student | PlatinumSecured | 399 | 207,811.30 | 520.83 |
| Student | Quicksilver | 230 | 122,247.19 | 531.51 |
| Student | Savor | 96 | 47,620.05 | 496.04 |
| Student | Venture | 41 | 18,620.10 | 454.15 |

**Named aggregation** (`agg(n_accounts=("account_id", "nunique"))`) is the thing to have in your
fingers. It produces flat column names directly; `.agg({"account_id": "nunique"})` hands you a
MultiIndex you then waste a minute flattening — a minute you don't have.

**Traps.** Filtering `amount > 0` *before* the groupby, not after. `nunique` on `account_id`, not
`count` (an account has many transactions). And note `n_accounts` counts accounts that *transacted*,
not accounts that exist — the spec says so, and the difference is real: the Student/Venture cell has
41 transacting accounts out of more in the portfolio.

## P3

```python
pur = tx[tx["amount"] > 0].copy()
pur["date"] = pur["txn_ts"].dt.normalize()

daily = (pur.groupby(["account_id", "date"], as_index=False)["amount"].sum()
            .sort_values(["account_id", "date"]))

roll = (daily.set_index("date")
             .groupby("account_id")["amount"]
             .rolling("30D").sum()
             .reset_index(name="trailing30"))

roll = roll.merge(acc[["account_id", "credit_limit"]], on="account_id", how="left")
roll["ratio"] = roll["trailing30"] / roll["credit_limit"]

first = roll[roll["ratio"] > 1.0].groupby("account_id", as_index=False)["date"].min()

p3 = {
    "n_accounts_flagged":   int(len(first)),
    "n_flagged_in_q1":      int((first["date"] < "2025-04-01").sum()),
    "max_trailing30_ratio": float(round(roll["ratio"].max(), 2)),
}
```

Reference: `{'n_accounts_flagged': 1506, 'n_flagged_in_q1': 442, 'max_trailing30_ratio': 5.93}`

**The whole question is `rolling("30D")` on a DatetimeIndex inside a groupby.** A *time-based*
window and a *row-based* window (`rolling(30)`) are completely different things, and the
distinction is the single most common reason people fail time-series questions in these
assessments. `rolling(30)` means "the last 30 rows", which here would mean 30 transactions spread
over an arbitrary stretch of calendar time. `rolling("30D")` means "the last 30 days", which is what
a velocity rule actually is.

**Why aggregate to daily totals first.** Two reasons. Correctness: the spec defines the window over
calendar days, so multiple same-day transactions must be one point. Practicality: 112k transaction
rows rolled per-account is slow; ~100k daily rows is not. Rolling on a non-unique index also has
edge cases you do not want to discover on the clock.

**Trap.** `pd.Timedelta("30D")` windows are right-closed and include the current point, so this is
"day *d* minus 29 days through day *d*" — exactly the 30 calendar days the spec asks for. If you
reached for `.rolling(window=30, on="date")` or resampled to a daily grid and filled zeros, you'd
get a different (and defensible-sounding, but wrong-per-spec) answer. Read the window definition
before you write.

## P4

```python
pur_cat = tx[(tx["amount"] > 0) & tx["merchant_category"].notna()]
m = pur_cat.merge(acc[["account_id", "customer_id"]], on="account_id", how="inner")

n_pur    = m.groupby("customer_id").size()
eligible = n_pur[n_pur >= 20].index
m        = m[m["customer_id"].isin(eligible)]

cat = m.groupby(["customer_id", "merchant_category"], as_index=False)["amount"].sum()
tot = cat.groupby("customer_id", as_index=False)["amount"].sum().rename(columns={"amount": "total"})

top = (cat.sort_values(["customer_id", "amount", "merchant_category"],
                       ascending=[True, False, True])
          .groupby("customer_id", as_index=False).first()
          .merge(tot, on="customer_id"))
top["share"] = top["amount"] / top["total"]

p4 = {
    "n_eligible":     int(len(eligible)),
    "n_concentrated": int((top["share"] >= 0.35).sum()),
    "top_category":   str(top["merchant_category"].value_counts().idxmax()),
    "mean_top_share": float(round(top["share"].mean(), 4)),
}
```

Reference: `{'n_eligible': 2393, 'n_concentrated': 277, 'top_category': 'groceries', 'mean_top_share': 0.2687}`

**Sort-then-`first()` beats `idxmax()`** when ties have a specified tiebreak. `idxmax()` returns the
first occurrence in whatever order the groupby happened to produce, which is not the alphabetical
rule the spec asks for. Sorting by `["customer_id", amount DESC, category ASC]` and taking `.first()`
encodes the tiebreak explicitly and is one line.

**Trap.** Eligibility is defined on purchases *with a category* — the same filter used for the shares.
If you count eligibility on all purchases including uncategorized ones, `n_eligible` drifts. When a
task defines a population and a metric, apply the same filter to both unless told otherwise.

---

# Section 2 — SQL

## S1 — Charge-off rate by segment and product

```sql
SELECT c.segment,
       a.product,
       COUNT(*) AS n_accounts,
       SUM(CASE WHEN a.status = 'charged_off' THEN 1 ELSE 0 END) AS n_charged_off,
       ROUND(1.0 * SUM(CASE WHEN a.status = 'charged_off' THEN 1 ELSE 0 END)
             / COUNT(*), 4) AS charge_off_rate
FROM accounts a
JOIN customers c ON c.customer_id = a.customer_id
GROUP BY c.segment, a.product
HAVING COUNT(*) >= 50
ORDER BY charge_off_rate DESC, segment ASC, product ASC;
```

Reference — 13 rows, top and bottom:

| segment | product | n_accounts | n_charged_off | charge_off_rate |
|---|---|---|---|---|
| Student | PlatinumSecured | 400 | 27 | 0.0675 |
| Student | Savor | 96 | 6 | 0.0625 |
| SmallBusiness | Savor | 98 | 6 | 0.0612 |
| … | | | | |
| Affluent | Quicksilver | 265 | 8 | 0.0302 |
| SmallBusiness | Quicksilver | 203 | 5 | 0.0246 |

16 segment×product pairs exist; `HAVING COUNT(*) >= 50` drops three.

**`1.0 *` is not optional.** SQLite, Postgres and MySQL all do integer division on
`SUM(...)/COUNT(*)` and hand you `0`. Multiplying by `1.0` (or `CAST(... AS REAL)`) is the fix.
Getting a column of zeros is the single most common self-inflicted SQL wound in these assessments.

**`HAVING` vs `WHERE`.** `HAVING` filters *after* aggregation, which is what "combinations with at
least 50 accounts" requires. `WHERE` filters rows before grouping and cannot see `COUNT(*)`.

**Modern alternative:** `COUNT(*) FILTER (WHERE a.status = 'charged_off')` reads better and works in
SQLite 3.30+ and Postgres. `SUM(CASE WHEN ...)` is the version that runs everywhere, so it's the one
to reach for when you don't know the grader's engine.

## S2 — Everyone's #1 spending category

```sql
WITH spend AS (
    SELECT a.customer_id,
           t.merchant_category,
           SUM(t.amount) AS cat_spend
    FROM transactions t
    JOIN accounts a ON a.account_id = t.account_id
    WHERE t.amount > 0
      AND t.merchant_category IS NOT NULL
      AND t.txn_ts >= '2025-01-01' AND t.txn_ts < '2026-01-01'
    GROUP BY a.customer_id, t.merchant_category
),
ranked AS (
    SELECT customer_id,
           merchant_category,
           ROW_NUMBER() OVER (PARTITION BY customer_id
                              ORDER BY cat_spend DESC, merchant_category ASC) AS rn
    FROM spend
)
SELECT merchant_category, COUNT(*) AS n_customers
FROM ranked
WHERE rn = 1
GROUP BY merchant_category
ORDER BY n_customers DESC, merchant_category ASC;
```

Reference:

| merchant_category | n_customers |
|---|---|
| Groceries | 1142 |
| Travel | 976 |
| Retail | 889 |
| Restaurants | 320 |
| Utilities | 190 |
| Healthcare | 172 |
| HomeImprovement | 167 |
| Gas | 84 |
| Entertainment | 49 |
| Pharmacy | 9 |

**The aggregate-then-rank-then-filter sandwich** is the shape to memorize. Three CTEs: aggregate to
the grain you want to rank at, apply the window function, filter on the rank. Almost every
"top N per group" question is this.

**`ROW_NUMBER` vs `RANK` vs `DENSE_RANK`.** `ROW_NUMBER` is right here because the spec demands
exactly one winner per customer and gives a deterministic tiebreak. `RANK` would return two rows for
a tied customer and inflate your counts. Know the difference cold — it gets asked verbally too.

**Note the row count: 10, not 12.** Two of the twelve categories are nobody's top category. If your
answer has 12 rows you probably aggregated the wrong thing; if it has 11 or 13, check your tiebreak.
A result having fewer groups than the universe is normal and you should not "fix" it.

## S3 — Month-over-month portfolio spend

```sql
WITH monthly AS (
    SELECT strftime('%Y-%m', txn_ts) AS month,
           ROUND(SUM(amount), 2) AS total_spend
    FROM transactions
    WHERE amount > 0
      AND txn_ts >= '2025-01-01' AND txn_ts < '2026-01-01'
    GROUP BY 1
)
SELECT month,
       total_spend,
       ROUND(100.0 * (total_spend - LAG(total_spend) OVER (ORDER BY month))
             / LAG(total_spend) OVER (ORDER BY month), 2) AS mom_pct_change
FROM monthly
ORDER BY month;
```

Reference:

| month | total_spend | mom_pct_change |
|---|---|---|
| 2025-01 | 621,632.64 | NULL |
| 2025-02 | 572,834.73 | −7.85 |
| 2025-03 | 637,916.07 | 11.36 |
| 2025-04 | 661,807.06 | 3.75 |
| 2025-05 | 693,203.08 | 4.74 |
| 2025-06 | 675,591.38 | −2.54 |
| 2025-07 | 706,389.42 | 4.56 |
| 2025-08 | 738,092.76 | 4.49 |
| 2025-09 | 739,400.37 | 0.18 |
| 2025-10 | 766,065.42 | 3.61 |
| 2025-11 | 804,912.55 | 5.07 |
| 2025-12 | 787,395.45 | −2.18 |

**`LAG` handles the January NULL for you** — there is no previous row, so it returns NULL and the
arithmetic propagates. Don't write a `CASE WHEN month = '2025-01'` special case; that's a tell that
you don't trust window functions.

**Why aggregating in a CTE first is not optional.** `LAG` operates over *result rows*. You need one
row per month before you can lag by a month. You cannot mix `LAG` and `SUM` at the same level here.

**Sanity habit worth having:** February is down 7.85% and it has 28 days. Month-over-month on raw
totals is partly a calendar artifact. Nobody asked, but noticing out loud — "I'd normalize per day,
or compare to the same month last year" — is exactly the instinct the open-ended sections reward.

## S4 — The 30→60 roll rate

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
       COUNT(*) AS n_30dpd,
       SUM(CASE WHEN next_month = date(statement_month, '+1 month')
                 AND next_dpd >= 60 THEN 1 ELSE 0 END) AS n_rolled,
       ROUND(1.0 * SUM(CASE WHEN next_month = date(statement_month, '+1 month')
                             AND next_dpd >= 60 THEN 1 ELSE 0 END) / COUNT(*), 4) AS roll_rate
FROM nxt
WHERE days_past_due = 30
  AND statement_month < '2025-12-01'
GROUP BY 1
ORDER BY month;
```

Reference — 11 rows, roll rate hovering around 0.55–0.60:

| month | n_30dpd | n_rolled | roll_rate |
|---|---|---|---|
| 2025-01 | 164 | 95 | 0.5793 |
| 2025-02 | 160 | 89 | 0.5563 |
| 2025-03 | 164 | 93 | 0.5671 |
| … | | | |
| 2025-11 | 162 | 91 | 0.5617 |

**`LEAD` beats a self-join** when "the next row" is defined by an ordering within a group. A
self-join on `date(a.statement_month, '+1 month')` also works and scores full marks here, but it is
an *inner* join, so accounts with no following statement silently vanish from the denominator. The
spec says they should count as not-rolled — with `LEAD` you keep them and test
`next_month = date(statement_month, '+1 month')` explicitly.

**The `next_month` check is the part people drop.** `LEAD` gives you the next *statement* row, which
is only the next *calendar month* if the account has an unbroken monthly history. Guarding on it is
what separates a query that's right from one that's right on this dataset.

**Numerator vs denominator is the whole metric.** `n_30dpd` counts accounts at exactly 30 DPD; the
denominator is that population, not all accounts. Getting the denominator wrong is the classic roll
rate mistake and an interviewer will absolutely probe it.

## S5 — Consecutive delinquency streaks (gaps and islands)

```sql
WITH cust_month AS (
    SELECT DISTINCT a.customer_id, s.statement_month
    FROM statements s
    JOIN accounts a ON a.account_id = s.account_id
    WHERE s.days_past_due > 0
),
numbered AS (
    SELECT customer_id,
           statement_month,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY statement_month) AS rn
    FROM cust_month
),
islands AS (
    SELECT customer_id,
           date(statement_month, '-' || rn || ' months') AS island,
           COUNT(*) AS streak
    FROM numbered
    GROUP BY customer_id, island
)
SELECT customer_id, MAX(streak) AS longest_streak
FROM islands
GROUP BY customer_id
HAVING MAX(streak) >= 3
ORDER BY longest_streak DESC, customer_id ASC;
```

Reference: 530 rows. Longest streak is 8 months (one customer). Distribution:
3 months → 247 customers, 4 → 267, 5 → 10, 6 → 3, 7 → 2, 8 → 1.

**The trick, stated plainly:** number the qualifying months per customer with `ROW_NUMBER()`. Inside
a run of consecutive months, *month minus row number* is constant. So subtracting `rn` months from
each date produces a synthetic key that is identical for every month in the same island and
different across islands. Group on it and count.

Once you've seen it, it takes 90 seconds. If you haven't, you will burn your whole SQL budget
reinventing it. **This is the highest-leverage SQL pattern to have pre-loaded** — it shows up as
consecutive logins, consecutive months of activity, session-izing events, and streaks of any kind.

**The final `MAX` is not decoration.** A customer can have two separate runs of 3+ months. Without
the outer `GROUP BY customer_id ... MAX(streak)` you emit that customer twice and fail on row count.

**`DISTINCT` in the first CTE matters** because the question is defined at the *customer* level and a
customer can hold several accounts, each with its own statement row for the same month.

---

# Section 3 — Applied machine learning

## M1 — A defensible baseline

```python
LEAKY = ["post_orig_30dpd_count", "recovery_amount_usd"]
DROP  = ["application_id", "app_date", "default_12m"]
CUT   = "2024-07-01"

apps = pd.read_csv(f"{DATA}/credit_applications.csv", parse_dates=["app_date"])
apps["employment_length_years"] = apps["employment_length_years"].replace(-1.0, np.nan)
apps["revolving_utilization"]   = apps["revolving_utilization"].replace(999.0, np.nan)

feats = [c for c in apps.columns if c not in DROP + LEAKY + ["zip3"]]
train, test = apps[apps.app_date < CUT], apps[apps.app_date >= CUT]

num = train[feats].select_dtypes(include=np.number).columns.tolist()
cat = [c for c in feats if c not in num]

pre = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                      ("sc",  StandardScaler())]), num),
    ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                      ("oh",  OneHotEncoder(handle_unknown="ignore"))]), cat),
])
pipe = Pipeline([("pre", pre),
                 ("clf", LogisticRegression(max_iter=3000, class_weight="balanced"))])
pipe.fit(train[feats], train.default_12m)

p = pipe.predict_proba(test[feats])[:, 1]
m1 = {
    "excluded_features": LEAKY,
    "test_roc_auc": round(roc_auc_score(test.default_12m, p), 4),
    "test_pr_auc":  round(average_precision_score(test.default_12m, p), 4),
    "n_train": len(train), "n_test": len(test),
}
```

Reference: ROC-AUC **0.7688**, PR-AUC **0.3633**, n_train 15,007, n_test 4,993.
Gradient boosting and random forest land at 0.75–0.77 on the same setup — the model family barely
matters here, which is itself the lesson.

**The two leaking columns.** `post_orig_30dpd_count` counts delinquencies *after the account was
opened*; `recovery_amount_usd` is money collections clawed back, which by definition only exists once
someone has already defaulted. Neither is knowable on the day the application is decided. Leave them
in and test AUC jumps to **0.987** — a number so good it should frighten you. **Treat an implausibly
high AUC as a bug report, not a result.** That reflex is worth more than any modeling technique in
this section.

**`assigned_credit_limit` is the interesting one.** It's assigned at underwriting, so it is arguably
available at decision time — but it's an *output* of the very decision process you're modeling, which
makes it a proxy for the incumbent underwriter's judgment and causes trouble in production when
policy changes. Dropping it is fine, keeping it is fine, **saying nothing about it is not.** The
grader accepts either; an interviewer wants the sentence.

**The sentinels.** `-1` for unknown employment length and `999` for utilization are not missing
values to pandas — they are numbers, and `SimpleImputer` will sail straight past them. Left alone
they drag a real coefficient toward nonsense. Always profile `min`/`max`/`value_counts()` on numeric
columns before modeling; sentinel values like `-1`, `999`, `-9999` and `1900-01-01` are everywhere in
financial data.

**Why a `Pipeline` rather than fitting the imputer on the full frame.** Scalers and imputers fitted on
train+test leak test-set statistics into training. It rarely changes the headline number much, and it
is still the thing you get marked down for, because it says you don't know where the boundary is.

**Why both ROC-AUC and PR-AUC.** ROC-AUC is insensitive to class balance, which makes it stable and
comparable but also flattering: at an 8% base rate, 0.77 ROC-AUC coexists with 0.36 PR-AUC. PR-AUC
tracks performance on the minority class you actually care about, and its baseline is the base rate
(0.086 here), so 0.36 is roughly 4× lift. Quote both; if you quote one, quote PR-AUC.

## M2 — What a random split costs you

```python
from sklearn.model_selection import train_test_split

rtr, rte = train_test_split(apps, test_size=len(test) / len(apps),
                            random_state=42, stratify=apps.default_12m)
pipe_r = clone(pipe)
pipe_r.fit(rtr[feats], rtr.default_12m)
rand_auc = roc_auc_score(rte.default_12m, pipe_r.predict_proba(rte[feats])[:, 1])

m2 = {
    "random_split_roc_auc": round(rand_auc, 4),
    "time_split_roc_auc":   m1["test_roc_auc"],
    "optimism":             round(rand_auc - m1["test_roc_auc"], 4),
}
```

Reference: random **0.8095**, time **0.7688**, optimism **+0.0407**. Tree models show the same gap
(HGB: 0.805 vs 0.753).

**Four AUC points is not noise, and it is not free.** If you reported the random-split number to a
business partner, every downstream volume and loss forecast would be built on a model that is
measurably worse than advertised the moment it meets new applications.

**What's actually happening.** Two things, and they compound:

1. **Interleaving.** A random split puts H1-2024 and H2-2024 applications in *both* train and test.
   The model gets to see the recent regime during training, which it will never do in production —
   production always predicts forward.
2. **A regime change in H2 2024.** The relationships shift: inquiry velocity becomes a much stronger
   risk signal, FICO separates less, and more of the outcome is simply unexplainable. The time split
   tests squarely inside that harder regime. The random split dilutes it with easy 2023 vintages.

**The general rule:** if the data has a time dimension and the model will be used to predict forward,
split by time. Full stop. For hyperparameter tuning, use `TimeSeriesSplit` rather than `KFold`. And
in credit specifically, hold out the most recent vintage entirely — an "out-of-time" sample is
standard practice and a model-risk reviewer will ask for it by name.

## M3 — Turning the score into a decision

```python
y = test.default_12m.to_numpy()
GOOD, BAD = 240.0, -1650.0

rows = []
for t in np.round(np.arange(0.005, 1.0005, 0.005), 3):
    approve = p < t
    profit  = (approve & (y == 0)).sum() * GOOD + (approve & (y == 1)).sum() * BAD
    rows.append((t, profit / len(y), approve.mean()))

sweep = pd.DataFrame(rows, columns=["t", "profit_per_app", "approval_rate"])
best  = sweep.loc[sweep.profit_per_app.idxmax()]

m3 = {
    "best_threshold":           float(best.t),
    "expected_profit_per_app":  round(float(best.profit_per_app), 2),
    "approval_rate_at_best":    round(float(best.approval_rate), 4),
    "profit_at_approve_all":    round(((y == 0).sum() * GOOD + (y == 1).sum() * BAD) / len(y), 2),
}
```

Reference: threshold 0.44, profit **+\$81.94** per application at a **65.2%** approval rate, versus
**−\$9.83** per application if you approve everyone.

**State the business case in one sentence:** *approving everyone loses about \$10 per application;
this model at a 65% approval rate makes about \$82 — roughly \$92 per application, or \$460k across
this 5,000-application test window.* That sentence is the answer to "so what?", and it is what
separates a data scientist from someone who ran `roc_auc_score`.

**Why the threshold is not 0.5.** The costs are asymmetric — a default costs about 6.9× what a good
account earns — so the break-even default probability is `240 / (240 + 1650) ≈ 0.127`. With
well-calibrated probabilities you'd approve below ~0.127. The reference threshold is 0.44 because
`class_weight="balanced"` deliberately distorts the probabilities away from the true base rate.
**That is the point of the task.** If you want your cutoff to mean what it says, either drop the
class weighting or wrap the model in `CalibratedClassifierCV`. Never assume 0.5.

**What a real answer adds.** The costs aren't constants — expected loss scales with the assigned
credit line and expected revenue with utilization and APR, so in practice you'd optimize
expected dollar profit per account, not per application, and you'd swap the hard cutoff for a
risk-based line assignment. Also: the cutoff was tuned *on the test set*, so \$81.94 is itself
optimistic. You'd pick the threshold on a validation fold and report profit on a held-out slice.
Saying that unprompted is a strong signal.

---

# M4 — Rubric and model answers

Score each of the six **0 / 1 / 2**: 0 = didn't engage or wrong, 1 = correct but generic, 2 = specific
and shows judgment. **12 total. Below 8, this is your weakest area** — and it's the one candidates
neglect most, because it's the only part you can't practice by running code.

Across all six, the marker of a 2 is the same: a **specific mechanism**, a **named trade-off**, and a
**decision you own**. "It depends" scores 0. "It depends on X, here's how I'd decide, here's what I'd
give up" scores 2.

### 1. Leakage

**Looking for:** both columns named; the *reason* framed as a timing test, not a correlation test;
a repeatable procedure.

> I dropped `post_orig_30dpd_count` and `recovery_amount_usd`. Both are measured after the account is
> booked — recoveries only exist once someone has already defaulted — so neither would be populated
> at the moment I have to make the decision. My general procedure is to ask, for every column, "on the
> application date, could this value have been known?", and to get the source system's timestamp for
> anything I'm unsure about. As a backstop I check univariate AUC per feature: anything above roughly
> 0.9 on its own, or a full model above ~0.95 on a problem where 0.75 is the industry norm, is a
> leakage investigation, not a win. I'd also flag `assigned_credit_limit` as borderline — it exists at
> underwriting but it's an output of the current policy, so it encodes the incumbent decision rule.

A 1 names the columns but justifies them by "they were too predictive". A 2 gives the timing test and
a detection routine.

### 2. Model choice

**Looking for:** an actual pick, defended on *regulatory explainability*, with the cost of the pick
stated. Either answer can score 2; refusing to choose cannot.

> Logistic regression on monotonic bins, because ECOA requires specific principal
> reasons on every decline and a linear model on monotone bins gives exact, stable reason
> codes rather than a post-hoc approximation. But I wouldn't accept a large accuracy cost
> for that — I'd measure it first. On this data the logistic regression actually beat gradient
> boosting (0.769 vs 0.754 AUC, about $9 per application at the profit-maximizing cutoff),
> which is common for credit features because they're largely monotone and additive in
> log-odds. If there were a real gap, I'd close it rather than absorb it: monotonic constraints
> on the GBM recovered about half of it here, and beyond that I'd look at an EBM, or use
> the GBM where adverse action doesn't bind — line assignment, pricing, prescreen —
> while keeping the interpretable model on the decline decision.

A 2 answer for GBM exists too: monotonic constraints, SHAP with a documented reason-code mapping, and
a challenger-model framework — as long as it acknowledges the model-risk review burden it creates.

### 3. Imbalance

**Looking for:** an understanding that 8% is *mild*, and a named technique deliberately rejected.

> 8% positive is imbalanced but not extreme, so I didn't resample. I used `class_weight="balanced"`
> to keep the gradient from being dominated by the negative class, and I steered on PR-AUC rather
> than accuracy — accuracy is 92% for a model that predicts "no default" every time. I specifically
> did **not** use SMOTE: it fabricates synthetic minority points by interpolating between neighbours,
> which is poorly behaved with one-hot categoricals and mixed types, and it distorts the predicted
> probabilities, which I need to be meaningful because the decision threshold is derived from dollar
> costs. If I'd resampled at all I'd have recalibrated afterwards.

A 1 says "I used SMOTE / class weights". A 2 explains why probability calibration matters *here* —
because M3 converts probabilities to dollars.

### 4. Fairness

**Looking for:** age identified as a **protected characteristic under ECOA**, `zip3` identified as a
**redlining proxy**, and an answer to the correlated-permitted-variable question.

> Age is a prohibited basis under ECOA — using it directly in a credit decision is not a fairness
> preference, it's a legal exposure, so it comes out. `zip3` I'd also drop: geography is a well-known
> proxy for race and national origin, and a model that learns "this ZIP defaults more" is redlining
> regardless of intent. Dropping the protected variable isn't sufficient, though, because permitted
> variables carry proxy signal. So I'd run disparate impact testing — adverse impact ratio on approval
> rates across proxied demographic groups, using BISG or whatever the compliance team uses — and if a
> permitted variable like utilization showed high correlation with a protected class, I wouldn't
> automatically drop it. I'd document its business justification, test whether a less discriminatory
> alternative achieves comparable performance (that search is itself an expectation under Reg B), and
> take that comparison to fair lending and model risk rather than deciding alone.

A 1 says "I'd remove age and zip because of bias". A 2 knows that removal isn't sufficient, names
disparate impact testing and the less-discriminatory-alternative search, and escalates rather than
deciding unilaterally.

### 5. Monitoring

**Looking for:** the distinction between things you can measure *now* and the outcome you can't
measure for 12 months — plus concrete triggers.

> Daily: score distribution and approval rate, which catch a broken feature pipeline within hours.
> Weekly: PSI on the score and on each top feature against the training distribution — PSI over 0.10
> is investigate, over 0.25 is escalate. Monthly: early performance indicators — first-payment
> default and 30-DPD at 3 and 6 months on book — plus segment-level approval rates for fair lending
> drift. The problem is that the actual target is a 12-month outcome, so I'm flying on leading
> indicators for a year; that's why early-delinquency proxies matter and why I'd hold a champion /
> challenger running in shadow rather than waiting. Retrain triggers: sustained PSI breach, early
> indicators outside their confidence band two months running, or any known policy or population
> change (a new acquisition channel, a pricing change). Rollback if the score distribution shifts
> abruptly, which almost always means a data pipeline defect rather than a genuine change in
> applicants.

A 1 lists "drift, accuracy, retrain periodically". A 2 names the 12-month outcome lag as the central
problem and gives numeric thresholds.

### 6. Highest-value next step

**Looking for:** something that beats "try XGBoost". The best answers target validation quality,
segment behaviour, or the business decision — not the algorithm.

> An out-of-time validation by vintage: retrain on rolling windows and plot test AUC by application
> month. I already know from M2 that there's a 4-point gap between a random and a time-based split,
> which means something changed in H2 2024, and I'd rather understand *what* changed than tune a model
> on top of it. It tells me how fast the model decays, which sets the retrain cadence, and whether
> the degradation is concentrated in a segment or channel I should be handling separately. Model
> tuning is worth maybe a point of AUC here; knowing the model's shelf life changes how it's
> operated.

Also excellent: calibration analysis, since M3's dollar threshold is meaningless on uncalibrated
probabilities; or reframing the objective as expected profit per *account* (scaled by credit line)
rather than per application. "Try XGBoost with Optuna" is a 1 — it's the answer everyone gives, and
on this data it's worth almost nothing.

---

# If you want to re-sit this

```bash
./bootstrap.sh 12345               # new data + matching key, from any seed
cd ../.. && ./new-attempt.sh capital-one-ds
```

Same questions, different numbers. Worth doing once you've read this file, to check that you can
execute the patterns rather than recall the answers.
