"""Small, strict JSON-RPC client for the repository's pinned MCP routes."""

from __future__ import annotations

import json
import os
import subprocess
import ctypes
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Sequence


class MCPRouteError(RuntimeError):
    """Raised when an MCP process cannot initialize or complete a call."""


def _create_windows_kill_job() -> Optional[int]:
    """Create a job object that terminates the whole MCP tree when closed."""

    if os.name != "nt":
        return None

    from ctypes import wintypes

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL

    job_handle = kernel32.CreateJobObjectW(None, None)
    if not job_handle:
        raise MCPRouteError(
            f"Unable to create MCP cleanup job (Windows error {ctypes.get_last_error()})."
        )

    information = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    information.BasicLimitInformation.LimitFlags = 0x00002000
    if not kernel32.SetInformationJobObject(
        job_handle,
        9,
        ctypes.byref(information),
        ctypes.sizeof(information),
    ):
        error = ctypes.get_last_error()
        kernel32.CloseHandle(job_handle)
        raise MCPRouteError(f"Unable to configure MCP cleanup job (Windows error {error}).")
    return int(job_handle)


def _assign_windows_kill_job(job_handle: Optional[int], process: subprocess.Popen[str]) -> None:
    """Attach the MCP wrapper before it can leave long-lived descendants."""

    if job_handle is None:
        return

    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    if not kernel32.AssignProcessToJobObject(job_handle, wintypes.HANDLE(process._handle)):
        raise MCPRouteError(
            f"Unable to attach MCP route to its cleanup job (Windows error {ctypes.get_last_error()})."
        )


def _windows_job_process_ids(job_handle: Optional[int]) -> list[int]:
    """Return the exact live PIDs assigned to one client-owned Job Object."""

    if job_handle is None:
        return []

    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.QueryInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryInformationJobObject.restype = wintypes.BOOL

    buffer_size = 64 * 1024
    buffer = ctypes.create_string_buffer(buffer_size)
    returned = wintypes.DWORD()
    if not kernel32.QueryInformationJobObject(
        wintypes.HANDLE(job_handle),
        3,
        buffer,
        buffer_size,
        ctypes.byref(returned),
    ):
        raise MCPRouteError(
            f"Unable to inspect MCP cleanup job (Windows error {ctypes.get_last_error()})."
        )

    assigned_count = ctypes.c_uint32.from_buffer(buffer, 0).value
    listed_count = ctypes.c_uint32.from_buffer(buffer, 4).value
    pid_size = ctypes.sizeof(ctypes.c_size_t)
    if listed_count > assigned_count or 8 + listed_count * pid_size > buffer_size:
        raise MCPRouteError("The MCP cleanup job returned an invalid process-id list.")
    process_ids = (ctypes.c_size_t * listed_count).from_buffer(buffer, 8)
    return [int(process_ids[index]) for index in range(listed_count)]


def _windows_pid_is_alive(pid: int) -> bool:
    """Check one exact PID without enumerating or mutating unrelated processes."""

    if os.name != "nt":
        return False

    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel32.GetExitCodeProcess.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    process_handle = kernel32.OpenProcess(0x1000, False, pid)
    if not process_handle:
        return False
    try:
        exit_code = wintypes.DWORD()
        return bool(
            kernel32.GetExitCodeProcess(process_handle, ctypes.byref(exit_code))
        ) and exit_code.value == 259
    finally:
        kernel32.CloseHandle(process_handle)


def _wait_windows_pids_exit(
    process_ids: Iterable[int], timeout_seconds: float = 5.0
) -> list[int]:
    """Wait briefly for only the supplied job-owned PIDs to disappear."""

    remaining = {int(pid) for pid in process_ids if int(pid) > 0}
    deadline = time.monotonic() + timeout_seconds
    while remaining and time.monotonic() < deadline:
        remaining = {pid for pid in remaining if _windows_pid_is_alive(pid)}
        if remaining:
            time.sleep(0.05)
    return sorted(pid for pid in remaining if _windows_pid_is_alive(pid))


def _close_windows_handle(handle: Optional[int]) -> None:
    """Close a Windows job handle, triggering kill-on-close for its process tree."""

    if handle is None:
        return
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.CloseHandle(wintypes.HANDLE(handle))


def _terminate_windows_descendants(root_pid: int) -> None:
    """Clean up only processes spawned beneath one completed MCP wrapper."""

    if os.name != "nt":
        return
    script = r"""
$rootPid = [int]$env:HOI4_MCP_ROOT_PID
$all = @(Get-CimInstance Win32_Process)
$known = [System.Collections.Generic.HashSet[int]]::new()
$null = $known.Add($rootPid)
$descendants = [System.Collections.Generic.List[int]]::new()
do {
	$added = $false
	foreach ($process in $all) {
		if ($known.Contains([int]$process.ParentProcessId) -and -not $known.Contains([int]$process.ProcessId)) {
			$null = $known.Add([int]$process.ProcessId)
			$descendants.Add([int]$process.ProcessId)
			$added = $true
		}
	}
} while ($added)
for ($index = $descendants.Count - 1; $index -ge 0; $index--) {
	Stop-Process -Id $descendants[$index] -Force -ErrorAction SilentlyContinue
}
Stop-Process -Id $rootPid -Force -ErrorAction SilentlyContinue
"""
    process_env = os.environ.copy()
    process_env["HOI4_MCP_ROOT_PID"] = str(root_pid)
    try:
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=process_env,
            timeout=15,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (OSError, subprocess.SubprocessError):
        pass


