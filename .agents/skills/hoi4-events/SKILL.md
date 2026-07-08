---
name: hoi4-events
description: Use when implementing, updating, auditing, or documenting ordinary Hearts of Iron IV events, event chains, news events, report events, on_action hooks, localisation, event pictures, optional mod registration hooks, and event validation.
---

# HOI4 Events

Use this skill for ordinary HOI4 event work in a mod repository.

This includes:

- adding or updating country events, hidden events, news events, report-style events, and narrative event chains
- wiring events through `on_actions`, decisions, focuses, scripted effects, scripted triggers, scripted localisation, and optional mod-specific registration hooks
- keeping localisation, event pictures, report pictures, news pictures, text and audio packages, docs, and any parent-provided tracking records aligned
- validating event ids, namespaces, scopes, triggers, effects, options, localisation keys, pictures, and follow-up hooks

Repository-wide reading and style rules live in `AGENTS.md`. This skill adds the event-specific implementation contract. It does not replace focus-tree, decision, asset, animation, text and audio research, or subagent skills.

When event work creates broad visible text, use `hoi4_localisation_auditor` before completion when that subagent is available. When repeated dynamic logic appears across events, decisions, focuses, GUI, or country setup, use `hoi4_scripted_system_architect` before duplicating logic.


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


## Relationship with other skills

Use this skill with:

- `hoi4-feature-planning` when the user asks for event design or a deeper event specification before implementation
- `hoi4-feature-assets` when the event needs event pictures, report images, news images, icons, flags, portraits, or final DDS assets
- `hoi4-frame-animation` when event presentation needs animated sprites, animated portraits, animated UI pieces, frame sheets, or GIF previews for review
- `hoi4-text-audio-research` when an event needs sourced quotes, cultural references, title-like references, slogans, or music and audio research
- `hoi4-focus-trees` when the event creates, unlocks, modifies, or depends on focus trees
- `hoi4-decisions-missions` when the event creates or depends on decisions, missions, timed objectives, formables, or decision-driven mechanics
- `hoi4-subagents` when bounded research, asset production, small patches, or completion audits should be delegated
- `hoi4-improvement-loop` when an implemented event works but is still shallow, generic, disconnected, or underdeveloped

The parent agent remains responsible for final integration, final validation, and completion claims. Subagents and helper skills provide evidence, patches, assets, or plans. They do not replace parent review.


## Spec and plan locations

Feature specs for event-related work live under `docs/specs/<feature_slug>/`. Implementation should read those files as the main design source when they exist.

Subagent plans, expansion addenda, audit follow-up notes, and implementation handoffs live under `docs/plans/<feature_slug>/`. Plans are working documents. If a plan becomes accepted source design, merge it into the relevant spec.


## Spec fidelity and implementation quality

When implementing from `docs/specs/`, treat mapped content as acceptance criteria. Do not silently replace mapped mechanics, routes, countries, decisions, achievements, assets, or text and audio packages with smaller fallback versions. If something must be merged, skipped, or simplified, report it in the completion notes with the reason and affected files.

Use dynamic factors for pressure, cooldowns, progress, chance, support, duration, costs, AI willingness, spawn strength, aid amounts, stage movement, recognition, etc when the spec calls for a living system. Flat values are allowed only as constants, caps, floors, or deliberate tuning anchors. Centralize shared values in script constants or documented tuning.

Do not implement major decisions, missions, focus rewards, GUI buttons, or event responses as political power or command power purchases by default. Use concrete costs and requirements from the spec when relevant: XP, equipment, manpower, fuel, trains, convoys, supply, stability, war support, local support, held states, unit presence, foreign access, intelligence exposure, or time pressure. Tooltips must explain blocked nonstandard requirements.

When the spec maps focus paths, implement a real tree, not a thin vertical chain. Preserve route locks, side branches, convergence points, hidden branches, crisis branches, AI weights, focus filters, varied icons, and branch payoffs. Rewards should vary across buildings, units, decisions, missions, advisors, identities, claims, cores, diplomacy, technologies, and mechanic changes. Do not fill trees with repeated new ideas, tiny modifiers, political power, stability, or war support.

