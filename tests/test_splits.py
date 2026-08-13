"""Tests for strict lexical holdouts."""

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from panini.splits import (  # noqa: E402
    build_strict_lexical_holdout,
    lexical_overlaps,
)


def _records():
    lemmas = [f"lemma-{index}" for index in range(80)]
    records = []
    for index, left in enumerate(lemmas):
        right = lemmas[(index + 7) % len(lemmas)]
        records.append(
            {
                "example_id": f"ex-{index:03d}",
                "left_lemma": left,
                "right_lemma": right,
                "rule_id": f"EVS-{(index % 3) + 1:03d}",
                "surface": f"surface-{index}",
            }
        )
    return records


def test_strict_split_is_deterministic_and_has_no_overlap():
    first = build_strict_lexical_holdout(
        _records(),
        seed=42,
    )
    second = build_strict_lexical_holdout(
        reversed(_records()),
        seed=42,
    )

    assert first.records == second.records
    assert all(
        not overlap
        for overlap in lexical_overlaps(
            first.records
        ).values()
    )
    assert sum(
        len(records)
        for records in first.records.values()
    ) == len(_records())


def test_cross_bucket_examples_are_preserved_as_mixed():
    result = build_strict_lexical_holdout(
        _records(),
        seed=42,
    )

    assert result.records["mixed"]
    for record in result.records["mixed"]:
        left_bucket = result.lemma_buckets[
            record["left_lemma"]
        ]
        right_bucket = result.lemma_buckets[
            record["right_lemma"]
        ]
        assert left_bucket != right_bucket


def test_manifest_reports_zero_lexical_leakage():
    manifest = build_strict_lexical_holdout(
        _records(),
        seed=7,
    ).manifest()

    assert manifest["method"] == "strict_lexical_v1"
    assert set(
        manifest["lexical_overlap_counts"].values()
    ) == {0}


def test_duplicate_example_id_is_rejected():
    records = _records()
    records[1]["example_id"] = records[0]["example_id"]

    with pytest.raises(
        ValueError,
        match="duplicate example_id",
    ):
        build_strict_lexical_holdout(records)
