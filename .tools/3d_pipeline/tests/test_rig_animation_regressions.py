"""Provider-free regressions for rig, promotion, stream, and root-channel defects found in pilot units."""

from __future__ import annotations

import ast
import hashlib
import json
import math
import re
import types
import unittest
from pathlib import Path


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
WORKER = PIPELINE_ROOT / "adapter/blender_worker.py"
TREE = ast.parse(WORKER.read_text(encoding="utf-8"))
STREAM_INDEX_BUDGET = 65535


def worker_function(name: str) -> ast.FunctionDef:
    return next(node for node in TREE.body if isinstance(node, ast.FunctionDef) and node.name == name)


def load_functions(names: set[str], namespace: dict) -> dict:
    nodes: list[ast.stmt] = [ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
    nodes += [
        node
        for node in TREE.body
        if isinstance(node, ast.FunctionDef) and (node.name in names or (
            "_promotion_" in names and node.name.startswith("_promotion_")
        ))
    ]
    module = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    namespace = {"Any": object, "Dict": dict, "List": list, "Tuple": tuple, "math": math, "json": json,
                 "hashlib": hashlib, "re": re, "Path": Path, **namespace}
    exec(compile(module, str(WORKER), "exec"), namespace)
    return namespace


class Props(dict):
    """An ID-like block with custom properties and attributes."""

    __hash__ = object.__hash__

    def __init__(self, name: str = "", props: dict | None = None, **attributes) -> None:
        super().__init__(props or {})
        self.name = name
        self.__dict__.update(attributes)

    def __eq__(self, other: object) -> bool:
        return self is other


class Tracks(list):
    def remove(self, track) -> None:  # noqa: D401 - mirrors bpy collection removal
        super().remove(track)


class FakeAction:
    def __init__(self, name: str) -> None:
        self.name = name

    def copy(self) -> "FakeAction":
        return FakeAction(self.name)


class FakeAnimation:
    def __init__(self, action=None, tracks=None, drivers=None) -> None:
        self.action = action
        self.nla_tracks = Tracks(tracks or [])
        self.drivers = drivers or []


class FakeObject(Props):
    def __init__(self, name: str, animation: FakeAnimation | None = None) -> None:
        super().__init__(name, animation_data=animation, data=None, parent=None, modifiers=[],
                         matrix_parent_inverse=None, hide_render=False)
        self.hidden = False

    def copy(self) -> "FakeObject":
        # Blender's Object.copy() duplicates animation data, including NLA tracks.
        duplicate = FakeObject(self.name + ".001")
        if self.animation_data is not None:
            duplicate.animation_data = FakeAnimation(self.animation_data.action, list(self.animation_data.nla_tracks))
        return duplicate

    def animation_data_create(self) -> FakeAnimation:
        if self.animation_data is None:
            self.animation_data = FakeAnimation()
        return self.animation_data

    def hide_set(self, value: bool) -> None:
        self.hidden = value


class WorkingRigCopyTests(unittest.TestCase):
    """Fix 7: copying the provider rig also copied the glTF importer's NLA track."""

    def test_working_copy_has_no_nla_tracks_and_source_keeps_its_evidence(self) -> None:
        ns = load_functions({"duplicate_hierarchy"}, {})
        track = types.SimpleNamespace(name="NlaTrack")
        source = FakeObject("Armature", FakeAnimation(FakeAction("Armature|Walk"), [track]))
        working = types.SimpleNamespace(objects=types.SimpleNamespace(link=lambda obj: None))
        (duplicate,) = ns["duplicate_hierarchy"]([source], None, working)
        self.assertEqual(list(duplicate.animation_data.nla_tracks), [])
        self.assertEqual(duplicate.animation_data.action.name, "Armature|Walk_WORKING")
        self.assertEqual(list(source.animation_data.nla_tracks), [track])
        self.assertTrue(source["hoi4_source_protected"])


class PromotionNlaTests(unittest.TestCase):
    """Fix 8: promotion refused the protected provider armature because of its imported NLA track."""

    def setUp(self) -> None:
        bpy = types.SimpleNamespace(types=types.SimpleNamespace(ID=Props))
        self.ns = load_functions({"_promotion_"}, {"bpy": bpy})

    def block(self, props: dict, *, drivers=None, mute: bool = False) -> Props:
        strip = types.SimpleNamespace(name="Walk", action=FakeAction("Armature|Walk"), frame_start=1.0, frame_end=25.0)
        track = types.SimpleNamespace(name="NlaTrack", mute=mute, strips=[strip])
        animation = FakeAnimation(None, [track], drivers)
        animation.bl_rna = types.SimpleNamespace(properties=[])
        return Props("Armature", props, animation_data=animation)

    def test_protected_source_nla_is_fingerprinted(self) -> None:
        for marker in ("hoi4_source_protected", "hoi4_reference_read_only"):
            with self.subTest(marker=marker):
                state = self.ns["_promotion_animation_state"](self.block({marker: True}))
                self.assertEqual(state["nla_tracks"], [{
                    "name": "NlaTrack",
                    "mute": False,
                    "strips": [{"name": "Walk", "action": "Armature|Walk", "frame_start": 1.0, "frame_end": 25.0}],
                }])
                muted = self.ns["_promotion_animation_state"](self.block({marker: True}, mute=True))
                self.assertNotEqual(self.ns["_promotion_digest"](state), self.ns["_promotion_digest"](muted))

    def test_editable_nla_and_drivers_still_refuse(self) -> None:
        cases = (({}, None), ({"hoi4_source_protected": True}, ["driver"]))
        for props, drivers in cases:
            with self.subTest(props=props, drivers=drivers), self.assertRaisesRegex(ValueError, "driver/NLA"):
                self.ns["_promotion_animation_state"](self.block(props, drivers=drivers))


class HumanoidStreamBudgetTests(unittest.TestCase):
    """Fix 9: the 30,000-triangle humanoid working mesh exported one 89,997-index stream."""

    def test_humanoid_working_mesh_fits_one_export_stream(self) -> None:
        profiles = json.loads((PIPELINE_ROOT / "config/asset_profiles.json").read_text(encoding="utf-8"))["profiles"]
        triangles = profiles["humanoid_unit"]["triangle_range"]
        self.assertLessEqual(triangles["working_triangle_target"] * 3, STREAM_INDEX_BUDGET)
        self.assertGreaterEqual(triangles["working_triangle_target"], triangles["preferred_min"])


class FakeKeyframe:
    def __init__(self, frame: float, value: float) -> None:
        self.co = [frame, value]
        self.handle_left = [frame, value]
        self.handle_right = [frame, value]


class FakeCurve:
    def __init__(self, index: int, values: list[float]) -> None:
        self.data_path = 'pose.bones["Hips"].location'
        self.array_index = index
        self.keyframe_points = [FakeKeyframe(float(frame), value) for frame, value in enumerate(values)]

    def update(self) -> None:
        pass

    def values(self) -> list[float]:
        return [point.co[1] for point in self.keyframe_points]

    def at(self, frame: int) -> float:
        return next(point.co[1] for point in self.keyframe_points if point.co[0] == frame)


class MeshyRigWorld:
    """A glTF-imported Meshy rig: Hips local Y is vertical, local Z is nearly horizontal."""

    RESPONSES = (0.0, 1.0, 0.01)
    GROUND_OFFSET = -0.5

    def __init__(self) -> None:
        self.frame = 0
        self.curves = [FakeCurve(0, [0.0, 5.0, 10.0]), FakeCurve(1, [0.3, 0.1, 0.3]), FakeCurve(2, [0.0, 2.0, 4.0])]
        self.hips = types.SimpleNamespace(location=[0.0, 0.0, 0.0])
        action = types.SimpleNamespace(name="Armature|Walk_WORKING", frame_range=(0.0, 2.0))
        self.rig = types.SimpleNamespace(
            name="Armature",
            animation_data=types.SimpleNamespace(action=action),
            matrix_world=types.SimpleNamespace(to_scale=lambda: types.SimpleNamespace(z=1.0)),
            pose=types.SimpleNamespace(bones={"Hips": self.hips}),
        )
        scene = types.SimpleNamespace(frame_set=self.frame_set)
        self.bpy = types.SimpleNamespace(context=types.SimpleNamespace(scene=scene, view_layer=types.SimpleNamespace(update=lambda: None)))

    def frame_set(self, frame: int) -> None:
        self.frame = frame

    def minimum_z(self) -> float:
        value = self.GROUND_OFFSET
        for curve in self.curves:
            value += self.RESPONSES[curve.array_index] * curve.at(self.frame)
        return value + sum(response * offset for response, offset in zip(self.RESPONSES, self.hips.location))

    def bounds(self, _objects):
        point = types.SimpleNamespace(z=self.minimum_z())
        return point, point

    def namespace(self) -> dict:
        return {
            "bpy": self.bpy,
            "armatures": lambda: [self.rig],
            "action_fcurves": lambda action: [(curve, None) for curve in self.curves],
            "evaluated_world_bounds": self.bounds,
            "mesh_objects": lambda: [],
        }


class RootVerticalChannelTests(unittest.TestCase):
    """Fix 10: grounding assumed Hips location index 2 was vertical, which slid Meshy units sideways."""

    def test_vertical_axis_is_the_strongest_world_z_response(self) -> None:
        world = MeshyRigWorld()
        ns = load_functions({"root_vertical_location_axis"}, world.namespace())
        axis, responses = ns["root_vertical_location_axis"](world.hips, world.minimum_z)
        self.assertEqual(axis, 1)
        self.assertEqual([round(value, 6) for value in responses], [0.0, 1.0, 0.01])
        self.assertEqual(world.hips.location, [0.0, 0.0, 0.0])

    def test_unresponsive_root_is_refused(self) -> None:
        world = MeshyRigWorld()
        ns = load_functions({"root_vertical_location_axis"}, world.namespace())
        with self.assertRaisesRegex(RuntimeError, "no usable pose-location response"):
            ns["root_vertical_location_axis"](world.hips, lambda: 0.0)

    def test_sanitize_locks_horizontal_motion_and_grounds_the_vertical_channel(self) -> None:
        world = MeshyRigWorld()
        ns = load_functions({"root_vertical_location_axis", "sanitize_root_translation_channels"}, world.namespace())
        report = ns["sanitize_root_translation_channels"]()["actions"][0]
        horizontal_x, vertical, horizontal_z = world.curves
        self.assertEqual(horizontal_x.values(), [0.0, 0.0, 0.0])
        self.assertEqual(horizontal_z.values(), [0.0, 0.0, 0.0])
        bob = vertical.values()
        self.assertAlmostEqual(bob[0] - bob[1], 0.2)
        self.assertAlmostEqual(report["ground_contact_after"], 0.0)
        self.assertAlmostEqual(report["ground_correction_source_units"], 0.2)
        self.assertEqual(report["root_location_axis_index"], 1)

    def test_no_root_grounding_assumes_local_index_two(self) -> None:
        for name in ("sanitize_root_translation_channels", "author_locomotion_action", "correct_action_grounding"):
            with self.subTest(function=name):
                function = worker_function(name)
                source = ast.unparse(function)
                self.assertFalse("array_index == 2" in source, f"{name} assumes local index 2 is vertical")
                self.assertFalse("Vector((0.0, 0.0, root_bob_amplitude" in source, f"{name} bobs on local index 2")
                calls = [
                    node for node in ast.walk(function)
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "root_vertical_location_axis"
                ]
                self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
