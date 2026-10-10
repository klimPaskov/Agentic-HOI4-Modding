# Final prompt files, response checklist, and quality gate

This reference belongs to the `hoi4-feature-planning` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 19. Final prompt files

Only after the full specification is complete, create separate prompt files outside the spec file and include them in the final zip package.

Required prompt files:

- `feature_slug_asset_prompt.md`
- `feature_slug_text_audio_research_prompt.md` when the feature needs sourced text or audio
- `feature_slug_achievement_prompt.md`
- `feature_slug_decision_mission_prompt.md` when the feature has large decision or mission systems
- `feature_slug_coding_prompt.md`
- `feature_slug_goal_prompt.md`

The final answer should point to the final zip package as the deliverable and briefly summarize what the package contains.

### Asset prompt file

Create an asset prompt for `hoi4-feature-assets`.

The prompt should cover all required visual assets, progression-state variants, final asset packaging, reference folders, source modes, and manifest requirements.

### Text and audio research prompt file

Create sourced quote, remark, or audio research prompt for `hoi4-text-audio-research` if the feature needs sourced text or audio.

The prompt should cover title direction, quote research, cultural remark research, slogan or allusion research, audio research, source documentation, licensing notes, and coordination with asset work when a custom image is also needed.

The prompt must not provide unresearched final titles, button text, quotes, slogans, lyric fragments, cultural references, or final audio choices. Use research gates and role labels instead. It must tell the text and audio researcher to produce the final text package only after source checks.

### Achievement prompt file

Create a separate achievement prompt file for the coding and asset agents.

The achievement prompt must include every planned achievement with id, title direction or working label, description direction, eligible countries, unlock conditions, disqualifiers, difficulty, hidden or visible status, why it is not trivial, icon direction, and all required tracking notes.

The achievement prompt should tell the implementation agent to inspect existing achievement patterns, implement the achievements, wire localisation and icons, create any required tracking flags or variables, document them, and avoid easy unlocks.

### Coding-agent prompt file

Create a coding-agent implementation prompt that summarizes the finished feature spec.

The prompt must tell the coding agent to:

- implement the feature according to the spec
- implement all mapped decisions, variants, escalation variants, focus trees, custom tags, country packages, achievements, assets, and sourced text or audio packages included in the spec
- implement the mapped cost and sacrifice model, avoiding boring political power or command power only decisions when the spec calls for XP, equipment, manpower, stability, war support, fuel, supply, units, local support, foreign access, or other concrete costs
- implement focus trees according to the path design, with coherent non-linear branches, route locks, side paths, convergence nodes, hidden routes, focus filter tags or search categories, varied reward types, proper icons, final localisation written from the spec direction, AI behavior, feature integration, and no filler shortcuts
- create the final exact focus layout and connections cleanly in implementation while preserving the spec's path logic
- implement every country package from the spec, including tag, history, names, cosmetic names, ideology names, ruling parties, leaders, leader changes, flags, route-specific identity changes, starting divisions, dynamic unit packages, force-growth decisions and focuses, volunteer routes, decisions, ideas, AI behavior, localisation, assets, and docs
- implement the full AI strategy matrix from the spec, including route preferences, foreign influence behavior, focus choices, unit-raising choices, decision choices, faction behavior, and extreme-route exceptions
- follow `AGENTS.md`
- follow `hoi4-events` if the feature includes ordinary HOI4 events, event chains, news events, or report events
- use `hoi4-feature-assets` if visual assets are required
- use `hoi4-text-audio-research` if sourced text or audio is required
- write final player-facing feature, decision, focus, achievement, GUI, feature-detail, and parent-provided external record wording from the direction in the spec. Do not expect the planning spec to provide finished copy
- treat unresearched text or audio titles, button text, quotes, cultural remarks, slogans, allusions, and audio choices as blockers, not as implementation-ready localisation
- keep all mod systems aligned
- report anything that cannot be implemented cleanly
- keep iterating until the full spec is implemented to its fullest extent
- spawn `hoi4_improvement_loop_planner` without inherited conversation context before claiming the goal is near complete, then resolve its addendum or closure handoff before final completion
- avoid fallbacks, simplifications, temporary versions, and good-enough approximations
- not claim completion until the implemented files satisfy the spec

### Goal prompt file

Create a separate `/goal` prompt file.

The goal prompt must be less than 3500-4000 characters.

