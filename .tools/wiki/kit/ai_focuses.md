# AI focuses

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="34354" sources="common/ai_focuses/ common/ai_strategy_plans/ common/technology_tags/ common/country_leader/00_traits.txt common/ideas/italy.txt common/ai_strategy/_documentation.md documentation/modifiers_documentation.md documentation/triggers_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 8 vanilla files in `common/ai_focuses/`, the nine `ai_focus_*_factor` modifiers, historical focus lists in the strategy plans and the technology category list.
- Kit blocks added: `ai-focus-ids-1193` (real block ids, modifier names, links to production planning), `ai-focus-research-format` (what a vanilla file holds and which keys are valid), `ai-focus-historical-moved`.
- Errors found: the focus called "Defensive" here is `defense` in files and modifier names; `ai_focuses` files hold only `research` weights, not national focus lists; the historical focus list moved into `ai_strategy_plans` (`ai_national_focuses`).
- Gaps left: the default values quoted for each focus (50 at peace, 100 at war and so on) are engine constants that no game file shows, so they stay unverified; what the `defensive` and `offensive` research keys do is not documented.
**1.19.4.1 re-check (2026-11-01).** Five statements depended on files the update changed (country leader traits, the Italian ideas, technology categories, strategy plans and the AI strategy documentation), and all five were re-measured. One number moved: plan files that test `is_historical_focus_on = yes` went from 72 to 70. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="ai-focus-ids-1193" at="section:focus-types" -->
Names of the nine AI focuses as the game files spell them. The section titles below are prose names; scripts use these ids. All rows: [vanilla-confirmed 1.19.3] `common/ai_focuses/generic.txt` (block ids), [docs] `documentation/modifiers_documentation.md` (the nine modifiers, category `ai`, one decimal).

| Section title | Block id in `common/ai_focuses` | Modifier |
| --- | --- | --- |
| Defensive | `ai_focus_defense` | `ai_focus_defense_factor` |
| Aggressive | `ai_focus_aggressive` | `ai_focus_aggressive_factor` |
| War production | `ai_focus_war_production` | `ai_focus_war_production_factor` |
| Military advancements | `ai_focus_military_advancements` | `ai_focus_military_advancements_factor` |
| Peaceful | `ai_focus_peaceful` | `ai_focus_peaceful_factor` |
| Naval | `ai_focus_naval` | `ai_focus_naval_factor` |
| Naval air | `ai_focus_naval_air` | `ai_focus_naval_air_factor` |
| Aviation | `ai_focus_aviation` | `ai_focus_aviation_factor` |
| Military equipment | `ai_focus_military_equipment` | `ai_focus_military_equipment_factor` |

- `ai_focus_defensive` and `ai_focus_production_factor` appear in no documentation, in no live vanilla script (the second only as a commented line) and in no `hoi4.exe` string, so do not use them; use the ids above. [vanilla-confirmed 1.19.4.1] `common/country_leader/00_traits.txt`.
- Vanilla applies the modifiers in a few places: `ai_focus_aggressive_factor = 0.5` in 4 country leader traits and 1 Italian idea, `ai_focus_aggressive_factor = 1` in another Italian idea, and `ai_focus_defense_factor = 0.5` in 1 trait. [vanilla-confirmed 1.19.4.1] `common/country_leader/00_traits.txt`, `common/ideas/italy.txt`.
- The aviation and naval air focus values also steer air production: the AI strategy documentation multiplies the number of wanted land-based planes by the hard-coded aviation focus value (after `ai_focus_aviation_factor`) and the wanted carrier planes by the naval air focus value (after `ai_focus_naval_air_factor`). [docs] `common/ai_strategy/_documentation.md`.
<!-- kit:end id="ai-focus-ids-1193" -->

<!-- kit:begin id="ai-focus-research-format" at="section:research-weights" -->
What vanilla `common/ai_focuses/` holds in 1.19.4.1. All lines: [vanilla-confirmed 1.19.4.1] `common/ai_focuses/*.txt`, `common/technology_tags/00_technology.txt`.

- 8 files: `generic.txt` (block ids `ai_focus_<name>`) and one per country with its own weights (`ENG`, `FRA`, `GER`, `ITA`, `JAP`, `SOV`, `USA`; block ids `ai_focus_<name>_<TAG>`, for example `ai_focus_naval_USA`). Each block holds only `research = { <key> = <weight> }`. No block holds national focuses.
- A country file replaces the whole generic block for that country, so a country block should list every research key it still wants. Not confirmed by a test [unverified].
- Research keys in vanilla are technology categories from `common/technology_tags/00_technology.txt`, such as `armor`, `artillery`, `industry`, `electronics`, `infantry_weapons`, `radar_tech`, `naval_doctrine`, `land_doctrine`, `air_doctrine`, `jet_technology`, `nuclear`, `para_tech`, `dd_tech` to `ss_tech`. Two keys are not categories: `defensive` (weight 5.0 in the defense block) and `offensive` (5.0 in the aggressive block). What they do is not documented.
- Weights are plain numbers; doctrine keys use large ones (`land_doctrine = 100.0`, `naval_doctrine = 100.0`, `air_doctrine = 50.0` generic, 75.0 for the USA). The wiki says only that these files control how much each focus affects research. Reading a weight as a multiplier on the research score of every technology in that category is [unverified].
<!-- kit:end id="ai-focus-research-format" -->

<!-- kit:begin id="ai-focus-historical-moved" at="section:historical-focuses-1" -->
In 1.19.4.1 historical focus lists are written in strategy plans, not in `ai_focuses`. The only `ai_historical_focus_list_USA` in vanilla sits in `common/ai_focuses/USA.txt`, and every line of it is commented out. Live lists are the `ai_national_focuses = { ... }` blocks of `common/ai_strategy_plans/*.txt` (124 plan files hold one; 70 plan files test `is_historical_focus_on = yes`, a trigger documented as "check if the historical focus is active"). See [AI modding](ai_modding.md#ai-strategy-plans) for the plan format and `focus_factors`. [vanilla-confirmed 1.19.4.1] `common/ai_focuses/USA.txt`, `common/ai_strategy_plans/`; [docs] `documentation/triggers_documentation.md` (`is_historical_focus_on`). That the string `ai_historical_focus_list` still exists in `hoi4.exe` does not show that the old block is read. In a test the old block was still read: an `ai_historical_focus_list_<TAG>` block in `common/ai_focuses` loaded with no log line, and each of the four generic-tree countries that had one started the focus it names first (TIB and NEP `aviation_effort`, YEM and SAU `army_effort`) by day 3. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, game.log read. The controls without a list started `industrial_effort` (OMA, MON) and `army_effort` (LIB), so the army pair is weaker evidence than the aviation pair. POL did not follow its list because its vanilla historical plan was still loaded (`POL_complete_april_constitution`), so that run does not say which source wins.
<!-- kit:end id="ai-focus-historical-moved" -->
