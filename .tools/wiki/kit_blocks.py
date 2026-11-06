"""Page format shared by the wiki tools: lean pages, kit sidecars and the manifest.

Agents read ``hoi4_wiki/``. Each page there is a title and its content, nothing else:
no review notes, evidence tags, source lines, navigation or HTML comments. Everything
the tools need to maintain a page lives next to the tools instead:

``.tools/wiki/kit/<page>.md`` (the sidecar, written by hand)
    The kit's text for the page, with its evidence. For a wiki page it holds the
    review block and the kit blocks that go into the wiki text::

        <!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="105661" sources="..." -->
        What was checked, what the kit changed, and the gaps that remain.
        <!-- kit:end id="review" -->

        <!-- kit:begin id="set-autonomy-scope" at="section:autonomy" -->
        `set_autonomy` runs in country scope. [docs] `documentation/effects_documentation.md`.
        <!-- kit:end id="set-autonomy-scope" -->

    A kit page (one the wiki does not have) has ``<!-- kit:page -->`` under its
    title, then its review block, then its whole text.

``.tools/wiki/manifest.json`` (generated, never edited)
    For each page: its source, the wiki revision and capture date, the hash of the
    wiki text, the wiki's heading ids and the lines each kit block fills on the page.

``hoi4_wiki/SOURCES.json`` (generated)
    The attribution the license asks for: every page's wiki page, URL, revision and
    capture date.

A block's text reaches the page through ``lean.lean_text`` (evidence removed), at the
place ``at`` names:

* ``top``: under the title;
* ``bottom``: at the end of the page;
* ``section:<slug>``: at the end of that section's own text, before the next heading;
* ``heading:<slug>``: directly under that heading.

``<slug>`` is the heading's GitHub-style id (``slug``): ``## Focus Types`` is
``focus-types``. Blocks that share a place keep their sidecar order. A block whose
heading is gone upstream is put at the bottom and reported.

File names: a page's title is its level-1 heading, and its file is ``file_name(title)``,
the title in lowercase snake_case plus ``.md``. HOI4 Agent Tools derives a page's
title from its file name by reading ``_`` as a space (see ``agent_title``).

Standard library only; Python 3.9 or newer.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple

FENCE = "`" * 3
BEGIN = re.compile(r"^<!-- kit:begin ((?:[a-z]+=\"[^\"]*\" )+)-->$", re.M)
END = re.compile(r"^<!-- kit:end id=\"([^\"]*)\" -->$", re.M)
ANY_MARKER = re.compile(r"<!-- kit:(?:begin|end)\b")
ATTR = re.compile(r"([a-z]+)=\"([^\"]*)\"")
KIT_PAGE = "<!-- kit:page -->"
ID_SHAPE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
AT_SHAPE = re.compile(r"^(top|bottom|(section|heading):[^\s\"]+)$")
HEADING = re.compile(r"^(#{1,6}) (.*)$")
ANCHOR = re.compile(r"\s*<a id=\"([^\"]+)\"></a>")
REVIEW_ID = "review"
DEFAULT_REVIEW = (
    '<!-- kit:begin id="review" build="none" checked="never" -->\n'
    "Not yet checked against the installed game.\n"
    '<!-- kit:end id="review" -->'
)
REVIEW_ORDER = ["id", "build", "checked", "revision", "via", "sources"]

PAGE_FILE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*\.md$")
MEDIA_FILE = re.compile(r"^[a-z0-9][a-z0-9_.]*$")
TITLE_LINE = re.compile(r"^# (.+?)\s*$", re.M)
WIKI_SITE = "https://hoi4.paradoxwikis.com"

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WIKI_DIR = REPO / "hoi4_wiki"
SIDECAR_DIR = HERE / "kit"
MANIFEST = HERE / "manifest.json"
SOURCES_NAME = "SOURCES.json"
LICENSE_NAME = "LICENSE.txt"

Heading = Tuple[int, int, str]  # line index, level, visible text


# --- names ----------------------------------------------------------------

def file_stem(title: str) -> str:
    """The title in lowercase snake_case: ``Scripted GUI modding`` -> ``scripted_gui_modding``."""
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


def file_name(title: str) -> str:
    """The snapshot file name of the page titled `title`."""
    return file_stem(title) + ".md"


def agent_title(name: str) -> str:
    """The title HOI4 Agent Tools derives from a snapshot file name (``event_modding.md`` -> ``event modding``)."""
    return re.sub(r"\.md$", "", name, flags=re.I).replace("_", " ")


def wiki_url(page: str) -> str:
    """The live wiki URL of a page title."""
    return f"{WIKI_SITE}/{page.replace(' ', '_')}"


def page_title(text: str) -> Optional[str]:
    """The page title: its first level-1 heading outside code fences, or None."""
    inside = False
    for line in text.split("\n"):
        if line.lstrip().startswith(FENCE):
            inside = not inside
            continue
        match = None if inside else TITLE_LINE.match(line.rstrip("\r"))
        if match:
            return match.group(1)
    return None


def slug(text: str) -> str:
    """The GitHub-style id of a heading: ``Focus Types`` -> ``focus-types``.

    Markup is dropped first (link targets, HTML tags, code ticks, emphasis stars), then
    the text is lowercased, every character that is not a letter, digit, space, ``-``
    or ``_`` is removed, and spaces become hyphens.
    """
    text = ANCHOR.sub("", text)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("`", "").replace("*", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


# --- headings ---------------------------------------------------------------

def headings(lines: List[str]) -> List[Heading]:
    """Every heading outside code fences, with anchors removed from its text."""
    found = []
    inside = False
    for index, line in enumerate(lines):
        if line.lstrip().startswith(FENCE):
            inside = not inside
            continue
        match = None if inside else HEADING.match(line)
        if match:
            found.append((index, len(match.group(1)), ANCHOR.sub("", match.group(2)).strip()))
    return found


def heading_slugs(lines: List[str]) -> List[Tuple[int, int, str]]:
    """(line index, level, slug) for every heading, numbered as GitHub numbers repeats."""
    seen: Dict[str, int] = {}
    out = []
    for index, level, title in headings(lines):
        base = slug(title)
        count = seen.get(base, 0)
        seen[base] = count + 1
        out.append((index, level, base if count == 0 else f"{base}-{count}"))
    return out


# --- sidecars ---------------------------------------------------------------

class KitBlockError(ValueError):
    """A sidecar whose kit markers cannot be read."""


class Block(NamedTuple):
    attrs: Dict[str, str]
    start: int  # character offset of the begin marker
    end: int  # character offset just past the end marker
    text: str  # the text between the markers

    @property
    def id(self) -> str:
        return self.attrs.get("id", "")

    @property
    def at(self) -> str:
        return self.attrs.get("at", "")


def find_blocks(text: str) -> List[Block]:
    """Every kit block of a sidecar in order, or raise KitBlockError."""
    blocks: List[Block] = []
    seen = set()
    for begin in BEGIN.finditer(text):
        if blocks and begin.start() < blocks[-1].end:
            raise KitBlockError(f"kit block nested inside {blocks[-1].id!r}")
        attrs = dict(ATTR.findall(begin.group(1)))
        block_id = attrs.get("id", "")
        if not ID_SHAPE.match(block_id):
            raise KitBlockError(f"kit block id {block_id!r} must be lowercase letters, digits and hyphens")
        if block_id in seen:
            raise KitBlockError(f"duplicate kit block id {block_id!r}")
        seen.add(block_id)
        if block_id != REVIEW_ID and not AT_SHAPE.match(attrs.get("at", "")):
            raise KitBlockError(f"kit block {block_id!r} needs at= top, bottom, section:<slug> or heading:<slug>")
        end = END.search(text, begin.end())
        if end is None or end.group(1) != block_id:
            raise KitBlockError(f"kit block {block_id!r} is not closed by its own kit:end marker")
        if BEGIN.search(text, begin.end(), end.start()):
            raise KitBlockError(f"kit block {block_id!r} contains another kit:begin marker")
        inner = text[begin.end():end.start()].strip("\n")
        blocks.append(Block(attrs, begin.start(), end.end(), inner))
    if len(ANY_MARKER.findall(text)) != 2 * len(blocks):
        raise KitBlockError("a kit:begin or kit:end marker is malformed or unpaired")
    return blocks


def is_kit_page(sidecar: str) -> bool:
    return any(line.strip() == KIT_PAGE for line in sidecar.split("\n")[:4])


def review(sidecar: str) -> Optional[Dict[str, str]]:
    """Attributes of the sidecar's review block, or None when it has none."""
    try:
        blocks = find_blocks(sidecar)
    except KitBlockError:
        return None
    return next((block.attrs for block in blocks if block.id == REVIEW_ID), None)


