"""The static route's delighting of a colour texture (lib/static_delight.py) and its ground slab rule (lib/static_slab.py), on synthetic
textures and meshes. Neither needs Blender."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np
from PIL import Image

from lib import static_delight as sd
from lib import static_slab as ss

SIZE = 256


def quad():
    """One square facet (two triangles) mapped over the whole texture."""

    positions = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=float)
    uv = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=float)
    triangles = np.array([[0, 1, 2], [0, 2, 3]])
    return positions, uv, triangles


def slate(seed=0, mean=(96.0, 104.0, 124.0)):
    """A roof-like texture: a mean colour with grain and mortar lines."""

    rng = np.random.default_rng(seed)
    image = np.ones((SIZE, SIZE, 3)) * np.array(mean)
    image *= 1.0 + 0.08 * rng.standard_normal((SIZE, SIZE, 1))
    image[::8, :, :] *= 0.8
    image[:, ::11, :] *= 0.85
    return image


def groups():
    positions, uv, triangles = quad()
    return sd.group_map(uv, triangles, sd.facet_labels(positions, triangles), SIZE)


def with_band(image, factor=0.5):
    """A hard diagonal band, a third of the roof's side wide and as long as the roof, darkening by `factor`."""

    out = image.copy()
    y, x = np.mgrid[0:SIZE, 0:SIZE]
    band = np.abs((x - y) - 20) < SIZE * 0.1
    out[band] *= factor
    return out, band


class DelightingTests(unittest.TestCase):
    def test_a_hard_cast_shadow_band_is_found_and_lifted_with_its_detail_kept(self) -> None:
        clean = slate()
        shadowed, band = with_band(clean)
        regions = sd.shadow_regions(shadowed, groups())
        self.assertEqual(len(regions), 1)
        self.assertGreater(regions[0]["share"], 0.1)
        lifted, report = sd.delight(Image.fromarray(np.uint8(shadowed), "RGB"), groups())
        lifted = np.asarray(lifted, dtype=float)
        inside_before = (shadowed @ sd.LUMA)[band].mean()
        inside_after = (lifted @ sd.LUMA)[band].mean()
        outside = (shadowed @ sd.LUMA)[~band].mean()
        # the band comes up to the roof's own brightness (its feathered rim excluded) ...
        core = band & (np.abs(np.mgrid[0:SIZE, 0:SIZE][1] - np.mgrid[0:SIZE, 0:SIZE][0] - 20) < SIZE * 0.07)
        self.assertLess(abs((lifted @ sd.LUMA)[core].mean() - outside) / outside, 0.12)
        self.assertGreater(inside_after, 1.6 * inside_before)
        # ... its mortar lines and grain are still there (the detail's contrast is kept, not flattened)
        before = (shadowed @ sd.LUMA)[core]
        after = (lifted @ sd.LUMA)[core]
        self.assertGreater(np.corrcoef(before, after)[0, 1], 0.9)
        self.assertGreater(after.std() / after.mean(), 0.7 * before.std() / before.mean())
        self.assertEqual(report["left"], [])
        # the roof outside the band is untouched
        far = ~band & (np.abs((np.mgrid[0:SIZE, 0:SIZE][1] - np.mgrid[0:SIZE, 0:SIZE][0]) - 20) > SIZE * 0.2)
        self.assertLess(np.abs(lifted[far] - np.round(shadowed[far])).max(), 1.5)

    def test_small_dark_detail_is_left_alone(self) -> None:
        image = slate()
        # windows (small, dark, bluish), a weathering streak (long but faint and soft), mortar and grain already in it
        for x0 in range(20, 220, 50):
            image[40:56, x0 : x0 + 12] = (30, 38, 52)
        streak = np.exp(-(((np.arange(SIZE) - 128) / 30.0) ** 2))[None, :, None]
        image = image * (1.0 - 0.2 * streak)
        self.assertEqual(sd.shadow_regions(image, groups()), [])
        lifted, report = sd.delight(Image.fromarray(np.uint8(image), "RGB"), groups())
        self.assertEqual(report["regions"], [])
        self.assertTrue(np.array_equal(np.asarray(lifted), np.uint8(image)))

    def test_a_large_dark_door_of_another_colour_is_left_alone(self) -> None:
        image = slate(mean=(150.0, 100.0, 80.0))  # a brick wall
        image[60:200, 90:150] = (60, 62, 66)  # a grey door a fifth of the wall: dark, big, another colour
        self.assertEqual(sd.shadow_regions(image, groups()), [])

    def test_a_soft_fade_is_not_a_cast_shadow(self) -> None:
        image = slate()
        fade = np.clip((np.arange(SIZE) - 100) / 140.0, 0.0, 1.0)[None, :, None]  # a slow darkening toward one side
        self.assertEqual(sd.shadow_regions(image * (1.0 - 0.55 * fade), groups()), [])

    def test_a_blob_is_not_a_cast_shadow_but_a_band_across_the_surface_is(self) -> None:
        image = slate()
        blob = image.copy()
        blob[90:150, 90:150] *= 0.5  # 5 % of the surface, hard edged, but a stain, not a shadow across it
        self.assertEqual(sd.shadow_regions(blob, groups()), [])

    def test_the_check_fails_a_texture_that_still_has_a_shadow_and_passes_a_lifted_one(self) -> None:
        shadowed, _band = with_band(slate())
        positions, uv, triangles = quad()
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(sd, "mesh_uv_geometry", return_value=(positions, uv, triangles)):
            path = Path(folder) / "unit_diffuse.png"
            Image.fromarray(np.uint8(shadowed), "RGB").save(path)
            findings = sd.shadow_findings(Path(folder) / "unit.mesh", path)
            self.assertEqual([f[0] for f in findings], ["STATIC-SHADOW"])
            lifted, _report = sd.delight(Image.fromarray(np.uint8(shadowed), "RGB"), groups())
            lifted.save(path)
            self.assertEqual(sd.shadow_findings(Path(folder) / "unit.mesh", path), [])
            self.assertEqual(sd.shadow_findings(Path(folder) / "unit.mesh", Path(folder) / "none.png"), [])

    def test_facets_group_by_direction_and_edges(self) -> None:
        # a roof: two planes meeting at a ridge are two facet groups, a plane of four triangles is one
        positions = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0.5], [0, 1, 0.5], [1, 2, 0], [0, 2, 0]], dtype=float)
        triangles = np.array([[0, 1, 2], [0, 2, 3], [3, 2, 4], [3, 4, 5]])
        labels = sd.facet_labels(positions, triangles)
        self.assertEqual(labels[0], labels[1])
        self.assertEqual(labels[2], labels[3])
        self.assertNotEqual(labels[0], labels[2])


