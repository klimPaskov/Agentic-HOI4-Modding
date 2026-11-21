"""TS.motionPromptCheck in tripo/tripo_studio.js refuses a text-to-motion prompt Tripo would refuse silently. Runs the page driver in
Node with a stub page; skipped when Node is not installed. No Blender."""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

DRIVER = Path(__file__).resolve().parents[1] / "tripo" / "tripo_studio.js"
SCRIPT = """
const fs = require("fs");
global.window = {}; global.location = {};
const lengths = JSON.parse(process.argv[2]);
const out = [];
for (const n of lengths) {
  global.document = { querySelectorAll: (s) => (s === "textarea" ? [{ offsetParent: 1, value: "x".repeat(n) }] : []) };
  eval(fs.readFileSync(process.argv[1], "utf8"));
  out.push(window.TS.motionPromptCheck());
}
console.log(JSON.stringify(out));
"""


@unittest.skipUnless(shutil.which("node"), "Node is not installed")
class MotionPrompt(unittest.TestCase):
    def test_a_long_prompt_is_refused_before_the_press(self) -> None:
        # 2026-11-21: a 330-character prompt started no task three times, 266 characters ran
        lengths = [0, 266, 280, 281, 330]
        run = subprocess.run(["node", "-e", SCRIPT, str(DRIVER), json.dumps(lengths)], capture_output=True, text=True, timeout=60, check=True)
        results = json.loads(run.stdout)
        self.assertEqual([item["ok"] for item in results], [False, True, True, False, False])
        self.assertIn("shorten", results[-1]["reason"])


if __name__ == "__main__":
    unittest.main()
