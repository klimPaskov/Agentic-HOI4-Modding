"""The Tripo presets (D-120): one per kind of model, pointing at the kit's other configs instead of copying them, and the card and the
job entry come from them, so a modder never sets a Tripo value by hand."""

from __future__ import annotations

import copy
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(PIPELINE_ROOT / "tripo"))

from lib import tripo_card as C
from lib import tripo_presets as P
import new_job

TEMPLATE = (PIPELINE_ROOT / "tripo" / "CARD_TEMPLATE.md").read_text(encoding="utf-8")
SOURCES = ["the owner's drawing: refs/drawings/x.jpg"]
WEAPON = {"weapon.name": "wooden mallet", "weapon.hand": "LeftHand", "weapon.grip_options.length_ratio": 0.6,
          "weapon.grip_options.grip": 0.3}
ANSWERS = {
    "humanoid": {"posture": "hunched"},
    "armed_humanoid": {"posture": "upright", **WEAPON},
    "large_creature": {"posture": "upright", "armed": True, **WEAPON},
    "winged_humanoid": {"posture": "upright", "tail": True},
    "rider": {"posture": "upright"},
}
TAG = re.compile(r"<!-- /?\w+ -->")


def entry(name: str) -> dict:
    return new_job.build_entry(name, f"t_{name}", SOURCES, "A test unit.", ANSWERS.get(name, {}))


def card(name: str) -> str:
    return C.fill(TEMPLATE, entry(name), f"t_{name}", job_folder=f"jobs/t_{name}", kit_commit="abc")


class PresetFile(unittest.TestCase):
    def test_presets_agree_with_the_kit_configs(self):
        self.assertEqual(P.check(), [])

    def test_a_preset_that_names_a_missing_unit_type_is_refused(self):
        data = copy.deepcopy(P.load())
        data["presets"]["humanoid"]["unit_type"] = "no_such_type"
        self.assertTrue(any("no_such_type" in item for item in P.check(data)))

    def test_a_static_preset_lists_no_clips_and_names_a_kind(self):
        data = copy.deepcopy(P.load())
        data["presets"]["tank"]["clips"] = {"idle": ["idle"]}
        data["presets"]["ship"]["model_kind"] = "submarine"
        found = P.check(data)
        self.assertTrue(any("tank" in item and "clips" in item for item in found))
        self.assertTrue(any("submarine" in item for item in found))

    def test_the_cap_covers_the_expected_credits(self):
        data = copy.deepcopy(P.load())
        data["presets"]["humanoid"]["cap"] = 40
        self.assertTrue(any("cap 40" in item for item in P.check(data)))

    def test_the_docs_table_lists_every_preset_and_no_other(self):
        docs = (PIPELINE_ROOT.parents[1] / "docs" / "3d-units.md").read_text(encoding="utf-8")
        section = docs.split("## Presets", 1)[1].split("\n## ", 1)[0]
        listed = re.findall(r"^\| `(\w+)` \|", section, re.M)
        self.assertEqual(sorted(listed), sorted(P.names()))

    def test_every_type_the_task_names_has_a_preset(self):
        names = set(P.names())
        for name in ("humanoid", "armed_humanoid", "large_creature", "winged_humanoid", "winged_quadruped", "mount_with_rider",
                     "tank", "plane", "ship", "building", "landmark"):
            self.assertIn(name, names)


class JobFromPreset(unittest.TestCase):
    def test_every_preset_gives_a_job_ready_for_a_card(self):
        for name in P.names():
            with self.subTest(preset=name):
                self.assertEqual(C.problems(entry(name)), [])

    def test_the_scale_reference_comes_from_the_unit_types_profile(self):
        job = entry("humanoid")
        profiles = json.loads((PIPELINE_ROOT / "config" / "asset_profiles.json").read_text(encoding="utf-8"))["profiles"]
        self.assertEqual(job["vanilla_scale_reference"]["mesh"], profiles["humanoid_unit"]["vanilla_reference"]["mesh"])
        self.assertNotIn("measurement", job["vanilla_scale_reference"])
        self.assertEqual(job["runtime_entity_scale"], 0.8)

    def test_anatomy_comes_from_the_body_preset_with_the_presets_changes(self):
        self.assertEqual(entry("humanoid")["anatomy"]["wings"], False)
        winged = entry("winged_humanoid")
        self.assertTrue(winged["anatomy"]["wings"])
        self.assertTrue(winged["anatomy"]["tail"])
        self.assertEqual(winged["tripo"]["chains"], [{"region": "wings"}])

    def test_a_large_creature_with_empty_hands_takes_beast_biped(self):
        unarmed = new_job.build_entry("large_creature", "yeti", SOURCES, "", {"posture": "hunched", "armed": False})
        self.assertEqual(unarmed["unit_type"], "beast_biped")
        self.assertNotIn("weapon", unarmed["tripo"])
        self.assertEqual(entry("large_creature")["unit_type"], "heavy_brute")

    def test_an_armed_unit_without_its_hand_is_not_ready(self):
        job = new_job.build_entry("armed_humanoid", "orc", SOURCES, "", {"posture": "upright"})
        self.assertTrue(any("hand" in item for item in C.problems(job)))

    def test_the_budget_is_the_presets_cap(self):
        self.assertEqual(entry("tank")["credit_budget"], P.get("tank")["cap"])

    def test_answers_with_a_dot_go_into_the_tripo_block(self):
        job = entry("armed_humanoid")
        self.assertEqual(job["tripo"]["weapon"]["hand"], "LeftHand")
        self.assertEqual(job["tripo"]["weapon"]["bone"], "Weapon")
        self.assertEqual(job["tripo"]["posture"], "upright")

    def test_an_old_job_without_a_preset_finds_its_preset(self):
        self.assertEqual(P.for_job({"unit_type": "infantry_melee"}), "armed_humanoid")
        self.assertEqual(P.for_job({"unit_type": "infantry_unarmed", "tripo": {"chains": [{"region": "wings"}]}}), "winged_humanoid")
        self.assertEqual(P.for_job({"unit_type": "heavy_brute"}), "large_creature")
        self.assertEqual(P.for_job({"unit_type": "mount"}), "mount_with_rider")
        self.assertEqual(P.for_job({"model_kind": "ship"}), "ship")
        # A dragon's job says it has wings: its unit type has one preset, which takes it.
        self.assertEqual(P.for_job({"unit_type": "winged_quadruped", "anatomy": {"wings": True}}), "winged_quadruped")
        self.assertIsNone(P.for_job({"unit_type": "archer"}))


