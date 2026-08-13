# Focused Solution Approach

**Current measured scope:** External vowel-sandhi candidate generation and
ranking
**Source scope:** Reproducible candidates across all sandhi families
**Supersedes for the first paper:** The broad translation, correction,
literary-generation, 7B-model, and guaranteed-correctness plans

## 1. Design Principle

Use symbolic and neural computation where each is testable:

- The symbolic layer defines which analyses are licensed by the frozen rule
  subset.
- The neural layer ranks licensed analyses using context.
- The verifier reconstructs the observed surface.
- The system abstains when its rule coverage or confidence is insufficient.
- The proof trace makes each accepted analysis auditable.

The first study does not train a neural model to reproduce rule tables from
examples. The rules remain explicit and inspectable.

## 2. System Boundary

Input:

- One observed fused external vowel boundary.
- Optional sentence context on both sides.
- Available grammatical and lexical tags.

Output:

- Left pre-sandhi form.
- Right pre-sandhi form.
- Operational EVS rule identifier.
- Source sūtra identifiers.
- Forward-reconstruction proof.
- Confidence or explicit abstention.

Out of scope:

- Full Sanskrit sentence generation.
- English translation.
- Universal grammar correction.
- Complete Aṣṭādhyāyī implementation.
- Claims of perfect Sanskrit.

## 3. Architecture

    source corpus and reviewed controlled examples
                         |
                         v
              normalized boundary records
                         |
                         v
             leakage-resistant split builder
                         |
                         v
       typed rules ---> candidate compiler
                         |
                         v
            candidates plus proof traces
                         |
                         v
             tiny contextual encoder ranker
                         |
                         v
          verifier and abstention controller
                         |
                         v
            predictions and audit artifacts

## 4. Typed Rule Layer

The grammar artifacts have two layers:

- A generated 148-record all-sandhi source inventory for screening and
  dependencies.
- A manually operationalized, independently reviewed executable inventory.

The generated layer never promotes chapter membership to computational
semantics. A source record can map to zero, one, or several executable records.

The rule record is deliberately stronger than a character substitution table.
It contains:

- Stable identity and review status.
- Pinned source text, revision, and license.
- Operational interpretation.
- Boundary match classes.
- Required and forbidden typed tags.
- Explicit keep, drop, and emit operations.
- Precedence and optionality.
- Positive examples and counterexamples.
- Independent review metadata.

The loader rejects unknown fields and validates positive examples by executing
the rewrite. Publication mode enforces 25 unique, reviewed, sourced records.

Current implementation:

    src/panini/rules.py

Current inventory:

    data/rules/external_vowel_sandhi.jsonl

The current inventory contains one draft example. Candidate-lattice
development should not assume that draft is linguistically approved.

All-sandhi source inventory:

    data/sources/ashtadhyayi_sandhi_sutras.jsonl

## 5. Data Layer

### 5.1 Raw Corpus

The DCS_pick archive is a legacy collection of per-sentence protocol-0
pickles. The archive is locally complete and matches Zenodo record 803508 by
filename, size, and MD5; its record is CC BY 4.0. No code should directly
execute serialized constructors, and provenance does not imply annotation
quality.

### 5.2 Safe Conversion

The next data-engineering component must use an opcode allow-list and a
restricted record decoder or a non-pickle upstream source. It should produce
JSONL plus a rejection log.

Conversion stages:

1. Validate archive and source manifest.
2. Decode only the expected primitive record structure.
3. Preserve original sentence and identifier.
4. Normalize transliteration with a versioned transform.
5. Detect candidate external vowel boundaries.
6. Align observed surface to lexical forms and lemmas.
7. Match one or more typed rules.
8. Require forward reconstruction.
9. Mark automatic confidence and route ambiguity to review.

The converter must report how many raw sentences produce no boundary,
unsupported boundaries, ambiguous alignments, or accepted examples.

### 5.3 Data Splits

Build random, exact-pair, and strict lexical splits from the same deduplicated
examples. The strict split implementation already exists:

    src/panini/splits.py

It assigns lemmas before examples, writes cross-partition examples to mixed,
and asserts zero train/dev/test lexical overlap.

## 6. Candidate Compiler

The next symbolic component will:

