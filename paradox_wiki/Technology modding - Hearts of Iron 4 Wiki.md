# Table of contents

- [Brief user interface](#brief-user-interface)
- [Technologies](#technologies)
  - [Triggers](#triggers)
  - [Modifiers](#modifiers)
  - [Effects](#effects)
  - [Enabling objects](#enabling-objects)
  - [Hidden technology examples](#hidden-technology-examples)
  - [Name and icon](#name-and-icon)
  - [Technology's cost](#technologys-cost)
  - [Position](#position)
  - [Sub-technologies](#sub-technologies)
  - [Categories](#categories)
  - [Experience costs](#experience-costs)
  - [AI weighting](#ai-weighting)
  - [Doctrines](#doctrines)
  - [Additional](#additional)
  - [Examples](#examples)
- [Folders](#folders)
- [Graphical user interface](#graphical-user-interface)
  - [Items](#items)
    - [Item sprites](#item-sprites)
  - [Folder](#folder)
  - [Folder tabs](#folder-tabs)
- [Technology sharing groups](#technology-sharing-groups)
- [References](#references)


---

Technologies can be used to apply effects and static [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) towards the country researching them. Additionally, technologies can unlock equipment, enable buildings to be built up to a specified level, as well as modifying the stats of the units of the country. Doctrines, while no longer researched as technologies, are still considered technologies in the in-game code, although there are some differences in their required definitions.

Technologies themselves are defined in /Hearts of Iron IV/common/technologies/\*.txt files, while their categories and folders are defined in /Hearts of Iron IV/common/technology\_tags/\*.txt files. The [graphical user interface file](<Interface modding - Hearts of Iron 4 Wiki.md>) where the technology tree is defined is /Hearts of Iron IV/interface/countrytechtreeview.gui, requiring edits for each new technology folder or branch within the folder. **This is mandatory to edit in order for new technologies to show up**, unless the new technology requires an existing base game technology with an existing path.

Doctrines are also defined in /Hearts of Iron IV/common/technologies/\*.txt files and their folders and categories also in /Hearts of Iron IV/common/technology\_tags/\*.txt files, however, the graphical interface file used is /Hearts of Iron IV/interface/countrydoctrinetreeview.gui. Similarly to technologies, the GUI file is very interconnected with the doctrine definitions.

## Brief user interface

/Hearts of Iron IV/interface/countrytechtreeview.gui, /Hearts of Iron IV/interface/countrytechtreeview.gfx, and /Hearts of Iron IV/interface/countrydoctrinetreeview.gui in particular define the *appearance* of technology/doctrine folders as well as the items within them. In particular, this exactly is included in the interface files:

- Technology branches – a series of technologies connected with the `path = { ... }` argument, being defined in the interface by a gridboxType formatted after the first technology that doesn't have a path defined to it. **This is mandatory for a technology to show up if it doesn't require any other technology**, as `path` assigns the gridbox of the parent to the linked technology. In particular, these are defined within a branch:
  - The position of the first technology in the branch, or rather the position of point (0, 0) in the coordinate system used to position the technologies in the branch.
  - The offset in pixels to use a singular unit when positioning technologies. This is in contrast to national focuses, where the offset used as a singular unit is consistent across different focus trees.
  - The orientation to use for drawing paths as to make it look like it's going down, right, or a different direction.
- The items – the icons used for each technology, including the background box itself. **This is mandatory to edit when creating new folders,** but it may also come to play in base game folders, such as with sub-technologies. This consists of the details for each element, in particular:
  - The background box – which GFX is used. The GFX also decides the size. This in particular is done in the /Hearts of Iron IV/interface/countrytechtreeview.gfx file.
  - The icon of the technology – the position on the box.
  - Ahead-of-time/technology boost icons – the position on the box, the used font, the used GFX.
  - The name of the technology – whether it should be displayed, and if it is: where to show it and with what font.
  - Sub-technologies – where to position them in the tree, which GFX they use. Technology-specific icons don't exist for sub-technologies, instead using a set of indices.
- The tabs in the top of the tree allowing changing between technology folders. **This is mandatory to edit when creating new folders.**
- The standard [interface information about the tree](<Interface modding - Hearts of Iron 4 Wiki.md>). Anything that can be done with GUI can be done to a given folder, including but not limited to:
  - Adding icons, including the background or the stripes highlighting technologies. [This is done with an iconType](<Interface modding - Hearts of Iron 4 Wiki.md#icontype>).
  - Adding text to be visible on the folder, **such as the years showing when each technology stops being ahead-of-time**. [This is done with an instantTextboxType](<Interface modding - Hearts of Iron 4 Wiki.md#instanttextboxtype>).
  - Creating new [container windows](<Interface modding - Hearts of Iron 4 Wiki.md#containerwindowtype>) that [scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) can be linked to with their `parent_window_name`, allowing it.

For exact technical details, see the [Graphical User Interface section](#graphical-user-interface).

## Technologies

Each technology is located within /Hearts of Iron IV/common/technologies/\*.txt files, within the `technologies = { ... }` block traditionally encompassing the entire contents of the file. Like most files, the filename has no bearing on how the file is read: any technology can be in any folder without issues. Each technology is a separate block within `technologies = { ... }`, where the name of the block is used as a technology ID.

In general, a technologies file is laid out similarly to the following example:

```text
technologies = {
    my_technology_1 = {
        ...
    }
    my_technology_2 = {
        ...
    }
}
```

Each technology is hidden by default, requiring special code to be put within GUI. However, AI can still research technology even if it's hidden, so [it should be made impossible to research manually](#triggers) if it's intended to be hidden.  
A technology can be researched as an effect with `set_technology = { my_technology_1 = 1 }` and unresearched with `set_technology = { my_technology_1 = 0 }`, with `popup = no` possibly being added in order to remove the notification given to the player. Note that while it is possible to unresearch technologies, this does not always work properly: this can fail to unresearch technologies that are mutually exclusive with other technologies and doesn't work properly [those that unlock database objects](#enabling-objects).

### Triggers

*See also: [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>)*

There are two types of trigger blocks used in technologies.  
`allow = { ... }` is a trigger block checked continuosly throughout the game. If it is false, then the technology will be impossible to research through the research menu, but it will still remain possible to research via an effect and it will remain visible in the menu. This is typically set to be never true for hidden technologies in order to prevent AI from researching it.

`allow_branch = { ... }` is a trigger block that, instead, needs to be met in order for the technology to be visible. If it's not met, then any technology connected to it via `path = { ... }` will also become invisible. If it's met, AI will also not be able to select the technology to research.

### Modifiers

*See also: [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>)*

Each [country-scoped modifier](<Modifiers - Hearts of Iron 4 Wiki.md#country-scope>) is allowed to be put directly within the technology, and these will apply to the country after researching the technology. This will look as such:

```text
my_technology_1 = {
    political_power_gain = 0.1
    local_resources_factor = 0.2
}
```

This particular technology will grant +10% ![Political Power](media/technology-modding-hearts-of-iron-4-wiki_21e8ff155d__img2.png)Political Power gain and +20% resource extraction efficiency when researched.

In addition, it's also possible to make a technology apply a bonus for specific sub-units making up land templates, ships, and the airforce. These sub-units are defined in /Hearts of Iron IV/common/units/\*.txt files. Technologies can make the bonus apply to either the sub-unit types themselves, or the categories they fall in, defined in /Hearts of Iron IV/common/unit\_tags/\*.txt and specified in the sub-unit definitions. Any modifier defined within the sub-unit definitions or the equipment archetypes used by them can be applied to units, which'll apply as a multiplicative modifier towards them.  
It is also possible to apply this effect only on a certain terrain. This is done by putting the terrain within the scope of the sub-unit type or category. Each terrain is defined in /Hearts of Iron IV/common/terrain/\*.txt. In addition to these terrains, `amphibious` gets used for naval invasions and `river` gets used for river crossings.  
For example, the following code will increase the naval speed of destroyer-type ships by 10%, decrease the combat width of all sub-units in the category of category\_all\_infantry by 20%, and increase the attack of the same category when fighting in urban terrain by 15% when the technology is researched:

```text
my_technology_1 = {
    category_all_infantry = {
        combat_width = -0.2
        urban = {
            attack = 0.15
        }
    }
    destroyer = {
        naval_speed = 0.1
    }
}
```

`show_effect_as_desc = yes` can also be used in order to make the modifiers show up in the description of the technology itself rather than in the tooltip showing up when hovering over the technology. Notably, this also applies to the effects of the technology.

### Effects

*See also: Effects*

An effect block ran for the country that unlocked the equipment is `on_research_complete = { ... }`. These effects will be run for the country and they will show up in the tooltip of the technology so that the player is aware of them. `on_research_complete = { ... }` WILL run for techs unlocked through effect, but NOT on techs that a country unlocks in its history file.

Additionally, `on_research_complete_limit = { ... }` serves as a trigger block necessary to be fulfilled for the effects to be executed. This would be necessary to set if it is possible for the entire `on_research_complete = { ... }` to either be visible or invisible depending on circustances, as the game handles generating the tooltip poorly in this circustance. If nothing within `on_research_complete = { ... }` grants a tooltip or there's always something showing a tooltip, it is not necessary to set `on_research_complete_limit = { ... }` This is an example of a tech with `on_research_complete_limit`:

```text
my_technology_1 = {
    on_research_complete_limit = {
        has_tech = my_technology_2
    }
    on_research_complete = {
        add_political_power = 100
    }
}
```

`show_effect_as_desc = yes` can also be used in order to make the effects show up in the description of the technology itself rather than in the tooltip showing up when hovering over the technology. Notably, this also applies to the modifiers of the technology.

### Enabling objects

Several database objects can be set to be unlocked by a technology, including equipment types, equipment modules, sub-units, and buildings.  
If the database object is not set to be unlocked by any technology in general, it'll be always possible to select it, while putting them in a technology will require the technology. This can be used to set these to be country-specific, such as the bicycle battalions for ![Flag of Netherlands](media/technology-modding-hearts-of-iron-4-wiki_21e8ff155d__img3.png) Netherlands and ![Flag of Japan](media/technology-modding-hearts-of-iron-4-wiki_21e8ff155d__img4.png) Japan, if they're within a hidden technology only set for specific countries in their history files or other effect blocks. If one of these database objects is locked behind technology, it won't be possible to force a country to use them without having the technology: equipment variants or orders of battle will fail to be created with the specified type.

Equipment types are assigned with `enable_equipments = { ... }`, with each equipment type within listed separated with any non-zero amount of whitespace characters. For example, `enable_equipments = { my_equipment_1 my_equipment_2 }` will set my\_equipment\_1 and my\_equipment\_2 to only be enabled after the technology was researched. Unique to equipment, this will also make the equipment icon be a copy from the technology icon, unless an equipment-specific icon was created in the `GFX_<equipment type>_medium` format.

Sub-units are done with `enable_subunits = { ... }`, and modules - with `enable_equipment_modules = { ... }`, with the same formatting as for equipment types: whitespace-separated entries within to set them to be unlocked.

Buildings are done with `enable_building = { ... }`. However, the formatting in this case is different: the building is specified with `building = my_building` and the level with `level = 3`. In particular, the level will not unlock this many levels of the building, but unlock the building to be built *up to* that level. For instance, if the building was already unlocked to level 2 from a technology researched beforehand, researching a technology with `level = 5` will result in it being possible to construct up to 5 of the building in the state/province rather than 7. A full example:

```text
enable_building = {
    building = my_building
    level = 5
}
```

Uniquely, it's possible to still construct buildings that aren't yet unlocked via technologies by using an [effect](<Effect - Hearts of Iron 4 Wiki.md#add-building-construction>) or with the starting buildings in the [state's history file](<State modding - Hearts of Iron 4 Wiki.md>). This can build up to the max level specified in the [building definition itself](<Building modding - Hearts of Iron 4 Wiki.md>). This is because the buildings are set for states themselves, and implementing it otherwise can cause buildings to be lost if the state control goes to a country that doesn't have the building researched.  
If desiring to make multiple buildings be unlocked by the same technology, another `enable_building = { ... }` block can be set in the technology.  
**The level within the technology cannot be higher than the building's max level** set within the [building definition itself](<Building modding - Hearts of Iron 4 Wiki.md>).

`enable_tactic = my_tactic` is also used to enable a combat tactic for the country that may be chosen during a land battle. These tactics are defined within /Hearts of Iron IV/common/combat\_tactics.txt.

When unresearched via an effect, this doesn't work entirely properly, rather, the database object in question will remain possible to use for the country until a restart of the game. For this reason, it's better to avoid unresearching technologies such as this and treat these database objects as being granted for forever without being possible to take away.

### Hidden technology examples

### Name and icon

The name of the technology for the specified language is set by using the technology's ID as the localisation key, with description by appending `_desc` in the end. For example, this can be used as localisation for the English language within any /Hearts of Iron IV/localisation/english/\*\_l\_english.yml file for `my_technology_1`:

```text
l_english
my_technology_1
"My
 
technology"

 
my_technology_1_desc
"My
 
technology's
 
description"
```

If a technology does *not* have a name defined, it gets 'borrowed' from the equipment that the technology unlocks. This would also make the description the same as the equipment's description, if one is present. This does allow making the names be country-specific by prepending it to the beginning, separated with an underscore. For example, if the technology unlocks `my_equipment_1`, then this within any /Hearts of Iron IV/localisation/english/\*\_l\_english.yml file will make the technology (and equipment) have the name of `My Honduran equipment` for ![Flag of Honduras](media/technology-modding-hearts-of-iron-4-wiki_21e8ff155d__img5.png) Honduras and `My equipment` for every other country:

```text
l_english
HON_my_equipment_1
"My
 
Honduran
 
equipment"

 
my_equipment_1
"My
 
equipment"
```

The icon is defined as a spriteType within any /Hearts of Iron IV/interface/\*.gfx file, by prepending the name of the technology with `GFX_` and appending `_medium` to the end. For example, the following will result in an icon for `my_technology_1`:

```text
spriteType = {
    name = GFX_my_technology_1_medium
    texturefile = gfx/interface/technologies/filename.dds
}
```

Here it is the other way around compared to names: if the equipment doesn't have a unique icon defined, then it will use the one defined by the technology. The country-specific equipment and technology icons are done with inserting the country tag between GFX and the name of the technology, still separated with underscores, as `name = GFX_HON_my_technology_1_medium`.

### Technology's cost

There are two primary arguments that modify the cost to a technology.

`research_cost = 1` assigns the base research cost for this technology. For comparison, a value of 1 is equal to 100 days worth of research assuming fully default research speed with no modifiers.

`start_year = 1935` assigns the year at which the technology is intended to be researched. Each year in advance adds +200% to the technology's cost, applied smoothly depending on the amount of days left. This does not modify the start year shown in the top of the technology folder for some of the folders, this is [defined within the interface file of the folder.](#folder)

Additionally, it's possible to make the cost be modified by [other technologies pathing to it](#position).

### Position

In order to connect a technology to a different one within the tree, `path` is used as such in the technology from which *the branch originates*:

```text
path = {
    leads_to_tech = my_technology_2
    research_cost_coeff = 1
}
```

In here, the technology where the path leads is specified with leads\_to\_tech. The path will be created in every folder that contains both of these technologies. This also leads to adding that technology to this technology's tree branch gridbox in every mutual folder. **If a technology doesn't have any other technology as a requirement using path in any folder where it's placed, then [it must have a separate gridboxType definition within the folder's container window.](#folder) Otherwise, the technology branch will never appear in-game.**  
The gridbox is used in order to assign the information used by the `folder = { ... }` block later on: the position of the coordinate origin on the screen, the size in pixels that one unit of x and y represent, and in which direction they aim (used for drawing the path). Add the argument `ignore_for_layout = yes` into the path block for secondary paths (such as light cruiser techs leading to heavy cruiser techs without MTG) to prevent the `Found multiple potential grid boxes for tech` error.

A pathing automatically makes the latter technology require the former. If a technology has several technologies connecting to it via path, then at least one of the technologies leading to it must be researched. If there are multiple technologies leading to this one within the same folder, the technology will use the same gridbox used in the technology pathing to it that was defined the earliest. research\_cost\_coeff can be used to decrease the cost if needed: if this technology is researched, the technology it paths towards will have this cost multiplied by the research\_cost\_coeff. This can be used if multiple technologies path to the same technology to make it faster to research if a more 'advanced' technology was researched.

Having assigned the technology to a branch, whether by having a different one path to it or by having created a gridboxType definition in the interface file, it is possible to define the exact position of the item with folder:

```text
folder = {
    name = my_folder
    position = { x = 0 y = 1 }
}
```

In this, the name refers to the folder. The position is in sets of coordinates defined by the slotsize of the gridbox that this technology is assigned to via the path. For example, within the gridbox's definition, `slotsize = { width = 70 height = 70 }` would mean that a single unit of either x or y represents 70 pixels in the GUI in the appropriate direction. The direction of x and y depends on the format of the gridbox: a "LEFT" format means that x goes up-to-down while y goes left-to-right, while an "UP" format would mean that x goes left-to-right while y goes up-to-down. The origin point (i.e. where the technology would be at `x = 0 y = 0`) is assigned by the `position = { x = 100 y = 100 }` within the gridbox's definition in the interface file, which uses pixels and is positioned relative to the top-left corner of the window.

Defining multiple folders for the same technology is done by having multiple of the `folder = { ... }` within the technology. For each folder, the technology must have a gridbox assigned to show up in one of the two ways.

In order to have a technology as a dependency without having to draw a path, `dependencies` can be used as such:

```text
dependencies = {
    my_technology_1 = 1
    my_technology_2 = 1
}
```

Since this doesn't draw a path, this does not assign the currently-defined technology to the gridbox of either of two technologies. Additionally, this also serves as an AND statement unlike the path that serves as an OR statement: every dependency must be researched to complete this technology, alongside at least one of the paths leading to this technology if there's one.

Additionally, `XOR = { ... }` is used to make the technology be mutually-exclusive with every technology specified within. The technologies within are separated with any whitespace characters, such as `XOR = { my_technology_1 my_technology_2 }`. A XOR should be in every mutually-exclusive technology, specifying the others, having it in just one of technologies isn't enough.

### Sub-technologies

A technology can have specified technologies assigned as sub-technologies by using `sub_technologies = { ... }`, where every listed technology is a sub-technology. The block contains technologies separated with whitespace characters, such as `sub_technologies = { my_technology_1 my_technology_2 }`. This also assigns them the indexes of 0 and 1 respectively, [which get used in determining which container exactly to use](#item).  
If desiring to use a container of a sub-technology with a different index, `sub_tech_index = 1` can overwrite it within the definition of the sub-technology itself. For example, setting it to be 2 will make the game treat it as if it's a third sub-technology that the item has, even if it's the first one, which'll move it to the according position and give it the according icon.

As a sub-technology item is directly assigned to each technology folder item as a separate container, the sub-technologies do not need their own gridbox definition and neither do they need the folder argument.

### Categories

A technology can have categories assigned to it with `categories = { ... }`, where each category is separated with whitespace characters as `categories = { my_category_1 my_category_2 }`.  
The player never sees the category for each technology, but it does have certain uses, including but not limited to:

- [AI modding](<AI modding - Hearts of Iron 4 Wiki.md>). It's possible to make AI prioritise taking technologies within specific categories, such as within AI focuses or AI strategy plans.
- [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>). `research_bonus = { my_category_1 = 0.1 }` is a special argument argument within idea, characters, and country leader traits that allows modifying the speed of researching a specific technology category.
- [the add\_tech\_bonus effect](<Effect - Hearts of Iron 4 Wiki.md#add-tech-bonus>), that can grant a one-use bonus for each technology within the specified folder.
- [Technology sharing groups](#technology-sharing-groups), which can be limited to only apply towards specified technologies.

Technology categories are defined within a `technology_categories = { ... }` block within /Hearts of Iron IV/common/technology\_tags/\*.txt files, where each category is separated with whitespace characters, no other info being assigned to it. For localisation, there are two keys assigned. Taking my\_category\_1 as an example, it'd have the localisation of this:

```text
 my_category_1: "My Category"
 my_category_1_research:0 "My Category's Research Speed"
```

In particular, the first one, the same as the category's name, is used for most cases (such as the one-time bonuses and technology sharing groups), while the second one, with \_research appended in the end, is used for the research\_bonus-type modifiers.

### Experience costs

In order to assign an experience type to a technology, `xp_research_type = army` is used. This has 3 types: army, navy, and air. This assigns a particular experience type to the technology.

After this, there are two types of experience costs that can be used:

- `xp_boost_cost = 40` and `xp_research_bonus = 1.5` can be used to make the technology be *boosted* by experience. This is done with the naval folder with ![Man the Guns](media/technology-modding-hearts-of-iron-4-wiki_21e8ff155d__img6.png)Man the Guns, for example.
- `xp_unlock_cost = 100` makes the experience cost fully grant the technology. This in particular is commonly done with doctrines.

### AI weighting

In order for the AI to research any technology, you MUST include at least one of its categories in any /Hearts of Iron IV/common/ai\_focuses/\*.txt [file](<AI focuses - Hearts of Iron 4 Wiki.md>).

`ai_will_do = { ... }` is a [MTTH block](<AI modding - Hearts of Iron 4 Wiki.md#ai-will-do>) that decides the likelihood for the AI to do this focus if [an AI strategy plan](#ai-strategy-plans) is not set.  
By default, each technology has a score of 1. The arguments of `base` (changing the value), `add`, and `factor` (multiplying it) can be used to modify it.  
Within the `ai_will_do = { ... }` block, `modifier = { ... }` functions as a trigger block where the prior three value-modifying arguments are also supported. The value will be modified if the triggers are true. For example, the following will result in the value of 3 for POL and a value of 1 for every other country:

```text
ai_will_do = {
    base = 1
    modifier = {
        factor = 3
        tag = POL
    }
}
```

An arbitrarily large amount of modifiers is possible to add to an ai\_will\_do, and they will apply in the order they're put in the code. It is also possible to use variables within a modifier of the ai\_will\_do value.

The way that the value is evaluated for AI picking the technology is that, every 7 days, it generates a random decimal value between 0 and the ai\_will\_do value for each of the technologies. There are several modifiers additionally, in order to make the AI take the cost, bonuses, and ahead-of-time into considerations. A lot of AI modifiers that apply to every single technology can be changed within [defines](<Defines - Hearts of Iron 4 Wiki.md>).

Additionally, `ai_research_weights = { offensive = -1.0 }` can be used to make the AI prioritise this technology less or more if it has the specified focus. This includes resources, sub-units, offensive and defensive, or sub-unit categories.

### Doctrines

In order to mark a technology as a doctrine, it must have `doctrine = yes`. It also will have to be within a technology folder that's assigned to hold doctrines.

`doctrine_name = my_doctrine_name` is also defined within the first doctrine of the branch in order to let the player know the name of the doctrine branch when hovering over the icon (e.g. *Strategic destruction* or *Grand battleplan*). This is a localisation key that gets assigned a value for each language within any /Hearts of Iron IV/localisation/ file.

### Additional

`show_equipment_icon = yes` is used in order to make the equipment icon show up when hovering over the technology in the tree. This can be useful for technologies which use an icon that's not the same as the equipment that it unlocks, such as the landing craft or rocket engine technologies in base game.

`force_use_small_tech_layout = yes` is used in order to force the game to use this technology to use the small item for this particular technology even if it unlocks equipment. Keep in mind that if there is no small item defined, all technologies will use the regular item, so this would only be useful if equipment-unlocking technologies in the folder are split between small and regular items.

`desc = MY_TECHNOLOGY_SPECIAL` provides additional text when hovering over the technology. *This is in addition to the technology's actual description*, rather than overwriting it. This is a localisation key that gets assigned a value for each language within any /Hearts of Iron IV/localisation/ file.

### Examples

## Folders

Folders are defined as blocks within the `technology_folders = { ... }` block in /Hearts of Iron IV/common/technology\_tags/\*.txt files, where the name of the block within is used as the folder's ID.  
In particular, there are 3 arguments that can go into folders:

- `available = { has_dlc = "Poland: United and Ready" }` is a trigger block that must be met for the folder to be *visible*.
- `ledger = army` is the intelligence ledger to which the folder is assigned to. Possible values are `army`, `air`, `navy`, `military` (Appearing on each of the prior ledgers), `civilian`, `all`, and `hidden`.
- `doctrine = yes`, if specified, marks the folder as being a doctrine folder. Defaults to false if left out.

The localisation key used for the name of the technology is the same as the folder's name, while the description is the name with \_desc appended. For example,

```text
 my_folder: "My folder's name"
 my_folder_desc: "My folder's description"
```

In order to make the folder appear in-game, the graphical user interface needs to be edited accordingly, in particular:

- [A folder tab](#folder-tabs) need to be added to the top bar in order for the player to be able to select the folder.
- [The folder's container](#folder) needs to be created and filled with gridboxes in order for the game to know where to place the technologies, as well as any additional elements of the user interface such as textboxes and the background.
- [Item containers](#items) decide on the appearance of technologies as they appear in the folder in order to decide the background and the arrangement of elements – such as a research bonus, the name of the technology or sub-technologies — on that background.

If any of these isn't present, it will be impossible for the player to research any new technologies manually, but the AI will still be able to do so and [set\_technology](<Effect - Hearts of Iron 4 Wiki.md#set-technology>) may be used to directly assign them to the player.

## Graphical user interface

*See also: [Interface modding](<Interface modding - Hearts of Iron 4 Wiki.md>)*

The menu for viewing the tree is defined within /Hearts of Iron IV/interface/countrytechtreeview.gui for technologies and /Hearts of Iron IV/interface/countrydoctrinetreeview.gui for doctrines. However, they are mostly similar in definition.

### Items

A technology or doctrine tree item is the technology itself within the tree. It assigns which background is used, where exactly to locate the technology's icon in the background, where to place the technology bonus icon, where to place sub-technologies (if needed), where to place the technology's name on the research tree (if defined).  
A technology item is defined by using a containerWindowType with the name of `techtree_<folder name>_item`, while the small item is defined with the name of `techtree_<folder name>_small_item`. The definition for doctrine items is fully identical and does not differ from technologies in any way. These container windows for items are *not* contained within any other container window, rather being defined fully independently. **Small items are not inherently smaller**: the categorisation only assigns a different containerWindowType to be used for technologies that don't unlock equipment, and all of the properties are determined within that container window. Both use the exact same images as the default icon, [which must be changed manually](#item-sprites) if needed.

When a small item is used and when a regular item is is determined by equipment. If a technology unlocks equipment, it'll use the regular item, while a technology that doesn't unlock equipment will use the small item. However, if the folder has no small item defined in the interface file, then every single technology will use the regular item. `force_use_small_tech_layout = yes` within the technology will force it to use the small item, if it exists.

In particular, this is an example of a regular small item:

In here, "Icon" represents the technology-specific icon. "bonus\_icon" represents the icon that's used for the [one-time technology research bonus](<Effect - Hearts of Iron 4 Wiki.md#add-tech-bonus>) and "bonus" represents the text for the bonus saying how much it actually boosts the research. These can be edited to change the position or the font.

For large items, usually the name of the technology is also shown on the tree without needing to see the description. This is done with inserting an instantTextBoxType with the name of "Name" into the item, usually between the "Icon" and "bonus\_icon".  
Additionally, this is also where sub-technologies are assigned. A sub-technology slot is defined with a containerWindowType with the name of "sub\_technology\_slot\_0", with the last number being 0 for the first one, 1 for the second one, and 2 for the third one. By default, there can be no more than 3 sub-technologies defined within an item. The picture defined within is done with the `picture` iconType, and it cannot be changed to be technology-specific, it depends only on the sub-technology index of the technology.  
This is an example of a regular item with a sub-technology slot and the technology's name shown, with positions also adjusted for a regular item slot size:

#### Item sprites

There are 5 sprites defined for item slots. By default, these are defined in /Hearts of Iron IV/interface/countrytechtreeview.gfx. If a folder doesn't have specific item slots, these are used for items:  
`GFX_technology_available_item_bg` is used for technologies that are shown to be available for the player to select  
`GFX_technology_branch_item_bg` is used for items that are mutually exclusive to a technology you've already researched  
`GFX_technology_unavailable_item_bg` is used for technologies that the country is not yet able to research  
`GFX_technology_researched_item_bg` is used for technologies that the country has already researched.  
`GFX_technology_currently_researching_item_bg` is used for technologies that are currently selected by the country.

These in particular are, by appearance, regular non-square rectangular land items in base game, such as the one used for Infantry Equipment; however, GFX\_technology\_branch\_item\_bg uses a smaller, square, icon since the base game doesn't have any mutually exclusive techs of the larger size. **These would be used for both regular and small items - in order to make small items be smaller by appearance, folder-specific sprite definition are required**. In order to define a specific folder's item to use a non-default background, the name of the technology folder can be appended after the word `technology`, such as `GFX_technology_my_folder_available_item_bg`. For small items, the word "small" would be added after the folder name as `GFX_technology_my_folder_small_researched_item_bg`.  
The item slots for sub-technologies are defined similarly, although with `technology` changed to `subtechnology`. In the exact same way, sub-technologies can have folder-specific items, such as `GFX_subtechnology_my_folder_available_item_bg`.

Example sprite definitions to make a folder with the name of `my_folder` have its small items use the same background as the regular small land items use in base game:

### Folder

A folder is defined as a containerWindowType the name of which is exactly the same as the name of the folder within. That container window would have to be located within the containerWindowType with the name of `countrytechtreeview`, defined within /Hearts of Iron IV/interface/countrytechtreeview.gui (**not countrytechnologyview.gui**), for technology folders and within the containerWindowType with the name of `countrydoctrineview`, defined within /Hearts of Iron IV/interface/countrydoctrinetreeview.gui, for doctrine folders.  
This container contains information on what's within the folder itself: the background image used, anything else in the background such as the start years of technologies or textboxes telling the branches, as well where each individual technology branch is located.

A simple technology folder definition looks like the following:

In here, one important thing is the iconType representing the background, in this case called `my_techtree_bg`. The spriteType specified here will get used as the background of the tree, with the static size.

Additionally, incredibly important are the gridboxes representing technology tree branches. The game uses them to know where exactly to locate the branches, how much to distance items within them, and in which direction to take the coordinates. The technology tree branch follows the name formatting of the first technology's name with \_tree appended in the end.

- `position = { ... }` argument is the position of the top-left corner of the technology icon counting from the upper left corner. x is left-to-right, y is up-to-down.
- `slotsize = { ... }` argument is used to tell how to translate [the technology's position](#position) within `folder = { ... }` into pixels.
- `format = "LEFT"` argument is used to tell into which direction to aim x and y. The two most commonly-used positions in here are "LEFT", for making x point up-to-down and y point left-to-right, and "UP", for making x point left-to-right and y up-to-down. Usually these are used in trees pointed right from left and down from up respectively in order to make y the direction into which the tree moves.

This also modifies how the paths are drawn between technologies. In most cases, with "LEFT", it goes right for one unit, then goes vertically for as much as necessary, and finally continues right for as much as needed; with "UP" it goes down by one unit, goes horizontally for as much as needed, and then continues down towards the technology. This does not always apply, such as when the technology is fairly close, but modifying the format can change the way the paths between technologies are drawn regardless.
Due to this, "LEFT" is used for horizontal trees (with the parent being on the very left), while "UP" is used for vertical trees (with the parent being on the very top).

Any icons or textboxes can be added to the container window, and they'll appear in that position in the technology tree. This is what the game does for showing the start years of technologies, for example: each one is a separate instantTextBoxType within the folder's container window.

### Folder tabs

In order to select a technology folder, it should appear in the top selection. While the above [folder](#folder) section detailed the insides of the folder, it didn't detail adding the folder to the selection.

The folder selection is done within the `folder_tabs` containerWindowType. For technologies, this is stored inside of the `countrytechtreeview` container window, while for doctrines, it's inside of the `countrydoctrineview` container window.

Within that containerWindowType, a buttonType with the name of the folder (with \_tab appended in the end) is used to represent the folder, using `my_folder` as an example:

```text
buttonType = {
    name = "my_folder_tab"
    position = { x = 22 y = 0 }
    quadTextureSprite = "GFX_my_folder_tab"
    frame = 1
    clicksound = click_default
}
```

In here, `position = { ... }` controls the position of the folder tab, while `quadTextureSprite` is the exact sprite used by the tab. An example definition of that sprite within any /Hearts of Iron IV/interface/\*.gfx file is the following:

```text
spriteType = {
    name = GFX_my_folder_tab
    textureFile = gfx/interface/techtree/techtree_my_tab.dds
    noOfFrames = 2
}
```

In particular, noOfFrames controls the amount of frames the sprite has, cutting the image in a left half and a right half with 2. The first frame, on the left, is used when the folder is opened, while the second frame, on the right, is used when the folder is closed.

For doctrines, it's also typical to add the textbox detailing what the folder is. This is done with a regular instantTextBoxType:

```text
instantTextBoxType = {
    name = "my_doctrine_title"
    text = "my_doctrine"
    position = { x=60 y=18}
    font = "hoi_20bs"
    maxWidth = 160
    maxHeight = 20
    format = center
    alwaystransparent = "yes"
}
```

The text is what gets used within localisation, and the primary thing needed to change, while the name should just be unique from all the rest.

## Technology sharing groups

Technology sharing groups are a feature allowing to receive bonuses to researching technology that other members of the group have already researched, up to 50%. A technology group is defined in /Hearts of Iron IV/common/technology\_sharing/\*.txt files, where each group is represented with a separate `technology_sharing_group = { ... }` block.  
The only way to add a country to a technology sharing group is to [use the add\_to\_tech\_sharing\_group effect to do so.](<Effect - Hearts of Iron 4 Wiki.md#add-to-tech-sharing-group>) A similar effect can be used to remove them, and technology sharing groups can be set to automatically kick out members that don't meet requirements.

These arguments are used within technology sharing groups:  
`id = my_tech_group` is used to tell how to refer to the group is internally for the effects or triggers referring to one.  
`name = my_tech_group_name` is used to say which key shjould be used in order to assign the name to this group depending on the currently-turned on language in localisation.  
`desc = my_tech_group_desc` is used to say which key shjould be used in order to assign the description to this group depending on the currently-turned on language in localisation.  
`picture = GFX_my_tech_group` is used to assign a sprite, defined in any /Hearts of Iron IV/interface/\*.gfx file, to this group. This shows up in the country's research menu in the top.  
`research_sharing_per_country_bonus = 0.05` assigns how much of a bonus the technology sharing group grants for every other member that has researched that particular technology.  
`categories = { ... }` is a list of technology categories separated by whitespace characters. If specified, then the group will only apply bonuses towards technologies located in these categories.  
`is_faction_sharing = yes` makes the technology sharing group only grant bonuses towards countries in the same faction and, vise-versa, receive bonuses only from countries in the same faction. Defaults to false if unspecified.  
`available = { ... }` is a trigger block, run for every country in the technology sharing group, that details the requirements needed to remain within the group. If false at some point, the country will be automatically kicked out.

Here's an example of a technology-sharing group defined using all of these:

```text
technology_sharing_group = {
    id = tech_group_id
    name = tech_group_name
    desc = tech_group_desc
    picture = GFX_technology_sharing_default

    research_sharing_per_country_bonus = 0.1
    is_faction_sharing = yes

    categories = { infantry industry }

    available = {
        is_in_faction = yes
    }
}
```

## References

1. [↑](#cite-ref-1) NDefines.NTechnology.BASE\_TECH\_COST = 100
2. [↑](#cite-ref-2) NDefines.NTechnology.BASE\_YEAR\_AHEAD\_PENALTY\_FACTOR = 2
3. [↑](#cite-ref-3) NDefines.NAI.RESEARCH\_DAYS\_BETWEEN\_WEIGHT\_UPDATE = 7
4. [↑](#cite-ref-4) NDefines.NTechnology.MAX\_SUBTECHS = 3
5. [↑](#cite-ref-5) `NDefines.NTechnology.MAX_TECH_SHARING_BONUS = 0.5` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>).

Every single one of the above references is specified within [defines](<Defines - Hearts of Iron 4 Wiki.md>) and can be changed within a mod. When changing the define files, make sure to use an override file rather than copying over the entire base game files, as copying over the entire thing will cause crashes even on otherwise minor game updates, which commonly add new defines.

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
