# Current Solution Architecture

The original solution architecture targeted quantized 7B models, LoRA
training, and end-user translation and correction. It is superseded for the
first paper.

## Components

| Component | Responsibility | Status |
| --- | --- | --- |
| Typed rule loader | Validate source, match, rewrite, examples, review | Implemented |
| Proof executor | Apply one rule and emit trace | Implemented |
| Corpus auditor | Compare ZIP/extraction and inspect opcodes safely | Implemented |
| Strict split builder | Partition lemmas and assert no overlap | Implemented |
| Safe corpus converter | Produce normalized boundary JSONL | Planned |
| Candidate compiler | Enumerate all licensed inverse analyses | Planned |
| Baselines | Majority, symbolic frequency, n-gram, unconstrained | Planned |
| Tiny ranker | Contextual score per candidate | Planned |
| Evaluator | Metrics, abstention, uncertainty, resources | Planned |
| Expert audit | Rule and trace judgments | Planned |

## Compute Target

Rule validation, corpus conversion, splitting, and symbolic baselines run on
CPU. The neural target is a four-layer, width-128 encoder with four attention
heads and a 512-wide feed-forward block. Report the exact parameter count and
measured memory; do not infer efficiency from architecture names.

## Artifact Flow

    pinned sources
          |
          v
    reviewed rules + licensed corpus
          |
          v
    normalized and deduplicated examples
          |
          v
    frozen split manifests
          |
          v
    candidate sets and proofs
          |
          v
    baseline and ranker predictions
          |
          v
    metrics, expert judgments, and paper tables

Every transition has a manifest, hash, test, or review gate. See
docs/EXPERIMENT_PROTOCOL.md for complete acceptance criteria.
