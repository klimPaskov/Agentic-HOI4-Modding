# HOI4 Events: Spec fidelity

Part of the [hoi4-events](../SKILL.md) skill. Read before implementing an event feature from docs/specs, and before deciding to merge, skip or simplify a mapped item.

## Spec and plan locations

Feature specs for event-related work live under `docs/specs/<feature_slug>/`. Implementation should read those files as the main design source when they exist.

Subagent plans, expansion addenda, audit follow-up notes, and implementation handoffs live under `docs/plans/<feature_slug>/`. Plans are working documents. If a plan becomes accepted source design, merge it into the relevant spec.


## Spec fidelity and implementation quality

When implementing from `docs/specs/`, treat mapped content as acceptance criteria. Do not silently replace mapped mechanics, routes, countries, decisions, achievements, assets, or text and audio packages with smaller fallback versions. If something must be merged, skipped, or simplified, report it in the completion notes with the reason and affected files.

Use dynamic factors for pressure, cooldowns, progress, chance, support, duration, costs, AI willingness, spawn strength, aid amounts, stage movement, recognition, etc when the spec calls for a living system. Flat values are allowed only as constants, caps, floors, or deliberate tuning anchors. Centralize shared values in script constants or documented tuning.

Do not implement major decisions, missions, focus rewards, GUI buttons, or event responses as political power or command power purchases by default. Use concrete costs and requirements from the spec when relevant: XP, equipment, manpower, fuel, trains, convoys, supply, stability, war support, local support, held states, unit presence, foreign access, intelligence exposure, or time pressure. Tooltips must explain blocked nonstandard requirements.

When the spec maps focus paths, implement a real tree, not a thin vertical chain. Preserve route locks, side branches, convergence points, hidden branches, crisis branches, AI weights, focus filters, varied icons, and branch payoffs. Rewards should vary across buildings, units, decisions, missions, advisors, identities, claims, cores, diplomacy, technologies, and mechanic changes. Do not fill trees with repeated new ideas, tiny modifiers, political power, stability, or war support.

When implementing starting or route ideas, wire their lifecycle. Negative, mixed, staged, or route-specific ideas should be removed, upgraded, replaced, worsened, or consumed by the mapped decisions, focuses, missions, wars, failures, or reforms. Avoid dead idea stacks that never change.

Mechanic variables must be visible somewhere meaningful, such as decision category text, scripted localisation, national spirit tooltip, scripted GUI, progress meter, or focus tooltip. Keep cause and effect readable. Values should be changed by the mapped decisions, focuses, missions, events, wars, state control, AI actions, and foreign influence. Use consistent localisation colours for important mechanic values and breakdowns.

Large decision systems must hide obsolete or irrelevant actions. Use phases, active caps, target pools, route locks, thresholds, emergency visibility, regional grouping, cooldowns, or cleanup flags. The category should show current playable actions, not every possible debug action.

If the spec defines achievements, implement the full achievement surface: tracking flags or variables, unlock triggers, disqualifiers, localisation, icons, docs, and any route or formable hooks. Do not convert hard achievements into automatic unlocks.

Before completion, check every visible asset named or implied by the spec: flags, ideology flags, cosmetic flags, leaders, portraits, focus icons, decision icons, ideas, achievements, faction emblems, report or news images, UI sprites, animated sprites, and static fallbacks. Do not claim completion while required visible assets are placeholders unless the completion report says so clearly.

Do not generate real historical leaders, historical flags, or well-attested real symbols as fictional art. Source them, document source and license status when possible, and convert them to the required HOI4 format. Generated art is for fictional, symbolic, alternate, supernatural, or invented identities unless the user says otherwise.

Any new, released, restored, transformed, or event-managed country that is expected to fight needs starting forces and a reinforcement pathway. Implement dynamic starting units, templates, equipment and manpower assumptions, commander or officer handling when relevant, and later unit growth through decisions, focuses, depots, objectives, volunteers, foreign support, mobilisation, or special mechanics. Do not leave a serious fighting country as an empty tag unless the spec says so and explains why.

Major events and country-creation events need route-specific AI. Implement focus choices, decision choices, unit-raising choices, faction behavior, foreign influence behavior, rare variant handling, extreme-route exceptions, invalid-route blocking, etc.

Do not reduce major spec effects to tiny decorative modifiers. Important effects must change incentives, unlock content, move visible mechanic values, alter army or economy behavior, create a real tradeoff, or connect to later outcomes.


