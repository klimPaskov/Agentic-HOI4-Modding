---
name: hoi4-super-events
description: Use when designing, researching, wiring or documenting Hearts of Iron IV super-events and their localisation, sourced quote, audio and image handoffs, slots and registration.
---

# HOI4 Super-Events

Use this skill when a mod task creates, updates, researches, or wires a super-event.

This skill covers super-event presentation, localisation, quote selection, audio research, image handoff, implementation wiring, and documentation.

General event implementation belongs to `hoi4-events`.

Visual asset sourcing and processing belongs to `hoi4-feature-assets`.

This file is a router. It keeps what a super-event package is, when to use the skill, how it relates to other skills, who owns what, the runtime and registration contract, and the role decision. The detailed rules sit in the references, which are as binding as this file. No rule was dropped.

How to work:

1. Use this skill only when the optional HOI4 Mod Setup super-event runtime is installed or the repository already has an accepted super-event architecture. Otherwise report that the workflow must be installed. Confirm the prefix and paths first ("Optional runtime and registration contract" below).
2. Decide the super-event's role (section 4 below). The role sets the tone of title, image, quote and audio.
3. For text, read [text-and-localisation](references/text-and-localisation.md), then [quotes-and-remarks](references/quotes-and-remarks.md) for the quote and the button remark.
4. For audio, read [audio-research](references/audio-research.md) before searching, then [audio-implementation](references/audio-implementation.md) before converting and wiring.
5. For the image direction and slot wiring, read [wiring-image-and-special-types](references/wiring-image-and-special-types.md).
6. For docs and the research note, read [documentation-and-research-note](references/documentation-and-research-note.md).
7. Before reporting completion, read [completion-checklist](references/completion-checklist.md) and confirm every item.

Costly to miss, with the full text in the references: never invent or misattribute a quote. Each super-event needs its own real, rights-verified musical track of 1 to 2 minutes with its own audio id. Never use generated tones, placeholders or defaults, and stop and report the blocker instead of faking a cue. Reserve one integer registration ID per super-event and never recycle it. For scripted-GUI surfaces `hoi4.gui_inspect` and `hoi4.gui_render` are mandatory before edits and after wiring. Update `GetSuperEventImage` in scripted localisation, or the slot shows default art. Do not wire only one part of the package.

## Reference map

- [Text and localisation](references/text-and-localisation.md): Read before writing or editing a super-event's localisation keys, title, description or button text. Covers: Localisation format; Title rules; Description rules; Button text and remark rules.
- [Quotes and cultural remarks](references/quotes-and-remarks.md): Read before choosing, researching, verifying or documenting a main quote or a cultural remark, or when matching quote style to a super-event type. Covers: Quote rules; Quote research workflow; Cultural remark research workflow; Quote style by super-event type.
- [Audio research](references/audio-research.md): Read before searching for, evaluating or rejecting a super-event track. Covers: Audio research purpose; Audio research rules.
- [Audio implementation](references/audio-implementation.md): Read before downloading, converting, editing or wiring a super-event track and its sound definitions. Covers: Audio implementation workflow; Audio editing notes; Audio implementation expectations.
- [Documentation and research note](references/documentation-and-research-note.md): Read before documenting a super-event's audio, event docs or its research note. Covers: Audio documentation; Documentation requirements; Manifest or research note.
- [Image handoff, slot wiring and special types](references/wiring-image-and-special-types.md): Read before handing image direction to `hoi4-feature-assets`, wiring a super-event slot, or designing a world-end, defeat-aftermath or improvement-addendum super-event. Covers: Super-event image handoff; Super-event slot wiring; World-end super-events; Defeat aftermath super-events; Improvement-loop super-event depth.
- [Completion checklist](references/completion-checklist.md): Read before reporting completion of any super-event task. Covers: Audio validation checklist; Final checklist.

## 1. Core purpose

A super-event is a major presentation moment.

It should mark a major event, major escalation, defeat aftermath, or world-end scenario that deserves stronger treatment than a normal popup.

A super-event package must keep these parts aligned:

- super-event slot
- title localisation
- description localisation
- button text localisation
- quote localisation
- image
- audio id
- final sound file
- audio documentation
- event trigger or effect wiring
- settings-aware sound playback
- event docs
- catalog or spreadsheet entry when the repository maintains one

Do not wire only one part of a super-event. The image, text, quote, sourced audio, event effect, docs, and any maintained catalog must agree.

## 2. When to use this skill

Use this skill for:

- major-event super-events
- evolved minor events that become major enough for super-event treatment
- world-end scenario super-events
- defeat aftermath super-events
- major faction or world-order announcements
- global threat escalation
- large event chain milestones
- super-event quote research
- super-event audio research
- super-event audio documentation
- super-event localisation updates
- super-event image handoff to `hoi4-feature-assets`

Do not use a super-event for every dramatic event. Use it when the campaign moment should feel larger than a normal popup.

## 3. Relationship with other skills

### `hoi4-events`

Use `hoi4-events` for the full implementation contract:

- event script
- event registration
- event log
- evolutions
- world-end logic
- docs
- spreadsheet updates
- full event system wiring

### `hoi4-feature-assets`

Use `hoi4-feature-assets` for:

