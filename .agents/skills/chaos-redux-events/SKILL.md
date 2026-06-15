---
name: chaos-redux-events
description: Use when implementing or updating Chaos Redux events.
---

# Chaos Redux Events

Use this skill for any Chaos Redux event work, including:

- adding or updating `chaosx.nr<ID>.*` event chains
- wiring event log, event details, evolutions, and world-end branches
- maintaining `docs/events/` event documentation
- updating the gameplay-facing event spreadsheet, including the `Manual_Scenarios` table for triggerable scenarios

Repository-wide reading and style rules live in `AGENTS.md`. This skill only adds the Chaos Redux event-specific implementation contract.

When an event implementation creates broad visible text, spawn `chaosx_localisation_auditor` before completion. When an event needs repeated dynamic logic across events, decisions, focuses, evolutions, logs, or GUI, use `chaosx_scripted_system_architect` before duplicating logic.

## Working model

In Chaos Redux, an event is not just an event block.

Treat every event as a contract across some or all of these surfaces:

- event definition and subevents
- random-event classification and registration
- auto-fire or runtime hooks
- shared scripted effects, scripted triggers, and script constants
- event logs, actor mapping, event-details content, and evolution views
- super-event image, localisation, and audio wiring
- decisions, ideas, AI, characters, unit templates, and more
- `docs/events/` documentation and spreadsheet

If a task seems to need custom one-off plumbing, first check whether the same behavior should become generic for future events.

### Custom subagent use during event implementation

For large or multi-surface event work, use project subagents to keep the main implementation pass focused.

- Spawn `chaosx_repo_explorer` before editing when the event touches many systems or when file locations are uncertain.
- Spawn `chaosx_asset_source_researcher`, `chaosx_generated_event_art`, and `chaosx_icon_artist` for actual visual asset packages according to `chaos-redux-event-assets`.
- Spawn `chaosx_super_event_text_researcher` and `chaosx_super_event_audio_researcher` for actual super-event research packages according to `chaos-redux-super-events`.
- Spawn `chaosx_improvement_loop_planner` after a meaningful implementation tranche when several new mechanics, country packages, formables, focus routes, decisions, scripted GUI surfaces, super-event candidates, or lore systems have been added and the event needs deeper connection. Do not spawn it again for the same event until the previous addendum is implemented, folded into specs, queued with a reason, or rejected.
- Spawn `chaosx_focus_tree_auditor` after creating or heavily changing focus trees.
- Spawn `chaosx_event_completion_auditor` before claiming a large event, event rework, or spec-driven implementation is complete.
- Spawn `chaosx_spreadsheet_doc_worker` after implementation when docs, catalog rows, manifests, route coverage tables, or spreadsheet-style records need to match the final repo state.

Subagents do not remove the main agent's responsibility to wire, review, validate, and report honestly.

## Spec and plan locations

Source event specs live under `docs/specs/<event_id>_<event_slug>_specs/`. Implementation should read those files as the main design source when they exist.

Subagent plans, expansion addenda, audit follow-up notes, and implementation handoffs live under `docs/plans/<event_id>_<event_slug>_plans/`. Plans are working documents. If a plan becomes accepted source design, merge it into the relevant spec.

## Spec fidelity and implementation quality

When implementing from `docs/specs/`, treat mapped content as acceptance criteria. Do not silently replace mapped mechanics, routes, countries, decisions, achievements, assets, or super-events with smaller fallback versions. If something must be merged, renamed, skipped, or simplified, report it in the completion notes with the reason and affected files.

Use dynamic factors for pressure, cooldowns, progress, chance, support, duration, costs, AI willingness, spawn strength, aid amounts, stage movement, and recognition when the spec calls for a living system. Flat values are allowed only as constants, caps, floors, or deliberate tuning anchors. Centralize shared values in script constants or documented tuning.

Do not implement major decisions, missions, focus rewards, GUI buttons, or event responses as political power or command power purchases by default. Use concrete costs and requirements from the spec when relevant: XP, equipment, manpower, fuel, trains, convoys, supply, stability, war support, local support, held states, unit presence, foreign access, intelligence exposure, or time pressure. Tooltips must explain blocked nonstandard requirements.

When the spec maps focus paths, implement a real tree, not a thin vertical chain. Preserve route locks, side branches, convergence points, hidden branches, crisis branches, AI weights, focus filters, varied icons, and branch payoffs. Rewards should vary across buildings, units, decisions, missions, advisors, identities, claims, cores, diplomacy, technologies, and mechanic changes. Do not fill trees with repeated new ideas, tiny modifiers, political power, stability, or war support.

When implementing starting or route ideas, wire their lifecycle. Negative, mixed, staged, or route-specific ideas should be removed, upgraded, replaced, worsened, or consumed by the mapped decisions, focuses, missions, wars, failures, or reforms. Avoid dead idea stacks that never change.

Mechanic variables must be visible somewhere meaningful, such as decision category text, scripted localisation, national spirit tooltip, scripted GUI, progress meter, or focus tooltip. Keep cause and effect readable. Values should be changed by the mapped decisions, focuses, missions, events, wars, state control, AI actions, and foreign influence. Use consistent localisation colours for important mechanic values and breakdowns.

