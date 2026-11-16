"""Skin weights fitted to a unit's own clips (lib/weight_fit.py), on synthetic bending strips (no Blender)."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import numpy as np

from lib import pdx_deform, stretch_smooth, weight_fit as W
from test_deformation_checks import BONES, write_anim, write_mesh

NAMES = [name for name, _parent, _position in BONES]


def strip():
    """A strip along x from 1 to 3 in steps of 0.1, two rows at y 0.9 and 1.1."""

    xs = [round(1.0 + 0.1 * i, 3) for i in range(21)]
    positions = [(x, y, 0.0) for x in xs for y in (0.9, 1.1)]
    triangles = []
    for i in range(len(xs) - 1):
        a, b, c, d = 2 * i, 2 * i + 1, 2 * i + 2, 2 * i + 3
        triangles += [(a, c, b), (b, c, d)]
    return positions, triangles


def bend(frames, degrees=90.0):
    """The hand turns up to `degrees` about z over the clip."""

    def pose(frame):
        angle = math.radians(degrees) * frame / max(frames - 1, 1)
        return {"HandR": ((1.0, 0.0, 0.0), (0.0, 0.0, math.sin(angle / 2), math.cos(angle / 2)))}

    return pose


def set_weights(path: Path, rows) -> None:
    """Rewrite `path`'s skin: `rows` gives each vertex {bone name: weight}."""

    mesh = pdx_deform.load_mesh(path)
    dense = np.zeros((len(mesh.positions), len(mesh.bones)))
    for v, row in enumerate(rows):
        for name, weight in row.items():
            dense[v, mesh.bones.index(name)] = weight
    joints, weights = stretch_smooth.sparse_rows(dense)
    stretch_smooth.write_weights(path, path, joints, weights, mesh.bones)


class Fit(unittest.TestCase):
    def run_strip(self, row_of_x, locked=(), prefixes=(), locked_mask=None, degrees=90.0):
        positions, triangles = strip()
        with tempfile.TemporaryDirectory() as folder:
            mesh, anim, out = Path(folder) / "u.mesh", Path(folder) / "u_attack.anim", Path(folder) / "out.mesh"
            write_mesh(mesh, positions, triangles, [0] * len(positions))
            set_weights(mesh, [row_of_x(x) for x, _y, _z in positions])
            write_anim(anim, 12, bend(12, degrees))
            result = W.fit(mesh, [anim], out, locked_bones=locked, locked_prefixes=prefixes, locked_mask=locked_mask)
            before = pdx_deform.deformation_report(pdx_deform.load_mesh(mesh), pdx_deform.load_anim(anim))
            fitted = pdx_deform.load_mesh(out)
            after = pdx_deform.deformation_report(fitted, pdx_deform.load_anim(anim))
            same = mesh.read_bytes() == out.read_bytes()
            sizes = (mesh.stat().st_size, out.stat().st_size)
        return result, before, after, fitted, same, sizes

    def test_a_hard_weight_border_that_a_clip_bends_is_fitted_until_it_deforms_less(self) -> None:
        result, before, after, fitted, _same, (size_before, size_after) = self.run_strip(
            lambda x: {"ArmR": 1.0} if x < 2.0 else {"HandR": 1.0})
        deformed = before.stretched_edges + before.squashed_edges
        self.assertGreater(deformed, 0, "the hard border deforms in the bend")
        self.assertTrue(result.changed, result.note)
        self.assertLess(after.stretched_edges + after.squashed_edges, deformed)
        self.assertEqual(result.before["u_attack"]["stretched"], before.stretched_edges, "the rule measures as UNIT-ANIM-STRETCH does")
        self.assertEqual(result.after["u_attack"]["stretched"], after.stretched_edges, "its rescoring matches a full measure")
        self.assertLessEqual(after.worst_stretch_share, before.worst_stretch_share * (1 + stretch_smooth.WORSEN_SHARE) + 1e-6)
        self.assertEqual(size_before, size_after, "only the skin values change, in place")
        np.testing.assert_allclose(fitted.weights.sum(axis=1), 1.0, atol=1e-5)
        self.assertLessEqual(int((fitted.weights > 0).sum(axis=1).max()), 4)
        used = {fitted.bones[j] for j in np.unique(fitted.joints[fitted.weights > 0])}
        self.assertEqual(used, {"ArmR", "HandR"}, "only bones already near a vertex are given to it")

    def test_a_bone_the_limb_does_not_follow_is_fitted_out_of_it(self) -> None:
        # The far part of the limb holds half the weight of a bone that stays still (as the orc's forearm held the upper spine's). Bent
        # 150 degrees, linear blending folds that part onto itself and its edges squash. The fit takes most of that deformation out.
        def row(x):
            if x < 2.0:
                return {"ArmR": 1.0}
            if x < 2.5:
                return {"HandR": 1.0}
            return {"HandR": 0.5, "Root": 0.5}

        result, before, after, _fitted, _same, _sizes = self.run_strip(row, degrees=150.0)
        deformed = before.stretched_edges + before.squashed_edges
        self.assertTrue(result.changed, result.note)
        self.assertGreater(deformed, 10)
        self.assertLess(3 * (after.stretched_edges + after.squashed_edges), deformed)

    def test_locked_bones_prefixes_and_masked_vertices_keep_their_weights(self) -> None:
        def row(x):
            return {"ArmR": 1.0} if x < 2.0 else {"HandR": 1.0}

        positions, _triangles = strip()
        mask = np.array([1.7 <= x <= 1.9 for x, _y, _z in positions])
        for kwargs in ({"locked": ("HandR",)}, {"prefixes": ("Hand",)}, {"locked_mask": mask}):
            with self.subTest(**{key: str(value) for key, value in kwargs.items()}):
                _result, _before, _after, fitted, _same, _sizes = self.run_strip(row, **kwargs)
                if "locked_mask" in kwargs:
                    keep = mask
                else:
                    keep = fitted.positions[:, 0] >= 2.0
                self.assertTrue(np.all(fitted.weights[keep, 0] == 1.0), "a locked vertex stays bound whole to its bone")
                expected = [NAMES.index("ArmR" if x < 2.0 else "HandR") for x in fitted.positions[keep, 0]]
                self.assertEqual(fitted.joints[keep, 0].tolist(), expected)
                hand = NAMES.index("HandR")
                if "locked" in kwargs or "prefixes" in kwargs:
                    gained = (fitted.joints == hand) & (fitted.weights > 0) & (fitted.positions[:, 0] < 2.0)[:, None]
                    self.assertFalse(gained.any(), "a locked bone is never added to a vertex that did not hold it")

    def test_a_clip_that_deforms_nothing_leaves_the_file_as_it_was(self) -> None:
        result, before, _after, _fitted, same, _sizes = self.run_strip(lambda x: {"ArmR": 1.0})
        self.assertEqual(before.stretched_edges + before.squashed_edges, 0)
        self.assertFalse(result.changed)
        self.assertTrue(same)


