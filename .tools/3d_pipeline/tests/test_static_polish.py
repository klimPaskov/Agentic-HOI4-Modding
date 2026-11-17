"""The static route's part-clip check, shading check, hole texel and review lighting (lib/static_kinds.py,
lib/static_delight.py, tripo/static_sheets.py), on synthetic meshes and textures. None needs Blender."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np
from PIL import Image

from lib import static_delight as sd
from lib import static_kinds as sk


def box_mesh(low, high):
    """A closed box: 8 corners, 12 triangles wound outward."""

    (x0, y0, z0), (x1, y1, z1) = low, high
    points = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], dtype=float)
    quads = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    triangles = np.array([t for a, b, c, d in quads for t in ((a, b, c), (a, c, d))], dtype=np.int64)
    return points, triangles


def turn_z(points, degrees, about):
    angle = math.radians(degrees)
    rotation = np.array([[math.cos(angle), -math.sin(angle), 0.0], [math.sin(angle), math.cos(angle), 0.0], [0.0, 0.0, 1.0]])
    return (points - about) @ rotation.T + about


class PartClipTests(unittest.TestCase):
    def setUp(self) -> None:
        self.hull = box_mesh((-1.5, -3.0, 0.0), (1.5, 3.0, 1.0))
        # a turret resting on the hull (on its top face, set off by a hair as the route does), and a gun in front of it
        turret, turret_triangles = box_mesh((-0.8, -0.8, 1.001), (0.8, 0.8, 1.8))
        gun, gun_triangles = box_mesh((-0.05, -2.5, 1.3), (0.05, -0.8, 1.4))
        self.turret = (np.vstack([turret, gun]), np.vstack([turret_triangles, gun_triangles + len(turret)]))

    def crossings(self, moving):
        return sk.part_crossings(moving[0], moving[1], self.hull[0], self.hull[1])

    def test_a_turret_resting_on_the_hull_does_not_clip_at_any_turn(self) -> None:
        for degrees in range(0, 360, 30):
            turned = (turn_z(self.turret[0], degrees, np.zeros(3)), self.turret[1])
            self.assertEqual(self.crossings(turned), 0, degrees)

    def test_a_rod_on_the_turret_hanging_into_the_hull_clips(self) -> None:
        points, triangles = self.turret
        rod, rod_triangles = box_mesh((0.5, -1.6, 0.6), (0.55, -0.8, 1.3))  # a strut from the mantlet down through the deck
        moving = (np.vstack([points, rod]), np.vstack([triangles, rod_triangles + len(points)]))
        self.assertGreater(self.crossings(moving), 0)

    def test_a_turret_sunk_into_the_hull_clips(self) -> None:
        points, triangles = self.turret
        self.assertGreater(self.crossings((points - [0.0, 0.0, 0.3], triangles)), 0)

    def test_a_part_clear_of_the_hull_is_not_a_clip(self) -> None:
        points, triangles = self.turret
        self.assertEqual(self.crossings((points + [4.0, 0.0, -0.5], triangles)), 0)

    def test_mounts_follow_the_chain(self) -> None:
        self.assertEqual(sk._mounted_on("turret", {"turret": "chassie", "barrel_base": "turret"}), {"turret", "barrel_base"})


class ShadingTests(unittest.TestCase):
    def test_a_box_shaded_flat_does_not_lean(self) -> None:
        points, triangles = box_mesh((0, 0, 0), (1, 2, 3))
        # one vertex per corner and face, each with its face's normal
        split = points[triangles].reshape(-1, 3)
        faces = np.arange(len(split)).reshape(-1, 3)
        normal = np.cross(split[faces[:, 1]] - split[faces[:, 0]], split[faces[:, 2]] - split[faces[:, 0]])
        normal /= np.linalg.norm(normal, axis=1, keepdims=True)
        self.assertEqual(sk.leaning_share(split, np.repeat(normal, 3, axis=0), faces), 0.0)

    def test_a_box_shaded_smooth_across_its_corners_leans(self) -> None:
        points, triangles = box_mesh((0, 0, 0), (1, 1, 1))
        averaged = points - points.mean(axis=0)  # a corner's normal averaged over its three faces: 54.7 degrees off each
        self.assertGreater(sk.leaning_share(points, averaged, triangles), 0.99)

    def test_a_gently_rounded_surface_does_not_lean(self) -> None:
        # a cylinder of 24 sides shaded smooth: each corner 7.5 degrees off its face
        angles = np.linspace(0, math.tau, 25)[:-1]
        ring = np.stack([np.cos(angles), np.sin(angles)], axis=1)
        points = np.vstack([np.c_[ring, np.zeros(24)], np.c_[ring, np.ones(24)]])
        triangles = np.array([t for k in range(24) for t in ((k, (k + 1) % 24, 24 + (k + 1) % 24), (k, 24 + (k + 1) % 24, 24 + k))])
        normals = np.c_[np.vstack([ring, ring]), np.zeros(48)]
        self.assertEqual(sk.leaning_share(points, normals, triangles), 0.0)


class HoleTexelTests(unittest.TestCase):
    def test_the_hole_is_deep_in_the_largest_dark_patch_the_model_uses(self) -> None:
        image = np.full((512, 512, 3), 140, dtype=np.uint8)
        image[40:80, 40:80] = 10  # a small dark spot
        image[300:460, 100:300] = 25  # a large dark patch (a track run)
        image[0:200, 300:512] = 0  # darkest of all, but no face covers it
        groups = np.full((512, 512), -1, dtype=np.int64)
        groups[:, :300] = 0
        hole = sd.hole_uv(Image.fromarray(image), groups)
        u, v = hole["uv"]
        self.assertTrue(100 / 512 < u < 300 / 512 and 300 / 512 < v < 460 / 512, hole)
        self.assertLess(hole["ratio"], 0.3)
        self.assertGreater(hole["depth"], 5)


class Node:
    """A stand-in for a pdx_binary node: a name, properties and children."""

    def __init__(self, name, properties=None, children=()):
        self.name, self.properties, self.children = name, properties or {}, list(children)

    def child(self, name):
        return next((c for c in self.children if c.name == name), None)


def stream(diffuse, shader, offset):
    points = [0, 0, 0, 1, 0, 0, 0, 1, 0]
    return Node("mesh", {"p": [v + offset for v in points], "u0": [0, 0, 1, 0, 0, 1], "tri": [0, 1, 2]},
                [Node("material", {"shader": [shader], **({"diff": [diffuse]} if diffuse else {})})])


class ShadowStreamTests(unittest.TestCase):
    def test_the_shadow_check_reads_only_the_streams_on_the_checked_texture(self) -> None:
        # a tank's track runs are a second stream on their own tread texture; their UVs drawn on the atlas found a
        # "shadow" along the run's underside
        shape = Node("tankShape", children=[stream("tank_diffuse.dds", "PdxMeshAdvanced", 0), stream("tank_tracks_diffuse.dds", "PdxMeshAdvancedAnim", 5),
                                            stream(None, "Collision", 9)])
        with mock.patch("lib.pdx_binary.read", return_value=Node("root", children=[Node("object", children=[shape])])):
            everything = sd.mesh_uv_geometry(Path("tank.mesh"))
            atlas = sd.mesh_uv_geometry(Path("tank.mesh"), "tank_diffuse.dds")
        self.assertEqual(len(everything[2]), 2)
        self.assertEqual(len(atlas[2]), 1)
        self.assertLess(float(atlas[0].max()), 2.0)


class ReviewLightingTests(unittest.TestCase):
    def test_static_review_sheets_render_without_the_suns_shadow(self) -> None:
        # a part's cast shadow on another (a barrel's on the hull front, a turret's on the deck) read as geometry and
        # as painted texture in a tank's review; the static sheets turn the sun's shadow off
        from tripo import static_sheets

        with mock.patch.object(static_sheets.review_unit, "render", side_effect=SystemExit("stop")) as render:
            with self.assertRaises(SystemExit):
                static_sheets.close_review(Path("model"), "vehicle", Path("out"), [])
        self.assertIs(render.call_args.kwargs.get("sun_shadow"), False)
        with mock.patch.object(static_sheets.subprocess, "run", side_effect=SystemExit("stop")), mock.patch.object(static_sheets.review_unit, "find_blender", return_value="blender"), \
                mock.patch.object(static_sheets.review_unit, "diffuse_maps", return_value={}), mock.patch.object(static_sheets.review_unit, "specular_maps", return_value={}):
            written = {}

            def capture(path, text, *args, **kwargs):
                written[path.name] = text
                return len(text)

            with mock.patch.object(Path, "write_text", capture), mock.patch.object(Path, "mkdir"):
                with self.assertRaises(SystemExit):
                    static_sheets.render_rest(Path("model.mesh"), Path("tiles"), [])
        self.assertIn('"sun_shadow": false', written["request.json"])


if __name__ == "__main__":
    unittest.main()
