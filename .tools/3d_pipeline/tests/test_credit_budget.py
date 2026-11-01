"""The job credit budget, attempt limits and ledger gate every paid create before it is submitted."""

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
from lib.credits import AttemptLimitReached, BudgetExceeded, PaidRequest
from meshy_client import MeshyTaskFailed


def request(operation: str = "rig", *, scope: str = "", budget: int = 40, limit: int = 1, fingerprint: str = "F1") -> PaidRequest:
    return PaidRequest(
        operation=operation,
        tool=f"meshy_{operation}",
        model="meshy-7" if operation == "image_to_3d" else None,
        fingerprint=fingerprint,
        scope=scope or f"{operation}@generation",
        attempt_limit=limit,
        credit_budget=budget,
    )


class FakeClient:
    """Stands in for the Meshy client: a balance, tasks that finish, and a count of paid creates."""

    def __init__(self, balance: int = 285) -> None:
        self.balance = balance
        self.created = 0
        self.outcomes: list = []

    def check_balance(self) -> dict:
        return {"structuredContent": {"balance": self.balance}}

    def create(self, cost: int):
        def create() -> dict:
            self.created += 1
            self.balance -= cost
            return {"structuredContent": {"task_id": f"task-{self.created}", "status": "PENDING"}}

        return create

    def wait_for_task(self, task_id: str, *, task_type: str) -> dict:
        outcome = self.outcomes.pop(0) if self.outcomes else {"status": "SUCCEEDED", "consumed_credits": 5}
        final = {"structuredContent": {**outcome, "task_id": task_id}}
        if outcome["status"] != "SUCCEEDED":
            raise MeshyTaskFailed(task_id, outcome["status"], final)
        return final


class JobCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.job = Path(self.temp.name) / "models_3d" / "unit_a"
        self.job.mkdir(parents=True)
        self.client = FakeClient()

    def pay(self, stage: str, req: PaidRequest, cost: int = 5, task_type: str = "rigging") -> str:
        return run_pilot.provider_task(
            self.client,
            self.job,
            stage,
            task_type=task_type,
            estimate=cost,
            create=self.client.create(cost),
            request=req,
        )

    def rows(self, outcome: str = "") -> list:
        return [row for row in credits.read_ledger(self.job) if not outcome or row["outcome"] == outcome]


class BudgetTests(JobCase):
    def test_a_call_that_would_exceed_the_budget_stops_before_submission_and_names_the_shortfall(self) -> None:
        self.client.outcomes = [{"status": "SUCCEEDED", "consumed_credits": 30}] + [{"status": "SUCCEEDED", "consumed_credits": 5}] * 2
        self.pay("generation", request("image_to_3d", scope="image_to_3d", budget=40), 30, "image-to-3d")
        self.pay("rig_remesh", request("remesh", budget=40), 5, "remesh")
        self.pay("rig", request("rig", budget=40), 5)
        created = self.client.created
        with self.assertRaises(BudgetExceeded) as stop:
            self.pay("animation_idle", request("animation", scope="animation:idle@generation", budget=40), 3, "animation")
        message = str(stop.exception)
        self.assertIn("needs 3 credits, but only 0 of the 40-credit job budget remain", message)
        self.assertIn("Short by 3", message)
        self.assertIn("at least 43", message)
        self.assertEqual(self.client.created, created, "nothing may be submitted")
        self.assertFalse(run_pilot.task_file(self.job, "animation_idle").exists())
        stopped = self.rows("rejected")[-1]
        self.assertEqual((stopped["stage"], stopped["consumed_credits"]), ("animation_idle", 0))
        self.assertIn("Credit budget stop", stopped["reason"])

    def test_open_reservations_count_against_the_budget(self) -> None:
        req = request("rig", budget=12)
        credits.reserve(self.job, request("remesh", budget=12), stage="rig_remesh", estimate=10, reason="in flight")
        with self.assertRaisesRegex(BudgetExceeded, "only 2 of the 12-credit job budget remain.*10 reserved"):
            self.pay("rig", req, 5)

    def test_a_settled_reservation_is_counted_once_at_what_it_cost(self) -> None:
        attempt = credits.reserve(self.job, request("rig"), stage="rig", estimate=5, reason="x")
        credits.settle(self.job, attempt, outcome="success", consumed=3, source="provider", reason="done")
        state = credits.budget_state(credits.read_ledger(self.job), 40)
        self.assertEqual((state["consumed"], state["reserved"], state["remaining"]), (3, 0, 37))

    def test_unknown_consumption_counts_the_estimate_against_the_budget(self) -> None:
        attempt = credits.reserve(self.job, request("rig"), stage="rig", estimate=5, reason="x")
        credits.settle(self.job, attempt, outcome="success", consumed=None, source="unknown", reason="done")
        self.assertEqual(credits.budget_state(credits.read_ledger(self.job), 40)["consumed"], 5)

    def test_the_live_balance_is_checked_after_the_budget(self) -> None:
        self.client.balance = 4
        with self.assertRaisesRegex(RuntimeError, "balance 4 is below the 5-credit gate.*short by 1"):
            self.pay("rig", request("rig"), 5)
        self.assertEqual(self.client.created, 0)
        self.assertIn("balance 4", self.rows("rejected")[-1]["reason"])

    def test_headroom_check_stops_a_plan_the_budget_cannot_cover(self) -> None:
        spec = {"asset_id": "hoi4.model.job.unit_a", "credit_budget": 40}
        pending = [{"job": "unit_a", "stage": "generation", "estimate_credits": 30}, {"job": "unit_a", "stage": "rig", "estimate_credits": 19}]
        with patch.object(run_pilot, "resolve_job_root", return_value=self.job), patch.object(run_pilot, "ensure_job_layout", return_value=self.job):
            with self.assertRaisesRegex(RuntimeError, "plans 49 credits but only 40.*Short by 9.*at least 49"):
                run_pilot.require_budget_headroom(pending, [spec])
            run_pilot.require_budget_headroom(pending[:1], [spec])


