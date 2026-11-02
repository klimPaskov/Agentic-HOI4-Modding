---
name: hoi4-imagegen
description: Make Hearts of Iron IV graphical assets (40 families: focus, ideas, decisions, technology and event pictures, flags, portraits, counters and more) with the hoi4-imagegen MCP. Use for any new or replaced mod art that is generated or processed rather than hand-drawn. Covers plan, generate, process, validate, preview, review and install.
---

# hoi4-imagegen

Use the `hoi4_imagegen` MCP (tools `hoi4.image_*`). It owns canvas sizes, alpha, margins, DDS or TGA export, naming, versions and provenance, and it runs the processing of every family itself: the report card with its fixed shadow, the achievement triplet, the advisor card from the kit template, the portrait crop with the bundled YuNet detector, the flag ladder, the focus `_shine` sprite, frame strips, and a flat opaque picture for the opaque families. Do not build a second image pipeline, do not run the kit's Python tools by hand for an asset the tool makes, and do not write DDS files or sprite names by hand. HOI4 Mod Setup installs the binary and the project MCP entry. `hoi4-feature-assets` keeps the source rules, naming and handoff rules this loop follows.

## Tools
* `hoi4.image_status`, `hoi4.image_families` (the catalogue: every family's measured spec, the mod's override, its style sources), `hoi4.image_references`.
* Six generation tools, one per group, each with a **required** `family` that the schema checks: `hoi4.image_icon`, `hoi4.image_picture`, `hoi4.image_portrait`, `hoi4.image_flag`, `hoi4.image_unit`, `hoi4.image_interface`. Without `approve` they return a free plan. With `approve: true` and an `idempotency_key` they generate.
* `hoi4.image_generate`, `hoi4.image_edit`, `hoi4.image_process`, `hoi4.image_validate`, `hoi4.image_preview`, `hoi4.image_review`, `hoi4.image_install`, `hoi4.image_ledger`, `hoi4.image_cancel`.
* `hoi4.image_audit`: the cross-family reuse audit of the whole mod. Run it before the handoff.

## The 40 families
* Icon group (`hoi4.image_icon`): `focus`, `idea_spirit`, `idea_concern`, `officer_corps_spirit`, `decision` (also missions), `decision_category_icon`, `state_modifier` (also dynamic modifiers), `special_project_icon`, `raid`, `mio_department`, `mio_trait`, `mio_policy`, `bop_side`, `medal`, `agency_upgrade`, `operation_icon`, `commander_trait`, `personal_trait`, `doctrine`.
* Picture group (`hoi4.image_picture`): `report_event`, `news_event`, `decision_category_picture`, `operation_picture`, `technology`, `achievement`.
* Portrait group (`hoi4.image_portrait`): `leader_portrait`, `commander_portrait`, `operative_portrait`, `scientist_portrait`, `advisor_card`.
* Flag (`hoi4.image_flag`): `flag`.
* Unit group (`hoi4.image_unit`): `counter_large`, `counter_small`, `division_emblem`, `building`, `faction_logo`, `agency_logo`.
* Interface group (`hoi4.image_interface`): `modifier_stat_icon`, `gui_texture`, `super_event`.

## When not to use it
* Animation beyond a frame strip: `hoi4-frame-animation`. 3D models, rigs and exports: `hoi4-3d-model-pipeline`. Bring a finished frame strip under the ledger with `hoi4.image_process` and `import`.
* Sourced and user-provided art of one of the 40 families is not generated, but it is imported with `hoi4.image_process` (a required `family`) so its crop, validation, review and install run under the same ledger. An image of another family's size, or the pixels of an installed asset of another family, is refused.
* Real people. `hoi4-feature-assets` section 21 decides first: a grounded real identity uses an attributed source, imported through `hoi4.image_process`, never a generated likeness. Only wholly fictional identities are generated. Providers may refuse or treat differently images of real people, and the project may forbid a category outright.
* Art that is not an asset family has no route here, for example the single reference image of the 3D pipeline.

## Providers
* The ChatGPT login is the default local provider once you have run `hoi4-imagegen login` (a browser sign-in and a one-time risk note). Every image runs on gpt-6-luna at high reasoning effort, and the route refuses a response whose model or effort differs. The backend's own image tool chooses the quality and size, which the route cannot force, so check the pixels. It calls an undocumented backend that OpenAI does not support for other tools, and it is never part of a hosted deployment.
* Documented providers stay available: `OPENAI_API_KEY`, `GEMINI_API_KEY` (or `GOOGLE_API_KEY`), `FAL_KEY`, and a ComfyUI endpoint. Keys come from the environment only: never type one into chat, a file or a command. A plan with an explicit `provider` wins over the default.

