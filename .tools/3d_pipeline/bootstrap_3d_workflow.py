"""Autonomously resolve and materialize feature-gated HOI4 3D MCP routes."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import site
import socket
import stat
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


MESHY_PACKAGE = "@meshy-ai/meshy-mcp-server"
MESHY_VERSION = "0.4.0"
MESHY_INTEGRITY = "sha512-py2xFIrrBcU4SW7ked90/qjRqa6bheVn0fNLEW8Lnki3BCJTFaVvWN0W6a9mJYr26+M9y0WezGsTCKalzWrGtg=="
BLENDER_MCP_REPOSITORY = "https://projects.blender.org/lab/blender_mcp.git"
IO_PDX_RELEASE = "0.91"
IO_PDX_ASSET_NAME = "blender-io_pdx_mesh.zip"
IO_PDX_DOWNLOAD_URL = "https://github.com/ross-g/io_pdx_mesh/releases/download/0.91/blender-io_pdx_mesh.zip"
IO_PDX_SHA256 = "a683df08318cb700014c7fe9a3d15139e5fb2313c7e98715204263e48931f7c2"
IO_PDX_SIZE = 235195
MESHY_BALANCE_API = "https://api.meshy.ai/openapi/v1/balance"
MAX_JSON_RESPONSE_BYTES = 1024 * 1024
MAX_MESHY_RESPONSE_BYTES = 16 * 1024
MAX_DOWNLOAD_BYTES = 256 * 1024 * 1024
MAX_ARCHIVE_FILES = 4096
MAX_ARCHIVE_ENTRY_BYTES = 64 * 1024 * 1024
MAX_ARCHIVE_EXPANDED_BYTES = 512 * 1024 * 1024
MAX_ARCHIVE_COMPRESSION_RATIO = 200
GITHUB_API_HOSTS = frozenset({"api.github.com"})
GITHUB_DOWNLOAD_HOSTS = frozenset(
    {
        "github.com",
        "objects.githubusercontent.com",
        "release-assets.githubusercontent.com",
    }
)
MESHY_API_HOSTS = frozenset({"api.meshy.ai"})


class SetupError(RuntimeError):
    """Raised when autonomous setup cannot safely finish."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(command: list[str], *, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        output = completed.stdout.strip()
        raise SetupError(f"Command failed ({completed.returncode}): {' '.join(command)}\n{output}")
    return completed.stdout


def _validate_https_url(url: str, allowed_hosts: frozenset[str]) -> None:
    parsed = urllib.parse.urlsplit(url)
    try:
        port = parsed.port
    except ValueError as exc:
        raise SetupError("Refusing an unapproved dependency URL or redirect target.") from exc
    if (
        parsed.scheme.lower() != "https"
        or not parsed.hostname
        or parsed.hostname.lower() not in allowed_hosts
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
    ):
        raise SetupError("Refusing an unapproved dependency URL or redirect target.")


class _BoundedRedirectHandler(urllib.request.HTTPRedirectHandler):
    max_redirections = 5

    def __init__(self, allowed_hosts: frozenset[str]) -> None:
        super().__init__()
        self.allowed_hosts = allowed_hosts

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        _validate_https_url(newurl, self.allowed_hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _read_bounded_response(response, max_bytes: int) -> bytes:  # type: ignore[no-untyped-def]
    declared = response.headers.get("Content-Length")
    if declared:
        try:
            if int(declared) > max_bytes:
                raise SetupError("The dependency response exceeds its reviewed byte limit.")
        except ValueError as exc:
            raise SetupError("The dependency response has an invalid Content-Length.") from exc
    data = bytearray()
    while True:
        chunk = response.read(min(1024 * 1024, max_bytes + 1 - len(data)))
        if not chunk:
            return bytes(data)
        data.extend(chunk)
        if len(data) > max_bytes:
            raise SetupError("The dependency response exceeds its reviewed byte limit.")


def _fetch_bytes(
    url: str,
    *,
    allowed_hosts: frozenset[str],
    max_bytes: int,
    timeout: int,
    headers: dict[str, str] | None = None,
) -> bytes:
    _validate_https_url(url, allowed_hosts)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "hoi4-3d-model-pipeline", **(headers or {})},
    )
    opener = urllib.request.build_opener(_BoundedRedirectHandler(allowed_hosts))
    try:
        with opener.open(request, timeout=timeout) as response:
            _validate_https_url(response.geturl(), allowed_hosts)
            return _read_bounded_response(response, max_bytes)
    except SetupError:
        raise
    except Exception as exc:  # pragma: no cover - provider/network-specific
        raise SetupError("The reviewed dependency endpoint could not be reached safely.") from exc


