"""Measure the surface and deformation of vanilla HOI4 units, to set the unit checks' limits.

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/calibrate_deformation.py "<HOI4 install>" --out .tools/3d_pipeline/config/deformation_calibration.json

It reads every skinned `.mesh` under `gfx/models/units`, pairs it with the `.anim` files the game
plays on it (the `pdxmesh` animation ids in `gfx/**/*.gfx`, resolved through the `animation`
blocks of `gfx/**/*.asset`), skins every frame with `lib/pdx_deform.py`, and writes the largest
value of each measure per group. `check_unit_files.py` uses those values as its limits,
so a custom unit may deform as much as the worst vanilla unit of its group and no more.

Groups: `organic` is soldiers, riders, mounts and animals (matched by `ORGANIC` on the file
name, where each word must start the name or follow `_`), `vehicle` is everything else (tanks, guns, trucks, headquarters). Vehicles keep open,
hidden backs on their panels, so their open-edge counts are far higher than a soldier's and must
not set a soldier's limit. Rerun after a game update. Text animations (`@@t@`) are skipped and
counted.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Dict, List

PIPELINE = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE))

from lib import pdx_deform
from lib.pdx_binary import PdxFormatError

# Planes, missiles and ships fly, roll and sink by design; they must not set a land vehicle's limits.
AIR_NAVAL = {"planes", "ships"}
# Frames that only carry locators (cavalry_frame.mesh is one triangle) are not a surface.
MIN_TRIANGLES = 200
ORGANIC = re.compile(r"(^|_)(infantry|marine|mountain|paratroop|cavalry|horse|camel|deer|elephant|soldier|rider|officer|commando|ranger|militia|guard)", re.I)
MEASURES = (
    "largest_open_loop",
    "open_edge_share",
    "winding_flips",
    "inside_out_triangles",
    "bridge_edges",
    "stretched_share",
    "squashed_share",
    "worst_stretch_share",
    "sink",
    "death_sink",
    "hover",
)


def group_of(relative_path: str) -> str:
    if ORGANIC.search(Path(relative_path).name):
        return "organic"
    return "air_naval" if relative_path.split("/")[0] in AIR_NAVAL else "vehicle"


def registered_clips(game: Path) -> Dict[Path, List[Path]]:
    """Mesh file -> the `.anim` files the game plays on it."""

    anim_files: Dict[str, Path] = {}
    for asset in (game / "gfx").rglob("*.asset"):
        text = asset.read_text(encoding="utf-8-sig", errors="replace")
        for block in re.finditer(r"animation\s*=\s*\{([^{}]*)\}", text):
            name = re.search(r'name\s*=\s*"([^"]+)"', block.group(1))
            file = re.search(r'file\s*=\s*"([^"]+)"', block.group(1))
            if name and file:
                relative = file.group(1).replace("\\", "/")
                anim_files[name.group(1).lower()] = game / relative if relative.lower().startswith("gfx/") else asset.parent / relative
    clips: Dict[Path, List[Path]] = {}
    for gfx in (game / "gfx").rglob("*.gfx"):
        text = gfx.read_text(encoding="utf-8-sig", errors="replace")
        for block in re.finditer(r"pdxmesh\s*=\s*\{(.*?)\n\t\}", text, re.S):
            file = re.search(r'file\s*=\s*"([^"]+)"', block.group(1))
            if not file:
                continue
            mesh = (game / file.group(1).replace("\\", "/")).resolve()
            for kind in re.findall(r'type\s*=\s*"([^"]+)"', block.group(1)):
                anim = anim_files.get(kind.lower())
                if anim is not None and anim.exists():
                    clips.setdefault(mesh, [])
                    if anim.resolve() not in clips[mesh]:
                        clips[mesh].append(anim.resolve())
    return clips


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("game", type=Path, help="the game's install folder")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--clips-per-mesh", type=int, default=6)
    parser.add_argument("--seed", type=int, default=1936)
    args = parser.parse_args()

    root = args.game / "gfx" / "models" / "units"
    registered = registered_clips(args.game)
    text_anims = 0
    rng = random.Random(args.seed)
    groups = {name: {measure: {"value": 0.0, "mesh": "", "clip": ""} for measure in MEASURES} for name in ("organic", "vehicle", "air_naval")}
    measured = {name: {"meshes": 0, "clips": 0} for name in groups}

    def record(group: str, measure: str, value: float, mesh: str, clip: str = "") -> None:
        if value > groups[group][measure]["value"]:
            groups[group][measure] = {"value": round(float(value), 6), "mesh": mesh, "clip": clip}

    for mesh_path in sorted(root.rglob("*.mesh")):
        try:
            mesh = pdx_deform.load_mesh(mesh_path)
        except (PdxFormatError, ValueError, IndexError, OSError):
            continue
        if not mesh.skinned or len(mesh.triangles) < MIN_TRIANGLES:
            continue
        clips = registered.get(mesh_path.resolve(), [])
        if not clips:
            continue
        rel = mesh_path.relative_to(root).as_posix()
        group = group_of(rel)
        measured[group]["meshes"] += 1
        surface = pdx_deform.surface_report(mesh)
        edges = max(len(pdx_deform.mesh_edges(mesh)), 1)
        static = {
            "largest_open_loop": surface.largest_open_loop,
            "open_edge_share": surface.open_edges / edges,
            "winding_flips": surface.winding_flips,
            "inside_out_triangles": sum(surface.inside_out_parts),
            "bridge_edges": pdx_deform.bridge_edges(mesh).edges,
        }
        for measure, value in static.items():
            record(group, measure, value, rel)
        print(f"[{group}] {rel}: " + ", ".join(f"{k} {v:.4g}" for k, v in static.items()), flush=True)
        for clip in rng.sample(clips, min(args.clips_per_mesh, len(clips))):
            try:
                report = pdx_deform.deformation_report(mesh, pdx_deform.load_anim(clip))
            except PdxFormatError:
                text_anims += 1  # a text (@@t@) animation; the binary reader skips it
                continue
            except (ValueError, IndexError):
                continue
            measured[group]["clips"] += 1
            # A rider clip plays on a body attached to a mount's Saddle_Node, so its feet never meet the ground.
            seated = "rider" in clip.stem.lower()
            death = "death" in clip.stem.lower()
            values = {
                "stretched_share": report.stretched_edges / edges,
                "squashed_share": report.squashed_edges / edges,
                "worst_stretch_share": report.worst_stretch_share,
                "sink": 0.0 if seated or death else -report.lowest,
                "death_sink": -report.lowest if death and not seated else 0.0,
                "hover": 0.0 if seated or death else report.highest_lowest,
            }
            for measure, value in values.items():
                record(group, measure, value, rel, clip.relative_to(args.game.resolve()).as_posix())
            print(f"    {clip.name}: " + ", ".join(f"{k} {v:.4f}" for k, v in values.items()), flush=True)
    payload = {
        "_about": "Largest surface and deformation measures over vanilla skinned units, per group, from calibrate_deformation.py. check_unit_files.py uses them as limits.",
        "game_folder": "gfx/models/units",
        "settings": {
            "stretch_ratio": pdx_deform.STRETCH_RATIO,
            "significant_share": pdx_deform.SIGNIFICANT_SHARE,
            "bridge_hops": pdx_deform.BRIDGE_HOPS,
            "organic_pattern": ORGANIC.pattern,
            "clips_per_mesh": args.clips_per_mesh,
            "seed": args.seed,
            "text_anims_skipped": text_anims,
        },
        "measured": measured,
        "groups": groups,
    }
    args.out.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(groups, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
