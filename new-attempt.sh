#!/usr/bin/env bash
# Starts a timed sitting: stamps a dated folder under attempts/ with a fresh copy of
# the blank exam and a NOTES.md pre-filled with the current seed.
#
#   ./new-attempt.sh                  # defaults to capital-one-ds
#   ./new-attempt.sh capital-one-ds
set -euo pipefail
cd "$(dirname "$0")"

SET="${1:-capital-one-ds}"
SET_DIR="sets/$SET"

[[ -d "$SET_DIR" ]] || { echo "No such set: $SET  (have: $(ls sets))" >&2; exit 1; }

if [[ ! -f "$SET_DIR/data/SEED" ]]; then
    echo "No data yet -- bootstrapping $SET first."
    "$SET_DIR/bootstrap.sh"
fi
SEED="$(cat "$SET_DIR/data/SEED")"

DATE="$(date +%Y-%m-%d)"
DIR="attempts/${DATE}-${SET}"
N=1
while [[ -d "$DIR" ]]; do
    N=$((N + 1))
    DIR="attempts/${DATE}-${SET}-${N}"
done

mkdir -p "$DIR"
cp "$SET_DIR/practice_exam.ipynb" "$DIR/exam.ipynb"

ATTEMPT_NO=$(find attempts -maxdepth 1 -type d -name "*-${SET}*" | wc -l | tr -d ' ')

cat > "$DIR/NOTES.md" <<EOF
# $SET — attempt #$ATTEMPT_NO — $DATE

- **seed:** $SEED
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

-

## What to drill before next time

-
EOF

echo "created $DIR"
echo
echo "  1. set an 80-minute timer"
echo "  2. open $DIR/exam.ipynb"
echo "  3. do NOT open $SET_DIR/SOLUTIONS.md until the timer stops"
echo
echo "when you're done: fill in $DIR/NOTES.md, add a row to PROGRESS.md, and commit"
echo "with outputs intact:  git add -A && git commit -m \"attempt: $SET #$ATTEMPT_NO — __%\""