def fetch_json(
    url: str,
    *,
    allowed_hosts: frozenset[str] = GITHUB_API_HOSTS,
    max_bytes: int = MAX_JSON_RESPONSE_BYTES,
    headers: dict[str, str] | None = None,
) -> dict:
    try:
        value = json.loads(
            _fetch_bytes(
                url,
                allowed_hosts=allowed_hosts,
                max_bytes=max_bytes,
                timeout=120,
                headers={"Accept": "application/json", **(headers or {})},
            ).decode("utf-8")
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SetupError("The reviewed endpoint returned malformed JSON.") from exc
    if not isinstance(value, dict):
        raise SetupError("The reviewed endpoint returned an unexpected JSON value.")
    return value


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    if temporary.exists():
        temporary.unlink()
    try:
        _validate_https_url(url, GITHUB_DOWNLOAD_HOSTS)
        request = urllib.request.Request(url, headers={"User-Agent": "hoi4-3d-model-pipeline"})
        opener = urllib.request.build_opener(_BoundedRedirectHandler(GITHUB_DOWNLOAD_HOSTS))
        with opener.open(request, timeout=300) as response, temporary.open("xb") as stream:
            _validate_https_url(response.geturl(), GITHUB_DOWNLOAD_HOSTS)
            declared = response.headers.get("Content-Length")
            if declared:
                try:
                    if int(declared) > MAX_DOWNLOAD_BYTES:
                        raise SetupError("The dependency download exceeds its reviewed byte limit.")
                except ValueError as exc:
                    raise SetupError("The dependency download has an invalid Content-Length.") from exc
            total = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_DOWNLOAD_BYTES:
                    raise SetupError("The dependency download exceeds its reviewed byte limit.")
                stream.write(chunk)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(destination)
    except SetupError:
        temporary.unlink(missing_ok=True)
        raise
    except Exception:
        temporary.unlink(missing_ok=True)
        raise SetupError("The reviewed dependency could not be downloaded safely.")


def require_meshy_key() -> str:
    # Remove the credential from the inherited environment immediately. Only
    # the bounded Meshy balance request below receives it; winget, pip, npm,
    # Git, uv, Blender, and downloaded setup code never inherit the secret.
    key = os.environ.pop("MESHY_API_KEY", "").strip()
    if key:
        return key
    print("MESHY_API_KEY is missing. Stop before any 3D setup begins.")
    print("Run this PowerShell command:")
    print(
        "[Environment]::SetEnvironmentVariable(\n"
        '    "MESHY_API_KEY",\n'
        '    "msy_your_actual_key_here",\n'
        '    "User"\n'
        ")"
    )
    print("Then restart the shell or Codex.")
    raise SetupError("MESHY_API_KEY is missing")


def verify_meshy_key(key: str) -> None:
    payload = fetch_json(
        MESHY_BALANCE_API,
        allowed_hosts=MESHY_API_HOSTS,
        max_bytes=MAX_MESHY_RESPONSE_BYTES,
        headers={"Authorization": f"Bearer {key}"},
    )
    balance = payload.get("balance")
    if isinstance(balance, bool) or not isinstance(balance, (int, float)):
        raise SetupError("Meshy authentication did not return a valid account balance.")


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def version_tuple(value: str) -> tuple[int, int, int] | None:
    numbers = re.findall(r"\d+", value)
    if not numbers:
        return None
    padded = (numbers + ["0", "0", "0"])[:3]
    return tuple(int(number) for number in padded)


def shortcut_target(shortcut: Path) -> Path | None:
    powershell = shutil.which("powershell.exe") or shutil.which("pwsh.exe")
    if not powershell:
        return None
    escaped = str(shortcut).replace("'", "''")
    expression = (
        "$shell = New-Object -ComObject WScript.Shell; "
        f"$shell.CreateShortcut('{escaped}').TargetPath"
    )
    completed = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", expression],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    target = completed.stdout.strip()
    if completed.returncode != 0 or not target:
        return None
    path = Path(target)
    if path.name.lower() == "blender-launcher.exe":
        executable = path.with_name("blender.exe")
        return executable if executable.is_file() else None
    return path if path.is_file() else None


def find_blender() -> tuple[Path, Path | None, str]:
    user_profile = Path(os.environ.get("USERPROFILE", str(Path.home())))
    local_appdata = Path(os.environ.get("LOCALAPPDATA", user_profile / "AppData/Local"))
    program_files = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
    program_files_x86 = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)"))

    candidates: list[tuple[Path, Path | None]] = []
    explicit = os.environ.get("BLENDER_EXE", "").strip()
    if explicit:
        candidates.append((Path(explicit), None))

    shortcut_dirs = [
        user_profile / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Blender",
        user_profile / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs",
    ]
    shortcuts: list[Path] = []
    for directory in shortcut_dirs:
        if directory.exists():
            shortcuts.extend(directory.glob("Blender*.lnk"))
            if directory.name == "Blender":
                shortcuts.extend(directory.glob("*.lnk"))
    for shortcut in sorted(set(shortcuts)):
        target = shortcut_target(shortcut)
        if target:
            candidates.append((target, shortcut))

    install_roots = [
        program_files / "Blender Foundation",
        program_files_x86 / "Blender Foundation",
        local_appdata / "Programs/Blender Foundation",
    ]
    for root in install_roots:
        if root.exists():
            candidates.extend((path, None) for path in root.rglob("blender.exe"))

    valid: list[tuple[tuple[int, int, int], Path, Path | None, str]] = []
    seen: set[Path] = set()
    for candidate, shortcut in candidates:
        if not candidate.is_file():
            continue
        try:
            executable = candidate.resolve()
        except OSError:
            continue
        if executable in seen:
            continue
        seen.add(executable)
        try:
            version_output = run([str(executable), "--version"])
        except SetupError:
            continue
        match = re.search(r"Blender (\d+\.\d+\.\d+)", version_output)
        if not match:
            continue
        parsed = version_tuple(match.group(1))
        if parsed is not None:
            valid.append((parsed, executable, shortcut, match.group(1)))

    if not valid:
        raise SetupError("No usable Blender executable could be discovered autonomously.")
    _, executable, shortcut, version = max(valid, key=lambda item: (item[0], str(item[1])))
    return executable, shortcut, version


def ensure_npx() -> Path:
    located = shutil.which("npx.cmd") or shutil.which("npx")
    if not located:
        winget = shutil.which("winget")
        if winget:
            run(
                [
                    winget,
                    "install",
                    "OpenJS.NodeJS.LTS",
                    "--scope",
                    "user",
                    "--silent",
                    "--disable-interactivity",
                    "--accept-source-agreements",
                    "--accept-package-agreements",
                ]
            )
            located = shutil.which("npx.cmd") or shutil.which("npx")
    if not located:
        raise SetupError("npx could not be discovered or installed autonomously.")
    return Path(located).resolve()


def ensure_uv() -> Path:
    explicit = os.environ.get("UV_EXE", "").strip()
    candidates = [Path(explicit)] if explicit else []
    located = shutil.which("uv.exe") or shutil.which("uv")
    if located:
        candidates.append(Path(located))
    candidates.append(Path(site.getuserbase()) / "Scripts/uv.exe")
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate.resolve()
    run([sys.executable, "-m", "pip", "install", "--user", "uv"])
    located = shutil.which("uv.exe") or shutil.which("uv")
    if located:
        return Path(located).resolve()
    user_candidate = Path(site.getuserbase()) / "Scripts/uv.exe"
    if user_candidate.exists():
        return user_candidate.resolve()
    raise SetupError("uv was installed but could not be discovered on PATH.")


