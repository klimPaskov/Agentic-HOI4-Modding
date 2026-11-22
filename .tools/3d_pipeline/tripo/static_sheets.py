"""Review sheets for a static or rigid-part model (building, landmark, ship, vehicle, plane) from `tripo/static_model.py`.

    py -3.13 -B .tools/3d_pipeline/tripo/static_sheets.py <model folder> --model-kind vehicle --out <job folder>/review

Two Blender starts, one after the other (a caller can gate them one by one with `--only close|game`):

- `close`: `review_unit.render` at 512 px: every clip from front, left, back, right, the map camera and below, with
  the diagnostics sheets, and `REVIEW_REQUEST.md` with the quality bar of `config/visual_review_prompt.md`, the
  checklist and the kind's fixed notes (`KIND_NOTES`: what the kind is, so a reviewer does not judge a tank by a
  soldier's feet).
- `game`: `sheets/game_size.png` (and a 3x nearest-neighbour copy): the model and the vanilla model its size and entity
  come from, side by side in the map camera and the front view, at the pixels a metre a vanilla soldier gets on the
  map (60 px for `humanoid_unit`'s runtime height, as `weapon_sheets.py`). The vanilla model is the one nearest the kind's
  median size (`size.nearest`). Each is drawn at its runtime size (mesh
  size times entity scale), so the sheet shows whether the model reads, and is as big as vanilla's, at game size.

Give `REVIEW_REQUEST.md` and the sheets, and nothing else, to a fresh reviewer, and record the reply with
`review_unit.py <model folder> --out <job folder>/review --record reply.md`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from PIL import Image, ImageDraw, ImageFont

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

import numpy as np

import review_unit
from lib import heavy_job
from lib import static_kinds as sk

# The pixels a metre of runtime size gets at game size: a vanilla soldier (humanoid_unit's source height 7.351824 at
# entity scale 0.8, config/asset_profiles.json) is 60 px tall on the map camera (weapon_sheets.GAME_HEIGHT_PX).
SOLDIER_RUNTIME_HEIGHT = 7.351824 * 0.8
PX_PER_METRE = 60 / SOLDIER_RUNTIME_HEIGHT
RENDER_SIZE, SHARE = 256, 1.45
# The close-up of the rest pose: two three-quarter views from the front and the back, framed tight, at 1024 px, so a
# long thin model (a ship, a plane) shows its small parts (a mast, gun stubs) larger than on the six-view sheets.
CLOSE_ANGLES = {"front_quarter": [35, 20], "back_quarter": [215, 20]}
CLOSE_SIZE, CLOSE_SHARE = 1024, 1.05
WATER_ALPHA = 0.6
KIND_NOTES = {
    "vehicle": [
        "This is a WW2 light tank, a vehicle made of rigid parts (hull, turret, gun). It has no feet: for item 5, its tracks rest on the green disc.",
        "The turret turns and the gun recoils by design. In idle the whole tank stands turned 45 degrees from its heading for the whole clip and only the turret moves, as every vanilla tank idle does (33 of 33).",
        "In the move the hull and running gear rock nose up and down on their suspension by a few degrees, as vanilla tank moves do (GER light tank up to 3.6 degrees).",
        "In the move clip the tread pattern on the tracks scrolls along the track runs, as vanilla tanks' tracks do.",
        "In the death clip the turret is blown off the hull and lands beside it, as vanilla tanks' death does: a turret leaving the hull there is the intended look.",
    ],
    "plane": [
        "This is a WW2 single-engine fighter. In game it flies. It is rendered just above the green disc. It has no feet, so item 5 does not apply.",
        "The propeller spins by design: between frames the blades are at different angles.",
    ],
    "ship": [
        "This is a WW2 warship. The green disc is the water surface: the hull below it is under water in game and hidden there.",
        "It is sized to the length of vanilla's destroyer. Its beam, superstructure and colours are its own design.",
        "The ship rocks on the water in idle. Like vanilla's support ship and freighter it has no attack clip: in game the shot shows as muzzle and water effects.",
        "The green disc is drawn see-through, so the hull under the water shows darker through it.",
        "In idle the ship only bobs gently on the water, as vanilla's destroyer does. In the death clip it tips up steeply and sinks, as vanilla's destroyer does. The whole hull is one rigid part.",
    ],
    "building": ["This is a static map building with no animation: the rest pose is its only clip. It stands on the green disc. It has no feet, so item 5 means its base meets the ground."],
    "landmark": ["This is a static landmark (a monument) with no animation: the rest pose is its only clip. It stands on the green disc. It has no feet, so item 5 means its base meets the ground."],
}


def close_review(folder: Path, kind: str, out: Path, notes: List[str]) -> List[Path]:
    # the disc is the game's ground (a ship's water) at z = 0, where the route puts it
    # a ship's water is see-through (60 % opaque), so the hull under it shows as it sinks
    sheets = review_unit.render(folder, None, out, None, review_unit.REVIEW_STEP, count=5, size=512, diagnostics=True, notes=KIND_NOTES[kind] + notes, checklist=True, ground_z=0.0,
                                ground_alpha=WATER_ALPHA if kind == "ship" else 1.0,
                                texture_anim_speed=(sk.kind_contract(kind).get("rules", {}).get("tracks") or {}).get("texture_anim_speed"), sun_shadow=False)
    mesh = sorted(folder.glob("*.mesh"))[0]
    index = render_rest(mesh, out / "closeup_tiles", [], views=tuple(CLOSE_ANGLES), size=CLOSE_SIZE, share=CLOSE_SHARE)
    row = index["clips"][0]["rows"][0]["tiles"]
    tiles = [Image.open(out / "closeup_tiles" / row[view]).convert("RGB") for view in CLOSE_ANGLES]
    image = Image.new("RGB", (sum(t.width for t in tiles), tiles[0].height + 20), (30, 30, 30))
    draw = ImageDraw.Draw(image)
    for k, (tile, view) in enumerate(zip(tiles, CLOSE_ANGLES)):
        image.paste(tile, (k * tile.width, 20))
        draw.text((k * tile.width + 4, 4), f"rest close-up {view}", fill=(230, 230, 230), font=ImageFont.load_default())
    target = out / "sheets" / "rest_closeup.png"
    image.save(target)
    return sheets + [target]


def render_rest(mesh: Path, out: Path, texts: List[str], views=("hoi4", "front"), size: int = RENDER_SIZE, share: float = SHARE,
                ground_alpha: float = 1.0) -> dict:
    request = {
        "out": str(out.resolve()), "mesh": str(mesh.resolve()),
        "diffuse": review_unit.diffuse_maps(mesh.resolve(), texts), "specular": review_unit.specular_maps(mesh.resolve()),
        "pbr": True, "clips": [], "views": list(views), "view_angles": CLOSE_ANGLES, "diagnostic_views": [], "size": size, "ortho_share": share,
        "ground_z": 0.0, "ground_alpha": ground_alpha, "sun_shadow": False,
    }
    out.mkdir(parents=True, exist_ok=True)
    path = out / "request.json"
    path.write_text(json.dumps(request, indent=1), encoding="utf-8", newline="\n")
    completed = heavy_job.run([str(review_unit.find_blender()), "-b", "--python", str(review_unit.BLENDER_SCRIPT), "--", str(path.resolve())],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
    if "REVIEW_RENDERED" not in completed.stdout:
        raise SystemExit("Blender did not finish the renders: " + (completed.stdout + completed.stderr)[-1500:])
    return json.loads((out / "index.json").read_text(encoding="utf-8"))


def model_columns(tile: Image.Image) -> tuple:
    """The first and last pixel columns the model covers in a tile: pixels unlike every colour on the tile's border
    (the magenta world and the ground disc both reach the border; the model does not)."""

    pixels = np.asarray(tile.convert("RGB")).astype(int)
    border = np.unique(np.concatenate([pixels[0], pixels[-1], pixels[:, 0], pixels[:, -1]]), axis=0)
    distance = np.abs(pixels[:, :, None, :] - border[None, None, :, :]).sum(-1).min(axis=2)
    columns = np.nonzero((distance > 24).any(axis=0))[0]
    return (int(columns.min()), int(columns.max()) + 1) if len(columns) else (0, tile.width)


def _points(mesh: Path):
    """The rendered (not `Collision`) points of a mesh, in Blender space."""

    from lib import pdx_deform

    loaded = pdx_deform.load_mesh(mesh)
    visible = ~loaded.collision if len(loaded.collision) else slice(None)
    return np.array([sk.to_blender(p) for p in loaded.positions[visible]])


def _span(mesh: Path) -> float:
    """The rest pose's largest side, which the review camera frames (`review_render.py`: ortho scale = span x share)."""

    from lib import pdx_deform

    loaded = pdx_deform.load_mesh(mesh)
    visible = ~loaded.collision if len(loaded.collision) else slice(None)
    return float((loaded.positions[visible].max(axis=0) - loaded.positions[visible].min(axis=0)).max())


