#!/usr/bin/env python3
"""Build deterministic splits with disjoint lemma vocabularies."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from panini.splits import build_strict_lexical_holdout  # noqa: E402


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{path}:{line_number}: {exc}"
                ) from exc
            if not isinstance(value, dict):
                raise ValueError(
                    f"{path}:{line_number}: "
                    "expected a JSON object"
                )
            records.append(value)
    return records


def write_jsonl(
    path: Path,
    records: tuple[dict[str, Any], ...],
) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    targets = [
        args.output_dir / f"{name}.jsonl"
        for name in ("train", "dev", "test", "mixed")
    ]
    targets.append(args.output_dir / "manifest.json")
    existing = [path for path in targets if path.exists()]
    if existing and not args.force:
        print(
            "ERROR: output files already exist; pass --force "
            "to replace them: "
            + ", ".join(str(path) for path in existing),
            file=sys.stderr,
        )
        return 1

    try:
        raw_bytes = args.input.read_bytes()
        records = read_jsonl(args.input)
        result = build_strict_lexical_holdout(
            records,
            seed=args.seed,
        )
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, split_records in result.records.items():
        write_jsonl(
            args.output_dir / f"{name}.jsonl",
            split_records,
        )

    manifest = result.manifest()
    manifest["input"] = str(args.input)
    manifest["input_sha256"] = hashlib.sha256(
        raw_bytes
    ).hexdigest()
    manifest_path = args.output_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(
            manifest,
            handle,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        handle.write("\n")

    counts = manifest["record_counts"]
    print(
        "Built strict lexical split: "
        + ", ".join(
            f"{name}={counts[name]}"
            for name in ("train", "dev", "test", "mixed")
        )
    )
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