Large decision systems must hide obsolete or irrelevant actions. Use phases, active caps, target pools, route locks, thresholds, emergency visibility, regional grouping, cooldowns, or cleanup flags. The category should show current playable actions, not every possible debug action.

If the spec defines achievements, implement the full achievement surface: tracking flags or variables, unlock triggers, disqualifiers, localisation, icons, docs, and any route or formable hooks. Do not convert hard achievements into automatic unlocks.

Before completion, check every visible asset named or implied by the spec: flags, ideology flags, cosmetic flags, leaders, portraits, focus icons, decision icons, ideas, achievements, faction emblems, report or news images, super-event images, UI sprites, animated sprites, and static fallbacks. Do not claim completion while required visible assets are placeholders unless the completion report says so clearly.

Do not generate real historical leaders, historical flags, or well-attested real symbols as fictional art. Source them, document source and license status when possible, and convert them to the required HOI4 format. Generated art is for fictional, symbolic, alternate, supernatural, or invented identities unless the user says otherwise.

Any new, released, restored, transformed, or event-managed country that is expected to fight needs starting forces and a reinforcement pathway. Implement dynamic starting units, templates, equipment and manpower assumptions, commander or officer handling when relevant, and later unit growth through decisions, focuses, depots, objectives, volunteers, foreign support, mobilisation, or special mechanics. Do not leave a serious fighting country as an empty tag unless the spec says so and explains why.

Major events and country-creation events need route-specific AI. Implement focus choices, decision choices, unit-raising choices, faction behavior, foreign influence behavior, rare variant handling, high-chaos exceptions, invalid-route blocking, and fallback behavior when preferred content becomes impossible.

Do not reduce major spec effects to tiny decorative modifiers. Important effects must change incentives, unlock content, move visible mechanic values, alter army or economy behavior, create a real tradeoff, or connect to later outcomes. Small modifiers are fine as support, not as the whole payoff.

## Parent and subagent implementation ownership

Patch-capable subagents are active by default inside the current task scope. Use them when a large event touches focus trees, decisions, country packages, localisation, GUI, scripted helpers, or assets at the same time.

Small subagent patches are allowed when they improve a specific surface without changing the event design. A decision subagent can vary costs, clarify tooltips, add cleanup, improve AI weights, and patch related localisation. A focus subagent can fix a route lock, prerequisite, bypass, focus AI, icon reference, small reward, or formable unlock hook. A country package subagent can patch tag setup, party names, focus loading, leader references, country localisation, simple starting setup, or existing formable requirements. A localisation subagent can patch dynamic text directly. A scripted-system architect can add narrow helpers and direct call sites when the repeated logic is already present.

The parent still owns final integration, docs, spreadsheets, event chain direction, completion claims, and any broad mechanic expansion. If a subagent sees a needed route family, new country package, new formable suite, new scripted GUI system, new event chain, or major balance redesign, it writes a plan under `docs/plans/<event_id>_<event_slug>_plans/` and stops.

Every subagent edit must produce a handoff under `docs/plans/<event_id>_<event_slug>_plans/subagent_handoffs/` when the event id and slug are known. The handoff lists changed files, identifiers, behavior before and after, meaningful validation, remaining gaps, and follow-up work for the parent.

## Event anatomy

- entry event: the canonical `chaosx.nr<ID>.1` start
- player-facing popup events: the things the player actually reads and clicks
- follow-up/news events: broadcast or consequence popups
- evolutions: mutation tracks inside the same event identity, distinct from baseline stage progression
- world-end scenarios and super-events
- triggerable scenario launch variants when the event has a manual sandbox or challenge setup
- connection with other events (meaning that events are not standalone and actually interact with each other)

### Evolution implementation

The implementation must preserve the design split between baseline stages and evolutions.

Baseline progression can use whatever state, flags, variables, decisions, or events the mechanic needs. Do not record every normal stage as an evolution unless the spec deliberately treats it as an evolution track.

For actual evolutions, the usual pattern is:

