#!/usr/bin/env python3
"""Install and verify the exact public HOI4 Agent Tools MCP package on Windows."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


PACKAGE_NAME = "hoi4-agent-tools"
PACKAGE_VERSION = "2.5.2"
PACKAGE_SPEC = f"{PACKAGE_NAME}@{PACKAGE_VERSION}"
PACKAGE_INTEGRITY = "sha512-/2CmEDqkEbRsA9CcgnV0KKF8pHWOaATsAlIZexo/2D9BMbIYfYHdimAa5ZMSQiXahCGvCBA1Pq2a9ANZnp8Waw=="
PACKAGE_TREE_SHA256 = "9da372df1c7870728f80e850c1c7fd6b5470285f27e1ef8e0841fcde60e0a208"
PACKAGE_FILE_COUNT = 181
RUNTIME_ENTRY = "dist/bin/stdio.js"
RUNTIME_ENTRY_SHA256 = "7ddc78a8c518957dea6e737663c2be5e8852795d6662fc607166f15f4fb719a8"
RUNTIME_ENTRY_SIZE = 1916
REGISTRY = "https://registry.npmjs.org"
MAX_OUTPUT_BYTES = 2 * 1024 * 1024


class BootstrapError(RuntimeError):
    pass


def run(arguments: list[str], timeout: int = 900) -> str:
    if not arguments or any("\x00" in argument for argument in arguments):
        raise BootstrapError("The reviewed MCP command arguments are invalid.")
    try:
        result = subprocess.run(
            arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
            shell=False,
            env=os.environ.copy(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BootstrapError("A reviewed MCP setup command could not complete.") from exc
    output = result.stdout[: MAX_OUTPUT_BYTES + 1]
    if len(output) > MAX_OUTPUT_BYTES:
        raise BootstrapError("A reviewed MCP setup command exceeded its output limit.")
    text = output.decode("utf-8", errors="replace")
    if result.returncode != 0:
        raise BootstrapError(f"A reviewed MCP setup command failed with exit code {result.returncode}.")
    return text


def candidate_node_roots() -> list[Path]:
    candidates: list[Path] = []
    located = shutil.which("node.exe") or shutil.which("node")
    if located:
        candidates.append(Path(located).resolve().parent)
    for variable, relative in [
        ("ProgramFiles", "nodejs"),
        ("LOCALAPPDATA", "Programs/nodejs"),
    ]:
        value = os.environ.get(variable, "").strip()
        if value:
            candidates.append((Path(value) / relative).resolve())
    unique: list[Path] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    return unique


def resolve_node_and_npm() -> tuple[Path, Path]:
    for root in candidate_node_roots():
        node = root / "node.exe"
        npm = root / "npm.cmd"
        if node.is_file() and npm.is_file():
            return node, npm
    raise BootstrapError("Node.js LTS and npm could not be discovered after installation.")


def ensure_node() -> tuple[Path, Path]:
    try:
        return resolve_node_and_npm()
    except BootstrapError:
        winget = shutil.which("winget.exe") or shutil.which("winget")
        if not winget:
            raise BootstrapError("winget is unavailable, so Node.js LTS could not be installed automatically.")
        run(
            [
                str(Path(winget).resolve()),
                "install",
                "OpenJS.NodeJS.LTS",
                "--scope",
                "user",
                "--silent",
                "--disable-interactivity",
                "--accept-source-agreements",
                "--accept-package-agreements",
            ],
            timeout=1800,
        )
        return resolve_node_and_npm()


def npm(node: Path, npm_cmd: Path, arguments: list[str], timeout: int = 900) -> str:
    npm_cli = node.parent / "node_modules" / "npm" / "bin" / "npm-cli.js"
    if not npm_cli.is_file():
        # npm.cmd is a fixed wrapper installed beside the authenticated Node
        # distribution. It is used only when that distribution does not expose
        # npm-cli.js at its standard location.
        return run([str(npm_cmd), *arguments], timeout=timeout)
    return run([str(node), str(npm_cli), *arguments], timeout=timeout)


def user_prefix() -> Path:
    appdata = os.environ.get("APPDATA", "").strip()
    if not appdata or "\x00" in appdata or len(appdata) > 4096:
        raise BootstrapError("The current-user application-data directory is unavailable.")
    root = Path(appdata).resolve()
    prefix = (root / "npm").resolve()
    try:
        prefix.relative_to(root)
    except ValueError as exc:
        raise BootstrapError("The current-user npm prefix escaped application-data storage.") from exc
    return prefix


def verify_registry_integrity(node: Path, npm_cmd: Path) -> None:
    output = npm(
        node,
        npm_cmd,
        ["view", PACKAGE_SPEC, "dist.integrity", "--json", f"--registry={REGISTRY}"],
    )
    try:
        integrity = json.loads(output)
    except json.JSONDecodeError as exc:
        raise BootstrapError("npm returned invalid package-integrity evidence.") from exc
    if integrity != PACKAGE_INTEGRITY:
        raise BootstrapError("The npm registry package integrity does not match the reviewed release.")


def install_package(node: Path, npm_cmd: Path, prefix: Path) -> None:
    npm(
        node,
        npm_cmd,
        [
            "install",
            "--global",
            "--prefix",
            str(prefix),
            "--ignore-scripts",
            "--no-audit",
            "--no-fund",
            f"--registry={REGISTRY}",
            PACKAGE_SPEC,
        ],
        timeout=1800,
    )


def read_json(path: Path, maximum: int) -> dict:
    if not path.is_file() or path.stat().st_size > maximum:
        raise BootstrapError("Installed MCP package evidence is missing or oversized.")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BootstrapError("Installed MCP package evidence is malformed.") from exc
    if not isinstance(value, dict):
        raise BootstrapError("Installed MCP package evidence is not an object.")
    return value


def package_tree_sha256(package_root: Path) -> tuple[str, int]:
    files: list[tuple[str, bytes]] = []
    total_bytes = 0
    for path in package_root.rglob("*"):
        if path.is_symlink():
            raise BootstrapError("The installed MCP package contains a link.")
        if not path.is_file():
            continue
        relative = path.relative_to(package_root).as_posix()
        data = path.read_bytes()
        total_bytes += len(data)
        if len(data) > 16 * 1024 * 1024 or total_bytes > 256 * 1024 * 1024:
            raise BootstrapError("The installed MCP package contains an oversized file.")
        files.append((relative, data))
    digest = hashlib.sha256()
    for relative, data in sorted(files):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
    return digest.hexdigest(), len(files)


def verify_installation(prefix: Path) -> Path:
    modules = prefix / "node_modules"
    package_root = modules / PACKAGE_NAME
    package = read_json(package_root / "package.json", 1024 * 1024)
    if package.get("name") != PACKAGE_NAME or package.get("version") != PACKAGE_VERSION:
        raise BootstrapError("The installed MCP package name or version is incorrect.")
    lock = read_json(modules / ".package-lock.json", 16 * 1024 * 1024)
    packages = lock.get("packages")
    installed = packages.get(f"node_modules/{PACKAGE_NAME}") if isinstance(packages, dict) else None
    if not isinstance(installed, dict) or installed.get("integrity") != PACKAGE_INTEGRITY:
        raise BootstrapError("The installed MCP package does not retain the reviewed integrity.")
    tree_digest, file_count = package_tree_sha256(package_root)
    if tree_digest != PACKAGE_TREE_SHA256 or file_count != PACKAGE_FILE_COUNT:
        raise BootstrapError("The installed MCP package tree does not match the reviewed release.")
    entry = package_root / RUNTIME_ENTRY
    if not entry.is_file() or entry.stat().st_size != RUNTIME_ENTRY_SIZE:
        raise BootstrapError("The installed MCP runtime entry has the wrong size.")
    digest = hashlib.sha256(entry.read_bytes()).hexdigest()
    if digest != RUNTIME_ENTRY_SHA256:
        raise BootstrapError("The installed MCP runtime entry has the wrong SHA-256.")
    wrapper = prefix / "hoi4-agent-tools.cmd"
    if not wrapper.is_file():
        raise BootstrapError("The installed MCP command wrapper is missing.")
    return wrapper


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    if os.name != "nt":
        raise BootstrapError("The published HOI4 Agent Tools bootstrap route is Windows-only.")
    node, npm_cmd = ensure_node()
    prefix = user_prefix()
    verify_registry_integrity(node, npm_cmd)
    install_package(node, npm_cmd, prefix)
    wrapper = verify_installation(prefix)
    if not arguments.quiet:
        print(f"Installed {PACKAGE_SPEC} at {wrapper.parent}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BootstrapError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
