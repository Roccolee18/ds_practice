# Capital One Data Scientist — 80-minute practice assessment

A timed, self-grading practice set for the CodeSignal-style online assessment used for Capital One's
Associate / New Grad Data Scientist roles. Weighted toward SQL and open-ended applied ML.

## Run it

From the repo root:

```bash
pip install -r requirements.txt
./sets/capital-one-ds/bootstrap.sh    # generates data/ + answer_key.b64 (both gitignored)
./new-attempt.sh capital-one-ds       # stamps a dated folder under attempts/
```

Then set an 80-minute timer and open the `exam.ipynb` it created. The notebook locates this set on
its own, so it works from `attempts/` as well as in place. No internet needed.

## What's here

| file | what it is |
|---|---|
| `practice_exam.ipynb` | The blank template — 12 graded tasks + 1 written task, 80 minutes. Don't work in it directly; `new-attempt.sh` copies it |
| `sql_drills.ipynb` | **18 graduated SQL drills**, ~95 min. Start here if SQL syntax isn't automatic yet — work them before re-sitting Section 2 |
| `DRILLS_SOLUTIONS.md` | Worked solutions + what each drill is really testing |
| `MCQ_BANK.md` | **40 multiple-choice questions** — probability, statistics, ML fundamentals — with worked explanations. There's an interactive version for drilling; this is the reference sheet |
| `mcq_bank.py`, `make_mcq_quiz.py` | The MCQ source of truth and the quiz-page generator |
| `SOLUTIONS.md` | Full worked solutions, the trap behind each task, and the M4 rubric — **don't open until the timer stops** |
| `grader.py` | `check("P1", p1)` tells you *that* you're wrong and roughly where, without giving the answer away. `score()` for the summary |
| `answer_key.b64` | Obfuscated expected values. Peeking is possible and pointless. **Generated, gitignored** |
| `data/` | The datasets (below). **Generated, gitignored** — `bootstrap.sh` rebuilds them |
| `bootstrap.sh` | Rebuilds `data/` + `answer_key.b64` together, from a seed |
| `generate_data.py`, `solutions_ref.py`, `make_key.py`, `make_notebook.py` | The generators `bootstrap.sh` drives. `solutions_ref.py` is the reference implementation — same spoilers as `SOLUTIONS.md`, so leave it shut too |

## The data

A synthetic credit card portfolio — 4,000 customers, 4,892 accounts, 112k transactions in 2025,
55k monthly statements, and 20k credit applications from 2023–2024 with 12-month default outcomes.

| file | rows | notes |
|---|---|---|
| `data/transactions_raw.csv` | 113,111 | **raw extract, deliberately dirty**: text amounts, accounting negatives, casing chaos, duplicate rows |
| `data/customers.csv` | 4,000 | segment, state, income (has nulls), bureau score |
| `data/accounts.csv` | 4,892 | product, credit limit, APR, open/closed/charged_off |
| `data/statements.csv` | 55,049 | account × month, with a realistic delinquency roll chain |
| `data/credit_applications.csv` | 20,000 | the ML dataset: 7.9% default rate, coded-missing sentinels, **two leaking columns**, and a genuine regime change in H2 2024 |
| `data/warehouse.db` | — | SQLite: clean, typed versions of the first four, for the SQL section |

## Structure

| | tasks | budget | covers |
|---|---|---|---|
| **1. pandas** | P1–P4 | 20 min | parsing a dirty extract, groupby/merge, time-based rolling windows, share-of-wallet reshaping |
| **2. SQL** | S1–S5 | 30 min | `HAVING`, `ROW_NUMBER` top-N-per-group, `LAG`/`LEAD` MoM change, delinquency roll rate, gaps-and-islands streaks |
| **3. Applied ML** | M1–M4 | 30 min | target leakage, time-based vs random split, class imbalance, cost-based threshold selection, and a written section on model choice, ECOA fair lending, and monitoring |

## How to use it

1. **Set a timer for 80 minutes and don't stop it.** Move on when a section's budget is up.
2. Docs are fine. `SOLUTIONS.md` is not, until you're done.
3. Run `check(...)` as you go — treat a FAIL like a failing hidden test and debug it yourself.
4. Run `score()` at the end for the per-section breakdown.
5. Then read `SOLUTIONS.md` in full, including the tasks you passed. Grade M4 against the rubric.

Rough calibration: **≥85%** with time left over is good shape; **65–85%** is competitive, go drill
your weak section; **<65%** means a specific named gap, which the breakdown will point at.

## A note on scope

This is modeled on CodeSignal's published Data Science Framework (90 minutes; data collection, data
processing, model development and evaluation) and on Capital One's domain — cards, credit risk, unit
economics, and the fair-lending constraints a regulated lender works under. Capital One does not
publish its question bank, and the format varies by role and year. Treat this as high-probability
coverage of the *skills*, not a leaked copy of the test. Two things worth knowing that this set
can't simulate: the real assessment may include multiple-choice probability and statistics items, and
later interview rounds at Capital One lean heavily on a **business case / unit economics** problem
done out loud — practice that separately.
