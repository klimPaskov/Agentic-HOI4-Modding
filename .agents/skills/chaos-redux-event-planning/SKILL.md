---
name: chaos-redux-event-planning
description: Use when turning a rough Chaos Redux event idea into a detailed event specification before implementation.
---

# Chaos Redux Event Planning

Use this skill to design or expand events for the Hearts of Iron IV mod Chaos Redux.

This skill creates event specifications. It does not implement code. Implementation belongs to `chaos-redux-events`. Visual asset generation and processing belongs to `chaos-redux-event-assets`.

## 1. Required reading

Before writing the event specification, use the following as the design baseline:

- `AGENTS.md`
- `chaos-redux-events`
- provided event spreadsheet rows
- provided existing event docs
- provided Chaos Redux mechanics docs

Use those sources to understand how Chaos Redux works, then expand creatively from there.

## 2. Input

The user will provide either:

- a rough event idea
- a partly developed concept
- an existing event that needs deeper rework
- a detailed spec that needs cleanup before implementation

Treat the user’s idea as the starting point. Do not assume it is final.

When the idea is rough, expand it into a deeper design.

When the idea is already detailed, preserve the core direction and improve structure, clarity, missing connections, and implementation readiness.

## 3. Design purpose

The goal is to create an event that feels like a layered Chaos Redux system, not a basic popup.

The event should have atmosphere, player choice, consequences, escalation, lore, replay value, and enough visual support to feel finished.

The design should stay open and creative. Do not reduce the event to a rigid checklist. Use the structure that fits the idea best.

## 3.1 Depth standard

The specification should be as deep as the event idea deserves.

For small events, this may mean a compact but complete spec. For major events, world crises, custom UI systems, event chains, or events with evolutions, the spec should become very large and multi-part.

Do not aim for a short answer. Aim for a complete design.

For larger events, it is acceptable and expected for the finished specification to span many files and potentially reach thousands of lines. A large event can justify 10,000+ lines across all parts.

Do not add filler to reach a size target. Add depth by thinking through the event from every useful angle:

- player experience
- event pacing
- escalation
- alternate paths
- rare outcomes
- AI behavior
- world reactions
- country-specific reactions
- ideological interpretations
- UI presentation
- event log presence
- asset needs
- possible super-events
- possible world-end branches
- interactions with existing Chaos Redux systems
- documentation needs

The finished spec should make the coding agent feel like the event has already been fully designed.

## 3.2 Focus tree depth standard

Focus trees should feel fully designed, not added as a thin bonus.

Every focus should have a purpose. It should create a real choice, unlock a meaningful effect, reveal lore, change the country’s direction, support a playstyle, or connect to the event’s wider consequences.

Do not design filler focuses just to make the tree larger.

A large country or major event outcome can justify a very large focus tree. A country can have around 100 focuses if the design supports that scale.

When planning a focus tree, think through:

- main political paths
- mutually exclusive branches
- hidden or conditional branches
- military development
- industry and economy
- diplomacy and factions
- internal power struggles
- balance of power
- ideology-specific routes
- event-driven unlocks
- rare campaign-state paths
- consequences of earlier player choices
- long-term replay value
- AI path behavior
- focus icons and visual identity
- evolution or chaos meter locked paths
- world end scenario path(s)

The focus tree should feel like it was designed carefully from the beginning. It should have enough alternate paths, internal logic, and meaningful decisions that a player can replay the country and get different experiences.

## 4. What the specification should explore

A strong specification usually explores:

- the core event concept
- why the event matters
- how the event first appears
- what the player sees and chooses
- what consequences follow
- how the situation can escalate
- what rare variants can happen
- how AI countries react
- how the event changes under different world conditions
- whether the event should create focus tree content
- what UI or visual presentation would make it stronger
- what other Chaos Redux systems it should interact with
- what assets the event needs
- what the coding agent needs to know before implementation

When exploring these areas, do not stop at the first obvious answer. Consider multiple possible versions of the event, then choose or describe the strongest ones.

For important events, think through edge cases, country differences, player incentives, AI incentives, possible abuse, pacing, cooldowns, narrative tone, and how the event feels after it has fired several times or evolved.

The final result should feel like a complete design document, not an outline.

## 5. Chaos Redux system awareness

Consider links to existing Chaos Redux systems when they strengthen the event.

Possible links include:

- Chaos Meter
- evolutions
- super events
- world-end scenarios
- event clusters
- condemnation
- deaths
- air cleanliness
- chemical warfare
- biological warfare
- world threats
- existing or planned events

Leave out connections that feel artificial.

## 6. Escalation and uncertainty

Dangerous systems should not reveal themselves too early.

Avoid blunt labels such as:

- Warnings
- Danger
- Threat
- World Ending Risk
- any direct UI label that tells the player too plainly what is coming

Early information should feel incomplete. Use uncertainty, conflicting reports, rumours, cautious diplomatic language, intelligence disagreements, unexplained incidents, and unclear public reactions.

The player should understand the deeper danger through patterns and consequences over time.

## 7. Depth and hidden connections

Look for design connections the user may not have considered.

Useful connection types can include:

- callbacks to existing events
- links to planned events
- rare unlock conditions
- alternate branches
- campaign-state dependent outcomes
- ideological interpretations
- historical parallels
- secret projects
- military exploitation
- propaganda themes
- myths or rumours
- diplomatic consequences
- internal faction disputes
- scientific uncertainty
- black market effects
- civilian behaviour
- regional differences
- long-term instability

Add these only when they make the event stronger.

