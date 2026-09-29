"""
Practice harness for the "floor of average revenue per city" question.

    python3 city_revenue_practice.py          # builds the DB, prints both tables

    # ...or from a notebook / REPL, in the same folder:
    from city_revenue_practice import q, check
    df = q('''
        SELECT ...
    ''')
    check(df)

The dataset is small (8 cities, 15 revenue rows) but every row is there to catch a
specific mistake. Write the query cold, run check(), and only then read WHAT_TO_WATCH
at the bottom of this file.
"""
import os
import sqlite3

import pandas as pd

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "city_revenue.db")

DDL = """
DROP TABLE IF EXISTS REVENUE;
DROP TABLE IF EXISTS CITIES;

CREATE TABLE CITIES (
    CITY_CODE INTEGER PRIMARY KEY,   -- the city's PINCODE
    CITY_NAME TEXT    NOT NULL
);

CREATE TABLE REVENUE (
    CITY_CODE INTEGER NOT NULL,      -- one row per agency estimate
    REVENUE   INTEGER NOT NULL
);
"""

CITIES = [
    (110001, "Delhi"),
    (400001, "Mumbai"),
    (560001, "Bengaluru"),
    (600001, "Chennai"),
    (700001, "Kolkata"),       # no agency has filed an estimate
    (452001, "Indore"),
    (431001, "Aurangabad"),    # Maharashtra
    (824101, "Aurangabad"),    # Bihar -- same name, different pincode
]

REVENUE = [
    (110001, 100), (110001, 200), (110001, 305),   # avg 201.666...
    (400001, 500), (400001, 700),                  # avg 600.0  exactly
    (560001,   1), (560001,   2),                  # avg 1.5
    (600001, 999),                                 # single estimate
    (452001,  -5), (452001,   2),                  # avg -1.5
    (431001, 300), (431001, 400),                  # avg 350.0
    (824101,  10), (824101,  20),                  # avg 15.0
    (999999, 50000),                               # orphan: no such city
]


def build(path=DB):
    con = sqlite3.connect(path)
    con.executescript(DDL)
    con.executemany("INSERT INTO CITIES  VALUES (?, ?)", CITIES)
    con.executemany("INSERT INTO REVENUE VALUES (?, ?)", REVENUE)
    con.commit()
    return con


_CON = None


def conn():
    global _CON
    if _CON is None:
        _CON = build()
    return _CON


def q(sql):
    """Run a query, return a DataFrame."""
    return pd.read_sql(sql, conn())


# --------------------------------------------------------------------------
_EXPECTED = {
    ("Delhi",       201),
    ("Mumbai",      600),
    ("Bengaluru",     1),
    ("Chennai",     999),
    ("Indore",       -2),
    ("Aurangabad",  350),
    ("Aurangabad",   15),
}


def check(df, reveal=False):
    """Grade a result. Column names and row order don't matter; values do."""
    G, R, D = "\033[32m", "\033[31m", "\033[0m"
    if not isinstance(df, pd.DataFrame):
        print(f"{R}FAIL{D} expected a DataFrame, got {type(df).__name__}")
        return
    if df.shape[1] != 2:
        print(f"{R}FAIL{D} expected 2 columns (name, floored average), got {df.shape[1]}")
        return

    got = []
    for name, val in df.itertuples(index=False):
        if pd.isna(val):
            got.append((str(name), None)); continue
        f = float(val)
        got.append((str(name), int(f) if f == int(f) else f))
    got_set, exp_set = set(got), set(_EXPECTED)

    if len(got) != len(got_set):
        print(f"{R}note{D} your result has duplicate rows")

    missing, extra = exp_set - got_set, got_set - exp_set
    if not missing and not extra:
        print(f"{G}PASS{D}  {len(got)} rows, all correct")
        return

    print(f"{R}FAIL{D}  {len(got)} rows returned, {len(_EXPECTED)} expected")
    for n, v in sorted(extra, key=lambda x: str(x)):
        hint = ""
        if v is None:
            hint = "   <- a NULL average: you kept a city with no estimates"
        elif n == "None" or n == "nan":
            hint = "   <- unnamed city: a REVENUE row points at a missing CITY_CODE"
        elif (n, v) in {(a, b) for a, b in exp_set}:
            hint = ""
        else:
            near = [e for e in exp_set if e[0] == n]
            if near:
                hint = f"   <- value is off for {n}"
            else:
                hint = f"   <- {n} should not be in the output"
        print(f"      unexpected: {(n, v)}{hint}")
    for row in sorted(missing, key=lambda x: str(x)):
        if reveal:
            print(f"      missing:    {row}")
        else:
            print(f"      missing:    a row for {row[0]}")
    if not reveal:
        print("      (call check(df, reveal=True) once you've genuinely given up)")


WHAT_TO_WATCH = """
Seven things this dataset is testing. Read only after you've run check().

1. Bengaluru: estimates 1 and 2, average 1.5.
   FLOOR(1.5) = 1, ROUND(1.5) = 2, CAST(1.5 AS INT) = 1.  Rounding gets this wrong.

2. Indore: estimates -5 and 2, average -1.5.
   FLOOR(-1.5) = -2, but CAST(-1.5 AS INT) = -1 -- CAST truncates toward zero, it
   does not floor. This is the row that separates the two approaches.

3. Aurangabad appears twice with different pincodes (431001 and 824101).
   CITY_CODE is the primary key, so a "city" is a code, not a name. GROUP BY the code.
   GROUP BY CITY_NAME merges them into one row of 182 and loses both real answers.

4. Kolkata has no estimates. An INNER JOIN drops it, a LEFT JOIN gives it a NULL
   average. Decide which the question wants and be able to say why.

5. REVENUE has a row for city_code 999999, which is not in CITIES. An inner join
   discards it; a right/full join or a query driven off REVENUE alone will surface an
   unnamed city with a 50000 average.

6. Mumbai averages 600.0 exactly. Flooring must not change it.

7. Chennai has one estimate. AVG over a single row is that row.

Engine notes
  - SQLite added FLOOR() in 3.35 (2021). Older builds have no FLOOR at all, which is
    why CAST(x AS INT) is the classic workaround -- and why trap 2 matters.
  - MySQL and Postgres both have FLOOR(). In Postgres, FLOOR() on an integer-typed
    AVG result returns numeric; CAST it if the grader is fussy about formatting.
  - The requested output format is `CITY_NAME AVERAGE_REVENUE` -- two columns,
    space-separated in HackerRank's renderer. Don't concatenate them into one string.
"""


if __name__ == "__main__":
    con = build()
    print(f"built {DB}\n")
    print("CITIES");  print(q("SELECT * FROM CITIES ORDER BY CITY_CODE").to_string(index=False))
    print("\nREVENUE"); print(q("SELECT * FROM REVENUE ORDER BY CITY_CODE").to_string(index=False))
    print(f"\n{len(CITIES)} cities, {len(REVENUE)} revenue rows. "
          f"Write your query, then call check(df).")
