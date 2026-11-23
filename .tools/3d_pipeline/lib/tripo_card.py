"""The Tripo card a job gets, and the armed unit's grip commands, from the job entry alone.

A small model follows the card as written, so the card comes from the job entry by rule instead of being copied by hand:
`tripo/make_card.py` fills `tripo/CARD_TEMPLATE.md` and keeps only the blocks the job needs (an armed unit gets the weapon picture,
the weapon model and the grip step, an unarmed unit does not), and `tripo/arm_unit.py` runs the grip stage with the same file names.
Both refuse a job that would leave a step open. The gaps a Sonnet run of the hobgoblin found in the hand-copied card (2026-11-22)
are the reasons for each rule below.

- An armed unit names the hand that holds the weapon by the rig's side (`tripo.weapon.hand`, `LeftHand` or `RightHand`). The picture is
  a front view, so a weapon on the viewer's right is in the character's left hand, the rig's `LeftHand`. Every tool defaults to
  `RightHand`, so a job that leaves it out silently grips the wrong hand.
- The weapon and the shield are their own Tripo models. Their files have fixed names in the job folder's `armed` folder, and the body's
  Tripo export goes there too: the inbox gets the gripped body only, as `<slug>__rigged.glb`, the one file the intake reads.
- The card records the kit commit it was written from, so a run that pulls a newer kit mid-way can tell which card it follows.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Sequence

HANDS = ("LeftHand", "RightHand")
OTHER_HAND = {"LeftHand": "RightHand", "RightHand": "LeftHand"}
# Unit types whose fighters hold a weapon (config/unit_types.json): a job of one of them needs `tripo.weapon`.
ARMED_TYPES = ("infantry_melee", "spearman", "heavy_brute")
ROLES = ("idle", "move", "attack", "defend", "retreat", "death")
# The roles that keep the weapon held up, the one whose hold fades as the blow starts, and the one that lets go of it.
HOLD_ROLES = ("idle", "move", "defend", "retreat")
FADE_ROLE = "attack"
DROP_ROLE = "death"
WEAPON_PART = "tripo_part_1"
WEAPON_BONE = "Weapon"
# Optional grip numbers a job may set in `tripo.weapon.grip_options` (or `tripo.shield.grip_options`), with the stage option each one sets.
WEAPON_OPTIONS = {"grip": "--grip", "length_ratio": "--length-ratio", "roll": "--roll", "head_toward": "--head-toward",
                  "hold_hand": "--hold-hand", "hold_axis": "--hold-axis"}
SHIELD_OPTIONS = {"height_share": "--height-share", "roll": "--roll", "head_toward": "--head-toward", "hold_hand": "--hold-hand",
                  "hold_axis": "--hold-axis"}

HAND_MESSAGE = (
    "tripo.weapon.hand must be \"LeftHand\" or \"RightHand\", named by the rig's side, not the viewer's. The picture is a front view, "
    "so a weapon on the viewer's right is in the character's left hand: \"LeftHand\". A weapon on the viewer's left is \"RightHand\"."
)

# The card's picture sentence starts with this unless the preset gives its own start (a building asks for a small yard and thick bracing).
DEFAULT_PICTURE_PREFIX = "Redraw this exact <subject> for 3D modelling. Keep <every detail>. Invent nothing."

BLOCK = re.compile(r"<!-- (armed|unarmed|shield|tripo_rig|kit_rig|static|model|unit|winged) -->\n(.*?)<!-- /\1 -->\n", re.S)


def job_entry(config: Path, slug: str) -> Dict[str, Any]:
    """One job's entry in a `3d_jobs.json`."""

    import json

    payload = json.loads(Path(config).read_text(encoding="utf-8"))
    jobs = payload.get("jobs", payload.get("pilots")) or {}
    if slug not in jobs:
        raise KeyError(f"{config} has no job {slug!r}. It has: {', '.join(sorted(jobs)) or 'none'}")
    return jobs[slug]


def preset_of(spec: Dict[str, Any]) -> Dict[str, Any]:
    """The job's preset (`config/tripo_presets.json`): its own `preset`, else the one its unit type or kind belongs to."""

    from lib import tripo_presets

    name = tripo_presets.for_job(spec)
    if name is None:
        raise ValueError("the job fits no Tripo preset: set \"preset\" to one of " + ", ".join(tripo_presets.names()))
    return {"name": name, **tripo_presets.get(name)}


