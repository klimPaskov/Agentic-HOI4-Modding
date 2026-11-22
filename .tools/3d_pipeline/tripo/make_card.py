"""Write a job's Tripo card from its job entry and `tripo/CARD_TEMPLATE.md`.

    py -3.13 -B .tools/3d_pipeline/tripo/make_card.py --jobs-config <3d_jobs.json> <asset_slug> [--out <card.md>]

The card goes to `<job folder>/CARD.md` unless `--out` names another file. It keeps the template's armed steps (weapon picture, weapon
model, grip) only for a job with `tripo.weapon`, fills the hand, the weapon's name, the sources and the file names, and records the kit
commit it was written from. It refuses, and lists what to add, a job entry that would leave a step open: no `reference_sources`, an
armed unit type without `tripo.weapon`, a weapon without `hand` (named by the rig's side) or `name`, no `tripo.posture` for a unit.
See `lib/tripo_card.py`.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import tripo_card
from lib.paths import resolve_job_root

TEMPLATE = Path(__file__).resolve().parent / "CARD_TEMPLATE.md"
REPO_ROOT = PIPELINE_ROOT.parents[1]


def kit_commit() -> str:
    try:
        out = subprocess.run(["git", "-C", str(PIPELINE_ROOT), "rev-parse", "--short=12", "HEAD"], capture_output=True, text=True, check=True)
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--jobs-config", required=True, type=Path)
    parser.add_argument("slug")
    parser.add_argument("--out", type=Path, help="where to write the card (default <job folder>/CARD.md)")
    args = parser.parse_args(argv)
    spec = tripo_card.job_entry(args.jobs_config, args.slug)
    found = tripo_card.problems(spec)
    if found:
        print("The job entry is not ready for a card. Add these to it, then run this again:", file=sys.stderr)
        for item in found:
            print(f"- {item}", file=sys.stderr)
        return 2
    job_root = resolve_job_root(args.slug)
    text = tripo_card.fill(TEMPLATE.read_text(encoding="utf-8"), spec, args.slug, job_folder=relative(job_root), kit_commit=kit_commit())
    out = args.out or job_root / "CARD.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(text.encode("utf-8"))
    kind = "armed" if tripo_card.is_armed(spec) else "unarmed"
    print(f"card written: {relative(out)} ({kind}{', hand ' + tripo_card.weapon_hand(spec) if kind == 'armed' else ''})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
