# PDX stream parser fixture provenance

The hierarchy, first three position values, triangle winding, final skeleton `headfront` transform and complete muzzle locator fields were transcribed from Alien Infantry V13 native io_pdx_mesh 0.91.0 text export `docs/assets/016_brilliant_scientist/models_3d/alien_infantry/export/v13_firearm_preset_locator_closure_20260904/alien_infantry.txt`, SHA256 `477FEE2694AC4784E7DBB94D2F50669634ADD40D1C729CD8E3F38BE0F06A9874`.
The fixture intentionally reduces positions/indices to one triangle and repeats it as a second material-backed mesh stream, updating counts consistently.
Skin weights are small illustrative values; the real skeleton uses `tx`, and the extra nested skeleton `p` in the regression test is an explicitly synthetic namespace-collision case.
The real final locator `p` reproduces the original overwrite bug without any synthetic field.
The actual full 53 MB native export is separately measured in the Alien repair receipt; this reduced fixture is not production acceptance evidence.
