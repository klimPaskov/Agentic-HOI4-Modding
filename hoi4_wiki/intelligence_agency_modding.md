# Intelligence agency modding

\*Available only with the La Résistance DLC enabled .\*

Cosmetically, country-specific intelligence agencies are used in mods only as a localisation and graphical interface, but this guide can also be used on creating generic intelligence agencies.

## Agency file

Intelligence agencies' cosmetics are defined and toggled for countries in it's respective definition in the agencies file, in `<yourmod>/common/intelligence_agencies`. By default, this is the `00_intelligence_agencies.txt` file. It is not recommended to overwrite the vanilla file, and instead to create a new one, for readability and to allow your mod to work better with future updates, DLCs, and other mods. An example for an intelligence agency definition is as follows:

```text
intelligence_agency = {
    picture = GFX_intelligence_agency_NOR_old_norse
    names = { "Hugin" "Munin" }

    default = {
        tag = NOR
    }
    available = {
        original_tag = NOR
    }
}
```

The `names` definition can list either hardcoded strings or localisation scopes (Vanilla files are typically hardcoded). They list out all the possible, random, names that can be given to the intelligence agency. These names are used when you call [create_intelligence_agency](effects.md), unless another name is provided in the effect. In this example, either Hugin or Munin are used as the intelligence agency name, which is randomly picked when the effect is called.

The `default` definition contains the trigger for the intelligence agency to be the default choice of any nation. For example, when you choose to create an intelligence agency when playing as the United Kingdom, it defaults with the MI6 icon and either 'SIS' or 'MI6' as it's title, which you can then edit from there.

The `available` definition contains the trigger for the intelligence agency to be a choice you can make when creating it manually. This only works with the icon, due to how the intelligence agency system works. For example, if you wanted to create a new generic intelligence agency icon, you could define it like so:

```text
intelligence_agency = {
    picture = GFX_intelligence_agency_mod_generic_1
    names = { "Svalbard Intelligence Group" } # This would not appear, but it's safer to have a name for it anyway.

    default = {
        always = yes # It's then in the random queue with the rest of the generic intelligence agencies. 'Rooke' is typically priority.
    }
    available = {
        always = yes
    }
}
```

Despite it being only a new icon, you must give it at least one possible name, or else the definition won't be valid.

Checks of the section above against `common/intelligence_agencies/00_intelligence_agencies.txt`, which holds 71 `intelligence_agency` blocks: 62 national agencies and 9 generic ones.

- Block shape: the top-level key is `intelligence_agency` and it repeats once per agency. All 71 blocks have `picture`, `names` and `available`, and 70 have `default` (the second Indian entry, `GFX_intelligence_agency_logo_RAJ_RAW`, has none). 59 have one `available` block and 12 have two (for example Romania and the first Chinese entry write `available = { always = yes }` and then a second `available` with the tag check). Which one counts is not documented, so write a single `available`. Which of two `available` blocks the engine reads is unverified.
- `names` is a list of quoted strings or of localisation keys, and one is picked at random. The file header says the same, and the wiki's "localisation scopes" is a slip. Ethiopia writes bare keys, `names = { fetno_derash arbegnoch }`, localised in `localisation/english/intelligence_agencies_l_english.yml`.
- `available` decides whether the picture is in the list of logos the player can choose from when creating the agency. `default` marks the entry a country gets when the agency is created without a chosen icon; the file header does not say so, but the effect text for `create_intelligence_agency = yes` speaks of creating "historical ones", and the wiki describes `default` the same way. That `default` is what picks the "historical" entry is unverified.
- National entries follow one habit: `default` tests `tag = X` and `available` tests `original_tag = X`, so a puppet or a country that changed tag can still pick its historical logo. Variants are split by conditions on government, focus or DLC: Germany has the Abwehr and, under `has_government = communism`, the Stasi; Japan switches to the Kempeitai once `JAP_establish_the_gunbatsu` is done; Belgium has three entries split on `has_dlc = "Gotterdammerung"`.
- The 9 generic entries use `default = { always = yes }` and `available = { always = yes }`, except `GFX_intelligence_agency_logo_generic_9` ("Hammer and Sickle"), which needs `has_government = communism` in `available`. The first generic entry in file order is "Rooke".
- The wiki's remark that a new agency "must have at least one name" does not hold. Every vanilla block has `names` and nothing documents a failure without it, but an `intelligence_agency` block with `picture`, `default = { tag = LUX }` and `available` and no `names` was accepted: no parse error, no crash, and an error.log equal to the clean control. After `create_intelligence_agency` ran for LUX, the agency existed and had a non-empty name, "Research and Analysis Wing", which is the `names` entry of vanilla's RAJ agency (`00_intelligence_agencies.txt`, line 787). So `names` is optional for the game to load and create the agency. Why that particular name was picked was not checked, and the Intelligence Agency window was not opened.

