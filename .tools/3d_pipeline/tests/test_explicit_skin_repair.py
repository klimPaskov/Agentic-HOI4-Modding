import copy
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "adapter" / "explicit_skin_repair.py"
spec = importlib.util.spec_from_file_location("explicit_skin_repair", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExplicitSkinValidation(unittest.TestCase):
    def setUp(self):
        self.valid = {"mesh": "body", "rig": "rig", "topology_sha256": "A" * 64, "review_evidence": "Reviewed exact forearm vertices in job report.", "vertices": [{"index": 42, "expected": {"hand": .8, "leg": .2}, "replacement": {"hand": 1.0}}]}

    def test_valid(self):
        self.assertEqual(module.validate_spec(self.valid), self.valid)

    def reject(self, edit):
        value = copy.deepcopy(self.valid)
        edit(value)
        with self.assertRaises(ValueError):
            module.validate_spec(value)

    def test_no_unknown_fields(self):
        self.reject(lambda v: v.update(auto_select=True))

    def test_duplicate_indices(self):
        self.reject(lambda v: v["vertices"].append(copy.deepcopy(v["vertices"][0])))

    def test_not_normalized(self):
        self.reject(lambda v: v["vertices"][0].update(replacement={"hand": .9}))

    def test_nan(self):
        self.reject(lambda v: v["vertices"][0].update(replacement={"hand": float("nan")}))

    def test_five_influences(self):
        self.reject(lambda v: v["vertices"][0].update(replacement={str(chr(97+i)): .2 for i in range(5)}))

    def test_negative_index(self):
        self.reject(lambda v: v["vertices"][0].update(index=-1))

    def test_no_ownership_evidence(self):
        self.reject(lambda v: v.update(review_evidence=""))

    def test_noop(self):
        self.reject(lambda v: v["vertices"][0].update(replacement={"hand": .8, "leg": .2}))

    def test_selection(self):
        value = {"mesh": "body", "topology_sha256": "A" * 64, "indices": [1, 2, 3]}
        self.assertEqual(module.validate_selection(value), value)
        for indices in ([1, 1], [], [-1], [True]):
            with self.assertRaises(ValueError):
                module.validate_selection(dict(value, indices=indices))


if __name__ == "__main__":
    unittest.main()
