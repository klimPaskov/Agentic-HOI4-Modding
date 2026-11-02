"""The maps bound to an exported model must belong to the model that supplies its geometry.

Meshy gives the generation model and the remesh/rig/animation models different
UV layouts. The humanoid route exports the animated GLB (remesh layout), so the
generation model's maps scramble its colours. These tests use tiny GLB and PNG
fixtures and a faked provider and Blender client; they need neither Blender nor
the network.
"""

from __future__ import annotations

import io
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import run_pilot
from lib import texture_lineage as lineage
from lib.texture_lineage import TextureLineageError

GEN_RGB, REMESH_RGB = (200, 30, 30), (30, 30, 200)


def png(rgb, size=(2, 2)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, rgb).save(buffer, format="PNG")
    return buffer.getvalue()


def jpeg(rgb) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), rgb).save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


def write_glb(path: Path, images: dict) -> None:
    """A GLB with one mesh whose material embeds `images` (role -> bytes)."""

    blobs, views, textures, material = [], [], [], {"pbrMetallicRoughness": {}}
    offset = 0
    keys = {"diffuse": ("baseColorTexture", True), "normal": ("normalTexture", False),
            "specular": ("metallicRoughnessTexture", True)}
    document_images = []
    for role, data in images.items():
        padded = data + b" " * (-len(data) % 4)
        views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(data)})
        document_images.append({"bufferView": len(views) - 1, "mimeType": "image/png"})
        textures.append({"source": len(document_images) - 1})
        key, in_pbr = keys[role]
        target = material["pbrMetallicRoughness"] if in_pbr else material
        target[key] = {"index": len(textures) - 1}
        blobs.append(padded)
        offset += len(padded)
    binary = b"".join(blobs)
    document = {
        "asset": {"version": "2.0"},
        "meshes": [{"primitives": [{"attributes": {}, "material": 0}]}],
        "materials": [material],
        "textures": textures,
        "images": document_images,
        "bufferViews": views,
        "buffers": [{"byteLength": len(binary)}],
    }
    text = json.dumps(document).encode("utf-8")
    text += b" " * (-len(text) % 4)
    body = struct.pack("<II", len(text), 0x4E4F534A) + text
    body += struct.pack("<II", len(binary), 0x004E4942) + binary
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body)


def maps(rgb) -> dict:
    return {"diffuse": png(rgb), "normal": png((128, 128, 255)), "specular": png((0, 90, 40))}


def write_textures(job: Path, model_rel: str, images: dict) -> None:
    folder = job / lineage.textures_dir_rel(model_rel)
    folder.mkdir(parents=True, exist_ok=True)
    for role, data in images.items():
        (folder / lineage.ROLE_FILES[role]).write_bytes(data)
    Image.open(io.BytesIO(images["specular"])).convert("L").save(folder / "roughness.png")
    Image.new("L", (2, 2), 40).save(folder / "metallic.png")


class LineageGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.job = Path(self._temp.name)
        self.downloads = "provider/downloads"

    def stage(self, name: str, rgb, *, textures=True) -> str:
        rel = f"{self.downloads}/{name}.glb"
        write_glb(self.job / rel, maps(rgb))
        if textures:
            write_textures(self.job, rel, maps(rgb))
        return rel

    def verify(self, geometry_rel: str, sources: dict) -> dict:
        return lineage.verify_texture_lineage(
            self.job, geometry_rel, sources, report_rel="blender/reports/texture_lineage_t.json"
        )

    def test_matching_remesh_maps_pass_and_both_hashes_are_recorded(self) -> None:
        self.stage("generation_model", GEN_RGB)
        remesh = self.stage("remesh_model", REMESH_RGB)
        animated = f"{self.downloads}/animation_attack_provider.glb"
        write_glb(self.job / animated, maps(REMESH_RGB))
        report = self.verify(animated, lineage.provider_texture_rels(remesh))
        diffuse = report["roles"]["diffuse"]
        self.assertEqual(report["status"], "pass")
        self.assertEqual(diffuse["matched_via"], "embedded_bytes")
        self.assertEqual(diffuse["bound_sha256"], diffuse["geometry_embedded_sha256"][0])
        saved = json.loads((self.job / "blender/reports/texture_lineage_t.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["roles"]["diffuse"]["bound_sha256"], diffuse["bound_sha256"])

    def test_generation_maps_with_remesh_geometry_fail_closed(self) -> None:
        generation = self.stage("generation_model", GEN_RGB)
        self.stage("remesh_model", REMESH_RGB)
        animated = f"{self.downloads}/animation_attack_provider.glb"
        write_glb(self.job / animated, maps(REMESH_RGB))
        with self.assertRaisesRegex(TextureLineageError, "diffuse.*not the image embedded"):
            self.verify(animated, lineage.provider_texture_rels(generation))
        saved = json.loads((self.job / "blender/reports/texture_lineage_t.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "fail")

    def test_one_wrong_secondary_map_also_fails(self) -> None:
        remesh = self.stage("remesh_model", REMESH_RGB)
        animated = f"{self.downloads}/animation_attack_provider.glb"
        write_glb(self.job / animated, {**maps(REMESH_RGB), "normal": png((1, 2, 3))})
        with self.assertRaisesRegex(TextureLineageError, "normal"):
            self.verify(animated, lineage.provider_texture_rels(remesh))

    def test_downloaded_with_model_proves_a_generation_glb_that_embeds_jpeg(self) -> None:
        rel = f"{self.downloads}/generation_model.glb"
        write_glb(self.job / rel, {**maps(GEN_RGB), "diffuse": jpeg(GEN_RGB)})
        write_textures(self.job, rel, maps(GEN_RGB))
        report = self.verify(rel, lineage.provider_texture_rels(rel))
        self.assertEqual(report["roles"]["diffuse"]["matched_via"], "downloaded_with_model")

    def test_a_model_with_no_proof_for_diffuse_fails_closed(self) -> None:
        remesh = self.stage("remesh_model", REMESH_RGB)
        bare = f"{self.downloads}/bare.glb"
        write_glb(self.job / bare, {})
        with self.assertRaisesRegex(TextureLineageError, "embeds no baseColor"):
            self.verify(bare, lineage.provider_texture_rels(remesh))

    def test_missing_geometry_or_source_raises(self) -> None:
        with self.assertRaises(TextureLineageError):
            self.verify("provider/downloads/nope.glb", {"diffuse": "x.png"})
        remesh = self.stage("remesh_model", REMESH_RGB)
        with self.assertRaises(TextureLineageError):
            self.verify(remesh, {"diffuse": "provider/downloads/gone.png"})

    def test_dds_header_reports_the_mip_count(self) -> None:
        def dds(mips: int) -> bytes:
            flags = 0x1 | 0x2 | 0x4 | 0x1000 | (0x20000 if mips else 0)
            header = struct.pack("<II", 124, flags) + struct.pack("<II", 16, 16) + struct.pack("<II", 64, 0)
            header += struct.pack("<I", mips) + b"\x00" * 44
            header += struct.pack("<II4sIIIII", 32, 0x41, b"\x00" * 4, 32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000)
            header += struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)
            return b"DDS " + header

        path = self.job / "t.dds"
        path.write_bytes(dds(0))
        flat = lineage.dds_header(path)
        self.assertEqual((flat["mip_count"], flat["mip_chain_present"]), (1, False))
        path.write_bytes(dds(5))
        full = lineage.dds_header(path)
        self.assertEqual((full["mip_count"], full["mip_chain_present"], full["expected_full_chain_mips"]), (5, True, 5))
        path.write_bytes(b"not a dds" * 20)
        with self.assertRaises(TextureLineageError):
            lineage.dds_header(path)


class Stop(Exception):
    """Raised by the fake Blender client once prepare_candidate has been captured."""


class HumanoidRouteTests(unittest.TestCase):
    """Drive continue_humanoid up to the first prepare_candidate call."""

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.job = Path(self._temp.name).resolve()
        for folder in ("provider/downloads", "blender/reports"):
            (self.job / folder).mkdir(parents=True)
        generation = "provider/downloads/generation_model.glb"
        write_glb(self.job / generation, maps(GEN_RGB))
        write_textures(self.job, generation, maps(GEN_RGB))
        self.animated_images = maps(REMESH_RGB)
        self.captured = {}

    def run_route(self, triangles: int) -> None:
        (self.job / "blender/reports/unit_candidate_prepare.json").write_text(
            json.dumps({"imported_geometry": {"triangles": triangles}}), encoding="utf-8"
        )
        job = self.job

        def fake_download(client, root, *, filename, **kwargs):
            rel = f"provider/downloads/{filename}"
            if filename.endswith("remesh_model.glb"):
                write_glb(job / rel, maps(REMESH_RGB))
                write_textures(job, rel, maps(REMESH_RGB))
            elif filename.endswith("_provider.glb"):
                write_glb(job / rel, self.animated_images)
            return {"file": {"relative_path": rel}}

        def fake_prepare(*args, **kwargs):
            self.captured = kwargs
            raise Stop

        blender = mock.Mock()
        blender.prepare_candidate.side_effect = fake_prepare
        spec = {
            "asset_id": "hoi4.model.job.unit",
            "asset_kind": "humanoid",
            "profile": "humanoid_unit",
            "runtime_stem": "unit",
            "target_height_m": 1.8,
            "rig_source_target_polycount": 20000,
            "rig_estimate_credits": 5,
            "animation_estimate_credits": 3,
            "rig_input_mode": "input_task_id",
            "required_actions": [{"role": "attack", "provider_action_id": 4}],
            "texture_source_rels": {
                "diffuse": "provider/downloads/generation_model_textures/base_color.png",
                "normal": "provider/downloads/generation_model_textures/normal.png",
                "specular": "provider/downloads/generation_model_textures/metallic_roughness.png",
            },
        }
        with (
            mock.patch.object(run_pilot, "ensure_job_layout", return_value=job),
            mock.patch.object(run_pilot, "resolve_job_root", return_value=job),
            mock.patch.object(run_pilot, "MeshyClient"),
            mock.patch.object(run_pilot, "BlenderAdapterClient", return_value=blender),
            mock.patch.object(run_pilot, "stage_vanilla_reference", return_value=None),
            mock.patch.object(run_pilot, "existing_task", return_value={"task_id": "gen"}),
            mock.patch.object(run_pilot, "prepare_spec", return_value={"remesh_estimate_credits": 5}),
            mock.patch.object(run_pilot, "provider_task", return_value="task"),
            mock.patch.object(run_pilot, "paid_request"),
            mock.patch.object(run_pilot, "download_once", side_effect=fake_download),
        ):
            self.spec = spec
            run_pilot.continue_humanoid(spec)

    def test_remeshed_humanoid_binds_the_remesh_textures(self) -> None:
        with self.assertRaises(Stop):
            self.run_route(triangles=900000)
        sources = self.captured["texture_source_rels"]
        for role in ("diffuse", "normal"):
            self.assertIn("/remesh_model_textures/", sources[role])
            self.assertNotIn("generation", sources[role])
        self.assertEqual(sources["specular"], "provider/downloads/remesh_model_textures/roughness.png")
        self.assertEqual(
            self.spec["_provider_texture_source_rels"]["specular"],
            "provider/downloads/remesh_model_textures/metallic_roughness.png",
        )
        report = json.loads(
            (self.job / "blender/reports/texture_lineage_animation_attack_provider.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["status"], "pass")

    def test_generation_maps_are_never_paired_with_remesh_geometry(self) -> None:
        # The animated GLB carries the remesh layout, so a generation pairing
        # cannot get past the gate even if something selects those maps.
        real = run_pilot.select_geometry_textures

        def force_generation(job, spec, model_rel):
            return real(job, spec, "provider/downloads/generation_model.glb")

        with mock.patch.object(run_pilot, "select_geometry_textures", side_effect=force_generation):
            with self.assertRaisesRegex(TextureLineageError, "not the image embedded"):
                self.run_route(triangles=900000)
        self.assertEqual(self.captured, {})

    def test_a_mismatched_animated_model_stops_before_export(self) -> None:
        self.animated_images = maps(GEN_RGB)  # animation built on a different layout
        with self.assertRaisesRegex(TextureLineageError, "diffuse"):
            self.run_route(triangles=900000)
        self.assertEqual(self.captured, {})

    def test_unremeshed_humanoid_keeps_the_generation_textures(self) -> None:
        self.animated_images = maps(GEN_RGB)
        with self.assertRaises(Stop):
            self.run_route(triangles=100000)
        self.assertIn("/generation_model_textures/", self.captured["texture_source_rels"]["diffuse"])


class RebuildTests(unittest.TestCase):
    """Repair a finished job's DDS from files on disk: no Meshy call, no Blender."""

    def rebuild(self, animated_rgb, remeshed=True):
        with tempfile.TemporaryDirectory() as temporary:
            job = Path(temporary).resolve()
            write_glb(job / "provider/downloads/generation_model.glb", maps(GEN_RGB))
            write_textures(job, "provider/downloads/generation_model.glb", maps(GEN_RGB))
            write_glb(job / "provider/downloads/remesh_model.glb", maps(REMESH_RGB))
            write_textures(job, "provider/downloads/remesh_model.glb", maps(REMESH_RGB))
            write_glb(job / "provider/downloads/animation_attack_provider.glb", maps(animated_rgb))
            (job / "blender/reports").mkdir(parents=True)
            (job / "blender/reports/textures_dds.json").write_text('{"conversions": []}', encoding="utf-8")
            spec = {"asset_id": "hoi4.model.job.unit", "asset_kind": "humanoid"}
            captured = {}

            def finalize(root, current, textures):
                captured["sources"] = dict(current["_provider_texture_source_rels"])
                return {"done": True}

            task = {"status": "SUCCEEDED"} if remeshed else None
            with (
                mock.patch.object(run_pilot, "prepare_spec"),
                mock.patch.object(run_pilot, "ensure_job_layout", return_value=job),
                mock.patch.object(run_pilot, "resolve_job_root", return_value=job),
                mock.patch.object(run_pilot, "existing_task", return_value=task),
                mock.patch.object(run_pilot, "finalize_pdx_runtime_textures", side_effect=finalize),
            ):
                run_pilot.rebuild_runtime_textures(spec)
            return captured

    def test_rebuild_uses_the_remesh_maps_of_the_exported_model(self) -> None:
        sources = self.rebuild(REMESH_RGB)["sources"]
        self.assertEqual(sources["diffuse"], "provider/downloads/remesh_model_textures/base_color.png")

    def test_rebuild_refuses_maps_that_do_not_match_the_exported_model(self) -> None:
        with self.assertRaises(TextureLineageError):
            self.rebuild(GEN_RGB)


class FallbackRemovedTests(unittest.TestCase):
    def test_runtime_finalization_has_no_generation_fallback(self) -> None:
        source = Path(run_pilot.__file__).read_text(encoding="utf-8")
        body = source.split("def finalize_pdx_runtime_textures", 1)[1].split("\ndef run_candidate", 1)[0]
        self.assertNotIn("generation_model_textures", body)

    def test_missing_specular_stays_in_the_bound_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            job = Path(temporary)
            generation = job / "provider/downloads/generation_model_textures"
            generation.mkdir(parents=True)
            Image.new("RGB", (2, 2)).save(generation / "metallic_roughness.png")
            (job / "provider/downloads/remesh_model_textures").mkdir()
            spec = {
                "asset_kind": "humanoid",
                "texture_source_rels": {"specular": "provider/downloads/remesh_model_textures/roughness.png"},
            }
            with self.assertRaises(FileNotFoundError):
                run_pilot.finalize_pdx_runtime_textures(job, spec, {})

    def test_preparing_twice_keeps_the_provider_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            job = Path(temporary)
            folder = job / "provider/downloads/remesh_model_textures"
            folder.mkdir(parents=True)
            for name in ("base_color.png", "normal.png", "metallic_roughness.png", "metallic.png", "roughness.png"):
                Image.new("RGBA", (2, 2), (10, 90, 40, 255)).save(folder / name)
            spec = {"texture_source_rels": lineage.provider_texture_rels("provider/downloads/remesh_model.glb")}
            run_pilot.prepare_pilot_texture_sources(job, spec)
            run_pilot.prepare_pilot_texture_sources(job, spec)
            self.assertTrue(spec["_provider_texture_source_rels"]["specular"].endswith("metallic_roughness.png"))
            self.assertTrue(spec["texture_source_rels"]["specular"].endswith("roughness.png"))


if __name__ == "__main__":
    unittest.main()
