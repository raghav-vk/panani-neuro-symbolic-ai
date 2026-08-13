# Experimental Protocol: Proof-Carrying External Vowel-Sandhi Splitting

**Protocol version:** 0.1
**Status:** Active design; freeze before training
**Primary task:** Rank rule-licensed analyses of one external vowel-sandhi boundary
**Compute target:** CPU or one modest consumer GPU
**Submission status:** Not ready for archival submission until every release gate passes

## 1. Objective

The first paper will test one narrow claim:

> A small contextual Transformer can rank candidate external vowel-sandhi
> splits while a typed symbolic layer enforces the encoded rule subset and
> emits an auditable proof trace.

This is not a Sanskrit language model, a translator, or a complete
implementation of the Aṣṭādhyāyī. The symbolic guarantee is also narrow:
every accepted output must be licensed by the encoded and tested rule
inventory. It does not guarantee complete Pāṇinian correctness, semantic
correctness, or agreement with every grammatical tradition.

## 2. Research Questions

**RQ1: Candidate coverage.** How often does the typed rule engine place the
gold split in its candidate set?

**RQ2: Ranking.** Does a tiny contextual Transformer rank the gold candidate
more accurately than symbolic-only and frequency-based baselines?

**RQ3: Lexical generalization.** Does the improvement remain when neither
lemma in a test pair appears in training?

**RQ4: Data efficiency.** How does performance change with 250, 1,000, 5,000,
and all available training examples?

**RQ5: Auditability.** Are the emitted rule identifiers and traces accepted
by qualified reviewers for a stratified sample?

## 3. Pre-Registered Hypotheses

H1. Gold candidate recall must reach at least 95 percent before candidate
ranking results are interpreted. If it does not, the primary bottleneck is
the symbolic inventory or data alignment rather than the neural ranker.

H2. The constrained ranker will improve exact split accuracy over a
symbolic-only frequency ranker on both random and strict lexical holdouts.

H3. Every non-abstained constrained prediction will pass the executable
validity check for the encoded subset. Report this as subset compliance, not
as general grammatical correctness.

H4. Rule and context ablations will reduce strict-holdout performance,
showing whether gains come from the proposed interface rather than only from
surface memorization.

Hypotheses may be revised while the protocol is version 0.x. Freeze the
protocol, commit hash, and split seed before the first reported training run.

## 4. Formal Task

Each example contains a fused surface span x, optional left and right sentence
context c, and a gold analysis y consisting of two lexical items plus a rule
identifier.

The symbolic compiler produces:

    C_R(x, t) = {candidate analyses licensed by rules R and tags t}

The neural component assigns a score:

    s_theta(c, x, candidate, rule_features)

Inference returns the highest-scoring valid candidate when confidence exceeds
a threshold selected on development data. Otherwise it abstains. The output
includes the left form, right form, rule identifier, source sūtra identifiers,
matched boundary, and resulting surface form.

The experiment must report candidate recall separately from ranking accuracy.
A ranker cannot recover a gold analysis that the symbolic layer never
generated.

## 5. Rule Inventory

The target inventory is 25 operational external vowel-sandhi rules. An
operational rule is a tested boundary rewrite used by this system; it need not
map one-to-one to a single sūtra. One sūtra may support multiple operational
cases, and one operational case may depend on inherited context or more than
one sūtra.

Rules live in:

    data/rules/external_vowel_sandhi.jsonl

The machine-readable schema lives in:

    data/schemas/sandhi-rule.schema.json

The release gate requires all of the following:

- Exactly 25 unique EVS-NNN identifiers.
- Status expert_reviewed for every rule.
- A pinned source commit and resolved source license.
- Named author, named independent reviewer, and review date.
- At least two positive examples per rule.
- At least one counterexample or documented non-application per rule.
- Executable agreement between every positive example and its rewrite.
- Explicit precedence and optionality.
- No unknown fields accepted by the loader.

Structural validation during drafting:

    python3 scripts/validate_rules.py

Publication gate:

    python3 scripts/validate_rules.py --expected-count 25 --publication-ready

### 5.1 Broader All-Sandhi Source Inventory

The operational 25-rule pilot is grounded in a broader generated source
inventory at `data/sources/ashtadhyayi_sandhi_sutras.jsonl`. It selects the
union of source records assigned to Siddhānta Kaumudī chapters 3-7 or Laghu
Siddhānta Kaumudī chapters 2-3 at pinned commit
`51bff9fb38c6f571b4a2bc8499d97576f00ffcce`.

