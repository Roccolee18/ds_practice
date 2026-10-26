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

pandas/python
- Get 1 col of a df and keep it as a df instead of series
   - df[["col1"]]
- filtering with multiple conditions:
   - df[(df["col1"] > 1) & (df["col2"] < 2>)]
- Drop duplicate rows based on values from a certain column
   - df.drop_duplicates(subset = ["col1"])
- Rename columns
   -  df.rename(columns = {"old": "new"})
- Sort column
   - df.sort_values(by = "col1")
- length of a cell in a dataframe
   - df["col1"].str.len()
- find rows based on a condition
   - df.loc[df["col"] > 1]
- dict of counts from a list
   - for i in arr:
      - counts[i] = counts.get(i, 0) + 1
- turn dict values/keys into list
   - list(counts.keys())
   - list(counts.values())
- Ranking
   - df["rank"] = df["col_to_rank"].rank(method = "dense")


<!-- - Get 1 col of a df and keep it as a df instead of series
   - df[["col"]]
- filtering with multiple conditions:
   - df[(cond1) | (cond2)]
- Drop duplicate rows based on values from a certain column
   - df.drop_duplicates(subset = ["col"])
- Rename columns
   - df.rename(columns = {"old": "new"}
- Sort column
   - df.sort_values(by = "col1", ascending = False)
- length of a cell in a dataframe
   - df["col"].str.len()
- find rows based on a condition
   - df.loc[df[cond]]
- dict of counts from a list
   - for i in arr:
   - counts[i] = counts.get(i, 0) + 1
- turn dict values/keys into list
   - list(count.keys())
   - list(count.values())
- Ranking
   - df["rank"] = df["col_to_rank"].rank(method = "dense") -->


SQL

- Filtering for multiple conditions
   - 
- date interval
   - 
- Matching sequence of 0 or more characters
   - 
- Matching exactly 1 character
   - 
- Only showing NEXT number of results from LIMIT
   - 
- Top N per group
   - 
      - 
   - 
   - 
- Anti-Join



<!-- - Filtering for multiple conditions
   - WHERE col IN ('one', 'two', 'three')
- date interval
   - WHERE DATE BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'
- Matching sequence of 0 or more characters
   - WHERE col LIKE 'AT%'
- Matching exactly 1 character
   - WHERE col LIKE 'AT_'
- Only showing NEXT number of results from LIMIT
   - LIMIT 5 OFFSET 5
- Top N per group
   - WITH rn AS(
   - ROW_NUMBER() OVER (PARTITION BY group_col ORDER BY ranked_col)) AS rank
   - )
   - SELECT rank FROM rn WHERE rn < N
- Anti-Join
   - LEFT JOIN(
      - SELECT a.customer_id, s.days_past_due
      - FROM accounts a
      - JOIN statements s ON a.account_id = s.account_id
      - WHERE s.days_past_due > 0
   - ) d ON d.customer_id = c.customer_id
   - WHERE d.customer_id IS NULL -->

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
