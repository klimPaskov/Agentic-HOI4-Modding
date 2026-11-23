"""tripo_intake.check_receipt: the stage's receipt, and `--reingest` (gaps 22 and 23 of the hobgoblin route test)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tripo_intake

SOURCES = [{"kind": "rigged", "name": "u__rigged.glb", "bytes": 10, "sha256": "aa"}]
OTHER = [{"kind": "rigged", "name": "u__rigged.glb", "bytes": 11, "sha256": "bb"}]


class Receipt(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "tripo_intake_generation_2.json"

    def write(self, sources) -> None:
        self.path.write_text(json.dumps({"sources": sources, "task_id": "t1"}), encoding="utf-8")

    def test_no_receipt_goes_on(self) -> None:
        self.assertIsNone(tripo_intake.check_receipt(self.path, SOURCES, "u", "generation_2", False))

    def test_the_same_files_do_nothing(self) -> None:
        self.write(SOURCES)
        self.assertEqual(tripo_intake.check_receipt(self.path, SOURCES, "u", "generation_2", False)["state"], "already_ingested")

    def test_other_files_are_refused_and_the_message_names_reingest(self) -> None:
        self.write(SOURCES)
        with self.assertRaisesRegex(RuntimeError, "--reingest"):
            tripo_intake.check_receipt(self.path, OTHER, "u", "generation_2", False)

    def test_reingest_keeps_the_old_receipt_and_goes_on_for_other_files_and_for_the_same_files(self) -> None:
        for sources in (OTHER, SOURCES):
            self.write(SOURCES)
            self.assertIsNone(tripo_intake.check_receipt(self.path, sources, "u", "generation_2", True))
            self.assertFalse(self.path.is_file())
            kept = list(self.path.parent.glob("tripo_intake_generation_2.replaced-*.json"))
            self.assertEqual(len(kept), 1)
            kept[0].unlink()


if __name__ == "__main__":
    unittest.main()
