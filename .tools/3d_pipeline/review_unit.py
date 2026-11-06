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

Each clip also gets a diagnostics sheet (`<clip>_diagnostics.png`) at its worst-stretch, lowest and
highest frames, in flat colours that show what the checks measure: grey is fine, yellow to red is
surface stretched or squashed by 1.3 to 1.5 times or more, cyan is an open edge, blue is below the
ground, magenta is a hole or a back face. `--no-diagnostics` skips them. Both forms print a one-line
stage verdict and write it to `<out>/verdict_render.json` or `<out>/verdict.json`.

Review rounds (decision 3D-7). The bar stays at no defects, and rounds converge because every reviewer
gets the same request:

- `--note TEXT` (repeatable) or `--note-file FILE` adds fixed notes for the unit, the same every round,
  for example that a ragged, torn hem is the unit's intended look. Keep the file in the job folder.
- The reviewer goes through the quality bar item by item and ends the reply with a `CHECKLIST:` block,
  one line per item. A reply without every item is recorded as a fail. `--no-checklist` drops it.
- `--clips attack death` makes an intermediate round: only those clips and the rest pose are rendered
  and judged. Use it after changing some clips. A unit is accepted only after a full round, without
  `--clips`, by a new reviewer. The round is recorded in `<out>/review_scope.json` and in the verdict.

The camera angles are fixed (`VIEWS`), so every round shows the same views.
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

from lib import pdx_binary, pdx_deform, stage_verdict

PROMPT = PIPELINE_ROOT / "config" / "visual_review_prompt.md"
BLENDER_SCRIPT = PIPELINE_ROOT / "blender" / "review_render.py"
VIEWS = ["front", "left", "back", "right", "hoi4", "below"]
DIAGNOSTIC_VIEWS = ["front", "left", "hoi4"]
LABEL_HEIGHT = 18
LEGEND = "grey fine | yellow to red stretched or squashed 1.3x to 1.5x+ | cyan open edge | blue below ground | magenta hole or back face"


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


def diagnostic_frames(mesh: pdx_deform.SkinnedMesh, anim_path: Path) -> List[int]:
    """The frames the checks care most about: the worst stretch, the lowest point and the highest."""

    anim = pdx_deform.load_anim(anim_path)
    if not mesh.skinned or not anim.frames:
        return []
    report = pdx_deform.deformation_report(mesh, anim)
    return sorted({report.worst_frame, report.lowest_frame, report.highest_frame})


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
        if clip.get("diagnostic_rows"):
            sheets.append(build_diagnostic_sheet(render_dir, sheet_dir, clip))
    return sheets


def build_diagnostic_sheet(render_dir: Path, sheet_dir: Path, clip: dict) -> Path:
    """The clip's diagnostic tiles with a legend line on top."""

    from PIL import Image, ImageDraw

    rows = clip["diagnostic_rows"]
    views = list(rows[0]["tiles"])
    width, height = Image.open(render_dir / rows[0]["tiles"][views[0]]).size
    top = LABEL_HEIGHT
    sheet = Image.new("RGB", (max(width * len(views), 8 * len(LEGEND)), top + (height + LABEL_HEIGHT) * len(rows)), (30, 30, 30))
    draw = ImageDraw.Draw(sheet)
    draw.text((4, 3), LEGEND, fill=(230, 230, 230))
    for r, row in enumerate(rows):
        y = top + r * (height + LABEL_HEIGHT)
        for c, view in enumerate(views):
            with Image.open(render_dir / row["tiles"][view]) as tile:
                sheet.paste(tile.convert("RGB"), (c * width, y + LABEL_HEIGHT))
            draw.text((c * width + 4, y + 3), f"{clip['name']} f{row['frame']} {view} diagnostics (worst edge change {row['worst_share']:.1%} of height)", fill=(230, 230, 230))
    path = sheet_dir / f"{clip['name']}_diagnostics.png"
    sheet.save(path)
    return path


CHECKLIST_ITEMS = 7  # the quality bar's items in config/visual_review_prompt.md
SCOPE_FILE = "review_scope.json"


def select_clips(anims: List[Path], stem: str, wanted: Optional[List[str]]) -> List[Path]:
    """The `.anim` files named by role (`attack`) or by file stem (`<unit>_attack`); all when `wanted` is empty."""

    if not wanted:
        return anims
    names = {name.lower() for name in wanted}
    chosen = [anim for anim in anims if anim.stem.lower() in names or anim.stem[len(stem) + 1 :].lower() in names]
    found = {anim.stem.lower() for anim in chosen} | {anim.stem[len(stem) + 1 :].lower() for anim in chosen}
    missing = sorted(names - found)
    if missing:
        raise SystemExit(f"no clip of {stem} is named {', '.join(missing)}; its clips are {', '.join(anim.stem for anim in anims)}")
    return chosen


