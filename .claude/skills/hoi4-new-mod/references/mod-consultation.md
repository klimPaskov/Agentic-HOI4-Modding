# Mod-defining consultation

Part of the [hoi4-new-mod](../SKILL.md) skill. Read before asking the user anything about a new mod.

The general consultation rules are in `hoi4-feature-planning/references/consultation-questions.md`: inspect first, sort every open point into established, yours to decide or genuine, ask once with suggested answers, record the answers, and do not ask again. This file adds the questions that decide a whole mod. Ask them in the same single message as the feature-level questions that are genuine for the request.

## The mod-defining questions

Ask each one that the request and the files do not already answer. Give the suggestion that fits this request, with a one-line reason; the right-hand column says how to choose it.

| Topic | Question | How to choose the suggestion |
| --- | --- | --- |
| Map position | Where does the mod sit on the map: existing states, a new island or region added to the vanilla map, or a new world? | Existing states when the idea is a country that could take over real land. A new region only when the idea needs land that does not exist, and say what the map tools can build (`hoi4-map-states`). A new world only for a total conversion |
| Start date | Which start date and bookmark? | A vanilla bookmark (1936.1.1 or 1939.8.14) unless the premise needs another year. Say what a new date costs: every country's history must be written for it |
| Kind of mod | An add-on to the vanilla world, or a total conversion? | An add-on unless the premise replaces the world |
| Playable nations | Which nations are playable, and which is the main one? | The protagonist nation, plus the rivals the story needs to be playable from both sides when the scope allows |
| Compatibility | Must it stay compatible with vanilla saves, other mods or DLC? | Compatible with the current game version and every DLC optional, unless the design uses a DLC mechanic, which then becomes a listed requirement |
| Tone and limits | Which tone, and which subjects need care? | The tone the request implies; real atrocities, living people and religions handled with care |
| Visual style | Which art direction for portraits, flags, icons and event pictures? | A period style that matches the start date and the setting, in the project's configured image route |
| In-game testing | Run in-game tests at all, how (the live-testing provider or a manual recipe; any limits on when the game may start) and when (after each feature, at milestones, at the end)? | With HOI4 Live Tools installed and supported here, a smoke test after each finished phase and before the mod is called done (`when: phases`); otherwise a short manual check at the same points. Record it in `decisions.md` and the ledger's `live_testing` (`hoi4-live-playtest`) |
| Autonomy | Ask once and then build, or stop at milestones for a look? | Ask once, then build, with one picture round at the first art feature |

Then add the feature-level questions that are genuine (`consultation-questions.md`): fallback policy, asset sources, spend for paid operations, audio, world iteration, animation.

## Example

A request of five words gets one message like this, shortened here:

> Before I start, a few choices with my suggestions. Reply "use your suggestions" or change any of them.
> 1. Map: Atlantis as a new island west of Portugal, built with the map tools. *Suggested because the idea needs land that does not exist.*
> 2. Start: 1936.1.1 with the vanilla bookmark. *Every existing country keeps its history.*
> 3. Build order: a playable core first (the country, its island, a focus tree, the first events and characters), then the expansions the brief lists, until the whole mod is done. *Playable at every step, nothing cut.*
> ...
> I will decide myself: file layout, the tag (`ATL` unless taken), event and focus ids, the order of work and the checks.

## Recording

Write every answer and default into `docs/mod/decisions.md`, in the format of `consultation-questions.md`:

| ID | Item | Decision | Origin | Date | Basis |
| --- | --- | --- | --- | --- | --- |
| M-01 | Map position | New island west of Portugal | user | 2026-01-01 | Consultation answer |
| M-02 | Start date | 1936.1.1 | agent default | 2026-01-01 | User said "use your suggestions" |

Then update `brief.md` so it says the same, and mark it agreed.

## When the user does not answer

If the user said to work without questions, or nobody is there to answer, apply the suggestions, record them as `agent default`, and list them at the top of the final report so the user can overrule any of them. An agent default never counts as the user's approval of a reduced scope.
