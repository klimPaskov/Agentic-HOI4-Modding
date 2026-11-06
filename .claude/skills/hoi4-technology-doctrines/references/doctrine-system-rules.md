# Hearts of Iron IV Technologies and Doctrines: Doctrine system rules

Part of the [hoi4-technology-doctrines](../SKILL.md) skill. Read before scripting grand doctrines, sub-doctrines, mastery or doctrine effects, triggers and modifiers.

## Doctrines

The current system is data in `common/doctrines/`: a **folder** holds mutually exclusive **grand doctrines**; a grand doctrine lists **tracks**; each track holds one **sub-doctrine** whose **rewards** unlock as **mastery** accrues; completing a track gives the grand doctrine's **milestone** for that track.
Grand doctrines and sub-doctrines cost experience of one `xp_type` (`army`, `navy`, `air`).

Folder files: `folders/`, `grand_doctrines/`, `tracks/`, `subdoctrines/` (any subfolder).
Vanilla precedents: `GAME/common/doctrines/folders/doctrine_folders.txt`, `grand_doctrines/land_grand_doctrines.txt` (`new_mobile_warfare`), `tracks/land_doctrine_tracks.txt`, `subdoctrines/land/armor_subdoctrines.txt`.

Key rules:

- Use the exact vanilla ids.
  The grand doctrine ids are `new_mobile_warfare`, `superior_firepower`, `grand_battleplan`, `mass_assault`, `new_strategic_destruction`, `new_battlefield_support`, `new_operational_integrity`, `new_fleet_in_being`, `new_convoy_raiding`, `new_base_strike`, `special_forces_quantity`, and `special_forces_quality`.
  The installed `_documentation.md` example `set_grand_doctrine = mobile_warfare` is not a vanilla id; history files use `new_mobile_warfare`.
- Activation effects are written directly in a grand doctrine, milestone, sub-doctrine, or reward: country modifiers (optionally in `modifiers = { }`), `enable_tactic`, sub-unit and category stat blocks, `equipment_bonus`, and `effect = { }` for scripted effects.
- Named reward blocks make localisation keys `<subdoctrine>_<reward>` (see `armored_spearhead_force_concentration` in `GAME/localisation/english/doctrines_l_english.yml`); the file notes a `_desc` key is also read.
- Mastery accrues from the manpower of the sub-units, categories, or equipment configured in the track's `mastery` block, overridden per sub-doctrine; tuning lives in `NDoctrines` in the defines (`DEFAULT_REWARD_MASTERY` 100, `MAX_MONTHLY_MASTERY_GAIN` 40, bank values).
- A reward's `mastery = N` overrides the default amount needed for that reward.
- `xor = { ... }` on a sub-doctrine blocks others from being active simultaneously in other tracks of the same folder; replacing on the same track is still allowed.
- `allow_in_multiple_tracks = yes` lets one sub-doctrine sit in several tracks at once.
- `track` on a sub-doctrine may be a list.
- Track `active` is a trigger that gates sub-doctrine selection and mastery gain (including banked mastery).
- Use `equipment_bonus` in doctrine blocks, not the `add_equipment_bonus` effect, because only the former is removed when the doctrine changes.

Effects: `set_grand_doctrine = id`, `set_sub_doctrine = id` or the extended form with `sub_doctrine`, `folder`, `track` (0-based index among all tracks in the folder), `add_mastery`, `add_daily_mastery`, `add_mastery_bonus`, and `add_doctrine_cost_reduction` (a limited-use cost reduction).
Filters on the mastery effects are `folder`, `grand_doctrine`, `sub_doctrine`, `track`, and `index`; a missing filter matches all.

Triggers: `has_doctrine` (grand or sub), `has_any_grand_doctrine = <folder>`, `has_subdoctrine_in_track = <track>`, `has_completed_subdoctrine`, `has_completed_track`, `has_mastery = { amount track }`, `has_mastery_level = { amount sub_doctrine }`, and `land_doctrine_level` (documented as checking the researched land doctrine level).

Modifiers (confirmed against `GAME/documentation/modifiers_documentation.md` and vanilla usage):

- `<folder>_doctrine_cost_factor`, for example `land_doctrine_cost_factor` and `naval_doctrine_cost_factor`.
- `<folder>_mastery_gain_factor`, for example `land_mastery_gain_factor`.
- `<track>_track_mastery_gain_factor`, for example `operations_track_mastery_gain_factor`.
- `<grand_doctrine>_mastery_gain_factor` and `<sub_doctrine>_mastery_gain_factor`.
- The installed `_documentation.md` writes the folder form as `land_track_mastery_gain_factor`; the modifier list and vanilla ideas use `land_mastery_gain_factor`, so use the latter.

Details for writing a new folder, grand doctrine, track, and sub-doctrine, their localisation and sprites, and the interface notes are in `references/doctrine-authoring.md`.

