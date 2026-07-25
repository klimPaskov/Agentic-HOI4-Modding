"""Autonomously install and materialize the optional HOI4 3D MCP routes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path


MESHY_VERSION = "0.4.0"
BLENDER_MCP_REPOSITORY = "https://projects.blender.org/lab/blender_mcp.git"
BLENDER_MCP_COMMIT = "03004fd0216bfe5e0a3d9ac9b47d5efadc3d78c4"
IO_PDX_URL = "https://github.com/ross-g/io_pdx_mesh/releases/download/0.91/blender-io_pdx_mesh.zip"
IO_PDX_SHA256 = "A683DF08318CB700014C7FE9A3D15139E5FB2313C7E98715204263E48931F7C2"


class SetupError(RuntimeError):
    """Raised when autonomous setup cannot safely finish."""


def require_meshy_key() -> None:
    if os.environ.get("MESHY_API_KEY", "").strip():
        return
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


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def find_blender() -> tuple[Path, Path]:
    user_profile = Path(os.environ.get("USERPROFILE", ""))
    program_files = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
    shortcut = user_profile / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Blender/Blender 5.1.lnk"
    candidates = [
        program_files / "Blender Foundation/Blender 5.1/blender.exe",
        program_files / "Blender Foundation/Blender 5.0/blender.exe",
        user_profile / "AppData/Local/Programs/Blender Foundation/Blender 5.1/blender.exe",
    ]
    executable = next((path for path in candidates if path.exists()), None)
    if executable is None:
        raise SetupError("Blender 5.1 executable could not be discovered autonomously.")
    version_output = run([str(executable), "--version"])
    match = re.search(r"Blender (\d+\.\d+\.\d+)", version_output)
    if not match or not match.group(1).startswith("5.1."):
        first_line = version_output.splitlines()[0] if version_output.splitlines() else version_output
        raise SetupError(f"The discovered Blender is not the locked 5.1 route: {first_line}")
    return executable.resolve(), shortcut.resolve() if shortcut.exists() else shortcut


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
                    "--silent",
                    "--accept-source-agreements",
                    "--accept-package-agreements",
                ]
            )
            located = shutil.which("npx.cmd") or shutil.which("npx")
    if not located:
        raise SetupError("npx could not be discovered or installed autonomously.")
    return Path(located).resolve()


def ensure_uv() -> Path:
    explicit = os.environ.get("UV_EXE", "")
    candidates = [Path(explicit)] if explicit else []
    candidates.extend(
        [
            Path("C:/Program Files/Python313/Scripts/uv.exe"),
            Path("C:/Program Files/Python312/Scripts/uv.exe"),
        ]
    )
    located = shutil.which("uv.exe")
    if located:
        candidates.append(Path(located))
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate.resolve()
    run([sys.executable, "-m", "pip", "install", "--user", "uv"])
    located = shutil.which("uv.exe")
    if not located:
        raise SetupError("uv was installed but could not be discovered on PATH.")
    return Path(located).resolve()


def ensure_blender_mcp(pipeline_root: Path) -> Path:
    vendor_root = pipeline_root / "vendor" / "blender_mcp"
    project_root = vendor_root / "mcp"
    if not project_root.joinpath("pyproject.toml").exists():
        vendor_root.parent.mkdir(parents=True, exist_ok=True)
        if vendor_root.exists():
            raise SetupError(f"Existing Blender MCP checkout is incomplete: {vendor_root}")
        run(["git", "clone", "--filter=blob:none", BLENDER_MCP_REPOSITORY, str(vendor_root)])
        run(["git", "checkout", "--detach", BLENDER_MCP_COMMIT], cwd=vendor_root)
    head = run(["git", "rev-parse", "HEAD"], cwd=vendor_root).strip()
    if head.lower() != BLENDER_MCP_COMMIT.lower():
        raise SetupError(f"Blender MCP checkout is not locked to {BLENDER_MCP_COMMIT}: {head}")
    return project_root.resolve()


def ensure_io_pdx_mesh(pipeline_root: Path, blender_executable: Path) -> Path:
    version_output = run([str(blender_executable), "--version"])
    match = re.search(r"Blender (\d+)\.(\d+)", version_output)
    if not match:
        raise SetupError("Unable to determine Blender minor version for io_pdx_mesh installation.")
    minor = f"{match.group(1)}.{match.group(2)}"
    appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    extension_root = appdata / "Blender Foundation/Blender" / minor / "extensions/user_default"
    install_root = extension_root / "io_pdx_mesh"
    if not (install_root / "blender_manifest.toml").exists():
        cache = pipeline_root / "vendor/io_pdx_mesh/blender-io_pdx_mesh.zip"
        cache.parent.mkdir(parents=True, exist_ok=True)
        if not cache.exists() or hashlib.sha256(cache.read_bytes()).hexdigest().upper() != IO_PDX_SHA256:
            with urllib.request.urlopen(IO_PDX_URL, timeout=120) as response:
                cache.write_bytes(response.read())
        actual_hash = hashlib.sha256(cache.read_bytes()).hexdigest().upper()
        if actual_hash != IO_PDX_SHA256:
            raise SetupError(f"io_pdx_mesh archive checksum mismatch: {actual_hash}")
        extension_root.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(cache) as archive:
            archive.extractall(extension_root)
    if not (install_root / "blender_manifest.toml").exists():
        raise SetupError(f"io_pdx_mesh installation is incomplete: {install_root}")
    return install_root.resolve()


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
env_vars = ["MESHY_API_KEY", "MESHY_MCP_VERSION"]
startup_timeout_sec = 120.0
tool_timeout_sec = 1800.0
default_tools_approval_mode = "auto"

[mcp_servers.blender_lab]
enabled = true
required = true
command = "cmd.exe"
args = ["/d", "/c", "call", ".tools/3d_pipeline/wrappers/run_blender_lab_mcp.cmd"]
cwd = "."
env_vars = ["MESHY_API_KEY"]
startup_timeout_sec = 120.0
tool_timeout_sec = 1800.0
default_tools_approval_mode = "auto"
"""
    rendered = existing.rstrip() + "\n\n" + generated
    if re.search(r"<[^>]+>", rendered):
        raise SetupError("The generated Codex config still contains a placeholder.")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(rendered, encoding="utf-8", newline="\n")
    template = root / ".codex/3d_mcp_config.template.toml"
    if template.exists():
        template.unlink()
    return config_path.resolve()


