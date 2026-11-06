"""Fit a held prop (a weapon, a tool, a staff) to an exported unit and bind it to the hand, for free in Blender.

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/fit_prop.py gfx/models/units/<unit> --prop <prop job>/provider/downloads/generation_model.glb \\
        --bone RightHand --length 0.55 --grip 0.15 --butt high --out <job folder>/props

The unit folder is copied to `<out>/files`. The prop's maps (`base_color.png`, `metallic.png` and
`roughness.png`, `normal.png`, from `--textures`, by default the GLB's `<stem>_textures` folder) are
copied to `<out>/prop_textures`, packed the way the unit route packs a unit's maps, and written as
`<prop>_{diffuse,specular,normal}.dds` next to the unit. Blender then (`blender/fit_prop.py`):

- closes the prop (the source's longest piece, welded, capped) and scales it to `--length` of the
  unit's height;
- puts its grip, `--grip` of its length from the butt, in the palm of `--bone`;
- tries 42 directions in the hand bone's frame over every `--step`-th frame of every clip, and keeps
  the one whose far end least often goes inside the body or below the ground;
- binds the prop rigidly to the hand as its own shape and exports the mesh again. The clips are not
  touched.

The verdict passes when the best direction never goes below the ground and goes inside the body in
at most 2 % of its sampled points, and names the check and the review to run next. Otherwise it
escalates: try another `--grip`, `--butt` or `--bone`, or seat the prop live (the skill's
references/live-authoring.md, "Props in hand"). A two-handed hold always needs the live step for
the second hand. Nothing under `gfx/` changes and nothing is paid.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

PIPELINE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import stage_verdict
from lib.model_dds import write_dxt5
from pack_pdx_material import ensure_gltf_metallic_roughness_map, pack_pdx_normal_map, pack_pdx_specular_map
from review_unit import find_blender, owned_anims

BLENDER_SCRIPT = PIPELINE_ROOT / "blender" / "fit_prop.py"
MAPS = ("base_color.png", "metallic.png", "roughness.png", "normal.png")
# The best grip may still graze the body: a finger or a sleeve. More than this share of the far end's
# sampled points inside the body is a prop passing through it.
INSIDE_SHARE = 0.02


def find_textures(prop: Path, textures: Optional[Path]) -> Path:
    candidates = [textures] if textures else [prop.with_name(prop.stem + "_textures"), prop.parent / "geometry_textures"]
    for folder in candidates:
        if folder and folder.is_dir() and (folder / "base_color.png").is_file():
            return folder
    raise SystemExit(f"No prop maps found (looked in {', '.join(str(c) for c in candidates if c)}); pass --textures <folder with base_color.png>")


def pack_textures(source: Path, work: Path, files: Path, prop_stem: str, size: int, gamma: float) -> Dict[str, dict]:
    """Copy the prop's maps to `work`, pack them like a unit's, and write the three DDS files into `files`."""

    from PIL import Image

    maps = work / "prop_textures"
    maps.mkdir(parents=True, exist_ok=True)
    for name in MAPS:
        if (source / name).is_file():
            shutil.copy2(source / name, maps / name)
    ensure_gltf_metallic_roughness_map(work, "prop_textures/metallic_roughness.png")
    pack_pdx_specular_map(work, "prop_textures/metallic_roughness.png")
    pack_pdx_normal_map(work, "prop_textures/normal.png")
    sources = {"diffuse": maps / "base_color.png", "specular": maps / "pdx_specular.png", "normal": maps / "pdx_normal.png"}
    written = {}
    for role, path in sources.items():
        if not path.is_file():
            raise SystemExit(f"The prop's {role} map was not produced from {source}")
        with Image.open(path) as image:
            image = image.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
            if role == "diffuse" and gamma != 1.0:
                table = [round(255 * (i / 255) ** gamma) for i in range(256)]
                red, green, blue, alpha = image.split()
                image = Image.merge("RGBA", (red.point(table), green.point(table), blue.point(table), alpha))
            staged = maps / f"{prop_stem}_{role}.png"
            image.save(staged)
        header = write_dxt5(staged, files / f"{prop_stem}_{role}.dds")
        written[role] = {key: header[key] for key in ("format", "width", "height") if key in header}
    return written


def fit(args: argparse.Namespace) -> dict:
    folder = args.folder.resolve()
    meshes = sorted(folder.glob("*.mesh"))
    mesh = next((m for m in meshes if m.stem == args.stem), meshes[0] if meshes else None)
    if mesh is None:
        raise SystemExit(f"no .mesh in {folder}")
    out = args.out.resolve()
    files = out / "files"
    if files.exists():
        shutil.rmtree(files)
    shutil.copytree(folder, files, ignore=shutil.ignore_patterns("review", "*.blend*"))
    prop_stem = args.prop_stem or f"{mesh.stem}_prop"
    textures = pack_textures(find_textures(args.prop.resolve(), args.textures), out, files, prop_stem, args.size, args.gamma)
    anims = [str(path) for path in owned_anims(files, mesh.stem, [m.stem for m in meshes])]
    request = {
        "mesh": str(files / mesh.name),
        "anims": anims,
        "prop": str(args.prop.resolve()),
        "prop_stem": prop_stem,
        "bone": args.bone,
        "length": args.length,
        "grip": args.grip,
        "butt": args.butt,
        "step": args.step,
        "ground_weight": args.ground_weight,
        "out": str(files / mesh.name),
        "report": str(out / "fit_report.json"),
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "fit_request.json").write_text(json.dumps(request, indent=1), encoding="utf-8", newline="\n")
    completed = subprocess.run(
        [str(find_blender()), "-b", "--python", str(BLENDER_SCRIPT), "--", str(out / "fit_request.json")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    (out / "blender.log").write_text(completed.stdout[-20000:] + completed.stderr[-20000:], encoding="utf-8")
    if "PROP_FITTED" not in completed.stdout:
        raise SystemExit(f"Blender did not fit the prop; see {out / 'blender.log'}")
    report = json.loads((out / "fit_report.json").read_text(encoding="utf-8"))
    report["textures"] = textures
    report["unit"] = mesh.stem
    report["prop_stem"] = prop_stem
    return report


def verdict_for(report: dict, args: argparse.Namespace) -> dict:
    best = report["best"]
    sampled = max(report["frames_checked"] * report["samples_per_frame"], 1)
    inside_share = best["inside"] / sampled
    ok = best["under"] == 0 and inside_share <= INSIDE_SHARE
    files = (args.out / "files").as_posix()
    outputs = {
        "files": files,
        "report": (args.out / "fit_report.json").as_posix(),
        "prop": report["prop_stem"],
        "inside_share": round(inside_share, 4),
        "under_ground_points": best["under"],
        "clips_with_clipping": best["per_clip"],
        "textures": report["textures"],
    }
    if ok:
        steps = [
            f"{stage_verdict.PY} {stage_verdict.PIPELINE}/check_unit_files.py {stage_verdict.quote(files)} --verdict {stage_verdict.quote(args.out.as_posix() + '/check.json')}",
            f"Add a meshsettings block for the {report['prop_stem']} shape (its three DDS files are next to the mesh), then render with review_unit.py and ask a fresh reviewer.",
        ]
        return stage_verdict.verdict("props", True, report["unit"], outputs=outputs, next_steps=steps)
    escalate = {
        "rules": ["PROP-CLIPS"],
        "why": [f"the best of 42 grips still goes inside the body in {inside_share:.1%} of its sampled points and below the ground in {best['under']}"],
        "how": f"Try another --grip, --butt or --bone; if no grip clears the clips, seat the prop live ({stage_verdict.LIVE_GUIDE}, Props in hand).",
    }
    return stage_verdict.verdict("props", False, report["unit"], outputs=outputs, escalate=escalate,
                                 findings=[{"rule": "PROP-CLIPS", "file": report["prop_stem"], "message": escalate["why"][0]}])


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", type=Path, help="the exported unit folder (.mesh, .anim, .dds)")
    parser.add_argument("--prop", type=Path, required=True, help="the prop's provider .glb (a sheet of several props keeps the tallest)")
    parser.add_argument("--textures", type=Path, help="folder with base_color.png, metallic.png, roughness.png and normal.png (default: next to the GLB)")
    parser.add_argument("--out", type=Path, required=True, help="work folder for the fitted copy and the report (outside gfx/)")
    parser.add_argument("--stem", help="the unit mesh's stem, in a folder shared with another unit")
    parser.add_argument("--prop-stem", help="name of the prop's shape and DDS files (default: <unit>_prop)")
    parser.add_argument("--bone", default="RightHand", help="the hand bone that holds the prop")
    parser.add_argument("--length", type=float, default=0.55, help="the prop's length as a share of the unit's height")
    parser.add_argument("--grip", type=float, default=0.15, help="where the hand holds it, as a share of its length from the butt")
    parser.add_argument("--butt", choices=("high", "low"), default="high", help="which end of the source model is the butt: the higher or the lower")
    parser.add_argument("--step", type=int, default=3, help="score every n-th frame of each clip")
    parser.add_argument("--ground-weight", type=float, default=10.0, help="how much a point below the ground counts against a grip")
    parser.add_argument("--size", type=int, default=1024, help="prop texture size")
    parser.add_argument("--gamma", type=float, default=1.0, help="gamma on the prop's diffuse, to match the unit's (the job's runtime_diffuse_gamma)")
    args = parser.parse_args(argv)
    report = fit(args)
    payload = verdict_for(report, args)
    stage_verdict.write(payload, args.out / "verdict.json")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
