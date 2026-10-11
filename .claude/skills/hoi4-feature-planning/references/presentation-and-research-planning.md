# Interactive UI, presentation, and research planning

This reference belongs to the `hoi4-feature-planning` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## Interactive mechanic UI and animated presentation in feature specs

When a feature has an important mechanic, decide whether the decision category needs a richer scripted GUI or a separate mechanic window. The spec should define the player-facing interface when the system is important enough to manage visually.

Use [hoi4-scripted-gui](../../hoi4-scripted-gui/SKILL.md) as the source of truth for reference images before implementation, native element and background mapping, content and interaction budgets, iterative MCP live previews, scenario and resolution coverage, and visual acceptance. The plan must give any event-owned UI worker enough exact scope and acceptance context to follow that workflow without guessing.

For major features, important decision categories, custom mechanic windows, formable routes, route reveals, crisis meters, leader transformations, and faction boards, run a presentation-choice pass. Choose ordinary category presentation, an eligible static or animated picture, a compact attached display, or a full GUI. Plan animation only when it clarifies a changing state or materially supports the accepted presentation. Static presentation needs no defensive justification when it is clearer.

A mechanic UI spec should include:

- where the UI appears, such as decision category header, attached scripted GUI, custom window, feature-details panel, or country mechanic panel
- what button opens or closes the window
- what values, targets, meters, cards, lists, tabs, or map states the player sees
- what buttons the player can click and what each costs
- how unavailable buttons explain missing requirements
- what scripted effects and scripted triggers own the button logic
- how AI performs equivalent actions without relying on human-only clicks
- how the UI cleans itself up after route change, tag change, annexation, civil war, peace, or feature completion
- what localisation and scripted localisation the UI needs
- what static assets, animated sprites, hover states, selected states, locked states, warning states, and progress variants it needs
- what animated state communicates, such as available action, rising pressure, critical danger, selected target, active ritual, foreign influence spread, reform momentum, hidden route reveal, route corruption, or completion
- which animation surfaces are state-driven and which are decorative
- which static fallback appears when animation is disabled, unsupported, not yet produced, or hidden by route state
- whether the UI is introduced and owned by one named event; when it is, the exact `hoi4_event_ui_worker` scope, allowed files, MCP evidence set, and handoff path
- explicit exclusion of any shared interface the event merely opens or references, including event logs, event-detail frameworks, settings, and shared framework windows

The spec should not make an interactive window for every small modifier. Use custom UI when it improves readability, choice, atmosphere, or management of a living system.

Animation can make pressure changes, council activation, available actions, crisis states, route changes, or failure thresholds easier to notice. Choose it for that useful feedback, preserve static fallbacks, and avoid noise. These GUI animation examples do not authorize adding category pictures alongside complex or already animated GUI.

Animation is especially useful when the player needs to notice a changed state without reading a long tooltip. Good default candidates include decision category seals, category headers, scripted GUI buttons, meter frames, status cards, selected target cards, warning borders, hidden route seals, formable progress emblems, faction cohesion panels, patron influence nodes, and extreme-route route emblems.

For each planned animated asset, the spec should define the in-game use, target surface, state logic, frame count expectation, loop behavior, static fallback, source mode, asset handoff owner, and proposed sprite names when they are known. The final animation must follow `hoi4-frame-animation`, meaning real source frames, a frame sheet, a static fallback, a preview GIF for review only, and a `.gfx` handoff. Do not describe a GIF, filter pulse, recolour loop, shifted still image, or transform-only mockup as the final game animation.

Leader portraits can have animated variants for major route reveals, extreme-route leaders, supernatural leaders, symbolic councils, final formables, or dramatic country transformations. The spec should say when the animated portrait appears, what static fallback exists, whether the portrait is sourced or generated, what state or route controls it, what removes or replaces it, and how the animation remains period-appropriate and readable at leader-portrait size.

## 9. Quote, remark, and audio research planning

If the feature needs sourced wording or audio, design the research need as part of the feature's emotional and gameplay pacing.

Do not assume every feature needs researched quotes, cultural remarks, or music. Use researched text or audio only when it improves a reveal, route payoff, achievement theme, custom UI surface, event chain, focus route, decision package, menu cue, or feature announcement.

When planning a researched text or audio package, define:

- why this feature needs researched material
- what exact feature state uses it
- whether it supports a reveal, escalation, transformation, defeat, aftermath, campaign-ending moment, route payoff, achievement theme, custom UI cue, or other feature role
- what the player should understand when it appears
- what information remains uncertain
- what quote direction would fit
- what cultural remark, slogan, or allusion direction would fit
- what audio mood would fit, if audio is needed
- whether follow-up events, decisions, focuses, UI, docs, or assets must stay aligned with it

Do not fully research quotes, cultural remarks, slogans, allusions, or music inside this planning skill. Use `hoi4-text-audio-research` for that work.

The feature spec should provide enough direction for `hoi4-text-audio-research` to find real quotes, meaningful cultural remarks, and suitable audio without guessing the feature role.

### Text boundary and research gate

This planning skill is direction-only for sourced quotes, cultural remarks, slogans, lyric fragments, scripture excerpts, literary allusions, film lines, song references, book references, game references, and audio choices. Do not write final source-dependent text inside the feature spec unless the exact wording has already been researched, sourced, and documented through `hoi4-text-audio-research` or a provided source file.

If research has not been done, use neutral research gates instead of lines that could be pasted into localisation:

- `Main quote: research required`
- `Cultural remark: research required`
- `Slogan or allusion: research required`
- `Audio candidate: research required`

Do not include unresearched `possible line`, `sample title`, `placeholder quote`, or `temporary button text`. Implementation agents may treat those as final localisation.

Describe the desired shape instead. For example, write `short public reaction direction about fear spreading through port cities, avoiding generic apocalypse wording`, not a finished line.

Functional labels are allowed for spec structure, asset filenames, prompt routing, branch labels, and internal handoffs, but they must be neutral and explicitly non-final. Do not name assets, localisation keys, or prompt files after unresearched title concepts.

### Major-feature defeat aftermath

Some major features should also have a structured aftermath when the threat is beaten.

Use a defeat aftermath package when all of these are true:

- the defeated threat was global or near-global in reach
- the campaign lasted long enough to feel like a world crisis
- the cost in casualties, destruction, or political disruption was high enough that the world should not simply snap back to normal

Typical aftermath content:

- a sourced quote, cultural remark, or audio cue when the aftermath needs researched material
- postwar treaties, compacts, or new world orders
- recurring remembrance, reconstruction, or vigilance features
- lasting ideas, tech-sharing groups, or diplomatic rules that exist because the world learned from the crisis

Do not add a treaty/new world order after every contained or short-lived disaster. Those only make sense when the feature genuinely reshaped the campaign.
