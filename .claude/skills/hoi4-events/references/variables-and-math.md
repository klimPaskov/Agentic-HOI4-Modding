# Variables, math and data structures

Engine facts for script variables, arrays, loops and math that apply to events, decisions, focuses and scripted GUI alike. Read the offline Data structures page and the installed `documentation/` files first; these notes record traps they and vanilla script show.

- A math expression that fails to parse silently becomes 0.0. [docs]
- A `hidden_trigger` whose temp-variable side effects must run needs `tooltip_evaluation = eval`. [docs] [vanilla-confirmed 1.19.3]
- The documented loop variable defaults disagree (`any_of` uses value and index, `all_of` uses v and i), so always name the loop variables explicitly. [docs]
- The dynamic variable is `air_intel`; `airforce_intel` is only an `add_intel` key. [docs]
- The plain `get_highest_scored_country` writes persistent variables, and the documentation describes the temp and non-temp scorers the wrong way round. [vanilla-confirmed 1.19.4.1]
- `lerp = yes` in vanilla is a Sweden scripted effect; use the native `lerp` math function. [vanilla-confirmed 1.19.4.1]
