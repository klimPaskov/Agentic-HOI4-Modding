# Scripted GUI modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="105160" sources="common/scripted_guis/ common/decisions/categories/ common/scripted_diplomatic_actions/scripted_diplomatic_actions.txt interface/ documentation/console_commands_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against `common/scripted_guis/_documentation.md`, the 17 vanilla scripted GUIs in `common/scripted_guis/` with their `.gui` windows in `interface/`, the decision categories that attach them, `common/scripted_diplomatic_actions/`, the GUI-related console commands in `documentation/`, a count of element sizes over the 130 vanilla `interface/*.gui` files, and key strings in `hoi4.exe`.
- Kit blocks added: what vanilla actually uses (17 scripted GUIs, all `decision_category`), the parent window keys the page omits (`parent_scripted_gui`, `map_mode`), the missing context `diplomacy_target_context`, the documented-but-unused keys, a table of every top-level key, the `ai_weights` entry shape in the documentation, the entry containers of dynamic lists, property value forms, button `size` forms, and GUI console commands.
- Flagged keys checked: `Button_1_click`, `Button_2_click`, `_click`, `_click_enabled`, `_visible`, `ai_check`, `ai_check_scope`, `ai_enabled`, `ai_weights`, `change_scope`, `dirty`, `dynamic_lists`, `effects`, `entry_container`, `ignore_lower_weights` and `parent_window_token` are element-name placeholders, naming suffixes or documented keys; none is wrong.
- Real differences found: the wiki's `ignore_lower_weights = { factor = ... }` block and its `weight` placement differ from the documentation, `ai_test_variance` is described differently (fraction on the wiki, hours in the documentation), and the documentation spells a parent key `parent_window_window` that is absent from `hoi4.exe`.
- Gaps left: vanilla uses no `effects`, `visible`, `dynamic_lists`, `dirty`, `parent_*` or `ai_*` key, so those sections rest on the documentation and the wiki only. Nothing was run in the game.
**1.19.4.1 re-check (2026-11-01).** 16 vanilla-confirmed statements depended on files the update changed (`common/scripted_guis/`, `common/decisions/categories/` and `interface/*.gui`), and all of them were re-measured. The update adds two scripted GUI files, so the vanilla count is 19 instead of 17, `triggers` is used by 4, and `dynamic_lists` (2) and `dirty` (1) now have vanilla uses, which corrects the earlier 'no vanilla use' statements; the `interface/*.gui` size counts also moved (82 button sizes of 2,054 buttons). The three console command bullets cite the changed console commands documentation: the six commands they name are all still listed, since only `debug_types` was removed. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="sg-vanilla-use" at="section:window-assignment" -->
What vanilla scripted GUIs look like in 1.19.4.1, so that the rest of this page can be judged against it.

- `common/scripted_guis/` holds 19 scripted GUIs in 19 files, and all 19 use `context_type = decision_category`. Their keys are `context_type` (19), `window_name` (19), `properties` (12), `triggers` (4), `dynamic_lists` (2) and `dirty` (1). None uses `visible`, `effects`, `parent_*`, `map_mode` or any `ai_*` key. [vanilla-confirmed 1.19.4.1] `common/scripted_guis/*.txt`. The documentation describes all those keys, so they are supported. [docs] `common/scripted_guis/_documentation.md`. `dynamic_lists` and `dirty` first appear in vanilla in 1.19.4.1, in the added files `MTG_naval_treaty_scripted_gui.txt` and `RAJ_GOE_partition_scripted_gui.txt`. For the keys that are still unused, nothing in vanilla shows them working. [vanilla-confirmed 1.19.4.1] `common/scripted_guis/*.txt`.
- Vanilla scripted GUIs are attached by a decision category: 19 `scripted_gui = <name>` lines in 13 files of `common/decisions/categories/`, for example `scripted_gui = AST_cabinet_trust_ui` in `AST_decision_categories.txt`. `INS_revolution_scripted_gui` is attached by two lines, and `swe_rearnament_system_ui` only by a commented-out line, so it is attached nowhere. [vanilla-confirmed 1.19.4.1] `common/decisions/categories/`.
- The window is a top-level `containerWindowType` in its own file, named after the scripted GUI file: `AST_cabinet_trust_ui` has `window_name = "AST_cabinet_trust_ui_window"` and the container sits in `interface/AST_cabinet_trust_scripted_gui.gui` with `size = { width = 100% height = 150 }`. Vanilla writes percentages both as `100%%` (706 uses in `interface/*.gui`) and as `100%` (348 uses). [vanilla-confirmed 1.19.4.1] `common/scripted_guis/AST_cabinet_trust_scripted_gui.txt`, `interface/AST_cabinet_trust_scripted_gui.gui`.

