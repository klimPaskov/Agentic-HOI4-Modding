---
name: hoi4-decisions-missions
description: Use when designing, implementing, auditing, or fixing Hearts of Iron IV decisions, missions, timed objectives, decision categories, and mission localisation.
---

# HOI4 Decisions and Missions

Use this skill when a task touches decisions, missions, timed objectives, decision categories, mission UI, costs, trigger tooltips, scripted localisation, AI decision behavior, or balance around decision-driven systems.

This skill is for implementation and cleanup. For broader event wiring, use `hoi4-events`. For focus trees, use `hoi4-focus-trees`. For visual assets, use `hoi4-feature-assets`.

For large or reworked decision systems, spawn `hoi4_decision_mission_auditor` after implementation and before completion. The subagent is patch-capable by default inside the current task scope. It should audit objective quality, costs, tooltips, AI validity, cleanup, duplicate missions, route integration, fairy-dust rewards, exploit risk, localisation, and balance evidence. Route every complex or balance-sensitive decision or mission weight to `hoi4_ai_probability_auditor` for the mandatory MCP probability pass. It may directly patch small decision, mission, tooltip, dynamic localisation, AI, cleanup, cooldown, visibility, and existing formable requirement issues when the fix is local and clearly safer.

## 1. Required reading

Before editing decisions or missions, read:

- `AGENTS.md`
- relevant offline Paradox wiki pages from `paradox_wiki/`
  - Decision modding
  - Triggers
  - Effects
  - Localisation
  - Modifiers
  - Scopes
  - Data structures
- vanilla decision files from `C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV/`
- vanilla documentation in `C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV/documentation`
- existing repository decision categories and scripted effects that do similar work

Do not rely on memory when syntax or UI behavior is documented.

## 2. Core design rule

A decision or mission should represent something the country is actually doing. Decisions should also connect to focus routes and wider mechanics instead of sitting as isolated buttons.

Avoid turning decisions into a store where the player spends political power for small modifiers. Do not make a decision category feel like a tray of tiny stat dust. A good decision or mission usually asks the player to commit resources, move units, hold a location, secure supply, manage foreign access, spend equipment, accept risk, meet a deadline, or change a living pressure system.

A mission should feel like an order or objective. A decision should feel like a meaningful choice.

## 3. Decision and mission types

Use the right tool for the job.

### Clickable decisions

Use clickable decisions when the player chooses to start an action, spend resources, accept risk, begin a project, send aid, escalate, negotiate, or select a target.

Clickable decisions should have clear costs, clear requirements, and clear consequences.

### Timed missions

Use timed missions when the player needs to achieve something before a deadline.

Timed missions are good for:

- holding capitals
- guarding borders
- securing rail hubs
- placing divisions in named states
- maintaining supply
- blocking foreign routes
- completing local support work
- holding a depot belt
- preventing a cascade
- proving authority before an enemy does

### Goal-style auto-completing objectives

Use goal-style missions when the player should not click again after doing the work.

If the objective is “place divisions here,” “hold this capital,” “secure this rail hub,” or “reach this influence threshold,” it should auto-complete when conditions are met.

Do not make the player pay a second click after already satisfying the goal.

## 4. Dynamic values

Everything that acts like cost, duration, cooldown, support, chance, pressure, threat, reward, mission difficulty, influence, aid amount, or AI willingness should be dynamic by default.

A fixed value can be a tuning anchor, but the system should explain what changes it.

Useful factors:

- country size
- industry
- manpower
- equipment stockpile
- stability
- war support
- war state
- current fronts
- supply
- rail control
- ports
- fuel
- trains
- convoys
- terrain
- distance
- local support
- legitimacy
- foreign access
- faction membership
- previous failures
- previous successes
- chaos tier or event pressure
- AI strategy situation

Do not copy the same cost or duration across every country unless the story and balance justify it.

## 4.1 Effect strength and no fairy-dust rewards

Do not fill decision systems, missions, scripted GUI buttons, or formable routes with tiny bonuses that feel meaningless. Small values such as plus 1 percent, plus 2 percent, minus 3 percent, tiny political power, tiny stability, tiny war support, small generic stockpiles, or slight production nudges do not count as meaningful design by themselves.

A decision or mission reward should usually do at least one meaningful thing:

- change what the player chooses next
- open or upgrade a decision family, mission family, formable step, advisor path, unit path, special mechanic, or route action
- move a visible value by enough that the player cares, such as legitimacy, authority, cohesion, readiness, corruption, recognition, panic, threat, local support, or sponsor pressure
- change the map, production, logistics, diplomacy, army behavior, intelligence behavior, or internal politics in a visible way
- create a real tradeoff, risk, deadline, escalation, partial success, or failure state
- transform an existing idea, national spirit, or mechanic stage into a stronger or weaker form
- connect to later events, focus routes, super-events, or country identity changes