Vanilla entry with a focus condition:

```text
intelligence_agency = {
	picture = GFX_intelligence_agency_logo_JAP_Kempeitai
	names = { "Kempeitai" }
	default = {
		tag = JAP
		has_completed_focus = JAP_establish_the_gunbatsu
	}
	available = {
		original_tag = JAP
		OR = {
			has_government = neutrality
			has_government = fascism
		}
	}
}
```

The effect that uses these definitions, `create_intelligence_agency`, runs in country scope and does nothing if the agency already exists. `create_intelligence_agency = yes` creates the historical agency, the one whose `default` block matches. `create_intelligence_agency = { name = "..." icon = GFX_... }` chooses both. Vanilla `common/` uses the block form 31 times in 13 national focus files: 26 give a quoted `name` and a `GFX_intelligence_agency_logo_*` icon, two give a localisation key as `name`, one gives only a `name` and two give only an `icon`. It uses the `= yes` form 42 times in 27 files, one of them in a commented-out line (decisions such as `common/decisions/ITA.txt` and `SIA.txt`, a faction goal, scripted effects and many focus trees). The trigger `has_intelligence_agency = no` guards the effect in 65 places. Several of these focuses also test `has_dlc = "La Resistance"`, which fits the wiki's DLC note at the top of the page. `GFX_intelligence_agency_logo_AUS_evidenzbureau_democratic` is used as an `icon` in `common/national_focus/austria.txt` although no `intelligence_agency` block names it, so the icon of the effect needs only a sprite, not an entry in this file. The trigger is `has_intelligence_agency`.

## GFX

The GFX for the intelligence agencies is slightly more complicated than the standard icon; when you select an intelligence agencies' icon, the selection effect is **not automatically generated**. This means that you must create two frames when defining your icon in a .gfx file, an example of such is as follows:

```text
spriteType = {
    name = "GFX_intelligence_agency_NOR_old_norse"
    textureFile = "gfx/interface/operatives/agencies/agency_logo_NOR_old_norse.dds"
    noOfFrames = 2 # This means it is cut along the X axis 2 times.
}
```

The `noOfFrames` property means the number of times the sprite icon is split along the X axis, in this case: twice. In terms of intelligence agencies, you do not need to do more than define `noOfFrames` and to create both your frames for your sprite icon.

The image size of an intelligence agency logo is **234px** by **119px** (x by y). This means the mid-point between your two icon frames should be at 117 pixels along the X axis. The frame on the left should be your unedited, actual intelligence agency icon. The frame on the right should be your icon when it is selected in the intelligence agency creation screen. In vanilla, this means a 2-pixel thick stroke/border with a gradient from white down to the main colour of your agency, and a strong, quickly-fading drop shadow. Once you are sure this is all correct, your GFX definition should be as well.

By default, .gfx files for intelligence agencies are stored in `interface/countryintelligenceagencyview.gfx`, and the sprite icons are stored in `gfx/interface/operatives/agencies`.

Checks of the GFX section against vanilla.

- All 71 agency logos are `spriteType` entries with `noOfFrames = 2`, in `interface/countryintelligenceagencyview.gfx`, and the textures sit in `gfx/interface/operatives/agencies/`. A further sprite, `GFX_intelligence_agency_logo_bg`, has no frame count.
- The wiki size is right with one correction: the 71 logo textures are 119 px high and either 234 px wide (37 files) or 233 px wide (34 files).
- The sprite name is free. Vanilla names its sprites `GFX_intelligence_agency_logo_<id>`, and the example name on this page works because the `picture` key only has to match a sprite. Put the sprite in your own `interface/*.gfx` file and keep the texture path under `gfx/` (all 165 `texturefile` lines in that file start with `gfx/`).
- Agency upgrades use different sprites: see the sizes in the section "Agency upgrades" at the bottom of this page.

