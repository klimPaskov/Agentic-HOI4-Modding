"""Render a unit's exported files for an independent visual review, and record the reviewer's verdict.

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/review_unit.py gfx/models/units/<unit> --mod-root . --out <job>/review
    py -3.13 -B .tools/3d_pipeline/review_unit.py gfx/models/units/<unit> --out <job>/review --record reviewer_reply.md

The first form imports the `.mesh` and every `.anim` of the unit into Blender with io_pdx_mesh,
renders each clip from six views (front, left, back, right, the HOI4 map camera, below) at
evenly spaced frames plus the clip's worst-stretch and worst-ground frames, and writes one
contact sheet per clip to `<out>/sheets/`. Back faces are culled as in the game and the
background is magenta, so holes show. It also writes `<out>/REVIEW_REQUEST.md`: the reviewer
prompt from `config/visual_review_prompt.md` with the sheet paths filled in.

Give that request, and only that request and the sheets, to a reviewer that has not seen how the
unit was made (a fresh subagent or a person). Save its whole reply and record it with the second
form. The unit passes only when the reply says `VERDICT: pass` and `DEFECTS: none`; anything else
records a fail with the reply kept next to the sheets. Put `<out>` in the job's evidence folder, never
under `gfx/`, or the renders ship with the mod.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

PIPELINE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import pdx_binary, pdx_deform

PROMPT = PIPELINE_ROOT / "config" / "visual_review_prompt.md"
BLENDER_SCRIPT = PIPELINE_ROOT / "blender" / "review_render.py"
VIEWS = ["front", "left", "back", "right", "hoi4", "below"]
LABEL_HEIGHT = 18


def owned_anims(folder: Path, stem: str, stems: List[str]) -> List[Path]:
    """The `.anim` files of `stem`, when a folder holds several units (a mount and its rider)."""

    owned = []
    for anim in sorted(folder.glob("*.anim")):
        owners = [candidate for candidate in stems if anim.stem.startswith(candidate + "_")]
        if owners and max(owners, key=len) == stem:
            owned.append(anim)
    return owned


def diffuse_maps(mesh_path: Path, gfx_texts: List[str]) -> Dict[str, str]:
    """Shape name -> diffuse texture path, from the `meshsettings` of the `.gfx` that registers the mesh.

    `"*"` holds a fallback: the folder's first `*diffuse*.dds`."""

    maps: Dict[str, str] = {}
    relative = mesh_path.as_posix()
    for text in gfx_texts:
        for block in re.finditer(r"pdxmesh\s*=\s*\{(.*?)\n\t\}", text, re.S):
            body = block.group(1)
            file_match = re.search(r'file\s*=\s*"([^"]+)"', body)
            if not file_match or not relative.lower().endswith(file_match.group(1).lower().lstrip("/")):
                continue
            for settings in re.finditer(r"meshsettings\s*=\s*\{(.*?)\}", body, re.S):
                name = re.search(r'name\s*=\s*"([^"]+)"', settings.group(1))
                texture = re.search(r'texture_diffuse\s*=\s*"([^"]+)"', settings.group(1))
                if name and texture and (mesh_path.parent / Path(texture.group(1)).name).exists():
                    maps[name.group(1)] = str(mesh_path.parent / Path(texture.group(1)).name)
    fallback = sorted(mesh_path.parent.glob(f"{mesh_path.stem}*diffuse*.dds")) or sorted(mesh_path.parent.glob("*diffuse*.dds"))
    if fallback:
        maps["*"] = str(fallback[0])
    return maps


def gfx_texts(mod_root: Optional[Path]) -> List[str]:
    if mod_root is None:
        return []
    texts = []
    for folder in ("gfx/entities", "interface", "gfx"):
        for path in sorted((mod_root / folder).glob("*.gfx")):
            try:
                texts.append(path.read_text(encoding="utf-8-sig", errors="replace"))
            except OSError:
                continue
    return texts


def pick_frames(mesh: pdx_deform.SkinnedMesh, anim_path: Path, count: int) -> List[int]:
    """Evenly spaced sample indices plus the worst-stretch frame and the lowest and highest frames."""

    anim = pdx_deform.load_anim(anim_path)
    last = max(anim.frames - 1, 0)
    frames = {round(last * k / max(count - 1, 1)) for k in range(count)}
    if mesh.skinned and anim.frames:
        report = pdx_deform.deformation_report(mesh, anim)
        frames.update((report.worst_frame, report.lowest_frame, report.highest_frame))
    return sorted(frame for frame in frames if 0 <= frame <= last)


def find_blender() -> Path:
    explicit = os.environ.get("BLENDER_EXE", "").strip()
    if explicit:
        return Path(explicit)
    import bootstrap_3d_workflow as bootstrap

    executable, _shortcut, _version = bootstrap.select_supported_blender(
        bootstrap.discover_blender_installs(), bootstrap.supported_blender_minors()
    )
    return executable


def build_sheets(render_dir: Path, sheet_dir: Path) -> List[Path]:
    """One sheet per clip: a row per frame, a column per view, each tile labelled."""

    from PIL import Image, ImageDraw

    index = json.loads((render_dir / "index.json").read_text(encoding="utf-8"))
    sheet_dir.mkdir(parents=True, exist_ok=True)
    sheets = []
    for clip in index["clips"]:
        rows = clip["rows"]
        views = list(rows[0]["tiles"])
        width, height = Image.open(render_dir / rows[0]["tiles"][views[0]]).size
        sheet = Image.new("RGB", (width * len(views), (height + LABEL_HEIGHT) * len(rows)), (30, 30, 30))
        draw = ImageDraw.Draw(sheet)
        for r, row in enumerate(rows):
            for c, view in enumerate(views):
                with Image.open(render_dir / row["tiles"][view]) as tile:
                    sheet.paste(tile.convert("RGB"), (c * width, r * (height + LABEL_HEIGHT) + LABEL_HEIGHT))
                draw.text((c * width + 4, r * (height + LABEL_HEIGHT) + 3), f"{clip['name']} f{row['frame']} {view}", fill=(230, 230, 230))
        path = sheet_dir / f"{clip['name']}.png"
        sheet.save(path)
        sheets.append(path)
    return sheets


