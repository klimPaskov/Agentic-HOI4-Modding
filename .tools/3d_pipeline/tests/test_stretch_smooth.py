"""Weight smoothing where a unit's clips stretch it (lib/stretch_smooth.py), on a synthetic bending strip (no Blender)."""

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

from lib import pdx_deform, stretch_smooth as S
from test_deformation_checks import BONES, write_anim, write_mesh

NAMES = [name for name, _parent, _position in BONES]


def strip(bone_of_x):
    """A strip along x from 1 to 3 in steps of 0.1, two rows at y 0.9 and 1.1; each vertex bound whole to `bone_of_x(x)`."""

    xs = [round(1.0 + 0.1 * i, 3) for i in range(21)]
    positions = [(x, y, 0.0) for x in xs for y in (0.9, 1.1)]
    triangles = []
    for i in range(len(xs) - 1):
        a, b, c, d = 2 * i, 2 * i + 1, 2 * i + 2, 2 * i + 3
        triangles += [(a, c, b), (b, c, d)]
    return positions, triangles, [NAMES.index(bone_of_x(x)) for x, _y, _z in positions]


def bend(frames):
    """The hand turns up to 90 degrees about z over the clip."""

    def pose(frame):
        angle = math.radians(90.0) * frame / max(frames - 1, 1)
        return {"HandR": ((1.0, 0.0, 0.0), (0.0, 0.0, math.sin(angle / 2), math.cos(angle / 2)))}

    return pose


class Smoothing(unittest.TestCase):
    def run_strip(self, bone_of_x, locked=(), prefixes=(), mask_of=None):
        positions, triangles, bones = strip(bone_of_x)
        with tempfile.TemporaryDirectory() as folder:
            mesh, anim, out = Path(folder) / "u.mesh", Path(folder) / "u_attack.anim", Path(folder) / "out.mesh"
            write_mesh(mesh, positions, triangles, bones)
            write_anim(anim, 12, bend(12))
            mask = None if mask_of is None else np.array([mask_of(x) for x, _y, _z in positions])
            result = S.smooth(mesh, [anim], out, locked_bones=locked, locked_prefixes=prefixes, locked_mask=mask)
            before = pdx_deform.deformation_report(pdx_deform.load_mesh(mesh), pdx_deform.load_anim(anim))
            smoothed = pdx_deform.load_mesh(out)
            after = pdx_deform.deformation_report(smoothed, pdx_deform.load_anim(anim))
            same = mesh.read_bytes() == out.read_bytes()
            size = (mesh.stat().st_size, out.stat().st_size)
        return result, before, after, smoothed, same, size

    def test_a_hard_weight_border_that_a_clip_bends_is_smoothed_until_it_stretches_less(self) -> None:
        result, before, after, smoothed, _same, (size_before, size_after) = self.run_strip(lambda x: "ArmR" if x < 2.0 else "HandR")
        self.assertGreater(before.stretched_edges + before.squashed_edges, 0, "the hard border deforms in the bend")
        self.assertTrue(result.changed, result.note)
        self.assertLess(after.stretched_edges + after.squashed_edges, before.stretched_edges + before.squashed_edges)
        self.assertEqual(result.before["u_attack"]["stretched"], before.stretched_edges, "the rule measures as UNIT-ANIM-STRETCH does")
        self.assertEqual(result.after["u_attack"]["stretched"], after.stretched_edges, "its rescoring of the region matches a full measure")
        self.assertEqual(size_before, size_after, "only the skin values change, in place")
        import json

        json.dumps(result.trials, sort_keys=True)  # run_pilot writes it into files.json with sorted keys (one key type)
        np.testing.assert_allclose(smoothed.weights.sum(axis=1), 1.0, atol=1e-5)
        self.assertLessEqual(int((smoothed.weights > 0).sum(axis=1).max()), 4)

    def test_only_bones_already_near_a_vertex_are_given_to_it(self) -> None:
        _result, _before, _after, smoothed, _same, _size = self.run_strip(lambda x: "ArmR" if x < 2.0 else "HandR")
        used = {smoothed.bones[j] for j in np.unique(smoothed.joints[smoothed.weights > 0])}
        self.assertEqual(used, {"ArmR", "HandR"})

    def test_a_locked_bone_keeps_its_vertices_whole(self) -> None:
        result, _before, _after, smoothed, same, _size = self.run_strip(lambda x: "ArmR" if x < 2.0 else "HandR", locked=("HandR",))
        hand = smoothed.joints[:, 0] == NAMES.index("HandR")
        self.assertTrue(np.all(smoothed.weights[hand, 0] == 1.0), "every vertex on the locked bone stays bound to it alone")
        self.assertTrue(result.changed or same)

    def test_a_locked_prefix_locks_every_bone_it_starts(self) -> None:
        _result, _before, _after, smoothed, _same, _size = self.run_strip(lambda x: "ArmR" if x < 2.0 else "HandR", prefixes=("Hand",))
        hand = smoothed.joints[:, 0] == NAMES.index("HandR")
        self.assertTrue(np.all(smoothed.weights[hand, 0] == 1.0))

    def test_a_locked_mask_keeps_its_vertices_whole(self) -> None:
        border = lambda x: 1.5 < x < 2.5  # the plate: the vertices around the hard border keep the weights they had
        _result, _before, _after, smoothed, _same, _size = self.run_strip(lambda x: "ArmR" if x < 2.0 else "HandR", mask_of=border)
        positions, _triangles, bones = strip(lambda x: "ArmR" if x < 2.0 else "HandR")
        kept = np.array([border(x) for x, _y, _z in positions])
        self.assertTrue(np.all(smoothed.weights[kept, 0] == 1.0), "a masked vertex stays bound to its own bone alone")

    def test_a_clip_that_deforms_nothing_leaves_the_file_as_it_was(self) -> None:
        result, before, _after, _smoothed, same, _size = self.run_strip(lambda x: "ArmR")
        self.assertEqual(before.stretched_edges + before.squashed_edges, 0)
        self.assertFalse(result.changed)
        self.assertTrue(same)

    def test_writing_the_weights_it_read_gives_the_same_file(self) -> None:
        positions, triangles, bones = strip(lambda x: "ArmR" if x < 2.0 else "HandR")
        with tempfile.TemporaryDirectory() as folder:
            mesh, out = Path(folder) / "u.mesh", Path(folder) / "out.mesh"
            write_mesh(mesh, positions, triangles, bones)
            loaded = pdx_deform.load_mesh(mesh)
            S.write_weights(mesh, out, loaded.joints, loaded.weights, loaded.bones)
            self.assertEqual(mesh.read_bytes(), out.read_bytes())


