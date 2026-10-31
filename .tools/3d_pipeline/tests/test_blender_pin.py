"""Blender is pinned to the lock's supported minors, and io_pdx_mesh is hash-checked on each.

Everything here runs on fake directory trees and a fake `blender --version`;
no Blender, network or add-on installation is involved.
"""

from __future__ import annotations

import ast
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_ROOT = PIPELINE_ROOT / "adapter"
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import bootstrap_3d_workflow as bootstrap
from test_io_pdx_compat import compatibility_resolution, sha256, source_archive


def load_lock() -> dict:
    return json.loads((PIPELINE_ROOT / "config/dependencies.lock.json").read_text(encoding="utf-8"))


class SupportedMinorLockTests(unittest.TestCase):
    def pipeline_with_lock(self, lock: dict) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "config").mkdir()
        (root / "config/dependencies.lock.json").write_text(json.dumps(lock), encoding="utf-8")
        return root

    def test_checked_in_lock_supports_exactly_blender_51_and_52(self) -> None:
        self.assertEqual(bootstrap.supported_blender_minors(), ["5.1", "5.2"])

    def test_checked_in_lock_covers_every_supported_minor_with_the_compat_archive(self) -> None:
        lock = load_lock()["compatibility"]
        self.assertEqual(set(lock["blender"]["supported_minors"]), set(lock["io_pdx_mesh"]["blender_minors"]))
        self.assertEqual(
            set(bootstrap.resolve_io_pdx_mesh()["compatibility"]["blender_minors"]),
            set(bootstrap.supported_blender_minors()),
        )

    def test_minors_are_returned_oldest_first_whatever_order_the_lock_uses(self) -> None:
        lock = load_lock()
        lock["compatibility"]["blender"]["supported_minors"] = ["5.2", "5.1", "5.10"]
        self.assertEqual(bootstrap.supported_blender_minors(self.pipeline_with_lock(lock)), ["5.1", "5.2", "5.10"])

    def test_a_missing_or_malformed_list_is_an_error_not_a_default(self) -> None:
        def without_blender_section(lock: dict) -> None:
            del lock["compatibility"]["blender"]

        def without_compatibility(lock: dict) -> None:
            del lock["compatibility"]

        def with_minors(value: object):
            def mutate(lock: dict) -> None:
                lock["compatibility"]["blender"]["supported_minors"] = value

            return mutate

        mutations = [without_blender_section, without_compatibility] + [
            with_minors(value) for value in ([], "5.2", ["5.2", "5.2"], [5.2], ["5"], ["5.2.1"])
        ]
        for mutate in mutations:
            lock = load_lock()
            mutate(lock)
            with self.subTest(lock=lock.get("compatibility", {}).get("blender")), self.assertRaisesRegex(
                bootstrap.SetupError, "supported_minors"
            ):
                bootstrap.supported_blender_minors(self.pipeline_with_lock(lock))
        with self.assertRaisesRegex(bootstrap.SetupError, "cannot be read"):
            bootstrap.supported_blender_minors(Path(tempfile.gettempdir()) / "no-such-pipeline-root")

    def test_compat_archive_minors_must_equal_the_supported_minors(self) -> None:
        for compat_minors in (["5.2"], ["5.1", "5.2", "5.3"], ["5.1"]):
            lock = load_lock()
            lock["compatibility"]["io_pdx_mesh"]["blender_minors"] = compat_minors
            with self.subTest(compat_minors=compat_minors), self.assertRaisesRegex(
                bootstrap.SetupError, "exactly the supported Blender minors"
            ):
                bootstrap.resolve_io_pdx_mesh(self.pipeline_with_lock(lock))

    def test_main_selects_blender_from_the_selected_projects_lock(self) -> None:
        tree = ast.parse((PIPELINE_ROOT / "bootstrap_3d_workflow.py").read_text(encoding="utf-8"))
        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
        calls = [
            node
            for node in ast.walk(main)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "find_blender"
        ]
        self.assertEqual([[ast.unparse(argument) for argument in call.args] for call in calls], [["pipeline_root"]])

    def test_new_adapter_modules_are_inside_the_hash_bound_source_closure(self) -> None:
        hashes = bootstrap.adapter_source_hashes(ADAPTER_ROOT)
        for name in (
            "texture_size_gate.py",
            "exporter_log_capture.py",
            "mesh_components.py",
            "profile_exceptions.py",
        ):
            self.assertIn(name, hashes)