def solid(low, high):
    """A closed box, outward winding: (positions, triangles)."""

    x0, y0, z0 = low
    x1, y1, z1 = high
    p = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], dtype=float)
    t = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
    return p, t


def join(*parts):
    positions, triangles, offset = [], [], 0
    for p, t in parts:
        positions.append(p)
        triangles.append(t + offset)
        offset += len(p)
    return np.concatenate(positions), np.concatenate(triangles)


def slab_and_hall(yaw=0.0):
    positions, triangles = join(solid((-3, -3, 0), (3, 3, 0.2)), solid((-2, -1.5, 0.2), (2, 1.5, 3.0)))
    if yaw:
        c, s = np.cos(yaw), np.sin(yaw)
        positions = positions @ np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
    return positions, triangles


class SlabTests(unittest.TestCase):
    def test_a_slab_under_a_hall_is_found(self) -> None:
        slab = ss.find_slab(*slab_and_hall())
        self.assertIsNotNone(slab)
        self.assertAlmostEqual(slab["top_z"], 0.2, places=6)
        self.assertAlmostEqual(slab["width"], 6.0, places=6)

    def test_a_warped_corner_is_pulled_back_and_the_top_flattened(self) -> None:
        positions, triangles = slab_and_hall()
        warped = positions.copy()
        # the slab's corner (3, 3): top and bottom vertex pulled out into a spike, the top lifted
        corner = np.nonzero((np.abs(warped[:, 0] - 3) < 1e-9) & (np.abs(warped[:, 1] - 3) < 1e-9) & (warped[:, 2] < 0.3))[0]
        warped[corner, :2] += np.array([0.5, 0.35])
        top = [i for i in corner if warped[i, 2] > 0.1][0]
        warped[top, 2] += 0.03
        slab = ss.find_slab(warped, triangles)
        self.assertIsNotNone(slab)
        before = ss.outline_error(slab, warped)
        self.assertGreater(before, 0.3)
        self.assertGreater(ss.top_spread(slab, warped), 0.02)
        fixed, report = ss.square_slab(warped, slab)
        self.assertLess(ss.outline_error(slab, fixed), 1e-9)
        self.assertLess(ss.top_spread(slab, fixed), 1e-9)
        self.assertGreater(report["before"]["outline_error"], 0.3)
        self.assertLess(report["after"]["outline_error"], 1e-9)
        # the spike went back onto the straight edge, nothing above the slab moved, no vertex was added
        self.assertEqual(len(fixed), len(warped))
        self.assertLess(np.abs(fixed[corner, :2] - 3.0).max(), 0.06)
        building = warped[:, 2] > 0.25
        self.assertTrue(np.array_equal(fixed[building], warped[building]))

    def test_a_turned_slab_is_squared_in_its_own_frame(self) -> None:
        positions, triangles = slab_and_hall(yaw=np.radians(23))
        positions = positions.copy()
        corner = int(np.nonzero((positions[:, 2] < 0.1) & (np.linalg.norm(positions[:, :2] - positions[:, :2].mean(0), axis=1) > 4))[0][0])
        positions[corner, :2] *= 1.12
        slab = ss.find_slab(positions, triangles)
        self.assertAlmostEqual(abs(np.degrees(slab["yaw"])) % 90, 23 % 90, delta=2.0)
        fixed, _report = ss.square_slab(positions, slab)
        self.assertLess(ss.outline_error(slab, fixed), 1e-9)

    def test_a_clean_slab_does_not_move(self) -> None:
        positions, triangles = slab_and_hall()
        slab = ss.find_slab(positions, triangles)
        fixed, report = ss.square_slab(positions, slab)
        self.assertEqual(report["vertices_moved"], 0)
        self.assertTrue(np.allclose(fixed, positions))
        self.assertEqual(ss.slab_findings(positions, triangles), [])

    def test_a_building_without_a_slab_is_left_alone(self) -> None:
        positions, triangles = solid((-2, -1.5, 0.0), (2, 1.5, 3.0))
        self.assertIsNone(ss.find_slab(positions, triangles))

    def test_a_stepped_base_is_not_a_slab(self) -> None:
        positions, triangles = join(solid((-3, -3, 0), (3, 3, 0.2)), solid((-2.4, -2.4, 0.2), (2.4, 2.4, 0.4)), solid((-1.8, -1.8, 0.4), (1.8, 1.8, 0.6)), solid((-0.9, -0.9, 0.6), (0.9, 0.9, 5.0)))
        self.assertIsNone(ss.find_slab(positions, triangles))

    def test_a_round_base_is_not_a_slab(self) -> None:
        angle = np.linspace(0, 2 * np.pi, 33)[:-1]
        ring = np.stack([3 * np.cos(angle), 3 * np.sin(angle)], axis=1)
        n = len(ring)
        bottom = np.column_stack([ring, np.zeros(n)])
        top = np.column_stack([ring, np.full(n, 0.2)])
        positions = np.vstack([bottom, top, [[0, 0, 0.0], [0, 0, 0.2]]])
        triangles = []
        for i in range(n):
            j = (i + 1) % n
            triangles += [[i, j, n + j], [i, n + j, n + i], [2 * n + 1, n + i, n + j], [2 * n, j, i]]
        tower, tt = solid((-0.5, -0.5, 0.2), (0.5, 0.5, 4.0))
        positions, triangles = join((positions, np.array(triangles)), (tower, tt))
        self.assertIsNone(ss.find_slab(positions, triangles))

    def test_the_check_names_a_tilted_top_corner_and_a_corner_out_of_line(self) -> None:
        positions, triangles = slab_and_hall()
        normals = np.zeros_like(positions)
        normals[:, 2] = 1.0
        self.assertEqual(ss.slab_findings(positions, triangles, normals), [])
        slab = ss.find_slab(positions, triangles)
        top = slab["plate_vertices"][0]
        tilted = normals.copy()
        tilted[top] = (-0.55, 0.66, 0.52)
        findings = ss.slab_findings(positions, triangles, tilted)
        self.assertEqual([f[0] for f in findings], ["STATIC-SLAB"])
        self.assertIn("tilted", findings[0][2])
        out = positions.copy()
        corner = np.nonzero((np.abs(out[:, 0] - 3) < 1e-9) & (np.abs(out[:, 1] - 3) < 1e-9))[0]
        out[corner, :2] += 0.4
        self.assertIn("sticks out", ss.slab_findings(out, triangles)[0][2])


if __name__ == "__main__":
    unittest.main()