def game_review(folder: Path, kind: str, out: Path, game: Path) -> Path:
    contract = sk.kind_contract(kind)
    mesh = sorted(folder.glob("*.mesh"))[0]
    # the vanilla model nearest the kind's median size, at its own entity scale; the model at the reference entity's
    nearest = contract["size"]["nearest"]
    if kind == "landmark" and contract["size"].get("nearest_tall") and sk.tall_and_thin(_points(mesh)):
        nearest = contract["size"]["nearest_tall"]  # an obelisk is compared with a vanilla tower, not a palace
    reference = game / nearest["rel"]
    rows = []
    for label, path, texts in (("this model", mesh, []), (f"vanilla {reference.stem}", reference, review_unit.gfx_texts(game))):
        scale = contract["entity"]["scale"] if path == mesh else nearest["scale"]
        # a plane flies: its game-size tiles have no ground disc, so its drawn wingspan can be measured
        index = render_rest(path, out / "game_tiles" / ("model" if path == mesh else "vanilla"), texts, ground_alpha=0.0 if kind == "plane" else 1.0)
        names = index["clips"][0]["rows"][0]["tiles"]
        folder_tiles = out / "game_tiles" / ("model" if path == mesh else "vanilla")
        if kind == "plane":
            # a plane is compared by its wingspan: the front view's drawn width is set to the runtime wingspan, so
            # whatever else the renderer frames (a long fuselage, a locator) does not change the comparison
            left, right = model_columns(Image.open(folder_tiles / names["front"]))
            factor = sk.main_measure(_points(path), kind) * scale * PX_PER_METRE / max(right - left, 1)
        else:
            # the tile shows span x SHARE across RENDER_SIZE px; at game size it shows span x scale x PX_PER_METRE
            factor = scale * PX_PER_METRE * _span(path) * SHARE / RENDER_SIZE
        small = max(4, round(RENDER_SIZE * factor))
        tiles = [Image.open(folder_tiles / names[view]).convert("RGB").resize((small, small), Image.Resampling.LANCZOS) for view in ("hoi4", "front")]
        rows.append((label, tiles))
    font = ImageFont.load_default()
    cell = max(max(t.width for _l, ts in rows for t in ts), 90) + 8
    height = max(t.height for _l, ts in rows for t in ts) + 34
    image = Image.new("RGB", (cell * 2 + 8, height * len(rows)), (30, 30, 30))
    draw = ImageDraw.Draw(image)
    for r, (label, tiles) in enumerate(rows):
        draw.text((4, r * height + 2), label, fill=(255, 220, 120), font=font)
        for c, (tile, view) in enumerate(zip(tiles, ("hoi4", "front"))):
            image.paste(tile, (c * cell + 4, r * height + 16))
            draw.text((c * cell + 4, r * height + 18 + tile.height), view, fill=(255, 255, 255), font=font)
    target = out / "sheets" / "game_size.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    image.resize((image.width * 3, image.height * 3), Image.Resampling.NEAREST).save(out / "sheets" / "game_size_x3.png")
    return target


