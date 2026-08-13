# Verification Guide

The project has four current verification layers: code, rule records, corpus
integrity, and dataset splitting. Model-training tests will be added after the
candidate compiler is implemented.

## 1. Fast Verification

    ./test_quick.sh

This runs:

1. Draft rule structural validation.
2. The complete pytest suite.
3. A small DCS archive audit when the local ZIP exists.

## 2. Unit and Integration Tests

Run all tests:

    python3 -m pytest tests -q

Run without pytest cache writes:

    python3 -m pytest tests -q -p no:cacheprovider

Run a focused group:

    python3 -m pytest tests/test_rules.py -q
    python3 -m pytest tests/test_splits.py -q
    python3 -m pytest tests/test_split_cli.py -q
    python3 -m pytest tests/test_dcs_audit.py -q

Current coverage includes:

- Strict rule field validation.
- Unknown-field rejection.
- Required and forbidden tags.
- Positive-example execution.
- Proof trace contents.
- Publication-gate rejection of drafts.
- Deterministic lemma assignment.
- Zero lexical overlap.
- Mixed-edge preservation.
- End-to-end split CLI and manifest.
- Non-executing pickle opcode checks.
- Legacy generator compatibility.

## 3. Rule Validation

Draft structural check:

    python3 scripts/validate_rules.py

Expected today:

    Validated 1 rule(s)
    Statuses: draft=1

Release check:

    python3 scripts/validate_rules.py \
      --expected-count 25 \
      --publication-ready

This must fail until the full independently reviewed inventory exists. A
successful structural check must never be reported as scholarly validation.

For each new rule, tests should cover:

- Two positive examples.
- One blocked or contrasting case.
- Non-matching left and right boundaries.
- Missing required tag.
- Present forbidden tag.
- Overlap and precedence.
- Optional alternatives when applicable.
- Stable forward-reconstruction proof.

## 4. Corpus Audit

Local integrity:

    python3 scripts/audit_dcs_archive.py --sample 100

Pre-experiment sample:

    python3 scripts/audit_dcs_archive.py --sample 1000

The command exits nonzero when pickle opcode inspection finds an unexpected
constructor, extracted data records are missing, or archive size/checksums do
not match the frozen manifest. It deliberately does not execute pickle
records.

Verified for the exact local DCS_pick ZIP in
`datasets/dcs_source_manifest.json`:

- Exact source URL recorded.
- SHA-256 recorded.
- Citation verified.
- License verified.
- Redistribution decision recorded.
- No placeholder remains in the source manifest.

The archive audit cannot satisfy these provenance gates by itself; the
manifest supplies the separate source evidence. Annotation quality and safe
boundary conversion remain open gates.

## 5. All-Sandhi Source Corpus

Rebuild from the pinned upstream checkout:

    PYTHONDONTWRITEBYTECODE=1 python3 \
      scripts/build_sandhi_sutra_corpus.py \
      --source-dir vendor/ashtadhyayi-data

Run its focused tests:

    PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
      tests/test_sandhi_source_corpus.py -q

Required outcomes are 148 unique source records, 108 operative candidates,
40 supporting records, and artifact SHA-256
`6160267d448a6ab589e00f9582ee87ea3bc47fd42fafb37fa9b3a9dfe0f2ebab`.
Every record must remain `source_candidate` until expert review maps it to zero,
one, or more computational rules.

## 6. Lexical Split Smoke Test

    python3 scripts/build_lexical_holdout.py \
      tests/fixtures/holdout_examples.jsonl \
      /tmp/panini-holdout-smoke \
      --force

    python3 -m json.tool \
      /tmp/panini-holdout-smoke/manifest.json

Required fixture outcome:

- train equals 2.
- dev equals 2.
- test equals 2.
- mixed equals 2.
- Every lexical overlap equals 0.

For real data, also inspect:

- Per-rule train, dev, and test counts.
- Mixed rate.
- Unique lemma counts.
- Input SHA-256.
- Fixed seed.
- Duplicate and source-group audits.

Do not choose a new seed after comparing model test results.

## 7. Publication Data Gates

Before training:

- Normalize and deduplicate before splitting.
- Assign stable example identifiers.
- Group all boundaries from one source sentence.
- Freeze random, pair, and strict lexical manifests.
- Confirm zero train/test exact duplicates.
- Confirm zero strict train/test lemma overlap.
- Ensure every evaluated rule has at least 20 strict test examples.

Before reporting:

- Preserve predictions for every seed.
- Recompute tables from saved predictions.
- Report candidate recall separately.
- Report macro and micro exact match.
- Report coverage with selective accuracy.
- Report parameter count, time, RAM, VRAM, and latency.
- Run paired bootstrap confidence intervals.

## 8. Future Model Tests

The candidate compiler and ranker are not yet implemented. Add these tests
before their first reported run:

- Gold analysis appears in generated candidates.
- Every candidate reconstructs the surface.
- File order cannot change precedence.
- Optional rules retain all licensed alternatives.
- Candidate batching does not cross example boundaries.
- Masked padding cannot change scores.
- Training is reproducible for a fixed seed.
- Checkpoint reload reproduces predictions.
- Unconstrained ablation has a matched parameter budget.
- Abstention threshold is selected only from development predictions.

## 9. Clean-Checkout Reproduction

A release candidate must be tested from a fresh clone with no local corpus
assumptions:

1. Install requirements.txt.
2. Run all tests.
3. Reconstruct data from the documented source when permitted.
4. Verify source and derived hashes.
5. Recreate every split manifest.
6. Recreate at least one baseline run.
7. Regenerate manuscript tables from artifacts.

If restricted data prevents reconstruction, document the limitation and
provide the maximum legally redistributable audit artifacts.
