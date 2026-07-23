---
name: hoi4-mtth
description: Define and use HOI4 MTTH variables safely (base/modifiers, file-scoped constants, and mtth:entry usage in set_variable/set_temp_variable) with guidance for minimizing ai_will_do clutter.
---

# HOI4 MTTH Variables

## Scope and References

Use MTTH variables to compute a value from a base plus modifiers, then inject that value into other logic.

Read existing repository MTTH files first if the mod already has them. Otherwise use `common/mtth/*.txt` as the standard location.

## Defining an MTTH entry

Create entries in `common/mtth/*.txt`:

```
example_mtth_value = {
	base = 50

	modifier = {
		factor = 0.8
		tag = GER
	}
	modifier = {
		add = 25
		has_war = yes
	}
}
```

Notes:
- `base` is the starting value.
- `modifier` blocks use `factor` or `add` and standard triggers.

## Using an MTTH entry

Vanilla example pattern:

```
set_variable = { my_value = mtth:example_mtth_value }
```

Typical usage:
- `set_variable` or `set_temp_variable` to store the computed MTTH value.
- Use the variable later (`add = temp`, `check_variable = { temp > 1 }`, etc.).

## AI weights with MTTH

To reduce `ai_will_do` clutter, compute the full weight in MTTH and inject it:

```
ai_will_do = {
	factor = 0
	modifier = {
		set_temp_variable = { temp = mtth:chem_ai_weight }
		add = temp
	}
}
```

## Scenario analysis

Use `hoi4.probability_inspect` to identify the MTTH entry, modifiers, helpers, and scenario inputs before evaluating timing. Use `hoi4.probability_evaluate` for named world states, `hoi4.probability_sweep` for thresholds and timing reversals, `hoi4.probability_simulate` for declared uncertain inputs, and `hoi4.probability_compare` after a patch. Use `hoi4.probability_render` for timing-survival, sensitivity, comparison, and unresolved views when visual evidence is clearer. Supply scheduled state changes when conditions vary across the horizon. Accept cumulative timing only from the verified game-version MTTH adapter, and keep exact, bounded, sampled, and unresolved results distinct. The analyzer supplies evidence and never chooses the intended timing or writes source.
