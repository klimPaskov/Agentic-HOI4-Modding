from __future__ import annotations

import contextlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".tools" / "mcp" / "bootstrap_hoi4_agent_tools.py"
SPEC = importlib.util.spec_from_file_location("bootstrap_hoi4_agent_tools", SCRIPT)
assert SPEC and SPEC.loader
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)
PIN_SPEC = importlib.util.spec_from_file_location("refresh_mcp_package_pin", ROOT / "scripts/refresh_mcp_package_pin.py")
assert PIN_SPEC and PIN_SPEC.loader
pin = importlib.util.module_from_spec(PIN_SPEC)
PIN_SPEC.loader.exec_module(pin)


class McpBootstrapContractTests(unittest.TestCase):
    def setUp(self) -> None:
        # Existing fixtures deliberately describe the Windows installation.
        patch = mock.patch.object(bootstrap, "platform_name", return_value="windows")
        patch.start()
        self.addCleanup(patch.stop)
        runtime = mock.patch.object(bootstrap, "pinned_npm_runtime", return_value=contextlib.nullcontext(Path("npm.cmd")))
        runtime.start()
        self.addCleanup(runtime.stop)

    def test_public_release_identity_is_exact(self) -> None:
        # The bootstrap and the setup manifest must pin the same measured release.
        manifest = json.loads((Path(__file__).resolve().parents[1] / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8"))
        health = next(
            rule["parameters"]
            for component in manifest["components"]
            for rule in component.get("validation", [])
            if rule.get("parameters", {}).get("package_name") == "hoi4-agent-tools"
        )
        self.assertEqual(bootstrap.PACKAGE_SPEC, f"hoi4-agent-tools@{health['package_version']}")
        self.assertEqual(bootstrap.PACKAGE_INTEGRITY, health["package_integrity"])
        self.assertEqual(bootstrap.PACKAGE_TREE_SHA256, health["package_tree_sha256"])
        self.assertEqual(bootstrap.PACKAGE_FILE_COUNT, health["package_file_count"])
        self.assertEqual(bootstrap.RUNTIME_ENTRY_SHA256, health["runtime_entry_sha256"])
        self.assertEqual(bootstrap.RUNTIME_ENTRY_SIZE, health["runtime_entry_size"])
        self.assertGreaterEqual(bootstrap.MAX_PACKAGE_FILE_BYTES, 18_406_400)
        self.assertEqual(bootstrap.RUNTIME_ENTRY, "dist/bin/stdio.js")
        self.assertEqual(len(bootstrap.RUNTIME_ENTRY_SHA256), 64)
        self.assertGreater(bootstrap.RUNTIME_ENTRY_SIZE, 0)

    def test_install_is_user_scoped_script_free_and_registry_bound(self) -> None:
        with mock.patch.object(bootstrap, "npm", return_value="") as npm:
            bootstrap.install_package(Path("node.exe"), Path("npm.cmd"), Path("user-prefix"))
        arguments = npm.call_args.args[2]
        self.assertIn("--global", arguments)
        self.assertIn("--ignore-scripts", arguments)
        self.assertIn("--prefix", arguments)
        self.assertIn("--registry=https://registry.npmjs.org", arguments)
        self.assertEqual(arguments[-1], bootstrap.PACKAGE_SPEC)

    def test_local_tarball_requires_exact_sha512(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "reviewed.tgz"
            archive.write_bytes(b"synthetic reviewed archive")
            integrity = "sha512-" + __import__("base64").b64encode(__import__("hashlib").sha512(archive.read_bytes()).digest()).decode("ascii")
            with mock.patch.object(bootstrap, "PACKAGE_INTEGRITY", integrity), mock.patch.object(bootstrap, "npm", return_value="") as npm:
                self.assertEqual(bootstrap.verify_local_tarball(archive), archive.resolve())
                bootstrap.install_package(Path("node.exe"), Path("npm.cmd"), Path("prefix"), archive)
            self.assertEqual(npm.call_args.args[2][-1], str(archive.resolve()))
            with self.assertRaisesRegex(bootstrap.BootstrapError, "integrity"):
                bootstrap.verify_local_tarball(archive)

    def test_missing_local_tarball_fails_before_npm_install(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(bootstrap, "npm") as npm:
            with self.assertRaises(bootstrap.BootstrapError):
                bootstrap.install_package(Path("node.exe"), Path("npm.cmd"), Path("prefix"), Path(temporary) / "missing.tgz")
            npm.assert_not_called()

    def test_oversized_local_tarball_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "oversized.tgz"
            archive.write_bytes(b"synthetic archive")
            with mock.patch.object(bootstrap, "MAX_PACKAGE_ARCHIVE_BYTES", 1):
                with self.assertRaisesRegex(bootstrap.BootstrapError, "oversized"):
                    bootstrap.verify_local_tarball(archive)

    def test_default_registry_failure_never_falls_back_or_installs(self) -> None:
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(bootstrap, "ensure_node", return_value=(Path("node.exe"), Path("npm.cmd"))))
            stack.enter_context(mock.patch.object(bootstrap, "user_prefix", return_value=Path("prefix")))
            stack.enter_context(mock.patch.object(bootstrap, "platform_name", return_value="windows"))
            stack.enter_context(mock.patch.object(bootstrap.sys, "argv", ["bootstrap", "--quiet"]))
            registry = stack.enter_context(mock.patch.object(bootstrap, "verify_registry_integrity", side_effect=bootstrap.BootstrapError("unpublished release")))
            local = stack.enter_context(mock.patch.object(bootstrap, "verify_local_tarball"))
            install = stack.enter_context(mock.patch.object(bootstrap, "install_package"))
            remove = stack.enter_context(mock.patch.object(bootstrap, "remove_mismatched_package"))
            with self.assertRaisesRegex(bootstrap.BootstrapError, "unpublished"):
                bootstrap.main()
            registry.assert_called_once()
            local.assert_not_called()
            install.assert_not_called()
            remove.assert_not_called()

    def test_explicit_local_route_skips_registry_but_checks_tree(self) -> None:
        prefix = Path("prefix")
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(bootstrap, "ensure_node", return_value=(Path("node.exe"), Path("npm.cmd"))))
            stack.enter_context(mock.patch.object(bootstrap, "user_prefix", return_value=prefix))
            stack.enter_context(mock.patch.object(bootstrap, "platform_name", return_value="windows"))
            stack.enter_context(mock.patch.object(bootstrap.sys, "argv", ["bootstrap", "--quiet", "--local-tarball", "reviewed.tgz"]))
            local = stack.enter_context(mock.patch.object(bootstrap, "verify_local_tarball"))
            registry = stack.enter_context(mock.patch.object(bootstrap, "verify_registry_integrity"))
            stack.enter_context(mock.patch.object(bootstrap, "installed_package_matches", return_value=False))
            stack.enter_context(mock.patch.object(bootstrap, "remove_mismatched_package"))
            install = stack.enter_context(mock.patch.object(bootstrap, "install_package"))
            verify = stack.enter_context(mock.patch.object(bootstrap, "verify_installation", return_value=Path("prefix/hoi4-agent-tools.cmd")))
            self.assertEqual(bootstrap.main(), 0)
            local.assert_called_once_with(Path("reviewed.tgz"))
            registry.assert_not_called()
            self.assertEqual(install.call_args.args[-1], Path("reviewed.tgz"))
            verify.assert_called_once_with(prefix)

    def test_registry_integrity_mismatch_fails_closed(self) -> None:
        with mock.patch.object(bootstrap, "npm", return_value='"sha512-wrong"'):
            with self.assertRaisesRegex(bootstrap.BootstrapError, "integrity"):
                bootstrap.verify_registry_integrity(Path("node.exe"), Path("npm.cmd"))

    def test_locked_native_library_reports_reconnect_without_echoing_output(self) -> None:
        result = mock.Mock(
            returncode=4294963214,
            stdout=b"",
            stderr=b"npm error code EBUSY\nnpm error dest retired/libvips-42.dll\nprivate-output-sentinel\n",
        )
        with mock.patch.object(bootstrap.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(bootstrap.BootstrapError, "reconnect existing HOI4 MCP clients") as caught:
                bootstrap.run(["node.exe", "npm-cli.js", "install"])
        self.assertNotIn("private-output-sentinel", str(caught.exception))

    def test_npm_warnings_on_stderr_do_not_break_json_results(self) -> None:
        result = mock.Mock(returncode=0, stdout=b'"sha512-abc"\n', stderr=b"npm warn config something\n")
        with mock.patch.object(bootstrap.subprocess, "run", return_value=result):
            self.assertEqual(bootstrap.run(["node.exe", "npm-cli.js", "view"]).strip(), '"sha512-abc"')

    def test_matching_installation_is_kept_without_npm(self) -> None:
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(bootstrap, "installed_package_matches", return_value=True))
            stack.enter_context(
                mock.patch.object(bootstrap, "resolve_node_and_npm", return_value=(Path("node.exe"), Path("npm.cmd")))
            )
            stack.enter_context(mock.patch.object(bootstrap, "user_prefix", return_value=Path("prefix")))
            stack.enter_context(mock.patch.object(bootstrap, "verify_registry_integrity"))
            stack.enter_context(
                mock.patch.object(bootstrap, "verify_installation", return_value=Path("prefix/hoi4-agent-tools.cmd"))
            )
            stack.enter_context(mock.patch.object(bootstrap, "platform_name", return_value="windows"))
            stack.enter_context(mock.patch.object(bootstrap.sys, "argv", ["bootstrap", "--quiet"]))
            npm = stack.enter_context(mock.patch.object(bootstrap, "npm"))
            self.assertEqual(bootstrap.main(), 0)
        npm.assert_not_called()

    def test_mismatched_installation_is_removed_before_a_clean_install(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            prefix = Path(temporary)
            package = prefix / "node_modules" / bootstrap.PACKAGE_NAME
            (package / "node_modules" / "is-glob").mkdir(parents=True)

            def uninstall(_node, _npm, arguments, timeout=900):
                self.assertEqual(arguments[0], "uninstall")
                self.assertIn("--global", arguments)
                self.assertIn("--ignore-scripts", arguments)
                self.assertEqual(arguments[-1], bootstrap.PACKAGE_NAME)
                __import__("shutil").rmtree(package)
                return ""

            with mock.patch.object(bootstrap, "npm", side_effect=uninstall) as npm:
                bootstrap.remove_mismatched_package(Path("node.exe"), Path("npm.cmd"), prefix)
            npm.assert_called_once()
            self.assertFalse(package.exists())

    def test_a_package_that_cannot_be_removed_asks_to_close_mcp_clients(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            prefix = Path(temporary)
            (prefix / "node_modules" / bootstrap.PACKAGE_NAME).mkdir(parents=True)
            with mock.patch.object(bootstrap, "npm", return_value=""):
                with self.assertRaisesRegex(bootstrap.BootstrapError, "reconnect existing HOI4 MCP clients"):
                    bootstrap.remove_mismatched_package(Path("node.exe"), Path("npm.cmd"), prefix)

    def test_an_absent_installation_needs_no_removal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(bootstrap, "npm") as npm:
                bootstrap.remove_mismatched_package(Path("node.exe"), Path("npm.cmd"), Path(temporary))
            npm.assert_not_called()

    def test_installed_package_requires_exact_lock_and_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            prefix = Path(temporary)
            package = prefix / "node_modules" / bootstrap.PACKAGE_NAME
            entry = package / bootstrap.RUNTIME_ENTRY
            entry.parent.mkdir(parents=True)
            entry.write_bytes(b"verified-entry")
            (package / "package.json").write_text(
                json.dumps({"name": bootstrap.PACKAGE_NAME, "version": bootstrap.PACKAGE_VERSION}),
                encoding="utf-8",
            )
            (prefix / "node_modules" / ".package-lock.json").write_text(
                json.dumps(
                    {
                        "packages": {
                            f"node_modules/{bootstrap.PACKAGE_NAME}": {
                                "integrity": bootstrap.PACKAGE_INTEGRITY
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            (prefix / "hoi4-agent-tools.cmd").write_text("@echo off\n", encoding="utf-8")
            tree_digest, file_count = bootstrap.package_tree_sha256(package)
            with mock.patch.object(bootstrap, "RUNTIME_ENTRY_SIZE", len(b"verified-entry")), \
                mock.patch.object(bootstrap, "RUNTIME_ENTRY_SHA256", __import__("hashlib").sha256(b"verified-entry").hexdigest()), \
                mock.patch.object(bootstrap, "PACKAGE_TREE_SHA256", tree_digest), \
                mock.patch.object(bootstrap, "PACKAGE_FILE_COUNT", file_count):
                wrapper = bootstrap.verify_installation(prefix)
            self.assertEqual(wrapper, prefix / "hoi4-agent-tools.cmd")

    def test_missing_optional_npm_lock_still_requires_exact_full_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            prefix = Path(temporary)
            package = prefix / "node_modules" / bootstrap.PACKAGE_NAME
            entry = package / bootstrap.RUNTIME_ENTRY
            entry.parent.mkdir(parents=True)
            entry.write_bytes(b"verified-entry")
            (package / "package.json").write_text(
                json.dumps({"name": bootstrap.PACKAGE_NAME, "version": bootstrap.PACKAGE_VERSION}),
                encoding="utf-8",
            )
            (prefix / "hoi4-agent-tools.cmd").write_text("@echo off\n", encoding="utf-8")
            tree_digest, file_count = bootstrap.package_tree_sha256(package)
            with mock.patch.object(bootstrap, "RUNTIME_ENTRY_SIZE", len(b"verified-entry")), \
                mock.patch.object(bootstrap, "RUNTIME_ENTRY_SHA256", __import__("hashlib").sha256(b"verified-entry").hexdigest()), \
                mock.patch.object(bootstrap, "PACKAGE_TREE_SHA256", tree_digest), \
                mock.patch.object(bootstrap, "PACKAGE_FILE_COUNT", file_count):
                wrapper = bootstrap.verify_installation(prefix)
            self.assertEqual(wrapper, prefix / "hoi4-agent-tools.cmd")

    def test_manifest_and_bootstrap_identity_agree(self) -> None:
        manifest = json.loads((ROOT / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8"))
        component = next(item for item in manifest["components"] if item["id"] == "mcp.hoi4_agent_tools")
        parameters = next(rule for rule in component["validation"] if rule["id"] == "mcp.hoi4.health")["parameters"]
        self.assertEqual(parameters["package_name"], bootstrap.PACKAGE_NAME)
        self.assertEqual(parameters["package_version"], bootstrap.PACKAGE_VERSION)
        self.assertEqual(parameters["package_integrity"], bootstrap.PACKAGE_INTEGRITY)
        self.assertEqual(parameters["package_tree_sha256"], bootstrap.PACKAGE_TREE_SHA256)
        self.assertEqual(parameters["package_file_count"], bootstrap.PACKAGE_FILE_COUNT)
        self.assertEqual(parameters["runtime_entry"], bootstrap.RUNTIME_ENTRY)
        self.assertEqual(parameters["runtime_entry_sha256"], bootstrap.RUNTIME_ENTRY_SHA256)
        self.assertEqual(parameters["runtime_entry_size"], bootstrap.RUNTIME_ENTRY_SIZE)
        self.assertEqual(parameters["required_tools"], list(pin.REQUIRED_TOOLS))
        self.assertEqual(len(parameters["required_tools"]), 28)
        self.assertEqual(len(set(parameters["required_tools"])), 28)

    def test_repin_rejects_malformed_integrity_before_reading_package(self) -> None:
        for integrity in ("sha256-wrong", "sha512-???", "sha512-YWJj", "sha512-" + "A" * 88):
            with self.subTest(integrity=integrity), self.assertRaises(ValueError):
                pin.measure(Path("absent-prefix"), integrity)

    def test_repin_measures_clean_tree_and_rejects_wrong_lock_or_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            prefix = Path(temporary)
            package = prefix / "node_modules/hoi4-agent-tools"
            entry = package / "dist/bin/stdio.js"
            entry.parent.mkdir(parents=True)
            entry.write_bytes(b"synthetic runtime")
            metadata = package / "package.json"
            metadata.write_text(json.dumps({"name": "hoi4-agent-tools", "version": bootstrap.PACKAGE_VERSION}), encoding="utf-8")
            integrity = "sha512-" + __import__("base64").b64encode(b"s" * 64).decode("ascii")
            lock = prefix / "node_modules/.package-lock.json"
            lock.write_text(json.dumps({"packages": {"node_modules/hoi4-agent-tools": {"integrity": integrity}}}), encoding="utf-8")
            evidence = pin.measure(prefix, integrity, platform="windows")
            self.assertEqual(evidence["package_file_count"], 2)
            self.assertEqual(evidence["runtime_entry_size"], len(b"synthetic runtime"))
            self.assertEqual(evidence["runtime_entry_sha256"], __import__("hashlib").sha256(b"synthetic runtime").hexdigest())
            self.assertEqual(len(evidence["required_tools"]), 28)
            lock.write_text(json.dumps({"packages": {}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "lock"):
                pin.measure(prefix, integrity, platform="windows")
            for packages in ([], "invalid", {"node_modules/hoi4-agent-tools": []}, {"node_modules/hoi4-agent-tools": {"integrity": "sha512-wrong"}}):
                lock.write_text(json.dumps({"packages": packages}), encoding="utf-8")
                with self.subTest(packages=packages), self.assertRaisesRegex(ValueError, "lock"):
                    pin.measure(prefix, integrity, platform="windows")
            lock.write_text("{malformed JSON", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "malformed"):
                pin.measure(prefix, integrity, platform="windows")
            metadata.write_text(json.dumps({"name": "hoi4-agent-tools", "version": "3.10.0"}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, bootstrap.PACKAGE_VERSION):
                pin.measure(prefix, integrity, platform="windows")

    def test_repin_without_optional_lock_still_measures_full_tree_and_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            prefix = Path(temporary)
            package = prefix / "node_modules/hoi4-agent-tools"
            entry = package / "dist/bin/stdio.js"
            entry.parent.mkdir(parents=True)
            entry.write_bytes(b"synthetic runtime")
            (package / "package.json").write_text(json.dumps({"name": "hoi4-agent-tools", "version": bootstrap.PACKAGE_VERSION}), encoding="utf-8")
            integrity = "sha512-" + __import__("base64").b64encode(b"s" * 64).decode("ascii")
            self.assertFalse((prefix / "node_modules/.package-lock.json").exists())
            before = pin.measure(prefix, integrity, platform="windows")
            self.assertEqual(before["package_file_count"], 2)
            self.assertEqual(before["runtime_entry_size"], len(b"synthetic runtime"))
            self.assertEqual(before["runtime_entry_sha256"], __import__("hashlib").sha256(entry.read_bytes()).hexdigest())
            (package / "dist/helper.js").write_bytes(b"synthetic imported module")
            after = pin.measure(prefix, integrity, platform="windows")
            self.assertEqual(after["package_file_count"], 3)
            self.assertNotEqual(before["package_tree_sha256"], after["package_tree_sha256"])
            self.assertEqual(before["runtime_entry_sha256"], after["runtime_entry_sha256"])

    def test_repin_updates_only_reviewed_identity_and_tool_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "bootstrap.py"
            manifest_path = Path(temporary) / "manifest.json"
            source.write_bytes(SCRIPT.read_bytes())
            manifest_path.write_bytes((ROOT / "hoi4-mod-setup.manifest.json").read_bytes())
            original = json.loads(manifest_path.read_text(encoding="utf-8"))
            evidence = {
                "package_name": "hoi4-agent-tools", "package_version": "4.0.0",
                "package_integrity": "sha512-synthetic", "package_tree_sha256": "a" * 64,
                "package_file_count": 12, "runtime_entry": "dist/bin/stdio.js",
                "runtime_entry_sha256": "b" * 64, "runtime_entry_size": 123,
                "required_tools": list(pin.REQUIRED_TOOLS),
            }
            pin.repin(evidence, source, manifest_path)
            updated = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["generated_for_revision"], original["generated_for_revision"])
            self.assertEqual(updated["components"][0], original["components"][0])
            component = next(item for item in updated["components"] if item["id"] == "mcp.hoi4_agent_tools")
            health = next(rule for rule in component["validation"] if rule["id"] == "mcp.hoi4.health")["parameters"]
            for key, value in evidence.items():
                self.assertEqual(health[key], value)
            self.assertIn('PACKAGE_TREE_SHA256 = "' + "a" * 64 + '"', source.read_text(encoding="utf-8"))

    def test_repin_missing_constant_refuses_all_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "bootstrap.py"
            manifest_path = Path(temporary) / "manifest.json"
            source.write_text("# incomplete bootstrap\n", encoding="utf-8")
            manifest_path.write_bytes((ROOT / "hoi4-mod-setup.manifest.json").read_bytes())
            before = (source.read_bytes(), manifest_path.read_bytes())
            with self.assertRaisesRegex(ValueError, "constant"):
                pin.repin({"package_version": "4.0.0"}, source, manifest_path)
            self.assertEqual((source.read_bytes(), manifest_path.read_bytes()), before)

    def test_imported_module_mutation_changes_package_tree_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "dist/bin").mkdir(parents=True)
            (root / "dist/bin/stdio.js").write_text("import '../core.js'\n", encoding="utf-8")
            sibling = root / "dist/core.js"
            sibling.write_text("export const value = 1\n", encoding="utf-8")
            before = bootstrap.package_tree_sha256(root)
            sibling.write_text("export const value = 2\n", encoding="utf-8")
            after = bootstrap.package_tree_sha256(root)
            self.assertNotEqual(before, after)


if __name__ == "__main__":
    unittest.main()
