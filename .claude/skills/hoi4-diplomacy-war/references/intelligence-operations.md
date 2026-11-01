# Intelligence agencies and operations

Engine facts for operations and agency upgrades. Read the installed documentation under `common/operations/` and `common/intelligence_agency_upgrades/` first; these notes record traps the documentation and vanilla script show.

- An operation reacts only to modifiers named in its own `cost_modifiers`, `outcome_modifiers` and `risk_modifiers` lists. [unverified] (vanilla lists them, but no file says unlisted ones are ignored)
- `awarded_tokens` is display only, so an outcome must call `add_operation_token` itself. [docs]
- The key is `outcome_extra_execute` (the documentation writes `outcome_execute_extra`), and `outcome_extra_chance` is a fraction from 0.25 to 0.5, not 50. [vanilla-confirmed 1.19.4.1]
- `operation_targeted_sabotage_industry` and `operation_targeted_sabotage_infrastructure` swap their risk and outcome modifier lists in vanilla, so do not copy them as templates. [vanilla-confirmed 1.19.3]
- Agency upgrade frames are `_unavailable`, `_current` and `_completed` (the documentation writes `_available`), and `upgrade_intelligence_agency` needs `NOT = { has_done_agency_upgrade = X }`. [vanilla-confirmed 1.19.4.1]