class PreflightTests(JobCase):
    """The whole plan is checked against the budget before the first paid call, ahead of the balance probe."""

    def spec(self, budget: int) -> dict:
        return {
            "asset_id": "hoi4.model.job.unit_a",
            "asset_kind": "humanoid",
            "profile": "humanoid_unit",
            "credit_budget": budget,
            "_requires_reference_approval": True,
            "required_actions": [
                {"role": "idle", "provider_action_id": 0},
                {"role": "attack", "provider_action_id": 4},
                {"role": "death", "provider_action_id": 8},
            ],
        }

    def preflight(self, budget: int, phase: str, balance: int = 100) -> None:
        self.client.balance = balance
        spec = run_pilot.prepare_spec(self.spec(budget))
        with patch.object(run_pilot, "resolve_job_root", return_value=self.job), patch.object(
            run_pilot, "ensure_job_layout", return_value=self.job
        ), patch.object(run_pilot, "MeshyClient", return_value=self.client):
            run_pilot.preflight_selected_credits([spec], phase)

    def test_a_budget_below_the_plan_stops_before_the_balance_is_read(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "plans 49 credits but only 40.*Short by 9"):
            self.preflight(40, "full", balance=0)

    def test_a_budget_that_covers_the_plan_goes_on_to_the_balance_gate(self) -> None:
        self.preflight(49, "full")
        with self.assertRaisesRegex(RuntimeError, "balance=48, required=49"):
            self.preflight(49, "full", balance=48)

    def test_a_candidate_phase_plans_only_the_generation(self) -> None:
        self.preflight(30, "candidate")
        with self.assertRaisesRegex(RuntimeError, "plans 30 credits but only 29"):
            self.preflight(29, "candidate")

    def test_stages_that_already_succeeded_are_not_planned_again(self) -> None:
        run_pilot.write_json(run_pilot.task_file(self.job, "generation"), {"stage": "generation", "task_id": "t", "status": "SUCCEEDED"})
        self.preflight(19, "full")
        with self.assertRaisesRegex(RuntimeError, "plans 19 credits but only 18"):
            self.preflight(18, "full")


