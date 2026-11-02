# Detailed 3D production guide

Use this skill for final 3D geometry and skeletal animation assets. It covers the bounded path from one approved source-informed model reference through provider generation, Blender normalization, PDX materials, rigs, actions, Paradox export, QA evidence, and a parent-owned runtime handoff.

Do not use it for 2D equipment illustrations, map counters, focus or idea icons, 2D frame-sheet animation, leader portraits, or concept-only requests. Those remain with `hoi4-feature-assets` and `hoi4-frame-animation` where applicable.

## Ownership and completion boundary

A provider result is a source candidate, a `.blend` is a working artifact, and a `.mesh` or `.anim` is a runtime candidate. The package is not complete merely because a provider task, Blender preview, or export succeeded. Completion requires the exact runtime registration, a live consumer, and in-game evidence owned by the parent implementation agent.

The 3D worker may create: source GLB, FBX and texture downloads; `.blend` source and checkpoint files; processed PNG and DDS model textures; final `.mesh` and `.anim` files; previews and contact sheets; model job and history files; manifests, QA reports, action manifests, evidence ledgers, requirement-to-runtime crosswalk rows and runtime handoffs; downloaded sourced unit-audio candidates, immutable provenance and licensing records, mechanically derived game-ready audio and sound-design handoffs; custom-unit counter briefs, installed-vanilla reference evidence, `hoi4_icon_artist` handoffs, bespoke counter outputs and comparison evidence; and a patch handoff under `docs/plans/<feature_slug>/subagent_handoffs/` when the feature slug is known.

It must not edit gameplay, sound definitions, localisation, scripted localisation, `.gfx`, `.gui`, `.asset`, entity, event, focus, decision, country, history, AI, on-action, spreadsheet, or unrelated asset files unless the parent grants a narrow exception explicitly. It must not change model identity, remove required components, omit required actions, reduce requested scope, or use an external, provider or source fallback without user discussion (the declared Blender recovery route itself is preauthorized). It must not create audio from scratch, expose the Meshy API key, use an unpinned extension or MCP package, or claim in-game completion. The parent owns runtime identifiers, source wiring, live consumer validation, and the overall completion claim.

`hoi4-feature-assets` remains the owner of broad asset inventories, source provenance conventions, texture/DDS conventions, and requirement-to-runtime coverage across asset types. Keep model geometry, model materials, entity wiring, and any separate 2D concept reference distinct. `hoi4-frame-animation` governs 2D frame-sheet animation; it does not replace skeletal 3D `.anim` production.

Every new custom unit, subunit, creature, vehicle, aircraft or ship also requires a sourced sound-design package and new counter art for every counter surface it uses. Both are mandatory completion items; the rules are in the two companion sections below. The parent owns final sound definitions, GFX, runtime wiring and in-game validation.

## Route selection and component completion

Choose the production or repair route before any provider call. This section is the only place the routes are defined; every other file links here.

- Firearm-bearing units, including existing firearm models, require a fresh weapon-free body and a separate geometry task for each required firearm, each from exactly one approved input and made with the profile's generation model (currently Meshy 7). Download firearms as independent assets. Each task keeps independent task, credit, source and download lineage. For an eligible biped, try one verified Meshy body rig and one supported action attempt per missing role, then use Blender for firearm fitting/attachment, rigid controls, locators, contacts, other props, and any missing or unusable rigs, weights, or substantive actions.
- Existing non-firearm repairs proceed directly in Blender and do not require a fresh provider attempt. They need no Meshy key unless explicit provider work is added. A standalone motion request does not authorize replacing accepted geometry, rigs, or actions.
- Other provider-eligible bipeds try Meshy rigging once and each required Meshy animation once when the verified endpoint supports the profile and role. Non-bipedal anatomy goes directly to verified Blender authoring. Preserve every usable result, then switch a failed, unusable, or unsupported stage to Blender. There are no paid rig or action retries, and switching endpoints or regenerating a rig does not reset the attempt count (the ledger counts attempts per operation).

Manual Blender modeling, rigging, weight work, and skeletal action authoring by the configured `hoi4_3d_model_pipeline` role are preauthorized for those routes. Always create or restore every required component, anatomy element, equipment piece, weapon, held tool, rig element, and substantive action without renewed approval. Record an inventory mapping each requirement to geometry, material, attachment or weights, action use, and export/reimport evidence. An absent verified capability is a blocker; it is not permission to omit a component, use a static pose, or alias one action to another role.

Prefer local Blender work for anything that needs no new geometry (scale, position, attachments, materials, rigs, weights, actions): it costs no credits.

## Hard start gates

