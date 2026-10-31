"""Page format shared by the wiki snapshot tools: kit blocks, kit pages and review markers.

A snapshot page is regenerated from the live wiki on every refresh, so a hand edit to
its wiki text is lost. Local improvements live in kit blocks instead, and the sync
carries every block over into the fresh page:

    <!-- kit:begin id="effects-scopes" at="section:Country_scope" -->
    **Kit note** [docs] ...
    <!-- kit:end id="effects-scopes" -->

``at`` says where the block belongs, and the sync re-inserts it there:

* ``top``: under the page's capture line, before the table of contents;
* ``bottom``: after the last section, before the navigation footer;
* ``section:<anchor>``: at the end of that section's own text, before the next heading;
* ``heading:<anchor>``: directly under that heading.

``<anchor>`` is an ``<a id="...">`` of a wiki heading on the same page. Blocks that
share a place keep their order. A block whose anchor no longer exists upstream is kept
at the bottom of the page and reported, so nothing written locally is ever dropped.

A kit page is written entirely by the kit. One of its first lines is
``<!-- kit:page -->``; the sync never fetches it and only refreshes its table of
contents and navigation footer.

Every page has one ``review`` block at ``top``. Its begin marker records the review:
``build`` (the game build the page was checked against, or ``none``), ``checked``
(the date) and, on wiki pages, ``revision`` (the wiki revision that was reviewed).

File names: a page's title is its level-1 heading, and its file is ``file_name(title)``,
the title in lowercase kebab-case plus ``.md`` (``Scripted GUI modding`` is
``scripted-gui-modding.md``). The file name never carries the title, so tools read the
title from the heading.

Standard library only; Python 3.9 or newer.
"""

from __future__ import annotations

import re
from collections import defaultdict
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
ANCHOR = re.compile(r"<a id=\"([^\"]+)\"></a>")
CAPTURE = re.compile(r"^\*(Offline snapshot of the Hearts of Iron IV Wiki page|Kit page)\b")
REVISION = re.compile(r"\brevision (\d+)\b")
REVIEW_ID = "review"
DEFAULT_REVIEW = (
    '<!-- kit:begin id="review" at="top" build="none" checked="never" -->\n'
    "**Kit review:** not yet checked against the installed game. Treat version-specific "
    "statements on this page as unverified until it is.\n"
    '<!-- kit:end id="review" -->'
)

Heading = Tuple[int, int, str, List[str]]  # line index, level, visible text, anchors

PAGE_FILE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
MEDIA_FILE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
TITLE_LINE = re.compile(r"^# (.+?)\s*$", re.M)


def file_stem(title: str) -> str:
    """The title in lowercase kebab-case: ``Scripted GUI modding`` -> ``scripted-gui-modding``."""
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def file_name(title: str) -> str:
    """The snapshot file name of the page titled `title`."""
    return file_stem(title) + ".md"


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


class KitBlockError(ValueError):
    """A page whose kit markers cannot be paired."""


class Block(NamedTuple):
    attrs: Dict[str, str]
    start: int  # character offset of the begin marker
    end: int  # character offset just past the end marker
    text: str

    @property
    def id(self) -> str:
        return self.attrs.get("id", "")

    @property
    def at(self) -> str:
        return self.attrs.get("at", "")


def find_blocks(text: str) -> List[Block]:
    """Return every kit block in page order, or raise KitBlockError."""
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
        if not AT_SHAPE.match(attrs.get("at", "")):
            raise KitBlockError(f"kit block {block_id!r} needs at= top, bottom, section:<anchor> or heading:<anchor>")
        end = END.search(text, begin.end())
        if end is None or end.group(1) != block_id:
            raise KitBlockError(f"kit block {block_id!r} is not closed by its own kit:end marker")
        if BEGIN.search(text, begin.end(), end.start()):
            raise KitBlockError(f"kit block {block_id!r} contains another kit:begin marker")
        blocks.append(Block(attrs, begin.start(), end.end(), text[begin.start():end.end()]))
    if len(ANY_MARKER.findall(text)) != 2 * len(blocks):
        raise KitBlockError("a kit:begin or kit:end marker is malformed or unpaired")
    return blocks


