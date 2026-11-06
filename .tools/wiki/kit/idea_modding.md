# Idea modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="99295" sources="common/ideas/ common/idea_tags/ interface/ dlc/ common/countries/ documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md common/national_focus/ common/decisions/ events/ history/" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 213 files in `common/ideas/` (6,508 ideas, parsed), `common/idea_tags/00_idea.txt`, the sprites in `interface/` and `dlc/*/interface/`, the effects, triggers and modifiers documentation, and `hoi4.exe` strings.
Kit blocks added: picture counts and `GFX_idea_unknown`, hidden category, effect and trigger syntax, modifier block keys, rule names, category defaults (corrects footnote a and the `removal_cost` default), idea keys the wiki omits, category and slot structure, slot sprites and grid sizes, cost-factor modifiers.
Gaps left: the load-order claims in "Modifying cost of a slot", the `on_add` timing and the `allowed` check timing are engine behaviour that script cannot show. The "to be added" stub marker is a false positive (ordinary prose). `ZZZ_idea_slot`, `designer_category`, `law_category` are placeholder names in the wiki examples, not vanilla names.
**1.19.4.1 re-check (2026-11-01).** About 40 statements depended on files the update changed (25 idea files, the interface files and the vanilla-wide use counts), and all were re-measured. Numbers that moved: ideas 6,508 to 6,515, modifier blocks 4,605 to 4,611, the picture and sprite counts, `hidden_ideas` 297 to 291, `removal_cost` 3,764 to 3,767, the `add_ideas`, `swap_ideas`, `has_idea`, `set_rule` and `has_rule` counts, and `navy_spirit_` files 4 to 6; the old `equipment_bonus` and `ai_will_do` counts were blocks, not ideas. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="idea-picture-vanilla" at="section:picture" -->
How vanilla fills `picture`, counted over the 6,515 ideas in the 213 files of `common/ideas/`.

- 6,110 ideas set `picture`. 6,088 of them give the bare name (`picture = new_economic_policy`), and 6,046 of those match a declared sprite named `GFX_idea_<value>` (here `GFX_idea_new_economic_policy` in `interface/ideas.gfx`). What matters is that a sprite with that full name is declared in some loaded `.gfx` file; vanilla also declares idea sprites in `dlc/*/interface/*.gfx`. [vanilla-confirmed 1.19.4.1] `common/ideas/`, `interface/`, `dlc/*/interface/`.
- 22 vanilla ideas write a full name (`picture = GFX_idea_...`). For 15 of them a sprite called `GFX_idea_<idea id>` also exists, so the name fallback would find a sprite anyway. The other 7 only work if the engine accepts a full sprite name. [vanilla-confirmed 1.19.4.1] `common/ideas/`, `interface/`. Whether it does is [unverified], so write the bare name.
- 405 ideas set no `picture`. 272 of them have a sprite called `GFX_idea_<idea id>`, and 119 of the rest are in `hidden_ideas`, which never show. [vanilla-confirmed 1.19.4.1] `common/ideas/`.
- 385 ideas set a bare `picture` that has its own sprite and also have a sprite named after the idea id. The files do not show which of the two the game displays. [vanilla-confirmed 1.19.4.1] `common/ideas/`, `interface/`.
- `GFX_idea_unknown` is declared in `interface/countrydiplomacyview.gfx` (texture `gfx/interface/ideas/idea_unknown.dds`) and is the placeholder icon several vanilla GUI files use. [vanilla-confirmed 1.19.4.1] `interface/*.gui`. That the engine falls back to it for an idea with no usable sprite is [unverified].
- Culture variants exist in vanilla: 160 sprites end in `_2d`, all for `generic_*` pictures, 20 for each of `asian_2d`, `commonwealth_2d`, `eastern_european_2d`, `middle_eastern_2d`, `sami_2d`, `southamerican_2d`, `western_european_2d` and 19 for `african_2d`. The same eight values are the `graphical_culture_2d` values in `common/countries/`; one sprite uses `middle_african_2d`, which no country uses. [vanilla-confirmed 1.19.4.1] `interface/`, `common/countries/`.
<!-- kit:end id="idea-picture-vanilla" -->

