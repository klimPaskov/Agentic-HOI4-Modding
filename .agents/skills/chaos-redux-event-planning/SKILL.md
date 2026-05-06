---
name: chaos-redux-event-planning
description: Use when turning a rough Chaos Redux event idea into a repository-aware event specification before implementation.
---

# Chaos Redux Event Planning

Use this skill to design or expand events for the Hearts of Iron IV mod Chaos Redux.

This skill creates event specifications. It does not implement code by itself. It is meant for a coding agent that can inspect the repository, read the existing systems, and write a spec that is ready to implement.

Implementation belongs to `chaos-redux-events`. Visual asset creation and wiring belongs to `chaos-redux-event-assets`. Super-event quote, remark, music, and presentation research belongs to `chaos-redux-super-events`.

## 1. Repository-aware baseline

Before writing the event specification, inspect the repository context that matters for the event.

Read:

- `AGENTS.md`
- `chaos-redux-events`
- `chaos-redux-event-assets` when visual assets may be needed
- `chaos-redux-super-events` when a super-event may be needed
- the provided event spreadsheet row or catalog entry
- existing docs for the same event, cluster, mechanic, or related events
- Chaos Redux mechanics docs
- relevant existing event files and localisation files
- relevant scripted effects, scripted triggers, scripted GUIs, ideas, decisions, focus trees, or assets if the event touches them

Use the actual repo as the source of truth. Do not design as if the agent has no code access. Check existing patterns before inventing new ones.

If the repo already has a system for the thing being designed, use that system in the spec. If the repo does not have it yet, say whether the spec depends on a new system, an extension to an existing system, or a simple event-local implementation.

Do not hallucinate existing mechanics, assets, event IDs, flags, GUI elements, or file paths. If something is uncertain after inspecting the repo, mark it as uncertain.

## 2. Input

The user may provide:

- a rough event idea
- a partly developed concept
- an existing event that needs deeper rework
- a detailed spec that needs cleanup before implementation
- a spreadsheet row
- existing docs or code references

Treat the user’s idea as the starting point. Preserve the core direction unless there is a clear design or implementation reason to change it.

When the idea is rough, expand it into a stronger event design.

When the idea is already detailed, improve structure, lore, clarity, missing connections, implementation readiness, and repo alignment.

## 3. Design purpose

The goal is to create an event that feels like it belongs in Chaos Redux.

The spec should explain:

- what happens in the world
- why it might happen
- how governments, civilians, soldiers, scientists, police, diplomats, or journalists understand it when relevant
- what the player sees
- what choices exist
- what those choices mean in the story
- how the event changes when it evolves
- how it fits existing Chaos Redux systems and repo patterns

The spec should help the coding agent write believable event text, choose correct effects, wire the event cleanly, and avoid inventing missing design during implementation.

## 3.1 Lore and immersion first

The specification should read like an event design document, not a programming note.

Start from the player-facing situation. Explain the event as something happening inside the campaign world. Technical notes come later and only where they matter.

Think through:

- what the world believes happened
- what is officially claimed
- what is disputed
- what information is missing
- how the event is reported
- how different governments might frame it
- what the options feel like from the country’s perspective
- how repeated firings or later stages change the story
- what makes the event feel like Chaos Redux without becoming meaningless noise

Do not let script structure, variables, IDs, arrays, or file wiring become the main content of the spec.

## 3.2 Depth standard

The specification should be as deep as the event deserves.

Small events should stay compact but complete. Major crises, new countries, focus trees, custom UI, super-events, or world-end paths can justify very large specs.

Depth means useful design, not more words.

Add depth through:

- player experience
- believable causes
- public reaction
- country-specific reactions
- ideological interpretations
- event pacing
- escalation
- rare variants
- alternate paths
- AI behavior when it affects outcomes
- UI presentation when needed
- asset direction when assets are needed
- event log presence
- direct interactions with existing Chaos Redux systems
- documentation needs
- edge cases that the coding agent must handle

Do not add filler to make the spec longer.

## 3.3 Focus tree depth standard

Focus trees should feel fully designed, not added as a thin bonus.

Every focus should have a purpose. It should create a real choice, unlock a meaningful effect, reveal lore, change the country’s direction, support a playstyle, or connect to the event’s wider consequences.

When planning a focus tree, think through:

- political paths
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
- consequences of earlier choices
- long-term replay value
- AI path behavior
- focus icons and visual identity
- evolution or chaos meter locked paths
- world-end paths if relevant

