"""
Self-check grader for the practice set.

    from grader import check, score
    check("P1", p1)

By default it tells you WHAT is wrong, not what the right answer is.
`check("P1", p1, reveal=True)` shows the expected values -- use it only once
you've genuinely given up on a task, or you'll burn the question.
"""
import base64
import json
import math
import os

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_KEY_PATH = os.path.join(_HERE, "answer_key.b64")

if not os.path.exists(_KEY_PATH):
    raise RuntimeError(
        "No answer key found -- it's generated, not committed.\n"
        f"Run: {os.path.join(_HERE, 'bootstrap.sh')}"
    )

with open(_KEY_PATH, "rb") as _f:
    KEY = json.loads(base64.b64decode(_f.read()).decode("utf-8"))

_RESULTS = {}

_G = "\033[32m"
_R = "\033[31m"
_Y = "\033[33m"
_D = "\033[0m"


def _ok(s):
    return f"{_G}PASS{_D} {s}"


def _no(s):
    return f"{_R}FAIL{_D} {s}"


def _tol(expected):
    if not isinstance(expected, (int, float)) or isinstance(expected, bool):
        return 0.0
    base = 0.006 if abs(expected) >= 1 else 1e-4
    return max(base, 1e-6 * abs(expected))


def _num_eq(got, exp):
    try:
        g = float(got)
    except (TypeError, ValueError):
        return False
    if isinstance(exp, float) and math.isnan(exp):
        return math.isnan(g)
    if math.isnan(g):
        return False
    return abs(g - exp) <= _tol(exp)


def _val_eq(got, exp):
    if exp is None or (isinstance(exp, float) and math.isnan(exp)):
        return got is None or (isinstance(got, float) and math.isnan(got)) or pd.isna(got)
    if isinstance(exp, str):
        return isinstance(got, str) and got.strip().lower() == exp.strip().lower()
    return _num_eq(got, exp)


# --------------------------------------------------------------------------
def _check_dict(name, got, spec, reveal):
    if not isinstance(got, dict):
        print(_no(f"{name}: expected a dict, got {type(got).__name__}"))
        return 0.0
    fields = spec["fields"]
    hits = 0
    for k, want in fields.items():
        if k not in got:
            print(_no(f"{name}.{k}: missing from your answer"))
            continue
        if _val_eq(got[k], want):
            hits += 1
            print(_ok(f"{name}.{k}"))
        else:
            extra = f"   (expected {want!r}, got {got[k]!r})" if reveal else f"   (you have {got[k]!r})"
            print(_no(f"{name}.{k}") + extra)
    unknown = set(got) - set(fields)
    if unknown:
        print(f"{_Y}note{_D} {name}: extra keys ignored: {sorted(unknown)}")
    return hits / len(fields)


def _check_df(name, got, spec, reveal):
    if not isinstance(got, pd.DataFrame):
        print(_no(f"{name}: expected a DataFrame, got {type(got).__name__}"))
        return 0.0

    cols = spec["columns"]
    exp = pd.DataFrame(spec["rows"], columns=cols)

    missing = [c for c in cols if c not in got.columns]
    extra = [c for c in got.columns if c not in cols]
    if missing:
        print(_no(f"{name}: missing column(s) {missing}"))
        return 0.0
    if extra:
        print(f"{_Y}note{_D} {name}: extra column(s) ignored: {extra}")

    g = got[cols].reset_index(drop=True)

    if len(g) != len(exp):
        print(_no(f"{name}: expected {len(exp)} rows, got {len(g)}"))
        if reveal:
            print(exp.to_string())
        return 0.0

    bad_rows, bad_cols = set(), set()
    for i in range(len(exp)):
        for c in cols:
            if not _val_eq(g.at[i, c], exp.at[i, c]):
                bad_rows.add(i)
                bad_cols.add(c)

    if not bad_rows:
        print(_ok(f"{name}: {len(exp)} rows, all values match"))
        return 1.0

    print(_no(f"{name}: {len(bad_rows)}/{len(exp)} row(s) differ; "
              f"first wrong row index {min(bad_rows)}; column(s) involved: {sorted(bad_cols)}"))
    if reveal:
        print("expected:")
        print(exp.to_string())
    return max(0.0, 1.0 - len(bad_rows) / len(exp))


def _check_m1(name, got, spec, reveal):
    if not isinstance(got, dict):
        print(_no(f"{name}: expected a dict"))
        return 0.0
    hits, total = 0, 4

    ex = set(str(c) for c in got.get("excluded_features", []))
    must = set(spec["must_exclude"])
    if must <= ex:
        over = ex - must - set(spec.get("defensible_extra", []))
        if over:
            print(_ok(f"{name}.excluded_features: caught both leaks")
                  + f"   {_Y}(also dropped {sorted(over)} -- defend that in M4){_D}")
        else:
            print(_ok(f"{name}.excluded_features: caught both leaks"))
        hits += 1
    else:
        n = len(must - ex)
        print(_no(f"{name}.excluded_features: {n} leaking feature(s) still in your model. "
                  f"Ask: could I have known this value on the day the application was filed?")
              + (f"   (expected {sorted(must)})" if reveal else ""))

    for k, band in (("test_roc_auc", spec["roc_band"]), ("test_pr_auc", spec["pr_band"])):
        v = got.get(k)
        if v is None:
            print(_no(f"{name}.{k}: missing"))
            continue
        if band[0] <= float(v) <= band[1]:
            hits += 1
            print(_ok(f"{name}.{k} = {float(v):.4f} (in the expected range)"))
        else:
            hi = float(v) > band[1]
            why = ("suspiciously high -- something post-decision is probably still in your features"
                   if hi else "low -- check imputation, encoding, and that you kept the real predictors")
            print(_no(f"{name}.{k} = {float(v):.4f}: {why}")
                  + (f"   (expected {band})" if reveal else ""))

    if _num_eq(got.get("n_train"), spec["n_train"]) and _num_eq(got.get("n_test"), spec["n_test"]):
        hits += 1
        print(_ok(f"{name}: train/test sizes match the required time split"))
    else:
        print(_no(f"{name}: n_train / n_test do not match the required split "
                  f"(train app_date < 2024-07-01, test >= 2024-07-01)")
              + (f"   (expected {spec['n_train']}/{spec['n_test']})" if reveal else ""))
    return hits / total


