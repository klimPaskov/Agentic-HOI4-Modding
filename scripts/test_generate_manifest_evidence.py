from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
import json
from pathlib import Path


SCRIPT = Path(__file__).with_name("generate_manifest_evidence.py")
SPEC = importlib.util.spec_from_file_location("manifest_generator", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)


class ManifestGeneratorTests(unittest.TestCase):
    def repository(self) -> tuple[tempfile.TemporaryDirectory[str], Path, str]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
        (root / ".agents/skills/example").mkdir(parents=True)
        (root / ".agents/skills/example/SKILL.md").write_text("example\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
        revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        return temporary, root, revision

    def test_tree_evidence_automatically_includes_new_declared_files(self) -> None:
        temporary, root, revision = self.repository()
        self.addCleanup(temporary.cleanup)
        evidence = GENERATOR.git_evidence_for(
            {"source": {"kind": "tree", "path": ".agents/skills", "include": ["**"]}},
            GENERATOR.git_snapshot(root, revision),
        )
        self.assertEqual([item["path"] for item in evidence], [".agents/skills/example/SKILL.md"])

    def test_revision_must_be_an_exact_commit(self) -> None:
        temporary, root, _revision = self.repository()
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(SystemExit, "exact lowercase 40-character commit"):
            GENERATOR.git_snapshot(root, "HEAD")

    def test_missing_declared_file_fails_closed(self) -> None:
        with self.assertRaisesRegex(SystemExit, "missing at the selected revision"):
            GENERATOR.git_evidence_for(
                {"source": {"kind": "file", "path": "missing.txt"}},
                {"present.txt": b"present"},
            )

    def test_unresolved_git_lfs_pointer_fails_closed(self) -> None:
        pointer = (
            b"version https://git-lfs.github.com/spec/v1\n"
            + b"oid sha256:" + b"0" * 64 + b"\nsize 11604\n"
        )
        with self.assertRaisesRegex(SystemExit, "unresolved Git LFS pointer"):
            GENERATOR.git_evidence_for(
                {"source": {"kind": "tree", "path": "paradox_wiki", "include": ["**"]}},
                {"paradox_wiki/media/image.jpg": pointer, "paradox_wiki/page.md": b"page"},
            )

    def test_empty_declared_tree_fails_closed(self) -> None:
        with self.assertRaisesRegex(SystemExit, "tree source has no files"):
            GENERATOR.git_evidence_for(
                {"source": {"kind": "tree", "path": ".qoder", "include": ["**"]}},
                {"present.txt": b"present"},
            )

    def test_canonical_manifest_uses_schema_four_and_declares_image_providers(self) -> None:
        manifest_path = SCRIPT.parents[1] / "hoi4-mod-setup.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        self.assertEqual(manifest["schema_version"].split(".")[0], "4")
        self.assertEqual(manifest["image_generation"]["default_provider"], "gptimage")
        self.assertEqual(manifest["image_generation"], GENERATOR.build_image_generation_table(manifest_path.parent))
        components = {component["id"]: component for component in manifest["components"]}
        self.assertIn("imagegen.gptimage", components)
        self.assertTrue(components["imagegen.gptimage"]["optional"])
        provider_ids = {provider["id"] for provider in manifest["image_generation"]["providers"]}
        self.assertTrue({"gptimage", "openai_api", "gemini_api", "fal_ai", "replicate", "black_forest_labs", "stability_ai", "ideogram", "recraft", "leonardo", "adobe_firefly", "xai_grok", "together_ai", "openrouter", "comfyui_local", "automatic1111_local", "forge_local", "codex_native", "vertex_imagen", "microsoft_foundry", "aws_bedrock", "huggingface_inference", "midjourney_manual", "none"}.issubset(provider_ids))
        declared = [environment["id"] for environment in manifest["coding_environments"]]
        self.assertEqual(declared[0], "claude_code")
        self.assertTrue(manifest["coding_environments"][0]["default_primary"])
        self.assertEqual(sum(1 for environment in manifest["coding_environments"] if environment.get("default_primary")), 1)

    def test_windows_mcp_bootstrap_is_optional_for_cross_platform_profiles(self) -> None:
        manifest_path = SCRIPT.parents[1] / "hoi4-mod-setup.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        components = {component["id"]: component for component in manifest["components"]}
        self.assertFalse(components["core.agents"]["optional"])
        self.assertTrue(components["mcp.hoi4_agent_tools.bootstrap"]["optional"])

    def test_published_setup_declares_all_coding_environments(self) -> None:
        manifest_path = SCRIPT.parents[1] / "hoi4-mod-setup.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        components = {component["id"]: component for component in manifest["components"]}
        environments = {
            component["coding_environment"]
            for component in manifest["components"]
            if "coding_environment" in component
        }
        self.assertEqual(environments, {environment["id"] for environment in manifest["coding_environments"]})
        for environment, component_id in {
            "codex": "codex.config",
            "claude_code": "runtime.claude",
            "cursor": "runtime.cursor",
            "qoder": "runtime.qoder",
            "opencode": "runtime.opencode",
        }.items():
            self.assertEqual(components[component_id]["coding_environment"], environment)
        self.assertNotIn("coding_environment", components["mcp.hoi4_agent_tools"])
        self.assertEqual(components["mcp.hoi4_agent_tools"]["category"], "mcp")

    def test_profiles_keep_environment_selection_composable(self) -> None:
        manifest_path = SCRIPT.parents[1] / "hoi4-mod-setup.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        components = {component["id"]: component for component in manifest["components"]}
        required = {"core.agents", "core.claude.instructions", "core.skills", "core.subagents", "runtime.agent_sync"}
        for profile in manifest["profiles"]:
            self.assertTrue(required.issubset(profile["components"]))
            environment_components = [
                component_id
                for component_id in profile["components"]
                if components[component_id].get("coding_environment")
            ]
            self.assertEqual(environment_components, [])

    def test_claude_files_are_canonical_and_other_runtimes_are_projections(self) -> None:
        manifest_path = SCRIPT.parents[1] / "hoi4-mod-setup.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        components = {component["id"]: component for component in manifest["components"]}
        self.assertEqual(components["core.skills"]["destination"]["path"], ".claude/skills/")
        self.assertEqual(components["core.subagents"]["destination"]["path"], ".claude/agents/")
        self.assertFalse(components["core.claude.instructions"]["optional"])
        self.assertNotIn("coding_environment", components["core.claude.instructions"])
        self.assertEqual(components["runtime.codex.skills"]["destination"]["path"], ".agents/skills/")
        self.assertEqual(components["runtime.codex.skills"]["source"], components["core.skills"]["source"])
        for runtime in ("cursor", "qoder", "opencode"):
            base = components[f"runtime.{runtime}"]
            excluded = set(base["source"].get("exclude", []))
            agent_prefix = "agent" if runtime == "opencode" else "agents"
            self.assertIn(f"{agent_prefix}/hoi4-portrait-creator.md", excluded)
            self.assertIn(f"{agent_prefix}/hoi4-super-event-*.md", excluded)
        for runtime in ("cursor", "qoder", "opencode", "codex"):
            portrait = components[f"runtime.{runtime}.portrait_agent"]
            super_events = components[f"runtime.{runtime}.super_event_agents"]
            self.assertTrue(portrait["optional"])
            self.assertTrue(super_events["optional"])
            self.assertIn("workflow.portraits.subagent", portrait["dependencies"])
            self.assertIn("workflow.super_events.subagents", super_events["dependencies"])
        for component in manifest["components"]:
            source = component["source"].get("path", "")
            self.assertFalse(source.startswith(".agents/"), component["id"])
            if component["destination"]["path"].startswith(".agents/skills"):
                self.assertEqual(component.get("coding_environment"), "codex", component["id"])

    def test_windows_mcp_registration_is_not_claimed_cross_platform(self) -> None:
        root = SCRIPT.parents[1]
        manifest = json.loads(
            (root / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8-sig")
        )
        components = {component["id"]: component for component in manifest["components"]}
        for runtime in ("claude", "cursor", "qoder", "opencode"):
            component = components[f"runtime.{runtime}.mcp"]
            self.assertEqual(component["platforms"], ["windows"])
            self.assertTrue(component["optional"])
            self.assertIn("mcp.hoi4_agent_tools", component["dependencies"])
        opencode = json.loads((root / "opencode.json").read_text(encoding="utf-8"))
        self.assertNotIn("mcp", opencode)
        qoder = json.loads((root / ".qoder/settings.json").read_text(encoding="utf-8"))
        self.assertNotIn("mcpServers", qoder)


if __name__ == "__main__":
    unittest.main()
