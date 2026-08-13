"""Typed boundary-rewrite rules for the external vowel-sandhi experiment."""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RULE_ID_RE = re.compile(r"^EVS-[0-9]{3}$")
SUTRA_ID_RE = re.compile(r"^[1-8]\.[1-4]\.[0-9]+$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
STATUSES = {"draft", "self_checked", "expert_reviewed"}
BOUNDARY_ACTIONS = {"drop_match", "keep_match"}
PLACEHOLDERS = {"", "TODO", "TO_VERIFY", "UNPINNED", "UNKNOWN"}


class RuleValidationError(ValueError):
    """Raised when a rule record violates the experiment contract."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RuleValidationError(f"{path} must be an object")
    return value


def _string(value: Any, path: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise RuleValidationError(f"{path} must be a string")
    if not allow_empty and not value.strip():
        raise RuleValidationError(f"{path} must not be empty")
    return value


def _string_list(
    value: Any,
    path: str,
    *,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise RuleValidationError(f"{path} must be an array")
    if not allow_empty and not value:
        raise RuleValidationError(f"{path} must not be empty")
    items = tuple(
        _string(item, f"{path}[{index}]") for index, item in enumerate(value)
    )
    if len(set(items)) != len(items):
        raise RuleValidationError(f"{path} must not contain duplicates")
    return items


def _check_keys(
    value: Mapping[str, Any],
    path: str,
    *,
    required: set[str],
    optional: set[str] | None = None,
) -> None:
    optional = optional or set()
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing:
        raise RuleValidationError(
            f"{path} is missing: {', '.join(sorted(missing))}"
        )
    if unknown:
        raise RuleValidationError(
            f"{path} has unknown fields: {', '.join(sorted(unknown))}"
        )


@dataclass(frozen=True)
class SourceRef:
    """Pinned grammatical source and the project's operational interpretation."""

    sutra_ids: tuple[str, ...]
    text_iast: str
    text_devanagari: str
    interpretation: str
    url: str
    commit: str
    license: str


@dataclass(frozen=True)
class BoundaryMatch:
    """Boundary strings and grammatical tags required for a rule to match."""

    left_suffixes: tuple[str, ...]
    right_prefixes: tuple[str, ...]
    required_tags: frozenset[str]
    forbidden_tags: frozenset[str]


@dataclass(frozen=True)
class RewriteOperation:
    """How the matched boundary strings are rewritten."""

    kind: str
    left: str
    emit: str
    right: str


@dataclass(frozen=True)
class RuleExample:
    """A positive example attached to a rule record."""

    left: str
    right: str
    surface: str
    tags: frozenset[str]
    source: str
    notes: str


@dataclass(frozen=True)
class Counterexample:
    """A documented non-application or contrasting case."""

    left: str
    right: str
    reason: str


@dataclass(frozen=True)
class Review:
    """Authorship and independent review metadata."""

    author: str
    reviewer: str
    reviewed_at: str


@dataclass(frozen=True)
class SandhiRule:
    """A complete, machine-checkable external vowel-sandhi rewrite rule."""

    schema_version: int
    rule_id: str
    name: str
    scope: str
    status: str
    source: SourceRef
    match: BoundaryMatch
    operation: RewriteOperation
    precedence: int
    optional: bool
    examples: tuple[RuleExample, ...]
    counterexamples: tuple[Counterexample, ...]
    review: Review
    notes: str

    @classmethod
    def from_mapping(cls, raw_value: Mapping[str, Any]) -> "SandhiRule":
        """Validate and construct a rule from a decoded JSON object."""
        raw = _mapping(raw_value, "rule")
        _check_keys(
            raw,
            "rule",
            required={
                "schema_version",
                "rule_id",
                "name",
                "scope",
                "status",
                "source",
                "match",
                "operation",
                "precedence",
                "optional",
                "examples",
                "counterexamples",
                "review",
                "notes",
            },
        )

        if raw["schema_version"] != 1:
            raise RuleValidationError("rule.schema_version must be 1")

        rule_id = _string(raw["rule_id"], "rule.rule_id")
        if not RULE_ID_RE.fullmatch(rule_id):
            raise RuleValidationError("rule.rule_id must match EVS-NNN")

        scope = _string(raw["scope"], "rule.scope")
        if scope != "external_vowel_sandhi":
            raise RuleValidationError("rule.scope must be external_vowel_sandhi")

        status = _string(raw["status"], "rule.status")
        if status not in STATUSES:
            raise RuleValidationError(
                f"rule.status must be one of {sorted(STATUSES)}"
            )

        source = cls._parse_source(raw["source"])
        match = cls._parse_match(raw["match"])
        operation = cls._parse_operation(raw["operation"])

        precedence = raw["precedence"]
        if (
            isinstance(precedence, bool)
            or not isinstance(precedence, int)
            or precedence < 0
        ):
            raise RuleValidationError(
                "rule.precedence must be a non-negative integer"
            )
        if not isinstance(raw["optional"], bool):
            raise RuleValidationError("rule.optional must be a boolean")

        examples_raw = raw["examples"]
        if not isinstance(examples_raw, list):
            raise RuleValidationError("rule.examples must be an array")
        examples = tuple(
            cls._parse_example(item, index)
            for index, item in enumerate(examples_raw)
        )

        counterexamples_raw = raw["counterexamples"]
        if not isinstance(counterexamples_raw, list):
            raise RuleValidationError("rule.counterexamples must be an array")
        counterexamples = tuple(
            cls._parse_counterexample(item, index)
            for index, item in enumerate(counterexamples_raw)
        )

        review = cls._parse_review(raw["review"])
        rule = cls(
            schema_version=1,
            rule_id=rule_id,
            name=_string(raw["name"], "rule.name"),
            scope=scope,
            status=status,
            source=source,
            match=match,
            operation=operation,
            precedence=precedence,
            optional=raw["optional"],
            examples=examples,
            counterexamples=counterexamples,
            review=review,
            notes=_string(raw["notes"], "rule.notes", allow_empty=True),
        )

        for index, example in enumerate(rule.examples):
            trace = apply_rule(rule, example.left, example.right, example.tags)
            if trace is None:
                raise RuleValidationError(
                    f"rule.examples[{index}] does not match {rule.rule_id}"
                )
            if trace.output != example.surface:
                raise RuleValidationError(
                    f"rule.examples[{index}].surface is {example.surface!r}, "
                    f"but the operation produces {trace.output!r}"
                )
        return rule

    @staticmethod
    def _parse_source(raw_value: Any) -> SourceRef:
        raw = _mapping(raw_value, "rule.source")
        _check_keys(
            raw,
            "rule.source",
            required={
                "sutra_ids",
                "text_iast",
                "text_devanagari",
                "interpretation",
                "url",
                "commit",
                "license",
            },
        )
        sutra_ids = _string_list(
            raw["sutra_ids"], "rule.source.sutra_ids"
        )
        for sutra_id in sutra_ids:
            if not SUTRA_ID_RE.fullmatch(sutra_id):
                raise RuleValidationError(f"invalid sutra id: {sutra_id}")
        url = _string(raw["url"], "rule.source.url")
        if not url.startswith(("https://", "http://")):
            raise RuleValidationError(
                "rule.source.url must be an HTTP(S) URL"
            )
        return SourceRef(
            sutra_ids=sutra_ids,
            text_iast=_string(raw["text_iast"], "rule.source.text_iast"),
            text_devanagari=_string(
                raw["text_devanagari"],
                "rule.source.text_devanagari",
                allow_empty=True,
            ),
            interpretation=_string(
                raw["interpretation"], "rule.source.interpretation"
            ),
            url=url,
            commit=_string(raw["commit"], "rule.source.commit"),
            license=_string(raw["license"], "rule.source.license"),
        )

    @staticmethod
    def _parse_match(raw_value: Any) -> BoundaryMatch:
        raw = _mapping(raw_value, "rule.match")
        _check_keys(
            raw,
            "rule.match",
            required={
                "left_suffixes",
                "right_prefixes",
                "required_tags",
                "forbidden_tags",
            },
        )
        required = frozenset(
            _string_list(
                raw["required_tags"],
                "rule.match.required_tags",
                allow_empty=True,
            )
        )
        forbidden = frozenset(
            _string_list(
                raw["forbidden_tags"],
                "rule.match.forbidden_tags",
                allow_empty=True,
            )
        )
        overlap = required & forbidden
        if overlap:
            raise RuleValidationError(
                "rule.match tags cannot be both required and forbidden: "
                + ", ".join(sorted(overlap))
            )
        return BoundaryMatch(
            left_suffixes=_string_list(
                raw["left_suffixes"], "rule.match.left_suffixes"
            ),
            right_prefixes=_string_list(
                raw["right_prefixes"], "rule.match.right_prefixes"
            ),
            required_tags=required,
            forbidden_tags=forbidden,
        )

    @staticmethod
    def _parse_operation(raw_value: Any) -> RewriteOperation:
        raw = _mapping(raw_value, "rule.operation")
        _check_keys(
            raw,
            "rule.operation",
            required={"kind", "left", "emit", "right"},
        )
        kind = _string(raw["kind"], "rule.operation.kind")
        if kind != "rewrite":
            raise RuleValidationError("rule.operation.kind must be rewrite")
        left = _string(raw["left"], "rule.operation.left")
        right = _string(raw["right"], "rule.operation.right")
        if left not in BOUNDARY_ACTIONS or right not in BOUNDARY_ACTIONS:
            raise RuleValidationError(
                f"boundary actions must be one of {sorted(BOUNDARY_ACTIONS)}"
            )
        return RewriteOperation(
            kind=kind,
            left=left,
            emit=_string(
                raw["emit"], "rule.operation.emit", allow_empty=True
            ),
            right=right,
        )

    @staticmethod
    def _parse_example(raw_value: Any, index: int) -> RuleExample:
        path = f"rule.examples[{index}]"
        raw = _mapping(raw_value, path)
        _check_keys(
            raw,
            path,
            required={"left", "right", "surface", "tags", "source", "notes"},
        )
        return RuleExample(
            left=_string(raw["left"], f"{path}.left"),
            right=_string(raw["right"], f"{path}.right"),
            surface=_string(raw["surface"], f"{path}.surface"),
            tags=frozenset(
                _string_list(
                    raw["tags"], f"{path}.tags", allow_empty=True
                )
            ),
            source=_string(raw["source"], f"{path}.source"),
            notes=_string(
                raw["notes"], f"{path}.notes", allow_empty=True
            ),
        )

    @staticmethod
    def _parse_counterexample(
        raw_value: Any, index: int
    ) -> Counterexample:
        path = f"rule.counterexamples[{index}]"
        raw = _mapping(raw_value, path)
        _check_keys(raw, path, required={"left", "right", "reason"})
        return Counterexample(
            left=_string(raw["left"], f"{path}.left"),
            right=_string(raw["right"], f"{path}.right"),
            reason=_string(raw["reason"], f"{path}.reason"),
        )

    @staticmethod
    def _parse_review(raw_value: Any) -> Review:
        raw = _mapping(raw_value, "rule.review")
        _check_keys(
            raw,
            "rule.review",
            required={"author", "reviewer", "reviewed_at"},
        )
        return Review(
            author=_string(raw["author"], "rule.review.author"),
            reviewer=_string(
                raw["reviewer"],
                "rule.review.reviewer",
                allow_empty=True,
            ),
            reviewed_at=_string(
                raw["reviewed_at"],
                "rule.review.reviewed_at",
                allow_empty=True,
            ),
        )


@dataclass(frozen=True)
class ProofTrace:
    """A compact certificate for one rule application."""

    rule_id: str
    sutra_ids: tuple[str, ...]
    left: str
    right: str
    matched_left: str
    matched_right: str
    output: str
    tags: tuple[str, ...]


def apply_rule(
    rule: SandhiRule,
    left: str,
    right: str,
    tags: Iterable[str] = (),
) -> ProofTrace | None:
    """Apply one boundary rule and return a proof trace when it matches."""
    if not isinstance(left, str) or not isinstance(right, str):
        raise TypeError("left and right must be strings")
    tag_set = frozenset(tags)
    if not rule.match.required_tags <= tag_set:
        return None
    if rule.match.forbidden_tags & tag_set:
        return None

    left_matches = [
        suffix
        for suffix in rule.match.left_suffixes
        if left.endswith(suffix)
    ]
    right_matches = [
        prefix
        for prefix in rule.match.right_prefixes
        if right.startswith(prefix)
    ]
    if not left_matches or not right_matches:
        return None

    matched_left = max(left_matches, key=len)
    matched_right = max(right_matches, key=len)
    left_stem = left[: -len(matched_left)] if matched_left else left
    right_tail = right[len(matched_right) :]
    left_boundary = (
        matched_left if rule.operation.left == "keep_match" else ""
    )
    right_boundary = (
        matched_right if rule.operation.right == "keep_match" else ""
    )
    output = (
        left_stem
        + left_boundary
        + rule.operation.emit
        + right_boundary
        + right_tail
    )
    return ProofTrace(
        rule_id=rule.rule_id,
        sutra_ids=rule.source.sutra_ids,
        left=left,
        right=right,
        matched_left=matched_left,
        matched_right=matched_right,
        output=output,
        tags=tuple(sorted(tag_set)),
    )


def load_rules(
    path: str | Path,
    *,
    publication_ready: bool = False,
    expected_count: int | None = None,
) -> list[SandhiRule]:
    """Load JSONL rules, reject duplicates, and optionally enforce release gates."""
    rule_path = Path(path)
    rules: list[SandhiRule] = []
    with rule_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                rules.append(SandhiRule.from_mapping(raw))
            except (json.JSONDecodeError, RuleValidationError) as exc:
                raise RuleValidationError(
                    f"{rule_path}:{line_number}: {exc}"
                ) from exc

    if not rules:
        raise RuleValidationError(f"{rule_path} contains no rules")
    duplicate_ids = [
        rule_id
        for rule_id, count in Counter(
            rule.rule_id for rule in rules
        ).items()
        if count > 1
    ]
    if duplicate_ids:
        raise RuleValidationError(
            "duplicate rule ids: " + ", ".join(sorted(duplicate_ids))
        )
    if expected_count is not None and len(rules) != expected_count:
        raise RuleValidationError(
            f"expected {expected_count} rules, found {len(rules)}"
        )
    if publication_ready:
        _validate_publication_gate(rules)
    return rules


def _validate_publication_gate(rules: Iterable[SandhiRule]) -> None:
    failures: list[str] = []
    for rule in rules:
        if rule.status != "expert_reviewed":
            failures.append(f"{rule.rule_id}: status is {rule.status}")
        if rule.source.commit.strip().upper() in PLACEHOLDERS:
            failures.append(
                f"{rule.rule_id}: source commit is not pinned"
            )
        if rule.source.license.strip().upper() in PLACEHOLDERS:
            failures.append(
                f"{rule.rule_id}: source license is unresolved"
            )
        if not rule.review.reviewer.strip():
            failures.append(f"{rule.rule_id}: reviewer is missing")
        if not DATE_RE.fullmatch(rule.review.reviewed_at):
            failures.append(
                f"{rule.rule_id}: reviewed_at must be YYYY-MM-DD"
            )
        if len(rule.examples) < 2:
            failures.append(
                f"{rule.rule_id}: needs at least two positive examples"
            )
        if len(rule.counterexamples) < 1:
            failures.append(
                f"{rule.rule_id}: needs at least one counterexample"
            )
    if failures:
        raise RuleValidationError(
            "publication gate failed:\n- " + "\n- ".join(failures)
        )
