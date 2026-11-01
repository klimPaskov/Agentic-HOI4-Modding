# Military industrial organisations and special projects

Engine facts for the two production systems that sit next to equipment. Read the installed `_documentation.md` files in `common/military_industrial_organization/organizations/`, `policies/` and `ai_bonus_weights/`, and the `documentation.md` files under `common/special_projects/`, first; these notes record traps those files and vanilla script show.

## Military industrial organisations

- Vanilla MIO archetypes carry `allowed = { always = no }` (23 of 30), so a derived MIO that uses `include` must write its own `allowed`. [vanilla-confirmed 1.19.3]
- Negative values of `production_cost_factor`, `production_resource_need_factor` and `production_resource_penalty_factor` are savings (83 of 93 vanilla uses). [vanilla-confirmed 1.19.4.1]
- Every bonus a MIO trait uses needs an entry in the `default` block of `ai_bonus_weights.txt`, or the game logs an error. [docs]
- `naval_supremacy_factor` does not exist; the stat is `naval_dominance_factor`, and `organization_bonus` is `organization_modifier`. [docs]
- `ENABLE_TASK_CAPACITY` is false in vanilla [vanilla-confirmed 1.19.4.1]; task capacity may then do nothing. [unverified]
- `set_mio_funds` does not exist in 1.19.3. [docs]

## Special projects

- Use the `documentation.md` files in `projects/`, `prototype_rewards/` and `specialization/`. The folder's `special_projects_documentation.md` describes keys that no vanilla file uses. [vanilla-confirmed 1.19.4.1]
- The scientist trait example modifier `special_project_prototype_speed_factor` does not exist; use `special_project_speed_factor`. [docs]
- Prototype reward thresholds run from 0 to 100. [docs] [vanilla-confirmed 1.19.4.1]
- A project's `allowed` runs once at startup and accepts only `tag`, `original_tag` and `has_dlc`. [docs] [vanilla-confirmed 1.19.4.1]
- In `available` and `visible`, country triggers go inside `FROM = { }`. [docs] [vanilla-confirmed 1.19.4.1]
- Constants are written bare in `complexity`, `prototype_time` and `add_breakthrough_progress.value`, but need `constant:` in variable positions. [vanilla-confirmed 1.19.4.1]
- `complete_special_project` skips facility-state and scientist effects and ignores parents. [docs]
- Special projects have `set_project_flag` and `has_project_flag`. [docs]
- `modify_mproject_flag` does not exist, keep the game's own spelling `prototyp_reward_option`, and `modify_facility_flag` is a documentation typo. [docs]
