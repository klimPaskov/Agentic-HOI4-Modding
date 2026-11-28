# Feature ledger

Part of the [hoi4-new-mod](../SKILL.md) skill. Read before writing or changing `docs/mod/ledger.json`.

The ledger is the mod's build plan in a form a program can check. `python -B .tools/check.py gate` reads it, so completion depends on the files, not on anyone's word. It is JSON because agents overwrite JSON less freely than prose.

## Format

```json
{
  "schema": "hoi4-mod-ledger/1",
  "mod": "Hanseatic Revival",
  "state": "planning",
  "scope": {"summary": "The Hanseatic League restored as a Baltic power, playable from 1936, with its rivals",
    "phases": [{"id": "core", "title": "Playable Hansa"}, {"id": "rivals", "title": "Rivals and the Baltic struggle"}],
    "surfaces": ["map", "country", "history", "ideas", "characters", "focus_tree", "events", "decisions", "ai", "art", "localisation"]},
  "gate": {"max_blocks": 30, "max_idle_blocks": 3},
  "placeholders_allowed": [],
  "features": [
    {
      "id": "country-han",
      "title": "Hansa country package",
      "phase": "core",
      "surfaces": ["country", "history", "localisation"],
      "depends_on": ["map-states"],
      "acceptance": [
        "HAN is defined with colours, a country file and 1936 history: capital, government, ideology popularities, leader, starting technology and forces",
        "Every new name has English localisation"
      ],
      "checks": [
        {"kind": "exists", "path": "history/countries/HAN - Hansa.txt"},
        {"kind": "contains", "path": "common/country_tags/*.txt", "regex": "^HAN\\s*="}
      ],
      "evidence": [],
      "passes": false,
      "blocker": null
    }
  ]
}
```

The example shows one feature of eleven surfaces. A real ledger has a feature for each buildable unit (`map-states` among them), and until it does the gate names every surface of `scope.surfaces` that has no feature.

| Field | Rule |
| --- | --- |
| `schema` | Always `hoi4-mod-ledger/1` |
| `state` | `planning` while the brief and scope are agreed (the gate is off), `building` once they are (the gate is on), `paused` when the user said stop, `complete` after the final report |
| `scope.kind`, `scope.request` | Optional. `mod` (the default) is a whole mod; `addition` is one big request on an existing mod and needs `scope.request`, a short slug (the request brief is `docs/mod/requests/<slug>.md`). The gate treats both the same; `check.py gate --archive` moves a `complete` ledger to `docs/mod/history/` before the next one |
| `scope` | A one-line summary of the complete mod or request, `phases` in build order (the playable core first, then each expansion from the brief) and `surfaces`: every surface the build plan names. The gate fails while a listed surface has no feature whose `surfaces` include it |
| `features[].phase` | The id of the phase the feature belongs to. The gate fails when a feature of a later phase passes while a feature of an earlier phase is still open, so the core is finished and playable first |
| `features[].surfaces` | The surfaces this feature builds, in the same words as `scope.surfaces` |
| `gate` | Optional caps for the Stop hook. Leave the defaults unless the user asks |
| `placeholders_allowed` | `{"path": ..., "reason": ...}` rows for placeholders the user approved, such as a sourced portrait waiting for its styled replacement. A folder path ends in `/` |
| `features[].id` | Lower-case letters, digits, `-` and `_`, unique |
| `depends_on` | Ids of features that must pass first. No cycles |
| `acceptance` | What a reviewer checks, in words: specific, countable where possible, taken from the scope contract and the owning skill's quality bar |
| `checks` | Machine checks the gate runs on a passed feature (below). They prove part of the acceptance, never all of it |
| `evidence` | Repository paths that prove the feature: a spec or report, check output saved under `docs/`, a render, an in-game log. Each must exist |
| `passes` | `false` until the acceptance is met and the evidence exists. Only then `true` |
| `blocker` | `null`, or `{"needs": ..., "reason": ...}` for a true blocker (below) |

Agents change `passes`, `evidence`, `blocker` and `state` as work proceeds. Adding a feature is fine. Removing a feature, weakening its `acceptance` or lowering a check's `min` needs the user's approval, recorded in `decisions.md`.

## Machine checks