class FindBlenderTests(unittest.TestCase):
    """find_blender on a fake Program Files tree whose executables answer --version."""

    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.versions: dict[Path, str] = {}
        environment = {
            "USERPROFILE": str(self.root / "user"),
            "LOCALAPPDATA": str(self.root / "user/AppData/Local"),
            "ProgramFiles": str(self.root / "Program Files"),
            "ProgramFiles(x86)": str(self.root / "Program Files (x86)"),
        }
        patcher = patch.dict(os.environ, environment)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("BLENDER_EXE", None)
        run_patch = patch.object(bootstrap, "run", side_effect=self.fake_version)
        run_patch.start()
        self.addCleanup(run_patch.stop)

    def fake_version(self, command: list[str], **_kwargs: object) -> str:
        self.assertEqual(command[1:], ["--version"])
        version = self.versions[Path(command[0]).resolve()]
        return f"Blender {version}\n\tbuild date: 2026-10-01\n" if version else "not a blender\n"

    def install(self, folder: str, version: str, parent: str = "Program Files") -> Path:
        executable = self.root / parent / "Blender Foundation" / folder / "blender.exe"
        executable.parent.mkdir(parents=True)
        executable.write_bytes(b"fake")
        self.versions[executable.resolve()] = version
        return executable.resolve()

    def test_highest_supported_minor_wins_over_older_and_unsupported_builds(self) -> None:
        self.install("Blender 4.4", "4.4.3")
        self.install("Blender 5.1", "5.1.2")
        newest = self.install("Blender 5.2", "5.2.1")
        self.install("Blender 5.3", "5.3.0")
        executable, shortcut, version = bootstrap.find_blender()
        self.assertEqual((executable, shortcut, version), (newest, None, "5.2.1"))

    def test_blender_51_is_accepted_when_it_is_the_only_supported_build(self) -> None:
        self.install("Blender 4.4", "4.4.3")
        only = self.install("Blender 5.1", "5.1.2")
        self.assertEqual(bootstrap.find_blender()[0::2], (only, "5.1.2"))

    def test_newest_patch_of_the_chosen_minor_is_used(self) -> None:
        self.install("Blender 5.2 a", "5.2.0")
        newer = self.install("Blender 5.2 b", "5.2.3", parent="Program Files (x86)")
        self.assertEqual(bootstrap.find_blender()[0::2], (newer, "5.2.3"))

    def test_only_unsupported_builds_are_refused_with_a_clear_message(self) -> None:
        self.install("Blender 4.4", "4.4.3")
        self.install("Blender 5.3", "5.3.0")
        with self.assertRaises(bootstrap.UnsupportedBlenderError) as raised:
            bootstrap.find_blender()
        message = str(raised.exception)
        self.assertIn("Blender 5.1 or 5.2 is required", message)
        self.assertIn("4.4.3", message)
        self.assertIn("5.3.0", message)

    def test_no_blender_at_all_keeps_the_discovery_error(self) -> None:
        with self.assertRaisesRegex(bootstrap.SetupError, "No usable Blender executable") as raised:
            bootstrap.find_blender()
        self.assertNotIsInstance(raised.exception, bootstrap.UnsupportedBlenderError)

    def test_a_build_that_does_not_report_a_version_is_ignored(self) -> None:
        self.install("Blender 9.9", "")
        supported = self.install("Blender 5.2", "5.2.0")
        self.assertEqual(bootstrap.find_blender()[0], supported)

    def test_blender_exe_naming_an_unsupported_build_is_refused_even_if_another_is_supported(self) -> None:
        self.install("Blender 5.2", "5.2.0")
        named = self.install("Blender 4.4", "4.4.3")
        with patch.dict(os.environ, {"BLENDER_EXE": str(named)}), self.assertRaisesRegex(
            bootstrap.UnsupportedBlenderError, r"BLENDER_EXE points to Blender 4\.4\.3"
        ):
            bootstrap.find_blender()

    def test_blender_exe_naming_a_supported_build_is_accepted(self) -> None:
        named = self.install("Blender 5.1", "5.1.2")
        with patch.dict(os.environ, {"BLENDER_EXE": str(named)}):
            self.assertEqual(bootstrap.find_blender()[0::2], (named, "5.1.2"))

    def test_selection_follows_the_lock_not_a_hardcoded_list(self) -> None:
        self.install("Blender 5.1", "5.1.2")
        newest = self.install("Blender 5.2", "5.2.1")
        lock = load_lock()
        lock["compatibility"]["blender"]["supported_minors"] = ["5.1"]
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        pipeline = Path(temp.name)
        (pipeline / "config").mkdir()
        (pipeline / "config/dependencies.lock.json").write_text(json.dumps(lock), encoding="utf-8")
        self.assertNotEqual(bootstrap.find_blender(pipeline)[0], newest)
        self.assertEqual(bootstrap.find_blender(pipeline)[2], "5.1.2")