<!-- kit:begin id="idea-implementation-syntax" at="section:implementation" -->
Idea effects and triggers in 1.19.4.1. All of them run in country scope. All rows: [docs] syntax from `documentation/effects_documentation.md` and `documentation/triggers_documentation.md`; use counts [vanilla-confirmed 1.19.4.1] over `common/`, `events/` and `history/`.

| Name | Kind | Syntax and notes |
| --- | --- | --- |
| `add_ideas`, `remove_ideas` | effect | `add_ideas = id` or `add_ideas = { id_a id_b }`. Vanilla writes `add_ideas` 2,899 times as a single value and 473 times as a block. |
| `swap_ideas` | effect | `swap_ideas = { remove_idea = a add_idea = b }`. The documentation also lists optional `days` (duration of the new idea) and `add_days` (change to that duration), but all 2,294 vanilla uses have only the two required keys. The documentation's syntax line says `swap_idea`; no vanilla file uses that spelling. |
| `add_timed_idea` | effect | `add_timed_idea = { idea = id days = 30 }`. `years`, `months` and `days` can be combined, at least one is required, and each accepts a variable. Vanilla: 1,730 uses with `days`, 4 with `months`. |
| `modify_timed_idea` | effect | `modify_timed_idea = { idea = id days = 60 }` lengthens the timer; a negative value shortens it. Same `years`, `months`, `days` keys. 16 vanilla uses. |
| `remove_ideas_with_trait` | effect | `remove_ideas_with_trait = trait_id`. 1 vanilla use (`events/ElectionEvents.txt`). |
| `show_ideas_tooltip` | effect | `show_ideas_tooltip = id` prints an idea's tooltip inside an effect tooltip; vanilla uses it for advisor ideas in focus rewards. 1,232 vanilla uses. |
| `has_idea` | trigger | `has_idea = id`. 7,414 vanilla uses. |
| `has_idea_with_trait` | trigger | `has_idea_with_trait = trait_id`. 326 vanilla uses. |
| `has_allowed_idea_with_traits` | trigger | `{ idea = trait_id characters = yes }`, with optional `limit` and `ignore`. 15 vanilla uses, all in `common/ideas/zzz_generic.txt` and `history/general/generic_advisors.txt`. `has_available_idea_with_traits` is documented the same way but unused in vanilla. |
| `amount_taken_ideas` | trigger | `{ amount < 3 slots = { political_advisor } }`, with optional `categories = { military_staff }`. Does not count national spirits, hidden ideas or categories with `law = yes`. 137 vanilla uses. |
<!-- kit:end id="idea-implementation-syntax" -->

<!-- kit:begin id="idea-modifier-block-keys" at="section:modifiers" -->
What vanilla puts inside idea blocks, counted over 4,611 `modifier` blocks and 6,515 ideas in `common/ideas/`.

- Every key in a vanilla `modifier` block is a numeric modifier except two: `custom_modifier_tooltip = LOC_KEY` (183 uses) adds an extra tooltip line from a localisation key, and `hidden_modifier = { ... }` (2 uses, `common/ideas/czechoslovakia.txt` and `italy.txt`) wraps modifiers that apply without being listed. `custom_modifier_tooltip` is the only non-numeric scalar. [vanilla-confirmed 1.19.4.1] `common/ideas/`.
- `research_bonus` is never inside `modifier` (0 of 4,611 blocks). It is an idea-level key: 1,086 ideas use it, with 37 different technology category names. `equipment_bonus` is also idea-level (653 blocks in 637 ideas); `instant = yes` appears 945 times inside it. [vanilla-confirmed 1.19.4.1] `common/ideas/`.
- `targeted_modifier` (481 uses) holds `tag = TAG` (479 blocks) and numeric modifiers; the only other non-numeric key is `custom_modifier_tooltip` (3 blocks). [vanilla-confirmed 1.19.4.1] `common/ideas/`.
<!-- kit:end id="idea-modifier-block-keys" -->

<!-- kit:begin id="idea-rule-notes" at="section:modifiers" -->
The `rule` table above, checked against vanilla and the game files.

