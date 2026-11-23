"""One entry point (D-120): fixed rules turn a few answers about the picture into the preset, with a confirm sentence that gives the card's
and the Canvas's cost. One answer set per type, the refusals of D-110 and D-123, and the next command."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(PIPELINE_ROOT / "tripo"))

from lib import tripo_presets as P
import new_job
import pick_preset as K

REF = ["the mod's art: gfx/units/axe_fighter.png"]
ANSWERS = {
    "humanoid": {"kind": "unit", "legs": 2},
    "armed_humanoid": {"kind": "unit", "legs": 2, "weapon": True, "hand": "LeftHand"},
    "large_creature": {"kind": "unit", "legs": 2, "large": True},
    "winged_humanoid": {"kind": "unit", "legs": 2, "wings": True},
    "winged_quadruped": {"kind": "unit", "legs": 4, "wings": True},
    "mount_with_rider": {"kind": "unit", "legs": 4, "rider": True},
    "quadruped": {"kind": "unit", "legs": 4},
    "tank": {"kind": "vehicle"},
    "plane": {"kind": "plane"},
    "ship": {"kind": "ship"},
    "building": {"kind": "building"},
    "landmark": {"kind": "landmark"},
}


class PickPreset(unittest.TestCase):
    def test_each_answer_set_gives_its_preset(self):
        for name, answers in ANSWERS.items():
            with self.subTest(preset=name):
                self.assertEqual(K.pick(answers), name)

    def test_every_preset_but_the_rider_is_reachable(self):
        self.assertEqual(set(P.names()) - set(ANSWERS), {"rider"})  # the rider is a job of mount_with_rider

    def test_an_armed_large_creature_and_an_armed_winged_one(self):
        self.assertEqual(K.pick({"kind": "unit", "legs": 2, "large": True, "weapon": True}), "large_creature")
        self.assertEqual(K.pick({"kind": "unit", "legs": 2, "wings": True, "weapon": True}), "winged_humanoid")

    def test_answers_that_fit_no_preset_are_refused(self):
        for answers in ({"kind": "unit", "legs": 0}, {"kind": "unit", "legs": 4, "weapon": True}, {"kind": "unit", "legs": 2, "rider": True},
                        {"kind": "tree"}):
            with self.subTest(answers=answers):
                with self.assertRaises(K.PickError):
                    K.pick(answers)

    def test_no_reference_is_refused_before_any_picture_step(self):
        with self.assertRaises(K.PickError) as caught:
            K.run(ANSWERS["humanoid"], [], [], "x")
        self.assertIn("D-110", str(caught.exception))

    def test_a_weapon_needs_its_hand(self):
        with self.assertRaises(K.PickError):
            K.run({"kind": "unit", "legs": 2, "weapon": True}, REF, [], "x")

    def test_the_confirm_sentence_gives_both_costs_and_the_cap(self):
        result = K.run({**ANSWERS["armed_humanoid"], "name": "A fighter with an axe"}, REF, [], "axe_fighter")
        self.assertEqual(result["preset"], "armed_humanoid")
        self.assertIn("A fighter with an axe: humanoid with a weapon (preset armed_humanoid).", result["confirm"])
        self.assertIn("The card costs about 80 to 200 credits", result["confirm"])
        self.assertIn("the Canvas workflow Armed unit about 95 to 215", result["confirm"])
        self.assertIn("cap 200", result["confirm"])
        self.assertTrue(result["confirm"].endswith("Right?"))
        self.assertIn("chop", " ".join(result["fitting_clips"]["attack"]))

    def test_an_unarmed_large_creature_takes_the_rigged_workflow(self):
        self.assertEqual(K.costs("large_creature", False)["canvas_workflow"], "Rigged unit")
        self.assertEqual(K.costs("large_creature", True)["canvas_workflow"], "Armed unit")

    def test_a_private_reference_is_marked_and_never_offered_to_tripo(self):
        result = K.run(ANSWERS["humanoid"], [*REF, "the owner's drawing 35"], ["the owner's drawing 35"], "axe_fighter")
        self.assertIn("D-123", result["private_note"])
        self.assertIn('--private-source "the owner\'s drawing 35"', result["next"])
        self.assertIn('--source "the mod\'s art: gfx/units/axe_fighter.png"', result["next"])

    def test_the_next_command_writes_a_job_of_that_preset(self):
        result = K.run({**ANSWERS["armed_humanoid"]}, REF, ["the owner's drawing 35"], "axe_fighter")
        self.assertIn("--preset armed_humanoid axe_fighter", result["next"])
        self.assertIn("--set weapon.hand=LeftHand", result["next"])
        with tempfile.TemporaryDirectory() as tmp:
            registry = Path(tmp) / "jobs.json"
            with mock.patch.object(new_job, "resolve_job_root", lambda slug: Path(tmp) / slug):
                new_job.main(["--jobs-config", str(registry), "--preset", "armed_humanoid", "axe_fighter", "--source", REF[0],
                              "--private-source", "the owner's drawing 35", "--set", "weapon.hand=LeftHand"])
            job = json.loads(registry.read_text(encoding="utf-8"))["jobs"]["axe_fighter"]
        self.assertEqual(job["reference_sources"], [REF[0], "private, never uploaded: the owner's drawing 35"])
        self.assertEqual(job["tripo"]["weapon"]["hand"], "LeftHand")

    def test_the_command_prints_the_sentence_and_refuses_with_exit_2(self):
        with mock.patch("sys.stdout") as out:
            self.assertEqual(K.main(["--kind", "ship", "--reference", REF[0], "--name", "A galley"]), 0)
        printed = "".join(call.args[0] for call in out.write.call_args_list)
        self.assertIn("A galley: ship (preset ship).", printed)
        with mock.patch("sys.stderr"):
            self.assertEqual(K.main(["--kind", "unit", "--legs", "2"]), 2)


if __name__ == "__main__":
    unittest.main()
