# National focus modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="105626" sources="common/national_focus/ common/continuous_focus/ common/focus_inlay_windows/ common/ai_strategy_plans/ common/technology_tags/ common/defines/00_defines.lua documentation/effects_documentation.md documentation/triggers_documentation.md documentation/console_commands_documentation.md documentation/modifiers_documentation.md interface/nationalfocusview.gfx localisation/english/core_l_english.yml localisation/english/focus_filter_tag_l_english.yml hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 81 files in `common/national_focus/` (67 trees, 10,333 focuses, 335 shared and 280 joint focuses), `common/continuous_focus/`, the 7 inlay windows and their `documentation.md`, `common/ai_strategy_plans/`, the focus effects and triggers in `documentation/`, the focus defines, and error strings in `hoi4.exe`.
- Kit blocks added: tree and shortcut keys, a corrected inlay window format and declaration, prerequisite, exclusivity and relative position rules, cost units, icon extras, search filters missing from the table, trigger and bypass keys, focus effects (`load_focus_tree`, `add_tech_bonus`), shared and joint focus facts, continuous focus palettes, AI strategy plan keys.
- Errors found in the wiki text: the inlay window example is missing a closing brace and the average tree example has `tag = 25` where `add = 25` is meant; the search filter table lacks three real filters; the wiki's `advisor_portrait`, `gfx_name_fallback`, `inlay_window_id`, `BHR_*` names are placeholders.
- Gaps left: the `allowed_is_joint` key and `copy_completed_from` are named by the game but not used in a way that shows their effect; the wiki sentence under `joint_trigger` is cut off in the captured text.
**1.19.4.1 re-check (2026-11-01).** About 55 statements depended on files the update changed (the 59 changed focus files, the AI strategy plans, the technology categories, two English loc files and the vanilla-wide effect counts), and all were re-measured. Numbers that moved: tree focuses 10,333 to 10,341, `prerequisite` blocks 10,901 to 10,912, `mutually_exclusive` entries 2,612 to 2,614, the cost, search filter and availability key counts, `complete_national_focus` 3,152 to 3,150 and `add_tech_bonus` 1,948 to 1,946 (the `technology` count is now 78). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="focus-tree-vanilla" at="section:focus-tree" -->
Focus tree files in vanilla 1.19.4.1 (81 files in `common/national_focus/`). All counts: [vanilla-confirmed 1.19.4.1] `common/national_focus/`.

| Top-level block | Count |
| --- | --- |
| `focus_tree` | 67, holding 10,341 focuses |
| `shared_focus` | 335 |
| `joint_focus` | 280 |
| `style` | 22 |
| `search_filter_prios` | 1 |

- Tree keys: `id`, `country` and `default` appear in all 67 trees; `continuous_focus_position` in 57; `initial_show_position` in 29; `shared_focus` lines (71 of them) in 37; `shortcut` blocks (52) in 7 trees; `inlay_window` in 5 trees (6 declarations); `reset_on_civilwar` in 1; `alternate_icon_set` in 1 (`germany.txt`).
- `country` blocks: 64 trees use `factor` with `modifier` blocks, 2 use only `factor` and 1 uses `base` with `modifier`.
- `default`: 66 trees write `default = no` and one writes `default = yes`, the generic tree `generic_focus` in `generic.txt`. `hoi4.exe` has the message "Only one national focus tree should be default, switching from %s to %s". [vanilla-confirmed 1.19.4.1] for the values. A second tree with `default = yes` wrote "Only one national focus tree should be default, switching from generic_focus to <tree>" to `error.log`, 443 times in one session, so the later default replaces the generic default. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read after load. Whether countries used the replaced default tree was not checked.
- `initial_show_position` forms: `x` with `y` (22 trees, one with an `offset`), `focus` (6 trees, one with an `offset`) and one tree with only `x`. `hoi4.exe` reports "Both focus and the pair x, y cannot be specified at the same time" and "initial_show_position references invalid focus". [vanilla-confirmed 1.19.4.1] for the forms. Giving `focus` together with `x` and `y` wrote "Both focus and the pair x, y cannot be specified at the same time" once, without naming the tree. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read after load. The message "initial_show_position references invalid focus" was not tested. [unverified]
- `shortcut` always has `name` and `target`; `scroll_wheel_factor` is set in 28 of the 52 shortcut blocks and `trigger` in 31. [vanilla-confirmed 1.19.4.1]
- A duplicate focus id wrote "Duplicate focus name will cause database problems: <id>" and "Focus <id> has a hash collision in tree <tree>, this must be fixed for correct behaviour", as the wiki warns. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read after load.
<!-- kit:end id="focus-tree-vanilla" -->

