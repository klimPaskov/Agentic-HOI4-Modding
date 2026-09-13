# Vanilla interface review shelf

The `vanilla/` subtree contains 42 PNG/SVG review artifacts carried from the
Chaos Redux working-tree reference collection on 2026-09-13. No mod-specific
interface art is included. The collection contains five actual families:

- `design_and_organization/`: organization and design windows.
- `diplomacy_and_outcomes/`: diplomatic presentation and outcomes.
- `market_and_inventory/`: market/inventory information.
- `projects_and_research/`: special-project and research windows.
- `settings_and_controls/`: settings and native control examples.

Inspect the selected artifact at native size and identify its exact installed
vanilla `.gui`, scripted-GUI, GFX, and texture consumer before adapting it.
`.full.png`, cropped PNG, SVG, and `_review_contact_sheet.png` are different
review aids, not interchangeable runtime outputs. These inherited artifacts
are not fresh live MCP evidence for the target mod and must never be wired as
final art or substituted for the target's inspection/render/comparison cycle.

Choose patterns for hierarchy, alignment, controls, grouping, spacing, and
information density. Generate an approved composition only when the brief
needs one, map all interactive/dynamic content to native controls, and use
`hoi4-scripted-gui` for actual live previews. A shelf image does not establish
legal script scopes, action costs, tooltips, or current game-version behavior.
