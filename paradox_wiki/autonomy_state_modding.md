# Autonomy state modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Autonomy state modding", revision 100160, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" revision="100160" sources="common/autonomous_states/ common/defines/00_defines.lua common/special_projects/projects/naval_projects.txt interface/countrypoliticsview.gfx localisation/english/autonomy_l_english.yml documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md documentation/dynamic_variables_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 21 vanilla autonomy state files, the autonomy defines, the autonomy effects, triggers, modifiers and the rule list.
- Kit blocks added: `autonomy-vanilla-values` (what vanilla sets, min_freedom_level table), `autonomy-rule-list-fixes` (rule names the wiki table gets wrong or lacks), `autonomy-effects-keys` (set_autonomy key spellings, full ids, related effects, triggers, modifiers), `autonomy-defines-extra`.
- Errors found: the rule name `can_join_factions_not_allowed_diplomacy` is not found in the game; `can_use_underway_replenishment` is missing from the rule table; docs examples write `has_autonomy_state = puppet` while vanilla always writes the full id.
- Gaps left: the effect of `peace_conference_initial_freedom` when absent (wiki says 0.5) is not confirmed; `autonomy_free` and `autonomy_annex` have no definition file to check.
**1.19.4.1 re-check (2026-11-01).** Five tagged statements depended on files the update changed (`dominion.txt` and the vanilla-wide scans of rule names, `set_autonomy`, `has_autonomy_state` and `freedom_level`), and all were re-measured. One number moved (`autonomous_state` is used in 81 `set_autonomy` blocks in 24 files, was 80 in 23), and two older statements were corrected (`is_puppet = yes` is also absent from `supervised_state.txt`, and `can_force_government` and `can_lower_tension` are keys of the ideology `rules` blocks). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Arguments](#Arguments)
- [Icon](#Icon)
- [Localisation](#Localisation)
- [Example](#Example)
- [Related defines](#Related_defines)
- [Additional notes](#Additional_notes)
- [References](#References)

---

Different levels of the autonomy system are defined in `/Hearts of Iron IV/common/autonomous_states/*.txt`, and new ones can be created.

## Arguments <a id="Arguments"></a>

- **id** is the ID of the autonomy state, unique to each one. It is necessary to define to distinguish it from other autonomy states.
- **default**: If true, the game will attempt to make the 'puppet' option in peace deals as well as the 'puppet' effect use this autonomy state among other default autonomy states. By default, set to no.
- **is_puppet** decides whether the subject is a puppet or not, making is_puppet and is_puppet_of triggers true in that case. By default, set to no.
- **use_overlord_color** makes the subject have the same country color as the overlord.
- **min_freedom_level** decides the order in which autonomy states are placed. The autonomy states with lower freedom levels have less autonomy than those with higher when the game places the autonomy states for the subject to lose or gain a level. This also decides how many autonomy points the subject needs to gain or lose a level, calculated by the difference between freedom levels multiplied by 5000[1]. As such, it would take 500 points to go from an autonomous state with the min_freedom_level of 0.1 to being annexed.
- **manpower_influence** decides how large of a portion of the subject's manpower the overlord can use in colonial divisions.
- **rule** sets the game rules for the subject to either yes or no.

**Game rule list**

The following game rules exist as possible options:

| Internal name | Localised name | Notes |
| --- | --- | --- |
| can_access_market | Can access International Market (Puppets and Overlords can always access each other's market) |  |
| can_be_spymaster | Can be Spy Master |  |
| can_boost_other_ideologies | Can boost popularity of other ideologies |  |
| can_boost_own_ideology | Can boost own party popularity in other countries |  |
| can_create_collaboration_government | Can create collaboration governments |  |
| can_create_factions | Can Create Factions |  |
| can_declare_war_on_same_ideology | Can declare war on country with the same ideology group without a war goal |  |
| can_declare_war_without_wargoal_when_in_war | Can declare war on a neighbor without a wargoal when at war with a major |  |
| can_decline_call_to_war | Can decline call to war |  |
| can_force_government | Can force government of another country to adopt the same ideology |  |
| can_generate_female_aces | Women in your country are allowed to become military pilots |  |
| can_generate_female_country_leaders | Can generate female country leaders |  |
| can_generate_female_unit_leaders | Can generate female unit leaders |  |
| can_guarantee_other_ideologies | Can guarantee other ideologies |  |
| can_join_factions | Can join factions |  |
| can_join_factions_not_allowed_diplomacy | Country's name is not allowed to join factions |  |
| can_join_opposite_factions | Can Join Factions led by another Ideology |  |
| can_lower_tension | Lowers World Tension with Guarantees |  |
| can_not_build_buildings | CAN_NOT_BUILD_BUILDINGS | Doesn't seem to work. |
| can_not_declare_war | Can not declare wars | Prevents generating wargoals, but not using existing ones. |
| can_occupy_non_war | Can hold territory owned by a country they are not at war with |  |
| can_only_justify_war_on_threat_country | Can justify war goals against a country that have not generated world tension |  |
| can_puppet | Can puppet a country |  |
| can_send_volunteers | Can send volunteer forces |  |
| can_use_kamikaze_pilots | Can use kamikaze pilots |  |
| contributes_operatives | Contributes Operatives to Spy Master: Yes | Only has an effect for subjects. |
| units_deployed_to_overlord | Control over deployed units go to overlord | Only has an effect for subjects. |

- **modifier** sets the modifier for the subject. All country [modifiers](<modifiers.md>) can apply.
- **ai_subject_wants_higher** decides whether or not the AI subject focuses on gaining a higher autonomy. If set to 0, AI will never gain an autonomy level through the autonomy system.
- **ai_overlord_wants_lower** decides whether or not the AI overlord focuses on gaining a lower autonomy for the subject. If set to 0, AI will never decrease the autonomy level through the autonomy system.
- **ai_overlord_wants_garrison** decides the triggers when the AI overlord garrisons the subject's territory as if it was their own land.
- **allowed** are the necessary triggers the subject must meet for the autonomy state to apply. The OVERLORD scope can be used to scope into the overlord.
- **use_for_peace_conference_weight** decides the chance for a potential overlord to puppet the country in the peace deal, where ROOT is the subject and FROM is the overlord.
- **can_take_level** sets the necessary triggers the subject must meet to be able to gain a level through the autonomy system.
- **can_lose_level** sets the necessary triggers the subject must meet for the overlord to be able to decrease the autonomy level through the autonomy system.
- **peace_conference_initial_freedom** is the initial freedom level of the country that gets set to this autonomy after a peace conference on a scale from 0 to 1. If not specified, assumed to be 0.5.
- **allowed_levels_filter** decides which autonomy levels a country with this autonomous state can change to, alongside autonomy_free. If not specified, all levels will be allowed.

<!-- kit:begin id="autonomy-vanilla-values" at="section:Arguments" -->
**Kit note** What the 21 vanilla files in `common/autonomous_states/` actually set, to calibrate new states. All lines: [vanilla-confirmed 1.19.4.1] `common/autonomous_states/*.txt`.

- `min_freedom_level` is a decimal from 0 to 1. Vanilla values: 0.0 (personal union, collaboration government, defense council member, Indonesian union state, EU member), 0.2 (integrated puppet, reichskommissariat, imperial protectorate, Austro-Hungarian subject, volkskommissariat), 0.4 puppet, 0.5 reichsprotectorate and integrated warlord subject, 0.6 colony and warlord subject, 0.7 imperial associate, 0.75 supervised state, 0.8 dominion, satellite, associated dominion and imperial subject.
- Several vanilla states share a value (four at 0.8, five at 0.0, five at 0.2). They are kept apart by `allowed` and `allowed_levels_filter`, so the wiki's advice to avoid equal values is a safe default, not an engine error.
- `is_puppet = yes` is absent from dominion, satellite, associated dominion and supervised state, so those subjects are not puppets for `is_puppet` and `is_puppet_of`. `wtt_imperial_subject.txt` writes `is_puppet = no` explicitly.
- `default = yes` appears in 7 files: puppet, reichsprotectorate, warlord subject, imperial protectorate, imperial subject, Austro-Hungarian subject and EU puppet.
- The `rule` block of every file starts with `desc = "RULE_DESC_IS_A_SUBJECT"`, a loc key for the tooltip text. `rule` keys vanilla uses: `can_not_declare_war`, `can_decline_call_to_war`, `can_be_spymaster` (all 21), `can_create_collaboration_government` (18), `contributes_operatives` (15), `units_deployed_to_overlord` (9).
- `use_for_peace_conference_weight` is set only in `puppet.txt` and `supervised_state.txt`. The vanilla comment reads "ROOT is puppet - FROM is potential OVERLORD". `peace_conference_initial_freedom` is set only in `supervised_state.txt` (0.001). The wiki's "0.5 when unset" is [unverified].
- `allowed_levels_filter` is set only in `nsb_personal_union.txt` and `supervised_state.txt`, and each lists only its own id, which locks the subject at that level. `can_lose_level = { always = no }` is used the same way. A stub `can_take_level = { }` that holds only a comment is legal and adds no condition.
- `ai_overlord_wants_garrison` is a trigger-style block, not a weight: 19 files set it, 10 to `always = yes`, 9 to `always = no`.
- `autonomy_free` (independent) and `autonomy_annex` (annexed) have no definition file but have loc keys in `localisation/english/autonomy_l_english.yml` and icons `GFX_autonomy_free_icon` and `GFX_autonomy_annex_icon` in `interface/countrypoliticsview.gfx`. `autonomy_free` is a valid `set_autonomy` value in vanilla focuses (`common/national_focus/australia.txt`).
<!-- kit:end id="autonomy-vanilla-values" -->

<!-- kit:begin id="autonomy-rule-list-fixes" at="section:Arguments" -->
**Kit correction** Corrections to the game rule table above (the same table is on the [Faction modding](<faction_modding.md>) page).

- Rule names used in vanilla script (in autonomy `rule` blocks, `set_rule`, `has_rule` or other `rule` blocks): `can_access_market`, `can_be_spymaster`, `can_boost_other_ideologies`, `can_boost_own_ideology`, `can_create_collaboration_government`, `can_create_factions`, `can_declare_war_on_same_ideology`, `can_declare_war_without_wargoal_when_in_war`, `can_decline_call_to_war`, `can_generate_female_aces`, `can_generate_female_country_leaders`, `can_generate_female_unit_leaders`, `can_guarantee_other_ideologies`, `can_join_factions`, `can_join_opposite_factions`, `can_not_declare_war`, `can_only_justify_war_on_threat_country`, `can_puppet`, `can_send_volunteers`, `can_use_kamikaze_pilots`, `contributes_operatives`, `units_deployed_to_overlord`. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`, searched by script.
- Missing from the table: `can_use_underway_replenishment`, set by `set_rule = { can_use_underway_replenishment = yes }` in a naval special project. [vanilla-confirmed 1.19.3] `common/special_projects/projects/naval_projects.txt`.
- Not used in any autonomy `rule` block, `set_rule` or `has_rule`, but present as strings in `hoi4.exe`: `can_force_government`, `can_lower_tension`, `can_not_build_buildings`, `can_occupy_non_war`. The first two are keys of the `rules` blocks in `common/ideologies/00_ideologies.txt`, the last two occur in no vanilla script. [vanilla-confirmed 1.19.4.1] Treat their effect as unverified. [unverified]
- `can_join_factions_not_allowed_diplomacy` occurs neither in vanilla script nor in `hoi4.exe`; the rule that exists is `can_join_factions`. Do not use the long name. [unverified]
- `has_rule = <rule>` checks a rule on the scoped country, `set_rule = { desc = <loc key> <rule> = yes }` overrides it, and `add_relation_rule_override` overrides `can_send_volunteer` or `can_access_market` toward one target or a named trigger. [docs] `documentation/triggers_documentation.md` (`has_rule`), `documentation/effects_documentation.md` (`set_rule`, `add_relation_rule_override`).
<!-- kit:end id="autonomy-rule-list-fixes" -->

## Icon <a id="Icon"></a>

**General sprite overview**

For loading GFX, the game uses the sprite system. Sprites are code definitions that attach a name to an image file, as well as optionally adding additional information, such as animation, the amount of frames, the way that the image will be loaded, and so on. This means **placing an image into the gfx folder isn't enough for it to work**, a sprite has to use that image file as well.

Sprites are defined in any `/Hearts of Iron IV/interface/*.gfx` file (this is separate from `gfx/interface/`), opened with a text editor. To create a new .gfx file, a text file can be created and renamed to change the extension (on Windows, the Windows Explorer needs to show the extensions, which it doesn't by default). In particular, sprites are defined within a `spriteTypes = { ... }` block, as to separate from fonts and map arrows also defined in that folder, while the simplest sprite with the least mandatory properties is a `spriteType = { ... }`. The simplest sprite definition looks like the following:

```text
spriteTypes = {
    spriteType = {
        name = GFX_first_sprite                         # In some cases, beginning with GFX_ is mandatory for it to work.
        texturefile = gfx/interface/folder/filename.dds # The folder and filename don't matter, as long as they are correct
    }                                                   # Only the forward slash '/' (can be doubled as '//') can be used to separate folders.
    spriteType = {                                      # The image doesn't have to be .dds, as .tga and .png are acceptable.
        name = GFX_second_sprite
        texturefile = gfx/interface/folder2/filename2.dds
        noOfFrames = 2 # Splits the image into 2 halves, which may be switched between dynamically in GUI
    }
}
```

In this case, this creates a sprite with the name of `GFX_first_sprite` and attaches the `/Hearts of Iron IV/gfx/interface/folder/filename.dds` image to it, and a second sprite similarly. The second sprite will be split into 2 frames: this is decided by having the left half of the image as the first frame and the right half as the second frame (more frames would further split the image horizontally). This doesn't make the sprite animated, just turns on the option to switch between the two halves as needed. `GFX_second_sprite:1` serves as a reference to the first frame, and GUI can be set up to change the shown frame depending on context, such as with radio stations.
In order to add animation, a [frameAnimatedSpriteType](<graphical_asset_modding.md#frameAnimatedSpriteType>) is used.

**It's never mandatory to copy a base game file to change a sprite**. If there are duplicate definitions of a sprite with the same name in different files, the game will prioritise the one that would be [evaluated later, based on the filename](<modding.md#Loading_files>), and the older sprite will be ignored in entirety. This can be ensured by beginning the replacement file's name with a symbol late in the ASCII character table. Typically the lowercase letter 'z' is used for this purpose. For example, to change the amount of frames in `GFX_idea_traits_strip` to 10, it is possible to define a sprite with that name with 10 frames in the mod's `modname/interface/zz_replace.gfx` file instead of copying over the base game file.
Since most .gfx files define integral parts of the user interface, copying them over can lead to the mod's loaded files missing sprites upon a major game update, which would appear in-game as the default image, which is the error dog by default. As to ease the burden of needing to check the interface files, it's best to never copy over .gfx files, unless more additions would be actively harmful to the mod, such as with `interface/subuniticons.gfx`

For the icon, the game will use a sprite named in the format of `GFX_<autonomy state>_icon`. An `/Hearts of Iron IV/interface/*.gfx` file containing such a definition may look like the following:

```text
spriteTypes = {
    spriteType = {
        name = "GFX_autonomy_mod_new_icon"
        textureFile = "gfx/interface/autonomy/autonomy_mod_new_icon.dds"
    }
    spriteType = {
        name = "GFX_example_icon"
        texturefile = "another_folder/image_name.dds"
    }
}
```

## Localisation <a id="Localisation"></a>

The localisation is set in an .yml file in the localisation/ folder. Using the prior example of autonomy_mod_new, a localisation entry will look like `autonomy_mod_new:0 "Mod's new autonomy state"`

It is possible to set a country-specific entry. An entry with `GER_autonomy_mod_new:0 "New mod Germany"` will make Germany have that name if its autonomy level is autonomy_mod_new. Similarly, `ENG_FRA_autonomy_mod_new:0 "New mod French UK"` will make the United Kingdom have that name if its overlord is France and the autonomy state is autonomy_mod_new.

## Example <a id="Example"></a>

```text
autonomy_state = {
	id = autonomy_example

	default = yes					#Will be a possible option for peace deals
	is_puppet = yes

	use_overlord_color = yes

	min_freedom_level = 0.2				#Puts it as 0.2 on the autonomy level scale, which is the same as an integrated puppet.

	peace_conference_initial_freedom = 0.9		#Close to independence

	manpower_influence = 0.9

	rule = {
		can_not_declare_war = yes
		can_decline_call_to_war = no
		units_deployed_to_overlord = yes
		can_be_spymaster = no
		contributes_operatives = no
		can_create_collaboration_government = no
	}

	modifier = {
		autonomy_manpower_share = 1.0
		can_master_build_for_us = 1
		extra_trade_to_overlord_factor = 1.0
		overlord_trade_cost_factor = -0.9
		cic_to_overlord_factor = 0.75
		mic_to_overlord_factor = 0.75
		research_sharing_per_country_bonus_factor = -0.5
	}

	ai_subject_wants_higher = {
		factor = 0.0
	}

	ai_overlord_wants_lower = {
		factor = 0.0
	}

	allowed = {
		has_dlc = "Together for Victory"
		OVERLORD = {
			tag = FRA
		}
	}

	allowed_levels_filter = {
		autonomy_example
		autonomy_example_1
		autonomy_example_2
	}

	use_for_peace_conference_weight = {
		base = 0
		modifier = {
			add = 10
			FROM = {
				has_wargoal_against = { target = ROOT type = puppet_wargoal_focus }
			}			# Adds 10 to the chance if the overlord has a wargoal to puppet the country.
		}
		modifier = {
			factor = 2
			tag = ENG	# Multiplies the chance by 2 if the subject is UK.
		}
	}

	can_take_level = {
		OVERLORD = {
			NOT = {
				controls_state = 123
			}	# If the overlord does not control state 123, the subject can gain a level.
		}
	}

	can_lose_level = {
		OVERLORD = {
			controls_state = 123
		}	# If the overlord controls state 123, it can decrease the subject's autonomy level.
	}
}
```

## Related defines <a id="Related_defines"></a>

Certain [Defines](<defines.md>) affect the autonomy system in a certain way. These are:

- **RESOURCE_SENT_AUTONOMY_DAILY_BASE** (0) Base autonomy gain from the overlord purchasing the subject's resources through trade.
- **RESOURCE_SENT_AUTONOMY_DAILY_FACTOR** (0.005) Autonomy gain multiplier from the overlord purchasing the subject's resources through trade.
- **WAR_SCORE_AUTONOMY_BASE** (0) Base autonomy gain from the subject gaining war score in a war.
- **WAR_SCORE_AUTONOMY_FACTOR** (0.6) Autonomy gain multiplier from the subject gaining war score in a war.
- **LL_TO_OVERLORD_AUTONOMY_DAILY_BASE** (0) Base autonomy gain from the subject lend-leasing to the overlord.
- **LL_TO_OVERLORD_AUTONOMY_DAILY_FACTOR** (0.05) Autonomy gain multiplier from the subject lend-leasing to the overlord.
- **LL_TO_PUPPET_AUTONOMY_DAILY_BASE** (0) Base autonomy gain from the overlord lend-leasing to the subject. Must be negative in order to lose autonomy.
- **LL_TO_PUPPET_AUTONOMY_DAILY_FACTOR** (-0.01) Autonomy gain multiplier from the overlord lend-leasing to the subject. Must be negative in order to lose autonomy.
- **AUTONOMY_FREEDOM_FROM_CAPITULATE** (0.5) Upon the overlord capitulating, the subject receives a large gain to the autonomy progress.
- **ATTACHE_TO_SUBJECT_EFFECT** (-0.05) Base autonomy gain from the overlord sending an attache to the subject. Must be negative in order to lose autonomy.
- **ATTACHE_TO_OVERLORD_EFFECT** (0.05) Base autonomy gain from the subject sending an attache to the overlord.
- **AUTONOMY_LEVEL_CHANGE_PP_COST_BASE** (50) The cost in political power to change between autonomy states.
- **AUTONOMY_LEVEL_CHANGE_PP_ANNEX** (300) The cost in political power to annex a subject.
- **AUTONOMY_LEVEL_CHANGE_PP_FREE** (300) The cost in political power to gain independence as a subject.
- **MAX_SCORE_DIFF_TO_CHANGE_AUTONOMY** (10) The maximum difference between the current freedom score and the cap for the next or previous level allowed for changing.
- **MASTER_BUILD_AUTONOMY_FACTOR** (-0.7) Autonomy gain multiplier from the overlord building in the subject's states. Must be negative in order to lose autonomy.
- **AUTONOMOUS_TOTAL_SCORE** (5000) The total amount of autonomy points between the country's annexation and independence.
- **AUTONOMOUS_SPILLOVER** (0.025) The amount that can be saved between levels.

<!-- kit:begin id="autonomy-defines-extra" at="section:Related_defines" -->
**Kit note** `NDefines.NDiplomacy.AUTONOMY_LEVEL_CHANGE_SANCTUARY = 30` is not in the wiki list: the number of days after an autonomy level change during which neither side can change the level again. The values the wiki gives for the other defines match 1.19.3, for example `AUTONOMOUS_TOTAL_SCORE` 5000 and `AUTONOMOUS_SPILLOVER` 0.025 (both in `NDefines.NCountry`), `AUTONOMY_LEVEL_CHANGE_PP_COST_BASE` 50 and `MASTER_BUILD_AUTONOMY_FACTOR` -0.7 (both in `NDefines.NDiplomacy`). [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.
<!-- kit:end id="autonomy-defines-extra" -->

## Additional notes <a id="Additional_notes"></a>

For a country to start the game as a subject, this can be done using the [set_autonomy](<effects.md>) effect in the history files. When doing this, it is preferable to do it in the subject's history file scoping to the overlord's tag, as shown below.

```text
TAG = {
    set_autonomy = {
        target = TAG2
        autonomy_state = autonomy_mod_new
    }
}
```

Autonomy effects are known to overwrite the political setup of a country, both in terms of leaders, ruling party and popularities. Therefore it has to be placed in the lines before recruiting characters and defining politics. Setting the autonomy level in the overlord's history file is one of the main sources of issues of ideologies being incorrect, due to the overwriting political definitions for the same reason. This happens due to the loading order, **but it is not recommended to make changes to the countries' loading order for this purpose.**

If deciding to create a new autonomy system similar to Japan's unique autonomies, it is necessary to disable the default autonomy states so that they could not be used via `allowed = {}` in them or via `allowed_levels_filter = {}` in the new autonomies. Note that if you choose the second option, you would still need to disable the default autonomies so that they do not appear while puppeting.

If a new autonomy level should only be possible to be manually assigned via the `set_autonomy` [effect](<effects.md>), then it's possible to set up allowed as such, using the autonomy state with the id of `autonomy_my_state`:

```text
allowed = {
    OR = {
        is_subject = no
        has_autonomy_state = autonomy_my_state
    }
}
```

That makes the autonomy state impossible to achieve through gaining or losing levels, as the `allowed` block is false if the subject has any other autonomy. This will ensure that `set_autonomy` will be possible to execute, *as long as the target country is independent at the time*, and that it wouldn't get cleared after being assigned, while it has that autonomy state.

When creating autonomy systems, avoid 2 different states having the same min_freedom_level.

<!-- kit:begin id="autonomy-effects-keys" at="section:Additional_notes" -->
**Kit addition** Script that reads or changes autonomy, checked against the documentation and vanilla.

| Name | Kind | Syntax or note |
| --- | --- | --- |
| `set_autonomy` | effect, country scope | `set_autonomy = { target = TAG autonomy_state = autonomy_puppet freedom_level = 0.5 end_wars = yes end_civil_wars = yes }`. The scope is the overlord, `target` the subject; both `end_` switches default to yes |
| `release_autonomy` | effect | `target`, `autonomy_state`, `freedom_level`, plus `release_non_owned_controlled` (default no) and `force_change_controller_for_non_ally_controlled` (default no) |
| `add_autonomy_ratio`, `add_autonomy_score` | effects | `{ value = 0.05 localization = LOC_KEY }`; ratio adds a share of the freedom score, score adds an exact amount |
| `puppet` | effect | `puppet = TAG` or `puppet = { target = TAG end_wars = yes end_civil_wars = yes }` |
| `end_puppet`, `release_puppet`, `release_puppet_on_controlled` | effects | Free a puppet, or release it from owned, or owned and controlled, states |
| `has_autonomy_state` | trigger | `has_autonomy_state = autonomy_puppet` |
| `compare_autonomy_state` | trigger | `compare_autonomy_state > autonomy_colony`; checks whether the state is higher than another |
| `compare_autonomy_progress_ratio` | trigger | `compare_autonomy_progress_ratio > 0.5` |
| `is_subject`, `is_subject_of`, `is_puppet`, `is_puppet_of`, `has_subject`, `num_subjects` | triggers | Subject relations |
| `pc_is_puppeted`, `pc_is_puppeted_by` | triggers | Also true for a country released as a puppet in a peace conference; see [Peace conference modding](<peace_conference_modding.md>) |
| `autonomy_ratio` | dynamic variable | Country scope; -1 if the country is not a subject |
| `autonomy_gain`, `autonomy_gain_global_factor`, `autonomy_gain_trade`, `autonomy_gain_trade_factor`, `autonomy_gain_warscore`, `autonomy_gain_warscore_factor`, `autonomy_gain_ll_to_overlord`, `autonomy_gain_ll_to_overlord_factor`, `autonomy_gain_ll_to_subject`, `autonomy_gain_ll_to_subject_factor`, `autonomy_manpower_share`, `autonomy_manpower_share_from_subjects`, `master_build_autonomy_factor`, `subjects_autonomy_gain` | modifiers | Autonomy-related country modifiers |

All rows: [docs] `documentation/effects_documentation.md`, `triggers_documentation.md`, `modifiers_documentation.md`, `dynamic_variables_documentation.md`.

Trap: the documentation examples write the short name (`has_autonomy_state = puppet`, `compare_autonomy_state > puppet`), but every vanilla use writes the full state id (`autonomy_puppet`, `autonomy_colony`, `autonomy_reichsprotectorate`), which is the `id` of the state file. Use the full id. [vanilla-confirmed 1.19.4.1] `has_autonomy_state` and `compare_autonomy_state` in `common/`, `events/`, `history/`.

Trap: the key for the state inside `set_autonomy` is `autonomy_state` in the documentation and in 500 vanilla `set_autonomy` blocks (34 more in `release_autonomy`). A second spelling, `autonomous_state`, is used in 81 vanilla `set_autonomy` blocks in 24 files, among them `history/countries/ENG - Britain.txt` (11) and `common/decisions/SLO.txt`, and is a string in `hoi4.exe`. Write `autonomy_state`; that the other spelling takes effect is likely but untested [unverified]. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`, counted by script.

`freedom_level` is a decimal. Vanilla values run from 0 to 1; the most common are 0.5 (62 uses), 0.2 (28), 1 (10) and 0.8 (9). [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`.
<!-- kit:end id="autonomy-effects-keys" -->

## References <a id="References"></a>

1. ↑ `NDefines.NCountry.AUTONOMOUS_TOTAL_SCORE = 5000` in [Defines](<defines.md>).

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>) • [Units](<unit_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