A complete vanilla scripted GUI is as short as this:

```text
scripted_gui = {
	GER_rk_ui = {
		context_type = decision_category
		window_name = "ger_rk_ui_window"
	}
}
```

The example is the whole file `GER_rk_scripted_gui.txt`, with the spacing changed. [vanilla-confirmed 1.19.3] `common/scripted_guis/GER_rk_scripted_gui.txt`.
<!-- kit:end id="sg-vanilla-use" -->

<!-- kit:begin id="sg-parent-keys" at="section:parent-window" -->
Checks of the parent window section against `common/scripted_guis/_documentation.md`.

- The `parent_window_token` list above is complete and exact: the documentation lists the same 30 tokens, from `top_bar` to `tech_industry_folder`. [docs] `common/scripted_guis/_documentation.md`.
- Without a parent, the GUI is attached to the main window, unless the context type overrides that. [docs] `common/scripted_guis/_documentation.md`.
- The documentation spells the container-name key `parent_window_window = "container_name"` and adds "may not work". The string `parent_window_window` does not occur in `hoi4.exe`, while `parent_window_name` does, so the wiki's `parent_window_name` is the key to write and the documentation spelling is probably a slip. [docs] `common/scripted_guis/_documentation.md`. The executable strings do not show which key the engine reads. [unverified] `hoi4.exe`
- Two keys are missing from the wiki: `parent_scripted_gui = "<scripted gui name>"` attaches a scripted GUI to another scripted GUI (the documentation comment says "container_name" but describes the scripted GUI case), and `map_mode = <map mode>` makes the GUI show only in that map mode. [docs] `common/scripted_guis/_documentation.md`. The second key did not work in a test: a `scripted_gui` block with `map_mode` was rejected at load as "Unexpected token: map_mode", whatever name followed (a scripted map mode id, a hard-coded layer name or a made-up name). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read at load. See [Map mode modding](map_mode_modding.md).
- No vanilla scripted GUI sets a parent key, so the `_instance` suffix rule for nested containers is a claim of the wiki that cannot be checked in the game files. [vanilla-confirmed 1.19.4.1] 0 of 19 scripted GUIs use `parent_window_token` or `parent_window_name`, and none uses `parent_window_window` or `parent_scripted_gui` either. The `_instance` rule is untested. [unverified]
<!-- kit:end id="sg-parent-keys" -->

<!-- kit:begin id="sg-context-fix" at="section:context" -->
The table above lacks one context type. The documentation lists nine: `player_context`, `selected_country_context`, `selected_state_context`, `diplomacy_target_context`, `decision_category`, `diplomatic_action`, `national_focus_context`, `country_mapicon` and `state_mapicon`. `diplomacy_target_context` attaches the GUI to the diplomacy window and targets the currently selected country. [docs] `common/scripted_guis/_documentation.md`.

More on the contexts. All bullets: [docs] `common/scripted_guis/_documentation.md` unless marked.

