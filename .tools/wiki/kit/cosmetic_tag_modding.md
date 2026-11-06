# Cosmetic tag modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="67378" sources="common/countries/cosmetic.txt localisation/english/countries_cosmetic_l_english.yml gfx/flags/ common/names/ portraits/ gfx/entities/ common/autonomous_states/ common/on_actions/_documentation.md documentation/effects_documentation.md documentation/triggers_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `common/countries/cosmetic.txt` (387 entries), the vanilla cosmetic localisation file (3,230 keys), `gfx/flags/`, `common/names/`, `portraits/`, `gfx/entities/`, every vanilla use of `set_cosmetic_tag` and `drop_cosmetic_tag`, and the effect, trigger and on action documentation.
Kit blocks added: scopes and vanilla use of the effects, flag file checks, `cosmetic.txt` format counts, localisation key shapes with counts, names, portraits and entities in vanilla.
Gaps left: how the game ranks competing flag and name variants, and the "one tag at a time" rule, are engine behaviour that script does not show. `COSMETICTAG` and `EUROPEAN_COSMETIC_TAG` are the wiki's placeholder names, not vanilla names. No vanilla entity is named after a cosmetic tag, so the entity example is unconfirmed.
**1.19.4.1 re-check (2026-11-01).** 6 tagged statements depended on files the update changed (`common/countries/cosmetic.txt`, `gfx/flags/`, the cosmetic localisation file, `common/names/00_names.txt` and the script folders that use the effects), and all of them were re-measured. `cosmetic.txt` has one more entry (388), one more cosmetic id has a group flag (197), the localisation key shapes grew (653 and 1,724 keys in the two largest) and `set_cosmetic_tag` is used 927 times in 178 files; the one new entry, `samanid_empire_tag`, has four group flags in `gfx/flags/`, and the tags without a flag file are still 115. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="cosmetic-flag-vanilla" at="section:flag" -->
Checks of the flag rules against `gfx/flags/`. All items: [vanilla-confirmed 1.19.4.1] `gfx/flags/`, `common/countries/cosmetic.txt`.

- The three sizes and the format hold: a sampled cosmetic flag (`RAJ_UK.tga`) is a 32-bit uncompressed TGA of 82x52 pixels in `gfx/flags/`, 41x26 in `gfx/flags/medium/` and 10x7 in `gfx/flags/small/`. The folders are only `medium` and `small`.
- File names follow `TAG.tga` and `TAG_<group>.tga` where `<group>` is one of `democratic`, `communism`, `fascism`, `neutrality` (for example `MAL_UK_democratic.tga`). Of the 387 distinct tags in `cosmetic.txt`, 91 have a plain `TAG.tga`, 197 have at least one group flag and 115 have no flag file at all, so they only change name, colour or the other cosmetic parts.
<!-- kit:end id="cosmetic-flag-vanilla" -->

<!-- kit:begin id="cosmetic-colour-vanilla" at="section:map-colour" -->
`common/countries/cosmetic.txt` has 388 entries (387 distinct ids; `SOV_ROME` is defined twice) and every one sets both `color` and `color_ui`. `color` is written with `rgb` in 386 entries and `hsv` in 2; `color_ui` with `rgb` in 387 and `hsv` in 1. An entry is optional: vanilla sets 191 cosmetic tag ids that have no entry in the file. [vanilla-confirmed 1.19.4.1] `common/countries/cosmetic.txt`, and every vanilla `set_cosmetic_tag` call.
<!-- kit:end id="cosmetic-colour-vanilla" -->

<!-- kit:begin id="cosmetic-localisation-vanilla" at="section:localisation" -->
Key shapes in the vanilla cosmetic localisation file, `localisation/english/countries_cosmetic_l_english.yml` (UTF-8 with BOM, `l_english:` header). The file mixes cosmetic tags and ordinary country tags; the counts below cover only keys whose tag is a cosmetic id (an id from `cosmetic.txt` or one set by script that is not a plain 3-letter tag): 2,486 keys in the first four shapes below. Counts and examples: [vanilla-confirmed 1.19.4.1] `localisation/english/countries_cosmetic_l_english.yml`.

| Shape | Keys | Example |
| --- | --- | --- |
| `<TAG>`, `<TAG>_DEF`, `<TAG>_ADJ` | 653 | `INS_HOL`, `INS_HOL_DEF`, `INS_JAP_ADJ` |
| `<TAG>_<group>` with optional `_DEF` or `_ADJ` | 1,724 | `RAJ_UK_democratic`, `RAJ_UK_democratic_DEF` |
| `<TAG>_autonomy_<autonomy id>` with optional `_DEF` or `_ADJ` | 106 | `INS_HOL_autonomy_dominion`, `INS_HOL_autonomy_dominion_DEF` |
| `<TAG>_subject` | 3 | `RAJ_UK_subject` |
| `<TAG>_<group>_autonomy_<autonomy id>` with optional suffix | 12 | `UKR_SOV_communism_autonomy_dominion` |
| `<TAG>_<overlord tag>_<group>_subject` or `<TAG>_<overlord tag>_subject`, optional suffix | 34 | `turkestan_united_SOV_communism_subject`, `dalmatia_YUG_subject` |

