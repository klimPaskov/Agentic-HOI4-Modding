#!/usr/bin/env python3
"""Regenerate AGENTS.md from the canonical CLAUDE.md.

CLAUDE.md is the single authoring source for project rules. Codex, Cursor,
Qoder, OpenCode, and DeepSeek Harness read AGENTS.md, so this tool writes it as
a projection: the same text with the runtime-specific phrases listed in
`instruction_projection.json` replaced. Edit CLAUDE.md, then run:

    python .tools/sync/sync_instructions.py           # write AGENTS.md
    python .tools/sync/sync_instructions.py --check   # report drift, write nothing

Pairs whose source file is absent are skipped, so the same configuration works
in the source package (templates) and in an installed mod. A replacement may
name the sources it applies to as a third element. A replacement whose phrase
no longer occurs in a source it applies to is reported as UNUSED, because the
generated file would then keep a phrase meant for one runtime only.

Exit codes: 0 in sync, 1 drift or an unused replacement, 2 the configuration
cannot be read.

Standard library only; runs on Python 3.9 or newer.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

TOOLS_DIR = Path(__file__).resolve().parent
MOD_ROOT = TOOLS_DIR.parents[1]
CONFIG_NAME = "instruction_projection.json"

Replacement = Tuple[str, str, Optional[Tuple[str, ...]]]


def project(text: str, replacements: Sequence[Replacement], source: str) -> str:
    for canonical, replacement, sources in replacements:
        if sources is None or source in sources:
            text = text.replace(canonical, replacement)
    return text


def load_config(root: Path) -> Tuple[List[dict], List[Replacement]]:
    path = root / ".tools" / "sync" / CONFIG_NAME
    config = json.loads((path if path.is_file() else TOOLS_DIR / CONFIG_NAME).read_text(encoding="utf-8"))
    replacements: List[Replacement] = []
    for row in config["replacements"]:
        sources = tuple(row[2]) if len(row) > 2 else None
        replacements.append((row[0], row[1], sources))
    return config["pairs"], replacements


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate AGENTS.md from the canonical CLAUDE.md.")
    parser.add_argument("--check", action="store_true", help="report drift without writing; exit 1 when out of sync")
    parser.add_argument("--root", type=Path, default=MOD_ROOT, help="project root (default: the project holding this tool)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        pairs, replacements = load_config(root)
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        print(f"ERROR: {CONFIG_NAME} cannot be read: {error}", file=sys.stderr)
        return 2
    handled = 0
    failures = 0
    for pair in pairs:
        source = root / pair["source"]
        target = root / pair["target"]
        if not source.is_file():
            continue
        handled += 1
        text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
        for canonical, _, sources in replacements:
            if (sources is None or pair["source"] in sources) and canonical not in text:
                print(f"UNUSED: {pair['source']} no longer contains the replacement phrase starting {canonical[:60]!r}; update {CONFIG_NAME}.")
                failures += 1
        expected = project(text, replacements, pair["source"])
        current = target.read_text(encoding="utf-8").replace("\r\n", "\n") if target.is_file() else None
        if current == expected:
            print(f"{pair['target']}: in sync with {pair['source']}.")
            continue
        if args.check:
            print(f"DRIFT: {pair['target']} differs from the projection of {pair['source']}.")
            failures += 1
            continue
        with target.open("w", encoding="utf-8", newline="") as handle:
            handle.write(expected)
        print(f"{pair['target']}: regenerated from {pair['source']}.")
    if not handled:
        print("No canonical instruction file (CLAUDE.md) was found; nothing to project.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
