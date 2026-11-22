"""Survey vanilla's unit and building effects: which particles each kind of model fires, at which locator (and the bone it follows), in which
entity states and at which moment. Writes `config/effects_vanilla.json`, the data behind the reference table in `docs/3d-effects.md`.

    py -3.13 -B .tools/3d_pipeline/calibrate_effects.py [--game <folder>] [--out config/effects_vanilla.json]

What it reads, all from the installed game:

- every `entity` in `gfx/entities/*.asset`, its `pdxmesh` and the `event` lines of its states (`time`, `node`, `particle`, `sound`);
- the `pdxmesh` registrations in `gfx/**/*.gfx`, to open each entity's `.mesh` and read which bone each locator (`node`) is parented to;
- the `pdxparticle` registrations (`name` to `type`) and the particle files under `gfx/particles` (`particle = { name = <type> }`), to name
  the `.asset` file each particle comes from;
- the destroyed landmarks' `destroy` clips, to measure the unit of an event's `time`: the frame at which a bone's scale drops (a part is
  hidden as it blows up) against the time of the state's first particle event.

Run it again after a game update. Nothing here is guessed: a locator whose mesh could not be read is recorded with `bone: null`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from lib import pdx_binary, pdx_deform, pdx_script

KIT_ROOT = HERE.parents[1]
OUT = HERE / "config" / "effects_vanilla.json"

# Entity file -> kind of model. Files not listed (trees, map items, weather, nukes, test entities) carry no unit or building effects.
KIND_OF_FILE = {
    "units_infantry.asset": "infantry",
    "units_army_headquarters.asset": "infantry",
    "units_cavalry.asset": "cavalry",
    "units_artillery.asset": "artillery",
    "units_howitzers.asset": "artillery",
    "units_railway_guns.asset": "artillery",
    "units_tanks.asset": "tank",
    "units_flame_tanks.asset": "tank",
    "units_armored_engineering_vehicles.asset": "tank",
    "units_command_vehicles.asset": "tank",
    "units_land_cruisers.asset": "tank",
    "units_vehicles.asset": "vehicle",
    "units_planes.asset": "plane",
    "units_helicopters.asset": "plane",
    "units_ships.asset": "ship",
    "_units_battleships_DLC.asset": "ship",
    "_units_heavy_cruisers_DLC.asset": "ship",
    "buildings.asset": "building",
    "MTG_buildings.asset": "building",
    "landmarks.asset": "landmark",
}
KINDS = ("infantry", "cavalry", "artillery", "tank", "vehicle", "plane", "ship", "building", "landmark")
MESHES_PER_NODE = 6  # meshes opened to find a locator's bone, per (kind, node)


def game_dir(given: Optional[str]) -> Path:
    if given:
        return Path(given)
    import importlib.util

    spec = importlib.util.spec_from_file_location("kit_game_locator", KIT_ROOT / ".tools" / "lib" / "game.py")
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    found = module.game_dir()
    if not found:
        raise SystemExit("the game folder was not found; pass --game")
    return Path(found)


def read_script(path: Path) -> List[Tuple[str, Any]]:
    return pdx_script.parse(path.read_text(encoding="utf-8", errors="replace"))


def mesh_files(game: Path) -> Dict[str, str]:
    """pdxmesh name -> its `.mesh` file, relative to the game folder."""

    found: Dict[str, str] = {}
    for gfx in sorted((game / "gfx").rglob("*.gfx")):
        for key, block in read_script(gfx):
            if key != "objectTypes" or not isinstance(block, list):
                continue
            for name, entry in block:
                if name == "pdxmesh" and isinstance(entry, list):
                    mesh, file = pdx_script.get(entry, "name"), pdx_script.get(entry, "file")
                    if isinstance(mesh, str) and isinstance(file, str):
                        found.setdefault(mesh, file.replace("\\", "/"))
    return found


def particle_sources(game: Path) -> Dict[str, Dict[str, Any]]:
    """Registered particle name -> {type, scale, file}: the `pdxparticle` entries and the `.asset` file that defines each type."""

    type_file: Dict[str, str] = {}
    for asset in sorted((game / "gfx" / "particles").rglob("*.asset")):
        for key, block in read_script(asset):
            if key == "particle" and isinstance(block, list):
                name = pdx_script.get(block, "name")
                if isinstance(name, str):
                    type_file.setdefault(name, asset.relative_to(game).as_posix())
    registered: Dict[str, Dict[str, Any]] = {}
    for gfx in sorted((game / "gfx").rglob("*.gfx")):
        for key, block in read_script(gfx):
            if key != "objectTypes" or not isinstance(block, list):
                continue
            for name, entry in block:
                if name != "pdxparticle" or not isinstance(entry, list):
                    continue
                particle, kind = pdx_script.get(entry, "name"), pdx_script.get(entry, "type")
                if isinstance(particle, str) and isinstance(kind, str):
                    scale = pdx_script.get(entry, "scale")
                    registered.setdefault(particle, {"type": kind, "scale": _number(scale, 1.0), "file": type_file.get(kind),
                                                     "registered_in": gfx.relative_to(game).as_posix()})
    return registered


def _number(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def entity_events(game: Path) -> List[Dict[str, Any]]:
    """One row per particle event of every entity in the listed files."""

    rows: List[Dict[str, Any]] = []
    for path in sorted((game / "gfx" / "entities").glob("*.asset")):
        kind = KIND_OF_FILE.get(path.name)
        if not kind:
            continue
        for key, block in read_script(path):
            if key != "entity" or not isinstance(block, list):
                continue
            entity = pdx_script.get(block, "name")
            mesh = pdx_script.get(block, "pdxmesh")
            for state in pdx_script.get_all(block, "state"):
                if not isinstance(state, list):
                    continue
                state_name = pdx_script.get(state, "name")
                speed = _number(pdx_script.get(state, "animation_speed"), 1.0)
                for event in pdx_script.get_all(state, "event"):
                    if not isinstance(event, list):
                        continue
                    particle = pdx_script.get(event, "particle")
                    if not isinstance(particle, str):
                        continue
                    sound = pdx_script.get(event, "sound")
                    rows.append({
                        "kind": kind, "file": path.name, "entity": entity, "mesh": mesh if isinstance(mesh, str) else None,
                        "state": state_name, "animation_speed": speed, "time": _number(pdx_script.get(event, "time"), 0.0),
                        "node": pdx_script.get(event, "node"), "particle": particle,
                        "keep_particle": pdx_script.get(event, "keep_particle") == "yes",
                        "trigger_once": pdx_script.get(event, "trigger_once") == "yes",
                        "sound": pdx_script.get(sound, "soundeffect") if isinstance(sound, list) else None,
                    })
    return rows


def locator_bones(game: Path, path: str) -> Dict[str, Optional[str]]:
    try:
        root = pdx_binary.read(game / path)
    except Exception:  # noqa: BLE001 - an unreadable mesh only leaves its locators' bones unknown
        return {}
    locators = root.child("locator")
    out: Dict[str, Optional[str]] = {}
    for node in (locators.children if locators else []):
        parent = node.properties.get("pa")
        out[node.name] = str(parent[0]) if parent else None
    return out


def time_unit(game: Path, meshes: Dict[str, str], rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """For each destroyed landmark: the frame at which a bone's scale first drops below half against its first particle event's time."""

    out = []
    seen = set()
    for row in rows:
        if row["kind"] != "landmark" or row["state"] != "destroy" or row["entity"] in seen or not row["mesh"]:
            continue
        seen.add(row["entity"])
        mesh = meshes.get(row["mesh"])
        if not mesh:
            continue
        anim = game / mesh.replace(".mesh", "_destroy.anim")
        if not anim.is_file():
            continue
        clip = pdx_deform.load_anim(anim)
        drop = None
        for joint, channel in clip.channels.items():
            below = [f for f in range(clip.frames) if channel["s"][f] < 0.5 * channel["s"][0]]
            if below and (drop is None or below[0] < drop[1]):
                drop = (joint, below[0])
        first = min(r["time"] for r in rows if r["entity"] == row["entity"] and r["state"] == "destroy")
        if drop:
            out.append({"entity": row["entity"], "anim": anim.relative_to(game).as_posix(), "fps": round(clip.fps, 3),
                        "animation_speed": row["animation_speed"], "hidden_bone": drop[0], "hide_frame": drop[1],
                        "hide_seconds": round(drop[1] / clip.fps, 3), "first_event_time": first})
    return out


def summarize(rows: List[Dict[str, Any]], game: Path, meshes: Dict[str, str], particles: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    by_kind: Dict[str, Dict[Tuple[str, str], Dict[str, Any]]] = {kind: {} for kind in KINDS}
    mesh_cache: Dict[str, Dict[str, Optional[str]]] = {}
    opened: Dict[Tuple[str, str], int] = defaultdict(int)
    for row in rows:
        key = (row["particle"], row["node"] or "")
        entry = by_kind[row["kind"]].setdefault(key, {
            "particle": row["particle"], "node": row["node"], "bones": set(), "states": set(), "times": set(), "entities": set(),
            "sounds": set(), "keep_particle": set(), "trigger_once": set(),
        })
        entry["states"].add(row["state"])
        entry["times"].add(row["time"])
        entry["entities"].add(row["entity"])
        entry["keep_particle"].add(row["keep_particle"])
        entry["trigger_once"].add(row["trigger_once"])
        if row["sound"]:
            entry["sounds"].add(row["sound"])
        mesh = meshes.get(row["mesh"] or "")
        if row["node"] and mesh and opened[(row["kind"], row["node"])] < MESHES_PER_NODE:
            if mesh not in mesh_cache:
                mesh_cache[mesh] = locator_bones(game, mesh)
                opened[(row["kind"], row["node"])] += 1
            if row["node"] in mesh_cache[mesh]:
                entry["bones"].add(mesh_cache[mesh][row["node"]] or "(none)")
    out: Dict[str, Any] = {}
    for kind, entries in by_kind.items():
        listed = []
        for entry in sorted(entries.values(), key=lambda e: (-len(e["entities"]), e["particle"], e["node"] or "")):
            source = particles.get(entry["particle"], {})
            listed.append({
                "particle": entry["particle"], "node": entry["node"], "bones": sorted(entry["bones"]),
                "states": sorted(s for s in entry["states"] if s), "times": sorted(entry["times"]), "entities": len(entry["entities"]),
                "example": sorted(e for e in entry["entities"] if e)[0] if any(entry["entities"]) else None,
                "sounds": sorted(entry["sounds"]), "keep_particle": sorted(entry["keep_particle"]), "trigger_once": sorted(entry["trigger_once"]),
                "file": source.get("file"), "scale": source.get("scale"),
            })
        out[kind] = listed
    return out


DOC = KIT_ROOT / "docs" / "3d-effects.md"
BEGIN, END = "<!-- calibrate_effects begin -->", "<!-- calibrate_effects end -->"
ROWS_PER_KIND = 8


def table(data: Dict[str, Any]) -> str:
    """The reference table of the docs: the most used particle events of each kind, from the survey."""

    lines = ["| Kind | Particle | Locator (bone) | States | Time (s) | Entities | File |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for kind in KINDS:
        rows = data["kinds"].get(kind) or []
        if not rows:
            lines.append(f"| {kind} | none | | | | 0 | |")
            continue
        for row in rows[:ROWS_PER_KIND]:
            bones = ", ".join(b for b in row["bones"] if b != "(none)") or "none"
            times = ", ".join(f"{t:g}" for t in row["times"][:4]) + (" ..." if len(row["times"]) > 4 else "")
            states = ", ".join(row["states"][:4]) + (" ..." if len(row["states"]) > 4 else "")
            lines.append(f"| {kind} | `{row['particle']}` | {row['node'] or 'none'} ({bones}) | {states} | {times} | {row['entities']} | "
                         f"`{(row['file'] or '').replace('gfx/particles/', '')}` |")
    return "\n".join(lines)


def write_doc(path: Path, data: Dict[str, Any]) -> bool:
    """Replace the table between the markers in the docs. False when the doc has no markers."""

    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if BEGIN not in text or END not in text:
        return False
    head, rest = text.split(BEGIN, 1)
    _old, tail = rest.split(END, 1)
    path.write_text(f"{head}{BEGIN}\n{table(data)}\n{END}{tail}", encoding="utf-8", newline="\n")
    return True


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--game", help="the game folder (found by the kit when left out)")
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--doc", default=str(DOC), help="the docs page whose reference table is rewritten")
    args = parser.parse_args(argv)
    game = game_dir(args.game)
    meshes = mesh_files(game)
    particles = particle_sources(game)
    rows = entity_events(game)
    fired = {row["particle"] for row in rows}
    data = {
        "about": "Vanilla's particle events by kind of model, written by calibrate_effects.py from the installed game. Each row is one particle at one "
                 "locator: the bones the locator is parented to in the entities' meshes, the states that fire it, the times, how many entities do, "
                 "and the .asset file that defines it. particles lists every registered vanilla particle, and whether a unit or building fires it. time_unit compares each destroyed landmark's first particle event with the frame its clip "
                 "hides a part: the event's time is the clip's own seconds (frame / fps), whatever the state's animation_speed.",
        "game_version": _game_version(game),
        "time_unit": time_unit(game, meshes, rows),
        "kinds": summarize(rows, game, meshes, particles),
        "particles": {name: dict(particles[name], fired_by_units=name in fired) for name in sorted(particles)},
    }
    Path(args.out).write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(rows)} particle events in {len({r['entity'] for r in rows})} entities, wrote {args.out}")
    if write_doc(Path(args.doc), data):
        print(f"rewrote the reference table in {args.doc}")
    for row in data["time_unit"]:
        print(f"time unit: {row['entity']} hides {row['hidden_bone']} at frame {row['hide_frame']} ({row['hide_seconds']} s), first event at time {row['first_event_time']}")
    return 0


def _game_version(game: Path) -> Optional[str]:
    launcher = game / "launcher-settings.json"
    try:
        return json.loads(launcher.read_text(encoding="utf-8")).get("rawVersion")
    except Exception:  # noqa: BLE001
        return None


if __name__ == "__main__":
    raise SystemExit(main())
