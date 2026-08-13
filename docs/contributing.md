# Contributing

The first paper has one focused task: proof-carrying external vowel-sandhi
splitting with a typed rule subset and a tiny candidate ranker. A broader
148-record all-sandhi source corpus supports expert-led expansion without
silently widening the measured claim.

Contributions that expand into translation, general correction, or literary
generation should be discussed separately and must not blur the current
experiment.

## Start Here

    python3 -m pip install -r requirements.txt
    ./test_quick.sh

Then read:

1. docs/ALL_SANDHI_DATASET.md
2. docs/EXPERIMENT_PROTOCOL.md
3. docs/RULE_AUTHORING_GUIDE.md
4. docs/panini-neuro-symbolic-ai.md

## Contribution Areas

### Grammar

- Screen all-sandhi source candidates as include, support-only, exclude, or
  needs-discussion without editing the generated source corpus.
- Classify reviewed candidates by family and internal/external domain.
- Author typed EVS draft records from pinned sources.
- Identify inherited context, exceptions, and precedence.
- Add positive examples and informative counterexamples.
- Review records independently.
- Audit model proof traces and error categories.

Only the named qualified reviewer may approve promotion to expert_reviewed.
Engineering validation is not scholarly approval.

### Data

- Recheck frozen manifests and resolve rights for any newly added source.
- Build a safe non-executing or restricted decoder for legacy records.
- Align source spans to external vowel boundaries.
- Preserve original text and stable identifiers.
- Define normalization and deduplication tests.
- Adjudicate ambiguous automatic labels.

Do not commit raw DCS files, generated splits, restricted material, or private
reviewer information.

### Engineering

- Implement precedence-aware candidate inversion.
- Add executable negative and overlap tests.
- Build random and exact-pair split utilities.
- Implement the tiny candidate ranker and matched baselines.
- Save run manifests, predictions, proofs, and resource metrics.
- Generate paper tables from artifacts.

### Evaluation

- Audit lexical and source leakage.
- Implement macro and micro metrics.
- Add bootstrap confidence intervals.
- Analyze candidate-recall failures before neural ranking errors.
- Design blinded expert-review forms.

## Rule Pull Requests

A rule change should include:

- Source URL and immutable commit.
- Verified license field.
- Operational interpretation.
- Required and forbidden tags.
- Precedence rationale.
- At least two executable positive examples.
- At least one counterexample.
- Tests for every overlap affected.
- Reviewer status represented honestly.

Run:

    python3 scripts/validate_rules.py
    python3 -m pytest tests/test_rules.py -q

Do not set expert_reviewed merely to make the publication gate pass.

## Data Pull Requests

Include:

- Input source and hash.
- Transformation version.
- Counts before and after every filter.
- Rejection reason counts.
- Duplicate audit.
- Source-group audit.
- Split manifest.
- License and redistribution assessment.

Never include test examples chosen after model errors were inspected without
versioning the benchmark and rerunning the full protocol.

## Code Standards

- Support Python 3.10 or newer.
- Prefer the standard library for rule and data validation.
- Use type hints for public interfaces.
- Reject malformed input rather than silently repairing it.
- Preserve deterministic ordering and explicit seeds.
- Add concise comments only for non-obvious logic.
- Add tests with every behavior change.
- Keep the legacy toy generator isolated from research artifacts.

## Research Standards

- No fabricated or estimated result in a results table.
- No test-set tuning.
- No unsupported perfect-correctness language.
- No hidden fallback from constrained to unconstrained output.
- No direct execution of unverified pickle payloads.
- No cross-dataset score comparison presented as a matched baseline.
- No archival submission with unresolved source rights or result placeholders.

## Pull Request Checklist

- The change stays within or explicitly updates the frozen protocol.
- All tests pass.
- Draft and publication validators behave as expected.
- New generated artifacts are ignored or intentionally licensed.
- Documentation describes limitations and validity boundaries.
- No unrelated user files are removed.
- Claims are supported by code, artifacts, citations, or named review.

## Questions and Coordination

Open a focused issue describing the artifact, decision, and acceptance test.
For grammatical questions, include the source passage and competing
interpretations. For experimental questions, identify which research question
and split are affected.
