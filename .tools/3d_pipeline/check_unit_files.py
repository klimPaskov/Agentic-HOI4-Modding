"""Check a 3D unit's runtime files, and its registration when a mod root is given.

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/check_unit_files.py gfx/models/units/<asset_id> --unit-type infantry_melee
    py -3.13 -B .tools/3d_pipeline/check_unit_files.py gfx/models/units/<asset_id> --unit-type mount --mod-root .

It reads the `.mesh`, `.anim` and `.dds` bytes in the folder without Blender
and reports each problem as a rule id, the file and a sentence. Errors make it
exit 1, warnings do not. `--json` prints the findings as JSON. `--verdict <file>`
writes the route's short stage verdict there (lib/stage_verdict.py) and prints it as
one line: the failed rules, the exact repair commands to run next, or an escalation
when no script fixes them.

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
- UNIT-ANIM-FPS: a soldier's, rider's or creature's clip that does not play at 30 frames a second, as
  vanilla's do (30.0 to 30.9). A Blender scene from factory settings runs at 24, and io_pdx_mesh writes
  the scene's rate. For a vehicle, plane or ship type (`calibration_group`), a warning outside 10 to 60
  (vanilla's run at 15, 30 or 60).
- UNIT-ROLE-MISSING: a role the unit type needs has no `<stem>_<role>.anim`.
- UNIT-DDS-UNREADABLE, UNIT-DDS-SIZE: a texture that does not parse, or is not a power of two or
  is larger than 2048.
- UNIT-DDS-MIPS, UNIT-DDS-FORMAT (warnings): no mip chain, or uncompressed. Vanilla unit
  textures are DXT5 or DXT1 with mips (736 of 743 files).
- UNIT-DDS-SHINY (warning): a specular map far shinier than vanilla units (95th-percentile metalness over 120
  or glossiness over 140); it renders as white speckles on the map.
- UNIT-DDS-EMISSIVE (warning): a normal map whose blue channel is not black. `PdxMeshAdvanced`
  reads normals as RRxG and uses blue as emissive light.

Surface and deformation rules (always; limits are the largest values measured on vanilla units by
`calibrate_deformation.py`, stored in `config/deformation_calibration.json`, for the unit type's
`calibration_group`: `organic` by default, `vehicle` for tanks, guns and trucks, `air_naval` for planes and ships):

- UNIT-HOLE: a larger share of open edges, or a larger open loop, than any vanilla unit of the
  group after welding coincident vertices.
- UNIT-WINDING: more edges between triangles facing opposite ways than any vanilla unit. The game
  culls back faces, so the flipped side shows as a hole.
- UNIT-INSIDE-OUT: a closed part whose triangles face inward.
- UNIT-BRIDGE: more rest-pose edges joining far-apart bones' regions (three or more parent steps,
  for example a hand and a thigh) than any vanilla unit. Skinning tears these joins.
- UNIT-ANIM-STRETCH: in some frame, more edges stretched or squashed (by 1.5 times and by 0.5 % of the
  unit's height), or one edge stretched further, than in any vanilla clip. The mesh is skinned per
  frame from the bytes, as the game does.
- UNIT-ANIM-GROUND: the lowest point sinks below, or (outside death) lifts above, the rest pose's
  ground further than in any vanilla clip. Riders are skipped: they sit on the mount's `Saddle_Node`.
- UNIT-SEAM: more rest-pose edges than any vanilla unit between two legs' regions with no blend
  across them (a crotch whose vertices follow one thigh each). Parting the legs tears the seam.
- UNIT-ANIM-KNEE: in some frame a knee of a two-legged unit bends backward, against the way the
  pelvis faces, by more than 5 % of the leg's length. No vanilla soldier's knee ever does.
- UNIT-ANIM-STILL: a clip moves its joints less than the stillest vanilla clip of the group. It
  reads as a frozen pose on the map.
- UNIT-ANIM-SAME: two roles of the unit play nearly the same motion (their distance is under 12 %
  of the larger clip's motion). Each role must read as itself. A seated rider is exempt for idle,
  move, retreat and training: the mount's gait carries it, so those roles reuse idle by design.
- UNIT-LOOSE-PART: a part not joined to the body's surface (a strap, a plate, a quiver, a separate
  weapon) has vertices with no skin weight, or sits or drifts farther from the rest of the unit, at
  rest or in any frame, than any loose part of vanilla GER_infantry or cavalry_horse. Selection boxes
  (`Collision` shapes) are skipped. Any number of parts is fine while each stays attached. A held prop,
  a separate shape that follows one bone wholly (the weapon `fit_prop.py` binds to the hand), is one
  part however many pieces it has, judged against the body vertices that follow the same bone (the
  hand that holds it): it must touch them at rest and stay on them in every frame. A polearm's head
  may reach as far from the body as its shaft carries it.
- UNIT-PROP-CLIP (warning): a held prop goes inside the body in some frame, more than 2 % of its
  sampled points (`fit_prop.py`'s bar), with the hand and forearm holding it left out. Every frame
  counts, in-betweens included. The warning names the worst clip and frame to look at. A point behind
  an open, one-sided sheet (a cape) also reads as inside, so look before changing the clip.

Mod rule (with `--mod-root`, or `--compare-units <folder>`):

- UNIT-ANIM-SHARED: a clip of this unit is the same clip as one of another unit's (every joint turns
  the same way over time). Units share clips only when one is a reskin of the other, declared with
  `--reskin-of <unit folder or mesh stem>` (decision 3D-6).
- UNIT-CALIBRATION-MISSING (warning): no calibration file, so these rules were skipped.

Registration rules (with `--mod-root`):

- UNIT-REG-PDXMESH: no `pdxmesh` uses the folder's mesh file.
- UNIT-REG-ANIM-FILE: an `.anim` in the folder that no `animation` block names.
- UNIT-REG-ROLE: a role the unit type needs that the `pdxmesh` has no animation id for.
- UNIT-REG-ENTITY: no entity shows the `pdxmesh`, or that entity lacks a needed state.
- UNIT-REG-STATE: an entity state plays an animation id the `pdxmesh` does not define.
- UNIT-REG-MESHSETTINGS, UNIT-REG-TEXTURE: a `meshsettings` name that is not an object of the
  mesh, or a texture that is not next to the mesh.
- UNIT-REG-SPRITE (warning): no sub-unit's sprite resolves to an entity that shows the unit.
- UNIT-REG-UNAVAILABLE (warning): the mod's `.tools/audits/audit_asset_wiring_static.py` is missing or an older
  copy without the kit's model API, so registration was not checked. The file rules still run.
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
CALIBRATION = PIPELINE_ROOT / "config" / "deformation_calibration.json"
# Open loops up to this size are closed by `repair_unit.py --repairs holes` with no visible seam.
SMALL_HOLE_EDGES = 32


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



# Vanilla soldiers, riders, horses, camels and deer play at 30.0 to 30.9 (their exporter rounds the length).
ORGANIC_FPS = 30.0
ORGANIC_FPS_TOLERANCE = 1.0


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
        if (unit_type or {}).get("calibration_group", "organic") == "organic":
            if abs(anim.fps - ORGANIC_FPS) > ORGANIC_FPS_TOLERANCE:
                add("UNIT-ANIM-FPS", "error", anim_path,
                    f"plays at {anim.fps:g} frames a second; soldiers, riders and creatures play at 30. Export it again with the kit (it keeps the clip's length in seconds)")
        elif not 10 <= anim.fps <= 60:
            add("UNIT-ANIM-FPS", "warning", anim_path, f"frame rate {anim.fps:.2f} is outside 10 to 60")
    for role in (unit_type or {}).get("roles", {}):
        if role not in roles_found:
            add("UNIT-ROLE-MISSING", "error", folder, f"no {stem}_{role}.anim for the {role} role")



def load_calibration(group: str = "organic", path: Optional[Path] = None) -> Optional[Dict[str, float]]:
    """One group's vanilla limits measured by `calibrate_deformation.py`, or None when the file is missing."""

    path = path or CALIBRATION
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    measures = payload.get("groups", {}).get(group)
    return {measure: float(entry["value"]) for measure, entry in measures.items()} if measures else None


