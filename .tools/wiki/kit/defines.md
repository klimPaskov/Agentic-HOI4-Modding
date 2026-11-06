# Defines

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="104682" sources="common/defines/ localisation/english/core_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** The tables on this page date from an older build. Checked against: all three files in `common/defines/` (`00_defines.lua`, `00_graphics.lua`, `01_career_profile.lua`: 4504 defines in 39 categories), parsed with a script and compared name by name and value by value with this page's 37 category tables. They lack 617 defines, list 127 values that changed and carry 58 names that no longer exist.
The missing defines, the changed values, the removed names and the two new categories `NFactions` and `NDoctrines` are on the kit page [Defines additions](<defines_additions.md>); the wiki text here is left unchanged, so a refresh can replace it without touching kit text. Re-check that page when this page's wiki revision changes.
Gaps left: meanings come from the Lua comments or, where there is none, from the define name. The "Usage" and "Developer comment" cells of existing rows were not rewritten. Which defines the engine still reads was not tested.
**1.19.4.1 re-check (2026-11-01).** The same script compared the 1.19.3 define set with the 1.19.4.1 files: 4523 defines in the same 39 categories, 19 new, none removed, and one changed value (`NMarket.REQUEST_AUTOMATION_AUTO_ACCEPT_PURCHASE_DEFAULT` is now `true`, while this page's table shows `false`). They are on [Defines additions](<defines_additions.md#Changes_1_19_4_1>). This page holds no kit statement besides this review, and its wiki text is unchanged.
<!-- kit:end id="review" -->

<!-- kit:begin id="defines-outdated-tables" at="top" -->
The tables on this page are out of date. Build 1.19.4.1 has 4523 defines in 39 categories. These tables lack 617 defines, show 127 values that have since changed, and list 58 names that no longer exist. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`

The missing defines, the changed values, the removed names and the two new categories `NFactions` and `NDoctrines` are on [Defines additions](<defines_additions.md>). Check that page before relying on a value from the tables below.

`NDefines.NMarket.REQUEST_AUTOMATION_AUTO_ACCEPT_PURCHASE_DEFAULT` is `true`, not `false` as the table below shows. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`
<!-- kit:end id="defines-outdated-tables" -->
