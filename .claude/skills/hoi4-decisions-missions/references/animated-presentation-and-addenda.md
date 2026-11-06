# HOI4 Decisions and Missions: Animated category presentation and improvement addenda

Part of the [hoi4-decisions-missions](../SKILL.md) skill. Read before animating a decision category or turning an improvement addendum into decisions and mechanic windows.

## Animated decision category presentation

Apply the same picture eligibility gate to static and animated category pictures. The GUI animation examples below apply to their own controls and panels, and do not authorize adding a picture alongside them.

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

## Improvement addenda for decisions and mechanic windows

When an improvement addendum proposes decision depth, scripted GUI, or mechanic windows, translate the design into active play. The decision category should show the mechanic clearly, but the gameplay should still live in decisions, missions, scripted effects, scripted triggers, AI rules, and cleanup logic.

Use scripted GUI when the player needs to read or manage values that would otherwise be buried in tooltips. Good uses include influence boards, federation congresses, formable progress, patron leverage, resource routing, public fear, occult pressure, faction cohesion, reform votes, target cards, and timed crisis panels.

The addendum must choose the presentation layer before requesting art or controls and explain why it is the clearest option. For a justified GUI, use the [reference-image workflow](../../hoi4-scripted-gui/SKILL.md#reference-image-before-implementation), [content and interaction budget](../../hoi4-scripted-gui/SKILL.md#content-and-interaction-budget), and [background mapping](../../hoi4-scripted-gui/references/visual-review.md#background-and-reference-coverage). Do not respond to a shallow mechanic by adding meters, decisions, text, or decorative controls. Every gameplay-changing button must satisfy GUI action integrity; animation must not obscure costs or compensate for weak effects.

For formables, the decision should verify the map state. Focuses may reveal claims, prepare institutions, or reduce costs, but the formation decision should prove control, legitimacy, recognition, or integration when those are central to the idea.

