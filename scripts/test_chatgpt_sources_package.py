"""Install the manifest-declared tool into a tiny mod and exercise its CLI."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

import generate_manifest_evidence as generator

ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.mod = self.base / "tiny-mod"
        self.mod.mkdir()
        manifest = json.loads((ROOT / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8"))
        component = next(item for item in manifest["components"] if item["id"] == "runtime.chatgpt_sources")
        # Optional and unchecked by default: no profile installs the packager.
        self.assertTrue(component["optional"])
        for profile in manifest["profiles"]:
            self.assertNotIn(component["id"], profile["components"])
        shared = next(item for item in manifest["components"] if item["id"] == "runtime.agent_sync")
        self.assertFalse(any("package_chatgpt" in entry["path"] for entry in shared["expected_files"]))
        # Same selected-source rules used to publish the install inventory.
        snapshot = {entry["path"]: (ROOT / entry["path"]).read_bytes() for entry in component["expected_files"]}
        for entry in generator.git_evidence_for(component, snapshot):
            relative = Path(entry["path"]).relative_to(component["source"]["path"])
            destination = self.mod / component["destination"]["path"] / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(snapshot[entry["path"]])
        self.tool = self.mod / ".tools/package_chatgpt_project_sources.py"
        self.assertTrue(self.tool.is_file())
        self.assertTrue((self.mod / ".tools/package_chatgpt_project_sources.bat").is_file())
        for relative, text in {"AGENTS.md": "Project guidance", "README.md": "Tiny mod", "common/ideas/tiny.txt": "ideas = {}", ".claude/skills/tiny/SKILL.md": "Skill", ".claude/agents/reviewer.md": "Agent", "docs/secret-notes.md": "excluded", ".env": "excluded"}.items():
            path = self.mod / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def run_tool(self, *args):
        return subprocess.run([sys.executable, "-B", str(self.tool), *map(str, args)], cwd=self.base,
                              capture_output=True, text=True)

    def test_installed_tool_builds_curated_loose_files_and_verified_archives(self):
        output = self.base / "bundle"
        result = self.run_tool("--output", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(output / "all-project-sources.zip") as bundle:
            self.assertIn("AGENTS.md", bundle.namelist())
            self.assertIn("common%2Fideas%2Ftiny.txt", bundle.namelist())
            self.assertIn(".claude%2Fskills%2Ftiny%2FSKILL.md", bundle.namelist())
            self.assertIn("subagents.zip", bundle.namelist())
            self.assertFalse(any("secret" in name or ".env" in name for name in bundle.namelist()))
            for name in bundle.namelist():
                self.assertEqual(bundle.read(name), (output / name).read_bytes())
        before = (output / "AGENTS.md").read_bytes()
        self.assertNotEqual(self.run_tool("--output", output).returncode, 0)
        self.assertEqual((output / "AGENTS.md").read_bytes(), before)

    def test_config_and_dry_run_do_not_write(self):
        config = self.base / "selection.json"
        config.write_text(json.dumps({"include": ["README.md", "common/**/*.txt"], "exclude": ["common/**"]}))
        output = self.base / "preview"
        result = self.run_tool("--config", config, "--output", output, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("README.md", result.stdout)
        self.assertNotIn("tiny.txt", result.stdout)
        self.assertFalse(output.exists())

    def test_unsafe_outputs_empty_selection_and_linked_sources_fail(self):
        self.assertNotEqual(self.run_tool("--output", self.mod / "bundle").returncode, 0)
        self.assertNotEqual(self.run_tool("--output", self.base / "empty", "--include", "absent.md").returncode, 0)
        outside = self.base / "outside.md"
        outside.write_text("private")
        link = self.mod / "linked.md"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("Creating symlinks requires OS permission")
        self.assertNotEqual(self.run_tool("--output", self.base / "links", "--include", "*.md").returncode, 0)


if __name__ == "__main__":
    unittest.main()
