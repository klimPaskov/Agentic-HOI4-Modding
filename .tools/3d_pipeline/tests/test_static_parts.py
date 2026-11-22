"""The static route's parts reduction (lib/static_parts.py): need, shares, the shape loop and part GLBs."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np

from lib import static_parts as parts


def box(low, high):
    """A closed box as 12 triangles, wound outward."""

    (x0, y0, z0), (x1, y1, z1) = low, high
    p = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], dtype=float)
    t = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
    return p, t


def sphere(centre, radius, rings=12, segments=16):
    """A closed UV sphere."""

    points = [[0, 0, radius]]
    for i in range(1, rings):
        theta = math.pi * i / rings
        for j in range(segments):
            phi = 2 * math.pi * j / segments
            points.append([radius * math.sin(theta) * math.cos(phi), radius * math.sin(theta) * math.sin(phi), radius * math.cos(theta)])
    points.append([0, 0, -radius])
    triangles = []
    last = len(points) - 1
    for j in range(segments):
        triangles.append([0, 1 + j, 1 + (j + 1) % segments])
    for i in range(rings - 2):
        a, b = 1 + i * segments, 1 + (i + 1) * segments
        for j in range(segments):
            k = (j + 1) % segments
            triangles += [[a + j, b + j, b + k], [a + j, b + k, a + k]]
    base = 1 + (rings - 2) * segments
    for j in range(segments):
        triangles.append([last, base + (j + 1) % segments, base + j])
    return np.array(points, dtype=float) + np.asarray(centre, dtype=float), np.array(triangles)


def slab(size, cells):
    """A closed flat slab of `cells` x `cells` squares on top and bottom (many triangles, little detail)."""

    xs = np.linspace(0, size, cells + 1)
    grid = np.array([[x, y] for y in xs for x in xs])
    top = np.column_stack([grid, np.full(len(grid), 0.1)])
    bottom = np.column_stack([grid, np.zeros(len(grid))])
    points = np.vstack([top, bottom])
    n = cells + 1
    triangles = []
    for r in range(cells):
        for c in range(cells):
            a, b, d, e = r * n + c, r * n + c + 1, (r + 1) * n + c, (r + 1) * n + c + 1
            triangles += [[a, b, e], [a, e, d], [a + n * n, e + n * n, b + n * n], [a + n * n, d + n * n, e + n * n]]
    rim = [r * 0 + c for c in range(cells)] + [c * n + cells for c in range(cells)] + [cells * n + cells - c for c in range(cells)] + [(cells - c) * n for c in range(cells)]
    for k, a in enumerate(rim):
        b = rim[(k + 1) % len(rim)]
        triangles += [[a, a + n * n, b], [b, a + n * n, b + n * n]]
    return points, np.array(triangles)


def drop_every_other(mesh, keep):
    """A crude reducer for tests: keep the first `keep` triangles (opens a closed part)."""

    p, t = mesh
    return p, t[:keep]


class Need(unittest.TestCase):
    def test_a_box_bends_at_its_twelve_edges_and_a_slab_little(self) -> None:
        need = parts.part_need(*box((0, 0, 0), (1, 1, 1)))
        self.assertEqual(need["triangles"], 12)
        self.assertAlmostEqual(need["area"], 6.0)
        self.assertAlmostEqual(need["bend"], 12 * math.pi / 2, places=6)
        # a slab bends only at its rim (two loops round 4 x 4 and four corners 0.1 high), not across its 480 flat triangles
        flat = parts.part_need(*slab(4.0, 10))
        self.assertAlmostEqual(flat["bend"], 2 * 16 * math.pi / 2 + 4 * 0.1 * math.pi / 2, places=6)

    def test_open_edges_of_a_closed_and_an_open_part(self) -> None:
        p, t = box((0, 0, 0), (1, 1, 1))
        self.assertEqual(parts.open_edges(p, t), 0)
        self.assertEqual(parts.open_edges(p, t[2:]), 4)


class Allocate(unittest.TestCase):
    def test_shares_follow_need_and_never_pass_a_part_count(self) -> None:
        plate, ball, small = slab(4.0, 30), sphere((10, 0, 0), 0.5), box((20, 0, 0), (20.2, 0.2, 0.2))
        needs = [parts.part_need(*m) for m in (plate, ball, small)]
        shares = parts.allocate(needs, 1200)
        self.assertLessEqual(sum(shares), 1200)
        self.assertEqual(shares[2], 12)  # the small box keeps all it has
        self.assertTrue(all(s <= n["triangles"] for s, n in zip(shares, needs)))
        # the ball (much bend for its area) gets a larger share of its own triangles than the plate
        self.assertGreater(shares[1] / needs[1]["triangles"], shares[0] / needs[0]["triangles"])

    def test_within_the_target_every_part_keeps_all(self) -> None:
        needs = [parts.part_need(*box((0, 0, 0), (1, 1, 1))), parts.part_need(*sphere((3, 0, 0), 1))]
        self.assertEqual(parts.allocate(needs, 10_000), [n["triangles"] for n in needs])

    def test_lower_bounds_over_the_target_stop(self) -> None:
        needs = [parts.part_need(*sphere((0, 0, 0), 1)), parts.part_need(*sphere((3, 0, 0), 1))]
        with self.assertRaises(parts.PartsBudgetError):
            parts.allocate(needs, 300, lower=[200, 200])


class ReduceLoop(unittest.TestCase):
    def setUp(self) -> None:
        self.meshes = [slab(4.0, 30), sphere((10, 0, 0), 0.5, rings=16, segments=24)]
        self.calls = []

    def reducer(self, i, triangles):
        self.calls.append((i, triangles))
        p, t = self.meshes[i]
        return p, t[: min(len(t), triangles)]

    def test_a_part_whose_shape_fails_grows_its_share_from_the_others(self) -> None:
        # a fake check: the ball needs 600 triangles, the slab anything
        def checker(original, reduced, min_iou):
            ok = len(reduced[1]) >= 600 or len(original[1]) > 3000
            return {"iou": {"front": 1.0 if ok else 0.5}, "open_edges_before": 0, "open_edges_after": 0}, [] if ok else ["the front silhouette agrees only 0.5"]

        receipt = parts.reduce_parts(["slab", "ball"], self.meshes, 1500, self.reducer, checker=checker)
        self.assertGreaterEqual(receipt["parts"]["ball"]["to"], 600)
        self.assertLessEqual(receipt["triangles"], 1500)
        # its least share is found close above 600 (within the search precision), more than its share by need
        self.assertTrue(600 <= receipt["parts"]["ball"]["least"] <= 640, receipt["parts"]["ball"])
        self.assertLess(receipt["parts"]["ball"]["first_share"], 600)
        # the reducer's last call for each part is its chosen share
        last = {i: n for i, n in self.calls}
        self.assertEqual(last[1], receipt["parts"]["ball"]["share"])
        self.assertEqual(last[0], receipt["parts"]["slab"]["share"])

    def test_least_share_searches_down_from_a_pass_and_up_from_a_fail(self) -> None:
        asked = []

        def passes(n):
            asked.append(n)
            return n >= 317

        self.assertTrue(317 <= parts.least_share(passes, 1000, 5000) <= 317 * 1.05 + 8)
        self.assertTrue(317 <= parts.least_share(passes, 40, 5000) <= 317 * 1.05 + 8)
        self.assertEqual(parts.least_share(lambda n: True, 400, 5000), parts.MIN_PART_TRIANGLES)
        self.assertEqual(parts.least_share(lambda n: n >= 90, 30, 90), 90)  # all of a small part always passes
        self.assertLess(len(asked), 30)

    def test_when_the_failing_parts_need_more_than_the_target_it_stops_with_their_names(self) -> None:
        def checker(original, reduced, min_iou):
            return {"iou": {}, "open_edges_before": 0, "open_edges_after": 0}, ["the side silhouette agrees only 0.4"]

        with self.assertRaises(parts.PartsBudgetError) as raised:
            parts.reduce_parts(["slab", "ball"], self.meshes, 400, self.reducer, checker=checker)
        self.assertIn("ball", str(raised.exception))
        self.assertIn("part_shape_iou", str(raised.exception))

    def test_the_real_check_refuses_a_reduction_that_opens_a_closed_part(self) -> None:
        ball = self.meshes[1]
        _shape, problems = parts.part_problems(ball, (ball[0], ball[1][:-40]))
        self.assertTrue(any("opened the part" in p for p in problems), problems)
        _shape, problems = parts.part_problems(ball, ball)
        self.assertEqual(problems, [])

    def test_silhouette_problems_ignore_the_shell_count(self) -> None:
        shape = {"iou": {"front": 0.99, "side": 0.9, "top": 0.98}, "shells_before": {"shells": 1}, "shells_after": {"shells": 3}}
        self.assertEqual(len(parts.silhouette_problems(shape)), 1)


class Whole(unittest.TestCase):
    def test_a_part_wholly_over_a_cut_goes_whole_and_a_straddling_one_is_cut(self) -> None:
        ids = np.array([1, 1, 1, 1, 2, 2, 3, 3, 0])
        areas = np.array([1, 1, 1, 0.05, 1, 1, 1, 0.02, 1])
        over = np.array([True, True, True, False, True, False, False, False, True])
        self.assertEqual(parts.whole_parts(ids, areas, over), {1: True, 3: False})


def track_loop(length, height, thick, width, x0=1.5, segments=24):
    """A track run as a closed loop seen from the side: a thin band round a stadium, extruded across (x)."""

    radius = height / 2
    outline = []
    for k in range(segments):
        a = math.pi / 2 + math.pi * k / (segments - 1)
        outline.append((-length / 2 + radius + radius * math.cos(a), radius + radius * math.sin(a)))
    for k in range(segments):
        a = -math.pi / 2 + math.pi * k / (segments - 1)
        outline.append((length / 2 - radius + radius * math.cos(a), radius + radius * math.sin(a)))
    centre = np.array([0.0, radius])
    outer = np.array(outline)
    inner = centre + (outer - centre) * (1 - thick / radius)
    points, triangles = [], []
    rings = [outer, inner]
    for x in (x0, x0 + width):
        for ring in rings:
            points += [[x, y, z] for y, z in ring]
    n = len(outer)
    base = {(side, ring): (2 * side + ring) * n for side in (0, 1) for ring in (0, 1)}
    for k in range(n):
        j = (k + 1) % n
        for side in (0, 1):
            o, i = base[(side, 0)], base[(side, 1)]
            triangles += [[o + k, o + j, i + j], [o + k, i + j, i + k]]
        for ring in (0, 1):
            a, b = base[(0, ring)], base[(1, ring)]
            triangles += [[a + k, b + k, b + j], [a + k, b + j, a + j]]
    return np.array(points, dtype=float), np.array(triangles)


class TrackRuns(unittest.TestCase):
    def test_a_loop_is_a_track_run_and_a_band_with_its_bogies_is_not(self) -> None:
        from lib import static_kinds as sk

        loop = track_loop(6.0, 1.0, 0.08, 0.5)
        band = box((1.5, -3.0, 0.0), (2.0, 3.0, 1.0))
        self.assertLess(sk.side_fill(*loop, np.arange(len(loop[0]))), 0.3)
        self.assertGreater(sk.side_fill(*band, np.arange(len(band[0]))), sk.TRACK_FILL_MAX)
        hull = box((-1.4, -3.0, 0.4), (1.4, 3.0, 2.0))
        rule = sk.kind_contract("vehicle")["rules"]["wheels"]
        for piece, runs in ((loop, True), (band, False)):
            points = np.vstack([hull[0], piece[0]])
            triangles = np.vstack([hull[1], piece[1] + len(hull[0])])
            found = sk.running_gear(points, triangles, rule)["tracks"]
            self.assertEqual(len(found) > 0, runs)


class PartsGlb(unittest.TestCase):
    def test_a_multi_part_glb_reads_back_part_by_part_and_plans_shares(self) -> None:
        hull = box((-1.5, -3, 0.4), (1.5, 3, 1.6))
        turret = sphere((0, 0.4, 2.1), 0.7)
        left, right = box((-2, -3.2, 0), (-1.5, 3.2, 0.9)), box((1.5, -3.2, 0), (2, 3.2, 0.9))
        gun = box((-0.08, -3.4, 2.0), (0.08, -0.4, 2.16))
        pieces = [("hull", *hull), ("turret", *turret), ("gun", *gun), ("track_left", *left), ("track_right", *right)]
        with tempfile.TemporaryDirectory() as folder:
            path = parts.write_parts_glb(pieces, Path(folder) / "parts.glb")
            read = parts.glb_parts(path)
            self.assertEqual([name for name, _p, _t in read], ["hull", "turret", "gun", "track_left", "track_right"])
            for (_n, p, t), (_m, q, u) in zip(pieces, read):
                np.testing.assert_allclose(p, q, atol=1e-5)
                np.testing.assert_array_equal(t, u)
            sys.path.insert(0, str(PIPELINE / "tripo"))
            import static_model

            from lib import static_kinds as sk

            contract = sk.kind_contract("vehicle")
            contract = dict(contract, triangle_budget={"value": 400})
            plan = static_model.parts_plan(path, contract, {})
            self.assertEqual(set(plan["parts"]), {"hull", "turret", "gun", "track_left", "track_right"})
            self.assertLessEqual(sum(v["share"] for v in plan["parts"].values()), plan["target"])
            self.assertEqual(plan["parts"]["gun"]["share"], 12)
            self.assertIsNone(static_model.parts_plan(path, contract, {"parts": False}))


class RunningGear(unittest.TestCase):
    def test_a_raise_for_the_running_gear_widens_the_budget_and_always_warns(self) -> None:
        from lib import static_kinds as sk

        vehicle = sk.kind_contract("vehicle")
        self.assertIs(sk.with_running_gear(vehicle, 0), vehicle)
        raised = sk.with_running_gear(vehicle, 3600)
        self.assertEqual(raised["triangle_budget"]["value"], vehicle["triangle_budget"]["value"] + 3600)
        self.assertEqual(raised["triangle_budget"]["vanilla"], vehicle["triangle_budget"]["value"])
        self.assertEqual(vehicle["triangle_budget"].get("running_gear"), None)
        with self.assertRaises(ValueError):
            sk.with_running_gear(sk.kind_contract("building"), 100)
        with self.assertRaises(ValueError):
            sk.with_running_gear(vehicle, -5)


if __name__ == "__main__":
    unittest.main()