def set_review(sidecar: str, updates: Dict[str, str]) -> str:
    """The sidecar with its review marker's attributes updated (an empty value removes one)."""
    block = next((b for b in find_blocks(sidecar) if b.id == REVIEW_ID), None)
    if block is None:
        raise KitBlockError("the sidecar has no review block")
    attrs = {k: v for k, v in {**block.attrs, **updates}.items() if v != ""}
    keys = [k for k in REVIEW_ORDER if k in attrs] + sorted(k for k in attrs if k not in REVIEW_ORDER)
    marker = "<!-- kit:begin " + "".join(f'{k}="{attrs[k]}" ' for k in keys) + "-->"
    return sidecar[:block.start] + marker + sidecar[sidecar.index("\n", block.start):]


def kit_page_body(sidecar: str) -> str:
    """A kit page's text after its title, kit:page marker and review block."""
    text = sidecar
    for block in reversed(find_blocks(sidecar)):
        if block.id == REVIEW_ID:
            text = text[:block.start] + text[block.end:]
    lines = [line for line in text.split("\n") if line.strip() != KIT_PAGE]
    title = next((i for i, line in enumerate(lines) if TITLE_LINE.match(line)), -1)
    return "\n".join(lines[title + 1:]).strip("\n")


# --- placing blocks ---------------------------------------------------------

