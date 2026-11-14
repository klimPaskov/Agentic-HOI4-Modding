"""Bring a person's Tripo exports into a job, so the shared Blender stage can run with no Meshy call.

Tripo has no API. Export the files from the Tripo web app into one inbox folder and name each by
the one rule `<asset_slug>__<kind>.glb`, where kind is

    rigged     a unit: one GLB with the skin and every clip (Tripo's Rig, then Animate, "stay in place")
    model      a building or prop: one textured GLB
    segmented  an unrigged GLB split into parts, only when a weapon is found from its twin (see below)

Then run, once per asset (see `docs/3d-units.md`)::

    py -3.13 -B .tools/3d_pipeline/tripo_intake.py --jobs-config <jobs.json> <asset_slug> --inbox <folder>
        [--task-id <tripo task id>] [--credits <n> --credits-note <text>] [--blender <blender.exe>]

and then `run_pilot.py` as for any unit. The job entry says `"provider": "tripo"` and, for a unit::

    "tripo": {"roles": {"idle": "idle", "move": "walk", "attack": "chop", ...},
              "weapon": {"part": "tripo_part_1", "bone": "RightHand", "source": "rigged"},
              "trim": {"idle": 120}}

`roles` maps each HOI4 role to a Tripo clip name. `weapon` is optional: the named part is bound
rigidly to the bone (`source` "rigged": the part is a mesh in the rigged export; "twin": the vertices
whose nearest vertex in the `segmented` export belongs to the part). `trim` is optional: it cuts a
long clip to at most that many frames, ending on the frame closest to frame 0 so the loop is smooth.

The intake records each file's SHA-256, size and name in `provider/tripo_intake.json`, runs
`tripo/prepare_tripo_unit.py` in headless Blender for a unit, and places Meshy-shaped files in
`provider/downloads/` (each with its `.manifest.json`) and one task record per stage in
`provider/tasks/` (`provider: tripo`, status SUCCEEDED, a stable id). A second run with the same
files does nothing. Other files for the same stage are refused: use a new `generation_stage`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PIPELINE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_ROOT))

import run_pilot  # noqa: E402
from lib.credits import append_entry, read_ledger  # noqa: E402
from lib.paths import ensure_job_layout, file_record, read_json, resolve_job_root, sha256_file, utc_now, write_json  # noqa: E402
from lib.tripo import inbox_file, uses_tripo  # noqa: E402

PREPARE_SCRIPT = PIPELINE_ROOT / "tripo" / "prepare_tripo_unit.py"
RECEIPT = "provider/tripo_intake.json"
SUCCEEDED = "SUCCEEDED"


def find_blender(explicit: Optional[str] = None) -> Path:
    """`--blender`, then BLENDER_EXE, then the pipeline's own discovery (it never installs here)."""

    import bootstrap_3d_workflow as bootstrap

    if explicit:
        return Path(explicit)
    found = bootstrap.discover_blender_installs()
    executable, _shortcut, _version = bootstrap.select_supported_blender(found, bootstrap.supported_blender_minors())
    return executable


def intake_files(spec: Dict[str, Any], slug: str, inbox: Path) -> Dict[str, Path]:
    """The inbox files this job needs, by kind. A unit needs `rigged`; anything else needs `model`."""

    unit = spec["asset_kind"] == "humanoid"
    config = spec.get("tripo") or {}
    wanted = ["rigged"] if unit else ["model"]
    if unit and (config.get("weapon") or {}).get("source") == "twin":
        wanted.append("segmented")
    found = {kind: inbox_file(inbox, slug, kind) for kind in wanted}
    missing = [f"{slug}__{kind}.glb" for kind, path in found.items() if path is None]
    if missing:
        raise FileNotFoundError(f"The inbox {inbox} lacks {', '.join(missing)}. Name each Tripo export <asset_slug>__<kind>.glb.")
    return found  # type: ignore[return-value]


def default_task_id(files: Dict[str, Path]) -> str:
    main = files.get("rigged") or files["model"]
    return f"tripo-{sha256_file(main).lower()[:12]}"


