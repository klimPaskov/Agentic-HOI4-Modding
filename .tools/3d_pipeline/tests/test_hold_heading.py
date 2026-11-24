"""lib/hold_heading.py: a clip's turn about the up axis is held within a limit, and the rest of the motion stays."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import rig_glb as RG
from lib import hold_heading as H
from lib.clip_transfer import quat_to_matrix
from lib.tripo_arm_seat import get, put, read_glb, write_glb


def yaw_quat(degrees: float) -> list:
    half = math.radians(degrees) / 2
    return [0.0, math.sin(half), 0.0, math.cos(half)]


def turning_rig(path: Path, keys: list) -> None:
    """The test rig with its `walk` clip's lean moved onto the hips and replaced by `keys`: a clip that turns the body."""

    built = RG.write_rig_glb(path)
    doc, blob = read_glb(path)
    walk = next(a for a in doc["animations"] if a["name"] == "walk")
    channel = next(c for c in walk["channels"] if c["target"]["path"] == "rotation")
    channel["target"]["node"] = built["nodes"]["mixamorig:Hips"]
    put(doc, blob, walk["samplers"][channel["sampler"]]["output"], np.array(keys, np.float32))
    write_glb(path, doc, blob)


def add_rotation(doc: dict, blob: bytearray, animation: dict, node: int, keys: list) -> None:
    """Key `node`'s rotation in `animation` at the clip's three key times."""

    times = animation["samplers"][0]["input"]
    doc["bufferViews"].append({"buffer": 0, "byteOffset": len(blob), "byteLength": 16 * len(keys)})
    doc["accessors"].append({"bufferView": len(doc["bufferViews"]) - 1, "componentType": 5126, "count": len(keys), "type": "VEC4"})
    blob.extend(np.array(keys, np.float32).tobytes())
    doc["buffers"][0]["byteLength"] = len(blob)
    animation["samplers"].append({"input": times, "output": len(doc["accessors"]) - 1})
    animation["channels"].append({"sampler": len(animation["samplers"]) - 1, "target": {"node": node, "path": "rotation"}})