1. the evolution condition becomes available from the current campaign state
2. the evolved incident, track, or milestone fires through dynamic pacing (an evolution never happens instantly, it uses MTTH. It can take a good amount of time before an evolution happens, the base should be like 90 days, but it could be more or less, depending on the evolution. Some happen instantly, for events that haven't fired yet for example, which just makes the initial firing more intense)
3. set the shared evolution context variables
4. record the evolution log entry through the shared pipeline
5. unlock or adjust the new behavior, tag, decision set, focus branch, or rare variant

Event evolutions that gate content must respect the enable and disable UI. If an evolution is disabled, the gated path must have a clean alternate route or must be safely skipped. Do not leave required baseline progression locked behind a disabled evolution.

The shared context is:

- `events_log_evolution_event_id`
- `events_log_evolution_type`
- `events_log_evolution_stage`
- `events_log_evolution_tier`
- `events_log_evolution_actor` when the milestone belongs to a specific country

Then:

- gate the milestone with `is_current_evolution_enabled = yes`
- call `record_events_log_evolution_entry = yes`
- If a helper sets a `*_recorded` flag or unlocks follow-up content, set the shared evolution context before its `limit` and include `is_current_evolution_enabled = yes` in that same limit. Disabled evolutions must not set recorded flags that later stages, decisions, reports, or focus branches read.
- When a logged evolution has an actor, save the country as `events_log_evolution_actor` and set `events_log_evolution_has_actor = 1` immediately before `record_events_log_evolution_entry = yes`. Regular event targets cannot be manually cleared and can leak through an effect chain, so no-actor records must rely on the shared logger's default `events_log_evolution_has_actor = 0` behavior instead of raw `has_event_target`.

Implementation design rules:

- `event_id` ties the evolution to the parent event.
- `type` separates parallel mutation tracks inside the same event.
- `stage` is the milestone inside one mutation track, not the ordinary event stage.
- `tier` is display-oriented. Do not use it as a substitute for real logic state.
- When a track uses stage-specific incidents, wire the stage-specific display text across every event-log view that can show it: list/current view, history/detail view, event-detail view, selected-detail title, selected-detail body, and any stage-number or roman-numeral helpers needed by the highest stage.
- Use dynamic factor models for evolution chance, pacing, intensity, and aftermath.
- If an evolution creates a persistent country, make the country playable or meaningful enough for its expected lifetime.

### Event-log UI surfaces

Before changing evolution log display, identify the exact surface and keep the change scoped to that surface. Patch the actual GUI/localisation/scripted data path; do not record a process note as a substitute for fixing the visible row.

- **Main Evolutions tab** uses `global.events_log_evolution_view_*`, `events_log_evolution_index`, and `events_log_evolution_entry_*` templates. This is a global logged-evolution history surface. Rows should visibly show the log index, date, source event, evolution name, tier, and stage.
- **History details related evolutions** uses `global.events_log_history_detail_evolution_*`, `events_log_history_detail_evolution_index`, and `events_log_history_detail_evolution_entry`. This is the selected-event filtered logged-evolution history surface. Rows should use the same visible metadata as the main Evolutions tab.
- **Event details evolution catalog** uses `global.events_log_event_detail_evolution_*`, `events_log_event_detail_evolution_index`, and `events_log_event_detail_evolution_entry`. This is a catalog/preview surface, not a history log. Do not add fake log indexes, fake dates, or history-only metadata here.

When adding evolution row metadata, reuse the arrays for that row surface: main rows read the `global.events_log_evolution_view_*` arrays rebuilt by `rebuild_events_log_evolution_view`, while selected-history rows read the `global.events_log_history_detail_evolution_*` arrays rebuilt by `events_log_rebuild_history_details_view`. The required row metadata is sequence, date, source event, type/name, tier, stage, actor, and enabled state. If the user reports row alignment, patch `interface/chaosx_events_log_popup.gui` row sizes, button bounds, and text widths for the affected surface in the same change.

## World-end scenarios

A world-end scenario is a terminal branch that changes the campaign into a resolved or end-state condition, not just a large disaster or strong major event. World-end scenario is chosen based on the world state. World-end scenario can only be triggered when the chaos value is over 1000.

### World-end scenario implementation

The normal contract is:

1. guard the branch with `NOT = { has_global_flag = world_end }`
2. set `world_end`
3. set a scenario-specific global flag
4. set the matching `super_event_visible`
5. update the matching super-event text, image, and audio wiring
6. stop or gate incompatible future systems and branches
7. document the end-state in the event doc, and spreadsheet

## Triggerable scenarios

Triggerable scenarios are manual sandbox or challenge setups launched from the Chaos Redux settings UI. They are separate from the normal random-event timer, chaos-tier eligibility, evolution pacing, and automatic source-event prerequisites.

Core rule: a triggerable scenario is always directly fireable from the scenario UI unless the launch would be impossible or conflict with an active terminal state. It creates instant chaos from setup controls, not from live Chaos Meter progression.

Use this contract when adding a scenario for an event:

1. Register a stable scenario ID and sort value in `triggerable_scenarios_initialize_registry`.
2. Add tuning constants in `common/script_constants/chaosx_triggerable_scenarios_constants.txt` for scenario IDs, sort values, intensity stops, scenario type IDs, and scale values.
3. Add or update launch, registry, sorting, intensity, and type effects in `common/scripted_effects/chaosx_triggerable_scenarios_effects.txt`.
4. Add launch eligibility in `common/scripted_triggers/chaosx_triggerable_scenarios_triggers.txt`.
5. Add scripted GUI click handling, dynamic list support, slider stops, and visibility checks in `common/scripted_guis/chaosx_scripted_gui_settings.txt`.
6. Add scenario name, sort text, detail text, type labels, and intensity impact text in `common/scripted_localisation/chaosx_scripted_localisation_scenarios.txt`.
7. Add or update player-facing labels, tooltips, confirmation text, and scenario event text in `localisation/english/chaosx_gui_l_english.yml`.
8. Update `interface/chaosx.gui` only when the existing scenario window cannot present the new controls cleanly.
9. Document the scenario in the relevant event doc or scenario doc, for example in `~\projects\chaos_redux\docs\systems\triggerable_scenarios.md`.

The scenario window is data-driven. It should use `global.triggerable_scenario_view_ids` for the sortable list, log-style entries for scenario rows, and a detail panel that updates from the selected entry. Do not hardcode one button per scenario when the registry and dynamic list can handle it.

The scenario button should open a confirmation window. Confirming must read the selected scenario, type, and intensity at launch time. Do not bake these values into the first click.

Intensity uses the existing four-stop scenario slider:

- Low
- Medium
- High
- Maximum

The selected intensity should be stored in `triggerable_scenarios_intensity`. The knob position, impact text, and launch effects must all read the same stored value. If a scenario deliberately ignores intensity, state that in its detail text and keep the slider harmless.

Scenario type controls are scenario-specific. If a scenario has types, define type constants, cycle buttons, labels, detail text, and launch branches.

Launch gates are not normal event prerequisites. They should only block impossible or conflicting launches, such as a required source country not existing, a required target scope being impossible to build. Do not block a triggerable scenario because chaos value, chaos tier, prior event state, evolution unlocks, date gates, route prerequisites, or super-event history flags are missing.

When a triggerable scenario needs to force a path that is normally gated, use an explicit scenario launch flag or variable. Scope the bypass tightly to the launch effect and clear it when the scenario setup is finished so automatic event behavior remains governed by normal event state.

Triggerable scenarios may call source-event helpers, unit-spawn helpers, release helpers, super-event helpers, or world-end helpers, but the scenario wrapper owns manual setup choices, intensity scaling, scenario type routing, confirmation flow, and bypass cleanup. Shared helpers must stay idempotent when the scenario and normal event chain can both call them.

The scenario UI normally reuses existing Chaos Redux and vanilla UI assets. Do not request dedicated scenario art, report images, icons, or animated UI unless the user asks for them or the existing scenario window cannot communicate the mechanic. If the UI requires a sprite entry for technical reasons, register a stable placeholder path and report that it is a placeholder.

Completion for a scenario-backed event requires:

- scenario ID and sort registration
- launch effect and confirmation flow
- launch eligibility using the same gate for click enablement and button state
- intensity and type controls wired
- scripted localisation and GUI localisation
- bypass flags scoped and cleaned up
- no normal chaos, evolution, date, route, or super-event-history prerequisite blocking manual launch
- documentation updated without listing stale or implementation-only debug details

## Major-event defeat aftermath

Some major events should also have a structured aftermath when the threat is beaten.

Use a defeat aftermath package when all of these are true:

- the defeated threat was global or near-global in reach
- the campaign lasted long enough to feel like a world crisis
- the cost in casualties, destruction, or political disruption was high enough that the world should not simply snap back to normal

Typical aftermath content:

- a defeat super-event or defeat-stage super-event effect
- postwar treaties, compacts, or new world orders
- recurring remembrance, reconstruction, or vigilance events
- lasting ideas, tech-sharing groups, or diplomatic rules that exist because the world learned from the crisis

Do not add a treaty/new world order after every contained or short-lived disaster. Those only make sense when the event genuinely reshaped the campaign.

## Event implementation workflow

### 1. Classify the event first

- Entry events keep the format `chaosx.nr<ID>.1`.
- Keep related subevents in the same namespace.
- Decide whether the event belongs in:
  - `global.major_events`
  - `global.repeatable_events`
  - `global.fire_once_events`
- Decide which pieces are:
  - hidden bootstrap/runtime events
  - player-facing popup events
  - news follow-ups
  - baseline progression events
  - evolution tracks
  - escalation events
  - world-end or super-event branches
  - aftermath content

Keep IDs stable when updating existing chains.

### 2. Map touched systems before editing

Always start from the event and walk outward through the systems it touches.

Core files to check:

- `events/<ID>_my_event.txt`
- `common/on_actions/chaosx_on_actions_system.txt`
- `common/scripted_effects/chaosx_logic_effects.txt`
- `common/scripted_effects/chaosx_events_log_effects.txt`
- `localisation/english/chaosx_event_names_l_english.yml`
- `localisation/english/chaosx_events_l_english.yml`
- `common/scripted_localisation/chaosx_scripted_localisation_debug.txt`
- `common/scripted_localisation/chaosx_scripted_localisation_events_log.txt`

Frequently-needed companion files:

- `common/on_actions/chaosx_on_actions.txt`
- `common/scripted_effects/chaosx_settings_effects.txt`
- `common/scripted_guis/chaosx_scripted_gui_events_log.txt`
- `common/scripted_guis/chaosx_scripted_gui_settings.txt`
- `common/scripted_guis/chaosx_scripted_gui_super_events.txt`
- `interface/chaosx_events_log_popup.gui`
- `interface/chaosx_super_events.gfx`
- `common/scripted_localisation/chaosx_scripted_localisation_super_events.txt`
- `localisation/english/chaosx_gui_l_english.yml`
- `common/script_constants/*.txt`
- `common/scripted_triggers/*.txt`
- `common/scripted_effects/*.txt`
- `common/decisions/*.txt`
- `common/decisions/categories/*.txt`
- `common/ideas/*.txt`
- `common/ai_strategy/*.txt`
- `common/ai_templates/*.txt`
- and possibly more. Some events can truly touch all systems.

### 3. Register the event in the random-event system

Update the event system registration in the same change.

Required checks:

1. Add or keep the event ID in the correct array inside `initialize_event_categories`.
2. Keep the event classification aligned with the actual gameplay behavior.
3. Make sure `get_event_type` can resolve the ID through the registered arrays.
4. Keep debug/event-log name mappings aligned with the registered ID.

Do not add an event script and leave the event system unaware of it.

### 4. Handle supporting gameplay systems

An event always needs more than its own script file.

Touch the relevant systems in the same change:

- decisions and categories if the event creates player tools, responses, or for example containment mechanics
- ideas or dynamic modifiers if the event creates persistent gameplay state
- AI strategies or templates if the event changes how AI should respond
- special-country exclusions if the event touches broad civilian, political, migration, or ideology systems
- shared country classification when the event creates or manages chaos countries: register every such country in `is_special_chaos_country` in `common/scripted_triggers/chaosx_dynamic_triggers.txt`, document it in `common/scripted_triggers/chaosx_dynamic_triggers.md`, also register/document it in `is_actual_nonhuman_country` when it is actually nonhuman, and avoid adding separate event-local classification triggers for the same concept
- and much more

When a decision, focus, or event option grants a one-time package through a shared helper effect, make the helper idempotent with a country/global flag and keep availability triggers aligned with that flag. Reused helper effects should be safe to call from later follow-up branches without duplicating manpower, equipment, PP, XP, or pressure adjustments.

When a decision fires a follow-up popup whose options need computed state from the decision, do not put those state variables in the decision's generic cleanup helper. Keep only immediate aid/cost variables in the cleanup helper, preserve the popup option state as scoped country variables, and clear that option state from each event option after it is consumed.

When a contest, rivalry, charter, or settlement event is meant to change later behavior, have each option set a persistent outcome flag and route future decisions/events through a small aftermath helper that reads those flags. Prefer this event-driven persistence over daily/weekly polling, and document which later action consumes the flags.

When custom or special tags can qualify for multiple named systems through broad eligibility triggers, route focus hooks by explicit tag groups before calling the shared helper. Do not let a broad first-match order decide which faction/system the tag joins. encode the intended mapping in the hook and let already-joined members use a maintenance/strengthening effect instead of creating a second membership.

If you add a new reusable dynamic scripted effect (an effect that could be generalized for all events), document it in `common/scripted_effects/chaosx_dynamic_effects.md` in the same change.

### 5. Event log integration

Events must appear in Chaos Redux’s event log, wire the full log contract in the same change.

Script ownership:

- Put history/evolution recording, actor sanitizing, default actor mapping, Event Details catalog rows, event-detail evolution previews, and History/Evolutions/Events tab rebuild logic in `common/scripted_effects/chaosx_events_log_effects.txt`.
- Keep random selection, fired-event handlers, timers, and event type accounting in `common/scripted_effects/chaosx_logic_effects.txt`; those effects should call the shared Event Logs recorders rather than defining log arrays themselves.
- Keep settings controls and generic event firing helpers in `common/scripted_effects/chaosx_settings_effects.txt`. Do not add new event-log history/evolution display logic there unless the settings window itself is changing.
- Keep button click routing in `common/scripted_guis/chaosx_scripted_gui_events_log.txt`, and layout changes in `interface/chaosx_events_log_popup.gui`.

Required name plumbing:

- add or update visible event-name loc in `localisation/english/chaosx_event_names_l_english.yml`
- update event-name selectors in `common/scripted_localisation/chaosx_scripted_localisation_events_log.txt`
- update debug-name selectors in `common/scripted_localisation/chaosx_scripted_localisation_debug.txt`

Required actor plumbing when a flag should appear:

- update `events_log_set_default_actor_for_current_event` in `common/scripted_effects/chaosx_events_log_effects.txt`
- use a default actor only when the event should show a meaningful actor before or without a fired history row
- if fired history should override the default actor, keep the history-context flow intact
- for random-event history rows, remember that the generic fired-event handler records the row before the target event's `immediate` block runs; if the actor is created or refreshed inside that event, move that preparation into a shared pre-fire helper and call it before `record_events_log_history_entry`
- for evolution rows with actors, save the country as `events_log_evolution_actor` and set `events_log_evolution_has_actor = 1` immediately before `record_events_log_evolution_entry = yes`; no-actor entries should let the shared logger default `events_log_evolution_has_actor` to `0`

Required detail-view plumbing:

- update the event-details text selectors in `common/scripted_localisation/chaosx_scripted_localisation_events_log.txt`
- update the actual user-facing text in `localisation/english/chaosx_gui_l_english.yml`
- if new generic event-log behavior is needed, wire it through:
  - `common/scripted_effects/chaosx_events_log_effects.txt`
  - `common/scripted_guis/chaosx_scripted_gui_events_log.txt`
  - `interface/chaosx_events_log_popup.gui`

Do not hardcode one-off GUI behavior if it should be reusable by later events.

When it's impossible for an event to fire due to conditions (the actor country doesn't exist, prerequisite not fulfilled, etc), always show `N/A` in the event list in place of a `0` for the weight.