def paid_prompt(preset: Dict[str, Any], armed: bool) -> str:
    """The made clip's prompt: the preset's own for a unit with empty hands where it has one (a large creature smashes with its fists)."""

    paid = preset.get("paid_clip") or {}
    return paid.get("prompt", "") if armed or not paid.get("prompt_unarmed") else paid["prompt_unarmed"]


def static_folder(kind: str) -> str:
    """Where `tripo/static_model.py` writes a static model of this kind inside its mod tree."""


    path = Path(__file__).resolve().parents[1] / "tripo" / "static_model.py"
    source = path.read_text(encoding="utf-8")
    # Read the FOLDERS table without importing the stage, which needs numpy and Pillow.
    match = re.search(r"^FOLDERS = (\{.*?\})\n", source, re.S | re.M)
    if not match:
        raise ValueError("tripo/static_model.py has no FOLDERS table")
    import ast

    return ast.literal_eval(match.group(1))[kind]


def route_of(spec: Dict[str, Any]) -> str:
    return preset_of(spec)["route"]


def is_armed(spec: Dict[str, Any]) -> bool:
    return bool((spec.get("tripo") or {}).get("weapon"))


def is_winged(spec: Dict[str, Any]) -> bool:
    """A Tripo-rigged job (a winged humanoid) whose anatomy has wings or whose `tripo.chains` names the wings region. A winged quadruped is
    rigged by the kit and has its own wing rules."""

    try:
        if route_of(spec) != "tripo_rig":
            return False
    except (KeyError, ValueError):
        return False
    chains = (spec.get("tripo") or {}).get("chains") or []
    return bool((spec.get("anatomy") or {}).get("wings")) or any(isinstance(c, dict) and c.get("region") == "wings" for c in chains)


def wing_problems(spec: Dict[str, Any]) -> List[str]:
    """A winged job needs the wings chains: Tripo's humanoid rig has no wing bones."""

    chains = (spec.get("tripo") or {}).get("chains") or []
    if is_winged(spec) and not any(isinstance(c, dict) and c.get("region") == "wings" for c in chains):
        return ["the anatomy has wings, so tripo.chains needs {\"region\": \"wings\"}: Tripo's humanoid rig has no wing bones, and without "
                "the chains the membrane follows the arms (docs/3d-units.md, Secondary chains)"]
    return []


# A burn death (lib/tripo_burn.py) plays a standing reaction, not a fall: the route burns the body away where it stands.
BURN_DEATH_CLIPS = ["hit_to_stomach"]


def clip_candidates(spec: Dict[str, Any], preset: Dict[str, Any]) -> Dict[str, Any]:
    """The preset with its death candidates swapped for a standing reaction when the job's death burns (`tripo.death_kind` `burn`)."""

    if (spec.get("tripo") or {}).get("death_kind") != "burn":
        return preset
    return {**preset, "clips": {**preset["clips"], "death": list(BURN_DEATH_CLIPS)}}


def held_by_others(spec: Dict[str, Any]) -> Dict[str, str]:
    """The clips another unit type of the job's mod holds (D-136), {export name: that unit}. Empty outside a mod repository."""

    from lib import anim_claims

    registry = anim_claims.registry_for(spec)
    if registry is None or not registry.exists():
        return {}
    data = anim_claims.load(registry)
    family = anim_claims._family(unit_slug(spec), spec.get("reskin_of"), data)
    return {clip: owner["unit"] for clip, owner in anim_claims.holders(registry).items() if owner["unit"] not in family}


def has_shield(spec: Dict[str, Any]) -> bool:
    return isinstance((spec.get("tripo") or {}).get("shield"), dict)


def weapon_hand(spec: Dict[str, Any]) -> str:
    """The hand that holds the weapon, by the rig's side. Refuses a job that does not name one."""

    hand = ((spec.get("tripo") or {}).get("weapon") or {}).get("hand")
    if hand not in HANDS:
        raise ValueError(HAND_MESSAGE + f" The job has {hand!r}.")
    return hand


