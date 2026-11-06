"""Regressions for the offline wiki: lean pages, kit sidecars, the manifest and their checks."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / ".tools/wiki/verify_wiki_snapshot.py"
SPEC = importlib.util.spec_from_file_location("wiki_validation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
KIT = MODULE.kit_blocks
LEAN = MODULE.lean
RENDER = MODULE.render_wiki


def verified(directory, manifest=None):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        status = MODULE.verify(str(directory), manifest=manifest)
    return status, output.getvalue()


class WikiValidationTests(unittest.TestCase):
    def test_literal_markdown_escapes_are_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "example.md").write_text(
                "# Example\n\nLiteral multiplier: 2 \\* 3. Range: (0,1\\].\n", encoding="utf-8")
            self.assertEqual(verified(directory)[0], 0)

    def test_unused_media_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "example.md").write_text("# Example\n", encoding="utf-8")
            media = Path(directory, "media")
            media.mkdir()
            (media / "unused.png").write_bytes(b"fixture")
            status, output = verified(directory)
            self.assertEqual(status, 1)
            self.assertIn("orphan_media", output)

    def test_pages_hold_no_maintenance_text(self):
        cases = {
            "html_comment": '<!-- kit:begin id="x" at="top" -->',
            "anchor": '## Second <a id="Second"></a>',
            "evidence_tag": "Vanilla uses it. [vanilla-confirmed 1.19.4.1] `common/ideas/`.",
            "kit_label": "**Kit note** Vanilla uses it.",
            "capture_line": '*Offline snapshot of the Hearts of Iron IV Wiki page "Example", revision 7.*',
            "furniture": "## Navigation",
        }
        for kind, line in cases.items():
            with tempfile.TemporaryDirectory() as directory:
                Path(directory, "example.md").write_text(f"# Example\n\n{line}\n", encoding="utf-8")
                status, output = verified(directory)
                self.assertEqual(status, 1, kind)
                self.assertIn(f"[{kind}]", output, kind)

    def test_code_may_show_tags_and_comments(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "example.md").write_text(
                "# Example\n\nWrite `[docs]` or `<!-- x -->` as text.\n\n```text\n<!-- kept -->\n```\n",
                encoding="utf-8")
            self.assertEqual(verified(directory)[0], 0)

    def test_section_links_use_heading_slugs(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "triggers.md").write_text("# Triggers\n\n## Country scope\n\nText.\n", encoding="utf-8")
            Path(directory, "effects.md").write_text(
                "# Effects\n\nSee [it](triggers.md#country-scope) and [old](triggers.md#Country_scope).\n",
                encoding="utf-8")
            status, output = verified(directory)
            self.assertEqual(status, 1)
            self.assertEqual(output.count("[broken_anchor]"), 1)
            self.assertIn("triggers.md#Country_scope", output)


class LeanTextTests(unittest.TestCase):
    def lean(self, text):
        return LEAN.lean_text(text)

    def test_a_citation_runs_to_the_end_of_its_sentence(self):
        self.assertEqual(self.lean("Use the ids above. [vanilla-confirmed 1.19.4.1] `common/x.txt`. Next one."),
                         "Use the ids above. Next one.")
        self.assertEqual(self.lean("It runs in country scope [docs] `documentation/effects_documentation.md`."),
                         "It runs in country scope.")
        self.assertEqual(self.lean("A test showed it. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, "
                                   "game.log read. The second claim stays."),
                         "A test showed it. The second claim stays.")

    def test_citation_lines_and_labels_disappear(self):
        self.assertEqual(self.lean("Intro.\n\nAll rows: [docs] `a.md`; counts [vanilla-confirmed 1.19.4.1] `b/`.\n\nEnd."),
                         "Intro.\n\nEnd.")
        self.assertEqual(self.lean("Keys vanilla uses. Counts are [vanilla-confirmed 1.19.4.1] `common/units/*.txt`."),
                         "Keys vanilla uses.")

    def test_a_label_that_introduces_a_list_stays(self):
        self.assertEqual(self.lean("Example: [vanilla-confirmed 1.19.3] `common/x.txt`.\n\n- item"),
                         "Example:\n\n- item")

    def test_statements_after_a_tag_stay(self):
        self.assertEqual(self.lean("Do not use it. [vanilla-confirmed 1.19.4.1] All four load without a message."),
                         "Do not use it. All four load without a message.")
        self.assertEqual(self.lean("X [docs] `f.md`, so the table is wrong."), "X, so the table is wrong.")

    def test_hedges_stay_as_words(self):
        self.assertEqual(self.lean("Whether it applies is [unverified]."), "Whether it applies is unverified.")
        self.assertEqual(self.lean("The default is 5 [unverified]."), "The default is 5 (unverified).")
        self.assertEqual(self.lean("Vanilla sets it [vanilla-confirmed 1.19.4.1] `x/`, effect [unverified]."),
                         "Vanilla sets it, effect (unverified).")

    def test_table_cells_and_code_are_kept_apart(self):
        self.assertEqual(self.lean("| `a` | used in 3 files [vanilla-confirmed 1.19.4.1] `common/` |"),
                         "| `a` | used in 3 files |")
        self.assertEqual(self.lean("Write `[docs]` literally."), "Write `[docs]` literally.")
        self.assertEqual(self.lean("```\n[docs] stays in code\n```"), "```\n[docs] stays in code\n```")

    def test_anchors_angle_links_and_kit_headings(self):
        self.assertEqual(self.lean('### Kit: raid categories <a id="kit-raid-categories"></a>'), "### Raid categories")
        self.assertEqual(self.lean("See [AI](<ai_modding.md#plans>)."), "See [AI](ai_modding.md#plans).")

    def test_evidence_written_before_its_statement_is_reported(self):
        self.assertEqual(LEAN.evidence_problems("Use counts: [vanilla-confirmed 1.19.4.1] `x/` and more"), [])
        problems = LEAN.evidence_problems("The rows: file lists are [vanilla-confirmed 1.19.4.1] under `common/`; "
                                          "every name is [docs] `x`, also checked.")
        self.assertTrue(problems)


BASE = "# Example\n\nIntro.\n\n## First\n\nFirst text.\n\n## Second\n\nSecond text.\n"
SIDECAR = """# Example

