"""The reference rules in the skill's texts agree with the code and with each other.

A real subject (a tank, a ship, a plane, a uniform) follows real references: public-domain or openly licensed photographs, plans, museum
pieces and period art, which may go to the image generator. A fantasy subject follows designed art, the owner's drawings or the mod's art
first, and the owner's drawings never leave the mod's private folder. The two texts once forbade every photograph and museum work, which
contradicted the picture review's own message (`init_pilot_jobs.SOURCES_MESSAGE`) and left no way to model a real tank or ship.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
REPO = PIPELINE.parents[1]
sys.path.insert(0, str(PIPELINE))

import init_pilot_jobs

REFERENCES = REPO / ".claude" / "skills" / "hoi4-3d-model-pipeline" / "references"
POLICY = REFERENCES / "source-reference-policy.md"
GUIDE = REFERENCES / "production-guide.md"
GATE = "## Designed source reference and provenance gate"


def gate_text() -> str:
    text = GUIDE.read_text(encoding="utf-8")
    start = text.index(GATE)
    end = text.index("\n## ", start + len(GATE))
    return text[start:end]


class ReferencePolicy(unittest.TestCase):
    def test_both_texts_let_a_real_subject_follow_real_references(self):
        for name, text in (("policy", POLICY.read_text(encoding="utf-8")), ("guide", gate_text())):
            with self.subTest(text=name):
                self.assertIn("never from a text prompt alone (D-110)", text)
                self.assertIn("public-domain or openly licensed", text)
                for kind in ("photographs", "plans", "museum pieces", "period art"):
                    self.assertIn(kind, text)
                self.assertIn("image generator", text)
                self.assertIn("licence and SHA-256", text)

    def test_both_texts_keep_designed_art_and_the_private_drawings_for_a_fantasy_subject(self):
        for name, text in (("policy", POLICY.read_text(encoding="utf-8")), ("guide", gate_text())):
            with self.subTest(text=name):
                self.assertIn("follows designed art", text)
                self.assertIn("the owner's drawings or the mod's existing art", text)
                self.assertIn("never leave the mod's private folder", text)
                self.assertIn("D-123", text)

    def test_no_text_forbids_every_photograph_or_museum_work(self):
        for name, text in (("policy", POLICY.read_text(encoding="utf-8")), ("guide", gate_text())):
            with self.subTest(text=name):
                self.assertNotIn("cannot satisfy the source gate", text)
                self.assertNotIn("Do not use archival photographs", text)
                self.assertNotIn("excluded historical material", text)

    def test_the_picture_reviews_message_names_the_same_real_references(self):
        message = init_pilot_jobs.SOURCES_MESSAGE
        self.assertIn("for a real-world subject, the real references research found and gave to the image tool", message)
        self.assertIn("never from a text prompt alone", message)


if __name__ == "__main__":
    unittest.main()
