"""The burn death (lib/tripo_burn.py, `"death_kind": "burn"`), the PDX writer it uses (lib/pdx_write.py), its particle events
(lib/unit_wiring.py) and how the checks judge it. A synthetic winged biped, and vanilla's files when the game is installed. No Blender."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import check_unit_files
import test_deformation_checks as TD
from lib import pdx_deform, pdx_write, tripo_burn as B, unit_wiring as W
from lib.pdx_binary import read
from test_tripo_chain_lift import NAMES, WingedBiped, local
from test_tripo_pose_upper import turn

GAME = Path(r"C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV")


class Writer(WingedBiped):
    def test_a_read_and_a_write_give_the_same_bytes(self) -> None:
        anim = self.death(droop=10.0)
        for path in (self.mesh_path, anim):
            self.assertEqual(pdx_write.dump(read(path)), path.read_bytes(), path.name)

    @unittest.skipUnless((GAME / "gfx/models/units/GER_infantry.mesh").is_file(), "the game is not installed here")
    def test_vanillas_files_round_trip(self) -> None:
        for name in ("GER_infantry.mesh", "GER_infantry_death_mg.anim"):
            path = GAME / "gfx/models/units" / name
            self.assertEqual(pdx_write.dump(read(path)), path.read_bytes(), name)


class Heap(unittest.TestCase):
    def test_the_heap_is_closed_and_faces_out(self) -> None:
        points, triangles = B.heap_geometry(1.0, 0.35)
        edges = {}
        for tri in triangles:
            for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
                edges[tuple(sorted((int(a), int(b))))] = edges.get(tuple(sorted((int(a), int(b)))), 0) + 1
        self.assertTrue(all(count == 2 for count in edges.values()), "every edge has two faces: no hole")
        volume = sum(float(np.dot(points[a], np.cross(points[b], points[c]))) for a, b, c in triangles) / 6.0
        self.assertGreater(volume, 0.0, "wound outward")
        self.assertAlmostEqual(float(points[:, 1].min()), 0.0)

    def test_the_ramp_never_turns_back(self) -> None:
        values = B.smoothstep(np.linspace(-0.5, 1.5, 50))
        self.assertTrue(np.all(np.diff(values) >= 0.0))

    def test_hips_held_behind_the_feet_slide_within_the_limit(self) -> None:
        """The demon's own made death doubled the body over with the hips 0.13 hip heights behind the feet, and the shrink toward
        the point under the feet slid them 0.12, past BURN-IN-PLACE (2026-11-23)."""

        feet, rest_hips = np.array([0.0, 0.0, 0.0]), 1.0
        hips = np.array([0.0, 0.9, -0.13])
        point = B.held_point(feet, hips, rest_hips)
        slide = float(np.linalg.norm((hips - point)[[0, 2]])) * (1.0 - B.END_SCALE)
        self.assertAlmostEqual(slide, B.HELD_TRAVEL_SHARE * B.TRAVEL_LIMIT, places=6)
        self.assertLess(point[2], 0.0, "the point moved toward the hips")
        self.assertEqual(point[1], 0.0, "and stays on the ground")
        near = np.array([0.0, 0.9, -0.02])
        np.testing.assert_array_equal(B.held_point(feet, near, rest_hips), feet, "hips close to the feet keep the point under the feet")


class Burn(WingedBiped):
    def bowed(self, frames: int = 30, lie: bool = False):
        """A standing reaction: the spine bows 30 degrees by frame 12 and straightens again (or the body tips over and lies)."""

        def pose(frame: int):
            share = math.sin(math.pi * min(frame, 24) / 24.0)
            if lie:
                hips = local("Hips")
                return {"Hips": ((hips[0], hips[1] * (1.0 - 0.8 * frame / (frames - 1)), hips[2]), turn("x", 90.0 * frame / (frames - 1)))}
            return {"Spine": (local("Spine"), turn("x", 30.0 * share))}

        path = self.folder / "unit_death.anim"
        TD.write_anim(path, frames, pose)
        idle = self.folder / "unit_idle.anim"
        TD.write_anim(idle, 10, lambda frame: {})
        return path, idle

    def burnt(self, lie: bool = False):
        death, idle = self.bowed(lie=lie)
        heap = B.add_heap(self.mesh_path, None)
        B.add_rest_joint(self.mesh_path, idle)
        plan = B.write_plan(self.folder, "unit", heap, B.burn_death(self.mesh_path, death))
        return plan, death, idle

    def test_a_standing_reaction_burns_to_a_heap_and_passes(self) -> None:
        plan, death, idle = self.burnt()
        mesh = pdx_deform.load_mesh(self.mesh_path)
        anim = pdx_deform.load_anim(death)
        self.assertIn(B.HEAP_BONE, mesh.bones)
        self.assertIn(B.LOCATOR, B.mesh_locators(self.mesh_path))
        self.assertEqual(anim.frames, plan["burn_start"] + B.BURN_FRAMES + B.HOLD_FRAMES + 1)
        self.assertEqual(plan["burn_start"], 12, "the burn starts at the reaction's peak")
        found, numbers = B.burn_findings(mesh, anim, plan, "unit_death", B.mesh_locators(self.mesh_path))
        self.assertEqual(found, [], numbers)
        self.assertAlmostEqual(numbers["end_scale"], B.END_SCALE, places=3)
        self.assertIn(B.HEAP_BONE, pdx_deform.load_anim(idle).channels, "every clip keys the heap's bone")

    def test_the_heap_is_its_own_stream_with_its_own_ash_maps(self) -> None:
        self.burnt()
        shape = B._shape(read(self.mesh_path))
        streams = [child for child in shape.children if child.name == "mesh"]
        self.assertEqual(len(streams), 2, "the body's stream is left as it was, the heap gets its own")
        material = streams[1].child("material").properties
        for key in ("diff", "n", "spec"):
            self.assertIn(B.ASH_MARK, material[key][0])
            self.assertTrue((self.folder / material[key][0]).is_file())
        from lib import model_dds

        ash = model_dds.decode_top_level((self.folder / material["diff"][0]).read_bytes())[..., :3].astype(float)
        self.assertLess(float(ash.mean()), 60.0, "dark grey to black")
        normal = model_dds.decode_top_level((self.folder / material["n"][0]).read_bytes())
        self.assertEqual(int(normal[..., 2].max()), 0, "no emissive blue")

    def test_the_heap_outline_is_round(self) -> None:
        points, _triangles = B.heap_geometry(1.0, 0.35)
        rim = points[np.isclose(points[:, 1], 0.0) & (np.linalg.norm(points[:, [0, 2]], axis=1) > 0.5)]
        self.assertGreaterEqual(len(rim), 16, "a rounded outline, not a seven-sided slab")

    def test_the_heap_is_hidden_in_every_other_clip(self) -> None:
        plan, _death, idle = self.burnt()
        mesh = pdx_deform.load_mesh(self.mesh_path)
        heap = pdx_deform.dominant_bones(mesh) == mesh.bones.index(B.HEAP_BONE)
        posed = pdx_deform.skin(mesh, pdx_deform.skinning_matrices(mesh, pdx_deform.load_anim(idle))[0])[heap]
        self.assertLess(float(np.ptp(posed, axis=0).max()), 0.01 * mesh.height)

    def test_a_body_that_lies_down_fails_the_stand(self) -> None:
        plan, death, _idle = self.burnt(lie=True)
        mesh = pdx_deform.load_mesh(self.mesh_path)
        found, _numbers = B.burn_findings(mesh, pdx_deform.load_anim(death), plan, "unit_death", B.mesh_locators(self.mesh_path))
        self.assertIn("BURN-STANDS", [item["rule"] for item in found])

    def test_a_body_that_grows_again_fails_the_shrink(self) -> None:
        plan, death, _idle = self.burnt()
        mesh = pdx_deform.load_mesh(self.mesh_path)
        anim = pdx_deform.load_anim(death)
        later = plan["burn_start"] + 40
        anim.channels["Hips"]["s"][later:] = 1.0
        found, _numbers = B.burn_findings(mesh, anim, plan, "unit_death", B.mesh_locators(self.mesh_path))
        self.assertIn("BURN-SHRINK", [item["rule"] for item in found])

    def slid(self, during_burn: bool) -> tuple:
        """The burnt clip with its hips slid back by 0.3 hip heights, during the burn or before its start: (findings, numbers)."""

        plan, death, _idle = self.burnt()
        start = plan["burn_start"]
        frames = slice(start, None) if during_burn else slice(0, start)
        mesh = pdx_deform.load_mesh(self.mesh_path)
        anim = pdx_deform.load_anim(death)
        hips = anim.channels["Hips"]["t"]
        rest = float(hips[0, 1])
        picked = np.arange(len(hips))[frames]
        hips[picked, 2] -= 0.3 * rest * np.linspace(0.0, 1.0, len(picked))
        hips[picked[-1] + 1:, 2] -= 0.3 * rest
        return B.burn_findings(mesh, anim, plan, "unit_death", B.mesh_locators(self.mesh_path))

    def test_the_collapse_toward_the_feet_is_not_travel(self) -> None:
        """Hips that stand behind the feet slide to the ground point as the body shrinks (the ZIN devil, run devil_e, 0.12 hip heights)."""

        found, numbers = self.slid(during_burn=True)
        self.assertNotIn("BURN-IN-PLACE", [item["rule"] for item in found])
        self.assertGreater(numbers["collapse_pull"], 0.25)

    def test_a_clip_that_walks_before_the_burn_fails_in_place(self) -> None:
        found, numbers = self.slid(during_burn=False)
        self.assertIn("BURN-IN-PLACE", [item["rule"] for item in found], numbers)

    def test_smoke_that_stops_early_does_not_cover_the_burn(self) -> None:
        plan, _death, _idle = self.burnt()
        self.assertTrue(B.particles_cover(plan))
        short = dict(plan, particles=[dict(p, duration_s=0.5) if p["standin"] == "smoke" else p for p in plan["particles"]])
        self.assertFalse(B.particles_cover(short))

    def test_the_tripo_checks_drop_the_lying_rules_for_a_burn_only(self) -> None:
        import tripo_checks as TC

        plan, _death, _idle = self.burnt()
        mesh, anims = TC.load_unit(self.folder)
        numbers = {}
        burn, cut = TC.burn_split(self.folder, mesh, anims, numbers)
        self.assertEqual(burn["clip"], "unit_death")
        self.assertEqual(cut["unit_death"].frames, plan["burn_start"] + 1)
        found = [{"rule": "TRIPO-NOT-DOWN", "subject": "unit_death", "message": ""}, {"rule": "TRIPO-NOT-DOWN", "subject": "other_death", "message": ""},
                 {"rule": "TRIPO-NECK-SUNK", "subject": "unit_death", "message": ""}]
        kept = [(item["rule"], item["subject"]) for item in TC.burn_filtered(found, burn)]
        self.assertEqual(kept[:2], [("TRIPO-NOT-DOWN", "other_death"), ("TRIPO-NECK-SUNK", "unit_death")])

    def test_the_kits_checks_read_the_burn_up_to_its_start(self) -> None:
        plan, death, _idle = self.burnt()
        judged = check_unit_files._burn_judged(self.folder, "unit", death, pdx_deform.load_anim(death))
        self.assertEqual(judged.frames, plan["burn_start"] + 1)


class Wiring(unittest.TestCase):
    BLOCK = 'entity = {\n\tname = "u_entity"\n\tstate = { name = "death" animation = "death" animation_blend_time = 0.3 }\n\tstate = { name = "idle" animation = "idle" }\n}'

    def test_the_death_state_gets_its_particle_events(self) -> None:
        out = W.apply_particle_events(self.BLOCK, "death", [{"time": 0, "node": "burn", "particle": "u_burn_fire_particle"}])
        self.assertIn('event = { time = 0 node = "burn" particle = "u_burn_fire_particle" keep_particle = yes }', out)
        self.assertEqual(out.count("event ="), 1, "only the death state")
        with self.assertRaises(W.WiringError):
            W.apply_particle_events(self.BLOCK, "burn", [{"time": 0, "particle": "x"}])

    def test_a_vanilla_particle_is_copied_with_a_finite_duration(self) -> None:
        text = 'particle={\n\tname="building_fire_file"\n\tsubsystem={\n\t\tduration=-1.000\n\t}\n\tsubsystem={\n\t\tduration=1.000\n\t}\n}'
        out = W.finite_particle(text, "u_fire_file", 3.5)
        self.assertIn('name="u_fire_file"', out)
        self.assertNotIn("duration=-1", out)
        self.assertIn("duration=3.500", out)
        self.assertIn("duration=1.000", out, "a finite subsystem keeps its own")
        self.assertIn('pdxparticle = {\n\t\tname = "a"\n\t\ttype = "b"', W.particle_gfx([{"name": "a", "type": "b"}]))


class Kinds(unittest.TestCase):
    def test_the_lying_rules_are_the_ones_the_burn_replaces(self) -> None:
        self.assertEqual(set(B.LYING_RULES), {"TRIPO-NOT-DOWN", "TRIPO-DEATH-REST", "TRIPO-DEATH-FEET", "TRIPO-DEATH-HOVER", "TRIPO-DEATH-LEG-KICK",
                                              "TRIPO-DEATH-SPLAY"})
        self.assertIn("Spine02", NAMES)


if __name__ == "__main__":
    unittest.main()
