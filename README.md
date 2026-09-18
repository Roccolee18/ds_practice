# ds-interview-prep

Timed, self-grading practice sets for data science interviews, plus a record of every attempt.

```bash
git init && git add -A && git commit -m "initial: capital-one-ds problem set"

pip install -r requirements.txt
chmod +x new-attempt.sh sets/*/bootstrap.sh    # only if your unzip dropped the exec bit
./sets/capital-one-ds/bootstrap.sh             # generates the data (gitignored)
./new-attempt.sh capital-one-ds                # stamps a dated attempt folder
```

Then set an 80-minute timer and open the `exam.ipynb` it created.

The data ships pre-generated, so you can skip `bootstrap.sh` on the first run — but it's gitignored,
so anyone cloning this repo (including future you on another machine) needs it.

## Layout

```
├── PROGRESS.md                     # the score log — the point of the repo
├── new-attempt.sh                  # start a sitting
├── sets/
│   └── capital-one-ds/             # the problem set (committed)
│       ├── practice_exam.ipynb     # blank template — never worked in directly
│       ├── SOLUTIONS.md            # worked answers + M4 rubric
│       ├── grader.py               # check("P1", p1) / score()
│       ├── bootstrap.sh            # rebuilds data/ + answer_key.b64
│       ├── generate_data.py  solutions_ref.py  make_key.py  make_notebook.py
│       └── data/                   # GITIGNORED — derived, ~29MB
└── attempts/
    └── 2026-09-17-capital-one-ds/  # one folder per sitting (committed, with outputs)
        ├── exam.ipynb
        └── NOTES.md
```

## Why it's split this way

**`data/` and `answer_key.b64` are gitignored.** Together they're 29MB, 16MB of it a SQLite binary,
and every byte is derivable from `generate_data.py` plus a seed. `bootstrap.sh` rebuilds both in
about five seconds, and it always rebuilds them *together* so they can't drift apart. Commit the
generator, not the output.

**The template stays blank.** Working directly in `sets/…/practice_exam.ipynb` means attempt #2
destroys the record of attempt #1. `new-attempt.sh` copies it into a dated folder instead.

**Attempts keep their outputs.** The `check()` PASS/FAIL results are the record of what you actually
did. If you run `nbstripout --install`, scope it to the template — see below.

**One commit per attempt.** `git log --oneline` becomes your history:

```
attempt: capital-one-ds #3 — 88% (SQL 100%)
attempt: capital-one-ds #2 — 81% (SQL 60%)
attempt: capital-one-ds #1 — 64% (SQL 40%)
```

No branches. `PROGRESS.md` gives the at-a-glance table, `git log` gives the narrative.

## Re-sitting a set

```bash
./sets/capital-one-ds/bootstrap.sh 12345   # same questions, different numbers
./new-attempt.sh capital-one-ds
```

The seed is written to `data/SEED`, printed by the notebook's setup cell, and copied into each
attempt's `NOTES.md` — so you always know which numbers an old attempt was working against.

## Optional: nbstripout on the template only

Outputs in notebooks make enormous, unreadable diffs. You want them stripped on the template and
kept on attempts, so scope it with a path-specific filter:

```bash
pip install nbstripout
nbstripout --install --attributes .gitattributes
# then edit .gitattributes so only the template is filtered:
echo 'sets/**/practice_exam.ipynb filter=nbstripout' > .gitattributes
```

The template ships with no outputs, so this is belt-and-braces — it only matters if you ever run the
blank notebook in place.

## Adding another set

Drop it in `sets/<name>/` with the same four entry points — `practice_exam.ipynb`, `grader.py`,
`bootstrap.sh`, `SOLUTIONS.md` — and `new-attempt.sh <name>` works unchanged. The notebook finds its
own set folder via the `SET_NAME` constant in its setup cell, so an attempt copy runs from
`attempts/` without any path fiddling.
