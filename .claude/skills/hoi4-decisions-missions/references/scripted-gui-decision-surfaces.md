# Scripted GUI decision surfaces and category presentation

This reference belongs to the `hoi4-decisions-missions` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## Scripted GUI decision categories and mechanic windows

Choose the presentation layer from the hierarchy above before creating a custom window. A major mechanic does not automatically need a full scripted GUI. Use an eligible ordinary category with a static or animated picture when it communicates the system clearly. Basic formatted value tables alone do not require rich GUI. A scripted GUI is appropriate when the player must manage interacting values, targets, meters, factions, sponsors, province groups, exact interactive formable requirements, investment tracks, or competing internal blocs.

### Player-facing category text and attached displays

Decision category descriptions, status summaries, scripted localisation, and compact attached displays must read as intentional game UI. Do not use repeated pipes or vertical bars, divider-character runs, ASCII or Unicode table rows, or other text separators to simulate columns, meters, ledger rows, buttons, or panel layout. Do not emit debug-style telemetry dumps such as `Label value | Label value | ...`, generic developer-state labels, raw variable names, or country-agnostic fallback prose that can leak another country's wording.

Use short natural-language lines, properly wired icons or texticons, real meters or panels, and concise tooltips. Introduce a real scripted GUI only when a justified, functional layout gives the player interaction or state clarity that ordinary category text, decisions, tooltips, and pictures cannot provide. Category pictures and compact attached displays must not paint or textually simulate fake buttons, meters, ledger columns, or controls. Resolve country- or route-specific wording through explicit localisation branches with a neutral default fallback that cannot inherit another country's text, and verify the fallback in every supported context.

This restriction applies to runtime player-facing text and art; internal Markdown audit tables may still use normal table syntax and must never be copied into localisation.

Use the scripted GUI skill's [reference-image workflow](../../hoi4-scripted-gui/SKILL.md#reference-image-before-implementation), [active MCP preview and comparison workflow](../../hoi4-scripted-gui/SKILL.md#required-mcp-visual-review-and-optional-rewrite), and [visual and usability review](../../hoi4-scripted-gui/references/visual-review.md). These are mandatory for GUI layout, backgrounds, text, content budgets, interaction presentation, and visual evidence. Keep gameplay validation and balance review in this skill.

When a named event or event-owned mechanic specifically introduces its own scripted GUI, route the bounded layout implementation or visual-quality pass to `hoi4_event_ui_worker`. That worker must apply every rule in this section and return mandatory MCP before-and-after evidence. The decision owner retains costs, effects, availability, AI equivalents, cleanup, and balance. Do not route repository-wide interfaces, event logs, event-detail frameworks, settings, shared windows, or an unrelated existing GUI to the event UI worker merely because an event opens or references it.

A scripted GUI or custom window must have a gameplay reason. It should expose useful choices and state clearly. It must not exist only to make a small mechanic look larger.

### GUI action integrity

Every button-shaped element must be one of these:

- a real interactive control with a meaningful action
- a clearly disabled control with a visible reason
- a decorative element that cannot reasonably be mistaken for a button

Do not use fake buttons, decorative frames styled like buttons, empty click boxes, dead controls, or button art with no gameplay action. Do not place a click region outside the visible button or make the click region smaller than the visual control. Informational content should use labels, status panels, icons, meters, or tooltips instead of fake controls.

Every real button needs:

- a clear label or icon
- an accurate click region
- hover, available, selected, active, completed, warning, and disabled states when relevant
- a visible cost and requirement summary
- a tooltip that explains the action and blocked reason
- a scripted effect or decision action
- an AI equivalent when AI countries can use the system
- cleanup when the action, target, route, or mechanic becomes invalid

