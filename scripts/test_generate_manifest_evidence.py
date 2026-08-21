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

    def test_legacy_manifest_removes_v2_validation_parameters(self) -> None:
        manifest = {
            "schema_version": "2.0.0",
            "components": [{"validation": [{"kind": "command", "parameters": {"arguments": ["--quiet"]}}]}],
        }
        legacy = json.loads(json.dumps(manifest))
        legacy["schema_version"] = "1.0.0"
        for component in legacy["components"]:
            for validation in component.get("validation", []):
                validation.pop("parameters", None)
        self.assertEqual(legacy["schema_version"], "1.0.0")
        self.assertNotIn("parameters", legacy["components"][0]["validation"][0])


if __name__ == "__main__":
    unittest.main()
