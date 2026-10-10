# Scripted GUI visual and usability review

Use this checklist when designing a native mapping and reviewing baseline, intermediate, and post-change MCP artifacts. Inspect the full composition at native output size and detailed crops for text and edges; record measurements when they reveal or verify a defect. Every applicable visible defect blocks visual completion regardless of source-edit method or optional rewrite outcome. Do not resize the preview or change UI scale to disguise a layout problem.

## Geometry, typography, and control bounds

Distinguish the source texture canvas, painted or alpha-visible shape, designed usable interior, logical GUI rectangle, rendered glyph bounds, and effective click region. Transparent padding, bevels, asymmetric ornaments, glyph bearings, borders, sprite-frame dimensions, and parent transforms can make these differ. Measure the actual element after scale, anchor or orientation, parent offsets, and frame selection; nominal texture width alone does not prove alignment.

| Check | Acceptance evidence |
| --- | --- |
| Button labels | Center rendered text horizontally and vertically in the button's usable face, accounting for glyph metrics and line height; compare left and right and top and bottom space, including hover, selected, and disabled states. |
| Text box versus visible label | `format = center` alone does not prove vertical or optical centering; verify final glyph bounds, native font and baseline, border offsets, wrapping, and the painted face. |
| Icon plus label | Center the combined group when the design calls for it, keep a consistent icon and text gap and baseline, and prevent the icon from shifting the label accidentally. |
| Margins and rhythm | Use consistent outer margins, inner padding, row pitch, column gutters, header gaps, card or button sizes, and divider spacing within the same family. |
| Alignment and symmetry | Align related edges, centers, baselines, and paired controls; preserve intentional asymmetry from the reference and correct unexplained imbalance. |
| Scaling and anchoring | Confirm parent-relative placement and usable bounds across the declared resolution and UI-scale matrix; art, text, borders, and hitboxes must remain aligned without distortion or unreadable shrinkage. |
| Clipping and overflow | Inspect container and scroll boundaries, text boxes, list rows, panels, and tooltips; no truncated labels, cut glyphs, hidden costs, half rows, or controls outside their intended region. |
| Contrast and font consistency | Match the inspected HOI4 font family and hierarchy; retain readable text and meaningful non-colour state cues against art in every state. |

Use actual native properties documented by the installed game and existing consumers. Do not invent CSS-style alignment fields or assume a sprite's scale transforms label metrics and hit geometry identically. If native button text cannot meet the layout, use a proven native text and control composition with verified click-through and state synchronization; do not leave a second painted label underneath.

## Background and reference coverage

Treat a designed background as the composition blueprint. Map each prominent panel, inset, slot, medallion, divider, illustration, ornament, and functional anchor before placing content. Preserve intentional negative space while assigning each designed usable region a purpose; a crowded corner next to abandoned functional panels is a defect. Keep text and controls inside intended interiors, clear of borders, handles, seals, illustrations, and important art. If content cannot fit, revise the composition or background within the accepted design instead of layering an unrelated generic layout over it.

Record one mapping that covers both reference and background:

| Reference or background region | Native GUI IDs and usable bounds | Content and interaction | Assets and states | Constraint or deviation and acceptance basis |
| --- | --- | --- | --- | --- |

Compare full-window renders with the reference at corresponding aspect and scale and with the actual source background. Check composition, hierarchy, focal points, proportions, button placement, density, illustration clearance, borders, and intentional empty space. Generated gibberish, fake labels, impossible components, and non-HOI4 effects must be replaced with usable native design and recorded adaptations. No reference button, meter, list, selection, or dynamic label may survive merely as flattened art when it represents actual interaction or state.

## Click regions, overlap, and state behavior

- Match the effective hitbox to the visible intended control face after scaling and parent transforms; inspect edge and center coverage and separation between adjacent controls.
- No invisible blocker may swallow input; decorative overlays and separate labels must have appropriate click-through behavior supported by their native element type.
- Review z-order and hierarchy for backgrounds, cards, icons, text, highlights, tooltips, popups, and selection overlays; required controls and text must not be occluded.
- Check hover, pressed, selected, active, completed, locked, warning, available, and disabled treatments where supported; missing tool support is an evidence limitation, not permission to claim a tested state.
- Keep frame size, label position, hitbox, contrast, and icon placement stable across states unless the reference intentionally specifies a supported change.
- Confirm selected and active states follow the displayed choice, disabled controls cannot perform the action, and their tooltip explains the blocked reason without relying on colour alone.
- Verify hidden or inactive panels cannot intercept clicks; mutually exclusive panels and actions must not overlap visibly or remain simultaneously interactive.
- Inspect close, back, open, tabs, target selection, list scrolling, and tooltip placement in the actual parent context; navigation must stay discoverable and usable in crowded states.
- Distinguish decorative texture, informational panels, and real controls visually; reject button-shaped decoration, dead controls, empty click boxes, and controls added to fill space.

## Scenario coverage and evidence

Derive normal review scenarios from linked source and accepted behavior, with coherent values and controls that can coexist on the same route. Label synthetic maximum-control stress fixtures explicitly and keep them separate from route-valid normal screens. Trace every rendered number to declared scenario inputs and its actual display source; for costs, also trace the value to affordability checks and the payment contract. Keep exact fixture values, selection, visibility and enabled state, localisation, list rows, reference version, source identity, and resource identities in the evidence manifest.

Read each emitted scenario's actual resolution and UI scale before claiming coverage; an explicit scenario resolution can override a render request's resolution list. Use separately identified scenarios with explicit resolution and scale when the emitted matrix does not contain the requested combinations. Use the live route's supported scenario fields and selectors; keep commentary and fixture provenance outside tool requests.

Cover applicable normal, hover, selected, disabled or locked, warning, active or completed, empty-list, full-list or crowded, minimum-value, maximum-value, long-text, and missing-localisation cases, plus actual open and closed panels and mutually exclusive phases. Include longest real labels, multi-line content where supported, large cost or value strings, selected targets with long names, and boundary rows in scrollable lists. Declare the supported resolution and UI-scale matrix from the brief and actual consumer, with 1920x1080 at scale 1 as the baseline unless the task specifies another target. Rerun matching scenarios after the patch; a different seed, runtime value, language, source dependency, or scale must not masquerade as an improvement.

Use supported centering, containment, visibility, and hidden-state assertions. Review warnings, source diagnostics, fidelity limits, hit-region artifacts, and the images themselves alongside assertions. Record findings by element, state, and resolution with before and after evidence and disposition; a passing validation boolean never overrides a visible defect.

## Usability and integration

Check that the player can identify current state, main objective or pressure, next meaningful action, and consequences without cross-referencing documentation. Keep related status, thresholds, costs, blocked reasons, and actions together, with concise labels and precise tooltips. Label counters truthfully as cumulative, periodic, or latest-receipt values, and distinguish all-cause totals from contributions attributed to the owning system. Show retained reserves as non-consumed requirements, separate from consumed costs, and make the actual debit clear.

Apply the skill's mechanic-value and action budgets without using extra tabs to evade them. For gameplay controls, obtain the decision owner's evidence that shown costs and requirements match selection checks, payment, effect, AI equivalent, and cleanup; a visual pass cannot establish gameplay balance. For information-only or navigation controls, verify their declared purpose and enabled or selected behavior instead of demanding a gameplay effect. Report an out-of-scope shared-interface problem to the parent without editing it.
