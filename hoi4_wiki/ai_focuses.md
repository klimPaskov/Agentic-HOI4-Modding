# AI focuses

*Offline snapshot of the Hearts of Iron IV Wiki page "AI focuses", revision 34354, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" revision="34354" sources="common/ai_focuses/ common/ai_strategy_plans/ common/technology_tags/ common/country_leader/00_traits.txt common/ideas/italy.txt common/ai_strategy/_documentation.md documentation/modifiers_documentation.md documentation/triggers_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 8 vanilla files in `common/ai_focuses/`, the nine `ai_focus_*_factor` modifiers, historical focus lists in the strategy plans and the technology category list.
- Kit blocks added: `ai-focus-ids-1193` (real block ids, modifier names, links to production planning), `ai-focus-research-format` (what a vanilla file holds and which keys are valid), `ai-focus-historical-moved`.
- Errors found: the focus called "Defensive" here is `defense` in files and modifier names; `ai_focuses` files hold only `research` weights, not national focus lists; the historical focus list moved into `ai_strategy_plans` (`ai_national_focuses`).
- Gaps left: the default values quoted for each focus (50 at peace, 100 at war and so on) are engine constants that no game file shows, so they stay unverified; what the `defensive` and `offensive` research keys do is not documented.
**1.19.4.1 re-check (2026-11-01).** Five statements depended on files the update changed (country leader traits, the Italian ideas, technology categories, strategy plans and the AI strategy documentation), and all five were re-measured. One number moved: plan files that test `is_historical_focus_on = yes` went from 72 to 70. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Focus Types](#Focus_Types)
  - [Defensive](#Defensive)
  - [Aggressive](#Aggressive)
  - [War production](#War_production)
  - [Military advancements](#Military_advancements)
  - [Peaceful](#Peaceful)
  - [Naval](#Naval)
  - [Naval air](#Naval_air)
  - [Aviation](#Aviation)
  - [Military equipment](#Military_equipment)
- [Historical focuses](#Historical_focuses)
- [Modding](#Modding)
  - [Focus factors](#Focus_factors)
  - [Research weights](#Research_weights)
  - [Historical focuses](#Historical_focuses_2)

---

AI focuses balance competing interests in several aspects of the game such as being more or less careful with attacks or prioritizing one field of research over another. Every AI country has a value for each of the focuses with higher values making the country focus more on that characteristic.

## Focus Types <a id="Focus_Types"></a>

<!-- kit:begin id="ai-focus-ids-1193" at="section:Focus_Types" -->
**Kit correction** Names of the nine AI focuses as the game files spell them. The section titles below are prose names; scripts use these ids. All rows: [vanilla-confirmed 1.19.3] `common/ai_focuses/generic.txt` (block ids), [docs] `documentation/modifiers_documentation.md` (the nine modifiers, category `ai`, one decimal).

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

### Defensive <a id="Defensive"></a>

Multiplied with PLAN_VALUE_TO_EXECUTE, defensive focus increases the threshold to execute battle plans. It increases the research priority of RADAR, construction and artillery among others.
It defaults to 50 during peace, 100 when being in a defensive war and 0 when being in an aggressive war. France has a +50% bonus due to Édouard Daladier's Stout Defender trait.

### Aggressive <a id="Aggressive"></a>

Aggressive focus decreases the threshold to execute battle plans, making the AI more likely to activate risky plans. It increases the research priority of synthetic refineries, motorization and armor.
It defaults to 50 during peace (fascist countries 75), 0 when being in a defensive war and 100 when being in an aggressive war. Italy has a +50% bonus due to the Vittoria Mutilata national idea.

### War production <a id="War_production"></a>

War production focus increases the research priority of industry and electronics techs to a lesser extent.
It defaults to 10 during peace (fascist countries 30) and 100 when at war.

### Military advancements <a id="Military_advancements"></a>

Military advancements focus increases the research priority for various advanced military techs like jets, night vision, nuclear etc.
It defaults to 25 times the number of research slots (capped at 100) when at war and is reduced by 25% when at peace.

### Peaceful <a id="Peaceful"></a>

Peaceful focus increases the research priority for industry and electronics.
It is 100 when at peace, 0 when at war.

### Naval <a id="Naval"></a>

Naval focus increases the research priority of naval doctrines by a large amount, marines and ship technologies to a lesser extent.
Countries with dockyards have a default value of number_of_dockyards + (convoys_in_use + imported_resources)/5, capped at 100. This is reduced by 25% when at peace. Countries without dockyards default to -999.

### Naval air <a id="Naval_air"></a>

Naval air focus increases the research priority of carrier plane variants and naval bombers.
The default value is 20 times the number of carriers, capped at 100. This is reduced by 25% when at peace.
Countries without carriers default to -999.

### Aviation <a id="Aviation"></a>

Aviation focus increases the research priority of air doctrines by a large amount, paratroopers and plane technologies to a lesser extent.
The default value is 10 times the number of airports, capped at 100. This is reduced by 25% when at peace.
Countries without airports default to -999.

### Military equipment <a id="Military_equipment"></a>

Military equipment focus increases the research priority of infantry technologies by a large amount, artillery and support equipment to a lesser extent.
The default value is 75 when at peace, 100 when at war.

## Historical focuses <a id="Historical_focuses"></a>

This focus doesn't have a value attached to it, but the AI will follow the national focuses in the specified order if historical AI focuses is enabled.

## Modding <a id="Modding"></a>

### Focus factors <a id="Focus_factors"></a>

Each of the AI focuses can be changed with a matching country specific modifier called ai_focus_<x>_factor that gets applied after the default calculations above. E.g. ai_focus_naval_air_factor = 0.5 adds a 50% bonus to the naval air focus of the country.

### Research weights <a id="Research_weights"></a>

The `/Hearts of Iron IV/common/ai_focuses` files controls how much the AI focuses affect which kinds of research and national focuses.

Each focus name can be postfixed with a country tag to make a specific focus setup for a country, i.e. **ai_focus_aviation_GER**.

Here is a generic example:

```text
<focus> = {
    research = {
        <technology category> = <weight>
    }
}
```

<!-- kit:begin id="ai-focus-research-format" at="section:Research_weights" -->
**Kit note** What vanilla `common/ai_focuses/` holds in 1.19.4.1. All lines: [vanilla-confirmed 1.19.4.1] `common/ai_focuses/*.txt`, `common/technology_tags/00_technology.txt`.

- 8 files: `generic.txt` (block ids `ai_focus_<name>`) and one per country with its own weights (`ENG`, `FRA`, `GER`, `ITA`, `JAP`, `SOV`, `USA`; block ids `ai_focus_<name>_<TAG>`, for example `ai_focus_naval_USA`). Each block holds only `research = { <key> = <weight> }`. No block holds national focuses.
- A country file replaces the whole generic block for that country, so a country block should list every research key it still wants. Not confirmed by a test [unverified].
- Research keys in vanilla are technology categories from `common/technology_tags/00_technology.txt`, such as `armor`, `artillery`, `industry`, `electronics`, `infantry_weapons`, `radar_tech`, `naval_doctrine`, `land_doctrine`, `air_doctrine`, `jet_technology`, `nuclear`, `para_tech`, `dd_tech` to `ss_tech`. Two keys are not categories: `defensive` (weight 5.0 in the defense block) and `offensive` (5.0 in the aggressive block). What they do is not documented.
- Weights are plain numbers; doctrine keys use large ones (`land_doctrine = 100.0`, `naval_doctrine = 100.0`, `air_doctrine = 50.0` generic, 75.0 for the USA). The wiki says only that these files control how much each focus affects research. Reading a weight as a multiplier on the research score of every technology in that category is [unverified].
<!-- kit:end id="ai-focus-research-format" -->

### Historical focuses <a id="Historical_focuses_2"></a>

To add historical national focuses, you add a **ai_historical_focus_list_<tag>** that contains the national focuses the AI should prioritize. This system has been somewhat super-seeded by AI strategy plans which allow for historical focus lists but also deviating from them when basic assumptions are broken.

Here is a generic example:

```text
ai_historical_focus_list_<tag> = {
    ai_national_focuses = {
        <national focus>
    }
}
```

<!-- kit:begin id="ai-focus-historical-moved" at="section:Historical_focuses_2" -->
**Kit correction** In 1.19.4.1 historical focus lists are written in strategy plans, not in `ai_focuses`. The only `ai_historical_focus_list_USA` in vanilla sits in `common/ai_focuses/USA.txt`, and every line of it is commented out. Live lists are the `ai_national_focuses = { ... }` blocks of `common/ai_strategy_plans/*.txt` (124 plan files hold one; 70 plan files test `is_historical_focus_on = yes`, a trigger documented as "check if the historical focus is active"). See [AI modding](<ai_modding.md#AI_strategy_plans>) for the plan format and `focus_factors`. [vanilla-confirmed 1.19.4.1] `common/ai_focuses/USA.txt`, `common/ai_strategy_plans/`; [docs] `documentation/triggers_documentation.md` (`is_historical_focus_on`). That the string `ai_historical_focus_list` still exists in `hoi4.exe` does not show that the old block is read. In a test the old block was still read: an `ai_historical_focus_list_<TAG>` block in `common/ai_focuses` loaded with no log line, and each of the four generic-tree countries that had one started the focus it names first (TIB and NEP `aviation_effort`, YEM and SAU `army_effort`) by day 3. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, game.log read. The controls without a list started `industrial_effort` (OMA, MON) and `army_effort` (LIB), so the army pair is weaker evidence than the aviation pair. POL did not follow its list because its vanilla historical plan was still loaded (`POL_complete_april_constitution`), so that run does not say which source wins.
<!-- kit:end id="ai-focus-historical-moved" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>) • [Units](<unit_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
