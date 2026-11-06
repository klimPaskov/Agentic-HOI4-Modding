# Event modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="102070" sources="events/ history/ common/defines/00_defines.lua documentation/effects_documentation.md hoi4.exe common/ documentation/" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 128 files in `events/` (6,974 events), the event effects in `documentation/effects_documentation.md`, the event defines in `common/defines/00_defines.lua`, vanilla effect calls in `history/` and `common/`, and message strings in `hoi4.exe`.
- Kit blocks added: event types and how rare state events are, id rules and exceptions, title, desc and picture usage, triggered-only events with `mean_time_to_happen`, major news events, option `ai_chance`, optional keys (`immediate`, `after`, `timeout_days`, `hidden`), arguments of the fire effects, engine log messages.
- Errors found in the wiki text: `major = yes` is not set in every news event (596 of 677 have it); `random_hours` and `random_days` exclude their upper bound.
- Gaps left: no game file documents `timeout_days`, `minor_flavor`, `after` or `original_recipient_only`, and the id collision for non-integer ids was not tested in the game.
**1.19.4.1 re-check (2026-11-01).** 43 statements depended on files the update changed (55 of the 128 `events/` files, `common/decisions/`, `common/on_actions/`, `history/countries/` and `common/defines/00_defines.lua`) and all 43 were re-measured. The event count rose from 6,974 to 6,990 (all 16 new ones are `country_event`), the title, desc, picture, trigger, `ai_chance`, optional-key and effect-call counts moved with it, history files now fire events from 10 files with 20 calls (was 8 and 14), and `common/decisions/ITA.txt` now fires the four non-integer `BBA_italy_missiolinis` events, so the old "no script fires them" is corrected. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="event-types-in-use" at="section:event-creation" -->
Event types in vanilla 1.19.4.1, counted as top-level definitions in `events/*.txt` (128 files, 6,990 events). All rows: [vanilla-confirmed 1.19.4.1] `events/`.

| Type | Events | Files | Notes |
| --- | --- | --- | --- |
| `country_event` | 6,267 | 114 | the default type |
| `news_event` | 677 | 36 | 596 set `major = yes` |
| `unit_leader_event` | 33 | 7 | all set `is_triggered_only = yes` |
| `operative_leader_event` | 7 | 2 | all set `is_triggered_only = yes` |
| `state_event` | 6 | 4 | all set `is_triggered_only = yes` |

- State events are rare: 6 of 6,990 definitions, fired by 10 effects, and every one of those effects is written `state_event = { id = <id> trigger_for = controller }`. [vanilla-confirmed 1.19.4.1] `events/`, `common/on_actions/00_on_actions.txt`, `common/on_actions/07_nsb_on_actions.txt`.
- 6,579 events (94%) set `is_triggered_only = yes`, 9 set it to `no`, and 402 leave it out and are therefore automatic events. [vanilla-confirmed 1.19.4.1] `events/`.
- Effect scopes: `country_event` and `news_event` run in country scope, `state_event` in state or country scope, `unit_leader_event` and `operative_leader_event` in character scope (the event goes to the owner country of the character). [docs] `documentation/effects_documentation.md`.
- `hoi4.exe` contains the message "Event is a leader event and has to be triggered only."; all 40 vanilla leader events (33 `unit_leader_event`, 7 `operative_leader_event`) are triggered only. [vanilla-confirmed 1.19.4.1] `events/`. Always write `is_triggered_only = yes` on them. [unverified] (string in `hoi4.exe`, condition not tested).
<!-- kit:end id="event-types-in-use" -->

<!-- kit:begin id="event-id-vanilla" at="section:id-rules" -->
Event ids in vanilla 1.19.4.1. All items: [vanilla-confirmed 1.19.4.1] `events/`.