def _check_deformation(mesh_path, folder, stem, stems, add, facts, limits, seated=False):
    """The surface, bridge and per-frame deformation rules, against the vanilla limits. A seated rider skips the ground rule."""

    from lib import pdx_deform

    if limits is None:
        add("UNIT-CALIBRATION-MISSING", "warning", CALIBRATION, "no vanilla calibration; run calibrate_deformation.py to check holes and deformation")
        return
    try:
        mesh = pdx_deform.load_mesh(mesh_path)
    except (OSError, ValueError, IndexError, pdx_binary.PdxFormatError) as error:
        add("UNIT-MESH-UNREADABLE", "error", mesh_path, f"cannot decode the mesh geometry: {error}")
        return
    surface = pdx_deform.surface_report(mesh)
    bridges = pdx_deform.bridge_edges(mesh)
    facts["surface"][mesh_path.name] = {**asdict(surface), "open_loops": surface.open_loops[:10], "bridge_edges": bridges.edges, "bridge_pairs": dict(list(bridges.pairs.items())[:6])}
    edges = max(len(pdx_deform.mesh_edges(mesh)), 1)
    if surface.largest_open_loop > limits["largest_open_loop"] or surface.open_edges / edges > limits["open_edge_share"]:
        add("UNIT-HOLE", "error", mesh_path, f"{surface.open_edges} open edges ({surface.open_edges / edges:.2%} of all edges) in {len(surface.open_loops)} loops, the largest {surface.largest_open_loop} edges; vanilla units reach {limits['open_edge_share']:.2%} and loops of {limits['largest_open_loop']:.0f}")
    if surface.winding_flips > limits["winding_flips"]:
        add("UNIT-WINDING", "error", mesh_path, f"{surface.winding_flips} edges between triangles facing opposite ways; the game culls back faces, so one side shows as a hole")
    if sum(surface.inside_out_parts) > limits["inside_out_triangles"]:
        add("UNIT-INSIDE-OUT", "error", mesh_path, f"{len(surface.inside_out_parts)} closed part(s) face inward ({sum(surface.inside_out_parts)} triangles); the game culls their outside")
    if bridges.edges > limits["bridge_edges"]:
        pairs = ", ".join(f"{pair} {count}" for pair, count in list(bridges.pairs.items())[:4])
        add("UNIT-BRIDGE", "error", mesh_path, f"{bridges.edges} edges join body parts that move apart ({pairs}); cut the join before rigging or the clips tear it")
    loaded = {}
    for anim_path in sorted(folder.glob("*.anim")):
        if stems and _owner_of(anim_path, stems) != stem:
            continue
        try:
            anim = pdx_deform.load_anim(anim_path)
            report = pdx_deform.deformation_report(mesh, anim)
        except (OSError, ValueError, IndexError, pdx_binary.PdxFormatError):
            continue  # UNIT-ANIM-UNREADABLE already reports it
        loaded[anim_path] = anim
        facts["deformation"][anim_path.name] = asdict(report)
        stretched, squashed = report.stretched_edges / edges, report.squashed_edges / edges
        if stretched > limits["stretched_share"] or squashed > limits["squashed_share"] or report.worst_stretch_share > limits["worst_stretch_share"]:
            pairs = ", ".join(f"{pair} {count}" for pair, count in list(report.worst_pairs.items())[:3])
            add("UNIT-ANIM-STRETCH", "error", anim_path, f"frame {report.worst_frame}: {report.stretched_edges} edges stretched and {report.squashed_edges} squashed, the worst by {report.worst_stretch_share:.1%} of the unit's height ({pairs}); vanilla units reach {limits['stretched_share']:.2%} and {limits['squashed_share']:.2%} of their edges and {limits['worst_stretch_share']:.1%}")
        death = (_role_of(anim_path, stem) or "") == "death"
        sink, sink_limit = -report.lowest, limits["death_sink"] if death else limits["sink"]
        hover = 0.0 if death else report.highest_lowest
        if not seated and (sink > sink_limit or hover > limits["hover"]):
            add("UNIT-ANIM-GROUND", "error", anim_path, f"the lowest point goes {sink:.1%} of the unit's height below the ground and up to {report.highest_lowest:.1%} above it; vanilla {'deaths sink' if death else 'units sink'} at most {sink_limit:.1%} and lift at most {limits['hover']:.1%}")
    _check_motion(mesh, mesh_path, loaded, add, facts, limits, seated)


