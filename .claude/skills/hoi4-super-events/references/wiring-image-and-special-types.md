# HOI4 Super-Events: Image handoff, slot wiring and special types

Part of the [hoi4-super-events](../SKILL.md) skill. Read before handing image direction to `hoi4-feature-assets`, wiring a super-event slot, or designing a world-end, defeat-aftermath or improvement-addendum super-event.

## 19. Super-event image handoff

Super-event images are handled through `hoi4-feature-assets`.

Default rule:

- use generated super-event images when the moment is fictional, alternate-history, symbolic, supernatural, surreal, or needs a unique emotional composition
- use internet-sourced images when the super-event must depict a real historical person, real photographed event, or real archival artifact
- follow `hoi4-feature-assets` and the image generator's workflow for generated images

The super-event skill should define the image direction:

- subject
- tone
- composition need
- symbolism
- source mode: generated, sourced, or user-provided
- source-image search direction or image-generation prompt direction
- what to avoid
- why the image fits the super-event

The asset skill handles:

- source search
- source documentation
- image processing
- PNG preview
- DDS conversion
- main-agent `.gfx` wiring
- manifest

Treat project-root `docs/assets/<feature_slug>/` as temporary evidence for super-event image and audio work. Retain source files, previews, contact sheets, manifests, provenance, research notes, and handoffs while work is active, blocked, awaiting review, or undergoing acceptance scenarios. Before declaring the feature goal fully complete, move or copy durable evidence into `docs/events/`, `docs/plans/`, `docs/specs/`, `docs/super_events/`, or another permanent documentation surface, then delete only that feature-scoped workspace. Never delete skill-local reusable assets under `.claude/skills/.../assets/` or unrelated workspaces. Do not require the deleted workspace to exist for a completion claim.

## 20. Super-event slot wiring

When wiring a super-event, choose the slot intentionally.

Make sure the implementation:

1. sets the correct visibility flag
2. sets the repository audio-selector variable
3. uses the settings-aware playback helper
4. updates scripted localisation, including `GetSuperEventImage` for the slot's sprite and the title/description/quote/remark getters
5. updates player-facing localisation
6. updates image wiring in the correct `.gfx` file
7. updates audio wiring
8. updates docs
9. updates spreadsheet or event catalog if relevant

Do not reuse a slot accidentally.

Do not let two unrelated super-events point to the same current image, text, or audio unless the reuse is intentional and documented.

## 21. World-end super-events

World-end super-events need stricter alignment.

When a super-event represents a world-end scenario:

- guard the branch with the world-end rules from `hoi4-events`
- make the terminal state clear
- set the scenario-specific global flag
- set the matching super-event visibility
- stop or gate incompatible future systems and branches
- make the docs and spreadsheet agree
- choose quote and audio with finality in mind

A world-end super-event should feel like an end-state, not a normal escalation.

## 22. Defeat aftermath super-events

Use defeat aftermath super-events only when the defeated threat was global or near-global, long enough, and costly enough to reshape the campaign.

The super-event should communicate:

- what was defeated
- what the world lost
- what remains unstable
- what new order or memory follows
- why the campaign does not simply return to normal

Quotes and audio should usually feel reflective, not triumphant without cost.

## 25. Improvement-loop super-event depth

Improvement addenda can propose new super-events, but a super-event should still mark a real campaign threshold. Do not add one just because a route has a strong image. Use one when a formable changes regional order, a hidden route becomes public, a scripted GUI mechanic reaches a global milestone, a league or world threat emerges, or a defeat aftermath reshapes the campaign.

For formables, the super-event should reflect the formation method. A negotiated federation, violent restoration, occult revival, imperial proclamation, anti-colonial congress, and puppet-backed union should not share the same tone. The title, quote, image, audio, remark, and trigger should reveal the route identity.

Animated portraits or animated scripted GUI assets can support a super-event-adjacent moment, but they are not replacements for the super-event package. The super-event still needs aligned text, quote, image, audio, trigger, docs, etc.

