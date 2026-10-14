from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / ".tools/mcp/bootstrap_hoi4_agent_tools.py"
SPEC = importlib.util.spec_from_file_location("private_npm_bootstrap", SCRIPT)
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)


def archive_bytes(extra=(), version="11.19.0"):
    contents = io.BytesIO()
    entries = [("package/package.json", json.dumps({"name": "npm", "version": version}).encode()), ("package/bin/npm-cli.js", b"// fixture only\n"), *extra]
    with tarfile.open(fileobj=contents, mode="w:") as archive:
        for name, data in entries:
            entry = name if isinstance(name, tarfile.TarInfo) else tarfile.TarInfo(name)
            entry.size = len(data)
            archive.addfile(entry, io.BytesIO(data))
    return gzip.compress(contents.getvalue())


class PrivateNpmToolchainTests(unittest.TestCase):
    def test_node_engine_intersection_and_architecture(self):
        for value in ["v22.19.0", "v22.23.3", "v24.0.0", "v24.21.0"]:
            self.assertTrue(bootstrap.supported_node_version(value), value)
        for value in ["v18.20.0", "v22.9.0", "v22.18.9", "v23.0.0", "v25.0.0", "v26.0.0", "v24.1.0-rc.1", "bad"]:
            self.assertFalse(bootstrap.supported_node_version(value), value)
        with mock.patch.object(bootstrap, "run", side_effect=["v24.21.0", "arm64"]), self.assertRaisesRegex(bootstrap.BootstrapError, "x64"):
            bootstrap.verify_node_runtime(Path("node"))

    def test_node_discovery_cannot_inherit_node_or_npm_overrides(self):
        completed = mock.Mock(returncode=0, stdout=b"v24.21.0", stderr=b"")
        with mock.patch.dict(os.environ, {"NODE_OPTIONS": "--require unsafe", "NPM_CONFIG_REGISTRY": "https://unsafe.invalid", "GITHUB_TOKEN": "private"}), mock.patch.object(bootstrap.subprocess, "run", return_value=completed) as run:
            bootstrap.run(["node", "--version"])
        for name in ["NODE_OPTIONS", "NPM_CONFIG_REGISTRY", "GITHUB_TOKEN"]:
            self.assertNotIn(name, run.call_args.kwargs["env"])

    def test_download_is_exact_origin_bounded_and_integrity_checked(self):
        body = archive_bytes()
        integrity = "sha512-" + base64.b64encode(hashlib.sha512(body).digest()).decode()
        response = io.BytesIO(body)
        response.status = 200
        response.url = "https://registry.npmjs.org/npm/-/npm-11.19.0.tgz"
        opener = mock.Mock()
        opener.open.return_value = response
        with mock.patch.object(bootstrap.urllib.request, "build_opener", return_value=opener):
            self.assertEqual(bootstrap.download_npm_archive("11.19.0", integrity), body)
        opener.open.assert_called_once_with(response.url, timeout=60)
        response = io.BytesIO(body)
        response.status = 200
        response.url = "https://registry.npmjs.org/npm/-/npm-11.19.0.tgz"
        opener.open.return_value = response
        with mock.patch.object(bootstrap.urllib.request, "build_opener", return_value=opener), self.assertRaisesRegex(bootstrap.BootstrapError, "integrity"):
            bootstrap.download_npm_archive("11.19.0", "sha512-wrong")
        with self.assertRaisesRegex(bootstrap.BootstrapError, "redirect"):
            bootstrap.NoRedirect().redirect_request(None, None, 302, "redirect", {}, "https://other.invalid")

    def test_valid_archive_is_exclusive_and_package_bound(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "runtime"
            entry = bootstrap.extract_npm_archive(archive_bytes(), destination, "11.19.0")
            self.assertEqual(entry.read_bytes(), b"// fixture only\n")
            with self.assertRaises(bootstrap.BootstrapError):
                bootstrap.extract_npm_archive(archive_bytes(), destination, "11.19.0")
            with self.assertRaisesRegex(bootstrap.BootstrapError, "identity"):
                bootstrap.extract_npm_archive(archive_bytes(), Path(temporary) / "wrong", "10.9.9")

    def test_unsafe_inventory_is_rejected_before_writes(self):
        paths = ["/absolute", "other/file", "package/../escape", "package/./file", "package//file", "package/a\\b", "package/a:stream", "package/.git/config", "package/NUL.txt", "package/trailing.", "package/" + "a" * 256, "package/" + "a/" * 33 + "file"]
        entries = [[(path, b"x")] for path in paths]
        entries += [[("package/A", b"x"), ("package/a", b"x")], [("package/caf\u00e9", b"x"), ("package/cafe\u0301", b"x")]]
        for kind in [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.CHRTYPE, tarfile.FIFOTYPE, tarfile.DIRTYPE]:
            member = tarfile.TarInfo("package/unsafe")
            member.type = kind
            entries.append([(member, b"")])
        for extra in entries:
            with self.subTest(extra=extra), tempfile.TemporaryDirectory() as temporary:
                destination = Path(temporary) / "runtime"
                with self.assertRaises(bootstrap.BootstrapError):
                    bootstrap.extract_npm_archive(archive_bytes(extra), destination, "11.19.0")
                self.assertFalse(destination.exists())

    def test_archive_resource_bounds(self):
        for name in ["MAX_NPM_ARCHIVE_BYTES", "MAX_NPM_TAR_BYTES", "MAX_NPM_FILES", "MAX_NPM_FILE_BYTES"]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                destination = Path(temporary) / "runtime"
                with mock.patch.object(bootstrap, name, 1), self.assertRaises(bootstrap.BootstrapError):
                    bootstrap.extract_npm_archive(archive_bytes(), destination, "11.19.0")
                self.assertFalse(destination.exists())
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(bootstrap.BootstrapError, "expansion"):
            bootstrap.extract_npm_archive(archive_bytes([("package/large", b"x" * 1024 * 1024)]), Path(temporary) / "runtime", "11.19.0")

    def test_private_runtime_never_uses_ambient_npm_config_or_project_cwd(self):
        with mock.patch.object(bootstrap, "platform_name", return_value="windows"), mock.patch.object(bootstrap, "download_npm_archive", return_value=archive_bytes()), mock.patch.dict(os.environ, {"NODE_OPTIONS": "--require private-value", "NPM_CONFIG_REGISTRY": "https://unreviewed.invalid", "GITHUB_TOKEN": "private-value", "PYTHONPATH": "private-value"}):
            with bootstrap.pinned_npm_runtime() as runtime:
                root = runtime.root
                for name in ["NODE_OPTIONS", "NPM_CONFIG_REGISTRY", "GITHUB_TOKEN", "PYTHONPATH"]:
                    self.assertNotIn(name, runtime.environment)
                self.assertEqual((root / "user.npmrc").read_bytes(), b"")
                self.assertEqual((root / "global.npmrc").read_bytes(), b"")
                with mock.patch.object(bootstrap, "run", return_value="{}") as run:
                    bootstrap.npm(Path("node"), runtime, ["view", bootstrap.PACKAGE_SPEC])
                self.assertEqual(run.call_args.kwargs["cwd"], root)
                self.assertEqual(run.call_args.kwargs["environment"], runtime.environment)
                self.assertIn("--registry=https://registry.npmjs.org", run.call_args.args[0])
                self.assertEqual(run.call_args.args[0][1], str(runtime.entry))
            self.assertFalse(root.exists())
        with self.assertRaisesRegex(bootstrap.BootstrapError, "Only the verified"):
            bootstrap.npm(Path("node"), Path("ambient/npm.cmd"), [])

    def test_runtime_cleanup_after_failure(self):
        with mock.patch.object(bootstrap, "platform_name", return_value="windows"), mock.patch.object(bootstrap, "download_npm_archive", return_value=archive_bytes()):
            with self.assertRaisesRegex(RuntimeError, "injected"):
                with bootstrap.pinned_npm_runtime() as runtime:
                    root = runtime.root
                    raise RuntimeError("injected")
            self.assertFalse(root.exists())

    def test_existing_package_bounds_precede_large_file_reads(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "large").write_bytes(b"large fixture")
            with mock.patch.object(bootstrap, "MAX_PACKAGE_FILE_BYTES", 1), mock.patch.object(Path, "open", side_effect=AssertionError("must not read oversized file")), self.assertRaisesRegex(bootstrap.BootstrapError, "oversized"):
                bootstrap.package_tree_sha256(root, {})
        for limit in ["MAX_PACKAGE_ENTRIES", "MAX_PACKAGE_DEPTH"]:
            with self.subTest(limit=limit), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / "a/b").mkdir(parents=True)
                with mock.patch.object(bootstrap, limit, 1), self.assertRaisesRegex(bootstrap.BootstrapError, "directory bounds"):
                    bootstrap.package_tree_sha256(root, {})


if __name__ == "__main__":
    unittest.main()
