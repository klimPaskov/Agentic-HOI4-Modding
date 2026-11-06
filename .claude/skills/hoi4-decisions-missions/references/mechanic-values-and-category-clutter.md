# HOI4 Decisions and Missions: Mechanic values, factions and category clutter

Part of the [hoi4-decisions-missions](../SKILL.md) skill. Read before adding special mechanic values, faction or league goals, value breakdowns, or deciding which decisions a category shows at once.

## 15.4 Special mechanic values and faction goals

Large decision and mission systems should interact with special mechanic values.

Special mechanic values can include legitimacy, authority, influence, faction cohesion, command obedience, public panic, regional control, military readiness, industrial capacity, corruption, foreign penetration, balance-of-power position, league cohesion, or sponsor pressure.

Decisions and missions should change these values through visible actions. Do not make a mechanic where values only drift passively or change through a few flat hidden effects.

Good examples:

- a recognition mission increases legitimacy and foreign influence
- a rail repair mission increases authority and logistics control
- a military crackdown increases command obedience but lowers legitimacy
- an industrial program increases industrial capacity but consumes civilian capacity
- a foreign aid decision increases arms influence and patronage risk
- a league vote increases faction cohesion or member confidence
- a failed border mission lowers authority and raises enemy momentum

Use as few player-facing values as the mechanic can support without losing meaningful choices. Prefer one primary value and up to three supporting values. More values need distinct causes, consequences, thresholds, and player actions. Internal calculations can remain hidden or be summarized into a total when the player does not need to manage each component directly.

If a mechanic has a total value made from several components, the UI should show a readable breakdown through scripted localisation or tooltips. Each important component should be named and use a consistent colour identity.

Examples of colour identities:

- authority in blue
- threat in red
- local support in green
- foreign influence in purple
- old movement pressure in orange
- faction cohesion in yellow

Use project-appropriate colours, but keep each value consistent across decisions, missions, events, tooltips, and UI summaries. Pair colour with a label, icon, frame, meter shape, or another non-colour cue. Do not present a plain changing number with no explained range, threshold, or gameplay meaning.

A visible value has failed when the player cannot answer what changes it, why it matters, and what action responds to it. Remove, merge, summarize, or redesign such values.

Balance-of-power or equivalent internal struggle mechanics should be considered when a country has competing power centers. Decisions and missions should push the balance, create risks, unlock branch content, and affect leaders, laws, advisors, events, or crises.

When a decision system creates or manages a faction, league, bloc, coalition, compact, or alliance, define its goals and rules. Include membership conditions, joining logic, refusal logic, expulsion or removal logic where relevant, shared decisions, war goals, AI behavior, victory conditions, and failure conditions.

Important event-created factions should usually have a mechanic such as cohesion, shared command, war council support, joint reserves, recognition, member confidence, sponsor pressure, or strategic goals. Decisions and missions should interact with that mechanic.

A faction should not form just because one country exists. Use minimum membership, crisis pressure, ideological compatibility, war state, diplomatic preparation, or regional logic.


## 15.5 Mechanic presentation, value clarity, and faction outcomes

Special mechanic values must be visible somewhere the player can understand them. A decision category can show values in its header, a custom scripted GUI, a progress meter, a scripted localisation tooltip, or national spirit tooltips.

Apply the [content and interaction budget](../../hoi4-scripted-gui/SKILL.md#content-and-interaction-budget) to every decision mechanic surface, including ordinary categories, attached displays, and full windows. Keep internal calculations hidden or summarized unless they change an immediate player decision or explain an important consequence. Merge or remove weak values and duplicate actions; moving clutter into another category, tab, tooltip, or popup does not resolve it.

The three-to-six primary-action budget guides usable action presentation; it is a design and readability limit, not a hard HOI4 engine row limit.
Counts alone establish neither engine capacity nor clipping; engine or visual claims require relevant documentation or actual consumer and render evidence, and source or scenario decision inspection is not visual proof.
Preserve accepted gameplay and navigation scope; do not require deletions or extra categories solely from a count.

Special mechanics may hide future surprises, but public cause and effect must remain clear: what changed a visible value, its consequence, and the broad response available.

Faction, league, bloc, or coalition goals need rewards and failure states. A successful faction goal can unlock shared decisions, war goals, legitimacy, cohesion, member rewards, postwar settlements, or new faction leadership. A failed goal can reduce cohesion, trigger member exits, invite foreign pressure, start leadership contests, weaken shared defenses, or open emergency missions.

AI strategy must respect route and decision validity. AI should not take decisions that require missing states, dead sponsors, non-existent factions, unavailable ideologies, disabled evolutions, impossible borders, absent enemies, invalid targets, or closed routes. Invalid actions should be hidden, bypassed, or weighted to zero.

Decision systems for shared trees or shared mechanics must still feel country-specific. Use scripted localisation, country-specific targets, country-specific AI weights, local leaders, regional decisions, and route-specific rewards to prevent every country from playing the same.

Important thresholds, caps, gains, losses, duration bands, AI weights, and scaling values should be centralized in script constants or a documented tuning file. Do not scatter magic numbers across decision files, events, focuses, scripted effects, and scripted triggers.


## 15.7 Decision category clutter control

Large decision systems should not show every possible decision at once.

Use phases, caps, priorities, regional pools, route locks, mechanic thresholds, or crisis-state filters so the player sees decisions that matter in the current situation.

A decision category should feel curated by current state, not like a debug menu. Apply the [content and interaction budget](../../hoi4-scripted-gui/SKILL.md#content-and-interaction-budget) to each ordinary decision phase as well as scripted GUI surfaces. If the system exceeds its action or mission budget, first merge weak or duplicate actions, then use state-based replacement, target selection, route gates, or phased visibility.

Too many decisions often means the system contains duplicate actions, weak actions, obsolete actions, or several buttons that should be one staged action. Merge or remove them before adding UI layers.

Good clutter-control patterns:

- early, middle, and late decision tiers
- active mission caps
- region pools that rotate or unlock gradually
- decisions hidden when their route is invalid
- obsolete decisions removed after war, peace, settlement, or route change
- basic decisions replaced by stronger later decisions
- decisions grouped by target region, sponsor, faction, or mechanic value
- emergency decisions visible only during emergency states
- late-game decisions hidden until the route payoff is reached

For large targeted decision families, prefer a separate target-management category over dumping every target row into the main mechanic category. Use a compact `Show Decisions for [FROM.GetName]` / `Hide Decisions for [FROM.GetName]` flow when the human player only needs to inspect or act on one target at a time. AI should still see all decisions at once.

The reusable selected-target pattern is:

- a category dedicated to the target family
- one visible selector decision over the target array
- one visible hide/close decision for the selected target
- a root variable that stores the selected target id
- a target flag on the selected country
- helper triggers for selecting, showing selected-target decisions, and recognizing the selected target from `FROM`
- helper effects that activate and remove only the selected target decisions
- cleanup that clears the target flag, stored id, event target if global, and active target decisions when the target becomes invalid
- AI bypass or separate AI visibility so AI can still evaluate useful targets without needing a player-facing selector

Do not leave stale, invalid, or irrelevant decisions visible simply because their scripted trigger is easy to write.