## The loop (one asset at a time)
1. `hoi4.image_status`. Check that a provider is signed in or has its key, and that the model is not retired or deprecated.
2. `hoi4.image_families { family }`. Read the group (it names the tool), the canvas, margin, evidence, review questions, and the style sources with the reason each was chosen. The canvas is the mod's profile (`.tools/gfx/profiles.json`), vanilla by default. A canvas that differs from the vanilla default is a project choice: say so.
3. References first. Style references come from the mod first (its copy of the asset skill's `assets/` folder and its existing assets of that family) and from the vanilla shelf second, and the tool reports which it used and why. Vanilla references may always be sent to a provider when they help, so no flag is needed. Add approved images with `hoi4.image_references` (role and rights note) and save a style with `style_save`. Roles: `style_anchor`, `subject_anchor`, `geometry_anchor`. Never invent a source: ask the user for references when style matters.
4. The group tool with a `family`. Without `approve` it is the free plan. Read the estimate, its basis, the warnings and `approvals`, and tell the user the cost before generating. A plan with the same inputs gives the same id. The family is fixed from here on: an idea icon is never a focus or decision icon, and the tool refuses to treat it as one.
5. Call the group tool again with `approve: true` and an `idempotency_key` (or `hoi4.image_generate { plan_id, idempotency_key }`). One asset per call. Reuse the key when retrying: it replays instead of paying again. After an error with retry class `reconcile_first`, use `hoi4.image_cancel` with `reconcile` and never retry blindly.
6. `hoi4.image_process { candidate_id }`. The deterministic fit for the family. If it says `no_transparency_in_source`, the provider returned an opaque picture: regenerate with a model that has native alpha, or use a matte workflow only when the background is one flat colour.
7. `hoi4.image_validate { targets: [artifact] }`. The artifact's own family and its full check set always apply. Fix errors, then validate again. A pass is geometry only.
8. `hoi4.image_preview`. Look at the native-size panels first, then compare with the reference panels.
9. `hoi4.image_review`. Answer every rubric question honestly. Approve only if all are true, otherwise `changes_requested`, then `hoi4.image_edit` with a precise instruction and go back to step 6.
10. `hoi4.image_install { target, approval_id }`. The default `mode: handoff` writes the sprite into `docs/assets/<feature>/gfx_handoff.md`, and the main agent wires `.gfx`.
11. When the feature is done, `hoi4.image_audit`, and list what it found in the handoff.

## What it refuses (and why)
* Install without a passing validation, an approving review of the exact file, and unchanged hashes (file, raw candidate, plan).
* Overwriting any file it did not install. Pick a new asset name.
* Retired models, unknown models, extra references a model cannot take, and keys sent to unlisted hosts.
* Using one family's asset as another's: `GFX-FAMILY-MISMATCH` (the size belongs to another family) and `GFX-FAMILY-REUSE` (the same pixels are already installed for another family).
* Enlarging an icon more than 1.25 times.
* Fake transparency: an opaque result, or a drawn grey and white checkerboard.

## Where things land
`docs/assets/<feature>/source_png|processed_png|prompts|contact_sheets`, finals in the kit's feature-scoped folders (for example `gfx/interface/goals/<feature>/focus_<asset>.dds`), state in `.hoi4-imagegen/` (config, styles, plans, `ledger.jsonl`, records). Names are lowercase snake_case, and flags use the country tag.

## Facts to keep straight
* Canvas sizes are the mod's profile, vanilla by default (HOI4 1.19.4.1): focus 100x88, idea_spirit 60x68, idea_concern 64x64, advisor_card 65x67, decision 33x32, report 210x176, news 397x153 (black and white), flags 82x52, 41x26 and 10x7. `CATALOG.md` in the vanilla shelf lists the canvas of every family. A mod that settled other sizes lists them in its own `.tools/gfx/profiles.json` rows, and `hoi4.image_families` then shows the override next to the vanilla value. `gui_texture` and `super_event` have no vanilla canvas, so the mod defines them.
* Focus icons have a paired `_shine` sprite in vanilla. The handoff includes one, marked "pattern observed, game behaviour untested". Do not claim it is required.
* No text in art. Generated text is always wrong.
* In-game appearance is user-operated evidence this tool cannot give. Say "installed", not "verified in game".
* Never start Hearts of Iron IV to check an asset. List exactly what the user should look at in game.

## Examples
`examples/` (in the hoi4-imagegen repository) has five focus icons with shine sprites from one style, a national spirit set, a report and a news picture, a three-size flag, and a refinement edit.