Do not design filler focuses just to make the tree larger.

## 4. What the specification should cover

Use the sections that fit the event. Do not force a fixed template.

A strong spec often covers:

- the in-world situation
- the likely cause or trigger
- what is known, disputed, or hidden
- what the player sees first
- option text direction and option meaning
- consequences
- escalation and evolutions
- rare variants
- country, ideology, faction, or regional differences
- event cluster placement when relevant
- AI behavior when it changes outcomes
- UI or presentation needs
- assets that are actually needed
- direct interactions with existing systems
- repo-specific implementation notes that prevent mistakes

The spec should not become a generic implementation checklist. The coding agent can inspect the repo. Include only technical details that are specific to this event or easy to get wrong.

## 5. Chaos Redux system awareness

Consider links to existing Chaos Redux systems when they strengthen the event.

Possible links include:

- Chaos Meter
- evolutions
- super-events
- world-end scenarios
- event clusters
- condemnation
- deaths
- air cleanliness
- chemical warfare
- biological warfare
- world threats
- existing or planned events

Mention only direct, non-obvious, or event-specific integrations.

Do not explain automatic HOI4 or Chaos Redux behavior that will happen without special event work. For example, do not say that a war feeds world tension, normal combat creates casualties, or existing systems react to their usual inputs unless the event must add special wiring.

For event clusters, use plain wording. State which cluster the event belongs to and any secondary connection if useful. Also define the event's cluster behavior when it matters: whether it is an early, middle, or late event inside the cluster, whether it is low, medium, or high danger, whether it can fire as soon as the cluster is unlocked, and whether it is likely or only sometimes included when the cluster fires.

Do not treat cluster unlock and event eligibility as the same thing. A cluster may become available at one chaos tier while a more dangerous member event only becomes eligible inside that cluster at a later chaos tier. Say that directly when relevant.

Keep exact cluster weighting rules, minimum chances, and implementation formulas in `event_clusters_spec`. The event planning spec should describe intent and relative behavior, not technical math.

Leave out connections that feel artificial.

## 6. Escalation and uncertainty

Dangerous systems should not reveal themselves too early.

Avoid blunt labels such as:

- Warnings
- Danger
- Threat
- World Ending Risk
- direct UI labels that tell the player too plainly what is coming

Early information should feel incomplete. Use uncertainty, conflicting reports, rumours, cautious diplomatic language, intelligence disagreements, unexplained incidents, and unclear public reactions.

The player should understand the deeper danger through patterns and consequences over time.

## 7. Hidden connections and variants

Look for design connections the user may not have considered, but add them only when they improve the event.

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

Do not add hidden connections just to make the spec look larger.

## 8. Custom UI and presentation

If the event benefits from custom UI, design it.

Describe what the player sees, how it changes, what information it shows, and what assets are needed.

If normal event popups, reports, news events, decisions, or existing GUI elements are enough, use them. Do not invent custom UI because the event sounds important.

## 9. Super-event planning

Use a super-event only when the moment deserves stronger presentation than a normal popup.

A super-event should mark a reveal, escalation, transformation, defeat, aftermath, ideological victory, global response, or world-end moment that changes how the player understands the campaign.

If a super-event is needed, define:

- purpose
- trigger moment
- role
- tone
- what the player should understand
- what the world believes happened
- what remains uncertain
- image direction
- quote direction
- cultural remark direction
- audio mood
- follow-up content if needed

Do not fully research quotes, cultural remarks, or music inside this skill. Use `chaos-redux-super-events` for that work.

## 10. Writing style

Write in a serious, direct, grounded HOI4 style.

The specification should be explanatory and immersive first, then implementation-ready. Keep it concise by default.

Avoid:

- generic disaster wording
- empty dramatic language
- vague purpose lines
- word salad
- making every event apocalyptic
- random chaos without purpose
- excessive technical detail
- dry implementation scaffolding
- long lists of standard script surfaces
- repeating facts already obvious
- explaining automatic vanilla or existing Chaos Redux behavior

Do not use filler phrases such as:

- source of global instability
- raises the stakes
- deepens the chaos
- creates a layered experience
- adds more depth
- the world descends further
- tension spreads across the globe

Replace vague explanation with direct event writing. Say what happens, what people believe, who is affected, what choices exist, and how the situation changes.

