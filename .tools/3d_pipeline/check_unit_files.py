"""Check a 3D unit's runtime files, and its registration when a mod root is given.

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/check_unit_files.py gfx/models/units/<asset_id> --unit-type infantry_melee
    py -3.13 -B .tools/3d_pipeline/check_unit_files.py gfx/models/units/<asset_id> --unit-type mount --mod-root .

It reads the `.mesh`, `.anim` and `.dds` bytes in the folder without Blender
and reports each problem as a rule id, the file and a sentence. Errors make it
exit 1, warnings do not. `--json` prints the findings as JSON.

File rules (always):

- UNIT-MESH-NONE, UNIT-MESH-UNREADABLE: no `.mesh`, or one that does not parse.
- UNIT-BONES: more than 50 bones. The installed `gfx/FX/pdxmesh.shader` declares
  `float4x4 matBones[50]` [vanilla-confirmed 1.19.4.1].
- UNIT-INFLUENCES: more than 4 bone influences per vertex (`PDXMESH_MAX_INFLUENCE = 4`, same file).
- UNIT-STREAM-VERTICES: more than 65,535 vertices in one stream (16-bit indices) [unverified engine
  limit; the largest vanilla stream has 38,447 vertices].
- UNIT-TRIANGLES: above the profile's `hard_max` (error) or `preferred_max` (warning).
- UNIT-UNSKINNED: the unit type needs animations but the mesh has no skeleton.
- UNIT-NODE-MISSING, UNIT-NODE-ORIENTATION: a bone the unit type attaches to (a mount's `Saddle_Node`) is
  missing, or is rotated (vanilla's has an identity rotation) [vanilla-confirmed 1.19.4.1].
- UNIT-ANIM-UNREADABLE, UNIT-ANIM-JOINTS, UNIT-ANIM-STATIC: an `.anim` that does not parse,
  animates bones the mesh does not have, or moves nothing.
- UNIT-ANIM-FPS (warning): a frame rate outside 10 to 60.
- UNIT-ROLE-MISSING: a role the unit type needs has no `<stem>_<role>.anim`.
- UNIT-DDS-UNREADABLE, UNIT-DDS-SIZE: a texture that does not parse, or is not a power of two or
  is larger than 2048.
- UNIT-DDS-MIPS, UNIT-DDS-FORMAT (warnings): no mip chain, or uncompressed. Vanilla unit
  textures are DXT5 or DXT1 with mips (736 of 743 files).
- UNIT-DDS-SHINY (warning): a specular map far shinier than vanilla units (95th-percentile metalness over 120
  or glossiness over 140); it renders as white speckles on the map.
- UNIT-DDS-EMISSIVE (warning): a normal map whose blue channel is not black. `PdxMeshAdvanced`
  reads normals as RRxG and uses blue as emissive light.

Registration rules (with `--mod-root`):

- UNIT-REG-PDXMESH: no `pdxmesh` uses the folder's mesh file.
- UNIT-REG-ANIM-FILE: an `.anim` in the folder that no `animation` block names.
- UNIT-REG-ROLE: a role the unit type needs that the `pdxmesh` has no animation id for.
- UNIT-REG-ENTITY: no entity shows the `pdxmesh`, or that entity lacks a needed state.
- UNIT-REG-STATE: an entity state plays an animation id the `pdxmesh` does not define.
- UNIT-REG-MESHSETTINGS, UNIT-REG-TEXTURE: a `meshsettings` name that is not an object of the
  mesh, or a texture that is not next to the mesh.
- UNIT-REG-SPRITE (warning): no sub-unit's sprite resolves to an entity that shows the unit.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

PIPELINE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PIPELINE_ROOT.parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import pdx_binary  # noqa: E402

MAX_BONES = 50
MAX_INFLUENCES = 4
MAX_STREAM_VERTICES = 65535
MAX_TEXTURE_SIDE = 2048
EMISSIVE_TOLERANCE = 8
SHINY_METALLIC = 120
SHINY_GLOSS = 140


@dataclass
class Finding:
    rule: str
    severity: str
    file: str
    message: str


def load_unit_types() -> Dict[str, dict]:
    return json.loads((PIPELINE_ROOT / "config" / "unit_types.json").read_text(encoding="utf-8"))["types"]


def load_profile(name: str) -> dict:
    profiles = json.loads((PIPELINE_ROOT / "config" / "asset_profiles.json").read_text(encoding="utf-8"))["profiles"]
    if name not in profiles:
        raise SystemExit(f"Unknown profile {name}; known: {', '.join(sorted(profiles))}")
    return profiles[name]


def _role_of(anim: Path, stem: str) -> Optional[str]:
    name = anim.stem
    return name[len(stem) + 1 :] if name.startswith(stem + "_") else None


def _owner_of(anim: Path, stems: Sequence[str]) -> Optional[str]:
    """The mesh stem an animation belongs to: the longest one its name starts with (`x_rider_idle` is `x_rider`'s, not `x`'s)."""

    owners = [stem for stem in stems if anim.stem.startswith(stem + "_")]
    return max(owners, key=len) if owners else None


def _check_meshes(meshes, unit_type, profile, needs_animation, add, facts, skeleton):
    """The mesh rules; fills `skeleton` with every bone name."""

    for mesh_path in meshes:
        try:
            summary = pdx_binary.summarize_mesh(pdx_binary.read(mesh_path))
        except (OSError, pdx_binary.PdxFormatError) as error:
            add("UNIT-MESH-UNREADABLE", "error", mesh_path, f"cannot read the mesh: {error}")
            continue
        facts["meshes"][mesh_path.name] = {
            "shapes": summary.shapes,
            "triangles": summary.triangles,
            "bones": len(summary.bones),
            "streams": [asdict(stream) for stream in summary.streams],
        }
        skeleton.extend(bone for bone in summary.bones if bone not in skeleton)
        if len(summary.bones) > MAX_BONES:
            add("UNIT-BONES", "error", mesh_path, f"{len(summary.bones)} bones; the engine skins at most {MAX_BONES} (pdxmesh.shader matBones[50])")
        for stream in summary.streams:
            if stream.influences_per_vertex > MAX_INFLUENCES:
                add("UNIT-INFLUENCES", "error", mesh_path, f"{stream.shape} has {stream.influences_per_vertex} influences per vertex; the engine reads {MAX_INFLUENCES}")
            if stream.vertices > MAX_STREAM_VERTICES:
                add("UNIT-STREAM-VERTICES", "error", mesh_path, f"{stream.shape} has {stream.vertices} vertices in one stream (limit {MAX_STREAM_VERTICES})")
        if profile:
            limits = profile.get("triangle_range", {})
            hard, preferred = limits.get("hard_max"), limits.get("preferred_max")
            if hard and summary.triangles > hard:
                add("UNIT-TRIANGLES", "error", mesh_path, f"{summary.triangles} triangles, above the profile's hard_max {hard}")
            elif preferred and summary.triangles > preferred:
                add("UNIT-TRIANGLES", "warning", mesh_path, f"{summary.triangles} triangles, above the profile's preferred_max {preferred}")
        if needs_animation and not summary.bones:
            add("UNIT-UNSKINNED", "error", mesh_path, "the unit type needs animations but the mesh has no skeleton")
        for node in (unit_type or {}).get("required_nodes", []):
            if node not in summary.bones and node not in summary.locators:
                add("UNIT-NODE-MISSING", "error", mesh_path, f"{node} is not a bone or locator of the mesh; the entity attaches to it")
            elif node in summary.bone_rotations and not summary.bone_rotations[node]:
                add("UNIT-NODE-ORIENTATION", "error", mesh_path, f"{node} is rotated; vanilla attach nodes (cavalry_horse.mesh Saddle_Node) have an identity rotation, and the engine turns the attached entity with the node")



def _check_animations(folder, stem, unit_type, skeleton, add, facts, stems=None):
    """The animation and role rules. With `stems`, only the animations `stem` owns are read."""

    skeleton_set = set(skeleton)
    roles_found: Dict[str, Path] = {}
    for anim_path in sorted(folder.glob("*.anim")):
        if stems and _owner_of(anim_path, stems) != stem:
            continue
        try:
            anim = pdx_binary.summarize_anim(pdx_binary.read(anim_path))
        except (OSError, pdx_binary.PdxFormatError) as error:
            add("UNIT-ANIM-UNREADABLE", "error", anim_path, f"cannot read the animation: {error}")
            continue
        facts["animations"][anim_path.name] = {
            "fps": round(anim.fps, 3),
            "samples": anim.samples,
            "seconds": round(anim.seconds, 3),
            "joints": len(anim.joints),
            "animated_joints": len(anim.animated_joints),
        }
        role = _role_of(anim_path, stem)
        if role:
            roles_found[role] = anim_path
        if skeleton_set:
            unknown = [joint for joint in anim.joints if joint not in skeleton_set]
            if unknown:
                add("UNIT-ANIM-JOINTS", "error", anim_path, f"animates {len(unknown)} bones the mesh does not have: {', '.join(unknown[:6])}")
        if not anim.animated_joints or anim.samples < 2:
            add("UNIT-ANIM-STATIC", "error", anim_path, f"moves nothing ({len(anim.animated_joints)} animated joints, {anim.samples} samples)")
        if not 10 <= anim.fps <= 60:
            add("UNIT-ANIM-FPS", "warning", anim_path, f"frame rate {anim.fps:.2f} is outside 10 to 60")
    for role in (unit_type or {}).get("roles", {}):
        if role not in roles_found:
            add("UNIT-ROLE-MISSING", "error", folder, f"no {stem}_{role}.anim for the {role} role")



def _check_textures(folder, add, facts):
    """The texture rules."""

    for dds_path in sorted(folder.glob("*.dds")):
        try:
            from lib import model_dds

            data = dds_path.read_bytes()
            header = model_dds.read_header(data)
        except (OSError, ValueError) as error:
            add("UNIT-DDS-UNREADABLE", "error", dds_path, f"cannot read the texture: {error}")
            continue
        facts["textures"][dds_path.name] = header
        width, height = int(header["width"]), int(header["height"])
        if width & (width - 1) or height & (height - 1) or max(width, height) > MAX_TEXTURE_SIDE:
            add("UNIT-DDS-SIZE", "error", dds_path, f"{width}x{height}; use a power of two on each side, at most {MAX_TEXTURE_SIDE}")
        if int(header["mips"]) < model_dds.full_mip_count(width, height):
            add("UNIT-DDS-MIPS", "warning", dds_path, f"{header['mips']} mip level(s) of {model_dds.full_mip_count(width, height)}; the zoomed-out map will shimmer")
        if not header["compressed"]:
            add("UNIT-DDS-FORMAT", "warning", dds_path, f"uncompressed {header['format']}; vanilla units use DXT5 or DXT1 (a quarter of the memory)")
        if dds_path.stem.endswith(("_specular", "_spec")):
            try:
                import numpy as np

                pixels = model_dds.decode_top_level(data)
                metal, gloss = (float(np.percentile(pixels[..., channel], 95)) for channel in (2, 3))
                if metal > SHINY_METALLIC or gloss > SHINY_GLOSS:
                    add("UNIT-DDS-SHINY", "warning", dds_path, f"95th-percentile metalness {metal:.0f} and glossiness {gloss:.0f}; vanilla units stay under about {SHINY_METALLIC} and {SHINY_GLOSS}, and brighter maps alias into white speckles")
            except (ValueError, model_dds.DdsError):
                pass
        if dds_path.stem.endswith("_normal"):
            try:
                pixels = model_dds.decode_top_level(data)
                blue = int(pixels[..., 2].max())
                if blue > EMISSIVE_TOLERANCE:
                    add("UNIT-DDS-EMISSIVE", "warning", dds_path, f"blue channel reaches {blue}; PdxMeshAdvanced reads normal-map blue as emissive light")
            except (ValueError, model_dds.DdsError):
                pass


def check_files(
    folder: Path, unit_type: Optional[dict], profile: Optional[dict], stem: Optional[str] = None
) -> tuple[List[Finding], dict]:
    """Check a unit folder. `stem` checks one mesh and its animations in a folder shared with another unit (a mount and its rider)."""

    findings: List[Finding] = []
    facts: dict = {"meshes": {}, "animations": {}, "textures": {}}

    def add(rule: str, severity: str, path: Path, message: str) -> None:
        findings.append(Finding(rule, severity, path.as_posix(), message))

    meshes = sorted(folder.glob("*.mesh"))
    stems = [mesh.stem for mesh in meshes]
    only_stem = bool(stem)
    if stem:
        meshes = [mesh for mesh in meshes if mesh.stem == stem]
    if not meshes:
        add("UNIT-MESH-NONE", "error", folder, f"the folder has no {stem or '*'}.mesh file")
    skeleton: List[str] = []
    stem = stem or (meshes[0].stem if meshes else folder.name)
    needs_animation = bool(unit_type and unit_type.get("roles"))
    _check_meshes(meshes, unit_type, profile, needs_animation, add, facts, skeleton)
    _check_animations(folder, stem, unit_type, skeleton, add, facts, stems if only_stem else None)
    _check_textures(folder, add, facts)
    return findings, facts


def _import_registration_audit():
    """Import `.tools/audits/audit_asset_wiring_static.py`, whose `lib` is `.tools/lib`, not this folder's."""

    pipeline_lib = {name: module for name, module in sys.modules.items() if name == "lib" or name.startswith("lib.")}
    for name in pipeline_lib:
        del sys.modules[name]
    saved_path = list(sys.path)
    sys.path[:0] = [str(REPO_ROOT / ".tools"), str(REPO_ROOT / ".tools" / "audits")]
    try:
        import audit_asset_wiring_static as audit
    finally:
        sys.path[:] = saved_path
        for name in [name for name in sys.modules if name == "lib" or name.startswith("lib.")]:
            del sys.modules[name]
        sys.modules.update(pipeline_lib)
    return audit


