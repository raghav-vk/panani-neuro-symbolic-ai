# Quick Start

This guide verifies the current research scaffolding. It does not train a
model yet.

## 1. Environment

Requirements:

- Python 3.10 or newer.
- pytest for the test suite.
- No GPU for the current rule, split, and archive utilities.

Optional virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install -r requirements.txt

## 2. Run Everything Implemented

    ./test_quick.sh

Or run the steps independently:

    python3 scripts/validate_rules.py
    python3 -m pytest tests -q

The rule command should validate one draft rule. It does not certify the
inventory for publication.

## 3. Inspect a Proof Trace

From the repository root:

    PYTHONPATH=src python3 -c "from panini.rules import load_rules, apply_rule; r=load_rules('data/rules/external_vowel_sandhi.jsonl')[0]; print(apply_rule(r, 'deva', 'ālaya', {'pada_boundary'}))"

The output identifies EVS-001, sūtra 6.1.101, matched boundaries, tags, and the
reconstructed surface. EVS-001 remains a draft pending qualified review.

## 4. Test the Lexical Holdout

Run the tracked smoke fixture:

    python3 scripts/build_lexical_holdout.py \
      tests/fixtures/holdout_examples.jsonl \
      /tmp/panini-holdout-smoke \
      --force

Inspect its manifest:

    python3 -m json.tool \
      /tmp/panini-holdout-smoke/manifest.json

Expected record counts:

| Split | Count |
| --- | ---: |
| train | 2 |
| dev | 2 |
| test | 2 |
| mixed | 2 |

Every lexical_overlap_counts value must be zero. The mixed examples
deliberately connect lemmas assigned to different partitions and are excluded
from train, dev, and test.

## 5. Audit the DCS Archive

If datasets/DCS_pick.zip is present:

    python3 scripts/audit_dcs_archive.py --sample 100

Expected local counts are 441,735 unique data records, no missing extracted
records, and two ancillary Python files. The utility examines pickle opcodes
without constructing the serialized DCS objects. It also requires zero
manifest identity problems for byte size, MD5, and SHA-256.

This is an integrity check, not an annotation-quality check. Provenance,
checksums, citation, and the CC BY 4.0 license for this exact archive are in
datasets/dcs_source_manifest.json.

## 6. Rebuild the All-Sandhi Source Corpus

After pinning an `ashtadhyayi-com/data` checkout to commit
`51bff9fb38c6f571b4a2bc8499d97576f00ffcce`, run:

    PYTHONDONTWRITEBYTECODE=1 python3 \
      scripts/build_sandhi_sutra_corpus.py \
      --source-dir vendor/ashtadhyayi-data

Expected totals are 148 records, 108 operative candidates, and 40 supporting
records. Read docs/ALL_SANDHI_DATASET.md before treating any source candidate
as an executable rule.

## 7. Author Rules

Read:

    docs/RULE_AUTHORING_GUIDE.md

Edit:

    data/rules/external_vowel_sandhi.jsonl

Validate after each rule:

    python3 scripts/validate_rules.py

The final release command is:

    python3 scripts/validate_rules.py \
      --expected-count 25 \
      --publication-ready

That command currently fails by design because the inventory has one draft,
no reviewer, and incomplete source and example coverage.

## 8. Understand the Experiment

Read in this order:

1. docs/README.md
2. docs/ALL_SANDHI_DATASET.md
3. docs/EXPERIMENT_PROTOCOL.md
4. docs/RULE_AUTHORING_GUIDE.md
5. docs/panini-neuro-symbolic-ai.md
6. datasets/README.md
7. docs/approach-to-solution.md

## 9. Current Next Step

The next scholarly milestone is expert screening of the 148 source candidates.
In parallel, the next engineering milestone is a safe DCS-to-JSONL converter
that:

- Never executes arbitrary pickle constructors.
- Preserves source identifiers and original text.
- Logs rejected and ambiguous records.
- Extracts only candidate external vowel boundaries.
- Aligns forms and lemmas to one of the reviewed EVS rules.
- Requires forward surface reconstruction.

Do not start neural training before the rule inventory, corpus manifest,
normalization, deduplication, and splits are frozen.
