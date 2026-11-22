"""Turn a Tripo GLB of a building, landmark, ship, tank or plane into HOI4 files, for free in Blender.

    py -3.13 -B .tools/3d_pipeline/tripo/static_model.py <inbox>/<name>.json --out <job folder>
    py -3.13 -B .tools/3d_pipeline/tripo/static_model.py <inbox>/<name>.json --out <job folder> --plan

The job file names the model and its `model_kind` (building, landmark, ship, vehicle, plane); the GLB is
`<name>.glb` next to it (or the job's `glb`). An optional `front` (`-y`, `+y`, `-x`, `+x`) overrides which way
the model is found to face. A GLB made in parts (Tripo's Generate in Parts: one mesh node a part) is reduced part by
part (`lib/static_parts.py`): each part gets a share of the triangle budget by its need and keeps its shape (the
silhouette agreement `part_shape_iou`, default 0.97, as the unit route's `part_shape_iou`) and its closure; `"parts":
false` joins the parts and reduces them as one, as before. Everything else comes from the kind's contract in `config/static_kinds.json`, measured
from vanilla files by `calibrate_static_kinds.py`:

- size and place: the kind's vanilla main measure (a tank's length, a plane's wingspan, a ship's length with its
  waterline at zero, a building's footprint, a landmark's largest side), and vanilla's entity scale;
- the triangle budget and texture size of the most detailed vanilla model of the kind, its shader, specular level
  and glossiness;
- the rigid parts and their bones (a tank's hull, turret and barrel, a plane's body and propeller, a ship's hull on
  `ship`), the `Collision` box and the locators of vanilla's entity;
- the role clips: vanilla's own clip of the kind (read from the installed game) retargeted onto the model's pivots,
  plus a turret turn before a tank's shot and a plane's propeller spin.

It writes a small mod tree under `<out>/mod`: `gfx/models/<folder>/<name>/` (the `.mesh`, the `.anim` per role, the
three DXT5 textures) and `gfx/entities/<name>.asset` (the `pdxmesh`, the `animation` blocks and the entity, made from
vanilla's entity for the kind), then runs `check_unit_files.py --model-kind` on it and prints a one-line verdict.
`--plan` runs only the geometry rules on the GLB (no Blender) and prints what the stage would do.
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import shutil
import sys
from pathlib import Path
from typing import Dict, Optional

import numpy as np
from PIL import Image

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import glb_atlas, heavy_job, model_dds, pdx_deform, static_delight, static_parts
from lib import static_kinds as sk
from lib.texture_lineage import embedded_images
from pack_pdx_material import remap_gloss_table

BLENDER_SCRIPT = Path(__file__).resolve().parent / "static_model_blender.py"
FOLDERS = {"vehicle": "gfx/models/units/tanks", "plane": "gfx/models/units/planes", "ship": "gfx/models/units/ships",
           "building": "gfx/models/buildings", "landmark": "gfx/models/buildings/landmarks"}
# A Tripo export without a metallic-roughness map gets a constant one: not metal, roughness 0.8 (as the unit route).
NEUTRAL_ROUGHNESS = 204


def game_dir() -> Path:
    spec = importlib.util.spec_from_file_location("kit_game", PIPELINE_ROOT.parent / "lib" / "game.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.game_dir()


def _resize(image: Image.Image, size: int) -> Image.Image:
    """Resize one channel at a time, so a packed map keeps its channels apart (Tripo default)."""

    return Image.merge(image.mode, [band.resize((size, size), Image.Resampling.LANCZOS) for band in image.split()])


def delighted(source: Image.Image, glb: Path, report: dict) -> Image.Image:
    """The base colour map with the cast shadows Tripo painted into it lifted (lib/static_delight.py), or as it is when it
    has none. The report says what was found."""

    try:
        groups = static_delight.glb_groups(glb, min(static_delight.ANALYSIS_SIZE, source.width))
    except (KeyError, ValueError) as error:
        report.update({"skipped": f"the GLB has no UVs to group the texture by ({error})"})
        return source
    lifted, found = static_delight.delight(source, groups)
    report.update(found)
    return lifted if found["regions"] else source


def placed_geometry(glb: Path, contract: dict, front: Optional[str]) -> tuple:
    """(placed vertices in Blender space, UVs, triangles, the plan) of a vehicle's GLB, the way the Blender stage places it
    (`lib/static_kinds.plan`)."""

    positions, uv, triangles = static_delight.glb_uv_geometry(glb)
    blender = np.stack([positions[:, 0], -positions[:, 2], positions[:, 1]], axis=1)
    arrays = sk.read_glb_geometry(glb)
    plan = sk.plan(arrays[0], arrays[1], contract, front)
    placed = sk.rotate_quarter_turns(blender, plan["quarter_turns"]) * plan["scale"] + np.asarray(plan["offset"])
    return placed, uv, triangles, plan


def ring_seamed(source: Image.Image, glb: Path, contract: dict, front: Optional[str], report: dict) -> Image.Image:
    """A tank's colour map with the band round its turret ring matched to the hull roof (lib/static_delight.ring_seam), or
    as it is for any other kind. The report says what was found."""

    if contract["kind"] != "vehicle":
        return source
    try:
        placed, uv, triangles, plan = placed_geometry(glb, contract, front)
        cut = plan["turret_cut"]["cut_z"]
        above = placed[(placed[:, 2] >= cut) & (placed[:, 1] >= plan["barrel_cut"]["cut_y"])]
        centre = (above.min(axis=0) + above.max(axis=0)) / 2
        radius = sk.ring_footprint(placed, triangles, cut, centre)
        fixed, found = static_delight.ring_seam(source, uv, placed, triangles, cut, float(placed[:, 2].max()), centre, radius)
    except (KeyError, ValueError) as error:
        report["ring_seam"] = {"skipped": str(error)}
        return source
    report["ring_seam"] = found
    return fixed if "off_after" in found and found["off_after"] != found["off_before"] else source


def vanilla_spread(game: Path, contract: dict) -> list:
    """The brightness spread (`static_delight.luma_spread`) of each reference model's colour texture."""

    spreads = []
    for rel in contract.get("references", []):
        mesh = game / rel
        diffuse = mesh.with_name(mesh.stem + "_diffuse.dds")
        if not mesh.is_file() or not diffuse.is_file():
            continue
        try:
            _p, uv, triangles = static_delight.mesh_uv_geometry(mesh)
            with Image.open(diffuse) as opened:
                spreads.append(static_delight.texture_spread(opened, uv, triangles))
        except (OSError, KeyError, ValueError):
            continue
    return spreads


