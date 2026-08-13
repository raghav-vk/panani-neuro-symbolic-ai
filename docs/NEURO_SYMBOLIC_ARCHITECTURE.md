# Historical Neuro-Symbolic Architecture Note

This file previously described a broad progression from a 7B language model
to constrained decoding, tree search, knowledge graphs, and poetry generation.
That design is not the architecture evaluated by the first paper.

The active architecture is:

- A reviewed typed subset of external vowel-sandhi rules.
- A symbolic candidate generator with forward reconstruction.
- A proof trace for every candidate.
- A roughly one-million-parameter contextual candidate ranker.
- Explicit abstention.
- Random, pair, and strict unseen-lemma evaluation.

Current specifications:

- docs/EXPERIMENT_PROTOCOL.md
- docs/approach-to-solution.md
- docs/panini-neuro-symbolic-ai.md
- docs/RULE_AUTHORING_GUIDE.md

Historical claims of mathematical perfection, 100 percent Sanskrit grammar,
or guaranteed poetry quality are withdrawn. The only intended invariant is
compliance with the encoded and tested subset, subject to the correctness of
its data, tags, interpretation, and implementation.
