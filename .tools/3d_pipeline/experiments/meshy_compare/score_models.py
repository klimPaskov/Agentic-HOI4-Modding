"""Score models with one harness: measure in Blender, then judge with the kit's own candidate_gate.

Free: no provider call, no key needed. Blender runs in background mode (score_model.py).

  # the baseline from the finished zin_men_infantry job (read-only), into a scratch folder
  py -3.13 -B experiments/meshy_compare/score_models.py --out-dir <dir> --zin-baseline <zin job root>

  # later, runs A and B (and the rig of B) from their job folders
  py -3.13 -B experiments/meshy_compare/score_models.py --out-dir <dir> \
      --item A_generation=<job A>/provider/downloads/generation_model.glb \
      --item B_generation=<job B>/provider/downloads/generation_model.glb \
      --item C_rigged=<job B>/provider/downloads/rigged_provider_model.glb --profile humanoid_unit

--item LABEL=PATH can be repeated; a .glb, .fbx, .blend or PDX .mesh path works. Add
--texture-dir LABEL=DIR for the DDS files that belong to a .mesh and --exclude NAME for provider
objects the job excludes (the zin generation GLB carries an `Icosphere`).

The verdict for each model is the real run_pilot.candidate_gate called with the profile's
validation limits, so the harness and the pipeline cannot drift apart. A raw provider download is
not what the pipeline gates (it gates the Blender-prepared candidate), so the raw rows are
calibration data about the limits, not predictions of a gate failure on the run.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPELINE_ROOT = HERE.parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

BLENDER = Path(os.environ.get("BLENDER_EXE", "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"))
PDX_ROOT = Path(os.environ.get("APPDATA", "")) / "Blender Foundation/Blender/5.1/extensions/user_default/io_pdx_mesh"
ADAPTER = PIPELINE_ROOT / "adapter"


def zin_items(root: Path) -> list:
    downloads = root / "provider" / "downloads"
    return [
        {"label": "baseline_generation_glb", "model": downloads / "generation_model.glb", "exclude": ["Icosphere"]},
        {"label": "baseline_remesh_glb", "model": downloads / "remesh_model.glb", "exclude": ["Icosphere"]},
        {"label": "baseline_final_export_mesh", "model": root / "export" / "mesh" / "zin_men_infantry.mesh", "exclude": [],
         "texture_dir": root / "export" / "mesh"},
    ]


def recorded_item(label: str, gate_json: Path, profile_name: str, out_dir: Path) -> dict:
    """Judge a geometry block an earlier run recorded (nothing is measured, nothing is rendered)."""

    record = json.loads(gate_json.read_text(encoding="utf-8"))
    geometry = record["geometry"]
    result = {"label": label, "geometry": geometry, "materials": {}}
    return {
        "label": label,
        "ok": True,
        "recorded": True,
        "source": str(gate_json),
        "recorded_status_at_the_time": record.get("status"),
        "geometry": geometry,
        "gate": judge(result, profile_name, out_dir),
    }


def run_blender(item: dict, out_dir: Path, resolution: int, previews: bool) -> dict:
    raw = out_dir / "raw" / f"{item['label']}.json"
    raw.parent.mkdir(parents=True, exist_ok=True)
    if raw.exists():
        raw.unlink()
    command = [
        str(BLENDER), "-b", "--factory-startup", "--python", str(HERE / "score_model.py"), "--",
        "--model", str(item["model"]), "--label", item["label"], "--out", str(raw),
        "--adapter", str(ADAPTER), "--previews", str(out_dir / "previews" / item["label"]),
        "--pdx-root", str(PDX_ROOT), "--resolution", str(resolution),
    ]
    for name in item.get("exclude", []):
        command += ["--exclude", name]
    if item.get("texture_dir"):
        command += ["--texture-dir", str(item["texture_dir"])]
    if not previews:
        command.append("--no-previews")
    log = out_dir / "raw" / f"{item['label']}.blender.log"
    with log.open("wb") as stream:
        completed = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=3000, check=False)
    if not raw.exists():
        return {"label": item["label"], "ok": False, "error": f"Blender exited {completed.returncode} without a result; see {log}"}
    return json.loads(raw.read_text(encoding="utf-8"))


def welded_geometry(result: dict) -> dict:
    """The same geometry with the adapter's diagnostic 1e-6 position weld applied to the topology counts.

    A glTF or PDX file stores a vertex once per UV or normal seam, so counting edges as imported reports
    every seam as a boundary and every shell as a loose part. The pipeline welds the working mesh before
    its gate; this is the closest offline stand-in for that.
    """

    geometry = dict(result["geometry"])
    welded = geometry.get("position_welded_topology")
    if welded:
        geometry["loose_boundary_edges"] = welded["loose_boundary_edges"]
        geometry["non_manifold_edges"] = welded["non_manifold_edges"]
        geometry["degenerate_faces"] = welded["degenerate_faces"]
        geometry["loose_component_count"] = sum(item["loose_component_count"] for item in welded["objects"])
    return geometry


def judge(result: dict, profile_name: str, out_dir: Path, *, welded: bool = False) -> dict:
    """The real candidate_gate on the measured geometry, plus the per-check table."""

    import run_pilot

    profile = run_pilot.load_profile(profile_name)
    geometry = welded_geometry(result) if welded else result["geometry"]
    prep = {"geometry": geometry, "materials": result["materials"]}
    job = out_dir / "gate_jobs" / (result["label"] + ("_welded" if welded else ""))
    (job / "validation").mkdir(parents=True, exist_ok=True)
    try:
        run_pilot.candidate_gate(job, prep, hard_max=profile["triangle_range"]["hard_max"], stage="scored", profile=profile)
    except RuntimeError:
        pass  # the gate writes its verdict before raising
    record = json.loads((job / "validation" / "scored_gate.json").read_text(encoding="utf-8"))
    return {
        "status": record["status"],
        "failures": record["failures"],
        "checks": {name: {k: v for k, v in check.items() if k in ("measured", "limit", "status")}
                   for name, check in record.get("checks", {}).items()},
    }


def summarize(result: dict) -> dict:
    geometry = result["geometry"]
    welded = geometry.get("position_welded_topology", {})
    textures = result["textures_in_blender"]["images"]
    return {
        "triangles": geometry["triangles"],
        "file_bytes": result["file"]["bytes"],
        "loose_components": geometry["loose_component_count"],
        "non_manifold_edges": geometry["non_manifold_edges"],
        "boundary_edges": geometry["loose_boundary_edges"],
        "boundary_edges_after_diagnostic_position_weld_1e-6": welded.get("loose_boundary_edges"),
        "non_manifold_after_weld": welded.get("non_manifold_edges"),
        "loose_components_after_weld": welded_geometry(result)["loose_component_count"],
        "degenerate_faces": geometry["degenerate_faces"],
        "material_slots": result["materials"]["unique_slots"],
        "uv_present": result["uv"]["present"],
        "texture_count_in_blender": len(textures),
        "texture_sizes_in_blender": [item["size"] for item in textures],
        "textures_on_disk": [
            {k: v for k, v in item.items() if k in ("file", "width", "height", "fourcc", "bytes")}
            for item in result.get("textures_on_disk", [])
        ],
        "bounding_height": round(result["bounding_height"], 4),
        "bounding_dimensions": [round(v, 4) for v in result["bounding_dimensions"]],
        "armatures": result["armatures"],
        "excluded_objects": [
            {k: item[k] for k in ("name", "triangles", "loose_boundary_edges", "non_manifold_edges")}
            for item in result["excluded_objects"]
        ],
        "preview_files": result.get("previews", {}).get("files"),
        "preview_error": result.get("previews", {}).get("error"),
    }


def text_summary(results: list, profile_name: str) -> str:
    lines = [
        f"Meshy comparison scoring harness, profile {profile_name}",
        "Limits judged by candidate_gate: non-manifold edges 0, boundary edges 0, loose components 1, "
        "triangles inside the preferred range, material slots at most 6, hard triangle maximum.",
        "",
    ]
    for item in results:
        lines.append(f"[{item['label']}]")
        if item.get("recorded"):
            g = item["geometry"]
            lines += [
                f"  recorded geometry from {item['source']} (status then: {item['recorded_status_at_the_time']}), not measured now",
                f"  triangles {g.get('triangles')}, non-manifold edges {g.get('non_manifold_edges')}, boundary edges "
                f"{g.get('loose_boundary_edges')} in {g.get('boundary_component_count')} boundary loops, "
                f"loose components {g.get('loose_component_count', 'not recorded')}",
                f"  candidate_gate verdict with today's limits: {item['gate']['status']}",
            ] + [f"    - {failure}" for failure in item["gate"]["failures"]] + [""]
            continue
        if not item.get("ok"):
            lines += [f"  FAILED TO MEASURE: {item.get('error')}", ""]
            continue
        s = item["summary"]
        lines += [
            f"  triangles {s['triangles']}, file {s['file_bytes']} bytes, bounding height {s['bounding_height']} "
            f"(dimensions {s['bounding_dimensions']})",
            f"  loose components {s['loose_components']}, non-manifold edges {s['non_manifold_edges']}, "
            f"boundary edges {s['boundary_edges']} (after a diagnostic 1e-6 position weld: "
            f"{s['boundary_edges_after_diagnostic_position_weld_1e-6']} boundary, {s['non_manifold_after_weld']} non-manifold, "
            f"{s['loose_components_after_weld']} loose components)",
            f"  material slots {s['material_slots']}, UV present {s['uv_present']}, textures in Blender "
            f"{s['texture_count_in_blender']} sizes {s['texture_sizes_in_blender']}",
        ]
        if s["textures_on_disk"]:
            lines.append(f"  textures on disk {s['textures_on_disk']}")
        if s["armatures"]:
            lines.append(f"  armatures {s['armatures']}")
        if s["excluded_objects"]:
            lines.append(f"  excluded provider objects {s['excluded_objects']}")
        gate = item["gate"]
        lines.append(f"  candidate_gate verdict: {gate['status']}")
        for failure in gate["failures"]:
            lines.append(f"    - {failure}")
        welded = item["gate_after_weld"]
        lines.append(f"  candidate_gate verdict if the seams were welded first (1e-6): {welded['status']}")
        for failure in welded["failures"]:
            lines.append(f"    - {failure}")
        lines.append(f"  previews: {s['preview_files'] or s['preview_error']}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--zin-baseline", type=Path, help="root of the finished zin_men_infantry job (read-only)")
    parser.add_argument("--recorded-gate", action="append", default=[], metavar="LABEL=GATE_JSON",
                        help="judge the geometry block of an earlier <stage>_gate.json with today's limits (no measuring)")
    parser.add_argument("--item", action="append", default=[], metavar="LABEL=PATH")
    parser.add_argument("--texture-dir", action="append", default=[], metavar="LABEL=DIR")
    parser.add_argument("--exclude", action="append", default=[], metavar="NAME", help="applied to every --item")
    parser.add_argument("--profile", default="humanoid_unit")
    parser.add_argument("--resolution", type=int, default=768)
    parser.add_argument("--no-previews", action="store_true")
    parser.add_argument("--only", action="append", default=[], help="score only these labels")
    args = parser.parse_args()

    items = zin_items(args.zin_baseline) if args.zin_baseline else []
    texture_dirs = dict(entry.split("=", 1) for entry in args.texture_dir)
    for entry in args.item:
        label, path = entry.split("=", 1)
        item = {"label": label, "model": Path(path), "exclude": list(args.exclude)}
        if label in texture_dirs:
            item["texture_dir"] = Path(texture_dirs[label])
        items.append(item)
    if args.only:
        items = [item for item in items if item["label"] in args.only]
    for item in items:
        if not Path(item["model"]).is_file():
            raise SystemExit(f"Missing model file: {item['model']}")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for item in items:
        print(f"scoring {item['label']} ...", flush=True)
        result = run_blender(item, args.out_dir, args.resolution, not args.no_previews)
        if result.get("ok"):
            result = {**result, "summary": summarize(result), "gate": judge(result, args.profile, args.out_dir),
                      "gate_after_weld": judge(result, args.profile, args.out_dir, welded=True)}
        results.append(result)
        (args.out_dir / "results.json").write_text(json.dumps(results, indent=2, default=str) + "\n", encoding="utf-8", newline="\n")
    for entry in args.recorded_gate:
        label, path = entry.split("=", 1)
        results.append(recorded_item(label, Path(path), args.profile, args.out_dir))
    (args.out_dir / "results.json").write_text(json.dumps(results, indent=2, default=str) + "\n", encoding="utf-8", newline="\n")
    summary = text_summary(results, args.profile)
    (args.out_dir / "summary.txt").write_text(summary, encoding="utf-8", newline="\n")
    print(summary)
    return 0 if all(item.get("ok") for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
