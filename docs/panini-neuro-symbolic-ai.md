# Proof-Carrying External Vowel-Sandhi Splitting with Typed Pāṇinian Rules and a Tiny Transformer

**Author:** Raghavendra V. Karnam
**Working manuscript version:** 0.3, August 2026
**Repository:** https://github.com/raghav-vk/panini-neuro-symbolic-ai
**Status:** Experimental protocol and implementation in progress

> This version is not ready for arXiv resubmission. It contains a complete
> study design but no measured model results or completed expert evaluation.
> All TBD cells must be replaced from reproducible runs before submission.

## Abstract

Sanskrit word segmentation is difficult because sandhi can alter characters
at word boundaries and can permit multiple analyses of the same surface form.
Purely neural systems can exploit context but may produce analyses unsupported
by the intended grammatical subset; purely symbolic systems can enumerate
licensed candidates but require a method for contextual ranking. This work
studies a deliberately narrow neuro-symbolic architecture for one phenomenon:
external vowel-sandhi splitting under a reviewed inventory of 25 operational
rules. A typed symbolic layer matches boundary conditions, constructs valid
candidate analyses, and attaches a proof trace containing the operational rule
and source sūtra identifiers. A small encoder-only Transformer, targeted at
approximately one million parameters, ranks these candidates from sentence
context. The evaluation is designed to separate candidate coverage from
ranking quality and to distinguish random, unseen-pair, and strict unseen-lemma
generalization. It includes symbolic and neural baselines, data-efficiency
curves, ablations, abstention analysis, resource measurements, and blinded
expert review. A separately versioned source layer inventories 148 sandhi-related
sūtra candidates across two pedagogical classifications, including 108
operative candidates and 40 supporting records; these are an expert review
queue, not automatically executable rules. This manuscript specifies the
system and preregistered evaluation; empirical results are pending and no claim
of general Sanskrit grammatical correctness is made.

## 1. Introduction

The Aṣṭādhyāyī provides a compact rule system whose interpretation depends on
technical vocabulary, inherited context, ordering, exceptions, and scholarly
traditions. This structure makes Sanskrit an attractive setting for
neuro-symbolic computation, but it does not make the engineering problem
automatic. A list of sūtras is not a training dataset, and a short table of
character substitutions is not a faithful implementation of Pāṇinian grammar.

Earlier versions of this project proposed a broad Sanskrit language model,
English-to-Sanskrit translation, grammatical correction, literary generation,
and guarantees of perfect output. Those goals were too broad to evaluate in
one paper and were not supported by experiments. The present work replaces
that proposal with a falsifiable question:

> Can a very small contextual model improve the ranking of analyses that are
> explicitly licensed by a typed, expert-reviewed external vowel-sandhi
> subset, especially when test lemmas never occur in training?

External vowel sandhi is narrow enough to encode and audit, yet difficult
enough to expose the central division of labor. Boundary rules determine which
analyses are licensed by the subset. Context and lexical plausibility determine
which licensed analysis is preferred. The proposed system therefore does not
ask a Transformer to learn the rules implicitly or generate arbitrary output.
It asks the Transformer to rank a symbolic candidate set.

The intended contributions are:

1. A reproducible, pinned 148-record source inventory spanning all sandhi
   families, with explicit selection evidence and conservative candidate
   status.
2. A strongly validated JSONL representation for operational external
   vowel-sandhi rules, including source revision, conditions, exceptions,
   precedence, positive examples, counterexamples, and review metadata.
3. A symbolic candidate interface that reconstructs the observed surface and
   emits a compact proof trace for every accepted analysis.
4. A tiny contextual candidate ranker designed for training on minimal
   hardware.
5. A lexical-holdout protocol that partitions lemmas before examples and
   proves that train, development, and test vocabularies are disjoint.
6. An evaluation plan that reports candidate recall, exact analysis, subset
   compliance, abstention, compute, uncertainty, and expert judgments.

The contribution is an experimental system for a bounded rule inventory, not
a complete computational grammar and not a claim that neural-symbolic
composition guarantees Sanskrit correctness in general.

## 2. Related Work

### 2.1 Sanskrit Word Segmentation

