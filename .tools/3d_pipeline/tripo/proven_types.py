"""Print or refresh the list of proven asset types, which is written once, in `config/tripo_presets.json`.

    py -3.13 -B .tools/3d_pipeline/tripo/proven_types.py            # print the table
    py -3.13 -B .tools/3d_pipeline/tripo/proven_types.py --check    # fail when docs/3d-units.md differs from it
    py -3.13 -B .tools/3d_pipeline/tripo/proven_types.py --write    # rewrite the table in docs/3d-units.md

Change a status in the preset's `proven` text, then run `--write`. Nothing else states which types are proven: the skill, the
quick start and the agent point at the table in `docs/3d-units.md` (the `What is proven` section) or at `new_job.py --list`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import tripo_presets

DOC = PIPELINE_ROOT.parents[1] / "docs" / "3d-units.md"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 when docs/3d-units.md differs from the presets")
    parser.add_argument("--write", action="store_true", help="rewrite the table in docs/3d-units.md")
    parser.add_argument("--doc", type=Path, default=DOC)
    args = parser.parse_args(argv)
    if not (args.check or args.write):
        print(tripo_presets.proven_table())
        return 0
    if not args.doc.is_file():
        print(f"{args.doc} is not in this project; nothing to {'write' if args.write else 'check'}.")
        return 0
    current = tripo_presets.sync_proven_doc(args.doc, write=args.write)
    if args.write:
        print("docs/3d-units.md: proven-types table written." if not current else "docs/3d-units.md: proven-types table already current.")
        return 0
    print("docs/3d-units.md: proven-types table is current." if current else
          "docs/3d-units.md: proven-types table differs from config/tripo_presets.json. Run tripo/proven_types.py --write.")
    return 0 if current else 1


if __name__ == "__main__":
    raise SystemExit(main())
