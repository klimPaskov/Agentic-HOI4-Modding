from __future__ import annotations

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


class McpBootstrapContractTests(unittest.TestCase):
    def test_public_release_identity_is_exact(self) -> None:
        self.assertEqual(bootstrap.PACKAGE_SPEC, "hoi4-agent-tools@2.5.2")
        self.assertTrue(bootstrap.PACKAGE_INTEGRITY.startswith("sha512-"))
        self.assertEqual(len(bootstrap.PACKAGE_TREE_SHA256), 64)
        self.assertEqual(bootstrap.PACKAGE_FILE_COUNT, 181)
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
        self.assertEqual(arguments[-1], "hoi4-agent-tools@2.5.2")

    def test_registry_integrity_mismatch_fails_closed(self) -> None:
        with mock.patch.object(bootstrap, "npm", return_value='"sha512-wrong"'):
            with self.assertRaisesRegex(bootstrap.BootstrapError, "integrity"):
                bootstrap.verify_registry_integrity(Path("node.exe"), Path("npm.cmd"))

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
