---
name: hoi4-3d-model-pipeline
description: Create, rig, animate, convert, export, audit, and integrate Hearts of Iron IV 3D units, buildings, props, creatures, vehicles, aircraft, and naval objects through a verified Meshy-to-Blender-to-io_pdx_mesh workflow, including sourced sound-design handoffs for custom unit packages. Use when a HOI4 mod needs .mesh, .anim, PDX model textures, entity or .asset handoffs, scale calibration, skeletal actions, companion unit audio, or runtime model QA.
---

# HOI4 3D Model Pipeline

Use this skill for a complete model package from one approved reference image through Meshy, Blender, PDX conversion, sourced unit sound design, runtime wiring, and live evidence. Treat geometry, materials, animation, sound roles, entity registration, gameplay consumers, and map placement as one contract with explicit ownership.

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

After the key gate passes for an actual 3D requirement, run `python .tools/3d_pipeline/bootstrap_3d_workflow.py` from the mod root before route discovery. The bootstrap autonomously discovers the repository and Blender paths, resolves the latest available Meshy package, Blender MCP release or default-branch head, and io_pdx_mesh release, verifies each resolved artifact, materializes concrete entries in `.codex/config.toml`, removes `.codex/3d_mcp_config.template.toml`, installs and enables the matching Blender MCP add-on into Blender's discovered extension repository, configures its resolved bridge endpoint, starts Blender when no reachable bridge exists, and records the observed versions, refs, paths, and checksums. The user must not be asked to copy, edit, replace, install, enable, or launch MCP or Blender components manually. Treat `.tools/3d_pipeline/config/dependencies.lock.json` as a generated resolution record with `resolution_policy = latest_at_bootstrap`, not as a stale hand-written version pin. Verify the selected Meshy MCP route is reachable, the latest official package and its live schema are usable, the latest Blender MCP server and matching add-on are installed and enabled, the discovered Blender executable and build are known, the configured Blender bridge is reachable, and the latest io_pdx_mesh archive is installed and checksum-recorded. If latest-version resolution, verification, add-on installation, bridge reachability, or compatibility fails, stop with `required installation/verification` or `blocked`; never silently substitute an unverified route or continue with an older dependency.

Read the repository AGENTS.md, the local offline wiki pages for entities, graphical assets, units, buildings, scopes, effects, and relevant gameplay surfaces, the local vanilla documentation, and the exact vanilla model/entity/material/action precedents before wiring source files.

## 2. Ownership and scope

The 3D worker owns the deterministic job, one-image reference gate, provider lineage, downloaded source models, Blender source and checkpoints, geometry repair, materials, processed textures, rigs, skeletal actions, sourced unit sound research, original and derived audio files, .mesh/.anim exports, reimport evidence, manifests, QA reports, and runtime handoff.

The parent implementation agent owns .asset, entity, .gfx, unit and building definitions, gameplay effects, text icons, province/state placement, final runtime synchronization, live consumers, in-game screenshots, and the overall completion claim.

Do not edit gameplay or runtime registration from the 3D worker unless the parent explicitly grants a narrow file scope. A provider task, .blend, preview, or export is not in-game completion.

Every custom unit, sub-unit, creature, vehicle, aircraft, or naval package requires a sourced sound-design handoff. The worker must search the Internet for a defensible, legally usable source for each applicable sound role, preserve the original download and source evidence, and record the original URL, license, usage terms, access date, and SHA-256 checksums. Mechanical trimming or format conversion is allowed only when the license permits the transformation, and the original must remain unchanged beside any derived file. Map each sound role and synchronization point to the relevant animation action and frame, or to the named runtime lifecycle when no animation exists. If no defensible source exists, mark the role or package `blocked`.

The worker must never generate, synthesize, record, manually author, fabricate, or use unlicensed audio. Test tones, primitive waveforms, placeholder beeps, noise beds, stock effects with unclear rights, and silent stand-ins are not acceptable unit audio. The parent owns final sound definitions, runtime wiring, and live validation.

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
sound/source/
sound/derived/
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