## 8. Custom UI and presentation

If the event benefits from custom UI, design one.

Describe what the player sees, how it changes, and what visual assets are needed.

## 9. Writing style

Write in a serious, direct, grounded HOI4 style.

Avoid:

- generic disaster wording
- empty dramatic language
- making every event apocalyptic
- random chaos without purpose
- implementation code
- excessive technical detail

Mention implementation only where it matters for the design, such as super-event treatment, custom UI, AI behavior, documentation, assets, or important system connections.

## 10. Specification shape

Do not force the specification into a fixed template.

Choose the structure that best fits the event idea.

The specification should still be easy for a coding agent to use. Use clear headings, explain the logic in a natural order, and make sure the important design decisions are not buried.

## 11. Depth and continuation

Do not compress the spec so much that important ideas become shallow.

The goal is depth, not speed.

Think through the event as far as the idea can reasonably go. If the event has multiple branches, evolutions, rare variants, UI elements, super-events, or major system connections, treat each of those as deserving real design space.

Large events should be written across multiple parts instead of being rushed into one response.

Each part should be complete enough to be useful on its own. Stop at a clean point and state what section should continue next.

Do not summarize later sections just because the current response is getting long. Continue in the next part instead.

For major events, the final combined specification may be extremely long. That is acceptable. A 10,000+ line specification is valid if the event truly needs that much design detail.

Avoid filler. Every section should add useful design, player-facing detail, implementation clarity, asset direction, or system connection.

## 12. Asset planning

The event specification should identify all important visual assets.

Consider whether the event needs:

- idea icons
- national spirit icons
- focus icons
- decision category icons
- decision icons
- achievement icons
- news event pictures
- report event pictures
- super-event art
- leader portraits
- faction emblems
- flags
- UI
- progression-state variants

Asset generation, cropping, resizing, DDS conversion, file placement, `.gfx` wiring, and manifests belong to `chaos-redux-event-assets`.

This skill should only define what assets are needed and what they should represent.

## 13. Asset prompt handoff

After the full event specification is complete, create a separate copy-pasteable asset prompt for `chaos-redux-event-assets`.

The asset prompt should include:

- required assets
- visual style
- symbols and motifs
- target sizes
- intended in-game use
- suggested filenames
- suggested sprite names
- whether each asset is for an event, report event, news event, super-event, decision, idea, focus, achievement, flag, leader portrait, or UI element
- manifest requirements

The prompt must state that image generation should be used for the base artwork.

Do not make the asset prompt vague.

## 14. HOI4 asset size reference

Use these sizes when planning assets:

- report event images: 210x176
- news event images: 397x153, black and white
- leader portraits: 156x210
- flags small: 10x7
- flags medium: 42x26
- flags normal: 82x52
- tech icons small: 64x64
- tech icons medium: 132x52
- achievements: 64x64
- super-event art: 457x328
- decision icons: 32x32
- idea and national spirit icons: 64x64
- focus icons: 94x86

Use other sizes when the event’s UI or asset type requires it.

## 15. Asset style reference

When planning visuals, use these style expectations.

Report and news event images should look like documentary photographs. News event images should be black and white.

Super-event art should be finished cinematic art before it is cropped or resized.

Focus icons should look like HOI4 focus icons, with a central symbol, readable silhouette, aged texture, painterly detail, and strong contrast.

Idea and national spirit icons should look like compact HOI4 icon art. They need strong symbolic shapes and clear readability at 64x64. They are similar to focus icons, but they are just missing the main frame.

Achievement icons should be readable at 64x64 and have a clear completion theme. The completed version is generated first. Grey and not-eligible variants can be produced later.

Flags should use clean symbols that remain readable at HOI4 flag sizes.

Progression-state variants may include selected, dim, active, locked, completed, rejected, damaged, corrupted, urgent, meter-fill, and bar-fill states.

Photoshop may be mentioned only for progression-state variants.

## 16. Super-event music planning

If the event has super-events, the asset prompt should also request music research.

For each proposed track, ask for:

- title
- composer
- performer or recording source if relevant
- public domain status
- source link
- why it fits the super-event

Do not claim public domain status without checking.

If the license is unclear, mark the track as uncertain.

## 17. Output rules

The event specification itself should be created as a downloadable Markdown file.

The spec file should contain only the event specification.

Do not put the asset prompt or coding-agent prompt inside the spec file.

For multi-part specs, create sequential files:

- `event_name_spec_part_1.md`
- `event_name_spec_part_2.md`
- `event_name_spec_part_3.md`

Continuation files should continue directly from the previous part so they can be combined later without cleanup.

Do not repeat earlier sections unless needed for clarity.

## 18. Final prompts

Only after the full specification is complete, output two separate copy-pasteable prompts outside the downloadable spec file.

### Asset prompt

Create an asset prompt for `chaos-redux-event-assets`.

The prompt should cover all required visual assets, progression-state variants, super-event music research when needed, and final asset packaging.

### Coding-agent prompt

Create a coding-agent implementation prompt that summarizes the finished event spec.

The prompt must tell the coding agent to:

- implement the event according to the spec
- implement any required focus tree content with meaningful focuses, coherent branches, proper icons, localisation, AI behavior, and event integration
- follow `AGENTS.md`
- follow `chaos-redux-events`
- use `chaos-redux-event-assets` if visual assets are required
- keep all Chaos Redux systems aligned
- report anything that cannot be implemented cleanly
- keep iterating until the full spec is implemented
- avoid fallbacks, simplifications, temporary versions, and good-enough approximations