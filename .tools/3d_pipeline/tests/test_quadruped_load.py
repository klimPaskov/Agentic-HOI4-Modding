"""A quadruped's load (a tower on its back), its Saddle_Node, its rigid binding and the loaded poses, without Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE / "adapter"))
sys.path.insert(0, str(PIPELINE))

import quadruped_layout as ql
import quadruped_load as qload
from lib import mount_size, unit_registration

BOX_FACES = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])


class Mesh:
    def __init__(self) -> None:
        self.points: list = []
        self.triangles: list = []

    def box(self, low, high) -> None:
        (x0, y0, z0), (x1, y1, z1) = low, high
        base = len(self.points)
        self.points += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        self.triangles += (BOX_FACES + base).tolist()

    def prism(self, y0, y1, centre_z, radius, sides=6, rings=9) -> None:
        """A barrel along Y with a vertex on top, so its back has no flat face."""

        base = len(self.points)
        angles = np.pi / 2 + np.arange(sides) * 2 * np.pi / sides
        for y in np.linspace(y0, y1, rings):
            self.points += [(radius * np.cos(a), y, centre_z + radius * np.sin(a)) for a in angles]
        for ring in range(rings - 1):
            for k in range(sides):
                a, b = base + ring * sides + k, base + ring * sides + (k + 1) % sides
                self.triangles += [[a, b + sides, b], [a, a + sides, b + sides]]

    def arrays(self):
        return np.array(self.points, float), np.array(self.triangles, int)


def war_elephant() -> Mesh:
    """Four legs, a barrel body whose back is at 0.98, a head in front, a deck on the back with a post and an upper floor."""

    mesh = Mesh()
    for x in (-0.15, 0.15):
        for y in (-0.45, 0.45):
            mesh.box((x - 0.06, y - 0.06, 0.0), (x + 0.06, y + 0.06, 0.55))
    mesh.prism(-0.6, 0.6, 0.76, 0.22)
    mesh.box((-0.12, -0.95, 0.65), (0.12, -0.6, 1.1))  # head, reaching above the deck's cut beside the deck
    mesh.box((-0.3, -0.5, 1.0), (0.3, 0.5, 1.05))  # deck
    mesh.box((-0.04, -0.04, 1.05), (0.04, 0.04, 1.6))  # post
    mesh.box((-0.22, -0.22, 1.6), (0.22, 0.22, 1.62))  # upper floor
    return mesh


class FindLoad(unittest.TestCase):
    def test_the_deck_and_what_stands_on_it_are_the_load(self) -> None:
        points, triangles = war_elephant().arrays()
        load = qload.find_load(points, triangles)
        self.assertAlmostEqual(load.deck_z, 1.05, delta=0.02)
        self.assertAlmostEqual(load.cut_z, 1.0, delta=0.02)
        deck = (points[:, 2] >= 1.0) & (np.abs(points[:, 1]) <= 0.5)
        self.assertTrue(load.mask[deck].all(), "deck, post and upper floor")
        head = points[:, 1] < -0.55
        self.assertFalse(load.mask[head].any(), "the head reaches above the cut beside the deck but is not joined to it")
        self.assertFalse(load.mask[points[:, 2] < 0.99].any(), "nothing under the deck")
        self.assertEqual(len(load.floors), 2)
        self.assertAlmostEqual(load.floors[1][0], 1.62, delta=0.02)

    def test_no_flat_floor_is_refused(self) -> None:
        mesh = Mesh()
        mesh.prism(-0.6, 0.6, 0.76, 0.22)
        points, triangles = mesh.arrays()
        with self.assertRaises(qload.LoadError):
            qload.find_load(points, triangles)


class Saddle(unittest.TestCase):
    def test_the_rider_stands_on_a_floor_clear_of_the_post(self) -> None:
        points, triangles = war_elephant().arrays()
        load = qload.find_load(points, triangles)
        seat = qload.place_saddle(points, triangles, load, 0.3)
        self.assertEqual(seat["column_load_vertices"], 0)
        self.assertGreater(float(np.hypot(*seat["point"][:2])), seat["column_radius"])
        self.assertIn(round(float(seat["point"][2]), 2), {1.05, 1.62})

    def test_the_rider_room_is_what_its_clips_sweep(self) -> None:
        points, triangles = war_elephant().arrays()
        load = qload.find_load(points, triangles)
        # A rider that reaches 0.3 forward (-Y) of its node: no deck point keeps the post out of that reach, so the floor wins
        # where the swept cells hold fewest load vertices, and the count is reported.
        cells = [[x, y] for x in range(-1, 1) for y in range(-6, 1)]
        seat = qload.place_saddle(points, triangles, load, 0.3, {"cells": cells, "cell": 0.05})
        self.assertIn("column_load_vertices", seat)
        clear = qload.place_saddle(points, triangles, load, 0.3, {"cells": [[0, 0]], "cell": 0.01})
        self.assertEqual(clear["column_load_vertices"], 0)

    def test_a_load_rolls_only_until_it_meets_the_ground(self) -> None:
        points, triangles = war_elephant().arrays()
        load = qload.find_load(points, triangles)
        torso = points[:, 2] > 0.54
        roll = qload.roll_limit(points, load.mask, torso, np.array([0.0, 1.0, 0.0]), ql.COLLAPSE_ROLL)
        self.assertGreater(roll, 10.0)
        self.assertLess(roll, ql.COLLAPSE_ROLL)


class Binding(unittest.TestCase):
    def test_the_load_rides_one_bone_and_fades_into_the_body(self) -> None:
        points, triangles = war_elephant().arrays()
        load = qload.find_load(points, triangles)
        names = ["Root", "Pelvis", "Spine", "Chest", "Load"]
        indices = np.tile(np.array([1, 3, 0, 0]), (len(points), 1))
        weights = np.tile(np.array([0.6, 0.4, 0.0, 0.0]), (len(points), 1))
        out_i, out_w, report = qload.bind_load(points, load.mask, indices, weights, names, ring=0.2)
        spine = names.index("Load")
        self.assertTrue(np.all(out_i[load.mask, 0] == spine) and np.allclose(out_w[load.mask, 0], 1.0))
        self.assertTrue(np.allclose(out_w.sum(axis=1), 1.0))
        near = (~load.mask) & (qload.nearest_distance(points, points[load.mask]) < 0.19)
        self.assertTrue(near.any() and report["ring_vertices"] > 0)
        share = np.where(out_i[near] == spine, out_w[near], 0.0).sum(axis=1)
        self.assertTrue((share > 0).all(), "the skin under the deck takes some of the load bone")
        far = points[:, 2] < 0.3
        self.assertTrue(np.array_equal(out_i[far], indices[far]), "the legs keep their own weights")


class LoadedPoses(unittest.TestCase):
    def setUp(self) -> None:
        rng = np.random.default_rng(3)
        parts = [rng.normal((x, y, z), 0.03, (300, 3)) for x in (-0.25, 0.25) for y in (0.0, 1.6) for z in np.linspace(0.05, 0.95, 4)]
        parts.append(np.column_stack([rng.uniform(-0.35, 0.35, 3000), rng.uniform(-0.2, 1.8, 3000), rng.uniform(1.0, 1.6, 3000)]))
        parts.append(rng.normal((0.0, -0.5, 1.8), 0.05, (300, 3)))
        self.landmarks = ql.detect_landmarks(np.vstack(parts))

    def test_a_loaded_back_does_not_bend_and_the_roll_is_capped(self) -> None:
        free = ql.build_layout(dict(self.landmarks))
        loaded = ql.build_layout({**self.landmarks, "load": {"roll_limit": 30.0, "bone": "Spine"}})
        self.assertIn("Spine", ql.pose_at("quadruped_trot", 5, free))
        self.assertNotIn(ql.LOAD_BONE, free.names())
        self.assertEqual(loaded.bone(ql.SADDLE_NODE).parent, ql.LOAD_BONE)
        self.assertEqual(loaded.bone(ql.LOAD_BONE).parent, "Spine")
        for frame in range(0, 20, 3):
            pose = ql.pose_at("quadruped_trot", frame, loaded)
            self.assertFalse(set(ql.LOADED_STILL) & set(pose))
        last = ql.frame_count("quadruped_collapse") - 1
        self.assertAlmostEqual(ql.pose_at("quadruped_collapse", last, loaded)["__root_roll__"][0][1], 30.0)
        self.assertAlmostEqual(ql.pose_at("quadruped_collapse", last, free)["__root_roll__"][0][1], ql.COLLAPSE_ROLL)

    def test_the_charge_ends_in_its_first_pose(self) -> None:
        layout = ql.build_layout(dict(self.landmarks))
        last = ql.frame_count("quadruped_charge") - 1
        first, end = ql.pose_at("quadruped_charge", 0, layout), ql.pose_at("quadruped_charge", last, layout)
        for name, rows in first.items():
            for (axis_a, degrees_a), (axis_b, degrees_b) in zip(rows, end[name]):
                self.assertEqual(axis_a, axis_b)
                self.assertAlmostEqual(degrees_a, degrees_b, places=6, msg=name)


class PillarLegs(unittest.TestCase):
    def test_pillar_legs_bend_less_and_never_gallop(self) -> None:
        rng = np.random.default_rng(5)
        parts = [rng.normal((x, y, z), 0.03, (300, 3)) for x in (-0.25, 0.25) for y in (0.0, 1.6) for z in np.linspace(0.05, 0.95, 4)]
        parts.append(np.column_stack([rng.uniform(-0.35, 0.35, 3000), rng.uniform(-0.2, 1.8, 3000), rng.uniform(1.0, 1.6, 3000)]))
        parts.append(rng.normal((0.0, -0.5, 1.8), 0.05, (300, 3)))
        runner = ql.detect_landmarks(np.vstack(parts))
        self.assertFalse(ql.leg_stance(runner)["graviportal"])
        self.assertEqual(ql.stance_style("quadruped_gallop", runner), "quadruped_gallop")
        heavy = {**runner, "legs": {key: {**joints, "radius": np.asarray(0.25 * float(runner["belly_z"]))} for key, joints in runner["legs"].items()}}
        stance = ql.leg_stance(heavy)
        self.assertTrue(stance["graviportal"])
        self.assertAlmostEqual(stance["flex"], ql.FLEX_REFERENCE / 0.25, places=3)
        self.assertEqual(ql.stance_style("quadruped_gallop", heavy), "quadruped_trot")
        self.assertEqual(ql.stance_style("quadruped_trot", heavy), "quadruped_walk")
        light, pillar = ql.build_layout(runner), ql.build_layout(heavy)
        for frame in range(0, 20, 4):
            a, b = ql.pose_at("quadruped_trot", frame, light), ql.pose_at("quadruped_trot", frame, pillar)
            self.assertAlmostEqual(b["Front_Left_Cannon"][0][1], a["Front_Left_Cannon"][0][1] * stance["flex"], places=6)
            self.assertAlmostEqual(b["Front_Left_Upper"][0][1], a["Front_Left_Upper"][0][1], places=6)


class MountSize(unittest.TestCase):
    def test_vanilla_constants(self) -> None:
        self.assertAlmostEqual(mount_size.VANILLA_WITHERS_MAP, 3.676, places=3)
        self.assertAlmostEqual(mount_size.VANILLA_RIDER_MAP, 3.823, places=3)

    def test_the_back_stands_at_the_species_size(self) -> None:
        points, triangles = war_elephant().arrays()
        with mock.patch.object(mount_size, "read_glb", return_value=(points, triangles)):
            size = mount_size.mount_size(Path("x.glb"), 0.8, 1.7, True, 7.3518)
        back = size["back_share"] * size["target_height_m"] * 0.8
        self.assertAlmostEqual(back, 3.676 * 1.7, places=2)
        self.assertAlmostEqual(size["back_share"], 1.0 / 1.62, delta=0.015)
        self.assertAlmostEqual(size["rider_entity_scale"] * 0.8, 0.52, places=3)
        self.assertAlmostEqual(size["rider_height_in_mount_mesh"] * 0.8, 3.823, places=2)



class RiderRegistration(unittest.TestCase):
    def test_the_rider_plays_its_mapped_clips_under_names_of_its_own(self) -> None:
        rider = {"stem": "zombie", "model_folder": "gfx/models/units/zombie", "shapes": ["body"], "roles": ["attack", "death", "idle", "move"],
                 "role_map": {"move": "idle", "death": "idle"}, "scale": 0.65, "mesh_name": "elephant_rider_mesh", "entity": "elephant_rider_entity"}
        text = unit_registration.registration_text(unit_entity="elephant_entity", model_folder="gfx/models/units/elephant", stem="elephant",
                                                   shapes=["body"], roles=["idle", "move", "attack", "death"], scale=0.8, template="mount",
                                                   rider=rider, state_set="infantry")
        self.assertIn('Saddle_Node = "elephant_rider_entity"', text)
        self.assertIn('name = "elephant_rider_mesh"', text)
        self.assertIn('animation = { id = "move" type = "zombie_idle_animation" }', text)
        self.assertIn('animation = { id = "death" type = "zombie_idle_animation" }', text)
        self.assertIn('animation = { id = "attack" type = "zombie_attack_animation" }', text)
        self.assertIn('pdxmesh = "elephant_rider_mesh"', text)
        self.assertIn("scale = 0.65", text)


if __name__ == "__main__":
    unittest.main()