Krishna, Satuluri, and Goyal formalized a Sanskrit word-segmentation benchmark
and released 115,000 sentences with ground-truth segmentation and lexical and
morphological candidate information. Their work emphasizes that task
definitions, candidate spaces, and evaluation criteria must be aligned
[Krishna et al., 2017].

Hellwig and Nehrdich modeled Sanskrit word splitting with character-level
recurrent and convolutional networks. Their formulation uses sentence context
to judge semantically plausible splits and demonstrates the value of learned
character representations [Hellwig and Nehrdich, 2018].

TransLIST combines Transformer representations with latent-word information,
soft-masked attention, and post-ranking of candidate paths. It is the closest
architectural comparison because it also combines learned representations with
linguistically informed candidates [Sandhan et al., 2022]. The present study
does not claim novelty merely from using a Transformer and a candidate lattice.
Its empirical distinction must come from hard subset validity, a typed and
reviewed rule interface, proof traces, strict lexical evaluation, and a much
smaller measured parameter and compute budget.

### 2.2 Symbolic Sanskrit Software and Data

The Sanskrit Heritage platform has motivated a line of finite-state,
lexicon-driven candidate generation used by segmentation research. Vidyut is
an open-source Sanskrit software ecosystem that implements a large
Aṣṭādhyāyī-based derivational subset and provides sandhi and segmentation
components. It is a valuable implementation reference and potential baseline,
but agreement with Vidyut alone is not treated as scholarly validation of this
project's operational rules.

The ashtadhyayi-com data repository contains digital material used by
ashtadhyayi.com, including sūtra and commentary data. From pinned commit
`51bff9fb38c6f571b4a2bc8499d97576f00ffcce`, this project deterministically
selects 148 sandhi-related source records using the union of the relevant
Siddhānta Kaumudī and Laghu Siddhānta Kaumudī chapter assignments. It records
the exact file and commit rather than treating the repository as an unversioned
grammar oracle. The repository snapshot contains no license file, so its
author-reported Apache-2.0 status remains unverified and modern commentary is
not copied into the released source inventory.

The Digital Corpus of Sanskrit provides morphologically analyzed Sanskrit
material. The local legacy archive examined for this project is verified as
the `DCS_pick.zip` artifact in Zenodo record 803508 by filename, byte size, and
MD5, and the record is licensed CC BY 4.0. Its hundreds of thousands of
sentence analyses still require a separate safe parsing and alignment step
before they become external vowel-sandhi examples.

### 2.3 Positioning

The proposed design follows a constrained-ranking view:

- Symbolic knowledge defines a permitted candidate set.
- A neural encoder estimates contextual preference within that set.
- A trace records why a candidate was admitted.
- Abstention handles insufficient symbolic coverage or low ranking confidence.

The study's scientific value depends on demonstrating measurable advantages
under controlled baselines and leakage-resistant evaluation. Architecture
description alone is insufficient.

## 3. Scope and Claims

### 3.1 Included

- External sandhi at a single vowel boundary.
- A target inventory of 25 expert-reviewed operational rules.
- One frozen internal transliteration.
- Candidate generation and contextual ranking.
- Random, exact-pair, strict lexical, and optional source holdouts.
- Proof traces relative to the encoded subset.

### 3.2 Excluded

- Internal sandhi and compound segmentation unless explicitly added before the
  protocol freeze.
- Executable consonant, visarga, and nasal/anusvāra rules outside the reviewed
  pilot inventory. Their sūtra candidates remain available in the broader
  source layer for staged expansion.
- Full sentence segmentation as the primary task.
- Morphological generation, kāraka analysis, translation, correction, and
  literary generation.
- Vedic-only rules unless declared as a separate evaluation stratum.
- Claims of complete Pāṇinian or semantic correctness.

### 3.3 Guarantee Boundary

For a non-abstained output, the system can guarantee only that:

1. An encoded rule matched the supplied boundary and typed tags.
2. No encoded forbidden tag was present.
3. Executing the recorded rewrite reconstructed the observed surface.
4. The proof identifies the operational record and its declared source.

This is subset compliance. It can still be linguistically wrong if the rule
inventory, tags, lexical analysis, source interpretation, or implementation is
wrong or incomplete. Expert evaluation is therefore part of the study rather
than an optional endorsement after it.