<!-- kit:begin id="review" build="1.19.3.0" checked="2026-10-31" revision="7" sources="common/x/" -->
Checked against common/x/.
<!-- kit:end id="review" -->

<!-- kit:begin id="first-note" at="section:first" -->
About First. [docs] `documentation/effects_documentation.md`

### Raid categories

More.
<!-- kit:end id="first-note" -->

<!-- kit:begin id="second-top" at="heading:second" -->
Under the Second heading.
<!-- kit:end id="second-top" -->

<!-- kit:begin id="intro" at="top" -->
Before the intro.
<!-- kit:end id="intro" -->

<!-- kit:begin id="gone" at="section:removed-upstream" -->
Whose section the wiki removed.
<!-- kit:end id="gone" -->
"""


class KitBlockTests(unittest.TestCase):
    def test_slugs_follow_github(self):
        self.assertEqual(KIT.slug("Focus Types"), "focus-types")
        self.assertEqual(KIT.slug("`set_rule` (old) <a id=\"x\"></a>"), "set_rule-old")
        lines = ["# A", "## Notes", "## Notes", "```", "## not a heading", "```"]
        self.assertEqual([s for _i, _l, s in KIT.heading_slugs(lines)], ["a", "notes", "notes-1"])

    def test_blocks_go_where_at_says_and_come_back_out_exactly(self):
        placed = RENDER.render_wiki_page(BASE, SIDECAR)
        page = placed.text
        self.assertEqual(placed.orphans, ["gone"])
        self.assertLess(page.index("Before the intro."), page.index("Intro."))
        self.assertLess(page.index("First text."), page.index("About First."))
        self.assertLess(page.index("About First."), page.index("## Second"))
        self.assertLess(page.index("## Second"), page.index("Under the Second heading."))
        self.assertLess(page.index("Under the Second heading."), page.index("Second text."))
        self.assertTrue(page.rstrip().endswith("Whose section the wiki removed."))
        self.assertNotIn("[docs]", page)
        lines = page.split("\n")
        first, last = placed.spans["first-note"]
        self.assertEqual(lines[first - 1], "About First.")
        self.assertEqual(lines[last - 1], "More.")
        self.assertEqual(KIT.disassemble(page, placed.spans), BASE)

    def test_markers_must_pair_and_name_a_place(self):
        with self.assertRaises(KIT.KitBlockError):
            KIT.find_blocks(SIDECAR.replace('<!-- kit:end id="gone" -->', ""))
        with self.assertRaises(KIT.KitBlockError):
            KIT.find_blocks(SIDECAR.replace(' at="heading:second"', ""))

    def test_review_markers_are_updated_in_place(self):
        updated = KIT.set_review(SIDECAR, {"build": "1.19.4.1", "via": "docs-diff"})
        self.assertEqual(KIT.review(updated)["build"], "1.19.4.1")
        self.assertEqual(KIT.review(updated)["via"], "docs-diff")
        self.assertEqual(updated.count("kit:begin"), SIDECAR.count("kit:begin"))


class RenderTests(unittest.TestCase):
    """A page rebuilt from its sidecar, and a hand edit in hoi4_wiki/ caught."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.wiki, self.sidecars, self.manifest = root / "wiki", root / "kit", root / "manifest.json"
        self.wiki.mkdir()
        self.sidecars.mkdir()
        (self.wiki / "LICENSE.txt").write_text("license\n", encoding="utf-8")
        sidecar = SIDECAR.replace(SIDECAR[SIDECAR.index("\n<!-- kit:begin id=\"gone\""):], "\n")
        (self.sidecars / "example.md").write_text(sidecar, encoding="utf-8")
        (self.sidecars / "raid_modding.md").write_text(
            "# Raid modding\n\n<!-- kit:page -->\n\n" + KIT.DEFAULT_REVIEW
            + "\n\n## Raids\n\nA raid is a block. [docs] `common/raids/_documentation.md`\n", encoding="utf-8")
        placed = RENDER.render_wiki_page(BASE, sidecar)
        (self.wiki / "example.md").write_text(placed.text, encoding="utf-8")
        self.manifest.write_text(json.dumps({"pages": {"example.md": {
            "title": "Example", "source": "wiki", "wiki_page": "Example", "revision": 7,
            "captured": "2026-01-01", "base_sha256": KIT.sha256(BASE), "anchors": {}, "blocks": placed.spans}}}),
            encoding="utf-8")
        self.saved, KIT.SIDECAR_DIR = KIT.SIDECAR_DIR, self.sidecars

    def tearDown(self):
        KIT.SIDECAR_DIR = self.saved
        self.temp.cleanup()

    def rebuild(self, write=True):
        return RENDER.rebuild(write=write, wiki_dir=self.wiki, manifest_path=self.manifest)

    def test_a_fresh_rebuild_writes_kit_pages_and_sources(self):
        report = self.rebuild()
        self.assertEqual(report["failed"], [])
        self.assertEqual((self.wiki / "raid_modding.md").read_text(encoding="utf-8"),
                         "# Raid modding\n\n## Raids\n\nA raid is a block.\n")
        sources = json.loads((self.wiki / "SOURCES.json").read_text(encoding="utf-8"))
        self.assertEqual(sources["license"], "CC BY-SA 3.0")
        self.assertEqual(sources["pages"][0]["url"], "https://hoi4.paradoxwikis.com/Example")
        self.assertEqual(self.rebuild(write=False)["changed"], [])
        self.assertEqual(verified(self.wiki, self.manifest)[0], 0)

    def test_an_edited_sidecar_reaches_the_page(self):
        self.rebuild()
        path = self.sidecars / "example.md"
        path.write_text(path.read_text(encoding="utf-8").replace("About First.", "About First, edited."),
                        encoding="utf-8")
        status, output = verified(self.wiki, self.manifest)
        self.assertEqual(status, 1)
        self.assertIn("[out_of_date] example.md", output)
        self.assertEqual(self.rebuild()["changed"], ["example.md"])
        self.assertIn("About First, edited.", (self.wiki / "example.md").read_text(encoding="utf-8"))
        self.assertEqual(verified(self.wiki, self.manifest)[0], 0)

    def test_a_hand_edit_in_the_page_is_caught(self):
        self.rebuild()
        page = self.wiki / "example.md"
        page.write_text(page.read_text(encoding="utf-8").replace("Second text.", "Second text, edited."),
                        encoding="utf-8")
        report = self.rebuild(write=False)
        self.assertEqual(len(report["failed"]), 1)
        self.assertIn("differs from the recorded text", report["failed"][0])
        self.assertIn("[render] example.md", verified(self.wiki, self.manifest)[1])


