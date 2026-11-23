"""Work out the preset of a model from a few plain answers about its picture, and say it in one sentence to confirm (D-120).

    py -3.13 -B .tools/3d_pipeline/tripo/pick_preset.py --reference "<the subject's own reference>" [--reference ...]
        (--kind unit --legs 2|4 [--wings] [--weapon --hand LeftHand|RightHand] [--large] [--rider]
         | --kind vehicle|plane|ship|building|landmark)
        [--name "a fighter with an axe"] [--private <reference>] [--json]

The modder says "make a 3D unit from this picture". The agent looks at the picture and the description and answers only these questions:

- What is it: a unit (a person, creature or beast), a vehicle (tank, armoured car), a plane, a ship, a building or a landmark?
- A unit: how many legs reach the ground (2 or 4)? Does it have wings? Does it hold a weapon, and in which hand by its own side?
  Is it much bigger and heavier than a soldier? Does a four-legged mount carry a rider?

Fixed rules turn the answers into a preset, so the type never rests on judgement alone. The tool prints one sentence to confirm, with the
cost of the card (the default) and of the preset's Agentic Canvas workflow, and the next command (`tripo/new_job.py`). It refuses before
any picture step when no reference is given (D-110: a picture is made from references, never from a prompt alone), and it marks a
private reference, such as an owner's drawing, as one that never goes to Tripo or any other online service (D-123): the 3D-ready
picture is then made offline, or by the mod's own image lane, from it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import tripo_presets

STATIC_KINDS = {"vehicle": "tank", "plane": "plane", "ship": "ship", "building": "building", "landmark": "landmark"}
HANDS = ("LeftHand", "RightHand")


class PickError(ValueError):
    pass


def pick(answers: Dict[str, Any]) -> str:
    """The preset for a set of answers, by fixed rules. Raises PickError when the answers fit none or contradict each other."""

    kind = answers.get("kind")
    if kind in STATIC_KINDS:
        return STATIC_KINDS[kind]
    if kind != "unit":
        raise PickError(f"say what it is: a unit, or one of {', '.join(STATIC_KINDS)}")
    legs, wings, weapon = answers.get("legs"), bool(answers.get("wings")), bool(answers.get("weapon"))
    if legs == 4:
        if weapon:
            raise PickError("a four-legged body holds no weapon: its rider does. Answer --rider and make the rider as its own unit")
        if wings:
            return "winged_quadruped"
        return "mount_with_rider" if answers.get("rider") else "quadruped"
    if legs != 2:
        raise PickError("the route makes bodies on two or four legs. A body with none, or more than four, has no preset yet: ask first")
    if answers.get("rider"):
        raise PickError("a two-legged body carries no rider. A rider on a mount is the mount_with_rider preset (--legs 4 --rider)")
    if wings:
        return "winged_humanoid"
    if answers.get("large"):
        return "large_creature"
    return "armed_humanoid" if weapon else "humanoid"


def models(name: str, armed: bool) -> int:
    return 2 if armed and tripo_presets.get(name)["route"] == "tripo_rig" else 1


def costs(name: str, armed: bool) -> Dict[str, Any]:
    """The card's expected credits and the Canvas workflow's, from the preset and its workflow's extra credits per model."""

    preset = tripo_presets.get(name)
    low, high = preset["expected_credits"]
    workflows = json.loads(tripo_presets.WORKFLOWS.read_text(encoding="utf-8"))["workflows"]
    flow = workflows[tripo_presets.canvas_name(preset, armed)]
    extra = flow.get("extra_credits")
    canvas = None if extra is None else [low + extra, high + extra]
    return {"card": [low, high], "canvas": canvas, "canvas_workflow": flow["title"], "cap": preset["cap"]}


def credits_text(span: Optional[List[int]]) -> str:
    if span is None:
        return "its node prices are not read yet"
    low, high = span
    return f"about {low}" if low == high else f"about {low} to {high}"