# A seated rider's idle, move, retreat and training are one clip by design: the mount's gait carries it.
SEATED_REUSE = {"idle", "move", "retreat", "training"}


def _check_motion(mesh, mesh_path, loaded, add, facts, limits, seated=False):
    """The seam, knee, still and same-role rules (lib/pdx_motion.py)."""

    from lib import pdx_motion

    legs = pdx_motion.find_legs(mesh)
    seam = pdx_motion.seam_edges(mesh, legs)
    facts["motion"][mesh_path.name] = {
        "legs": [mesh.bones[leg.knee] for leg in legs.legs],
        "seam_edges": seam.edges,
        "seam_pairs": dict(list(seam.pairs.items())[:4]),
        "clips": {},
    }
    if "seam_edges" in limits and seam.edges > limits["seam_edges"]:
        pairs = ", ".join(f"{pair} {count}" for pair, count in list(seam.pairs.items())[:3])
        add("UNIT-SEAM", "error", mesh_path, f"{seam.edges} edges join two legs with no blend across them ({pairs}); vanilla units have at most {limits['seam_edges']:.0f}. Blend the seam's weights across the pelvis and both legs, or the clips tear it")
    # Knees: anatomy allows a little hyperextension; a group whose vanilla units reach more keeps that.
    knee_limit = max(pdx_motion.KNEE_TOLERANCE, limits.get("knee_backward", 0.0))
    motions = {}
    for anim_path, anim in loaded.items():
        knee = pdx_motion.knee_report(mesh, anim, legs, knee_limit)
        motion = pdx_motion.motion_amount(mesh, anim)
        motions[anim_path] = motion
        facts["motion"][mesh_path.name]["clips"][anim_path.name] = {
            "motion": round(motion, 4),
            "worst_knee_bend": round(knee.worst_bend, 4),
            "backward_knee_frames": knee.backward_frames,
        }
        if knee.worst_bend < -knee_limit:
            add("UNIT-ANIM-KNEE", "error", anim_path, f"frame {knee.worst_frame}: knee {knee.worst_leg} bends backward by {-knee.worst_bend:.0%} of the leg's length ({knee.backward_frames} frame(s) past {knee_limit:.0%}); vanilla soldiers' knees bend back at most {limits.get('knee_backward', 0.0):.1%}. Solve the leg again with the knee toward the toes")
        if "still_motion" in limits and motion < limits["still_motion"]:
            add("UNIT-ANIM-STILL", "error", anim_path, f"the joints move {motion:.2%} of the unit's height on average; the stillest vanilla clip moves {limits['still_motion']:.2%}. It reads as a frozen pose")
    _check_loose_parts(mesh, mesh_path, loaded, add, facts, limits)
    _check_prop_clearance(mesh, mesh_path, loaded, add, facts)
    paths = sorted(loaded)
    for index, first in enumerate(paths):
        for second in paths[index + 1 :]:
            roles = {path.stem[len(mesh_path.stem) + 1 :] for path in (first, second)}
            if seated and roles <= SEATED_REUSE:
                continue
            larger = max(motions[first], motions[second])
            if larger <= 0 or ("still_motion" in limits and larger < limits["still_motion"]):
                continue  # UNIT-ANIM-STATIC or UNIT-ANIM-STILL already names both
            distance = pdx_motion.clip_distance(mesh, loaded[first], loaded[second])
            if distance < pdx_motion.SAME_RATIO * larger:
                add("UNIT-ANIM-SAME", "error", second, f"plays nearly the same motion as {first.name} (distance {distance / larger:.0%} of the clip's motion, under {pdx_motion.SAME_RATIO:.0%}); each role needs its own motion")


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
    folder: Path,
    unit_type: Optional[dict],
    profile: Optional[dict],
    stem: Optional[str] = None,
    deformation: bool = True,
    limits: Optional[Dict[str, float]] = None,
) -> tuple[List[Finding], dict]:
    """Check a unit folder. `stem` checks one mesh and its animations in a folder shared with another unit (a mount and its rider)."""

    findings: List[Finding] = []
    facts: dict = {"meshes": {}, "animations": {}, "textures": {}, "surface": {}, "deformation": {}, "motion": {}}

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
    if deformation and meshes:
        group = (unit_type or {}).get("calibration_group", "organic")
        seated = (unit_type or {}).get("entity_template") == "rider"
        _check_deformation(meshes[0], folder, stem, stems if only_stem else None, add, facts, load_calibration(group) if limits is None else limits, seated)
    _check_textures(folder, add, facts)
    return findings, facts