class InstalledIoPdxHashTests(unittest.TestCase):
    """ensure_io_pdx_mesh keeps an install only when its locked patched files hash correctly."""

    MINORS = ("5.1", "5.2")

    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = source_archive()
        self.resolution = compatibility_resolution(self.source)
        self.expected = self.resolution["compatibility"]["installed_patch_files_sha256"]
        self.extractions: list[Path] = []
        self.after_extract = None

    def install_root(self, minor: str) -> Path:
        return self.root / "appdata/Blender Foundation/Blender" / minor / "extensions/user_default/io_pdx_mesh"

    def ensure(self, minor: str, patch_level: str = "2") -> dict:
        original_extract = bootstrap.safe_extract

        def record_extract(archive, destination: Path) -> None:
            self.extractions.append(destination)
            original_extract(archive, destination)
            if self.after_extract is not None:
                self.after_extract(destination)

        def fake_download(_url: str, destination: Path) -> None:
            destination.write_bytes(self.source)

        with patch.dict(os.environ, {"APPDATA": str(self.root / "appdata")}), patch.object(
            bootstrap, "run", return_value=f"Blender {minor}.{patch_level}"
        ), patch.object(bootstrap, "download", side_effect=fake_download), patch.object(
            bootstrap, "safe_extract", side_effect=record_extract
        ):
            return bootstrap.ensure_io_pdx_mesh(self.root / "pipeline", Path("blender.exe"), self.resolution)

    def installed_hashes(self, minor: str) -> dict[str, str]:
        root = self.install_root(minor)
        return {relative: sha256((root / relative).read_bytes()) for relative in self.expected}

    def test_fresh_install_writes_and_verifies_the_patched_files_on_each_minor(self) -> None:
        for minor in self.MINORS:
            with self.subTest(minor=minor):
                result = self.ensure(minor)
                self.assertTrue(result["compatibility_applied"])
                self.assertEqual(result["blender_minor"], minor)
                self.assertEqual(result["version"], "0.91.0")
                self.assertEqual(result["installed_patch_files_sha256"], self.expected)
                self.assertEqual(self.installed_hashes(minor), self.expected)

    def test_a_matching_install_is_kept_without_extracting_again(self) -> None:
        for minor in self.MINORS:
            with self.subTest(minor=minor):
                self.ensure(minor)
                before = len(self.extractions)
                again = self.ensure(minor)
                self.assertEqual(len(self.extractions), before)
                self.assertEqual(again["installed_patch_files_sha256"], self.expected)

    def test_same_version_text_is_not_enough_to_keep_an_unpatched_install(self) -> None:
        for minor in self.MINORS:
            with self.subTest(minor=minor):
                install = self.install_root(minor)
                install.mkdir(parents=True)
                with zipfile.ZipFile(io.BytesIO(self.source)) as archive:
                    for member in archive.namelist():
                        destination = install / Path(*Path(member).parts[1:])
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_bytes(archive.read(member))
                self.assertNotEqual(self.installed_hashes(minor), self.expected)
                before = len(self.extractions)
                self.ensure(minor)
                self.assertEqual(len(self.extractions), before + 1)
                self.assertEqual(self.installed_hashes(minor), self.expected)

    def test_an_edited_or_missing_patched_file_forces_a_reinstall_on_each_minor(self) -> None:
        for minor in self.MINORS:
            for damage in ("append", "delete"):
                with self.subTest(minor=minor, damage=damage):
                    self.ensure(minor)
                    target = self.install_root(minor) / "pdx_blender/blender_import_export.py"
                    if damage == "append":
                        target.write_bytes(target.read_bytes() + b"# edited\n")
                    else:
                        target.unlink()
                    before = len(self.extractions)
                    self.ensure(minor)
                    self.assertEqual(len(self.extractions), before + 1)
                    self.assertEqual(self.installed_hashes(minor), self.expected)

    def test_an_install_that_still_fails_its_hash_after_extraction_is_an_error(self) -> None:
        for minor in self.MINORS:
            with self.subTest(minor=minor):
                self.after_extract = lambda staging: next(staging.rglob("__init__.py")).write_bytes(b"tampered\n")
                with self.assertRaisesRegex(bootstrap.SetupError, "failed hash verification: __init__.py"):
                    self.ensure(minor)
                self.after_extract = None
                shutil.rmtree(self.install_root(minor).parent, ignore_errors=True)

    def test_unsupported_minor_is_refused_and_leaves_the_verified_cache_and_user_folder_alone(self) -> None:
        for minor in ("4.4", "5.0", "5.3"):
            with self.subTest(minor=minor):
                cache = self.root / "pipeline/vendor/io_pdx_mesh/0.91-io_pdx_mesh.zip"
                with self.assertRaises(bootstrap.UnsupportedBlenderError):
                    self.ensure(minor)
                self.assertTrue(cache.is_file())
                self.assertFalse((self.root / "appdata/Blender Foundation/Blender" / minor).exists())

    def test_a_tampered_cache_is_still_deleted_on_a_supported_minor(self) -> None:
        cache = self.root / "pipeline/vendor/io_pdx_mesh/0.91-io_pdx_mesh.zip"
        cache.parent.mkdir(parents=True)
        cache.write_bytes(b"tampered")
        with patch.dict(os.environ, {"APPDATA": str(self.root / "appdata")}), patch.object(
            bootstrap, "run", return_value="Blender 5.1.2"
        ), self.assertRaisesRegex(bootstrap.SetupError, "size"):
            bootstrap.ensure_io_pdx_mesh(self.root / "pipeline", Path("blender.exe"), self.resolution)
        self.assertFalse(cache.exists())

    def test_patch_mismatch_helper_reports_missing_and_changed_files(self) -> None:
        install = self.install_root("5.1")
        self.assertEqual(sorted(bootstrap.installed_patch_mismatches(install, self.expected)), sorted(self.expected))
        self.ensure("5.1")
        self.assertEqual(bootstrap.installed_patch_mismatches(install, self.expected), [])
        (install / "__init__.py").write_bytes(b"changed")
        self.assertEqual(bootstrap.installed_patch_mismatches(install, self.expected), ["__init__.py"])


if __name__ == "__main__":
    unittest.main()