- `selected_country_context` targets the country the player right-clicks and `selected_state_context` the state the player left-clicks; the documentation text for the state case says "target country", which looks like a slip for the state.
- `country_mapicon` and `state_mapicon` take a `mapicon_targets = { ... }` block that uses targeting code like targeted decisions. The documentation gives no more detail on that block, and no vanilla scripted GUI uses it. [vanilla-confirmed 1.19.4.1] 0 of 19.
- The `diplomatic_action` context pairs with two keys of a scripted diplomatic action, `send_scripted_gui` (shown before the request is sent) and `receive_scripted_gui` (shown to the receiver instead of the yes/no popup). They are described in the comment block of `common/scripted_diplomatic_actions/scripted_diplomatic_actions.txt`; each has a `reset_send_effect` or `reset_receive_effect` to clear the state, and the `can_be_sent` and `can_be_accepted` triggers. [vanilla-confirmed 1.19.3] `common/scripted_diplomatic_actions/scripted_diplomatic_actions.txt`.
- `decision_category` is the only context vanilla uses, in all 19 scripted GUIs. [vanilla-confirmed 1.19.4.1] `common/scripted_guis/*.txt`.
<!-- kit:end id="sg-context-fix" -->

<!-- kit:begin id="sg-dirty-notes" at="section:dirty" -->
The documentation adds that a GUI is updated every tick by default, and that with `dirty = <var_name>` an effect can force an update by changing that variable, for example `add_to_variable = { var_name = 1 }`. [docs] `common/scripted_guis/_documentation.md`. One vanilla scripted GUI uses `dirty`: `MTG_naval_treaties_ui` writes `dirty = global.MTG_naval_treaty_ui_version`, and `add_to_variable = { global.MTG_naval_treaty_ui_version = 1 }` appears in four places in the scripted effects. A file comment says the GUI refreshes off the counter instead of every tick. [vanilla-confirmed 1.19.4.1] 1 of 19, `common/scripted_guis/MTG_naval_treaty_scripted_gui.txt`, `common/scripted_effects/00_scripted_effects.txt`.
<!-- kit:end id="sg-dirty-notes" -->

<!-- kit:begin id="sg-effects-triggers-notes" at="section:triggers" -->
The names flagged in the page inventory are placeholders, suffix patterns or documented keys, and none is an error.

- `Button_1_click` and `Button_2_click` in the dynamic list example are the element names `Button_1` and `Button_2` from the `.gui` file plus the `_click` suffix. `my_button_alt_right_click` and `my_temp_array_calculator_click_enabled` follow the same pattern. The modifiers `right`, `alt`, `control` and `shift` go in front of `click`. [docs] `common/scripted_guis/_documentation.md`.
- `_click`, `_click_enabled` and `_visible` are suffixes that attach an effect or a trigger to an element: `<element>_click` goes in `effects`, and `<element>_click_enabled` and `<element>_visible` go in `triggers`. [docs] `common/scripted_guis/_documentation.md`.
- Four vanilla scripted GUIs use `triggers`. `RAJ_tax_fraud_scripted_ui` has four `eic_current_taxes_<n>_visible` triggers that each test `check_variable`. `sov_paranoia_system_ui`, `MTG_naval_treaties_ui` and `RAJ_GOE_partition_scripted_ui` have one `_visible` trigger each, testing `has_country_flag`, `check_variable` and `has_global_flag`. Only the tax fraud GUI used `triggers` in 1.19.3. [vanilla-confirmed 1.19.4.1] `common/scripted_guis/*.txt`.
- Vanilla uses no `effects` block, so the `<element>_click` form has no vanilla precedent. [vanilla-confirmed 1.19.4.1] 0 of 19.
<!-- kit:end id="sg-effects-triggers-notes" -->

<!-- kit:begin id="sg-dynamic-list-notes" at="section:dynamic-lists" -->
Checks of the dynamic list section against `common/scripted_guis/_documentation.md`.

