"""Read-only release inventory, generic-content, and local documentation link checks."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

import generate_manifest_evidence as generator

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    manifest = json.loads((ROOT / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8-sig"))
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    snapshot = {name: (ROOT / name).read_bytes() for name in names if name and (ROOT / name).is_file()}
    covered = {entry["path"] for component in manifest["components"]
               for entry in generator.git_evidence_for(component, snapshot)}
    canonical = {name for name in snapshot if name.startswith((".claude/skills/", ".claude/agents/"))}
    missing = canonical - covered
    assert not missing, f"Canonical files missing from manifest: {sorted(missing)}"
    for name, raw in snapshot.items():
        if not name.endswith((".md", ".json", ".toml", ".yml", ".yaml", ".py", ".cmd", ".html")):
            continue
        text = raw.decode("utf-8-sig")
        assert "hoi4-" + "state-ledgers" not in text, name
        if not name.startswith("scripts/test_"):
            usernames = re.findall(r"[A-Za-z]:[/\\]Users[/\\]([^/\\`\n]+)", text)
            examples = {"username", "<Username>", "<you>", "\u041f\u0440\u0438\u043c\u0435\u0440 \u043a\u0438\u0440\u0438\u043b\u043b\u0438\u0446\u044b"}
            assert all(value in examples for value in usernames), f"Personal path: {name}"
        if name.startswith(".claude/skills/"):
            assert not re.search(r"Chaos Redux|chaos_redux|chaosx", text, re.I), f"Mod-specific skill: {name}"
    docs = [ROOT / "README.md", ROOT / "RELEASING.md", *sorted((ROOT / "docs").rglob("*.md")),
            ROOT / ".tools/sync/README.md", *sorted((ROOT / ".claude").rglob("*.md"))]
    checked = 0
    for page in docs:
        text = page.read_text(encoding="utf-8")
        # Code examples can contain placeholder paths that are not real links.
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for target in generator.markdown_targets(text):
            if target.startswith("#") or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            assert (page.parent / target).exists(), f"Missing link: {page.relative_to(ROOT)} -> {target}"
            checked += 1
    print(f"Release inventory covers {len(canonical)} canonical files; {checked} local documentation links pass.")


if __name__ == "__main__":
    main()