The result contains 148 source candidates: 108 source-labeled operative
candidates and 40 definitions, governing scopes, and interpretive support
records. Every record remains `source_candidate` with no computational rule
mapping. The source inventory therefore broadens coverage to all sandhi
families without weakening the publication gate: chapter membership is not
expert review, and sūtras do not map one-to-one to executable rules.

Reproduction, record schema, licensing status, and the expert screening
workflow are specified in `docs/ALL_SANDHI_DATASET.md`. A future all-sandhi
benchmark must version a reviewed mapping from these sources to operational
rules and report coverage separately for vowel, consonant, visarga,
nasal/anusvāra, non-application, and general-support families.

## 6. Example Data Contract

Each derived boundary example must be one JSON object with these fields:

| Field | Meaning |
| --- | --- |
| example_id | Stable identifier independent of split |
| source_record_id | Identifier in the source corpus |
| source_work_id | Work or document identifier when available |
| context_left | Text before the target surface span |
| surface | Observed fused boundary span |
| context_right | Text after the target surface span |
| left_form | Gold left member before external sandhi |
| right_form | Gold right member before external sandhi |
| left_lemma | Canonical lemma used for leakage control |
| right_lemma | Canonical lemma used for leakage control |
| rule_id | Operational EVS rule identifier |
| tags | Typed contextual conditions used by the rule |
| proof | Gold or reviewed symbolic trace |
| provenance | Source URL, version, extraction method, and annotator |
| annotation_status | automatic, self_checked, or expert_reviewed |

Example identifiers must be assigned before splitting. A source sentence must
not be split into multiple partitions.

## 7. Raw DCS Archive

The local archive audit currently observes:

- 441,735 unique pickle data records.
- Two ancillary Python files in the ZIP.
- 441,735 extracted pickle data records.
- No missing or duplicate record basenames.
- The sampled records use legacy protocol-0 pickles with a DCS object and
  fields such as sentence, lemmas, dcs_chunks, cng, and sent_id.

These counts establish local file integrity. The exact ZIP is additionally
matched to Zenodo record 803508 by filename, byte size, and MD5, with a local
SHA-256 in `datasets/dcs_source_manifest.json`. Zenodo identifies the record as
CC BY 4.0 and the manifest records the creators, DOI, citation, and attribution
conditions. These provenance facts do not establish annotation quality or
suitability for automatic boundary conversion.

Never directly call pickle.load on these records. The audit script inspects
pickle opcodes without constructing serialized Python objects:

    python3 scripts/audit_dcs_archive.py --sample 100

The archive contains sentence analyses, not a ready-made set of 441,735
external vowel-sandhi labels. A conversion stage must identify candidate
two-word boundaries, normalize the script, align forms and lemmas, attach an
EVS rule, preserve the source identifier, and reject ambiguous automatic
alignments for review.

## 8. Dataset Construction

### 8.1 Source Strata

Build two clearly labeled strata:

- **Attested:** boundaries extracted from a licensed corpus with stable source
  identifiers.
- **Controlled:** examples generated from lexemes partitioned before
  generation, then reviewed for rule application.

Never describe automatically generated material as attested. Never use
controlled test lexemes to generate training pairs.

### 8.2 Normalization

Choose one internal transliteration before annotation and freeze it. NFC
Unicode normalization and surrounding-whitespace removal are mandatory.
Case folding is forbidden unless the selected transliteration formally makes
it safe. Store original source text alongside normalized text.

The normalization version belongs in every dataset manifest. Changing
normalization invalidates all existing splits.

### 8.3 Deduplication

Deduplicate before splitting using all of these keys:

- Source record and target span.
- Normalized surface plus normalized left and right forms.
- Ordered normalized lemma pair plus rule identifier.
- Exact context hash.

Near-duplicate verses or repeated editions require a work-level or source-level
group identifier so variants cannot cross partitions.

### 8.4 Annotation

Automatic alignment may create draft labels. A publication test set must be
expert-reviewed or adjudicated. Reviewers must see the original context,
proposed split, rule trace, and source reference. Record disagreements rather
than silently overwriting them.

## 9. Evaluation Splits

Use all three primary splits. They answer different questions and must not be
collapsed into one number.

### 9.1 Random Source-Grouped Split

Assign source sentences or source groups, not individual boundaries, to
80/10/10 train/dev/test. This provides continuity with conventional
evaluation but can reward lexical memorization.

### 9.2 Exact Pair Holdout

Hash the ordered normalized pair:

    left_lemma || separator || right_lemma

All occurrences of a pair must remain in one partition. Individual lemmas may
still occur with other partners. This tests unseen combinations but not unseen
vocabulary.

### 9.3 Strict Lexical Holdout