Keep an append-only history, a manifest, a provider task ledger, a dependency record, a sound-source ledger, a requirement-to-runtime crosswalk, and a handoff under the job root. Record absolute paths only in local evidence and portable relative paths in manifests.

## 4. Classify the model profile

Choose one profile before provider work: `static_prop`, `building`, `humanoid_unit`, `nonhumanoid_creature`, `vehicle_land`, `aircraft`, `naval`, or `articulated_attachment`.

For a humanoid unit, define the unit or sub-unit consumer, entity key, .asset key, mesh key, material paths, icon or text-icon requirements, idle action, move action, attack action, death action when relevant, and the country/province/state test that exposes it.

For a building or map entity, define the building key, entity key, mesh key, state and province placement, valid state-to-province pair, construction or level behavior, zoom visibility, rotation, runtime scale, and a test location that is not hidden by an existing building.

For a nonhumanoid creature, vehicle, aircraft, or naval object, define the domain-specific coordinate axes, ground/water contact, orientation, required actions, camera/zoom expectation, rigid or deforming parts, and live consumer before export.

For every custom unit profile, define applicable sound roles such as selection, movement or engine, idle, attack, impact, special action, and death or destruction, along with the animation actions or runtime moments that synchronize each role.

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
3. Submit image-to-3D using the latest verified official route and live schema.
4. Poll task status until success or a recorded terminal failure.
5. Download GLB/FBX and textures immediately and checksum them.
6. Review the candidate from front, rear, side, top, and underside views where relevant, plus wireframe, untextured shading, and textured material views, before spending on remesh, retexture, rig, or animation.
7. Use remesh, retexture, rig, or animation only when the profile and QA gates justify the paid tranche.

Provider actions are candidates, not final runtime files. Preserve rejected candidates and reason codes in the job evidence.

## 7. Blender checkpoints and calibration

Create and retain at least these checkpoints: provider source import, normalized, repaired, material-processed, rigged, action-cleaned, and pre-export. Protect provider source objects and work on duplicates.

Import the named vanilla model/entity/material/action reference read-only and measure it before adjusting the custom asset. Record axes, forward direction, origin, source geometry height, entity scale, effective runtime height, ground/water contact, and any exporter coordinate conversion.

For humanoid units, match the custom source geometry to the measured vanilla source mesh height and apply the entity scale exactly once. Do not guess a real-world height, use a generic 1.8m target, or compensate for a wrong source height with an arbitrary runtime scale.

Do not apply nonuniform scale, leave negative transforms, or allow the mesh to float, shrink on movement, change orientation between actions, or exceed the intended runtime footprint. The scale crosswalk must distinguish source geometry height from effective in-game height.

Repair or reject the working geometry so it has no holes, loose components, non-manifold edges, boundary defects, degenerate triangles, missing body parts, invalid normals, duplicate shells, or zero-weight deforming vertices. Record the geometry counts, bounds, transforms, material slots, UV layers, ground/water contact, and repair results. Triangulate unless a verified local export path requires another topology.

## 8. PDX materials and textures

Use the local vanilla shader, UV, texture names, dimensions, and entity material pattern as the authority. Do not assume that a provider preview is a runtime-ready PDX material.

For the installed vanilla PdxMeshAdvanced pattern, verify the packed specular convention against the local precedent before export. The tested convention is R=0, G=32, B=metallic, and A=roughness; raw grayscale roughness in the specular texture produces chrome-black or incorrectly lit surfaces. Record the shader, channel semantics, color space, alpha behavior, texture dimensions, and DDS format rather than trusting a provider preview.

Keep provider textures immutable and derive all processed maps from those originals. If the provider diffuse is too dark, apply a deterministic documented grade from the immutable source on every run and never compound an older processed texture. Use the local vanilla model dimension limit, currently 1024 pixels unless local installed references prove otherwise, and the repository DDS converter. Process and checksum the PNG and DDS files, record shader slots and channel semantics, and compare the final runtime copy against the approved source hash immediately before wiring.

## 9. Skeletal animation