<!-- kit:begin id="focus-example-corrections" at="section:examples" -->
The "Average tree" example above has `tag = 25` inside the `country` modifier. The `tag` trigger takes a country tag, so this is a typo for `add = 25`; vanilla writes `modifier = { add = 10 tag = GER }` in `common/national_focus/germany.txt`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="focus-example-corrections" -->

<!-- kit:begin id="focus-inlay-warning" at="heading:definition" -->
The example below is not valid script. `scripted_buttons` is never closed, so `scripted_images` ends up inside it and the definition has one `}` too few. The names in it are placeholders: `inlay_window_id` is the name of your own definition (vanilla: `ger_inner_circle_inlay_window`), `advisor_portrait` stands for the name of a subcomponent of the GUI window, and `gfx_name` and `gfx_name_fallback` stand for sprite names starting with `GFX_`. A corrected format follows after this section's text. [vanilla-confirmed 1.19.3] `common/focus_inlay_windows/`.
<!-- kit:end id="focus-inlay-warning" -->

<!-- kit:begin id="focus-inlay-format" at="section:definition" -->
Inlay window definition, from `common/focus_inlay_windows/documentation.md`:

- `window_name` is the name of the GUI component to show. In vanilla it is the `name` of a window in `interface/*.gui`, for example `sia_khana_ratsadon_ui_window` in `interface/SIA_khana_ratsadon_scripted_gui.gui`. [docs] for the key, [vanilla-confirmed 1.19.3] for the `.gui` link.
- `internal = yes` shows the window only to the country itself; the default is `no`. All 7 vanilla windows set `internal = yes`. [docs] and [vanilla-confirmed 1.19.3] `common/focus_inlay_windows/`.
- `visible` is a trigger; while it is false nothing in the window is evaluated. [docs]
- `scripted_images`: per icon name (a subcomponent of the window or a button) a list of `GFX_...` sprite names, each with a trigger or `yes`. The first entry whose trigger is true is used, on every update, and triggers run in the country scope of the focus tree. `yes` is normally the last entry, as the default. [docs]
- `scripted_buttons`: per button name an `available` trigger and a `click_effect` in country scope. A button name may also appear in `scripted_images` to choose its sprite; otherwise the sprite from the `.gui` file is used. [docs]
- `scripted_progressbars`: per progress bar name a `progress = <variable name>` line. The bar must be a subcomponent that uses a `progressbartype` sprite. The wiki does not mention this block. [docs]
- Vanilla windows: `scripted_images` in 5 of the 7 files, `scripted_buttons` in 3 and `scripted_progressbars` in 1. A button may have only a `click_effect` (the 5 buttons in `cze_industry_focus_inlay_window.txt`). [vanilla-confirmed 1.19.3] `common/focus_inlay_windows/`.

```text
my_inlay_window = {
    window_name = my_ui_window
    internal = yes
    visible = { has_completed_focus = TAG_focus_name }
    scripted_images = {
        my_status_icon = {
            GFX_my_status_good = { has_idea = TAG_good_idea }
            GFX_my_status_default = yes
        }
    }
    scripted_buttons = {
        my_button = { available = { has_political_power > 0 } click_effect = { add_political_power = -5 } }
    }
    scripted_progressbars = { my_bar = { progress = my_progress_variable } }
}
```

All names in the example are placeholders; the structure is the one the documentation and the vanilla files use. [docs]
<!-- kit:end id="focus-inlay-format" -->

<!-- kit:begin id="focus-inlay-declaration" at="section:declaration" -->
Declarations in vanilla 1.19.4.1. All items: [vanilla-confirmed 1.19.4.1] `common/national_focus/`.

