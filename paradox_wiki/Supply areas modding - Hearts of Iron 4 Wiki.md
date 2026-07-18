**NOTE: Supply areas are deprecated as of patch 1.11 Barbarossa/No Step Back. The following only applies to version 1.10 and before.**

Supply areas are defined in `/Hearts of Iron IV/map/supplyareas/*.txt`.

Each supply area is typically stored in it's own file, although you can store multiple supply area definitions within the same file, as the ID is defined within the supply area definition, rather than the file title.

Here is a generic example of a supply area:

```text
supply_area = {
    id = <int>
    name = <localization key>
    value = <amount>
    states = {
        <state id>
    }
}
```

- **id** defines the numerical id used by the supply area. The supply area IDs must be added sequentially, skipping numbers will cause crashes.

- **name** defines the localization key the supply area uses. You can use a non-localized string (i.e. "Paris"), but it is best practice to use localized strings.

- **value** defines the amount of base supply the supply area grants. In vanilla, the supply varies from 0 to 16.

- **states** scope defines which states the supply area covers. Note that supply areas should normally cover more than one state.

## <a id="tips"></a>Tips

- When placing supply areas, the states they are compose of should be contiguous. This means islands should have their own supply areas.
- The average supply value in vanilla is 10.

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

|  |  |
| --- | --- |
| Documentation | [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](https://hoi4.paradoxwikis.com/Conditions) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](https://hoi4.paradoxwikis.com/List_of_modifiers) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) ([Flags](<Data structures - Hearts of Iron 4 Wiki.md#flags>), [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#event-targets>), [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#country-tag-aliases>), [Variables](<Data structures - Hearts of Iron 4 Wiki.md#variables>), [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#arrays>)) |

|  |  |
| --- | --- |
| Scripting | [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) ([Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#game-rules>)) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Map | [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • Supply areas • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Graphical | [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Cosmetic | [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Other | [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](https://hoi4.paradoxwikis.com/Mod_structure) • [Mods](https://hoi4.paradoxwikis.com/Mods) • [Nudger](https://hoi4.paradoxwikis.com/Nudger) |