### 6. Event cluster integration

Event clusters are a catalogue layer above normal random events. The Clusters tab must show every registered cluster, while History shows only clusters that actually fired.

Core files:

- `common/script_constants/event_cluster_constants.txt`
- `common/scripted_effects/chaosx_event_cluster_effects.txt`
- `common/scripted_effects/chaosx_events_log_effects.txt` when event-log view state changes
- `common/scripted_effects/chaosx_settings_effects.txt` when settings controls or generic event firing helpers change
- `common/scripted_guis/chaosx_scripted_gui_events_log.txt` when cluster log UI behavior changes
- `interface/chaosx_events_log_popup.gui` when cluster list/details layout changes
- `common/scripted_localisation/chaosx_scripted_localisation_events_log.txt`
- `common/scripted_localisation/chaosx_scripted_localisation_settings.txt`
- `localisation/english/chaosx_gui_l_english.yml`

To add a new cluster:

1. Add an ID in `event_cluster_id`.
2. Add any cluster-specific tuning group, for example `event_cluster_<slug> = { unlock_tier cooldown_days }`.
3. Register the cluster in `initialize_event_cluster_definitions` by pushing aligned entries into `global.event_clusters`, `global.event_cluster_type_entries`, and `global.event_cluster_unlock_tier_entries`.
4. Map member events in `event_belongs_to_cluster`, from normal event ID to cluster ID.
5. Add ordered member rows in `load_event_cluster_members`.
6. Add or update cluster name/type/description scripted localisation and GUI localisation.
7. If it needs custom runtime setup, add that branch to `event_cluster_prepare_runtime_context`.
8. If it needs a custom cooldown or one-time state, update `mark_event_cluster_fired_state` and any availability logic in `can_event_cluster_fire`.

