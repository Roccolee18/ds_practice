"""
Generates the synthetic Capital One-style dataset bundle for the practice exam.

Raw CSVs are deliberately messy (the way an extract from a source system is).
warehouse.db is the clean, typed version (the way a warehouse is), so the SQL
section is about query logic, not string surgery.
"""
import os
import sqlite3
import numpy as np
import pandas as pd

SEED = int(os.environ.get("SEED", 20260917))
RNG = np.random.default_rng(SEED)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT, exist_ok=True)

N_CUST = 4000
N_TXN = 112_437
N_APPS = 20_000

STATES = ["VA", "TX", "NY", "CA", "FL", "IL", "NJ", "PA", "OH", "GA", "NC", "MD", "WA", "AZ", "MA"]
STATE_W = np.array([12, 11, 9, 11, 8, 6, 5, 5, 5, 5, 5, 5, 4, 4, 5], dtype=float)
STATE_W /= STATE_W.sum()

SEGMENTS = ["Mass", "Affluent", "Student", "SmallBusiness"]
SEG_W = [0.55, 0.20, 0.15, 0.10]

CATEGORIES = ["Groceries", "Restaurants", "Travel", "Gas", "Retail", "Entertainment",
              "Utilities", "Healthcare", "Streaming", "HomeImprovement", "Rideshare", "Pharmacy"]
CAT_W = np.array([16, 15, 7, 10, 14, 6, 8, 5, 5, 4, 5, 5], dtype=float)
CAT_W /= CAT_W.sum()


# --------------------------------------------------------------------------
# customers
# --------------------------------------------------------------------------
def make_customers():
    cid = [f"C{100000 + i}" for i in range(N_CUST)]
    seg = RNG.choice(SEGMENTS, size=N_CUST, p=SEG_W)

    signup = pd.to_datetime("2021-01-01") + pd.to_timedelta(RNG.integers(0, 1460, N_CUST), unit="D")

    age = np.where(seg == "Student",
                   RNG.integers(18, 26, N_CUST),
                   np.clip(RNG.normal(44, 14, N_CUST), 22, 84).astype(int))

    base_inc = {"Mass": 10.95, "Affluent": 11.85, "Student": 9.7, "SmallBusiness": 11.3}
    mu = np.array([base_inc[s] for s in seg])
    income = np.round(np.exp(RNG.normal(mu, 0.42)), -2)

    base_fico = {"Mass": 690, "Affluent": 758, "Student": 655, "SmallBusiness": 712}
    fmu = np.array([base_fico[s] for s in seg])
    fico = np.clip(RNG.normal(fmu, 52), 520, 840).astype(int)

    df = pd.DataFrame({
        "customer_id": cid,
        "signup_date": signup.strftime("%Y-%m-%d"),
        "state": RNG.choice(STATES, size=N_CUST, p=STATE_W),
        "age": age,
        "segment": seg,
        "annual_income": income.astype(float),
        "credit_score_at_signup": fico.astype(float),
    })

    # missingness
    df.loc[RNG.random(N_CUST) < 0.07, "annual_income"] = np.nan
    df.loc[RNG.random(N_CUST) < 0.03, "credit_score_at_signup"] = np.nan
    return df


# --------------------------------------------------------------------------
# accounts
# --------------------------------------------------------------------------
PRODUCTS = ["Quicksilver", "Venture", "Savor", "PlatinumSecured"]


