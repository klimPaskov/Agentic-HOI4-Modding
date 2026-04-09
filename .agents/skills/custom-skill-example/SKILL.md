---
name: chaos-redux-events
description: Use when implementing or updating Chaos Redux events.
---

# Chaos Redux Events

Use this skill for any Chaos Redux event work, including:

- adding or updating `chaosx.nr<ID>.*` event chains
- wiring event log, event details, evolutions, and world-end branches
- maintaining `docs/events/` event documentation
- updating the gameplay-facing event spreadsheet

Repository-wide reading, style, and validation rules live in `AGENTS.md`. This skill only adds the Chaos Redux event-specific implementation contract.

## Working model

In Chaos Redux, an event is not just an event block.

Treat every event as a contract across some or all of these surfaces:

- event definition and subevents
- random-event classification and registration
- auto-fire or runtime hooks
- shared scripted effects, scripted triggers, and script constants
- event-name and debug-name mappings
- event log names, actor mapping, event-details content, and evolution views
- super-event image, localisation, and audio wiring
- decisions, ideas, AI, characters, unit templates, or special-country handling
- `docs/events/` documentation and spreadsheet

If a task seems to need custom one-off plumbing, first check whether the same behavior should become generic for future events.

## Event anatomy

- entry event: the canonical `chaosx.nr<ID>.1` start
- player-facing popup events: the things the player actually reads and clicks
- follow-up/news events: broadcast or consequence popups
- evolutions: milestone states inside the same event identity
- world-end scenarios and super-events
- connection with other events (meaning that events are not standalone and actually interact with each other)

## What evolutions are

In Chaos Redux, an evolution is a meaningful milestone inside one event's lifecycle that the player should be able to understand as part of the same story/mechanic.

Typical examples of evolutions:

- a threat reaching a stronger stage
- a system mutating into a new gameplay phase
- a branch changing severity, scale, or behavior

### Evolution implementation

The usual pattern is:

1. the evolution MTTH event becomes available
2. set the shared evolution context variables
3. record the evolution log entry through the shared pipeline

The shared context is:

- `events_log_evolution_event_id`
- `events_log_evolution_type`
- `events_log_evolution_stage`
- `events_log_evolution_tier`
- `events_log_evolution_actor` when the stage belongs to a country

Then:

- gate the stage with `is_current_evolution_enabled = yes` only if the stage should be disableable from the UI
- call `record_events_log_evolution_entry = yes`

Design rules:

- `event_id` ties the evolution to the parent event
- `type` separates parallel tracks inside the same event if needed
- `stage` should increase cleanly inside one type
- `tier` is display-oriented; do not use it as a substitute for real logic state

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
  - evolution/escalation events
  - world-end or super-event branches

Keep IDs stable when updating existing chains.

### 2. Map touched systems before editing

Always start from the event and walk outward through the systems it touches.

Core files to check:

- `events/XXX_my_event.txt`
- `common/on_actions/chaosx_on_actions_system.txt`
- `common/scripted_effects/chaosx_logic_effects.txt`
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
- and possibly more. Some events truly can touch all systems.

If the event creates or manages non-standard countries, then account for that as well. Events interact with each other, so events that usually affect normal countries (like black plague or mass panic), shouldn't for example affect zombie or alien countries.

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
- and much more

If you add a new reusable dynamic scripted effect, document it in `common/scripted_effects/chaosx_dynamic_effects.md` in the same change.

### 5. Event log integration

Events must appear in Chaos Redux’s event log, wire the full log contract in the same change.

Required name plumbing:

- add or update visible event-name loc in `localisation/english/chaosx_event_names_l_english.yml`
- update event-name selectors in `common/scripted_localisation/chaosx_scripted_localisation_events_log.txt`
- update debug-name selectors in `common/scripted_localisation/chaosx_scripted_localisation_debug.txt`

Required actor plumbing when a flag should appear:

- update `events_log_set_default_actor_for_current_event` in `common/scripted_effects/chaosx_logic_effects.txt`
- use a default actor only when the event should show a meaningful actor before or without a fired history row
- if fired history should override the default actor, keep the history-context flow intact

Required detail-view plumbing:

- update the event-details text selectors in `common/scripted_localisation/chaosx_scripted_localisation_events_log.txt`
- update the actual user-facing text in `localisation/english/chaosx_gui_l_english.yml`
- if new generic event-log behavior is needed, wire it through:
  - `common/scripted_effects/chaosx_settings_effects.txt`
  - `common/scripted_guis/chaosx_scripted_gui_events_log.txt`
  - `interface/chaosx_events_log_popup.gui`

Do not hardcode one-off GUI behavior if it should be reusable by later events.

### 6. Super-event integration

If the event shows or drives a super event, wire the whole package:

- choose the slot intentionally
- set `super_event_visible`
- set `global.current_super_event_audio_id`
- use the settings-aware playback helper rather than bypassing it
- update scripted localisation in `common/scripted_localisation/chaosx_scripted_localisation_super_events.txt`
- update image wiring in `interface/chaosx_super_events.gfx`
- update player-facing localisation in the correct `.yml` files

Do not wire only the image or only the audio; keep the slot, loc, image, and audio ID aligned.

### 7. World-end integration

If the event can produce a terminal scenario:

- keep the world-end flagging explicit and centralized
- make sure the terminal branch is distinguishable from ordinary major-event escalation
- gate later random events, branches, or systems that should no longer operate after the terminal state
- make the event log, docs, and spreadsheet, all agree on what the terminal branch actually is

If the branch is dramatic but not actually terminal, treat it as a major escalation evolution or super-event branch instead of world-end.

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
7. Evolutions and escalation flow if relevant.
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

- write for players, not script readers
- focus on what happens in play
- keep the `Details` field aligned with the event-details window description
- keep evolution/world-end columns aligned with the real chain structure

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
- evolutions should visibly evolve
- terminal branches should get heavier final-slide treatment
- keep deck path and asset folder stable unless the user asks otherwise

Preferred deck path:

- `docs/presentations/chaos_redux_events.pptx`

## Final event checklist

Before closing an event task, verify:

1. Event script is updated.
2. Event classification/registration arrays are updated.
3. Auto-firing or runtime hooks are updated if needed.
4. Shared effects, triggers, and constants are updated if needed.
5. Event-name and debug-name mappings are updated.
6. Event log actor mapping is updated if needed.
7. Event details window content is updated if the event appears there.
8. Evolution logging and preview wiring are updated if relevant.
9. Super-event slot, loc, image, and audio wiring are updated if relevant.
10. Supporting decisions, ideas, AI, country setup, or exclusions are updated if relevant.
11. `docs/events/` is updated.
12. `docs/spreadsheets/chaos_redux_events_catalog.xlsx` is updated.