Member attributes are parallel arrays in `load_event_cluster_members`:

- `temp_event_cluster_member_event_id_entries`: normal event ID.
- `temp_event_cluster_member_role_entries`: `event_cluster_member_role.required` or `event_cluster_member_role.optional`.
- `temp_event_cluster_member_chance_entries`: participation chance for optional members, usually from `event_cluster_member_participation`.
- `temp_event_cluster_member_min_tier_entries`: minimum chaos tier for that member.
- `temp_event_cluster_member_danger_entries`: display severity in cluster details.

To change a member's behavior, edit those attributes together. Do not reorder one array without the others.

Member severity uses four values:

- Low
- Medium
- High
- Severe

Cluster firing rules:

- Automatic cluster firing happens from `try_fire_event_cluster_for_selected_event` after a member event is selected.
- Automatic firing respects cluster unlock tier, cooldown, one-time state, member eligibility, optional participation rolls, and runtime context.
- Manual firing from Settings uses `force_fire_event_cluster_by_temp_id`. it bypasses tier, cooldown, disabled-state, and member availability checks. Runtime context can still fail if the event cannot build the required scopes.
- Cluster history rows are recorded by `record_events_log_cluster_entry`. cluster catalogue rows are rebuilt by `rebuild_events_log_cluster_view`.

