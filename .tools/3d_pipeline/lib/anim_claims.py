"""Which unit of a mod holds which clip (D-136, 3D-6): every distinct unit type of a mod has its own animations.

A clip, a free Tripo preset or a made one, belongs to one unit type of a mod. Only a reskin or a variant of the same people shares a
set (its job's `reskin_of` names the unit it reskins). The record is one JSON file in the mod, `<mod root>/.hoi4_3d/anim_claims.json`,
committed with the mod so every worker and machine sees the same claims:

    {"schema_version": "1.0.0", "claims": [{"clip": "hit_to_stomach", "unit": "beast", "role": "defend", "source": "free preset",
                                            "time": "2026-11-22T18:40:00Z"}, ...]}

A claim is written under a lock (a directory made beside the file, which is atomic), after reading the file again inside the lock,
so two workers who claim at once never both win: the earliest claim holds the clip. `check` is the route's UNIT-ANIM-SHARED: it fails a
job whose role clips another unit of the mod holds, before any Blender step, not only when the finished files are compared.

The record never ships with the mod: `.hoi4_3d/` is a development folder like `.tools/` and `.claude/`, which the game ignores and which
stays out of a Workshop upload. A job's `anim_registry` (or the command's `--registry`) keeps the record outside the mod instead, as a
.json path.

A clip is named as the export names it (Tripo exports the tile `defeat` as `defeat_02` and `defeat_02` as `defeat_03`), lower case,
spaces as underscores. A made clip is named by its text, as the job's `tripo.roles` names it.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

REGISTRY = Path(".hoi4_3d") / "anim_claims.json"
# Tripo exports two preset tiles under the next tile's name.
EXPORT_NAMES = {"defeat": "defeat_02", "defeat_02": "defeat_03"}
LOCK_WAIT = 30.0


class ClaimError(ValueError):
    pass


def clip_key(name: str) -> str:
    return "_".join(str(name).strip().lower().split())


def export_name(tile: str) -> str:
    """The clip name a preset tile exports under."""

    return EXPORT_NAMES.get(clip_key(tile), clip_key(tile))


def mod_root(spec: Dict[str, Any], jobs_config: Optional[Path] = None) -> Optional[Path]:
    """The mod the job belongs to: its `mod_root` (relative to the jobs file), else the git repository that holds the jobs file."""

    base = Path(jobs_config).resolve().parent if jobs_config else Path.cwd()
    if spec.get("mod_root"):
        root = Path(spec["mod_root"])
        return (root if root.is_absolute() else base / root).resolve()
    try:
        out = subprocess.run(["git", "-C", str(base), "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        top = out.stdout.strip() if isinstance(out.stdout, str) else ""
    except (OSError, subprocess.CalledProcessError, TypeError, ValueError):
        return None
    return Path(top).resolve() if top else None


def registry_path(root: Path) -> Path:
    """The registry file: `root` itself when it names a .json file (a registry kept outside the mod), else the mod's own."""

    root = Path(root)
    return root if root.suffix.lower() == ".json" else root / REGISTRY


def registry_for(spec: Dict[str, Any], jobs_config: Optional[Path] = None) -> Optional[Path]:
    """The job's registry: its `anim_registry` (a .json path, relative to the jobs file), else the mod's `.hoi4_3d/anim_claims.json`."""

    if spec.get("anim_registry"):
        path = Path(spec["anim_registry"])
        base = Path(jobs_config).resolve().parent if jobs_config else Path.cwd()
        return (path if path.is_absolute() else base / path).resolve()
    root = mod_root(spec, jobs_config)
    return registry_path(root) if root else None


def load(root: Path) -> Dict[str, Any]:
    path = registry_path(root)
    if not path.exists():
        return {"schema_version": "1.0.0", "claims": []}
    return json.loads(path.read_text(encoding="utf-8"))


def holders(root: Path) -> Dict[str, Dict[str, Any]]:
    """Each clip's earliest claim: {clip: claim}."""

    found: Dict[str, Dict[str, Any]] = {}
    for claim in load(root).get("claims", []):
        found.setdefault(clip_key(claim["clip"]), claim)
    return found


def _family(unit: str, reskin_of: Optional[str], data: Dict[str, Any]) -> set:
    """The unit and the units that share its set: the unit it reskins, and every reskin of that base unit."""

    base = reskin_of or unit
    return {unit, base} | {item["unit"] for item in data.get("claims", []) if item.get("reskin_of") == base}


def unit_key(name: str) -> str:
    """A unit named as a job slug: lower case, spaces as underscores, a note in brackets left out."""

    return clip_key(str(name).split(" (")[0])


class _Lock:
    def __init__(self, path: Path, wait: float = LOCK_WAIT):
        self.dir = Path(str(path) + ".lock")
        self.wait = wait

    def __enter__(self):
        self.dir.parent.mkdir(parents=True, exist_ok=True)
        start = time.monotonic()
        while True:
            try:
                os.mkdir(self.dir)
                return self
            except FileExistsError as error:
                if time.monotonic() - start > self.wait:
                    raise ClaimError(f"{self.dir} is held by another claim for over {self.wait:.0f} s: try again") from error
                time.sleep(0.1)

    def __exit__(self, *exc):
        try:
            os.rmdir(self.dir)
        except OSError:
            pass


