"""The agent's Tripo browser rules in docs/3d-units.md that keep Chrome usable: memory before a page, a frozen page closed at once, the
agent's own tabs closed, and the model's asset id recorded (2026-11-27, a frozen Tripo tab hung every later Tripo page)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

DOC = Path(__file__).resolve().parents[3] / "docs" / "3d-units.md"


class TripoBrowserRules(unittest.TestCase):
    def setUp(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        start = text.index("The agent works in your Chrome through Claude in Chrome")
        self.section = text[start:text.index("## Old Meshy jobs", start)]

    def test_the_agent_starts_only_with_memory_free(self) -> None:
        self.assertRegex(self.section, r"at least 3 GB of RAM free")

    def test_a_page_that_does_not_answer_is_closed_before_another_opens(self) -> None:
        self.assertIn("within about 30 seconds", self.section)
        self.assertIn("closes that tab before it opens another", self.section)
        self.assertIn("opens no further Tripo page", self.section)

    def test_the_agent_closes_its_own_tabs_and_records_the_asset_id(self) -> None:
        self.assertIn("closes every Tripo tab it opened", self.section)
        self.assertTrue(re.search(r'`"tripo_asset"`', self.section))


if __name__ == "__main__":
    unittest.main()
