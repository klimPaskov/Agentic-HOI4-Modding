"""Turn a Tripo GLB of a building, landmark, ship, tank or plane into HOI4 files, for free in Blender.

    py -3.13 -B .tools/3d_pipeline/tripo/static_model.py <inbox>/<name>.json --out <job folder>
    py -3.13 -B .tools/3d_pipeline/tripo/static_model.py <inbox>/<name>.json --out <job folder> --plan

The job file names the model and its `model_kind` (building, landmark, ship, vehicle, plane); the GLB is
`<name>.glb` next to it (or the job's `glb`). An optional `front` (`-y`, `+y`, `-x`, `+x`) overrides which way
the model is found to face. Everything else comes from the kind's contract in `config/static_kinds.json`, measured
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
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

import numpy as np
from PIL import Image

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import model_dds, pdx_deform  # noqa: E402
from lib import static_kinds as sk  # noqa: E402
from lib.texture_lineage import embedded_images  # noqa: E402
from pack_pdx_material import remap_gloss_table  # noqa: E402

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


def pack_textures(glb: Path, contract: dict, name: str, files: Path, work: Path) -> Dict[str, dict]:
    """The GLB's base colour, normal and metallic-roughness maps as the kind's PDX diffuse, normal and specular DDS."""

    images = embedded_images(glb)
    if not images["diffuse"]:
        raise SystemExit(f"{glb.name} has no base colour map")
    if len(images["diffuse"]) > 1:
        raise SystemExit(f"{glb.name} has {len(images['diffuse'])} base colour maps; the route packs one atlas")
    size = int(contract["texture_size"])
    work.mkdir(parents=True, exist_ok=True)
    colour = _resize(Image.open(io.BytesIO(images["diffuse"][0])).convert("RGBA"), size)
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
        motions[role] = {
            "frames": frames,
            "scale": scale,
            "source": clip["anim"],
            "bones": {bone: {"q": [[round(float(v), 7) for v in q] for q in channel["q"]],
                             "d": [[round(float(v) * scale, 6) for v in d] for d in channel["d"]]}
                      for bone, channel in motion.items()},
            "extras": extras,
        }
    return motions, barrel_length


def vanilla_barrel_length(mesh) -> Optional[float]:
    """The length of the surface vanilla's barrel bones carry, along the hull (Blender y)."""

    dominant = mesh.joints[np.arange(len(mesh.joints)), np.argmax(mesh.weights, axis=1)]
    barrel = [i for i, name in enumerate(mesh.bones) if name.startswith("barrel")]
    chosen = np.isin(dominant, barrel) & ~mesh.collision
    if chosen.sum() < 4:
        return None
    return float(np.ptp(np.array([sk.to_blender(p) for p in mesh.positions[chosen]])[:, 1]))


def registration(name: str, kind: str, contract: dict, roles: list, nodes: list, game: Path) -> str:
    folder = FOLDERS[kind]
    animations = {role: f"{name}_{role}_animation" for role in roles}
    entity = contract["entity"]
    definitions = sk.scan_definitions(game, ("gfx/entities",)) if (game / "gfx/entities").is_dir() else {"entity": {}}
    reference = definitions["entity"].get(entity["reference"], {}).get("text")
    if not reference:
        raise SystemExit(f"vanilla's entity {entity['reference']} was not found under {game / 'gfx/entities'}")
    settings = [{"name": f"{name}Shape", "index": 0, "texture_diffuse": f"{name}_diffuse.dds", "texture_normal": f"{name}_normal.dds",
                 "texture_specular": f"{name}_specular.dds", "shader": contract["shader"]}]
    pdxmesh_scale = entity.get("pdxmesh_scale", 1.0)
    parts = ["objectTypes = {",
             sk.pdxmesh_text(name, f"{folder}/{name}/{name}.mesh", animations, settings, pdxmesh_scale if abs(pdxmesh_scale - 1.0) > 1e-9 else None),
             "}", ""]
    for role, animation in animations.items():
        parts += [sk.animation_text(animation, f"{folder}/{name}/{name}_{role}.anim"), ""]
    parts.append(sk.entity_text(reference, name, f"{name}_mesh", nodes, roles, entity.get("entity_scale", entity["scale"])))
    return "\n".join(parts) + "\n"


def run_blender(request_path: Path, log: Path) -> None:
    import review_unit

    completed = subprocess.run([str(review_unit.find_blender()), "-b", "--factory-startup", "--python", str(BLENDER_SCRIPT), "--", str(request_path)],
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
    parser.add_argument("--game", type=Path, help="the game folder (default: the one .tools/lib/game.py finds)")
    args = parser.parse_args(argv)
    job = json.loads(args.job.read_text(encoding="utf-8"))
    name, kind = job["name"], job["model_kind"]
    glb = (args.job.parent / job.get("glb", f"{name}.glb")).resolve()
    contract = sk.kind_contract(kind)
    front = args.front or job.get("front")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if args.plan:
        points, triangles = sk.read_glb_geometry(glb)
        print(json.dumps(sk.plan(points, triangles, contract, front), indent=1, default=float))
        return 0
    game = args.game or game_dir()
    files = out / "mod" / FOLDERS[kind] / name
    if files.exists():
        shutil.rmtree(files)
    files.mkdir(parents=True)
    textures = pack_textures(glb, contract, name, files, out / "textures")
    motion, barrel_length = clip_motion(game, contract) if contract.get("clips") else ({}, None)
    request = {
        "glb": str(glb), "name": name, "out": str(files), "contract": contract, "front": front,
        "textures": {role: entry["file"] for role, entry in textures.items()},
        "motion": motion, "vanilla_barrel_length": barrel_length,
        "report": str(out / "blender_report.json"), "blend": str(out / f"{name}.blend"),
    }
    request_path = out / "blender_request.json"
    request_path.write_text(json.dumps(request), encoding="utf-8", newline="\n")
    run_blender(request_path, out / "blender.log")
    report = json.loads((out / "blender_report.json").read_text(encoding="utf-8"))
    nodes = list(report.get("locators", {})) + list(report.get("bones", {}))
    entities = out / "mod" / "gfx" / "entities"
    entities.mkdir(parents=True, exist_ok=True)
    (entities / f"{name}.asset").write_text(registration(name, kind, contract, list(motion), nodes, game), encoding="utf-8", newline="\n")
    report["textures"] = textures
    (out / "blender_report.json").write_text(json.dumps(report, indent=1), encoding="utf-8", newline="\n")
    import check_unit_files

    verdict = out / "verdict_check.json"
    code = check_unit_files.main([str(files), "--model-kind", kind, "--mod-root", str(out / "mod"), "--verdict", str(verdict)])
    problems = report.get("reduction", {}).get("problems") or []
    if problems:
        # STATIC-SHAPE: the reduction to vanilla's budget lost part of the silhouette (lib/tripo_shape.py)
        print(f"STATIC-SHAPE: reducing {name} to {report['reduction']['budget']} triangles changed its outline: " + "; ".join(problems))
        code = 1
    print(json.dumps({"tool": "static_model", "name": name, "kind": kind, "files": str(files), "triangles": report.get("triangles"),
                      "parts": report.get("parts", {}).get("triangles_per_part"), "reduction_problems": report.get("reduction", {}).get("problems"),
                      "check": "pass" if code == 0 else "fail"}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
