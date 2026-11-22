"""The effects step of the 3D route: place a unit's effect locators, time its particle events and check them. No Blender, no credits.

    py -3.13 -B .tools/3d_pipeline/tripo/effects_stage.py <unit files folder> --job <job.json> [--stem <stem>] [--preset <name>]
        [--entity <entity .asset>] [--mod-root <mod>] [--check-only] [--json]

`<unit files folder>` holds `<stem>.mesh` and `<stem>_<role>.anim`: a Tripo unit's `runtime/files`, or a static model's
`mod/gfx/models/<folder>/<name>`. The job (a job entry, or any JSON file) holds an `effects` block, at the top level or under `tripo`:

    "effects": {"profiles": ["tank_cannon", "tank_wreck"], "setting": ["gunpowder"],
                "colour": {"spell_bolt": [90, 200, 255]}, "frames": {"cast_hand_r": 31}}

`profiles` are keys of `config/effects.json`. `setting` says what the unit's world has (`gunpowder`, `magic`, `fire_creature`): a profile
that needs what the setting lacks is refused (EFFECT-FIT, D-127). `colour` overrides an adapted particle's colour, `frames` a slot's frame.
With `--preset`, a profile the preset does not list in its `effects` is refused too.

It writes the new locators into the `.mesh`, the plan `<stem>_effects.json` beside it, and then:

- with `--entity` (a static model's `mod/gfx/entities/<name>.asset`): the events and sounds into that entity's states, replacing the
  particle events vanilla's entity had at the same locators, and a state for a role the entity lacks (a tank's death);
- with `--mod-root`: the adapted particle files and their `.gfx` registration under that mod (a Tripo unit gets them from `wire_unit.py`).

Then it runs the checks (`lib/unit_effects.findings`) and prints PASS or FAIL. Exit code 1 on any finding, 2 on unreadable input.
`--check-only` checks an existing plan without measuring or writing anything.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

from lib import tripo_presets, unit_effects, unit_wiring

KIT_ROOT = PIPELINE.parents[1]


def game_dir() -> Optional[Path]:
    import importlib.util

    try:
        spec = importlib.util.spec_from_file_location("kit_game_locator", KIT_ROOT / ".tools" / "lib" / "game.py")
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        found = module.game_dir()
        return Path(found) if found and Path(found).is_dir() else None
    except Exception:  # noqa: BLE001 - no game folder only skips the file checks
        return None


def effects_block(job: Dict[str, Any]) -> Dict[str, Any]:
    block = job.get("effects") or (job.get("tripo") or {}).get("effects")
    if not isinstance(block, dict):
        raise unit_effects.EffectsError("the job has no effects block (`effects` at the top level or in `tripo`)")
    return block


def find_stem(folder: Path, given: Optional[str]) -> str:
    if given:
        return given
    meshes = sorted(folder.glob("*.mesh"))
    if len(meshes) != 1:
        raise unit_effects.EffectsError(f"{folder} holds {len(meshes)} .mesh files; pass --stem")
    return meshes[0].stem


def write_entity(path: Path, plan: Dict[str, Any]) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.find("entity = {")
    if start < 0:
        raise unit_effects.EffectsError(f"{path} holds no entity")
    roles_with_clips = sorted({e["role"] for e in plan["events"]} | {s["role"] for s in plan.get("sounds", [])})
    head, block = text[:start], text[start:]
    block = unit_wiring.apply_effect_events(block, plan["events"], plan.get("sounds", []), add_states=[r for r in roles_with_clips if r == "death"])
    path.write_text(head + block, encoding="utf-8", newline="\n")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("folder")
    parser.add_argument("--job", help="a JSON file with an effects block")
    parser.add_argument("--stem")
    parser.add_argument("--preset", help="the Tripo preset the unit was made from (its `effects` list bounds the profiles)")
    parser.add_argument("--entity", help="a static model's entity .asset to write the events into")
    parser.add_argument("--mod-root", help="write the adapted particle files under this mod")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    folder = Path(args.folder)
    game = game_dir()
    try:
        stem = find_stem(folder, args.stem)
        allowed = None
        if args.preset:
            allowed = tripo_presets.get(args.preset).get("effects", [])
        if args.check_only:
            plan = unit_effects.read_plan(folder, stem)
            if plan is None:
                raise unit_effects.EffectsError(f"no {stem}{unit_effects.PLAN_SUFFIX} in {folder}")
        else:
            if not args.job:
                raise unit_effects.EffectsError("pass --job (or --check-only)")
            job = json.loads(Path(args.job).read_text(encoding="utf-8"))
            plan = unit_effects.make_plan(folder, stem, effects_block(job), allowed=allowed)
            if args.entity:
                write_entity(Path(args.entity), plan)
            if args.mod_root:
                files, problems = unit_effects.particle_files(plan, game)
                if problems:
                    raise unit_effects.EffectsError("; ".join(problems))
                for rel, text in files:
                    dest = Path(args.mod_root) / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(text, encoding="utf-8", newline="\n")
        found = unit_effects.findings(folder, stem, plan, game=game, allowed=allowed)
    except (unit_effects.EffectsError, OSError, json.JSONDecodeError, KeyError) as error:
        print(f"effects: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"plan": plan, "findings": found}, indent=1))
    else:
        for line in unit_effects.summary_lines(plan):
            print(line)
        for item in found:
            print(f"{item['rule']}: {item['message']}")
        print("effects: " + ("PASS" if not found else f"FAIL ({len(found)})"))
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
