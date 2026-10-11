# Formable state-puzzle template package

This directory is reference scaffolding for a formable decision whose central proof is exact control of installed-map states. The files are not loaded by Hearts of Iron IV: copy them into the feature- or system-owned `common/`, `interface/`, and `localisation/` paths, replace every `<PLACEHOLDER>`, and keep the manifest beside the owning implementation. Do not wire a skill-local template directly into runtime.

## Selection gate

Use the state puzzle when the player must read several separately qualifying states, alternate state groups, or a live territorial count. Each state is shown in its real map position as its own piece. Use the static category-picture option only when all of the following are true:

- The formable has one required state, or at most two adjacent states treated as one indivisible requirement.
- There are no alternate groups, sponsor/member counting rules, or state-by-state actions to explain.
- A per-state hover does not add meaningful information beyond the category description and decision tooltip.
- The picture can remain a static territorial overview without pretending to be a control surface.

If any condition fails, use the state puzzle. A static picture is never a substitute for missing exact-state qualification, live control detail, or a compact map that the player needs to inspect.

## Non-negotiable contract

1. **Installed geometry is authoritative.** Derive each state mask from the active installed `map/provinces.bmp`, `definition.csv`, and state history province membership. Never hand-draw outlines, use generated art, use a province blob as a state, or copy geometry from another map version. Record the source revision, province IDs, row-run or mask checksum, projection, and transparent bounding box in the manifest.
2. **One state, one piece.** Every required state has one manifest entry, one state-piece sprite family, one hover region, and one shared qualification call site. Shared borders must be rendered once or with an explicitly recorded seam rule so neighboring pieces assemble without gaps.
3. **Current state drives presentation.** Grey means unresolved and green means qualifying. Both variants retain an outline; the unresolved variant also uses a hatch or texture cue and the qualifying variant uses a check, solid inner keyline, or another non-colour cue. Colour alone is forbidden.
4. **Hover is factual and dynamic.** Hover text names the state and resolves current owner, controller, control result, and core result. It must handle absent owners/controllers and must not cache a stale country name. The hover area is the tight transparent bounding box for that state mask, not a full-map button or an oversized rectangle.
5. **One qualification source.** The state trigger is called by each state piece, the live qualifying count, the summary, and the formation decision availability. Do not duplicate owner/control/core logic in GUI-only branches.
6. **No world scan.** Do not add `on_daily`, `on_weekly`, or another whole-world iterator for this display. Prefer a live scripted-localisation count built from descending `count_triggers` checks over the same generated state wrappers. Use a country-owned count and dirty variable only when every relevant state change has a proven scoped refresh call; otherwise report the count as unresolved instead of scheduling a world scan.
7. **AI is not a GUI.** AI uses the same formation trigger and decision conditions without opening or clicking the human-facing puzzle. The puzzle contains informational icons only; it has no fake buttons and no AI-only shortcut.
8. **No animation.** State pieces, borders, hatches, status icons, and the static alternative are still sprites. Do not add `noOfFrames`, animation blocks, moving elements, pulse effects, or transform-only animation.
9. **No tuning literals in call sites.** Required counts, alternate-group rules, owner/controller/core policy, thresholds, refresh cadence, and any costs belong in the owning manifest, script constants, or documented tuning files. Layout coordinates are generated from the manifest projection, not hand-tuned independently in each file.

## Package files

