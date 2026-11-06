"""Body measurement and preset choice (measure_body.py), on box bodies written as small GLB files."""

from __future__ import annotations

import io
import json
import struct
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np

import measure_body
from lib import body_measure

HUMAN = {"legs": 2, "arms": 2, "wings": False, "tail": False, "extra_limbs": False, "vehicle": False, "rider_on_mount": False}
HORSE = {**HUMAN, "legs": 4, "arms": 0}


def box(x0, x1, y0, y1, z0, z1):
    points = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return points, [(a, b, c) for a, b, c, _d in quads] + [(a, c, d) for a, _b, c, d in quads]


def body(*boxes):
    positions, triangles = [], []
    for points, tris in (box(*b) for b in boxes):
        offset = len(positions)
        positions += points
        triangles += [(a + offset, b + offset, c + offset) for a, b, c in tris]
    return np.asarray(positions, dtype=np.float32), np.asarray(triangles, dtype=np.uint32)


# Y up, faces +Z, as Meshy delivers. Sizes in metres.
SOLDIER = body(
    (0.14, 0.26, 0.0, 0.9, -0.06, 0.06), (-0.26, -0.14, 0.0, 0.9, -0.06, 0.06),  # legs
    (-0.2, 0.2, 0.9, 1.5, -0.1, 0.1),  # torso
    (0.36, 0.44, 0.95, 1.45, -0.04, 0.04), (-0.44, -0.36, 0.95, 1.45, -0.04, 0.04),  # arms held clear, as in an A-pose
    (0.2, 0.44, 1.42, 1.5, -0.05, 0.05), (-0.44, -0.2, 1.42, 1.5, -0.05, 0.05),  # shoulders joining them to the torso
    (-0.1, 0.1, 1.5, 1.75, -0.1, 0.1),  # head
)
BRUTE = body(
    (0.14, 0.3, 0.0, 0.7, -0.08, 0.08), (-0.3, -0.14, 0.0, 0.7, -0.08, 0.08),
    (-0.42, 0.42, 0.7, 1.5, -0.2, 0.2),  # a wide torso
    (0.5, 0.62, 0.35, 1.45, -0.06, 0.06), (-0.62, -0.5, 0.35, 1.45, -0.06, 0.06),  # arms to the knees
    (0.42, 0.62, 1.37, 1.47, -0.07, 0.07), (-0.62, -0.42, 1.37, 1.47, -0.07, 0.07),  # shoulders
    (-0.12, 0.12, 1.5, 1.75, -0.1, 0.12),
)
HORSE_BODY = body(
    (-0.13, 0.03, 0.0, 0.62, 0.42, 0.58), (0.12, 0.28, 0.0, 0.62, 0.42, 0.58),  # front legs
    (-0.13, 0.03, 0.0, 0.62, -0.58, -0.42), (0.12, 0.28, 0.0, 0.62, -0.58, -0.42),  # hind legs
    (-0.15, 0.3, 0.6, 1.0, -0.6, 0.62),  # barrel
    (-0.05, 0.2, 0.9, 1.35, 0.55, 0.75),  # neck and head
)


def write_glb(path: Path, positions: np.ndarray, triangles: np.ndarray, scale: float = 1.0) -> None:
    position_bytes = positions.astype(np.float32).tobytes()
    index_bytes = triangles.astype(np.uint32).ravel().tobytes()
    gltf = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "scale": [scale, scale, scale]}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1, "mode": 4}]}],
        "buffers": [{"byteLength": len(position_bytes) + len(index_bytes)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(position_bytes)},
            {"buffer": 0, "byteOffset": len(position_bytes), "byteLength": len(index_bytes)},
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(positions), "type": "VEC3"},
            {"bufferView": 1, "componentType": 5125, "count": triangles.size, "type": "SCALAR"},
        ],
    }
    chunk = json.dumps(gltf).encode("utf-8")
    chunk += b" " * (-len(chunk) % 4)
    binary = position_bytes + index_bytes
    binary += b"\0" * (-len(binary) % 4)
    total = 12 + 8 + len(chunk) + 8 + len(binary)
    path.write_bytes(
        struct.pack("<4sII", b"glTF", 2, total)
        + struct.pack("<II", len(chunk), 0x4E4F534A) + chunk
        + struct.pack("<II", len(binary), 0x004E4942) + binary
    )


class Measures(unittest.TestCase):
    def measure(self, shape, scale=1.0):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "g.glb"
            write_glb(path, *shape, scale=scale)
            return body_measure.measure_file(path)

    def test_a_soldier_stands_on_two_feet(self) -> None:
        m = self.measure(SOLDIER)
        self.assertEqual(m.contacts, 2)
        self.assertGreaterEqual(m.upper_pieces, 3)  # torso and two free arms
        self.assertLess(m.torso_width, 0.4)

    def test_a_horse_stands_on_four_feet_and_is_long(self) -> None:
        m = self.measure(HORSE_BODY)
        self.assertEqual(m.contacts, 4)
        self.assertGreater(m.lower_length, 0.8)

    def test_scale_does_not_change_the_shares(self) -> None:
        small, large = self.measure(SOLDIER).as_dict(), self.measure(SOLDIER, scale=4.0).as_dict()
        for key in ("contacts", "legs", "torso_width", "lower_length", "centre_height"):
            self.assertAlmostEqual(small[key], large[key], places=2, msg=key)


