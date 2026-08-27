"""Focused, provider-free regressions for reusable 3D workflow synchronization."""

from __future__ import annotations

import ast
import inspect
import json
import sys
import unittest
from unittest import mock
from pathlib import Path


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from adapter.normalization_convergence import evaluate_convergence_step  # noqa: E402
from lib import mcp_stdio  # noqa: E402
from lib.mcp_stdio import MCPRouteError, call_stdio  # noqa: E402
from meshy_client import _payload  # noqa: E402


def function_arguments(path: Path, name: str) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    function = next(
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name
    )
    return [argument.arg for argument in function.args.args]


class WorkflowSyncContractTests(unittest.TestCase):
    def test_normalization_convergence_accepts_and_corrects(self) -> None:
        accepted = evaluate_convergence_step(
            target=8.0,
            persisted=8.00001,
            tolerance=0.0001,
            previous_delta=0.001,
            corrections_applied=2,
            max_corrections=8,
        )
        self.assertEqual(accepted["status"], "accepted")
        correction = evaluate_convergence_step(
            target=8.0,
            persisted=8.001,
            tolerance=0.0001,
            previous_delta=0.004,
            corrections_applied=2,
            max_corrections=8,
        )
        self.assertEqual(correction["status"], "correct")
        self.assertGreater(correction["correction_factor"], 0.0)

    def test_normalization_convergence_rejects_unstable_steps(self) -> None:
        cases = (
            (8.001, 0.0010001, "stalled"),
            (8.002, 0.001, "diverged"),
            (7.999, 0.001, "changed sign"),
        )
        for persisted, previous, expected in cases:
            with self.subTest(expected=expected), self.assertRaisesRegex(RuntimeError, expected):
                evaluate_convergence_step(
                    target=8.0,
                    persisted=persisted,
                    tolerance=0.00001,
                    previous_delta=previous,
                    corrections_applied=2,
                    max_corrections=8,
                )

    def test_stdio_lifecycle_receipt_records_exact_cleanup(self) -> None:
        receipt: dict[str, object] = {}
        script = (
            "import json,sys; sys.stdin.read(); "
            "print(json.dumps({'jsonrpc':'2.0','id':2,'result':{'ok':True}}))"
        )
        result = call_stdio(
            [sys.executable, "-c", script],
            list_tools=True,
            timeout_seconds=20,
            lifecycle_receipt=receipt,
        )
        self.assertTrue(result["ok"])
        self.assertIsInstance(receipt["root_pid"], int)
        self.assertEqual(receipt["surviving_process_ids"], [])
        self.assertIn(receipt["ownership"], {"windows_job_object", "direct_process"})

    def test_meshy_payload_keeps_structured_and_text_results_compatible(self) -> None:
        self.assertEqual(_payload({"structuredContent": {"task_id": "one"}})["task_id"], "one")
        text_result = {"content": [{"type": "text", "text": json.dumps({"task_id": "two"})}]}
        self.assertEqual(_payload(text_result)["task_id"], "two")

    def test_verified_animation_source_arguments_cross_adapter_boundaries(self) -> None:
        expected = {
            "provenance_rel",
            "source_action_name",
            "target_armature_name",
            "target_action_name",
            "source_kind",
            "source_reference_id",
            "source_sha256",
            "source_armature_name",
        }
        adapter_args = set(
            function_arguments(
                PIPELINE_ROOT / "adapter" / "hoi4_blender_mcp.py",
                "hoi4_blender_import_animation_action",
            )
        )
        client_args = set(
            function_arguments(PIPELINE_ROOT / "blender_client.py", "import_animation_action")
        )
        self.assertTrue(expected <= adapter_args)
        self.assertTrue(expected <= client_args)

    def test_worker_persists_scale_and_fails_closed_on_source_receipts(self) -> None:
        source = (PIPELINE_ROOT / "adapter" / "blender_worker.py").read_text(encoding="utf-8")
        self.assertIn("stabilize_saved_normalization(pre_export, target_height)", source)
        self.assertIn("verify_saved_normalization(pre_export, target_height)", source)
        self.assertIn("source_armature_uniform_world_scale / target_armature_uniform_world_scale", source)
        self.assertIn('"verification_status": "verified"', source)
        self.assertIn("Animation source checksum did not match the verified provenance receipt", source)
        self.assertIn("balanced parenthetical qualifiers", source)

    def test_shared_runner_no_longer_authors_replacement_locomotion(self) -> None:
        source = (PIPELINE_ROOT / "run_pilot.py").read_text(encoding="utf-8")
        continuation = source.split("def continue_humanoid_shared", 1)[1]
        self.assertIn('import_verified_action(\n        "move"', continuation)
        self.assertNotIn("blender.author_locomotion_action(", continuation)

    def test_call_stdio_exposes_lifecycle_receipt(self) -> None:
        self.assertIn("lifecycle_receipt", inspect.signature(call_stdio).parameters)

    def test_stdio_cleanup_continues_when_job_inspection_fails(self) -> None:
        script = (
            "import json,sys; sys.stdin.read(); "
            "print(json.dumps({'jsonrpc':'2.0','id':2,'result':{'ok':True}}))"
        )
        with (
            mock.patch.object(
                mcp_stdio,
                "_windows_job_process_ids",
                side_effect=MCPRouteError("inspection failed"),
            ),
            mock.patch.object(mcp_stdio, "_close_windows_handle") as close_handle,
            mock.patch.object(mcp_stdio, "_terminate_windows_descendants") as terminate,
            mock.patch.object(mcp_stdio, "_wait_windows_pids_exit", return_value=[]),
            self.assertRaisesRegex(MCPRouteError, "could not verify"),
        ):
            call_stdio([sys.executable, "-c", script], list_tools=True, timeout_seconds=20)
        close_handle.assert_called()
        terminate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
