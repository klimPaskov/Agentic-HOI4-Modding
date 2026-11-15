"""Measure vanilla buildings, landmarks, ships, tanks and planes, to set the static-model route's contracts.

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/calibrate_static_kinds.py ["<HOI4 install>"] --out .tools/3d_pipeline/config/static_kinds.json

For each kind it reads a fixed set of vanilla models (`REFERENCES`) with `lib/pdx_binary.py` and
`lib/pdx_deform.py`, resolves their entity scale from `gfx/entities` and `gfx/models`, and writes what
`tripo/static_model.py` and the STATIC-* checks use, each with the files it came from:

- the size (the kind's main measure at runtime, the median over the set) and the entity scale;
- the triangle budget (the most detailed model of the set) and the texture size (the median);
- the shader, the specular level and the glossiness distribution of the set's specular maps;
- the `Collision` box (its share of the visible box), the bones, their rest places as a share of the visible box,
  and the locators of the kind's entity reference;
- the vanilla clip each role retargets, and the numbers of the split rules (turret, barrel, waterline).

Rerun after a game update. The game folder defaults to the one `.tools/lib/game.py` finds.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

PIPELINE = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE))

from lib import model_dds, pdx_binary, pdx_deform
from lib import static_kinds as sk

UNITS = "gfx/models/units"
# The vanilla models each kind is measured on. Destroyed variants, jets, trains and the one-section wall are left out:
# they are not what the kind's Tripo model replaces.
REFERENCES = {
    "vehicle": [f"{UNITS}/tanks/{tag}_tank_light.mesh" for tag in ("ENG", "FRA", "generic", "GER", "ITA", "JAP", "SOV", "USA")]
    + [f"{UNITS}/tanks/FIN_light_armor.mesh"],
    "plane": [f"{UNITS}/planes/{tag}_plane_light.mesh" for tag in ("ENG", "FRA", "GER", "ITA", "JAP", "SOV", "USA")]
    + [f"{UNITS}/planes/FIN_light_plane_0.mesh", f"{UNITS}/planes/FIN_light_plane_2.mesh", f"{UNITS}/planes/JAP_light_plane_1.mesh",
       f"{UNITS}/planes/JAP_light_plane_3.mesh", f"{UNITS}/planes/generic_plane_light.mesh"],
    "ship": [f"{UNITS}/ships/generic_destroyer.mesh"],
    "building": [f"gfx/models/buildings/facility_{name}.mesh" for name in ("land", "air", "naval", "nuclear")],
    "landmark": [f"gfx/models/buildings/landmarks/landmark_{name}.mesh" for name in (
        "big_ben", "bojnice_castle", "colosseum", "cristo_redentor", "eiffel_tower", "forbidden_city", "hagia_sophia",
        "hakko_ichiu", "hofburg_palace", "kremlin", "nanjing_presidential_palace", "national_diet", "prague_castle",
        "reichstag", "sadabad_complex", "statue_of_liberty", "taj_mahal", "tokyo_imperial_palace", "volkshalle")],
}
# The triangle budget and texture size: the most detailed vanilla model of the whole kind, not only of the size set
# (a destroyer is the size a ship is drawn at, but vanilla draws ships with up to the budget of its most detailed one).
# Destroyed variants, test meshes and one-triangle formation frames are left out.
BUDGET_GLOBS = {
    "vehicle": [f"{UNITS}/tanks/*.mesh"],
    "plane": [f"{UNITS}/planes/*.mesh"],
    "ship": [f"{UNITS}/ships/*.mesh"],
    "building": ["gfx/models/buildings/*.mesh"],
    "landmark": ["gfx/models/buildings/landmarks/*.mesh"],
}
BUDGET_SKIP = ("destroyed", "TEST_", "test_")
# A ship's waterline is measured over every vanilla ship with the two-bone contract, not only the size reference.
WATERLINE_REFERENCES = [f"{UNITS}/ships/generic_destroyer.mesh", f"{UNITS}/ships/support_ship.mesh", f"{UNITS}/ships/generic_freighter.mesh"]
# The model whose entity, skeleton, locators and clips the kind copies (the destroyer is the ship the size is measured
# for; the light tank's clips are the ones vanilla light tanks play; its death comes from a heavy tank, since light
# tanks have none).
ENTITY_REFERENCE = {
    "vehicle": f"{UNITS}/tanks/GER_tank_light.mesh",
    "plane": f"{UNITS}/planes/ENG_plane_light.mesh",
    "ship": f"{UNITS}/ships/generic_destroyer.mesh",
    "building": "gfx/models/buildings/facility_land.mesh",
    "landmark": None,  # the landmark nearest the median size
}
CLIPS = {
    "vehicle": {"idle": (f"{UNITS}/tanks/GER_tank_light.mesh", f"{UNITS}/tanks/GER_tank_light_idle.anim"),
                "move": (f"{UNITS}/tanks/GER_tank_light.mesh", f"{UNITS}/tanks/GER_tank_light_moving.anim"),
                "attack": (f"{UNITS}/tanks/GER_tank_light.mesh", f"{UNITS}/tanks/GER_tank_light_attack.anim"),
                "death": (f"{UNITS}/tanks/GER_tank_heavy.mesh", f"{UNITS}/tanks/GER_tank_heavy_death.anim")},
    "plane": {"idle": (f"{UNITS}/planes/ENG_plane_light.mesh", f"{UNITS}/planes/fighter_default_idle.anim")},
    "ship": {role: (f"{UNITS}/ships/generic_destroyer.mesh", f"{UNITS}/ships/generic_destroyer_{role}.anim") for role in ("idle", "attack", "defend", "death")},
    "building": {},
    "landmark": {},
}
# The skeleton each kind rebuilds (vanilla's names). A tank keeps vanilla's hull and gun bones; its wheels are not rebuilt
# (a Tripo tank has no separate wheels). A ship keeps vanilla's two-bone contract; a plane vanilla's root plus a propeller.
SKELETON = {
    "vehicle": ["root", "tank_base", "chassie", "turret", "barrel_base", "barrel_tip"],
    "plane": ["root"],
    "ship": ["root", "ship"],
    "building": [],
    "landmark": None,  # the majority of the set
}
# Bones a rigid part of the model follows wholly, and the part each is mounted on (STATIC-PART-GAP).
PARTS = {
    # A Tripo barrel is one tube: it follows vanilla's barrel_base, the outer tube. Vanilla's barrel_tip is an inner tube
    # that slides back into it on the shot (most of the barrel's length), so a one-piece barrel on it all but vanishes.
    "vehicle": {"body": "chassie", "turret": "turret", "barrel": "barrel_base"},
    "plane": {"body": "root", "propeller": "propeller"},
    "ship": {"body": "ship"},
    "landmark": {"body": "root"},
    "building": {},
}
MOUNTS = {"vehicle": {"turret": "chassie", "barrel_base": "turret"}, "plane": {"propeller": "root"}}
# Kit rules that vanilla cannot measure, each with its reason:
# - a rigid part may lift off its mount by 1 % of the main measure in a clip (half a pixel at game size);
# - a plane's propeller is looked for in the front fifth of the fuselage and ends where the disc narrows to 60 % of
#   its span (vanilla planes have no separate propeller part to measure);
# - a propeller turns 0.4 of a four-blade period a frame at most, so it never strobes backward, and at most 90 % of
#   the fastest vanilla air and naval joint (`deformation_calibration.json`, UNIT-ANIM-SPIN).
GAP_SHARE = 0.01
PROPELLER_RULE = {"search_share": 0.2, "width_threshold": 0.6, "source": "kit rule: vanilla planes have no separate propeller part"}


def _game_dir() -> Path:
    spec = importlib.util.spec_from_file_location("kit_game", PIPELINE.parent / "lib" / "game.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.game_dir()


def visible_points(mesh) -> np.ndarray:
    visible = ~mesh.collision if len(mesh.collision) else np.ones(len(mesh.positions), dtype=bool)
    return np.array([sk.to_blender(p) for p in mesh.positions[visible]])


def measure_mesh(game: Path, rel: str) -> dict:
    path = game / rel
    root = pdx_binary.read(path)
    summary = pdx_binary.summarize_mesh(root)
    mesh = pdx_deform.load_mesh(path)
    points = visible_points(mesh)
    low, high = points.min(axis=0), points.max(axis=0)
    shader_tris: Dict[str, int] = {}
    textures, most = {}, -1
    for stream in summary.streams:
        if stream.material_shader.lower() == "collision":
            continue
        shader_tris[stream.material_shader] = shader_tris.get(stream.material_shader, 0) + stream.triangles
        if stream.textures and stream.triangles > most:  # the body's maps, not a track strip's
            textures, most = stream.textures, stream.triangles
    collision = None
    if mesh.collision.any():
        box = np.array([sk.to_blender(p) for p in mesh.positions[mesh.collision]])
        names = [s.shape for s in summary.streams if s.material_shader.lower() == "collision"]
        collision = {"low": box.min(axis=0), "high": box.max(axis=0), "name": names[0] if names else "collisionShape"}
    heads = {name: sk.to_blender(head) for name, head in sk.bone_rest_heads(mesh).items()}
    parents = {name: (mesh.bones[p] if p >= 0 else None) for name, p in zip(mesh.bones, mesh.parents)}
    locators = []
    node = root.child("locator")
    for loc in (node.children if node is not None else []):
        p = loc.properties.get("p")
        parent = loc.properties.get("pa")
        if not p:
            continue
        local = sk.to_blender([float(v) for v in p])
        world = local + (heads.get(str(parent[0]), np.zeros(3)) if parent else 0)
        locators.append({"name": loc.name, "parent": str(parent[0]) if parent else None, "world": world})
    return {
        "rel": rel, "mesh": mesh, "points": points, "low": low, "high": high,
        "triangles": sum(s.triangles for s in summary.streams if s.material_shader.lower() != "collision"),
        "shaders": shader_tris, "textures": textures, "collision": collision, "bones": mesh.bones, "parents": parents,
        "heads": heads, "locators": locators, "skinned": mesh.skinned,
    }


def share_in_box(point, low, high) -> List[float]:
    span = np.maximum(np.asarray(high) - np.asarray(low), 1e-9)
    return [round(float(v), 4) for v in (np.asarray(point) - np.asarray(low)) / span]


def texture_stats(game: Path, measured: List[dict]) -> dict:
    """Largest diffuse size, and the specular maps' level (green) and glossiness (alpha) quantiles, averaged."""

    sizes, levels, quantiles, files = [], [], [], []
    for entry in measured:
        folder = (game / entry["rel"]).parent
        diffuse, specular = entry["textures"].get("diff"), entry["textures"].get("spec")
        if diffuse and (folder / diffuse).is_file():
            sizes.append(int(model_dds.read_header((folder / diffuse).read_bytes())["width"]))
        if specular and (folder / specular).is_file():
            try:
                pixels = model_dds.decode_top_level((folder / specular).read_bytes())
            except (ValueError, model_dds.DdsError):
                continue
            levels.append(float(np.median(pixels[..., 1])))
            alpha = pixels[..., 3].ravel().astype(float)
            quantiles.append(np.percentile(alpha, np.arange(101)))
            files.append(f"{(folder / specular).relative_to(game).as_posix()}")
    return {
        # the most detailed model's size, like the triangle budget: a generated atlas needs every texel vanilla allows
        "texture_size": int(max(sizes)) if sizes else 1024,
        "specular_level": int(round(float(np.median(levels)))) if levels else 32,
        "gloss_quantiles": [round(float(v), 2) for v in np.mean(quantiles, axis=0)] if quantiles else None,
        "texture_sources": files,
    }


