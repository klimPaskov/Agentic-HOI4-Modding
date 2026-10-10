from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".tools" / "mcp" / "bootstrap_hoi4_live_tools.py"
SPEC = importlib.util.spec_from_file_location("bootstrap_hoi4_live_tools", SCRIPT)
assert SPEC and SPEC.loader
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)


def manifest() -> dict:
    return json.loads((ROOT / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8"))


def component(manifest_data: dict, component_id: str) -> dict:
    return next(item for item in manifest_data["components"] if item["id"] == component_id)


def write_archive(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as bundle:
        for name, data in members.items():
            bundle.writestr(name, data)


class LiveBootstrapContractTests(unittest.TestCase):
    def test_manifest_pins_the_same_release(self) -> None:
        action = next(
            rule for rule in component(manifest(), "mcp.hoi4_live.bootstrap")["validation"] if rule["id"] == "mcp.live_bootstrap"
        )
        parameters = action["parameters"]
        self.assertEqual(parameters["release_version"], bootstrap.RELEASE_VERSION)
        self.assertEqual(parameters["release_url"], bootstrap.RELEASE_URL)
        self.assertEqual(parameters["release_sha256"], bootstrap.RELEASE_SHA256)
        self.assertEqual(parameters["release_size"], bootstrap.RELEASE_SIZE)
        self.assertEqual(action["target"], ".tools/mcp/bootstrap_hoi4_live_tools.py")
        self.assertEqual(parameters["arguments"], ["--quiet"])
        self.assertEqual(parameters["privilege"], "current_user")
        self.assertTrue(parameters["network_access"] and parameters["expected_writes"] and parameters["rollback_boundary"])

    def test_pin_is_well_formed(self) -> None:
        self.assertEqual(len(bootstrap.RELEASE_SHA256), 64)
        int(bootstrap.RELEASE_SHA256, 16)
        self.assertTrue(bootstrap.RELEASE_URL.startswith("https://github.com/klimPaskov/HOI4-Live-Tools/releases/download/"))
        self.assertIn(f"v{bootstrap.RELEASE_VERSION}/", bootstrap.RELEASE_URL)
        self.assertTrue(bootstrap.RELEASE_URL.endswith(f"hoi4-live-tools-{bootstrap.RELEASE_VERSION}.zip"))
        self.assertTrue(bootstrap.host_allowed(bootstrap.RELEASE_URL))
        self.assertGreater(bootstrap.RELEASE_SIZE, 0)

    def test_workflow_component_depends_on_the_bootstrap_and_the_skill_exists(self) -> None:
        data = manifest()
        workflow = component(data, "workflow.live_tools")
        self.assertIn("mcp.hoi4_live.bootstrap", workflow["dependencies"])
        self.assertEqual(workflow["source"]["include"], ["hoi4-live-playtest/**"])
        self.assertTrue((ROOT / ".claude" / "skills" / "hoi4-live-playtest" / "SKILL.md").is_file())
        self.assertFalse((ROOT / ".claude" / "skills" / "hoi4-live-testing").exists())
        bootstrap_component = component(data, "mcp.hoi4_live.bootstrap")
        self.assertEqual(bootstrap_component["source"]["path"], ".tools/mcp/bootstrap_hoi4_live_tools.py")
        self.assertEqual(bootstrap_component["platforms"], ["windows"])

    def test_hosts_and_redirects(self) -> None:
        self.assertTrue(bootstrap.host_allowed("https://github.com/x"))
        self.assertTrue(bootstrap.host_allowed("https://objects.githubusercontent.com/x"))
        self.assertTrue(bootstrap.host_allowed("https://release-assets.githubusercontent.com/x"))
        self.assertFalse(bootstrap.host_allowed("http://github.com/x"))
        self.assertFalse(bootstrap.host_allowed("https://github.com.evil.example/x"))
        self.assertFalse(bootstrap.host_allowed("https://evilgithubusercontent.com/x"))

    def test_archive_must_match_size_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.zip"
            write_archive(path, {f"{bootstrap.ARCHIVE_TOP}/install.py": b"print(1)\n"})
            with self.assertRaisesRegex(bootstrap.BootstrapError, "pins"):
                bootstrap.verify_archive(path)
            with mock.patch.object(bootstrap, "RELEASE_SIZE", path.stat().st_size):
                with self.assertRaisesRegex(bootstrap.BootstrapError, "SHA-256"):
                    bootstrap.verify_archive(path)
                with mock.patch.object(bootstrap, "RELEASE_SHA256", bootstrap.sha256_file(path)):
                    bootstrap.verify_archive(path)

    def test_extraction_rejects_unsafe_members(self) -> None:
        top = bootstrap.ARCHIVE_TOP
        bad_names = [
            "../evil.txt",
            f"{top}/../../evil.txt",
            "/abs/evil.txt",
            "C:/evil.txt",
            "other/install.py",
        ]
        for name in bad_names:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "a.zip"
                write_archive(path, {name: b"x"})
                with self.assertRaisesRegex(bootstrap.BootstrapError, "unsafe|outside"):
                    bootstrap.safe_extract(path, Path(tmp) / "out")

    def test_extraction_rejects_links_and_oversized_members(self) -> None:
        top = bootstrap.ARCHIVE_TOP
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "link.zip"
            with zipfile.ZipFile(path, "w") as bundle:
                info = zipfile.ZipInfo(f"{top}/link")
                info.external_attr = 0o120777 << 16
                bundle.writestr(info, "target")
            with self.assertRaisesRegex(bootstrap.BootstrapError, "unsafe"):
                bootstrap.safe_extract(path, Path(tmp) / "out1")
            big = Path(tmp) / "big.zip"
            write_archive(big, {f"{top}/install.py": b"x" * 100})
            with mock.patch.object(bootstrap, "MAX_MEMBER_BYTES", 10):
                with self.assertRaisesRegex(bootstrap.BootstrapError, "oversized"):
                    bootstrap.safe_extract(big, Path(tmp) / "out2")

    def test_extraction_returns_the_installer(self) -> None:
        top = bootstrap.ARCHIVE_TOP
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ok.zip"
            write_archive(path, {f"{top}/install.py": b"print(1)\n", f"{top}/hoi4_live/__init__.py": b""})
            installer = bootstrap.safe_extract(path, Path(tmp) / "out")
            self.assertEqual(installer.name, "install.py")
            self.assertTrue((installer.parent / "hoi4_live" / "__init__.py").is_file())

    def test_download_over_the_pinned_size_is_refused(self) -> None:
        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        opener = mock.Mock()
        opener.open.return_value = Response(b"x" * 50)
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(bootstrap, "RELEASE_SIZE", 10), mock.patch.object(
            bootstrap.urllib.request, "build_opener", return_value=opener
        ):
            with self.assertRaisesRegex(bootstrap.BootstrapError, "larger than the pinned size"):
                bootstrap.download(Path(tmp) / "r.zip")

    def test_installed_copy_is_reused_without_download(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp)
            (prefix / "app").mkdir()
            (prefix / "app" / "install.py").write_text("", encoding="utf-8")
            (prefix / "install.json").write_text(json.dumps({"version": bootstrap.RELEASE_VERSION}), encoding="utf-8")
            with contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(bootstrap, "installed_prefix", return_value=prefix))
                stack.enter_context(mock.patch.object(bootstrap.sys, "platform", "win32"))
                run = stack.enter_context(mock.patch.object(bootstrap, "run_installer", return_value=0))
                fetch = stack.enter_context(mock.patch.object(bootstrap, "download"))
                self.assertEqual(bootstrap.main(["--quiet"]), 0)
            fetch.assert_not_called()
            self.assertEqual(run.call_args.args[0], prefix / "app" / "install.py")

    def test_installer_exit_code_is_returned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            top = bootstrap.ARCHIVE_TOP
            archive = Path(tmp) / "r.zip"
            write_archive(archive, {f"{top}/install.py": b"import sys\nsys.exit(4)\n"})
            with contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(bootstrap, "RELEASE_SIZE", archive.stat().st_size))
                stack.enter_context(mock.patch.object(bootstrap, "RELEASE_SHA256", bootstrap.sha256_file(archive)))
                stack.enter_context(mock.patch.object(bootstrap, "installed_prefix", return_value=Path(tmp) / "none"))
                stack.enter_context(mock.patch.object(bootstrap.sys, "platform", "win32"))
                self.assertEqual(bootstrap.main(["--quiet", "--archive", str(archive)]), 4)


if __name__ == "__main__":
    unittest.main()