- 6,983 of 6,990 events use the plain form `<namespace>.<integer>`. The files hold 436 `add_namespace` lines and none is repeated. The largest numeric part is 2102, so no vanilla id comes near the 100000 limit. 227 ids have leading zeros, such as `namespace.01`.
- Nested namespace (3 events in 2 namespaces): `events/MUN_Czechoslovakia.txt` declares `add_namespace = MUN_czech.news` and defines `MUN_czech.news.1` and `MUN_czech.news.2`; `events/MUN_Slovakia.txt` declares `MUN_slovakia.news` and defines `MUN_slovakia.news.1`.
- Non-integer suffix (4 events): `BBA_italy_missiolinis.02_north`, `.03_north`, `.04_south` and `.05_south` in `events/BBA_Italy.txt`. Only `common/decisions/ITA.txt` fires them (8 calls such as `country_event = { id = BBA_italy_missiolinis.03_north hours = 1 }`), and no script in `events/` or `history/` does.
- Letter case differs from the namespace line in 34 events: 31 events in `events/BBA_Switzerland.txt` use `BBA_switzerland.N` while the file declares `BBA_Switzerland`; 2 events use `taog_news.N` where `TAOG_news` is declared; `NSB_news.200` is declared as `nsb_news`.

Vanilla ships those 34 events. The namespace match ignores case: `add_namespace = IGC_B_G093_Case` matched the event id `igc_b_g093_case.1`, which loaded and fired. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, events fired from the console, game.log read.
The wiki's collision rule for non-integer ids would give the four `BBA_italy_missiolinis` events above the same internal id as `BBA_italy_missiolinis.00`. In a test, an id with a non-integer suffix (`col.x`) beside `col.00` and `col.01` loaded without a message and fired its own effects when called by its own id, so no collision showed, and no "Malformed token" or "Failed to create id" line was written. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, events fired from the console, error.log and game.log read. The test events were hidden with their effects in `immediate`, so options were not tested, and a collision could still exist for something other than console calls.
<!-- kit:end id="event-id-vanilla" -->

<!-- kit:begin id="event-localisation-vanilla" at="section:localisation" -->
Title, desc and options in vanilla 1.19.4.1.

- All 6,803 events that are not hidden have a `title`, a `desc` and at least one `option`. [vanilla-confirmed 1.19.4.1] `events/`.
- Conditional text is common for `desc` and rare for `title`: 214 events use `desc = { text = ... trigger = ... }` blocks and 19 use `title` blocks. [vanilla-confirmed 1.19.4.1] `events/`.
- `hoi4.exe` contains the log messages "Event is missing a title.", "Event is missing a desc." and "Event has no options.", so a visible event without all three is reported. [unverified] (strings in `hoi4.exe`, conditions not tested).
<!-- kit:end id="event-localisation-vanilla" -->

<!-- kit:begin id="event-picture-vanilla" at="section:picture" -->
Picture usage in vanilla 1.19.4.1. All items: [vanilla-confirmed 1.19.4.1] `events/`.

- 6,791 events set a picture: 6,783 write `picture` and 8 write `Picture`. The value is always a single sprite name or a string. 19 events use the scripted localisation form `picture = "[Name]"`; none uses a block form.
- The 8 `Picture` events are in `events/BBA_Ethiopia.txt`, `events/BBA_Switzerland.txt` and `events/LaR_France.txt`. Write the key in lowercase.
<!-- kit:end id="event-picture-vanilla" -->

<!-- kit:begin id="event-triggered-only-mtth" at="section:triggering" -->
Triggered-only events and `mean_time_to_happen` in vanilla 1.19.4.1.

