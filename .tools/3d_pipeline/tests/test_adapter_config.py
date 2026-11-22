"""The Blender adapter client names the fix when a worktree has no adapter config, or one copied from another worktree."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from blender_client import BlenderAdapterClient


class AdapterConfigTests(unittest.TestCase):
    def client(self, folder: Path) -> BlenderAdapterClient:
        wrapper = folder / ".tools/3d_pipeline/wrappers/run_blender_hoi4_adapter.cmd"
        wrapper.parent.mkdir(parents=True)
        wrapper.write_text("", encoding="utf-8")
        (folder / ".tools/3d_pipeline/config").mkdir(parents=True)
        return BlenderAdapterClient(folder)

    def write(self, folder: Path, root: str) -> None:
        path = folder / ".tools/3d_pipeline/config/blender_hoi4_adapter.json"
        path.write_text(json.dumps({"repository_root": root, "job_root": root + "/docs/assets"}), encoding="utf-8")

    def test_a_missing_config_names_the_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            client = self.client(Path(name))
            with self.assertRaisesRegex(FileNotFoundError, "bootstrap_3d_workflow.py"):
                client.adapter_config()

    def test_a_config_from_another_worktree_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as name, tempfile.TemporaryDirectory() as other:
            client = self.client(Path(name))
            self.write(Path(name), Path(other).as_posix())
            with self.assertRaisesRegex(ValueError, "not this worktree"):
                client.adapter_config()

    def test_the_worktrees_own_config_is_read(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            client = self.client(Path(name))
            self.write(Path(name), Path(name).resolve().as_posix())
            self.assertEqual(client.adapter_config()["repository_root"], Path(name).resolve().as_posix())


if __name__ == "__main__":
    unittest.main()