def vanilla_metallic(game: Optional[Path], contract: dict) -> Optional[int]:
    """The metallic channel (blue) of the reference models' specular maps, median of their medians: vanilla's tanks are
    painted metal (their light tanks 129), where Tripo's maps carry none and a flat panel facing the light washes out white."""

    if game is None:
        return None
    values = []
    for rel in contract.get("references", []):
        mesh = game / rel
        spec = mesh.with_name(mesh.stem + "_specular.dds")
        try:
            with Image.open(spec) as opened:
                values.append(float(np.median(np.asarray(opened.convert("RGBA"))[..., 2])))
        except OSError:
            continue
    return int(round(float(np.median(values)))) if len(values) >= 3 else None


def contrasted(source: Image.Image, glb: Path, contract: dict, front: Optional[str], game: Optional[Path], report: dict) -> Image.Image:
    """A tank's colour map with its brightness spread lifted to the flattest quarter of vanilla's light tanks
    (lib/static_delight.contrast_lift), or as it is for any other kind or a texture already that lively."""

    if contract["kind"] != "vehicle" or game is None:
        return source
    spreads = vanilla_spread(game, contract)
    if len(spreads) < 3:
        report["contrast"] = {"skipped": f"only {len(spreads)} vanilla textures to measure"}
        return source
    try:
        placed, uv, triangles, _plan = placed_geometry(glb, contract, front)
        fixed, found = static_delight.contrast_lift(source, uv, placed[:, 2], triangles, float(np.percentile(spreads, 25)))
    except (KeyError, ValueError) as error:
        report["contrast"] = {"skipped": str(error)}
        return source
    found["vanilla_spreads"] = [round(v, 3) for v in sorted(spreads)]
    report["contrast"] = found
    return fixed if found["spread_after"] != found["spread_before"] else source