def add_game_sheet(out: Path) -> None:
    request = out / "REVIEW_REQUEST.md"
    if not request.is_file():
        return
    text = request.read_text(encoding="utf-8")
    marker = "Single tiles, if a sheet"
    closeup = out / "sheets" / "rest_closeup.png"
    extra = (f"Close-up of the rest pose (the same model, larger): `{closeup.resolve()}`.\n\n" if closeup.is_file() else "") + ("Game-size sheet (the model above, the vanilla model of the same kind below, both at the size the map shows them. "
             f"`game_size_x3.png` is the same sheet enlarged three times.): `{(out / 'sheets' / 'game_size.png').resolve()}` and "
             f"`{(out / 'sheets' / 'game_size_x3.png').resolve()}`. Judge on it whether the model reads as what it is at game size "
             "and is about as large as the vanilla one.\n\n")
    if "Game-size sheet" not in text and marker in text:
        request.write_text(text.replace(marker, extra + marker, 1), encoding="utf-8", newline="\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("folder", type=Path, help="the model's folder (its .mesh, .anim and .dds files)")
    parser.add_argument("--model-kind", required=True, choices=sk.KINDS)
    parser.add_argument("--out", type=Path, required=True, help="the review folder (outside gfx/)")
    parser.add_argument("--only", choices=("close", "game"), help="one Blender start: the close-up review or the game-size sheet")
    parser.add_argument("--note", action="append", default=[], help="a fixed note added to the kind's own (repeatable)")
    parser.add_argument("--game", type=Path, help="the game folder (default: the one .tools/lib/game.py finds)")
    heavy_job.add_argument(parser)
    args = parser.parse_args(argv)
    heavy_job.apply(args)
    folder, out = args.folder.resolve(), args.out.resolve()
    if args.only in (None, "close"):
        close_review(folder, args.model_kind, out, args.note)
    if args.only in (None, "game"):
        from tripo.static_model import game_dir

        print(game_review(folder, args.model_kind, out, args.game or game_dir()))
    add_game_sheet(out)
    print(out / "REVIEW_REQUEST.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
