"""The credits ledger and the `run_pilot.py --credits-report` option, tested on real zin pilot records."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import credits
from lib.credits import PaidRequest

ZIN_RECORDS = ROOT / "tests" / "fixtures" / "zin_credit_records"
MEN = ZIN_RECORDS / "zin_men_infantry"
ORCS = ZIN_RECORDS / "zin_orcs_warrior"


def request(operation: str, scope: str = "") -> PaidRequest:
    return PaidRequest(operation, f"meshy_{operation}", "meshy-7.1" if operation == "image_to_3d" else None, "FP", scope or operation, 2, 200)


def paid_attempt(job: Path, stage: str, operation: str, *, outcome: str, consumed, estimate: int, scope: str = "", source: str = "provider") -> None:
    attempt = credits.reserve(job, request(operation, scope), stage=stage, estimate=estimate, reason="submitted")
    credits.settle(job, attempt, outcome=outcome, consumed=consumed, source=source, reason="ended")


class ZinRecordTests(unittest.TestCase):
    """49 credits per unit: generation 30, remesh 5, rig 5, idle, attack and death 3 each."""

    def test_a_job_without_a_ledger_is_read_from_its_reconciliation_records(self) -> None:
        rows = credits.ledger_entries(MEN)
        self.assertEqual(
            {row["stage"]: row["consumed_credits"] for row in rows},
            {
                "generation": 30,
                "rig_remesh": 5,
                "rig": 5,
                "animation_idle": 3,
                "animation_attack": 3,
                "animation_death": 3,
            },
        )
        self.assertEqual({row["outcome"] for row in rows}, {"success"})
        self.assertEqual({row["operation"] for row in rows}, {"image_to_3d", "remesh", "rig", "animation"})
        self.assertEqual(sum(row["consumed_credits"] for row in rows), 49)

    def test_the_provider_figure_wins_where_concurrent_jobs_inflated_the_balance_delta(self) -> None:
        generation = next(row for row in credits.ledger_entries(ORCS) if row["stage"] == "generation")
        self.assertEqual((generation["consumed_credits"], generation["consumed_source"]), (30, "provider"))
        self.assertEqual(generation["reconciliation"], "balance_delta_mismatch")

    def test_report_over_two_real_jobs(self) -> None:
        report = credits.credits_report(credits.find_job_roots(ZIN_RECORDS))
        self.assertEqual([job["job"] for job in report["jobs"]], ["zin_men_infantry", "zin_orcs_warrior"])
        self.assertEqual([job["consumed"] for job in report["jobs"]], [49, 49])
        totals = report["totals"]
        self.assertEqual(totals["consumed"], 98)
        self.assertEqual((totals["failed"], totals["wasted"], totals["avoided_reuse"], totals["avoided_local_repair"]), (0, 0, 0, 0))
        self.assertEqual(totals["balance_delta_mismatch"], 5)
        self.assertEqual(
            report["by_stage"],
            {
                "generation": 60,
                "rig_remesh": 10,
                "rig": 10,
                "animation_idle": 6,
                "animation_attack": 6,
                "animation_death": 6,
            },
        )
        self.assertEqual(report["by_model"], {"unrecorded": 60, "(not model-specific)": 38})

    def test_report_for_one_job_and_for_a_root_find_the_same_jobs(self) -> None:
        self.assertEqual(credits.find_job_roots(MEN), [MEN.resolve()])
        self.assertEqual(len(credits.find_job_roots(ZIN_RECORDS)), 2)
        self.assertEqual(credits.credits_report([MEN])["totals"]["consumed"], 49)

    def test_the_fixture_records_hold_no_signed_download_urls(self) -> None:
        for path in ZIN_RECORDS.rglob("*.json"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("Signature=", text, path.name)


class CommandLineTests(unittest.TestCase):
    def run_report(self, *arguments: str) -> subprocess.CompletedProcess:
        environment = {key: value for key, value in os.environ.items() if key != "MESHY_API_KEY"}
        return subprocess.run(
            [sys.executable, "-B", str(ROOT / "run_pilot.py"), "--credits-report", *arguments],
            capture_output=True, text=True, encoding="utf-8", env=environment, timeout=120,
        )

    def test_the_option_prints_the_totals_without_an_api_key(self) -> None:
        completed = self.run_report(str(ZIN_RECORDS))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Credits report for 2 job(s)", completed.stdout)
        self.assertIn("consumed 98 credits, of which 0 on failed attempts", completed.stdout)
        self.assertIn("generation: 60", completed.stdout)
        self.assertIn("zin_orcs_warrior: 49 consumed, 0 wasted, 0 avoided", completed.stdout)

    def test_one_job_can_be_reported_alone(self) -> None:
        completed = self.run_report(str(MEN))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Credits report for 1 job(s)", completed.stdout)

    def test_an_empty_location_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            completed = self.run_report(temporary)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("No job folders", completed.stdout)

    def test_provider_work_still_needs_the_api_key_and_a_registry(self) -> None:
        environment = {key: value for key, value in os.environ.items() if key != "MESHY_API_KEY"}

        def run(*arguments: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, "-B", str(ROOT / "run_pilot.py"), *arguments],
                capture_output=True, text=True, encoding="utf-8", env=environment, timeout=120,
            )

        without_registry = run()
        self.assertEqual(without_registry.returncode, 2)
        self.assertIn("--jobs-config is required", without_registry.stderr)
        without_key = run("--jobs-config", "jobs.json")
        self.assertEqual(without_key.returncode, 2)
        self.assertIn("MESHY_API_KEY is missing", without_key.stdout)


class LedgerReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.job = Path(self.temp.name) / "models_3d" / "unit_x"
        (self.job / "provider").mkdir(parents=True)

    def report(self) -> dict:
        return credits.credits_report([self.job])

    def test_failed_replaced_reused_and_repaired_credits_are_told_apart(self) -> None:
        paid_attempt(self.job, "generation", "image_to_3d", outcome="success", consumed=30, estimate=30)
        paid_attempt(self.job, "generation_2", "image_to_3d", outcome="success", consumed=30, estimate=30)
        paid_attempt(self.job, "generation_2_rig", "rig", outcome="failed", consumed=5, estimate=5, scope="rig@generation_2")
        paid_attempt(self.job, "generation_2_rig_again", "rig", outcome="success", consumed=None, estimate=5, scope="rig@generation_2", source="unknown")
        credits.record_reuse(self.job, stage="generation_3", operation="image_to_3d", estimate=30, reason="same image in unit_y")
        credits.record_local_repair(self.job, stage="local_humanoid_rig", operation="rig_and_animation", estimate=14, reason="Blender rig")
        credits.reject(self.job, request("rig", "rig@generation_2"), stage="generation_2_rig_third", estimate=5, reason="attempt limit")
        totals = self.report()["totals"]
        self.assertEqual(totals["consumed"], 65, "30 + 30 + 5 failed; the unknown attempt adds nothing known")
        self.assertEqual(totals["failed"], 5)
        self.assertEqual(totals["wasted"], 35, "the replaced first generation (30) and the failed rig (5)")
        self.assertEqual((totals["avoided_reuse"], totals["avoided_local_repair"]), (30, 14))
        self.assertEqual((totals["retries"], totals["rejected"], totals["unknown_consumption"]), (2, 1, 1))

    def test_totals_per_model_and_stage(self) -> None:
        paid_attempt(self.job, "generation", "image_to_3d", outcome="success", consumed=30, estimate=30)
        paid_attempt(self.job, "rig", "rig", outcome="success", consumed=5, estimate=5)
        report = self.report()
        self.assertEqual(report["by_model"], {"meshy-7.1": 30, "(not model-specific)": 5})
        self.assertEqual(report["by_stage"], {"generation": 30, "rig": 5})

    def test_legacy_records_fill_in_only_the_stages_the_ledger_does_not_cover(self) -> None:
        credits_dir = self.job / "provider" / "credits"
        tasks_dir = self.job / "provider" / "tasks"
        for stage, spent in (("generation", 30), ("rig", 5)):
            run_write(credits_dir / f"{stage}_reconciliation.json", {"stage": stage, "provider_consumed_credits": spent, "status": "reconciled"})
            run_write(tasks_dir / f"{stage}.json", {"stage": stage, "task_id": stage, "task_type": "image-to-3d" if stage == "generation" else "rigging", "status": "SUCCEEDED"})
        paid_attempt(self.job, "generation", "image_to_3d", outcome="success", consumed=30, estimate=30)
        self.assertEqual(self.report()["totals"]["consumed"], 35, "generation is counted once, from the ledger")

    def test_a_failed_legacy_task_counts_as_failed_credits(self) -> None:
        run_write(self.job / "provider" / "tasks" / "rig.json", {"stage": "rig", "task_id": "t", "task_type": "rigging", "status": "FAILED", "consumed_credits": 5})
        totals = self.report()["totals"]
        self.assertEqual((totals["consumed"], totals["failed"], totals["wasted"]), (5, 5, 5))

    def test_a_reused_task_record_is_not_double_counted(self) -> None:
        run_write(self.job / "provider" / "tasks" / "generation.json", {"stage": "generation", "task_id": "t", "task_type": "image-to-3d", "status": "SUCCEEDED", "consumed_credits": 0, "reused_from": {"job": "unit_y"}})
        self.assertEqual(self.report()["totals"]["consumed"], 0)

    def test_the_report_text_names_every_total(self) -> None:
        paid_attempt(self.job, "generation", "image_to_3d", outcome="failed", consumed=30, estimate=30)
        text = credits.format_report(self.report())
        for expected in ("consumed 30 credits, of which 30 on failed attempts", "wasted 30 credits", "avoided 0 credits by reuse", "By model", "By stage", "By job", "unit_x: 30 consumed, 30 wasted"):
            self.assertIn(expected, text)


def run_write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