class FileNameTests(unittest.TestCase):
    def built(self, build):
        with tempfile.TemporaryDirectory() as directory:
            build(Path(directory))
            return verified(directory)

    @staticmethod
    def page(directory, name, title, extra=""):
        Path(directory, name).write_text(f"# {title}\n\nText.\n{extra}", encoding="utf-8")

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
        self.assertEqual(self.built(lambda d: self.page(d, "scripted_gui_modding.md", "Scripted GUI modding"))[0], 0)

    def test_a_title_with_punctuation_is_reported(self):
        status, output = self.built(lambda d: self.page(d, "mod_old.md", "Mod (old)"))
        self.assertEqual(status, 1)
        self.assertIn("agent_title", output)

    def test_kebab_case_and_old_spaced_names_are_rejected(self):
        for name in ("scripted-gui-modding.md", "Scripted GUI modding - Hearts of Iron 4 Wiki.md"):
            status, output = self.built(lambda d, n=name: self.page(d, n, "Scripted GUI modding"))
            self.assertEqual(status, 1, name)
            self.assertIn("file_name", output, name)

    def test_a_file_name_that_is_not_the_title_slug_is_rejected(self):
        status, output = self.built(lambda d: self.page(d, "other.md", "Scripted GUI modding"))
        self.assertEqual(status, 1)
        self.assertIn("belongs in scripted_gui_modding.md", output)

    def test_links_must_match_the_file_name_exactly(self):
        def build(d):
            self.page(d, "triggers.md", "Triggers")
            self.page(d, "effects.md", "Effects", "\nSee [Triggers](Triggers.md).\n")
        status, output = self.built(build)
        self.assertEqual(status, 1)
        self.assertIn("broken_link", output)

    def test_media_names_must_be_lowercase_without_spaces(self):
        def build(d):
            self.page(d, "triggers.md", "Triggers", "\n![x](media/Some Image.png)\n")
            (d / "media").mkdir()
            (d / "media" / "Some Image.png").write_bytes(b"fixture")
        status, output = self.built(build)
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