def _check_m2(name, got, spec, reveal):
    if not isinstance(got, dict):
        print(_no(f"{name}: expected a dict"))
        return 0.0
    hits, total = 0, 3
    for k, band in (("random_split_roc_auc", spec["rand_band"]),
                    ("time_split_roc_auc", spec["time_band"])):
        v = got.get(k)
        if v is not None and band[0] <= float(v) <= band[1]:
            hits += 1
            print(_ok(f"{name}.{k} = {float(v):.4f}"))
        else:
            print(_no(f"{name}.{k} = {v}") + (f"   (expected within {band})" if reveal else ""))
    opt = got.get("optimism")
    if opt is not None and float(opt) >= spec["optimism_min"]:
        hits += 1
        print(_ok(f"{name}.optimism = {float(opt):.4f} -- you measured the gap, which is the point"))
    else:
        print(_no(f"{name}.optimism = {opt}: the random split should look "
                  f"meaningfully better than the honest one"))
    return hits / total


def _check_m3(name, got, spec, reveal):
    if not isinstance(got, dict):
        print(_no(f"{name}: expected a dict"))
        return 0.0
    hits, total = 0, 3

    if _num_eq(got.get("profit_at_approve_all"), spec["approve_all"]):
        hits += 1
        print(_ok(f"{name}.profit_at_approve_all (this one is model-independent)"))
    else:
        print(_no(f"{name}.profit_at_approve_all: recompute it straight from the test labels")
              + (f"   (expected {spec['approve_all']})" if reveal else ""))

    p = got.get("expected_profit_per_app")
    lo, hi = spec["profit_band"]
    if p is not None and lo <= float(p) <= hi:
        hits += 1
        print(_ok(f"{name}.expected_profit_per_app = {float(p):.2f}"))
    else:
        print(_no(f"{name}.expected_profit_per_app = {p}")
              + (f"   (expected within {spec['profit_band']})" if reveal else
                 "   (a sound model + threshold sweep turns a loss-making book profitable)"))

    r = got.get("approval_rate_at_best")
    rlo, rhi = spec["rate_band"]
    if r is not None and rlo <= float(r) <= rhi:
        hits += 1
        print(_ok(f"{name}.approval_rate_at_best = {float(r):.4f}"))
    else:
        print(_no(f"{name}.approval_rate_at_best = {r}")
              + (f"   (expected within {spec['rate_band']})" if reveal else ""))

    print(f"{_Y}note{_D} {name}.best_threshold is not graded -- its value depends on how your "
          f"model is calibrated (class_weight, model family). The profit is what matters.")
    return hits / total


_DISPATCH = {"dict": _check_dict, "df": _check_df,
             "m1": _check_m1, "m2": _check_m2, "m3": _check_m3}


def check(task, answer, reveal=False):
    """Grade one task. `task` is 'P1'..'P4', 'S1'..'S5', 'M1'..'M3'."""
    task = task.upper().strip()
    if task not in KEY:
        print(_no(f"unknown task {task!r}. Valid: {', '.join(KEY)}"))
        return
    spec = KEY[task]
    print(f"--- {task} " + "-" * (60 - len(task)))
    frac = _DISPATCH[spec["kind"]](task, answer, spec, reveal)
    _RESULTS[task] = frac
    print(f"    {task} score: {frac * 100:.0f}%\n")


def score():
    """Summary of everything you've checked so far."""
    order = [k for k in KEY if k in _RESULTS]
    if not order:
        print("Nothing checked yet.")
        return
    print("=" * 52)
    print(f"{'task':6s} {'score':>7s}   section")
    print("-" * 52)
    sec = {"P": "pandas", "S": "SQL", "M": "applied ML"}
    by_sec = {}
    for k in order:
        print(f"{k:6s} {_RESULTS[k] * 100:6.0f}%   {sec[k[0]]}")
        by_sec.setdefault(k[0], []).append(_RESULTS[k])
    print("-" * 52)
    for s, vals in by_sec.items():
        print(f"{sec[s]:>12s}: {np.mean(vals) * 100:5.0f}%  ({len(vals)} graded)")
    print(f"{'OVERALL':>12s}: {np.mean([_RESULTS[k] for k in order]) * 100:5.0f}%")
    print("=" * 52)
    print("M4 is not auto-graded -- score it against the rubric in SOLUTIONS.md.")


def tasks():
    return list(KEY)
