"""D-136: every distinct unit type of a mod has its own animations. A hand-kept claims file got three double claims in minutes, so
the claims are a tool: an atomic claim per mod, the earliest wins, and the route refuses a job that uses a clip another unit holds."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(PIPELINE_ROOT / "tripo"))

from lib import anim_claims as A
from lib import tripo_card as C
from lib import tripo_presets as P
import anim_claims as cli
import new_job
import tripo_intake

ROLES = {"idle": "idle", "move": "walk", "attack": "chop", "defend": "hit_to_stomach", "retreat": "flee_01", "death": "defeat_03"}
TEMPLATE = (PIPELINE_ROOT / "tripo" / "CARD_TEMPLATE.md").read_text(encoding="utf-8")
WEAPON = {"weapon.name": "hand axe", "weapon.hand": "LeftHand", "weapon.grip_options.length_ratio": 0.6, "weapon.grip_options.grip": 0.3}


class Registry(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_earliest_claim_holds_a_clip(self):
        self.assertEqual(A.claim(self.root, "unit_a", {"defend": "hit_to_stomach"})["claimed"], ["hit_to_stomach"])
        result = A.claim(self.root, "unit_b", {"defend": "Hit_To_Stomach", "idle": "idle"})
        self.assertEqual(result["held"]["hit_to_stomach"]["unit"], "unit_a")
        self.assertEqual(result["claimed"], [])
        self.assertNotIn("idle", A.holders(self.root))  # nothing of a refused claim is written

    def test_claiming_again_is_harmless(self):
        A.claim(self.root, "unit_a", {"idle": "idle"})
        self.assertEqual(A.claim(self.root, "unit_a", {"idle": "idle"})["already"], ["idle"])
        self.assertEqual(len(A.load(self.root)["claims"]), 1)

    def test_concurrent_claims_leave_one_holder(self):
        results = {}

        def worker(unit):
            results[unit] = A.claim(self.root, unit, {"defend": "hit_to_side"})

        threads = [threading.Thread(target=worker, args=(f"unit_{n}",)) for n in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        winners = [unit for unit, result in results.items() if result["claimed"]]
        self.assertEqual(len(winners), 1)
        self.assertEqual([c["unit"] for c in A.load(self.root)["claims"]], winners)

    def test_a_reskin_shares_its_base_units_clips(self):
        A.claim(self.root, "spearman", {"idle": "idle"})
        self.assertEqual(A.claim(self.root, "spearman_winter", {"idle": "idle"}, reskin_of="spearman")["held"], {})
        self.assertEqual(A.conflicts(self.root, "spearman_winter", ["idle"], "spearman"), {})
        self.assertIn("idle", A.conflicts(self.root, "archer", ["idle"]))

    def test_tiles_are_named_as_they_export(self):
        self.assertEqual(A.export_name("defeat"), "defeat_02")
        self.assertEqual(A.export_name("defeat_02"), "defeat_03")
        self.assertEqual(A.export_name("fall"), "fall")

    def test_seeding_from_the_hand_kept_table(self):
        table = "\n".join([
            "| Mod | Unit type (subject) | State | Clip | Source (free preset, library clip or made with task id) | Worker | Time |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            "| MODA | Beast | defend | hit_to_stomach | free preset | w1 | 2026-11-22 |",
            "| MODA | Brute (with a mallet) | defend | hit_to_stomach | free preset | w2 | 2026-11-22 |",
            "| MODA | Brute | idle | planned made: shifts weight (text-to-motion, 20) | planned | w2 | 2026-11-22 |",
            "| MODA | Flyer (winged) | idle, move | idle | free preset idle | w3 | 2026-11-22 |",
            "| MODA | Steed | idle | the kit's quadruped clips | made in Blender, free | w4 | 2026-11-22 |",
            "| MODB | Other | idle | walk | free preset | w5 | 2026-11-22 |",
        ])
        rows = A.import_markdown(self.root, table, "MODA")["rows"]
        self.assertEqual([(u, c, s) for u, _r, c, s in rows],
                         [("beast", "hit_to_stomach", "ok"), ("brute", "hit_to_stomach", "held"), ("flyer", "idle", "ok"), ("flyer", "idle", "ok")])
        self.assertEqual(A.holders(self.root)["hit_to_stomach"]["unit"], "beast")
        self.assertNotIn("walk", A.holders(self.root))


class InTheRoute(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        A.claim(self.root, "other_unit", {"defend": "hit_to_stomach", "death": "defeat_03"})
        self.job = new_job.build_entry("armed_humanoid", "axe_fighter", ["the mod's art"], "", {"posture": "upright", **WEAPON})
        self.job["mod_root"] = str(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_card_check_and_the_intake_refuse_a_held_clip(self):
        job = copy.deepcopy(self.job)
        job["tripo"]["roles"] = dict(ROLES)
        found = [item for item in C.problems(job) if "UNIT-ANIM-SHARED" in item]
        self.assertEqual(len(found), 1)
        self.assertIn("hit_to_stomach (held by other_unit for defend)", found[0])
        with self.assertRaises(ValueError):
            tripo_intake.refuse_shared_clips(job, "axe_fighter")
        job["tripo"]["roles"]["defend"] = "hit_to_body_01"
        job["tripo"]["roles"]["death"] = "fall"
        self.assertEqual([item for item in C.problems(job) if "UNIT-ANIM-SHARED" in item], [])
        tripo_intake.refuse_shared_clips(job, "axe_fighter")

    def test_the_clip_table_strikes_held_presets_and_plans_own_clips(self):
        text = C.fill(TEMPLATE, self.job, "axe_fighter", job_folder="jobs/axe_fighter", kit_commit="abc")
        self.assertIn("~~`hit_to_stomach`~~ (held by other_unit)", text)
        self.assertIn("~~`defeat_02`~~ (held by other_unit)", text)  # the tile defeat_02 exports as defeat_03
        self.assertIn("`hit_to_body_01`", text)
        self.assertIn("make: `raises the hand axe across its body", text)
        self.assertNotIn("<weapon>", text)

    def test_the_command_claims_checks_and_refuses(self):
        registry = self.root / "jobs.json"
        job = copy.deepcopy(self.job)
        job["tripo"]["roles"] = {**ROLES, "defend": "hit_to_body_01", "death": "fall"}
        registry.write_text(json.dumps({"jobs": {"axe_fighter": job}}), encoding="utf-8")
        self.assertEqual(cli.main(["check", "--jobs-config", str(registry), "axe_fighter"]), 0)
        self.assertEqual(cli.main(["claim", "--jobs-config", str(registry), "axe_fighter", "--source", "free preset"]), 0)
        self.assertEqual(A.holders(self.root)["chop"]["unit"], "axe_fighter")
        job["tripo"]["roles"]["defend"] = "hit_to_stomach"
        registry.write_text(json.dumps({"jobs": {"axe_fighter": job}}), encoding="utf-8")
        self.assertEqual(cli.main(["claim", "--jobs-config", str(registry), "axe_fighter"]), 3)


class OutsideRegistry(unittest.TestCase):
    """The record never ships with the mod. A job's `anim_registry`, or the command's --registry, keeps it as a .json file elsewhere."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.registry = self.dir / "notes" / "mod_a.json"
        A.claim(self.registry, "other_unit", {"defend": "hit_to_stomach"})

    def tearDown(self):
        self.tmp.cleanup()

    def test_release_gives_back_only_the_holders_own_claim(self):
        # A worker claimed a clip, then the intake refused it (hip travel over 0.1, zin_demon 2026-11-23): it gives the clip back.
        A.claim(self.registry, "demon", {"retreat": "flee_02", "defend": "A tall winged demon is struck in the chest"})
        A.claim(self.registry, "late_unit", {"retreat": "flee_02"})  # held: nothing is written for late_unit
        reg = str(self.registry)
        self.assertEqual(cli.main(["release", "--registry", reg, "other_unit", "flee_02"]), 3)  # not the holder
        self.assertEqual(cli.main(["release", "--registry", reg, "demon", "hit_to_stomach"]), 3)  # another unit's clip
        self.assertEqual(cli.main(["release", "--registry", reg, "demon", "walk"]), 3)  # never claimed
        self.assertEqual(A.holders(self.registry)["flee_02"]["unit"], "demon")
        self.assertEqual(cli.main(["release", "--registry", reg, "demon", "flee_02"]), 0)
        self.assertEqual(cli.main(["release", "--registry", reg, "demon", "a_tall_winged_demon_is_struck_in_the_chest"]), 0)
        holders = A.holders(self.registry)
        self.assertNotIn("flee_02", holders)
        self.assertNotIn("a_tall_winged_demon_is_struck_in_the_chest", holders)
        self.assertEqual(holders["hit_to_stomach"]["unit"], "other_unit")
        self.assertEqual(A.claim(self.registry, "late_unit", {"retreat": "flee_02"})["claimed"], ["flee_02"])
        with self.assertRaises(A.ClaimError):
            A.release(self.registry, "demon", "flee_02")

    def test_a_json_path_is_the_registry_itself(self):
        self.assertTrue(self.registry.exists())
        self.assertFalse((self.dir / "notes" / ".hoi4_3d").exists())
        self.assertEqual(A.holders(self.registry)["hit_to_stomach"]["unit"], "other_unit")

    def test_the_jobs_anim_registry_is_read_by_the_card_and_the_intake(self):
        job = new_job.build_entry("humanoid", "walker", ["the mod's art"], "", {"posture": "upright"})
        job["anim_registry"] = str(self.registry)
        job["tripo"]["roles"] = {**ROLES, "attack": "a soldier lunges"}
        self.assertTrue(any("UNIT-ANIM-SHARED" in item for item in C.problems(job)))
        with self.assertRaises(ValueError):
            tripo_intake.refuse_shared_clips(job, "walker")

    def test_the_command_takes_registry(self):
        jobs = self.dir / "jobs.json"
        job = {"provider": "tripo", "tripo": {"roles": {"idle": "idle"}}}
        jobs.write_text(json.dumps({"jobs": {"walker": job}}), encoding="utf-8")
        self.assertEqual(cli.main(["claim", "--jobs-config", str(jobs), "walker", "--registry", str(self.registry)]), 0)
        self.assertEqual(A.holders(self.registry)["idle"]["unit"], "walker")
        from unittest import mock

        with mock.patch("sys.stdout"):
            self.assertEqual(cli.main(["list", "--registry", str(self.registry)]), 0)


class OwnClipsPerType(unittest.TestCase):
    def test_every_tripo_rigged_type_has_an_own_clip_prompt_for_each_state(self):
        for name in P.names():
            preset = P.get(name)
            if preset["route"] != "tripo_rig":
                continue
            with self.subTest(preset=name):
                for role in ("idle", "move", "defend", "retreat", "death"):
                    prompt = preset["made_clips"][role]
                    self.assertTrue(prompt and len(prompt) < 266)
                self.assertGreaterEqual(preset["expected_credits"][1], 170)

    def test_a_preset_without_own_clip_prompts_is_refused(self):
        data = copy.deepcopy(P.load())
        del data["presets"]["humanoid"]["made_clips"]["idle"]
        self.assertTrue(any("D-136" in item for item in P.check(data)))


if __name__ == "__main__":
    unittest.main()
