"""Leakage-resistant dataset splits for sandhi experiments."""

from __future__ import annotations

import hashlib
import math
import unicodedata
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


SPLIT_NAMES = ("train", "dev", "test")
DEFAULT_RATIOS = {"train": 0.8, "dev": 0.1, "test": 0.1}


@dataclass(frozen=True)
class SplitResult:
    """Strict lexical splits plus cross-bucket records that were withheld."""

    records: dict[str, tuple[dict[str, Any], ...]]
    lemma_buckets: dict[str, str]
    requested_ratios: dict[str, float]
    lemma_bucket_ratios: dict[str, float]
    seed: int

    def manifest(self) -> dict[str, Any]:
        """Return auditable counts and rule coverage for serialization."""
        per_rule: dict[str, dict[str, int]] = {}
        for split_name, records in self.records.items():
            counts = Counter(
                str(record["rule_id"]) for record in records
            )
            per_rule[split_name] = dict(sorted(counts.items()))
        overlaps = lexical_overlaps(self.records)
        return {
            "schema_version": 1,
            "method": "strict_lexical_v1",
            "seed": self.seed,
            "requested_example_ratios": self.requested_ratios,
            "lemma_bucket_ratios": self.lemma_bucket_ratios,
            "record_counts": {
                name: len(records)
                for name, records in self.records.items()
            },
            "unique_lemma_counts": {
                name: len(_lemmas(records))
                for name, records in self.records.items()
                if name in SPLIT_NAMES
            },
            "lexical_overlap_counts": {
                pair: len(values)
                for pair, values in overlaps.items()
            },
            "per_rule_counts": per_rule,
        }


def normalize_lemma(value: Any) -> str:
    """Apply the experiment's minimal, script-preserving normalization."""
    if not isinstance(value, str):
        raise ValueError("lemmas must be strings")
    normalized = unicodedata.normalize("NFC", value).strip()
    if not normalized:
        raise ValueError("lemmas must not be empty")
    return normalized


def _validate_ratios(
    ratios: Mapping[str, float],
) -> dict[str, float]:
    if set(ratios) != set(SPLIT_NAMES):
        raise ValueError(f"ratios must define exactly {SPLIT_NAMES}")
    parsed = {name: float(ratios[name]) for name in SPLIT_NAMES}
    if any(value <= 0 for value in parsed.values()):
        raise ValueError("all split ratios must be positive")
    if not math.isclose(sum(parsed.values()), 1.0, abs_tol=1e-9):
        raise ValueError("split ratios must sum to 1.0")
    return parsed


def _lemma_ratios(
    example_ratios: Mapping[str, float],
) -> dict[str, float]:
    # Squaring these endpoint proportions recovers the requested distribution
    # among examples whose two lemmas land in the same partition.
    roots = {
        name: math.sqrt(value)
        for name, value in example_ratios.items()
    }
    total = sum(roots.values())
    return {name: roots[name] / total for name in SPLIT_NAMES}


def _hash_fraction(seed: int, lemma: str) -> float:
    digest = hashlib.sha256(
        f"{seed}:{lemma}".encode("utf-8")
    ).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def _assign_bucket(
    seed: int,
    lemma: str,
    ratios: Mapping[str, float],
) -> str:
    value = _hash_fraction(seed, lemma)
    cumulative = 0.0
    for name in SPLIT_NAMES:
        cumulative += ratios[name]
        if value < cumulative:
            return name
    return SPLIT_NAMES[-1]


def build_strict_lexical_holdout(
    records: Iterable[Mapping[str, Any]],
    *,
    seed: int = 1729,
    ratios: Mapping[str, float] | None = None,
) -> SplitResult:
    """Partition lemmas first, withholding every cross-partition example.

    The same normalized lemma is assigned to exactly one bucket. An example is
    retained only when both endpoint lemmas have that bucket, which makes the
    train/dev/test lemma vocabularies disjoint by construction. Cross-bucket
    examples are preserved in the mixed split for transparent accounting.
    """
    requested = _validate_ratios(ratios or DEFAULT_RATIOS)
    lemma_ratios = _lemma_ratios(requested)
    materialized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    lemmas: set[str] = set()

    for index, raw_record in enumerate(records):
        record = dict(raw_record)
        for field in (
            "example_id",
            "left_lemma",
            "right_lemma",
            "rule_id",
        ):
            if field not in record:
                raise ValueError(
                    f"record {index} is missing {field}"
                )
            if (
                not isinstance(record[field], str)
                or not record[field].strip()
            ):
                raise ValueError(
                    f"record {index}.{field} "
                    "must be a non-empty string"
                )
        example_id = record["example_id"]
        if example_id in seen_ids:
            raise ValueError(f"duplicate example_id: {example_id}")
        seen_ids.add(example_id)
        record["left_lemma"] = normalize_lemma(
            record["left_lemma"]
        )
        record["right_lemma"] = normalize_lemma(
            record["right_lemma"]
        )
        lemmas.update(
            (record["left_lemma"], record["right_lemma"])
        )
        materialized.append(record)

    lemma_buckets = {
        lemma: _assign_bucket(seed, lemma, lemma_ratios)
        for lemma in sorted(lemmas)
    }
    assigned: dict[str, list[dict[str, Any]]] = {
        "train": [],
        "dev": [],
        "test": [],
        "mixed": [],
    }
    for record in materialized:
        left_bucket = lemma_buckets[record["left_lemma"]]
        right_bucket = lemma_buckets[record["right_lemma"]]
        bucket = (
            left_bucket
            if left_bucket == right_bucket
            else "mixed"
        )
        assigned[bucket].append(record)

    frozen = {
        name: tuple(
            sorted(items, key=lambda item: item["example_id"])
        )
        for name, items in assigned.items()
    }
    overlaps = lexical_overlaps(frozen)
    if any(overlaps.values()):
        raise AssertionError(
            "strict lexical split construction leaked lemmas"
        )
    return SplitResult(
        records=frozen,
        lemma_buckets=lemma_buckets,
        requested_ratios=requested,
        lemma_bucket_ratios=lemma_ratios,
        seed=seed,
    )


def _lemmas(
    records: Iterable[Mapping[str, Any]],
) -> set[str]:
    values: set[str] = set()
    for record in records:
        values.add(normalize_lemma(record["left_lemma"]))
        values.add(normalize_lemma(record["right_lemma"]))
    return values


def lexical_overlaps(
    records: Mapping[str, Iterable[Mapping[str, Any]]],
) -> dict[str, set[str]]:
    """Return pairwise train/dev/test lemma intersections."""
    vocabularies = {
        name: _lemmas(records.get(name, ()))
        for name in SPLIT_NAMES
    }
    return {
        "train_dev": (
            vocabularies["train"] & vocabularies["dev"]
        ),
        "train_test": (
            vocabularies["train"] & vocabularies["test"]
        ),
        "dev_test": (
            vocabularies["dev"] & vocabularies["test"]
        ),
    }
