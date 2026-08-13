# Historical Paninian Engine Architecture Note

The earlier dual-path Constructor and Auditor plan combined translation,
grammar correction, script conversion, morphology, syntax, and literary
generation. It was too broad for one falsifiable experiment and is not the
current research system.

For the first paper, Paninian Engine means only:

    external vowel boundary
             |
             v
    typed reviewed rule inventory
             |
             v
    valid candidate analyses and proofs
             |
             v
    tiny contextual ranker
             |
             v
    verified subset candidate or abstention

Verified means that the output executes under the encoded subset and
reconstructs the observed surface. It does not mean universally correct
Sanskrit.

See docs/approach-to-solution.md for the active design and
docs/EXPERIMENT_PROTOCOL.md for its evaluation.
