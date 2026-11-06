# Bookmark modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="81580" sources="common/bookmarks/ common/game_rules/00_game_rules.txt common/difficulty_settings/00_difficulty.txt common/modifiers/00_static_modifiers.txt common/defines/00_defines.lua interface/frontendgamesetupview.gui interface/frontendgamesetupview.gfx documentation/effects_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: both vanilla bookmark files, the game rule and difficulty setting files, the setup screen GUI and the START_DATE defines.
- Kit blocks added: `bookmark-1193-keys` (bookmark and country-entry keys the wiki lacks: `filters`, `version`, `required_dlc`, `assume_not_played_if_missing_data`, `override_leader_portrait`, six commented layout switches), `bookmark-effect-weather`, `bookmark-date-defines`, `bookmark-ui-limits`, `bookmark-difficulty-vanilla`, `bookmark-game-rules-1193`.
- Errors found: the focus card limit is 4, not 3, in the 1.19.3 GUI; the stated default date `2.1.1.1` is not confirmed; the example rule group names are examples only.
- Gaps left: what `version`, `assume_not_played_if_missing_data` and the `new_content` filter do at runtime is not documented anywhere in the game files.
**1.19.4.1 re-check (2026-11-01).** 8 tagged statements depended on files the update changed (`common/bookmarks/blitzkrieg.txt`, `common/defines/00_defines.lua` and the setup screen localisation), and all of them were re-measured. Nothing moved: still 152 country entries, the same `version` values, 3 focuses on every entry, the seeds 12345 and 22345, and the START_DATE defines. The statement that vanilla entries list 3 ideas is corrected to 114 of 152, since some entries list fewer or more. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="bookmark-1193-keys" at="section:attributes" -->
Keys of the 1.19.3 bookmark format that the list above does not name.

Bookmark-level keys. Row 1: [vanilla-confirmed 1.19.4.1] `common/bookmarks/the_gathering_storm.txt` and `blitzkrieg.txt` (both set `filters = { new_content continent }`). Rows 2 to 8 exist only in comments of `the_gathering_storm.txt`: no uncommented use of any of the seven tokens in `common/`, `events/`, `history/` or `interface/`. [vanilla-confirmed 1.19.4.1] Each token is also a string in `hoi4.exe`, and the defaults are the comment's and untested [unverified].

| Key | Value | Meaning |
| --- | --- | --- |
| `filters` | list of tokens | Filter buttons above the country list. Vanilla uses `new_content` and `continent`. The vanilla comment says the list "can also contain `label`" |
| `label` (country entry) | `label = { label_1 label_2 }` | Labels are gathered from all entries and become filter buttons, only when `label` is in `filters` |
| `label_order` | `{ label_1 label_2 }` | Forces the button order. The comment says a warning is logged for a label that countries use but the list lacks |
| `sort_unplayed_first` | yes/no, default yes | Countries with unplayed content are listed first |
| `include_majors_in_minor_list` | yes/no, default yes | When a filter is active, majors also show in the small list |
| `apply_filter_to_majors` | yes/no, default no | When yes, the major row obeys the filter too |
| `apply_filter_to_other_country` | yes/no, default no | By default the `"---"` entry is always shown; when yes it obeys the filter |
| `scrollable_country_list` | yes/no, default no | Scrolls the small-flag list with a vertical scrollbar instead of the overflow dropdown |

Country-entry keys beyond the wiki list. Counts are from both vanilla files together. [vanilla-confirmed 1.19.4.1] `common/bookmarks/` for the keys and counts (152 entries: 85 and 67 uncommented `version` lines); what the engine does with `version` and `assume_not_played_if_missing_data` is [unverified].

| Key | Seen | Meaning |
| --- | --- | --- |
| `version = base_game` | on every one of the 152 entries | Name of the content version of this entry. The 12 values seen are in the note below the table. Probably what the `new_content` filter and the unplayed sorting key on [unverified] |
| `required_dlc = { "Name" }` | 46 and 31 entries | Entry exists only with every listed DLC. The block takes several names (`{ "Gotterdammerung" "No Compromise, No Surrender" }`, 2 entries). The value is a block here, unlike `required_dlc = "Name"` in game rules |
| `assume_not_played_if_missing_data = yes` | 6 and 5 entries | Set mostly on entries of newer DLC: 8 `thunder_at_our_gates` and 1 `peace_for_our_time`, plus 2 `base_game` entries (the Australia fallbacks shown without Thunder at Our Gates) [vanilla-confirmed 1.19.4.1]. Name suggests the entry counts as unplayed when the profile has no data for it [unverified] |
| `override_leader_portrait = JAP_emperor_hirohito` | 3 entries, all Japan | Character id from `common/characters/JAP.txt` whose portrait is shown instead of the leader's |