When implementing starting or route ideas, wire their lifecycle. Negative, mixed, staged, or route-specific ideas should be removed, upgraded, replaced, worsened, or consumed by the mapped decisions, focuses, missions, wars, failures, or reforms. Avoid dead idea stacks that never change.

Mechanic variables must be visible somewhere meaningful, such as decision category text, scripted localisation, national spirit tooltip, scripted GUI, progress meter, or focus tooltip. Keep cause and effect readable. Values should be changed by the mapped decisions, focuses, missions, events, wars, state control, AI actions, and foreign influence. Use consistent localisation colours for important mechanic values and breakdowns.

Large decision systems must hide obsolete or irrelevant actions. Use phases, active caps, target pools, route locks, thresholds, emergency visibility, regional grouping, cooldowns, or cleanup flags. The category should show current playable actions, not every possible debug action.

If the spec defines achievements, implement the full achievement surface: tracking flags or variables, unlock triggers, disqualifiers, localisation, icons, docs, and any route or formable hooks. Do not convert hard achievements into automatic unlocks.

Before completion, check every visible asset named or implied by the spec: flags, ideology flags, cosmetic flags, leaders, portraits, focus icons, decision icons, ideas, achievements, faction emblems, report or news images, UI sprites, animated sprites, and static fallbacks. Do not claim completion while required visible assets are placeholders unless the completion report says so clearly.

Do not generate real historical leaders, historical flags, or well-attested real symbols as fictional art. Source them, document source and license status when possible, and convert them to the required HOI4 format. Generated art is for fictional, symbolic, alternate, supernatural, or invented identities unless the user says otherwise.

Any new, released, restored, transformed, or event-managed country that is expected to fight needs starting forces and a reinforcement pathway. Implement dynamic starting units, templates, equipment and manpower assumptions, commander or officer handling when relevant, and later unit growth through decisions, focuses, depots, objectives, volunteers, foreign support, mobilisation, or special mechanics. Do not leave a serious fighting country as an empty tag unless the spec says so and explains why.

Major events and country-creation events need route-specific AI. Implement focus choices, decision choices, unit-raising choices, faction behavior, foreign influence behavior, rare variant handling, extreme-route exceptions, invalid-route blocking, etc.

Do not reduce major spec effects to tiny decorative modifiers. Important effects must change incentives, unlock content, move visible mechanic values, alter army or economy behavior, create a real tradeoff, or connect to later outcomes.


## Event writing and player-facing text

Event implementation owns final player-facing wording for event popups, news events, report events, event details, decision text, focus text, tooltips, GUI labels, scripted localisation, documentation summaries, and any parent-provided external records that mirror in-game text. Convert direction into finished wording, but do not paste working labels, prompt fragments, route notes, placeholder text, or process notes into localisation.

These writing style rules apply to every mod prose surface, including event text, news text, researched text, decision text, focus descriptions, tooltips, docs, specs, plans, prompts, and all player-facing text.

1. Never use the em dash or semicolons in sentences.
2. Absolutely avoid dialectical hedging. Do not frame sentences as thesis, antithesis, synthesis.
  - Dialectical hedging examples:
   - `This is not just a strike. This is a warning.`
   - `The cult is not fighting for land, but for meaning.`
   - `The disaster is both a local tragedy and a global sign.`
   - `The army did not collapse. It transformed.`
   - `This is less a rebellion than a confession.`
   - `The question is not whether order can return, but what kind of order will survive.`
  - Thesis, antithesis, synthesis examples:
   - `The army claims the province is secure. Refugees say it is already lost. The truth lies between them.`
   - `Some call the new state liberation. Others call it occupation. In reality, it is both.`
   - `The priests call it a miracle. The generals call it a weapon. History will call it both.`
3. Avoid AI-style explanatory templates. Do not write lines that sound prebuilt or reusable across any event.
4. Absolutely avoid staccato sentences. Do not split one simple thought into a chain of tiny lines for artificial weight or dramatic effect. Use complete, readable sentences with enough context to be clear.
  - Staccato examples:
   - `No orders. No mercy. No dawn.`
   - `The guns stopped. The screaming did not.`
   - `First hunger. Then anger. Then flags.`
   - `The gate opened. The crowd moved. The guards ran.`
