---
name: hoi4-3d-model-pipeline
description: Create, rig, animate, convert, export, or repair custom Hearts of Iron IV 3D models and prepare their sourced sound and bespoke counter handoffs.
---

# HOI4 3D Model Pipeline

This skill owns bounded model-source production through Blender/PDX export and
evidence handoff. It does not own final gameplay, GFX/entity/sound wiring or the
overall in-game completion claim. Route portraits and other 2D art through their
dedicated skills; frame sheets use `hoi4-frame-animation`, not skeletal `.anim`.

## Required mode reading

Read [the production guide](references/production-guide.md) before job intake,
provider production, Blender processing/repair, custom-unit companion work,
export, or handoff. It is the full rule set: route selection, hard start gates,
credits and attempts, the job schema/layout, calibrated vanilla scale/material
rules, source rights, fail-closed checks, checkpoint and runtime-copy
discipline, audio/counter requirements, the registration audit and in-game
check, and completion boundaries. This file only points to it.

Read [source-reference policy](references/source-reference-policy.md) before
searching or approving a model input. Read [motion and repair QA](references/motion-and-repair-qa.md)
before standalone motion, retargeting, skeletal repair, material rebinding,
assembly yaw, or export acceptance. Read [live authoring](references/live-authoring.md)
before posing, keying, re-weighting or seating a prop by hand in a live Blender
session (small fixes and last resort only: rig with auto-rig tools and animate with researched presets first, per unit). Read only the other system/asset references
needed for the actual consumer; do not start provider/runtime operations for a
workflow-documentation task.

## Gates in one glance

Each gate is defined once in the guide:

- **Route**: choose it before any provider call ([Route selection](references/production-guide.md#route-selection-and-component-completion)).
- **Unit type and body**: a land unit names one `unit_type`, which sets its body preset, rig and animations; `measure_body.py <job>` checks the generation fits that body before any rig is paid for, and escalates a body no preset fits ([Unit types](references/production-guide.md#unit-types-and-the-unit-route)).
- **Files**: `check_unit_files.py` checks the exported bytes and the registration; `check_holes.py` renders the unit and fails holes larger than vanilla's own specks (on the provider `.glb` before the rig, and after export); `run_pilot.py --status` names the next step after any failure.
- **Generator**: Tripo is the default (`"provider": "tripo"`). It runs in the
  Tripo web app under the user's own sign-in, never through an API, and follows
  the route in `docs/3d-units.md`: a 3D-ready picture (neutral pose, empty
  hands), model, rig, candidate presets, export, clips picked by measurement
  with the map camera's readings as advice only (`pose_check.py --map`, the
  job's `tripo.posture`, TRIPO-MAP-*, D-140), `tripo_intake.py`,
  `run_pilot.py`, `tripo/tripo_checks.py`. Reviewers judge each clip on the
  designer preview sheet (`tripo/weapon_sheets.py --sheet preview`, 249 px
  tiles) and in close-up, and the still model on the game-size sheet. Work out the
  preset with `tripo/pick_preset.py` from plain answers about the picture,
  show the user its confirm sentence and wait for a yes, then write the job
  entry with `tripo/new_job.py --preset <preset>`, giving only what the
  user knows with `--set`. Do the picture review of step 2 in
  `docs/3d-units.md` (a Tripo job needs `init_pilot_jobs.py` for its picture
  too). Write the card with `tripo/make_card.py`, never by hand. Every unit
  type of a mod has its own clips: claim them with `tripo/anim_claims.py`
  as soon as they are picked (D-136). An armed unit names
  `tripo.weapon.hand` by the rig's side and gets its weapon from
  `tripo/arm_unit.py`. An unarmed soldier-sized
  unit takes `infantry_unarmed`. Every command that starts Blender waits for
  the machine first (`lib/heavy_job.py`). Never type the user's password. Proven on armed humanoids, a large creature, a mount, a
  plane and a ship. Winged units, tanks, buildings and landmarks are not
  proven yet.
- **Effects**: muzzle flashes, spells, fire and explosions are particles at
  locators, fired by entity events, never part of the model. Add them with
  `tripo/effects_stage.py` from the job's `effects` block (profiles the
  preset lists, and the unit's `setting`), look at `tripo/effects_sheet.py`,
  and list the in-game checks of `docs/3d-effects.md`. Each effect must fit
  the unit: a world without gunpowder never gets a muzzle flash.
- **Picture sources**: a 3D reference picture is made from existing
  references and research, never from a text prompt alone. Start from the
  subject's own reference (the owner's drawing, the mod's art), research real
  references for a real-world subject, give them to the image tool, and list
  them in the job's `reference_sources` and the card's Sources row. The
  picture review refuses a job without them.
- **Detail and look**: never simplify a subject, picture, clip choice or
  requirement to make a step easier or a check pass, and never change a look
  by a tint, filter or recolour of its texture. Change the method, or make a
  new picture and model, or ask the user. See the rules in `docs/3d-units.md`.
- **Key and dependencies**: an old Meshy job needs a nonblank `MESHY_API_KEY`
  first. Every job needs the reviewed dependency lock, Blender bridge and
  pinned io_pdx_mesh export support ([Hard start gates](references/production-guide.md#hard-start-gates)).
- **Credits**: one `credit_budget` per job, approved by the user once at job
  start; no paid retries ([Credits and attempts](references/production-guide.md#credits-and-attempts)).
- **Reference image**: one approved image per geometry task, visually reviewed
  by the parent before any paid call ([Exactly one reference image](references/production-guide.md#exactly-one-reference-image-per-meshy-geometry-task)).
- **Checks**: gates fail closed and every role needs anatomical multi-phase
  motion with exported-byte reimport proof. Sapient armed fighters (soldiers, riders, armed undead warriors, giants and other tool-using peoples) hold their weapon in hand, bound to a hand or forearm bone, and their attack clip swings it; a rigging fix moves the weapon into the hand, never removes it. Ents, mindless undead and animals attack with their own bodies. No two units of a mod share a clip in any state (idle, move, attack, defend, retreat, death), riders and mounts included, unless one is a reskin of the other (`reskin_of`, decision 3D-6): `plan_clips.py` plans distinct clips before any is paid for and UNIT-ANIM-SHARED checks the exports; the Meshy library is humanoid only, so mounts and other quadrupeds need their own authored gaits, distinct per mount ([Geometry, materials, rigging, and actions](references/production-guide.md#geometry-materials-rigging-and-actions)).
- **Independent visual review**: a unit is finished only after `review_unit.py`
  renders every clip and a reviewer with a fresh context, given only the
  sheets and `config/visual_review_prompt.md`, finds no defect. Never pass the
  reviewer your conclusions, never review your own renders in its place, and
  keep its reply as evidence ([Independent visual review](references/production-guide.md#independent-visual-review)).
  Every round gets the same request: the unit's fixed notes (`--note-file`, for an
  intended look such as a torn hem), the item-by-item checklist, and the same views.
  After fixes, review only the changed clips (`--clips`), then a full round with a new
  reviewer before acceptance (decision 3D-7).
- **Custom units**: defensibly sourced audio (including selection) and bespoke
  vanilla-green counters, or the package stays blocked ([counters](references/production-guide.md#custom-unit-counter-companion), [sound](references/production-guide.md#custom-unit-sound-design-companion)).

## Handoff

The worker hands off source/checkpoint/export lineage, task/credit records
(including the `--credits-report` output), meaningful QA, audio/counter status,
exact proposed runtime identifiers, and remaining work. The parent owns runtime
integration, a clean `GFX-3D-*` run of `.tools/audits/audit_asset_wiring_static.py`,
reviewed live-consumer evidence, and final completion
([Registration audit and in-game check](references/production-guide.md#registration-audit-and-in-game-check)).
Never launch HOI4 from the 3D worker.
