# Table of contents

- [Structure](#structure)
- [Triggers and Effects](#triggers-and-effects)
  - [List of doctrine-related triggers:](#list-of-doctrine-related-triggers)
  - [List of doctrine-related effects:](#list-of-doctrine-related-effects)
- [Folders](#folders)
- [Grand Doctrines](#grand-doctrines)
- [Tracks](#tracks)
- [Subdoctrines](#subdoctrines)

---

## <a id="structure"></a>Structure

The files are structured as follows:

- `common/doctrines/folders/*.txt` - Doctrine folders
- `common/doctrines/grand_doctrines/*.txt` - Grand Doctrines
- `common/doctrines/tracks/*.txt` - Subdoctrine Tracks
- `common/doctrines/subdoctrines/*.txt` (or any subfolder) - Subdoctrines

## <a id="triggers-and-effects"></a>Triggers and Effects

### <a id="list-of-doctrine-related-triggers"></a>List of doctrine-related triggers:

- set\_grand\_doctrine - Gives a country the specified grand doctrine.
- set\_sub\_doctrine - Gives a country the specified subdoctrine.
- add\_mastery - Adds doctrine mastery.
- add\_daily\_mastery - Gives daily mastery for a specified duration
- add\_mastery\_bonus - Get a bonus to doctrine mastery gain for a certain duration.

### <a id="list-of-doctrine-related-effects"></a>List of doctrine-related effects:

- has\_any\_grand\_doctrine - Checks if any grand doctrine in folder is currently active for the country.
- has\_completed\_subdoctrine - Checks if the current country has ever completed the specified subdoctrine (even if it was later switched out).
- has\_doctrine - Checks if the given grand doctrine or subdoctrine is currently active for the country.
- has\_completed\_track - Checks if the given subdoctrine track has been completed
- has\_subdoctrine\_in\_track - Checks if any subdoctrine is currently assigned to (any instance of) the given track.
- has\_mastery - Checks if any track of the given type has at least X mastery.
- has\_mastery\_level - Checks if the country has reached the specified number of mastery levels (rewards) for the given subdoctrine.

## <a id="folders"></a>Folders

## <a id="grand-doctrines"></a>Grand Doctrines

## <a id="tracks"></a>Tracks

## <a id="subdoctrines"></a>Subdoctrines

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

|  |  |
| --- | --- |
| Documentation | [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](https://hoi4.paradoxwikis.com/Conditions) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](https://hoi4.paradoxwikis.com/List_of_modifiers) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) ([Flags](<Data structures - Hearts of Iron 4 Wiki.md#flags>), [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#event-targets>), [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#country-tag-aliases>), [Variables](<Data structures - Hearts of Iron 4 Wiki.md#variables>), [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#arrays>)) |

|  |  |
| --- | --- |
| Scripting | [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) ([Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#game-rules>)) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • Doctrines • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Map | [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Graphical | [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Cosmetic | [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Other | [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](https://hoi4.paradoxwikis.com/Mod_structure) • [Mods](https://hoi4.paradoxwikis.com/Mods) • [Nudger](https://hoi4.paradoxwikis.com/Nudger) |