- super-event image sourcing or generation
- image processing
- PNG previews
- DDS conversion
- sprite handoff notes for main-agent `.gfx` wiring
- asset manifests

Super-event images may be sourced or generated. Prefer generated images for fictional, alternate-history, symbolic, supernatural, surreal, or emotionally specific moments. use sourced images when the visual must depict real historical material.

### This skill

This skill owns:

- super-event presentation design
- localisation structure
- quote selection and verification
- audio research and licensing checks
- audio documentation
- super-event package checklist

### Custom research subagent split

For actual research work, use the narrow project subagents instead of making one agent research everything at once.

| Need | Spawn |
| --- | --- |
| Main quote candidates, wording verification, attribution, source confidence, and quote recommendation | `hoi4_super_event_quote_researcher` |
| Button text, cultural remark, short allusion, slogan, title-like reference, and copyright-risk notes | `hoi4_super_event_quote_researcher` |
| Audio candidates, license verification, legitimate download, conversion to a game-ready `.wav`, and audio research notes | `hoi4_super_event_audio_researcher` |
| Real historical, archival, or real-world super-event image that must depict real material | `hoi4_asset_source_researcher` |
| Fictional, alternate-history, symbolic, supernatural, surreal, or emotionally specific generated super-event image | `hoi4_generated_feature_art` |

The main agent owns final localisation, scripted localisation, slot wiring, settings-aware sound playback wiring, audio id wiring, sound definition wiring, `.gfx` image wiring, event trigger wiring, docs alignment, and catalog alignment. When the repository maintains an authoritative XLSX and generated CSV exports, edit only the XLSX and run its repository-owned export command; never edit generated exports directly.

The quote, remark, audio, and image subagents produce research notes, final files where applicable, and handoff notes. They do not edit event files, localisation files, `.gfx` files, GUI files, sound definition files, or spreadsheet rows unless the parent prompt explicitly expands their scope.

## Optional runtime and registration contract

Use this skill only when the optional HOI4 Mod Setup super-event runtime is installed or the repository already has an accepted super-event architecture. The upstream package uses `hoi4ms_*` only as stable source and manifest names. Installation adapts runtime filenames, scripted identifiers, namespace, sprites, localisation keys, flags, and example text to the confirmed `<mod_prefix>_*` and project name.

The optional package normally installs:

```text
interface/<mod_prefix>_super_events.gui
interface/<mod_prefix>_super_events.gfx
common/scripted_guis/<mod_prefix>_super_events.txt
common/scripted_effects/<mod_prefix>_super_events.txt
common/scripted_localisation/<mod_prefix>_super_events.txt
events/<mod_prefix>_super_event_examples.txt
localisation/english/<mod_prefix>_super_events_l_english.yml
gfx/interface/super_event_option.dds
gfx/super_events/super_event_bg.dds
gfx/super_events/super_event_default.dds
gfx/super_events/super_event_image_default.dds
gfx/super_events/super_event_template.psd
gfx/super_events/super_event_image_template_457x328.psd
docs/super_events/README.md
```

Never copy identifiers or feature-specific content from another mod, and never silently replace an existing custom architecture. If the installed runtime is absent, use only the repository's accepted custom architecture or report that the optional workflow must be installed.

Before editing, confirm the project prefix and installed paths; inspect the owning event, effect, focus, decision, on-action, or other caller; inspect the current GUI, GFX, scripted GUI, scripted localisation, localisation, assets, audio definitions, and permanent docs; check for existing IDs and presentation moments; and identify every player-visible and AI invocation path.

For every supported scripted-GUI surface, `hoi4.gui_inspect` and `hoi4.gui_render` are mandatory before edits and after wiring. If the route or scenario is unavailable, record the exact blocker and leave the layout claim unresolved. Source review is not equivalent MCP evidence.

Every registration keeps these surfaces aligned:

- stable integer registration ID and unique owning caller
- project-scoped visibility state, close behavior, and cleanup
- image sprite and texture
- title, description, sourced quote, and short response remark
- unique rights-verified Internet-sourced audio file, ID, sound definition or wrapper, playback route, and provenance
- permanent documentation, smoke-test evidence, and live acceptance handoff

Reserve one integer per super-event and never recycle an established ID for a different moment. The installed runtime exposes a project-adapted helper equivalent to:

```text
<mod_prefix>_show_super_event = {
    SUPER_EVENT_ID = <integer>
}
```

The helper stores the selected ID in the project visibility state. Every scripted-localisation branch for image, title, description, quote, and remark must read the same integer; the close action clears the state. Add one sprite, one branch to each required `defined_text` block, all localisation keys, the accepted caller, the sourced-audio wiring, and a permanent registry record for every new ID.

The package's hidden `<mod_prefix>_super_event.1` event is smoke-test infrastructure. It should open the default package and close cleanly. Do not repurpose ID `1` without updating the package docs and test.

## 4. Super-event design role

Before wiring a super-event, decide what role it plays.

Common roles:

- first reveal
- escalation
- global response
- faction formation
- world-end scenario
- defeat aftermath
- irreversible political shift
- campaign-ending signal
- rare hidden branch
- ideological victory or collapse

The role should determine the tone, title, image, quote, and audio.

Do not choose a quote, image, or track because it sounds dramatic in isolation. It must fit the exact super-event role.

