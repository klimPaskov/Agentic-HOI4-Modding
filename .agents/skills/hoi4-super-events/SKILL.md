---
name: hoi4-super-events
description: Use when designing, researching, registering, wiring, testing, or documenting a Hearts of Iron IV Super Event with the optional reusable runtime.
---

# HOI4 Super Events

Use this skill only when the optional Super Events workflow is installed or the
repository already has an accepted Super Event architecture. A Super Event is a
large campaign presentation moment, not a substitute for an ordinary event
popup.

The HOI4 Mod Setup package provides a neutral runtime derived from a proven
mod architecture and adapted to the project’s confirmed namespace. It includes
GUI, GFX, scripted GUI, scripted localisation, one hidden smoke-test event,
default assets, editable Photoshop templates, and a registration guide.

## Boundaries

The main agent owns final registration, caller effects, GUI/GFX integration,
localisation, audio wiring, documentation, validation, and completion claims.

Route bounded work to:

- `hoi4_quote_remark_researcher` for exact quotations, attribution, cultural
  remarks, slogans, title references, and copyright risk
- `hoi4_audio_researcher` for licensed or public-domain audio research,
  downloads, editing, conversion, rights evidence, and handoff
- `hoi4_asset_source_researcher` for real or archival Super Event images
- `hoi4_generated_feature_art` for approved fictional, symbolic,
  supernatural, or alternate-history Super Event images
- `hoi4_localisation_auditor` for consistency and key coverage
- `hoi4_repo_explorer` only when the owning caller or an existing custom
  architecture is not already known

Use `hoi4-feature-assets` for image production and DDS handoff,
`hoi4-text-audio-research` for source-aware text and audio, `hoi4-events` for
event-chain ownership, and `hoi4-subagents` for bounded delegation.

Subagents do not edit the registry, scripted localisation, GUI, GFX, callers,
sound definitions, or gameplay unless the parent explicitly grants that narrow
scope.

## Installed package

The optional package installs these managed surfaces:

```text
interface/hoi4ms_super_events.gui
interface/hoi4ms_super_events.gfx
common/scripted_guis/hoi4ms_super_events.txt
common/scripted_effects/hoi4ms_super_events.txt
common/scripted_localisation/hoi4ms_super_events.txt
events/hoi4ms_super_event_examples.txt
localisation/english/hoi4ms_super_events_l_english.yml
gfx/interface/super_event_option.dds
gfx/super_events/super_event_bg.dds
gfx/super_events/super_event_default.dds
gfx/super_events/super_event_image_default.dds
gfx/super_events/super_event_template.psd
gfx/super_events/super_event_image_template_457x328.psd
docs/super_events/README.md
```

Filenames stay stable for managed update and repair. Scripted identifiers,
event namespace, sprite names, flags, localisation keys, and example text are
adapted from `[MOD_PREFIX]` and `[MOD_NAME]` during installation.

Never copy identifiers or event-specific content from another mod. Never
silently replace an existing custom Super Event architecture. Compare base,
local, and incoming files through the setup transaction and honor the user’s
conflict choices.

## Discovery gate

Before editing:

1. Read `AGENTS.md`.
2. Read this skill and `docs/super_events/README.md`.
3. Confirm the current mod prefix and installed package paths.
4. Search the requested event, effect, focus, decision, on_action, or other
   caller.
5. Inspect the current GUI, GFX, scripted GUI, scripted localisation,
   localisation, assets, audio definitions, and permanent Super Event docs.
6. Check whether an ID, sprite, localisation key, audio cue, or presentation
   moment already exists.
7. Identify every player-visible and AI path that can invoke the moment.

Use `hoi4.gui_inspect` before changing a scripted GUI you do not understand.
Use `hoi4.gui_render` after wiring when the available scenario can represent
the window. Keep tool output as evidence; it does not replace source review or
live in-game validation.

If the installed runtime is absent, do not fabricate its paths or claim it is
available. Either use the repository’s accepted custom architecture or ask the
user to add the optional workflow through HOI4 Mod Setup.

