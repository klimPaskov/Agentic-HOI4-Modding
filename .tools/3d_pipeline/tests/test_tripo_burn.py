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
