"""End-to-end test for the lexical-holdout command."""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent
FIXTURE = (
    ROOT / "tests/fixtures/holdout_examples.jsonl"
)


def test_split_cli_writes_expected_manifest(tmp_path):
    output = tmp_path / "strict"
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_lexical_holdout.py"),
            str(FIXTURE),
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    manifest = json.loads(
        (output / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["record_counts"] == {
        "dev": 2,
        "mixed": 2,
        "test": 2,
        "train": 2,
    }
    assert set(
        manifest["lexical_overlap_counts"].values()
    ) == {0}
