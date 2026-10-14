#!/usr/bin/env python3
"""Install and verify the exact public HOI4 Agent Tools MCP package for this user."""

from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unicodedata
import urllib.error
import urllib.request


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
MAX_PACKAGE_ENTRIES = 20000
MAX_PACKAGE_DEPTH = 64
MAX_PACKAGE_ARCHIVE_BYTES = 512 * 1024 * 1024
NPM_TOOLCHAINS = {
    "windows": ("11.19.0", "sha512-SDd/hHg3KqHE5Ht2NHWxNYNtqCQ2pXAPLl6OtQhPyED5PHsRfrOtO199MZTIG2cQoQ1ZRI9t28shrD+2cr3AAw=="),
    "linux": ("10.9.9", "sha512-1g+6jLQvaIuB4zwvHL7yrXuXcWZwDsCtBX8bbWDqbvJSSr9nPiDDWTHNgwXR27iIcTTW7v3A57hDW9RYv2W4Yg=="),
}
MAX_NPM_ARCHIVE_BYTES = 8 * 1024 * 1024
MAX_NPM_TAR_BYTES = 32 * 1024 * 1024
MAX_NPM_FILES = 4096
MAX_NPM_FILE_BYTES = 1024 * 1024


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


def minimal_environment() -> dict:
    keep = {"PATH", "PATHEXT", "SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "COMSPEC", "PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMDATA", "ALLUSERSPROFILE", "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP"}
    return {key: value for key, value in os.environ.items() if key.upper() in keep}


def run(arguments: list[str], timeout: int = 900, *, environment: dict | None = None, cwd: Path | None = None) -> str:
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
            env=minimal_environment() if environment is None else environment,
            cwd=cwd,
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


def supported_node_version(version: str) -> bool:
    match = re.fullmatch(r"v(22|24)\.(\d+)\.(\d+)", version.strip())
    return bool(match and (match[1] == "24" or int(match[2]) >= 19))


def verify_node_runtime(node: Path) -> None:
    if not supported_node_version(run([str(node), "--version"]).strip()):
        raise BootstrapError("HOI4 Agent Tools requires Node.js 22.19+ in major 22, or Node.js 24 LTS.")
    if run([str(node), "-p", "process.arch"]).strip() != "x64":
        raise BootstrapError("The reviewed HOI4 Agent Tools runtime requires native x64 Node.js.")


def resolve_node_and_npm() -> tuple[Path, Path]:
    if platform_name() == "linux":
        node_value = shutil.which("node")
        npm_value = shutil.which("npm")
        if node_value and npm_value:
            node = Path(node_value).resolve(strict=True)
            npm_path = Path(npm_value).resolve(strict=True)
            if node.is_file() and npm_path.is_file() and node.suffix != ".exe" and npm_path.suffix != ".cmd":
                verify_node_runtime(node)
                return node, npm_path
        raise BootstrapError("Install native Node.js LTS and npm; imported Windows executables are not Linux dependencies.")
    for root in candidate_node_roots():
        node = root / "node.exe"
        npm = root / "npm.cmd"
        if node.is_file() and npm.is_file():
            try:
                verify_node_runtime(node)
            except BootstrapError:
                continue
            return node, npm
    raise BootstrapError("Install native x64 Node.js 22.19+ in major 22, or Node.js 24 LTS, then retry.")


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


class PinnedNpm:
    def __init__(self, root: Path, entry: Path, environment: dict) -> None:
        self.root = root
        self.entry = entry
        self.environment = environment


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        raise BootstrapError("The pinned npm archive must not redirect.")


def download_npm_archive(version: str, integrity: str) -> bytes:
    url = f"{REGISTRY}/npm/-/npm-{version}.tgz"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(url, timeout=60) as response:
            if response.status != 200 or response.url != url:
                raise BootstrapError("The pinned npm archive response is invalid.")
            data = response.read(MAX_NPM_ARCHIVE_BYTES + 1)
    except (OSError, urllib.error.URLError) as exc:
        raise BootstrapError("The verified npm toolchain could not be downloaded. Retry the setup.") from exc
    if len(data) > MAX_NPM_ARCHIVE_BYTES:
        raise BootstrapError("The pinned npm archive exceeds its size bound.")
    actual = "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode("ascii")
    if actual != integrity:
        raise BootstrapError("The pinned npm archive integrity does not match.")
    return data


def extract_npm_archive(data: bytes, destination: Path, version: str) -> Path:
    if destination.exists() or len(data) > MAX_NPM_ARCHIVE_BYTES:
        raise BootstrapError("The npm extraction destination or archive is invalid.")
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as compressed:
            expanded = compressed.read(MAX_NPM_TAR_BYTES + 1)
        if len(expanded) > MAX_NPM_TAR_BYTES or len(expanded) > max(1, len(data)) * 200:
            raise BootstrapError("The npm archive expansion exceeds its bound.")
        with tarfile.open(fileobj=io.BytesIO(expanded), mode="r:") as archive:
            members = archive.getmembers()
            if len(members) > MAX_NPM_FILES:
                raise BootstrapError("The npm archive has too many entries.")
            seen = set()
            total = 0
            for member in members:
                path = PurePosixPath(member.name)
                parts = member.name.split("/")
                if not member.isfile() or member.linkname or path.is_absolute() or parts[0] != "package" or len(parts) < 2 or len(parts) > 32:
                    raise BootstrapError("The npm archive contains an unreviewed entry.")
                if len(member.name.encode("utf-8")) > 1024 or any(
                    part in {"", ".", ".."} or part.casefold() == ".git" or ":" in part or "\\" in part
                    or any(ord(char) < 32 for char in part) or len(part.encode("utf-8")) > 255
                    or part.rstrip(" .") != part or re.match(r"^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)", part, re.I)
                    for part in parts
                ):
                    raise BootstrapError("The npm archive contains an unsafe path.")
                key = unicodedata.normalize("NFC", member.name).casefold()
                if key in seen:
                    raise BootstrapError("The npm archive contains duplicate paths.")
                seen.add(key)
                total += member.size
                if not 0 <= member.size <= MAX_NPM_FILE_BYTES or total > MAX_NPM_TAR_BYTES:
                    raise BootstrapError("The npm archive file sizes exceed their bounds.")
            destination.mkdir(mode=0o700)
            for member in members:
                target = destination.joinpath(*PurePosixPath(member.name).parts)
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                source = archive.extractfile(member)
                if source is None:
                    raise BootstrapError("The npm archive member is unreadable.")
                with source, target.open("xb") as output:
                    content = source.read(member.size + 1)
                    if len(content) != member.size:
                        raise BootstrapError("The npm archive member is truncated.")
                    output.write(content)
                target.chmod(0o600)
        metadata = read_json(destination / "package/package.json", MAX_NPM_FILE_BYTES)
        if metadata.get("name") != "npm" or metadata.get("version") != version:
            raise BootstrapError("The private npm package identity is incorrect.")
        entry = destination / "package/bin/npm-cli.js"
        if not entry.is_file() or entry.is_symlink():
            raise BootstrapError("The private npm entry is missing.")
        return entry
    except (OSError, EOFError, tarfile.TarError, ValueError) as exc:
        raise BootstrapError("The private npm archive could not be safely extracted.") from exc


@contextmanager
def pinned_npm_runtime():
    version, integrity = NPM_TOOLCHAINS[platform_name()]
    with tempfile.TemporaryDirectory(prefix="hoi4-setup-npm-") as temporary:
        root = Path(temporary).resolve(strict=True)
        entry = extract_npm_archive(download_npm_archive(version, integrity), root / "runtime", version)
        environment = minimal_environment()
        for name in ("home", "config", "data", "cache", "tmp"):
            (root / name).mkdir(mode=0o700)
        for name in ("user.npmrc", "global.npmrc"):
            (root / name).write_bytes(b"")
        environment.update({
            "HOME": str(root / "home"), "USERPROFILE": str(root / "home"),
            "APPDATA": str(root / "config"), "LOCALAPPDATA": str(root / "data"),
            "TEMP": str(root / "tmp"), "TMP": str(root / "tmp"),
            "NPM_CONFIG_USERCONFIG": str(root / "user.npmrc"),
            "NPM_CONFIG_GLOBALCONFIG": str(root / "global.npmrc"),
            "NPM_CONFIG_CACHE": str(root / "cache"), "CI": "true",
        })
        yield PinnedNpm(root, entry, environment)


def npm(node: Path, runtime: PinnedNpm, arguments: list[str], timeout: int = 900) -> str:
    if not isinstance(runtime, PinnedNpm):
        raise BootstrapError("Only the verified private npm toolchain may run.")
    return run([
        str(node), str(runtime.entry),
        f"--userconfig={runtime.root / 'user.npmrc'}",
        f"--globalconfig={runtime.root / 'global.npmrc'}",
        f"--cache={runtime.root / 'cache'}", f"--registry={REGISTRY}", *arguments,
    ], timeout=timeout, environment=runtime.environment, cwd=runtime.root)


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
    entries = 0
    for path in package_root.rglob("*"):
        entries += 1
        metadata = path.lstat()
        if entries > MAX_PACKAGE_ENTRIES or len(path.relative_to(package_root).parts) > MAX_PACKAGE_DEPTH:
            raise BootstrapError("The installed MCP package exceeds its directory bounds.")
        if getattr(metadata, "st_file_attributes", 0) & 0x400:
            raise BootstrapError("The installed MCP package contains a Windows reparse point.")
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
        if metadata.st_size > MAX_PACKAGE_FILE_BYTES or total_bytes + metadata.st_size > MAX_PACKAGE_TREE_BYTES:
            raise BootstrapError("The installed MCP package contains an oversized file.")
        with path.open("rb") as source:
            data = source.read(min(MAX_PACKAGE_FILE_BYTES, MAX_PACKAGE_TREE_BYTES - total_bytes) + 1)
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
    node, _ = ensure_node()
    prefix = user_prefix()
    with pinned_npm_runtime() as npm_cmd:
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
