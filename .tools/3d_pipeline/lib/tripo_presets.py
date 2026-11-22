"""The Tripo presets of `config/tripo_presets.json`: one per kind of model a modder can make (D-120).

A preset holds what is Tripo-specific for its type and points at the kit's other files for the rest, so nothing is copied:

- the unit type (`unit_type`) is a key of `config/unit_types.json`, which names the body (`config/body_presets.json`), the rig and,
  for a type the kit rigs itself, the Blender clips;
- a static model's kind (`model_kind`) is a key of `config/static_kinds.json`, which holds its size, triangle budget and clips;
- the Canvas workflow (`canvas`) is a key of `config/tripo_canvas_workflows.json`.

`check()` refuses a preset that points at something missing, so a renamed unit type or kind fails the tests instead of a modder's run.
`tripo/new_job.py` writes a job entry from a preset and `tripo/make_card.py` writes the card from the job and its preset.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CONFIG = Path(__file__).resolve().parents[1] / "config"
PRESETS = CONFIG / "tripo_presets.json"
WORKFLOWS = CONFIG / "tripo_canvas_workflows.json"
ROUTES = ("tripo_rig", "kit_rig", "static")
ROLES = ("idle", "move", "attack", "defend", "retreat", "death")
WEAPON_STEPS = ("weapon_picture", "weapon_model")
REQUIRED = ("label", "for", "route", "picture", "tripo_steps", "checks", "expected_credits", "cap", "canvas", "proven")


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load(path: Path = PRESETS) -> Dict[str, Any]:
    return _load(path)


def names(data: Optional[Dict[str, Any]] = None) -> List[str]:
    return list((data or load())["presets"])


def get(name: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = data or load()
    presets = data["presets"]
    if name not in presets:
        raise KeyError(f"no Tripo preset {name!r}. The presets are: {', '.join(presets)}")
    return presets[name]


def check(data: Optional[Dict[str, Any]] = None, *, config: Path = CONFIG) -> List[str]:
    """Every way the presets disagree with the kit's other files. Empty when they agree."""

    data = data or load(config / PRESETS.name)
    refs = {
        "unit_types": _load(config / "unit_types.json")["types"],
        "bodies": _load(config / "body_presets.json")["presets"],
        "kinds": _load(config / "static_kinds.json")["kinds"],
        "workflows": _load(config / WORKFLOWS.name)["workflows"] if (config / WORKFLOWS.name).exists() else {},
        "effects": _load(config / "effects.json")["profiles"] if (config / "effects.json").exists() else {},
    }
    found: List[str] = []
    for name, preset in data["presets"].items():
        where = f"preset {name}"
        found += [f"{where} lacks {key}" for key in REQUIRED if key not in preset]
        route = preset.get("route")
        if route not in ROUTES:
            found.append(f"{where}: route {route!r} is not one of {', '.join(ROUTES)}")
            continue
        found += [f"{where}: {item}" for item in _reference_problems(preset, refs)]
        found += [f"{where}: {item}" for item in _step_problems(preset, data)]
    return found


def _reference_problems(preset: Dict[str, Any], refs: Dict[str, Dict[str, Any]]) -> List[str]:
    """The unit type, body, static kind and Canvas workflow a preset names must exist in their own files."""

    found: List[str] = []
    if preset["route"] == "static":
        if preset.get("model_kind") not in refs["kinds"]:
            found.append(f"model_kind {preset.get('model_kind')!r} is not a kind of static_kinds.json")
    else:
        unit_types, bodies = refs["unit_types"], refs["bodies"]
        for unit_type in [preset.get("unit_type"), *(preset.get("unit_types") or []), preset.get("unarmed_unit_type")]:
            if unit_type is not None and unit_type not in unit_types:
                found.append(f"unit type {unit_type!r} is not in unit_types.json")
        body = (unit_types.get(preset.get("unit_type")) or {}).get("body")
        if body is not None and body not in bodies:
            found.append(f"its unit type's body {body!r} is not in body_presets.json")
        found += [f"anatomy_changes names {key!r}, which the body {body} has no answer for"
                  for key in (preset.get("anatomy_changes") or {}) if body in bodies and key not in bodies[body]["anatomy"]]
    found += [f"effect profile {name!r} is not in effects.json" for name in preset.get("effects", []) if refs["effects"] and name not in refs["effects"]]
    if refs["workflows"] and preset.get("canvas") not in refs["workflows"]:
        found.append(f"Canvas workflow {preset.get('canvas')!r} is not in {WORKFLOWS.name}")
    return found