class HoldHeading(unittest.TestCase):
    def setUp(self) -> None:
        self.folder = Path(tempfile.mkdtemp(prefix="hh_"))

    def test_a_clip_that_turns_away_is_held_within_the_limit(self) -> None:
        source, out = self.folder / "in.glb", self.folder / "out.glb"
        turning_rig(source, [yaw_quat(0), yaw_quat(95), yaw_quat(190)])
        report = H.hold(source, out, ["walk"], 20.0)
        self.assertGreater(report[0]["turned"], 180.0)
        doc, blob = read_glb(out)
        walk = next(a for a in doc["animations"] if a["name"] == "walk")
        channel = next(c for c in walk["channels"] if c["target"]["path"] == "rotation")
        quats = get(doc, blob, walk["samplers"][channel["sampler"]]["output"]).astype(float)
        turn = H.headings(quats, np.eye(3))
        self.assertLessEqual(float(np.abs(turn - turn[0]).max()), 20.0 + 1e-3)

    def test_a_lean_without_a_turn_is_kept(self) -> None:
        source, out = self.folder / "in.glb", self.folder / "out.glb"
        lean = [[0.0, 0.0, 0.0, 1.0], [0.0871557, 0.0, 0.0, 0.9961947], [0.0, 0.0, 0.0, 1.0]]
        turning_rig(source, lean)
        H.hold(source, out, ["walk"], 20.0)
        doc, blob = read_glb(out)
        walk = next(a for a in doc["animations"] if a["name"] == "walk")
        channel = next(c for c in walk["channels"] if c["target"]["path"] == "rotation")
        quats = get(doc, blob, walk["samplers"][channel["sampler"]]["output"]).astype(float)
        np.testing.assert_allclose(np.abs(quats), np.abs(np.array(lean)), atol=1e-5)

    def test_a_turn_and_a_lean_keep_the_lean(self) -> None:
        """Hunched and turning: the yaw beyond the limit goes, the forward bend stays."""

        lean = np.array([0.0871557, 0.0, 0.0, 0.9961947])

        def compose(a, b):
            x1, y1, z1, w1 = a
            x2, y2, z2, w2 = b
            return [w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2, w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                    w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2, w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2]

        keys = [compose(yaw_quat(d), lean) for d in (0, 90, 180)]
        source, out = self.folder / "in.glb", self.folder / "out.glb"
        turning_rig(source, keys)
        H.hold(source, out, ["wal"], 0.0)
        doc, blob = read_glb(out)
        walk = next(a for a in doc["animations"] if a["name"] == "walk")
        channel = next(c for c in walk["channels"] if c["target"]["path"] == "rotation")
        quats = get(doc, blob, walk["samplers"][channel["sampler"]]["output"]).astype(float)
        for q in quats:
            np.testing.assert_allclose(np.abs(q), np.abs(lean), atol=1e-5)

    def test_with_the_spine_the_shoulders_do_not_lead_the_held_hips(self) -> None:
        """The hips turn 190 degrees and the spine 30 more against them: held with the spine, the spine's world heading stays too."""

        source, out = self.folder / "in.glb", self.folder / "out.glb"
        built = RG.write_rig_glb(source)
        doc, blob = read_glb(source)
        walk = next(a for a in doc["animations"] if a["name"] == "walk")
        spine = built["nodes"]["mixamorig:Spine"]
        lean = next(c for c in walk["channels"] if c["target"]["path"] == "rotation")
        put(doc, blob, walk["samplers"][lean["sampler"]]["output"], np.array([yaw_quat(0), yaw_quat(15), yaw_quat(30)], np.float32))
        add_rotation(doc, blob, walk, built["nodes"]["mixamorig:Hips"], [yaw_quat(0), yaw_quat(95), yaw_quat(190)])
        write_glb(source, doc, blob)
        report = H.hold(source, out, ["walk"], 0.0, spine=True)
        self.assertEqual(set(report[0]["joints"]), {"Hips", "Spine"})
        self.assertAlmostEqual(report[0]["joints"]["Spine"], 30.0, places=0)  # read after the hips are held
        doc, blob = read_glb(out)
        walk = next(a for a in doc["animations"] if a["name"] == "walk")
        quats = {c["target"]["node"]: get(doc, blob, walk["samplers"][c["sampler"]]["output"]).astype(float) for c in walk["channels"] if c["target"]["path"] == "rotation"}
        for hips, local in zip(quats[built["nodes"]["mixamorig:Hips"]], quats[spine]):
            forward = quat_to_matrix(hips) @ quat_to_matrix(local) @ np.array([0.0, 0.0, 1.0])
            self.assertAlmostEqual(float(np.degrees(np.arctan2(forward[0], forward[2]))), 0.0, places=3)

    def test_with_the_spine_the_line_between_the_upper_arms_keeps_its_heading(self) -> None:
        """A collar bone swings 25 degrees with the spine still: the top spine bone turns back so the shoulder line keeps its heading."""

        saved = list(RG.CHAIN)
        self.addCleanup(lambda: RG.CHAIN.__setitem__(slice(None), saved))
        RG.CHAIN[:] = saved + [
            ("mixamorig:LeftShoulder", 1, (0.1, 0.25, 0.0)),
            ("mixamorig:LeftArm", len(saved), (0.1, 0.0, 0.0)),
            ("mixamorig:RightArm", 1, (-0.2, 0.25, 0.0)),
        ]
        source, out = self.folder / "in.glb", self.folder / "out.glb"
        built = RG.write_rig_glb(source)
        doc, blob = read_glb(source)
        walk = next(a for a in doc["animations"] if a["name"] == "walk")
        add_rotation(doc, blob, walk, built["nodes"]["mixamorig:LeftShoulder"], [yaw_quat(0), yaw_quat(25), yaw_quat(0)])
        write_glb(source, doc, blob)
        report = H.hold(source, out, ["walk"], 0.0, spine=True)
        self.assertGreater(report[0]["shoulder_line"], 5.0)
        doc, blob = read_glb(out)
        names = {doc["nodes"][i]["name"]: i for i in range(len(doc["nodes"]))}
        walk = next(a for a in doc["animations"] if a["name"] == "walk")
        channels = {}
        for channel in walk["channels"]:
            sampler = walk["samplers"][channel["sampler"]]
            channels.setdefault(channel["target"]["node"], {})[channel["target"]["path"]] = (get(doc, blob, sampler["input"]).astype(float).ravel(), get(doc, blob, sampler["output"]).astype(float))
        parent_of = {child: i for i, node in enumerate(doc["nodes"]) for child in node.get("children", [])}
        lines = []
        for t in (0.0, 0.5, 1.0):
            posed = H._world_positions(doc, parent_of, channels, t)
            v = posed[names["mixamorig:RightArm"]] - posed[names["mixamorig:LeftArm"]]
            lines.append(math.degrees(math.atan2(v[0], v[2])))
        self.assertAlmostEqual(lines[1], lines[0], places=3)

    def test_an_unknown_clip_is_refused(self) -> None:
        source = self.folder / "in.glb"
        RG.write_rig_glb(source)
        with self.assertRaises(H.HeadingError):
            H.hold(source, self.folder / "out.glb", ["fly"], 20.0)


if __name__ == "__main__":
    unittest.main()
