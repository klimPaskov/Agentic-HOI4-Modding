---
name: hoi4-3d-model-pipeline
description: Create, rig, animate, convert, export, audit, and integrate Hearts of Iron IV 3D units, buildings, props, creatures, vehicles, aircraft, and naval objects through a verified Meshy-to-Blender-to-io_pdx_mesh workflow. Use when a HOI4 mod needs .mesh, .anim, PDX model textures, entity or .asset handoffs, scale calibration, skeletal actions, or runtime model QA.
---

# HOI4 3D Model Pipeline

Use this skill for a complete model package from one approved reference image through Meshy, Blender, PDX conversion, runtime wiring, and live evidence. Treat geometry, materials, animation, entity registration, gameplay consumers, and map placement as one contract with explicit ownership.

## 1. Hard start gates

This workflow is optional. Do not inspect, install, enable, or call any 3D provider or Blender route for a mod that has no requirement for a new 3D model, entity, unit action, or skeletal animation.

Check the process environment for a nonblank MESHY_API_KEY before reading a model brief for path discovery, generating a reference, checking balance, or calling any provider.

If the key is missing or blank, stop and tell the user to run this exact PowerShell command:

~~~powershell
[Environment]::SetEnvironmentVariable(
    "MESHY_API_KEY",
    "msy_your_actual_key_here",
    "User"
)
~~~

Then tell the user to restart the shell or Codex. Do not continue until the restarted process exposes the key.

After the key gate passes for an actual 3D requirement, run `python .tools/3d_pipeline/bootstrap_3d_workflow.py` from the mod root before route discovery. The bootstrap autonomously discovers the repository and Blender paths, installs or verifies the pinned Meshy and Blender MCP dependencies, installs the checksum-locked io_pdx_mesh extension, materializes concrete entries in `.codex/config.toml`, removes `.codex/3d_mcp_config.template.toml`, and records the resolved paths. The user must not be asked to copy, edit, or replace MCP configuration. Verify the selected Meshy MCP route is reachable, the official Meshy server version is pinned, the generated Blender MCP route or a verified narrow adapter is available, the intended Blender executable and version are known, and the io_pdx_mesh archive/version/checksum is locked. Stop with blocked or needs_user_review when a required route or dependency is unavailable; never silently substitute an unverified route.

Read the repository AGENTS.md, the local offline wiki pages for entities, graphical assets, units, buildings, scopes, effects, and relevant gameplay surfaces, the local vanilla documentation, and the exact vanilla model/entity/material/action precedents before wiring source files.

## 2. Ownership and scope

The 3D worker owns the deterministic job, one-image reference gate, provider lineage, downloaded source models, Blender source and checkpoints, geometry repair, materials, processed textures, rigs, skeletal actions, .mesh/.anim exports, reimport evidence, manifests, QA reports, and runtime handoff.

The parent implementation agent owns .asset, entity, .gfx, unit and building definitions, gameplay effects, text icons, province/state placement, final runtime synchronization, live consumers, in-game screenshots, and the overall completion claim.

Do not edit gameplay or runtime registration from the 3D worker unless the parent explicitly grants a narrow file scope. A provider task, .blend, preview, or export is not in-game completion.

## 3. Resolve the job root

Resolve the mod root from the current repository and derive a lowercase safe owner/feature/asset slug. Do not use a path from chat when the repository can determine it.

Use a deterministic job root such as docs/assets/<feature_slug>/models_3d/<asset_slug>/ unless the repository has an established model evidence root. Keep source evidence and runtime sources separate.

Create these job surfaces as needed:

~~~text
refs/original/
refs/derived/
refs/briefs/
provider/requests/
provider/responses/
provider/tasks/
provider/credits/
provider/downloads/
provider/rejected/
blender/source/
blender/reference/
blender/working/
blender/checkpoints/
blender/previews/
blender/reports/
textures/source/
textures/processed/
textures/dds/
export/mesh/
export/anim/
validation/
evidence/
runtime/
logs/
~~~

Keep an append-only history, a manifest, a provider task ledger, a dependency record, a requirement-to-runtime crosswalk, and a handoff under the job root. Record absolute paths only in local evidence and portable relative paths in manifests.

## 4. Classify the model profile

Choose one profile before provider work: static_prop, building, humanoid_unit, creature, vehicle, aircraft, naval, or articulated_attachment.

For a humanoid unit, define the unit or sub-unit consumer, entity key, .asset key, mesh key, material paths, icon or text-icon requirements, idle action, move action, attack action, death action when relevant, and the country/province/state test that exposes it.

For a building or map entity, define the building key, entity key, mesh key, state and province placement, valid state-to-province pair, construction or level behavior, zoom visibility, rotation, runtime scale, and a test location that is not hidden by an existing building.

For a creature, vehicle, aircraft, or naval object, define the domain-specific coordinate axes, ground/water contact, orientation, required actions, camera/zoom expectation, and live consumer before export.

## 5. Reference-image gate

If a ready reference image is supplied, preserve it unchanged, record its provenance or user authorization, compute its checksum, and use it as the sole provider input.

If only an asset brief is supplied, autonomously generate exactly one clean Meshy-ready reference image and save it as the single approved input in the job's original-reference folder. Record the generation request, output checksum, dimensions, and approval.

Never generate or send side-profile sheets, turnaround boards, collages, or multi-view boards to Meshy. Blender renders, QA angles, contact sheets, and comparison boards may be created later for review but are never provider inputs.

Do not create a second provider reference to compensate for a failed task without recording a new approved attempt and its reason. Do not hide a paid retry or claim that multiple images were one input.