Treat requested animations as required outputs, not optional polish. Define semantic action names, FPS, frame ranges, loop policy, root-motion or in-place policy, ground contacts, deformation expectations, runtime binding, and acceptance evidence for every action.

Provider humanoid actions are candidates. Clean, retarget, bake, and validate them in Blender. Normalize armature transforms, scale keyed location channels deliberately when the source and target scales differ, lock or remove unintended root translation for in-place locomotion, and check first/last-frame ground contact.

Use a custom Blender rig for non-humanoid, mechanical, building, aircraft, naval, or creature assets when animation is required. Do not use hoi4-frame-animation for skeletal .anim work; that skill is for 2D frame-sheet assets.

Export real .anim files for every requested action and reimport or parse those actual files. A still image, static mesh, camera movement, transform-only mockup, or GIF preview cannot satisfy a requested skeletal action.

## 10. Sourced unit sound design

Search the Internet for each required unit sound role after the parent brief and local vanilla sound precedents are known. Prefer sources with explicit permission for the intended mod use, and reject unclear licenses, unclear recordings, or sources that cannot be preserved and attributed.

For every candidate and selected file, preserve the original download and record the source URL, original download URL when different, title or description, creator or recording source, license, usage terms, access date, source checksum, derived checksum, and any attribution requirement. Keep the original file immutable. Trim, crop, resample, normalize, or convert only as a mechanical transformation that the license permits, and record the exact operation and tool.

Map every selected role to the animation action and frame or to a documented runtime lifecycle point. Record whether the cue is looped, one-shot, attached to an action phase, or parent-triggered. If the required role has no defensible source, stop that role or package as `blocked` rather than inventing audio or silently reusing an unlicensed file.

## 11. Export and reimport

Use only the latest verified io_pdx_mesh extension resolved by bootstrap and record its export settings, Blender build, extension version, release URL, and archive checksum in the generated dependency record.

Export .mesh and .anim files into the job export folders first. Reimport or parse each approved export, inspect identity, bounds, material slots, skeleton, actions, FPS, frame range, contacts, and warnings, and save the proof beside the job manifest.

Do not copy exports to the live mod root until the parent has selected the final candidate. Synchronize the final runtime copy in one hash-aware step and record source and destination hashes for every mesh, animation, texture, entity, and .asset file.

Treat selected source exports, staged runtime copies, and active consumer files as separate surfaces. Select the final geometry, material maps, and actions first, then lock the selected source paths in the manifest before copying. Never synchronize from an older provider or processed path, never let a filename choose the source, and compare destination hashes after synchronization.

## 12. Runtime integration handoff

For a unit, the parent must wire the unit or sub-unit to the correct model, entity, material, and action names and verify the required unit_<id>_icon_small text icon when the engine emits that token. Spawn the unit through a supported country scope and test it while stationary and moving.

For a building, the parent must wire the building to an existing entity key, verify the .gfx/.asset chain, place it in a province that belongs to the specified state, use the correct building syntax and argument count, and test visibility at the intended zoom and level.

For all profiles, the handoff must list exact source paths, runtime paths, identifiers, actions, sound roles, animation synchronization points, source and derived audio paths, licenses, access dates, hashes, live-consumer commands or effects, and the remaining parent-owned work. Never point runtime source to a temporary evidence folder.

## 13. Completion evidence

Do not mark the model complete until the manifest, provider lineage, dependency lock, one-image reference proof, Blender checkpoint ledger, processed textures, sourced unit sound package, original and derived audio checksums, sound-role synchronization map, .mesh/.anim outputs, reimport proof, runtime crosswalk, final hashes, and parent handoff exist.

The parent must add the live consumer and in-game screenshot or equivalent runtime proof for the requested surface. The final report must list meaningful validation, skipped validation and why, blockers, needs_user_review items, credits, versions, selected vanilla references, changed files, and simplifications.

Never hide a missing route, missing action, bad texture, invalid placement, failed reimport, unresolved scale, missing entity, stale runtime copy, or absent screenshot behind a fallback. Report it as blocked or incomplete and keep the job evidence.
