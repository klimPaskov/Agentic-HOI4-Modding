# HOI4 Events: MCP evidence and subagent ownership

Part of the [hoi4-events](../SKILL.md) skill. Read before treating an MCP inspection, render or probability result as evidence, and before delegating event work to subagents.

### MCP evidence gate

Before treating an event inspection or render as lifecycle evidence, read its `analysisMode`, `complete`, indexed helper count, files-scanned or source-hash inventory, unresolved entries, and diagnostics. In the installed event service, `trace` and `explain_path` use focused analysis, and `scan`, `roots`, `lint`, or `event_render` use focused analysis when a selector is supplied. Focused analysis reads only the bounded event and on-action sources, disables workspace-wide helper projections and lifecycle passes, and keeps the focused-boundary blocker even when helper expansion is requested. `state_flow` and `impact` request full analysis even when narrowed, while selector-free `scan` requests full analysis. Use a full route when helper or lifecycle coverage is required, and do not treat a focused trace or zero helper count as proof that a chain has no helpers.

`event_inspect` with `mode: "compare"` accepts cached revisions, validated event-graph artifacts, or proposed source overlays. Report-only trace artifacts and render or manifest artifacts may fail artifact graph validation because they do not contain an event-graph payload. Use a graph-bearing artifact or another supported compare input when available. If none is available, preserve the exact blocker and do not invent a conversion or comparison result.

For every event-option `ai_chance`, event MTTH, direct random chance, or `random_list` surface, route the read-only probability pass through `hoi4_ai_probability_auditor`. Establish named baseline scenarios with `hoi4.probability_inspect`, let the owning agent apply any bounded patch, then run mandatory `hoi4.probability_analyze` with `analysis: "compare"` against the same scenarios. Use `hoi4.probability_inspect`, `hoi4.probability_analyze` with `analysis: "sweep"`, `hoi4.probability_analyze` with `analysis: "simulate"`, `hoi4.probability_analyze` with `analysis: "sequence"`, and `hoi4.probability_analyze` with `analysis: "render"` only when their declared evidence conditions apply. Provide complete option or list pools when normalization applies, and provide scheduled state changes for timing questions. Treat exact, bounded, sampled, score-only, and unresolved results as different evidence. For `hoi4.probability_analyze` with `analysis: "compare"`, pass both `before` and `after` as probability-source objects with a source identifier or path, inline Clausewitz, or virtual patch, or pass before and after manifests under an identical scenario set. Do not put a cached `analysisId` in a source identifier; it belongs only to rendering. The auditor does not choose balance targets or edit event source. If the probability route is unavailable, record the exact blocker and leave the conclusion unresolved.

For event-option audits, qualify a reused option identifier with its parent event identifier and include every option in that event's local candidate pool. Verify the installed server version and live route schema before building scenarios; use top-level scenario dates, explicit controller maps, and typed scope bindings only when that schema accepts them. Inspect returned `poolComplete` and `unresolved` fields before interpreting a normalized share. Treat `candidateOverrides` as declared assumptions, not proof of live eligibility. An option share conditional on an event firing does not include the event's firing chance.

Give patch-capable subagents disjoint file ownership. Serialize overlapping edits and run the final comparison only after their handoffs are integrated.


## Parent and subagent implementation ownership

Patch-capable subagents are active by default inside the current task scope. Use them when a large event touches focus trees, decisions, country packages, localisation, GUI, scripted helpers, or assets at the same time.

Small subagent patches are allowed when they improve a specific surface without changing the event design. A decision subagent can vary costs, clarify tooltips, add cleanup, improve AI weights, and patch related localisation. A focus subagent can fix a route lock, prerequisite, bypass, focus AI, icon reference, small reward, or formable unlock hook. A country package subagent can patch tag setup, party names, focus loading, leader references, country localisation, simple starting setup, or existing formable requirements. A localisation subagent can patch dynamic text directly. A scripted-system architect can add narrow helpers and direct call sites when the repeated logic is already present.

The parent still owns final integration, docs, explicitly scoped external records, event chain direction, completion claims, and any broad mechanic expansion. If a subagent sees a needed route family, new country package, new formable suite, new scripted GUI system, new event chain, or major balance redesign, it writes a plan under `docs/plans/<feature_slug>/` and stops.

Every subagent edit must produce a handoff under `docs/plans/<feature_slug>/subagent_handoffs/` when the feature slug is known. The handoff lists changed files, identifiers, behavior before and after, meaningful validation, remaining gaps, and follow-up work for the parent.