def _json_lines(output: str) -> Iterable[Dict[str, Any]]:
    decoder = json.JSONDecoder()
    cursor = 0
    while cursor < len(output):
        start = output.find("{", cursor)
        if start < 0:
            return
        try:
            value, consumed = decoder.raw_decode(output[start:])
        except json.JSONDecodeError:
            cursor = start + 1
            continue
        cursor = start + consumed
        if isinstance(value, dict) and value.get("jsonrpc") == "2.0":
            yield value


def call_stdio(
    command: Sequence[str],
    *,
    tool: Optional[str] = None,
    arguments: Optional[Dict[str, Any]] = None,
    list_tools: bool = False,
    timeout_seconds: int = 1800,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    lifecycle_receipt: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Initialize an MCP server, call one tool, and close the stdio session.

    The client accepts only JSON-RPC output from stdout. Human-readable logs
    belong on stderr and are retained in the returned diagnostic when present.
    """

    if tool is not None and list_tools:
        raise ValueError("Choose either a tool call or a tools/list request, not both.")

    messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "hoi4-3d-pipeline", "version": "1.0.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
    ]
    if tool is not None:
        messages.append(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": tool, "arguments": arguments or {}},
            }
        )
    elif list_tools:
        messages.append({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})

    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    request = "\n".join(json.dumps(message, separators=(",", ":")) for message in messages) + "\n"

    process: Optional[subprocess.Popen[str]] = None
    windows_job = _create_windows_kill_job()
    owned_at_cleanup: list[int] = []
    surviving_process_ids: list[int] = []
    cleanup_inspection_error: Optional[MCPRouteError] = None
    if lifecycle_receipt is not None:
        lifecycle_receipt.clear()
        lifecycle_receipt.update(
            {
                "ownership": "windows_job_object" if os.name == "nt" else "direct_process",
                "root_pid": None,
                "owned_process_ids_at_cleanup": [],
                "surviving_process_ids": [],
                "cleanup_inspection_error": None,
            }
        )
    try:
        process = subprocess.Popen(
            list(command),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(cwd) if cwd else None,
            env=process_env,
        )
        if lifecycle_receipt is not None:
            lifecycle_receipt["root_pid"] = process.pid
        _assign_windows_kill_job(windows_job, process)
        stdout_text, stderr_text = process.communicate(request, timeout=timeout_seconds)
        completed = subprocess.CompletedProcess(
            list(command),
            process.returncode,
            stdout_text,
            stderr_text,
        )
    except subprocess.TimeoutExpired as exc:
        if process is not None:
            process.kill()
            process.communicate()
        raise MCPRouteError(f"MCP route timed out after {timeout_seconds}s: {command}") from exc
    except OSError as exc:
        raise MCPRouteError(f"Unable to start MCP route: {command}") from exc
    finally:
        if process is not None:
            try:
                owned_at_cleanup = _windows_job_process_ids(windows_job)
            except MCPRouteError as exc:
                cleanup_inspection_error = exc
                owned_at_cleanup = [process.pid]
            finally:
                _close_windows_handle(windows_job)
                windows_job = None
            _terminate_windows_descendants(process.pid)
            if process.poll() is None:
                try:
                    process.kill()
                    process.wait(timeout=5)
                except (OSError, subprocess.SubprocessError):
                    pass
            surviving_process_ids = _wait_windows_pids_exit(
                set(owned_at_cleanup) | {process.pid}
            )
            if lifecycle_receipt is not None:
                lifecycle_receipt["owned_process_ids_at_cleanup"] = sorted(owned_at_cleanup)
                lifecycle_receipt["surviving_process_ids"] = surviving_process_ids
                lifecycle_receipt["cleanup_inspection_error"] = (
                    str(cleanup_inspection_error) if cleanup_inspection_error else None
                )
        _close_windows_handle(windows_job)

    if cleanup_inspection_error is not None:
        raise MCPRouteError(
            "MCP route cleanup could not verify the exact Windows Job Object process list."
        ) from cleanup_inspection_error
    if surviving_process_ids:
        raise MCPRouteError(
            f"MCP route cleanup left owned process IDs alive: {surviving_process_ids}"
        )

    responses = list(_json_lines(completed.stdout))
    response = next((item for item in reversed(responses) if item.get("id") == 2), None)
    if response is None and tool is None and not list_tools:
        response = next((item for item in reversed(responses) if item.get("id") == 1), None)
    if response is None:
        diagnostics = (completed.stderr or "").strip()[-4000:]
        requested = f" for tool {tool!r}" if tool else " for tools/list" if list_tools else ""
        raise MCPRouteError(
            f"MCP route returned no JSON-RPC response{requested} (exit={completed.returncode}). {diagnostics}"
        )
    if "error" in response:
        raise MCPRouteError(json.dumps(response["error"], sort_keys=True))
    if completed.returncode != 0:
        raise MCPRouteError(
            f"MCP route exited with {completed.returncode}: {(completed.stderr or '').strip()[-4000:]}"
        )
    stderr_text = completed.stderr or ""
    if stderr_text.strip():
        response["_route_stderr"] = stderr_text.strip()[-4000:]
    return response.get("result", response)