5. Absolutely avoid empty dramatic filler. Do not lean on vague intensity words when concrete detail would do the work.
6. Do not paste instruction text, task labels, prompt fragments, or process notes into in-game text, specs, docs, localisation, external documentation fields, or reports.
  - For example, when the user says `Do not reveal the hidden mechanics here.`, do not write `This path purposely doesn't reveal the hidden mechanics`.

Write in-world text. Describe what the country, army, population, strange force, disaster, cult, machine, disease, movement, or leader is doing. Do not make the emotional center a changed map, a staff-table scene, administrative paperwork, formal diplomatic phrasing, sealed reports or generic crisis communications. They should not become the default way to create mystery.

Player-facing escalation text must not label itself as a warning, a non-warning, a threat, a danger signal, or a campaign-endinging risk. Let the player infer trouble through fear, missing people, strange behaviour, rumours, unexplained anomalies, local panic, and consequences that repeat over time. Do not build tension with staged contrast formulas. Forbid patterns such as `claim X while officials Y`, `reports say X while authorities Y`, `X before Y`, `people do X before governments Y`, and any similar construction that pairs one observation against a denial, admission, delay, or official reaction. Write the observed fear and uncertainty directly instead of using those contrast frames.

Only write sections for event surfaces that actually exist. Omit absent systems entirely. This applies to campaign-ending branches, manual scenarios, text or audio research packages, achievement sets, focus trees, country packages, and custom UI.

Do not expose hidden routes, secret variables, future surprises, achievement paths, implementation history, tuning history, or rework history in player-facing text. event details and any explicitly scoped external records describe the situation and premise, not the mechanical effects. Options, decisions, focuses, and tooltips must still clearly describe visible consequences and requirements, but they should not read like reward lists or spoil content.

For sourced text or audio packages, do not invent quotes, cultural remarks, song fragments, title references, or final audio choices. Use `hoi4-text-audio-research` and the relevant research subagents when the event needs sourced wording or music.


## Parent and subagent implementation ownership

Patch-capable subagents are active by default inside the current task scope. Use them when a large event touches focus trees, decisions, country packages, localisation, GUI, scripted helpers, or assets at the same time.

Small subagent patches are allowed when they improve a specific surface without changing the event design. A decision subagent can vary costs, clarify tooltips, add cleanup, improve AI weights, and patch related localisation. A focus subagent can fix a route lock, prerequisite, bypass, focus AI, icon reference, small reward, or formable unlock hook. A country package subagent can patch tag setup, party names, focus loading, leader references, country localisation, simple starting setup, or existing formable requirements. A localisation subagent can patch dynamic text directly. A scripted-system architect can add narrow helpers and direct call sites when the repeated logic is already present.

The parent still owns final integration, docs, explicitly scoped external records, event chain direction, completion claims, and any broad mechanic expansion. If a subagent sees a needed route family, new country package, new formable suite, new scripted GUI system, new event chain, or major balance redesign, it writes a plan under `docs/plans/<feature_slug>/` and stops.

Every subagent edit must produce a handoff under `docs/plans/<feature_slug>/subagent_handoffs/` when the feature slug is known. The handoff lists changed files, identifiers, behavior before and after, meaningful validation, remaining gaps, and follow-up work for the parent.


## Major-event defeat aftermath

Some major events should also have a structured aftermath when the threat is beaten.

Use a defeat aftermath package when all of these are true:

- the defeated threat was global or near-global in reach
- the campaign lasted long enough to feel like a world crisis
- the cost in casualties, destruction, or political disruption was high enough that the world should not simply snap back to normal

Typical aftermath content:

- a sourced defeat quote, cultural remark, or audio cue when the feature needs one
- postwar treaties, compacts, or new world orders
- recurring remembrance, reconstruction, or vigilance events
- lasting ideas, tech-sharing groups, or diplomatic rules that exist because the world learned from the crisis

Do not add a treaty/new world order after every contained or short-lived disaster. Those only make sense when the event genuinely reshaped the campaign.


### 7. Duration fields and constants

Use `script_constants` for shared tuning, but remember that some duration fields reject both `constant:` and variable tokens.

Known sensitive fields:

- `set_country_flag = { days = ... }`
- `set_global_flag = { days = ... }`
- any other timed field that throws `Malformed token` for either `constant:category.key` or a variable token

