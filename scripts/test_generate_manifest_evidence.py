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

    def test_empty_declared_tree_fails_closed(self) -> None:
        with self.assertRaisesRegex(SystemExit, "tree source has no files"):
            GENERATOR.git_evidence_for(
                {"source": {"kind": "tree", "path": ".qoder", "include": ["**"]}},
                {"present.txt": b"present"},
            )

    def test_canonical_manifest_uses_schema_two(self) -> None:
        manifest_path = SCRIPT.parents[1] / "hoi4-mod-setup.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        self.assertEqual(manifest["schema_version"], "2.0.0")

    def test_windows_mcp_bootstrap_is_optional_for_cross_platform_profiles(self) -> None:
        manifest_path = SCRIPT.parents[1] / "hoi4-mod-setup.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        components = {component["id"]: component for component in manifest["components"]}
        self.assertFalse(components["core.agents"]["optional"])
        self.assertTrue(components["mcp.hoi4_agent_tools.bootstrap"]["optional"])

    def test_published_setup_has_no_qoder_runtime(self) -> None:
        manifest_path = SCRIPT.parents[1] / "hoi4-mod-setup.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        component_ids = {component["id"] for component in manifest["components"]}
        profile_ids = {profile["id"] for profile in manifest["profiles"]}
        self.assertFalse(any(component_id.startswith("runtime.qoder.") for component_id in component_ids))
        self.assertNotIn("core_with_qoder", profile_ids)


if __name__ == "__main__":
    unittest.main()
