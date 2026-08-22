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

PIPELINE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PIPELINE_ROOT.parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib.mcp_stdio import call_stdio  # noqa: E402
from meshy_client import MeshyClient, _payload  # noqa: E402


def read_json(relative: str) -> dict[str, Any]:
    value = json.loads((PIPELINE_ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {relative}")
    return value


def adapter_tools() -> list[str]:
    source = (PIPELINE_ROOT / "adapter/hoi4_blender_mcp.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    return sorted(
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("hoi4_blender_")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-meshy", action="store_true")
    args = parser.parse_args()
    findings: list[str] = []

    try:
        contract = read_json("config/meshy_tool_contract.json")
        schema = read_json("config/meshy_tool_schema.lock.json")
        profiles = read_json("config/asset_profiles.json")
        if contract.get("provider_policy", {}).get("required_generation_model") != "meshy-7":
            findings.append("Meshy contract does not require meshy-7")
        image_contract = contract.get("required_tools", {}).get("meshy_image_to_3d", {})
        if image_contract.get("required_ai_model") != "meshy-7":
            findings.append("meshy_image_to_3d contract does not require meshy-7")
        image_schema = schema.get("required_tools", {}).get("meshy_image_to_3d", {})
        if image_schema.get("accepted_ai_models") != ["meshy-7"]:
            findings.append("locked live schema is not restricted to meshy-7")
        if not profiles.get("profiles"):
            findings.append("asset profile registry is empty")
        tools = adapter_tools()
        if "hoi4_blender_attach_rigid_weapon_from_checkpoint" not in tools:
            findings.append("rigid weapon attachment tool is missing")
        if len(tools) != len(set(tools)):
            findings.append("duplicate Blender adapter tool names")
    except (OSError, ValueError, json.JSONDecodeError, SyntaxError) as exc:
        findings.append(str(exc))
        tools = []

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
        if '"meshy-7"' not in live_schema:
            findings.append("live meshy_image_to_3d schema does not expose meshy-7")
        meshy = {
            "status": "probed",
            "tools": sorted(live),
            "balance": _payload(client.check_balance()),
        }

    result = {
        "status": "passed" if not findings else "blocked",
        "findings": findings,
        "adapter_tools": tools,
        "meshy": meshy,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