class Pieces(unittest.TestCase):
    def test_sparse_rows_keep_the_four_largest_and_normalise(self) -> None:
        joints, weights = S.sparse_rows(np.array([[0.1, 0.2, 0.3, 0.4, 0.5], [1.0, 0, 0, 0, 0]]))
        self.assertEqual(sorted(joints[0].tolist()), [1, 2, 3, 4])
        self.assertAlmostEqual(float(weights[0].sum()), 1.0)
        self.assertEqual(joints[1].tolist(), [0, -1, -1, -1])

    def test_smoothing_moves_only_the_region_and_fades_into_the_fixed_skin(self) -> None:
        dense = np.array([[1.0, 0.0]] * 3 + [[0.0, 1.0]] * 3)
        edges = np.array([[i, i + 1] for i in range(5)])
        region = np.array([False, True, True, True, True, False])
        out = S.smooth_dense(dense, edges, region, 8)
        np.testing.assert_allclose(out[[0, 5]], dense[[0, 5]])
        self.assertTrue(np.all(np.diff(out[:, 1]) >= -1e-9), "the second bone's weight rises steadily along the strip")

    def hand_body(self, joined: bool):
        """An arm (x 1 to 2.5, the hand from x 2) and, apart from it, a body path whose first point lies under the hand and holds 40% of
        the hand's weight. `joined` links the hand to that point, as a hand fused to the body."""

        from types import SimpleNamespace

        arm = [(1.0 + 0.1 * i, 0.0, 0.0) for i in range(16)]
        body = [(2.2, -0.3 - 0.05 * i, 0.0) for i in range(100)]
        positions = np.array(arm + body)
        edges = [[i, i + 1] for i in range(15)] + [[16 + i, 17 + i] for i in range(99)] + ([[12, 16]] if joined else [])
        dense = np.zeros((len(positions), 3))
        dense[:10, 1] = 1.0
        dense[10:16, 2] = 1.0
        dense[16:, 0] = 1.0
        dense[16] = [0.6, 0.0, 0.4]
        mesh = SimpleNamespace(bones=["Hips", "RightForeArm", "RightHand"], positions=positions, shape=np.zeros(len(positions), int))
        return mesh, dense, np.arange(len(positions)), np.array(edges)

    def unbleed(self, joined: bool):
        from unittest import mock

        from lib import pdx_motion

        mesh, dense, canon, edges = self.hand_body(joined)
        with mock.patch.object(pdx_motion, "rest_joints", return_value=np.array([[0.0, 0, 0], [1.0, 0, 0], [2.0, 0, 0]])):
            return dense, S.unbleed_hands(mesh, dense, canon, edges)

    def test_hand_weight_on_skin_apart_from_the_hand_goes_to_that_skins_other_bones(self) -> None:
        dense, (out, changed) = self.unbleed(joined=False)
        self.assertEqual(changed, 1)
        np.testing.assert_allclose(out[16], [1.0, 0.0, 0.0])
        np.testing.assert_allclose(out[:16], dense[:16], err_msg="the arm and the hand keep their weights")
        np.testing.assert_allclose(out[17:], dense[17:])

    def test_a_hand_joined_to_the_body_is_left_alone(self) -> None:
        dense, (out, changed) = self.unbleed(joined=True)
        self.assertEqual(changed, 0)
        np.testing.assert_allclose(out, dense)

    def test_the_thigh_split_moves_the_shared_part_of_both_thighs_to_the_pelvis(self) -> None:
        from unittest import mock

        from lib import pdx_motion

        legs = pdx_motion.LegSet([pdx_motion.Leg(1, 3, 4, -1, 1.0), pdx_motion.Leg(2, 5, 6, -1, 1.0)], 0, None)
        # pelvis, left thigh, right thigh: a skirt point between the legs, one on a thigh alone, and one locked (a cloak)
        dense = np.array([[0.0, 0.5, 0.5], [0.0, 1.0, 0.0], [0.2, 0.4, 0.4]])
        locked = np.array([False, False, True])
        with mock.patch.object(pdx_motion, "find_legs", return_value=legs):
            out = S.split_thighs(object(), dense, locked, 0.5)
        np.testing.assert_allclose(out[0], [0.5, 0.25, 0.25])
        np.testing.assert_allclose(out[1:], dense[1:], err_msg="a one-thigh point and a locked point keep their weights")
        np.testing.assert_allclose(out.sum(axis=1), dense.sum(axis=1))
        with mock.patch.object(pdx_motion, "find_legs", return_value=pdx_motion.LegSet([], -1, None)):
            self.assertIsNone(S.split_thighs(object(), dense, locked, 0.5), "no legs, no split")


if __name__ == "__main__":
    unittest.main()