For provider-dependent work, the first process check is `MESHY_API_KEY`, which must be a non-blank process environment variable before provider preparation, balance checks, or provider calls. If it is missing or blank, stop that work, print the exact PowerShell command from the [3D agent's hard start gate](../../../agents/hoi4-3d-model-pipeline.md), and tell the user to restart the shell or the agent runtime. Never record credentials. A key alone is not enough: Meshy creates API tasks only for accounts on a paid plan. On the free plan every create returns HTTP 402 ("Task creation on the free plan is no longer supported") and charges nothing, although the balance still shows the free monthly credits. Treat that refusal as a blocker for the user, who must upgrade the plan; never retry it or switch to another route. Existing-model Blender-only repair may inspect the approved model, job, dependency lock, and Blender routes without this key and must not start a provider call.

For an explicitly requested existing non-firearm repair, verify the Blender/adapter/io_pdx_mesh lock, live callable schemas, bridge health, approved source/checkpoint paths, and export support before repair. A missing Meshy key or unavailable Meshy service does not block that Blender-only route; a missing required Blender capability remains `required installation/verification` or `blocked`.

After the key gate passes, resolve the repository and job roots from repository-owned files, then run `.tools/3d_pipeline/bootstrap_3d_workflow.py` through HOI4 Mod Setup before any paid/provider call. The bootstrap must install Meshy MCP 0.6.7 from `.tools/3d_pipeline/meshy_runtime/package-lock.json`, require the exact registry integrity, verify the complete 3,954-file runtime tree, resolve Blender Lab MCP to an exact commit, discover the Blender executable/build, and install io_pdx_mesh 0.91 only from its pinned asset size and SHA-256. It writes observed resolution evidence to `.tools/3d_pipeline/config/dependencies.lock.json`, installs and enables the matching Blender MCP add-on, configures the resolved bridge endpoint, starts Blender when needed, and verifies bridge reachability. Treat the generated lock as evidence, not authority over the checked-in Meshy and io_pdx pins.

Blender is pinned. The supported minors are the lock's `compatibility.blender.supported_minors` (today 5.1 and 5.2). The bootstrap selects the highest supported minor and refuses any other, including a `BLENDER_EXE` that names an unsupported build. Every supported minor installs the same deterministic derived io_pdx_mesh compatibility archive, and the bootstrap verifies the archive digest and the installed patched-file hashes before export. Never patch or replace the upstream archive outside the reviewed builder, and rebootstrap through that builder after any change.

Meshy credentials flow only through the external installed HOI4 Mod Setup executable with only `--run-verified-meshy-mcp`. Project wrappers, project Python files, mutable version/npx records, mutable runtime patches, PATH Python and direct REST calls are forbidden credential routes. The one exception is the bootstrap's own bounded authenticated balance request that verifies the key. The app-owned launcher rejects linked or changed runtime files, copies the complete runtime and Node executable privately, verifies the exact private Node certificate simple name through the native Windows verifier, re-hashes the exact private bytes immediately before spawn, clears Node influence variables, and only then passes `MESHY_API_KEY` to the exact entry.

Verify the selected Meshy route, the narrow repository-owned Blender HOI4 adapter route, the resolved Blender server and add-on route, the reachable bridge, and the pinned io_pdx_mesh installation. A running Blender process is not proof that the configured bridge is listening: probe `127.0.0.1:<socket_port>` separately using `blender_mcp_addon.socket_port` from the lock; when it is absent, start the lock-selected Blender executable in hidden background mode with `--background --online-mode --command blender_mcp --host 127.0.0.1 --port <socket_port>`, then probe again and record both results. If lock verification, live schema, add-on installation, bridge reachability, compatibility, or checksum verification fails, stop and report `required installation/verification` or `blocked`; do not install packages, substitute an unapproved dependency or route, or invent a live MCP/tool name.

Use only actual live-listed capabilities. Optional Text-to-Motion client and contract support do not prove launcher exposure. A missing capability is an exact blocker; use authorized Blender recovery where applicable. Rebootstrap stale adapter deployments and verify the complete local source closure. Python 3.9 closure checks include the interpreter's standard-library extension directories (`lib-dynload`, `DESTSHARED`, and Windows `DLLs`); they never trust `site-packages` as standard library or execute modules to classify imports.

Verify against `.tools/3d_pipeline/config/dependencies.lock.json`, `meshy_tool_schema.lock.json` and `blender_hoi4_adapter.json`, and record the exact verified server package, version, git head, route or wrapper, schema version, actual tool identifiers, paid flags, input exclusivity, required arguments, adapter operation names, schemas, arguments and request IDs, Blender build, extension manifest, archive checksum, dependency-lock checksums, provider task IDs, response IDs, and output checksums. Never substitute remembered or hardcoded versions. The required Meshy tools are `meshy_check_balance`, `meshy_image_to_3d`, `meshy_get_task_status`, `meshy_download_model`, `meshy_remesh`, `meshy_rig`, `meshy_convert`, and `meshy_animate`. Optional Text-to-Motion uses `meshy_text_to_motion`, `meshy_list_animations` and the generic `meshy_get_task_status`, `meshy_list_tasks` and `meshy_download_model`. Use only names returned by the live locked route and record the arguments used. `meshy_image_to_3d` never gets `multi_view_thumbnails`, and `meshy_rig` never gets `texture_image_url` (it drops the PBR maps).

Keep provider and Blender integration guidance in this skill and the job's dependency lock. Do not create a central MCP router or tool-specific wrapper. Any viewer, inspector, renderer, or comparison route used for QA must be read-only. Technology-tree QA belongs to the installed HOI4 Agent Tools route: require `hoi4.tech_inspect`, `hoi4.tech_render`, and `hoi4.tech_inspect` with `mode: "compare"` when the asset consumes technology effects. If those exact tools are unavailable, record the exact unavailable route and block that evidence; source-only inspection is not equivalent.

There is no silent simplification. The authorized Blender route above is a normal recovery path, not a fallback requiring renewed approval. External animation packages, provider substitutions, source substitutions, source-free references, identity changes, or omitted requirements still require explicit parent/user approval. Record the actual approval basis, not file dates or old spec/status labels. A static animation companion is review evidence only and never replaces a requested skeletal action.

## Required reading and local calibration

Before 3D work, read:

- `CLAUDE.md`.
- `.claude/skills/hoi4-feature-assets/SKILL.md`.
- `.claude/skills/hoi4-subagents/SKILL.md` when a subagent is used.
- The parent brief, accepted spec, plan, manifest, job, dependency lock, and handoff.
- The HOI4 wiki pages relevant to the target surface, especially `hoi4_wiki/graphical_asset_modding.md` and `hoi4_wiki/entity_modding.md`.
- Relevant character or interface pages when the target consumes those systems.
- Relevant documentation under `C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV/documentation`.
- Local vanilla `.mesh`, `.anim`, `.asset`, entity, material, texture, and model precedents for the exact domain, plus existing repository model precedents.
- For custom units, the exact installed vanilla sound, voice, soundeffect, and entity precedents used by the closest matching unit surface.
- For custom units, the exact installed vanilla counter consumer, sprite definition, texture, canvas, frame order, alpha treatment, and closest visual precedent, plus the matching `hoi4-feature-assets/assets/vanilla_reference/units/` counter family and contact sheet.

Use existing repository paths under `gfx/models/` and `gfx/entities/` as local precedents where applicable, but confirm the final path, shader, material channels, scale, axes, skeleton, action names, and entity structure against the installed vanilla version. Do not lock tutorial values or assume that a nearby asset belongs to the same runtime surface. Treat tutorial polygon counts, texture dimensions, and provider defaults as starting heuristics only; the installed game and latest verified toolchain decide acceptance.

For a humanoid land-unit pilot, this is a hard calibration gate, not a suggestion: import the installed vanilla infantry `.mesh` into the Blender reference collection read-only, identify the exact entity and runtime `scale`, exclude collision-only geometry, and record the measured source-mesh height, effective runtime height, forward axis, ground contact, and the comparison result in the job and manifest. When the custom entity retains the vanilla entity scale, normalize the exported mesh to the measured source-mesh height so the engine applies that scale exactly once; do not normalize to the effective runtime height and then multiply it by the entity scale again. Do not use a generic real-world height or an arbitrary entity `scale` as a substitute. Keep the provider/animation height and the Blender source-mesh calibration height as separate fields when the provider and HOI4 coordinate spaces differ.

For a static map-building pilot, this is also a hard calibration gate: import the installed vanilla mesh used by the actual building entity, identify the exact `pdxmesh` and entity scale, measure the source dimensions and effective runtime dimensions, and record the reference in the job and manifest. Height-only calibration is invalid for buildings. The current `building` profile uses `facility_land.mesh` with `building_land_facility`, source height `3.4697628021`, entity scale `0.6`, effective runtime height `2.0818576813`, and a hard runtime X/Y footprint ceiling of `4.0` meters. A candidate over that ceiling must be explicitly fit with one uniform X/Y factor and must record before/after dimensions; silent anisotropic stretching is forbidden.

## Job intake and deterministic layout

Validate the job before any paid work. The parent must provide:

- event or system owner, stable asset ID, and lowercase asset slug
- one ready reference image path and checksum, or enough brief input to generate it
- source mode (`user_authorized`, `licensed_search`, or `from_scratch_after_failed_search`), immutable source path or documented search record, provenance and rights status including `reference_only_user_authorized` when applicable, and explicit parent or user approval state
- one asset profile from `config/asset_profiles.json`: `static_prop`, `building`, `humanoid_unit`, `nonhumanoid_winged_biped` or `nonhumanoid_creature`. Each carries a `generation` block (the model and request settings), a `validation` block (the fail-closed limits) and an `exceptions` list. A vehicle, aircraft, ship or attachment needs its own profile, calibrated before paid or export work
- geometry intent, required components, forbidden additions, texture direction, and unseen-side/rear-geometry policy
- a style-preflight result rejecting anime-derived presentation, a period-fit declaration for the 1936-1945 setting with explicit exceptions, and color status/palette direction; monochrome or untextured sources require an approved faithful colorization before Meshy
- for every firearm-bearing unit, a `fires_in_combat` or `non_firing` declaration; a firing unit must pass the unobstructed trigger-hand, support-hand, stock/shoulder, weapon-body, and muzzle relationship gate in both source and prepared Meshy input, while a non-firing unit receives no firing action or effect requirements
- the selected `pose_preparation_mode`: `t_pose`, `a_pose`, or `none` with a reason; neutralization is allowed only when it preserves identity, equipment, and critical contacts
- named vanilla reference paths and the expected scale relationship
- for buildings, the measured runtime footprint budget and whether the consumer is a dedicated provincial map building or a state-level gameplay building with a provincial visual anchor
- required action roles, runtime consumer, the job's `credit_budget` (whole credits, see Credits and attempts), and the one-attempt Meshy rig/action policy; rig or action failure switches to Blender, while provider geometry recovery stops for refusal, unavailable capability, an exhausted budget, or exhausted attempt limits
- for every custom unit, a sound-design brief covering applicable voice, selection, movement, idle or engine loop, attack, impact, special-action, and death or destruction roles, plus the selected vanilla precedent and animation synchronization points
- for every custom unit, a counter brief naming each exact runtime counter consumer, token, required state and size, final sprite and DDS path, inspected installed-vanilla definition and texture paths, matching skill-local counter reference family, and `hoi4_icon_artist` handoff path
- the locked provider, Blender, adapter, and `io_pdx_mesh` dependencies
- the deterministic job root and exact handoff path

When the parent does not supply a root, derive it from the resolved repository root, a normalized stable owner id, and a normalized asset slug:

```text
docs/assets/<owner_id>/models_3d/<asset_slug>/
  job.yaml
  manifest.md
  history.jsonl
  refs/
    source/
      untouched.<ext>          # immutable selected or user-supplied source; evidence only
      provenance.json
      source_search.md         # required when no authoritative source is supplied
    original/
      meshy_input.png        # the only image sent to Meshy
      input_manifest.json
    derived/                  # optional, approved clarification only
    briefs/
  provider/
    requests/
    responses/
    tasks/
    submissions/             # one journal entry per paid submission
    credits/
      ledger.jsonl           # append-only credit ledger
    downloads/
    rejected/
  blender/
    source/
    reference/
    working/
    checkpoints/
    previews/
    reports/
  textures/
    source/
    processed/
    dds/
  export/
    mesh/
    anim/
  validation/
  evidence/
  logs/
  runtime/
    handoff.md
    crosswalk.md
```

Use the same derived path every time and pass job-relative paths to provider and adapter calls after root-containment checks. Do not use chat assumptions, timestamps, random IDs, pilot names, or workstation paths as the primary path. Keep append-only task history, manifest state, checksums, copy provenance, and dependency records inside the job root; never archive secrets. Final runtime files must not remain runtime-referenced from `docs/assets/`.

When the owner id identifies an event or another temporary system workspace, keep source files, provider downloads, Blender checkpoints, exports, manifests, QA evidence, and handoffs in that workspace while work is active, blocked, awaiting review, or undergoing acceptance scenarios. Promote durable provenance, licensing, checksums, QA/reimport results, crosswalk facts, and runtime-handoff facts into owner-approved permanent documentation before completion. Place final runtime files in engine-facing folders, verify that no runtime reference points into `docs/assets/`, and remove a temporary workspace only after the complete package is accepted. Retain incomplete or blocked work and report the blocker; never delete skill-local references, durable source archives, or another owner's workspace.

## Designed source reference and provenance gate

Before creating a provider input, inspect the parent brief and apply `references/source-reference-policy.md`. After the mandatory credential and job-root gates, when no authoritative user-supplied image exists, search the Internet for suitable unit-specific modern designed artwork before creating a model reference. Build the candidate pool from game concept art, game character or unit art, game production or promotional art, tabletop or miniature concepts and renders, fantasy or horror illustration, and professional character or creature design sheets. Do not use archival photographs, museum works, historical paintings or drawings, historical plates, antiquities, archaeological images, ethnographic records, reenactment photography, or documentary imagery as model-reference candidates, shortlist entries, comparison images, or selected sources.

Prefer official artist, game studio, publisher, portfolio, or asset pages and sources with explicit reusable licensing or recorded user authorization. Record the search scope, queries, date, eligible candidate URLs, rights decisions, and exact rejection reasons in `refs/source/source_search.md`. A copyrighted source may proceed only as `reference_only_user_authorized` when the user explicitly directs the project to use the actual game or artwork reference; preserve that authorization and provenance, and still reject unclear provenance or any explicit `NoAI` or equivalent restriction.

Archive every selected source's original bytes unchanged as `refs/source/untouched.<ext>`. Record its source page and direct URL, title, creator or publisher, rights or license terms, rights/reuse status, explicit AI-use restrictions, original dimensions and format, retrieval date, and SHA-256 in `refs/source/provenance.json`. A parent- or user-supplied image is authoritative only when that authorization is explicit; never overwrite it with a search result or generated image.

For a licensed or explicitly user-authorized source, use the image generator to create one substantially original, model-ready refinement informed by the selected concept traits. It may clarify or complete model readability and adapt pose, composition, silhouette, background, or other production-facing presentation while preserving the selected traits and intended unit identity; it need not be pixel-faithful. If the source cannot support a defensible refinement without losing the selected identity, reject it and select better artwork.

Only when `source_search.md` documents a reasonable search across the eligible artwork families and finds no acceptable source may a source-free reference be proposed. It remains forbidden unless the parent or user explicitly requests that specific fallback. A reference-only candidate, excluded historical material, or a generic category result is not proof that the search failed. Ordinary model-production authorization does not authorize a source-free reference; without explicit fallback direction, continue source research or mark the reference `needs_user_review` or `blocked`.

## Exactly one reference image per Meshy geometry task

Each Meshy geometry task receives exactly one approved clean final reference image. Never send a search-result page, untouched source, comparison sheet, turnaround, or multi-view board. The body input is `refs/original/meshy_input.png`; each separate firearm input is `refs/firearms/<firearm_id>/meshy_input.png`. By default it must be a source-informed generated refinement of one archived eligible source, retaining the prompt, processing record, source and refined checksums, a source-to-refinement comparison, and explicit parent or user approval. A source-free reference is allowed only after the documented failed-search and explicit fallback gate above. If the required image or provider route is unavailable, mark the job `required installation/verification`, `needs_user_review`, or `blocked` rather than substituting.

For a firearm-bearing unit, this one image must show the complete colored body without a firearm or held prop. Preserve the source equipment identity and reconstruction references as evidence, restore body regions that the source weapon obscured, and generate each firearm separately with the profile's generation model, then fit and attach its downloaded geometry in Blender. Record whether the unit `fires_in_combat` or is `non_firing`; a firing unit needs grip, stock or shoulder, weapon body, muzzle, recoil, effect, and sound synchronization evidence for every firing state.

Do not create or submit a turnaround sheet, multi-view board, collage, side-profile set, or separate front/rear images. Vanilla references may be imported into Blender read-only for calibration, and Blender may render front, rear, side, top, underside, wireframe, or material QA views after generation, but none of those views is a Meshy input or may be sent back to the provider. For native image-generation routes, request transparent output when the downstream asset requires alpha; do not paint a checkerboard or simulated transparency into the submitted image. If native transparency is unavailable, stop or obtain explicit approval for a separate alpha-processing route; a flattened checkerboard is not equivalent. Use background removal only as a documented fallback for failed native output or an inherited, sourced, or user-provided opaque backdrop.

Preflight the one input for silhouette, cropped parts, limb or component separation, dark gaps, strong shadows, alpha quality or background complexity, thin structures, painted details that may be mistaken for geometry, symmetry or asymmetry, unseen-side ambiguity, and source rights. The refinement may clarify or complete model readability and adapt production-facing presentation while preserving the selected traits and intended identity. Require explicit parent or user approval of the final image and source-to-refinement comparison before the Meshy call. Keep the untouched source, final input, refinement prompt, processing record, comparison, and all checksums.

**Visual review.** The reference's visual preflight starts unreviewed: `init_pilot_jobs.py` writes `validation/reference_preflight.json` at `pending_review`, and nothing the job records counts as approval. The parent looks at the final image, then answers each check true or false (`single_subject`, `complete_silhouette`, `component_separation`, `neutral_background`, `no_multi_view_board`, `no_side_profile_sheet`) in a JSON file inside the repository, with an optional `notes` string, and records it:

```powershell
py -3 -B .tools/3d_pipeline/init_pilot_jobs.py --jobs-config docs/plans/<feature>/3d_jobs.json --record-visual-review <asset_slug> --reviewer <name> --review-file <answers.json>
```

It exits 0 only when every check is true. `run_pilot.py` refuses a job whose preflight is not `passed`, before any paid call, and a changed reference image needs a new review.

## Provider generation and lineage

For a new non-firearm model, the normal provider sequence is:

```text
verified balance -> image-to-3D -> status -> immediate download
                 -> optional remesh/retexture
                 -> one suitable Meshy rig attempt
                 -> one Meshy animation attempt per missing supported role
                 -> failed/unusable/unsupported stage: Blender rig/actions
                 -> deformation QA -> PDX export/reimport
```

**Generation model.** The model is the profile's `generation.ai_model` in `config/asset_profiles.json` (currently Meshy 7, `meshy-7`, for every profile). A job may restate it but never change it. Verify that the live `meshy_image_to_3d` schema accepts that exact identifier, compare it with `config/meshy_tool_contract.json` and `config/meshy_tool_schema.lock.json`, and record the exact live identifier used. Retired models (`meshy-t1`, `meshy-5`, `meshy-4`, `meshy-3`), the `lowpoly` model type and the alias `latest` are refused before any paid call. Never alias, relabel an older result or silently downgrade. If the profile's model is unavailable or incompatible with the required operation, stop with `needs_user_review` or `blocked` and explain the exact provider limitation before anything else is used.

### Credits and attempts

One budget per job authorizes the paid work. Every paid job carries a `credit_budget` (whole credits) in its spec and `job.yaml`. Estimates come only from `config/meshy_pricing.json`. The parent gets the user's approval of the budget once, when the job starts; the planned remesh, retexture, conversion, first rig attempt and first required animation attempt, and bounded geometry recovery then run inside that budget without further questions. A plan the budget cannot cover stops at preflight.

- Before each paid create the runner checks the remaining budget (budget minus consumed and reserved credits) and the live balance. A call that would exceed either stops before submission and names the shortfall; the parent asks the user once to raise `credit_budget`. Also stop for provider refusal, unavailable capability, or exhausted attempt limits.
- Attempts per operation are counted from `provider/credits/ledger.jsonl` against the contract limits `max_generation_attempts`, `max_remesh_attempts`, `max_rig_attempts` (1), `max_action_attempts_per_role` (1) and `max_text_to_motion_attempts`. Renaming a stage or changing endpoint or rig does not reset them. Do not submit paid rig or animation retries: preserve passing outputs and switch the affected stage to Blender after the first failure, unusable result, or unsupported role.
- Reuse before paying: a succeeded stage in this job, then a succeeded result in another job under the same jobs root with the same request fingerprint (input file SHA-256 plus canonical request JSON). Any unreconciled submission (`provider/submissions/*.json`) blocks the new call until it is reconciled with `lib.reuse.reconcile_submission`. An uncertain response is recovered from the task inventory and receipts, not by a second paid submission.
- Every attempt, stop, reuse and avoided call is a ledger row with one outcome: `success`, `failed`, `rejected`, `retry`, `reused` or `local_repair`. Record estimates, operation names, attempt numbers, consumed credits and the remaining balance; for failure-driven recovery also the failed operation, the credits already consumed and the proposed paid operation with its estimate.
- `py -3 -B .tools/3d_pipeline/run_pilot.py --credits-report [PATH]` prints totals per model and stage plus failed, wasted and avoided credits for one job folder or every job under a root. It needs no API key and makes no provider call. Put its output in the handoff.

Inspect the live schema before paid calls; do not promise a general geometry prompt when the current Image-to-3D surface exposes only texture-direction text. Record the exact verified arguments and response/task IDs without exposing the API key.

Prefer smart topology when suitable, triangular output, PBR maps when textures are required, removal of baked lighting when supported, and A/T pose for a riggable humanoid. Use the suitable provider pose or `none` for static or mechanical assets. Download every successful artifact immediately, retain the GLB as the canonical provider archive, retain FBX when a rig/action route needs it, and record exact arguments, checksums, provider version, task IDs, request/response lineage, credits, and local download paths. Remote URLs are never the only accepted copy.

Treat every provider result as a candidate, and do not treat an AI result as accepted until it passes the generation gate. Do not invent unseen geometry silently. Review front, rear, sides, top, and underside where relevant, plus wireframe, untextured shading, and textured views. Block on rejected geometry before any additional paid recovery attempt for missing major components, floating critical parts, fused limbs/weapons/turrets/wings, open holes, identity mismatch, broken thin structures, or unacceptable unseen-side invention. Recovery remains bounded by the declared limits and stop conditions. Do not spend retexture, rig, or animation credits on rejected geometry. High-detail generation followed by controlled reduction is allowed only when the job explicitly permits it and the lineage records both candidates.

Tutorial values near 10,000 vertices and the 25,000–30,000 caution band are seed heuristics only. Local vanilla calibration and measured runtime evidence decide the profile target.

## Motion sources and repair QA

Read [motion and repair QA](motion-and-repair-qa.md) before standalone Text-to-Motion, action retargeting, skeletal repair, material rebinding, assembly yaw, or final export QA. Explicit existing-model motion requests do not authorize replacing accepted geometry, rigs, or actions. The app-owned Meshy launcher must actually expose the optional tools; this repo does not patch its credential runtime.

## Blender processing and checkpoints

Use a versioned scene template with protected provider-source, working, rig, action, export, reference, and evidence collections. Unattended work must use the verified repository-owned allowlisted adapter. Do not expose unrestricted Blender Python, shell commands, arbitrary URLs, or paths outside the job and approved reference roots. A development-only Blender route (the official Blender Lab MCP server) is allowed only in the isolated profile, within the parent-approved task boundary and only after the parent verifies its installation and actual callable interface; it never replaces the repository-owned adapter.

Required stages:

1. import the approved GLB or FBX and preserve provider objects
2. duplicate into the working collection
3. name a local vanilla precedent for axes, scale, skeleton, actions, materials, and paths, and import named vanilla references read-only; humanoid land units must include the installed vanilla infantry reference and its entity scale, and building jobs must include the installed mesh and exact map-building entity scale
4. inspect scene and geometry
5. normalize orientation, scale, origin, and ground/water contact
6. measure and enforce the profile runtime footprint budget for static map buildings
7. perform bounded repairs and model every missing required component
8. triangulate before final rig and export QA
9. convert PBR inputs to the locally verified PDX material convention
10. process textures and record DDS paths
11. create or validate the rig
12. create, retarget, clean, and bake actions
13. save checkpoints, export, and build evidence

Save stable checkpoint stages in `blender/checkpoints/` (source import, normalized, repaired, material, rigged, actions, and pre-export). Preserve source checkpoints, working checkpoints, Blender version, adapter version, checksums, and stage transitions. Never edit provider-source objects in place. Required component completion and modest, budget-preserving reduction are authorized Blender work; record before/after topology and preserve identity, silhouette, joints, contacts, UVs, materials, and required detail.

## Geometry, materials, rigging, and actions

Record triangles, vertices, objects, material slots, loose components, non-manifold and boundary edges, holes, degenerates, normals, UV layers and relevant overlap, transforms, negative scale, bounds, origin, ground/water contact, reference comparison, and profile semantic checks. Repair or reject holes, loose components, non-manifold edges, and degenerate geometry before acceptance; any intentional open surface must be named by the profile and marked for review. Final topology is triangular unless a verified local engine path says otherwise.

Inspect source normals and engine material packing rather than trusting a plausible viewport.

**Fail-closed gates.** The code blocks on a missing measurement instead of assuming it passed:

- `candidate_gate` blocks on non-manifold edges, boundary edges, loose components, a triangle count outside the profile's preferred range, material slots above `max_slots`, residual zero-weight deforming vertices (when measured), and any measurement missing from the report. The limits are the profile's `validation` block. The three topology checks count welded geometry (the adapter's 1e-6 position weld, reported as `position_welded_topology`), because a glTF or PDX file stores a vertex once per UV seam and the as-imported counts would report every seam as a boundary edge and every UV island as a loose part. The as-imported counts stay in each check's `raw_as_imported`. Each profile's `validation_calibration` records what the limits were measured on.
- The texture size cap is read from the PNG header. An unreadable image, or a profile without a cap, blocks the conversion.
- io_pdx_mesh export output is captured into the result: a `warnings` list, or `null` with an `exporter_report` that says why it could not be captured. An uncaptured export, or any exporter ERROR, is refused. The reports are `blender/reports/export_mesh.json` and `export_anim_*.json`.
- A profile waives one check only by listing it in its `exceptions` with a reason (`exporter_report` for the export check). The gate record lists every exception applied; report each one in the handoff.

For dual-source preparation, name the accepted geometry mesh and rig mesh set explicitly, reset the target armature to an action-free base, and retain saved/reopened convergence evidence. Select the verified weight-transfer mode deliberately; nearest-face barycentric transfer and configurable one-to-four influence sanitation require their audit output. Vertices dominated by named non-contact bones may be excluded from grounding only when the role is documented.

Bind the maps of the model whose geometry is exported. Each Meshy stage has its own UV layout: the humanoid route exports the animated GLB, which keeps the remesh layout (or the generation layout when no remesh ran), so it takes `remesh_model_textures/*` (or `generation_model_textures/*`), never the other stage's maps. A static or building route that exports the generation geometry takes the generation maps. Before export, `lib/texture_lineage.py` hashes the provider diffuse source (before any grade), normal and metallic/roughness maps and requires each to equal the image embedded in the exported geometry's GLB or downloaded with that model, else the run stops and `blender/reports/texture_lineage_<model>.json` records both hashes. `blender/reports/textures_dds.json` also reports each DDS's mip count; `convert_to_dds.py` writes one mip level, so `mip_chain_present` is false until that tool offers mips. To repair a finished job exported before this gate, run `py -3.13 -B .tools/3d_pipeline/run_pilot.py --jobs-config <jobs.json> --rebuild-runtime-textures <asset>`: it rebuilds `textures/dds/texture_0.dds`, `texture_specular.dds` and `texture_normal.dds` from the files on disk with no Meshy call and no Blender run and needs no `credit_budget`. The parent then copies the three DDS to the runtime paths, or, in a mod whose build stages runtime files from the job folders, runs that build and apply instead. Retain provider source maps unchanged. Record the installed shader, channel mapping, color space, texture limits, DDS paths, and unsupported maps. For the inspected `PdxMeshAdvanced`/`PdxMeshAdvancedSkinned` improved Blinn-Phong route, green is specular strength, blue metalness, and alpha glossiness: invert provider roughness with `A = 255 - roughness` (or `1 - roughness` when normalized), keeping red at the locally verified unused/mask value. Resize packed material RGBA as four independent scalar channels without color conversion or alpha premultiplication; verify channel ranges, constants, inversion, and DDS round-trip. The importer may display alpha as Blender roughness; keep corrected previews separate from engine-packed data. New component textures retain the calibrated default 1024-pixel budget; an existing body atlas may be preserved up to 2048 when inspected and explicitly bounded. Use `.claude/skills/hoi4-feature-assets/tools/convert_to_dds.py` and its header/alpha validation. Rebuild diffuse grades from immutable provider originals, never compound derivatives. Missing, black, magenta, invisible, accidentally transparent, or implausibly reflective materials fail QA, as does a raw grayscale roughness map used as specular.

Use one profile's calibrated axes, scale, triangle range, material/texture limits, rig route, action roles, root policy, instance density, semantic checks, export preset, and runtime pattern. A profile must be calibrated before paid or export work begins.

For map buildings, the profile's footprint budget is a hard runtime gate. The default policy is `reject`; `fit_to_budget` is allowed only when the job explicitly requests it and applies a uniform X/Y fit after height normalization. The adapter report must retain `runtime_dimensions_before_fit_m`, `runtime_dimensions_after_fit_m`, `fit_factor_xy`, `runtime_footprint_before_m`, and `runtime_footprint_after_m`.

The reusable pilot runner treats `building` and `static_building` as static routes, prepares their `Image_0`/`Image_1`/`Image_2` texture sources, and never sends them through humanoid rig or action continuation. A building job without a named installed vanilla reference is rejected before Blender preparation.

For static map-building materials, use the shader from the installed vanilla building consumer. With the current vanilla surface this is `PdxMeshAdvancedSnow`. Verify packed PDX normal and specular channel statistics before synchronizing runtime DDS files.

Provider rigging follows Route selection and is tried only for a clear standard biped within the verified endpoint's constraints. Inspect and map a passing result in Blender; otherwise author or repair the rig and weights through the bounded Blender adapter. Nonhumanoids require a measured scale crosswalk, a dedicated custom rig, and a written rig map. Mechanical assets use rigid components and deliberate pivots: turrets, barrels, recoil, propellers, rotors, doors, wheels, and tracks must not bend from blended weights.

When a requested variant is a faithful parent-unit specialization, reuse the approved parent model, rig, materials, and verified action set where the silhouette and animation semantics remain valid. Record the parent asset ID, source/checksum lineage, reused components, and every changed component. Do not silently reuse a parent counter or other 2D surface; route those surfaces through `hoi4-feature-assets` for bespoke production.

## Custom unit-counter companion

Every new custom unit or subunit must ship with bespoke counter art for every counter surface it uses. At minimum, a land subunit that emits the standard tokens needs its own large `unit_<subunit_id>_icon` counter strip and small `onmap_unit_<subunit_id>_icon` map counter. Air and naval units need the corresponding domain-specific map counters and inverted or state variants when the verified consumer exposes them. Derive the actual required tokens from the installed unit and `interface/subuniticons.gfx`; do not infer them only from this example.

This skill owns the custom-unit counter requirement and routes actual 2D production to `hoi4-feature-assets` and `hoi4_icon_artist`. The asset skill owns image-generation source evidence, alpha processing, native-canvas QA, contact sheets, DDS round-trip validation, and parent-review states. The 3D worker must not draw, trace, reconstruct, resize, recolour, or otherwise author 2D counter icons itself.

Before counter design, inspect the closest matching installed-vanilla definition and DDS. Record source paths, native canvas, per-frame dimensions, `noOfFrames`, frame order, alpha/background behavior, border treatment, visual scale, silhouette, exact green hues and value range, shading, contrast, and owning consumer. Also inspect the matching skill-local reference and contact sheet: `units/land/counters_large/`, `units/land/map_counters/`, `units/air/map_counters/`, or `units/naval/map_counters/`. If the installed vanilla definition, texture, and matching reference family cannot be inspected, mark counter production `blocked`; never guess the canvas, frame layout, sprite contract, or style. A counter made without recorded vanilla-reference inspection cannot satisfy completion.

Route the counter brief to `hoi4_icon_artist` through `hoi4-feature-assets`. Require the worker to return the original source PNG, saved prompt, processed alpha PNG, final DDS, native-size contact sheet, decoded DDS round-trip evidence, manifest entry, and `gfx_handoff.md`. Preserve the sampled exact vanilla green palette and selected, inverted, or frame-state behavior rather than using arbitrary green. The parent owns `.gfx`, texticons, subunit definitions, localisation, and runtime wiring. A missing bespoke counter is `needs_user_review` or `blocked`; never use a copied vanilla counter, renamed counter, generic placeholder, or other fallback for runtime promotion or completion.

Keep the counter source, processed evidence, and runtime copy distinct, report the selected source and hashes, and never silently synchronize an older candidate back into the runtime surface. Until the parent visually reviews the native-size contact sheet, the handoff remains `needs_user_review` or `blocked` and the worker must not claim completion.

Require no zero-weight deforming vertices, normalized weights, influence counts within local precedent, no unapproved opposite-side stretch, rigid assignment for rigid parts, and deformation tests in representative poses. Automatic weights are only a seed where the profile allows them.

Nearest-N bone weighting and axis-aligned bounding-box selections can produce abrupt weight seams despite full coverage and nonzero weights. Render articulation extremes and inspect stretched edges; repair affected deforming regions with locally smooth, explicit normalized weights, verify that selected vertices receive the intended assignment, and confirm unselected weights remain unchanged.

A complete-looking surface with backface culling disabled does not prove reversed faces: the visible surface may be a far wall seen through a hole. Distinguish rest-topology defects from posed foldovers using neutral and posed views, exact affected edges, and face/corner normals before choosing a local repair. Do not blanket-flip faces, weld vertices, or cap openings.

Every requested semantic action is produced or marked blocked. Each must have a semantic role, final name, source route, FPS, frame range, loop state, root policy, preview, exported `.anim`, proposed runtime binding, and validation result. Provider actions follow Route selection: retain included locomotion clips when they pass, and after failure or an unusable result author the affected role in Blender while preserving passing source actions. Blender may create or repair anatomy-appropriate bones, hierarchy, bind pose, skin weights, controls, constraints, and substantive articulated keyed actions, then bake, inspect deformation and contacts, synchronize sound/effects, export, and reimport. Static, transform-only, whole-rig-only, or semantically aliased motion cannot pass.

Define in-place or root-motion policy before editing keys, apply any location conversion exactly once, and record the factor and before/after channels. Check foot, hand, equipment, muzzle, and ground contacts at representative frames. Attack or firing actions must visibly aim, discharge, recoil, and recover when the role requires it; death actions must visibly collapse, impact, and settle. For loop actions, sample at least the first, quarter, middle, three-quarter, and last phases. For non-loop terminal actions, retain start/middle/end or another role-appropriate set. A skeleton change invalidates weights, actions, exports, and downstream evidence. External animation packages or another provider remain separate fallbacks requiring explicit approval and provenance.

Measure ground-contact correction from each frame's uncorrected posed contacts and apply world-vertical correction through the verified exported root basis, or an object-transform route validated for that source and exporter. Preserve rotation modes and prevent lateral drift; require contact preservation in the actual exported bytes after reimport, because a grounded Blender object alone does not prove exported grounding. Global minimum-Z clearance is not anatomical support: a prop, finger, or coat hem can touch the ground while the torso floats. Inspect intended support contacts in terminal death poses and each limb's stance/swing contacts through gait phases, then correct articulation and prop contacts rather than relying only on whole-body Z translation.

A professional BVH source must use the bounded native BVH import route with a verified source receipt, exact filename/action identity, explicit bone-chain mapping, axis and scale settings, frame-rate conversion, root-motion policy, and saved/reopened curve signature. Before PDX animation export, create the guarded export-coordinate checkpoint and fail closed on protected-source, topology, material, armature, bone, action, or provenance drift.

## Custom unit sound-design companion

Final unit audio is source-only. The worker must never create, synthesize, record, generate, or manually author sound, and must never replace a missing source with test tones, primitive waveforms, placeholder beeps, noise beds, or an unlicensed stock effect. If a suitable sourced file cannot be found and licensed, mark the affected role or package `blocked`.

Every new custom unit package must define a coherent custom sound identity. Do not leave a distinctive unit silent or attach an unrelated default sound family. A vanilla sound family may be reused only when the accepted design says it genuinely matches the unit.

Selection audio is mandatory for every custom unit package. Provide at least one sourced selection one-shot, a stable runtime identifier, and an exact consumer/binding plan; do not treat idle entry, entity creation, or another animation-state event as unit selection. Acceptance requires evidence from the actual selection consumer, not an idle or entity-state inference.

Inspect the exact vanilla consumer before planning the package because land units, creatures, vehicles, aircraft, and ships do not necessarily expose the same sound roles. Include the applicable roles:

- selection and order acknowledgements or unit voice
- idle, ambient, engine, rotor, mechanical, or creature loops
- movement
- weapon discharge and attack
- impact, hit, or contact
- special actions
- death, destruction, shutdown, or disappearance

For infantry voices, recheck the installed vanilla templates and bindings for the current game version. Common templates include `TAG_infantry_idle`, `TAG_infantry_move_out`, `TAG_infantry_neutral_combat`, `TAG_infantry_positive_combat`, and `TAG_infantry_retreat`. A custom infantry family owned by a dedicated country or original tag must identify the exact `<TAG>_infantry_idle` selection soundeffect in the installed voice category, verify the effective tag or `original_tag` for dynamic and cosmetic transitions, and enumerate every infantry division under that identity. This is country/original-tag routing, not subunit or sprite routing. If ordinary and custom infantry under one tag require distinct selection voices, mark per-subunit selection blocked rather than replacing the other family.

Use the repository web-search workflow to locate candidate files on the Internet, inspect the source page and direct download terms, record the source page and download URLs before downloading, and save only approved candidates under the deterministic job evidence root. This narrow research exception does not permit arbitrary URLs, remote execution, or files outside the job and approved reference roots. Prefer public-domain, Creative Commons, official archive, institutional, user-authorized, or otherwise clearly licensed sources. Reject unclear provenance, unclear recording rights, unclear modification rights, vague royalty-free claims, and sources that do not permit the intended mod use.

Download and preserve the original source file under the deterministic job evidence root. Record the source page URL, direct download URL when distinct, title, creator or performer, license, usage terms, download date, original format and duration, and SHA-256 checksum. Keep the source file immutable and link every derived file back to it.

Mechanical transformations such as trimming, fading, silence removal, normalization, channel conversion, resampling, and codec conversion are permitted only when the source license allows them. Keep the original source, transformation recipe, derived checksum, and final format in the evidence package. These operations must never become a way to create audio from scratch.

The sound handoff must define:

- the unit or subunit id and runtime consumer
- the chosen vanilla sound and voice precedents
- the mandatory selection source, soundeffect identifier, exact engine consumer, binding scope, resolved country or original tag, and every infantry consumer under that identity
- proposed sound, soundeffect, wrapper, and file identifiers
- one-shot or loop behavior
- the animation action and exact frame or phase that each sound should follow
- source mode, provenance, licence status, and forbidden substitutions
- expected final file format and runtime path based on verified local precedent
- any volume, range, variation, or randomization behavior supported by that precedent
- the Internet source URL, attribution, license, original file path, derived file path, and checksums for every sourced audio candidate
- the parent-owned files that must be wired and the validation still required

Before claiming family-wide model or sound coverage, enumerate every `common/units` subunit that resolves the custom sprite token. An entity-state sound package reaches only consumers that resolve that entity; shared-family consumers must share the binding and deliberate exclusions must be recorded in the handoff.

Custom vocal units should have voice direction that matches their culture, language, body, and role. Nonhuman or impossible units should use purpose-built, sourced vocalizations or mechanical sounds instead of ordinary soldier acknowledgements. Do not manufacture final audio from test tones, primitive oscillators, placeholder beeps, or unrelated stock effects.

The model worker does not claim the sound package complete merely because synchronization points and identifiers are documented. It must provide sourced audio candidates and licensing evidence or mark the role blocked. Sound definitions, entity or unit wiring, and in-game playback validation remain parent-owned unless the task explicitly grants that production scope.

## PDX export and reimport evidence

Before export, ensure the export collection contains only approved objects and that transforms, topology, materials, armature, actions, exporter version, and preset pass. Export `.mesh` and required `.anim` files using the checksum-locked verified `io_pdx_mesh` route. Capture the exporter report (see Fail-closed gates), every warning, output path, byte size, and checksum.

Keep the assembled body and all added props within calibrated runtime triangle, material, texture, and export-stream budgets. Never omit required equipment or anatomy to hit a target. Controlled reduction of low-value topology is authorized when it preserves silhouette, joints, contacts, grips, UV/material quality, and required detail. For an oversized accepted skeletal or static mesh, use the bounded material-batch partition operation, parse the actual text export, and prove every stream remains within the verified vertex/index envelope with a matching `meshsettings` registration.

For every output, retain the export log and reimport or parse the actual `.mesh` or `.anim` bytes through the locked stack, saving the proof scene or parser report, measured geometry/action facts, output checksum, and any warnings. If the verified stack cannot re-import or parse that format, record an explicit `required installation/verification` or `blocked` result. A Blender viewport, provider preview, file existence, or plausible filename is not reimport evidence. Do not silently ignore exporter warnings, missing actions, unsupported material channels, or an absent parser.

Before final runtime wiring for every custom model consumer, including articulated units, decode or reimport the selected actual `.mesh` bytes and compare each `pdxmesh` `meshsettings.name` and `index` against the decoded object-node names and material-stream names and indices, then verify the shader and texture references. Provider labels, job slugs, prior-candidate names, file existence, and successful `.mesh`/`.anim`/DDS decoding alone do not prove material binding. Retain the byte identity and binding comparison in the runtime handoff, and repeat the check when the selected runtime mesh changes. The parent may perform this read-only decoding and binding review without reopening model production.

A visual variant that shares a unit's mesh and actions, such as an elite or regional company, gets its own diffuse texture processed under the variant's stem. Register it as a second `pdxmesh` that reuses the same mesh file and animations in a separate variants `.gfx` file, so rewiring the base unit cannot overwrite it, and as an entity `clone` of the base entity that overrides only `pdxmesh`, following the vanilla `clone = "artillery_entity"` precedent in `gfx/entities/units_artillery.asset`. Render the variants side by side at map scale before conversion.

For static map buildings, also audit the runtime consumer after reimport: the `.gfx` scale and shader, meshsettings object name, runtime mesh and DDS paths, building definition, and spawn policy must agree. A custom map building must not use vanilla `special_project_facility_spawn`. Use a dedicated `type = province` spawn pool for a direct map consumer, and define the matching `building_<spawn_point>` entity in the active `.asset` file. Different meshes must never share one spawn point because HOI4 resolves one map entity per spawn point. When every gameplay building level must appear, wire the gameplay building directly and provide one explicit spawn position per possible rendered level. Use a hidden provincial anchor only for an intentional single visual independent of gameplay level, place it with state-scoped `set_building_level`, and explicitly clean it up on conversion, dismantlement, annexation, or deletion. Leave automatic nudging enabled unless complete `map/buildings.txt` coverage is maintained; if nudging fails, preserve every vanilla row in a deterministic generated override and add complete custom coverage.

## Evidence package and handoff

The job package must contain, as applicable:

- job intake and append-only history
- immutable source artwork or documented failed-search fallback, `source_search.md`, provenance record, rights or authorization, source URL, creator or publisher, rights/reuse status, explicit AI-use restrictions, source-informed refinement prompt and processing record, source and refined-input checksums, source-to-refinement comparison, and final approval
- provider requests, responses, task IDs, versions, balance, estimated and consumed credits, `provider/credits/ledger.jsonl` and the `--credits-report` output, downloads, one-attempt rig/action ledger, and every retained passing result
- selected production/repair route, complete component inventory, Blender-authored geometry/rig/weight/action evidence, exact bounded operations, checkpoint hashes, and before/after deformation and role-motion review
- source and checkpoint `.blend` files
- geometry, material, rig, weight, action, and export reports, including the fail-closed gate records with every profile exception applied and the exporter reports
- Blender and extension versions, selected vanilla references, dependency-lock, route-schema and copy-provenance evidence, and the selected source-to-runtime hashes with the final synchronization result
- source and final textures, animation previews, `.mesh`, and `.anim`
- immutable Internet-sourced unit audio candidates, licensing records, derived files, transformations, and checksums
- export/reimport evidence, manifest, and requirement-to-runtime crosswalk
- a runtime handoff with proposed stable names, paths, material/shader mapping, action mapping, and the exact files/identifiers the parent must wire
- for every custom unit, a sound-design handoff with sourced audio files, source URLs, attribution, licensing evidence, sound roles, voice direction where applicable, vanilla precedents, animation synchronization points, proposed runtime identifiers, and remaining parent-owned wiring
- for every custom unit, a counter handoff with inspected installed-vanilla definitions and DDS files, matching skill-local counter family, exact consumers and tokens, required frames/states/sizes, original counter-art paths, final DDS paths, sampled exact vanilla green evidence, source and runtime hashes, native-size comparison evidence, parent review status, proposed sprite definitions, and remaining parent-owned wiring
- for static buildings, footprint/scale evidence, meshsettings object-name evidence, dedicated spawn or provincial-anchor evidence, and runtime-consumer evidence
- the meaningful validation performed, the meaningful validation skipped and why, every blocker and `needs_user_review` item, and the remaining parent work
- the clean static registration audit (below) once the parent has wired the model

Each model manifest entry records the asset ID/slug, profile, source mode, source-search record, immutable source reference and checksum, source URL or authorization, creator or publisher, rights/license and AI-use status, refinement mode, source-informed refinement prompt and processing record, refined-input lineage and checksum, source-to-refinement comparison and approval, selected production/repair route, firearm intent and weapon-free body proof where applicable, provider lineage and one-attempt ledger, selected candidate, required-component inventory, Blender-authored component/rig/weight/action evidence, checkpoint hashes, geometry counts, objects/materials, armature/bones, actions/frame data, custom-unit sound/effect synchronization, custom-unit counter consumers, inspected vanilla counter references, bespoke counter handoff and status, source/final textures, exports/checksums and per-stream limits, exporter version/settings, proposed runtime identifiers, actual runtime registration only after parent wiring, live consumer, in-game evidence only after parent validation, and status. Use `complete`, `needs_user_review`, `blocked`, or `canceled`; never create a fallback completion state.

When the event/system owner and slug are known, place the subagent handoff under the parent-provided `docs/plans/<owner_id>_<owner_slug>_plans/subagent_handoffs/` path. The parent must review every artifact and either wire it, queue it with a reason, reject it with a reason, or carry its blocker forward.

## Runtime copy synchronization

Treat the selected source exports, staged runtime copies, and active consumer files as separate surfaces. A runtime file can be stale or be overwritten by an older mapped texture even when the current source export is correct. Select the final geometry, material maps, and actions first, then lock the selected source paths in the manifest before synchronizing any runtime copy. Record each source and destination path, source and destination SHA-256, copy tool or actor, copy time, and provenance link, then compare destination hashes after synchronization. Never synchronize from an older provider or processed path, never let a filename alone choose the source, and never synchronize before final source selection. The parent owns active runtime copies, `.asset`, entity, `.gfx`, gameplay wiring, live consumers, and in-game screenshots; the worker owns the evidence and exact handoff needed to perform that work.

## Registration audit and in-game check

Both belong to the parent. The worker never launches HOI4.

**Static registration audit.** After the parent wires the mesh, animations, entity, unit sprite and `meshsettings`, run `py -3 -B .tools/audits/audit_asset_wiring_static.py --paths gfx interface common/units`. It reports `GFX-3D-*` errors for the mesh, animation, entity, unit sprite `<sprite>_entity`, `meshsettings` against the exported mesh, and textures. The handoff needs a run with no `GFX-3D-*` error.

**Entity names the audit does not check.** [vanilla-confirmed 1.19.4.1] An entity's `propagate_state` keys are `attach` names, not mesh `node` names. An entity `event` `particle` takes the `pdxparticle` name defined in a `.gfx` file, not a particle name from an `.asset` file.

**In-game check.** Unconfirmed: whether the console `moveunit` takes the `create_unit` script `id`, and the exact `hoi4_orders` arguments. The recipe has not been run; adjust those two commands when they differ and record what was used. Models load only at game launch.

1. Run the static registration audit above.
2. `hoi4_status`, `hoi4_launch restart=true` with the test mod in the playset, `hoi4_lock action=acquire purpose=unit-model`, `hoi4_load` a test-mode save, `hoi4_logs set_mark=model`.
3. Place the unit: `hoi4_eval_effect scope=<TAG> effect='create_unit = { division = "name = \"Model test\" division_template = \"<template using the new sub-unit>\"" owner = <TAG> prioritize_location = <province id> id = 9001 }'`.
4. Frame it: `goto_province <id>`, `nomapicons`, `nopausetext`, and zoom until the 3D model draws.
5. Idle: `hoi4_screenshot`, and `dbg_ue` to note the resolved entity.
6. Move: order the unit to a neighbouring province, step one day with popups stopped, and screenshot while it walks.
7. Attack: create an enemy division next to it, declare war, step one day, and screenshot.
8. Errors: `hoi4_logs log=error since=model`. A line naming the mod's mesh, anim, pdxmesh, entity or texture is a defect.
9. Release the lock, leave the game paused, and report the screenshots, entity name and log delta as agent-observed evidence.

## Bounded subagent route

Spawn `hoi4_3d_model_pipeline` without inherited conversation context, and put every needed constraint into the prompt or named repository files. The prompt must contain: the event, feature or system id and asset slug; the exact job root, output folders and handoff path; the approved reference/model-input paths and checksums, or the source/reference path or authorized source-search scope; source mode and status, with source permissions and explicit source/fallback authority; the asset profile; named vanilla references and the scale relationship; required components and actions; the selected route (see Route selection, chosen before provider calls); the job's approved `credit_budget` and the planned paid operations; the dependency lock; custom-unit sound roles and Internet-source requirements; custom-unit counter consumers and tokens, inspected vanilla counter definition/texture paths, the matching skill-local counter family and the counter-artist handoff path; synchronization requirements where applicable; and forbidden simplifications. The prompt must require the modern-artwork source-first gate, exactly one approved image per geometry task, and complete source-to-input evidence. If a required input is missing, the worker reports it instead of exploring the repository or guessing from invisible conversation state.

## Final state and fallback disclosure

Mark each requested 3D requirement as `complete`, `needs_user_review`, `blocked`, or `canceled` in the package. For a custom unit, the package must also record the sourced sound candidates, licensing evidence, synchronization handoff, bespoke counter package, mandatory vanilla-counter inspection evidence, and the status of parent-owned audio and counter wiring. A package-level `complete` means the worker's requested source, processing, export, sound-source research, counter handoff, and evidence outputs are present; it does not mean the repository runtime feature is complete. Report every omitted component, rejected candidate, unverified capability, budget stop, missing reimport proof, missing sound source, and proposed static companion explicitly. Never hide a simplification behind a successful export or a parent-owned runtime handoff.
