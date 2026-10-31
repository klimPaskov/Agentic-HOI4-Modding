"""Before a paid create the runner reuses an existing result, or stops on an unreconciled submission."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import run_pilot
from lib import credits
from lib.credits import PaidRequest, UnreconciledSubmission
from lib.mcp_stdio import MCPRouteError
from lib.reuse import reconcile_submission
from meshy_client import MeshyClient, image_to_3d_arguments
from test_credit_budget import FakeClient

FINGERPRINT = "FP-SHARED-INPUT"
LONG_AGO = "2020-01-01T00:00:00Z"


def request(fingerprint: str = FINGERPRINT, operation: str = "image_to_3d") -> PaidRequest:
    return PaidRequest(
        operation=operation,
        tool="meshy_image_to_3d",
        model="meshy-7",
        fingerprint=fingerprint,
        scope=operation,
        attempt_limit=1,
        credit_budget=100,
    )


class ReuseCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "models_3d"
        self.job = self.new_job("unit_b")
        self.client = FakeClient()

    def new_job(self, name: str) -> Path:
        job = self.root / name
        (job / "provider").mkdir(parents=True)
        return job

    def finished_job(self, name: str = "unit_a", *, fingerprint: str = FINGERPRINT, status: str = "SUCCEEDED",
                     recorded_at: str = "", downloads: bool = True) -> Path:
        """Another job that already paid for this request."""
        job = self.new_job(name)
        run_pilot.write_json(
            run_pilot.task_file(job, "generation"),
            {
                "stage": "generation",
                "task_id": f"task-from-{name}",
                "task_type": "image-to-3d",
                "status": status,
                "fingerprint": fingerprint,
                "consumed_credits": 30,
                "estimated_credits": 30,
                "recorded_at": recorded_at or run_pilot.utc_now(),
                "final_response": {"status": status},
            },
        )
        if downloads:
            downloaded = job / "provider" / "downloads"
            (downloaded / "generation_model_textures").mkdir(parents=True)
            (downloaded / "generation_model.glb").write_bytes(b"glb bytes of " + name.encode())
            (downloaded / "generation_model_textures" / "base_color.png").write_bytes(b"png")
            run_pilot.write_json(
                downloaded / "generation_model.glb.manifest.json",
                {"task_id": f"task-from-{name}", "format": "glb", "file": {"name": "generation_model.glb", "path": "elsewhere"}},
            )
        return job

    def pay(self, req: PaidRequest | None = None, stage: str = "generation", cost: int = 30) -> str:
        return run_pilot.provider_task(
            self.client,
            self.job,
            stage,
            task_type="image-to-3d",
            estimate=cost,
            create=self.client.create(cost),
            request=req or request(),
        )

    def rows(self, outcome: str = "") -> list:
        return [row for row in credits.read_ledger(self.job) if not outcome or row["outcome"] == outcome]

    def journal(self, job: Path, name: str = "entry", **fields) -> Path:
        entry = {"tool": "meshy_image_to_3d", "fingerprint": FINGERPRINT, "state": "uncertain", "timestamp": "2026-10-30T10:00:00Z"}
        entry.update(fields)
        path = job / "provider" / "submissions" / f"{name}.json"
        run_pilot.write_json(path, entry)
        return path


class OtherJobResultTests(ReuseCase):
    def test_a_succeeded_result_in_another_job_is_adopted_without_paying(self) -> None:
        source = self.finished_job()
        self.assertEqual(self.pay(), "task-from-unit_a")
        self.assertEqual(self.client.created, 0)
        task = json.loads(run_pilot.task_file(self.job, "generation").read_text(encoding="utf-8"))
        self.assertEqual((task["status"], task["task_id"], task["consumed_credits"]), ("SUCCEEDED", "task-from-unit_a", 0))
        self.assertEqual((task["reused_from"]["job"], task["reused_from"]["source_consumed_credits"]), ("unit_a", 30))
        copied = self.job / "provider" / "downloads"
        self.assertEqual((copied / "generation_model.glb").read_bytes(), (source / "provider/downloads/generation_model.glb").read_bytes())
        self.assertTrue((copied / "generation_model_textures" / "base_color.png").is_file())
        manifest = json.loads((copied / "generation_model.glb.manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["file"]["relative_path"], "provider/downloads/generation_model.glb")
        self.assertEqual(manifest["reused_from"]["job"], "unit_a")
        self.assertEqual([row["outcome"] for row in self.rows()], ["reused"], "no reservation, no paid attempt")
        reused = self.rows("reused")[0]
        self.assertEqual((reused["estimate_credits"], reused["consumed_credits"], reused["reused_from"]["tier"]), (30, 0, "other_job"))
        self.assertEqual(credits.attempts_made(credits.read_ledger(self.job), "image_to_3d"), 0)
        self.assertEqual(credits.budget_state(credits.read_ledger(self.job), 100)["consumed"], 0)

    def test_asking_again_uses_the_job_stage_and_records_no_second_reuse(self) -> None:
        self.finished_job()
        self.pay()
        self.pay()
        self.assertEqual(len(self.rows("reused")), 1)
        self.assertEqual(self.client.created, 0)

    def test_the_newest_matching_result_wins(self) -> None:
        self.finished_job("unit_old", recorded_at="2026-10-01T00:00:00Z")
        self.finished_job("unit_new", recorded_at="2026-10-20T00:00:00Z")
        self.assertEqual(self.pay(), "task-from-unit_new")

    def test_a_different_input_or_request_is_a_miss_that_pays_and_records_what_was_checked(self) -> None:
        self.finished_job(fingerprint="FP-OTHER-IMAGE")
        self.assertEqual(self.pay(), "task-1")
        self.assertEqual(self.client.created, 1)
        reserved = self.rows("reserved")[0]
        checks = reserved["reuse_checks"]
        self.assertEqual(checks["job_stage"], "no succeeded task for this stage")
        self.assertIn("in 1 other job(s)", checks["other_jobs"])
        self.assertEqual(checks["submission_journal"], "no unreconciled submission for this request")
        self.assertIn("meshy_list_tasks", checks["meshy_lookup"])
        history = [json.loads(line) for line in (self.job / "history.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertIn("provider_reuse_decision", [event["state"] for event in history])

    def test_a_failed_result_elsewhere_is_never_reused(self) -> None:
        self.finished_job(status="FAILED")
        self.assertEqual(self.pay(), "task-1")
        self.assertEqual(self.client.created, 1)

    def test_a_result_meshy_no_longer_keeps_is_reused_only_if_its_files_are_local(self) -> None:
        self.finished_job("unit_gone", recorded_at=LONG_AGO, downloads=False)
        self.assertEqual(self.pay(), "task-1")
        self.assertIn("1 expired", self.rows("reserved")[0]["reuse_checks"]["other_jobs"])

    def test_old_results_with_local_files_are_still_reused(self) -> None:
        self.finished_job("unit_kept", recorded_at=LONG_AGO)
        self.assertEqual(self.pay(), "task-from-unit_kept")
        self.assertEqual(self.client.created, 0)

    def test_a_job_with_no_neighbours_pays(self) -> None:
        self.assertEqual(self.pay(), "task-1")
        self.assertIn("in 0 other job(s)", self.rows("reserved")[0]["reuse_checks"]["other_jobs"])


class SubmissionJournalTests(ReuseCase):
    def test_an_uncertain_submission_for_the_same_request_blocks_the_call(self) -> None:
        path = self.journal(self.job)
        with self.assertRaises(UnreconciledSubmission) as stop:
            self.pay()
        self.assertEqual(self.client.created, 0)
        self.assertIn(str(path), str(stop.exception))
        self.assertIn("meshy_list_tasks", str(stop.exception))
        self.assertIn("reconcile_submission", str(stop.exception))
        blocked = self.rows("rejected")[0]
        self.assertEqual((blocked["stage"], blocked["consumed_credits"]), ("generation", 0))
        self.assertEqual(blocked["reuse_checks"]["submission_journal"], "1 unreconciled submission(s)")
        self.assertFalse(run_pilot.task_file(self.job, "generation").exists())

    def test_a_started_submission_with_no_result_blocks_too(self) -> None:
        self.journal(self.job, state="submission_started")
        with self.assertRaises(UnreconciledSubmission):
            self.pay()

    def test_an_unreconciled_submission_in_another_job_blocks_the_same_request(self) -> None:
        self.journal(self.new_job("unit_c"))
        with self.assertRaises(UnreconciledSubmission):
            self.pay()

    def test_submissions_that_do_not_block(self) -> None:
        self.journal(self.job, "other_request", fingerprint="FP-OTHER")
        self.journal(self.job, "answered", state="response_received", response={"structuredContent": {"task_id": "t"}})
        self.journal(self.job, "has_task", response={"structuredContent": {"task_id": "t"}})
        self.journal(self.job, "done", state="reconciled")
        self.assertEqual(self.pay(), "task-1")

    def test_a_reusable_result_beats_a_blocking_submission(self) -> None:
        self.finished_job()
        self.journal(self.job)
        self.assertEqual(self.pay(), "task-from-unit_a")
        self.assertEqual(self.client.created, 0)

    def test_reconciling_as_never_created_releases_the_credits_and_unblocks(self) -> None:
        credits.reserve(self.job, request(), stage="generation", estimate=30, reason="submitted")
        path = self.journal(self.job)
        with self.assertRaises(UnreconciledSubmission):
            self.pay()
        reconcile_submission(path, note="Meshy lists no task for that time")
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["state"], "reconciled")
        ledger = credits.read_ledger(self.job)
        self.assertEqual(credits.budget_state(ledger, 100)["reserved"], 0)
        self.assertEqual(credits.attempts_made(ledger, "image_to_3d"), 0)
        self.assertEqual(self.pay(), "task-1")

    def test_reconciling_with_a_task_id_resumes_that_task_instead_of_paying(self) -> None:
        attempt = credits.reserve(self.job, request(), stage="generation", estimate=30, reason="submitted")
        path = self.journal(self.job)
        reconcile_submission(path, task_id="task-found-on-meshy")
        record = json.loads(run_pilot.task_file(self.job, "generation").read_text(encoding="utf-8"))
        self.assertEqual((record["task_id"], record["status"], record["task_type"]), ("task-found-on-meshy", "PENDING", "image-to-3d"))
        self.client.outcomes = [{"status": "SUCCEEDED", "consumed_credits": 30}]
        self.assertEqual(self.pay(), "task-found-on-meshy")
        self.assertEqual(self.client.created, 0)
        self.assertEqual(self.rows("success")[0]["attempt_id"], attempt)

    def test_reconciling_with_a_task_id_needs_a_reservation_to_attach_it_to(self) -> None:
        path = self.journal(self.job)
        with self.assertRaisesRegex(ValueError, "No open ledger reservation"):
            reconcile_submission(path, task_id="task-found-on-meshy")
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["state"], "uncertain")


class ClientJournalTests(unittest.TestCase):
    def test_every_paid_submission_journal_carries_the_request_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            client = object.__new__(MeshyClient)
            client.repo_root = Path(temporary)
            client.job_root = Path(temporary) / "job"
            client.job_root.mkdir()
            client.launcher = Path(temporary) / "launcher.exe"
            client.sequence = 0
            image = client.job_root / "meshy_input.png"
            image.write_bytes(b"image")
            arguments = {"file_path": str(image), "ai_model": "meshy-7", "response_format": "json"}
            with patch("meshy_client.require_meshy_key"), patch("meshy_client.call_stdio", side_effect=MCPRouteError("lost")):
                with self.assertRaises(MCPRouteError):
                    client.call("meshy_image_to_3d", arguments, paid=True)
            entry = json.loads(next((client.job_root / "provider" / "submissions").glob("*.json")).read_text(encoding="utf-8"))
            self.assertEqual(entry["state"], "uncertain")
            self.assertEqual(entry["fingerprint"], credits.request_fingerprint("meshy_image_to_3d", arguments))

    def test_the_runner_and_the_client_fingerprint_the_same_request(self) -> None:
        spec = run_pilot.prepare_spec(
            {
                "asset_id": "hoi4.model.job.unit_a",
                "asset_kind": "static",
                "profile": "static_prop",
                "credit_budget": 60,
                "meshy_pose_mode": "a-pose",
            }
        )
        with tempfile.TemporaryDirectory() as temporary:
            client = object.__new__(MeshyClient)
            client.repo_root = Path(temporary)
            client.job_root = Path(temporary).resolve() / "job"
            client.job_root.mkdir()
            client.launcher = Path(temporary) / "launcher.exe"
            client.sequence = 0
            image = client.job_root / "meshy_input.png"
            image.write_bytes(b"image")
            expected = run_pilot.paid_request(
                spec,
                "image_to_3d",
                "meshy_image_to_3d",
                image_to_3d_arguments(image.resolve(), spec["generation"], "a-pose"),
            )
            with patch("meshy_client.require_meshy_key"), patch("meshy_client.call_stdio", side_effect=MCPRouteError("lost")):
                with self.assertRaises(MCPRouteError):
                    client.image_to_3d(image_path=image, generation=spec["generation"], pose_mode="a-pose", estimate_credits=15)
            entry = json.loads(next((client.job_root / "provider" / "submissions").glob("*.json")).read_text(encoding="utf-8"))
        self.assertEqual(entry["fingerprint"], expected.fingerprint)
        self.assertEqual((expected.operation, expected.scope, expected.attempt_limit, expected.model), ("image_to_3d", "image_to_3d", 1, "meshy-7"))


if __name__ == "__main__":
    unittest.main()
