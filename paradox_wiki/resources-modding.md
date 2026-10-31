# Resources modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Resources modding", revision 73143, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="73143" sources="common/resources/ interface/general_stuff.gfx interface/countryproductionlineview.gui gfx/interface/resources_strip.dds common/defines/00_defines.lua localisation/english/production_l_english.yml localisation/english/core_l_english.yml history/states/ documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `common/resources/_documentation.md` and `00_resources.txt`, the strip sprites and the production GUI, the resource defines, the localisation files and the effects, triggers and modifiers that name a resource.
Kit blocks added: the vanilla resource table, strip size, localisation keys, one correction for the production GUI (no `<resource>_value` text box), the resource defines, and a table of the script that names resources.
Gaps left: the wiki claim that `cic` cannot exceed 1 is not stated in any game file. Adding or removing a resource was not tested in the game.
<!-- kit:end id="review" -->

## Table of contents

- [Resources](#Resources)
  - [Icon frame](#Icon_frame)
  - [CIC](#CIC)
  - [Convoys](#Convoys)
- [Localization](#Localization)
- [Interface](#Interface)
  - [Additional notes](#Additional_notes)
    - [Kit: Where script names a resource](#kit-resource-script-surface)

---

## Resources <a id="Resources"></a>

The resources used by the game are found in `/Hearts of Iron IV/common/resources/00_resources.txt`.

The resource file follows this format:

```text
resources = {
    <resource> = {
        icon_frame = <frame>
        cic = <float>
        convoys = <float>
    }
}
```

<!-- kit:begin id="vanilla-resources" at="section:Resources" -->
**Kit note** Vanilla 1.19.3 defines seven resources in `common/resources/00_resources.txt`, in this order. All seven use `cic = 0.125` and `convoys = 0.1`. [vanilla-confirmed 1.19.3]

| `icon_frame` | Resource key |
| --- | --- |
| 1 | `oil` |
| 2 | `aluminium` |
| 3 | `rubber` |
| 4 | `tungsten` |
| 5 | `steel` |
| 6 | `chromium` |
| 7 | `coal` |

The game's own note in `common/resources/_documentation.md`: when you add a resource or change the order, update the define `NAI.MIN_FACTORIES_TO_WANT_TO_IMPORT`. It is a list with one number per resource in file order (vanilla: `0` for the first six, `10` for `coal`). [docs] `common/resources/_documentation.md`. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

Resource keys are plain lowercase identifiers that other script repeats: the state block `resources = { steel = 6 }` (512 of 1081 vanilla state files have a `resources` block), the equipment block `resources = { steel = 2 }`, and the `type` or `resource` argument of the effects and triggers in the table at the end of this page. [vanilla-confirmed 1.19.3] `history/states/`, `common/units/equipment/infantry.txt`.
<!-- kit:end id="vanilla-resources" -->

### Icon frame <a id="Icon_frame"></a>

Icon frame controls which frame from the resource image strip is used for the resource icon. A 'frame' is the 27 by 27 pixel square the icon occupies in the image.

The resource image strip is defined by the **GFX_resources_strip** spritetype, which points to `/Hearts of Iron IV/gfx/interface/resources_strip.dds` by default. By default 1 will refer to the Oil icon, 2 to Aluminium, etc.

The icons are defined in `/Hearts of Iron IV/interface/general_stuff.gfx`. Their definition must be changed if you're adding or removing resources:

```text
	spriteType = {
		name = "GFX_resources_strip"
		texturefile = "gfx/interface/resources_strip.dds"
		noOfFrames = X #X being the number of resources you have,
	}

	spriteType = {
		name = "GFX_missing_resources_strip"
		texturefile = "gfx/interface/missing_resources_strip.dds"
		noOfFrames = X
	}
```

The number of frames strictly corresponds to the amount of resources.

<!-- kit:begin id="strip-size" at="section:Icon_frame" -->
**Kit note** `gfx/interface/resources_strip.dds` and `gfx/interface/missing_resources_strip.dds` are both 189 x 27 pixels, which is seven frames of 27 x 27. The sprites `GFX_resources_strip` and `GFX_missing_resources_strip` both set `noOfFrames = 7` in `interface/general_stuff.gfx`. [vanilla-confirmed 1.19.3] DDS headers of both files, `interface/general_stuff.gfx`.
<!-- kit:end id="strip-size" -->

### CIC <a id="CIC"></a>

CIC defines the amount of resources needed to trade for 1 Civilian Factory. By default, this is 0.125, meaning 8 units of that resource are traded for 1 factory. Value can not be larger than 1.

### Convoys <a id="Convoys"></a>

Convoys controls the maximum amount of this resource a single convoy carries. By default, this is 0.1, meaning a convoy can carry 10 of the resource.

## Localization <a id="Localization"></a>

Localisation is defined in `/Hearts of Iron IV/localisation/production_l_<language>.yml` with the following localization keys:

```text
PRODUCTION_MATERIALS_<RESOURCE>:0 "Name of resource"
<resource>_desc:0 "Description of resource"
```

<!-- kit:begin id="loc-keys" at="section:Localization" -->
**Kit note** Vanilla keeps the name keys in `localisation/english/production_l_english.yml` (`PRODUCTION_MATERIALS_OIL`, `PRODUCTION_MATERIALS_ALUMINIUM`, and so on, one per resource) and the descriptions in `localisation/english/core_l_english.yml` (`oil_desc`, `aluminium_desc`, `rubber_desc`, `tungsten_desc`, `steel_desc`, `chromium_desc`, `coal_desc`). Vanilla writes both without the `:0` version number. [vanilla-confirmed 1.19.3]
<!-- kit:end id="loc-keys" -->

## Interface <a id="Interface"></a>

If implementing different resources, you will need to edit the interface so the game understands how to display the new resource. `/Hearts of Iron IV/interface/countryproductionlineview.gui` is the relevant file here.

Each resource is utilised two GUI elements: *<resource>_icon* and *<resource>_value*, which are found under the **resources** windowtype.

```text
buttonType = {
    name = "<resource>_icon"
    position = { x=0 y=2 }
    spriteType = "GFX_resources_strip"
    frame = 1 # Which icon is used from the spriteType image referred to above.
}

instantTextboxType = {
    name = "<resource>_value"
    position = { x = 31 y = 5 }
    textureFile = ""
    font = "hoi_18mbs"
    borderSize = {x = 0 y = 0}
    text = "999"
    maxWidth = 50
    maxHeight = 20
    format = left
}
```

<!-- kit:begin id="interface-correction" at="section:Interface" -->
**Kit correction** In 1.19.3 the `resources` window in `interface/countryproductionlineview.gui` is a `containerWindowType` that holds two elements per resource, `<resource>_icon` and `<resource>_checkbox`. It has no `<resource>_value` text box. All bullets below: [vanilla-confirmed 1.19.3] `interface/countryproductionlineview.gui`.

- `<resource>_icon` is an `iconType` (not a `buttonType`) with `spriteType = "GFX_resources_strip"` and a hard-coded `frame`. Each one has a commented-out `#pdx_tooltip = "PRODUCTION_MATERIALS_<RESOURCE>"` line.
- `<resource>_checkbox` is a `buttonType` with `quadTextureSprite = "GFX_generic_checkbox"`.
- The seven pairs run left to right in this order: oil, rubber, steel, aluminium, tungsten, chromium, coal. The window is 462 wide; the coal icon sits at `x = 396` and its checkbox at `x = 424`.
- Each `frame` repeats the `icon_frame` from the resource file. The two places must agree, and the positions are set by hand, so adding a resource means editing this window.

`GFX_resources_strip` is also used by `interface/countrydiplomacyview.gui`, `interface/countryintelledger.gui` and `interface/countrylogisticsview.gui`. [vanilla-confirmed 1.19.3] `interface/countryproductionlineview.gui`
<!-- kit:end id="interface-correction" -->

### Additional notes <a id="Additional_notes"></a>

A fuel can also correspond to the fuel dynamic, however only one resource at a time can do that. This is decided by the FUEL_RESOURCE [define](<defines.md>).
Infrastructure's bonus on resource gain is decided by the INFRASTRUCTURE_RESOURCE_BONUS define and applies to all resources the same.

<!-- kit:begin id="resource-defines" at="section:Additional_notes" -->
**Kit note** The resource-related defines in 1.19.3. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Group | Vanilla value | Meaning |
| --- | --- | --- | --- |
| `OIL_RESOURCE` | `NGame` | `"oil"` | name of the oil resource |
| `FUEL_RESOURCE` | `NGame` | `"oil"` | resource that gives the country fuel |
| `ENERGY_RESOURCE` | `NGame` | `"coal"` | resource that gives the country energy |
| `RESOURCE_TO_ENERGY_COEFFICIENT` | `NProduction` | `9.0` | energy produced per unit of the energy resource |
| `MAX_EQUIPMENT_RESOURCES_NEED` | `NProduction` | `3` | most different resources one equipment type can depend on |
| `INFRASTRUCTURE_RESOURCE_BONUS` | `NBuildings` | `0.15` | multiplicative resource bonus per level of undamaged infrastructure |
| `SUPPLY_ROUTE_RESOURCE_BONUS` | `NBuildings` | `0.2` | multiplicative resource bonus for a railway or naval link to the capital |
| `MIN_FACTORIES_TO_WANT_TO_IMPORT` | `NAI` | one entry per resource | civilian factories the AI needs before it imports that resource |

The wiki sentence above about fuel is `FUEL_RESOURCE`. The energy resource has its own define, `ENERGY_RESOURCE`.
<!-- kit:end id="resource-defines" -->

<!-- kit:begin id="resource-script-surface" at="section:Additional_notes" -->
#### Kit: Where script names a resource <a id="kit-resource-script-surface"></a>

All rows: [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`, `documentation/modifiers_documentation.md`.

| Kind | Name | Scope | Arguments or meaning |
| --- | --- | --- | --- |
| Effect | `add_resource` | state or country | `type`, `amount`, `state`, optional `days` (temporary), optional `show_state_in_tooltip` |
| Effect | `modify_building_resources` | country | `building`, `resource`, `amount` |
| Effect | `give_resource_rights` | country | `receiver`, `state`, optional `resources = { ... }` |
| Effect | `remove_resource_rights` | country | `remove_resource_rights = ID` |
| Trigger | `has_resources_amount` | state | `resource`, `amount`, optional `state`, optional `delivered` |
| Trigger | `has_resources_in_country` | country | `resource`, `amount`, optional `only_imported`, `extracted`, `buildings` |
| Trigger | `has_resources_in_collection` | country | `collection` plus resource amounts |
| Trigger | `has_resources_rights` | state or country | optional `state`, `receiver`, `resources`; always false if the state has no resource |
| Trigger | `resource_count_trigger` | state or country | `<resource> < <int>` |
| Modifier | `country_resource_<Resource>`, `country_resource_cost_<Resource>` | country | the key ends in a resource name, for example `country_resource_oil = 20` |
| Modifier | `state_resource_<Resource>`, `temporary_state_resource_<Resource>`, `state_resource_cost_<Resource>`, `state_resources_<Resource>_factor` | state | per-resource state values |
| Modifier | `local_resources`, `local_resources_factor`, `state_resources_factor`, `local_resource_gain_efficiency_per_infrastructure` | state | not tied to one resource |
| Modifier | `production_lack_of_resource_penalty_factor`, `resource_trade_cost_bonus_per_factory`, `resources_to_overlord_factor` | country or autonomy | trade and production penalties |

The modifier documentation lists exactly the seven vanilla resource keys as the modified types of every `<Resource>` family. `country_resource_oil` appears in two traits of `common/country_leader/00_traits.txt` and `temporary_state_resource_oil` in `common/dynamic_modifiers/0_dynamic_modifiers.txt`; 83 vanilla files under `common`, `events` and `history` use `add_resource`. [vanilla-confirmed 1.19.3]
<!-- kit:end id="resource-script-surface" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>) • [Units](<unit-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
