"""Claim a unit's clips in its mod, so every distinct unit type has its own animations (D-136, 3D-6). See lib/anim_claims.py.

    py -3.13 -B .tools/3d_pipeline/tripo/anim_claims.py claim --jobs-config <3d_jobs.json> <asset_slug> [--source "<free preset|made, task id>"]
    py -3.13 -B .tools/3d_pipeline/tripo/anim_claims.py check --jobs-config <3d_jobs.json> <asset_slug>
    py -3.13 -B .tools/3d_pipeline/tripo/anim_claims.py list --mod-root <mod>
    py -3.13 -B .tools/3d_pipeline/tripo/anim_claims.py import --mod-root <mod> --mod <name in the table> <claims.md>

`--registry <file.json>` (or the job's `anim_registry`) keeps the record outside the mod. `.hoi4_3d/` is a development folder: it never
ships with the mod. `claim` takes the clips of the job's `tripo.roles` and writes them for the job under a lock: the earliest claim holds a clip. It exits 3
and writes nothing when another unit of the mod already holds one of them, and names that unit. A reskin of another unit sets
`reskin_of` in its job and shares that unit's clips. `check` reports without writing (exit 3 on a clash). Claim as soon as you pick a
clip for a role, before you export or run the Blender stage, so the next worker sees it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import anim_claims as A
from lib import tripo_card


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("action", choices=["claim", "check", "list", "import"])
    parser.add_argument("slug", nargs="?")
    parser.add_argument("--jobs-config", type=Path)
    parser.add_argument("--mod-root", type=Path)
    parser.add_argument("--registry", type=Path, help="a registry .json kept outside the mod (instead of <mod root>/.hoi4_3d/anim_claims.json)")
    parser.add_argument("--mod", help="import: the mod's name in the table's first column")
    parser.add_argument("--source", default="", help="claim: where the clips come from (free preset, or made with its task id)")
    args = parser.parse_args(argv)

    if args.action in ("claim", "check"):
        if not (args.jobs_config and args.slug):
            parser.error("claim and check need --jobs-config and the job's name")
        spec = tripo_card.job_entry(args.jobs_config, args.slug)
        root = args.registry or args.mod_root or A.registry_for(spec, args.jobs_config)
        if root is None:
            print("no mod root: set `mod_root` in the job, or keep the jobs file inside the mod's git repository", file=sys.stderr)
            return 2
        roles = (spec.get("tripo") or {}).get("roles") or {}
        if not roles:
            print("the job names no clips yet (tripo.roles)", file=sys.stderr)
            return 2
        if args.action == "check":
            found = A.conflicts(root, args.slug, roles.values(), spec.get("reskin_of"))
            if found:
                print(A.conflict_message(found))
                return 3
            print(f"UNIT-ANIM-SHARED: pass, no other unit of {root.name} holds {', '.join(A.clip_key(c) for c in roles.values())}")
            return 0
        result = A.claim(root, args.slug, roles, source=args.source, reskin_of=spec.get("reskin_of"))
        if result["held"]:
            print(A.conflict_message(result["held"]))
            return 3
        print(json.dumps({"tool": "anim_claims", "registry": A.registry_path(root).as_posix(), **result}))
        return 0

    if args.registry:
        args.mod_root = args.registry
    if not args.mod_root:
        parser.error(f"{args.action} needs --mod-root or --registry")
    if args.action == "list":
        for clip, owner in sorted(A.holders(args.mod_root).items()):
            print(f"{clip:40} {owner['unit']:24} {owner.get('role', ''):8} {owner.get('time', '')}")
        return 0
    if not (args.mod and args.slug):
        parser.error("import needs --mod and the claims file")
    result = A.import_markdown(args.mod_root, Path(args.slug).read_text(encoding="utf-8"), args.mod)
    for unit, role, clip, state in result["rows"]:
        print(f"{state:5} {unit:24} {role:8} {clip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