def _step_problems(preset: Dict[str, Any], data: Dict[str, Any]) -> List[str]:
    """The Tripo steps exist, a Tripo-rigged type has a rig and clips for every role, and the steps' price stays within the cap."""

    route = preset["route"]
    steps = preset.get("tripo_steps") or []
    found = [f"Tripo step {step!r} is not in steps" for step in steps if step not in data["steps"]]
    if route == "tripo_rig":
        clips = preset.get("clips") or {}
        missing = [role for role in ROLES if not clips.get(role)]
        if missing:
            found.append(f"no clip candidates for {', '.join(missing)}")
        if "auto_rig" not in steps:
            found.append("a Tripo-rigged type needs the auto_rig step")
        found += [f"the {role} candidate {clip!r} never fits a unit (D-127)" for role, clip in _unfitting_candidates(preset, data)]
    elif preset.get("clips"):
        found.append(f"a {route} type takes its clips from the kit, so it lists none")
    low, high = (preset.get("expected_credits") or [0, 0])
    if not low <= high <= preset.get("cap", 0):
        found.append(f"expected credits {low} to {high} must stay within the cap {preset.get('cap')}")
    prices = data["prices"]
    cost = sum(prices[price_of(step)]["credits"] for step in steps if price_of(step) in prices and step not in WEAPON_STEPS)
    if cost > high:
        found.append(f"its steps cost {cost}, more than the expected {high}")
    return found


def _unfitting_candidates(preset: Dict[str, Any], data: Dict[str, Any]) -> List[Tuple[str, str]]:
    import fnmatch

    patterns = never_fitting(preset, data)
    found = []
    for role, clips in (preset.get("clips") or {}).items():
        for clip in clips:
            # A candidate is a preset name, or a sentence naming one in backticks (`chop` (with a weapon only)).
            names = re.findall(r"`([^`]+)`", clip) or ([clip] if " " not in clip else [])
            found += [(role, name) for name in names if any(fnmatch.fnmatch(name.lower(), pattern) for pattern in patterns)]
    return found


def free_attacks(preset: Dict[str, Any], armed: bool) -> List[str]:
    """The free library attacks the card's step 6 checks: the preset names in the attack candidates, without one marked for a weapon
    when the unit has empty hands."""

    found = []
    for clip in (preset.get("clips") or {}).get("attack") or []:
        names = re.findall(r"`([^`]+)`", clip) or ([clip] if " " not in clip else [])
        if names and "with a weapon only" in clip and not armed:
            continue
        found += names
    return found


