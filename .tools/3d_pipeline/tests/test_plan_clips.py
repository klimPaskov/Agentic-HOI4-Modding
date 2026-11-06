"""The clip plan (plan_clips.py): every unit its own library clips, shared only by reskins of one base (3D-6)."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import plan_clips


def clips(result, slug):
    return {row["role"]: row.get("provider_action_id") for row in result["planned"][slug]}


class Plan(unittest.TestCase):
    def test_two_units_of_one_type_get_different_clips(self) -> None:
        result = plan_clips.plan({"jobs": {"elf_archers": {"unit_type": "archer"}, "men_archers": {"unit_type": "archer"}}})
        first, second = clips(result, "elf_archers"), clips(result, "men_archers")
        self.assertEqual(result["ran_out"], [])
        for role in first:
            self.assertNotEqual(first[role], second[role], role)
        self.assertEqual(first["idle"], 0)
        self.assertEqual(second["idle"], 11)

    def test_a_third_unit_runs_out_and_says_who_plays_the_clip(self) -> None:
        jobs = {name: {"unit_type": "archer"} for name in ("a", "b", "c")}
        result = plan_clips.plan({"jobs": jobs})
        self.assertTrue(result["ran_out"])
        self.assertTrue(all(item["unit"] == "c" for item in result["ran_out"]))
        self.assertEqual({item["played_by"] for item in result["ran_out"]}, {"a"})

    def test_a_reskin_gets_its_base_units_clips(self) -> None:
        jobs = {"knights": {"unit_type": "infantry_melee"}, "knights_winter": {"unit_type": "infantry_melee", "reskin_of": "knights"}, "guards": {"unit_type": "infantry_melee"}}
        result = plan_clips.plan({"jobs": jobs})
        self.assertEqual(clips(result, "knights"), clips(result, "knights_winter"))
        self.assertNotEqual(clips(result, "knights")["attack"], clips(result, "guards")["attack"])
        self.assertEqual(result["ran_out"], [])

    def test_a_jobs_own_actions_are_kept_and_claim_their_clips(self) -> None:
        own = [{"role": "idle", "provider_action_id": 0}, {"role": "attack", "provider_action_id": 224}]
        result = plan_clips.plan({"jobs": {"mine": {"unit_type": "archer", "required_actions": own}, "other": {"unit_type": "archer"}}})
        self.assertNotIn("mine", result["planned"])
        self.assertEqual(clips(result, "other")["idle"], 11)
        self.assertEqual(clips(result, "other")["attack"], 225)

    def test_a_seated_rider_keeps_reusing_its_own_idle(self) -> None:
        result = plan_clips.plan({"jobs": {"archers": {"unit_type": "archer"}, "riders": {"unit_type": "rider"}}})
        rows = {row["role"]: row for row in result["planned"]["riders"]}
        self.assertEqual(rows["idle"]["provider_action_id"], 11)
        self.assertEqual(rows["move"].get("reuse_role"), "idle")

    def test_an_authored_project_plans_no_library_clip(self) -> None:
        result = plan_clips.plan({"animation_policy": "authored", "jobs": {"a": {"unit_type": "archer"}}})
        self.assertEqual(result["planned"], {})
        self.assertEqual({item["role"] for item in result["authored"]}, {"idle", "move", "attack", "defend", "retreat", "death"})

    def test_a_reskin_of_an_unknown_job_is_refused(self) -> None:
        with self.assertRaises(SystemExit):
            plan_clips.plan({"jobs": {"a": {"unit_type": "archer", "reskin_of": "nobody"}}})


class Command(unittest.TestCase):
    def test_write_puts_the_plan_where_run_pilot_reads_it(self) -> None:
        import run_pilot

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "3d_jobs.json"
            path.write_text(json.dumps({"jobs": {"a": {"unit_type": "archer"}, "b": {"unit_type": "archer"}}}), encoding="utf-8")
            with redirect_stdout(io.StringIO()) as output:
                code = plan_clips.main(["--jobs-config", str(path), "--write"])
            written = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["verdict"], "pass")
        b = written["jobs"]["b"]
        self.assertEqual(run_pilot.apply_unit_type(dict(b))["required_actions"], b["required_actions"])
        self.assertEqual([row["provider_action_id"] for row in b["required_actions"] if row["role"] == "idle"], [11])

    def test_running_out_escalates_and_writes_nothing_unasked(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "3d_jobs.json"
            path.write_text(json.dumps({"jobs": {name: {"unit_type": "archer"} for name in "abc"}}), encoding="utf-8")
            before = path.read_text(encoding="utf-8")
            with redirect_stdout(io.StringIO()) as output:
                code = plan_clips.main(["--jobs-config", str(path)])
            self.assertEqual(path.read_text(encoding="utf-8"), before)
        payload = json.loads(output.getvalue())
        self.assertEqual((code, payload["verdict"]), (1, "escalate"))
        self.assertEqual(payload["escalate"]["rules"], ["CLIPS-RAN-OUT"])


if __name__ == "__main__":
    unittest.main()
