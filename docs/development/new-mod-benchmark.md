# New-mod benchmark

`scripts/benchmark_new_mod.py` measures the whole new-mod flow (`hoi4-new-mod`, `check.py gate`) from one-line prompts. Each prompt runs in its own copy of a fresh mod that HOI4 Mod Setup made, with a scripted user who answers the consultation with "Use your suggestions." and then says "Continue building." until the gate passes, the ledger is paused or the session limit is reached. Each session resumes the last one, so the ledger's session routine is exercised too.

The verdict comes from files and checks, never from the agent's report: the `docs/mod/` files, the ledger, `check.py gate`, `check.py quick`, the Git log and, with `--game-check`, an in-game check of the result (for example a smoke test on a test copy of the game). The runner writes `report.json` and `report.md`.

```powershell
python scripts/benchmark_new_mod.py --template <fresh mod folder> --prompts <prompts.json> --out <run folder> --model sonnet
python scripts/benchmark_new_mod.py --report <run folder>
```

- Use several prompts and keep them outside the repository, so the kit is not tuned to them. `scripts/benchmark_prompts.example.json` shows the format.
- The default client is `claude -p` with permission prompts skipped, so the runner only ever works on its own copies. `--client` takes another command template.
- Fix the kit from each run's failures as steps, rules or checks a small model can follow, and run the benchmark again.