- 6 `inlay_window` declarations in 5 trees (`australia_taog_focus` declares two windows at the same position, an empty one and the real one; `mu_czech_focus`, `german_focus`, `japan_wtt_focus`, `siam_focus`). Positions are in pixels, for example `x = 4500 y = 1150` for the German window.
- The Czech and Japanese trees add `override_position = { x = ... y = ... trigger = { ... } }` blocks (10 and 9) that move the window when branches are hidden. `override_position` is not mentioned in the documentation or on this page. A vanilla position block is also written with a capital `X` once, so key names look case-insensitive; keep them lowercase.
- `hoi4.exe` has the messages "Inlay window %s already exist" and "Couldn't find inlay window %s". Every `id` must be unique and must name an existing definition, and the game does not survive a fault of either kind. A duplicate `inlay_window` id logged "Inlay window ger_inner_circle_inlay_window already exist" at load. A focus that names an undefined inlay window logged "Focus inlay window b5_missing_window not found in database", and the text "Couldn't find inlay window" appeared nowhere. Right after those two lines the game crashed at load (EXCEPTION_ACCESS_VIOLATION), before "Loaded 13414 provinces" in game.log. Both faults were in the same focus tree file, so which one crashes is not separated, and the crash stack has no symbol names. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log and the crash folder read.
<!-- kit:end id="focus-inlay-declaration" -->

<!-- kit:begin id="focus-prerequisites-vanilla" at="section:interaction-with-other-focuses" -->
Prerequisites, exclusivity and relative positions, checked against vanilla 1.19.4.1 (focuses inside the 67 `focus_tree` blocks).