Mention implementation only where it matters for the design, such as custom UI, AI behavior, documentation, assets, unusual selection rules, exclusions, or important system connections.

## 11. Specification shape

Do not force the spec into a fixed template. Choose the structure that fits the event.

The spec should be easy for a coding agent to use. Use clear headings, explain the logic in a natural order, and keep important design decisions visible.

### 11.1 No spreadsheet metadata block

Do not start the specification with a metadata block that repeats spreadsheet fields.

Avoid blocks like:

```markdown
- **Event ID:** ...
- **Event name:** ...
- **Type:** ...
- **Status:** ...
- **Cluster:** ...
- **Event availability:** ...
- **Evolution track:** ...
```

The filename, title, spreadsheet row, and implementation prompt can carry those facts. The specification should begin with the actual event design.

If a spreadsheet field needs clarification, mention it in the relevant section only.

### 11.2 No negative feature inventory

Do not list things the event does not have.

Avoid sections or bullets such as:

- no custom GUI
- no decisions
- no focus tree
- no super-event
- no world-end branch

If the spec does not mention a feature, the coding agent should assume it is not part of the design.

Only mention an excluded feature when it prevents a likely implementation mistake or corrects a user request.

### 11.3 No obvious system restatement

Do not include lines that only describe automatic game behavior.

Avoid saying that:

- wars increase world tension through normal gameplay
- normal combat can create deaths
- existing systems react to their normal inputs
- standard event registration needs to happen unless a special event-specific rule is needed

Mention a system only when the event adds special logic, changes weighting, creates a new variable, writes to a log, overrides normal behavior, gates content, or requires careful exclusion handling.

### 11.4 Keep technical detail in its place

The main spec should not become a checklist of files, scripted effects, variables, constants, event roots, or registration steps.

The coding agent has access to the code. It should inspect existing patterns and wire standard surfaces through the existing implementation skill.

Use technical detail in the spec only when it changes the event design, prevents a likely mistake, or explains a non-obvious rule.

### 11.5 Event cluster placement

Cluster sections should be plain and useful.

State the cluster membership directly:

```markdown
This event belongs in the X cluster.
```

If there is a secondary connection, state it directly.

When the event belongs to a cluster, decide the parts that affect cluster behavior:

- whether the event is early, middle, or late in the cluster sequence
- whether the event is low, medium, or high danger inside the cluster
- whether it can fire in the cluster as soon as the cluster unlocks
- whether it needs a higher chaos tier before it can appear inside the cluster
- whether it is likely, occasional, or rare when the cluster fires
- whether it is required for the cluster or only an optional member

Do not add abstract cluster justification. Do not explain the cluster as a mood or theme unless it affects visibility, ordering, weighting, event log text, or documentation.

Do not put exact formulas or minimum percentages here. Those belong in `event_clusters_spec`.

### 11.6 Direct sections

Every section should answer a useful design, lore, gameplay, or implementation question.

Useful sections often cover:

- what happens in-world
- why it happens
- what different countries or groups believe happened
- what the player sees
- what options exist and what they mean
- how evolutions change the situation
- rare variants or campaign-state variants
- AI behavior when it affects outcomes
- cooldowns and exclusions when they affect pacing or fairness
- event log text needs
- assets that are actually needed

Remove sections that only restate theme, identity, or mood without explaining the event. Keep lore when it tells the coding agent what to write, what to show, what to trigger, or how the event should feel in-game.

## 12. One-file specification rule

Create one complete Markdown specification file by default.

Do not split the spec into `part_1`, `part_2`, or similar files unless the user explicitly asks for it or a tool limit makes a split unavoidable.

A single spec file may be very large. That is acceptable when the event deserves it. Keep one clean document that can be read from top to bottom and implemented without merging multiple files later.

If the spec is large, use headings and a table of contents instead of splitting it.

Do not summarize later sections because the file is long. Write the full design in the same file.

Small events should still stay small when the idea does not justify more. A compact event can have strong flavour, clear options, evolutions, variants, cooldowns, and AI behavior without becoming a major system.

## 13. Asset planning

The event specification should identify important visual assets when assets are needed.

Consider whether the event needs:

- idea icons
- national spirit icons
- focus icons
- decision category icons
- decision icons
- achievement icons
- news event pictures
- report event pictures
- super-event images
- leader portraits
- faction emblems
- flags
- UI
- progression-state variants

