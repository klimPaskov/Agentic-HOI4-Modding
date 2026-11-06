# HOI4 Feature Planning: Spec output and packaging

Part of the [hoi4-feature-planning](../SKILL.md) skill. Read before choosing the spec's shape, splitting it into files, writing the localisation handoff or packaging the output zip.

## 11. Specification shape

Do not force the specification into a fixed template.

Choose the structure that best fits the feature idea.

The specification should still be easy for a coding agent to use. Use clear headings, explain the logic in a natural order, and make sure important design decisions are not buried.

For major features, split the spec into parts if needed. Do not compress deep design just to fit one file.

Only include sections for surfaces that exist or that need design. If a researched text package, custom presentation surface, focus tree, custom country, achievement set, asset family, or other major surface is absent, omit that section instead of writing that it is absent. Because negative notes create noise and can mislead later agents into thinking the absence is a designed feature.

## 12. Depth, file splitting, and internal resume notes

Read [`references/specification-delivery.md`](specification-delivery.md) when shaping, splitting, or resuming a long specification, or writing an improvement-loop expansion spec. It contains the complete standard for this section and its subsections.

## Improvement-loop expansion specs

Read [`references/specification-delivery.md`](specification-delivery.md) when shaping, splitting, or resuming a long specification, or writing an improvement-loop expansion spec. It contains the complete standard for this section and its subsections.

## General localisation handoff

When a spec includes text-bearing content, give a localisation handoff, not final copy.

The handoff should list each needed text surface and describe its direction:

- feature title direction
- feature description direction
- option reaction direction
- news or report direction
- decision name and description direction
- focus name and description direction
- achievement title and description direction
- GUI label direction
- feature-detail and feature-log wording direction
- dynamic placeholders the coding agent should use
- research gates for quotes, slogans, songs, films, books, speeches, scriptures, proverbs, or other source-dependent references

The coding agent writes the final in-game text during implementation. The planning spec should not provide final prose for the coding agent to paste.

The planning agent should preserve the open structure of the addendum where that helps the idea. Use tables, route maps, prose, diagrams, or country package matrices only when they make the design easier to implement. Do not convert every improvement into a rigid checklist.

When an improvement addendum proposes formables, scripted GUI, animated sprites, animated portraits, or hidden routes, the final spec pack should carry those ideas into the relevant files instead of leaving them isolated. The core spec explains why the expansion matters. The decision and focus files explain how the player reaches it. The asset prompt explains the static and animated visual work. The coding prompt and goal prompt tell the implementation agent to wire and validate it.


## 18. Output rules

The feature specification itself should be created as Markdown files.

Full feature or feature specification output belongs under `docs/specs/<feature_slug>/`. This is the source-of-truth design folder for the feature spec pack.

Subagent planning addenda, audit follow-up plans, implementation notes, and temporary handoffs belong under `docs/plans/<feature_slug>/`. The plans folder is a working area. Accepted plan content should be folded into the relevant spec under `docs/specs/` when the final source-of-truth spec is updated.

Do not create new feature specs, addenda, prompt packages, or extracted handoffs under `docs/planning/`, `planning/`, or any other planning folder. If a prompt says "planning folder", interpret that as `docs/plans/` for subagent plans and `docs/specs/` for source specs unless the user explicitly provides a different path.

The spec file should contain only the feature specification.

Do not put the asset prompt, text and audio research prompt, coding-agent prompt, or goal prompt inside the spec file.

Keep planning files readable as design handoffs, not implementation blueprints. Prefer route purpose, player-facing behavior, balance intent, asset direction, AI intent, and acceptance criteria. Avoid long technical tables, exact constant lists, full scripted-effect recipes, exhaustive file inventories, parser-level implementation notes, and detailed code wiring. The specs you create are not implementation oriented. You do not give implementation guidance, you are just handing off ideas.

Create sequential files:

- `<feature_slug>_spec_part_1_core.md`
- `<feature_slug>_spec_part_2_<theme>.md`
- `<feature_slug>_spec_part_3_<theme>.md`
- and more as needed

Do not repeat earlier sections unless needed for clarity.


## 18.1 Final zip package requirement

The final output should be delivered as one zip file that contains every necessary file for the planning handoff.

The zip should include, when relevant:

- all spec Markdown files
- focus-tree path spec parts
- optional focus tree path diagrams or route sketches when useful
- asset prompt file
- text and audio research prompt file
- achievement prompt file
- coding-agent prompt file
- goal prompt file
- research notes or bibliography files
- any country package matrices, AI matrices, decision maps, or acceptance criteria files created separately

Do not make the user collect many loose files manually. The main deliverable should be a single zip package.

Use a clear package name such as:

`feature_slug_planning_package.zip`

The package should have a clean internal structure, for example:

```text
specs/
prompts/
focus_graphs/
research/
matrices/
```

The goal prompt inside the package must still be 3500-4000 characters.
The extracted zip should be placed in `docs/specs/<feature_slug>/` when it is the source spec pack. If the zip contains only subagent plans, follow-up handoffs, or audits, place it under `docs/plans/<feature_slug>/`.