- A dynamic list entry has `array` (one GUI element per array element), `value` (name of the variable that holds the current element, default `v`), `index` (name of the variable that holds the current index, default `i`) and `change_scope` (when `yes`, the scope changes to the array element while the child is built). [docs] `common/scripted_guis/_documentation.md`.
- The entry container is picked with `entry_container = "<container>"`, and the documentation says all the container keys accept scripted localisation. It also lists `country_scope_entry_container`, which the documentation writes twice; the second line was probably meant to be `state_scope_entry_container`, a token that exists in `hoi4.exe` and that vanilla writes in `RAJ_GOE_partition_scripted_gui.txt`. [docs] `common/scripted_guis/_documentation.md`. [vanilla-confirmed 1.19.4.1] `common/scripted_guis/RAJ_GOE_partition_scripted_gui.txt`.
- A dynamic list entry may hold its own `ai_weights` block, and the list uses the `effects` and `triggers` of the same scripted GUI. [docs] `common/scripted_guis/_documentation.md`.
- Two vanilla scripted GUIs have a `dynamic_lists` block, `MTG_naval_treaties_ui` and `RAJ_GOE_partition_scripted_ui`, both added in 1.19.4.1. Each holds one list, named after a `gridBoxType` in the window's `.gui` file (the file comment says the binding is by name). The list sets `array` (a `global.` array in one, a country array in the other) and `change_scope = yes`, plus `country_scope_entry_container` or `state_scope_entry_container`. That key holds a quoted scripted localisation call, and the call returns the name of a container in the `.gui` file; an empty result drops the entry, as the file comments say. Neither list sets `value`, `index` or `ai_weights`. [vanilla-confirmed 1.19.4.1] `common/scripted_guis/MTG_naval_treaty_scripted_gui.txt`, `common/scripted_guis/RAJ_GOE_partition_scripted_gui.txt`, `interface/MTG_naval_treaty_scripted_gui.gui`, `interface/RAJ_GOE_partition_scripted_gui.gui`.
- Element sizes in vanilla `.gui` files, for the example windows above: `containerWindowType` blocks that set `size` write `{ width = .. height = .. }` (1,794 of 1,809, while 13 add `min` and 2 write only `width`), while `buttonType` blocks that set `size` all write `{ x = .. y = .. }`: 82 of 2,054 `buttonType` blocks set a size and all 82 use the x and y form. A `buttonType` normally takes its size from its sprite and writes no `size`. [vanilla-confirmed 1.19.4.1] `interface/*.gui` (132 files).
<!-- kit:end id="sg-dynamic-list-notes" -->

<!-- kit:begin id="sg-properties-notes" at="section:properties" -->
Vanilla `properties` blocks (12 of the 19 scripted GUIs) use only two attributes: `frame` (51 times) and `image` (32 times). [vanilla-confirmed 1.19.4.1] `common/scripted_guis/*.txt`.

- `image` takes a string that holds a scripted localisation call, for example `image = "[GET_WAR_ESCALATION_LEVEL_1_COLOR]"`, and the call returns a GFX name. [vanilla-confirmed 1.19.3] `common/scripted_guis/war_escalation_scripted_gui.txt`. `MTG_naval_treaty_scripted_gui.txt` also writes `image = "[This.GetFlag]"`, a localisation object function instead of a scripted localisation entry. [vanilla-confirmed 1.19.4.1] `common/scripted_guis/MTG_naval_treaty_scripted_gui.txt`.
- `frame` takes a plain number (`frame = 3`), a variable name (`frame = SOV_poster_left_icon_frame`) or an array element (`frame = SOV_paranoia_generic_portraits_array^1`). [vanilla-confirmed 1.19.4.1] `common/scripted_guis/war_escalation_scripted_gui.txt`, `SOV_propaganda_campaigns_scripted_gui.txt`, `SOV_paranoia_system_scripted_gui.txt`.
- `x` and `y` are documented as variables that move an element, and no vanilla scripted GUI uses them. [docs] `common/scripted_guis/_documentation.md`. [vanilla-confirmed 1.19.4.1] 0 of 19.
- Frame numbers count from 1: vanilla sets frames 1 to 10 on ten icons. [vanilla-confirmed 1.19.3] `common/scripted_guis/war_escalation_scripted_gui.txt`.
<!-- kit:end id="sg-properties-notes" -->