def make_accounts(cust):
    rows = []
    n_acct = np.where(RNG.random(len(cust)) < 0.22, 2, 1)
    counter = 0
    for (_, c), k in zip(cust.iterrows(), n_acct):
        for _ in range(k):
            counter += 1
            seg = c["segment"]
            if seg == "Student":
                prod = RNG.choice(PRODUCTS, p=[0.30, 0.05, 0.15, 0.50])
            elif seg == "Affluent":
                prod = RNG.choice(PRODUCTS, p=[0.30, 0.50, 0.18, 0.02])
            elif seg == "SmallBusiness":
                prod = RNG.choice(PRODUCTS, p=[0.40, 0.35, 0.20, 0.05])
            else:
                prod = RNG.choice(PRODUCTS, p=[0.42, 0.18, 0.28, 0.12])

            signup = pd.Timestamp(c["signup_date"])
            open_date = signup + pd.Timedelta(days=int(RNG.integers(0, 400)))
            if open_date > pd.Timestamp("2025-11-01"):
                open_date = pd.Timestamp("2025-11-01")

            fico = c["credit_score_at_signup"]
            fico = 690.0 if pd.isna(fico) else float(fico)
            lim_base = 200 * np.exp((fico - 600) / 110)
            if prod == "PlatinumSecured":
                lim_base = min(lim_base, 1500)
            if prod == "Venture":
                lim_base *= 1.5
            limit = float(np.clip(np.round(lim_base * RNG.uniform(0.75, 1.3), -2), 300, 35000))

            apr = float(np.round(np.clip(31.0 - (fico - 520) * 0.028 + RNG.normal(0, 1.1), 14.9, 30.9), 2))

            r = RNG.random()
            risk = 1.0 / (1.0 + np.exp((fico - 660) / 45.0))
            if r < 0.035 + 0.06 * risk:
                status = "charged_off"
            elif r < 0.12 + 0.06 * risk:
                status = "closed"
            else:
                status = "open"

            rows.append({
                "account_id": f"A{2000000 + counter}",
                "customer_id": c["customer_id"],
                "product": prod,
                "open_date": open_date.strftime("%Y-%m-%d"),
                "credit_limit": limit,
                "apr": apr,
                "status": status,
            })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# transactions (2025)