This is the main answer to memorized word-pair inflation:

1. Normalize all left and right lemmas.
2. Hash each distinct lemma with a fixed seed.
3. Assign each lemma to exactly one of train, dev, or test.
4. Keep an example only when both lemmas have the same assignment.
5. Put cross-assignment examples in a mixed file; never silently discard them.
6. Assert that train, dev, and test lemma intersections are empty.
7. Report retained, mixed, and per-rule counts in a manifest.

Because an example has two endpoints, the implementation derives lemma bucket
proportions from the square roots of the requested example proportions. This
improves the expected 80/10/10 example balance under independent endpoints.
Real lexical graphs are not independent, so actual counts must be reported and
must never be hand-adjusted after seeing test outcomes.

Build the split with:

    python3 scripts/build_lexical_holdout.py \
      data/processed/examples.jsonl \
      data/processed/strict-lexical

The generated manifest includes the input SHA-256 digest, split seed, requested
ratios, lemma bucket ratios, record counts, rule counts, and lexical-overlap
assertions.

### 9.4 Source Holdout

When work identifiers are available, reserve entire works or editions as a
secondary robustness test. This detects leakage from repeated passages and
source-specific orthography. Do not substitute this for strict lexical
holdout; it tests a different failure mode.

## 10. Candidate Generator

For each surface boundary, apply all type-compatible operational rules and
return all legal analyses. Resolve conflicts using explicit precedence, not
file order. Optional rules may create multiple candidates.

Each candidate carries a proof object:

- Operational rule identifier.
- Source sūtra identifiers.
- Input left and right forms.
- Matched suffix and prefix.
- Required and observed tags.
- Boundary rewrite.
- Reconstructed surface.

The candidate generator must reject any candidate whose forward application
does not reconstruct the observed surface. Candidate recall and candidate-set
size are reported before neural training.

## 11. Neural Ranker

Initial target configuration:

| Component | Value |
| --- | --- |
| Architecture | Encoder-only candidate scorer |
| Layers | 4 |
| Hidden width | 128 |
| Attention heads | 4 |
| Feed-forward width | 512 |
| Input unit | Character or byte, fixed before training |
| Context | Left and right sentence context |
| Candidate features | Forms, rule ID, tags, and trace features |
| Parameter target | Approximately one million; report exact count |

Serialize one candidate with explicit segment markers for context, observed
surface, proposed left and right forms, rule identifier, and tags. Score each
candidate independently, then normalize scores within that example's
candidate set.

Select architecture and optimization settings on development data only.
Record optimizer, learning rate, batch size, maximum length, early-stopping
rule, seed, epochs, parameter count, wall time, peak RAM, and peak VRAM.

## 12. Baselines

Run at least these baselines under identical splits:

- **B0 majority rule:** most frequent training rule, with deterministic
  candidate tie-breaking.
- **B1 symbolic only:** candidate generator ranked by precedence and training
  frequency, without a neural model.
- **B2 n-gram ranker:** character and lemma-frequency features.
- **B3 tiny unconstrained Transformer:** matched parameter budget, directly
  predicts the split.
- **B4 constrained ranker without rule features:** candidate forms and context
  only.
- **P proposed:** constrained ranker with typed rule and trace features.

External systems such as Vidyut or TransLIST may be added only when inputs,
training data, and metrics can be aligned. Do not compare published scores
from different datasets as if they were head-to-head results.

## 13. Training Matrix

For each learned model run:

- Data sizes: 250, 1,000, 5,000, and all training examples.
- Splits: random source-grouped, pair holdout, and strict lexical holdout.
- Seeds: five fixed seeds.
- Hyperparameters: selected once on the corresponding development split.
- Test sets: untouched until configuration is frozen.

If compute is constrained, run all baselines and ablations on three seeds
first, then repeat the frozen final configuration on five seeds.

## 14. Metrics

### 14.1 Symbolic Layer

- Gold candidate recall.
- Mean and percentile candidate-set size.
- Forward reconstruction pass rate.
- Rule coverage and examples per rule.
- Failure reasons for missing gold candidates.

### 14.2 End-to-End

- Exact pair match.
- Exact rule-and-pair match.
- Top-3 candidate recall.
- Macro exact match across rules.
- Micro exact match across examples.
- Subset-compliance rate.
- Coverage at the selected abstention threshold.
- Risk-coverage curve.

### 14.3 Efficiency

- Exact trainable and total parameter counts.
- CPU and GPU training wall time.
- Peak RAM and VRAM.
- Median and p95 inference latency.
- Serialized checkpoint size.

