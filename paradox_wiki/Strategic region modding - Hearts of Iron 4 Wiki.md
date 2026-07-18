[Strategic regions](https://hoi4.paradoxwikis.com/Strategic_Region) are defined in `/Hearts of Iron IV/map/strategicregions/*.txt`.

Each strategic region is typically stored in it's own file, although you can store multiple strategic region definitions within the same file, as the ID is defined within the strategic region definition, rather than the file title.

Here is a generic example of a strategic region:

```text
strategic_region = {
    id = <int>
    name = <localization key>

    provinces = {
        <province ids>
    }

    weather = {
        period = {
            between = { <min> <max> }
            temperature = { <min> <max> }
            no_phenomenon = <weight>
            rain_light = <weight>
            rain_heavy = <weight>
            snow = <weight>
            blizzard = <weight>
            mud = <weight>
            sandstorm = <weight>
            min_snow_level = <amount>
        }
    }
}
```

- **id** defines the numerical id used by the strategic region. The strategic region IDs must be added sequentially, skipping numbers will cause crashes.

- **name** defines the localization key the strategic region uses. You can use a non-localized string (i.e. "Paris"), but it is best practice to use localized strings.

- **provinces** scope defines which provinces the strategic region is composed over.

- **weather** scope determines the weather within the provinces covered by the strategic region.

## <a id="weather"></a>Weather

Each strategic region has a **weather** scope that determines how the weather changes for provinces within it.

Each weather system is defined within a **period** scope within the **weather** scope.

- **between** scope determines when the weather system occurs, the notation is `day.month day.month`, i.e. `0.0 30.0` means the weather system occurs between the 1st of January and the 31st, including these days. Note that the first day and the first month are marked as 0, not as 1.

- **temperature** scope determines the minimum and maximum temperature for the weather system.

- ~~**temperature\_day\_night** scope determines the minimum and maximum temperature variability during day and night for the weather system.~~ (This is no longer used since version 1.11, set all temperature ranges via temperature)

- **min\_snow\_level** scope determines the minimum amount of snow that is always present in the weather system. Typically only used for areas with year-round snow.

Each of the weather states are given a weight, determining how likely the state will occur within the weather system. The weather states can be found in `/Hearts of Iron IV/common/weather.txt`.

## <a id="tips"></a>Tips

- When placing strategic regions, the provinces they are compose of should be contiguous. This means islands are normally part of a *sea* strategic region.

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

|  |  |
| --- | --- |
| Documentation | [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](https://hoi4.paradoxwikis.com/Conditions) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](https://hoi4.paradoxwikis.com/List_of_modifiers) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) ([Flags](<Data structures - Hearts of Iron 4 Wiki.md#flags>), [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#event-targets>), [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#country-tag-aliases>), [Variables](<Data structures - Hearts of Iron 4 Wiki.md#variables>), [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#arrays>)) |

|  |  |
| --- | --- |
| Scripting | [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) ([Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#game-rules>)) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Map | [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • Strategic regions |

|  |  |
| --- | --- |
| Graphical | [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Cosmetic | [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Other | [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](https://hoi4.paradoxwikis.com/Mod_structure) • [Mods](https://hoi4.paradoxwikis.com/Mods) • [Nudger](https://hoi4.paradoxwikis.com/Nudger) |
