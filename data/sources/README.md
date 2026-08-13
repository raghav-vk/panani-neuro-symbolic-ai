# Sandhi Source Corpus

This directory contains a deterministic source-candidate corpus, not a
finished executable grammar.

| Artifact | Purpose |
| --- | --- |
| `ashtadhyayi_sandhi_sutras.jsonl` | 148 selected sūtra records |
| `ashtadhyayi_sandhi_manifest.json` | Source commit, selection, counts, license status, and SHA-256 |
| `../schemas/sandhi-sutra-source.schema.json` | Record-level JSON Schema |

The corpus has 108 records marked `operative_candidate` and 40 supporting
definitions, governing scopes, and interpretive principles. Every record
remains `source_candidate`, requires expert review, and has an empty
`computational_rule_ids` list.

See `docs/ALL_SANDHI_DATASET.md` for selection rationale, reproduction,
annotation workflow, and tests.
