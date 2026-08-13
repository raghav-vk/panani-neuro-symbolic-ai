"""Tests for non-executing inspection of legacy pickle records."""

import hashlib
import json
import pickle
import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from audit_dcs_archive import (  # noqa: E402
    archive_identity,
    audit_opcodes,
    verify_archive_identity,
)


def test_plain_data_pickle_has_no_constructor_problem():
    data = pickle.dumps(
        {"sentence": "example", "lemmas": [["deva"]]},
        protocol=0,
    )

    assert audit_opcodes(data) == []


def test_reduce_constructor_is_rejected():
    class Suspicious:
        def __reduce__(self):
            return (str, ("not executed",))

    data = pickle.dumps(Suspicious(), protocol=0)

    problems = audit_opcodes(data)
    assert any("REDUCE" in problem for problem in problems)


def test_archive_identity_matches_manifest(tmp_path):
    archive = tmp_path / "archive.zip"
    archive.write_bytes(b"small archive fixture")
    identity = archive_identity(archive)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "artifact": {
                    "size_bytes": identity["size_bytes"],
                    "local_md5": identity["md5"],
                    "local_sha256": identity["sha256"],
                }
            }
        ),
        encoding="utf-8",
    )

    observed, problems = verify_archive_identity(archive, manifest)

    assert observed == identity
    assert problems == []


def test_archive_identity_reports_digest_mismatch(tmp_path):
    archive = tmp_path / "archive.zip"
    archive.write_bytes(b"changed")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "artifact": {
                    "size_bytes": len(b"changed"),
                    "local_md5": "0" * 32,
                    "local_sha256": hashlib.sha256(b"changed").hexdigest(),
                }
            }
        ),
        encoding="utf-8",
    )

    _, problems = verify_archive_identity(archive, manifest)

    assert len(problems) == 1
    assert problems[0].startswith("md5:")
