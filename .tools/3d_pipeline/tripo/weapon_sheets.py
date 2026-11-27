"""Two extra review sheets for a unit with a held weapon: does the weapon pass through the body, and how does it read at game size.

    py -3.13 -B .tools/3d_pipeline/tripo/weapon_sheets.py <unit folder> --out <review folder> --sheet close
    py -3.13 -B .tools/3d_pipeline/tripo/weapon_sheets.py <unit folder> --out <review folder> --sheet game
    py -3.13 -B .tools/3d_pipeline/tripo/weapon_sheets.py <unit folder> --out <review folder> --sheet preview --jobs-config <3d_jobs.json> --unit <slug>
    py -3.13 -B .tools/3d_pipeline/tripo/weapon_sheets.py <unit folder> --out <review folder> --sheet preview --entity-scale <scale> [--reference <vanilla .mesh> --reference-scale <scale>]

`--sheet close` writes `sheets/weapon_frames.png`: every clip of the unit (one row each), three evenly
spaced frames (first, middle, last), a front three-quarter view at close-up size. `--sheet game` writes
`sheets/game_size.png` (and a 3x nearest-neighbour copy for reading): the idle and move clips, four
frames each, in the HOI4 map camera and the front view, scaled so the unit is about 60 px tall. It judges the still model's size and
silhouette beside vanilla. `--sheet preview` writes `sheets/preview_size.png`: every clip in six frames in tiles the size of the game's
designer preview (`lib/designer_preview.py`, 249 px), where the clips are judged (D-140). It draws them with the designer's camera, measured
in the game, at the unit's entity scale, so the unit is as large in each tile as the game shows it. Its first row is the vanilla
reference of the unit's class (the job's `vanilla_scale_reference`, else vanilla's light tank) under the same camera.
Each call is one Blender start (the review renderer), so a caller can gate them one by one.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

import review_unit
import run_pilot
from lib import designer_preview, heavy_job, pdx_deform

THREE_QUARTER = {"threequarter": [35, 8]}
CLOSE_SIZE, CLOSE_SHARE = 512, 1.15
GAME_SIZE, GAME_HEIGHT_PX = 160, 60
PBR = True  # shade from the packed specular, as the game does; False is the old Workbench studio light
LABEL = 20
CAPTION_BREAK = "|"  # a caption's lines are split here


def evenly(frames: int, count: int) -> List[int]:
    last = max(frames - 1, 0)
    return sorted({round(last * k / max(count - 1, 1)) for k in range(count)})


RIDER: Dict = {}  # the `attach` block for a mount's rider (review_unit.rider_attach), set by --rider


def render_tiles(folder: Path, out: Path, wanted: List[str], count: int, views: List[str], angles: Dict, size: int, share: float,
                 ortho: Optional[float] = None, tiles_name: str = "weapon_tiles", reference: Optional[Dict] = None) -> dict:
    """Render the tiles through the review renderer. `ortho` fixes the frame's width in the mesh's own units instead of fitting the
    unit (`share` times its largest extent). `reference` renders a vanilla mesh in place instead, in its rest pose only: `{"mesh": path,
    "diffuse": maps, "specular": maps}` (`reference_maps`)."""

    if reference:
        mesh_path, owned = Path(reference["mesh"]), []
    else:
        meshes = sorted(folder.glob("*.mesh"))
        mesh_path = meshes[0]
        owned = review_unit.owned_anims(folder, mesh_path.stem, [m.stem for m in meshes])
    clips = []
    for anim in owned:
        role = anim.stem[len(mesh_path.stem) + 1 :]
        if wanted and role not in wanted:
            continue
        clips.append({"name": anim.stem, "path": str(anim.resolve()), "frames": evenly(pdx_deform.load_anim(anim).frames, count)})
    request = {
        "out": str((out / tiles_name).resolve()),
        "mesh": str(mesh_path.resolve()),
        "diffuse": reference["diffuse"] if reference else review_unit.diffuse_maps(mesh_path.resolve(), review_unit.gfx_texts(None)),
        "specular": reference["specular"] if reference else review_unit.specular_maps(mesh_path.resolve()),
        "pbr": PBR,
        "clips": clips,
        "views": views,
        "view_angles": angles,
        "ortho_share": share,
        "diagnostic_views": [],
        "size": size,
    }
    if ortho:
        request["ortho_scale"] = float(ortho)
    if RIDER:
        request["attach"] = review_unit.rider_attach(Path(RIDER["folder"]), RIDER.get("stem"), RIDER["scale"], RIDER["roles"], [c["name"] for c in clips])
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{tiles_name}_request.json"
    path.write_text(json.dumps(request, indent=1), encoding="utf-8", newline="\n")
    completed = heavy_job.run(
        [str(review_unit.find_blender()), "-b", "--python", str(review_unit.BLENDER_SCRIPT), "--", str(path.resolve())],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if "REVIEW_RENDERED" not in completed.stdout:
        raise SystemExit("Blender did not finish the renders: " + (completed.stdout + completed.stderr)[-1500:])
    return json.loads((out / tiles_name / "index.json").read_text(encoding="utf-8"))


def unit_pixels(tile: Image.Image) -> tuple:
    """Bounding box of the lit unit: not the magenta world, not the dark ground disc (sampled in the corner)."""

    pixels = np.asarray(tile.convert("RGB")).astype(int)
    magenta = (pixels[..., 0] > 240) & (pixels[..., 1] < 15) & (pixels[..., 2] > 240)
    ground = np.abs(pixels - pixels[-3, 3]).sum(-1) < 12
    mask = ~magenta & ~ground
    rows, columns = np.where(mask)
    return (columns.min(), rows.min(), columns.max() + 1, rows.max() + 1) if len(rows) else (0, 0, tile.width, tile.height)


def sheet(index: dict, tiles: Path, views: List[str], clip_names: List[str], title_of, scale=None) -> Image.Image:
    """One row per clip: a band with the clip's name, then the tiles, each with a caption under it (frame, then view) in a cell as wide as
    the tile or its caption, whichever is wider, so no caption runs into its neighbour at any tile size."""

    rows = []
    for name in clip_names:
        clip = next(c for c in index["clips"] if c["name"] == name)
        rows.append((name, clip["rows"]))
    font = ImageFont.load_default()
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    cells = []  # per row: [(tile image, caption lines)]
    for name, frames in rows:
        row = []
        for entry in frames:
            for view in views:
                tile = Image.open(tiles / entry["tiles"][view]).convert("RGB")
                row.append((tile, title_of(name, entry["frame"], view).split(CAPTION_BREAK)))
        cells.append(row)
    pad = 6
    tile_width = max(tile.width for row in cells for tile, _ in row)
    tile_height = max(tile.height for row in cells for tile, _ in row)
    caption_width = max(int(probe.textlength(line, font=font)) for row in cells for _, lines in row for line in lines)
    cell = max(tile_width, caption_width) + pad
    lines_per = max(len(lines) for row in cells for _, lines in row)
    caption_height = lines_per * (LABEL // 2 + 1) + 6
    band = LABEL
    row_height = band + tile_height + caption_height
    per_row = max(len(row) for row in cells)
    image = Image.new("RGB", (max(cell * per_row, int(probe.textlength(max((n for n, _ in rows), key=len), font=font)) + 2 * pad), row_height * len(rows)), (30, 30, 30))
    draw = ImageDraw.Draw(image)
    for r, ((name, _frames), row) in enumerate(zip(rows, cells)):
        top = r * row_height
        draw.text((pad, top + 5), name.split("_", 1)[-1] if "_" in name else name, fill=(255, 220, 120), font=font)
        for c, (tile, lines) in enumerate(row):
            left = c * cell + (cell - tile.width) // 2
            image.paste(tile, (left, top + band))
            for k, line in enumerate(lines):
                width = int(probe.textlength(line, font=font))
                draw.text((c * cell + (cell - width) // 2, top + band + tile_height + 2 + k * (LABEL // 2 + 1)), line, fill=(255, 255, 255), font=font)
    return image


def close_sheet(folder: Path, out: Path) -> Path:
    index = render_tiles(folder, out, [], 3, ["threequarter"], THREE_QUARTER, CLOSE_SIZE, CLOSE_SHARE)
    names = [c["name"] for c in index["clips"] if c["name"] != "rest"]
    image = sheet(index, out / "weapon_tiles", ["threequarter"], names, lambda n, f, v: f"frame {f}")
    target = out / "sheets" / "weapon_frames.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    return target


def game_sheet(folder: Path, out: Path) -> Path:
    # Every role at the size a player sees it: a reviewer judges the attack, death and the rest there too, not only the idle and the walk.
    index = render_tiles(folder, out, [], 4, ["hoi4", "front"], {}, GAME_SIZE, 1.45)
    tiles = out / "weapon_tiles"
    names = [c["name"] for c in index["clips"] if c["name"] != "rest"]
    # Scale every tile by one factor so the unit in the front view is GAME_HEIGHT_PX tall.
    probe = next(Image.open(tiles / row["tiles"]["front"]) for c in index["clips"] if c["name"] in names for row in c["rows"][:1])
    left, top, right, bottom = unit_pixels(probe)
    factor = GAME_HEIGHT_PX / max(bottom - top, 1)
    small = max(1, round(GAME_SIZE * factor))
    for clip in index["clips"]:
        for row in clip["rows"]:
            for name in row["tiles"].values():
                path = tiles / name
                Image.open(path).convert("RGB").resize((small, small), Image.Resampling.LANCZOS).save(path)
    image = sheet(index, tiles, ["hoi4", "front"], names, lambda n, f, v: f"f{f}{CAPTION_BREAK}{v}")
    target = out / "sheets" / "game_size.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    image.resize((image.width * 3, image.height * 3), Image.Resampling.NEAREST).save(out / "sheets" / "game_size_x3.png")
    print(f"unit height in the front view: {bottom - top} px at {GAME_SIZE} px, scaled by {factor:.3f} to {GAME_HEIGHT_PX} px (tile {small} px)")
    return target


PREVIEW = {"entity_scale": None, "reference": None, "reference_scale": None}  # set by --jobs-config/--unit or --entity-scale, --reference


def preview_settings(jobs_config: Optional[Path], unit: Optional[str], entity_scale: Optional[float], reference: Optional[str],
                     reference_scale: Optional[float]) -> Dict:
    """The unit's entity scale and its class's vanilla reference (a `.mesh` and its entity scale): the job's `runtime_entity_scale`
    and `vanilla_scale_reference`, each overridden by the option given, the reference falling back to vanilla's light tank
    (`designer_preview.VEHICLE_REFERENCE`)."""

    job: Dict = {}
    if jobs_config and unit:
        job = json.loads(Path(jobs_config).read_text(encoding="utf-8"))["jobs"][unit]
    known = job.get("vanilla_scale_reference") or {}
    scale = entity_scale if entity_scale is not None else job.get("runtime_entity_scale", known.get("entity_scale"))
    if scale is None:
        raise SystemExit("the preview sheet draws the unit at its size in the game: give --jobs-config and --unit, or --entity-scale")
    mesh = reference or known.get("mesh") or designer_preview.VEHICLE_REFERENCE["mesh"]
    if reference_scale is not None:
        ref_scale = reference_scale
    elif reference:
        raise SystemExit("--reference needs --reference-scale, the vanilla entity's own scale")
    else:
        ref_scale = known.get("entity_scale") if known.get("mesh") else designer_preview.VEHICLE_REFERENCE["entity_scale"]
    path = Path(mesh)
    if not path.is_absolute():
        path = Path(run_pilot.installed_game_dir()) / mesh
    return {"entity_scale": float(scale), "reference": path, "reference_scale": float(ref_scale)}


def reference_maps(mesh: Path) -> Dict:
    """A vanilla mesh's body maps for `render_tiles`, read from the mesh's own material (`diff`, `spec`): vanilla textures often carry
    another name than the mesh (`western_european_infantry.mesh` uses `western_europe_infantry_diffuse.dds`). The mesh renders in place,
    so io_pdx_mesh finds its other materials' maps (a tank's tracks) beside it."""

    diffuse: Dict[str, str] = {}
    specular: Dict[str, str] = {}
    for shape in pdx_deform.read(mesh).child("object").children:
        for stream in (node for node in shape.children if node.name == "mesh"):
            material = stream.child("material")
            if material is None or (material.properties.get("shader") or [""])[0] != "PdxMeshAdvanced":
                continue  # collision boxes, and a tank's scrolling tracks, which keep their own maps
            for key, maps in (("diff", diffuse), ("spec", specular)):
                name = (material.properties.get(key) or [""])[0]
                if name and (mesh.parent / name).is_file():
                    maps.setdefault("*", str(mesh.parent / name))
    return {"mesh": str(mesh.resolve()), "diffuse": diffuse or review_unit.diffuse_maps(mesh.resolve(), []),
            "specular": specular or review_unit.specular_maps(mesh.resolve())}


def preview_sheet(folder: Path, out: Path) -> Path:
    """Every clip at the size of the game's designer preview, where a player watches a unit's animations (D-140): six frames each, in tiles
    `designer_preview.PREVIEW_PX` square, drawn with the designer's camera at the unit's entity scale. The first row is the class's vanilla
    reference under the same camera, so a reviewer sees the unit's size as the game shows it."""

    settings = PREVIEW if PREVIEW["entity_scale"] else preview_settings(None, None, None, None, None)
    view = {"designer": list(designer_preview.VIEW)}
    size = designer_preview.PREVIEW_PX
    reference = settings["reference"]
    ref_index = render_tiles(reference.parent, out, [], 1, ["designer"], view, size, 1.0, ortho=designer_preview.ortho_for(settings["reference_scale"]),
                             tiles_name="preview_reference_tiles", reference=reference_maps(reference))
    index = render_tiles(folder, out, [], 6, ["designer"], view, size, 1.0, ortho=designer_preview.ortho_for(settings["entity_scale"]),
                         tiles_name="preview_tiles")
    names = [c["name"] for c in index["clips"] if c["name"] != "rest"]
    label = f"vanilla {reference.stem} (scale {settings['reference_scale']:g}), the same camera"
    top = sheet(ref_index, out / "preview_reference_tiles", ["designer"], ["rest"], lambda n, f, v: label)
    body = sheet(index, out / "preview_tiles", ["designer"], names, lambda n, f, v: f"frame {f}")
    image = Image.new("RGB", (max(top.width, body.width), top.height + body.height), (30, 30, 30))
    image.paste(top, (0, 0))
    image.paste(body, (0, top.height))
    target = out / "sheets" / "preview_size.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    fill = designer_preview.GAME_FILL
    print(f"designer preview: tiles {size} px ({designer_preview.GUI_FILE}, toggle_model_selector_button), camera {designer_preview.VIEW} "
          f"with the frame {designer_preview.FRAME_WORLD:g} game units wide (fitted on {fill['unit']}: {fill['width']:.2f} by "
          f"{fill['height']:.2f} of the frame in HOI4 {fill['build']}); unit entity scale {settings['entity_scale']:g}")
    return target


