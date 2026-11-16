"""The static-model route's rules that run without Blender (lib/static_kinds.py) and its contract (config/static_kinds.json)."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np

from lib import pdx_deform
from lib import static_kinds as sk

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
        # a tank is sized on the area the map camera sees
        self.assertAlmostEqual(sk.main_measure(placed, "vehicle"), 8.0, places=3)
        self.assertAlmostEqual(float(placed[:, 2].min()), 0.0, places=6)

    def test_a_taller_tank_is_drawn_smaller(self):
        squat, tall = tank(), tank()
        tall[:, 2] *= 1.5
        self.assertLess(sk.main_measure(squat, "vehicle"), sk.main_measure(tall, "vehicle"))
        self.assertAlmostEqual(sk.main_measure(squat, "ship"), sk.main_measure(tall, "ship"))  # a ship is sized on length alone

    def test_landing_clears_the_hull_the_short_way(self):
        hull = box([-2.0, -4.0, 0.0], [2.0, 4.0, 2.0])
        against_side = box([1.5, -0.5, 0.0], [3.0, 0.5, 1.0])
        shift = sk.landing_shift(against_side, hull)
        clearance = sk.LANDING_CLEARANCE_SHARE * 1.5  # a tenth of the part's own plan size
        self.assertAlmostEqual(shift[0], 0.5 + clearance, places=6)  # off the side and clear of it, not 7 m off the end
        self.assertEqual(shift[1], 0.0)
        clear = box([2.5, -0.5, 0.0], [3.5, 0.5, 1.0])
        self.assertFalse(sk.landing_shift(clear, hull).any())
        moved = against_side + shift
        self.assertFalse(sk.landing_shift(moved + [1e-6, 0, 0], hull).any())

    def test_a_landed_turret_sits_on_its_base(self):
        flipped = np.eye(4)
        flipped[:3, :3] = sk.quaternion_matrix(sk.axis_quaternion([1, 0, 0], 172.9))
        settle = sk.upright_turn(flipped)
        up = settle @ flipped[:3, :3] @ np.array([0.0, 0.0, 1.0])
        self.assertAlmostEqual(float(up[2]), 1.0, places=6)
        self.assertTrue(np.allclose(sk.upright_turn(np.eye(4)), np.eye(3)))

    def test_tall_landmarks_and_the_map_camera_measure(self):
        base = box([-16.0, -16.0, 0.0], [16.0, 16.0, 0.5], 8000)
        obelisk = box([-1.5, -1.5, 0.5], [1.5, 1.5, 29.0], 8000, seed=3)
        palace = box([-15.0, -10.0, 0.0], [15.0, 10.0, 8.0], 8000, seed=4)
        self.assertTrue(sk.tall_and_thin(np.vstack([base, obelisk])))
        self.assertFalse(sk.tall_and_thin(palace))
        self.assertAlmostEqual(sk.main_measure(np.vstack([base, obelisk]), "landmark"), 29.0, delta=0.1)
        self.assertAlmostEqual(sk.main_measure(palace, "landmark"), 30.0, delta=0.1)
        long_low, short_tall = box([-1, -4, 0], [1, 4, 1], 4000), box([-1, -3, 0], [1, 3, 2], 4000)
        # the camera sees length x (width sin 55 + height cos 55)
        self.assertAlmostEqual(sk.main_measure(long_low, "vehicle") ** 2, 8 * (2 * np.sin(np.radians(55)) + np.cos(np.radians(55))), delta=0.05)
        self.assertGreater(sk.main_measure(short_tall, "vehicle"), 0)

    def test_a_tall_landmark_on_a_wide_base_is_sized_on_the_base(self):
        contract = {"size": {"source": 30.0, "centre_share": [0.0, 0.0, 0.0], "ground_share": 0.0, "tall_base": {"max_share": 0.9}}}
        share = sk.tall_base_share(contract)
        self.assertAlmostEqual(share, 0.9)
        self.assertIsNone(sk.tall_base_share({"size": {}}))
        plaza = box([-16.0, -16.0, 0.0], [16.0, 16.0, 0.5], 8000)
        wide = np.vstack([plaza, box([-1.5, -1.5, 0.5], [1.5, 1.5, 29.0], 8000, seed=3)])
        slim = np.vstack([box([-8.0, -8.0, 0.0], [8.0, 8.0, 0.5], 8000), box([-1.5, -1.5, 0.5], [1.5, 1.5, 29.0], 8000, seed=3)])
        self.assertTrue(sk.tall_and_thin(wide) and sk.tall_and_thin(slim))
        # a base within the bound keeps the height measure, a wider one is sized on its base
        self.assertAlmostEqual(sk.main_measure(slim, "landmark", share), 29.0, delta=0.1)
        self.assertAlmostEqual(sk.main_measure(wide, "landmark", share), 32.0 / 0.9, delta=0.1)
        scale, offset = sk.placement(wide, "landmark", contract)
        placed = wide * scale + offset
        base = float(max(np.ptp(placed[:, 0]), np.ptp(placed[:, 1])))
        self.assertAlmostEqual(base, 0.9 * 30.0, delta=0.05)
        self.assertLess(float(np.ptp(placed[:, 2])), 30.0)
        # the check agrees: the placed model is not flagged, the unplaced one is
        self.assertAlmostEqual(sk.main_measure(placed, "landmark", share), 30.0, delta=0.05)
        self.assertGreater(abs(sk.main_measure(wide, "landmark", share) - 30.0), 0.02 * 30.0)
        # without a bound the old rule holds, and a palace is never bounded
        self.assertAlmostEqual(sk.main_measure(wide, "landmark"), 29.0, delta=0.1)
        palace = box([-15.0, -10.0, 0.0], [15.0, 10.0, 8.0], 8000, seed=4)
        self.assertAlmostEqual(sk.main_measure(palace, "landmark", share), 30.0, delta=0.1)

    @unittest.skipUnless((GAME / "gfx/models/buildings/landmarks").is_dir(), "the game is not installed here")
    def test_the_contract_bound_is_the_widest_vanilla_tall_base(self):
        contract = sk.kind_contract("landmark")
        tall_base = contract["size"]["tall_base"]
        self.assertEqual(max(m["share"] for m in tall_base["models"]), tall_base["max_share"])
        for row in tall_base["models"]:
            mesh = pdx_deform.load_mesh(GAME / row["rel"])
            points = np.array([sk.to_blender(p) for p in mesh.positions[~mesh.collision]])
            self.assertTrue(sk.tall_and_thin(points))
            self.assertAlmostEqual(sk.main_measure(points, "landmark", tall_base["max_share"]), float(np.ptp(points[:, 2])), places=3)

    def test_a_building_is_sized_on_what_the_map_camera_sees(self):
        low_wide, tall = box([-3, -2, 0], [3, 2, 2], 4000), box([-3, -2, 0], [3, 2, 6], 4000, seed=2)
        seen = 6 * (4 * np.sin(np.radians(55)) + 2 * np.cos(np.radians(55)))
        self.assertAlmostEqual(sk.main_measure(low_wide, "building") ** 2, seen, delta=0.05)
        # the same footprint with tall chimneys is drawn smaller, so it does not read bulkier than vanilla's
        self.assertGreater(sk.main_measure(tall, "building"), sk.main_measure(low_wide, "building"))

    def test_flight_progress_and_ground_lift(self):
        path = np.array([[0, 0, 0], [0, 0, 2], [1, 0, 3], [2, 0, 0]], dtype=float)
        progress = sk.flight_progress(path)
        self.assertEqual(progress[0], 0.0)
        self.assertEqual(progress[-1], 1.0)
        self.assertTrue((progress >= 0).all() and (progress <= 1).all())
        self.assertEqual(list(sk.ground_lift([0.1, -0.2, 0.0])), [0.0, 0.2, 0.0])


def box_mesh(low, high):
    """An 8-vertex closed box: (points, triangles)."""

    (x0, y0, z0), (x1, y1, z1) = low, high
    points = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], dtype=float)
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return points, np.array(faces)


def disc_mesh(centre, radius, thickness, sides=16):
    """A closed wheel facing x: (points, triangles)."""

    angles = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    ring = np.stack([np.zeros(sides), radius * np.cos(angles), radius * np.sin(angles)], axis=1)
    outer = ring + np.array(centre) + [thickness / 2, 0, 0]
    inner = ring + np.array(centre) - [thickness / 2, 0, 0]
    points = np.vstack([outer, inner, [np.array(centre) + [thickness / 2, 0, 0]], [np.array(centre) - [thickness / 2, 0, 0]]])
    faces = []
    for k in range(sides):
        n = (k + 1) % sides
        faces += [(k, n, sides + n), (k, sides + n, sides + k), (2 * sides, n, k), (2 * sides + 1, sides + k, sides + n)]
    return points, np.array(faces)


def assemble(parts):
    points, triangles, offset = [], [], 0
    for p, t in parts:
        points.append(p)
        triangles.append(t + offset)
        offset += len(p)
    return np.vstack(points), np.vstack(triangles)


class RunningGearTests(unittest.TestCase):
    RULE = {"x_share": 0.5, "diameter_share": [0.03, 0.28], "round_ratio": 1.67, "track_length_share": 0.5, "top_margin_share": 0.02}

    def test_wheels_and_tracks_of_a_tank_in_pieces(self):
        parts = [box_mesh([-1.5, -4.0, 0.6], [1.5, 4.0, 2.5])]  # hull
        for side in (-1, 1):
            parts.append(box_mesh([side * 2.0 - 0.3, -4.0, 0.0], [side * 2.0 + 0.3, 4.0, 1.4]))  # a track run
            for y in (-2.4, -0.8, 0.8, 2.4):
                parts.append(disc_mesh([side * 1.8, y, 0.5], 0.45, 0.25))  # road wheels inside the track loop
        parts.append(disc_mesh([1.9, 0.0, 3.0], 0.2, 0.1))  # a round fitting high on the hull: not a wheel
        points, triangles = assemble(parts)
        gear = sk.running_gear(points, triangles, self.RULE)
        self.assertEqual(len(gear["wheels"]), 8)
        for wheel in gear["wheels"]:
            self.assertAlmostEqual(wheel["radius"], 0.45, delta=0.02)
            self.assertAlmostEqual(wheel["centre"][2], 0.5, delta=0.02)
        self.assertEqual(len(gear["tracks"]), 16)  # both track boxes, 8 vertices each
        self.assertEqual([round(w["centre"][1], 1) for w in gear["wheels"][:2]], [-2.4, -2.4])  # front first, left then right

    def test_a_coarse_piece_does_not_spin(self):
        round_wheel = disc_mesh([1.8, 0.0, 0.5], 0.45, 0.25, sides=16)[0]
        diamond = disc_mesh([1.8, 0.0, 0.5], 0.45, 0.25, sides=4)[0]
        self.assertEqual(sk.rim_coverage(round_wheel, np.array([1.8, 0.0, 0.5])), 1.0)
        self.assertLessEqual(sk.rim_coverage(diamond, np.array([1.8, 0.0, 0.5])), 0.34)

    def test_an_arm_is_not_round_about_its_axle(self):
        wheel = disc_mesh([1.8, 0.0, 0.5], 0.45, 0.25, sides=16)[0]
        self.assertLess(sk.half_turn_mismatch(wheel, np.array([1.8, 0.0, 0.5]), 0.45), 0.01)
        arm = np.array([[1.8, -0.4, 0.2], [1.8, 0.0, 0.5], [1.8, 0.4, 0.6], [1.8, 0.1, 0.9], [1.8, -0.3, 0.7]])
        self.assertGreater(sk.half_turn_mismatch(arm, np.array([1.8, 0.0, 0.55]), 0.45), 0.2)

    def test_a_tank_in_one_piece_has_no_wheels(self):
        points, triangles = box_mesh([-2.0, -4.0, 0.0], [2.0, 4.0, 2.5])
        gear = sk.running_gear(points, triangles, self.RULE)
        self.assertEqual(gear["wheels"], [])


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
        early = np.zeros(60)
        early[1:8] = 1.0  # a gun that fires on its second frame, as vanilla's light tank does
        turn = sk.turn_before_shot(60, early, 20.0, 12)
        self.assertLess(np.abs(np.diff(turn)).max(), 2.6)  # still eased over 12 frames, not snapped
        self.assertAlmostEqual(turn[12], 20.0)
        self.assertAlmostEqual(turn[-1], 0.0, places=6)

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


class TrackTests(unittest.TestCase):
    def test_track_uvs_run_across_and_along_the_hull(self):
        left = box([-2.0, -4.0, 0.0], [-1.4, 4.0, 1.0], 3000)
        right = box([1.4, -4.0, 0.0], [2.0, 4.0, 1.0], 3000, seed=3)
        points = np.concatenate([left, right])
        uv = sk.track_uvs(points, 0.75, 1.0)
        self.assertAlmostEqual(float(uv[:, 0].min()), 0.03, places=6)  # u spans the run's width, as vanilla's 0.03 to 0.97
        self.assertAlmostEqual(float(uv[:, 0].max()), 0.97, places=6)
        mirrored = np.abs(points[:, 0])
        order = np.argsort(mirrored)
        self.assertTrue(np.all(np.diff(uv[order, 0]) >= -1e-9))  # both runs map their outer edge to the same u
        slope = np.polyfit(points[:, 1], uv[:, 1], 1)[0]
        self.assertAlmostEqual(float(slope), 0.75, places=6)  # v grows along the hull at the asked density
        self.assertAlmostEqual(float(uv[:, 1].min()), 0.0, places=6)
        backwards = sk.track_uvs(points, 0.75, -1.0)
        self.assertAlmostEqual(float(np.polyfit(points[:, 1], backwards[:, 1], 1)[0]), -0.75, places=6)

    def test_tread_images_are_the_asked_size_and_tangent_space(self):
        images = sk.tread_images(np.array([90.0, 85.0, 70.0]), 5, (64, 32))
        self.assertEqual(set(images), {"diffuse", "normal", "specular"})
        for role, array in images.items():
            self.assertEqual(array.shape, (32, 64, 4), role)
            self.assertEqual(array.dtype, np.uint8, role)
        self.assertEqual(int(images["normal"][..., 2].max()), 0)  # PDX normal maps keep x in green and y in alpha
        rows = images["diffuse"][..., :3].astype(float).mean(axis=(1, 2))
        self.assertEqual(sk.tread_links(rows), 5)  # as many links a tile as asked, counted as calibration counts vanilla's
        self.assertLess(abs(float(np.median(images["diffuse"][..., :3].reshape(-1, 3), axis=0)[0]) - 90.0), 40.0)

    def test_tread_links_count_the_gaps_round_the_tile(self):
        self.assertEqual(sk.tread_links([71, 119, 116, 96, 99, 89, 61, 92, 117, 100, 95, 107, 64, 73, 109, 99, 90, 106, 68, 50,
                                         106, 112, 93, 108, 102, 70, 88, 117, 101, 96, 114, 78]), 5)  # vanilla's tank_threads_01 rows
        self.assertEqual(sk.tread_links([50, 100, 100, 100, 50, 100, 100, 50]), 2)  # a gap across the seam counts once
        self.assertEqual(sk.tread_links([90] * 8), 1)

    def test_the_vehicle_contract_carries_vanillas_track_rule(self):
        rule = sk.kind_contract("vehicle")["rules"]["tracks"]
        self.assertEqual(rule["shader"], "PdxMeshAdvancedAnim")
        self.assertGreater(rule["v_per_measure"], 0)
        self.assertIn(rule["v_sign"], (1.0, -1.0))
        self.assertGreater(rule["links"], 0)
        self.assertGreater(rule["texture_anim_speed"], 0)

    def test_clipped_hull_fittings_stay_on_the_hull(self):
        shell = np.linspace(3.08, 4.24, 50)  # the turret, from its cut to its roof
        fender = np.array([3.08, 3.09, 3.1])  # a fender corner the cut clipped 2 cm under its top
        hatch = np.array([4.2, 4.3])  # a hatch on the roof
        mantlet = np.linspace(3.2, 4.0, 10)  # in front, at the turret's height
        self.assertEqual(sk.cut_slivers([shell, fender, hatch, mantlet], 3.08, 4.3), [1])

    def test_a_landed_part_is_judged_by_tilt_and_gap(self):
        points = np.array([sk.to_blender(p) for p in box([-1, -1, 0], [1, 1, 0.5], 500)])  # PDX space via the swap
        flat = np.eye(4)
        tilt, lowest = sk.landed_pose(flat, points)
        self.assertAlmostEqual(tilt, 0.0, places=6)
        self.assertAlmostEqual(lowest, 0.0, places=6)
        lifted = np.eye(4)
        lifted[1, 3] = 1.44  # PDX y is up: the turret the review saw floating
        self.assertAlmostEqual(sk.landed_pose(lifted, points)[1], 1.44, places=6)
        tipped = np.eye(4)
        tipped[:3, :3] = sk.SWAP @ sk.quaternion_matrix(sk.axis_quaternion([1, 0, 0], 30.0))[:3, :3] @ sk.SWAP
        self.assertAlmostEqual(sk.landed_pose(tipped, points)[0], 30.0, places=4)


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
        self.assertEqual(set(kinds["ship"]["clips"]), {"idle", "death"})  # what vanilla's two-bone ships play
        self.assertEqual(kinds["ship"]["role_aliases"], {"defend": "idle", "attack": "idle"})
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
    def test_role_clips_from_vanilla(self):
        sys.path.insert(0, str(PIPELINE / "tripo"))
        import static_model

        tank, barrel = static_model.clip_motion(GAME, sk.kind_contract("vehicle"))
        self.assertEqual(set(tank), {"idle", "move", "attack", "death"})
        spin = tank["move"]["wheel_spin"]["degrees"]
        self.assertLess(min(spin[-1] % 360.0, 360.0 - spin[-1] % 360.0), 12.0)  # the wheels close whole turns over the loop
        self.assertIsNone(tank["idle"]["wheel_spin"])
        self.assertGreater(barrel, 0)
        turn = tank["attack"]["extras"]["turret"][0]["degrees"]
        self.assertAlmostEqual(max(turn), sk.kind_contract("vehicle")["attack_turn"]["degrees"], places=3)
        self.assertEqual(len(turn), tank["attack"]["frames"])
        plane, _ = static_model.clip_motion(GAME, sk.kind_contract("plane"))
        spin = plane["idle"]["extras"]["propeller"][0]["degrees_per_frame"]
        self.assertEqual(((plane["idle"]["frames"] - 1) * spin) % 360.0, 0.0)  # the loop closes a whole turn
        ship, _ = static_model.clip_motion(GAME, sk.kind_contract("ship"))
        self.assertIn("ship", ship["death"]["bones"])
        self.assertNotIn("attack", ship)

    @unittest.skipUnless((GAME / "gfx/entities").is_dir(), "the game is not installed here")
    def test_every_kind_gets_a_parsable_entity_from_vanilla(self):
        definitions = sk.scan_definitions(GAME, ("gfx/entities",))
        for kind, contract in sk.load_kinds().items():
            reference = definitions["entity"][contract["entity"]["reference"]]["text"]
            nodes = [loc["name"] for loc in contract["locators"]] + [bone["name"] for bone in contract["skeleton"]["bones"]]
            text = sk.entity_text(reference, "x", "x_mesh", nodes, list(contract["clips"]), contract["entity"]["entity_scale"])
            items = sk.parse_script(text)
            self.assertEqual(items[0][0], "entity", kind)
            self.assertEqual(sk.scalar(items[0][1], "name"), "x_entity", kind)
            self.assertEqual(text.count("{"), text.count("}"), kind)
            for name, value, _span in items[0][1]:
                if name == "state":
                    played = sk.scalar(value, "animation")
                    self.assertTrue(played is None or played in contract["clips"], (kind, played))

    def test_wheel_rule_finds_every_vanilla_wheel(self):
        """The wheel rule, run on vanilla's light tanks, finds every vertex their wheel bones carry."""

        for rel, row in sk.load_kinds()["vehicle"]["rules"]["wheels"]["validation"].items():
            self.assertGreaterEqual(row["recall"], 0.99, rel)
            self.assertGreaterEqual(row["wheels"], 4, rel)

    @unittest.skipUnless((GAME / "gfx/models/units/tanks").is_dir(), "the game is not installed here")
    def test_kind_rules_fire_on_an_unscaled_vanilla_tank(self):
        findings = sk.kind_findings(GAME / "gfx/models/units/tanks/GER_tank_light.mesh", sk.kind_contract("vehicle"))
        rules = {rule for rule, _severity, _message in findings}
        self.assertIn("STATIC-SIZE", rules)  # vanilla's own mesh is 0.77 of the size the reference entity scale needs
        self.assertNotIn("STATIC-BONES", rules)
        self.assertNotIn("STATIC-COLLISION", rules)
        self.assertNotIn("STATIC-SHADER", rules)  # its track runs use vanilla's scrolling shader, which the contract allows


if __name__ == "__main__":
    unittest.main()