def _check_prop_clearance(mesh, mesh_path, loaded, add, facts):
    """UNIT-PROP-CLIP (warning): the frames in which a held prop goes inside the body, hand and forearm left out."""

    from lib import pdx_motion

    reports = pdx_motion.prop_clearance(mesh, {path.name: anim for path, anim in loaded.items()})
    facts["motion"][mesh_path.name]["props"] = [
        {"prop_bone": r.prop_bone, "triangles": r.pieces_triangles, "worst_inside_share": round(r.worst_share, 4),
         "worst_clip": r.worst_clip, "worst_frame": r.worst_frame, "frames_over": r.frames_over}
        for r in reports
    ]
    for report in reports:
        if report.frames_over:
            add("UNIT-PROP-CLIP", "warning", mesh_path,
                f"the prop bound to {report.prop_bone} goes inside the body in {report.frames_over} frame(s), worst {report.worst_share:.0%} of its points in "
                f"{report.worst_clip} frame {report.worst_frame} (the hand and forearm holding it are left out). Look at those frames: an in-between can swing it "
                f"through the head or a leg although every key is clear")


def _check_loose_parts(mesh, mesh_path, loaded, add, facts, limits):
    """UNIT-LOOSE-PART: every loose part is skinned and stays within vanilla's contact distance in every frame."""

    from lib import pdx_motion

    parts = pdx_motion.loose_parts(mesh, {path.name: anim for path, anim in loaded.items()})
    facts["motion"][mesh_path.name]["loose_parts"] = [
        {"triangles": part.triangles, "unweighted": part.unweighted, "rest_gap": round(part.rest_gap, 4),
         "worst_gap": round(part.worst_gap, 4), "worst_clip": part.worst_clip, "worst_frame": part.worst_frame,
         "prop_bone": part.prop_bone, "held_by": part.held_by, "pieces": part.pieces}
        for part in parts[:10]
    ]
    unweighted = [part for part in parts if part.unweighted and mesh.skinned]
    if unweighted:
        add("UNIT-LOOSE-PART", "error", mesh_path, f"{len(unweighted)} loose part(s) have vertices with no skin weight ({sum(p.unweighted for p in unweighted)} vertices, the largest part {max(p.triangles for p in unweighted)} triangles); they stay where the bind pose put them while the body moves. Bind each to the bone it rests on (the job's loose_part_edits) or drop it")
    limit = limits.get("loose_gap")
    if limit is None:
        return
    for prop in (part for part in parts if part.prop_bone and part.held_by):
        where = f"the body vertices that follow {prop.held_by}"
        if prop.rest_gap > limit:
            add("UNIT-LOOSE-PART", "error", mesh_path, f"the prop bound to {prop.prop_bone} ({prop.pieces} piece(s), {prop.triangles} triangles) is {prop.rest_gap:.1%} of the unit's height from {where} at rest: nothing holds it. Fit it to the hand again (fit_prop.py) or bind it to the bone that holds it")
        elif prop.worst_gap > limit:
            add("UNIT-LOOSE-PART", "error", mesh_path, f"the prop bound to {prop.prop_bone} slides {prop.worst_gap:.1%} of the unit's height off {where} in {prop.worst_clip} frame {prop.worst_frame}; vanilla loose parts stay within {limit:.1%}")
    parts = [part for part in parts if not (part.prop_bone and part.held_by)]
    floating = [part for part in parts if part.rest_gap > limit]
    drifting = [part for part in parts if part.rest_gap <= limit < part.worst_gap]
    if floating:
        worst = max(floating, key=lambda part: part.rest_gap)
        add("UNIT-LOOSE-PART", "error", mesh_path, f"{len(floating)} loose part(s) float apart from the body at rest, the farthest {worst.rest_gap:.1%} of the unit's height away ({worst.triangles} triangles); vanilla loose parts stay within {limit:.1%}. Move the part onto the body or drop it")
    if drifting:
        worst = drifting[0]
        add("UNIT-LOOSE-PART", "error", mesh_path, f"{len(drifting)} loose part(s) drift off the body in a clip, the worst {worst.worst_gap:.1%} of the unit's height in {worst.worst_clip} frame {worst.worst_frame} ({worst.triangles} triangles); vanilla loose parts stay within {limit:.1%}. Weight the part to the bone it rests on (the job's loose_part_edits bind rule)")


