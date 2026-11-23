"""A straight polearm built from a side-view picture (lib/turned_prop.py), on a drawn picture, without Blender."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import mount_size, turned_prop


def spear(path: Path, head_right: bool = True, tilt: float = 0.0) -> None:
    """A grey picture of a brown shaft 600 px long and 14 px thick, a wider socket, and a leaf head 90 px long and 40 px wide."""

    image = Image.new("RGB", (900, 300), (190, 190, 190))
    draw = ImageDraw.Draw(image)
    draw.rectangle((100, 143, 700, 157), fill=(150, 110, 60))
    draw.rectangle((690, 140, 720, 160), fill=(120, 120, 125))
    draw.polygon([(720, 150), (740, 130), (810, 150), (740, 170)], fill=(170, 170, 175))
    if not head_right:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    if tilt:
        image = image.rotate(tilt, resample=Image.BICUBIC, expand=True, fillcolor=(190, 190, 190))
    image.save(path)


class TurnedProp(unittest.TestCase):
    def build(self, **kwargs):
        with tempfile.TemporaryDirectory() as folder:
            picture = Path(folder) / "spear.png"
            spear(picture, **kwargs)
            profile = turned_prop.measure(picture)
            mesh = turned_prop.build(profile, 3.0)
            out = Path(folder) / "spear.glb"
            turned_prop.write_glb(out, mesh, turned_prop.filled_texture(profile))
            points, triangles = mount_size.read_glb(out)
        return profile, mesh, points, triangles

    def test_the_head_is_a_flat_blade_and_the_shaft_is_round(self) -> None:
        profile, mesh, _, _ = self.build()
        self.assertTrue(profile.head_at_end)
        self.assertGreater(profile.flat.mean(), 0.08)
        self.assertLess(profile.flat.mean(), 0.16)
        positions = mesh["positions"]
        blade = positions[positions[:, 0] > 2.7]
        shaft = positions[(positions[:, 0] > 0.05) & (positions[:, 0] < 2.5)]
        self.assertLess(np.ptp(blade[:, 2]), 0.5 * np.ptp(blade[:, 1]))  # flat: thinner than it is wide
        self.assertAlmostEqual(float(np.ptp(shaft[:, 1])), float(np.ptp(shaft[:, 2])), delta=0.01)  # round

    def test_the_size_follows_the_length_and_the_picture(self) -> None:
        _, mesh, points, triangles = self.build()
        positions = mesh["positions"]
        self.assertAlmostEqual(float(np.ptp(positions[:, 0])), 3.0, places=3)
        self.assertAlmostEqual(float(np.ptp(positions[:, 1])), 3.0 * 41 / 711, delta=0.02)  # the head's width
        self.assertEqual(len(points), len(positions))
        self.assertLess(len(triangles), 600)  # rings only where the outline changes

    def test_a_head_on_the_left_and_a_tilted_picture_give_the_same_prop(self) -> None:
        _, plain, _, _ = self.build()
        _, mirrored, _, _ = self.build(head_right=False, tilt=4.0)
        for mesh in (plain, mirrored):
            head = mesh["positions"][mesh["positions"][:, 0] > 2.9]
            self.assertGreater(float(np.ptp(head[:, 1])), 0.0)
        self.assertAlmostEqual(float(np.ptp(mirrored["positions"][:, 0])), 3.0, places=3)

    def test_every_triangle_faces_outward(self) -> None:
        _, mesh, _, _ = self.build()
        p, t = mesh["positions"], mesh["triangles"]
        a, b, c = p[t[:, 0]], p[t[:, 1]], p[t[:, 2]]
        normal = np.cross(b - a, c - a)
        radial = (a + b + c) / 3.0
        radial[:, 0] = 0.0
        side = (normal * radial).sum(axis=1)
        tube = np.linalg.norm(radial, axis=1) > 1e-6
        self.assertTrue((side[tube] >= -1e-12).all())


if __name__ == "__main__":
    unittest.main()
