#!/usr/bin/env python3
"""Install the pinned HOI4 Live Tools release for the current Windows user.

HOI4 Mod Setup runs this script (``--quiet``) when the HOI4 Live Tools workflow is selected. It downloads the release
archive named below, checks its size and SHA-256 against the pinned values, extracts it into a private temporary folder
(no absolute paths, parent references, links, or oversized members), runs that folder's ``install.py`` with the same
Python, and removes the temporary folder. ``install.py`` creates ``%LOCALAPPDATA%\\hoi4-live-tools`` (program, private
Python environment, artifacts), starts the installed server once to confirm it lists its tools, and registers it in
the user configuration of every coding client it finds. When the pinned version is already installed, the installed
copy's ``install.py`` runs again instead (it repairs the environment and the registrations without a download).

The exit code is the installer's: 0 done, 1 failed, 2 unsupported platform or Python, 3 installed but not verified,
4 installed and verified but a client registration failed or conflicts.

The pinned values move with each HOI4 Live Tools release together with the matching parameters of the
``mcp.hoi4_live.bootstrap`` component in ``hoi4-mod-setup.manifest.json`` (``scripts/test_live_bootstrap_contract.py``
fails when they differ).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile


RELEASE_VERSION = "1.0.0"
RELEASE_URL = "https://github.com/klimPaskov/HOI4-Live-Tools/releases/download/v1.0.0/hoi4-live-tools-1.0.0.zip"
RELEASE_SHA256 = "e80c011d0858c3bb1f6e1c8333ed4f441b44e912758b8e2c9c35b730105d5ba2"
RELEASE_SIZE = 1023867
ARCHIVE_TOP = f"hoi4-live-tools-{RELEASE_VERSION}"
ALLOWED_HOSTS = ("github.com",)
ALLOWED_HOST_SUFFIXES = (".githubusercontent.com",)
MAX_MEMBERS = 400
MAX_MEMBER_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 16 * 1024 * 1024
MAX_OUTPUT_BYTES = 2 * 1024 * 1024
INSTALL_TIMEOUT_SECONDS = 25 * 60
DOWNLOAD_TIMEOUT_SECONDS = 120


class BootstrapError(RuntimeError):
    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.code = code


def host_allowed(url: str) -> bool:
    parts = urllib.parse.urlsplit(url)
    host = (parts.hostname or "").lower()
    return parts.scheme == "https" and (
        host in ALLOWED_HOSTS or any(host.endswith(suffix) for suffix in ALLOWED_HOST_SUFFIXES)
    )


class _CheckedRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        if not host_allowed(newurl):
            raise BootstrapError("The release download was redirected to a host this package does not allow.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def local_app_data() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    return Path(base) if base else Path.home() / "AppData" / "Local"


def installed_prefix() -> Path:
    override = os.environ.get("HOI4_LIVE_PREFIX")
    return Path(override) if override else local_app_data() / "hoi4-live-tools"


def installed_version(prefix: Path) -> str | None:
    try:
        record = json.loads((prefix / "install.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return record.get("version") if isinstance(record, dict) else None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_archive(path: Path) -> None:
    size = path.stat().st_size
    if size != RELEASE_SIZE:
        raise BootstrapError(f"The release archive has {size} bytes; this package pins {RELEASE_SIZE}.")
    if sha256_file(path) != RELEASE_SHA256:
        raise BootstrapError("The release archive does not match the SHA-256 this package pins.")


def download(destination: Path) -> None:
    if not host_allowed(RELEASE_URL):
        raise BootstrapError("The pinned release URL is not on an allowed host.")
    opener = urllib.request.build_opener(_CheckedRedirects)
    request = urllib.request.Request(RELEASE_URL, headers={"User-Agent": "hoi4-live-tools-bootstrap"})
    received = 0
    try:
        with opener.open(request, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response, destination.open("wb") as handle:
            while True:
                block = response.read(1 << 16)
                if not block:
                    break
                received += len(block)
                if received > RELEASE_SIZE:
                    raise BootstrapError("The release download is larger than the pinned size.")
                handle.write(block)
    except urllib.error.HTTPError as exc:
        raise BootstrapError(
            f"The release could not be downloaded (HTTP {exc.code}). "
            f"HOI4 Live Tools {RELEASE_VERSION} may not be published yet."
        ) from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise BootstrapError(f"The release could not be downloaded: {exc}") from exc


def safe_extract(archive: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    total = 0
    with zipfile.ZipFile(archive) as bundle:
        members = bundle.infolist()
        if not members or len(members) > MAX_MEMBERS:
            raise BootstrapError("The release archive has an unexpected number of members.")
        for member in members:
            name = member.filename
            pure = PurePosixPath(name)
            mode = member.external_attr >> 16
            if (
                "\\" in name
                or name.startswith("/")
                or pure.is_absolute()
                or ".." in pure.parts
                or (pure.parts and ":" in pure.parts[0])
                or (mode & 0o170000) == 0o120000
                or pure.parts[:1] != (ARCHIVE_TOP,)
            ):
                raise BootstrapError("The release archive contains an unsafe member path.")
            if member.file_size > MAX_MEMBER_BYTES:
                raise BootstrapError("The release archive contains an oversized member.")
            total += member.file_size
            if total > MAX_TOTAL_BYTES:
                raise BootstrapError("The release archive expands beyond the allowed size.")
            target = (root / Path(*pure.parts)).resolve()
            if root != target and root not in target.parents:
                raise BootstrapError("The release archive contains a member outside its folder.")
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(member) as source, target.open("wb") as handle:
                shutil.copyfileobj(source, handle)
    installer = root / ARCHIVE_TOP / "install.py"
    if not installer.is_file():
        raise BootstrapError("The release archive has no installer.")
    return installer


def run_installer(installer: Path, quiet: bool) -> int:
    arguments = [sys.executable, "-I", str(installer), "--register", "auto"]
    if quiet:
        arguments.append("--quiet")
    try:
        result = subprocess.run(
            arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=INSTALL_TIMEOUT_SECONDS,
            check=False,
            shell=False,
            cwd=str(installer.parent),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BootstrapError(f"The HOI4 Live Tools installer could not complete: {exc}") from exc
    text = result.stdout[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace").strip()
    if text:
        print(text[-4000:], file=sys.stderr if result.returncode else sys.stdout)
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--quiet", action="store_true", help="print only problems")
    parser.add_argument("--archive", type=Path, help="use this local copy of the pinned archive instead of downloading")
    args = parser.parse_args(argv)
    if sys.platform != "win32":
        print("HOI4 Live Tools installs on Windows only.", file=sys.stderr)
        return 2
    if sys.version_info < (3, 9):
        print(f"HOI4 Live Tools needs Python 3.9 or newer; this is {sys.version.split()[0]}.", file=sys.stderr)
        return 2
    prefix = installed_prefix()
    installed_installer = prefix / "app" / "install.py"
    if installed_version(prefix) == RELEASE_VERSION and installed_installer.is_file():
        try:
            return run_installer(installed_installer, args.quiet)
        except BootstrapError as exc:
            print(str(exc), file=sys.stderr)
            return exc.code
    workspace = Path(tempfile.mkdtemp(prefix="hoi4live_install_"))
    try:
        archive = args.archive or workspace / "release.zip"
        if args.archive is None:
            download(archive)
        verify_archive(archive)
        installer = safe_extract(archive, workspace / "release")
        return run_installer(installer, args.quiet)
    except BootstrapError as exc:
        print(str(exc), file=sys.stderr)
        return exc.code
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
