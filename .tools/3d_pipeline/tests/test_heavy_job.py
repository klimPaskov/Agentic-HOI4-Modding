"""The machine-wide gate in front of every Blender start (lib/heavy_job.py), with a fake clock, a fake lock and no real sleep."""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import blender_client
from lib import heavy_job

GIB = heavy_job.GIB


class FakeClock:
    """Time that only `sleep` moves, and a count of the sleeps."""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps = 0

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds
        self.sleeps += 1


class FakeLock:
    """A lock that refuses the first `busy` attempts."""

    def __init__(self, busy: int = 0, holder: str = "4242 review_unit.py") -> None:
        self.busy, self.attempts, self.held, self.releases, self._holder = busy, 0, False, 0, holder

    def try_acquire(self, label: str) -> bool:
        self.attempts += 1
        if self.attempts <= self.busy:
            return False
        self.held = True
        return True

    def holder(self) -> str:
        return self._holder

    def release(self) -> None:
        if self.held:
            self.held = False
            self.releases += 1


class HoldTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.said = []
        patcher = mock.patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in (heavy_job.SKIP_ENV, heavy_job.HELD_ENV, heavy_job.FLOOR_ENV, heavy_job.WAIT_ENV):
            os.environ.pop(name, None)

    def hold(self, lock, free_ram=lambda: 16 * GIB, **options):
        return heavy_job.hold("test", lock=lock, free_ram=free_ram, clock=self.clock, sleep=self.clock.sleep, say=self.said.append, **options)

    def test_a_free_machine_starts_at_once_and_says_nothing(self) -> None:
        lock = FakeLock()
        with self.hold(lock):
            self.assertTrue(lock.held)
            self.assertEqual(os.environ[heavy_job.HELD_ENV], str(os.getpid()))
        self.assertFalse(lock.held)
        self.assertEqual((self.said, self.clock.sleeps), ([], 0))
        self.assertNotIn(heavy_job.HELD_ENV, os.environ)

    def test_a_busy_lock_waits_and_says_why_once(self) -> None:
        lock = FakeLock(busy=4)
        with self.hold(lock):
            pass
        self.assertEqual(self.clock.sleeps, 4)
        self.assertEqual(self.clock.now, 4 * heavy_job.POLL_SECONDS)
        self.assertEqual(len(self.said), 2, "one line for the reason, one when it starts")
        self.assertIn("another kit Blender job is running (4242 review_unit.py)", self.said[0])
        self.assertIn(heavy_job.SKIP_ENV, self.said[0])
        self.assertIn("starting", self.said[1])

    def test_low_free_ram_waits_for_the_floor_and_lets_the_lock_go_meanwhile(self) -> None:
        readings = iter([2 * GIB, 3 * GIB, 5 * GIB])
        lock = FakeLock()
        with self.hold(lock, free_ram=lambda: next(readings)):
            pass
        self.assertEqual(self.clock.sleeps, 2)
        self.assertEqual(lock.releases, 3, "released twice while waiting, once after the run")
        self.assertIn("free RAM is 2.0 GB, under the 4.0 GB floor", self.said[0])
        self.assertEqual(len(self.said), 3, "the second reading is a new reason (3.0 GB), then the start")

    def test_the_floor_is_configurable(self) -> None:
        os.environ[heavy_job.FLOOR_ENV] = "1.5"
        with self.hold(FakeLock(), free_ram=lambda: 2 * GIB):
            pass
        self.assertEqual(self.clock.sleeps, 0)
        os.environ[heavy_job.FLOOR_ENV] = "8"
        readings = iter([6 * GIB, 9 * GIB])
        with self.hold(FakeLock(), free_ram=lambda: next(readings)):
            pass
        self.assertEqual(self.clock.sleeps, 1)

    def test_a_machine_that_does_not_tell_its_free_ram_has_no_floor(self) -> None:
        with self.hold(FakeLock(), free_ram=lambda: None):
            pass
        self.assertEqual(self.clock.sleeps, 0)

    def test_a_machine_that_stays_busy_ends_in_an_error_that_names_the_reason(self) -> None:
        os.environ[heavy_job.WAIT_ENV] = "1"
        with self.assertRaisesRegex(heavy_job.HeavyJobTimeout, "another kit Blender job is running"):
            with self.hold(FakeLock(busy=10 ** 9)):
                self.fail("must not start")
        self.assertLessEqual(self.clock.sleeps, 5, "one minute of 15 s polls")

    def test_the_poll_cap_fails_a_stuck_wait_fast(self) -> None:
        with self.assertRaisesRegex(heavy_job.HeavyJobTimeout, "3 checks"):
            with self.hold(FakeLock(busy=10 ** 9), max_polls=3):
                self.fail("must not start")
        self.assertEqual(self.clock.sleeps, 3)

    def test_skip_starts_at_once_with_no_lock(self) -> None:
        lock = FakeLock(busy=10 ** 9)
        with self.hold(lock, skip=True):
            pass
        self.assertEqual((lock.attempts, self.clock.sleeps), (0, 0))
        os.environ[heavy_job.SKIP_ENV] = "1"
        with self.hold(lock):
            pass
        self.assertEqual(lock.attempts, 0)

    def test_a_zero_in_the_skip_variable_does_not_skip(self) -> None:
        os.environ[heavy_job.SKIP_ENV] = "0"
        lock = FakeLock()
        with self.hold(lock):
            self.assertEqual(lock.attempts, 1)

    def test_a_kit_command_started_by_a_holder_does_not_wait_for_it(self) -> None:
        outer = FakeLock()
        with self.hold(outer):
            inner = FakeLock(busy=10 ** 9)
            with self.hold(inner):  # the child inherits the holder's variable
                pass
            self.assertEqual(inner.attempts, 0)
        self.assertEqual(self.clock.sleeps, 0)

    def test_an_error_inside_the_block_still_releases_the_lock(self) -> None:
        lock = FakeLock()
        with self.assertRaises(RuntimeError):
            with self.hold(lock):
                raise RuntimeError("blender failed")
        self.assertFalse(lock.held)
        self.assertNotIn(heavy_job.HELD_ENV, os.environ)


