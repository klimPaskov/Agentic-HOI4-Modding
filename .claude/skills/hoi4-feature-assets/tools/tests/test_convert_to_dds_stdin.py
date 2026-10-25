from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock


TOOL_PATH = Path(__file__).resolve().parents[1] / "convert_to_dds.py"
SPEC = importlib.util.spec_from_file_location("convert_to_dds", TOOL_PATH)
if SPEC is None or SPEC.loader is None:
	raise RuntimeError(f"Unable to load DDS converter: {TOOL_PATH}")
CONVERTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONVERTER)

# The child reads stdin to EOF, as ffmpeg does when no -nostdin is given.
READ_STDIN = "import sys; sys.stdout.write(str(len(sys.stdin.read())))"


class ConverterStdinTests(unittest.TestCase):
	"""An MCP stdio server calls the converter while its own stdin pipe stays open."""

	def run_under_open_pipe(self, helper: str) -> subprocess.CompletedProcess[str]:
		script = textwrap.dedent(
			f"""
			import importlib.util, sys
			spec = importlib.util.spec_from_file_location("convert_to_dds", {str(TOOL_PATH)!r})
			module = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(module)
			result = module.{helper}([sys.executable, "-c", {READ_STDIN!r}])
			output = result.stdout if isinstance(result.stdout, str) else result.stdout.decode()
			print("child-read:" + output)
			"""
		)
		process = subprocess.Popen(
			[sys.executable, "-c", script],
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True,
		)
		try:
			# Keep stdin open without writing, like a stdio server awaiting its client.
			stdout, stderr = self._wait(process)
		finally:
			if process.poll() is None:
				process.kill()
				process.wait()
			if process.stdin is not None:
				process.stdin.close()
		return subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)

	def _wait(self, process: subprocess.Popen[str]) -> tuple[str, str]:
		try:
			process.wait(timeout=30)
		except subprocess.TimeoutExpired:
			self.fail("converter child inherited the caller's open stdin and blocked")
		assert process.stdout is not None and process.stderr is not None
		return process.stdout.read(), process.stderr.read()

	def test_children_do_not_inherit_an_open_stdin(self) -> None:
		for helper in ("run_command", "run_binary_command"):
			with self.subTest(helper=helper):
				completed = self.run_under_open_pipe(helper)
				self.assertEqual(completed.returncode, 0, completed.stderr)
				self.assertIn("child-read:0", completed.stdout)

	def test_ffmpeg_fallback_never_reads_stdin(self) -> None:
		with tempfile.TemporaryDirectory() as temp:
			output = Path(temp) / "out.dds"
			with mock.patch.object(CONVERTER, "find_ffmpeg", return_value=Path("ffmpeg")), mock.patch.object(
				CONVERTER, "probe_image_size", return_value=(2, 2)
			), mock.patch.object(
				CONVERTER, "run_binary_command", return_value=mock.Mock(stdout=bytes(16))
			) as run:
				CONVERTER.run_ffmpeg_bgra_fallback(Path(temp) / "in.png", output, None, None)
		command = run.call_args.args[0]
		self.assertEqual(command[:2], ["ffmpeg", "-nostdin"])


if __name__ == "__main__":
	unittest.main()
