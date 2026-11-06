# HOI4 Decisions and Missions: Trigger clarity and engine facts

Part of the [hoi4-decisions-missions](../SKILL.md) skill. Read before writing available, visible, allowed or target triggers and the requirement text the player sees.

## 7. Trigger and requirement clarity

Long triggers should not be exposed raw to the player.

Use:

- scripted triggers
- custom trigger tooltips
- scripted localisation
- named regions
- short requirement summaries with detailed tooltips

Avoid showing huge trigger blocks inside the UI.

Any requirement involving places must name the places or a clear named region.

Bad:

- `required states`
- `border states`
- `some divisions`
- `sufficient troops`
- `enough equipment`

Good:

- `Place 8 supplied divisions in Smolensk, Gomel, and Bryansk.`
- `Hold Kyiv and Minsk for 120 days.`

If the list is dynamic, scripted localisation must print the current targets or explain the named region.

Every named region should have a tooltip or documentation entry explaining which states belong to it.

### Trigger evaluation cost

The installed vanilla `common/decisions/_documentation.md` defines how often each block runs. `allowed` runs once at game start or save load, so permanent filters such as `original_tag` belong there. `visible` and `available` run every frame while the decision interface refreshes, so keep them cheap and move expensive or world-scanning checks elsewhere. For targeted decisions, put acting-country prechecks in `target_root_trigger` and per-target selection in `target_trigger`, which run once per day, and narrow the candidates with `targets`, `target_array` (vanilla `AST.txt` uses `target_array = AST.core_states`), or a `state_target` value such as `any_controlled_state` instead of checking every state or country. Vanilla writes `state_target` (209 `state_target = yes`, 34 `state_target = any_controlled_state`) and never the documentation's `state_trigger`. [vanilla-confirmed 1.19.4.1]

### Engine facts for decision keys

- In a targeted decision `ROOT` is the taker and `FROM` the current target. [vanilla-confirmed 1.19.4.1]
- `activate_targeted_decision` works on decisions that are not missions (44 of 63 vanilla targets). [vanilla-confirmed 1.19.4.1]
- The `highlight_color_*` values index the 15-entry define `BORDER_COLOR_CUSTOM_HIGHLIGHTS`, not 0 to 3. [vanilla-confirmed 1.19.4.1]
- `visible_when_empty` is used in 45 vanilla files but is undocumented. [vanilla-confirmed 1.19.4.1]
- The wiki example name `has_command_power` does not exist, because the trigger is `command_power`. [docs] [vanilla-confirmed 1.19.4.1]
- All 3 vanilla costed missions are selectable. [vanilla-confirmed 1.19.4.1] A `cost` on an unselectable mission logs "Cost for normal missions not implemented". [unverified]