## References

## Agency upgrades

Agency upgrades are separate from the cosmetic agency definition above. They live in `common/intelligence_agency_upgrades/`, which holds `_documentation.md` and `intelligence_agency_upgrades.txt`. Vanilla defines 21 upgrades in 5 branches with 31 levels in all. Operations are a different system; see [Intelligence operation modding](intelligence_operation_modding.md).

### Upgrade file format

The top-level keys are branch names and each branch holds upgrades. An upgrade token must be unique across all branches.

```text
branch_crypto = {
	upgrade_decryption_boost = {
		picture = GFX_agency_decryption_boost_1
		sound = Spy_Agency_Cryptology_Upgrades_Confirm
		ai_will_do = { factor = 2 }
		available = { has_done_agency_upgrade = upgrade_form_department }
		modifiers_during_progress = { civilian_factory_use = 5 }
		level = { modifier = { decryption_power = 25 } }
		level = { modifier = { decryption_power = 10 } }
	}
}
```

Keys of an upgrade. Counts are vanilla upgrades that use the key, out of 21.

| Key | Meaning | Vanilla |
| --- | --- | --- |
| `picture` | GFX sprite of the icon. | 21; the 21 textures are 68 by 68 px |
| `frame` | GFX name of the icon border, given without a suffix; optional, default `upgrade_frame_1`. | 6, each a themed set: `GFX_upgrade_frame_economy`, `_army`, `_naval`, `_airforce`, `_defense`, `_form` |
| `sound` | Sound entry played on click; optional, default `click_default`. | 20, plus one written `Sound =` with a capital S in `upgrade_training_centers` |
| `ai_will_do` | Modifiable value for the AI, for example `factor` with `modifier` blocks. | 21: 20 write `factor`, `upgrade_form_department` writes `base = 2` with a `modifier` for `original_tag = ENG` |
| `modifiers_during_progress` | Modifiers that apply while the upgrade is being done, for example its factory cost. | 21, always `civilian_factory_use`: 5 in 14, 8 in 4, 10 in 2, 15 in 1 |
| `visible` | Trigger, like a decision; optional. | 0 |
| `available` | Trigger, like a decision; optional. If false the upgrade is shown but locked. | 5, using `has_done_agency_upgrade` and `has_tech` |
| `level` | Repeatable block, one per level, holding `modifier = { ... }` and an optional `complete_effect = { ... }`. | 31 blocks in total; 15 upgrades have one level, `upgrade_passive_defense` has 4 |

### Branches, names and levels

- Branches are the five keys `branch_intelligence` (4 upgrades), `branch_defense` (2), `branch_operation` (5), `branch_operative` (5) and `branch_crypto` (5). The branch titles are localisation keys with the same names in `localisation/english/operatives_l_english.yml`.
- An upgrade has no `description` key. Its name is the localisation key `<upgrade token>` and its description is `<upgrade token>_desc`. Vanilla follows this, for example `upgrade_economy_civilian` and `upgrade_economy_civilian_desc`.
- The branch list of the upgrade window is a one-column gridbox named `branches_grid`, and vanilla gives each of its five branches a localisation key and an `intelligence_agency_branch_desire_factor` AI strategy. A new branch of your own would need the same two things; nothing states that extra branches display correctly, so whether a sixth branch shows in the window is unverified.
- Each `level` block lists the modifiers of that level. Vanilla writes the step of each level, for example four `intelligence_agency_defense` levels of 1.5, 1.25, 1 and 1 in `upgrade_passive_defense`, which suggests the levels add up. That reading is not documented. The levels do add up: `intelligence_agency_defense`, read in country scope with `THIS.modifier@intelligence_agency_defense`, was 0 after the agency was created, 1.5 after level 1 and 2.75 (1.5 plus 1.25) after level 2, with no error.log line for the read. Levels 3 and 4 were not read.
- `complete_effect` runs when its level is researched, in country scope: the one vanilla use is `unlock_decision_category_tooltip = lar_local_recruitment` in `upgrade_training_centers`.
- `has_done_agency_upgrade = <token>` is true once the upgrade has been done to its highest level, and `agency_upgrade_number` counts the upgrades done.

### Progress cost, timing and modifiers