For those fields, use a file-scoped `@NAME = literal` constant in the same script file and pass `days = @NAME`. Keep the value mirrored with the matching `common/script_constants/` tuning entry, and update both in the same change.

Do not work around this by setting a temp variable and passing `days = temp_name`. those fields can reject variable tokens too. In which case, a `meta_effect` must be used if possible.


## Documentation rules

Event-specific documentation belongs in `docs/events/`.

Preferred naming pattern:

- `docs/events/<feature_slug>.md`, using the same feature slug as the related spec, plan, and asset folders.

Keep one canonical doc per event chain instead of splitting mechanics across multiple top-level docs unless the user explicitly asks for that.

Event doc structure:

1. What the event is.
2. Event map and subevents.
3. Trigger and runtime flow.
4. Main gameplay effects.
5. Supporting systems touched.
6. AI behavior if relevant.
7. Baseline progression, escalation variant tracks, and escalation flow if relevant.
8. Campaign-ending and source-researched text or audio integration if relevant.
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
- outdated external record or deck expectations


### Docs and gameplay must stay aligned

When mechanics change, update the matching event doc in the same change.

Do not leave the doc describing:

- old triggers
- old cooldowns
- old stage counts
- removed branches
- removed assets
- outdated external record or deck expectations


## Formable nations as event surfaces

When an event can create or empower countries, consider whether it should create formable nation routes. A formable can be a major event payoff, a late-game ambition, a hidden branch, a rare escalation variant reward, a country package route, or a post-crisis consolidation goal.

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
- researched text or audio packages where the formation changes world order
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

Animated leader portraits, animated route emblems, glow effects, particles, and float effects should be used for major reveals, extreme-route escalation, hidden formables, supernatural leaders, or final transformations. Each animated asset needs a static fallback and manifest entry.


## Generated asset handling

Use the `hoi4-feature-assets` skill whenever an event task requires generated or processed visual assets.

For every generated asset:

1. Create the base artwork by following the official `$imagegen` skill workflow through `hoi4-feature-assets`.
2. Save the original generated image as a source PNG.
3. Create a processed PNG preview at the correct HOI4 target size.
4. Convert the processed PNG to DDS 32 bit unsigned BGRB 8.8.8.8.
5. Move the DDS into the correct mod asset folder.
6. Add or update the matching sprite definition in the correct `.gfx` file.
7. Update localisation, docs, and any explicitly scoped external records that reference the asset.
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
- related event id when the asset is tied to a real HOI4 event
- related feature slug
- notes

Do not leave generated assets only in a temporary folder. If the event uses them, wire them into the mod.


## Final event checklist

Before closing an event task, verify the surfaces that actually exist for the feature:

1. Event script files are updated, ids are stable, and namespaces are unique.
2. Firing path is correct: decision, focus, on_action, hidden event, scripted effect, or optional mod registry.
3. Triggers, scopes, immediate effects, option effects, and cleanup effects match the design.
4. Shared effects, triggers, script constants, and event targets are updated when needed.
5. Localisation exists for titles, descriptions, options, tooltips, news/report text, and dynamic values.
6. News events, report events, and researched text or audio packages are wired only when they are real surfaces in the design.
7. Supporting decisions, missions, ideas, focuses, AI, country setup, or scripted GUI surfaces are aligned when relevant.
8. Event pictures, report images, news images, icons, flags, portraits, animated sprites, and fallbacks exist when required.
9. Generated or sourced assets are resized, converted, moved into correct folders, wired in `.gfx`, and recorded in manifests when they are part of the task.
10. Documentation, specs, plans, manifests, and any explicitly scoped external records are updated only when the repository actually uses those surfaces.
11. Spec-mapped mechanics, routes, countries, decisions, achievements, assets, and researched text or audio packages are implemented or clearly reported as blocked, merged, renamed, skipped, or simplified.
12. Dynamic values, concrete costs, mechanic visibility, decision filtering, cleanup, AI behavior, and effect strength are checked where the spec calls for them.
13. Focus trees preserve route structure, focus filters, varied rewards, idea lifecycles, route-specific AI, and visible branch payoffs where relevant.
14. New fighting countries have dynamic starting forces, template assumptions, equipment and manpower handling, and reinforcement pathways.
15. No fallback, placeholder, missing localisation, missing asset, missing AI behavior, or shallow substitute is hidden in the completion report.


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

