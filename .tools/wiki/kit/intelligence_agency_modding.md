# Intelligence agency modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="91095" sources="common/intelligence_agencies/ common/intelligence_agency_upgrades/ common/ai_strategy/default.txt common/defines/00_defines.lua common/national_focus/ common/decisions/ITA.txt common/operations/00_operations.txt interface/countryintelligenceagencyview.gfx interface/countryintelligenceagencyview.gui gfx/interface/operatives/ documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md localisation/english/intelligence_agencies_l_english.yml localisation/english/operatives_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against `common/intelligence_agencies/00_intelligence_agencies.txt` (71 agency definitions), `common/intelligence_agency_upgrades/` (`_documentation.md` and the 21 vanilla upgrades), `interface/countryintelligenceagencyview.gfx`, the agency GFX files, the agency defines, the agency effects, triggers and modifiers in `documentation/`, the AI strategy entries for agencies and the vanilla uses of `create_intelligence_agency` and `upgrade_intelligence_agency`.
- Kit blocks added: checks of the agency file format against vanilla (`names`, `default`, `available`, generic agencies, duplicated `available`), the `create_intelligence_agency` forms, GFX sizes and sprite names, and a new section for agency upgrades (file format, every key, branches, levels, progress cost, modifiers, AI, script, GUI sprites, defines).
- Errors found in the wiki text: `names` takes quoted strings or localisation keys, not localisation scopes; the upgrade documentation's `_available` frame suffix is not what vanilla defines (`_unavailable`, `_current`, `_completed`).
- Gaps left: operations are covered by [Intelligence operation modding](<intelligence_operation_modding.md>). Which of two `available` blocks counts and how the game ranks several matching `default` blocks are not documented. A test run on 2026-11-02 settled that `upgrade_intelligence_agency` advances one level per call and that the modifiers of the levels add up (tagged `[game-tested 1.19.4.1]`). Nothing else on this page was run in the game.
**1.19.4.1 re-check (2026-11-01).** 19 tagged statements depended on files the update changed (the agency definitions, the agency GFX and GUI files, `ai_strategy/default.txt`, operative localisation and national focus files) and all were re-measured. Changed: 71 agency blocks (62 national) and 71 logo sprites (37 textures 234 px wide) after a new Indian entry, `RAJ_RAW` now has no `default`, `create_intelligence_agency = yes` appears 42 times, only 26 of 31 block-form calls give a literal name and logo icon, and `intelligence_agency_usable_factories` has 4 entries (was 6). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="ia-agency-file-checks" at="section:agency-file" -->
Checks of the section above against `common/intelligence_agencies/00_intelligence_agencies.txt`, which holds 71 `intelligence_agency` blocks: 62 national agencies and 9 generic ones. [vanilla-confirmed 1.19.4.1] `common/intelligence_agencies/00_intelligence_agencies.txt`.