<!-- kit:begin id="sg-ai-enabled-notes" at="section:ai-enabled" -->
`ai_enabled` is checked once and a false result excludes the GUI for the whole game, so the documentation advises testing only things like `tag` or `original_tag` in it. [docs] `common/scripted_guis/_documentation.md`. `ai_check` is evaluated once for each AI and each GUI, and a false result makes the AI ignore the GUI in that tick. [docs] `common/scripted_guis/_documentation.md`.
<!-- kit:end id="sg-ai-enabled-notes" -->

<!-- kit:begin id="sg-ai-attribute-notes" at="section:ai-test-attributes" -->
The two sources disagree on `ai_test_variance`. The documentation example sets `ai_test_interval = 24` and `ai_test_variance = 24` under the comment "ai test interval & variance in hours", while this page describes the variance as a fraction with default 0.2. [docs] `common/scripted_guis/_documentation.md`. No vanilla scripted GUI sets either attribute (0 of 19), so the unit cannot be settled from the game files. [vanilla-confirmed 1.19.4.1] `common/scripted_guis/*.txt`. Write both `ai_test_interval` and `ai_test_variance` explicitly and check the result in `scripted_ai.log`. Which unit the variance uses is untested. [unverified] The value changes how often the AI tests the button, by a lot. A button with `ai_test_variance = 24` was pressed by each of 97 AI countries about once per game hour (528 presses per country in 6 days, every gap 1 hour). Two buttons with `ai_test_variance = 0.2` were pressed 3 to 17 times per country, with gaps of about 22 to 24 hours or a multiple of that. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, a `log` line in each button effect, game.log read. The AI countries pressed the buttons without `human_ai` being needed for them. The unit is not settled by this: one of the two `0.2` buttons also set `ai_test_parent`, and that key's effect was not separated.
<!-- kit:end id="sg-ai-attribute-notes" -->

<!-- kit:begin id="sg-ai-weights-notes" at="section:ai-weights" -->
The documentation puts `weight` and `ignore_lower_weights` beside `ai_will_do`, not inside it, and `ignore_lower_weights` is a yes/no value:

```text
ai_weights = {
	button_name_click = {
		ai_will_do = {
			base = 10
			modifier = {
				tag = GER
				add = 50
			}
		}
		ignore_lower_weights = yes
		weight = 50
	}
}
ai_max_weight_taken_per_test = 100
```

`weight` is the weight of the option, `ignore_lower_weights = yes` makes the AI skip options of lower weight, and `ai_max_weight_taken_per_test` stops the AI from clicking more buttons once that weight is reached. The block form `ignore_lower_weights = { factor = <float> }` in the template below, and the sentences above that attach `weight` and `ignore_lower_weights` to `ai_will_do`, have no counterpart in the documentation. [docs] `common/scripted_guis/_documentation.md`. Whether the engine also accepts the wiki forms is untested. [unverified] In a test, `weight = 50` inside an `ai_weights` entry was reported at load as "unknown command 'weight' for MTTH" (in three of the four test files), yet the buttons of those files were still pressed by the AI. A test with `ignore_lower_weights` written as a block with `factor` gave no load error and its button was never pressed. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log and game.log read over 6 game days. Why that button was never pressed was not isolated.

The `ai_will_do` inside an entry is a normal AI value block: the documentation example uses `base` with a `modifier` that carries `add`. No vanilla scripted GUI has an `ai_weights` block. [docs] `common/scripted_guis/_documentation.md`. [vanilla-confirmed 1.19.4.1] 0 of 19.
<!-- kit:end id="sg-ai-weights-notes" -->

