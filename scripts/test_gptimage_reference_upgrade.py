"""Exercise vendored reference discovery without credentials or generation."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / ".tools/image_generation/providers/gptimage"


class GPTImageReferenceUpgradeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node.js is required for vendored source checks")
    def test_reference_discovery_and_non_overwrite_outputs(self):
        script = """
import fs from 'node:fs/promises';
import path from 'node:path';
const images = await import(process.argv[1]);
const root = process.argv[2];
await images.ensureReferencesDir(root);
await fs.writeFile(path.join(root, 'references', 'z.PNG'), Buffer.from([137,80,78,71,13,10,26,10]));
await fs.writeFile(path.join(root, 'references', 'a.jpg'), Buffer.from([255,216,255]));
await fs.writeFile(path.join(root, 'references', 'notes.txt'), 'excluded');
await fs.mkdir(path.join(root, 'references', 'directory.png'));
const references = await images.listReferences(root);
const data = await images.readReferenceImages(references, root);
const first = await images.savePng('out.png', root, 'YWJj');
const second = await images.savePng('out.png', root, 'ZGVm');
console.log(JSON.stringify({references,data,first,second,original:await fs.readFile(first.savedPath,'utf8')}));
"""
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [shutil.which("node"), "--input-type=module", "-e", script,
                 (PACKAGE / "src/images.js").as_uri(), temporary],
                check=True, capture_output=True, text=True, timeout=30,
            )
            data = json.loads(result.stdout)
        self.assertEqual([Path(item).name for item in data["references"]], ["a.jpg", "z.PNG"])
        self.assertTrue(data["data"][0].startswith("data:image/jpeg;base64,"))
        self.assertTrue(data["data"][1].startswith("data:image/png;base64,"))
        self.assertFalse(data["first"]["versioned"])
        self.assertTrue(data["second"]["versioned"])
        self.assertEqual(Path(data["second"]["savedPath"]).name, "out-v2.png")
        self.assertEqual(data["original"], "abc")

    def test_windows_login_and_dependency_lock_remain_managed(self):
        login = (PACKAGE / "src/login.js").read_text(encoding="utf-8")
        self.assertIn('[["rundll32", ["url.dll,FileProtocolHandler", url]]]', login)
        lock = json.loads((PACKAGE / "package-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["packages"][""]["version"], "0.1.0")
        for name, package in lock["packages"].items():
            if name:
                self.assertTrue(package.get("integrity", "").startswith("sha512-"), name)


if __name__ == "__main__":
    unittest.main()
