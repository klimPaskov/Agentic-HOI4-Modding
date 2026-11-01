# Guidance audit of 2026-10-31

This audit covers the guidance changes made with the generator registry (commit `35fcffa`) and the following guidance pass: the upfront consultation rule, the `hoi4-investigate` skill, the feasibility check, evidence tags, and the first slimming of `CLAUDE_template.md`. The rule for slimming is that no instruction is lost. Text is moved or deduplicated, never dropped, and every removed sentence is listed here with the place that now holds it.

## Method

Every guidance file changed in the pass was compared with commit `35fcffa`, split into sentences, and each sentence missing from the new file was searched word for word in every other `.claude/` and `docs/` Markdown file. A sentence found elsewhere is listed as moved. Every other removed sentence was checked by reading and is listed below as covered (the skill already states the same instruction in its own words, with the line), changed (a deliberate rule change, with its source), or reworded in place.

## Template size

`CLAUDE_template.md` went from 59,559 bytes at `35fcffa` to 59,741 bytes, below the 60,000-byte single-read ceiling. The consultation stub, the `hoi4-investigate` routing line, the evidence-tag rule in Skill Maintenance and the reconciled MCP sentence were added. The space came from shortening three subagent routing bullets whose full rules live in `hoi4-subagents`.

## Moved word for word

| Sentence | From | Now in |
| --- | --- | --- |
| A parsed-object key recovered from a crash dump is an investigative lead, not proof that the named entry alone caused the crash. | `hoi4-debug-playtest` section 7 | `hoi4-investigate` section 5 |
| Shortening or removing it does not establish a cause without a successful controlled retest. | `hoi4-debug-playtest` section 7 | `hoi4-investigate` section 5 |
| Resolving an early parse crash can expose a large downstream error batch that earlier launches never reached, so distinguish newly observable errors from demonstrated patch regressions. | `hoi4-debug-playtest` section 7 | `hoi4-investigate` section 5 |
| Do not dismiss a new error introduced after the agent's own patch as pre-existing. Treat it as part of the current change set until disproven with evidence. | `hoi4-debug-playtest` section 7 | `hoi4-investigate` section 1 |
| Do not fix warnings by suppressing, deleting, or renaming content without understanding the gameplay consequence. | `hoi4-debug-playtest` section 8 | `hoi4-investigate` section 1 |

`hoi4-debug-playtest` now points to `hoi4-investigate` at both places.

## Covered by the skill the template routes to

The template keeps each routing decision (which agent, when) and points to the full rule.

| Removed from the template | Already stated in |
| --- | --- |
| The parent prompt must prove event ownership and name exact GUI identifiers, files, entry point, states, resolutions, assets, and handoff path. | `hoi4-subagents`, Event UI worker gate: the prompt contents and the ownership proof |
| The worker owns bounded layout implementation and the iterative MCP live-preview and comparison evidence required by `hoi4-scripted-gui`, while the parent and decision owner retain gameplay, costs, effects, AI, balance, final integration, and in-game validation. | `hoi4-subagents`, Event UI worker gate: what the worker owns, what the parent and decision worker retain, and the mandatory live-preview and comparison evidence |
| It must not audit event logs, event-detail frameworks, settings, super-event frameworks, shared registries, or unrelated existing UIs. | `hoi4-subagents`, Event UI worker gate: the same list "remain out of scope" |
| It patches documentation surfaces only, writes source-of-truth maps and resume packets, and does not edit gameplay files or spreadsheets. (documentation curator) | `hoi4-subagents`, the `hoi4_documentation_curator` routing paragraph |
| It creates concrete feature expansion addenda with research, historical connections, playable mechanics, and implementation surfaces for the main agent. (improvement planner) | `hoi4-subagents`, Improvement routing, and `hoi4-improvement-loop`, Feature loop improvement role |
| Use it after meaningful implementation tranches of major feature work, when several new mechanics need deeper connections. | Kept in the shortened template bullet, and in `hoi4-improvement-loop`, Deployment cadence |

