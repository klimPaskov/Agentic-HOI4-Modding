"""The clip pick's pose measure (tripo/pose_check.py): a GLB's clips played on a unit's exported skeleton, and the swell, neck, raise and
reach measured there. A fake GLB rig stands in for the file: the unit's own clip, mirrored and scaled the way an export flips and sizes the
GLB's axes. No Blender."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import pose_check as PC
import test_tripo_shoulder as TS
from lib import pdx_deform, pdx_motion, tripo_shoulder

MIRROR = np.diag([1.0, 1.0, -1.0])
SCALE = 0.25


class FakeRig:
    """A GLB rig whose joints are the mesh's, in mirrored and scaled axes, with one clip that plays `anim`."""

    def __init__(self, mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation):
        self.mesh, self.anim = mesh, anim
        self.joint_names = [PC.glb_name(name) for name in mesh.bones]
        self.bind = np.linalg.inv(mesh.inverse_bind)
        self.posed = pdx_deform.skinning_matrices(mesh, anim) @ self.bind[None]

    def _glb(self, worlds: np.ndarray) -> np.ndarray:
        out = worlds.copy()
        out[:, :3, :3] = MIRROR @ worlds[:, :3, :3] @ MIRROR
        out[:, :3, 3] = SCALE * worlds[:, :3, 3] @ MIRROR.T
        return out

    def pose_for(self, tracks, t):
        return {"frame": int(round(t * PC.FRAME_RATE))}

    def joint_worlds(self, pose):
        return self._glb(self.bind if not pose else self.posed[min(pose["frame"], self.anim.frames - 1)])

    def clips(self):
        yield "clip", {}, (self.anim.frames - 1) / PC.FRAME_RATE


class Transfer(TS.Unit):
    def test_procrustes_finds_a_mirror_and_a_scale(self) -> None:
        points = np.random.default_rng(1).normal(size=(12, 3))
        axes, scale, offset = PC.procrustes(points, 3.0 * points @ MIRROR.T + np.array([1.0, 2.0, 3.0]))
        self.assertTrue(np.allclose(axes, MIRROR, atol=1e-9))
        self.assertAlmostEqual(scale, 3.0, places=9)
        self.assertTrue(np.allclose(offset, [1.0, 2.0, 3.0], atol=1e-9))

    def test_a_clip_played_back_on_the_mesh_puts_every_joint_where_it_was(self) -> None:
        anim = pdx_deform.load_anim(self.clip("attack", 9, lambda f: {**TS.bent(6.0 * f), "RightArm": (TS.local("RightArm"), TS.about(2, 10.0 * f))}))
        transfer = PC.Transfer(FakeRig(self.mesh, anim), self.mesh)
        self.assertAlmostEqual(transfer.scale, 1.0 / SCALE, places=6)
        played = transfer.animation({}, (anim.frames - 1) / PC.FRAME_RATE)
        self.assertEqual(played.frames, anim.frames)
        self.assertTrue(np.allclose(pdx_motion.posed_joints(self.mesh, played), pdx_motion.posed_joints(self.mesh, anim), atol=1e-6))


class Measure(TS.Unit):
    def test_a_swollen_clip_fails_and_the_routes_ease_brings_it_under_the_limit(self) -> None:
        anim = pdx_deform.load_anim(self.clip("attack", 21, lambda f: TS.bent(60.0 * math.sin(math.pi * f / 20))))
        raw = PC.measure(self.mesh, anim)
        self.assertEqual(raw["verdict"], "fail")
        self.assertGreater(raw["swell"], tripo_shoulder.SWELL_LIMIT)
        idle = pdx_deform.load_anim(self.clip("idle", 3, lambda f: {}))
        after = PC.measure(self.mesh, PC.route(self.mesh, anim, idle))
        self.assertEqual(after["verdict"], "pass")
        self.assertLessEqual(after["swell"], tripo_shoulder.SWELL_TARGET + 1e-9)

    def test_the_raise_is_the_holding_joint_above_the_chest(self) -> None:
        names = self.mesh.bones
        joints = pdx_motion.rest_joints(self.mesh)
        height = self.mesh.height
        still = PC.measure(self.mesh, pdx_deform.load_anim(self.clip("idle", 3, lambda f: {})), hand="RightForeArm")
        rest = (joints[names.index("RightForeArm"), 1] - joints[names.index("Spine02"), 1]) / height
        self.assertAlmostEqual(still["raise_"], round(float(rest), 3), places=3)
        self.assertEqual(still["pelvis_travel"], 0.0)
        raised = PC.measure(self.mesh, pdx_deform.load_anim(self.clip("attack", 3, lambda f: {"RightArm": (TS.local("RightArm"), TS.about(2, 150.0))})),
                            hand="RightForeArm")
        self.assertGreater(raised["raise_"], still["raise_"] + 0.1)


if __name__ == "__main__":
    unittest.main()