class Stage(unittest.TestCase):
    def test_the_stage_fits_the_staged_mesh_in_place_and_records_what_changed(self) -> None:
        import run_pilot

        positions, triangles = strip()
        with tempfile.TemporaryDirectory() as folder:
            staged = Path(folder)
            mesh = staged / "unit.mesh"
            write_mesh(mesh, positions, triangles, [0] * len(positions))
            set_weights(mesh, [{"ArmR": 1.0} if x < 2.0 else {"HandR": 1.0} for x, _y, _z in positions])
            write_anim(staged / "unit_attack.anim", 12, bend(12))
            original = mesh.read_bytes()
            record = run_pilot.fit_clip_weights(staged, "unit", ["attack"], {})
            self.assertTrue(record["changed"], record["note"])
            self.assertLess(record["deformed_edges_after"], record["deformed_edges_before"])
            self.assertEqual(record["plate_vertices_locked"], 0)
            self.assertNotEqual(mesh.read_bytes(), original, "the staged mesh is rewritten in place")
            self.assertEqual(len(mesh.read_bytes()), len(original))


class Pieces(unittest.TestCase):
    def test_the_simplex_projection_keeps_rows_on_their_candidates(self) -> None:
        values = np.array([[0.5, 0.5, 0.5], [2.0, -1.0, 0.0], [0.2, 0.9, 0.3]])
        mask = np.array([[True, True, True], [True, True, True], [True, False, True]])
        out = W._project_simplex(values, mask)
        np.testing.assert_allclose(out.sum(axis=1), 1.0)
        self.assertTrue(np.all(out >= 0))
        np.testing.assert_allclose(out[0], [1 / 3] * 3)
        np.testing.assert_allclose(out[1], [1.0, 0.0, 0.0])
        self.assertEqual(out[2, 1], 0.0, "a bone that is not a candidate stays at zero")
        np.testing.assert_allclose(out[2], [0.45, 0.0, 0.55])

    def test_the_gather_adds_each_edge_to_its_first_vertex_and_takes_it_from_its_second(self) -> None:
        first, second = np.array([0, 1, -1]), np.array([1, -1, 0])
        gather = W._Gather(first, second, 3)
        out = gather(np.array([[1.0], [10.0], [100.0]], np.float32))
        np.testing.assert_allclose(out[:, 0], [1.0 - 100.0, 10.0 - 1.0, 0.0])


if __name__ == "__main__":
    unittest.main()