- 6,579 of 6,990 events set `is_triggered_only = yes`. Of the 411 that do not, 375 define `mean_time_to_happen`. 377 events define it in total. [vanilla-confirmed 1.19.4.1] `events/`.
- 301 triggered-only events also carry a `trigger` block, the normal way to gate an event that an effect or an on_action fires. [vanilla-confirmed 1.19.4.1] `events/`.
- Two vanilla events combine `is_triggered_only = yes` with `mean_time_to_happen = { days = 1 }`: `JUNO_brazil_events.202` (`events/TOA_Brazil.txt`, also `hidden = yes`) and `ww_BEL_event_war.3` (`events/WUW_Belgium.txt`). Effects fire both (`country_event = { id = JUNO_brazil_events.202 months = 48 }` in `events/TOA_Brazil.txt`, and `id = ww_BEL_event_war.3 hours = 6` in `common/on_actions/12_wuw_on_actions.txt`), so a triggered-only event with a leftover timer still fires when it is called. [vanilla-confirmed 1.19.4.1]
- The wiki says the timer has no effect on a triggered-only event, which fits both vanilla events being started by effects. `hoi4.exe` has the message "Event is triggered only, but does not have a 1 base-factor." The wording points at the size of the timer, and both vanilla events use `days = 1`, which is also the shape of the wiki's broken example below. When exactly the message is logged is unknown, so leave `mean_time_to_happen` out of every triggered-only event. [unverified] (wiki claim and a string in `hoi4.exe`).
<!-- kit:end id="event-triggered-only-mtth" -->

<!-- kit:begin id="event-major-news" at="section:triggering" -->
The wiki says `major = yes` "is done in every news event". In 1.19.4.1 only 596 of 677 vanilla news events set it, and 81 do not (for example `AAT_norway_news.2` in `events/AAT_Norway.txt`). [vanilla-confirmed 1.19.4.1] `events/`.

- `major` is not limited to news events: `south_american_events.61` and `.62` (country events in `events/TOA_Generic_Events.txt`) set `major = yes`, and the 6 operative leader events in `events/LaR_agent_events.txt` set `major = no`. [vanilla-confirmed 1.19.4.1]
- `show_major = { ... }` appears in 5 news events (`news.44` to `news.47` and `news.124`, all in `events/NewsEvents.txt`). `fire_for_sender = no` appears in 36 news events in `events/NewsEvents.txt` and `events/WTT_NewsEvents.txt`. [vanilla-confirmed 1.19.4.1]
- 7 news events set both `major = yes` and `fire_only_once = yes`: `news.55`, `news.270` to `news.273` and `news.337` (`events/NewsEvents.txt`) and `nuke_dropped.0` (`events/NukeEvents.txt`). The wiki says `fire_only_once` then limits the news to one country; no game file documents the combination. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="event-major-news" -->

<!-- kit:begin id="event-option-ai-chance" at="section:options" -->
Options and `ai_chance` in vanilla 1.19.4.1 (11,572 options in `events/`). All counts: [vanilla-confirmed 1.19.4.1] `events/`.

- 6,268 options (54%) set `ai_chance` and 3,276 set a `trigger`. No vanilla option uses `original_recipient_only`, and the name is in no file under `events/`, `common/`, `history/` or `documentation/`. [vanilla-confirmed 1.19.4.1] The wiki's description stands but is untested. [unverified]
- The 6,270 `ai_chance` blocks have these top-level keys:

| Top-level keys | Blocks |
| --- | --- |
| `base` only | 3,151 |
| `base` and `modifier` | 1,955 |
| `factor` only | 643 |
| `factor` and `modifier` | 515 |
| `modifier` only | 2 |
| empty block | 4 |

- No block mixes a top-level `base` with a top-level `factor`, and `base` is never used inside a `modifier`: modifiers inside `ai_chance` use `factor` (4,836 times) and `add` (1,265 times). The most common `base` values are 10 (1,678 blocks), 1 (784) and 0 (607).
- Prefer `base = N` (81% of vanilla blocks) and put `factor` and `add` inside `modifier` blocks. No file in `documentation/` mentions `ai_chance` at all, and the wiki example that sets `base` and a top-level `factor` together has no vanilla precedent. [vanilla-confirmed 1.19.4.1] A lone top-level `factor` without `base` acts as a weight equal to its value. `factor = 0` was never chosen against `base = 1` (0 of 48, like `base = 0`), and `factor = 10` against `base = 1` was chosen 42 of 48 times (like `base = 10`). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, eight AI countries answering an event for six rounds, game.log read. The 42 of 48 is within chance of the 91 percent that weight 10 against 1 gives.
<!-- kit:end id="event-option-ai-chance" -->

