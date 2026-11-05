"""The unit-file checker, the PDX reader, the DXT5 writer and the unit-type catalog."""

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

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

import check_unit_files  # noqa: E402
from lib import model_dds, pdx_binary  # noqa: E402

LAND_ROLES = {"idle", "move", "attack", "defend", "retreat", "death"}


def _prop(name: str, kind: str, values: list) -> bytes:
    data = b"!" + struct.pack("<B", len(name)) + name.encode("latin-1") + kind.encode() + struct.pack("<i", len(values))
    if kind == "i":
        return data + struct.pack(f"<{len(values)}i", *values)
    if kind == "f":
        return data + struct.pack(f"<{len(values)}f", *values)
    for value in values:
        encoded = value.encode("latin-1") + b"\0"
        data += struct.pack("<i", len(encoded)) + encoded
    return data


def _obj(name: str, depth: int) -> bytes:
    return b"[" * depth + name.encode("latin-1") + b"\0"


def write_mesh(path: Path, bones: list[str], influences: int = 4, triangles: int = 2) -> None:
    data = b"@@b@" + _obj("object", 1) + _obj("unit_shape", 2) + _obj("mesh", 3)
    vertices = triangles + 2
    data += _prop("p", "f", [0.0] * (3 * vertices))
    data += _prop("tri", "i", [index for t in range(triangles) for index in (0, t + 1, t + 2)])
    data += _obj("material", 4) + _prop("shader", "s", ["PdxMeshAdvanced"]) + _prop("diff", "s", ["unit_diffuse.dds"])
    if bones:
        data += _obj("skin", 4) + _prop("bones", "i", [influences])
        data += _obj("skeleton", 3)
        for index, bone in enumerate(bones):
            data += _obj(bone, 4) + _prop("ix", "i", [index])
    path.write_bytes(data)


def write_anim(path: Path, joints: list[str], animated: bool = True, fps: float = 24.0, samples: int = 24) -> None:
    data = b"@@b@" + _obj("info", 1) + _prop("fps", "f", [fps]) + _prop("sa", "i", [samples]) + _prop("j", "i", [len(joints)])
    for joint in joints:
        data += _obj(joint, 2) + _prop("sa", "s", ["q" if animated else ""])
    path.write_bytes(data)


def write_bgra_dds(path: Path, image: Image.Image) -> None:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    bgra = np.asarray(rgba)[..., [2, 1, 0, 3]].tobytes()
    header = struct.pack(
        "<4sIIIIIII44sIIIIIIIIIIIII", b"DDS ", 124, 0x100F, height, width, width * 4, 0, 1, b"\0" * 44,
        32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000, 0x1000, 0, 0, 0, 0,
    )
    path.write_bytes(header + bgra)


class PdxReader(unittest.TestCase):
    def test_mesh_and_anim_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            mesh = Path(folder) / "u.mesh"
            write_mesh(mesh, ["Hips", "Spine"], triangles=3)
            summary = pdx_binary.summarize_mesh(pdx_binary.read(mesh))
            self.assertEqual(summary.bones, ["Hips", "Spine"])
            self.assertEqual(summary.triangles, 3)
            self.assertEqual(summary.streams[0].influences_per_vertex, 4)
            self.assertEqual(summary.streams[0].textures, {"diff": "unit_diffuse.dds"})
            anim = Path(folder) / "u_idle.anim"
            write_anim(anim, ["Hips", "Spine"], samples=48)
            parsed = pdx_binary.summarize_anim(pdx_binary.read(anim))
            self.assertEqual((parsed.fps, parsed.samples, parsed.joints), (24.0, 48, ["Hips", "Spine"]))
            self.assertAlmostEqual(parsed.seconds, 2.0)

    def test_rejects_other_files(self) -> None:
        with self.assertRaises(pdx_binary.PdxFormatError):
            pdx_binary.parse(b"DDS \0\0\0\0")
        with self.assertRaises(pdx_binary.PdxFormatError):
            pdx_binary.parse(b"@@b@!\x01p" + b"q")