- Block shape: the top-level key is `intelligence_agency` and it repeats once per agency. All 71 blocks have `picture`, `names` and `available`, and 70 have `default` (the second Indian entry, `GFX_intelligence_agency_logo_RAJ_RAW`, has none). 59 have one `available` block and 12 have two (for example Romania and the first Chinese entry write `available = { always = yes }` and then a second `available` with the tag check). Which one counts is not documented, so write a single `available`. [vanilla-confirmed 1.19.4.1] `common/intelligence_agencies/00_intelligence_agencies.txt` (the header comment does not say). Which of two `available` blocks the engine reads is [unverified].
- `names` is a list of quoted strings or of localisation keys, and one is picked at random. The file header says the same, and the wiki's "localisation scopes" is a slip. Ethiopia writes bare keys, `names = { fetno_derash arbegnoch }`, localised in `localisation/english/intelligence_agencies_l_english.yml`. [vanilla-confirmed 1.19.4.1] `common/intelligence_agencies/00_intelligence_agencies.txt`, `localisation/english/intelligence_agencies_l_english.yml`.
- `available` decides whether the picture is in the list of logos the player can choose from when creating the agency. [vanilla-confirmed 1.19.4.1] header comment of `common/intelligence_agencies/00_intelligence_agencies.txt`. `default` marks the entry a country gets when the agency is created without a chosen icon; the file header does not say so, but the effect text for `create_intelligence_agency = yes` speaks of creating "historical ones", and the wiki describes `default` the same way. [docs] `documentation/effects_documentation.md`. That `default` is what picks the "historical" entry is [unverified].
- National entries follow one habit: `default` tests `tag = X` and `available` tests `original_tag = X`, so a puppet or a country that changed tag can still pick its historical logo. Variants are split by conditions on government, focus or DLC: Germany has the Abwehr and, under `has_government = communism`, the Stasi; Japan switches to the Kempeitai once `JAP_establish_the_gunbatsu` is done; Belgium has three entries split on `has_dlc = "Gotterdammerung"`. [vanilla-confirmed 1.19.4.1] `common/intelligence_agencies/00_intelligence_agencies.txt`.
- The 9 generic entries use `default = { always = yes }` and `available = { always = yes }`, except `GFX_intelligence_agency_logo_generic_9` ("Hammer and Sickle"), which needs `has_government = communism` in `available`. The first generic entry in file order is "Rooke". [vanilla-confirmed 1.19.4.1] `common/intelligence_agencies/00_intelligence_agencies.txt`.
- The wiki's remark that a new agency "must have at least one name" does not hold. Every vanilla block has `names` and nothing documents a failure without it, but an `intelligence_agency` block with `picture`, `default = { tag = LUX }` and `available` and no `names` was accepted: no parse error, no crash, and an error.log equal to the clean control. After `create_intelligence_agency` ran for LUX, the agency existed and had a non-empty name, "Research and Analysis Wing", which is the `names` entry of vanilla's RAJ agency (`00_intelligence_agencies.txt`, line 787). So `names` is optional for the game to load and create the agency. Why that particular name was picked was not checked, and the Intelligence Agency window was not opened. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log and a script probe read in game.log.

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

Source of the example (whitespace changed): [vanilla-confirmed 1.19.4.1] `common/intelligence_agencies/00_intelligence_agencies.txt`.

The effect that uses these definitions, `create_intelligence_agency`, runs in country scope and does nothing if the agency already exists. `create_intelligence_agency = yes` creates the historical agency, the one whose `default` block matches. `create_intelligence_agency = { name = "..." icon = GFX_... }` chooses both. [docs] `documentation/effects_documentation.md`. Vanilla `common/` uses the block form 31 times in 13 national focus files: 26 give a quoted `name` and a `GFX_intelligence_agency_logo_*` icon, two give a localisation key as `name`, one gives only a `name` and two give only an `icon`. It uses the `= yes` form 42 times in 27 files, one of them in a commented-out line (decisions such as `common/decisions/ITA.txt` and `SIA.txt`, a faction goal, scripted effects and many focus trees). The trigger `has_intelligence_agency = no` guards the effect in 65 places. Several of these focuses also test `has_dlc = "La Resistance"`, which fits the wiki's DLC note at the top of the page. [vanilla-confirmed 1.19.4.1] `common/national_focus/argentina.txt`, `common/national_focus/austria.txt`, `common/decisions/ITA.txt`. `GFX_intelligence_agency_logo_AUS_evidenzbureau_democratic` is used as an `icon` in `common/national_focus/austria.txt` although no `intelligence_agency` block names it, so the icon of the effect needs only a sprite, not an entry in this file. [vanilla-confirmed 1.19.4.1] `common/national_focus/austria.txt`, `interface/countryintelligenceagencyview.gfx`. The trigger is `has_intelligence_agency`. [docs] `documentation/triggers_documentation.md`.
<!-- kit:end id="ia-agency-file-checks" -->

