"""The effects layer (lib/unit_effects.py, tripo/effects_stage.py, config/effects.json): fit, locators, frames, checks, particle copies and
entity events. A synthetic winged biped that faces +z (its toes point there), and the committed survey of vanilla. No Blender, no game."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import test_deformation_checks as TD
from lib import pdx_deform, unit_effects as E, unit_wiring as W
from lib.pdx_binary import read
from lib.pdx_write import write
from test_tripo_chain_lift import WingedBiped, local
from test_tripo_pose_upper import turn

FIRE = {"profiles": ["hellfire"], "setting": ["fire_creature"]}
EYES = {"profiles": ["necro_eyes"], "setting": ["magic"]}


class Config(unittest.TestCase):
    def test_the_shipped_profiles_agree_with_themselves_and_with_vanilla(self) -> None:
        self.assertEqual(E.check_config(), [])

    def test_every_preset_effect_is_a_profile(self) -> None:
        presets = json.loads((PIPELINE / "config" / "tripo_presets.json").read_text(encoding="utf-8"))["presets"]
        profiles = E.load()["profiles"]
        for name, preset in presets.items():
            for profile in preset.get("effects", []):
                self.assertIn(profile, profiles, f"preset {name}")

    def test_the_survey_measured_seconds(self) -> None:
        """An event's time is the clip's seconds: each destroyed landmark that fires after its start does so within 0.3 s of the frame its
        clip hides a part (frames would put the explosion at frame 2 of a 6 s collapse)."""

        rows = [row for row in E.load_vanilla()["time_unit"] if row["first_event_time"] > 0.5]
        self.assertGreaterEqual(len(rows), 5)
        for row in rows:
            self.assertLessEqual(abs(row["hide_seconds"] - row["first_event_time"]), 0.3, row["entity"])

    def test_a_vanilla_particle_is_fired_as_it_is(self) -> None:
        data = E.load()
        data["particles"]["tank_cannon_flash"]["colour"] = [1, 2, 3]
        self.assertTrue(any("fired as it is" in p for p in E.check_config(data)))


class Fit(unittest.TestCase):
    def test_a_world_without_gunpowder_never_gets_a_muzzle_flash(self) -> None:
        problems = E.fit_problems(["tank_cannon"], ["magic"], E.load())
        self.assertTrue(problems and "gunpowder" in problems[0])

    def test_the_preset_bounds_the_profiles(self) -> None:
        problems = E.fit_problems(["fire_breath"], ["fire_creature"], E.load(), allowed=["spell_cast"])
        self.assertTrue(any("not one the preset lists" in p for p in problems))

    def test_a_setting_may_be_a_mapping(self) -> None:
        self.assertEqual(E.setting_tags({"gunpowder": False, "magic": True}), ["magic"])


class Biped(WingedBiped):
    def strike(self, peak: int = 12, frames: int = 30) -> Path:
        """The right arm swings from out to the side to straight forward (+z) by `peak` and back."""

        def pose(frame: int):
            share = max(0.0, 1.0 - abs(frame - peak) / peak)
            return {"RightArm": (local("RightArm"), turn("y", -90.0 * share))}

        path = self.folder / "unit_attack.anim"
        TD.write_anim(path, frames, pose)
        return path

    def test_a_fire_locator_goes_on_the_hand_tip_and_fires_at_the_strike(self) -> None:
        self.strike(peak=12)
        plan = E.make_plan(self.folder, "unit", FIRE)
        hand = next(l for l in plan["locators"] if l["name"] == "fire_hand_r")
        self.assertEqual(hand["bone"], "RightHand")
        self.assertGreater(hand["rest"][0], 0.45, "past the hand's joint, toward the fingers")
        event = next(e for e in plan["events"] if e["node"] == "fire_hand_r")
        self.assertEqual(event["frame"], 12)
        self.assertAlmostEqual(event["time"], 0.4)
        props = E.mesh_locators(read(self.mesh_path))["fire_hand_r"]
        self.assertEqual(props["pa"], ["RightHand"])
        self.assertEqual(E.findings(self.folder, "unit", plan), [])

    def test_the_front_comes_from_the_toes(self) -> None:
        self.assertGreater(float(E.front(self.mesh)[2]), 0.9)

    def test_a_new_clip_makes_the_plan_stale(self) -> None:
        self.strike(peak=12)
        plan = E.make_plan(self.folder, "unit", FIRE)
        self.strike(peak=20)
        rules = {f["rule"] for f in E.findings(self.folder, "unit", plan)}
        self.assertIn("EFFECT-FRAME", rules)

    def test_a_locator_on_the_wrong_bone_is_found(self) -> None:
        self.strike()
        plan = E.make_plan(self.folder, "unit", FIRE)
        root = read(self.mesh_path)
        hand = next(l for l in plan["locators"] if l["name"] == "fire_hand_r")
        hips = E.bind_world(self.mesh)[self.mesh.bones.index("Hips")][:3, 3]
        for node in root.child("locator").children:
            if node.name == "fire_hand_r":  # the same place at rest, but hung from the hips
                node.properties["pa"] = ["Hips"]
                node.properties["p"] = [float(v) for v in np.asarray(hand["rest"]) - hips]
        write(self.mesh_path, root)
        rules = [f["rule"] for f in E.findings(self.folder, "unit", plan)]
        self.assertIn("EFFECT-LOCATOR", rules)
        self.assertIn("EFFECT-ON-PART", rules, "a locator on the hips stays behind while the hand swings away")

    def test_a_job_outside_its_world_is_refused_before_anything_is_written(self) -> None:
        self.strike()
        before = self.mesh_path.read_bytes()
        with self.assertRaises(E.EffectsError):
            E.make_plan(self.folder, "unit", {"profiles": ["tank_cannon"], "setting": ["magic"]})
        self.assertEqual(self.mesh_path.read_bytes(), before)

    def test_recoil_is_the_first_frame_the_gun_moves_back(self) -> None:
        def pose(frame: int):
            back = 0.0 if frame < 7 else 0.05 * (1.0 - (frame - 7) / 23.0)
            hand = local("RightHand")
            return {"RightHand": ((hand[0] - back, hand[1], hand[2]), (0.0, 0.0, 0.0, 1.0))}

        TD.write_anim(self.folder / "unit_attack.anim", 30, pose)
        anim = pdx_deform.load_anim(self.folder / "unit_attack.anim")
        frame, how = E.measure_frame("recoil", self.mesh, anim, "RightHand", np.array([0.5, 0.88, 0.0]))
        self.assertEqual(frame, 7)
        self.assertEqual(how["bone"], "RightHand")


class Glow(WingedBiped):
    def clips(self) -> None:
        for role in ("idle", "move", "attack", "death"):
            TD.write_anim(self.folder / f"unit_{role}.anim", 10, lambda frame: {})

    def test_the_eyes_sit_side_by_side_inside_the_head_and_glow_in_every_state_but_death(self) -> None:
        self.clips()
        plan = E.make_plan(self.folder, "unit", EYES)
        eyes = {l["name"]: l for l in plan["locators"]}
        left, right = eyes["glow_eye_l"], eyes["glow_eye_r"]
        self.assertEqual((left["bone"], right["bone"]), ("Head", "Head"))
        self.assertLess(left["rest"][0], right["rest"][0], "the rig's left hand is at -x on this biped, and so is its left eye")
        head = self.mesh.positions[E.region(self.mesh, "Head")]
        self.assertLess(left["rest"][2], float(head[:, 2].max()), "pushed back from the head's front, into the hood")
        roles = {e["role"] for e in plan["events"]}
        self.assertEqual(roles, {"idle", "move", "attack", "defend", "support_attack"}, "no retreat clip, so no retreat, and never death")
        self.assertTrue(all(e["loop"] and e["frame"] == 0 for e in plan["events"]))
        self.assertEqual(E.findings(self.folder, "unit", plan), [])

    def test_a_wing_tip_is_found_on_its_side(self) -> None:
        self.clips()
        plan = E.make_plan(self.folder, "unit", {"profiles": ["wing_gust"], "setting": []})
        tips = {l["name"]: l for l in plan["locators"]}
        self.assertLess(tips["gust_wing_l"]["rest"][0], -1.0)
        self.assertGreater(tips["gust_wing_r"]["rest"][0], 1.0)
        self.assertTrue(tips["gust_wing_l"]["bone"].startswith("WingL"))


class Entity(unittest.TestCase):
    ENTITY = (
        'entity = {\n\tname = "t_entity"\n\tpdxmesh = "t_mesh"\n'
        '\tstate = { name = "idle"\t\tanimation = "idle" }\n'
        '\tstate = { name = "attack"\t\tanimation = "attack"\n'
        '\t\tevent = { time = 0 node="barrel" particle = "rifle_muzzle_particle"  keep_particle = yes sound = { soundeffect = light_armour_fire } }\n'
        '\t\tevent = { time = 0 node="exhaust" particle = "tank_exhaust_particle" }\n'
        '\t}\n'
        '\tstate = { name = "support_attack"\tanimation = "attack" }\n'
        '\tscale = 0.7\n}'
    )

    def test_the_plan_replaces_vanillas_event_at_its_locator_and_adds_a_death(self) -> None:
        events = [{"role": r, "node": "barrel", "time": 0.033, "particle": "light_tank_attack_barrel_particle"} for r in ("attack", "support_attack")]
        events.append({"role": "death", "node": "blast_ring", "time": 0.5, "particle": "vehicle_explode_effect"})
        out = W.apply_effect_events(self.ENTITY, events, [{"role": "attack", "soundeffect": "light_armour_fire", "frame": 1}], add_states=["death"])
        self.assertNotIn("rifle_muzzle_particle", out)
        self.assertIn('node="exhaust"', out, "an event at another locator stays")
        self.assertEqual(out.count('particle = "light_tank_attack_barrel_particle"'), 2)
        self.assertIn('event = { time = 0.033 sound = { soundeffect = "light_armour_fire" } }', out)
        self.assertIn('state = { name = "death"', out)
        self.assertIn('event = { time = 0.5 node = "blast_ring" particle = "vehicle_explode_effect" keep_particle = yes }', out)
        self.assertNotIn("light_tank", out.split('name = "attack"')[0], "idle fires nothing")

    def test_a_sound_frame_is_written_as_seconds(self) -> None:
        self.assertIn("time = 0.5 ", W.sound_event_line("x", 15))


class Particles(unittest.TestCase):
    TEXT = (
        'particle={\n\tname="flame_file"\n'
        '\tsubsystem={\n\t\tname="fire"\n\t\tcolor={\n\t\t\tx=255.000\n\t\t\ty=160.000\n\t\t\tz=10.000\n\t\t\talpha=100.000\n\t\t}\n\t\tduration=-1\n\t}\n'
        '\tsubsystem={\n\t\tname="smoke"\n\t\tcolor={\n\t\t\tx=60.000\n\t\t\ty=60.000\n\t\t\tz=58.000\n\t\t\talpha=80.000\n\t\t}\n\t\tduration=2.000\n\t}\n'
        '}\n'
        'particle={\n\tname="other_file"\n}\n'
    )

    def test_a_copy_changes_colour_and_name_only(self) -> None:
        out = E.adapted_particle(self.TEXT, "flame_file", "u_spell_file", [120, 150, 255], 0.5)
        self.assertIn('name="u_spell_file"', out)
        self.assertNotIn("other_file", out)
        self.assertIn("duration=0.500", out)
        self.assertIn("x=60.000", out, "grey smoke keeps its colour")
        fire = out.split('name="smoke"')[0]
        x, y, z = (float(fire.split(f"{k}=")[1].split()[0]) for k in "xyz")
        self.assertGreater(z, x, "the flame takes the blue")
        self.assertAlmostEqual(max(x, y, z), 255.0, places=1, msg="at the flame's own brightness")

    def test_a_looping_copy_stays_endless(self) -> None:
        out = E.adapted_particle(self.TEXT, "flame_file", "u_eye_file", [176, 64, 255], None)
        self.assertIn("duration=-1", out)

    def test_a_tinted_smoke_takes_the_hue(self) -> None:
        out = E.adapted_particle(self.TEXT, "flame_file", "u_smoke_file", [110, 40, 170], 1.0, tint_grey=True)
        smoke = out.split('name="smoke"')[1]
        x, y, z = (float(smoke.split(f"{k}=")[1].split()[0]) for k in "xyz")
        self.assertGreater(z, y, "purple, not grey")
        self.assertAlmostEqual(max(x, y, z), 60.0, places=0, msg="at the smoke's own brightness")

    def test_the_registration_names_the_copy(self) -> None:
        plan = {"stem": "u", "particles": [{"vanilla": True, "name": "x"}]}
        files, problems = E.particle_files(plan, None)
        self.assertEqual((files, problems), ([], []))


if __name__ == "__main__":
    unittest.main()
