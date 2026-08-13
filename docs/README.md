# Documentation

This directory contains only the active research specification and
collaboration guides for the current neuro-symbolic sandhi experiment.

## Start Here

| Document | Purpose |
| --- | --- |
| [Working paper](panini-neuro-symbolic-ai.md) | Manuscript being developed for archival submission |
| [Experiment protocol](EXPERIMENT_PROTOCOL.md) | Research questions, frozen-study design, metrics, and release gates |
| [All-sandhi dataset](ALL_SANDHI_DATASET.md) | Reproducible 148-record source corpus and expert-screening workflow |
| [Rule authoring guide](RULE_AUTHORING_GUIDE.md) | Convert reviewed interpretations into typed executable rules |
| [Solution approach](approach-to-solution.md) | Current architecture, implementation sequence, and decision gates |
| [Contributing](contributing.md) | Contribution boundaries and review requirements |

For setup and verification, use the repository-level
[Quick Start](../QUICKSTART.md) and [Verification Guide](../COMPILE_AND_TEST.md).
Corpus-specific requirements are in [datasets/README.md](../datasets/README.md).

## Scope

The broad language-model, translation, literary-generation, and universal
grammar-engine plans from early project drafts are retired. They are available
from Git history if needed but are intentionally absent from the current
documentation tree.

The current source corpus spans sandhi families, while the first executable
and measured benchmark remains external vowel-sandhi splitting until broader
rules receive expert operational review. No document in this directory should
describe source candidates as automatically executable rules or subset
compliance as complete Sanskrit correctness.