| File | Purpose | Copy target | Runtime ownership |
| --- | --- | --- | --- |
| `state_manifest.schema.json` | Machine-readable contract for map revision, states, counting rules, projection, and sprite names. | Documentation or owner package. | Owner validates and preserves it; no loader is assumed. |
| `state_manifest.example.json` | Filled three-state example with an alternate group and exact-geometry provenance fields. | Copy, then replace all example IDs and hashes. | Feature/system owner. |
| `formable_state_puzzle.gui` | Compact decision-category container plus one generated state-piece entry pattern. | `interface/<owner>_formable_state_puzzle.gui`. | Feature/system owner. |
| `formable_state_puzzle.gfx` | Static unresolved/qualifying/hatch/border sprite registrations and optional category picture registration. | `interface/<owner>_formable_state_puzzle.gfx`. | Feature/system owner and asset owner. |
| `formable_state_puzzle_scripted_gui.txt` | Decision-category scripted-GUI binding, dynamic piece images, summary properties, and presentation-only AI contract. | `common/scripted_guis/<owner>_formable_state_puzzle.txt`. | Feature/system owner. |
| `formable_state_puzzle_scripted_triggers.txt` | Shared state, alternate-group, territory, and decision availability trigger scaffolding. | `common/scripted_triggers/<owner>_formable_state_puzzle.txt`. | Decision/system owner. |
| `formable_state_puzzle_scripted_effects.txt` | Bounded count refresh, dirty-variable update, and cleanup effect scaffolding. | `common/scripted_effects/<owner>_formable_state_puzzle.txt`. | Decision/system owner. |
| `formable_state_puzzle_scripted_localisation.txt` | Dynamic sprite selection and status/tooltip localisation scaffolding. | `common/scripted_localisation/<owner>_formable_state_puzzle.txt`. | Localisation/system owner. |
| `formable_state_puzzle_localisation.example.yml` | UTF-8 BOM example for category description, summary, state hover, and tooltip keys. | `localisation/english/<owner>_formable_state_puzzle_l_english.yml`. | Localisation owner. |
| `static_category_picture_option.md` | Gate and snippets for the genuinely simple one-state/small-shape alternative. | Owner documentation. | Feature/system owner. |
| `validation_checklist.md` | Task-specific acceptance checks and evidence record. | Owner plan or handoff. | Parent/owner reviewer. |

## Setup workflow

### 1. Lock the owner and state policy

Record the formable decision ID, owning country/route, category ID, state counting rule, alternate groups, required owner/controller/core semantics, subject/ally/occupation policy, route or reveal gates, and cleanup transition. Keep the AI decision trigger independent from the GUI. If a state is counted through a subject, ally, or alternate controller, say so explicitly in `counting_rules` rather than silently broadening a generic helper.

### 2. Build the manifest from the installed map

Use the currently installed map and the exact state-history file that the active game loads. For each state, preserve the state ID, localisation key, province IDs, geometry source, geometry checksum, map projection, canvas position, transparent bounding box, and all three sprite names. `state_manifest.example.json` shows the minimum record. A state sprite is a preprocessed mask plus the status treatment; it is not an image of a generic tile.

The canonical geometry evidence should include either the HOI4 MCP `map-province-geometry` artifact (row runs) or an equivalent reproducible extraction report. The manifest's `map_revision` must change when the installed map changes. Rebuild all pieces after such a change; do not stretch an old mask to fit.

### 3. Generate the GUI entries

Copy `formable_state_puzzle.gui` and emit one `iconType` per manifest state using the manifest's position and transparent bounding box. The icon's sprite is selected by the scripted-GUI property and its `pdx_tooltip_delayed` points to the state hover key. Keep the map canvas inside the decision category description width. The entry is an icon, not a button: informational state pieces must not expose a dead click action.

The GUI template intentionally contains placeholders for positions and state IDs. A copied runtime file must contain concrete IDs and coordinates generated from the approved manifest, not placeholder tokens or a second hand-authored projection. Use the same origin and scale for every piece and retain `clipping = yes` on the compact container.

### 4. Register static sprite families

Copy `formable_state_puzzle.gfx` and register, for each state, `unresolved`, `qualifying`, and `hatch`/border variants. The source textures must use the same state mask and projection. The unresolved variant is grey with a visible hatch or texture; the qualifying variant is green with a visible keyline/check cue. The sprite files belong under the owner asset package, normally `gfx/interface/formables/<formable_id>/states/`. Do not include skill-local paths in runtime GFX.

### 5. Wire the shared triggers

Copy `formable_state_puzzle_scripted_triggers.txt`. Implement one state-scope helper with the exact owner/controller/core policy, then call that helper from the generated state wrappers. The territory helper composes those wrappers and alternate groups. The decision's `available` block calls the territory helper directly. The GUI state visibility/status selection and the summary's final eligibility call the same helpers; never reimplement the state rule in localisation.

The generated state wrappers may use numeric state scopes, for example `<STATE_ID> = { formable_<FORMABLE_ID>_state_qualifies = yes }`, because state IDs are installed-map data. Avoid relying on event targets in scripted GUI: the offline Scripted GUI wiki explicitly warns that event targets break there. Use the decision-category country context and state arrays/variables only where the installed engine version has been verified to support them.

