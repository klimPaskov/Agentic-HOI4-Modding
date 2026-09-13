"""Scoped exact integer membership acceleration; pinned io_pdx_mesh bytes untouched."""
from __future__ import annotations
from contextlib import contextmanager, nullcontext
import hashlib
import importlib
import json
from pathlib import Path


class IndexedVertexIds(list):
    """A real ordered list retaining duplicates; accelerate only integer membership."""
    def __init__(self, values):
        values = list(values)
        self._validate(values)
        super().__init__(values)
        self._members = frozenset(values)

    @staticmethod
    def _validate(values):
        if len(values) > 1000000 or any(type(v) is not int or v < 0 for v in values):
            raise ValueError("Native vertex IDs must be a bounded sequence of nonnegative exact integers.")

    def __contains__(self, value):
        return value in self._members if type(value) in (int, bool) else super().__contains__(value)

    def _replace(self, values):
        self._validate(values)
        super().clear()
        super().extend(values)
        self._members = frozenset(values)

    def append(self, value):
        self._replace(list(self) + [value])

    def extend(self, values):
        self._replace(list(self) + list(values))

    def insert(self, index, value):
        values = list(self)
        values.insert(index, value)
        self._replace(values)

    def __setitem__(self, index, value):
        values = list(self)
        values[index] = value
        self._replace(values)

    def __delitem__(self, index):
        values = list(self)
        del values[index]
        self._replace(values)

    def pop(self, index=-1):
        values = list(self)
        result = values.pop(index)
        self._replace(values)
        return result

    def remove(self, value):
        values = list(self)
        values.remove(value)
        self._replace(values)

    def clear(self):
        self._replace([])

    def __iadd__(self, values):
        self.extend(values)
        return self

    def __imul__(self, count):
        self._replace(list(self) * count)
        return self

    # reverse/sort change only order, so their inherited list implementations
    # preserve the membership index without rebuilding it.


@contextmanager
def optimized_skin_membership(io_pdx_root):
    module = importlib.import_module("io_pdx_mesh.pdx_blender.blender_import_export")
    expected = Path(io_pdx_root).resolve() / "pdx_blender" / "blender_import_export.py"
    if Path(module.__file__).resolve() != expected:
        raise RuntimeError("Membership wrapper must target the selected locked native exporter.")
    original = module.get_mesh_info
    if getattr(original, "_hoi4_membership_wrapper", False):
        raise RuntimeError("Nested native membership wrappers are forbidden.")

    def indexed_info(*args, **kwargs):
        info, vertex_ids = original(*args, **kwargs)
        return info, IndexedVertexIds(vertex_ids) if vertex_ids is not None else None
    indexed_info._hoi4_membership_wrapper = True
    module.get_mesh_info = indexed_info
    try:
        yield
    finally:
        module.get_mesh_info = original
        if module.get_mesh_info is not original:
            raise RuntimeError("Native get_mesh_info restoration failed.")


def export_mesh_with_membership_policy(pdx, io_pdx_root, enabled, *args, **kwargs):
    with optimized_skin_membership(io_pdx_root) if enabled else nullcontext():
        return pdx["export_meshfile"](*args, **kwargs)


def verify_pdx_skin_membership(req, api):
    """Small native weighted fixture, never a shipping/source-model replacement."""
    payload, job = req["payload"], Path(req["job_root"]).resolve()
    if set(payload) != {"output_namespace_rel"}:
        raise ValueError("Membership fixture accepts only its new job-relative evidence directory.")
    relative = payload["output_namespace_rel"]
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative or ".." in Path(relative).parts:
        raise ValueError("Fixture evidence directory must be job-relative without traversal.")
    output = api.within(job, relative, allow_missing=True)
    if output.exists():
        raise ValueError("Membership fixture evidence directory already exists.")
    output.mkdir(parents=True)
    bpy = api.bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    pdx = api.load_pdx(req["io_pdx_root"])
    mesh = bpy.data.meshes.new("MembershipParityFixture")
    mesh.from_pydata([(0,0,0), (1,0,0), (0,1,0), (0,0,1)], [], [(0,2,1), (0,1,3), (0,3,2), (1,2,3)])
    obj = bpy.data.objects.new("MembershipParityFixture", mesh)
    bpy.context.scene.collection.objects.link(obj)
    uv = mesh.uv_layers.new(name="UVMap")
    for face in mesh.polygons:
        face.use_smooth = True
        for loop, point in zip(face.loop_indices, [(0,0), (1,0), (0,1)]):
            uv.data[loop].uv = point
    material = bpy.data.materials.new("MembershipParityMaterial")
    material.use_nodes = True
    material[pdx["PDX_SHADER"]] = "PdxMeshAdvanced"
    mesh.materials.append(material)
    rig_data = bpy.data.armatures.new("MembershipParityRig")
    rig = bpy.data.objects.new("MembershipParityRig", rig_data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    root = rig_data.edit_bones.new("Root")
    root.head, root.tail = (0,0,0), (0,0,1)
    tip = rig_data.edit_bones.new("Tip")
    tip.head, tip.tail, tip.parent = (0,0,1), (0,0,2), root
    bpy.ops.object.mode_set(mode="OBJECT")
    groups = [obj.vertex_groups.new(name=name) for name in ("Root", "Tip")]
    groups[0].add([0,2], 0.25, "REPLACE")
    groups[1].add([0,2], 0.75, "REPLACE")
    groups[0].add([1], 1.0, "REPLACE")
    groups[1].add([3], 1.0, "REPLACE")
    obj.modifiers.new("FixtureSkin", "ARMATURE").object = rig
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.update()
    module = importlib.import_module("io_pdx_mesh.pdx_blender.blender_import_export")
    original = module.get_mesh_info
    cases = []
    for split in (False, True):
        paths = []
        for enabled in (False, True):
            path = output / f"split_{int(split)}_optimized_{int(enabled)}.mesh"
            export_mesh_with_membership_policy(pdx, req["io_pdx_root"], enabled, str(path), exp_mesh=True, exp_skel=True, exp_locs=False, exp_selected=True, as_blendshape=False, debug_mode=False, split_verts=split, sort_verts="+", plain_txt=True)
            paths.append(path)
        same_binary = paths[0].read_bytes() == paths[1].read_bytes()
        same_text = paths[0].with_suffix(".txt").read_bytes() == paths[1].with_suffix(".txt").read_bytes()
        cases.append({"split_verts": split, "same_complete_mesh_bytes": same_binary, "same_complete_text_including_skin": same_text, "mesh_sha256": hashlib.sha256(paths[0].read_bytes()).hexdigest().upper(), "bytes": paths[0].stat().st_size, "files": [p.relative_to(job).as_posix() for p in paths]})
        if not same_binary or not same_text or module.get_mesh_info is not original:
            raise RuntimeError("Native membership byte/skin parity or restoration failed.")
    report = {"status": "pass", "cases": cases, "native_function_restored": module.get_mesh_info is original, "shipping_model_created": False, "checkpoint_saved": False, "extension_source_sha256": api.file_sha256(Path(module.__file__)), "adapter_helper_sha256": api.file_sha256(Path(__file__)), "policy": "same pinned native exporter; same complete weighted mesh bytes in split and indexed modes"}
    (output / "proof.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