Asset generation, sourcing, cropping, resizing, DDS conversion, file placement, `.gfx` wiring, and manifests belong to `chaos-redux-event-assets`.

This skill should define what assets are needed and what they should represent. For generic events, prefer existing vanilla HOI4 or existing Chaos Redux images when they fit.

Do not include assets that the event does not need.

## 14. Asset prompt handoff

Create a separate asset prompt only when the user wants a handoff prompt or when asset work is actually needed.

The asset prompt should include:

- required assets
- visual style
- symbols and motifs
- target sizes
- intended in-game use
- suggested filenames
- suggested sprite names
- asset type
- source mode
- manifest requirements
- user review requirements where relevant

Use `chaos-redux-event-assets` rules for source selection. Symbolic icons usually use `image_gen`. News event images, report event images, super-event images, and real leader portraits use sourced or existing images unless the user says otherwise.

For generic events, prefer existing vanilla HOI4 or existing Chaos Redux images when they fit. Do not require new assets only to make the asset list look complete.

## 15. HOI4 asset size reference

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
- super-event images: 457x328
- decision icons: 32x32
- idea and national spirit icons: 64x64
- focus icons: 94x86

Use other sizes when the event’s UI or asset type requires it.

## 16. Asset style reference

Report and news event images should look like documentary photographs. News event images should be black and white.

Super-event images should have a strong central composition, clear theme, readable subject, and enough contrast for HOI4 UI.

Focus icons should look like HOI4 focus icons, with a central symbol, readable silhouette, aged texture, painterly detail, and strong contrast.

Idea and national spirit icons should look like compact HOI4 icon art. They need strong symbolic shapes and clear readability at 64x64.

Achievement icons should be readable at 64x64 and have a clear completion theme. The completed version is generated first. Grey and not-eligible variants can be produced later.

Flags should use clean symbols that remain readable at HOI4 flag sizes.

Progression-state variants may include selected, dim, active, locked, completed, rejected, damaged, corrupted, urgent, meter-fill, and bar-fill states.

Photoshop may be mentioned only for progression-state variants.

## 17. Super-event research handoff

If the event has one or more super-events, create a separate copy-pasteable prompt for `chaos-redux-super-events` when a handoff prompt is needed.

For each super-event, include:

- purpose
- trigger moment
- tone
- title direction
- description direction
- quote direction
- cultural remark direction
- audio mood
- image direction
- whether it is an escalation, defeat moment, aftermath moment, ideological moment, or world-end moment
- special constraints from the event spec

The `chaos-redux-super-events` prompt should ask the agent to:

- find a real quote using the internet search MCP server
- verify quote wording and attribution
- find a meaningful cultural remark, reference, allusion, or short line where appropriate
- follow copyright limits for songs, films, books, and other protected works
- find suitable public domain or clearly licensed audio
- document all sources, license notes, and uncertainties
- coordinate super-event image needs with `chaos-redux-event-assets`

Do not claim a quote, cultural reference, or audio track is usable without checking.

If a license or attribution is unclear, mark it as uncertain.

## 18. Output rules

Create one Markdown spec file.

The spec file should contain only the event specification.

Do not put asset prompts, super-event prompts, or coding-agent prompts inside the spec file.

If working inside the repository, save the spec in the repo location that matches the project’s documentation pattern. If no pattern exists, choose a clear docs path and keep the filename stable and descriptive.

If working outside the repository, create a downloadable Markdown file.

Do not split the spec into multiple files unless the user explicitly asks or a tool limit forces it.

## 19. Final prompts and final answer

Only create separate handoff prompts when the user asks for them or when the next step clearly requires a different skill or agent.

### Asset prompt

Create an asset prompt for `chaos-redux-event-assets` only if asset work is needed.

The prompt should cover required assets, progression-state variants, review needs, and final asset packaging.

### Super-event prompt

Create a super-event prompt for `chaos-redux-super-events` only if one or more super-events are part of the spec.

The prompt should cover titles, descriptions, quotes, cultural remarks, audio research, image direction, source documentation, and licensing notes.

### Implementation prompt

Create a coding-agent implementation prompt only when the user wants a handoff prompt.

Keep it short. Tell the coding agent to implement the spec fully, follow `AGENTS.md` and the relevant skills, keep iterating until done, and report files changed, implemented work, wiring, documentation, localisation, catalog updates, validation, and anything that could not be implemented cleanly.

The implementation prompt should not repeat the whole spec.