## 6. Provider sequence

Before each paid tranche, check the live Meshy balance and record estimated and consumed credits. Save the exact tool name, schema version, arguments, request, response, provider task id, timestamps, status transitions, download URL host, and output checksums.

Use this sequence:

1. Preflight the one reference image and job manifest.
2. Check provider balance and record the result.
3. Submit image-to-3D using the pinned official route and the verified schema.
4. Poll task status until success or a recorded terminal failure.
5. Download GLB/FBX and textures immediately and checksum them.
6. Review the candidate from several local Blender views before spending on remesh, retexture, rig, or animation.
7. Use remesh, retexture, rig, or animation only when the profile and QA gates justify the paid tranche.

Provider actions are candidates, not final runtime files. Preserve rejected candidates and reason codes in the job evidence.

## 7. Blender checkpoints and calibration

Create and retain at least these checkpoints: provider source import, normalized, repaired, material-processed, rigged, action-cleaned, and pre-export. Protect provider source objects and work on duplicates.

Import the named vanilla model/entity/material/action reference read-only and measure it before adjusting the custom asset. Record axes, forward direction, origin, source geometry height, entity scale, effective runtime height, ground/water contact, and any exporter coordinate conversion.

For humanoid units, match the custom source geometry to the measured vanilla source mesh height and apply the entity scale exactly once. Do not guess a real-world height, use a generic 1.8m target, or compensate for a wrong source height with an arbitrary runtime scale.

Do not apply nonuniform scale, leave negative transforms, or allow the mesh to float, shrink on movement, change orientation between actions, or exceed the intended runtime footprint. The scale crosswalk must distinguish source geometry height from effective in-game height.

Repair the working geometry so it has no holes, loose components, non-manifold edges, degenerate triangles, missing body parts, invalid normals, duplicate shells, or zero-weight deforming vertices. Triangulate unless a verified local export path requires another topology.

## 8. PDX materials and textures

Use the local vanilla shader, UV, texture names, dimensions, and entity material pattern as the authority. Do not assume that a provider preview is a runtime-ready PDX material.

For the installed vanilla PdxMeshAdvanced pattern, verify the packed specular convention against the local precedent before export. The tested convention is R=0, G=32, B=metallic, and A=roughness; raw grayscale roughness in the specular texture produces chrome-black or incorrectly lit surfaces.

Keep provider source textures immutable and derive processed textures from them without compounding edits. If the provider diffuse is too dark, record a deterministic grade and apply it from the immutable base on every run. Do not overwrite a final mapped texture with an older candidate.

Match the local runtime texture dimension and DDS format. Process and checksum the PNG and DDS files, record shader slots and channel semantics, and compare the final runtime copy against the approved source hash immediately before wiring.

## 9. Skeletal animation

Treat requested animations as required outputs, not optional polish. Define semantic action names, FPS, frame ranges, loop policy, root-motion or in-place policy, ground contacts, deformation expectations, runtime binding, and acceptance evidence for every action.

Provider humanoid actions are candidates. Clean, retarget, bake, and validate them in Blender. Normalize armature transforms, scale keyed location channels deliberately when the source and target scales differ, lock or remove unintended root translation for in-place locomotion, and check first/last-frame ground contact.

Use a custom Blender rig for non-humanoid, mechanical, building, aircraft, naval, or creature assets when animation is required. Do not use hoi4-frame-animation for skeletal .anim work; that skill is for 2D frame-sheet assets.

Export real .anim files for every requested action and reimport or parse those actual files. A still image, static mesh, camera movement, transform-only mockup, or GIF preview cannot satisfy a requested skeletal action.

## 10. Export and reimport

Use only the checksum-locked io_pdx_mesh extension and record its export settings, Blender version, extension version, and archive checksum.

Export .mesh and .anim files into the job export folders first. Reimport or parse each approved export, inspect identity, bounds, material slots, skeleton, actions, FPS, frame range, contacts, and warnings, and save the proof beside the job manifest.

Do not copy exports to the live mod root until the parent has selected the final candidate. Synchronize the final runtime copy in one hash-aware step and record source and destination hashes for every mesh, animation, texture, entity, and .asset file.

## 11. Runtime integration handoff

For a unit, the parent must wire the unit or sub-unit to the correct model, entity, material, and action names and verify the required unit_<id>_icon_small text icon when the engine emits that token. Spawn the unit through a supported country scope and test it while stationary and moving.

For a building, the parent must wire the building to an existing entity key, verify the .gfx/.asset chain, place it in a province that belongs to the specified state, use the correct building syntax and argument count, and test visibility at the intended zoom and level.

For all profiles, the handoff must list exact source paths, runtime paths, identifiers, actions, scale values, texture slots, hashes, live-consumer commands or effects, and the remaining parent-owned work. Never point runtime source to a temporary evidence folder.

## 12. Completion evidence

Do not mark the model complete until the manifest, provider lineage, dependency lock, one-image reference proof, Blender checkpoint ledger, processed textures, .mesh/.anim outputs, reimport proof, runtime crosswalk, final hashes, and parent handoff exist.

The parent must add the live consumer and in-game screenshot or equivalent runtime proof for the requested surface. The final report must list meaningful validation, skipped validation and why, blockers, needs_user_review items, credits, versions, selected vanilla references, changed files, and simplifications.

Never hide a missing route, missing action, bad texture, invalid placement, failed reimport, unresolved scale, missing entity, stale runtime copy, or absent screenshot behind a fallback. Report it as blocked or incomplete and keep the job evidence.
