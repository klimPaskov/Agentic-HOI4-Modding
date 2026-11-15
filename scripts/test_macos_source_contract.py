"""The macOS route of the HOI4 Agent Tools bootstrap: prefix, private Node.js runtime and manifest pins."""

from __future__ import annotations

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


ROOT = Path(__file__).resolve().parents[1]


def module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


bootstrap = module("macos_source_bootstrap", ".tools/mcp/bootstrap_hoi4_agent_tools.py")
MEMBER = f"node-v{bootstrap.MACOS_NODE_VERSION}-darwin-arm64/bin/node"


def archive_bytes(content: bytes, *, link: bool = False) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        info = tarfile.TarInfo(MEMBER)
        if link:
            info.type = tarfile.SYMTYPE
            info.linkname = "/bin/sh"
            archive.addfile(info)
        else:
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))
        extra = tarfile.TarInfo(f"node-v{bootstrap.MACOS_NODE_VERSION}-darwin-arm64/bin/npm")
        extra.type = tarfile.SYMTYPE
        extra.linkname = "../lib/node_modules/npm/bin/npm-cli.js"
        archive.addfile(extra)
    return buffer.getvalue()


class MacosSourceContractTests(unittest.TestCase):
    def test_darwin_is_the_macos_platform_with_the_posix_layout(self):
        with mock.patch.object(bootstrap.os, "name", "posix"), mock.patch.object(bootstrap.sys, "platform", "darwin"):
            self.assertEqual(bootstrap.platform_name(), "macos")
            self.assertTrue(bootstrap.posix_layout())
        self.assertFalse(bootstrap.posix_layout("windows"))

    def test_macos_prefix_is_current_user_application_support(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(bootstrap, "platform_name", return_value="macos"):
            home = Path(directory)
            with mock.patch.object(bootstrap.Path, "home", return_value=home):
                prefix = bootstrap.user_prefix()
            self.assertEqual(prefix, home.resolve() / "Library/Application Support/hoi4-mod-setup/npm")
            self.assertEqual(bootstrap.modules_directory(prefix), prefix / "lib/node_modules")
            self.assertEqual(bootstrap.macos_node_path(prefix), prefix / "node/bin/node")

    def test_only_apple_silicon_has_a_reviewed_route(self):
        with mock.patch.object(bootstrap, "run", return_value="1\n"):
            self.assertEqual(bootstrap.macos_node_arch(), "arm64")
        with mock.patch.object(bootstrap, "run", side_effect=bootstrap.BootstrapError("no key")), self.assertRaisesRegex(bootstrap.BootstrapError, "Apple Silicon"):
            bootstrap.macos_node_arch()
        self.assertEqual(set(bootstrap.MACOS_NODE_BUILDS), {"arm64"})

    def test_macos_node_and_npm_toolchain_are_pinned(self):
        build = bootstrap.MACOS_NODE_BUILDS["arm64"]
        for key in ("archive_sha256", "binary_sha256"):
            self.assertRegex(build[key], r"^[0-9a-f]{64}$")
        self.assertGreater(build["binary_size"], 0)
        self.assertTrue(bootstrap.supported_node_version(f"v{bootstrap.MACOS_NODE_VERSION}"))
        self.assertEqual(bootstrap.NPM_TOOLCHAINS["macos"], bootstrap.NPM_TOOLCHAINS["linux"])
        self.assertEqual(bootstrap.MACOS_NODE_TEAM_ID, "HX7739G8FX")

    def private_node(self, content: bytes, archive: bytes):
        build = {
            "archive_sha256": hashlib.sha256(archive).hexdigest(),
            "binary_sha256": hashlib.sha256(content).hexdigest(),
            "binary_size": len(content),
        }
        downloads = []

        def download(arch, selected, destination):
            downloads.append(arch)
            destination.write_bytes(archive)
            if hashlib.sha256(archive).hexdigest() != selected["archive_sha256"]:
                raise bootstrap.BootstrapError("The pinned Node.js archive SHA-256 does not match.")

        patches = [
            mock.patch.object(bootstrap, "MACOS_NODE_BUILDS", {"arm64": build}),
            mock.patch.object(bootstrap, "macos_node_arch", return_value="arm64"),
            mock.patch.object(bootstrap, "download_macos_node_archive", side_effect=download),
            mock.patch.object(bootstrap, "verify_macos_node_signature"),
            mock.patch.object(bootstrap, "verify_node_runtime"),
        ]
        return patches, downloads

    def test_private_node_extracts_only_the_reviewed_executable_and_is_idempotent(self):
        content = b"#!fake node\n" * 64
        patches, downloads = self.private_node(content, archive_bytes(content))
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory).resolve() / "npm"
            with patches[0], patches[1], patches[2], patches[3] as signature, patches[4]:
                node = bootstrap.ensure_macos_node(prefix)
                self.assertEqual(node, prefix / "node/bin/node")
                self.assertEqual(node.read_bytes(), content)
                self.assertTrue(os.access(node, os.X_OK))
                self.assertEqual(sorted(path.name for path in node.parent.iterdir()), ["node"])
                bootstrap.ensure_macos_node(prefix)
                self.assertEqual(downloads, ["arm64"])
                self.assertEqual(signature.call_count, 2)
                node.write_bytes(b"tampered")
                bootstrap.ensure_macos_node(prefix)
                self.assertEqual(downloads, ["arm64", "arm64"])
                self.assertEqual(node.read_bytes(), content)

    def test_private_node_refuses_a_linked_executable_member(self):
        content = b"#!fake node\n"
        patches, _ = self.private_node(content, archive_bytes(content, link=True))
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory).resolve() / "npm"
            with patches[0], patches[1], patches[2], patches[3], patches[4], self.assertRaisesRegex(bootstrap.BootstrapError, "reviewed file"):
                bootstrap.ensure_macos_node(prefix)
            self.assertFalse((prefix / "node/bin/node").exists())

    def test_private_node_refuses_a_changed_archive(self):
        content = b"#!fake node\n"
        patches, _ = self.private_node(content, archive_bytes(content))
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory).resolve() / "npm"
            with patches[0] as builds, patches[1], patches[2], patches[3], patches[4]:
                builds["arm64"]["archive_sha256"] = "0" * 64
                with self.assertRaisesRegex(bootstrap.BootstrapError, "SHA-256"):
                    bootstrap.ensure_macos_node(prefix)
            self.assertFalse((prefix / "node/bin/node").exists())

    def test_signature_check_requires_the_node_foundation_developer_id(self):
        with mock.patch.object(bootstrap, "run", return_value="") as run:
            bootstrap.verify_macos_node_signature(Path("/tmp/node"))
        arguments = run.call_args.args[0]
        self.assertEqual(arguments[:3], ["/usr/bin/codesign", "--verify", "--strict"])
        self.assertIn('certificate leaf[subject.OU] = "HX7739G8FX"', arguments[3])
        self.assertIn("anchor apple generic", arguments[3])
        with mock.patch.object(bootstrap, "run", side_effect=bootstrap.BootstrapError("bad")), self.assertRaisesRegex(bootstrap.BootstrapError, "Node.js Foundation"):
            bootstrap.verify_macos_node_signature(Path("/tmp/node"))

    def test_macos_node_must_match_the_host_architecture(self):
        with mock.patch.object(bootstrap, "platform_name", return_value="macos"), mock.patch.object(bootstrap, "macos_node_arch", return_value="arm64"):
            with mock.patch.object(bootstrap, "run", side_effect=["v24.22.0", "arm64"]):
                bootstrap.verify_node_runtime(Path("/tmp/node"))
            with mock.patch.object(bootstrap, "run", side_effect=["v24.22.0", "x64"]), self.assertRaisesRegex(bootstrap.BootstrapError, "arm64"):
                bootstrap.verify_node_runtime(Path("/tmp/node"))

    def test_manifest_offers_agent_tools_and_every_client_registration_on_macos(self):
        manifest = json.loads((ROOT / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"].split(".")[0], "7")
        components = {component["id"]: component for component in manifest["components"]}
        for component_id in ("mcp.hoi4_agent_tools", "mcp.hoi4_agent_tools.bootstrap"):
            self.assertIn("macos", components[component_id]["platforms"])
        registrations = [component for component in components.values() if "mcp.hoi4_agent_tools" in component["dependencies"] and component["id"].endswith(".mcp")]
        self.assertGreaterEqual(len(registrations), 10)
        for component in registrations:
            self.assertIn("macos", component["platforms"], component["id"])
        health = next(rule for rule in components["mcp.hoi4_agent_tools"]["validation"] if rule["id"] == "mcp.hoi4.health")
        self.assertEqual(health["parameters"]["platform_targets"]["macos"], "hoi4-agent-tools")
        self.assertEqual(health["parameters"]["platform_pins"]["macos"], bootstrap.platform_evidence("macos"))
        self.assertNotEqual(bootstrap.platform_evidence("macos")["package_tree_sha256"], bootstrap.platform_evidence("linux")["package_tree_sha256"])


if __name__ == "__main__":
    unittest.main()