Never report only accuracy. A system that omits difficult cases can appear
accurate; coverage and abstention must accompany it.

## 15. Ablations

Run these ablations on the frozen configuration:

- Remove sentence context.
- Remove rule identifiers and typed tags.
- Remove trace features.
- Replace hard candidate restriction with unconstrained output.
- Randomize rule identifiers while preserving candidate forms.
- Train on random split and evaluate on strict lexical test.

The last two checks help identify label leakage and lexical memorization.

## 16. Statistical Analysis

Report mean and standard deviation across seeds. Use paired bootstrap
confidence intervals over test examples for differences in exact match.
Because rules vary in frequency, report both macro and micro scores.

Do not tune thresholds on test data. Freeze the development-selected
abstention threshold and include it in the run manifest.

## 17. Expert Evaluation

Target a blinded, stratified sample of at least 200 system outputs:

- At least eight examples from each of the 25 rules when available.
- A mix of correct, incorrect, and abstained cases.
- Both random and strict lexical holdouts.
- Two qualified reviewers when feasible.

Ask reviewers separately whether the split is acceptable, the cited rule is
applicable, and the trace is sufficient. Report raw agreement and Cohen's
kappa when two reviewers are available. Preserve reviewer comments as an
error-analysis artifact.

## 18. Test Ladder

### Gate A: Code

    python3 -m pytest tests -q

All tests must pass from a clean checkout.

### Gate B: Rules

    python3 scripts/validate_rules.py --expected-count 25 --publication-ready

No draft rule can enter a reported experiment.

### Gate C: Corpus

    python3 scripts/audit_dcs_archive.py --sample 1000
    python3 scripts/build_sandhi_sutra_corpus.py \
      --source-dir vendor/ashtadhyayi-data

The DCS source manifest must contain no placeholders and the audit must report
zero identity problems. The rebuilt all-sandhi artifact must match its
committed SHA-256, preserve 148/108/40 counts, and keep every generated record
at `source_candidate`. No modern grammar annotation may enter a released
artifact until its rights are authoritatively confirmed.

### Gate D: Splits

- Zero exact duplicates across train/dev/test.
- Zero source-group overlap for the random split.
- Zero exact pair overlap for the pair holdout.
- Zero normalized lemma overlap for the strict holdout.
- Per-rule test coverage reported.

### Gate E: Symbolic Coverage

Gold candidate recall at least 95 percent overall. Any rule below 90 percent
must be repaired or excluded with a predeclared rationale.

### Gate F: Experiment

- All baselines complete.
- All five final seeds complete.
- Results regenerated from saved predictions.
- Run manifests include code, data, rules, and split hashes.

### Gate G: Scholarship

- Expert review complete.
- Limitations and disagreements reported.
- Related work and dataset licenses verified.
- No result placeholder remains in the manuscript.

## 19. Minimum Publishable Result

The paper becomes a candidate for archival submission only when it contains:

- A frozen, expert-reviewed 25-rule inventory.
- A licensed and fully documented dataset.
- A strict lexical holdout with zero leakage.
- At least 500 strict-holdout test examples and at least 20 examples for every
  rule included in macro evaluation.
- Reproducible baselines and ablations.
- Measured accuracy, coverage, efficiency, and uncertainty.
- Expert analysis of at least 200 outputs.
- Released code, configuration, manifests, and non-restricted derived data.

If per-rule support is insufficient, report only supported rules and describe
the smaller scope in the title and abstract.

## 20. Immediate Work Queue

| Order | Deliverable | Owner needed | Completion test |
| --- | --- | --- | --- |
| 1 | Screen 148 all-sandhi source candidates | Pāṇinian scholars | Every record has an adjudicated scope decision |
| 2 | Confirm upstream rights for modern grammar annotations | Data owner plus upstream | Authoritative license evidence archived |
| 3 | Author 25 typed pilot rule drafts | Grammar collaborator | Structural validator passes |
| 4 | Review rule interpretation and examples | Pāṇinian scholar | Publication rule gate passes |
| 5 | Convert DCS analyses to candidate boundaries | Engineer plus reviewer | Audited JSONL and rejection log |
| 6 | Freeze normalization and deduplication | Project team | Data tests pass |
| 7 | Build three split families | Engineer | Leakage assertions are zero |
| 8 | Implement candidate lattice and precedence | Engineer | Candidate recall gate passes |
| 9 | Train baselines and tiny ranker | ML collaborator | Run matrix complete |
| 10 | Conduct blinded expert audit | Sanskrit reviewers | Agreement and comments recorded |
| 11 | Replace manuscript placeholders | Authors | Reproducible paper build |