## 4. Task Formulation

Let x be an observed surface span, c its sentence context, t a set of typed
grammatical tags, and R the frozen rule inventory. The symbolic component
enumerates:

    C_R(x, t) = {z_1, z_2, ..., z_k}

Each candidate z contains a left form, right form, operational rule, and proof
trace. Every z in the set must reconstruct x under its recorded rewrite.

The neural ranker computes:

    score_theta(c, x, z) in the real numbers

and estimates a distribution over candidates in the same set:

    p_theta(z | c, x, C_R) = softmax(score_theta(c, x, z))

At inference, the model returns the highest-scoring candidate only when its
development-calibrated confidence exceeds threshold tau. Otherwise it
abstains.

Evaluation separates:

- **Candidate recall:** whether the gold z is in C_R.
- **Conditional ranking accuracy:** whether the model ranks gold first when it
  is present.
- **End-to-end accuracy:** whether the final output is exactly correct over all
  examples.
- **Selective performance:** accuracy and error risk as coverage changes with
  tau.

## 5. Typed Rule Representation

Each operational rule has:

- A stable EVS-NNN identifier and scope.
- Draft, self-checked, or expert-reviewed status.
- One or more source sūtra identifiers.
- Source text, URL, immutable commit, and license.
- An explicit operational interpretation.
- Left suffix and right prefix classes.
- Required and forbidden grammatical tags.
- A boundary operation specifying which matches are kept or dropped and what
  string is emitted.
- Precedence and optionality.
- Positive examples, counterexamples, notes, and review metadata.

Unknown fields are rejected. Positive examples execute during loading and fail
validation if their declared surface differs from the rewrite output.
Publication mode rejects draft rules, unresolved licenses, unpinned source
revisions, missing review, and insufficient examples.

The current repository contains one illustrative draft. It is not a completed
inventory and must not be used to claim 25-rule coverage.

## 6. Symbolic Candidate Layer

### 6.1 Matching

The compiler normalizes input using a frozen versioned transform, checks typed
tags, and finds matching boundary suffixes and prefixes. Longest boundary
strings are matched first within a rule. Rule conflicts are resolved by
explicit precedence rather than source-file order.

### 6.2 Candidate Construction

For each applicable rule, the engine constructs the unsandhied pair, executes
the forward rewrite, and keeps the analysis only if the resulting surface
equals the observation. Optional rules may contribute more than one licensed
candidate.

### 6.3 Proof Trace

Every candidate includes:

- Rule and source sūtra identifiers.
- Input forms and observed tags.
- Matched left and right boundary strings.
- Kept, dropped, and emitted boundary content.
- Reconstructed surface.
- Rule-inventory version.

The trace is intended for reproducibility and expert inspection. It is a
certificate of program execution against a declared subset, not a formal proof
that the grammatical interpretation is universally accepted.

### 6.4 Failure and Abstention

The system abstains when no candidate exists. It may also abstain when:

- The candidate set exceeds a predeclared safety limit.
- Required lexical or grammatical tags are unavailable.
- Multiple top candidates remain below a calibrated margin.
- The best score is below a development-selected threshold.

Failure categories are logged and reported rather than converted to fallback
concatenations or unconstrained neural guesses.

## 7. Neural Candidate Ranker

The initial ranker is a four-layer encoder with hidden width 128, four
attention heads, and feed-forward width 512. The exact parameter count depends
on the frozen input vocabulary and is reported from code. The target is
approximately one million parameters.

Each candidate serialization contains:

- Left sentence context.
- Observed surface.
- Right sentence context.
- Candidate left and right forms.
- Operational rule identifier.
- Typed condition tags.
- Compact proof features.

A learned classification representation is projected to one scalar score.
Scores are normalized only among candidates for the same example. This avoids
asking the model to generate arbitrary transliteration strings and makes every
ranked output inspectable.

The model uses character or byte inputs so rare Sanskrit forms do not become
unknown tokens. The choice, normalization, maximum sequence length, and
truncation policy are frozen before experiments. No pretrained language model
is required for the primary system.

## 8. Data

### 8.1 Grammar Source and Operational Rule Data

