"""Reference solutions. Used to build the answer key and to validate the exam."""
import os
import re
import sqlite3
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


# ==========================================================================
# helpers
# ==========================================================================
def parse_amount(s: pd.Series) -> pd.Series:
    t = s.astype("string").str.strip()
    neg = t.str.startswith("(") & t.str.endswith(")")
    t = t.str.replace(r"[()$,\s]", "", regex=True)
    out = pd.to_numeric(t, errors="coerce")
    return out.where(~neg, -out).astype("float64")


def clean_transactions() -> pd.DataFrame:
    tx = pd.read_csv(f"{DATA}/transactions_raw.csv")
    tx = tx.drop_duplicates()
    tx["amount"] = parse_amount(tx["amount"])
    tx["merchant_category"] = (tx["merchant_category"].astype("string")
                               .str.strip().str.lower().replace({"": pd.NA}))
    tx["txn_ts"] = pd.to_datetime(tx["txn_ts"])
    return tx.reset_index(drop=True)


# ==========================================================================
# SECTION 1 -- pandas
# ==========================================================================
def p1():
    tx = clean_transactions()
    return {
        "n_rows": int(len(tx)),
        "n_categories": int(tx["merchant_category"].dropna().nunique()),
        "net_amount": float(round(tx["amount"].sum(), 2)),
        "refund_count": int((tx["amount"] < 0).sum()),
    }


def p2():
    tx = clean_transactions()
    acc = pd.read_csv(f"{DATA}/accounts.csv")
    cus = pd.read_csv(f"{DATA}/customers.csv")

    pur = tx[tx["amount"] > 0]
    m = (pur.merge(acc[["account_id", "customer_id", "product"]], on="account_id", how="inner")
            .merge(cus[["customer_id", "segment"]], on="customer_id", how="inner"))

    g = m.groupby(["segment", "product"], as_index=False).agg(
        n_accounts=("account_id", "nunique"),
        total_spend=("amount", "sum"))
    g["total_spend"] = g["total_spend"].round(2)
    g["spend_per_account"] = (g["total_spend"] / g["n_accounts"]).round(2)
    return (g.sort_values(["segment", "product"])
             .reset_index(drop=True)[["segment", "product", "n_accounts",
                                      "total_spend", "spend_per_account"]])


def p3():
    tx = clean_transactions()
    acc = pd.read_csv(f"{DATA}/accounts.csv")

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

    hit = roll[roll["ratio"] > 1.0]
    first = hit.groupby("account_id", as_index=False)["date"].min()

    return {
        "n_accounts_flagged": int(len(first)),
        "n_flagged_in_q1": int((first["date"] < "2025-04-01").sum()),
        "max_trailing30_ratio": float(round(roll["ratio"].max(), 2)),
    }


def p4():
    tx = clean_transactions()
    acc = pd.read_csv(f"{DATA}/accounts.csv")

    pur = tx[(tx["amount"] > 0) & tx["merchant_category"].notna()]
    m = pur.merge(acc[["account_id", "customer_id"]], on="account_id", how="inner")

    n_pur = m.groupby("customer_id").size().rename("n_purchases")
    eligible = n_pur[n_pur >= 20].index

    m = m[m["customer_id"].isin(eligible)]
    cat = (m.groupby(["customer_id", "merchant_category"], as_index=False)["amount"].sum())
    tot = cat.groupby("customer_id", as_index=False)["amount"].sum().rename(
        columns={"amount": "total"})

    top = (cat.sort_values(["customer_id", "amount", "merchant_category"],
                           ascending=[True, False, True])
              .groupby("customer_id", as_index=False).first())
    top = top.merge(tot, on="customer_id")
    top["share"] = top["amount"] / top["total"]

    return {
        "n_eligible": int(len(eligible)),
        "n_concentrated": int((top["share"] >= 0.35).sum()),
        "top_category": str(top["merchant_category"].value_counts().idxmax()),
        "mean_top_share": float(round(top["share"].mean(), 4)),
    }


# ==========================================================================
# SECTION 2 -- SQL
# ==========================================================================
SQL = {
"S1": """
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
ORDER BY charge_off_rate DESC, segment ASC, product ASC
""",

"S2": """
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
SELECT merchant_category,
       COUNT(*) AS n_customers
FROM ranked
WHERE rn = 1
GROUP BY merchant_category
ORDER BY n_customers DESC, merchant_category ASC
""",

"S3": """
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
ORDER BY month
""",

"S4": """
WITH nxt AS (
    SELECT account_id,
           statement_month,
           days_past_due,
           LEAD(days_past_due)    OVER (PARTITION BY account_id ORDER BY statement_month) AS next_dpd,
           LEAD(statement_month)  OVER (PARTITION BY account_id ORDER BY statement_month) AS next_month
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
ORDER BY month
""",

"S5": """
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
ORDER BY longest_streak DESC, customer_id ASC
""",
}


