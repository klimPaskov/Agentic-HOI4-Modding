# HOI4 Decisions and Missions: Balance review and completion report

Part of the [hoi4-decisions-missions](../SKILL.md) skill. Read before reporting completion, before the balance review, and before delegating patches to decision subagents.

## 12. Duplicate mission cleanup

Before claiming completion, audit for duplicates.

Duplicate warning signs:

- same owner
- same category
- same trigger
- same requirement threshold
- same success effect
- same failure effect
- different name but same gameplay
- repeated stability or war support thresholds
- repeated generic stockpile checks

Create or update a mission audit for large systems.

Suggested audit table:

| Mission | Owner | Category | Region | Requirement | Duration | Success effect | Failure effect | Duplicate risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Merge, remove, or rewrite duplicates.

## 19. Balance review

For large decision and mission systems, balance review is required.

Review:

- opening values
- daily changes
- weekly changes
- monthly changes
- mission success effects
- mission failure effects
- auto-completion effects
- AI use
- costs
- durations
- active mission count
- reward strength
- threat or pressure growth
- edge cases
- cleanup behavior

Document test scenarios or observations. Do not only say `balanced`.

### Production action contract tests

When source contract tests cover a paid action, execute the real selector, action mapper, debit, refund, receipt, and cooldown helpers that belong to the tested path.
Restrict mocks to native primitives or explicitly out-of-scope consumers, and record those boundaries in the evidence.
Assert the actual native flag identifier, requested cooldown duration, and write count on success, rejection, refund, and repeated invocation where applicable; a mocked success counter does not prove that the production mapper has the required branch.
Do not replace a required production helper with a no-op solely to pass a loader error; fix the test loader or report the uncovered path.
These source tests do not establish native engine execution or timed expiry.

## Subagent patches for decision systems

Decision and mission subagents are active small-patch agents by default inside the current task scope. They can patch varied costs, clearer dynamic localisation, custom trigger tooltips, AI target checks, cleanup hooks, visibility checks, cooldown fixes, scripted GUI button text, narrow helper call sites, and existing formable requirement fixes without waiting for a separate permission prompt.

They should not expand a whole decision system, create a new mechanic window, add a new event chain, or invent a formable suite. When the gap is broad, they should write an improvement plan under `docs/plans/<event_id>_<event_slug>_plans/` and leave implementation to the main agent.

Every patch must write a handoff with changed files, changed decision or mission ids, localisation keys, behavior before and after, meaningful validation, skipped task-specific validation, and remaining design risks.

## 20. Completion report

Before the completion audit, run `python -B .tools/check.py quick` on the changed files and fix every error it lists; it checks localisation keys, decision icons and sprite wiring, script syntax and MCP script validation, not costs, balance or AI behaviour.

A decision or mission task is complete only when:

- decisions and categories exist
- focus-unlocked decisions are implemented
- route-unlocked decision families have enough content, clear AI, localisation, cleanup, and route-specific consequences
- decision categories evolve with route progress when the design calls for it
- decision pacing is early, middle, and late where relevant
- decision families have visible tradeoffs and failure states
- decision localisation explains visible baseline effects without revealing hidden outcomes
- special mechanic values are changed by decisions and missions
- important values have consistent colour identities and readable breakdowns
- balance-of-power or equivalent internal struggle decisions exist when appropriate
- faction, league, bloc, or coalition decisions include goals, membership rules, AI behavior, rewards, and success or failure states
- special mechanics have visible UI or tooltip presentation
- every mechanic surface meets the [content and interaction budget](../../hoi4-scripted-gui/SKILL.md#content-and-interaction-budget), including ordinary categories and attached displays
- scripted GUI work meets the [active MCP preview and comparison workflow](../../hoi4-scripted-gui/SKILL.md#required-mcp-visual-review-and-optional-rewrite) and [visual and usability review](../../hoi4-scripted-gui/references/visual-review.md), including intermediate preview evidence
- gameplay-changing GUI controls have action-integrity evidence from the decision owner
- visible values explain basic cause and effect without revealing hidden future surprises
- AI decisions respect route validity and avoid impossible actions
- shared decision systems are adapted per country where needed
- important tuning values are centralized in script constants or documented tuning files
- one-time reward dumps are not the main decision pattern
- fairy-dust bonuses, tiny modifiers, and harmless penalties are not the main reward or failure pattern
- every important decision, mission, GUI button, formable step, and crisis response changes play enough for the player to notice and plan around
- balance review checks for exploits, farming loops, spam, abuse cases, and low-impact reward dust
- decision categories use phases, caps, priorities, regional pools, route locks, or crisis filters to avoid clutter
- missions behave correctly
- costs are dynamic where needed
- cost localisation is readable
- inline native cost text meets its display budget without concealing any payment, and category pictures pass the simple-category gate
- long triggers are hidden or summarized
- named states, capitals, depots, borders, and regions are clear
- success and failure effects are distinct
- AI behavior is implemented
- duplicate missions are removed
- stale mission cleanup exists
- docs are updated
- meaningful validation is documented
- simplifications and blockers are reported

If anything was simplified, skipped, approximated, replaced with a weaker substitute, or reduced to tiny low-impact modifiers, report it clearly.

If nothing was simplified, say so and provide evidence.