class Presets(unittest.TestCase):
    def decide(self, shape, unit_type=None, anatomy=None, override=None, reason=""):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "g.glb"
            write_glb(path, *shape)
            return measure_body.measure_body(path, unit_type, dict(anatomy or {}), override, reason)

    def test_a_soldier_for_an_archer_passes_as_humanoid(self) -> None:
        verdict = self.decide(SOLDIER, "archer", HUMAN)
        self.assertEqual((verdict["verdict"], verdict["outputs"]["preset"]), ("pass", "humanoid"))
        self.assertIsNone(verdict["checklist"])

    def test_a_brute_for_a_heavy_brute_passes_as_large_biped(self) -> None:
        verdict = self.decide(BRUTE, "heavy_brute", HUMAN)
        self.assertEqual((verdict["verdict"], verdict["outputs"]["preset"]), ("pass", "large_biped"))

    def test_a_horse_for_a_mount_passes_as_quadruped(self) -> None:
        verdict = self.decide(HORSE_BODY, "mount", HORSE)
        self.assertEqual((verdict["verdict"], verdict["outputs"]["preset"]), ("pass", "quadruped"))

    def test_a_horse_for_an_archer_names_the_types_that_fit(self) -> None:
        verdict = self.decide(HORSE_BODY, "archer", HORSE)
        self.assertEqual(verdict["verdict"], "fail")
        self.assertEqual(verdict["findings"][0]["rule"], "BODY-UNIT-TYPE")
        self.assertEqual(verdict["outputs"]["unit_types_for_preset"], ["mount", "quadruped_beast"])

    def test_wings_fit_no_preset_and_escalate(self) -> None:
        verdict = self.decide(SOLDIER, "archer", {**HUMAN, "wings": True})
        self.assertEqual(verdict["verdict"], "escalate")
        self.assertIn("live-authoring.md", verdict["escalate"]["how"])

    def test_measured_legs_must_agree_with_the_declared_ones(self) -> None:
        verdict = self.decide(HORSE_BODY, "archer", HUMAN)
        self.assertEqual(verdict["verdict"], "escalate")

    def test_an_override_with_a_reason_passes_and_is_recorded(self) -> None:
        verdict = self.decide(SOLDIER, "archer", {**HUMAN, "wings": True}, "humanoid", "the wings are a stiff cape")
        self.assertEqual(verdict["verdict"], "pass")
        self.assertEqual(verdict["outputs"]["overridden"]["reason"], "the wings are a stiff cape")
        with self.assertRaises(SystemExit):
            self.decide(SOLDIER, "archer", HUMAN, "humanoid", "")

    def test_without_anatomy_the_confidence_is_capped_and_the_questions_asked(self) -> None:
        verdict = self.decide(SOLDIER, "archer")
        self.assertLessEqual(verdict["outputs"]["confidence"], 0.6)
        self.assertIn("anatomy", verdict["checklist"])


def with_extras(shape, *boxes):
    """A body plus extra separate boxes (plates, a prop, a stray shard)."""

    extra = body(*boxes)
    positions = np.concatenate([shape[0], extra[0]])
    triangles = np.concatenate([shape[1], extra[1] + len(shape[0])])
    return positions, triangles


class Parts(unittest.TestCase):
    def decide(self, shape):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "g.glb"
            write_glb(path, *shape)
            return measure_body.measure_body(path, "archer", dict(HUMAN), None, "")

    def test_plates_and_a_held_bow_do_not_change_the_measures(self) -> None:
        # The archer case: dozens of small plates on the body, a quiver and a long bow beside the hand.
        plates = [(-0.2 + 0.04 * (k % 10), -0.17 + 0.04 * (k % 10), 0.95 + 0.06 * (k // 10), 1.0 + 0.06 * (k // 10), 0.1, 0.13) for k in range(40)]
        bow = (0.445, 0.455, 0.3, 1.4, -0.005, 0.005)  # thin, reaches below the knee, touching the hand
        plain, armed = self.decide(SOLDIER), self.decide(with_extras(SOLDIER, *plates, bow))
        self.assertEqual(armed["verdict"], "pass", armed["findings"])
        self.assertEqual(armed["outputs"]["measured"]["parts"], 6 + 41 + 2)
        for key in ("contacts", "legs", "torso_width", "lower_length"):
            self.assertEqual(plain["outputs"]["measured"][key], armed["outputs"]["measured"][key], key)

    def test_a_shard_floating_apart_is_debris_before_the_rig(self) -> None:
        verdict = self.decide(with_extras(SOLDIER, (0.9, 0.95, 1.0, 1.05, 0.5, 0.55)))
        self.assertEqual(verdict["verdict"], "fail")
        self.assertEqual(verdict["findings"][0]["rule"], "BODY-DEBRIS")
        self.assertIn("loose_part_edits", verdict["next"][0])


class Job(unittest.TestCase):
    def test_a_job_folder_is_read_and_the_verdict_saved(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder) / "unit"
            (job / "provider" / "downloads").mkdir(parents=True)
            write_glb(job / "provider" / "downloads" / "generation_model.glb", *HORSE_BODY)
            (job / "job.yaml").write_text(json.dumps({"asset_slug": "warhorse", "unit_type": "mount", "anatomy": HORSE}), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                code = measure_body.main([str(job)])
            saved = json.loads((job / "evidence" / "body_verdict.json").read_text(encoding="utf-8"))
        self.assertEqual((code, saved["unit"], saved["outputs"]["preset"]), (0, "warhorse", "quadruped"))
        self.assertIn("--status warhorse", saved["next"][0])

    def test_every_unit_type_names_a_preset_with_its_rig(self) -> None:
        presets = measure_body.load_presets()["presets"]
        types = json.loads(measure_body.UNIT_TYPES.read_text(encoding="utf-8"))["types"]
        for name, entry in types.items():
            self.assertIn(entry.get("body"), presets, name)
            self.assertEqual(presets[entry["body"]]["blender"]["rig"], entry["rig"], name)


if __name__ == "__main__":
    unittest.main()
