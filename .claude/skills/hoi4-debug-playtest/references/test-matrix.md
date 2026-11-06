# HOI4 Autonomous Debug Playtest: Generic HOI4 test matrix

Part of the [hoi4-debug-playtest](../SKILL.md) skill. Read when choosing which surfaces to test and what to check on each.

## 11. Generic HOI4 test matrix

Select only the surfaces in scope, but do not ignore an adjacent surface that the feature visibly depends on.

### Startup and content loading

- game reaches the main menu
- correct mod is visibly loaded
- new game reaches country selection
- selected country loads into the map
- no new attributable startup error appears
- a dedicated test save can be created and loaded

### Events and news

- event triggers under intended conditions
- event does not trigger under a named invalid condition when eligibility is in scope
- title, description, options, images, sounds, and tooltips appear
- no raw localisation keys appear
- each option produces the visible result it describes
- a save diff taken immediately before and after each option shows its state changes once and nothing unrelated
- follow-up events occur once and in the intended order
- hidden effects do not duplicate visible option effects
- event targets and actors remain correct across follow-ups

### Decisions, missions, and categories

- category visibility and lifecycle are correct
- costs and blocked requirements are readable
- buttons enable and disable at the correct state
- timers advance and resolve
- success, failure, cancellation, and cleanup work
- obsolete decisions disappear
- repeated use does not create free rewards or stale targets
- AI has a valid path when the system is AI-usable

### Focus trees

- correct tree loads for the correct country and origin
- branches are visible, readable, and connected
- prerequisites and mutual exclusions behave as intended
- focus icons and localisation are present
- completion rewards and unlocked content occur once
- route-specific decisions, events, leaders, flags, and ideas appear
- AI does not choose invalid or impossible routes

### Countries and map state

- tag, name, adjective, flag, portrait, leader, parties, capital, cores, claims, ownership, and controller state are coherent
- released or transformed countries receive their intended tree, ideas, units, equipment, and AI
- no country is accidentally deleted or left landless unless that is the intended result
- annexation, release, civil war, transfer, peace, and cleanup produce valid map state

### Localisation and dynamic text

- no raw keys, broken format codes, missing icons, or wrong scope names appear
- dynamic values update after the underlying state changes
- integer values do not show unwanted decimal noise
- hidden content is not spoiled early
- tooltips describe visible requirements and consequences

### GUI and graphics

- windows open, close, move, and return to the correct state
- tabs, lists, scroll areas, sliders, buttons, hover states, and selected states work
- text does not overlap, clip, escape its container, or sit behind another layer
- decorative layers do not intercept clicks
- no pink textures, checkerboards, missing sprites, stretched assets, wrong flags, or wrong portraits appear
- animated sprites loop correctly and have a usable static fallback
- UI remains usable at the current resolution and scale

### Runtime, AI, and pacing

- the feature continues working after time advances
- repeated ticks do not spam events or logs
- AI uses actions only when valid
- cleanup occurs after war, annexation, route change, target death, or feature completion
- no obvious performance stall, runaway loop, or uncontrolled decision spam appears
- `footprint` on the start and end saves of a time pass shows no script state growing without cleanup, and AI outcome tallies from the end save match the intended behaviour

### Save and reload

- the dedicated test save loads
- important variables, flags, event targets, missions, GUI state, and country identity persist correctly
- temporary state that should be cleared does not return after reload
- the console `savecheck` command's `Test_01` and `Test_02` saves show no mod-owned differences in a save diff