def scope_text(notes: List[str], checklist: bool, clips: Optional[List[str]]) -> str:
    """The fixed part of the request that 3D-7 adds: notes, the checklist and the round's scope."""

    parts = []
    if notes:
        lines = "\n".join(f"- {note.strip()}" for note in notes if note.strip())
        parts.append(
            "## Fixed notes for this unit (the same every round)\n\n"
            f"{lines}\n\n"
            "These notes describe the unit's intended design. Judge everything they do not name as usual, including any hole in the body."
        )
    if checklist:
        items = "\n".join(f"{number}: ok | defects" for number in range(1, CHECKLIST_ITEMS + 1))
        parts.append(
            "## Checklist\n\n"
            f"Go through the quality bar item by item, 1 to {CHECKLIST_ITEMS}, for every sheet you open. After the DEFECTS list, "
            "end your reply with this block, one line per item: `ok` when you found nothing of that kind, `defects` when you listed some.\n\n"
            f"```\nCHECKLIST:\n{items}\n```"
        )
    if clips:
        parts.append(
            "## This round\n\n"
            f"This is an intermediate round. The sheets below are the rest pose and only these clips: {', '.join(clips)}. "
            "Judge only them. The other clips are judged again in a later full round."
        )
    else:
        parts.append("## This round\n\nThis is a full review. Open every sheet below.")
    return "\n\n".join(parts)


def write_request(
    out: Path,
    unit: str,
    sheets: List[Path],
    tile_dir: Path,
    notes: Optional[List[str]] = None,
    checklist: bool = True,
    clips: Optional[List[str]] = None,
) -> Path:
    prompt = PROMPT.read_text(encoding="utf-8")
    listing = "\n".join(f"- `{sheet.resolve()}`" for sheet in sheets if not sheet.stem.endswith("_diagnostics"))
    diagnostics = "\n".join(f"- `{sheet.resolve()}`" for sheet in sheets if sheet.stem.endswith("_diagnostics"))
    if diagnostics:
        listing += f"\n\nDiagnostic sheets (flat colours; {LEGEND}):\n\n{diagnostics}"
    request = (
        f"{prompt.rstrip()}\n\n{scope_text(notes or [], checklist, clips)}\n\n## This review\n\nUnit: `{unit}`\n\nSheets (open every one):\n\n{listing}\n\n"
        f"Single tiles, if a sheet is too small to judge a region: `{tile_dir.resolve()}` (`<clip>_<frame>_<view>.png`). "
        "Open nothing else.\n"
    )
    path = out / "REVIEW_REQUEST.md"
    path.write_text(request, encoding="utf-8", newline="\n")
    scope = {"round": "intermediate" if clips else "full", "clips": list(clips or []), "checklist": bool(checklist), "notes": list(notes or [])}
    (out / SCOPE_FILE).write_text(json.dumps(scope, indent=1) + "\n", encoding="utf-8", newline="\n")
    return path


