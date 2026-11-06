# HOI4 AI Strategies: Sources and open questions

Part of the [hoi4-ai-strategies](../SKILL.md) skill. Read first to find the authoritative text and vanilla precedent for each AI surface, or before relying on a point the sources leave open.

## Contents

- Source map: where the authoritative text lives
- Decision procedure: which mechanism for which goal
- Weight semantics: ai_will_do, ai_chance, base, add, factor
- common/ai_strategy: structure, lifecycle, stacking
- add_ai_strategy and flag-gated strategies
- Strategy families and the common tokens
- AI strategy plans
- AI focuses, research weights, and AI areas
- Other AI systems (templates, equipment, navy, theaters, peace) in the reference file
- Debugging and verification
- Repository conventions
- Common mistakes
- Unverified or conflicting points

Deeper material lives in two reference files inside this skill folder:

- `references/strategy-token-catalog.md`: read when you need the exact parameters, ids, value semantics, or unit-ratio arithmetic of a specific `ai_strategy` type (production, market, front, navy, intelligence, research, XP and PP spend).
- `references/other-ai-systems.md`: read when you touch `common/ai_templates`, `common/ai_equipment`, `common/ai_navy`, `common/ai_faction_theaters`, `common/peace_conference/ai_peace`, `ai_attitudes`, or the AI-facing blocks of factions, autonomy, and scripted diplomatic actions.

## Source map

`GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md`.
`WIKI` means the offline snapshot in `hoi4_wiki/` at the mod root.
Installed documentation is more authoritative than the wiki; where they disagree, follow the installed file and record the conflict.

| Topic | Authoritative text | Vanilla precedent |
| --- | --- | --- |
| Every `ai_strategy` token, value semantics, unit ratios | `GAME/common/ai_strategy/_documentation.md` (updated 2024-11) | `GAME/common/ai_strategy/default.txt` (generic), `GER.txt`, `FRA.txt`, `INS.txt` (reversed), `SOV.txt` (front_control) |
| AI strategy plans, ai_will_do math, ai_chance, AI areas | `WIKI/ai_modding.md` (sections MTTH blocks, AI strategies, AI areas, AI strategy plans) | `GAME/common/ai_strategy_plans/GER_historical_strategy_plan.txt`, `ENG_historical_strategy_plan.txt` |
| Research and focus weighting | `WIKI/ai_focuses.md` | `GAME/common/ai_focuses/generic.txt`, `GER.txt` |
| Focus `ai_will_do` and the plan override | `WIKI/national_focus_modding.md` (AI will do, AI strategy plans) | `GAME/common/national_focus/*.txt` |
| Decision `ai_will_do` | `WIKI/decision_modding.md` (AI section) | `GAME/common/decisions/political_decisions.txt` |
| Event option `ai_chance` | `WIKI/event_modding.md` (options) | `GAME/events/Germany.txt` |
| Technology `ai_will_do`, `ai_research_weights` | `WIKI/technology_modding.md` | `GAME/common/technologies/*.txt` |
| AI templates | `GAME/common/ai_templates/_documentation.md` (updated 2024-08) | `GAME/common/ai_templates/generic.txt`, `templates_ENG.txt` |
| AI equipment designer | `GAME/common/ai_equipment/_documentation.md` | `GAME/common/ai_equipment/generic_tank.txt` |
| Goal-based naval AI | `GAME/common/ai_navy/_documentation.md`, `ai_navy/taskforce/_documentation.md` | `GAME/common/ai_navy/goals/goals_generic.txt`, `fleet/generic_fleet_templates.txt` |
| Faction theaters | `GAME/common/ai_faction_theaters/_documentation.md` | `ai_faction_theaters.txt` in the same folder |
| AI peace desires | `GAME/common/peace_conference/ai_peace/_documentation.md` | `GAME/common/peace_conference/ai_peace/00_misc.txt` |
| Faction AI (rules, goals, initiative spend) | `GAME/common/factions/_documentation.md` | `GAME/common/factions/rules/joining_rules.txt` |
| Effects and triggers touching AI | `GAME/documentation/effects_documentation.md` (`add_ai_strategy`, `ai_message`), `triggers_documentation.md` (`is_ai`, `ai_irrationality`, `ai_has_role_division`, `ai_has_role_template`, `ai_liberate_desire`, `ai_wants_divisions`) | |
| AI modifiers (`ai_focus_*_factor`, `ai_desired_divisions_factor`, `ai_get_ally_desire_factor`, `ai_join_ally_desire_factor`, `ai_call_ally_desire_factor`, `ai_badass_factor`, `ai_license_acceptance`) | `GAME/documentation/modifiers_documentation.md`, section "Modifiers for scope ai" | |
| AI tuning constants | `GAME/common/defines/00_defines.lua`, table `NAI` | |
| Debug commands | `GAME/documentation/console_commands_documentation.md` | |

Use the hoi4 MCP reference routes (`hoi4_reference_context` with surface `ai`, `hoi4_reference_search`, `hoi4_reference_read`, `hoi4_source_lookup`) to cite exact line spans.
If a route fails once, retry once with narrower input, then read the local file directly.

## Unverified or conflicting points

- Repeated `add_ai_strategy` with the same type and id: replacement versus accumulation is not documented in the installed files.
- `reversed` / `enable_reverse` holder and target scopes are described loosely; vanilla `INS.txt` and `FRA.txt` use them in ways that need in-game confirmation.
- The wiki states `allowed` is checked only at game start and `abort` blocks adding; the installed documentation only states that `abort` deactivates. Behaviour for strategies added by `add_ai_strategy` with `abort` blocks is not described.
- `hoi4_probability_inspect` returned an invalid-arguments error when called with only an adapter name and no source selector; a source or candidate pool is evidently required, but the selector shape was not confirmed in this review.
- Many numeric hardcoded behaviours (for example how conquer weights compare to force factors in declaring war) live in engine code; only `NAI` defines are visible.
