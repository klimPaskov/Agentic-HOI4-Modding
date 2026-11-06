"""Measure a generated body and pick its body preset, before anything is rigged (decision 3D-4).

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/measure_body.py <job folder>
    py -3.13 -B .tools/3d_pipeline/measure_body.py provider/downloads/generation_model.glb --unit-type archer \\
        --anatomy legs=2 arms=2 wings=no tail=no extra_limbs=no vehicle=no rider_on_mount=no

It reads the generation (`provider/downloads/generation_model.glb` of a job, or any `.glb` or exported
`.mesh`), measures it (`lib/body_measure.py`: ground contacts, torso width, lower-body reach, height of
the surface's centre) and scores every preset of `config/body_presets.json`. A preset is eligible when
the declared anatomy matches it and every measure falls in its range. The best eligible preset wins,
with a confidence: its score minus the next eligible preset's score, lowered when no anatomy was
declared (wings, tails and extra limbs do not show reliably in a measurement).

The verdict (also written to `<job>/evidence/body_verdict.json` or `--verdict`) is:
- `pass` when the job's unit type uses the chosen preset, or when the job overrides it with
  `body_preset` and a `body_preset_reason`;
- `fail` when the unit type needs another body: change `unit_type` to one the verdict lists, or
  override with a reason;
- `escalate` when no preset fits: the unit needs a custom rig and live authoring
  (the skill's references/live-authoring.md).

A job declares its anatomy in its registry entry, answered from the reference image during its
visual review: `"anatomy": {"legs": 2, "arms": 2, "wings": false, "tail": false, "extra_limbs": false,
"vehicle": false, "rider_on_mount": false}`. The questions are in `config/body_presets.json`.
Reading files only: no Blender, no provider call, no cost.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

PIPELINE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import body_measure, stage_verdict
from lib.paths import read_job_document

PRESETS = PIPELINE_ROOT / "config" / "body_presets.json"
UNIT_TYPES = PIPELINE_ROOT / "config" / "unit_types.json"
GEOMETRY_NAMES = ("generation_model.glb", "geometry.glb", "remesh_model.glb")
# Without declared anatomy, a fit this weak (a vehicle measures like a low quadruped) is not trusted.
LOW_CONFIDENCE = 0.35
YES = {"yes", "true", "1", "y"}
NO = {"no", "false", "0", "n"}


def load_presets(path: Path = PRESETS) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def body_types(path: Path = UNIT_TYPES) -> Dict[str, Optional[str]]:
    """Unit type -> its body preset."""

    types = json.loads(path.read_text(encoding="utf-8"))["types"]
    return {name: entry.get("body") for name, entry in types.items()}


def parse_anatomy(pairs: Sequence[str]) -> Dict[str, Any]:
    anatomy: Dict[str, Any] = {}
    for pair in pairs:
        key, _, value = pair.partition("=")
        value = value.strip().lower()
        if value in YES:
            anatomy[key] = True
        elif value in NO:
            anatomy[key] = False
        elif value.isdigit():
            anatomy[key] = int(value)
        else:
            raise SystemExit(f"--anatomy {pair}: use key=yes|no or key=<count>")
    return anatomy


def score_range(value: float, bounds: Sequence[float], margin: float) -> float:
    """1 inside the range, falling to 0 at `margin` of its width outside it."""

    low, high = bounds
    if low <= value <= high:
        return 1.0
    slack = max(high - low, 1e-6) * margin
    distance = low - value if value < low else value - high
    return max(0.0, 1.0 - distance / slack)


def score_presets(measures: Dict[str, float], anatomy: Dict[str, Any], config: dict) -> Dict[str, dict]:
    margin = float(config.get("margin", 0.15))
    results = {}
    for name, preset in config["presets"].items():
        reasons: List[str] = []
        for key, wanted in preset.get("anatomy", {}).items():
            if wanted is None or key not in anatomy:
                continue
            if anatomy[key] != wanted:
                reasons.append(f"anatomy {key} is {anatomy[key]}, the preset needs {wanted}")
        scores = []
        for key, bounds in preset.get("measured", {}).items():
            value = float(measures[key])
            score = score_range(value, bounds, margin)
            scores.append(score)
            if score == 0.0:
                reasons.append(f"{key} {value:.2f} is outside {bounds[0]} to {bounds[1]}")
        score = min(scores) if scores else 0.0
        results[name] = {
            "eligible": not reasons and score > 0.0,
            "score": round(score if not reasons else 0.0, 3),
            "mean_score": round(sum(scores) / len(scores), 3) if scores else 0.0,
            "reasons": reasons,
        }
    return results


def choose(results: Dict[str, dict], declared: bool, wanted: Optional[str]) -> tuple[Optional[str], float]:
    """The preset to use and its confidence (0 to 1)."""

    eligible = sorted((r["score"], r["mean_score"], name) for name, r in results.items() if r["eligible"])
    if not eligible:
        return None, 0.0
    # Presets that fit equally well are told apart by the unit type the job asked for.
    best_score = eligible[-1][0]
    tied = [name for score, _mean, name in eligible if score == best_score]
    chosen = wanted if wanted in tied else eligible[-1][2]
    others = [score for score, _mean, name in eligible if name != chosen]
    confidence = results[chosen]["score"] - (max(others) if others else 0.0) * 0.5
    if not declared:
        confidence = min(confidence, 0.6)
    return chosen, round(max(0.0, min(1.0, confidence)), 2)


def find_geometry(target: Path) -> Path:
    if target.is_file():
        return target
    downloads = target / "provider" / "downloads"
    for name in GEOMETRY_NAMES:
        if (downloads / name).is_file():
            return downloads / name
    exported = sorted((target / "export" / "mesh").glob("*.mesh")) if (target / "export" / "mesh").is_dir() else []
    if exported:
        return exported[0]
    raise SystemExit(f"No generation to measure in {target}: expected provider/downloads/{GEOMETRY_NAMES[0]} or export/mesh/*.mesh")


def measure_body(target: Path, unit_type: Optional[str], anatomy: Dict[str, Any], override: Optional[str], reason: str) -> dict:
    """Measure, score and decide. Returns the stage verdict."""

    job: Dict[str, Any] = {}
    if target.is_dir() and (target / "job.yaml").is_file():
        job = read_job_document(target / "job.yaml")
    unit_type = unit_type or job.get("unit_type")
    anatomy = {**(job.get("anatomy") or {}), **anatomy}
    override = override or job.get("body_preset")
    reason = reason or str(job.get("body_preset_reason") or "")
    geometry = find_geometry(target)
    measures = body_measure.measure_file(geometry).as_dict()
    config = load_presets()
    bodies = body_types()
    wanted = bodies.get(unit_type) if unit_type else None
    results = score_presets(measures, anatomy, config)
    chosen, confidence = choose(results, bool(anatomy), wanted)
    fitting_types = sorted(name for name, body in bodies.items() if body == chosen)
    unit = str(job.get("asset_slug") or geometry.stem)
    outputs = {
        "geometry": geometry.as_posix(),
        "measured": {key: value for key, value in measures.items() if key != "slices"},
        "presets": results,
        "preset": chosen,
        "confidence": confidence,
        "unit_type": unit_type,
        "unit_type_body": wanted,
        "unit_types_for_preset": fitting_types,
        "anatomy": anatomy,
    }
    checklist = None if anatomy else "Answer the anatomy questions in config/body_presets.json from the reference image and add them to the job as `anatomy`."
    status = f"py -3.13 -B .tools/3d_pipeline/run_pilot.py --jobs-config <your 3d_jobs.json> --status {unit}"
    if override:
        if override not in config["presets"] or not reason.strip():
            raise SystemExit("body_preset needs a preset from config/body_presets.json and a body_preset_reason.")
        outputs.update({"preset": override, "overridden": {"measured_preset": chosen, "reason": reason}})
        return stage_verdict.verdict("measure", True, unit, outputs=outputs, checklist=checklist, next_steps=[status])
    if chosen is None:
        why = sorted({reason for result in results.values() for reason in result["reasons"]})
        escalate = {
            "rules": ["BODY-NO-PRESET"],
            "why": why,
            "how": f"No preset fits: rig and animate this body live in Blender ({stage_verdict.LIVE_GUIDE}), or set body_preset with a body_preset_reason if the measurement is wrong.",
        }
        return stage_verdict.verdict("measure", False, unit, outputs=outputs, checklist=checklist, escalate=escalate,
                                     findings=[{"rule": "BODY-NO-PRESET", "file": geometry.name, "message": "; ".join(why)[:200]}])
    if wanted and wanted != chosen:
        message = f"unit type {unit_type} needs the {wanted} body, but the generation measures as {chosen}"
        steps = [f"Set the job's unit_type to one of {', '.join(fitting_types)}, or set body_preset to {wanted} with a body_preset_reason, then measure again."]
        return stage_verdict.verdict("measure", False, unit, outputs=outputs, checklist=checklist, next_steps=steps,
                                     findings=[{"rule": "BODY-UNIT-TYPE", "file": geometry.name, "message": message}])
    if not anatomy and confidence < LOW_CONFIDENCE:
        steps = ["Answer the anatomy questions from the reference image, add them to the job as `anatomy`, then measure again."]
        return stage_verdict.verdict("measure", False, unit, outputs=outputs, checklist=checklist, next_steps=steps,
                                     findings=[{"rule": "BODY-LOW-CONFIDENCE", "file": geometry.name, "message": f"the {chosen} preset fits only with confidence {confidence} and no anatomy was declared"}])
    if measures.get("debris"):
        message = f"{measures['debris']} separate piece(s) float apart from the body, the farthest {measures['debris_gap']:.1%} of its height away"
        steps = ["Drop them before the rig: add loose_part_edits rules (action drop) for them to the job, or generate again, then measure again."]
        return stage_verdict.verdict("measure", False, unit, outputs=outputs, checklist=checklist, next_steps=steps,
                                     findings=[{"rule": "BODY-DEBRIS", "file": geometry.name, "message": message}])
    if not unit_type:
        steps = [f"Pick the job's unit_type from {', '.join(fitting_types)}, then measure again."]
        return stage_verdict.verdict("measure", False, unit, outputs=outputs, checklist=checklist, next_steps=steps,
                                     findings=[{"rule": "BODY-NO-UNIT-TYPE", "file": geometry.name, "message": "the job names no unit_type"}])
    return stage_verdict.verdict("measure", True, unit, outputs=outputs, checklist=checklist, next_steps=[status])


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("target", type=Path, help="a job folder, or a .glb or .mesh file")
    parser.add_argument("--unit-type", help="the unit type the body should fit (default: the job's unit_type)")
    parser.add_argument("--anatomy", nargs="*", default=[], metavar="KEY=VALUE", help="anatomy answers, e.g. legs=2 arms=2 wings=no")
    parser.add_argument("--override", help="use this preset whatever the measurement says (needs --reason)")
    parser.add_argument("--reason", default="", help="why the override is right")
    parser.add_argument("--verdict", type=Path, help="where to write the verdict (default: <job>/evidence/body_verdict.json for a job)")
    args = parser.parse_args(argv)
    target = args.target.resolve()
    payload = measure_body(target, args.unit_type, parse_anatomy(args.anatomy), args.override, args.reason)
    path = args.verdict or (target / "evidence" / "body_verdict.json" if target.is_dir() else None)
    stage_verdict.write(payload, path)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
