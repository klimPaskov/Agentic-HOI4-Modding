from __future__ import annotations

import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".tools" / "image_generation" / "providers" / "gptimage"))
import bootstrap as bootstrap_gptimage


class GptimageBootstrapTests(unittest.TestCase):
    def make_package(self, root: Path) -> Path:
        package = root / "gptimage"
        (package / "src").mkdir(parents=True)
        (package / "package.json").write_text(json.dumps({"name": "gptimage", "version": "0.1.0"}), encoding="utf-8")
        (package / "package-lock.json").write_text("{}\n", encoding="utf-8")
        (package / "src" / "server.js").write_text("server\n", encoding="utf-8")
        return package

    def test_uses_frozen_lock_and_removes_temporary_npm_cache(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package(Path(directory))
            calls = []

            def fake_run(args, **kwargs):
                calls.append((args, kwargs))
                cache = Path(args[args.index("--cache") + 1])
                (package / "node_modules" / "@modelcontextprotocol" / "sdk").mkdir(parents=True)
                (package / "node_modules" / "@modelcontextprotocol" / "sdk" / "package.json").write_text("{}", encoding="utf-8")
                self.assertTrue(cache.is_dir())
                return SimpleNamespace(returncode=0, stdout="", stderr="")

            result = bootstrap_gptimage.install(
                package,
                fake_run,
                expected_tree_sha256=bootstrap_gptimage.source_tree_sha256(package),
                expected_lock_sha256=hashlib.sha256((package / "package-lock.json").read_bytes()).hexdigest(),
            )
            self.assertEqual(result, {"status": "ready", "package": "gptimage", "version": "0.1.0"})
            args, kwargs = calls[0]
            self.assertEqual(args[:2], ["npm", "ci"])
            self.assertIn("--ignore-scripts", args)
            self.assertIn("--no-audit", args)
            self.assertNotIn("shell", kwargs)
            self.assertFalse(Path(args[args.index("--cache") + 1]).exists())

    def test_rejects_an_unexpected_package_before_running_npm(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package(Path(directory))
            (package / "package.json").write_text(json.dumps({"name": "other", "version": "0.1.0"}), encoding="utf-8")
            called = False

            def fake_run(*args, **kwargs):
                nonlocal called
                called = True
                return SimpleNamespace(returncode=0, stdout="", stderr="")

            with self.assertRaisesRegex(RuntimeError, "does not match"):
                bootstrap_gptimage.install(package, fake_run)
            self.assertFalse(called)

    def test_rejects_changed_source_and_lockfile_before_running_npm(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package(Path(directory))
            expected_tree = bootstrap_gptimage.source_tree_sha256(package)
            expected_lock = hashlib.sha256((package / "package-lock.json").read_bytes()).hexdigest()
            (package / "src" / "server.js").write_text("changed\n", encoding="utf-8")
            called = False

            def fake_run(*args, **kwargs):
                nonlocal called
                called = True
                return SimpleNamespace(returncode=0, stdout="", stderr="")

            with self.assertRaisesRegex(RuntimeError, "source tree"):
                bootstrap_gptimage.install(package, fake_run, expected_tree_sha256=expected_tree)
            self.assertFalse(called)
            (package / "src" / "server.js").write_text("server\n", encoding="utf-8")
            (package / "package-lock.json").write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "lockfile"):
                bootstrap_gptimage.install(package, fake_run, expected_lock_sha256=expected_lock)
            self.assertFalse(called)

    def test_install_errors_do_not_return_dependency_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package(Path(directory))

            def fake_run(*args, **kwargs):
                return SimpleNamespace(returncode=1, stdout="private output", stderr="token=private-value")

            with self.assertRaisesRegex(RuntimeError, "could not be installed") as error:
                bootstrap_gptimage.install(package, fake_run)
            self.assertNotIn("private-value", str(error.exception))


if __name__ == "__main__":
    unittest.main()
