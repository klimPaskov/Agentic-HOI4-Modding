"""Put an armed unit's weapon (and shield) in its hands, from the job entry, and write the body the intake reads.

    py -3.13 -B .tools/3d_pipeline/tripo/arm_unit.py --jobs-config <3d_jobs.json> <asset_slug> [--blender <blender.exe>]
        [--dry-run] [--skip-heavy-check]

It reads the files the card's export steps saved (`lib/tripo_card.armed_files`):

    <job folder>/armed/<slug>__body.glb            the rigged body with every clip, Tripo's Animate export
    <job folder>/armed/<slug>_weapon__model.glb    the weapon, Tripo's Model export
    <job folder>/armed/<slug>_shield__model.glb    the shield, only for a job with `tripo.shield`

and runs `tripo/grip_weapon.py` in headless Blender with the job's `tripo.weapon.hand`, the weapon on its own bone, the hold in the idle,
move, defend and retreat clips, the hold fading as the attack starts, the drop at the death's fall and the clearance in every role clip
(the commands of the orc and dwarf runs that passed review, November 2026). A job with `tripo.shield` then runs `tripo/shield_stage.py`
for the other hand. The last stage writes `<job folder>/inbox/<slug>__rigged.glb`, and each stage's report goes to `<job folder>/evidence`.
`tripo.weapon.grip_options` (and `tripo.shield.grip_options`) pass the stage's own numbers, for example `{"length_ratio": 1.4,
"grip": 0.47, "hold_hand": [0.26, 0.07, 0.69]}`.

Every Blender start waits for the machine first (`lib/heavy_job.py`), so no outer gate is needed. `--dry-run` checks the job and the
files, prints the commands and starts nothing. Exit 0 when the inbox file is written, 2 for a job or file that is not ready, and the
stage's own exit code when a stage fails.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import heavy_job, tripo_card
from lib.paths import resolve_job_root

HERE = Path(__file__).resolve().parent


def clip_names(glb: Path) -> List[str]:
    from lib import glb_root

    doc, _blob = glb_root._read(glb)
    return [str(animation.get("name") or "") for animation in doc.get("animations", [])]


def plan(spec: dict, slug: str, blender: str, job_root: Optional[Path] = None) -> List[List[str]]:
    """The stage commands for one armed job. Raises ValueError or FileNotFoundError naming what is not ready."""

    if not tripo_card.is_armed(spec):
        raise ValueError(f"{slug} has no tripo.weapon: an unarmed unit goes from its export straight to the intake")
    found = [item for item in tripo_card.problems(spec) if "posture" not in item]
    if found:
        raise ValueError("The job entry is not ready:\n- " + "\n- ".join(found))
    files = tripo_card.armed_files(job_root or resolve_job_root(slug), slug)
    wanted = ["body", "weapon"] + (["shield"] if tripo_card.has_shield(spec) else [])
    missing = [str(files[key]) for key in wanted if not files[key].is_file()]
    if missing:
        raise FileNotFoundError("Save the Tripo exports first (the card's export steps): " + ", ".join(missing))
    clips = tripo_card.role_clips(spec, clip_names(files["body"]))
    commands = [tripo_card.grip_command(spec, files, clips, blender, HERE / "grip_weapon.py")]
    if tripo_card.has_shield(spec):
        commands.append(tripo_card.shield_command(spec, files, clips, blender, HERE / "shield_stage.py"))
    return commands


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--jobs-config", required=True, type=Path)
    parser.add_argument("slug")
    parser.add_argument("--blender", help="the Blender to run (default BLENDER_EXE, then the kit's discovery)")
    parser.add_argument("--dry-run", action="store_true", help="check the job and the files, print the commands, start nothing")
    heavy_job.add_argument(parser)
    args = parser.parse_args(argv)
    heavy_job.apply(args)
    spec = tripo_card.job_entry(args.jobs_config, args.slug)
    if args.dry_run:
        blender = args.blender or "blender"
    else:
        import tripo_intake

        blender = str(tripo_intake.find_blender(args.blender))
    try:
        commands = plan(spec, args.slug, blender)
    except (ValueError, FileNotFoundError) as exc:
        print(f"arm_unit: {exc}", file=sys.stderr)
        return 2
    job_root = resolve_job_root(args.slug)
    (job_root / "evidence").mkdir(parents=True, exist_ok=True)
    (job_root / "inbox").mkdir(parents=True, exist_ok=True)
    for command in commands:
        stage = Path(command[command.index("--python") + 1]).stem
        print(f"{stage}: {' '.join(shlex.quote(part) for part in command)}")
        if args.dry_run:
            continue
        log = job_root / "evidence" / f"{stage}.log"
        with log.open("w", encoding="utf-8") as handle:
            done = heavy_job.run(command, label=f"arm_unit {stage} {args.slug}", stdout=handle, stderr=subprocess.STDOUT)
        if done.returncode != 0:
            print(f"arm_unit: {stage} failed with exit {done.returncode}. Its log is {log}, its report in {job_root / 'evidence'}.", file=sys.stderr)
            return done.returncode
        print(f"{stage}: done, log {log}")
    if not args.dry_run:
        print(f"arm_unit: wrote {tripo_card.armed_files(job_root, args.slug)['rigged']}. Next: tripo_intake.py (docs/3d-units.md step 8).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