def never_fitting(preset: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> List[str]:
    """The name patterns of clips that never fit (D-127): the shared list and the preset's own."""

    data = data or load()
    preset = preset or {}
    own = [*(preset.get("never_fitting") or []), *((preset.get("never_fits") or {}).get("clips") or [])]
    return [*data.get("never_fitting", {}).get("patterns", []), *[item.lower() for item in own]]


def unfitting_clips(spec: Dict[str, Any], data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """The job's role clips whose names match a never-fitting pattern, {role: clip}. Empty when every clip may fit (D-127)."""

    import fnmatch

    data = data or load()
    name = for_job(spec, data)
    patterns = never_fitting(data["presets"].get(name) if name else None, data)
    roles = (spec.get("tripo") or {}).get("roles") or {}
    return {role: clip for role, clip in roles.items() if isinstance(clip, str)
            and any(fnmatch.fnmatch(clip.strip().lower().replace(" ", "_"), pattern) for pattern in patterns)}


def unfitting_message(found: Dict[str, str]) -> str:
    listed = ", ".join(f"{role} {clip!r}" for role, clip in found.items())
    return (f"these clips do not fit the unit (D-127: every clip fits its era, its weapon and its kind of creature, no modern boxing, kicks "
            f"or dance, even when a free preset passes the checks): {listed}. Pick a fitting clip from the card's table, or make one "
            f"that fits")


def price_of(step: str) -> str:
    """The price entry a Tripo step is charged by."""

    return {"weapon_picture": "picture", "weapon_model": "hd_model", "preset_clips": "preset_clip", "export_rigged": "export",
            "export_model": "export"}.get(step, step)


def for_job(spec: Dict[str, Any], data: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """The preset a job follows: its own `preset`, else the one whose unit type or kind it has. None when no preset fits."""

    data = data or load()
    if spec.get("preset"):
        get(spec["preset"], data)
        return spec["preset"]
    unit_type, kind = spec.get("unit_type"), spec.get("model_kind")
    wings = bool((spec.get("anatomy") or {}).get("wings")) or any(
        (chain or {}).get("region") == "wings" for chain in (spec.get("tripo") or {}).get("chains") or [])
    if kind:
        return next((name for name, preset in data["presets"].items() if preset.get("model_kind") == kind), None)
    if not unit_type:
        return None
    # Presets of the unit type. Where several share it (an armed humanoid and a winged one), wings decide: a preset that adds wings
    # takes a winged job, the others an unwinged one. A type with one preset (a dragon's winged_quadruped) takes it whatever the anatomy.
    fitting = [name for name, preset in data["presets"].items() if preset.get("route") != "static"
               and unit_type in [preset.get("unit_type"), *(preset.get("unit_types") or []), preset.get("unarmed_unit_type")]]
    exact = [name for name in fitting if wings == bool((data["presets"][name].get("anatomy_changes") or {}).get("wings"))]
    return (exact or fitting or [None])[0]


def steps_for(preset: Dict[str, Any], armed: bool) -> List[str]:
    return [step for step in preset["tripo_steps"] if armed or step not in WEAPON_STEPS]


def new_job(name: str, answers: Dict[str, Any], data: Optional[Dict[str, Any]] = None, *, config: Path = CONFIG) -> Dict[str, Any]:
    """A job entry from a preset: its defaults, the body's anatomy with the preset's changes, the cap as the budget, then the answers.

    `answers` holds what only the modder knows: the picture and its sources, the posture, the weapon (name, hand, grip), the size.
    Keys with a dot (`weapon.hand`) go into the `tripo` block. The result still has to pass `tripo_card.problems`."""

    data = data or load(config / PRESETS.name)
    preset = get(name, data)
    job: Dict[str, Any] = {"provider": "tripo", "preset": name, "credit_budget": preset["cap"]}
    job.update(copy.deepcopy(preset.get("job") or {}))
    job.setdefault("tripo", {})
    if preset["route"] == "static":
        job["model_kind"] = preset["model_kind"]
    else:
        unit_types = _load(config / "unit_types.json")["types"]
        bodies = _load(config / "body_presets.json")["presets"]
        armed = answers.get("armed", preset.get("armed") is True)
        unit_type = preset["unit_type"] if armed or not preset.get("unarmed_unit_type") else preset["unarmed_unit_type"]
        if preset.get("armed") == "optional" and armed and unit_type == "infantry_unarmed":
            unit_type = "infantry_melee"
        job["unit_type"] = answers.get("unit_type", unit_type)
        body = unit_types[job["unit_type"]].get("body")
        if body in bodies:
            anatomy = dict(bodies[body]["anatomy"])
            anatomy.update(preset.get("anatomy_changes") or {})
            if "tail" in answers:
                anatomy["tail"] = bool(answers["tail"])
            job["anatomy"] = anatomy
        if not armed:
            job["tripo"].pop("weapon", None)
        elif preset.get("armed") == "optional":
            job["tripo"].setdefault("weapon", {"part": "tripo_part_1", "bone": "Weapon", "source": "rigged", "release_roles": ["death"]})
    return apply_answers(job, {key: value for key, value in answers.items() if key not in ("armed", "unit_type", "tail")})


TRIPO_KEYS = ("posture", "idle_pose", "roles", "weapon", "shield", "chains", "load")


def apply_answers(job: Dict[str, Any], answers: Dict[str, Any]) -> Dict[str, Any]:
    """Write answers into a job entry. `posture` and keys with a dot (`weapon.hand`) go into the `tripo` block, the rest at the top."""

    for key, value in answers.items():
        parts = key.split(".")
        if parts[0] in TRIPO_KEYS:
            target = job.setdefault("tripo", {})
        else:
            target = job
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = value
    return job


def clip_table(preset: Dict[str, Any]) -> str:
    """The card's table of free candidates per role, from the preset."""

    rows = ["| Role | Candidates |", "| --- | --- |"]
    for role in ROLES:
        cells = [f"`{clip}`" if " " not in clip else clip for clip in preset["clips"][role]]
        rows.append(f"| {role} | {', '.join(cells)} |")
    return "\n".join(rows)


def polycount(preset: Dict[str, Any], *, config: Path = CONFIG) -> Dict[str, str]:
    """A static model's Smart Mesh polycount: the preset's own, with its reason, else the kind's vanilla triangle budget."""

    if preset.get("polycount"):
        return {"<polycount>": f"{preset['polycount']:,}", "<polycount reason>": preset.get("polycount_reason", "")}
    budget = _load(config / "static_kinds.json")["kinds"][preset["model_kind"]]["triangle_budget"]
    return {"<polycount>": f"{budget['value']:,}",
            "<polycount reason>": f"vanilla's most detailed {preset['model_kind']} has {budget['value']:,} triangles, from `config/static_kinds.json`"}


def canvas_name(preset: Dict[str, Any], armed: bool) -> str:
    """The Canvas workflow a job follows: an armed preset's job with empty hands (a large creature without a weapon) takes the rigged one."""

    return "rigged_unit" if preset["canvas"] == "armed_unit" and not armed else preset["canvas"]


def canvas_line(preset: Dict[str, Any], *, armed: bool = False, config: Path = CONFIG) -> str:
    """The card's line about the type's Agentic Canvas workflow: its name, its price against the page and its link when shared."""

    path = config / WORKFLOWS.name
    if not path.exists():
        return "none yet"
    workflows = _load(path)
    flow = workflows["workflows"].get(canvas_name(preset, armed))
    if not flow:
        return "none yet"
    link = (workflows.get("links") or {}).get(preset.get("name") or "") or flow.get("link")
    where = f"[{flow['title']}]({link})" if link else f"{flow['title']}, built from `docs/3d-canvas.md` (no shared link yet)"
    if flow.get("extra_credits") is None:
        return f"{where}, its node prices not read yet: read each node before you run it"
    return f"{where}, {flow['extra_credits']} more credits than the card for the same model"


def budget_line(preset: Dict[str, Any]) -> str:
    low, high = preset["expected_credits"]
    expected = f"{low}" if low == high else f"{low} to {high}"
    line = f"expected {expected}, cap {preset['cap']}"
    if preset.get("cap_note"):
        line += f". {preset['cap_note']}"
    return line