<!-- kit:begin id="event-optional-keys" at="section:additional-arguments" -->
Optional event keys in vanilla 1.19.4.1 (6,990 events). Counts: [vanilla-confirmed 1.19.4.1] `events/`.

| Key | Events | Notes |
| --- | --- | --- |
| `immediate` | 961 | about 14% of all events |
| `hidden = yes` | 185 | 2 more write `Hidden = yes` (`events/USA.txt`); 54 events write `hidden = no` |
| `fire_only_once` | 1,398 | 1,162 `yes`, 236 `no` |
| `after` | 8 | `bftb_turkey.134`, `germany.55`, `MUN_czech.1034`, `MUN_the_fall_of_the_republic.3`, `SEA_japan_foreign_policy.60` and `.67`, `SEA_japan_popup_events.22` and `.29` |
| `timeout_days` | 6 | `AAT_Sweden.28`, `.29` and `.30` use 6; `MUN_czech_skoda_priority.1` uses 30; `MUN_czech.1` uses 1; `MUN_czech.1017` uses 7 |
| `minor_flavor = yes` | 6 | all in `events/AcePilots.txt` |

- Of the 187 hidden events, 116 have no `option` and 71 have one or more (2 of those have several). [vanilla-confirmed 1.19.4.1] `events/`.
- `timeout_days` is rare and no game documentation file describes it. The define `NDefines.NGame.EVENT_TIMEOUT_DEFAULT = 13` is commented as the default number of days before an event times out if not scripted. What the game does when the timeout expires is not documented. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua` for the define. The wiki says the first option is picked, and that held: when a `timeout_days = 2` event ran out unanswered for the player, the first option in the file ran two game days after the event fired. `ai_chance` did not change which option ran, because the first option ran in an event whose second option had `ai_chance = 1000`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, events fired and left unanswered, game.log read. The log does not show whether the popup closed.
- `NDefines.NCountry.EVENT_PROCESS_OFFSET = 20` is commented "Events are checked every X day per country or state", which matches the 20 day trigger check described above. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`.
- No game documentation file explains `after` or `minor_flavor`. Vanilla writes `minor_flavor = yes` in 6 events (all in `events/AcePilots.txt`) and `after = { ... }` 8 times in 4 files. [vanilla-confirmed 1.19.4.1] What `minor_flavor` does is [unverified]. The `after` block runs once, after the chosen option's effects, and can see the flags the option set: in the test the option's effect ran, then `after` ran once and read the option's flag as set. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, popups answered with the first option, game.log read.
<!-- kit:end id="event-optional-keys" -->

<!-- kit:begin id="event-fire-effects" at="section:effect" -->
Delay arguments of the event-firing effects, from `documentation/effects_documentation.md`:

- `hours`, `days` and `months` are added together; a month counts as 30 days. [docs]
- `random_hours` adds a random delay from 0 up to but not including its value, and `random_days` adds one from 0 up to one hour less than its value. The wiki text above says the range includes both ends; the game documentation says the upper bound is excluded. If both are given they are added. [docs]
- `random = 6` is an older spelling of `random_hours = 6`. `random = { chance = 50 ... }` is a different feature: a group of child effects that run with that percentage chance. [docs]
- `tooltip = <loc key>` picks the tooltip text for the effect. No vanilla file uses it. [docs] for the key, [vanilla-confirmed 1.19.4.1] for the absence in `events/`, `common/` and `history/`.

| Effect | Scope | Arguments named in the documentation |
| --- | --- | --- |
| `country_event` | country | `id`, `hours`, `days`, `months`, `random_hours`, `random_days`, `random`, `tooltip` |
| `news_event` | country | the same as `country_event` |
| `state_event` | state or country | the same, plus `trigger_for` (`controller`, `owner`, `occupied`, `from`, `prev`, `root` or a tag) |
| `unit_leader_event` | character | `id`, the delay arguments, `random`, `tooltip` |
| `operative_leader_event` | character | the same as `unit_leader_event`, plus `originator`, `recipient`, `set_root`, `set_from`, `set_from_from` |