def problems(spec: Dict[str, Any]) -> List[str]:
    """What the job entry must still say before a card can be written from it. Empty when it is ready."""

    found: List[str] = []
    if str(spec.get("provider") or "").lower() != "tripo":
        found.append("provider must be \"tripo\"")
    sources = spec.get("reference_sources") or []
    if isinstance(sources, str):
        sources = [sources]
    if not [item for item in sources if isinstance(item, str) and item.strip()]:
        found.append("reference_sources is empty: list the subject's own reference (the owner's drawing or the mod's art) and, for a "
                     "real-world subject, the real references research found. The picture is made from them, never from a text prompt alone")
    unit_type = spec.get("unit_type")
    block = spec.get("tripo") or {}
    route = _preset_problems(spec, found)
    if unit_type and unit_type in ARMED_TYPES and not is_armed(spec):
        found.append(f"unit_type {unit_type} holds a weapon, so the job needs tripo.weapon (an unarmed unit takes infantry_unarmed or beast_biped)")
    found += wing_problems(spec)
    if is_armed(spec):
        found += _weapon_problems(block["weapon"])
    if has_shield(spec):
        if not is_armed(spec):
            found.append("a shield goes in the free hand of an armed unit: the job needs tripo.weapon too")
        elif block["shield"].get("hand", OTHER_HAND.get(block["weapon"].get("hand"))) != OTHER_HAND.get(block["weapon"].get("hand")):
            found.append("tripo.shield.hand must be the other hand than tripo.weapon.hand")
    if unit_type and route == "tripo_rig" and block.get("posture") not in ("upright", "hunched"):
        found.append("tripo.posture must be \"upright\" or \"hunched\" (see the card's clip choice step)")
    return found


def _preset_problems(spec: Dict[str, Any], found: List[str]) -> str | None:
    """Add what the job lacks for its preset to `found`, and return the preset's route (None when no preset fits)."""

    from lib import tripo_presets

    try:
        name = tripo_presets.for_job(spec)
    except KeyError as error:
        found.append(str(error).strip("'\""))
        return None
    if name is None:
        found.append("the job fits no Tripo preset: set \"preset\" to one of " + ", ".join(tripo_presets.names())
                     + " (tripo/new_job.py writes a job from a preset)")
        return None
    preset = tripo_presets.get(name)
    if preset["route"] == "static" and spec.get("model_kind") != preset["model_kind"]:
        found.append(f"the preset {name} makes a {preset['model_kind']}: set model_kind to \"{preset['model_kind']}\"")
    if preset["route"] != "static" and not spec.get("unit_type"):
        found.append(f"the preset {name} is a unit: set unit_type (the preset's is \"{preset['unit_type']}\")")
    unfitting = tripo_presets.unfitting_clips(spec)
    if unfitting:
        found.append(tripo_presets.unfitting_message(unfitting))
    found.extend(tripo_presets.renamed_tile_clips(spec).values())
    from lib import anim_claims

    shared = anim_claims.job_conflicts(spec, unit_slug(spec))
    if shared:
        found.append(anim_claims.conflict_message(shared))
    return preset["route"]


def unit_slug(spec: Dict[str, Any]) -> str:
    """The job's name in its mod: the part of `asset_id` after the last dot."""

    return str(spec.get("asset_id") or "").rsplit(".", 1)[-1]


def _weapon_problems(weapon: Dict[str, Any]) -> List[str]:
    found: List[str] = []
    if weapon.get("hand") not in HANDS:
        found.append(HAND_MESSAGE)
    if weapon.get("part", WEAPON_PART) != WEAPON_PART or weapon.get("bone", WEAPON_BONE) != WEAPON_BONE:
        found.append(f"tripo.weapon for a separately modelled weapon is part {WEAPON_PART} on bone {WEAPON_BONE}, the names the grip stage gives it")
    options = weapon.get("grip_options") or {}
    for key, meaning in (("length_ratio", "the weapon's length over the body's height, read from the art (the grip stage scales the weapon "
                                          "to it, and its default of 1.06 makes a short weapon as long as the body is tall)"),
                         ("grip", "where the hand holds the weapon, as a share of its length from the butt, read from the art")):
        if not isinstance(options.get(key), (int, float)):
            found.append(f"tripo.weapon.grip_options.{key}: {meaning}")
    if not str(weapon.get("name") or "").strip():
        found.append("tripo.weapon.name names the weapon as the picture shows it, for example \"wooden mallet\": the card's weapon steps use it")
    return found