def main() -> int:
    try:
        require_meshy_key()
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--quiet", action="store_true")
        args = parser.parse_args()
        root = repository_root()
        pipeline_root = root / ".tools/3d_pipeline"
        pipeline_root.joinpath("config").mkdir(parents=True, exist_ok=True)
        npx_executable = ensure_npx()
        blender_executable, blender_shortcut = find_blender()
        uv_executable = ensure_uv()
        blender_mcp_project = ensure_blender_mcp(pipeline_root)
        io_pdx_root = ensure_io_pdx_mesh(pipeline_root, blender_executable)
        config_path = materialize_config(root)
        runtime = {
            "schema_version": "1.0.0",
            "repository_root": root.as_posix(),
            "blender_executable": blender_executable.as_posix(),
            "blender_shortcut": blender_shortcut.as_posix(),
            "npx_executable": npx_executable.as_posix(),
            "uv_executable": uv_executable.as_posix(),
            "blender_mcp_project": blender_mcp_project.as_posix(),
            "io_pdx_mesh_root": io_pdx_root.as_posix(),
            "meshy_mcp_version": MESHY_VERSION,
            "config_path": config_path.as_posix(),
            "template_removed": True,
        }
        runtime_path = pipeline_root / "config/runtime.json"
        runtime_path.write_text(json.dumps(runtime, indent=2) + "\n", encoding="utf-8", newline="\n")
        if not args.quiet:
            print(json.dumps(runtime, indent=2))
        return 0
    except SetupError as exc:
        print(f"3D workflow setup blocked: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
