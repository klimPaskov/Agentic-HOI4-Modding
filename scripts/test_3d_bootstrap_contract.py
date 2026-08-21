from __future__ import annotations

import importlib.util
import io
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / ".tools/3d_pipeline/bootstrap_3d_workflow.py"
SPEC = importlib.util.spec_from_file_location("three_d_bootstrap", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
BOOTSTRAP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOOTSTRAP)


class ReviewedConfigTests(unittest.TestCase):
    def test_materialized_routes_pass_reviewed_config_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = BOOTSTRAP.materialize_config(root)

            self.assertEqual(BOOTSTRAP.verify_reviewed_config(root), config)

    def test_changed_reviewed_route_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = BOOTSTRAP.materialize_config(root)
            config.write_text(
                config.read_text(encoding="utf-8").replace(
                    'command = "cmd.exe"', 'command = "unreviewed.exe"', 1
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(BOOTSTRAP.SetupError, "unexpected"):
                BOOTSTRAP.verify_reviewed_config(root)

    def test_only_meshy_route_receives_the_meshy_credential(self) -> None:
        self.assertEqual(BOOTSTRAP.THREE_D_MCP_ROUTES["meshy"]["env_vars"], ["MESHY_API_KEY"])
        self.assertEqual(BOOTSTRAP.THREE_D_MCP_ROUTES["blender_hoi4"]["env_vars"], [])
        self.assertEqual(BOOTSTRAP.THREE_D_MCP_ROUTES["blender_lab"]["env_vars"], [])


class CredentialBoundaryTests(unittest.TestCase):
    def test_meshy_key_is_removed_before_dependency_children_can_inherit_it(self) -> None:
        with mock.patch.dict(os.environ, {"MESHY_API_KEY": "msy_test_value"}, clear=False):
            self.assertEqual(BOOTSTRAP.require_meshy_key(), "msy_test_value")
            self.assertNotIn("MESHY_API_KEY", os.environ)

    def test_meshy_verification_uses_the_bounded_authenticated_endpoint(self) -> None:
        with mock.patch.object(BOOTSTRAP, "fetch_json", return_value={"balance": 1.25}) as fetch:
            BOOTSTRAP.verify_meshy_key("msy_test_value")
        fetch.assert_called_once_with(
            BOOTSTRAP.MESHY_BALANCE_API,
            allowed_hosts=BOOTSTRAP.MESHY_API_HOSTS,
            max_bytes=BOOTSTRAP.MAX_MESHY_RESPONSE_BYTES,
            headers={"Authorization": "Bearer msy_test_value"},
        )

    def test_dependency_child_environment_never_contains_meshy_key(self) -> None:
        completed = mock.Mock(returncode=0, stdout="ok")
        with mock.patch.dict(os.environ, {"MESHY_API_KEY": "msy_test_value"}, clear=False), \
            mock.patch.object(BOOTSTRAP.subprocess, "run", return_value=completed) as run:
            self.assertEqual(BOOTSTRAP.run(["C:/approved/tool.exe"]), "ok")
        self.assertNotIn("MESHY_API_KEY", run.call_args.kwargs["env"])

    def test_provider_rejection_stops_before_project_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "project"
            with mock.patch.dict(os.environ, {"MESHY_API_KEY": "msy_invalid"}, clear=False), mock.patch.object(
                BOOTSTRAP, "verify_meshy_key", side_effect=BOOTSTRAP.SetupError("rejected")
            ), mock.patch.object(
                BOOTSTRAP.sys, "argv", [str(SCRIPT), "--project-root", str(root), "--quiet"]
            ):
                self.assertEqual(BOOTSTRAP.main(), 2)
            self.assertFalse(root.exists())


class DependencyBoundaryTests(unittest.TestCase):
    def test_meshy_package_is_pinned_to_exact_registry_integrity(self) -> None:
        with mock.patch.object(BOOTSTRAP, "npm_for_npx", return_value=Path("C:/node/npm.cmd")), \
            mock.patch.object(BOOTSTRAP, "run", return_value=f'"{BOOTSTRAP.MESHY_INTEGRITY}"'):
            resolution = BOOTSTRAP.resolve_meshy(Path("C:/node/npx.cmd"))
        self.assertEqual(resolution["version"], BOOTSTRAP.MESHY_VERSION)
        self.assertEqual(resolution["integrity"], BOOTSTRAP.MESHY_INTEGRITY)

    def test_tampered_cached_io_pdx_archive_is_deleted_before_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            resolution = BOOTSTRAP.resolve_io_pdx_mesh()
            cache = root / "vendor/io_pdx_mesh" / f"{resolution['release']}-{resolution['asset_name']}"
            cache.parent.mkdir(parents=True)
            cache.write_bytes(b"tampered")
            with mock.patch.object(BOOTSTRAP, "run", return_value="Blender 4.3.0"), \
                mock.patch.dict(os.environ, {"APPDATA": str(root / "appdata")}, clear=False), \
                self.assertRaisesRegex(BOOTSTRAP.SetupError, "SHA-256"):
                BOOTSTRAP.ensure_io_pdx_mesh(root, Path("C:/Blender/blender.exe"), resolution)
            self.assertFalse(cache.exists())

    def test_node_install_is_current_user_scoped(self) -> None:
        installed = False

        def which(name: str) -> str | None:
            if name in ("npx.cmd", "npx"):
                return "C:/Users/test/AppData/Local/nodejs/npx.cmd" if installed else None
            if name == "winget":
                return "C:/Windows/System32/winget.exe"
            return None

        def run(command: list[str], **_kwargs: object) -> str:
            nonlocal installed
            installed = True
            self.assertIn("--scope", command)
            self.assertEqual(command[command.index("--scope") + 1], "user")
            self.assertIn("--disable-interactivity", command)
            return ""

        with mock.patch.object(BOOTSTRAP.shutil, "which", side_effect=which), mock.patch.object(
            BOOTSTRAP, "run", side_effect=run
        ):
            self.assertTrue(str(BOOTSTRAP.ensure_npx()).lower().endswith("npx.cmd"))

    def test_unapproved_download_hosts_and_ports_are_rejected(self) -> None:
        for url in (
            "http://github.com/example.zip",
            "https://example.com/example.zip",
            "https://github.com:8443/example.zip",
            "https://user@github.com/example.zip",
        ):
            with self.subTest(url=url), self.assertRaises(BOOTSTRAP.SetupError):
                BOOTSTRAP._validate_https_url(url, BOOTSTRAP.GITHUB_DOWNLOAD_HOSTS)

    def test_response_bytes_are_bounded_even_without_content_length(self) -> None:
        class Response:
            headers: dict[str, str] = {}

            def __init__(self) -> None:
                self.stream = io.BytesIO(b"x" * 9)

            def read(self, size: int) -> bytes:
                return self.stream.read(size)

        with self.assertRaisesRegex(BOOTSTRAP.SetupError, "byte limit"):
            BOOTSTRAP._read_bounded_response(Response(), 8)

    def test_archive_duplicate_cleanup_is_atomic(self) -> None:
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("a.txt", "first")
            archive.writestr("A.txt", "second")
        payload.seek(0)
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "staging"
            with zipfile.ZipFile(payload) as archive, self.assertRaisesRegex(
                BOOTSTRAP.SetupError, "duplicate"
            ):
                BOOTSTRAP.safe_extract(archive, destination)
            self.assertFalse(destination.exists())

    def test_archive_traversal_and_extreme_compression_are_rejected(self) -> None:
        traversal = io.BytesIO()
        with zipfile.ZipFile(traversal, "w") as archive:
            archive.writestr("../escape.txt", "escape")
        traversal.seek(0)
        compressed = io.BytesIO()
        with zipfile.ZipFile(compressed, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("large.txt", b"0" * (2 * 1024 * 1024))
        compressed.seek(0)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with zipfile.ZipFile(traversal) as archive, self.assertRaises(BOOTSTRAP.SetupError):
                BOOTSTRAP.safe_extract(archive, root / "traversal")
            with zipfile.ZipFile(compressed) as archive, self.assertRaisesRegex(
                BOOTSTRAP.SetupError, "compression ratio"
            ):
                BOOTSTRAP.safe_extract(archive, root / "compressed")


if __name__ == "__main__":
    unittest.main()
