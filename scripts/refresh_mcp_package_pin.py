"""Repin MCP evidence from an explicitly selected clean, reviewed installation.

This measures package bytes, never installs or publishes anything, and never
regenerates Git-blob manifest evidence. Commit the changed source first, then
run generate_manifest_evidence.py at that exact commit.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / ".tools/mcp/bootstrap_hoi4_agent_tools.py"
MANIFEST = ROOT / "hoi4-mod-setup.manifest.json"
# Reviewed 39-route contract of 4.13.0: the 34 routes of 4.11.0 and 4.12.0 plus
# hoi4.explain_error, hoi4.mod_health, hoi4.script_guard, hoi4.localisation_write and
# hoi4.compat_check. The server lists it when HOI4_AGENT_TOOLS_PROFILES=all.
ROUTE_CONTRACT = tuple(sorted((
    "hoi4.reference_context", "hoi4.reference_search", "hoi4.reference_read",
    "hoi4.source_lookup", "hoi4.script_validate", "hoi4.error_log", "hoi4.mod_index",
    "hoi4.focus_inspect", "hoi4.focus_render", "hoi4.focus_rewrite",
    "hoi4.gui_inspect", "hoi4.gui_render", "hoi4.gui_rewrite",
    "hoi4.map_inspect", "hoi4.map_rewrite", "hoi4.event_inspect", "hoi4.event_render",
    "hoi4.tech_inspect", "hoi4.tech_render", "hoi4.probability_inspect",
    "hoi4.probability_analyze", "hoi4.impact_inspect", "hoi4.decision_inspect",
    "hoi4.idea_inspect", "hoi4.localisation_inspect",
    "hoi4.asset_inspect", "hoi4.system_inspect", "hoi4.unit_inspect", "hoi4.skill",
    "hoi4.mechanic_test", "hoi4.package_check", "hoi4.scenario_test",
    "hoi4.job_inspect", "hoi4.job_cancel",
    "hoi4.explain_error", "hoi4.mod_health", "hoi4.script_guard",
    "hoi4.localisation_write", "hoi4.compat_check",
)))
# The core profile, which a stdio server lists when nothing chooses profiles (4.13.0, R-4).
# HOI4 Mod Setup's health check starts the server with a cleared environment, so the manifest
# requires only these; the kit's client registrations set HOI4_AGENT_TOOLS_PROFILES=all.
REQUIRED_TOOLS = tuple(sorted((
    "hoi4.skill", "hoi4.reference_search", "hoi4.reference_read", "hoi4.reference_context",
    "hoi4.source_lookup", "hoi4.script_validate", "hoi4.script_guard", "hoi4.error_log",
    "hoi4.explain_error", "hoi4.mod_health", "hoi4.mod_index", "hoi4.localisation_inspect",
    "hoi4.localisation_write",
)))
PROFILES_ENV = "HOI4_AGENT_TOOLS_PROFILES"


def list_routes(command: list[str], profiles: str | None, timeout: float = 120.0) -> list[str]:
    """Start the server over stdio and return the tool names its tools/list answers.

    The child gets a scratch home so it never reads the maintainer's own configuration, and the
    profile choice (or none) is the only variable that picks the listing.
    """
    import os
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as scratch:
        # The server starts only inside a mod, so the child runs in a scratch mod folder.
        # macOS keeps temporary folders under the /var -> /private/var link, which the server refuses.
        scratch = str(Path(scratch).resolve())
        mod = Path(scratch) / "mod"
        mod.mkdir()
        (mod / "descriptor.mod").write_bytes(b'name="route-contract-check"\nversion="1.0"\nsupported_version="1.*"\n')
        env = {key: os.environ[key] for key in ("SystemRoot", "PATH", "PATHEXT", "TEMP", "TMP") if key in os.environ}
        for key in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
            env[key] = scratch
        if profiles is not None:
            env[PROFILES_ENV] = profiles
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                "protocolVersion": "2025-06-18", "capabilities": {},
                "clientInfo": {"name": "route-contract-check", "version": "1.0.0"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        ]
        payload = "".join(json.dumps(item) + "\n" for item in requests)
        # The server answers requests as it reads them and exits when stdin closes.
        done = subprocess.run(command, input=payload, capture_output=True, text=True, encoding="utf-8",
                              env=env, cwd=mod, timeout=timeout, check=False)
    for line in done.stdout.splitlines():
        try:
            message = json.loads(line)
        except ValueError:
            continue
        if message.get("id") == 2 and isinstance(message.get("result"), dict):
            return sorted(tool["name"] for tool in message["result"]["tools"])
    raise ValueError("The server answered no tools/list result.")


def check_routes(command: list[str]) -> None:
    """Assert the default listing is the core profile and the all-profiles listing is the contract."""
    core = list_routes(command, None)
    if core != list(REQUIRED_TOOLS):
        raise ValueError(f"The default tools/list is not the core profile: {core}")
    everything = list_routes(command, "all")
    if everything != list(ROUTE_CONTRACT):
        missing = sorted(set(ROUTE_CONTRACT) - set(everything))
        extra = sorted(set(everything) - set(ROUTE_CONTRACT))
        raise ValueError(f"The all-profiles tools/list differs from the reviewed contract: missing {missing}, extra {extra}")


def measure(prefix: Path, integrity: str, version: str | None = None, platform: str | None = None) -> dict:
    if not integrity.startswith("sha512-"):
        raise ValueError("Integrity must be an exact SHA-512 npm SRI value.")
    try:
        raw = base64.b64decode(integrity[7:], validate=True)
    except ValueError as exc:
        raise ValueError("Integrity must be an exact SHA-512 npm SRI value.") from exc
    if len(raw) != 64 or base64.b64encode(raw).decode("ascii") != integrity[7:]:
        raise ValueError("Integrity must be an exact SHA-512 npm SRI value.")
    spec = importlib.util.spec_from_file_location("reviewed_mcp_bootstrap", BOOTSTRAP)
    assert spec and spec.loader
    bootstrap = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bootstrap)
    version = version or bootstrap.PACKAGE_VERSION
    if re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        raise ValueError("Select an exact published package version.")
    platform = platform or bootstrap.platform_name()
    platform_pin = bootstrap.platform_evidence(platform)
    modules = prefix.resolve(strict=True) / ("lib/node_modules" if platform in {"linux", "macos"} else "node_modules")
    package_root = modules / bootstrap.PACKAGE_NAME
    if modules.is_symlink() or package_root.is_symlink():
        raise ValueError("The clean installation must not use linked package directories.")
    package = bootstrap.read_json(package_root / "package.json", 1024 * 1024)
    if package.get("name") != "hoi4-agent-tools" or package.get("version") != version:
        raise ValueError(f"The clean installation must contain hoi4-agent-tools@{version}.")
    # npm can omit this optional global lock for Windows shrinkwrapped installs.
    # Its absence never skips the full package-tree and runtime measurements.
    lock_path = modules / ".package-lock.json"
    if lock_path.exists():
        lock = bootstrap.read_json(lock_path, 16 * 1024 * 1024)
        packages = lock.get("packages")
        installed = packages.get("node_modules/hoi4-agent-tools") if isinstance(packages, dict) else None
        if not isinstance(installed, dict) or installed.get("integrity") != integrity:
            raise ValueError("The clean installation lock must retain the selected integrity.")
    tree_digest, count = bootstrap.package_tree_sha256(package_root, platform_pin["package_symlinks"])
    entry = package_root / bootstrap.RUNTIME_ENTRY
    if not entry.is_file() or entry.stat().st_size > bootstrap.MAX_PACKAGE_FILE_BYTES:
        raise ValueError("The measured runtime entry is missing or oversized.")
    return {
        "package_name": "hoi4-agent-tools", "package_version": version,
        "package_integrity": integrity, "package_tree_sha256": tree_digest,
        "package_file_count": count, "runtime_entry": bootstrap.RUNTIME_ENTRY,
        "runtime_entry_sha256": hashlib.sha256(entry.read_bytes()).hexdigest(),
        "runtime_entry_size": entry.stat().st_size, "required_tools": list(REQUIRED_TOOLS),
        "platform": platform, "package_symlinks": platform_pin["package_symlinks"],
    }


def repin(evidence: dict, bootstrap_path: Path = BOOTSTRAP, manifest_path: Path = MANIFEST) -> None:
    source = bootstrap_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    constants = {
        "PACKAGE_VERSION": "package_version", "PACKAGE_INTEGRITY": "package_integrity",
        "PACKAGE_TREE_SHA256": "package_tree_sha256", "PACKAGE_FILE_COUNT": "package_file_count",
        "RUNTIME_ENTRY": "runtime_entry", "RUNTIME_ENTRY_SHA256": "runtime_entry_sha256",
        "RUNTIME_ENTRY_SIZE": "runtime_entry_size",
    }
    platform = evidence.get("platform", "windows")
    if platform in {"linux", "macos"}:
        constants[f"{platform.upper()}_PACKAGE_TREE_SHA256"] = constants.pop("PACKAGE_TREE_SHA256")
        constants[f"{platform.upper()}_PACKAGE_FILE_COUNT"] = constants.pop("PACKAGE_FILE_COUNT")
    elif platform != "windows":
        raise ValueError("The MCP platform has no reviewed package evidence.")
    for constant, key in constants.items():
        source, count = re.subn(rf"^{constant} = .+$", f"{constant} = {json.dumps(evidence[key])}", source, flags=re.MULTILINE)
        if count != 1:
            raise ValueError(f"Expected exactly one bootstrap constant: {constant}")
    component = next(item for item in manifest["components"] if item["id"] == "mcp.hoi4_agent_tools")
    health = next(rule for rule in component["validation"] if rule["id"] == "mcp.hoi4.health")
    health["parameters"].update({key: value for key, value in evidence.items() if key not in {"platform", "package_symlinks", "package_tree_sha256", "package_file_count"}})
    platform_pin = {key: evidence[key] for key in ("package_tree_sha256", "package_file_count", "runtime_entry_sha256", "runtime_entry_size")}
    platform_pin["package_symlinks"] = evidence.get("package_symlinks", {})
    health["parameters"].setdefault("platform_pins", {})[platform] = platform_pin
    if platform == "windows":
        health["parameters"].update({key: evidence[key] for key in ("package_tree_sha256", "package_file_count")})
    for tool in component.get("required_tools", []):
        if isinstance(tool, dict) and tool.get("id") == "hoi4-agent-tools.cmd":
            tool["version"] = evidence["package_version"]
    # Finish all structure/constant validation before writing either owned file.
    bootstrap_path.write_bytes(source.encode("utf-8"))
    manifest_path.write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=Path, required=True, help="Explicit clean npm global install prefix")
    parser.add_argument("--integrity", required=True, help="Reviewed published npm dist.integrity")
    parser.add_argument("--version", help="Exact reviewed public version; defaults to the current bootstrap pin")
    parser.add_argument("--platform", choices=("windows", "linux", "macos"), help="Measured native installation platform; defaults to the current host")
    parser.add_argument("--skip-route-check", action="store_true", help="Skip the live tools/list check (the check needs Node on PATH)")
    args = parser.parse_args()
    evidence = measure(args.prefix, args.integrity, args.version, args.platform)
    if not args.skip_route_check:
        package = args.prefix.resolve(strict=True) / ("lib/node_modules" if evidence["platform"] in {"linux", "macos"} else "node_modules") / "hoi4-agent-tools"
        check_routes(["node", str(package / evidence["runtime_entry"])])
    repin(evidence)
    print(json.dumps(evidence, sort_keys=True))


if __name__ == "__main__":
    main()
