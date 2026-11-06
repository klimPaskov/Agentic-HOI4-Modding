#!/usr/bin/env python3
"""Check that instruction files, skills, and agent prompts stay readable in one pass and within the context budget.

Two kinds of limit live in `read_limits.json`.

1. The single-read ceiling (`guidance_file_tokens`, `root_skill_max_bytes`) is the
   largest file an agent can read completely in one tool call with a safety
   margin. It applies to every project, including an installed mod. It is a
   ceiling, not a target: a file above it is split by moving a complete,
   coherent topic into `references/<topic>.md` next to the skill and linking it
   from the section that needs it. Never shorten requirements to fit.
2. The context budget (`context_budget`) keeps what an agent loads before it
   starts working small enough for a mid-tier model: the instruction template
   (loaded in every session), each skill's `SKILL.md` (loaded when the skill
   triggers) and each skill description (listed in every session). It is
   enforced in the kit's source package, recognised by a `CLAUDE_template.md`
   at the project root, so an installed mod keeps its own instructions and
   skills under the single-read ceiling only. `--strict` forces it anywhere.
   Details of a skill belong in `references/`, which an agent opens on demand,
   so every reference must be linked from its `SKILL.md` or from a reference
   that is, or an agent reading only the skill would never learn it exists.

    python .tools/sync/check_guidance_size.py

Sizes are counted with LF line endings, so a Windows checkout that stores
CRLF measures the same as every other machine. A token is estimated as
`bytes_per_token` bytes (4), the conventional ratio. On the kit's guidance the
o200k tokenizer measured 4.3 to 5.1 bytes per token (2026-11-06), so the
estimate leaves headroom for tokenizers that split this text more finely.

Exit codes: 0 every file fits, 1 a file is over its limit, 2 the limits
cannot be read.

Standard library only; runs on Python 3.9 or newer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TOOLS_DIR = Path(__file__).resolve().parent
MOD_ROOT = TOOLS_DIR.parents[1]
TEMPLATES = ("CLAUDE_template.md", "AGENTS_template.md")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
DESCRIPTION = re.compile(r"^description:[ \t]*(.*)$", re.M)
SENTENCE_BREAK = re.compile(r"[.!?][\"')\]`]*\s+[A-Z`\"(]")
MD_LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)\s]*)?\)")
REFERENCE_MENTION = re.compile(r"references/([A-Za-z0-9_./-]+\.md)")
URL_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


@dataclass
class Limits:
    ceiling_tokens: int
    bytes_per_token: int
    patterns: List[str]
    skill_limit: int
    budget: Optional[Dict[str, int]]

    @property
    def single_read_bytes(self) -> int:
        return self.ceiling_tokens * self.bytes_per_token


def load_limits(root: Path) -> Limits:
    path = root / ".tools" / "sync" / "read_limits.json"
    data: Dict[str, Any] = json.loads((path if path.is_file() else TOOLS_DIR / "read_limits.json").read_text(encoding="utf-8"))
    ceiling, ratio = data["guidance_file_tokens"], data["estimated_bytes_per_token"]
    raw = data.get("context_budget")
    budget = {key: int(raw[key]) for key in ("bytes_per_token", "template_tokens", "skill_tokens", "description_max_chars")} if raw else None
    return Limits(ceiling, ratio, data["checked"], data.get("root_skill_max_bytes", ceiling * ratio), budget)


def read_text(path: Path) -> str:
    # Count LF bytes: a Windows checkout with core.autocrlf turns every LF into CRLF, which a model never reads.
    return path.read_bytes().replace(b"\r\n", b"\n").decode("utf-8", errors="replace")


def skill_description(text: str) -> Tuple[Optional[str], bool]:
    """Return the one-line description and whether it is a quoted YAML scalar."""
    match = FRONTMATTER.match(text)
    found = DESCRIPTION.search(match.group(1)) if match else None
    if not found:
        return None, False
    value = found.group(1).strip()
    quoted = len(value) > 1 and value[0] in "\"'" and value[-1] == value[0]
    return (value[1:-1] if quoted else value), quoted


def description_problem(name: str, text: str, max_chars: int) -> Optional[str]:
    """One line describing what is wrong with a skill description, or None when it fits the budget."""
    description, quoted = skill_description(text)
    if not description:
        return f"DESCRIPTION: {name} has no one-line description in its frontmatter."
    if len(description) > max_chars:
        return f"DESCRIPTION: {name} description is {len(description)} characters; the limit is {max_chars}. Keep one sentence and move the rest into the skill body."
    if SENTENCE_BREAK.search(description):
        return f"DESCRIPTION: {name} description is more than one sentence. Keep one sentence and move the rest into the skill body."
    if not quoted and (": " in description or " #" in description):
        return f"DESCRIPTION: {name} description holds a colon followed by a space or a space and #, which plain YAML cannot hold, so a runtime may skip the skill. Reword it or quote it."
    return None


def unreachable_references(skill: Path) -> List[Path]:
    """Reference files of one skill that neither SKILL.md nor a reference it reaches links to or names."""
    start = skill / "SKILL.md"
    reached = {start.resolve()}
    todo = [start]
    while todo:
        current = todo.pop()
        text = re.sub(r"```.*?```", "", read_text(current), flags=re.S)
        targets = [(current.parent / target).resolve() for target in MD_LINK.findall(text) if not URL_SCHEME.match(target)]
        targets += [(skill / "references" / name).resolve() for name in REFERENCE_MENTION.findall(text)]
        for target in targets:
            if target.suffix == ".md" and target not in reached and target.is_file() and skill.resolve() in target.parents:
                reached.add(target)
                todo.append(target)
    references = skill / "references"
    return [path for path in sorted(references.rglob("*.md")) if path.resolve() not in reached] if references.is_dir() else []


def file_limit(limits: Limits, name: str, strict: bool) -> Tuple[int, str]:
    """The byte limit for one guidance file and what it is called in a message."""
    budget = limits.budget
    if strict and budget and name in TEMPLATES:
        return budget["template_tokens"] * budget["bytes_per_token"], f"the {budget['template_tokens']:,}-token template budget"
    if strict and budget and name == "SKILL.md":
        return budget["skill_tokens"] * budget["bytes_per_token"], f"the {budget['skill_tokens']:,}-token skill budget"
    return (limits.skill_limit if name == "SKILL.md" else limits.single_read_bytes), "the single-read ceiling"


def check_file(root: Path, path: Path, limits: Limits, strict: bool) -> List[str]:
    """The problem lines for one guidance file."""
    text = read_text(path)
    size = len(text.encode("utf-8"))
    name = path.relative_to(root).as_posix()
    limit, kind = file_limit(limits, path.name, strict)
    found: List[str] = []
    if size > limit:
        per_token = limits.budget["bytes_per_token"] if strict and limits.budget else limits.bytes_per_token
        found.append(f"OVER: {name} is {size:,} bytes (about {size // per_token:,} tokens); the limit is {limit:,} bytes ({kind}). Move a complete topic into a linked reference file.")
    if strict and limits.budget and path.name == "SKILL.md":
        problem = description_problem(name, text, limits.budget["description_max_chars"])
        if problem:
            found.append(problem)
    return found


def scan(root: Path, limits: Limits, strict: bool) -> Tuple[List[str], int]:
    """Return every problem line and how many files were checked."""
    problems: List[str] = []
    checked = 0
    for pattern in limits.patterns:
        for path in sorted(root.glob(pattern)):
            checked += 1
            problems += check_file(root, path, limits, strict)
    if strict:
        for skill in sorted(path for path in (root / ".claude" / "skills").glob("*") if (path / "SKILL.md").is_file()):
            for path in unreachable_references(skill):
                problems.append(f"UNREACHABLE: {path.relative_to(root).as_posix()} is not linked from {skill.name}/SKILL.md or from a reference it reaches, so an agent that reads only the skill never learns it exists. Add it to the reference map.")
    return problems, checked


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check that guidance files stay below the single-read ceiling and the context budget.")
    parser.add_argument("--root", type=Path, default=MOD_ROOT, help="project root (default: the project holding this tool)")
    parser.add_argument("--strict", action="store_true", help="enforce the context budget even without a CLAUDE_template.md at the root")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        limits = load_limits(root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: read_limits.json cannot be read: {error}", file=sys.stderr)
        return 2
    strict = bool(limits.budget) and (args.strict or (root / TEMPLATES[0]).is_file())
    problems, checked = scan(root, limits, strict)
    for line in problems:
        print(line)
    if problems:
        return 1
    suffix = ""
    if strict and limits.budget:
        suffix = f" and the context budget ({limits.budget['template_tokens']:,}-token template, {limits.budget['skill_tokens']:,}-token skills, {limits.budget['description_max_chars']}-character descriptions)"
    print(f"{checked} guidance files are within the {limits.ceiling_tokens:,}-token single-read ceiling{suffix}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