- While an upgrade is being researched, `modifiers_during_progress` applies; vanilla uses it only to tie up civilian factories with `civilian_factory_use`, a country modifier.
- Base numbers from the defines: `AGENCY_CREATION_DAYS` 30, `AGENCY_UPGRADE_DAYS` 30, `AGENCY_CREATION_FACTORIES` 5, `AGENCY_UPGRADE_PER_OPERATIVE_SLOT` 5 (upgrades needed per extra operative slot), `MAX_OPERATIVE_SLOT_FROM_AGENCY_UPGRADES` 1, `BECOME_SPYMASTER_MIN_UPGRADES` 3 and `AGENCY_DEFENSE_EFFECT_ON_HOSTILE_ACTION_COST` 0.2. See [Defines](defines.md). A country modifier `agency_upgrade_time` exists in the `country` category.
- The level modifiers in vanilla are almost all of category `intelligence_agency`: `civilian_intel_factor`, `army_intel_factor`, `navy_intel_factor`, `airforce_intel_factor`, `intelligence_agency_defense`, `root_out_resistance_effectiveness_factor`, `intel_from_operatives_factor`, `crypto_department_enabled`, `crypto_strength`, `decryption_power`, `enemy_operative_recruitment_chance`, `occupied_operative_recruitment_chance`, `new_operative_slot_bonus`, `commando_trait_chance_factor`, `control_trade_mission_factor`, `diplomatic_pressure_mission_factor`, `propaganda_mission_factor`, `boost_ideology_mission_factor`, `boost_resistance_factor`, `target_sabotage_factor`, `operative_death_on_capture_chance`. Three more are in other categories: `enemy_operative_capture_chance_factor` and `enemy_operative_intel_extraction_rate` (unit leader and country) and `own_operative_detection_chance`.
- `operation_steal_tech_outcome`, `operation_steal_tech_risk` and `operation_coordinated_strike_outcome` are not listed by name in the modifier documentation. They are instances of the documented `<Operation>_outcome` and `<Operation>_risk` templates, whose operation tokens come from `common/operations/`.

### AI and script

- The upgrade-level `ai_will_do` is the per-upgrade weight. Country-level pacing is set by AI strategies, all in `common/ai_strategy/default.txt`: `intelligence_agency_branch_desire_factor` with `id = branch_intelligence` and `branch_defense` at 1000, `branch_operation` at 500, `branch_operative` at 100 and `branch_crypto` at 2000, `intelligence_agency_usable_factories` (4 entries), and `agency_ai_base_num_factories_factor` and `agency_ai_per_upgrade_factories_factor`. The defines `AGENCY_AI_BASE_NUM_FACTORIES` (25.0) and `AGENCY_AI_PER_UPGRADE_FACTORIES` (6.0) pace the AI as described in their comments.
- `upgrade_intelligence_agency = <upgrade token>` adds an upgrade to the country's agency, which must exist already. Vanilla guards it with `NOT = { has_done_agency_upgrade = <token> }`, usually together with `has_dlc = "La Resistance"`. What the effect does on an upgrade that is already complete is not described, and the number of levels per call is not stated. One call adds one level: after `upgrade_intelligence_agency = upgrade_passive_defense` four times, `agency_upgrade_number` read 1, 2, 3 and 4, and `has_done_agency_upgrade` turned TRUE only after the fourth call. Only one upgrade was used, so counting levels cannot be told from counting steps of that upgrade. Calls on a finished upgrade change nothing: five more calls left the level at 4 and `has_done_agency_upgrade` TRUE, with no new error.log line and no crash.
- Traps: an upgrade token that repeats across branches breaks the uniqueness rule. A `frame` value needs a matching set of frame sprites, described below. Which suffixes the engine reads (`_available` or `_current`) is unverified.

### Upgrade GFX

- The documentation says a frame needs the suffixes `_available`, `_completed` and `_unavailable`. Vanilla defines `_unavailable`, `_current` and `_completed` for `GFX_upgrade_frame_1` and each themed frame, and the `_available` texture sits in commented-out lines (the `form` frame instead uses its `_available` texture for the `_current` sprite). Define the three vanilla suffixes for a custom frame.
- Vanilla frame textures are 139 by 74 px (22 files `gfx/interface/operatives/upgrade_frame_*.dds`), and the 21 upgrade pictures are 68 by 68 px, mostly under `gfx/interface/operatives/`.