class CardFromPreset(unittest.TestCase):
    def test_every_card_keeps_only_its_routes_steps(self):
        for name in P.names():
            with self.subTest(preset=name):
                text = card(name)
                self.assertEqual(TAG.findall(text), [])
                route = P.get(name)["route"]
                self.assertEqual("## 3. Rig" in text, route == "tripo_rig")
                self.assertEqual("Smart Mesh" in text, route == "static")
                self.assertEqual(f"inbox/t_{name}__model.glb" in text, route == "kit_rig")
                self.assertEqual("## 1. Weapon picture" in text, bool(entry(name).get("tripo", {}).get("weapon")))
                self.assertIn(P.get(name)["picture"]["pose"], text)
                self.assertIn(f"`{name}`", text)

    def test_the_clip_table_is_the_presets(self):
        text = card("large_creature")
        for role in P.get("large_creature")["clips"]:
            self.assertIn(f"| {role} | ", text)
        self.assertIn("| attack | `chop`, `box_01`", text)

    def test_the_armed_attack_prompt_names_the_weapon_and_hand(self):
        text = card("armed_humanoid")
        self.assertIn("raises the wooden mallet in his own left hand", text)
        self.assertNotIn("<weapon>", text)

    def test_a_static_card_names_its_polycount_kind_and_folder(self):
        text = card("ship")
        budget = json.loads((PIPELINE_ROOT / "config" / "static_kinds.json").read_text(encoding="utf-8"))["kinds"]["ship"]["triangle_budget"]
        self.assertIn(f"polycount {budget['value']:,}", text)
        self.assertIn("mod/gfx/models/units/ships/t_ship", text)
        self.assertIn("polycount 7,000", card("tank"))

    def test_only_a_building_or_landmark_card_asks_for_a_small_yard_and_thick_bracing(self):
        for name in P.names():
            with self.subTest(preset=name):
                text = card(name)
                building = name in ("building", "landmark")
                self.assertEqual("no square paved plate" in text, building)
                self.assertEqual("Redraw this exact <subject> for 3D modelling" in text, not building)


class NewJobCommand(unittest.TestCase):
    def test_writes_the_registry_adds_answers_and_the_static_job_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "3d_jobs.json"
            with mock.patch.object(new_job, "resolve_job_root", lambda slug: root / slug):
                code = new_job.main(["--jobs-config", str(registry), "--preset", "armed_humanoid", "orc", "--source", SOURCES[0],
                                     "--set", "posture=upright"])
                self.assertEqual(code, 3)  # the weapon is still missing
                code = new_job.main(["--jobs-config", str(registry), "--preset", "armed_humanoid", "orc",
                                     *sum((["--set", f"{key}={json.dumps(value)}"] for key, value in WEAPON.items()), [])])
                self.assertEqual(code, 0)
                job = json.loads(registry.read_text(encoding="utf-8"))["jobs"]["orc"]
                self.assertEqual(job["tripo"]["posture"], "upright")
                self.assertEqual(job["tripo"]["weapon"]["grip_options"]["grip"], 0.3)
                self.assertEqual(job["reference_sources"], SOURCES)
                self.assertEqual(new_job.main(["--jobs-config", str(registry), "--preset", "tank", "orc"]), 2)
                self.assertEqual(new_job.main(["--jobs-config", str(registry), "--preset", "ship", "galley", "--source", "a photo"]), 0)
                static = json.loads((root / "galley" / "inbox" / "galley.json").read_text(encoding="utf-8"))
                self.assertEqual(static, {"name": "galley", "model_kind": "ship"})

    def test_list_prints_every_preset(self):
        with mock.patch("sys.stdout") as out:
            self.assertEqual(new_job.main(["--list"]), 0)
        printed = "".join(call.args[0] for call in out.write.call_args_list)
        for name in P.names():
            self.assertIn(name, printed)


if __name__ == "__main__":
    unittest.main()
