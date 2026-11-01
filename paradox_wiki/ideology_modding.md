# Ideology modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Ideology modding", revision 90513, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" revision="90513" sources="common/ideologies/ common/peace_conference/ common/country_leader/ common/ideas/zzz_generic.txt history/general/generic_advisors.txt history/countries/ interface/countrypoliticsview.gfx localisation/english/parties_l_english.yml localisation/english/modifiers_l_english.yml documentation/modifiers_documentation.md documentation/effects_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `common/ideologies/00_ideologies.txt` (the only vanilla ideology file), the peace conference folders, `set_politics` / `set_popularities` / `add_popularity` in every vanilla file under `common/`, `events/` and `history/`, the ideology sprites and localisation, the generic advisor setup, the modifier documentation and `hoi4.exe` strings.
Kit blocks added: vanilla group and type table, corrections to the example block (`take_states_cost_factor`, `ai_<ideology>`, placeholder names), `can_be_boosted`, the duplicate group id risk, the moved AI peace folder, localisation and sprite checks, `set_politics` and popularity counts, the political advisor setup in 1.19.3 and the `<group>_drift` modifier family.
Gaps left: whether a duplicate group id is rejected at load, and what `can_be_boosted` does, are not shown by script. The wiki's `_booster` suffix is a naming idea, not a vanilla convention.
**1.19.4.1 re-check (2026-11-01).** Nine tagged statements depended on files the update changed (the peace conference folders, `hoi4.exe` strings, modifier localisation, the generic advisor files, country leader traits and the vanilla-wide political setup counts), and all were re-measured. Numbers that moved: `set_politics` 1,051 uses (`ruling_party` 1,050 values, `democratic` 304, `fascism` 194), `last_election` 500, `election_frequency` 509, `add_popularity` 1,831 uses and `create_country_leader` 176 uses (was 181), and two older statements were tightened (the word `anarchist` occurs in comments and localisation prose, and `can_boost_own_ideology` is set in an event, not an idea). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Ideologies](#Ideologies)
- [Ai peace](#Ai_peace)
- [Getting the ideology in your game](#Getting_the_ideology_in_your_game)
  - [Localisation](#Localisation)
  - [GFX](#GFX)
  - [Country history](#Country_history)
  - [Political advisor](#Political_advisor)

---

Ideologies represent all of the different political beliefs or alignments in the selected nation. An ideology will help to determine the choices and paths that the nation will take.

Ideologies are found in `/Hearts of Iron IV/common/ideologies/*.txt`.

## Ideologies <a id="Ideologies"></a>

An ideology definition follows this format:

```text
ideologies = {

	anarchist = {

		types = {
			anarcho_syndicalism = { # Used when assigning ideologies to leaders. Eg. democratic has conservatism, liberalism, and socialism. One value can be defined (yes/no).
				can_be_randomly_selected = no # If no, the subideology will not be randomly selected when creating a new random leader.
				color = { 169 42 42 } # Optional - if not specified, the subideology has the color of its ideology.
			}
		}

		dynamic_faction_names = {
			"FACTION_NAME_ANARCHIST_1" # Faction names used by the ai when an ai with this ideology creates a faction. Can be defined in any localisation file.
		}

		color = { 169 42 42 } # RGB ideology colour, used in the political pie chart or next to the chart. Can be overwritten in a subideology.

		rules = { # Rules for the ideology.  (yes/no)
                        can_create_collaboration_government = # Can create a collaboration government
			can_declare_war_on_same_ideology = # Declare war on same ideology. Not required
			can_force_government = # Can change ideology in peace deal. Required
			can_send_volunteers = # Can send volunteers. Required
			can_puppet = # Can puppet a nation at peace deal. Required
			can_lower_tension = # Lowers tension at peace deal. Not required
			can_only_justify_war_on_threat_country = # Can only justify on a nation that has generated world tension/threat. Not required
			can_guarantee_other_ideologies = # Can guarantee nations with different ideologies. Not required
		}

                can_host_government_in_exile = no #Can host a government in exile

		war_impact_on_world_tension = 0.2 # Goes from -1 to 1. Increases or decreases the world tension created by this nation
		faction_impact_on_world_tension = 0.3 # Goes from -1 to 1. Increases or decreases a faction of this ideologies impact on tension

		modifiers = { # More rules for the ideology. Every country [[Modifiers|modifier]] can apply.
			generate_wargoal_tension = # Required world tension to start justifying a war (0 to 1)
			join_faction_tension = # Required world tension to join a faction (0 to 1)
			lend_lease_tension = # Required tension to start a lend-lease (0 to 1)
			send_volunteers_tension = # Required tension to send volunteers (0 to 1)
			guarantee_tension = # Required tension to guarantee a nation (0 to 1)
			take_states_cost_factor = # Changes the cost of states in a peace deal. 0.25 would increase state cost by 25% (-1 to 1)
			annex_cost_factor = # Changes the cost of entirely annexing a nation in a peace deal. 0.5 would increase annexing cost by 50% (-1 to 1)
			justify_war_goal_when_in_major_war_time = # Changes the cost of justifying a war while in a major war. 0.5 would decrease time by 50% (0 to 1)
			drift_defence_factor = # Natural drift defence for the ideology # 0.3 would grant 30% drift defence (-1 to 1)
			puppet_cost_factor = # Changes the cost of puppeting a nation in a peace deal (-1 to 1)
		}

		can_be_boosted = no # Can you boost this ideologies popularity in another country (yes/no)
		can_collaborate = yes # Can create collaboration governments

		faction_modifiers = {    # Applies to the entire faction if the faction leader has this ideology. Every country [[Modifiers|modifier]] can apply.
			faction_trade_opinion_factor = 0.50 #plus 50% trade opinion
		}
		ai_<ideology> = yes # Determines what ai this ideology will use (democratic, communism, fascism, neutral)
	}
}
```

<!-- kit:begin id="ideology-vanilla-structure" at="section:Ideologies" -->
**Kit note** What vanilla `common/ideologies/00_ideologies.txt` defines: 4 groups and 22 types. All items: [vanilla-confirmed 1.19.3] `common/ideologies/00_ideologies.txt`.

| Group | Types | `rules` block | Other group keys |
| --- | --- | --- | --- |
| `democratic` | `conservatism`, `liberalism`, `socialism`, `populism` (4) | all 8 rules: `can_create_collaboration_government = no`, `can_declare_war_on_same_ideology = no`, `can_force_government = yes`, `can_send_volunteers = no`, `can_puppet = no`, `can_lower_tension = yes`, `can_only_justify_war_on_threat_country = yes`, `can_guarantee_other_ideologies = yes` | `can_host_government_in_exile = yes`, `ai_democratic = yes`, `ai_ideology_wanted_units_factor = 1.10`, `ai_give_core_state_control_threshold = 0`, `faction_modifiers = { faction_trade_opinion_factor = 0.50 }` |
| `communism` | `marxism`, `leninism`, `stalinism`, `anti_revisionism`, `anarchist_communism`, `buddhist_socialism` (6) | `can_force_government = yes`, `can_send_volunteers = yes`, `can_puppet = yes` | `can_collaborate = yes`, `ai_communist = yes`, 1.20, 10 |
| `fascism` | `nazism`, `gen_nazism`, `fascism_ideology`, `falangism`, `rexism`, `emperor_fascism` (6) | same three, all `yes` | `can_collaborate = yes`, `ai_fascist = yes`, 1.65, 10000, `justify_war_goal_when_in_major_war_time = -0.80` |
| `neutrality` | `despotism`, `oligarchism`, `anarchism`, `moderatism`, `centrism`, `japan_militarism_ideology` (6) | `can_force_government = yes`, `can_puppet = yes`, `can_send_volunteers = no` | `ai_neutral = yes`, 1.15, 10000 |

- The last two numbers in each "Other group keys" cell are `ai_ideology_wanted_units_factor` and `ai_give_core_state_control_threshold`. The wiki example omits both keys; every vanilla group sets them.
- `can_be_randomly_selected = no` is set on exactly 4 types: `buddhist_socialism`, `emperor_fascism`, `anarchism` and `japan_militarism_ideology`. No type sets its own `color`.
- All groups set `types`, `dynamic_faction_names` (6 names for `democratic`, 5 for the others), `color` (`democratic` 0 0 255, `communism` 255 0 0, `fascism` 150 75 0, `neutrality` 124 124 124), `war_impact_on_world_tension`, `faction_impact_on_world_tension` and `modifiers`. `faction_modifiers` is set in `democratic`, empty in `communism` and `neutrality` and missing in `fascism`.
- Inside `modifiers`, vanilla also uses `civilian_intel_to_others`, `army_intel_to_others`, `navy_intel_to_others`, `airforce_intel_to_others`, `embargo_cost_factor`, `embargo_threshold_factor`, `drift_defence_factor` and, in `communism` and `fascism`, `hidden_modifier = { join_faction_tension = -0.1 }`.
<!-- kit:end id="ideology-vanilla-structure" -->

<!-- kit:begin id="ideology-example-corrections" at="section:Ideologies" -->
**Kit correction** Problems in the example block above. Items 1 to 4 are checked against the game files; each carries its own tag.

1. `take_states_cost_factor` is not a modifier. It is absent from `documentation/modifiers_documentation.md`, from `hoi4.exe` and from every vanilla file. The vanilla ideology file lists `annex_cost_factor` and `puppet_cost_factor` only as commented lines marked deprecated in favour of `00_generic_peace.txt`, which now sits in `common/peace_conference/cost_modifiers/`. Peace conference costs come from that folder (`peace_action_modifiers` with `cost_multiplier`). `annex_cost_factor` (categories peace and aggressive) and `puppet_cost_factor` (peace and defensive) are still documented modifiers. [vanilla-confirmed 1.19.4.1] `common/ideologies/00_ideologies.txt`, `common/peace_conference/cost_modifiers/`; [docs] `documentation/modifiers_documentation.md`, `common/peace_conference/cost_modifiers/_documentation.md`.
2. `ai_<ideology> = yes` is not a free pattern. Vanilla uses exactly four keys, `ai_democratic`, `ai_communist`, `ai_fascist` and `ai_neutral`, and these four are the only ideology AI strings in `hoi4.exe`. Note `communist` and `neutral`, not `communism` and `neutrality`. A new group picks one of the four. [vanilla-confirmed 1.19.4.1] `common/ideologies/00_ideologies.txt`; that no other `ai_` key exists is [unverified] (executable strings only).
3. `anarchist` and `anarcho_syndicalism` are placeholders. Neither id is used by any vanilla script: `anarcho_syndicalism` occurs nowhere, and the word `anarchist` occurs only in comments and localisation prose. Vanilla has no `anarchist` group; its anarchism is the type `anarchism` inside `neutrality`. [vanilla-confirmed 1.19.4.1] `common/ideologies/00_ideologies.txt`.
4. `can_be_boosted` is a string in `hoi4.exe` but is set by no vanilla group and is not in the documentation, so its meaning (the wiki says it controls whether other countries can boost the ideology) is [unverified]. The related rules `can_boost_own_ideology` and `can_boost_other_ideologies` exist as rule names (`can_boost_other_ideologies` in idea `rule` blocks, `can_boost_own_ideology` in `set_rule` blocks in `events/LAR_Spain.txt`); see the rule table on [Idea modding](<idea_modding.md#Modifiers>).

The wiki also says the `_drift` entries are per ideology. The documented modifier families `<Ideology>_drift`, `<Ideology>_acceptance` and `<Ideology>_drift_from_guarantees` list exactly the four groups as their valid names (`communism_drift`, `democratic_drift`, `fascism_drift`, `neutrality_drift`), not the types, so `marxism_drift` is not a modifier (0 vanilla uses). [docs] `documentation/modifiers_documentation.md`
<!-- kit:end id="ideology-example-corrections" -->

<!-- kit:begin id="ideology-duplicate-group-id" at="section:Ideologies" -->
**Kit note** Define a new group under a new id and leave the four vanilla ids (`democratic`, `communism`, `fascism`, `neutrality`) alone. `hoi4.exe` contains the database loader message "Duplicate database id", so a second definition of an existing id is the likely cause of a duplicate-id problem; whether the engine uses that message for ideology groups is not shown by script. To change a vanilla group, replace `common/ideologies/00_ideologies.txt` in the mod instead of adding a second definition. [unverified]
<!-- kit:end id="ideology-duplicate-group-id" -->

## Ai peace <a id="Ai_peace"></a>

<!-- kit:begin id="ideology-ai-peace-correction" at="heading:Ai_peace" -->
**Kit correction** The folder `common/ai_peace/` and the file `1_fascist.txt` do not exist in 1.19.4.1. AI peace desires are in `common/peace_conference/ai_peace/` (for example `00_misc.txt`, `GER.txt`, `yalta.txt`, `warlords.txt`), written as `peace_ai_desires = { name = { peace_action_type = ... enable = { ... } ai_desire = 100 } }`. `peace_action_type` is `take_states`, `puppet`, `force_government` or `liberate` (one or a list). `ROOT` is the negotiator, `ROOT.FROM` the taker, `ROOT.FROM.FROM` the giver and `ROOT.FROM.FROM.FROM` the state. `ai_desire` is a percentage change, and a total of zero or less means the AI will not take the action. Costs are separate, in `common/peace_conference/cost_modifiers/`. [docs] `common/peace_conference/ai_peace/_documentation.md`, `common/peace_conference/cost_modifiers/_documentation.md`; folder contents [vanilla-confirmed 1.19.4.1] `common/peace_conference/`.
<!-- kit:end id="ideology-ai-peace-correction" -->

AI peace determines the AI's behaviour in a peace deal. The triggers can be seen inside of enable = {} in the files, and they are generally reliant on ideologies.

The files are located in `/Hearts of Iron IV/common/ai_peace/*.txt` and every ideology has its own file. Unless the triggers are adjusted, AI will be likely to use `/Hearts of Iron IV/common/ai_peace/1_fascist.txt`. It is recommended to change the triggers in these files to assign a proper peace AI to the ideology or to create a new file.

## Getting the ideology in your game <a id="Getting_the_ideology_in_your_game"></a>

### Localisation <a id="Localisation"></a>

The names, descriptions and nouns for ideologies are defined in any `/Hearts of Iron IV/localisation/english/*.yml` file, assuming the English language. By default, the base game uses `parties_l_english.yml`
An ideology has 3 localisation keys: for its name as an adjective matching the ideology's name, for its name as a noun where _noun is appended, and for its description, used primarily in the country selection menu, where _desc is appended. Taking an ideology with the name of `my_ideology` as an example, these will look like the following:

```text
my_ideology:0 "My ideologic"
my_ideology_noun:0 "My ideology"
my_ideology_desc:0 "Ideological regime" # Must be short: only shows up in the scenario/bookmark selection screen where it should take up one line.
```

Ideology types are localised similarly, but with just the noun and description:

```text
my_subideology:0 "My ideology type" # Noun
my_subideology_desc:0 "My ideology type's description" # Shows up when hovering over an ideology icon in-game
```

Prefacing a description entry with the country's tag will make it country-specific, as `POL_my_subideology_desc:0 "Description for my_subideology that shows up only for Poland."`

Similarly, each country has ideological names:

```text
TAG_my_ideology:0 "Ideological Country"
TAG_my_ideology_ADJ:0 "Ideological" #Adjective
TAG_my_ideology_DEF:0 "the Ideological Country" #Used to say if the country's name must be prefixed with "the". Leave "the" lowercase, if adding one.
TAG_my_subideology:0 "Sub-ideological Country" #Shows up if the country has the specified ideology type. For instance, "TUR_liberalism" will be used if TUR has a leader with the liberalism ideology type.
```

If you do not define the ideology and just leave it as `TAG:0 "Test"`, it will apply to the country regardless of the ideology unless an ideology-specific name takes priority. This name is also used for the collaboration governments, referenced in localisation as `[GetNonIdeologyName]` or, specifically for cosmetic tags, as `$NONIDEOLOGY$`.

Note that you will also have to add localisation for your ideology's drift. The base game uses `/Hearts of Iron IV/localisation/english/modifiers_l_english.yml` for this.

```text
my_ideology_drift:0 "Daily Ideology Support"
```

<!-- kit:begin id="ideology-localisation-vanilla" at="section:Localisation" -->
**Kit note** Checks against `localisation/english/parties_l_english.yml` and `localisation/english/modifiers_l_english.yml`. All items: [vanilla-confirmed 1.19.4.1] those two files.

- Each vanilla group has the three keys the wiki names: `democratic` with `democratic_noun` and `democratic_desc`, and likewise `communism`, `fascism` and `neutrality`. Types have a noun and a description only, for example `conservatism` and `conservatism_desc`, `fascism_ideology` and `fascism_ideology_desc`.
- Country-specific type names exist with the tag in front: `TUR_liberalism`, `ARG_marxism`, `AUS_stalinism` (plus `_DEF`), and group names such as `GER_fascism` and `GER_democratic_DEF`.
- The drift names are `communism_drift`, `democratic_drift`, `fascism_drift` and `neutrality_drift` in `modifiers_l_english.yml` (for example `democratic_drift: "Daily Democracy Support"`), and the acceptance names are `<group>_acceptance`.
<!-- kit:end id="ideology-localisation-vanilla" -->

### GFX <a id="GFX"></a>

*See also: [Country creation § Flag](<country_creation.md#Flag>)*

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

Ideology icons are defined as sprites in any `/Hearts of Iron IV/interface/*.gfx` file, with the name of the sprite determining when it will be used.
For entire ideology groups, the sprite naming pattern must be of the sort `name = GFX_ideology_<name>_group`. If some ideology type within `types = { ... }` of the group should have a unique icon, it will be defined as `name = GFX_ideology_<name>`.

It is possible to make a sprite get used only for a certain country by prepending the country tag before the ideology's name (separated with underscores), as `GFX_ideology_<TAG>_<name>_group` for ideology groups and `GFX_ideology_<TAG>_<name>` for ideology types.

Example interface file defining ideology sprites:

```text
spriteTypes = {
    spriteType = {
        name = GFX_ideology_monarchism_group # Will be used for the "monarchism" group.
        texturefile = gfx/interface/ideologies/monarchism_group.dds
    }
    spriteType = {
        name = GFX_ideology_BHR_monarchism_group # Will be used for the "monarchism" group for the country BHR
        texturefile = gfx/interface/ideologies/BHR_monarchism_group.dds
    }
    spriteType = {
        name = GFX_ideology_absolutism # Will be used for the "absolutism" type, possibly within the "monarchism" group.
        texturefile = gfx/interface/ideologies/absolutism.dds
    }
    spriteType = {
        name = GFX_ideology_BHR_absolutism # Will be used for the "absolutism" type for the country BHR
        texturefile = gfx/interface/ideologies/BHR_absolutism.dds
    }
}
```

<!-- kit:begin id="ideology-gfx-vanilla" at="section:GFX" -->
**Kit note** Vanilla declares only six ideology sprites, all in `interface/countrypoliticsview.gfx`: `GFX_ideology_neutrality_group`, `GFX_ideology_communism_group`, `GFX_ideology_fascism_group`, `GFX_ideology_democratic_group`, `GFX_ideology_anarchism` (the one type with its own icon) and `GFX_ideology_unknown`. Textures are in `gfx/interface/ideologies/`. No vanilla sprite uses the `GFX_ideology_<TAG>_...` country pattern, so that pattern comes from the wiki alone. [vanilla-confirmed 1.19.4.1] `interface/countrypoliticsview.gfx`; country-specific sprites [unverified].
<!-- kit:end id="ideology-gfx-vanilla" -->

### Country history <a id="Country_history"></a>

If you want the ideology to appear in a country you will have to add it like this to a countries history file like this: In France, for example
`/Hearts of Iron IV/history/countries/FRA - France.txt`

```text
set_politics = {
	ruling_party = democratic
	last_election = "1932.5.1"
	election_frequency = 48
	elections_allowed = yes
}
set_popularities = { #This MUST add up to 100 otherwise the ideologies break
	democratic = 69
	fascism = 1
	communism = 30
}
```

France will now need a new leader

```text
create_country_leader = {
	name = "Édouard Daladier"
	desc = "POLITICS_ÉDOUARD_DALADIER_DESC"
	picture = "Portrait_France_Edouard_Daladier.dds"
	expire = "1965.1.1"
	ideology = socialism
	traits = {
		stout_defender
	}
}
```

<!-- kit:begin id="ideology-country-history-vanilla" at="section:Country_history" -->
**Kit note** How vanilla scripts the political setup. Counts cover every file under `common/`, `events/` and `history/`. Syntax: [docs] `documentation/effects_documentation.md`; counts: [vanilla-confirmed 1.19.4.1].

- `set_politics` has 1,051 uses. `ruling_party` takes an ideology group name: of its 1,050 values, 1,030 are literal group names (`neutrality` 355, `democratic` 304, `fascism` 194, `communism` 177) and none is a type such as `conservatism`. The rest are `ROOT` (10), `FROM` (7), a variable (2: `var:ROOT.current_party_ideology_group`, `var:ROOT.ruling_ideology_before_change`) and the tag `ETH` (1, with a comment in `events/LAR_occupation.txt` saying it copies Ethiopia's setup). Use the group name; the scope forms are [unverified].
- The effect documentation lists only `ruling_party`, `elections_allowed`, `name` and `long_name` for `set_politics`. Vanilla also uses `last_election` (500 times) and `election_frequency` (509 times), as the wiki example does.
- `set_popularities` has 515 uses and its keys are only the four group names. 476 literal blocks add up to exactly 100; 36 use variables; 3 in `common/national_focus/brazil.txt` set a single group to 0. The documentation says unlisted groups become 0 and the total must be exactly 100.
- `add_popularity = { ideology = group popularity = 0.05 }` takes group names (`fascism` 574, `communism` 489, `democratic` 331, `neutrality` 288) as well as scope or variable values. 1,831 uses.
- `create_country_leader` (176 uses) is still in vanilla, but new leaders are normally characters with a `country_leader` role; see [Character modding](<character_modding.md#Country_leaders>). The `ideology` there is a type, not a group.
<!-- kit:end id="ideology-country-history-vanilla" -->

### Political advisor <a id="Political_advisor"></a>

<!-- kit:begin id="ideology-advisor-correction" at="heading:Political_advisor" -->
**Kit correction** In 1.19.4.1 vanilla builds the generic ideology booster advisors with `generate_character` in `history/general/generic_advisors.txt`, not as ideas in `zzz_generic.txt` as the template below does: `token_base = generic_communist_revolutionary` (and `generic_democratic_reformer`, `generic_fascist_demagogue`), each with `advisor = { slot = political_advisor traits = { communist_revolutionary } available = { ... } ai_will_do = { factor = 1 } }` and `portraits = { army = { small = GFX_idea_generic_communist_revolutionary } }`. The guard is `NOT = { has_allowed_idea_with_traits = { idea = communist_revolutionary characters = yes } }`. `zzz_generic.txt` still exists but holds hidden ideas, national spirits and designer and company ideas, and `has_available_idea_with_traits` (used in the wiki template) has no vanilla use, while `has_allowed_idea_with_traits` has 15. [vanilla-confirmed 1.19.4.1] `history/general/generic_advisors.txt`, `common/ideas/zzz_generic.txt`.

The trait part matches the wiki. Vanilla `communist_revolutionary`, `democratic_reformer` and `fascist_demagogue` in `common/country_leader/00_traits.txt` each set `random = no`, `sprite = 13` and `<group>_drift = 0.1` plus an `ai_will_do`. The `<ideology>_booster` suffix in the template is the wiki's own and occurs in no vanilla file. [vanilla-confirmed 1.19.4.1] `common/country_leader/00_traits.txt`. For a custom advisor, define a character with an advisor role instead; see [Character modding](<character_modding.md#Advisors>).
<!-- kit:end id="ideology-advisor-correction" -->

In order to add a political advisor increasing the popularity of the ideology, first, a trait that will be added to that advisor must be added in `/Hearts of Iron IV/common/country_leader/*.txt`

```text
<ideology>_booster = {
	random = no
	sprite = 13
	<ideology>_drift = 0.1

	ai_will_do = {
		factor = 0
	}
}
```

Localisation can be added like so:

```text
<ideology>_booster:0 "Ideology booster" #Whatever you want to call the person that supports the ideology. Eg. Democratic Politician, Communist Politician, Fascist Politician
```

It is recommended to add the generic advisors in `/Hearts of Iron IV/common/ideas/zzz_generic.txt` to ensure the file is loaded after the country-specific ones. A generic advisor can be added following this example:

```text
 <name> = {

	allowed = {
		NOT = {
			has_available_idea_with_traits = { idea = <ideology>_booster limit = 1 }		#In order to prevent it from appearing alongside country-specific ones.
		}
	}
	traits = { <ideology>_booster }

	available = {
		if = {
			limit = { has_dlc = "Man the Guns" }
			NOT = { has_autonomy_state = autonomy_supervised_state }
		}
	}

	do_effect = {
		NOT = {
			has_government = <ideology> # You can only select it if your current ideology isn't your new one
		}
	}

	ai_will_do = {
		factor = 0
	}
}
```

More information about GFX and localisation can be found in the [Idea modding](<idea_modding.md>) page.

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>) • [Units](<unit_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
