#!/usr/bin/env bash

set -euo pipefail

echo "Project Panini: quick verification"
echo

echo "[1/3] Validating draft rule structure"
python3 scripts/validate_rules.py
echo

echo "[2/3] Running tests"
python3 -m pytest tests -q -p no:cacheprovider
echo

if [[ -f datasets/DCS_pick.zip ]]; then
    echo "[3/3] Auditing 10 DCS records without unpickling"
    python3 scripts/audit_dcs_archive.py --sample 10
else
    echo "[3/3] DCS archive not present; skipping local corpus audit"
fi

echo
echo "Quick verification passed."
