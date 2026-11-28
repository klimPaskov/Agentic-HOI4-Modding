"""Moving clips between rigs by each bone's turn from rest (lib/clip_transfer.py). The small rigged GLB of rig_glb.py, with a right thigh
added so the body has a frame. No Blender."""

from __future__ import annotations

import json
import math
import struct
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import rig_glb as RG
from lib import clip_transfer as C


def renamed_copy(source: Path, target: Path) -> None:
    """The same GLB with every Left and Right joint name swapped: its sides named the wrong way round, as Tripo named the ZIN devil's."""

    data = source.read_bytes()
    length = struct.unpack("<I", data[12:16])[0]
    doc = json.loads(data[20:20 + length])
    rest = data[20 + length:]
    for node in doc["nodes"]:
        name = node.get("name", "")
        if ":Left" in name:
            node["name"] = name.replace(":Left", ":Right")
        elif ":Right" in name:
            node["name"] = name.replace(":Right", ":Left")
    text = json.dumps(doc).encode()
    text += b" " * (-len(text) % 4)
    target.write_bytes(b"glTF" + struct.pack("<II", 2, 12 + 8 + len(text) + len(rest)) + struct.pack("<I", len(text)) + b"JSON" + text + rest)


def turned_copy(source: Path, target: Path, degrees: float) -> None:
    """The same GLB with its hips turned `degrees` about the up axis at rest: a body that faces another way."""

    data = source.read_bytes()
    length = struct.unpack("<I", data[12:16])[0]
    doc = json.loads(data[20:20 + length])
    rest = data[20 + length:]
    for node in doc["nodes"]:
        if node.get("name") == "mixamorig:Hips":
            half = math.radians(degrees) / 2
            node["rotation"] = [0.0, math.sin(half), 0.0, math.cos(half)]
    text = json.dumps(doc).encode()
    text += b" " * (-len(text) % 4)
    target.write_bytes(b"glTF" + struct.pack("<II", 2, 12 + 8 + len(text) + len(rest)) + struct.pack("<I", len(text)) + b"JSON" + text + rest)


class RigCase(unittest.TestCase):
    def setUp(self) -> None:
        saved = list(RG.CHAIN)
        RG.CHAIN.append(("mixamorig:RightUpLeg", 0, (-0.1, -0.1, 0.0)))
        # feet and toes, so the body's front comes from its anatomy (the toes point to +z)
        RG.CHAIN.append(("mixamorig:LeftFoot", 4, (0.0, -0.45, 0.0)))
        RG.CHAIN.append(("mixamorig:LeftToeBase", len(RG.CHAIN) - 1, (0.0, -0.05, 0.1)))
        RG.CHAIN.append(("mixamorig:RightLeg", 7, (0.0, -0.45, 0.0)))
        RG.CHAIN.append(("mixamorig:RightFoot", len(RG.CHAIN) - 1, (0.0, -0.45, 0.0)))
        RG.CHAIN.append(("mixamorig:RightToeBase", len(RG.CHAIN) - 1, (0.0, -0.05, 0.1)))
        self.addCleanup(lambda: RG.CHAIN.__setitem__(slice(None), saved))
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.source = self.folder / "source.glb"
        RG.write_rig_glb(self.source, extra_joint=None, clips=("idle",))

    def local_spine(self, path: Path) -> np.ndarray:
        rig = C.Rig(path)
        channels = rig.clips()["idle"]
        spine = rig.joints["Spine"]
        _times, values = channels[spine]["rotation"]
        return values[1]