### 6. Calculate the compact summary without a world scan

The fixed-entry scripted-localisation template demonstrates a live count with descending `count_triggers` clauses over the same per-state wrappers used by the pieces. The first matching threshold supplies the exact numerator, requires no mutation, and cannot fall out of sync with the decision.

`formable_state_puzzle_scripted_effects.txt` remains available for owners whose verified GUI contract requires a country variable. Its refresh effect starts the count at zero, evaluates each manifest state through the shared helper, writes the country-scoped count, and changes a dirty variable. Call it only from every proven scoped owner/controller/state-transfer path. If complete event-driven coverage cannot be proven and direct trigger counting is not usable, report the summary count as unresolved rather than scheduling a daily or weekly scan.

The final formation decision must still call the territory helper at `available` time. A stale count can affect presentation only; it must never grant the formable or bypass the decision trigger.

### 7. Wire dynamic hover localisation

Copy `formable_state_puzzle_scripted_localisation.txt` and the UTF-8 BOM YAML example. The generated state entry supplies a state scope to the tooltip context (normally via the verified dynamic-list/state-scope pattern or an owner-generated fixed entry). Hover text must include the state name, current owner, current controller, current control result, and current core result. Keep the summary to one compact line such as `Qualifying states: 2 / 3 — Formation ready` and put requirement detail in the delayed tooltip.

Do not print raw variable names, map hashes, implementation notes, or hidden future outcomes in player-facing text. Do not put colour control codes in scripted-localisation definitions; use the project's established localisation formatting and pair status colours with the border/hatch cues in the sprites.

### 8. Validate before handing off

Run every item in `validation_checklist.md`, attach map geometry and GUI inspect/render artifacts, and record skipped checks with the exact reason. A skill-local package is not an in-game completion claim. The parent still owns runtime wiring, final source review, and live-consumer validation.

## Helper contract and migration map

These names are placeholders and must be namespaced to the owning formable. The contract is deliberately narrow so a future implementation can migrate duplicated checks safely.

| Helper | Scope | Inputs | Outputs | Side effects | Required call sites |
| --- | --- | --- | --- | --- | --- |
| `formable_<FORMABLE_ID>_state_qualifies` | State | Owner/controller/core policy from the owner package; `ROOT` is prospective formable carrier. | Boolean qualification for the current state. | None. | Every generated state wrapper, count refresh, and any state-targeted summary check. |
| `formable_<FORMABLE_ID>_state_<STATE_ID>_qualifies` | Country | Installed numeric `<STATE_ID>`. | Boolean qualification for that one state. | None. | Piece status/hover, count refresh, territory helper. |
| `formable_<FORMABLE_ID>_territory_qualifies` | Country | State wrappers and alternate-group policy. | Final formation eligibility boolean. | None. | Decision `available`, summary final-status trigger, AI-facing decision logic. |
| `formable_<FORMABLE_ID>_puzzle_refresh` | Country | Manifest state list; optional route/reveal flags already resolved by caller. | `formable_<FORMABLE_ID>_qualifying_count`, `formable_<FORMABLE_ID>_required_count`, dirty variable. | Mutates only scoped count/dirty variables. No map changes, no event targets, no world iteration. | Decision category/open refresh, every scoped state-transfer/control-change caller, formation completion cleanup. |
| `formable_<FORMABLE_ID>_puzzle_clear` | Country | None. | Cleared count/dirty/progress variables. | Clears only owner-owned temporary flags/variables. | Formable completion, route cancellation, target invalidation, country identity change. |
| `formable_<FORMABLE_ID>_state_piece_sprite` | GUI country/state entry | Current state scope and qualification helper. | One static GFX sprite key. | None. | `properties` for the state piece image. |
| `formable_<FORMABLE_ID>_state_hover` | GUI state entry | Current state scope and qualification helper. | Dynamic tooltip text. | None. | `pdx_tooltip_delayed` on every state icon. |

### Constants and tuning table plan