# --------------------------------------------------------------------------
def make_transactions(acct, cust):
    m = acct.merge(cust[["customer_id", "segment"]], on="customer_id", how="left")
    # spend propensity
    w = np.ones(len(m))
    w *= np.where(m["segment"] == "Affluent", 2.0, 1.0)
    w *= np.where(m["segment"] == "Student", 0.55, 1.0)
    w *= np.where(m["segment"] == "SmallBusiness", 1.6, 1.0)
    w *= np.where(m["status"] == "open", 1.0, 0.45)
    w = w / w.sum()

    idx = RNG.choice(len(m), size=N_TXN, p=w)
    acct_ids = m["account_id"].to_numpy()[idx]
    seg_of = m["segment"].to_numpy()[idx]
    open_dt = pd.to_datetime(m["open_date"]).to_numpy()[idx]

    start = np.maximum(open_dt, np.datetime64("2025-01-01"))
    span_days = (np.datetime64("2025-12-31") - start).astype("timedelta64[D]").astype(int)
    span_days = np.maximum(span_days, 1)
    offset = (RNG.random(N_TXN) * span_days).astype(int)
    ts = pd.to_datetime(start) + pd.to_timedelta(offset, unit="D") \
        + pd.to_timedelta(RNG.integers(0, 86400, N_TXN), unit="s")

    cat = RNG.choice(CATEGORIES, size=N_TXN, p=CAT_W)

    cat_mu = {"Groceries": 4.15, "Restaurants": 3.75, "Travel": 4.85, "Gas": 3.70, "Retail": 4.20,
              "Entertainment": 3.80, "Utilities": 4.05, "Healthcare": 4.35, "Streaming": 2.60,
              "HomeImprovement": 4.50, "Rideshare": 2.95, "Pharmacy": 3.40}
    mu = np.array([cat_mu[c] for c in cat])
    mu = mu + np.where(seg_of == "Affluent", 0.35, 0.0) + np.where(seg_of == "Student", -0.3, 0.0)
    amount = np.round(np.exp(RNG.normal(mu, 0.62)), 2)
    amount = np.clip(amount, 1.0, 12000.0)

    # refunds
    refund = RNG.random(N_TXN) < 0.03
    amount = np.where(refund, -np.round(amount * RNG.uniform(0.2, 1.0, N_TXN), 2), amount)

    df = pd.DataFrame({
        "transaction_id": [f"T{500000000 + i}" for i in range(N_TXN)],
        "account_id": acct_ids,
        "txn_ts": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "amount_true": amount,
        "merchant_category_true": cat,
        "merchant_id": [f"M{n:04d}" for n in RNG.integers(1000, 9999, N_TXN)],
        "channel": RNG.choice(["online", "in_store"], size=N_TXN, p=[0.46, 0.54]),
        "is_disputed": (RNG.random(N_TXN) < 0.012).astype(int),
    })

    # ---------------- messy raw version ----------------
    raw = df.copy()

    def fmt(a):
        style = RNG.integers(0, 5)
        if a < 0:
            # accounting-style negatives for some refunds
            return f"(${abs(a):,.2f})" if style < 3 else f"{a:.2f}"
        if style == 0:
            return f"${a:,.2f}"
        if style == 1:
            return f"{a:,.2f}"
        if style == 2:
            return f"  {a:.2f} "
        return f"{a:.2f}"

    raw["amount"] = [fmt(a) for a in raw["amount_true"]]

    def mess_cat(c):
        style = RNG.integers(0, 4)
        if style == 0:
            return c.upper()
        if style == 1:
            return c.lower()
        if style == 2:
            return f" {c} "
        return c

    raw["merchant_category"] = [mess_cat(c) for c in raw["merchant_category_true"]]
    null_cat = RNG.random(N_TXN) < 0.02
    raw.loc[null_cat, "merchant_category"] = np.nan

    raw = raw[["transaction_id", "account_id", "txn_ts", "amount",
               "merchant_category", "merchant_id", "channel", "is_disputed"]]

    # exact duplicate rows (same transaction_id, identical payload)
    dup_idx = RNG.choice(len(raw), size=int(0.006 * len(raw)), replace=False)
    raw_out = pd.concat([raw, raw.iloc[dup_idx]], ignore_index=True)
    raw_out = raw_out.sample(frac=1.0, random_state=7).reset_index(drop=True)

    clean = df.rename(columns={"amount_true": "amount", "merchant_category_true": "merchant_category"})
    clean = clean[["transaction_id", "account_id", "txn_ts", "amount",
                   "merchant_category", "merchant_id", "channel", "is_disputed"]]
    # the warehouse also loses the category where the source was null
    clean.loc[null_cat, "merchant_category"] = None
    return raw_out, clean