def npm_for_npx(npx: Path) -> Path:
    candidates = [npx.with_name("npm.cmd"), npx.with_name("npm.exe")]
    located = shutil.which("npm.cmd") or shutil.which("npm")
    if located:
        candidates.append(Path(located))
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    raise SetupError("npm could not be discovered next to the resolved npx executable.")


def resolve_meshy(npx: Path) -> dict:
    npm = npm_for_npx(npx)
    package_spec = f"{MESHY_PACKAGE}@{MESHY_VERSION}"
    output = run([str(npm), "view", package_spec, "dist.integrity", "--json"])
    try:
        integrity = json.loads(output)
    except json.JSONDecodeError as exc:
        raise SetupError("npm returned malformed Meshy integrity evidence.") from exc
    if integrity != MESHY_INTEGRITY:
        raise SetupError("The pinned Meshy package integrity does not match the reviewed release.")
    return {
        "package": MESHY_PACKAGE,
        "version": MESHY_VERSION,
        "integrity": MESHY_INTEGRITY,
        "resolution": "pinned npm version and integrity",
    }


def resolve_blender_mcp() -> dict:
    symref_output = run(["git", "ls-remote", "--symref", BLENDER_MCP_REPOSITORY, "HEAD"])
    default_branch = "main"
    default_commit = ""
    for line in symref_output.splitlines():
        if line.startswith("ref: refs/heads/") and line.endswith("\tHEAD"):
            default_branch = line.split("refs/heads/", 1)[1].split("\t", 1)[0]
        parts = line.split()
        if len(parts) == 2 and parts[1] == "HEAD":
            default_commit = parts[0]
    if not default_commit:
        raise SetupError("The Blender MCP repository did not expose a default-branch head.")

    tag_output = run(["git", "ls-remote", "--tags", "--refs", BLENDER_MCP_REPOSITORY])
    tags: list[tuple[tuple[int, int, int], str, str]] = []
    for line in tag_output.splitlines():
        parts = line.split()
        if len(parts) != 2 or not parts[1].startswith("refs/tags/"):
            continue
        tag = parts[1].split("refs/tags/", 1)[1]
        parsed = version_tuple(tag)
        if parsed is not None and re.search(r"\d+\.\d+", tag):
            tags.append((parsed, tag, parts[0]))

    if tags:
        _, tag, commit = max(tags, key=lambda item: (item[0], item[1]))
        return {
            "repository": BLENDER_MCP_REPOSITORY,
            "ref_type": "tag",
            "ref": tag,
            "commit": commit,
            "default_branch": default_branch,
            "default_head": default_commit,
            "resolution": "latest semantic release tag",
        }
    return {
        "repository": BLENDER_MCP_REPOSITORY,
        "ref_type": "branch",
        "ref": default_branch,
        "commit": default_commit,
        "default_branch": default_branch,
        "default_head": default_commit,
        "resolution": "latest default-branch head",
    }


def ensure_blender_mcp(pipeline_root: Path, resolution: dict) -> Path:
    vendor_root = pipeline_root / "vendor" / "blender_mcp"
    if not (vendor_root / ".git").exists():
        if vendor_root.exists():
            raise SetupError(f"Existing Blender MCP checkout is not a git repository: {vendor_root}")
        vendor_root.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--filter=blob:none", BLENDER_MCP_REPOSITORY, str(vendor_root)])
    origin = run(["git", "remote", "get-url", "origin"], cwd=vendor_root).strip().rstrip("/")
    expected_origin = BLENDER_MCP_REPOSITORY.rstrip("/")
    normalized_origin = origin[:-4] if origin.endswith(".git") else origin
    normalized_expected = expected_origin[:-4] if expected_origin.endswith(".git") else expected_origin
    if normalized_origin != normalized_expected:
        raise SetupError(f"Blender MCP checkout has an unexpected origin: {origin}")
    exclude = vendor_root / ".git/info/exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    excluded_lines = exclude.read_text(encoding="utf-8").splitlines() if exclude.exists() else []
    if "uv.lock" not in excluded_lines:
        exclude.write_text("\n".join([*excluded_lines, "uv.lock"]).rstrip() + "\n", encoding="utf-8")
    if run(["git", "status", "--porcelain"], cwd=vendor_root).strip():
        raise SetupError(f"Blender MCP checkout has local changes and cannot be updated safely: {vendor_root}")
    run(["git", "fetch", "--tags", "--prune", "origin"], cwd=vendor_root)
    try:
        run(["git", "cat-file", "-e", f"{resolution['commit']}^{{commit}}"], cwd=vendor_root)
    except SetupError:
        run(["git", "fetch", "origin", resolution["commit"]], cwd=vendor_root)
    run(["git", "checkout", "--detach", resolution["commit"]], cwd=vendor_root)
    head = run(["git", "rev-parse", "HEAD"], cwd=vendor_root).strip()
    if head.lower() != resolution["commit"].lower():
        raise SetupError(f"Blender MCP did not resolve to the latest selected ref: {head}")
    project_candidates = [vendor_root, vendor_root / "mcp"]
    for project_root in project_candidates:
        pyproject = project_root / "pyproject.toml"
        if pyproject.exists() and "blender-mcp" in pyproject.read_text(encoding="utf-8"):
            return project_root.resolve()
    raise SetupError(f"Resolved Blender MCP checkout has no discoverable Python project: {vendor_root}")


def safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    members = archive.infolist()
    if len(members) > MAX_ARCHIVE_FILES:
        raise SetupError("The io_pdx_mesh archive contains too many entries.")
    if destination.exists() and any(destination.iterdir()):
        raise SetupError("The io_pdx_mesh extraction destination is not empty.")
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    seen: set[str] = set()
    expanded = 0
    try:
        for member in members:
            name = member.filename
            relative = PurePosixPath(name)
            if (
                not name
                or "\\" in name
                or relative.is_absolute()
                or any(part in ("", ".", "..") for part in relative.parts)
            ):
                raise SetupError("The io_pdx_mesh archive contains an unsafe path.")
            collision_key = relative.as_posix().casefold()
            if collision_key in seen:
                raise SetupError("The io_pdx_mesh archive contains duplicate or case-colliding paths.")
            seen.add(collision_key)
            mode = (member.external_attr >> 16) & 0o170000
            if mode == stat.S_IFLNK:
                raise SetupError("The io_pdx_mesh archive contains a symbolic link.")
            if mode not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise SetupError("The io_pdx_mesh archive contains a special file.")
            if member.flag_bits & 0x1:
                raise SetupError("The io_pdx_mesh archive contains an encrypted entry.")
            if member.file_size > MAX_ARCHIVE_ENTRY_BYTES:
                raise SetupError("The io_pdx_mesh archive contains an oversized entry.")
            expanded += member.file_size
            if expanded > MAX_ARCHIVE_EXPANDED_BYTES:
                raise SetupError("The io_pdx_mesh archive expands beyond its reviewed byte limit.")
            if (
                member.file_size > 1024 * 1024
                and (
                    member.compress_size == 0
                    or member.file_size / member.compress_size > MAX_ARCHIVE_COMPRESSION_RATIO
                )
            ):
                raise SetupError("The io_pdx_mesh archive has an unsafe compression ratio.")
            target = (destination / Path(*relative.parts)).resolve()
            try:
                target.relative_to(root)
            except ValueError as exc:
                raise SetupError("The io_pdx_mesh archive escaped its destination.") from exc
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            written = 0
            with archive.open(member, "r") as source, target.open("xb") as output:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > member.file_size or written > MAX_ARCHIVE_ENTRY_BYTES:
                        raise SetupError("The io_pdx_mesh archive entry exceeded its declared size.")
                    output.write(chunk)
            if written != member.file_size:
                raise SetupError("The io_pdx_mesh archive entry size did not match its evidence.")
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def manifest_version(install_root: Path) -> str | None:
    return manifest_value(install_root, "version")


