"""Bring a person's Tripo exports into a job, so the shared Blender stage can run with no Meshy call.

Tripo has no API. Export the files from the Tripo web app into one inbox folder and name each by
the one rule `<asset_slug>__<kind>.glb`, where kind is

    rigged     a unit: one GLB with the skin and every clip (Tripo's Rig, then Animate, "stay in place")
    model      a building or prop: one textured GLB
    segmented  an unrigged GLB split into parts, only when a weapon is found from its twin (see below)

Then run, once per asset (see `docs/3d-units.md`)::

    py -3.13 -B .tools/3d_pipeline/tripo_intake.py --jobs-config <jobs.json> <asset_slug> --inbox <folder>
        [--task-id <tripo task id>] [--credits <n> --credits-note <text>] [--blender <blender.exe>] [--skip-heavy-check]

The intake starts Blender itself. It first waits for the machine (lib/heavy_job.py): one kit Blender at a time and a floor of free RAM,
with one line saying why it waits; `--skip-heavy-check` starts at once.

Run `run_pilot.py` after it, as for any unit. Tripo's auto-rig may add extra joints to the Mixamo skeleton (`neutral_bone` since
November 2026: a childless joint with no animation under the armature). The intake drops them, moves any weight they carry to the
nearest kit bone by the vertex's position (lib/tripo_extra_joints.py) and prints one line, `extra joints dropped: ...`, with how many
weights moved. The job entry says `"provider": "tripo"` and, for a unit::

    "tripo": {"roles": {"idle": "idle", "move": "walk", "attack": "chop", ...},
              "weapon": {"part": "tripo_part_1", "bone": "RightHand", "source": "rigged"},
              "trim": {"idle": 120}}

`roles` maps each HOI4 role to a Tripo clip name, or to the start of one (Tripo names a text-to-motion
clip with its whole prompt). A start that matches two clips or none is refused with the list of clip names,
and the intake prints the clip names it found. `weapon` is optional: the named part is bound
rigidly to the bone (`source` "rigged": the part is a mesh in the rigged export; "twin": the vertices
whose nearest vertex in the `segmented` export belongs to the part). `weapon.bone` may be `Weapon`, the bone a
separate weapon gets from `tripo/grip_weapon.py --weapon-bone`; `weapon.release_roles` (for example `["death"]`) names the
roles in which the unit lets go of it: the kit grounds those clips by the body alone and the loose-part check does not
judge that bone's part for drifting. `shield` is optional too: `{"part": "tripo_part_2", "bone": "Shield", "release_roles": ["death"]}`
(those are the defaults but for the roles) names the shield `tripo/shield_stage.py` put in the free hand, bound rigidly to its own bone,
with the same release rule as the weapon. `trim` is optional: it cuts a
long clip to at most that many frames, ending on the frame closest to frame 0 so the loop is smooth.
A clip that ends still is trimmed by rule without it (`lib/tripo_trim.py`): attack, defend and retreat drop the part after the motion fell under
5% of the clip's own peak and keep half a second of settle. `trim` for a role wins, and `"auto_trim": false` (or a list of roles) switches the rule off (or limits it).
`settle` (default attack, defend and retreat, `false` or a shorter list to limit it) appends frames that blend the clip's last pose back to its first, because the game loops it (`lib/tripo_trim.py`).
The move and the retreat are a looped gait and get the loop window instead (`lib/tripo_loop.py`): the clip is cut to its best whole number of strides, the window inside its
striding phase whose end continues into its start best, and the seam is closed over the last frames with no stop. A preset walk that already loops keeps every frame.
`trim` for a role wins, and `"loop_window": false` (or a list of roles) switches the rule off (or limits it), which gives the role the trim and the settle above.
`untwist` (default every role, `false` or a shorter list to limit it) turns the spine back where the shoulders twist against the standing feet past vanilla's worst for the role (`lib/tripo_pose.py`, the stance twist).
`ease_snaps` (default 14, `false` to switch it off, or another number of degrees per frame to ease from) eases any joint turn faster than that in the role clips (the kit rejects a clip over 37 degrees in one frame at 30 fps).
`chains` is optional: `[{"region": "cloak"}]` or `[{"region": "wings"}]` (or both) gives that region its own bone chains, rebinds it and keys
it per role by fixed rules (`tripo/chain_stage.py`, `lib/tripo_chains.py`), so a cloak no longer follows the thighs and wings no longer follow the arms.
`part_triangles` is optional too: `{"tripo_part_1": 1500}` reduces a part to about that many triangles
before it is bound (a separately modelled weapon has far more than a hand weapon needs), and `"auto"` takes
the first of 1500, 2500 and 4000 that keeps the part's shape. The reduction welds first and is checked
(shell count, front/side/top silhouette agreement of at least `part_shape_iou`, default 0.97), and a part that
fails the check stops the intake.

The intake records each file's SHA-256, size and name in `provider/tripo_intake.json`, runs
`tripo/prepare_tripo_unit.py` in headless Blender for a unit, and places Meshy-shaped files in
`provider/downloads/` (each with its `.manifest.json`) and one task record per stage in
`provider/tasks/` (`provider: tripo`, status SUCCEEDED, a stable id). A second run with the same
files does nothing. Other files for the same stage are refused: use a new `generation_stage`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

PIPELINE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_ROOT))

import run_pilot
from lib import heavy_job, tripo_extra_joints, tripo_loop, tripo_pose, tripo_trim
from lib.credits import append_entry, read_ledger
from lib.paths import ensure_job_layout, file_record, read_json, resolve_job_root, sha256_file, utc_now, write_json
from lib.tripo import inbox_file, uses_tripo
from lib.tripo_shield import SHIELD_BONE, SHIELD_PART

# Every Tripo job eases joint turns faster than this many degrees per frame (tripo/prepare_tripo_unit.py --ease-snaps). The kit retimes
# Tripo's 24 fps clips to 30 and one frame's step can double, so a clip with 20 degrees a frame arrives at 38 against the kit's limit of 37
# (the zombie's `fall` did at 20). 14 holds for the zombie and the orc (spin per clip in their reports) and moves little else.
DEFAULT_EASE_SNAPS = 14.0
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


def refuse_travelling_clips(spec: Dict[str, Any], rigged: Path) -> None:
    """Refuse a rigged export whose role clips carry travel in the hips (lib/glb_root.py): the route's loop, grounding and weapon-drop
    rules expect clips exported with Tripo's "Animation in Place" switch on."""

    from lib import glb_root

    roles = (spec.get("tripo") or {}).get("roles") or {}
    try:
        travelling = glb_root.travelling_clips(rigged, roles.values())
    except ValueError:  # not a binary glTF: the Blender stage reads it and says what is wrong
        return
    if travelling:
        listed = ", ".join(f"{clip.strip()} {travel:.2f}" for clip, travel in sorted(travelling.items()))
        raise ValueError(
            f"{rigged.name}: these role clips move the hips across the ground ({listed} times the hip height, limit "
            f"{glb_root.MAX_ROOT_TRAVEL_SHARE}). Export again from Tripo with \"Animation in Place\" switched on.")


