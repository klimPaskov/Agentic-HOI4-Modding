# Table of contents

- [Focus Types](#focus-types)
  - [Defensive](#defensive)
  - [Aggressive](#aggressive)
  - [War production](#war-production)
  - [Military advancements](#military-advancements)
  - [Peaceful](#peaceful)
  - [Naval](#naval)
  - [Naval air](#naval-air)
  - [Aviation](#aviation)
  - [Military equipment](#military-equipment)
  - [Focus factors](#focus-factors)
  - [Research weights](#research-weights)
  - [Historical focuses](#historical-focuses)


---

AI focuses balance competing interests in several aspects of the game such as being more or less careful with attacks or prioritizing one field of research over another. Every AI country has a value for each of the focuses with higher values making the country focus more on that characteristic.

## Focus Types

### Defensive

Multiplied with PLAN\_VALUE\_TO\_EXECUTE, defensive focus increases the threshold to execute battle plans. It increases the research priority of RADAR, construction and artillery among others.
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
Countries with dockyards have a default value of number\_of\_dockyards + (convoys\_in\_use + imported\_resources)/5, capped at 100. This is reduced by 25% when at peace. Countries without dockyards default to -999.

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

# Historical focuses

This focus doesn't have a value attached to it, but the AI will follow the national focuses in the specified order if historical AI focuses is enabled.

# Modding

### Focus factors

Each of the AI focuses can be changed with a matching country specific modifier called ai\_focus\_<x>\_factor that gets applied after the default calculations above. E.g. ai\_focus\_naval\_air\_factor = 0.5 adds a 50% bonus to the naval air focus of the country.

### Research weights

The /Hearts of Iron IV/common/ai\_focuses files controls how much the AI focuses affect which kinds of research and national focuses.

Each focus name can be postfixed with a country tag to make a specific focus setup for a country, i.e. **ai\_focus\_aviation\_GER**.

Here is a generic example:

```text
<focus> = {
    research = {
        <technology category> = <weight>
    }
}
```

### Historical focuses

To add historical national focuses, you add a **ai\_historical\_focus\_list\_<tag>** that contains the national focuses the AI should prioritize. This system has been somewhat super-seeded by AI strategy plans which allow for historical focus lists but also deviating from them when basic assumptions are broken.

Here is a generic example:

```text
ai_historical_focus_list_<tag> = {
    ai_national_focuses = {
        <national focus>
    }
}
```

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
