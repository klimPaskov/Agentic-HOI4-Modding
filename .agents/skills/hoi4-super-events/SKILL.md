---
name: hoi4-super-events
description: Design, research, implement, audit, or document complete Hearts of Iron IV super-event presentation packages. Use for major reveal, escalation, world-order, victory, defeat, collapse, or campaign-ending moments that need aligned event wiring, scripted GUI or scripted localisation, title and body text, reaction text, sourced quote, image, audio, settings-aware playback, provenance, and validation.
---

# HOI4 Super Events

Treat a super-event as one cross-file presentation package. Keep its trigger,
slot or presentation ID, text, quote, art, audio, player settings, documentation,
and cleanup aligned.

Super-events are mod-owned presentation systems, not one universal vanilla
feature. Detect the current mod's architecture before editing. Never copy names,
prefixes, slots, paths, helper effects, spreadsheet rules, or audio formats from
another mod unless the current repository explicitly adopts them.

## Boundaries

- Use `hoi4-events` for the surrounding event or event-chain implementation.
- Use `hoi4-feature-assets` for image sourcing or generation, processing, DDS
  output, sprite handoff, and asset provenance.
- Use `hoi4-text-audio-research` for quote, cultural-reference, audio-source,
  attribution, license, and copyright research.
- Use `hoi4-subagents` when the repository exposes narrow quote, audio, source
  image, generated art, localisation, or completion-audit workers.
- Keep final gameplay, GUI, localisation, `.gfx`, sound, trigger, documentation,
  and validation ownership with the main agent.

Do not create a super-event for every dramatic popup. Reserve the workflow for a
campaign threshold that should feel larger than a normal country, news, or
report event.

## Discovery gate

Before writing:

1. Read `AGENTS.md` and use its declared game version, vanilla path, offline
   wiki path, and approved reference policy. If one is absent and the task
   needs it, ask for that exact value rather than choosing a path or version.
   Read the relevant offline wiki pages for events, scripted GUI, scripted
   localisation, graphical assets, sound, and localisation.
2. Search exact existing super-event identifiers and known presentation files.
3. Determine whether the mod already has:
   - a scripted GUI or event-window implementation
   - slots, cards, or presentation IDs
   - scripted localisation selectors
   - visibility flags and current-selection variables
   - sprite definitions and art dimensions
   - base sound definitions and volume-aware wrappers or helpers
   - player sound settings
   - documentation, catalogues, manifests, or tracking records
4. Record detected values with file evidence. Separate detected behavior from a
   proposed new convention.
5. If no architecture exists, inspect vanilla only for the underlying engine
   primitives and prepare a mod-owned design. Do not claim that vanilla
   provides a standard super-event system.

Do not use another mod as a reference unless the repository or user explicitly
approves it.

Bound the architecture search to the selected mod root. Inspect `AGENTS.md`,
`events/`, `common/scripted_guis/`, `common/scripted_localisation/`,
`common/scripted_effects/`, `common/scripted_triggers/`, `interface/`,
`localisation/`, `gfx/`, `sound/`, `music/`, and the repository's documented
docs or manifest roots when they exist. Search exact variants of `super_event`,
`super event`, known presentation IDs, sprite consumers, sound consumers, and
visibility state. Exclude `.git`, offline wiki copies, caches, backups, exports,
and generated build output. Conclude that no architecture exists only after
these relevant roots have no implementation or consumer evidence; report
unreadable or oversized roots as unresolved instead of treating them as absent.

When no architecture exists, record the proposal in the repository's existing
architecture-decision or plan format. If there is no established format, use
`docs/plans/super_event_architecture.md`. Include the mechanism, ID allocation,
naming, file placement, state and cleanup model, localisation fallback, image
contract, audio and player-volume contract, save/load, repeat, AI, multiplayer,
language, platform, documentation, and provenance decisions. Obtain explicit
user acceptance of that design before implementation.

## Package contract

A complete package accounts for every surface that the detected architecture
uses:

- presentation or slot ID
- firing event, decision, focus, on_action, or scripted effect
- visibility state and repeat/fire-once behavior
- title, description, reaction/button text, and quote
- scripted localisation selectors and safe fallbacks
- image source, processed preview, final texture, sprite, and dimensions
- audio source, license, final game-ready file, sound definition, playback route,
  and player-volume behavior
- cleanup of temporary flags, variables, event targets, and presentation state
- event or feature documentation
- permanent quote, image, and audio provenance
- repository-specific catalogue or tracking entry when one actually exists

Do not wire only the event, only the image, or only the localisation and call
the super-event complete.

## Design the moment

Classify the role before selecting text, art, or audio:

- first reveal or public disclosure
- escalation or failed containment
- faction or state formation
- irreversible political transformation
- ideological victory or collapse
- global threat
- defeat aftermath
- rare hidden branch
- world-order or campaign-ending state

