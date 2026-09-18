"""Builds answer_key.b64 from the reference solutions."""
import base64
import json
import math
import os

import numpy as np
import pandas as pd

import solutions_ref as R
import drills_sql as D

HERE = os.path.dirname(os.path.abspath(__file__))


def jsonable(v):
    if v is None:
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        v = float(v)
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, (pd.Timestamp,)):
        return str(v.date())
    return v


def df_spec(df):
    df = df.reset_index(drop=True)
    return {
        "kind": "df",
        "columns": list(df.columns),
        "rows": [[jsonable(v) for v in row] for row in df.itertuples(index=False, name=None)],
    }


def dict_spec(d):
    return {"kind": "dict", "fields": {k: jsonable(v) for k, v in d.items()}}


def main():
    key = {}

    key["P1"] = dict_spec(R.p1())
    key["P2"] = df_spec(R.p2())
    key["P3"] = dict_spec(R.p3())
    key["P4"] = dict_spec(R.p4())

    for s in ["S1", "S2", "S3", "S4", "S5"]:
        key[s] = df_spec(R.run_sql(s))

    for d in D.SQL:
        key[d] = df_spec(D.run(d))

    m1, _, _ = R.m1()
    key["M1"] = {
        "kind": "m1",
        "must_exclude": R.LEAKY,
        "defensible_extra": ["zip3", "state", "applicant_age", "assigned_credit_limit"],
        "roc_band": [0.720, 0.820],
        "pr_band": [0.270, 0.470],
        "n_train": m1["n_train"],
        "n_test": m1["n_test"],
    }

    m2 = R.m2()
    key["M2"] = {
        "kind": "m2",
        "rand_band": [0.770, 0.860],
        "time_band": [0.720, 0.820],
        "optimism_min": 0.010,
    }

    m3 = R.m3()
    key["M3"] = {
        "kind": "m3",
        "approve_all": m3["profit_at_approve_all"],
        "profit_band": [55.0, 115.0],
        "rate_band": [0.45, 0.85],
    }

    blob = base64.b64encode(json.dumps(key).encode("utf-8"))
    with open(os.path.join(HERE, "answer_key.b64"), "wb") as f:
        f.write(blob)

    print(f"answer_key.b64 written ({len(blob)/1024:.1f} KB)")
    print("reference M1:", m1)
    print("reference M2:", m2)
    print("reference M3:", m3)


if __name__ == "__main__":
    main()