- `<group>` is one of the four ideology groups (`democratic`, `communism`, `fascism`, `neutrality`). The file has no key that adds a sub-ideology type such as `despotism` to a cosmetic tag, so the wiki's `COSMETICTAG_despotism_subject` has no vanilla precedent. [vanilla-confirmed 1.19.4.1] `localisation/english/countries_cosmetic_l_english.yml`: of 3,242 keys, none has a type id of `common/ideologies/00_ideologies.txt` in the ideology slot. The only hits, `SPR_POR_anarchism_*` and `ARG_marxism`, are part of the cosmetic id.
- `<autonomy id>` is the `id` of an autonomy state in `common/autonomous_states/`, written with its `autonomy_` prefix, for example `autonomy_dominion` or `autonomy_puppet`.
- Cosmetic ids need not be 3 letters or upper case: the file has keys such as `turkestan_united_...` and `FRA_THIRD_EMPIRE_def`. 90 cosmetic keys end in a lower-case `_def` or `_adj` (for example `USA_wallis_simpson_neutrality_def`) next to the upper-case `_DEF` and `_ADJ` forms, and none of the 90 has an upper-case twin. [vanilla-confirmed 1.19.4.1] `localisation/english/countries_cosmetic_l_english.yml`. Write `_DEF` and `_ADJ` in upper case. The lower-case keys are read all the same. SPR first gave GetName "Spain", GetNameDef "Spain" and GetAdjective "Spanish". After `set_politics = { ruling_party = neutrality }` and `set_cosmetic_tag = SPR_anarchist_spain` it gave "Regional Defense Council of Aragón", "the Regional Defense Council of Aragón" and "Aragonese Anarchist", from the lower-case keys `SPR_anarchist_spain_neutrality_def` and `_adj`, which have no upper-case twin. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, name getters logged with the `log` effect.
- Keys can reuse others with `$KEY$`, for example `INS_HOL_FLAG_autonomy_dominion: "$INS_HOL_autonomy_dominion$"`, and use the tokens `$OVERLORDADJ$` (`RAJ_UK_subject: "$OVERLORDADJ$ Raj"`) and `$NONIDEOLOGY$`. `INS_HOL_FLAG` is a separate entry in `cosmetic.txt` with the same colours as `INS_HOL`, and its names point back to `INS_HOL`.
<!-- kit:end id="cosmetic-localisation-vanilla" -->

<!-- kit:begin id="cosmetic-other-vanilla" at="section:other-changes" -->
What vanilla does with the three minor uses. The placeholder ids `COSMETICTAG` and `EUROPEAN_COSMETIC_TAG` are not vanilla names; use a real id. All items: [vanilla-confirmed 1.19.4.1] `common/names/00_names.txt`, `portraits/00_portraits.txt`, `portraits/998_scientist_portraits.txt`, `gfx/entities/`.

- Names: only `RAJ_UK` and `MAL_UK` have a cosmetic entry in `common/names/00_names.txt`.
- Portraits: `RAJ_UK`, `MAL_UK`, `INS_HOL` and `SAF_COM` have top-level entries in `portraits/00_portraits.txt` and in `portraits/998_scientist_portraits.txt`, next to the real tag entries (`GER`, `ENG`, ...). The file also has `default` and `continent` blocks.
- Entities: no `.asset` file in `gfx/entities/` defines an entity whose name starts with a cosmetic tag id, so the wiki's `COSMETICTAG_artillery_entity` pattern is not exercised by vanilla. [vanilla-confirmed 1.19.4.1] `gfx/entities/` (6,254 `name` values checked against all 388 ids in `common/countries/cosmetic.txt`). Whether the game uses such an entity is [unverified].
<!-- kit:end id="cosmetic-other-vanilla" -->

<!-- kit:begin id="cosmetic-effects-vanilla" at="section:application" -->
Scopes, forms and use of the cosmetic tag effects and trigger. Scope and syntax: [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`. Counts: [vanilla-confirmed 1.19.4.1] over `common/`, `events/` and `history/`.

| Name | Kind | Scope | Vanilla form and use |
| --- | --- | --- | --- |
| `set_cosmetic_tag` | effect | COUNTRY, no targets | Always `set_cosmetic_tag = ID` (927 uses in 178 files, 560 different ids). |
| `drop_cosmetic_tag` | effect | COUNTRY, no targets | Always `drop_cosmetic_tag = yes` (252 uses in 71 files). The documentation example `INS = { drop_cosmetic_tag }` has no value; write `= yes` as vanilla does. |
| `has_cosmetic_tag` | trigger | COUNTRY | `has_cosmetic_tag = ID`. Almost all of its 87,057 uses are in scripted localisation. |

- Where `set_cosmetic_tag` appears: national focuses 281, events 202, scripted effects 142, decisions 144, on actions 132, `history/countries/` 24, and 2 inside an idea's effect block (`common/ideas/czechoslovakia.txt`), so country history files, idea effects and on actions all accept it.
- `on_ruling_party_change`, `on_government_change`, `on_puppet`, `on_release_as_puppet` and `on_subject_autonomy_level_change` are all listed in the on action documentation, so a cosmetic tag can be tied to an ideology change, a puppeting or a change of autonomy level. [docs] `common/on_actions/_documentation.md`
- Since it takes a bare id, the scope the effect runs in decides which country gets the tag; wrap it in `TAG = { set_cosmetic_tag = ID }` when you are not already in that country's scope. [docs] `documentation/effects_documentation.md`
- Of the ids vanilla sets, 191 are not listed in `common/countries/cosmetic.txt`, and 18 ids listed there are never set by vanilla script. [vanilla-confirmed 1.19.4.1] `common/countries/cosmetic.txt`.
<!-- kit:end id="cosmetic-effects-vanilla" -->
