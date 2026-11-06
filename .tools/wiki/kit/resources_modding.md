# Resources modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="73143" sources="common/resources/ interface/general_stuff.gfx interface/countryproductionlineview.gui gfx/interface/resources_strip.dds common/defines/00_defines.lua localisation/english/production_l_english.yml localisation/english/core_l_english.yml history/states/ documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `common/resources/_documentation.md` and `00_resources.txt`, the strip sprites and the production GUI, the resource defines, the localisation files and the effects, triggers and modifiers that name a resource.
Kit blocks added: the vanilla resource table, strip size, localisation keys, one correction for the production GUI (no `<resource>_value` text box), the resource defines, and a table of the script that names resources.
Gaps left: the wiki claim that `cic` cannot exceed 1 is not stated in any game file. Adding or removing a resource was not tested in the game.
**1.19.4.1 re-check (2026-11-01).** 7 kit statements depended on files the update changed (the defines file, state history, `interface/general_stuff.gfx`, the production and core localisation, interface files that use the resource strip, and scripts scanned for `add_resource` and resource modifiers) and all were re-measured. Changed: 511 state files (was 512, one `resources` block is commented out) have a `resources` block, and `GFX_resources_strip` is used by six other interface files, not three. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="vanilla-resources" at="section:resources" -->
Vanilla 1.19.3 defines seven resources in `common/resources/00_resources.txt`, in this order. All seven use `cic = 0.125` and `convoys = 0.1`. [vanilla-confirmed 1.19.3]

| `icon_frame` | Resource key |
| --- | --- |
| 1 | `oil` |
| 2 | `aluminium` |
| 3 | `rubber` |
| 4 | `tungsten` |
| 5 | `steel` |
| 6 | `chromium` |
| 7 | `coal` |

The game's own note in `common/resources/_documentation.md`: when you add a resource or change the order, update the define `NAI.MIN_FACTORIES_TO_WANT_TO_IMPORT`. It is a list with one number per resource in file order (vanilla: `0` for the first six, `10` for `coal`). [docs] `common/resources/_documentation.md`. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`.

Resource keys are plain lowercase identifiers that other script repeats: the state block `resources = { steel = 6 }` (511 of 1081 vanilla state files have a `resources` block), the equipment block `resources = { steel = 2 }`, and the `type` or `resource` argument of the effects and triggers in the table at the end of this page. [vanilla-confirmed 1.19.4.1] `history/states/`, `common/units/equipment/infantry.txt`.
<!-- kit:end id="vanilla-resources" -->

<!-- kit:begin id="strip-size" at="section:icon-frame" -->
`gfx/interface/resources_strip.dds` and `gfx/interface/missing_resources_strip.dds` are both 189 x 27 pixels, which is seven frames of 27 x 27. The sprites `GFX_resources_strip` and `GFX_missing_resources_strip` both set `noOfFrames = 7` in `interface/general_stuff.gfx`. [vanilla-confirmed 1.19.4.1] DDS headers of both files, `interface/general_stuff.gfx`.
<!-- kit:end id="strip-size" -->

<!-- kit:begin id="loc-keys" at="section:localization" -->
Vanilla keeps the name keys in `localisation/english/production_l_english.yml` (`PRODUCTION_MATERIALS_OIL`, `PRODUCTION_MATERIALS_ALUMINIUM`, and so on, one per resource) and the descriptions in `localisation/english/core_l_english.yml` (`oil_desc`, `aluminium_desc`, `rubber_desc`, `tungsten_desc`, `steel_desc`, `chromium_desc`, `coal_desc`). Vanilla writes both without the `:0` version number. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="loc-keys" -->

<!-- kit:begin id="interface-correction" at="section:interface" -->
In 1.19.3 the `resources` window in `interface/countryproductionlineview.gui` is a `containerWindowType` that holds two elements per resource, `<resource>_icon` and `<resource>_checkbox`. It has no `<resource>_value` text box. All bullets below: [vanilla-confirmed 1.19.3] `interface/countryproductionlineview.gui`.

- `<resource>_icon` is an `iconType` (not a `buttonType`) with `spriteType = "GFX_resources_strip"` and a hard-coded `frame`. Each one has a commented-out `#pdx_tooltip = "PRODUCTION_MATERIALS_<RESOURCE>"` line.
- `<resource>_checkbox` is a `buttonType` with `quadTextureSprite = "GFX_generic_checkbox"`.
- The seven pairs run left to right in this order: oil, rubber, steel, aluminium, tungsten, chromium, coal. The window is 462 wide; the coal icon sits at `x = 396` and its checkbox at `x = 424`.
- Each `frame` repeats the `icon_frame` from the resource file. The two places must agree, and the positions are set by hand, so adding a resource means editing this window.

`GFX_resources_strip` is also used by `interface/countrydiplomacyview.gui`, `interface/countryintelledger.gui`, `interface/countrylogisticsview.gui`, `interface/countrystateview.gui`, `interface/countrytradeview.gui` and `interface/mapicons.gui`. [vanilla-confirmed 1.19.4.1] `interface/countryproductionlineview.gui`, `interface/`
<!-- kit:end id="interface-correction" -->

<!-- kit:begin id="resource-defines" at="section:additional-notes" -->
The resource-related defines in 1.19.4.1. All rows: [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`.

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

<!-- kit:begin id="resource-script-surface" at="section:additional-notes" -->
#### Where script names a resource

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

The modifier documentation lists exactly the seven vanilla resource keys as the modified types of every `<Resource>` family. `country_resource_oil` appears in two traits of `common/country_leader/00_traits.txt` and `temporary_state_resource_oil` in `common/dynamic_modifiers/0_dynamic_modifiers.txt`; 83 vanilla files under `common`, `events` and `history` use `add_resource`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="resource-script-surface" -->
