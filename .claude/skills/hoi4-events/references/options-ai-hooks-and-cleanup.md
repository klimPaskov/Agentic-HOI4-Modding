# HOI4 Events: Options, AI, hooks and cleanup

Part of the [hoi4-events](../SKILL.md) skill. Read before writing immediate and option effects, AI chance, news or report events, on_action hooks, the text and audio handoff, or chain cleanup.

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

For deterministic max-score selectors, track explicit first-valid-candidate presence and accept that first candidate regardless of its score.
A numeric best-score sentinel must not reject an otherwise valid negative score.
After the first candidate, retain the exact score comparison and existing ID tie-break without changing weights or eligibility.

### 9. News and report events

Use news or report presentation when the event is public enough or visually specific enough to need it.

News events should have a broad public framing and use appropriate news images. Report events should feel like documentary or field-report material when the repository supports that style.

Do not use a news event for every ordinary result. Use it for public shifts, wars, country formations, leadership changes, disasters, major discoveries, or events that many countries would plausibly hear about.

### 10. on_action integration

Use `on_actions` when an event should react to engine events such as war, capitulation, annexation, peace, state control changes, focus completion, monthly pulses, or other supported hooks.

An `on_actions` block holds only `effect` and `random_events`. [vanilla-confirmed 1.19.4.1]

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

During active asset work, retain sources, processed previews, manifests, crosswalks, and handoffs under the temporary `docs/assets/<feature_slug>/` workspace. Before declaring the event fully complete, promote durable provenance, licensing, attribution, coverage, review, and wiring facts into permanent event, plan, spec, super-event, or system documentation; verify that no runtime reference points into `docs/assets/`; and delete the complete feature-scoped workspace. Keep it when work is blocked or incomplete. Its absence is expected after full completion.

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


