#!/usr/bin/env bash
# Rebuilds data/ and answer_key.b64 -- both are gitignored because both are derived.
#
#   ./bootstrap.sh            # default seed (the original sitting)
#   ./bootstrap.sh 42         # a fresh sitting: same questions, different numbers
#
# Data and key are ALWAYS regenerated together, so they can never drift apart.
set -euo pipefail
cd "$(dirname "$0")"

SEED="${1:-${SEED:-20260917}}"

echo "==> regenerating data with seed $SEED"
SEED="$SEED" python3 generate_data.py

echo "==> rebuilding answer key"
python3 make_key.py >/dev/null

echo
echo "ready. seed $SEED recorded in data/SEED"
echo "timed exam : ./new-attempt.sh capital-one-ds   (from the repo root)"
echo "SQL drills : sets/capital-one-ds/sql_drills.ipynb"
