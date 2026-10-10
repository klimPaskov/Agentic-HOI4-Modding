#!/usr/bin/env python3
"""Check that instruction files, skills, and agent prompts stay readable in one pass.

The ceiling in `read_limits.json` is the largest file an agent can read
completely in a single tool call with a safety margin. It is a ceiling, not a
target: a file below it is left alone. A file above it is split by moving a
complete, coherent topic into `references/<topic>.md` next to the skill and
linking it from the section that needs it. Never shorten requirements to fit.

    python .tools/sync/check_guidance_size.py

Standard library only; runs on Python 3.9 or newer.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
MOD_ROOT = TOOLS_DIR.parents[1]


def main() -> int:
    limits = json.loads((TOOLS_DIR / "read_limits.json").read_text(encoding="utf-8"))
    ceiling = limits["guidance_file_tokens"]
    ratio = limits["estimated_bytes_per_token"]
    skill_limit = limits.get("root_skill_max_bytes", ceiling * ratio)
    over = []
    checked = 0
    for pattern in limits["checked"]:
        for path in sorted(MOD_ROOT.glob(pattern)):
            checked += 1
            size = path.stat().st_size
            limit = skill_limit if path.name == "SKILL.md" else ceiling * ratio
            if size > limit:
                over.append((path.relative_to(MOD_ROOT).as_posix(), size, limit))
    for name, size, limit in over:
        print(f"OVER: {name} is {size:,} bytes (about {size // ratio:,} tokens); the limit is {limit:,} bytes. Move a complete topic into a linked reference file.")
    if not over:
        print(f"{checked} guidance files are within the {ceiling:,}-token single-read ceiling.")
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