<!-- kit:begin id="ia-gfx-checks" at="section:gfx" -->
Checks of the GFX section against vanilla.

- All 71 agency logos are `spriteType` entries with `noOfFrames = 2`, in `interface/countryintelligenceagencyview.gfx`, and the textures sit in `gfx/interface/operatives/agencies/`. A further sprite, `GFX_intelligence_agency_logo_bg`, has no frame count. [vanilla-confirmed 1.19.4.1] `interface/countryintelligenceagencyview.gfx`.
- The wiki size is right with one correction: the 71 logo textures are 119 px high and either 234 px wide (37 files) or 233 px wide (34 files). [vanilla-confirmed 1.19.4.1] header read of the `.dds` files in `gfx/interface/operatives/agencies/`.
- The sprite name is free. Vanilla names its sprites `GFX_intelligence_agency_logo_<id>`, and the example name on this page works because the `picture` key only has to match a sprite. [vanilla-confirmed 1.19.4.1] `interface/countryintelligenceagencyview.gfx`. Put the sprite in your own `interface/*.gfx` file and keep the texture path under `gfx/` (all 165 `texturefile` lines in that file start with `gfx/`). [vanilla-confirmed 1.19.4.1] `interface/countryintelligenceagencyview.gfx`.
- Agency upgrades use different sprites: see the sizes in the section "Agency upgrades" at the bottom of this page.
<!-- kit:end id="ia-gfx-checks" -->

<!-- kit:begin id="ia-upgrades" at="bottom" -->
## Agency upgrades

Agency upgrades are separate from the cosmetic agency definition above. They live in `common/intelligence_agency_upgrades/`, which holds `_documentation.md` and `intelligence_agency_upgrades.txt`. Vanilla defines 21 upgrades in 5 branches with 31 levels in all. [vanilla-confirmed 1.19.3] `common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt`. Operations are a different system; see [Intelligence operation modding](intelligence_operation_modding.md).

### Upgrade file format

The top-level keys are branch names and each branch holds upgrades. An upgrade token must be unique across all branches. [docs] `common/intelligence_agency_upgrades/_documentation.md`.

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

Source of the example (compacted from the vanilla block): [vanilla-confirmed 1.19.3] `common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt`.

Keys of an upgrade. Counts are vanilla upgrades that use the key, out of 21.

| Key | Meaning | Vanilla |
| --- | --- | --- |
| `picture` | GFX sprite of the icon. [docs] | 21; the 21 textures are 68 by 68 px |
| `frame` | GFX name of the icon border, given without a suffix; optional, default `upgrade_frame_1`. [docs] | 6, each a themed set: `GFX_upgrade_frame_economy`, `_army`, `_naval`, `_airforce`, `_defense`, `_form` |
| `sound` | Sound entry played on click; optional, default `click_default`. [docs] | 20, plus one written `Sound =` with a capital S in `upgrade_training_centers` |
| `ai_will_do` | Modifiable value for the AI, for example `factor` with `modifier` blocks. [docs] | 21: 20 write `factor`, `upgrade_form_department` writes `base = 2` with a `modifier` for `original_tag = ENG` |
| `modifiers_during_progress` | Modifiers that apply while the upgrade is being done, for example its factory cost. [docs] | 21, always `civilian_factory_use`: 5 in 14, 8 in 4, 10 in 2, 15 in 1 |
| `visible` | Trigger, like a decision; optional. [docs] | 0 |
| `available` | Trigger, like a decision; optional. If false the upgrade is shown but locked. [docs] | 5, using `has_done_agency_upgrade` and `has_tech` |
| `level` | Repeatable block, one per level, holding `modifier = { ... }` and an optional `complete_effect = { ... }`. [docs] | 31 blocks in total; 15 upgrades have one level, `upgrade_passive_defense` has 4 |

The "Vanilla" column: [vanilla-confirmed 1.19.3] `common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt`.

### Branches, names and levels