def check_registration(folder: Path, mod_root: Path, unit_type: Optional[dict]) -> List[Finding]:
    audit = _import_registration_audit()
    findings: List[Finding] = []
    lookup = audit.ModelLookup([mod_root], audit.game_model_roots())
    folder_rel = folder.resolve().relative_to(mod_root.resolve()).as_posix().lower()
    meshes = [mesh for mesh in lookup.mod.pdxmeshes.values() if mesh.file.replace("\\", "/").lower().rsplit("/", 1)[0] == folder_rel]
    if not meshes:
        findings.append(Finding("UNIT-REG-PDXMESH", "error", folder_rel, "no pdxmesh uses a mesh file in this folder"))
        return findings
    registered_files = {
        Path(animation.file.replace("\\", "/")).name.lower()
        for animation in lookup.mod.animations.values()
    }
    for anim_path in sorted(folder.glob("*.anim")):
        if anim_path.name.lower() not in registered_files:
            findings.append(Finding("UNIT-REG-ANIM-FILE", "error", anim_path.as_posix(), "no animation block names this file"))
    needed_roles = list((unit_type or {}).get("roles", {}))
    needed_states = list((unit_type or {}).get("entity_states", {}))
    mesh_names = {mesh.name for mesh in meshes}
    for mesh in meshes:
        ids = {identifier for identifier, _kind, _line in mesh.animations}
        for role in needed_roles:
            if role not in ids:
                findings.append(Finding("UNIT-REG-ROLE", "error", mesh.path, f"pdxmesh {mesh.name} has no animation id {role}"))
        for row in audit.check_pdxmesh(mesh, lookup):
            # The audit resolves texture names against its own repository's asset index;
            # the next-to-the-mesh check below is the one that holds for any mod root.
            if row[0] == "GFX-3D-TEXTURE-MISSING":
                continue
            rule = {"GFX-3D-MESHSETTINGS": "UNIT-REG-MESHSETTINGS"}.get(row[0], row[0])
            findings.append(Finding(rule, "error", row[1], row[3]))
        mesh_path = lookup.find_file(mesh.file)
        for settings in mesh.settings:
            for key, texture, _line in settings.textures:
                if mesh_path is not None and not (mesh_path.parent / texture).is_file():
                    findings.append(Finding("UNIT-REG-TEXTURE", "error", mesh.path, f"{key} {texture} of {mesh.name} is not next to {mesh.file}"))
    entities = [entity for entity in lookup.mod.entities.values() if entity.pdxmesh in mesh_names]
    if not entities:
        findings.append(Finding("UNIT-REG-ENTITY", "error", folder_rel, f"no entity shows pdxmesh {', '.join(sorted(mesh_names))}"))
    for entity in entities:
        states = {state for state, _animation, _line in entity.states}
        for state in needed_states:
            if state not in states:
                findings.append(Finding("UNIT-REG-ENTITY", "error", entity.path, f"entity {entity.name} has no {state} state"))
        mesh = lookup.pdxmesh(entity.pdxmesh or "")
        known = {identifier for identifier, _kind, _line in mesh.animations} if mesh else set()
        for state, animation, line in entity.states:
            if animation not in known:
                findings.append(Finding("UNIT-REG-STATE", "error", entity.path, f"state {state} of {entity.name} (line {line}) plays {animation}, which pdxmesh {entity.pdxmesh} does not define"))
    showing = {entity.name for entity in entities}
    holders = {
        entity.name
        for entity in lookup.mod.entities.values()
        if any(target in showing for _slot, target, _line in entity.attaches)
    }
    sprites = set()
    for path in audit._files(mod_root, "common/units"):
        for key, _operator, value, _line in audit._parse_source(path):
            if key == "sub_units" and isinstance(value, list):
                for _unit, _op, block, _l in value:
                    sprite = audit._scalar_node(block, "sprite") if isinstance(block, list) else None
                    if sprite:
                        sprites.add(f"{sprite[0]}_entity")
    if not sprites & (showing | holders):
        findings.append(Finding("UNIT-REG-SPRITE", "warning", folder_rel, "no sub-unit sprite resolves to an entity that shows this unit (it is not wired yet)"))
    return findings


