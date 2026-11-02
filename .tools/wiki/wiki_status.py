#!/usr/bin/env python
"""Report how current the offline wiki snapshot is against the installed game.

Every snapshot page carries a review block whose marker records the game build the
page was checked against (``build``), the date (``checked``), the wiki revision that
was reviewed (``revision``) and the game files it was checked against (``sources``,
space-separated paths or folder prefixes under the game folder). See
``kit_blocks.py`` for the format.

``game_docs_index.json`` next to this script records the game's own documentation
for the build the snapshot was last checked against: every heading of
``documentation/*.md`` and of the ``_documentation.md`` files under ``common/``,
with a short hash of its text. When a new game build changes those files, this tool
lists the entries that were added, removed or changed and the pages to re-check.
The index also records the installed Steam depot manifests (``steam_depots.py``), so
after an update the tool can list every game file that changed and flag the pages
whose ``sources`` name one, not only the pages that cite documentation.

    python -B .tools/wiki/wiki_status.py                      # status and documentation diff
    python -B .tools/wiki/wiki_status.py --strict             # exit 1 unless every page is current
    python -B .tools/wiki/wiki_status.py --mark-reviewed Effects "Raid modding"
    python -B .tools/wiki/wiki_status.py --carry-forward      # after a build change, see README
    python -B .tools/wiki/wiki_status.py --record             # store the installed build's index

A page is current when its review names the installed build and the wiki revision on
its capture line. The tool reads the installed game (``HOI4_GAME_DIR``,
``.tools/local_settings.json`` or the Steam libraries) and never launches it. Only
``--mark-reviewed``, ``--carry-forward`` and ``--record`` write anything.
Standard library only; Python 3.9 or newer.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import kit_blocks  # the page format, next to this script
import steam_depots  # the game files that changed between two Steam builds
from lib import game  # .tools/lib: locates the installed game

REPO = HERE.parents[1]
WIKI_DIR = REPO / "hoi4_wiki"
INDEX = HERE / "game_docs_index.json"
DOC_GLOBS = ("documentation/*.md", "common/**/*documentation*.md",
             "interface/**/_documentation.info", "gfx/**/_documentation.info")
SKIP_HEADING = re.compile(r"^(table of contents?|.+ for scope .+)$", re.I)
NAME = re.compile(r"^[a-z][a-z0-9_]*$")
WORD = re.compile(r"[A-Za-z0-9_]+")


# --- the installed game's documentation ----------------------------------

def installed_build(game_dir: Path) -> Dict[str, str]:
    settings = json.loads((game_dir / "launcher-settings.json").read_text(encoding="utf-8"))
    return {"build": settings.get("rawVersion", "unknown"), "version": settings.get("version", "")}


def doc_files(game_dir: Path) -> List[str]:
    found: Set[str] = set()
    for pattern in DOC_GLOBS:
        found.update(p.relative_to(game_dir).as_posix() for p in game_dir.glob(pattern) if p.is_file())
    return sorted(found)


def short_hash(text: str) -> str:
    lines = [line.rstrip() for line in text.strip().split("\n")]
    normalised = re.sub(r"\n{2,}", "\n", "\n".join(lines))
    return hashlib.sha1(normalised.encode("utf-8")).hexdigest()[:8]


def index_document(text: str) -> Dict[str, str]:
    """Map each heading (as an h2 / h3 path) to a hash of its own text."""
    entries: Dict[str, str] = {}
    parent, key, body, inside = "", None, [], False
    for line in text.replace("\r\n", "\n").split("\n") + ["## "]:
        if line.lstrip().startswith("```"):
            inside = not inside
        match = None if inside else re.match(r"^(#{2,3})\s+(.*)$", line)
        if not match:
            body.append(line)
            continue
        if key is not None:
            # A heading can repeat (template families); number the repeats.
            unique, n = key, 2
            while unique in entries:
                unique, n = f"{key} ({n})", n + 1
            entries[unique] = short_hash("\n".join(body))
        title = re.sub(r"[`*]|<span[^>]*></span>", "", match.group(2)).strip().rstrip(":")
        body = []
        top = len(match.group(1)) == 2
        if top:
            parent = title
        # Tables of contents and "X for scope Y" lists only repeat entry names.
        key = None if not title or (top and SKIP_HEADING.match(title)) else (
            title if top else f"{parent} / {title}")
    return entries


def build_index(game_dir: Path) -> Dict[str, object]:
    files = {}
    for relative in doc_files(game_dir):
        text = (game_dir / relative).read_text(encoding="utf-8", errors="replace")
        files[relative] = {"sha1": hashlib.sha1(text.encode("utf-8")).hexdigest(),
                           "entries": index_document(text)}
    index: Dict[str, object] = {**installed_build(game_dir), "recorded": datetime.date.today().isoformat(),
                                "files": files}
    depots = steam_depots.installed_depots(game_dir)
    if depots:
        index["depots"] = depots
    return index


def diff_index(old: Dict[str, object], new: Dict[str, object]) -> Dict[str, Dict[str, List[str]]]:
    """Per documentation file: entries added, removed and changed between two indexes."""
    old_files, new_files = old.get("files", {}), new.get("files", {})
    result = {}
    for path in sorted(set(old_files) | set(new_files)):
        before = old_files.get(path, {"sha1": None, "entries": {}})
        after = new_files.get(path, {"sha1": None, "entries": {}})
        if before["sha1"] == after["sha1"]:
            continue
        a, b = before["entries"], after["entries"]
        result[path] = {"added": sorted(set(b) - set(a)), "removed": sorted(set(a) - set(b)),
                        "changed": sorted(k for k in set(a) & set(b) if a[k] != b[k]),
                        "file": ["added"] if before["sha1"] is None else ["removed"] if after["sha1"] is None else []}
    return result


# --- the snapshot pages ---------------------------------------------------

def load_pages() -> Dict[str, str]:
    """Page title -> text. The title is the page's level-1 heading, not its file name."""
    pages: Dict[str, str] = {}
    for path in sorted(WIKI_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        pages[kit_blocks.page_title(text) or path.stem] = text
    return pages


def page_sources(text: str) -> List[str]:
    review = kit_blocks.review(text) or {}
    return review.get("sources", "").split()


def covers(sources: Iterable[str], doc: str) -> bool:
    return any(doc == s or (s.endswith("/") and doc.startswith(s)) for s in sources)


def entry_name(key: str) -> Optional[str]:
    """The script token an entry documents, when it is distinctive enough to search for."""
    name = key.split(" / ")[-1].strip()
    return name if NAME.match(name) and ("_" in name or len(name) >= 8) else None


def affected_pages(diff: Dict[str, Dict[str, List[str]]], pages: Dict[str, str]) -> Dict[str, List[str]]:
    """Page title -> reasons it should be re-checked after a documentation change."""
    words = {title: set(WORD.findall(text)) for title, text in pages.items()}
    sources = {title: page_sources(text) for title, text in pages.items()}
    reasons: Dict[str, List[str]] = {}
    for doc, change in diff.items():
        for title in pages:
            if covers(sources[title], doc):
                reasons.setdefault(title, []).append(f"source {doc} changed")
        for kind in ("removed", "changed"):
            for key in change[kind]:
                name = entry_name(key)
                for title in pages:
                    if name and name in words[title] and not covers(sources[title], doc):
                        reasons.setdefault(title, []).append(f"mentions {kind} entry {name} ({doc})")
    return reasons


def is_documentation(path: str) -> bool:
    return path.startswith("documentation/") or "_documentation." in path


def game_file_changes(game_dir: Path, recorded: Dict[str, object]) -> Dict[str, str]:
    """Game files the Steam depot manifests show as changed since the recorded build (empty when unknown)."""
    old = recorded.get("depots")
    if not isinstance(old, dict) or not old:
        print("game files: the recorded index has no Steam depot ids, so changed script and define files "
              "cannot be listed; check the pages' sources by hand (see README)")
        return {}
    new = steam_depots.installed_depots(game_dir)
    if not new:
        print("game files: no Steam app manifest next to the game folder, so changed files cannot be listed")
        return {}
    changes, notes = steam_depots.changed_files(old, new, steam_depots.depot_caches(game_dir, game.steam_roots()))
    for note in notes:
        print(f"game files: {note}")
    counts = {kind: sum(1 for k in changes.values() if k == kind) for kind in ("added", "removed", "changed")}
    print("game files changed since the recorded build: " + ", ".join(f"{n} {k}" for k, n in counts.items()))
    folders: Dict[str, int] = {}
    for path in changes:
        folder = "/".join(path.split("/")[:2]) if "/" in path else path
        folders[folder] = folders.get(folder, 0) + 1
    for folder, count in sorted(folders.items(), key=lambda item: (-item[1], item[0]))[:15]:
        print(f"  {folder}: {count}")
    return changes


def file_reasons(changes: Dict[str, str], pages: Dict[str, str]) -> Dict[str, List[str]]:
    """Page title -> reasons to re-check: sources (other than documentation) that cover changed game files."""
    scripts = [path for path in changes if not is_documentation(path)]
    reasons: Dict[str, List[str]] = {}
    for title, text in pages.items():
        for source in page_sources(text):
            count = sum(1 for path in scripts if covers([source], path))
            if count:
                reasons.setdefault(title, []).append(f"source {source}: {count} game file(s) changed")
    return reasons


def page_state(text: str, build: str) -> str:
    review = kit_blocks.review(text) or {}
    if review.get("build", "none") == "none":
        return "not reviewed"
    if review.get("build") != build:
        return "reviewed on an older build"
    revision = kit_blocks.capture_revision(text)
    if revision is not None and review.get("revision") != str(revision):
        return "wiki text changed since the review"
    return "current"


# --- writing review markers ----------------------------------------------

def set_review(text: str, updates: Dict[str, str]) -> str:
    blocks = kit_blocks.find_blocks(text)
    block = next((b for b in blocks if b.id == kit_blocks.REVIEW_ID), None)
    if block is None:
        raise SystemExit("page has no review block; run the sync or add one")
    attrs = {**block.attrs, **updates}
    attrs = {k: v for k, v in attrs.items() if v != ""}
    order = ["id", "at", "build", "checked", "revision", "via", "sources"]
    keys = [k for k in order if k in attrs] + sorted(k for k in attrs if k not in order)
    marker = "<!-- kit:begin " + "".join(f'{k}="{attrs[k]}" ' for k in keys) + "-->"
    first_line_end = text.index("\n", block.start)
    return text[:block.start] + marker + text[first_line_end:]


def write_lf(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def page_path(name: str) -> Path:
    """The page file for a title (``Effects``), a file stem (``effects``) or a file name."""
    wanted = {name.lower(), kit_blocks.file_name(name)}
    for path in sorted(WIKI_DIR.glob("*.md")):
        title = kit_blocks.page_title(path.read_text(encoding="utf-8")) or path.stem
        if path.name in wanted or title.lower() == name.lower():
            return path
    raise SystemExit(f"no snapshot page named {name!r}")


def mark_reviewed(names: List[str], build: str, via: str = "") -> None:
    today = datetime.date.today().isoformat()
    for name in names:
        path = page_path(name)
        text = path.read_text(encoding="utf-8")
        revision = kit_blocks.capture_revision(text)
        updates = {"build": build, "checked": today, "via": via,
                   "revision": "" if revision is None else str(revision)}
        write_lf(path, set_review(text, updates))
        print(f"review recorded: {path.name} ({build})")


# --- reporting ------------------------------------------------------------

def print_diff(diff: Dict[str, Dict[str, List[str]]], limit: int = 12) -> None:
    for doc, change in diff.items():
        state = change["file"][0] if change["file"] else "changed"
        counts = ", ".join(f"{len(change[k])} {k}" for k in ("added", "removed", "changed") if change[k])
        print(f"  {doc}: {state}{' (' + counts + ')' if counts else ''}")
        for kind in ("added", "removed", "changed"):
            if change[kind]:
                shown = ", ".join(change[kind][:limit])
                more = f" and {len(change[kind]) - limit} more" if len(change[kind]) > limit else ""
                print(f"      {kind}: {shown}{more}")


def print_status(pages: Dict[str, str], build: str, docs: List[str]) -> int:
    groups: Dict[str, List[str]] = {}
    for title, text in pages.items():
        groups.setdefault(page_state(text, build), []).append(title)
    kit = sum(1 for text in pages.values() if kit_blocks.is_kit_page(text))
    print(f"\npages: {len(pages)} ({len(pages) - kit} from the wiki, {kit} kit pages)")
    for state in ("current", "wiki text changed since the review", "reviewed on an older build", "not reviewed"):
        titles = groups.get(state, [])
        listing = "" if state == "current" or not titles else ": " + ", ".join(titles)
        print(f"  {state}: {len(titles)}{listing}")
    all_sources = [s for text in pages.values() for s in page_sources(text)]
    uncovered = [d for d in docs if not covers(all_sources, d)]
    if uncovered:
        print(f"\ngame documentation files no page names as a source ({len(uncovered)}):")
        for doc in uncovered:
            print(f"  {doc}")
    return len(pages) - len(groups.get("current", []))


def report(game_dir: Path, pages: Dict[str, str]) -> Dict[str, List[str]]:
    current = build_index(game_dir)
    print(f"installed game: {current['build']} ({current['version']})")
    if not INDEX.exists():
        print("no recorded documentation index yet; run with --record once the pages are checked")
        return {}
    recorded = json.loads(INDEX.read_text(encoding="utf-8"))
    diff = diff_index(recorded, current)
    if diff:
        print(f"documentation changed between the recorded index ({recorded['build']}) and the installed game:")
        print_diff(diff)
    else:
        print(f"documentation index: {recorded['build']} recorded {recorded['recorded']}, "
              "matches the installed files")
    reasons = affected_pages(diff, pages)
    if recorded.get("build") != current["build"]:
        for title, why in file_reasons(game_file_changes(game_dir, recorded), pages).items():
            reasons.setdefault(title, []).extend(why)
    if not reasons:
        return {}
    print(f"\npages to re-check ({len(reasons)}):")
    for title in sorted(reasons):
        print(f"  {title}: " + "; ".join(dict.fromkeys(reasons[title])))
    return reasons


def carry_forward(game_dir: Path, pages: Dict[str, str], reasons: Dict[str, List[str]]) -> None:
    """Move pages the documentation diff does not touch to the installed build."""
    if not INDEX.exists():
        raise SystemExit("--carry-forward needs a recorded index from the previous build")
    old_build = json.loads(INDEX.read_text(encoding="utf-8"))["build"]
    build = installed_build(game_dir)["build"]
    if build == old_build:
        raise SystemExit("the installed build is the recorded one; nothing to carry forward")
    names = [t for t, text in pages.items()
             if t not in reasons and (kit_blocks.review(text) or {}).get("build") == old_build]
    mark_reviewed(names, build, via="docs-diff")


def main() -> int:
    parser = argparse.ArgumentParser(description="Report how current the wiki snapshot is.")
    parser.add_argument("--mark-reviewed", nargs="+", metavar="PAGE",
                        help="record that these pages were checked against the installed build")
    parser.add_argument("--carry-forward", action="store_true",
                        help="move pages the documentation diff does not touch to the installed build")
    parser.add_argument("--record", action="store_true",
                        help="store the installed build's documentation index")
    parser.add_argument("--strict", action="store_true", help="exit 1 unless every page is current")
    args = parser.parse_args()
    missing = game.require_game_dir()
    if missing is not None:
        return missing
    game_dir = game.game_dir()
    if args.mark_reviewed:
        mark_reviewed(args.mark_reviewed, installed_build(game_dir)["build"])
        return 0
    pages = load_pages()
    reasons = report(game_dir, pages)
    if args.carry_forward:
        carry_forward(game_dir, pages, reasons)
        pages = load_pages()
    if args.record:
        write_lf(INDEX, json.dumps(build_index(game_dir), indent=1, sort_keys=True) + "\n")
        print(f"recorded {INDEX.name} for {installed_build(game_dir)['build']}")
    stale = print_status(pages, installed_build(game_dir)["build"], doc_files(game_dir))
    return 1 if args.strict and stale else 0


if __name__ == "__main__":
    sys.exit(main())
