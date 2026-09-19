# Doctrine modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Doctrine modding", captured 2026-09-19.*

## Table of contents

- [Structure](#Structure)
- [Triggers and Effects](#Triggers_and_Effects)
  - [List of doctrine-related triggers:](#List_of_doctrine-related_triggers:)
  - [List of doctrine-related effects:](#List_of_doctrine-related_effects:)
- [Folders](#Folders)
- [Grand Doctrines](#Grand_Doctrines)
- [Tracks](#Tracks)
- [Subdoctrines](#Subdoctrines)

---

\*Please help improve this article or section by expanding it .\*

## Structure <a id="Structure"></a>

The files are structured as follows:

- `common/doctrines/folders/*.txt` - Doctrine folders
- `common/doctrines/grand_doctrines/*.txt` - Grand Doctrines
- `common/doctrines/tracks/*.txt` - Subdoctrine Tracks
- `common/doctrines/subdoctrines/*.txt` (or any subfolder) - Subdoctrines

## Triggers and Effects <a id="Triggers_and_Effects"></a>

### List of doctrine-related triggers: <a id="List_of_doctrine-related_triggers:"></a>

- set_grand_doctrine - Gives a country the specified grand doctrine.
- set_sub_doctrine - Gives a country the specified subdoctrine.
- add_mastery - Adds doctrine mastery.
- add_daily_mastery - Gives daily mastery for a specified duration
- add_mastery_bonus - Get a bonus to doctrine mastery gain for a certain duration.

### List of doctrine-related effects: <a id="List_of_doctrine-related_effects:"></a>

- has_any_grand_doctrine - Checks if any grand doctrine in folder is currently active for the country.
- has_completed_subdoctrine - Checks if the current country has ever completed the specified subdoctrine (even if it was later switched out).
- has_doctrine - Checks if the given grand doctrine or subdoctrine is currently active for the country.
- has_completed_track - Checks if the given subdoctrine track has been completed
- has_subdoctrine_in_track - Checks if any subdoctrine is currently assigned to (any instance of) the given track.
- has_mastery - Checks if any track of the given type has at least X mastery.
- has_mastery_level - Checks if the country has reached the specified number of mastery levels (rewards) for the given subdoctrine.

## Folders <a id="Folders"></a>

## Grand Doctrines <a id="Grand_Doctrines"></a>

## Tracks <a id="Tracks"></a>

## Subdoctrines <a id="Subdoctrines"></a>

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