def hole_texel(glb: Path, colour: Path) -> Optional[dict]:
    """The atlas texel a blown-open turret ring takes (lib/static_delight.hole_uv), from the packed colour map and the
    faces the GLB's UVs cover, or None when the GLB has no UVs."""

    try:
        with Image.open(colour) as opened:
            image = opened.convert("RGB")
        return static_delight.hole_uv(image, static_delight.glb_groups(glb, min(static_delight.ANALYSIS_SIZE, image.width)))
    except (KeyError, ValueError):
        return None


def pack_textures(glb: Path, contract: dict, name: str, files: Path, work: Path, delight: Optional[dict] = None, front: Optional[str] = None, game: Optional[Path] = None) -> Dict[str, dict]:
    """The GLB's base colour, normal and metallic-roughness maps as the kind's PDX diffuse, normal and specular DDS. The
    colour map is delighted first; `delight` (when given) receives what was lifted."""

    images = embedded_images(glb)
    if not images["diffuse"]:
        raise SystemExit(f"{glb.name} has no base colour map")
    if len(images["diffuse"]) > 1:
        raise SystemExit(f"{glb.name} has {len(images['diffuse'])} base colour maps; the route packs one atlas")
    size = int(contract["texture_size"])
    work.mkdir(parents=True, exist_ok=True)
    found = delight if delight is not None else {}
    lifted = delighted(Image.open(io.BytesIO(images["diffuse"][0])).convert("RGB"), glb, found)
    lifted = ring_seamed(lifted, glb, contract, front, found)
    colour = _resize(contrasted(lifted, glb, contract, front, game, found).convert("RGBA"), size)
    colour = Image.merge("RGBA", (*colour.split()[:3], Image.new("L", (size, size), 255)))
    if images["normal"]:
        source = _resize(Image.open(io.BytesIO(images["normal"][0])).convert("RGB"), size)
        red, green, _blue = source.split()
    else:
        red = green = Image.new("L", (size, size), 128)
    zero = Image.new("L", (size, size), 0)
    # PdxMeshAdvanced reads tangent x from green and y from alpha; blue would glow (pack_pdx_material.pack_pdx_normal_map)
    normal = Image.merge("RGBA", (zero, red, zero, green))
    if images["specular"]:
        source = _resize(Image.open(io.BytesIO(images["specular"][0])).convert("RGB"), size)
        _r, roughness, metallic = source.split()
    else:
        roughness, metallic = Image.new("L", (size, size), NEUTRAL_ROUGHNESS), zero
    if contract["kind"] == "vehicle" and metallic.getextrema()[1] == 0:
        vanilla = vanilla_metallic(game, contract)
        if vanilla:
            metallic = Image.new("L", (size, size), vanilla)
            found["metallic"] = vanilla
    gloss = roughness.point(lambda v: 255 - v)
    if contract.get("gloss_quantiles"):
        gloss = gloss.point(remap_gloss_table(gloss, contract["gloss_quantiles"]))
    specular = Image.merge("RGBA", (zero, Image.new("L", (size, size), int(contract["specular_level"])), metallic, gloss))
    written = {}
    for role, image in (("diffuse", colour), ("normal", normal), ("specular", specular)):
        staged = work / f"{name}_{role}.png"
        image.save(staged)
        header = model_dds.write_dxt5(staged, files / f"{name}_{role}.dds")
        written[role] = {"file": f"{name}_{role}.dds", "size": [header["width"], header["height"]], "format": header["format"], "mips": header["mips"]}
    return written


