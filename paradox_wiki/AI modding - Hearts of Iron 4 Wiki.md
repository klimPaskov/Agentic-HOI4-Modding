# AI modding

*Offline snapshot of the Hearts of Iron IV Wiki page "AI modding", revision 105110, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="105110" sources="common/ai_strategy/ common/ai_strategy_plans/ common/ai_areas/ common/ai_focuses/ common/ai_templates/ common/ai_equipment/ common/ai_navy/ common/ai_faction_theaters/ common/peace_conference/ai_peace/ common/factions/_documentation.md common/defines/00_defines.lua documentation/triggers_documentation.md documentation/modifiers_documentation.md documentation/console_commands_documentation.md documentation/dynamic_variables_documentation.md documentation/effects_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: every `_documentation.md` of the AI folders (strategy, templates, equipment, navy, taskforce, faction theaters, peace) and the vanilla files of each folder, counted by script.
- Kit blocks added: strategy file keys, 31 documented strategy tokens the page lacked, 9 vanilla-only tokens, unit ratio rules, AI areas wrapper, peace corrections (including `take_navy`), strategy plan facts and fixes, template and equipment additions, and bottom sections for AI navy, task forces, faction theaters and the documented AI triggers, modifiers and console commands.
- Errors found: `take_navy` is not a peace action type and the pre-1.12 `common/ai_peace/` folder is gone; the "outdated" pointer to `documentation.info` leads nowhere (`_documentation.md` is the real list); `FORCE_CONCENTRATION_UNIT_RATIO_BASE` is `NAI.AIFC_UNIT_RATIO_BASE`; the plan example trait `fascist_demagouge` is `fascist_demagogue`; the AI areas example lacks the `areas = { }` wrapper; `allowed_types` is in neither the docs nor vanilla.
- Gaps left: meaning of `template_prio`, `save_equipment`, `ai_wanted_divisions_factor` and the other tokens the documentation lists without a description is unverified; peace `ai_desire` scale is covered on the Peace conference page.
<!-- kit:end id="review" -->

## Table of contents

