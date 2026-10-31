#!/usr/bin/env python3
"""Check that instruction files, skills, and agent prompts stay readable in one pass.

The ceiling in `read_limits.json` is the largest file an agent can read
completely in a single tool call with a safety margin. It is a ceiling, not a
target: a file below it is left alone. A file above it is split by moving a
complete, coherent topic into `references/<topic>.md` next to the skill and
linking it from the section that needs it. Never shorten requirements to fit.

    python .tools/sync/check_guidance_size.py

Sizes are counted with LF line endings, so a Windows checkout that stores
CRLF measures the same as every other machine.

Exit codes: 0 every file fits, 1 a file is over the ceiling, 2 the limits
cannot be read.

Standard library only; runs on Python 3.9 or newer.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

TOOLS_DIR = Path(__file__).resolve().parent
MOD_ROOT = TOOLS_DIR.parents[1]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check that guidance files stay below the single-read ceiling.")
    parser.add_argument("--root", type=Path, default=MOD_ROOT, help="project root (default: the project holding this tool)")
    root = parser.parse_args(argv).root.resolve()
    limits_path = root / ".tools" / "sync" / "read_limits.json"
    try:
        limits = json.loads((limits_path if limits_path.is_file() else TOOLS_DIR / "read_limits.json").read_text(encoding="utf-8"))
        ceiling = limits["guidance_file_tokens"]
        ratio = limits["estimated_bytes_per_token"]
        patterns = limits["checked"]
    except (OSError, ValueError, KeyError) as error:
        print(f"ERROR: read_limits.json cannot be read: {error}", file=sys.stderr)
        return 2
    skill_limit = limits.get("root_skill_max_bytes", ceiling * ratio)
    over = []
    checked = 0
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            checked += 1
            # Count LF bytes: a Windows checkout with core.autocrlf turns every LF into CRLF, which a model never reads.
            size = len(path.read_bytes().replace(b"\r\n", b"\n"))
            limit = skill_limit if path.name == "SKILL.md" else ceiling * ratio
            if size > limit:
                over.append((path.relative_to(root).as_posix(), size, limit))
    for name, size, limit in over:
        print(f"OVER: {name} is {size:,} bytes (about {size // ratio:,} tokens); the limit is {limit:,} bytes. Move a complete topic into a linked reference file.")
    if not over:
        print(f"{checked} guidance files are within the {ceiling:,}-token single-read ceiling.")
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
