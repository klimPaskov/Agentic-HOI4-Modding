"""The static route's last rules for a tank, on synthetic meshes and textures (no Blender): the roof the turret cut only clipped, the
ring radius, the band round the turret ring, the brightness spread lifted against vanilla, and a blown-off turret flying rigid."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np
from PIL import Image

from lib import static_delight as sd
from lib import static_kinds as sk

SIZE = 256
CUT = 2.0


def annulus(inner: float, outer: float, z: float, rings: int = 6, sectors: int = 32):
    """A flat ring of triangles at height z."""

    radii = np.linspace(inner, outer, rings + 1)
    angles = np.linspace(0, 2 * np.pi, sectors, endpoint=False)
    points = np.array([[r * np.cos(a), r * np.sin(a), z] for r in radii for a in angles])
    triangles = []
    for i in range(rings):
        for j in range(sectors):
            a, b = i * sectors + j, i * sectors + (j + 1) % sectors
            c, d = (i + 1) * sectors + j, (i + 1) * sectors + (j + 1) % sectors
            triangles += [[a, b, d], [a, d, c]]
    return points, np.array(triangles)


def roof_scene():
    """A band (0.9 to 1.45 of a ring radius of 1) inside a roof (1.6 to 2.5), at the cut height. UVs are a plan view (-4 to 4 sideways)."""

    band_p, band_t = annulus(0.9, 1.45, CUT - 0.01)
    roof_p, roof_t = annulus(1.6, 2.5, CUT - 0.01)
    positions = np.concatenate([band_p, roof_p])
    triangles = np.concatenate([band_t, roof_t + len(band_p)])
    uv = positions[:, :2] / 8.0 + 0.5
    return positions, uv, triangles


def roof_texture(band_colour, roof_colour=(106, 105, 68), seed=3):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    x, y = (xx + 0.5) / SIZE * 8 - 4, (yy + 0.5) / SIZE * 8 - 4
    inside = np.hypot(x, y) < 1.5
    rgb = np.where(inside[..., None], np.array(band_colour, float), np.array(roof_colour, float))
    rgb = rgb + rng.normal(0, 2.0, rgb.shape)
    return Image.fromarray(np.uint8(np.clip(rgb, 0, 255)), "RGB")


class RingFootprintTests(unittest.TestCase):
    def test_the_radius_is_the_closest_wall_crossing_and_fittings_lie_farther(self):
        angles = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        wall = [[np.cos(a), np.sin(a), CUT - 0.1] for a in angles] + [[np.cos(a), np.sin(a), CUT + 0.1] for a in angles]
        triangles = [[i, (i + 1) % 24, 24 + i] for i in range(24)]
        fender = [[2.0, 0.0, CUT - 0.1], [2.1, 0.0, CUT + 0.1], [2.2, 0.1, CUT + 0.1]]
        positions = np.array(wall + fender)
        triangles = np.array(triangles + [[48, 49, 50]])
        radius = sk.ring_footprint(positions, triangles, CUT, np.zeros(3))
        self.assertAlmostEqual(radius, 1.0, delta=0.05)

    def test_a_cut_nothing_crosses_is_an_error(self):
        with self.assertRaises(ValueError):
            sk.ring_footprint(np.zeros((3, 3)), np.array([[0, 1, 2]]), 5.0, np.zeros(3))


class HullLevelTests(unittest.TestCase):
    def test_a_roof_plate_outside_the_ring_just_over_the_cut_stays_on_the_hull(self):
        plate = np.array([[1.3, 0.2, CUT + 0.01], [1.5, 0.2, CUT + 0.01], [1.4, 0.4, CUT + 0.02]])
        bolt = np.array([[-1.4, 0.0, CUT + 0.02], [-1.5, 0.1, CUT + 0.05]])
        shell = np.array([[1.0, 0.0, CUT], [0.0, 1.0, CUT + 1.2], [-1.0, 0.0, CUT + 0.5]])  # the turret: reaches high
        hatch = np.array([[0.2, 0.2, CUT + 0.9], [0.3, 0.2, CUT + 0.95]])  # high on the turret
        tall_outside = np.array([[1.6, 0.0, CUT + 0.01], [1.6, 0.0, CUT + 0.9]])  # a bin on the turret rear: too tall for roof
        kept = sk.hull_level_pieces([plate, bolt, shell, hatch, tall_outside], CUT, CUT + 1.25, np.zeros(2), 1.0)
        self.assertEqual(kept, [0, 1])

    def test_a_piece_over_the_turret_seat_is_the_turrets_even_when_low(self):
        flange = np.array([[0.4, 0.0, CUT + 0.02], [1.3, 0.0, CUT + 0.03]])
        self.assertEqual(sk.hull_level_pieces([flange], CUT, CUT + 1.25, np.zeros(2), 1.0), [])


class RingSeamTests(unittest.TestCase):
    def run_seam(self, source):
        positions, uv, triangles = roof_scene()
        return sd.ring_seam(source, uv, positions, triangles, CUT, CUT + 1.25, np.zeros(3), 1.0)

    def test_a_yellow_green_band_takes_the_roof_colour(self):
        fixed, report = self.run_seam(roof_texture((178, 184, 60)))
        self.assertGreater(report["off_before"], 0.9)
        self.assertEqual(report["off_after"], 0.0)
        pixel = np.asarray(fixed.resize((SIZE, SIZE)))[SIZE // 2 + 44, SIZE // 2]  # a band texel (1.4 from the axis)
        self.assertLess(abs(float(pixel[0]) - 106.0), 16.0)
        self.assertLess(abs(float(pixel[2]) - 68.0), 12.0)

    def test_a_big_roof_triangle_along_the_ring_is_matched_by_its_texels_not_its_centre(self):
        """Four big triangles fan out from the turret's axis: each one's centre is far outside the band, but its edge runs along the
        ring, so its texels near the axis lie in the band (a Smart Mesh's big roof plates: the bright arc outside a turret base)."""

        z = CUT - 0.01
        fan_p = np.array([[0, 0, z], [5, 0, z], [0, 5, z], [-5, 0, z], [0, -5, z]], dtype=float)
        fan_t = np.array([[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 1]])
        band_p, band_t = annulus(0.9, 1.45, z, sectors=32)
        wedge = band_t[:3]  # the only band triangles: a small wedge by the +x axis
        positions = np.concatenate([fan_p, band_p])
        triangles = np.concatenate([fan_t, wedge + len(fan_p)])
        roof_p, roof_t = annulus(1.6, 2.5, z)
        triangles = np.concatenate([triangles, roof_t + len(positions)])
        positions = np.concatenate([positions, roof_p])
        uv = positions[:, :2] / 8.0 + 0.5
        fixed, report = sd.ring_seam(roof_texture((178, 184, 60)), uv, positions, triangles, CUT, CUT + 1.25, np.zeros(3), 1.0)
        self.assertGreater(report["band_texels_from_points"], 1000)
        pixel = np.asarray(fixed.resize((SIZE, SIZE)))[SIZE // 2 + 44, SIZE // 2]  # a band texel (1.4 from the axis) far from the wedge
        self.assertLess(abs(float(pixel[0]) - 106.0), 16.0)

    def test_the_roof_itself_is_not_touched(self):
        source = roof_texture((178, 184, 60))
        fixed, _ = self.run_seam(source)
        far = (slice(SIZE // 2 + 74, SIZE // 2 + 80), slice(SIZE // 2, SIZE // 2 + 6))  # 2.4 from the axis, in the roof
        self.assertTrue(np.array_equal(np.asarray(fixed)[far], np.asarray(source)[far]))

    def test_a_band_already_the_roof_colour_is_left_alone(self):
        source = roof_texture((106, 105, 68))
        fixed, report = self.run_seam(source)
        self.assertEqual(report["off_after"], report["off_before"])
        self.assertTrue(np.array_equal(np.asarray(fixed), np.asarray(source)))

    def test_a_model_with_no_roof_round_the_ring_is_skipped(self):
        positions, triangles = annulus(0.9, 1.45, CUT - 0.01)
        uv = positions[:, :2] / 8.0 + 0.5
        _fixed, report = sd.ring_seam(roof_texture((178, 184, 60)), uv, positions, triangles, CUT, CUT + 1.25, np.zeros(3), 1.0)
        self.assertIn("skipped", report)


class SmallPieceTests(unittest.TestCase):
    def test_small_pieces_are_the_separate_shells_under_the_size_share(self):
        big = annulus(0.9, 1.45, 0.0, rings=2, sectors=8)
        cube = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]], dtype=float) * 0.1 + [3, 0, 0]
        faces = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
        points = np.concatenate([big[0], cube])
        triangles = np.concatenate([big[1], faces + len(big[0])])
        pieces = sk.small_pieces(points, triangles, 0.1)
        self.assertEqual(len(pieces), 1)
        self.assertEqual(sorted(pieces[0].tolist()), list(range(len(big[1]), len(triangles))))


class InsideOutWallTests(unittest.TestCase):
    def box(self, flip_back):
        """A closed box 0..2 each way, outward faces, except that the back wall (y = 2) faces inward when `flip_back`."""

        p = np.array([[x, y, z] for x in (0, 2) for y in (0, 2) for z in (0, 2)], dtype=float)
        idx = lambda x, y, z: x * 4 + y * 2 + z
        quads = {"front": ([0, 1, 0], [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]), "back": ([0, 1, 0], [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]),
                 "bottom": ([0, 0, 1], [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]), "top": ([0, 0, 1], [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
                 "left": ([1, 0, 0], [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]), "right": ([1, 0, 0], [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)])}
        triangles, names = [], []
        for name, (_axis, corners) in quads.items():
            q = [idx(*c) for c in corners]
            tri = [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]
            normal = np.cross(p[tri[0][1]] - p[tri[0][0]], p[tri[0][2]] - p[tri[0][0]])
            centre = p[tri[0]].mean(axis=0)
            outward = float(normal @ (centre - np.array([1.0, 1.0, 1.0]))) > 0
            if outward == (name == "back" and flip_back):
                tri = [t[::-1] for t in tri]
            triangles += tri
            names += [name] * 2
        return p, np.array(triangles), names

    def test_a_wall_facing_into_the_model_is_found_and_the_others_are_not(self):
        p, t, names = self.box(flip_back=True)
        found = sk.inside_out_walls(p, t, share=0.01)
        self.assertEqual(sorted(names[i] for i in found), ["back", "back"])
        p, t, _names = self.box(flip_back=False)
        self.assertEqual(sk.inside_out_walls(p, t, share=0.01), [])

    def test_a_thin_one_sided_plate_is_left_alone(self):
        p = np.array([[0, 0, 0], [2, 0, 0], [2, 0, 2], [0, 0, 2]], dtype=float)
        self.assertEqual(sk.inside_out_walls(p, np.array([[0, 1, 2], [0, 2, 3]]), share=0.01), [])


class TreadToneTests(unittest.TestCase):
    def run_tread(self, colour):
        import tempfile

        from tripo import static_model

        contract = sk.kind_contract("vehicle")
        with tempfile.TemporaryDirectory() as folder:
            work, files = Path(folder) / "w", Path(folder) / "f"
            work.mkdir()
            files.mkdir()
            Image.new("RGB", (8, 8), colour).save(work / "t_diffuse.png")
            report = {"tracks": True, "track_atlas_uvs": [[0.5, 0.5]]}
            written = static_model.tread_textures(report, contract, "t", files, work)
        return written, report, contract["rules"]["tracks"]["tone"]["luma"]

    def test_a_run_painted_in_a_light_colour_is_darkened_to_vanillas_tread(self):
        written, report, tone = self.run_tread((200, 200, 120))
        self.assertIn("track_tone", report)
        self.assertLess(max(written["colour"]), 200)

    def test_a_run_already_darker_than_vanillas_tread_is_left_alone(self):
        written, report, _tone = self.run_tread((60, 60, 40))
        self.assertNotIn("track_tone", report)
        self.assertEqual(written["colour"], [60.0, 60.0, 40.0])


class ContrastTests(unittest.TestCase):
    def scene(self, amplitude):
        """A quad rising from height 0 to 3, its texture a horizontal gradient of the given brightness swing."""

        heights = np.array([0.0, 0.0, 3.0, 3.0])
        uv = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=float)
        triangles = np.array([[0, 1, 2], [0, 2, 3]])
        ramp = 100 + amplitude * (np.linspace(-1, 1, 64)[None, :] * np.ones((64, 1)))
        image = Image.fromarray(np.uint8(np.repeat(ramp[..., None], 3, axis=2)), "RGB")
        return image, uv, heights, triangles

    def test_a_flat_texture_is_lifted_but_not_past_the_maximum_gain(self):
        image, uv, heights, triangles = self.scene(8)
        fixed, report = sd.contrast_lift(image, uv, heights, triangles, 0.5)
        self.assertEqual(report["gain"], sd.CONTRAST_MAX_GAIN)
        self.assertGreater(report["spread_after"], report["spread_before"] * 1.3)
        self.assertLess(report["spread_after"], 0.5)
        self.assertEqual(fixed.size, (64, 64))

    def test_the_top_is_lightened_and_the_foot_darkened(self):
        image = Image.new("RGB", (64, 64), (100, 100, 100))
        uv = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=float)
        triangles = np.array([[0, 1, 2], [0, 2, 3]])
        # v runs down the texture: row 0 is v = 0 (height 0, the foot), the last row is the top
        fixed, _ = sd.contrast_lift(image, uv, np.array([0.0, 0.0, 3.0, 3.0]), triangles, 0.3)
        pixels = np.asarray(fixed, float)
        self.assertLess(pixels[2, 32, 1], pixels[61, 32, 1])

    def test_a_texture_already_lively_enough_is_left_as_it_is(self):
        image, uv, heights, triangles = self.scene(90)
        fixed, report = sd.contrast_lift(image, uv, heights, triangles, 0.05)
        self.assertEqual(report["spread_after"], report["spread_before"])
        self.assertTrue(np.array_equal(np.asarray(fixed), np.asarray(image)))


class DeathRigidTests(unittest.TestCase):
    def test_a_rigid_motion_does_not_drift_and_a_piece_with_its_own_motion_does(self):
        rng = np.random.default_rng(1)
        rest = rng.uniform(-1, 1, (200, 3))
        angle = 0.7
        turn = np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
        flown = rest @ turn.T + np.array([3.0, -2.0, 5.0])
        self.assertLess(sk.rigid_drift(rest, flown), 1e-9)
        loose = flown.copy()
        loose[:10] += np.array([0.0, 0.0, 0.4])  # a fitting that did not follow the turret
        self.assertGreater(sk.rigid_drift(rest, loose), 0.3)


if __name__ == "__main__":
    unittest.main()
