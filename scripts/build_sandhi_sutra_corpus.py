#!/usr/bin/env python3
"""Build a pinned all-sandhi sutra candidate corpus.

The source repository groups sutras according to several pedagogical works.
This generator takes the union of the sandhi chapters in Siddhanta Kaumudi
and Laghu Siddhanta Kaumudi. Chapter membership identifies candidates; it
does not by itself make a sutra an executable computational rule.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


SOURCE_REPOSITORY = "https://github.com/ashtadhyayi-com/data"
SOURCE_DATA_PATH = "sutraani/data.txt"
SELECTION_CRITERION = "sandhi-chapter-union-v1"
SIDDHANTA_KAUMUDI_CHAPTERS = frozenset({"3", "4", "5", "6", "7"})
LAGHU_SIDDHANTA_KAUMUDI_CHAPTERS = frozenset({"2", "3"})
ROLE_BY_TYPE_CODE = {
    "V": "operative_candidate",
    "S": "definition",
    "AD": "governing_scope",
    "P": "interpretive_principle",
    "AT": "transference_principle",
}
PINNED_SOURCE_COMMIT = "51bff9fb38c6f571b4a2bc8499d97576f00ffcce"


class CorpusBuildError(ValueError):
    """Raised when source data violates the corpus build contract."""


def _required_string(record: Mapping[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise CorpusBuildError(f"source record field {key!r} must be a string")
    return value


def _sutra_id(record: Mapping[str, Any]) -> str:
    adhyaya = _required_string(record, "a")
    pada = _required_string(record, "p")
    number = _required_string(record, "n")
    if not (adhyaya.isdigit() and pada.isdigit() and number.isdigit()):
        raise CorpusBuildError("sutra coordinates must contain decimal digits")

    compact = _required_string(record, "i")
    expected_compact = f"{int(adhyaya)}{int(pada)}{int(number):03d}"
    if compact != expected_compact:
        raise CorpusBuildError(
            f"source record {compact!r} does not match coordinates "
            f"{adhyaya}.{pada}.{number}"
        )
    return f"{int(adhyaya)}.{int(pada)}.{int(number)}"


def _type_code(record: Mapping[str, Any]) -> str:
    raw_type = _required_string(record, "type")
    code = raw_type.split("$", maxsplit=1)[0]
    if code not in ROLE_BY_TYPE_CODE:
        raise CorpusBuildError(f"unsupported source type code {code!r}")
    return code


def _selection(record: Mapping[str, Any]) -> tuple[str, ...]:
    matches: list[str] = []
    if record.get("sk_chapter") in SIDDHANTA_KAUMUDI_CHAPTERS:
        matches.append("siddhanta_kaumudi")
    if record.get("lsk_chapter") in LAGHU_SIDDHANTA_KAUMUDI_CHAPTERS:
        matches.append("laghu_siddhanta_kaumudi")
    return tuple(matches)


def normalize_record(
    source_record: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    """Convert one selected upstream record to the public corpus schema."""
    matches = _selection(source_record)
    if not matches:
        raise CorpusBuildError("cannot normalize a record outside the selection")

    sutra_id = _sutra_id(source_record)
    source_record_id = _required_string(source_record, "i")
    type_code = _type_code(source_record)
    source_url = (
        f"{SOURCE_REPOSITORY}/blob/{source_commit}/{SOURCE_DATA_PATH}"
    )
    return {
        "schema_version": 1,
        "record_id": f"ASHT-SANDHI-{sutra_id}",
        "sutra_id": sutra_id,
        "source_record_id": source_record_id,
        "text_devanagari": _required_string(source_record, "s"),
        "source_type_code": type_code,
        "rule_role": ROLE_BY_TYPE_CODE[type_code],
        "selection": {
            "criterion": SELECTION_CRITERION,
            "matched_traditions": list(matches),
            "siddhanta_kaumudi_chapter": str(
                source_record.get("sk_chapter", "")
            ),
            "laghu_siddhanta_kaumudi_chapter": str(
                source_record.get("lsk_chapter", "")
            ),
        },
        "annotation_status": "source_candidate",
        "computational_rule_ids": [],
        "expert_review_required": True,
        "source": {
            "repository": SOURCE_REPOSITORY,
            "commit": source_commit,
            "path": SOURCE_DATA_PATH,
            "url": source_url,
        },
    }


def build_corpus(
    source_payload: Mapping[str, Any],
    source_commit: str,
) -> list[dict[str, Any]]:
    """Select, normalize, validate, and sort source records."""
    source_records = source_payload.get("data")
    if not isinstance(source_records, list):
        raise CorpusBuildError("source payload must contain a data array")
    if len(source_commit) != 40 or any(
        character not in "0123456789abcdef" for character in source_commit
    ):
        raise CorpusBuildError("source commit must be a lowercase 40-digit SHA")

    selected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw_record in enumerate(source_records):
        if not isinstance(raw_record, Mapping):
            raise CorpusBuildError(f"source data[{index}] must be an object")
        if not _selection(raw_record):
            continue
        normalized = normalize_record(raw_record, source_commit)
        sutra_id = normalized["sutra_id"]
        if sutra_id in seen_ids:
            raise CorpusBuildError(f"duplicate selected sutra {sutra_id}")
        seen_ids.add(sutra_id)
        selected.append(normalized)

    selected.sort(
        key=lambda record: tuple(
            int(part) for part in record["sutra_id"].split(".")
        )
    )
    if not selected:
        raise CorpusBuildError("selection produced no sutra records")
    return selected


def render_jsonl(records: Sequence[Mapping[str, Any]]) -> bytes:
    """Render canonical UTF-8 JSON Lines for hashing and publication."""
    lines = [
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for record in records
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def build_manifest(
    records: Sequence[Mapping[str, Any]],
    source_commit: str,
    source_file_sha256: str,
    jsonl_bytes: bytes,
) -> dict[str, Any]:
    """Describe provenance, selection, licensing status, and corpus counts."""
    role_counts = Counter(str(record["rule_role"]) for record in records)
    type_counts = Counter(str(record["source_type_code"]) for record in records)
    sk_counts = Counter(
        str(record["selection"]["siddhanta_kaumudi_chapter"])
        for record in records
    )
    lsk_counts = Counter(
        str(record["selection"]["laghu_siddhanta_kaumudi_chapter"])
        for record in records
    )
    operative = role_counts["operative_candidate"]
    return {
        "schema_version": 1,
        "dataset_name": "Ashtadhyayi all-sandhi sutra candidate corpus",
        "dataset_version": "0.1.0",
        "artifact": {
            "path": "data/sources/ashtadhyayi_sandhi_sutras.jsonl",
            "media_type": "application/x-ndjson",
            "sha256": hashlib.sha256(jsonl_bytes).hexdigest(),
        },
        "source": {
            "repository": SOURCE_REPOSITORY,
            "commit": source_commit,
            "path": SOURCE_DATA_PATH,
            "file_sha256": source_file_sha256,
        },
        "license": {
            "claimed_spdx": "Apache-2.0",
            "claim_evidence": "supplied by project author",
            "checked_on": "2026-08-12",
            "verified_at_source_commit": False,
            "repository_license_file_found": False,
            "github_license_api_status": 404,
            "redistribution_status": "review_required",
            "note": (
                "The pinned repository snapshot contains no LICENSE, NOTICE, "
                "or COPYING file. Confirm the grant with the upstream owner "
                "before redistributing modern annotations. This artifact omits "
                "modern commentary and translations."
            ),
        },
        "selection": {
            "criterion": SELECTION_CRITERION,
            "description": (
                "Union of records assigned to Siddhanta Kaumudi chapters 3-7 "
                "or Laghu Siddhanta Kaumudi chapters 2-3 by the source dataset."
            ),
            "siddhanta_kaumudi_chapters": sorted(
                SIDDHANTA_KAUMUDI_CHAPTERS, key=int
            ),
            "laghu_siddhanta_kaumudi_chapters": sorted(
                LAGHU_SIDDHANTA_KAUMUDI_CHAPTERS, key=int
            ),
            "scope_limit": (
                "Chapter membership supplies source candidates, not a claim "
                "that each record is an executable rule or that the selection "
                "is an expert-certified exhaustive inventory."
            ),
        },
        "counts": {
            "records": len(records),
            "operative_candidates": operative,
            "supporting_records": len(records) - operative,
            "by_role": dict(sorted(role_counts.items())),
            "by_source_type_code": dict(sorted(type_counts.items())),
            "by_siddhanta_kaumudi_chapter": dict(
                sorted(sk_counts.items(), key=lambda item: int(item[0]))
            ),
            "by_laghu_siddhanta_kaumudi_chapter": dict(
                sorted(lsk_counts.items(), key=lambda item: int(item[0]))
            ),
        },
    }


def _git_commit(source_dir: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(source_dir), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CorpusBuildError(
            "could not derive the source commit; pass --source-commit"
        ) from exc
    return result.stdout.strip()


def _git_output(source_dir: Path, arguments: Sequence[str]) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(source_dir), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CorpusBuildError(
            f"git verification failed for {' '.join(arguments)}"
        ) from exc
    return result.stdout.strip()


def _verify_source_blob(source_dir: Path, source_commit: str) -> None:
    source_file = source_dir / SOURCE_DATA_PATH
    expected_blob = _git_output(
        source_dir,
        ["rev-parse", f"{source_commit}:{SOURCE_DATA_PATH}"],
    )
    actual_blob = _git_output(
        source_dir,
        ["hash-object", str(source_file)],
    )
    if actual_blob != expected_blob:
        raise CorpusBuildError(
            f"{SOURCE_DATA_PATH} differs from pinned commit {source_commit}"
        )


def _load_source(source_dir: Path) -> tuple[Mapping[str, Any], str]:
    source_file = source_dir / SOURCE_DATA_PATH
    try:
        source_bytes = source_file.read_bytes()
        payload = json.loads(source_bytes.decode("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CorpusBuildError(f"cannot read {source_file}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise CorpusBuildError(f"{source_file} is not UTF-8: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise CorpusBuildError("source payload root must be an object")
    return payload, hashlib.sha256(source_bytes).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--source-commit")
    parser.add_argument(
        "--expected-commit",
        default=PINNED_SOURCE_COMMIT,
        help="abort unless the source checkout matches this SHA",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/sources/ashtadhyayi_sandhi_sutras.jsonl"),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/sources/ashtadhyayi_sandhi_manifest.json"),
    )
    args = parser.parse_args()

    try:
        source_commit = args.source_commit or _git_commit(args.source_dir)
        if args.expected_commit and source_commit != args.expected_commit:
            raise CorpusBuildError(
                f"source commit {source_commit} does not match expected "
                f"{args.expected_commit}"
            )
        _verify_source_blob(args.source_dir, source_commit)
        source_payload, source_file_sha256 = _load_source(args.source_dir)
        records = build_corpus(source_payload, source_commit)
        jsonl_bytes = render_jsonl(records)
        manifest = build_manifest(
            records,
            source_commit,
            source_file_sha256,
            jsonl_bytes,
        )

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(jsonl_bytes)
        args.manifest.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    except CorpusBuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {len(records)} records to {args.output}")
    print(
        "Operative candidates: "
        f"{manifest['counts']['operative_candidates']}"
    )
    print(f"Supporting records: {manifest['counts']['supporting_records']}")
    print(f"SHA-256: {manifest['artifact']['sha256']}")
    print(f"Manifest: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
