#!/usr/bin/env python
"""Rebuild the hoi4_wiki/ pages from the kit sidecars, without fetching the wiki.

Edit kit text in ``.tools/wiki/kit/<page>.md``, never in ``hoi4_wiki/``, then run:

    python -B .tools/wiki/render_wiki.py                 # rebuild every page
    python -B .tools/wiki/render_wiki.py ai_focuses      # only these pages (title, stem or file)
    python -B .tools/wiki/render_wiki.py --check         # exit 1 when a page is out of date

For a wiki page the tool takes the page's wiki text back out of ``hoi4_wiki/`` (the
lines ``manifest.json`` says the kit blocks fill are removed, and the rest must match
the recorded hash), puts the lean text of every kit block back at its ``at`` place,
and records where each block landed. A kit page is its sidecar's lean text under its
title. ``hoi4_wiki/SOURCES.json`` and ``manifest.json`` are rewritten to match.

A hand edit to wiki text in ``hoi4_wiki/`` makes the hash check fail: move the change
into a kit block, or refresh the page with ``sync_wiki_snapshot.py``. See README.md.

Standard library only; Python 3.9 or newer.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kit_blocks  # the page format, next to this script
import lean  # annotated kit text -> lean text


class RenderError(ValueError):
    """A page that cannot be rebuilt from its sidecar."""


def block_texts(sidecar: str) -> List[Tuple[str, str, str]]:
    """(id, at, lean text) of every kit block of a wiki page's sidecar, review block left out."""
    return [(b.id, b.at, lean.lean_text(b.text)) for b in kit_blocks.find_blocks(sidecar)
            if b.id != kit_blocks.REVIEW_ID]


def render_kit_page(sidecar: str) -> str:
    title = kit_blocks.page_title(sidecar)
    if not title:
        raise RenderError("kit page sidecar has no title")
    body = lean.lean_text(kit_blocks.kit_page_body(sidecar)).strip("\n")
    return f"# {title}\n\n{body}\n"


def render_wiki_page(base: str, sidecar: str) -> kit_blocks.Placed:
    """Kit text placed into a wiki page's wiki text; raises RenderError if it cannot be taken back out."""
    placed = kit_blocks.assemble(base, block_texts(sidecar))
    if kit_blocks.disassemble(placed.text, placed.spans) != base:
        raise RenderError("the page cannot be split back into wiki text and kit blocks "
                          "(a block next to a doubled blank line?)")
    return placed


def wiki_text(page: str, entry: Dict[str, object]) -> str:
    """The wiki text of a page in hoi4_wiki/, checked against the hash in the manifest."""
    spans = entry.get("blocks", {})
    assert isinstance(spans, dict)
    base = kit_blocks.disassemble(page, spans)
    if kit_blocks.sha256(base) != entry.get("base_sha256"):
        raise RenderError("its wiki text differs from the recorded text: a kit block was edited in "
                          "hoi4_wiki/ instead of in its sidecar, or the wiki text was edited by hand")
    return base


def sidecar_for(name: str) -> Path:
    return kit_blocks.SIDECAR_DIR / name


def rebuild_page(name: str, entry: Dict[str, object], wiki_dir: Path) -> Tuple[str, List[str]]:
    """The page as its sidecar says it should read, and the ids of orphaned blocks."""
    path = sidecar_for(name)
    if not path.exists():
        raise RenderError(f"no sidecar {path.relative_to(kit_blocks.REPO).as_posix()}")
    sidecar = path.read_text(encoding="utf-8")
    if entry["source"] == "kit":
        if not kit_blocks.is_kit_page(sidecar):
            raise RenderError("the manifest says kit page but the sidecar has no kit:page marker")
        return render_kit_page(sidecar), []
    page_path = wiki_dir / name
    if not page_path.exists():
        raise RenderError("the page file is missing; refresh it with sync_wiki_snapshot.py")
    base = wiki_text(page_path.read_text(encoding="utf-8"), entry)
    placed = render_wiki_page(base, sidecar)
    entry["blocks"] = placed.spans
    return placed.text, placed.orphans


