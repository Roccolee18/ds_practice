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
