#!/usr/bin/env python
"""Validate the offline Paradox wiki snapshot. Read-only; never writes.

This is the acceptance check for ``.tools/wiki/sync_wiki_snapshot.py``. It exits
non-zero when the snapshot is not self-contained and readable, and reports:

* unbalanced code fences and fenced blocks that would break a table row;
* outbound hyperlinks, which the snapshot must not contain;
* page and media file names that are not lowercase snake_case without spaces, pages
  whose file name is not the slug of their level-1 heading, and titles that HOI4
  Agent Tools would not read back from the file name (it turns `_` into a space);
* links to missing snapshot files (a link must match the file name letter for
  letter, so it also works on a case-sensitive file system), and section links
  whose anchor is absent;
* images with no file on disk, or image files nothing references;
* table rows whose column count differs from their header;
* pages that do not have exactly one level-1 heading;
* encoding damage: byte order marks, non-breaking and
  zero-width characters, and mojibake;
* kit blocks that are unpaired, sit away from the place their ``at`` names,
  point at a heading the page no longer has, or do not say they are kit text;
* snapshot pages without a review block, and a missing ``LICENSE.txt``.

Usage::

    python -B .tools/wiki/verify_wiki_snapshot.py
    python -B .tools/wiki/verify_wiki_snapshot.py .tmp/wiki-preview
    python -B .tools/wiki/verify_wiki_snapshot.py --quiet
"""

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit_blocks  # the page format, next to this script

FENCE = "`" * 3
PIPE = re.compile(r"(?<!\\)\|")
VERSIONED_TAG = re.compile(r"\[(?:vanilla-confirmed|game-tested)\b[^\]\n]*\]")
WELL_FORMED_TAG = re.compile(r"^\[(?:vanilla-confirmed|game-tested) \d+(?:\.\d+){1,3}\]$")


def find_repo_root(start):
    """Walk up from this file until the snapshot directory is found."""
    current = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(current, "paradox_wiki")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        current = parent


def columns(line):
    return len(PIPE.findall(line))


def check_encoding(name, text, report):
    """Non-breaking, zero-width and control characters, and mojibake."""
    # Markdown escapes preserve literal punctuation and are not encoding damage.
    for pat, kind in (("\u00a0", "nbsp"), ("\u200b", "zwsp"),
                      ("\u2011", "nb_hyphen"),
                      ("[\u0080-\u009f]", "control_char")):
        hits = re.findall(pat, text)
        if hits:
            report(kind, name, f"{len(hits)} occurrence(s)")

    for bad in ("\u00e2\u20ac", "\u00c3\u00a9", "\u00d0\u0178",
                "\u00ef\u00bb\u00bf", "\u00c2 "):
        if bad in text:
            report("mojibake", name, bad)


def check_kit(name, text, report):
    """Kit blocks, the review block, and the label that marks kit text."""
    # A Windows checkout with core.autocrlf=true has CRLF pages.
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")
    snapshot_page = kit_blocks.CAPTURE.match(lines[kit_blocks.layout(lines)["capture"]])
    for problem in kit_blocks.position_problems(text):
        if snapshot_page or "no review block" not in problem:
            report("kit_block", name, problem)
    try:
        blocks = kit_blocks.find_blocks(text)
    except kit_blocks.KitBlockError:
        return  # already reported
    for block in blocks:
        body = [line for line in block.text.split("\n")[1:-1] if line.strip()]
        if not body or "Kit" not in body[0]:
            report("kit_label", name,
                   f"kit block {block.id!r}: first line must say it is kit text")
    # Tag counts and the re-check after a game update read the build from the tag itself.
    kit_text = [text] if kit_blocks.is_kit_page(text) else [block.text for block in blocks]
    for chunk in kit_text:
        for tag in VERSIONED_TAG.findall(chunk):
            if not WELL_FORMED_TAG.match(tag):
                report("evidence_tag", name, f"{tag} must be [vanilla-confirmed <build>] "
                       "or [game-tested <build>], with sources outside the brackets")
    review = kit_blocks.review(text)
    if review and not re.match(r"^(none|\d+(\.\d+){1,3})$", review.get("build", "")):
        report("kit_block", name, f"review build {review.get('build')!r} is not a "
               "game version or none")


