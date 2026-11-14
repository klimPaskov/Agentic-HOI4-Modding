"""The separate-weapon assembler on tiny synthetic GLBs: no orc files, no Blender."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE / "tripo"))

import assemble_separate as asm  # noqa: E402
import clip_check as cc  # noqa: E402

HAND = np.array([0.8, 0.5, 0.0])
JOINT_NAMES = ["mixamorig:Hips", "mixamorig:RightHand", "mixamorig:RightHandIndex1", "mixamorig:RightHandMiddle1", "mixamorig:RightHandRing1"]
WORLD = [np.zeros(3), HAND, HAND + [-0.04, 0, 0], HAND, HAND + [0.04, 0, 0]]


def box_vertices(lo, hi) -> np.ndarray:
    return np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])], dtype=float)


QUADS = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def box_triangles(offset: int = 0) -> np.ndarray:
    tris = []
    for a, b, c, d in QUADS:
        tris += [[a + offset, b + offset, c + offset], [a + offset, c + offset, d + offset]]
    return np.array(tris, dtype=np.int64)


def make_body(clip: str, mesh_name: str = "tripo_node_a", shift_ibm: float = 0.0, hand_name: str = "mixamorig:RightHand", track_y: float = 0.0, scale_y_end: float = 0.0) -> bytes:
    """A box body (hips) with a small fist blob on the right hand, one clip that lowers the hand by `track_y`."""

    names = list(JOINT_NAMES)
    names[1] = hand_name
    nodes = [
        {"name": names[0], "children": [1], "translation": [0, 0, 0]},
        {"name": names[1], "children": [2, 3, 4], "translation": HAND.tolist()},
        {"name": names[2], "translation": [-0.04, 0, 0]},
        {"name": names[3], "translation": [0, 0, 0]},
        {"name": names[4], "translation": [0.04, 0, 0]},
        {"name": mesh_name, "mesh": 0, "skin": 0},
        {"name": "Armature", "children": [5, 0]},
    ]
    glb = asm.Glb({"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [6]}], "nodes": nodes, "meshes": [], "skins": [], "animations": []}, b"")
    torso = box_vertices((-0.5, 0.0, -0.5), (0.5, 1.0, 0.5))
    fist = box_vertices(HAND - 0.05, HAND + 0.05)
    positions = np.concatenate([torso, fist])
    joints = np.zeros((16, 4), np.uint8)
    joints[8:, 0] = [2, 3, 4, 2, 3, 4, 2, 3]  # the fist blob is weighted to the finger joints
    weights = np.zeros((16, 4), np.float32)
    weights[:, 0] = 1.0
    indices = np.concatenate([box_triangles(0), box_triangles(8)]).ravel()
    prim = {
        "attributes": {
            "POSITION": glb.add_accessor(positions, "VEC3", asm.FLOAT, asm.ARRAY_BUFFER, bounds=True),
            "JOINTS_0": glb.add_accessor(joints, "VEC4", asm.UBYTE, asm.ARRAY_BUFFER),
            "WEIGHTS_0": glb.add_accessor(weights, "VEC4", asm.FLOAT, asm.ARRAY_BUFFER),
        },
        "indices": glb.add_accessor(indices, "SCALAR", asm.USHORT, asm.ELEMENT_ARRAY_BUFFER),
    }
    glb.doc["meshes"].append({"name": "body", "primitives": [prim]})
    ibm = np.zeros((5, 4, 4))
    for i, w in enumerate(WORLD):
        ibm[i] = np.eye(4)
        ibm[i, :3, 3] = -w + shift_ibm
    # glTF stores matrices column-major: the translation sits in elements 12..14.
    glb.doc["skins"].append({"joints": [0, 1, 2, 3, 4], "inverseBindMatrices": glb.add_accessor(ibm.transpose(0, 2, 1), "MAT4", asm.FLOAT)})
    times = glb.add_accessor(np.array([0.0, 1.0, 2.0, 3.0]), "SCALAR", asm.FLOAT, bounds=True)
    # The hand zigzags up and down by `track_y`, so the weapon head travels 3 x track_y in the clip.
    moved = np.array([HAND + [0, track_y * (i % 2), 0] for i in range(4)])
    out = glb.add_accessor(moved, "VEC3", asm.FLOAT)
    anim = {"name": clip, "samplers": [{"input": times, "output": out, "interpolation": "LINEAR"}], "channels": [{"sampler": 0, "target": {"node": 1, "path": "translation"}}]}
    if scale_y_end:
        squash = glb.add_accessor(np.array([[1, 1, 1], [1, scale_y_end, 1], [1, scale_y_end, 1], [1, scale_y_end, 1]]), "VEC3", asm.FLOAT)
        anim["samplers"].append({"input": times, "output": squash, "interpolation": "LINEAR"})
        anim["channels"].append({"sampler": 1, "target": {"node": 0, "path": "scale"}})
    glb.doc["animations"].append(anim)
    return glb.to_bytes()


def make_weapon() -> bytes:
    """A haft along +y (0..1) with a wide head on top, a material with one embedded image."""

    haft = box_vertices((-0.02, 0.0, -0.02), (0.02, 1.0, 0.02))
    head = box_vertices((-0.15, 0.8, -0.02), (0.15, 1.0, 0.02))
    positions = np.concatenate([haft, head])
    indices = np.concatenate([box_triangles(0), box_triangles(8)]).ravel()
    glb = asm.Glb({"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"name": "tripo_node_w", "mesh": 0}], "meshes": [], "materials": [], "images": [], "textures": [], "samplers": [{"magFilter": 9729}]}, b"")
    attrs = {
        "POSITION": glb.add_accessor(positions, "VEC3", asm.FLOAT, asm.ARRAY_BUFFER, bounds=True),
        "NORMAL": glb.add_accessor(np.tile([0.0, 0.0, 1.0], (16, 1)), "VEC3", asm.FLOAT, asm.ARRAY_BUFFER),
        "TEXCOORD_0": glb.add_accessor(np.zeros((16, 2)), "VEC2", asm.FLOAT, asm.ARRAY_BUFFER),
    }
    view = glb.add_view(b"\xff\xd8weapon-image-bytes")
    glb.doc["images"].append({"bufferView": view, "mimeType": "image/jpeg"})
    glb.doc["textures"].append({"source": 0, "sampler": 0})
    glb.doc["materials"].append({"name": "weapon_mat", "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}}, "extensions": {"KHR_materials_volume": {}}})
    glb.doc["meshes"].append({"name": "w", "primitives": [{"mode": 4, "material": 0, "attributes": attrs, "indices": glb.add_accessor(indices, "SCALAR", asm.UINT, asm.ELEMENT_ARRAY_BUFFER)}]})
    return glb.to_bytes()


class Workspace(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name: str, data: bytes) -> Path:
        path = self.dir / name
        path.write_bytes(data)
        return path


class Merge(Workspace):
    def test_two_single_clip_files_give_both_clips(self) -> None:
        a = self.write("a.glb", make_body("idle", "tripo_node_a"))
        b = self.write("b.glb", make_body("chop", "tripo_node_other", track_y=0.2))
        merged, report = asm.merge_body_clips([a, b])
        self.assertEqual(report["clips"], ["idle", "chop"])
        rig = cc.Rig(merged.to_bytes(), asm.BODY_NODE, None)
        clips = {name: (tracks, end) for name, tracks, end in rig.clips()}
        self.assertEqual(set(clips), {"idle", "chop"})
        times, values = clips["chop"][0][1]["translation"]
        self.assertEqual(times.tolist(), [0.0, 1.0, 2.0, 3.0])
        self.assertAlmostEqual(float(values[1][1]), 0.5 + 0.2, places=5)
        names = [n.get("name") for n in merged.doc["nodes"]]
        self.assertIn(asm.BODY_NODE, names)
        self.assertNotIn("tripo_node_a", names)

    def test_mismatched_inverse_bind_matrices_fail(self) -> None:
        a = self.write("a.glb", make_body("idle"))
        b = self.write("b.glb", make_body("chop", shift_ibm=0.01))
        with self.assertRaisesRegex(asm.AssembleError, "inverse bind matrix"):
            asm.merge_body_clips([a, b])

    def test_mismatched_joint_names_fail(self) -> None:
        a = self.write("a.glb", make_body("idle"))
        b = self.write("b.glb", make_body("chop", hand_name="mixamorig:LeftHand"))
        with self.assertRaisesRegex(asm.AssembleError, "node names"):
            asm.merge_body_clips([a, b])

    def test_a_repeated_clip_name_fails(self) -> None:
        a = self.write("a.glb", make_body("idle"))
        b = self.write("b.glb", make_body("idle"))
        with self.assertRaisesRegex(asm.AssembleError, "already in"):
            asm.merge_body_clips([a, b])

    def test_a_weaponless_file_is_not_taken_from_a_folder(self) -> None:
        self.write("body.glb", make_body("idle"))
        self.write("axe.glb", make_weapon())
        files = asm.gather_body_files([str(self.dir)])
        self.assertEqual([f.name for f in files], ["body.glb"])


class Assemble(Workspace):
    def run_assemble(self, verify: bool = False, max_tilt: float = 25.0, grip_range=(0.2, 0.7)) -> dict:
        a = self.write("a.glb", make_body("idle"))
        b = self.write("b.glb", make_body("chop", track_y=0.5))
        weapon = self.write("w.glb", make_weapon())
        out = self.dir / "out.glb"
        report = asm.assemble([a, b], weapon, out, 1.06, 0.6, "RightHand", grip_range, max_tilt, trade_tilts=(), fit_frames=3, directions=60, rolls=6, candidates=3, weapon_triangles=10, verify=verify, selection_samples=4, log=lambda *_: None)
        self.out = out
        return report

    def test_weapon_is_scaled_to_the_ratio_and_bound_to_the_hand(self) -> None:
        report = self.run_assemble()
        rig = cc.Rig(self.out, asm.BODY_NODE, asm.WEAPON_NODE)
        height = float(rig.body["positions"][:, 1].max() - rig.body["positions"][:, 1].min())
        rest = rig.skin(rig.weapon, rig.skin_mats(rig.joint_worlds({})))
        axis = asm.pca_axis(rest)
        length = float(np.ptp((rest - rest.mean(axis=0)) @ axis))
        self.assertAlmostEqual(length, 1.06 * height, places=3)
        hand = rig.joint_names.index("mixamorig:RightHand")
        self.assertTrue((rig.weapon["joint_ids"][:, 0] == hand).all())
        self.assertTrue(np.allclose(rig.weapon["weights"][:, 0], 1.0))
        self.assertEqual(report["weapon"]["bound_to"], "mixamorig:RightHand")
        self.assertTrue(report["weapon"]["above_triangle_target"])
        self.assertFalse(report["weapon"]["head_was_at_negative_end_of_pca_axis"])
        # The chosen grip point (that share of the length from the butt) sits at the palm, the head end above it.
        direction = np.array(report["pose"]["haft_direction_butt_to_head_rest_world"])
        share = report["pose"]["grip"]
        along = (rest - np.array(report["grip_geometry"]["palm_rest_world"])) @ direction
        self.assertAlmostEqual(float(along.min()), -share * 1.06 * height, places=2)
        self.assertAlmostEqual(float(along.max()), (1 - share) * 1.06 * height, places=2)

    def test_output_has_the_in_hand_route_shape(self) -> None:
        self.run_assemble()
        doc, _ = cc.load_glb(self.out)
        mesh_nodes = sorted(n["name"] for n in doc["nodes"] if "mesh" in n)
        self.assertEqual(mesh_nodes, [asm.BODY_NODE, asm.WEAPON_NODE])
        self.assertEqual(len(doc["skins"]), 1)
        self.assertTrue(all(n["skin"] == 0 for n in doc["nodes"] if "mesh" in n))
        self.assertEqual([a["name"] for a in doc["animations"]], ["idle", "chop"])
        self.assertEqual(len(doc["images"]), 1)
        material = doc["materials"][-1]
        self.assertNotIn("extensions", material)
        texture = doc["textures"][material["pbrMetallicRoughness"]["baseColorTexture"]["index"]]
        view = doc["bufferViews"][doc["images"][texture["source"]]["bufferView"]]
        _, binary = cc.load_glb(self.out)
        self.assertEqual(binary[view["byteOffset"] : view["byteOffset"] + view["byteLength"]], b"\xff\xd8weapon-image-bytes")

    def test_the_fit_moves_a_stick_out_of_a_box_body(self) -> None:
        report = self.run_assemble(verify=True)
        table = report["clip_check"]
        naive = [c["weapon_deep_in_body_pct"] for c in table["naive"].values()]
        fitted = [c["weapon_deep_in_body_pct"] for c in table["fitted"].values()]
        self.assertGreater(max(naive), 100 * cc.MAX_IN_BODY_SHARE, "the naive haft along the fist axis should go through the box")
        self.assertLessEqual(max(fitted), 100 * cc.MAX_IN_BODY_SHARE)
        self.assertEqual(set(table["fitted_passes"]), {"idle", "chop"})
        self.assertEqual(report["pose"]["roles"]["attack"]["best_passing_clip"], "chop")

    def test_the_haft_stays_within_the_tilt_of_up_in_idle(self) -> None:
        for limit in (10.0, 25.0):
            report = self.run_assemble(verify=True, max_tilt=limit)
            self.assertLessEqual(report["pose"]["tilt_from_up_deg_in_idle"], limit + 0.5)
            self.assertGreater(report["pose"]["lowest_weapon_point_above_ground_cm_in_idle"], -0.01)
            self.assertIn("max_tilt_%g" % limit, report["trade"])
        # The same limit, measured on the rest pose when the named clip is absent.
        a = self.write("a.glb", make_body("idle"))
        weapon = self.write("w.glb", make_weapon())
        report = asm.assemble([a], weapon, self.dir / "r.glb", 1.06, 0.6, "RightHand", (0.2, 0.7), 15.0, "no_such_clip", {"idle": "idle"}, (), fit_frames=2, directions=40, rolls=4, candidates=2, verify=False, log=lambda *_: None)
        self.assertEqual(report["fit"]["tilt_clip"], "rest pose")

    def test_the_grip_slides_so_the_butt_clears_the_ground(self) -> None:
        # The hand is 0.5 high and the weapon 1.06 long: held upright at the recorded 0.6 the butt is 0.14 below the ground.
        report = self.run_assemble(verify=True, max_tilt=10.0, grip_range=(0.2, 0.7))
        grip = report["pose"]["grip"]
        self.assertLess(grip, 0.5)
        self.assertGreaterEqual(grip, 0.2)
        self.assertGreater(report["pose"]["lowest_weapon_point_above_ground_cm_in_idle"], -0.01)
        self.assertLess(grip, 0.5 / (1.06 * np.cos(np.radians(10.0))) + 1e-3)  # any larger grip sinks the butt

    def test_a_grip_range_that_cannot_satisfy_the_hard_rules_is_refused(self) -> None:
        with self.assertRaisesRegex(asm.AssembleError, "no pose meets the hard rules"):
            self.run_assemble(max_tilt=10.0, grip_range=(0.6, 0.7))


class Measures(Workspace):
    """The fist, the weapon head path, the death test, and clip names given as prefixes."""

    def multi_clip_body(self, **clips) -> Path:
        """One body GLB holding several clips: name -> make_body keywords."""

        files = [self.write(f"{name}.glb", make_body(name, **kw)) for name, kw in clips.items()]
        merged, _ = asm.merge_body_clips(files)
        return self.write("multi.glb", merged.to_bytes())

    def go(self, body: Path, roles: dict, **kw) -> dict:
        weapon = self.write("w.glb", make_weapon())
        args = dict(grip_range=(0.2, 0.7), max_tilt=25.0, trade_tilts=(), fit_frames=3, directions=60, rolls=6, candidates=3, selection_samples=4, log=lambda *_: None)
        args.update(kw)
        return asm.assemble([body], weapon, self.dir / "out.glb", 1.06, 0.6, "RightHand", roles=roles, **args)

    def test_fist_axis_from_joints_follows_the_row_of_knuckles_and_the_flexion_planes(self) -> None:
        names, pos = [], []
        for f, finger in enumerate(("Index", "Middle", "Ring", "Pinky")):
            for k in (1, 2, 3, 4):
                names.append(f"mixamorig:RightHand{finger}{k}")
                pos.append([0.03 * (k - 1), 0.01 * (k - 1) ** 2, 0.02 * f])  # each finger curls in its own plane z = const
        axis, details = asm.fist_hole_axis(names, "mixamorig:RightHand", np.array(pos))
        self.assertGreater(abs(float(axis @ [0, 0, 1])), 0.999)
        self.assertLess(details["knuckle_vs_flexion_deg"], 5.0)
        self.assertEqual(details["fingers_used"], 4)

    def test_one_body_file_with_many_clips_and_clip_prefixes(self) -> None:
        body = self.multi_clip_body(idle={}, chop={"track_y": 0.5}, collapse={"scale_y_end": 0.3})
        report = self.go(body, {"idl": "idle", "ch": "attack", "coll": "death"})
        self.assertEqual(report["clips_in_body"], ["idle", "chop", "collapse"])
        self.assertEqual(report["fit"]["role_map"], {"idle": "idle", "chop": "attack", "collapse": "death"})
        with self.assertRaisesRegex(asm.AssembleError, "several"):
            self.go(body, {"c": "attack", "idle": "idle"})

    def test_the_haft_axis_passes_through_the_fist_and_the_numbers_are_reported(self) -> None:
        body = self.multi_clip_body(idle={}, chop={"track_y": 0.5})
        report = self.go(body, {"idle": "idle", "chop": "attack"})
        fist = report["pose"]["fist"]
        self.assertLessEqual(fist["rest"]["distance_cm"], fist["fist_radius_cm"] + 1e-6)
        self.assertLessEqual(fist["idle"]["distance_cm_worst"], fist["fist_radius_cm"] + 1e-6)
        self.assertGreaterEqual(fist["rest"]["angle_deg"], 0.0)
        self.assertGreater(report["grip_geometry"]["finger_vertices"], 3)

    def test_the_head_must_travel_to_make_an_attack(self) -> None:
        body = self.multi_clip_body(idle={}, chop={"track_y": 0.5}, twitch={"track_y": 0.1})
        report = self.go(body, {"idle": "idle", "chop": "attack", "twitch": "attack"})
        roles = report["pose"]["clip_roles"]
        self.assertAlmostEqual(roles["chop"]["head_travel_body_heights"], 1.5, delta=0.1)
        self.assertAlmostEqual(roles["twitch"]["head_travel_body_heights"], 0.3, delta=0.05)
        self.assertGreater(roles["chop"]["head_max_speed_body_heights_per_s"], 0.4)
        self.assertAlmostEqual(roles["_idle_baseline"]["head_travel_body_heights"], 0.0, delta=0.01)
        status = report["pose"]["roles"]["attack"]
        self.assertEqual(status["best_passing_clip"], "chop")
        self.assertTrue(status["clips"]["twitch"].startswith("not an attack"))
        only_twitch = self.go(body, {"idle": "idle", "twitch": "attack"})
        self.assertIsNone(only_twitch["pose"]["roles"]["attack"]["best_passing_clip"])

    def test_a_death_must_end_on_the_ground_and_the_fallen_clip_gets_the_lying_tolerance(self) -> None:
        body = self.multi_clip_body(idle={}, collapse={"scale_y_end": 0.3}, stand={})
        report = self.go(body, {"idle": "idle", "collapse": "death", "stand": "death"})
        roles = report["pose"]["clip_roles"]
        self.assertAlmostEqual(roles["collapse"]["last_frame_extent_pct_of_standing_height"], 30.0, delta=2.0)
        self.assertTrue(roles["collapse"]["eligible"])
        self.assertFalse(roles["stand"]["eligible"])
        self.assertEqual(roles["collapse"]["ground_tolerance_pct"], 100 * asm.DEATH_GROUND_TOLERANCE_SHARE)
        self.assertEqual(roles["stand"]["ground_tolerance_pct"], 100 * cc.FRAME_GROUND_TOLERANCE_SHARE)
        self.assertTrue(report["pose"]["roles"]["death"]["clips"]["stand"].startswith("not a death"))
        self.assertNotEqual(report["pose"]["roles"]["death"]["best_passing_clip"], "stand")

    def test_clip_check_takes_its_own_ground_tolerance_for_named_clips(self) -> None:
        body = self.multi_clip_body(idle={}, collapse={"scale_y_end": 0.3})
        self.go(body, {"idle": "idle", "collapse": "death"})
        out = self.dir / "out.glb"
        strict = cc.check(out, per_frame_ground=True, samples=4)["clips"]["collapse"]["weapon_below_ground_pct"]
        lax = cc.check(out, per_frame_ground=True, samples=4, ground_tolerance_by_clip={"collapse": 5.0})["clips"]["collapse"]["weapon_below_ground_pct"]
        self.assertLessEqual(lax, strict)
        self.assertEqual(lax, 0.0)


if __name__ == "__main__":
    unittest.main()
