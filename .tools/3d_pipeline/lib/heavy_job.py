"""Start Blender only when the machine can take it: one kit Blender at a time, and enough free RAM.

Blender is the heavy step of the 3D route. A person's machine may already run a game, a render or another unit's Blender stage, and two
of them at once exhaust the RAM. Every kit command that starts Blender calls `run` (or holds `hold` around its own start) first. It

1. takes a machine-wide lock, an operating system file lock on `hoi4-kit-heavy-job.lock` in the temporary folder, so a second kit Blender
   waits for the first and a crashed holder frees the lock by itself (no stale lock to clear),
2. waits while the free RAM is under a floor (`HOI4_KIT_MIN_FREE_RAM_GB`, 4 by default; a machine where the free RAM cannot be read
   has no floor),
3. says in one line why it waits (once for each reason) and one line when it starts,
4. gives up after `HOI4_KIT_HEAVY_WAIT_MINUTES` minutes (360 by default) with an error that names the reason.

A kit command that starts another kit command (the intake or a review inside a longer run) does not wait for itself: the holder sets
`HOI4_KIT_HEAVY_JOB_HELD` for its children, and a nested `hold` passes. `HOI4_KIT_SKIP_HEAVY_CHECK=1` (or `skip=True`) skips the whole
check, for a machine that is known to be free. A command whose program does not exist fails at once in `subprocess`, so `run` does
not wait for it.
"""

from __future__ import annotations

import argparse
import contextlib
import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Iterator, List, Optional, Sequence

LOCK_NAME = "hoi4-kit-heavy-job.lock"
SKIP_ENV = "HOI4_KIT_SKIP_HEAVY_CHECK"
HELD_ENV = "HOI4_KIT_HEAVY_JOB_HELD"
FLOOR_ENV = "HOI4_KIT_MIN_FREE_RAM_GB"
WAIT_ENV = "HOI4_KIT_HEAVY_WAIT_MINUTES"
LOCK_DIR_ENV = "HOI4_KIT_HEAVY_LOCK_DIR"
DEFAULT_FLOOR_GB = 4.0
DEFAULT_WAIT_MINUTES = 360.0
POLL_SECONDS = 15.0
GIB = 1024 ** 3


class HeavyJobTimeout(RuntimeError):
    """The machine stayed busy for the whole wait."""


# ---------------------------------------------------------------------------------------------
# What the machine has free
# ---------------------------------------------------------------------------------------------


def free_ram_bytes() -> Optional[int]:
    """The RAM that is free for a new process, or None when this machine does not tell."""

    try:
        if sys.platform == "win32":
            class Status(ctypes.Structure):
                _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total", ctypes.c_ulonglong),
                            ("free", ctypes.c_ulonglong), ("page_total", ctypes.c_ulonglong), ("page_free", ctypes.c_ulonglong),
                            ("virtual_total", ctypes.c_ulonglong), ("virtual_free", ctypes.c_ulonglong), ("extended", ctypes.c_ulonglong)]

            status = Status()
            status.length = ctypes.sizeof(Status)
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):  # type: ignore[attr-defined]
                return None
            return int(status.free)
        meminfo = Path("/proc/meminfo")
        if meminfo.is_file():
            for line in meminfo.read_text(encoding="ascii", errors="replace").splitlines():
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) * 1024
            return None
        if sys.platform == "darwin" and shutil.which("vm_stat"):
            text = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=10, check=False).stdout
            page = int(text.split("page size of")[1].split()[0])
            pages = 0
            for key in ("Pages free", "Pages inactive", "Pages speculative"):
                pages += int(next(line for line in text.splitlines() if line.startswith(key)).split(":")[1].strip().rstrip("."))
            return pages * page
    except (OSError, ValueError, IndexError, StopIteration, subprocess.SubprocessError, AttributeError):
        return None
    return None


def min_free_ram_bytes() -> int:
    try:
        return int(float(os.environ.get(FLOOR_ENV, DEFAULT_FLOOR_GB)) * GIB)
    except ValueError:
        return int(DEFAULT_FLOOR_GB * GIB)


def max_wait_seconds() -> float:
    try:
        return float(os.environ.get(WAIT_ENV, DEFAULT_WAIT_MINUTES)) * 60.0
    except ValueError:
        return DEFAULT_WAIT_MINUTES * 60.0


# ---------------------------------------------------------------------------------------------
# The machine-wide lock
# ---------------------------------------------------------------------------------------------