def clip_motion(game: Path, contract: dict) -> tuple[dict, Optional[float]]:
    """Each role's vanilla motion, resampled to 30 fps, displacements scaled to the model's size, with the extras."""

    motions = {}
    barrel_length = None
    for role, clip in contract["clips"].items():
        mesh = pdx_deform.load_mesh(game / clip["mesh"])
        anim = pdx_deform.load_anim(game / clip["anim"])
        points = np.array([sk.to_blender(p) for p in mesh.positions[~mesh.collision]])
        scale = contract["size"]["source"] / sk.main_measure(points, contract["kind"])
        raw = sk.local_motion(mesh, anim)
        count = None
        extras: Dict[str, list] = {}
        if contract.get("spin"):
            seconds = (anim.frames - 1) / anim.fps
            count = sk.spin_frames(seconds, contract["spin"]["degrees_per_frame"])
            extras["propeller"] = [{"type": "spin", "axis": contract["spin"]["axis"], "degrees_per_frame": contract["spin"]["degrees_per_frame"]}]
        motion, frames = sk.resample(raw, anim.fps, count=count)
        if contract["kind"] == "vehicle":
            if barrel_length is None and clip["mesh"] == contract["clips"]["attack"]["mesh"]:
                barrel_length = vanilla_barrel_length(mesh)
            if role == "attack" and "barrel_tip" in motion:
                recoil = np.linalg.norm(motion["barrel_tip"]["d"], axis=1)
                turn = contract["attack_turn"]
                extras["turret"] = [{"type": "turn", "axis": [0.0, 0.0, 1.0],
                                     "degrees": [round(float(v), 4) for v in sk.turn_before_shot(frames, recoil, turn["degrees"], turn["ease_frames"])]}]
        spin = vanilla_wheel_spin(mesh, motion) if contract["kind"] == "vehicle" else None
        motions[role] = {
            "frames": frames,
            "scale": scale,
            "source": clip["anim"],
            "wheel_spin": None if spin is None else {"degrees": spin[0], "radius": spin[1] * scale},
            "bones": {bone: {"q": [[round(float(v), 7) for v in q] for q in channel["q"]],
                             "d": [[round(float(v) * scale, 6) for v in d] for d in channel["d"]]}
                      for bone, channel in motion.items()},
            "extras": extras,
        }
    return motions, barrel_length


