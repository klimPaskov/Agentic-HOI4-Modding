# Idea modding

Ideas are a static way to apply modifiers to a country, notably including national spirits, laws, designers, officer corps spirits, and hidden ideas. Ideas themselves are defined in `/Hearts of Iron IV/common/ideas/*.txt`, while idea categories are defined in `/Hearts of Iron IV/common/idea_tags/*.txt`

## National spirit creation

Spirits are created in `/Hearts of Iron IV/common/ideas/*.txt`. An example of a file with empty spirits, without modifiers yet still applicable if added via `add_ideas = idea_name`, is

```text
ideas = {
    country = {
        my_idea_1 = {
        }
        my_idea_2 = {
        }
    }
}
```

In this case, `ideas = { ... }` encompasses each idea in the file, necessary to include due to the engine consraints. Meanwhile, `country = {}` is an idea category, which is why the game would recognise `my_idea_1` and `my_idea_2` as spirits rather than laws or designers, which are also ideas.

### Localisation

Localisation for ideas is defined in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file **encoded in UTF-8-BOM**, assuming the English language. If an idea does not have a name, the game uses the country's name-list in `/Hearts of Iron IV/common/names` to create a random name. This, however, does not apply to national spirits, where it uses the idea's ID. An idea can have both a name and a description that appears when hovering over it. Their localisation entries are defined as such, taking ZZZ_example_idea as an example:

```yaml
l_english:
 ZZZ_example_idea: "Idea's name"
 ZZZ_example_idea_desc: "Idea's description"
```

`name = new_idea_name` assigns the idea's name to use a different localisation key. This can be useful if you plan to modify an idea by swapping it multiple times, ensuring that you needn't create a duplicate localisation entry for every instance of the idea. This will get defined in a localisation file similarly:

```yaml
l_english:
 new_idea_name: "New idea's name"
 new_idea_name_desc: "New idea's description"
```

