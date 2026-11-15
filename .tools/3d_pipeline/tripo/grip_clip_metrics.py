"""Per-clip numbers for choosing a unit's roles on a gripped body (numpy only, no Blender).

    py -3.13 .tools/3d_pipeline/tripo/grip_clip_metrics.py <gripped.glb> [--json out.json]

For every clip of a GLB made by `grip_weapon.py` (body `tripo_part_0`, weapon `tripo_part_1` bound to the hand):

- `head_travel`: the path length of the weapon's head tip over the clip, in body heights (an attack swings the
  weapon: about one body height or more);
- `final_extent`: the body's vertical extent in the last frame as a share of its rest height (a death ends on the
  ground: well under 0.5);
- the `clip_check` numbers: weapon deep in the body (share of free weapon points deeper than the margin), the
  deepest penetration, the weapon below the ground, the worst stretch, and its verdict. Death candidates are
  also checked with the ground taken as the lowest body vertex of each frame, because the body is allowed to lie.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import clip_check as cc

PATH_SAMPLES = 60


def clip_metrics(path, body="tripo_part_0", weapon="tripo_part_1") -> dict:
    rig = cc.Rig(path, body, weapon)
    rest_worlds = rig.joint_worlds({})
    rest_mats = rig.skin_mats(rest_worlds)
    rest_body = rig.skin(rig.body, rest_mats)
    height = float(np.ptp(rest_body[:, 1]))
    weapon_rest = rig.skin(rig.weapon, rest_mats) if "joint_ids" in rig.weapon else rig.weapon["positions"]
    joint_rest = rest_worlds[:, :3, 3]
    hand = cc.resolve_weapon_joint(rig.joint_names, weapon_rest, joint_rest, "auto")
    hand_pos = joint_rest[hand]
    # the head tip: the weapon vertex farthest from the hand (the haft's butt is nearer than the head's far edge)
    far = np.linalg.norm(weapon_rest - hand_pos, axis=1)
    tip_rest = np.append(weapon_rest[int(np.argmax(far))], 1.0)
    rows = {}
    for name, tracks, end in rig.clips():
        times = end * np.arange(PATH_SAMPLES) / (PATH_SAMPLES - 1)
        tips, last_body = [], None
        for t in times:
            mats = rig.skin_mats(rig.joint_worlds(rig.pose_for(tracks, t)))
            tips.append((mats[hand] @ tip_rest)[:3])
            last_body = mats
        tips = np.array(tips)
        final = rig.skin(rig.body, last_body)
        rows[name] = {
            "head_travel": round(float(np.linalg.norm(np.diff(tips, axis=0), axis=1).sum() / height), 3),
            "final_extent": round(float(np.ptp(final[:, 1]) / height), 3),
            "seconds": round(float(end), 2),
        }
    normal = cc.check(path, body, weapon, samples=24)
    ground = cc.check(path, body, weapon, samples=24, per_frame_ground=True)
    for name, row in rows.items():
        for label, result in (("", normal), ("lying_", ground)):
            clip = result["clips"][name]
            row[label + "weapon_in_body_pct"] = clip["weapon_in_body_pct"]
            row[label + "weapon_deep_in_body_pct"] = clip["weapon_deep_in_body_pct"]
            row[label + "deepest_penetration_pct_of_height"] = clip["deepest_penetration_pct_of_height"]
            row[label + "weapon_below_ground_pct"] = clip["weapon_below_ground_pct"]
            row[label + "verdict"] = clip["verdict"]
        row["stretched_pct"] = normal["clips"][name]["stretched_pct"]
    return rows


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("glb", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    rows = clip_metrics(args.glb)
    for name, row in rows.items():
        print(f"{name[:40]:40s} head_travel {row['head_travel']:5.2f}  final_extent {row['final_extent']:.2f}  deep {row['weapon_deep_in_body_pct']:5.2f}%  "
              f"lying deep {row['lying_weapon_deep_in_body_pct']:5.2f}% below_ground {row['lying_weapon_below_ground_pct']:5.2f}%  stretch {row['stretched_pct']:5.2f}%  {row['verdict']}")
    if args.json:
        args.json.write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