### 7. Duration fields and constants

Use `script_constants` for shared tuning, but remember that some duration fields reject both `constant:` and variable tokens.

Known sensitive fields:

- `set_country_flag = { days = ... }`
- `set_global_flag = { days = ... }`
- any other timed field that throws `Malformed token` for either `constant:category.key` or a variable token

For those fields, use a file-scoped `@NAME = literal` constant in the same script file and pass `days = @NAME`. Keep the value mirrored with the matching `common/script_constants/` tuning entry, and update both in the same change.

Do not work around this by setting a temp variable and passing `days = temp_name`. those fields can reject variable tokens too. In which case, a `meta_effect` must be used if possible.

### 8. Super-event integration

If the event shows or drives a super event, wire the whole package:

- choose the slot intentionally
- set `super_event_visible`
- set `global.current_super_event_audio_id`. Every super event has a unique audio. Copy an existing audio and use it as placeholder, so that I can replace it with the real track later.
- use the settings-aware playback helper rather than bypassing it
- update scripted localisation in `common/scripted_localisation/chaosx_scripted_localisation_super_events.txt`
- update image wiring in `interface/chaosx_super_events.gfx`
- update player-facing localisation in the correct `.yml` files
- also update the .html documentation of music files correctly. If you can't get all the info from the file metadata and the user didn't provide the author or the name of the piece, then ask the user to do so.

Use `chaos-redux-super-events` whenever an event includes a super-event.

That skill handles super-event title direction, description tone, quote research, cultural remark selection, audio research, source documentation, and super-event presentation rules.

This skill handles implementation wiring: slot, flags, localisation, image, audio ID, scripted localisation, `.gfx`, docs, and spreadsheet updates.

### 9. World-end integration

If the event can produce a terminal scenario:

- keep the world-end flagging explicit and centralized
- make sure the terminal branch is distinguishable from ordinary major-event escalation
- gate later random events, branches, or systems that should no longer operate after the terminal state
- make the docs and spreadsheet, all agree on what the terminal branch actually is

If the branch is dramatic but not actually terminal, treat it as a major escalation evolution or super-event instead of world-end.

### World threat framework

If an event or mechanic creates an existential external threat that should push other systems toward cooperation, integrate it with the shared world-threat framework instead of inventing a new one-off flag.

Current shared state:

- aggregate flag: `world_in_threat`
- source-count variable: `global.world_threat_source_count`
- current source flag: `world_threat_source_zombies`

Implementation pattern:

1. create or reuse a threat-specific source flag
2. write a threat-specific refresh effect that sets or clears that source flag from real gameplay conditions
3. update `refresh_world_threat_state` in `common/scripted_effects/chaosx_dynamic_effects.txt`
4. expose reusable scripted triggers if other systems should read the new source directly
5. document the threat source in the mechanic doc

Do not create a parallel global "cooperation crisis" or "threat active" flag for a single event chain. Everything should fold back into `world_in_threat`.
The exact purpose of that flag is not yet planned.

## Documentation rules

Event-specific documentation belongs in `docs/events/`.

Preferred naming pattern:

- `docs/events/<zero_padded_id>_<slug>.md`, so exactly like with event script files.

Keep one canonical doc per event chain instead of splitting mechanics across multiple top-level docs unless the user explicitly asks for that.

Event doc structure:

1. What the event is.
2. Event map and subevents.
3. Trigger and runtime flow.
4. Main gameplay effects.
5. Supporting systems touched.
6. AI behavior if relevant.
7. Baseline progression, evolution tracks, and escalation flow if relevant.
8. World-end and super-event integration if relevant.
9. Connections with other events if relevant.
10. Asset wiring and sprite expectations if relevant.
11. Limitations if any.
12. Open tuning notes and future expansion ideas.

### Docs and gameplay must stay aligned

When mechanics change, update the matching event doc in the same change.

Do not leave the doc describing:

- old triggers
- old cooldowns
- old stage counts
- removed branches
- removed assets
- outdated spreadsheet or deck expectations

## Event catalog spreadsheet

Maintain the gameplay-facing event table in:

- `docs/spreadsheets/chaos_redux_events_catalog.xlsx`

Rules:

- use the `xlsx` skill
- write for players, not script readers
- don't put effects into descriptions
- focus on what happens in play
- keep the `Details` field aligned with the event-details window description
- keep evolution and world-end columns aligned with the real chain structure
- do not put baseline progression stages into evolution columns unless they are actual mutation tracks

## Event presentation workflow

Use this when the user asks for event slides, a showcase deck, or presentation updates.

Required tools and order:

1. `pptx`
2. `theme-factory`
3. `canvas-design`
4. LaTeX rendering when formulas or gameplay math need to be shown clearly

Visual standard:

- minimalistic
- stark
- propaganda-poster energy
- 1984-inspired restraint
- strong contrast
- deliberate negative space
- bold composition
- no generic corporate deck styling

Rules:

- every slide gets original event-specific art
- evolutions should visibly mutate the event, not merely show the next ordinary stage
- terminal branches should get heavier final-slide treatment
- keep deck path and asset folder stable unless the user asks otherwise

Preferred deck path:

- `docs/presentations/chaos_redux_events.pptx`

### Extra rules to follow

Event Details text must never display mechanical effects. The Event Details window, spreadsheet `Details` field, and player-facing detail summaries should describe the situation and premise, not list rewards, penalties, modifiers, variable changes, or script effects. If an event is meant to apply gameplay effects immediately regardless of which option the player chooses, place the real effects in the event `immediate` block inside a `hidden_effect`. The option should not reapply those effects. The option may show the immediate result only through a custom tooltip for cosmetic clarity, so the player sees the consequence without turning Event Details into an effects list.

If the event creates or manages non-standard countries, account for that in shared classification triggers. Any event-created or event-managed chaos country must be registered in `is_special_chaos_country` in `common/scripted_triggers/chaosx_dynamic_triggers.txt` and documented in `common/scripted_triggers/chaosx_dynamic_triggers.md`. If that chaos country is actually nonhuman rather than merely unusual, supernatural, extremist, or scenario-specific, also register it in `is_actual_nonhuman_country` and update the same documentation. Do not create event-specific duplicate classifiers such as `is_<event>_chaos_enemy`, `is_<event>_special_country`, or per-event nonhuman triggers when the shared triggers can express the category. Events interact with each other, so systems that usually affect normal countries, such as black plague, mass panic, civilian migration, or ideology spread, should exclude zombie, alien, and other nonhuman countries through the shared triggers instead of one-off checks.

When an event can create a normal tag that may also already exist from vanilla, another mod, or prior campaign state, track whether the event actually created it before loading a runtime focus tree. A good pattern is to set a country flag immediately after `release = TAG` and have the focus-tree loader check that flag before `load_focus_tree`. Existing tags with their own meaningful trees should get crisis ideas, decisions, events, or additive branch integration, not a blind replacement tree.