def insertion_line(lines: List[str], at: str) -> Optional[int]:
    """Index of the line a block placed `at` goes in front of, or None if its heading is gone.

    `lines` is a page without kit text (``text.rstrip("\\n").split("\\n")``).
    """
    if at == "top":
        return 1
    if at == "bottom":
        return len(lines)
    kind, _, wanted = at.partition(":")
    marks = [h for h in heading_slugs(lines) if h[1] > 1]
    for position, (index, _level, name) in enumerate(marks):
        if name != wanted:
            continue
        if kind == "heading":
            return index + 1
        return marks[position + 1][0] if position + 1 < len(marks) else len(lines)
    return None


def _splice(lines: List[str], index: int, block: List[str]) -> List[str]:
    """Insert lines in front of line `index` with exactly one blank line around them."""
    before, after = lines[:index], lines[index:]
    while before and before[-1].strip() == "":
        before.pop()
    while after and after[0].strip() == "":
        after.pop(0)
    return before + [""] + block + ([""] + after if after else [])


class Placed(NamedTuple):
    text: str  # the page
    spans: Dict[str, List[int]]  # block id -> [first line, last line], 1-based
    orphans: List[str]  # ids of blocks whose heading is gone, kept at the bottom


def assemble(base: str, blocks: List[Tuple[str, str, str]]) -> Placed:
    """Put kit text into a page's wiki text.

    `blocks` holds (id, at, lean text) in sidecar order. The result can be taken apart
    again with ``disassemble`` to give back `base` exactly.
    """
    lines = base.rstrip("\n").split("\n")
    groups: Dict[int, List[Tuple[str, str]]] = defaultdict(list)
    orphans = []
    for block_id, at, text in blocks:
        index = insertion_line(lines, at)
        if index is None:
            orphans.append(block_id)
            index = len(lines)
        groups[index].append((block_id, text))
    for index in sorted(groups, reverse=True):
        chunk: List[str] = []
        for block_id, text in groups[index]:
            body = text.strip("\n").split("\n")
            # A marker line in front of each block records where it lands; it is removed below.
            chunk += ([""] if chunk else []) + [f"\0{block_id}\0{len(body)}"] + body
        lines = _splice(lines, index, chunk)
    spans: Dict[str, List[int]] = {}
    out: List[str] = []
    for line in lines:
        if line.startswith("\0"):
            _, block_id, count = line.split("\0")
            spans[block_id] = [len(out) + 1, len(out) + int(count)]
            continue
        out.append(line)
    return Placed("\n".join(out).rstrip("\n") + "\n", spans, orphans)


def disassemble(page: str, spans: Dict[str, List[int]]) -> str:
    """The page without the lines its kit blocks fill: the wiki text it was built from."""
    lines = page.rstrip("\n").split("\n")
    for first, last in sorted(spans.values(), reverse=True):
        start, end = first - 1, last
        if end < len(lines) and lines[end].strip() == "":
            end += 1
        elif start > 0 and lines[start - 1].strip() == "":
            start -= 1
        del lines[start:end]
    return "\n".join(lines).rstrip("\n") + "\n"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --- manifest and sources ---------------------------------------------------

def load_manifest(path: Optional[Path] = None) -> Dict[str, object]:
    """The manifest (``MANIFEST`` unless `path` is given), or an empty one."""
    path = MANIFEST if path is None else path
    if not path.exists():
        return {"pages": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(data: object) -> str:
    return json.dumps(data, indent=1, ensure_ascii=False, sort_keys=False) + "\n"


def write_text(path: Path, text: str) -> bool:
    """Write `text` with LF line ends when it differs from the file; return whether it changed."""
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return True


SOURCES_NOTICE = (
    "Wiki pages in this folder are adapted from the Hearts of Iron IV Wiki ({site}), "
    "written by its editors and licensed under CC BY-SA 3.0. The Agentic HOI4 Modding Kit "
    "converted them to Markdown, removed site navigation and added its own corrections and "
    "notes in the text. Kit pages were written by the kit's contributors. Everything the kit "
    "wrote here is licensed under CC BY-SA 3.0 as well. Images in media/ keep their own terms. "
    "See LICENSE.txt."
)


def sources_document(manifest: Dict[str, object]) -> Dict[str, object]:
    """The attribution file for hoi4_wiki/: license and the source of every page."""
    pages = []
    entries = manifest.get("pages", {})
    assert isinstance(entries, dict)
    for name in sorted(entries):
        entry = entries[name]
        item: Dict[str, object] = {"file": name, "title": entry["title"], "source": entry["source"]}
        if entry["source"] == "wiki":
            item.update({
                "wiki_page": entry["wiki_page"],
                "url": wiki_url(entry["wiki_page"]),
                "revision": entry.get("revision"),
                "revision_url": f"{WIKI_SITE}/index.php?oldid={entry.get('revision')}",
                "captured": entry.get("captured"),
            })
        pages.append(item)
    return {
        "license": "CC BY-SA 3.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
        "license_file": LICENSE_NAME,
        "notice": SOURCES_NOTICE.format(site=WIKI_SITE),
        "pages": pages,
    }
