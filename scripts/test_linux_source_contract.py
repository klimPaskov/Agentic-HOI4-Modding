"""Native platform evidence, bounded paths, schema gates and vault contracts."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from jsonschema import Draft202012Validator
from manifest_schema import load_manifest_schema

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


bootstrap = module("linux_source_bootstrap", ".tools/mcp/bootstrap_hoi4_agent_tools.py")
images = module("linux_source_images", ".tools/image_generation/runtime/server.py")


class LinuxSourceContractTests(unittest.TestCase):
    def test_schema_major_five_is_explicit_and_unknown_majors_fail(self):
        for version in ("3.0.0", "4.0.0", "5.0.0"):
            Draft202012Validator.check_schema(load_manifest_schema(version, ROOT))
        for version in ("6.0.0", "5", "5.0.0-extra", None):
            with self.assertRaises(ValueError):
                load_manifest_schema(version, ROOT)
        manifest = json.loads((ROOT / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(load_manifest_schema("5.0.0", ROOT))
        validator.validate(manifest)
        health = next(v for c in manifest["components"] for v in c.get("validation", []) if v["id"] == "mcp.hoi4.health")
        health["parameters"]["platform_pins"]["linux"].pop("package_symlinks")
        self.assertTrue(list(validator.iter_errors(manifest)))

    def test_linux_prefix_uses_only_absolute_current_user_data(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(bootstrap, "platform_name", return_value="linux"):
            root = Path(directory)
            with mock.patch.dict(os.environ, {"XDG_DATA_HOME": str(root)}, clear=True):
                self.assertEqual(bootstrap.user_prefix(), root.resolve() / "hoi4-mod-setup/npm")
                self.assertEqual(bootstrap.modules_directory(bootstrap.user_prefix()), root.resolve() / "hoi4-mod-setup/npm/lib/node_modules")
            for value in ("relative", "bad\0path", "a" * 4097):
                with mock.patch.object(bootstrap.os, "environ", {"XDG_DATA_HOME": value}), self.assertRaises(bootstrap.BootstrapError):
                    bootstrap.user_prefix()
            with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(bootstrap.Path, "home", return_value=root):
                self.assertEqual(bootstrap.user_prefix(), root.resolve() / ".local/share/hoi4-mod-setup/npm")

    def test_platform_manifest_pins_match_the_bootstrap(self):
        manifest = json.loads((ROOT / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8"))
        health = next(v for c in manifest["components"] for v in c.get("validation", []) if v["id"] == "mcp.hoi4.health")
        self.assertEqual(health["parameters"]["platform_targets"], {"windows": "hoi4-agent-tools.cmd", "linux": "hoi4-agent-tools"})
        for platform in ("windows", "linux"):
            self.assertEqual(health["parameters"]["platform_pins"][platform], bootstrap.platform_evidence(platform))
        self.assertNotEqual(bootstrap.platform_evidence("linux")["package_tree_sha256"], bootstrap.platform_evidence("windows")["package_tree_sha256"])

    def test_native_node_and_npm_discovery_is_shell_free(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            node = root / "node"
            cli = root / "npm-cli.js"
            node.write_bytes(b"fixture")
            cli.write_bytes(b"fixture")
            with mock.patch.object(bootstrap, "platform_name", return_value="linux"), mock.patch.object(bootstrap.shutil, "which", side_effect=[str(node), str(cli)]), mock.patch.object(bootstrap, "run", side_effect=["v22.23.3", "x64"]):
                self.assertEqual(bootstrap.resolve_node_and_npm(), (node.resolve(), cli.resolve()))
            with mock.patch.object(bootstrap, "platform_name", return_value="linux"), mock.patch.object(bootstrap, "run", return_value="{}") as run:
                runtime = bootstrap.PinnedNpm(root, cli, {})
                bootstrap.npm(node, runtime, ["view", bootstrap.PACKAGE_SPEC])
            self.assertEqual(run.call_args.args[0][:2], [str(node), str(cli)])
            self.assertEqual(run.call_args.args[0][-2:], ["view", bootstrap.PACKAGE_SPEC])
            self.assertEqual(run.call_args.kwargs["cwd"], root)
            with mock.patch.object(bootstrap, "platform_name", return_value="linux"), mock.patch.object(bootstrap.shutil, "which", side_effect=[str(node), str(cli)]), mock.patch.object(bootstrap, "run", return_value="v18.19.1"), self.assertRaisesRegex(bootstrap.BootstrapError, "22.19"):
                bootstrap.resolve_node_and_npm()

    def test_linux_vault_uses_exact_app_secret_service_attributes(self):
        reference = "credential://image_generation_api_key/project_openai_api_key"
        completed = mock.Mock(returncode=0, stdout=b"synthetic-only\n")
        with mock.patch.object(images.subprocess, "run", return_value=completed) as run:
            self.assertEqual(images._linux_credential(reference), "synthetic-only")
        self.assertEqual(run.call_args.args[0], ["/usr/bin/secret-tool", "lookup", "target", "default", "service", "com.klimpaskov.hoi4-mod-setup", "username", reference])
        self.assertEqual(run.call_args.kwargs["stderr"], images.subprocess.DEVNULL)
        with mock.patch.object(images.subprocess, "run", side_effect=OSError("unavailable")):
            self.assertIsNone(images._linux_credential(reference))

    @unittest.skipUnless(sys.platform.startswith("linux"), "Native symlink fixtures require Linux")
    def test_only_exact_reviewed_file_links_are_included_in_the_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "node_modules/semver/bin/semver.js"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"reviewed source")
            link = root / "node_modules/.bin/semver"
            link.parent.mkdir(parents=True)
            link.symlink_to("../semver/bin/semver.js")
            allowed = {"node_modules/.bin/semver": "../semver/bin/semver.js"}
            digest, count = bootstrap.package_tree_sha256(root, allowed)
            self.assertEqual(count, 2)
            with self.assertRaisesRegex(bootstrap.BootstrapError, "unreviewed link"):
                bootstrap.package_tree_sha256(root, {})
            link.unlink()
            with self.assertRaisesRegex(bootstrap.BootstrapError, "missing a reviewed link"):
                bootstrap.package_tree_sha256(root, allowed)
            link.symlink_to("../semver/bin/semver.js")
            target.write_bytes(b"changed source")
            self.assertNotEqual(digest, bootstrap.package_tree_sha256(root, allowed)[0])
            link.unlink()
            link.symlink_to("/etc/passwd")
            with self.assertRaises(bootstrap.BootstrapError):
                bootstrap.package_tree_sha256(root, allowed)


if __name__ == "__main__":
    unittest.main()
