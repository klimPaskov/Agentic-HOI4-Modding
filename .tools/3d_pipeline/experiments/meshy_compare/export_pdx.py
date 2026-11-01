"""Export a comparison job's model through the kit's PDX path. No provider call, no credits.

Needs the Blender adapter route (config/blender_hoi4_adapter.json from the bootstrap) but not the
Meshy launcher and not MESHY_API_KEY beyond the import-time check that the kit's own modules make.

  # A or B: the Blender-prepared candidate -> PDX textures -> .mesh -> reimport proof
  # (exactly run_pilot.continue_static, the kit's static export path)
  py -3.13 -B experiments/meshy_compare/export_pdx.py zin_infantry_cmp_m71
  py -3.13 -B experiments/meshy_compare/export_pdx.py zin_infantry_cmp_t25

  # C: the Meshy-rigged GLB of job B, prepared and exported as a skinned mesh without any animation
  # (the same prepare_candidate -> gate -> textures -> checkpoint -> export_mesh -> reimport steps
  # run_pilot.continue_humanoid performs for its attack animation, minus the .anim export)
  py -3.13 -B experiments/meshy_compare/export_pdx.py zin_infantry_cmp_t25 --rigged

The --rigged branch has not been run yet: it is the one piece of this experiment that was written
without being able to execute it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

import run_pilot as rp
from blender_client import BlenderAdapterClient


def export_rigged(spec: dict) -> dict:
    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = rp.ensure_job_layout(rp.resolve_job_root(slug))
    blender = BlenderAdapterClient(rp.REPO_ROOT)
    rig_glb = job / "provider" / "downloads" / rp.rig_download_name(spec, "glb")
    if not rig_glb.is_file():
        raise SystemExit(f"{slug}: no rigged GLB at {rig_glb}; run run_rig_only.py --submit-rig first.")
    profile = rp.load_profile(spec["profile"])
    stem = f"{spec['runtime_stem']}_rigged"
    prep = blender.prepare_candidate(
        slug,
        source_rel=rig_glb.relative_to(job).as_posix(),
        asset_kind="humanoid",
        target_height_m=spec.get("blender_target_height_m", spec["target_height_m"]),
        runtime_entity_scale=float(spec.get("runtime_entity_scale", 1.0)),
        runtime_stem=stem,
        target_triangles=profile["triangle_range"]["working_triangle_target"],
        excluded_provider_objects=spec.get("excluded_provider_objects"),
        vanilla_reference=rp.stage_vanilla_reference(job, spec),
        texture_source_rels=rp.prepare_pilot_texture_sources(job, spec),
        repair_before_reduction=True,
        topology_weld_distance=0.0,
    )
    rp.candidate_gate(job, prep, hard_max=profile["triangle_range"]["hard_max"], stage="rigged_candidate")
    textures = rp.finalize_pdx_runtime_textures(job, spec, blender.process_textures(slug, prep["checkpoints"]["pre_export"]))
    blender.save_checkpoint(slug, prep["checkpoints"]["pre_export"], "rigged_pre_export")
    mesh_rel = f"export/mesh/{stem}.mesh"
    exported = blender.export_mesh(slug, "blender/checkpoints/rigged_pre_export.blend", mesh_rel)
    reimport = blender.reimport_export(slug, mesh_rel, proof_name=stem)
    return {"textures": textures, "export": exported, "reimport": reimport}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("job")
    parser.add_argument("--jobs-config", type=Path, default=HERE / "jobs.json")
    parser.add_argument("--rigged", action="store_true")
    args = parser.parse_args()
    spec = rp.load_job_configs(args.jobs_config)[args.job]
    rp.vet_spec(spec)
    result = export_rigged(spec) if args.rigged else rp.continue_static(spec)
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