1. Index rules by boundary class.
2. Check required and forbidden tags.
3. Apply all compatible rules.
4. Resolve specificity and precedence explicitly.
5. Preserve licensed alternatives for optional rules.
6. Reconstruct the surface for every candidate.
7. Reject candidates that do not reconstruct.
8. Emit a stable proof object.

Candidate recall is the compiler's primary metric. If the gold analysis is
absent, neural ranking cannot solve the example.

## 7. Tiny Neural Ranker

Initial configuration:

| Setting | Value |
| --- | --- |
| Encoder layers | 4 |
| Hidden width | 128 |
| Attention heads | 4 |
| Feed-forward width | 512 |
| Input | Character or byte |
| Output | One scalar per candidate |
| Parameter target | About one million |

One training item is a set of candidates for one surface boundary. The loss is
cross-entropy over candidate scores, not free-form string generation.

The ranker receives:

- Context.
- Observed surface.
- Candidate left and right forms.
- Rule identifier.
- Typed tags.
- Compact trace features.

This design keeps inference inside the symbolic candidate set and permits a
matched unconstrained ablation.

## 8. Abstention

Abstention is a first-class output, not an error hidden by fallback behavior.
Calibrate its threshold on development data. Report:

- Accuracy among accepted outputs.
- Coverage.
- Risk-coverage curve.
- No-candidate rate.
- Low-confidence rate.
- Failure categories by rule.

The legacy toy generator concatenates unsupported inputs. That behavior is
retained only for compatibility tests and is forbidden in reported
experiments.

## 9. Implementation Sequence

### Milestone 1: Rule Contract

Implemented:

- Schema.
- Typed loader.
- Positive-example execution.
- Proof traces.
- Publication gates.
- Pinned 148-record all-sandhi source inventory and deterministic generator.

Remaining:

- Twenty-four additional draft records.
- Controlled tag vocabulary.
- Expert review.
- Precedence tests across overlaps.

### Milestone 2: Corpus Contract

Implemented:

- Archive integrity and opcode audit.
- Verified DCS provenance, checksums, citation, and CC BY 4.0 manifest.

Remaining:

- Safe decoder.
- Boundary extractor.
- Rejection taxonomy.
- Reviewed derived-example sample.

### Milestone 3: Evaluation Splits

Implemented:

- Strict lemma-first partition.
- Mixed-edge preservation.
- Deterministic manifest.
- Zero-overlap tests.

Remaining:

- Source-grouped random split.
- Exact-pair holdout.
- Duplicate-group detection.
- Per-rule minimum-coverage gate.

### Milestone 4: Symbolic Lattice

Remaining:

- Rule index and candidate inverse generation.
- Precedence and optionality.
- Candidate-set serialization.
- Candidate recall report.

### Milestone 5: Models

Remaining:

- Majority, symbolic-frequency, and n-gram baselines.
- Parameter-matched unconstrained encoder.
- Full candidate ranker.
- Checkpoint and run manifests.

### Milestone 6: Research Evaluation

Remaining:

- Five-seed run matrix.
- Data-efficiency curves.
- Ablations.
- Bootstrap confidence intervals.
- Resource measurements.
- Blinded expert audit.
- Error taxonomy.

## 10. Decision Gates

Pause and revise rather than train when:

- A source used in the frozen experiment has unresolved rights. DCS is
  resolved; copied modern ashtadhyayi-com annotations are not.
- The 25-rule publication validator fails.
- Strict split leakage is nonzero.
- A rule has fewer than 20 strict test examples.
- Overall candidate recall is below 95 percent.
- A major source or normalization change occurs after split freeze.

Pause and narrow the paper when:

- Expert review rejects material parts of the inventory.
- The corpus cannot reliably distinguish external vowel boundaries.
- Most strict examples are withheld as mixed.
- Baselines cannot be reproduced under the same data contract.

## 11. Why This Can Be Archival

A small system can still be substantive when the experiment establishes:

- A reusable typed scholarly rule artifact.
- A clear validity boundary.
- A hard unseen-lemma benchmark.
- Candidate-coverage versus ranking analysis.
- Matched baselines and ablations.
- Compute and data-efficiency measurements.
- Expert judgments and documented disagreements.
- Reproducible manifests and predictions.

The paper's value will come from this evidence, not from broad promises or the
number of model parameters.
