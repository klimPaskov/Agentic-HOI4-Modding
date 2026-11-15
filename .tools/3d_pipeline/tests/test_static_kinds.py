"""The static-model route's rules that run without Blender (lib/static_kinds.py) and its contract (config/static_kinds.json)."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np  # noqa: E402

from lib import pdx_deform  # noqa: E402
from lib import static_kinds as sk  # noqa: E402

GAME = Path(r"C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV")


def box(low, high, count=4000, seed=0):
    """Points on the surface of an axis-aligned box."""

    rng = np.random.default_rng(seed)
    low, high = np.asarray(low, float), np.asarray(high, float)
    points = rng.random((count, 3)) * (high - low) + low
    axis = rng.integers(0, 3, count)
    side = rng.integers(0, 2, count)
    points[np.arange(count), axis] = np.where(side, high[axis], low[axis])
    return points


def cylinder(centre, radius, z0, z1, axis="z", count=3000, seed=1):
    rng = np.random.default_rng(seed)
    angle = rng.random(count) * math.tau
    along = rng.random(count) * (z1 - z0) + z0
    a, b = radius * np.cos(angle), radius * np.sin(angle)
    if axis == "z":
        return np.stack([centre[0] + a, centre[1] + b, along], axis=1)
    return np.stack([centre[0] + a, along, centre[2] + b], axis=1)  # along y


def tank(front=-1.0):
    """A hull with tracks, a narrower superstructure, a round turret and a barrel toward `front` y."""

    hull = box([-2.0, -4.0, 0.0], [2.0, 4.0, 1.6], 40000)
    deck = box([-2.0, -4.0, 1.55], [2.0, 4.0, 1.6], 20000, seed=5)
    upper = box([-1.3, -2.5, 1.6], [1.3, 2.0, 2.4], 15000, seed=2)
    roof = box([-1.3, -2.5, 2.35], [1.3, 2.0, 2.4], 12000, seed=6)
    turret = cylinder([0.0, 0.0], 0.9, 2.4, 3.4, count=12000)
    lid = box([-0.9, -0.9, 3.38], [0.9, 0.9, 3.4], 3000, seed=3)
    barrel = cylinder([0.0, 0.0, 2.9], 0.08, 0.0, 1.5, axis="y", count=800)
    barrel[:, 1] = -0.9 - barrel[:, 1] if front < 0 else 0.9 + barrel[:, 1]
    return np.concatenate([hull, deck, upper, roof, turret, lid, barrel])


class ScriptTests(unittest.TestCase):
    TEXT = '''# a comment { not a block
entity = {
\tname = "X_entity"
\tpdxmesh = "X_mesh"
\tstate = { name = "idle" animation = "idle" }
\tstate = { name = "attack" animation = "attack"
\t\tevent = { time = 0 node="barrel" particle = "p" }
\t\tevent = { time = 0 node="gone" particle = "p" }
\t}
\tstate = { name = "death" animation = "explode" }
\tscale = 0.7
}
'''

    def test_parse_keeps_blocks_and_their_text(self):
        items = sk.parse_script(self.TEXT)
        self.assertEqual(items[0][0], "entity")
        body = items[0][1]
        self.assertEqual(sk.scalar(body, "name"), "X_entity")
        self.assertEqual(sk.scalar(body, "scale"), "0.7")
        start, end = items[0][2]
        self.assertTrue(self.TEXT[start:end].startswith("entity"))
        self.assertTrue(self.TEXT[start:end].rstrip().endswith("}"))

    def test_entity_text_renames_and_keeps_only_what_the_model_has(self):
        text = sk.entity_text(self.TEXT.split("\n", 1)[1], "tank", "tank_mesh", ["barrel"], ["idle", "attack", "death"], 0.7)
        self.assertIn('name = "tank_entity"', text)
        self.assertIn('pdxmesh = "tank_mesh"', text)
        self.assertIn('node="barrel"', text)
        self.assertNotIn('node="gone"', text)
        self.assertNotIn('"explode"', text)  # a state playing an animation the model lacks plays idle
        self.assertEqual(text.count("scale = 0.7"), 1)
        self.assertEqual(text.count("{"), text.count("}"))
        self.assertTrue(sk.parse_script(text))

    def test_scan_definitions_and_entity_scale(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "gfx/entities").mkdir(parents=True)
            (root / "gfx/entities/a.asset").write_text(
                'pdxmesh = { name = "X_mesh" file = "gfx/models/x.mesh" scale = 0.6 animation = { id = "idle" type = "X_idle" } }\n'
                + self.TEXT + 'animation = { name = "X_idle" file = "x_idle.anim" }\n', encoding="utf-8")
            found = sk.scan_definitions(root)
            self.assertEqual(found["pdxmesh"]["X_mesh"]["animations"], {"idle": "X_idle"})
            self.assertIn("X_idle", found["animation"])
            self.assertEqual(sk.entity_scale(found, "gfx/models/x.mesh")["scale"], 0.42)

    def test_mesh_text_is_balanced(self):
        text = sk.pdxmesh_text("t", "gfx/models/t/t.mesh", {"idle": "t_idle_animation"},
                               [{"name": "tShape", "texture_diffuse": "d", "texture_normal": "n", "texture_specular": "s", "shader": "PdxMeshAdvanced"}], 0.6)
        self.assertEqual(text.count("{"), text.count("}"))
        self.assertIn("scale = 0.6", text)


class GeometryTests(unittest.TestCase):
    RULE = {"area_threshold": 0.45, "search_from": 0.47, "cell_share": 0.02, "min_height_share": 0.13}
    BARREL = {"width_threshold": 0.28, "min_length_share": 0.25}

    def test_tank_front_is_where_the_barrel_points(self):
        for front, turns in ((-1.0, 0), (1.0, 2)):
            self.assertEqual(sk.facing_quarter_turns(tank(front), "vehicle", self.RULE), turns)
        sideways = sk.rotate_quarter_turns(tank(-1.0), 1)  # front now toward +x
        turns = sk.facing_quarter_turns(sideways, "vehicle", self.RULE)
        self.assertEqual(turns, 3)
        back = sk.rotate_quarter_turns(sideways, turns)
        self.assertLess(back[:, 1].min(), -2.35)  # the barrel's muzzle is the front again

    def test_turret_cut_skips_the_superstructure_and_the_lid(self):
        cut = sk.turret_cut(tank(), self.RULE)
        self.assertAlmostEqual(cut["cut_z"], 2.4, delta=0.1)

    def test_barrel_cut_is_at_the_turret_face(self):
        cut = sk.barrel_cut(tank(), 2.45, self.BARREL)
        self.assertAlmostEqual(cut["cut_y"], -0.9, delta=0.15)
        self.assertAlmostEqual(cut["muzzle"][1], -2.4, delta=0.05)
        self.assertAlmostEqual(cut["pivot"][2], 2.9, delta=0.1)

    def test_no_barrel_is_an_error(self):
        points = tank()
        points = points[~((points[:, 1] < -0.95) & (points[:, 2] > 2.6))]
        with self.assertRaises(ValueError):
            sk.barrel_cut(points, 2.45, self.BARREL)

    def plane(self):
        fuselage = cylinder([0.0, 0.0, 2.0], 0.8, -5.0, 5.0, axis="y", count=6000)
        wing = box([-7.0, -2.5, 1.8], [7.0, -0.5, 2.0], 6000)
        tail = box([-2.5, 4.0, 1.9], [2.5, 4.8, 2.0], 1500, seed=4)
        fin = box([-0.05, 4.0, 2.0], [0.05, 4.8, 3.6], 800, seed=5)
        blades = box([-1.6, -5.4, 1.85], [1.6, -5.3, 2.15], 1500, seed=6)
        spinner = cylinder([0.0, 0.0, 2.0], 0.3, -5.5, -5.0, axis="y", count=500, seed=7)
        return np.concatenate([fuselage, wing, tail, fin, blades, spinner])

    def test_plane_nose_is_the_end_nearer_the_wing(self):
        plane = self.plane()
        self.assertEqual(sk.facing_quarter_turns(plane, "plane"), 0)
        self.assertEqual(sk.facing_quarter_turns(sk.rotate_quarter_turns(plane, 2), "plane"), 2)

    def test_propeller_cut_keeps_the_cowling(self):
        cut = sk.propeller_cut(self.plane(), {"search_share": 0.2, "width_threshold": 0.6})
        self.assertGreater(cut["cut_y"], -5.3)
        self.assertLess(cut["cut_y"], -4.6)
        self.assertAlmostEqual(cut["hub"][0], 0.0, delta=0.05)
        self.assertAlmostEqual(cut["hub"][2], 2.0, delta=0.1)

    def test_waterline_is_where_the_hull_reaches_its_beam(self):
        rng = np.random.default_rng(3)
        z = rng.random(20000) * 2.0
        half = np.where(z < 0.5, 0.2 + 0.6 * z / 0.5, 0.8)  # a hull that curves in below z = 0.5
        y = rng.random(20000) * 10 - 5
        side = np.where(rng.random(20000) < 0.5, -1, 1)
        hull = np.stack([side * half, y, z], axis=1)
        self.assertAlmostEqual(sk.waterline_height(hull, 0.95), 0.47, delta=0.05)

    def test_placement_gives_vanilla_size_and_ground(self):
        contract = {"size": {"source": 8.0, "centre_share": [0.0, 0.0, 0.2], "ground_share": 0.0}, "rules": {}}
        scale, offset = sk.placement(tank(), "vehicle", contract)
        placed = tank() * scale + offset
        self.assertAlmostEqual(float(np.ptp(placed[:, 1])), 8.0, places=3)
        self.assertAlmostEqual(float(placed[:, 2].min()), 0.0, places=6)


class ClipTests(unittest.TestCase):
    def test_resample_keeps_seconds_or_the_count_asked(self):
        q = np.array([sk.axis_quaternion([0, 0, 1], a) for a in np.linspace(0, 90, 16)])
        motion = {"b": {"q": q, "d": np.zeros((16, 3))}}
        out, frames = sk.resample(motion, 15.0)
        self.assertEqual(frames, 31)
        self.assertAlmostEqual(sk.rotation_angle(out["b"]["q"][-1]), 90.0, places=3)
        self.assertAlmostEqual(sk.rotation_angle(out["b"]["q"][15]), 45.0, places=1)
        _out, frames = sk.resample(motion, 15.0, count=21)
        self.assertEqual(frames, 21)

    def test_turn_before_shot_is_held_through_the_recoil(self):
        recoil = np.zeros(60)
        recoil[30:40] = np.hanning(10)
        turn = sk.turn_before_shot(60, recoil, 20.0, 12)
        self.assertAlmostEqual(turn[0], 0.0)
        self.assertAlmostEqual(turn[32], 20.0)
        self.assertAlmostEqual(turn[38], 20.0)
        self.assertAlmostEqual(turn[-1], 0.0, places=6)
        self.assertLess(np.abs(np.diff(turn)).max(), 2.5)

    def test_spin_closes_whole_turns(self):
        frames = sk.spin_frames(1.85, 36.0)
        self.assertEqual(((frames - 1) * 36.0) % 360.0, 0.0)

    def test_local_motion_turns_about_the_bone(self):
        # two bones: root at the origin, turret at (0, 1, 0) in PDX (y up), turning 90 degrees about up
        inverse = np.stack([np.eye(4), np.eye(4)])
        inverse[1, :3, 3] = [0.0, -1.0, 0.0]
        mesh = pdx_deform.SkinnedMesh(positions=np.zeros((3, 3)), triangles=np.array([[0, 1, 2]]), joints=np.zeros((3, 4), dtype=np.int64),
                                      weights=np.tile([1.0, 0, 0, 0], (3, 1)), bones=["root", "turret"], parents=[-1, 0], inverse_bind=inverse)
        half = math.sin(math.radians(45))
        channels = {
            "root": {"t": np.zeros((2, 3)), "q": np.tile([0.0, 0.0, 0.0, 1.0], (2, 1)), "s": np.ones(2)},
            "turret": {"t": np.tile([0.0, 1.0, 0.0], (2, 1)), "q": np.array([[0.0, 0.0, 0.0, 1.0], [0.0, half, 0.0, half]]), "s": np.ones(2)},
        }
        motion = sk.local_motion(mesh, pdx_deform.Animation(fps=30.0, frames=2, channels=channels))
        self.assertAlmostEqual(sk.rotation_angle(motion["turret"]["q"][1]), 90.0, places=3)
        self.assertLess(float(np.abs(motion["turret"]["d"]).max()), 1e-9)  # a turn about its own pivot moves it nowhere
        axis = motion["turret"]["q"][1][1:]
        self.assertAlmostEqual(abs(axis[2]) / np.linalg.norm(axis), 1.0, places=6)  # PDX up is Blender z


class ContractTests(unittest.TestCase):
    def test_every_kind_has_a_measured_contract(self):
        kinds = sk.load_kinds()
        self.assertEqual(set(kinds), set(sk.KINDS))
        for kind, contract in kinds.items():
            self.assertTrue(contract["references"], kind)
            self.assertGreater(contract["size"]["source"], 0, kind)
            self.assertGreater(contract["triangle_budget"]["value"], 0, kind)
            self.assertTrue(contract["entity"]["reference"], kind)
            if contract["skeleton"]["bones"]:
                self.assertEqual(contract["skeleton"]["bones"][0]["name"], "root", kind)
        self.assertEqual(set(kinds["vehicle"]["clips"]), {"idle", "move", "attack", "death"})
        self.assertEqual(set(kinds["ship"]["clips"]), {"idle", "attack", "defend", "death"})
        self.assertTrue(kinds["building"]["collision"] and kinds["landmark"]["collision"])
        self.assertLess(kinds["plane"]["spin"]["degrees_per_frame"], 45.0)

    @unittest.skipUnless((GAME / "gfx/models/units/tanks").is_dir(), "the game is not installed here")
    def test_turret_rule_matches_vanilla_skinning(self):
        """The turret rule, run on vanilla's light tanks, puts nine in ten of their surface where their own skin does."""

        import calibrate_static_kinds as calibrate

        rule = sk.load_kinds()["vehicle"]["rules"]["turret"]
        for rel in rule["validation"]:  # the light tanks whose skin has a turret and a hull to compare with
            mesh = pdx_deform.load_mesh(GAME / rel)
            points, labels = calibrate.labelled_samples(mesh)
            cut = sk.turret_cut(points, rule)["cut_z"]
            upper = np.isin(labels, ["turret", "barrel_base", "barrel_tip"])
            judged = upper | (labels == "chassie")
            self.assertGreater(float(((points[:, 2] >= cut) == upper)[judged].mean()), 0.9, rel)

    @unittest.skipUnless((GAME / "gfx/models/units/tanks").is_dir(), "the game is not installed here")
    def test_kind_rules_fire_on_an_unscaled_vanilla_tank(self):
        findings = sk.kind_findings(GAME / "gfx/models/units/tanks/GER_tank_light.mesh", sk.kind_contract("vehicle"))
        rules = {rule for rule, _severity, _message in findings}
        self.assertIn("STATIC-SIZE", rules)  # vanilla's own mesh is 0.77 of the size the reference entity scale needs
        self.assertNotIn("STATIC-BONES", rules)
        self.assertNotIn("STATIC-COLLISION", rules)


if __name__ == "__main__":
    unittest.main()