All rows: [docs] `documentation/effects_documentation.md`.

- Vanilla calls across `events/`, `common/` and `history/`: `country_event` is written in block form 7,473 times and as `country_event = <id>` 1,505 times; `news_event` 712 block and 13 short; `unit_leader_event` 32 block and 6 short; `state_event` 10; `operative_leader_event` 7, all with `set_from_from`. Inside `country_event` blocks: `hours` 3,724, `days` 2,636, `random_hours` 799, `random_days` 782, `random` 118, `months` 28. [vanilla-confirmed 1.19.4.1]
- There is no effect that cancels, disables or lists a pending delayed event: no effect or trigger in `documentation/effects_documentation.md` or `documentation/triggers_documentation.md` has such a name. [docs]
- To make a pending call harmless, give the target event a `trigger` that tests a flag and clear the flag when the call should lapse. [unverified] The wiki says an event's `trigger` is checked when the delayed event is about to fire, and that held: a delayed triggered-only event was checked against its trigger when it fired, not when it was called. A flag set after the call let the event fire, and an event whose flag was never set did not fire. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, delayed events, game.log read. The case of a flag removed before the event fires was not run.
<!-- kit:end id="event-fire-effects" -->

<!-- kit:begin id="event-engine-messages" at="section:unintuitive-logged-errors" -->
Event log messages found as strings in `hoi4.exe`. All rows: [unverified] (strings read from `hoi4.exe`). A load run tested several of them, and its results are listed under the table.

| Message | Likely cause |
| --- | --- |
| "Event is missing a title." | a visible event without `title` |
| "Event is missing a desc." | a visible event without `desc` |
| "Event has no options." | a visible event without `option` |
| "Event is triggered only, but does not have a 1 base-factor." | `is_triggered_only = yes` together with a `mean_time_to_happen` timer |
| "Event is set to trigger every day." | automatic event with a timer of one day or less that can repeat |
| "Event is a leader event and has to be triggered only." | `unit_leader_event` or `operative_leader_event` without `is_triggered_only = yes` |
| "Malformed token" and "Failed to create id" | namespace problems and duplicate internal ids, as described above |

The first three do not occur in vanilla: every non-hidden vanilla event has a title, a desc and an option. [vanilla-confirmed 1.19.4.1] `events/`.

What a test mod's events logged at load in 1.19.4.1:

- An event with no title, no desc and no option logged "Event is missing a title.", "Event is missing a desc.", "Event has no options." and "Event is set to trigger every day.", plus "non-hidden event with no options defined". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read.
- "Event is set to trigger every day." appeared on non-triggered-only events, including one with no timer whose trigger is never true. It did not appear on a hidden `fire_only_once` event that has no trigger. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read.
- A triggered-only event with a `mean_time_to_happen` timer logged no message, so "Event is triggered only, but does not have a 1 base-factor." did not show. The event could still be called: `event <id> ITA` from the console opened it. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read and console run.
- A `unit_leader_event` that is not triggered only logged only "Event is set to trigger every day.", with nothing about leader events, and a triggered-only leader event logged nothing. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read. Whether an event with a timer repeats every day was not seen.
<!-- kit:end id="event-engine-messages" -->

<!-- kit:begin id="event-history-vanilla" at="section:integration-with-history" -->
Vanilla fires events from country history files in 10 files (`BRA`, `CHL`, `CZE`, `FIN`, `ITA`, `RAJ`, `ROM`, `SOV`, `SWI` and `USA` in `history/countries/`), 20 calls in total, and every call carries a delay (`days` or `months`, in some with `random_days` or `random_hours`). No vanilla history file fires an event without a delay. [vanilla-confirmed 1.19.4.1] `history/countries/`.
<!-- kit:end id="event-history-vanilla" -->