def repair_textures(folder: Path) -> List[str]:
    """Rewrite single-level or uncompressed DDS files as DXT5 with mips; clear normal-map blue.

    The top level is decoded and re-encoded, so a DXT5 file that already has mips is left
    alone. Returns the names of the files rewritten.
    """

    import numpy as np
    from PIL import Image

    from lib import model_dds

    rewritten = []
    for dds_path in sorted(folder.glob("*.dds")):
        data = dds_path.read_bytes()
        header = model_dds.read_header(data)
        width, height = int(header["width"]), int(header["height"])
        is_normal = dds_path.stem.endswith("_normal")
        pixels = model_dds.decode_top_level(data)
        emissive = is_normal and int(pixels[..., 2].max()) > 0
        if header["compressed"] and int(header["mips"]) >= model_dds.full_mip_count(width, height) and not emissive:
            continue
        if is_normal:
            pixels = pixels.copy()
            pixels[..., 2] = 0
        image = Image.fromarray(np.ascontiguousarray(pixels), "RGBA")
        temporary = dds_path.with_name(dds_path.name + ".partial")
        temporary.write_bytes(model_dds.dxt5_bytes(image))
        temporary.replace(dds_path)
        rewritten.append(dds_path.name)
    return rewritten


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("folder", type=Path, help="the folder that holds the unit's .mesh, .anim and .dds files")
    parser.add_argument("--unit-type", help="a type from config/unit_types.json; sets the roles, nodes and profile")
    parser.add_argument("--stem", help="check only <stem>.mesh and its animations, in a folder shared with another unit")
    parser.add_argument("--profile", help="an asset profile for the triangle budget (default: the unit type's)")
    parser.add_argument("--mod-root", type=Path, help="also check the mod's registration of the unit")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--repair-textures",
        action="store_true",
        help="first rewrite uncompressed or single-level DDS files as DXT5 with mips and clear normal-map blue",
    )
    args = parser.parse_args(argv)
    if args.repair_textures:
        for name in repair_textures(args.folder.resolve()):
            print(f"REPAIRED {name}: DXT5 with a full mip chain")

    unit_type = None
    if args.unit_type:
        types = load_unit_types()
        if args.unit_type not in types:
            raise SystemExit(f"Unknown unit type {args.unit_type}; known: {', '.join(sorted(types))}")
        unit_type = types[args.unit_type]
    profile_name = args.profile or (unit_type or {}).get("profile")
    profile = load_profile(profile_name) if profile_name else None
    folder = args.folder.resolve()
    if not folder.is_dir():
        raise SystemExit(f"Not a folder: {folder}")
    findings, facts = check_files(folder, unit_type, profile, args.stem)
    if args.mod_root:
        findings.extend(check_registration(folder, args.mod_root, unit_type))
    errors = [item for item in findings if item.severity == "error"]
    if args.json:
        print(json.dumps({"findings": [asdict(item) for item in findings], "facts": facts}, indent=2))
    else:
        for item in findings:
            print(f"{item.severity.upper():7} {item.rule:22} {item.file}: {item.message}")
        print(f"{len(errors)} error(s), {len(findings) - len(errors)} warning(s) in {folder.name}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