def vanilla_wheel_spin(mesh, motion: dict):
    """A vanilla road wheel's turn about its axle per frame (degrees, unwrapped) and its radius, or None when the
    clip turns no wheel. The road wheel is the wheel bone whose carried surface is nearest vanilla's median wheel size."""

    wheels = [name for name in motion if name.startswith(("wheel_0", "wheel_1", "wheel_2"))]
    if not wheels:
        return None
    dominant = mesh.joints[np.arange(len(mesh.joints)), np.argmax(mesh.weights, axis=1)]
    radii = {}
    for name in wheels:
        chosen = (dominant == mesh.bones.index(name)) & ~mesh.collision
        if chosen.sum() >= 4:
            q = np.array([sk.to_blender(p) for p in mesh.positions[chosen]])
            q = q[(q[:, 0] - q[:, 0].mean()) >= 0] if ((q[:, 0] - q[:, 0].mean()) >= 0).sum() >= 4 else q
            radii[name] = float(max(np.ptp(q[:, 1]), np.ptp(q[:, 2])) / 2)
    if not radii:
        return None
    road = sorted(radii, key=lambda n: radii[n])[len(radii) // 2]
    quaternions = np.asarray(motion[road]["q"])
    angles = np.unwrap(2 * np.arctan2(quaternions[:, 1] * np.sign(quaternions[:, 0] + 1e-12), np.abs(quaternions[:, 0])))
    if np.ptp(angles) < 1e-3:
        return None
    return [round(float(v), 4) for v in np.degrees(angles - angles[0])], radii[road]


def vanilla_barrel_length(mesh) -> Optional[float]:
    """The length of the surface vanilla's barrel bones carry, along the hull (Blender y)."""

    dominant = mesh.joints[np.arange(len(mesh.joints)), np.argmax(mesh.weights, axis=1)]
    barrel = [i for i, name in enumerate(mesh.bones) if name.startswith("barrel")]
    chosen = np.isin(dominant, barrel) & ~mesh.collision
    if chosen.sum() < 4:
        return None
    return float(np.ptp(np.array([sk.to_blender(p) for p in mesh.positions[chosen]])[:, 1]))


def tread_textures(report: dict, contract: dict, name: str, files: Path, work: Path) -> Optional[dict]:
    """The tread texture of a tank's scrolling tracks (lib/static_kinds.tread_images), in the colour the run had in
    the model's own atlas (the median texel under its old UVs), at the size and link count of vanilla's tread."""

    if not report.get("tracks"):
        return None
    rule = contract["rules"]["tracks"]
    with Image.open(work / f"{name}_diffuse.png") as atlas:
        pixels = np.asarray(atlas.convert("RGB"))
    height, width = pixels.shape[:2]
    samples = [pixels[min(height - 1, int((1.0 - v) * height)) % height, min(width - 1, int(u * width)) % width] for u, v in report.get("track_atlas_uvs", [])]
    colour = np.median(np.array(samples), axis=0) if samples else np.array([70.0, 70.0, 65.0])
    images = sk.tread_images(colour, rule["links"], tuple(rule["texture_size"]))
    tone = (rule.get("tone") or {}).get("luma")
    if tone:
        # no brighter than vanilla's light tanks' treads (their texture's mean luma): a run painted in a light hull colour is darkened to it
        luma = float((images["diffuse"][..., :3].astype(float) @ np.array([0.299, 0.587, 0.114])).mean())
        target = sk.tread_target_luma(luma, tone)
        if target != luma:
            colour = sk.tread_colour_at(colour, luma, target)
            images = sk.tread_images(colour, rule["links"], tuple(rule["texture_size"]))
            report["track_tone"] = {"luma_before": round(luma, 1), "luma_after": round(target, 1)}
    written = {}
    for role, array in images.items():
        staged = work / f"{name}_tracks_{role}.png"
        Image.fromarray(array, "RGBA").save(staged)
        header = model_dds.write_dxt5(staged, files / f"{name}_tracks_{role}.dds")
        written[role] = {"file": f"{name}_tracks_{role}.dds", "size": [header["width"], header["height"]]}
    written["colour"] = [round(float(v), 1) for v in colour]
    return written


def registration(name: str, kind: str, contract: dict, roles: list, nodes: list, game: Path, tracks: bool = False) -> str:
    folder = FOLDERS[kind]
    animations = {role: f"{name}_{role}_animation" for role in roles}
    entity = contract["entity"]
    definitions = sk.scan_definitions(game, ("gfx/entities",)) if (game / "gfx/entities").is_dir() else {"entity": {}}
    reference = definitions["entity"].get(entity["reference"], {}).get("text")
    if not reference:
        raise SystemExit(f"vanilla's entity {entity['reference']} was not found under {game / 'gfx/entities'}")
    settings = [{"name": f"{name}Shape", "index": 0, "texture_diffuse": f"{name}_diffuse.dds", "texture_normal": f"{name}_normal.dds",
                 "texture_specular": f"{name}_specular.dds", "shader": contract["shader"]}]
    if tracks:
        # the shape's second stream, the track runs, on vanilla's scrolling shader (as vanilla's FIN_light_armor lists it)
        settings.append({"name": f"{name}Shape", "index": 1, "texture_diffuse": f"{name}_tracks_diffuse.dds", "texture_normal": f"{name}_tracks_normal.dds",
                         "texture_specular": f"{name}_tracks_specular.dds", "shader": contract["rules"]["tracks"]["shader"]})
    pdxmesh_scale = entity.get("pdxmesh_scale", 1.0)
    parts = ["objectTypes = {",
             sk.pdxmesh_text(name, f"{folder}/{name}/{name}.mesh", animations, settings, pdxmesh_scale if abs(pdxmesh_scale - 1.0) > 1e-9 else None),
             "}", ""]
    for role, animation in animations.items():
        parts += [sk.animation_text(animation, f"{folder}/{name}/{name}_{role}.anim"), ""]
    parts.append(sk.entity_text(reference, name, f"{name}_mesh", nodes, roles, entity.get("entity_scale", entity["scale"]), contract.get("role_aliases")))
    return "\n".join(parts) + "\n"


def job_contract(job: dict) -> tuple:
    """The kind's contract for this job and the job's raise for a tank's running gear (`running_gear_triangles`), sized
    to the vanilla model the job names (`size_reference`, sk.with_size_reference) when it names one."""

    running_gear = int(job.get("running_gear_triangles") or 0)
    contract = sk.with_size_reference(sk.kind_contract(job["model_kind"]), job.get("size_reference"))
    return sk.with_running_gear(contract, running_gear), running_gear


def atlas_source(glb: Path, out: Path) -> tuple:
    """The GLB the stage reads, and the atlas receipt: a GLB whose parts carry their own maps is rewritten with one
    atlas (`lib/glb_atlas.py`) under <out>/atlas, or the source and None when it has one map. STATIC-ATLAS stops the
    stage when the maps cannot share an atlas without changing the look."""

    try:
        receipt = glb_atlas.merged_glb(glb, out / "atlas" / glb.name)
    except glb_atlas.AtlasError as problem:
        raise SystemExit(f"STATIC-ATLAS: {problem}") from problem
    return (out / "atlas" / glb.name, receipt) if receipt else (glb, None)


def parts_plan(glb: Path, contract: dict, job: dict) -> Optional[dict]:
    """What the stage would do with a GLB made in parts: each part's triangles, need and first share of the reduction
    target (the stage keeps back a little more for the cards it thickens), or None for a model in one piece."""

    parts = static_parts.glb_parts(glb)
    if len(parts) < 2 or job.get("parts", "auto") is False:
        return None
    needs = [static_parts.part_need(p, t) for _name, p, t in parts]
    target = int(contract["triangle_budget"]["value"] * 0.94)
    try:
        shares = static_parts.allocate(needs, target)
    except static_parts.PartsBudgetError as problem:
        return {"target": target, "problem": str(problem)}
    weights = static_parts.need_weights(needs)
    return {"target": target, "parts": {name: {"triangles": n["triangles"], "need": round(w, 4), "share": share}
                                        for (name, _p, _t), n, w, share in zip(parts, needs, weights, shares)}}


def parts_summary(report: dict):
    """Each source part's triangles before and after its reduction, the part names when the model was within its target,
    or None for a model in one piece."""

    source = (report.get("reduction", {}).get("parts") or {}).get("parts")
    return {k: [v["from"], v["to"]] for k, v in source.items()} if isinstance(source, dict) else source


def run_blender(request_path: Path, log: Path) -> None:
    import review_unit

    completed = heavy_job.run([str(review_unit.find_blender()), "-b", "--factory-startup", "--python", str(BLENDER_SCRIPT), "--", str(request_path)],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
    log.write_text(completed.stdout[-40000:] + completed.stderr[-20000:], encoding="utf-8")
    if "STATIC_MODEL_DONE" not in completed.stdout:
        tail = [line for line in (completed.stdout + completed.stderr).splitlines() if line.strip()][-8:]
        raise SystemExit("Blender did not finish the model; see " + str(log) + "\n" + "\n".join(tail))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("job", type=Path, help="the inbox's <name>.json (name, model_kind, optional glb and front)")
    parser.add_argument("--out", type=Path, required=True, help="the job folder (the mod tree goes to <out>/mod)")
    parser.add_argument("--front", choices=sorted(sk.FRONT_TURNS), help="which way the model faces as imported (default: found by rule)")
    parser.add_argument("--plan", action="store_true", help="only run the geometry rules on the GLB and print them")
    parser.add_argument("--keep-blend", action="store_true", help="also save the Blender scene (tens of megabytes) for a look by hand")
    parser.add_argument("--game", type=Path, help="the game folder (default: the one .tools/lib/game.py finds)")
    args = parser.parse_args(argv)
    job = json.loads(args.job.read_text(encoding="utf-8"))
    name, kind = job["name"], job["model_kind"]
    glb = (args.job.parent / job.get("glb", f"{name}.glb")).resolve()
    contract, running_gear = job_contract(job)
    front = args.front or job.get("front")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if args.plan:
        points, triangles = sk.read_glb_geometry(glb)
        print(json.dumps({**sk.plan(points, triangles, contract, front), "parts": parts_plan(glb, contract, job)}, indent=1, default=float))
        return 0
    game = args.game or game_dir()
    files = out / "mod" / FOLDERS[kind] / name
    if files.exists():
        shutil.rmtree(files)
    files.mkdir(parents=True)
    delight: dict = {}
    glb, atlas = atlas_source(glb, out)
    textures = pack_textures(glb, contract, name, files, out / "textures", delight, front, game)
    motion, barrel_length = clip_motion(game, contract) if contract.get("clips") else ({}, None)
    hole = hole_texel(glb, out / "textures" / f"{name}_diffuse.png") if kind == "vehicle" else None
    request = {
        "glb": str(glb), "name": name, "out": str(files), "contract": contract, "front": front,
        "textures": {role: entry["file"] for role, entry in textures.items()},
        "motion": motion, "vanilla_barrel_length": barrel_length,
        # Blender's v runs up, glTF's down
        "hole_uv": [hole["uv"][0], 1.0 - hole["uv"][1]] if hole else None,
        "report": str(out / "blender_report.json"), "blend": str(out / f"{name}.blend") if args.keep_blend else None,
        "parts": job.get("parts", "auto"), "part_shape_iou": job.get("part_shape_iou"),
    }
    request_path = out / "blender_request.json"
    request_path.write_text(json.dumps(request), encoding="utf-8", newline="\n")
    run_blender(request_path, out / "blender.log")
    report = json.loads((out / "blender_report.json").read_text(encoding="utf-8"))
    nodes = list(report.get("locators", {})) + list(report.get("bones", {}))
    entities = out / "mod" / "gfx" / "entities"
    entities.mkdir(parents=True, exist_ok=True)
    (entities / f"{name}.asset").write_text(registration(name, kind, contract, list(motion), nodes, game, bool(report.get("tracks"))), encoding="utf-8", newline="\n")
    report["textures"] = textures
    report["delight"] = delight
    report.update(hole=hole, atlas=atlas)
    report["tread"] = tread_textures(report, contract, name, files, out / "textures")
    (out / "blender_report.json").write_text(json.dumps(report, indent=1), encoding="utf-8", newline="\n")
    import check_unit_files

    verdict = out / "verdict_check.json"
    code = check_unit_files.main([str(files), "--model-kind", kind, "--mod-root", str(out / "mod"), "--verdict", str(verdict)]
                                 + (["--running-gear-triangles", str(running_gear)] if running_gear else [])
                                 + (["--size-reference", str(job["size_reference"])] if job.get("size_reference") else []))
    problems = report.get("reduction", {}).get("problems") or []
    if problems:
        # STATIC-SHAPE: the reduction to vanilla's budget lost part of the silhouette (lib/tripo_shape.py)
        print(f"STATIC-SHAPE: reducing {name} to {report['reduction']['budget']} triangles changed its outline: " + "; ".join(problems))
        code = 1
    print(json.dumps({"tool": "static_model", "name": name, "kind": kind, "files": str(files), "triangles": report.get("triangles"),
                      "parts": report.get("parts", {}).get("triangles_per_part"), "reduction_problems": report.get("reduction", {}).get("problems"),
                      "source_parts": parts_summary(report),
                      "check": "pass" if code == 0 else "fail"}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