The goal prompt should not contain the whole spec or all long instructions. It should point to the spec files and the other prompt files, then state the most important pass or fail requirements.

The goal prompt must tell the implementation agent to keep iterating until the goal is accomplished to its fullest extent. It must also say not to claim completion until the implemented files satisfy the spec.

A good goal prompt should include:

- the spec file path
- the coding prompt file path
- the asset prompt file path
- the text and audio research prompt file path when relevant
- the achievement prompt file path
- the required skills or docs to follow
- the top design non-negotiables
- the requirement to create all required static and animated assets, static fallbacks, tags, starting divisions, reinforcement pathways, non-linear focus trees based on the mapped paths, focus filter tags, decisions, escalation variants, achievements, and docs
- the requirement to research and source final presentation titles, button text, quotes, cultural remarks, slogans, allusions, and audio through the proper text and audio research workflow when sourced text or audio exists
- the requirement to spawn `hoi4_improvement_loop_planner` near completion and resolve its addendum or closure handoff before claiming completion
- the requirement to provide a concrete completion report

If the goal prompt is near 4000 characters, shorten it by pointing to files instead of repeating details.

## Formation and UI questions for planning passes

Before finishing a major feature spec, ask:

- Can any country created or empowered by the feature form a larger state later?
- Are there regional, ideological, hidden, or extreme-route formables that should be locked behind focuses, decisions, or features?
- Does each formable have concrete map requirements and a clear post-formation identity?
- Do formation rewards avoid free core spam, free war-goal spam, and instant runaway snowballing?
- Does the decision category need a scripted GUI, progress meter, custom window, or animated presentation?
- If a named event introduces that UI, does the plan route only the event-owned window to `hoi4_event_ui_worker` with exact identifiers and mandatory MCP before-and-after evidence while excluding shared interfaces?
- Has every important mechanic, formable route, reveal, faction board, crisis meter, and major transformation received a presentation-choice pass?
- Are animated sprites, leader portraits, particles, glow, float loops, warning pulses, selected states, hover states, or button states planned where they would make the mechanic clearer?
- Are static and animated category pictures restricted to eligible simple categories, with no extra picture alongside complex or animated GUI?
- Does the asset prompt include all static and animated UI pieces, frame-sheet needs, sprite names, state logic, and fallbacks?
- Does the goal prompt tell the implementation agent to verify formables, UI windows, animated sprites, frame-sheet handoffs, and fallbacks?

## 20. Final response checklist

The final response should include:

- spec file created
- external records used only when the repository has them and the parent provides them
- repo context inspected
- linked feature group role defined when relevant
- assets defined when needed, including country identity assets
- presentation-choice pass completed for important mechanics, custom UI, formables, route reveals, and leader transformations, with category-picture eligibility recorded
- animated sprite and animated portrait needs mapped with static fallbacks, state logic, and `hoi4-frame-animation` handoff expectations when relevant
- historical flags and real symbols marked for sourced asset work, with real leader portraits routed to `hoi4_portrait_creator`
- quote, remark, image, or audio direction defined when needed
- general localisation handoff uses direction only for feature titles, options, descriptions, decision text, focus text, achievement text, GUI labels, feature-detail text, and external record wording
- researched text research gates used when final title, button text, quote, cultural remark, or audio has not been researched
- no unresearched text or audio title, button text, quote, cultural remark, slogan, lyric fragment, or allusion presented as final localisation
- country package matrices created for new or modified countries when relevant
- starting force and reinforcement pathway plans created for new or transformed fighting countries, including dynamic scaling, template families, unit sources, and later reinforcement routes
- AI strategy matrix created for major features or country-creation features
- focus tree paths mapped clearly when the feature creates playable or long-lived countries, with major routes, anchor focuses, mutual exclusions, rewards, and filter categories described
- every major focus tree written with clear path logic, not vague branch names
- every major focus tree includes a non-linear architecture map with trunk focuses, fork points, route locks, optional branches, convergence nodes, hidden routes, crisis branches, and late-game branches where relevant
- every major focus tree includes focus reward diversity and an idea audit when ideas or national spirits are used
- focus rewards include varied buildings, factories, military, industry, diplomacy, decisions, missions, identities, and mechanics where appropriate, not mostly new ideas
- final zip package created with all spec files, prompt files, route diagrams if used, research notes, and matrices
- focus tree files split into separate parts when the tree is too large for one file
- decisions and rare variants mapped when they exist
- feature option tone mapped where feature options exist, including irony, sarcasm, cultural remarks, humour, or deliberate plain severity
- escalation variant entry paths mapped when escalation variants exist, including active-feature escalation variant, pre-activation escalated opening, or a clear reason only one path applies
- decision and objective costs use varied resources, sacrifices, requirements, and risks instead of defaulting to political power or command power
- achievements mapped with difficult conditions, icon directions, and tracking notes
- ideology-specific names, cosmetic names, leader changes, and flag changes mapped when relevant
- unit-creating focuses and decisions mapped with requirements, template families, pressure effects, AI behavior, and blocked localisation notes when relevant
- uncertainties or blockers
- idea, spirit, decision, mission, and focus effects are strong enough to matter and not only conservative small modifiers
- `hoi4_improvement_loop_planner` spawned near completion, with its expansion addendum folded in, queued with reason, rejected with reason, or closure handoff recorded
- downloadable link to the final zip package

