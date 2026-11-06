# HOI4 Feature Planning: Exploration, depth and feasibility

Part of the [hoi4-feature-planning](../SKILL.md) skill. Read while expanding a rough idea into a deep design, and before the spec commits to any mechanic.

## 3.2 Depth standard

The specification should be as deep as the feature idea deserves.

For small features, this may mean a compact but complete spec. For major features, large crises, custom UI systems, feature chains, focus trees, custom tags, or features with escalation variants, the spec should become very large and multi-part.

Do not aim for a short answer. Aim for a complete design.

For larger features, it is acceptable and expected for the finished specification to span many files and potentially reach tens of thousands or more than 100,000 lines. A huge feature with multiple countries, full focus trees, rare variants, and international-order routes can justify 100,000+ lines, and even more, across all parts if the content is meaningful. Do not shorten the spec because it becomes long.

Do not add filler to reach a size target. Add depth by thinking through the feature from every useful angle:

- player experience
- feature pacing
- escalation
- alternate paths
- rare outcomes
- decision maps
- branch maps
- AI strategy matrices
- country package matrices
- starting armies, unit templates, force-growth decisions, and dynamic military setup for newly appearing countries
- dynamic country identities, cosmetic names, flags, leaders, and politics
- AI behavior
- world reactions
- country-specific reactions
- ideological interpretations
- UI presentation
- optional feature history or logging surface presence
- assets
- text and audio packages
- achievements and difficult achievement routes
- campaign-ending branches
- linked feature group behavior
- focus trees
- clear focus-tree path maps with major routes, anchor focuses, mutual exclusions, and branch logic
- custom tags
- flag, portrait, emblem, and country-identity asset needs
- historical source needs for real flags, leaders, symbols, and portraits
- interactions with existing mod systems
- documentation needs

Every section should add usable design, player-facing detail, implementation clarity, asset direction, or system connection.

## 3.3 Research depth standard

Use research to make the feature richer. Do not rely on the first obvious idea.

When the feature has historical, cultural, scientific, political, regional, military, religious, or ideological inspiration, research enough to produce specific variants, names, factions, symbols, motives, and consequences.

Research should help answer:

- what real or plausible movements inspire the feature
- what old conflicts, myths, institutions, military traditions, or political factions can return
- what regional differences should matter
- what foreign governments would believe
- what soldiers, civilians, journalists, scientists, diplomats, or observers would think
- what rare branches can appear only in unusual campaign states
- what assets and symbols would fit each branch
- what focus tree paths each new country should have
- what starting forces and later unit-generation routes each new country should have
- what each major focus path and anchor focus should do, unlock, represent, and connect to
- what achievements would reward deep mastery, rare routes, and difficult campaign outcomes

If the topic is niche, current, uncertain, or historically specific, verify with reliable sources. Do not invent source claims. If a source-dependent point is uncertain, mark it as uncertain.

Research should not make the spec dry. Use it to create better feature content.

## 4. What the specification should explore

A strong specification usually explores:

- the core feature concept
- why the feature matters
- how the feature first appears
- what the player sees and chooses
- what tone the feature options use, including irony, sarcasm, cultural remarks, humour, or plain severity where appropriate
- what consequences follow
- how the situation can escalate
- what rare variants can happen
- how AI countries react and choose routes
- how the feature changes under different world conditions
- what decisions exist and how they interlock
- whether the feature should create focus tree content
- whether the feature should create new tags or transform existing countries
- what starting units and reinforcement routes new countries receive
- how each new or transformed country changes names, flags, leaders, ideologies, parties, and politics
- whether the feature needs sourced quotes, cultural remarks, or audio
- what achievements should exist and why they are difficult
- what UI or visual presentation would make it stronger
- what other mod systems it should interact with
- what assets the feature needs, including all route-specific country assets
- what historical flags, symbols, and portraits must be sourced rather than generated
- what the coding agent needs to know before implementation

When exploring these areas, do not stop at the first obvious answer. Consider multiple versions and choose or describe the strongest ones.

For important features, think through edge cases, country differences, country package completeness, player incentives, AI incentives, abuse risks, pacing, cooldown factors, narrative tone, repeat play, and escalated behavior.

## 5. Mod system awareness

Consider links to existing mod systems when they strengthen the feature. Do not copy a system from another repository just because the source package had one.

Possible generic links include:

- escalation values or pressure meters that already exist in the target repository
- optional feature history or logging surfaces that already exist in the target repository
- text and audio packages
- decisions, missions, focus trees, country packages, scripted GUI, achievements, and formables
- diplomacy, war, ideology, casualties, public panic, contamination, legitimacy, recognition, or other mechanics that the target repository already supports
- existing or planned features in the same mod

Leave out connections that feel artificial. Optional registry hooks, debug menus, parent-provided tracking records, and custom UI surfaces should be used only when the target repository actually has them.

### Feasibility check

Before the spec commits to a mechanic, confirm with the reference tools, the game's documentation and vanilla precedent that each hook, effect, trigger and scope it relies on exists in the installed game and fires where the design needs it, and trace the real setters of every flag or variable the design reads. Record the result beside the spec item with its evidence tag: `[game-tested <version>]`, `[vanilla-confirmed <version>]`, `[docs]` or `[unverified]`. A mechanic that cannot be confirmed stays `[unverified]` and becomes a consultation question with a fallback, not a silent assumption.


## 7. Depth and hidden connections

Look for design connections the user may not have considered.

Useful connection types can include:

- callbacks to existing features
- links to planned features
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
- old movements returning under new conditions
- custom countries that only make sense in specific campaign states

Add these when they make the feature stronger.