def default_task_id(files: Dict[str, Path]) -> str:
    main = files.get("rigged") or files["model"]
    return f"tripo-{sha256_file(main).lower()[:12]}"


def loop_roles(config: Dict[str, Any], wanted: Sequence[str], explicit: Dict[str, Any]) -> List[str]:
    """The roles that get the loop window (lib/tripo_loop.py): the move and the retreat, less the roles with a `trim` of their own and what
    the job's `loop_window` switches off (`false`, or a list that names the roles to keep)."""

    chosen = config.get("loop_window", list(tripo_loop.STRIDE_ROLES))
    if not chosen:
        return []
    return [role for role in tripo_loop.STRIDE_ROLES if role in wanted and role not in explicit and (chosen is True or role in chosen)]


def loop_arguments(config: Dict[str, Any], wanted: Sequence[str], explicit: Dict[str, Any], roles: Dict[str, str], rigged: Path):
    """(the prepare stage's `--loop-window` and `--loop-close` arguments, {role: its window}) for the looped gaits of a job."""

    looped = loop_roles(config, wanted, explicit)
    windows = tripo_loop.auto_windows(rigged, roles, explicit=set(explicit), apply_to=looped) if looped else {}
    arguments: List[str] = []
    for role, found in windows.items():
        if not found["whole"]:
            arguments += ["--loop-window", f"{role}={found['first']}:{found['last']}"]
        print(f"loop window: {role} ({found['clip'][:40]}) frames {found['first']} to {found['last']} of {found['from_frames']}"
              + (" (the clip loops as it is)" if found["whole"] else f", striding from frame {found['phase'][0]} to {found['phase'][1]}")
              + f", seam cost {found['cost']} of the height", file=sys.stderr)
    for role in looped:
        if role not in windows:
            print(f"loop window: {role} never strides, so it keeps the trim and the settle (TRIPO-LOOP-STANDS will fail it)", file=sys.stderr)
    looped = [role for role in looped if role in windows]
    if looped:
        arguments += ["--loop-close", *looped]
    return arguments, windows


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
    for part, budget in (config.get("part_triangles") or {}).items():
        command += ["--part-triangles", f"{part}={budget if budget == 'auto' else int(budget)}"]
    if config.get("part_shape_iou") is not None:
        command += ["--shape-iou", str(float(config["part_shape_iou"]))]
    explicit = config.get("trim") or {}
    for role, frames in explicit.items():
        command += ["--trim", f"{role}={int(frames)}"]
    # The looped gait (lib/tripo_loop.py): the move and the retreat are cut to their best whole strides and closed with no stop. A job's own trim wins.
    looping, windows = loop_arguments(config, wanted, explicit, roles, files["rigged"])
    command += looping
    # The rule for a clip that ends still (lib/tripo_trim.py): an attack, defend or retreat clip drops its trailing still part. A job's own trim wins.
    auto = config.get("auto_trim", list(tripo_trim.DEFAULT_ROLES))
    if auto:
        for role, found in tripo_trim.auto_trims(files["rigged"], roles, explicit=set(explicit), apply_to=[role for role in tripo_trim.DEFAULT_ROLES if role in wanted and role not in windows and (auto is True or role in auto)]).items():
            command += ["--trim-end", f"{role}={found['keep_frames']}"]
            print(f"auto trim: {role} ({found['clip'][:40]}) {found['from_frames']} -> {found['keep_frames']} frames, still from frame {found['still_from_frame']} "
                  f"(floor {found['floor_degrees']} degrees a frame, 5% of its peak {found['peak_degrees']})", file=sys.stderr)
    # The game loops an action clip, so it must end in its first frame's pose (lib/tripo_trim.settle_frames): `settle` lists the roles ([] or false to switch it off).
    settled = config.get("settle", list(tripo_trim.SETTLE_ROLES))
    settled = [role for role in tripo_trim.SETTLE_ROLES if role in wanted and settled and (settled is True or role in settled)]
    if settled:
        command += ["--settle", *settled]
    # Shoulders twisted against the hips past vanilla's worst for the role are turned back at the spine (lib/tripo_pose.py, TRIPO-WAIST-TWIST):
    # `untwist` lists the roles ([] or false to switch it off); the default is every role.
    untwisted = config.get("untwist", list(tripo_pose.VANILLA_WAIST_TWIST_DEGREES))
    untwisted = [role for role in tripo_pose.VANILLA_WAIST_TWIST_DEGREES if role in wanted and untwisted and (untwisted is True or role in untwisted)]
    if untwisted:
        command += ["--untwist", *untwisted]
    # An unarmed unit's attack clip gets the arm-level rule (lib/tripo_arms.py): Tripo's text-to-motion attacks hold the hands over the head and
    # hide it. `arm_level` lists the roles ([] or false to switch it off); the default is the attack of a job with no weapon.
    levelled = config.get("arm_level", [] if config.get("weapon") else ["attack"])
    if levelled:
        command += ["--arm-level"] + list(levelled)
        # The target height defaults to 0.85 in prepare_tripo_unit.py (arms straight forward at shoulder height); a job may name another.
        if config.get("arm_level_target") is not None:
            command += ["--arm-level-target", str(float(config["arm_level_target"]))]
    value = config.get("ease_snaps", DEFAULT_EASE_SNAPS)
    if value:
        command += ["--ease-snaps"] + ([] if value is True else [str(float(value))])
    # Secondary chains (tripo/chain_stage.py): `"chains": [{"region": "cloak"}, {"region": "wings"}]`, or the region names alone.
    regions = [item["region"] if isinstance(item, dict) else str(item) for item in config.get("chains") or []]
    if regions:
        command += ["--chains", *regions]
    return command + rigid_part_args(config, files)