## 21. Cleanup and quality gate

Before saving the final files, perform a strict review.

Reject the draft if it has any of these problems:

- vague placeholder decisions
- vague rare variants
- vague country paths
- custom tags without full country identity, assets, politics, leaders, flags, AI, and content expectations
- new or modified countries without country package matrices when they matter
- newly appearing crisis countries without dynamic starting unit packages or a clear reason why they start without troops
- country-created crisis specs without decisions, focuses, objectives, depots, volunteers, or faction systems that let those countries gain more units later
- new fighting countries without starting force plans, dynamic unit scaling, or reinforcement pathways
- long-lived new countries without dynamically scaled starting units or credible reinforcement routes
- newly appearing or transformed countries without mapped starting divisions, unit templates, equipment/manpower assumptions, and dynamic scaling factors
- countries with no designed way to gain, improve, convert, or coordinate more units through focuses, decisions, objectives, volunteers, depots, or faction mechanics
- generic repeated unit focuses or unit decisions that hand out identical divisions without story, route identity, or conditional requirements
- historical countries or movements with invented generated flags when sourced historical flags should be used
- real historical leaders planned as generated portraits instead of sourced portraits
- playable countries without clear focus-tree path maps
- focus tree sections that list only branch names without explaining path logic, mutual exclusions, rewards, and connections
- focus tree plans that give only vague samples without enough path detail for implementation
- focus trees where most focuses grant a new idea or national spirit without a clear reason
- focus trees with repeated new ideas where modifying or upgrading an existing idea would be better
- focus trees without an idea audit when many ideas or national spirits are used
- focus rewards that are mostly political power, stability, war support, or repeated flat modifiers
- focus trees missing varied reward types such as factories, forts, anti-air, airbases, railways, supply hubs, units, decisions, missions, advisors, leaders, identities, claims, or diplomacy where those rewards would fit
- major focus paths without focus filter categories or search categories
- major focus trees without a focus filter taxonomy or path category table
- major countries without separate political, military, industry, diplomacy, and expansion or special-mechanic sections when those sections fit the country
- focus trees that are too small, generic, linear, or boring for the country role
- focus trees missing distinct political, industry, and expansion branches
- important country trees with isolated branches that do not affect each other
- major branches without clear payoff
- political branches that do not change politics, leaders, advisors, parties, laws, names, flags, or country identity where relevant
- industry branches that do not change the map, production, logistics, construction, or resources
- expansion branches that do not create claims, cores, war goals, leagues, protectorates, settlement decisions, or external diplomacy
- expansion routes without postwar handling
- industry routes without geographic grounding where relevant
- major routes without route-specific AI behavior or localisation tone
- large features without a special mechanic or clear reason for not needing one
- special mechanics without clearly named values
- mechanic values without dynamic focus, decision, mission, feature, war, state-control, foreign-influence, or AI hooks
- important mechanic values without consistent colour identity or readable breakdowns
- focus trees or decision systems disconnected from the mechanic values they should affect
- feature-created factions without goals, rules, membership logic, shared decisions, AI behavior, rewards, or success and failure states
- special mechanics without a defined player-facing presentation surface
- scripted GUI mechanics that would benefit from progress meters, status frames, variants, or animation but define only static text
- special mechanics that hide basic visible cause and effect
- generic playable country packages with no specific identity, map role, military style, economy, diplomacy, AI, or mechanic
- shared trees with no country-specific localisation, route names, decisions, AI weights, leaders, or rewards
- AI routes that can choose invalid, impossible, or unavailable branches
- important mechanic values scattered as magic numbers instead of script constants or documented tuning
- reward dump design used as the main pattern
- balance plans without exploit checks for free units, factory loops, equipment farming, influence farming, puppet abuse, war-goal spam, claim or core spam, advisor stacking, bypass abuse, or repeatable decision abuse
- decision systems that show every possible action at once instead of using phases, caps, priorities, pools, route locks, thresholds, or crisis filters
- factions that form too easily without minimum membership, crisis pressure, ideological compatibility, war state, or diplomatic preparation
- routes with no visible game evidence beyond hidden variables or tiny modifiers
- large trees with no early, middle, and late pacing
- routes with no tradeoff or failure state
- overuse of mutual exclusions where support branches should coexist
- localisation that reveals hidden effects, secret outcomes, or future surprises instead of visible baseline effects
- route-unlocked advisors that do not match route identity
- major focus trees without achievement hooks
- completion prompts missing a route coverage table requirement
- near-completion work that skipped the mandatory `hoi4_improvement_loop_planner` pass without a tooling blocker
- unresolved loop-agent expansion addendum, missing addendum disposition, or missing closure handoff before completion
- focus trees where unit rewards are repeated generic division spawns instead of route-specific military institutions, decisions, templates, or mobilization systems
- unit-granting focuses that exist only as filler or repeated free divisions with no story, route logic, or constraints
- major focus trees that read like one vertical checklist instead of a branching system
- focus tree sections without an architecture map or path plan showing route locks, optional branches, convergence points, hidden routes, crisis branches, and late-game branches where relevant
- branches where every focus simply follows the previous one without a strong story reason
- expansion trees that are only linear claim ladders instead of ideology, trauma, patron, military, economic, or escalation-driven ambitions
- escalation variants that are really just ordinary stages
- escalation variant specs that do not define whether each escalation variant enters through active-feature escalation variant, pre-activation escalated opening, or both
- active-feature escalation variants that do not state what changes immediately for existing active actors
- pre-activation escalated openings that do not state how the first run changes before the ordinary baseline starts
- fixed cooldowns or pressure values without dynamic factors
- decision, mission, or focus cost plans that rely mostly on political power or command power when concrete costs such as XP, equipment, manpower, fuel, stability, war support, supply, local support, foreign access, or unit commitments would fit better
- achievements missing from a major feature spec
- achievements that unlock too easily or only reward the obvious route
- achievements without conditions, disqualifiers, icon directions, or tracking notes
- missing asset handoff for required assets
- major mechanic, formable, reveal, scripted GUI, or leader transformation with no presentation-choice pass, or category pictures requested for ineligible complex or animated categories
- animated asset plan that lacks static fallback, state logic, frame-sheet handoff, target surface, sprite names, or `hoi4-frame-animation` ownership
- missing asset coverage for country names, cosmetic identities, ideology flags, focus-route flags, leader changes, portraits, faction emblems, decisions, focuses, ideas, achievements, and UI where relevant
- missing AI route matrix for major features, country-creation features, or foreign-influence systems
- missing text/audio research handoff for required text and audio packages
- final feature titles, feature options, feature descriptions, report prose, news prose, decision names, decision descriptions, focus names, focus descriptions, achievement titles, achievement descriptions, GUI labels, feature-detail text, or external record wording written as pasteable localisation when the spec should give direction only
- sample, possible, temporary, or placeholder player-facing text included in the spec when the coding agent should write the final wording
- presentation title, button text, quote, cultural remark, slogan, lyric fragment, allusion, or audio choice written as final content without research and source documentation
- placeholder, sample, or working researched text that could be pasted into localisation
- role labels, asset names, achievement titles, or prompt filenames reused as final presentation localisation without research
- coding prompt or goal prompt that lets unresearched researched text be implemented instead of treating it as blocked
- goal prompt over 4000 characters
- goal prompt that tries to contain the whole spec instead of pointing to files
- missing final zip package containing all required spec files, prompt files, route diagrams if used, research notes, and matrices
- admin audit sections inside the spec
- major feature ideas or spirits whose main effect is a tiny modifier with no meaningful strategic role
- obvious system plumbing repeated as design

The spec should be ambitious, detailed, researched, and usable. Do not stop at a conservative minimum when the idea supports more.
