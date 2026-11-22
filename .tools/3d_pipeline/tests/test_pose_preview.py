"""tripo/pose_preview.py: a quadruped clip played on exported files without Blender."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "adapter"))
sys.path.insert(0, str(PIPELINE / "tripo"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadruped_layout as ql
import quadruped_wings as qw
from lib import pdx_deform
from test_quadruped_wings import _found, _found_necked

import pose_preview as pp

# The files the route exports are Y up and mirrored against the rig's frame, and scaled: the test writes its mesh the same way.
TO_FILE = np.array([[-0.5, 0.0, 0.0, 0.3], [0.0, 0.0, 0.5, 0.0], [0.0, 0.5, 0.0, -0.2], [0.0, 0.0, 0.0, 1.0]])


def _write_unit(folder: Path, found=_found) -> dict:
    """A blocky winged quadruped as a `.mesh` with the layout's bones and the rig's own weights. Returns its landmarks."""

    points, triangles, landmarks, plans, masks = found()
    if found is _found:
        # the block model has no head the landmark rules can find: name the poll and the muzzle
        landmarks["poll"], landmarks["muzzle"] = np.array([0.0, -0.45, 1.75]), np.array([0.0, -0.7, 1.55])
    layout = ql.build_layout(landmarks)
    indices, weights = ql.skin_weights(points, layout)
    indices, weights = qw.wing_weights(points, triangles, layout.names(), plans, masks, indices, weights, float(landmarks["centre_x"]),
                                       float(landmarks["ground_offset"]) + float(landmarks["belly_z"]))
    moved = points @ TO_FILE[:3, :3].T + TO_FILE[:3, 3]
    data = b"@@b@" + pp._obj("object", 1) + pp._obj("unit", 2) + pp._obj("mesh", 3)
    data += pp._prop("p", "f", [float(v) for p in moved for v in p]) + pp._prop("tri", "i", [int(i) for t in triangles for i in t])
    data += pp._obj("material", 4) + pp._prop("shader", "s", ["PdxMeshAdvanced"])
    ix, w = [], []
    for row_i, row_w in zip(indices, weights):
        ix += [int(i) if value > 0 else -1 for i, value in zip(row_i, row_w)]
        w += [float(value) for value in row_w]
    data += pp._obj("skin", 4) + pp._prop("bones", "i", [4]) + pp._prop("ix", "i", ix) + pp._prop("w", "f", w)
    data += pp._obj("skeleton", 3)
    names = layout.names()
    for index, bone in enumerate(layout.bones):
        head = TO_FILE[:3, :3] @ np.asarray(bone.head, float) + TO_FILE[:3, 3]
        data += pp._obj(bone.name, 4) + pp._prop("ix", "i", [index])
        if bone.parent is not None:
            data += pp._prop("pa", "i", [names.index(bone.parent)])
        data += pp._prop("tx", "f", [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, -float(head[0]), -float(head[1]), -float(head[2])])
    (folder / "beast.mesh").write_bytes(data)
    (folder / "beast_diffuse.dds").write_bytes(b"dds")
    return landmarks


class Frame(unittest.TestCase):
    def test_the_fit_finds_a_mirrored_scaled_frame(self) -> None:
        source = np.random.default_rng(1).uniform(-1, 1, (12, 3))
        matrix, miss = pp.fit_frame(source, source @ TO_FILE[:3, :3].T + TO_FILE[:3, 3])
        self.assertLess(miss, 1e-9)
        np.testing.assert_allclose(matrix, TO_FILE, atol=1e-9)

    def test_landmarks_are_read_from_a_job_root_and_a_logged_result(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        plain = json.loads(json.dumps({key: value for key, value in landmarks.items() if key != "wings"}, default=lambda v: np.asarray(v).tolist()))
        with tempfile.TemporaryDirectory() as temp:
            logs = Path(temp) / "logs" / "adapter"
            logs.mkdir(parents=True)
            (logs / "a.result.json").write_text("[io_pdx] INFO: a log line\n" + json.dumps({"status": "pass"}) + "\n", encoding="utf-8")
            (logs / "b.result.json").write_text("[io_pdx] INFO: a log line\n" + json.dumps({"landmarks": plain}) + "\ntrailing\n", encoding="utf-8")
            read = pp.read_landmarks(Path(temp))
        self.assertAlmostEqual(float(read["height"]), float(landmarks["height"]))
        self.assertIsInstance(read["legs"]["Front_Left"]["top"], np.ndarray)

    def test_settings_change_a_constant_for_one_clip_only(self) -> None:
        before = dict(qw.FOLDED), ql.WINGED_STRIDE
        with pp.Settings({"quadruped_wings.FOLDED": {"sweep": 10.0}, "quadruped_layout.WINGED_STRIDE": 2.0}):
            self.assertEqual(qw.FOLDED["sweep"], 10.0)
            self.assertEqual(qw.FOLDED["curl"], before[0]["curl"], "a dict value updates the keys it names")
            self.assertEqual(ql.WINGED_STRIDE, 2.0)
        self.assertEqual((dict(qw.FOLDED), ql.WINGED_STRIDE), before)
        with self.assertRaises(KeyError):
            with pp.Settings({"quadruped_wings.NO_SUCH": 1.0}):
                pass

    def test_the_export_resamples_24_frames_a_second_to_30(self) -> None:
        self.assertEqual(pp.export_frames("winged_idle"), 91)
        self.assertEqual(pp.export_frames("winged_rear"), 70)
        self.assertEqual(pp.role_styles("winged_quadruped")["defend"], "winged_guard")


class Clips(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.folder = Path(cls.temp.name) / "unit"
        cls.folder.mkdir()
        cls.landmarks = _write_unit(cls.folder)
        cls.out = Path(cls.temp.name) / "out"
        clips = [{"name": "idle", "style": "winged_idle"}, {"name": "defend", "style": "winged_guard"},
                 {"name": "death", "style": "winged_collapse"},
                 {"name": "keys", "style": "winged_guard", "times": [0.0, 0.5], "set": {"quadruped_layout.GUARD_BEND": 20.0}}]
        cls.report = pp.write_folder(cls.folder, cls.landmarks, cls.out, clips)
        cls.mesh = pdx_deform.load_mesh(cls.out / "beast.mesh")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def _posed(self, name: str) -> np.ndarray:
        anim = pdx_deform.load_anim(self.out / f"beast_{name}.anim")
        matrices = pdx_deform.skinning_matrices(self.mesh, anim)
        return np.stack([pdx_deform.skin(self.mesh, frame) for frame in matrices])

    def test_the_folder_is_a_unit_folder(self) -> None:
        self.assertTrue((self.out / "beast_diffuse.dds").exists())
        rows = {row["name"]: row for row in self.report}
        self.assertEqual(rows["idle"]["frames"], 91)
        self.assertEqual(rows["keys"]["frames"], 2)
        self.assertLess(rows["idle"]["frame_fit"], 1e-6, "the layout's bones are the mesh's")
        self.assertIn("roll", rows["death"]["collapse"])

    def test_a_clip_starts_in_the_rest_pose_on_the_ground(self) -> None:
        posed = self._posed("defend")
        height = float(np.ptp(self.mesh.positions[:, 1]))
        for frame in posed[::6]:
            self.assertAlmostEqual(float(frame[:, 1].min()), float(self.mesh.positions[:, 1].min()), delta=1e-4 * height, msg="set on the ground, mixed frames too")

    def test_the_defend_sinks_and_shifts_back_over_planted_hooves(self) -> None:
        posed = self._posed("defend")
        names = np.asarray(self.mesh.bones)[self.mesh.joints[np.arange(len(self.mesh.joints)), np.argmax(self.mesh.weights, axis=1)]]
        torso = np.isin(names, ["Pelvis", "Spine", "Chest"])
        middle = len(posed) // 2
        height = float(np.ptp(self.mesh.positions[:, 1]))
        self.assertLess(float(posed[middle][torso, 1].mean()), float(posed[0][torso, 1].mean()) - 0.002 * height, "the torso sinks")
        hooves = np.char.endswith(names.astype(str), "_Hoof")
        self.assertLess(float(posed[middle][hooves, 1].min() - self.mesh.positions[:, 1].min()), 0.01 * height, "on its hooves, not on its tail")
        # the rig faces -Y, which TO_FILE carries to -Z: back is +Z in the file
        self.assertGreater(float(posed[middle][torso, 2].mean()), float(posed[0][torso, 2].mean()) + 0.01 * height, "and shifts back")

    def test_the_death_ends_on_its_side(self) -> None:
        posed = self._posed("death")
        self.assertLess(float(np.ptp(posed[-1][:, 1])), 0.8 * float(np.ptp(posed[0][:, 1])), "the body lies lower than it stood")

    def test_key_poses_take_the_clips_settings(self) -> None:
        keys, defend = self._posed("keys"), self._posed("defend")
        np.testing.assert_allclose(keys[0], defend[0], atol=1e-6)
        self.assertGreater(float(np.abs(keys[1] - defend[len(defend) // 2]).max()), 1e-3, "a shallower crouch than the kit's")
        self.assertNotEqual(ql.GUARD_BEND, 20.0, "the setting is put back")

    def test_compare_reads_no_difference_against_itself(self) -> None:
        self.assertEqual(set(pp.compare(self.out, self.out).values()), {0.0})


class Rerig(unittest.TestCase):
    """Round 11 (D-107): files made with the withers' neck are tried with the measured neck column without Blender."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        cls.unit, cls.out = root / "unit", root / "out"
        cls.unit.mkdir()
        cls.landmarks = _write_unit(cls.unit, _found_necked)
        cls.report = pp.rerig(cls.unit, pp.as_arrays(cls.landmarks), cls.out)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_the_neck_bones_move_to_the_column_and_the_skin_follows(self) -> None:
        measured = pp.read_landmarks(self.out / "landmarks.json")
        self.assertIn("neck", measured)
        mesh = pdx_deform.load_mesh(self.out / "beast.mesh")
        bind = np.linalg.inv(mesh.inverse_bind[mesh.bones.index("Neck_01")])
        base = TO_FILE[:3, :3] @ np.asarray(measured["neck"]["base"], float) + TO_FILE[:3, 3]
        np.testing.assert_allclose(bind[:3, 3], base, atol=1e-5, err_msg="the neck's bind sits on the column's base")
        self.assertGreater(self.report["reweighted"], 0)
        stage = pp.Stage(mesh, measured)
        self.assertLess(stage.miss / stage.height, 1e-5, "the moved bones are the layout's")
        old = pdx_deform.load_mesh(self.unit / "beast.mesh")
        wings = np.char.startswith(np.asarray(old.bones)[old.joints[:, 0]].astype(str), "Wing") & (old.weights[:, 0] > 0.5)
        np.testing.assert_allclose(mesh.weights[wings], old.weights[wings], atol=1e-6, err_msg="wing skin keeps its weights")

    def test_the_head_front_check_still_fails_wings_behind_the_head(self) -> None:
        """TRIPO-WING-HEAD-FRONT judges the head alone since round 11: wings raised behind the head itself must still fail it."""

        import tripo_checks as tc

        mesh = pdx_deform.load_mesh(self.out / "beast.mesh")
        left, right = tc.wing_sides(mesh)
        head, head_neck, _trunk = tc._parts(mesh, left | right)
        region = tc.head_front_region(head, head_neck)
        self.assertTrue(region.any())
        rest = np.stack([np.eye(4)] * len(mesh.bones))
        self.assertLess(tc.head_front_share(mesh, rest[None], left | right, region), tc.MAX_HEAD_FRONT_SHARE, "wings beside the body")
        # move each wing plate in toward the middle and up, behind the head as seen from the front (the screen of run 9)
        screen = rest.copy()
        for index, name in enumerate(mesh.bones):
            if name.startswith(("WingLeft_", "WingRight_")):
                shift = np.eye(4)
                shift[:3, 3] = (-0.6 if name.startswith("WingLeft_") else 0.6, 0.0, 0.3)
                screen[index] = TO_FILE @ shift @ np.linalg.inv(TO_FILE)
        share = tc.head_front_share(mesh, screen[None], left | right, region)
        self.assertGreater(share, tc.MAX_HEAD_FRONT_SHARE, f"wings standing behind the head frame it ({share:.2f})")

    def test_round_12_measures_catch_a_folded_neck_a_boxed_head_and_a_lost_head(self) -> None:
        """TRIPO-NECK-SQUASH, TRIPO-DEFEND-HEAD-BOXED and TRIPO-DEATH-HEAD-LOST on the rerigged block dragon: each reads its rest pose as
        fine and fails the pose a fresh review of run 19 failed."""

        import tripo_checks as tc

        mesh = pdx_deform.load_mesh(self.out / "beast.mesh")
        left, right = tc.wing_sides(mesh)
        wings = left | right
        head, head_neck, _trunk = tc._parts(mesh, wings)
        named = np.asarray(mesh.bones)[pdx_deform.dominant_bones(mesh)]
        chest = (named == "Chest") & ~wings
        front = tc.front_direction(mesh)
        rest = np.stack([np.eye(4)] * len(mesh.bones))

        def moved(prefixes, shift_rig):
            out = rest.copy()
            shift = np.eye(4)
            shift[:3, 3] = shift_rig
            for index, name in enumerate(mesh.bones):
                if name.startswith(prefixes):
                    out[index] = TO_FILE @ shift @ np.linalg.inv(TO_FILE)
            return out

        self.assertGreater(tc.neck_squash(mesh, rest[None], head, chest)[0], tc.NECK_SQUASH_MIN)
        folded = moved(("Head",), (0.0, 0.45, -0.4))  # the head pulled back and down onto the chest
        self.assertLess(tc.neck_squash(mesh, np.stack([rest, folded]), head, chest)[0], tc.NECK_SQUASH_MIN)
        self.assertGreater(tc.head_lead_over_wings(mesh, rest[None], head, wings, front)[0], tc.DEFEND_HEAD_LEAD)
        hood = moved(("WingLeft_", "WingRight_"), (0.0, -1.0, 0.0))  # the wings brought forward past the head
        self.assertLess(tc.head_lead_over_wings(mesh, np.stack([rest, hood]), head, wings, front)[0], tc.DEFEND_HEAD_LEAD)
        alone = pdx_deform.skin(mesh, moved(("Head",), (0.0, -1.5, 0.0)))  # the head well clear of everything
        self.assertGreater(tc.head_findable(mesh, alone, head, head_neck), tc.DEATH_HEAD_FINDABLE)
        buried = pdx_deform.skin(mesh, moved(("Head",), (0.0, 0.9, -0.5)))  # the head pushed into the chest
        self.assertLess(tc.head_findable(mesh, buried, head, head_neck), tc.DEATH_HEAD_FINDABLE)
        # round 13 leaves the head's own neck out, but a wing laid over the head still loses it
        covered = pdx_deform.skin(mesh, moved(("WingLeft_",), (-0.5, -0.9, 0.5)))
        self.assertLess(tc.head_findable(mesh, covered, head, head_neck), tc.DEATH_HEAD_FINDABLE, "a wing over the head hides it")

    def test_the_fold_spike_fails_an_arm_standing_up_over_the_body(self) -> None:
        """TRIPO-WING-FOLD-SPIKE (round 13): the folded wing's arm raised over the body, as both fresh reviews of run 19 named it, fails."""

        import tripo_checks as tc

        mesh = pdx_deform.load_mesh(self.out / "beast.mesh")
        left, right = tc.wing_sides(mesh)
        named = np.asarray(mesh.bones)[pdx_deform.dominant_bones(mesh)].astype(str)
        arm = np.char.startswith(named, "WingLeft_4") | np.char.startswith(named, "WingRight_4")
        self.assertTrue(arm.any())
        rest = np.stack([np.eye(4)] * len(mesh.bones))
        self.assertLess(tc.fold_spike(mesh, rest[None], arm, ~(left | right))[0], tc.FOLD_SPIKE_MAX)
        raised = rest.copy()
        shift = np.eye(4)
        shift[:3, 3] = (0.0, 0.0, 3.0)  # the arm far up: the screen's up leans back, where the long tail stands highest
        for index, name in enumerate(mesh.bones):
            if name.startswith(("WingLeft_4", "WingRight_4")):
                raised[index] = TO_FILE @ shift @ np.linalg.inv(TO_FILE)
        self.assertGreater(tc.fold_spike(mesh, raised[None], arm, ~(left | right))[0], tc.FOLD_SPIKE_MAX)

    def test_the_winged_humanoid_screen_and_span_checks_judge_a_quadruped_only_in_its_move(self) -> None:
        """QUADRUPED_SCOPE (round 13): no TRIPO-WING-SCREEN for a winged quadruped, and TRIPO-WING-SPAN in its move only."""

        import tripo_checks as tc

        clips = [{"name": name, "style": style, "times": [0.0, 0.5]} for name, style in (("idle", "winged_idle"), ("move", "winged_walk"), ("attack", "winged_rear"))]
        pp.write_folder(self.out, pp.read_landmarks(self.out / "landmarks.json"), self.out, clips)
        mesh = pdx_deform.load_mesh(self.out / "beast.mesh")
        anims = {f"beast_{clip['name']}": pdx_deform.load_anim(self.out / f"beast_{clip['name']}.anim") for clip in clips}
        numbers: dict = {}
        found, _advisory = tc.wing_checks(mesh, anims, True, False, numbers)
        self.assertNotIn("wing_screen", numbers)
        self.assertFalse([item for item in found if item["rule"] == "TRIPO-WING-SCREEN"])
        self.assertEqual(set(numbers.get("wing_span", {})), {"beast_move"})

    def test_a_rerigged_folder_plays_its_clips(self) -> None:
        clips = [{"name": "idle", "style": "winged_idle", "times": [0.0]}, {"name": "attack", "style": "winged_rear", "times": [0.435]}]
        report = pp.write_folder(self.out, pp.read_landmarks(self.out / "landmarks.json"), self.out, clips)
        self.assertEqual([row["name"] for row in report], ["idle", "attack"])
        self.assertTrue((self.out / "beast_attack.anim").exists())


if __name__ == "__main__":
    unittest.main()
