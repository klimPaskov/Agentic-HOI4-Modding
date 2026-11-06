---
name: hoi4-localisation
description: Use when writing, fixing or auditing HOI4 localisation, covering .yml files, keys, replace, § colours, £ icons, [Scope.Get] and [?var] commands, scripted localisation and raw keys in game.
---

# HOI4 Localisation

This skill covers `localisation/**/*.yml`, `common/scripted_localisation/*.txt` and the `$KEY$`, `[...]`, `§` and `£` codes in text. `hoi4-events`, `hoi4-decisions-missions`, `hoi4-ideas-modifiers` and `hoi4-characters-leaders` own which keys their objects need.

`GAME` is the installed game folder named in `CLAUDE.md` (build 1.19.4.2). `[vanilla-confirmed 1.19.4.2]` means counted or read in the installed game. `[docs]` means only a document says it (the game's `documentation/` or the wiki snapshot written for 1.19.4.1). `[game-tested 1.19.4.1]` is a test the wiki page records, not re-run. Installed files beat the wiki.

## Source map

| Topic | Wiki (`hoi4_wiki/`) | Installed |
| --- | --- | --- |
| File rules, BOM, replace | [checklist](../../../hoi4_wiki/localisation.md#quick-checklist), [replacing](../../../hoi4_wiki/localisation.md#replacing) | `GAME/localisation/` |
| Key lines, `$KEY$` | [basics](../../../hoi4_wiki/localisation.md#basics), [nesting](../../../hoi4_wiki/localisation.md#nesting-strings) | `GAME/localisation/english/` |
| `§` and `£` | [colours](../../../hoi4_wiki/localisation.md#colouring-characters), [icons](../../../hoi4_wiki/localisation.md#text-icons) | `GAME/interface/core.gfx`, `texticons.gfx` |
| Loc commands, scopes | [namespaces](../../../hoi4_wiki/localisation.md#namespaces), [objects](../../../hoi4_wiki/localisation.md#documentation-of-localized-objects), [dual scopes](../../../hoi4_wiki/scopes.md#dual-scopes) | `GAME/documentation/loc_objects_documentation.md` |
| Variables in text | [formats](../../../hoi4_wiki/localisation.md#formatting-variables), [variables](../../../hoi4_wiki/data_structures.md#localisation) | `GAME/localisation/english/` |
| Formatters, bound tooltips | [bindable](../../../hoi4_wiki/localisation.md#bindable-localisation) | `GAME/documentation/loc_formatter_documentation.md`, `script_concept_documentation.md` |
| Scripted localisation | [scripted](../../../hoi4_wiki/localisation.md#scripted-localisation), [temp variables](../../../hoi4_wiki/localisation.md#temporary-variable-display) | `GAME/common/scripted_localisation/00_scripted_localisation.txt` |
| Event and idea keys | [events](../../../hoi4_wiki/event_modding.md#localisation), [ideas](../../../hoi4_wiki/idea_modding.md#localisation) | `GAME/events/`, `GAME/common/ideas/` |

## Checklist

1. Name files `localisation/<language>/<name>_l_<language>.yml` and make line 1 the header `l_<language>:`, because a name without the language is not loaded. [docs] In vanilla 2,091 of 2,092 language-folder files carry their folder's language and 2,083 have the header on line 1. [vanilla-confirmed 1.19.4.2]
2. Save UTF-8 with BOM and LF line endings, as all 2,093 vanilla `.yml` files are. [vanilla-confirmed 1.19.4.2] A test file without the BOM logged "Missing UTF8 BOM" in `error.log` and its keys showed as raw names. [game-tested 1.19.4.1]
3. Write `key: "text"` on one line with no version number (kit rule). The game ignores the number [docs], yet vanilla English has it on 2,378 of 130,098 lines, indents one space on 119,128 and not at all on 4,787. [vanilla-confirmed 1.19.4.2] See open point 1.
4. Use only letters, digits, `_`, `.` and `-` in keys, as vanilla does. [vanilla-confirmed 1.19.4.2] Any other character breaks the rest of the file. [docs]
5. Write line breaks as `\n`, inner quotes as `\"` and comments with `#` at a line start or after the closing quote. Vanilla English has `\n` 12,287 times, `\"` 52, `\t` 16 and no other escape, plus 2,462 comment lines and 346 trailing comments. [vanilla-confirmed 1.19.4.2]
6. Define each key once. In a test the first of two files by name won and `text.log` listed "Duplicate localization found". [game-tested 1.19.4.1] Vanilla English repeats no key. [vanilla-confirmed 1.19.4.2]
7. To change a vanilla key use `localisation/english/replace/<name>_l_english.yml`. A test also overrode a key with files in `localisation/replace/` and `localisation/replace/english/`. [game-tested 1.19.4.1] Vanilla has no `replace` folder. [vanilla-confirmed 1.19.4.2] A mod file named like a vanilla file overwrites it whole. [docs]
8. Name event text inside the event (`title`, `desc`, option `name`), usually `<namespace>.<n>.t`, `.d` and `.a`. [docs] All 6,803 visible vanilla events set `title` and `desc`. [vanilla-confirmed 1.19.4.2] Do not rely on an implicit `<id>.t`. [unverified]
9. Focuses, decisions and ideas use their id (idea: its `name`) as key and `<key>_desc` as description. [docs] Vanilla defines every focus title and description but leaves about two thirds of decision `_desc` keys undefined (2,800 of 4,201), so `_desc` is optional. [vanilla-confirmed 1.19.4.2]
10. Country names are `TAG`, `TAG_ADJ` and `TAG_DEF`, with ideology forms such as `GER_fascism`, `GER_fascism_ADJ` and `GER_fascism_party`. Ideology groups have `fascism`, `fascism_noun` and `fascism_desc`. [vanilla-confirmed 1.19.4.2] The `localisation` check holds the other implicit-key rules.
11. A flag in a displayed requirement uses its own name as the tooltip key, and GUI `text`, `pdx_tooltip` and the custom tooltips name keys. [docs] A `GFX_` sprite name is not a key.
12. `$KEY$` inserts another key and `$KEY|Y$` formats it, but a nested `$KEY$` in `pdx_tooltip` shows its dollar signs. [docs] A literal dollar sign is `$$` (`$$100` printed `$100`). [game-tested 1.19.4.1]
13. Write loc commands as `[Scope.Function]` with chains such as `[ROOT.Capital.GetName]` or a character through its country, `[NOR.NOR_otto_ruge.GetName]`. The functions per object are in `loc_objects_documentation.md`. [docs] Vanilla writes `FROM` and `From` alike (6,603 and 2,810 uses) and has 9 country-then-character chains. [vanilla-confirmed 1.19.4.2]
14. Address a saved event target by its bare name, `[my_target.GetName]` (kit rule), and a variable that holds a scope with the `?`, `[?var.GetName]`. [docs] Vanilla also writes `[?event_target:name.GetName]` 37 times and `[event_target:name...]` 4 times. [vanilla-confirmed 1.19.4.2]
15. Show variables with `[?var]`, `[?TAG.var]` or `[?var@token]`. After a pipe go digits for decimals, `%`, `+` or `-` for good or bad colour, `=` for a sign, `*` or `^` for K and M, and colour letters. [docs] Vanilla English has 1,795 `[?` uses, 444 with a format, mostly `|+0`, `|Y0` and `|%`. [vanilla-confirmed 1.19.4.2]
16. Bind tooltip parts with `custom_effect_tooltip = { localization_key = KEY PARAM = value }`, which fills `$PARAM$` in KEY with a key, a string or another bound object. Eight formatters such as `idea_desc|x` and `country_leader_desc|x` work in the same places (`loc_formatter_documentation.md`). `custom_trigger_tooltip` is an alias of `custom_override_tooltip`. [docs]
17. Colour with `§Xtext§!` and close every span. [docs] X is one of 23 letters in the global `textcolors` of `interface/core.gfx` (`C L W B G R b g Y H T O`, `0` to `9`, `t`), and vanilla uses `§Y` 12,297 times, then `G`, `R`, `H` and `L`. [vanilla-confirmed 1.19.4.2] An unknown letter logs "Could not find coloring for character". [game-tested 1.19.4.1] A scripted localisation can return a letter for `§[GetColorX]` (13 vanilla uses). [vanilla-confirmed 1.19.4.2]
18. Show icons with `£name`, which pulls sprite `GFX_name`, or `£name|N` for frame N. `£GFX_name` also works. Vanilla has 1,580 `£name` against 351 `£GFX_name`. [vanilla-confirmed 1.19.4.2] `@TAG` shows a flag. [docs]
19. Define scripted localisation in `common/scripted_localisation/<name>.txt` as below. All 1,546 vanilla entries use only `name` and `text`, and a `text` only `trigger`, `localization_key` (with a z) and `random_list`. None of the 42 files has a BOM. [vanilla-confirmed 1.19.4.2]
```
defined_text = {
	name = GetMyText
	text = { trigger = { tag = FRA } localization_key = FRA_text }
	text = { localization_key = default_text }
}
```
20. The first `text` whose trigger passes wins, so put a trigger-less default last (all 829 vanilla ones are). Triggers must suit the scope the key is called in. Call it as `[GetMyText]` or `[ROOT.GetMyText]`. [vanilla-confirmed 1.19.4.2]
21. Put a formatted number in a real `.yml` key and name that key (kit rule, `hoi4-events`). Vanilla has 27 quoted bracket strings and none has a `|format`. [vanilla-confirmed 1.19.4.2]
22. Give a `random_list` a `seed = <scoped variable>`, or the roll repeats. The vanilla header says so and seeds 12 of 22 blocks. [vanilla-confirmed 1.19.4.2]
23. Never write `§` or `£` in scripted localisation (kit rule, checked by `script-rules`). None of the 42 vanilla files has one. [vanilla-confirmed 1.19.4.2]
24. Vanilla ships ten languages: `l_english`, `l_braz_por`, `l_french`, `l_german`, `l_polish`, `l_russian`, `l_spanish`, `l_japanese`, `l_simp_chinese`, `l_korean`. A translation is another file with that language's name and header. Vanilla has every English key in all ten and some languages add their own. [vanilla-confirmed 1.19.4.2] The fall-back for a key missing in the chosen language is not known. [unverified]

## Silent failures

- A raw key in game means an undefined key, an unloaded file (wrong name, no BOM, an earlier parse error) or an object reading another key (`name =`). [docs]
- One bad line breaks the file from there on. [docs]
- A duplicate key (`text.log`) and an unknown colour letter (`error.log`) leave only a log line, and a missing BOM also shows raw keys. [game-tested 1.19.4.1]
- `§X` without `§!` bleeds into later text. [docs]
- `[...]` shown literally means the UI has no dynamic text, and a focus title needs `dynamic = yes`. [docs]
- `[var]` without `?` reads a scope, not a variable, and a glyph missing from the font prints `?`. [docs]

## Validation

Run `python -B .tools/check.py quick --paths localisation/english/x.yml` or `full --only localisation script-rules asset-wiring`. The `localisation` check reads BOM, header, `key: "value"` shape, `:0` suffixes, duplicates, undefined keys that script names, flags and variables in displayed requirements and the implicit keys above. `--calibrate` shows how well each rule fits vanilla. `script-rules` checks `§` and `£` in scripted localisation, and `asset-wiring` resolves `£name` to `GFX_name`.

It does not prove what the player sees, that a `[...]` command suits its scope, that `§` letters pair up, that scripted localisation triggers pass, other languages, `localisation/english/` subfolders, `localisation/replace/` (only `localisation/english/replace/` is read, to resolve keys) or prose quality (`hoi4-localisation-auditor`). Its achievement rule matches 0 of 586 vanilla ids, so doubt those findings. In game the `loc_check` console commands list missing keys ([checking localisation](../../../hoi4_wiki/localisation.md#checking-localisation)). [docs]

## Unverified or open points

1. `CLAUDE.md` section 2 says no leading space before a key, but the shipped `hoi4ms_super_events_l_english.yml` and most of vanilla use one. That unindented keys load is inferred from vanilla, not tested. The maintainer should pick a style.
2. The `localisation` check assumes `<id>.t` and `.d` when an event has no `title` or `desc`. Vanilla never omits them.
3. What a scripted localisation shows when no `text` passes, and which of two `defined_text` entries with one name wins (vanilla repeats 7 names), are unknown.
4. Key case sensitivity, a mod key that repeats a vanilla key outside `replace`, and the crash the wiki ties to a missing header are untested.
5. The wiki advises no space after `\n`, yet vanilla has 924.
6. `dynamic_variables_documentation.md` lists variables and has no display syntax, so `[?var|fmt]` rests on the wiki and vanilla use.
7. Tests tagged `[game-tested 1.19.4.1]` come from tests the wiki pages record and were not re-run on 1.19.4.2.