def rigid_part_args(config: Dict[str, Any], files: Dict[str, Path]) -> List[str]:
    """The prepare script's options for the parts bound rigidly to one bone each: the weapon, then a shield held in the free hand
    (tripo/shield_stage.py), a second rigid part on its own bone."""

    out: List[str] = []
    weapon = config.get("weapon")
    if weapon:
        pair = f"{weapon['part']}={weapon['bone']}"
        if weapon.get("source") == "twin":
            out += ["--rigid-from-twin", str(files["segmented"]), pair]
        else:
            out += ["--rigid-part", pair]
    shield = config.get("shield")
    if isinstance(shield, dict):  # an empty block is a shield with the default part and bone
        out += ["--rigid-part", f"{shield.get('part', SHIELD_PART)}={shield.get('bone', SHIELD_BONE)}"]
    return out


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
    if "rigged" in files:
        refuse_travelling_clips(spec, files["rigged"])
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
        completed = heavy_job.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
        if completed.returncode != 0:
            raise RuntimeError(f"Blender failed ({completed.returncode}): {(completed.stdout + completed.stderr)[-2500:]}")
        prepared = parse_report(completed.stdout)
        extra = prepared.get("extra_joints") or {}
        print(tripo_extra_joints.report_line(extra.get("dropped", []), int(extra.get("weights_moved", 0))), file=sys.stderr)
        print(f"Tripo clips in {files['rigged'].name}: {prepared['clips_in_file']}", file=sys.stderr)
        print(f"Roles use: { {role: clip['clip'] for role, clip in prepared['clips'].items()} }", file=sys.stderr)
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
        "extra_joints": (prepared.get("extra_joints") or {"dropped": [], "weights_moved": 0}) if prepared else None,
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
    heavy_job.add_argument(parser)
    parser.add_argument("asset")
    args = parser.parse_args()
    heavy_job.apply(args)
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
