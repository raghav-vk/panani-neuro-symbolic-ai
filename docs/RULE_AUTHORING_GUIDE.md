# Authoring Reviewed Sandhi Rules

**Audience:** Project lead, Sanskrit collaborators, and rule-engine
contributors
**Goal:** Convert a scholarly interpretation into an executable, reviewable
boundary rule without claiming more than the record supports

**Pilot:** 25 external vowel-sandhi operational rules

**Expansion source:** 148 all-sandhi sūtra candidates

## 1. What Counts as One Rule

The inventory contains 25 operational rules, not necessarily 25 sūtras.
An operational rule is one deterministic boundary match and rewrite under a
typed set of conditions. Split one source rule into multiple records when its
cases require different matches, outputs, precedence, or optionality.

Do not force distinct scholarly rules into one broad pattern merely to reach a
count. If expert review supports 18 defensible operational rules rather than
25, change the experimental scope and paper honestly.

The wider source corpus does not change this principle. Its 148 records are a
review queue: one source candidate may map to zero, one, or several operational
rules, and an operational rule may cite several source records. Definitions,
adhikāras, paribhāṣā-like principles, and exceptions are dependencies rather
than standalone character rewrites.

## 2. Files

Rule inventory:

    data/rules/external_vowel_sandhi.jsonl

All-sandhi source candidates and manifest:

    data/sources/ashtadhyayi_sandhi_sutras.jsonl
    data/sources/ashtadhyayi_sandhi_manifest.json

JSON Schema:

    data/schemas/sandhi-rule.schema.json

Executable loader:

    src/panini/rules.py

The inventory contains one seed draft. It demonstrates the format only and is
explicitly not expert-reviewed.

The current executable schema is intentionally restricted to the pilot. Do
not broaden its scope enum or identifier format by guessing at consonant,
visarga, or nasal semantics. First complete reviewed examples from each family;
then version a general schema from the observed requirements while retaining
backward compatibility for EVS records.

## 3. Source Preparation

Before authoring:

1. Choose a primary textual and commentary basis for the inventory.
2. Pin the exact commit of every digital source.
3. Verify its license and attribution requirements.
4. Record variant interpretations rather than silently selecting one.
5. Ask a qualified reviewer which inherited headings, exceptions, and
   precedence relations must be represented.

The ashtadhyayi-com source corpus is pinned to commit
`51bff9fb38c6f571b4a2bc8499d97576f00ffcce` and rebuilt deterministically. The
project author's Apache-2.0 license claim is not evidenced by a license file in
that snapshot. Obtain confirmation from the upstream owner before copying
modern commentary or translation fields:

    https://github.com/ashtadhyayi-com/data

Vidyut is useful as an independent implementation reference, not as automatic
proof that this project's interpretation is correct:

    https://github.com/ambuda-org/vidyut

## 4. Field Contract

| Field | Authoring rule |
| --- | --- |
| schema_version | Always 1 for this protocol |
| rule_id | Stable EVS-NNN identifier; never recycle an identifier |
| name | Short operational name, not an unsupported translation claim |
| scope | Always external_vowel_sandhi |
| status | draft, self_checked, or expert_reviewed |
| source.sutra_ids | Every directly used sūtra identifier |
| source.text_iast | Source text in the chosen transliteration |
| source.text_devanagari | Source text when verified; may be empty during draft |
| source.interpretation | Exact operational reading and scope |
| source.url | Direct source location |
| source.commit | Immutable source revision |
| source.license | Verified license or rights statement |
| match.left_suffixes | All left boundary strings consumed or retained |
| match.right_prefixes | All right boundary strings consumed or retained |
| match.required_tags | Conditions that must be present |
| match.forbidden_tags | Exceptions that block this record |
| operation.left | Keep or drop the matched left suffix |
| operation.emit | Boundary string emitted by the operation |
| operation.right | Keep or drop the matched right prefix |
| precedence | Explicit conflict priority; larger values rank first |
| optional | True only when alternative application is licensed |
| examples | Positive cases that execute to the stated surface |
| counterexamples | Non-applications or contrasts with reasons |
| review | Author, independent reviewer, and date |
| notes | Ambiguity, commentary dependence, and open questions |

## 5. Tag Vocabulary

Use tags for grammatical conditions that cannot be represented by boundary
characters alone. Begin with a small controlled vocabulary in a shared issue
or future schema file. Candidate tags include:

- pada_boundary
- left_pragrhya
- right_vowel
- optional_context
- vedic_only
- compound_internal

Do not invent spelling variants of an existing tag. A tag must have a written
definition and at least one positive or negative test. The first paper excludes
Vedic-only and compound-internal cases unless the protocol is amended before
the split is frozen.

## 6. Authoring Workflow

### Step 0: Screen a Source Candidate