- Branches are the five keys `branch_intelligence` (4 upgrades), `branch_defense` (2), `branch_operation` (5), `branch_operative` (5) and `branch_crypto` (5). The branch titles are localisation keys with the same names in `localisation/english/operatives_l_english.yml`. [vanilla-confirmed 1.19.4.1] `common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt`, `localisation/english/operatives_l_english.yml`.
- An upgrade has no `description` key. Its name is the localisation key `<upgrade token>` and its description is `<upgrade token>_desc`. [docs] `common/intelligence_agency_upgrades/_documentation.md`. Vanilla follows this, for example `upgrade_economy_civilian` and `upgrade_economy_civilian_desc`. [vanilla-confirmed 1.19.4.1] `localisation/english/operatives_l_english.yml`.
- The branch list of the upgrade window is a one-column gridbox named `branches_grid`, and vanilla gives each of its five branches a localisation key and an `intelligence_agency_branch_desire_factor` AI strategy. [vanilla-confirmed 1.19.4.1] `interface/countryintelligenceagencyview.gui`, `common/ai_strategy/default.txt`. A new branch of your own would need the same two things; nothing states that extra branches display correctly, so whether a sixth branch shows in the window is [unverified].
- Each `level` block lists the modifiers of that level. Vanilla writes the step of each level, for example four `intelligence_agency_defense` levels of 1.5, 1.25, 1 and 1 in `upgrade_passive_defense`, which suggests the levels add up. [vanilla-confirmed 1.19.3] `common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt`. That reading is not documented. The levels do add up: `intelligence_agency_defense`, read in country scope with `THIS.modifier@intelligence_agency_defense`, was 0 after the agency was created, 1.5 after level 1 and 2.75 (1.5 plus 1.25) after level 2, with no error.log line for the read. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted effect and game.log read. Levels 3 and 4 were not read.
- `complete_effect` runs when its level is researched, in country scope: the one vanilla use is `unlock_decision_category_tooltip = lar_local_recruitment` in `upgrade_training_centers`. [docs] `common/intelligence_agency_upgrades/_documentation.md`. [vanilla-confirmed 1.19.3] `common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt`.
- `has_done_agency_upgrade = <token>` is true once the upgrade has been done to its highest level, and `agency_upgrade_number` counts the upgrades done. [docs] `documentation/triggers_documentation.md`.

### Progress cost, timing and modifiers

- While an upgrade is being researched, `modifiers_during_progress` applies; vanilla uses it only to tie up civilian factories with `civilian_factory_use`, a country modifier. [docs] `documentation/modifiers_documentation.md`. [vanilla-confirmed 1.19.3] `common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt`.
- Base numbers from the defines: `AGENCY_CREATION_DAYS` 30, `AGENCY_UPGRADE_DAYS` 30, `AGENCY_CREATION_FACTORIES` 5, `AGENCY_UPGRADE_PER_OPERATIVE_SLOT` 5 (upgrades needed per extra operative slot), `MAX_OPERATIVE_SLOT_FROM_AGENCY_UPGRADES` 1, `BECOME_SPYMASTER_MIN_UPGRADES` 3 and `AGENCY_DEFENSE_EFFECT_ON_HOSTILE_ACTION_COST` 0.2. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. See [Defines](defines.md). A country modifier `agency_upgrade_time` exists in the `country` category. [docs] `documentation/modifiers_documentation.md`.
- The level modifiers in vanilla are almost all of category `intelligence_agency`: `civilian_intel_factor`, `army_intel_factor`, `navy_intel_factor`, `airforce_intel_factor`, `intelligence_agency_defense`, `root_out_resistance_effectiveness_factor`, `intel_from_operatives_factor`, `crypto_department_enabled`, `crypto_strength`, `decryption_power`, `enemy_operative_recruitment_chance`, `occupied_operative_recruitment_chance`, `new_operative_slot_bonus`, `commando_trait_chance_factor`, `control_trade_mission_factor`, `diplomatic_pressure_mission_factor`, `propaganda_mission_factor`, `boost_ideology_mission_factor`, `boost_resistance_factor`, `target_sabotage_factor`, `operative_death_on_capture_chance`. Three more are in other categories: `enemy_operative_capture_chance_factor` and `enemy_operative_intel_extraction_rate` (unit leader and country) and `own_operative_detection_chance`. [docs] `documentation/modifiers_documentation.md`.
- `operation_steal_tech_outcome`, `operation_steal_tech_risk` and `operation_coordinated_strike_outcome` are not listed by name in the modifier documentation. They are instances of the documented `<Operation>_outcome` and `<Operation>_risk` templates, whose operation tokens come from `common/operations/`. [docs] `documentation/modifiers_documentation.md`. [vanilla-confirmed 1.19.3] `common/operations/00_operations.txt`.

