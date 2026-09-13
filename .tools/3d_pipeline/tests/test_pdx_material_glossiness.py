"""Check the runtime shader contract independently of Blender preview shading."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

from PIL import Image

SOURCE = Path(__file__).parents[1] / "pack_pdx_material.py"
SPEC = importlib.util.spec_from_file_location("pack_pdx_material", SOURCE)
PACK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACK)


class PdxGlossinessTests(unittest.TestCase):
    def test_runtime_gloss_inverts_roughness_while_gltf_and_sources_preserve_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            roughness = Image.new("L", (4, 1))
            roughness.putdata([0, 64, 128, 255])
            roughness.save(root / "roughness.png")
            Image.new("L", (4, 1), 73).save(root / "metallic.png")
            originals = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in root.glob("*.png")}
            PACK.ensure_gltf_metallic_roughness_map(root, "metallic_roughness.png")
            with Image.open(root / "metallic_roughness.png") as gltf:
                self.assertEqual(list(gltf.getchannel("G").getdata()), [0, 64, 128, 255])
            reports = [PACK.pack_pdx_specular_map(root, "metallic_roughness.png"),
                       PACK.pack_pdx_specular_channels(root, "metallic.png", "roughness.png", "separate.png")]
            for report in reports:
                self.assertEqual(report["layout"]["alpha"], "glossiness_255_minus_roughness")
                with Image.open(root / report["output"]["path"]) as result:
                    self.assertEqual(list(result.getchannel("A").getdata()), [255, 191, 127, 0])
                    self.assertEqual(list(result.getchannel("G").getdata()), [PACK.PDX_SPECULAR_LEVEL] * 4)
                    self.assertEqual(list(result.getchannel("B").getdata()), [73] * 4)
            for filename, digest in originals.items():
                self.assertEqual(hashlib.sha256((root / filename).read_bytes()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
