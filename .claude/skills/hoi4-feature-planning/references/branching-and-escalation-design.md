# HOI4 Feature Planning: Branching and escalation design

Part of the [hoi4-feature-planning](../SKILL.md) skill. Read before mapping decisions, rare variants, branches, baseline stages, escalation variants or escalation text.

## 3.4 Full decision, rare variant, and branch mapping

When the feature includes decisions, rare variants, country paths, custom actors, or special outcomes, map them out fully.

Do not write vague lines such as:

- add some decisions
- add rare variants
- create several flavor events
- the country should get a focus tree
- the branch can become extreme
- some strange countries may appear

Instead, define the content. For each meaningful decision or decision group, map:

- who sees it
- when it becomes available
- what it means in the story
- what the player is choosing between
- what short-term consequence follows
- what long-term consequence it can create
- what pressures, cooldowns, costs, sacrifices, or risks it changes
- what the decision costs beyond political power or command power, such as army XP, navy XP, air XP, equipment, manpower, stability, war support, fuel, trains, convoys, supply strain, tied-down divisions, local support, faction cohesion, foreign influence debt, legitimacy, or crisis pressure
- what AI should prefer and why
- what variants or follow-up events it can unlock
- what assets, icons, or localisation it needs

For rare variants, map:

- the conditions that make them possible
- the campaign state that makes them more likely
- what the player first sees
- how observers interpret it
- what new rules or actors it adds
- what decisions, focuses, spirits, features, or text and audio packages it unlocks
- how it ends, spreads, mutates, or is contained
- what makes it different from the baseline feature

For branch trees or outcome webs, show the structure. Use headings, named routes, tables, or lists. The coding agent should not have to invent the branch map.

## 3.8 Baseline stages and escalation variants

Baseline stages and escalation variants are different.

Baseline stages describe the ordinary flow of the feature. They are the expected crisis lifecycle, such as first outbreak, containment attempt, spread, coalition formation, deep collapse, settlement, or defeat.

Escalation variants are mutation tracks layered on top of the baseline. They make the feature more predictable in some ways, more severe, stranger, more patterned, or more replayable. They can add new actors, new rules, new incidents, new tags, old movements, strange variants, stronger breakaways, or rare side branches.

Do not treat ordinary stages as special escalation variants.

Do not use escalation tiers as simple walls that lock ordinary stage progression. Ordinary stages should flow from the feature state. Escalation should affect intensity, probability, severity, weirdness, and opening strength.

### Escalation variant entry paths

When a feature has escalation variants, the spec must say how each escalation variant enters play. Do not write escalation variants only as future modifiers or only as post-fire upgrades unless that is truly the design.

Use two separate entry-path concepts when the feature supports both.

**Active feature escalation variant** means the feature is already active and an escalation variant unlocks while one or more actors from that feature still exist or the feature system is still active. The spec must define what changes immediately for the active actors: focus paths, decision families, national spirits, unit growth, targeting rules, AI strategy, faction behavior, source-researched text or audio eligibility, and cleanup. The feature should not need to activate again for the active actor to receive the escalation variant content.

**Pre-activation escalated opening** means the feature has not started yet, but the world state, escalation tier, previous escalation variant memory, or other allowed feature trigger lets the first activation start in a more escalated form. The spec must define the changed opening package: number of actors, target selection, starting ideas, initial units, first decisions, opening features, AI plan.

If both entry paths exist, write both explicitly under one escalation variant. For example, a feature may have an active escalation variant that unlocks a focus path for an already spawned country, while a later first run may start with multiple spawned countries.

If the repository uses a staged escalation model, keep stages readable and avoid stacking multiple unrelated variants behind the same threshold.

Good escalation variants can include:

- the same kind of crisis becoming easier to recognize and harder to stop
- foreign liaison networks appearing
- old historical movements returning in changed form
- new custom tags appearing that did not exist in vanilla
- extremist, occult, scientific, cultic, or ideological splinters appearing at high escalation
- strange fighter movements, partisan networks, or paramilitary identities forming
- new focus tree routes and decision categories opening

Each escalation variant should define:

- what changes from the baseline
- what conditions make it possible
- what makes it more likely
- what new player-facing content appears
- what new incidents or variants it unlocks
- what optional history or documentation title direction should represent
- how it interacts with escalation tier without being only a escalation-tier lock
- how it can be contained, spread, or escalate

## 6. Escalation and uncertainty

Dangerous systems should not reveal themselves too early.

Player-facing escalation text must not label itself as a warning, a non-warning, a threat, a danger signal, or a campaign-ending risk. Do not tell the coding agent to write text that announces what the player is supposed to infer. Do not frame a feature-detail entry, report, news item, tooltip, decision category, focus description, quote, remark, image, or audio direction, or external record summary around that direct label.

Use mysterious information, fear, and uncertainty instead. Early information should feel incomplete because people cannot yet explain what is happening.

Do not build mystery from bureaucratic document motifs, archive-style secrecy, diplomatic evasions, or paperwork drama. Avoid staged contrast formulas that make tension from one side saying or seeing something while an official body denies, delays, softens, avoids, or reacts to it. Avoid timing formulas that make one observation happen before an official admission, public reaction, government response, or wider consequence. Describe the observed fear and uncertainty directly.

The player should understand deeper danger through patterns and consequences over time. It should not explain that the content is a warning or reassure the player that it is not one.

