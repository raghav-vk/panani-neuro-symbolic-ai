#!/usr/bin/env python3
"""Validate the typed external vowel-sandhi rule inventory."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from panini.rules import RuleValidationError, load_rules  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=ROOT
        / "data/rules/external_vowel_sandhi.jsonl",
    )
    parser.add_argument("--expected-count", type=int)
    parser.add_argument(
        "--publication-ready",
        action="store_true",
    )
    args = parser.parse_args()

    try:
        rules = load_rules(
            args.path,
            publication_ready=args.publication_ready,
            expected_count=args.expected_count,
        )
    except (OSError, RuleValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    statuses = Counter(rule.status for rule in rules)
    print(f"Validated {len(rules)} rule(s) from {args.path}")
    print(
        "Statuses: "
        + ", ".join(
            f"{key}={value}"
            for key, value in sorted(statuses.items())
        )
    )
    if not args.publication_ready:
        print(
            "Structural validation only; use --publication-ready "
            "for release gates."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