def check_file_name(name, text, report):
    """Lowercase snake_case, the slug of the level-1 heading, and readable by HOI4 Agent Tools."""
    title = kit_blocks.page_title(text)
    if not kit_blocks.PAGE_FILE.match(name):
        report("file_name", name, "page file names are lowercase snake_case without "
               "spaces, for example scripted_gui_modding.md")
    elif title is not None and kit_blocks.file_name(title) != name:
        report("file_name", name, f"the page {title!r} belongs in "
               f"{kit_blocks.file_name(title)}")
    elif title is not None and kit_blocks.agent_title(name).lower() != title.lower():
        # HOI4 Agent Tools reads the page title from the file name (`_` as a space)
        # and matches it without regard to case; punctuation in a title is lost.
        report("agent_title", name, f"HOI4 Agent Tools would read this file as the page "
               f"{kit_blocks.agent_title(name)!r}, not {title!r}")


def check_h1(name, lines, report):
    """One level-1 heading per page; heading-shaped lines inside a code fence are comments."""
    h1 = 0
    inside = False
    for line in lines:
        if line.lstrip().startswith(FENCE):
            inside = not inside
            continue
        if not inside and re.match(r"^# ", line):
            h1 += 1
    if h1 != 1:
        report("h1_count", name, f"{h1} level-1 headings")


def check_media(directory, files, media_names, report):
    """Media file names, and media that pages reference but lack or that nothing references."""
    for media_name in sorted(media_names):
        if not kit_blocks.MEDIA_FILE.match(media_name):
            report("file_name", "(media)", f"{media_name}: media file names are "
                   "lowercase without spaces")
    referenced = set()
    long_rows = 0
    for name in files:
        text = Path(directory, name).read_text(encoding="utf-8")
        referenced.update(os.path.basename(m)
                          for m in re.findall(r"\]\((media/[^)]+)\)", text))
        long_rows += sum(1 for line in text.split("\n")
                         if line.startswith("|") and len(line) > 400)
    for name in sorted(referenced - media_names)[:20]:
        report("missing_media", "(media)", name)
    for name in sorted(media_names - referenced)[:20]:
        report("orphan_media", "(media)", name)
    return referenced, long_rows


