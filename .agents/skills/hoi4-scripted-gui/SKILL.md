---
name: hoi4-scripted-gui
description: Design, implement, repair, or review Hearts of Iron IV scripted GUI layouts using reference images, native controls, and active MCP live previews throughout construction.
---

# HOI4 Scripted GUI

Use this skill for scripted GUI composition, layout, interaction presentation, and visual acceptance, including attached decision displays and custom windows. It owns reusable GUI layout guidance.

Actively use MCP live previews while building or repairing a GUI: edit, render, inspect the images, correct defects, and rerender throughout implementation. Do not postpone visual review until the whole window is built or treat a final screenshot as a substitute for this loop.

`hoi4-decisions-missions` retains presentation-layer choice, gameplay action integrity, costs, requirements, AI equivalents, cleanup, and balance. Use `hoi4-feature-assets` for reference-image and final asset production, and `hoi4-frame-animation` when the accepted interface needs animation.

## Scope and source reading

Read `AGENTS.md`, the offline `Interface modding` and `Scripted GUI modding` pages alongside their required core wiki pages, installed vanilla documentation, and the linked source for the exact window. Installed vanilla `common/scripted_guis/_documentation.md` documents contexts, parent attachment, click effects and triggers, dynamic properties and lists, and dirty updates. Consult relevant localisation and script-concept documentation under the game's `documentation` directory, and inspect an exact vanilla precedent plus the closest existing project pattern.

For an attached visual meter, vanilla `interface/sov_paranoia_system_scripted_gui.gui` and `common/scripted_guis/SOV_paranoia_system_scripted_gui.txt` demonstrate separate background, meter, text, and dynamic-frame consumers. Choose a closer precedent when the requested interaction differs. Verify context-specific scope, variable, and event-target support against installed documentation and actual consumers. Inspect pointer lifecycle, stale-target handling, and cleanup instead of assuming support or prohibition from memory.

Name the authorized window, files, entry point, parent or context, linked assets, states, resolutions, and exclusions before editing. Route a dedicated UI introduced and owned by one named event to `hoi4_event_ui_worker` under `hoi4-subagents`. Shared event logs, event-detail frameworks, settings, super-event frameworks, shared registries, and unrelated interfaces remain parent-owned and require their own task authorization. Using this skill or opening a shared window does not authorize changing it.

## Reference image before implementation

Use the [vanilla interface review shelf](../hoi4-feature-assets/assets/vanilla_reference/interface/README.md) for native hierarchy, spacing, controls, and information-density precedents. Its five `interface/vanilla/` families are reference artifacts only; inspect the exact source consumer and retain fixture and fidelity limits. They are neither approved final art nor fresh MCP evidence for the target window.

Create reference image or images before implementing a new or redesigned scripted GUI. Use native ImageGen through the asset workflow, or use a supplied reference that already shows the intended design. Cover materially different layouts or states with additional images where necessary. For a small repair, create a scoped reference of the intended corrected layout, such as an annotated baseline or a reference edit of the affected region. Preserve the surrounding design instead of forcing a redesign. Keep references and their acceptance record in the owning task's design or asset workspace, never inside this reusable skill.

Follow the asset skill's [generated source art and review](../hoi4-feature-assets/references/generation-and-review.md), including truthful model-selection evidence and reference roles. For native layout references, retain the full render, source window/files, resolution, UI scale, and crop bounds, then crop review images to useful UI bounds. Use internally consistent scenarios without raw localisation tokens, contradictory panes, debug labels, or unexplained empty fields. If C++-bound content needs a fixture, use an isolated copy of the source with explicitly recorded text/state substitutions while preserving geometry, hierarchy, fonts, assets, and controls. Never edit installed vanilla or paint fake labels onto screenshots to fabricate a clean reference. A fixture is source evidence, not live-game proof.

Translate the reference as closely as feasible into a usable native HOI4 interface. Preserve composition, hierarchy, proportions, grouping, visual identity, and designed content regions while adapting impossible geometry, generated text or artifacts, unsupported effects, and styling that does not fit the inspected HOI4 family. Use real controls, live localisation, native lists and meters, accurate input regions, and wired states. A flattened picture of buttons or dynamic values is not an implementation. Decorative art may be rasterized, but interactive controls and changing information must remain functional elements.

Before source changes, record:

- reference paths and intended state and resolution
- acceptance basis: explicit user direction or the parent's recorded selection within the current authorization
- reference-region to native-element or ID mapping, including interaction, assets, and states
- engine constraints and justified deviations, with supporting documentation or source evidence
- missing assets and their production owners

A file's existence, placement in specs, date, or old status label does not establish approval. Existing authorization can support parent acceptance without another permission request. Do not silently drop behavior or substitute a fallback when adapting the image. Unresolved design changes follow the repository's acceptance rules.

## Required MCP visual review and optional rewrite

Use the installed `hoi4_agent_tools` service and discover the live schema before use. Tool exposure alone does not establish service health. The portable GUI routes are `hoi4.gui_inspect`, `hoi4.gui_render`, and `hoi4.gui_rewrite`; runtime adapters may expose provider-specific callable names. Inspection and rendering are read-only source operations. Rewrite is an optional applying and validation route.

Use `gui_render` as the live preview of current source after each meaningful layout, asset, text, or state-wiring change, including intermediate construction stages. Inspect the returned full-window image and affected detail or state views before proceeding to the next layout tranche; a tool success message or artifact path is not an image review. Fix visible defects in the current tranche and rerender the affected scenarios before building further on that layout. For a new window with no renderable baseline, record that absence and render as soon as the first native container is renderable, then continue the same preview loop. Keep intermediate source and scenario identities and findings in the owning task's evidence so the final handoff demonstrates iterative review as well as the final comparison.

