"""The robe re-rig for a robed humanoid whose skeleton Tripo misplaced (lib/tripo_robe_rig.py, tripo/robe_rig.py). A synthetic figure: a
floor-length skirt, a torso, a neck, a head and two arms held out from the robe in an A pose, each a separate closed tube, with a Mixamo
skeleton squeezed into its top third as Tripo placed Elzon's. No Blender."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import clip_transfer as C
from lib import tripo_arm_seat as S
from lib import tripo_robe_rig as R
from tripo import robe_rig as robe_rig_cli

RING = 48  # as dense as a Tripo mesh around a body: a sparse ring leaves false gaps between its points
NECK_Y = 0.82
TIP = (0.36, 0.52)


def tube(centres: np.ndarray, radii: np.ndarray, depth: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    """A closed tube through `centres` (rings at right angles to the local direction), `depth` squeezing it front to back."""

    rings = []
    for i, centre in enumerate(centres):
        ahead = centres[min(i + 1, len(centres) - 1)] - centres[max(i - 1, 0)]
        ahead = ahead / np.linalg.norm(ahead)
        side = np.cross(ahead, [0.0, 0.0, 1.0])
        side = side / np.linalg.norm(side) if np.linalg.norm(side) > 1e-9 else np.array([1.0, 0.0, 0.0])
        front = np.cross(side, ahead)
        angles = np.linspace(0.0, 2 * np.pi, RING, endpoint=False) + 0.37 * i  # each ring turned: the points fill every angle
        rings.append(centre + radii[i] * (np.cos(angles)[:, None] * side + depth * np.sin(angles)[:, None] * front))
    points = np.concatenate(rings + [centres[:1], centres[-1:]])
    tris = []
    for r in range(len(rings) - 1):
        for k in range(RING):
            a, b, c, d = r * RING + k, r * RING + (k + 1) % RING, (r + 1) * RING + k, (r + 1) * RING + (k + 1) % RING
            tris += [(a, b, c), (b, d, c)]
    first, last = len(points) - 2, len(points) - 1
    for k in range(RING):
        tris += [(first, (k + 1) % RING, k), (last, (len(rings) - 1) * RING + k, (len(rings) - 1) * RING + (k + 1) % RING)]
    return points, np.array(tris, int)


def figure(arm_out: float = 1.0) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """(positions, triangles, the part of each vertex). `arm_out` < 1 brings the hands in against the robe."""

    parts = []
    y = np.linspace(0.0, 0.8, 160)
    parts.append(("body", *tube(np.stack([np.zeros_like(y), y, np.zeros_like(y)], 1), 0.22 - 0.1 * np.clip(y / 0.5, 0, 1), depth=0.8)))
    y = np.linspace(0.8, 0.86, 4)
    parts.append(("neck", *tube(np.stack([np.zeros_like(y), y, np.zeros_like(y)], 1), np.full(4, 0.05))))
    y = np.linspace(0.86, 1.0, 10)
    parts.append(("head", *tube(np.stack([np.zeros_like(y), y, np.zeros_like(y)], 1), 0.03 + 0.09 * np.sin(np.pi * (y - 0.86) / 0.14))))
    for sign in (1.0, -1.0):
        t = np.linspace(0.0, 1.0, 60)[:, None]
        start, end = np.array([sign * 0.12, 0.76, 0.0]), np.array([sign * TIP[0] * arm_out, TIP[1], 0.04])
        parts.append(("left arm" if sign > 0 else "right arm", *tube(start + t * (end - start), np.full(60, 0.035))))
    positions, triangles, labels, offset = [], [], [], 0
    for name, points, tris in parts:
        positions.append(points)
        triangles.append(tris + offset)
        labels += [name] * len(points)
        offset += len(points)
    return np.concatenate(positions), np.concatenate(triangles), labels


# Mixamo's joints Tripo gives a humanoid, misplaced as on Elzon: squeezed into the top third of the figure.
JOINTS: List[Tuple[str, Optional[str], Tuple[float, float, float]]] = [
    ("Hips", None, (0.0, 0.9, 0.0)), ("Spine", "Hips", (0.0, 0.92, 0.0)), ("Spine1", "Spine", (0.0, 0.95, 0.0)),
    ("Spine2", "Spine1", (0.0, 0.98, 0.0)), ("Neck", "Spine2", (0.0, 0.97, 0.0)), ("Head", "Neck", (0.0, 1.0, 0.0)),
    ("HeadTop_End", "Head", (0.0, 1.07, 0.0))]
for _side, _sign in (("Left", 1.0), ("Right", -1.0)):
    JOINTS += [(f"{_side}Shoulder", "Spine2", (_sign * 0.06, 0.97, 0.0)), (f"{_side}Arm", f"{_side}Shoulder", (_sign * 0.1, 0.94, 0.0)),
               (f"{_side}ForeArm", f"{_side}Arm", (_sign * 0.16, 0.8, 0.0)), (f"{_side}Hand", f"{_side}ForeArm", (_sign * 0.24, 0.78, 0.1)),
               (f"{_side}HandIndex1", f"{_side}Hand", (_sign * 0.3, 0.75, 0.15)),
               (f"{_side}UpLeg", "Hips", (_sign * 0.04, 0.88, 0.0)), (f"{_side}Leg", f"{_side}UpLeg", (_sign * 0.04, 0.78, 0.0)),
               (f"{_side}Foot", f"{_side}Leg", (_sign * 0.04, 0.66, 0.0)), (f"{_side}ToeBase", f"{_side}Foot", (_sign * 0.04, 0.62, 0.03)),
               (f"{_side}Toe_End", f"{_side}ToeBase", (_sign * 0.04, 0.62, 0.05))]


def write_glb(path: Path, positions: np.ndarray, triangles: np.ndarray) -> None:
    """A skinned GLB shaped like a Tripo export: every vertex on the toe joints and the hips, one clip that bends the spine."""

    names = [name for name, _p, _w in JOINTS]
    world = {name: np.array(at) for name, _p, at in JOINTS}
    nodes = [{"name": "Armature", "children": [1]}]
    for name, parent, _at in JOINTS:
        local = world[name] - (world[parent] if parent else 0.0)
        nodes.append({"name": f"mixamorig:{name}", "translation": local.tolist()})
    for k, (_name, parent, _at) in enumerate(JOINTS):
        if parent:
            nodes[1 + names.index(parent)].setdefault("children", []).append(1 + k)
    nodes.append({"name": "tripo_node_robe", "mesh": 0, "skin": 0})
    nodes[0]["children"].append(len(nodes) - 1)
    blob = bytearray()
    views, accessors = [], []

    def add(values: np.ndarray, kind: str, component: int, target: Optional[int] = None) -> int:
        data = np.ascontiguousarray(values).tobytes()
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(data), **({"target": target} if target else {})})
        blob.extend(data + b"\0" * (-len(data) % 4))
        item = {"bufferView": len(views) - 1, "componentType": component, "count": len(values), "type": kind}
        if kind == "VEC3" and component == 5126:
            item["min"], item["max"] = values.min(0).tolist(), values.max(0).tolist()
        accessors.append(item)
        return len(accessors) - 1

    toe = [names.index("LeftToeBase") if x > 0 else names.index("RightToeBase") for x in positions[:, 0]]
    joint_ids = np.array([[t, names.index("Hips"), 0, 0] for t in toe], np.uint16)
    weights = np.tile(np.array([0.8, 0.2, 0.0, 0.0], np.float32), (len(positions), 1))
    ibm = np.stack([np.linalg.inv(np.block([[np.eye(3), world[n][:, None]], [np.zeros((1, 3)), np.ones((1, 1))]])) for n in names])
    attributes = {"POSITION": add(positions.astype(np.float32), "VEC3", 5126, 34962), "JOINTS_0": add(joint_ids, "VEC4", 5123, 34962),
                  "WEIGHTS_0": add(weights, "VEC4", 5126, 34962)}
    indices = add(triangles.astype(np.uint32).ravel(), "SCALAR", 5125, 34963)
    skin = {"joints": [1 + k for k in range(len(names))], "inverseBindMatrices": add(ibm.transpose(0, 2, 1).reshape(-1, 16).astype(np.float32), "MAT4", 5126)}
    times = add(np.array([0.0, 0.5, 1.0], np.float32), "SCALAR", 5126)
    bend = add(np.array([[0, 0, 0, 1], [0.2588, 0, 0, 0.9659], [0, 0, 0, 1]], np.float32), "VEC4", 5126)
    animation = {"name": "idle", "samplers": [{"input": times, "output": bend}],
                 "channels": [{"sampler": 0, "target": {"node": 1 + names.index("Spine1"), "path": "rotation"}}]}
    doc = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [0]}], "nodes": nodes,
           "meshes": [{"name": "tripo_mesh_robe", "primitives": [{"attributes": attributes, "indices": indices}]}],
           "skins": [skin], "animations": [animation], "accessors": accessors, "bufferViews": views, "buffers": [{"byteLength": len(blob)}]}
    S.write_glb(path, doc, blob)


class Placement(unittest.TestCase):
    def setUp(self) -> None:
        self.positions, self.triangles, self.labels = figure()
        heads = {name: np.array(at) for name, _p, at in JOINTS}
        self.local = R.Frame(self.positions, heads).local(self.positions)

    def test_the_landmarks_follow_the_body_not_the_misplaced_joints(self) -> None:
        placed = R.place(self.local, self.triangles)
        heights = placed["heights"]
        self.assertAlmostEqual(heights["neck"], NECK_Y, delta=0.04)
        self.assertAlmostEqual(heights["hips"], R.HIP_SHARE * heights["neck"], places=6)
        self.assertLess(heights["knee"], heights["hips"])
        joints = placed["joints"]
        self.assertGreater(joints["LeftUpLeg"][0], 0)
        self.assertLess(joints["RightUpLeg"][0], 0)
        self.assertLess(joints["LeftFoot"][1], 0.06)
        for side, sign in (("Left", 1.0), ("Right", -1.0)):
            tip = placed["arms"][side]["tip"]
            self.assertAlmostEqual(tip[0] * sign, TIP[0], delta=0.04)
            self.assertAlmostEqual(tip[1], TIP[1], delta=0.04)
            self.assertGreater(joints[f"{side}Hand"][0] * sign, joints[f"{side}ForeArm"][0] * sign)

    def test_each_arm_takes_its_own_tube_and_nothing_of_the_robe(self) -> None:
        placed = R.place(self.local, self.triangles)
        labels = np.array(self.labels)
        for side, name in (("Left", "left arm"), ("Right", "right arm")):
            core = placed["arms"][side]["core"]
            self.assertGreater(core[labels == name].mean(), 0.9)
            self.assertFalse(core[np.isin(labels, ["body", "neck", "head"])].any())

    def test_arms_against_the_robe_are_refused(self) -> None:
        positions, triangles, _labels = figure(arm_out=0.3)
        heads = {name: np.array(at) for name, _p, at in JOINTS}
        local = R.Frame(positions, heads).local(positions)
        with self.assertRaises(R.SeatError):
            R.place(local, triangles)

    def test_a_hanging_sleeve_never_takes_the_hand_and_blends_wider_far_from_the_run(self) -> None:
        for share in np.linspace(0.0, 1.0, 21):
            for offset in (0.0, 0.1, 0.4):
                self.assertAlmostEqual(sum(R.sleeve_weights(float(share), offset).values()), 1.0, places=6)
        self.assertNotIn("Hand", R.sleeve_weights(0.95, R.HAND_OUTER + 0.01))
        self.assertEqual(R.sleeve_weights(0.95, 0.0), {"Hand": 1.0})
        near, far = R.sleeve_weights(0.55, 0.0), R.sleeve_weights(0.55, 0.4)
        self.assertEqual(near, {"ForeArm": 1.0})
        self.assertIn("Arm", far)


class WholeFile(unittest.TestCase):
    def test_the_joints_move_onto_the_body_and_the_skin_and_clip_follow(self) -> None:
        positions, triangles, labels = figure()
        with tempfile.TemporaryDirectory() as folder:
            source, out = Path(folder) / "rigged.glb", Path(folder) / "robe.glb"
            write_glb(source, positions, triangles)
            self.assertEqual(robe_rig_cli.main([str(source), "--out", str(out), "--json", str(Path(folder) / "r.json")]), 0)
            report = json.loads((Path(folder) / "r.json").read_text(encoding="utf-8"))
            self.assertEqual(report["clips"], ["idle"])
            doc, blob = S.read_glb(out)
            rig = S.load_rig(doc, blob)  # refuses a file whose nodes left the bind pose
            hips = rig["heads"]["Hips"][1]
            self.assertAlmostEqual(hips, R.HIP_SHARE * report["heights"]["neck"], delta=0.02)
            self.assertLess(rig["heads"]["LeftToeBase"][1], 0.05)
            self.assertTrue(np.allclose(rig["weights"].sum(axis=1), 1.0, atol=1e-5))
            arm = np.array(labels) == "left arm"
            dominant = rig["dominant"][arm]
            self.assertGreater(np.mean([name.startswith("Left") for name in dominant]), 0.9)  # its root blends into the body
            outer = rig["dominant"][arm & (positions[:, 0] > 0.2)]
            self.assertTrue(all(name in ("LeftArm", "LeftForeArm", "LeftHand") for name in outer), set(outer))
            skirt = rig["dominant"][(np.array(labels) == "body") & (positions[:, 1] < 0.3)]
            self.assertFalse(any("Toe" in name for name in skirt))
            self.assertIn("idle", C.Rig(out).clips())

    def test_an_unreadable_body_is_refused_without_an_output(self) -> None:
        positions, triangles, _labels = figure(arm_out=0.3)
        with tempfile.TemporaryDirectory() as folder:
            source, out = Path(folder) / "rigged.glb", Path(folder) / "robe.glb"
            write_glb(source, positions, triangles)
            self.assertEqual(robe_rig_cli.main([str(source), "--out", str(out)]), 2)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