When auditing event-created country packages, verify the whole playable-country surface, not only the release effect. Check country files, history files, tag registration, base localisation, ideology-specific cosmetic localisation (`TAG_democratic`, `TAG_communism`, `TAG_fascism`, `TAG_neutrality` plus `_DEF` and `_ADJ`), flags, decision/focus/idea icons, focus loading, AI strategy, docs, and manifests together. For existing-country variants, verify the event-created flag is set only on the release path and every `load_focus_tree` path is gated by that flag.

## Formable nations as event surfaces

When an event can create or empower countries, consider whether it should create formable nation routes. A formable can be a major event payoff, a late-game ambition, a hidden branch, a rare evolution reward, a country package route, or a post-crisis consolidation goal.

Event implementation must keep formables aligned across:

- event flags and route flags
- decision category visibility
- focus unlocks
- scripted triggers for state control
- scripted effects for formation
- cosmetic tags and country names
- flags and portraits
- AI strategy
- achievements
- super-events where the formation changes world order
- cleanup after tag switch, annexation, puppet transfer, civil war, or route failure

Use scripted helpers for formation effects. Do not duplicate formation logic in events, decisions, focuses, scripted GUI buttons, and achievements. The decision can pay the cost and validate requirements, while a shared helper performs the identity change and logs the result.

Hidden formables should still have implementation coverage. They need reveal events, hidden flags, visibility triggers, localisation, assets, AI rules, and cleanup.

## Scripted GUI and animated event presentation

Major event mechanics can use scripted GUI windows, decision-category interfaces, animated category art, animated leader portraits, or custom buttons when they make the system easier to play. Treat that UI as part of the event contract, not as decoration added later.

When an event uses a custom interface, align these surfaces:

- decision category or entry button
- scripted GUI definition
- scripted triggers and effects
- costs and tooltips
- animated and static sprites
- localisation and scripted localisation
- AI fallback behavior
- cleanup and invalidation rules
- documentation and asset manifest

Every player-clickable GUI button that changes gameplay must validate the same requirements as a normal decision. It must show costs and missing requirements clearly. It must call scripted effects that can also be used by AI, decisions, focuses, and cleanup systems.

Animated leader portraits, animated route emblems, glow effects, particles, and float effects should be used for major reveals, high-chaos escalation, hidden formables, supernatural leaders, or final transformations. Each animated asset needs a static fallback and manifest entry.

## Generated asset handling

Use the `chaos-redux-event-assets` skill whenever an event task requires generated or processed visual assets.

For every generated asset:

1. Create the base artwork by following the official `$imagegen` skill workflow through `chaos-redux-event-assets`.
2. Save the original generated image as a source PNG.
3. Create a processed PNG preview at the correct HOI4 target size.
4. Convert the processed PNG to DDS 32 bit unsigned BGRB 8.8.8.8.
5. Move the DDS into the correct mod asset folder.
6. Add or update the matching sprite definition in the correct `.gfx` file.
7. Update localisation, docs, and event spreadsheet entries that reference the asset.
8. Record the asset in a markdown manifest.

The asset manifest must include:

- asset name
- asset type
- source PNG path
- processed PNG path
- final DDS path
- target size
- sprite name
- intended in-game use
- related event id
- notes

Do not leave generated assets only in a temporary folder. If the event uses them, wire them into the mod.

## Final event checklist

Before closing an event task, verify:

1. Event script is updated.
2. Event classification/registration arrays are updated.
3. Auto-firing or runtime hooks are updated if needed.
4. Shared effects, triggers, and constants are updated if needed.
5. Event-name and debug-name mappings are updated.
6. Event log actor mapping is updated if needed.
7. Evolution logging and preview wiring are updated if relevant.
8. Triggerable scenario registry, launch gates, type controls, intensity controls, localisation, documentation, and bypass cleanup are updated if relevant.
9. If the event has a super-event, `chaos-redux-super-events` has been used for quote, remark, audio, and presentation planning.
10. Supporting decisions, ideas, AI, country setup, or exclusions are updated if relevant.
11. `docs/events/` is updated.
12. `docs/spreadsheets/chaos_redux_events_catalog.xlsx` is updated.
13. If assets are required, `chaos-redux-event-assets` has been used.
14. Generated assets are resized, converted to DDS 32 bit unsigned BGRB 8.8.8.8, moved into the correct folders, wired in `.gfx`, and recorded in an asset manifest.
15. Spec-mapped mechanics, routes, countries, decisions, achievements, assets, and super-events are implemented or clearly reported as blocked, merged, renamed, skipped, or simplified.
16. Dynamic values, concrete costs, mechanic visibility, decision category filtering, and effect strength are checked where the spec calls for them.
17. Focus trees preserve route structure, focus filters, varied rewards, idea lifecycles, route-specific AI, and visible branch payoffs where relevant.
18. New fighting countries have dynamic starting forces, template assumptions, equipment and manpower handling, and reinforcement pathways.
19. Achievement tracking, historical source mode, full asset coverage, animated fallbacks, and placeholder status are checked where relevant.