The generated all-sandhi source corpus contains 148 unique sūtra candidates
from pinned ashtadhyayi-com commit
`51bff9fb38c6f571b4a2bc8499d97576f00ffcce`. The reproducible inclusion
criterion is the union of records assigned by the source to Siddhānta Kaumudī
chapters 3-7 or Laghu Siddhānta Kaumudī chapters 2-3. Source type codes identify
108 operative candidates and 40 definitions, governing scopes, and
interpretive or transference principles. The artifact SHA-256 is
`6160267d448a6ab589e00f9582ee87ea3bc47fd42fafb37fa9b3a9dfe0f2ebab`.

All 148 records are marked `source_candidate`, require expert review, and have
no linked computational rules. This distinction prevents three unsupported
assumptions: that pedagogical chapter membership proves exhaustiveness, that
every selected sūtra independently performs a rewrite, or that one sūtra maps
to exactly one operational rule.

The 25-rule inventory will be authored from pinned sources and independently
reviewed. Each rule requires multiple positive examples and at least one
counterexample. Controlled examples belong to the symbolic specification and
cannot be introduced after test results are inspected.

### 8.2 Corpus Data

The local DCS_pick ZIP contains 441,735 unique pickle data records and two
ancillary Python files. All 441,735 data records are extracted. A non-executing
audit of 100 sampled pickle streams found the expected legacy DCS constructor
and no additional constructor opcodes. The local ZIP also matches Zenodo record
803508 by filename (`DCS_pick.zip`), byte size (199,818,951), and MD5
(`556395ddc0f087fbf0a199a0581775d0`). Its independently computed SHA-256 is
`7b13cc2fda84318cba23d9c7667cd3ea30600091e446dac43fae86ebe90e4e85`.
Zenodo records a CC BY 4.0 license. These facts establish provenance and local
integrity, not annotation accuracy.

The records include sentence, lemma grouping, chunk, morphology-code, and
sentence-identifier fields. They are sentence analyses rather than directly
labeled instances of this paper's task. The preprocessing pipeline must:

1. Check the local archive against the frozen verified manifest.
2. Parse records without executing untrusted constructors.
3. Preserve original identifiers and source strings.
4. Normalize to the frozen internal transliteration.
5. Identify two-lexeme external vowel boundaries.
6. Align the observed surface with left and right forms.
7. Attach an operational rule and proof.
8. Route ambiguous or unsupported cases to review or rejection.

The 53-example translation toy dataset from the original project is excluded
from all experiments.

### 8.3 Derived Example Schema

Every example stores stable example and source identifiers, context, surface,
left and right forms, left and right lemmas, operational rule, typed tags,
proof, provenance, and annotation status. Original and normalized text are
both retained.

### 8.4 Deduplication

Before splitting, the pipeline removes exact duplicate source spans, identical
surface-analysis triples, repeated ordered lemma-rule triples, and exact
context hashes. Near-duplicate editions are grouped by work or source so they
cannot cross partitions.

## 9. Lexical Holdout

A random split can overestimate performance when frequent forms or exact pairs
occur in both training and test data. The study therefore reports three
primary split families.

### 9.1 Source-Grouped Random

Source sentences, not isolated boundaries, are assigned 80/10/10 to
train/development/test. This is the easiest setting.

### 9.2 Exact-Pair Holdout

The ordered normalized pair of left lemma and right lemma is assigned as one
unit. Test pairs are unseen during training, but each individual lemma may
have appeared with another partner.

### 9.3 Strict Unseen-Lemma Holdout

Distinct normalized lemmas are assigned to partitions before examples.
An example enters train, development, or test only when both lemmas belong to
that partition. Cross-partition examples are retained in a mixed audit file
but are not used in the strict benchmark. The implementation asserts:

    V_train intersect V_dev = empty
    V_train intersect V_test = empty
    V_dev intersect V_test = empty

The split is deterministic from a fixed seed and logs its input hash, lemma
bucket ratios, retained counts, mixed count, rule counts, and overlap checks.
This prevents both exact-pair memorization and reuse of either constituent
lemma from inflating the strict result.

Strict splitting can remove many edges in a densely connected lexical graph.
That is an honest cost of the stronger question. The paper reports the mixed
rate and does not silently search seeds for a favorable test distribution.