def _unit_clips(folder: Path):
    """(mesh stem, mesh path, {anim path: Animation}) for every mesh in a unit folder."""

    from lib import pdx_deform

    meshes = sorted(folder.glob("*.mesh"))
    stems = [mesh.stem for mesh in meshes]
    for mesh_path in meshes:
        clips = {}
        for anim_path in sorted(folder.glob("*.anim")):
            if _owner_of(anim_path, stems) != mesh_path.stem:
                continue
            try:
                clips[anim_path] = pdx_deform.load_anim(anim_path)
            except (OSError, ValueError, IndexError, pdx_binary.PdxFormatError):
                continue
        yield mesh_path.stem, mesh_path, clips


def check_shared_clips(
    folder: Path, units_root: Path, stem: Optional[str] = None, reskins: Sequence[str] = ()
) -> List[Finding]:
    """UNIT-ANIM-SHARED: a clip of the unit in `folder` that another unit under `units_root` also plays.

    Units are compared on the bone names they share (at least 8). `reskins` names unit folders or mesh
    stems whose clips this unit may share (decision 3D-6: reskins of one base unit only).
    """

    from lib import pdx_deform, pdx_motion

    def bones_of(mesh_path: Path) -> List[str]:
        try:
            return pdx_deform.load_mesh(mesh_path).bones
        except (OSError, ValueError, IndexError, pdx_binary.PdxFormatError):
            return []

    allowed = {name.lower() for name in reskins}
    folder = folder.resolve()
    ours = [(s, path, clips) for s, path, clips in _unit_clips(folder) if not stem or s == stem]
    own_paths = {path.resolve() for _s, path, _c in ours}
    others = []
    for other_folder in sorted({mesh.parent.resolve() for mesh in units_root.rglob("*.mesh")}):
        for other_stem, other_path, other_clips in _unit_clips(other_folder):
            if other_path.resolve() in own_paths or other_folder.name.lower() in allowed or other_stem.lower() in allowed:
                continue
            if other_clips:
                others.append((other_path, other_clips, bones_of(other_path)))
    findings: List[Finding] = []
    for _own_stem, own_path, own_clips in ours:
        own_bones = bones_of(own_path)
        for _other_path, other_clips, other_bones in others:
            common = [bone for bone in own_bones if bone in set(other_bones)]
            if len(common) < 8:
                continue
            theirs = {path: pdx_motion.rotation_profile(anim, common) for path, anim in other_clips.items()}
            for anim_path, anim in own_clips.items():
                profile = pdx_motion.rotation_profile(anim, common)
                for other_anim, other_profile in theirs.items():
                    distance = pdx_motion.same_clip(profile, other_profile)
                    if distance is not None:
                        findings.append(Finding(
                            "UNIT-ANIM-SHARED", "error", anim_path.as_posix(),
                            f"is the same clip as {other_anim.parent.name}/{other_anim.name} ({distance:.2f} degrees apart per joint); "
                            "every unit needs its own animations unless it is a reskin of the other (--reskin-of)",
                        ))
                        break
    return findings


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


