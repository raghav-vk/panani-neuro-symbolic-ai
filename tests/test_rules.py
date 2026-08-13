"""Tests for typed sandhi rules and proof traces."""

import copy
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from panini.rules import (  # noqa: E402
    RuleValidationError,
    SandhiRule,
    apply_rule,
    load_rules,
)


RULE_PATH = (
    ROOT / "data/rules/external_vowel_sandhi.jsonl"
)


def _raw_rule():
    return json.loads(
        RULE_PATH.read_text(encoding="utf-8").strip()
    )


def test_seed_rule_loads_and_emits_proof_trace():
    rules = load_rules(RULE_PATH)

    assert len(rules) == 1
    trace = apply_rule(
        rules[0],
        "deva",
        "ālaya",
        {"pada_boundary"},
    )

    assert trace is not None
    assert trace.rule_id == "EVS-001"
    assert trace.sutra_ids == ("6.1.101",)
    assert trace.output == "devālaya"


def test_rule_does_not_apply_without_required_tag():
    rule = load_rules(RULE_PATH)[0]

    assert apply_rule(rule, "deva", "ālaya") is None


def test_rule_does_not_apply_with_forbidden_tag():
    rule = load_rules(RULE_PATH)[0]

    trace = apply_rule(
        rule,
        "deva",
        "ālaya",
        {"pada_boundary", "left_pragrhya"},
    )
    assert trace is None


def test_unknown_rule_field_is_rejected():
    raw = _raw_rule()
    raw["unreviewed_shortcut"] = True

    with pytest.raises(
        RuleValidationError,
        match="unknown fields",
    ):
        SandhiRule.from_mapping(raw)


def test_incorrect_positive_example_is_rejected():
    raw = _raw_rule()
    raw["examples"][0]["surface"] = "incorrect"

    with pytest.raises(
        RuleValidationError,
        match="operation produces",
    ):
        SandhiRule.from_mapping(raw)


def test_publication_gate_rejects_draft(tmp_path):
    path = tmp_path / "rules.jsonl"
    path.write_text(
        json.dumps(
            copy.deepcopy(_raw_rule()),
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        RuleValidationError,
        match="publication gate failed",
    ):
        load_rules(
            path,
            publication_ready=True,
            expected_count=1,
        )