def verify(directory, show_details=True):
    problems = Counter()
    details = []

    def report(kind, page, message):
        problems[kind] += 1
        details.append(f"  [{kind}] {page}: {message}")

    files = sorted(f for f in os.listdir(directory) if f.endswith(".md"))
    # Exact-case names: Windows and macOS would resolve a link with the wrong case.
    names = set(os.listdir(directory))
    media_dir = os.path.join(directory, "media")
    media_names = set(os.listdir(media_dir)) if os.path.isdir(media_dir) else set()

    def exists_exact(relative):
        head, _, tail = relative.partition("/")
        if not tail:
            return head in names
        if head == "media" and "/" not in tail:
            return tail in media_names
        return os.path.exists(os.path.join(directory, relative.replace("/", os.sep)))

    anchors_by_file = {}
    for name in files:
        text = Path(directory, name).read_text(encoding="utf-8")
        anchors_by_file[name] = set(re.findall(r'<a id="([^"]+)"', text))

    for name in files:
        path = os.path.join(directory, name)
        raw = Path(path).read_bytes()
        text = raw.decode("utf-8")
        lines = text.split("\n")

        if raw.startswith(b"\xef\xbb\xbf"):
            report("bom", name, "file starts with a byte order mark")

        check_file_name(name, text, report)

        # --- code fences ---------------------------------------------------
        fences = [i + 1 for i, l in enumerate(lines) if l.strip().startswith(FENCE)]
        if len(fences) % 2:
            report("odd_fences", name, f"unbalanced code fences at {fences[:6]}")
        inside = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(FENCE):
                inside = not inside
                continue
            if inside and stripped.startswith("|") and re.match(
                    r"^\|[\s:|-]+\|$", stripped):
                report("fence_in_table", name, f"line {i + 1}")
            if not inside and stripped.startswith("|") and FENCE in line:
                report("fence_in_table", name,
                       f"line {i + 1}: fenced code inside a table row")
        if inside:
            report("odd_fences", name, "file ends inside a code fence")

        # --- outbound links ------------------------------------------------
        for m in re.finditer(r"(?<!!)\[[^\]]*\]\((https?://[^)]+)\)", text):
            report("external_link", name, m.group(1)[:70])

        # --- internal links ------------------------------------------------
        for i, line in enumerate(lines):
            for m in re.finditer(r"\]\(<([^>]+)>\)", line):
                target = m.group(1)
                page, _, anchor = target.partition("#")
                if not exists_exact(page):
                    report("broken_link", name, f"line {i + 1}: missing file {page}")
                    continue
                if anchor and anchor not in anchors_by_file.get(page, set()):
                    report("broken_anchor", name, f"line {i + 1}: {page}#{anchor}")

        # --- media ---------------------------------------------------------
        for i, line in enumerate(lines):
            for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", line):
                src = m.group(1)
                if src.startswith("http"):
                    report("remote_image", name, f"line {i + 1}: {src[:70]}")
                elif not exists_exact(src):
                    report("missing_media", name, f"line {i + 1}: {src}")

        # --- tables --------------------------------------------------------
        i = 0
        while i < len(lines):
            if (lines[i].strip().startswith("|") and i + 1 < len(lines)
                    and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1])):
                width = columns(lines[i])
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith("|"):
                    if columns(lines[j]) != width:
                        report("ragged_table", name,
                               f"line {j + 1}: {columns(lines[j])} cols vs {width}")
                    longest = max((len(s) for s in lines[j].split("`")[1::2]),
                                  default=0)
                    if longest >= 300:
                        # The signature of a multi-line code sample flattened
                        # into a single span instead of one span per line.
                        report("flat_cell_code", name,
                               f"line {j + 1}: one code span of {longest} chars")
                    for span in lines[j].split("`")[1::2]:
                        if len(span) - len(span.lstrip(" ")) >= 4:
                            # Indented code belongs in a fenced block after the
                            # table; a renderer collapses it inside a cell.
                            report("indented_cell_code", name,
                                   f"line {j + 1}: {span[:50]!r}")
                            break
                    j += 1
                i = j
            else:
                i += 1

        # --- definition lists ----------------------------------------------
        # ":" definition list syntax is not CommonMark, and a four-space
        # indented ":" renders as a code block.
        inside_fence = False
        for i, line in enumerate(lines):
            if line.lstrip().startswith(FENCE):
                inside_fence = not inside_fence
                continue
            if inside_fence or line.lstrip().startswith("|"):
                continue
            if re.match(r"^\s*:", line):
                report("definition_list", name, f"line {i + 1}")

        # --- table of contents ---------------------------------------------
        own = anchors_by_file[name]
        for m in re.finditer(r"^\s*-\s*\[[^\]]*\]\(#([^)]+)\)", text, flags=re.M):
            if m.group(1) not in own:
                report("broken_toc", name, m.group(1))

        check_h1(name, lines, report)
        check_encoding(name, text, report)
        check_kit(name, text, report)
        if "LICENSE.txt" in text and not os.path.exists(
                os.path.join(directory, "LICENSE.txt")):
            report("license", name, "names LICENSE.txt, which is missing")

    referenced, long_rows = check_media(directory, files, media_names, report)

    print(f"pages: {len(files)}   media on disk: {len(media_names)}   "
          f"referenced: {len(referenced)}")
    # A markdown table row is one line by definition, so rows carrying a code
    # example are legitimately long. Reported for visibility, not as a defect.
    print(f"table rows over 400 characters: {long_rows}")
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


def main():
    parser = argparse.ArgumentParser(
        description="Validate the offline Paradox wiki snapshot.")
    parser.add_argument("directory", nargs="?", default=None,
                        help="snapshot directory (default paradox_wiki/)")
    parser.add_argument("--quiet", action="store_true",
                        help="print only the problem summary")
    args = parser.parse_args()

    if args.directory:
        directory = args.directory
    else:
        root = find_repo_root(os.path.dirname(os.path.abspath(__file__)))
        directory = os.path.join(root, "paradox_wiki")
    if not os.path.isdir(directory):
        print(f"not a directory: {directory}")
        return 1
    return verify(directory, show_details=not args.quiet)


if __name__ == "__main__":
    sys.exit(main())
