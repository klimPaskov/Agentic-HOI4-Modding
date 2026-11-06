# HOI4 Events: Event anatomy and classification

Part of the [hoi4-events](../SKILL.md) skill. Read before editing an event chain, to classify each event block and keep ids, event types and stages consistent.

## Working model

A HOI4 event is not only one `country_event` or `news_event` block.

Treat every event as a contract across some or all of these surfaces:

- event namespace and event ids
- hidden bootstrap events and player-facing events
- country, state, and global scopes
- triggers, immediate blocks, options, after blocks, and hidden effects
- follow-up events, news events, and report events
- `on_actions`, decisions, focuses, ideas, scripted GUI, scripted effects, scripted triggers, and scripted localisation
- AI chance, AI-only follow-ups, AI strategies, and scripted behavior
- event pictures, report images, news images, custom audio, researched text, and icons
- localisation files, scripted localisation files, and custom trigger tooltips
- optional mod-specific event registries, debug tools, event documentation, and tracking records when the repository actually has them

If a task seems to need custom one-off plumbing, first check whether the behavior should become a reusable helper for future events. Repeated target selection, weighted random actor choice, cleanup, event target storage, scripted localisation selectors, variable formatting, dynamic costs, and common option effects usually belong in scripted helpers.


## Event anatomy

Use a clear anatomy before editing.

Common event pieces:

- **namespace**: a stable namespace in the event file, such as `namespace = my_mod_event`.
- **entry event**: the first event that starts the chain, usually hidden if the user should not see setup work.
- **player-facing popup event**: the visible country event the player reads and answers.
- **news event**: a broader announcement for large public events.
- **report event**: a documentary or report-style event using the mod's report-image presentation when the repository supports it.
- **hidden runtime event**: an internal helper event used for setup, target selection, delayed consequences, cleanup, or AI behavior.
- **follow-up event**: a later consequence, escalation, aftermath, foreign reaction, or branch result.
- **variant event**: a route-specific, ideology-specific, country-specific, or campaign-state-specific version of a normal step.
- **campaign-ending event**: a terminal or campaign-ending presentation only when the mod deliberately supports that kind of branch. Do not invent such a branch for ordinary events.

Keep ids stable when updating existing chains. If an event already exists in a namespace, do not renumber it for cosmetic tidiness.

- Leader events (`unit_leader_event`, `operative_leader_event`) must set `is_triggered_only = yes`, as the engine message and 40 of 40 vanilla leader events show. [vanilla-confirmed 1.19.4.1]
- A non-integer event id suffix is not dead in vanilla, since `common/decisions/ITA.txt` fires `BBA_italy_missiolinis.02_north` and 3 more. Prefer integer suffixes anyway. [vanilla-confirmed 1.19.4.1]
- Public news events normally set `major = yes`, as 596 of 677 vanilla news events do. [vanilla-confirmed 1.19.4.1]
- The delay arguments of `country_event` include `days`, `hours`, `months`, `random_days` and `random_hours`, and the upper bounds of the `random_*` ones are exclusive. [docs]
- No script effect disables or cancels an event. [docs]

### Baseline stages and escalation variants

Baseline stages are the ordinary flow of the event chain. They are not automatically special mod systems. They can be represented by flags, variables, follow-up events, timed missions, decisions, focus unlocks, or scripted GUI state.

Escalation variants are optional branches that change the shape of the event because the campaign state changed. They can add new actors, harsher mechanics, additional decisions, new focus paths, country transformations, stronger AI behavior, or source-researched text or audio eligibility.

Do not record ordinary stage progression as a special escalation record unless the repository has an explicit generic feature for that purpose and the current event is meant to use it.


## Event implementation workflow

### 1. Classify the event first

Before editing, decide what each event block does:

- hidden bootstrap or setup event
- visible country event
- news event
- report event
- AI-only event
- state-scoped event
- delayed follow-up
- cleanup event
- decision result
- focus result
- on_action result
- presentation trigger event
- aftermath event

Also decide whether the event is fire-once, repeatable, decision-triggered, focus-triggered, on_action-triggered, random, scripted-only, or a mod-specific registered event. Keep this classification aligned with the script.