Make the title, description, reaction, quote, image, and audio serve that exact
role. Avoid generic end-of-the-world wording and unrelated dramatic assets.

## Text and quote rules

Follow the detected localisation key pattern. If none exists, propose a pattern
derived from the confirmed project namespace and presentation ID.

Write:

- a short, specific title
- a concise description that explains visible consequences without leaking
  hidden mechanics
- reaction text that fits the tone and UI width
- one sourced quote that deepens the exact moment

Never invent or misattribute a quote. Verify wording, author, work or speech,
date when known, source URL, and attribution confidence. Prefer primary,
archival, public-domain, religious, literary, philosophical, legal, or
historical sources. Use modern copyrighted text only as a very short compliant
fragment or an allusion, and record the risk.

If the event is intentionally uncertain, preserve uncertainty in player-facing
text instead of revealing the hidden branch.

## Image rules

Define image direction before production:

- subject and campaign context
- tone and symbolism
- composition at the detected display dimensions
- generated, sourced, or user-provided mode
- what must be historically exact
- what to avoid

Use a sourced image for a real photographed person, event, place, document, or
artifact. Use generated art for fictional, alternate-history, symbolic,
supernatural, or composition-specific scenes. Follow `hoi4-feature-assets` for
source evidence, previews, DDS conversion, final placement, sprite handoff, and
validation. Never fabricate a real person's likeness.

## Audio rules

Check a repository-approved track catalogue or documented audio pool first when
one exists. Reuse audio only when its rights, source, format, duration, and
intended use are known and the reuse fits the moment.

For new audio:

1. Find multiple role-appropriate candidates.
2. Verify composition and recording rights separately.
3. Record title, creator or composer, performer or recording source, source URL,
   license, usage terms, duration, attribution, fit, and uncertainty.
4. Reject unclear licenses, unlicensed commercial recordings, vague
   "royalty-free" claims, generated test tones, beeps, oscillator layers, and
   placeholder ambience.
5. Preserve the source when permitted and create a game-ready derivative using
   the repository's verified format and conversion route.
6. Register a stable sound or music ID following the current mod's naming
   convention.
7. Use the detected player-volume or settings-aware playback route. If the mod
   has none, block final audio wiring until the user approves either a new
   settings-aware route or direct playback as a documented exception. Never
   silently omit audio or invent a helper name.

Do not hardcode `.wav`, `.ogg`, a duration range, wrapper count, or volume suffix
without repository or engine evidence.

## Wiring workflow

1. Reserve or confirm one presentation ID; reject accidental collisions.
2. Add the final localisation keys and scripted-localisation branches.
3. Add the final image and sprite wiring.
4. Add the final audio definition and settings-aware playback wiring.
5. Set the presentation state in the firing event or effect.
6. Clear or replace prior state safely when the architecture requires it.
7. Preserve fire-once, repeatable, hidden-branch, AI, and multiplayer behavior.
8. Update docs, manifests, and catalogues that the current repository uses.
9. Validate all consumers after the files are aligned.

For world-ending or terminal branches, also stop or gate incompatible future
systems and make the terminal state explicit. For defeat aftermath, communicate
cost, memory, and the changed post-crisis order rather than a cost-free victory.

## Research note

Store durable evidence in the repository's existing documentation structure. If
there is no established location, use:

```text
docs/super_events/<feature_slug>_super_event_research.md
```

Include:

- feature and presentation ID
- role, trigger, and visibility conditions
- final title, description, reaction, and quote
- quote source and confidence
- image direction, source mode, final path, sprite, and provenance path
- audio candidates and final selection
- audio rights, duration, source file, final file, sound ID, and playback route
- implementation paths
- cleanup behavior
- uncertainties and blocked items

Do not leave durable provenance only in a temporary asset workspace.

## Validation

Before completion, verify:

1. The trigger can reach the intended presentation exactly when designed.
2. Presentation IDs, flags, variables, and localisation selectors do not
   collide and have safe fallback behavior.
3. Title, description, reaction, and quote render in every supported language
   fallback.
4. The final sprite resolves to a real texture with the expected dimensions.
5. The final audio resolves to a real game-ready file with documented rights.
6. Playback respects the current mod's player sound settings when they exist.
7. No default, placeholder, mismatched, or wrong-format asset remains.
8. Repeat, cleanup, save/load, AI, hidden branch, and incompatible terminal
   states behave as intended.
9. Event docs, research notes, manifests, and catalogues match final IDs and
   paths.
10. The completion report lists evidence, validation, simplifications, and any
    remaining blocker.

Mark the workflow incomplete when a required final quote, image, audio license,
runtime file, trigger, or playback route is unresolved. Never report a
presentation package as finished from a mockup or isolated asset alone.