### Picture

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
In order to add animation, a [frameAnimatedSpriteType](graphical_asset_modding.md#frameanimatedspritetype) is used.

**It's never mandatory to copy a base game file to change a sprite**. If there are duplicate definitions of a sprite with the same name in different files, the game will prioritise the one that would be [evaluated later, based on the filename](modding.md#loading-files), and the older sprite will be ignored in entirety. This can be ensured by beginning the replacement file's name with a symbol late in the ASCII character table. Typically the lowercase letter 'z' is used for this purpose. For example, to change the amount of frames in `GFX_idea_traits_strip` to 10, it is possible to define a sprite with that name with 10 frames in the mod's `modname/interface/zz_replace.gfx` file instead of copying over the base game file.
Since most .gfx files define integral parts of the user interface, copying them over can lead to the mod's loaded files missing sprites upon a major game update, which would appear in-game as the default image, which is the error dog by default. As to ease the burden of needing to check the interface files, it's best to never copy over .gfx files, unless more additions would be actively harmful to the mod, such as with `interface/subuniticons.gfx`

By default, an idea uses a sprite that is the same as the idea's name, but with `GFX_idea_` prepended in the beginning. For example, an idea with the name of `my_idea_1` will use the sprite with the name of `GFX_idea_my_idea_1`.

This is possible to change using the `picture = my_sprite` attribute within the idea (**The game still checks for GFX_idea_ideaname and will use it if it finds it, even if a `picture =` argument is used**). **The game still inserts a prefix of `GFX_idea_` to the argument** to decide the sprite that should be used, e.g. `picture = XYZ` leads to `GFX_idea_XYZ` being used as the sprite. If the game cannot find a sprite with the name it expects, the ![Unknown.png](media/idea_modding_e610dc0262__img1.png) default icon will be used instead.
The prefix being inserted means that, most of the time, `picture = GFX_XYZ` (which makes `GFX_idea_GFX_XYZ` get used as the sprite) or `picture = idea_XYZ` (which makes `GFX_idea_idea_XYZ` get used as the sprite) will lead to the game expecting a sprite that doesn't exist and that sprites that do not follow the `GFX_idea_XYZ` naming pattern cannot be used as idea pictures.

If the `texturefile` within the sprite is incorrect, the idea will be invisible in the country politics view, yet still apply the modifiers. Ensure that the idea is stored with the same folder path location, the same filename (including the extension), and that the right folder separator is used.

It is also possible to make the picture depend on the `graphical_culture_2d` of the country, defined in the `/Hearts of Iron IV/common/countries/*.txt` file. This is done by appending the name after the picture's name, separated by an underscore. For example, a sprite with the name of `GFX_idea_my_picture_middle_eastern_2d` in its definition will show up instead of `GFX_idea_my_picture` for countries that have the `middle_eastern_2d` 2D graphical culture.

How vanilla fills `picture`, counted over the 6,515 ideas in the 213 files of `common/ideas/`.

- 6,110 ideas set `picture`. 6,088 of them give the bare name (`picture = new_economic_policy`), and 6,046 of those match a declared sprite named `GFX_idea_<value>` (here `GFX_idea_new_economic_policy` in `interface/ideas.gfx`). What matters is that a sprite with that full name is declared in some loaded `.gfx` file; vanilla also declares idea sprites in `dlc/*/interface/*.gfx`.
- 22 vanilla ideas write a full name (`picture = GFX_idea_...`). For 15 of them a sprite called `GFX_idea_<idea id>` also exists, so the name fallback would find a sprite anyway. The other 7 only work if the engine accepts a full sprite name. Whether it does is unverified, so write the bare name.
- 405 ideas set no `picture`. 272 of them have a sprite called `GFX_idea_<idea id>`, and 119 of the rest are in `hidden_ideas`, which never show.
- 385 ideas set a bare `picture` that has its own sprite and also have a sprite named after the idea id. The files do not show which of the two the game displays.
- `GFX_idea_unknown` is declared in `interface/countrydiplomacyview.gfx` (texture `gfx/interface/ideas/idea_unknown.dds`) and is the placeholder icon several vanilla GUI files use. That the engine falls back to it for an idea with no usable sprite is unverified.
- Culture variants exist in vanilla: 160 sprites end in `_2d`, all for `generic_*` pictures, 20 for each of `asian_2d`, `commonwealth_2d`, `eastern_european_2d`, `middle_eastern_2d`, `sami_2d`, `southamerican_2d`, `western_european_2d` and 19 for `african_2d`. The same eight values are the `graphical_culture_2d` values in `common/countries/`; one sprite uses `middle_african_2d`, which no country uses.

### Implementation

A spirit can only be added manually, using an [effect](effects.md). `add_ideas = idea_name` within an effect block (Such a focus completion reward), while `remove_ideas = idea_name` will remove it.

In order to swap two ideas and have the game show the modifiers, `swap_ideas` is used. **There is no way to directly modify an idea**, however in case the 2 swapped spirits have the same name in localisation, this will show up in-game as modifying the idea. `swap_ideas` is used as the following:

```text
swap_ideas = {
    remove_idea = old_idea
    add_idea = new_idea
}
```

In most cases, it's enough to create multiple ideas and swap between them, such as if there's a direct progression of several stages (Scripted effects can be used to create one series of conditional statements and re-use them each time it's needed). If creating multiple ideas is too infeasible, such as if there are several progressions that would need to be modified, [dynamic modifiers](modifiers.md) allow variable modifier values, but they only accept modifiers (not unrelated attributes such as research or equipment bonuses) and are harder to work with due to no hot-reloading.

In order for a spirit to last for a period of time, the `add_timed_idea` effect is used as such:

```text
add_timed_idea = {
    idea = my_timed_idea
    days = 365
}
```

[modify_timed_idea](effects.md) can be used to extend or speed up the timer as needed.

In order for a country to start with the idea, the file in `/Hearts of Iron IV/history/countries/` for that country serves as an effect block that decides the starting historical information. Using [add_ideas](effects.md), usually in the expanded form to assign multiple ideas at once, in there will enforce it starting with the idea. In order for the idea to show up in country selection, the [bookmark is edited](bookmark_modding.md) to include the idea within its `ideas = { ... }` block for the country's entry.

Idea effects and triggers in 1.19.4.1. All of them run in country scope.

| Name | Kind | Syntax and notes |
| --- | --- | --- |
| `add_ideas`, `remove_ideas` | effect | `add_ideas = id` or `add_ideas = { id_a id_b }`. Vanilla writes `add_ideas` 2,899 times as a single value and 473 times as a block. |
| `swap_ideas` | effect | `swap_ideas = { remove_idea = a add_idea = b }`. The documentation also lists optional `days` (duration of the new idea) and `add_days` (change to that duration), but all 2,294 vanilla uses have only the two required keys. The documentation's syntax line says `swap_idea`; no vanilla file uses that spelling. |
| `add_timed_idea` | effect | `add_timed_idea = { idea = id days = 30 }`. `years`, `months` and `days` can be combined, at least one is required, and each accepts a variable. Vanilla: 1,730 uses with `days`, 4 with `months`. |
| `modify_timed_idea` | effect | `modify_timed_idea = { idea = id days = 60 }` lengthens the timer; a negative value shortens it. Same `years`, `months`, `days` keys. 16 vanilla uses. |
| `remove_ideas_with_trait` | effect | `remove_ideas_with_trait = trait_id`. 1 vanilla use (`events/ElectionEvents.txt`). |
| `show_ideas_tooltip` | effect | `show_ideas_tooltip = id` prints an idea's tooltip inside an effect tooltip; vanilla uses it for advisor ideas in focus rewards. 1,232 vanilla uses. |
| `has_idea` | trigger | `has_idea = id`. 7,414 vanilla uses. |
| `has_idea_with_trait` | trigger | `has_idea_with_trait = trait_id`. 326 vanilla uses. |
| `has_allowed_idea_with_traits` | trigger | `{ idea = trait_id characters = yes }`, with optional `limit` and `ignore`. 15 vanilla uses, all in `common/ideas/zzz_generic.txt` and `history/general/generic_advisors.txt`. `has_available_idea_with_traits` is documented the same way but unused in vanilla. |
| `amount_taken_ideas` | trigger | `{ amount < 3 slots = { political_advisor } }`, with optional `categories = { military_staff }`. Does not count national spirits, hidden ideas or categories with `law = yes`. 137 vanilla uses. |

### Modifiers

[Modifiers](modifiers.md) are applied continuously as long as the spirit is applied to a country. Alongside modifiers, the spirit can also add a bonus to a technology category or modify an equipment archetype. The spirit can only apply modifiers towards the country that has the spirit, there is no way to scope into a different country. **Each of these attributes is entirely separate within the idea** and so each one should be located directly inside of the idea. For example, defining `research_bonus` inside of `modifier = { ... }` is erroneous, since `research_bonus` is an attribute of the idea rather than a modifier.

`modifier = { ... }` stores the regular modifiers, applied to the country with the spirit. A modifier block can list multiple modifiers, and negatives are also allowed. **Variables do not work in this section**: instead, use [dynamic modifiers](modifiers.md). A typical example of a modifier block is the following:

```text
modifier = {
    political_power_cost = 0.1
    stability_factor = -0.2
}
```

`targeted_modifier = { ... }` is for using [modifiers targeted towards a different country](modifiers.md#targeted-modifiers). The target is specified as `tag = ABC`, where ABC represents the target's tag. These are still applied towards the country with the spirit, but their effect is targeted towards a different country. For example, the following block will give the country with the idea a 10% attack bonus against ![Flag of Afghanistan](media/idea_modding_e610dc0262__img2.png) Afghanistan:

```text
targeted_modifier = {
    tag = AFG
    attack_bonus_against = 0.1
}
```

`research_bonus = { ... }` grants the country a boost to researching a specific technology category. An unsorted list of technology categories can be found in `/Hearts of Iron IV/common/technology_tags/` or, if desiring to know which technologies exactly are assigned to each category, individual technologies can be checked in `/Hearts of Iron IV/common/technologies/`. The following example would provide a +10% bonus to researching destroyers and a -20% bonus to artillery:

```text
research_bonus = {
    dd_tech = 0.1
    artillery = -0.2
}
```

`equipment_bonus = { ... }` applies the bonuses towards an equipment archetype or a type of equipment archetypes. By default, the bonus is not granted immediately, but rather requiring to research a new tech first, which is how it's done within designer ideas. This can be prevented by adding `instant = yes` inside of the equipment archetype within the equipment bonus. Equipment archetypes are defined in `/Hearts of Iron IV/common/units/equipment/*.txt`, which is where you can also find what can be applied to them. The name of the block within the `/Hearts of Iron IV/common/units/equipment/*.txt` file would be the archetype, while `type = { ... }` or `type = archetype_type` provides the types that the equipment archetype has. The following example will modify the cost to produce equipment within the `artillery` type (including artillery, rocket artillery, and tank artillery) by -20%, applying immediately, as well as increasing soft attack of any infantry equipment researched after the spirit was added by 10%:

```text
equipment_bonus = {
    artillery = {
        instant = yes
        build_cost_ic = -0.2
    }
    infantry_equipment = {
        soft_attack = 0.1
    }
}
```

`rule` modifies the set of rules that decide what the country is allowed to do. This usually includes diplomatic options (such as peace conference options or being called to war). They show up in the tooltip only if the rule differs from the value without the idea, e.g. `can_create_factions = no` will usually not appear in the tooltip as countries are already unable to create a faction by default.

```text
rule = {
    can_join_factions = no
    can_send_volunteers = yes
}
```

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

What vanilla puts inside idea blocks, counted over 4,611 `modifier` blocks and 6,515 ideas in `common/ideas/`.

- Every key in a vanilla `modifier` block is a numeric modifier except two: `custom_modifier_tooltip = LOC_KEY` (183 uses) adds an extra tooltip line from a localisation key, and `hidden_modifier = { ... }` (2 uses, `common/ideas/czechoslovakia.txt` and `italy.txt`) wraps modifiers that apply without being listed. `custom_modifier_tooltip` is the only non-numeric scalar.
- `research_bonus` is never inside `modifier` (0 of 4,611 blocks). It is an idea-level key: 1,086 ideas use it, with 37 different technology category names. `equipment_bonus` is also idea-level (653 blocks in 637 ideas); `instant = yes` appears 945 times inside it.
- `targeted_modifier` (481 uses) holds `tag = TAG` (479 blocks) and numeric modifiers; the only other non-numeric key is `custom_modifier_tooltip` (3 blocks).

The `rule` table above, checked against vanilla and the game files.

- 47 vanilla ideas use a `rule` block. They use 8 rule names: `can_send_volunteers` (20 entries), `can_access_market` (8), `can_create_factions` (6), `can_decline_call_to_war` (6), `can_join_factions` (4), `can_join_opposite_factions` (3), `can_boost_other_ideologies` (2), `can_guarantee_other_ideologies` (1). One block also has `desc`, which is a description key, not a rule.
- `can_join_factions_not_allowed_diplomacy` is in no vanilla script, so do not rely on it. (unverified) The idea loader reports it: in an idea's `rule` block it drew "unknown rule 'can_join_factions_not_allowed_diplomacy'", the same message as a made-up name.
- `can_declare_war_without_wargoal_when_in_war`, `can_not_build_buildings` and `can_occupy_non_war` are in `hoi4.exe` (unverified) but in no active vanilla script (the first appears once, in a commented-out line in `common/national_focus/uruguay.txt`). All three load without an "unknown rule" line in an idea's `rule` block, so they are known rule keys. Whether they have their effect as idea rules was not read: the `has_rule` readouts failed in that run, and no error is not proof that a rule works.
- The same names can be set at runtime. `set_rule = { desc = LOC_KEY can_not_declare_war = yes }` adds a rule to the country in scope and overrides the other sources, `clear_rule = { can_not_declare_war = yes }` removes a rule that `set_rule` added, and `has_rule = can_puppet` tests one. Vanilla: `set_rule` 502 uses, `clear_rule` 2, `has_rule` 68.
- `add_relation_rule_override` sets a rule for one target country (`target = TAG`) or for every country a named trigger matches (`trigger = name`), with an optional `usage_desc`. The documentation says only `can_send_volunteer` (sic) and `can_access_market` are supported there. 47 vanilla uses.
- The table is not the full list of rule names: ideologies use a `rules` block (`can_force_government`, `can_puppet`, `can_lower_tension`, `can_host_government_in_exile`) and one special project uses `set_rule = { can_use_underway_replenishment = yes }`.

### Effects

A spirit can be set to apply [effects](effects.md) when added or removed. This is done, respectively, with `on_add` and `on_remove` effect blocks, looking like the following example:

```text
on_add = {
    add_stability = 0.1
}
on_remove = {
    add_political_power = -50
}
```

The effects will only get executed if the idea is added after the game has already started: if done via a history file or a bookmark's `effect = { ... }` block, the effects will not be executed. In that case, it's needed to replicate the effects given when adding the idea within the same effect block that adds the idea.

### Cancellation

A spirit can be set to automatically cancel itself once a set of [triggers](triggers.md) is met. This is done with the `cancel` block. A cancellation will also trigger the `on_remove` effect block in the idea if one is present. This will look like the following:

```text
cancel = {
    has_political_power > 50
}
```

### Additional arguments

Another trigger block that can go into an idea is `allowed_civil_war = { ... }`. When starting a civil war, this is evaluated for each side, and the spirit will only appear for sides where this is true. For instance, a `has_government = democratic` will ensure that only the ![Democracy](media/character_modding_cee5ae9645__img1.png)Democratic side in a civil war will obtain the spirit. **By default, always false, leading to the spirits disappearing when a civil war starts.** [Setting it to be always true](triggers.md) can be preferred over the default, making it appear for both sides.

`do_effect = { ... }` is a trigger block that assigns the necessary conditions for the idea to apply its modifiers. If false, the modifiers (including research and equipment bonuses) will not apply, but the idea will not be removed.

### Full idea file example

```text
ideas = {
    country = { # Necessary for the game to consider them spirits rather than a different idea type.
        my_spirit = {
            picture = my_picture        # Using GFX_idea_my_picture
            modifier = {
                training_time_factor = -0.1
            }
            targeted_modifier = {
                tag = QAT
                defense_bonus_against = 0.2
            }
            research_bonus = {
                infantry = 0.1
            }
            equipment_bonus = {
                infantry_equipment = {
                    instant = yes
                    defense = 0.2
                }
            }
            rule = {
                can_join_factions = no
            }
        }
        my_spirit_2 = {        # Using GFX_idea_my_spirit_2
            allowed_civil_war = {
                has_government = democratic         # Only appear in a civil war for the democratic side.
            }
            cancel = {
                democratic > 0.6
            }
            on_add = {
                add_popularity = {
                    ideology = democratic
                    popularity = 0.2
                }
            }
            on_remove = {
                if = {
                    limit = {
                        democratic > 0.6
                    }
                    start_civil_war = {
                        ideology = democratic
                        size = 0.6
                    }
                }
            }
            do_effect = {
                NOT = {
                    has_government = democratic
                }
            }
            modifier = {
                democratic_drift = 0.005
            }
        }
    }
}
```

## Other idea categories

Non-spirit ideas can use everything that can be within spirits, however there are more arguments that make sense to be added in them that do not do anything in spirits or don't have any reason to be added.

### Hidden ideas

Hidden idea are exactly the same as regular spirits in every aspect in regards to creation, except for the fact that they have to be defined within the `hidden_ideas` idea category instead of using `country`. This will ensure that the idea will be hidden and not show up in the spirit container. However, it can still make sense to create localisation for them: If a hidden idea cancels automatically, the pop-up will show up, and hovering over certain elements (Such as the stability counter or research speed) will show each idea that modifies it.

`hidden_ideas` is a category in `common/idea_tags/00_idea.txt` with `hidden = yes`, `cost = 0`, `removal_cost = -1` and `ledger = hidden`. Vanilla has 291 ideas in 28 `hidden_ideas` blocks; 171 of them still set a `picture`, which is never shown.

### Idea category arguments

These arguments are used within the idea category within the `/Hearts of Iron IV/common/ideas/*.txt` file.

`designer = yes` marks the entire category as designer ideas. This is primarily used for AI.
`law = yes` marks the entire category as laws. This is primarily used for AI.
`use_list_view = yes` marks the entire category to use a list view for selecting the idea, akin to how the base game treats laws.

These will look in the idea file like the following:

```text
ideas = {
    my_law_category = {
        law = yes
        use_list_view = yes
        my_law_1 = {
        }
        my_law_2 = {
        }
    }
}
```

In vanilla, `designer = yes` always sits on the category block, never on an idea: 161 category blocks in 51 files, 0 ideas. `law = yes` is on 4 category blocks (`economy` twice, `trade_laws`, `mobilization_laws`) and `use_list_view = yes` on 3.

### Additional arguments

This assumes that the idea is of the type that can be selected in-game, such as a law or a designer.

`allowed` is a [trigger](triggers.md) block that checks only at the game's start or when loading a save, primarily used to restrict an idea to a country (As `tag = BHR` or `original_tag = POL`) and/or a DLC (As `has_dlc = "One Step Back"`). If an idea's allowed is unfulfilled, it will never appear within the selection unless it becomes true on the save being reloaded; however, manual assignment via `add_ideas` bypasses the check. If left out, assumes to be always allowed. **This only checks once!**

`allowed_to_remove` is a trigger block that details when exactly you can remove the idea, changing it to a different one in the category. This is checked continuously, unlike `allowed`.

`visible` is a trigger block that continuously checks every frame if allowed was met, required to make the idea be visible in the decision selection screen. It is preferable to put country or DLC checks into allowed instead.

`available` is a trigger block that continuously checks every frame if visible was met, required to be possible to actually take the idea. If false, the idea will remain visible, but will be greyed out and be impossible to take. This is applied on top of the political power cost.

`cost = 123` is the price in political power it takes to add the idea. This becomes 150 political power if not set`[a]`.

`removal_cost = 123` is the price in political power it takes to remove the idea. If set to -1, the idea cannot be removed manually. Defaults to 0 if not set.

`level = 2` is used in ideas to create the escalating price, akin to the recruitment laws. If you have the law with the level of 1, changing to level 3 will require the cost of the idea with the level 2 in addition to the level 3, and vise-versa.

`traits` is a block of traits that are assigned to this idea, defined in `/Hearts of Iron IV/common/country_leader/*.txt`, also granting a static modifier and showing up near the idea.

`ledger` decides which intelligence ledger the idea will be assigned to. This is primarily a leftover now applying to the [character](character_modding.md) system, but this can still be used in officer corps spirits. Possible values are `army`, `air`, `navy`, `military` (Appearing on each of the prior ledgers), `civilian`, `all`, and `hidden`.

The default `cost` and `removal_cost` come from the idea's category, so they are not always 150 and 0. Table:

| Category | Default `cost` | Default `removal_cost` |
| --- | --- | --- |
| `government`, `research_production`, `military_staff` | 150 | 0 |
| `country` (national spirits), `hidden_ideas` | 0 | -1 |
| `academy_spirit`, `naval_academy_spirit` | 20 | -1 |
| `army_spirit`, `navy_spirit` | 35 | -1 |
| `division_command_spirit`, `naval_command_spirit`, `air_force_academy_spirit`, `air_force_spirit`, `air_force_command_spirit` | 50 | -1 |

An idea's own `cost` or `removal_cost` replaces the default. 3,730 of the 3,767 vanilla ideas that set `removal_cost` write `-1` (not removable by hand) and the other 37 write `10`, all in the `industrial_concern` and manufacturer slots.

Vanilla use of idea keys, including three the page does not list (`ai_will_do`, `default`, `cancel_if_invalid`).

| Key | Vanilla use |
| --- | --- |
| `ai_will_do` | 1,052 ideas with 1,055 blocks (three ideas write it twice): laws, advisors, designers and officer corps spirits. Body is `factor = n` alone (857) or `base = n` alone (63), and the other 135 blocks add `modifier` blocks. |
| `default = yes` | 5 ideas: `civilian_economy`, `export_focus`, `volunteer_only`, `ETH_chitet_law`, `ETH_chitet_law_peace_time`. What it does is not stated in the files. It does not refill an empty slot, see the note below the table. Any other engine effect of `default = yes` is unverified. |
| `cancel_if_invalid = no` | 31 laws in `economy`, `trade_laws` and `mobilization_laws`; the value is always `no`. Its exact effect is not stated in the files. (unverified) In a test, a law with `cancel_if_invalid = no` stayed after its condition failed, while the same law with the default was removed within a day (both present right after the flag was set, only the `no` law at day 1 and day 2). Only the first two days were read, and a stand-in country was used. |
| `level` | 11 ideas, all in `mobilization_laws`, with values 1 to 7. |
| `ledger` | 475 ideas. All 234 `high_command` and all 145 `theorist` ideas set it, because those two slots are `invalid` in `slot_ledgers`; the officer corps spirits set it too. Values used: `army`, `navy`, `air`. |
| `traits` | 2,013 ideas. 2,009 are in the advisor, chief, theorist, designer and industrial concern slots; 4 are national spirits (`george_v`, `ENG_george_vi`, `HOL_wilhelmina`, `SWE_gustaf_v_idea`). |

`default = yes` does not refill an empty slot. GER started with the economy law `partial_economic_mobilisation`, the console `add_ideas war_economy` replaced it ("Added 1 ideas"), and the effect `remove_ideas = war_economy` then removed it and left no economy law, so the politics view showed "Click to add Economy Law" even though `civilian_economy` has `default = yes`. The console `remove_ideas war_economy` printed "Removed 0 ideas" and the law stayed.

### Example

```text
ideas = {
    law_category = {
        law = yes
        use_list_view = yes
        my_law = {
            allowed_to_remove = {
                num_of_civilian_factories > 10
            }
            removal_cost = 100
            cost = 100
            level = 3
            modifier = {
                production_speed_industrial_complex_factor = 0.2
            }
        }
    }
    designer_category = {
        designer = yes
        my_designer = {        # No cost is defined, defaults to 150
            allowed = {
                tag = QAT
            }
            visible = {
                has_tech = infantry_weapons1
            }
            available = {
                has_equipment = {
                    infantry_equipment > 1000
                }
            }
            traits = { infantry_equipment_manufacturer }
        }
    }
}
```

## Categories

Idea categories are defined in any `/Hearts of Iron IV/common/idea_tags/*.txt` file. All categories will be contained in the `idea_categories` top element and can contain the following arguments:

- `slot` is a proper idea category slot. This is what shows up in the GUI in the politics view menu, and this is what ideas have to have as their category in their definition.
- `character_slot` is a [character](character_modding.md) slot. Ideas can also be defined to use this slot and it will show up in the GUI like a regular idea slot, however.
- `cost` is the default price in political power to add an idea within one of the slots of this category. This is applied if the idea doesn't have one.
- `removal_cost` is the default price in political power to remove an idea within one of the slots of this category.
- `ledger` is the intelligence ledger defined to ideas in this category, unless overridden within the slot, idea, or character. Possible values are `army`, `air`, `navy`, `military` (Appearing on each of the prior ledgers), `civilian`, `all`, and `hidden`. Additionally, `invalid` can be used, forcing the ledger to be defined one level lower.
- `hidden` is a boolean value making this category not show up in the GUI. Optional, defaults to no.
- `politics_tab` is a boolean value making this category show up in the politics tab. Optional, defaults to yes.

This will look like the following:

```text
idea_categories = {
    my_category = {
        slot = my_slot
        character_slot = my_character_slot
        cost = 30
        removal_cost = 10
        ledger = hidden
    }
}
```

The category will then be used by the idea via the slot (which allows mapping an idea to a category)
The file also includes slot_ledgers, which distributes idea slots to intelligence ledgers individually, which will take priority over the idea category's ledger. An example of it being used is

```text
slot_ledgers = {
	XXX_idea_slot = civilian
	ZZZ_idea_slot = invalid
}
```

Invalid will require specification in each idea individually.

What the vanilla file `common/idea_tags/00_idea.txt` shows.

- It defines 14 categories. `slot` and `character_slot` lines can repeat, and each repetition is one more slot: `government` has `slot = mobilization_laws`, `trade_laws`, `economy` and three `character_slot = political_advisor` lines; `military_staff` has `army_chief`, `navy_chief`, `air_chief` and three `high_command` lines.
- The wiki does not mention `type`. Vanilla sets `type = national_spirit` on `country`, `army_spirit` on `academy_spirit`, `army_spirit` and `division_command_spirit`, `navy_spirit` on the three naval spirit categories and `air_spirit` on the three air force ones. The strings are in `hoi4.exe` and the three `*_spirit` types are the targets of the `<IdeaCategory>_category_type_cost_factor` modifier.
- The blocks inside `ideas = { }` are named by category or by slot. The 24 names vanilla uses are category names for categories without slots (`country`, `hidden_ideas`) and for the spirit categories (each has a slot of the same name), slot names (`economy`, `trade_laws`, `mobilization_laws`, `tank_manufacturer`, `naval_manufacturer`, `aircraft_manufacturer`, `materiel_manufacturer`, `industrial_concern`) and character slot names (`political_advisor`, `theorist`, `army_chief`, `navy_chief`, `air_chief`, `high_command`).
- Vanilla `slot_ledgers`: `army_chief = army`, `navy_chief = navy`, `air_chief = air`, `tank_manufacturer = army`, `naval_manufacturer = navy`, `aircraft_manufacturer = air`, `mobilization_laws = civilian`, and `theorist` and `high_command` as `invalid`. `ZZZ_idea_slot`, `XXX_idea_slot`, `law_category` and `designer_category` in the wiki examples are placeholders; none exists in vanilla.

### GFX and GUI

*See also: [Interface modding](interface_modding.md)*

Each idea category represents a row in the country politics view, while each slot represents a slot under that row.
The `country_politics_idea_category_entry` container window within the `/Hearts of Iron IV/interface/countrypoliticsview.gui` file decides the user inteface information about each row. The most important thing here is the gridbox, as it decides the following:

- The size of each idea slot within the category, by default 80 by width and 64 by height. This is used for distances between slots.
- The max amount of slots, **by default 7 horizontally and 1 vertically.** If not adjusted, it'd be impossible to have more than 7 idea slots in a category.
- The format of the gridbox, deciding in which direction the idea slots are added.

The idea category's icon, shown on the left of the category's row, is decided by the GFX_idea_categories sprite. The sprite is split into multiple frames horizontally, and each category is assigned a part of it depending on its order defined in `/Hearts of Iron IV/common/idea_tags/*.txt`. The sprite is defined in `/Hearts of Iron IV/interface/countrypoliticsview.gfx` and its definition in the base game consists of the following:

```text
	spriteType = {
		name = "GFX_idea_categories"
		texturefile = "gfx/interface/idea_categories.dds"
		noOfFrames = 6
	}
```

When adding a new category, make sure to update the sprite and the amount of frames accordingly.

An icon can be defined for idea slots, which will be used for them if there is no idea assigned to that slot. This definition in any `/Hearts of Iron IV/interface/*.gfx` file, taking XXX_idea_slot as an example, is done the following way:

```text
	spriteType = {
		name = GFX_idea_slot_XXX_idea_slot
		textureFile = gfx/interface/filename.dds
	}
```

In other words, the sprite must have the same name as the idea slot but with `GFX_idea_slot_` prepended in the beginning.

Checks against the vanilla interface files.

- `country_politics_idea_category_entry` has `ideas_grid` with `slotsize = { width = 80 height = 64 }` and `max_slots = { x = 7 y = 1 }`, as the wiki says. `GFX_idea_categories` has `noOfFrames = 6`.
- Vanilla declares `GFX_idea_slot_<slot>` for 11 slots: `air_chief`, `aircraft_manufacturer`, `army_chief`, `high_command`, `industrial_concern`, `materiel_manufacturer`, `naval_manufacturer`, `navy_chief`, `political_advisor`, `tank_manufacturer`, `theorist`. The three law slots have none. The prefix `GFX_idea_slot_` is also a string in `hoi4.exe`.

## Modifying cost of a slot

The `<idea slot>_cost_factor` modifier can be used to modify the price in political power for adding ideas or characters in this slot. However, there is a restriction on that modifier. In order for it to work, the idea slot needs to have any ideas or characters defined beforehand.

The files in the `/Hearts of Iron IV/common/ideas/*.txt` folder are loaded in the order of the Unicode character IDs, which put capital letters before underscores, which are put before lowercase letters. For example, this means that a file with the filename of `TAG.txt` is loaded before `_economy.txt` or `_manpower.txt` (the base game's locations of laws), which would get loaded before `country.txt`. Due to the above quirk, this means that an idea with the modifier affecting a price of a law, for instance, `economy_cost_factor = -0.10`, **will throw an error if the filename starts with an uppercase character** unless the laws are stored from files different from base game.

There are two primary ways to fix this. The first one is to simply change the filename of the country's idea file, changing it from, for instance, `GER.txt` to`germany.txt`. In case you have to keep the filename the same to overwrite a file, a new file can be created instead. Alternatively, [assuming that you have a replace_path to the ideas folder](modding.md), you could rename the files storing the laws to begin with a character with a smaller ID, for instance, to `00_economy.txt`, which would get loaded prior to `TAG.txt`.

Additionally, this also means that there have to be ideas defined within character slots for the modifier to work, such as `political_advisor_cost_factor = 0.1`. This is because characters are loaded later than ideas or country leader traits, so they're not loaded yet when evaluating the modifier, causing the error. This can be bypassed by creating ideas for the character slots in `/Hearts of Iron IV/common/ideas/*.txt` files. These will never appear for the countries as these are character slots rather than idea slots, but an idea that was loaded beforehand will correct the error.

The documented modifiers behind this section.

- The documentation calls the modifier `<IdeaGroup>_cost_factor` (country category, number). Its 25 valid group names are `academy_spirit`, `air_chief`, `air_force_academy_spirit`, `air_force_command_spirit`, `air_force_spirit`, `aircraft_manufacturer`, `army_chief`, `army_spirit`, `country`, `division_command_spirit`, `economy`, `hidden_ideas`, `high_command`, `industrial_concern`, `materiel_manufacturer`, `mobilization_laws`, `naval_academy_spirit`, `naval_command_spirit`, `naval_manufacturer`, `navy_chief`, `navy_spirit`, `political_advisor`, `tank_manufacturer`, `theorist` and `trade_laws`. Vanilla uses it for the 14 law, advisor, chief, theorist, designer and concern slots, for example `political_advisor_cost_factor` (174 uses), `economy_cost_factor` (158), `mobilization_laws_cost_factor` (146) and `theorist_cost_factor` (10). It never uses the `country_`, `hidden_ideas_` or spirit-category forms.
- `<IdeaCategory>_category_type_cost_factor` is a separate documented modifier for the three category types `army_spirit`, `navy_spirit` and `air_spirit`. The wiki does not mention it. Vanilla uses `navy_spirit_` in 6 files and `army_spirit_` and `air_spirit_` in 2.
- `disabled_ideas` is a documented boolean country modifier with no description. Vanilla has one use, `disabled_ideas = 1` inside an idea in `common/ideas/spain_republic.txt`. What it disables is not stated. (unverified) It does not switch off another national spirit: with an idea carrying `disabled_ideas = 1` added next to a +0.5 `political_power_gain` spirit, the modifier read 0.5 while both were present, 0.5 after the disabling idea was removed, and 0 once both were gone. No error.log line named `disabled_ideas`. Only one other spirit in the country category was read, through one modifier. What it does to other idea types (laws, advisors) was not tested.

## Notes

**^** **a:** Depends on the value in the `/Hearts of Iron IV/common/idea_tags/*.txt` file, which is always 150 in base game

Footnote a is out of date: the default price depends on the category and is not 150 everywhere in 1.19.3. See the default table under "Additional arguments".
