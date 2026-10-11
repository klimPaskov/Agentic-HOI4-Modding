# Formable nation decisions

This reference belongs to the `hoi4-decisions-missions` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

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

Each required state must be represented separately. A state that does not satisfy the requirement is grey; a qualifying state is green; borders, texture, labels, or another non-colour cue must distinguish the states; hovering a piece names the state and explains its status; and the panel shows the qualifying count, required count, and final eligibility without exposing raw internal variables. When a formable family spans shared or phase-specific decision categories, enumerate every in-scope category in `templates/formable_state_puzzle/category_attachment_audit.md` and record the exact generated `scripted_gui` identifier attached to each category. A valid state-piece render never proves category coverage by itself.

Derive every piece from the installed map data. Do not approximate outlines by hand, generate them with the image generator, replace them with generic tiles, or use province blobs that differ from the actual requirement. Every piece must share one projection, scale, origin, and border treatment.

The display must refresh from current ownership, control, subject or ally counting, alternate state-set rules, route locks, and eligibility. Do not cache a green state after it stops qualifying, and do not add a whole-world daily scan unless the user explicitly authorizes it. Use the same scripted eligibility helpers for the pieces, summary, and formation decision so the GUI and decision can never disagree.

Keep the display compact. Do not add unrelated meters, fake controls, or lore panels around the map. The human-facing puzzle must not become an AI dependency; AI uses the same formation conditions and decision logic directly.

Copy and adapt the reusable scaffolding from:

`.claude/skills/hoi4-decisions-missions/templates/formable_state_puzzle/`

If the repository provides a canonical installed-map state registry and consumer compiler, treat that registry as immutable build input and record its map revision, content hash, ordered map roots, consumer manifest, generated runtime outputs, and provenance checks. If those tools are not available in the current repository, do not invent them: document the exact gap and keep the state puzzle blocked until exact geometry can be reproduced and validated.

The package contains manifest, `.gui`, `.gfx`, scripted GUI, scripted trigger/effect, localisation, static-picture, category-attachment audit, and validation templates. Skill-local templates are reference scaffolding and must never be wired directly into a mod.

Hidden formables need extra care. A hidden formable can be locked behind an event, secret focus, rare ideology, high chaos, special leader, historical artifact, super-event, achievement route, or scripted GUI investigation. Hidden does not mean undocumented. The implementation handoff must still define all triggers, effects, assets, and cleanup.