def strip_blocks(text: str, blocks: Optional[List[Block]] = None) -> str:
    """Return the page without its kit blocks: the text the wiki supplied."""
    blocks = find_blocks(text) if blocks is None else blocks
    parts, cursor = [], 0
    for block in blocks:
        parts.append(text[cursor:block.start])
        cursor = block.end
    parts.append(text[cursor:])
    return re.sub(r"\n{3,}", "\n\n", "".join(parts))


def is_kit_page(text: str) -> bool:
    return any(line.strip() == KIT_PAGE for line in text.split("\n")[:8])


def headings(lines: List[str]) -> List[Heading]:
    """Every heading outside code fences."""
    found = []
    inside = False
    for index, line in enumerate(lines):
        if line.lstrip().startswith(FENCE):
            inside = not inside
            continue
        match = None if inside else HEADING.match(line)
        if match:
            title = ANCHOR.sub("", match.group(2)).strip()
            found.append((index, len(match.group(1)), title, ANCHOR.findall(line)))
    return found


def layout(lines: List[str]) -> Dict[str, int]:
    """Line indices of the page furniture.

    ``capture`` is the italic capture line, ``toc`` the table of contents heading (-1 when
    there is none), ``body`` the ``---`` rule that opens the article and ``footer`` the
    ``---`` rule in front of the navigation footer (the line count when there is none).
    """
    capture = next((i for i, line in enumerate(lines[:12]) if CAPTURE.match(line)), 0)
    marks = headings(lines)
    toc = next((i for i, _level, title, _a in marks if title == "Table of contents"), -1)
    start_from = toc if toc >= 0 else capture
    body = next((i for i in range(start_from + 1, len(lines)) if lines[i].strip() == "---"), len(lines))
    footer = len(lines)
    navigation = [i for i, level, title, _a in marks if level == 2 and title == "Navigation" and i > body]
    if navigation:
        rule = navigation[-1] - 1
        while rule > body and lines[rule].strip() == "":
            rule -= 1
        footer = rule if lines[rule].strip() == "---" else navigation[-1]
    return {"capture": capture, "toc": toc, "body": body, "footer": footer}


def insertion_line(lines: List[str], at: str) -> Optional[int]:
    """Index of the line a block placed `at` goes in front of, or None if its anchor is gone.

    `lines` must be a page without kit blocks, so headings inside blocks cannot mislead it.
    """
    marks = layout(lines)
    if at == "top":
        return marks["capture"] + 1
    if at == "bottom":
        return marks["footer"]
    kind, _, anchor = at.partition(":")
    found = [h for h in headings(lines) if marks["body"] < h[0] < marks["footer"]]
    for position, (index, _level, _title, anchors) in enumerate(found):
        if anchor not in anchors:
            continue
        if kind == "heading":
            return index + 1
        return found[position + 1][0] if position + 1 < len(found) else marks["footer"]
    return None


def splice(lines: List[str], index: int, block: str) -> List[str]:
    """Insert text in front of line `index` with exactly one blank line around it."""
    before, after = lines[:index], lines[index:]
    while before and before[-1].strip() == "":
        before.pop()
    while after and after[0].strip() == "":
        after.pop(0)
    return before + [""] + block.split("\n") + [""] + after


def place_blocks(text: str, blocks: List[Block]) -> Tuple[str, List[Block]]:
    """Insert blocks into a page without kit blocks; return it and the blocks whose anchor is gone.

    Insertion points are worked out on the plain page first and filled from the bottom
    up, so blocks that share a place keep their order. A block whose anchor is missing
    goes to the bottom with its `at` unchanged, and the verify check reports it until
    someone moves it.
    """
    lines = text.rstrip("\n").split("\n")
    groups: Dict[int, List[Block]] = defaultdict(list)
    orphans = []
    for block in blocks:
        index = insertion_line(lines, block.at)
        if index is None:
            orphans.append(block)
            index = insertion_line(lines, "bottom") or len(lines)
        groups[index].append(block)
    for index in sorted(groups, reverse=True):
        lines = splice(lines, index, "\n\n".join(block.text for block in groups[index]))
    return "\n".join(lines).rstrip("\n") + "\n", orphans


