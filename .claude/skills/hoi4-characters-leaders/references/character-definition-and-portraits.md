# HOI4 Characters, Leaders and Traits: Character definition, portraits and localisation

Part of the [hoi4-characters-leaders](../SKILL.md) skill. Read before writing a character entry, wiring its portrait sprites, or localising characters, traits and parties.

## Character definition

Skeleton (wiki `Character modding` and vanilla `common/characters/GER.txt`):

```text
characters = {
	TAG_example_person = {
		name = TAG_example_person
		gender = female
		can_be_captured = no
		portraits = {
			civilian = {
				large = GFX_portrait_TAG_example_person
				small = GFX_portrait_TAG_example_person_small
			}
			army = {
				large = GFX_portrait_TAG_example_person_army
			}
		}
		country_leader = {
			ideology = liberalism
			traits = { my_leader_trait }
			expire = "1965.1.1.1"
		}
		advisor = {
			slot = political_advisor
			idea_token = TAG_example_person
			traits = { my_advisor_trait }
			cost = 150
			allowed = { original_tag = TAG }
			available = { has_completed_focus = TAG_some_focus }
			visible = { has_country_flag = TAG_person_visible }
			on_add = { }
			on_remove = { }
		}
		corps_commander = {
			traits = { }
			skill = 3
			attack_skill = 3
			defense_skill = 2
			planning_skill = 3
			logistics_skill = 2
		}
	}
}
```

Rules and notes:

- The character id (outer key) is what `recruit_character`, `promote_character` and scope entry use (`TAG_example_person = { ... }`). File names do not matter.
- `name`: a localisation key. If the name or portrait is missing, the engine generates them from gender, country name lists and portrait pools.
- `gender`: `undefined` (default, behaves like male in almost all respects), `male`, `female`. Used for pronouns in `[Character.GetSheHe]` style loc and for generating missing names or portraits.
- `can_be_captured = no`: general cannot be captured (installed `common/characters/_documentation.md`). Characters with a country leader role are always uncapturable.
- `instance = { allowed = { ... } <whole character body> }`: alternative definitions evaluated once at game start; each instance needs an `allowed` block and the character needs multiple instances to make sense (`common/characters/AFG.txt`). A single-state character should omit `instance`.
- One role block per slot: repeat `advisor = {}` for several slots; repeat `country_leader = {}` for several ideologies.
- Role keys seen in vanilla characters: `country_leader`, `advisor`, `corps_commander`, `field_marshal`, `navy_leader`, `scientist`, plus `allowed_civil_war` (a trigger block seen in vanilla, for example `GER_heinrich_himmler`; it is not in the sources read, so treat it as civil-war side selection by inference and check a vanilla example before using it).
- `id = -1` and `legacy_id = N` are leftovers from the pre-1.11 leader system. Omit them in new content and use character-specific triggers.
- Do not rely on file ordering; ids must be globally unique across all character files.

## Portraits and GFX wiring (overview)

- `portraits` has three categories: `civilian`, `army`, `navy`; each holds `large` and `small`. A small portrait in any category serves as an advisor portrait; a large portrait is used for leaders and commanders and is category-specific.
- Values are `spriteType` names defined in `interface/*.gfx` (the name must start with `GFX_`, contain no spaces and be ASCII), or direct `gfx/...` paths. Sprites are the recommended form (wiki).
- Army leaders also need a small portrait (officer corps ministers). Either define `small` explicitly or add a sprite named `<large_sprite_name>_small`; the `_small` suffix convention also applies to portraits drawn from `portraits/*.txt`.
- If a portrait definition is invalid the engine silently substitutes a random portrait. Check, in order: the sprite name spelling, the `interface/*.gfx` file extension and `spriteTypes = { }` wrapper, the `texturefile` path (forward slashes, extension included), and the file on disk.
- Wiki: if a category defines a valid sprite for one size but not the other, no random portrait is generated for the missing size, so it can show blank. Define both sizes.
- Characters without a portrait show a silhouette or nothing during country selection and receive a generated portrait only after the game starts (cosmetic tags decide the pool).
- Portraits can be changed in play with `set_portraits` (country scope with `character = X`, or character scope); animated portraits use `frameAnimatedSpriteType` (see `hoi4-frame-animation`).
- Conventional locations: advisor art in `gfx/interface/ideas/`, leader art in `gfx/leaders/<TAG>/`; the folder is not enforced.
- Portrait sprite casing is mixed in vanilla (`GFX_portrait_` and `GFX_Portrait_` are both declared), so copy the declared name exactly. [vanilla-confirmed 1.19.4.1]
- Prefer new `.gfx` files for mod sprites; a later-sorted file name overrides an earlier sprite of the same name (wiki `Character modding` > Portraits). Never edit vanilla `.gfx` files.
- Production of the art, grounded source handling, DDS conversion and manifests are not documented here: use `hoi4-feature-assets` and route every portrait to `hoi4_portrait_creator`.

## Localisation

- Character name: the `name` key, in a character name file (vanilla `nsb_characters_l_english.yml`). Keys defined once can be reused with `$other_key$`.
- Character description: the wiki states `<id>_desc`; country leader `desc` must be a key; vanilla characters mostly omit descriptions.
- Advisor idea token: `<idea_token>: "Name"` and optional `<idea_token>_desc`.
- Trait: `<trait>` and `<trait>_desc`; unit leader trait icon `GFX_trait_<trait>`.
- Ideology and party names: `parties_l_english.yml` pattern.
- Advisor ideas are ideas: for generic idea, spirit and modifier mechanics use `hoi4-ideas-modifiers`.
- A flag trigger such as `has_country_flag` placed in a player-visible `available` block uses the flag name as the tooltip key. Localise it or wrap it: `hidden_trigger` plus `custom_trigger_tooltip`.
- Localisation files: UTF-8 with BOM, `l_english:` header, keys without `:0` in this repository.