## Package contract

Every registered Super Event keeps these surfaces aligned:

- stable integer registration ID
- unique scripted trigger or caller
- project-scoped visibility flag
- image sprite and texture
- title
- description
- sourced quote or a deliberate no-quote decision
- short response remark
- optional audio ID, sound definition, final file, and rights record
- close behavior and cleanup
- owning event, focus, decision, effect, or on_action
- permanent documentation and source evidence
- smoke-test and live acceptance evidence

Do not wire only one part. A new image without registry text, a caller without
close cleanup, or audio without rights evidence is incomplete.

## Registration model

Reserve one integer ID per Super Event. Never recycle an established ID for a
different moment.

The installed runtime exposes:

```text
<mod_prefix>_show_super_event = {
    SUPER_EVENT_ID = <integer>
}
```

The helper stores the ID as the value of
`<mod_prefix>_super_event_visible`. The scripted GUI becomes visible while that
flag is present. Each `defined_text` block selects image, title, description,
quote, and remark from that same value. The close action clears the visibility
flag.

For every new ID:

1. Add one sprite in `interface/hoi4ms_super_events.gfx`.
2. Add one matching branch to each of the five `defined_text` blocks in
   `common/scripted_localisation/hoi4ms_super_events.txt`.
3. Add all player-facing keys to the project localisation file.
4. Call `<mod_prefix>_show_super_event` from the accepted gameplay moment.
5. Add optional audio only after its source and usage rights are verified.
6. Record the ID, caller, sprite, texture, text keys, quote source, optional
   audio, and validation state in permanent docs.

Keep every branch keyed to the same integer. Do not use one ID for text and a
different ID for image or audio.

## Smoke-test example

The package includes one hidden, trigger-only event:

```text
event <mod_prefix>_super_event.1
```

Run it from the debug console. It should open the default package, render the
project-adapted text and image, and close cleanly. The example is test
infrastructure, not a finished campaign moment. Do not repurpose ID `1` without
updating the package docs and test.

## Design the moment

Use a Super Event for campaign-scale reveals, irreversible escalation, a major
world-order change, rare ideological victory, catastrophic collapse, global
defeat, or a genuine campaign-ending moment. Do not create one merely because a
normal event is dramatic.

Before production, define:

- exact gameplay moment
- intended emotional role
- owning caller and scopes
- whether every player should see it
- title direction
- description direction
- quote role
- response tone
- image subject and source mode
- whether audio is required, optional, or deliberately omitted
- close cleanup
- test scenario

The title, image, quote, response, and audio should express the same moment.
Avoid a generic “dramatic” package with unrelated components.

## Title and description

Titles should be short, memorable, and specific. Prefer a person, state,
movement, place, institution, transformation, collapse, or irreversible
condition. Avoid generic labels such as `THE CRISIS` unless the project’s
accepted style requires them.

Descriptions should:

- state what changed
- establish campaign significance
- fit the available GUI space
- avoid repeating the title
- use the project’s established prose rules
- avoid invented factual claims

Keep text readable at the actual game resolution and UI scale. Long text that
overflows the window is a blocking presentation defect.

## Quote and response research

Do not invent a quotation and present it as real. Use
`hoi4_quote_remark_researcher` when wording, attribution, cultural origin, or
copyright risk needs research.

For every direct quote record:

- exact text
- author or speaker
- source work, speech, scripture, document, archive, or collection
- year or approximate period when known
- source URL or repository path
- attribution confidence
- public-domain or copyright note when known
- why it fits this exact moment

Prefer primary sources, official transcripts, libraries, archives, reputable
editions, and traceable historical collections. Unsourced quote sites are
search leads only.

The response remark is a short player reaction, not a second description. It
may be sober, ceremonial, bitter, fatalistic, defiant, or culturally grounded.
For modern copyrighted works, keep direct fragments very short and prefer a
title-like allusion or paraphrase. Record the source and risk.

## Image workflow

The visible image area is `457x328`. Use
`gfx/super_events/super_event_image_template_457x328.psd` for the image and
`gfx/super_events/super_event_template.psd` to review the complete composition.