Notes on rows of the table above:

- `version`: Values seen: `base_game`, `no_compromise_no_surrender`, `trial_of_allegiance`, `graveyard_of_empires`, `gotterdammerung`, `thunder_at_our_gates`, `arms_against_tyranny`, `by_blood_alone`, `la_resistance`, `man_the_guns`, `no_step_back`, `peace_for_our_time`.

Base-plus-DLC pair, the vanilla pattern for a country that changes with a DLC:

```text
"FRA"={
    history = "FRA_GATHERING_STORM_DESC"
    ideology = democratic
    version = base_game
    available = { NOT = { has_dlc = "La Resistance" } }
    ideas = { FRA_victors_of_wwi FRA_disjointed_government FRA_protected_by_the_maginot_line }
    focuses = { FRA_form_the_popular_front FRA_revive_the_national_bloc FRA_france_leads }
}
"FRA"={
    history = "FRA_GATHERING_STORM_DESC"
    ideology = democratic
    version = la_resistance
    required_dlc = { "La Resistance" }
    ideas = { FRA_victors_of_wwi FRA_disjointed_government FRA_protected_by_the_maginot_line }
    focuses = { FRA_invite_communist_ministers FRA_utilize_the_leagues FRA_je_suis_la_deluge }
}
```

Example: [vanilla-confirmed 1.19.3] `common/bookmarks/the_gathering_storm.txt` (FRA entries, ideas and focuses shortened to one line). Vanilla `ideology` values: `neutrality` (76), `democratic` (45), `fascism` (21), `communism` (10). [vanilla-confirmed 1.19.4.1] `common/bookmarks/`.
<!-- kit:end id="bookmark-1193-keys" -->

<!-- kit:begin id="bookmark-effect-weather" at="section:attributes" -->
Both vanilla bookmarks end with an `effect` block whose only live line is `randomize_weather = <seed>`, followed by the vanilla comment "Obligatory in every bookmark". Seeds are 12345 in `blitzkrieg.txt` and 22345 in `the_gathering_storm.txt`; give each bookmark of a mod its own seed. [vanilla-confirmed 1.19.4.1] `common/bookmarks/blitzkrieg.txt`, `the_gathering_storm.txt`.

`randomize_weather` is documented as a one-line effect usable in any scope and takes no documented parameters. [docs] `documentation/effects_documentation.md`. The commented line `#123 = { rain_light = yes }` in both files is not a documented effect (`rain_light` is a weather type defined in `common/weather.txt`), so do not copy it as a working example. [vanilla-confirmed 1.19.4.1] `common/weather.txt`; no `rain_light` effect in `documentation/effects_documentation.md`.
<!-- kit:end id="bookmark-effect-weather" -->

<!-- kit:begin id="bookmark-ui-limits" at="section:user-interface" -->
The card limits in `interface/frontendgamesetupview.gui` of 1.19.3: `ideas_grid` has `max_slots = { x = 3 y = 1 }` and `focus_grid` has `max_slots = { x = 4 y = 1 }`, so a country card shows up to 3 ideas and up to 4 focuses (the wiki says 3 for both). Vanilla entries list 3 focuses each (all 152) and usually 3 ideas (114 of 152, the rest list 0 to 2, 4 or 5). [vanilla-confirmed 1.19.4.1] `interface/frontendgamesetupview.gui`, `common/bookmarks/`.

Other grids: `bookmarks_grid` has `slotsize` 260 wide and `max_slots_vertical = 1`; `countries_medium` holds 8 slots per row; `countries_mini` holds 23 per row and 2 rows; a new `filters` element (`OverlappingElementsBoxType`) holds the filter buttons, and the `country_filter` window defines one such button. [vanilla-confirmed 1.19.3] `interface/frontendgamesetupview.gui`.

Bookmark pictures: `GFX_select_date_1936` and `GFX_select_date_1939` are defined in `interface/frontendgamesetupview.gfx` and both textures (`gfx/interface/select_date_1936.dds`, `select_date_1939.dds`) are 180 by 104 pixels, matching the wiki. [vanilla-confirmed 1.19.3] `interface/frontendgamesetupview.gfx`, DDS header.
<!-- kit:end id="bookmark-ui-limits" -->

