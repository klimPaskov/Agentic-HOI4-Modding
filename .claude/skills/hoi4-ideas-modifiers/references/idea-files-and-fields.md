# HOI4 Ideas and Modifiers: Idea files, slots and fields

Part of the [hoi4-ideas-modifiers](../SKILL.md) skill. Read before writing an idea, adding a slot or category, or deciding which idea field to use.

## Ideas: files, categories, slots

- Ideas live in `common/ideas/*.txt`: `ideas = { <slot_or_category> = { <idea_id> = { ... } } }`. Keep idea ids unique across files and slots (duplicate-id resolution is unverified). Files load in Unicode filename order (capitals, then underscore, then lowercase).
- Category and slot declarations live in `common/idea_tags/*.txt` under `idea_categories = { ... }` with keys `slot`, `character_slot`, `type`, `cost`, `removal_cost`, `ledger`, `hidden`, `politics_tab`. Vanilla `GAME/common/idea_tags/00_idea.txt` declares `hidden_ideas` (`hidden = yes`, `removal_cost = -1`), `country` (`type = national_spirit`, `cost = 0`, `removal_cost = -1`), `government` (slots `economy`, `trade_laws`, `mobilization_laws`, character slots `political_advisor` x3), `research_production`, `military_staff`, and spirit categories with `type = army_spirit`, `navy_spirit`, `air_spirit`.
- The block name inside `ideas = { }` is the slot (or the category for `country` and `hidden_ideas`): `economy = { law = yes ... }`, `tank_manufacturer = { designer = yes ... }`, `political_advisor = { ... }`.
- A new slot needs a category entry, a sprite `GFX_idea_slot_<slot>` for the empty-slot icon (see `GAME/interface/countrypoliticsview.gfx`), and GUI room: the politics view gridbox defaults to 7 horizontal slots per row, and `GFX_idea_categories` is a frame strip whose frame count must match the number of categories (`WIKI/idea_modding.md`, GFX and GUI).
- Cost factors: the modifier `<slot>_cost_factor` only works if the slot already has an idea or character defined when the modifier is loaded. Idea files starting with a capital letter load before `_economic.txt` and `_manpower.txt`, so an idea in `GER.txt` using `economy_cost_factor` errors; name country idea files with lowercase initials or add a placeholder idea in an earlier-loading file. Character slots (for example `political_advisor_cost_factor`) need at least one idea defined in the slot for the same reason.

## Idea body: every field that matters

Frequencies are from the 6,000-plus ideas in `GAME/common/ideas/` (each field's count is how often vanilla uses it): `allowed`, `picture`, `modifier`, `removal_cost`, `allowed_civil_war`, `traits`, `name`, `research_bonus`, `ai_will_do`, `available`, `equipment_bonus`, `visible`, `ledger`, `targeted_modifier`, `cancel`, `cost`, `do_effect`, `on_remove`, `on_add`, `rule`, `cancel_if_invalid`, `allowed_to_remove`, `level`, `default`.

```
ideas = {
	country = {
		example_spirit = {
			allowed = { always = no }          # event/focus-granted only; add_ideas bypasses it
			allowed_civil_war = { always = yes }
			picture = generic_war_preparation  # sprite GFX_idea_generic_war_preparation
			name = shared_display_name         # optional alternate loc key
			modifier = {
				political_power_gain = 0.1
				stability_factor = -0.05
				custom_modifier_tooltip = example_spirit_tt
			}
			targeted_modifier = { tag = QAT defense_bonus_against = 0.2 }
			research_bonus = { infantry = 0.1 }
			equipment_bonus = { infantry_equipment = { instant = yes defense = 0.2 } }
			rule = { can_join_factions = no }
			do_effect = { NOT = { has_government = democratic } }   # modifiers apply only while true
			cancel = { has_political_power > 50 }                    # auto-removes when true; runs on_remove
			on_add = { add_stability = 0.05 }
			on_remove = { add_political_power = -50 }
			ai_will_do = { factor = 0 }
		}
	}
}
```

- `modifier = { }`: static numbers only. Variables are not read here ("Variables do not work in this section", `WIKI/idea_modding.md`). Negative values allowed.
- `targeted_modifier = { tag = TAG <targeted modifiers> }`: applied by the idea holder, effective against TAG; see the Targeted modifiers section of `WIKI/list_of_modifiers.md`.
- `research_bonus = { <technology category> = <number> }`: categories from `common/technology_tags/` (examples: `infantry`, `armor`, `dd_tech`, `artillery`).
- `equipment_bonus = { <archetype or type> = { instant = yes <stat> = <number> } }`: without `instant = yes` the bonus applies only to equipment researched after the idea was added. Archetypes and types come from `common/units/equipment/*.txt`.
- `rule = { <game rule> = yes|no }`: tooltip lists only rules that differ from the default. The wiki's table of rules includes `can_join_factions`, `can_create_factions`, `can_send_volunteers`, `can_not_declare_war`, `can_puppet`, `can_boost_own_ideology`.
- `on_add` and `on_remove` are country-scope effects. They do not run when the idea is added by a country history file or bookmark; copy the effect into that block. `cancel` triggers `on_remove` too.
- `allowed_civil_war` defaults to false: the spirit disappears when a civil war starts unless the trigger passes for a side. Vanilla sets `allowed_civil_war` on ideas that must survive (3,669 uses, 2,270 of them `{ always = yes }`).
- `do_effect` gates the modifiers, equipment bonus, and research bonus without removing the idea (181 vanilla uses).
- `allowed` is checked once at game start or load, and manual `add_ideas` bypasses it. It restricts selectable ideas (tag, DLC) and by convention `allowed = { always = no }` marks event-granted ideas.
- `visible` and `available` are checked continuously for selectable ideas (laws, designers, advisors); `visible` hides, `available` greys out. Put tag and DLC checks in `allowed`, not `visible`.
- `cost` and `removal_cost` (political power). `removal_cost = -1` forbids manual removal. `cost` falls back to the category value (150 in vanilla for selectable categories, 0 for `country`). `level` makes laws escalate: moving from level 1 to 3 charges the cost of level 2 as well.
- `traits = { ... }` references traits defined in `common/country_leader/*.txt` (for example `heavy_tank_manufacturer`); the trait supplies the modifier and icon.
- `ledger = army|air|navy|military|civilian|all|hidden`: which intelligence ledger shows it; `hidden` suppresses it. Resolution order is idea, then slot, then category.
- `default = yes` marks the law a country starts with when none is assigned (5 vanilla uses). `cancel_if_invalid = no` is used on vanilla laws (31 uses) and is not described in the wiki or installed documentation; copy it only from a vanilla precedent such as `_manpower.txt`.
- `ai_will_do` on a selectable idea steers the AI; on event-granted spirits vanilla uses `factor = 0`. Weight design belongs to `hoi4-ai-strategies`.