def new_kit_pages(manifest: Dict[str, object]) -> List[str]:
    """Sidecars of kit pages the manifest does not list yet; adds an entry for each."""
    pages = manifest.setdefault("pages", {})
    assert isinstance(pages, dict)
    added = []
    for path in sorted(kit_blocks.SIDECAR_DIR.glob("*.md")):
        if path.name in pages:
            continue
        sidecar = path.read_text(encoding="utf-8")
        title = kit_blocks.page_title(sidecar) or path.stem
        if not kit_blocks.is_kit_page(sidecar):
            raise RenderError(f"{path.name}: a wiki page's sidecar with no manifest entry; "
                              f"import the page with sync_wiki_snapshot.py --only \"{title}\"")
        pages[path.name] = {"title": title, "source": "kit"}
        added.append(path.name)
    return added


def select(manifest: Dict[str, object], wanted: Optional[List[str]]) -> List[str]:
    pages = manifest.get("pages", {})
    assert isinstance(pages, dict)
    if not wanted:
        return sorted(pages)
    chosen = []
    for item in wanted:
        keys = {item, item + ".md", kit_blocks.file_name(item)}
        match = next((name for name in pages if name in keys), None)
        if match is None:
            raise SystemExit(f"no page named {item!r} in the manifest")
        chosen.append(match)
    return chosen


def rebuild(names: Optional[List[str]] = None, write: bool = True,
            wiki_dir: Optional[Path] = None, manifest_path: Optional[Path] = None) -> Dict[str, List[str]]:
    """Rebuild pages, the manifest and SOURCES.json; return what changed and what failed.

    With ``write=False`` nothing is written; the report says which files would change.
    `wiki_dir` and `manifest_path` default to ``hoi4_wiki/`` and ``manifest.json``.
    """
    wiki_dir = kit_blocks.WIKI_DIR if wiki_dir is None else wiki_dir
    manifest_path = kit_blocks.MANIFEST if manifest_path is None else manifest_path
    manifest = kit_blocks.load_manifest(manifest_path)
    report: Dict[str, List[str]] = {"changed": [], "failed": [], "orphans": []}
    report["changed"] += new_kit_pages(manifest)
    pages = manifest["pages"]
    assert isinstance(pages, dict)
    for name in select(manifest, names):
        try:
            text, orphans = rebuild_page(name, pages[name], wiki_dir)
        except (RenderError, kit_blocks.KitBlockError) as error:
            report["failed"].append(f"{name}: {error}")
            continue
        report["orphans"] += [f"{name}: {block_id}" for block_id in orphans]
        path = wiki_dir / name
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            report["changed"].append(name)
            if write:
                kit_blocks.write_text(path, text)
    outputs = [(manifest_path, kit_blocks.dump_json(manifest)),
               (wiki_dir / kit_blocks.SOURCES_NAME, kit_blocks.dump_json(kit_blocks.sources_document(manifest)))]
    for path, text in outputs:
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            report["changed"].append(path.name)
            if write and not report["failed"]:
                kit_blocks.write_text(path, text)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild hoi4_wiki/ pages from the kit sidecars.")
    parser.add_argument("pages", nargs="*", help="page titles, file stems or file names (default: all)")
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 when a file would change")
    args = parser.parse_args()
    report = rebuild(args.pages or None, write=not args.check)
    for line in report["failed"]:
        print(f"failed: {line}")
    for line in report["orphans"]:
        print(f"kit block whose heading is gone (kept at the bottom): {line}")
    verb = "out of date" if args.check else "written"
    for name in report["changed"]:
        print(f"{verb}: {name}")
    if report["failed"] or report["orphans"] or (args.check and report["changed"]):
        return 1
    if not report["changed"]:
        print("every page matches its sidecar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