## 10. Experimental Design

### 10.1 Baselines

- Majority operational rule.
- Symbolic candidate ranking by precedence and training frequency.
- Character n-gram and lexical-frequency ranker.
- Parameter-matched unconstrained tiny Transformer.
- Constrained candidate ranker without rule or trace features.
- Full typed constrained ranker.

Vidyut and TransLIST are optional external comparisons if their licenses,
input formats, data, and metrics can be aligned. Published results on a
different benchmark are cited as context, not copied into the main comparison
table.

### 10.2 Data Efficiency

Train learned systems on 250, 1,000, 5,000, and all available examples. Sample
training subsets once per seed while preserving the frozen development and
test sets. Run five final seeds.

### 10.3 Ablations

- No sentence context.
- No operational rule identifiers or typed tags.
- No proof features.
- No hard candidate constraint.
- Randomized rule identifiers.
- Random-split training evaluated on strict lexical test.

### 10.4 Metrics

Symbolic metrics are gold candidate recall, candidate-set size, forward
reconstruction rate, rule coverage, and missing-gold error category.

End-to-end metrics are exact pair match, exact pair-and-rule match, top-3
recall, macro and micro exact match, subset compliance, coverage, and
risk-coverage curves.

Efficiency metrics are parameter count, checkpoint size, wall-clock training
time, peak RAM, peak VRAM, median latency, and p95 latency.

### 10.5 Statistical Reporting

Report mean and standard deviation across seeds. Use paired bootstrap
confidence intervals over test examples for model differences. Select
hyperparameters and abstention thresholds on development data only.

## 11. Results

No model results have been measured for this version.

### 11.1 Dataset and Candidate Coverage

| Split | Train | Dev | Test | Mixed | Lemma overlap | Gold candidate recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Source-grouped random | TBD | TBD | TBD | not applicable | report | TBD |
| Exact-pair holdout | TBD | TBD | TBD | not applicable | allowed by design | TBD |
| Strict lexical | TBD | TBD | TBD | TBD | 0 required | TBD |

### 11.2 Main Comparison

| System | Parameters | Random exact | Pair exact | Strict exact | Compliance | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Majority rule | 0 | TBD | TBD | TBD | TBD | 100 percent |
| Symbolic frequency | 0 | TBD | TBD | TBD | 100 percent expected | TBD |
| Character n-gram | TBD | TBD | TBD | TBD | TBD | TBD |
| Tiny unconstrained Transformer | TBD | TBD | TBD | TBD | measured | 100 percent |
| Constrained without rule features | TBD | TBD | TBD | TBD | 100 percent expected | TBD |
| Proposed typed ranker | TBD | TBD | TBD | TBD | 100 percent expected | TBD |

Expected compliance values are architectural expectations and must still be
verified from saved predictions before replacing TBD.

### 11.3 Data Efficiency

| Training examples | Random exact | Pair exact | Strict exact | Train time |
| ---: | ---: | ---: | ---: | ---: |
| 250 | TBD | TBD | TBD | TBD |
| 1,000 | TBD | TBD | TBD | TBD |
| 5,000 | TBD | TBD | TBD | TBD |
| All | TBD | TBD | TBD | TBD |

### 11.4 Ablation

| Variant | Strict exact | Change | Interpretation |
| --- | ---: | ---: | --- |
| Full model | TBD | reference | TBD |
| No context | TBD | TBD | TBD |
| No rule or tag features | TBD | TBD | TBD |
| No trace features | TBD | TBD | TBD |
| No hard constraint | TBD | TBD | TBD |
| Randomized rule IDs | TBD | TBD | TBD |

## 12. Expert Evaluation

At least 200 outputs will be sampled across rules, split families, correctness
categories, and abstentions. When feasible, two reviewers with Pāṇinian
grammar expertise will independently judge:

- Whether the split is acceptable in context.
- Whether the operational rule applies.
- Whether the cited source is appropriate.
- Whether the proof trace is sufficient and understandable.

The paper reports acceptance rates, raw agreement, Cohen's kappa when two
reviewers participate, and a qualitative error taxonomy. Reviewer
disagreements remain visible and may motivate a narrower rule inventory.

## 13. Reproducibility

