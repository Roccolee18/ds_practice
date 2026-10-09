# Progress log

One row per sitting. Add the row when you finish, in the same commit as the attempt.

## capital-one-ds

Budget 80 min. Calibration: **≥85%** good shape · **65–85%** competitive · **<65%** a specific gap.

| # | date | seed | elapsed | pandas | SQL | ML | overall | M4 /12 | the one thing that cost me most |
|---|------|------|---------|--------|-----|----|---------|--------|----------------------------------|
| 1 | | | | | | | | | |

<!-- template row:
| 2 | 2026-09-24 | 20260917 | 80 min | 100% | 60% | 83% | 81% | 9 | gaps-and-islands — burned 11 min reinventing it |
-->

## Notes to self

Things that have bitten me more than once — keep this list short and honest, and reread it
before the next sitting.

pandas
- Get 1 col of a df and keep it as a df instead of series
   - df[["col1"]]
- filtering with multiple conditions:
   - df[(col1) & (col2)]
- Drop duplicate rows based on values from a certain column
   - df.drop_duplicates(subset = ["col"])
- Rename columns
   - df.rename({"old": "new"})
- Sort column
   - df.sort_values(by = "col")
- length of a cell in a dataframe
   - df["col"].str.len()
- find rows based on a condition
   - df[df["col"] == cond]
- camel case
   - df["text_col"].str.captialize()
   - df["text_col"].str.title()
- matching column to regex
   - df[df["col"].str.contains(r'')]
   - df[df["text_col"].str.matches(r'')]
- XOR cancellation - finding single number/finding missing number
   - result ^= x
- dict of counts from a list
   - for i in arr:
   - counts[i] = counts.get(i, 0) + 1
- turn dict values/keys into list
   - list(mydict.values())
   - list(mydict.keys())

SQL
- date interval
   - 
- Matching sequence of 0 or more characters
   - 
- Matching exactly 1 character
   - 
- Only showing NEXT number of results from LIMIT
   - 
## Patterns I want automatic

Move an item here once I've done it correctly, cold, twice.

- [ ] `ROW_NUMBER() OVER (PARTITION BY … ORDER BY …)` → filter `rn = 1` (top-N per group)
- [ ] gaps-and-islands: `date - ROW_NUMBER()` is constant within a consecutive run
- [ ] `LAG`/`LEAD` for period-over-period, with the explicit next-period guard
- [ ] `1.0 *` before any SQL division (integer division returns 0)
- [ ] `HAVING` for post-aggregation filters
- [ ] pandas `rolling("30D")` on a DatetimeIndex inside a groupby (time window ≠ row window)
- [ ] named aggregation: `.agg(n=("col", "nunique"))`
- [ ] sort-then-`.first()` when a tiebreak is specified (not `idxmax`)
- [ ] leakage check: "could I have known this on the decision date?"
- [ ] time-based split whenever the model predicts forward
- [ ] cost-asymmetric threshold: break-even p = gain / (gain + loss)
- [ ] profile numeric columns for sentinel values (`-1`, `999`, `-9999`) before modeling
