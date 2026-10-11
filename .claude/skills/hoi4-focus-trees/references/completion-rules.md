# Focus tree completion rules

This reference belongs to the `hoi4-focus-trees` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 17. Completion rules

A focus tree task is complete only when:

- the tree has distinct political, industry, and expansion branch families, unless it is explicitly documented as a temporary non-playable tag
- large playable countries have military, diplomacy, internal faction, special mechanic, and late-game branches where their identity supports them
- the opening is lean enough to understand and complexity is revealed in stages
- stable countries do not start with unnecessary stacks of national spirits or military clutter
- the country's main constraints create route incentives and are not erased immediately
- the first meaningful strategic choice appears early
- political routes exist because they have a real historical, institutional, alternate-history, event, or high-chaos basis
- no shallow ideology route exists only to satisfy a route quota
- focus durations match the size of the decision and do not split one reward into empty clicks
- early choices change the build plan, military timetable, foreign alignment, leadership, mechanic, or route
- underused branches provide country-specific cross-branch utility
- branches interact through prerequisites, decisions, missions, events, AI, crisis values, diplomacy, or route locks
- every major branch has a clear payoff
- political routes change visible country identity where relevant
- industry routes affect the map, production, logistics, or construction
- expansion routes create claims, cores, war goals, leagues, protectorates, settlements, declarations, guarantees, or external diplomacy
- route architecture is implemented
- expansion branch exists for large trees
- political routes actually change politics
- rewards are varied and concrete
- fairy-dust reward patterns have been removed, merged, strengthened, or connected to visible mechanics
- authored gameplay tuning values use round multiples of 5 unless a documented engine, formula, or technical exception applies
- no route can maintain more than three focus-tree-created national spirits at the same time
- focus terminal nodes are real capstones, convergence points, route locks, failure states, formable steps, or meaningful optional side payoffs
- dead-end branches with weak final rewards have been redesigned
- ideas are not spammed
- national spirits are earned through meaningful route commitment, cost, risk, milestone progress, or mechanic interaction when their effects are important
- important national spirits have lifecycle stages, decision or mission hooks, mechanic hooks, or clear route identity
- easy national spirits are narrow, temporary, modest, or part of a staged system
- focus-decision integration exists
- AI behavior is implemented
- localisation and icons exist
- distinct focus-tree branches use distinct palette families and do not rely on one repeated colour palette or simple hue-shifted icon composition
- layout is readable
- the tree is compact, symmetrical, and centered around its opening group or main trunk
- comparable sibling branches use balanced mirrored spacing and consistent vertical rhythm
- no focus boxes overlap and no connector lines overlap, intersect, or pass through focuses
- every prerequisite uses the shortest clean practical path and no avoidable long connector remains
- no ladder, staircase, zigzag, decorative detour, or offset linear chain is used to fake complexity or non-linearity
- documentation is updated
- route coverage table compares required routes with implemented routes
- routes have visible baseline effects without revealing hidden outcomes
- special mechanic values are changed by relevant focus paths
- balance-of-power or equivalent internal struggle mechanics are used when appropriate
- event-created factions have goals, membership rules, shared mechanics, AI behavior, rewards, and success or failure states
- special mechanics have visible presentation through decision headers, scripted GUI, progress meters, tooltips, or spirits
- important custom GUI mechanics consider progress variants, status frames, warning frames, selected or locked variants, and frame animations where useful
- AI routes respect validity and avoid impossible branches
- shared trees are adapted per country and do not read or play identically
- important tuning values are centralized in script constants or documented tuning files
- one-time reward dumps are not the main branch pattern
- small modifiers are never the main reward pattern for important branches
- fairy-dusted values such as `+2%`, `+3%`, `+7%`, `12`, or `18` are absent unless their exact use is documented and justified
- exploit checks cover unit loops, factory loops, equipment dumps, cores, claims, war goals, advisor stacking, influence farming, bypass abuse, and puppet abuse
- decision categories avoid showing every possible action at once
- large trees have early, middle, and late pacing
- major routes have real tradeoffs and failure states
- important early branches offer distinct short-term, balanced, or long-term strategies where the country supports them
- temporary power windows define their duration, active cost, intended use, aftermath, and AI behavior
- permanent extreme policies have an exit or a documented identity reason for remaining permanent
- interactive focus requirements use relevant game systems and explain exact requirements
- central route gates have decisions, missions, or other tools that let the player pursue them intentionally
- several-focus autopilot chains have been merged, shortened, or given real interaction
- optional side investments remain optional unless the route logic requires full commitment
- meaningful early active play exists where the country premise calls for it
- limited wars define objectives, participants, escalation, peace, AI, cleanup, and postwar handling
- external event gates have alternate activation, timeout, player action, bypass, or clean closure
- civil wars are controlled, previewable, and fully cleaned up when they are used
- leader or institution customization has viable specialist and generalist outcomes when it is used
- mutual exclusions are not overused
- major routes have distinct AI behavior and localisation tone
- expansion branches include postwar handling
- industry branches are geographically grounded where possible
- advisor unlocks match route identity
- achievement hooks exist for major route accomplishments
- simplifications and blockers are reported

If a tree uses a fallback tree where the spec requires a bespoke tree, report it as a simplification.

If no simplifications were made, say so and provide evidence.
