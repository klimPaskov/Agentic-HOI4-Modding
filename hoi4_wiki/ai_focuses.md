# AI focuses

AI focuses balance competing interests in several aspects of the game such as being more or less careful with attacks or prioritizing one field of research over another. Every AI country has a value for each of the focuses with higher values making the country focus more on that characteristic.

## Focus Types

Names of the nine AI focuses as the game files spell them. The section titles below are prose names; scripts use these ids.

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

- `ai_focus_defensive` and `ai_focus_production_factor` appear in no documentation, in no live vanilla script (the second only as a commented line) and in no `hoi4.exe` string, so do not use them; use the ids above.
- Vanilla applies the modifiers in a few places: `ai_focus_aggressive_factor = 0.5` in 4 country leader traits and 1 Italian idea, `ai_focus_aggressive_factor = 1` in another Italian idea, and `ai_focus_defense_factor = 0.5` in 1 trait.
- The aviation and naval air focus values also steer air production: the AI strategy documentation multiplies the number of wanted land-based planes by the hard-coded aviation focus value (after `ai_focus_aviation_factor`) and the wanted carrier planes by the naval air focus value (after `ai_focus_naval_air_factor`).

### Defensive

Multiplied with PLAN_VALUE_TO_EXECUTE, defensive focus increases the threshold to execute battle plans. It increases the research priority of RADAR, construction and artillery among others.
It defaults to 50 during peace, 100 when being in a defensive war and 0 when being in an aggressive war. France has a +50% bonus due to Édouard Daladier's Stout Defender trait.

### Aggressive

Aggressive focus decreases the threshold to execute battle plans, making the AI more likely to activate risky plans. It increases the research priority of synthetic refineries, motorization and armor.
It defaults to 50 during peace (fascist countries 75), 0 when being in a defensive war and 100 when being in an aggressive war. Italy has a +50% bonus due to the Vittoria Mutilata national idea.

### War production

War production focus increases the research priority of industry and electronics techs to a lesser extent.
It defaults to 10 during peace (fascist countries 30) and 100 when at war.

### Military advancements

Military advancements focus increases the research priority for various advanced military techs like jets, night vision, nuclear etc.
It defaults to 25 times the number of research slots (capped at 100) when at war and is reduced by 25% when at peace.

### Peaceful

Peaceful focus increases the research priority for industry and electronics.
It is 100 when at peace, 0 when at war.

### Naval

Naval focus increases the research priority of naval doctrines by a large amount, marines and ship technologies to a lesser extent.
Countries with dockyards have a default value of number_of_dockyards + (convoys_in_use + imported_resources)/5, capped at 100. This is reduced by 25% when at peace. Countries without dockyards default to -999.

### Naval air

Naval air focus increases the research priority of carrier plane variants and naval bombers.
The default value is 20 times the number of carriers, capped at 100. This is reduced by 25% when at peace.
Countries without carriers default to -999.

### Aviation

Aviation focus increases the research priority of air doctrines by a large amount, paratroopers and plane technologies to a lesser extent.
The default value is 10 times the number of airports, capped at 100. This is reduced by 25% when at peace.
Countries without airports default to -999.

### Military equipment

Military equipment focus increases the research priority of infantry technologies by a large amount, artillery and support equipment to a lesser extent.
The default value is 75 when at peace, 100 when at war.

## Historical focuses

This focus doesn't have a value attached to it, but the AI will follow the national focuses in the specified order if historical AI focuses is enabled.

## Modding

### Focus factors

Each of the AI focuses can be changed with a matching country specific modifier called ai_focus_<x>_factor that gets applied after the default calculations above. E.g. ai_focus_naval_air_factor = 0.5 adds a 50% bonus to the naval air focus of the country.

### Research weights

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

What vanilla `common/ai_focuses/` holds in 1.19.4.1.

- 8 files: `generic.txt` (block ids `ai_focus_<name>`) and one per country with its own weights (`ENG`, `FRA`, `GER`, `ITA`, `JAP`, `SOV`, `USA`; block ids `ai_focus_<name>_<TAG>`, for example `ai_focus_naval_USA`). Each block holds only `research = { <key> = <weight> }`. No block holds national focuses.
- A country file replaces the whole generic block for that country, so a country block should list every research key it still wants. Not confirmed by a test (unverified).
- Research keys in vanilla are technology categories from `common/technology_tags/00_technology.txt`, such as `armor`, `artillery`, `industry`, `electronics`, `infantry_weapons`, `radar_tech`, `naval_doctrine`, `land_doctrine`, `air_doctrine`, `jet_technology`, `nuclear`, `para_tech`, `dd_tech` to `ss_tech`. Two keys are not categories: `defensive` (weight 5.0 in the defense block) and `offensive` (5.0 in the aggressive block). What they do is not documented.
- Weights are plain numbers; doctrine keys use large ones (`land_doctrine = 100.0`, `naval_doctrine = 100.0`, `air_doctrine = 50.0` generic, 75.0 for the USA). The wiki says only that these files control how much each focus affects research. Reading a weight as a multiplier on the research score of every technology in that category is unverified.

### Historical focuses

To add historical national focuses, you add a **ai_historical_focus_list_<tag>** that contains the national focuses the AI should prioritize. This system has been somewhat super-seeded by AI strategy plans which allow for historical focus lists but also deviating from them when basic assumptions are broken.

Here is a generic example:

```text
ai_historical_focus_list_<tag> = {
    ai_national_focuses = {
        <national focus>
    }
}
```

In 1.19.4.1 historical focus lists are written in strategy plans, not in `ai_focuses`. The only `ai_historical_focus_list_USA` in vanilla sits in `common/ai_focuses/USA.txt`, and every line of it is commented out. Live lists are the `ai_national_focuses = { ... }` blocks of `common/ai_strategy_plans/*.txt` (124 plan files hold one; 70 plan files test `is_historical_focus_on = yes`, a trigger documented as "check if the historical focus is active"). See [AI modding](ai_modding.md#ai-strategy-plans) for the plan format and `focus_factors`. That the string `ai_historical_focus_list` still exists in `hoi4.exe` does not show that the old block is read. In a test the old block was still read: an `ai_historical_focus_list_<TAG>` block in `common/ai_focuses` loaded with no log line, and each of the four generic-tree countries that had one started the focus it names first (TIB and NEP `aviation_effort`, YEM and SAU `army_effort`) by day 3. The controls without a list started `industrial_effort` (OMA, MON) and `army_effort` (LIB), so the army pair is weaker evidence than the aviation pair. POL did not follow its list because its vanilla historical plan was still loaded (`POL_complete_april_constitution`), so that run does not say which source wins.
