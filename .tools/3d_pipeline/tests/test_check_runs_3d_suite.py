"""`.tools/check.py full` runs this suite, so a stale or broken 3D gate fails the standard check."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
REPO = PIPELINE.parents[1]
PATTERN = ".tools/3d_pipeline/tests/test_*.py"


def check_patterns() -> tuple:
    """TEST_PATTERNS read from check.py's source; importing it would shadow this suite's `lib` package."""

    tree = ast.parse((REPO / ".tools" / "check.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(target, "id", "") == "TEST_PATTERNS" for target in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("check.py defines no TEST_PATTERNS")


class CheckCoverageTests(unittest.TestCase):
    def test_the_standard_check_discovers_the_3d_suite(self) -> None:
        self.assertIn(PATTERN, check_patterns())
        found = {path.name for path in REPO.glob(PATTERN)}
        for name in (
            "test_credit_budget.py",
            "test_credits_report.py",
            "test_generation_settings.py",
            "test_meshy_contract_lock.py",
            "test_reuse_before_paying.py",
            Path(__file__).name,
        ):
            self.assertIn(name, found)

    def test_every_gate_test_file_is_found_by_the_pattern(self) -> None:
        on_disk = {path.name for path in (PIPELINE / "tests").glob("test_*.py")}
        self.assertEqual(on_disk, {path.name for path in REPO.glob(PATTERN)})


if __name__ == "__main__":
    unittest.main()