The first sentence of each of the three bullets stays in the template, shortened or extended with the pointer.

## Deliberate rule changes

| Old text | New rule | Source |
| --- | --- | --- |
| If an indispensable design choice or input is missing, finish independent work and ask a focused question. | Ask once as Upfront consultation allows, after finishing independent work. The consultation itself is a new template subsection with its detail in `hoi4-feature-planning/references/consultation-questions.md` | FR-1, upfront questions rule |
| Source review and local checks can support completion when a tool is unavailable, but never describe them as MCP proof or live engine validation. | Same rule, plus: when a skill calls an MCP route mandatory and it is unavailable, record the blocker, report the evidence as missing, and an auditor marks the missing evidence unresolved, never passed | P11, resolving the contradiction between the template and the skills that call MCP evidence mandatory |
| (`hoi4_feature_completion_auditor`) record the exact blocker and mark the completion claim unresolved | record the exact blocker and mark that evidence item unresolved in the completion claim, never passed | Same contradiction, aligned with the template and `docs/systems/hoi4_agent_tools_mcp_integration.md` |
| (`hoi4-super-events`) reject the track or ask the user for the missing information | reject the track or add the missing information to the next batch of questions; reuse and longer tracks are asked in the upfront consultation | FR-1 |
| (`hoi4-frame-animation`) report a blocker or ask for permission to run a narrow exploration pass | the same, asked in the upfront consultation when the spec already shows the gap | FR-1 |

## Corrections from vanilla

The trap import compared each verified trap with the existing skill text and reported nine conflicts. Each was checked against the installed 1.19.3 game. Six kit rules were wrong and are corrected with their evidence:

| Old rule | Vanilla shows | Now |
| --- | --- | --- |
| `hoi4-decisions-missions`: narrow targeted decisions with a `state_trigger` value | `state_target` appears 236 times in `common/decisions` (202 `= yes`, 34 `= any_controlled_state`), `state_trigger` never | `state_target`, tagged `[vanilla-confirmed 1.19.3]` |
| `hoi4-map-states`: `add_building_construction` crashes on `supply_node` | 72 vanilla uses with `type = supply_node`, none with `rail_way` | Rails use `build_railway`. Supply hubs may use `add_building_construction` |
| `hoi4-map-states` map geometry: weather sizes `small\|large` | `map/weatherpositions.txt` has 452 `big` and 136 `small` rows | `small\|big` |
| `hoi4-ai-strategies`: `FORCE_CONCENTRATION_UNIT_RATIO_BASE` | Not in `common/defines/00_defines.lua`, which has `AIFC_UNIT_RATIO_BASE = 0.15` | `NAI.AIFC_UNIT_RATIO_BASE` |
| `hoi4-equipment`: internal equipment `type` values come from `_documentation.md` | `script_enum_equipment_category` in `common/script_enums.txt` has the 38 values | The enum is named as the source |
| `hoi4-equipment`: special project prototypes are covered by `special_projects_documentation.md` | Its keys appear in no vanilla file. The per-folder `documentation.md` files in `projects/`, `prototype_rewards/` and `specialization/` describe what vanilla uses | Those three files |

Three conflicts kept the kit rule:

- The trap about `definition.csv` line endings is wrong: vanilla `map/definition.csv` uses CRLF on every line, so the kit's rule stands and the trap was not imported.
- The peace `ai_desire` scale is stated as a percentage by `common/peace_conference/ai_peace/_documentation.md`, which matches the kit.
- `collection_size` stays as the kit states it, inclusive.

The two runtime questions behind the last two go to the `[unverified]` in-game notes on the wiki pages. One more conflict, whether the country leader role check runs per ideology or per ideology group, rests on executable strings only and stays as the kit states it until a game test.

## Not done in this pass

The largest skills (`hoi4-feature-assets` at 57,907 bytes, `hoi4-feature-planning`) were not slimmed. The 3D pipeline files were left to the session that owns them. The ComfyUI and vanilla-reference rule changes (decisions D3 and D4) land with the image generation server, because no agent tool can operate a ComfyUI endpoint yet.