Tiny modifiers are allowed only when they belong to a visible stacking system, frequent tick, temporary crisis push, dynamic scaling formula, or larger effect package. They should never be the whole reward for an important decision, mission, GUI button, formable step, route unlock, or crisis response.

If a decision family has many small rewards, combine them into fewer stronger actions, convert them into staged idea upgrades, make them change a visible mechanic value. Do not scatter small bonuses across a category to create the appearance of progress.

Starting penalties and negative mission outcomes must also matter. A failed objective, broken authority value, bad crisis decision, or starting debuff should create pressure the player must answer. Harmless negative modifiers that can be ignored are not valid crisis design.

Scripted GUI presentation cannot compensate for weak gameplay. Do not use glowing buttons, animated seals, long tooltips, or dramatic localisation to make a tiny effect look important. If the action is important enough to receive custom presentation, its gameplay effect must be important too.

## 5. Cost and sacrifice design

Political power and command power are allowed, but they should not be the default answer.

Use varied costs that fit the action:

- army XP
- navy XP
- air XP
- command power (can't be expensive, command power costs must be conservative. A decision can't cost more than 60 command power)
- political power only when the action is genuinely bureaucratic or political
- infantry equipment
- support equipment
- artillery
- trucks
- trains
- convoys
- aircraft
- ships
- tanks
- fuel (don't use conservative values)
- manpower
- stability
- war support
- local support
- legitimacy
- faction cohesion
- foreign influence debt
- intelligence exposure
- supply strain
- temporarily tied-down divisions
- civilian factory burden
- military factory output loss
- dockyard commitment
- construction capacity
- rail access
- depot control
- port control
- route access
- deadlines
- map objectives

A military crackdown may use command power, but it should also strain units, consume equipment, risk stability, or affect local resistance when appropriate.

A foreign aid decision may use political power, but it should also require relations, convoys, equipment, route access, consumer goods burden, intelligence exposure, or patronage risk.

A mobilisation decision may require manpower, equipment, training time, supply, local support, or unit placement.

## 6. Cost localisation

Cost localisation should be short, readable, and icon-first.

Do not prefix every blocked cost line with words like `Requires` or `Needed`. In most cases, show only the value and the matching text icon.

Good examples:

- `2,000 <infantry_equipment_texticon>`
- `20 <army_xp_texticon> 20 <command_power_texticon>`
- `200 <support_equipment_texticon>`
- `Depot control`

Do not add filler words between costs.

Use:

`20 <army_xp_texticon> 20 <command_power_texticon>`

Do not use:

`20 <army_xp_texticon> and 20 <command_power_texticon>`

If the country does not meet a requirement, show the missing or unmet cost in red. If the country meets the requirement, show it normally.

If a decision has more than three or four simultaneous costs or requirements, do not show all of them inline. Use a short scripted localisation summary:

- met: `Requirements met`
- not met: `§RRequirements not met§!`

Then put the full requirement list in a tooltip. The tooltip should still use short icon-first entries. Missing requirements should be red, while satisfied requirements should display normally.

## 7. Trigger and requirement clarity

Long triggers should not be exposed raw to the player.

Use:

- scripted triggers
- custom trigger tooltips
- scripted localisation
- named regions
- short requirement summaries with detailed tooltips

Avoid showing huge trigger blocks inside the UI.

Any requirement involving places must name the places or a clear named region.

Bad:

- `required states`
- `border states`
- `some divisions`
- `sufficient troops`
- `enough equipment`

Good:

- `Place 8 supplied divisions in Smolensk, Gomel, and Bryansk.`
- `Hold Kyiv and Minsk for 120 days.`

If the list is dynamic, scripted localisation must print the current targets or explain the named region.

Every named region should have a tooltip or documentation entry explaining which states belong to it.

## 8. Mission quality

Do not create passive checklist missions that the player already satisfies.

Bad missions:

- have 20,000 manpower
- have 500 rifles
- have stability above 35 percent
- have war support above 35 percent
- own a small generic stockpile
- wait until a passive condition is true
- pay political power to reduce a meter

Good missions:

- hold named capitals for a deadline
- place supplied divisions in named states
- secure named rail hubs
- guard named depots
- keep a capital connected to supply
- send equipment through an aid decision
- open or close a named corridor
- build influence over a target country
- protect a border line with actual units
- complete a local support chain before a deadline
- prevent a rival influence threshold
- rebuild a named railway or supply line
- keep a port open while a convoy mission runs

Even easy missions should require real action. Easy should mean lower risk or shorter scope, not passive.

## 9. Mission duration

Timed missions need enough time for the player and AI to act.

Use varied durations based on mission difficulty.

Recommended bands:

- easy missions: at least 90 days, often 90, 95, 100, 105, or 110 days
- medium missions: usually 120 to 180 days
- hard missions: half a year or a full year when the objective is large

Emergency missions can be shorter only when the event story clearly justifies immediate danger.

Do not give every mission the same timer.

## 10. Success, failure, and partial success

Success and failure must use distinct effect logic.

A successful stabilising mission should lower or stabilise the relevant pressure. It should not raise the main threat by accident.

Failure should create consequences, such as:

- higher threat
- lower authority
- higher enemy confidence
- higher foreign penetration
- depot vulnerability
- local unrest
- new report event
- harder follow-up mission
- AI strategy change

Partial success is useful when a mission has mixed outcomes.

Example:

- rail hub secured, but local support lost
- capital held, but foreign recognition spread
- depot guarded, but old movement pressure rose
- border reinforced, but another front weakened

A heavy-handed success may lower one pressure while raising another. The tooltip must explain the tradeoff.

## 11. Objective capacity

Do not overload a decision category with too many active missions.

When a system has many possible missions, use:

- hidden queued missions
- active mission cap
- priority scoring
- regional mission families
- phased unlocks
- mission pools

Only show the most relevant active missions. A player should not see a wall of similar objectives.

If the spec defines a cap, respect it.

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

## 13. Influence, aid, and intervention decisions

Foreign intervention should be action-based, not passive stockpile checking.

Good influence decisions include:

- recognise a provisional authority
- fund civilian construction
- fund military construction
- send equipment convoy
- transfer volunteer formation
- send officer cadres
- open intelligence liaison office
- sponsor press and radio network
- secure aid corridor
- build conference support
- expose rival patronage
- buy out a foreign contract
- offer better guarantees
- demand anti-puppet clauses

Influence should be tracked per sponsor and per target where relevant.

Useful influence categories:

- recognition
- arms
- volunteers
- industrial investment
- intelligence
- ideology
- logistics
- patronage risk

If one sponsor dominates, puppet pressure or dependency risk should rise. If several sponsors balance each other, the target should gain more independence resilience.

## 14. Stackable ideas from missions

Some missions should improve existing ideas rather than create new ones.

Stackable mission ideas can represent:

- recognition
- foreign reconstruction
- volunteer cadres
- adviser missions
- arms pipelines
- local defense committees
- depot security
- rail authority
- public legitimacy

A base idea can be weak at first and mature through mission success.

Example recognition progression:

1. Unrecognized Authority
2. Observed Provisional Authority
3. De Facto Recognized Republic
4. Treaty-Backed Republic
5. Internationally Entrenched Republic

Do not create a separate idea for every mission if the same institution is clearly growing.


## 15. Focus and decision integration

Focuses and decisions should be designed together.

A decision system should not feel detached from the focus tree. Focuses should unlock new decision families, expand existing mechanics, change decision costs, alter mission success conditions, add new targets, or open new diplomatic, military, industry, or expansion choices.

Common patterns:

- expansion focuses unlock declarations, ultimatums, league votes, protectorate demands, border settlement decisions, war-preparation missions, and postwar integration decisions
- industry focuses unlock factory construction, rail repair, supply hub expansion, airbase construction, anti-air construction, fortification, resource extraction, and infrastructure programs
- military focuses unlock reserve mobilisation, special unit training, template conversion, border defense missions, depot seizure missions, commander recruitment, and offensive preparation
- diplomacy focuses unlock recognition missions, aid corridors, advisor missions, volunteer transfers, anti-puppet clauses, sponsor-balancing decisions, and foreign investment decisions
- political focuses unlock elections, councils, purges, compromises, advisor appointments, party campaigns, reform missions, leader changes, and ideology decisions
- faction or league focuses unlock shared reserve decisions, member votes, joint declarations, common fronts, intervention forces, and arbitration missions

When a focus unlocks decisions, document:

- focus id or route
- decision category or family unlocked
- new decision targets
- costs and requirements
- AI behavior
- success and failure effects
- follow-up events or missions
- cleanup rules

When a decision family is route-locked, localisation should explain which political, expansion, industry, military, diplomacy, or league route enabled it.

Industry decision families should generally do real map work, such as building or repairing factories, railways, forts, anti-air, airbases, infrastructure, supply hubs, ports, or resources.

Expansion decision families should generally create real strategic options, such as claims, cores, war goals, protectorates, leagues, declarations, border incidents, treaties, ultimatums, or postwar settlement choices.


## 15.1 Progressive decision categories

Decision categories should evolve as the focus tree develops.

A decision category should not remain a static list of buttons after a country changes ideology, builds an industry route, joins a league, chooses an expansion path, or accepts foreign influence.

Focus progress can change decision systems by:

- unlocking new decision families
- adding new targets
- reducing or changing costs
- adding new risks
- changing success or failure effects
- unlocking stronger versions of earlier decisions
- adding mission variants
- changing AI priorities
- changing localisation
- closing decisions that no longer fit the route

Examples:

- an industry route starts with small repair decisions, then unlocks factory projects, rail expansion, supply hub construction, anti-air construction, airbase construction, and resource extraction
- an expansion route starts with border incidents, then unlocks guarantees, ultimata, claims, cores, protectorates, local leagues, war goals, and settlement decisions
- a military route starts with emergency units, then unlocks templates, training missions, offensive planning, border defense, and special force recruitment
- a political route starts with legitimacy decisions, then unlocks party campaigns, advisor appointments, leader changes, purges, elections, councils, laws, and cosmetic identity changes
- a diplomacy route starts with observers, then unlocks recognition, aid corridors, volunteer transfers, anti-puppet clauses, sponsor rivalry, and treaty decisions

If a focus branch says it changes the country, the decision layer should reflect that change.


## 15.2 Route-aware decision depth

A decision family unlocked by a focus path must have enough content to matter.

A route-unlocked decision family should usually include:

- several decisions or missions, not only one button
- route-specific costs
- route-specific risks
- route-specific AI behavior
- route-specific localisation
- visible consequences
- cleanup when the route, war, target, or crisis ends

Expansion decision families should include postwar handling when they create conflict. War goals, declarations, ultimatums, and border incidents should connect to occupation, integration, protectorate, puppet, resistance, league, faction, or settlement decisions.

Industry decision families should be geographically grounded where possible. Construction, rail, supply, anti-air, fort, airbase, dockyard, port, and resource decisions should name states or regions, and they should change the map or production system.

Political decision families should interact with leaders, advisors, parties, laws, ideology, legitimacy, councils, internal factions, cosmetic names, or flags when the focus route changes politics.

Advisor, leader, and council decisions should match the route that unlocked them. Do not unlock generic advisors unrelated to the route identity.

Decision families can include achievement tracking when they support difficult route completions, rare combinations, expansion victories, internal reform, or survival under high-chaos conditions.


## 15.3 Decision pacing, tradeoffs, and visible effects

Decision categories unlocked by focuses should progress over time.

- Early decisions should be limited, urgent, and tied to survival or first institutions.
- Middle decisions should add stronger tools, new targets, route mechanics, influence actions, military actions, and construction options.
- Late decisions should support route payoffs, expansion, integration, faction leadership, League leadership, postwar settlement, or high-chaos end states.

Decision families should have tradeoffs. A powerful decision should cost or risk something that fits the action: equipment, manpower, stability, war support, consumer goods burden, foreign dependency, legitimacy, faction cohesion, unit commitment, fuel, convoys, or crisis pressure.

Do not overuse mutually exclusive decision paths. Use them when the choices represent incompatible policy, route identity, foreign alignment, or institutional structure. Support actions should usually coexist unless the design says otherwise.

Important decision families should define failure states. Failed reforms, failed influence balancing, failed expansion, failed military centralisation, failed construction, or failed diplomacy should create visible follow-up problems where the mechanic supports it.

Decision localisation should describe the visible baseline effect of the decision. Do not reveal hidden outcomes, secret variables, hidden follow-up events, or future surprise branches. The player should understand the public action and likely visible direction without being spoiled.


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

When a mechanic uses a scripted GUI, consider whether it needs visual state changes. Useful presentation can include progress bars, meter fill variants, status icons, warning frames, selected and locked frames, animated frames, or frame-by-frame changes. Use visual motion or variants only when they clarify the mechanic.

Do not treat dynamic text as presentation by itself. A changing number needs a labelled role, visual identity, threshold context, and visible consequence. A large collection of plain numbers is a design defect even when every number is technically dynamic.

Special mechanics can hide future surprises, but should not hide basic cause and effect. If a visible value rises or falls, the player should understand the public reason, the consequence, and the broad response available. Explain this through concise labels and tooltips instead of large text blocks.

Faction, league, bloc, or coalition goals need rewards and failure states. A successful faction goal can unlock shared decisions, war goals, legitimacy, cohesion, member rewards, postwar settlements, or new faction leadership. A failed goal can reduce cohesion, trigger member exits, invite foreign pressure, start leadership contests, weaken shared defenses, or open emergency missions.

AI strategy must respect route and decision validity. AI should not take decisions that require missing states, dead sponsors, non-existent factions, unavailable ideologies, disabled evolutions, impossible borders, absent enemies, invalid targets, or closed routes. Invalid actions should be hidden, bypassed, or weighted to zero.

Decision systems for shared trees or shared mechanics must still feel country-specific. Use scripted localisation, country-specific targets, country-specific AI weights, local leaders, regional decisions, and route-specific rewards to prevent every country from playing the same.

Important thresholds, caps, gains, losses, duration bands, AI weights, and scaling values should be centralized in script constants or a documented tuning file. Do not scatter magic numbers across decision files, events, focuses, scripted effects, and scripted triggers.


## 15.6 Reward dumps and exploit checks

Avoid one-time reward dumps as the main decision or mission design. A decision or mission can give units, equipment, factories, buildings, resources, or influence, but important decisions should usually connect to a repeatable system, timed objective family, mechanic value, advisor path, route branch, or long-term gameplay loop.

A large decision system should not become a sequence of buttons that only give free rewards.

A large decision system should also not become a sequence of tiny fairy-dusted rewards. Repeated minor modifiers, token stockpiles, small stability changes, and tiny production nudges are not better than reward dumps when they do not change play. Treat low-impact reward dust as a design failure unless it is part of a visible cumulative system with clear thresholds and consequences.

Balance review must include exploit checks and impact checks. The question is not only whether the decision can be abused. The question is also whether a reasonable player would notice the reward, care about the failure, and plan around the system.

Check for:

- repeatable rewards without meaningful cost
- free unit loops
- cheap factory construction loops
- equipment farming
- influence farming
- puppet abuse
- war-goal spam
- claim or core spam
- advisor discount stacking
- bypass abuse
- repeated mission success farming
- decisions that can be clicked without real risk
- AI taking decisions that create broken loops

Fix exploits with route locks, flags, cooldowns, dynamic costs, limited targets, escalating costs, one-time completion flags, scripted triggers, AI limits, or cleanup effects.


## 15.7 Decision category clutter control

Large decision systems should not show every possible decision at once.

Use phases, caps, priorities, regional pools, route locks, mechanic thresholds, or crisis-state filters so the player sees decisions that matter in the current situation.

A decision category should feel curated by current state, not like a debug menu. Treat visible decision count as a design budget. A phase should normally expose three to six primary decisions, with only a small number of active missions that the player can assess quickly. If more actions are needed, split them by phase, target, region, route, or category instead of adding another long visible list.

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

## Decision category presentation hierarchy

A complex scripted GUI is not the default presentation for a decision category. Choose the least complex surface that communicates the category's current state, purpose, and available actions clearly.

Use this order:

1. ordinary category icon with concise category text
2. static category picture
3. animated category picture with a static fallback
4. compact attached display or category header
5. full scripted GUI or separate mechanic window

Do not move to a more complex layer only because the category is important. A static or animated category picture is often stronger for a category that needs identity and atmosphere but does not require the player to manage several live values or targets.

Category pictures are especially suitable for propaganda and public campaigns; civil-war preparation, insurgency, and preparedness; ideology, elections, monarchism, party control, and trade-union politics; faction management, diplomatic blocs, treaties, and intervention campaigns; formables where a territorial overview is useful but individual state pieces do not need interaction; and one-theme crisis categories whose decisions already explain the actionable details.

A category picture must remain presentation. Do not draw fake buttons, meters, values, or controls into it. Use a full scripted GUI only when the player must manage a living system that cannot be read cleanly from ordinary decisions, category text, tooltips, and a category picture, such as several interacting values, target selection, repeated map interaction, competing factions, a state-by-state formable display, or a persistent board whose state changes often.

### Decision category picture reference workflow

Before designing or auditing a category picture, inspect:

`.agents/skills/hoi4-feature-assets/assets/vanilla_reference/icons/decision_categories/pictures/`

This is the canonical larger-picture reference family and is separate from `icons/decision_categories/`, which contains small category icons. The folder must contain a labeled `contact_sheet.png`. If the sheet is missing, create it from the references, label every filename and native dimension, and update the reference `README.md` and `CATALOG.md` with provenance and surface ownership. Reference images and the contact sheet are review material only and must never be wired into runtime GFX.

When reviewing an existing mod, record category id, owner system, current presentation, recommended layer, the picture-or-GUI reason, and any missing asset or implementation. Do not add a picture to every category. Keep ordinary categories ordinary when a picture would add no useful identity, territorial context, or state feedback.

## Formable nation decisions

Use decisions for formable nations when the player should prove control over land, complete a political route, or spend resources before changing the country identity. A formable decision should feel like a proclamation, settlement, congress, coronation, constitutional act, annexation settlement, liberation charter, or administrative project. It should not be only a hidden tag switch.

A formable decision must define:

- visible name and hidden debug name
- decision category and visibility timing
- required owned and controlled states
- required subjects, allies, faction members, puppets, occupied territories, cores, claims, or compliance thresholds
- required focus, event flag, route flag, ideology, leader, legitimacy, chaos tier, or hidden reveal state
- whether the decision is visible before requirements are met, hidden until unlocked, or fully secret until an event reveals it
- political, military, economic, legitimacy, stability, war support, command power, XP, equipment, fuel, convoy, train, manpower, or factory costs
- what happens to the tag, cosmetic tag, country name, adjective, flag, leader, portrait, ruling party, advisors, national spirits, cores, claims, puppets, factions, wars, and guarantees
- whether claims become cores instantly, gradually through decisions, or only after compliance and local support work
- follow-up missions, border integration projects, legitimacy projects, resistance suppression, diplomatic reactions, and achievement hooks
- AI willingness, AI blockers, AI timing, and AI target safety
- cleanup for obsolete formation decisions after the formable is created

State requirements must be readable. Use named state groups and custom trigger tooltips. Do not expose raw state id lists to the player unless the existing UI pattern already does that cleanly. If several alternate maps can qualify, create clear requirement groups.

### Formable state-puzzle presentation standard

When exact territorial control is the central proof for a formable, use the reusable formable state-puzzle presentation. Show the required territory assembled from the exact in-game shapes of its states, arranged in their real geographic positions like pieces of one map.

Each required state must be represented separately. A state that does not satisfy the requirement is grey; a qualifying state is green; borders, texture, labels, or another non-colour cue must distinguish the states; hovering a piece names the state and explains its status; and the panel shows the qualifying count, required count, and final eligibility without exposing raw internal variables.

Derive every piece from the installed map data. Do not approximate outlines by hand, generate them with ImageGen, replace them with generic tiles, or use province blobs that differ from the actual requirement. Every piece must share one projection, scale, origin, and border treatment.

The display must refresh from current ownership, control, subject or ally counting, alternate state-set rules, route locks, and eligibility. Do not cache a green state after it stops qualifying, and do not add a whole-world daily scan unless the user explicitly authorizes it. Use the same scripted eligibility helpers for the pieces, summary, and formation decision so the GUI and decision can never disagree.

Keep the display compact. Do not add unrelated meters, fake controls, or lore panels around the map. The human-facing puzzle must not become an AI dependency; AI uses the same formation conditions and decision logic directly.

Copy and adapt the reusable scaffolding from:

`.agents/skills/hoi4-decisions-missions/templates/formable_state_puzzle/`

The package contains manifest, `.gui`, `.gfx`, scripted GUI, scripted trigger/effect, localisation, static-picture, and validation templates. Skill-local templates are reference scaffolding and must never be wired directly into a mod.

Hidden formables need extra care. A hidden formable can be locked behind an event, secret focus, rare ideology, high chaos, special leader, historical artifact, super-event, achievement route, or scripted GUI investigation. Hidden does not mean undocumented. The implementation handoff must still define all triggers, effects, assets, and cleanup.

## Formation missions and integration projects

Large formables should usually need post-formation work. Use missions or decision chains for integration when instant cores would be too strong.

Good formation follow-ups include:

- hold named capitals for 180 days
- secure rail links between old and new capitals
- integrate border districts through local support work
- spend infantry equipment and support equipment to build local administrations
- negotiate autonomy with subject members
- reduce resistance before coring a newly claimed area
- hold a plebiscite under observer conditions
- build a capital road, port, or rail hub before moving the capital
- keep stability and legitimacy above a threshold during the formation crisis
- prevent rivals from reaching an influence threshold before the final proclamation

Formation systems should support partial success and failure. A country can form the title but gain only claims, delay core grants, create dissatisfied regions, trigger rival reactions, or open emergency missions.

## Scripted GUI decision categories and mechanic windows

Choose the presentation layer from the hierarchy above before creating a custom window. A major mechanic does not automatically need a full scripted GUI. Use an ordinary category with a strong static or animated picture when the player mainly needs theme, territorial context, or a clear visual identity. A scripted GUI is appropriate when the player must manage values, targets, meters, factions, sponsors, province groups, exact interactive formable requirements, investment tracks, or competing internal blocs.

Use `hoi4.gui_inspect` to map linked layout, states, resolutions, click regions, localisation, sprites, fonts, animation, and background ownership. Then call `hoi4.gui_render` for deterministic full-window, cropped, annotated, state, resolution, click-region, hierarchy, and comparison views. MCP diagnostics expose bad alignment, uneven spacing, overlapping controls, clipping, overflow, broken click regions, state mismatches, resolution drift, missing assets, and other layout defects. Full-window and comparison renders also make poor use of the background visible, but the implementation agent must still review whether every painted region and visual anchor is being used as intended. Use `hoi4.gui_rewrite` for an in-scope GUI change after reviewing those diagnostics and the render fidelity report. Keep gameplay validation and balance review in this skill.

When a named event or event-owned mechanic specifically introduces its own scripted GUI, route the bounded layout implementation or visual-quality pass to `hoi4_event_ui_worker`. That worker must apply every rule in this section and return mandatory MCP before-and-after evidence. The decision owner retains costs, effects, availability, AI equivalents, cleanup, and balance. Do not route repository-wide interfaces, event logs, event-detail frameworks, settings, shared windows, or an unrelated existing GUI to the event UI worker merely because an event opens or references it.

A scripted GUI or custom window must have a gameplay reason. It should expose useful choices and state clearly. It must not exist only to make a small mechanic look larger.

### GUI action integrity

Every button-shaped element must be one of these:

- a real interactive control with a meaningful action
- a clearly disabled control with a visible reason
- a decorative element that cannot reasonably be mistaken for a button

Do not use fake buttons, decorative frames styled like buttons, empty click boxes, dead controls, or button art with no gameplay action. Do not place a click region outside the visible button or make the click region smaller than the visual control. Informational content should use labels, status panels, icons, meters, or tooltips instead of fake controls.

Every real button needs:

- a clear label or icon
- an accurate click region
- hover, available, selected, active, completed, warning, and disabled states when relevant
- a visible cost and requirement summary
- a tooltip that explains the action and blocked reason
- a scripted effect or decision action
- an AI equivalent when AI countries can use the system
- cleanup when the action, target, route, or mechanic becomes invalid

Do not add buttons to fill empty space or manufacture the appearance of depth. Merge actions that do the same job, and remove controls whose result does not change play.

### Text and explanation budget

The main panel should use short labels, concise state summaries, and current actions. Do not cover the window with paragraphs, repeated descriptions, raw triggers, long instructions, or text that restates the same mechanic in several places.

A mechanic still needs to be explained. Every non-obvious value, state, threshold, target, and action must have a short visible label and a concise tooltip or help surface that explains:

- what it represents
- what raises or lowers it
- which thresholds matter
- what it unlocks, blocks, improves, or worsens
- what the player can do about it

Keep the explanation close to the value or control it describes. Do not hide basic cause and effect in documentation outside the game. Do not use long prose to compensate for unclear layout or weak mechanics.

### Visible value budget

A scripted GUI should normally expose one primary mechanic value and no more than three supporting values at the same time. More visible values require a clear reason and distinct player actions. Internal variables may be numerous, but the player-facing interface should summarize, combine, or hide values that do not need direct management.

Reject value bloat. Merge values that measure the same pressure, remove values that do not change decisions, and avoid parallel meters whose effects are difficult to distinguish.

Do not display plain dynamic numbers with no visual or gameplay significance. Every visible value needs:

- a stable name
- a clear unit, range, or direction
- a consistent colour identity
- a second non-colour cue such as an icon, frame, label, or meter shape
- meaningful thresholds or states
- visible consequences
- at least one player action that can affect it when the mechanic allows intervention

Colour alone is not enough, and an uncoloured number alone is not enough. The player should understand why the value matters without reading implementation notes.

### Decision and action budget

A scripted GUI must not become a wall of decisions. A single phase or state should normally show three to six primary actions, plus only the active missions or target controls that matter at that moment. Use phases, target selection, tabs, replacement, priorities, or conditional visibility when the full system contains more actions.

Do not show every possible decision, target, mission, and upgrade at once. Obsolete, invalid, duplicate, low-impact, and route-incompatible actions must be hidden or removed. A system that needs dozens of simultaneous buttons should be redesigned before more layout work is added.

### Background-first layout

An ImageGen-created scripted GUI background is part of the interface design. Treat it as a functional layout blueprint, not as wallpaper behind unrelated text.

Before placing controls, map the background into intended content regions. Record every prominent panel, inset, slot, frame, medallion, divider, illustration, empty field, and decorative anchor that affects placement. Each intentional functional region should have a matching GUI use, or the background should be revised.

Use the whole background deliberately. This means using its intended panels and visual anchors while preserving intentional negative space. It does not mean filling every pixel.

Do not:

- ignore a painted panel and place unrelated text beside it
- write text across ornaments, illustrations, borders, handles, seals, diagrams, or other visual elements
- cover a prominent background feature with a generic text box
- place controls between the designed slots only because the coordinates are easier
- leave half of the functional background unused while another area is crowded
- force content onto a background whose composition does not support the mechanic

Text, values, icons, meters, cards, and buttons should align with the painted frames and content zones that were created for them. If the required content does not fit those regions, revise or regenerate the background. Do not ignore the art and layer a generic interface over it.

The implementation handoff should include a background coverage map:

| Background region | Intended content | GUI elements | Interaction or state | Status |
| --- | --- | --- | --- | --- |

Use full-window renders at every supported resolution and compare them with the source background. Review the normal, selected, disabled, warning, and crowded states. Confirm that text stays inside intended regions, click boxes match visible controls, no element overlaps important artwork, and no designed functional region is accidentally abandoned.

### Interactive design contract

Interactive GUI design should define:

- entry point from the decision category
- background coverage map and layout regions
- primary value and supporting value hierarchy
- visible decision and mission budget by phase
- visible tabs, panels, cards, meters, bars, or target lists
- button costs and requirements
- what each button changes
- locked, available, selected, active, completed, warning, and disabled states
- hover and tooltip text
- scripted localisation for dynamic values
- scripted effects for button outcomes
- scripted triggers for button availability
- AI equivalents for every meaningful button
- cleanup and fallback behavior

When buttons spend resources, show the cost clearly. Use icon-first cost localisation. If the GUI button has more than a few requirements, show a short requirement summary and put details in a tooltip.

Do not use GUI buttons to bypass decision balance. GUI buttons should call the same scripted effect families, cost logic, validation triggers, logging, and cleanup that the normal decision system would use.

## Animated decision category presentation

Decision categories and mechanic windows can use animated sprites when motion improves readability or atmosphere. Suitable uses include:

- soft glow around an available formation seal
- warning pulse when pressure is near a threshold
- slow float on an occult, diplomatic, or propaganda emblem
- particle drift behind a high-chaos category header
- meter shimmer when a value changes
- selected-card glow for the active sponsor, faction, or route
- animated border for crisis mode
- animated leader or council portrait inside a special mechanic window

Use static fallback sprites for every animated element. Keep animations subtle unless the route is deliberately supernatural or high-chaos. Do not animate every icon in a category. Too much movement makes the UI harder to read.

The decision implementation handoff should list animated sprite names, static fallback names, target sizes, frame counts if known, loop behavior, file paths, source mode, and whether the animation is purely decorative or tied to a mechanic state.

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

For complex decision or mission weights, route the analysis through `hoi4_ai_probability_auditor`. Establish named baseline campaign scenarios before any patch with `hoi4.probability_inspect`, `hoi4.probability_evaluate`, and `hoi4.probability_sweep` as appropriate. The gameplay owner chooses targets and applies the patch; the auditor remains read-only. After the source change, require `hoi4.probability_compare` against the same named scenarios so the before-and-after evidence is directly comparable. Use `hoi4.probability_simulate` only for explicitly declared uncertain inputs, and use `hoi4.probability_render` when the ranking, matrix, sensitivity, comparison, or unresolved view improves review. Decision and mission `ai_will_do` results are willingness scores, so do not present them as click probabilities. Include availability, target, cost, cooldown, and route state where relevant, and retain unresolved engine state in the result. If the probability route is unavailable, record the exact blocker and do not substitute source-only analysis.

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

Document test scenarios or observations. Do not only say “balanced.”

## Improvement addenda for decisions and mechanic windows

When an improvement addendum proposes decision depth, scripted GUI, or mechanic windows, translate the design into active play. The decision category should show the mechanic clearly, but the gameplay should still live in decisions, missions, scripted effects, scripted triggers, AI rules, and cleanup logic.

Use scripted GUI when the player needs to read or manage values that would otherwise be buried in tooltips. Good uses include influence boards, federation congresses, formable progress, patron leverage, resource routing, public fear, occult pressure, faction cohesion, reform votes, target cards, and timed crisis panels.

The addendum must define the information budget before asking for more art or controls. Name the primary value, supporting values, visible action count, active mission cap, explanation surfaces, and the content assigned to each background region. Do not respond to a shallow mechanic by adding more meters, more decisions, more text, or more decorative buttons.

A GUI button should be treated like a decision. It needs cost logic, requirement logic, tooltips, scripted effects, AI equivalents, state cleanup, and a visible result. Fake buttons are forbidden. Animated buttons, glowing meters, floating seals, and warning pulses should clarify state changes. Do not use animation to hide the cost or make a weak action look important.

When the background is generated for a specific layout, the addendum should identify the intended panels, slots, anchors, and content regions. The implementation must fit controls to those regions or revise the background. It must not cover the artwork with generic text and controls.

For formables, the decision should verify the map state. Focuses may reveal claims, prepare institutions, or reduce costs, but the formation decision should prove control, legitimacy, recognition, or integration when those are central to the idea.

## Subagent patches for decision systems

Decision and mission subagents are active small-patch agents by default inside the current task scope. They can patch varied costs, clearer dynamic localisation, custom trigger tooltips, AI target checks, cleanup hooks, visibility checks, cooldown fixes, scripted GUI button text, narrow helper call sites, and existing formable requirement fixes without waiting for a separate permission prompt.

They should not expand a whole decision system, create a new mechanic window, add a new event chain, or invent a formable suite. When the gap is broad, they should write an improvement plan under `docs/plans/<event_id>_<event_slug>_plans/` and leave implementation to the main agent.

Every patch must write a handoff with changed files, changed decision or mission ids, localisation keys, behavior before and after, meaningful validation, skipped task-specific validation, and remaining design risks.

## 20. Completion report

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
- scripted GUI mechanics use progress meters, variants, frames, or frame animations when useful
- scripted GUI layouts were inspected and rendered with full-window, state, resolution, click-region, hierarchy, and comparison views where relevant
- every button-shaped element is a real control, a clearly explained disabled control, or unmistakably decorative
- no fake buttons, dead click boxes, misleading controls, or click regions that disagree with visible button bounds remain
- main-panel text is concise and does not cover the interface with repeated explanations, raw triggers, or long paragraphs
- every non-obvious mechanic, value, threshold, and action has a concise in-game explanation
- each scripted GUI has a clear primary value and a limited set of supporting values
- plain dynamic numbers without colour, labels, threshold context, consequences, or visual significance are not used as mechanic presentation
- visible values use consistent colour identities plus non-colour cues
- visible decision and mission counts stay within a readable phase budget, with excess actions phased, filtered, grouped, replaced, or removed
- ImageGen-created backgrounds are treated as functional layouts, with intended panels, slots, frames, and anchors mapped to actual GUI elements
- text and controls align with the background's designed regions and do not cover or ignore prominent artwork
- background coverage is documented and full-window renders confirm that functional regions are used deliberately
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
