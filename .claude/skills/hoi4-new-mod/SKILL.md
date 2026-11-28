---
name: hoi4-new-mod
description: Use for a whole new mod or any big request, such as a new nation, a focus tree or an event chain, to write the brief, scope, canon and feature ledger and build to the completion gate.
---

# HOI4 New Mod

This is the mod-level entry point. It turns a short request such as "Create an Atlantis mod.", "Make a mod about a second American civil war." or, in an existing mod, "Add a Hanseatic nation with its own focus tree." into four files, agreed with the user, and then builds it one feature at a time until the deterministic completion gate passes.

The skill works the same for any idea and any model. It never assumes a setting or a nation, and a short request always aims at the complete mod, never a reduced one: every answer comes from the user, the established material, or a suggested default recorded as one.

## When to use it

- The request names a whole mod, a total conversion, a new world, a set of new countries, or an add-on large enough to span several surfaces (map, countries, focus trees, events, decisions, characters, art).
- The request is big (below), even when the mod already exists.
- The user returns to a mod that has `docs/mod/ledger.json`: follow the session routine below before anything else.

Each ledger feature that needs a deep design still gets its own spec through `hoi4-feature-planning`, and one feature the user asks for on its own uses `hoi4-feature-planning` directly.

## Big or small

Decide this before building, from the request and the mod's files, and never from the model, the wording or the mod:

- **Big:** the request adds something new that has parts on two or more surfaces (map, country, history, ideas, characters, focus tree, events, decisions, units, technology, art, localisation, interface), such as a nation, a focus tree with its rewards, an event chain with its pictures and effects, or a mechanic with its decisions and screens; or you expect to build more than about five features, or to need more than one sitting.
- **Small:** it changes something that exists or adds one self-contained thing on one surface: a fix, a rebalance, a rename, one event, one decision, one idea, one localisation block, one icon.

A big request in an existing mod runs this workflow scaled to the request (below). A small one needs no brief, ledger or gate: do it directly with the owning skill. Record the size and the reason in `docs/mod/decisions.md` for a big request, and say it in one line for a small one. When a small request grows past the line while you work, stop and treat it as big.

## Scaled to an existing mod

The workflow is the same; each step takes only what the request needs:

- **Material.** The mod's files, `canon.md` and earlier `docs/mod/` files are established material: read them first and never ask what they answer (setting, era, tone, art style, naming). Without a `canon.md`, write one from the mod's own files, marking what exists as established.
- **Brief.** A half-page request brief in `docs/mod/requests/<slug>.md`: what is added, where it fits in the existing mod, the build plan. The mod's `brief.md` stays as it is.
- **Consultation.** Ask only the questions of `references/mod-consultation.md` that the request leaves open and the files do not answer, in one message with suggestions.
- **Ledger.** `scope.kind` is `addition` and `scope.request` is the slug; `scope.surfaces` lists only the surfaces the request touches, and one phase (the part that works on its own) is enough unless the request is large. If a finished ledger is still in `docs/mod/`, run `python -B .tools/check.py gate --archive` first: it moves the finished ledger and its progress log to `docs/mod/history/`.
- **Art.** Run the style round only when the addition needs a style the mod does not have; otherwise match the existing art.
- **Gate.** The same gate decides when the request is done. Everything else in the mod stays untouched.

## The four files

All of them live in `docs/mod/`, so every session and every client finds them in one place.

| File | What it holds | Reference |
| --- | --- | --- |
| `brief.md` | The one-page creative brief: setting, era and start date, map concept, playable nations, tone, visual style, and the build plan: the playable core and the expansions | `references/creative-brief.md` |
| `canon.md` | The canon policy: what is established, what is proposed, and who may promote a proposal | `references/canon-policy.md` |
| `decisions.md` | Every consultation answer and default, with its origin | `references/mod-consultation.md` |
| `ledger.json` | The machine-readable feature ledger: features, dependencies, acceptance checks, evidence and a `passes` flag set only with evidence | `references/feature-ledger.md` |

`progress.md` sits beside them: a short log each session appends to (what it built, what it verified, what is next).

## Workflow

