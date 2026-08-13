# Legacy Toy Generator

src/generator/sandhi_generator.py is retained so the original examples and
compatibility tests continue to run. It contains hard-coded word pairs, a
small character table, and fallback concatenation.

It is not the symbolic engine for the research paper and must not generate
reported training or test data.

Use these components for current work:

- src/panini/rules.py for typed rules and proof traces.
- data/rules/external_vowel_sandhi.jsonl for the reviewed inventory.
- docs/RULE_AUTHORING_GUIDE.md for scholarly authoring.
- docs/EXPERIMENT_PROTOCOL.md for candidate and evaluation requirements.

Legacy tests remain useful only for guarding the historical API:

    python3 -m pytest tests/test_sandhi_generator.py -q
