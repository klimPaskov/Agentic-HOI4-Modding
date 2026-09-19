#!/usr/bin/env python
"""Validate the offline Paradox wiki snapshot. Read-only; never writes.

This is the acceptance check for ``.tools/wiki/sync_wiki_snapshot.py``. It exits
non-zero when the snapshot is not self-contained and readable, and reports:

* unbalanced code fences and fenced blocks that would break a table row;
* outbound hyperlinks, which the snapshot must not contain;
* links to missing snapshot files, and section links whose anchor is absent;
* images with no file on disk, or image files nothing references;
* table rows whose column count differs from their header;
* pages that do not have exactly one level-1 heading;
* encoding damage: byte order marks, escaped punctuation, non-breaking and
  zero-width characters, and mojibake.

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

FENCE = "`" * 3
PIPE = re.compile(r"(?<!\\)\|")


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


def verify(directory, show_details=True):
    problems = Counter()
    details = []

    def report(kind, page, message):
        problems[kind] += 1
        details.append(f"  [{kind}] {page}: {message}")

    files = sorted(f for f in os.listdir(directory) if f.endswith(".md"))
    anchors_by_file = {}
    for name in files:
        text = open(os.path.join(directory, name), encoding="utf-8").read()
        anchors_by_file[name] = set(re.findall(r'<a id="([^"]+)"', text))

    for name in files:
        path = os.path.join(directory, name)
        raw = open(path, "rb").read()
        text = raw.decode("utf-8")
        lines = text.split("\n")

        if raw.startswith(b"\xef\xbb\xbf"):
            report("bom", name, "file starts with a byte order mark")

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
                if not os.path.exists(os.path.join(directory, page)):
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
                elif not os.path.exists(os.path.join(directory,
                                                     src.replace("/", os.sep))):
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
                    j += 1
                i = j
            else:
                i += 1

        # --- table of contents ---------------------------------------------
        own = anchors_by_file[name]
        for m in re.finditer(r"^\s*-\s*\[[^\]]*\]\(#([^)]+)\)", text, flags=re.M):
            if m.group(1) not in own:
                report("broken_toc", name, m.group(1))

        # --- one level-1 heading per page ----------------------------------
        h1 = sum(1 for l in lines if re.match(r"^# ", l))
        if h1 != 1:
            report("h1_count", name, f"{h1} level-1 headings")

        # --- encoding artefacts --------------------------------------------
        for pat, kind in ((r"\\[_*\[\]<>]", "escape_artifact"),
                          ("\u00a0", "nbsp"), ("\u200b", "zwsp"),
                          ("\u2011", "nb_hyphen"),
                          ("[\u0080-\u009f]", "control_char")):
            hits = re.findall(pat, text)
            if hits:
                report(kind, name, f"{len(hits)} occurrence(s)")

        for bad in ("\u00e2\u20ac", "\u00c3\u00a9", "\u00d0\u0178",
                    "\u00ef\u00bb\u00bf", "\u00c2 "):
            if bad in text:
                report("mojibake", name, bad)

    # --- media coverage ----------------------------------------------------
    media_dir = os.path.join(directory, "media")
    referenced = set()
    for name in files:
        text = open(os.path.join(directory, name), encoding="utf-8").read()
        referenced.update(os.path.basename(m)
                          for m in re.findall(r"\]\((media/[^)]+)\)", text))
    on_disk = set(os.listdir(media_dir)) if os.path.isdir(media_dir) else set()
    orphans = sorted(on_disk - referenced)
    missing = sorted(referenced - on_disk)
    if missing:
        for name in missing[:20]:
            report("missing_media", "(media)", name)
    if orphans:
        for name in orphans[:20]:
            report("orphan_media", "(media)", name)

    print(f"pages: {len(files)}   media on disk: {len(on_disk)}   "
          f"referenced: {len(referenced)}")
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