- Prerequisite logic matches the wiki: one `prerequisite` block with several `focus` lines means one of them, several blocks mean all blocks, and mixing both means every block must be met, each by one of its focuses. The vanilla tooltips say so: "Requires one of the following" (`FOCUS_SINGLE_OR_PREREQ_HEADER`) and "Requires all of the following" (`FOCUS_AND_PREREQ_HEADER`, `FOCUS_MIX_PREREQ_HEADER`) in `localisation/english/core_l_english.yml`. [vanilla-confirmed 1.19.4.1]
- Vanilla uses 10,912 `prerequisite` blocks: 1,786 list more than one focus, 828 focuses have more than one block and 61 focuses mix both forms. [vanilla-confirmed 1.19.4.1] `common/national_focus/`.
- `mutually_exclusive` is written on both focuses: all 2,614 vanilla entries in tree focuses have the reverse entry on the target focus, and none is one-way. [vanilla-confirmed 1.19.4.1] for the counts. A one-way `mutually_exclusive` wrote "Error in focus: <id> (<file>:<line>) Has mutual exclusivity with <other> but the other focus does not." [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read after load.
- `relative_position_id` is used by 10,145 focuses and always points at a focus defined earlier in the same tree (none later, none in another tree). `hoi4.exe` contains "Error in focus: ... does not exist. Relative focus must be scripted before this." and "Circular reference detected for relative position.", so define the anchor focus first and never close a loop. [vanilla-confirmed 1.19.4.1] for the counts. A `relative_position_id` that points at a focus defined later wrote "Error in focus: <id> relative_focus_id: <other> does not exist. Relative focus must be scripted before this." A circular pair of two focuses wrote only that forward-reference message and no circular-reference line, so the "Circular reference detected" message did not show. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read after load. The test tree held both a forward and a circular reference, so a circular-only case was not isolated.
<!-- kit:end id="focus-prerequisites-vanilla" -->

<!-- kit:begin id="focus-cost-units" at="section:cost" -->
Cost units. `cost` counts in units of `FOCUS_POINT_DAYS` days: `NDefines.NFocus.FOCUS_POINT_DAYS = 7` ("Each point takes a week"), with `FOCUS_PROGRESS_PEACE = 1`, `FOCUS_PROGRESS_WAR = 1` and `MAX_SAVED_FOCUS_PROGRESS = 10`. At the default progress of 1 per day, `cost = 10` is 70 days. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

- Vanilla costs: 10 in 6,735 of 10,341 entries (70 days), 5 in 3,494 (35 days); the rest are 0, 1, 2, 3, 4, 12, 15, 20, 30 or 35, or a file-scoped constant: `germany.txt` defines `@inner_circle_time_tier_1 = 20` and uses `cost = @inner_circle_time_tier_1`. No vanilla cost has decimals. [vanilla-confirmed 1.19.4.1] `common/national_focus/`.
- `reduce_focus_completion_cost = { focus = <id> cost = N }` accepts script constants, and `focus` can be a single token or a list. Vanilla uses it 152 times. [docs] `documentation/effects_documentation.md` and [vanilla-confirmed 1.19.4.1].
<!-- kit:end id="focus-cost-units" -->

<!-- kit:begin id="focus-icon-extras" at="section:icon" -->
Icon keys and messages in vanilla 1.19.4.1.

- `hoi4.exe` has "Missing icon for focus: " and "Missing icon shine for focus: ", which fits the wiki's rule that both `GFX_name` and `GFX_name_shine` must exist. [unverified] A focus whose icon sprite does not exist wrote both "Missing icon for focus: <id>" and "Missing icon shine for focus: <id>" at load. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read after load. The overlay image needs the interface and was not checked.
- `overlay = GFX_...` is set in 94 focuses (`czechoslovakia_mu.txt` 44, `australia_taog.txt` 21, `philippines.txt` 17, `indonesia_joint.txt` 4, `japan.txt` 4, `china_communist_sea.txt` 3, `indonesia.txt` 1). The wiki does not mention it; the name suggests an image drawn over the icon. [vanilla-confirmed 1.19.4.1] `common/national_focus/` for the usage, [unverified] for the effect.
- `alternate_icon = GFX_...` is set in 22 focuses, all in `germany.txt`, and the tree sets `alternate_icon_set = FOCUS_ICON_SET_HISTORICAL_KEY_FOCUS` (sprite `GFX_FOCUS_ICON_SET_HISTORICAL_KEY_FOCUS` in `interface/nationalfocusview.gfx`, name in `localisation/english/wuw_focus_l_english.yml`). A commented line in `germany.txt` shows the other set name `FOCUS_ALTERNATE_ICONS`, whose toggle button needs a localisation key and a `GFX_` sprite of the same name. [vanilla-confirmed 1.19.4.1]
- `hoi4.exe` also has "Missing alternate icon for focus: " and "Missing alternate icon shine for focus: ", so an alternate icon needs its own `_shine` sprite as well. [unverified]
<!-- kit:end id="focus-icon-extras" -->

<!-- kit:begin id="focus-dynamic-vanilla" at="section:dynamic-appearance" -->
Dynamic icons in vanilla 1.19.4.1. All counts: [vanilla-confirmed 1.19.4.1] `common/national_focus/`.

- 254 focuses set `dynamic = yes` (127 in trees, 26 shared, 101 joint). 60 focuses write `icon` as a block; 24 of them set `dynamic = yes` and 36 do not, which is the case the wiki describes where the icon is chosen once at game start.
- Every one of the 60 icon blocks contains a default entry written `GFX_name = yes`. [vanilla-confirmed 1.19.4.1] `common/national_focus/`. `hoi4.exe` has "Focus %s (%s) does not have a default icon case." and "Focus %s (%s) has alternate icons but does not have a default case.", so always add the default. [unverified] (strings in `hoi4.exe`). An icon block without a default entry wrote "Focus <id> does not have a default icon case." at load. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read after load.
<!-- kit:end id="focus-dynamic-vanilla" -->

<!-- kit:begin id="focus-trigger-keys-vanilla" at="section:triggers" -->
Availability keys in vanilla 1.19.4.1. Counts are focuses inside `focus_tree` blocks (10,341) unless stated. All rows: [vanilla-confirmed 1.19.4.1] `common/national_focus/`.

| Key | Focuses | Notes |
| --- | --- | --- |
| `available` | 9,728 | |
| `bypass` | 5,889 | |
| `available_if_capitulated` | 5,514 | across tree, shared and joint focuses: 4,143 `no`, 1,690 `yes` |
| `cancel_if_invalid` | 3,807 | across all kinds: 3,478 `yes`, 563 `no` |
| `continue_if_invalid` | 3,780 | across all kinds: 3,555 `no`, 458 `yes` |
| `allow_branch` | 523 | plus 20 shared and 11 joint |
| `will_lead_to_war_with` | 777 | |
| `complete_tooltip` | 370 | |
| `select_effect` | 75 | |
| `enable_automatic_bypass = no` | 23 | |
| `cancel` | 20 | |
| `bypass_effect` | 18 | |
| `historical_ai` | 10 | |
| `bypass_if_unavailable = yes` | 8 | |
| `cancelable = no` | 2 | |

- Vanilla writes the defaults explicitly (`cancel_if_invalid = yes`, `continue_if_invalid = no`), so a missing line is not a mistake.
- The vanilla tooltips for the four outcomes when `available` turns false are `FOCUS_WILL_PAUSE`, `FOCUS_WILL_CANCEL`, `FOCUS_WILL_BYPASS_IF_UNAVAILABLE` and `FOCUS_WILL_CONTINUE` in `localisation/english/core_l_english.yml`, matching the key names above. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="focus-trigger-keys-vanilla" -->

<!-- kit:begin id="focus-effects-vanilla" at="section:effects" -->
Focus effects and triggers that this page does not name. Documentation: `documentation/effects_documentation.md` and `documentation/triggers_documentation.md` ([docs]). Uses are counted over `events/`, `common/` and `history/` ([vanilla-confirmed 1.19.4.1]).

| Name | What the documentation says | Uses |
| --- | --- | --- |
| `complete_national_focus = <id>` | completes a focus for the country | 3,150 short; 36 in block form `{ focus = <id> use_side_message = yes originator_name = ... }`, which the documentation does not describe |
| `unlock_national_focus = <id>` | unlocks a focus for the country | 354 |
| `uncomplete_national_focus = { focus = <id> uncomplete_children = yes refund_political_power = yes }` | uncompletes a focus; both flags default to `no`; runs an `on_uncomplete` effect on each uncompleted focus if one is specified | 101 |
| `activate_shine_on_focus = <id>`, `deactivate_shine_on_focus = <id>` | switch the shine on a focus; a completed focus cannot be given a shine and the current focus cannot lose it; tooltips show only in debug mode | 24 and 32 |
| `focus_progress = { focus = <id> progress > 0.5 }` | trigger on the progress of a focus | 194 |
| `has_shine_effect_on_focus = <id>` | trigger: the focus has a shine, by hand or by being worked on | 71 |

- The `uncomplete_national_focus` entry says an `on_uncomplete` effect runs on each uncompleted focus. [docs] `documentation/effects_documentation.md`. No vanilla focus uses it. [vanilla-confirmed 1.19.4.1] `common/national_focus/`. Placed directly in the focus block, it runs when `uncomplete_national_focus` removes the focus: a flag set in it was FALSE after the focus was completed and TRUE after it was uncompleted. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, focus tree loaded with `load_focus_tree`, game.log read. `uncomplete_children` and the refund were not tested.
- Console commands: `Focus.IgnorePrerequisites`, `Focus.NoChecks`, `Focus.AutoComplete`, `freefocuses`, `show_focuses`, `list_hidden_focuses`, `loc_check_focuses` and `focus_count`. [docs] `documentation/console_commands_documentation.md`.

**`load_focus_tree`.** The documentation names `tree`, `keep_completed` (default `no`: keep the completed focuses of the old tree that also exist in the new one) and `copy_completed_from = <country>` (mark everything that country has completed as completed in the new tree); the effect retains finished shared focuses. [docs] `documentation/effects_documentation.md`.

- Vanilla has 80 uses: 25 short (`load_focus_tree = <tree id>`) and 55 block form, every block with `tree` and `keep_completed`; none uses `copy_completed_from`. [vanilla-confirmed 1.19.4.1]
- `load_focus_tree` with an unknown tree id writes "Unable to find focus tree with ID: <id>" when the script loads, in the short and the block form, and running the effect does not stop the rest of the event. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read after load and the event run. The message came at load, so the two lines cannot be matched to the two forms.

**`add_tech_bonus`.** The documentation only says "adds a limited use tech bonus". [docs] `documentation/effects_documentation.md`.

- Vanilla has 1,946 uses. Keys: `name` (1,893), `bonus` (1,899) or `ahead_reduction` (177, and 130 of those also write `bonus`), `uses` (1,918), and either one or more `category` lines (1,868 uses, 211 of them with two or more) or one `technology` line (78 uses). [vanilla-confirmed 1.19.4.1] `common/national_focus/generic.txt` and others.
- `category` takes a technology category from `common/technology_tags/00_technology.txt`, which lists 134 names, such as `industry` (117 uses), `construction_tech` (25 uses), `electronics` and `infantry_weapons`. There is no category called `construction`. [vanilla-confirmed 1.19.4.1]

```text
add_tech_bonus = {
    name = infantry_artillery_bonus
    bonus = 1.0
    uses = 1
    category = infantry_weapons
    category = artillery
}
```

**`research_bonus`** is not an effect. It is a key of ideas (1,086 uses in `common/ideas/`), characters (15) and military industrial organizations (2), and `documentation/effects_documentation.md` has no effect of that name. In a focus reward use `add_tech_bonus`, or add an idea that carries `research_bonus`. [vanilla-confirmed 1.19.4.1] and [docs]
<!-- kit:end id="focus-effects-vanilla" -->

<!-- kit:begin id="focus-search-filters-vanilla" at="section:search-filters" -->
Search filters in vanilla 1.19.4.1. The focuses in `common/national_focus/` use 38 distinct `FOCUS_FILTER_*` names, and 8,980 of the 10,341 tree focuses write `search_filters` (9,052 lines, 944 of them empty blocks). The most used are `FOCUS_FILTER_INDUSTRY` (2,657 uses), `FOCUS_FILTER_POLITICAL` (2,551) and `FOCUS_FILTER_RESEARCH` (1,717). [vanilla-confirmed 1.19.4.1] `common/national_focus/`.

Real filters that the table above lacks. All rows: [vanilla-confirmed 1.19.4.1] `common/national_focus/`, `interface/nationalfocusview.gfx`, `localisation/english/focus_filter_tag_l_english.yml`.

| Internal name | Uses | Localised name |
| --- | --- | --- |
| `FOCUS_FILTER_IMPERIAL_INFLUENCE` | 51 | Imperial Influence |
| `FOCUS_FILTER_INNER_CIRCLE` | 30 | Inner Circle |
| `FOCUS_FILTER_COMPLETED_BY_EVENT` | 13 | Completed Through Events |

- `FOCUS_FILTER_INDUSTRIAL` (one use, in `paraguay_uruguay_shared_branch.txt`) has no sprite and no localisation key anywhere in the game files: it is a typo for `FOCUS_FILTER_INDUSTRY`. [vanilla-confirmed 1.19.4.1]
- `search_filter_prios` in `generic.txt` holds 10 entries. Its entry `FOCUS_FILTER_MISSIOLINI = 110` does not match the name focuses use (`FOCUS_FILTER_ITA_MISSIOLINI`), so it probably never applies. [vanilla-confirmed 1.19.4.1] for the entries. A repeated `search_filter_prios` entry wrote "Prio is already set for focus tree filter <name>", also when vanilla already sets the name (`FOCUS_FILTER_POLITICAL`). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read after load. Whether the entry applies is [unverified].
<!-- kit:end id="focus-search-filters-vanilla" -->

<!-- kit:begin id="focus-titlebar-vanilla" at="section:titlebar-styles" -->
Titlebar styles in vanilla 1.19.4.1. All 22 `style` blocks are in `common/national_focus/00_titlebar_styles.txt`, each with exactly `name`, `unavailable`, `completed`, `available` and `current`; one (`default_style`) also sets `default = yes`. `text_icon` is set in 316 focuses (20 in trees, 16 shared, all 280 joint). [vanilla-confirmed 1.19.4.1] `common/national_focus/`.
<!-- kit:end id="focus-titlebar-vanilla" -->

<!-- kit:begin id="focus-joint-shared-vanilla" at="section:joint-focuses" -->
Shared and joint focuses in vanilla 1.19.4.1. All counts: [vanilla-confirmed 1.19.4.1] `common/national_focus/`.

- 335 shared focuses sit in 7 files (largest: `toa_shared_military_branch.txt` 76, `china_shared_TSR.txt` 69, `china_shared.txt` 65, `baltic_shared.txt` 60, `paraguay_uruguay_shared_branch.txt` 49).
- 280 joint focuses sit in 8 files: `indonesia_joint.txt` 96, `congo_shared.txt` 57, `nordic_shared.txt` 51, `habsburg_joint.txt` 35, `goe_shared_saadabad_branch.txt` 18, `abdacom_shared_branch.txt` 11, `TSR_lingguang_incident_joint_branch.txt` 7 and `ncns_ma_clique_joint_branch.txt` 5.
- Joint focus keys: `completion_reward_joint_originator` in 263, `completion_reward_joint_member` in 221, `completion_reward` in 168, `joint_trigger` in 135, and `allowed_is_joint = yes` in 12 (7 in `TSR_lingguang_incident_joint_branch.txt`, 5 in `ncns_ma_clique_joint_branch.txt`). [vanilla-confirmed 1.19.4.1] The wiki and `documentation/` do not mention `allowed_is_joint`, and what it does is [unverified].
- All 280 joint focuses set `text_icon`, and 273 set `search_filters`.
<!-- kit:end id="focus-joint-shared-vanilla" -->

<!-- kit:begin id="focus-continuous-vanilla" at="section:continuous-focuses" -->
Continuous focuses in vanilla 1.19.4.1. All counts: [vanilla-confirmed 1.19.4.1] `common/continuous_focus/generic.txt` and `common/national_focus/`.

- All of vanilla is one file with one palette: `generic.txt` defines `continuous_focus_palette = { id = generic_focus ... }` with `country = { factor = 1 }`, `default = yes`, `reset_on_civilwar = no`, `position = { x = 50 y = 1000 }` and 14 focuses.
- Keys used by the 14 focuses: `id`, `icon`, `available`, `ai_will_do`, `supports_ai_strategy`, `daily_cost` and `available_if_capitulated` in all 14; `modifier` in 11; `enable` in 7; `select_effect` and `cancel_effect` in 4; `idea` in 2.
- Focus trees only place the palette with `continuous_focus_position = { x = ... y = ... }` (57 of the 67 trees). No focus in `common/national_focus/` or `common/continuous_focus/` sets `continuous = yes`; a continuous focus is defined in a palette, not flagged in a tree.
- `NDefines.NCountry.MIN_FOCUSES_FOR_CONTINUOUS = 10` is commented "Focuses needed to unlock continuous focuses". [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.
<!-- kit:end id="focus-continuous-vanilla" -->

<!-- kit:begin id="focus-ai-plans-vanilla" at="section:ai-strategy-plans" -->
AI strategy plans in vanilla 1.19.4.1: 376 plans in 128 files of `common/ai_strategy_plans/`. Keys per plan: `enable` 376, `abort` 368, `name` 366, `allowed` 366, `ideas` 365, `desc` 364, `weight` 362, `ai_national_focuses` 352, `research` 351, `focus_factors` 252, `traits` 125 and `ai_strategy` 61. The keys `ideas`, `research`, `traits` and `ai_strategy` are not covered on this page; see [AI modding](ai_modding.md). [vanilla-confirmed 1.19.4.1] `common/ai_strategy_plans/`.

The nine modifiers `ai_focus_aggressive_factor`, `ai_focus_aviation_factor`, `ai_focus_defense_factor`, `ai_focus_military_advancements_factor`, `ai_focus_military_equipment_factor`, `ai_focus_naval_air_factor`, `ai_focus_naval_factor`, `ai_focus_peaceful_factor` and `ai_focus_war_production_factor` are listed in `documentation/modifiers_documentation.md`. [docs]
<!-- kit:end id="focus-ai-plans-vanilla" -->