def parse_verdict(reply: str, checklist: bool = False) -> dict:
    """Read one unit's block of a reviewer reply. Pass needs `VERDICT: pass` and `DEFECTS: none`.

    With `checklist`, the reply must also answer every quality-bar item in a `CHECKLIST:` block.
    """

    verdict = re.search(r"^\s*VERDICT:\s*(pass|fail)\b", reply, re.I | re.M)
    defects = re.findall(r"^\s*-\s*\[[^\]]*\].*$", reply, re.M)
    none = re.search(r"^\s*DEFECTS:\s*none\b", reply, re.I | re.M)
    passed = bool(verdict and verdict.group(1).lower() == "pass" and none and not defects)
    result = {"verdict": "pass" if passed else "fail", "stated_verdict": verdict.group(1).lower() if verdict else None, "defects": len(defects)}
    if checklist:
        block = reply[reply.upper().rfind("CHECKLIST:"):] if "CHECKLIST:" in reply.upper() else ""
        answers = {int(number): answer.lower() for number, answer in re.findall(r"^\s*([1-9])\s*[:.]\s*(ok|defects?)\b", block, re.I | re.M)}
        missing = [number for number in range(1, CHECKLIST_ITEMS + 1) if number not in answers]
        result["checklist"] = {str(number): answers[number] for number in sorted(answers)}
        if missing:
            result["checklist_missing"] = missing
            result["verdict"] = "fail"
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_scope(out: Path) -> dict:
    try:
        return json.loads((out / SCOPE_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"round": "full", "clips": [], "checklist": False, "notes": []}


def record(out: Path, reply_path: Path) -> dict:
    reply = reply_path.read_text(encoding="utf-8")
    scope = read_scope(out)
    result = parse_verdict(reply, bool(scope.get("checklist")))
    result.update({"round": scope.get("round", "full"), "clips": scope.get("clips", [])})
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


def render(
    folder: Path,
    stem: Optional[str],
    out: Path,
    mod_root: Optional[Path],
    frames: int,
    size: int,
    diagnostics: bool = True,
    notes: Optional[List[str]] = None,
    checklist: bool = True,
    only: Optional[List[str]] = None,
) -> List[Path]:
    meshes = sorted(folder.glob("*.mesh"))
    stems = [mesh.stem for mesh in meshes]
    mesh_path = next((mesh for mesh in meshes if mesh.stem == stem), meshes[0] if meshes else None)
    if mesh_path is None:
        raise SystemExit(f"no .mesh in {folder}")
    mesh = pdx_deform.load_mesh(mesh_path)
    clips = []
    for anim in select_clips(owned_anims(folder, mesh_path.stem, stems), mesh_path.stem, only):
        try:
            entry = {"name": anim.stem, "path": str(anim.resolve()), "frames": pick_frames(mesh, anim, frames)}
            if diagnostics:
                entry["diagnostic_frames"] = diagnostic_frames(mesh, anim)
            clips.append(entry)
        except (pdx_binary.PdxFormatError, ValueError, IndexError) as error:
            print(f"skipped {anim.name}: {error}")
    tile_dir = out / "tiles"
    request = {
        "out": str(tile_dir.resolve()),
        "mesh": str(mesh_path.resolve()),
        "diffuse": diffuse_maps(mesh_path.resolve(), gfx_texts(mod_root)),
        "clips": clips,
        "views": VIEWS,
        "diagnostic_views": DIAGNOSTIC_VIEWS if diagnostics else [],
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
    write_request(out, mesh_path.stem, sheets, tile_dir, notes, checklist, only)
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
    parser.add_argument("--no-diagnostics", action="store_true", help="skip the flat-colour diagnostics sheets")
    parser.add_argument("--note", action="append", default=[], help="a fixed note for the reviewer, the same every round, such as a torn hem that is the intended look (repeatable)")
    parser.add_argument("--note-file", type=Path, help="a file of fixed notes, one per line (keep it in the job folder so every round uses it)")
    parser.add_argument("--checklist", action=argparse.BooleanOptionalAction, default=True, help="ask for the quality bar item by item and fail a reply without it (default on)")
    parser.add_argument("--clips", nargs="+", metavar="CLIP", help="an intermediate round: render and judge only these clips (roles or file stems) and the rest pose")
    args = parser.parse_args(argv)
    out = args.out
    unit = args.stem or next((mesh.stem for mesh in sorted(args.folder.glob("*.mesh"))), args.folder.name)
    if args.record:
        result = record(out, args.record)
        passed = result["verdict"] == "pass"
        if passed and result["round"] == "intermediate":
            steps = [
                f"The changed clips pass. Before acceptance, run a full round with a new reviewer: {stage_verdict.PY} {stage_verdict.PIPELINE}/review_unit.py "
                f"{stage_verdict.quote(args.folder.as_posix())} --out <a new review folder> (no --clips, the same notes)"
            ]
        elif passed:
            steps = []
        elif result.get("checklist_missing"):
            steps = [f"The reply does not answer checklist item(s) {', '.join(map(str, result['checklist_missing']))}: ask a new reviewer with the same request."]
        else:
            steps = ["Fix every listed defect at its cause, export again, then render the changed clips (--clips) and ask a new reviewer."]
        stage_verdict.write(
            stage_verdict.verdict(
                "review", passed, unit,
                outputs={"verdict": str(out / "verdict.json"), "reply": str(out / "review_reply.md"), "round": result["round"], "clips": result["clips"]},
                findings=[{"rule": "REVIEW-DEFECT", "file": "review_reply.md", "message": f"{result['defects']} defect(s) listed by the reviewer"}] if not passed else [],
                next_steps=steps,
            ),
            None,
        )
        return 0 if passed else 1
    notes = list(args.note)
    if args.note_file:
        notes += [line.strip().lstrip("-").strip() for line in args.note_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    sheets = render(args.folder, args.stem, out, args.mod_root, args.frames, args.size, not args.no_diagnostics, notes, args.checklist, args.clips)
    request = out / "REVIEW_REQUEST.md"
    stage_verdict.write(
        stage_verdict.verdict(
            "render", True, unit,
            outputs={"sheets": str(out / "sheets"), "tiles": str(out / "tiles")},
            sheets=[str(sheet) for sheet in sheets],
            checklist=str(request),
            next_steps=[
                f"Give {request} and the sheets, and nothing else, to a reviewer with a fresh context.",
                f"{stage_verdict.PY} {stage_verdict.PIPELINE}/review_unit.py {stage_verdict.quote(args.folder.as_posix())} --out {stage_verdict.quote(out.as_posix())} --record <reply.md>",
            ],
        ),
        out / "verdict_render.json",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