Before creating an executable rule, record an expert decision for the source
candidate:

- `include`: relevant to the declared computational sandhi scope.
- `support_only`: needed for a definition, inherited scope, exception, or
  precedence relation but not independently executable.
- `exclude`: incidental to the selected chapters or outside the benchmark.
- `needs_discussion`: interpretation or tradition-dependent scope is unresolved.

For included candidates, record a provisional family, domain
(external/internal/both), directly required source dependencies, and the
number of operational cases expected. Preserve disagreements. Never edit the
generated source JSONL to store these decisions; keep review annotations in a
separate versioned artifact so rebuilding the source remains deterministic.

### Step 1: Create a Draft

Copy the seed JSON object to a new line, assign the next EVS identifier, and
replace every field. Keep status draft, reviewer empty, and reviewed_at empty.

### Step 2: State the Operational Reading

Write what the program will do, including:

- Domain of application.
- Inherited grammatical context.
- Boundary classes.
- Exceptions.
- Whether application is optional.
- Relationship to more specific rules.

Avoid phrases such as always correct or perfectly grammatical.

### Step 3: Encode Boundary Behavior

List complete matched suffixes and prefixes. The engine chooses the longest
matching boundary string. Select keep_match or drop_match independently for
each side and state the emitted string.

Run structural validation after every edit:

    python3 scripts/validate_rules.py

The validator rejects unknown fields, duplicate identifiers, malformed sūtra
identifiers, contradictory tags, and positive examples that do not execute to
their stated surface.

### Step 4: Add Positive Examples

Add at least two examples with different lexical items. Every example needs:

- Left and right forms in the frozen internal transliteration.
- Expected fused surface.
- All tags required for the rule to apply.
- Source classified as attested or constructed.
- A note when interpretation or normalization is uncertain.

Do not use a test-set example as a rule example after results have been seen.
Rule examples are part of the symbolic specification and therefore part of
the training-side research process.

### Step 5: Add Counterexamples

Include at least one near-miss that a naive character rewrite would wrongly
accept. State why the rule must not apply: exception, domain mismatch,
precedence, lexical condition, or unsupported interpretation.

Counterexamples are not decorative. They define the boundary of the encoded
claim and should become executable negative tests as the compiler matures.

### Step 6: Self-Check

Set status self_checked only after:

- Structural validation passes.
- Every source link opens.
- The source commit is pinned.
- Transliteration is normalized.
- Positive examples reconstruct exactly.
- The precedence relation has been compared with every overlapping rule.

### Step 7: Independent Review

The reviewer should inspect the source, operational interpretation, examples,
counterexample, tags, optionality, and precedence. Review is not merely a
spelling check.

After accepted corrections, set status expert_reviewed and record reviewer
and date. Run:

    python3 scripts/validate_rules.py \
      --expected-count 25 \
      --publication-ready

## 7. Tests Required Per Rule

Each rule eventually needs:

- At least two positive boundary applications.
- At least one character-compatible but grammatically blocked case.
- A non-matching left boundary.
- A non-matching right boundary.
- A required-tag omission.
- A forbidden-tag presence.
- A precedence conflict when another rule overlaps.
- Both outputs when the rule is optional.
- Forward reconstruction of the observed surface.
- Stable proof fields and source identifiers.

Round-trip uniqueness is not required. Sandhi splitting can be ambiguous, so
the correct invariant is that each proposed analysis reconstructs the surface,
not that every surface has one inverse.

## 8. Review Worksheet

For each EVS record, answer:

| Question | Response |
| --- | --- |
| Is the cited source text accurate? | yes, no, uncertain |
| Is inherited context represented? | yes, no, not applicable |
| Are exceptions represented? | yes, no, unresolved |
| Is the rewrite operationally faithful? | yes, no, uncertain |
| Is precedence correct? | yes, no, unresolved |
| Are examples acceptable? | all, some, none |
| Is the counterexample informative? | yes, no |
| May the record enter experiments? | approve, revise, exclude |

Preserve completed worksheets or issue discussions as supplementary audit
material.

## 9. Collaboration Boundary

Engineering contributors may implement the schema, compiler, tests, and data
pipeline. They must not promote a rule to expert_reviewed unless the named
reviewer has actually approved it. Sanskrit collaborators own interpretive
approval; the project lead owns provenance and release records; experiment
authors own the accuracy of claims made from the subset.

## 10. Definition of Done

The rule-authoring milestone is complete when:

- The inventory contains exactly 25 defensible records.
- The publication validator exits successfully.
- Every overlap has a deterministic precedence test.
- Every rule has corpus support or is explicitly controlled-only.
- Every rule included in macro evaluation has at least 20 strict-holdout test
  examples.
- The inventory commit hash is frozen in the experiment manifest.
