# HOI4 Decisions and Missions: AI, lifecycle cleanup and localisation

Part of the [hoi4-decisions-missions](../SKILL.md) skill. Read before writing ai_will_do for decisions and missions, cleanup of ended systems, or decision and mission localisation.

## 16. AI behavior

Every important decision family and mission family needs AI behavior.

AI should understand:

- when to start a mission
- when a mission is too expensive
- when a target is strategically relevant
- when to accept risk
- when to avoid escalation
- how war state changes priorities
- how stability and war support change willingness
- how foreign access changes aid decisions
- how local support changes internal decisions
- how faction membership changes league or alliance behavior
- how crisis pressure changes urgency

Avoid flat `ai_will_do` when campaign state matters.

For every in-scope decision or mission weight, route the analysis through `hoi4_ai_probability_auditor`. Establish named baseline campaign scenarios before any patch with `hoi4.probability_inspect`, and `hoi4.probability_analyze` with `analysis: "sweep"` as appropriate. The gameplay owner chooses targets and applies the patch; the auditor remains read-only. After the source change, require `hoi4.probability_analyze` with `analysis: "compare"` against the same named scenarios so the before-and-after evidence is directly comparable. Use `hoi4.probability_analyze` with `analysis: "simulate"` only for explicitly declared uncertain inputs, and use `hoi4.probability_analyze` with `analysis: "render"` when the ranking, matrix, sensitivity, comparison, or unresolved view improves review. Decision and mission `ai_will_do` results are willingness scores, so do not present them as click probabilities. Include availability, target, cost, cooldown, and route state where relevant, and retain unresolved engine state in the result. If the probability route is unavailable, record the exact blocker and do not substitute source-only analysis.

AI should not take suicidal or nonsensical decisions just because they are available.

## 17. Category cleanup and lifecycle

Decision categories and missions should have lifecycle cleanup.

When the crisis, war, target, or country state ends:

- cancel obsolete missions
- hide obsolete decisions
- clear temporary flags
- clear global event targets when used
- remove invalid target variables
- convert pre-crisis decisions into aftermath decisions only when designed
- close categories that no longer make sense

Do not leave stale missions active after the system they refer to has ended.

## 18. Localisation requirements

For every decision or mission, provide:

- category name
- category description
- decision or mission title
- decision or mission description
- visible requirement text
- cost text
- blocked cost text
- unavailable target text
- success text when visible
- failure text when visible
- effect tooltip
- dynamic scripted localisation when requirements are dynamic

Do not leave placeholder localisation.

Player-facing text should describe the world state, not implementation history.

Avoid phrases such as:

- newly added
- reworked
- dynamic baseline
- fixed in this update
- this was changed because