class ModelDds(unittest.TestCase):
    def test_dxt5_has_a_full_chain_and_decodes_like_pillow(self) -> None:
        gradient = np.zeros((64, 32, 4), dtype=np.uint8)
        gradient[..., 0] = np.linspace(0, 255, 32, dtype=np.uint8)[None, :]
        gradient[..., 1] = np.linspace(255, 0, 64, dtype=np.uint8)[:, None]
        gradient[..., 3] = 200
        data = model_dds.dxt5_bytes(Image.fromarray(gradient, "RGBA"))
        header = model_dds.read_header(data)
        self.assertEqual((header["width"], header["height"], header["mips"], header["format"]), (32, 64, 7, "DXT5"))
        mine = model_dds.decode_top_level(data).astype(int)
        self.assertLess(np.abs(mine - gradient.astype(int)).max(), 24)
        theirs = np.asarray(Image.open(io.BytesIO(data)).convert("RGBA"), dtype=int)
        self.assertLessEqual(np.abs(mine - theirs).max(), 1)

    def test_refuses_sizes_that_are_not_powers_of_two(self) -> None:
        with self.assertRaises(model_dds.DdsError):
            model_dds.dxt5_bytes(Image.new("RGBA", (24, 16)))


class CheckUnitFiles(unittest.TestCase):
    def run_check(self, folder: Path, unit_type: str) -> list:
        types = check_unit_files.load_unit_types()
        profile = check_unit_files.load_profile(types[unit_type]["profile"])
        findings, _facts = check_unit_files.check_files(folder, types[unit_type], profile)
        return findings

    def test_a_complete_unit_passes(self) -> None:
        bones = ["Hips", "Spine", "Head"]
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            write_mesh(folder / "unit.mesh", bones)
            for role in LAND_ROLES:
                write_anim(folder / f"unit_{role}.anim", bones)
            self.assertEqual([item.rule for item in self.run_check(folder, "infantry_melee") if item.severity == "error"], [])

    def test_engine_limits_and_missing_roles(self) -> None:
        bones = [f"Bone_{index}" for index in range(51)]
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            write_mesh(folder / "unit.mesh", bones, influences=5)
            write_anim(folder / "unit_idle.anim", bones + ["Tail"])
            write_anim(folder / "unit_move.anim", bones, animated=False)
            rules = {item.rule for item in self.run_check(folder, "mount")}
        self.assertTrue({"UNIT-BONES", "UNIT-INFLUENCES", "UNIT-ANIM-JOINTS", "UNIT-ANIM-STATIC", "UNIT-ROLE-MISSING", "UNIT-NODE-MISSING"} <= rules)

    def test_texture_warnings_and_repair(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            write_mesh(folder / "unit.mesh", [])
            normal = Image.new("RGBA", (16, 16), (0, 128, 40, 128))
            write_bgra_dds(folder / "unit_normal.dds", normal)
            rules = {item.rule for item in check_unit_files.check_files(folder, None, None)[0]}
            self.assertTrue({"UNIT-DDS-MIPS", "UNIT-DDS-FORMAT", "UNIT-DDS-EMISSIVE"} <= rules)
            self.assertEqual(check_unit_files.repair_textures(folder), ["unit_normal.dds"])
            rules = {item.rule for item in check_unit_files.check_files(folder, None, None)[0]}
            self.assertFalse({"UNIT-DDS-MIPS", "UNIT-DDS-FORMAT", "UNIT-DDS-EMISSIVE"} & rules)
            self.assertEqual(check_unit_files.repair_textures(folder), [])

    def test_command_line_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(check_unit_files.main([name]), 1)


class UnitTypeCatalog(unittest.TestCase):
    def test_every_type_is_complete(self) -> None:
        types = check_unit_files.load_unit_types()
        profiles = json.loads((PIPELINE / "config" / "asset_profiles.json").read_text(encoding="utf-8"))["profiles"]
        for name, unit_type in types.items():
            with self.subTest(unit_type=name):
                self.assertIn(unit_type["profile"], profiles)
                self.assertEqual(set(unit_type["roles"]), LAND_ROLES)
                for role in unit_type["roles"].values():
                    self.assertTrue(role.get("meshy") or role.get("blender"))
                    for clip in role.get("meshy", []):
                        self.assertIsInstance(clip[0], int)
                        self.assertIsInstance(clip[1], str)
                    if unit_type["rig"] != "meshy_humanoid":
                        self.assertNotIn("meshy", role)
        self.assertIn("Saddle_Node", types["mount"]["required_nodes"])


if __name__ == "__main__":
    unittest.main()
