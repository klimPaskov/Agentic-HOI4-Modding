#!/usr/bin/env python3
"""Install and verify the exact public HOI4 Agent Tools MCP package for this user."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


PACKAGE_NAME = "hoi4-agent-tools"
PACKAGE_VERSION = "4.0.3"
PACKAGE_SPEC = f"{PACKAGE_NAME}@{PACKAGE_VERSION}"
# Reviewed npm registry integrity and clean published installation evidence.
PACKAGE_INTEGRITY = "sha512-pgiQYcQiWsba78IOK1DzOb7feEl0ktpiZg3LdyxSMcklA7HV+Zofo3hdR5BOp9YWlWHubrTkl6AMtBgDhqnUmQ=="
PACKAGE_TREE_SHA256 = "b93b47b341e6bc33a0822d631e187af7e3c29eec48196ccd10c89f957729dc35"
PACKAGE_FILE_COUNT = 5387
LINUX_PACKAGE_TREE_SHA256 = "c2f7344ff1ee5ab4ba1c99299cdab2fbf01c1b56bf87d866810dfdafc9d30d41"
LINUX_PACKAGE_FILE_COUNT = 5253
LINUX_PACKAGE_SYMLINKS = {
    "node_modules/.bin/node-which": "../which/bin/node-which",
    "node_modules/.bin/semver": "../semver/bin/semver.js",
}
RUNTIME_ENTRY = "dist/bin/stdio.js"
RUNTIME_ENTRY_SHA256 = "e503ef634bcd473b5a7225f6752ff7d99c9897cb2126dac3eb2c4cc55859f24e"
RUNTIME_ENTRY_SIZE = 4205
REGISTRY = "https://registry.npmjs.org"
MAX_OUTPUT_BYTES = 2 * 1024 * 1024
MAX_PACKAGE_FILE_BYTES = 32 * 1024 * 1024
MAX_PACKAGE_TREE_BYTES = 512 * 1024 * 1024
MAX_PACKAGE_FILES = 10000
MAX_PACKAGE_ARCHIVE_BYTES = 512 * 1024 * 1024


class BootstrapError(RuntimeError):
    pass


def platform_name() -> str:
    if os.name == "nt":
        return "windows"
    if sys.platform.startswith("linux"):
        return "linux"
    raise BootstrapError("The reviewed bootstrap supports native Windows and Linux.")


def platform_evidence(platform: str | None = None) -> dict:
    platform = platform or platform_name()
    if platform not in {"windows", "linux"}:
        raise BootstrapError("The MCP platform has no reviewed package evidence.")
    return {
        "package_tree_sha256": PACKAGE_TREE_SHA256 if platform == "windows" else LINUX_PACKAGE_TREE_SHA256,
        "package_file_count": PACKAGE_FILE_COUNT if platform == "windows" else LINUX_PACKAGE_FILE_COUNT,
        "runtime_entry_sha256": RUNTIME_ENTRY_SHA256,
        "runtime_entry_size": RUNTIME_ENTRY_SIZE,
        "package_symlinks": {} if platform == "windows" else dict(LINUX_PACKAGE_SYMLINKS),
    }


def modules_directory(prefix: Path) -> Path:
    modules = prefix / ("lib/node_modules" if platform_name() == "linux" else "node_modules")
    for path in (modules, *modules.parents):
        if path == prefix.parent:
            break
        if path.is_symlink():
            raise BootstrapError("The MCP installation directory contains a link.")
    return modules


def run(arguments: list[str], timeout: int = 900) -> str:
    if not arguments or any("\x00" in argument for argument in arguments):
        raise BootstrapError("The reviewed MCP command arguments are invalid.")
    try:
        result = subprocess.run(
            arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            shell=False,
            env=os.environ.copy(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BootstrapError("A reviewed MCP setup command could not complete.") from exc
    output = result.stdout[: MAX_OUTPUT_BYTES + 1]
    diagnostics = result.stderr[: MAX_OUTPUT_BYTES + 1]
    if len(output) > MAX_OUTPUT_BYTES or len(diagnostics) > MAX_OUTPUT_BYTES:
        raise BootstrapError("A reviewed MCP setup command exceeded its output limit.")
    # npm writes warnings and notices to stderr; keep them out of the JSON
    # results read from stdout, but use them to explain failures.
    text = output.decode("utf-8", errors="replace")
    if result.returncode != 0:
        text = text + "\n" + diagnostics.decode("utf-8", errors="replace")
        if "EBUSY" in text and ".dll" in text.lower():
            raise BootstrapError(
                "npm could not replace loaded MCP native libraries. "
                "Close or reconnect existing HOI4 MCP clients, then rerun the exact-package installer."
            )
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
    if platform_name() == "linux":
        node_value = shutil.which("node")
        npm_value = shutil.which("npm")
        if node_value and npm_value:
            node = Path(node_value).resolve(strict=True)
            npm_path = Path(npm_value).resolve(strict=True)
            if node.is_file() and npm_path.is_file() and node.suffix != ".exe" and npm_path.suffix != ".cmd":
                version = run([str(node), "--version"]).strip()
                try:
                    major = int(version.removeprefix("v").split(".")[0])
                except ValueError as exc:
                    raise BootstrapError("Node.js returned invalid version evidence.") from exc
                if major < 22:
                    raise BootstrapError("Install a native supported Node.js LTS release (22 or newer) and npm before continuing.")
                return node, npm_path
        raise BootstrapError("Install native Node.js LTS and npm; imported Windows executables are not Linux dependencies.")
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
        if platform_name() == "linux":
            raise
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
    if platform_name() == "linux" and npm_cmd.name == "npm-cli.js":
        npm_cli = npm_cmd
    if not npm_cli.is_file():
        if platform_name() == "linux":
            raise BootstrapError("The native npm JavaScript entry could not be discovered.")
        # npm.cmd is a fixed wrapper installed beside the authenticated Node
        # distribution. It is used only when that distribution does not expose
        # npm-cli.js at its standard location.
        return run([str(npm_cmd), *arguments], timeout=timeout)
    return run([str(node), str(npm_cli), *arguments], timeout=timeout)


def user_prefix() -> Path:
    if platform_name() == "linux":
        xdg = os.environ.get("XDG_DATA_HOME", "").strip()
        if xdg:
            if "\x00" in xdg or len(xdg) > 4096 or not Path(xdg).is_absolute():
                raise BootstrapError("XDG_DATA_HOME must be a bounded absolute directory.")
            root = Path(xdg).resolve()
        else:
            root = (Path.home() / ".local/share").resolve()
        prefix = (root / "hoi4-mod-setup/npm").resolve()
        try:
            prefix.relative_to(root)
        except ValueError as exc:
            raise BootstrapError("The current-user npm prefix escaped application-data storage.") from exc
        return prefix
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


def verify_local_tarball(path: Path) -> Path:
    """Verify an explicitly selected local archive; never discover a fallback."""
    try:
        archive = path.resolve(strict=True)
        if not archive.is_file() or archive.stat().st_size > MAX_PACKAGE_ARCHIVE_BYTES:
            raise BootstrapError("The selected local MCP archive is missing or oversized.")
        digest = hashlib.sha512()
        total_bytes = 0
        with archive.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > MAX_PACKAGE_ARCHIVE_BYTES:
                    raise BootstrapError("The selected local MCP archive is oversized.")
                digest.update(chunk)
    except OSError as exc:
        raise BootstrapError("The selected local MCP archive could not be read.") from exc
    integrity = "sha512-" + base64.b64encode(digest.digest()).decode("ascii")
    if integrity != PACKAGE_INTEGRITY:
        raise BootstrapError("The selected local MCP archive integrity does not match the reviewed release.")
    return archive


def install_package(node: Path, npm_cmd: Path, prefix: Path, local_tarball: Path | None = None) -> None:
    package_source = PACKAGE_SPEC if local_tarball is None else str(verify_local_tarball(local_tarball))
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
            package_source,
        ],
        timeout=1800,
    )


def read_json(path: Path, maximum: int) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > maximum:
        raise BootstrapError("Installed MCP package evidence is missing or oversized.")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BootstrapError("Installed MCP package evidence is malformed.") from exc
    if not isinstance(value, dict):
        raise BootstrapError("Installed MCP package evidence is not an object.")
    return value


def package_tree_sha256(package_root: Path, allowed_symlinks: dict[str, str] | None = None) -> tuple[str, int]:
    allowed_symlinks = platform_evidence()["package_symlinks"] if allowed_symlinks is None else allowed_symlinks
    if package_root.is_symlink():
        raise BootstrapError("The installed MCP package root contains a link.")
    files: list[tuple[str, bytes]] = []
    seen_symlinks = set()
    total_bytes = 0
    for path in package_root.rglob("*"):
        if len(files) >= MAX_PACKAGE_FILES:
            raise BootstrapError("The installed MCP package exceeds its file-count bound.")
        if path.is_symlink():
            relative = path.relative_to(package_root).as_posix()
            target = os.readlink(path)
            if allowed_symlinks.get(relative) != target:
                raise BootstrapError("The installed MCP package contains an unreviewed link.")
            destination = path.parent / target
            try:
                destination.resolve(strict=True).relative_to(package_root.resolve(strict=True))
            except (OSError, ValueError) as exc:
                raise BootstrapError("The installed MCP package link escapes its tree.") from exc
            for part in (destination, *destination.parents):
                if part == package_root.parent:
                    break
                if part.is_symlink():
                    raise BootstrapError("The installed MCP package link target contains a link.")
            if not destination.is_file():
                raise BootstrapError("The installed MCP package link target is not a regular file.")
            seen_symlinks.add(relative)
            files.append((relative, b"symlink\0" + target.encode("utf-8")))
            continue
        if not path.is_file():
            continue
        relative = path.relative_to(package_root).as_posix()
        data = path.read_bytes()
        total_bytes += len(data)
        if len(data) > MAX_PACKAGE_FILE_BYTES or total_bytes > MAX_PACKAGE_TREE_BYTES:
            raise BootstrapError("The installed MCP package contains an oversized file.")
        files.append((relative, data))
    if seen_symlinks != set(allowed_symlinks):
        raise BootstrapError("The installed MCP package is missing a reviewed link.")
    digest = hashlib.sha256()
    for relative, data in sorted(files):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
    return digest.hexdigest(), len(files)


def verify_installation(prefix: Path) -> Path:
    modules = modules_directory(prefix)
    package_root = modules / PACKAGE_NAME
    package = read_json(package_root / "package.json", 1024 * 1024)
    if package.get("name") != PACKAGE_NAME or package.get("version") != PACKAGE_VERSION:
        raise BootstrapError("The installed MCP package name or version is incorrect.")
    lock_path = modules / ".package-lock.json"
    if lock_path.exists():
        lock = read_json(lock_path, 16 * 1024 * 1024)
        packages = lock.get("packages")
        installed = packages.get(f"node_modules/{PACKAGE_NAME}") if isinstance(packages, dict) else None
        if not isinstance(installed, dict) or installed.get("integrity") != PACKAGE_INTEGRITY:
            raise BootstrapError("The installed MCP package does not retain the reviewed integrity.")
    tree_digest, file_count = package_tree_sha256(package_root)
    evidence = platform_evidence()
    if tree_digest != evidence["package_tree_sha256"] or file_count != evidence["package_file_count"]:
        raise BootstrapError("The installed MCP package tree does not match the reviewed release.")
    entry = package_root / RUNTIME_ENTRY
    if not entry.is_file() or entry.stat().st_size != RUNTIME_ENTRY_SIZE:
        raise BootstrapError("The installed MCP runtime entry has the wrong size.")
    digest = hashlib.sha256(entry.read_bytes()).hexdigest()
    if digest != RUNTIME_ENTRY_SHA256:
        raise BootstrapError("The installed MCP runtime entry has the wrong SHA-256.")
    wrapper = prefix / ("bin/hoi4-agent-tools" if platform_name() == "linux" else "hoi4-agent-tools.cmd")
    if not wrapper.is_file():
        raise BootstrapError("The installed MCP command wrapper is missing.")
    if platform_name() == "linux":
        if not wrapper.is_symlink() or os.readlink(wrapper) != f"../lib/node_modules/{PACKAGE_NAME}/{RUNTIME_ENTRY}" or wrapper.resolve() != entry.resolve():
            raise BootstrapError("The installed native MCP locator does not point to its reviewed entry.")
    return wrapper


def installed_package_matches(prefix: Path) -> bool:
    try:
        verify_installation(prefix)
    except (BootstrapError, OSError, ValueError):
        return False
    return True


def remove_mismatched_package(node: Path, npm_cmd: Path, prefix: Path) -> None:
    """Remove an installed package that is not the reviewed release.

    npm upgrades a package that ships a shrinkwrap in place without pruning
    modules the previous release needed, so the upgraded tree keeps stale files
    and never matches the reviewed tree identity. A clean reinstall does.
    """
    package_root = modules_directory(prefix) / PACKAGE_NAME
    if not package_root.exists():
        return
    npm(
        node,
        npm_cmd,
        [
            "uninstall",
            "--global",
            "--prefix",
            str(prefix),
            "--ignore-scripts",
            "--no-audit",
            "--no-fund",
            PACKAGE_NAME,
        ],
    )
    if package_root.exists():
        raise BootstrapError(
            "The previous HOI4 Agent Tools installation could not be removed. "
            "Close or reconnect existing HOI4 MCP clients, then rerun the exact-package installer."
        )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--local-tarball", type=Path, help="Explicitly install the exact reviewed local archive without a registry integrity query.")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    platform_name()
    node, npm_cmd = ensure_node()
    prefix = user_prefix()
    if arguments.local_tarball is None:
        verify_registry_integrity(node, npm_cmd)
    else:
        verify_local_tarball(arguments.local_tarball)
    if not installed_package_matches(prefix):
        remove_mismatched_package(node, npm_cmd, prefix)
        install_package(node, npm_cmd, prefix, arguments.local_tarball)
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
