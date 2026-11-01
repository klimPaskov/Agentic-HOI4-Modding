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


def _protobuf_field(number, value):
    def varint(n):
        out = bytearray()
        while True:
            byte, n = n & 0x7F, n >> 7
            out.append(byte | (0x80 if n else 0))
            if not n:
                return bytes(out)
    if isinstance(value, int):
        return varint(number << 3) + varint(value)
    return varint(number << 3 | 2) + varint(len(value)) + value


def _depot_manifest(files):
    """A minimal Steam depot manifest: (name, sha1 hex or None for a directory) per entry."""
    import struct
    payload = b""
    for name, digest in files:
        entry = _protobuf_field(1, name.encode("utf-8")) + _protobuf_field(2, 10)
        entry += _protobuf_field(3, 64 if digest is None else 0)
        if digest is not None:
            entry += _protobuf_field(5, bytes.fromhex(digest))
        payload += _protobuf_field(1, entry)
    metadata = _protobuf_field(1, 394361)
    return (struct.pack("<II", 0x71F617D0, len(payload)) + payload
            + struct.pack("<II", 0x1F4812BE, len(metadata)) + metadata)


class SteamDepotTests(unittest.TestCase):
    """The game-file diff that flags pages whose script or define sources changed in a game update."""

    def setUp(self):
        self.depots = _load("steam_depots")
        self.status = _load("wiki_status")
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.game = root / "steamapps" / "common" / "Hearts of Iron IV"
        self.game.mkdir(parents=True)
        (root / "depotcache").mkdir()
        self.cache = root / "depotcache"
        (root / "steamapps" / "appmanifest_394360.acf").write_text(
            '"AppState"\n{\n\t"InstalledDepots"\n\t{\n\t\t"394361"\n\t\t{\n\t\t\t"manifest"\t\t"200"\n'
            '\t\t\t"size"\t\t"5"\n\t\t}\n\t\t"394362"\n\t\t{\n\t\t\t"manifest"\t\t"7"\n\t\t}\n\t}\n'
            '\t"UserConfig"\n\t{\n\t\t"language"\t\t"english"\n\t}\n}\n', encoding="utf-8")
        old = [("common", None), ("common\\raids\\a.txt", "aa" * 20), ("common/raids/b.txt", "bb" * 20),
               ("documentation/effects_documentation.md", "cc" * 20), ("tbb.dll", "dd" * 20)]
        new = [("common", None), ("common\\raids\\a.txt", "aa" * 20), ("common/raids/b.txt", "b0" * 20),
               ("documentation/effects_documentation.md", "c0" * 20), ("common/ideas/new.txt", "ee" * 20)]
        (self.cache / "394361_100.manifest").write_bytes(_depot_manifest(old))
        (self.cache / "394361_200.manifest").write_bytes(_depot_manifest(new))

    def tearDown(self):
        self.temp.cleanup()

    def test_installed_depots_come_from_the_app_manifest(self):
        self.assertEqual(self.depots.installed_depots(self.game), {"394361": "200", "394362": "7"})
        self.assertEqual(self.depots.installed_depots(self.game / "missing"), {})

    def test_manifest_files_skip_directories_and_use_forward_slashes(self):
        files = self.depots.read_manifest(self.cache / "394361_100.manifest")
        self.assertEqual(sorted(files), ["common/raids/a.txt", "common/raids/b.txt",
                                         "documentation/effects_documentation.md", "tbb.dll"])
        self.assertEqual(files["common/raids/a.txt"], "aa" * 20)

    def test_changed_files_and_unavailable_depots(self):
        caches = self.depots.depot_caches(self.game)
        changes, notes = self.depots.changed_files({"394361": "100", "394362": "6"},
                                                   {"394361": "200", "394362": "7"}, caches)
        self.assertEqual(changes, {"common/raids/b.txt": "changed", "documentation/effects_documentation.md": "changed",
                                   "common/ideas/new.txt": "added", "tbb.dll": "removed"})
        self.assertEqual(notes, ["depot 394362: manifest 6, 7 is not in the Steam depot cache"])
        self.assertEqual(self.depots.changed_files({"394361": "200"}, {"394361": "200"}, caches), ({}, []))

    def test_pages_are_flagged_by_changed_script_sources_not_documentation(self):
        def page(sources):
            return (f'# T\n\n<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" '
                    f'sources="{sources}" -->\n**Kit review**\n<!-- kit:end id="review" -->\n')
        pages = {"Raid modding": page("common/raids/ documentation/effects_documentation.md"),
                 "Effects": page("documentation/effects_documentation.md"),
                 "Idea modding": page("common/ideas/new.txt")}
        changes = {"common/raids/b.txt": "changed", "documentation/effects_documentation.md": "changed",
                   "common/ideas/new.txt": "added"}
        self.assertEqual(self.status.file_reasons(changes, pages), {
            "Raid modding": ["source common/raids/: 1 game file(s) changed"],
            "Idea modding": ["source common/ideas/new.txt: 1 game file(s) changed"]})


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