def sentence(name: str, answers: Dict[str, Any]) -> str:
    preset = tripo_presets.get(name)
    armed = bool(answers.get("weapon"))
    cost = costs(name, armed)
    subject = answers.get("name") or "This model"
    return (f"{subject}: {preset['label'].lower()} (preset {name}). The card costs {credits_text(cost['card'])} credits, the Canvas "
            f"workflow {cost['canvas_workflow']} {credits_text(cost['canvas'])}, cap {cost['cap']}. {preset['proven']} Right?")


def new_job_command(name: str, answers: Dict[str, Any], references: List[str], slug: str, private: List[str]) -> str:
    parts = ["py", "-3.13", "-B", ".tools/3d_pipeline/tripo/new_job.py", "--jobs-config", "<your 3d_jobs.json>", "--preset", name, slug]
    for reference in references:
        parts += ["--private-source" if reference in private else "--source", reference]
    sets = []
    if tripo_presets.get(name).get("armed") == "optional":
        sets.append(f"armed={'true' if answers.get('weapon') else 'false'}")
    if answers.get("weapon") and answers.get("hand"):
        sets.append(f"weapon.hand={answers['hand']}")
    for item in sets:
        parts += ["--set", item]
    # Double quotes read the same in PowerShell, cmd, Git Bash and zsh for a value with spaces and apostrophes.
    return " ".join(json.dumps(part) if (" " in part or "'" in part) and part[:1] != "<" else part for part in parts)


def run(answers: Dict[str, Any], references: List[str], private: List[str], slug: str) -> Dict[str, Any]:
    if not [item for item in references if item.strip()]:
        raise PickError("give the subject's own reference first (the mod's art, an approved picture or a drawing), and for a real-world "
                        "subject the real references you found. A 3D picture is never made from a text prompt alone (D-110)")
    if answers.get("weapon") and answers.get("hand") not in HANDS:
        raise PickError("name the hand that holds the weapon by the character's own side: --hand LeftHand when the weapon is on the "
                        "viewer's right in a front view, --hand RightHand when it is on the viewer's left")
    name = pick(answers)
    preset = tripo_presets.get(name)
    clips = preset.get("clips") or {}
    return {
        "preset": name,
        "confirm": sentence(name, answers),
        "costs": costs(name, bool(answers.get("weapon"))),
        "fitting_clips": clips,
        "private_references": private,
        "private_note": ("These references are private and never go to Tripo or any other online service (D-123). Make the 3D-ready "
                         "picture from them offline or with the mod's own image lane, and give Tripo only that picture.") if private else "",
        "next": new_job_command(name, answers, references, slug, private),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kind", required=True, choices=["unit", *STATIC_KINDS])
    parser.add_argument("--legs", type=int, choices=[0, 2, 4])
    parser.add_argument("--wings", action="store_true")
    parser.add_argument("--weapon", action="store_true", help="it holds a weapon")
    parser.add_argument("--hand", choices=HANDS, help="the hand that holds the weapon, by the character's own side")
    parser.add_argument("--large", action="store_true", help="much bigger and heavier than a soldier")
    parser.add_argument("--rider", action="store_true", help="a four-legged mount that carries a rider")
    parser.add_argument("--name", default="", help="what it is, in a few words: 'a fighter with an axe'")
    parser.add_argument("--slug", default="<asset_slug>", help="the job's name, for the next command")
    parser.add_argument("--reference", action="append", default=[], help="a reference the picture is made from (repeat)")
    parser.add_argument("--private", action="append", default=[], help="a reference that is private, such as an owner's drawing")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    answers = {key: getattr(args, key) for key in ("kind", "legs", "wings", "weapon", "hand", "large", "rider", "name")}
    references = [*args.reference, *[item for item in args.private if item not in args.reference]]
    try:
        result = run(answers, references, args.private, args.slug)
    except PickError as error:
        print(f"no preset yet: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    print(result["confirm"])
    if result["private_note"]:
        print(result["private_note"])
    print(f"after a yes: {result['next']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
