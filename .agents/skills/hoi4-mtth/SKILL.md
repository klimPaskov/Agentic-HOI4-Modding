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

Route every MTTH timing or MTTH-backed AI-weight audit through `hoi4_ai_probability_auditor`. Establish named baseline scenarios before any patch with `hoi4.probability_inspect`, `hoi4.probability_evaluate`, and `hoi4.probability_sweep` as appropriate. The gameplay owner chooses the intended timing and applies the source patch; the auditor remains read-only. After the patch, require `hoi4.probability_compare` against the same named scenarios. Use `hoi4.probability_simulate` only for declared uncertain inputs and `hoi4.probability_render` for timing-survival, sensitivity, comparison, and unresolved views when visual evidence is clearer. Supply scheduled state changes when conditions vary across the horizon. Accept cumulative timing only from the verified game-version MTTH adapter, and keep exact, bounded, sampled, and unresolved results distinct.
