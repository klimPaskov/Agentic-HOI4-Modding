"""Provider-free motion, journal, redaction, and mutation-boundary regressions."""
from __future__ import annotations

import hashlib
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from meshy_client import MeshyClient, task_id_from
from lib.mcp_stdio import MCPRouteError
from lib.paths import redact
from blender_client import BlenderAdapterClient


class OptionalMotionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.client = object.__new__(MeshyClient)
        self.client.repo_root = Path(self.temp.name)
        self.client.job_root = Path(self.temp.name) / "job"
        self.client.job_root.mkdir()
        self.client.launcher = Path(self.temp.name) / "app-owned.exe"
        self.client.sequence = 0

    def live_tools(self):
        arguments = {
            "meshy_text_to_motion": ["prompt", "mode", "duration"],
            "meshy_get_motion_status": ["task_id"],
            "meshy_list_motion_tasks": ["page_num", "page_size"],
            "meshy_download_motion": ["task_id", "format", "save_to"],
            "meshy_animation_library": [],
            "meshy_animate": ["rig_task_id", "motion_task_id"],
        }
        return {"tools": [{"name": name, "inputSchema": {"properties": {key: {} for key in keys}}} for name, keys in arguments.items()]}

    def test_live_optional_tool_names_and_arguments_are_required(self):
        with patch("meshy_client.require_meshy_key"), patch("meshy_client.call_stdio", return_value=self.live_tools()) as called:
            self.client._require_motion_tools(generated_retarget=True)
            self.assertEqual(called.call_args.args[0], [str(self.client.launcher), "--run-verified-meshy-mcp"])
        for listed in ({"tools": []}, {"tools": [{"name": "meshy_text_to_motion", "inputSchema": {"properties": {}}}]}):
            with patch("meshy_client.require_meshy_key"), patch("meshy_client.call_stdio", return_value=listed):
                with self.assertRaisesRegex(MCPRouteError, "app-owned.*motion tools/schema"):
                    self.client._require_motion_tools()

    def test_invalid_duration_or_blank_prompt_never_probes_or_submits(self):
        self.client._require_motion_tools = Mock()
        self.client.call = Mock()
        for duration in (True, None, "3", math.nan, math.inf, 1, 10.5, 3.1):
            with self.assertRaises(ValueError):
                self.client.text_to_motion(prompt="Collapse and settle", mode="prime", duration=duration)
        with self.assertRaises(ValueError):
            self.client.text_to_motion(prompt="   ", mode="prime", duration=3)
        self.client._require_motion_tools.assert_not_called()
        self.client.call.assert_not_called()

    def test_valid_motion_has_one_paid_submission_and_known_estimate(self):
        self.client._require_motion_tools = Mock()
        self.client.call = Mock(return_value={"ok": True})
        self.client.text_to_motion(prompt="Wave", mode="swift", duration=3.5)
        self.client.call.assert_called_once_with("meshy_text_to_motion", {"prompt": "Wave", "mode": "swift", "duration": 3.5}, paid=True, estimate_credits=3, timeout_seconds=300)

    def test_animation_inputs_are_exclusive_before_submission(self):
        self.client._require_motion_tools = Mock()
        self.client.call = Mock()
        for kwargs in ({}, {"action_id": 1, "motion_task_id": "motion"}, {"motion_task_id": ""}):
            with self.assertRaises(ValueError):
                self.client.animate(rig_task_id="rig", estimate_credits=3, **kwargs)
        self.client.call.assert_not_called()
        self.client.animate(rig_task_id="rig", estimate_credits=3, motion_task_id="motion")
        self.client._require_motion_tools.assert_called_once_with(generated_retarget=True)
        self.assertEqual(self.client.call.call_args.args[1]["motion_task_id"], "motion")

    def test_uncertain_paid_submission_has_upfront_non_retry_journal(self):
        def uncertain(*args, **kwargs):
            journals = list((self.client.job_root / "provider/submissions").glob("*.json"))
            self.assertEqual(len(journals), 1)
            self.assertEqual(json.loads(journals[0].read_text())["state"], "submission_started")
            raise MCPRouteError("uncertain fixture")
        with patch("meshy_client.require_meshy_key"), patch("meshy_client.call_stdio", side_effect=uncertain) as called:
            with self.assertRaises(MCPRouteError):
                self.client.call("meshy_text_to_motion", {"prompt": "Wave"}, paid=True)
        self.assertEqual(called.call_count, 1)
        entry = json.loads(next((self.client.job_root / "provider/submissions").glob("*.json")).read_text())
        self.assertEqual(entry["state"], "uncertain")
        self.assertIs(entry["automatic_retry"], False)

    def test_motion_download_receipt_identity_and_bytes_match(self):
        output = self.client.job_root / "clip.fbx"
        self.client._require_motion_tools = Mock()
        def downloaded(*args, **kwargs):
            output.write_bytes(b"fixture FBX bytes")
            return {"structuredContent": {"task_id": "motion", "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}}
        self.client.call = Mock(side_effect=downloaded)
        receipt = self.client.download_motion(task_id="motion", format_name="fbx", destination=output)
        self.assertEqual(receipt["task_id"], "motion")
        with self.assertRaises(FileExistsError):
            self.client.download_motion(task_id="motion", format_name="fbx", destination=output)

    def test_motion_urls_remain_redacted(self):
        result = redact({"motion_url": "https://assets.meshy.ai/clip?signature=private", "task_id": "motion"})
        self.assertEqual(result, {"motion_url": "[REDACTED]", "task_id": "motion"})

    def test_official_result_string_is_a_task_id(self):
        self.assertEqual(task_id_from({"structuredContent": {"result": "motion-id"}}), "motion-id")


class MutationRetryTests(unittest.TestCase):
    def test_blender_mutation_is_not_replayed(self):
        client = object.__new__(BlenderAdapterClient)
        client.repo_root = ROOT.parents[1]
        client.wrapper = ROOT / "wrappers/run_blender_hoi4_adapter.cmd"
        with patch("blender_client.call_stdio", side_effect=MCPRouteError("uncertain")) as called, patch.object(client, "_matching_mutation_receipts", return_value=[]):
            with self.assertRaisesRegex(MCPRouteError, "no automatic retry"):
                client.call("hoi4_blender_export_mesh", {"job_id": "owner/job"})
        self.assertEqual(called.call_count, 1)

    def test_read_only_blender_inspection_retries_are_separate(self):
        client = object.__new__(BlenderAdapterClient)
        client.repo_root = ROOT.parents[1]
        client.wrapper = ROOT / "wrappers/run_blender_hoi4_adapter.cmd"
        with patch("blender_client.call_stdio", side_effect=[MCPRouteError("temporary"), {"structuredContent": {"ok": True}}]) as called:
            self.assertEqual(client.call("hoi4_blender_inspect_scene", {"job_id": "owner/job"}), {"ok": True})
        self.assertEqual(called.call_count, 2)


if __name__ == "__main__":
    unittest.main()
