#!/usr/bin/env python3
"""Audit the legacy DCS ZIP without executing its pickle records."""

from __future__ import annotations

import argparse
import hashlib
import json
import pickletools
import sys
import zipfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any


DANGEROUS_CONSTRUCTORS = {
    "GLOBAL",
    "REDUCE",
    "OBJ",
    "NEWOBJ",
    "NEWOBJ_EX",
    "EXT1",
    "EXT2",
    "EXT4",
    "PERSID",
    "BINPERSID",
}


def archive_identity(path: Path) -> dict[str, str | int]:
    """Compute size and identity digests in one streaming pass."""
    md5 = hashlib.md5(usedforsecurity=False)
    sha256 = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            size += len(chunk)
            md5.update(chunk)
            sha256.update(chunk)
    return {
        "size_bytes": size,
        "md5": md5.hexdigest(),
        "sha256": sha256.hexdigest(),
    }


def verify_archive_identity(
    archive_path: Path,
    manifest_path: Path,
) -> tuple[dict[str, str | int], list[str]]:
    """Compare a local archive with its frozen source manifest."""
    try:
        manifest_value: Any = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read manifest {manifest_path}: {exc}") from exc
    if not isinstance(manifest_value, Mapping):
        raise ValueError("source manifest root must be an object")
    artifact = manifest_value.get("artifact")
    if not isinstance(artifact, Mapping):
        raise ValueError("source manifest must contain an artifact object")

    expected = {
        "size_bytes": artifact.get("size_bytes"),
        "md5": artifact.get("local_md5"),
        "sha256": artifact.get("local_sha256"),
    }
    for key, value in expected.items():
        if key == "size_bytes":
            valid = isinstance(value, int) and not isinstance(value, bool)
        else:
            valid = isinstance(value, str) and bool(value)
        if not valid:
            raise ValueError(f"source manifest has invalid artifact.{key}")

    observed = archive_identity(archive_path)
    problems = [
        f"{key}: expected {expected[key]}, observed {observed[key]}"
        for key in expected
        if observed[key] != expected[key]
    ]
    return observed, problems


def audit_opcodes(data: bytes) -> list[str]:
    """Inspect pickle opcodes only; never instantiate the object."""
    problems: list[str] = []
    for opcode, argument, position in pickletools.genops(data):
        if opcode.name in DANGEROUS_CONSTRUCTORS:
            problems.append(
                f"{opcode.name} at byte {position}"
            )
        if (
            opcode.name == "INST"
            and argument != "__main__ DCS"
        ):
            problems.append(
                f"unexpected INST {argument!r} "
                f"at byte {position}"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive",
        type=Path,
        default=Path("datasets/DCS_pick.zip"),
    )
    parser.add_argument(
        "--extracted",
        type=Path,
        default=Path("datasets/DCS_pick"),
    )
    parser.add_argument("--sample", type=int, default=100)
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("datasets/dcs_source_manifest.json"),
    )
    parser.add_argument(
        "--skip-manifest-check",
        action="store_true",
        help="skip size and checksum verification",
    )
    args = parser.parse_args()

    try:
        identity: dict[str, str | int] | None = None
        identity_problems: list[str] = []
        if not args.skip_manifest_check:
            identity, identity_problems = verify_archive_identity(
                args.archive,
                args.manifest,
            )
        with zipfile.ZipFile(args.archive) as archive:
            all_files = [
                item
                for item in archive.infolist()
                if not item.is_dir()
            ]
            records = [
                item
                for item in all_files
                if Path(item.filename).suffix == ".p"
            ]
            ancillary = [
                item.filename
                for item in all_files
                if Path(item.filename).suffix != ".p"
            ]
            archive_names = {
                Path(item.filename).name for item in records
            }
            duplicates = len(records) - len(archive_names)
            sampled = records[: max(0, args.sample)]
            opcode_problems: list[str] = []
            for item in sampled:
                for problem in audit_opcodes(
                    archive.read(item)
                ):
                    opcode_problems.append(
                        f"{item.filename}: {problem}"
                    )
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    extracted_names = (
        {
            path.name
            for path in args.extracted.glob("*.p")
        }
        if args.extracted.exists()
        else set()
    )
    missing = archive_names - extracted_names
    extra = extracted_names - archive_names

    print(f"Archive data records: {len(records)}")
    if identity is not None:
        print(f"Archive size: {identity['size_bytes']}")
        print(f"Archive MD5: {identity['md5']}")
        print(f"Archive SHA-256: {identity['sha256']}")
        print(f"Manifest identity problems: {len(identity_problems)}")
        for problem in identity_problems:
            print(f"  {problem}")
    print(f"Unique record basenames: {len(archive_names)}")
    print(f"Duplicate record basenames: {duplicates}")
    print(f"Ancillary archive files: {len(ancillary)}")
    if ancillary:
        print("Ancillary names: " + ", ".join(ancillary))
    print(f"Extracted data records: {len(extracted_names)}")
    print(f"Missing extracted records: {len(missing)}")
    print(f"Unexpected extracted records: {len(extra)}")
    print(
        "Opcode samples inspected without unpickling: "
        f"{len(sampled)}"
    )
    print(f"Opcode problems: {len(opcode_problems)}")
    for problem in opcode_problems[:10]:
        print(f"  {problem}")

    if identity_problems or opcode_problems:
        return 1
    if missing and not args.allow_incomplete:
        print(
            "ERROR: extraction is incomplete",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
