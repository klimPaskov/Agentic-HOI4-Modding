---
name: hoi4-mtth
description: Define and use HOI4 MTTH variables safely (base/modifiers, file-scoped constants, and mtth:entry usage in set_variable/set_temp_variable) with guidance for minimizing ai_will_do clutter.
---

# HOI4 MTTH Variables

## Scope and References

Use MTTH variables to compute a value from a base plus modifiers, then inject that value into other logic.

Read first to see how Chaos Redux already implements them:
- `/home/klim/projects/chaos_redux/common/mtth/chaosx_mtth_variables.txt`

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
