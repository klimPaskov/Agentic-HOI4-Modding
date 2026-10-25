"""Minimal stdio MCP session: one server start, several sequential tool calls.

Repository checks use it to call HOI4 Agent Tools for many files without paying the server's
start-up indexing once per file. The server is configured once in `.mcp.json`; `server_command`
reads its command, working directory and environment from there.

The 3D pipeline keeps its own single-call client (`.tools/3d_pipeline/lib/mcp_stdio.py`), which is
hash-pinned in `.tools/3d_pipeline/config/dependencies.lock.json` and changes only with an adapter
release. Stdin stays open until each response arrives, because Node-based MCP servers stop reading
at stdin EOF before answering a pending call.
"""

from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
import time
from pathlib import Path
from typing import IO, Any, Dict, List, Optional, Sequence, Tuple, cast

REPO_ROOT = Path(__file__).resolve().parents[2]


class McpError(RuntimeError):
	"""The server could not start, answer in time, or complete a call."""


def server_command(name: str) -> Tuple[List[str], Path, Dict[str, str]]:
	"""Return (command, cwd, env overrides) for a server declared in the repository `.mcp.json`."""
	config = json.loads((REPO_ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
	if name not in config:
		raise McpError(f"{name} is not declared in .mcp.json")
	server = config[name]
	env = {key: value for key, value in server.get("env", {}).items() if "${" not in value}
	return [server["command"], *server.get("args", [])], Path(server.get("cwd") or REPO_ROOT), env


class McpSession:
	def __init__(self, command: Sequence[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None,
			timeout_seconds: float = 300) -> None:
		self.command, self.cwd, self.env, self.timeout = list(command), cwd, env or {}, timeout_seconds
		self.process: "Optional[subprocess.Popen[str]]" = None
		self.responses: "queue.Queue[Optional[Dict[str, Any]]]" = queue.Queue()
		self.stderr: List[str] = []
		self.next_id = 1

	def __enter__(self) -> "McpSession":
		try:
			self.process = subprocess.Popen(self.command, cwd=str(self.cwd) if self.cwd else None,
				env={**os.environ, **self.env}, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
				text=True, encoding="utf-8", errors="replace")
		except OSError as error:
			raise McpError(f"cannot start {self.command[0]}: {error}") from error
		threading.Thread(target=self._read_stdout, daemon=True).start()
		threading.Thread(target=lambda: self.stderr.extend(self._pipe("stderr")), daemon=True).start()
		self._request("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
			"clientInfo": {"name": "hoi4-repository-checks", "version": "1.0.0"}})
		self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
		return self

	def __exit__(self, *exc_info: object) -> None:
		if self.process is None:
			return
		try:
			self._pipe("stdin").close()
			self.process.wait(timeout=10)
		except (OSError, subprocess.TimeoutExpired):
			if os.name == "nt":
				subprocess.run(["taskkill", "/T", "/F", "/PID", str(self.process.pid)], capture_output=True)
			self.process.kill()

	def call(self, tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
		"""Call one tool and return its `structuredContent`, or its raw result when it has none."""
		result = self._request("tools/call", {"name": tool, "arguments": arguments})
		if result.get("isError"):
			text = " ".join(part.get("text", "") for part in result.get("content", []))
			raise McpError(f"{tool} failed: {text.strip()}")
		return cast(Dict[str, Any], result.get("structuredContent", result))

	def _pipe(self, name: str) -> IO[str]:
		"""Return one of the running server's text pipes."""
		assert self.process is not None, "the session is not running"
		pipe = getattr(self.process, name)
		assert pipe is not None
		return cast(IO[str], pipe)

	def _read_stdout(self) -> None:
		for line in self._pipe("stdout"):
			line = line.strip()
			if line.startswith("{"):
				try:
					self.responses.put(json.loads(line))
				except json.JSONDecodeError:
					continue
		self.responses.put(None)

	def _send(self, message: Dict[str, Any]) -> None:
		stdin = self._pipe("stdin")
		stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
		stdin.flush()

	def _request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
		identifier, self.next_id = self.next_id, self.next_id + 1
		self._send({"jsonrpc": "2.0", "id": identifier, "method": method, "params": params})
		deadline = time.monotonic() + self.timeout
		while True:
			try:
				message = self.responses.get(timeout=max(0.01, deadline - time.monotonic()))
			except queue.Empty:
				raise McpError(f"{method} timed out after {self.timeout:.0f} s") from None
			if message is None:
				raise McpError(f"server closed before answering {method}: {''.join(self.stderr).strip()[-500:]}")
			if message.get("id") == identifier:
				if "error" in message:
					raise McpError(json.dumps(message["error"], sort_keys=True))
				return cast(Dict[str, Any], message.get("result", {}))