Choose source mode deliberately:

- real historical material: attributed archival or user-provided source
- fictional, symbolic, supernatural, or alternate-history moment: generated
  art may be appropriate
- a user-provided final image: preserve its provenance and process it

Keep the full-resolution source, processed PNG, final DDS, hashes, dimensions,
crop/composition notes, source link, rights status, and sprite handoff. Use
`hoi4-feature-assets`; do not wire a contact sheet, PSD, or temporary evidence
path as runtime art.

The image must remain legible at `457x328`, match the described moment, and
avoid text baked into the image unless the accepted design explicitly needs
it.

## Audio workflow

Audio is optional for the reusable runtime. A missing or blocked track must not
break the visual Super Event.

When audio is requested:

1. Define its role: reveal, escalation, victory, defeat, aftermath, collapse,
   ritual, or campaign ending.
2. Check only approved existing audio catalogues or folders named by the
   parent.
3. Use `hoi4_audio_researcher` when no approved track fits.
4. Verify composition and recording rights separately.
5. Preserve the original download and source page.
6. Document title, creator/composer, performer or recording source, URL,
   license, attribution, duration, edits, and final path.
7. Convert through the repository’s verified audio workflow.
8. Give the cue a unique project-scoped sound ID.
9. Wire playback from the same accepted caller as the presentation.
10. Verify the cue plays once, honors the project’s audio settings if such a
    system exists, and does not survive close or retrigger unexpectedly.

Do not use commercial game, film, trailer, or album music without verified
permission. Do not treat a public-domain composition as proof that a modern
recording is public domain. Do not use test tones, beeps, oscillator output, or
noise beds as final music.

If the mod has no settings-aware playback helper, do not invent one silently.
Document the existing sound route or propose a bounded design before adding a
new settings surface.

## Caller and scope wiring

Show the Super Event from the gameplay effect that owns the completed moment,
after the state transition it announces is established. Avoid firing from
multiple routes unless duplicate suppression is explicit.

Verify:

- the caller has the correct country, state, character, or global scope
- every intended player path invokes the same registration
- AI-only effects do not attempt to interact with the GUI
- multiplayer visibility is intentional
- retriggers are prevented or deliberately supported
- close cleanup does not clear unrelated project state
- the visibility flag is not left set by an interrupted or bypassed path

Keep project-specific cleanup in the owning feature, not in the generic close
button.

## Documentation

Maintain one permanent registry or research note under `docs/super_events/`.
For each Super Event include:

- ID and stable slug
- role and owning feature
- caller path and effect
- sprite and texture
- title, description, quote, response keys
- quote/remark source and confidence
- audio ID, file, source, rights, duration, and edits, or `not used`
- acceptance scenario
- status and blockers

Temporary asset workspaces may hold downloads, processed previews, contact
sheets, and handoffs during active work. Before declaring the feature complete,
promote durable facts into permanent docs, verify runtime paths, and clean only
the task-owned temporary workspace.

## Validation

Before completion:

1. Run the installed example smoke test.
2. Trigger the real caller through its intended gameplay path.
3. Confirm the correct ID, title, description, quote, response, and image.
4. Confirm no missing localisation or sprite fallback appears.
5. Confirm the window fits at supported resolutions and UI scales.
6. Confirm keyboard/mouse close behavior and cleanup.
7. Confirm repeated or simultaneous triggers follow the documented policy.
8. Confirm AI and multiplayer behavior is intentional.
9. If audio is used, verify rights evidence, file format, one-time playback,
   volume behavior, and cleanup.
10. Search for duplicate IDs, duplicate sprite names, unresolved template
    tokens, missing textures, missing localisation keys, stale docs, and
    unreferenced final files.
11. Use GUI inspect/render evidence where available.
12. Check the game logs after the scenario and separate pre-existing messages
    from messages caused by this package.

A Super Event is incomplete while any caller, registry branch, localisation
key, image, required audio, close path, provenance record, or acceptance
scenario is missing or contradictory.