def ensure_review(blocks: List[Block]) -> List[Block]:
    """Add the placeholder review block when a page has none."""
    if any(block.id == REVIEW_ID for block in blocks):
        return blocks
    return find_blocks(DEFAULT_REVIEW) + blocks


def review(text: str) -> Optional[Dict[str, str]]:
    """Attributes of the page's review block, or None when it has none."""
    try:
        blocks = find_blocks(text)
    except KitBlockError:
        return None
    return next((block.attrs for block in blocks if block.id == REVIEW_ID), None)


def capture_revision(text: str) -> Optional[int]:
    """The wiki revision named on the page's capture line."""
    lines = text.split("\n")
    line = lines[layout(lines)["capture"]]
    match = REVISION.search(line) if CAPTURE.match(line) else None
    return int(match.group(1)) if match else None


def refresh_toc(text: str) -> str:
    """Rebuild the table of contents from the body's headings, kit headings included."""
    lines = text.rstrip("\n").split("\n")
    marks = layout(lines)
    entries: List[str] = []
    base = None
    for index, level, title, anchors in headings(lines):
        if index <= marks["body"] or index >= marks["footer"] or not anchors:
            continue
        base = level if base is None else base
        entries.append("  " * max(0, level - base) + f"- [{title}](#{anchors[0]})")
    head = lines[:marks["toc"] if marks["toc"] >= 0 else marks["body"]]
    while head and head[-1].strip() == "":
        head.pop()
    toc = ["", "## Table of contents", "", *entries] if entries else []
    return "\n".join(head + toc + [""] + lines[marks["body"]:]).rstrip("\n") + "\n"


def replace_footer(text: str, footer: str) -> str:
    """Swap the navigation footer (from its ``---`` rule to the end) for `footer`."""
    lines = text.rstrip("\n").split("\n")
    marks = layout(lines)
    head = lines[:marks["footer"]]
    while head and head[-1].strip() == "":
        head.pop()
    return "\n".join(head + ["", "---", "", footer.strip("\n")]) + "\n"


def position_problems(text: str) -> List[str]:
    """Kit blocks that do not sit where their `at` says, and a missing review block."""
    try:
        blocks = find_blocks(text)
    except KitBlockError as error:
        return [str(error)]
    lines = text.split("\n")
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line) + 1)
    upstream = {a for _i, _l, _t, anchors in headings(strip_blocks(text, blocks).split("\n")) for a in anchors}
    marks = layout(lines)
    wiki_headings = [h for h in headings(lines) if not any(b.start <= starts[h[0]] < b.end for b in blocks)]
    problems = []
    for block in blocks:
        line = text.count("\n", 0, block.start)
        problem = _position_problem(block, line, marks, upstream, wiki_headings)
        if problem:
            problems.append(f"kit block {block.id!r}: {problem}")
    if not any(block.id == REVIEW_ID for block in blocks):
        problems.append("page has no review block")
    return problems


def _position_problem(block: Block, line: int, marks: Dict[str, int], upstream: set, wiki_headings: List[Heading]) -> str:
    kind, _, anchor = block.at.partition(":")
    if kind == "top":
        limit = marks["toc"] if marks["toc"] >= 0 else marks["body"]
        return "" if line < limit else "at=top but it sits below the table of contents"
    if kind == "bottom":
        later = [h for h in wiki_headings if line < h[0] < marks["footer"]]
        return "at=bottom but a wiki section follows it" if later else ""
    if anchor not in upstream:
        return f"anchor {anchor!r} is not a wiki heading on this page"
    owner = next((h[3] for h in reversed(wiki_headings) if h[0] < line), [])
    return "" if anchor in owner else f"at={block.at} but it sits under another heading"
