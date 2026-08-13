# Datasets and Provenance

This directory holds local source corpora and small repository fixtures.
Large corpora are ignored by Git. A source corpus does not inherit the
repository's MIT license.

## Current Local Archive

The current DCS_pick ZIP audit reports:

| Check | Observed |
| --- | ---: |
| Pickle data records in ZIP | 441,735 |
| Unique pickle basenames | 441,735 |
| Duplicate pickle basenames | 0 |
| Ancillary Python files | 2 |
| Extracted pickle records | 441,735 |
| Missing extracted pickle records | 0 |
| Unexpected extracted pickle records | 0 |

The ancillary files are dcssave.py and findingwrong_1.py. They are not data
records and are not needed for the experiment.

The local archive is now matched to the Zenodo artifact:

| Provenance check | Verified value |
| --- | --- |
| Zenodo record | 803508 |
| DOI | 10.5281/zenodo.803508 |
| Artifact | DCS_pick.zip |
| Bytes | 199,818,951 |
| MD5 | 556395ddc0f087fbf0a199a0581775d0 |
| SHA-256 | 7b13cc2fda84318cba23d9c7667cd3ea30600091e446dac43fae86ebe90e4e85 |
| License | CC BY 4.0 |

The citable, machine-readable record is
`datasets/dcs_source_manifest.json`.

Sample records contain fields such as:

- sentence
- lemmas
- dcs_chunks
- cng
- sent_id

They use legacy text-protocol Python pickle streams. Do not call pickle.load
on them directly. The audit utility uses pickletools to inspect opcodes without
instantiating serialized classes and, by default, verifies archive size, MD5,
and SHA-256 against `datasets/dcs_source_manifest.json`:

    python3 scripts/audit_dcs_archive.py --sample 100

Increase the sample before a frozen run:

    python3 scripts/audit_dcs_archive.py --sample 1000

## DCS Provenance Gate

The filename alone is not sufficient provenance. This repository now records:

1. The exact Zenodo record and DOI.
2. Official filename, byte size, and MD5.
3. An independently computed local MD5 and SHA-256.
4. The creators and citation.
5. The CC BY 4.0 license and attribution conditions.

For a different source archive, copy the generic template:

    datasets/source_manifest.example.json

Archive identity and licensing are now resolved for this exact DCS_pick ZIP.
Safety, annotation quality, conversion correctness, and suitability for a
sandhi benchmark remain separate gates.

## All-Sandhi Sūtra Candidates

The repository tracks a generated source inventory under `data/sources/`:

| Artifact | Value |
| --- | ---: |
| Selected sūtra records | 148 |
| Operative candidates | 108 |
| Supporting records | 40 |
| Source commit | 51bff9fb38c6f571b4a2bc8499d97576f00ffcce |
| Source-file SHA-256 | 6a22591f418cd924ba4bd621944de2359cc06721b5ada79ef08d70f17a07bcc6 |
| Artifact SHA-256 | 6160267d448a6ab589e00f9582ee87ea3bc47fd42fafb37fa9b3a9dfe0f2ebab |

Selection is the union of source records assigned to Siddhānta Kaumudī
chapters 3-7 or Laghu Siddhānta Kaumudī chapters 2-3. Every record is labeled
`source_candidate`; chapter membership is not treated as expert approval or
as a one-to-one executable rule.

See `docs/ALL_SANDHI_DATASET.md` for reconstruction, licensing caveats, and
the expert operationalization workflow.

## What the Archive Is Not

The 441,735 records are sentence analyses. They are not 441,735 labeled
external vowel-sandhi examples. A valid conversion pipeline must:

- Preserve the source sentence and sent_id.
- Parse without executing arbitrary pickle constructors.
- Freeze one internal transliteration.
- Identify a specific two-lexeme external vowel boundary.
- Align left form, right form, and fused surface.
- Attach one or more candidate EVS rules.
- Generate a forward-reconstructing proof trace.
- Send ambiguous cases to review or reject them.
- Log all rejection reasons.

Do not train directly on raw lemma groups and call the result a sandhi
experiment.

## Derived Example Contract

The canonical derived JSONL fields are:

| Field | Required | Notes |
| --- | --- | --- |
| example_id | yes | Stable before splitting |
| source_record_id | yes | Maps to sent_id or equivalent |
| source_work_id | when available | Used for source holdout |
| original_text | yes | Unmodified source text |
| normalized_text | yes | Frozen versioned normalization |
| context_left | yes | May be empty at sentence start |
| surface | yes | Observed fused target |
| context_right | yes | May be empty at sentence end |
| left_form | yes | Gold pre-sandhi form |
| right_form | yes | Gold pre-sandhi form |
| left_lemma | yes | Leakage-control key |
| right_lemma | yes | Leakage-control key |
| rule_id | yes | EVS-NNN |
| tags | yes | Typed rule conditions |
| proof | yes | Forward reconstruction trace |
| provenance | yes | Source and extraction details |
| annotation_status | yes | automatic, self_checked, expert_reviewed |

The initial parser may produce automatic records. The final test set must be
expert-reviewed or adjudicated.

## Deduplication

Deduplicate before any split. Audit at least:

- Source record plus target span.
- Surface plus left and right forms.
- Ordered lemma pair plus rule identifier.
- Exact normalized context hash.
- Work or edition group for near-duplicate passages.

Store a rejection file with counts and reasons. Do not silently remove records
after observing test performance.

## Required Split Families

### Source-Grouped Random

Split whole source sentences or duplicate groups 80/10/10. Never place two
boundaries from the same sentence in different partitions.

### Exact Pair Holdout

Keep every occurrence of an ordered normalized lemma pair in one partition.
This blocks exact-pair memorization while allowing each lemma with other
partners.

### Strict Lexical Holdout

Partition lemmas before examples. Keep an example in train, dev, or test only
when both lemmas map to that partition. Preserve cross-partition examples as
mixed and report them.

Build:

    python3 scripts/build_lexical_holdout.py \
      data/processed/examples.jsonl \
      data/processed/strict-lexical

Required manifest checks:

- train versus dev lemma overlap equals zero.
- train versus test lemma overlap equals zero.
- dev versus test lemma overlap equals zero.
- Input SHA-256 and seed recorded.
- Counts and unique lemmas recorded per split.
- Per-rule counts recorded.
- Mixed count recorded.

## Controlled Examples

Controlled examples are useful for rule unit tests and low-frequency rules.
Partition the lexicon before generating them. If pairs are generated first and
randomly split later, the strict lexical claim is invalid.

Label every generated record controlled. Do not present generated examples as
corpus attestations.

## Toy Dataset

datasets/toy_dataset.jsonl contains 53 manually entered
English-to-transliterated-Sanskrit demonstration pairs from the original broad
project. It has no role in the external vowel-sandhi study, is not an
evaluation set, and must not be used as evidence of grammatical quality.

## Release Layout

A completed local experiment should produce:

    datasets/dcs_source_manifest.json
    data/sources/ashtadhyayi_sandhi_manifest.json
    data/sources/ashtadhyayi_sandhi_sutras.jsonl
    data/processed/examples.jsonl
    data/processed/rejections.jsonl
    data/processed/random/manifest.json
    data/processed/pair-holdout/manifest.json
    data/processed/strict-lexical/manifest.json

Generated and potentially restricted files stay out of Git. Release only
artifacts permitted by source licenses; otherwise release hashes, code,
statistics, and reconstruction instructions.
