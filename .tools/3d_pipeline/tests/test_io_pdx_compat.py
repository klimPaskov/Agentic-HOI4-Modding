from __future__ import annotations

import hashlib
import io
import os
import sys
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

import bootstrap_3d_workflow as bootstrap  # noqa: E402
from build_io_pdx_py313_compat import (  # noqa: E402
    build_compatibility_archive as bootstrap_build_compatibility_archive,
    compatibility_archive_bytes,
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def source_archive(overrides: dict[str, bytes] | None = None) -> bytes:
    files = {
        "io_pdx_mesh/blender_manifest.toml": b'version = "0.91.0"\n',
        "io_pdx_mesh/__init__.py": b"from imp import reload\n",
        "io_pdx_mesh/pdx_maya/maya_ui.py": b"from imp import reload\r\n",
        "io_pdx_mesh/pdx_blender/blender_import_export.py": (
            b'    new_shader.shadow_method = "CLIP"\n'
            b"\n"
            b"                ctx = bpy.context.copy()\n"
            b'                ctx["active_object"] = created[0]\n'
            b'                ctx["selected_editable_objects"] = created\n'
            b"                bpy.ops.object.join(ctx)\n"
            b"                ctx.clear()\n"
        ),
        "io_pdx_mesh/untouched.txt": b"preserve this entry\n",
    }
    files.update(overrides or {})
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return output.getvalue()


def compatibility_resolution(source: bytes) -> dict:
    derived = compatibility_archive_bytes(source)
    with zipfile.ZipFile(io.BytesIO(derived)) as archive:
        patch_hashes = {
            relative: sha256(archive.read(f"io_pdx_mesh/{relative}"))
            for relative in (
                "__init__.py",
                "pdx_maya/maya_ui.py",
                "pdx_blender/blender_import_export.py",
            )
        }
    source_hash = sha256(source)
    return {
        "release": "0.91",
        "download_url": "https://example.invalid/io_pdx_mesh.zip",
        "asset_name": "io_pdx_mesh.zip",
        "sha256": source_hash,
        "size": len(source),
        "compatibility": {
            "source_sha256": source_hash,
            "source_size": len(source),
            "blender_minors": ["5.2"],
            "archive_sha256": sha256(derived),
            "archive_size": len(derived),
            "installed_patch_files_sha256": patch_hashes,
        },
    }


class IoPdxCompatibilityTests(unittest.TestCase):
    def test_checked_in_io_pdx_lock_selects_blender_52_only(self) -> None:
        resolution = bootstrap.resolve_io_pdx_mesh()
        self.assertEqual(resolution["release"], "0.91")
        self.assertEqual(resolution["compatibility"]["blender_minors"], ["5.2"])

    def test_compatibility_archive_changes_only_the_locked_sites(self) -> None:
        source = source_archive()
        derived = compatibility_archive_bytes(source)
        with zipfile.ZipFile(io.BytesIO(source)) as before, zipfile.ZipFile(io.BytesIO(derived)) as after:
            self.assertEqual(before.namelist(), after.namelist())
            self.assertEqual(after.read("io_pdx_mesh/untouched.txt"), b"preserve this entry\n")
            self.assertEqual(after.read("io_pdx_mesh/__init__.py"), b"from importlib import reload\n")
            self.assertEqual(after.read("io_pdx_mesh/pdx_maya/maya_ui.py"), b"from importlib import reload\r\n")
            blender = after.read("io_pdx_mesh/pdx_blender/blender_import_export.py")
            self.assertIn(b"bpy.context.temp_override(", blender)
            self.assertIn(b"bpy.ops.object.join()", blender)
            self.assertNotIn(b"bpy.ops.object.join(ctx)", blender)
        self.assertNotEqual(sha256(source), sha256(derived))

    def test_compatibility_archive_rejects_missing_or_ambiguous_anchors(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unexpected compatibility anchor"):
            compatibility_archive_bytes(
                source_archive({"io_pdx_mesh/__init__.py": b"from importlib import reload\n"})
            )
        with self.assertRaisesRegex(ValueError, "Unexpected compatibility anchor"):
            compatibility_archive_bytes(
                source_archive({"io_pdx_mesh/__init__.py": b"from imp import reload\nfrom imp import reload\n"})
            )

    def test_bootstrap_selects_only_the_matching_locked_minor(self) -> None:
        source = source_archive()
        resolution = compatibility_resolution(source)
        for minor, expected in (("4.5", False), ("5.2", True)):
            selected = bootstrap.resolve_io_pdx_archive(source, minor, resolution)
            self.assertEqual(selected["compatibility_applied"], expected)
            if expected:
                self.assertEqual(selected["install_archive_sha256"], resolution["compatibility"]["archive_sha256"])
                self.assertNotEqual(selected["install_archive"], source)
            else:
                self.assertEqual(selected["install_archive"], source)

    def test_bootstrap_rejects_unsafe_compatibility_file_evidence(self) -> None:
        source = source_archive()
        resolution = compatibility_resolution(source)
        resolution["compatibility"]["installed_patch_files_sha256"]["../outside.txt"] = "0" * 64
        with self.assertRaisesRegex(bootstrap.SetupError, "unexpected installed-file set"):
            bootstrap.resolve_io_pdx_archive(source, "5.2", resolution)

        resolution = compatibility_resolution(source)
        resolution["compatibility"]["installed_patch_files_sha256"]["__init__.py"] = "invalid"
        with self.assertRaisesRegex(bootstrap.SetupError, "unsafe path or file hash"):
            bootstrap.resolve_io_pdx_archive(source, "5.2", resolution)

    def test_builder_never_overwrites_upstream_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = Path(temporary) / "upstream.zip"
            source_path.write_bytes(source_archive())
            with self.assertRaisesRegex(ValueError, "must not overwrite the upstream archive"):
                bootstrap_build_compatibility_archive(source_path, source_path, {})

    def test_bootstrap_reinstalls_same_version_when_compatibility_hashes_differ(self) -> None:
        source = source_archive()
        resolution = compatibility_resolution(source)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            appdata = root / "appdata"
            install = appdata / "Blender Foundation/Blender/5.2/extensions/user_default/io_pdx_mesh"
            install.mkdir(parents=True)
            # A same-version upstream install must not satisfy the 5.2 patched-file contract.
            with zipfile.ZipFile(io.BytesIO(source)) as archive:
                for member in archive.namelist():
                    if member.startswith("io_pdx_mesh/"):
                        relative = Path(*Path(member).parts[1:])
                        destination = install / relative
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_bytes(archive.read(member))
            safe_extract_calls = []
            original_safe_extract = bootstrap.safe_extract

            def record_extract(archive: zipfile.ZipFile, destination: Path) -> None:
                safe_extract_calls.append(destination)
                original_safe_extract(archive, destination)

            def fake_download(_url: str, destination: Path) -> None:
                destination.write_bytes(source)

            with patch.dict(os.environ, {"APPDATA": str(appdata)}), patch.object(
                bootstrap, "run", return_value="Blender 5.2.2"
            ), patch.object(bootstrap, "download", side_effect=fake_download), patch.object(
                bootstrap, "safe_extract", side_effect=record_extract
            ):
                result = bootstrap.ensure_io_pdx_mesh(root / "pipeline", Path("blender.exe"), resolution)

            self.assertTrue(result["compatibility_applied"])
            self.assertEqual(result["installed_archive_sha256"], resolution["compatibility"]["archive_sha256"])
            self.assertEqual(len(safe_extract_calls), 1)
            for relative, expected_hash in resolution["compatibility"]["installed_patch_files_sha256"].items():
                installed_file = install / Path(*Path(relative).parts)
                self.assertEqual(sha256(installed_file.read_bytes()), expected_hash)


if __name__ == "__main__":
    unittest.main()
