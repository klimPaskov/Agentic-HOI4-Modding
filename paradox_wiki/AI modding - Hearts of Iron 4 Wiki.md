# Table of contents

- [MTTH blocks](#mtth-blocks)
  - [Example](#example)
- [AI strategies](#ai-strategies)
  - [Arguments](#arguments)
  - [Types](#types)
- [AI areas](#ai-areas)
- [AI focuses](#ai-focuses)
- [AI peace](#ai-peace)
- [AI strategy plans](#ai-strategy-plans)
  - [Example](#example_2)
- [AI templates](#ai-templates)
  - [Example](#example_3)
- [AI equipment](#ai-equipment)
  - [Example](#example_4)

---

The artificial intelligence controlling countries in Hearts of Iron IV can be changed in many different aspects. This includes changing the focuses or technologies it pursues, changing how many units or buildings it should produce and of which type, where it should focus forces, which templates or variants it should aim for, and so on.

## <a id="mtth-block"></a><a id="mtth-blocks"></a>MTTH blocks

<a id="ai-will-do"></a>
<a id="ai-will-do"></a>
<a id="ai-chance"></a>

MTTH blocks, named in the game within /Hearts of Iron IV/common/mtth/, are a way to assign a dynamic value to some block, whether it's a [country = { ... } in a focus tree to assign which countries can get it](<National focus modding - Hearts of Iron 4 Wiki.md#focus-tree>), a dynamically-changing variable value (as in /Hearts of Iron IV/common/mtth/), a [mean-time-to-happen value for an event](<Event modding - Hearts of Iron 4 Wiki.md#triggering>), et cetera. As MTTH blocks are spread throughout the entire game, it's incredibly important to know how one works. Its most common application, however, is assigning a base AI weight to a database entry such as a national focus or a technology.

In most cases, marked with ai\_will\_do, the approach taken by the game is generating a decimal number between 0 and the value of the ai\_will\_do block, and picking the entry with the highest value. There can be other modifiers applied after the ai\_will\_do value, such as the ones applied within [AI strategy plans](#ai-strategy-plans) towards focuses and research or the ones that get defined within [Defines](<Defines - Hearts of Iron 4 Wiki.md>), which'll multiply the value you get. This can include different ai\_will\_do values such as what's done with country leader traits and with ideas or characters that use them.  
Event options, instead, use ai\_chance, which uses [probability-proportional-to-size sampling](http://en.wikipedia.org/wiki/Sampling_(statistics)#Probability-proportional-to-size_sampling) with a virtual roll of d00 being the final deciding factor. Due to that, in the end, an event option cannot have a probability which isn't a multiple of 1/100 to be picked, although the total sum of each option's weights can be vastly different from 100. In other words, if one option has a value of 1, while the other has a value of 999, the probability for the first option to be picked will be 1% rather than 0.1%.

A MTTH block begins with an assumed value of 1. Further manipulations are done from that value as a starting point. There are 3 value-modifying arguments that can be done, `add`, `base`, and `factor`, done like `factor = 0.3`, `base = 10`, or `add = 5`. `add` adds the specified argument to the value, `factor` *multiplies* it, and `base`, typically done in the start before any changes, sets it to a different number entirely, akin to multiplying by 0 and adding the number.  
In order for an operation to apply conditionally, a `modifier = { ... }` block is used. This also functions as a trigger block, with the default scope (thus also ROOT) being the country for which the MTTH block is evaluated. Depending on the MTTH block, [there may be additional scopes marked with FROM](<Decision modding - Hearts of Iron 4 Wiki.md#targeted-decisions>) [or FROM.FROM other than the default.](#ai-peace) The value-modifying arguments function as regular arguments, they can be put in anywhere directly within the `modifier = { ... }` block with almost no difference, whether it's in the end, the beginning, or between triggers.

Variables can be used within the value-modifying arguments as well. If using a temporary variable that is defined within the `modifier = { ... }` trigger block, then the value-modifying argument of the modifier has to be after the definition of the variable in order for the variable to apply as defined. Variables can also be used outside of the `modifier = { ... }` block and directly inside of the MTTH block itself.

### <a id="example"></a>Example

```text
ai_will_do = {
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

    modifier = {
        set_temp_variable = { t = num_of_civilian_factories }
        add_to_temp_variable = { t = num_of_military_factories }
        divide_temp_variable = { t = 10 }
        round_temp_variable = t
        add = t
    }
}
```

Assuming that GER and FRA are major countries, the result is

- 0 for GER: ![{\displaystyle 10.5\cdot 0=0}](media/ai-modding-hearts-of-iron-4-wiki_04cfcba22e__img1.svg)
- 74 for FRA: ![{\displaystyle ((10.5+1)\cdot 3+2.5)\cdot 2=74}](media/ai-modding-hearts-of-iron-4-wiki_04cfcba22e__img2.svg)
- 23 for other majors: ![{\displaystyle (10.5+1)\cdot 2=23}](media/ai-modding-hearts-of-iron-4-wiki_04cfcba22e__img3.svg)
- 21 for minors: ![{\displaystyle 10.5\cdot 2=21}](media/ai-modding-hearts-of-iron-4-wiki_04cfcba22e__img4.svg)

After calculating that value, the total number of civilian and military factories within the country, divided by 10 and rounded, will get added to the score. If FRA has a total of 43 civilian and military factories as it does in base game, then this will result in 4 being added to the prior 74 for a total of 78, for example.

## <a id="ai-strategies"></a>AI strategies

AI strategies are used in order to pursue AI to do or avoid something. This includes diplomatic actions the AI will do, where and how exactly AI should focus and use its land army and the navy, the production lines for buildings and equipment, how AI should handle the intelligence system within the ![La Résistance](media/ai-modding-hearts-of-iron-4-wiki_04cfcba22e__img6.png) La Résistance DLC.  
A value within an AI strategy can be either positive or negative, and it being negative will make AI desire to do it less.

Regular AI strategies are stored in /Hearts of Iron IV/common/ai\_strategy/\*.txt files, however, AI strategies may be defined outside of that file. The [add\_ai\_strategy effect](<Effects - Hearts of Iron 4 Wiki.md#add-ai-strategy>) can add a permament AI strategy within any effect block, and [AI strategy plans](#ai-strategy-plans) can also include AI strategies defined within of themselves. Overall, /Hearts of Iron IV/common/ai\_strategy/\*.txt files describe AI strategies that would enable and disable themselves automatically.  
Each entry within a /Hearts of Iron IV/common/ai\_strategy/\*.txt file is a block with the name of the AI strategy. This name can be anything, even allowing overlap between them: this will only appear in AI dumps and the player will never see it. If an AI strategy modifies the chance for AI to pick a diplomatic option with the player, it will be seen as `COUNTRY has strategic reasons to be ...` to the player when hovering over the option. This is an example of an AI strategy with the name of BHR\_invade\_qatar:

```text
BHR_invade_qatar = {
    allowed = {
        original_tag = BHR
    }
    enable = {
        country_exists = QAT
    }
    abort = {
        has_war_with = QAT
    }
    abort_when_not_enabled = yes
    ai_strategy = {
        type = invade
        id = QAT
        value = 200
    }
}
```

### <a id="arguments"></a>Arguments

These in particular are arguments for /Hearts of Iron IV/common/ai\_strategy/\*.txt entries, rather for AI strategy entries within them.

`allowed = { ... }` is a trigger block that's **checked only before the game's start**, permamently allowing or disallowing an AI strategy. Typically, only used for country checks (such as `tag = OMA`) or DLC checks that can never be unfulfilled once they are met.

`enable = { ... }` is a trigger block that must be met in order to enable the AI strategy. By default, this being unmet will *not* cancel the AI strategy. However, `abort_when_not_enabled = yes` can be used as a separate argument in order to make that be no longer the case. Unlike allowed, this is checked continuously.

`abort = { ... }` is a trigger block that must be met in order to *remove* the AI strategy. It being unmet also prevents it from being added in the first place.

`ai_strategy = { ... }` is, itself, the AI strategy that would be applied. The only argument shared for every AI strategy is `type = <AI strategy type>`. [The rest depends on the AI strategy](#types).

In addition, reversed AI strategies exist. These are used with AI strategies that use `id = TAG` to target towards a specific country to swap it around: that strategy will be enabled for TAG towards the country which meets `enable = { ... }`. In order to mark the AI strategy as reversed, `reversed = yes` is used. `enable_reverse = { ... }` is an additional trigger block required to *enable* this AI strategy. It does not have a default scope, so scoping into a country is required.  
An example of a reversed AI strategy is the following:

```text
BHR_support_neutrals = {
    allowed = {
        NOT = { original_tag = BHR }
    }
    enable = {
        has_government = neutrality
    }
    enable_reverse = {
        BHR = { has_government = neutrality }
    }
    reversed = yes
    abort_when_not_enabled = yes
    ai_strategy = {
        type = support
        id = BHR
        value = 100
    }
}
```

Without `reversed = yes`, this would make every ![{{{1}}}](media/ai-modding-hearts-of-iron-4-wiki_04cfcba22e__img7.png) non-aligned country support BHR. Due to that argument, the strategy is reversed: instead, BHR supports every ![{{{1}}}](media/ai-modding-hearts-of-iron-4-wiki_04cfcba22e__img8.png) non-aligned country.

### <a id="types"></a>Types

This list may be outdated. A list of every AI strategy can be found within base game's /Hearts of Iron IV/common/ai\_strategy/documentation.info file.

AI strategies related to diplomatic actions:
| Name | Parameters | Examples | Description | Notes |
| --- | --- | --- | --- | --- |
| <a id="alliance"></a> alliance | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = alliance id = USA value = -100 }` | Pursues AI to ally with a country, joining the same faction if possible. |  |
| <a id="antagonize"></a> antagonize | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = antagonize id = USA value = -100 }` | Pursues AI to antagonize a country, refusing most diplomatic actions with them. |  |
| <a id="asking-foreign-garrison"></a> asking\_foreign\_garrison | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = asking_foreign_garrison id = USA value = 100 }` | Pursues AI to ask for foreign manpower to fulfill garrisons, from a specific country if specified. | If `id` is not specified, will apply towards every other country. |
| <a id="befriend"></a> befriend | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = befriend id = USA value = 100 }` | Pursues AI to befriend a country, accepting most diplomatic actions with them. |  |
| <a id="conquer"></a> conquer | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = conquer id = USA value = 100 }` | Pursues AI to conquer a country, being more likely to declare war and justify wargoals. | This does *not* change how the AI will control frontlines when at war with that country. |
| <a id="consider-weak"></a> consider\_weak | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = consider_weak id = USA value = 100 }` | Pursues AI to consider a country more weak, decreasing hesitation for declaration of war or making alliance less likely. |  |
| <a id="contain"></a> contain | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = contain id = USA value = 100 }` | Pursues AI to contain a country, protecting any countries that it would try to antagonize or invade. |  |
| <a id="declare-war"></a> declare\_war | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = declare_war id = USA value = 100 }` | Pursues AI to declare war on a country if a wargoal already exists. |  |
| <a id="diplo-action-acceptance"></a> diplo\_action\_acceptance | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy.  `target = <diplomatic action>` The diplomatic action to modify. | `ai_strategy = { type = diplo_action_acceptance id = USA value = 100 target = join_allies }` | Pursues AI to accept a diplomatic action if a different country requests it. | AI will not be more likely to propose the diplomatic action in question. Names of diplomatic actions can usually be found from localisation keys used for the title, most of the time yet not always in the /Hearts of Iron IV/localisation/english/diplomacy\_l\_english.yml file: `DIPLOMACY_SEND_VOLUNTEERS_TITLE:0 "Send Volunteers"` means that the name of the diplomatic action for sending volunteers is `send_volunteers`. |
| <a id="diplo-action-desire"></a> diplo\_action\_desire | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy.  `target = <diplomatic action>` The diplomatic action to modify. | `ai_strategy = { type = diplo_action_desire id = USA value = 100 target = call_allies }` | Pursues AI to request a diplomatic action towards the specified country. | AI will not be more likely to accept the diplomatic action in question if it gets proposed to them. Names of diplomatic actions can usually be found from localisation keys used for the title, most of the time yet not always in the /Hearts of Iron IV/localisation/english/diplomacy\_l\_english.yml file: `DIPLOMACY_SEND_VOLUNTEERS_TITLE:0 "Send Volunteers"` means that the name of the diplomatic action for sending volunteers is `send_volunteers`. |
| <a id="dont-join-wars-with"></a> dont\_join\_wars\_with | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy.  `target_country = <country>` The country against whom the war is joined. | `ai_strategy = { type = dont_join_wars_with id = USA value = 100 target_country = BHR }` | Pursues AI to be less likely to join a war together with a specified country against a specific one. | Does not make AI less likely to join a war together with a *different* country against target\_country, even if it'll result in fighting against target\_country together with the specified country. |
| <a id="ignore"></a> ignore | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = ignore id = USA value = 100 }` | Pursues AI to be less likely to accept or desire any sort of diplomatic action with this country. |  |
| <a id="ignore-claim"></a> ignore\_claim | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = ignore_claim id = USA value = 1 }` | Pursues AI to ignore any claims that it has on the specified country. | The value is boolean, just set to be 1. |
| <a id="protect"></a> protect | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = protect id = USA value = 100 }` | Pursues AI to protect a certain country, guaranteeing them or adding to the same faction. | A negative total value (taking every AI strategy into consideration) results in AI never guaranteeing that country. |
| <a id="support"></a> support | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = support id = USA value = 100 }` | Pursues AI to support a certain country within wars, sending lend lease, volunteers, or expeditionary forces. |  |
| <a id="send-lend-lease-desire"></a> send\_lend\_lease\_desire | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = send_lend_lease_desire id = USA value = 100 }` | Pursues AI to lend-lease equipment to the specified country. |  |
| <a id="send-volunteers-desire"></a> send\_volunteers\_desire | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = send_volunteers_desire id = USA value = 100 }` | Pursues AI to send volunteers to the specified country. |  |

AI strategies related to land army management:
| Name | Parameters | Examples | Description | Notes |
| --- | --- | --- | --- | --- |
| <a id="invade"></a> invade | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = invade id = USA value = -100 }` | Pursues AI to do naval invasions against the specified country. |  |
| <a id="naval-invasion-focus"></a> naval\_invasion\_focus | `value = <int>` The weight of the strategy. | `ai_strategy = { type = naval_invasion_focus value = 100 }` | Pursues AI to launch naval invasions. |  |
| <a id="prepare-for-war"></a> prepare\_for\_war | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = prepare_for_war id = USA value = 100 }` | Pursues AI to prepare for a war against a specified country, moving troops to their border. |  |
| <a id="area-priority"></a> area\_priority | `value = <int>` The weight of the strategy.  `id = <AI area>` The [AI area](#ai-areas) to prioritise. | `ai_strategy = { type = area_priority id = europe value = 100 }` | Pursues AI to put more units within the specified AI area. |  |
| strategic\_air\_importance | `id = <strategic_region>` The strategic region to consider `value = <int>` The score added or substracted. | `ai_strategy = { type = strategic_air_importance id = 18 #English Channel value = -30000 }` | Modifies the total 'Strategic Importance' score of the specified region that the AI uses to prioritize where to perform Air Missions. | - ID of the strategic regions can be found here, in /Hearts of Iron IV/map/strategicregions/\*.txt files, or alternatively in the game using [console command](<Console commands - Hearts of Iron 4 Wiki.md>) *tdebug* and hovering a mouse over the specific region while in the 'Default' map mode. - Current 'Strategic Importance' AI score can be found in the game using [console command](<Console commands - Hearts of Iron 4 Wiki.md>) *aiview* , while in the 'observe mode' and hovering a mouse over the desired air zone, while using the 'Strategic Air' map mode. The score shown is for the currently selected TAG. AI wants to do air missions in the regions with the highest scores, and none in the regions with low or negative score. - AI score numbers are large, in higher dozens of thousands or lower hundreds of thousands, so appropriate values need to be used to have any visible effect on the AI. |
| <a id="dont-defend-ally-borders"></a> dont\_defend\_ally\_borders | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = dont_defend_ally_borders id = POL value = 10 }` | Makes AI never put troops on the border between the specified country and countries that are at war with it. | Strictly binary. If the total value (taking every AI strategy into consideration) is positive, AI will never put any troops on the border. |
| <a id="force-defend-ally-borders"></a> force\_defend\_ally\_borders | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = force_defend_ally_borders id = FRA value = 100 }` | Pursues AI to put troops on the border between the specified country and countries that are at war with it. | Also accepts [AI areas](#ai-areas) within `id`. |
| <a id="front-armor-score"></a> front\_armor\_score | `value = <int>` The weight of the strategy.  `id = <country>` The target of the strategy. | `ai_strategy = { type = front_armor_score id = POL value = 100 }` | Pursues AI to put more tank units for invading the specified country. |  |
| <a id="front-control"></a> front\_control | `state = <state>` The state to target.  `tag = <country>` The country to target.  `strategic_region = <ID>` The strategic region to target.  `area = <area>` The [AI area](#ai-areas) to target.  `country_trigger = { ... }` Trigger block checked for states to have them as a target.  `state_trigger = { ... }` Trigger block checked for countries to have them as a target.  `ratio = <decimal>` How much of a frontline ratio the specified front must have **as a requirement to enable the strategy**. Defaults to 0.  `priority = <integer>` Sets the priority of this front control strategy. If there are contradictory front control strategies, the one with a higher priority is followed.  `ordertype = <front\|invasion>` If set, this will make the AI strategy only apply on land frontlines or naval invasions respectively.  `execution_type = <careful\|balanced\|rush\|rush_weak>` If set, this pursues AI to make the frontline plans have the set execution type. Only for front.  `execute_order = <bool>` If set, makes AI to either force execute the frontline order or force it being never executed.  `manual_attack = <bool>` If set to false, prevents AI from doing small engagements that are not a part of a frontline plan. Defaults to true, only for front. | `ai_strategy = { type = front_control state_trigger = { industrial_complex > 1 is_owned_by = ENG } ratio = 0.1 ordertype = front execution_type = rush manual_attack = no }`  `ai_strategy = { type = front_control area = suez priority = 1 ratio = 0.2 ordertype = invasion execute_order = yes }` | Modifies the orders that AI would give to divisions on a specified frontline. | More than one target type can be used at a time, in which case each one must be met. This only changes the orders assigned to an already-existing frontline, this will not change the amount of units assigned to any particular front or force any to be created. |
| force\_concentration\_front\_factor | `tag = <country>` The country to target. Multiple can be specified. `state = <state>` The state to target. Multiple can be specified. `strategic_region = <ID>` The strategic region to target. Multiple can be specified. `area = <area>` The [AI area](#ai-areas) to target. Multiple can be specified. `country_trigger = { ... }` Trigger block checked for countries. Scope is enemy country, FROM scope is our country. `state_trigger = { ... }` Trigger block checked for states.  Scope is state. FROM scope is enemy country FROM.FROM scope is our country.  `ratio = <decimal>` The strategy is enabled only if ratio of the front covered by this strategy's targets is greater than this ratio. `value = <int>` Factor for the normal priority. 40 means +40 %, -60 means -60 %. | `ai_strategy = { type = force_concentration_front_factor tag = CZE state = 9 strategic_region = 22 ratio = 0.2 value = 40 }` | Used for increasing/decreasing priority score for AI force concentration on specified fronts. | All the arguments are optional, only one needs to be specified. AI primarily assigns units with 'armor' , 'heavy\_armor' and 'mechanized\_assault' unit roles to the attack. |
| force\_concentration\_factor | `value = <int>` The percentage value added or substracted. | `ai_strategy = { type = force_concentration_factor value = 20 }` | Factor added on top of the default force concentration ratio. Value of 20 means +20 %, so if the base define is 15 % the result would be 35 %. | See FORCE\_CONCENTRATION\_UNIT\_RATIO\_BASE in the [defines](<Defines - Hearts of Iron 4 Wiki.md>). A large negative value stops AI from using Force Concentration anywhere. |
| force\_concentration\_target\_weight | `tag = <country>` The country to target. Multiple can be specified. `state = <state>` The state to target. Multiple can be specified. `strategic_region = <ID>` The strategic region to target. Multiple can be specified. `area = <area>` The [AI area](#ai-areas) to target. Multiple can be specified. `country_trigger = { ... }` Trigger block checked for countries. Scope is enemy country, FROM scope is our country. `state_trigger = { ... }` Trigger block checked for states.  Scope is state. FROM scope is enemy country FROM.FROM scope is our country.  `value = <int>` Factor for the normal priority. 40 means +40 %, -60 means -60 %. | `ai_strategy = { # As Germany - Avoid attacking the areas behind the Maginot line type = force_concentration_target_weight state = 18 # Champagne state = 17 # Franche-Comte state = 28 # Alsace-Lorraine state = 27 # Bourgogne value = -60 }` | Affects the score for offensive targets for AI Force Concentration. | All the arguments are optional, only one needs to be specified. |
| <a id="front-unit-request"></a> front\_unit\_request | `state = <state>` The state to target.  `tag = <country>` The state to target.  `strategic_region = <ID>` The strategic region to target.  `area = <state>` The [AI area](#ai-areas) to target.  `country_trigger = { ... }` Trigger block checked for states to have them as a target.  `state_trigger = { ... }` Trigger block checked for countries to have them as a target.  `value = <int>` The weight of the strategy. | `ai_strategy = { type = front_unit_request tag = POL value = 100 }`  `ai_strategy = { type = front_unit_request country_trigger = { original_tag = SPR has_government = fascism } value = 100 }` | Pursues AI to put more (or less - if negative value is used) units on a specified land frontline. | More than one target type can be used at a time, in which case each one must be met. |
| <a id="invasion-unit-request"></a> invasion\_unit\_request | `state = <state>` The state to target.  `tag = <country>` The state to target.  `strategic_region = <ID>` The strategic region to target.  `area = <state>` The [AI area](#ai-areas) to target.  `country_trigger = { ... }` Trigger block checked for states to have them as a target.  `state_trigger = { ... }` Trigger block checked for countries to have them as a target.  `value = <int>` The weight of the strategy. | `ai_strategy = { type = invasion_unit_request state = 123 value = 100 }`  `ai_strategy = { type = invasion_unit_request strategic_region = 42 value = 100 }` | Pursues AI to put more units on a naval invasion with the specified target. | More than one target type can be used at a time, in which case each one must be met. |
| <a id="garrison"></a> garrison | `value = <int>` The weight of the strategy. | `ai_strategy = { type = garrison value = 10 }` | Controls the amount of units spent on defending the victory points and ports rather than being active on the frontline. |  |
| <a id="garrison-reinforcement-priority"></a> garrison\_reinforcement\_priority | `value = <int>` The weight of the strategy. | `ai_strategy = { type = garrison_reinforcement_priority value = 100 }` | Pursues AI to reinforce units that are put on garrisons, protecting victory points and naval bases, with higher priority. |  |
| <a id="ignore-army-incompetence"></a> ignore\_army\_incompetence | `value = <int>` The weight of the strategy. | `ai_strategy = { type = ignore_army_incompetence value = 100 }` | Pursues AI to ignore the modifier given by the lack of experience of divisions in calculations. |  |
| <a id="put-unit-buffers"></a> put\_unit\_buffers | `ratio = <decimal>` The amount of units to buffer.  `order_id = 2`  If two put\_unit\_buffers strategies use the same ID, the ratio used for them will be shared rather than them being added together.  `states = { ... }`  List of states where to buffer units  `area = <AI area>`  The AI area where to buffer units.  `subtract_invasions_from_need = yes`  If true, naval invasions within the area will not count towards the ratio. Defaults to false.  `subtract_fronts_from_need = yes`  If true, land frontlines within the area will not count towards the ratio. Defaults to false. | `ai_strategy = { type = put_unit_buffers ratio = 0.2 states = { 123 124 125 126 } subtract_fronts_from_need = yes }` | Pursues AI to keep a certain ratio of divisions on garrison duty in the specified area. |  |
| <a id="spare-unit-factor"></a> spare\_unit\_factor | `value = <int>` The weight of the strategy. | `ai_strategy = { type = spare_unit_factor value = 100 }` | Pursues AI to spare more units towards defending allies. |  |
| <a id="theatre-distribution-demand-increase"></a> theatre\_distribution\_demand\_increase | `value = <int>` The weight of the strategy.  `id = <state>` The target of the strategy. | `ai_strategy = { type = theatre_distribution_demand_increase value = 10 id = 123 }` | Pursues AI to put more units in the specified state's theater. | A value of 1 translates to 1 unit. |

AI strategies related to navy management:
| Name | Parameters | Examples | Description | Notes |
| --- | --- | --- | --- | --- |
| <a id="naval-avoid-region"></a> naval\_avoid\_region | `value = <int>` The weight of the strategy.  `id = <strategic region>` The target of the strategy. | `ai_strategy = { type = naval_avoid_region id = 23 value = 100 }` | Pursues AI to avoid a specific strategic region with its ships. |  |
| <a id="naval-convoy-raid-region"></a> naval\_convoy\_raid\_region | `value = <int>` The weight of the strategy.  `id = <strategic region>` The target of the strategy. | `ai_strategy = { type = naval_convoy_raid_region id = 23 value = 100 }` | Pursues AI to raid convoys within the specified strategic region. |  |
| <a id="naval-mission-threshold"></a> naval\_mission\_threshold | `value = <int>` The weight of the strategy.  `id = <mission>` The mission to change the threshold of. | `ai_strategy = { type = naval_mission_threshold id = MISSION_CONVOY_RAIDING value = -100 }` | Makes AI have a higher threshold for its desire to do a naval mission. | A higher value means AI is less likely to do the mission. Names of missions can be found in /Hearts of Iron IV/localisation/english/core\_l\_english.yml, where a localisation key of `NAVAL_MISSION_NAME_CONVOY_RAIDING` means the mission is called `MISSION_CONVOY_RAIDING` |
| <a id="strike-force-home-base"></a> strike\_force\_home\_base | `value = <int>` The weight of the strategy.  `id = <strategic region>` The target of the strategy. | `ai_strategy = { type = strike_force_home_base id = 18 value = 70 }` | Pursues AI to do the strike force mission within the specified strategic region. |  |

AI strategies related to intelligence:
| Name | Parameters | Examples | Description | Notes |
| --- | --- | --- | --- | --- |
| <a id="agency-ai-base-num-factories-factor"></a> agency\_ai\_base\_num\_factories\_factor | `value = <int>` The weight of the strategy. | `ai_strategy = { type = agency_ai_base_num_factories_factor value = 70 }` | Changes the baseline used in the calculation of AI doing agency upgrades. | A value of 1 equals to a 1% increase over the baseline in [Defines](<Defines - Hearts of Iron 4 Wiki.md>). |
| <a id="agency-ai-per-upgrade-factories-factor"></a> agency\_ai\_per\_upgrade\_factories\_factor | `value = <int>` The weight of the strategy. | `ai_strategy = { type = agency_ai_per_upgrade_factories_factor value = 70 }` | Modifies the needed amount of factories used in the calculation of AI doing agency upgrades. | A value of 1 equals to a 1% increase over the baseline in [Defines](<Defines - Hearts of Iron 4 Wiki.md>). |
| <a id="intelligence-agency-branch-desire-factor"></a> intelligence\_agency\_branch\_desire\_factor | `value = <int>` The weight of the strategy.  `id = <branch>` The target of the strategy. | `ai_strategy = { type = intelligence_agency_branch_desire_factor id = branch_crypto value = 70 }` | Modifies the needed amount of factories used in the calculation of AI doing agency upgrades. | Branches are defined in /Hearts of Iron IV/common/intelligence\_agency\_upgrades/\*.txt files. |
| <a id="intelligence-agency-usable-factories"></a> intelligence\_agency\_usable\_factories | `value = <int>` The weight of the strategy. | `ai_strategy = { type = intelligence_agency_usable_factories value = 8 }` | Modifies the amount of factories that AI would use for intelligence agencies. |  |
| <a id="operation-equipment-priority"></a> operation\_equipment\_priority | `value = <int>` The weight of the strategy. | `ai_strategy = { type = operation_equipment_priority value = 80 }` | Pursues the AI to prioritise equipment for funding operations over other usages. |  |
| <a id="operative-mission"></a> operative\_mission | `value = <int>` The weight of the strategy.  `mission = <mission>` The mission to prioritise  `mission_target = <country>` The country to target  `state = <state>` The state to prioritise within the target country if valid. Optional.  `priority = <int>` If contradictory AI strategies are defined, the one with the highest priority is picked. `num_operatives = <int>`  Number of operatives to assign to mission. Optional. | `ai_strategy = { type = operative_mission value = 80 mission = quiet_intel_network state = 123 state = 321 mission_target = ENG }` | Pursues the AI to do the specified mission over the target. | Multiple states can be defined, leading to one of them being prioritised. Mission names can be seen in /Hearts of Iron IV/localisation/english/operatives\_l\_english.yml. For example, `OPERATIVE_MISSION_BOOST_IDEOLOGY_TITLE:0 "Boost Ideology"` means that boosting ideology is boost\_ideology. |
| <a id="operative-operation"></a> operative\_operation | `value = <int>` The weight of the strategy.  `operation = <mission>` The mission to prioritise  `operation_target = <country>` The country to target  `state = <state>` The state to prioritise within the target country if valid. Optional.  `region = <strategic region>` The strategic region to prioritise within the target country if valid. Optional.  `priority = <int>` If contradictory AI strategies are defined, the one with the highest priority is picked. | `ai_strategy = { type = operative_operation value = 80 operation = heavy_water_raid operation_target = ENG }` | Pursues the AI to do the specified operation over the target. | Multiple states can be defined, leading to one of them being prioritised. Operations are defined within /Hearts of Iron IV/common/operations/\*.txt files. |
| <a id="become-spymaster"></a> become\_spymaster | `value = <int>` The weight of the strategy. | `ai_strategy = { type = become_spymaster value = 30 }` | Used to set weight for a faction leader to become spymaster if not already a spymaster | Weight value for pp spend to become spymaster. Added in 1.15.2 |

AI strategies related to production, construction, and recruitment:
| Name | Parameters | Examples | Description | Notes |
| --- | --- | --- | --- | --- |
| <a id="added-military-to-civilian-factory-ratio"></a> added\_military\_to\_civilian\_factory\_ratio | `value = <int>` The weight of the strategy. | `ai_strategy = { type = added_military_to_civilian_factory_ratio value = 50 }` | Modifies the ratio of military to civilian factories that the AI desires to keep. | A positive value means more military factories. |
| <a id="air-factory-balance"></a> air\_factory\_balance | `value = <int>` The weight of the strategy. | `ai_strategy = { type = air_factory_balance value = 50 }` | Modifies the ratio of airforce to factories that the AI desires to keep. | A positive value means more airforce. |
| <a id="dockyard-to-military-factory-ratio"></a> dockyard\_to\_military\_factory\_ratio | `value = <int>` The weight of the strategy. | `ai_strategy = { type = dockyard_to_military_factory_ratio value = 50 }` | Modifies the ratio of dockyards to military factories that the AI desires to keep. | A positive value means more dockyards. |
| <a id="railway-gun-divisions-ratio"></a> railway\_gun\_divisions\_ratio | `value = <int>` The weight of the strategy. | `ai_strategy = { type = railway_gun_divisions_ratio value = 5 }` | Modifies the ratio of railway guns to divisions that the AI desires to keep. | Base ratio is RAILWAY\_GUN\_PRODUCTION\_BASE\_DIVISIONS\_RATIO\_PERCENT in [Defines](<Defines - Hearts of Iron 4 Wiki.md>), by default 0. This gets added to it, on the 0-100 scale. |
| <a id="build-building"></a> build\_building | `value = <int>` The weight of the strategy.  `id = <building>` The target of the strategy.  `target = <state> (OR) <province>` The state (or province) where to build. | `ai_strategy = { type = build_building id = industrial_complex target = 803 value = 1 }` | Pursues AI to construct a specific building within the specified state (or a specified province, if the building is province based). If no target is specified, AI selects a random location. | Value is an AI weight, used for weighted random selection of what to build. The AI gathers all build\_building strategies (including the ones created dynamically) with non-zero values, and selects one of them. Strategy is ignored if the specified building is already being constructed. |
| <a id="building-target"></a> building\_target | `value = <int>` The weight of the strategy.  `id = <building>` A building to consider. | `ai_strategy = { type = building_target id = industrial_complex value = 30 }` | Makes AI keep a minimum amount of the specified buildings. | The AI will construct the specified building until it reaches the target value (prioritizing it over other construction). **Note:** The AI uses 'total' amount of buildings. So in this specific case it will check, if it has a total of 30 Civilian Factories in its own states, in the occupied states AND from trade and received from subjects! |
| <a id="factory-build-score-factor"></a> factory\_build\_score\_factor | `value = <int>` The weight of the strategy.  `target = <state>` The state where to build. | `ai_strategy = { type = factory_build_score_factor target = 365 value = 1 }` | Pursues AI to construct buildings within the specified state. |  |
| <a id="equipment-production-factor"></a> equipment\_production\_factor | `value = <int>` The weight of the strategy.  `id = <equipment archetype type>` The target of the strategy. | `ai_strategy = { type = equipment_production_factor id = armor value = 30 }` | Pursues AI to produce equipment types of the specified type. | Types are defined for each equipment archetype in /Hearts of Iron IV/common/units/equipment/\*.txt files within `types = { ... }`. |
| <a id="equipment-production-min-factories"></a> equipment\_production\_min\_factories | `value = <int>` The weight of the strategy.  `id = <equipment type>` The target of the strategy. | `ai_strategy = { type = equipment_production_min_factories id = artillery value = 3 }` | Pursues AI to keep a minimum amount of factories on the production lines for the equipment of the specified **type**. If multiple strategies are used at once, they stack. | A value of 1 corresponds to 1 military factory. Types are defined for each equipment archetype in /Hearts of Iron IV/common/units/equipment/\*.txt files within `types = { ... }`. **Note:** Multiple variants of the same 'type' of equipment may exist. This specific strategy will for example make AI have 3 lines of Artillery AND 3 lines of Rocket Artillery AND 3 lines of Motorized Rocket Artillery. |
| equipment\_production\_min\_factories\_archetype | `value = <int>` The weight of the strategy.  `id = <equipment archetype>` The target of the strategy. | `ai_strategy = { type = equipment_production_min_factories_archetype id = artillery_equipment value = 4 }` | Pursues AI to keep a minimum amount of factories on the production lines for the equipment of the specified **archetype**. If multiple strategies are used at once, they stack. | A value of 1 corresponds to 1 military factory. Archetypes are defined in each file in /Hearts of Iron IV/common/units/equipment/\*.txt with `is_archetype = yes` argument. |
| <a id="equipment-variant-production-factor"></a> equipment\_variant\_production\_factor | `value = <int>` The weight of the strategy.  `id = <equipment archetype>` The target of the strategy. | `ai_strategy = { type = equipment_variant_production_factor id = light_tank_chassis value = -100 }` | Pursues AI to produce more of the specified equipment archetype. | Equipment archetypes are defined in /Hearts of Iron IV/common/units/equipment/\*.txt files. |
| <a id="equipment-stockpile-surplus-ratio"></a> equipment\_stockpile\_surplus\_ratio | `value = <int>` The weight of the strategy. | `ai_strategy = { type = equipment_stockpile_surplus_ratio value = 30 }` | Changes the ratio of equipment that AI would hold in stockpile rather than immediately using. |  |
| <a id="build-army"></a> build\_army | `value = <int>` The weight of the strategy.  `id = <unit role>` The target of the strategy. | `ai_strategy = { type = build_army id = infantry value = 200 }` | Modifies the desired division amount for AI. | The used target is roles within [AI templates](#ai-templates). This example would make the AI want exactly 200 divisions with 'infantry' role. |
| <a id="force-build-armies"></a> force\_build\_armies | `value = <int>` The weight of the strategy. | `ai_strategy = { type = force_build_armies value = 30 }` | Forces AI to build divisions above the desired amount. |  |
| <a id="production-upgrade-desire-offset"></a> production\_upgrade\_desire\_offset | `value = <int>` The weight of the strategy.  `id = <equipment type>` The target of the strategy. | `ai_strategy = { type = production_upgrade_desire_offset id = artillery_equipment_2 value = -50 }` | Pursues AI to upgrade production lines to the specified equipment type. | Equipment types are defined in /Hearts of Iron IV/common/units/equipment/\*.txt files. |
| <a id="role-ratio"></a> role\_ratio | `value = <int>` The weight of the strategy.  `id = <role>` The target of the strategy. | `ai_strategy = { type = role_ratio id = paratroopers value = 30 }` | Modifies the amount of templates that the AI makes for the specified role. | Roles are defined within [AI templates](#ai-templates) for unit templates and [AI equipment](#ai-equipment) for ship and tank variants. |
| <a id="unit-ratio"></a> unit\_ratio | `value = <int>` The weight of the strategy.  `id = <unit>` The target of the strategy. | `ai_strategy = { type = unit_ratio id = cas value = 30 }` | Modifies the amount of templates that the AI makes with the specified unit. | Units are defined in /Hearts of Iron IV/common/units/\*.txt files. This includes the airforce and navy alongside land army. |
| <a id="min-wanted-supply-trains"></a> min\_wanted\_supply\_trains | `value = <int>` The weight of the strategy. | `ai_strategy = { type = min_wanted_supply_trains value = 300 }` | Overrides the minimum amount of supply trains wanted by AI. |  |
| <a id="min-wanted-supply-trucks"></a> min\_wanted\_supply\_trucks | `value = <int>` The weight of the strategy. | `ai_strategy = { type = min_wanted_supply_trucks value = 30 }` | Overrides the minimum amount of supply trucks wanted by AI. |  |

Other AI strategies:
| Name | Parameters | Examples | Description | Notes |
| --- | --- | --- | --- | --- |
| <a id="scorched-earth-prio"></a> scorched\_earth\_prio | `value = <int>` The weight of the strategy.  `id = <country>` The owner of the states where to use scorched earth.  `states = { ... }`  List of states where to use scorched earth. | `ai_strategy = { type = scorched_earth_prio value = 100 id = ENG states = { 123 124 125 126 } }` | Pursues AI to use scorched earth within the specified states. |  |
| <a id="land-xp-spend-priority"></a> land\_xp\_spend\_priority | `value = <int>` The weight of the strategy.  `id = <type>` The target of the strategy. | `ai_strategy = { type = land_xp_spend_priority id = division_template value = 30 }` | Modifies the priority for AI to spend land experience. | Base game usages include `division_template` and `upgrade_xp_cutoff`. |
| <a id="pp-spend-amount"></a> pp\_spend\_amount | `value = <int>` The weight of the strategy.  `id = <type>` The target of the strategy. | `ai_strategy = { type = pp_spend_amount id = idea value = 100 }` | Modifies the political power that AI should preserve for the specified purpose. | Base game usages include `idea` and `decision`. |
| <a id="pp-spend-priority"></a> pp\_spend\_priority | `value = <int>` The weight of the strategy.  `id = <type>` The target of the strategy. | `ai_strategy = { type = pp_spend_priority id = relation value = 100 }` | Modifies where AI should prioritise spending political power. | Base game usages include the following:  - `admiral` - `guarantee` - `relation` - `decision` |
| <a id="research-weight-factor"></a> research\_weight\_factor | `value = <int>` The weight of the strategy.  `id = <type>` The target of the strategy. | `ai_strategy = { type = research_weight_factor id = radio_detection value = 2000 }` | Modifies the AI weight (score) of a specific technology. | value = 50 means 50% increase, -30 means 30% decrease, etc. |

## <a id="ai-areas"></a>AI areas

AI areas are defined within /Hearts of Iron IV/common/ai\_areas/\*.txt files. These are *only* used in a variety of previously-listed AI strategies, such as [area\_priority](#area-priority). A province may be in several AI areas and it may be in none. Hovering over a province with the debug mode turned on will provide information in which AI areas the province is, if any.

Each AI area is a separate block within the file, with the name of the block being the name of the area. Within these blocks, 2 things can be added:  
`continents = { ... }` is a list of continents that make up the AI area. Continents are defined within /Hearts of Iron IV/map/continent.txt and assigned to provinces within [their definitions](<Map modding - Hearts of Iron 4 Wiki.md#provinces>) in /Hearts of Iron IV/map/definition.csv. The full name of the continent should be used within the AI area's definition, rather than the ID used in the province definition.  
`strategic_regions = { ... }` is a list of strategic regions that make up the AI area, by their ID number.

If there are multiple defined, the province has to be in *any* of them.

An example of an AI area is the following:

```text
my_ai_area = {
    continents = {
        europe
        africa
    }
    strategic_regions = {
        53  # Caribbean
        189 # Burma
    }
}
```

## <a id="ai-focuses"></a>AI focuses

*Main article: [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>)*

AI focuses, defined within /Hearts of Iron IV/common/ai\_focuses/\*.txt files, are used to tell the game which technology categories and focuses the AI should pick depending on its currently-pursued focuses.

## <a id="ai-peace"></a>AI peace
| AI peace since 1.12 |
| --- |
| The peace conference behaviour for AI is defined within /Hearts of Iron IV/common/peace\_conference/ai\_peace/\*.txt files.  When defining the peace conference AI that would be used by the country, the AI will take into account all blocks for which the enable condition is true.  When evaluating the peace conference, `ROOT` (the default scope) is used to represent the currently-evaluated winner, `FROM` is the country which will undergo the selected peace action, this can be a previously non-existent country that will now be liberated or puppeted, or even a different winner country when liberating, finally `FROM.FROM.FROM` can be used to set conditions on the specific state that the peace action is taken on.  The `enable = { ... }` trigger block is used to determine whether the AI should be enabled, and finally an `ai_desire = ...` block determines the priority of the defined strategy: a value of -1000 would make AI never pursue the selected peace action if the conditions are met, while a value of 1000 would make the action their top priority.  The following peace options are used in the game:   - `liberate` - The country FROM gets liberated by ROOT. - `puppet` - The country FROM gets puppeted by ROOT. - `take_states` - The state FROM.FROM.FROM, previously owned by FROM, gets annexed by ROOT. - `force_government` - The country FROM gets its ideology forcefully changed by ROOT. - `take_navy` - No AI modding supported, cost modifiers can still be applied for players in games with ![By Blood Alone](media/ai-modding-hearts-of-iron-4-wiki_04cfcba22e__img12.png) By Blood Alone enabled.   When evaluating peace conferences, the controller of a given state is the same one that occupied it before the start of the conference while the owner is the original owner. Example: `peace_ai_desires = { dont_puppet_warlord_countries = { peace_action_type = { puppet liberate force_government } #all but take states enable = { FROM = { OR = { tag = SIK tag = PRC tag = GXC tag = YUN tag = SHX tag = XSM tag = MAN tag = MEN } } } ai_desire = -1000 } }` |
| Pre-1.12 AI peace |
| --- |
| The peace conference behaviour for AI is defined within /Hearts of Iron IV/common/ai\_peace/\*.txt files.  When defining the peace conference AI that would be used by the country, the game picks the first-defined one that meets the prerequisites. In this case, files are loaded sorted by their filename using [ASCII character IDs](http://en.wikipedia.org/wiki/ASCII#Printable_characters).  When evaluating the peace conference, ROOT (the default scope) is used to represent the currently-evaluated winner and FROM is used to represent the currently-evaluated loser. Additionally, the following temporary variables exist within:   - taken\_states@TAG is an array of states that are annexed by the country TAG as a part of the peace conference. - taken\_by@123 is the country that took the specified state, in this case 123. - current\_states@TAG is an array of states that aren't decided upon yet in the peace conference and are under the control of TAG that lost the war. - subject\_states@TAG is an array of states that are, within the peace conference, set to be transferred to countries that are subjected by TAG. - subject\_countries@TAG is an array of countries that are, within the peace conference, set to be subjected by TAG. - subjected\_by@123 is the overlord of the country that is set to have the specified state in the peace conference, in this case 123. - subjected\_by@TAG is an array of countries that have TAG as their overlord. - liberate\_states@TAG is an array of states that are going to countries that have been liberated by TAG. - liberate\_countries@TAG is an array of countries that have been liberated by TAG.   The `enable = { ... }` trigger block is used to determine whether the AI should be enabled. If true and no other previously-loaded peace conference AI is true, this AI will be chosen.  There are the following peace options that are used in the game:   - annex - The country FROM gets entirely annexed by ROOT. This only evaluates the countries. - liberate - The country FROM gets liberated by ROOT. - puppet - The country FROM gets puppeted by ROOT. - puppet\_all - The country FROM gets puppeted by ROOT *and* is able to retain all of its states. - puppet\_state - The state ROOT gets transferred to FROM.FROM, which became a subject of FROM within the peace conference. - take\_states - The state FROM gets annexed by ROOT. - force\_government - The country FROM gets its ideology forcefully changed by ROOT.   When evaluating peace conferences, the controller of a given state is the same one that occupied it before the start of the conference while the owner is the original owner.  Each peace conference option is a [MTTH block](#mtth-blocks) within the file's definition. Example: `my_peace_conference = { enable = { has_government = my_ideology_group } annex = { base = 500 modifier = { factor = 0 any_allied_country = { any_state = { is_owned_by = FROM is_core_of = PREV NOT = { is_core_of = ROOT is_claimed_by = ROOT } } } } } puppet = { base = 100 modifier = { factor = 0 FROM = { tag = QAT } } } puppet_all = { base = 0 } puppet_state = { base = 100 modifier = { factor = 0 FROM.FROM = { tag = QAT } } modifier = { factor = 0 any_allied_country = { ROOT = { is_core_of = PREV NOT = { is_core_of = FROM.FROM is_claimed_by = FROM.FROM } } } } } take_states = { base = 100 modifier = { factor = 0 any_allied_country = { FROM = { is_core_of = PREV NOT = { is_core_of = ROOT is_claimed_by = ROOT } } } } } }` |

## <a id="ai-strategy-plans"></a>AI strategy plans

AI strategy plans to tell AI what to prioritise depending on circumstances: which advisors to pick, which technologies to research, which AI strategies to apply, which focuses to pick, etc. These are more detailed than general AI strategies, primarily intended to be activated for most of the game to tell the overall plan of a country. Multiple AI strategy plans can be defined and executed at the same time for a country.

AI strategy plans are defined within /Hearts of Iron IV/common/ai\_strategy\_plans/\*.txt files. Within these files, a new strategy plan is done as a new block, the name of which must be the same as the internal ID of the plan.

Within that plan, `name = "AI plan's name"` and `desc = "AI plan's description"` decide the name and the description of the strategy plan. *This is never intended to be shown to the player*, so localising it into different languages is never needed. Instead, this is used within the `aiview` console command, which tells info to the developer about what AI wants to prioritise.

`allowed = { ... }` is, similarly to decisions or ideas, is a trigger block **checked only at the game's start**. This is primarily used to tell which country and DLCs to restrict the strategy plan to.

`enable = { ... }` is checked each day if the allowed is met. If `enable = { ... }` is met, then the AI strategy plan will be assigned to the AI regardless of whether `enable = { ... }` turns false later or not. Commonly, [Triggers#has\_game\_rule](<Triggers - Hearts of Iron 4 Wiki.md#has-game-rule>) is used to make it work with custom game rules deciding what path the AI will pick. [is\_historical\_focus\_on](<Triggers - Hearts of Iron 4 Wiki.md#is-historical-focus-on>) is commonly used with the default AI game rule, and country flags can be used for randomisation, by setting up an [on\_startup](<On actions - Hearts of Iron 4 Wiki.md>) to set a random one using [random\_list](<Scopes - Hearts of Iron 4 Wiki.md#random-list>)

`abort = { ... }` is checked every day in order to make the AI *stop* using this AI strategy plan if `enable = { ... }` is met. Additionally, it must be false in order for the AI strategy plan to be possible to be picked.

`ai_national_focuses = { TAG_focus_name_1 TAG_focus_name_2 }` is a list of national focuses, separated by whitespaces, in the order that the AI should take them. In this example, the AI will try to take TAG\_focus\_name\_1 first if possible. If it's already taken or TAG\_focus\_name\_1 is impossible to take, then AI will try to take TAG\_focus\_name\_2. If both of the focuses are impossible to take due to being completed or unavailable, then it will move on to other focuses, taking `ai_will_do = { ... }` into consideration. While following a focus order, it ignores `ai_will_do = { ... }` values.

`focus_factors = { ... }` assigns a multiplier to ai\_will\_do values of the specified focus. An entry in this block looks like `TAG_focus_name = 3`. In this case, this will make the ai\_will\_do value of the focus be multiplied by 3, assuming AI strategy plan's weight of 1. If the focus has an ai\_will\_do value of 4 after applying modifiers, it'll become 12 if AI is following this strategy plan, and get treated as such. And, of course, a factor of 0 will make the focus be never picked without specification in ai\_national\_focuses. This can serve as a faster-to-write or a more randomised way to make AI follow a political path by making focuses it should never pick have a value of 0.

`research = { ... }` assigns a multiplier to ai\_will\_do values of the specified research categories. An entry in this block looks like `artillery = 3`. In this case, this will make the ai\_will\_do value of every technology within the category be multiplied by 3, assuming AI strategy plan's weight of 1. Other built-in modifiers still apply, but this will increase the likelihood.

Other blocks that also assign bonuses are `ideas = { ... }` and `traits = { ... }`, with the similar formatting. The ideas block is used for individual ideas (such as laws or designers) or advisors (using the idea\_token in the entry), while traits are for country leader traits that are assigned to the ideas/advisors.

`ai_strategy = { ... }` allows an [AI strategy](#ai-strategies) to apply when the strategy plan is turned on.

`weight = { ... }` is a [MTTH block](#mtth-blocks) assigning an overall weight to the plan. This multiplies each factor within the AI strategy plan by the weight before applying them. A weight of 1.25 will turn a focus factor of 4 into 5 before applying it, for instance. This can be used to make the AI follow the strategy plan more strictly in some cases and less strictly in others.

### <a id="example_2"></a>Example

```text
BHR_historical = {
    name = "Historical plan for BHR"
    desc = "4 focuses in a specific order"
    allowed = {
        tag = BHR
    }
    enable = {
        OR = {
            AND = {
                is_historical_focus_on = yes
                has_game_rule = {
                    rule = BHR_ai_behavior
                    option = DEFAULT
                }
            }
            has_country_flag = BHR_AI_RANDOM_HISTORICAL # Randomly set in on_actions if BHR_ai_behavior is set to RANDOM. Make sure to set that up!
            has_game_rule = {
                rule = BHR_ai_behavior
                option = HISTORICAL
            }
        }
    }
    abort = {
        OMA = {
            OR = {
                has_government = fascism
                has_government = communism
            }
        }
    }
    ai_national_focuses = {
        BHR_focus_name_1
        BHR_focus_name_2
        BHR_focus_name_3
        BHR_focus_name_4
    }
    ideas = {
        BHR_advisor = 3
    }
    traits = {
        fascist_demagouge = 0
    }
    ai_strategy = {
        type = invade
        id = OMA
        value = 200
    }
}
BHR_alternate = {
    name = "Alternative plan for BHR"
    desc = "AI is just set to never do BHR_focus_name_2 and be more likely to do BHR_focus_name_5, especially if after 1937"
    enable = {
        OR = {
            has_country_flag = BHR_AI_RANDOM_ALTERNATE # Randomly set in on_actions if BHR_ai_behavior is set to RANDOM. Make sure to set that up!
            has_game_rule = {
                rule = BHR_ai_behavior
                option = ALTERNATE
            }
        }
    }
    focus_factors = {
        BHR_focus_name_2 = 0
        BHR_focus_name_5 = 2
    }
    weight = {
        modifier = {
            factor = 2
            date > 1937.1.1
        }
    }
    research = {
        artillery = 2
    }
}
```

## <a id="ai-templates"></a>AI templates

Scripters/modders are able to specify so called "target templates" that the AI try to reach when upgrading division templates.

Target templates are defined on a "role" level, and it's possible to define a number of different target templates for a specific role. The AI then chooses one of those target templates (based on scripted priorities) and aims for that.

For each role, the AI will select one target template based on the `prio`, `enable`, and `replace_with` parameters. This is referred to as the "currently targeted template".

The AI will then compare the existing division templates it has to find which one best matches the targeted template. This is referred to as the "best match" and the "match score"/"match" refers to how well it matches (100 % match = 1.0).

When the AI decides to upgrade a division template, it will make a copy of the best matching template and modify it so it gets a higher match score (i.e. looks more like the target template). (Note that the AI actually never does in-place modification of templates, it just makes a copy and modifies the copy instead.)

The AI strategy `role\_ratio` determines how many divisions the AI wants for each role.

Role arguments:

- `role =` the role token that this role-level template entry targets. These tokens are defined by script and are targeted by the 'role\_ratio' AI strategy.
- `blocked_for = { ... }` Determines which countries will use this role-level template entry. Both 'blocked\_for' and 'available\_for' are possible to use. Use one or the other, if you use neither or both, the resulting behavior is undefined. Generally you want to make sure that each country has max one role-level template entry targeting a role. So if you add custom AI templates for e.g. Germany you should make sure that only Germany is allowed for it, and you should also block Germany from using the generic AI templates for the same role.
- `upgrade_prio = { ... }` An MTTH style block used for weighted-random selection when the AI chooses which role to upgrade templates for. Set it to zero to prevent the AI from spending XP on upgrading templates for this role. Example: If three role-level templates [A, B, C] have upgrade prio [1, 2, 1] respectively, then the probabilities for upgrading each template is [25%, 50%, 25%] respectively.
- `enable = { ... }` Optional: Whether to evaluate this target template at all. Trigger with country scope. If false, the AI will pretend this target template doesn't exist.

Target template arguments:

- `reinforce_prio =` Optional: Determines the reinforcement prio of the resulting template. For example, garrison templates should use 0 (low prio) while elite templates should use 2 (high prio). Default 1 (normal prio).
- `custom_icon =` Optional: Determines whether to use a custom icon for resulting template.
- `division_names_group =` Optional: Specifies the division name group to use. By default uses the name group of the template "branched off" from.
- `upgrade_prio = { ... }` The priority of this target template. This is used to determine (deterministically, no randomness involved) which of the target templates is the "currently targeted template".
- `enable = { ... }` Optional: Whether to evaluate this target template at all. Trigger with country scope. If false, the AI will pretend this target template doesn't exist.
- `can_upgrade_in_field = { ... }` Optional: Whether to allow upgrading divisions in the field. Trigger with country scope. If false, the AI will not field-upgrade divisions matching this target template. If true, the AI will consider field-upgrading divisions matching this target template to the target template defined by 'replace\_with' (assuming they have enough manpower and equipment for it).
- `target_template = { ... }` The "meat" of the target template: the actual template contents.
  - `support = { ... }` The desired support companies. The AI will try to add them to the template if allowed by research etc.
  - `regiments = { ... }` The desired line regiments. The AI will try to add them to the template if allowed by research etc.

In addition, the optional replace-with chain. If the match score is at least 'replace\_at\_match', then replace the currently targeted template with 'replace\_with', as long as the match score between best matching template and the next target template is at least 'target\_min\_match':

- `replace_at_match =` Optional: Match score of this target template.
- `replace_with =` Optional: Other target template to replace currently targeted template with. Also affects fielded divisions when upgrading in the field.
- `target_min_match =` Optional: Match score between the best matching template and the target template defined by 'replace\_with' has to be at least this high in order for the switch to happen.

### <a id="example_3"></a>Example

```text
infantry_generic = {
    blocked_for = {
        GER
        JAP
    }

    role = infantry

    upgrade_prio = {
        factor = 1

        modifier = {
            factor = 5
        }
    }

    # In this example, the AI will first try to reach a 6-inf (+support) template, before upgrading it to a 9-inf 2-arty (+support) template.
    # Since the 'upgrade_prio' is higher for the first template, that one will be targeted. And when the match score is good enough it will use the 'replace_with' to switch over to the larger template.
    # If two target templates have the same 'upgrade_prio', the first one will be preferred (so order matters in those cases).

    # Target template 1 (the smaller infantry template)
    infantry_1 = {
        reinforce_prio = 0
        custom_icon = 7
        division_names_group = GER_MEC_01

        upgrade_prio = {
            factor = 1

            modifier = {
                factor = 1.5
            }
        }

        enable = {
            date < 1940.3.14
        }

        can_upgrade_in_field = {
            has_equipment = { infantry_equipment > 3000 }
        }

        target_template = {
            support = {
                engineer = 1
                anti_air = 1
                artillery = 1
            }
            regiments = {
                infantry = 6
            }
        }

        replace_at_match = 0.9
        replace_with = infantry_2
        target_min_match = 0.9
    }

    # Target template 2 (the larger infantry template)
    infantry_2 = {
        upgrade_prio = {
            factor = 1

            modifier = {
                factor = 1
            }
        }

        target_template = {

            support = {
                engineer = 1
                recon = 1
                field_hospital = 1
                anti_air = 1
                anti_tank = 1
            }

            regiments = {
                infantry = 9
                artillery_brigade = 2
            }
        }
    }
}
```

## <a id="ai-equipment"></a>AI equipment

/Hearts of Iron IV/common/ai\_equipment/\*.txt files are used in order to define the equipment variants that the AI should aim for when assigning modules to tank or ship variants.

A role template is defined as a block within any file in the folder with the name of the block being the same as the name of the role template.  
These arguments are used for role templates themselves:

- `category = <land|naval|air>` decides whether the template is used for tanks, ships or planes respectively.
- `roles = { ... }` is a list of roles that the templates would have. These can be anything, getting used for the [role\_ratio AI strategy](#role-ratio). AI will try to have one variant for each role it has.
- `available_for = { ... }` restricts the countries that use this role template to the tags in the list. If unspecified, every country uses them.
- `blocked_for = { ... }` restricts the countries that use this role template from being the tags in the list. This is only needed if there is no `available_for = { ... }` block.
- `priority = { ... }` is a [MTTH block](#mtth-blocks) that decides the 'importance' of the role template compared to other role templates for spending experience on improving. If there are several role templates with the same roles, the one with the highest priority gets used, otherwise this decides likelihood compared to role templates with different roles.

Additionally, within role templates each individual design is defined as a block with the name of the design being the name of the block. It may be anything, as long as there is no overlap.  
These arguments are used within a design definition:

- `name = angry_speedboat` required to enable the equipment to be used as preset. If not defined, for example German `light_tank_artillery_2` will use `GER_light_tank_artillery_equipment_2_short` localization if defined.
- `role_icon_index = 2` is used to assign a specific role icon to a *ship*. This does not work within land equipment. The icons are defined as a part of `naval_equipment_role = { ... }` within /Hearts of Iron IV/gfx/army\_icons/army\_icons.txt.
- `priority = { ... }` is a [MTTH block](#mtth-blocks) that decides the 'importance' of the design compared to other templates within the role template for spending experience on improving.
- `enable = { ... }` is a trigger block that decides when AI should aim towards the design.
- `allowed_types = { ... }` is a list of sub-units that the AI can add to the design. If one is omitted, then the AI would never add it. This can be used to make AI not put units of different varieties in the design, such as putting infantry in a mobile light tank division, slowing it down.
- `target_variant = { ... }` assigns the variant that AI should aim for. In particular, these arguments go inside of it:
  - `match_value = 5000` is a value that decides how much the template is worth to AI if it's matched.
  - `type = light_tank_chassis_0` is the specific equipment type that must be used by the design.
  - `modules = { ... }` is a list of modules that the equipment should have, in particular:
    - `main_armament_slot = tank_flamethrower` decides requirements for a specified module slot, in first place. The requirement may be a module category, a specific module, or the word `empty`. If specifying a module, the greater-than or lesser-than signs can be used in order to require greater or lesser modules: this is decided by the year defined within the module. If lesser is specified, AI aims towards oldest modules, if greater is specified, AI aims towards newest modules. If specifying empty, greater than can be used to ensure it's *not* empty.
    - `main_armament_slot = { ... }` allows specifying more details for a module slot:
      - `module = tank_flamethrower` decides a module requirement for the slot. This is the exact same formatting as previous `main_armament_slot = tank_flamethrower`: module categories, modules, or empty are allowed, and the equality signs can be used in the same way.
      - `any_of = { ... }` is a list of modules or module categories. The module slot must have at least one of them.
      - `upgrade = current` ensures that, when upgrading a variant to match this design, it must use the same one as on the existing equipment. If the 'greater than' sign is used (>), then it would require AI to upgrade this slot as well.
  - `upgrades = { ... }` is a list of upgrades that the design should have, in particular:
    - `tank_nsb_engine_upgrade = 3` decides the AI priority that the specified upgrade should have to a fixed number.
    - `tank_nsb_engine_upgrade = { ... }` is a [MTTH block](#mtth-blocks) that assigns the AI priority to the specified upgrade dynamically.
- `requirements = { ... }` is a list of modules that the AI *must* have. This follows the same formatting as a specified module slot within a target variant's modules block: `module = tank_flamethrower`, `any_of = { ... }`, etc. However, this is not tied to a specific slot.
- `allowed_modules = { ... }` is a list of modules that the AI can use after the requirements in the target variant are met. If a module isn't here, it'll never be picked. The modules specified first take priority over the later ones.

### <a id="example_4"></a>Example

```text
BHR_light_tanks = {
    category = land

    available_for = {BHR}

    roles = {
        land_light_tank
    }

    priority = {
        factor = 1000
    }

    great_war_tank_default = {
        priority = {
            factor = 1
            modifier = {
                has_tech = basic_light_tank_chassis
                factor = 0 #let's not waste XP here
            }
        }

        target_variant = {
            match_value = 1000
            type = light_tank_chassis_0
            modules = {
                main_armament_slot = tank_heavy_machine_gun
                turret_type_slot = tank_light_one_man_tank_turret
                suspension_type_slot = tank_bogie_suspension
                armor_type_slot = tank_riveted_armor
                engine_type_slot = tank_gasoline_engine
                special_type_slot_1 = empty
                special_type_slot_2 = empty
                special_type_slot_3 = empty
                special_type_slot_4 = empty
            }
            upgrades = {
                tank_nsb_engine_upgrade = 3
                tank_nsb_armor_upgrade = {
                    base = 1
                    modifier = {
                        add = 1
                        has_war = yes
                    }
                }
            }
        }

        allowed_modules = {
            tank_heavy_machine_gun
            tank_light_one_man_tank_turret
            tank_bogie_suspension
            tank_riveted_armor
            tank_gasoline_engine
        }
    }
}
```

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