def run_sql(key):
    con = sqlite3.connect(f"{DATA}/warehouse.db")
    try:
        return pd.read_sql_query(SQL[key], con)
    finally:
        con.close()


# ==========================================================================
# SECTION 3 -- applied ML
# ==========================================================================
LEAKY = ["post_orig_30dpd_count", "recovery_amount_usd"]
NON_FEATURES = ["application_id", "app_date", "default_12m"]
CUT = "2024-07-01"


def _load_apps():
    df = pd.read_csv(f"{DATA}/credit_applications.csv", parse_dates=["app_date"])
    df["employment_length_years"] = df["employment_length_years"].replace(-1.0, np.nan)
    df["revolving_utilization"] = df["revolving_utilization"].replace(999.0, np.nan)
    return df


def _pipeline(X):
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.linear_model import LogisticRegression

    num = X.select_dtypes(include=np.number).columns.tolist()
    cat = [c for c in X.columns if c not in num]
    ct = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                          ("sc", StandardScaler())]), num),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore"))]), cat),
    ])
    return Pipeline([("prep", ct),
                     ("clf", LogisticRegression(max_iter=3000, class_weight="balanced"))])


def m1():
    from sklearn.metrics import roc_auc_score, average_precision_score
    df = _load_apps()
    feats = [c for c in df.columns if c not in NON_FEATURES + LEAKY + ["zip3"]]
    tr, te = df[df.app_date < CUT], df[df.app_date >= CUT]
    pipe = _pipeline(tr[feats])
    pipe.fit(tr[feats], tr["default_12m"])
    p = pipe.predict_proba(te[feats])[:, 1]
    return {
        "excluded_features": LEAKY,
        "test_roc_auc": float(round(roc_auc_score(te["default_12m"], p), 4)),
        "test_pr_auc": float(round(average_precision_score(te["default_12m"], p), 4)),
        "n_train": int(len(tr)),
        "n_test": int(len(te)),
    }, p, te.reset_index(drop=True)


def m2():
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import train_test_split
    df = _load_apps()
    feats = [c for c in df.columns if c not in NON_FEATURES + LEAKY + ["zip3"]]
    tr, te = df[df.app_date < CUT], df[df.app_date >= CUT]
    pipe = _pipeline(tr[feats]); pipe.fit(tr[feats], tr["default_12m"])
    time_auc = roc_auc_score(te["default_12m"], pipe.predict_proba(te[feats])[:, 1])

    rtr, rte = train_test_split(df, test_size=len(te) / len(df), random_state=42,
                                stratify=df["default_12m"])
    pipe2 = _pipeline(rtr[feats]); pipe2.fit(rtr[feats], rtr["default_12m"])
    rand_auc = roc_auc_score(rte["default_12m"], pipe2.predict_proba(rte[feats])[:, 1])
    return {
        "random_split_roc_auc": float(round(rand_auc, 4)),
        "time_split_roc_auc": float(round(time_auc, 4)),
        "optimism": float(round(rand_auc - time_auc, 4)),
    }


PROFIT_GOOD, LOSS_BAD = 240.0, -1650.0


def m3():
    _, p, te = m1()
    y = te["default_12m"].to_numpy()
    n = len(y)
    best_t, best_profit, best_rate = None, -np.inf, None
    for t in np.round(np.arange(0.005, 1.0005, 0.005), 3):
        approve = p < t
        profit = (approve & (y == 0)).sum() * PROFIT_GOOD + (approve & (y == 1)).sum() * LOSS_BAD
        if profit > best_profit:
            best_t, best_profit, best_rate = float(t), float(profit), float(approve.mean())
    approve_all = ((y == 0).sum() * PROFIT_GOOD + (y == 1).sum() * LOSS_BAD) / n
    return {
        "best_threshold": round(best_t, 3),
        "expected_profit_per_app": round(best_profit / n, 2),
        "approval_rate_at_best": round(best_rate, 4),
        "profit_at_approve_all": float(round(approve_all, 2)),
    }


if __name__ == "__main__":
    import json
    print("P1", p1())
    print("P2\n", p2())
    print("P3", p3())
    print("P4", p4())
    for k in SQL:
        d = run_sql(k)
        print(f"{k} shape={d.shape}\n", d.head(6))
    a, _, _ = m1()
    print("M1", a)
    print("M2", m2())
    print("M3", m3())
