# Table of contents

- [Structure](#structure)
- [Triggers and Effects](#triggers-and-effects)
  - [List of faction-related effects](#list-of-faction-related-effects)
  - [List of faction-related triggers](#list-of-faction-related-triggers)
  - [List of faction-related modifiers](#list-of-faction-related-modifiers)
- [Templates](#templates)
- [Goals](#goals)
- [Manifests](#manifests)


---

## Structure

The file structure is as follows:

- /Hearts of Iron IV/common/factions/goals/\*.txt - Faction [goals](#goals) and [manifests](#manifests).
- /Hearts of Iron IV/common/factions/icons/\*.txt - Icons definitions for generated factions.
- /Hearts of Iron IV/common/factions/member\_upgrades/\*.txt -
- /Hearts of Iron IV/common/factions/member\_upgrades/member\_groups/\*.txt -
- /Hearts of Iron IV/common/factions/rules/\*.txt - Faction rules.
- /Hearts of Iron IV/common/factions/rules/groups/\*.txt - Groups for rules.
- /Hearts of Iron IV/common/factions/templates/\*.txt - Faction [templates](#templates).

## Triggers and Effects

### List of faction-related effects

- create\_faction - creates a faction without a template (OBSOLETE)
- create\_faction\_from\_template - the new fancy way of creating factions
- dismantle\_faction - dismantles faction
- set\_faction\_leader - changes faction's leader
- set\_faction\_spymaster - changes faction's spymaster
- set\_faction\_name - changes faction's name
- add\_to\_faction - adds a country to a faction
- remove\_from\_faction - removes a country from a faction
- leave\_faction - removes the current country from faction
- set\_faction\_rule - sets a rule on a faction
- set\_faction\_manifest - changes faction's manifest (main goal)
- add\_faction\_goal - adds a goal to a faction
- remove\_faction\_goal - removes a goal from a faction
- add\_faction\_initiative - adds FI to faction
- add\_faction\_power\_projection - adds power to the faction
- add\_faction\_influence\_score - adds influence to the country in the faction
- add\_faction\_influence\_ratio - adds influence to the country based on the given ratio of the faction's total influence

### List of faction-related triggers

- faction\_manifest\_fulfillment - compares the current country faction's manifest fulfillmens to a value
- has\_faction\_template - checks if the current country is in a faction created from a template
- faction\_power\_projection - compares the current country faction's power to a value
- faction\_influence\_score - checks influence value of current country in the faction
- faction\_influence\_ratio - checks influence ratio of current country in the faction
- faction\_influence\_rank - checks influence rank in the faction of the current country
- has\_faction\_goal - checks if the current country's faction has an active or completed goal
- has\_completed\_faction\_goal - checks if the current country's faction has completed a goal
- faction\_goal\_fulfillment - checks goal fulfillment for the current country's faction
- has\_manpower\_to\_become\_leader - checks if the current country exceeds the current faction leader and its subjects in deployed manpower
- has\_industry\_to\_become\_leader - checks if the current country exceeds the faction leader in number of factories

### List of faction-related modifiers

- faction\_influence\_war\_score\_factor - war score modifier for faction influence
- faction\_influence\_industrial\_capacity\_factor - industrial capacity modifier for faction influence
- faction\_influence\_garrison\_support\_provider\_factor - garrison support provider modifier for faction influence
- faction\_influence\_garrison\_support\_reciver\_factor - garrison support reciver modifier for faction influence
- faction\_influence\_expeditionary\_force\_provider\_factor - expeditionary force provider modifier for faction influence
- faction\_influence\_expeditionary\_force\_reciver\_factor - expeditionary force reciver modifier for faction influence

## Templates

TODO

## Goals

TODO

## Manifests

TODO

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