# A page as the converter hands it over: wiki heading ids as anchors, links with them.
CONVERTED = """# Example

Intro with [a link](<example.md#Second>) and [defines](<defines.md>).

## First <a id="First"></a>

First text.

## Second <a id="Second"></a>

1. ↑ `NDefines.NGame.END_DATE = "1949.1.1.1"` in [Defines](<defines.md>).
"""


@unittest.skipIf(SYNC is None, "the sync needs requests, beautifulsoup4 and markdownify")
class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.sidecars = self.root / "kit"
        self.sidecars.mkdir()
        self.saved = (KIT.SIDECAR_DIR, KIT.MANIFEST)
        KIT.SIDECAR_DIR, KIT.MANIFEST = self.sidecars, self.root / "manifest.json"

    def tearDown(self):
        KIT.SIDECAR_DIR, KIT.MANIFEST = self.saved
        self.temp.cleanup()

    def test_local_names(self):
        self.assertEqual(SYNC.WikiConverter.local_name("Scripted GUI modding"), "scripted_gui_modding.md")
        self.assertEqual(SYNC.WikiConverter.local_name("Effect"), "effects.md")
        self.assertEqual(SYNC._slug("Building modding"), "building_modding")

    def test_a_reimport_writes_a_lean_page_with_its_kit_blocks(self):
        (self.sidecars / "example.md").write_text(SIDECAR.split('\n<!-- kit:begin id="second-top"')[0] + "\n",
                                                  encoding="utf-8")
        out = self.root / "out"
        out.mkdir()
        context = {"out_dir": str(out), "dry_run": True, "manifest": {"pages": {}},
                   "converted": {"example.md": ("Example", "Example", CONVERTED, 42)},
                   "anchors": {"example.md": LEAN.anchor_map(CONVERTED.split("\n"))}}
        report = {"failures": [], "changed": [], "orphans": []}
        SYNC.write_pages(context, report)
        self.assertEqual(report, {"failures": [], "changed": [], "orphans": []})
        page = (out / "example.md").read_text(encoding="utf-8")
        self.assertIn("[a link](example.md#second)", page)
        self.assertIn("[defines](defines.md)", page)
        self.assertIn('1. `NDefines.NGame.END_DATE = "1949.1.1.1"`', page)
        self.assertIn("First text.\n\nAbout First.\n\n### Raid categories", page)
        for unwanted in ("<a id", "<!--", "[docs]", "↑", "Offline snapshot", "## Navigation"):
            self.assertNotIn(unwanted, page)
        entry = context["manifest"]["pages"]["example.md"]
        self.assertEqual((entry["revision"], entry["wiki_page"], entry["anchors"]["Second"]), (42, "Example", "second"))
        self.assertEqual(KIT.sha256(KIT.disassemble(page, entry["blocks"])), entry["base_sha256"])

    def test_pages_come_from_the_manifest_and_the_sidecars(self):
        KIT.MANIFEST.write_text(json.dumps({"pages": {
            "scripted_gui_modding.md": {"title": "Scripted GUI modding", "source": "wiki"}}}), encoding="utf-8")
        (self.sidecars / "raid_modding.md").write_text("# Raid modding\n\n<!-- kit:page -->\n", encoding="utf-8")
        self.assertEqual(SYNC.snapshot_pages(), (["Scripted GUI modding"], ["Raid modding"]))
        (self.sidecars / "wrong.md").write_text("# Another page\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            SYNC.snapshot_pages()

    def test_a_snapshot_with_old_names_is_not_refreshed(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("Triggers - Hearts of Iron 4 Wiki.md", "scripted-gui-modding.md", "effects.md"):
                Path(directory, name).write_text("# Page\n", encoding="utf-8")
            saved, SYNC.WIKI_DIR = SYNC.WIKI_DIR, directory
            argv, SYNC.sys.argv = SYNC.sys.argv, ["sync_wiki_snapshot.py"]
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
            return (f'# T\n\n<!-- kit:begin id="review" build="1.19.3.0" checked="2026-10-31" '
                    f'sources="{sources}" -->\nChecked.\n<!-- kit:end id="review" -->\n')
        pages = {"Raid modding": page("common/raids/ documentation/effects_documentation.md"),
                 "Effects": page("documentation/effects_documentation.md"),
                 "Idea modding": page("common/ideas/new.txt")}
        changes = {"common/raids/b.txt": "changed", "documentation/effects_documentation.md": "changed",
                   "common/ideas/new.txt": "added"}
        self.assertEqual(self.status.file_reasons(changes, pages), {
            "Raid modding": ["source common/raids/: 1 game file(s) changed"],
            "Idea modding": ["source common/ideas/new.txt: 1 game file(s) changed"]})


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.status = _load("wiki_status")
        self.temp = tempfile.TemporaryDirectory()
        self.saved, KIT.SIDECAR_DIR = KIT.SIDECAR_DIR, Path(self.temp.name)
        Path(self.temp.name, "scripted_gui_modding.md").write_text(
            "# Scripted GUI modding\n\n" + KIT.DEFAULT_REVIEW + "\n", encoding="utf-8")

    def tearDown(self):
        KIT.SIDECAR_DIR = self.saved
        self.temp.cleanup()

    def test_sidecars_are_found_by_title_stem_or_file_name(self):
        self.assertEqual(list(self.status.load_pages()), ["Scripted GUI modding"])
        for name in ("Scripted GUI modding", "scripted gui modding", "scripted-gui-modding",
                     "scripted_gui_modding.md"):
            self.assertEqual(self.status.page_path(name).name, "scripted_gui_modding.md", name)
        with self.assertRaises(SystemExit):
            self.status.page_path("Triggers")

    def test_a_page_is_current_for_the_build_and_the_revision_it_holds(self):
        sidecar = KIT.set_review(SIDECAR, {"build": "1.19.4.1", "revision": "7"})
        self.assertEqual(self.status.page_state(sidecar, "1.19.4.1", 7), "current")
        self.assertEqual(self.status.page_state(sidecar, "1.19.4.1", 8), "wiki text changed since the review")
        self.assertEqual(self.status.page_state(sidecar, "1.19.5.0", 7), "reviewed on an older build")
        self.assertEqual(self.status.page_state(KIT.DEFAULT_REVIEW, "1.19.4.1"), "not reviewed")


if __name__ == "__main__":
    unittest.main()