REGISTRATION_API = ("ModelLookup", "game_model_roots", "check_pdxmesh", "_files", "_parse_source", "_scalar_node")


def _registration_audit():
    """The kit's registration audit, or None and the reason a mod's copy cannot be used."""

    try:
        audit = _import_registration_audit()
    except ImportError as error:
        return None, f"cannot import it ({error})"
    missing = [name for name in REGISTRATION_API if not hasattr(audit, name)]
    return (None, f"it lacks {', '.join(missing)}") if missing else (audit, "")


def check_unit_registration(folder: Path, mod_root: Path, unit_type: Optional[dict]) -> List[Finding]:
    """The registration rules, or one warning when the mod's audit cannot run them."""

    _audit, reason = _registration_audit()
    if reason:
        # A mod that carries its own, older `.tools/audits` checks registration with its own audits.
        return [Finding("UNIT-REG-UNAVAILABLE", "warning", (mod_root / ".tools" / "audits").as_posix(),
                        f"registration not checked: the mod's audit_asset_wiring_static.py is not the kit's ({reason})")]
    return check_registration(folder, mod_root, unit_type)


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


def _write_verdict(args, folder: Path, findings: List[Finding], errors: List[Finding], facts: dict) -> None:
    from lib import stage_verdict

    shown = args.folder.as_posix()
    out = args.verdict.parent.as_posix()
    stem = args.stem or (next(iter(facts["meshes"]), folder.name).rsplit(".", 1)[0])
    steps, escalate = stage_verdict.next_for_findings(
        {item.rule for item in errors}, shown, out, args.stem, args.unit_type, repaired=folder.name == "files" and folder.parent.name == "repair"
    )
    if not errors:
        mod = f" --mod-root {stage_verdict.quote(args.mod_root.as_posix())}" if args.mod_root else ""
        steps = []
        # Open loops within vanilla's limits still show magenta where a reviewer looks: close the small ones first.
        small = [size for surface in facts["surface"].values() for size in surface.get("open_loops", []) if size <= SMALL_HOLE_EDGES]
        if small and not (folder.name == "files" and folder.parent.name == "repair"):
            steps.append(
                f"{stage_verdict.PY} {stage_verdict.PIPELINE}/repair_unit.py {stage_verdict.quote(shown)}{' --stem ' + args.stem if args.stem else ''}"
                f" --out {stage_verdict.quote(out + '/repair')} --repairs holes --max-hole-edges {SMALL_HOLE_EDGES}"
                f"  (optional: closes {len(small)} small open loop(s) a reviewer can see, then check the copy)"
            )
        steps.append(f"{stage_verdict.PY} {stage_verdict.PIPELINE}/review_unit.py {stage_verdict.quote(shown)}{' --stem ' + args.stem if args.stem else ''}{mod} --out {stage_verdict.quote(out + '/review')}")
    stage_verdict.write(
        stage_verdict.verdict(
            "check", not errors, stem,
            outputs={"folder": shown, "errors": len(errors), "warnings": len(findings) - len(errors)},
            findings=[{"rule": item.rule, "file": Path(item.file).name, "message": stage_verdict.short(item.message)} for item in errors],
            escalate=escalate,
            next_steps=steps,
        ),
        args.verdict,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("folder", type=Path, help="the folder that holds the unit's .mesh, .anim and .dds files")
    parser.add_argument("--unit-type", help="a type from config/unit_types.json; sets the roles, nodes and profile")
    parser.add_argument("--stem", help="check only <stem>.mesh and its animations, in a folder shared with another unit")
    parser.add_argument("--profile", help="an asset profile for the triangle budget (default: the unit type's)")
    parser.add_argument("--mod-root", type=Path, help="also check the mod's registration of the unit, and compare its clips with the mod's other units")
    parser.add_argument("--compare-units", type=Path, help="compare the unit's clips with every unit under this folder (default with --mod-root: <mod-root>/gfx/models/units)")
    parser.add_argument("--reskin-of", action="append", default=[], metavar="UNIT", help="a unit folder or mesh stem this unit reskins; it may share that unit's clips (repeatable)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verdict", type=Path, help="write the stage verdict (pass, fail with repair commands, or escalate) to this file and print it")
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
        findings.extend(check_unit_registration(folder, args.mod_root, unit_type))
    units_root = args.compare_units or (args.mod_root / "gfx" / "models" / "units" if args.mod_root else None)
    if units_root and units_root.is_dir():
        findings.extend(check_shared_clips(folder, units_root, args.stem, args.reskin_of))
    errors = [item for item in findings if item.severity == "error"]
    if args.verdict:
        _write_verdict(args, folder, findings, errors, facts)
        return 1 if errors else 0
    if args.json:
        print(json.dumps({"findings": [asdict(item) for item in findings], "facts": facts}, indent=2))
    else:
        for item in findings:
            print(f"{item.severity.upper():7} {item.rule:22} {item.file}: {item.message}")
        print(f"{len(errors)} error(s), {len(findings) - len(errors)} warning(s) in {folder.name}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
