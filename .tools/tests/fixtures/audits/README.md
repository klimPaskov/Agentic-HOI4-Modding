# Audit fixtures

`mod/` is a tiny mod that both audits accept without an error, and `game/` is a tiny stand-in for the installed game that `HOI4_GAME_DIR` points at during the tests.
`.tools/tests/test_audits.py` copies `mod/` into a temporary folder and adds one defect per case, so each error rule has a valid and an invalid case.
The 3D model registration cases in `test_audits.py` add a registration of their own to the copy (text files plus a mesh built in memory) and read the game stand-in's `gfx/entities/vanilla_models.*` and `dlc/dlc999_fixture/` definitions as the installed game and one of its DLC packages.