- 47 vanilla ideas use a `rule` block. They use 8 rule names: `can_send_volunteers` (20 entries), `can_access_market` (8), `can_create_factions` (6), `can_decline_call_to_war` (6), `can_join_factions` (4), `can_join_opposite_factions` (3), `can_boost_other_ideologies` (2), `can_guarantee_other_ideologies` (1). One block also has `desc`, which is a description key, not a rule. [vanilla-confirmed 1.19.4.1] `common/ideas/`.
- `can_join_factions_not_allowed_diplomacy` is in no vanilla script, so do not rely on it. [vanilla-confirmed 1.19.4.1] 26 of the 27 names in the table are strings in `hoi4.exe`, and this one is not. [unverified] The idea loader reports it: in an idea's `rule` block it drew "unknown rule 'can_join_factions_not_allowed_diplomacy'", the same message as a made-up name. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read at load.
- `can_declare_war_without_wargoal_when_in_war`, `can_not_build_buildings` and `can_occupy_non_war` are in `hoi4.exe` [unverified] but in no active vanilla script (the first appears once, in a commented-out line in `common/national_focus/uruguay.txt`). [vanilla-confirmed 1.19.4.1] All three load without an "unknown rule" line in an idea's `rule` block, so they are known rule keys. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read at load. Whether they have their effect as idea rules was not read: the `has_rule` readouts failed in that run, and no error is not proof that a rule works.
- The same names can be set at runtime. `set_rule = { desc = LOC_KEY can_not_declare_war = yes }` adds a rule to the country in scope and overrides the other sources, `clear_rule = { can_not_declare_war = yes }` removes a rule that `set_rule` added, and `has_rule = can_puppet` tests one. Vanilla: `set_rule` 502 uses, `clear_rule` 2, `has_rule` 68 [vanilla-confirmed 1.19.4.1]. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`
- `add_relation_rule_override` sets a rule for one target country (`target = TAG`) or for every country a named trigger matches (`trigger = name`), with an optional `usage_desc`. The documentation says only `can_send_volunteer` (sic) and `can_access_market` are supported there. 47 vanilla uses. [docs] `documentation/effects_documentation.md`
- The table is not the full list of rule names: ideologies use a `rules` block (`can_force_government`, `can_puppet`, `can_lower_tension`, `can_host_government_in_exile`) and one special project uses `set_rule = { can_use_underway_replenishment = yes }`. [vanilla-confirmed 1.19.3] `common/ideologies/00_ideologies.txt`, `common/special_projects/projects/naval_projects.txt`.
<!-- kit:end id="idea-rule-notes" -->

<!-- kit:begin id="idea-hidden-category" at="section:hidden-ideas" -->
`hidden_ideas` is a category in `common/idea_tags/00_idea.txt` with `hidden = yes`, `cost = 0`, `removal_cost = -1` and `ledger = hidden`. [vanilla-confirmed 1.19.3] `common/idea_tags/00_idea.txt`. Vanilla has 291 ideas in 28 `hidden_ideas` blocks; 171 of them still set a `picture`, which is never shown. [vanilla-confirmed 1.19.4.1] `common/ideas/`.
<!-- kit:end id="idea-hidden-category" -->

<!-- kit:begin id="idea-category-args-vanilla" at="section:idea-category-arguments" -->
In vanilla, `designer = yes` always sits on the category block, never on an idea: 161 category blocks in 51 files, 0 ideas. `law = yes` is on 4 category blocks (`economy` twice, `trade_laws`, `mobilization_laws`) and `use_list_view = yes` on 3. [vanilla-confirmed 1.19.4.1] `common/ideas/`.
<!-- kit:end id="idea-category-args-vanilla" -->

<!-- kit:begin id="idea-cost-defaults" at="section:additional-arguments-1" -->
The default `cost` and `removal_cost` come from the idea's category, so they are not always 150 and 0. Table: [vanilla-confirmed 1.19.3] `common/idea_tags/00_idea.txt`.

| Category | Default `cost` | Default `removal_cost` |
| --- | --- | --- |
| `government`, `research_production`, `military_staff` | 150 | 0 |
| `country` (national spirits), `hidden_ideas` | 0 | -1 |
| `academy_spirit`, `naval_academy_spirit` | 20 | -1 |
| `army_spirit`, `navy_spirit` | 35 | -1 |
| `division_command_spirit`, `naval_command_spirit`, `air_force_academy_spirit`, `air_force_spirit`, `air_force_command_spirit` | 50 | -1 |

An idea's own `cost` or `removal_cost` replaces the default. 3,730 of the 3,767 vanilla ideas that set `removal_cost` write `-1` (not removable by hand) and the other 37 write `10`, all in the `industrial_concern` and manufacturer slots. [vanilla-confirmed 1.19.4.1] `common/ideas/`.

Vanilla use of idea keys, including three the page does not list (`ai_will_do`, `default`, `cancel_if_invalid`). All rows: [vanilla-confirmed 1.19.4.1] `common/ideas/`.

| Key | Vanilla use |
| --- | --- |
| `ai_will_do` | 1,052 ideas with 1,055 blocks (three ideas write it twice): laws, advisors, designers and officer corps spirits. Body is `factor = n` alone (857) or `base = n` alone (63), and the other 135 blocks add `modifier` blocks. |
| `default = yes` | 5 ideas: `civilian_economy`, `export_focus`, `volunteer_only`, `ETH_chitet_law`, `ETH_chitet_law_peace_time`. What it does is not stated in the files. [vanilla-confirmed 1.19.4.1] It does not refill an empty slot, see the note below the table. Any other engine effect of `default = yes` is [unverified]. |
| `cancel_if_invalid = no` | 31 laws in `economy`, `trade_laws` and `mobilization_laws`; the value is always `no`. [vanilla-confirmed 1.19.4.1] Its exact effect is not stated in the files. [unverified] In a test, a law with `cancel_if_invalid = no` stayed after its condition failed, while the same law with the default was removed within a day (both present right after the flag was set, only the `no` law at day 1 and day 2). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, laws added by effect, game.log read. Only the first two days were read, and a stand-in country was used. |
| `level` | 11 ideas, all in `mobilization_laws`, with values 1 to 7. |
| `ledger` | 475 ideas. All 234 `high_command` and all 145 `theorist` ideas set it, because those two slots are `invalid` in `slot_ledgers`; the officer corps spirits set it too. Values used: `army`, `navy`, `air`. |
| `traits` | 2,013 ideas. 2,009 are in the advisor, chief, theorist, designer and industrial concern slots; 4 are national spirits (`george_v`, `ENG_george_vi`, `HOL_wilhelmina`, `SWE_gustaf_v_idea`). |

`default = yes` does not refill an empty slot. GER started with the economy law `partial_economic_mobilisation`, the console `add_ideas war_economy` replaced it ("Added 1 ideas"), and the effect `remove_ideas = war_economy` then removed it and left no economy law, so the politics view showed "Click to add Economy Law" even though `civilian_economy` has `default = yes`. The console `remove_ideas war_economy` printed "Removed 0 ideas" and the law stayed. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console replies and the politics view.
<!-- kit:end id="idea-cost-defaults" -->

<!-- kit:begin id="idea-categories-vanilla" at="section:categories" -->
What the vanilla file `common/idea_tags/00_idea.txt` shows. All items: [vanilla-confirmed 1.19.4.1] `common/idea_tags/00_idea.txt`, `common/ideas/`.

- It defines 14 categories. `slot` and `character_slot` lines can repeat, and each repetition is one more slot: `government` has `slot = mobilization_laws`, `trade_laws`, `economy` and three `character_slot = political_advisor` lines; `military_staff` has `army_chief`, `navy_chief`, `air_chief` and three `high_command` lines.
- The wiki does not mention `type`. Vanilla sets `type = national_spirit` on `country`, `army_spirit` on `academy_spirit`, `army_spirit` and `division_command_spirit`, `navy_spirit` on the three naval spirit categories and `air_spirit` on the three air force ones. The strings are in `hoi4.exe` and the three `*_spirit` types are the targets of the `<IdeaCategory>_category_type_cost_factor` modifier.
- The blocks inside `ideas = { }` are named by category or by slot. The 24 names vanilla uses are category names for categories without slots (`country`, `hidden_ideas`) and for the spirit categories (each has a slot of the same name), slot names (`economy`, `trade_laws`, `mobilization_laws`, `tank_manufacturer`, `naval_manufacturer`, `aircraft_manufacturer`, `materiel_manufacturer`, `industrial_concern`) and character slot names (`political_advisor`, `theorist`, `army_chief`, `navy_chief`, `air_chief`, `high_command`).
- Vanilla `slot_ledgers`: `army_chief = army`, `navy_chief = navy`, `air_chief = air`, `tank_manufacturer = army`, `naval_manufacturer = navy`, `aircraft_manufacturer = air`, `mobilization_laws = civilian`, and `theorist` and `high_command` as `invalid`. `ZZZ_idea_slot`, `XXX_idea_slot`, `law_category` and `designer_category` in the wiki examples are placeholders; none exists in vanilla.
<!-- kit:end id="idea-categories-vanilla" -->

<!-- kit:begin id="idea-slot-sprites" at="section:gfx-and-gui" -->
Checks against the vanilla interface files. All items: [vanilla-confirmed 1.19.4.1] `interface/countrypoliticsview.gui`, `interface/countrypoliticsview.gfx`, `interface/`.

- `country_politics_idea_category_entry` has `ideas_grid` with `slotsize = { width = 80 height = 64 }` and `max_slots = { x = 7 y = 1 }`, as the wiki says. `GFX_idea_categories` has `noOfFrames = 6`.
- Vanilla declares `GFX_idea_slot_<slot>` for 11 slots: `air_chief`, `aircraft_manufacturer`, `army_chief`, `high_command`, `industrial_concern`, `materiel_manufacturer`, `naval_manufacturer`, `navy_chief`, `political_advisor`, `tank_manufacturer`, `theorist`. The three law slots have none. The prefix `GFX_idea_slot_` is also a string in `hoi4.exe`.
<!-- kit:end id="idea-slot-sprites" -->

<!-- kit:begin id="idea-cost-factor-modifiers" at="section:modifying-cost-of-a-slot" -->
The documented modifiers behind this section. All items: [docs] `documentation/modifiers_documentation.md`; use counts are [vanilla-confirmed 1.19.4.1] `common/`.

- The documentation calls the modifier `<IdeaGroup>_cost_factor` (country category, number). Its 25 valid group names are `academy_spirit`, `air_chief`, `air_force_academy_spirit`, `air_force_command_spirit`, `air_force_spirit`, `aircraft_manufacturer`, `army_chief`, `army_spirit`, `country`, `division_command_spirit`, `economy`, `hidden_ideas`, `high_command`, `industrial_concern`, `materiel_manufacturer`, `mobilization_laws`, `naval_academy_spirit`, `naval_command_spirit`, `naval_manufacturer`, `navy_chief`, `navy_spirit`, `political_advisor`, `tank_manufacturer`, `theorist` and `trade_laws`. Vanilla uses it for the 14 law, advisor, chief, theorist, designer and concern slots, for example `political_advisor_cost_factor` (174 uses), `economy_cost_factor` (158), `mobilization_laws_cost_factor` (146) and `theorist_cost_factor` (10). It never uses the `country_`, `hidden_ideas_` or spirit-category forms.
- `<IdeaCategory>_category_type_cost_factor` is a separate documented modifier for the three category types `army_spirit`, `navy_spirit` and `air_spirit`. The wiki does not mention it. Vanilla uses `navy_spirit_` in 6 files and `army_spirit_` and `air_spirit_` in 2.
- `disabled_ideas` is a documented boolean country modifier with no description. [docs] `documentation/modifiers_documentation.md`. Vanilla has one use, `disabled_ideas = 1` inside an idea in `common/ideas/spain_republic.txt`. [vanilla-confirmed 1.19.4.1] What it disables is not stated. [unverified] It does not switch off another national spirit: with an idea carrying `disabled_ideas = 1` added next to a +0.5 `political_power_gain` spirit, the modifier read 0.5 while both were present, 0.5 after the disabling idea was removed, and 0 once both were gone. No error.log line named `disabled_ideas`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, modifier read in game.log. Only one other spirit in the country category was read, through one modifier. What it does to other idea types (laws, advisors) was not tested.
<!-- kit:end id="idea-cost-factor-modifiers" -->

<!-- kit:begin id="idea-notes-correction" at="section:notes" -->
Footnote a is out of date: the default price depends on the category and is not 150 everywhere in 1.19.3. See the default table under "Additional arguments". [vanilla-confirmed 1.19.3] `common/idea_tags/00_idea.txt`.
<!-- kit:end id="idea-notes-correction" -->
