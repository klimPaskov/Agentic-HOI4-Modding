# Creative brief and build plan

Part of the [hoi4-new-mod](../SKILL.md) skill. Read before drafting `docs/mod/brief.md`.

The brief fixes the mod's direction before any feature is designed, so every feature spec, every picture and every line of text serves one mod. It is one page. Detail belongs in the feature specs.

## Drafting from a short request

1. Take every fact the request states as established (origin `user`).
2. For every other field, write a suggested answer that fits the request and the game, with a one-line reason. Mark it `(suggested)`.
3. Prefer suggestions that keep the mod playable and coherent at every phase: a start date with a vanilla bookmark, nations the map can hold, a tone the art route can reach.
4. Never invent real people's words or attribute views to them. Real history, people and places follow the canon policy.

## Template

Copy this into `docs/mod/brief.md` and fill every field.

```markdown
# <Mod name>: creative brief

Request: "<the user's words>"
Status: draft | agreed (date)

## Setting
- Premise: <one or two sentences: what is different about this world>
- Era and start date: <for example 1936.1.1, the vanilla bookmark it uses or replaces>
- Map concept: <where it sits on the map: existing states, a new island or region on the vanilla map, or a new world>
- Kind of mod: <add-on to the vanilla world | total conversion>
- Compatibility: <vanilla compatible | needs listed DLC | standalone>; <other mods it must load with, if any>

## Nations
| Tag | Name | Role | Playable | Notes |
| --- | --- | --- | --- | --- |
| <TAG> | <name> | <protagonist, rival, faction leader, minor> | yes/no | <ideology, government, key characters> |

## Tone and themes
- Tone: <for example grounded alternate history, pulp adventure, grim, satirical>
- Themes: <three to five>
- Limits: <subjects to avoid or treat with care>

## Visual and audio style
- Art direction: <period, palette, references: for example "1930s Mediterranean poster art, sea greens and bronze">
- Portraits, flags, icons: <generated in the mod's style | vanilla reuse | sourced>
- Music and sound: <none | vanilla | sourced or licensed>

## Build plan
- Aim: <the complete mod this idea implies, in one or two sentences>
- Core (playable first): <the country, its map presence, a focus tree, the first events, its characters and art>
- Expansion 1: <for example the rivals and their trees, an event chain, a decision category>
- Expansion 2 and later: <each a playable step towards the complete mod>
- Surfaces: <every surface the plan touches: map, country, history, ideas, characters, focus_tree, events, decisions, mechanics, interface, ai, art, localisation>
- Excluded by the user: <only what the user chose to leave out, with the decision id>

## Autonomy
- Questions: <ask once, then build | check in at milestones>
- In-game testing: <the answer recorded in decisions.md>
```

## The build plan

A short request always aims at the complete mod the idea implies. There is no size to pick and nothing is cut: the plan only sets the order. The core comes first and is playable on its own: the main country with its history, its presence on the map, a focus tree with real effects, its first events, characters and the art for all of it. Each expansion then adds the next part (rivals and their trees, longer event chains, decisions and mechanics, interface, AI for every new country, more art), and the mod is playable after each one.

Every phase is built to the full quality bar of its owning skills. The plan becomes the ledger's `scope.phases`, and each feature names its phase, so the gate builds the core before any expansion. Removing an expansion, or a part of one, needs the user's approval in `decisions.md`.

## Autonomy dial

Ask the user how much they want to steer, with "ask once, then build" as the suggestion:

- **Ask once, then build.** One consultation, then the agent builds to the gate and reports. Defaults are recorded as `agent default`.
- **Milestones.** The agent pauses at named milestones (for example after the map and countries, after the focus trees, after the art) for the user to look, with `check.py gate --wait`.

Either way, art and interface taste is the user's to judge: the ledger's first art feature is a style round, so the style is agreed once before the rest is made, and then each feature makes its own art.