def write_request(out: Path, unit: str, sheets: List[Path], tile_dir: Path) -> Path:
    prompt = PROMPT.read_text(encoding="utf-8")
    listing = "\n".join(f"- `{sheet.resolve()}`" for sheet in sheets)
    request = (
        f"{prompt.rstrip()}\n\n## This review\n\nUnit: `{unit}`\n\nSheets (open every one):\n\n{listing}\n\n"
        f"Single tiles, if a sheet is too small to judge a region: `{tile_dir.resolve()}` (`<clip>_<frame>_<view>.png`). "
        "Open nothing else.\n"
    )
    path = out / "REVIEW_REQUEST.md"
    path.write_text(request, encoding="utf-8", newline="\n")
    return path


def parse_verdict(reply: str) -> dict:
    """Read one unit's block of a reviewer reply. Pass needs `VERDICT: pass` and `DEFECTS: none`."""

    verdict = re.search(r"^\s*VERDICT:\s*(pass|fail)\b", reply, re.I | re.M)
    defects = re.findall(r"^\s*-\s*\[[^\]]*\].*$", reply, re.M)
    none = re.search(r"^\s*DEFECTS:\s*none\b", reply, re.I | re.M)
    passed = bool(verdict and verdict.group(1).lower() == "pass" and none and not defects)
    return {"verdict": "pass" if passed else "fail", "stated_verdict": verdict.group(1).lower() if verdict else None, "defects": len(defects)}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(out: Path, reply_path: Path) -> dict:
    reply = reply_path.read_text(encoding="utf-8")
    result = parse_verdict(reply)
    sheets = sorted((out / "sheets").glob("*.png"))
    if not sheets:
        raise SystemExit(f"no sheets in {out / 'sheets'}; render the unit first")
    (out / "review_reply.md").write_text(reply, encoding="utf-8", newline="\n")
    result.update(
        {
            "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "reply_sha256": sha256(out / "review_reply.md"),
            "sheets": {sheet.name: sha256(sheet) for sheet in sheets},
        }
    )
    (out / "verdict.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8", newline="\n")
    return result


def render(folder: Path, stem: Optional[str], out: Path, mod_root: Optional[Path], frames: int, size: int) -> List[Path]:
    meshes = sorted(folder.glob("*.mesh"))
    stems = [mesh.stem for mesh in meshes]
    mesh_path = next((mesh for mesh in meshes if mesh.stem == stem), meshes[0] if meshes else None)
    if mesh_path is None:
        raise SystemExit(f"no .mesh in {folder}")
    mesh = pdx_deform.load_mesh(mesh_path)
    clips = []
    for anim in owned_anims(folder, mesh_path.stem, stems):
        try:
            clips.append({"name": anim.stem, "path": str(anim.resolve()), "frames": pick_frames(mesh, anim, frames)})
        except (pdx_binary.PdxFormatError, ValueError, IndexError) as error:
            print(f"skipped {anim.name}: {error}")
    tile_dir = out / "tiles"
    request = {
        "out": str(tile_dir.resolve()),
        "mesh": str(mesh_path.resolve()),
        "diffuse": diffuse_maps(mesh_path.resolve(), gfx_texts(mod_root)),
        "clips": clips,
        "views": VIEWS,
        "size": size,
    }
    out.mkdir(parents=True, exist_ok=True)
    request_path = out / "render_request.json"
    request_path.write_text(json.dumps(request, indent=1), encoding="utf-8", newline="\n")
    completed = subprocess.run(
        [str(find_blender()), "-b", "--python", str(BLENDER_SCRIPT), "--", str(request_path.resolve())],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    (out / "blender.log").write_text(completed.stdout[-20000:] + completed.stderr[-20000:], encoding="utf-8")
    if "REVIEW_RENDERED" not in completed.stdout:
        raise SystemExit(f"Blender did not finish the renders; see {out / 'blender.log'}")
    sheets = build_sheets(tile_dir, out / "sheets")
    write_request(out, mesh_path.stem, sheets, tile_dir)
    return sheets


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", type=Path, help="the folder that holds the unit's .mesh and .anim files")
    parser.add_argument("--stem", help="review only <stem>.mesh and its animations (a mount and its rider share a folder)")
    parser.add_argument("--mod-root", type=Path, help="read the .gfx meshsettings for each shape's diffuse map")
    parser.add_argument("--out", type=Path, required=True, help="where the tiles, sheets, request and verdict go (outside gfx/)")
    parser.add_argument("--frames", type=int, default=5, help="evenly spaced frames per clip, before the worst frames are added")
    parser.add_argument("--size", type=int, default=384, help="tile size in pixels")
    parser.add_argument("--record", type=Path, help="record a reviewer's reply instead of rendering")
    args = parser.parse_args(argv)
    out = args.out
    if args.record:
        result = record(out, args.record)
        print(f"{result['verdict']}: {result['defects']} defect(s) recorded in {out / 'verdict.json'}")
        return 0 if result["verdict"] == "pass" else 1
    sheets = render(args.folder, args.stem, out, args.mod_root, args.frames, args.size)
    print(f"{len(sheets)} sheets in {out / 'sheets'}. Give {out / 'REVIEW_REQUEST.md'} to a fresh reviewer, then rerun with --record <reply>.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
