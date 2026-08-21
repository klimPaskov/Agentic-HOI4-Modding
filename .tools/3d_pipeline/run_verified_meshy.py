"""Launch the exact reviewed Meshy MCP runtime without trusting project records."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


MESHY_PACKAGE = "@meshy-ai/meshy-mcp-server"
MESHY_VERSION = "0.4.0"
MESHY_TREE_SHA256 = "720075e2b1e266208f435b08d8ab81609f5e5e1a247ca4680c51b5a4f00f2011"
MESHY_TREE_FILE_COUNT = 3916
MESHY_TREE_MAX_FILES = 5000
MESHY_TREE_MAX_BYTES = 64 * 1024 * 1024
MESHY_FILE_MAX_BYTES = 16 * 1024 * 1024
NODE_MAX_BYTES = 128 * 1024 * 1024
FILE_ATTRIBUTE_REPARSE_POINT = 0x400


class LaunchError(RuntimeError):
    """Raised before any unverified process receives the Meshy credential."""


def _is_reparse(stat_result: os.stat_result) -> bool:
    return bool(getattr(stat_result, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT)


def _regular_file_bytes(path: Path, max_bytes: int) -> bytes:
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or _is_reparse(before) or before.st_size > max_bytes:
        raise LaunchError(f"Refusing unsafe runtime file: {path.name}")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or _is_reparse(opened)
            or opened.st_size != before.st_size
            or opened.st_size > max_bytes
        ):
            raise LaunchError(f"Runtime file changed while opening: {path.name}")
        chunks: list[bytes] = []
        remaining = max_bytes + 1
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        if len(data) != opened.st_size or len(data) > max_bytes:
            raise LaunchError(f"Runtime file changed while reading: {path.name}")
        return data
    finally:
        os.close(descriptor)


def _runtime_root() -> Path:
    local = os.environ.get("LOCALAPPDATA", "").strip()
    if not local:
        raise LaunchError("LOCALAPPDATA is unavailable for the reviewed Meshy runtime.")
    root = Path(local) / "HOI4 Mod Setup" / "runtimes" / f"meshy-{MESHY_VERSION}"
    node_modules = root / "node_modules"
    if not node_modules.is_dir():
        raise LaunchError("The reviewed Meshy runtime is not installed; run Repair.")
    return node_modules


def _copy_verified_tree(source_root: Path, destination_root: Path) -> None:
    source_state = source_root.lstat()
    if not stat.S_ISDIR(source_state.st_mode) or _is_reparse(source_state):
        raise LaunchError("The Meshy runtime root is not a regular directory.")
    files: list[tuple[str, Path]] = []
    for current, directories, names in os.walk(source_root, topdown=True, followlinks=False):
        current_path = Path(current)
        current_state = current_path.lstat()
        if not stat.S_ISDIR(current_state.st_mode) or _is_reparse(current_state):
            raise LaunchError("The Meshy runtime contains a linked directory.")
        for directory in directories:
            state = (current_path / directory).lstat()
            if not stat.S_ISDIR(state.st_mode) or _is_reparse(state):
                raise LaunchError("The Meshy runtime contains a linked directory.")
        for name in names:
            path = current_path / name
            relative = path.relative_to(source_root).as_posix()
            files.append((relative, path))
            if len(files) > MESHY_TREE_MAX_FILES:
                raise LaunchError("The Meshy runtime exceeds its reviewed file count.")
    files.sort(key=lambda item: item[0])
    digest = hashlib.sha256()
    total = 0
    for relative, path in files:
        data = _regular_file_bytes(path, MESHY_FILE_MAX_BYTES)
        total += len(data)
        if total > MESHY_TREE_MAX_BYTES:
            raise LaunchError("The Meshy runtime exceeds its reviewed size.")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
        destination = destination_root.joinpath(*relative.split("/"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    if len(files) != MESHY_TREE_FILE_COUNT or digest.hexdigest() != MESHY_TREE_SHA256:
        raise LaunchError("The installed Meshy runtime does not match the reviewed lock.")


def _verified_private_node(destination: Path) -> Path:
    located = shutil.which("node.exe") or shutil.which("node")
    if not located:
        raise LaunchError("Node.js LTS is unavailable; run Repair.")
    node = Path(located).resolve()
    system_root = os.environ.get("SystemRoot", "C:/Windows")
    powershell = Path(system_root) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    if not powershell.is_file():
        raise LaunchError("Windows signature verification is unavailable.")
    check_environment = {"SystemRoot": system_root}
    escaped = str(node).replace("'", "''")
    check = subprocess.run(
        [
            str(powershell),
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            f"$s=Get-AuthenticodeSignature -LiteralPath '{escaped}'; "
            "if ($s.Status -ne 'Valid' -or $s.SignerCertificate.Subject -notmatch 'OpenJS Foundation') { exit 7 }",
        ],
        env=check_environment,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if check.returncode != 0:
        raise LaunchError("Node.js did not pass the reviewed publisher check.")
    node_bytes = _regular_file_bytes(node, NODE_MAX_BYTES)
    private_node = destination / "node.exe"
    private_node.write_bytes(node_bytes)
    if hashlib.sha256(private_node.read_bytes()).digest() != hashlib.sha256(node_bytes).digest():
        raise LaunchError("The private Node.js runtime copy failed verification.")
    return private_node


def main() -> int:
    key = os.environ.pop("MESHY_API_KEY", "").strip()
    if not key:
        raise LaunchError("MESHY_API_KEY is missing.")
    with tempfile.TemporaryDirectory(prefix="hoi4-meshy-runtime-") as temporary:
        private_root = Path(temporary)
        private_modules = private_root / "node_modules"
        private_modules.mkdir()
        _copy_verified_tree(_runtime_root(), private_modules)
        package = json.loads(
            (private_modules / "@meshy-ai/meshy-mcp-server/package.json").read_text(encoding="utf-8")
        )
        if package.get("name") != MESHY_PACKAGE or package.get("version") != MESHY_VERSION:
            raise LaunchError("The private Meshy package identity is invalid.")
        node = _verified_private_node(private_root)
        child_environment = {
            "MESHY_API_KEY": key,
            "SystemRoot": os.environ.get("SystemRoot", "C:/Windows"),
            "TEMP": temporary,
            "TMP": temporary,
        }
        del key
        entry = private_modules / "@meshy-ai/meshy-mcp-server/dist/index.js"
        return subprocess.run([str(node), str(entry)], env=child_environment, check=False).returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LaunchError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(3) from None