def clip_entry(game: Path, mesh_rel: str, anim_rel: str) -> dict:
    anim = pdx_deform.load_anim(game / anim_rel)
    return {"mesh": mesh_rel, "anim": anim_rel, "fps": round(anim.fps, 4), "frames": anim.frames, "seconds": round((anim.frames - 1) / anim.fps, 3)}


def _width(points: np.ndarray, chosen: np.ndarray) -> float:
    return float(np.percentile(points[chosen, 0], 99) - np.percentile(points[chosen, 0], 1))


def vehicle_rules(game: Path, measured: List[dict]) -> dict:
    """The turret and barrel split thresholds, from vanilla's skinning: which vertices follow the turret, the barrel, the hull."""

    turret_shares, bottom_shares, barrel_shares, sources, turret_heights, barrel_lengths = [], [], [], [], [], []
    labelled = []
    for entry in measured:
        mesh = entry["mesh"]
        points, labels = labelled_samples(mesh)
        height = float(np.ptp(points[:, 2]))
        hull, turret = labels == "chassie", labels == "turret"
        barrel = np.isin(labels, ["barrel_base", "barrel_tip"])
        if hull.sum() < 200 or turret.sum() < 200:
            continue
        # the rule's own measure: the plan area of each height slice (sk.slice_areas), hull band against the slices
        # that are mostly turret
        edges = np.linspace(points[:, 2].min(), points[:, 2].max(), sk.SLICES + 1)
        areas = sk.slice_areas(points, edges, CELL_SHARE * float(np.ptp(points[:, 1])))
        bottom = float((np.percentile(points[turret, 2], 2) - points[:, 2].min()) / height)
        band = areas[max(int(0.75 * bottom * sk.SLICES) // 2, 1): max(int(0.75 * bottom * sk.SLICES), 2)]
        bins = np.clip(np.digitize(points[:, 2], edges) - 1, 0, sk.SLICES - 1)
        mostly = [k for k in range(sk.SLICES) if (bins == k).sum() > 20 and (turret | barrel)[bins == k].mean() > 0.8]
        if not mostly or not (band > 0).any():
            continue
        turret_shares.append(float(np.median(areas[mostly]) / np.median(band[band > 0])))
        bottom_shares.append(float((np.percentile(points[turret, 2], 2) - points[:, 2].min()) / height))
        turret_heights.append(float((np.percentile(points[turret, 2], 98) - np.percentile(points[turret, 2], 2)) / height))
        if barrel.sum() >= 50:
            barrel_shares.append(_width(points, barrel) / _width(points, turret))
            barrel_lengths.append(float(np.ptp(points[barrel, 1]) / np.ptp(points[turret, 1])))
        sources.append(entry["rel"])
        labelled.append((entry["rel"], points, labels))
    turret_share = float(np.median(turret_shares))
    barrel_share = float(np.median(barrel_shares))
    turret_rule = {
        "area_share": round(turret_share, 4),
        "area_threshold": round(math.sqrt(turret_share), 4),
        "search_from": round(0.75 * min(bottom_shares), 4),
        "cell_share": CELL_SHARE,
        "min_height_share": round(0.5 * min(turret_heights), 4),
        "source": f"plan area of the height slices that are mostly turret over the lower hull's (sk.slice_areas), over {len(sources)} vanilla light tanks; the threshold is their geometric middle, "
                  "the search starts at three quarters of the lowest turret bottom, and a turret is at least half as tall as the shortest",
    }
    # The rule run on vanilla's own tanks: the share of the surface it puts on the side vanilla's skinning does.
    validation = {}
    for rel, points, labels in labelled:
        try:
            cut = sk.turret_cut(points, turret_rule)["cut_z"]
        except ValueError as error:
            validation[rel] = str(error)
            continue
        upper = np.isin(labels, ["turret", "barrel_base", "barrel_tip"])
        judged = upper | (labels == "chassie")
        validation[rel] = round(float(((points[:, 2] >= cut) == upper)[judged].mean()), 4)
    turret_rule["validation"] = validation
    return {
        "turret": turret_rule,
        "barrel": {
            "width_share": round(barrel_share, 4),
            "width_threshold": round(math.sqrt(barrel_share), 4),
            "min_length_share": round(0.5 * min(barrel_lengths), 4),
            "source": f"barrel-weighted vs turret-weighted width over {len(barrel_shares)} vanilla light tanks; the threshold is their geometric middle; "
                      "a barrel is at least half as long, against its turret, as vanilla's shortest",
        },
    }


CELL_SHARE = 0.02  # plan-view grid cell, a share of the length: a tank's road wheel is about two cells


def labelled_samples(mesh, count: int = 60000):  # the count the Blender stage samples a model with
    """Surface samples of a vanilla mesh (Blender space) with the bone each sample's triangle follows most."""

    visible = ~mesh.collision
    triangles = mesh.triangles[visible[mesh.triangles].all(axis=1)]
    points = np.array([sk.to_blender(p) for p in mesh.positions])
    dominant = mesh.joints[np.arange(len(mesh.joints)), np.argmax(mesh.weights, axis=1)]
    a, b, c = (points[triangles[:, k]] for k in range(3))
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    rng = np.random.default_rng(7)
    chosen = rng.choice(len(triangles), size=count, p=area / area.sum())
    u, v = rng.random(count), rng.random(count)
    flip = u + v > 1
    u[flip], v[flip] = 1 - u[flip], 1 - v[flip]
    samples = a[chosen] + (b[chosen] - a[chosen]) * u[:, None] + (c[chosen] - a[chosen]) * v[:, None]
    labels = np.array([mesh.bones[j] if j >= 0 else "" for j in dominant[triangles[chosen, 0]]])
    return samples, labels


def attack_turn(game: Path, clip: dict) -> dict:
    """The turret's turn before the shot, measured on vanilla's idle: its widest traverse and its fastest rate."""

    mesh = pdx_deform.load_mesh(game / clip["mesh"])
    anim = pdx_deform.load_anim(game / clip["anim"])
    motion, frames = sk.resample(sk.local_motion(mesh, anim), anim.fps)
    q = motion["turret"]["q"]
    angles = np.array([sk.rotation_angle(v) for v in q])
    rates = np.array([sk.rotation_angle(sk._quaternion_from_matrix(sk.quaternion_matrix(q[k]).T @ sk.quaternion_matrix(q[k + 1]))) for k in range(len(q) - 1)])
    degrees = float(angles.max())
    return {
        "degrees": round(degrees, 2),
        "ease_frames": int(math.ceil(1.5 * degrees / max(float(rates.max()), 1e-6))),
        "source": f"{clip['anim']}: the turret's widest turn from rest, and the frames its fastest rate needs for it (eased, so 1.5 times)",
    }


def ship_rules(game: Path, measured: List[dict]) -> dict:
    """The waterline: vanilla hulls end at z = 0; the beam there against the widest beam, and how far the keel goes below."""

    width_shares, drafts = [], []
    for entry in measured:
        pts = entry["points"]
        length = float(np.ptp(pts[:, 1]))
        near = pts[np.abs(pts[:, 2]) < 0.02 * length]
        hull = pts[pts[:, 2] < 0.6 * pts[:, 2].max()]
        if len(near) > 8:
            width_shares.append(float(np.ptp(near[:, 0]) / np.ptp(hull[:, 0])))
        drafts.append(float(-pts[:, 2].min() / length))
    return {"width_share": round(float(np.median(width_shares)), 4), "draft_share": round(float(np.median(drafts)), 4),
            "source": "beam at the waterline over the widest beam, and the keel's depth over the length, medians over " + ", ".join(e["rel"] for e in measured)}


def budget_models(game: Path, kind: str) -> List[dict]:
    """Every vanilla model of the kind (`BUDGET_GLOBS`) with a surface, for the triangle budget and texture size."""

    found = [measure_mesh(game, path.relative_to(game).as_posix()) for pattern in BUDGET_GLOBS[kind] for path in sorted(game.glob(pattern))
             if not any(skip in path.name for skip in BUDGET_SKIP)]
    return [e for e in found if e["triangles"] >= 200]


def _span(entry: dict) -> np.ndarray:
    return np.maximum(entry["high"] - entry["low"], 1e-9)


def collision_entry(measured: List[dict]) -> Optional[dict]:
    """The `Collision` box as shares of the visible box (medians), when most of the set carries one."""

    collisions = [e for e in measured if e["collision"]]
    if len(collisions) * 2 <= len(measured):
        return None
    shares = np.median([(e["collision"]["high"] - e["collision"]["low"]) / _span(e) for e in collisions], axis=0)
    centres = np.median([((e["collision"]["high"] + e["collision"]["low"]) / 2 - e["low"]) / _span(e) for e in collisions], axis=0)
    bottoms = np.median([(e["collision"]["low"][2] - e["low"][2]) / _span(e)[2] for e in collisions])
    names = [e["collision"]["name"] for e in collisions]
    return {"name": max(set(names), key=names.count), "size_share": [round(float(v), 4) for v in shares],
            "centre_share": [round(float(v), 4) for v in centres], "bottom_share": round(float(bottoms), 4),
            "source": f"Collision boxes of {len(collisions)} of {len(measured)} models, as shares of their visible box (medians)"}


def skeleton_entry(kind: str, measured: List[dict], ref_entry: dict) -> tuple:
    """The kind's bones (rest places as shares of the visible box, medians) and the reference's locators on them."""

    bones = SKELETON[kind]
    if bones is None:
        counts: Dict[int, int] = {}
        for e in measured:
            counts[len(e["bones"])] = counts.get(len(e["bones"]), 0) + 1
        common = max(counts, key=lambda n: (counts[n], -n))
        bones = ["root"] if common == 1 else []
    skeleton = []
    for bone in bones:
        holders = [e for e in measured if bone in e["heads"]] or ([ref_entry] if bone in ref_entry["heads"] else [])
        share = [round(float(v), 4) for v in np.median([share_in_box(e["heads"][bone], e["low"], e["high"]) for e in holders], axis=0)] if holders else [0.5, 0.5, 0.0]
        parent = ref_entry["parents"].get(bone) if bone in ref_entry["parents"] else (skeleton[-1]["name"] if skeleton else None)
        skeleton.append({"name": bone, "parent": parent, "head_share": share})
    locators = [{"name": loc["name"], "parent": loc["parent"], "share": share_in_box(loc["world"], ref_entry["low"], ref_entry["high"])}
                for loc in ref_entry["locators"] if not (loc["parent"] and loc["parent"] not in bones)]
    return skeleton, locators


def role_aliases(game: Path, clips: dict, bones: List[str]) -> dict:
    """Roles whose vanilla clips move the kind's own bones the same way (UNIT-ANIM-SAME's measure on the reference,
    with only the surface those bones carry): the later role is dropped, and the entity plays the earlier one for it.

    The destroyer's attack and defend differ only in a gun turret's turn; on a hull that is one rigid part they are one clip.
    """

    from lib import pdx_motion

    aliases: Dict[str, str] = {}
    roles = list(clips)
    for index, role in enumerate(roles):
        for earlier in roles[:index]:
            if earlier in aliases or role in aliases or clips[role]["mesh"] != clips[earlier]["mesh"]:
                continue
            mesh = pdx_deform.load_mesh(game / clips[role]["mesh"])
            dominant = mesh.joints[np.arange(len(mesh.joints)), np.argmax(mesh.weights, axis=1)]
            keep = np.isin(dominant, [i for i, name in enumerate(mesh.bones) if name in bones]) & ~mesh.collision
            if keep.sum() < 3:
                continue
            index_of = -np.ones(len(keep), dtype=np.int64)
            index_of[keep] = np.arange(int(keep.sum()))
            triangles = index_of[mesh.triangles[keep[mesh.triangles].all(axis=1)]]
            part = pdx_deform.SkinnedMesh(positions=mesh.positions[keep], triangles=triangles, joints=mesh.joints[keep], weights=mesh.weights[keep],
                                          bones=mesh.bones, parents=mesh.parents, inverse_bind=mesh.inverse_bind, skinned=mesh.skinned,
                                          collision=mesh.collision[keep], shape=mesh.shape[keep], normals=mesh.normals[keep])
            first, second = (pdx_deform.load_anim(game / clips[name]["anim"]) for name in (earlier, role))
            larger = max(pdx_motion.motion_amount(part, first), pdx_motion.motion_amount(part, second))
            if larger > 0 and pdx_motion.clip_distance(part, first, second) < pdx_motion.SAME_RATIO * larger:
                aliases[role] = earlier
    return aliases


def calibrate(game: Path) -> dict:
    definitions = sk.scan_definitions(game)
    turn_limit = json.loads((PIPELINE / "config" / "deformation_calibration.json").read_text(encoding="utf-8"))["groups"]["air_naval"]["turn_per_frame"]["value"]
    kinds = {}
    for kind, refs in REFERENCES.items():
        measured = [measure_mesh(game, rel) for rel in refs if (game / rel).is_file()]
        rows = []
        for entry in measured:
            scale = sk.entity_scale(definitions, entry["rel"])
            measure = sk.main_measure(entry["points"], kind)
            rows.append({"rel": entry["rel"], "measure": measure, "scale": scale["scale"] if scale else None,
                         "runtime": measure * scale["scale"] if scale else None})
        with_scale = [r for r in rows if r["runtime"]]
        runtime = float(np.median([r["runtime"] for r in with_scale]))
        reference = ENTITY_REFERENCE[kind] or min(with_scale, key=lambda r: abs(r["runtime"] - runtime))["rel"]
        ref_entry = next(e for e in measured if e["rel"] == reference)
        ref_scale = sk.entity_scale(definitions, reference)
        entity_name = ref_scale["entities"][0]
        source = runtime / ref_scale["scale"]
        main = [sk.main_measure(e["points"], kind) for e in measured]
        centre = np.median([((e["low"] + e["high"]) / 2) / m for e, m in zip(measured, main)], axis=0)
        ground = float(np.median([e["low"][2] / m for e, m in zip(measured, main)]))
        shaders: Dict[str, int] = {}
        for e in measured:
            for shader, tris in e["shaders"].items():
                shaders[shader] = shaders.get(shader, 0) + tris
        budget_set = budget_models(game, kind)
        budget = max(budget_set, key=lambda e: e["triangles"])
        collision = collision_entry(measured)
        skeleton, locators = skeleton_entry(kind, measured, ref_entry)
        clips = {role: clip_entry(game, *pair) for role, pair in CLIPS[kind].items()}
        aliases = role_aliases(game, clips, [bone["name"] for bone in skeleton])
        clips = {role: clip for role, clip in clips.items() if role not in aliases}
        stats = texture_stats(game, measured)
        stats["texture_size"] = texture_stats(game, budget_set)["texture_size"]
        if stats["gloss_quantiles"] is None and kind == "building":
            # vanilla facilities ship no specular map of their own; buildings take the landmarks' (the nearest kind)
            stats.update({k: v for k, v in texture_stats(game, [measure_mesh(game, rel) for rel in REFERENCES["landmark"]]).items() if k != "texture_size"})
        contract = {
            "kind": kind,
            "references": [e["rel"] for e in measured],
            "size": {
                "measure": {"vehicle": "length", "ship": "length", "plane": "wingspan", "building": "footprint", "landmark": "largest side"}[kind],
                "runtime": round(runtime, 4),
                "source": round(source, 4),
                "centre_share": [round(float(v), 4) for v in centre],
                "ground_share": round(ground, 4),
                "per_model": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()} for r in rows],
                "about": "runtime = main measure x entity scale; the model is exported at runtime / the reference entity's scale",
            },
            "entity": {"reference": entity_name, "mesh": reference, "scale": ref_scale["scale"], "file": definitions["entity"][entity_name]["source"],
                       "entity_scale": float(definitions["entity"][entity_name].get("scale", 1.0)),
                       "pdxmesh_scale": float(definitions["pdxmesh"][definitions["entity"][entity_name]["pdxmesh"]].get("scale", 1.0)),
                       "pdxmesh": definitions["entity"][entity_name]["pdxmesh"]},
            "triangle_budget": {"value": int(budget["triangles"]), "mesh": budget["rel"], "models": len(budget_set)},
            "shader": max(shaders, key=shaders.get),
            **stats,
            "collision": collision,
            "skeleton": {"bones": skeleton, "source": "rest places as shares of the visible box, medians over the models that have the bone"},
            "locators": locators,
            "clips": clips,
            "role_aliases": aliases,
            "parts": PARTS[kind] if skeleton else {},
            "mounts": MOUNTS.get(kind, {}),
            "rigid": {"max_gap_share": GAP_SHARE, "source": "kit rule: half a pixel at game size"} if skeleton else None,
        }
        if kind == "vehicle":
            contract["rules"] = vehicle_rules(game, measured)
            contract["attack_turn"] = attack_turn(game, contract["clips"]["idle"])
        if kind == "plane":
            contract["rules"] = {"propeller": PROPELLER_RULE}
            contract["extra_bones"] = ["propeller"]
            spin = min(0.9 * turn_limit, 0.4 * 360 / 4)
            contract["spin"] = {"degrees_per_frame": round(spin, 2), "axis": [0.0, 1.0, 0.0],
                                "source": f"kit rule: 0.4 of a four-blade period and at most 90 % of vanilla's fastest air and naval joint ({turn_limit:.1f} degrees a frame)"}
        if kind == "ship":
            contract["waterline"] = ship_rules(game, [measure_mesh(game, rel) for rel in WATERLINE_REFERENCES])
        kinds[kind] = contract
    return kinds


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("game", nargs="?", type=Path, help="the game folder (default: the one .tools/lib/game.py finds)")
    parser.add_argument("--out", type=Path, default=sk.CONFIG)
    args = parser.parse_args(argv)
    game = args.game or _game_dir()
    kinds = calibrate(game)
    payload = {"_about": "Vanilla measurements for the static-model route (tripo/static_model.py) and its STATIC-* checks, from calibrate_static_kinds.py. Rerun after a game update; never edit a number by hand.",
               "kinds": kinds}
    args.out.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8", newline="\n")
    for kind, contract in kinds.items():
        print(f"{kind}: {contract['size']['measure']} {contract['size']['source']} (runtime {contract['size']['runtime']}, scale {contract['entity']['scale']}), "
              f"budget {contract['triangle_budget']['value']}, shader {contract['shader']}, bones {[b['name'] for b in contract['skeleton']['bones']]}, "
              f"locators {len(contract['locators'])}, clips {list(contract['clips'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