class AttemptTests(JobCase):
    def test_a_new_stage_name_does_not_reset_the_attempt_count(self) -> None:
        self.client.outcomes = [{"status": "FAILED", "consumed_credits": 0}]
        with self.assertRaises(MeshyTaskFailed):
            self.pay("rig", request("rig"), 5)
        created = self.client.created
        with self.assertRaises(AttemptLimitReached) as stop:
            self.pay("rig_second_try", request("rig"), 5)
        self.assertIn("rig@generation already has 1 paid attempt(s)", str(stop.exception))
        self.assertEqual(self.client.created, created)
        self.assertFalse(run_pilot.task_file(self.job, "rig_second_try").exists())

    def test_a_higher_contract_limit_allows_one_more_and_marks_it_a_retry(self) -> None:
        self.client.outcomes = [{"status": "FAILED", "consumed_credits": 0}]
        with self.assertRaises(MeshyTaskFailed):
            self.pay("rig", request("rig", limit=2), 5)
        self.pay("rig_second_try", request("rig", limit=2), 5)
        self.assertEqual([row["outcome"] for row in self.rows() if row["outcome"] in credits.RESERVATIONS], ["reserved", "retry"])
        with self.assertRaises(AttemptLimitReached):
            self.pay("rig_third_try", request("rig", limit=2), 5)

    def test_scopes_are_independent(self) -> None:
        self.pay("rig", request("rig"), 5)
        self.pay("generation_2_rig", request("rig", scope="rig@generation_2"), 5)
        self.pay("animation_idle", request("animation", scope="animation:idle@generation"), 3, "animation")
        self.pay("animation_attack", request("animation", scope="animation:attack@generation"), 3, "animation")

    def test_attempts_reconciled_as_never_submitted_do_not_count(self) -> None:
        attempt = credits.reserve(self.job, request("rig"), stage="rig", estimate=5, reason="x")
        self.assertEqual(credits.attempts_made(credits.read_ledger(self.job), "rig@generation"), 1)
        credits.settle(self.job, attempt, outcome="rejected", consumed=0, source="none", reason="reconciled: no task")
        self.assertEqual(credits.attempts_made(credits.read_ledger(self.job), "rig@generation"), 0)

    def test_attempt_limits_come_from_the_contract(self) -> None:
        contract = json.loads((ROOT / "config/meshy_tool_contract.json").read_text(encoding="utf-8"))
        self.assertEqual(credits.attempt_limit("rig", contract), contract["provider_policy"]["max_rig_attempts"])
        self.assertEqual(credits.attempt_limit("animation", contract), contract["provider_policy"]["max_action_attempts_per_role"])
        self.assertEqual(credits.attempt_limit("image_to_3d", contract), 1)
        self.assertEqual(credits.attempt_limit("image_to_3d", contract, declared=3), 3, "a job may declare more geometry attempts")
        self.assertEqual(credits.attempt_limit("rig", contract, declared=9), 1, "other operations ignore a job's declaration")


