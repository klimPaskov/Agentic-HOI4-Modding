"""The reference image's visual preflight starts unreviewed and is accepted only once reviewed.

`initialize_one` used to write every visual_preflight flag as a constant True with
the approval "parent_agent_visual_review", so a job looked reviewed before anyone
had looked. These tests run it against a temporary job root with a placeholder
Meshy key; no provider is called.
"""

from __future__ import annotations

import json
import os
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

with mock.patch.dict(os.environ, {"MESHY_API_KEY": "placeholder-not-a-real-key"}):
    import init_pilot_jobs as init


def png_bytes(width: int = 64, height: int = 64, tint: int = 0) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    rows = b"".join(b"\x00" + bytes([tint]) * width for _ in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")


ALL_TRUE = {check: True for check in init.VISUAL_PREFLIGHT_CHECKS}


class VisualPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.job = self.root / "unit_slug"
        self.spec = {
            "asset_id": "hoi4_3d_model_jobs.unit_slug",
            "reference_path": "refs/original/meshy_input.png",
            "profile": "static_prop",
            "asset_kind": "static",
            "asset_brief": "A lamp post.",
            "required_components": ["post"],
            "forbidden_additions": ["text"],
            "reference_source_mode": "agent_generated",
            "reference_generator_output": "gpt-image",
            "meshy_ai_model": "meshy-7",
            "meshy_pose_mode": "",
            "target_polycount": 30000,
            "target_height_m": 1.5,
            "runtime_stem": "lamp",
            "required_actions": [],
            "proposed_runtime_identifiers": {},
        }
        for directory in ("refs/original", "refs/derived", "refs/briefs", "validation"):
            (self.job / directory).mkdir(parents=True)
        self.reference = self.job / "refs/original/meshy_input.png"
        self.reference.write_bytes(png_bytes())
        for name, replacement in (
            ("resolve_job_root", lambda slug: self.job),
            ("ensure_job_layout", lambda root: root),
        ):
            patcher = mock.patch.object(init, name, side_effect=replacement)
            patcher.start()
            self.addCleanup(patcher.stop)

    def initialize(self, **kwargs) -> dict:
        return init.initialize_one(self.spec, **kwargs)

    def read(self, relative: str) -> dict:
        return json.loads((self.job / relative).read_text(encoding="utf-8"))

    def preflight(self) -> dict:
        return self.read("refs/derived/reference_provenance.json")["visual_preflight"]

    def test_a_new_job_starts_with_every_check_unanswered_and_no_approval(self) -> None:
        result = self.initialize(require_review=False)
        preflight = self.preflight()
        for check in init.VISUAL_PREFLIGHT_CHECKS:
            self.assertIsNone(preflight[check], check)
        self.assertIsNone(preflight["approval"])
        self.assertEqual(preflight["review"]["status"], "not_reviewed")
        self.assertIsNone(preflight["review"]["reviewer"])
        self.assertEqual(result["visual_preflight"], "pending_review")
        record = self.read("validation/reference_preflight.json")
        self.assertEqual(record["status"], "pending_review")
        self.assertNotIn(True, [record["checks"].get(check) for check in init.VISUAL_PREFLIGHT_CHECKS])

    def test_running_a_job_is_blocked_before_any_paid_call_until_the_review_is_recorded(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "pending_review.*--record-visual-review unit_slug.*No paid call"):
            self.initialize()
        # The job files were still written, so the review can be recorded without another init.
        self.assertTrue((self.job / "refs/derived/reference_provenance.json").is_file())
        init.record_visual_preflight_review(self.job, ALL_TRUE, reviewer="parent_agent")
        self.assertEqual(self.initialize()["visual_preflight"], "passed")

    def test_recording_a_review_passes_and_is_attributed(self) -> None:
        self.initialize(require_review=False)
        outcome = init.record_visual_preflight_review(
            self.job, ALL_TRUE, reviewer="parent_agent", notes="Single lamp on a plain background."
        )
        self.assertEqual(outcome["status"], "passed")
        preflight = self.preflight()
        self.assertTrue(all(preflight[check] is True for check in init.VISUAL_PREFLIGHT_CHECKS))
        self.assertEqual(preflight["review"]["reviewer"], "parent_agent")
        self.assertEqual(preflight["review"]["notes"], "Single lamp on a plain background.")
        self.assertTrue(preflight["review"]["reviewed_at"])
        self.assertEqual(self.read("validation/reference_preflight.json")["status"], "passed")
        history = (self.job / "history.jsonl").read_text(encoding="utf-8")
        self.assertIn("visual_preflight_reviewed", history)

    def test_a_review_with_a_failed_check_is_failed_and_still_blocks_the_run(self) -> None:
        self.initialize(require_review=False)
        answers = {**ALL_TRUE, "neutral_background": False}
        self.assertEqual(init.record_visual_preflight_review(self.job, answers, reviewer="parent_agent")["status"], "failed")
        self.assertEqual(self.read("validation/reference_preflight.json")["status"], "failed")
        with self.assertRaisesRegex(RuntimeError, "visual preflight is failed"):
            self.initialize()

    def test_reinitializing_keeps_a_review_of_the_same_image(self) -> None:
        self.initialize(require_review=False)
        init.record_visual_preflight_review(self.job, ALL_TRUE, reviewer="parent_agent")
        self.initialize()
        self.assertEqual(self.preflight()["review"]["reviewer"], "parent_agent")
        self.assertEqual(self.read("validation/reference_preflight.json")["status"], "passed")

    def test_a_replaced_reference_image_invalidates_the_review(self) -> None:
        self.initialize(require_review=False)
        init.record_visual_preflight_review(self.job, ALL_TRUE, reviewer="parent_agent")
        self.reference.write_bytes(png_bytes(tint=90))
        with self.assertRaisesRegex(RuntimeError, "visual preflight is pending_review"):
            self.initialize()
        self.assertEqual(self.preflight()["review"]["status"], "not_reviewed")

    def test_a_review_cannot_be_recorded_for_an_image_that_changed_since_initialization(self) -> None:
        self.initialize(require_review=False)
        self.reference.write_bytes(png_bytes(tint=40))
        with self.assertRaisesRegex(RuntimeError, "changed since the job was initialized"):
            init.record_visual_preflight_review(self.job, ALL_TRUE, reviewer="parent_agent")

    def test_only_complete_boolean_answers_from_a_named_reviewer_are_recorded(self) -> None:
        self.initialize(require_review=False)
        incomplete = {key: value for key, value in ALL_TRUE.items() if key != "single_subject"}
        bad_answers = [
            incomplete,
            {**ALL_TRUE, "single_subject": "yes"},
            {**ALL_TRUE, "single_subject": None},
            {**ALL_TRUE, "extra_check": True},
            {},
        ]
        for answers in bad_answers:
            with self.subTest(answers=answers), self.assertRaisesRegex(ValueError, "exactly these checks"):
                init.record_visual_preflight_review(self.job, answers, reviewer="parent_agent")
        for reviewer in ("", "   ", None):
            with self.subTest(reviewer=reviewer), self.assertRaisesRegex(ValueError, "non-empty reviewer"):
                init.record_visual_preflight_review(self.job, ALL_TRUE, reviewer=reviewer)
        self.assertEqual(self.preflight()["review"]["status"], "not_reviewed")

    def test_review_needs_an_initialized_job(self) -> None:
        with self.assertRaises(FileNotFoundError):
            init.record_visual_preflight_review(self.job, ALL_TRUE, reviewer="parent_agent")

    def test_a_job_past_preflight_is_not_blocked_retroactively(self) -> None:
        self.initialize(require_review=False)
        job_file = self.job / "job.yaml"
        record = json.loads(job_file.read_text(encoding="utf-8"))
        record["status"] = "candidate_qa"
        job_file.write_text(json.dumps(record), encoding="utf-8")
        result = self.initialize()
        self.assertEqual(result["status"], "candidate_qa")
        self.assertEqual(result["visual_preflight"], "pending_review")

    def test_the_status_function_accepts_only_a_recorded_all_true_review(self) -> None:
        pending = init.pending_visual_preflight("0" * 64)
        self.assertEqual(init.visual_preflight_status(pending), "pending_review")
        legacy_constants = {**ALL_TRUE, "approval": "parent_agent_visual_review"}  # the old fail-open shape
        self.assertEqual(init.visual_preflight_status(legacy_constants), "pending_review")
        reviewed = {**ALL_TRUE, "review": {"status": "reviewed"}}
        self.assertEqual(init.visual_preflight_status(reviewed), "passed")
        reviewed["single_subject"] = None
        self.assertEqual(init.visual_preflight_status(reviewed), "failed")

    def test_the_command_line_records_a_review_from_a_json_file(self) -> None:
        self.initialize(require_review=False)
        review = self.root / "review.json"
        review.write_text(json.dumps({**ALL_TRUE, "notes": "Looks right."}), encoding="utf-8")
        config = self.root / "jobs.json"
        config.write_text(json.dumps({"jobs": {"unit_slug": self.spec}}), encoding="utf-8")
        argv = [
            "init_pilot_jobs.py",
            "--jobs-config", str(config),
            "--record-visual-review", "unit_slug",
            "--reviewer", "parent_agent",
            "--review-file", str(review),
        ]
        with mock.patch.object(init, "REPO_ROOT", self.root), mock.patch.object(sys, "argv", argv), mock.patch(
            "builtins.print"
        ):
            self.assertEqual(init.main(), 0)
        self.assertEqual(self.preflight()["review"]["notes"], "Looks right.")
        self.assertEqual(self.read("validation/reference_preflight.json")["status"], "passed")

    def test_the_command_line_refuses_a_review_file_outside_the_repository(self) -> None:
        self.initialize(require_review=False)
        config = self.root / "jobs.json"
        config.write_text(json.dumps({"jobs": {"unit_slug": self.spec}}), encoding="utf-8")
        outside = Path(tempfile.gettempdir()).resolve() / "outside-review.json"
        argv = [
            "init_pilot_jobs.py",
            "--jobs-config", str(config),
            "--record-visual-review", "unit_slug",
            "--reviewer", "parent_agent",
            "--review-file", str(outside),
        ]
        inside = self.root / "repo"
        inside.mkdir()
        config_inside = inside / "jobs.json"
        config_inside.write_text(json.dumps({"jobs": {"unit_slug": self.spec}}), encoding="utf-8")
        argv[2] = str(config_inside)
        with mock.patch.object(init, "REPO_ROOT", inside), mock.patch.object(sys, "argv", argv), self.assertRaisesRegex(
            ValueError, "must remain inside the repository"
        ):
            init.main()
        self.assertEqual(self.preflight()["review"]["status"], "not_reviewed")


if __name__ == "__main__":
    unittest.main()