<!-- kit:begin id="sg-ai-parent-notes" at="section:ai-parents" -->
The key that sets an AI parent is `ai_test_parent` in the wiki template. The documentation does not list it and no vanilla scripted GUI uses it. [vanilla-confirmed 1.19.4.1] `common/scripted_guis/_documentation.md`, `common/scripted_guis/*.txt`. The string is present in `hoi4.exe`, and the key is untested. [unverified] The documented key for attaching one scripted GUI to another is `parent_scripted_gui`, which concerns the window, not the AI. [docs] `common/scripted_guis/_documentation.md`.
<!-- kit:end id="sg-ai-parent-notes" -->

<!-- kit:begin id="sg-template-keys" at="section:template" -->
Every top-level key of a scripted GUI that the sources name. "Vanilla" counts the 19 vanilla scripted GUIs that use the key.

| Key | Source | Vanilla |
| --- | --- | --- |
| `context_type` | docs, wiki | 19 |
| `window_name` | docs, wiki | 19 |
| `parent_window_token` | docs, wiki | 0 |
| `parent_window_name` | wiki, `hoi4.exe` (the docs spell it `parent_window_window`) | 0 |
| `parent_scripted_gui` | docs | 0 |
| `map_mode` | docs | 0 |
| `mapicon_targets` | docs, `hoi4.exe` | 0 |
| `visible` | docs, wiki | 0 |
| `effects` | docs, wiki | 0 |
| `triggers` | docs, wiki | 4 |
| `properties` | docs, wiki | 12 |
| `dynamic_lists` | docs, wiki | 2 |
| `dirty` | docs, wiki | 1 |
| `ai_enabled`, `ai_check`, `ai_check_scope` | docs, wiki | 0 |
| `ai_test_interval`, `ai_test_variance`, `ai_test_scopes` | docs, wiki | 0 |
| `ai_weights`, `ai_max_weight_taken_per_test` | docs, wiki | 0 |
| `ai_test_parent` | wiki, `hoi4.exe` | 0 |

Rows whose source is `hoi4.exe` rest on an executable string, so they are [unverified]. The "Source" column: [docs] `common/scripted_guis/_documentation.md`. The "Vanilla" column: [vanilla-confirmed 1.19.4.1] `common/scripted_guis/*.txt`.
<!-- kit:end id="sg-template-keys" -->

<!-- kit:begin id="sg-tips-notes" at="section:tips" -->
Console commands for working on scripted GUIs. All bullets: [docs] `documentation/console_commands_documentation.md`.

- `human_ai` toggles AI for human countries. The page says it writes the AI checks to `scripted_ai.log`; that file name appears in `hoi4.exe` but not in the documentation. [docs] `documentation/console_commands_documentation.md` says only "Toggles AI for Human countries". The log write is untested. [unverified] The log is written: with `human_ai` on, `scripted_ai.log` appeared in the logs folder, held GER's evaluations only (GER being the human country), with a score near 10 and an `ignore_below` value one lower (for example `igc_f_g250_c_btn_click GER ignore_below:9.2824`). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted_ai.log read over 6 game days. Only 6 days of GER lines were read.
- `reloadinterface` reloads the entire interface, which picks up edits to `interface/*.gui` without a restart. See [Console commands](console_commands.md).
- `dbg_enable_scripted_gui <scope>` enables scripted GUIs and is not available in the release build. `guibounds` (alias `gui`) toggles GUI bounds debugging and `debug_nogui` toggles the whole GUI.

The statement that event targets cannot be used in scripted GUIs is not in the documentation, and vanilla scripted GUIs contain no script that would test it (0 of 19 use `event_target`). [vanilla-confirmed 1.19.4.1] `common/scripted_guis/*.txt`. Whether event targets work there is untested. [unverified]
<!-- kit:end id="sg-tips-notes" -->
