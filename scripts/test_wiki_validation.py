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


REVIEW = (
    '<!-- kit:begin id="review" at="top" build="none" checked="never" -->\n'
    "**Kit review:** none.\n"
    '<!-- kit:end id="review" -->\n'
)


def _write_page(directory, name, title, extra="", kit_page=False):
    marker = "<!-- kit:page -->\n" if kit_page else ""
    Path(directory, name).write_text(
        f"# {title}\n\n*Offline snapshot of the Hearts of Iron IV Wiki page \"{title}\", "
        f"revision 7, captured 2026-01-01.*\n{marker}\n{REVIEW}{extra}", encoding="utf-8")


class FileNameTests(unittest.TestCase):
    def verified(self, build):
        with tempfile.TemporaryDirectory() as directory:
            build(Path(directory))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = MODULE.verify(directory)
            return status, output.getvalue()

    def test_file_names_follow_the_title(self):
        self.assertEqual(KIT.file_name("Scripted GUI modding"), "scripted_gui_modding.md")
        self.assertEqual(KIT.file_name("AI focuses"), "ai_focuses.md")
        self.assertEqual(KIT.file_name("Effects"), "effects.md")
        self.assertEqual(KIT.page_title("# Mods\n\n```\n# not a title\n```\n"), "Mods")

    def test_agent_tools_read_the_title_back_from_the_file_name(self):
        # HOI4 Agent Tools: strip .md, turn "_" into a space, compare ignoring case.
        for title in ("Scripted GUI modding", "AI focuses", "Effects", "Console commands"):
            self.assertEqual(KIT.agent_title(KIT.file_name(title)).lower(), title.lower())
        self.assertNotEqual(KIT.agent_title(KIT.file_name("Mod (old)")).lower(), "mod (old)")

    def test_snake_case_names_pass(self):
        status, _ = self.verified(lambda d: _write_page(d, "scripted_gui_modding.md", "Scripted GUI modding"))
        self.assertEqual(status, 0)

    def test_a_title_with_punctuation_is_reported(self):
        status, output = self.verified(lambda d: _write_page(d, "mod_old.md", "Mod (old)"))
        self.assertEqual(status, 1)
        self.assertIn("agent_title", output)

    def test_kebab_case_names_are_rejected(self):
        status, output = self.verified(lambda d: _write_page(
            d, "scripted-gui-modding.md", "Scripted GUI modding"))
        self.assertEqual(status, 1)
        self.assertIn("file_name", output)

    def test_old_spaced_names_are_rejected(self):
        status, output = self.verified(lambda d: _write_page(
            d, "Scripted GUI modding - Hearts of Iron 4 Wiki.md", "Scripted GUI modding"))
        self.assertEqual(status, 1)
        self.assertIn("file_name", output)

    def test_a_file_name_that_is_not_the_title_slug_is_rejected(self):
        status, output = self.verified(lambda d: _write_page(d, "other.md", "Scripted GUI modding"))
        self.assertEqual(status, 1)
        self.assertIn("belongs in scripted_gui_modding.md", output)

    def test_links_must_match_the_file_name_exactly(self):
        def build(d):
            _write_page(d, "triggers.md", "Triggers")
            _write_page(d, "effects.md", "Effects", "\nSee [Triggers](<Triggers.md>).\n")
        status, output = self.verified(build)
        self.assertEqual(status, 1)
        self.assertIn("broken_link", output)

    def test_media_names_must_be_lowercase_without_spaces(self):
        def build(d):
            _write_page(d, "triggers.md", "Triggers", "\n![x](media/Some Image.png)\n")
            (d / "media").mkdir()
            (d / "media" / "Some Image.png").write_bytes(b"fixture")
        status, output = self.verified(build)
        self.assertEqual(status, 1)
        self.assertIn("media file names are lowercase", output)


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPT.with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sync_module():
    try:
        return _load("sync_wiki_snapshot")
    except SystemExit:  # requests, beautifulsoup4 or markdownify is not installed
        return None


SYNC = _sync_module()


@unittest.skipIf(SYNC is None, "the sync needs requests, beautifulsoup4 and markdownify")
class SyncNameTests(unittest.TestCase):
    def test_links_and_media_use_the_new_names(self):
        self.assertEqual(SYNC.WikiConverter.local_name("Scripted GUI modding"), "scripted_gui_modding.md")
        self.assertEqual(SYNC.WikiConverter.local_name("Effect"), "effects.md")
        self.assertEqual(SYNC.WikiConverter.local_name("Effects"), "effects.md")
        self.assertEqual(SYNC.render_link("Triggers", "Flags", "flags", {"Triggers"}),
                         "[flags](<triggers.md#Flags>)")
        self.assertEqual(SYNC._slug("Building modding"), "building_modding")
        footer = SYNC.navbox_footer([{"title": "Modding", "groups": []}], {"Modding"})
        self.assertIn("[Modding](<modding.md>)", footer)

    def test_titles_come_from_the_heading_and_kit_pages_from_their_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            _write_page(directory, "scripted_gui_modding.md", "Scripted GUI modding")
            _write_page(directory, "raid_modding.md", "Raid modding", kit_page=True)
            saved, SYNC.WIKI_DIR = SYNC.WIKI_DIR, directory
            try:
                wiki, kit = SYNC.snapshot_pages()
                self.assertEqual((wiki, kit), (["Scripted GUI modding"], ["Raid modding"]))
                _write_page(directory, "wrong.md", "Another page")
                with self.assertRaises(SystemExit):
                    SYNC.snapshot_pages()
            finally:
                SYNC.WIKI_DIR = saved

    def test_a_snapshot_with_old_names_is_not_refreshed(self):
        with tempfile.TemporaryDirectory() as directory:
            _write_page(directory, "Triggers - Hearts of Iron 4 Wiki.md", "Triggers")
            _write_page(directory, "scripted-gui-modding.md", "Scripted GUI modding")
            _write_page(directory, "effects.md", "Effects")
            saved, SYNC.WIKI_DIR = SYNC.WIKI_DIR, directory
            argv, sys_argv = SYNC.sys.argv, ["sync_wiki_snapshot.py"]
            SYNC.sys.argv = sys_argv
            try:
                self.assertEqual(SYNC.legacy_files(),
                                 ["Triggers - Hearts of Iron 4 Wiki.md", "scripted-gui-modding.md"])
                with self.assertRaises(SystemExit) as raised:
                    SYNC.main()
                self.assertIn("snake_case", str(raised.exception))
            finally:
                SYNC.WIKI_DIR, SYNC.sys.argv = saved, argv


class StatusNameTests(unittest.TestCase):
    def test_pages_are_found_by_title_stem_or_file_name(self):
        status = _load("wiki_status")
        with tempfile.TemporaryDirectory() as directory:
            _write_page(directory, "scripted_gui_modding.md", "Scripted GUI modding")
            saved, status.WIKI_DIR = status.WIKI_DIR, Path(directory)
            try:
                self.assertEqual(list(status.load_pages()), ["Scripted GUI modding"])
                for name in ("Scripted GUI modding", "scripted gui modding", "scripted-gui-modding",
                             "scripted_gui_modding.md"):
                    self.assertEqual(status.page_path(name).name, "scripted_gui_modding.md", name)
                with self.assertRaises(SystemExit):
                    status.page_path("Triggers")
            finally:
                status.WIKI_DIR = saved
