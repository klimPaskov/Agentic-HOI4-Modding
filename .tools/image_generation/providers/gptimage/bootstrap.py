#!/usr/bin/env python3
"""Install the manifest-pinned GPTImage runtime beside its vendored source."""

from __future__ import annotations

import json
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import argparse
from pathlib import Path

TEXT_SOURCE_SUFFIXES = {".js", ".json", ".md", ".py", ".txt"}


def source_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.name == "LICENSE" or path.suffix.lower() in TEXT_SOURCE_SUFFIXES:
        return data.replace(b"\r\n", b"\n")
    return data


def source_tree_sha256(package_root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(
        (
            item
            for item in package_root.rglob("*")
            if item.is_file() and not {"node_modules", "__pycache__"}.intersection(item.parts)
        ),
        key=lambda item: item.relative_to(package_root).as_posix(),
    ):
        relative = path.relative_to(package_root).as_posix()
        data = source_bytes(path)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
    return digest.hexdigest()


def install(package_root: Path, run=subprocess.run, *, expected_tree_sha256: str | None = None,
            expected_lock_sha256: str | None = None) -> dict[str, str]:
    package_root = package_root.resolve(strict=True)
    if expected_tree_sha256 is not None:
        if not re.fullmatch(r"[0-9a-f]{64}", expected_tree_sha256) or source_tree_sha256(package_root) != expected_tree_sha256:
            raise RuntimeError("The selected GPTImage source tree does not match its reviewed pin.")
    if expected_lock_sha256 is not None:
        actual_lock_sha256 = hashlib.sha256(source_bytes(package_root / "package-lock.json")).hexdigest()
        if not re.fullmatch(r"[0-9a-f]{64}", expected_lock_sha256) or actual_lock_sha256 != expected_lock_sha256:
            raise RuntimeError("The selected GPTImage lockfile does not match its reviewed integrity pin.")
    package = json.loads((package_root / "package.json").read_text(encoding="utf-8"))
    if package.get("name") != "gptimage" or package.get("version") != "0.1.0":
        raise RuntimeError("The selected image package does not match the pinned GPTImage source.")
    if not (package_root / "package-lock.json").is_file():
        raise RuntimeError("The GPTImage lockfile is missing.")
    if not (package_root / "src" / "server.js").is_file():
        raise RuntimeError("The GPTImage MCP entry point is missing.")

    npm_cache = tempfile.mkdtemp(prefix="hoi4-imagegen-npm-")
    clean_config = Path(npm_cache) / "empty.npmrc"
    clean_config.write_text("", encoding="utf-8")
    allowed_names = {
        "PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR", "USERPROFILE",
        "HOME", "APPDATA", "LOCALAPPDATA", "LANG", "LC_ALL",
    }
    environment = {name: value for name, value in os.environ.items() if name.upper() in allowed_names}
    environment["CI"] = "true"
    try:
        result = run(
            ["npm", "ci", "--omit=dev", "--ignore-scripts", "--no-bin-links", "--no-audit", "--no-fund", "--cache", npm_cache,
             "--userconfig", str(clean_config), "--globalconfig", str(clean_config)],
            cwd=package_root,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            shutil.rmtree(package_root / "node_modules", ignore_errors=True)
            raise RuntimeError("The pinned GPTImage dependencies could not be installed.")
    except Exception:
        shutil.rmtree(package_root / "node_modules", ignore_errors=True)
        raise
    finally:
        shutil.rmtree(npm_cache, ignore_errors=True)

    installed = package_root / "node_modules" / "@modelcontextprotocol" / "sdk" / "package.json"
    if not installed.is_file():
        raise RuntimeError("GPTImage dependencies are incomplete after installation.")
    return {"status": "ready", "package": package["name"], "version": package["version"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--expected-tree-sha256")
    parser.add_argument("--expected-lock-sha256")
    args = parser.parse_args()
    result = install(args.package_root, expected_tree_sha256=args.expected_tree_sha256, expected_lock_sha256=args.expected_lock_sha256)
    print(json.dumps(result, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        # The app captures this bounded text and filters it before journaling.
        print(json.dumps({"status": "error", "message": str(error)}, separators=(",", ":")))
        raise SystemExit(1)
