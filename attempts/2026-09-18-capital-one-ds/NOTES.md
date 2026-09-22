# capital-one-ds — attempt #1 — 2026-09-18

- **seed:** 20260917
- **started:**
- **elapsed:**     (budget 80 min)

## Score

| section | score |
|---|---|
| pandas (P1–P4) | % |
| SQL (S1–S5) | % |
| applied ML (M1–M3) | % |
| **overall** | **%** |
| M4 written (rubric, /12) | |

## What went wrong

- restart first, debug second to wipe buggy objects from memory

## What to drill before next time

- Machine learning focused, as per `GAME_PLAN.md`
- Beginning to internalize general ML flow for creating baseline models
- Look, Cover, Recall on M1. M2 and M3
- M1 Notes
   - `select_dtypes()` subsets **dataframe**, here its being used to get a list of number columns for preprocessing, so I need the column names in a list
      - add `.columns.to_list()`
   - Derive column lists from the exact frame you pass to fit.
    num = X[feats].select_dtypes(include=np.number).columns.tolist()
    cat = [c for c in feats if c not in num]
    assert set(num + cat) == set(feats)

- SQL drills
   - GROUP BY after after aggregation fuctions (e.g. COUNT, AVG, etc.)
   - JOIN syntax
   - anti-join with left join syntax
      1. build group that you don't want first
      2. left join on FROM table
      3. WHERE key IS NULL
      4. then GROUP_BY clause
   - JOIN first, then GROUP BY
   - Ensure everything that isn't aggregated is in GROUP BY
   - 