class LedgerTests(JobCase):
    def test_a_successful_attempt_is_reserved_then_settled_with_the_provider_figure(self) -> None:
        self.client.outcomes = [{"status": "SUCCEEDED", "consumed_credits": 30}]
        self.pay("generation", request("image_to_3d", scope="image_to_3d"), 30, "image-to-3d")
        reserved, success = self.rows()
        self.assertEqual((reserved["outcome"], reserved["estimate_credits"], reserved["consumed_credits"]), ("reserved", 30, None))
        self.assertEqual(reserved["attempt_id"], success["attempt_id"])
        self.assertEqual(
            (success["outcome"], success["consumed_credits"], success["consumed_source"], success["model"]),
            ("success", 30, "provider", "meshy-7"),
        )
        self.assertEqual(success["reconciliation"], "reconciled")
        self.assertEqual((success["balance_before"], success["balance_after"]), (285, 255))
        task = json.loads(run_pilot.task_file(self.job, "generation").read_text(encoding="utf-8"))
        self.assertEqual((task["fingerprint"], task["operation"]), ("F1", "image_to_3d"))

    def test_the_provider_figure_wins_over_a_balance_delta_inflated_by_concurrent_jobs(self) -> None:
        self.client.outcomes = [{"status": "SUCCEEDED", "consumed_credits": 30}]
        create = self.client.create(35)
        run_pilot.provider_task(
            self.client, self.job, "generation", task_type="image-to-3d", estimate=30, create=create,
            request=request("image_to_3d", scope="image_to_3d"),
        )
        success = self.rows("success")[0]
        self.assertEqual((success["consumed_credits"], success["consumed_source"]), (30, "provider"))
        self.assertEqual(success["reconciliation"], "balance_delta_mismatch")

    def test_the_balance_delta_is_used_when_the_provider_reports_nothing(self) -> None:
        self.client.outcomes = [{"status": "SUCCEEDED"}]
        self.pay("rig", request("rig"), 5)
        success = self.rows("success")[0]
        self.assertEqual((success["consumed_credits"], success["consumed_source"]), (5, "balance_delta"))

    def test_a_failed_task_is_recorded_with_what_it_cost(self) -> None:
        self.client.outcomes = [{"status": "FAILED", "consumed_credits": 0}]
        with self.assertRaises(MeshyTaskFailed):
            self.pay("rig", request("rig"), 5)
        failed = self.rows("failed")[0]
        self.assertEqual((failed["consumed_credits"], failed["stage"]), (0, "rig"))
        self.assertEqual(credits.open_reservation(credits.read_ledger(self.job), "rig"), None)

    def test_resuming_a_pending_task_settles_its_reservation_without_a_new_one(self) -> None:
        attempt = credits.reserve(self.job, request("rig"), stage="rig", estimate=5, reason="submitted")
        run_pilot.write_json(
            run_pilot.task_file(self.job, "rig"),
            {"stage": "rig", "task_id": "task-9", "status": "PENDING", "initial_response": {}},
        )
        self.client.outcomes = [{"status": "SUCCEEDED", "consumed_credits": 5}]
        self.assertEqual(self.pay("rig", request("rig"), 5), "task-9")
        self.assertEqual(self.client.created, 0)
        self.assertEqual([row["outcome"] for row in self.rows()], ["reserved", "success"])
        self.assertEqual(self.rows("success")[0]["attempt_id"], attempt)

    def test_a_succeeded_stage_is_not_paid_again_and_the_reuse_is_recorded_once(self) -> None:
        self.pay("rig", request("rig"), 5)
        for _ in range(3):
            self.pay("rig", request("rig"), 5)
        self.assertEqual(self.client.created, 1)
        reused = self.rows("reused")
        self.assertEqual(len(reused), 1)
        self.assertEqual((reused[0]["estimate_credits"], reused[0]["consumed_credits"], reused[0]["reused_from"]["tier"]), (5, 0, "job_stage"))

    def test_a_failed_stage_keeps_the_no_paid_retry_guard(self) -> None:
        self.client.outcomes = [{"status": "FAILED", "consumed_credits": 0}]
        with self.assertRaises(MeshyTaskFailed):
            self.pay("rig", request("rig", limit=5), 5)
        with self.assertRaisesRegex(RuntimeError, "No paid retry is permitted"):
            self.pay("rig", request("rig", limit=5), 5)

    def test_unknown_outcomes_and_corrupt_lines_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            credits.append_entry(self.job, stage="x", outcome="refunded")
        credits.record_local_repair(self.job, stage="s", operation="rig", estimate=5, reason="r")
        with credits.ledger_file(self.job).open("a", encoding="utf-8") as stream:
            stream.write("{not json\n")
        with self.assertRaisesRegex(ValueError, "line 2 is not valid JSON"):
            credits.read_ledger(self.job)

    def test_local_rig_route_is_recorded_once_as_a_saving(self) -> None:
        spec = {
            "asset_id": "hoi4.model.job.unit_a",
            "asset_kind": "humanoid",
            "profile": "humanoid_unit",
            "credit_budget": 60,
            "humanoid_rig_route": "blender_failure_recovery_humanoid_v1",
            "required_actions": [
                {"role": "idle", "provider_action_id": 0},
                {"role": "attack", "provider_action_id": 4},
                {"role": "death", "provider_action_id": 8},
            ],
        }
        run_pilot.record_local_rig_saving(self.job, spec)
        run_pilot.record_local_rig_saving(self.job, spec)
        saving = self.rows("local_repair")
        self.assertEqual(len(saving), 1)
        self.assertEqual((saving[0]["estimate_credits"], saving[0]["consumed_credits"]), (5 + 3 * 3, 0))


class FingerprintTests(unittest.TestCase):
    def test_same_bytes_and_arguments_give_the_same_fingerprint_whatever_the_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first, second, other = (Path(temporary) / name for name in ("a.png", "b.png", "c.png"))
            first.write_bytes(b"image")
            second.write_bytes(b"image")
            other.write_bytes(b"different")
            args = {"ai_model": "meshy-7", "should_remesh": False, "response_format": "json"}
            base = credits.request_fingerprint("meshy_image_to_3d", {**args, "file_path": str(first)})
            self.assertEqual(base, credits.request_fingerprint("meshy_image_to_3d", {**args, "file_path": str(second)}))
            self.assertNotEqual(base, credits.request_fingerprint("meshy_image_to_3d", {**args, "file_path": str(other)}))
            self.assertNotEqual(base, credits.request_fingerprint("meshy_image_to_3d", {**args, "file_path": str(first), "ai_model": "meshy-7.1"}))
            self.assertNotEqual(base, credits.request_fingerprint("meshy_remesh", {**args, "file_path": str(first)}))

    def test_presentation_arguments_do_not_change_the_fingerprint(self) -> None:
        a = credits.request_fingerprint("meshy_rig", {"input_task_id": "t", "response_format": "json"})
        b = credits.request_fingerprint("meshy_rig", {"input_task_id": "t", "response_format": "markdown"})
        self.assertEqual(a, b)
        self.assertNotEqual(a, credits.request_fingerprint("meshy_rig", {"input_task_id": "u"}))


if __name__ == "__main__":
    unittest.main()