# --------------------------------------------------------------------------
# statements (monthly, 2025) with a delinquency Markov chain
# --------------------------------------------------------------------------
def make_statements(acct, cust):
    m = acct.merge(cust[["customer_id", "credit_score_at_signup"]], on="customer_id", how="left")
    months = pd.date_range("2025-01-01", "2025-12-01", freq="MS")
    rows = []
    sid = 0
    for r in m.itertuples(index=False):
        open_dt = pd.Timestamp(r.open_date)
        fico = 690.0 if pd.isna(r.credit_score_at_signup) else float(r.credit_score_at_signup)
        risk = 1.0 / (1.0 + np.exp((fico - 645) / 40.0))
        p_enter = 0.010 + 0.085 * risk
        if r.status == "charged_off":
            p_enter *= 3.2

        state = 0
        bal = float(r.credit_limit) * RNG.uniform(0.05, 0.55)
        charged_off_at = None
        for mo in months:
            if mo < open_dt.to_period("M").to_timestamp():
                continue
            if charged_off_at is not None:
                break

            spend = float(r.credit_limit) * RNG.uniform(0.02, 0.22)
            bal = max(0.0, bal + spend)
            bal = min(bal, float(r.credit_limit) * 1.05)

            if state == 0:
                state = 30 if RNG.random() < p_enter else 0
            else:
                p_cure = 0.52 - 0.22 * risk
                if RNG.random() < p_cure:
                    state = 0
                else:
                    state = min(state + 30, 120)

            min_due = round(max(25.0, bal * 0.02), 2)
            if state == 0:
                payment = round(min_due * RNG.uniform(1.0, 6.0), 2)
                payment = min(payment, round(bal, 2))
            else:
                payment = round(min_due * RNG.uniform(0.0, 0.4), 2)
            bal = max(0.0, bal - payment)

            rows.append({
                "statement_id": f"S{7000000 + sid}",
                "account_id": r.account_id,
                "statement_month": mo.strftime("%Y-%m-%d"),
                "statement_balance": round(bal, 2),
                "min_payment_due": min_due,
                "payment_made": payment,
                "days_past_due": int(state),
            })
            sid += 1

            if state >= 120:
                charged_off_at = mo
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# credit applications (the ML dataset)
# --------------------------------------------------------------------------
def make_applications():
    n = N_APPS
    app_date = pd.to_datetime("2023-01-01") + pd.to_timedelta(RNG.integers(0, 730, n), unit="D")
    year = app_date.year.to_numpy()

    product = RNG.choice(PRODUCTS, size=n, p=[0.40, 0.22, 0.26, 0.12])
    channel = RNG.choice(["online", "branch", "partner", "direct_mail"], size=n, p=[0.52, 0.16, 0.20, 0.12])

    fico = np.clip(RNG.normal(688, 62, n), 500, 840).round().astype(float)
    age = np.clip(RNG.normal(42, 14, n), 18, 82).round().astype(int)
    income = np.round(np.exp(RNG.normal(10.95 + 0.0015 * (fico - 688), 0.48, n)), -2)
    dti = np.clip(RNG.normal(0.28, 0.11, n) - 0.00035 * (fico - 688), 0.01, 0.85).round(4)
    emp_len = np.clip(RNG.gamma(2.0, 2.6, n), 0, 30).round(1)
    inq = RNG.poisson(np.clip(2.4 - 0.012 * (fico - 688), 0.3, 9), n)
    util = np.clip(RNG.beta(2.0, 3.2, n) * 1.25 - 0.0015 * (fico - 688), 0.0, 1.6).round(4)
    delinq = RNG.poisson(np.clip(0.55 - 0.004 * (fico - 688), 0.02, 4), n)
    home = RNG.choice(["RENT", "MORTGAGE", "OWN", "OTHER"], size=n, p=[0.42, 0.40, 0.14, 0.04])
    state = RNG.choice(STATES, size=n, p=STATE_W)
    zip3 = RNG.integers(100, 999, n)
    requested = np.round(np.clip(RNG.lognormal(8.3, 0.55, n), 500, 40000), -2)

    def z(x):
        x = np.asarray(x, dtype=float)
        return (x - np.nanmean(x)) / np.nanstd(x)

    # 2024 is a different credit regime: FICO discriminates less, utilization more.
    # A random train/test split hides this; a time-based split exposes it.
    is24 = (year == 2024).astype(float)
    # a credit shock lands in H2 2024: inquiry velocity starts mattering much more
    # and FICO separates less. This is the regime the time-based test set lives in.
    shock = np.asarray(app_date >= pd.Timestamp("2024-07-01"), dtype=float)
    logit = (-4.05
             + (-1.00 + 0.25 * is24 + 0.40 * shock) * z(fico)
             + (0.45 + 0.40 * is24) * z(util)
             + 0.40 * z(dti)
             + (0.25 + 0.55 * shock) * z(inq)
             + 0.44 * z(delinq)
             - 0.20 * z(np.log(income))
             - 0.10 * z(emp_len)
             + 0.28 * is24                                # vintage drift
             + 0.18 * (channel == "direct_mail")
             + 0.12 * (product == "PlatinumSecured")
             - 0.10 * (home == "OWN")
             + RNG.normal(0, 1.00 + 1.15 * shock, n))
    p = 1.0 / (1.0 + np.exp(-logit))
    y = (RNG.random(n) < p).astype(int)

    # ---- leakage: measured AFTER the account was booked ----
    post_30dpd = RNG.poisson(np.where(y == 1, 2.6, 0.06))
    recovery = np.where((y == 1) & (RNG.random(n) < 0.55),
                        np.round(RNG.lognormal(6.0, 0.7, n), 2), 0.0)

    df = pd.DataFrame({
        "application_id": [f"AP{900000 + i}" for i in range(n)],
        "app_date": app_date.strftime("%Y-%m-%d"),
        "requested_product": product,
        "channel": channel,
        "applicant_age": age,
        "state": state,
        "zip3": zip3,
        "fico_score": fico,
        "annual_income": income,
        "dti_ratio": dti,
        "employment_length_years": emp_len,
        "num_inquiries_6m": inq,
        "revolving_utilization": util,
        "delinq_2yrs": delinq,
        "home_ownership": home,
        "requested_amount": requested,
        "assigned_credit_limit": np.round(np.clip(requested * RNG.uniform(0.3, 1.0, n), 300, 35000), -2),
        "post_orig_30dpd_count": post_30dpd,
        "recovery_amount_usd": recovery,
        "default_12m": y,
    })

    # realistic dirt
    df.loc[RNG.random(n) < 0.08, "annual_income"] = np.nan
    df.loc[RNG.random(n) < 0.03, "home_ownership"] = np.nan
    # -1 sentinel for unknown employment length (NOT NaN -- a classic trap)
    df.loc[RNG.random(n) < 0.06, "employment_length_years"] = -1.0
    # a few utilization outliers recorded as 999
    df.loc[RNG.random(n) < 0.004, "revolving_utilization"] = 999.0

    return df.sort_values("app_date").reset_index(drop=True)