### AI and script

- The upgrade-level `ai_will_do` is the per-upgrade weight. Country-level pacing is set by AI strategies, all in `common/ai_strategy/default.txt`: `intelligence_agency_branch_desire_factor` with `id = branch_intelligence` and `branch_defense` at 1000, `branch_operation` at 500, `branch_operative` at 100 and `branch_crypto` at 2000, `intelligence_agency_usable_factories` (4 entries), and `agency_ai_base_num_factories_factor` and `agency_ai_per_upgrade_factories_factor`. [vanilla-confirmed 1.19.4.1] `common/ai_strategy/default.txt`. The defines `AGENCY_AI_BASE_NUM_FACTORIES` (25.0) and `AGENCY_AI_PER_UPGRADE_FACTORIES` (6.0) pace the AI as described in their comments. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.
- `upgrade_intelligence_agency = <upgrade token>` adds an upgrade to the country's agency, which must exist already. [docs] `documentation/effects_documentation.md`. Vanilla guards it with `NOT = { has_done_agency_upgrade = <token> }`, usually together with `has_dlc = "La Resistance"`. [vanilla-confirmed 1.19.4.1] `common/national_focus/austria.txt`. What the effect does on an upgrade that is already complete is not described, and the number of levels per call is not stated. One call adds one level: after `upgrade_intelligence_agency = upgrade_passive_defense` four times, `agency_upgrade_number` read 1, 2, 3 and 4, and `has_done_agency_upgrade` turned TRUE only after the fourth call. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted effect and game.log read. Only one upgrade was used, so counting levels cannot be told from counting steps of that upgrade. Calls on a finished upgrade change nothing: five more calls left the level at 4 and `has_done_agency_upgrade` TRUE, with no new error.log line and no crash. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted effect, game.log and error.log read.
- Traps: an upgrade token that repeats across branches breaks the uniqueness rule. [docs] `common/intelligence_agency_upgrades/_documentation.md`. A `frame` value needs a matching set of frame sprites, described below. [docs] `common/intelligence_agency_upgrades/_documentation.md`. Which suffixes the engine reads (`_available` or `_current`) is [unverified].

### Upgrade GFX

- The documentation says a frame needs the suffixes `_available`, `_completed` and `_unavailable`. Vanilla defines `_unavailable`, `_current` and `_completed` for `GFX_upgrade_frame_1` and each themed frame, and the `_available` texture sits in commented-out lines (the `form` frame instead uses its `_available` texture for the `_current` sprite). Define the three vanilla suffixes for a custom frame. [vanilla-confirmed 1.19.4.1] `interface/countryintelligenceagencyview.gfx`.
- Vanilla frame textures are 139 by 74 px (22 files `gfx/interface/operatives/upgrade_frame_*.dds`), and the 21 upgrade pictures are 68 by 68 px, mostly under `gfx/interface/operatives/`. [vanilla-confirmed 1.19.4.1] header read of the `.dds` files, `interface/countryintelligenceagencyview.gfx`.
<!-- kit:end id="ia-upgrades" -->