def armed_files(job_root: Path, slug: str) -> Dict[str, Path]:
    """Where an armed unit's Tripo exports go, and where the grip stage writes the body the intake reads."""

    armed = Path(job_root) / "armed"
    return {
        "body": armed / f"{slug}__body.glb",
        "weapon": armed / f"{slug}_weapon__model.glb",
        "shield": armed / f"{slug}_shield__model.glb",
        "gripped": armed / f"{slug}__gripped.glb",
        "rigged": Path(job_root) / "inbox" / f"{slug}__rigged.glb",
        "grip_report": Path(job_root) / "evidence" / "grip_report.json",
        "shield_report": Path(job_root) / "evidence" / "shield_report.json",
    }


def role_clips(spec: Dict[str, Any], clip_names: Sequence[str]) -> Dict[str, str]:
    """Each role's clip as the stages take it, from the job's `tripo.roles` (an exact name or its first words), checked to name exactly
    one clip of the export. The stages take the names as a comma separated list and resolve each by its first words themselves, so
    the job's own words are passed, never the full export name: Tripo names a made clip after its prompt, which may hold a comma
    ("A small goblin stands ready, the axe held low"), and a full name with a comma would split in two. A role that names a clip
    with a comma is refused: give the words before the first comma."""

    from lib.tripo import resolve_clip_name

    roles = (spec.get("tripo") or {}).get("roles") or {}
    missing = [role for role in ROLES if not roles.get(role)]
    if missing:
        raise ValueError(f"tripo.roles lacks {', '.join(missing)}: pick a clip for every role first (the card's clip choice step)")
    found = {}
    for role in ROLES:
        if "," in roles[role]:
            raise ValueError(f"tripo.roles.{role} {roles[role]!r} holds a comma: give only the clip's first words, before the first comma")
        resolve_clip_name(roles[role], clip_names)  # refuses a name that matches no clip, or more than one
        found[role] = roles[role]
    return found


def _options(block: Dict[str, Any], table: Dict[str, str]) -> List[str]:
    out: List[str] = []
    for key, value in (block.get("grip_options") or {}).items():
        if key not in table:
            raise ValueError(f"unknown grip option {key!r}: use one of {', '.join(sorted(table))}")
        if isinstance(value, (list, tuple)):
            value = ",".join(str(v) for v in value)
        out += [table[key], str(value)]
    return out


def grip_command(spec: Dict[str, Any], files: Dict[str, Path], clips: Dict[str, str], blender: str, stage: Path) -> List[str]:
    """The grip stage's command line (tripo/grip_weapon.py): the job's hand, the hold in idle, move, defend and retreat, the hold that
    fades as the attack starts, the drop at the death's fall, the clearance in every role, and the weapon on its own bone."""

    weapon = spec["tripo"]["weapon"]
    held = [clips[role] for role in HOLD_ROLES]
    out = files["gripped"] if has_shield(spec) else files["rigged"]
    return [
        blender, "-b", "--factory-startup", "--python-exit-code", "1", "--python", str(stage), "--",
        str(files["body"]), str(files["weapon"]), "--out", str(out), "--report", str(files["grip_report"]),
        "--hand", weapon_hand(spec), "--weapon-bone",
        "--hold-clips", ",".join(held), "--hold-fade-clips", clips[FADE_ROLE], "--release-clips", clips[DROP_ROLE],
        "--clearance-clips", ",".join(clips[role] for role in ROLES),
        *_options(weapon, WEAPON_OPTIONS),
    ]


def shield_command(spec: Dict[str, Any], files: Dict[str, Path], clips: Dict[str, str], blender: str, stage: Path) -> List[str]:
    """The shield stage's command line (tripo/shield_stage.py) on the gripped body: the free hand, the same holds and the same drop."""

    shield = spec["tripo"]["shield"]
    return [
        blender, "-b", "--factory-startup", "--python-exit-code", "1", "--python", str(stage), "--",
        str(files["gripped"]), str(files["shield"]), "--out", str(files["rigged"]), "--report", str(files["shield_report"]),
        "--hand", OTHER_HAND[weapon_hand(spec)],
        "--hold-clips", ",".join(clips[role] for role in HOLD_ROLES), "--hold-fade-clips", clips[FADE_ROLE],
        "--release-clips", clips[DROP_ROLE], "--clearance-clips", ",".join(clips[role] for role in ROLES),
        *_options(shield, SHIELD_OPTIONS),
    ]