class FileLock:
    """An operating system lock on one small file. Held until `release` or the end of the process, whichever comes first."""

    def __init__(self, path: Path):
        self.path = path
        self.handle: Optional[Any] = None

    def try_acquire(self, label: str) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle = open(self.path, "a+b")
        try:
            if sys.platform == "win32":
                import msvcrt

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)  # type: ignore[attr-defined]
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)  # type: ignore[attr-defined]
        except OSError:
            handle.close()
            return False
        self.handle = handle
        handle.seek(1)
        handle.truncate(1)
        handle.write(f"{os.getpid()} {label}\n".encode("utf-8", "replace"))
        handle.flush()
        return True

    def holder(self) -> str:
        """Who holds the lock, as `<pid> <label>` (empty when unreadable)."""

        try:
            with open(self.path, "rb") as handle:
                handle.seek(1)  # byte 0 is the locked byte, and Windows refuses to read it
                return handle.read(200).decode("utf-8", "replace").strip()
        except OSError:
            return ""

    def release(self) -> None:
        handle, self.handle = self.handle, None
        if handle is None:
            return
        try:
            handle.seek(0)
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)  # type: ignore[attr-defined]
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)  # type: ignore[attr-defined]
        except OSError:
            pass
        finally:
            handle.close()


def lock_path() -> Path:
    return Path(os.environ.get(LOCK_DIR_ENV) or tempfile.gettempdir()) / LOCK_NAME


# ---------------------------------------------------------------------------------------------
# Hold the machine for one Blender start
# ---------------------------------------------------------------------------------------------


def _say(message: str) -> None:
    print(f"heavy job: {message}", file=sys.stderr, flush=True)


@contextlib.contextmanager
def hold(
    label: str,
    *,
    skip: bool = False,
    lock: Optional[FileLock] = None,
    free_ram: Callable[[], Optional[int]] = free_ram_bytes,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    say: Callable[[str], None] = _say,
    max_polls: int = 100000,
) -> Iterator[None]:
    """Wait until this process may start a Blender, hold the lock while the block runs, then release it.

    `label` names the command for the line other waiters print. `clock`, `sleep` and `max_polls` exist for tests (a fake clock that every
    sleep advances, and a cap on the loop, so a stuck wait fails fast)."""

    if skip or os.environ.get(SKIP_ENV, "").strip() not in ("", "0") or os.environ.get(HELD_ENV):
        yield
        return
    lock = lock or FileLock(lock_path())
    floor = min_free_ram_bytes()
    deadline = clock() + max_wait_seconds()
    said: List[str] = []
    for _ in range(max_polls):
        reason = ""
        if not lock.try_acquire(label):
            reason = f"another kit Blender job is running ({lock.holder() or 'holder unknown'})"
        else:
            free = free_ram()
            if free is not None and free < floor:
                lock.release()
                reason = f"free RAM is {free / GIB:.1f} GB, under the {floor / GIB:.1f} GB floor ({FLOOR_ENV})"
        if not reason:
            break
        if reason not in said:
            said.append(reason)
            say(f"waiting, {reason}. Set {SKIP_ENV}=1 to start now.")
        if clock() >= deadline:
            raise HeavyJobTimeout(f"The machine stayed busy for {max_wait_seconds() / 60:.0f} minutes: {reason}.")
        sleep(POLL_SECONDS)
    else:
        raise HeavyJobTimeout(f"The machine stayed busy after {max_polls} checks: {said[-1] if said else 'unknown'}.")
    if said:
        say("the machine is free, starting")
    previous = os.environ.get(HELD_ENV)
    os.environ[HELD_ENV] = str(os.getpid())
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(HELD_ENV, None)
        else:
            os.environ[HELD_ENV] = previous
        lock.release()


def run(command: Sequence[Any], *, label: Optional[str] = None, skip: bool = False, **options: Any) -> "subprocess.CompletedProcess[Any]":
    """`subprocess.run(command, **options)` for a command that starts Blender, after `hold`."""

    program = str(command[0])
    if not (Path(program).exists() or shutil.which(program)):
        return subprocess.run(command, **options)  # fails at once with FileNotFoundError: nothing heavy starts
    with hold(label or Path(sys.argv[0]).name or Path(program).stem, skip=skip):
        return subprocess.run(command, **options)


def add_argument(parser: Any) -> None:
    """The shared `--skip-heavy-check` option of a command that starts Blender."""

    parser.add_argument("--skip-heavy-check", action="store_true",
                        help=f"start Blender without waiting for the machine (the same as {SKIP_ENV}=1): no lock, no free RAM floor")


def apply(args: Any) -> None:
    if getattr(args, "skip_heavy_check", False):
        os.environ[SKIP_ENV] = "1"


def main(argv: Optional[Sequence[str]] = None) -> int:
    """`py -3.13 -B .tools/3d_pipeline/lib/heavy_job.py [--skip-heavy-check] -- <command>`: run a Blender command you type yourself (a stage
    script such as `blender -b --python tripo/shield_stage.py -- ...`) after the same wait as the kit's own commands."""

    parser = argparse.ArgumentParser(description=main.__doc__)
    add_argument(parser)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("give the command to run after `--`")
    apply(args)
    return run(command, label="a Blender command typed by hand").returncode


if __name__ == "__main__":
    raise SystemExit(main())