class Transfer(RigCase):
    def test_the_same_rig_gets_the_same_clip(self) -> None:
        out = self.folder / "out.glb"
        report = C.transfer(self.source, self.source, out, ["idle"])
        self.assertEqual(report["clips"], ["idle"])
        np.testing.assert_allclose(np.abs(self.local_spine(out)), np.abs(np.array(RG.LEAN[1])), atol=1e-5)

    def test_a_body_that_faces_the_other_way_gets_the_same_lean_in_its_own_frame(self) -> None:
        target, out = self.folder / "turned.glb", self.folder / "out.glb"
        turned_copy(self.source, target, 180.0)
        C.transfer(self.source, target, out, ["idle"])
        # the spine leans forward in the body's own frame, so its local turn is the source's, not mirrored
        np.testing.assert_allclose(np.abs(self.local_spine(out)), np.abs(np.array(RG.LEAN[1])), atol=1e-5)

    def test_the_hips_keep_their_motion_but_not_a_held_level_offset(self) -> None:
        """Tripo's run on the demo goblin held the hips off their rest spot in every frame; the route plays clips in place."""

        out = self.folder / "out.glb"
        C.transfer(self.source, self.source, out, ["idle"])
        rig = C.Rig(out)
        _times, values = rig.clips()["idle"][rig.joints["Hips"]]["translation"]
        rest = np.asarray(rig.nodes[rig.joints["Hips"]].get("translation", [0.0, 0.0, 0.0]))
        np.testing.assert_allclose((values - rest)[:, [0, 2]].mean(axis=0), [0.0, 0.0], atol=1e-6)
        self.assertGreater(float(np.ptp(values[:, 1])), 0.01, "the bob up and down stays")

    def test_the_body_faces_its_toes_and_a_rig_named_the_wrong_way_round_is_found(self) -> None:
        rig = C.Rig(self.source)
        np.testing.assert_allclose(C.body_frame(rig)[:, 2], [0.0, 0.0, 1.0], atol=1e-6)
        self.assertFalse(C.mirrored(rig))
        swapped = self.folder / "swapped.glb"
        renamed_copy(self.source, swapped)
        self.assertTrue(C.mirrored(C.Rig(swapped)))

    def test_a_rig_named_the_wrong_way_round_takes_each_side_from_the_same_side_of_the_body(self) -> None:
        swapped, out = self.folder / "swapped.glb", self.folder / "out.glb"
        renamed_copy(self.source, swapped)
        self.assertEqual(C.limb_chains(C.Rig(self.source), C.Rig(swapped), True)[0][0], C.Rig(swapped).joints["LeftUpLeg"])
        C.transfer(self.source, swapped, out, ["idle"])
        np.testing.assert_allclose(np.abs(self.local_spine(out)), np.abs(np.array(RG.LEAN[1])), atol=1e-5)

    def test_keep_target_clips_adds_the_moved_clip_beside_the_targets_own(self) -> None:
        """A clip made on a motion donor for one role joins the unit's other clips, and a same-named clip is replaced (2026-11-28)."""

        target = self.folder / "own.glb"
        rig = C.Rig(self.source)
        doc = json.loads(json.dumps(rig.doc))
        doc["animations"][0]["name"] = "stand"
        C.write_glb(target, doc, rig.blob)
        only, both = self.folder / "only.glb", self.folder / "both.glb"
        C.transfer(self.source, target, only, ["idle"])
        report = C.transfer(self.source, target, both, ["idle"], keep_target_clips=True)
        self.assertEqual(sorted(C.Rig(only).clips()), ["idle"])
        self.assertEqual(sorted(C.Rig(both).clips()), ["idle", "stand"])
        self.assertEqual(report["kept"], ["stand"])
        again = self.folder / "again.glb"
        C.transfer(self.source, both, again, ["idle"], keep_target_clips=True)
        self.assertEqual(sorted(C.Rig(again).clips()), ["idle", "stand"], "a moved clip replaces the target's clip of the same name")

    def test_a_missing_clip_is_named(self) -> None:
        with self.assertRaises(C.TransferError):
            C.transfer(self.source, self.source, self.folder / "out.glb", ["swagger"])


class DonorIntake(RigCase):
    """The default route for a made clip: made on the motion donor, dropped in the inbox as `<slug>__donor.glb`, and carried onto the
    unit's rig by the intake beside the unit's own clips (so no Tripo page that draws the unit's heavy model is needed for it)."""

    def inbox(self) -> Path:
        import tripo_intake  # noqa: F401  (the import must work before the tests use it)

        inbox = self.folder / "inbox"
        inbox.mkdir()
        rig = C.Rig(self.source)
        doc = json.loads(json.dumps(rig.doc))
        doc["animations"][0]["name"] = "walk"
        C.write_glb(inbox / "u__rigged.glb", doc, rig.blob)
        donor = json.loads(json.dumps(rig.doc))
        donor["animations"][0]["name"] = "A hunched brute lunges"
        C.write_glb(inbox / "u__donor.glb", donor, rig.blob)
        return inbox

    def test_the_intake_finds_the_donor_and_merges_its_clips_beside_the_units_own(self) -> None:
        sys.path.insert(0, str(PIPELINE))
        import tripo_intake

        inbox = self.inbox()
        spec = {"asset_kind": "humanoid", "tripo": {"roles": {"move": "walk", "attack": "A hunched brute"}}}
        files = tripo_intake.intake_files(spec, "u", inbox)
        self.assertEqual(sorted(files), ["donor", "rigged"])
        job = self.folder / "job"
        report = tripo_intake.merge_donor_clips(spec, files, job)
        merged = job / "provider" / tripo_intake.DONOR_MERGED
        self.assertEqual(sorted(C.Rig(merged).clips()), ["A hunched brute lunges", "walk"])
        self.assertEqual(report["kept"], ["walk"])
        tripo_intake.refuse_unknown_role_clips(spec, merged)  # both roles name a clip of the merged file

    def test_donor_clips_names_the_clips_to_carry(self) -> None:
        import tripo_intake

        inbox = self.inbox()
        spec = {"asset_kind": "humanoid", "tripo": {"donor_clips": ["nothing like it"]}}
        with self.assertRaisesRegex(ValueError, "unit's own Animate page"):
            tripo_intake.merge_donor_clips(spec, tripo_intake.intake_files(spec, "u", inbox), self.folder / "job")

    def test_no_donor_file_changes_nothing(self) -> None:
        import tripo_intake

        inbox = self.inbox()
        (inbox / "u__donor.glb").unlink()
        spec = {"asset_kind": "humanoid", "tripo": {}}
        files = tripo_intake.intake_files(spec, "u", inbox)
        self.assertEqual(sorted(files), ["rigged"])
        self.assertIsNone(tripo_intake.merge_donor_clips(spec, files, self.folder / "job"))

    def test_an_armed_unit_is_told_to_carry_the_clips_onto_its_body_before_the_grip_stage(self) -> None:
        import tripo_intake

        inbox = self.inbox()
        spec = {"asset_kind": "humanoid", "tripo": {"weapon": {"bone": "Weapon"}}}
        with self.assertRaisesRegex(ValueError, "arm_unit"):
            tripo_intake.intake_files(spec, "u", inbox)


if __name__ == "__main__":
    unittest.main()