1. Inspect the exact linked window before editing. Supply the window name with a valid explicit scenario for narrow inspection, and record source identity, hierarchy, parent or context, GFX, fonts, localisation, state logic, and click regions.
2. Render the baseline before editing, preserving full-window images and relevant detail, hierarchy, click-region, diagnostic, state, and resolution artifacts. Read the fidelity report, resolve supplied runtime values and flags, and inspect the actual images.
3. Create or select the intended reference and native-element mapping, then review the proposed source change against both reference and baseline.
4. Apply the authorized, reviewed edit through the normal source-edit workflow, or optionally use `hoi4.gui_rewrite` to apply and validate it. Keep dependencies and changed files inside scope and review the resulting source. When using patches mode, use exact single scalar assignment or value ranges; whole-line replacements spanning several assignments are rejected. `expectedSourceHash` belongs to patches mode and must not be passed to source mode.
5. Reinspect and rerender after each accepted change over the same named scenarios, values, states, resolutions, UI scales, language, and assets as the baseline. Compare matching before and after source versions and artifact images, then compare the result with the reference. Read [references/visual-review.md](references/visual-review.md) before any visual completion claim.

The optional rewrite transaction's automatic post-write or index validation and transaction success are not mandatory GUI completion gates. If it blocks or rolls back, review its diagnostics and current source bytes, then directly apply the already authorized, reviewed edit without another fallback approval solely because the rewrite route failed. Record the route failure and application method. Resolve actual source defects and complete the required MCP inspection, renders, click-region checks, and matched scenario and reference comparison. Do not change the installed MCP package or configuration merely to remove an internal check.

`gui_render` may expose a comparison scenario. Use it for supported scenario comparisons, not as an assumed snapshot of older source. There is no separately exposed GUI comparison tool: preserve pre-change artifacts and source identity, and compare them with matching post-change artifacts. Preserve exact manifest, source revision, and scenario identities. Never substitute whichever concurrent output has the latest filename.

For tabbed windows, prefer explicit per-control states. A global selected-state render can activate mutually exclusive tabs and create an impossible fixture. Keep fixture choices and provenance in the evidence manifest, not invented scenario fields. For exact regression fixtures disable generated scenarios where the schema supports it. Generated exploratory scenarios require a stable seed and do not replace explicit boundary cases. At 1920x1080 use UI scale 1; UI scale represents the game setting, not image enlargement.

Where supported, add visible, hidden, containment, and centering expectations against actual element selectors. Centering checks should use rendered glyph bounds when supported so they can catch a visually off-center label inside an apparently centered text box. A successful tool call or passing validation flag does not prove visual acceptance. Warnings and rendered defects still require review and correction.

Treat the production MCP render as the one-to-one in-game visual-review surface required by the repository instructions. Every visible defect in the in-scope GUI blocks completion, including warnings the tool does not classify as fatal. Never dismiss bad alignment, spacing, clipping, backgrounds, states, assets, or click regions as a renderer discrepancy or defer correction for lack of a separate game screenshot. The render does not execute the game: preserve fidelity limits and unverified behavior without using them to waive visible defects.

If required inspection or render evidence, artifacts, scenarios, or dependencies are unavailable, record the exact call, selector, error, and affected evidence as blocked. Source-only review is not equivalent. An incidental defect outside authorized scope becomes a parent-owned finding, not permission to edit another interface.

## Content and interaction budget

The player should identify current state, main pressure or objective, and useful next actions at a glance. Use meters, thresholds, icon states, stage frames, map cues, and concise labels instead of raw variable dumps or paragraphs.

Normally expose one primary mechanic value and at most two supporting values. Four simultaneously visible mechanic values is the hard ceiling on the current surface or state. A fourth needs a distinct decision, threshold, and consequence. Each visible value needs a stable name, unit or range or direction, meaningful states, consequences, a player response where intervention is possible, and a non-colour cue alongside consistent colour identity.

Normally show three to five primary actions per visible phase, with six as the hard maximum. Active missions or target controls should normally number one to three when sharing that surface. Phase, replace, or prioritize actions. Do not warehouse weak or duplicate controls in extra tabs. These budgets govern mechanic values and gameplay actions, not records in an authorized browser or list or ordinary navigation.

Main explanations normally fit in one to three short lines. A tooltip for one value or action normally fits in two to four. Explain meaning, causes, relevant thresholds, consequences, and the player's response close to the affected element. Avoid vague text, duplicated instructions, raw triggers, and long mixed cost strings. Use the decision skill's cost and action-integrity rules for gameplay-changing controls, including correct texticons, at most four spendable cost types, shared validation, payment and effects, AI equivalence, and cleanup. Every button-like element must be interactive, visibly disabled with a reason, or unmistakably decorative.

## Handoff and completion

Return exact changed files and identifiers, source precedents, reference images and acceptance basis, image-to-element and background mapping, justified native adaptations, asset and state coverage, and matched MCP before and after artifacts with scenario and source identities. Include intermediate MCP preview evidence and corrections, completed visual-review findings, content and action budget assessment, and the decision owner's action-integrity evidence where gameplay controls exist.

List blockers, unresolved diagnostics, missing assets, unavailable states, remaining parent integration, and every simplification explicitly. If none, say so with the evidence. Do not claim a complete GUI from source checks, a successful rewrite, or a single normal-state screenshot. The parent reviews final integration. Live-game validation belongs to the user under `AGENTS.md` and is not replaced by MCP evidence.
