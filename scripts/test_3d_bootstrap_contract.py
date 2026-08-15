from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / ".tools/3d_pipeline/bootstrap_3d_workflow.py"
SPEC = importlib.util.spec_from_file_location("three_d_bootstrap", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
BOOTSTRAP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOOTSTRAP)


class ReviewedConfigTests(unittest.TestCase):
    def test_materialized_routes_pass_reviewed_config_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = BOOTSTRAP.materialize_config(root)

            self.assertEqual(BOOTSTRAP.verify_reviewed_config(root), config)

    def test_changed_reviewed_route_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = BOOTSTRAP.materialize_config(root)
            config.write_text(
                config.read_text(encoding="utf-8").replace(
                    'command = "cmd.exe"', 'command = "unreviewed.exe"', 1
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(BOOTSTRAP.SetupError, "unexpected"):
                BOOTSTRAP.verify_reviewed_config(root)


if __name__ == "__main__":
    unittest.main()
