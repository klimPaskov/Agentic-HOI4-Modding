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
# Reviewed 28-route contract retained by the published 4.0.3 release.
REQUIRED_TOOLS = tuple(sorted((
    "hoi4.reference_context", "hoi4.reference_search", "hoi4.reference_read",
    "hoi4.source_lookup", "hoi4.script_validate", "hoi4.error_log", "hoi4.mod_index",
    "hoi4.focus_inspect", "hoi4.focus_render", "hoi4.focus_rewrite",
    "hoi4.gui_inspect", "hoi4.gui_render", "hoi4.gui_rewrite",
    "hoi4.map_inspect", "hoi4.map_rewrite", "hoi4.event_inspect", "hoi4.event_render",
    "hoi4.tech_inspect", "hoi4.tech_render", "hoi4.probability_inspect",
    "hoi4.probability_analyze", "hoi4.impact_inspect", "hoi4.decision_inspect",
    "hoi4.mechanic_test", "hoi4.package_check", "hoi4.scenario_test",
    "hoi4.job_inspect", "hoi4.job_cancel",
)))


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
    modules = prefix.resolve(strict=True) / ("lib/node_modules" if platform == "linux" else "node_modules")
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
    if platform == "linux":
        constants["LINUX_PACKAGE_TREE_SHA256"] = constants.pop("PACKAGE_TREE_SHA256")
        constants["LINUX_PACKAGE_FILE_COUNT"] = constants.pop("PACKAGE_FILE_COUNT")
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
    parser.add_argument("--platform", choices=("windows", "linux"), help="Measured native installation platform; defaults to the current host")
    args = parser.parse_args()
    evidence = measure(args.prefix, args.integrity, args.version, args.platform)
    repin(evidence)
    print(json.dumps(evidence, sort_keys=True))


if __name__ == "__main__":
    main()