<!-- kit:begin id="bookmark-date-defines" at="section:notes" -->
The wiki's "defaults to 2.1.1.1" for `date` is not confirmed. What 1.19.4.1 shows: `NDefines.NGame.START_DATE = "1936.1.1.12"`, `END_DATE = "1949.1.1.1"` and `NDefines.NDiplomacy.TENSION_TIME_SCALE_START_DATE = "1936.1.1.12"`. The bookmark dates are `1936.1.1.12` (`the_gathering_storm.txt`) and `1939.8.14.12` (`blitzkrieg.txt`). [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`, `common/bookmarks/`. The wiki says a mod that starts earlier than 1936.1.1.12 needs all three defines. It does not need all three: a bookmark dated 1935.1.1.12 started on 1 January 1935 with `NGame.START_DATE` and `TENSION_TIME_SCALE_START_DATE` both set to it, with `START_DATE` alone and with `TENSION_TIME_SCALE_START_DATE` alone, and each launch logged nothing new in error.log. `END_DATE` was left at its default in all three. No variant had the bookmark with neither define, and the threat is 0 at day 0 in the 1935 and 1936 starts, so an effect of `TENSION_TIME_SCALE_START_DATE` could not show at the start. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, new game from a one-mod bookmark, error.log read and a date probe in game.log.

The history-date rule above (a block in `history/` applies when the start date is later than the block's date) holds in this direction: a history block dated `1939.1.1` applied to a `1939.8.14.12` start (5 research slots and `war_economy` for GER) and did not apply to a `1936.1.1.12` start (4 slots, no `war_economy`). The rule is not "strictly later" at the exact start moment, where a block runs. See [State modding](state_modding.md#history). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, two new games, script probe read in game.log.
<!-- kit:end id="bookmark-date-defines" -->

<!-- kit:begin id="bookmark-difficulty-vanilla" at="section:difficulty-settings" -->
Vanilla `common/difficulty_settings/00_difficulty.txt` holds 8 settings, all with `multiplier = 2.0` and the static modifier `diff_strong_ai_generic`: GER, ITA, SOV, FRA, ENG, USA, JAP (`{ JAP MEN MAN }`) and CHI (`{ CHI PRC }`). Keys are `custom_diff_strong_<tag>` and the loc key `custom_diff_strong_ger` exists in `localisation/english/frontend_l_english.yml`. [vanilla-confirmed 1.19.4.1] `common/difficulty_settings/00_difficulty.txt`, `localisation/english/frontend_l_english.yml`.

`diff_weak_ai_generic` in the wiki example does not exist; `diff_strong_ai_generic` is the only generic modifier. The per-difficulty modifiers are `diff_very_easy_player` to `diff_very_hard_player` and `diff_very_easy_ai` to `diff_very_hard_ai`, as footnote a says. [vanilla-confirmed 1.19.3] `common/modifiers/00_static_modifiers.txt` (11 `diff_*` blocks).
<!-- kit:end id="bookmark-difficulty-vanilla" -->

<!-- kit:begin id="bookmark-game-rules-1193" at="section:game-rules-1" -->
Facts about `common/game_rules/00_game_rules.txt` in 1.19.3 (86 root blocks, 434 `option` and 78 `default` entries). All lines: [vanilla-confirmed 1.19.3] `common/game_rules/00_game_rules.txt`.

- The file's own header comment says the first `option` is the default unless a `default = { ... }` entry exists, and that `allow_achievements` defaults to yes for the default option and no for every other option. Vanilla sets `allow_achievements = yes` on 61 options and `= no` on 108 (the other options rely on the default).
- The same header comment says one rule can be in several groups (repeat `group`), but no vanilla rule has more than one `group` line. The 10 vanilla groups are `RULE_GROUP_AI_BEHAVIOR`, `COUNTRY_SPECIFIC`, `COVERT_ACTIONS`, `DIVISION_TEMPLATES`, `GAMEPLAY`, `GAME_SETUP`, `GENERAL_FOREIGN_POLICY`, `GENERAL_UI`, `PEACE_SCORE` and `RESEARCH`.
- `required_dlc = "Name"` is a plain string here (130 uses) and `exclude_dlc` appears 14 times. This differs from the block form `required_dlc = { "Name" }` of bookmark country entries.
- Country AI rules are named `<TAG>_ai_behavior` (51 blocks, a few written `<TAG>_AI_BEHAVIOR`); `BHR_ai_behavior` in the example above is an invented name that follows this pattern. The root block id is what scripts use: `has_game_rule = { rule = GER_ai_behavior option = FASCIST }`. Vanilla writes the AFG rule both as `rule = AFG_AI_BEHAVIOR` (10 uses) and `rule = AFG_ai_behavior` (2 uses) though the block id is `AFG_ai_behavior`, so the lookup may ignore case; write the exact block id to be safe [unverified].
- Option names in `has_game_rule` are the `name` of the option (`FASCIST`, `DEMOCRATIC`, `RANDOM`), not the loc key.
<!-- kit:end id="bookmark-game-rules-1193" -->