class RealLock(unittest.TestCase):
    def test_a_second_holder_is_refused_until_the_first_releases_and_sees_who_holds_it(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / heavy_job.LOCK_NAME
            first, second = heavy_job.FileLock(path), heavy_job.FileLock(path)
            self.assertTrue(first.try_acquire("intake"))
            self.assertFalse(second.try_acquire("review"))
            self.assertEqual(second.holder(), f"{os.getpid()} intake")
            first.release()
            self.assertTrue(second.try_acquire("review"))
            self.assertEqual(first.holder(), f"{os.getpid()} review")
            second.release()
            second.release()  # a second release is harmless

    def test_the_lock_lives_in_the_temporary_folder_unless_told_otherwise(self) -> None:
        with mock.patch.dict(os.environ):
            os.environ.pop(heavy_job.LOCK_DIR_ENV, None)
            self.assertEqual(heavy_job.lock_path(), Path(tempfile.gettempdir()) / heavy_job.LOCK_NAME)
            os.environ[heavy_job.LOCK_DIR_ENV] = "elsewhere"
            self.assertEqual(heavy_job.lock_path(), Path("elsewhere") / heavy_job.LOCK_NAME)

    def test_the_free_ram_is_a_number_or_unknown(self) -> None:
        free = heavy_job.free_ram_bytes()
        self.assertTrue(free is None or free > 0)


class RunWrapper(unittest.TestCase):
    def test_a_program_that_does_not_exist_fails_at_once_without_waiting(self) -> None:
        with mock.patch.object(heavy_job, "hold", side_effect=AssertionError("must not wait")), \
                mock.patch.object(heavy_job.subprocess, "run", return_value="done") as run:
            self.assertEqual(heavy_job.run(["no-such-blender-program", "-b"], text=True), "done")
        run.assert_called_once()

    def test_an_existing_program_runs_inside_the_hold(self) -> None:
        events = []

        class Spy:
            def __enter__(self_inner):
                events.append("hold")

            def __exit__(self_inner, *_exc):
                events.append("release")

        def fake_run(command, **options):
            events.append("run")
            return subprocess.CompletedProcess(command, 0)

        with mock.patch.object(heavy_job, "hold", return_value=Spy()) as hold, mock.patch.object(heavy_job.subprocess, "run", side_effect=fake_run):
            heavy_job.run([sys.executable, "-c", "pass"], capture_output=True)
        self.assertEqual(events, ["hold", "run", "release"])
        self.assertEqual(hold.call_args.kwargs, {"skip": False})

    def test_the_option_sets_the_skip_variable_for_this_process_and_its_children(self) -> None:
        parser = argparse.ArgumentParser()
        heavy_job.add_argument(parser)
        with mock.patch.dict(os.environ):
            os.environ.pop(heavy_job.SKIP_ENV, None)
            heavy_job.apply(parser.parse_args([]))
            self.assertNotIn(heavy_job.SKIP_ENV, os.environ)
            heavy_job.apply(parser.parse_args(["--skip-heavy-check"]))
            self.assertEqual(os.environ[heavy_job.SKIP_ENV], "1")


class CommandLine(unittest.TestCase):
    def test_a_command_typed_by_hand_runs_after_the_wait_and_returns_its_code(self) -> None:
        with mock.patch.object(heavy_job, "run", return_value=subprocess.CompletedProcess(["blender"], 7)) as run:
            self.assertEqual(heavy_job.main(["--", "blender", "-b", "--python", "stage.py"]), 7)
        self.assertEqual(run.call_args.args[0], ["blender", "-b", "--python", "stage.py"])

    def test_the_skip_option_is_passed_on_and_a_missing_command_is_refused(self) -> None:
        with mock.patch.dict(os.environ), mock.patch.object(heavy_job, "run", return_value=subprocess.CompletedProcess(["x"], 0)):
            os.environ.pop(heavy_job.SKIP_ENV, None)
            heavy_job.main(["--skip-heavy-check", "--", "x"])
            self.assertEqual(os.environ[heavy_job.SKIP_ENV], "1")
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            heavy_job.main([])


class EveryBlenderStart(unittest.TestCase):
    """The gate must stand in front of every kit command that starts Blender, so a new one cannot forget it."""

    PRODUCTION = [
        path for path in PIPELINE.rglob("*.py")
        # `vendor/` is the git-ignored copy of the Blender MCP server the bootstrap installs: not the kit's own tools (a set-up checkout failed here)
        if "tests" not in path.parts and "adapter" not in path.parts and "blender" not in path.parts and "meshy_runtime" not in path.parts
        and "vendor" not in path.parts
        and path.name not in {"heavy_job.py", "bootstrap_3d_workflow.py", "mcp_stdio.py"}
    ]

    def test_no_tool_starts_blender_with_a_bare_subprocess_call(self) -> None:
        for path in self.PRODUCTION:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and ast.unparse(node.func) in {"subprocess.run", "subprocess.Popen", "subprocess.check_output", "subprocess.call"}:
                    with self.subTest(file=path.name, line=node.lineno):
                        self.assertNotIn("blender", ast.unparse(node).lower(), f"{path.name}:{node.lineno} starts Blender without lib/heavy_job.py")

    def test_the_tools_that_start_blender_call_the_gate(self) -> None:
        for name in ("tripo_intake.py", "review_unit.py", "repair_unit.py", "check_holes.py", "fit_prop.py", "tripo/colour_compare.py",
                     "tripo/static_model.py", "tripo/static_sheets.py", "tripo/weapon_sheets.py"):
            with self.subTest(tool=name):
                self.assertIn("heavy_job.run(", (PIPELINE / name).read_text(encoding="utf-8"))

    def test_the_bootstrap_and_the_adapter_route_are_gated(self) -> None:
        self.assertIn('heavy_job.hold("bootstrap_3d_workflow")', (PIPELINE / "bootstrap_3d_workflow.py").read_text(encoding="utf-8"))
        client = object.__new__(blender_client.BlenderAdapterClient)
        client.repo_root = PIPELINE.parents[1]
        client.wrapper = PIPELINE / "wrappers" / "run_blender_hoi4_adapter.cmd"
        with mock.patch.object(heavy_job, "hold") as hold, mock.patch.object(blender_client, "call_stdio", return_value={"structuredContent": {"ok": True}}) as inner:
            self.assertEqual(client.call("hoi4_blender_health", {}), {"ok": True})
        hold.assert_called_once()
        self.assertIn("hoi4_blender_health", hold.call_args.args[0])
        self.assertEqual(inner.call_count, 1)


if __name__ == "__main__":
    unittest.main()
