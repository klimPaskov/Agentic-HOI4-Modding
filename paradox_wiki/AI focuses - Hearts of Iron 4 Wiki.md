# AI focuses

*Offline snapshot of the Hearts of Iron IV Wiki page "AI focuses", captured 2026-09-19.*

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

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