def prepare_command(blender: Path, spec: Dict[str, Any], files: Dict[str, Path], out_dir: Path, report: Path) -> List[str]:
    """The headless Blender command that makes the base model and one GLB per role."""

    config = spec.get("tripo") or {}
    roles = config.get("roles") or {}
    wanted = [action.get("reuse_role") or action["role"] for action in spec["required_actions"]]
    missing = sorted({role for role in wanted if role not in roles})
    if missing:
        raise ValueError(f"The job's tripo.roles names no Tripo clip for: {', '.join(missing)}.")
    command = [
        str(blender), "-b", "--factory-startup", "--python-exit-code", "1", "--python", str(PREPARE_SCRIPT), "--",
        str(files["rigged"]), "--out-dir", str(out_dir), "--report", str(report),
        "--base-name", Path(run_pilot.generation_download_name(spec, "glb")).stem,
        "--role-name", Path(run_pilot.animation_download_name(spec, "{role}", "glb")).stem,
        "--roles", *[f"{role}={clip}" for role, clip in roles.items() if role in wanted],
    ]
    for role, frames in (config.get("trim") or {}).items():
        command += ["--trim", f"{role}={int(frames)}"]
    weapon = config.get("weapon")
    if weapon:
        pair = f"{weapon['part']}={weapon['bone']}"
        if weapon.get("source") == "twin":
            command += ["--rigid-from-twin", str(files["segmented"]), pair]
        else:
            command += ["--rigid-part", pair]
    return command


def parse_report(output: str) -> Dict[str, Any]:
    for line in reversed(output.splitlines()):
        if line.startswith('{"') and '"tool": "prepare_tripo_unit"' in line:
            return json.loads(line)
    raise RuntimeError("prepare_tripo_unit.py printed no report line; its output ends: " + output[-1500:])


def write_static_textures(glb: Path, folder: Path) -> Dict[str, str]:
    """PNG sidecars of the maps embedded in a one-material GLB (Pillow decodes; names as the lineage gate expects)."""

    import io

    from PIL import Image

    from lib.texture_lineage import ROLE_FILES, embedded_images

    found = embedded_images(glb)
    folder.mkdir(parents=True, exist_ok=True)
    written = {}
    for role, name in ROLE_FILES.items():
        images = found.get(role) or []
        if len(images) > 1:
            raise RuntimeError(f"{glb.name} uses {len(images)} different {role} maps; export a model with one material.")
        if images:
            picture = Image.open(io.BytesIO(images[0])).convert("RGB")
            picture.save(folder / name)
            if role == "specular":  # glTF packs roughness in green and metallic in blue; the PDX packer wants both apart
                picture.getchannel("B").save(folder / "metallic.png")
                picture.getchannel("G").save(folder / "roughness.png")
            written[role] = name
    if "diffuse" not in written:
        raise RuntimeError(f"{glb.name} embeds no base color map.")
    return written


def write_manifest(job: Path, path: Path, task_id: str, sources: List[Dict[str, Any]], *, textures: bool) -> Dict[str, Any]:
    record = {
        "timestamp": utc_now(),
        "provider": "tripo",
        "task_id": task_id,
        "task_type": "tripo_export",
        "format": "glb",
        "include_textures": textures,
        "file": file_record(path, relative_to=job),
        "source_files": sources,
    }
    write_json(path.with_name(path.name + ".manifest.json"), record)
    return record


def write_task(job: Path, stage: str, task_type: str, task_id: str, sources: List[Dict[str, Any]], **extra: Any) -> None:
    write_json(run_pilot.task_file(job, stage), {
        "schema_version": "1.0.0",
        "stage": stage,
        "task_id": task_id,
        "task_type": task_type,
        "status": SUCCEEDED,
        "provider": {"name": "tripo", "mode": "manual_export"},
        "estimated_credits": 0,
        "consumed_credits": 0,
        "input_files": sources,
        "recorded_at": utc_now(),
        **extra,
    })


