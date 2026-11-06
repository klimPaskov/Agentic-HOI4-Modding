# HOI4 Focus Trees: Formable routes and addenda

Part of the [hoi4-focus-trees](../SKILL.md) skill. Read before a focus tree prepares, reveals or completes a formable nation, uses animated leader portraits, or is deepened by an addendum.

## Focus routes that lead to formable nations

A focus tree can prepare, reveal, enable, or stabilize a formable nation, but the final formation should usually be handled by a decision when state control matters. Use focuses to build the political claim. Use decisions to verify the map and perform the formation.

A formation route in a focus tree should define:

- narrative reason the country can claim the formable identity
- route family that unlocks the claim
- focuses that reveal the formation decision
- focuses that mark required regions, start border commissions, invite subjects, sponsor plebiscites, or prepare integration
- mutually exclusive formable routes
- compatible support branches, such as industry, army, diplomacy, intelligence, or legitimacy
- hidden formables that require rare events, special leaders, secret focuses, high chaos, or unusual state control
- post-formation focuses that stabilize the new country, integrate regions, resolve opposition, change capital, update advisors, or expand claims
- AI route behavior and AI safety checks
- asset needs, including flags, cosmetic tags, leader portraits, focus icons, decision icons, and possible animated route portraits

Do not make a formable route a linear claim ladder by default. The best formation routes usually combine legitimacy, state control, diplomatic recognition, military readiness, local integration, and a visible identity change.

## Formation route architecture

When mapping a focus tree that can form countries, include a formation lane or route overlay in the architecture map.

Useful formation lane structure:

1. claim preparation focus group
2. required-region survey or claim office focus group
3. diplomacy or internal legitimacy focus group
4. decision unlock focus
5. map-control decision handled in a decision category
6. formation event or news event
7. post-formation stabilization branch
8. late ambition or hidden second-stage formable, if justified

The tree should state whether the formable is:

- visible from game start
- revealed by a normal focus
- revealed by a rare event
- hidden until the player controls key states
- hidden behind ideology, leader, chaos tier, patron, or secret route
- available only if another country does not exist
- available only if the forming country has the correct release origin or event origin

For shared event-created trees, formables must use origin and package checks so unrelated countries do not receive the wrong route.

## Focus rewards tied to formation decisions

Focus rewards can:

- unlock formation decisions
- add claims on required regions
- reduce integration costs
- add temporary legitimacy for a formation crisis
- reveal hidden state requirements in a tooltip
- invite subjects or allies to join the formation
- open border plebiscite missions
- create a custom scripted GUI meter for formation progress
- unlock post-formation branch content
- switch to animated leader portraits or route emblems after a dramatic transformation

Focus rewards should not:

- grant all required states without gameplay reason
- create a formable without checking map requirements
- give instant full cores on large conquered regions without integration work
- bypass route locks or hidden formable conditions
- leave obsolete pre-formation focuses visible after the formation completes

## Animated leader portraits and visual route payoffs

Focus trees should consider animated portraits or animated route emblems for major political transformations. Use them for route payoffs such as a supernatural leader reveal, a restored dynasty, a revolutionary cult, a final formable proclamation, or a high-chaos state identity.

Animated portraits need static fallbacks. They should be assigned through the same leader, character, or cosmetic identity logic as the route itself. `hoi4_portrait_creator` owns the sourced or generated base portrait before `hoi4-frame-animation` creates the animation package.

Do not make every leader animated. Animation should signal a special route, a high-chaos identity, a super-event-level transformation, or a rare hidden outcome.

## Improvement addenda and formation routes

When an improvement addendum deepens a focus tree, preserve the route idea before adding nodes. Aim for a sharper country identity, stronger branch interaction, clearer route locks, better rewards, stronger AI, and more visible consequences.

Formation routes should usually combine focus preparation with a decision that verifies state control. Focuses can discover old claims, call a congress, unlock a seal, prepare integration, recruit elites, expose a hidden identity, or open the formation decision. The decision then checks the map and performs the formation.

Hidden formables can be routed through secret focuses, events, leader changes, chaos tiers, ancient artifacts, internal factions, or custom GUI investigation. Hidden content should still have a full implementation handoff. It needs reveal logic, visibility rules, localisation, assets, AI handling, post-formation gameplay, and disqualifiers.

Animated leader portraits and animated route emblems should be reserved for major transformations. Use them when the route payoff changes the country's identity, reveals a high-chaos leader, forms a new state, or completes a dramatic ideological break. Keep a static fallback and ensure the animation has a clear trigger and cleanup state.

