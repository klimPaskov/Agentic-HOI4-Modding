"""Regressions for the offline wiki snapshot checks and its kit blocks."""
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


KIT = MODULE.kit_blocks
PAGE = """# Example

*Offline snapshot of the Hearts of Iron IV Wiki page "Example", revision 7, captured 2026-01-01.*

## Table of contents

- [First](#First)
- [Second](#Second)

---

Intro.

## First <a id="First"></a>

First text.

## Second <a id="Second"></a>

Second text.
"""
BLOCKS = """<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="7" -->
**Kit review:** checked.
<!-- kit:end id="review" -->

<!-- kit:begin id="first-note" at="section:First" -->
**Kit note** about First.

### Kit heading <a id="kit-heading"></a>

More.
<!-- kit:end id="first-note" -->

<!-- kit:begin id="second-top" at="heading:Second" -->
**Kit note** under the Second heading.
<!-- kit:end id="second-top" -->

<!-- kit:begin id="gone" at="section:Removed_upstream" -->
**Kit note** whose section the wiki removed.
<!-- kit:end id="gone" -->"""


class KitBlockTests(unittest.TestCase):
    def merged(self):
        page, orphans = KIT.place_blocks(PAGE, KIT.find_blocks(BLOCKS))
        return KIT.refresh_toc(page), orphans

    def test_blocks_survive_a_refresh_unchanged(self):
        page, orphans = self.merged()
        self.assertEqual([block.id for block in orphans], ["gone"])
        self.assertLess(page.index("first-note"), page.index("## Second"))
        self.assertLess(page.index("## Second"), page.index("second-top"))
        self.assertIn("  - [Kit heading](#kit-heading)", page)
        again, _ = KIT.place_blocks(KIT.strip_blocks(page), KIT.find_blocks(page))
        self.assertEqual(KIT.refresh_toc(again), page)
        self.assertEqual(KIT.refresh_toc(KIT.strip_blocks(page)), PAGE)

    def test_orphaned_and_misplaced_blocks_are_reported(self):
        page, _ = self.merged()
        problems = KIT.position_problems(page)
        self.assertEqual(len(problems), 1)
        self.assertIn("Removed_upstream", problems[0])
        note = KIT.find_blocks(BLOCKS)[1].text
        moved = page.replace(note + "\n\n## Second", "## Second", 1)
        moved = moved.replace("Second text.", "Second text.\n\n" + note)
        self.assertTrue(any("another heading" in p for p in KIT.position_problems(moved)))

    def test_unpaired_markers_are_rejected(self):
        with self.assertRaises(KIT.KitBlockError):
            KIT.find_blocks(BLOCKS.replace('<!-- kit:end id="gone" -->', ""))

    def test_verify_requires_review_and_label(self):
        page, _ = self.merged()
        page = page.replace("**Kit note** about First.", "About First.")
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "example.md").write_text(page, encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(MODULE.verify(directory), 1)
            self.assertIn("kit_label", output.getvalue())
            self.assertIn("kit_block", output.getvalue())