### 2. Map touched systems before editing

Start from the event file and walk outward.

Common files to inspect or update:

- `events/<event_file>.txt`
- `common/on_actions/*.txt`
- `common/scripted_effects/*.txt`
- `common/scripted_triggers/*.txt`
- `common/script_constants/*.txt`
- `common/scripted_localisation/*.txt`
- `common/decisions/*.txt` and `common/decisions/categories/*.txt`
- `common/national_focus/*.txt`
- `common/ideas/*.txt`
- `common/country_tags/*.txt`, `common/countries/*.txt`, `history/countries/*.txt`, and `history/states/*.txt` when countries are created or transformed
- `common/ai_strategy/*.txt` and other AI files when behavior changes
- `interface/*.gfx` when event pictures or sprites are referenced
- `localisation/<language>/*.yml`
- `gfx/event_pictures/`, `gfx/interface/`, `gfx/leaders/`, `gfx/flags/`, and other asset folders
- `docs/`, specs, plans, manifests, and any explicitly scoped external records when the repository uses them

Use exact ids, namespaces, flags, variables, localisation keys, sprite names, tags, and file stems to search. Avoid broad repo exploration when the files are already known.

### 3. Register optional mod hooks only when they exist

Many mods have their own event registries, debug menus, scenario tools, event lists, or documentation tables. Use those hooks only when the repository actually has them.

Generic rule:

1. Find the existing registration pattern.
2. Add the event id, display name, category, enabled state, or weight in the same shape as existing events.
3. Keep any scripted-localisation selectors aligned with the registration.
4. Keep optional docs or parent-provided tracking records aligned with the in-game text.
5. If the repository has no such system, do not invent one for a normal event.

### 4. Handle supporting gameplay systems

An event often needs more than its own event file.

Touch the relevant systems in the same implementation pass:

- decisions and categories if the event creates player tools or responses
- missions if the player must meet a deadline or map objective
- ideas or dynamic modifiers if the event creates persistent gameplay state
- focus trees if the event creates a route, unlock, or country tree
- country files and history files if the event creates or transforms a country
- AI strategies if the event changes how AI should react
- assets and `.gfx` if visible pictures, icons, flags, portraits, or sprites are used
- documentation when mechanics change

If new reusable dynamic scripted effects or triggers are added, document them in the matching markdown file or repository helper documentation in the same change.

### 5. Use scopes deliberately

Event bugs often come from scope drift.

Before writing an effect, identify the expected scope:

- `ROOT` for the event owner
- `FROM` for the caller or target from the firing context
- `FROM.FROM` only when the chain is clear and documented
- `THIS` for the current iterator scope
- state scopes when selecting states or using state modifiers
- country scopes when saving targets or applying country effects
- global scope only for intentionally shared values

If an effect chain needs a scope later, save it as an event target. Use regular event targets for short chains and global event targets only when persistence is required. Clean global event targets when the system ends.

### 6. Put real effects in the right place

Use `immediate` for setup and effects that happen regardless of player choice. Hide mechanical setup with `hidden_effect` when it should not clutter the event option.

Use option effects for consequences tied to that option. Do not apply the same effect in both `immediate` and an option unless the design really needs both.

Use `after` or delayed hidden events for cleanup, follow-up scheduling, or consequences that must happen after the popup resolves.

### 7. Keep event options meaningful

Options should represent choices when choices exist. If the player has no real choice, a single acknowledgement option is acceptable, but do not fake choice with two buttons that do the same thing.

For meaningful options, make differences clear through:

- resource cost
- risk
- target
- ideology or route commitment
- timing
- AI chance
- follow-up event
- decision unlock
- focus unlock
- idea stage
- relations, war support, stability, legitimacy, or other visible value

Do not make all event options small political power, stability, or war support adjustments unless the event is genuinely small.

### 8. Write AI chance deliberately

Do not leave important options with default or flat AI behavior.

AI chance should consider:

- ideology
- war state
- stability and war support
- manpower and equipment
- strength of nearby enemies
- faction membership
- route flags
- prior choices
- target validity
- hidden or dangerous branch restrictions
- player-adjacent risk

When AI behavior is complex, centralize it in scripted triggers, scripted values, or helper effects rather than scattering repeated conditions across many options.

### 9. News and report events

Use news or report presentation when the event is public enough or visually specific enough to need it.

News events should have a broad public framing and use appropriate news images. Report events should feel like documentary or field-report material when the repository supports that style.

Do not use a news event for every ordinary result. Use it for public shifts, wars, country formations, leadership changes, disasters, major discoveries, or events that many countries would plausibly hear about.

### 10. on_action integration

Use `on_actions` when an event should react to engine events such as war, capitulation, annexation, peace, state control changes, focus completion, monthly pulses, or other supported hooks.

Do not use whole-world daily or weekly scans unless the repository rules allow that and the feature truly needs it. Prefer narrower hooks, targeted pulses, country flags, scripted triggers, and cleanup events.

When using `on_actions`, document:

- hook name
- scope received by the hook
- event or effect called
- gating conditions
- cleanup conditions
- performance risk
- validation check

### 11. Text, audio, and custom presentation handoff

If the event uses sourced quotes, cultural remarks, slogans, allusions, custom audio, or a custom presentation surface, keep the package aligned:

- localisation keys and scripted localisation that show the final text
- source notes for quotes, remarks, slogans, allusions, and audio
- final audio file and audio id when custom audio is used
- playback helper or sound definition when the repository has one
- image or sprite references only when a real custom visual surface exists
- triggering event or effect
- docs and asset manifest when the repository uses them

Use `hoi4-text-audio-research` for quote, cultural remark, slogan, allusion, audio source documentation, attribution checks, and license checks. Use the owning implementation skill for event-side wiring.

Do not leave default, placeholder, mismatched, undocumented, or wrong-format audio in a completed package.

### 12. Completion cleanup

Every event chain needs cleanup for flags, variables, event targets, missions, decisions, temporary ideas, temporary modifiers, and invalid targets.

Cleanup should handle:

- owner annexed or tag switched
- target country no longer exists
- state owner changed
- war ended
- route closed
- focus branch bypassed
- mission expired
- decision category no longer relevant
- hidden branch disqualified
- presentation cue already used
- repeated event should not duplicate a state

Do not leave stale flags or missions that make a later branch believe the old target is still valid.


## Localisation and scripted localisation

Every player-facing event needs complete localisation:

- event title
- event description
- every option
- option tooltips when effects are not self-evident
- custom trigger tooltips for complex requirements
- news or report title and body
- scripted localisation selectors when dynamic names, states, countries, values, or routes appear
- event picture or sprite localisation only when the UI needs it

Localisation must describe the in-world situation and visible consequences. It must not expose implementation history, prompt fragments, hidden variables, secret route names, future surprises, or achievement spoilers.

Dynamic values often display decimal places unless formatted. If a value is conceptually an integer, use an integer formatter such as `|0` or an equivalent scripted-localisation helper. Use fractional precision only when the fraction changes player decisions.

When text mirrors a docs field or a parent-provided external record, the in-game localisation is the source of truth. Do not paraphrase mirror fields unless the field is explicitly a summary field.


## Validation checks

Use task-specific validation that can realistically catch mistakes.

Common useful checks:

- duplicate event ids inside a namespace
- duplicate namespaces
- event file contains `namespace = ...`
- referenced events exist
- `country_event`, `news_event`, or `state_event` type matches the intended use
- option names and localisation keys exist
- event picture sprites exist and point to real files
- `fire_only_once`, `is_triggered_only`, and `hidden = yes` match the trigger path
- on_action hook calls the expected event or effect
- scripted effects and triggers referenced by the event exist
- global event targets created by the event are cleaned up
- decision or focus unlocks referenced by the event exist
- news/report images have final DDS files and `.gfx` definitions
- dynamic localisation selectors return fallback-safe text for every visible route
- AI chance exists for meaningful choices
- docs and manifests match final ids and assets

Do not fill the final report with boilerplate checks that only restate repo-wide rules. Report validation when it affected confidence, found a problem, or directly proves a task-specific surface is wired.