def claim(root: Path, unit: str, clips: Dict[str, str], *, source: str = "", reskin_of: Optional[str] = None,
          time_stamp: Optional[str] = None) -> Dict[str, Any]:
    """Claim the clips {role: clip} for `unit` in the mod. Returns {"claimed": [...], "already": [...], "held": {clip: holder}}.

    Nothing is written when any clip is held by another unit outside the unit's reskin family: the caller picks another clip or
    makes one, then claims again."""

    path = registry_path(root)
    stamp = time_stamp or _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    with _Lock(path):
        data = load(root)
        family = _family(unit, reskin_of, data)
        first = {}
        for item in data["claims"]:
            first.setdefault(clip_key(item["clip"]), item)
        held = {}
        already = []
        new = []
        for role, clip in clips.items():
            key = clip_key(clip)
            owner = first.get(key)
            if owner and owner["unit"] not in family:
                held[key] = owner
            elif owner:
                already.append(key)
            else:
                entry = {"clip": key, "unit": unit, "role": role, "source": source, "time": stamp}
                if reskin_of:
                    entry["reskin_of"] = reskin_of
                new.append(entry)
                first[key] = entry
        if held:
            return {"claimed": [], "already": already, "held": held}
        if new:
            data["claims"].extend(new)
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".json.tmp")
            tmp.write_bytes((json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
            os.replace(tmp, path)
        return {"claimed": [entry["clip"] for entry in new], "already": already, "held": {}}


def release(root: Path, unit: str, clip: str) -> Dict[str, Any]:
    """Give back `unit`'s claim on `clip`, for a clip that failed its checks after the claim. Returns {"released": clip, "now_held_by":
    the next claim of that clip or None}.

    Refuses (ClaimError) when `unit` holds no claim on the clip, or when another unit claimed it first: only the holder gives a clip
    back, so a worker never frees a clip another unit type uses."""

    path = registry_path(root)
    key = clip_key(clip)
    with _Lock(path):
        data = load(root)
        mine = [item for item in data["claims"] if clip_key(item["clip"]) == key and item["unit"] == unit]
        if not mine:
            raise ClaimError(f"{unit} holds no claim on {key} in {path}: nothing to release")
        first = next(item for item in data["claims"] if clip_key(item["clip"]) == key)
        if first["unit"] != unit:
            raise ClaimError(f"{key} is held by {first['unit']} (claimed {first.get('time', '')}), not by {unit}: only the holder releases it")
        data["claims"] = [item for item in data["claims"] if not (clip_key(item["clip"]) == key and item["unit"] == unit)]
        tmp = path.with_suffix(".json.tmp")
        tmp.write_bytes((json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        os.replace(tmp, path)
        after = next((item["unit"] for item in data["claims"] if clip_key(item["clip"]) == key), None)
        return {"released": key, "now_held_by": after}


def conflicts(root: Path, unit: str, clips: Iterable[str], reskin_of: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """UNIT-ANIM-SHARED in the route: the clips another unit of the mod, outside the unit's reskin family, already holds."""

    data = load(root)
    family = _family(unit, reskin_of, data)
    first = holders(root)
    return {clip_key(c): first[clip_key(c)] for c in clips if clip_key(c) in first and first[clip_key(c)]["unit"] not in family}


def job_conflicts(spec: Dict[str, Any], unit: str, jobs_config: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    roles = (spec.get("tripo") or {}).get("roles") or {}
    if not roles:
        return {}
    registry = registry_for(spec, jobs_config)
    if registry is None or not registry.exists():
        return {}
    return conflicts(registry, unit, roles.values(), spec.get("reskin_of"))


def conflict_message(found: Dict[str, Dict[str, Any]]) -> str:
    listed = ", ".join(f"{clip} (held by {owner['unit']} for {owner.get('role', '?')})" for clip, owner in found.items())
    return (f"UNIT-ANIM-SHARED: another unit type of this mod already holds {listed}. Every distinct unit type has its own animations "
            f"(D-136): pick another fitting clip, or make one, then claim it with tripo/anim_claims.py. A reskin of that unit sets "
            f"`reskin_of` in its job")


def import_markdown(root: Path, text: str, mod: str) -> Dict[str, Any]:
    """Seed the registry from a hand-kept claims table (| Mod | Unit | State | Clip | Source | Worker | Time |), rows of `mod` only,
    in the table's order, so its earliest row wins. Only rows whose clip cell names a preset (a single word) or a made clip's text
    are taken. Planned rows are left out."""

    taken = []
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 7 or cells[0] != mod or cells[1] in ("Unit type (subject)",) or set(cells[0]) <= {"-", " "}:
            continue
        unit, roles, clip, source = unit_key(cells[1]), cells[2], cells[3], cells[4]
        # Planned clips are not claims yet. Clips the kit makes in Blender on a unit's own rig never collide with a Tripo clip.
        if "planned" in source.lower() or clip.lower().startswith(("planned", "made:", "the kit")) or "blender" in source.lower()                 or "made by the kit" in source.lower():
            continue
        name = clip.split(" (")[0].strip()
        if not name:
            continue
        for role in [r.strip() for r in roles.split(",")]:
            result = claim(root, unit, {role: name}, source=source, time_stamp=cells[6])
            taken.append((unit, role, name, "held" if result["held"] else "ok"))
    return {"rows": taken}
