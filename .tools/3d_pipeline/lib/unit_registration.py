"""Write the registration a finished unit needs, as text the parent pastes or generates.

The layout follows a wiring that loads in the game: the `pdxmesh` block (with
`meshsettings` and one animation id per entity state) in a `.gfx` file, the
`animation` blocks in an `.asset` file next to the model, and the entity in
`gfx/entities/*.asset`. A mounted unit mirrors vanilla `units_cavalry.asset`:
the unit entity shows the mount and attaches the rider entity to the mount's
`Saddle_Node`. The worker never edits these files in a mod; it hands this text
over in `runtime/registration.md`.
"""

from __future__ import annotations

from typing import Dict, List, Optional

STATE_TO_ROLE = {
    "idle": "idle",
    "move": "move",
    "move_snow": "move",
    "move_mud": "move",
    "attack": "attack",
    "defend": "defend",
    "support_attack": "attack",
    "retreat": "retreat",
    "training": "idle",
    "death": "death",
}
# The states each vanilla entity family declares [vanilla-confirmed 1.19.4.1]: units_infantry.asset,
# units_cavalry.asset (no death state) and units_tanks.asset (move_snow and move_mud, no death state).
STATE_SETS = {
    "infantry": ["idle", "move", "attack", "defend", "support_attack", "retreat", "training", "death"],
    "cavalry": ["idle", "move", "attack", "support_attack", "defend", "retreat", "training"],
    "armor": ["idle", "move", "move_snow", "move_mud", "retreat", "attack", "defend", "support_attack", "training"],
}
NON_LOOPING = {"attack", "death"}


def pdxmesh_block(stem: str, model_folder: str, shape_names: List[str], roles: List[str], states: Optional[List[str]] = None) -> str:
    lines = ["\tpdxmesh = {", f'\t\tname = "{stem}_mesh"', f'\t\tfile = "{model_folder}/{stem}.mesh"']
    for index, shape in enumerate(shape_names):
        lines += [
            "\t\tmeshsettings = {",
            f'\t\t\tname = "{shape}"',
            f"\t\t\tindex = {index}",
            f'\t\t\ttexture_diffuse = "{stem}_diffuse.dds"',
            f'\t\t\ttexture_normal = "{stem}_normal.dds"',
            f'\t\t\ttexture_specular = "{stem}_specular.dds"',
            '\t\t\tshader = "PdxMeshAdvanced"',
            "\t\t}",
        ]
    for state, role in STATE_TO_ROLE.items():
        if role in roles:
            lines.append(f'\t\tanimation = {{ id = "{state}" type = "{stem}_{role}_animation" }}')
    lines.append("\t}")
    return "\n".join(lines)


def animation_blocks(stem: str, roles: List[str]) -> str:
    return "\n".join(
        f'animation = {{\n\tname = "{stem}_{role}_animation"\n\tfile = "{stem}_{role}.anim"\n}}' for role in roles
    )


def entity_block(
    name: str,
    stem: str,
    roles: List[str],
    scale: float,
    attach: Optional[Dict[str, str]] = None,
    move_sound: str = "",
    states: Optional[List[str]] = None,
) -> str:
    lines = ["entity = {", f'\tname = "{name}"', f'\tpdxmesh = "{stem}_mesh"', '\tdefault_state = "idle"']
    for state in states or STATE_SETS["infantry"]:
        role = STATE_TO_ROLE[state]
        if role not in roles:
            continue
        extra = " looping = no" if role in NON_LOOPING else ""
        if state == "attack":
            extra += ' next_state = "attack"'
        blend = 0.2 if role == "attack" else 0.3
        line = f'\tstate = {{ name = "{state}" animation = "{state}" animation_blend_time = {blend} animation_speed = 1.0{extra}'
        if state == "move" and move_sound:
            lines += [line, f'\t\tevent = {{ sound = {{ soundeffect = "{move_sound}" }} }}', "\t}"]
        else:
            lines.append(line + " }")
    for node, target in (attach or {}).items():
        lines.append(f'\tattach = {{ name = "{target.removesuffix("_entity")}" {node} = "{target}" }}')
    lines += [f"\tscale = {scale:g}", "}"]
    return "\n".join(lines)


def registration_text(
    *,
    unit_entity: str,
    model_folder: str,
    stem: str,
    shapes: List[str],
    roles: List[str],
    scale: float,
    template: str,
    rider: Optional[Dict[str, object]] = None,
    move_sound: str = "",
    state_set: str = "infantry",
) -> str:
    """Markdown with the three blocks to wire one unit; a mount also wires its rider."""

    parts = [
        f"# Registration for {unit_entity}",
        "",
        "Paste or generate these blocks. The sub-unit's `sprite` must be the entity name without `_entity`.",
        "",
        f"## `.gfx` (for example `gfx/entities/<mod>_units.gfx`, inside `objectTypes = {{ }}`)",
        "",
        "```",
        pdxmesh_block(stem, model_folder, shapes, roles, STATE_SETS[state_set]),
    ]
    if rider:
        parts.append(pdxmesh_block(str(rider["stem"]), str(rider["model_folder"]), list(rider["shapes"]), list(rider["roles"]), STATE_SETS[state_set]))  # type: ignore[arg-type]
    parts += ["```", "", f"## `{model_folder}/{stem}.asset`", "", "```", animation_blocks(stem, roles), "```"]
    if rider:
        parts += ["", f"## `{rider['model_folder']}/{rider['stem']}.asset`", "", "```", animation_blocks(str(rider["stem"]), list(rider["roles"])), "```"]  # type: ignore[arg-type]
    parts += ["", "## Entities (`gfx/entities/<mod>_units.asset`)", "", "```"]
    if template == "mount" and rider:
        rider_entity = f"{rider['stem']}_entity"
        parts.append(entity_block(unit_entity, stem, roles, scale, attach={"Saddle_Node": rider_entity}, move_sound=move_sound, states=STATE_SETS[state_set]))
        parts.append("")
        parts.append(entity_block(rider_entity, str(rider["stem"]), list(rider["roles"]), float(rider.get("scale", 1.0)), states=STATE_SETS[state_set]))  # type: ignore[arg-type]
    else:
        parts.append(entity_block(unit_entity, stem, roles, scale, move_sound=move_sound, states=STATE_SETS[state_set]))
    parts += [
        "```",
        "",
        "Then run, from the mod root:",
        "",
        "```",
        f"py -3.13 -B .tools/3d_pipeline/check_unit_files.py {model_folder} --mod-root .",
        "py -3.13 -B .tools/audits/audit_asset_wiring_static.py --paths gfx interface common/units",
        "```",
    ]
    return "\n".join(parts) + "\n"
