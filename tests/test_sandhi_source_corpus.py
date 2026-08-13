"""Tests for the deterministic all-sandhi source-corpus builder."""

import hashlib
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_sandhi_sutra_corpus as corpus_builder  # noqa: E402
from build_sandhi_sutra_corpus import (  # noqa: E402
    CorpusBuildError,
    PINNED_SOURCE_COMMIT,
    build_corpus,
    build_manifest,
    render_jsonl,
)


def source_record(
    compact: str,
    adhyaya: str,
    pada: str,
    number: str,
    *,
    sk_chapter: str = "0",
    lsk_chapter: str = "0",
    type_value: str = "V$$",
) -> dict[str, str]:
    return {
        "i": compact,
        "a": adhyaya,
        "p": pada,
        "n": number,
        "s": f"सूत्रम् {compact}",
        "type": type_value,
        "sk_chapter": sk_chapter,
        "lsk_chapter": lsk_chapter,
    }


def test_build_uses_union_of_both_chapter_classifications():
    payload = {
        "data": [
            source_record("83015", "8", "3", "15", sk_chapter="6"),
            source_record(
                "11001",
                "1",
                "1",
                "1",
                lsk_chapter="2",
                type_value="S$definition$",
            ),
            source_record("61077", "6", "1", "77", sk_chapter="3"),
            source_record("31001", "3", "1", "1"),
        ]
    }

    records = build_corpus(payload, PINNED_SOURCE_COMMIT)

    assert [record["sutra_id"] for record in records] == [
        "1.1.1",
        "6.1.77",
        "8.3.15",
    ]
    assert records[0]["rule_role"] == "definition"
    assert records[1]["rule_role"] == "operative_candidate"
    assert records[0]["selection"]["matched_traditions"] == [
        "laghu_siddhanta_kaumudi"
    ]


def test_compact_id_must_match_coordinates():
    payload = {
        "data": [
            source_record("61078", "6", "1", "77", sk_chapter="3")
        ]
    }

    with pytest.raises(CorpusBuildError, match="does not match coordinates"):
        build_corpus(payload, PINNED_SOURCE_COMMIT)


def test_unknown_type_code_is_rejected():
    payload = {
        "data": [
            source_record(
                "61077",
                "6",
                "1",
                "77",
                sk_chapter="3",
                type_value="UNKNOWN$$",
            )
        ]
    }

    with pytest.raises(CorpusBuildError, match="unsupported source type"):
        build_corpus(payload, PINNED_SOURCE_COMMIT)


def test_modified_source_blob_is_rejected(monkeypatch, tmp_path):
    def fake_git_output(_source_dir, arguments):
        if arguments[0] == "rev-parse":
            return "expected-blob"
        return "modified-blob"

    monkeypatch.setattr(corpus_builder, "_git_output", fake_git_output)

    with pytest.raises(CorpusBuildError, match="differs from pinned commit"):
        corpus_builder._verify_source_blob(tmp_path, PINNED_SOURCE_COMMIT)


def test_render_and_manifest_hash_are_deterministic():
    payload = {
        "data": [source_record("61077", "6", "1", "77", sk_chapter="3")]
    }
    records = build_corpus(payload, PINNED_SOURCE_COMMIT)

    first = render_jsonl(records)
    second = render_jsonl(records)
    manifest = build_manifest(
        records,
        PINNED_SOURCE_COMMIT,
        "a" * 64,
        first,
    )

    assert first == second
    assert manifest["artifact"]["sha256"] == hashlib.sha256(first).hexdigest()
    assert manifest["counts"]["operative_candidates"] == 1


def test_committed_corpus_matches_its_manifest():
    corpus_path = ROOT / "data/sources/ashtadhyayi_sandhi_sutras.jsonl"
    manifest_path = ROOT / "data/sources/ashtadhyayi_sandhi_manifest.json"
    if not corpus_path.exists() or not manifest_path.exists():
        pytest.skip("generated source corpus is not present")

    corpus_bytes = corpus_path.read_bytes()
    records = [
        json.loads(line)
        for line in corpus_bytes.decode("utf-8").splitlines()
        if line
    ]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert len(records) == manifest["counts"]["records"] == 148
    assert manifest["counts"]["operative_candidates"] == 108
    assert manifest["counts"]["supporting_records"] == 40
    assert manifest["artifact"]["sha256"] == hashlib.sha256(
        corpus_bytes
    ).hexdigest()
    sutra_ids = [record["sutra_id"] for record in records]
    assert len(sutra_ids) == len(set(sutra_ids))
    assert sutra_ids == sorted(
        sutra_ids,
        key=lambda value: tuple(int(part) for part in value.split(".")),
    )
    assert all(record["annotation_status"] == "source_candidate" for record in records)
    assert all(record["computational_rule_ids"] == [] for record in records)
    assert all(record["expert_review_required"] is True for record in records)
    assert all(
        record["source"]["commit"] == PINNED_SOURCE_COMMIT
        for record in records
    )
    assert len(manifest["source"]["file_sha256"]) == 64
    assert manifest["license"]["verified_at_source_commit"] is False
    assert manifest["license"]["github_license_api_status"] == 404