Every reported run must preserve:

- Code commit.
- Rule-inventory commit and SHA-256 digest.
- Source and derived-data manifests.
- Normalization and deduplication versions.
- Split method, seed, and manifest.
- Model configuration and exact parameter count.
- Optimizer, schedule, batch size, epochs, and early-stopping rule.
- Hardware, software versions, wall time, and memory.
- Predictions, proof traces, metric output, and bootstrap samples.

The test command is:

    python3 -m pytest tests -q

The current suite covers the typed loader, proof application, publication
gates, deterministic lexical splitting, zero lemma overlap, pickle-opcode
audit, all-sandhi source-corpus reproducibility, and legacy compatibility
tests.

## 14. Limitations and Risks

First, a 25-rule inventory represents only a small operational subset and may
not capture commentary-dependent interpretation, optionality, lexical
exceptions, or interactions required by expert analysis. The broader
148-record corpus is only a source review queue and does not remove this
limitation.

Second, corpus analyses can contain annotation errors and may not identify the
precise external boundary needed by this task. Automatic conversion can create
selection bias toward easy, unambiguous cases.

Third, strict lexical holdout changes the lexical and rule distribution and
withholds cross-partition examples. Both retained coverage and excluded mixed
examples must be reported.

Fourth, proof traces explain execution of encoded rules but do not establish
the truth or completeness of those rules. Trace faithfulness and grammatical
acceptability are separate evaluation questions.

Fifth, results on external vowel sandhi do not justify claims about full word
segmentation, morphology, syntax, translation, literary quality, or language
modeling.

Finally, the DCS archive's CC BY 4.0 terms are verified, but the claimed
Apache-2.0 status of the pinned ashtadhyayi-com snapshot is not evidenced by a
repository license file. If rights for modern annotations cannot be confirmed,
release only ancient source text, code, manifests, hashes, and reconstruction
instructions rather than copied commentary or translations.

## 15. Conclusion

This study replaces a broad proposal for a Sanskrit language model with a
bounded experiment whose claims can be falsified. A reproducible all-sandhi
source inventory creates a transparent path for expert-led expansion, while a
typed symbolic layer defines and traces the reviewed external-vowel pilot. A
tiny Transformer ranks only licensed candidates, and strict lexical evaluation
tests whether results survive removal of training vocabulary. The architecture
is lightweight by design, but archival value will come from completed
experiments, leakage controls, baselines, ablations, resource measurements,
and expert analysis. Until those results replace all placeholders, this
document remains a working protocol rather than a completed research article.

## References

Hellwig, Oliver, and Sebastian Nehrdich. 2018. Sanskrit Word Segmentation Using
Character-level Recurrent and Convolutional Neural Networks. Proceedings of
EMNLP 2018. https://aclanthology.org/D18-1295/

Krishna, Amrith, Pavan Kumar Satuluri, and Pawan Goyal. 2017. A Dataset for
Sanskrit Word Segmentation. Proceedings of the LaTeCH-CLfL Workshop.
https://aclanthology.org/W17-2214/

Krishna, Amrith, Pavankumar Satuluri, and Pawan Goyal. 2017. A Dataset for
Sanskrit Word Segmentation [dataset]. Zenodo. DOI: 10.5281/zenodo.803508.
https://zenodo.org/records/803508

Sandhan, Jivnesh, Rathin Singha, Narein Rao, Suvendu Samanta, Laxmidhar
Behera, and Pawan Goyal. 2022. TransLIST: A Transformer-Based Linguistically
Informed Sanskrit Tokenizer. Findings of EMNLP 2022.
https://aclanthology.org/2022.findings-emnlp.513/

Vaswani, Ashish, et al. 2017. Attention Is All You Need. Advances in Neural
Information Processing Systems 30.
https://papers.nips.cc/paper/7181-attention-is-all-you-need

ashtadhyayi-com contributors. Data powering ashtadhyayi.com.
https://github.com/ashtadhyayi-com/data

Ambuda contributors. Vidyut: Reliable infrastructure for Sanskrit software.
https://github.com/ambuda-org/vidyut

Ambuda contributors. Sanitized data from the Digital Corpus of Sanskrit.
https://github.com/ambuda-org/dcs
