#!/usr/bin/env python
"""Validate the kit's HOI4 wiki. Read-only; never writes.

This is the acceptance check for the wiki tools. It exits non-zero when the pages in
``hoi4_wiki/`` are not lean, self-contained and readable, or do not match the kit
sidecars and the manifest. It reports:

* anything on a page that is not modding text: HTML comments, ``<a id>`` anchors,
  evidence tags, "Kit note" style labels, capture lines, tables of contents and
  navigation footers;
* unbalanced code fences and fenced blocks that would break a table row;
* outbound hyperlinks, which the wiki must not contain;
* page and media file names that are not lowercase snake_case without spaces, pages
  whose file name is not the slug of their level-1 heading, and titles that HOI4
  Agent Tools would not read back from the file name (it turns `_` into a space);
* links to missing pages (a link must match the file name letter for letter, so it
  also works on a case-sensitive file system), and section links whose heading slug
  is absent;
* images with no file on disk, or image files nothing references;
* table rows whose column count differs from their header;
* pages that do not have exactly one level-1 heading;
* encoding damage: byte order marks, non-breaking and zero-width characters, and mojibake;
* sidecars whose markers are unpaired, that lack a review block, that use a malformed
  evidence tag, or whose evidence would leave a broken sentence on the page;
* pages that differ from what their sidecar and wiki text give (``render_wiki.py --check``),
  kit blocks whose heading is gone, a stale ``SOURCES.json`` and a missing ``LICENSE.txt``.

Usage::

    python -B .tools/wiki/verify_wiki_snapshot.py
    python -B .tools/wiki/verify_wiki_snapshot.py .tmp/wiki-preview      # its manifest.json is used
    python -B .tools/wiki/verify_wiki_snapshot.py --quiet
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit_blocks  # the page format, next to this script
import lean  # annotated kit text -> lean text
import render_wiki  # rebuilds pages from the sidecars

FENCE = "`" * 3
PIPE = re.compile(r"(?<!\\)\|")
VERSIONED_TAG = re.compile(r"\[(?:vanilla-confirmed|game-tested)\b[^\]\n]*\]")
WELL_FORMED_TAG = re.compile(r"^\[(?:vanilla-confirmed|game-tested) \d+(?:\.\d+){1,3}\]$")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(<?([^()<>\s]+)>?\)")
KIT_LABEL = re.compile(r"\*\*Kit (?:note|correction|addition|review)\b")
LEAN_FORBIDDEN = (
    (re.compile(r"<!--"), "html_comment", "an HTML comment"),
    (re.compile(r"<a id=\""), "anchor", "an <a id> anchor (headings get GitHub-style ids)"),
    (lean.ANY_TAG, "evidence_tag", "an evidence tag (evidence belongs in the sidecar)"),
    (KIT_LABEL, "kit_label", "a Kit note/correction/addition/review label"),
    (lean.CAPTURE, "capture_line", "a capture line (sources are in SOURCES.json)"),
    (re.compile(r"^## (?:Table of contents|Navigation)$"), "furniture", "a table of contents or navigation footer"),
)

Report = Callable[[str, str, str], None]


def columns(line: str) -> int:
    return len(PIPE.findall(line))


def prose_lines(lines: List[str]):
    """(index, line with inline code blanked) for every line outside code fences."""
    inside = False
    for index, line in enumerate(lines):
        if line.lstrip().startswith(FENCE):
            inside = not inside
            continue
        if not inside:
            yield index, re.sub(r"(`+)[^`]*?\1", "``", line)


def check_encoding(name: str, text: str, report: Report) -> None:
    """Non-breaking, zero-width and control characters, and mojibake."""
    for pat, kind in (("\u00a0", "nbsp"), ("\u200b", "zwsp"), ("\u2011", "nb_hyphen"),
                      ("[\u0080-\u009f]", "control_char")):
        hits = re.findall(pat, text)
        if hits:
            report(kind, name, f"{len(hits)} occurrence(s)")
    for bad in ("\u00e2\u20ac", "\u00c3\u00a9", "\u00d0\u0178", "\u00ef\u00bb\u00bf", "\u00c2 "):
        if bad in text:
            report("mojibake", name, bad)


def check_lean(name: str, lines: List[str], report: Report) -> None:
    """Nothing on the page that is not modding text."""
    for index, line in prose_lines(lines):
        for pattern, kind, what in LEAN_FORBIDDEN:
            if pattern.search(line):
                report(kind, name, f"line {index + 1}: {what}")


def check_file_name(name: str, text: str, report: Report) -> None:
    """Lowercase snake_case, the slug of the level-1 heading, and readable by HOI4 Agent Tools."""
    title = kit_blocks.page_title(text)
    if not kit_blocks.PAGE_FILE.match(name):
        report("file_name", name, "page file names are lowercase snake_case without "
               "spaces, for example scripted_gui_modding.md")
    elif title is not None and kit_blocks.file_name(title) != name:
        report("file_name", name, f"the page {title!r} belongs in {kit_blocks.file_name(title)}")
    elif title is not None and kit_blocks.agent_title(name).lower() != title.lower():
        # HOI4 Agent Tools reads the page title from the file name (`_` as a space)
        # and matches it without regard to case; punctuation in a title is lost.
        report("agent_title", name, f"HOI4 Agent Tools would read this file as the page "
               f"{kit_blocks.agent_title(name)!r}, not {title!r}")


def check_fences(name: str, lines: List[str], report: Report) -> None:
    fences = [i + 1 for i, line in enumerate(lines) if line.strip().startswith(FENCE)]
    if len(fences) % 2:
        report("odd_fences", name, f"unbalanced code fences at {fences[:6]}")
    inside = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(FENCE):
            inside = not inside
            continue
        if inside and stripped.startswith("|") and re.match(r"^\|[\s:|-]+\|$", stripped):
            report("fence_in_table", name, f"line {i + 1}")
        if not inside and stripped.startswith("|") and FENCE in line:
            report("fence_in_table", name, f"line {i + 1}: fenced code inside a table row")
    if inside:
        report("odd_fences", name, "file ends inside a code fence")


def check_links(name: str, lines: List[str], slugs: Dict[str, Set[str]], exists: Callable[[str], bool],
                report: Report) -> None:
    """Outbound links, links to missing pages or media, and section links without a heading."""
    for i, line in prose_lines(lines):
        for match in LINK.finditer(line):
            target = match.group(1)
            if re.match(r"https?://", target):
                report("external_link", name, target[:70])
                continue
            page, _, fragment = target.partition("#")
            if page and not exists(page):
                report("broken_link", name, f"line {i + 1}: missing file {page}")
            elif fragment and fragment not in slugs.get(page or name, set()):
                report("broken_anchor", name, f"line {i + 1}: {page or name}#{fragment}")
        for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", line):
            src = match.group(1)
            if src.startswith("http"):
                report("remote_image", name, f"line {i + 1}: {src[:70]}")
            elif not exists(src):
                report("missing_media", name, f"line {i + 1}: {src}")


def check_table_row(name: str, number: int, line: str, width: int, report: Report) -> None:
    if columns(line) != width:
        report("ragged_table", name, f"line {number}: {columns(line)} cols vs {width}")
    spans = line.split("`")[1::2]
    longest = max((len(s) for s in spans), default=0)
    if longest >= 300:
        # The signature of a multi-line code sample flattened into a single span.
        report("flat_cell_code", name, f"line {number}: one code span of {longest} chars")
    indented = next((s for s in spans if len(s) - len(s.lstrip(" ")) >= 4), None)
    if indented is not None:
        # Indented code belongs in a fenced block after the table; a renderer collapses it in a cell.
        report("indented_cell_code", name, f"line {number}: {indented[:50]!r}")


def check_tables(name: str, lines: List[str], report: Report) -> None:
    i = 0
    while i < len(lines):
        if (lines[i].strip().startswith("|") and i + 1 < len(lines)
                and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1])):
            width = columns(lines[i])
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                check_table_row(name, j + 1, lines[j], width, report)
                j += 1
            i = j
        else:
            i += 1


def check_structure(name: str, lines: List[str], report: Report) -> None:
    """One level-1 heading, and no ':' definition lists (not CommonMark)."""
    h1 = 0
    for i, line in prose_lines(lines):
        if re.match(r"^# ", line):
            h1 += 1
        if not line.lstrip().startswith("|") and re.match(r"^\s*:", line):
            report("definition_list", name, f"line {i + 1}")
    if h1 != 1:
        report("h1_count", name, f"{h1} level-1 headings")


def check_media(directory: str, files: List[str], media_names: Set[str], report: Report):
    """Media file names, and media that pages reference but lack or that nothing references."""
    for media_name in sorted(media_names):
        if not kit_blocks.MEDIA_FILE.match(media_name):
            report("file_name", "(media)", f"{media_name}: media file names are lowercase without spaces")
    referenced: Set[str] = set()
    long_rows = 0
    for name in files:
        text = Path(directory, name).read_text(encoding="utf-8")
        referenced.update(os.path.basename(m) for m in re.findall(r"\]\((media/[^)]+)\)", text))
        long_rows += sum(1 for line in text.split("\n") if line.startswith("|") and len(line) > 400)
    for name in sorted(referenced - media_names)[:20]:
        report("missing_media", "(media)", name)
    for name in sorted(media_names - referenced)[:20]:
        report("orphan_media", "(media)", name)
    return referenced, long_rows


def check_sidecar(name: str, text: str, report: Report) -> None:
    """Markers, the review block, evidence tags and evidence placement of one sidecar."""
    label = f"kit/{name}"
    try:
        blocks = kit_blocks.find_blocks(text)
    except kit_blocks.KitBlockError as error:
        report("kit_block", label, str(error))
        return
    review = next((b for b in blocks if b.id == kit_blocks.REVIEW_ID), None)
    if review is None:
        report("kit_block", label, "no review block")
    elif not re.match(r"^(none|\d+(\.\d+){1,3})$", review.attrs.get("build", "")):
        report("kit_block", label, f"review build {review.attrs.get('build')!r} is not a game version or none")
    kit_text = [kit_blocks.kit_page_body(text)] if kit_blocks.is_kit_page(text) else [
        b.text for b in blocks if b.id != kit_blocks.REVIEW_ID]
    for chunk in kit_text:
        for tag in VERSIONED_TAG.findall(chunk):
            if not WELL_FORMED_TAG.match(tag):
                report("evidence_tag", label, f"{tag} must be [vanilla-confirmed <build>] "
                       "or [game-tested <build>], with sources outside the brackets")
        for problem in lean.evidence_problems(chunk):
            report("evidence_placement", label, problem)


def check_sources(directory: str, manifest_path: Path, report: Report) -> None:
    """Every page has a sidecar and a manifest entry; pages match what the sidecars give."""
    manifest = kit_blocks.load_manifest(manifest_path)
    pages = manifest.get("pages", {})
    assert isinstance(pages, dict)
    on_disk = {n for n in os.listdir(directory) if n.endswith(".md")}
    sidecars = {p.name for p in kit_blocks.SIDECAR_DIR.glob("*.md")}
    for name in sorted(on_disk - set(pages)):
        report("manifest", name, "page has no manifest entry; import it with sync_wiki_snapshot.py")
    for name in sorted(on_disk - sidecars):
        report("sidecar", name, f"no sidecar .tools/wiki/kit/{name}")
    for name in sorted(sidecars - on_disk):
        report("sidecar", f"kit/{name}", "sidecar has no page; run render_wiki.py or the sync")
    for name in sorted(sidecars):
        check_sidecar(name, (kit_blocks.SIDECAR_DIR / name).read_text(encoding="utf-8"), report)
    result = render_wiki.rebuild(write=False, wiki_dir=Path(directory), manifest_path=manifest_path)
    for line in result["failed"]:
        report("render", line.split(":", 1)[0], line.split(":", 1)[1].strip())
    for line in result["orphans"]:
        report("orphan_block", line.split(":", 1)[0], f"kit block {line.split(':', 1)[1].strip()} "
               "names a heading the page no longer has; point its at= at the new heading slug")
    for name in result["changed"]:
        report("out_of_date", name, "differs from its sidecar; run render_wiki.py")
    if not os.path.exists(os.path.join(directory, kit_blocks.LICENSE_NAME)):
        report("license", kit_blocks.LICENSE_NAME, "missing")


def page_slugs(directory: str, files: List[str]) -> Dict[str, Set[str]]:
    slugs = {}
    for name in files:
        lines = Path(directory, name).read_text(encoding="utf-8").split("\n")
        slugs[name] = {s for _i, _l, s in kit_blocks.heading_slugs(lines)}
    return slugs


def verify(directory: str, show_details: bool = True, manifest: Optional[Path] = None) -> int:
    problems: Counter = Counter()
    details: List[str] = []

    def report(kind: str, page: str, message: str) -> None:
        problems[kind] += 1
        details.append(f"  [{kind}] {page}: {message}")

    files = sorted(f for f in os.listdir(directory) if f.endswith(".md"))
    # Exact-case names: Windows and macOS would resolve a link with the wrong case.
    names = set(os.listdir(directory))
    media_dir = os.path.join(directory, "media")
    media_names = set(os.listdir(media_dir)) if os.path.isdir(media_dir) else set()

    def exists(relative: str) -> bool:
        head, _, tail = relative.partition("/")
        if not tail:
            return head in names
        if head == "media" and "/" not in tail:
            return tail in media_names
        return os.path.exists(os.path.join(directory, relative.replace("/", os.sep)))

    slugs = page_slugs(directory, files)
    for name in files:
        raw = Path(directory, name).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            report("bom", name, "file starts with a byte order mark")
        # A checkout with core.autocrlf=true has CRLF pages; the checks read lines.
        text = raw.decode("utf-8").replace("\r\n", "\n")
        lines = text.split("\n")
        check_file_name(name, text, report)
        check_lean(name, lines, report)
        check_fences(name, lines, report)
        check_links(name, lines, slugs, exists, report)
        check_tables(name, lines, report)
        check_structure(name, lines, report)
        check_encoding(name, text, report)
    referenced, long_rows = check_media(directory, files, media_names, report)
    if manifest is not None:
        check_sources(directory, manifest, report)
    print(f"pages: {len(files)}   media on disk: {len(media_names)}   referenced: {len(referenced)}")
    # A Markdown table row is one line by definition, so rows carrying a code
    # example are legitimately long. Reported for visibility, not as a defect.
    print(f"table rows over 400 characters: {long_rows}")
    if manifest is None:
        print("no manifest.json for this folder: sidecar and rebuild checks skipped")
    print("\nPROBLEM SUMMARY")
    if not problems:
        print("  none")
    for kind, count in problems.most_common():
        print(f"  {count:5d}  {kind}")
    if details and show_details:
        print("\nDETAILS (first 120)")
        for line in details[:120]:
            print(line)
    return 1 if problems else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the kit's HOI4 wiki.")
    parser.add_argument("directory", nargs="?", default=None, help="wiki folder (default hoi4_wiki/)")
    parser.add_argument("--quiet", action="store_true", help="print only the problem summary")
    args = parser.parse_args()
    directory = Path(args.directory) if args.directory else kit_blocks.WIKI_DIR
    if not directory.is_dir():
        print(f"not a directory: {directory}")
        return 1
    manifest: Optional[Path] = None
    if (directory / "manifest.json").exists():
        manifest = directory / "manifest.json"
    elif directory.resolve() == kit_blocks.WIKI_DIR.resolve():
        manifest = kit_blocks.MANIFEST
    return verify(str(directory), show_details=not args.quiet, manifest=manifest)


if __name__ == "__main__":
    sys.exit(main())