SHEETS = {"close": close_sheet, "game": game_sheet, "preview": preview_sheet}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sheet", choices=tuple(SHEETS), required=True)
    parser.add_argument("--rider", type=Path, help="a mount's rider folder, drawn on the mount's Saddle_Node (as review_unit.py --rider)")
    parser.add_argument("--rider-stem")
    parser.add_argument("--rider-scale", type=float, default=1.0)
    parser.add_argument("--rider-roles", nargs="*", default=[], metavar="ROLE=RIDER_ROLE")
    parser.add_argument("--jobs-config", type=Path, help="--sheet preview: the job file whose entry gives the entity scale and vanilla reference")
    parser.add_argument("--unit", help="--sheet preview: the unit's slug in --jobs-config")
    parser.add_argument("--entity-scale", type=float, help="--sheet preview: the unit entity's scale, when no job gives it")
    parser.add_argument("--reference", help="--sheet preview: the class's vanilla .mesh (a path in the game folder, or absolute)")
    parser.add_argument("--reference-scale", type=float, help="--sheet preview: that vanilla entity's scale")
    heavy_job.add_argument(parser)
    args = parser.parse_args()
    heavy_job.apply(args)
    if args.rider:
        RIDER.update(folder=str(args.rider), stem=args.rider_stem, scale=args.rider_scale, roles=dict(pair.split("=", 1) for pair in args.rider_roles))
    if args.sheet == "preview":
        PREVIEW.update(preview_settings(args.jobs_config, args.unit, args.entity_scale, args.reference, args.reference_scale))
    target = SHEETS[args.sheet](args.folder, args.out)
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