1. **Inspect.** Read `CLAUDE.md`, the mod's files and any existing `docs/` material. An empty mod is quick. Never ask what the files answer.
2. **Draft the brief.** Fill `references/creative-brief.md` from the request, with a suggested answer for every field the request leaves open. Say which fields are suggestions.
3. **Consult once.** Ask the mod-defining questions of `references/mod-consultation.md` in one grouped message, each with its suggested answer and a one-line reason, then list what you will decide yourself. The user can answer "use your suggestions". Before you end the turn to wait, run `python -B .tools/check.py gate --wait "<one-line summary of the questions>"` when the ledger already exists.
4. **Record.** Write the answers to `docs/mod/decisions.md` (origin `user`, `established` or `agent default`), finish `brief.md`, and write `canon.md` from `references/canon-policy.md`.
5. **Plan the whole mod (or the whole request) in phases.** The brief's build plan aims at the complete mod the idea implies, built in order: a playable core first (the country, its map presence, a focus tree and the first events), then each expansion. The mod is playable after every phase, and nothing is cut: an expansion is the next part of the same mod, never a later maybe. Shrinking the plan needs the user's approval.
6. **Agree the art style early.** Make the ledger's first art feature the style round: a few pictures in the brief's style (a flag, a portrait, an icon), shown to the user once with `gate --wait`. Every feature that needs art depends on it, and after it each feature makes its own art.
7. **Write the ledger.** Break the scope into features with `references/feature-ledger.md`: one row per buildable unit that covers every surface of `scope.surfaces`, each in its `phase`, with dependencies in build order, acceptance criteria, machine checks where a file or count proves part of it, and `passes: false`. Set `state` to `building` once the user has agreed the plan, or once you applied the suggestions because the user said to work without questions.
8. **Build, one feature at a time.** Follow the session routine. For each feature open the owning skill (`hoi4-map-states`, `hoi4-focus-trees`, `hoi4-events`, `hoi4-decisions-missions`, `hoi4-characters-leaders`, `hoi4-imagegen` and the others in `CLAUDE.md`), write a feature spec with `hoi4-feature-planning` when the feature needs design depth, implement it completely, run its checks, and only then set `passes: true` with the evidence paths.
9. **Finish at the gate.** `python -B .tools/check.py gate` passes only when every feature has passed with evidence or carries a recorded true blocker, no placeholder is left, and the static checks are clean. Then write the completion report that `CLAUDE.md` section 5 requires, set `state` to `complete`, and lead the report with what the user must do (for example enable the mod in the launcher).

## Session routine

Every session, a resumed one and a new one after a context reset alike, starts the same way. In Claude Code the `SessionStart` hook prints this routine with the next feature; other clients run `python -B .tools/check.py gate --next`.

1. Read `docs/mod/progress.md`, the ledger, `brief.md` and `canon.md`.
2. Run the baseline: `python -B .tools/check.py quick` (and `python -B .tools/check.py gate`). Fix a regression before new work.
3. Take the next feature the gate names: the first open, unblocked feature of the earliest unfinished phase whose dependencies have passed.
4. Build it, verify it, record `evidence` and set `passes`, append to `progress.md`, and commit the feature on its own.
5. Run `python -B .tools/check.py gate` and continue with the next feature.

One feature per step keeps each change reviewable and lets a new context pick up from the files alone. A subagent may research, audit or produce assets for a feature; the main agent still owns the feature's implementation, its evidence and its `passes` flag.

## The completion gate

`python -B .tools/check.py gate` is the same check in every client. In Claude Code the project's `Stop` hook runs it and keeps the session working while the ledger has open features. It lets a stop through when:

- every feature has passed with evidence or has a recorded `blocker`, and the checks are clean;
- you are waiting for the user: run `python -B .tools/check.py gate --wait "<question>"` before you ask; the user's reply clears it;
- the user told you to stop: run `python -B .tools/check.py gate --pause "<their words>"`, and `--resume` when they return;
- its cap is reached: three blocks in a row with no change to the files, or 30 in one session.

A blocker is only a true blocker: a decision, asset or approval only the user can give, a credential, money, access, an in-game check that cannot run here, or a missing tool. Difficulty, length and an unfinished design are not blockers, and a reduced version is never recorded as passed (`CLAUDE.md` section 5). A missing picture, icon or portrait is open work, not a blocker: make it with `hoi4-imagegen` in the agreed style. While the user looks at a picture round or answers a question, use `gate --wait`, not a blocker.

## Rules

- `passes` changes to true only after the feature's acceptance criteria are met and its evidence files exist: check output, a spec section, a render, a log, a report. Never edit `acceptance` or remove a feature to make the gate pass; that needs the user's approval and a line in `decisions.md`.
- Keep established material apart from proposals as `canon.md` says. Write player-facing text only from established canon or from proposals the brief allows the agent to settle.
- Record every default you apply in `decisions.md` and list it in the final report.
- Do not stop to ask routine questions. After the consultation, ask again only at the hard gates of `hoi4-feature-planning/references/consultation-questions.md`.

## References

- `references/creative-brief.md`: the brief template, the build plan in phases and the autonomy dial.
- `references/mod-consultation.md`: the mod-defining questions with suggested answers, and how to record them.
- `references/canon-policy.md`: established and proposed material, and how a proposal is promoted.
- `references/feature-ledger.md`: the ledger format (including `scope.kind` and `scope.request` for a big request in an existing mod), the feature catalogue by surface, machine checks and blockers.