# --------------------------------------------------------------------------
def main():
    cust = make_customers()
    acct = make_accounts(cust)
    raw_txn, clean_txn = make_transactions(acct, cust)
    stmt = make_statements(acct, cust)
    apps = make_applications()

    cust.to_csv(f"{OUT}/customers.csv", index=False)
    acct.to_csv(f"{OUT}/accounts.csv", index=False)
    raw_txn.to_csv(f"{OUT}/transactions_raw.csv", index=False)
    stmt.to_csv(f"{OUT}/statements.csv", index=False)
    apps.to_csv(f"{OUT}/credit_applications.csv", index=False)

    db = f"{OUT}/warehouse.db"
    if os.path.exists(db):
        os.remove(db)
    con = sqlite3.connect(db)
    cust.to_sql("customers", con, index=False)
    acct.to_sql("accounts", con, index=False)
    clean_txn.to_sql("transactions", con, index=False)
    stmt.to_sql("statements", con, index=False)
    con.executescript("""
        CREATE INDEX idx_txn_acct ON transactions(account_id);
        CREATE INDEX idx_acct_cust ON accounts(customer_id);
        CREATE INDEX idx_stmt_acct ON statements(account_id, statement_month);
    """)
    con.commit()
    con.close()

    print("customers          ", cust.shape)
    print("accounts           ", acct.shape)
    print("transactions_raw   ", raw_txn.shape, "| clean:", clean_txn.shape)
    print("statements         ", stmt.shape)
    print("credit_applications", apps.shape, "| default rate:", round(apps.default_12m.mean(), 4))
    print("dpd distribution   ", stmt.days_past_due.value_counts().to_dict())
    with open(f"{OUT}/SEED", "w") as fh:
        fh.write(f"{SEED}\n")

    print(f"seed               {SEED}")
    for f in sorted(os.listdir(OUT)):
        print(f"  {f:28s} {os.path.getsize(os.path.join(OUT, f))/1e6:8.2f} MB")


if __name__ == "__main__":
    main()
