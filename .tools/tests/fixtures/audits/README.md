# Audit fixtures

`mod/` is a tiny mod that both audits accept without an error, and `game/` is a tiny stand-in for the installed game that `HOI4_GAME_DIR` points at during the tests.
`.tools/tests/test_audits.py` copies `mod/` into a temporary folder and adds one defect per case, so each error rule has a valid and an invalid case.
