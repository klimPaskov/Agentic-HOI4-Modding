# HOI4 Feature Planning: Focus trees, countries and UI planning

Part of the [hoi4-feature-planning](../SKILL.md) skill. Read before planning focus trees, country packages and formables, starting forces and 3D units, custom UI and animation, quote and audio research, or the MCP implementation handoff.

## 3.5 Focus tree path design standard

Read [`references/focus-tree-path-design.md`](focus-tree-path-design.md) whenever the specification plans national focus routes, their ideas, branch interactions, special mechanics, or faction outcomes. It contains the complete standard for this section and its subsections.

## 3.6 Focus tree visual planning standard

Focus tree visuals should help the user and implementation agent understand the intended branch structure. The spec may include a high-level branch diagram, lane map, or route sketch for major trees, but it should not try to lock every final focus coordinate unless the user explicitly asks for that.

A useful focus tree visual should show:

- major path families
- route locks
- mutually exclusive choices
- hidden or rare paths
- convergence points
- late-game route families
- which paths should be visually separate
- which paths should be placed near each other because they interact

The visual should be readable, symmetrical where possible, and free of tangled connector lines. It should not contain random crossing lines or misleading geometry.

If the spec creates a graph or diagram, it should be treated as a design guide unless the user says it must match the final in-game tree exactly. The implementation agent may adjust the final layout to make the actual HOI4 tree cleaner.

Do not spend excessive planning effort forcing exact graph coordinates if the result becomes ugly, brittle, or unhelpful. A clear path architecture is more important than a fake exact graph.

### MCP implementation handoff

When the planned feature includes a focus tree, event chain, technology or doctrine tree, weighted logic, scripted GUI, or map surface supported by `hoi4-agent-tools`, make the matching MCP pass mandatory in the implementation prompt. Require the matching read-only inspect and render evidence before source edits, compare evidence after edits, and bounded rewrite operations only where the discovered route exists. For weighted logic, require `hoi4_ai_probability_auditor` to establish named baseline scenarios, the owner to apply the bounded patch, and mandatory `hoi4.probability_analyze` with `analysis: "compare"` against the same scenarios. If any required route is unavailable, record the exact missing tool or selector and do not treat source-only review as equivalent. The normal owning skill still controls design, source review, assets, and final validation.

If the feature is a named event that specifically introduces a dedicated scripted GUI, include a bounded `hoi4_event_ui_worker` handoff in the implementation prompt. Name the event-owned GUI identifiers, files, entry point, layout regions, states, resolutions, decisions, assets, and handoff path. Require the accepted reference, native-element mapping, iterative MCP inspection/render/correction loop, and matched final comparison under `hoi4-scripted-gui`. Reviewed source edits may be applied directly or with optional rewrite. Do not route shared event logs, event-detail frameworks, settings, super-event frameworks, or unrelated existing UIs to that worker.


## 3.12 Country package and dynamic identity standard

Read [`references/country-packages-and-formables.md`](country-packages-and-formables.md) whenever the specification creates or changes a country package, a dynamic identity, or a formable nation. It contains the complete standard for this section and its subsections. It also holds `Formable nations and formation routes`.

## 3.13 Starting forces and reinforcement pathway standard

Read [`references/forces-and-3d-planning.md`](forces-and-3d-planning.md) whenever the specification adds starting forces, reinforcements, a new unit type, or any 3D model or skeletal animation. It contains the complete standard for this section and its subsections. It also holds `3.13.1 3D model and skeletal animation planning standard`.

## 8. Custom UI and presentation

If the feature benefits from custom UI, design one.

Describe what the player sees, how it changes, and what visual assets are needed.

Map the UI states if the UI represents pressure, route choice, threat, stage, faction cohesion, recognition, contamination, loyalty, or any other living value.

## Interactive mechanic UI and animated presentation in feature specs

Read [`references/presentation-and-research-planning.md`](presentation-and-research-planning.md) whenever the specification plans an interactive mechanic UI, animated presentation, or quote, remark, and audio research. It contains the complete standard for this section and its subsections.

## 9. Quote, remark, and audio research planning

Read [`references/presentation-and-research-planning.md`](presentation-and-research-planning.md) whenever the specification plans an interactive mechanic UI, animated presentation, or quote, remark, and audio research. It contains the complete standard for this section and its subsections.

