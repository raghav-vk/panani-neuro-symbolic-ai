"""Legacy toy sandhi generator.

This module is retained for compatibility with the original demonstration.
Its hard-coded examples and fallback concatenation are not part of the
research system. Use panini.rules for typed experiment rules.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SandhiGenerator:
    """Generate toy combinations for legacy examples and tests only."""

    def __init__(self):
        self.sandhi_rules = {
            ("a", "a"): "ā",
            ("a", "i"): "e",
            ("a", "u"): "o",
            ("a", "e"): "ai",
            ("a", "o"): "au",
            ("i", "a"): "ya",
            ("u", "a"): "va",
            ("e", "a"): "aya",
            ("o", "a"): "ava",
            ("ḥ", "a"): "a",
            ("ḥ", "i"): "i",
            ("ḥ", "u"): "u",
            ("m", "a"): "ma",
            ("m", "i"): "mi",
            ("m", "u"): "mu",
        }
        self.known_combinations = {
            ("Deva", "Alaya"): "Devalaya",
            ("Rama", "Ayana"): "Ramanayana",
            ("Krishna", "Arjuna"): "Krishnarjuna",
            ("Ganga", "Uttara"): "Gangottara",
        }

    def apply_sandhi(self, word1: str, word2: str) -> str:
        """Combine a pair using the legacy demonstration table."""
        if not isinstance(word1, str) or not isinstance(word2, str):
            raise TypeError("Both words must be strings")
        if not word1 or not word2:
            raise ValueError("Both words must be non-empty")

        known = self.known_combinations.get((word1, word2))
        if known is not None:
            return known

        replacement = self.sandhi_rules.get(
            (word1[-1].lower(), word2[0].lower())
        )
        if replacement is None:
            return word1 + word2
        return word1[:-1] + replacement + word2[1:]

    def generate_training_pairs(
        self,
        word_pairs: List[Tuple[str, str]],
        output_format: str = "jsonl",
    ) -> List[Dict]:
        """Format toy pairs using the legacy API."""
        examples = []
        for word1, word2 in word_pairs:
            combined = self.apply_sandhi(word1, word2)
            if output_format in {"jsonl", "alpaca"}:
                example = {
                    "instruction": (
                        "Apply Sandhi rules to combine these Sanskrit words."
                    ),
                    "input": f"{word1} + {word2}",
                    "output": combined,
                }
            elif output_format == "chatml":
                example = {
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                "Combine these Sanskrit words using Sandhi: "
                                f"{word1} + {word2}"
                            ),
                        },
                        {
                            "role": "assistant",
                            "content": combined,
                        },
                    ]
                }
            else:
                example = {
                    "word1": word1,
                    "word2": word2,
                    "combined": combined,
                    "rules_applied": "sandhi",
                }
            examples.append(example)
        return examples

    def generate_dataset(
        self,
        num_samples: int,
        output_file: Optional[str] = None,
    ) -> List[Dict]:
        """Generate a deterministic toy dataset."""
        word_pairs = self._generate_word_pairs(num_samples)
        examples = self.generate_training_pairs(word_pairs)
        if output_file:
            output_path = Path(output_file)
            with output_path.open("w", encoding="utf-8") as handle:
                for example in examples:
                    handle.write(
                        json.dumps(
                            example,
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
        return examples

    def _generate_word_pairs(
        self,
        num_samples: int,
    ) -> List[Tuple[str, str]]:
        """Return deterministic pairs for compatibility tests."""
        if num_samples < 0:
            raise ValueError("num_samples must be non-negative")
        first_words = [
            "Deva",
            "Rama",
            "Krishna",
            "Ganga",
            "Sita",
            "Lakshmana",
        ]
        second_words = [
            "Alaya",
            "Ayana",
            "Arjuna",
            "Uttara",
            "Mandira",
            "Kutira",
        ]
        known_pairs = list(self.known_combinations)
        pairs: List[Tuple[str, str]] = []
        for index in range(num_samples):
            if index < len(known_pairs):
                pairs.append(known_pairs[index])
                continue
            first = first_words[index % len(first_words)]
            second = second_words[
                (index // len(first_words)) % len(second_words)
            ]
            pairs.append((first, second))
        return pairs

    def validate_sandhi(
        self,
        word1: str,
        word2: str,
        expected: str,
    ) -> bool:
        """Check a legacy output against an expected string."""
        return self.apply_sandhi(word1, word2) == expected


def main():
    generator = SandhiGenerator()
    for word1, word2 in (
        ("Deva", "Alaya"),
        ("Rama", "Ayana"),
        ("Krishna", "Arjuna"),
    ):
        print(
            f"{word1} + {word2} = "
            f"{generator.apply_sandhi(word1, word2)}"
        )


if __name__ == "__main__":
    main()