| Kind | Holds when |
| --- | --- |
| `{"kind": "exists", "path": "<path or glob>", "min": 1}` | At least `min` files match |
| `{"kind": "contains", "path": "<path or glob>", "text": "<literal>"}` or `"regex": "<pattern>"` | The text or pattern occurs at least `min` times (default 1) across the matching files |
| `{"kind": "count", "path": "<glob>", "regex": "<pattern>", "min": <n>}` | The same as `contains`, written for the sizes the brief and the feature spec set, such as the number of focuses or events |

Patterns are Python regular expressions in multiline mode, so `^` matches a line start. Examples: `{"kind": "count", "path": "common/national_focus/han_*.txt", "regex": "^\\tfocus\\s*=", "min": 50}`, `{"kind": "count", "path": "events/han_*.txt", "regex": "^country_event\\s*=", "min": 12}`.

## Blockers

A blocker stops a feature only for a reason the agent cannot remove:

| `needs` | Use for |
| --- | --- |
| `user` | A decision, approval or asset only the user can give (an approved picture round, a portrait they supply) |
| `credential` | A sign-in or key the agent must not handle |
| `money` | Spend beyond the agreed budget |
| `access` | A file, account or service the agent cannot reach |
| `in_game` | An in-game check that cannot run on this machine |
| `tool` | A capability no installed tool has (name the tool and the missing operation) |

Difficulty, length, an unfinished design, a failing check or a missing asset are not blockers: they are open work. A feature that needs a picture makes it with `hoi4-imagegen` once the style round has passed; only the style round itself waits for the user, and it waits with `check.py gate --wait`, not with a blocker. Report every blocker in the final report with what the user can do about it.

## Building the feature list

Cover every surface the build plan names. The core phase takes a first feature of each row the core needs (at least the style round, map presence, the main country, its focus tree, its first events, its characters and their art), and each expansion takes further features of the same rows, such as a rival's country package or a second event chain. Inside a phase, build in this order. Drop a row only when the user excluded the surface, and split a row when it is large.

| Order | Feature | Owning skills | Typical acceptance and checks |
| --- | --- | --- | --- |
| 0 | Art style round | `hoi4-imagegen` | A few pictures in the brief's style (flag, portrait, icon) approved by the user once; every feature with art depends on it |
| 1 | Map and states | `hoi4-map-states` | New or changed states, provinces, victory points, strategic regions and supply load without errors; `exists` on each new state file |
| 2 | Country packages | `hoi4-diplomacy-war`, `hoi4-characters-leaders`, `hoi4-units-divisions` | Tag, colours, country file, history for the start date, leader, parties, starting forces and technology; `contains` on the tag file, `exists` on the history and OOB |
| 3 | Ideologies, ideas and characters | `hoi4-ideologies`, `hoi4-ideas-modifiers`, `hoi4-characters-leaders` | National spirits with real modifiers, advisors and commanders with traits and portraits |
| 4 | Focus trees | `hoi4-focus-trees` | The size the feature spec sets, every focus with effects, AI weights and localisation, a layout that passes the layout verdict; `count` on focuses |
| 5 | Events | `hoi4-events` | Chains with triggers, options with effects, pictures and localisation; `count` on events |
| 6 | Decisions and missions | `hoi4-decisions-missions` | Categories, costs, AI and tooltips |
| 7 | Mechanics and interface | `hoi4-scripted-triggers-effects`, `hoi4-scripted-gui`, `hoi4-on-actions` | The mechanic works from its spec; any custom window built and previewed |
| 8 | AI | `hoi4-ai-strategies` | Strategies and weights for every playable and major new country, analysed with the probability tools |
| 9 | Remaining art | `hoi4-imagegen`, `hoi4-feature-assets`, `hoi4-portrait-production` | Every flag, portrait, focus, idea, decision and event picture not made with its own feature exists in the agreed style |
| 10 | Localisation pass | `hoi4-localisation` | Every key present and readable; `check.py` localisation clean |
| 11 | In-game check | `hoi4-live-playtest` | As the consultation recorded |

Each feature with design depth (a focus tree, an event chain, a mechanic) gets its own spec under `docs/specs/<feature_slug>/` through `hoi4-feature-planning`, and its evidence includes that spec.

## Evidence that counts

- The saved output of the checks that cover the feature (`python -B .tools/check.py quick --json docs/mod/evidence/<id>-checks.json`), with no errors.
- The owning tool's verdict where one exists: a focus layout verdict, a render, `hoi4.script_validate` results, a probability analysis.
- The feature's spec and its implementation handoff.
- For an in-game step, the log or report it produced.

A file that only restates the acceptance is not evidence.