def run_intake(
    spec: Dict[str, Any],
    inbox: Path,
    *,
    task_id: Optional[str] = None,
    credits: Optional[int] = None,
    credits_note: str = "",
    blender: Optional[str] = None,
) -> Dict[str, Any]:
    if not uses_tripo(spec):
        raise ValueError(f"{spec['asset_id']} is not a Tripo job; add \"provider\": \"tripo\" to its entry.")
    run_pilot.prepare_spec(spec)
    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = ensure_job_layout(resolve_job_root(slug))
    files = intake_files(spec, slug, Path(inbox))
    sources = [
        {"kind": kind, "name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for kind, path in sorted(files.items())
    ]
    task_id = task_id or default_task_id(files)
    receipt_path = job / RECEIPT
    if receipt_path.is_file():
        previous = read_json(receipt_path)
        if previous["sources"] == sources:
            return {**previous, "state": "already_ingested"}
        raise RuntimeError(
            f"{slug} already took other Tripo files (task {previous['task_id']}). A new export is a new stage: "
            f"set \"generation_stage\": \"generation_2\" in the job entry, then run the intake again."
        )
    downloads = job / "provider" / "downloads"
    generation_stage = run_pilot.generation_stage_for(spec)
    base = downloads / run_pilot.generation_download_name(spec, "glb")
    outputs: Dict[str, Any] = {}
    prepared: Optional[Dict[str, Any]] = None
    if spec["asset_kind"] == "humanoid":
        report = job / "provider" / "tripo_prepare_report.json"
        command = prepare_command(find_blender(blender), spec, files, downloads, report)
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
        if completed.returncode != 0:
            raise RuntimeError(f"Blender failed ({completed.returncode}): {(completed.stdout + completed.stderr)[-2000:]}")
        prepared = parse_report(completed.stdout)
        outputs["generation"] = write_manifest(job, base, task_id, sources, textures=True)
        write_task(job, generation_stage, "image-to-3d", task_id, sources)
        for role, clip in prepared["clips"].items():
            path = downloads / clip["file"]
            outputs[role] = write_manifest(job, path, task_id, sources, textures=False)
            write_task(job, run_pilot.animation_stage_for(spec, role), "animation", task_id, sources, library_clip=clip["clip"])
    else:
        import shutil

        shutil.copy2(files["model"], base)
        write_static_textures(base, base.with_name(base.stem + "_textures"))
        outputs["generation"] = write_manifest(job, base, task_id, sources, textures=True)
        write_task(job, generation_stage, "image-to-3d", task_id, sources)
    if credits is not None and not any(row.get("intake_task_id") == task_id for row in read_ledger(job)):
        append_entry(
            job,
            stage=generation_stage,
            operation="image_to_3d",
            model="tripo",
            scope=f"tripo:{slug}",
            estimate_credits=credits,
            consumed_credits=credits,
            consumed_source="manual_entry",
            outcome="success",
            reason=credits_note or "Tripo credits typed in at intake",
            intake_task_id=task_id,
        )
    record = {
        "schema_version": "1.0.0",
        "asset": slug,
        "task_id": task_id,
        "received_at": utc_now(),
        "sources": sources,
        "credits": credits,
        "credits_note": credits_note,
        "outputs": {name: item["file"]["relative_path"] for name, item in outputs.items()},
        "prepare": {key: prepared[key] for key in ("blender", "bones_before", "bones_after", "weapon", "clips", "triangles")} if prepared else None,
    }
    write_json(receipt_path, record)
    run_pilot.append_history(job, state="provider_task_completed", event=generation_stage, actor="tripo_intake", details={"task_id": task_id, "files": sources})
    return {**record, "state": "ingested"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Bring Tripo exports from an inbox folder into a job.")
    parser.add_argument("--jobs-config", required=True, type=Path)
    parser.add_argument("--inbox", required=True, type=Path)
    parser.add_argument("--task-id", help="Tripo task id (default: tripo-<first 12 hex of the main file's SHA-256>)")
    parser.add_argument("--credits", type=int, help="Tripo credits spent on this asset")
    parser.add_argument("--credits-note", default="")
    parser.add_argument("--blender", help="blender executable (default: BLENDER_EXE, then the pipeline's discovery)")
    parser.add_argument("asset")
    args = parser.parse_args()
    configs = run_pilot.load_job_configs(args.jobs_config)
    if args.asset not in configs:
        raise KeyError(f"Unknown configured 3D job: {args.asset}")
    result = run_intake(
        configs[args.asset], args.inbox, task_id=args.task_id, credits=args.credits,
        credits_note=args.credits_note, blender=args.blender,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