Do not put tuning values in this skill-local package. The owner should centralise shared values in `common/script_constants/<owner>_formable_constants.txt` or an owner-documented tuning file, including required count derivation, alternate-group minimums, control/ownership/core policy, category refresh limits, and any formation cost or integration duration. State IDs, province IDs, map hashes, projection bounds, and sprite names are manifest data, not tuning. Every unsupported dynamic field must be called out in the owner handoff; do not replace it with a magic literal.

### Event target and cleanup plan

The puzzle does not use event targets. Scripted GUI context cannot safely use event targets according to the offline wiki. Keep state pointers in the verified state-entry/dynamic-list scope or in short-lived country variables. If the owning gameplay chain needs a persistent scope pointer outside the GUI, it may use a regular/global event target in its own event/decision logic, but that target is not consumed by the puzzle and must follow the normal clear-on-completion lifecycle. `formable_<FORMABLE_ID>_puzzle_clear` clears count, dirty, stale route flags, and any selected-state variables on completion or cancellation.

### Migration from duplicated logic

1. Inventory every existing formable owner/control/core check in the decision, category, focus, event, tooltip, AI, and scripted-GUI files.
2. Copy the manifest and write the state-scope helper first. Prove the helper against the existing decision `available` trigger before changing presentation.
3. Replace decision availability and AI checks with `territory_qualifies`; preserve unrelated route, ideology, cost, and reveal gates around that call.
4. Replace each copied piece and summary branch with generated wrappers and the same helper. Remove only duplicate owner/control/core clauses; do not move mechanic design into the helper.
5. Add the bounded refresh effect and call it from existing scoped state-changing effects. Do not add a new on-action or world scan merely to feed the display.
6. Validate old and new decision results against the same named scenarios, then remove obsolete flags/variables after the parent confirms no other system reads them.

## Ownership boundaries

The template author owns the schema, examples, placeholder syntax, and validation guidance. The feature/system owner owns state policy, map extraction, generated geometry, runtime source wiring, costs, decision effects, route gates, AI weighting, integration missions, and final in-game acceptance. Asset work must preserve source masks and checksums; it must not silently redraw a state. Localisation owners keep the YAML BOM and player-facing wording aligned with the actual decision and summary. No file in this directory is a runtime gameplay file.

## Reference evidence used for this package

- Offline wiki: `paradox_wiki/Decision modding - Hearts of Iron 4 Wiki.md`, `Scripted GUI modding - Hearts of Iron 4 Wiki.md`, `Interface modding - Hearts of Iron 4 Wiki.md`, `Data structures - Hearts of Iron 4 Wiki.md`, `Triggers - Hearts of Iron 4 Wiki.md`, `Effects - Hearts of Iron 4 Wiki.md`, `Modifiers - Hearts of Iron 4 Wiki.md`, `Localisation - Hearts of Iron 4 Wiki.md`, `Scopes - Hearts of Iron 4 Wiki.md`, `On actions - Hearts of Iron 4 Wiki.md`, `Event modding - Hearts of Iron 4 Wiki.md`, `Idea modding - Hearts of Iron 4 Wiki.md`, `AI modding - Hearts of Iron 4 Wiki.md`, `Map modding - Hearts of Iron 4 Wiki.md`, and `State modding - Hearts of Iron 4 Wiki.md`.
- Vanilla documentation: `documentation/script_concept_documentation.md`, `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`, `documentation/dynamic_variables_documentation.md`, `documentation/loc_objects_documentation.md`, and `documentation/loc_formatter_documentation.md`.
- Vanilla precedent: `common/decisions/categories/AUS_decision_categories.txt`, `common/scripted_guis/AUS_antischluss_measures_scripted_gui.txt`, and `interface/aus_antischluss_measures_scripted_gui.gui`. It confirms a compact `decision_category` scripted GUI attached below category text and presentation-only scripted-GUI properties.
- HOI4 MCP read-only evidence: record the current repository's `hoi4.gui_inspect`, matching `hoi4.gui_render` artifact family, and `hoi4.map_inspect` or province-geometry artifact identifiers in the owner handoff. Do not copy artifact URIs from another repository or revision.

The MCP scans also reported pre-existing repository-wide GUI context diagnostics and map building/port-position diagnostics while inspecting vanilla references. They do not authorize changing runtime files in this task; the exact evidence and limitations are recorded in the handoff.
