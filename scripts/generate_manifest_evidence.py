"""Regenerate setup-manifest evidence from one exact repository commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import unquote


def glob_matches(pattern: str, value: str) -> bool:
    expression = "^"
    index = 0
    while index < len(pattern):
        if pattern.startswith("**", index):
            expression += ".*"
            index += 2
        elif pattern[index] == "*":
            expression += "[^/]*"
            index += 1
        elif pattern[index] == "?":
            expression += "[^/]"
            index += 1
        else:
            expression += re.escape(pattern[index])
            index += 1
    return re.fullmatch(expression[1:], value) is not None


def git_snapshot(source_root: Path, revision: str) -> dict[str, bytes]:
    if re.fullmatch(r"[0-9a-f]{40}", revision) is None:
        raise SystemExit("--revision must be one exact lowercase 40-character commit")
    subprocess.run(
        ["git", "-C", str(source_root), "cat-file", "-e", f"{revision}^{{commit}}"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    tree = subprocess.check_output(
        ["git", "-C", str(source_root), "ls-tree", "-r", "-z", "--full-tree", revision]
    )
    objects: list[tuple[str, str]] = []
    for record in tree.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        _mode, object_type, object_id = metadata.decode("ascii").split(" ", 2)
        if object_type == "blob":
            objects.append((raw_path.decode("utf-8"), object_id))
    process = subprocess.Popen(
        ["git", "-C", str(source_root), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None and process.stdout is not None and process.stderr is not None
    snapshot: dict[str, bytes] = {}
    for path, object_id in objects:
        process.stdin.write(f"{object_id}\n".encode("ascii"))
        process.stdin.flush()
        header = process.stdout.readline().decode("ascii").strip().split(" ")
        if len(header) != 3 or header[1] != "blob":
            raise SystemExit(f"unable to read Git blob for {path}")
        size = int(header[2])
        data = process.stdout.read(size)
        if len(data) != size or process.stdout.read(1) != b"\n":
            raise SystemExit(f"truncated Git blob for {path}")
        snapshot[path] = data
    process.stdin.close()
    return_code = process.wait()
    detail = process.stderr.read().decode("utf-8", errors="replace").strip()
    process.stdout.close()
    process.stderr.close()
    if return_code != 0:
        raise SystemExit(f"git cat-file failed: {detail}")
    return snapshot


def git_evidence_for(component: dict, snapshot: dict[str, bytes]) -> list[dict]:
    source = component["source"]
    if source["kind"] == "generated":
        return []
    prefix = PurePosixPath(source["path"]).as_posix()
    if source["kind"] == "file":
        names = [prefix]
    else:
        names = []
        for name in sorted(snapshot):
            if name != prefix and not name.startswith(f"{prefix}/"):
                continue
            relative = name[len(prefix):].lstrip("/")
            if source.get("include") and not any(
                glob_matches(pattern, relative) for pattern in source["include"]
            ):
                continue
            if any(glob_matches(pattern, relative) for pattern in source.get("exclude", [])):
                continue
            names.append(name)
    missing = [name for name in names if name not in snapshot]
    if missing:
        raise SystemExit(f"declared source file is missing at the selected revision: {missing[0]}")
    return [
        {
            "path": name,
            "sha256": hashlib.sha256(snapshot[name]).hexdigest(),
            "size": len(snapshot[name]),
        }
        for name in names
    ]


def markdown_targets(text: str) -> list[str]:
    return [match.group(1) or match.group(2) for match in re.finditer(r"\]\((?:<([^>]+)>|([^\s)]+))", text)]


def normalize_wiki_target(page: str, raw_target: str) -> str | None:
    target = raw_target.strip()
    if not target or target.startswith("#") or re.match(
        r"^(?:https?|mailto|tel|data):", target, flags=re.IGNORECASE
    ):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0]
    target = re.sub(r"\\([\\`*_{}\[\]()#+\-.!])", r"\1", target).replace("\\", "/")
    target = unquote(target).lstrip("/")
    parts: list[str] = []
    for part in (PurePosixPath(page).parent / target).parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                raise SystemExit(f"offline wiki link escapes its root: {page} -> {raw_target}")
            parts.pop()
        else:
            parts.append(part)
    return PurePosixPath(*parts).as_posix()


def validate_offline_wiki_links(snapshot: dict[str, bytes]) -> None:
    wiki_files = {name for name in snapshot if name.startswith("paradox_wiki/")}
    for page in sorted(name for name in wiki_files if name.lower().endswith(".md")):
        text = snapshot[page].decode("utf-8")
        for raw_target in markdown_targets(text):
            target = normalize_wiki_target(page, raw_target)
            if target is not None and target not in wiki_files:
                raise SystemExit(f"offline wiki link is missing: {page} -> {target}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--legacy-manifest", type=Path)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    snapshot = git_snapshot(args.source_root.resolve(), args.revision)
    validate_offline_wiki_links(snapshot)
    manifest["generated_for_revision"] = args.revision
    for component in manifest["components"]:
        component["expected_files"] = git_evidence_for(component, snapshot)
    args.manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if args.legacy_manifest is not None:
        legacy = json.loads(json.dumps(manifest))
        legacy["schema_version"] = "1.0.0"
        for component in legacy["components"]:
            for validation in component.get("validation", []):
                validation.pop("parameters", None)
        args.legacy_manifest.write_text(
            json.dumps(legacy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