def keep_blocks(text: str, spec: Dict[str, Any]) -> str:
    """Keep the template's blocks the job needs and drop the others: `armed`, `unarmed` and `shield` by the weapon, and by the preset's
    route `tripo_rig` (Tripo rigs and animates), `kit_rig` (a plain model the kit rigs), `static`, `model` (an HD Model, any route but
    static) and `unit` (any route but static)."""

    route = route_of(spec)
    wanted = {"armed": is_armed(spec), "unarmed": not is_armed(spec), "shield": has_shield(spec), "tripo_rig": route == "tripo_rig",
              "kit_rig": route == "kit_rig", "static": route == "static", "model": route != "static", "unit": route != "static",
              "winged": is_winged(spec)}
    # Blocks nest (an armed block inside the Tripo rig's steps), so resolve the outer ones first and repeat until none is left.
    while True:
        kept = BLOCK.sub(lambda match: match.group(2) if wanted[match.group(1)] else "", text)
        if kept == text:
            return text
        text = kept


def fill(template: str, spec: Dict[str, Any], slug: str, *, job_folder: str, kit_commit: str) -> str:
    """The card for one job: the template's blocks for the job, every placeholder filled."""

    problems_found = problems(spec)
    if problems_found:
        raise ValueError("The job entry is not ready for a card:\n- " + "\n- ".join(problems_found))
    from lib import tripo_presets

    block = spec.get("tripo") or {}
    preset = preset_of(spec)
    sources = spec["reference_sources"]
    sources = [sources] if isinstance(sources, str) else sources
    # The preset's values go first: some of them hold placeholders of their own (the armed attack prompt names <weapon>).
    values = {
        "<clip table>": tripo_presets.clip_table(clip_candidates(spec, preset), held_by_others(spec)) if preset["route"] == "tripo_rig" else "",
        "<paid clip>": paid_prompt(preset, is_armed(spec)),
        "<paid clip when>": (preset.get("paid_clip") or {}).get("when", "only when step 6 says no attack passes"),
        "<free attacks>": " ".join(tripo_presets.free_attacks(preset, is_armed(spec))),
        "<picture sentence>": " ".join([preset["picture"].get("sentence_prefix") or DEFAULT_PICTURE_PREFIX, preset["picture"]["pose"]]),
        "<picture rules>": "\n".join(f"- {rule}" for rule in preset["picture"].get("rules") or []),
        "<preset>": preset["name"],
        "<preset label>": preset["label"],
        "<preset proven>": preset["proven"],
        "<preset budget>": tripo_presets.budget_line(preset),
        "<canvas>": tripo_presets.canvas_line(preset, armed=is_armed(spec)),
    }
    if preset["route"] == "static":
        values.update({"<model_kind>": preset["model_kind"], "<static folder>": static_folder(preset["model_kind"]),
                       **tripo_presets.polycount(preset)})
    values.update({
        "<asset_slug>": slug,
        "<runtime_stem>": str(spec.get("runtime_stem") or "<runtime_stem>"),
        "<kit commit>": kit_commit,
        "<picture>": f"{job_folder}/{spec.get('reference_path', 'refs/original/<picture>.png')}",
        "<sources>": "<br>".join(str(item).strip() for item in sources if str(item).strip()),
        "<unit_type>": str(spec.get("unit_type") or f"static model, {spec.get('model_kind')}"),
        "<posture>": str(block.get("posture") or "none (static model)"),
        "<credit_budget>": str(spec.get("credit_budget", "")),
        "<job folder>": job_folder,
    })
    if is_armed(spec):
        hand = weapon_hand(spec)
        values.update({
            "<hand>": hand,
            "<viewer side>": "right" if hand == "LeftHand" else "left",
            "<hand words>": "left hand" if hand == "LeftHand" else "right hand",
            "<free hand>": OTHER_HAND[hand],
            "<weapon>": str(block["weapon"]["name"]).strip(),
        })
        if has_shield(spec):
            values["<shield>"] = str(block["shield"].get("name") or "shield").strip()
    text = keep_blocks(template, spec)
    for key, value in values.items():
        text = text.replace(key, value)
    # A unit with no fitting free attack checks only its earlier made clips (D-127).
    return text.replace("--attack  <earlier clips>", "--attack <earlier clips>")
