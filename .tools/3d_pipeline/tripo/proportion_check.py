"""Before the rig: does Tripo's quadruped keep its reference's neck and legs? Compares the model's measured neck and leg length with the
same shares read off the reference picture.

    py -3.13 -B .tools/3d_pipeline/tripo/proportion_check.py <model .glb> --neck <share> [--legs <share>] [--json out.json]
    py -3.13 -B .tools/3d_pipeline/tripo/proportion_check.py --shares neck=<share>,legs=<share> --neck <share> [--legs <share>]

The second form judges a picture before any credits: read the same shares off the 3D-ready picture, or off a multi-view's side view,
and give them as `--shares`; `--neck` and `--legs` are the owner's reference. A redraw or a multi-view that already lost the neck stops
the job before the model press: the Tripo dragon's multi-view showed the same short thick neck its model later had.

Run it on the model's own export (Model page, Export, GLB: free) before any rig work, beside `span_check.py`. A model whose neck came out
much shorter than drawn cannot be posed into the drawn creature: the Tripo dragon's picture has a long S-shaped neck, about a fifth of
its height from the shoulders to the jaw, and its model a short column under a large horned head (0.09 of the height). Four rig rounds
(11 to 14) were spent before a fresh review named it ("the long neck behaves like a short one"). TRIPO-PROPORTION-PICTURE fails when a
share differs from the picture's by more than `MAX_PROPORTION_DIFFERENCE` of it either way. Then make the model again (the picture
redrawn so the part reads plainly), not the rig.

Read the shares off the reference picture, in pixels, with the subject standing as drawn:
- `--neck`: the height from where the neck leaves the shoulders to where it meets the back of the head (the jaw's root), over the
  subject's height from the feet to the top of the head, horns included and wings left out.
- `--legs`: the height of the belly between the legs, over the same height.

The model's shares are measured the way the rig measures it (`quadruped_layout.detect_landmarks` and `detect_neck` on the body without its
wings, `lib/mount_size.winged_body`): the neck column from its base to the head's root, and the belly's height. A model with no neck
column the measure can find reads 0 and fails a picture that has a neck. Reading files only: no Blender, no cost.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional, Sequence

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "adapter"))

import quadruped_layout as ql
from lib import mount_size

# A share read off a picture by eye, through a three-quarter view's foreshortening, is good to about a fifth. A neck half as long as
# drawn is a different creature.
MAX_PROPORTION_DIFFERENCE = 0.3


def model_proportions(points: np.ndarray, triangles: np.ndarray, winged: bool = True) -> Dict[str, float]:
    """The model's neck and leg shares of its height (points in the working frame, +Z up)."""

    body = np.ones(len(points), bool)
    if winged:
        points, found = mount_size.winged_body(points, triangles)
        body = found["body"]
    if ql.faces_plus_y(points[body]):
        centre = np.array([(points[:, 0].min() + points[:, 0].max()) / 2, (points[:, 1].min() + points[:, 1].max()) / 2, 0.0])
        points = np.c_[2 * centre[0] - points[:, 0], 2 * centre[1] - points[:, 1], points[:, 2]]
    landmarks = ql.detect_landmarks(points[body])
    height = float(landmarks["height"])
    neck = ql.detect_neck(points[body], landmarks)
    neck_share = (float(neck["head"][2]) - float(neck["base"][2])) / height if neck else 0.0
    return {"neck": round(neck_share, 3), "legs": round(float(landmarks["belly_z"]) / height, 3)}


def proportion_verdict(model: Dict[str, float], picture: Dict[str, float], limit: float = MAX_PROPORTION_DIFFERENCE) -> dict:
    findings = []
    shares = {}
    for part, drawn in picture.items():
        if drawn is None:
            continue
        share = model.get(part, 0.0) / drawn if drawn > 0 else 1.0
        shares[part] = round(share, 3)
        if abs(share - 1.0) > limit:
            findings.append({"rule": "TRIPO-PROPORTION-PICTURE", "part": part, "share": round(share, 3),
                             "message": f"the measured {part} is {share:.0%} of the reference's ({model.get(part, 0.0):.2f} against {drawn:.2f} of the height, allowed "
                                        f"{1 - limit:.0%} to {1 + limit:.0%}): not the drawn creature. Redraw the picture or make the model again, not the rig"})
    return {"model": model, "picture": {k: v for k, v in picture.items() if v is not None}, "shares": shares,
            "verdict": "fail" if findings else "pass", "findings": findings}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("model", type=Path, nargs="?", help="the model's .glb")
    parser.add_argument("--shares", help="instead of a model: the shares read off another picture, as neck=<share>,legs=<share>")
    parser.add_argument("--neck", type=float, required=True, help="the picture's neck share of the height (see the module text)")
    parser.add_argument("--legs", type=float, help="the picture's belly height share")
    parser.add_argument("--no-wings", action="store_true", help="a quadruped without wings")
    parser.add_argument("--json", type=Path, help="write the verdict here")
    args = parser.parse_args(argv)
    if args.shares:
        measured = {key.strip(): float(value) for key, value in (item.split("=") for item in args.shares.split(","))}
    elif args.model:
        points, triangles = mount_size.read_glb(args.model)
        measured = model_proportions(points, triangles, not args.no_wings)
    else:
        parser.error("give the model's .glb or --shares read off a picture")
    result = proportion_verdict(measured, {"neck": args.neck, "legs": args.legs})
    print(f"model {result['model']}, picture {result['picture']}: {result['verdict']}")
    for item in result["findings"]:
        print(f"  {item['rule']}: {item['message']}")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if result["verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
