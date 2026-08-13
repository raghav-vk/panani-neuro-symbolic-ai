# All-Sandhi Sūtra Candidate Corpus

**Dataset version:** 0.1.0

**Pinned source commit:** `51bff9fb38c6f571b4a2bc8499d97576f00ffcce`

**Pinned source-file SHA-256:** `6a22591f418cd924ba4bd621944de2359cc06721b5ada79ef08d70f17a07bcc6`

**Records:** 148 total, 108 operative candidates, 40 supporting records

**Status:** Reproducible source inventory; expert operationalization pending

## What This Dataset Is

`data/sources/ashtadhyayi_sandhi_sutras.jsonl` is a broad, auditable inventory
of Aṣṭādhyāyī records associated with sandhi in two pedagogical orderings. It
includes vowel, consonant, visarga, nasal/anusvāra, non-application, and
supporting material instead of restricting source collection to external
vowel sandhi.

It is intentionally called a **source-candidate corpus**, not a complete
computational rule inventory. A Pāṇinian sūtra can establish a definition or
scope, inherit conditions from another sūtra, interact with exceptions, yield
several executable cases, or support no boundary rewrite by itself. Treating
every selected line as one independent neural label would erase the grammar
we are trying to preserve.

## Reproducible Inclusion Criterion

The generator selects the union of source records assigned to:

- Siddhānta Kaumudī chapters 3, 4, 5, 6, or 7; or
- Laghu Siddhānta Kaumudī chapters 2 or 3.

This `sandhi-chapter-union-v1` criterion returns 148 unique sūtras. Using the
source type codes, the generator classifies 108 as operative candidates and
40 as supporting records:

| Role | Count | Meaning in this corpus |
| --- | ---: | --- |
| operative_candidate | 108 | Source marks the record as a vidhi candidate |
| definition | 19 | Supplies a saṃjñā or other definition |
| governing_scope | 5 | Supplies an adhikāra or inherited scope |
| interpretive_principle | 11 | Supplies a paribhāṣā-like decision principle |
| transference_principle | 5 | Supplies an atideśa-like relation |

The union is deliberately reproducible and broad, but it is not yet an
expert-certified claim of exhaustiveness. An expert may add omitted records,
exclude incidental chapter members, or revise the role mapping. Such changes
must create a new criterion and dataset version rather than silently editing
version 0.1.0.

## Record Contract

Every JSONL record contains:

| Field | Purpose |
| --- | --- |
| `sutra_id` | Canonical `adhyāya.pāda.number` identifier |
| `text_devanagari` | Sūtra text from the pinned source record |
| `source_type_code` | Preserved source category code |
| `rule_role` | Conservative project role derived from that code |
| `selection` | Chapters and traditions that caused inclusion |
| `annotation_status` | Always `source_candidate` in this generated layer |
| `computational_rule_ids` | Empty until reviewed operational rules are linked |
| `expert_review_required` | Always true in this generated layer |
| `source` | Repository, immutable commit, path, and pinned URL |

The formal contract is
`data/schemas/sandhi-sutra-source.schema.json`. Modern translations,
commentary, expanded interpretations, and examples are not copied into this
release because the source repository's claimed Apache-2.0 grant could not be
verified from a license file at the pinned commit.

## Rebuild Exactly

Clone and pin the upstream source:

```bash
git clone https://github.com/ashtadhyayi-com/data.git vendor/ashtadhyayi-data
git -C vendor/ashtadhyayi-data checkout 51bff9fb38c6f571b4a2bc8499d97576f00ffcce
```

Build the corpus and manifest:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_sandhi_sutra_corpus.py \
  --source-dir vendor/ashtadhyayi-data
```

Expected output:

```text
Wrote 148 records
Operative candidates: 108
Supporting records: 40
SHA-256: 6160267d448a6ab589e00f9582ee87ea3bc47fd42fafb37fa9b3a9dfe0f2ebab
```

The generator aborts on the wrong commit, a source file whose Git blob differs
from that commit, malformed coordinates, duplicate sūtra identifiers, unknown
source type codes, or an empty selection.

## From Sūtras to Strongly Typed Rules

Experts and engineers should operationalize candidates in seven review steps:

1. Confirm whether the sūtra belongs in the computational sandhi scope.
2. Classify its family: vowel, consonant, visarga, nasal/anusvāra,
   non-application, or general support.
3. Record whether it applies externally, internally, in both domains, or only
   under a narrower grammatical condition.
4. Resolve inherited scope, technical terms, exceptions, optionality, and
   dependencies on other sūtras.
5. Split the interpretation into one or more deterministic match/rewrite
   records; never force a one-sūtra/one-rule correspondence.
6. Add attested positive examples, controlled edge cases, counterexamples,
   and precedence conflicts.
7. Obtain independent Pāṇinian review before setting `expert_reviewed` or
   including the rule in the frozen benchmark.

The current `EVS-001` rule remains a format demonstration for the narrow
external-vowel pilot. It is not evidence that all 108 operative candidates
have been encoded. Expanding the executable schema should follow reviewed
examples from at least one rule in each family so the types reflect grammar
rather than engineering guesses.

## How to Test the Dataset

Run the builder tests and full suite:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
  tests/test_sandhi_source_corpus.py -q
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests -q
```

For any regenerated corpus, require all of these checks before review:

- The JSONL has 148 unique, numerically sorted `sutra_id` values.
- The role totals are 108 operative candidates and 40 supporting records.
- The artifact SHA-256 matches its manifest.
- Every record points to the same immutable source commit.
- Every record remains `source_candidate` until an expert decision is stored.
- No modern commentary or translation fields appear in the release.

For computational rules, additionally require forward reconstruction,
positive and negative tests, exception and precedence tests, named review,
and per-family coverage. For model examples, deduplicate before splitting and
run the strict lexical holdout so no normalized lemma occurs in more than one
of train, development, or test. This blocks both exact-pair memorization and
reuse of either constituent word from inflating the strict result.

## Relation to DCS_pick

The two datasets have different jobs:

- This sūtra corpus supplies grammatical sources and the expert review queue.
- DCS_pick supplies potentially attested sentence analyses from which boundary
  examples may be derived.

The local `DCS_pick.zip` is now verified against Zenodo by filename, byte
size, and MD5 and is licensed CC BY 4.0. Its 441,735 pickle records still need
safe conversion, boundary alignment, proof reconstruction, filtering, and
review. They must not be counted as 441,735 ready-made sandhi examples.

## Licensing Boundary

The DCS record's CC BY 4.0 license is verified in
`datasets/dcs_source_manifest.json`. The ashtadhyayi-com source license is not:
the project author supplied an Apache-2.0 claim, but the pinned repository has
no license or notice file. `data/sources/ashtadhyayi_sandhi_manifest.json` keeps
that distinction machine-readable.

Apache-2.0 is permissive rather than copyleft; it does not by itself require
downstream source publication. This repository is nevertheless open source
under MIT. Before releasing copied modern annotations, obtain an authoritative
upstream rights statement and preserve any required license and notice text.