- [MTTH blocks](#MTTH_blocks)
  - [Example](#Example)
- [AI strategies](#AI_strategies)
  - [Arguments](#Arguments)
  - [Types](#Types)
- [AI areas](#AI_areas)
- [AI focuses](#AI_focuses)
- [AI peace](#AI_peace)
- [AI strategy plans](#AI_strategy_plans)
  - [Example](#Example_2)
- [AI templates](#AI_templates)
  - [Example](#Example_3)
- [AI equipment](#AI_equipment)
  - [Example](#Example_4)
- [Kit: AI navy goals, fleets and task forces](#kit-ai-navy)
- [Kit: AI faction theaters](#kit-ai-faction-theaters)
- [Kit: Documented AI script surface](#kit-ai-docs-surface)

---

The artificial intelligence controlling countries in Hearts of Iron IV can be changed in many different aspects. This includes changing the focuses or technologies it pursues, changing how many units or buildings it should produce and of which type, where it should focus forces, which templates or variants it should aim for, and so on.

## MTTH blocks <a id="MTTH_blocks"></a>

MTTH blocks, named in the game within `/Hearts of Iron IV/common/mtth/`, are a way to assign a dynamic value to some block, whether it's a [country = { ... } in a focus tree to assign which countries can get it](<National focus modding - Hearts of Iron 4 Wiki.md#Focus_tree>), a dynamically-changing variable value (as in `/Hearts of Iron IV/common/mtth/`), a [mean-time-to-happen value for an event](<Event modding - Hearts of Iron 4 Wiki.md#Triggering>), et cetera. As MTTH blocks are spread throughout the entire game, it's incredibly important to know how one works. Its most common application, however, is assigning a base AI weight to a database entry such as a national focus or a technology.

In most cases, marked with ai_will_do, the approach taken by the game is generating a decimal number between 0 and the value of the ai_will_do block, and picking the entry with the highest value. There can be other modifiers applied after the ai_will_do value, such as the ones applied within [AI strategy plans](#AI_strategy_plans) towards focuses and research or the ones that get defined within [Defines](<Defines - Hearts of Iron 4 Wiki.md>), which'll multiply the value you get. This can include different ai_will_do values such as what's done with country leader traits and with ideas or characters that use them.
Event options, instead, use ai_chance, which uses probability-proportional-to-size sampling with a virtual roll of d00 being the final deciding factor. Due to that, in the end, an event option cannot have a probability which isn't a multiple of 1/100 to be picked, although the total sum of each option's weights can be vastly different from 100. In other words, if one option has a value of 1, while the other has a value of 999, the probability for the first option to be picked will be 1% rather than 0.1%.

A MTTH block begins with an assumed value of 1. Further manipulations are done from that value as a starting point. There are 3 value-modifying arguments that can be done, `add`, `base`, and `factor`, done like `factor = 0.3`, `base = 10`, or `add = 5`. `add` adds the specified argument to the value, `factor` *multiplies* it, and `base`, typically done in the start before any changes, sets it to a different number entirely, akin to multiplying by 0 and adding the number.
In order for an operation to apply conditionally, a `modifier = { ... }` block is used. This also functions as a [trigger block](<Triggers - Hearts of Iron 4 Wiki.md>), with the default scope (thus also ROOT) being the country for which the MTTH block is evaluated. Depending on the MTTH block, [there may be additional scopes marked with FROM](<Decision modding - Hearts of Iron 4 Wiki.md#Targeted_decisions>) [or FROM.FROM other than the default.](#AI_peace) The value-modifying arguments function as regular arguments, they can be put in anywhere directly within the `modifier = { ... }` block with almost no difference, whether it's in the end, the beginning, or between triggers.

[Variables](<Data structures - Hearts of Iron 4 Wiki.md>) can be used within the value-modifying arguments as well. If using a temporary variable that is defined within the `modifier = { ... }` trigger block, then the value-modifying argument of the modifier has to be after the definition of the variable in order for the variable to apply as defined. Variables can also be used outside of the `modifier = { ... }` block and directly inside of the MTTH block itself.

### Example <a id="Example"></a>

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

- 0 for GER: `10.5\cdot 0=0`
- 74 for FRA: `((10.5+1)\cdot 3+2.5)\cdot 2=74`
- 23 for other majors: `(10.5+1)\cdot 2=23`
- 21 for minors: `10.5\cdot 2=21`

After calculating that value, the total number of civilian and military factories within the country, divided by 10 and rounded, will get added to the score. If FRA has a total of 43 civilian and military factories as it does in base game, then this will result in 4 being added to the prior 74 for a total of 78, for example.

## AI strategies <a id="AI_strategies"></a>

AI strategies are used in order to pursue AI to do or avoid something. This includes diplomatic actions the AI will do, where and how exactly AI should focus and use its land army and the navy, the production lines for buildings and equipment, how AI should handle the intelligence system within the ![La Résistance](media/ai-modding-hearts-of-iron-4-wiki_04cfcba22e__img6.png)La Résistance DLC.
A value within an AI strategy can be either positive or negative, and it being negative will make AI desire to do it less.

Regular AI strategies are stored in `/Hearts of Iron IV/common/ai_strategy/*.txt` files, however, AI strategies may be defined outside of that file. The [add_ai_strategy effect](<Effects - Hearts of Iron 4 Wiki.md>) can add a permament AI strategy within any effect block, and [AI strategy plans](#AI_strategy_plans) can also include AI strategies defined within of themselves. Overall, `/Hearts of Iron IV/common/ai_strategy/*.txt` files describe AI strategies that would enable and disable themselves automatically.
Each entry within a `/Hearts of Iron IV/common/ai_strategy/*.txt` file is a block with the name of the AI strategy. This name can be anything, even allowing overlap between them: this will only appear in AI dumps and the player will never see it. If an AI strategy modifies the chance for AI to pick a diplomatic option with the player, it will be seen as `COUNTRY has strategic reasons to be ...` to the player when hovering over the option. This is an example of an AI strategy with the name of BHR_invade_qatar:

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

### Arguments <a id="Arguments"></a>

These in particular are arguments for `/Hearts of Iron IV/common/ai_strategy/*.txt` entries, rather for AI strategy entries within them.

`allowed = { ... }` is a trigger block that's **checked only before the game's start**, permamently allowing or disallowing an AI strategy. Typically, only used for country checks (such as `tag = OMA`) or DLC checks that can never be unfulfilled once they are met.

`enable = { ... }` is a trigger block that must be met in order to enable the AI strategy. By default, this being unmet will *not* cancel the AI strategy. However, `abort_when_not_enabled = yes` can be used as a separate argument in order to make that be no longer the case. Unlike allowed, this is checked continuously.

`abort = { ... }` is a trigger block that must be met in order to *remove* the AI strategy. It being unmet also prevents it from being added in the first place.

`ai_strategy = { ... }` is, itself, the AI strategy that would be applied. The only argument shared for every AI strategy is `type = <AI strategy type>`. [The rest depends on the AI strategy](#Types).

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

Without `reversed = yes`, this would make every ![Neutrality](media/ai-modding-hearts-of-iron-4-wiki_25696e0a81__img2.png)non-aligned country support BHR. Due to that argument, the strategy is reversed: instead, BHR supports every ![Neutrality](media/ai-modding-hearts-of-iron-4-wiki_25696e0a81__img2.png)non-aligned country.

<!-- kit:begin id="ai-strategy-file-keys" at="section:Arguments" -->
**Kit note** Facts about `common/ai_strategy/` in 1.19.3. All lines: [vanilla-confirmed 1.19.3] `common/ai_strategy/*.txt`, counted by script, unless tagged [docs] `common/ai_strategy/_documentation.md`.

- 925 strategy blocks in 49 files: `default.txt`, `doctrines.txt`, `operatives_default.txt`, `generic_operation_strats.txt`, three `*_operation_strats.txt` files and one file per country. Keys at the top of a block: `enable` (925), `allowed` (796), `abort_when_not_enabled` (553), `abort` (379), `reversed` (9), `enable_reverse` (4), and `ai_strategy` (2617 entries in all).
- The documentation asks for either `abort` or `abort_when_not_enabled` in every block, and says to write `abort = { always = no }` for a strategy that should never end. It calls `allowed` a first-step filter that should avoid expensive triggers. [docs]
- Entry keys vanilla uses besides `type`, `id` and `value`: `target` (145), `ratio` (132), `state` and `states`, `area`, `tag`, `strategic_region`, `ordertype`, `execution_type`, `priority`, `execute_order`, `manual_attack`, `target_country` (21), `mission`, `mission_target`, `operation`, `operation_target`, `equipment_type`, `seller`, `num_operatives`, `country_trigger`, `state_trigger`, `order_id`, `subtract_invasions_from_need` and `subtract_fronts_from_need`.
- `add_ai_strategy` is a country effect with the same block as an entry: `add_ai_strategy = { type = contain id = "SOV" value = -800 }` (`common/scripted_effects/00_scripted_effects.txt`). [docs] `documentation/effects_documentation.md` (one-line description).
- The `BHR_*` strategy names on this page (`BHR_invade_qatar`, `BHR_support_neutrals`) and `BHR_ai_behavior` are invented examples. Real ids follow `<TAG>_ai_behavior`, see the game rule notes on [Bookmark modding](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules_2>).
<!-- kit:end id="ai-strategy-file-keys" -->

### Types <a id="Types"></a>

<!-- kit:begin id="ai-types-doc-pointer" at="heading:Types" -->
**Kit correction** The file named in the next paragraph, `common/ai_strategy/documentation.info`, does not exist in 1.19.3. The folder holds `common/ai_strategy/_documentation.md`, headed "updated 2024-11", with 104 strategy tokens in seven groups (diplomacy, fronts and armies, navies, intelligence, production and resources, airforce, raids). This page's tables list 73 of them. The block `ai-types-missing` after the tables lists the 31 it lacks, and `ai-types-vanilla-only` adds the 9 types that vanilla uses without the documentation listing them. [docs] `common/ai_strategy/_documentation.md`; [vanilla-confirmed 1.19.3] folder listing of `common/ai_strategy/`.
<!-- kit:end id="ai-types-doc-pointer" -->

This list may be outdated. A list of every AI strategy can be found within base game's `/Hearts of Iron IV/common/ai_strategy/documentation.info` file.

AI strategies related to diplomatic actions:

| Name | Parameters | Examples | Description | Notes |
| --- | --- | --- | --- | --- |
| alliance | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to ally with a country, joining the same faction if possible. |  |
| antagonize | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to antagonize a country, refusing most diplomatic actions with them. |  |
| asking_foreign_garrison | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to ask for foreign manpower to fulfill garrisons, from a specific country if specified. | If `id` is not specified, will apply towards every other country. |
| befriend | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to befriend a country, accepting most diplomatic actions with them. |  |
| conquer | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to conquer a country, being more likely to declare war and justify wargoals. | This does *not* change how the AI will control frontlines when at war with that country. |
| consider_weak | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to consider a country more weak, decreasing hesitation for declaration of war or making alliance less likely. |  |
| contain | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to contain a country, protecting any countries that it would try to antagonize or invade. |  |
| declare_war | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to declare war on a country if a wargoal already exists. |  |
| diplo_action_acceptance | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy.<br> `target = <diplomatic action>`<br>The diplomatic action to modify. | *(example below)* | Pursues AI to accept a diplomatic action if a different country requests it. | AI will not be more likely to propose the diplomatic action in question. Names of diplomatic actions can usually be found from localisation keys used for the title, most of the time yet not always in the `/Hearts of Iron IV/localisation/english/diplomacy_l_english.yml` file: `DIPLOMACY_SEND_VOLUNTEERS_TITLE:0 "Send Volunteers"` means that the name of the diplomatic action for sending volunteers is `send_volunteers`. |
| diplo_action_desire | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy.<br> `target = <diplomatic action>`<br>The diplomatic action to modify. | *(example below)* | Pursues AI to request a diplomatic action towards the specified country. | AI will not be more likely to accept the diplomatic action in question if it gets proposed to them. Names of diplomatic actions can usually be found from localisation keys used for the title, most of the time yet not always in the `/Hearts of Iron IV/localisation/english/diplomacy_l_english.yml` file: `DIPLOMACY_SEND_VOLUNTEERS_TITLE:0 "Send Volunteers"` means that the name of the diplomatic action for sending volunteers is `send_volunteers`. |
| dont_join_wars_with | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy.<br> `target_country = <country>`<br>The country against whom the war is joined. | *(example below)* | Pursues AI to be less likely to join a war together with a specified country against a specific one. | Does not make AI less likely to join a war together with a *different* country against target_country, even if it'll result in fighting against target_country together with the specified country. |
| ignore | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to be less likely to accept or desire any sort of diplomatic action with this country. |  |
| ignore_claim | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to ignore any claims that it has on the specified country. | The value is boolean, just set to be 1. |
| protect | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to protect a certain country, guaranteeing them or adding to the same faction. | A negative total value (taking every AI strategy into consideration) results in AI never guaranteeing that country. |
| support | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to support a certain country within wars, sending lend lease, volunteers, or expeditionary forces. |  |
| send_lend_lease_desire | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to lend-lease equipment to the specified country. |  |
| send_volunteers_desire | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to send volunteers to the specified country. |  |

**Example: alliance**

```text
ai_strategy = {
    type = alliance
    id = USA
    value = -100
}
```

**Example: antagonize**

```text
ai_strategy = {
    type = antagonize
    id = USA
    value = -100
}
```

**Example: asking_foreign_garrison**

```text
ai_strategy = {
    type = asking_foreign_garrison
    id = USA
    value = 100
}
```

**Example: befriend**

```text
ai_strategy = {
    type = befriend
    id = USA
    value = 100
}
```

**Example: conquer**

```text
ai_strategy = {
    type = conquer
    id = USA
    value = 100
}
```

**Example: consider_weak**

```text
ai_strategy = {
    type = consider_weak
    id = USA
    value = 100
}
```

**Example: contain**

```text
ai_strategy = {
    type = contain
    id = USA
    value = 100
}
```

**Example: declare_war**

```text
ai_strategy = {
    type = declare_war
    id = USA
    value = 100
}
```

**Example: diplo_action_acceptance**

```text
ai_strategy = {
    type = diplo_action_acceptance
    id = USA
    value = 100
    target = join_allies
}
```

**Example: diplo_action_desire**

```text
ai_strategy = {
    type = diplo_action_desire
    id = USA
    value = 100
    target = call_allies
}
```

**Example: dont_join_wars_with**

```text
ai_strategy = {
    type = dont_join_wars_with
    id = USA
    value = 100
    target_country = BHR
}
```

**Example: ignore**

```text
ai_strategy = {
    type = ignore
    id = USA
    value = 100
}
```

**Example: ignore_claim**

```text
ai_strategy = {
    type = ignore_claim
    id = USA
    value = 1
}
```

**Example: protect**

```text
ai_strategy = {
    type = protect
    id = USA
    value = 100
}
```

**Example: support**

```text
ai_strategy = {
    type = support
    id = USA
    value = 100
}
```

**Example: send_lend_lease_desire**

```text
ai_strategy = {
    type = send_lend_lease_desire
    id = USA
    value = 100
}
```

**Example: send_volunteers_desire**

```text
ai_strategy = {
    type = send_volunteers_desire
    id = USA
    value = 100
}
```

AI strategies related to land army management:

| Name | Parameters | Examples | Description | Notes |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| invade | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to do naval invasions against the specified country. |  |  |  |  |  |
| naval_invasion_focus | `value = <int>`<br>The weight of the strategy. | *(example below)* | Pursues AI to launch naval invasions. |  |  |  |  |  |
| prepare_for_war | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to prepare for a war against a specified country, moving troops to their border. |  |  |  |  |  |
| area_priority | `value = <int>`<br>The weight of the strategy.<br> `id = <AI area>`<br>The [AI area](#AI_areas) to prioritise. | *(example below)* | Pursues AI to put more units within the specified AI area. |  |  |  |  |  |
| strategic_air_importance | `id = <strategic_region>`<br>The strategic region to consider `value = <int>`<br>The score added or substracted.<br> | *(example below)* | Modifies the total 'Strategic Importance' score of the specified region that the AI uses to prioritize where to perform Air Missions. | - ID of the strategic regions can be found here, in `/Hearts of Iron IV/map/strategicregions/*.txt` files, or alternatively in the game using [console command](<Console commands - Hearts of Iron 4 Wiki.md>) *tdebug* and hovering a mouse over the specific region while in the 'Default' map mode. - Current 'Strategic Importance' AI score can be found in the game using [console command](<Console commands - Hearts of Iron 4 Wiki.md>) *aiview* , while in the 'observe mode' and hovering a mouse over the desired air zone, while using the 'Strategic Air' map mode. The score shown is for the currently selected TAG. AI wants to do air missions in the regions with the highest scores, and none in the regions with low or negative score. - AI score numbers are large, in higher dozens of thousands or lower hundreds of thousands, so appropriate values need to be used to have any visible effect on the AI. |  |  |  |  |
| dont_defend_ally_borders | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Makes AI never put troops on the border between the specified country and countries that are at war with it. | Strictly binary. If the total value (taking every AI strategy into consideration) is positive, AI will never put any troops on the border. |  |  |  |  |
| force_defend_ally_borders | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to put troops on the border between the specified country and countries that are at war with it. | Also accepts [AI areas](#AI_areas) within `id`. |  |  |  |  |
| front_armor_score | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The target of the strategy. | *(example below)* | Pursues AI to put more tank units for invading the specified country. |  |  |  |  |  |
| front_control | `state = <state>`<br>The state to target.<br> `tag = <country>`<br>The country to target.<br> `strategic_region = <ID>`<br>The strategic region to target.<br> `area = <area>`<br>The [AI area](#AI_areas) to target.<br> `country_trigger = { ... }`<br>Trigger block checked for states to have them as a target.<br> `state_trigger = { ... }`<br>Trigger block checked for countries to have them as a target.  `ratio = <decimal>`<br>How much of a frontline ratio the specified front must have **as a requirement to enable the strategy**. Defaults to 0.<br> `priority = <integer>`<br>Sets the priority of this front control strategy. If there are contradictory front control strategies, the one with a higher priority is followed.<br> `ordertype = <front | invasion>`<br>If set, this will make the AI strategy only apply on land frontlines or naval invasions respectively.<br> `execution_type = <careful | balanced | rush | rush_weak>`<br>If set, this pursues AI to make the frontline plans have the set execution type. Only for front.<br> `execute_order = <bool>`<br>If set, makes AI to either force execute the frontline order or force it being never executed.<br> `manual_attack = <bool>`<br>If set to false, prevents AI from doing small engagements that are not a part of a frontline plan. Defaults to true, only for front. | *(example below)* *(example below)* | Modifies the orders that AI would give to divisions on a specified frontline. | More than one target type can be used at a time, in which case each one must be met. This only changes the orders assigned to an already-existing frontline, this will not change the amount of units assigned to any particular front or force any to be created. |
| force_concentration_front_factor | `tag = <country>`<br>The country to target. Multiple can be specified. `state = <state>`<br>The state to target. Multiple can be specified.<br>`strategic_region = <ID>`<br>The strategic region to target. Multiple can be specified.<br>`area = <area>`<br>The [AI area](#AI_areas) to target. Multiple can be specified.<br>`country_trigger = { ... }`<br>Trigger block checked for countries. Scope is enemy country, FROM scope is our country.<br>`state_trigger = { ... }`<br>Trigger block checked for states.  Scope is state. FROM scope is enemy country FROM.FROM scope is our country.  `ratio = <decimal>`<br>The strategy is enabled only if ratio of the front covered by this strategy's targets is greater than this ratio.<br>`value = <int>`<br>Factor for the normal priority. 40 means +40 %, -60 means -60 %. | *(example below)* | Used for increasing/decreasing priority score for AI force concentration on specified fronts. | All the arguments are optional, only one needs to be specified. AI primarily assigns units with 'armor' , 'heavy_armor' and 'mechanized_assault' unit roles to the attack. |  |  |  |  |
| force_concentration_factor | `value = <int>`<br>The percentage value added or substracted. | *(example below)* | Factor added on top of the default force concentration ratio. Value of 20 means +20 %, so if the base define is 15 % the result would be 35 %. | See FORCE_CONCENTRATION_UNIT_RATIO_BASE in the [defines](<Defines - Hearts of Iron 4 Wiki.md>). A large negative value stops AI from using Force Concentration anywhere. |  |  |  |  |
| force_concentration_target_weight | `tag = <country>`<br>The country to target. Multiple can be specified. `state = <state>`<br>The state to target. Multiple can be specified.<br>`strategic_region = <ID>`<br>The strategic region to target. Multiple can be specified.<br>`area = <area>`<br>The [AI area](#AI_areas) to target. Multiple can be specified.<br>`country_trigger = { ... }`<br>Trigger block checked for countries. Scope is enemy country, FROM scope is our country.<br>`state_trigger = { ... }`<br>Trigger block checked for states.  Scope is state. FROM scope is enemy country FROM.FROM scope is our country.  <br>`value = <int>`<br>Factor for the normal priority. 40 means +40 %, -60 means -60 %. | *(example below)* | Affects the score for offensive targets for AI Force Concentration. | All the arguments are optional, only one needs to be specified. |  |  |  |  |
| front_unit_request | `state = <state>`<br>The state to target.<br> `tag = <country>`<br>The state to target.<br> `strategic_region = <ID>`<br>The strategic region to target.<br> `area = <state>`<br>The [AI area](#AI_areas) to target.<br> `country_trigger = { ... }`<br>Trigger block checked for states to have them as a target.<br> `state_trigger = { ... }`<br>Trigger block checked for countries to have them as a target.  `value = <int>`<br>The weight of the strategy. | *(example below)* *(example below)* | Pursues AI to put more (or less - if negative value is used) units on a specified land frontline. | More than one target type can be used at a time, in which case each one must be met. |  |  |  |  |
| invasion_unit_request | `state = <state>`<br>The state to target.<br> `tag = <country>`<br>The state to target.<br> `strategic_region = <ID>`<br>The strategic region to target.<br> `area = <state>`<br>The [AI area](#AI_areas) to target.<br> `country_trigger = { ... }`<br>Trigger block checked for states to have them as a target.<br> `state_trigger = { ... }`<br>Trigger block checked for countries to have them as a target.  `value = <int>`<br>The weight of the strategy. | *(example below)* *(example below)* | Pursues AI to put more units on a naval invasion with the specified target. | More than one target type can be used at a time, in which case each one must be met. |  |  |  |  |
| garrison | `value = <int>`<br>The weight of the strategy. | *(example below)* | Controls the amount of units spent on defending the victory points and ports rather than being active on the frontline. |  |  |  |  |  |
| garrison_reinforcement_priority | `value = <int>`<br>The weight of the strategy. | *(example below)* | Pursues AI to reinforce units that are put on garrisons, protecting victory points and naval bases, with higher priority. |  |  |  |  |  |
| ignore_army_incompetence | `value = <int>`<br>The weight of the strategy. | *(example below)* | Pursues AI to ignore the modifier given by the lack of experience of divisions in calculations. |  |  |  |  |  |
| put_unit_buffers | `ratio = <decimal>`<br>The amount of units to buffer.<br> `order_id = 2`<br> If two put_unit_buffers strategies use the same ID, the ratio used for them will be shared rather than them being added together.<br> `states = { ... }`<br> List of states where to buffer units<br> `area = <AI area>`<br> The AI area where to buffer units.<br> `subtract_invasions_from_need = yes`<br> If true, naval invasions within the area will not count towards the ratio. Defaults to false.<br> `subtract_fronts_from_need = yes`<br> If true, land frontlines within the area will not count towards the ratio. Defaults to false. | *(example below)* | Pursues AI to keep a certain ratio of divisions on garrison duty in the specified area. |  |  |  |  |  |
| spare_unit_factor | `value = <int>`<br>The weight of the strategy. | *(example below)* | Pursues AI to spare more units towards defending allies. |  |  |  |  |  |
| theatre_distribution_demand_increase | `value = <int>`<br>The weight of the strategy.<br> `id = <state>`<br>The target of the strategy.<br> | *(example below)* | Pursues AI to put more units in the specified state's theater. | A value of 1 translates to 1 unit. |  |  |  |  |

**Example: invade**

```text
ai_strategy = {
    type = invade
    id = USA
    value = -100
}
```

**Example: naval_invasion_focus**

```text
ai_strategy = {
    type = naval_invasion_focus
    value = 100
}
```

**Example: prepare_for_war**

```text
ai_strategy = {
    type = prepare_for_war
    id = USA
    value = 100
}
```

**Example: area_priority**

```text
ai_strategy = {
    type = area_priority
    id = europe
    value = 100
}
```

**Example: strategic_air_importance**

```text
ai_strategy = {
	type = strategic_air_importance
	id = 18 #English Channel
	value = -30000
}
```

**Example: dont_defend_ally_borders**

```text
ai_strategy = {
    type = dont_defend_ally_borders
    id = POL
    value = 10
}
```

**Example: force_defend_ally_borders**

```text
ai_strategy = {
    type = force_defend_ally_borders
    id = FRA
    value = 100
}
```

**Example: front_armor_score**

```text
ai_strategy = {
    type = front_armor_score
    id = POL
    value = 100
}
```

**Example: front_control**

```text
ai_strategy = {
    type = front_control
    state_trigger = {
        industrial_complex > 1
        is_owned_by = ENG
    }
    ratio = 0.1
    ordertype = front
    execution_type = rush
    manual_attack = no
}
```

**Example: front_control**

```text
ai_strategy = {
    type = front_control
    area = suez
    priority = 1
    ratio = 0.2
    ordertype = invasion
    execute_order = yes
}
```

**Example: force_concentration_front_factor**

```text
ai_strategy = {
	type = force_concentration_front_factor

	tag = CZE
	state = 9
	strategic_region = 22
	ratio = 0.2

	value = 40
}
```

**Example: force_concentration_factor**

```text
ai_strategy = {
	type = force_concentration_factor
	value = 20
}
```

**Example: force_concentration_target_weight**

```text
ai_strategy = {
# As Germany - Avoid attacking the areas behind the Maginot line
	type = force_concentration_target_weight
	state = 18 # Champagne
	state = 17 # Franche-Comte
	state = 28 # Alsace-Lorraine
	state = 27 # Bourgogne

	value = -60
}
```

**Example: front_unit_request**

```text
ai_strategy = {
    type = front_unit_request
    tag = POL
    value = 100
}
```

**Example: front_unit_request**

```text
ai_strategy = {
    type = front_unit_request
    country_trigger = {
        original_tag = SPR
        has_government = fascism
    }
    value = 100
}
```

**Example: invasion_unit_request**

```text
ai_strategy = {
    type = invasion_unit_request
    state = 123
    value = 100
}
```

**Example: invasion_unit_request**

```text
ai_strategy = {
    type = invasion_unit_request
    strategic_region = 42
    value = 100
}
```

**Example: garrison**

```text
ai_strategy = {
    type = garrison
    value = 10
}
```

**Example: garrison_reinforcement_priority**

```text
ai_strategy = {
    type = garrison_reinforcement_priority
    value = 100
}
```

**Example: ignore_army_incompetence**

```text
ai_strategy = {
    type = ignore_army_incompetence
    value = 100
}
```

**Example: put_unit_buffers**

```text
ai_strategy = {
    type = put_unit_buffers
    ratio = 0.2
    states = {
        123
        124
        125
        126
    }
    subtract_fronts_from_need = yes
}
```

**Example: spare_unit_factor**

```text
ai_strategy = {
    type = spare_unit_factor
    value = 100
}
```

**Example: theatre_distribution_demand_increase**

```text
ai_strategy = {
    type = theatre_distribution_demand_increase
    value = 10
    id = 123
}
```

AI strategies related to navy management:

| Name | Parameters | Examples | Description | Notes |
| --- | --- | --- | --- | --- |
| naval_avoid_region | `value = <int>`<br>The weight of the strategy.<br> `id = <strategic region>`<br>The target of the strategy. | *(example below)* | Pursues AI to avoid a specific strategic region with its ships. |  |
| naval_convoy_raid_region | `value = <int>`<br>The weight of the strategy.<br> `id = <strategic region>`<br>The target of the strategy. | *(example below)* | Pursues AI to raid convoys within the specified strategic region. |  |
| naval_mission_threshold | `value = <int>`<br>The weight of the strategy.<br> `id = <mission>`<br>The mission to change the threshold of. | *(example below)* | Makes AI have a higher threshold for its desire to do a naval mission. | A higher value means AI is less likely to do the mission. Names of missions can be found in `/Hearts of Iron IV/localisation/english/core_l_english.yml`, where a localisation key of `NAVAL_MISSION_NAME_CONVOY_RAIDING` means the mission is called `MISSION_CONVOY_RAIDING` |
| strike_force_home_base | `value = <int>`<br>The weight of the strategy.<br> `id = <strategic region>`<br>The target of the strategy. | *(example below)* | Pursues AI to do the strike force mission within the specified strategic region. |  |

**Example: naval_avoid_region**

```text
ai_strategy = {
    type = naval_avoid_region
    id = 23
    value = 100
}
```

**Example: naval_convoy_raid_region**

```text
ai_strategy = {
    type = naval_convoy_raid_region
    id = 23
    value = 100
}
```

**Example: naval_mission_threshold**

```text
ai_strategy = {
    type = naval_mission_threshold
    id = MISSION_CONVOY_RAIDING
    value = -100
}
```

**Example: strike_force_home_base**

```text
ai_strategy = {
    type = strike_force_home_base
    id = 18
    value = 70
}
```

AI strategies related to intelligence:

| Name | Parameters | Examples | Description | Notes |
| --- | --- | --- | --- | --- |
| agency_ai_base_num_factories_factor | `value = <int>`<br>The weight of the strategy. | *(example below)* | Changes the baseline used in the calculation of AI doing agency upgrades. | A value of 1 equals to a 1% increase over the baseline in [Defines](<Defines - Hearts of Iron 4 Wiki.md>). |
| agency_ai_per_upgrade_factories_factor | `value = <int>`<br>The weight of the strategy. | *(example below)* | Modifies the needed amount of factories used in the calculation of AI doing agency upgrades. | A value of 1 equals to a 1% increase over the baseline in [Defines](<Defines - Hearts of Iron 4 Wiki.md>). |
| intelligence_agency_branch_desire_factor | `value = <int>`<br>The weight of the strategy.<br> `id = <branch>`<br>The target of the strategy. | *(example below)* | Modifies the needed amount of factories used in the calculation of AI doing agency upgrades. | Branches are defined in `/Hearts of Iron IV/common/intelligence_agency_upgrades/*.txt` files. |
| intelligence_agency_usable_factories | `value = <int>`<br>The weight of the strategy. | *(example below)* | Modifies the amount of factories that AI would use for intelligence agencies. |  |
| operation_equipment_priority | `value = <int>`<br>The weight of the strategy. | *(example below)* | Pursues the AI to prioritise equipment for funding operations over other usages. |  |
| operative_mission | `value = <int>`<br>The weight of the strategy.<br> `mission = <mission>`<br>The mission to prioritise<br> `mission_target = <country>`<br>The country to target<br> `state = <state>`<br>The state to prioritise within the target country if valid. Optional.<br> `priority = <int>`<br>If contradictory AI strategies are defined, the one with the highest priority is picked. `num_operatives = <int>`  Number of operatives to assign to mission. Optional. | *(example below)* | Pursues the AI to do the specified mission over the target. | Multiple states can be defined, leading to one of them being prioritised. Mission names can be seen in `/Hearts of Iron IV/localisation/english/operatives_l_english.yml`. For example, `OPERATIVE_MISSION_BOOST_IDEOLOGY_TITLE:0 "Boost Ideology"` means that boosting ideology is boost_ideology. |
| operative_operation | `value = <int>`<br>The weight of the strategy.<br> `operation = <mission>`<br>The mission to prioritise<br> `operation_target = <country>`<br>The country to target<br> `state = <state>`<br>The state to prioritise within the target country if valid. Optional.<br> `region = <strategic region>`<br>The strategic region to prioritise within the target country if valid. Optional.<br> `priority = <int>`<br>If contradictory AI strategies are defined, the one with the highest priority is picked. | *(example below)* | Pursues the AI to do the specified operation over the target. | Multiple states can be defined, leading to one of them being prioritised. Operations are defined within `/Hearts of Iron IV/common/operations/*.txt` files. |
| become_spymaster | `value = <int>`<br>The weight of the strategy. | *(example below)* | Used to set weight for a faction leader to become spymaster if not already a spymaster | Weight value for pp spend to become spymaster. Added in 1.15.2 |

**Example: agency_ai_base_num_factories_factor**

```text
ai_strategy = {
    type = agency_ai_base_num_factories_factor
    value = 70
}
```

**Example: agency_ai_per_upgrade_factories_factor**

```text
ai_strategy = {
    type = agency_ai_per_upgrade_factories_factor
    value = 70
}
```

**Example: intelligence_agency_branch_desire_factor**

```text
ai_strategy = {
    type = intelligence_agency_branch_desire_factor
    id = branch_crypto
    value = 70
}
```

**Example: intelligence_agency_usable_factories**

```text
ai_strategy = {
    type = intelligence_agency_usable_factories
    value = 8
}
```

**Example: operation_equipment_priority**

```text
ai_strategy = {
    type = operation_equipment_priority
    value = 80
}
```

**Example: operative_mission**

```text
ai_strategy = {
    type = operative_mission
    value = 80
    mission = quiet_intel_network
    state = 123
    state = 321
    mission_target = ENG
}
```

**Example: operative_operation**

```text
ai_strategy = {
    type = operative_operation
    value = 80
    operation = heavy_water_raid
    operation_target = ENG
}
```

**Example: become_spymaster**

```text
ai_strategy = {
    type = become_spymaster
    value = 30
}
```

AI strategies related to production, construction, and recruitment:

| Name | Parameters | Examples | Description | Notes |
| --- | --- | --- | --- | --- |
| added_military_to_civilian_factory_ratio | `value = <int>`<br>The weight of the strategy. | *(example below)* | Modifies the ratio of military to civilian factories that the AI desires to keep. | A positive value means more military factories. |
| air_factory_balance | `value = <int>`<br>The weight of the strategy. | *(example below)* | Modifies the ratio of airforce to factories that the AI desires to keep. | A positive value means more airforce. |
| dockyard_to_military_factory_ratio | `value = <int>`<br>The weight of the strategy. | *(example below)* | Modifies the ratio of dockyards to military factories that the AI desires to keep. | A positive value means more dockyards. |
| railway_gun_divisions_ratio | `value = <int>`<br>The weight of the strategy. | *(example below)* | Modifies the ratio of railway guns to divisions that the AI desires to keep. | Base ratio is RAILWAY_GUN_PRODUCTION_BASE_DIVISIONS_RATIO_PERCENT in [Defines](<Defines - Hearts of Iron 4 Wiki.md>), by default 0. This gets added to it, on the 0-100 scale. |
| build_building | `value = <int>`<br>The weight of the strategy.<br> `id = <building>`<br>The target of the strategy.<br> `target = <state> (OR) <province>`<br>The state (or province) where to build. | *(example below)* | Pursues AI to construct a specific building within the specified state (or a specified province, if the building is province based). If no target is specified, AI selects a random location. | Value is an AI weight, used for weighted random selection of what to build. The AI gathers all build_building strategies (including the ones created dynamically) with non-zero values, and selects one of them. Strategy is ignored if the specified building is already being constructed. |
| building_target | `value = <int>`<br>The weight of the strategy.<br> `id = <building>`<br>A building to consider. | *(example below)* | Makes AI keep a minimum amount of the specified buildings. | The AI will construct the specified building until it reaches the target value (prioritizing it over other construction). **Note:** The AI uses 'total' amount of buildings. So in this specific case it will check, if it has a total of 30 Civilian Factories in its own states, in the occupied states AND from trade and received from subjects! |
| factory_build_score_factor | `value = <int>`<br>The weight of the strategy.<br> `target = <state>`<br>The state where to build. | *(example below)* | Pursues AI to construct buildings within the specified state. |  |
| equipment_production_factor | `value = <int>`<br>The weight of the strategy.<br> `id = <equipment archetype type>`<br>The target of the strategy. | *(example below)* | Pursues AI to produce equipment types of the specified type. | Types are defined for each equipment archetype in `/Hearts of Iron IV/common/units/equipment/*.txt` files within `types = { ... }`. |
| equipment_production_min_factories | `value = <int>`<br>The weight of the strategy.<br> `id = <equipment type>`<br>The target of the strategy. | *(example below)* | Pursues AI to keep a minimum amount of factories on the production lines for the equipment of the specified **type**. If multiple strategies are used at once, they stack. | A value of 1 corresponds to 1 military factory. Types are defined for each equipment archetype in `/Hearts of Iron IV/common/units/equipment/*.txt` files within `types = { ... }`. **Note:** Multiple variants of the same 'type' of equipment may exist. This specific strategy will for example make AI have 3 lines of Artillery AND 3 lines of Rocket Artillery AND 3 lines of Motorized Rocket Artillery. |
| equipment_production_min_factories_archetype | `value = <int>`<br>The weight of the strategy.<br> `id = <equipment archetype>`<br>The target of the strategy. | *(example below)* | Pursues AI to keep a minimum amount of factories on the production lines for the equipment of the specified **archetype**. If multiple strategies are used at once, they stack. | A value of 1 corresponds to 1 military factory. Archetypes are defined in each file in `/Hearts of Iron IV/common/units/equipment/*.txt` with `is_archetype = yes` argument. |
| equipment_variant_production_factor | `value = <int>`<br>The weight of the strategy.<br> `id = <equipment archetype>`<br>The target of the strategy. | *(example below)* | Pursues AI to produce more of the specified equipment archetype. | Equipment archetypes are defined in `/Hearts of Iron IV/common/units/equipment/*.txt` files. |
| equipment_stockpile_surplus_ratio | `value = <int>`<br>The weight of the strategy. | *(example below)* | Changes the ratio of equipment that AI would hold in stockpile rather than immediately using. |  |
| build_army | `value = <int>`<br>The weight of the strategy.<br> `id = <unit role>`<br>The target of the strategy. | *(example below)* | Modifies the desired division amount for AI. | The used target is roles within [AI templates](#AI_templates). This example would make the AI want exactly 200 divisions with 'infantry' role. |
| force_build_armies | `value = <int>`<br>The weight of the strategy. | *(example below)* | Forces AI to build divisions above the desired amount. |  |
| production_upgrade_desire_offset | `value = <int>`<br>The weight of the strategy.<br> `id = <equipment type>`<br>The target of the strategy. | *(example below)* | Pursues AI to upgrade production lines to the specified equipment type. | Equipment types are defined in `/Hearts of Iron IV/common/units/equipment/*.txt` files. |
| role_ratio | `value = <int>`<br>The weight of the strategy.<br> `id = <role>`<br>The target of the strategy. | *(example below)* | Modifies the amount of templates that the AI makes for the specified role. | Roles are defined within [AI templates](#AI_templates) for unit templates and [AI equipment](#AI_equipment) for ship and tank variants. |
| unit_ratio | `value = <int>`<br>The weight of the strategy.<br> `id = <unit>`<br>The target of the strategy. | *(example below)* | Modifies the amount of templates that the AI makes with the specified unit. | Units are defined in `/Hearts of Iron IV/common/units/*.txt` files. This includes the airforce and navy alongside land army. |
| min_wanted_supply_trains | `value = <int>`<br>The weight of the strategy. | *(example below)* | Overrides the minimum amount of supply trains wanted by AI. |  |
| min_wanted_supply_trucks | `value = <int>`<br>The weight of the strategy. | *(example below)* | Overrides the minimum amount of supply trucks wanted by AI. |  |

**Example: added_military_to_civilian_factory_ratio**

```text
ai_strategy = {
    type = added_military_to_civilian_factory_ratio
    value = 50
}
```

**Example: air_factory_balance**

```text
ai_strategy = {
    type = air_factory_balance
    value = 50
}
```

**Example: dockyard_to_military_factory_ratio**

```text
ai_strategy = {
    type = dockyard_to_military_factory_ratio
    value = 50
}
```

**Example: railway_gun_divisions_ratio**

```text
ai_strategy = {
    type = railway_gun_divisions_ratio
    value = 5
}
```

**Example: build_building**

```text
ai_strategy = {
    type = build_building
    id = industrial_complex
    target = 803
    value = 1
}
```

**Example: building_target**

```text
ai_strategy = {
    type = building_target
    id = industrial_complex
    value = 30
}
```

**Example: factory_build_score_factor**

```text
ai_strategy = {
    type = factory_build_score_factor
    target = 365
    value = 1
}
```

**Example: equipment_production_factor**

```text
ai_strategy = {
    type = equipment_production_factor
    id = armor
    value = 30
}
```

**Example: equipment_production_min_factories**

```text
ai_strategy = {
    type = equipment_production_min_factories
    id = artillery
    value = 3
}
```

**Example: equipment_production_min_factories_archetype**

```text
ai_strategy = {
    type = equipment_production_min_factories_archetype
    id = artillery_equipment
    value = 4
}
```

**Example: equipment_variant_production_factor**

```text
ai_strategy = {
    type = equipment_variant_production_factor
    id = light_tank_chassis
    value = -100
}
```

**Example: equipment_stockpile_surplus_ratio**

```text
ai_strategy = {
    type = equipment_stockpile_surplus_ratio
    value = 30
}
```

**Example: build_army**

```text
ai_strategy = {
    type = build_army
    id = infantry
    value = 200
}
```

**Example: force_build_armies**

```text
ai_strategy = {
    type = force_build_armies
    value = 30
}
```

**Example: production_upgrade_desire_offset**

```text
ai_strategy = {
    type = production_upgrade_desire_offset
    id = artillery_equipment_2
    value = -50
}
```

**Example: role_ratio**

```text
ai_strategy = {
    type = role_ratio
    id = paratroopers
    value = 30
}
```

**Example: unit_ratio**

```text
ai_strategy = {
    type = unit_ratio
    id = cas
    value = 30
}
```

**Example: min_wanted_supply_trains**

```text
ai_strategy = {
    type = min_wanted_supply_trains
    value = 300
}
```

**Example: min_wanted_supply_trucks**

```text
ai_strategy = {
    type = min_wanted_supply_trucks
    value = 30
}
```

Other AI strategies:

| Name | Parameters | Examples | Description | Notes |
| --- | --- | --- | --- | --- |
| scorched_earth_prio | `value = <int>`<br>The weight of the strategy.<br> `id = <country>`<br>The owner of the states where to use scorched earth.<br> `states = { ... }`<br> List of states where to use scorched earth. | *(example below)* | Pursues AI to use scorched earth within the specified states. |  |
| land_xp_spend_priority | `value = <int>`<br>The weight of the strategy.<br> `id = <type>`<br>The target of the strategy. | *(example below)* | Modifies the priority for AI to spend land experience. | Base game usages include `division_template` and `upgrade_xp_cutoff`. |
| pp_spend_amount | `value = <int>`<br>The weight of the strategy.<br> `id = <type>`<br>The target of the strategy. | *(example below)* | Modifies the political power that AI should preserve for the specified purpose. | Base game usages include `idea` and `decision`. |
| pp_spend_priority | `value = <int>`<br>The weight of the strategy.<br> `id = <type>`<br>The target of the strategy. | *(example below)* | Modifies where AI should prioritise spending political power. | Base game usages include the following:  - `admiral` - `guarantee` - `relation` - `decision` |
| research_weight_factor | `value = <int>`<br>The weight of the strategy.<br> `id = <type>`<br>The target of the strategy. | *(example below)* | Modifies the AI weight (score) of a specific technology. | value = 50 means 50% increase, -30 means 30% decrease, etc. |

**Example: scorched_earth_prio**

```text
ai_strategy = {
    type = scorched_earth_prio
    value = 100
    id = ENG
    states = {
        123
        124
        125
        126
    }
}
```

**Example: land_xp_spend_priority**

```text
ai_strategy = {
    type = land_xp_spend_priority
    id = division_template
    value = 30
}
```

**Example: pp_spend_amount**

```text
ai_strategy = {
    type = pp_spend_amount
    id = idea
    value = 100
}
```

**Example: pp_spend_priority**

```text
ai_strategy = {
    type = pp_spend_priority
    id = relation
    value = 100
}
```

**Example: research_weight_factor**

```text
ai_strategy = {
    type = research_weight_factor
    id = radio_detection
    value = 2000
}
```

<!-- kit:begin id="ai-types-missing" at="section:Types" -->
**Kit addition** The 31 strategy tokens of the documentation's list that no table above names. `id` is the target unless stated. "Used" counts strategy entries in vanilla `ai_strategy/` and `ai_strategy_plans/` (a lower bound). All rows: [docs] `common/ai_strategy/_documentation.md` for token, parameters and meaning; [vanilla-confirmed 1.19.3] for "Used". Cells marked [unverified] have no description in the documentation.

| Type | Parameters | Meaning and value | Used |
| --- | --- | --- | --- |
| `avoid_starting_wars` | `value` | Targetless and additive with `conquer`; for narrow situations only. Doc example: -200 here plus `conquer` 200 on GER leaves GER at 0 and everyone else at -200. Vanilla writes -400 in `default.txt` | 9 |
| `naval_invasion_dominance_weight` | `value` | Makes the AI spend more of its navy on supremacy in regions that its naval invasions pass through. Doc example 30; vanilla 30 and 40 in `USA.txt` | 3 |
| `naval_dominance` | `id` = AI area key or strategic region id, `value` | Wanted naval dominance in that area as a percentage, 0 to 100 (vanilla also writes -100 in `ENG.txt`) | 41 |
| `convoy_raiding_target` | `id` = country, `value` | Importance of convoy raiding against that country, percentage 0 to 100 | 0 |
| `naval_blockade` | `target_country`, `id` = strategic region, `value` | Blockade importance, percentage 0 to 100. In the doc examples but not in its token list | 0 |
| `coast_defense` | `id` = strategic region, `value` | Coast defense importance, percentage 0 to 100. In the doc examples but not in its token list | 0 |
| `equipment_production_surplus_management` | `id` = equipment type, `value` | Weight of what to produce once all normal needs are met. Very high values can disturb the normal need calculation. Vanilla: `infantry_equipment` 10, `support_equipment` 5 | 6 |
| `equipment_market_spend_factories` | `value` | Factor on the define `NAI.EQUIPMENT_MARKET_MAX_CIVS_FOR_PURCHASES_RATIO` (0.1): 20 gives a factor of 1.2 | 3 |
| `equipment_market_for_sale_threshold` | `id` = equipment, `value` | Units of surplus needed before the AI offers the equipment for sale (absolute number) | 32 |
| `equipment_market_for_sale_factor` | `id` = equipment, `value` | Factor on `NAI.EQUIPMENT_MARKET_BASE_MARKET_RATIO` (0.2): 50 gives 1.5 | 8 |
| `equipment_market_max_for_sale` | `id` = equipment, `value` | Most units put on the market; a value of 0 is ignored | 1 |
| `equipment_market_min_for_sale` | `id` = equipment, `value` | Smallest lot on offer, kept in multiples; overrides `EQUIPMENT_MARKET_DEFAULT_CIC_CHUNK_FOR_SALE` (150) | 2 |
| `equipment_market_buying_threshold` | `id` = equipment archetype, `value` | Absolute units: 50 means buy 50 more than needed, -20 means buy only when the deficit exceeds 20 | 5 |
| `equipment_market_buy` | `equipment_type` and or `seller`, `value` | Part of the score of what to buy; at least one of the two keys. Related define `EQUIPMENT_MARKET_SCORE_FACTOR_AI_STRAT_WEIGHT` (50) | 4 |
| `equipment_market_trade_desire` | `id` = trade partner, `value` | Raises acceptance and desire to trade with that country | 35 |
| `research_tech` | `id` = technology, `value` | Forces research as soon as possible; any positive value | 0 |
| `air_xp_spend_priority`, `navy_xp_spend_priority` | `id`, `value` | Same ids as `land_xp_spend_priority`: `division_template`, `unlock_doctrine`, `equipment_variant`, `upgrade_xp_cutoff`, and `army_spirit`, `air_spirit` or `navy_spirit` matching the category | 1 and 2 |
| `raid_target_country` | `id` = country, `value` | Percentage change of the raid chance toward that country: 200 is +200 percent | 1 |
| `save_equipment` | `id` = equipment type, `value` | No description; vanilla writes `transport_plane_equipment` 10 and `support_equipment` 100 in `GER.txt`. Probably keeps stock back [unverified] | 7 |
| `template_prio` | `id`, `value` | No description; ids are unit or role tokens (`medium_armor` 21, `light_armor` 19, `cavalry` 17, `motorized` 16, `heavy_armor` 14, `paratroopers` 14, `infantry` 14 and others), values -100 to 100 [unverified] | 143 |
| `ai_wanted_divisions_factor` | `value` | No description; vanilla writes 100 and 1000 in `CHI.txt` [unverified] | 5 |
| `occupation_policy`, `influence`, `activate_crypto`, `decrypt_target` | `id` = country | Listed without description; each has a readable variable `ai_strategy_<type>@<country>` [docs] `documentation/dynamic_variables_documentation.md` | 0 |
| `build_airplane`, `build_ship` | | Listed without description. The unit ratio text says the game itself sets `build_airplane` values from `unit_ratio`, so do not script it | 0 |
| `convoy_efficiency_to_cancel_trades`, `min_convoy_efficiency_factor_for_war_support_hit`, `fuel_buffer`, `wanted_supply_trucks`, `wanted_supply_trains` | `value` | Listed without description; the page already covers `min_wanted_supply_trucks` and `min_wanted_supply_trains` | 0 |

All 31 tokens (and `naval_blockade`, `coast_defense`) are also standalone strings in `hoi4.exe`. [unverified] read-only grep, no test.
<!-- kit:end id="ai-types-missing" -->

<!-- kit:begin id="ai-types-vanilla-only" at="section:Types" -->
**Kit addition** Types that vanilla uses but the 1.19.3 token list does not contain. All rows: [vanilla-confirmed 1.19.3] `common/ai_strategy/*.txt`; meaning of `recruit_scientist` and `naval_invasion_support_priority` is read from the ids, not stated in a game file [unverified].

| Type | Seen as | Used |
| --- | --- | --- |
| `spent_faction_initiative_priority` | `id` = `program`, `unlock_doctrine_sharing` or `unlock_faction_commander`, `value`. Ids and meaning are in `common/factions/_documentation.md` [docs]; see the end of [Faction modding](<Faction modding - Hearts of Iron 4 Wiki.md>) | 9 |
| `become_head_of_crypto`, `become_head_of_counter_intel`, `become_head_of_operations` | `value` only; the same shape as `become_spymaster`, listed in `common/factions/_documentation.md` [docs] | 2, 1, 1 |
| `recruit_scientist` | `id = specialization_land` or `specialization_nuclear`, `value = 100`, in `default.txt`. Probably weighs which scientist specialization to recruit | 4 |
| `naval_invasion_support_priority` | `id` = strategic region number (the comment says "Central Mediterranean" for 29), `value = 200`, in `ENG.txt`. Probably raises where invasion support goes | 7 |
<!-- kit:end id="ai-types-vanilla-only" -->

<!-- kit:begin id="ai-types-corrections" at="section:Types" -->
**Kit correction** Three fixes to the tables above.

- `force_concentration_factor` refers to `FORCE_CONCENTRATION_UNIT_RATIO_BASE`. No such define exists in `common/defines/00_defines.lua` or `hoi4.exe`. The matching define is `NDefines.NAI.AIFC_UNIT_RATIO_BASE = 0.15`: after front minimums are met, this share of the extra units goes to force concentration. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`; the documentation uses the wrong name too. [docs] `common/ai_strategy/_documentation.md`.
- The `front_unit_request` and `invasion_unit_request` rows say `tag` is "the state to target" and `area` is `<state>`. `tag` is a country tag and `area` is an AI area key. [docs] `common/ai_strategy/_documentation.md`.
- `invade`: a negative value makes the AI avoid invading that country at all; a positive value multiplies the importance of invasions against it while it is a potential enemy (60 means 1.6 times). `dont_defend_ally_borders` is binary, any value above 0 turns it on. [docs] `common/ai_strategy/_documentation.md`.
<!-- kit:end id="ai-types-corrections" -->

<!-- kit:begin id="ai-unit-ratios" at="section:Types" -->
**Kit addition** How `unit_ratio`, `role_ratio` and `equipment_production_factor` turn into numbers. All lines: [docs] `common/ai_strategy/_documentation.md`; the define values are [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` (`NDefines.NAI`).

- Land, naval and other non-air types: the wanted share is 100 plus the strategy value. A `unit_ratio` of -40 gives 60 percent of the wanted number. `equipment_production_factor` works the same way on the factory count that the need calculation yields.
- Air types are weights, not percentages. A type without a `unit_ratio` has weight 0, and a plane type locked by a missing DLC is treated as 0. Land-based and carrier planes are counted separately.
- Wanted land-based planes: total air base capacity (without carriers) times `WANTED_LAND_PLANES_PER_BASE_CAPACITY_FACTOR` (1), plus wanted divisions times `WANTED_LAND_PLANES_PER_DIVISION` (20), minus planes already in air wings, limited to 0 and to wanted divisions times `WANTED_LAND_PLANES_TOTAL_MAX_PER_DIVISION` (100). The result is multiplied by the hard-coded aviation focus value, which `ai_focus_aviation_factor` has already scaled.
- Wanted carrier planes: carrier deck capacity times `WANTED_CARRIER_PLANES_PER_CARRIER_CAPACITY_FACTOR` (1.5), plus deck capacity of carriers finishing within `CARRIER_CAPACITY_IN_PRODUCTION_MAX_DAYS_LEFT_TO_INCLUDE_FACTOR` (365) days times `WANTED_CARRIER_PLANES_PER_CARRIER_CAPACITY_IN_PRODUCTION_FACTOR` (1), minus carrier planes in air wings, at least 0. The result is multiplied by the naval air focus value, scaled by `ai_focus_naval_air_factor`.
- Each plane type then gets its `unit_ratio` divided by the sum of the `unit_ratio` values of its group, times the wanted total; that sets the `build_airplane` values.
<!-- kit:end id="ai-unit-ratios" -->

## AI areas <a id="AI_areas"></a>

AI areas are defined within `/Hearts of Iron IV/common/ai_areas/*.txt` files. These are *only* used in a variety of previously-listed AI strategies, such as area_priority. A province may be in several AI areas and it may be in none. Hovering over a province with the debug mode turned on will provide information in which AI areas the province is, if any.

Each AI area is a separate block within the file, with the name of the block being the name of the area. Within these blocks, 2 things can be added:
`continents = { ... }` is a list of continents that make up the AI area. Continents are defined within `/Hearts of Iron IV/map/continent.txt` and assigned to provinces within [their definitions](<Map modding - Hearts of Iron 4 Wiki.md#Provinces>) in `/Hearts of Iron IV/map/definition.csv`. The full name of the continent should be used within the AI area's definition, rather than the ID used in the province definition.
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

<!-- kit:begin id="ai-areas-wrapper" at="section:AI_areas" -->
**Kit correction** The example above leaves out the root block. Vanilla `common/ai_areas/default.txt` is one `areas = { ... }` block holding every area, for example `areas = { suez = { strategic_regions = { 128 28 232 } } ... }`. It defines 56 areas; 50 use `strategic_regions` and 6 use `continents`, and no area uses another key. Write the wrapper as vanilla does; a file without it is [unverified]. [vanilla-confirmed 1.19.3] `common/ai_areas/default.txt`.

Strategies that take an AI area key: `area_priority`, `front_control`, `front_unit_request`, `invasion_unit_request`, `force_concentration_front_factor`, `force_concentration_target_weight`, `put_unit_buffers` (`area`) and `naval_dominance` (`id`, a key or a region id). [docs] `common/ai_strategy/_documentation.md`.
<!-- kit:end id="ai-areas-wrapper" -->

## AI focuses <a id="AI_focuses"></a>

*Main article: [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>)*

AI focuses, defined within `/Hearts of Iron IV/common/ai_focuses/*.txt` files, are used to tell the game which technology categories and focuses the AI should pick depending on its currently-pursued focuses.

<!-- kit:begin id="ai-focuses-content-fix" at="section:AI_focuses" -->
**Kit correction** `common/ai_focuses/` files do not choose national focuses. In 1.19.3 each block holds only `research = { <technology category> = <weight> }`. National focus lists belong to strategy plans (`ai_national_focuses`, `focus_factors`) below. The nine focus ids, their `ai_focus_<x>_factor` modifiers and the file format are on [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>). [vanilla-confirmed 1.19.3] `common/ai_focuses/*.txt`.
<!-- kit:end id="ai-focuses-content-fix" -->

## AI peace <a id="AI_peace"></a>

<!-- kit:begin id="ai-peace-1193" at="heading:AI_peace" -->
**Kit correction** This section is partly outdated for 1.19.3. The checked reference is [Peace conference modding](<Peace conference modding - Hearts of Iron 4 Wiki.md>). What differs:

- The "Pre-1.12" folder `common/ai_peace/` does not exist in 1.19.3. The only peace AI folder is `common/peace_conference/ai_peace/` (15 files: `00_misc.txt`, `yalta.txt`, `warlords.txt` and country files). The old action blocks `annex`, `puppet_all` and `puppet_state` have no counterpart: entries now have exactly `peace_action_type`, `enable` and `ai_desire`. [vanilla-confirmed 1.19.3] `common/peace_conference/ai_peace/`, folder listing of `common/`.
- The documented action types are `take_states`, `puppet`, `force_government` and `liberate`. `take_navy`, listed above as a fifth type, is not one: no vanilla file uses it as a `peace_action_type`, so give a `take_navy` AI desire no weight. [docs] `common/peace_conference/ai_peace/_documentation.md`; [vanilla-confirmed 1.19.3] `common/peace_conference/` (no file contains `take_navy`).
- Scopes in an entry, as the documentation states them: `ROOT` is the negotiator, `FROM` the taker (who owns the result), `FROM.FROM` the giver and `FROM.FROM.FROM` the state. The text above calls `FROM` the country that undergoes the action; that reading differs. [docs] `common/peace_conference/ai_peace/_documentation.md`.
- All active entries for an action are summed and a total of 0 or lower means the AI does not take it; the documentation example also reads `ai_desire = 100` as +100 percent. The -1000 and 1000 meanings stated above are not in the documentation. The scale is discussed on the Peace conference page. [docs] `common/peace_conference/ai_peace/_documentation.md`.
- `dont_puppet_warlord_countries` in the example is an invented name. The real warlord entry is `warlords_want_to_conquer_china` in `warlords.txt`. [vanilla-confirmed 1.19.3] `common/peace_conference/ai_peace/warlords.txt`.
<!-- kit:end id="ai-peace-1193" -->

**AI peace since 1.12**

The peace conference behaviour for AI is defined within `/Hearts of Iron IV/common/peace_conference/ai_peace/*.txt` files.

When defining the peace conference AI that would be used by the country, the AI will take into account all blocks for which the enable condition is true.

When evaluating the peace conference, `ROOT` (the default scope) is used to represent the currently-evaluated winner, `FROM` is the country which will undergo the selected peace action, this can be a previously non-existent country that will now be liberated or puppeted, or even a different winner country when liberating, finally `FROM.FROM.FROM` can be used to set conditions on the specific state that the peace action is taken on.

The `enable = { ... }` trigger block is used to determine whether the AI should be enabled, and finally an `ai_desire = ...` block determines the priority of the defined strategy: a value of -1000 would make AI never pursue the selected peace action if the conditions are met, while a value of 1000 would make the action their top priority.

The following peace options are used in the game:

- `liberate` - The country FROM gets liberated by ROOT.
- `puppet` - The country FROM gets puppeted by ROOT.
- `take_states` - We give state FROM.FROM.FROM, previously owned by FROM.FROM, to FROM. FROM here is either the country itself (ROOT) or an ally with either cores or claims.
- `force_government` - The country FROM gets its ideology forcefully changed by ROOT.
- `take_navy` - No AI modding supported, cost modifiers can still be applied for players in games with ![By Blood Alone](media/ai-modding-hearts-of-iron-4-wiki_04cfcba22e__img12.png)By Blood Alone enabled.

When evaluating peace conferences, the controller of a given state is the same one that occupied it before the start of the conference while the owner is the original owner.

Example:

```text
peace_ai_desires = {
    dont_puppet_warlord_countries = {
        peace_action_type = { puppet liberate force_government }    #all but take states
        enable = {
            FROM = {
                OR = {
                    tag = SIK
                    tag = PRC
                    tag = GXC
                    tag = YUN
                    tag = SHX
                    tag = XSM
                    tag = MAN
                    tag = MEN
                }
            }
        }
        ai_desire = -1000
    }
}
```

**Pre-1.12 AI peace**

The peace conference behaviour for AI is defined within `/Hearts of Iron IV/common/ai_peace/*.txt` files.

When defining the peace conference AI that would be used by the country, the game picks the first-defined one that meets the prerequisites. In this case, files are loaded sorted by their filename using ASCII character IDs.

When evaluating the peace conference, ROOT (the default scope) is used to represent the currently-evaluated winner and FROM is used to represent the currently-evaluated loser. Additionally, the following [temporary variables](<Data structures - Hearts of Iron 4 Wiki.md>) exist within:

- taken_states@TAG is an array of states that are annexed by the country TAG as a part of the peace conference.
- taken_by@123 is the country that took the specified state, in this case 123.
- current_states@TAG is an array of states that aren't decided upon yet in the peace conference and are under the control of TAG that lost the war.
- subject_states@TAG is an array of states that are, within the peace conference, set to be transferred to countries that are subjected by TAG.
- subject_countries@TAG is an array of countries that are, within the peace conference, set to be subjected by TAG.
- subjected_by@123 is the overlord of the country that is set to have the specified state in the peace conference, in this case 123.
- subjected_by@TAG is an array of countries that have TAG as their overlord.
- liberate_states@TAG is an array of states that are going to countries that have been liberated by TAG.
- liberate_countries@TAG is an array of countries that have been liberated by TAG.

The `enable = { ... }` trigger block is used to determine whether the AI should be enabled. If true and no other previously-loaded peace conference AI is true, this AI will be chosen.

There are the following peace options that are used in the game:

- annex - The country FROM gets entirely annexed by ROOT. This only evaluates the countries.
- liberate - The country FROM gets liberated by ROOT.
- puppet - The country FROM gets puppeted by ROOT.
- puppet_all - The country FROM gets puppeted by ROOT *and* is able to retain all of its states.
- puppet_state - The state ROOT gets transferred to FROM.FROM, which became a subject of FROM within the peace conference.
- take_states - The state FROM gets annexed by ROOT.
- force_government - The country FROM gets its ideology forcefully changed by ROOT.

When evaluating peace conferences, the controller of a given state is the same one that occupied it before the start of the conference while the owner is the original owner.

Each peace conference option is a [MTTH block](#MTTH_blocks) within the file's definition.

Example:

```text
my_peace_conference = {
    enable = {
        has_government = my_ideology_group
    }
    annex = {
        base = 500
        modifier = {
            factor = 0
            any_allied_country = {
                any_state = {
                    is_owned_by = FROM
                    is_core_of = PREV
                    NOT = {
                        is_core_of = ROOT
                        is_claimed_by = ROOT
                    }
                }
            }
        }
    }
    puppet = {
        base = 100
        modifier = {
            factor = 0
            FROM = { tag = QAT }
        }
    }
    puppet_all = {
        base = 0
    }
    puppet_state = {
        base = 100
        modifier = {
            factor = 0
            FROM.FROM = { tag = QAT }
        }
        modifier = {
            factor = 0
            any_allied_country = {
                ROOT = {
                    is_core_of = PREV
                    NOT = {
                        is_core_of = FROM.FROM
                        is_claimed_by = FROM.FROM
                    }
                }
            }
        }
    }
    take_states = {
        base = 100
        modifier = {
            factor = 0
            any_allied_country = {
                FROM = {
                    is_core_of = PREV
                    NOT = {
                        is_core_of = ROOT
                        is_claimed_by = ROOT
                    }
                }
            }
        }
    }
}
```

## AI strategy plans <a id="AI_strategy_plans"></a>

AI strategy plans to tell AI what to prioritise depending on circumstances: which advisors to pick, which technologies to research, which AI strategies to apply, which focuses to pick, etc. These are more detailed than general AI strategies, primarily intended to be activated for most of the game to tell the overall plan of a country. Multiple AI strategy plans can be defined and executed at the same time for a country.

AI strategy plans are defined within `/Hearts of Iron IV/common/ai_strategy_plans/*.txt` files. Within these files, a new strategy plan is done as a new block, the name of which must be the same as the internal ID of the plan.

Within that plan, `name = "AI plan's name"` and `desc = "AI plan's description"` decide the name and the description of the strategy plan. *This is never intended to be shown to the player*, so localising it into different languages is never needed. Instead, this is used within the `aiview` console command, which tells info to the developer about what AI wants to prioritise.

`allowed = { ... }` is, similarly to decisions or ideas, is a trigger block **checked only at the game's start**. This is primarily used to tell which country and DLCs to restrict the strategy plan to.

`enable = { ... }` is checked each day if the allowed is met. If `enable = { ... }` is met, then the AI strategy plan will be assigned to the AI regardless of whether `enable = { ... }` turns false later or not. Commonly, [Triggers#has_game_rule](<Triggers - Hearts of Iron 4 Wiki.md>) is used to make it work with custom game rules deciding what path the AI will pick. [is_historical_focus_on](<Triggers - Hearts of Iron 4 Wiki.md>) is commonly used with the default AI game rule, and country flags can be used for randomisation, by setting up an [on_startup](<On actions - Hearts of Iron 4 Wiki.md>) to set a random one using [random_list](<Scopes - Hearts of Iron 4 Wiki.md>)

`abort = { ... }` is checked every day in order to make the AI *stop* using this AI strategy plan if `enable = { ... }` is met. Additionally, it must be false in order for the AI strategy plan to be possible to be picked.

`ai_national_focuses = { TAG_focus_name_1 TAG_focus_name_2 }` is a list of national focuses, separated by whitespaces, in the order that the AI should take them. In this example, the AI will try to take TAG_focus_name_1 first if possible. If it's already taken or TAG_focus_name_1 is impossible to take, then AI will try to take TAG_focus_name_2. If both of the focuses are impossible to take due to being completed or unavailable, then it will move on to other focuses, taking `ai_will_do = { ... }` into consideration. While following a focus order, it ignores `ai_will_do = { ... }` values.

`focus_factors = { ... }` assigns a multiplier to ai_will_do values of the specified focus. An entry in this block looks like `TAG_focus_name = 3`. In this case, this will make the ai_will_do value of the focus be multiplied by 3, assuming AI strategy plan's weight of 1. If the focus has an ai_will_do value of 4 after applying modifiers, it'll become 12 if AI is following this strategy plan, and get treated as such. And, of course, a factor of 0 will make the focus be never picked without specification in ai_national_focuses. This can serve as a faster-to-write or a more randomised way to make AI follow a political path by making focuses it should never pick have a value of 0.

`research = { ... }` assigns a multiplier to ai_will_do values of the specified research categories. An entry in this block looks like `artillery = 3`. In this case, this will make the ai_will_do value of every technology within the category be multiplied by 3, assuming AI strategy plan's weight of 1. Other built-in modifiers still apply, but this will increase the likelihood.

Other blocks that also assign bonuses are `ideas = { ... }` and `traits = { ... }`, with the similar formatting. The ideas block is used for individual ideas (such as laws or designers) or advisors (using the idea_token in the entry), while traits are for country leader traits that are assigned to the ideas/advisors.

`ai_strategy = { ... }` allows an [AI strategy](#AI_strategies) to apply when the strategy plan is turned on.

`weight = { ... }` is a [MTTH block](#MTTH_blocks) assigning an overall weight to the plan. This multiplies each factor within the AI strategy plan by the weight before applying them. A weight of 1.25 will turn a focus factor of 4 into 5 before applying it, for instance. This can be used to make the AI follow the strategy plan more strictly in some cases and less strictly in others.

<!-- kit:begin id="ai-plans-1193" at="section:AI_strategy_plans" -->
**Kit note** Facts about plans in 1.19.3. All lines: [vanilla-confirmed 1.19.3] `common/ai_strategy_plans/*.txt`, counted by script.

- 376 plan blocks in 128 files. Top-level keys and how many plans use them: `enable` 376, `abort` 368, `name` 366, `allowed` 366, `ideas` 365, `desc` 364, `weight` 362, `ai_national_focuses` 352, `research` 351, `focus_factors` 252, `traits` 125, `ai_strategy` 61. No other top-level key occurs, so the key list above is complete.
- `weight` is a weight block: 361 plans use `modifier` and 359 use `factor`. `research` keys are technology categories such as `artillery` (96 plans), `infantry_tech` (88), `support_tech` (88) and `industry` (87). `traits` lists country leader or advisor trait ids such as `captain_of_industry` (75 plans) and `war_industrialist` (56). `ideas` lists idea ids and spirits.
- 72 plan files test `is_historical_focus_on = yes` in `enable`, usually together with `has_game_rule`. Plan ids and file names follow `<TAG>_historical_strategy_plan` and `<TAG>_alternate_strategy_plan` by habit, nothing requires it.
- 124 plan files carry an `ai_national_focuses` list; `focus_factors` of 0 bans a focus (`GER_prioritize_economic_growth = 0` in `GER_historical_strategy_plan.txt`).
<!-- kit:end id="ai-plans-1193" -->

### Example <a id="Example_2"></a>

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

<!-- kit:begin id="ai-plan-example-fixes" at="section:Example_2" -->
**Kit correction** In the example, `traits = { fascist_demagouge = 0 }` has a misspelled id. The country leader trait is `fascist_demagogue`, defined in `common/country_leader/00_traits.txt`; the misspelled key matches no trait. `BHR_historical`, `BHR_alternate`, `BHR_advisor`, `BHR_focus_name_1` to `5`, `BHR_ai_behavior` and the `BHR_AI_RANDOM_*` flags are placeholders, as is the `OMA` abort condition. [vanilla-confirmed 1.19.3] `common/country_leader/00_traits.txt` (`fascist_demagogue`); a typo'd key being ignored without an error is [unverified].

Game rule options named in `has_game_rule` must be option names of a rule in `common/game_rules/`; vanilla uses `DEFAULT`, `FASCIST`, `DEMOCRATIC`, `RANDOM` and similar. See [Bookmark modding](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules_2>). [vanilla-confirmed 1.19.3] `common/ai_strategy_plans/GER_historical_strategy_plan.txt`.
<!-- kit:end id="ai-plan-example-fixes" -->

## AI templates <a id="AI_templates"></a>

Scripters/modders are able to specify so called "target templates" that the AI try to reach when upgrading division templates.

Target templates are defined on a "role" level, and it's possible to define a number of different target templates for a specific role. The AI then chooses one of those target templates (based on scripted priorities) and aims for that.

For each role, the AI will select one target template based on the `prio`, `enable`, and `replace_with` parameters. This is referred to as the "currently targeted template".

The AI will then compare the existing division templates it has to find which one best matches the targeted template. This is referred to as the "best match" and the "match score"/"match" refers to how well it matches (100 % match = 1.0).

When the AI decides to upgrade a division template, it will make a copy of the best matching template and modify it so it gets a higher match score (i.e. looks more like the target template). (Note that the AI actually never does in-place modification of templates, it just makes a copy and modifies the copy instead.)

The AI strategy \`role_ratio\` determines how many divisions the AI wants for each role.

Role arguments:

- `role =` the role token that this role-level template entry targets. These tokens are defined by script and are targeted by the 'role_ratio' AI strategy.
- `blocked_for = { ... }` Determines which countries will use this role-level template entry. Both 'blocked_for' and 'available_for' are possible to use. Use one or the other, if you use neither or both, the resulting behavior is undefined. Generally you want to make sure that each country has max one role-level template entry targeting a role. So if you add custom AI templates for e.g. Germany you should make sure that only Germany is allowed for it, and you should also block Germany from using the generic AI templates for the same role.
- `upgrade_prio = { ... }` An MTTH style block used for weighted-random selection when the AI chooses which role to upgrade templates for. Set it to zero to prevent the AI from spending XP on upgrading templates for this role. Example: If three role-level templates `[A, B, C]` have upgrade prio `[1, 2, 1]` respectively, then the probabilities for upgrading each template is `[25%, 50%, 25%]` respectively.
- `enable = { ... }` Optional: Whether to evaluate this target template at all. Trigger with country scope. If false, the AI will pretend this target template doesn't exist.

Target template arguments:

- `reinforce_prio =` Optional: Determines the reinforcement prio of the resulting template. For example, garrison templates should use 0 (low prio) while elite templates should use 2 (high prio). Default 1 (normal prio).
- `custom_icon =` Optional: Determines whether to use a custom icon for resulting template.
- `division_names_group =` Optional: Specifies the division name group to use. By default uses the name group of the template "branched off" from.
- `upgrade_prio = { ... }` The priority of this target template. This is used to determine (deterministically, no randomness involved) which of the target templates is the "currently targeted template".
- `enable = { ... }` Optional: Whether to evaluate this target template at all. Trigger with country scope. If false, the AI will pretend this target template doesn't exist.
- `can_upgrade_in_field = { ... }` Optional: Whether to allow upgrading divisions in the field. Trigger with country scope. If false, the AI will not field-upgrade divisions matching this target template. If true, the AI will consider field-upgrading divisions matching this target template to the target template defined by 'replace_with' (assuming they have enough manpower and equipment for it).
- `target_template = { ... }` The "meat" of the target template: the actual template contents.
  - `support = { ... }` The desired support companies. The AI will try to add them to the template if allowed by research etc.
  - `regiments = { ... }` The desired line regiments. The AI will try to add them to the template if allowed by research etc.

In addition, the optional replace-with chain. If the match score is at least 'replace_at_match', then replace the currently targeted template with 'replace_with', as long as the match score between best matching template and the next target template is at least 'target_min_match':

- `replace_at_match =` Optional: Match score of this target template.
- `replace_with =` Optional: Other target template to replace currently targeted template with. Also affects fielded divisions when upgrading in the field.
- `target_min_match =` Optional: Match score between the best matching template and the target template defined by 'replace_with' has to be at least this high in order for the switch to happen.

<!-- kit:begin id="ai-templates-1193" at="section:AI_templates" -->
**Kit addition** What the 1.19.3 documentation and vanilla add for division templates.

- The documentation (headed "updated 2024-08") says the system was reworked in 2023-10 and that some old parameters are being deprecated or renamed. It names two debug commands: `imgui show ai_templates` (targeted templates and best matches) and `imgui show ai_division_production` (divisions wanted per role). [docs] `common/ai_templates/_documentation.md`.
- Vanilla has 69 role entries and 143 target templates in 15 files. Role-level keys: `role`, `upgrade_prio` (all), `available_for` (58), `blocked_for` (7) and `front_role_override = offence` (2, heavy armor for GER and SOV; the `front_armor_score` documentation mentions it). No vanilla role entry has a role-level `enable`, though the list above gives one; the documentation example also shows none [unverified]. [vanilla-confirmed 1.19.3] `common/ai_templates/*.txt`.
- Target-template keys in vanilla: `upgrade_prio` and `target_template` (143 each), `division_names_group` (54), `custom_icon` (20), `reinforce_prio` and `replace_at_match` (19 each), `replace_with` and `target_min_match` (18 each), `can_upgrade_in_field` (7), `enable` (1). [vanilla-confirmed 1.19.3] `common/ai_templates/*.txt`.
- `target_template` takes `regiments` (143), `support` (142) and `regimental_support` (114): `regimental_support = { anti_air_battery = 1 mot_fire_support = 1 }` in `templates_GER.txt`. The block is in neither the template documentation nor the list above. [vanilla-confirmed 1.19.3] `common/ai_templates/templates_GER.txt`.
- Role tokens vanilla defines: `armor`, `garrison`, `infantry`, `mountaineers`, `marines`, `paratroopers`, `militias`, `motorized`, `mobile`, `suppression`, `heavy_armor`, `anti_armor`, `mechanized_assault`, `irregular_infantry`, `rangers_role`, `hq_role`, `mega_heavy_breakthrough_role`, `super_heavy_breakthrough_role`. `role_ratio` strategies target these (313 uses). [vanilla-confirmed 1.19.3] `common/ai_templates/`, `common/ai_strategy/`.
- `infantry_1` and `infantry_2` in the example are free block names, as in the documentation's own example. Real vanilla names are like `light_armor_default_ENG` and `medium_armor_2_ENG`. [docs] `common/ai_templates/_documentation.md`.
- Triggers that read this system: `ai_has_role_template = <role>` (used in `ai_templates/generic.txt`), `ai_has_role_division`, `has_template_ai_majority_unit`. [docs] `documentation/triggers_documentation.md`.
<!-- kit:end id="ai-templates-1193" -->

### Example <a id="Example_3"></a>

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

## AI equipment <a id="AI_equipment"></a>

`/Hearts of Iron IV/common/ai_equipment/*.txt` files are used in order to define the equipment variants that the AI should aim for when assigning modules to tank or ship variants.

A role template is defined as a block within any file in the folder with the name of the block being the same as the name of the role template.
These arguments are used for role templates themselves:

- `category = <land|naval|air>` decides whether the template is used for tanks, ships or planes respectively.
- `roles = { ... }` is a list of roles that the templates would have. These can be anything, getting used for the role_ratio AI strategy. AI will try to have one variant for each role it has.
- `available_for = { ... }` restricts the countries that use this role template to the tags in the list. If unspecified, every country uses them.
- `blocked_for = { ... }` restricts the countries that use this role template from being the tags in the list. This is only needed if there is no `available_for = { ... }` block.
- `priority = { ... }` is a [MTTH block](#MTTH_blocks) that decides the 'importance' of the role template compared to other role templates for spending experience on improving. If there are several role templates with the same roles, the one with the highest priority gets used, otherwise this decides likelihood compared to role templates with different roles.

Additionally, within role templates each individual design is defined as a block with the name of the design being the name of the block. It may be anything, as long as there is no overlap.
These arguments are used within a design definition:

- `name = angry_speedboat` required to enable the equipment to be used as preset. If not defined, for example German `light_tank_artillery_2` will use `GER_light_tank_artillery_equipment_2_short` localization if defined.
- `role_icon_index = 2` is used to assign a specific role icon to a *ship*. This does not work within land equipment. The icons are defined as a part of `naval_equipment_role = { ... }` within `/Hearts of Iron IV/gfx/army_icons/army_icons.txt`.
- `priority = { ... }` is a [MTTH block](#MTTH_blocks) that decides the 'importance' of the design compared to other templates within the role template for spending experience on improving.
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
    - `tank_nsb_engine_upgrade = { ... }` is a [MTTH block](#MTTH_blocks) that assigns the AI priority to the specified upgrade dynamically.
- `requirements = { ... }` is a list of modules that the AI *must* have. This follows the same formatting as a specified module slot within a target variant's modules block: `module = tank_flamethrower`, `any_of = { ... }`, etc. However, this is not tied to a specific slot.
- `allowed_modules = { ... }` is a list of modules that the AI can use after the requirements in the target variant are met. If a module isn't here, it'll never be picked. The modules specified first take priority over the later ones.

<!-- kit:begin id="ai-equipment-1193" at="section:AI_equipment" -->
**Kit addition** What the 1.19.3 documentation and vanilla add for equipment designs.

- Vanilla has 268 design groups with 822 designs in 22 files: `category = land` 147, `naval` 81 and `air` 40. The documentation notes that naval support began in 1.6.0 and land in 1.11.0; it does not name `air`, which vanilla uses (`generic_planes.txt` and others). [vanilla-confirmed 1.19.3] `common/ai_equipment/*.txt`; [docs] `common/ai_equipment/_documentation.md`.
- `available_for` and `blocked_for`: if `available_for` is empty every country not in `blocked_for` may use the group; if it is not empty only listed countries that are not in `blocked_for` may. So `blocked_for` still applies together with `available_for`, unlike the list above suggests. `generic_planes.txt` writes `blocked_for = {GER ENG USA ITA}` with an empty `available_for = {}`. [docs] `common/ai_equipment/_documentation.md`; [vanilla-confirmed 1.19.3] `common/ai_equipment/generic_planes.txt`.
- Design keys the list above lacks: `history = yes` (820 of 822 designs; the documentation says it decides the designer folder the design appears in), `visible = no` (9), `design_team = <id>` (1, `ENG_naval.txt`), and the capitalised `Name = illustrious_class` (1) next to `name` (82). `role_icon_index` appears in 296 designs, all in naval files. [docs] `common/ai_equipment/_documentation.md` (`history`); [vanilla-confirmed 1.19.3] `common/ai_equipment/*.txt`.
- `allowed_types`, described above, is in neither the documentation nor any vanilla `ai_equipment` file. Do not rely on it [unverified]. [vanilla-confirmed 1.19.3] `common/ai_equipment/` (no match).
- `target_variant` always has `match_value`, `type` and `modules`; `upgrades` appears in 368 designs; `requirements` in 33; `enable` in 255. `upgrade = current` or `upgrade > current` inside a slot block is used 12 times, all in naval files. A slot written `<slot> = empty` fails the match for any module; `<slot> > empty` fails only an empty slot. [vanilla-confirmed 1.19.3] `common/ai_equipment/*_naval.txt`; [docs] `common/ai_equipment/_documentation.md`.
- `BHR_light_tanks` in the example is an invented group name. Roles are free tokens and also the ids of `role_ratio` strategies; vanilla naval roles include `naval_screen`, `naval_escort`, `naval_submarine`, `naval_carrier`, `naval_cruiser_light`, `naval_cruiser_heavy`, `naval_capital_bb`, `naval_capital_bc`, `naval_mine_layer` and `naval_mine_sweeper`. [vanilla-confirmed 1.19.3] `common/ai_strategy/*.txt`.
<!-- kit:end id="ai-equipment-1193" -->

### Example <a id="Example_4"></a>

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

<!-- kit:begin id="ai-navy-1193" at="bottom" -->
## Kit: AI navy goals, fleets and task forces <a id="kit-ai-navy"></a>

The goal-based naval AI replaces the older mission-priority system. It has three layers of files under `common/ai_navy/`. All of it is checked against `common/ai_navy/_documentation.md` and `common/ai_navy/taskforce/_documentation.md` [docs] and the vanilla files [vanilla-confirmed 1.19.3] (74 goals, 32 fleets, 61 task force templates, in 8 files each for goals, fleets and task forces: a generic file plus ENG, FRA, GER, ITA, JAP, SOV, USA).

**Goals** (`ai_navy/goals/goals_<TAG>.txt`). A goal is a type of operation; an objective is the goal applied to a target. All active objectives of a country are scored and executed from the best down. Score of an objective = `min_priority` + (`max_priority` - `min_priority`) times its importance, where importance is a value from 0 to 1. Doc example: naval invasion support with priorities 5 to 10 and importance 0.8 scores 9.0. [docs] `common/ai_navy/_documentation.md`.

```text
ENG_naval_invasion_support = {
    objective_type = naval_invasion_support
    available_for = { ENG }
    min_priority = 4
    max_priority = 14
}
```

Example: [vanilla-confirmed 1.19.3] `common/ai_navy/goals/goals_ENG.txt`.

- Keys: `objective_type`, `min_priority` and `max_priority` (all 74 goals), `available_for` (64) and `blocked_for` (10). With `available_for` present the goal is off for every other country; `blocked_for` switches it off for the listed ones. [docs]
- The documentation lists six objective types: `naval_invasion_support`, `naval_invasion_defense`, `mines_sweeping`, `coast_defense`, `convoy_protection`, `convoy_raiding`. Vanilla also uses `naval_dominance`, `mines_planting`, `training` (8 goals each) and `naval_blockade` (2). [docs]; [vanilla-confirmed 1.19.3] `common/ai_navy/goals/`.
- Debug with the console command `imgui show ai_navy`. [docs]

**Task force templates** (`ai_navy/taskforce/<TAG>_taskforce_templates.txt`). A template says which ships a task force wants and for which mission.

```text
GER_ConvoyRaiding_1 = {
    allowed = { original_tag = GER }
    ai_will_do = { factor = 1 }
    keep_updated = yes
    mission = { convoy_raiding }
    min_composition = { submarine = { amount = 4 } }
    optimal_composition = { submarine = { amount = 6 } }
}
```

Example: [vanilla-confirmed 1.19.3] `common/ai_navy/taskforce/GER_taskforce_templates.txt` (spaced onto fewer lines).

- Documented keys: `allowed` (country scope), `ai_will_do` (a weight, 0 or lower means the AI never uses the template), `mission` (a list, currently limited to one entry), `min_composition` and `optimal_composition`. [docs] `common/ai_navy/taskforce/_documentation.md`
- The documentation writes compositions as `carrier = 1`. Vanilla writes every ship type as a block with `amount`, and 24 composition entries add `role = 4`: `destroyer = { amount = 2 role = 4 }`. `keep_updated = yes` is set on 25 of the 61 templates and is not documented. [vanilla-confirmed 1.19.3] `common/ai_navy/taskforce/*.txt`.
- Ship types in vanilla compositions: `destroyer`, `light_cruiser`, `heavy_cruiser`, `battleship`, `battle_cruiser`, `submarine`, `carrier`. Missions in vanilla: `naval_patrol` (17), `convoy_raiding` (14), `naval_strike` (11), `mines_planting` (8), `convoy_escort` (8), `naval_invasion_support` (3). [vanilla-confirmed 1.19.3] `common/ai_navy/taskforce/*.txt`.

**Fleet templates** (`ai_navy/fleet/<TAG>_fleet_templates.txt`). Not covered by either documentation file. A fleet lists task force template ids and how many of each:

```text
generic_dominance_fleet_1 = {
    required_taskforces = { StrikeForce_1 = 1 PatrolReconForce_1 = 2 }
    optional_taskforces = { StrikeForce_1 = 1 PatrolReconForce_1 = 1 }
}
```

Example: [vanilla-confirmed 1.19.3] `common/ai_navy/fleet/generic_fleet_templates.txt` (shortened). Of 32 fleets, 24 have `required_taskforces`; all have `optional_taskforces`. The meaning of required and optional is read from the names [unverified].

Strategies that feed this system: `naval_dominance`, `naval_blockade`, `coast_defense`, `convoy_raiding_target`, `naval_invasion_dominance_weight`, `naval_invasion_support_priority`, `naval_mission_threshold`, `strike_force_home_base`. See `ai-types-missing`.
<!-- kit:end id="ai-navy-1193" -->

<!-- kit:begin id="ai-faction-theaters-1193" at="bottom" -->
## Kit: AI faction theaters <a id="kit-ai-faction-theaters"></a>

`common/ai_faction_theaters/ai_faction_theaters.txt` tells the AI which theaters a faction leader creates and which members it assigns. Keys per theater, from the documentation: `name` (loc key, faction leader loc scope), `ai_will_do` (how likely the AI creates it, scope the acting country), `cancel` (when the AI drops its theater), `regions` (strategic region ids, the area must be connected), `can_skip_first_region` and `preferred_countries` (priority list of members). By default the first region must be available to create the theater; `can_skip_first_region = yes` lets at least one available region suffice. [docs] `common/ai_faction_theaters/_documentation.md`.

Vanilla defines 30 theaters (`western_europe`, `eastern_europe`, `barbarossa_north`, `north_africa`, `chinese_coastline`, `central_pacific` and others). Every theater has `name`, `regions`, `cancel` and `ai_will_do`; only 3 use `preferred_countries` (for example `GER SLO`) and none use `can_skip_first_region`. [vanilla-confirmed 1.19.3] `common/ai_faction_theaters/ai_faction_theaters.txt`.

```text
western_europe = {
    name = theater_western_europe
    regions = { 19 5 7 208 6 18 1 275 20 42 21 }
    cancel = { has_war = no }
    ai_will_do = { base = 0 modifier = { add = 1 capital_scope = { is_on_continent = europe } } }
}
```

Example: [vanilla-confirmed 1.19.3] `common/ai_faction_theaters/ai_faction_theaters.txt` (the vanilla `cancel` and `ai_will_do` are longer; this keeps the shape). The `name` key `theater_western_europe` is localised in `localisation/english/factions_l_english.yml`.

Related defines (`NDefines.NFactions`): `MAX_FACTION_THEATERS` 4, `AI_THEATER_CREATION_PENALTY` 2.5 (each existing theater lowers the creation chance linearly), `AI_FACTION_THEATER_TEMPLATE_SELECTION_RANDOMNESS` 1, `AI_FACTION_THEATER_COMMANDER_SELECTION_RANDOMNESS` 1, `FACTION_UNLOCK_COMMANDER_COST` 1 (faction initiative). The AI spends that initiative through the strategy `spent_faction_initiative_priority` with `id = unlock_faction_commander`. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`; [docs] `common/factions/_documentation.md`. See [Faction modding](<Faction modding - Hearts of Iron 4 Wiki.md>).
<!-- kit:end id="ai-faction-theaters-1193" -->

<!-- kit:begin id="ai-docs-surface-1193" at="bottom" -->
## Kit: Documented AI script surface <a id="kit-ai-docs-surface"></a>

Items from the game documentation that read or steer the AI and that the page above never names.

| Name | Kind | What it does |
| --- | --- | --- |
| `is_ai` | trigger | True if the country is AI controlled |
| `ai_has_role_template`, `ai_has_role_division` | triggers | The AI country has a template, or fielded divisions, for a role |
| `has_template_ai_majority_unit` | trigger | The country has a division template whose majority unit matches, counted by AI priorities rather than visually |
| `ai_wants_divisions` | trigger | Compares with the number of divisions the AI wants |
| `ai_irrationality` | trigger and variable | The AI irrationality value |
| `ai_liberate_desire` | trigger | The liberation desire toward a given country |
| `ai_message` | effect | Documented only as "ai message... ?", no usable description |
| `ai_badass_factor`, `ai_call_ally_desire_factor`, `ai_desired_divisions_factor`, `ai_get_ally_desire_factor`, `ai_join_ally_desire_factor`, `ai_license_acceptance` | modifiers | Category `ai`; listed without description |
| `ai_focus_<x>_factor` | modifiers | Nine of them, see [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) |
| `ai_strategy_<type>@<country>` | dynamic variable | Value of a strategy toward a country, for example `GER.ai_strategy_conquer@ENG`. Exists for `alliance`, `antagonize`, `befriend`, `conquer`, `consider_weak`, `contain`, `declare_war`, `dont_defend_ally_borders`, `force_defend_ally_borders`, `ignore`, `ignore_claim`, `invade`, `prepare_for_war`, `protect`, `send_volunteers_desire`, `support`, `influence`, `occupation_policy`, `activate_crypto`, `decrypt_target` |
| `ai_attitude_<x>_weight@<country>`, `ai_attitude_wants_<x>`, `ai_attitude_is_threatened` | dynamic variables | Weights of an AI attitude toward a country (allied, friendly, hostile, neutral, outraged, protective, threatened), and flags such as `ai_attitude_wants_ally`, which is 1 if the AI wants an ally; siblings exist for antagonize, ignore, protect and weaken |

All rows above: [docs] `documentation/triggers_documentation.md`, `effects_documentation.md`, `modifiers_documentation.md`, `dynamic_variables_documentation.md`.

Console commands for AI work. All rows: [docs] `documentation/console_commands_documentation.md`; several are marked "Not available in release build".

| Command | Use |
| --- | --- |
| `aiview` | Show AI debug info |
| `ai_accept` (alias `yesman`) | Toggle the AI accepting every diplomatic request |
| `ai_invasion` | Toggle AI naval invasions |
| `ai_force_equipment`, `ai_force_template` | Make the AI spend army XP only on equipment designs, or only on templates |
| `ai_idea_desire_log`, `ai_pp_log`, `ai_research_log` | Print AI idea desire, political power use and research choices to the log (the last is not in release builds) |
| `ai_dump`, `ai_front_dump`, `ai_front_id`, `ai_trace` | Dump AI data and fronts or open the trace window; not in release builds |
| `enable_ai`, `disable_ai`, `human_ai` | Switch the AI on or off, or give human countries AI control |
| `emulate_ai_operative_assignment` | Log what the operative AI would do this tick |
| `imgui show ai_templates`, `imgui show ai_division_production`, `imgui show ai_navy` | Debug views for templates, wanted divisions and naval goals. [docs] the AI template and AI navy documentation files |
<!-- kit:end id="ai-docs-surface-1193" -->

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<Collection modding - Hearts of Iron 4 Wiki.md>) • [Game rule modding](<Game rule modding - Hearts of Iron 4 Wiki.md>) • [Intelligence operation modding](<Intelligence operation modding - Hearts of Iron 4 Wiki.md>) • [Map mode modding](<Map mode modding - Hearts of Iron 4 Wiki.md>) • [Occupation and resistance modding](<Occupation and resistance modding - Hearts of Iron 4 Wiki.md>) • [Peace conference modding](<Peace conference modding - Hearts of Iron 4 Wiki.md>) • [Raid modding](<Raid modding - Hearts of Iron 4 Wiki.md>) • [Script constant modding](<Script constant modding - Hearts of Iron 4 Wiki.md>) • [Special project modding](<Special project modding - Hearts of Iron 4 Wiki.md>)