def manifest_value(install_root: Path, key: str) -> str | None:
    manifest = install_root / "blender_manifest.toml"
    if not manifest.exists():
        return None
    match = re.search(
        rf'^\s*{re.escape(key)}\s*=\s*["\']([^"\']+)',
        manifest.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    return match.group(1) if match else None


def archive_extension(source_root: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    if temporary.exists():
        temporary.unlink()
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in sorted(source_root.rglob("*")):
            if not source.is_file() or "__pycache__" in source.parts or source.suffix == ".pyc":
                continue
            archive.write(source, source.relative_to(source_root).as_posix())
    temporary.replace(destination)


def resolve_blender_extension_repo(
    blender_executable: Path,
    preferred_root: Path,
    extension_id: str,
) -> dict:
    target = json.dumps(str(preferred_root.resolve()))
    extension_id_literal = json.dumps(extension_id)
    code = (
        "import bpy\n"
        f"target = __import__('pathlib').Path({target}).resolve()\n"
        f"extension_id = {extension_id_literal}\n"
        "repos = list(bpy.context.preferences.extensions.repos)\n"
        "existing = [repo for repo in repos if repo.enabled and "
        "(__import__('pathlib').Path(repo.directory) / extension_id / 'blender_manifest.toml').exists()]\n"
        "preferred = [repo for repo in repos if repo.enabled and "
        "__import__('pathlib').Path(repo.directory).resolve() == target]\n"
        "selected = existing[0] if existing else (preferred[0] if preferred else None)\n"
        "print('CODEX_EXTENSION_REPO=' + (selected.module if selected else ''))\n"
        "print('CODEX_EXTENSION_REPO_DIRECTORY=' + (selected.directory if selected else ''))\n"
    )
    output = run([str(blender_executable), "--background", "--python-expr", code])
    module_match = re.search(r"CODEX_EXTENSION_REPO=([^\s]+)", output)
    directory_match = re.search(r"CODEX_EXTENSION_REPO_DIRECTORY=(.*)", output)
    if (
        not module_match
        or not module_match.group(1).strip()
        or not directory_match
        or not directory_match.group(1).strip()
    ):
        raise SetupError(f"Blender has no enabled extension repository for {preferred_root}.")
    return {
        "module": module_match.group(1).strip(),
        "directory": Path(directory_match.group(1).strip()).resolve(),
    }


def resolve_blender_bridge_settings(addon_source: Path) -> dict:
    server_source = addon_source / "mcp_to_blender_server.py"
    if not server_source.exists():
        raise SetupError(f"The resolved Blender MCP add-on has no bridge server module: {server_source}")
    source = server_source.read_text(encoding="utf-8")
    host_match = re.search(r'^DEFAULT_HOST\s*=\s*["\']([^"\']+)', source, re.MULTILINE)
    port_match = re.search(r"^DEFAULT_PORT\s*=\s*(\d+)", source, re.MULTILINE)
    if not host_match or not port_match:
        raise SetupError("The resolved Blender MCP add-on did not expose a discoverable default bridge endpoint.")
    return {
        "host": host_match.group(1),
        "port": int(port_match.group(1)),
        "resolution": "latest resolved Blender MCP add-on source",
    }


def install_blender_extension(
    blender_executable: Path,
    archive: Path,
    extension_repo: str,
) -> str:
    archive_literal = json.dumps(str(archive.resolve()))
    repo_literal = json.dumps(extension_repo)
    code = (
        "import bpy\n"
        f"result = bpy.ops.extensions.package_install_files(filepath={archive_literal}, "
        f"repo={repo_literal}, enable_on_install=True, overwrite=True)\n"
        "print('CODEX_EXTENSION_INSTALL=' + repr(result))\n"
    )
    output = run([str(blender_executable), "--background", "--python-expr", code])
    if "'FINISHED'" not in output:
        raise SetupError(f"Blender did not install the MCP add-on archive: {output.strip()}")
    return output


def configure_blender_extension(
    blender_executable: Path,
    extension_repo: str,
    extension_id: str,
    bridge: dict,
) -> bool:
    module = f"bl_ext.{extension_repo}.{extension_id}"
    module_literal = json.dumps(module)
    host_literal = json.dumps(bridge["host"])
    port = int(bridge["port"])
    code = (
        "import bpy\n"
        f"addon = bpy.context.preferences.addons.get({module_literal})\n"
        "if addon is None:\n"
        "    print('CODEX_EXTENSION_CONFIGURED=0')\n"
        "else:\n"
        "    prefs = addon.preferences\n"
        f"    prefs.host = {host_literal}\n"
        f"    prefs.port = {port}\n"
        "    prefs.use_autostart = True\n"
        "    bpy.ops.wm.save_userpref()\n"
        "    print('CODEX_EXTENSION_CONFIGURED=1')\n"
    )
    output = run([str(blender_executable), "--background", "--python-expr", code])
    return "CODEX_EXTENSION_CONFIGURED=1" in output


def ensure_blender_mcp_addon(
    pipeline_root: Path,
    blender_executable: Path,
    blender_mcp_project: Path,
    blender_mcp: dict,
    io_pdx_mesh: dict,
    bridge: dict,
) -> dict:
    checkout_root = pipeline_root / "vendor" / "blender_mcp"
    addon_source = checkout_root / "addon" / "blender_mcp_addon"
    addon_version = manifest_version(addon_source)
    addon_id = manifest_value(addon_source, "id")
    if not addon_version or not addon_id:
        raise SetupError(f"The latest Blender MCP checkout has no usable add-on manifest: {addon_source}")

    preferred_root = Path(io_pdx_mesh["install_root"]).parent
    repo_info = resolve_blender_extension_repo(blender_executable, preferred_root, addon_id)
    extension_repo = repo_info["module"]
    extension_root = repo_info["directory"]
    safe_ref = re.sub(r"[^A-Za-z0-9._-]+", "_", blender_mcp["ref"])
    archive = pipeline_root / "vendor" / "blender_mcp_addon_cache" / f"{safe_ref}-{addon_id}-{addon_version}.zip"
    archive_extension(addon_source, archive)
    archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest().upper()

    install_root = extension_root / addon_id
    installed_version = manifest_version(install_root)
    configured = installed_version == addon_version and configure_blender_extension(
        blender_executable,
        extension_repo,
        addon_id,
        bridge,
    )
    if not configured:
        install_blender_extension(blender_executable, archive, extension_repo)
        configured = configure_blender_extension(
            blender_executable,
            extension_repo,
            addon_id,
            bridge,
        )
    if not configured:
        raise SetupError(
            f"Blender installed the MCP add-on files but did not enable {addon_id} in repository {extension_repo}."
        )
    installed_version = manifest_version(install_root)
    if installed_version != addon_version:
        raise SetupError(
            f"Blender MCP add-on version mismatch after installation: expected {addon_version}, "
            f"found {installed_version or 'missing'}."
        )
    return {
        "repository": blender_mcp["repository"],
        "ref": blender_mcp["ref"],
        "commit": blender_mcp["commit"],
        "addon_id": addon_id,
        "version": installed_version,
        "source_root": addon_source.resolve().as_posix(),
        "archive": archive.resolve().as_posix(),
        "sha256": archive_hash,
        "extension_repo": extension_repo,
        "install_root": install_root.resolve().as_posix(),
        "blender_mcp_project": blender_mcp_project.resolve().as_posix(),
        "bridge": bridge,
    }


def bridge_reachable(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def ensure_blender_bridge(blender_executable: Path, bridge: dict) -> dict:
    probe_host = "127.0.0.1"
    port = int(bridge["port"])
    started_by_bootstrap = False
    blender_process = None
    if not bridge_reachable(probe_host, port):
        command = [
            str(blender_executable),
            "--background",
            "--online-mode",
            "--command",
            "blender_mcp",
            "--host",
            probe_host,
            "--port",
            str(port),
        ]
        blender_process = subprocess.Popen(
            command,
            cwd=str(blender_executable.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        started_by_bootstrap = True
        deadline = time.monotonic() + 60.0
        while time.monotonic() < deadline and not bridge_reachable(probe_host, port):
            if blender_process.poll() is not None:
                raise SetupError(
                    f"Blender exited before the MCP bridge became reachable (exit {blender_process.returncode})."
                )
            time.sleep(1.0)
    if not bridge_reachable(probe_host, port):
        raise SetupError(
            f"Blender is running but the MCP bridge is not reachable at {bridge['host']}:{port}."
        )
    return {
        **bridge,
        "probe_host": probe_host,
        "reachable": True,
        "started_by_bootstrap": started_by_bootstrap,
        "process_id": blender_process.pid if blender_process else None,
        "start_command": command if started_by_bootstrap else None,
    }


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def materialize_hoi4_adapter(
    root: Path,
    pipeline_root: Path,
    uv_executable: Path,
    blender_executable: Path,
    io_pdx_mesh: dict,
) -> dict:
    """Install and lock the repository-owned production adapter without exposing arbitrary Python."""

    adapter_root = pipeline_root / "adapter"
    pyproject = adapter_root / "pyproject.toml"
    module = adapter_root / "hoi4_blender_mcp.py"
    worker = adapter_root / "blender_worker.py"
    wrapper = pipeline_root / "wrappers/run_blender_hoi4_adapter.cmd"
    for required in (pyproject, module, worker, wrapper):
        if not required.is_file():
            raise SetupError(f"Repository-owned Blender HOI4 adapter file is missing: {required}")

    pyproject_text = pyproject.read_text(encoding="utf-8")
    version_match = re.search(r'^version\s*=\s*["\']([^"\']+)', pyproject_text, re.MULTILINE)
    if not version_match:
        raise SetupError("The Blender HOI4 adapter pyproject has no version.")
    adapter_version = version_match.group(1)
    run([str(uv_executable), "lock", "--upgrade"], cwd=adapter_root)
    run([str(uv_executable), "sync", "--locked"], cwd=adapter_root)
    uv_lock = adapter_root / "uv.lock"
    if not uv_lock.is_file():
        raise SetupError("uv did not materialize the Blender HOI4 adapter dependency lock.")

    game_root = Path(
        os.environ.get(
            "HOI4_GAME_ROOT",
            "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV",
        )
    ).resolve()
    job_root = Path(os.environ.get("HOI4_3D_JOB_ROOT", str(root / "docs/assets"))).resolve()
    try:
        job_root.relative_to(root.resolve())
    except ValueError as exc:
        raise SetupError("HOI4_3D_JOB_ROOT must remain inside the repository.") from exc

    operations = re.findall(r'^def (hoi4_blender_[a-z0-9_]+)\(', module.read_text(encoding="utf-8"), re.MULTILINE)
    if not operations:
        raise SetupError("The Blender HOI4 adapter exposes no structured tools.")
    worker_operations = [name.removeprefix("hoi4_blender_") for name in operations]
    config_path = pipeline_root / "config/blender_hoi4_adapter.json"
    config = {
        "schema_version": "1.0.0",
        "adapter_id": "hoi4_blender_adapter",
        "adapter_version": adapter_version,
        "repository_root": root.resolve().as_posix(),
        "job_root": job_root.as_posix(),
        "blender_executable": blender_executable.resolve().as_posix(),
        "io_pdx_mesh_root": Path(io_pdx_mesh["install_root"]).resolve().as_posix(),
        "allowed_read_roots": [
            root.resolve().as_posix(),
            game_root.as_posix(),
            Path(io_pdx_mesh["install_root"]).resolve().as_posix(),
        ],
        "approved_reference_roots": {
            "vanilla": game_root.as_posix(),
        },
        "allowed_write_roots": [job_root.as_posix()],
        "operations": worker_operations,
        "forbidden_inputs": [
            "arbitrary_python",
            "arbitrary_shell",
            "arbitrary_url",
            "unrestricted_absolute_write_path",
            "provider_secret",
            "runtime_gameplay_wiring",
        ],
        "runtime_boundary": "parent_owned",
    }
    write_json(config_path, config)
    return {
        "id": "hoi4_blender_adapter",
        "version": adapter_version,
        "project": adapter_root.resolve().as_posix(),
        "module": "hoi4_blender_mcp",
        "wrapper": ".tools/3d_pipeline/wrappers/run_blender_hoi4_adapter.cmd",
        "config": config_path.resolve().as_posix(),
        "tool_identifiers": operations,
        "worker_operations": worker_operations,
        "dependency_lock": uv_lock.resolve().as_posix(),
        "checksums": {
            "pyproject_sha256": sha256_path(pyproject),
            "module_sha256": sha256_path(module),
            "worker_sha256": sha256_path(worker),
            "wrapper_sha256": sha256_path(wrapper),
            "config_sha256": sha256_path(config_path),
            "uv_lock_sha256": sha256_path(uv_lock),
        },
        "unrestricted_blender_python": False,
        "runtime_wiring": "parent_owned",
    }


def resolve_io_pdx_mesh() -> dict:
    _validate_https_url(IO_PDX_DOWNLOAD_URL, GITHUB_DOWNLOAD_HOSTS)
    return {
        "release": IO_PDX_RELEASE,
        "download_url": IO_PDX_DOWNLOAD_URL,
        "asset_name": IO_PDX_ASSET_NAME,
        "sha256": IO_PDX_SHA256,
        "size": IO_PDX_SIZE,
        "resolution": "pinned GitHub release asset with SHA-256",
    }


def ensure_io_pdx_mesh(pipeline_root: Path, blender_executable: Path, resolution: dict) -> dict:
    version_output = run([str(blender_executable), "--version"])
    match = re.search(r"Blender (\d+)\.(\d+)", version_output)
    if not match:
        raise SetupError("Unable to determine Blender minor version for io_pdx_mesh installation.")
    minor = f"{match.group(1)}.{match.group(2)}"
    appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    extension_root = appdata / "Blender Foundation/Blender" / minor / "extensions/user_default"
    install_root = extension_root / "io_pdx_mesh"

    safe_release = re.sub(r"[^A-Za-z0-9._-]+", "_", resolution["release"])
    cache = pipeline_root / "vendor" / "io_pdx_mesh" / f"{safe_release}-{resolution['asset_name']}"
    cache.parent.mkdir(parents=True, exist_ok=True)
    if not cache.exists():
        download(resolution["download_url"], cache)
    archive_bytes = cache.read_bytes()
    archive_hash = hashlib.sha256(archive_bytes).hexdigest()
    if len(archive_bytes) != resolution["size"] or archive_hash != resolution["sha256"]:
        cache.unlink(missing_ok=True)
        raise SetupError("The pinned io_pdx_mesh archive failed size or SHA-256 verification.")
    desired_version = version_tuple(resolution["release"])
    installed_version = manifest_version(install_root)
    installed_matches = (
        installed_version is not None
        and desired_version is not None
        and version_tuple(installed_version) == desired_version
    )

    if not installed_matches:
        extension_root.mkdir(parents=True, exist_ok=True)
        staging = extension_root / f".io_pdx_mesh_staging_{os.getpid()}"
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(cache) as archive:
            safe_extract(archive, staging)
        manifests = list(staging.rglob("blender_manifest.toml"))
        if len(manifests) != 1:
            shutil.rmtree(staging, ignore_errors=True)
            raise SetupError("The latest io_pdx_mesh archive did not contain exactly one extension manifest.")
        source_root = manifests[0].parent
        resolved_manifest_version = manifest_version(source_root)
        if not resolved_manifest_version:
            shutil.rmtree(staging, ignore_errors=True)
            raise SetupError("The latest io_pdx_mesh manifest has no version.")
        if install_root.exists():
            shutil.rmtree(install_root)
        install_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_root), str(install_root))
        shutil.rmtree(staging, ignore_errors=True)
        installed_version = resolved_manifest_version

    if not (install_root / "blender_manifest.toml").exists():
        raise SetupError(f"io_pdx_mesh installation is incomplete: {install_root}")
    return {
        "release": resolution["release"],
        "version": installed_version,
        "download_url": resolution["download_url"],
        "archive": cache.as_posix(),
        "sha256": archive_hash,
        "installed_extension_id": "io_pdx_mesh",
        "blender_minor": minor,
        "install_root": install_root.resolve().as_posix(),
    }


THREE_D_MCP_ROUTES = {
    "meshy": {
        "enabled": True,
        "required": True,
        "command": "cmd.exe",
        "args": ["/d", "/c", "call", ".tools/3d_pipeline/wrappers/run_meshy_mcp.cmd"],
        "cwd": ".",
        "env_vars": ["MESHY_API_KEY"],
        "startup_timeout_sec": 120.0,
        "tool_timeout_sec": 1800.0,
        "default_tools_approval_mode": "auto",
    },
    "blender_hoi4": {
        "enabled": True,
        "required": True,
        "command": "cmd.exe",
        "args": ["/d", "/c", "call", ".tools/3d_pipeline/wrappers/run_blender_hoi4_adapter.cmd"],
        "cwd": ".",
        "env_vars": [],
        "startup_timeout_sec": 120.0,
        "tool_timeout_sec": 1800.0,
        "default_tools_approval_mode": "auto",
    },
    "blender_lab": {
        "enabled": False,
        "required": False,
        "command": "cmd.exe",
        "args": ["/d", "/c", "call", ".tools/3d_pipeline/wrappers/run_blender_lab_mcp.cmd"],
        "cwd": ".",
        "env_vars": [],
        "startup_timeout_sec": 120.0,
        "tool_timeout_sec": 1800.0,
        "default_tools_approval_mode": "prompt",
    },
}


def parse_reviewed_mcp_routes(config_text: str) -> dict[str, dict]:
    routes: dict[str, dict] = {}
    current: dict | None = None
    for line in config_text.splitlines():
        stripped = line.strip()
        section = re.fullmatch(r"\[mcp_servers\.([A-Za-z0-9_-]+)\]", stripped)
        if section:
            current = routes.setdefault(section.group(1), {})
            continue
        if stripped.startswith("["):
            current = None
            continue
        if current is None or not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, raw_value = (part.strip() for part in stripped.split("=", 1))
        try:
            current[key] = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise SetupError(f"Reviewed Codex config has an unsupported value for {key}: {exc}") from exc
    return routes


def verify_reviewed_config(root: Path) -> Path:
    config_path = root / ".codex/config.toml"
    if not config_path.is_file():
        raise SetupError("The reviewed Codex config is missing.")
    routes = parse_reviewed_mcp_routes(config_path.read_text(encoding="utf-8"))
    for route_id, expected in THREE_D_MCP_ROUTES.items():
        actual = routes.get(route_id)
        if actual is None:
            raise SetupError(f"The reviewed Codex config is missing mcp_servers.{route_id}.")
        for key, value in expected.items():
            if actual.get(key) != value:
                raise SetupError(
                    f"The reviewed Codex config has an unexpected mcp_servers.{route_id}.{key}."
                )
    return config_path.resolve()


def materialize_config(root: Path) -> Path:
    config_path = root / ".codex/config.toml"
    existing = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    existing = existing.replace("<mod_root>", root.as_posix())
    marker = "# BEGIN AUTONOMOUS HOI4 3D MCP ROUTES"
    if marker in existing:
        existing = existing.split(marker, 1)[0].rstrip()
    generated = f"""{marker}
# This block is generated by .tools/3d_pipeline/bootstrap_3d_workflow.py.
# Do not replace it with a placeholder or ask the user to edit it manually.

[mcp_servers.meshy]
enabled = true
required = true
command = "cmd.exe"
args = ["/d", "/c", "call", ".tools/3d_pipeline/wrappers/run_meshy_mcp.cmd"]
cwd = "."
env_vars = ["MESHY_API_KEY"]
startup_timeout_sec = 120.0
tool_timeout_sec = 1800.0
default_tools_approval_mode = "auto"

[mcp_servers.blender_hoi4]
enabled = true
required = true
command = "cmd.exe"
args = ["/d", "/c", "call", ".tools/3d_pipeline/wrappers/run_blender_hoi4_adapter.cmd"]
cwd = "."
env_vars = []
startup_timeout_sec = 120.0
tool_timeout_sec = 1800.0
default_tools_approval_mode = "auto"

# Unrestricted Blender Lab is retained only as an isolated development aid.
# Production 3D work must use the repository-owned blender_hoi4 route above.
[mcp_servers.blender_lab]
enabled = false
required = false
command = "cmd.exe"
args = ["/d", "/c", "call", ".tools/3d_pipeline/wrappers/run_blender_lab_mcp.cmd"]
cwd = "."
env_vars = []
startup_timeout_sec = 120.0
tool_timeout_sec = 1800.0
default_tools_approval_mode = "prompt"
"""
    rendered = existing.rstrip() + "\n\n" + generated
    if re.search(r"<[^>]+>", rendered):
        raise SetupError("The generated Codex config still contains a placeholder.")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(rendered, encoding="utf-8")
    template = root / ".codex/3d_mcp_config.template.toml"
    if template.exists():
        template.unlink()
    return config_path.resolve()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_dependency_record(root: Path, payload: dict) -> Path:
    lock_path = root / ".tools/3d_pipeline/config/dependencies.lock.json"
    previous = {}
    if lock_path.exists():
        try:
            previous = json.loads(lock_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = {}
    previous_policy = previous.get("policy", {})
    legacy_attempt_key = "paid_generation_attempts_per_" + "pilot"
    previous_policy.pop(legacy_attempt_key, None)
    policy = {
        **previous_policy,
        "provider_input_image_count": 1,
        "allow_meshy_multiview_thumbnails": False,
        "default_generation_model": "Meshy 6 when exposed by the verified live schema",
        "silent_generation_model_downgrade": False,
        "planned_paid_operations_pre_authorized": True,
        "failure_recovery_requires_confirmation": True,
        "runtime_sources_must_not_reference_docs_assets": True,
        "runtime_copy_requires_selected_source_hash": True,
        "mesh_and_anim_reimport_required": True,
        "loop_phase_samples": [0.0, 0.25, 0.5, 0.75, 1.0],
        "building_footprint_and_object_name_evidence_required": True,
        "runtime_wiring_owner": "parent",
    }
    record = {
        "schema_version": "1.0.0",
        "lock_name": "hoi4-3d-model-pipeline",
        "resolution_policy": "latest_at_bootstrap",
        "resolved_at_utc": payload["resolved_at_utc"],
        "bootstrap": ".tools/3d_pipeline/bootstrap_3d_workflow.py",
        "routes": {
            "meshy_mcp": payload["meshy"],
            "meshy_tool_contract": payload["meshy_tool_contract"],
            "blender_lab_mcp": {
                **payload["blender_mcp"],
                "project": payload["blender_mcp_project"],
                "wrapper": ".tools/3d_pipeline/wrappers/run_blender_lab_mcp.cmd",
                "profile": "development_only",
                "enabled_in_production": False,
            },
            "blender_hoi4_adapter": payload["blender_hoi4_adapter"],
            "blender_mcp_addon": payload["blender_mcp_addon"],
            "blender_bridge": payload["blender_bridge"],
            "blender": {
                "executable": payload["blender_executable"],
                "shortcut": payload["blender_shortcut"],
                "version": payload["blender_version"],
            },
            "io_pdx_mesh": payload["io_pdx_mesh"],
        },
        "policy": policy,
    }
    write_json(lock_path, record)
    return lock_path.resolve()


def main() -> int:
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--quiet", action="store_true")
        parser.add_argument("--project-root", type=Path)
        parser.add_argument(
            "--verify-reviewed-config",
            action="store_true",
            help="Validate the transaction-reviewed MCP routes instead of rewriting Codex config.",
        )
        args = parser.parse_args()
        meshy_key = require_meshy_key()
        verify_meshy_key(meshy_key)
        del meshy_key
        root = (args.project_root or repository_root()).resolve()
        pipeline_root = root / ".tools/3d_pipeline"
        if not (pipeline_root / "bootstrap_3d_workflow.py").is_file():
            raise SetupError(f"The selected project has no installed 3D workflow: {pipeline_root}")
        pipeline_root.joinpath("config").mkdir(parents=True, exist_ok=True)

        npx_executable = ensure_npx()
        blender_executable, blender_shortcut, blender_version = find_blender()
        uv_executable = ensure_uv()
        meshy = resolve_meshy(npx_executable)
        meshy_contract_path = pipeline_root / "config/meshy_tool_contract.json"
        if not meshy_contract_path.is_file():
            raise SetupError(f"Meshy tool contract is missing: {meshy_contract_path}")
        meshy_tool_contract = {
            "path": meshy_contract_path.resolve().as_posix(),
            "sha256": sha256_path(meshy_contract_path),
            "contract": json.loads(meshy_contract_path.read_text(encoding="utf-8")),
            "live_schema_verification_required_before_provider_calls": True,
        }
        blender_mcp = resolve_blender_mcp()
        blender_mcp_project = ensure_blender_mcp(pipeline_root, blender_mcp)
        io_resolution = resolve_io_pdx_mesh()
        io_pdx_mesh = ensure_io_pdx_mesh(pipeline_root, blender_executable, io_resolution)
        blender_hoi4_adapter = materialize_hoi4_adapter(
            root,
            pipeline_root,
            uv_executable,
            blender_executable,
            io_pdx_mesh,
        )
        addon_source = pipeline_root / "vendor" / "blender_mcp" / "addon" / "blender_mcp_addon"
        bridge = resolve_blender_bridge_settings(addon_source)
        blender_mcp_addon = ensure_blender_mcp_addon(
            pipeline_root,
            blender_executable,
            blender_mcp_project,
            blender_mcp,
            io_pdx_mesh,
            bridge,
        )
        blender_bridge = ensure_blender_bridge(blender_executable, bridge)
        config_path = (
            verify_reviewed_config(root)
            if args.verify_reviewed_config
            else materialize_config(root)
        )
        resolved_at = utc_now()

        payload = {
            "resolved_at_utc": resolved_at,
            "repository_root": root.as_posix(),
            "blender_executable": blender_executable.as_posix(),
            "blender_shortcut": blender_shortcut.as_posix() if blender_shortcut else None,
            "blender_version": blender_version,
            "npx_executable": npx_executable.as_posix(),
            "uv_executable": uv_executable.as_posix(),
            "blender_mcp_project": blender_mcp_project.as_posix(),
            "meshy": meshy,
            "meshy_tool_contract": meshy_tool_contract,
            "blender_mcp": blender_mcp,
            "blender_mcp_addon": blender_mcp_addon,
            "blender_bridge": blender_bridge,
            "io_pdx_mesh": io_pdx_mesh,
            "blender_hoi4_adapter": blender_hoi4_adapter,
            "config_path": config_path.as_posix(),
            "template_removed": True,
        }
        lock_path = write_dependency_record(root, payload)
        runtime = {
            "schema_version": "1.0.0",
            **payload,
            "dependency_lock": lock_path.as_posix(),
            "resolution_policy": "latest_at_bootstrap",
        }
        runtime_path = pipeline_root / "config/runtime.json"
        write_json(runtime_path, runtime)
        (pipeline_root / "config/meshy_mcp_version.txt").write_text(
            f"{meshy['version']}\n", encoding="utf-8"
        )
        (pipeline_root / "config/npx_executable.txt").write_text(
            f"{npx_executable.resolve().as_posix()}\n", encoding="utf-8"
        )
        (pipeline_root / "config/blender_mcp_project.txt").write_text(
            f"{blender_mcp_project.as_posix()}\n", encoding="utf-8"
        )
        (pipeline_root / "config/uv_executable.txt").write_text(
            f"{uv_executable.as_posix()}\n", encoding="utf-8"
        )
        (pipeline_root / "config/blender_mcp_host.txt").write_text(
            f"{blender_bridge['host']}\n", encoding="utf-8"
        )
        (pipeline_root / "config/blender_mcp_port.txt").write_text(
            f"{blender_bridge['port']}\n", encoding="utf-8"
        )
        if not args.quiet:
            print(json.dumps(runtime, indent=2))
        return 0
    except SetupError as exc:
        print(f"3D workflow setup blocked: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
