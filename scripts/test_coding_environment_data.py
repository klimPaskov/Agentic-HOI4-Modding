"""Contract tests for the source-owned coding-client declarations."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and older
    tomllib = None

SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[1]
sys.path.insert(0, str(SCRIPT.parent))

import coding_environment_data as data  # noqa: E402


def published() -> dict:
    return json.loads((ROOT / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8-sig"))


class CodingEnvironmentTableTests(unittest.TestCase):
    def test_table_is_unique_bounded_and_honest_about_mcp(self) -> None:
        table = data.build_coding_environment_table()
        ids = [entry["id"] for entry in table]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids[0], "claude_code")
        self.assertEqual(sum(1 for entry in table if entry.get("default_primary")), 1)
        for entry in table:
            self.assertLessEqual(len(entry["display_name"]), 64, entry["id"])
            self.assertLessEqual(len(entry["description"]), 300, entry["id"])
            self.assertIn(entry["mcp_support"], {"project", "manual", "none"})
            if entry["mcp_support"] == "project":
                self.assertEqual(set(entry["mcp_registration"]), {"component_id", "path", "format"})
            else:
                self.assertNotIn("mcp_registration", entry)
                self.assertTrue(entry["documentation_url"].startswith("https://"), entry["id"])
                self.assertNotIn("and MCP", entry["description"])
        self.assertTrue({"gemini_cli", "grok_build", "github_copilot", "antigravity", "kilo_code", "kiro", "qwen_code", "cline", "devin_desktop", "augment", "continue", "aider"}.issubset(ids))
        self.assertNotIn("roo_code", ids)

    def test_every_client_has_a_complete_package_and_matching_registration(self) -> None:
        manifest = published()
        components = {component["id"]: component for component in manifest["components"]}
        self.assertEqual(manifest["coding_environments"], data.build_coding_environment_table())
        for entry in manifest["coding_environments"]:
            owned = [component for component in components.values() if component.get("coding_environment") == entry["id"]]
            self.assertTrue(any(not component["optional"] for component in owned), entry["id"])
            registration = entry.get("mcp_registration")
            if registration:
                owner = components[registration["component_id"]]
                self.assertEqual(owner["coding_environment"], entry["id"])
                self.assertEqual(owner["destination"]["path"], registration["path"])
                self.assertEqual(owner["source"]["path"], registration["path"])
        for component_id in data.REMOVED_COMPONENTS:
            self.assertNotIn(component_id, components)
        self.assertEqual(components["runtime.augment"]["platforms"], ["macos", "linux"])

    def test_generated_declarations_are_reproducible_from_the_published_manifest(self) -> None:
        manifest = published()
        components = {component["id"]: component for component in manifest["components"]}
        for expected in data.build_coding_environment_components(manifest["components"]):
            actual = dict(components[expected["id"]])
            actual.pop("expected_files")
            expected.pop("expected_files")
            self.assertEqual(actual, expected, expected["id"])

    def test_destinations_are_never_installed_by_two_components(self) -> None:
        manifest = published()
        owners: dict = {}
        for component in manifest["components"]:
            for file in component["expected_files"]:
                source = component["source"]
                if source["kind"] == "file":
                    destination = component["destination"]["path"]
                else:
                    relative = file["path"][len(source["path"]):].lstrip("/")
                    destination = component["destination"]["path"].rstrip("/") + "/" + relative
                previous = owners.setdefault(destination, component["id"])
                self.assertEqual(previous, component["id"], destination)

    def test_skill_copies_and_shared_copy_cover_the_canonical_library(self) -> None:
        manifest = published()
        components = {component["id"]: component for component in manifest["components"]}
        canonical = components["runtime.codex.skills"]
        self.assertEqual(canonical["shared_coding_environments"], data.SHARED_SKILLS_CLIENTS)
        for environment, prefix, destination, _label in data.SKILL_COPIES:
            copy = components[f"runtime.{prefix}.skills"]
            self.assertEqual(copy["coding_environment"], environment)
            self.assertEqual(copy["source"], canonical["source"])
            self.assertEqual(copy["destination"]["path"], destination)
            self.assertEqual([file["path"] for file in copy["expected_files"]], [file["path"] for file in canonical["expected_files"]])
            for suffix in ("portrait_skill", "super_events_skill", "live_tools_skill"):
                optional = components[f"runtime.{prefix}.{suffix}"]
                self.assertTrue(optional["optional"])
                self.assertTrue(optional["destination"]["path"].startswith(destination))
                self.assertIn(f"runtime.{prefix}.skills", optional["dependencies"])


class ClientFileTests(unittest.TestCase):
    def test_agent_projections_cover_every_canonical_agent(self) -> None:
        names = sorted(path.name for path in (ROOT / ".claude" / "agents").glob("*.md"))
        for _environment, _prefix, folder, label, _platforms in data.AGENT_PROJECTIONS:
            projected = sorted(path.name for path in (ROOT / folder / "agents").glob("*.md"))
            self.assertEqual(projected, names, label)
            self.assertTrue((ROOT / folder / "agent-map.md").is_file(), label)
            sample = (ROOT / folder / "agents" / "hoi4-repo-explorer.md").read_text(encoding="utf-8")
            self.assertTrue(sample.startswith("---\n"), label)
            self.assertIn("by .tools/sync/sync_agents.py", sample)
            self.assertNotIn("CLAUDE.md", sample.split("\n---\n", 1)[1])

    def test_mcp_files_register_only_the_shared_placeholder_route(self) -> None:
        for entry in data.build_coding_environment_table():
            registration = entry.get("mcp_registration")
            if not registration:
                continue
            path = ROOT / registration["path"]
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"(?i)api[_-]?key|token|secret|[A-Za-z]:[\\/]Users")
            fmt = registration["format"]
            if fmt == "toml_mcp_servers":
                if tomllib is None:
                    continue
                value = tomllib.loads(text)
                route = value["mcp_servers"]["hoi4_agent_tools"]
                if registration["path"] == ".grok/config.toml":
                    self.assertEqual(set(value), {"mcp_servers"})
            else:
                value = json.loads(text)
                key = {"json_mcp_servers": "mcpServers", "vscode_servers": "servers", "local_command_array": "mcp"}[fmt]
                route = value[key]["hoi4_agent_tools"]
            if fmt == "local_command_array":
                self.assertEqual(route["type"], "local")
                self.assertEqual(route["command"], ["hoi4-agent-tools.cmd"])
            else:
                self.assertEqual(route["command"], "hoi4-agent-tools.cmd")
                self.assertEqual(route.get("args", []), [])
            if fmt == "vscode_servers":
                self.assertEqual(route["type"], "stdio")

    def test_instruction_pointers_lead_to_the_shared_project_instructions(self) -> None:
        self.assertIn("@./AGENTS.md", (ROOT / "GEMINI_template.md").read_text(encoding="utf-8"))
        for path in (".github/instructions/hoi4-mod-setup.instructions.md", ".clinerules/hoi4-mod-setup.md", ".continue/rules/hoi4-mod-setup.md"):
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn("AGENTS.md", text, path)
            self.assertIn(".claude/skills/", text, path)
        self.assertIn('applyTo: "**"', (ROOT / ".github/instructions/hoi4-mod-setup.instructions.md").read_text(encoding="utf-8"))
        self.assertIn("alwaysApply: true", (ROOT / ".continue/rules/hoi4-mod-setup.md").read_text(encoding="utf-8"))
        self.assertIn("- AGENTS.md", (ROOT / ".aider.conf.yml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
