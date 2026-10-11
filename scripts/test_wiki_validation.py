"""Regressions for literal Markdown punctuation and unused snapshot media."""
import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / ".tools/wiki/verify_wiki_snapshot.py"
SPEC = importlib.util.spec_from_file_location("wiki_validation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WikiValidationTests(unittest.TestCase):
    def test_literal_markdown_escapes_are_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "example.md").write_text(
                "# Example\n\nLiteral multiplier: 2 \\* 3. Range: (0,1\\].\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(MODULE.verify(directory), 0)

    def test_unused_media_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "example.md").write_text("# Example\n", encoding="utf-8")
            media = Path(directory, "media")
            media.mkdir()
            (media / "unused.png").write_bytes(b"fixture")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(MODULE.verify(directory), 1)
            self.assertIn("orphan_media", output.getvalue())
