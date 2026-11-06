# HOI4 Focus Trees: Political depth and route locks

Part of the [hoi4-focus-trees](../SKILL.md) skill. Read before designing political branches, leader customization, civil war or internal conflict, mutual exclusions, or gates on external events.

## 7. Political depth

Large focus trees must alter politics directly.

Political branches should include meaningful changes such as:

- ideology shifts
- ruling party changes
- party popularity changes
- leader changes
- new advisors
- advisor cost discounts
- ministers or high command unlocks
- laws
- scripted leader traits
- balance-of-power changes
- internal faction decisions
- coups, compromises, elections, councils, juntas, congresses, regencies, cult offices, syndicates, committees, or directorates
- cosmetic country names
- flag changes
- focus-route names
- ideology-specific party names
- local support or legitimacy mechanics

A country should not remain politically static through a major focus tree unless that is the explicit concept.

Examples of route families:

- socialism
- democratic legalism
- nationalism
- monarchism
- military government
- anarchism
- religious government
- foreign client government
- revolutionary council
- security directorate
- high-chaos cult
- machine or factory state
- death-state actor

Fixed-purpose chaos countries can have narrower political design. For example, a country whose entire identity is death, plague, machine rule, or total destruction may have one ideological purpose. Even then, its tree should still create mechanical choices inside that purpose, such as doctrine, expansion method, internal hierarchy, recruitment, economy, and endgame ambition.


## 7.1 Leader and institution customization

Some routes should let the player build a leader, regency, council, cabinet, doctrine, or governing institution through several choices.

A customization sequence can use events, focuses, decisions, or a dedicated mechanic to select traits and priorities. Useful dimensions include construction, military command, diplomacy, reform, logistics, research, legitimacy, or faction management.

A strong customization system should:

- give two or three clear choices at each stage
- let repeated investment in one theme unlock a specialist threshold bonus
- allow mixed choices to create a generalist
- cap or price stacking so one combination does not become the automatic answer
- update the visible leader, traits, portrait, institution, or national spirit
- give AI route-specific profiles instead of random trait stacking
- preserve a regent, council, or interim authority as a valid final choice when the route supports it

Do not use leader customization as a menu of small percentage bonuses. The selected traits should change build priorities, decisions, route access, or how the country handles its main problem.

Use this system only when leadership construction is part of the route fantasy.

## 7.2 Civil war restraint and controlled internal conflict

Do not use a vanilla civil war as the default climax for political disagreement.

Prefer controlled alternatives when they fit:

- balance-of-power struggle
- coup attempt
- election crisis
- timed loyalty contest
- state-by-state allegiance
- targeted regional secession
- negotiated settlement
- purge or officer removal
- rival council mechanic
- limited mutiny
- leader replacement
- staged takeover through decisions and events

A full civil war is justified when territorial control and military command are central to the route.

When a focus tree uses a civil war:

- determine the participating states through clear route logic
- control division transfer where the engine and project patterns allow it
- tell the player which areas and forces are at risk
- avoid arbitrary loss of half the army
- define stockpile, navy, air force, commander, subject, and faction handling
- define postwar reintegration and the fate of surviving units
- give AI a viable war plan
- clean up all temporary tags, flags, decisions, ideas, and route locks
- make the result affect later politics instead of returning immediately to the same tree state

Do not repeat several similar civil wars inside one tree unless repeated fragmentation is the country's central mechanic. Use different internal-conflict forms for different political struggles.

## 11. Route locks and mutual exclusions

Use mutual exclusions when the country's identity changes.

Good mutual exclusions include:

- socialism versus nationalism versus democratic legalism
- civilian government versus military junta
- foreign client path versus independent path
- death cult takeover versus normal republic
- local league leadership versus isolationism
- negotiated settlement versus expansion war

Do not use mutual exclusions for branches that should logically coexist, such as army and industry.

When a route becomes impossible, use bypasses or availability logic cleanly.


A route must not depend forever on one external country taking one scripted action.

If a branch expects an invasion, alliance offer, foreign conference, sponsor decision, or historical war, define at least one safe resolution:

- an alternate valid aggressor or sponsor
- a campaign-state trigger that represents the same pressure
- a timed reveal after the historical opportunity passes
- a player decision that provokes or requests the interaction
- a bypass into the appropriate aftermath route
- a clean route closure when the premise can no longer happen

Do not leave a meaningful branch permanently inaccessible because one AI country chose another focus.

External-event gates need AI and multiplayer checks. Verify that alternate history, missing countries, dead leaders, faction changes, and player-controlled foreign actors cannot strand the tree.

