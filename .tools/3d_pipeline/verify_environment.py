"""Validate checked-in 3D contracts and optionally probe the live Meshy route."""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from pathlib import Path
from typing import Any


REQUIRED_KEY_MESSAGE = (
    "MESHY_API_KEY is missing or blank. Stop. Run this PowerShell command, then restart "
    "the shell or Codex:\n\n[Environment]::SetEnvironmentVariable(\n"
    '    "MESHY_API_KEY",\n    "msy_your_actual_key_here",\n    "User"\n)'
)

ADAPTER_STARTUP_TIMEOUT_SECONDS = 300
WINDOWS = os.name == "nt"

PIPELINE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PIPELINE_ROOT.parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib.generation import generation_problems, load_pricing
from lib.mcp_stdio import MCPRouteError, call_stdio  # noqa: E402
from meshy_client import MOTION_TOOL_ARGUMENTS, MeshyClient, _payload  # noqa: E402


def read_json(relative: str) -> dict[str, Any]:
    value = json.loads((PIPELINE_ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {relative}")
    return value


def registered_tools(source: str) -> list[str]:
    """Return adapter tool names, rejecting a name that is defined or registered twice."""

    names: list[str] = []
    for node in ast.parse(source).body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("hoi4_blender_"):
            continue
        registrations = sum(ast.unparse(item) == "mcp.tool()" for item in node.decorator_list)
        if node.name in names or registrations != 1:
            raise ValueError(f"Blender adapter tool is not registered exactly once: {node.name}")
        names.append(node.name)
    return sorted(names)


def contract_findings(contract: dict[str, Any], schema: dict[str, Any], profiles: dict[str, Any]) -> list[str]:
    """Findings for a contract, schema lock, price table or profile that disagree with each other."""

    findings: list[str] = []
    locked = {**schema.get("required_tools", {}), **schema.get("optional_tools", {})}
    capabilities = contract.get("optional_capabilities", {})
    named = set(contract.get("required_tools", {}))
    for capability in capabilities.values():
        named.update(capability.get("tool_names", []))
    for name in sorted(named - set(locked)):
        findings.append(f"contract names {name}, which the locked schema does not register")
    motion_names = set(capabilities.get("text_to_motion", {}).get("tool_names", []))
    if motion_names != set(MOTION_TOOL_ARGUMENTS):
        findings.append("the Text-to-Motion tool names in the contract differ from the ones the client calls")
    pricing = load_pricing()
    if not pricing.get("source_url") or not pricing.get("retrieved"):
        findings.append("config/meshy_pricing.json must name its source_url and retrieved date")
    for name, profile in profiles.get("profiles", {}).items():
        findings.extend(f"profile {name}: {problem}" for problem in generation_problems(profile.get("generation")))
    return findings


def adapter_tools() -> list[str]:
    return registered_tools((PIPELINE_ROOT / "adapter/hoi4_blender_mcp.py").read_text(encoding="utf-8"))


def probe_blender_adapter(
    repo_root: Path,
    expected_tools: list[str],
    *,
    required: bool = False,
    timeout_seconds: int = ADAPTER_STARTUP_TIMEOUT_SECONDS,
) -> tuple[dict[str, Any], list[str]]:
    """Start the materialized adapter through its wrapper and list the tools it serves."""

    pipeline_root = repo_root.resolve() / ".tools/3d_pipeline"
    config = pipeline_root / "config/blender_hoi4_adapter.json"
    wrapper = pipeline_root / "wrappers/run_blender_hoi4_adapter.cmd"
    if not config.is_file():
        finding = "Blender adapter is not materialized; run bootstrap_3d_workflow.py first"
        return {"status": "not_materialized"}, [finding] if required else []
    if not WINDOWS:
        finding = "Blender adapter startup probe requires the Windows wrapper"
        return {"status": "unsupported_platform"}, [finding] if required else []
    command = ["cmd.exe", "/d", "/c", "call", str(wrapper.resolve())]
    try:
        listed = call_stdio(command, list_tools=True, timeout_seconds=timeout_seconds, cwd=repo_root.resolve())
    except MCPRouteError as exc:
        return {"status": "failed"}, [f"Blender adapter failed to start: {exc}"]
    served = sorted(str(item.get("name")) for item in listed.get("tools", []))
    if served != sorted(expected_tools):
        missing = sorted(set(expected_tools) - set(served))
        unexpected = sorted(set(served) - set(expected_tools))
        return {"status": "failed", "tools": served}, [
            f"Blender adapter served tools differ from its source: missing {missing}, unexpected {unexpected}"
        ]
    return {"status": "probed", "tools": served}, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-meshy", action="store_true")
    parser.add_argument(
        "--probe-adapter",
        action="store_true",
        help="Fail when the Blender adapter cannot be started; it is probed whenever materialized.",
    )
    args = parser.parse_args()
    findings: list[str] = []

    try:
        contract = read_json("config/meshy_tool_contract.json")
        schema = read_json("config/meshy_tool_schema.lock.json")
        profiles = read_json("config/asset_profiles.json")
        findings.extend(contract_findings(contract, schema, profiles))
        if not profiles.get("profiles"):
            findings.append("asset profile registry is empty")
        tools = adapter_tools()
        if "hoi4_blender_attach_rigid_weapon_from_checkpoint" not in tools:
            findings.append("rigid weapon attachment tool is missing")
    except (OSError, ValueError, json.JSONDecodeError, SyntaxError) as exc:
        findings.append(str(exc))
        tools = []

    if tools:
        blender_adapter, adapter_findings = probe_blender_adapter(
            REPO_ROOT, tools, required=args.probe_adapter
        )
        findings.extend(adapter_findings)
    else:
        blender_adapter = {"status": "not_probed"}

    meshy: dict[str, Any] = {"status": "not_probed"}
    if args.probe_meshy:
        if not os.environ.get("MESHY_API_KEY", "").strip():
            raise RuntimeError(REQUIRED_KEY_MESSAGE)
        client = MeshyClient(REPO_ROOT)
        listed = call_stdio(client._command(), list_tools=True, timeout_seconds=300, cwd=REPO_ROOT)
        live = {item.get("name"): item for item in listed.get("tools", [])}
        required = set(contract.get("required_tools", {}))
        missing = sorted(required - set(live))
        live_schema = json.dumps(live.get("meshy_image_to_3d", {}).get("inputSchema", {}), sort_keys=True)
        if missing:
            findings.append(f"live Meshy route is missing tools: {missing}")
        for name, profile in profiles.get("profiles", {}).items():
            model = profile.get("generation", {}).get("ai_model")
            if f'"{model}"' not in live_schema:
                findings.append(f"live meshy_image_to_3d schema does not expose {model}, the model of profile {name}")
        meshy = {
            "status": "probed",
            "tools": sorted(live),
            "balance": _payload(client.check_balance()),
        }

    result = {
        "status": "passed" if not findings else "blocked",
        "findings": findings,
        "adapter_tools": tools,
        "blender_adapter": blender_adapter,
        "meshy": meshy,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
