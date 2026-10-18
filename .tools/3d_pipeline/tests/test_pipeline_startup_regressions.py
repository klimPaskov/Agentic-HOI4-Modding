"""Provider-free regressions for defects that blocked the first end-to-end pipeline run."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PIPELINE_ROOT.parents[1]
ADAPTER_ROOT = PIPELINE_ROOT / "adapter"
ADAPTER_MODULE = ADAPTER_ROOT / "hoi4_blender_mcp.py"
sys.path.insert(0, str(PIPELINE_ROOT))

import bootstrap_3d_workflow as bootstrap  # noqa: E402
import verify_environment  # noqa: E402
from lib import paths  # noqa: E402
from lib.mcp_stdio import MCPRouteError  # noqa: E402


# A minimal stand-in for the mcp 1.x FastMCP surface the adapter imports. It
# refuses duplicate registrations and reports what main() would serve.
FASTMCP_STUB = textwrap.dedent(
    """
    import json
    import sys


    class FastMCP:
        def __init__(self, name):
            self.name = name
            self.tools = []

        def tool(self):
            def register(function):
                if function.__name__ in self.tools:
                    raise RuntimeError(f"duplicate tool registration: {function.__name__}")
                self.tools.append(function.__name__)
                return function
            return register

        def run(self, transport):
            sys.stdout.write(json.dumps({"transport": transport, "tools": self.tools}) + "\\n")
    """
)


def adapter_tool_functions() -> list[str]:
    tree = ast.parse(ADAPTER_MODULE.read_text(encoding="utf-8"))
    return [
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("hoi4_blender_")
    ]


class AdapterHarness:
    """Run the real adapter module against a stub FastMCP and a temporary config."""

    def __init__(self, repo_root: Path = REPO_ROOT) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.root = Path(self._temp.name)
        stub = self.root / "stub" / "mcp" / "server" / "fastmcp"
        stub.mkdir(parents=True)
        for package in (stub.parents[1], stub.parent):
            (package / "__init__.py").write_text("", encoding="utf-8")
        (stub / "__init__.py").write_text(FASTMCP_STUB, encoding="utf-8")
        self.config = self.root / "blender_hoi4_adapter.json"
        self.config.write_text(
            json.dumps(
                {
                    "adapter_version": "test",
                    "job_root": str(self.root / "jobs"),
                    "blender_executable": str(self.root / "blender.exe"),
                    "io_pdx_mesh_root": str(self.root / "io_pdx_mesh"),
                    "operations": [],
                    "source_files_sha256": {
                        path.name: hashlib.sha256(path.read_bytes()).hexdigest().upper()
                        for path in ADAPTER_ROOT.glob("*.py")
                    },
                }
            ),
            encoding="utf-8",
        )

    def close(self) -> None:
        self._temp.cleanup()

    def run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        env = {
            key: value
            for key, value in os.environ.items()
            if key not in {"PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP"}
        }
        env["PYTHONPATH"] = os.pathsep.join([str(self.root / "stub"), str(ADAPTER_ROOT)])
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["HOI4_3D_CONFIG"] = str(self.config)
        return subprocess.run(
            [sys.executable, *arguments],
            cwd=str(self.root),
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )


class AdapterDependencyBoundTests(unittest.TestCase):
    """Defect 1: an unbounded mcp requirement resolved 2.x, which removed FastMCP."""

    def test_mcp_requirement_excludes_the_2x_api(self) -> None:
        pyproject = (ADAPTER_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        requirements = re.findall(r'^\s*"(mcp(?:\[[^\]]*\])?[^"]*)"', pyproject, re.MULTILINE)
        self.assertEqual(len(requirements), 1, requirements)
        specifiers = [item.strip().replace(" ", "") for item in requirements[0].split("]", 1)[-1].split(",")]
        upper = [item for item in specifiers if item.startswith("<")]
        self.assertTrue(upper, f"mcp has no upper bound: {requirements[0]}")
        major = [int(match.group(1)) for item in upper if (match := re.fullmatch(r"<(\d+)(?:\.0)*", item))]
        self.assertTrue(major and max(major) <= 2, f"mcp upper bound admits 2.x: {requirements[0]}")

    def test_adapter_uses_the_bounded_fastmcp_api(self) -> None:
        source = ADAPTER_MODULE.read_text(encoding="utf-8")
        self.assertIn("from mcp.server.fastmcp import FastMCP", source)


class ConverterResolutionTests(unittest.TestCase):
    """Defect 2: run_pilot.py called a converter in the removed hoi4-event-assets skill."""

    def test_pipeline_sources_do_not_reference_the_removed_skill(self) -> None:
        for path in (PIPELINE_ROOT / "run_pilot.py", ADAPTER_MODULE):
            with self.subTest(path=path.name):
                self.assertNotIn("hoi4-event-assets", path.read_text(encoding="utf-8"))

    def test_run_pilot_resolves_the_converter_from_the_owning_skill(self) -> None:
        source = (PIPELINE_ROOT / "run_pilot.py").read_text(encoding="utf-8")
        self.assertNotIn('"convert_to_dds.py"', source)
        self.assertEqual(source.count("dds_converter()"), 2)
        converter = paths.dds_converter()
        self.assertTrue(converter.is_file())
        self.assertEqual(converter.parent.parent.name, "hoi4-feature-assets")

    def test_converter_resolution_follows_each_runtime_skill_root(self) -> None:
        relative = Path("hoi4-feature-assets/tools/convert_to_dds.py")
        for skill_root in (".claude/skills", ".agents/skills", ".qoder/skills"):
            with self.subTest(skill_root=skill_root), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                converter = root / skill_root / relative
                converter.parent.mkdir(parents=True)
                converter.write_text("", encoding="utf-8")
                self.assertEqual(paths.dds_converter(root), converter.resolve())

    def test_missing_converter_names_every_searched_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError) as raised:
                paths.dds_converter(Path(temp))
        message = str(raised.exception)
        for skill_root in (".claude", ".agents", ".qoder"):
            self.assertIn(skill_root, message)

    def test_adapter_resolves_the_converter_without_the_codex_mirror(self) -> None:
        harness = AdapterHarness()
        try:
            completed = harness.run(
                "-c",
                "import hoi4_blender_mcp as adapter; print(adapter._dds_converter().as_posix())",
            )
        finally:
            harness.close()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(Path(completed.stdout.strip()), paths.dds_converter())


class DependencyLockRerunTests(unittest.TestCase):
    """Defect 3: a successful bootstrap rewrote the lock without the io_pdx_mesh evidence."""

    def payload(self) -> dict:
        return {
            "resolved_at_utc": "2026-10-18T00:00:00Z",
            "meshy": {},
            "meshy_tool_contract": {},
            "blender_mcp": {},
            "blender_mcp_project": "project",
            "blender_hoi4_adapter": {},
            "blender_mcp_addon": {},
            "blender_bridge": {},
            "blender_executable": "blender.exe",
            "blender_shortcut": None,
            "blender_version": "5.2.0",
            "io_pdx_mesh": {},
        }

    def test_second_bootstrap_reads_its_own_dependency_record(self) -> None:
        checked_in = json.loads((PIPELINE_ROOT / "config/dependencies.lock.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pipeline_root = root / ".tools/3d_pipeline"
            (pipeline_root / "config").mkdir(parents=True)
            shutil.copyfile(
                PIPELINE_ROOT / "config/dependencies.lock.json",
                pipeline_root / "config/dependencies.lock.json",
            )
            first = bootstrap.resolve_io_pdx_mesh(pipeline_root)
            for _ in range(2):
                bootstrap.write_dependency_record(root, self.payload())
                rerun = bootstrap.resolve_io_pdx_mesh(pipeline_root)
                self.assertEqual(rerun["compatibility"], first["compatibility"])
            written = json.loads((pipeline_root / "config/dependencies.lock.json").read_text(encoding="utf-8"))
        self.assertEqual(written["compatibility"], checked_in["compatibility"])
        self.assertEqual(written["sources"], checked_in["sources"])
        self.assertEqual(written["resolution_policy"], "latest_at_bootstrap")

    def test_record_never_invents_missing_compatibility_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bootstrap.write_dependency_record(root, self.payload())
            with self.assertRaisesRegex(bootstrap.SetupError, "compatibility evidence is missing"):
                bootstrap.resolve_io_pdx_mesh(root / ".tools/3d_pipeline")

    def test_main_reads_the_lock_from_the_selected_project(self) -> None:
        tree = ast.parse((PIPELINE_ROOT / "bootstrap_3d_workflow.py").read_text(encoding="utf-8"))
        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
        calls = [
            node
            for node in ast.walk(main)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "resolve_io_pdx_mesh"
        ]
        self.assertEqual(len(calls), 1)
        self.assertEqual([ast.unparse(argument) for argument in calls[0].args], ["pipeline_root"])


class AdapterStartupProbeTests(unittest.TestCase):
    """Defect 4: verify_environment.py passed the adapter route without starting it."""

    def materialized_root(self, temp: str) -> Path:
        root = Path(temp)
        pipeline_root = root / ".tools/3d_pipeline"
        (pipeline_root / "config").mkdir(parents=True)
        (pipeline_root / "wrappers").mkdir()
        (pipeline_root / "config/blender_hoi4_adapter.json").write_text("{}", encoding="utf-8")
        (pipeline_root / "wrappers/run_blender_hoi4_adapter.cmd").write_text("", encoding="utf-8")
        return root

    def listed(self, names: list[str]) -> dict:
        return {"tools": [{"name": name} for name in names]}

    def test_probe_starts_the_wrapper_and_lists_the_served_tools(self) -> None:
        expected = sorted(adapter_tool_functions())
        with tempfile.TemporaryDirectory() as temp:
            root = self.materialized_root(temp)
            with mock.patch.object(verify_environment, "WINDOWS", True), mock.patch.object(
                verify_environment, "call_stdio", return_value=self.listed(expected)
            ) as call:
                result, findings = verify_environment.probe_blender_adapter(root, expected)
        self.assertEqual(findings, [])
        self.assertEqual(result["status"], "probed")
        self.assertEqual(result["tools"], expected)
        command = call.call_args.args[0]
        self.assertEqual(command[:4], ["cmd.exe", "/d", "/c", "call"])
        self.assertEqual(
            Path(command[4]),
            (root / ".tools/3d_pipeline/wrappers/run_blender_hoi4_adapter.cmd").resolve(),
        )
        self.assertTrue(call.call_args.kwargs["list_tools"])
        self.assertEqual(call.call_args.kwargs["cwd"], root.resolve())

    def test_startup_failure_blocks_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.materialized_root(temp)
            with mock.patch.object(verify_environment, "WINDOWS", True), mock.patch.object(
                verify_environment,
                "call_stdio",
                side_effect=MCPRouteError("stdout EOF: NameError: name 'main' is not defined"),
            ):
                result, findings = verify_environment.probe_blender_adapter(root, ["hoi4_blender_health"])
        self.assertEqual(result["status"], "failed")
        self.assertEqual(len(findings), 1)
        self.assertIn("Blender adapter failed to start", findings[0])
        self.assertIn("NameError", findings[0])

    def test_served_tools_must_match_the_checked_in_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.materialized_root(temp)
            with mock.patch.object(verify_environment, "WINDOWS", True), mock.patch.object(
                verify_environment,
                "call_stdio",
                return_value=self.listed(["hoi4_blender_health", "hoi4_blender_unknown"]),
            ):
                result, findings = verify_environment.probe_blender_adapter(
                    root, ["hoi4_blender_health", "hoi4_blender_inspect_scene"]
                )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(len(findings), 1)
        self.assertIn("hoi4_blender_inspect_scene", findings[0])
        self.assertIn("hoi4_blender_unknown", findings[0])

    def test_unmaterialized_adapter_is_reported_not_passed(self) -> None:
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(verify_environment, "call_stdio") as call:
            result, findings = verify_environment.probe_blender_adapter(Path(temp), ["hoi4_blender_health"])
            required, required_findings = verify_environment.probe_blender_adapter(
                Path(temp), ["hoi4_blender_health"], required=True
            )
        call.assert_not_called()
        self.assertEqual(result["status"], "not_materialized")
        self.assertEqual(findings, [])
        self.assertEqual(required["status"], "not_materialized")
        self.assertEqual(len(required_findings), 1)

    def test_main_reports_the_adapter_probe(self) -> None:
        probe = mock.Mock(return_value=({"status": "failed"}, ["Blender adapter failed to start: boom"]))
        with mock.patch.object(verify_environment, "probe_blender_adapter", probe), mock.patch.object(
            sys, "argv", ["verify_environment.py"]
        ), mock.patch("builtins.print") as printed:
            exit_code = verify_environment.main()
        self.assertEqual(exit_code, 1)
        report = json.loads(printed.call_args.args[0])
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(report["blender_adapter"], {"status": "failed"})
        self.assertIn("Blender adapter failed to start: boom", report["findings"])


class AdapterEntryPointTests(unittest.TestCase):
    """Defect 5: a premature __main__ block raised NameError; one tool registered twice."""

    def test_module_entry_point_serves_every_tool_once(self) -> None:
        harness = AdapterHarness()
        try:
            completed = harness.run("-m", "hoi4_blender_mcp")
        finally:
            harness.close()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        served = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertEqual(served["transport"], "stdio")
        self.assertEqual(sorted(served["tools"]), sorted(adapter_tool_functions()))

    def test_main_guard_is_last_and_follows_main(self) -> None:
        tree = ast.parse(ADAPTER_MODULE.read_text(encoding="utf-8"))
        guards = [
            index
            for index, node in enumerate(tree.body)
            if isinstance(node, ast.If) and ast.unparse(node.test) == "__name__ == '__main__'"
        ]
        main = [
            index
            for index, node in enumerate(tree.body)
            if isinstance(node, ast.FunctionDef) and node.name == "main"
        ]
        self.assertEqual(guards, [len(tree.body) - 1])
        self.assertEqual(len(main), 1)
        self.assertLess(main[0], guards[0])

    def test_each_tool_is_defined_and_registered_once(self) -> None:
        tree = ast.parse(ADAPTER_MODULE.read_text(encoding="utf-8"))
        names = adapter_tool_functions()
        self.assertEqual(len(names), len(set(names)))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("hoi4_blender_"):
                with self.subTest(tool=node.name):
                    decorators = [ast.unparse(item) for item in node.decorator_list]
                    self.assertEqual(decorators, ["mcp.tool()"])

    def test_verify_environment_rejects_duplicate_registrations(self) -> None:
        source = textwrap.dedent(
            """
            @mcp.tool()
            @mcp.tool()
            def hoi4_blender_example():
                pass
            """
        )
        with self.assertRaisesRegex(ValueError, "hoi4_blender_example"):
            verify_environment.registered_tools(source)

    def test_adapter_children_never_inherit_the_mcp_stdin(self) -> None:
        tree = ast.parse(ADAPTER_MODULE.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and ast.unparse(node.func) in {"subprocess.run", "subprocess.Popen"}:
                with self.subTest(line=node.lineno):
                    stdin = [ast.unparse(item.value) for item in node.keywords if item.arg == "stdin"]
                    self.assertEqual(stdin, ["subprocess.DEVNULL"])


if __name__ == "__main__":
    unittest.main()