Do not add buttons to fill empty space or manufacture the appearance of depth. Merge actions that do the same job, and remove controls whose result does not change play. Information and navigation controls follow [click regions and state behavior](../../hoi4-scripted-gui/references/visual-review.md#click-regions-overlap-and-state-behavior); they do not require an invented gameplay effect.

### Text and explanation budget

The main panel should use short labels, concise state summaries, and current actions. Do not cover the window with paragraphs, repeated descriptions, raw triggers, long instructions, or text that restates the same mechanic in several places.

A mechanic still needs to be explained. Every non-obvious value, state, threshold, target, and action must have a short visible label and a concise tooltip or help surface that explains:

- what it represents
- what raises or lowers it
- which thresholds matter
- what it unlocks, blocks, improves, or worsens
- what the player can do about it

Keep the explanation close to the value or control it describes. Do not hide basic cause and effect in documentation outside the game. Do not use long prose to compensate for unclear layout or weak mechanics.

### Visible value budget

A scripted GUI should normally expose one primary mechanic value and no more than three supporting values at the same time. More visible values require a clear reason and distinct player actions. Internal variables may be numerous, but the player-facing interface should summarize, combine, or hide values that do not need direct management.

Reject value bloat. Merge values that measure the same pressure, remove values that do not change decisions, and avoid parallel meters whose effects are difficult to distinguish.

Do not display plain dynamic numbers with no visual or gameplay significance. Every visible value needs:

- a stable name
- a clear unit, range, or direction
- a consistent colour identity
- a second non-colour cue such as an icon, frame, label, or meter shape
- meaningful thresholds or states
- visible consequences
- at least one player action that can affect it when the mechanic allows intervention

Colour alone is not enough, and an uncoloured number alone is not enough. The player should understand why the value matters without reading implementation notes.

### Decision and action budget

A scripted GUI must not become a wall of decisions. A single phase or state should normally show three to six primary actions, plus only the active missions or target controls that matter at that moment. Use phases, target selection, tabs, replacement, priorities, or conditional visibility when the full system contains more actions.

Do not show every possible decision, target, mission, and upgrade at once. Obsolete, invalid, duplicate, low-impact, and route-incompatible actions must be hidden or removed. A system that needs dozens of simultaneous buttons should be redesigned before more layout work is added.

### Background-first layout

An image-generator-created scripted GUI background is part of the interface design. Treat it as a functional layout blueprint, not as wallpaper behind unrelated text.

Before placing controls, map the background into intended content regions. Record every prominent panel, inset, slot, frame, medallion, divider, illustration, empty field, and decorative anchor that affects placement. Each intentional functional region should have a matching GUI use, or the background should be revised.

Use the whole background deliberately. This means using its intended panels and visual anchors while preserving intentional negative space. It does not mean filling every pixel.

Do not:

- ignore a painted panel and place unrelated text beside it
- write text across ornaments, illustrations, borders, handles, seals, diagrams, or other visual elements
- cover a prominent background feature with a generic text box
- place controls between the designed slots only because the coordinates are easier
- leave half of the functional background unused while another area is crowded
- force content onto a background whose composition does not support the mechanic

Text, values, icons, meters, cards, and buttons should align with the painted frames and content zones that were created for them. If the required content does not fit those regions, revise or regenerate the background. Do not ignore the art and layer a generic interface over it.

The implementation handoff should include a background coverage map:

| Background region | Intended content | GUI elements | Interaction or state | Status |
| --- | --- | --- | --- | --- |

Use full-window renders at every supported resolution and compare them with the source background. Review the normal, selected, disabled, warning, and crowded states. Confirm that text stays inside intended regions, click boxes match visible controls, no element overlaps important artwork, and no designed functional region is accidentally abandoned.

### Interactive design contract

Interactive GUI design should define:

- entry point from the decision category
- background coverage map and layout regions
- primary value and supporting value hierarchy
- visible decision and mission budget by phase
- visible tabs, panels, cards, meters, bars, or target lists
- button costs and requirements
- what each button changes
- locked, available, selected, active, completed, warning, and disabled states
- hover and tooltip text
- scripted localisation for dynamic values
- scripted effects for button outcomes
- scripted triggers for button availability
- AI equivalents for every meaningful button
- cleanup and fallback behavior

When buttons spend resources, show the cost clearly. Use icon-first cost localisation. If the GUI button has more than a few requirements, show a short requirement summary and put details in a tooltip.

Do not use GUI buttons to bypass decision balance. GUI buttons should call the same scripted effect families, cost logic, validation triggers, logging, and cleanup that the normal decision system would use.

## Decision category presentation hierarchy

A complex scripted GUI is not the default presentation for a decision category. Choose the least complex surface that communicates the category's current state, purpose, and available actions clearly.

Static and animated category pictures are eligible only for simple categories with a description, an ordinary decision list, and at most basic formatted value tables. Existing complex UI, meters, extra custom buttons or controls, rich interactive panels, or other animations exclude an additional category picture. Ordinary decision-list buttons remain allowed, and the picture itself may be animated. Identity, atmosphere, propaganda, and territorial context do not override this gate. An interactive state-puzzle GUI cannot also receive a category picture.

Use this order:

1. ordinary category icon with concise category text
2. static category picture when eligible
3. animated category picture with a static fallback when eligible
4. compact attached display or category header
5. full scripted GUI or separate mechanic window

Do not move to a more complex layer only because the category is important. A static or animated category picture is often stronger for a category that needs identity and atmosphere but does not require the player to manage several live values or targets.

Category pictures are especially suitable for propaganda and public campaigns; civil-war preparation, insurgency, and preparedness; ideology, elections, monarchism, party control, and trade-union politics; faction management, diplomatic blocs, treaties, and intervention campaigns; formables where a territorial overview is useful but individual state pieces do not need interaction; and one-theme crisis categories whose decisions already explain the actionable details.

A category picture must remain presentation. Do not draw fake buttons, meters, values, or controls into it. Use a full scripted GUI only when the player must manage a living system that cannot be read cleanly from ordinary decisions, category text, tooltips, and a category picture, such as several interacting values, target selection, repeated map interaction, competing factions, a state-by-state formable display, or a persistent board whose state changes often.

### Decision category picture reference workflow

Before designing or auditing a category picture, inspect:

`.claude/skills/hoi4-feature-assets/assets/vanilla_reference/icons/decision_categories/pictures/`

This is the canonical larger-picture reference family and is separate from `icons/decision_categories/`, which contains small category icons. The folder must contain a labeled `contact_sheet.png`. If the sheet is missing, create it from the references, label every filename and native dimension, and update the reference `README.md` and `CATALOG.md` with provenance and surface ownership. Reference images and the contact sheet are review material only and must never be wired into runtime GFX.

When reviewing an existing mod, record category id, owner system, current presentation, picture eligibility including existing controls and animations, recommended layer, the picture-or-GUI reason, and any missing asset or implementation. Ineligible categories are not missing picture assets. Do not add a picture to every category. Keep ordinary categories ordinary when a picture would add no useful identity, territorial context, or state feedback.
