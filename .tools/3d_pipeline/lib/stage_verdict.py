"""One short JSON verdict per stage of the 3D route, so any model can follow the route from a checklist.

Every stage command (`check_unit_files.py`, `repair_unit.py`, `review_unit.py`, `measure_body.py`, and the
Meshy stages of `run_pilot.py`) can write the same shape:

    {"stage": "check", "ok": false, "verdict": "fail", "unit": "zin_yeti_band",
     "outputs": {...}, "sheets": [...], "checklist": "...", "findings": [...],
     "escalate": null, "next": ["py -3.13 -B .tools/3d_pipeline/repair_unit.py ..."]}

- `verdict` is `pass`, `fail` (a free fix exists: run `next`) or `escalate` (no scripted fix: author the
  motion live in Blender, or ask the user about a paid step; `escalate` says why and where to read).
- `findings` are short: rule, file name and the first sentence of the message.
- `next` holds the exact commands to run, in order. A stage that passes names the following stage.

`next_for_findings` maps each check rule to its fix. A rule a script cannot fix escalates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

SCHEMA = 1
PIPELINE = ".tools/3d_pipeline"
PY = "py -3.13 -B"
LIVE_GUIDE = ".claude/skills/hoi4-3d-model-pipeline/references/live-authoring.md"
MAX_FINDINGS = 20

# Rule -> the repair that fixes it for free (`repair_unit.py --repairs <name>`).
REPAIRS = {
    "UNIT-WINDING": "winding",
    "UNIT-INSIDE-OUT": "winding",
    "UNIT-BRIDGE": "bridges",
    "UNIT-HOLE": "holes",
    "UNIT-SEAM": "weights",
    "UNIT-ANIM-GROUND": "ground",
    # Most stretch comes from fused parts and hard weight seams; when it stays after these, it escalates.
    "UNIT-ANIM-STRETCH": "bridges weights",
}
# Rules no script fixes: the motion or the rig needs authoring.
ESCALATE = {
    "UNIT-ANIM-KNEE": "a knee bends backward: solve the leg again with the knee toward the toes",
    "UNIT-ANIM-STILL": "a clip barely moves: author a clip that reads as its role",
    "UNIT-ANIM-SAME": "two roles play the same motion: give one its own clip",
    "UNIT-ANIM-SHARED": "the unit plays another unit's clip: give it its own clip, or declare it a reskin",
    "UNIT-ROLE-MISSING": "a role has no clip",
    "UNIT-ANIM-STATIC": "a clip moves nothing",
    "UNIT-ANIM-FPS": "a clip is not at 30 fps: export it again with the kit (run_pilot.py's export step, or live_helpers.export_clip in a live session), which retimes it to 30 and keeps its length in seconds",
    "UNIT-NORMALS": "corner normals point against their faces and shade as pale flat facets: flip those normals, or recalculate them on a welded copy (the winding repair keeps imported normals)",
    "UNIT-UNSKINNED": "the mesh has no skeleton",
    "UNIT-LOOSE-PART": "a loose part floats or drifts off the body: bind it to the bone it rests on with the job's loose_part_edits and rerun the job (free), or weight it by hand",
}
TEXTURE_RULES = {"UNIT-DDS-MIPS", "UNIT-DDS-FORMAT", "UNIT-DDS-EMISSIVE"}


def verdict(
    stage: str,
    ok: bool,
    unit: str,
    *,
    outputs: Optional[Dict[str, Any]] = None,
    sheets: Sequence[str] = (),
    checklist: Optional[str] = None,
    findings: Sequence[Dict[str, str]] = (),
    escalate: Optional[Dict[str, Any]] = None,
    next_steps: Sequence[str] = (),
    **extra: Any,
) -> Dict[str, Any]:
    """The verdict dictionary. `extra` keys (a Meshy task id, credits) are kept as they are."""

    state = "pass" if ok else ("escalate" if escalate else "fail")
    payload: Dict[str, Any] = {
        "schema": SCHEMA,
        "stage": stage,
        "ok": bool(ok),
        "verdict": state,
        "unit": unit,
        "outputs": outputs or {},
        "sheets": [str(sheet) for sheet in sheets],
        "checklist": checklist,
        "findings": list(findings)[:MAX_FINDINGS],
        "findings_total": len(findings),
        "escalate": escalate,
        "next": list(next_steps),
    }
    payload.update(extra)
    return payload


def write(payload: Dict[str, Any], path: Optional[Path]) -> None:
    """Write the verdict to `path` (when given) and print it as one compact line."""

    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload, separators=(",", ":")))


def quote(path: str) -> str:
    """A path as a shell argument: quoted when it holds a space."""

    return f'"{path}"' if any(ch.isspace() for ch in path) else path


def short(message: str) -> str:
    """The first clause of a finding's message, for the verdict."""

    first = message.split("; ")[0]
    return first if len(first) <= 200 else first[:197] + "..."


def next_for_findings(
    rules: Iterable[str],
    folder: str,
    out: str,
    stem: Optional[str] = None,
    unit_type: Optional[str] = None,
    repaired: bool = False,
) -> tuple[List[str], Optional[Dict[str, Any]]]:
    """The commands that fix the failed rules, and an escalation when a rule has no scripted fix.

    `repaired` says the unit already went through `repair_unit.py`: stretch that stays escalates.
    """

    rules = set(rules)
    folder, out = quote(folder), out.rstrip("/")
    steps: List[str] = []
    stem_arg = f" --stem {stem}" if stem else ""
    type_arg = f" --unit-type {unit_type}" if unit_type else ""
    repairs: List[str] = []
    for rule in sorted(rules):
        for name in REPAIRS.get(rule, "").split():
            if name not in repairs:
                repairs.append(name)
    order = ["winding", "bridges", "holes", "weights", "ground"]
    repairs.sort(key=order.index)
    escalating = {rule: ESCALATE[rule] for rule in rules if rule in ESCALATE}
    if repaired and "UNIT-ANIM-STRETCH" in rules:
        escalating["UNIT-ANIM-STRETCH"] = "stretch stays after the free repair: re-weight by hand or author the clip again"
        repairs = [name for name in repairs if name not in ("bridges", "weights")]
    if rules & TEXTURE_RULES:
        steps.append(f"{PY} {PIPELINE}/check_unit_files.py {folder}{stem_arg}{type_arg} --repair-textures")
    if repairs:
        steps.append(f"{PY} {PIPELINE}/repair_unit.py {folder}{stem_arg}{type_arg} --out {quote(out + '/repair')} --repairs {' '.join(repairs)}")
        steps.append(f"{PY} {PIPELINE}/check_unit_files.py {quote(out + '/repair/files')}{stem_arg}{type_arg} --verdict {quote(out + '/check_after_repair.json')}")
    if any(rule.startswith("UNIT-REG-") for rule in rules):
        steps.append("Fix the registration the findings name (.gfx, .asset, entity, sub-unit sprite), then check again with --mod-root.")
    escalation = None
    if escalating:
        escalation = {
            "rules": sorted(escalating),
            "why": sorted(set(escalating.values())),
            "how": f"Author the named clips live in Blender ({LIVE_GUIDE}), or ask the user before ordering a paid clip.",
        }
    return steps, escalation
