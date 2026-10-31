# Event modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Event modding", revision 102070, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="102070" sources="events/ history/ common/defines/00_defines.lua documentation/effects_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 128 files in `events/` (6,974 events), the event effects in `documentation/effects_documentation.md`, the event defines in `common/defines/00_defines.lua`, vanilla effect calls in `history/` and `common/`, and message strings in `hoi4.exe`.
- Kit blocks added: event types and how rare state events are, id rules and exceptions, title, desc and picture usage, triggered-only events with `mean_time_to_happen`, major news events, option `ai_chance`, optional keys (`immediate`, `after`, `timeout_days`, `hidden`), arguments of the fire effects, engine log messages.
- Errors found in the wiki text: `major = yes` is not set in every news event (596 of 677 have it); `random_hours` and `random_days` exclude their upper bound.
- Gaps left: no game file documents `timeout_days`, `minor_flavor`, `after` or `original_recipient_only`, and the id collision for non-integer ids was not tested in the game.
<!-- kit:end id="review" -->

## Table of contents

- [Event creation](#Event_creation)
  - [ID rules](#ID_rules)
  - [Localisation](#Localisation)
  - [Picture](#Picture)
  - [Triggering](#Triggering)
  - [Options](#Options)
  - [Additional arguments](#Additional_arguments)
- [Effect](#Effect)
- [Common mistakes](#Common_mistakes)
  - [Unlogged errors](#Unlogged_errors)
  - [Unintuitive logged errors](#Unintuitive_logged_errors)
- [Event file example](#Event_file_example)
  - [Integration with on actions](#Integration_with_on_actions)
  - [Integration with history](#Integration_with_history)
- [Notes and references](#Notes_and_references)

---

Events are defined in the `/Hearts of Iron IV/events/` folder. There are several types of events, changing the appearance or the target of the events.

The list of event types includes `country_event`, `news_event`, `state_event`, `unit_leader_event`, and `operative_leader_event`.

In each event type, the ROOT [scope](<Scopes - Hearts of Iron 4 Wiki.md>) refers to the country getting the event, however, the default assumed scope, also known as THIS, is not always purely the country. In state events, operative leader events, and unit leader events, the assumed scope is *both* the country and the event-specific scope type, accepting effects for either scope, sorting them at will. In case of overlap between something being possible for the country or the other scope (e.g. `add_manpower` being both a state- and country-scoped effect), the country is preferred.
Due to this confusion, it is recommended to avoid state events as they appear identical to country events ([Event targets](<Data structures - Hearts of Iron 4 Wiki.md>) can be used within country events aimed to a specific state instead), however unit leader and operative leader events can be unavoidable due to their distinct appearance. **There is nearly no difference between event types**, with the exception of appearance, default scopes, and the fact that news event can have their pop-up disabled (However, the country will still get them). If the player country gets an event and doesn't pick a choice, the first option will get assumed by default.

When [fired using an effect](<Effects - Hearts of Iron 4 Wiki.md>), the game ports over the [regular event targets](<Data structures - Hearts of Iron 4 Wiki.md>) existing in the previous effect block to the event, as well as the ROOT scope of the block, which becomes FROM within the event. The previous effect block's FROM scopes get shifted one level down, with the effect block's FROM becoming FROM.FROM, previous FROM.FROM becoming FROM.FROM.FROM, and et cetera. Due to this, FROM is commonly called the 'sender' of the event in jargon, making FROM.FROM the sender to the sender. Although this does not always apply, as FROM.FROM can be something else entirely, e.g. [an additional scope within on actions](<On actions - Hearts of Iron 4 Wiki.md>) or [the target of a decision](<Decision modding - Hearts of Iron 4 Wiki.md#Targeted_decisions>). Importantly, it's what the FROM block of the effect block that fired it is, which depends on where it's fired exactly.
This does not happen if the event gets fired using an on action's random_events block: the same scoping rules as in the regular on action apply.

A country that doesn't exist may still get events [if fired via an effect](#Effect), but any other method doesn't work. However, if there's a time delay set in the effect that fires it, the timers in each delayed_event`[a]` will not decrease. This effectively puts any events with a time delay onto a backlog of the country, put on hold until it gets released. For example, if BHR doesn't exist when `BHR = { country_event = { id = event.0 days = 1 } }` is executed, then the event will only fire a day after BHR starts existing. This also applies to the original recipient of major events.

## Event creation <a id="Event_creation"></a>

Each event is contained within a code block corresponding to the event type, such as `country_event` or `news_event`. Within the event, a mandatory line is `id`, corresponding to the event's ID, such as `id = my_event.123`.

<!-- kit:begin id="event-types-in-use" at="section:Event_creation" -->
**Kit addition** Event types in vanilla 1.19.3, counted as top-level definitions in `events/*.txt` (128 files, 6,974 events). All rows: [vanilla-confirmed 1.19.3] `events/`.

| Type | Events | Files | Notes |
| --- | --- | --- | --- |
| `country_event` | 6,251 | 114 | the default type |
| `news_event` | 677 | 36 | 596 set `major = yes` |
| `unit_leader_event` | 33 | 7 | all set `is_triggered_only = yes` |
| `operative_leader_event` | 7 | 2 | all set `is_triggered_only = yes` |
| `state_event` | 6 | 4 | all set `is_triggered_only = yes` |

- State events are rare: 6 of 6,974 definitions, fired by 10 effects, and every one of those effects is written `state_event = { id = <id> trigger_for = controller }`. [vanilla-confirmed 1.19.3] `events/`, `common/on_actions/00_on_actions.txt`, `common/on_actions/07_nsb_on_actions.txt`.
- 6,574 events (94%) set `is_triggered_only = yes`, 9 set it to `no`, and 391 leave it out and are therefore automatic events. [vanilla-confirmed 1.19.3] `events/`.
- Effect scopes: `country_event` and `news_event` run in country scope, `state_event` in state or country scope, `unit_leader_event` and `operative_leader_event` in character scope (the event goes to the owner country of the character). [docs] `documentation/effects_documentation.md`.
- `hoi4.exe` contains the message "Event is a leader event and has to be triggered only."; all 40 vanilla leader events are triggered only, so always write `is_triggered_only = yes` on them. [unverified] (string in `hoi4.exe`, condition not tested).
<!-- kit:end id="event-types-in-use" -->

### ID rules <a id="ID_rules"></a>

Within an event file, all events have to have an ID in the format of `<namespace>.<integer ID>`. For example, in an event `my_event.123`, the namespace will be "my_event", while the ID is "123".

**A namespace must be first created** before defining any events that use it. This is done with the line `add_namespace = my_event` **which must be outside of any event**. If a namespace is not defined, then the event ID will be considered a malformed token, leading it to not working in-game. The event namespace consists of word characters (e.g. letters of the English alphabet or underscores). This includes dots: `add_namespace = my_event.subtopic` can be used for events of the type of `id = my_event.subtopic.1`. The numeric ID will be taken to be everything after the last dot converted to an integer, or 0 if the conversion fails.

Internal IDs are defined for events by assigning an ID to each namespace (IDs are assigned in the order in the code, files being loaded by filename in the character order), with the first-defined namespace being assigned an ID of 10, incrementing it by 1 for each next created namespace, multiplying it by 100000, and adding the integer ID. If the ID after the namespace fails conversion to an integer, then it'll default to 0. For this reason, every event with a non-integer ID will be considered the same event, so **the ID of the event after the namespace must be an integer**.

<!-- kit:begin id="event-id-vanilla" at="section:ID_rules" -->
**Kit addition** Event ids in vanilla 1.19.3. All items: [vanilla-confirmed 1.19.3] `events/`.

- 6,967 of 6,974 events use the plain form `<namespace>.<integer>`. The files hold 436 `add_namespace` lines and none is repeated. The largest numeric part is 2102, so no vanilla id comes near the 100000 limit. 225 ids have leading zeros, such as `namespace.01`.
- Nested namespace (3 events in 2 namespaces): `events/MUN_Czechoslovakia.txt` declares `add_namespace = MUN_czech.news` and defines `MUN_czech.news.1` and `MUN_czech.news.2`; `events/MUN_Slovakia.txt` declares `MUN_slovakia.news` and defines `MUN_slovakia.news.1`.
- Non-integer suffix (4 events): `BBA_italy_missiolinis.02_north`, `.03_north`, `.04_south` and `.05_south` in `events/BBA_Italy.txt`. No script in `events/`, `common/` or `history/` fires them.
- Letter case differs from the namespace line in 34 events: 31 events in `events/BBA_Switzerland.txt` use `BBA_switzerland.N` while the file declares `BBA_Switzerland`; 2 events use `taog_news.N` where `TAOG_news` is declared; `NSB_news.200` is declared as `nsb_news`.

Vanilla ships those 34 events, so the namespace match looks case-insensitive, but that is only an inference from the files; keep the case identical anyway. [unverified]
The wiki's collision rule for non-integer ids would give the four `BBA_italy_missiolinis` events above the same internal id as `BBA_italy_missiolinis.00`; this was not tested. [unverified]
<!-- kit:end id="event-id-vanilla" -->

### Localisation <a id="Localisation"></a>

The lines `title` and `desc` are used to assign a [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key to the event, creating its title and description depending on the current language of the game. An example line is `title = my_event.123.t` or `desc = my_event_description`. An event is required to have a title or a description unless it is hidden.

Localisation is defined in the `/Hearts of Iron IV/localisation/english/` folder for the English language. It is preferable to use a new file in the folder instead of overwriting any base game files. The newly-created file will have to end with `_l_english.yml` in its filename (Note that it is a lowercase L, not an uppercase i) for it to be loaded properly. Additionally, it has to use the UTF-8-BOM text encoding. Exact details on how to change the encoding depend on the text editor used. Within the file, assuming that `l_english:` is already added as the first line, localisation can be added as such:

```text
 my_event.123.t: "My event title"
 my_event_description: "My event description"
```

It is also possible to add multiple titles and descriptions to an event, making it choose one depending on conditions. This is done as the following:

```text
title = {
    text = my_event.123.t.a
    trigger = {
        tag = ENG
    }
}
title = {
    text = my_event.123.t.b
}
```

The game will choose the first localisation key where the conditions are met. In this case, the event title will use the my_event.123.t.a localisation key if the country receiving the event has the tag of ENG, and every other country will have the event title use the my_event.123.t.b localisation key. `trigger` is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block, requiring all of the triggers inside to be true by default. The formatting for event descriptions is the same, with `title` changed for `desc`.

<!-- kit:begin id="event-localisation-vanilla" at="section:Localisation" -->
**Kit addition** Title, desc and options in vanilla 1.19.3.

- All 6,788 events that are not hidden have a `title`, a `desc` and at least one `option`. [vanilla-confirmed 1.19.3] `events/`.
- Conditional text is common for `desc` and rare for `title`: 212 events use `desc = { text = ... trigger = ... }` blocks and 13 use `title` blocks. [vanilla-confirmed 1.19.3] `events/`.
- `hoi4.exe` contains the log messages "Event is missing a title.", "Event is missing a desc." and "Event has no options.", so a visible event without all three is reported. [unverified] (strings in `hoi4.exe`, conditions not tested).
<!-- kit:end id="event-localisation-vanilla" -->

### Picture <a id="Picture"></a>

In order to add a picture to be shown for the event, the `picture` argument is used with the name of the sprite leading to the file of the picture, such as `picture = GFX_my_sprite`.

Sprites are defined in any `/Hearts of Iron IV/interface/*.gfx` file, by default using eventpictures.gfx, opened within any text editor. It is recommended to create a new file in the folder instead of using a base game file in the mod for update compatibility reasons.
Within the `/Hearts of Iron IV/interface/*.gfx` file of your choice, the following lines can be added within the `spriteTypes = { ... }` block to define a sprite:

```text
spriteType = {
    name = "GFX_my_sprite"
    texturefile = "gfx/event_pictures/my_event_picture.dds"
}
```

After creating this sprite, the file `<yourmod>/gfx/event_pictures/my_event_picture.dds` can be used within an event as `picture = GFX_my_sprite`

Picture can be made dynamic, using [scripted localisation](<Localisation - Hearts of Iron 4 Wiki.md#Scripted_localisation>). To achieve this, one must use `picture = "[SomeScriptedLocalisationTitle]"`, with actual event pictures defined in scripted localisation (as its `localization_key` variants), for example

```text
defined_text = {
	name = SomeScriptedLocalisationTitle
	text = {
		trigger = {
			(conditions...)
		}
		localization_key = GFX_my_alternate_sprite
	}
	text = {
		trigger = {
			(other conditions...)
		}
		localization_key = GFX_my_another_alternate_sprite
	}
	(...)
	# Default picture
	text = {
		localization_key = GFX_my_sprite
	}
}
```

<!-- kit:begin id="event-picture-vanilla" at="section:Picture" -->
**Kit addition** Picture usage in vanilla 1.19.3. All items: [vanilla-confirmed 1.19.3] `events/`.

- 6,775 events set a picture: 6,767 write `picture` and 8 write `Picture`. The value is always a single sprite name or a string. 18 events use the scripted localisation form `picture = "[Name]"`; none uses a block form.
- The 8 `Picture` events are in `events/BBA_Ethiopia.txt`, `events/BBA_Switzerland.txt` and `events/LaR_France.txt`. Write the key in lowercase.
<!-- kit:end id="event-picture-vanilla" -->

### Triggering <a id="Triggering"></a>

The `trigger = { ... }` block of [triggers](<Triggers - Hearts of Iron 4 Wiki.md>) is used to declare conditions that must be met so that the event is possible to appear. If it's false, there's no way to fire the event aside from using [the console command](<Console commands - Hearts of Iron 4 Wiki.md>). This will look like the following:

```text
trigger = {
    tag = GER
    has_political_power > 100
}
```

If the event is fired in console, the trigger will be written into it as the contents of a regular trigger tooltip, highlighting which conditions were met and which were not.

By default, the event will fire automatically. This consists of the trigger being checked every 20 days.[1] If it is true, it changes to checking the `mean_time_to_happen = { ... }` daily. That is a modified MTTH block: it is evaluated for a country and returns an amount of days; if the returned amount of days is `M` the chance for an event to fire on that day is `1-2^{-{\frac {1}{M}}}`, making this a median time to happen. If the trigger is false on a daily check, it reverts to checking the trigger every 20 days.

`mean_time_to_happen = { ... }` has the attributes of `days`, `months`, and `years` to decide the base amount of days. A month is interpreted as being 30 days, a year is interpreted as being 365 days. If the amount of days should be dynamic, `modifier = { ... }` serves as a trigger block with additional attributes of `add = 123` (adding that amount of days) and `factor = 0.2` (multiplying the amount of days by the specified number). The modifiers are evaluated in the order that they're placed in, and they support [variables](<Data structures - Hearts of Iron 4 Wiki.md>) in the argument. An example mean time to happen looks like the following:

```text
mean_time_to_happen = {
    days = 10
    years = 1  # 375 days as the base.
    modifier = {
        factor = 0.2        #  Takes 20% as much to fire for POL, or 75 days.
        tag = POL
    }
}
```

The automatic firing can be disabled by adding `is_triggered_only = yes` into the event. This doesn't prevent any other way to fire the event, whether by the [effect used to do so](#Effect), an [on action](<On actions - Hearts of Iron 4 Wiki.md>)'s `random_events`, [a border war](<Effects - Hearts of Iron 4 Wiki.md#Border_wars>), or anything else. This is entirely unrelated to `trigger = { ... }`: the conditions within must still be fulfilled for either of these to be possible to fire an event. If the [effect used to fire an event](#Effect) (e.g. country_event or state_event) is set with a delay, then the trigger must be true when the event is intended to be fired.

`fire_only_once = yes` makes the event impossible to fire more than once. This is checked within the event itself: a country getting the event will also prevent any other country from receiving it. This is bypassed by using [the console command](<Console commands - Hearts of Iron 4 Wiki.md>).

`major = yes` is used to make the event fire for every country once any country receives it. **This is done in every news event**, since news events are purely a graphical reskin of country events. In case of overlap with `fire_only_once = yes`, the latter will take priority and remove any effect of the event being major, making it only appear for the country receiving it for the first time. Countries other than the first country receiving it will ignore `trigger = { ... }`. To make only some countries get the event shown while it's still major, `show_major = { ... }` is used as a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that makes the event show up only if it's true. If `fire_for_sender = no` is also added, the event will fire for every country that meets `show_major` aside from the country that was intended to receive it.

<!-- kit:begin id="event-triggered-only-mtth" at="section:Triggering" -->
**Kit addition** Triggered-only events and `mean_time_to_happen` in vanilla 1.19.3.

- 6,574 of 6,974 events set `is_triggered_only = yes`. Of the 400 that do not, 373 define `mean_time_to_happen`; 375 events define it in total. [vanilla-confirmed 1.19.3] `events/`.
- 298 triggered-only events also carry a `trigger` block, the normal way to gate an event that an effect or an on_action fires. [vanilla-confirmed 1.19.3] `events/`.
- Two vanilla events combine `is_triggered_only = yes` with `mean_time_to_happen = { days = 1 }`: `JUNO_brazil_events.202` (`events/TOA_Brazil.txt`, also `hidden = yes`) and `ww_BEL_event_war.3` (`events/WUW_Belgium.txt`). Effects fire both (`country_event = { id = JUNO_brazil_events.202 months = 48 }` in `events/TOA_Brazil.txt`, and `id = ww_BEL_event_war.3 hours = 6` in `common/on_actions/12_wuw_on_actions.txt`), so a triggered-only event with a leftover timer still fires when it is called. [vanilla-confirmed 1.19.3]
- The wiki says the timer has no effect on a triggered-only event, which fits both vanilla events being started by effects. `hoi4.exe` has the message "Event is triggered only, but does not have a 1 base-factor." The wording points at the size of the timer, and both vanilla events use `days = 1`, which is also the shape of the wiki's broken example below. When exactly the message is logged is unknown, so leave `mean_time_to_happen` out of every triggered-only event. [unverified] (wiki claim and a string in `hoi4.exe`).
<!-- kit:end id="event-triggered-only-mtth" -->

<!-- kit:begin id="event-major-news" at="section:Triggering" -->
**Kit correction** The wiki says `major = yes` "is done in every news event". In 1.19.3 only 596 of 677 vanilla news events set it, and 81 do not (for example `AAT_norway_news.2` in `events/AAT_Norway.txt`). [vanilla-confirmed 1.19.3] `events/`.

- `major` is not limited to news events: `south_american_events.61` and `.62` (country events in `events/TOA_Generic_Events.txt`) set `major = yes`, and the 6 operative leader events in `events/LaR_agent_events.txt` set `major = no`. [vanilla-confirmed 1.19.3]
- `show_major = { ... }` appears in 5 news events (`news.44` to `news.47` and `news.124`, all in `events/NewsEvents.txt`). `fire_for_sender = no` appears in 36 news events in `events/NewsEvents.txt` and `events/WTT_NewsEvents.txt`. [vanilla-confirmed 1.19.3]
- 7 news events set both `major = yes` and `fire_only_once = yes`: `news.55`, `news.270` to `news.273` and `news.337` (`events/NewsEvents.txt`) and `nuke_dropped.0` (`events/NukeEvents.txt`). The wiki says `fire_only_once` then limits the news to one country; no game file documents the combination. [vanilla-confirmed 1.19.3]
<!-- kit:end id="event-major-news" -->

### Options <a id="Options"></a>

An event option is added with an `option = { ... }` block. An event option is an [effect](<Effects - Hearts of Iron 4 Wiki.md>) block, with a few extra options:

`name` decides the localisation key used for the option, such as `name = my_option_name`. It is not possible to make the option name depend on the triggers in the same way it's possible for event titles, instead, completely different event options can be used, disabling each one with a name that shouldn't be used.

`trigger = { ... }` is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block, deciding when the option is visible to be picked. If the trigger is false at the time of being fired, it will not appear until the event is fired again. Additionally, for major events, `original_recipient_only = yes` can be used to ensure that only the country that fired the event has this option available, with others not having it.

`ai_chance = { ... }` is a block deciding the [AI chance](<AI modding - Hearts of Iron 4 Wiki.md>) for event options: deciding in a proportional way which option to pick. The AI chance in event options do not have to add up to 100, as it is proportional. It is structured in a near-identical way to the mean time to happen. If unset, assumed to be 1. The probability of each option is its weight divided by the sum of all option weights. If all options have a weight of zero, the first one is chosen. The randomized choice is made by rolling a d100, so options can't have an effective non-zero probability below 1%. The choice remains consistent across reloads, based on unique game seed, in-game time, country, and unit leader.

As a MTTH block, the attributes are in the form of `base = 10`, `factor = 0.1`, `add = 10`, with `modifier = { ... }` serving as trigger blocks:

```text
ai_chance = {
    base = 10.5

    # If the country is Germany, set the value to 0,
    # causing an early end of the evaluation.
    modifier = { tag = GER factor = 0 }
    modifier = { is_major = yes add = 1 }
    modifier = {
        factor = 3
        add = 2.5
        tag = FRA
    }
    factor = 2
}
```

<!-- kit:begin id="event-option-ai-chance" at="section:Options" -->
**Kit addition** Options and `ai_chance` in vanilla 1.19.3 (11,547 options in `events/`). All counts: [vanilla-confirmed 1.19.3] `events/`.

- 6,247 options (54%) set `ai_chance` and 3,275 set a `trigger`. No vanilla option uses `original_recipient_only`; the token exists in `hoi4.exe`, so the wiki's description stands but is untested. [unverified]
- The 6,249 `ai_chance` blocks have these top-level keys:

| Top-level keys | Blocks |
| --- | --- |
| `base` only | 3,138 |
| `base` and `modifier` | 1,947 |
| `factor` only | 643 |
| `factor` and `modifier` | 515 |
| `modifier` only | 2 |
| empty block | 4 |

- No block mixes a top-level `base` with a top-level `factor`, and `base` is never used inside a `modifier`: modifiers inside `ai_chance` use `factor` (4,806 times) and `add` (1,262 times). The most common `base` values are 10 (1,678 blocks), 1 (775) and 0 (604).
- Prefer `base = N` (81% of vanilla blocks) and put `factor` and `add` inside `modifier` blocks. No game document defines how a top-level `factor` behaves when `base` is absent, and the wiki example that sets `base` and a top-level `factor` together has no vanilla precedent. [unverified]
<!-- kit:end id="event-option-ai-chance" -->

### Additional arguments <a id="Additional_arguments"></a>

`immediate = { ... }` is an [effect](<Effects - Hearts of Iron 4 Wiki.md>) block, executed as soon as the event is fired, before an option is chosen by the player. This can also be used for AI: AI only picks an option after the event triggers are evaluated for every other country, while immediate is executed immediately, before evaluating other events. This can be used in mean-time-to-happen type major events: by making the immediate set a global flag, which is required to be unset in the event trigger, this will prevent it from being fired more than once for each country, but it is preferable to avoid mean-time-to-happen events in entirety. Note that the effect will appear in the tooltip after the event's description, so the [hidden_effect](<Effects - Hearts of Iron 4 Wiki.md#Tooltip_manipulation>) flow tool can be helpful.

`after = { ... }` is an [effect](<Effects - Hearts of Iron 4 Wiki.md>) block, executed at the end of the event after an option is chosen by the player (as opposed to "immediate"). Introduced with War Effort | Patch 1.16.9

`timeout_days = 20` sets the amount of days that the player has to pick an option before the first option is automatically selected. This can be used to make the event be more or less urgent than default. If unset, assumed to be 13 days.[2]

`hidden = yes` will make an event hidden. A hidden event does not need a title or a description. The first defined option, if one is present, will be automatically picked upon being fired. Hidden events can be useful instead of [scripted effects](<Effects - Hearts of Iron 4 Wiki.md>) to delay the execution of an effect block by a period of time or to utilise the FROM scope.

`minor_flavor = yes` marks the event as being a minor flavour event. This does not change its appearance or change its effects, but allows turning off the pop-up within the game's decision menu.

<!-- kit:begin id="event-optional-keys" at="section:Additional_arguments" -->
**Kit addition** Optional event keys in vanilla 1.19.3 (6,974 events). Counts: [vanilla-confirmed 1.19.3] `events/`.

| Key | Events | Notes |
| --- | --- | --- |
| `immediate` | 959 | about 14% of all events |
| `hidden = yes` | 184 | 2 more write `Hidden = yes` (`events/USA.txt`); 54 events write `hidden = no` |
| `fire_only_once` | 1,391 | 1,155 `yes`, 236 `no` |
| `after` | 8 | `bftb_turkey.134`, `germany.55`, `MUN_czech.1034`, `MUN_the_fall_of_the_republic.3`, `SEA_japan_foreign_policy.60` and `.67`, `SEA_japan_popup_events.22` and `.29` |
| `timeout_days` | 6 | `AAT_Sweden.28`, `.29` and `.30` use 6; `MUN_czech_skoda_priority.1` uses 30; `MUN_czech.1` uses 1; `MUN_czech.1017` uses 7 |
| `minor_flavor = yes` | 6 | all in `events/AcePilots.txt` |

- Of the 186 hidden events, 116 have no `option` and 70 have one or more (2 of those have several). [vanilla-confirmed 1.19.3] `events/`.
- `timeout_days` is rare and no game documentation file describes it. The define `NDefines.NGame.EVENT_TIMEOUT_DEFAULT = 13` is commented as the default number of days before an event times out if not scripted. What the game does when the timeout expires is not documented; the wiki says the first option is picked. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` for the define; [unverified] for the behaviour.
- `NDefines.NCountry.EVENT_PROCESS_OFFSET = 20` is commented "Events are checked every X day per country or state", which matches the 20 day trigger check described above. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.
- No game documentation file explains `after` or `minor_flavor`; both tokens exist in `hoi4.exe`. [unverified]
<!-- kit:end id="event-optional-keys" -->

## Effect <a id="Effect"></a>

Any [effect block](<Effects - Hearts of Iron 4 Wiki.md>) can be used to fire an event, such as focus rewards, [event options](#Options), or decision effects. This is usually paired with `is_triggered_only = yes` within the event as to disable automatic firing.

In its simplest way, this is done with the effect of `country_event = my_event.1` (or `news_event = my_event.1`), which'll instantly fire the event for the scoped country. As country and news events are the exact same thing under the surface, both shortened effects can be used for either country and news events, with there being no difference between them whatsoever.
However, more options can be added primarily for setting up the delay. Additionally, expanded versions are mandatory for state and operative leader events.

A more complex effect to fire is `country_event = { id = my_event.1 days = 100 random_days = 123 }`. This'll fire the event in 100 to 223 (`100+123`) days. There are the following arguments that can go into the effect (All of them are optional with one exception):

- `id = my_event.1` — The ID of the event to fire. This is mandatory as to let the game know which event to fire.
- `hours = 1`|`days = 2`|`months = 3` — The lower bound on the needed time that the event will fire in. In this case, a month is treated as exactly 30 days. If multiple of these are used, the game will add them up together (e.g. the example with 1 hour, 2 days, and 3 months will fire in 92 days and 1 hour).
- `random_hours = 1`|`random_days = 2` — This sets the upper bound on the needed time that the event will fire in. The game selects a random amount (uniform distribution) of days and hours between 0 and the set amount, including both ends, and adds them to the delay to fire the event. Similarly to above, if both are specified, the game will add them together. `random = 123` also serves as an equivalent for `random_hours = 123`.
- `tooltip = my_event.1.t` — This decides what the name of the event that would fire would be displayed as in localisation. Defaults to the event's name, this may be useful if the title may change between the effect to fire it and its actual appearance.

Example effect using several of these parameters:

```text
country_event = {
    id = my_event.1
    hours = 12
    random_hours = 6
    days = 2
    tooltip = another_event.1.t
}
```

The optional delay is incredibly useful, as hidden events can be used to create a delay between an effect block's execution and the actual application of effects without the player detecting anything. This can also be used to make the events appear more "natural": news events can have a delay of a few hours (typically around 6-12) in order to simulate the time it takes for the news agencies to report on the event. Similarly can be done with other event types to simulate waiting a few hours for a diplomatic response, rather than it being unnaturally instant.
`trigger = { ... }` of the event gets checked when it would fire, meaning that it's also possible to [fire the event on startup of the game](<On actions - Hearts of Iron 4 Wiki.md>) with a needed delay to get it on a specific day, then use the event's trigger to simulate additional requirements.

Additionally, there are these event type-specific arguments:

- `trigger_for = TAG` (Unique to state events) — The country for which the event will fire for. This is mandatory as state events are to be fired in state scope. This can also be replaced with `controller`, `owner`, `occupied`, or a [dual scope that can be used as a target](<Scopes - Hearts of Iron 4 Wiki.md#Dual_scopes>), such as ROOT or FROM.
- `originator = TAG` (Unique to operative leader events) — The country which serves as the originator of the event (i.e. FROM). Defaults to the operative's owner if unset.
- `recipient = TAG` (Unique to operative leader events) — The country which would receive the event. Defaults to the operative's owner if unset.
- `set_root = TAG` (Unique to operative leader events) — Changes the scope of ROOT within the dynamic localisation of the event, without actually changing it in code.
- `set_from = TAG` (Unique to operative leader events) — Changes the scope of FROM within the dynamic localisation of the event, without actually changing it in code.
- `set_from_from = TAG` (Unique to operative leader events) — Changes the scope of FROM.FROM within the dynamic localisation of the event, without actually changing it in code.

<!-- kit:begin id="event-fire-effects" at="section:Effect" -->
**Kit correction** Delay arguments of the event-firing effects, from `documentation/effects_documentation.md`:

- `hours`, `days` and `months` are added together; a month counts as 30 days. [docs]
- `random_hours` adds a random delay from 0 up to but not including its value, and `random_days` adds one from 0 up to one hour less than its value. The wiki text above says the range includes both ends; the game documentation says the upper bound is excluded. If both are given they are added. [docs]
- `random = 6` is an older spelling of `random_hours = 6`. `random = { chance = 50 ... }` is a different feature: a group of child effects that run with that percentage chance. [docs]
- `tooltip = <loc key>` picks the tooltip text for the effect. No vanilla file uses it. [docs] for the key, [vanilla-confirmed 1.19.3] for the absence in `events/`, `common/` and `history/`.

| Effect | Scope | Arguments named in the documentation |
| --- | --- | --- |
| `country_event` | country | `id`, `hours`, `days`, `months`, `random_hours`, `random_days`, `random`, `tooltip` |
| `news_event` | country | the same as `country_event` |
| `state_event` | state or country | the same, plus `trigger_for` (`controller`, `owner`, `occupied`, `from`, `prev`, `root` or a tag) |
| `unit_leader_event` | character | `id`, the delay arguments, `random`, `tooltip` |
| `operative_leader_event` | character | the same as `unit_leader_event`, plus `originator`, `recipient`, `set_root`, `set_from`, `set_from_from` |

All rows: [docs] `documentation/effects_documentation.md`.

- Vanilla calls across `events/`, `common/` and `history/`: `country_event` is written in block form 7,457 times and as `country_event = <id>` 1,506 times; `news_event` 711 block and 13 short; `unit_leader_event` 32 block and 6 short; `state_event` 10; `operative_leader_event` 7, all with `set_from_from`. Inside `country_event` blocks: `hours` 3,709, `days` 2,633, `random_hours` 797, `random_days` 781, `random` 118, `months` 28. [vanilla-confirmed 1.19.3]
- There is no effect that cancels, disables or lists a pending delayed event: no effect or trigger in `documentation/effects_documentation.md` or `documentation/triggers_documentation.md` has such a name. [docs]
- To make a pending call harmless, give the target event a `trigger` that tests a flag and clear the flag when the call should lapse. The wiki says an event's `trigger` is checked when the delayed event is about to fire. [unverified]
<!-- kit:end id="event-fire-effects" -->

## Common mistakes <a id="Common_mistakes"></a>

Some errors are quite common to make when beginning to make events, whether it's poor practice or if it would prevent the event from working in entirely. Some of them may be hard to notice when modding, with the event seemingly working fine, such as the error that prevents news events from being fired for more than one country.
This covers some of them, as well as the less intuitive errors in the log.

### Unlogged errors <a id="Unlogged_errors"></a>

- **Leaving an event as triggered only when it's to be fired automatically** (*Event never fires*) – `is_triggered_only = yes` disables the automatic firing of the event, instead enforcing [using the effect to do so](<Effects - Hearts of Iron 4 Wiki.md>). Therefore, if it is left in within an event intended to fire automatically, the event will never do so.

Note that `trigger = { ... }` can still co-exist with `is_triggered_only = yes`, so an event with both `is_triggered_only = yes` and `trigger = { ... }` may still be correct. Valid usages of them at the same time include the event being triggered via an [on action](<On actions - Hearts of Iron 4 Wiki.md>)'s `random_events` or the effect firing it has a delay (where the trigger would check if when the event is to be received), along others.

**Example event with this issue and a correction to it**

**Broken:**

```text
country_event = {
    id = my_event.1
    title = my_event.1.t
    desc = my_event.1.desc

    trigger = {
        tag = GHA
        has_stability > 0.9
    }
    fire_only_once = yes
    is_triggered_only = yes  # Will make the event never automatically trigger.

    option = {
        name = my_event.1.a
        add_war_support = 0.2
    }
}
```

**Corrected:**

```text
country_event = {
    id = my_event.1
    title = my_event.1.t
    desc = my_event.1.desc

    trigger = {
        tag = GHA
        has_stability > 0.9
    }
    fire_only_once = yes

    option = {
        name = my_event.1.a
        add_war_support = 0.2
    }
}
```

- **Not checking the country in the trigger for country-specific auto-triggered events** (*Event fires for the wrong country/never fires*) – The events are not assigned to countries in any way (namespaces and filenames serve a purely organisational purpose), and each event trigger is checked for each country in order specified in the tag list.

In the provided example, the event requires ITA to have more than 123 political power, upon which the country receiving the event would annex AUS. However, once ITA has that much, this trigger would be true *regardless* of where it's checked. The first country in the taglist by default is GER, and so it'll be the first country where the triggers are checked. In practice, this event will result in GER annexing AUS rather than ITA.
In the correction, a change is made: first it checks that the country that would receive the event is ITA, and only then then it checks that it has more than enough political power. This makes sure that no other countries can receive this event. Specifying the tag is unnecessary if the trigger itself already implies a certain tag (e.g. `has_completed_focus` with a tag-specific focus tree), but is needed otherwise.

**Example event with this issue and a correction to it**

```text
country_event = {
    id = my_event.1     # Broken event
    title = my_event.1.t
    desc = my_event.1.desc

    trigger = {
        ITA = { has_political_power > 123 }  # Either true within every country's scope or for none
    }                                        # First fires for GER, since it's true in GER's scope and GER is the first country.
    fire_only_once = yes

    option = {
        name = my_event.1.a
        annex_country = { target = AUS }     # Results in GER annexing AUS instead of ITA as intended.
    }
}
country_event = {
    id = my_event.2     # Fixed version
    title = my_event.2.t
    desc = my_event.2.desc

    trigger = {
        tag = ITA                       # Checks that the country is ITA
        has_political_power > 123       # Checks current political power of ITA (as any other country is disqualified by the previous trigger)
    }
    fire_only_once = yes

    option = {
        name = my_event.2.a
        annex_country = { target = AUS }
    }
}
```

- **Unnecessarily using auto-triggered events instead of ones that are triggered only** (*Poor practice/optimisation*) – This is more of a poor practice than an error. In general, if an event's condition can be triggered with an effect, it should be.

The example is the most obvious way of doing this: a [has_completed_focus check](<Triggers - Hearts of Iron 4 Wiki.md>) instead of firing it directly in the focus. However, other such cases can occur, e.g. when a war starts between two countries, when a state gets occupied, or for firing one on a specific date. It's best practice to check [on actions](<On actions - Hearts of Iron 4 Wiki.md>) before creating an automatically-triggered event to see if they can be made to replicate.
Firing it via an effect has a purpose of being instant instead of having to wait up to 20 days. If so desired, a delay of a few hours can be added to make it appear more natural to the player. Additionally, it serves as a way to optimise the modification, as this reduces the amount of trigger checks repeatedly done. Events with a large mean-time-to-happen are particularly awful for performance and can be replaced with an effect block firing one with a large [delay created with random_days within the effect](<Effects - Hearts of Iron 4 Wiki.md>) in some cases.

**Example event with this issue and a correction to it**

**Broken event:**

```text
country_event = {
    id = my_event.1
    title = my_event.1.t
    desc = my_event.1.desc

    trigger = {
        has_completed_focus = TAG_focus_name
    }
    fire_only_once = yes

    option = {
        name = my_event.1.a
    }
}
```

**Corrected event and focus:**

```text
country_event = {
    id = my_event.1
    title = my_event.1.t
    desc = my_event.1.desc

    is_triggered_only = yes

    option = {
        name = my_event.1.a
    }
}
```

```text
focus = {
    id = TAG_focus_name
    x = 5
    y = 0
    icon = GFX_focus_icon_name

    cost = 8
    search_filters = { FOCUS_FILTER_POLITICAL }

    completion_reward = {
        country_event = { id = my_event.1 hours = 6 random_hours = 3 }  # Fires the event in 6-9 hours.
    }
}
```

- **Tight bounds on date triggers** (*Event never fires*)/**Auto-triggered event intended to be fired at a specific date** (*Event fires later than intended*) – The `trigger = { ... }` block is checked every 20 days by default, and this isn't possible to change for just one event in particular. If the date triggers are set with tight upper and lower bounds (e.g. `date > 1936.1.1` and `date < 1936.1.3`), it's very likely that the event will never fire, as this will not force the game to check the trigger at that date, but just prevent it from firing the event if the range is never checked, as the game doesn't see into the future and cannot predict that the trigger will be true or false at some point. Similarly, just placing a `date > 1936.1.1` will not ensure the event will be fired at exactly the second of January, but it may be anywhere between the 2nd and 21st (though it will be the same day on each reset).

In order to fire an event at a certain date, it's best to fire it on startup with the needed delay, setting the event to never fire by itself with `is_triggered_only = yes` and optionally adding additional prerequisites for it to appear within `trigger = { ... }`, which would be checked at the moment the event is intended to appear. For the calculation of the amount of days to be correct, leap days must be ignored as the game doesn't contain them.
Any effect block executed before or during startup can be used. An example using the [on_startup on action](<On actions - Hearts of Iron 4 Wiki.md>) exists [further down the article](#Integration_with_on_actions).

**Example event with this issue and a correction to it**

**Broken event**:

```text
country_event = {
    id = my_event.1
    title = my_event.1.t
    desc = my_event.1.desc

    trigger = {
        tag = POL
        NOT = { has_completed_focus = POL_my_focus }
        date > 1936.2.11 # If the event trigger check happens on the 1st of February and the 21st of February,
        date < 1936.2.13 # at least one of the date checks will always be false and the event will never trigger
    }

    option = {
        name = my_event.1.a
    }
}
```

**Correction**:

Event:

```text
country_event = {
    id = my_event.1
    title = my_event.1.t
    desc = my_event.1.desc

    is_triggered_only = yes # To prevent the 20-day range from causing a delay
    trigger = {
        NOT = { has_completed_focus = POL_my_focus }
    }

    option = {
        name = my_event.1.a
    }
}
```

In any `/Hearts of Iron IV/common/on_actions/*.txt` file:

```text
on_actions = {
    on_startup = {
        effect = {
            POL = {
                country_event = { id = my_event.1 days = 42 } # 12th of February 1936, if on the first start date
            }
        }
    }
}
```

- **Setting a news event to fire only once or not setting one as major** (*News event only fires for one country*) – An event requires `major = yes` in order to appear for every country. News events are purely a reskin of country events and are not set to fire for every country by default, so this line is mandatory. Alongside that, events that fire only once don't appear more than once *globally* rather than per country. The event appearing for more than one country counts as it firing once again, so setting an event to fire only once will lead to only one country getting the news event instead of every one as intended.

**Example events with this issue**

```text
news_event = {
    id = my_event.1
    title = my_event.1.t
    desc = my_event.1.desc

    is_triggered_only = yes     # Missing 'major = yes', only will fire for one country.

    option = {
        name = my_event.1.a
    }
}
news_event = {
    id = my_event.2
    title = my_event.2.t
    desc = my_event.2.desc

    is_triggered_only = yes
    major = yes
    fire_only_once = yes        # Fires only once, only will file for one country. Remove this line to fix.

    option = {
        name = my_event.2.a
    }
}
```

### Unintuitive logged errors <a id="Unintuitive_logged_errors"></a>

- **Event is triggered only, but does not have a 1 base-factor.** – This occurs when there are contradictory arguments within an event about whether it's allowed to be fired automatically or if it can only be fired manually. In particular, `mean_time_to_happen = { ... }` only has an effect when the event can only be fired automatically. However, if the event is triggered only, it cannot be fired automatically, resulting in the error being created.

**Example event with this issue**

```text
country_event = {
    id = my_event.1
    hidden = yes

    is_triggered_only = yes
    mean_time_to_happen = {
        days = 1
    }
}
```

- **Event is set to trigger every day.** – This occurs when all of the following is true for the event:
  - The event is possible to be fired automatically. In other words, `is_triggered_only = yes` is **not** present in the event.
  - The event has a mean time to happen of 1 or less days. If it is omitted, it counts as 1 day.
  - The event can fire more than once. In other words, `fire_only_once = yes` is **not** present in the event.

This error warns the player that the event may fire every day once the `trigger = { ... }` evaluates as true in a check that happens every 20 days. In order to remove the error, either of the three necessary clauses can be made to be not true for the event. For example, in a lot of cases, it is possible to make the event not be fired automatically and use an effect block to fire it instead, [such as by using on actions](<On actions - Hearts of Iron 4 Wiki.md>).

**Example event with this issue**

```text
country_event = {
    id = my_event.1
    hidden = yes

    is_triggered_only = no  # Changing to yes will fix the error
    fire_only_once = no     # Changing to yes will fix the error
    trigger = {
        tag = BHR
        controls_state = 123
    }
    mean_time_to_happen = {
        days = 1            # Changing to 2 or more will fix the error
    }
}
```

- **Malformed token: event_id.123, near line** on a line specifying the event ID – This occurs if [the event namespace was not added as needed](#ID_rules).

**Example event file**

```text
add_namespace = my_event # Not having this line will cause the issue.
country_event = {
    id = my_event.1
    hidden = yes

    is_triggered_only = yes
}
```

- **Failed to create id 12300000 50. Already exists in game. This might crash the game. Reverse id lookup: id 12300000 = my_namespace.0** – Note that this is the exact same error split into two instead of being two separate errors as it might seem on the first glance. This means that the internal event ID is used by 2 or more events. There are the following reasons for this error to appear:
  - Putting 2 events with the exact same ID by error – `id = my_namespace.0` is included in two events at once. This is self-explanatory.
  - Using non-integers as the numeric ID after the namespace – One event has `id = my_namespace.abc`, the other has `id = my_namespace.cba`. [Due to how the game generates internal IDs](#ID_rules), a non-numeric ID is not supported, always becoming the number 0. As such, these are the exact same ID, even if they appear different.
  - Using a numeric ID not smaller than 100000 – Two events across different namespaces got assigned the same internal IDs. By the virtue of how the game generates internal IDs, each namespace is assigned 100000 numeric IDs, from 0 to 99999. Anything larger than that will start encroaching to other namespaces' IDs. The game fully allows numbers this large as the numeric IDs, so the event might work, but the duplicate internal ID means that there is a pair of events that are treated as the same event, meaning one of them will fire the other one instead.

Since the reverse id lookup is not always provided, the way to tell if this is event-related is the second number: `50` signifies that it's event-related, while a different number means a different database entry, e.g. `54` means country leader IDs and `55` means unit leader IDs, the numeric legacy IDs which are unneeded due to the [1.11-introduced character system](<Character modding - Hearts of Iron 4 Wiki.md>)

**Example event file with this issue**

```text
add_namespace = prev_event
add_namespace = my_event        # Let this namespace have an ID of 321 in calculations, meaning the previous one has an ID of 320.
country_event = {
    id = my_event.1
    hidden = yes
}
country_event = {
    id = my_event.1             #  Creates "Failed to create id 32100001 50. Reverse id lookup: id 32100001 = my_event.1"
    hidden = yes
}
country_event = {
    id = my_event.abc
    hidden = yes
}
country_event = {
    id = my_event.letters       #  Creates "Failed to create id 32100000 50. Reverse id lookup: id 32100000 = my_event.abc"
    hidden = yes
}
country_event = {
    id = prev_event.100001      #  Creates "Failed to create id 32100001 50. Reverse id lookup: id 32100001 = my_event.1"
    hidden = yes
}
```

<!-- kit:begin id="event-engine-messages" at="section:Unintuitive_logged_errors" -->
**Kit addition** Event log messages found as strings in `hoi4.exe`. All rows: [unverified] (strings read from `hoi4.exe`; the exact trigger conditions were not tested).

| Message | Likely cause |
| --- | --- |
| "Event is missing a title." | a visible event without `title` |
| "Event is missing a desc." | a visible event without `desc` |
| "Event has no options." | a visible event without `option` |
| "Event is triggered only, but does not have a 1 base-factor." | `is_triggered_only = yes` together with a `mean_time_to_happen` timer |
| "Event is set to trigger every day." | automatic event with a timer of one day or less that can repeat |
| "Event is a leader event and has to be triggered only." | `unit_leader_event` or `operative_leader_event` without `is_triggered_only = yes` |
| "Malformed token" and "Failed to create id" | namespace problems and duplicate internal ids, as described above |

The first three do not occur in vanilla: every non-hidden vanilla event has a title, a desc and an option. [vanilla-confirmed 1.19.3] `events/`.
<!-- kit:end id="event-engine-messages" -->

## Event file example <a id="Event_file_example"></a>

```text
add_namespace = my_event
add_namespace = my_hidden_event

country_event = {
    id = my_event.1
    title = my_event.1.t
    desc = my_event.1.desc

    is_triggered_only = yes

    option = {
        name = my_event.1.a
        add_political_power = 100
    }
}

add_namespace = my_news_event
news_event = {
    id = my_news_event.1
    title = {
        text = my_news_event.1.t.a
        trigger = {
            tag = POL
        }
    }
    title = {
        text = my_event.1.t
    }
    desc = {
        text = my_news_event.1.desc.a
        trigger = {
            tag = POL
        }
    }
    desc = {
        text = my_event.1.desc
    }

    picture = GFX_my_news_event_picture

    is_triggered_only = yes
    major = yes

    option = {
        name = my_news_event.1.a
        trigger = {
            tag = POL
        }
    }

    option = {
        name = my_news_event.1.b
        trigger = {
            NOT = { tag = POL }
        }
    }

    option = {
        name = my_news_event.1.c
        original_recipient_only = yes
    }
}

country_event = {
    id = my_hidden_event.1

    trigger = {
        has_country_flag = event_happened
        country_exists = BHR
    }

    mean_time_to_happen = {
        days = 10
        months = 2
        years = 1
        modifier = {
            base = 300
            country_exists = QAT
        }
        modifier = {
            add = 10
            country_exists = OMA
        }
    }

    fire_only_once = yes
    hidden = yes

    immediate = {
        random_country = {
            limit = {
                is_neighbor_of = BHR
            }
            annex_country = {
                target = BHR
                transfer_troops = yes
            }
        }
    }
}

state_event = {
    id = my_event.2
    title = my_event.2.t
    desc = my_event.2.desc
    picture = GFX_my_event_picture

    trigger = {
        ROOT = {
            has_country_flag = fire_this_event
        }
    }
    is_triggered_only = yes

    option = {
        name = my_event.2.a
        transfer_state_to = ROOT
    }

    option = {
        name = my_event.2.b
        ai_chance = {
            base = 0        # Never pick this option.
        }
        transfer_state_to = FROM
    }
}
```

### Integration with on actions <a id="Integration_with_on_actions"></a>

*See also: [On actions](<On actions - Hearts of Iron 4 Wiki.md>)*

These events are the primary types to trigger via on_actions:

```text
add_namespace = on_action_events
news_event = {      # City capture news event
    id = on_action_events.1
    title = on_action_events.1.t    # Fall of Giza
    desc = on_action_events.1.desc

    is_triggered_only = yes
    major = yes

    option = {
        trigger = {
            OR = {
                tag = EGY
                is_in_faction_with = EGY
                is_subject_of = EGY
            }
        }
        name = on_action_events.1.a
    }

    option = {
        trigger = {
            NOT = {
                tag = EGY
                is_in_faction_with = EGY
                is_subject_of = EGY
            }
        }
        name = on_action_events.1.b
    }
}

country_event = {       # Fired on a specific day if circumstances are met
    id = on_action_events.2
    title = on_action_events.2.t
    desc = on_action_events.2.desc

    is_triggered_only = yes                     # Prevents from firing automatically.
    trigger = {
        has_completed_focus = BHR_focus_name    # If the focus isn't completed, will never fire.
    }

    option = {
        name = on_action_events.2
    }
}

country_event = {       # Other types of on_actions
    id = on_action_events.3 # In this case, a prompt on annexing a country with an option to release it.
    title = on_action_events.3.t
    desc = on_action_events.3.desc

    is_triggered_only = yes                     # Prevents from firing automatically.

    trigger = {     # If all core states of FROM are cored or claimed by ROOT, should never appear.
        NOT = {     # Triggered within on_annex's random_events = { ... }, so has the same FROM as the on_action
            any_state = {
                NOT = {
                    is_core_of = ROOT
                    is_claimed_by = ROOT
                }
                is_core_of = FROM
            }
        }
        FROM = {
            NOT = {
                tag = GER       # Has separate event
            }
        }
    }

    option = {
        name = on_action_events.3.a   # "Release [FROM.GetName] as puppet"
        every_owned_state = {
            limit = {
                is_core_of = FROM
                NOT = {
                    is_core_of = ROOT
                    is_claimed_by = ROOT
                }
            }
            transfer_state_to = FROM
        }
        if = {
            limit = {
                has_dlc = "Together for Victory"
            }
            set_autonomy = {
                target = FROM
                autonomy_state = autonomy_integrated_puppet
            }
        }
        else = {
            puppet = FROM
        }
    }

    option = {
        name = on_action_events.3.b # "Don't release [FROM.GetName]"
        add_stability = -0.1
        add_war_support = -0.1
    }
}
```

In order to fire this, code has to be created within any `/Hearts of Iron IV/common/on_actions/*.txt` file, sometimes paired with [boolean flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) to prevent them from being fired more than once if fire_only_once is impossible. In the above example, this would be used:

```text
on_actions = {
    on_state_control_changed = {
        effect = {
            if = {
                limit = {
                    FROM.FROM = {
                        state = 999 # Custom state ID. Will crash the game if doesn't exist.
                    }
                    NOT = {
                        has_global_flag = giza_fall # To prevent from firing twice.
                    }                               # Due to 'major = yes', a fire_only_once will NOT work
                }
                news_event = { id = on_action_events.1 hours = 6 random_hours = 3 } # Fires in 6-9 hours to feel more natural.
            }
        }
    }
    on_startup = {
        effect = {
            BHR = {
                country_event = {
                    id = on_action_events.2
                    days = 357
                    random_days = 7     # Fires in the last week of 1936, assuming default start date.
                }
            }
        }
    }
    on_annex = {
        random_events = {
            1 = on_action_events.3
        }
    }
}
```

### Integration with history <a id="Integration_with_history"></a>

*See also: [Country creation#History](<Country creation - Hearts of Iron 4 Wiki.md#History>)*

Alternatively, you can fire the event inside `/Hearts of Iron IV/history/countries/*.txt` file:

```text
# history/countries/BHR - Bahrain.txt
# Other code is omitted
country_event = {
	id = on_action_events.2
	days = 357
	random_days = 7     # Fires in the last week of 1936, assuming default start date.
}
```

<!-- kit:begin id="event-history-vanilla" at="section:Integration_with_history" -->
**Kit addition** Vanilla fires events from country history files in 8 files (`BRA`, `CHL`, `CZE`, `FIN`, `RAJ`, `SOV`, `SWI` and `USA` in `history/countries/`), 14 calls in total, and every call carries a delay (`days` or `months`, in some with `random_days` or `random_hours`). No vanilla history file fires an event without a delay. [vanilla-confirmed 1.19.3] `history/countries/`.
<!-- kit:end id="event-history-vanilla" -->

## Notes and references <a id="Notes_and_references"></a>

**^** **a:** `delayed_event` is used for tracking events that are to be fired with a time delay in the save games (as they're formatted with `save_as_binary=no` in `/Hearts of Iron IV/settings.txt`). This is used for every single event type, such as country events or state events.

1. ↑ `NDefines.NCountry.EVENT_PROCESS_OFFSET = 20` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>).
2. ↑ `NDefines.NGame.EVENT_TIMEOUT_DEFAULT = 13` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>).

Note that when editing defines, it is far preferable to use an [override file](<Defines - Hearts of Iron 4 Wiki.md#Overrides>) than copying over the entire file, as defines are edited commonly even in 'minor' updates, which can cause crashes when the game updates.

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
