# Table of contents

- [Overrides](#overrides)
- [NGame](#ngame)
- [NGeography](#ngeography)
- [NDiplomacy](#ndiplomacy)
- [NCountry](#ncountry)
- [NResistance](#nresistance)
- [NProduction](#nproduction)
- [NMarket](#nmarket)
- [NTechnology](#ntechnology)
- [NPolitics](#npolitics)
- [NBuildings](#nbuildings)
- [NDeployment](#ndeployment)
- [NMilitary](#nmilitary)
- [NAir](#nair)
- [NNavy](#nnavy)
- [NRailwayGun](#nrailwaygun)
- [NTrade](#ntrade)
- [NAI](#nai)
- [NFocus](#nfocus)
- [NOperatives](#noperatives)
- [NIntel](#nintel)
- [NCharacter](#ncharacter)
- [NSupply](#nsupply)
- [NAITheatre](#naitheatre)
- [NIndustrialOrganisation](#nindustrialorganisation)
- [NProject](#nproject)
- [NRaids](#nraids)
- [NWiki](#nwiki)
- [NMapMode](#nmapmode)
- [NMapIcons](#nmapicons)
- [NAirGfx](#nairgfx)
- [NGraphics](#ngraphics)
- [NInterface](#ninterface)
- [NFrontend](#nfrontend)
- [NSound](#nsound)
- [NFriendGUI](#nfriendgui)
- [NCareerProfile](#ncareerprofile)
- [NCareerProfileGUI](#ncareerprofilegui)


---

Defines are exposed constants used by the game to control almost every aspect of it. They allow modders to influence systems that do not have a direct script component.

Defines are defined in /Hearts of Iron IV/common/defines/\*.lua files.

## Overrides

As defines are Lua code rather than a PDXscript-interpreted file, any Lua code can go in there, however modules allowing to go out of this directory are not available. As a consequence of this, **there is no need to copy the entire file to edit it**. Defines, including graphical defines, are merely a Lua-contained array, and it is possible to modify a single member of the array in Lua using, for example, `NDefines.NGame.START_DATE = "1936.1.2.12"`. Each of these lines is contained on a separate line and **there are no commas separating them**, such as the following:

```text
NDefines
.
NGame
.
START_DATE
 
=
 
"1936.1.2.12"
 
-- An unnecessary comma will result in a game crash upon launching.

NDefines
.
NGraphics
.
COUNTRY_FLAG_TEX_MAX_SIZE
 
=
 
2048
 
-- They are present in the base game defines file due to the fact that NDefines is one single large array, and when defining an array with members, the members are separated with commas. However, commands are not separated with commas.
```

This goes into a separate file set to be evaluated after the base game defines, which is sorted by filenames using the [ASCII character IDs](http://en.wikipedia.org/wiki/ASCII#Printable_characters). Since 0 is among the earliest characters by ID – placed before letters, other numbers, and underscores – almost any filename can work.   
In the base game files, the graphical defines are set to be merged into NDefines in the last line of the base game file. However, since Lua does not create copies of tables by default, the base game's NDefines contains pointers to the actual elements, which are contained within NDefines\_Graphics regardless. For this reason, modifying either NDefines or NDefines\_Graphics works for changing graphical defines.  
A mod should **never** contain the 00\_defines.lua and 00\_graphics.lua files within of itself: these files are commonly changed even in minor game updates, and having a define missing from a file results in the mod being unstable, potentially having a crash on startup.

## NGame

- **START_DATE**
  - Default: "1936.1.1.12"
  - Usage: Default start date, base for some durations (e.g. license costs, AI construction strategy)

- **END_DATE**
  - Default: "1949.1.1.1"
  - Usage: Decides on the date when the final scoreboard is shown, unless a sufficiently major war is ongoing

- **MAP_SCALE_PIXEL_TO_KM**
  - Default: 7.114
  - Developer comment: Yes, we did the math
  - Usage: Translates the pixel distances from world map bitmaps into distances in-game, such as for unit speed

- **SAVE_VERSION**
  - Default: 25
  - Developer comment: 1.16.0 (Countenance)
  - Usage: Compatibility version for save files

- **CHECKSUM_SALT**
  - Default: "zwOdv5d9wm9uDSOT"
  - Developer comment: Data to modify generated checksum when game binaries have changed but not any content files.

- **LAG_DAYS_FOR_LOWER_SPEED**
  - Default: 10
  - Developer comment: Days of client lag for decrease of gamespeed

- **LAG_DAYS_FOR_PAUSE**
  - Default: 25
  - Developer comment: Days of client lag for pause of gamespeed.

- **GAME_SPEED_SECONDS**
  - Default: { 2.0, 0.5, 0.2, 0.1, 0.0 }
  - Developer comment: game speeds for each level. Must be 5 entries with last one 0 for unbound
  - Usage: Useful for multiplayer mods

- **MAJOR_PARTICIPANTS_FOR_MAJOR_WAR**
  - Default: 3
  - Developer comment: Minimum number of major countries involved in a war to consider it major enough to not end the game even though the enddate has been reached.

- **TRADE_ROUTE_RECALCULATE_FREQUENCY_DAYS**
  - Default: 30
  - Developer comment: Max recalculation time for all trade routes (0 means we do not recalucate prediodically trade routes)

- **COMBAT_LOG_MAX_MONTHS**
  - Default: 12
  - Usage: Non-air combat log data will be pruned after this duration

- **MESSAGE_TIMEOUT_DAYS**
  - Default: 60
  - Developer comment: Useful if running the handsoff game. The popup messages that doesn't require the player respond will automatically hide after some timeout.

- **INFO_MESSAGE_TIMEOUT_DAYS**
  - Default: 3
  - Developer comment: Same but for unimportant messages.

- **AIR_LOG_TIMEOUT_HOURS**
  - Default: 24
  - Developer comment: Data storring data
  - Usage: Air combat log data will be pruned after this duration

- **EVENT_TIMEOUT_DEFAULT**
  - Default: 13
  - Developer comment: Default days before an event times out if not scripted

- **MISSION_REMOVE_FROM_INTERFACE_DEFAULT**
  - Default: 13
  - Developer comment: Default days before a mission is removed from the interface after having failed or completed

- **DECISION_ALERT_TIMEOUT_DAYS**
  - Default: 30
  - Developer comment: Days left when player will be alerted about timing out events or decisions

- **FUEL_RESOURCE**
  - Default: "oil"
  - Developer comment: resource that will give country fuel
  - Usage:
    ```text
    If changed, localisation may need to be updated to make the icon show the new resource. The default values that can be
    replaced
    are
    FUEL_DAILY_GAIN_FROM_OIL:0 "From $OIL$£resources_strip|1 : $NUM|H$"
    and
    FUEL_DAILY_GAIN_OIL_ONLY:0 "Daily Gain: $NUM|H$ (from $OIL|H$£resources_strip|1 )"
    .
    £resources_strip|1
    is a
    text icon
    which may need to be updated, and
    $OIL$
    shouldn't be changed.
    ```

- **MAX_EFFECT_ITERATION**
  - Default: 1000
  - Developer comment: maximum allowed iteration for loop effects

- **MAX_SCRIPTED_LOC_RECURSION**
  - Default: 30
  - Developer comment: max recursion for scripted localizations

- **HANDS_OFF_START_TAG**
  - Default: "HAI"
  - Developer comment: tag for player country for -hands_off runs. use an existing tag that is less likely to affect the game

- **ALERT_SFX_COOLDOWN_DAYS**
  - Default: 14
  - Developer comment: After playing an alert sound, don't play the same sound for XXX days, even if it fires again.

- **MUSIC_PLAYER_RECENTLY_PLAYED_SIZE**
  - Default: 10
  - Developer comment: The music player keeps track of recently played music to try and avoid playing the same songs too often. This determines the max number of songs in the recently played list.

## NGeography

- **MEDITERRANEAN_SEA_REGIONS**
  - Default: { 29, 68, 69, 168, 169, 202 }
  - Developer comment: The sea regions that are considered as part of the Mediterranean sea

## NDiplomacy

- **DIPLOMACY_REQUEST_EXPIRY_DAYS**
  - Default: 30

- **BASE_SURRENDER_LEVEL**
  - Default: 1.0
  - Developer comment: Surrender when level reached. valid 0-1

- **MAX_TRUST_VALUE**
  - Default: 100
  - Developer comment: Max trust value cap.

- **MIN_TRUST_VALUE**
  - Default: -100
  - Developer comment: Min trust value cap.

- **MAX_OPINION_VALUE**
  - Default: 100
  - Developer comment: Max opinion value cap.

- **MIN_OPINION_VALUE**
  - Default: -100
  - Developer comment: Min opinion value cap.

- **BASE_TRUCE_PERIOD**
  - Default: 180
  - Developer comment: Base truce period in days.

- **TRUCE_PERIOD_AFTER_KICKING_FROM_FACTION**
  - Default: 60
  - Developer comment: Truce period after kicking someone from faction in days.

- **NUM_DAYS_TO_ENABLE_KICKING_NEW_MEMBERS_OF_FACTION**
  - Default: 90
  - Developer comment: Number of days before being able to kick a new member of faction

- **NUM_DAYS_TO_ENABLE_REINVITE_KICKED_NATIONS**
  - Default: 90
  - Developer comment: Number of days before being able to re invite a kicked nation to your faction

- **BASE_NEGATIVE_OPINION_AFTER_BEING_KICKED**
  - Default: 20
  - Developer comment: Negative opinion that will be received after kicking a nation

- **DECAY_RATE_OF_NEGATIVE_OPINION_AFTER_BEING_KICKED**
  - Default: 1
  - Developer comment: Weekly decay rate of the negative opinion

- **TRUCE_BREAK_COST_PP**
  - Default: 200
  - Developer comment: Base cost in PP of breaking a truce by joining a war or accepting a call to war ( you cannot declare war yourself until the truce if up ), this is then multiplied by the time left on the truce ( so once half the truce is up it only cost 50% of this )

- **BASE_PEACE_PUPPET_FACTOR**
  - Default: 100
  - Developer comment: Base factor for puppet in %.

- **BASE_PEACE_LIBERATE_FACTOR**
  - Default: 100
  - Developer comment: Base factor for liberate in %.

- **BASE_PEACE_TAKE_UNCONTROLLED_STATE_FACTOR**
  - Default: 10.0
  - Developer comment: Base factor for taking state you do not control

- **BASE_PEACE_TAKE_FACTION_CONTROLLED_STATE_FACTOR**
  - Default: 0.5
  - Developer comment: Base factor for taking state you do not control, but someone in faction does

- **BASE_PEACE_FORCE_GOVERNMENT_COST**
  - Default: 100
  - Developer comment: Base cost for forcing a country to change government.

- **PEACE_COST_FACTOR_CONTESTED_MAX**
  - Default: 15
  - Developer comment:
    ```text
    In peace conference, cost is factored based on how many times the state has been contested and for how long it has been uncontested (for everyone else)
    To prevent overflows due to the exponential increase, cap the contested factor to this
    ```

- **PEACE_COST_FACTOR_UNCONTESTED_MAX**
  - Default: 15
  - Developer comment: To prevent overflows due to the exponential increase, cap the uncontested factor to this

- **PEACE_COST_FACTOR_CONTESTED_BID**
  - Default: 1.20
  - Developer comment: Cost factor for each contested bid on the state.

- **PEACE_COST_FACTOR_UNCONTESTED_BID_MIN**
  - Default: 1.15
  - Developer comment: Minimum cost factor for each turn a bid has been uncontested on the state.

- **PEACE_COST_FACTOR_UNCONTESTED_BID_MAX**
  - Default: 1.60
  - Developer comment: Maximum cost factor for each turn a bid has been uncontested on the state.

- **PEACE_COST_FACTOR_UNCONTESTED_BID_STEP**
  - Default: 0.15
  - Developer comment: Uncontested cost factor will increase by this much each turn.

- **PEACE_COST_FACTOR_CAPITAL_SHIP_IC**
  - Default: 0.005
  - Developer comment: In peace conference, cost for taking one capital ship per IC

- **PEACE_COST_FACTOR_SCREENING_SHIP_IC**
  - Default: 0.005
  - Developer comment: In peace conference, cost for taking a part of the screening ships per IC

- **PEACE_INCREASE_COST_FACTOR_PER_MISSING_PERCENT_FOR_CAPITULATION**
  - Default: 0.0012
  - Developer comment: increase factor if loser has not capitulated, for every percent between surrender level and BASE_SURRENDER_LEVEL

- **PEACE_COST_FACTOR_COMPLIANCE_STEPS**
  - Default:
    ```text
    { 0, 1.0,
    30, 0.9,
    70, 0.8 }
    ```
  - Developer comment:
    ```text
    peace action taker has a discount if they occupy the state depending on compliance
    it's a table where first value is the compliance level, and the second the factor
    between 0%  and 30% compliance, factor is 1.0
    between 30% and 70%
    above 70%
    ```

- **PEACE_COST_FACTOR_STACK_DEMILITARIZED_ZONE**
  - Default: 0.25
  - Developer comment: In peace conference, adding a stackable to a peace action, increment the cost by a percentage

- **PEACE_COST_FACTOR_STACK_WAR_REPARATION**
  - Default: 0.25

- **PEACE_COST_FACTOR_STACK_RESOURCE_RIGHTS**
  - Default: 0.25

- **PEACE_COST_FACTOR_STACK_DISMANTLE_INDUSTRY**
  - Default: 0.25

- **PEACE_TIMED_EFFECT_LENGTH_DEMILITARIZED_ZONE**
  - Default: 1825
  - Developer comment:
    ```text
    peace conference can set timed effect, set length in days
    5 years
    ```

- **PEACE_TIMED_EFFECT_LENGTH_WAR_REPARATION**
  - Default: 1825

- **PEACE_TIMED_EFFECT_LENGTH_RESOURCE_RIGHTS**
  - Default: 1825

- **PEACE_TIMED_EFFECT_RATIO_CIVILIAN_FACTORY_WAR_REPARATION**
  - Default: 0.5
  - Developer comment: ratio of civilian factories taken via stackable war reparation

- **INFLUENCE_NEUTRAL_DIST_CAPITAL**
  - Default: 30.0
  - Developer comment:
    ```text
    The Influence cost modifier is basically the inverse of distance. Nearby states are cheaper, and far-away states are more expensive.
    We basically do a two-segment lerp:
    if distance is between [0, NEUTRAL_DIST], we lerp the cost modifier between [MIN_DIST_COST_MODIFIER, 1.0]
    if distance is between [NEUTRAL_DIST, MAX_DIST], we lerp the cost modifier between [1.0, MAX_DIST_COST_MODIFIER]
    The below values represent (pixel distance / INFLUENCE_DISTANCE_DIVISOR)
    distance to capital that results in a cost modifier of 1.0
    ```

- **INFLUENCE_MAX_DIST_CAPITAL**
  - Default: 45.0
  - Developer comment: distance to capital that results in a cost modifier of INFLUENCE_MAX_DIST_COST_MODIFIER

- **INFLUENCE_NEUTRAL_DIST_CORE**
  - Default: 6.0
  - Developer comment: distance to nearest core state that results in a cost modifier of 1.0

- **INFLUENCE_MAX_DIST_CORE**
  - Default: 13.0
  - Developer comment: distance to nearest core state that results in a cost modifier of INFLUENCE_MAX_DIST_COST_MODIFIER

- **INFLUENCE_NEUTRAL_DIST_CONTROLLED**
  - Default: 14.0
  - Developer comment: distance to nearest controlled state that results in a cost modifier of 1.0

- **INFLUENCE_MAX_DIST_CONTROLLED**
  - Default: 20.0
  - Developer comment: distance to nearest controlled state that results in a cost modifier of INFLUENCE_MAX_DIST_COST_MODIFIER

- **INFLUENCE_MIN_DIST_COST_MODIFIER**
  - Default: 0.70
  - Developer comment: Cost modifier at min (zero) distance

- **INFLUENCE_MAX_DIST_COST_MODIFIER**
  - Default: 1.00
  - Developer comment: Cost modifier at max distance

- **INFLUENCE_RATIO_CAPITAL**
  - Default: 0.05
  - Developer comment: Ratio of influence based on distance to capital

- **INFLUENCE_RATIO_CORE**
  - Default: 0.45
  - Developer comment: Ratio of influence based on distance to nearest core territory

- **INFLUENCE_RATIO_CONTROLLED**
  - Default: 0.5
  - Developer comment: Ratio of influence based on distance to neared controlled territory (including uncontested peace conference bids)

- **INFLUENCE_DISTANCE_DIVISOR**
  - Default: 22.0
  - Developer comment: Divide pixel distance with this when determining distance to capital / core / controlled states. Just an arbitrary way of scaling the distance numbers.

- **INFLUENCE_PER_ADJACENCY**
  - Default: 0.05
  - Developer comment: How much influence to add per uncontested adjacent state in the PC (blob, don't snake)

- **INFLUENCE_MAJOR_FACTOR**
  - Default: 1.0
  - Developer comment: How much influence discount an AI major will get (inverse)

- **INFLUENCE_MINOR_FACTOR**
  - Default: 1.0
  - Developer comment: How much influence discount an AI minor will get (inverse)

- **PEACE_TRIGGER_AI_MAX_INFLUENCE_VALUE**
  - Default: 0.99
  - Developer comment: Max influence value for pc_is_state_outside_influence_for_winner trigger

- **BASE_IMPROVE_RELATION_COST**
  - Default: 10
  - Developer comment: Political power cost to initiate relation improvement

- **BASE_IMPROVE_RELATION_SAME_IDEOLOGY_GROUP_MAINTAIN_COST**
  - Default: 0.2
  - Developer comment: Political power cost each update when boosting relations with nation of same ideology

- **BASE_IMPROVE_RELATION_DIFFERENT_IDEOLOGY_GROUP_MAINTAIN_COST**
  - Default: 0.4
  - Developer comment: Political power cost each update when boosting relations with nation of different ideology

- **BASE_SEND_ATTACHE_COST**
  - Default: 100
  - Developer comment: Political power cost to send attache

- **BASE_SEND_ATTACHE_CP_COST**
  - Default: 50.0
  - Developer comment: Command Power sent attache usage cost

- **BASE_GENERATE_WARGOAL_DAILY_PP**
  - Default: 0.2
  - Developer comment: Daily pp cost for generation of wargoals

- **WARGOAL_VERSUS_MAJOR_AT_WAR_REDUCTION**
  - Default: -0.75
  - Developer comment: reduction of pp cost for wargoal vs major at war.

- **WARGOAL_WORLD_TENSION_REDUCTION**
  - Default: -0.5
  - Developer comment: Reduction of pp cost for wargoal at 100% world tension, scales linearly

- **WARGOAL_JUSTIFY_TENSION_FROM_PRODUCTION**
  - Default: 30.0
  - Developer comment: Base value scaled by production capacity of country compared to biggest country

- **MIN_WARGOAL_JUSTIFY_COST**
  - Default: 2.0
  - Developer comment: It always takes atleast 10 days to justify a wargoal

- **WARGOAL_PER_JUSTIFY_AND_WAR_COST_FACTOR**
  - Default: 1.5
  - Developer comment: Cost factor per nation at war with or justifying against

- **WARGOAL_THREAT_MAX_TIME_RATIO**
  - Default: 1.0
  - Developer comment: Threat from justifying a wargoal slowly builds up, hitting 100% at this proportion of the way to completion

- **BASE_BOOST_PARTY_POPULARITY_DAILY_PP**
  - Default: 0.25
  - Developer comment: Daily pp cost for boost party popularity

- **BASE_BOOST_PARTY_POPULARITY_DAILY_DRIFT**
  - Default: 0.1
  - Developer comment: Daily amount of popularity that will be added by the activity.

- **BASE_STAGE_COUP_DAILY_PP**
  - Default: 0.5
  - Developer comment: Daily pp cost for staging a coup

- **BASE_STAGE_COUP_TOTAL_COST**
  - Default: 200
  - Developer comment: Equipment consume factor for stage coup.

- **NAP_EXPIRY_MONTHS**
  - Default: 48
  - Developer comment: NAPs expire after this many months

- **NAP_UNBREAKABLE_MONTHS**
  - Default: 12
  - Developer comment: NAPS cannot be broken for this many months

- **NAP_FORCE_BALANCE_RULE_MONTHS**
  - Default: 6
  - Developer comment: The NAP border force balance rule changes with this interval

- **NAP_BREAK_FORCE_BALANCE_1**
  - Default: 2.0
  - Developer comment: 2-1 brigades along the border required to break NAP

- **NAP_BREAK_FORCE_BALANCE_2**
  - Default: 1.0
  - Developer comment: 1-1 brigades along the border required to break NAP

- **NAP_BREAK_FORCE_BALANCE_3**
  - Default: 0.5
  - Developer comment: 1-2 brigades along the border required to break NAP

- **VERY_GOOD_OPINION**
  - Default: 50
  - Developer comment: Threshold for a country that has a very good opinion of you.

- **VERY_BAD_OPINION**
  - Default: -50
  - Developer comment: Threshold for a country that has a very bad opinion of you.

- **DIPLOMACY_HOURS_BETWEEN_REQUESTS**
  - Default: 24
  - Developer comment: How long a country must wait before sending a new diplomatic request.

- **TROOP_FEAR**
  - Default: 1
  - Developer comment: Impact on troops on borders when deciding how willing a nation is to trade

- **FLEET_FEAR**
  - Default: 1
  - Developer comment: Impact on troops on borders when deciding how willing a nation is to trade

- **IC_TO_EQUIPMENT_COUP_RATIO**
  - Default: 0.1
  - Developer comment: Ratio for calculating cost of staging coup

- **VOLUNTEERS_PER_TARGET_PROVINCE**
  - Default: 0.05
  - Developer comment: Each province owned by the target country contributes this amount of volunteers to the limit.

- **VOLUNTEERS_PER_COUNTRY_ARMY**
  - Default: 0.05
  - Developer comment: Each army unit owned by the source country contributes this amount of volunteers to the limit.

- **VOLUNTEERS_RETURN_EQUIPMENT**
  - Default: 0.95
  - Developer comment: Returning volunteers keep this much equipment

- **VOLUNTEERS_TRANSFER_SPEED**
  - Default: 14
  - Developer comment: days to transfer a unit to another nation

- **VOLUNTEERS_DIVISIONS_REQUIRED**
  - Default: 30
  - Developer comment: This many divisons are required for the country to be able to send volunteers.

- **TENSION_STATE_VALUE**
  - Default: 2
  - Developer comment: Tension value gained by annexing one state

- **TENSION_CIVIL_WAR_IMPACT**
  - Default: 0.2
  - Developer comment: civil war multiplier on tension.

- **TENSION_NO_CB_WAR**
  - Default: 10
  - Developer comment: Amount of tension generated by a no-CB wargoal

- **TENSION_CB_WAR**
  - Default: 7
  - Developer comment: Amount of tension generated by a war with a CB

- **TENSION_ANNEX_NO_CLAIM**
  - Default: 2
  - Developer comment: Amount of tension generated by annexing a state you don't have claims on

- **TENSION_ANNEX_CLAIM**
  - Default: 0.5
  - Developer comment: Amount of tension generated by annexing a state you DO have claims on

- **TENSION_ANNEX_CORE**
  - Default: 0
  - Developer comment: Amount of tension generated by annexing a state that is your core

- **TENSION_PUPPET**
  - Default: 1.25
  - Developer comment: Amount of tension generated by puppeting (per state)

- **TENSION_FORCE_GOVERNMENT**
  - Default: 0.75
  - Developer comment: Amount of tension generated by forcing government (per state)

- **TENSION_VOLUNTEER_FORCE_DIVISION**
  - Default: 0.2
  - Developer comment: Amount of tension generated for each sent division

- **TENSION_DECAY_DAILY**
  - Default: 0.005
  - Developer comment: Each day tension decays this much for Threat sources which are no longer relevant. Replaces TENSION_DECAY as of 1.12.0

- **TENSION_SIZE_FACTOR**
  - Default: 1.0
  - Developer comment: All action tension values are multiplied by this value

- **TENSION_TIME_SCALE_START_DATE**
  - Default: "1936.1.1.12"
  - Developer comment: Starting at this date, the tension values will be scaled down (will be equal to 1 before that)

- **TENSION_TIME_SCALE_MONTHLY_FACTOR**
  - Default: -0.005
  - Developer comment: Timed tension scale will be modified by this amount starting with TENSION_TIME_SCALE_START_DATE

- **TENSION_TIME_SCALE_MIN**
  - Default: 0.25
  - Developer comment: Timed tension scale won't decrease under this value

- **TENSION_GUARANTEE**
  - Default: -5

- **TENSION_FACTION_JOIN**
  - Default: 4

- **TENSION_JOIN_ATTACKER**
  - Default: 2
  - Developer comment: scale of the amount of tension added when country joins attacker side

- **TENSION_PEACE_FACTOR**
  - Default: 0.25
  - Developer comment: scale of the amount of tension (from war declaration) reduced when peace is completed.

- **TENSION_LIBERATE**
  - Default: -1
  - Developer comment: Amount of tension generated by liberating a country.

- **TENSION_TAKE_ONE_CAPITAL_SHIP**
  - Default: 0.25
  - Developer comment: Amount of tension generated by 1 take navy peace action

- **TENSION_DEMILITARIZE_ZONE**
  - Default: 0.25
  - Developer comment: Amount of tension generated by stacking demilitarize zone on 1 state, multiplied with the state base threat

- **TENSION_WAR_REPARATION**
  - Default: 0.25
  - Developer comment: Amount of tension generated by stacking war reparation on 1 state, multiplied with the state base threat

- **TENSION_RESOURCE_RIGHTS**
  - Default: 0.25
  - Developer comment: Amount of tension generated by stacking resource rights on 1 state, multiplied with the state base threat

- **TENSION_DISMANTLE_INDUSTRY**
  - Default: 0.25
  - Developer comment: Amount of tension generated by stacking dismantle military industry on 1 state, multiplied with the state base threat

- **TENSION_CAPITULATE**
  - Default: 0.40
  - Developer comment: Scale of the amount of tension created by a countries capitulation.

- **GUARANTEE_COST**
  - Default: 25
  - Developer comment: Scale with the number of already guaranteed countries.

- **REVOKE_GUARANTEE_COST**
  - Default: 25

- **BASE_CONDITIONAL_PEACE_WARESCORE_RATIO**
  - Default: 0.5
  - Developer comment: Warscore ratio needed for the losing side to able to surrender.

- **BASE_CONDITIONAL_PEACE_MONTHS**
  - Default: 3
  - Developer comment: War length must be before a surrender is possible.

- **JOINING_NAP_WAR_PENALTY**
  - Default: 0.2
  - Developer comment: War support penalty for breaking non-breakable NAP

- **BREAKING_GUARANTEE_PENALTY**
  - Default: 0.2
  - Developer comment: War support penalty for breaking guarantee

- **PEACE_SCORE_TRANSFERRED_TO_FACTION_LEADER**
  - Default: 0.1
  - Developer comment:
    ```text
    WARNING ! if you modify the following values, you should update corresponding loc keys in games_rules_l_english.yml
    Part of the peace score transferred from the faction members to the faction leader (if game rule enabled)
    ```

- **PEACE_SCORE_RESET_LOW_SCORE_THRESHOLD**
  - Default: 0.05
  - Developer comment: Winners with less than this ratio of war participation will give all their score to other players

- **PEACE_SCORE_RESET_LOW_SCORE_MINIMUM_FOR_RECEIVER**
  - Default: 0.1
  - Developer comment: Disable the previous, if no winner has at least this ratio of war participation

- **PEACE_SCORE_SCALE_FACTOR**
  - Default: 1.35
  - Developer comment: Losers' total value times this factor becomes the default total peace conference score that is distributed to the winners.

- **PEACE_SCORE_MINOR_BOOST_FRACTION**
  - Default: 0.05
  - Developer comment: Low-scoring winners are boosted by receiving more of their score earlier. This value, multiplied by the total score distributed this turn, is the minimum score they will receive (up until their total allocated score).

- **PEACE_SCORE_DISTRIBUTION**
  - Default: { 0.2, 0.2, 0.2, 0.2, 0.2 }
  - Developer comment:
    ```text
    Example: If 2000 score is distributed to winners this turn and this value is set to 0.05, each winner will receive a minimum of 100 score (clamped by the max score they will receive over the cource of the conference).
    How much of the total peace conference score you get during the first n turns.
    ```

- **PEACE_CONTEST_REFUND_FACTOR**
  - Default: { 1.0, 0.92, 0.84, 0.76 }
  - Developer comment:
    ```text
    More explanation of the peace score distribution above:
    {1.0} would give you all the score on the first turn.
    {0.5, 0.5, 0.5} would give you 50 % of the total score on each of the first three turns (in this case resulting in receiving 150 % of the total score).
    How much of the spent peace conference score that gets refunded in a contest. First element applies for the first round of conflicts, second element for the second round of conflicts, etc. The final element is used for each consecutive turn, so setting that to e.g. 0.7 means you get 70 % of the spent score back for every turn thereafter.
    ```

- **PEACE_PLAY_SOUND_ON_NEW_TURN**
  - Default: true
  - Developer comment: Whether the 'peace_conference_new_turn' audio hook is called or not

- **PEACE_PLAY_NEW_TURN_SOUND_ONLY_IF_NOT_ALREADY_PLAYING**
  - Default: true
  - Developer comment: Whether the 'peace_conference_new_turn' audio hook should play only if not already playing (relevant if players spam-click the pass/submit button)

- **MAX_REMEMBERED_LEASED_IC**
  - Default: 1000
  - Developer comment: Maximum of leased equipment value that is remembered for opinion bonus

- **MAX_OPINION_FOR_LEASED_IC**
  - Default: 30
  - Developer comment: Positive opinion when remembering the MAX_REMEMBERED_LEASED_IC equipment

- **MONTHLY_LEASED_IC_DECAY**
  - Default: 35
  - Developer comment: How much of leased equipment is being "forgot" each month

- **OPINION_PER_VOLUNTEER**
  - Default: 3
  - Developer comment: Opinion bonus per one sent volunteer division

- **MAX_OPINION_FROM_VOLUNTEERS**
  - Default: 30
  - Developer comment: Opinion bonus per one sent volunteer division

- **OPINION_FOR_DEMO_FROM_WT_GENERATION**
  - Default: -2.0
  - Developer comment: How much less do democracies like us if we generate world tension

- **NOT_READY_FOR_WAR_BASE**
  - Default: -50
  - Developer comment: AI should be unwilling to enter accept a call to war if not ready for war against the relevant enemies.

- **FRONT_IS_DANGEROUS**
  - Default: -100
  - Developer comment: AI should be unwilling to enter accept a call to war if front is too dangerous.

- **NOT_READY_FOR_WAR_VAL_PER_DAY_SINCE_CALL**
  - Default: 1
  - Developer comment: Value modifying the not ready base over time.

- **PEACE_ACTION_MAX_COST**
  - Default: 9999
  - Developer comment: Max value for a peace action cost (after all modifiers)

- **RESOURCE_SENT_AUTONOMY_DAILY_BASE**
  - Default: 0.0
  - Developer comment: If puppet provides resources to its master they increasy their autonomy by at least this amount

- **RESOURCE_SENT_AUTONOMY_DAILY_FACTOR**
  - Default: 0.005
  - Developer comment: If puppet provides resources to its master they increasy their autonomy by the resources factored by this

- **WAR_SCORE_AUTONOMY_BASE**
  - Default: 0.0
  - Developer comment: Value added if any war score is contributed by puppet

- **WAR_SCORE_AUTONOMY_FACTOR**
  - Default: 0.6
  - Developer comment: If puppet generates war score it get a boost to independence

- **LL_TO_OVERLORD_AUTONOMY_DAILY_BASE**
  - Default: 0.0
  - Developer comment: If puppet lend leases equipment to overlord of at least same tech level as they have, they gain autonomy

- **LL_TO_OVERLORD_AUTONOMY_DAILY_FACTOR**
  - Default: 0.05
  - Developer comment: If puppet lend leases equipment to overlord of at least same tech level as they have, they gain autonomy

- **LL_TO_PUPPET_AUTONOMY_DAILY_BASE**
  - Default: 0.0
  - Developer comment: If overlord lend leases equipment to puppet of higher tech level as they have, puppet losses autonomy

- **LL_TO_PUPPET_AUTONOMY_DAILY_FACTOR**
  - Default: -0.01
  - Developer comment: If overlord lend leases equipment to puppet of higher tech level as they have, puppet losses autonomy

- **AUTONOMY_FREEDOM_FROM_CAPITULATE**
  - Default: 0.5
  - Developer comment: if overlord capitulate you get this

- **ATTACHE_TO_SUBJECT_EFFECT**
  - Default: -0.05
  - Developer comment: If overlord sent attaches to the subject it losses autonomy

- **ATTACHE_TO_OVERLORD_EFFECT**
  - Default: 0.05
  - Developer comment: If subject sent attaches to the overlord it gains autonomy

- **AUTONOMY_LEVEL_CHANGE_SANCTUARY**
  - Default: 30
  - Developer comment: The number of days post autonomy level has changed where neither side can increase nor decrease the autonomy level.

- **AUTONOMY_LEVEL_CHANGE_PP_COST_BASE**
  - Default: 50.0
  - Developer comment: Base cost of changing level of autonomy

- **AUTONOMY_LEVEL_CHANGE_PP_ANNEX**
  - Default: 300
  - Developer comment: Annexation cost

- **AUTONOMY_LEVEL_CHANGE_PP_FREE**
  - Default: 300
  - Developer comment: Break free cost

- **MAX_SCORE_DIFF_TO_CHANGE_AUTONOMY**
  - Default: 10
  - Developer comment: The max diff between current freedom score and the cap for next or previous level allowed for changing

- **MASTER_BUILD_AUTONOMY_FACTOR**
  - Default: -0.7
  - Developer comment: scales autonomy gain from construction by this

- **VICTORY_POINT_WORTH_FACTOR**
  - Default: 10
  - Developer comment: multiplier when calcualting proince worth (surrender)

- **VICTORY_POINT_WORTH_FACTOR_WARSCORE**
  - Default: 0.2
  - Developer comment: multiplier for each victory points when calculating province worth for warscore

- **PROVINCE_WORTH_FROM_STATE_VALUE_FACTOR_WARSCORE**
  - Default: 0.2
  - Developer comment: multiplier for the average value a province received from state for warscore

- **CAPITAL_CAPITULATE_BONUS_SCORE**
  - Default: 150
  - Developer comment: extra bonus when deciding who to capitulate to (applied to capital holder)

- **CAPITAL_CAPITULATE_BONUS_SCORE_MUL**
  - Default: 1.5
  - Developer comment: extra bonus multiplier when deciding who to capitulate to (applied to capital holder)

- **IDEOLOGY_JOIN_FACTION_MIN_LEVEL**
  - Default: 0.3
  - Developer comment: ideology limit required to join faction

- **JOIN_FACTION_LIMIT_CHANGE_AT_WAR**
  - Default: 0.5
  - Developer comment: if in defensive war this or your modifier is counted as limit to join factions (so if you have 80% join limit this now means you can join at 50%)

- **LICENSE_ACCEPTANCE_OPINION_FACTOR**
  - Default: 0.4
  - Developer comment: Opinion modifier for acceptance of license production requests.

- **LICENSE_ACCEPTANCE_PUPPET_BASE**
  - Default: 15
  - Developer comment: Acceptance modifier for puppets requesting production licenses.

- **LICENSE_ACCEPTANCE_TECH_DIFFERENCE**
  - Default: 2
  - Developer comment: Acceptance modifier for each year of technology difference.

- **LICENSE_ACCEPTANCE_TECH_DIFFERENCE_BASE**
  - Default: 10
  - Developer comment: Acceptance base for tech difference

- **LICENSE_ACCEPTANCE_SAME_FACTION**
  - Default: 20
  - Developer comment: Acceptance modifier for being in the same faction

- **WARGOAL_COST_LEND_LEASE**
  - Default: -0.25
  - Developer comment: cost modifier to wargoaljustification for LL

- **WARGOAL_COST_DOCKING_RIGHTS**
  - Default: -0.2
  - Developer comment: cost modifier to wargoaljustification for dockign rights

- **WARGOAL_COST_VOLUNTEERS**
  - Default: -0.5
  - Developer comment: cost modifier to wargoaljustification for volunteers

- **ASSUME_FACTION_LEADERSHIP_PP_COST**
  - Default: 200
  - Developer comment: Political power cost to assume faction leadership

- **ASSUME_FACTION_LEADERSHIP_MIN_MANPOWER_RATIO**
  - Default: 2
  - Developer comment: The minimum ratio of manpower that a country must have compared to the current leader in order to assume leadership.

- **ASSUME_FACTION_LEADERSHIP_MIN_FACTORY_RATIO**
  - Default: 1.5
  - Developer comment: The minimum ratio of factories that a country must have compared to the current leader in order to assume leadership.

- **ASSUME_FACTION_LEADERSHIP_COOLDOWN_DAYS**
  - Default: 180
  - Developer comment: Number of days after formation of faction or change in leadership before another country is allowed to assume leadership.

- **ASSUME_FACTION_SPYMASTER_COOLDOWN_DAYS**
  - Default: 180
  - Developer comment: Number of days after change of Spy Master before another country is allowed to become Spy Master.

- **FACTION_LEADERSHIP_CHANGE_ALERT_THRESHOLD**
  - Default: 0.8
  - Developer comment: Threshold for showing an alert when a faction member is close to being able to assume leadership of the faction that a player currently leads.

- **FACTION_LEADERSHIP_CHANGE_NOT_SUBJECT_WEIGHT**
  - Default: 2
  - Developer comment: Importance of subject status when determining how close a faction member is to being able to assume leadership.

- **FACTION_LEADERSHIP_CHANGE_NOT_CAPITULATED_WEIGHT**
  - Default: 2
  - Developer comment: Importance of capitulation status when determining how close a faction member is to being able to assume leadership.

- **FACTION_LEADERSHIP_CHANGE_IN_ALL_WARS_WEIGHT**
  - Default: 1
  - Developer comment: Importance not being in all faction leader wars when determining how close a faction member is to being able to assume leadership.

- **FACTION_LEADERSHIP_CHANGE_COOLDOWN_WEIGHT**
  - Default: 1
  - Developer comment: Importance of leadership change cooldown when determining how close a faction member is to being able to assume leadership.

- **FACTION_LEADERSHIP_CHANGE_MANPOWER_WEIGHT**
  - Default: 2
  - Developer comment: Importance of manpower in field when determining how close a faction member is to being able to assume leadership.

- **FACTION_LEADERSHIP_CHANGE_FACTORY_WEIGHT**
  - Default: 2
  - Developer comment: Importance of factory count when determining how close a faction member is to being able to assume leadership.

- **EMBARGO_COST**
  - Default: 100
  - Developer comment: One-time cost

- **REVOKE_EMBARGO_COST**
  - Default: 0
  - Developer comment: Cost to remove an existing embargo

- **EMBARGO_THREAT_THRESHOLD**
  - Default: 30
  - Developer comment: Target-generated threat threshold to allow embargo (affected by modifiers)

- **EMBARGO_SAME_IDEOLOGY_AI_WEIGHT**
  - Default: -20
  - Developer comment: AI weight for same ideology

- **EMBARGO_DIFFERENT_IDEOLOGY_AI_WEIGHT**
  - Default: 15
  - Developer comment: AI weight for different ideology

- **EMBARGO_DIFFERENT_IDEOLOGY_AT_OFFENSIVE_WAR_AI_WEIGHT**
  - Default: 10
  - Developer comment: AI weight for different ideology and in offensive war (additive with above)

- **EMBARGO_RECIPIENT_IS_MAJOR_AI_WEIGHT**
  - Default: 10
  - Developer comment: Ai weight for recipient being major

- **EMBARGO_NEIGHBOUR_AI_WEIGHT**
  - Default: -10
  - Developer comment: AI weight for embargoing neighbors (neighbors are big and scary, we should consider not doing it)

- **EQUIPMENT_PURCHASE_ACCEPTANCE_OPINION**
  - Default: 1.1
  - Developer comment: Acceptance factor for opinion

- **EQUIPMENT_PURCHASE_ACCEPTANCE_SAME_IDEOLOGY**
  - Default: 15
  - Developer comment: Acceptance value added if same ideology

- **EQUIPMENT_PURCHASE_ACCEPTANCE_SCRIPTED_IDEOLOGY_ACCEPTANCE**
  - Default: 1.0
  - Developer comment: Acceptance factor for scripted ideology acceptance modifier

- **EQUIPMENT_PURCHASE_ACCEPTANCE_TRADE_INFLUENCE**
  - Default: 0.70
  - Developer comment: Acceptance factor for trade influence (adjusted from base value)

- **EQUIPMENT_PURCHASE_ACCEPTANCE_COMPETING_FACTIONS**
  - Default: -30
  - Developer comment: Acceptance value added if both countries are in factions, and factions are different

- **EQUIPMENT_PURCHASE_ACCEPTANCE_EMBARGO**
  - Default: -200
  - Developer comment: Acceptance value added if either side has embargoed the other

- **EQUIPMENT_PURCHASE_ACCEPTANCE_NON_AGGRESSION_PACT**
  - Default: 25
  - Developer comment: Acceptance value added if there is a non-aggression pact between the countries

- **MARKET_ACCESS_ACCEPTANCE_OPINION**
  - Default: 1.1
  - Developer comment: Acceptance factor for opinion

- **MARKET_ACCESS_ACCEPTANCE_SAME_IDEOLOGY**
  - Default: 15
  - Developer comment: Acceptance value added if same ideology

- **MARKET_ACCESS_ACCEPTANCE_SCRIPTED_IDEOLOGY_ACCEPTANCE**
  - Default: 1.0
  - Developer comment: Acceptance factor for scripted ideology acceptance modifier

- **MARKET_ACCESS_ACCEPTANCE_TRADE_INFLUENCE**
  - Default: 0.70
  - Developer comment: Acceptance factor for trade influence (adjusted from base value)

- **MARKET_ACCESS_ACCEPTANCE_COMPETING_FACTIONS**
  - Default: -30
  - Developer comment: Acceptance value added if both countries are in factions, and factions are different

- **MARKET_ACCESS_ACCEPTANCE_EMBARGO**
  - Default: -200
  - Developer comment: Acceptance value added if either side has embargoed the other

- **MARKET_ACCESS_ACCEPTANCE_NO_TRADE_ROUTE**
  - Default: -100
  - Developer comment: Acceptance value added if there is no valid trade route between the countries

- **MARKET_ACCESS_ACCEPTANCE_NON_AGGRESSION_PACT**
  - Default: 25
  - Developer comment: Acceptance value added if there is a non-aggression pact between the countries

## NCountry

- **EVENT_PROCESS_OFFSET**
  - Default: 20
  - Developer comment: Events are checked every X day per country or state (1 is ideal, but CPU heavy)

- **BASE_RESEARCH_SLOTS**
  - Default: 2
  - Developer comment: Base number of research slots per country.

- **POPULATION_YEARLY_GROWTH_BASE**
  - Default: 0.015
  - Developer comment: basic population growth per year, used for monthly manpower gain

- **RESISTANCE_STRENGTH_FROM_VP**
  - Default: 0.001
  - Developer comment: How much strength ticking speed gives each VP score.

- **RESISTANCE_STRENGTH_FROM_NEIGHBORS**
  - Default: 0.5
  - Developer comment: Multiplies how much resistance can spread from one state to its neighbors, a state will spread whatever is highest of its victorypoints resistance increase or half of any of its neighbors spread, multiplied by this

- **RESISTANCE_DECAY_WHEN_NO_GROWTH**
  - Default: 0.005
  - Developer comment: Resistance will fall by this much each day if there is nothing increasing it ( no VPs and no spread from neighbors )

- **REINFORCEMENT_DIVISION_PRIORITY_COUNT**
  - Default: 3
  - Developer comment: How many priority stages we have in division template? 0)Reserves, 1)Normal, 2)Elite.

- **REINFORCEMENT_DIVISION_PRIORITY_DEFAULT**
  - Default: 1
  - Developer comment: Each template by default is 1)Normal

- **REINFORCEMENT_THEATER_GROUP_PRIORITY_DEFAULT**
  - Default: 1
  - Developer comment: Each theater group by default is 1)Normal

- **REINFORCEMENT_THEATRE_PRIORITY_COUNT**
  - Default: 3
  - Developer comment: Same as with divisions...

- **REINFORCEMENT_THEATRE_PRIORITY_DEFAULT**
  - Default: 1

- **REINFORCEMENT_AIRBASE_PRIORITY_COUNT**
  - Default: 3

- **REINFORCEMENT_AIRBASE_PRIORITY_DEFAULT**
  - Default: 1

- **REINFORCEMENT_DELIVERY_SPEED_MIN**
  - Default: 0.6
  - Developer comment: The distance from the supply region to capital should affect the speed only a little bit. Main factor for penalty is overcrowded areas, and not the route length.

- **REINFORCEMENT_EQUIPMENT_DELIVERY_SPEED**
  - Default: 0.3
  - Developer comment: Modifier for army equipment reinforcement speed

- **REINFORCEMENT_MANPOWER_DELIVERY_SPEED**
  - Default: 10.0
  - Developer comment: Modifier for army manpower reinforcement delivery speed (travel time)

- **REINFORCEMENT_MANPOWER_CHUNK**
  - Default: 0.1
  - Developer comment: Chunk size of manpower reinforcement delivery, in % of total manpower needed by the template.

- **EQUIPMENT_UPGRADE_CHUNK_MAX_SIZE**
  - Default: 10
  - Developer comment: Maximum chunk size of equipment upgrade distribution per update.

- **COUNTRY_SCORE_MULTIPLIER**
  - Default: 1.0
  - Developer comment: Weight of the country score.

- **ARMY_SCORE_MULTIPLIER**
  - Default: 0.15
  - Developer comment: Based on number of armies.

- **NAVY_SCORE_MULTIPLIER**
  - Default: 1.0
  - Developer comment: Based on number of navies.

- **AIR_SCORE_MULTIPLIER**
  - Default: 0.1
  - Developer comment: Based on number of planes (which is typically a lot).

- **INDUSTRY_SCORE_MULTIPLIER**
  - Default: 1.0
  - Developer comment: Based on number of factories.

- **PROVINCE_SCORE_MULTIPLIER**
  - Default: 0.1
  - Developer comment: Based on number of controlled provinces.

- **NUCLEAR_BOMB_DROP_WAR_SUPPORT_EFFECT_MAX_INFRA**
  - Default: 0.2
  - Developer comment: Reduce enemy national war support on nuking a province, the value scales with infrastructure up to this number

- **NUCLEAR_BOMB_DROP_WAR_SUPPORT_EFFECT_MAX_VP**
  - Default: 3
  - Developer comment: War support will be scaled down if there's less VP than this in the province

- **THERMONUCLEAR_BOMB_DROP_WAR_SUPPORT_EFFECT_MAX_INFRA**
  - Default: 0.2
  - Developer comment: Reduce enemy national war support on nuking a province, the value scales with infrastructure up to this number

- **THERMONUCLEAR_BOMB_DROP_WAR_SUPPORT_EFFECT_MAX_VP**
  - Default: 3
  - Developer comment: War support will be scaled down if there's less VP than this in the province

- **WEEKLY_STABILITY_GAIN**
  - Default: 0.0

- **WEEKLY_WAR_SUPPORT_GAIN**
  - Default: 0.0

- **SUPPLY_CONVOY_FACTOR**
  - Default: 0.25
  - Developer comment: How many convoys each supply needs

- **CONVOY_RANGE_FACTOR**
  - Default: 1
  - Developer comment: How much range affects convoy need for resource trades and supply

- **CONVOY_LENDLEASE_RANGE_FACTOR**
  - Default: 1
  - Developer comment: How much range affects convoy need for lend lease

- **CONVOY_INTERNATIONAL_MARKET_RANGE_FACTOR**
  - Default: 1
  - Developer comment: How much range affects convoy need for international market

- **LOCAL_MANPOWER_ACCESSIBLE_NON_CORE_FACTOR**
  - Default: 0.02
  - Developer comment: accessible recruitable factor base

- **MAX_NON_CORE_MANPOWER_FACTOR**
  - Default: 1.0
  - Developer comment: max clamp for recruitable local non core manpower factor for states

- **DEFAULT_STABILITY**
  - Default: 0.5
  - Developer comment: Default stability if not scripted otherwise.
  - Usage:
    ```text
    Also used for calculating the modifiers applied to the country with the
    stability_good_modifier
    and
    stability_bad_modifier
    static modifiers
    , multiplying the relevant modifiers by
    |
    Current Stability
    −
    DEFAULT STABILITY
    |
    DEFAULT STABILITY
    {\displaystyle {\frac {|{\text{Current Stability}}-{\text{DEFAULT STABILITY}}|}{\text{DEFAULT STABILITY}}}}
    . Highly unstable on the low values and completely disables the modifier if set to 0.
    ```

- **DEFAULT_WAR_SUPPORT**
  - Default: 0.5
  - Developer comment: Default war support if not scripted otherwise.
  - Usage:
    ```text
    Also used for calculating the modifiers applied to the country with the
    war_support_good_modifier
    and
    war_support_bad_modifier
    static modifiers
    , multiplying the relevant modifiers by
    |
    Current War Support
    −
    DEFAULT WAR SUPPORT
    |
    DEFAULT WAR SUPPORT
    {\displaystyle {\frac {|{\text{Current War Support}}-{\text{DEFAULT WAR SUPPORT}}|}{\text{DEFAULT WAR SUPPORT}}}}
    . Highly unstable on the low values and completely disables the modifier if set to 0.
    ```

- **BASE_STABILITY_WAR_FACTOR**
  - Default: -0.2
  - Developer comment: Default stability war factor

- **BASE_STABILITY_PARTY_POPULARITY_FACTOR**
  - Default: 0.15
  - Developer comment: Default stability rulling party popularity factor

- **MIN_COUP_STABILITY_FACTOR**
  - Default: 0.0
  - Developer comment: Min value of coup factor in stability

- **MAX_COUP_STABILITY_FACTOR**
  - Default: 2.0
  - Developer comment: Max value of coup factor in stability

- **MIN_COUP_SUCCESS_STABILITY**
  - Default: 0.8
  - Developer comment: Max stability when coup will happen

- **WAR_SUPPORT_OFFNSIVE_WAR**
  - Default: -0.2
  - Developer comment: Impact of being in offensive war

- **WAR_SUPPORT_DEFENSIVE_WAR**
  - Default: 0.2
  - Developer comment: Impact of being in defensive war

- **WAR_SUPPORT_TENSION_IMPACT**
  - Default: 0.4
  - Developer comment: Total impact of world tension

- **MIN_STABILITY**
  - Default: 0.0

- **MAX_STABILITY**
  - Default: 1.0

- **MIN_WAR_SUPPORT**
  - Default: 0.0

- **MAX_WAR_SUPPORT**
  - Default: 1.0

- **FRONT_PROVINCE_SCORE**
  - Default: 20
  - Developer comment: Max province score of a front. Used for the hostile troop alert

- **MAJOR_IC_RATIO**
  - Default: 3
  - Developer comment: difference in total factories needed to be considered major with respect to other nation

- **MAJOR_MIN_FACTORIES**
  - Default: 35
  - Developer comment: need at least these many factories to become a major

- **MAX_INTELLIGENCE_DIFFERENCE**
  - Default: 10.0
  - Developer comment: (Old Intel) Max difference in intelligence levels between countries

- **INTEL_FROM_ALLIANCE_FACTOR**
  - Default: 0.3
  - Developer comment: Multiplied to the difference between a country intel and the maximum value in the alliance to compute the amount of intel that flows from the alliance to that country. 0 means no alliance contribution, 1 means a country intel's is the same as the max in the alliance.

- **MAX_INTELLIGENCE_DATA_DEVIATION**
  - Default: 1.0
  - Developer comment: (Old Intel) Max deviation in estimating default espionage values ( 0.0 - 1.0 )

- **MAX_INTELLIGENCE_MILITARY_DATA_DEVIATION**
  - Default: 1.0
  - Developer comment: (Old Intel) Max deviation in estimating enemy military units amount ( 0.0 - 1.0 )

- **MAX_INTELLIGENCE_NAVY_DATA_DEVIATION**
  - Default: 0.3
  - Developer comment: (Old Intel) Max deviation in estimating enemy ships amount ( 0.0 - 1.0 )

- **MAX_INTELLIGENCE_AIR_DATA_DEVIATION**
  - Default: 1.0
  - Developer comment: (Old Intel) Max deviation in estimating enemy air planes amount ( 0.0 - 1.0 )

- **MAX_INTELLIGENCE_CONVOY_DATA_DEVIATION**
  - Default: 0.3
  - Developer comment: (Old Intel) Max deviation in estimating enemy convoys amount ( 0.0 - 1.0 )

- **MAX_INTELLIGENCE_MANPOWER_DATA_DEVIATION**
  - Default: 0.4
  - Developer comment: (Old Intel) Max deviation in estimating enemy total manpower amount ( 0.0 - 1.0 )

- **MAX_INTELLIGENCE_FIELDED_MANPOWER_DATA_DEVIATION**
  - Default: 0.35
  - Developer comment: (Old Intel) Max deviation in estimating enemy fielded manpower amount ( 0.0 - 1.0 )

- **MAX_INTELLIGENCE_INDUSTRY_DATA_DEVIATION**
  - Default: 0.4
  - Developer comment: (Old Intel) Max deviation in estimating enemy total industry

- **MIN_MANPOWER_RATIO**
  - Default: 0.15
  - Developer comment: Min manpower ratio to show manpower alert

- **ARMY_IMPORTANCE_FACTOR**
  - Default: 5.0
  - Developer comment: Army factor for AI and calculations

- **TERRAIN_IMPORTANCE_FACTOR**
  - Default: 5.0
  - Developer comment: Terrain base factor for state strategic value

- **VICTORY_POINTS_IMPORTANCE_FACTOR**
  - Default: 5.0
  - Developer comment: State victory points importance factor for AI and calculations

- **BUILDING_IMPORTANCE_FACTOR**
  - Default: 3.0
  - Developer comment: State building importance factor for AI and calculations

- **RESOURCE_IMPORTANCE_FACTOR**
  - Default: 1.0
  - Developer comment: State resource importance factor for AI and calculations

- **INTERPOLATED_FRONT_STEPS_SHORT**
  - Default: 2
  - Developer comment: Performance optimization - The amount of steps for interpolated fronts. Non-AI countries got full interpolated fronts, the rest has optimized version of it.

- **MIN_AIR_RESERVE_RATIO**
  - Default: 0.33
  - Developer comment: Min manpower ratio to show air reserves alert

- **POLITICAL_POWER_LOWER_CAP**
  - Default: -500.0
  - Developer comment: Min amount of political power country should have

- **POLITICAL_POWER_UPPER_CAP**
  - Default: 2000.0
  - Developer comment: Max amount of political power country should have

- **RESISTANCE_IMPORTANT_LEVEL**
  - Default: 0.25
  - Developer comment: Level when resistance becomes dangerous

- **RESISTANCE_IMPORTANT_COUNTRY_LEVEL**
  - Default: 0.25
  - Developer comment: Level when average resistance in a country becomes dangerous

- **MIN_MAJOR_COUNTRIES**
  - Default: 7
  - Developer comment: MIN_MAJOR_COUNTRIES countries with most factories will be considered as major countries

- **ADDITIONAL_MAJOR_COUNTRIES_IC_RATIO**
  - Default: 0.7
  - Developer comment: Countries will also be considered major when having more factories that the average of top MIN_MAJOR_COUNTRIES countries' factories times ADDITIONAL_MAJOR_COUNTRIES_IC_RATIO

- **BASE_TENSION_MAJOR_COUNTRY_INDEX**
  - Default: 1
  - Developer comment: Which major country should be considered the base country when scaling generated world tension. 0 is the country with the most factories, 1 is the second most-factories country etc. This number has to be lower than MIN_MAJOR_COUNTRIES

- **MIN_NAVAL_SUPPLY_EFFICIENCY**
  - Default: 0.1
  - Developer comment: Min ratio when supplies will be considered delivered from the capital by naval path

- **PARADROP_AIR_SUPERIORITY_RATIO**
  - Default: 0.7
  - Developer comment: Min ratio of air superiority for paradropping

- **STATE_VALUE_BASE**
  - Default: 10.0
  - Developer comment: Base value of a state (value is used to determine costs in e.g. peace conferences)

- **STATE_VALUE_BUILDING_SLOTS_MULT**
  - Default: 4.0
  - Developer comment: The value of each building slot in a state

- **STATE_VALUE_MANPOWER_FACTOR**
  - Default: 0.1
  - Developer comment: State cost increases with this for every 10k population (so 3.1M becomes 310 and then multiplied by this)

- **INVASION_REPORT_EXPERATION_DAYS**
  - Default: 30
  - Developer comment: Invasion experation days

- **MIN_FOCUSES_FOR_CONTINUOUS**
  - Default: 10
  - Developer comment: Focuses needed to unlock continuous focuses

- **AUTONOMOUS_TOTAL_SCORE**
  - Default: 5000
  - Developer comment: Total score for autonomous scale

- **AUTONOMOUS_SPILLOVER**
  - Default: 0.025
  - Developer comment: Total score that can be saved to reach next level

- **CIVIL_WAR_INVOLVEMENT_MIN_TENSION**
  - Default: 0.5
  - Developer comment: base value of world tension to involve other sides to the civil war

- **UNCAPITULATE_LEVEL**
  - Default: 0.1
  - Developer comment: if we reclaim this much and our capital we reset capitulate status

- **BASE_SURRENDER_LIMIT**
  - Default: 0.8
  - Developer comment: Base level of occupation required for country surrender

- **SURRENDER_LIMIT_MULT_FOR_COUNTRIES_WITH_NO_CORES**
  - Default: 0.7
  - Developer comment: Countries with no owned cores will their surrender level multiplied by this amount

- **MIN_SURRENDER_LIMIT**
  - Default: 0.2
  - Developer comment: Minimum non-forced surrender limit. valid 0-1

- **BASE_MOBILIZATION_SPEED**
  - Default: 0.01
  - Developer comment: Base speed of manpower mobilization  #in 1/1000 of 1 %

- **INTERCEPTION_WAR_SUPPORT_SCALE**
  - Default: 0.00001
  - Developer comment: Scaling of interceptions to war support impact

- **INTERCEPTION_BOMBING_WAR_SUPPORT_IMPACT**
  - Default: 0.3
  - Developer comment: Max impact of interceptions on the war support

- **BOMBING_WAR_SUPPORT_PENALTY_SCALE**
  - Default: -0.00015
  - Developer comment: Scaling of bomber damage to war support impact, will be added weekly as a war support penalty

- **MAX_BOMBING_WEEKLY_WAR_SUPPORT_PENALTY**
  - Default: -0.006
  - Developer comment: Max penalty that will gained per week from bomber's damage

- **BOMBING_WEEKLY_WAR_SUPPORT_PENALTY_DECAY**
  - Default: 0.001
  - Developer comment: Weekly decay of bomber damage war support penalty

- **MAX_BOMBING_WAR_SUPPORT_IMPACT**
  - Default: -0.3
  - Developer comment: Max total penalty from bomber's damage

- **HEROES_BEING_KILLED_WAR_SUPPORT_PENALTY_SCALE**
  - Default: -0.03
  - Developer comment: Scaling of war heroes manpower lost to war support impact, will be added weekly as a war support penalty

- **MAX_HEROES_BEING_KILLED_WEEKLY_WAR_SUPPORT_PENALTY**
  - Default: -0.006
  - Developer comment: Max penalty that will gained per week from war heroes manpower lost

- **HEROES_BEING_KILLED_WEEKLY_WAR_SUPPORT_PENALTY_DECAY**
  - Default: 0.001
  - Developer comment: Weekly decay of war heroes manpower lost war support penalty

- **MAX_HEROES_BEING_KILLED_WAR_SUPPORT_IMPACT**
  - Default: -0.3
  - Developer comment: Max total penalty from war heroes manpower lost

- **WAR_SUPPORT_FROM_CASUALTIES**
  - Default: 0.025
  - Developer comment: Base value (inverted) for calculating heroes being killed

- **CONVOYS_BEING_RAIDED_WAR_SUPPORT_PENALTY_SCALE**
  - Default: -0.05
  - Developer comment: Scaling of trade convoy raided to war support impact, will be added weekly as a war support penalty

- **MAX_CONVOYS_BEING_RAIDED_WEEKLY_WAR_SUPPORT_PENALTY**
  - Default: -0.006
  - Developer comment: Max penalty that will gained per week from trade convoy raided

- **CONVOYS_BEING_RAIDED_WEEKLY_WAR_SUPPORT_PENALTY_DECAY**
  - Default: 0.001
  - Developer comment: Weekly decay of trade convoy raided war support penalty

- **MAX_CONVOYS_BEING_RAIDED_WAR_SUPPORT_IMPACT**
  - Default: -0.5
  - Developer comment: Max total penalty from trade convoy raided

- **FEMALE_UNIT_LEADER_BASE_CHANCE**
  - Default: { 0.5, 0.5, 0.5, 0.5, 0.5 }
  - Developer comment:
    ```text
    applies as a factor to female unit leader randomization
    the values needs to be zero if you don't actually have random portraits
    country leaders
    army leaders
    navy leaders
    air leaders
    operatives
    ```

- **CONVOYS_SUNK_MULTIPLIER_FOR_WAR_SUPPORT**
  - Default: 0.2
  - Developer comment: once a trade convoy ship sunk, you will get a larger negative impact on your war support

- **CONVOYS_BEING_RAIDED_DAILY_WAR_SUPPORT_IMPACT_FROM_OVERSEA_STATES**
  - Default: 0.2
  - Developer comment: resource transfer convoys convoys from our states being raided will give a daily war support penalty depending on how important that resource is and how inefficent convoys are

- **CONVOYS_SUNK_MULTIPLIER_FOR_WAR_SUPPORT_FROM_OVERSEA_STATES**
  - Default: 0.2
  - Developer comment: once a resource transfer convoys from our states ship sunk, you will get a larger negative impact on your war support

- **CONVOYS_BEING_RAIDED_DAILY_WAR_SUPPORT_IMPACT**
  - Default: 0.2
  - Developer comment: trade convoys being raided will give a daily war support penalty depending on how important that resource is and how inefficent convoys are

- **MAX_PROPAGANDA_STABILITY_IMPACT**
  - Default: -0.2
  - Developer comment: Max total penalty from operative performing the propaganda mission in a country

- **MAX_PROPAGANDA_WAR_SUPPORT_IMPACT**
  - Default: -0.2
  - Developer comment: Max total penalty from operative performing the propaganda mission in a country

- **PROPAGANDA_STABILITY_DAILY_DECAY**
  - Default: 0.001
  - Developer comment: Amount of stability recovered daily from propaganda effort

- **PROPAGANDA_WAR_SUPPORT_DAILY_DECAY**
  - Default: 0.001
  - Developer comment: Amount of war support recovered daily from war support effort

- **NUM_DAYS_TO_FULLY_DELETE_STOCKPILED_EQUIPMENT**
  - Default: 90
  - Developer comment: time in days to fully delete equipments from stockpile. when you delete an equipment, they go to a temporary hidden pool which still can be seized

- **AIR_SUPPLY_CONVERSION_SCALE**
  - Default: 0.01
  - Developer comment: Conversion scale for planes to air supply

- **AIR_SUPPLY_DROP_EXPIRATION_HOURS**
  - Default: 168
  - Developer comment: Air drop length after being dropped

- **STARTING_COMMAND_POWER**
  - Default: 0.0
  - Developer comment: starting command power for every country

- **BASE_MAX_COMMAND_POWER**
  - Default: 80.0
  - Developer comment: base value for maximum command power

- **BASE_COMMAND_POWER_GAIN**
  - Default: 0.4
  - Developer comment: base value for daily command power gain

- **AIR_VOLUNTEER_PLANES_RATIO**
  - Default: 0.2
  - Developer comment: Ratio for volunteer planes available for sending in relation to sender air force

- **AIR_VOLUNTEER_BASES_CAPACITY_LIMIT**
  - Default: 0.1
  - Developer comment: Ratio for volunteer planes available for sending in relation to receiver air base capacity

- **ATTACHE_XP_SHARE**
  - Default: 0.15
  - Developer comment: Country received xp from attaches

- **SPECIAL_FORCES_CAP_BASE**
  - Default: 0.05
  - Developer comment: Max ammount of special forces battalions is total number of non-special forces battalions multiplied by this and modified by a country modifier

- **SPECIAL_FORCES_CAP_MIN**
  - Default: 24
  - Developer comment: You can have a minimum of this many special forces battalions, regardless of the number of non-special forces battalions you have, this can also be modified by a country modifier

- **DAYS_OF_WAR_BEFORE_SURRENDER**
  - Default: 7
  - Developer comment: Number of days a war has to have existed before anyone can surrender in it

- **FUEL_LEASE_CONVOY_RATIO**
  - Default: 0.0005
  - Developer comment: num convoys needed per fuel land lease

- **STARTING_FUEL_RATIO**
  - Default: 0.25
  - Developer comment: starting fuel ratio compared to max fuel for countries

- **BASE_FUEL_GAIN_PER_OIL**
  - Default: 2
  - Developer comment: base amount of fuel gained hourly per excess oil

- **BASE_FUEL_GAIN**
  - Default: 2.0
  - Developer comment: base amount of fuel gained hourly, independent of excess oil

- **BASE_FUEL_CAPACITY**
  - Default: 50000
  - Developer comment: base amount of fuel capacity

- **SCORCHED_EARTH_STATE_COST**
  - Default: 5
  - Developer comment: pp cost to scorch a state

- **COUNTRY_MANPOWER_CAPITULATED_FREE_POOL_FACTOR**
  - Default: 0.1
  - Developer comment: Factor on amount of normal manpower left for an exiled nation with no territory.

- **COUNTRY_MANPOWER_CAPITULATED_CORE_GAIN_FACTOR**
  - Default: 0.001
  - Developer comment: Factor on amount of normal manpower gained for the exile nation. From owned states that are controlled by an enemy. State manpower reduced by factor 1000 in code.

- **COUNTRY_MANPOWER_CAPITULATED_NON_CORE_GAIN_FACTOR**
  - Default: 0.001
  - Developer comment: Factor on amount of normal manpower gained for the exile nation. From owned states that are controlled by an enemy. State manpower reduced by factor 1000 in code.

- **GIE_MAX_LEGITIMACY**
  - Default: 100
  - Developer comment: Legitimacy max of a GiE

- **GIE_CAPITULATE_MAX_STOCKPILE_TRANSFER**
  - Default: 0.1
  - Developer comment: 0-1 Transfers ratio of stockpile. from 0 to this define depending on starting legitimacy on capitulation.

- **GIE_CAPITULATE_MIN_LEGIT_FOR_TRANSFER**
  - Default: 5
  - Developer comment: 0-100 Minimum starting legitimacy to transfer any equipment at all.

- **GIE_CAPITULATION_LEGITIMACY_WARSCORE_FACTOR**
  - Default: 0.5
  - Developer comment: Multiplies war contribution percent with this factor for part of starting legitimacy. (0.5 would mean a 50 % war contribution gives 25 more legitimacy)

- **GIE_CAPITULATION_LEGITIMACY_WARLENGTH_FACTOR**
  - Default: 1.0
  - Developer comment: Multiplies war length (nr of weeks) with this factor for part of starting legitimacy. (1.0 would mean a war length of 30 weeks gives 30 more legitimacy)

- **GIE_WARSCORE_GAIN_LEGITIMACY_FACTOR**
  - Default: 1
  - Developer comment: Factor on how much legitimacy is gained from warscore earned by GiE units.

- **GIE_HOST_CIC_FROM_LEGITIMACY_MAX**
  - Default: 5
  - Developer comment: Host will receive from 0 to this value in CIC.

- **GIE_HOST_MIC_FROM_LEGITIMACY_MAX**
  - Default: 5
  - Developer comment: Host will receive from 0 to this value in MIC.

- **GIE_HOST_DOCKYARDS_FROM_LEGITIMACY_MAX**
  - Default: 0
  - Developer comment: Host will receive from 0 to this value in dockyards.

- **GIE_VETERAN_MANPOWER_NON_CORE_GAIN_FACTOR**
  - Default: 0.005
  - Developer comment: Factor on amount of manpower gained from owned states that are controlled by an enemy. State manpower reduced by factor 1000 in code.

- **GIE_VETERAN_MANPOWER_CORE_GAIN_FACTOR**
  - Default: 0.01
  - Developer comment: Factor on amount of manpower gained from owned states that are controlled by an enemy. State manpower reduced by factor 1000 in code.

- **GIE_MANPOWER_TOTAL_MAX_FACTOR**
  - Default: 0.5
  - Developer comment: Factor on max amount of exile manpower that can be gained from owned states. Approaching this will give diminishing returns. Reduced by factor 100 in code.

- **GIE_MANPOWER_RATO_OF_MAX_START_PENALTY**
  - Default: 0.5
  - Developer comment: When this ratio of max manpower has been recruited we start applying the penalty.

- **GIE_MANPOWER_GAIN_PENALTY_MAX**
  - Default: 0.95
  - Developer comment: Max penalty on exile manpower growth.

- **GIE_EXILE_AIR_RECRUITMENT_LEGITIMACY**
  - Default: 50
  - Developer comment: Legitimacy required to recruit exile airwings

- **GIE_EXILE_AIR_START_EXPERIENCE**
  - Default: 3
  - Developer comment: Starting experience for exile airwings

- **GIE_EXILE_TROOP_RECRUITMENT_LEGITIMACY**
  - Default: 25
  - Developer comment: Legitimacy required to recruit exile troops

- **GIE_EXILE_TROOPS_DEPLOY_TRAINING_MAX_LEVEL**
  - Default: 2
  - Developer comment: Max XP exile troops can receive from training

- **GIE_EXILE_ARMY_LEADER_LEGITIMACY_LEVELS**
  - Default: { 30, 60, 90 }
  - Developer comment: Legitimacy levels where a new army leader is received.

- **GIE_EXILE_ARMY_LEADER_START_LEVEL**
  - Default: 3
  - Developer comment: Starting level for exile leader

- **GIE_ESCAPING_DIVISIONS_TRANSFER_DAYS**
  - Default: 30
  - Developer comment: days to transfer escaping divisions to host nation

- **GIE_ESCAPING_DIVISIONS_XP_BOOST**
  - Default: 0.4
  - Developer comment: Escaping divisions gain a boost to experience. Only the toughest motherbadasses will band together and survive to git me one hundred Nazi scalps ... Or die tryin'...

- **GIE_DIVISION_ATTACK_BONUS_AGAINST_OCCUPIER**
  - Default: 0.1
  - Developer comment: Attack bonus factor against whoever occupies your core territory.

- **GIE_DIVISION_DEFENSE_BONUS_AGAINST_OCCUPIER**
  - Default: 0.1
  - Developer comment: Attack bonus factor against whoever occupies your core territory.

- **GIE_DIVISION_ATTACK_BONUS_ON_CORE**
  - Default: 0.1
  - Developer comment: Attack bonus factor when fighting on cores.

- **GIE_DIVISION_DEFENSE_BONUS_ON_CORE**
  - Default: 0.1
  - Developer comment: Defense bonus factor when fighting on cores.

- **GIE_ESCAPING_DIVISIONS_EQUIPMENT_RATIO**
  - Default: 0.2
  - Developer comment: Base equipment ratio on escaped troops.

- **GIE_ESCAPING_DIVISIONS_AMOUNT_RATIO**
  - Default: 0.1
  - Developer comment: Ratio on amount of divisions that escapes. Scales with starting legitimacy

- **GIE_LIBERATED_NATION_DAILY_LEGITIMACY_CHANGE**
  - Default: -1.5
  - Developer comment: An uncapitulated exile that is fully liberated will have legitimacy changed with this amount daily. Will be automatically reinstated when it reaches 0.

- **GIE_EXILE_TRANSFER_ON_LEADER_CAPITULATION_MANPOWER_FACTOR**
  - Default: 0.1
  - Developer comment: Factor on exile manpower kept when a faction leader capitulates and the hosted exiles are transfered.

- **GIE_CONVOY_ON_CREATION**
  - Default: 10
  - Developer comment: Number of convoy a GiE will get on creation.

- **SURRENDER_LIMIT_REDUCTION_PER_COLLABORATION**
  - Default: 0.3
  - Developer comment: each percent of collaboration will lower surrender limit by this percentage

- **SURRENDER_RECIPIENT_SCORE_PER_COLLABORATION**
  - Default: 1.0
  - Developer comment: countries with collaboration will get bonus while game calculates which country the enemy will capitulate

- **COMPLIANCE_PER_COLLABORATION**
  - Default: 1.0
  - Developer comment: each percent of collaboration will be converted to this compliance at capitulation

- **WILL_LEAD_TO_WAR_FOCUS_PERSISTENCE**
  - Default: 60
  - Developer comment: taken focuses that has lead to war will still make ai prep for war for this many days after being taken

- **WILL_LEAD_TO_WAR_DECISION_PERSISTENCE**
  - Default: 30
  - Developer comment: the decision thats lead to war will sitll make ai prep for war for this many days after being taken/cooldown/timeout

- **ARMY_COUNT_DAILY_LERP_FOR_TRAINING_XP**
  - Default: 0.002
  - Developer comment: number of armies that is used in training xp calculates daily lerps to actual number (if real number is lower)

- **ARMY_COUNT_DAILY_DECREASE_FOR_TRAINING_XP**
  - Default: 0.1
  - Developer comment: number of armies that is used in training xp calculates daily linearly approaches this number (if real number is lower)

## NResistance

- **INITIAL_STATE_RESISTANCE**
  - Default: 1.0
  - Developer comment: initial resistance percentage of a state once it is captured

- **INITIAL_STATE_COMPLIANCE**
  - Default: 0.0
  - Developer comment: initial compliance percentage of a state once it is captured

- **COMPLIANCE_FACTOR_ON_STATE_CONTROLLER_CHANGE**
  - Default: -0.5
  - Developer comment: compliance factor that applies when the state controller changes (in between allies, compliance is zeroed if it is taken by original country)

- **RESISTANCE_COOLDOWN_WHEN_DISABLED**
  - Default: -0.25
  - Developer comment: resistance cooldown when the state is taken back by its original owner (compliance is zeroed in that case)

- **RESISTANCE_TARGET_BASE**
  - Default: 35.0
  - Developer comment: base resistance target percentage

- **RESISTANCE_TARGET_MODIFIER_HAS_CLAIM**
  - Default: -5.0
  - Developer comment: resistance target modifier in % for states we have claim

- **RESISTANCE_TARGET_MODIFIER_PER_STABILITY_LOSS**
  - Default: 0.2
  - Developer comment: resistance target modifier per stability below 100%

- **RESISTANCE_TARGET_MODIFIER_PER_COMPLIANCE**
  - Default: -0.5
  - Developer comment: resistance target modifier per compliance %

- **RESISTANCE_TARGET_MODIFIER_IS_AT_PEACE**
  - Default: -10.0
  - Developer comment: resistance target modifier when we are at peace

- **RESISTANCE_TARGET_MODIFIER_STATE_VP**
  - Default: { 0, 0.0, 5, 5.0, 20, 10.0, 50, 20.0 }
  - Developer comment:
    ```text
    resistance target modifier pairs for vp. first entry is total vp in state and second entry is amount of target modifier that applies for that threshold
    0 - 5
    5 - 20
    20 - 50
    50 - ...
    ```

- **RESISTANCE_TARGET_MODIFIER_OCCUPIED_CAPITULATED**
  - Default: 10.0
  - Developer comment: resistance target modifier when the enemy is capitulated

- **RESISTANCE_TARGET_MODIFIER_OCCUPIED_IS_EXILE_MIN**
  - Default: 2.0
  - Developer comment: min & max resistance target modifier resistance target modifier for exile countries. interpolated using legitimacy

- **RESISTANCE_TARGET_MODIFIER_OCCUPIED_IS_EXILE_MAX**
  - Default: 20.0

- **RESISTANCE_TARGET_MODIFIER_POP_LOW**
  - Default: -20.0
  - Developer comment: how much we reduce the resistance target

- **RESISTANCE_TARGET_MODIFIER_POP_VERY_LOW**
  - Default: -50.0
  - Developer comment: resistance target modifier in % for states we have claim

- **RESISTANCE_POP_LOW_CUTOFF**
  - Default: 10000

- **RESISTANCE_POP_VERY_LOW_CUTOFF**
  - Default: 1000

- **RESISTANCE_TARGET_MIN_CAP_FOR_NON_COMPLIANCE**
  - Default: 10
  - Developer comment: min resistance target will be capped to this percentage for non-compliance sources

- **RESISTANCE_DECAY_BASE**
  - Default: 0.1
  - Developer comment: base resistance decay

- **RESISTANCE_DECAY_MIN**
  - Default: 0.01
  - Developer comment: min resistance decay

- **RESISTANCE_DECAY_MAX**
  - Default: 100.0
  - Developer comment: nax resistance decay

- **RESISTANCE_DECAY_MODIFIER_HAS_CLAIM**
  - Default: 25.0
  - Developer comment: resistance decay modifier for our claims

- **RESISTANCE_DECAY_MODIFIER_FACTORS**
  - Default: { 10, -50, 20, -25 }
  - Developer comment:
    ```text
    resistance decay modifier when resistance hits a certain percentage
    below 10% it has a -50% modifier on decay
    below 20% it has a -25% modifier on decay
    ```

- **MIN_DAMAGE_TO_GARRISONS_MODIFIER**
  - Default: 0.1
  - Developer comment: modifier that applies to losses from resistance attack to garrisons at most can be reduced to this amount

- **RESISTANCE_GROWTH_BASE**
  - Default: 0.2
  - Developer comment: base resistance grow

- **RESISTANCE_GROWTH_MIN**
  - Default: 0.01
  - Developer comment: min resistance grow

- **RESISTANCE_GROWTH_MAX**
  - Default: 100.0
  - Developer comment: max resistance grow

- **COMPLIANCE_GROWTH_BASE**
  - Default: 0.075
  - Developer comment: base compliance grow

- **COMPLIANCE_GROWTH_MIN**
  - Default: -100.0
  - Developer comment: min compliance grow

- **COMPLIANCE_GROWTH_MAX**
  - Default: 100.0
  - Developer comment: max compliance grow

- **COMPLIANCE_GROWTH_IS_AT_PEACE**
  - Default: 10
  - Developer comment: compliance growth buff at peace

- **COMPLIANCE_GROWTH_HAS_CLAIM**
  - Default: 5
  - Developer comment: compliance growth buff if state has a claim

- **COMPLIANCE_DECAY_AT_MAX_COMPLIANCE**
  - Default: -0.083
  - Developer comment: as compliance increases, it gets a decay rate depending on its value. compliance should stabilize at some value until its growth changes

- **COMPLIANCE_DECAY_PER_EXILE_LEGITIMACY**
  - Default: -0.015
  - Developer comment: higher legitimacy will give higher decay to compliance

- **RESISTANCE_RATIO_DIFF_TO_SPREAD**
  - Default: 0.5
  - Developer comment: resistance diff between two neighbour states will spread by this ratio ( from highest resistance states to lower ones and it will only spread once to a state)

- **RESISTANCE_ACTIVITY_CHANCE_AT_MAX_RESISTANCE**
  - Default: 0.312

- **RESISTANCE_ACTIVITY_MIN_GARRISON_PENETRATE_CHANCE**
  - Default: 0.02

- **RESISTANCE_TARGET_TO_REENABLE_RESISTANCE**
  - Default: 10
  - Developer comment: resistance will be disabled once it reaches zero and will not be reenabled until resistance target reaches above this value

- **GARRISON_LOG_MAX_MONTHS**
  - Default: 12

- **NO_COMPLIANCE_GAIN_ENABLE_LIMIT**
  - Default: 0.5
  - Developer comment: at least this ratio of no garrison law should be active in order to no compliance gain to take effect

- **GARRISON_MANPOWER_MIN_DELIVERY_SPEED**
  - Default: 0.7
  - Developer comment: Minimum base delivery speed if the chunk can't be calculated.

- **GARRISON_MANPOWER_REINFORCEMENT_SPEED**
  - Default: 2000.0
  - Developer comment: Modifier for garrison manpower reinforcement.  This value is the maximum to be delivered which is then modified by distance

- **GARRISON_EQUIPMENT_DELIVERY_SPEED**
  - Default: 4.0
  - Developer comment: Modifier for garrison equipment reinforcement speed

- **GARRISON_STR_POW_MANPOWER**
  - Default: 2
  - Developer comment: Scales impact of manpower deficiency by raising that deficiency to the number here. Formula: efficiency = 1.0 - manpower_deficiency^GARRISON_STR_POW_MANPOWER

- **GARRISON_STR_POW_EQUIPMENT**
  - Default: 3
  - Developer comment: Scales impact of euqipment deficiency by raising that deficiency to the number here. Formula: efficiency = 1.0 - equipment_deficiency^GARRISON_STR_POW_EQUIPMENT

- **SUPPRESSION_NEEDED_BY_RESISTANCE_POINT**
  - Default: 0.75
  - Developer comment: Number of suppression point we need for each 1% of resistance

- **SUPPRESSION_NEEDED_LOWER_CAP**
  - Default: 10.0
  - Developer comment: if resistance is lower than this value then we always act as though it is at the define for the purpose of suppresion requirements

- **SUPPRESSION_NEEDED_UPPER_CAP**
  - Default: 50.0
  - Developer comment: if resistance is greater than this value then we always act as though it is at the define for the purpose of suppresion requirements

- **GARRISON_MANPOWER_LOST_BY_ATTACK**
  - Default: 0.016
  - Developer comment: Ratio of manpower lost by garrison at each attack on garrison (this number will be reduced by the hardness of garrison template)

- **GARRISON_EQUIPMENT_LOST_BY_ATTACK**
  - Default: 0.02
  - Developer comment: Ratio of equipment lost by garrison at each attack on garrison (this number will be reduced by the hardness of garrison template)

- **MAXIMUM_GARRISON_HARDNESS_WHEN_ATTACKED**
  - Default: 0.90
  - Developer comment: Cap to be sure that garrison will suffer lost in attack, even with a almost 100% hardness

- **FOREIGN_MANPOWER_MIN_THRESHOLD**
  - Default: 5000
  - Developer comment: The minimum number of Manpower that AI will accept to give at once, in order to avoid many weird little transfer.

- **MANPOWER_BUFFER_TO_NOT_GIVE_MINOR**
  - Default: 0.3
  - Developer comment: To determine how much AI can give as foreign manpower, we calculate how much manpower we use, and add this buffer. The result is what we want to keep, for minor countries. So higher this number is, lower we will give Manpower.

- **MANPOWER_BUFFER_TO_NOT_GIVE_MAJOR**
  - Default: 0.6
  - Developer comment: To determine how much AI can give as foreign manpower, we calculate how much manpower we use, and add this buffer. The result is what we want to keep, for major countries. So higher this number is, lower we will give Manpower.

- **MAX_GARRISON_RATIO_WE_AGREE_TO_SUPPORT**
  - Default: 3.0
  - Developer comment: The part of the manpower needed by the foreign garrison, that AI will agree to support with our manpower. If negative number, AI will not take into consideration the need, and just calculate how much they can give.

- **FOREIGN_MANPOWER_AI_COOLDOWN_DAYS**
  - Default: 30
  - Developer comment: Number of days after an AI give us manpower before the AI accept to give more.

- **INITIAL_HISTORY_RESISTANCE**
  - Default: 0.0
  - Developer comment: resistance value for initial colony states

- **INITIAL_HISTORY_COMPLIANCE**
  - Default: 70.0
  - Developer comment: compliance value for initial colony states

- **INITIAL_GARRISON_STRENGTH**
  - Default: 1
  - Developer comment: garrison value for initial colony states

- **STATE_COMPLIANCE_DECAY_FOR_LOST_STATES**
  - Default: 0.05
  - Developer comment: daily compliance decay for the states you lost control of

## NProduction

- **MAX_EQUIPMENT_RESOURCES_NEED**
  - Default: 3
  - Developer comment: Max number of different strategic resources an equipment can be dependent on.

- **MAX_CIV_FACTORIES_PER_LINE**
  - Default: 15
  - Developer comment: Max number of factories that can be assigned a single production line.

- **DEFAULT_MAX_NAV_FACTORIES_PER_LINE**
  - Default: 10

- **FLOATING_HARBOR_MAX_NAV_FACTORIES_PER_LINE**
  - Default: 5

- **CONVOY_MAX_NAV_FACTORIES_PER_LINE**
  - Default: 15

- **CAPITAL_SHIP_MAX_NAV_FACTORIES_PER_LINE**
  - Default: 5

- **MAX_MIL_FACTORIES_PER_LINE**
  - Default: 150

- **RAILWAY_GUN_MAX_MIL_FACTORIES_PER_LINE**
  - Default: 5

- **RAILWAY_GUN_REPAIR_SPEED**
  - Default: 8.0
  - Developer comment: Railway gun strength repair speed per factory

- **EFFICIENCY_LOSS_PER_UNUSED_DAY**
  - Default: 1
  - Developer comment: Daily loss of efficiency for unused factory slots ( efficiency is tracked per factory slot in the production line )

- **RESOURCE_PENALTY_WARNING_CRITICAL_RATIO**
  - Default: 0.8
  - Developer comment: Switch to red progress bar if penalty is over threshold

- **BASE_FACTORY_SPEED**
  - Default: 5
  - Developer comment: Base factory speed multiplier (how much hoi3 style IC each factory gives).

- **BASE_FACTORY_SPEED_MIL**
  - Default: 4.50
  - Developer comment: Base factory speed multiplier (how much hoi3 style IC each factory gives).

- **BASE_FACTORY_SPEED_NAV**
  - Default: 2.5
  - Developer comment: Base factory speed multiplier (how much hoi3 style IC each factory gives).

- **BASE_FACTORY_START_EFFICIENCY_FACTOR**
  - Default: 10
  - Developer comment: Base start efficiency for factories expressed in %.

- **BASE_FACTORY_MAX_EFFICIENCY_FACTOR**
  - Default: 50
  - Developer comment: Base max efficiency for factories expressed in %.

- **BASE_FACTORY_EFFICIENCY_GAIN**
  - Default: 1
  - Developer comment: Base efficiency factor.

- **BASE_FACTORY_EFFICIENCY_BALANCE_FACTOR**
  - Default: 0.1
  - Developer comment: Factory efficiency balancing factor

- **BASE_FACTORY_EFFICIENCY_VARIANT_CHANGE_FACTOR**
  - Default: 90
  - Developer comment: Base factor for changing production variants in %.

- **BASE_FACTORY_EFFICIENCY_PARENT_CHANGE_FACTOR**
  - Default: 30
  - Developer comment: Base factor for changing production parent<->children in %.

- **BASE_FACTORY_EFFICIENCY_FAMILY_CHANGE_FACTOR**
  - Default: 70
  - Developer comment: Base factor for changing production with same family in %.

- **BASE_FACTORY_EFFICIENCY_ARCHETYPE_CHANGE_FACTOR**
  - Default: 20
  - Developer comment: Base factor for changing production with same archetype in %.

- **EQUIPMENT_BASE_LEND_LEASE_WEIGHT**
  - Default: 1.0
  - Developer comment: Base equipment lend lease weight

- **EQUIPMENT_LEND_LEASE_WEIGHT_FACTOR**
  - Default: 0.01
  - Developer comment: Base equipment lend lease factor

- **LEND_LEASE_DELIVERY_TOTAL_DAYS**
  - Default: 30
  - Developer comment: Nr of days between lend lease deliveries

- **ANNEX_STOCKPILES_RATIO**
  - Default: 1.0
  - Developer comment: How much stockpiled equipment will be transferred on annexation

- **ANNEX_FIELD_EQUIPMENT_RATIO**
  - Default: 0.25
  - Developer comment: How much equipment from deployed divisions will be transferred on annexation

- **ANNEX_FUEL_RATIO**
  - Default: 0.25
  - Developer comment: How much fuel will be transferred on annexation

- **ANNEX_CONVOYS_RATIO**
  - Default: 0.15
  - Developer comment: How many convoys will be transferred on annexation

- **MIN_POSSIBLE_TRAINING_MANPOWER**
  - Default: 100000
  - Developer comment: How many deployment lines minimum can be training

- **MIN_FIELD_TO_TRAINING_MANPOWER_RATIO**
  - Default: 0.75
  - Developer comment: Ratio which % of army in field can be trained

- **CAPITULATE_STOCKPILES_RATIO**
  - Default: 0.5
  - Developer comment: How much equipment from deployed divisions will be transferred on capitulation

- **CAPITULATE_FUEL_RATIO**
  - Default: 0.5
  - Developer comment: How much fuel will be transferred on capitulation

- **INFRA_MAX_CONSTRUCTION_COST_EFFECT**
  - Default: 1
  - Developer comment: Building in a state with higher infrastructure will reduce the cost of shared buildings.

- **PRODUCTION_RESOURCE_LACK_PENALTY**
  - Default: -0.05
  - Developer comment: Penalty decrease while lack of resource per factory

- **CIC_BANK_SPEED_BOOST_FACTOR**
  - Default: 0.25
  - Developer comment: The CIC bank can boost production speed with this factor (0.5 means 50 %)

- **MIN_LICENSE_ACTIVE_DAYS**
  - Default: 30
  - Developer comment: Min days for license to be active

- **BASE_LICENSE_IC_COST**
  - Default: 1
  - Developer comment: Base IC cost for lended license

- **LICENSE_IC_COST_YEAR_INCREASE**
  - Default: 1
  - Developer comment: IC cost equipment for every year of equipment after 1936

- **LICENSE_EQUIPMENT_BASE_SPEED**
  - Default: -0.25
  - Developer comment: base MIC speed modifier for licensed equipment

- **LICENSE_EQUIPMENT_TECH_SPEED_PER_YEAR**
  - Default: -0.05
  - Developer comment: MIC speed modifier for licensed equipment for each year of difference between actual and latest equipment

- **LICENSE_EQUIPMENT_TECH_SPEED_MAX_YEARS**
  - Default: 4
  - Developer comment: Maximum years for MIC speed modifier

- **LICENSE_EQUIPMENT_SPEED_NOT_FACTION**
  - Default: -0.10
  - Developer comment: MIC speed modifier for licensed equipment for not being in faction

- **LICENSE_EQUIPMENT_UPGRADE_XP_FACTOR**
  - Default: 2.0
  - Developer comment: XP cost for upgrading licensed equipment

- **LICENSE_EQUIPMENT_SPEED_NO_LICENSE**
  - Default: -0.50
  - Developer comment: Penalty for producing non licensed equipment

- **CONVERSION_SPEED_BONUS**
  - Default: 0
  - Developer comment: Modifier to the production speed when converting equipment

- **EQUIPMENT_MODULE_ADD_XP_COST**
  - Default: 5.0
  - Developer comment: XP cost for adding a new equipment module in an empty slot when creating an equipment variant.

- **EQUIPMENT_MODULE_REPLACE_XP_COST**
  - Default: 6.0
  - Developer comment: XP cost for replacing one equipment module with an unrelated module when creating an equipment variant.

- **EQUIPMENT_MODULE_CONVERT_XP_COST**
  - Default: 3.0
  - Developer comment: XP cost for converting one equipment module to a related module when creating an equipment variant.

- **EQUIPMENT_MODULE_REMOVE_XP_COST**
  - Default: 1.0
  - Developer comment: XP cost for removing an equipment module and leaving the slot empty when creating an equipment variant.

- **BASE_NAVAL_EQUIPMENT_CONVERSION_IC_COST_FACTOR**
  - Default: 0.2
  - Developer comment: Fraction of the hull industry cost which is always included in the refitting cost.

- **BASE_LAND_EQUIPMENT_CONVERSION_IC_COST_FACTOR**
  - Default: 0.9
  - Developer comment: Fraction of the chassis industry cost which is always included in the conversion cost.

- **MIN_NAVAL_EQUIPMENT_CONVERSION_RESOURCE_COST_FACTOR**
  - Default: 0.2
  - Developer comment: Minimum fraction of a naval equipment's strategic resource cost that any conversion will cost.

- **MIN_LAND_EQUIPMENT_CONVERSION_RESOURCE_COST_FACTOR**
  - Default: 0
  - Developer comment: Minimum fraction of a land equipment's strategic resource cost that any conversion will cost.

- **SHIP_REFIT_MAX_PROGRESS_TO_CANCEL**
  - Default: 0.2
  - Developer comment: Maximum refitting progress % that we still allow to cancel wihtout having to scuttle the ship.

- **SHIP_REFIT_DAMAGE_TO_PROGRESS_FACTOR**
  - Default: 0.5
  - Developer comment: When a ship is being damaged (for example port strike) while refitting, the damage is transferred to the production line progress instead. This variable is used to balance it.

- **MINIMUM_NUMBER_OF_FACTORIES_TAKEN_BY_CONSUMER_GOODS_VALUE**
  - Default: 1
  - Developer comment: The minimum number of factories we have to put on consumer goods, by value.

- **MINIMUM_NUMBER_OF_FACTORIES_TAKEN_BY_CONSUMER_GOODS_PERCENT**
  - Default: 0.1
  - Developer comment: The minimum number of factories we have to put on consumer goods, in percent.

- **INITIAL_ALLOWED_FACTORY_RATIO_FOR_REPAIRS**
  - Default: 1.0
  - Developer comment: max % of factories allowed on autorepairs

## NMarket

- **PURCHASE_CONTRACT_DELIVERY_TOTAL_DAYS**
  - Default: 30
  - Developer comment: Number of days between purchase contract deliveries

- **IC_TO_CIC_FACTOR**
  - Default: 2.0
  - Developer comment: The factor for mapping IC cost to CIC cost. Should be a positive number.

- **MAX_CIV_FACTORIES_PER_CONTRACT**
  - Default: 15
  - Developer comment: Max number of factories that can be assigned for paying single contract.

- **LOW_PRICE_LEVEL_FACTOR**
  - Default: 0.75
  - Developer comment: The factor of base equipment price for low price level. Should be in range (0,1]

- **HIGH_PRICE_LEVEL_FACTOR**
  - Default: 1.25
  - Developer comment: The factor of base equipment price for high price level. Should be more than 1.

- **MIN_DELIVERY_LIMIT_WARNING_UI**
  - Default: 0.8
  - Developer comment: The delivery percentage under we want to let player know the contract is inefficient. [0,1]

- **PURCHASE_CONTRACT_SUBSIDY_BONUS_SPEED_FACTOR**
  - Default: 1.0
  - Developer comment: The factor of speed bonus from subsidies

- **CONVOY_WEIGHT_OVERRIDE**
  - Default: 0.0
  - Developer comment: Overrides the default lend leas weight of convoys for international market

- **REQUEST_AUTOMATION_AUTO_ACCEPT_MARKET_ACCESS_DEFAULT**
  - Default: true
  - Developer comment: Whether by default should accept market access requests from other countries.

- **REQUEST_AUTOMATION_AUTO_SEND_MARKET_ACCESS_DEFAULT**
  - Default: true
  - Developer comment: Whether by default should send market access requests to other countries.

- **REQUEST_AUTOMATION_AUTO_ACCEPT_PURCHASE_DEFAULT**
  - Default: false
  - Developer comment: Whether by default should accept purchase requests from other countries.

- **CONTRACT_ESTIMATE_AVERAGE_CONVOY_COUNT_ALPHA**
  - Default: 0.5
  - Developer comment: How strong effect should have the daily convoy count on the average (1.0 means it will use only the new number as average)

- **CONTRACT_ESTIMATE_AVERAGE_DAILY_PRODUCTION_ALPHA**
  - Default: 0.5
  - Developer comment: How strong effect should have the daily production on the average (1.0 means it will use only the new number as average)

- **CONTRACT_ESTIMATE_AVERAGE_CONVOY_COUNT_SNAP_LIMIT**
  - Default: 0.3
  - Developer comment: If the difference between current and estimated available convoy count is smaller then this value, we will use the current value for calculations.

- **CONTRACT_ESTIMATE_AVERAGE_DAILY_PRODUCTION_SNAP_LIMIT**
  - Default: 1.5
  - Developer comment: If the difference between current and estimated daily production is smaller then this value, we will use the current value for calculations.

- **CONTRACT_ESTIMATE_AVERAGE_CONVOY_SUNK_MULTIPLIER_ALPHA**
  - Default: 0.5
  - Developer comment: How strong effect should have the daily sunk efficiency on the average (1.0 means it will use only the new number as average)

- **CONTRACT_ESTIMATE_AVERAGE_CONVOY_SUNK_MULTIPLIER_SNAP_LIMIT**
  - Default: 0.05
  - Developer comment: If the difference between current and estimated sunk efficiency convoy count is smaller then this value, we will use the current value for calculations.

- **WARNING_CONVOYS_SUNK_MAX_DAYS**
  - Default: 30
  - Developer comment: The contracts will show sunk convoy message if there was sunk convoy in this amount of days

## NTechnology

- **MAX_SUBTECHS**
  - Default: 3
  - Developer comment: Max number of sub technologies a technology can have.

- **BASE_RESEARCH_POINTS_SAVED**
  - Default: 30.0
  - Developer comment: Base amount of research points a country can save per slot.

- **BASE_YEAR_AHEAD_PENALTY_FACTOR**
  - Default: 2
  - Developer comment: Base year ahead penalty

- **BASE_TECH_COST**
  - Default: 110
  - Developer comment: Base cost for a tech. multiplied with tech cost and ahead of time penalties

- **MAX_TECH_SHARING_BONUS**
  - Default: 0.5
  - Developer comment: Max technology sharing bonus that can be applied instantly

- **LICENSE_PRODUCTION_TECH_BONUS**
  - Default: 0.2
  - Developer comment: License production tech bonus

- **DEFAULT_XP_UNLOCK_RESEARCH_COST**
  - Default: 0
  - Developer comment: default xp cost of a research to unlock directly

- **DEFAULT_XP_BOOST_RESEARCH_COST**
  - Default: 0
  - Developer comment: default xp cost of a research to speed up the process

- **DEFAULT_XP_BOOST_RESEARCH_BONUS**
  - Default: 0
  - Developer comment: default boost research bonus gained when xp is used to research an item

- **MIN_RESEARCH_SPEED**
  - Default: 0.1
  - Developer comment: research speed can't go below this value

- **USE_BONUS_REGRET_TIMER**
  - Default: 3
  - Developer comment: Number of days the player has to regret using a limited tech bonus

## NPolitics

- **BASE_LEADER_TRAITS**
  - Default: 3
  - Developer comment: Base amount of leader traits.

- **MAX_RANDOM_LEADERS**
  - Default: 1
  - Developer comment: Maximum amount random leader to have per party.

- **BASE_POLITICAL_POWER_INCREASE**
  - Default: 2
  - Developer comment: Weekly increase of PP.

- **ARMY_LEADER_COST**
  - Default: 5
  - Developer comment: command power cost for recruiting new leaders, 'this value' * number_of_existing_leaders_of_type

- **NAVY_LEADER_COST**
  - Default: 5
  - Developer comment: command power cost for recruiting new leaders, 'this value' * number_of_existing_leaders_of_type

- **ARMY_LEADER_MAX_COST**
  - Default: 80
  - Developer comment: max cost BEFORE modifiers

- **NAVY_LEADER_MAX_COST**
  - Default: 80
  - Developer comment: max cost BEFORE modifiers

- **LEADER_TRAITS_XP_SHOW**
  - Default: 0.05
  - Developer comment: Amount of XP a trait needs to be shown in tooltips of a leader.

- **REVOLTER_PARTY_POPULARITY**
  - Default: 0.4
  - Developer comment: Revolter party loses 80% popularity when the civil war breaks out

- **MIN_OVERTHROWN_GOVERNMENT_SUPPORT_RATIO**
  - Default: 0.4
  - Developer comment: Min possible support for new government after puppeting the government

- **NUM_OCCUPATION_POLICIES**
  - Default: 4
  - Developer comment: Number of potential occupation policies

- **DEFAULT_OCCUPATION_POLICY**
  - Default: 1
  - Developer comment: Defaullt value for occupation policy

- **INSTANT_WIN_REVOLTER_POPULARITY_RATIO**
  - Default: 0.4
  - Developer comment: Min party popularity for instant win in one province state

- **INSTANT_WIN_POPULARITY_WIN**
  - Default: 50
  - Developer comment: New party popularity

## NBuildings

- **ANTI_AIR_SUPERIORITY_MULT**
  - Default: 5.0
  - Developer comment: How much air superiority reduction to the enemy does our AA guns? Normally each building level = -1 reduction. With this multiplier.

- **SAM_MISSION_SUPERIORITY**
  - Default: 5.0
  - Developer comment: How much air superiority each SAM mission gives per rocket wing performing SAM missions.

- **MAX_BUILDING_LEVELS**
  - Default: 15
  - Developer comment: Max levels a building can have.

- **AIRBASE_CAPACITY_MULT**
  - Default: 200
  - Developer comment: Each level of airbase building multiplied by this, gives capacity (max operational value). Value is int. 1 for each airplane.

- **ROCKETSITE_CAPACITY_MULT**
  - Default: 100
  - Developer comment: Each level of rocketsite building multiplied by this, gives capacity (max operational value). Value is int. 1 for each rocket.

- **NAVALBASE_REPAIR_MULT**
  - Default: 0.05
  - Developer comment: Each level of navalbase building repairs X strength and can repair as many ships as its level

- **RADAR_RANGE_BASE**
  - Default: 20
  - Developer comment: Radar range base, first level radar will be this + min, best radar will be this + max

- **RADAR_RANGE_MIN**
  - Default: 20
  - Developer comment: Radar range (from state center to province center) in measure of map pixels. Exluding techs.

- **RADAR_RANGE_MAX**
  - Default: 200
  - Developer comment: Range is interpolated between building levels 1-15.

- **RADAR_INTEL_EFFECT**
  - Default: 40
  - Developer comment: Province covered by radar increases intel by 10 (where 255 is max). Province may be covered by multiple radars, then the value sums up.

- **SABOTAGE_FACTORY_DAMAGE**
  - Default: 100.0
  - Developer comment: How much damage takes a factory building in sabotage when state is occupied. Damage is mult by (1 + resistance strength), i.e. up to 2 x base value.

- **BASE_FACTORY_REPAIR**
  - Default: 1.0
  - Developer comment: Default repair rate in percentage before factories are taken into account (1.0 equals 1%).

- **BASE_FACTORY_REPAIR_FACTOR**
  - Default: 2.0
  - Developer comment: Factory speed modifier when repairing.

- **SUPPLY_PORT_LEVEL_THROUGHPUT**
  - Default: 3
  - Developer comment: supply throughput per level of naval base

- **MAX_SHARED_SLOTS**
  - Default: 25
  - Developer comment: Max slots shared by factories

- **OWNER_CHANGE_EXTRA_SHARED_SLOTS_FACTOR**
  - Default: 1
  - Developer comment: Scale factor of extra shared slots when state owner change.

- **DESTRUCTION_COOLDOWN_IN_WAR**
  - Default: 30
  - Developer comment: Number of days cooldown between removal of buildings in war times

- **INFRASTRUCTURE_RESOURCE_BONUS**
  - Default: 0.2
  - Developer comment: multiplicative resource bonus for each level of (non damaged) infrastructure

- **SUPPLY_ROUTE_RESOURCE_BONUS**
  - Default: 0.2
  - Developer comment: multiplicative resource bonus for having a railway/naval connection to the capital

- **INFRASTRUCTURE_MUD_EFFECT**
  - Default: -0.8
  - Developer comment: multiplicative effect on mud growth for max infra

## NDeployment

- **BASE_DEPLOYMENT_TRAINING**
  - Default: 1
  - Developer comment: Base training done each day during deployment.

## NMilitary

- **COMBAT_VALUE_ORG_IMPORTANCE**
  - Default: 1
  - Developer comment: Multiplier on TotalOrganisation when determining the combat value of a division

- **COMBAT_VALUE_STR_IMPORTANCE**
  - Default: 1
  - Developer comment: Multiplier on TotalStrength when determining the combat value of a division

- **SOFT_ATTACK_TARGETING_FACTOR**
  - Default: 1.0
  - Developer comment: How much we care about potential soft attacks when evaluating priority combat target

- **HARD_ATTACK_TARGETING_FACTOR**
  - Default: 1.2
  - Developer comment: How much we care about potential hard attacks when evaluating priority combat target

- **CASUALTIES_WS_P_PENALTY_DIVISOR**
  - Default: 200
  - Developer comment: Divisor for casualties WS penalty

- **CASUALTIES_WS_A_PENALTY_DIVISOR**
  - Default: 600
  - Developer comment: Divisor for casualties WS penalty

- **PIERCING_THRESHOLDS**
  - Default: { 1.00, 0.75, 0.50, 0.00 }
  - Developer comment:
    ```text
    Our piercing / their armor must be this value to deal damage fraction equal to the index in the array below [higher number = higher penetration]. If armor is 0, 1.00 will be returned.
    there isn't much point setting this higher than 0
    ```

- **PIERCING_THRESHOLD_DAMAGE_VALUES**
  - Default: { 1.00, 0.80, 0.65, 0.50 }
  - Developer comment: 0 armor will always receive maximum damage (so add overmatching at your own peril). the system expects at least 2 values, with no upper limit.

- **DIVISIONAL_COMMANDER_TRAIT_XP_REQUIREMENT**
  - Default: 400.0
  - Developer comment: Get a trait if any valid options & xp gained >= this

- **NUM_DAYS_FOR_OPERATION_ENTRY**
  - Default: 60
  - Developer comment: Number of days that a unit must have been on a particular active order instance to receive a history entry.

- **MAX_LEADERS_TO_SHOW**
  - Default: 50
  - Developer comment: Max officers to show in field officers list, sorted by field EXP. Divisions with awardable entries will potentially supercede this limit

- **BASE_FEMALE_DIVISIONAL_COMMANDER_CHANCE**
  - Default: 0
  - Developer comment: Chance to receive a female divisonal commander. This is set to zero in the base game, as we do not have generic female portraits for many graphical culture groups.

- **DIVISIONAL_COMMANDER_RANK_XP_THRESHOLD**
  - Default: { 0, 100.0, 200.0, 400.0, 800.0 }
  - Developer comment: this expects a value between 0 and 1 and is added to by female_divisional_commander_chance. If you don't have female generic portraits defined, you -will- get silhouettes.XP thresholds for divisional commander ranks. [TAG]_DIVISION_EXPERIENCE_TITLE_ARMY_EXPERIENCE_[array index]

- **USE_MULTIPLICATIVE_ORG_LOSS_WHEN_MOVING**
  - Default: true
  - Developer comment: whether to apply org_loss_when_moving modifiers additively or multiplicatively (hardcoded multiplicative pre-2021)

- **HOURLY_ORG_MOVEMENT_IMPACT**
  - Default: -0.2
  - Developer comment: how much org is lost every hour while moving an army.

- **ZERO_ORG_MOVEMENT_MODIFIER**
  - Default: -0.8
  - Developer comment: speed impact at 0 org.

- **INFRA_ORG_IMPACT**
  - Default: 0.5
  - Developer comment: scale factor of infra on org regain.

- **ENGAGEMENT_WIDTH_PER_WIDTH**
  - Default: 2.0
  - Developer comment: how much enemy combat width we are allowed to engage per width of our own

- **INFRASTRUCTURE_MOVEMENT_SPEED_IMPACT**
  - Default: -0.05
  - Developer comment: speed penalty per infrastucture below maximum.

- **VPS_FOR_HISTORY_ENTRY**
  - Default: 3
  - Developer comment: Minimum VPs required to receive an entry in divisional history

- **VPS_FOR_HIGH_HISTORY_ENTRY**
  - Default: 8
  - Developer comment: VPs required for high-level history entry

- **ENTRIES_TO_CHECK_FOR_DUPLICATE**
  - Default: 2
  - Developer comment: Max number of history entries to check back to see if we're being awarded the same entry

- **COST_INCREASE_PER_ACTIVE_MEDAL**
  - Default: 0.25
  - Developer comment: Additional cost factor per active medal

- **MAX_ENTRY_ELISION_COUNT**
  - Default: 4
  - Developer comment: If we do the same type of thing consecutively, each entry will stack locations up to this number

- **GENERATE_AI_DIV_COMMAND_HISTORY_ENTRIES**
  - Default: true
  - Developer comment: Should we generate history entries for the AI (may cause savegame bloat)

- **FIELD_EXPERIENCE_ON_DIVISION_MULT**
  - Default: 0.04
  - Developer comment: Multiply field experience gained by this, when applying to divisional commander

- **MAX_FIELD_EXPERIENCE_ON_DIVISION**
  - Default: 8000
  - Developer comment: Max experience that can be gained on divisional commanders

- **FIELD_EXPERIENCE_ON_DIVISION_PER_MEDAL_MULT**
  - Default: 0.1
  - Developer comment: Multiply officer field experience gain by this * number of division medals on application

- **HISTORY_OPERATION_RANDOM_MAX**
  - Default: 24
  - Developer comment: max random int to roll when determining whether to grant an awardable entry for operations. 1/N chances.

- **CASUALTY_COUNT_FOR_HISTORY_ENTRY**
  - Default: 40000
  - Developer comment: number of received casualties to receive a history entry (one only)

- **FIELD_OFFICER_PROMOTION_PENALTY**
  - Default: 0.25
  - Developer comment: Amount of division experience lost when promoting a commander (reduced by modifiers)

- **HISTORICAL_ORDER_NAME_EXHAUSTION**
  - Default: false
  - Developer comment: Do historically chosen order instances exhaust their case names? If false ie, Operation Barbarossa will appear for any orders fulfilling the conditions for Germany

- **WAR_SCORE_LOSSES_RATIO**
  - Default: 0.5
  - Developer comment: war score gained for every 1000 casualties

- **WAR_SCORE_LOSSES_MULT_IF_CAPITULATED**
  - Default: 0.25
  - Developer comment: factor applied to war score gained from casualties if capitulated

- **WAR_SCORE_STRATEGIC_BOMBING_FACTOR**
  - Default: 0.02
  - Developer comment: war score gained for every damage made to enemy's building with strategic bombing

- **WAR_SCORE_STRAT_BOMBING_DECAY_PER_CIVILIAN_FACTORY**
  - Default: 0.10
  - Developer comment: monthly war score deducted from strategic bombing for every civilian factory in service on the bombed enemy side

- **WAR_SCORE_AIR_IC_LOSS_FACTOR**
  - Default: 0.08
  - Developer comment: war score gained for every IC of damage done to an enemy's air mission

- **WAR_SCORE_LAND_DAMAGE_FACTOR**
  - Default: 0.1
  - Developer comment: war score gained for every strengh damage done to an enemy's army

- **WAR_SCORE_ATTACKER_AND_WINNER_FACTOR**
  - Default: 1.2
  - Developer comment: factor applied to war score gained for strength damage done when being the attacker and the winner

- **WAR_SCORE_LAND_IC_LOSS_FACTOR**
  - Default: 0.08
  - Developer comment: war score gained for every IC damage done to an enemy's army

- **WAR_SCORE_PROVINCE_FACTOR**
  - Default: 4.0
  - Developer comment: war score gained when capturing a province for the first time, multiplied by province's worth

- **WAR_SCORE_LEND_LEASE_GIVEN_IC_FACTOR**
  - Default: 0.003
  - Developer comment: war score gained for every IC of lend lease sent to allies

- **WAR_SCORE_LEND_LEASE_GIVEN_FUEL_FACTOR**
  - Default: 0.003
  - Developer comment: war score gained for every 100 units of fuel lend lease sent to allies

- **WAR_SCORE_LEND_LEASE_RECEIVED_IC_FACTOR**
  - Default: 0.002
  - Developer comment: war score deducted for every IC of lend lease received from allies

- **WAR_SCORE_LEND_LEASE_RECEIVED_FUEL_FACTOR**
  - Default: 0.002
  - Developer comment: war score deducted for every 100 units of fuel lend lease received from allies

- **CORPS_COMMANDER_DIVISIONS_CAP**
  - Default: 24
  - Developer comment: how many divisions a corps commander is limited to. 0 = inf, < 0 = blocked

- **DIVISION_SIZE_FOR_XP**
  - Default: 8
  - Developer comment: how many battalions should a division have to count as a full divisions when calculating XP stuff

- **CORPS_COMMANDER_ARMIES_CAP**
  - Default: -1
  - Developer comment: how many armies a corps commander is limited to. 0 = inf, < 0 = blocked

- **FIELD_MARSHAL_DIVISIONS_CAP**
  - Default: 24
  - Developer comment: how many divisions a field marshall is limited to. 0 = inf, < 0 = blocked

- **FIELD_MARSHAL_ARMIES_CAP**
  - Default: 5
  - Developer comment: how many armies a field marshall is limited to. 0 = inf, < 0 = blocked

- **UNIT_LEADER_GENERATION_CAPITAL_CONTINENT_FACTOR**
  - Default: 100
  - Developer comment: Integer factor to multiply manpower.

- **RECON_SKILL_IMPACT**
  - Default: 5
  - Developer comment: how many skillpoints is a recon advantage worth when picking a tactic.

- **MAX_DIVISION_BRIGADE_WIDTH**
  - Default: 5
  - Developer comment: Max width of regiments in division designer.

- **MAX_DIVISION_BRIGADE_HEIGHT**
  - Default: 5
  - Developer comment: Max height of regiments in division designer.

- **MIN_DIVISION_BRIGADE_HEIGHT**
  - Default: 4
  - Developer comment: Min height of regiments in division designer.

- **MAX_DIVISION_SUPPORT_WIDTH**
  - Default: 1
  - Developer comment: Max width of support in division designer.

- **MAX_DIVISION_SUPPORT_HEIGHT**
  - Default: 5
  - Developer comment: Max height of support in division designer.

- **BASE_DIVISION_BRIGADE_GROUP_COST**
  - Default: 20
  - Developer comment: Base cost to unlock a regiment slot,

- **BASE_DIVISION_BRIGADE_CHANGE_COST**
  - Default: 5
  - Developer comment: Base cost to change a regiment column.

- **BASE_DIVISION_SUPPORT_SLOT_COST**
  - Default: 10
  - Developer comment: Base cost to unlock a support slot

- **MAX_ARMY_EXPERIENCE**
  - Default: 500
  - Developer comment: Max army experience a country can store

- **MAX_NAVY_EXPERIENCE**
  - Default: 500
  - Developer comment: Max navy experience a country can store

- **MAX_AIR_EXPERIENCE**
  - Default: 500
  - Developer comment: Max air experience a country can store

- **COMBAT_MINIMUM_TIME**
  - Default: 4
  - Developer comment: Shortest time possible for a combat in hours

- **SPOTTING_QUALITY_DROP_HOURS**
  - Default: 4
  - Developer comment: Each X hours the intel quality drops after unit was spotted.

- **LEADER_GROUP_MAX_SIZE**
  - Default: 1000
  - Developer comment: 5,			-- Max slots for leader groups.

- **MIN_SUPPLY_CONSUMPTION**
  - Default: 0.05
  - Developer comment: minimum value of supply consumption that a unit can get

- **LAND_COMBAT_ORG_DICE_SIZE**
  - Default: 4
  - Developer comment: nr of damage dice

- **LAND_COMBAT_STR_DICE_SIZE**
  - Default: 2
  - Developer comment: nr of damage dice

- **LAND_COMBAT_STR_DAMAGE_MODIFIER**
  - Default: 0.060
  - Developer comment: global damage modifier... but some equipment is returned at end of battles see : EQUIPMENT_COMBAT_LOSS_FACTOR

- **LAND_COMBAT_ORG_DAMAGE_MODIFIER**
  - Default: 0.053
  - Developer comment: global damage modifier

- **LAND_AIR_COMBAT_STR_DAMAGE_MODIFIER**
  - Default: 0.05
  - Developer comment: air global damage modifier

- **LAND_AIR_COMBAT_ORG_DAMAGE_MODIFIER**
  - Default: 0.10
  - Developer comment: global damage modifier

- **LAND_AIR_COMBAT_MAX_PLANES_PER_ENEMY_WIDTH**
  - Default: 3
  - Developer comment: how many CAS/TAC can enter a combat depending on enemy width there

- **LAND_COMBAT_STR_ARMOR_ON_SOFT_DICE_SIZE**
  - Default: 2
  - Developer comment: extra damage dice if our armor outclasses enemy

- **LAND_COMBAT_ORG_ARMOR_ON_SOFT_DICE_SIZE**
  - Default: 6
  - Developer comment: extra damage dice if our armor outclasses enemy

- **LAND_COMBAT_STR_ARMOR_DEFLECTION_FACTOR**
  - Default: 0.5
  - Developer comment: damage reduction if armor outclassing enemy

- **LAND_COMBAT_ORG_ARMOR_DEFLECTION_FACTOR**
  - Default: 0.5
  - Developer comment: damage reduction if armor outclassing enemy

- **LAND_COMBAT_COLLATERAL_FORT_FACTOR**
  - Default: 0.005
  - Developer comment: Factor to scale collateral damage to forts with.

- **LAND_COMBAT_COLLATERAL_INFRA_FACTOR**
  - Default: 0.0022
  - Developer comment: Factor to scale collateral damage to infra with.

- **LAND_COMBAT_FORT_DAMAGE_CHANCE**
  - Default: 5
  - Developer comment: chance to get a hit to damage on forts. (out of 100)

- **ATTRITION_DAMAGE_ORG**
  - Default: 0.08
  - Developer comment: damage from attrition to Organisation

- **ATTRITION_EQUIPMENT_LOSS_CHANCE**
  - Default: 0.1
  - Developer comment: Chance for loosing equipment when suffer attrition. Scaled up the stronger attrition is. Then scaled down by equipment reliability.

- **ATTRITION_EQUIPMENT_PER_TYPE_LOSS_CHANCE**
  - Default: 0.1
  - Developer comment: Chance for loosing equipment when suffer attrition. Scaled up the stronger attrition is. Then scaled down by equipment reliability.

- **ATTRITION_WHILE_MOVING_FACTOR**
  - Default: 1

- **RELIABILITY_ORG_REGAIN**
  - Default: -0.3
  - Developer comment: how much reliability affects org regain

- **RELIABILITY_ORG_MOVING**
  - Default: -1.0
  - Developer comment: how much reliability affects org loss on moving

- **RELIABILITY_WEATHER**
  - Default: 3.0
  - Developer comment: how much reliability is afffecting weather impact

- **RELIABILTY_RECOVERY**
  - Default: 0.4
  - Developer comment: factor affecting how much equipment is returned "from the dead"

- **BASE_CHANCE_TO_AVOID_HIT**
  - Default: 90
  - Developer comment: Base chance to avoid hit if defences left.

- **CHANCE_TO_AVOID_HIT_AT_NO_DEF**
  - Default: 60
  - Developer comment: chance to avoid hit if no defences left.

- **COMBAT_MOVEMENT_SPEED**
  - Default: 0.33
  - Developer comment: speed reduction base modifier in combat
  - Usage: Capped between 0.01 and 1

- **TACTIC_SWAP_FREQUENCEY**
  - Default: 12
  - Developer comment: hours between tactic swaps

- **PREFERRED_TACTIC_CHARACTER_SKILL_LEVEL_REQUIRED**
  - Default: 5
  - Developer comment: Which level a field marhal or general has to be before they can pick their preferred tactic

- **COUNTRY_PREFERRED_TACTIC_WEIGHT_FACTOR**
  - Default: 0.25
  - Developer comment: extra weight multiplier for the country preferred tactic when doing weighted random

- **ARMY_GENERAL_PREFERRED_TACTIC_WEIGHT_FACTOR**
  - Default: 0.5
  - Developer comment: extra weight multiplier for the army general preferred tactic when doing weighted random

- **FIELD_MARSHAL_PREFERRED_TACTIC_WEIGHT_FACTOR**
  - Default: 0.25
  - Developer comment: extra weight multiplier for the field marhsal preferred tactic when doing weighted random

- **PREFERRED_TACTIC_COMMAND_POWER_COST**
  - Default: 20
  - Developer comment: command point cost for changing preferred tactic

- **INITIATIVE_PICK_COUNTER_ADVANTAGE_FACTOR**
  - Default: 0.35
  - Developer comment: advantage per leader level for picking a counter

- **AMPHIBIOUS_INVADE_MOVEMENT_COST**
  - Default: 24.0
  - Developer comment: total progress cost of movement while amphibious invading

- **LAND_SPEED_MODIFIER**
  - Default: 0.05
  - Developer comment: basic speed control

- **RIVER_CROSSING_PENALTY**
  - Default: -0.3
  - Developer comment: small river crossing

- **RIVER_CROSSING_PENALTY_LARGE**
  - Default: -0.6
  - Developer comment: large river crossing

- **RIVER_CROSSING_SPEED_PENALTY**
  - Default: -0.25
  - Developer comment: small river crossing

- **RIVER_CROSSING_SPEED_PENALTY_LARGE**
  - Default: -0.5
  - Developer comment: large river crossing

- **RIVER_SMALL_START_INDEX**
  - Default: 0
  - Developer comment: color indices for rivers

- **RIVER_SMALL_STOP_INDEX**
  - Default: 6

- **RIVER_LARGE_STOP_INDEX**
  - Default: 11

- **BASE_FORT_PENALTY**
  - Default: -0.15
  - Developer comment: fort penalty

- **MULTIPLE_COMBATS_PENALTY**
  - Default: -0.5
  - Developer comment: defender penalty if attacked from multiple directions

- **DIG_IN_FACTOR**
  - Default: 0.02
  - Developer comment: bonus factor for each dug-in level

- **ARMY_LEADER_XP_GAIN_PER_UNIT_IN_COMBAT**
  - Default: 0.1
  - Developer comment: XP gain per unit in combat

- **CONSTANT_XP_RATIO_FOR_MULTIPLE_LEADERS_IN_SAME_COMBAT**
  - Default: 0.5
  - Developer comment: if there are multiple leaders in same combat, each one gets thisratio + (1-thisratio)/num leaders. amount of xp each general gets scales 1 0.75 0.66 etc for 1 2 3 generals

- **BASE_LEADER_TRAIT_GAIN_XP**
  - Default: 0.45
  - Developer comment: Base xp gain for traits per hour for armies

- **MAX_NUM_TRAITS**
  - Default: -1
  - Developer comment: cant have more, -1 to disable

- **ENEMY_AIR_SUPERIORITY_IMPACT**
  - Default: -0.35
  - Developer comment: effect on defense due to enemy air superiorty

- **ENEMY_AIR_SUPERIORITY_DEFENSE**
  - Default: 0.70
  - Developer comment: more AA attack will approach this amount of help (diminishing returns)

- **ENEMY_AIR_SUPERIORITY_DEFENSE_STEEPNESS**
  - Default: 112
  - Developer comment: how quickly defense approaches the max impact diminishing returns curve

- **ENEMY_AIR_SUPERIORITY_SPEED_IMPACT**
  - Default: -0.3
  - Developer comment: effect on speed due to enemy air superiority

- **ANTI_AIR_TARGETTING_TO_CHANCE**
  - Default: 0.07
  - Developer comment: Balancing value to determine the chance of ground AA hitting an attacking airplane, affecting both the effective average damage done by AA to airplanes, and the reduction of damage done by airplanes due to AA support

- **ANTI_AIR_ATTACK_TO_AMOUNT**
  - Default: 0.005
  - Developer comment: Balancing value to convert equipment stat anti_air_attack to the random % value of airplanes being hit.

- **ENCIRCLED_PENALTY**
  - Default: -0.3
  - Developer comment: penalty when completely encircled

- **UNIT_EXPERIENCE_PER_COMBAT_HOUR**
  - Default: 0.0001

- **UNIT_EXPERIENCE_SCALE**
  - Default: 1.0

- **UNIT_EXPERIENCE_PER_TRAINING_DAY**
  - Default: 0.0015

- **TRAINING_MAX_LEVEL**
  - Default: 2

- **DEPLOY_TRAINING_MAX_LEVEL**
  - Default: 1

- **TRAINING_EXPERIENCE_SCALE**
  - Default: 62.0

- **TRAINING_ORG**
  - Default: 0.2

- **ARMY_EXP_BASE_LEVEL**
  - Default: 1

- **UNIT_EXP_LEVELS**
  - Default: { 0.1, 0.3, 0.75, 0.9 }
  - Developer comment: Experience needed to progress to the next level

- **FIELD_EXPERIENCE_SCALE**
  - Default: 0.0015

- **FIELD_EXPERIENCE_MAX_PER_DAY**
  - Default: 1.2
  - Developer comment: Most xp you can gain per day

- **EXPEDITIONARY_FIELD_EXPERIENCE_SCALE**
  - Default: 0.3
  - Developer comment: reduction factor in Xp from expeditionary forces

- **LEND_LEASE_FIELD_EXPERIENCE_SCALE**
  - Default: 0.0005
  - Developer comment: Experience scale for lend leased equipment used in combat.

- **LEADER_EXPERIENCE_SCALE**
  - Default: 1.0

- **SLOWEST_SPEED**
  - Default: 4

- **REINFORCEMENT_REQUEST_MAX_WAITING_DAYS**
  - Default: 14
  - Developer comment: Every X days the equipment will be sent, regardless if still didn't produced all that has been requested.

- **REINFORCEMENT_REQUEST_DAYS_FREQUENCY**
  - Default: 7
  - Developer comment: How many days must pass until we may give another reinforcement request

- **EXPERIENCE_COMBAT_FACTOR**
  - Default: 0.25

- **UNIT_DIGIN_CAP**
  - Default: 5
  - Developer comment: how "deep" you can dig you can dig in until hitting max bonus

- **UNIT_DIGIN_SPEED**
  - Default: 1
  - Developer comment: how "deep" you can dig a day.

- **PARACHUTE_FAILED_EQUIPMENT_DIV**
  - Default: 50.0
  - Developer comment: When the transport plane was shot down, we drop unit with almost NONE equipment

- **PARACHUTE_FAILED_MANPOWER_DIV**
  - Default: 100.0
  - Developer comment: When the transport plane was shot down, we drop unit with almost NONE manpower

- **PARACHUTE_FAILED_STR_DIV**
  - Default: 10.0
  - Developer comment: When the transport plane was shot down, we drop unit with almost NONE strenght

- **PARACHUTE_DISRUPTED_EQUIPMENT_DIV**
  - Default: 1.5
  - Developer comment: When the transport plane was hit, we drop unit with reduced equipment. Penalty is higher as more hits was received (and AA guns was in the state).

- **PARACHUTE_DISRUPTED_MANPOWER_DIV**
  - Default: 1.9
  - Developer comment: When the transport plane was hit, we drop unit with reduced manpower. Penalty is higher as more hits was received (and AA guns was in the state).

- **PARACHUTE_DISRUPTED_STR_DIV**
  - Default: 2.2
  - Developer comment: When the transport plane was hit, we drop unit with reduced strength. Penalty is higher as more hits was received (and AA guns was in the state).

- **PARACHUTE_PENALTY_RANDOMNESS**
  - Default: 0.1
  - Developer comment: Random factor for str,manpower,eq penalties.

- **PARACHUTE_DISRUPTED_AA_PENALTY**
  - Default: 1
  - Developer comment: How much the Air defence in the state (from AA buildings level * air_defence) is scaled to affect overall disruption (equipment,manpower,str).

- **PARACHUTE_COMPLETE_ORG**
  - Default: 0.4
  - Developer comment: Organisation value (in %) after unit being dropped, regardless if failed, disrupted, or successful.

- **PARACHUTE_ORG_REGAIN_PENALTY_DURATION**
  - Default: 120
  - Developer comment: penalty in org regain after being parachuted. Value is in hours.

- **PARACHUTE_ORG_REGAIN_PENALTY_MULT**
  - Default: -0.8
  - Developer comment: penalty to org regain after being parachuted.

- **SHIP_MORALE_TO_ORG_REGAIN_BASE**
  - Default: 0.2
  - Developer comment: Base org regain per hour

- **BASE_NIGHT_ATTACK_PENALTY**
  - Default: -0.5

- **EXILE_EQUIPMENT**
  - Default: 1.0
  - Developer comment: Amount of equipment to keep

- **EXILE_ORG**
  - Default: 0.0
  - Developer comment: Amount of org to keep

- **EXPERIENCE_LOSS_FACTOR**
  - Default: 1.00
  - Developer comment: percentage of experienced solders who die when manpower is removed

- **EQUIPMENT_COMBAT_LOSS_FACTOR**
  - Default: 0.70
  - Developer comment: % of equipment lost to strength ratio in combat, so some % is returned if below 1

- **SUPPLY_USE_FACTOR_MOVING**
  - Default: 1.5
  - Developer comment: Deprecated/Unused

- **SUPPLY_USE_FACTOR_INACTIVE**
  - Default: 0.95
  - Developer comment: Deprecated/Unused

- **SUPPLY_GRACE**
  - Default: 72
  - Developer comment: troops always carry 3 days of food and supply

- **SUPPLY_GRACE_MAX_REDUCE_PER_HOUR**
  - Default: 2
  - Developer comment: supply grace is not decreased instantly when it is buffed temporarily and buff is removed

- **SUPPLY_ORG_MAX_CAP**
  - Default: 0.35
  - Developer comment: Max organization is factored by this if completely out of supply

- **MAX_OUT_OF_SUPPLY_DAYS**
  - Default: 30
  - Developer comment: how many days of shitty supply until max penalty achieved

- **OUT_OF_SUPPLY_ATTRITION**
  - Default: 0.2
  - Developer comment: max attrition when out of supply

- **OUT_OF_SUPPLY_SPEED**
  - Default: -0.8
  - Developer comment: max speed reduction from supply

- **NON_CORE_SUPPLY_SPEED**
  - Default: -0.5
  - Developer comment: we are not running on our own VP supply so need to steal stuff along the way

- **NON_CORE_SUPPLY_AIR_SPEED**
  - Default: -0.25
  - Developer comment: we are not running on our own VP supply so need to steal stuff along the way, a bit less due to air supply

- **OUT_OF_SUPPLY_MORALE**
  - Default: -0.2
  - Developer comment: max org regain reduction from supply

- **TRAINING_ATTRITION**
  - Default: 0.05
  - Developer comment: amount of extra attrition from being in training

- **TRAINING_MIN_STRENGTH**
  - Default: 0.1
  - Developer comment: if strength is less than this, the unit will pause training until it's been reinforced

- **TRAINING_MAX_DAILY_COUNTRY_EXP**
  - Default: 0.08
  - Developer comment: Maximum army XP gained per day from training

- **AIR_SUPPORT_BASE**
  - Default: 0.25
  - Developer comment: CAS bonus factor for air support moddifier for land unit in combat

- **LOW_SUPPLY**
  - Default: 0.99
  - Developer comment: When the supply status of an unit becomes low.

- **BORDER_WAR_ATTRITION_FACTOR**
  - Default: 0.1
  - Developer comment: How much of borderwar balance of power makes it into attrition

- **BORDER_WAR_VICTORY**
  - Default: 0.8
  - Developer comment: At wich border war balance of power is victory declared

- **REINFORCE_CHANCE**
  - Default: 0.02
  - Developer comment: base chance to join combat from back line when empty

- **SPEED_REINFORCEMENT_BONUS**
  - Default: 0.01
  - Developer comment: chance to join combat bonus by each 100% larger than infantry base (up to 200%)

- **OVERSEAS_LOSE_EQUIPMENT_FACTOR**
  - Default: 0.75
  - Developer comment: percentage of equipment lost disbanded overseas

- **NAVAL_TRANSFER_DISBAND_MANPOWER_FACTOR**
  - Default: 0.5
  - Developer comment: percentage of manpower returned when a naval transfering unit is disbanded

- **ENCIRCLED_DISBAND_MANPOWER_FACTOR**
  - Default: 0.2
  - Developer comment: percentage of manpower returned when an encircled unit is disbanded

- **ORG_LOSS_FACTOR_ON_CONQUER**
  - Default: 0.2
  - Developer comment: percentage of (max) org loss on takign enemy province

- **LOW_ORG_FOR_ATTACK**
  - Default: 0.3
  - Developer comment: at what org % we start affecting speed when doign hostile moves. scales down ZERO_ORG_MOVEMENT_MODIFIER

- **PLANNING_DECAY**
  - Default: 0.01

- **PLAYER_ORDER_PLANNING_DECAY**
  - Default: 0.03
  - Developer comment: Amount of planning lost due to player manual order

- **PLANNING_GAIN**
  - Default: 0.02

- **NAVAL_INVASION_PLANNING_BONUS_GAIN**
  - Default: 0.02
  - Developer comment: Planning Bonus gain per day for naval invasions

- **NAVAL_INVASION_PLANNING_BONUS_MALUS**
  - Default: -1
  - Developer comment: Malus in percentage for the planning bonus gain for naval invasions

- **PLANNING_MAX**
  - Default: 0.3
  - Developer comment: can get more from techs

- **CIVILWAR_ORGANIZATION_FACTOR**
  - Default: 0.3
  - Developer comment: Multiplier of org for both sides when civilwar.

- **PLAN_CONSIDERED_GOOD**
  - Default: 0.25
  - Developer comment: Plan evaluations above this value are considered more or less safe

- **PLAN_CONSIDERED_BAD**
  - Default: -0.25
  - Developer comment: Plan evaluations below this value are considered unsafe

- **PLAN_MIN_AUTOMATED_EMPTY_POCKET_SIZE**
  - Default: 2
  - Developer comment: The battle plan system will only automatically attack provinces in pockets that has no resistance and are no bigger than these many provinces

- **PLAN_SPREAD_ATTACK_WEIGHT**
  - Default: 12.0
  - Developer comment: The higher the value, the less it should crowd provinces with multiple attacks.

- **PLAN_NEIGHBORING_ENEMY_PROVINCE_FACTOR**
  - Default: 0.7
  - Developer comment: When calculating the importance of provinces, it takes number of enemy provinces into account, factored by this

- **PLAN_PROVINCE_BASE_IMPORTANCE**
  - Default: 2.0
  - Developer comment: Used when calculating the calue of front and defense area provinces for the battle plan system

- **PLAN_PROVINCE_LOW_VP_IMPORTANCE_AREA**
  - Default: 2.0
  - Developer comment: Used when calculating the value of defense area in the battle plan system

- **PLAN_PROVINCE_MEDIUM_VP_IMPORTANCE_AREA**
  - Default: 5.0
  - Developer comment: Used when calculating the value of defense area in the battle plan system

- **PLAN_PROVINCE_HIGH_VP_IMPORTANCE_AREA**
  - Default: 10.0
  - Developer comment: Used when calculating the value of defense area in the battle plan system

- **PLAN_PROVINCE_CAPITAL_IMPORTANCE_AREA**
  - Default: 50.0
  - Developer comment: Used when calculating the balue of defense area in the battle plan system

- **MIN_VP_NEEDED_FOR_DEFENSE_ORDER_ASSIGNMENTS**
  - Default: 1.0
  - Developer comment: If a province has more than this VP, unit controller will try to assign units that prov

- **PLAN_PROVINCE_LOW_VP_IMPORTANCE_FRONT**
  - Default: 2.0
  - Developer comment: Used when calculating the calue of fronts in the battle plan system

- **PLAN_PROVINCE_MEDIUM_VP_IMPORTANCE_FRONT**
  - Default: 2.25
  - Developer comment: Used when calculating the calue of fronts in the battle plan system

- **PLAN_PROVINCE_HIGH_VP_IMPORTANCE_FRONT**
  - Default: 2.75
  - Developer comment: Used when calculating the calue of fronts in the battle plan system

- **PLAN_SHARED_FRONT_PROV_IMPORTANCE_FACTOR**
  - Default: 0.8
  - Developer comment: If fornt orders share end provinces, they should each have a somewhat reduced prio due to it being shared.

- **PLAN_PORVINCE_PORT_BASE_IMPORTANCE**
  - Default: 12.0
  - Developer comment: Added importance for area defense province with a port

- **PLAN_PORVINCE_PORT_LEVEL_FACTOR**
  - Default: 1.5
  - Developer comment: Bonus factor for port level

- **PLAN_PORVINCE_AIRFIELD_BASE_IMPORTANCE**
  - Default: 3.0
  - Developer comment: Added importance for area defense province with air field

- **PLAN_PORVINCE_AIRFIELD_POPULATED_FACTOR**
  - Default: 1.5
  - Developer comment: Bonus factor when an airfield has planes on it

- **PLAN_PORVINCE_AIRFIELD_LEVEL_FACTOR**
  - Default: 0.25
  - Developer comment: Bonus factor for airfield level

- **PLAN_PORVINCE_RESISTANCE_BASE_IMPORTANCE**
  - Default: 10.0
  - Developer comment: Used when calculating the calue of defense area provinces for the battle plan system (factored by resistance level)

- **PLAN_PROVINCE_VP_PORT_FACTOR**
  - Default: 0.25

- **PLAN_AREA_DEFENSE_ENEMY_CONTROLLER_SCORE**
  - Default: 25.0
  - Developer comment:
    ```text
    These need to result in province value > 1.0 for it to matter.
    Score applied to provinces in the defense area order controlled by enemies
    ```

- **PLAN_AREA_DEFENSE_ENEMY_UNIT_FACTOR**
  - Default: -2.0
  - Developer comment: Factor applied to province score in area defense order per enemy unit in that province

- **PLAN_AREA_DEFENSE_FORT_IMPORTANCE**
  - Default: 0.25
  - Developer comment: Used when calculating the value of defense area provinces for the battle plan system, works as multipliers on the rest

- **PLAN_AREA_DEFENSE_COASTAL_FORT_IMPORTANCE**
  - Default: 3.0
  - Developer comment: Used when calculating the value of defense area provinces for the battle plan system

- **PLAN_AREA_DEFENSE_COAST_NO_FORT_IMPORTANCE**
  - Default: 1.1
  - Developer comment: Used when calculating the value of defense area provinces for the battle plan system

- **PLAN_AREA_DEFENSE_HAS_RAIL_IMPORTANCE**
  - Default: 1.5
  - Developer comment: Used when calculating the value of defense area provinces for the battle plan system

- **PLAN_AREA_DEFENSE_HAS_SUPPLY_NODE**
  - Default: 20.0
  - Developer comment: Used when calculating the value of defense area provinces for the battle plan system

- **PLAN_STICKINESS_FACTOR**
  - Default: 100.0
  - Developer comment: Factor used in unitcontroller when prioritizing units for locations

- **PLAN_PROVINCE_PRIO_DISTRIBUTION_MIN**
  - Default: 0.7
  - Developer comment: Lowest fraction of divisions that will be distributed based on province priority

- **PLAN_PROVINCE_PRIO_DISTRIBUTION_MAX**
  - Default: 1.0
  - Developer comment: Highest fraction of divisions that will be distributed based on province priority

- **PLAN_PROVINCE_PRIO_DISTRIBUTION_DPP_HIGH**
  - Default: 3.0
  - Developer comment: At what divisions per province should we use PLAN_PROVINCE_PRIO_DISTRIBUTION_MIN

- **PLAN_PROVINCE_PRIO_DISTRIBUTION_DPP_LOW**
  - Default: 2.0
  - Developer comment: At what divisions per province should we use PLAN_PROVINCE_PRIO_DISTRIBUTION_MAX

- **PLAN_EXECUTE_CAREFUL_LIMIT**
  - Default: 25
  - Developer comment: When looking for an attach target, this score limit is required in the battle plan to consider province for attack

- **PLAN_EXECUTE_BALANCED_LIMIT**
  - Default: 0
  - Developer comment: When looking for an attach target, this score limit is required in the battle plan to consider province for attack

- **PLAN_EXECUTE_RUSH**
  - Default: -200
  - Developer comment: When looking for an attach target, this score limit is required in the battle plan to consider province for attack

- **PLAN_EXECUTE_CAREFUL_MAX_FORT**
  - Default: 5
  - Developer comment: If execution mode is set to careful, units will not attack provinces with fort levels greater than or equal to this

- **PLAN_EXECUTE_SUPPLY_CHECK**
  - Default: { 1.0, 0.0, 0.0, 1.0, 0.0 }
  - Developer comment:
    ```text
    order by EExecutionType: careful, balanced, rush, <skip>, rush_weak
    for each execution mode how careful should we be with supply (1.0 means full required supply available, zero is no limit).
    ```

- **PLAN_MAX_PROGRESS_TO_JOIN**
  - Default: 0.50
  - Developer comment: If Lower progress than this, probably needs support

- **PLAN_COHESION_WEIGHTS**
  - Default: { 1.0, 40.0, 80.0 }
  - Developer comment: for each cohesion setting, how keen on relocating from distance should we be? (default 1.0), higher weight = shorter max distance

- **PLAN_COHESION_DISTANCE_MAX_WHEN_LEFT_BEHIND**
  - Default: 38
  - Developer comment: Unused and deprecated - will be removed in next major version.

- **PLAN_BLITZ_OPTIMISM**
  - Default: 0.2
  - Developer comment: Additional combat balance value in favor of blitzing side when considering targets (not a combat bonus, just offsets planning)

- **MIN_BALANCE_SCORE_TO_PROCEED_ATTACK**
  - Default: 0.2
  - Developer comment: A combat balance score of less than this will prevent auto attacking

- **DYNAMIC_MODIFIER_ATTACK_BIAS**
  - Default: 1.0
  - Developer comment: This factors the weighting bias of dynamic attack modifiers

- **FLANKED_PROVINCES_COUNT**
  - Default: 3
  - Developer comment: Attacker has to attack from that many provinces for the attack to be considered as flanking

- **NUKE_MIN_DAMAGE_PERCENT**
  - Default: 0.1
  - Developer comment: Minimum damage from nukes as a percentage of current strength/organisation

- **NUKE_MAX_DAMAGE_PERCENT**
  - Default: 0.9
  - Developer comment: Minimum damage from nukes as a percentage of current strength/organisation

- **EQUIPMENT_REPLACEMENT_RATIO**
  - Default: 0.1
  - Developer comment: Equipment min ratio after blocking the equipment type

- **NUKE_DELAY_HOURS**
  - Default: 2
  - Developer comment: How many hours does it take for the nuclear drop to happen

- **PARADROP_PENALTY**
  - Default: -0.3
  - Developer comment: Combat penalty when recently paradropped

- **PARADROP_HOURS**
  - Default: 48
  - Developer comment: time paratroopers suffer penalties in combat

- **COMBAT_SUPPLY_LACK_ATTACKER_ATTACK**
  - Default: -0.25
  - Developer comment: attack combat penalty for attacker if out of supply

- **COMBAT_SUPPLY_LACK_ATTACKER_DEFEND**
  - Default: -0.65
  - Developer comment: defend combat penalty for attacker if out of supply

- **COMBAT_SUPPLY_LACK_DEFENDER_ATTACK**
  - Default: -0.35
  - Developer comment: attack combat penalty for defender if out of supply

- **COMBAT_SUPPLY_LACK_DEFENDER_DEFEND**
  - Default: -0.15
  - Developer comment: defend combat penalty for defender if out of supply

- **COMBAT_STACKING_START**
  - Default: 5
  - Developer comment: at what nr of divisions stacking penalty starts

- **COMBAT_STACKING_EXTRA**
  - Default: 3
  - Developer comment: extra stacking from directions

- **COMBAT_STACKING_PENALTY**
  - Default: -0.02
  - Developer comment: how much stackign penalty per division

- **COMBAT_OVER_WIDTH_PENALTY**
  - Default: -1
  - Developer comment: over combat width penalty per %.

- **COMBAT_OVER_WIDTH_PENALTY_MAX**
  - Default: -0.33
  - Developer comment: over combat width max (when you cant join no more).

- **RETREAT_SPEED_FACTOR**
  - Default: 0.25
  - Developer comment: speed bonus when retreating

- **WITHDRAWING_SPEED_FACTOR**
  - Default: 0.15
  - Developer comment: speed bonus when withdrawing

- **STRATEGIC_SPEED_INFRA_BASE**
  - Default: 5.0
  - Developer comment: Base speed of strategic redeployment when not on railways

- **STRATEGIC_SPEED_INFRA_MAX**
  - Default: 10.0
  - Developer comment: Additional speed of strategic redeployment on max-level infrastructure

- **STRATEGIC_SPEED_RAIL_BASE**
  - Default: 15.0
  - Developer comment: Base speed of strategic redeployment when on railways

- **STRATEGIC_SPEED_RAIL_MAX**
  - Default: 25.0
  - Developer comment: Additional speed of strategic redeployment on max-level railways

- **STRATEGIC_REDEPLOY_ORG_RATIO**
  - Default: 0.1
  - Developer comment: Ratio of max org while strategic redeployment

- **BATALION_NOT_CHANGED_EXPERIENCE_DROP**
  - Default: 0.0
  - Developer comment: Division experience drop if unit has same batalion

- **BATALION_CHANGED_EXPERIENCE_DROP**
  - Default: 0.5
  - Developer comment: Division experience drop if unit has different batalion

- **ARMOR_VS_AVERAGE**
  - Default: 0.4
  - Developer comment: how to weight in highest armor & pen vs the division average

- **PEN_VS_AVERAGE**
  - Default: 0.4

- **LAND_EQUIPMENT_BASE_COST**
  - Default: 10
  - Developer comment: Cost in XP to upgrade a piece of equipment one level is base + ( total levels * ramp )

- **LAND_EQUIPMENT_RAMP_COST**
  - Default: 5

- **NAVAL_EQUIPMENT_BASE_COST**
  - Default: 25

- **NAVAL_EQUIPMENT_RAMP_COST**
  - Default: 5

- **AIR_EQUIPMENT_BASE_COST**
  - Default: 25

- **AIR_EQUIPMENT_RAMP_COST**
  - Default: 5

- **FASTER_ORG_REGAIN_LEVEL**
  - Default: 0.25

- **FASTER_ORG_REGAIN_MULT**
  - Default: 1.0

- **SLOWER_ORG_REGAIN_LEVEL**
  - Default: 0.80

- **SLOWER_ORG_REGAIN_MULT**
  - Default: -0.5

- **DISBAND_MANPOWER_LOSS**
  - Default: 0.0

- **MIN_DIVISION_DEPLOYMENT_TRAINING**
  - Default: 0.2
  - Developer comment: Min level of division training

- **FRONTLINE_EXPANSION_FACTOR**
  - Default: 0.6
  - Developer comment: When attacking along a frontline, how much should units spread out as they advance. 0.0 means head (more or less) directly to the drawn frontline, with no distractions

- **FRONT_MIN_PATH_TO_REDEPLOY**
  - Default: 8
  - Developer comment: If a units path is at least this long to reach its front location, it will strategically redeploy.

- **ARMY_INITIATIVE_REINFORCE_FACTOR**
  - Default: 0.25
  - Developer comment: scales initiative for reinforce chance

- **BASE_CAPTURE_EQUIPMENT_RATIO**
  - Default: 0.0
  - Developer comment: after a successful land combat, ratio of the equipments that are being captured/salvaged from enemy's lost equipment

- **ACCLIMATIZATION_IN_COMBAT_SPEED_FACTOR**
  - Default: 3
  - Developer comment: Acclimatization speed multiplier while being in combat.

- **ACCLIMATIZATION_SPEED_GAIN**
  - Default: 0.15
  - Developer comment: A variable used to balance the overall speed of gaining the acclimatization

- **ACCLIMATIZATION_LOSS_SPEED_FACTOR**
  - Default: 2.0
  - Developer comment: Loosing one acclimatization while being under affect of the opposite climate should cause it to drop down much faster than gaining.

- **PROMOTE_LEADER_CP_COST**
  - Default: 40.0
  - Developer comment: cost of promoting a leader

- **FIELD_MARSHAL_ARMY_BONUS_RATIO**
  - Default: 0.5
  - Developer comment: ratio to apply regular bonuses FM bonuses to armies

- **FIELD_MARSHAL_XP_RATIO**
  - Default: 0.3
  - Developer comment: xp gain ratio for army group leaders

- **GARRISON_ORDER_ARMY_CAP_FACTOR**
  - Default: 3.0
  - Developer comment: armies gets increased cap when they are garrisoned

- **COMMANDER_LEVEL_UP_STAT_COUNT**
  - Default: 3
  - Developer comment: num stats gained on level up

- **COMMANDER_LEVEL_UP_STAT_WEIGHTS**
  - Default: { 5, 5, 5, 5 }
  - Developer comment: level up stat random base weights attack, defense, planning, logistics

- **NAVY_LEADER_LEVEL_UP_STAT_WEIGHTS**
  - Default: { 5, 5, 5, 5 }
  - Developer comment: level up stat random base weights attack, defense, maneuvering, coordination

- **UNIT_LEADER_INITIAL_TRAIT_SLOT**
  - Default: { 1.0, 0.0, 1.0, 0.0 }
  - Developer comment:
    ```text
    trait slot for 0 level leader
    field marshal
    corps commander
    navy general
    operative
    ```

- **UNIT_LEADER_TRAIT_SLOT_PER_LEVEL**
  - Default: { 0.5, 0.5, 0.5, 0.0 }
  - Developer comment:
    ```text
    num extra traits on each level
    field marshal
    corps commander
    navy general
    operative
    ```

- **UNIT_LEADER_USE_NONLINEAR_XP_GAIN**
  - Default: true
  - Developer comment: Whether unit leader XP gain is scaled by 1/<nr_of_traits>

- **HOURS_REQ_REJOIN_BORDER_WAR_FOR_INJURED_UNITS**
  - Default: 1
  - Developer comment: minimum hours required for units to rejoin border wars, values below zero will make units never return

- **NEW_COMMANDER_RANDOM_PERSONALITY_TRAIT_CHANCES**
  - Default: { 0.5, 0.15 }
  - Developer comment:
    ```text
    chances to gain a personality trait for new generals
    50% for first trait
    15% for second trait after that
    ```

- **NEW_COMMANDER_RANDOM_BASIC_TRAIT_CHANCES**
  - Default: {  }
  - Developer comment: chances to gain a basic trait for new generals

- **NEW_COMMANDER_RANDOM_STATUS_TRAIT_CHANCES**
  - Default: {  }
  - Developer comment: chances to gain a status trait for new generals

- **NEW_OPERATIVE_RANDOM_PERSONALITY_TRAIT_CHANCES**
  - Default: { 0.5, 0.1 }
  - Developer comment:
    ```text
    chances to gain a personality trait for new operatives
    50% for first trait
    10% for second trait after that
    ```

- **NEW_OPERATIVE_RANDOM_BASIC_TRAIT_CHANCES**
  - Default: { 0.25, 0.05 }
  - Developer comment:
    ```text
    chances to gain a basic trait for new operatives
    25% for first trait
    5% for second trait after that
    ```

- **NEW_OPERATIVE_RANDOM_STATUS_TRAIT_CHANCES**
  - Default: {  }
  - Developer comment: chances to gain a status trait for new operatives

- **NEW_COMMANDER_RANDOM_SKILL_CHANCES**
  - Default: {  }
  - Developer comment: chances to give a random stat skill for new operatives?

- **NEW_NAVY_LEADER_RANDOM_SKILL_CHANCES**
  - Default: {  }
  - Developer comment: chances to give a random stat skill point for a new admiral

- **UNIT_LEADER_MODIFIER_COOLDOWN_ON_GROUP_CHANGE**
  - Default: 15
  - Developer comment: time in days for a unit leader to regain its modifiers

- **UNIT_LEADER_ASSIGN_TRAIT_COST**
  - Default: 15.0
  - Developer comment: cost to assign a new trait to a unit leader

- **ATTACHED_WINGS_ORDER_UPDATE_DAYS**
  - Default: 5
  - Developer comment: Days untill the attached wing will update the order

- **BORDER_WAR_WIN_DAYS_AGAINST_EMPTY_OPPONENTS**
  - Default: 14
  - Developer comment: border wars will be automatically won if no opponent shows up for this duration

- **MAX_RELATIVE_COMBAT_DAMAGE_TO_MODIFY_XP**
  - Default: 4.0
  - Developer comment: you gain more XP if you are doing more damage relative to enemy, this is the max relative amount to gain following RATe

- **XP_GAIN_FACTOR_FOR_MAX_RELATIVE_COMBAT_DAMAGE**
  - Default: 4.0
  - Developer comment: XP factor scaling for max relative combat damage

- **XP_DECAY_RATE_PER_HOUR_IN_COMBAT**
  - Default: 0.03
  - Developer comment: you get reduced XP as combat drags

- **MIN_XP_RATE_TO_DECAY**
  - Default: 0.1
  - Developer comment: minimum XP factor for dragged combats

- **XP_GAIN_PER_OVERRUN_UNIT**
  - Default: 35.0
  - Developer comment: fixed XP gain per overrun unit

- **XP_GAIN_FOR_SHATTERING**
  - Default: 35.0
  - Developer comment: fixed XP gain per shattered unit

- **UNIT_UPKEEP_ATTRITION**
  - Default: 0.00
  - Developer comment: Constant attrition value applied to armies.

- **FUEL_PENALTY_START_RATIO**
  - Default: 0.25
  - Developer comment: ratio of fuel in an army to start getting penalties

- **SURPLUS_SUPPLY_RATIO_FOR_ZERO_FUEL_FLOW**
  - Default: 0.5
  - Developer comment: if a supply chunk has more supply needed than this ratio + 1 compared to its max supply flow, the units inside the chiunk will get no fuel

- **ARMY_MAX_FUEL_FLOW_MULT**
  - Default: 2.0
  - Developer comment: max fuel ratio that an army can get per hour, multiplied by supply situation

- **ARMY_FUEL_COST_MULT**
  - Default: 0.5
  - Developer comment: fuel cost multiplier for all army related stuff

- **ARMY_COMBAT_FUEL_MULT**
  - Default: 1.0
  - Developer comment: fuel consumption ratio in combat (plus ARMY_MOVEMENT_FUEL_MULT if you are also moving. ie offensive combat)

- **ARMY_TRAINING_FUEL_MULT**
  - Default: 1.0
  - Developer comment: fuel consumption ratio while training

- **ARMY_MOVEMENT_FUEL_MULT**
  - Default: 1.0
  - Developer comment: fuel consumption ratio while moving

- **ARMY_NAVAL_TRANSFER_FUEL_MULT**
  - Default: 0.0
  - Developer comment: fuel consumption ratio while naval transferring

- **ARMY_STRATEGIC_DEPLOYMENT_FUEL_MULT**
  - Default: 0.0
  - Developer comment: fuel consumption ratio while doing strategic deployment

- **ARMY_IDLE_FUEL_MULT**
  - Default: 0.0
  - Developer comment: fuel consumption ratio while just existing

- **FUEL_EFFICIENCY_RAID_MULTIPLIER**
  - Default: 1.0
  - Developer comment: convoy raid multiplier for fuel sunk

- **FUEL_FLOW_PENALTY_FOR_SUPPLY_CHUNK_EDGE_RATIO**
  - Default: 0.5
  - Developer comment: supply flow that is limited by control of incoming edge provinces will have lesser effect on fuel flow

- **OUT_OF_FUEL_EQUIPMENT_MULT**
  - Default: 0.1
  - Developer comment: ratio of the stats that you get from equipments that uses fuel and you lack it

- **OUT_OF_FUEL_SPEED_MULT**
  - Default: 0.4
  - Developer comment: speed mult that armies get when out of fuel

- **OUT_OF_FUEL_TRAINING_XP_GAIN_MULT**
  - Default: 0.0
  - Developer comment: xp gain mult from training when a unit is out of fuel

- **FUEL_CAPACITY_DEFAULT_HOURS**
  - Default: 96
  - Developer comment: default capacity if not specified

- **MAX_ESTIMATED_PLAN_UNITS_NOT_IN_PLACE_FACTOR**
  - Default: -0.6
  - Developer comment: Scaled by % of units not in place. Used to be a flat -50%

- **DAMAGE_SPLIT_ON_FIRST_TARGET**
  - Default: 0.35
  - Developer comment: % of damage dealt to the first target in a combat. The rest will be split amongst subsequent targets. Modifiers can affect this up to a maximum of 0.9. That value must not be exposed as a define.

- **NEW_ARMY_LEADER_LEVEL_CHANCES**
  - Default: { 0.95, 0.05 }
  - Developer comment:
    ```text
    chances for new army leaders to start at a given level
    95% for level one
    5% for level two
    0% for level three to ten
    ```

## NAir

- **AIR_WING_FLIGHT_SPEED_MULT**
  - Default: 0.02
  - Developer comment: Global speed multiplier for airplanes (affects fe.transferring to another base)

- **AIR_WING_MAX_STATS_ATTACK**
  - Default: 100
  - Developer comment: Max stats

- **AIR_WING_MAX_STATS_DEFENCE**
  - Default: 100

- **AIR_WING_MAX_STATS_AGILITY**
  - Default: 100

- **AIR_WING_MAX_STATS_SPEED**
  - Default: 800

- **AIR_WING_MAX_STATS_BOMBING**
  - Default: 100

- **AIR_WING_MAX_SIZE**
  - Default: 1000
  - Developer comment: Max amount of airplanes in wing

- **AIR_WING_AVERAGE_SIZE**
  - Default: 100
  - Developer comment: Eyeballed average amount of airplanes in wing. Used when calculating air volunteer.

- **AIR_WING_BOMB_DAMAGE_FACTOR**
  - Default: 2
  - Developer comment: Used to balance the damage done while bombing.

- **BIGGEST_AGILITY_FACTOR_DIFF**
  - Default: 4.0
  - Developer comment: biggest factor difference in agility for doing damage (caps to this)

- **BIGGEST_SPEED_FACTOR_DIFF**
  - Default: 3.5
  - Developer comment: biggest factor difference in speed for doing damage (caps to this)

- **TOP_SPEED_DAMAGE_BONUS_FACTOR**
  - Default: 0.025
  - Developer comment: A factor for scaling the top speed of a plane into damage buff. If an attacking wing has a speed advantage of any form their speed value will be converted into a percentage bonus with this modifier

- **COMBAT_DAMAGE_STATS_MULTILPIER**
  - Default: 0.2

- **COMBAT_BETTER_AGILITY_DAMAGE_REDUCTION**
  - Default: 0.45
  - Developer comment: How much the better agility (than opponent's) can reduce their damage to us.

- **COMBAT_BETTER_SPEED_DAMAGE_INCREASE**
  - Default: 0.65
  - Developer comment:
    ```text
    How much the better Speed (than opponent's) can reduce increase our damage to them.
    Both of these defines are combined with their sister FACTOR_DIFF defines to create defense or offensive buffs
    In both cases the maximum bonus or reduction is (BIGGEST_X_FACTOR_DIFF - 1) * COMBAT_BETTER_X_DAMAGE_Y * Damage
    ```

- **COMBAT_MAX_WINGS_AT_ONCE**
  - Default: 10000
  - Developer comment: Max amount of air wings in one combat simulation. The higher value, the quicker countries may loose their wings. It's a gameplay balance value.
  - Usage: Deprecated/Unused

- **COMBAT_MAX_WINGS_AT_GROUND_ATTACK**
  - Default: 10000
  - Developer comment: we can really pounce a land strike and escalate
  - Usage: Deprecated/Unused

- **COMBAT_MAX_WINGS_AT_ONCE_PORT_STRIKE**
  - Default: 10000
  - Developer comment: we can really pounce a naval strike and escalate
  - Usage: Deprecated/Unused

- **AIR_REGION_SUPERIORITY_PIXEL_SCALE**
  - Default: 0.04
  - Developer comment: air superiority scale = superiority/(pixels*this)

- **COMBAT_MULTIPLANE_CAP**
  - Default: 3.0
  - Developer comment: How many planes can shoot at each plane on other side ( if there are 100 planes we are atttacking COMBAT_MULTIPLANE_CAP * 100 of our planes can shoot )

- **COMBAT_DAMAGE_SCALE**
  - Default: 1
  - Developer comment: Higher value = more shot down planes

- **COMBAT_DAMAGE_SCALE_CARRIER**
  - Default: 5
  - Developer comment: same as above but used inside naval combat for carrier battles

- **DETECT_CHANCE_FROM_OCCUPATION**
  - Default: 0.10
  - Developer comment: How much the controlled provinces in area affects the air detection base value.

- **DETECT_CHANCE_FROM_RADARS**
  - Default: 0.5
  - Developer comment: How much the radars in area affects detection chance.

- **DETECT_CHANCE_FROM_AIRCRAFTS_EFFECTIVE_COUNT**
  - Default: 3000
  - Developer comment: Max amount of aircrafts in region to give full detection bonus.

- **DETECT_CHANCE_FROM_AIRCRAFTS**
  - Default: 0.8
  - Developer comment: How much aircrafts in region improves air detection (up to effective count).

- **DETECT_CHANCE_FROM_NIGHT**
  - Default: -0.2
  - Developer comment: How much the night can reduce the air detection. (see static modifiers to check how weather affects it too.)

- **DETECT_EFFICIENCY_BASE**
  - Default: 0.1
  - Developer comment: Base value for detection efficiency (once something detected, efficiency says how many airplanes was detected).

- **DETECT_EFFICIENCY_FROM_RADAR**
  - Default: 0.7
  - Developer comment: How much radars affect the efficiency.

- **DETECT_EFFICIENCY_RANDOM_FACTOR**
  - Default: 0.1
  - Developer comment: How much randomness is in amount of detected aircrafts.

- **DAY_NIGHT_COVERAGE_FACTOR**
  - Default: 0.5
  - Developer comment: The max night coverage in a region that is still considered to be day-time when determining if day/night air missions shall run.

- **HOURS_DELAY_AFTER_EACH_COMBAT**
  - Default: 4
  - Developer comment: How many hours needs the wing to be ready for the next combat. Use for tweaking if combats happens too often. (generally used as double because of roundtrip)

- **PORT_STRIKES_DELAY_MULTIPLIER**
  - Default: 2
  - Developer comment: multplies HOURS_DELAY_AFTER_EACH_COMBAT if port strikes

- **CARRIER_HOURS_DELAY_AFTER_EACH_COMBAT**
  - Default: 3
  - Developer comment: how often carrier planes do battle inside naval combat

- **CARRIER_SIZE_STAT_INCREMENT**
  - Default: 10
  - Developer comment: Each Point of carrier_size state adds capacity for this many planes

- **NAVAL_STRIKE_TARGETTING_TO_AMOUNT**
  - Default: 0.3
  - Developer comment: Balancing value to convert the naval_strike_targetting equipment stats to chances of how many airplanes managed to do successfull strike.

- **NAVAL_STRIKE_DAMAGE_TO_STR**
  - Default: 1.0
  - Developer comment: Balancing value to convert damage ( naval_strike_attack * hits ) to Strength reduction.

- **NAVAL_STRIKE_DAMAGE_TO_ORG**
  - Default: 1.5
  - Developer comment: Balancing value to convert damage ( naval_strike_attack * hits ) to Organisation reduction.

- **NAVAL_STRIKE_CARRIER_MULTIPLIER**
  - Default: 10.0
  - Developer comment: damage bonus when planes are in naval combat where their carrier is present (and can thus sortie faster and more effectively)

- **FIELD_EXPERIENCE_SCALE**
  - Default: 0.0004

- **FIELD_EXPERIENCE_MAX_PER_DAY**
  - Default: 2
  - Developer comment: Most xp you can gain per day

- **CLOSE_AIR_SUPPORT_EXPERIENCE_SCALE**
  - Default: 0.0005
  - Developer comment: How much the experinence gained by CAS is scaled

- **PARADROP_EXPERIENCE_SCALE**
  - Default: 0.03
  - Developer comment: How much the experinence gained by paradropping is scaled

- **BOMBING_DAMAGE_EXPERIENCE_SCALE**
  - Default: 0.0002
  - Developer comment: How much the experinence gained by bombing is scaled

- **EXPERIENCE_SCALE_ATTACK_LOGISTICS_NO_TRUCK_CONSUMERS**
  - Default: 0.0001
  - Developer comment: How much country experinence gained by attacking consumers who aren't motorized

- **EXPERIENCE_SCALE_ATTACK_LOGISTICS_NODE_AND_TRAINS**
  - Default: 0.0002
  - Developer comment: How much country experinence gained by attacking node/trains

- **EXPERIENCE_SCALE_ATTACK_LOGISTICS_TRUCKS**
  - Default: 0.0002
  - Developer comment: How much country experinence gained by attacking trucks

- **FIELD_EXPERIENCE_FACTOR**
  - Default: 0.7
  - Developer comment: Factor all air experience gain from missions by this

- **AI_ALLOWED_PLANES_KEPT_IN_RESERVE**
  - Default: 0.10
  - Developer comment: AI allowed planes is reduced by this percentage. Overflow will be distributed to the next valid order. Worst case, this will result in this % of planes no being assigned any order.

- **ACCIDENT_CHANCE_BASE**
  - Default: 0.1
  - Developer comment: Base chance % (0 - 100) for accident to happen. Reduced with higher reliability stat.

- **ACCIDENT_CHANCE_CARRIER_MULT**
  - Default: 1.5
  - Developer comment: The total accident chance is scaled up when it happens on the carrier ship.

- **ACCIDENT_CHANCE_BALANCE_MULT**
  - Default: 0.10
  - Developer comment: Multiplier for balancing how often the air accident really happens. The higher mult, the more often.

- **ACCIDENT_CHANCE_RELIABILITY_MULT**
  - Default: 2.0
  - Developer comment: Multiplier to accident chance per point of missing reliability.

- **ACCIDENT_EFFECT_MULT**
  - Default: 0.007
  - Developer comment: Multiplier for balancing the effect of accidents

- **ACE_DEATH_CHANCE_BASE**
  - Default: 0.005
  - Developer comment: Base chance % for ace pilot die when an airplane is shot down in the Ace wing.

- **ACE_DEATH_BY_OTHER_ACE_CHANCE**
  - Default: 1.0
  - Developer comment: chance to an ace dying by another ace if it was hit by ace in combat

- **ACE_DEATH_CHANCE_PLANES_MULT**
  - Default: 0.001
  - Developer comment: The more airplanes was lost in a single airplanes (more bloody it was) the higher chance of Ace to die.

- **AIR_AGILITY_TO_NAVAL_STRIKE_AGILITY**
  - Default: 0.02
  - Developer comment: conversion factor to bring agility in line with ship AA

- **ACE_EARN_CHANCE_BASE**
  - Default: 0.01
  - Developer comment: Base chance % for ace pilot creation roll to happen. Happens only when successfully kill airplane/ship or damage the buildings.

- **ACE_EARN_CHANCE_PLANES_MULT**
  - Default: 0.005
  - Developer comment: Ace generation chance per aircraft. Chance is rolled twice because decimal numbers can't be small enough

- **AIR_DAMAGE_TO_DIVISION_LOSSES**
  - Default: 1.0
  - Developer comment: factor for conversion air damage to division losses for details statistics of air wings

- **AIR_NAVAL_KAMIKAZE_DAMAGE_MULT**
  - Default: 20.0
  - Developer comment: Balancing value to increase usual damage to Strength for Kamikaze

- **AIR_NAVAL_KAMIKAZE_LOSSES_MULT**
  - Default: 4.0
  - Developer comment: Balancing value to increase usual losses if Kamikaze participating in the battle

- **BASE_KAMIKAZE_DAMAGE**
  - Default: 2.0
  - Developer comment: Base Kamikaze death rate

- **BASE_KAMIKAZE_TARGETING**
  - Default: 2.0
  - Developer comment: Kamikaze can't be a bad target

- **BASE_STRATEGIC_BOMBING_HIT_SHIP_CHANCE**
  - Default: 0.01
  - Developer comment: Chance to hit a ship in port when it is bombed.

- **BASE_STRATEGIC_BOMBING_HIT_SHIP_DAMAGE_FACTOR**
  - Default: 50

- **BASE_STRATEGIC_BOMBING_HIT_PLANE_CHANCE**
  - Default: 0.5
  - Developer comment: Chance to hit a plane in airbase when it is bombed.

- **BASE_STRATEGIC_BOMBING_HIT_PLANE_DAMAGE_FACTOR**
  - Default: 0.2

- **STRATEGIC_BOMBER_NUKE_AIR_SUPERIORITY**
  - Default: 0.75
  - Developer comment: How much air superiority is needed for a tactical bomber to be able to nuke a province

- **AGGRESSION_THRESHOLD**
  - Default: { 0.0, 0.25, 0.5 }
  - Developer comment: Threshold levels for mission aggressivity for air

- **ACE_WING_SIZE**
  - Default: 100
  - Developer comment: size of wing ace bonuses are set up for. if lower more bonus, if higher less bonus

- **ACE_WING_SIZE_MAX_BONUS**
  - Default: 2
  - Developer comment: biggest bonus we can get from having a small wing with an ace on

- **NO_SEARCH_MISSION_DETECT_FACTOR**
  - Default: -0.5
  - Developer comment: value of planes not on active search missions for detection

- **SUPPLY_NEED_FACTOR**
  - Default: 0.28
  - Developer comment: multiplies supply usage

- **SUPPLY_PRIO_FACTOR**
  - Default: 100.0
  - Developer comment: Effect of supply need per unit for target province picking for air supply

- **CAPACITY_PENALTY**
  - Default: 2
  - Developer comment: scales penalty of having overcrowded bases.

- **AIR_COMBAT_FINAL_DAMAGE_SCALE**
  - Default: 0.015
  - Developer comment: % how many max disrupted only planes are alloed to die in a single combat

- **AIR_COMBAT_FINAL_DAMAGE_PLANES**
  - Default: 50
  - Developer comment: scaling/control for when only very few planes exist to stop roundoff issues

- **AIR_COMBAT_FINAL_DAMAGE_PLANES_FACTOR**
  - Default: 0.1

- **AA_INDUSTRY_AIR_DAMAGE_FACTOR**
  - Default: -0.12
  - Developer comment: 5x levels = 60% defense from bombing

- **NAVAL_STRIKE_DETECTION_BALANCE_FACTOR**
  - Default: 0.5
  - Developer comment: Value used to scale the surface_visibility stats to balance the gameplay, so 100% detection chance still won't spam the strikes.

- **NAVAL_RECON_DETECTION_BALANCE_FACTOR**
  - Default: 0.5
  - Developer comment: Value used to scale the surface_visibility stats to balance the gameplay, so 100% detection chance still won't spam spotting.

- **LEND_LEASED_EQUIPMENT_EXPERIENCE_GAIN**
  - Default: 0.5
  - Developer comment: Value used for equipment

- **ANTI_AIR_PLANE_DAMAGE_FACTOR**
  - Default: 0.8
  - Developer comment: Anti Air Gun Damage factor

- **ANTI_AIR_PLANE_DAMAGE_CHANCE**
  - Default: 0.1
  - Developer comment: Anti Air Gun hit chance

- **ANTI_AIR_ATTACK_TO_DAMAGE_REDUCTION_FACTOR**
  - Default: 1.0
  - Developer comment: Balancing value to convert equipment stat anti_air_attack to the damage reduction modifier apply to incoming air attacks against units with AA.

- **ANTI_AIR_MAXIMUM_DAMAGE_REDUCTION_FACTOR**
  - Default: 0.75
  - Developer comment: Maximum damage reduction factor applied to incoming air attacks against units with AA.

- **AIR_DEPLOYMENT_DAYS**
  - Default: 2
  - Developer comment: Days to deploy one air wing

- **NAVAL_STRIKE_BASE_STR_TO_PLANES_RATIO**
  - Default: 0.03
  - Developer comment: Max airbombers to do port strike comparing to strength

- **NAVAL_COMBAT_EXTERNAL_PLANES_JOIN_RATIO**
  - Default: 0.05
  - Developer comment: Max planes that can join a combat comparing to the total strength of the ships

- **NAVAL_COMBAT_EXTERNAL_PLANES_JOIN_RATIO_PER_DAY**
  - Default: 0.2
  - Developer comment: max extra plane % that can join every day

- **NAVAL_COMBAT_EXTERNAL_PLANES_MIN_CAP**
  - Default: 20
  - Developer comment: Min cap for planes that can join naval combat

- **AIR_MORE_GROUND_CREWS_COST**
  - Default: 20.0
  - Developer comment: CP cost to maintain more ground crews

- **AIR_MORE_GROUND_CREWS_BOOST**
  - Default: 0.1
  - Developer comment: Efficienct boost for more ground crews

- **EFFICIENCY_REGION_CHANGE_PENALTY_FACTOR**
  - Default: 0.9
  - Developer comment: Penalty applied for changing region

- **EFFICIENCY_REGION_CHANGE_DAILY_GAIN_DEFAULT**
  - Default: 1
  - Developer comment:
    ```text
    Gain should be changed in increments of 0.024 due to precision.
    Default how much efficiency to regain per day. Gain applied hourly.
    ```

- **EFFICIENCY_REGION_CHANGE_DAILY_GAIN_CAS**
  - Default: 0.888
  - Developer comment: How much efficiency to regain per day. Gain applied hourly.

- **EFFICIENCY_REGION_CHANGE_DAILY_GAIN_NAVAL_BOMBER**
  - Default: 0.192
  - Developer comment: How much efficiency to regain per day. Gain applied hourly.

- **EFFICIENCY_REGION_CHANGE_DAILY_GAIN_TACTICAL_BOMBER**
  - Default: 0.192
  - Developer comment: How much efficiency to regain per day. Gain applied hourly.

- **EFFICIENCY_REGION_CHANGE_DAILY_GAIN_FIGHTER**
  - Default: 0.888
  - Developer comment: How much efficiency to regain per day. Gain applied hourly.

- **EFFICIENCY_REGION_CHANGE_DAILY_GAIN_STRATEGIC_BOMBER**
  - Default: 0.072
  - Developer comment: How much efficiency to regain per day. Gain applied hourly.

- **EFFICIENCY_REGION_CHANGE_DAILY_GAIN_MARITIME_PATROL_PLANE**
  - Default: 1

- **AIR_WING_XP_MAX**
  - Default: 1000.0
  - Developer comment: Per plane XP.

- **AIR_WING_XP_LEVELS**
  - Default: { 100, 300, 700, 900 }
  - Developer comment: Experience needed to progress to the next level

- **AIR_WING_XP_LOSS_WHEN_KILLED**
  - Default: 300
  - Developer comment: if a plane dies, the game assumes that a pilot with this amount of xp died and recalcs average.

- **AIR_WING_XP_TRAINING_MAX**
  - Default: 300.0
  - Developer comment: Max average XP achieved with training.

- **AIR_WING_XP_TRAINING_MISSION_GAIN_DAILY**
  - Default: 7.0
  - Developer comment: Daily gain when running training exercise mission

- **AIR_WING_XP_AIR_VS_AIR_COMBAT_GAIN**
  - Default: 0.8
  - Developer comment: Wings in combat gain extra XP

- **AIR_WING_XP_GROUND_MISSION_COMPLETED_GAIN**
  - Default: 0.28
  - Developer comment: Bombers bombing, CAS cassing, NBs nbing, kamikazees kamikazeeing, etc.

- **AIR_WING_XP_RECON_MISSION_COMPLETED_GAIN**
  - Default: 0.05
  - Developer comment: recon mission

- **AIR_WING_COUNTRY_XP_FROM_TRAINING_FACTOR**
  - Default: 0.003
  - Developer comment: Factor on country Air XP gained from wing training

- **AIR_WING_XP_TRAINING_MISSION_ACCIDENT_FACTOR**
  - Default: 0.2
  - Developer comment: Training exercises cause more accidents

- **AIR_WING_XP_LOSS_REDUCTION_OVER_FRIENDLY_TERRITORY_FACTOR**
  - Default: 0.3
  - Developer comment: Reduction on XP loss over friendly territory

- **DISRUPTION_FACTOR**
  - Default: 4.0
  - Developer comment: multiplier on disruption damage to scale its effects on planes

- **DISRUPTION_FACTOR_CARRIER**
  - Default: 6.0
  - Developer comment: multiplier on disruption damage to scale its effects on carrier vs carrier planes

- **DISRUPTION_SPEED_FACTOR**
  - Default: 1.0

- **DISRUPTION_AGILITY_FACTOR**
  - Default: 0.0

- **DISRUPTION_ATTACK_FACTOR**
  - Default: 0.0

- **DISRUPTION_DETECTION_FACTOR**
  - Default: 1.0

- **ESCORT_FACTOR**
  - Default: 2.0

- **ESCORT_SPEED_FACTOR**
  - Default: 1.0

- **ESCORT_AGILITY_FACTOR**
  - Default: 1.0

- **ESCORT_ATTACK_FACTOR**
  - Default: 1.0

- **DISRUPTION_DEFENCE_DEFENCE_FACTOR**
  - Default: 0.5

- **DISRUPTION_DEFENCE_SPEED_FACTOR**
  - Default: 1.0

- **DISRUPTION_DEFENCE_ATTACK_FACTOR**
  - Default: 0.5

- **CARRIER_PLANES_AMOUNT_FOR_POSITIONING**
  - Default: 50
  - Developer comment: below this amount of planes on a carrier we no longer get max benefit on enemy positioning

- **CAS_NIGHT_ATTACK_FACTOR**
  - Default: 0.1
  - Developer comment: CAS damaged get multiplied by this in land combats at night

- **AIR_WING_ATTACK_LOGISTICS_NO_TRUCK_DISRUPTION_FACTOR**
  - Default: 0.02
  - Developer comment: If a unit isn't motorized, still disrupt its supply by damage * this

- **AIR_WING_ATTACK_LOGISTICS_TRUCK_DAMAGE_FACTOR**
  - Default: 0.27

- **AIR_WING_ATTACK_LOGISTICS_INFRA_DAMAGE_SPILL_FACTOR**
  - Default: 0.0016
  - Developer comment: Portion of truck damage to additionally deal to infrastructure

- **AIR_WING_ATTACK_LOGISTICS_TRAIN_DAMAGE_FACTOR**
  - Default: 0.040

- **AIR_WING_ATTACK_LOGISTICS_TRAIN_DAMAGE_DISRUPTION_MITIGATION**
  - Default: 6.0
  - Developer comment: Multiply Train Damage by (Smooth / (Smooth + (Disruption * Mitigation)))

- **AIR_WING_ATTACK_LOGISTICS_TRAIN_DAMAGE_DISRUPTION_SMOOTHING**
  - Default: 5.0

- **AIR_WING_ATTACK_LOGISTICS_RAILWAY_DAMAGE_SPILL_FACTOR**
  - Default: 0.006
  - Developer comment: Portion of train damage to additionally deal to railways

- **AIR_WING_ATTACK_LOGISTICS_DISRUPTION_MIN_DAMAGE_FACTOR**
  - Default: 0.1
  - Developer comment: Multiply train damage by this factor, scale from 1.0 at 0 disruption to this at AIR_WING_ATTACK_LOGISTICS_MAX_DISRUPTION_DAMAGE_TO_CONSIDER

- **AIR_WING_ATTACK_LOGISTICS_MAX_DISRUPTION_DAMAGE_TO_CONSIDER**
  - Default: 15.0
  - Developer comment: see above

- **AIR_WING_ATTACK_LOGISTICS_DIRECT_DISRUPTION_DAMAGE_FACTOR**
  - Default: 0.01
  - Developer comment: Disruption damage to supply throughput done by bombing damage, not dependant on killing trains which also causes diruption.

- **AIR_WING_ATTACK_LOGISTICS_TRUCK_MAX_FACTOR**
  - Default: 0.3
  - Developer comment: max trucks we can destroy in one instance of a logistics strike

- **SECONDARY_DAMAGE_STRAT**
  - Default: 0.2
  - Developer comment: how much damage gets translated to railway guns for strat bombing

- **SECONDARY_DAMAGE_LOGISTICS**
  - Default: 1.0
  - Developer comment: how much damage gets translated to railway guns for logistic strike

- **INTERCEPTION_DISTANCE_SCALE**
  - Default: 50
  - Developer comment: At this many pixels of path length, full interception efficiency is applied to air missions. Lerp from 0.

- **INTERCEPTION_DAMAGE_SCALE**
  - Default: 0.3
  - Developer comment: Multiply the interception damage with this value. Works as a cap when interception distance is at maximum.

- **MIN_PLANE_COUNT_PARADROP**
  - Default: 50

- **MIN_PLANE_COUNT_AIR_SUPPLY**
  - Default: 1

- **BASE_UNIT_WEIGHT_IN_TRANSPORT_PLANES**
  - Default: 45.0

- **MANPOWER_LOSS_RATIO_PLANE_SHOT**
  - Default: 0.10
  - Developer comment: The loss ratio of manpower for a shot plane.

- **MISSION_COMMAND_POWER_COSTS**
  - Default: { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.0, 0.0, 0.0, 0.0, 0.0 }
  - Developer comment:
    ```text
    command power cost per plane to create a mission
    AIR_SUPERIORITY
    CAS
    INTERCEPTION
    STRATEGIC_BOMBER
    NAVAL_BOMBER
    DROP_NUKE
    PARADROP
    NAVAL_KAMIKAZE
    PORT_STRIKE
    ATTACK_LOGISTICS
    AIR_SUPPLY
    TRAINING
    NAVAL_MINES_PLANTING
    NAVAL_MINES_SWEEPING
    RECON
    NAVAL_PATROL
    ```

- **MISSION_FUEL_COSTS**
  - Default: { 1.0, 1.0, 0.2, 1.0, 1.0, 1.0, 1.0, 0.75, 1.2, 1.2, 1.0, 0.6, 1.0, 1.0, 1.0, 1.0 }
  - Developer comment:
    ```text
    fuel cost per plane for each mission
    AIR_SUPERIORITY
    CAS
    INTERCEPTION
    STRATEGIC_BOMBER
    NAVAL_BOMBER
    DROP_NUKE
    PARADROP
    NAVAL_KAMIKAZE
    PORT_STRIKE
    ATTACK_LOGISTICS
    AIR_SUPPLY
    TRAINING
    NAVAL_MINES_PLANTING
    NAVAL_MINES_SWEEPING
    RECON
    NAVAL_PATROL
    ```

- **MAX_FUEL_FLOW_MULT**
  - Default: 1.0
  - Developer comment: max fuel flow ratio for planes, which will be multiplied by supply

- **FUEL_COST_MULT**
  - Default: 0.35
  - Developer comment: fuel multiplier for all air missions

- **MISSION_EFFICIENCY_MULT_AT_LACK_OF_FUEL**
  - Default: 0.25
  - Developer comment: multiplier for mission efficiency when a base lacks fuel

- **BOMBING_TARGETING_RANDOM_FACTOR**
  - Default: 0.25
  - Developer comment: % of picking the wrong target

- **BOMBING_PROV_BUILD_PRIO_SCALE**
  - Default: 1.5
  - Developer comment: Scale of the selected priority for provincial buildings

- **BOMBING_STATE_BUILD_PRIO_SCALE**
  - Default: 1.5
  - Developer comment: Scale of the selected priority for state buildings

- **BOMBING_INFRA_PRIO_SCALE**
  - Default: 0.7
  - Developer comment: Scale of the selected priority for infastryctyre

- **NAVAL_MINES_PLANTING_SPEED_MULT**
  - Default: 0.025
  - Developer comment: Value used to overall balance of the speed of planting naval mines

- **NAVAL_MINES_SWEEPING_SPEED_MULT**
  - Default: 0.025
  - Developer comment: Value used to overall balance of the speed of sweeping naval mines

- **NON_CORE_STRATEGIC_IMPACT**
  - Default: 0.5
  - Developer comment: multiplier for strategic impact of non-core bombing

- **RECON_LAND_SPOT_CHANCE**
  - Default: 0.02
  - Developer comment: scale factor on spotting lan

- **REINFORCEMENT_DISABLING_DURATION_IN_LAND_CARRIER_TRANSFER**
  - Default: 48
  - Developer comment: The reinforcement disabling duration in hours when transfering from land to carrier and vice versa

- **THRUST_WEIGHT_AGILITY_FACTOR**
  - Default: 0.5
  - Developer comment: For plane designs, additive agility bonus per point of thrust exceeding weight

- **MAX_QUICK_WING_SELECTION**
  - Default: 3
  - Developer comment: Max possible selection for airwing quick deploy

- **USE_SINGLE_NAVAL_ARMAMENT_CATEGORY**
  - Default: true
  - Developer comment: If true, only the armament module category that inflicts the greatest damage to naval targets will contribute naval strike and port strike mission specific stats. Only modules with both naval_strike_attack and naval_strike_targetting are considered. This is used to prevent torpedo_mounting and bomb_locks stats from stacking.

- **PORT_STRIKE_DAMAGE_FACTOR**
  - Default: 1.0
  - Developer comment: How much damage is dealt to ports during a port strike (per plane damage [complex number] * num flying planes * define)

## NNavy

- **WAR_SCORE_GAIN_FOR_SUNK_SHIP_MANPOWER_FACTOR**
  - Default: 0.004
  - Developer comment:
    ```text
    Peace Conference
    war score gained for every manpower killed when sinking a ship
    ```

- **WAR_SCORE_GAIN_FOR_SUNK_SHIP_PRODUCTION_COST_FACTOR**
  - Default: 0.020
  - Developer comment: war score gained for every IC of the sunk ship

- **WAR_SCORE_GAIN_FOR_SUNK_CONVOY**
  - Default: 0.08
  - Developer comment: war score gained for every sunk convoy

- **WAR_SCORE_DECAY_FOR_BUILT_CONVOY**
  - Default: 0.01
  - Developer comment: war score deducted when convoy-raided enemy produces one new convoy

- **PEACE_ACTION_TRANSFER_NAVY_EXPERIENCE_RETAINED**
  - Default: 0.25
  - Developer comment: % of experience to retain after being transferred in a peace conference

- **NAVAL_INVASION_PRIORITY**
  - Default: 1
  - Developer comment:
    ```text
    Convoy Priorities START
    Default convoy priority for naval invasions
    ```

- **NAVAL_TRANSFER_PRIORITY**
  - Default: 1
  - Developer comment: Default convoy priority for naval transports

- **SUPPLY_PRIORITY**
  - Default: 2
  - Developer comment: Default convoy priority for supplying units via sea

- **RESOURCE_LENDLEASE_PRIORITY**
  - Default: 3
  - Developer comment: Default convoy priority for export lend lease

- **RESOURCE_EXPORT_PRIORITY**
  - Default: 4
  - Developer comment: Default convoy priority for export trade

- **RESOURCE_ORIGIN_PRIORITY**
  - Default: 5
  - Developer comment: Default convoy priority for resources shipped internally

- **RESOURCE_PURCHASE_PRIORITY**
  - Default: 6
  - Developer comment: Default convoy priority for export equipment purchase

- **ADMIRAL_TASKFORCE_CAP**
  - Default: 10
  - Developer comment:
    ```text
    Convoy Priorities END
    admirals will start getting penalties after this amount of taskforces
    ```

- **DETECTION_CHANCE_MULT_BASE**
  - Default: 0.1
  - Developer comment: base multiplier value for detection chance. Later the chance is an average between our detection and enemy visibility, mult by surface/sub detection chance in the following defines.

- **DETECTION_CHANCE_MULT_RADAR_BONUS**
  - Default: 0.1
  - Developer comment: detection chance bonus from radars.

- **DETECTION_CHANCE_MULT_AIR_SUPERIORITY_BONUS**
  - Default: 0.25
  - Developer comment: bonus from air superiority.

- **MAX_CAPITALS_PER_AUTO_TASK_FORCE**
  - Default: 5
  - Developer comment: maximum number of capital ships the auto-task force creation will put together when designing SurfaceActionGroup

- **MAX_SUBMARINES_PER_AUTO_TASK_FORCE**
  - Default: 30
  - Developer comment: maximum number of submarines the auto-task force creation will put together when designing wolfpack

- **BEST_CAPITALS_TO_CARRIER_RATIO**
  - Default: 1
  - Developer comment: capitals / carriers ratio used when auto-task force creation designs CarrierTaskForce

- **BEST_CAPITALS_TO_SCREENS_RATIO**
  - Default: 0.25
  - Developer comment: capitals / screens ratio used for creating FEX groups in naval combat

- **COMBAT_BASE_HIT_CHANCE**
  - Default: 0.1
  - Developer comment: base chance for hit

- **COMBAT_MIN_HIT_CHANCE**
  - Default: 0.05
  - Developer comment: never less hit chance then this?

- **COMBAT_EVASION_TO_HIT_CHANCE**
  - Default: 0.007
  - Developer comment:
    ```text
    we take ship evasion stats, and mult by this value, so it gives hit chance reduction. So if reduction is 0.025 and ship evasion = 10, then there will be 0.25 (25%) lower hit chance. (Fe. 50% base -25% from evasion +10% bcoz it's very close).
    ```

- **COMBAT_EVASION_TO_HIT_CHANCE_TORPEDO_MULT**
  - Default: 10.0
  - Developer comment: the above evasion hit chance is multiplied by 400% if shooting with torpedoes. Torpedoes are slow, so evasion matters more.

- **MIN_HIT_PROFILE_MULT**
  - Default: 0.0
  - Developer comment: largest hit profile penalty to hitting

- **COMBAT_LOW_ORG_HIT_CHANCE_PENALTY**
  - Default: -0.5
  - Developer comment: % of penalty applied to hit chance when ORG is very low.

- **COMBAT_LOW_MANPOWER_HIT_CHANCE_PENALTY**
  - Default: -0.25
  - Developer comment: % of penalty applied to hit chance when manpower is very low.

- **COMBAT_DAMAGE_RANDOMNESS**
  - Default: 0.5
  - Developer comment: random factor in damage. So if max damage is fe. 10, and randomness is 30%, then damage will be between 7-10.

- **COMBAT_TORPEDO_CRITICAL_CHANCE**
  - Default: 0.1
  - Developer comment: chance for critical hit from torpedo.

- **COMBAT_TORPEDO_CRITICAL_DAMAGE_MULT**
  - Default: 2.0
  - Developer comment: multiplier to damage when got critical hit from torpedo. (Critical hits are devastating as usualy torpedo_attack are pretty high base values).

- **COMBAT_DAMAGE_TO_STR_FACTOR**
  - Default: 0.6
  - Developer comment: casting damage value to ship strength multiplier. Use it ot balance the game difficulty.

- **COMBAT_DAMAGE_TO_ORG_FACTOR**
  - Default: 1.0
  - Developer comment: casting damage value to ship organisation multiplier. Use it to balance the game difficulty.

- **NAVY_MAX_XP**
  - Default: 100

- **COMBAT_ON_THE_WAY_INIT_DISTANCE_BALANCE**
  - Default: 0.25
  - Developer comment: Value to balance initial distance to arrive for ships that are "on the way"

- **COMBAT_CHASE_RESIGNATION_HOURS**
  - Default: 8
  - Developer comment: Before we resign chasing enemy, give them some minimum time so the combat doesn't end instantly.

- **COMBAT_MAX_GROUPS**
  - Default: 1
  - Developer comment: Max amount of "Fire Exchange" groups (FEX).

- **COMBAT_MIN_DURATION**
  - Default: 8
  - Developer comment: Min combat duration before we can retreat. It's a balancing variable so it's not possible to always run with our weak ships agains big flotillas.

- **COMBAT_INITIAL_DURATION**
  - Default: 6
  - Developer comment: Number of hours that is considered the "initial phase" of naval combat, used for modifiers like surprise attack during "initial combat"

- **COMBAT_RETREAT_DECISION_CHANCE**
  - Default: 0.22
  - Developer comment: There is also random factor in deciding if we should retreat or not. That causes a delay in taking decision, that sooner or later will be picked. It's needed so damaged fast ships won't troll the combat.

- **COMBAT_DETECTED_CONVOYS_FROM_SURFACE_DETECTION_STAT**
  - Default: 0.1
  - Developer comment: Each 1.0 of surface_detection that ship has (equipment stat), gives x% of convoys discovered from total travelling along the route.

- **COMBAT_BASE_CRITICAL_CHANCE**
  - Default: 0.05
  - Developer comment: Base chance for receiving a critical chance. It get's scaled down with ship reliability.

- **COMBAT_CRITICAL_DAMAGE_MULT**
  - Default: 5.0
  - Developer comment: Multiplier for the critical damage. Scaled down with the ship reliability.

- **COMBAT_ARMOR_PIERCING_CRITICAL_BONUS**
  - Default: 1.0
  - Developer comment: Bonus to critical chance when shooter armor piercing is higher then target armor.

- **COMBAT_ARMOR_PIERCING_DAMAGE_REDUCTION**
  - Default: 0
  - Developer comment: All damage reduction % when target armor is >= then shooter armor piercing. (depricated)

- **REPAIR_AND_RETURN_PRIO_LOW**
  - Default: 0.2
  - Developer comment: % of total Strength. When below, navy will go to home base to repair.

- **REPAIR_AND_RETURN_PRIO_MEDIUM**
  - Default: 0.5
  - Developer comment: % of total Strength. When below, navy will go to home base to repair.

- **REPAIR_AND_RETURN_PRIO_HIGH**
  - Default: 0.9
  - Developer comment: % of total Strength. When below, navy will go to home base to repair.

- **REPAIR_AND_RETURN_PRIO_LOW_COMBAT**
  - Default: 0.6
  - Developer comment: % of total Strength. When below, navy will go to home base to repair (in combat).

- **REPAIR_AND_RETURN_PRIO_MEDIUM_COMBAT**
  - Default: 0.3
  - Developer comment: % of total Strength. When below, navy will go to home base to repair (in combat).

- **REPAIR_AND_RETURN_PRIO_HIGH_COMBAT**
  - Default: 0.1
  - Developer comment: % of total Strength. When below, navy will go to home base to repair (in combat).

- **REPAIR_AND_RETURN_AMOUNT_SHIPS_LOW**
  - Default: 0.2
  - Developer comment: % of total damaged ships, that will be sent for repair-and-return in one call.

- **REPAIR_AND_RETURN_AMOUNT_SHIPS_MEDIUM**
  - Default: 0.4
  - Developer comment: % of total damaged ships, that will be sent for repair-and-return in one call.

- **REPAIR_AND_RETURN_AMOUNT_SHIPS_HIGH**
  - Default: 0.8
  - Developer comment: % of total damaged ships, that will be sent for repair-and-return in one call.

- **REPAIR_AND_RETURN_UNIT_DYING_STR**
  - Default: 0.2
  - Developer comment: Str below this point is considering a single ship "dying", and a high priority to send to repair.

- **EXPERIENCE_LOSS_FACTOR**
  - Default: 1.00
  - Developer comment: percentage of experienced solders who die when manpower is removed

- **NAVY_EXPENSIVE_IC**
  - Default: 5500
  - Developer comment: How much IC is considering the fleet to be expensive. Those expensive will triger the alert, when are on low STR.

- **MISSION_MAX_REGIONS**
  - Default: 0
  - Developer comment: Limit of the regions that can be assigned to naval mission. Set to 0 for unlimited.

- **CONVOY_EFFICIENCY_LOSS_MODIFIER**
  - Default: 1.25
  - Developer comment: How much efficiency drops when losing convoys. If modifier is 0.5, then losing 100% of convoys in short period, the efficiency will drop by 50%.

- **CONVOY_EFFICIENCY_REGAIN_AFTER_DAYS**
  - Default: 7
  - Developer comment: Convoy starts regaining it's efficiency after X days without any convoys being sink.

- **CONVOY_EFFICIENCY_REGAIN_BASE_SPEED**
  - Default: 0.04
  - Developer comment: How much efficiency regains every day.

- **CONVOY_EFFICIENCY_MIN_VALUE**
  - Default: 0.05
  - Developer comment: To avoid complete 0% efficiency, set the lower limit.

- **CONVOY_ROUTE_SIZE_CONVOY_SCALE**
  - Default: 0.5
  - Developer comment: scales impact of convoy route size (0 to turn off)

- **ANTI_AIR_TARGETTING_TO_CHANCE**
  - Default: 0.2
  - Developer comment: Balancing value to convert averaged equipment stats (anti_air_targetting and naval_strike_agility) to probability chances of airplane being hit by navies AA.

- **ANTI_AIR_ATTACK_TO_AMOUNT**
  - Default: 0.01
  - Developer comment: Balancing value to convert equipment stat anti_air_attack to the random % value of airplanes being hit.

- **CONVOY_SINKING_SPILLOVER**
  - Default: 0.5
  - Developer comment: Damaged convoys roll for if they sink in the end of combat by accumulating the damage. This scales that chance.

- **UNIT_EXPERIENCE_PER_COMBAT_HOUR**
  - Default: 10

- **UNIT_EXPERIENCE_SCALE**
  - Default: 1

- **EXPERIENCE_FACTOR_CONVOY_ATTACK**
  - Default: 0.04

- **EXPERIENCE_FACTOR_NON_CARRIER_GAIN**
  - Default: 0.04
  - Developer comment: Xp gain by non-carrier ships in the combat

- **EXPERIENCE_FACTOR_CARRIER_GAIN**
  - Default: 0.08
  - Developer comment: Xp gain by carrier ships in the combat

- **FIELD_EXPERIENCE_SCALE**
  - Default: 0.075

- **FIELD_EXPERIENCE_MAX_PER_DAY**
  - Default: 50
  - Developer comment: Most xp you can gain per day

- **LEADER_EXPERIENCE_SCALE**
  - Default: 1.0

- **BATTLE_NAME_VP_FACTOR**
  - Default: 100
  - Developer comment: Name is given by ((VP value) * BATTLE_NAME_VP_FACTOR) / (Distance VP -> battle)

- **BATTLE_NAME_VP_CUTOFF**
  - Default: 1.0
  - Developer comment: If best score of above calculation is below this, name will be that of region.

- **AMPHIBIOUS_LANDING_PENALTY**
  - Default: -0.7
  - Developer comment: amphibious landing penalty

- **AMPHIBIOUS_INVADE_SPEED_BASE**
  - Default: 0.5
  - Developer comment: every hour movement progress on amphibious invasion

- **AMPHIBIOUS_INVADE_MOVEMENT_COST**
  - Default: 24.0
  - Developer comment: total progress cost of movement while amphibious invading

- **AMPHIBIOUS_INVADE_ATTACK_LOW**
  - Default: 0.2
  - Developer comment: low and high cap of attack modifier scale. Scale interpolated by invasion progress.

- **AMPHIBIOUS_INVADE_ATTACK_HIGH**
  - Default: 1.0

- **AMPHIBIOUS_INVADE_DEFEND_LOW**
  - Default: 1.5
  - Developer comment: low and high cap of defend modifier scale. Scale interpolated by invasion progress.

- **AMPHIBIOUS_INVADE_DEFEND_HIGH**
  - Default: 1.0

- **AMPHIBIOUS_INVADE_LANDING_PENALTY_DECREASE**
  - Default: 3.5
  - Developer comment: scale of bonus that decreases "amphibious penalty" during combat, relative to invading transporter tech.

- **BASE_CARRIER_SORTIE_EFFICIENCY**
  - Default: 0.5
  - Developer comment: factor of planes that can sortie by default from a carrier

- **CONVOY_ATTACK_BASE_FACTOR**
  - Default: 0.15
  - Developer comment: base % of convoys that get intercepted

- **NAVAL_SPEED_MODIFIER**
  - Default: 0.1
  - Developer comment: basic speed control

- **NAVAL_RANGE_TO_INGAME_DISTANCE**
  - Default: 0.12
  - Developer comment: Scale the ship stats "naval_range" to the ingame distance

- **NAVAL_INVASION_PREPARE_HOURS**
  - Default: 168
  - Developer comment: base hours needed to prepare an invasion

- **NAVAL_COMBAT_RESULT_TIMEOUT_YEARS**
  - Default: 2
  - Developer comment: after that many years, we clear the naval combat results, so they don't get stuck forever in the memory.

- **CONVOY_LOSS_HISTORY_TIMEOUT_MONTHS**
  - Default: 24
  - Developer comment: after this many months remove the history of lost convoys to not bloat savegames and memory since there is no way to see them anyway

- **NAVAL_TRANSFER_BASE_SPEED**
  - Default: 6
  - Developer comment: base speed of units on water being transported

- **NAVAL_TRANSFER_BASE_NAVAL_DIST_ADD**
  - Default: 100
  - Developer comment: Extra cost for naval movement ( compared to land movement ) when deciding what ports to use for a naval transfer

- **NAVAL_TRANSFER_BASE_NAVAL_DIST_MULT**
  - Default: 20
  - Developer comment: Multiplier for the cost of naval movement ( compared to land movement ) when deciding what ports to use for naval transfer

- **NAVAL_SUPREMACY_CAN_INVADE**
  - Default: 0.5
  - Developer comment: required naval supremacy to perform invasions on an area

- **CARRIER_STACK_PENALTY**
  - Default: 4
  - Developer comment: The most efficient is 4 carriers in combat. 5+ brings the penalty to the amount of wings in battle.

- **CARRIER_STACK_PENALTY_EFFECT**
  - Default: 0.2
  - Developer comment: Each carrier above the optimal amount decreases the amount of airplanes being able to takeoff by such %.

- **SHORE_BOMBARDMENT_CAP**
  - Default: 0.25

- **ANTI_AIR_TARGETING**
  - Default: 0.9
  - Developer comment: how good ships are at hitting aircraft

- **MIN_TRACTED_ASSIST_DAMAGE_RATIO**
  - Default: 0.05
  - Developer comment: How much damage counts as assist damage

- **SUPPLY_NEED_FACTOR**
  - Default: 4
  - Developer comment: multiplies supply usage

- **DECRYPTION_SPOTTING_BONUS**
  - Default: 0.2

- **DISBAND_MANPOWER_LOSS**
  - Default: 0.0

- **MANPOWER_LOSS_RATIO_ON_SUNK**
  - Default: 0.5
  - Developer comment: sunk ships will lose this ratio of their current manpower

- **MANPOWER_LOSS_RATIO_ON_STR_LOSS**
  - Default: 0.5
  - Developer comment: losing strength will make you also lose manpower at this ratio of total manpower

- **MIN_MANPOWER_RATIO_TO_DROP**
  - Default: 0.1
  - Developer comment: ships will not lose man power to below this ratio

- **DAILY_MANPOWER_GAIN_RATIO**
  - Default: 0.05
  - Developer comment: the ships not in combat will be able to gain this ratio of their max manpower

- **PRIDE_OF_THE_FLEET_UNASSIGN_COST**
  - Default: 100
  - Developer comment: cost to unassign/replace pride of the fleet

- **PRIDE_OF_THE_FLEET_LOST_TEMP_MODIFIER_DURATION**
  - Default: 30
  - Developer comment: duration for temp modifiers that you get when you lose your pride of the fleet

- **XP_GAIN_FACTOR**
  - Default: 1.0
  - Developer comment: xp gain factor for navy

- **NAVAL_TRANSFER_DAMAGE_REDUCTION**
  - Default: 0.25
  - Developer comment: its hard to specifically balance 1-tick naval strikes vs unit transports so here is a factor for it

- **CARRIER_ONLY_COMBAT_ACTIVATE_TIME**
  - Default: 0
  - Developer comment: hours from start of combat when carriers get to fight

- **CAPITAL_ONLY_COMBAT_ACTIVATE_TIME**
  - Default: 6
  - Developer comment: hours from start of combat when only carriers, capitals and subs get to attack

- **ALL_SHIPS_ACTIVATE_TIME**
  - Default: 8
  - Developer comment: hours where all get to attack

- **MINIMUM_SHIP_SPEED**
  - Default: 1.0
  - Developer comment: slowest speed a ship can have

- **REPAIR_SPLIT_TASKFORCE_SIZE**
  - Default: 5
  - Developer comment: if a country does not have empty naval naval bases for repairs, it will split ships with this sizes and distribute them around

- **NAVY_REPAIR_BASE_SEARCH_SCORE_PER_SHIP_WAITING_EXTRA_SHIP**
  - Default: 5
  - Developer comment: if a naval base has more ships than it can repair, it will get penalties

- **NAVY_REPAIR_BASE_SEARCH_SCORE_PER_SLOT**
  - Default: 1.0
  - Developer comment: while searching for a naval base for repairs, the bases gets a bonus to their scores per empty slot they have

- **NAVY_REPAIR_BASE_SEARCH_BOOST_FOR_SAME_COUNTRY**
  - Default: 5
  - Developer comment: while searching for a naval base for repairs, your own bases gets a bonus

- **CONVOY_SPOTTING_COOLDOWN**
  - Default: 0.3
  - Developer comment: % of travel time

- **CONVOY_SPOTTING_COOLDOWN_MIN**
  - Default: 36
  - Developer comment: minimum cooldown time

- **CONVOY_SPOTTING_COOLDOWN_MAX**
  - Default: 168
  - Developer comment: maximum cooldown time

- **CONVOY_SPOTTING_COOLDOWN_MIN_FROM_EFFICIENCY**
  - Default: 15
  - Developer comment: clamped min value after screening efficiency has been applied

- **MISSION_FUEL_COSTS**
  - Default: { 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.6, 0.0, 1.0 }
  - Developer comment:
    ```text
    fuel cost for each mission
    HOLD (consumes fuel HOLD_MISSION_MOVEMENT_COST fuel while moving)
    PATROL
    STRIKE FORCE (does not cost fuel at base, and uses IN_COMBAT_FUEL_COST in combat. this is just for the movement in between)
    CONVOY RAIDING
    CONVOY ESCORT
    MINES PLANTING
    MINES SWEEPING
    TRAIN
    RESERVE_FLEET (consumes fuel HOLD_MISSION_MOVEMENT_COST fuel while moving)
    NAVAL_INVASION_SUPPORT (does not cost fuel at base, only costs while doing bombardment and escorting units)
    ```

- **HOLD_MISSION_MOVEMENT_COST**
  - Default: 1.0
  - Developer comment: ships on hold cost this much fuel while moving

- **ON_BASE_FUEL_COST**
  - Default: 0.0
  - Developer comment: ships that waits at naval bases cost this ratio

- **IN_COMBAT_FUEL_COST**
  - Default: 2.0
  - Developer comment: ships in combat will get this ratio for fuel cost

- **TRAINING_FUEL_COST_FOR_ESCORT_SHIPS**
  - Default: 0.15
  - Developer comment: ships that are on training mission but not training (ie they are at max xp and training will cancel at max xp) will consume this ratio of fuel

- **MAX_FUEL_FLOW_MULT**
  - Default: 2.0
  - Developer comment: max fuel flow ratio for ships, which will be multiplied by supply

- **FUEL_COST_MULT**
  - Default: 0.10
  - Developer comment: fuel multiplier for all naval missions

- **OUT_OF_FUEL_SPEED_FACTOR**
  - Default: -0.75

- **OUT_OF_FUEL_RANGE_FACTOR**
  - Default: -0.75

- **OUT_OF_FUEL_ATTACK_FACTOR**
  - Default: -0.5

- **OUT_OF_FUEL_TORPEDO_FACTOR**
  - Default: -0.8

- **MISSION_SPREADS**
  - Default: { 0.0, 0.0, 0.0, 0.0, 0.0, 0.7, 0.7, 0.5, 0.0, 0.0 }
  - Developer comment:
    ```text
    mission spreads in the case a ship join combat, which is calculated for number of ships that will be in combat. 1 means no ship will be at start
    HOLD
    PATROL
    STRIKE FORCE
    CONVOY RAIDING
    CONVOY ESCORT
    MINES PLANTING
    MINES SWEEPING
    TRAIN
    RESERVE_FLEET
    NAVAL_INVASION_SUPPORT
    ```

- **MISSION_DEFAULT_SPREAD_BASE**
  - Default: 1.0
  - Developer comment: multiplier for mission spreads. higher = less ships on start

- **AGGRESSION_SETTINGS_VALUES**
  - Default: { 0, 0.5, 0.9, 2.0, 10000 }
  - Developer comment:
    ```text
    ships will use this values while deciding to attack enemies
    do not engage
    low
    medium
    high
    I am death incarnate!
    ```

- **AGGRESION_MULTIPLIER_FOR_COMBAT**
  - Default: 1.2
  - Developer comment: ships are more aggresive in combat

- **AGGRESSION_ARMOR_EFFICIENCY_MULTIPLIER**
  - Default: 1.0
  - Developer comment: armor to enemy piercing ratio is multiplied by this value, which will increase the strength of ships while considering them for aggression

- **AGGRESSION_MIN_ARMOR_EFFICIENCY**
  - Default: 0.5
  - Developer comment: armor multiplier has a min and max caps while being factored in aggression

- **AGGRESSION_MAX_ARMOR_EFFICIENCY**
  - Default: 1.5
  - Developer comment: armor multiplier has a min and max caps while being factored in aggression

- **AGGRESSION_LIGHT_GUN_EFFICIENCY_ON_LIGHT_SHIPS**
  - Default: 1.0
  - Developer comment: ratio for scoring for different gun types against light ships

- **AGGRESSION_HEAVY_GUN_EFFICIENCY_ON_LIGHT_SHIPS**
  - Default: 0.25
  - Developer comment: ratio for scoring for different gun types against light ships

- **AGGRESSION_TORPEDO_EFFICIENCY_ON_LIGHT_SHIPS**
  - Default: 0.1
  - Developer comment: ratio for scoring for different gun types against light ships

- **AGGRESSION_LIGHT_GUN_EFFICIENCY_ON_HEAVY_SHIPS**
  - Default: 0.1
  - Developer comment: ratio for scoring for different gun types against heavy ships

- **AGGRESSION_HEAVY_GUN_EFFICIENCY_ON_HEAVY_SHIPS**
  - Default: 1.0
  - Developer comment: ratio for scoring for different gun types against heavy ships

- **AGGRESSION_TORPEDO_EFFICIENCY_ON_HEAVY_SHIPS**
  - Default: 1.1
  - Developer comment: ratio for scoring for different gun types against heavy ships

- **AGGRESSION_CONVOY_STRENGTH_FACTOR**
  - Default: 0.3
  - Developer comment: convoys in combat gets a penalty to their strength in aggression calculations

- **SUBMARINE_ESCAPE_RATIOS**
  - Default: { 1000, 15, 3.0, 1.0, 0.1 }
  - Developer comment:
    ```text
    subs will escape battle in convoy raid if there are enemies that can attack
    do not engage
    low
    medium
    high
    I am death incarnate!
    ```

- **MIN_REPAIR_FOR_JOINING_COMBATS**
  - Default: { 0.0, 0.5, 0.7, 0.9 }
  - Developer comment:
    ```text
    strikeforces/patrol forces will not join combats if they are not repaired enough
    do not repair
    low
    medium
    high
    ```

- **ORG_COST_WHILE_MOVING**
  - Default: { 0.3, 0.2, 0.25, 0.2, 0.2, 0.2, 0.2, 0.2, 0.3, 0.2 }
  - Developer comment:
    ```text
    org cost while the ships are moving
    HOLD
    PATROL
    STRIKE FORCE
    CONVOY RAIDING
    CONVOY ESCORT
    MINES PLANTING
    MINES SWEEPING
    TRAIN
    RESERVE_FLEET
    NAVAL_INVASION_SUPPORT
    ```

- **ORG_COST_WHILE_MOVING_IN_MISSION_ZONE**
  - Default: { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }
  - Developer comment:
    ```text
    org cost while moving in mission zone
    HOLD
    PATROL
    STRIKE FORCE
    CONVOY RAIDING
    CONVOY ESCORT
    MINES PLANTING
    MINES SWEEPING
    TRAIN
    RESERVE_FLEET
    NAVAL_INVASION_SUPPORT
    ```

- **MAX_ORG_ON_MANUAL_MOVE**
  - Default: 0.66
  - Developer comment: org will clamped to this ratio on manual move

- **MIN_ORG_ON_MANUAL_MOVE**
  - Default: 0.1
  - Developer comment: org will clamped to this ratio on manual move

- **INITIAL_ALLOWED_DOCKYARD_RATIO_FOR_REPAIRS**
  - Default: 0.25
  - Developer comment: initially countries will allocate this ratio of dockyards for repairs

- **MISSION_SUPREMACY_RATIOS**
  - Default: { 0.0, 1.0, 1.0, 0.5, 0.5, 0.3, 0.3, 0.0, 0.0, 1.0 }
  - Developer comment:
    ```text
    supremacy multipliers for different mission types
    HOLD
    PATROL
    STRIKE FORCE
    CONVOY RAIDING
    CONVOY ESCORT
    MINES PLANTING
    MINES SWEEPING
    TRAIN
    RESERVE_FLEET
    NAVAL_INVASION_SUPPORT
    ```

- **SUPREMACY_PER_SHIP_PER_MANPOWER**
  - Default: 0.05
  - Developer comment: supremacy of a ship is calculated using its IC, manpower and a base define

- **SUPREMACY_PER_SHIP_PER_IC**
  - Default: 0.005

- **SUPREMACY_PER_SHIP_BASE**
  - Default: 0

- **NAVAL_MINES_IN_REGION_MAX**
  - Default: 1000.0
  - Developer comment: Max number of mines that can be layed by the ships. The value should be hidden from the user, as we present % so it's an abstract value that should be used for balancing.

- **NAVAL_MINES_PLANTING_SPEED_MULT**
  - Default: 0.01
  - Developer comment: Value used to overall balance of the speed of planting naval mines

- **NAVAL_MINES_SWEEPING_SPEED_MULT**
  - Default: 0.009
  - Developer comment: Value used to overall balance of the speed of sweeping naval mines

- **NAVAL_MINES_DECAY_AT_PEACE_TIME**
  - Default: 0.25
  - Developer comment: How fast mines are decaying in peace time. Planting mines in peace time may be exploitable, so it's blocked atm. That's why after war we should decay them too.

- **NAVAL_MINES_SWEEPERS_REDUCTION_ON_PENALTY_EFFECT**
  - Default: 3.3
  - Developer comment: How much is the task force's sweeping attribute reducing the penalty effect.

- **NAVAL_MINES_INTEL_DIFF_FACTOR**
  - Default: 0.5
  - Developer comment: Better our decryption over enemy encryption will reduce the penalties from the enemy mines in the region. This value is a factor to be used for balancing.

- **NAVAL_MINES_NAVAL_SUPREMACY_FACTOR**
  - Default: 1.0
  - Developer comment: Factor for max amount of mines increasing naval supremacy

- **ATTRITION_WHILE_MOVING_FACTOR**
  - Default: 1.5
  - Developer comment: attrition multiplier while moving & doing missions

- **ATTRITION_DAMAGE_ORG**
  - Default: 0.01
  - Developer comment: damage from attrition to Organisation (relative to max org)

- **ATTRITION_DAMAGE_STR**
  - Default: 0.03
  - Developer comment: damage from attrition to str (relative to max str)

- **ATTRITION_STR_DAMAGE_CHANCE**
  - Default: 0.2
  - Developer comment: chance to get damaged at highest attrition

- **NAVAL_ACCIDENT_CHANCE_REDUCTION_ON_POTF**
  - Default: 0.01
  - Developer comment: Scale of the current chance for an accident to happen, applied for the pride of the fleet.

- **NAVAL_ACCIDENT_CRITICAL_HIT_CHANCE_REDUCTION_POTF**
  - Default: 0.01
  - Developer comment: Scale of the current chance for a critical hit when an accident happens, applied for the pride of the fleet.

- **NAVAL_MINES_ACCIDENT_CRITICAL_HIT_CHANCES**
  - Default: 0.14
  - Developer comment: If an accident happens, how likely it is to be a critical hit (caused by naval mines)

- **NAVAL_MINES_ACCIDENT_CRITICAL_HIT_DAMAGE_SCALE**
  - Default: 5.0
  - Developer comment: Scale the value below in case of critical hit (caused by naval mines)

- **NAVAL_MINES_ACCIDENT_STRENGTH_LOSS**
  - Default: 50.0
  - Developer comment: Amount of strength loss when hit by naval mine

- **NAVAL_MINES_ACCIDENT_ORG_LOSS_FACTOR**
  - Default: 0.5
  - Developer comment: Amount of strength loss when hit by naval mine

- **TRAINING_ACCIDENT_CHANCES**
  - Default: 0.02
  - Developer comment: Chances one ship get damage each hour while on training

- **TRAINING_ACCIDENT_CRITICAL_HIT_CHANCES**
  - Default: 0.3
  - Developer comment: If an accident happens, how likely it is to be a critical hit

- **TRAINING_ACCIDENT_CRITICAL_HIT_DAMAGE_SCALE**
  - Default: 4.0
  - Developer comment: Scale the value below in case of critical hit

- **TRAINING_ACCIDENT_STRENGTH_LOSS**
  - Default: 4.0
  - Developer comment: Amount of strength loss in a training accident

- **TRAINING_ACCIDENT_STRENGTH_LOSS_FACTOR**
  - Default: 0.05
  - Developer comment: Amount of strength loss in a training accident, propotional to the maximum strength of the ship

- **TRAINING_ACCIDENT_ORG_LOSS_FACTOR**
  - Default: 0.3
  - Developer comment: Amount of current organization the ship lose

- **ACCIDENTS_CHANCE_BALANCE_FACTOR**
  - Default: 0.04
  - Developer comment: General chance for naval accidents for balancing the gameplay.

- **TRAINING_EXPERIENCE_FACTOR**
  - Default: 0.3
  - Developer comment:
    ```text
    The Formula: Min( TRAINING_MAX_DAILY_COUNTRY_EXP * Ratio, TRAINING_DAILY_COUNTRY_EXP_FACTOR * ( TRAINING_DAILY_COUNTRY_EXP_SHIP_RATIO_FACTOR * TrainingShipCount / CountryShipCount
    + TRAINING_DAILY_COUNTRY_EXP_MANPOWER_FACTOR * Manpower + TRAINING_DAILY_COUNTRY_EXP_MANPOWER_RATIO_FACTOR * Manpower / CountryShipCount ) )
    Amount of exp each ship gain every 24h while training (before modifiers)
    ```

- **TRAINING_DAILY_COUNTRY_EXP_FACTOR**
  - Default: 0.001
  - Developer comment: Factor used to scale the Daily Country Navy XP gain

- **TRAINING_DAILY_COUNTRY_EXP_MANPOWER_FACTOR**
  - Default: 0.006
  - Developer comment: Factor used to scale the sum of the training manpower for the Daily Country Navy XP gain

- **TRAINING_DAILY_COUNTRY_EXP_MANPOWER_RATIO_FACTOR**
  - Default: 0.01
  - Developer comment: Factor used to scale the sum of the manpower divided by the country's number of ship for the Daily Country Navy XP gain

- **TRAINING_DAILY_COUNTRY_EXP_SHIP_RATIO_FACTOR**
  - Default: 300.0
  - Developer comment: Factor used to scale the ratio of training ships for the Daily Country Navy XP gain

- **TRAINING_MAX_DAILY_COUNTRY_EXP**
  - Default: 3.5
  - Developer comment: Maximum navy XP daily gain

- **TRAINING_MIN_STRENGTH**
  - Default: 0.1
  - Developer comment: if strength is less than this, the unit will not contribute to training and cant be damaged by training

- **TRAINING_ORG**
  - Default: 0.2
  - Developer comment: max organization on traiaing mission

- **BASE_SPOTTING**
  - Default: 1
  - Developer comment: base spotting percentage for navy

- **BASE_SPOTTING_FROM_RADAR**
  - Default: 5
  - Developer comment: base spotting percentage that comes from full radar coverage

- **NAVY_SPOTTER_DETECTION_FACTOR**
  - Default: 0.1
  - Developer comment: multiplier for task forces' detection value before logistic transform

- **BASE_SPOTTING_FROM_NAVY**
  - Default: 10
  - Developer comment: base spotting percentage that comes from task forces in area

- **AIR_SPOTTER_NORMALIZED_AIRWING_SIZE**
  - Default: 100
  - Developer comment: each plane will contribute 1/this of the air-wing's detection stat

- **AIR_SPOTTER_DETECTION_FACTOR**
  - Default: 0.025
  - Developer comment: multiplier for air-wings' detection value before logistic transform

- **BASE_SPOTTING_FROM_AIR**
  - Default: 20
  - Developer comment: base spotting percentage that comes from air-wings in area

- **BASE_SPOTTING_FROM_DECRYPTION**
  - Default: 10
  - Developer comment: base spotting percentage that comes from decryption, can go negative (enemy decryption is subtracted)

- **MIN_SPOTTING_PROGRESS**
  - Default: 0.01
  - Developer comment: Minimum spotting progress (in percent) per hourly tick

- **AIR_MISSION_SPOTTING_FACTORS**
  - Default: { 0.50, 0, 0.25, 0, 0.50, 0, 0, 0.25, 0, 0, 0, 0, 0.25, 0.50, 1.00, 1.50 }
  - Developer comment:
    ```text
    Multiplier for air-wings' spotting contribution per mission type
    AIR_SUPERIORITY
    CAS
    INTERCEPTION
    STRATEGIC_BOMBER
    NAVAL_BOMBER
    DROP_NUKE
    PARADROP
    NAVAL_KAMIKAZE
    PORT_STRIKE
    ATTACK_LOGISTICS
    AIR_SUPPLY
    TRAINING
    NAVAL_MINES_PLANTING
    NAVAL_MINES_SWEEPING
    RECON
    NAVAL_PATROL
    ```

- **MIN_HOURS_TO_SHUFFLE_NEWLY_ASSIGNED_PATROLS**
  - Default: 7*24
  - Developer comment: if a fleet has less patrol than it needs to cover all of it areas, it will shuffle the patrols around. it will wait this much hour before shuffling a task force to new area

- **SPOTTING_ENEMY_SPOTTING_MULTIPLIER_FOR_RUNNING_AWAY**
  - Default: 0.80
  - Developer comment: enemy spotting is multiplied by this value to simulate running away

- **SPOTTING_MULTIPLIER_FOR_SURFACE**
  - Default: 1.0
  - Developer comment: task force surface spotting value is multiplied by this and added to spotting percentage every hour

- **SPOTTING_MULTIPLIER_FOR_SUB**
  - Default: 1.0
  - Developer comment: task force sub spotting value is multiplied by this and added to spotting percentage every hour

- **SPOTTING_SPEED_MULT_FOR_RUNNING_AWAY**
  - Default: 0.5
  - Developer comment: task forces that does not want to engage will reduce enemy spotting rate every hour by speed diff mult this ratio

- **SPOTTING_SPEED_MULT_FOR_CATCHING_UP**
  - Default: 0.2
  - Developer comment: speed diff bonus rate that is added to spotting every hour

- **SPOTTING_MISSION_DETECTION_THRESHOLD_LOW**
  - Default: 10.0
  - Developer comment: value between 0 and 100 above which to show very coarse information about the spotted task force

- **SPOTTING_MISSION_DETECTION_THRESHOLD_MEDIUM**
  - Default: 70.0
  - Developer comment: value between 0 and 100 above which to show coarse information about the spotted task force. Note: accurate information are shown when spotting reach 100.

- **NAVY_VISIBILITY_BONUS_ON_RETURN_FOR_REPAIR**
  - Default: 0.9
  - Developer comment: Multiplier for the surface/sub visiblity when the heavily damaged fleet is returning to the home base for reparation. 1.0 = no bonus. 0.0 = invisible.

- **VISIBILITY_MULTIPLIER_FOR_SPOTTING**
  - Default: 0.1
  - Developer comment: multiplier for visibility stat

- **INTEL_LEVEL_LOW_HALF_RANGE_PERCENTAGE**
  - Default: 10
  - Developer comment: Integer representing the maximum offset of the displayed value to the original, in percentage (divided by 100 in code). For spotting level "low".

- **INTEL_LEVEL_MEDIUM_HALF_RANGE_PERCENTAGE**
  - Default: 5
  - Developer comment: Same as above but for the spotting level "medium"

- **INTEL_LEVEL_LOW_HALF_RANGE_MIN_SHIPS**
  - Default: 3
  - Developer comment: If the percentage of the value is lower than this, use this value instead. For spotting level "low"

- **INTEL_LEVEL_LOW_HALF_RANGE_MIN_CAPITALS**
  - Default: 1
  - Developer comment: Same as above but for capital ships

- **INTEL_LEVEL_MEDIUM_HALF_RANGE_MIN_SHIPS**
  - Default: 1
  - Developer comment: If the percentage of the value is lower than this, use this value instead. For spotting level "medium"

- **INTEL_LEVEL_MEDIUM_HALF_RANGE_MIN_CAPITALS**
  - Default: 1
  - Developer comment: Same as above but for capital ships. NOTE: overriden to 0 if the total number of ships in the task force is less than four.

- **INTEL_LEVEL_LOW_STRENGTH_ESTIMATE_HALF_RANGE_PERCENTAGE**
  - Default: 20
  - Developer comment: Integer representing the maximum offset of the estimated enemy strength to the original, in percentage (divided by 100 in code). For spotting level "low".

- **INTEL_LEVEL_MEDIUM_STRENGTH_ESTIMATE_HALF_RANGE_PERCENTAGE**
  - Default: 10
  - Developer comment: Same as above for spotting level "medium"

- **BASE_SPOTTING_SPEED**
  - Default: 0.0
  - Developer comment: daily base spotting speed

- **BASE_ESCAPE_SPEED**
  - Default: 0.045
  - Developer comment: daily base escape speed (gained as percentagE)

- **SPEED_TO_ESCAPE_SPEED**
  - Default: 0.95
  - Developer comment: ratio to converstion from ship speed to escape speed (divided by hundred)

- **ESCAPE_SPEED_PER_COMBAT_DAY**
  - Default: 0.01
  - Developer comment: daily increase in escape speed during combat duration

- **MAX_ESCAPE_SPEED_FROM_COMBAT_DURATION**
  - Default: 0.15
  - Developer comment: max escape speed that will be gained from combat duration

- **ESCAPE_SPEED_SUB_BASE**
  - Default: 0.08
  - Developer comment: subs get faster escape speed. gets replaced by hidden version below if hidden

- **ESCAPE_SPEED_HIDDEN_SUB**
  - Default: 0.18
  - Developer comment: hidden subs get faster escape speed

- **SUB_DETECTION_CHANCE_BASE**
  - Default: 5
  - Developer comment: to start spotting a submarine, a dice is rolled and checked if it succeeds this percentage. if not, that enemy sub force won't be spotted on this tick

- **SUB_DETECTION_CHANCE_BASE_SPOTTING_EFFECT**
  - Default: 0.5
  - Developer comment: effect of base spotting for initial spotting of pure submarine forces. this along with next value is added together and rolled against a random to start spotting

- **SUB_DETECTION_CHANCE_SPOTTING_SPEED_EFFECT**
  - Default: 2.0
  - Developer comment: effect of spotting speed for initial spotting of pure submarine forces. this along with prev value is added together and rolled against a random to start spotting

- **SUB_DETECTION_CHANCE_BASE_SPOTTING_POW_EFFECT**
  - Default: 1.5
  - Developer comment: effect of spotting speed will be powered by this for initial spotting of pure submarine forces. this along with prev value is added together and rolled against a random to start spotting

- **BASE_CONVOY_SPOTTING_SPEED**
  - Default: 0.0
  - Developer comment: daily base spotting speed against convoys

- **BASE_UNIT_TRANSFER_SPOTTING_SPEED**
  - Default: 0.0
  - Developer comment: daily base spotting speed against unit trans

- **BASE_NAVAL_INVASION_SPOTTING_SPEED**
  - Default: 0.0
  - Developer comment: daily base spotting speed against unit transfers

- **CONVOY_SPOTTING_SPEED_MULT**
  - Default: 1.0
  - Developer comment: spotting speed mult against convoys

- **UNIT_TRANSFER_SPOTTING_SPEED_MULT**
  - Default: 5.0
  - Developer comment: spotting speed mult against unit transfers

- **NAVAL_INVASION_SPOTTING_SPEED_MULT**
  - Default: 10.0
  - Developer comment: spotting speed mult against naval invasion armies

- **CONVOY_DETECTION_CHANCE_BASE**
  - Default: 4.12
  - Developer comment: regular convoy base chance detection percentage (if this fails, no detection is done on that tick)

- **BASE_SPOTTING_EFFECT_FOR_INITIAL_CONVOY_SPOTTING**
  - Default: 0.05
  - Developer comment: effect of base convoy spotting for initial spotting of regular convoys. this along with next value is added together and rolled a random  once for every convoy to check for spotting

- **SPOTTING_SPEED_EFFECT_FOR_INITIAL_CONVOY_SPOTTING**
  - Default: 0.50
  - Developer comment: effect of convoy spotting speed for initial spotting of regular convoys. this along with prev value is added together and rolled a random once for every convoy to check for spotting

- **SPOTTING_MOD_FOR_CONVOY_COUNT**
  - Default: 0.2
  - Developer comment: a modifier for scaling the count of convoys on a parabolic curve (counvoy_count ^ SPOTTING_MOD_FOR_CONVOY_COUNT)

- **UNIT_TRANSFER_DETECTION_CHANCE_BASE**
  - Default: 8.0
  - Developer comment: unit transfer and naval invasion base chance detection percentage (if this fails, no detection is done on that tick)

- **BASE_SPOTTING_EFFECT_FOR_INITIAL_UNIT_TRANSFER_SPOTTING**
  - Default: 2.4
  - Developer comment: same as BASE_SPOTTING_EFFECT_FOR_INITIAL_CONVOY_SPOTTING, but for naval transfer convoys

- **SPOTTING_SPEED_EFFECT_FOR_INITIAL_UNIT_TRANSFER_SPOTTING**
  - Default: 0.12
  - Developer comment: same as SPOTTING_SPEED_EFFECT_FOR_INITIAL_CONVOY_SPOTTING, but for naval transfer convoys

- **BASE_SPOTTING_EFFECT_FOR_INITIAL_NAVAL_INVASION_SPOTTING**
  - Default: 2.4
  - Developer comment: same as BASE_SPOTTING_EFFECT_FOR_INITIAL_CONVOY_SPOTTING, but for naval invasion convoys

- **SPOTTING_SPEED_EFFECT_FOR_INITIAL_NAVAL_INVASION_SPOTTING**
  - Default: 0.12
  - Developer comment: same as SPOTTING_SPEED_EFFECT_FOR_INITIAL_CONVOY_SPOTTING, but for naval invasion convoys

- **MIN_GUN_COOLDOWN**
  - Default: 0.1
  - Developer comment: minimum cooldown for a gun

- **BASE_GUN_COOLDOWNS**
  - Default: { 1.0, 4.0, 1.0 }
  - Developer comment:
    ```text
    number of hours for a gun to be ready after shooting
    big guns
    torpedoes
    small guns
    ```

- **BASE_JOIN_COMBAT_HOURS**
  - Default: 2
  - Developer comment: the taskforces that wants to join existing combats will wait for at least this amount

- **LOW_ORG_FACTOR_ON_JOIN_COMBAT_DURATION**
  - Default: 4.0
  - Developer comment: low org of the ships will be factored in when a taskforce wants to join combat

- **BASE_POSITIONING**
  - Default: 1.0
  - Developer comment: base value for positioning

- **RELATIVE_SURFACE_DETECTION_TO_POSITIONING_FACTOR**
  - Default: 0.01
  - Developer comment: multiples the surface detection difference between two sides. the side with higher detection will get a bonus of this value

- **MAX_POSITIONING_BONUS_FROM_SURFACE_DETECTION**
  - Default: 0.0
  - Developer comment: will clamp the bonus that you get from detection

- **HIGHER_SHIP_RATIO_POSITIONING_PENALTY_FACTOR**
  - Default: 0.25
  - Developer comment: if one side has more ships than the other, that side will get this penalty for each +100% ship ratio it has

- **MAX_POSITIONING_PENALTY_FROM_HIGHER_SHIP_RATIO**
  - Default: 0.75
  - Developer comment: maximum penalty to get from larger fleets

- **HIGHER_CARRIER_RATIO_POSITIONING_PENALTY_FACTOR**
  - Default: 0.2
  - Developer comment: penalty if other side has stronger carrier air force

- **MAX_CARRIER_RATIO_POSITIONING_PENALTY_FACTOR**
  - Default: 0.2
  - Developer comment: max penalty from stronger carrier air force

- **POSITIONING_PENALTY_FOR_SHIPS_JOINED_COMBAT_AFTER_IT_STARTS**
  - Default: 0.01
  - Developer comment: each ship that joins the combat will have this penalty to be added into positioning

- **MAX_POSITIONING_PENALTY_FOR_NEWLY_JOINED_SHIPS**
  - Default: 0.25
  - Developer comment: the accumulated penalty from new ships will be clamped to this value

- **POSITIONING_PENALTY_HOURLY_DECAY_FOR_NEWLY_JOINED_SHIPS**
  - Default: 0.05
  - Developer comment: the accumulated penalty from new ships will decay hourly by this value

- **DAMAGE_PENALTY_ON_MINIMUM_POSITIONING**
  - Default: 0.5
  - Developer comment: damage penalty at 0% positioning

- **SCREENING_EFFICIENCY_PENALTY_ON_MINIMUM_POSITIONING**
  - Default: 0.5
  - Developer comment: screening efficiency (screen to capital ratio) at 0% positioning

- **AA_EFFICIENCY_PENALTY_ON_MINIMUM_POSITIONING**
  - Default: 0.7
  - Developer comment: AA penalty at 0% positioning

- **SUBMARINE_REVEAL_ON_MINIMUM_POSITIONING**
  - Default: 2.0
  - Developer comment: submarine reveal change on 0% positioning

- **SHIP_TO_FLEET_ANTI_AIR_RATIO**
  - Default: 0.25
  - Developer comment: total sum of fleet's anti air will be multiplied with this ratio and added to calculations anti-air of individual ships while air damage reduction

- **ANTI_AIR_POW_ON_INCOMING_AIR_DAMAGE**
  - Default: 0.225
  - Developer comment: received air damage is calculated using following: 1 - ( (ship_anti_air + fleet_anti_air * SHIP_TO_FLEET_ANTI_AIR_RATIO )^ANTI_AIR_POW_ON_INCOMING_AIR_DAMAGE ) * ANTI_AIR_MULT_ON_INCOMING_AIR_DAMAGE

- **ANTI_AIR_MULT_ON_INCOMING_AIR_DAMAGE**
  - Default: 0.18

- **MAX_ANTI_AIR_REDUCTION_EFFECT_ON_INCOMING_AIR_DAMAGE**
  - Default: 0.75
  - Developer comment: damage reduction for incoming air attacks is clamped to this value at maximum.

- **CHANCE_TO_DAMAGE_PART_ON_CRITICAL_HIT**
  - Default: 0.1
  - Developer comment: the game will roll between 0-1 and will damage a random part if below this val on naval critical hits

- **CHANCE_TO_DAMAGE_PART_ON_CRITICAL_HIT_FROM_AIR**
  - Default: 0.1
  - Developer comment: the game will roll between 0-1 and will damage a random part if below this val on air critical hits

- **SCREEN_RATIO_FOR_FULL_SCREENING_FOR_CAPITALS**
  - Default: 3.0
  - Developer comment: this screen ratio to num capital/carriers is needed for full screening beyond screen line

- **SCREEN_RATIO_FOR_FULL_SCREENING_FOR_CONVOYS**
  - Default: 0.5
  - Developer comment: this screen ratio to num convoys is needed for full screening beyond screen line

- **CAPITAL_RATIO_FOR_FULL_SCREENING_FOR_CARRIERS**
  - Default: 1.0
  - Developer comment: this capital ratio to num carriers is needed for full screening beyond screen line

- **CAPITAL_RATIO_FOR_FULL_SCREENING_FOR_CONVOYS**
  - Default: 0.25
  - Developer comment: this capital ratio to num convoys is needed for full screening beyond screen line

- **TASK_FORCE_ROLE_TO_INSIGNIA**
  - Default: { 6, 15, 22, 26, 16, 17, 29, 1 }
  - Developer comment:
    ```text
    define the index of the insignia to use for a task force designed for a specific role
    Role undefined
    Wolfpack
    Carrier task force
    Surface action group
    Mine layers
    Mine sweepers
    Patrol task force
    Convoy escort
    ```

- **MIN_SHIP_COUNT_FOR_TASK_FORCE_ROLE_ASSIGNMENT**
  - Default: 4
  - Developer comment:
    ```text
    NOTE: you can see the effect of changing the values down below by running the command tfria with a task force selected
    define the minimum number of ship that should be in a task force for it to be considered a patrol or an escort task force (used to the insignia assignment, see TASK_FORCE_ROLE_TO_INSIGNIA)
    ```

- **SURFACE_DETECTION_STAT_FOR_SHIP_TO_BE_PATROL**
  - Default: 16
  - Developer comment: amount of surface detection required for a ship to be considered as part of a patrol task force

- **DEPTH_CHARGE_STAT_FOR_SHIP_TO_BE_SUB_HUNTER**
  - Default: 15
  - Developer comment: amount of depth charge required for a ship to be considred a sub hunter and so good for convoy escort

- **SUB_DETECTION_STAT_FOR_SHIP_TO_BE_SUB_HUNTER**
  - Default: 2
  - Developer comment: amount of sub detection required for a ship to be considered a sub hunter

- **HEAVY_GUN_ATTACK_TO_SHORE_BOMBARDMENT**
  - Default: 0.1
  - Developer comment: heavy gun attack value is divided by this value * 100 and added to shore bombardment modifier

- **LIGHT_GUN_ATTACK_TO_SHORE_BOMBARDMENT**
  - Default: 0.05
  - Developer comment: light gun attack value is divided by this value * 100 and added to shore bombardment modifier

- **GUN_HIT_PROFILES**
  - Default: { 80.0, 100.0, 45.0 }
  - Developer comment:
    ```text
    hit profiles for guns, if target ih profile is lower the gun will have lower accuracy
    big guns
    torpedoes
    small guns
    ```

- **DEPTH_CHARGES_HIT_CHANCE_MULT**
  - Default: 1.1
  - Developer comment: multiplies hit chance of small guns

- **DEPTH_CHARGES_DAMAGE_MULT**
  - Default: 0.7
  - Developer comment: multiplies damage of depth charges

- **DEPTH_CHARGES_HIT_PROFILE**
  - Default: 100.0
  - Developer comment: hit profile for depth charges

- **CONVOY_HIT_PROFILE**
  - Default: 85.0
  - Developer comment: convoys has this contant hit profile

- **HIT_PROFILE_MULT**
  - Default: 100.0
  - Developer comment: multiplies hit profile of every ship

- **HIT_PROFILE_SPEED_FACTOR**
  - Default: 0.5
  - Developer comment: factors speed value when determining it profile (Vis * HIT_PROFILE_MULT * Ship Hit Profile Mult)

- **HIT_PROFILE_SPEED_BASE**
  - Default: 20
  - Developer comment: Base value added to hitprofile speed calulation

- **CONVOY_RAID_MAX_REGION_TO_TASKFORCE_RATIO**
  - Default: 1.5
  - Developer comment: each taskforce in convoy raid mission can at most cover this many regions without losing efficiency

- **CONVOY_DEFENSE_MAX_CONVOY_TO_SHIP_RATIO**
  - Default: 12.0
  - Developer comment: each ship in convoy defense mission can at most cover this many convoys without losing efficiency

- **CONVOY_DEFENSE_MAX_REGION_TO_TASKFORCE_RATIO**
  - Default: 5.0
  - Developer comment: each taskforce in convoy defense mission can at most cover this many regions without losing efficiency

- **MINE_SWEEPING_SUPREMACY_EFFICIENCY_MAX_REGION_TO_TASKFORCE_RATIO**
  - Default: 1.0
  - Developer comment: mine missions will get lower supremacies if they are assigned more regions than this

- **MINE_PLANTING_SUPREMACY_EFFICIENCY_MAX_REGION_TO_TASKFORCE_RATIO**
  - Default: 1.0
  - Developer comment: mine missions will get lower supremacies if they are assigned more regions than this

- **EFFICIENCY_TO_JOIN_COMBAT_RATIO_PENALTY**
  - Default: 1.0
  - Developer comment: at lower efficiencies less ships will be able to join combat

- **EFFICIENCY_TO_TIME_TO_JOIN_COMBAT_PENALTY**
  - Default: 100.0
  - Developer comment: at lower efficiencies less time to join combat hour will be increased

- **COORDINATION_EFFECT_ON_CONVOY_RAID_EFFICIENCY**
  - Default: 1.5
  - Developer comment: coordination will increase the number of areas you can cover in convoy raid

- **COORDINATION_EFFECT_ON_CONVOY_DEFENSE_EFFICIENCY**
  - Default: 1.5
  - Developer comment: coordination will increase the number of convoys you can cover in convoy defense

- **COORDINATION_EFFECT_ON_TIME_TO_JOIN_COMBAT**
  - Default: 1.0
  - Developer comment: coordination will reduce the time to join combat penalties

- **COORDINATION_EFFECT_ON_MINE_LAYING_SPEED**
  - Default: 0.5
  - Developer comment: affect of coordination modifier in mine laying speed

- **COORDINATION_EFFECT_ON_MINE_SWEEPING_SPEED**
  - Default: 0.5
  - Developer comment: affect of coordination modifier in mine sweeping speed

- **COORDINATION_EFFECT_ON_PATROL_SPOTTING**
  - Default: 1.0
  - Developer comment: affect of coordination modifier in spotting speed

- **COORDINATION_EFFECT_ON_MINE_SWEEPING_SUPREMACY_EFFICIENCY**
  - Default: 1.0
  - Developer comment: mine missions supremacy can be buffed by coordination

- **COORDINATION_EFFECT_ON_MINE_PLANTING_SUPREMACY_EFFICIENCY**
  - Default: 1.0
  - Developer comment: mine missions supremacy can be buffed by coordination

- **MISSION_EFFICIENCY_POW_FACTOR**
  - Default: 1.7
  - Developer comment: mission efficiencies will be powered up by this to further penalize low efficiencies

- **NAVAL_COMBAT_SUB_DETECTION_FACTOR**
  - Default: 1.0
  - Developer comment: balance value for sub detection in combat by ships

- **SUBMARINE_HIDE_TIMEOUT**
  - Default: 20
  - Developer comment: Amount of in-game-hours that takes the submarine (with position unrevealed), to hide.

- **SUBMARINE_REVEALED_TIMEOUT**
  - Default: 16
  - Developer comment: Amount of in-game-hours that makes the submarine visible if it is on the defender side.

- **SUBMARINE_REVEAL_BASE_CHANCE**
  - Default: 11
  - Developer comment: Base factor for submarine detection. It's modified by the difference of a spotter's submarines detection vs submarine visibility. Use this variable for game balancing. setting this too low will cause bad spotting issues.

- **SUBMARINE_REVEAL_POW**
  - Default: 3.0
  - Developer comment: A scaling factor that is applied to the reveal chance in order to make large differences in detection vs visibility more pronounced

- **SUBMARINE_BASE_TORPEDO_REVEAL_CHANCE**
  - Default: 0.035
  - Developer comment: Chance of a submarine being revealed when it fires. 1.0 is 100%. this chance is then multiplied with modifier created by comparing firer's visibiility and target's detection

- **MAX_NUM_HOURS_TO_WAIT_AT_ALLY_DOCKYARDS_FOR_REPAIRS**
  - Default: 48
  - Developer comment: taskforces will wait at most this amount of hours in ally bases for repairs before switching to another base for repairs

- **COMBAT_RESULT_PRIORITY_THRESHOLDS**
  - Default: { 0, 4000, 20000 }
  - Developer comment:
    ```text
    the game will use this thresholds to define importance of a naval combat result. it will use the highest level that has higher threshold than the amount of production lost in combat
    low (keep at zero)
    medium
    high
    ```

- **COMBAT_RESULT_PRIORITY_DAY_TO_LIVE**
  - Default: { 7, 30, 120 }
  - Developer comment: the game will delete the combat results after some duration depending on its importance

- **NAVAL_ACCIDENTS_DAYS_TO_LIVE**
  - Default: 120

- **NAVAL_MINE_DANGER_RATIOS**
  - Default: { 0.1, 0.5, 1.0, 1.0, 3.0 }
  - Developer comment:
    ```text
    not owned
    near controlled
    near owned
    controlled
    owned
    ```

- **NAVAL_MINE_DANGER_TRIGGER_MIN**
  - Default: 0.0

- **NAVAL_MINE_DANGER_TRIGGER_MAX**
  - Default: 2.0

- **NAVAL_CONVOY_DANGER_RATIOS**
  - Default: { 0.10, 0.10, 0.10, 0.15, 0.15 }
  - Developer comment:
    ```text
    not owned
    near controlled
    near owned
    controlled
    owned
    ```

- **NAVAL_CONVOY_DANGER_TRIGGER_MIN**
  - Default: 0.0

- **NAVAL_CONVOY_DANGER_TRIGGER_MAX**
  - Default: 100.0

- **NAVAL_COMBAT_AIR_SUB_DETECTION_MAX**
  - Default: 10.0
  - Developer comment: those two work together in the formula f(x) = Y(x/(x+X)) where Y is MAX and X is SLOPE

- **NAVAL_COMBAT_AIR_SUB_DETECTION_SLOPE**
  - Default: 10.0
  - Developer comment: lower means sharper curve (ramps up very fast, then flatten out very fast). Must be >0

- **NAVAL_COMBAT_AIR_SUB_DETECTION_EXTERNAL_FACTOR**
  - Default: 1.0
  - Developer comment: Factor applied to the stats of external air planes

- **NAVAL_COMBAT_AIR_SUB_DETECTION_INTERNAL_EFFICIENCY_FACTOR**
  - Default: 1.0
  - Developer comment: Factor of Carrier's sortie efficiency on the stats bellow

- **NAVAL_COMBAT_AIR_AGILITY_TO_SUB_DETECTION**
  - Default: 0.0
  - Developer comment: Factor to apply to the agility of air planes active in a naval combat to deduce their contibution to sub detection

- **NAVAL_COMBAT_AIR_STRIKE_ATTACK_TO_SUB_DETECTION**
  - Default: 0.0
  - Developer comment: Same, but for strike attack (aka naval attack)

- **NAVAL_COMBAT_AIR_STRIKE_TARGETING_TO_SUB_DETECTION**
  - Default: 0.0
  - Developer comment: Same, but for strike targeting (aka naval targeting)

- **NAVAL_COMBAT_AIR_MAX_SPEED_TO_SUB_DETECTION**
  - Default: 0.0
  - Developer comment: Same, but for Max Speed

- **NAVAL_COMBAT_AIR_PLANE_COUNT_TO_SUB_DETECTION**
  - Default: 1.0
  - Developer comment: Factor applied to the number of active plane in a naval combat to deduce their contribution to sub detection

- **NAVAL_COMBAT_AIR_SUB_DETECTION_DECAY_RATE**
  - Default: 1.0
  - Developer comment: Factor to decay the value of sub detection contributed by planes on the last hour. Note: the maximum value between the decayed value and the newly computed one is taken into account. A decay rate of 1 means that nothing is carried over, the previous value is zerod out. A decay rate of 0 means that the previous value is carried over as is.

- **NAVAL_COMBAT_AIR_SUB_DETECTION_FACTOR**
  - Default: 0.0
  - Developer comment: A global factor that applies after all others, right before the sub detection contributed by plane is added to the global sub detection of a combatant

- **NAVAL_COMBAT_AIR_SUB_TARGET_SCORE**
  - Default: 10
  - Developer comment: scoring for target picking for planes inside naval combat, one define per ship typ

- **NAVAL_COMBAT_AIR_CAPITAL_TARGET_SCORE**
  - Default: 50

- **NAVAL_COMBAT_AIR_CARRIER_TARGET_SCORE**
  - Default: 200

- **NAVAL_COMBAT_AIR_CONVOY_TARGET_SCORE**
  - Default: 1.0

- **NAVAL_COMBAT_AIR_STRENGTH_TARGET_SCORE**
  - Default: 5
  - Developer comment: how much score factor from low health (scales between 0->this number)

- **NAVAL_COMBAT_AIR_LOW_AA_TARGET_SCORE**
  - Default: 5
  - Developer comment: how much score factor from low AA guns (scales between 0->this number)

- **NEW_NAVY_LEADER_LEVEL_CHANCES**
  - Default: { 0.95, 0.05 }
  - Developer comment:
    ```text
    chances for new navy leaders to start at a given level
    95% for level one
    5% for level two
    0% for level three to ten
    ```

- **NAVY_PIERCING_THRESHOLDS**
  - Default: { 2.00, 1.00, 0.75, 0.50, 0.10, 0.00 }
  - Developer comment:
    ```text
    Our piercing / their armor must be this value to deal damage fraction equal to the index in the array below [higher number = higher penetration]. If armor is 0, 1.00 will be returned.
    there isn't much point setting this higher than 0
    ```

- **NAVY_PIERCING_THRESHOLD_CRITICAL_VALUES**
  - Default: { 2.00, 1.00, 0.75, 0.50, 0.10, 0.00 }
  - Developer comment:
    ```text
    0 armor will always receive maximum damage (so add overmatching at your own peril). the system expects at least 2 values, with no upper limit.
    For criticals, you could reduce crit chance unlike damage in army combat, but we do not for now.
    ```

- **NAVY_PIERCING_THRESHOLD_DAMAGE_VALUES**
  - Default: { 1.00, 1.00, 0.70, 0.40, 0.30, 0.10 }
  - Developer comment: all of these NEED to be the same size!!!!0 armor will always receive maximum damage (so add overmatching at your own peril). the system expects at least 2 values, with no upper limit.

## NRailwayGun

- **RAILWAY_GUN_POSSIBLE_RANGES**
  - Default: { 30, 15, 45 }
  - Developer comment:
    ```text
    Possible values for railway gun range in pixel.
    -- For optimization reasons, they are listed here and equipment DB must use one of those.
    -- when writing railway gun in equipment, use the index in this array
    -- the first value in array is the default value
    ```

- **ATTACK_TO_FORTS_MODIFIER_FACTOR**
  - Default: 1.333
  - Developer comment: Forts modifier is calculated by multiplying railway gun attack value with this and dividing by 100

- **ATTACK_TO_ENTRENCHMENT_MODIFIER_FACTOR**
  - Default: 0.8
  - Developer comment: Entrenchment modifier is calculated by multiplying railway gun attack value with this and dividing by 100

- **ATTACK_TO_BOMBARDMENT_MODIFIER_FACTOR**
  - Default: 0.4
  - Developer comment: Bombardment modifier is calculated by multiplying railway gun attack value with this and dividing by 100

- **DAILY_MANPOWER_GAIN_RATIO**
  - Default: 0.05
  - Developer comment: Railway Guns will be able to gain this ratio of their max manpower daily

- **DISBAND_MANPOWER_LOSS**
  - Default: 0.0
  - Developer comment: The ration of manpower lost on disbanding railway guns

- **ENCIRCLED_DISBAND_MANPOWER_FACTOR**
  - Default: 0.2
  - Developer comment: The percentage of manpower returned when an encircled unit is disbanded

- **OUT_OF_SUPPLY_SPEED**
  - Default: -0.8
  - Developer comment: Max speed reduction from supply for railway guns

- **BASE_CAPTURE_CHANCE**
  - Default: 0.2
  - Developer comment: The base chance of railway guns being captured during an overrrun. Will be further modified by the equipment capture chance of the capturing unit.

- **ANNEX_RATIO**
  - Default: 0.5
  - Developer comment: How many railway guns will be transferred on annexation

- **HOURS_BETWEEN_REDISTRIBUTION**
  - Default: 24
  - Developer comment: Number of hours between redistribution of attached railway guns, tracked per army

- **DISTRIBUTION_RAILWAY_GUN_PRESENCE_SCORE**
  - Default: -100
  - Developer comment: Score for Railway Guns in nearby provs. x3 if on that province. x2 if adjacent. x1 if 2 away.

- **DISTRIBUTION_OUR_UNITS_PRESENCE_SCORE**
  - Default: 1
  - Developer comment: Score for our units in province when distributing Railway Guns

- **DISTRIBUTION_FRIENDLY_UNITS_PRESENCE_SCORE**
  - Default: 0
  - Developer comment: Score for friendly units in province when distributing Railway Guns

- **DISTRIBUTION_HOSTILE_UNITS_PRESENCE_SCORE**
  - Default: -45
  - Developer comment: Score for hostile units in province when distributing Railway Guns

- **DISTRIBUTION_COMBATS_PRESENCE_SCORE**
  - Default: -30
  - Developer comment: Score for combats in province when distributing Railway Guns

- **DISTRIBUTION_COMBATS_INRANGE_SCORE**
  - Default: 15
  - Developer comment: Score for combats in range when distributing Railway Guns

- **DISTRIBUTION_OUR_UNITS_INRANGE_SCORE**
  - Default: 2.5
  - Developer comment: Score for our units in range when distributing Railway Guns

- **DISTRIBUTION_FRIENDLY_UNITS_INRANGE_SCORE**
  - Default: 1.5
  - Developer comment: Score for friendly units in range when distributing Railway Guns

- **DISTRIBUTION_HOSTILE_UNITS_INRANGE_SCORE**
  - Default: 6
  - Developer comment: Score for hostile units in range when distributing Railway Guns

- **DISTRIBUTION_DISTANCE_SCORE**
  - Default: -0.08
  - Developer comment: Score for distance to province when distributing Railway Guns

- **DISTRIBUTION_PROVINCE_CONTROLLED_BY_ENEMY_SCORE**
  - Default: -3
  - Developer comment: Score for staying in province controlled by enemy

- **DISTRIBUTION_PROVINCES_CONTROLLED_BY_ENEMY_INRANGE_SCORE**
  - Default: 15
  - Developer comment: Score for provinces controlled by enemy in range when distributing Railway Guns

- **DISTRIBUTION_HOLD_POSITION_SCORE**
  - Default: 30
  - Developer comment: Score for staying in the same province when distributing Railway Guns

- **DISTRIBUTION_NO_RAILWAY_SCORE**
  - Default: -500
  - Developer comment: Score for provinces with no railways (need to be low, but we allow RG to enter port provinces without railways)

- **DISTRIBUTION_SUPPLY_DEFICIT_SCORE**
  - Default: -100
  - Developer comment: Score for provinces without sufficient supply cap

## NTrade

- **DISTANCE_TRADE_FACTOR**
  - Default: -0.02
  - Developer comment: Trade factor is modified by distance times this

- **RELATION_TRADE_FACTOR**
  - Default: 1
  - Developer comment: Trade factor is modified by Opinion value times this

- **ALLOW_TRADE_CUT_OFF**
  - Default: 0
  - Developer comment: If trade factor is less than this, no trade will be allowed

- **MONTH_TRADE_FACTOR**
  - Default: 2
  - Developer comment: Each month a trade gets this much boost to it's trade factor

- **MAX_MONTH_TRADE_FACTOR**
  - Default: 50
  - Developer comment: This is the maximum bonus that can be gained from time

- **BASE_TRADE_FACTOR**
  - Default: 150
  - Developer comment: This is the base trade factor

- **PUPPET_MASTER_TRADE_FACTOR**
  - Default: 400
  - Developer comment: This is priority for puppet master

- **PUPPET_TRADE_FACTOR**
  - Default: 0
  - Developer comment: This is unpriority for puppets

- **BASE_LAND_TRADE_RANGE**
  - Default: 1000

- **PARTY_SUPPORT_TRADE_FACTOR**
  - Default: 50
  - Developer comment: Trade factor bonus at the other side having 100 % party popularity for my party

- **ANTI_MONOPOLY_TRADE_FACTOR_THRESHOLD**
  - Default: 0.5
  - Developer comment: What percentage of resources has to be sold to the buyer for the anti-monopoly factor to take effect

- **ANTI_MONOPOLY_TRADE_FACTOR**
  - Default: -100
  - Developer comment: This is added to the factor value when anti-monopoly threshold is exceeded

- **NAVAL_ROUTE_ACCESS_AVOID_COST_MULT**
  - Default: 1
  - Developer comment: Naval pathfinding should avoid certain regions that you mark. High "cost multiplier" will make it less willingly go through a specific region.

## NAI

- **GARRISON_FRACTION**
  - Default: 0.0
  - Developer comment: How large part of a front should always be holding the line rather than advancing at the enemy

- **THEORIST_SCALING_WEIGHT_FACTOR_PER_NON_POLITICAL_ADVISORS**
  - Default: 0.15
  - Developer comment: Scale theorist weight by this * num non political advisors

- **DIPLOMATIC_ACTION_GOOD_BAD_RATIO_THRESHOLD**
  - Default: 1

- **BASE_RELUCTANCE**
  - Default: 20
  - Developer comment: Base reluctance applied to all diplomatic offers

- **DIPLOMATIC_ACTION_RANDOM_FACTOR**
  - Default: 0.5
  - Developer comment: How much of the AI diplomatic action scoring is randomly determined (1.0 = half random, 2.0 = 2/3rd random, etc)

- **DIPLOMATIC_ACTION_PROPOSE_SCORE**
  - Default: 50
  - Developer comment: AI must score a diplomatic action at least this highly to propose it themselves

- **DILPOMATIC_ACTION_DECLARE_WAR_WARGOAL_BASE**
  - Default: 50
  - Developer comment: Base diplomatic action score bonus to go to war per wargoal

- **DIPLOMATIC_ACTION_BREAK_SCORE**
  - Default: -10
  - Developer comment: AI must score a diplomatic action less than this to break it off

- **DIPLOMACY_CREATE_FACTION_FACTOR**
  - Default: 0.75
  - Developer comment: Factor for AI desire to create a new faction. Val < 1.0 makes it less likely to create than to join.

- **DIPLOMACY_FACTION_WRONG_IDEOLOGY_PENALTY**
  - Default: 60
  - Developer comment: AI penalty for diplomatic faction acitons between nations of different ideologies

- **DIPLOMACY_FACTION_SAME_IDEOLOGY_MAJOR**
  - Default: 10
  - Developer comment: AI bonus acceptance when being asked about faction is a major of the same ideology

- **DIPLOMACY_FACTION_NEUTRALITY_PENALTY**
  - Default: 50
  - Developer comment: Neutral nations have a separate penalty, not wanting to get involved at all, rather than caring much about the difference in ideology

- **DIPLOMACY_FACTION_GLOBAL_TENSION_FACTOR**
  - Default: 0.2
  - Developer comment: How much the AI takes global tension into account when considering faction actions

- **DIPLOMACY_FACTION_WAR_RELUCTANCE**
  - Default: -50
  - Developer comment: Penalty to desire to enter a faction with a country that we are not fighting wars together with.

- **DIPLOMACY_FACTION_TAKE_OVER_RELUCTANCE_VERSUS_HUMAN**
  - Default: 2.0
  - Developer comment: Multiplier penalty for how much stronger than a human faction member an AI country must be to choose to assume faction leadership.

- **DIPLOMACY_SCARED_MINOR_EXTRA_RELUCTANCE**
  - Default: -50
  - Developer comment: extra reluctance to join stuff as scared minor

- **DIPLOMACY_FACTION_PLAYER_JOIN**
  - Default: 20
  - Developer comment: Bonus for human players asking to join a faction.

- **DIPLOMACY_BOOST_PARTY_COST_FACTOR**
  - Default: 100.0
  - Developer comment: Desire to boost party popularity subtracts the daily cost multiplied by this

- **DIPLOMACY_IMPROVE_RELATION_COST_FACTOR**
  - Default: 5.0
  - Developer comment: Desire to boost relations subtracts the cost multiplied by this

- **DIPLOMACY_IMPROVE_RELATION_PP_FACTOR**
  - Default: 0.1
  - Developer comment: Desire to boost relations adds total PP multiplied by this

- **DIPLOMACY_SEND_ATTACHE_COST_FACTOR**
  - Default: 5.0
  - Developer comment: Desire to send attache substracts the cost multiplied by this

- **DIPLOMACY_SEND_ATTACHE_PP_FACTOR**
  - Default: 0.1
  - Developer comment: Desire to send attache adds total PP multiplied by this

- **DIPLOMACY_REJECTED_WAIT_MONTHS_BASE**
  - Default: 4
  - Developer comment: AI will not repeat offers until at least this time has passed, and at most the double

- **DIPLOMACY_LEND_LEASE_MONTHS_TO_CANCEL**
  - Default: 1
  - Developer comment: AI will not cancel a lend lease offer until this time has passed

- **DIPLOMACY_CALL_ALLY_VALIDITY_DURATION**
  - Default: 1
  - Developer comment: Overwrite above value for CallAlly and JoinAlly diplo action. This is however fixed, and is not subject to randomness. Also, this is the time the AI will keep the action in its incoming queue without declining it.

- **DIPLOMACY_PURCHASE_EQUIPMENT_MONTHS**
  - Default: 2
  - Developer comment: AI will not ask to purchase equipment more often than this

- **DIPLOMACY_SEND_MAX_FACTION**
  - Default: 0.75
  - Developer comment: Country should not send away more units than this as expeditionaries

- **DIPLOMACY_ACCEPT_VOLUNTEERS_BASE**
  - Default: 50
  - Developer comment: Base value of volunteer acceptance (help is welcome)

- **DIPLOMACY_ACCEPT_ATTACHE_BASE**
  - Default: 50
  - Developer comment: Base value of attache acceptance (help is welcome)

- **DIPLOMACY_ACCEPT_ATTACHE_OPINION_TRASHHOLD**
  - Default: 20
  - Developer comment: Value of opinion that will remove accepting penalty for receiveing the attache

- **DIPLOMACY_ACCEPT_ATTACHE_OPINION_PENALTY**
  - Default: -100
  - Developer comment: Value of acceptance penalty if the opinion too low

- **DIPLOMACY_FACTION_MAJOR_AT_WAR**
  - Default: 1000.0
  - Developer comment: Factor that will be multiplied with the surrender level in the desire to offer to the other ai to join a faction

- **DIPLOMACY_FACTION_SURRENDER_LEVEL**
  - Default: 20
  - Developer comment: How much the recipient nation losing matters for joining a faction

- **DIPLO_PREFER_OTHER_FACTION**
  - Default: -200
  - Developer comment: The country has yet to ask some other faction it would prefer to be a part of.

- **DIPLO_DISTANCE_BETWEEN_CAPITALS**
  - Default: -340
  - Developer comment: Max scaled malus from distance between capitals

- **DIPLO_ACCEPTABLE_DISTANCE_BETWEEN_CAPITALS**
  - Default: 1000.0
  - Developer comment: When scaled distance malus begins to kick in. At double this value, max penalty (above) is achieved

- **DIPLO_SHOW_FACTION_JOIN_WARNING_THRESHOLD**
  - Default: -20
  - Developer comment: Show warning if declare-war target is this close to accepting or being sent a faction invitiation

- **DIPLO_MAX_CONTAINMENT_ACCEPTANCE**
  - Default: 100
  - Developer comment: Max value for 'wants to contain' diplo acceptance

- **RESEARCH_DAYS_BETWEEN_WEIGHT_UPDATE**
  - Default: 7
  - Developer comment: Refreshes need scores based on country situation.

- **RESEARCH_WEIGHT_TRUNCATION_THRESHOLD**
  - Default: 0.75
  - Developer comment: When choosing a tech to research, use this truncation selection threshold. (for example, if the top score is 10, a threshold of 0.75 will pick randomly from anything above 7.5 score)

- **RESEARCH_LAND_DOCTRINE_NEED_GAIN_FACTOR**
  - Default: 0.15
  - Developer comment: Multiplies value based on relative military industry size / country size.

- **RESEARCH_NAVAL_DOCTRINE_NEED_GAIN_FACTOR**
  - Default: 0.05
  - Developer comment: Multiplies value based on relative naval industry size / country size.

- **RESEARCH_AIR_DOCTRINE_NEED_GAIN_FACTOR**
  - Default: 0.07
  - Developer comment: Multiplies value based on relative number of air base / country size.

- **RESEARCH_NEW_DOCTRINE_RANDOM_FACTOR**
  - Default: 0.05
  - Developer comment: How much randomness is allowed to contribute to do new research expressed as a factor of total tech weights. Higher means more random exploration.

- **RESEARCH_AHEAD_BONUS_FACTOR**
  - Default: 4.0
  - Developer comment: To which extent AI should care about ahead of time bonuses to research

- **RESEARCH_BONUS_FACTOR**
  - Default: 5.0
  - Developer comment: To which extent AI should care about research speed bonuses

- **RESEARCH_YEARS_BEHIND_FACTOR**
  - Default: 0.2
  - Developer comment: To which extent AI should care about not falling behind (i.e. increase weight for old tech)

- **RESEARCH_NEEDS_FACTOR**
  - Default: 0.01
  - Developer comment: To which extent AI should care about its research needs (research needs are matched against the tech category)

- **RESEARCH_LENGTH_FACTOR**
  - Default: 3
  - Developer comment: To which extent AI should care about how long it takes to research something (it prefers short research times)

- **MAX_AHEAD_RESEARCH_PENALTY**
  - Default: 3
  - Developer comment: Max ahead of time penalty AI will ever consider (this also includes BASE_YEAR_AHEAD_PENALTY_FACTOR, so not the raw time)

- **RESEARCH_AHEAD_OF_TIME_FACTOR**
  - Default: 4.0
  - Developer comment: To which extent AI should care about ahead of time penalties to research

- **RESEARCH_BASE_DAYS**
  - Default: 60
  - Developer comment: AI adds a base number of days when weighting completion time for techs to ensure it doesn't only research quick techs

- **DECLARE_WAR_RELATIVE_FORCE_FACTOR**
  - Default: 0.5
  - Developer comment: Weight of relative force between nations that consider going to war

- **TRADEABLE_FACTORIES_FRACTION**
  - Default: 0.8
  - Developer comment: Will at most trade away this fraction of factories.

- **MIN_DELIVERED_TRADE_FRACTION**
  - Default: 0.8
  - Developer comment: AI will cancel trade deals that are not able to deliver more than this fraction of the agreed amount

- **SEA_PATH_LENGTH_SCORE_BASE**
  - Default: -30
  - Developer comment: scoring reduction from naval paths for AI when picking trade partners

- **MINIMUM_GOOD_TRADE_RATIO_PER_CIV**
  - Default: 0.005
  - Developer comment: for each civ factory we have mul with this we are allowed to trade under % of resource on a trade

- **NAVAL_DOCKYARDS_SHIP_FACTOR**
  - Default: 1.5
  - Developer comment: The extent to which number of dockyards play into amount of sips a nation wants

- **PRODUCTION_EQUIPMENT_SURPLUS_FACTOR**
  - Default: 0.5
  - Developer comment: Base value for how much of currently used equipment the AI will at least strive to have in stock

- **PRODUCTION_EQUIPMENT_SURPLUS_FACTOR_GARRISON**
  - Default: 0.3
  - Developer comment: Base value for how much of currently used equipment the AI will at least strive to have in stock for garrison forces

- **AIR_SUPERIORITY_FACTOR**
  - Default: 2.5
  - Developer comment: Factor for air superiority score

- **ROCKET_MIN_ASSIGN_SCORE**
  - Default: 10
  - Developer comment: Minimum total score for region to be considered for rocket air missions

- **ROCKET_MIN_PRIO_ASSIGN_SCORE**
  - Default: 50
  - Developer comment: Minimum total score for region to be considered for critical rocket air missions

- **ROCKET_ASSIGN_SCORE_REDUCTION_PER_ASSIGNMENT**
  - Default: 0.5
  - Developer comment: each assigned rocket reduces the score of a region by this amount

- **MAX_VOLUNTEER_ARMY_FRACTION**
  - Default: 0.25
  - Developer comment: Countries will not send more than their forces time this number to aid another country

- **DEPLOY_MIN_TRAINING_SURRENDER_FACTOR**
  - Default: 0.5
  - Developer comment: Required percentage of training (1.0 = 100%) for AI to deploy unit in wartime while surrender progress is higher than 0

- **DEPLOY_MIN_EQUIPMENT_SURRENDER_FACTOR**
  - Default: 0.90
  - Developer comment: Required percentage of equipment (1.0 = 100%) for AI to deploy unit in wartime while surrender progress is higher than 0

- **DEPLOY_MIN_TRAINING_PEACE_FACTOR**
  - Default: 0.98
  - Developer comment: Required percentage of training (1.0 = 100%) for AI to deploy unit in peacetime

- **DEPLOY_MIN_EQUIPMENT_PEACE_FACTOR**
  - Default: 0.98
  - Developer comment: Required percentage of equipment (1.0 = 100%) for AI to deploy unit in peacetime

- **DEPLOY_MIN_TRAINING_WAR_FACTOR**
  - Default: 0.95
  - Developer comment: Required percentage of training (1.0 = 100%) for AI to deploy unit in wartime

- **DEPLOY_MIN_EQUIPMENT_WAR_FACTOR**
  - Default: 0.95
  - Developer comment: Required percentage of equipment (1.0 = 100%) for AI to deploy unit in wartime

- **DEPLOY_MIN_EQUIPMENT_CAP_DEPLOY_FACTOR**
  - Default: 0.85
  - Developer comment: If training is capped by equipment deficit and we have reached that cap, deploy unit anyway if percentage is above this (reinforce in field instead).

- **DYNAMIC_STRATEGIES_THREAT_FACTOR**
  - Default: 4.0
  - Developer comment: How much threat generated by other countries effects generated strategies

- **LOCATION_BALANCE_TO_ADVANCE**
  - Default: 0.0
  - Developer comment: Limit on location strength balance between country and enemy for unit to dare to move forward.

- **EQUIPMENT_MARKET_UPDATE_FREQUENCY_DAYS**
  - Default: 11
  - Developer comment: How often the AI runs its market logic

- **EQUIPMENT_MARKET_MAX_CIVS_FOR_PURCHASES_RATIO**
  - Default: 0.1
  - Developer comment:
    ```text
    Ratio of available civilian factories to max use for equipment purchases (0.2 = 20 %, so 50 available civs would mean max ca 10 civs to spend on purchases at any one time). Gets modified by equipment_market_spend_factories AI strategy.
    ```

- **EQUIPMENT_MARKET_BASE_MARKET_RATIO**
  - Default: 0.2
  - Developer comment: The AI tries to keep ca this ratio of equipment surplus for sale on the market. Gets modified by equipment_market_for_sale_factor AI strategy.

- **EQUIPMENT_MARKET_DEFAULT_CIC_CHUNK_FOR_SALE**
  - Default: 150.0
  - Developer comment:
    ```text
    When putting things up for sale on the market, this determines the default "chunk" size of equipment the AI puts up. Gets overridden by equipment_market_min_for_sale AI strategy. (If one equipment is worth 5 CIC, a value of 150 would result in chunk sizes of 150/5 = 30 units)
    ```

- **EQUIPMENT_MARKET_NR_DELIVERIES_SOFT_MAX**
  - Default: 10
  - Developer comment: AI tries to adjust assigned factories and amount of equipment to keep nr deliveries at max this

- **EQUIPMENT_MARKET_EXTRA_CONVOYS_OVERRIDE**
  - Default: 2
  - Developer comment: Makes the AI able to buy convoys even if they are lacking free convoys. 0 will make them stop this behavior, anything > 0 will allow overriding the perceived nr of free convoys. Only if convoy equipment has a non-zero weight does the actual value matter.

- **EQUIPMENT_MARKET_WANTED_CONVOY_USAGE_RATIO**
  - Default: 0.3
  - Developer comment: If the AI's available/free/unused convoys is reduced to this ratio (0.3 = 30 %), start buying convoys.

- **EQUIPMENT_MARKET_CONTRACT_DURATION_ACCEPTANCE**
  - Default: -10
  - Developer comment: If expected contract duration is longer than EQUIPMENT_MARKET_NR_DELIVERIES_SOFT_MAX deliveries, then add this to the PurchaseContract AI acceptance score per nr overdue deliveries

- **EQUIPMENT_MARKET_CONTRACT_EFFICIENCY_TO_CANCEL**
  - Default: 0.1
  - Developer comment: If contract efficiency stays below this, the AI will cancel the contract

- **EQUIPMENT_MARKET_EQUIPMENT_SUNK_TO_CANCEL**
  - Default: 0.5
  - Developer comment: If more equipment is sunk then the given percentage, the AI will cancel the contract

- **EQUIPMENT_MARKET_SHORTAGE_DAYS_TO_CANCEL**
  - Default: 30
  - Developer comment: If equipment deficit will take more than these many days to fix, the AI will cancel the contract

- **EQUIPMENT_MARKET_MAX_CONVOY_RATIO_FOR_MARKET_PEACE**
  - Default: 0.5
  - Developer comment: Max ratio of total convoys to use for equipment trade while at peace

- **EQUIPMENT_MARKET_MAX_CONVOY_RATIO_FOR_MARKET_WAR**
  - Default: 0.25
  - Developer comment: Max ratio of total convoys to use for equipment trade while at war

- **EQUIPMENT_MARKET_SCORE_FACTOR_VARIANT_SCORE**
  - Default: 5.0
  - Developer comment: Score coefficient for VariantScore (high is good)

- **EQUIPMENT_MARKET_SCORE_FACTOR_CIC_VALUE_NEEDED**
  - Default: 8.0
  - Developer comment: Score coefficient for CicValueNeeded (high is prio)

- **EQUIPMENT_MARKET_SCORE_FACTOR_SUBSIDY_VALUE**
  - Default: 2.0
  - Developer comment: Score coefficient for SubsidyValue (high is good)

- **EQUIPMENT_MARKET_SCORE_FACTOR_COST_PER_UNIT**
  - Default: -5.0
  - Developer comment: Score coefficient for SubsidizedCostPerUnit (low is good)

- **EQUIPMENT_MARKET_SCORE_FACTOR_AI_STRAT_WEIGHT**
  - Default: 50.0
  - Developer comment: Score coefficient for AiStratWeight (high is prio)

- **EQUIPMENT_MARKET_SCORE_FACTOR_DIPLO_OPINION**
  - Default: 1.0
  - Developer comment: Score coefficient for DiploOpinion, mainly used as tie breaker (high is good)

- **DIPLOMACY_ACCEPT_CONDITIONAL_SURRENDER_MANPOWER_IN_FIELD**
  - Default: -20
  - Developer comment: Scale multiplied by difference in manpower in field

- **DIPLOMACY_ACCEPT_CONDITIONAL_SURRENDER_GLOBAL_TENSION**
  - Default: -10
  - Developer comment: Multiplied by WT

- **DIPLOMACY_ACCEPT_CONDITIONAL_SURRENDER_WAR_SUPPORT**
  - Default: -10
  - Developer comment: Multiplied by recipient WS

- **DIPLOMACY_ACCEPT_CONDITIONAL_SURRENDER_EMBARGO**
  - Default: 2
  - Developer comment: Multiplied by num embargo, max 5 embargo

- **DIPLOMACY_ACCEPT_CONDITIONAL_SURRENDER_OWN_SURRENDER_LIMIT**
  - Default: 20
  - Developer comment: Multiplied by recipient nation's surrender level

- **DIPLOMACY_ACCEPT_CONDITIONAL_SURRENDER_MINOR_WAR**
  - Default: 10
  - Developer comment: Applied if recipient is a minor nation (and therefore there are no majors in this war)

- **MIN_POLITICAL_POWER_MONTHLY_GAIN_FOR_IMPROVE_RELATIONS**
  - Default: 0.50
  - Developer comment: If country makes less than this PP per month, they won't improve relations

- **NUM_RESOURCES_TO_ALLOW_MINOR_EMBARGO**
  - Default: 69
  - Developer comment: If we or any of our puppets have more total resources of a single category that this, we will consider embargoing countries

- **EMBARGO_WORLD_TENSION_THREAT_DIVISOR**
  - Default: 2.5
  - Developer comment: A divisor to generated world tension when applying how much we care about it in AI desire

- **OPINION_CUTOFF_FOR_IMPROVE_RELATIONS**
  - Default: 80
  - Developer comment: AI will never consider improving relations if above this opinion with target.

- **DEFAULT_MODULE_VARIANT_CREATION_XP_CUTOFF_LAND**
  - Default: 35
  - Developer comment: Army XP needed before attempting to create a variant of a type that uses the tank designer (the tank designer DLC feature must be active).

- **DEFAULT_MODULE_VARIANT_CREATION_XP_CUTOFF_NAVY**
  - Default: 50
  - Developer comment: Same as above but for the ship designer.

- **DEFAULT_MODULE_VARIANT_CREATION_XP_CUTOFF_AIR**
  - Default: 25
  - Developer comment: Same as above but for the plane designer.

- **DEFAULT_LEGACY_VARIANT_CREATION_XP_CUTOFF_LAND**
  - Default: 35
  - Developer comment: Army XP needed before attempting to create a variant of a type that uses the legacy upgrades system. ai_strategy supports land_xp_spend_priority upgrade_xp_cutoff. If none is set, this define is used instead.

- **DEFAULT_LEGACY_VARIANT_CREATION_XP_CUTOFF_NAVY**
  - Default: 25
  - Developer comment: Same as above but for navy XP and navy_xp_spend_priority.

- **DEFAULT_LEGACY_VARIANT_CREATION_XP_CUTOFF_AIR**
  - Default: 25
  - Developer comment: Same as above but for air XP and air_xp_spend_priority.

- **VARIANT_CREATION_XP_RESERVE_LAND**
  - Default: 50
  - Developer comment: If the AI lacks army XP to create a variant it will reserve this much XP for variant creation so that it will eventually be able to create a variant.

- **VARIANT_CREATION_XP_RESERVE_NAVY**
  - Default: 50
  - Developer comment: Same as above but for navy XP.

- **VARIANT_CREATION_XP_RESERVE_AIR**
  - Default: 50
  - Developer comment: Same as above but for air XP.

- **LAND_DESIGN_ALTERNATIVE_ABSENT**
  - Default: 1000000
  - Developer comment:
    ```text
    The AI uses the below values when selecting which design to make among the types that use the tank designer
    (the tank designer DLC feature must be active). For each role, the highest priority AI design that can be
    created, if any, is assigned a weight. Any design with a weight of zero or a weight that falls below the
    cutoff is dropped. A random design is then picked from the remaining.
    Weight is calculated as AlternativeFactor * DemandFactor.
    An "alternative" is a producible design of the same archetype (each specialized type is its own archetype).
    ```

- **LAND_DESIGN_ALTERNATIVE_OF_LESSER_TECH**
  - Default: 10000

- **LAND_DESIGN_ALTERNATIVE_OF_EQUAL_TECH**
  - Default: 100

- **LAND_DESIGN_ALTERNATIVE_OF_GREATER_TECH**
  - Default: 1

- **LAND_DESIGN_DEMAND_FIELD_DIVISION**
  - Default: 20
  - Developer comment:
    ```text
    If a template may be reinforced with the archetype it's considered to be "demanded". If multiple conditions
    are met, e.g. it's both in the field and in training, the largest value is used.
    ```

- **LAND_DESIGN_DEMAND_TRAINING_DIVISION**
  - Default: 15

- **LAND_DESIGN_DEMAND_GARRISON_DIVISION**
  - Default: 10

- **LAND_DESIGN_DEMAND_UNUSED_TEMPLATE**
  - Default: 1

- **LAND_DESIGN_DEMAND_ABSENT**
  - Default: 0

- **LAND_DESIGN_CUTOFF_AS_PERCENTAGE_OF_MAX**
  - Default: 0.25
  - Developer comment:
    ```text
    If a design with a weight when divided by the largest weight falls below this value it's excluded from the
    selection. Valid values are in the range [0, 1] inclusive.
    ```

- **AIR_DESIGN_ALTERNATIVE_ABSENT**
  - Default: 1000000
  - Developer comment: See above documentation.

- **AIR_DESIGN_ALTERNATIVE_OF_LESSER_TECH**
  - Default: 10000

- **AIR_DESIGN_ALTERNATIVE_OF_EQUAL_TECH**
  - Default: 100

- **AIR_DESIGN_ALTERNATIVE_OF_GREATER_TECH**
  - Default: 1

- **AIR_DESIGN_DEMAND_MAX**
  - Default: 33
  - Developer comment:
    ```text
    The AI desires to produce equipment at a certain rate per archetype, and demand is determined per archetype
    relative to the least and most desired counts.
    ```

- **AIR_DESIGN_DEMAND_MIN**
  - Default: 1

- **AIR_DESIGN_DEMAND_ABSENT**
  - Default: 0

- **AIR_DESIGN_CUTOFF_AS_PERCENTAGE_OF_MAX**
  - Default: 0.34

- **DESIRE_USE_XP_TO_UNLOCK_LAND_DOCTRINE**
  - Default: 0.5
  - Developer comment:
    ```text
    The AI "desires" to spend XP on doctrines, templates, and equipment.
    The desire is built up over time and when XP is available it spends it on the action that has the highest accumulated desire. After spending XP the desire is reset, in effect balancing the desires.
    Below is the daily desire gain for each action.
    How quickly is desire to unlock land doctrines accumulated?
    ```

- **DESIRE_USE_XP_TO_UNLOCK_NAVAL_DOCTRINE**
  - Default: 0.5
  - Developer comment: How quickly is desire to unlock naval doctrines accumulated?

- **DESIRE_USE_XP_TO_UNLOCK_AIR_DOCTRINE**
  - Default: 0.5
  - Developer comment: How quickly is desire to unlock air doctrines accumulated?

- **DESIRE_USE_XP_TO_UPDATE_LAND_TEMPLATE**
  - Default: 2.0
  - Developer comment: How quickly is desire to update/create templates accumulated?

- **DESIRE_USE_XP_TO_UPGRADE_LAND_EQUIPMENT**
  - Default: 1.0
  - Developer comment: How quickly is desire to update/create land equipment variants accumulated?

- **DESIRE_USE_XP_TO_UPGRADE_NAVAL_EQUIPMENT**
  - Default: 1.0
  - Developer comment: How quickly is desire to update/create naval equipment variants accumulated?

- **DESIRE_USE_XP_TO_UPGRADE_AIR_EQUIPMENT**
  - Default: 1.0
  - Developer comment: How quickly is desire to update/create air equipment variants accumulated?

- **DESIRE_USE_XP_TO_UNLOCK_ARMY_SPIRIT**
  - Default: 0.20
  - Developer comment: How quickly is desire to unlock army spirits accumulated?

- **DESIRE_USE_XP_TO_UNLOCK_NAVY_SPIRIT**
  - Default: 0.20
  - Developer comment: How quickly is desire to unlock naval spirits accumulated?

- **DESIRE_USE_XP_TO_UNLOCK_AIR_SPIRIT**
  - Default: 0.25
  - Developer comment: How quickly is desire to unlock air spirits accumulated?

- **DAYS_BETWEEN_CHECK_BEST_DOCTRINE**
  - Default: 7
  - Developer comment: Recalculate desired best doctrine to unlock with this many days inbetween.

- **DAYS_BETWEEN_CHECK_BEST_TEMPLATE**
  - Default: 7
  - Developer comment: Recalculate desired best template to upgrade with this many days inbetween.

- **DAYS_BETWEEN_CHECK_BEST_EQUIPMENT**
  - Default: 7
  - Developer comment: Recalculate desired best equipment to upgrade with this many days inbetween.

- **UNLOCK_SPIRIT_AI_WILL_DO_FACTOR**
  - Default: 20
  - Developer comment: Factor for scripted ai_will_do value

- **UNLOCK_SPIRIT_MODIFIER_FACTOR**
  - Default: 0.05
  - Developer comment: Factor for AI's evaluated value of the modifiers connected to the spirit

- **UNLOCK_SPIRIT_USE_TRUNCATION_SELECT**
  - Default: false
  - Developer comment: Whether to use truncation select or roulette-wheel select. Set threshold for truncation select below.

- **UNLOCK_SPIRIT_TRUNCATION_SELECT_THRESHOLD**
  - Default: 0.8
  - Developer comment:
    ```text
    Valid between [0.0, 1.0]. When unlocking spirits, select randomly from all spirits with AI score >= VALUE * HighestSpiritScore. To always select the best, set this value to 1.0. To select fully randomly, set this value to 0.0.
    ```

- **FOCUS_TREE_CONTINUE_FACTOR**
  - Default: 1.5
  - Developer comment: Factor for score of how likely the AI is to keep going down a focus tree rather than starting a new path.

- **PLAN_VALUE_TO_EXECUTE**
  - Default: -0.5
  - Developer comment: AI will typically avoid carrying out a plan it below this value (0.0 is considered balanced).

- **DECLARE_WAR_NOT_NEIGHBOR_FACTOR**
  - Default: 0.25
  - Developer comment: Multiplier applied before force factor if country is not neighbor with the one it is considering going to war

- **CALL_ALLY_BASE_DESIRE**
  - Default: 20
  - Developer comment: exactly what it says

- **CALL_ALLY_DEMOCRATIC_DESIRE**
  - Default: 50
  - Developer comment: Desire to call ally added for democratic AI

- **CALL_ALLY_NEUTRAL_DESIRE**
  - Default: 25
  - Developer comment: Desire to call ally added for neutral AI

- **CALL_ALLY_FASCIST_DESIRE**
  - Default: -10
  - Developer comment: Desire to call ally added for fascist AI

- **CALL_ALLY_COMMUNIST_DESIRE**
  - Default: 75
  - Developer comment: Desire to call ally added for communist AI

- **CALL_ALLY_PUPPET_INVITE_OVERLORD**
  - Default: 1000
  - Developer comment: Desire for a puppet to call its overlord into the war

- **CALL_ALLY_OVERLORD_INVITE_PUPPET**
  - Default: 20
  - Developer comment: Desire for an overlord to call its puppet into the war

- **CALL_ALLY_RELATIVE_INDUSTRY_STRENGTH_THRESHOLD**
  - Default: 1.5
  - Developer comment: If our relative industry strength ratio is less than this (compared to all enemies), increase desire to call allies

- **CALL_ALLY_RELATIVE_ARMY_STRENGTH_THRESHOLD**
  - Default: 1.5
  - Developer comment: If our relative army strength ratio is less than this (compared to all enemies), increase desire to call allies

- **CALL_ALLY_RELATIVE_INDUSTRY_STRENGTH_MAX**
  - Default: 50.0
  - Developer comment: Max desire value for relative industry strength (lerping between zero and this based on the threshold)

- **CALL_ALLY_RELATIVE_ARMY_STRENGTH_MAX**
  - Default: 100.0
  - Developer comment: Max desire value for relative army strength (lerping between zero and this based on the threshold)

- **CALL_ALLY_LOSING_WAR_THRESHOLD**
  - Default: 0.45
  - Developer comment: If our war progress is less than this, increase desire to call allies (0.5 is stalemate)

- **CALL_ALLY_LOSING_WAR_MAX**
  - Default: 100.0
  - Developer comment: Max desire value for losing war (lerping between zero and this based on the threshold)

- **CALL_ALLY_WAR_LENGTH_NR_MONTHS**
  - Default: 2
  - Developer comment: For every month the war has gone on, increase desire this much

- **CALL_ALLY_JOINER_HAS_ENEMY_NEIGHBOR**
  - Default: 100
  - Developer comment: If the joining country is neighbor to at least one of the enemies, increase desire this much

- **AI_CHAIN_CALLS_ALLIES**
  - Default: true
  - Developer comment: with this enabled the AI will automatically call AI allies when called into a war (which in turn generates a single popup, this circumvents some potential modfiable scripts with the call ally diplo action, which might be a cause to disable it in some mods

- **MIN_AI_UNITS_PER_TILE_FOR_STANDARD_COHESION**
  - Default: 1.5
  - Developer comment: How many units should we have for each tile along a front in order to switch to standard cohesion (less moving around)

- **MIN_FRONT_SIZE_TO_CONSIDER_STANDARD_COHESION**
  - Default: 12
  - Developer comment: How long should fronts be before we consider switching to standard cohesion (under this, standard cohesion fronts will switch back to relaxed)

- **JOIN_ALLY_BASE_DESIRE**
  - Default: 20
  - Developer comment: exactly what it says

- **JOIN_ALLY_DEMOCRATIC_DESIRE**
  - Default: 50
  - Developer comment: Desire to join ally added for democratic AI

- **JOIN_ALLY_NEUTRAL_DESIRE**
  - Default: 25
  - Developer comment: Desire to join ally added for neutral AI

- **JOIN_ALLY_FASCIST_DESIRE**
  - Default: -10
  - Developer comment: Desire to join ally added for fascist AI

- **JOIN_ALLY_COMMUNIST_DESIRE**
  - Default: 75
  - Developer comment: Desire to join ally added for communist AI

- **JOIN_FACTION_BOTH_LOSING**
  - Default: -300
  - Developer comment: Desire to be in a faction when both we and htey are in losing wars

- **LENDLEASE_FRACTION_OF_PRODUCTION**
  - Default: 0.5
  - Developer comment: Base fraction AI would send as lendlease

- **LENDLEASE_FRACTION_OF_STOCKPILE**
  - Default: 0.25
  - Developer comment: Base fraction AI would send as lendlease

- **MINIMUM_EQUIPMENT_TO_ASK_LEND_LEASE**
  - Default: -100
  - Developer comment: AI will accept to lend lease this equipment only if our stockpile is less than that.

- **MINIMUM_CONVOY_TO_ASK_LEND_LEASE**
  - Default: 30
  - Developer comment: AI will accept to lend lease convoys only if our stockpile is less than that (special case because convoy stockpile can't be negative).

- **MINIMUM_FUEL_DAYS_TO_ASK_LEND_LEASE**
  - Default: 2
  - Developer comment: AI will accept to lend lease fuel only if the player have less fuel than this number multiply by his max daily consumption.

- **MINIMUM_FUEL_DAYS_TO_ACCEPT_LEND_LEASE**
  - Default: 10
  - Developer comment: AI will accept to lend lease fuel only if they have more fuel than this number multiply by their max daily consumption. Note that for a GiE asking to its host, we divide this number by 2.

- **DEFAULT_SUPPLY_TRUCK_BUFFER_RATIO**
  - Default: 1.5
  - Developer comment: ai will set to truck buffer ratio to this. can be modified by wanted_supply_trucks min_wanted_supply_trucks ai strats

- **DEFAULT_SUPPLY_TRAIN_NEED_FACTOR**
  - Default: 1.2
  - Developer comment: AI multiplies current train usage by this to determine desired nr of wanted trains. Can be modified by wanted_supply_train min_wanted_supply_trains ai strats.

- **POLITICAL_IDEA_MIN_SCORE**
  - Default: 0.1
  - Developer comment: Only replace or add an idea if score is above this score.

- **HIGH_COMMAND_ADDED_WEIGHT_FACTOR**
  - Default: 0.25
  - Developer comment: Weight multiplier for high_command advisors over other chosen advisor or idea types

- **CHIEF_ADDED_WEIGHT_FACTOR**
  - Default: 12.5
  - Developer comment: Weight multiplier for chief roles over other advisor or idea types

- **GARRISON_TEMPLATE_SCORE_IC_FACTOR**
  - Default: 1.0
  - Developer comment: ai uses these defines while calculating garrison template score of a template.

- **GARRISON_TEMPLATE_SCORE_MANPOWER_FACTOR**
  - Default: 0.05
  - Developer comment: formula is (template_ic * ic_factor + template_manpower * manpower_factor ) / template_supression (lower is better)

- **ADVISOR_SCORE_TRAIT_MODIFIER_FACTOR**
  - Default: 0.2
  - Developer comment: When scoring advisors, factor the score contribution from the advisor's trait modifiers by this value

- **ADVISOR_SCORE_CHEAPER_IS_BETTER_FACTOR**
  - Default: 0.1
  - Developer comment: When scoring advisors, this define scales how much the AI prefers cheaper advisors over more expensive ones. 0.0 means no effect, 0.15 means a cost difference of 100 PP modifies the score by 15 %.

- **ADVISOR_SCORE_CHEAPER_IS_BETTER_MIN**
  - Default: 0.5
  - Developer comment: Clamps the above scoring factor to at minimum this value

- **EVAL_MODIFIER_NON_PERCENT_FACTOR**
  - Default: 0.1
  - Developer comment:
    ```text
    stuff related to how the AI evaluates/scores how useful modifiers are
    Multiply non-percent-based modifiers with this to put the values in the approximately same range so they can be compared. (Why we are using 0.1 and not 0.01? No idea...)
    ```

- **EVAL_MODIFIER_UNSPECIFIED_CATEGORY_FACTOR**
  - Default: 0.75
  - Developer comment: Arbitrary scoring factor for modifiers the AI doesn't know how to categorize

- **EVAL_MODIFIER_MAX_COMMAND_POWER_FACTOR**
  - Default: 0.01
  - Developer comment: Increasing CP cap with x is maybe 100 times less useful than e.g. gaining x more XP per day

- **MIN_AI_SCORE_TO_MOBILIZATION_LAW_OVERRIDE_HARD_CODED_SCORE**
  - Default: 0.0
  - Developer comment: for positive values of following defines, ai weights will take over of hardcoded ai scoring system

- **MIN_AI_SCORE_TO_ECONOMY_LAW_OVERRIDE_HARD_CODED_SCORE**
  - Default: 0.0

- **MIN_AI_SCORE_TO_TRADE_LAW_OVERRIDE_HARD_CODED_SCORE**
  - Default: 1000.0

- **MIN_AI_SCORE_TO_ALL_LAWS_OVERRIDE_HARD_CODED_SCORE**
  - Default: 0.0

- **AT_WAR_THREAT_FACTOR**
  - Default: 2.0
  - Developer comment: How much increase in threat does AI feel for being in war against someone

- **NEIGHBOUR_WAR_THREAT_FACTOR**
  - Default: 1.10
  - Developer comment: How much increase in threat does AI feel against neighbours who are at war

- **POTENTIAL_ALLY_JOIN_WAR_FACTOR**
  - Default: 100
  - Developer comment: How much increase in threat does AI feel against neighbours who are allied against one of our enemies

- **POTENTIAL_FUTURE_ENEMY_FACTOR**
  - Default: 100
  - Developer comment: How much increase in threat does AI feel against neighbours who at war with our allies

- **NEUTRAL_THREAT_PARANOIA**
  - Default: 10
  - Developer comment: How scared neutrals are of everyone

- **DIFFERENT_FACTION_THREAT**
  - Default: 30
  - Developer comment: Threat caused by not being in the same faction

- **MAX_THREAT_FOR_FIRST_YEAR_CIVILIAN_MODE**
  - Default: 60
  - Developer comment: above this threshold, ai will leave first year civilian factory mode which bumps it civilian factory scores while building

- **PLAN_ATTACK_MIN_ORG_FACTOR_LOW**
  - Default: 0.85
  - Developer comment: Minimum org % for a unit to actively attack an enemy unit when executing a plan

- **PLAN_ATTACK_MIN_STRENGTH_FACTOR_LOW**
  - Default: 0.60
  - Developer comment: Minimum strength for a unit to actively attack an enemy unit when executing a plan

- **PLAN_ATTACK_MIN_ORG_FACTOR_MED**
  - Default: 0.7
  - Developer comment: (LOW,MED,HIGH) corresponds to the plan execution agressiveness level.

- **PLAN_ATTACK_MIN_STRENGTH_FACTOR_MED**
  - Default: 0.50

- **PLAN_ATTACK_MIN_ORG_FACTOR_HIGH**
  - Default: 0.45

- **PLAN_ATTACK_MIN_STRENGTH_FACTOR_HIGH**
  - Default: 0.30

- **PLAN_FRONTUNIT_DISTANCE_FACTOR**
  - Default: 10.0
  - Developer comment: Factor for candidate units distance to front positions.

- **PLAN_ATTACK_DEPTH_FACTOR**
  - Default: 0.5
  - Developer comment: Factor applied to size or enemy being attacked.

- **PLAN_STEP_COST_LIMIT**
  - Default: 9
  - Developer comment: When stepping to draw a plan this cost makes it break if it hits hard terrain (multiplied by number of desired steps)

- **PLAN_STEP_COST_LIMIT_REDUCTION**
  - Default: 3
  - Developer comment: Cost limit is reduced per iteration, making hard terrain less likely to be crossed the further into enemy territory it is

- **PLAN_FRONT_SECTION_MAX_LENGTH**
  - Default: 18
  - Developer comment: When a front is longer than this it will be split in two sections for the AI

- **PLAN_FRONT_SECTION_MIN_LENGTH**
  - Default: 10
  - Developer comment: When two front sections together are this short they will be merged for the AI

- **PLAN_MIN_SIZE_FOR_FALLBACK**
  - Default: 50
  - Developer comment: A country with less provinces than this will not draw fallback plans, but rather station their troops along the front

- **SEND_VOLUNTEER_EVAL_BASE_DISTANCE**
  - Default: 175.0
  - Developer comment: How far away it will evaluate sending volunteers if not a major power

- **SEND_VOLUNTEER_EVAL_MAJOER_POWER**
  - Default: 1.0
  - Developer comment: How willing major powers are to send volunteers.

- **SEND_VOLUNTEER_EVAL_CONTAINMENT_FACTOR**
  - Default: 0.1
  - Developer comment: How much AI containment factors into its evaluation of sending volunteers.

- **GIVE_STATE_CONTROL_MIN_CONTROLLED**
  - Default: 1
  - Developer comment: AI needs to control more than this number of states before considering giving any away

- **GIVE_STATE_CONTROL_MIN_CONTROL_DIFF**
  - Default: 2
  - Developer comment: The difference in number of controlled states compared to war participation needs to be bigger than this for the AI to consider giving a state to a country

- **RELATIVE_STRENGTH_TO_INVADE**
  - Default: 0.08
  - Developer comment: Compares the estimated strength of the country/faction compared to it's enemies to see if it should invade or stay at home to defend.

- **RELATIVE_STRENGTH_TO_INVADE_DEFENSIVE**
  - Default: 0.4
  - Developer comment: Compares the estimated strength of the country/faction compared to it's enemies to see if it should invade or stay at home to defend, but while being a defensive country.

- **GIVE_STATE_CONTROL_BASE_SCORE**
  - Default: 50
  - Developer comment: Base diplo score for giving away control of states

- **GIVE_STATE_CONTROL_DIFF_FACTOR**
  - Default: 2.0
  - Developer comment: Diplo score multiplier for state control compared to war participation difference

- **GIVE_STATE_CONTROL_NEIGHBOR_SCORE**
  - Default: 20
  - Developer comment: Diplo score for each neighboring state controlled by the target

- **GIVE_STATE_CONTROL_NEIGHBOR_ACTOR_SCORE**
  - Default: -5
  - Developer comment: Diplo score for each neighboring state that is controlled by the sender

- **GIVE_STATE_CONTROL_NEIGHBOR_OTHER_SCORE**
  - Default: 5
  - Developer comment: Diplo score for each neighboring state controlled by someone else

- **GIVE_STATE_CONTROL_MAX_SCORE_DIST**
  - Default: 600
  - Developer comment: A State that is closer to the recipient capital than this gets a score bonus based on the below value

- **GIVE_STATE_CONTROL_DIST_SCORE_MULT**
  - Default: 0.2
  - Developer comment: Multiplier for the score gained from distance ( GIVE_STATE_CONTROL_MAX_SCORE_DIST - distance ) * this

- **IRRATIONALITY_LAMBDA**
  - Default: 200
  - Developer comment: Lambda given to Poisson Random function determining if a leader should act a bit irrational

- **GENERATE_WARGOAL_THREAT_BASELINE**
  - Default: 1.0
  - Developer comment:
    ```text
    Value of 200 should give 0.3% chance of Stalin going for instance crazy and conquering all of America
    The baseline for what the AI considers the world is getting dangerous and we want to generate wargoals with no antagonize value
    ```

- **GENERATE_WARGOAL_ANTAGONIZE_SCALE**
  - Default: 0.35
  - Developer comment: works to scale the AIs antagonize value vs the threat baseline for when it should act on existing claims: threat used for baseline is min_threat - antagonize * scale

- **RESERVE_TO_COMMITTED_BALANCE**
  - Default: 0.3
  - Developer comment: How many reserves compared to number of committed divisions in a combat (1.0 = as many as reserves as committed)

- **DIPLOMACY_COMMUNIST_NOT_NEIGHBOUR**
  - Default: -10
  - Developer comment: Communists want to stay consolidated with their influence

- **MAIN_ENEMY_FRONT_IMPORTANCE**
  - Default: 4.0
  - Developer comment: How much extra focus the AI should put on who it considers to be its current main enemy.

- **EASY_TARGET_FRONT_IMPORTANCE**
  - Default: 7.5
  - Developer comment: How much extra focus the AI should put on who it considers to be the easiest target.

- **AI_FRONT_MOVEMENT_FACTOR_FOR_READY**
  - Default: 0.25
  - Developer comment: If less than this fraction of units on a front is moving, AI sees it as ready for action

- **MICRO_POCKET_SIZE**
  - Default: 4
  - Developer comment: Pockets with a size equal to or lower than this will be mocroed by the AI, for efficiency.

- **DECLARE_WAR_MIN_FRONT_SIZE_TO_CONSIDER_FOR_NOT_READY**
  - Default: 0.04
  - Developer comment: fronts with less armies than this ratio compared to total number of armies are ignored when ai checks if it is ready for war

- **POCKET_DISTANCE_MAX**
  - Default: 40000
  - Developer comment: shortest square distance we bother about chasing pockets

- **VP_MAX_PROVINCE_WORTH**
  - Default: 500
  - Developer comment: Max worth a province can have to a defensive order

- **VP_LEVEL_IMPORTANCE_MEDIUM**
  - Default: 10
  - Developer comment: Victory points with values higher than or equal to this are considered to be of medium importance.

- **AREA_DEFENSE_CAPITAL_PEACE_VP_WEIGHT**
  - Default: { 1.0, 1.0, 1.0 }
  - Developer comment: these are all 3 numbers for min, desired, max unit need weights for area defense

- **AREA_DEFENSE_CAPITAL_VP_WEIGHT**
  - Default: { 0.0, 1.0, 2.0 }

- **AREA_DEFENSE_HOME_VP_WEIGHT**
  - Default: { 0.0, 0.5, 1.0 }

- **AREA_DEFENSE_OTHER_VP_WEIGHT**
  - Default: { 0.0, 0.0, 1.0 }

- **AREA_DEFENSE_CAPITAL_PEACE_COAST_WEIGHT**
  - Default: { 0.0, 0.0, 0.0 }

- **AREA_DEFENSE_CAPITAL_COAST_WEIGHT**
  - Default: { 0.0, 0.2, 0.7 }

- **AREA_DEFENSE_HOME_COAST_WEIGHT**
  - Default: { 0.0, 0.1, 0.5 }

- **AREA_DEFENSE_OTHER_COAST_WEIGHT**
  - Default: { 0.0, 0.0, 0.0 }

- **AREA_DEFENSE_CAPITAL_PEACE_BASE_WEIGHT**
  - Default: { 0.0, 0.0, 0.0 }

- **AREA_DEFENSE_CAPITAL_BASE_WEIGHT**
  - Default: { 0.5, 1.0, 1.5 }

- **AREA_DEFENSE_HOME_BASE_WEIGHT**
  - Default: { 0.5, 1.0, 1.0 }

- **AREA_DEFENSE_OTHER_BASE_WEIGHT**
  - Default: { 0.5, 0.5, 1.0 }

- **ESTIMATED_CONVOYS_PER_DIVISION**
  - Default: 6
  - Developer comment: Not always correct, but mainly used to make sure AI does not go crazy

- **ENTRENCHMENT_WEIGHT**
  - Default: 2.0
  - Developer comment: AI should favour units with less entrenchment when assigning units around.

- **FRONT_TERRAIN_DEFENSE_FACTOR**
  - Default: 3.75
  - Developer comment: Multiplier applied to unit defense modifier for terrain on front province multiplied by terrain importance

- **FRONT_TERRAIN_ATTACK_FACTOR**
  - Default: 5.0
  - Developer comment: Multiplier applied to unit attack modifier for terrain on enemy front province multiplied by terrain importance

- **BASE_DISTANCE_TO_CARE**
  - Default: 600.0
  - Developer comment: Countries that are too far away are less interesting in diplomacy

- **MIN_FORCE_RATIO_TO_PROTECT**
  - Default: 0.5
  - Developer comment: Tiny countries should not feel protective or really large ones

- **ORG_UNIT_STRONG**
  - Default: 0.75
  - Developer comment: Organization % for unit to be considered strong

- **STR_UNIT_STRONG**
  - Default: 0.70
  - Developer comment: Strength (equipment) % for unit to be considered strong

- **ORG_UNIT_WEAK**
  - Default: 0.25
  - Developer comment: Organization % for unit to be considered weak

- **STR_UNIT_WEAK**
  - Default: 0.30
  - Developer comment: Strength (equipment) % for unit to be considered weak

- **ORG_UNIT_NORMAL**
  - Default: 0.35
  - Developer comment: Organization % for unit to be considered normal

- **STR_UNIT_NORMAL**
  - Default: 0.4
  - Developer comment: Strength (equipment) % for unit to be considered normal

- **PLAN_FACTION_STRONG_TO_EXECUTE**
  - Default: 0.50
  - Developer comment: % or more of units in an order to consider executing the plan

- **PLAN_FACTION_NORMAL_TO_EXECUTE**
  - Default: 0.65
  - Developer comment: % or more of units in an order to consider executing the plan

- **PLAN_FACTION_WEAK_TO_ABORT**
  - Default: 0.65
  - Developer comment: % or more of units in an order to consider executing the plan

- **PLAN_AVG_PREPARATION_TO_EXECUTE**
  - Default: 0.5
  - Developer comment: % or more average plan preparation before executing

- **REDEPLOY_DISTANCE_VS_ORDER_SIZE**
  - Default: 1.0
  - Developer comment: Factor applied to the path length of a unit compared to length of an order to determine if it should use strategic redeployment

- **FORT_LEVEL_TO_CONSIDER_HIGHLY_FORTIFIED**
  - Default: 1
  - Developer comment: Provinces above this level of fortification will be considered highly fortified by plan evaluation

- **PLAN_VALUE_FORTIFICATION_LEVEL_MAX_PENALTY**
  - Default: -0.5
  - Developer comment: Max plan value penalty from fortification. This is scaled by number of provinces along a frontline, over the number which exceed the fort value value above

- **MAX_ALLOWED_NAVAL_DANGER**
  - Default: 80
  - Developer comment: AI will ignore naval paths that has danger value of above this threshold while assigning units

- **TRANSFER_DANGER_HOSTILE_SHIPS**
  - Default: 50
  - Developer comment: max danger from complete enemy naval supriority over ai in an area

- **EXPORT_RESOURCE_TRADE_NEED_IMPORTANCE**
  - Default: 0.5
  - Developer comment: how important is each lost resource to overexport for trade law selection

- **OPERATION_EQUIPMENT_NEED_PRODUCTION_MULT**
  - Default: 1.0
  - Developer comment: equipment requests for operations will be added the equipment needs that ai considers while assigning factories to production

- **MIN_FUEL_RATIO_TO_NOT_IGNORE_STRIKE_FORCE_COST**
  - Default: 0.0
  - Developer comment: ai will still assign strike forces unless fuel ratio drops below this one

- **MIN_FUEL_RATIO_TO_NOT_IGNORE_INVASION_SUPPORT_COST**
  - Default: 0.0
  - Developer comment: ai will still naval invasion support forces unless fuel ratio drops below this one

- **ENEMY_HOME_AREA_RATIO_TO_DISABLE_INVASIONS**
  - Default: 0.3
  - Developer comment: if we are fighting against an enemy home area from our home area and if the enemy area is larger than this ratio, non strategy invasions are disabled

- **HOURS_BETWEEN_ENCIRCLEMENT_DISCOVERY**
  - Default: 72
  - Developer comment: Per army, interval in hours between refresh of which provinces it considers make up potential encirclement points

- **FASCISTS_BEFRIEND_FASCISTS**
  - Default: 10

- **FASCISTS_BEFRIEND_DEMOCRACIES**
  - Default: -25

- **FASCISTS_BEFRIEND_COMMUNISTS**
  - Default: -25

- **FASCISTS_ALLY_FASCISTS**
  - Default: 0

- **FASCISTS_ALLY_DEMOCRACIES**
  - Default: -100

- **FASCISTS_ALLY_COMMUNISTS**
  - Default: -100

- **FASCISTS_ANTAGONIZE_FASCISTS**
  - Default: -10

- **FASCISTS_ANTAGONIZE_DEMOCRACIES**
  - Default: 100

- **FASCISTS_ANTAGONIZE_COMMUNISTS**
  - Default: 100

- **DEMOCRACIES_BEFRIEND_FASCISTS**
  - Default: -25

- **DEMOCRACIES_BEFRIEND_DEMOCRACIES**
  - Default: 0

- **DEMOCRACIES_BEFRIEND_COMMUNISTS**
  - Default: -25

- **DEMOCRACIES_ALLY_FASCISTS**
  - Default: -50

- **DEMOCRACIES_ALLY_DEMOCRACIES**
  - Default: 0

- **DEMOCRACIES_ALLY_COMMUNISTS**
  - Default: -50

- **DEMOCRACIES_ANTAGONIZE_FASCISTS**
  - Default: 0

- **DEMOCRACIES_ANTAGONIZE_DEMOCRACIES**
  - Default: -25

- **DEMOCRACIES_ANTAGONIZE_COMMUNISTS**
  - Default: 0

- **COMMUNISTS_BEFRIEND_FASCISTS**
  - Default: -25

- **COMMUNISTS_BEFRIEND_DEMOCRACIES**
  - Default: -25

- **COMMUNISTS_BEFRIEND_COMMUNISTS**
  - Default: 25

- **COMMUNISTS_ALLY_FASCISTS**
  - Default: -100

- **COMMUNISTS_ALLY_DEMOCRACIES**
  - Default: -50

- **COMMUNISTS_ALLY_COMMUNISTS**
  - Default: 0

- **COMMUNISTS_ANTAGONIZE_FASCISTS**
  - Default: 100

- **COMMUNISTS_ANTAGONIZE_DEMOCRACIES**
  - Default: 10

- **COMMUNISTS_ANTAGONIZE_COMMUNISTS**
  - Default: -10

- **TENSION_MIN_FOR_GUARANTEE_VS_MINOR**
  - Default: 10
  - Developer comment: for non faction people AI will not consider you worth guaranteeing below this

- **NUM_AI_MESSAGES**
  - Default: 10
  - Developer comment: Set to whatever category has the highest number of messages

- **DIPLOMACY_FACTION_WAR_WANTS_HELP**
  - Default: 50
  - Developer comment: Desire to send to nations to join a faction if you are at war

- **DIPLOMACY_FACTION_CIVILWAR_WANTS_HELP**
  - Default: -50

- **FACTION_UNSTABLE_ACCEPTANCE**
  - Default: -100

- **DIPLOMACY_AT_WAR_WITH_ALLY_RELUCTANCE**
  - Default: -1000

- **DIPLOMACY_FACTION_JOIN_COUP_INITIATOR_BONUS**
  - Default: 70
  - Developer comment: If a country initiated coup on an another country, civil war revolter is more likely to join initiator's faction

- **SHIPS_PRODUCTION_BASE_COST**
  - Default: 10000
  - Developer comment: Used by the AI to normalize IC values when picking what ship to build.

- **NEEDED_NAVAL_FACTORIES_EXPENSIVE_SHIP_BONUS**
  - Default: 12
  - Developer comment: Amount of naval yards you need to get a bonus to building really expensive ships

- **FORTIFIED_RATIO_TO_CONSIDER_A_FRONT_FORTIFIED**
  - Default: 0.5
  - Developer comment: ai will consider a front fortified if this ratio of provinces has fort

- **HEAVILY_FORTIFIED_RATIO_TO_CONSIDER_A_FRONT_FORTIFIED**
  - Default: 0.5
  - Developer comment: ai will consider a front super fortified if this ratio of provinces has lots of forts

- **FORTIFIED_MIN_ORG_FACTOR_TO_CONSIDER_A_FRONT_FORTIFIED**
  - Default: 0.2
  - Developer comment: ai will treat fortified provinces as unfortified if no unit in that province has an organization factor at least this high

- **DESPERATE_AI_MIN_UNIT_ASSIGN_TO_ESCAPE**
  - Default: 0
  - Developer comment: AI will assign at least this amount of units to break from desperate situations

- **DESPERATE_AI_WEAK_UNIT_STR_LIMIT**
  - Default: 0.35
  - Developer comment: ai will increase number of units assigned to break from desperate situations when units are start falling lower than this str limit

- **DESPERATE_AI_MIN_ORG_BEFORE_ATTACK**
  - Default: 0.3
  - Developer comment: ai will wait for this much org to attack an enemy prov in desperate situations

- **DESPERATE_AI_MIN_ORG_BEFORE_MOVE**
  - Default: 0.06
  - Developer comment: ai will wait for this much org to move in desperate situations

- **DESPERATE_ATTACK_WITHOUT_ORG_WHEN_NO_ORG_GAIN**
  - Default: 120
  - Developer comment: if ai can't regain enough org to attack in this many hours, it will go truly desperate and attack anyway (still has to wait for move org)

- **MAX_REQUEST_EXPEDITIONARIES_ARMY_RATIO**
  - Default: 0.3
  - Developer comment: AI will not accept expeditionary requests if its expeditions are above this ratio

- **CASUALTY_RATIO_TO_PULL_EXPEDITIONARIES_BACK**
  - Default: 0.1
  - Developer comment: AI will pull expeditioniries back if its casualties is aboce this ratio compared to their total deployed manpower

- **CASUALTY_RATIO_TO_NOT_SEND_EXPEDITIONARIES**
  - Default: 0.05
  - Developer comment: AI will not send expeditioniries if its casualties is aboce this ratio compared to their total deployed manpower

- **SURRENDER_LEVEL_TO_PULL_EXPEDITIONARIES_BACK**
  - Default: 0.3
  - Developer comment: AI will pull expeditioniries back if its surrender level is above this ratio

- **SURRENDER_LEVEL_TO_NOT_SEND_EXPEDITIONARIES**
  - Default: 0.15
  - Developer comment: AI will not send expeditioniries if its surrender level is above this ratio

- **EXPEDITIONARY_CASUALTY_DECAY_RATIO**
  - Default: 0.3333
  - Developer comment: expeditionary manpower lost will decay by thousands daily by this ratio (compared to deployed manpower)

- **NUM_DAYS_TO_PULL_EXPEDITIONARIES_BACK**
  - Default: 14
  - Developer comment: AI will pull units back from non-ai players after waiting this days if things are not going well for its units

- **ACCESS_SCORE_FOR_DEMOCRATIC_COUNTRIES**
  - Default: 500
  - Developer comment: democracies gives each other access if they have a common enemy

- **AI_AIR_MISSION_COVERAGE_TO_STAY_PUT**
  - Default: 0.5
  - Developer comment: AI will not rebase air wings on missions if their new mission target exceeds this percentage of region coverage

- **ACCESS_SCORE_PENALTY_PER_EXISTING_ACCESS_AT_WAR**
  - Default: 250
  - Developer comment: each access reduces the desire of next access

- **ACCESS_SCORE_PENALTY_PER_EXISTING_ACCESS**
  - Default: 500
  - Developer comment: each access reduces the desire of next access

- **NAVAL_ACCESS_SCORE_PENALTY_PER_EXISTING_ACCESS_AT_WAR**
  - Default: 150

- **NAVAL_ACCESS_SCORE_PENALTY_PER_EXISTING_ACCESS**
  - Default: 250

- **NAVAL_SUPREMACY_WEIGHT_PER_DIVISION_ON_INVASION_ORDER**
  - Default: 6
  - Developer comment: adds to supremacy requests for regions with active or pending naval invasions

- **TOO_INSIGNIFICANT_ARMY_RATIO_BEGIN**
  - Default: 0.75
  - Developer comment: if army ratio is of a country is larger than this threshold, it will be less reluctant to accept certain diplo actions

- **TOO_INSIGNIFICANT_MAX_PENALTY**
  - Default: 350
  - Developer comment: max penalty that will be applied for thinking a country is too insignificant

- **WANTED_UNITS_INDUSTRY_FACTOR**
  - Default: 1.60
  - Developer comment:
    ```text
    Calculating wanted nr of divisions
    How many units a country wants is partially based on how much military industry that is available
    ```

- **WANTED_UNITS_THREAT_BASE**
  - Default: 0.7
  - Developer comment: If no threat, multiply min wanted units by this

- **WANTED_UNITS_THREAT_MAX**
  - Default: 6.0
  - Developer comment: Normalized threat is clamped to this

- **WANTED_UNITS_WAR_THREAT_FACTOR**
  - Default: 1.15
  - Developer comment: Factor threat with this if country is at war. this value is overriden by the value in ideology database if that value exceedes this.

- **WANTED_UNITS_DANGEROUS_NEIGHBOR_FACTOR**
  - Default: 1.15
  - Developer comment: Factor if has dangerous neighbor

- **WANTED_UNITS_MANPOWER_DIVISOR**
  - Default: 21000
  - Developer comment: Normalizing divisor for AI manpower. (for each x max available manpower, they want one division)

- **WANTED_UNITS_WEIGHT_FRONTS_WANT**
  - Default: 0.35
  - Developer comment: Weight of front needs when computing final nr wanted units

- **WANTED_UNITS_WEIGHT_FACTORIES**
  - Default: 0.45
  - Developer comment: Weight of military factories when computing final nr wanted units

- **WANTED_UNITS_WEIGHT_MANPOWER**
  - Default: 0.3
  - Developer comment: Weight of manpower availability when computing final nr wanted units

- **WANTED_UNITS_MIN_DEFENCE_FACTOR**
  - Default: 0.4
  - Developer comment: Factor on units required for min defence

- **WANTED_UNITS_MAX_WANTED_CAP**
  - Default: 500
  - Developer comment:
    ```text
    End of calculating wanted nr of divisions
    Maximum wanted divisions for a country. This can be exceeded by certain hardcoded multipliers, but not by base calculation logic.
    ```

- **WANTED_LAND_PLANES_PER_BASE_CAPACITY_FACTOR**
  - Default: 1
  - Developer comment: Scales how many land-based planes the AI want per air base space (excluding carriers).

- **WANTED_LAND_PLANES_PER_DIVISION**
  - Default: 20
  - Developer comment: How many land-based planes the AI want for each division it wants.

- **WANTED_LAND_PLANES_TOTAL_MAX_PER_DIVISION**
  - Default: 100
  - Developer comment: The max total number of land-based planes the AI want.

- **WANTED_CARRIER_PLANES_PER_CARRIER_CAPACITY_FACTOR**
  - Default: 1.5
  - Developer comment: Scales how many carrier planes the AI want per carrier deck space.

- **WANTED_CARRIER_PLANES_PER_CARRIER_CAPACITY_IN_PRODUCTION_FACTOR**
  - Default: 1
  - Developer comment: Scales how many carrier planes the AI want per deck space of carriers in production.

- **CARRIER_CAPACITY_IN_PRODUCTION_MAX_DAYS_LEFT_TO_INCLUDE_FACTOR**
  - Default: 365
  - Developer comment: Carriers in production that will take more days to complete than this value will be ignored when calculating the above.

- **START_TRAINING_EQUIPMENT_LEVEL**
  - Default: 0.95
  - Developer comment: ai will not start to train if equipment drops below this level

- **STOP_TRAINING_EQUIPMENT_LEVEL**
  - Default: 0.90
  - Developer comment: ai will not train if equipment drops below this level

- **BUILD_REFINERY_LACK_OF_RESOURCE_MODIFIER**
  - Default: 0.003
  - Developer comment: How much lack of resources are worth when evaluating what to build.

- **DIVISION_DESIGN_WEIGHTS**
  - Default: { 0.5, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, -0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.0, 0.0, -0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5 }
  - Developer comment:
    ```text
    Base values used by AI to evaluate value of a stat
    Army Values
    default_morale
    defense
    breakthrough
    hardness
    soft_attack
    hard_attack
    recon
    entrenchment
    initiative
    casualty_trickleback
    supply_consumption_factor
    supply_consumption
    suppression
    suppression_factor
    experience_loss_factor
    equipment_capture_factor
    fuel_capacity
    Navy Values
    surface_detection
    sub_detection
    surface_visibility
    sub_visibility
    lg attack
    lg piercing
    hg attack
    hg piercing
    torpedo
    sub attack
    anti air attack
    amphibious_defense
    naval_speed
    range
    mine plant
    mine sweep
    navy light gun hit chance
    navy heavy gun hit chance
    navy torpedo hit chance
    navy incoming torpedo damage reduction
    navy incoming torpedo crit chance
    weather penalty
    raiding coordination
    patrol coordination
    search and destroy coordination
    Air Values
    air_range
    air_defence
    air_attack
    air_agility
    air_bombing
    air_superiority
    naval_strike_attack
    naval_strike_targetting
    air_ground_attack
    air_visibility_factor
    Railway gun Values
    railway_gun_attack
    railway_gun_attack_range
    Common Values
    max_organisation
    max_strength
    maximum_speed
    armor_value
    ap_attack
    reliability
    reliability_factor
    weight
    thrust
    fuel_consumption
    fuel_consumption_factor
    Special Values
    strategic_attack
    carrier_size
    acclimatization hot gain
    acclimatization cold gain
    night_penalty
    build_cost_ic
    ```

- **DIVISION_DESIGN_MANPOWER_WEIGHT**
  - Default: 0.005

- **DIVISION_DESIGN_STOCKPILE_WEIGHT**
  - Default: 0.01

- **DIVISION_DESIGN_COMBAT_WIDTH_WEIGHT**
  - Default: -1.0
  - Developer comment: This score is reduced the higher width is when comparing pure changes with no target

- **DIVISION_DESIGN_COMBAT_WIDTH_TARGET_WEIGHT**
  - Default: -200.0
  - Developer comment: This score is reduced the farther the width is from the target width (if set)

- **DIVISION_DESIGN_MAX_FAILED_DAYS**
  - Default: 60
  - Developer comment: max days we keep track of since failure of a template design update

- **DIVISION_MATCH_ROLE_BOOST_FACTOR**
  - Default: 1.2
  - Developer comment: When finding closest matching existing template to a target template, boost the score by this much if the template also has the correct role

- **EQUIPMENT_DESIGN_MAX_FAILED_DAYS**
  - Default: 60
  - Developer comment: max days we keep track of since failure of an equipment design update

- **UPGRADE_DIVISION_RELUCTANCE**
  - Default: 7
  - Developer comment: How often to consider upgrading to new templates for units in the field

- **UPGRADE_PERCENTAGE_OF_FORCES**
  - Default: 0.03
  - Developer comment: How big part of the army that should be considered for upgrading

- **REFIT_SHIP_RELUCTANCE**
  - Default: 28
  - Developer comment: How often to consider refitting to new equipment variants for ships in the field

- **REFIT_SHIP_PERCENTAGE_OF_FORCES**
  - Default: 0.1
  - Developer comment: How big part of the navy that should be considered for refitting

- **NAVY_PREFERED_MAX_SIZE**
  - Default: 25
  - Developer comment: AI will generally attempt to merge fleets into this size, but as a soft limit.

- **INVASION_COASTAL_PROVS_PER_ORDER**
  - Default: 24
  - Developer comment: AI will consider one extra invasion per number of provinces stated here (num orders = total coast / this)

- **MIN_INVASION_AREA_SIZE_FOR_FLOATING_HARBORS**
  - Default: 15
  - Developer comment: AI will consider using floating harbors for naval invasion if invasion area is larger than this many provinces

- **CONVOY_NEED_SAFETY_BUFFER**
  - Default: 1.30
  - Developer comment: AI will try and keep 15% more convoys than what it needs.

- **REGION_THREAT_PER_SUNK_CONVOY**
  - Default: 25
  - Developer comment: Threat value per convoy sunk in a region. Decays over time.

- **REGION_THREAT_LEVEL_TO_AVOID_REGION**
  - Default: 25*10
  - Developer comment: How much threat must be generated in region ( by REGION_THREAT_PER_SUNK_CONVOY ) so the AI will decide to mark the region as avoid

- **REGION_THREAT_LEVEL_TO_BLOCK_REGION**
  - Default: 25*100
  - Developer comment: How much threat must be generated in region ( by REGION_THREAT_PER_SUNK_CONVOY ) so the AI will decide to mark the region as avoid

- **REGION_CONVOY_DANGER_DAILY_DECAY**
  - Default: 1
  - Developer comment: When convoys are sunk it generates threat in the region which the AI uses to prio nalval missions

- **PRODUCTION_LINE_SWITCH_SURPLUS_NEEDED_MODIFIER**
  - Default: 0.2
  - Developer comment: Is modified by efficency modifiers.

- **PLAN_ACTIVATION_MAJOR_WEIGHT_FACTOR**
  - Default: 1.5
  - Developer comment: AI countries will hold on activating plans if stronger countries have plans in the same location. Majors count extra (value of 1 will negate this)

- **PLAN_ACTIVATION_PLAYER_WEIGHT_FACTOR**
  - Default: 50.0
  - Developer comment: AI countries will hold on activating plans if player controlled countries have plans in the same location.

- **AREA_DEFENSE_BASE_IMPORTANCE**
  - Default: 30
  - Developer comment: Area defense order base importance value (used for determining order of troop selections)

- **AREA_DEFENSE_CIVIL_WAR_IMPORTANCE**
  - Default: 30
  - Developer comment: Area defense order importance value when a country is in a civil war as target or revolter.

- **AREA_DEFENSE_IMPORTANCE_FACTOR**
  - Default: 1.0
  - Developer comment: used to balance defensive area importance vs other fronts

- **COMBINED_ARMS_LEVEL**
  - Default: 1
  - Developer comment: 0 = Never, 1 = Infantry/Artillery, 2 = Go wild

- **MAX_DISTANCE_NAVAL_INVASION**
  - Default: 200.0
  - Developer comment: AI is extremely unwilling to plan naval invasions above this naval distance limit.

- **ENEMY_NAVY_STRENGTH_DONT_BOTHER**
  - Default: 2.5
  - Developer comment: If the enemy has a navy at least these many times stronger that the own, don't bother invading

- **MIN_SUPPLY_USE_SANITY_CAP**
  - Default: 100
  - Developer comment: Ignore supply cap if below this value when deciding on how many divisions to produce.

- **MAX_SUPPLY_DIVISOR**
  - Default: 1.75
  - Developer comment: To make sure the AI does not overdeploy divisions. Higher number means more supply per unit.

- **MISSING_CONVOYS_BOOST_FACTOR**
  - Default: 50.0
  - Developer comment: The more convoys a country is missing, the more resources it diverts to cover this.

- **TRANSPORTS_PER_PARATROOPER**
  - Default: 20
  - Developer comment: Currently unused.

- **MAX_MICRO_ATTACKS_PER_ORDER**
  - Default: 3
  - Developer comment: AI goes through its orders and checks if there are situations to take advantage of

- **FALLBACK_LOSING_FACTOR**
  - Default: 1.0
  - Developer comment: The lower this number, the longer the AI will hold the line before sending them to the fallback line

- **PRODUCTION_MAX_PROGRESS_TO_SWITCH_NAVAL**
  - Default: 0.1
  - Developer comment: AI will not replace ships being built by newer types if progress is above this

- **PRODUCTION_WAIT_TO_FINISH_IF_EXPENSIVE**
  - Default: 0.25
  - Developer comment: If produced item is expensive (producing less than one/week), wait to finish item if progress is above this

- **PRODUCTION_WAIT_TO_FINISH_IF_CHEAP**
  - Default: 0.75
  - Developer comment: If produced item is cheap (producing more than one/week), wait to finish item if progress is above this

- **STATE_CONTROL_FOR_AREA_DEFENSE**
  - Default: 0.4
  - Developer comment: To avoid AI sending area defense to area with very little foothold

- **FORCE_FACTOR_AGAINST_EXTRA_MINOR**
  - Default: 0.15
  - Developer comment: AI considers generating wargoals against minors below this % of force compared to themselves to get at a bigger enemy.

- **MAX_EXTRA_WARGOAL_GENERATION**
  - Default: 2
  - Developer comment: AI may want to generate wargoals against weak minors to get at larger enemy, but never more that this at any given time.

- **NAVAL_MISSION_DISTANCE_BASE**
  - Default: 3500
  - Developer comment: Base value when AI is evaluating distance score to places

- **NAVAL_MISSION_INVASION_BASE**
  - Default: 1000
  - Developer comment: Base score for region with naval invasion (modified dynamically by prioritizing orders)

- **NAVAL_MISSION_AGGRESSIVE_PATROL_DIVISOR**
  - Default: 1
  - Developer comment: Divides patrol score when not defending

- **NAVAL_MISSION_AGGRESSIVE_ESCORT_DIVISOR**
  - Default: 2
  - Developer comment: Divides escort score when not defending

- **NAVAL_MISSION_PATROL_NEAR_OWNED**
  - Default: 500
  - Developer comment: Extra patrol mission score near owned provinces

- **NAVAL_MISSION_ESCORT_NEAR_OWNED**
  - Default: 300
  - Developer comment: Extra escort mission score near owned provinces

- **NAVAL_MISSION_PATROL_NEAR_CONTROLLED**
  - Default: 120
  - Developer comment: Extra patrol mission score near controlled provinces

- **NAVAL_MISSION_ESCORT_NEAR_CONTROLLED**
  - Default: 200
  - Developer comment: Extra escort mission score near controlled provinces

- **NAVAL_MISSION_MINES_PLANTING_NEAR_OWNED**
  - Default: 40000

- **NAVAL_MISSION_MINES_PLANTING_NEAR_CONTROLLED**
  - Default: 30000

- **NAVAL_MISSION_MINES_SWEEPING_NEAR_OWNED**
  - Default: 60000
  - Developer comment: How likely the AI will do the sweeping missions. The value is scaled by the amount of mines to sweep.

- **NAVAL_MISSION_MINES_SWEEPING_NEAR_CONTROLLED**
  - Default: 50000
  - Developer comment: Same as above, but nearby the controlled territory.

- **NEW_LEADER_EXTRA_CP_FACTOR**
  - Default: 2.0
  - Developer comment: Country must have at least this many times extra command power to get new admirals or army leaders

- **SCARY_LEVEL_AVERAGE_DEFENSE**
  - Default: -0.7
  - Developer comment: average front defense modifier to make it consider it as a PITA to go for

- **ATTACK_HEAVILY_DEFENDED_LIMIT**
  - Default: 0.5
  - Developer comment: AI will not launch attacks against heavily defended fronts unless they consider to have this level of advantage (1.0 = 100%)

- **HOUR_BAD_COMBAT_REEVALUATE**
  - Default: 48
  - Developer comment: if we are in combat for this amount and it goes shitty then try skipping it

- **MIN_PLAN_VALUE_TO_MICRO_INACTIVE**
  - Default: 0.25
  - Developer comment: The AI will not consider members of groups which plan is not activated AND evaluates lower than this.

- **MAX_UNITS_FACTOR_AREA_ORDER**
  - Default: 0.75
  - Developer comment: Factor for max number of units to assign to area defense orders

- **DESIRED_UNITS_FACTOR_AREA_ORDER**
  - Default: 0.7
  - Developer comment: Factor for desired number of units to assign to area defense orders

- **MIN_UNITS_FACTOR_AREA_ORDER**
  - Default: 1.0
  - Developer comment: Factor for min number of units to assign to area defense orders

- **MAX_UNITS_FACTOR_FRONT_ORDER**
  - Default: 1.0
  - Developer comment: Factor for max number of units to assign to area front orders

- **DESIRED_UNITS_FACTOR_FRONT_ORDER**
  - Default: 1.1
  - Developer comment: Factor for desired number of units to assign to area front orders

- **MIN_UNITS_FACTOR_FRONT_ORDER**
  - Default: 1.0
  - Developer comment: Factor for min number of units to assign to area front orders

- **MAX_UNITS_FACTOR_INVASION_ORDER**
  - Default: 1.0
  - Developer comment: Factor for max number of units to assign to naval invasion orders

- **DESIRED_UNITS_FACTOR_INVASION_ORDER**
  - Default: 1.0
  - Developer comment: Factor for desired number of units to assign to naval invasion orders

- **MIN_UNITS_FACTOR_INVASION_ORDER**
  - Default: 1.0
  - Developer comment: Factor for min number of units to assign to naval invasion orders

- **FRONT_UNITS_CAP_FACTOR**
  - Default: 15.0
  - Developer comment: A factor applied to total front size and supply use. Primarily effects small fronts

- **MAX_DIST_PORT_RUSH**
  - Default: 20.0
  - Developer comment: If a unit is in enemy territory with no supply it will consider nearby ports within this distance.

- **MIN_FIELD_STRENGTH_TO_BUILD_UNITS**
  - Default: 0.7
  - Developer comment: Cancel unit production if below this to get resources out to units in the field

- **MIN_MANPOWER_TO_BUILD_UNITS**
  - Default: 0.7
  - Developer comment: Cancel unit production if below this to get resources out to units in the field

- **AVERAGE_SUPPLY_USE_PESSIMISM**
  - Default: 1.5
  - Developer comment: Multiplier for when AI calculates average supply use of entire army.

- **PROPOSE_LEND_LEASE_AIDESIRE_SAME_IDEOLOGY**
  - Default: 40
  - Developer comment: Added to AI desire to propose lend lease if recipent is same ideology (and AI can't declare war on recipient)

- **PROPOSE_LEND_LEASE_AIDESIRE_SAME_IDEOLOGY_CIVIL_WAR**
  - Default: 25
  - Developer comment: Added to AI desire to propose lend lease if recipent is same ideology and they are currently in civil war

- **SEND_VOLUNTEER_AIDESIRE_SAME_IDEOLOGY**
  - Default: 40
  - Developer comment: Added to AI desire to send volunteers if recipent is same ideology (and AI can't declare war on recipient)

- **SEND_VOLUNTEER_AIDESIRE_SAME_IDEOLOGY_CIVIL_WAR**
  - Default: 25
  - Developer comment: Added to AI desire to send volunteers if recipent is same ideology and they are currently in civil war

- **REQUEST_LEND_LEASE_PROTECT_VALUE**
  - Default: 75
  - Developer comment: Limit for protect enemy desire for reducing lend lease desire

- **REQUEST_LEND_LEASE_CONTAINS_VALUE**
  - Default: 100
  - Developer comment: Limit of contain enemy desire for boosting friendly help

- **FRONT_BULGE_RATIO_UPPER_CUTOFF**
  - Default: 1.5
  - Developer comment: If total bulginess is lower than this, the front is ignored.

- **FRONT_BULGE_RATIO_LOWER_CUTOFF**
  - Default: 0.95
  - Developer comment: If local bulginess drops below this, a point of interest is found

- **FRONT_CUTOFF_MIN_EDGE_PROXIMITY**
  - Default: 2
  - Developer comment: Minimum number of provinces to the front edge to determine for cutoff oportunity.

- **INVASION_DISTANCE_RANDOMNESS**
  - Default: 300
  - Developer comment: This higher the value, the more unpredictable the invasions. Compares to actual map distance in pixels.

- **AIR_SCORE_DISTANCE_IMPACT**
  - Default: 0.3
  - Developer comment: Effect of distance applied to the score calculations

- **DAYS_BETWEEN_AIR_PRIORITIES_UPDATE**
  - Default: 4
  - Developer comment: Amount of days between air ai updates priorities for air wings ( from 1 to N )

- **NAVAL_AIR_SUPERIORITY_IMPORTANCE**
  - Default: 0.10
  - Developer comment: Strategic importance of air superiority ( amount of enemy planes in area )

- **NAVAL_SHIP_AIR_IMPORTANCE**
  - Default: 2.0
  - Developer comment: Naval ship air importance

- **NAVAL_SHIP_IN_PORT_AIR_IMPORTANCE**
  - Default: 6.0
  - Developer comment: Naval ship in the port air importance

- **NAVAL_COMBAT_AIR_IMPORTANCE**
  - Default: 8.0
  - Developer comment: Naval combat air importance

- **NAVAL_TRANSFER_AIR_IMPORTANCE**
  - Default: 0.0
  - Developer comment: Naval transfer air importance

- **NAVAL_COMBAT_TRANSFER_AIR_IMPORTANCE**
  - Default: 50.0
  - Developer comment: Naval combat involving enemy land units

- **NAVAL_IMPORTANCE_SCALE**
  - Default: 0.65
  - Developer comment: Naval total importance scale (every naval score get's multiplied by it)

- **NAVAL_COMBAT_OUR_NAVY_MULT_ON_IMPORTANCE**
  - Default: 0.35
  - Developer comment: Naval region importance are scaled by our ships as well

- **NAVAL_COMBAT_ALLY_NAVY_MULT_ON_IMPORTANCE**
  - Default: 0.15
  - Developer comment: Naval region importance are scaled by our ships as well

- **NAVAL_COMBAT_MIN_OUR_NAVY_MULT_ON_IMPORTANCE**
  - Default: 0.5
  - Developer comment: Min scale factor for naval region importance from our ships

- **NAVAL_COMBAT_MAX_OUR_NAVY_MULT_ON_IMPORTANCE**
  - Default: 1.0
  - Developer comment: Max scale factor for naval region importance from our ships

- **NAVAL_RANGE_FOR_DOCKING_RIGHTS_CHECK**
  - Default: 240.0
  - Developer comment: Naval range used to check if docking rights would allow us to reach a specific province

- **NAVAL_PATROL_PLANES_PER_SHIP_PATROLLING**
  - Default: 10.0
  - Developer comment: Amount of naval patrol planes per ship on a patrol mission

- **NAVAL_PATROL_PLANES_PER_SHIP_RAIDING**
  - Default: 10.0
  - Developer comment: Amount of naval patrol planes per ship on a convoy raid mission

- **NAVAL_PATROL_PLANES_PER_SHIP_ESCORTING**
  - Default: 10.0
  - Developer comment: Amount of naval patrol planes per ship on a convoy escort mission

- **NAVAL_FIGHTERS_PER_PLANE**
  - Default: 1.0
  - Developer comment: Amounts of air superiority planes requested per enemy plane

- **NAVAL_STRIKE_PLANES_PER_ARMY**
  - Default: 0
  - Developer comment: Amount of planes requested per enemy army

- **NAVAL_STRIKE_PLANES_PER_SHIP**
  - Default: 20
  - Developer comment: Amount of bombers requested per enemy ship

- **PORT_STRIKE_PLANES_PER_SHIP**
  - Default: 10
  - Developer comment: Amount of bombers request per enemy ship in the port

- **MINES_SWEEPING_PLANES_PER_MAX_MINES**
  - Default: 150
  - Developer comment: Amount of air planes request for mines sweeping when there is max amount of mines planted by enemy in certain region

- **MINES_PLANTING_PLANES_PER_MAX_DESIRE**
  - Default: 100
  - Developer comment: Amount of air planes request for mines planting when there is max desire for it.

- **MINES_PLANTING_DESIRE_PER_HOME_STATE**
  - Default: 0.4
  - Developer comment: Scoring for how much do we want to plant naval mines with our air wings if the naval region is adjacent to a home state. Multiple adjacent states increases the score. Max sum of score is 1.0.

- **MINES_PLANTING_DESIRE_PER_ENEMY_STATE**
  - Default: 0.1
  - Developer comment: Scoring for how much do we want to plant naval mines with our air wings if the naval region is adjacent to the enemy state. Multiple adjacent states increases the score. Max sum of score is 1.0.

- **MINES_PLANTING_DESIRE_PER_NAVAL_THREAT**
  - Default: 250
  - Developer comment: How much threat must be generated in the naval region, in order to get the maximum desire to plant naval mines in there.

- **NAVAL_MIN_EXCORT_PLANES**
  - Default: 0
  - Developer comment: Min amount of planes requested to excort operations

- **DEMOCRATIC_AI_FACTION_KICKING_PLAYER_THREAT_DIFFERENCE**
  - Default: 6.0
  - Developer comment: World threat generation difference needed to kick a player from a democratic faction

- **BEFRIEND_FACTOR_FOR_KICKING_COUNTRIES**
  - Default: 7.5
  - Developer comment: World threat difference addition per 100 befriend against a country, democratic leaders will forgive allies if they are befriending them

- **LAND_DEFENSE_AIR_SUPERIORITY_IMPORTANCE**
  - Default: 1.0
  - Developer comment: Strategic importance of air superiority ( amount of enemy planes in area )

- **LAND_DEFENSE_CIVIL_FACTORY_IMPORTANCE**
  - Default: 50
  - Developer comment: Strategic importance of civil factories

- **LAND_DEFENSE_MILITARY_FACTORY_IMPORTANCE**
  - Default: 70
  - Developer comment: Strategic importance of military factories

- **LAND_DEFENSE_NAVAL_FACTORY_IMPORTANCE**
  - Default: 30
  - Developer comment: Strategic importance of naval factories

- **LAND_DEFENSE_SUPPLY_HUB_IMPORTANCE**
  - Default: 4
  - Developer comment: Strategic importance of supply hubs

- **LAND_DEFENSE_AA_IMPORTANCE_FACTOR**
  - Default: 1.0
  - Developer comment: Factor of AA influence on strategic importance ( 0.0 - 1.0 )

- **LAND_DEFENSE_INFRA_IMPORTANCE_FACTOR**
  - Default: 0.5
  - Developer comment: Factor of infrastructure influence on strategic importance ( 0.0 - 1.0 )

- **LAND_DEFENSE_IMPORTANCE_SCALE**
  - Default: 3.0
  - Developer comment: Lend defence total importance scale (every land defence score get's multiplied by it)

- **NUM_HOURS_SINCE_LAST_COMBAT_TO_SUPPORT_UNITS_VIA_AIR**
  - Default: 72
  - Developer comment: units will be considered in combat if they are just out of their last combat for air supporting

- **LAND_DEFENSE_MIN_FACTORIES_FOR_AIR_IMPORTANCE**
  - Default: 5
  - Developer comment: If amount of factories is less importance of factories won't apply

- **LAND_DEFENSE_FIGHERS_PER_PLANE**
  - Default: 1.8
  - Developer comment: Amount of air superiority planes requested per enemy plane

- **LAND_DEFENSE_INTERSEPTORS_PER_BOMBERS**
  - Default: 0.8
  - Developer comment: Amount of air interceptor planes requested per enemy bomber

- **LAND_DEFENSE_INTERSEPTORS_PER_PLANE**
  - Default: 0.1
  - Developer comment: Amount of air interceptor planes requested per enemy plane (non bomber)

- **LAND_COMBAT_AIR_SUPERIORITY_IMPORTANCE**
  - Default: 0.40
  - Developer comment: Strategic importance of air superiority ( amount of enemy planes in area )

- **LAND_COMBAT_OUR_ARMIES_AIR_IMPORTANCE**
  - Default: 20
  - Developer comment: Strategic importance of our armies

- **LAND_COMBAT_OUR_COMBATS_AIR_IMPORTANCE**
  - Default: 155
  - Developer comment: Strategic importance of our armies in the combats

- **LAND_COMBAT_FRIEND_ARMIES_AIR_IMPORTANCE**
  - Default: 10
  - Developer comment: Strategic importance of friendly armies

- **LAND_COMBAT_FRIEND_COMBATS_AIR_IMPORTANCE**
  - Default: 8
  - Developer comment: Strategic importance of friendly armies in the combat

- **LAND_COMBAT_ENEMY_ARMIES_AIR_IMPORTANCE**
  - Default: 12
  - Developer comment: Strategic importance of our armies

- **LAND_COMBAT_ENEMY_LAND_FORTS_AIR_IMPORTANCE**
  - Default: 5
  - Developer comment: Strategic importance of enemy land forts in the region

- **LAND_COMBAT_ENEMY_COASTAL_FORTS_AIR_IMPORTANCE**
  - Default: 3
  - Developer comment: Strategic importance of enemy coastal fronts in the region

- **LAND_COMBAT_IMPORTANCE_SCALE**
  - Default: 5.0
  - Developer comment: Lend combat total importance scale (every land combat score get's multiplied by it)

- **LAND_COMBAT_FIGHTERS_PER_PLANE**
  - Default: 1.0
  - Developer comment: Amount of air superiority planes requested per enemy plane

- **LAND_COMBAT_CAS_PLANES_PER_ENEMY_ARMY_LIMIT**
  - Default: 200
  - Developer comment: Limit of CAS planes requested by enemy armies

- **LAND_COMBAT_CAS_PER_ENEMY_ARMY**
  - Default: 30
  - Developer comment: Amount of CAS planes requested per enemy division

- **LAND_COMBAT_ANTI_LOGISTICS_PER_ENEMY_ARMY**
  - Default: 0.1
  - Developer comment: Amount of CAS planes requested per enemy army for anti-logistics

- **LAND_COMBAT_CAS_PER_COMBAT**
  - Default: 60
  - Developer comment: Amount of CAS requested per combat

- **LAND_COMBAT_BOMBERS_PER_LAND_FORT_LEVEL**
  - Default: 6
  - Developer comment: Amount of bomber planes requested per enemy land fort level

- **LAND_COMBAT_BOMBERS_PER_COASTAL_FORT_LEVEL**
  - Default: 6
  - Developer comment: Amount of bomber planes requested per enemy coastal fort level

- **LAND_COMBAT_MIN_EXCORT_PLANES**
  - Default: 80
  - Developer comment: Min amount of planes requested to excort operations

- **LAND_COMBAT_INTERCEPT_PER_PLANE**
  - Default: 0.25
  - Developer comment: Amount of interception planes requested per enemy plane

- **MIN_ALLIED_DEFENSE_FACTOR_AIRWING_REQUESTS**
  - Default: 0.07
  - Developer comment: Airwing requests will be factored by a minimum of this when comparing own vs friendly troops in area

- **AIR_SUPERIORITY_FOR_FRIENDLY_CAS_RATIO**
  - Default: 0.75
  - Developer comment: Demand at least this proportion of our cas planes as air superiority regardless of other needs

- **LAND_COMBAT_GUIDE_DISTANCE**
  - Default: 290.0
  - Developer comment: Distance within whch we'll care a bit more about sending planes regardless of whether our boiz are dying

- **ENEMY_PASSING_THROUGH_PLANES_PER_BOMBER**
  - Default: 0.1
  - Developer comment: Amount of planes we assign to intercept enemies en-route to a location

- **ENEMY_PASSING_THROUGH_PLANES_PER_FIGHTER**
  - Default: 0.1
  - Developer comment: Amount of planes we assign to intercept enemies en-route to a location

- **ENEMY_PASSING_THROUGH_PLANES_PER_SUPPORT**
  - Default: 0.1
  - Developer comment: Amount of planes we assign to intercept enemies en-route to a location

- **AI_FRACTION_OF_FIGHTERS_RESERVED_FOR_INTERCEPTION**
  - Default: 0.25
  - Developer comment: Percentage of fighters we reserve for interception vs AS

- **MAX_AIR_REGIONS_TO_CARE_ABOUT**
  - Default: 6
  - Developer comment: Number of regions we'll consider when trying to split planes a bit. Split is NOT equal, just a guide, leftovers still applied elsewhere if needed

- **ENEMY_PASSING_THROUGH_PLANES_PER_BOMBER_NAVAL_REGION**
  - Default: 0.15
  - Developer comment: Amount of planes we assign to intercept enemies en-route to a location over a sea region

- **ENEMY_PASSING_THROUGH_PLANES_PER_FIGHTER_NAVAL_REGION**
  - Default: 0.15
  - Developer comment: Amount of planes we assign to intercept enemies en-route to a location over a sea region

- **ENEMY_PASSING_THROUGH_PLANES_PER_SUPPORT_NAVAL_REGION**
  - Default: 0.15
  - Developer comment: Amount of planes we assign to intercept enemies en-route to a location over a sea region

- **NAVAL_DEFENSE_INTERCEPTION_IMPORTANCE_FACTOR**
  - Default: 30
  - Developer comment: Factor on added planes passing through region to strategic importance

- **XP_RATIO_REQUIRED_TO_RESEARCH_WITH_XP**
  - Default: 2.0
  - Developer comment: AI will at least need this amount of xp compared to cost of a tech to reserch it with XP

- **RESEARCH_WITH_XP_AI_WEIGHT_MULT**
  - Default: 1.2
  - Developer comment: AI will bump score of a research with this mult if it can use XP

- **STR_BOMB_AIR_SUPERIORITY_IMPORTANCE**
  - Default: 0.10
  - Developer comment: Strategic importance of air superiority ( amount of enemy planes in area )

- **STR_BOMB_CIVIL_FACTORY_IMPORTANCE**
  - Default: 50
  - Developer comment: Strategic importance of enemy civil factories

- **STR_BOMB_MILITARY_FACTORY_IMPORTANCE**
  - Default: 70
  - Developer comment: Strategic importance of enemy military factories

- **STR_BOMB_NAVAL_FACTORY_IMPORTANCE**
  - Default: 30
  - Developer comment: Strategic importance of enemy naval factories

- **STR_BOMB_SUPPLY_HUB_IMPORTANCE**
  - Default: 1
  - Developer comment: Strategic importance of enemy supply hubs

- **STR_BOMB_AA_IMPORTANCE_FACTOR**
  - Default: 0.5
  - Developer comment: Factor of AA influence on strategic importance ( 0.0 - 1.0 )

- **STR_BOMB_INFRA_IMPORTANCE_FACTOR**
  - Default: 0.25
  - Developer comment: Factor of infrastructure influence on strategic importance ( 0.0 - 1.0 )

- **STR_BOMB_IMPORTANCE_SCALE**
  - Default: 1.0
  - Developer comment: str bombing total importance scale (every str bombing score get's multiplied by it)

- **STR_BOMB_MIN_ENEMY_FIGHTERS_IN_AREA**
  - Default: 2000
  - Developer comment: If amount of enemy fighters is higher than this mission won't perform

- **STR_BOMB_FIGHTERS_PER_PLANE**
  - Default: 1.1
  - Developer comment: Amount of air superiority planes requested per enemy plane

- **STR_BOMB_PLANES_PER_CIV_FACTORY**
  - Default: 20
  - Developer comment: Amount of planes requested per enemy civ factory

- **STR_BOMB_PLANES_PER_MIL_FACTORY**
  - Default: 25
  - Developer comment: Amount of planes requested per enemy military factory

- **STR_BOMB_PLANES_PER_NAV_FACTORY**
  - Default: 15
  - Developer comment: Amount of planes requested per enemy naval factory

- **STR_BOMB_PLANES_PER_SUPPLY_HUB**
  - Default: 3
  - Developer comment: Amount of planes requested per enemy supply node

- **STR_BOMB_MIN_EXCORT_PLANES**
  - Default: 200
  - Developer comment: Min amount of planes requested to excort operations

- **RECON_PLANES_NAVAL**
  - Default: 50
  - Developer comment: scale on recon for naval areas

- **RECON_PLANES_LAND_COMBAT**
  - Default: 25
  - Developer comment: scale on recon for land combat areas

- **RECON_PLANES_STRATEGIC**
  - Default: 50
  - Developer comment: scale on recon for strategic areas

- **ASSIGN_FRONT_ARMY_SOFT_ATTACK_FACTOR**
  - Default: 0.1
  - Developer comment: Importance of unit's ARMY_SOFT_ATTACK stat when assigning to a front

- **ASSIGN_FRONT_ARMY_HARD_ATTACK_FACTOR**
  - Default: 0.1
  - Developer comment: Importance of unit's ARMY_HARD_ATTACK stat when assigning to a front

- **ASSIGN_FRONT_ARMY_BREAKTHROUGH_FACTOR**
  - Default: 0.2
  - Developer comment: Importance of unit's ARMY_BREAKTHROUGH stat when assigning to a front

- **ASSIGN_DEFENSE_ARMY_DEFENSE_FACTOR**
  - Default: 3.0
  - Developer comment: Importance of unit's ARMY_DEFENSE stat when assigning to an area defense order

- **ASSIGN_DEFENSE_ARMY_ENTRENCHMENT_FACTOR**
  - Default: 2.0
  - Developer comment: Importance of unit's ARMY_ENTRENCHMENT stat when assigning to an area defense order

- **ASSIGN_DEFENSE_TEMPLATE_CLASS_SCORE**
  - Default: 3.0
  - Developer comment: Importance of unit's AI template class (AREA_DEFENSE, CAVALRY) when assigning to an area defense order

- **ASSIGN_INVASION_AMPHIBIOUS_ATTACK_FACTOR**
  - Default: 50.0
  - Developer comment: Importance of unit's amphibious attack adjuster when assigning to an invasion order

- **ORDER_ASSIGNMENT_DISTANCE_FACTOR**
  - Default: 100.0
  - Developer comment: When the AI assigns units to orders, how much should distance be taken into account?

- **REVISITED_PROV_BOOST_FACTOR**
  - Default: 4
  - Developer comment: When the AI picks units for a front, it prioritises units already nearby.

- **UNIT_ASSIGNMENT_STATS_IMPORTANCE**
  - Default: 3.0
  - Developer comment: Stats score for units are multiplied by this when the AI is deciding which front they should be assigned to

- **ASSIGN_FRONT_TERRAIN_ATTACK_FACTOR**
  - Default: 3.0
  - Developer comment: Importance of unit's terrain adjusted attack stat when assigning to a front

- **ASSIGN_FRONT_TERRAIN_DEFENSE_FACTOR**
  - Default: 1.0
  - Developer comment: Importance of unit's terrain adjusted defense stat when assigning to a front

- **ASSIGN_FRONT_TERRAIN_MOVEMENT_FACTOR**
  - Default: 2.0
  - Developer comment: Importance of unit's terrain adjusted movement stat when assigning to a front

- **ASSIGN_DEFENSE_TERRAIN_ATTACK_FACTOR**
  - Default: 0.5
  - Developer comment: Importance of unit's terrain adjusted attack stat when assigning to an area defense order

- **ASSIGN_DEFENSE_TERRAIN_DEFENSE_FACTOR**
  - Default: 4.0
  - Developer comment: Importance of unit's terrain adjusted defense stat when assigning to an area defense order

- **ASSIGN_DEFENSE_TERRAIN_MOVEMENT_FACTOR**
  - Default: 0.5
  - Developer comment: Importance of unit's terrain adjusted movement stat when assigning to an area defense order

- **ASSIGN_MOUNTAINEERS_TO_MOUNTAINS**
  - Default: 10.0
  - Developer comment: factor for assigning mountaineer divisions to fronts with mountains (proportional to how much of that terrain type)

- **ASSIGN_TANKS_TO_MOUNTAINS**
  - Default: -6.0
  - Developer comment: factor for assigning tank divisions to fronts with mountains (proportional to how much of that terrain type)

- **ASSIGN_TANKS_TO_JUNGLE**
  - Default: -6.0
  - Developer comment: factor for assigning tank divisions to fronts with jungle (proportional to how much of that terrain type)

- **UNIT_ASSIGNMENT_TERRAIN_IMPORTANCE**
  - Default: 10.0
  - Developer comment: Terrain score for units are multiplied by this when the AI is deciding which front they should be assigned to

- **ASSIGN_TANKS_TO_WAR_FRONT**
  - Default: 6.0
  - Developer comment: Scoring factor for assigning divisions with 'role = armor' or 'front_role_override = offence' to active war fronts

- **ASSIGN_TANKS_TO_NON_WAR_FRONT**
  - Default: 0.4
  - Developer comment: Scoring factor for assigning divisions with 'role = armor' or 'front_role_override = offence' to non-war fronts

- **REASSIGN_TO_ANOTHER_FRONT_FACTOR**
  - Default: 0.5
  - Developer comment: Factor for reassigning to another front. 0.0 < X < 1.0 means reluctant, X > 1.0 means want to.

- **REASSIGN_TO_ANOTHER_FRONT_IF_IN_COMBAT_FACTOR**
  - Default: 0.2
  - Developer comment: Factor for reassigning to another front if in combat. 0.0 < X < 1.0 means reluctant, X > 1.0 means want to.

- **ENEMY_FORTIFICATION_FACTOR_FOR_FRONT_REQUESTS**
  - Default: 2.0
  - Developer comment: front unit request factor at max enemy fortification

- **ENEMY_FORTIFICATION_FACTOR_FOR_FRONT_REQUESTS_MAX**
  - Default: 0.7
  - Developer comment: max factor that can be added by enemy fortification

- **MANPOWER_RATIO_CAREFULNESS_THRESHOLD**
  - Default: 0.05
  - Developer comment: if manpower ratio (available/used-by-army) is less than this, start being more careful with plan execution (i.e. don't throw your men into the meat grinder if you're running out of manpower)

- **PLAN_ACTIVATION_SUPERIORITY_AGGRO**
  - Default: 1.0
  - Developer comment: How aggressive a country is in activating a plan based on how superiour their force is.

- **WAIT_YEARS_BEFORE_FREER_BUILDING**
  - Default: 3
  - Developer comment: The AI will skip considering certain buildings during the buildup phase, after htese many years it starts building them regardless of threat.

- **MAX_CARRIER_OVERFILL**
  - Default: 1.85
  - Developer comment: Carriers will be overfilled to this amount if there are doctrines to justify it

- **FIELDED_EQUIPMENT_BUFFER_RATIO_FOR_OCCUPATION_AI**
  - Default: 0.5
  - Developer comment: garrison ai will try to leave this ratio of buffers while assigning laws

- **FIELDED_MANPOWER_BUFFER_RATIO_FOR_OCCUPATION_AI**
  - Default: 0.3
  - Developer comment: garrison ai will try to leave this ratio of buffers while assigning laws

- **IMPORTANT_VICTORY_POINT**
  - Default: 15
  - Developer comment: during occupation ai will only care so much to ask for extra garrisons if VP amount is at least this

- **DOCKYARDS_PER_NAVAL_DESIRE_EFFECT**
  - Default: -20.0
  - Developer comment: Effects how much AI wants to build dockyards based on how navally focused they are in general. Recommended range -100.0 to 100.0.

- **DECISION_PRIORITY_RANDOMIZER**
  - Default: 0.1
  - Developer comment: random factor that is used while picking decisions. ai is able to pick a lower priority decision earler than a higher one if it is within this threshold

- **DESIGN_COMPANY_SCORE_MULTIPLIER**
  - Default: 1.25
  - Developer comment: score multiplier for hiring a design company

- **ARMY_CHIEF_SCORE_MULTIPLIER**
  - Default: 2.0
  - Developer comment: score multiplier for hiring an army chief

- **AIR_CHIEF_SCORE_MULTIPLIER**
  - Default: 1.5
  - Developer comment: score multiplier for hiring an air chief

- **NAVY_CHIEF_SCORE_MULTIPLIER**
  - Default: 1.0
  - Developer comment: score multiplier for hiring an navy chief

- **POLITICAL_ADVISOR_SCORE_MULTIPLIER**
  - Default: 1.25
  - Developer comment: score multiplier for hiring political advisors

- **THEORIST_ACCEPTANCE_MULTIPLIER**
  - Default: 0.7
  - Developer comment: scale the acceptance of hiring a theorist by this number times the amount of non-theorists we have, capped at one.

- **MIN_SCALED_IDEA_WEIGHT_TO_COMPARE_WITH_DECISIONS**
  - Default: 100
  - Developer comment: idea scores are scaled between these two values while comparing them to decisions

- **MAX_SCALED_IDEA_WEIGHT_TO_COMPARE_WITH_DECISIONS**
  - Default: 200
  - Developer comment: idea scores are scaled between these two values while comparing them to decisions

- **CRITICAL_DECISION_PRIORITY**
  - Default: 200
  - Developer comment: critical ai score for decisions, ai will be able to pick decisions if it has higher prio even if it is not time to pick them (0 to disable)

- **CRITICAL_IDEA_PRIORITY**
  - Default: 400
  - Developer comment: critical ai score for ideas, ai will be able to pick ideas if it has higher prio even if it is not time to pick them (0 to disable)

- **MAX_PP_TO_SPEND_ON_LOWER_PRIO_TASKS**
  - Default: 25
  - Developer comment: max pp cost for ai to allow spend pp on lower prio things while a higher prio things are available

- **MIN_SCORE_FOR_LOWER_PRIO_TASKS**
  - Default: 100
  - Developer comment: this is a threshold for low prio tasks that will be considered critical

- **LOW_PRIO_TEMPLATE_BONUS_FOR_GARRISONS**
  - Default: 1000
  - Developer comment: bonus to make ai more likely to assign low prio units to garrisons

- **LOW_PRIO_TEMPLATE_PENALTY_FOR_FRONTS**
  - Default: 500
  - Developer comment: penalty to make ai less likely to assign low prio units to fronts

- **DEPLOYED_UNIT_MANPOWER_RATIO_TO_BUFFER_WARTIME**
  - Default: 0.2
  - Developer comment: deployment will try to buffer a ratio of deployed manpower (for reinforcements) during war time

- **DEPLOYED_UNIT_MANPOWER_RATIO_TO_BUFFER_PEACETIME**
  - Default: 0.1
  - Developer comment: deployment will try to buffer a ratio of deployed manpower (for reinforcements) during peace time

- **MAX_AVAILABLE_MANPOWER_RATIO_TO_BUFFER_WARTIME**
  - Default: 0.4
  - Developer comment: deployment will try to buffer a ratio of manpower (for reinforcements) during war time

- **MAX_AVAILABLE_MANPOWER_RATIO_TO_BUFFER_PEACETIME**
  - Default: 0.2
  - Developer comment: deployment will try to buffer a ratio of manpower (for reinforcements) during peace time

- **MANPOWER_RATIO_REQUIRED_TO_PRIO_MOBILIZATION_LAW**
  - Default: 0.4
  - Developer comment: percentage of manpower in field is desired to be buffered for AI when it has upcoming wars or already at war. if it has less manpower, it will prio manpower laws

- **UPGRADES_DEFICIT_LIMIT_DAYS**
  - Default: 7
  - Developer comment: Ai will avoid upgrading units in the field to new templates if it takes longer than this to fullfill their equipment need

- **GIE_EXILE_AIR_MANPOWER_USAGE_RATIO**
  - Default: 0.2
  - Developer comment: AI will not deploy new exile wings when this percentage of available exile manpower is already used for wing recruitment.

- **CARRIER_TASKFORCE_MAX_CARRIER_COUNT**
  - Default: 4
  - Developer comment: optimum carrier count for carrier taskforces

- **CAPITAL_TASKFORCE_MAX_CAPITAL_COUNT**
  - Default: 12
  - Developer comment: optimum capital count for capital taskforces

- **SCREEN_TASKFORCE_MAX_SHIP_COUNT**
  - Default: 12
  - Developer comment: optimum screen count for screen taskforces

- **SUB_TASKFORCE_MAX_SHIP_COUNT**
  - Default: 16
  - Developer comment: optimum sub count for sub taskforces

- **MIN_CAPITALS_FOR_CARRIER_TASKFORCE**
  - Default: 6
  - Developer comment: carrier fleets will at least have this amount of capitals

- **CAPITALS_TO_CARRIER_RATIO**
  - Default: 1.5
  - Developer comment: capital to carrier count in carrier taskfoces

- **SCREENS_TO_CAPITAL_RATIO**
  - Default: 4.0
  - Developer comment: screens to capital/carrier count in carrier & capital taskforces

- **MIN_MAIN_SHIP_RATIO**
  - Default: 0.3
  - Developer comment: if main ship ratio is below this, steal other ships.

- **MIN_SUPPORT_SHIP_RATIO**
  - Default: 0.7
  - Developer comment: if support ship ratio is below this, steal other ships.

- **MIN_MAIN_SHIP_RATIO_TO_REINFORCE**
  - Default: 0.5
  - Developer comment: the main ships will be tried to reinforce this level.

- **MIN_SUPPORT_SHIP_RATIO_TO_REINFORCE**
  - Default: 0.9
  - Developer comment: the support ships will be tried to reinforce this level.

- **MIN_MAIN_SHIP_TO_SPARE**
  - Default: 0.7
  - Developer comment: can only steal ships from a task force if their main ship ratio is above this.

- **MIN_SUPPORT_SHIP_TO_SPARE**
  - Default: 1.0
  - Developer comment: can only steal ships from a task force if their support ship ratio is above this.

- **MIN_MAIN_SHIP_RATIO_TO_MERGE**
  - Default: 0.7
  - Developer comment: try merge task force if main ship ratio is lower than this.

- **MAX_MAIN_SHIP_RATIO_TO_MERGE**
  - Default: 1.001
  - Developer comment: if resulting main ship ratio would be at most this, allow merging into this task force.

- **MAIN_SHIP_RATIO_TO_SPLIT**
  - Default: 1.8
  - Developer comment: if main ship ratio in a task force is larger than this, split it. (If a carrier TF wants 4 carriers (see defines above), but it has more than [this * 4] carriers, then we try to split the TF.)

- **MISSION_FLEET_ICONS**
  - Default: { 4, 29, 21, 15, 23, 24, 5, 4, 4, 9 }
  - Developer comment:
    ```text
    HOLD
    PATROL
    STRIKE FORCE
    CONVOY RAIDING
    CONVOY ESCORT
    MINES PLANTING
    MINES SWEEPING
    TRAIN
    RESERVE_FLEET
    NAVAL INVASION SUPPORT
    ```

- **MIN_NAVAL_MISSION_PRIO_TO_ASSIGN**
  - Default: { 0, 200, 200, 200, 100, 200, 100, 0, 0, 100 }
  - Developer comment:
    ```text
    priorities for regions to get assigned to a mission
    HOLD (consumes fuel HOLD_MISSION_MOVEMENT_COST fuel while moving)
    PATROL
    STRIKE FORCE
    CONVOY RAIDING
    CONVOY ESCORT
    MINES PLANTING
    MINES SWEEPING
    TRAIN
    RESERVE_FLEET
    NAVAL INVASION SUPPORT
    ```

- **HIGH_PRIO_NAVAL_MISSION_SCORES**
  - Default: { 0, 100000, 1000, 1500, 1000, -1, 300, 0, 0, 1000 }
  - Developer comment:
    ```text
    priorities for regions to get assigned to a mission
    HOLD (consumes fuel HOLD_MISSION_MOVEMENT_COST fuel while moving)
    PATROL
    STRIKE FORCE
    CONVOY RAIDING
    CONVOY ESCORT
    MINES PLANTING
    MINES SWEEPING
    TRAIN
    RESERVE_FLEET
    NAVAL INVASION SUPPORT
    ```

- **MAX_MISSION_PER_TASKFORCE**
  - Default: { 0, 1.5, 6, 1.5, 4, 2, 2, 0, 0, 10 }
  - Developer comment:
    ```text
    max mission region/taskforce ratio
    HOLD (consumes fuel HOLD_MISSION_MOVEMENT_COST fuel while moving)
    PATROL
    STRIKE FORCE
    CONVOY RAIDING
    CONVOY ESCORT
    MINES PLANTING
    MINES SWEEPING
    TRAIN
    RESERVE_FLEET
    NAVAL INVASION SUPPORT
    ```

- **MAX_SCREEN_TASKFORCES_FOR_CONVOY_DEFENSE_MIN**
  - Default: 0.20
  - Developer comment:
    ```text
    all-screen taskforces will be shared between convoy defense, mine missions and patrols (in this prio)
    and these ratios limits the maximum ratio of these taskforces to allocate on type
    maximum ratio of all screen-ships forces to be used in convoy defense (increases up to max as AI loses convoys).
    ```

- **MAX_SCREEN_TASKFORCES_FOR_CONVOY_DEFENSE_MAX**
  - Default: 0.70
  - Developer comment: maximum ratio of all screen-ships forces to be used in convoy defense (increases up to max as AI loses convoys).

- **MAX_SCREEN_TASKFORCES_FOR_CONVOY_DEFENSE_MIN_CONVOY_THREAT**
  - Default: 100
  - Developer comment: AI will increase screen assignment for escort missions as threate increases

- **MAX_SCREEN_TASKFORCES_FOR_CONVOY_DEFENSE_MAX_CONVOY_THREAT**
  - Default: 1500
  - Developer comment: AI will increase screen assignment for escort missions as threate increases

- **MAX_SCREEN_TASKFORCES_FOR_MINE_SWEEPING**
  - Default: 0.10
  - Developer comment: maximum ratio of screens forces to be used in mine sweeping

- **MAX_SCREEN_TASKFORCES_FOR_MINE_SWEEPING_PRIO**
  - Default: 0.8
  - Developer comment: if you have mines near your owned states, you will start priotize mine missions and will assign this ratio of screens

- **MAX_SCREEN_TASKFORCES_FOR_MINE_SWEEPING_PRIO_MIN_MINES**
  - Default: 10
  - Developer comment: lowest mine for prioing mine missions

- **MAX_SCREEN_TASKFORCES_FOR_MINE_SWEEPING_PRIO_MAX_MINES**
  - Default: 1000
  - Developer comment: highest mines for highest prio for mine missions

- **MAX_SCREEN_TASKFORCES_FOR_MINE_LAYING**
  - Default: 0.10
  - Developer comment: maximum ratio of screens forces to be used in mine laying

- **MAX_SCREEN_FORCES_FOR_INVASION_SUPPORT**
  - Default: 0.25
  - Developer comment: max ratio of screens forces to be used in naval invasion missions

- **MAX_CAPITAL_FORCES_FOR_INVASION_SUPPORT**
  - Default: 0.25
  - Developer comment: max ratio of capital forces to be used in naval invasion missions

- **MAX_PATROL_TO_STRIKE_FORCE_RATIO**
  - Default: 3.0
  - Developer comment: maximum patrol/strike force ratio

- **CONSTRUCTION_PRIO_INFRASTRUCTURE**
  - Default: 0.20
  - Developer comment:
    ```text
    <start> construction prioritization
    base prio for infrastructure in the construction queue
    ```

- **CONSTRUCTION_PRIO_CIV_FACTORY**
  - Default: 0.80
  - Developer comment: base prio for civilian factories in the construction queue

- **CONSTRUCTION_PRIO_MIL_FACTORY**
  - Default: 0.70
  - Developer comment: base prio for military factories in the construction queue

- **CONSTRUCTION_PRIO_RAILWAY**
  - Default: 4.00
  - Developer comment: base prio for railways in the construction queue

- **CONSTRUCTION_PRIO_RAILWAY_GUN_REPAIR**
  - Default: 15.00
  - Developer comment: base prio for railway gun repairs in the construction queue

- **CONSTRUCTION_PRIO_UNSPECIFIED**
  - Default: 0.50
  - Developer comment: base prio for unspecified buildings (none of the categories above) in the construction queue

- **CONSTRUCTION_PRIO_FACTOR_OCCUPIED_TERRITORY**
  - Default: 1.00
  - Developer comment: factor prio with this if occupied territory

- **CONSTRUCTION_PRIO_FACTOR_OWNED_NONCORE**
  - Default: 1.50
  - Developer comment: factor prio with this if owned non-core territory

- **CONSTRUCTION_PRIO_FACTOR_OWNED_CORE**
  - Default: 2.00
  - Developer comment: factor prio with this if owned core territory

- **CONSTRUCTION_PRIO_FACTOR_REPAIRING**
  - Default: 0.30
  - Developer comment: factor prio with this if building is being repaired

- **MAX_FACTORY_TO_SPARE_FOR_MISSION_FUEL_TRADE**
  - Default: 0.12
  - Developer comment:
    ```text
    <end> construction prioritization
    amount of factories to spend on oil trade in case of fuel need for missions
    ```

- **MAX_FACTORY_TO_SPARE_FOR_CRITICAL_MISSION_FUEL_TRADE**
  - Default: 0.3
  - Developer comment: amount of factories to spend on oil trade in case of fuel need for prio missions

- **MAX_FACTORY_TO_TRADE_FOR_FUEL**
  - Default: 0.5

- **FUEL_TRADE_PRIO_FOR_CONVOY_DEFENSE**
  - Default: 0.3
  - Developer comment: AI will be less reluctant to cancel convoy missions if it is trading for oil

- **MAX_FACTORY_TO_SPARE_FOR_MISSION_FUEL_TRADE_IN_PEACE**
  - Default: 0.03
  - Developer comment: amount of factories to spend on oil trade in case of fuel need for missions in peace time

- **MAX_FACTORY_TO_SPARE_FOR_CRITICAL_MISSION_FUEL_TRADE_IN_PEACE**
  - Default: 0.1
  - Developer comment: amount of factories to spend on oil trade in case of fuel need for prio missions in peace time

- **MAX_FACTORY_TO_TRADE_FOR_FUEL_IN_PEACE**
  - Default: 0.15

- **FUEL_REQUEST_RATIO_FOR_COMBATS**
  - Default: 0.6
  - Developer comment: ratio of ship combat fuel cost that is to be considered in fuel usage and request system

- **PRIO_FUEL_REQUEST_RATIO_FOR_COMBATS**
  - Default: 0.8
  - Developer comment: ratio of ship combat fuel cost that is to be considered in prio fuel usage and request system

- **FUEL_REQUEST_RATIO_FOR_MOVEMENT**
  - Default: 0.4
  - Developer comment: ratio of ship movement fuel cost that is to be considered in fuel usage and request system

- **PRIO_FUEL_REQUEST_RATIO_FOR_MOVEMENT**
  - Default: 0.2
  - Developer comment: ratio of ship movement fuel cost that is to be considered in prio fuel usage and request system

- **NAVY_ACTUAL_FUEL_USAGE_WEIGHT_ON_OIL_REQUEST**
  - Default: 0.5
  - Developer comment: weight of actual fuel usage of ships compared to what is being asked for missions while calculating oil needed for trade

- **AIR_ACTUAL_FUEL_USAGE_WEIGHT_ON_OIL_REQUEST**
  - Default: 0.5
  - Developer comment: weight of actual fuel usage of planes compared to what is being asked for missions while calculating oil needed for trade

- **MONTHS_TO_FILL_FUEL_BUFFER_WITH_OIL_REQUESTS**
  - Default: 6.0
  - Developer comment: in war time, coutries will try to fill their buffer in this duration and trade for oil if necesarry

- **MONTHS_TO_FILL_FUEL_BUFFER_WITH_OIL_REQUESTS_IN_PEACE_TIME**
  - Default: 10.0
  - Developer comment: in peace time, coutries will try to fill their buffer in this duration and trade for oil if necesarry

- **FUEL_CONSUMPTION_MULT_FOR_FUEL_SAVING_MODE**
  - Default: 0.25
  - Developer comment: fuel consumptions will be limited by this ratio in fuel saving mode

- **FUEL_CONSUMPTION_MULT_REGULAR_FUEL_MODE**
  - Default: 1.0
  - Developer comment: fuel consumptions will be limited by this ratio in regular fuel mode

- **FUEL_CONSUMPTION_MULT_AGRESSIVE_FUEL_MODE**
  - Default: 3.0
  - Developer comment: fuel consumptions will be limited by this ratio in aggressive fuel usage mode

- **DAYS_FUEL_REMAINING_TO_ENTER_FUEL_SAVING_MODE**
  - Default: 30
  - Developer comment: countries will enter fuel saving mode if they will be out of fuel in this number of days and their fuel ratio is below next define

- **DAYS_FUEL_REMAINING_TO_ENTER_FUEL_SAVING_MODE_FUEL_RATIO**
  - Default: 0.4

- **FUEL_RATIO_TO_EXIST_FUEL_SAVING_MODE**
  - Default: 0.60
  - Developer comment: countries will exit fuel saving mode if they have more fuel ratio than this

- **WANTED_MAX_FUEL_BUFFER_IN_DAYS_FOR_ARMY_MAX_CONSUMPTION**
  - Default: 60
  - Developer comment: AI will try to buffer at least this amount of days on max consumption, will trade if necesarry and will go into fuel saving mode/aggresive mode using this buffer

- **WANTED_MAX_FUEL_BUFFER_IN_DAYS_FOR_AIR_MAX_CONSUMPTION**
  - Default: 60
  - Developer comment: AI will try to buffer at least this amount of days on max consumption, will trade if necesarry and will go into fuel saving mode/aggresive mode using this buffer

- **WANTED_MAX_FUEL_BUFFER_IN_DAYS_FOR_NAVY_MAX_CONSUMPTION**
  - Default: 60
  - Developer comment: AI will try to buffer at least this amount of days on max consumption, will trade if necesarry and will go into fuel saving mode/aggresive mode using this buffer

- **MIN_WANTED_MAX_FUEL**
  - Default: 50
  - Developer comment: minimum value for wanted fuel buffers for AI (in thousands)

- **GIE_LEND_LEASE_TO_PLAYER_EXILE_DESIRE_BONUS**
  - Default: 40
  - Developer comment: AI host is more likely to accept lend lease requests from a player.

- **NAVAL_BASE_RATIO_ALLOCATED_FOR_REPAIRS**
  - Default: 0.25
  - Developer comment: ai will allocate at most this ratio of dockyards for repairs in peace time

- **NAVAL_BASE_RATIO_ALLOCATED_FOR_REPAIRS_IN_WAR_TIME**
  - Default: 0.6
  - Developer comment: ai will allocate at most this ratio of dockyards for repairs in war time

- **MAX_FUEL_CONSUMPTION_RATIO_FOR_AIR_TRAINING**
  - Default: 0.20
  - Developer comment: ai will use at most this ratio of affordable fuel for air training

- **MAX_FUEL_CONSUMPTION_RATIO_FOR_NAVY_TRAINING**
  - Default: 0.20
  - Developer comment: ai will use at most this ratio of affordable fuel for naval training

- **MAX_FULLY_TRAINED_SHIP_RATIO_FOR_TRAINING**
  - Default: 0.7
  - Developer comment: ai will not train a taskforce if fully trained ships are above this ratio

- **NUM_SILOS_PER_CIVILIAN_FACTORIES**
  - Default: 0.0025
  - Developer comment: ai will try to build a silo per this ratio of civ factories

- **NUM_SILOS_PER_MILITARY_FACTORIES**
  - Default: 0.012
  - Developer comment: ai will try to build a silo per this ratio of mil factories

- **NUM_SILOS_PER_DOCKYARDS**
  - Default: 0.02
  - Developer comment: ai will try to build a silo per this ratio of dockyards

- **SHIP_STR_RATIO_PUT_ON_REPAIRS**
  - Default: 0.8
  - Developer comment: if ships are damaged below this ratio, they are put for repairs

- **SHIP_STR_RATIO_EXIT_REPAIRS**
  - Default: 1.00
  - Developer comment: the ships will leave repairs if they are >= this ratio of total str

- **REPAIR_TASKFORCE_SIZE**
  - Default: 4
  - Developer comment: repair taskforce sizes are limited to this many ships

- **PLAN_VALUE_BONUS_FOR_MOVING_UNITS**
  - Default: 0.35
  - Developer comment: AI plans gets a bonus when units are not moving and ready to fight

- **AGGRESSIVENESS_BONUS_FOR_FRONTS_THAT_ARE_ON_HIGH_AGGRESSIVENESS**
  - Default: -0.4
  - Developer comment: AI gets a bonus to aggresiveness if it is already executing an aggressive plan (lower is more aggressive)

- **AGGRESSIVENESS_CHECK_BASE**
  - Default: 1.5
  - Developer comment: front comparison where ai will consider aggressive stance, unless it is already then the number above is used

- **AGGRESSIVENESS_CHECK_EASY_TARGET**
  - Default: -0.3
  - Developer comment: if target nation is flagged as easy target we also adjust down the front comparison needed

- **AGGRESSIVENESS_CHECK_CAREFUL**
  - Default: 0.6
  - Developer comment: at what front strength balance do we go careful

- **AGGRESSIVENESS_CHECK_PARTLY_FORTIFIED**
  - Default: 2.0
  - Developer comment: if front strength balance is at or above this value versus a party fortified enemy, we do a balanced attack

- **AGGRESSIVENESS_CHECK_PARTLY_FORTIFIED_WEAK_POINTS**
  - Default: 0.75
  - Developer comment: if front strength balance is at or above this value versus a party fortified enemy, we rush attack weak points; below this value, we are careful

- **AGGRESSIVENESS_CHECK_FULLY_FORTIFIED**
  - Default: 10
  - Developer comment: if front strength balance is at or above this value versus a fully fortified enemy with no weak points, we do a balanced attack instead being careful

- **AGGRESSIVENESS_CHECK_FULLY_FORTIFIED_POCKET**
  - Default: 6
  - Developer comment: if front strength balance is at or above this value versus a fully fortified enemy in a pocket, we do a balanced attack instead being careful

- **FRONT_EVAL_UNIT_ACCURACY**
  - Default: 1.0
  - Developer comment: scale how stupid ai will act on fronts. 0 is potato

- **FRONT_EVAL_UNIT_AIR_SUP_IMPACT**
  - Default: 1.0
  - Developer comment: scale how good the AI thinks air superiority is for units

- **FRONT_EVAL_UNIT_SUPPLY_AND_ORG_LACK_IMPACT**
  - Default: 1.0
  - Developer comment: scale how painful the AI thinks a combined lack of supply and organization is for units

- **FRONT_EVAL_PERCENT_TO_ASSIST_ALLY_FRONT**
  - Default: 0.5
  - Developer comment: percentage of how many units the AI thinks it should have compared to an ally before considering sending units

- **PRODUCTION_CARRIER_PLANE_BUFFER_RATIO**
  - Default: 1.5
  - Developer comment: in addition to total deck size of carriers, we want at least this ratio to buffer it

- **PRODUCTION_CARRIER_PLANE_PRODUCTION_BOOST_TO_BUFFER**
  - Default: 4.0
  - Developer comment: production of carrier planes will go up by this ratio if we lack buffers

- **NAVAL_MAX_CONVOY_TO_INTEL_FOR_CONVOY_RAIDS**
  - Default: 200
  - Developer comment: number of convoys in region will be clamped to this max, anything more will be ignored while assigning raids

- **EXTRA_NAVY_INTEL_FOR_CONVOY_RAIDING**
  - Default: 0.0
  - Developer comment: this amount of intel is added to navy intel while ai is assigning convoy raiding mission

- **INTEL_NEEDED_TO_NEGATVE_CONVOY_COUNT_REDUCTION**
  - Default: 80.0
  - Developer comment: navy intel is divided by this ratio to negate NAVAL_CONVOY_COUNT_INTEL_DROPOFF_DUE_TO_LOW_DECYPTION

- **NAVAL_CONVOY_COUNT_INTEL_DROPOFF_DUE_TO_LOW_DECYPTION**
  - Default: 200
  - Developer comment: on lowest navy intel, ai won't be able to see enemy convoys lower than this ratio

- **CONVOY_RAID_SCORE_FROM_CONVOY_INTELLIGENCE**
  - Default: 2.5
  - Developer comment: each convoy intelligenge will incease raid score by this

- **AIR_AI_ENEMY_PROV_RATIO_FOR_COMBAT_REGION**
  - Default: 0.15
  - Developer comment: if a region has more than this ratio of provinces controlled by enemy, AI will consider it as a combat zone while assigning planes

- **RESEARCH_MULTI_DOCTRINE_SCORE**
  - Default: 0.3
  - Developer comment: score penalty to researchign multiple doctrines at once for AI

- **CONVOY_ESCORT_SCORE_FROM_CONVOYS**
  - Default: 15
  - Developer comment: score for each convoy you have in area

- **CONVOY_ESCORT_MUL_FROM_NO_CONVOYS**
  - Default: 0.02
  - Developer comment: score multiplier when no convoys are around

- **CONVOY_RAID_MIN_ENEMY_THREAT**
  - Default: 0.05

- **RAILWAY_GUN_PRODUCTION_BASE_DIVISIONS_RATIO_PERCENT**
  - Default: 0
  - Developer comment: Base ratio of desired railway guns to divisions for AI (5 means 5%). Can be modified by railway_guns_divisions_ratio AI strategy value

- **RAILWAY_GUN_PRODUCTION_MIN_DIVISONS**
  - Default: 20
  - Developer comment: Minimum required number of divisions for the AI to consider producing railway guns

- **RAILWAY_GUN_PRODUCTION_MIN_FACTORIES**
  - Default: 10
  - Developer comment: Minimum required number of military factories for the AI to consider producing railway guns

- **RAILWAY_GUN_PER_ARMY_CAP**
  - Default: 5
  - Developer comment: Maximum railway guns assigned to one army for the AI

- **RAILWAY_GUN_ASSIGNMENT_SCORE_UNITCOUNT_MULTIPLIER**
  - Default: 10.0
  - Developer comment: Score multiplier for favoring orders groups with more units when assigning railway guns

- **RAILWAY_GUN_ASSIGNMENT_SCORE_HOLD**
  - Default: 20
  - Developer comment: Score for keeping current assignment when assigning railway guns

- **MAX_UNIT_RATIO_FOR_INVASIONS**
  - Default: 0.4
  - Developer comment: countries won't use armies more than this ratio of total units for invasions

- **MIN_UNIT_RATIO_FOR_INVASIONS**
  - Default: 0.1
  - Developer comment: don't allocate more divisions than this for naval invasions

- **MAX_INVASION_FRONT_SCORE**
  - Default: 1000
  - Developer comment: max score for naval invasion front scores

- **MIN_FRONT_SCORE_FOR_AFTER_INVASION_AREAS**
  - Default: 1500
  - Developer comment: min score for army fronts that are created on recently invaded regions

- **MIN_CONVOY_EFFICIENCY_TO_CANCEL_TRADES**
  - Default: 0.4
  - Developer comment: min efficiency (due to convoy raid) to cancel trades

- **MIN_CONVOY_EFFICIENCY_TO_START_TRADES**
  - Default: 0.6
  - Developer comment: min efficiency (due to convoy raid) to start be able to trades

- **MIN_CONVOY_EFFICIENCY_PER_WAR_SUPPORT_HIT**
  - Default: 0.6
  - Developer comment: percentage of warsupport hit you get is multiplied by this value and added to min convoy efficiencies

- **NAVAL_INVADED_AREA_PRIO_DURATION**
  - Default: 90
  - Developer comment: after successful invasion, AI will prio the enemy area for this number of days

- **NAVAL_INVADED_AREA_PRIO_MULT**
  - Default: 1.2
  - Developer comment: fronts that belongs to recent invasions gets more prio

- **MIN_NUM_CONQUERED_PROVINCES_TO_DEPRIO_NAVAL_INVADED_FRONTS**
  - Default: 20
  - Developer comment: if you conquer this amount of provinces after a naval invasion, it will lose its prio status and will act as a regular front

- **FAILED_INVASION_AVOID_DURATION**
  - Default: 60
  - Developer comment: after a failed invasion, AI will down-prioritize invading the same area again for this number of days

- **FAILED_INVASION_AREA_PRIO_FACTOR**
  - Default: 0.5
  - Developer comment: for every failed invasion on an area, factor that area's invasion prio with this value

- **FAILED_INVASION_PORT_PRIO_FACTOR**
  - Default: 0.66
  - Developer comment: for every failed invasion on a target port (province), factor the chance that we try to invade that same port again (relative to other ports)

- **BUILDING_TARGETS_BUILDING_PRIORITIES**
  - Default: { "industrial_complex" }
  - Developer comment: buildings in order of pirority when considering building targets strategies. First has the greatest priority, omitted has the lowest. NOTE: not all buildings are supported by building targets strategies.

- **MIN_INVASION_PLAN_VALUE_TO_EXECUTE**
  - Default: 0.2
  - Developer comment: ai will only activate invasions if plan value is above this

- **MIN_INVASION_ORG_FACTOR_TO_EXECUTE**
  - Default: 0.75
  - Developer comment: ai will only activate invasions if average org factor is above this

- **MAX_INVASION_SIZE**
  - Default: 24
  - Developer comment: max invasion group size

- **MAX_PORT_STRIKE_HISTORY_TO_REMEMBER**
  - Default: 5000
  - Developer comment: maximum port strike history to keep track (will be used to disable ports

- **PORT_STRIKE_HISTORY_DECAY_MIN**
  - Default: 10
  - Developer comment: minimum decay for port strike history (<7 days since last port strike)

- **PORT_STRIKE_HISTORY_DECAY_MAX**
  - Default: 400
  - Developer comment: maximum decay for port strike history (>=37 days since last port strike)

- **MAX_PORT_RATIO_TO_DISABLE**
  - Default: 0.8
  - Developer comment: max ratio of ports to disable due to port strikes

- **PORT_STRIKE_HISTORY_VALUE_TO_DISABLE_REPAIRS**
  - Default: 200
  - Developer comment: cut off for disabling ports above this threshold

- **PORT_STRIKE_HISTORY_VALUE_TO_REENABLE_REPAIRS**
  - Default: 10
  - Developer comment: cut off for reenabling ports bloew this threshold

- **CURRENT_LAW_SCORE_BONUS**
  - Default: 50.0
  - Developer comment: current score will get an additional bonus to its ai weight

- **OIL_WANT_PER_POTENTIAL_LAND_CONSUMPTION_K**
  - Default: 0.05
  - Developer comment:
    ```text
    these values are used for ai_desire_ variables that are used occupation law selection
    how much extra oil requested on top of balance for country's potential oil consumptions
    ```

- **OIL_WANT_PER_POTENTIAL_NAVY_CONSUMPTION_K**
  - Default: 0.03

- **OIL_WANT_PER_POTENTIAL_AIR_CONSUMPTION_K**
  - Default: 0.03

- **OIL_WANT_PER_POTENTIAL_MISC_CONSUMPTION_K**
  - Default: 0.1

- **OIL_WANT_AT_PEACE_PER_POTENTIAL_LAND_CONSUMPTION_K**
  - Default: 0.02

- **OIL_WANT_AT_PEACE_PER_POTENTIAL_NAVY_CONSUMPTION_K**
  - Default: 0.0

- **OIL_WANT_AT_PEACE_PER_POTENTIAL_AIR_CONSUMPTION_K**
  - Default: 0.0

- **OIL_WANT_AT_PEACE_PER_POTENTIAL_MISC_CONSUMPTION_K**
  - Default: 0.1

- **RESOURCE_WANT_PER_MISSING_BALANCE**
  - Default: 0.2
  - Developer comment: negative balance increases the desire on a resource

- **RESOURCE_WANT_PER_CONSUMED**
  - Default: 0.05
  - Developer comment: if resource is being used in production, increase the desire

- **CRYPTO_ACTIVATION_THRESHOLD**
  - Default: 1.25
  - Developer comment:
    ```text
    ~end
    crypto ai calculates a score & a threshold for each cracked crypto
    if score > crypto, it activates the crypto
    will multiply crypto activation threshold. larger
    ```

- **CRYPTO_ACTIVATE_NUM_DAYS_DROP_OFF**
  - Default: 0.4
  - Developer comment: longer decrypted crypto waits, lower threshold it will have. threshold will be multiplied by this value at most

- **CRYPTO_ACTIVATE_NUM_DAYS_DECAY**
  - Default: 60
  - Developer comment: at this number of days, it will decay by %50 of prev define

- **CRYPTO_ACTIVATE_NUM_ACTIVATED_DROP_OFF**
  - Default: 0.6
  - Developer comment: having an already activated cryptos will further multiply threshold, down to this value

- **CRYPTO_ACTIVATION_SCORE_ARMIES_IN_COMBAT_BONUS**
  - Default: 0.2
  - Developer comment: having units in combat will increase the score by this ratio

- **CRYPTO_ACTIVATION_SCORE_OUR_CAPITAL_BONUS**
  - Default: 0.2
  - Developer comment: fronts of our capital get a bonus by this ratio

- **CRYPTO_ACTIVATION_SCORE_ENEMY_CAPITAL_BONUS**
  - Default: 0.2
  - Developer comment: fronts of enemy capital get a bonus by this ratio

- **CRYPTO_AFTER_SCORE_INVASION_FRONT_BONUS**
  - Default: 1.0
  - Developer comment: a front that is naval invading will increase the score by this ratio

- **MAX_MODULAR_EQUIPMENT_EQUIPMENT_UPGRADE_COUNT_PER_PASS**
  - Default: 4
  - Developer comment:
    ```text
    ~crypto ai
    the maximum number of level AI will try to add to an equipment upgrade of an equipment defined in common/ai_equipment in one pass
    ```

- **EQUIPMENT_UPGRADE_VARIANT_MATCH_SCORE_FACTOR**
  - Default: 0.2
  - Developer comment: the weight of equipment upgrade level when computing the match score of a variant to an ai equipment design.

- **AI_UPDATE_ROLES_FREQUENCY_HOURS**
  - Default: 48
  - Developer comment: Update the roles for a country AI this often (affects performance)

- **UPDATE_SUPPLY_BOTTLENECKS_FREQUENCY_HOURS**
  - Default: 168
  - Developer comment: Check for and try to fix supply bottlenecks this often. (168 hours = 1 week)

- **FIX_SUPPLY_BOTTLENECK_SATURATION_THRESHOLD**
  - Default: 0.85
  - Developer comment: Try to fix supply bottlenecks if supply node saturation exceeds this value.

- **UPDATE_SUPPLY_MOTORIZATION_FREQUENCY_HOURS**
  - Default: 52
  - Developer comment: Check if activating motorization would improve supply situation this often.

- **AI_PREFERRED_TACTIC_WEEKLY_CHANGE_CHANCE**
  - Default: 0.05
  - Developer comment: Chance for AI to select a new preferred tactic if they don't have one selected

- **ARMY_LEADER_ASSIGN_FIELD_MARSHAL_TO_ARMY**
  - Default: -500
  - Developer comment:
    ```text
    <start> assigning leaders to armies
    Score for assigning a field marshal to a normal army (want to use them for army groups)
    ```

- **ARMY_LEADER_ASSIGN_KEEP_LEADER**
  - Default: 500
  - Developer comment: Score for keeping the leader if already assigned

- **ARMY_LEADER_ASSIGN_EMPTYNESS_MALUS**
  - Default: 0.2
  - Developer comment: Factor for avoiding assigning leaders that can lead large armies to small armies (a value of 0.2 reduces the score by max 20 %)

- **ARMY_LEADER_ASSIGN_OVERCAPACITY**
  - Default: -200
  - Developer comment: Score for assigning leader to a too large army

- **ARMY_LEADER_ASSIGN_OVERALL_SKILL_FACTOR**
  - Default: 50
  - Developer comment: This times general's overall skill is added to score

- **ARMY_LEADER_ASSIGN_DEFENSE_OVERALL_SKILL_FACTOR**
  - Default: 10
  - Developer comment: If defensive army, this times general's overall skill is added to score

- **ARMY_LEADER_ASSIGN_DEFENSE_ATTACK_SKILL_FACTOR**
  - Default: 3
  - Developer comment: If defensive army, this times general's attack skill is added to score

- **ARMY_LEADER_ASSIGN_DEFENSE_DEFENSE_SKILL_FACTOR**
  - Default: 20
  - Developer comment: If defensive army, this times general's defense skill is added to score

- **ARMY_LEADER_ASSIGN_DEFENSE_LOGISTICS_SKILL_FACTOR**
  - Default: 3
  - Developer comment: If defensive army, this times general's logistics skill is added to score

- **ARMY_LEADER_ASSIGN_DEFENSE_PLANNING_SKILL_FACTOR**
  - Default: 3
  - Developer comment: If defensive army, this times general's planning skill is added to score

- **ARMY_LEADER_ASSIGN_INVASION_ATTACK_SKILL_FACTOR**
  - Default: 10
  - Developer comment: If invasion army, this times general's attack skill is added to score

- **ARMY_LEADER_ASSIGN_INVASION_DEFENSE_SKILL_FACTOR**
  - Default: 10
  - Developer comment: If invasion army, this times general's defense skill is added to score

- **ARMY_LEADER_ASSIGN_INVASION_LOGISTICS_SKILL_FACTOR**
  - Default: 20
  - Developer comment: If invasion army, this times general's logistics skill is added to score

- **ARMY_LEADER_ASSIGN_INVASION_PLANNING_SKILL_FACTOR**
  - Default: 20
  - Developer comment: If invasion army, this times general's planning skill is added to score

- **ARMY_LEADER_ASSIGN_ATTACK_SKILL_FACTOR**
  - Default: 20
  - Developer comment: This times general's attack skill is added to score

- **ARMY_LEADER_ASSIGN_DEFENSE_SKILL_FACTOR**
  - Default: 10
  - Developer comment: This times general's defense skill is added to score

- **ARMY_LEADER_ASSIGN_LOGISTICS_SKILL_FACTOR**
  - Default: 7
  - Developer comment: This times general's logistics skill is added to score

- **ARMY_LEADER_ASSIGN_PLANNING_SKILL_FACTOR**
  - Default: 7
  - Developer comment: This times general's planning skill is added to score

- **ARMY_LEADER_ASSIGN_NR_TRAITS**
  - Default: 5
  - Developer comment: This times general's nr of active traits is added to score

- **ARMY_LEADER_ASSIGN_EXILED_LEADS_EXILED_TROOPS**
  - Default: 10
  - Developer comment: If exiled leader, increase chance of leading army with exiled troops

- **ARMY_LEADER_ASSIGN_EXILED_LEADS_OWN_EXILED_TROOPS**
  - Default: 100
  - Developer comment: If exiled leader, increase chance of leading army with exiled troops from same country as the leader

- **ARMY_LEADER_ASSIGN_DEFENSE_MAX_DIG_IN_FACTOR**
  - Default: 1.0
  - Developer comment:
    ```text
    the following defines concern the general's modifiers
    If defensive army, importance of general's MAX_DIG_IN_FACTOR modifier
    ```

- **ARMY_LEADER_ASSIGN_DEFENSE_ARMY_ARMOR_DEFENCE_FACTOR**
  - Default: 1.0
  - Developer comment: If defensive army, importance of general's ARMY_ARMOR_DEFENCE_FACTOR modifier (proportional to armor ratio in the army)

- **ARMY_LEADER_ASSIGN_PLANNING_SPEED**
  - Default: 0.1
  - Developer comment: Importance of general's PLANNING_SPEED modifier

- **ARMY_LEADER_ASSIGN_MAX_PLANNING**
  - Default: 0.1
  - Developer comment: Importance of general's MAX_PLANNING modifier

- **ARMY_LEADER_ASSIGN_RECON_FACTOR**
  - Default: 2.0
  - Developer comment: Importance of general's RECON_FACTOR modifier

- **ARMY_LEADER_ASSIGN_OUT_OF_SUPPLY_FACTOR**
  - Default: 1.0
  - Developer comment: Importance of general's OUT_OF_SUPPLY_FACTOR modifier

- **ARMY_LEADER_ASSIGN_WINTER_ATTRITION_FACTOR**
  - Default: 1.0
  - Developer comment: Importance of general's WINTER_ATTRITION_FACTOR modifier

- **ARMY_LEADER_ASSIGN_ARMY_ARMOR_SPEED_FACTOR**
  - Default: 20.0
  - Developer comment: Importance of general's ARMY_ARMOR_SPEED_FACTOR modifier (proportional to armor ratio in the army)

- **ARMY_LEADER_ASSIGN_ARMY_ARMOR_ATTACK_FACTOR**
  - Default: 20.0
  - Developer comment: Importance of general's ARMY_ARMOR_ATTACK_FACTOR modifier (proportional to armor ratio in the army)

- **ARMY_LEADER_ASSIGN_BOOST_ARMOR_SKILL**
  - Default: 20.0
  - Developer comment: Importance of general's trait where armor skill is boosted, e.g. armor_officer which boosts panzer_leader (proportional to armor ratio in the army)

- **ARMY_LEADER_ASSIGN_ARMOR_LEADER_IF_NO_ARMOR**
  - Default: -0.5
  - Developer comment: Avoid assigning a general with armor skills to an army with no armor (can be negative)

- **ARMY_LEADER_ASSIGN_AMPHIBIOUS_INVASION**
  - Default: 1.0
  - Developer comment: If involved in invasion, importance of general's AMPHIBIOUS_INVASION modifier

- **ARMY_LEADER_ASSIGN_NAVAL_INVASION_PREPARATION**
  - Default: 1.0
  - Developer comment: If involved in invasion, importance of general's NAVAL_INVASION_PREPARATION modifier

- **ARMY_LEADER_ASSIGN_XP_GAIN_FACTOR**
  - Default: 2.0
  - Developer comment: Importance of general's XP_GAIN_FACTOR modifier

- **ARMY_LEADER_ASSIGN_SUPPLY_CONSUMPTION_FACTOR**
  - Default: 1.0
  - Developer comment: Importance of general's SUPPLY_CONSUMPTION_FACTOR modifier

- **ARMY_LEADER_ASSIGN_LAND_REINFORCE_RATE**
  - Default: 1.0
  - Developer comment: Importance of general's LAND_REINFORCE_RATE modifier

- **ARMY_LEADER_ASSIGN_ARMY_MORALE_FACTOR**
  - Default: 1.0
  - Developer comment: Importance of general's ARMY_MORALE_FACTOR modifier

- **ARMY_LEADER_ASSIGN_TERRAIN_FACTOR**
  - Default: 0.2
  - Developer comment: Importance of general's terrain skills

- **AREA_DEFENSE_SETTING_VP**
  - Default: false
  - Developer comment:
    ```text
    <end> assigning leaders to armies
    Which settings will AI use for area defense by default
    ```

- **AREA_DEFENSE_SETTING_PORTS**
  - Default: true

- **AREA_DEFENSE_SETTING_AIRBASES**
  - Default: false

- **AREA_DEFENSE_SETTING_FORTS**
  - Default: false

- **AREA_DEFENSE_SETTING_COASTLINES**
  - Default: true

- **AREA_DEFENSE_SETTING_RAILWAYS**
  - Default: false

- **AREA_DEFENSE_MINCAP_MAX_CAPITAL_DEFENSE**
  - Default: 100
  - Developer comment: MaxUnits for capital defense is at least this. (basically use capital defense as a buffer if we have "too many units")

- **AREA_DEFENSE_MINCAP_DESIRED_CAPITAL_DEFENSE**
  - Default: 5
  - Developer comment: DesiredUnits for capital defense is at least this.

- **AREA_DEFENSE_MINCAP_MAX_HOME_AREA**
  - Default: 10
  - Developer comment: MaxUnits for home area is at least this.

- **AREA_DEFENSE_MINCAP_DESIRED_HOME_AREA**
  - Default: 3
  - Developer comment: DesiredUnits for home area is at least this.

- **COMMAND_POWER_BEFORE_SPEND_ON_TRAITS**
  - Default: 30.0

- **PEACE_BID_FOLD_TURNS_AGAINST_OTHER_AI**
  - Default: 2
  - Developer comment: Resolve contests against other AIs after this many turns. Don't always contest forever, it yields the same results.

- **PEACE_BID_CONTEST_TIE_BREAKER_CONFERENCE_SCORE**
  - Default: 1.0
  - Developer comment: When resolving contest against other AI, a tie breaker score is calculated and the loser folds. This is how much to weigh relative remaining peace conference score between the countries.

- **PEACE_BID_CONTEST_TIE_BREAKER_INFLUENCE_DISTANCE**
  - Default: 1.0
  - Developer comment: When resolving contest against other AI, a tie breaker score is calculated and the loser folds. This is how much to weigh relative influence distance between the countries.

- **PEACE_BID_CONTEST_TIE_BREAKER_COUNTRY_SCORE**
  - Default: 1.0
  - Developer comment: When resolving contest against other AI, a tie breaker score is calculated and the loser folds. This is how much to weigh relative country score between the countries.

- **PEACE_BID_FOLD_AGAINST_PLAYER_CHANCE**
  - Default: 0.5
  - Developer comment: Likelihood that AI will fold in a bidding contest against human player.

- **PEACE_BID_FOLD_AGAINST_LIBERATE_CONTEST**
  - Default: 1.0
  - Developer comment: Likelihood that the AI will back down against a same-ideology country performing a contesting liberate bid ##Bordergore prevention therapy

- **PEACE_AI_GROUP_PEACE_ACTIONS**
  - Default: true
  - Developer comment: Whether AI should group peace actions or greedily just select the most-desired peace actions

- **PEACE_AI_EVALUATE_FOR_SUBJECTS**
  - Default: true
  - Developer comment: Whether AI should include subjects when evaluating giving states to other winners (may affect performance on new conference turn)

- **PEACE_AI_EVALUATE_FOR_ALLIES**
  - Default: true
  - Developer comment: Whether AI should include allies when evaluating giving states to other winners (may affect performance on new conference turn)

- **PEACE_AI_EVALUATE_FOR_NON_ALLIES**
  - Default: false
  - Developer comment: Whether AI should include non-allies (not in same faction) when evaluating giving states to other winners (may affect performance on new conference turn)

- **PEACE_AI_EVALUATE_OTHER_IF_CORE**
  - Default: true
  - Developer comment: Whether AI should evaluate giving states to other winners if state is their core (may affect performance on new conference turn)

- **PEACE_AI_EVALUATE_OTHER_IF_CLAIM**
  - Default: true
  - Developer comment: Whether AI should evaluate giving states to other winners if they have a claim on the state (may affect performance on new conference turn)

- **PEACE_AI_EVALUATE_OTHER_ALWAYS**
  - Default: false
  - Developer comment: Whether AI should always evaluate giving states to other winners (!!! may heavily affect performance on new conference turn for large peace conferences !!!)

- **DIVISION_SUPPLY_RATIO_TO_MOTORIZE**
  - Default: 0.80
  - Developer comment: If supply ratio is less than this, consider motorizing any applicable nearby supply hub

- **INDUSTRIAL_ORG_TRAIT_UNLOCK_RANDOMNESS**
  - Default: 3
  - Developer comment: AI will pick a random from N top traits when choosing a trait to unlock

- **INDUSTRIAL_ORG_POLICY_CHANGE_RANDOMNESS**
  - Default: 3
  - Developer comment: AI will pick a random from N top policies when choosing a policy to attach to an MIO

- **INDUSTRIAL_ORG_RESEARCH_ASSIGN_RANDOMNESS**
  - Default: 3
  - Developer comment: AI will pick a random from N top MIOs when choosing an MIO to assign to a research

- **INDUSTRIAL_ORG_PRODUCTION_ASSIGN_RANDOMNESS**
  - Default: 3
  - Developer comment: AI will pick a random from N top MIOs when choosing an MIO to assign to a production line

- **INDUSTRIAL_ORG_POLICY_CHANGE_SCALE**
  - Default: 1.0
  - Developer comment: Policy change weight will be scaled by this value

- **INDUSTRIAL_ORG_TRAIT_RANK_FACTOR**
  - Default: 0.80
  - Developer comment: When precomputing weights, traits will affect the final score less the further down the tree they are, by this factor

- **INDUSTRIAL_ORG_RESEARCH_BONUS_FACTOR**
  - Default: 1.0
  - Developer comment: Research bonus will be multiplied by this factor when evaluating design teams

- **AI_WANTED_LAND_BASED_PLANES_FACTOR**
  - Default: 0.50
  - Developer comment: Factor applied to desire for land based planes (total airbase space * define)

- **AI_WANTED_CARRIER_BASED_PLANES_FACTOR**
  - Default: 1.0
  - Developer comment: Factor applied to desire for carrier based planes (total carrier space * define)

## NFocus

- **FOCUS_POINT_DAYS**
  - Default: 7
  - Developer comment: Each point takes a week

- **FOCUS_PROGRESS_PEACE**
  - Default: 1
  - Developer comment: Progress during peace

- **FOCUS_PROGRESS_WAR**
  - Default: 1
  - Developer comment: Progress during war

- **MAX_SAVED_FOCUS_PROGRESS**
  - Default: 10
  - Developer comment: This much progress can be saved while not having a focus selected

## NOperatives

- **AGENCY_CREATION_DAYS**
  - Default: 30
  - Developer comment: Number of days needed to create an intelligence agency

- **AGENCY_UPGRADE_DAYS**
  - Default: 30
  - Developer comment: Number of days needed to upgrade an intelligence agency

- **AGENCY_CREATION_FACTORIES**
  - Default: 5
  - Developer comment: Number of factories used to create an intelligence agency

- **AGENCY_AI_BASE_NUM_FACTORIES**
  - Default: 25.0
  - Developer comment: Used by AI to pace the upgrades. Formula : if( AGENCY_AI_BASE_NUM_FACTORIES <= num_civ_factories - num_upgrades * AGENCY_AI_PER_UPGRADE_FACTORIES )

- **AGENCY_AI_PER_UPGRADE_FACTORIES**
  - Default: 6.0
  - Developer comment: Used by AI to pace the upgrades. Formula : if( AGENCY_AI_BASE_NUM_FACTORIES <= num_civ_factories - num_upgrades * AGENCY_AI_PER_UPGRADE_FACTORIES )

- **AGENCY_UPGRADE_PER_OPERATIVE_SLOT**
  - Default: 5
  - Developer comment: Number of upgrade needed to unlock an additional operative slot

- **MAX_OPERATIVE_SLOT_FROM_AGENCY_UPGRADES**
  - Default: 1
  - Developer comment: max operative slots gained from upgrades

- **AGENCY_OPERATIVE_RECRUITMENT_TIME**
  - Default: 30
  - Developer comment: Number of days to wait to have operative to recruit when an operative slot first becomes available

- **BECOME_SPYMASTER_PP_COST**
  - Default: 50
  - Developer comment: Number of political power used to become Spy Master

- **BECOME_SPYMASTER_MIN_UPGRADES**
  - Default: 3
  - Developer comment: Number of agency upgrades you need before becoming Spy Master

- **BASE_COUNTER_INTELLIGENCE_RATING**
  - Default: 0.0
  - Developer comment: Base national counter intelligence rating for all countries

- **AGENCY_DEFENSE_EFFECT_ON_HOSTILE_ACTION_COST**
  - Default: 0.2
  - Developer comment: Defense factor that is responsible for multiplying the cost hostile actions against our country by its level and this value

- **INTEL_NETWORK_GAIN_RATE_ON_WRONG_CONTROLLER**
  - Default: -10.0
  - Developer comment: Amount of network strength lost in a state when it does not have the right controller anymore

- **INTEL_NETWORK_GAIN_RATE_ON_OUT_OF_RANGE**
  - Default: -1.75
  - Developer comment: Amount of network strength lost in a state that has the right controller but is out of range of any operative

- **INTEL_NETWORK_GAIN_FROM_ADJACENCY_FACTOR**
  - Default: 0.5
  - Developer comment: Factor multiplied to the sum of the positive difference between a state's strength and its neighbors'. In other words, how strongly neighbors impact the strength gained in a state. Values greater or equal to 1 are discouraged.

- **INTEL_NETWORK_GAIN_DECAY_PER_STEP_FACTOR**
  - Default: 0.5
  - Developer comment: Factor multiplied to the gain of the previous node in the netowrk initially contributed by the agent. In other words, before adjacency, the strength gain in a state would be GainFromOperative * ( INTEL_NETWORK_GAIN_DECAY_PER_STEP_FACTOR ^ NodeDepth ) where NodeDepth is the distance between the state and the operative's location.

- **INTEL_NETWORK_STRENGTH_TARGET_OFFSET_PER_OPERATIVE**
  - Default: 15.0
  - Developer comment: The amount of strength each operative on build intel network mission in a sub network add to the base target network strength

- **INTEL_NETWORK_STRENGTH_DECAY_WHEN_ABOVE_TARGET**
  - Default: -2.5
  - Developer comment: The amount of strength removed each tick from a state that has more strength than the target

- **INTEL_NETWORK_BASE_STRENGTH_TARGET_COUNTERINTELLIGENCE_FACTOR**
  - Default: -10.0
  - Developer comment: BaseStrengthTarget = Factor * CounterIntelligenceRating + Offset

- **INTEL_NETWORK_BASE_STRENGTH_TARGET_COUNTERINTELLIGENCE_OFFSET**
  - Default: 90
  - Developer comment: Offset mentioned above

- **INTEL_NETWORK_MIN_VP_TO_TARGET**
  - Default: 15
  - Developer comment: The minimum value of the highest VP in a state to consider the state as a valid target to start building an intel network

- **INTEL_NETWORK_MIN_STRENGTH_TO_TARGET**
  - Default: 101.0
  - Developer comment: The minimum value of the intel network in a state to consider it a valid target to deploy an operative in

- **INTEL_NETWORK_MIN_STRENGTH_TO_LINK_SUBNETWORKS**
  - Default: 0.0
  - Developer comment: Where the influence of two operative meet, the two nodes on each side have to have strictly more than the given strength before the two operatives have a chance of being considered in the same network

- **INTEL_NETWORK_OPERATIVE_GAIN_STACKING_FACTOR**
  - Default: 0.5
  - Developer comment:
    ```text
    When multiple operative are present in the same location, this factor is applied for each operative with a lower gain than the max. So if operatives have the gain [ 3, 1, 2 ] in the same location, it is sorted to [ 1, 2, 3 ] then converted to [ 1*D^2, 2*D^1, 3 ], with D being this define, so if D=0.5 we have [ 0.25, 1, 3 ] and the final gain from operative at this location will be 4.25. Putting this define to 0 is equivalent to considering the maximum value only.
    ```

- **INTEL_NETWORK_MIN_STRENGTH_FOR_STATE_TO_COUNT_TOWARD_NATIONAL_COVERAGE**
  - Default: 0.0
  - Developer comment: Amount of strength (0, 100) in a state required for it to count toward the national coverage

- **INTEL_NETWORK_NATIONAL_COVERAGE_CONTROLLED_STATES_WEIGHT**
  - Default: 0.2
  - Developer comment: Weight (expected [0,1]) multiplied by the number of states covered by the network that are controlled by the target over the total number of states the target controls

- **INTEL_NETWORK_NATIONAL_COVERAGE_CORE_STATES_WEIGHT**
  - Default: 0.6
  - Developer comment: Weight (expected [0,1]) multiplied by the number of states covered by the network that are core to the target over the total number of states the target has for core

- **INTEL_NETWORK_NATIONAL_COVERAGE_OWNED_WORTH_WEIGHT**
  - Default: 0.2
  - Developer comment: Weight (expected [0,1]) multiplied by the value of victory points covered by the network over the total value of victory points controlled by the targets

- **INTEL_NETWORK_OCCUPIED_TAG_STATES_WEIGHT**
  - Default: 0.5
  - Developer comment: Weight (expected [0,1]) multiplied to the fraction of number of state covered by the intel network divided by the number of states occupied by the target of the network, per occupied tag

- **INTEL_NETWORK_OCCUPIED_TAG_WORTH_WEIGHT**
  - Default: 0.5
  - Developer comment: Weight (expected [0,1]) multiplied to the fraction of victory points worth of states covered by the intel network divided by the worth of states occupied by the target of the network, per occupied tag

- **INTEL_NETWORK_MIN_SUB_NETWORK_SIZE_FOR_DETECTION**
  - Default: 0
  - Developer comment: minimum number of state of a sub-intel network before an operative on build intel network mission in this network can be detected

- **INTEL_NETWORK_MIN_NATIONAL_COVERAGE_FOR_DETECTION**
  - Default: 0.02
  - Developer comment: [0, 1] minimum national coverage required for an operative on build intel network to have a chance to be discovered

- **INTEL_NETWORK_MIN_SUB_NETWORK_NATIONAL_COVERAGE_FOR_DETECTION**
  - Default: 0.01
  - Developer comment: [0, 1] minimum national coverage of the network the operative on build intel network is in to have a chance to be discovered

- **INTEL_NETWORK_MIN_SUB_NETWORK_STRENGTH_FOR_DETECTION**
  - Default: 10.0
  - Developer comment: [0, 100] minimum network strength of the network the operative on build intel network mission is in to have a chance to be discovered

- **INTEL_NETWORK_INTELLIGENCE_AGENCY_DEFENSE_TO_DETECTION_FACTOR**
  - Default: 2.0
  - Developer comment: multiplied to the intelligence agency defense of the target of the intel network

- **INTEL_NETWORK_INTELLIGENCE_AGENCY_DEFENSE_DETECTION_SCALE_FACTOR**
  - Default: 0.0
  - Developer comment: factor multiplied to the intelligence agency defense of the target of the intel network before being factored to the detection chance

- **INTEL_NETWORK_MAX_INTELLIGENCE_AGENCY_DEFENSE_DETECTION_SCALE_FACTOR**
  - Default: 1.0
  - Developer comment: clamp the value from the multiplication of the above factor (expect a value greater or equal to 1)

- **INTEL_NETWORK_NATIONAL_COVERAGE_TO_DETECTION_CHANCE_FACTOR**
  - Default: 1.0
  - Developer comment: multiplied to the national coverage (a value in range [0, 1]

- **INTEL_NETWORK_SUB_NETWORK_STRENGTH_TO_DETECTION_CHANCE_FACTOR**
  - Default: 0.1
  - Developer comment: multiplied to the network strength (a value in range [0, 100]

- **INTEL_NETWORK_SUB_NETWORK_NATIONAL_COVERAGE_TO_DETECTION_CHANCE_FACTOR**
  - Default: 3.0
  - Developer comment: multiplied to the contribution to the national coverage of the sub network (a value in range [0, 1])

- **INTEL_NETWORK_DETECTION_GLOBAL_FACTOR**
  - Default: 0.01
  - Developer comment: global factor multiplied to the detection chance before it is multiplied a dice roll in the range [0,1000)

- **BUILD_INTEL_NETWORK_DAILY_XP_GAIN**
  - Default: 1

- **QUIET_INTEL_NETWORK_DAILY_XP_GAIN**
  - Default: 0

- **OPERATIVE_MISSION_DETECTION_CHANCE_FACTOR**
  - Default: { 0.0, 1.0, 1.0, 1.0, 0.0, 3.0, 0.1, 0.1, 3.0 }
  - Developer comment:
    ```text
    Factor multiplied to the detection chance of an agent on mission before the offsets
    NoMission
    BuildIntelNetwork
    QuietIntelNetwork
    CounterIntelligence
    RootOutResistance
    BoostIdeology
    ControlTrade
    DiplomaticPressure
    Propaganda
    ```

- **OPERATIVE_SLOTS_FROM_FACTION_MEMBERS_FOR_SPY_MASTER**
  - Default: { 0.0, 0.0, 0.25, 10.0, 0.5, 50.0 }
  - Developer comment:
    ```text
    used for calculating how many operatives will a spy master gain from its faction members
    first number in every now is number of operatives gained
    second number is total factory needed (mil and civ) for giving previous ratio
    0 operative for [0, 10)
    0.25 operative for [10, 50)
    0.5 operative for >= 50
    ```

- **INTEL_NETWORK_STATE_MODIFIER_STRENGTH_THRESHOLD**
  - Default: 10
  - Developer comment: Minimum amount of strength required in a state for the intel network related modifiers to start being applied

- **INTEL_NETWORK_MIN_DEFAULT_FOR_SHOWING**
  - Default: 25
  - Developer comment: default min level for networks used to filter operation requirements if not overriden

- **OPERATIVE_BASE_INTEL_NETWORK_GAIN**
  - Default: 0.4
  - Developer comment: Base amount of network strength gain per day provided by an operative

- **OPERATIVE_MAX_INTEL_NETWORK_GAIN**
  - Default: -1.0
  - Developer comment: Max amount of network strength gain per day provided by an operative after modifiers have been applied (negative value means no max)

- **COUNTER_INTELLIGENCE_FOREIGN_AGENT_FACTOR**
  - Default: 0.0
  - Developer comment: Multiplier to the counter intelligence provided by foreign (ally) operatives

- **COUNTER_INTELLIGENCE_STACKING_FACTOR**
  - Default: 0.5
  - Developer comment: Multiplier applied to each operative after the first one. So if we have the following counter intelligence rating values [ 0.1, 0.3, 0.2 ], the factor is applied twice for the lowest value and once for the 2nd lowest one as such : [ 0.3, 0.2 * D, 0.1 * D * D ] and then the result is summed up to give the final rating value

- **COUNTER_INTELLIGENCE_TO_DEFENSE_LOG_FACTOR**
  - Default: 0.0
  - Developer comment: Defense = LogFactor * log( 1 + CounterIntelligence ) + CounterIntelligence / Divisor

- **COUNTER_INTELLIGENCE_TO_DEFENSE_DIVISOR**
  - Default: 1.0
  - Developer comment: see above

- **COUNTER_INTELLIGENCE_DAILY_XP_GAIN**
  - Default: 0.112

- **BOOST_IDEOLOGY_NATIONAL_COVERAGE_FACTOR**
  - Default: 1.0
  - Developer comment: used to compute the drift factor as follow: BASE * SUB_NETWORK_NC * BOOST_IDEOLOGY_DEFENSE_FACTOR

- **BOOST_IDEOLOGY_MAX_DRIFT_BY_OPERATIVE**
  - Default: 0.25
  - Developer comment: the maximum drift an operative can cause, a negative value means no maximum

- **BOOST_IDEOLOGY_DRIFT_STACKING_FACTOR**
  - Default: 0.5
  - Developer comment: multiplied to the drift of an operative for each operative after the first one, with the greatest drift. So if we have the following drift values [ 0.1, 0.3, 0.2 ], the factor is applied twice for the lowest value and once for the 2nd lowest one as such : [ 0.3, 0.2 * D, 0.1 * D * D ] and then the result is summed up to give the final drift value.

- **BOOST_IDEOLOGY_DEFENSE_FACTOR**
  - Default: 0.2
  - Developer comment: multiplied to the target's defense to get the amount of drift to remove from each operative's drift

- **BOOST_IDEOLOGY_DAILY_XP_GAIN**
  - Default: 0.274

- **OPERATIVE_BASE_INTEL_AGENCY_DEFENSE**
  - Default: 1.0
  - Developer comment: Base amount of intel agency defense contributed by an operative on counter_intelligence mission

- **OPERATIVE_BASE_BOOST_IDEOLOGY**
  - Default: 0.1
  - Developer comment: Base amount of daily ideology drift provoked by an operative

- **OPERATIVE_BASE_PROPAGANDA_POWER**
  - Default: 0.0005
  - Developer comment: Base amount of daily war support and stability change when an operative is assigned to propaganda

- **PROPAGANDA_SUB_NETWORK_STRENGTH_FACTOR**
  - Default: 1.0
  - Developer comment: Multiplied to the network strength before being multiplied to the Stability/WarSupport drift caused by an operative

- **PROPAGANDA_DEFENSE_FACTOR**
  - Default: 0.01
  - Developer comment: Multiplied to the target's defense before being subtracted from the Stability/WarSupport drift caused by an operative

- **PROPAGANDA_OPERATIVE_STACKING_FACTOR**
  - Default: 0.5
  - Developer comment: Multiplied to the Stability/WarSupport drift values of each operative after the one with the greatest values. The process is done separatly for Stability and WarSupport

- **PROPAGANDA_COUNTRY_STACKING_FACTOR**
  - Default: 0.5
  - Developer comment: Multiplied to the Stability/WarSupport drift values of each country after the one with the greatest values. The process is done separatly for Stability and WarSupport

- **PROPAGANDA_DAILY_XP_GAIN**
  - Default: 0.350

- **OPERATIVE_BASE_ROOT_OUT_RESISTANCE_EFFICIENCY**
  - Default: 1.0
  - Developer comment: The base efficiency of an operative at the RootOutResistance mission (this is a percentage, 1.0 == 100%)

- **ROOT_OUT_RESISTANCE_STACKING_FACTOR**
  - Default: 0.5
  - Developer comment: Multiplied to each operative efficiency after the first one

- **ROOT_OUT_RESISTANCE_RANGE_STEP_FACTOR**
  - Default: 0.5
  - Developer comment: Multiplied to the summed up efficiency from all operative operating in a same state to determine the efficiency in neighboring states

- **ROOT_OUT_RESISTANCE_DAILY_XP_GAIN**
  - Default: 0.068

- **OPERATIVE_BASE_CONTROL_TRADE_DRIFT**
  - Default: 0.5
  - Developer comment: The base daily drift in trade influence caused by an operative

- **CONTROL_TRADE_STACKING_FACTOR**
  - Default: 0.5
  - Developer comment: Multiplied to the drift of each operative after the first one

- **CONTROL_TRADE_MAX_INFLUENCE**
  - Default: 50.0
  - Developer comment: The maximum amount of trade influence that can be gained through the control trade mission

- **CONTROL_TRADE_INFLUENCE_DAILY_DECAY**
  - Default: 0.1
  - Developer comment: The amount of trade influence lost when no operative are assigned to the mission

- **CONTROL_TRADE_DAILY_XP_GAIN**
  - Default: 0.137

- **OPERATIVE_BASE_DIPLOMATIC_PRESSURE_AI_ACCEPTANCE_SCORE_DRIFT**
  - Default: 0.4
  - Developer comment: The daily change in the amount of opinion requiered to join a faction

- **OPERATIVE_BASE_DIPLOMATIC_PRESSURE_TENSION_REQUIREMENTS_DRIFT**
  - Default: 0.001
  - Developer comment: The daily change in world tension requiered to join a faction

- **DIPLOMATIC_PRESSURE_MAX_AI_ACCEPTANCE_SCORE_INCREASE**
  - Default: 20.0
  - Developer comment: the maximum amount of ai acceptance score from diplomatic pressure

- **DIPLOMATIC_PRESSURE_MAX_TENSION_REQUIREMENTS_DECREASE**
  - Default: 0.20
  - Developer comment: amount of tension (tensions is in range [0,1]) that can be removed from the requirements imposed by the modifier join_faction_tension_limit

- **DIPLOMATIC_PRESSURE_OPERATIVE_STACKING_FACTOR**
  - Default: 0.5
  - Developer comment: The diminishing return factor to apply to operative working for the same faction after the first one. Operatives operating for a same faction are ranked by their efficiency and their opinion and tension drift are individually applyied a stacking factor like so: DRIFT * STACKING_FACTOR^RANK where RANK is a value from 0 to the number of operative -1 where the opperative with the highest drift value has rank 0

- **DIPLOMATIC_PRESSURE_AI_ACCEPTANCE_SCORE_DECAY**
  - Default: 0.4
  - Developer comment: daily decay when the mission is not active

- **DIPLOMATIC_PRESSURE_TENSION_REQUIREMENTS_DECAY**
  - Default: 0.001

- **DIPLOMATIC_PRESSURE_DAILY_XP_GAIN**
  - Default: 0.137

- **MIN_NATIONAL_COVERAGE_FOR_BOOST_IDEOLOGY**
  - Default: 0.01
  - Developer comment: Minimum network coverage required to start the mission (the code ensures that a network exists at all)

- **MIN_NATIONAL_COVERAGE_FOR_PROPAGANDA**
  - Default: 0.01
  - Developer comment: Minimum network coverage required to start the mission (the code ensures that a network exists at all)

- **OPERATIVE_MIN_DAYS_HARMED**
  - Default: 30
  - Developer comment: Minimum number of days an operative can be harmed. Applied after modifiers. Can be zero.

- **OPERATIVE_MAX_DAYS_HARMED**
  - Default: 120
  - Developer comment: Maximum number of days an operative can be harmed. Applied after modifiers. Is ignored if negative

- **OPERATIVE_MIN_DAYS_FORCED_INTO_HIDING**
  - Default: 7
  - Developer comment: Minimum number of days an operative can be forced into hiding. Applied after modifiers. Can be zero.

- **OPERATIVE_MAX_DAYS_FORCED_INTO_HIDING**
  - Default: 120
  - Developer comment: Maximum number of days an operative can be forced into hiding. Applied after modifiers. Is ignored if negative

- **OPERATIVE_MAX_DAYS_TO_AUTO_RESUME_MISSION**
  - Default: 30
  - Developer comment: Maximum number of days an operative has to be disabled before its mission is not automatically resumed once he is available again

- **MAX_RECRUITED_OPERATIVES**
  - Default: 10

- **CRYPTO_BASE_CRYPTO_LEVEL**
  - Default: 12000
  - Developer comment: base crypto strength for a country

- **CRYPTO_CRYPTO_LEVEL_PER_CRYPTO_UPGRADE**
  - Default: 4250
  - Developer comment: crypto strength per crypto upgrade

- **CRYPTO_CRYPTO_ACTIVE_BONUS_DURATION**
  - Default: 30
  - Developer comment: number of days the active decryption bonuses will be applied before enemy resets their intelligence

- **CYRPTO_ACTIVE_BONUS_ACTIVATION_PROGRESS_RATIO**
  - Default: 0.5
  - Developer comment: once bonus is activated, decryption progress will be reduced to this ratio

- **OPERATION_AI_MINIMUM_SCORE**
  - Default: 10.0
  - Developer comment: Once an operation's AI weight falls below the minimum score it will be scrapped if it is being prepared

- **OPERATION_COMPLETION_XP**
  - Default: 18

- **OPERATIVE_CAPTURE_DURATION_IN_DAYS**
  - Default: 9*30

- **DEFAULT_OPERATION_COST_MULTIPLIER**
  - Default: 0.15
  - Developer comment:
    ```text
    operation cost & time are increased by default this ratios for each
    instance of operation that were already executed against same target.
    can be overridden using time_multiplier & cost_multiplier in operation.
    ```

- **DEFAULT_OPERATION_TIME_MULTIPLIER**
  - Default: 0.0

- **BUILD_INTEL_NETWORK_MISSION_ACTIVITY_INDICATOR_FACTOR**
  - Default: 10
  - Developer comment: The following defines are multiplied to the number of operatives operating in the target country the activity level is computed for

- **BOOST_IDEOLOGY_NETWORK_MISSION_ACTIVITY_INDICATOR_FACTOR**
  - Default: 10

- **PROPAGANDA_NETWORK_MISSION_ACTIVITY_INDICATOR_FACTOR**
  - Default: 10

- **CONTROL_TRADE_NETWORK_MISSION_ACTIVITY_INDICATOR_FACTOR**
  - Default: 1

- **DIPLOMATIC_PRESSURE_NETWORK_MISSION_ACTIVITY_INDICATOR_FACTOR**
  - Default: 1

- **INTEL_NETWORK_COVERAGE_ACTIVITY_FACTOR**
  - Default: 100
  - Developer comment: multiplied to the sum of the network coverage [0,1] all countries have over the target

- **INTEL_NETWORK_STRENGTH_DANGER_FACTOR**
  - Default: 1
  - Developer comment: multiplied to the strength [0,100] of the strongest network over that country

- **ACTIVITY_LEVEL_PROPORTIONAL_FACTOR**
  - Default: 0.01
  - Developer comment: Activity level PID values

- **ACTIVITY_LEVEL_INTEGRAL_FACTOR**
  - Default: 0.001

- **ACTIVITY_LEVEL_DERIVATIVE_FACTOR**
  - Default: 0

- **DANGER_LEVEL_PROPORTIONAL_FACTOR**
  - Default: 0.01
  - Developer comment: Danger level PID values

- **DANGER_LEVEL_INTEGRAL_FACTOR**
  - Default: 0.001

- **DANGER_LEVEL_DERIVATIVE_FACTOR**
  - Default: 0

- **NUM_DAYS_BEFORE_REMOVING_PREPARED_OPERATIONS**
  - Default: 60
  - Developer comment: num days before removing prepared operations

- **ON_CAPTURE_COUNTERINTELLIGENCE_OPERATIVE_XP_GAIN**
  - Default: 100
  - Developer comment: Xp gain when an enemy operative is captured in the country the operative is assigned to counter intelligence to. Apply to a single randomly selected operative

- **ON_CAPTURE_COUNTERINTELLIGENCE_OPERATIVE_WEIGHT_OWN_COUNTRY_FOR_XP**
  - Default: 2
  - Developer comment: An integer on how likely an operative operating in his own country is to get selected for the xp reward on enemy operative capture

- **ON_CAPTURE_COUNTERINTELLIGENCE_OPERATIVE_WEIGHT_DIFFERENT_COUNTRY_FOR_XP**
  - Default: 1
  - Developer comment: same for an operative assigned to counter intelligence in a different country than his own

- **RISK_LEVELS**
  - Default: { 0.1, 0.2, 0.3 }
  - Developer comment:
    ```text
    risk and outcome texts. each number array should match its labels in size, but its ok to have different amount of risk levels than outcomes
    each risk level comes with a label to display for operations if it goes abve that number. If below the first it will isntead show the good outcomes
    ```

- **RISK_LEVELS_LABELS**
  - Default: { "RISK_LOW", "RISK_MID", "RISK_HIGH" }

- **OUTCOME_LEVELS**
  - Default: { 0.0, 0.2, 0.3 }
  - Developer comment: outcome levels are shown if risk is below its first entry instead

- **OUTCOME_LEVELS_LABELS**
  - Default: { "OUTCOME_BASE", "OUTCOME_GOOD", "OUTCOME_VGOOD" }

- **TECH_STEAL_EQUIPMENT_FACTOR**
  - Default: 4

- **TECH_STEAL_YEAR_FACTOR**
  - Default: 4

## NIntel

- **COUNTRY_LEVEL_INTEL_MAXIMUMS**
  - Default: { 100.0, 100.0, 100.0, 100.0 }
  - Developer comment:
    ```text
    The maximum intel a country can have over another
    Civilian
    Army
    Navy
    Airforce
    ```

- **STATIC_INTEL_SOURCE_OPERATION_TOKENS_MAXIMUMS**
  - Default: {  }
  - Developer comment:
    ```text
    Static sources:
    A static source is a source that will fully decay once its origin disappear.
    (e.g. radar destroyed)
    MAXIMUMS:
    if set to an non-empty arrays, overrides COUNTRY_LEVEL_INTEL_MAXIMUMS
    for this specific source (note that COUNTRY_LEVEL_INTEL_MAXIMUMS is
    applied after INTEL_SOURCE_XXX_MAXIMUMS)
    ```

- **STATIC_INTEL_SOURCE_BROKEN_CYPHER_MAXIMUMS**
  - Default: { 60.0, 60.0, 60.0, 60.0 }

- **STATIC_INTEL_SOURCE_RADAR_MAXIMUMS**
  - Default: { 10.0, 10.0, 20.0, 20.0 }

- **STATIC_INTEL_SOURCE_INTEL_NETWORK_MAXIMUMS**
  - Default: { 30.0, 30.0, 40.0, 30.0 }

- **DYNAMIC_INTEL_SOURCE_EVENT_FLAT_DECAY**
  - Default: 0.0
  - Developer comment:
    ```text
    Dynamic intel pool can be manipulated through the following defines:
    FLAT_DECAY and MULT_DECAY control the rate at which the intel decays
    The formula is applied as follow (runs daily):
    NextIntel = ( Intel - FLAT_DECAY ) * MULT_DECAY
    AGGREGAT_LOG_FACTOR and AGGREGAT_DIVISOR control the rate at which
    intel accumulates. It is applied to the sum of the intel generated
    throughout the day as follow:
    Aggregat = LOG_FACTOR * log( 1 + IntelOfTheDay ) + IntelOfTheDay / DIVISOR
    The Aggregat is then added to the pool of intel.
    If DIVISOR is zero then the division is evaluated to zero.
    MAXIMUMS controls the maximum value that the pool can contribute to
    the final intel values.
    ABSOLUTE_MAXIMUMS defines a ceiling for the intel in the pool that
    will never be exceeded. They are meant to be greater or equal to
    MAXIMUMS. If the array is empty, no absolute maximum is defined.
    Dynamic pool EVENT
    ```

- **DYNAMIC_INTEL_SOURCE_EVENT_MULT_DECAY**
  - Default: 0.985

- **DYNAMIC_INTEL_SOURCE_EVENT_AGGREGAT_LOG_FACTOR**
  - Default: 0

- **DYNAMIC_INTEL_SOURCE_EVENT_AGGREGAT_DIVISOR**
  - Default: 1

- **DYNAMIC_INTEL_SOURCE_EVENT_MAXIMUMS**
  - Default: { 40, 40, 40, 40 }

- **DYNAMIC_INTEL_SOURCE_EVENT_ABSOLUTE_MAXIMUMS**
  - Default: { 50, 50, 50, 50 }

- **DYNAMIC_INTEL_SOURCE_LAND_COMBAT_FLAT_DECAY**
  - Default: 0.0
  - Developer comment: Dynamic pool LAND_COMBAT

- **DYNAMIC_INTEL_SOURCE_LAND_COMBAT_MULT_DECAY**
  - Default: 0.985

- **DYNAMIC_INTEL_SOURCE_LAND_COMBAT_AGGREGAT_LOG_FACTOR**
  - Default: 0.25

- **DYNAMIC_INTEL_SOURCE_LAND_COMBAT_AGGREGAT_DIVISOR**
  - Default: 10

- **DYNAMIC_INTEL_SOURCE_LAND_COMBAT_MAXIMUMS**
  - Default: { 0, 30, 5, 10 }

- **DYNAMIC_INTEL_SOURCE_LAND_COMBAT_ABSOLUTE_MAXIMUMS**
  - Default: { 0, 40, 10, 15 }

- **DYNAMIC_INTEL_SOURCE_NAVAL_COMBAT_FLAT_DECAY**
  - Default: 0.0
  - Developer comment: Dynamic pool NAVAL_COMBAT

- **DYNAMIC_INTEL_SOURCE_NAVAL_COMBAT_MULT_DECAY**
  - Default: 0.985

- **DYNAMIC_INTEL_SOURCE_NAVAL_COMBAT_AGGREGAT_LOG_FACTOR**
  - Default: 0.02

- **DYNAMIC_INTEL_SOURCE_NAVAL_COMBAT_AGGREGAT_DIVISOR**
  - Default: 200

- **DYNAMIC_INTEL_SOURCE_NAVAL_COMBAT_MAXIMUMS**
  - Default: { 10, 0, 40, 20 }

- **DYNAMIC_INTEL_SOURCE_NAVAL_COMBAT_ABSOLUTE_MAXIMUMS**
  - Default: { 15, 0, 45, 25 }

- **DYNAMIC_INTEL_SOURCE_AIR_COMBAT_FLAT_DECAY**
  - Default: 0.0
  - Developer comment: Dynamic pool AIR_COMBAT

- **DYNAMIC_INTEL_SOURCE_AIR_COMBAT_MULT_DECAY**
  - Default: 0.985

- **DYNAMIC_INTEL_SOURCE_AIR_COMBAT_AGGREGAT_LOG_FACTOR**
  - Default: 1

- **DYNAMIC_INTEL_SOURCE_AIR_COMBAT_AGGREGAT_DIVISOR**
  - Default: 2

- **DYNAMIC_INTEL_SOURCE_AIR_COMBAT_MAXIMUMS**
  - Default: { 0, 0, 0, 25 }

- **DYNAMIC_INTEL_SOURCE_AIR_COMBAT_ABSOLUTE_MAXIMUMS**
  - Default: { 0, 0, 0, 30 }

- **DYNAMIC_INTEL_SOURCE_AIR_RECON_FLAT_DECAY**
  - Default: 0.0
  - Developer comment: Dynamic pool AIR_RECON

- **DYNAMIC_INTEL_SOURCE_AIR_RECON_MULT_DECAY**
  - Default: 0.995

- **DYNAMIC_INTEL_SOURCE_AIR_RECON_AGGREGAT_LOG_FACTOR**
  - Default: 0.05

- **DYNAMIC_INTEL_SOURCE_AIR_RECON_AGGREGAT_DIVISOR**
  - Default: 200

- **DYNAMIC_INTEL_SOURCE_AIR_RECON_MAXIMUMS**
  - Default: { 25, 20, 30, 20 }

- **DYNAMIC_INTEL_SOURCE_AIR_RECON_ABSOLUTE_MAXIMUMS**
  - Default: { 30, 25, 35, 25 }

- **DYNAMIC_INTEL_SOURCE_CAPTURED_OPERATIVE_FLAT_DECAY**
  - Default: 0.0
  - Developer comment: Dynamic pool CAPTURED_OPERATIVE

- **DYNAMIC_INTEL_SOURCE_CAPTURED_OPERATIVE_MULT_DECAY**
  - Default: 0.95

- **DYNAMIC_INTEL_SOURCE_CAPTURED_OPERATIVE_AGGREGAT_LOG_FACTOR**
  - Default: 1

- **DYNAMIC_INTEL_SOURCE_CAPTURED_OPERATIVE_AGGREGAT_DIVISOR**
  - Default: 2

- **DYNAMIC_INTEL_SOURCE_CAPTURED_OPERATIVE_MAXIMUMS**
  - Default: { 50, 40, 40, 30 }

- **DYNAMIC_INTEL_SOURCE_CAPTURED_OPERATIVE_ABSOLUTE_MAXIMUMS**
  - Default: { 50, 40, 40, 30 }

- **LAND_COMBAT_ARMY_INTEL_OVER_OPPONENT_PER_INSTANCE**
  - Default: 1.0
  - Developer comment: if the opponent has any division present, flat intel value generated py a participant against an opponent

- **LAND_COMBAT_ARMY_INTEL_OVER_OPPONENT_PER_COMITTED_DIVISIONS**
  - Default: 0.5
  - Developer comment: multiplied to the number of comitted divisions of the opponent

- **LAND_COMBAT_ARMY_INTEL_OVER_OPPONENT_PER_RESERVE_DIVISIONS**
  - Default: 0.1
  - Developer comment: same for divisions in reserve

- **LAND_COMBAT_ARMY_INTEL_OVER_OPPONENT_PER_RETREATING_DIVISIONS**
  - Default: 0.2
  - Developer comment: same for retreating divisions

- **LAND_COMBAT_ARMY_INTEL_FACTOR**
  - Default: 0.01
  - Developer comment: factor applied once all values have been added together

- **LAND_COMBAT_AIR_INTEL_OVER_OPPONENT_PER_INSTANCE**
  - Default: 1.0
  - Developer comment: if the opponent has any plane active in the, flat intel value generated by a participant against that opponent

- **LAND_COMBAT_AIR_INTEL_OVER_OPPONENT_PER_PLANE**
  - Default: 0.1
  - Developer comment: multiplied to the number of plane that opponent has in the combat

- **LAND_COMBAT_AIR_INTEL_FACTOR**
  - Default: 0.01
  - Developer comment: factor applied once all values have been added together

- **RECON_INTEL_BONUS**
  - Default: 0.075
  - Developer comment: each recon gives this bonus to overall gathered land intel in combat

- **NAVAL_COMBAT_NAVY_INTEL_OVER_OPPONENT_PER_INSTANCE**
  - Default: 1.0

- **NAVAL_COMBAT_NAVY_INTEL_OVER_OPPONENT_PER_SUBMARINE**
  - Default: 0.2

- **NAVAL_COMBAT_NAVY_INTEL_OVER_OPPONENT_PER_SCREEN_SHIP**
  - Default: 0.5

- **NAVAL_COMBAT_NAVY_INTEL_OVER_OPPONENT_PER_CAPITAL_SHIP**
  - Default: 1.0

- **NAVAL_COMBAT_NAVY_INTEL_OVER_OPPONENT_PER_INTERNAL_PLANES**
  - Default: 0.05

- **NAVAL_COMBAT_NAVY_INTEL_FACTOR**
  - Default: 1.0

- **NAVAL_COMBAT_CIVILIAN_INTEL_OVER_OPPONENT_PER_INSTANCE**
  - Default: 0.0

- **NAVAL_COMBAT_CIVILIAN_INTEL_OVER_OPPONENT_PER_TRADE_CONVOY**
  - Default: 1.0

- **NAVAL_COMBAT_CIVILIAN_INTEL_FACTOR**
  - Default: 1.0

- **NAVAL_COMBAT_ARMY_INTEL_OVER_OPPONENT_PER_INSTANCE**
  - Default: 0.0

- **NAVAL_COMBAT_ARMY_INTEL_OVER_OPPONENT_PER_TRANSFER_CONVOY**
  - Default: 1.0

- **NAVAL_COMBAT_ARMY_INTEL_FACTOR**
  - Default: 1.0

- **NAVAL_COMBAT_AIR_INTEL_OVER_OPPONENT_PER_INSTANCE**
  - Default: 1.0

- **NAVAL_COMBAT_AIR_INTEL_OVER_OPPONENT_PER_INTERNAL_PLANES**
  - Default: 0.0

- **NAVAL_COMBAT_AIR_INTEL_OVER_OPPONENT_PER_EXTERNAL_PLANES**
  - Default: 0.01

- **NAVAL_COMBAT_AIR_INTEL_FACTOR**
  - Default: 1.0

- **NAVY_INTEL_BASE_SPOTTING_BONUS_MIN_INTEL_FOR_BONUS**
  - Default: 5
  - Developer comment: at least this intel diff is needed for start applying BASE_SPOTTING_FROM_DECRYPTION bonus

- **NAVY_INTEL_BASE_SPOTTING_BONUS_MAX_INTEL_FOR_BONUS**
  - Default: 40
  - Developer comment: at this intel BASE_SPOTTING_FROM_DECRYPTION will be applied fully

- **NAVY_INTEL_MINE_DAMAGE_REDUCTION_FACTOR_MIN_INTEL_FOR_BONUS**
  - Default: 5
  - Developer comment: at least this intel diff is needed for start applying NAVAL_MINES_INTEL_DIFF_FACTOR bonus

- **NAVY_INTEL_MINE_DAMAGE_REDUCTION_FACTOR_MAX_INTEL_FOR_BONUS**
  - Default: 40
  - Developer comment: t this intel NAVAL_MINES_INTEL_DIFF_FACTOR will be applied fully

- **AIR_COMBAT_AIR_INTEL_PER_INSTANCE**
  - Default: 1.0

- **AIR_COMBAT_AIR_INTEL_PER_OPPONENT_PLANE**
  - Default: 0.0

- **AIR_COMBAT_AIR_INTEL_FACTOR**
  - Default: 0.2

- **INTEL_NETWORK_NATIONAL_COVERAGE_FACTOR**
  - Default: 2.0
  - Developer comment: multiplied to the national coverage to deduce the fraction of the maximum value listed below that will be added to the intel against the network's target

- **INTEL_NETWORK_NATIONAL_COVERAGE_NAVAL_BASE_FACTOR**
  - Default: 15.0
  - Developer comment: factor used instead of above in case you dont cover naval bases etc

- **INTEL_NETWORK_MAX_CIVILIAN_INTEL**
  - Default: 20.0
  - Developer comment: the maximum intel values that an intel network will provide against a target

- **INTEL_NETWORK_MAX_ARMY_INTEL**
  - Default: 20.0

- **INTEL_NETWORK_MAX_NAVY_INTEL**
  - Default: 25.0
  - Developer comment: only apply if the network encompass a naval base controlled by the network's target

- **INTEL_NETWORK_MAX_AIRFORCE_INTEL**
  - Default: 15.0

- **RADAR_LEVEL_INTEL_FACTOR**
  - Default: 1.25
  - Developer comment: Multiplied to the radar level to tell the fraction of intel per covered province we get. The radar level is computed as BuildingLevel / MaxBuildingLevel.

- **RADAR_INTEL_STACKING_FACTOR**
  - Default: 0.5
  - Developer comment: Used when multiple radars cover the same province

- **RADAR_BASE_INTEL_VALUES_FOR_COUNTRY_COVERAGE_PERCENTAGE**
  - Default: { 9.0, 9.0, 0.0, 18.0 }
  - Developer comment:
    ```text
    Values are the same order as in COUNTRY_LEVEL_INTEL_MAXIMUMS
    Multiplied by the total radar efficiency over the provinces of
    a specific country divided by the number of provinces controlled
    by that same country.
    ```

- **RADAR_BASE_INTEL_VALUES_FOR_COVERED_LAND_PROVINCES**
  - Default: { 5.0, 5.0, 0.0, 12.0 }
  - Developer comment:
    ```text
    Values are the same order as in COUNTRY_LEVEL_INTEL_MAXIMUMS
    Multiplied by the total radar efficiency of the provinces of
    a specific country divided by the individual radar's
    percentage of covered provinces.
    ```

- **RADAR_BASE_INTEL_VALUES_FOR_COVERED_SEA_PROVINCES**
  - Default: { 0.0, 0.0, 280.0, 0.0 }
  - Developer comment:
    ```text
    Values are the same order as in COUNTRY_LEVEL_INTEL_MAXIMUMS
    Multiplied by the total radar efficiency of the provinces
    covered by the radar for each strategic region that has
    convoy routes and multiplied by the fraction of convoy
    that country has going through the region (excluding the
    convoys of the radar's owner)
    ```

- **RADAR_NAVY_INTEL_FACTOR_PER_SHIP_TYPE**
  - Default: { 5.0, 10.0, 20.0, 30.0 }
  - Developer comment:
    ```text
    Navy intel value factored to the fraction of the country's
    ships in the sea zone covered by the radar, by ship type
    Submarine
    Screen ship
    Capital ship
    Carrier ship
    ```

- **CAPTURED_OPERATIVE_MAX_FACTOR**
  - Default: 35.0
  - Developer comment: Define the maximum of the randomized factor, before the factor from operative is applied

- **CAPTURED_OPERATIVE_MIN_FACTOR**
  - Default: 10.0
  - Developer comment: Define the minimum of the randomized factor, before the factor from operative is applied

- **CAPTURED_OPERATIVE_INTEL_YIELD**
  - Default: { 0.3, 0.3, 0.3, 0.3 }
  - Developer comment:
    ```text
    Values are the same order as in COUNTRY_LEVEL_INTEL_MAXIMUMS
    Daily base intel yield from an operative, before the
    factors defined above are applied
    ```

- **RECON_PLANE_INTEL_BASE**
  - Default: 0.02
  - Developer comment: intel base amount for a strategic area per plane

- **RECON_PLANE_LAND_DISTRIBUTION**
  - Default: { 10.0, 6.0, 0.0, 3.0 }
  - Developer comment: controls for land and sea zones how much of each intel typee is given (civ, army, navy, air)

- **RECON_PLANE_SEA_DISTRIBUTION**
  - Default: { 0.0, 0.0, 10.0, 0.0 }

- **LAND_SPOT_DECAY**
  - Default: 0.05

- **NAVAL_SPOT_DECAY**
  - Default: 1

- **ENCRYPTION_DECRYPTION_INTEL_FACTORS**
  - Default: { 15.0, 15.0, 15.0, 15.0 }
  - Developer comment:
    ```text
    Factored to ( 1 + A.decryption ) / ( 1 + B.encryption ) to determine the intel
    A has over B when legacy encryption and decryption modifier are used.
    Note that if A.decryption is zero, the result is forced to zero
    In the ame order as COUNTRY_LEVEL_INTEL_MAXIMUMS
    ```

- **CIVILIAN_PRODUCTION_RANGE_INTEL_MIN**
  - Default: 0.1
  - Developer comment:
    ```text
    intel ledger defines
    minimum value to show fuzzy factory counts below this you will get ???
    ```

- **CIVILIAN_PRODUCTION_RANGE_INTEL_MAX**
  - Default: 0.5
  - Developer comment: maximum value to show fuzzy factory counts. above this you will get full count

- **CIVILIAN_PRODUCTION_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5
  - Developer comment: range of intel values at lowest intel

- **CIVILIAN_FUEL_RANGE_INTEL_MIN**
  - Default: 0.3
  - Developer comment: minimum value to show fuzzy factory counts below this you will get ???

- **CIVILIAN_FUEL_RANGE_INTEL_MAX**
  - Default: 0.7
  - Developer comment: maximum value to show fuzzy factory counts. above this you will get full count

- **CIVILIAN_FUEL_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5
  - Developer comment: range of intel values at lowest intel

- **CIVILIAN_MANPOWER_RANGE_INTEL_MIN**
  - Default: 0.1
  - Developer comment: minimum value to show fuzzy factory counts below this you will get ???

- **CIVILIAN_MANPOWER_RANGE_INTEL_MAX**
  - Default: 0.7
  - Developer comment: maximum value to show fuzzy factory counts. above this you will get full count

- **CIVILIAN_MANPOWER_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5
  - Developer comment: range of intel values at lowest intel

- **CIVILIAN_CONVOYS_RANGE_INTEL_MIN**
  - Default: 0.1
  - Developer comment: minimum value to show fuzzy factory counts below this you will get ???

- **CIVILIAN_CONVOYS_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5
  - Developer comment: range of intel values at lowest intel

- **CIVILIAN_TRUCKS_RANGE_INTEL_MIN**
  - Default: 0.1
  - Developer comment: minimum value to show fuzzy factory counts below this you will get ???

- **CIVILIAN_TRUCKS_RANGE_INTEL_MAX**
  - Default: 0.5
  - Developer comment: maximum value to show fuzzy factory counts. above this you will get full count

- **CIVILIAN_TRUCKS_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5
  - Developer comment: range of intel values at lowest intel

- **CIVILIAN_TRAINS_RANGE_INTEL_MIN**
  - Default: 0.1
  - Developer comment: minimum value to show fuzzy factory counts below this you will get ???

- **CIVILIAN_TRAINS_RANGE_INTEL_MAX**
  - Default: 0.5
  - Developer comment: maximum value to show fuzzy factory counts. above this you will get full count

- **CIVILIAN_TRAINS_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5
  - Developer comment: range of intel values at lowest intel

- **CIVILIAN_SUPPLY_RANGE_INTEL_MIN**
  - Default: 0.1
  - Developer comment: minimum value to show fuzzy factory counts below this you will get ???

- **CIVILIAN_SUPPLY_RANGE_INTEL_MAX**
  - Default: 0.5
  - Developer comment: maximum value to show fuzzy factory counts. above this you will get full count

- **CIVILIAN_SUPPLY_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5
  - Developer comment: range of intel values at lowest intel

- **CIVILIAN_TRADE_SHOW_TRADE_AMOUNTS**
  - Default: 0.0
  - Developer comment: minimum value to show how much a country trades a resource

- **CIVILIAN_TRADE_SHOW_TRADE_PARTNERS**
  - Default: 0.1
  - Developer comment: minimum value to show who a country trades with

- **CIVILIAN_MIN_INTEL_FOR_RESOURCE_ROUTES_TOOLTIPS**
  - Default: 0.9
  - Developer comment: minimum value to show convoy routes for resource transfer

- **CIVILIAN_MIN_INTEL_FOR_TRADE_ROUTES**
  - Default: 0.7
  - Developer comment: minimum value to show trade routes on map

- **CIVILIAN_MIN_INTEL_FOR_RESOURCE_ORIGIN_ROUTES**
  - Default: 0.5
  - Developer comment: minimum value to show resource transfers to mainland on map

- **ARMY_MIN_INTEL_FOR_SUPPLY_ROUTES**
  - Default: 0.5
  - Developer comment: minimum value to show convoy routes for supply transfer

- **ARMY_MIN_INTEL_FOR_SUPPLY_ROUTES_TOOLTIPS**
  - Default: 0.7
  - Developer comment: minimum value to show convoy route tooltips for supply transfer

- **CIVILIAN_INTEL_NEEDED_TO_SHOW_ANTI_AIR_REDUCTION**
  - Default: 0.3
  - Developer comment: minimum value to show anti air damage reduction

- **CIVILIAN_INTEL_NEEDED_TO_SHOW_FOCUS_TREE**
  - Default: 0.5
  - Developer comment: min required intel to focus tree with taken focuses

- **CIVILIAN_INTEL_NEEDED_TO_SHOW_CURRENT_FOCUS**
  - Default: 0.7
  - Developer comment: min required intel to show currently focus

- **CIVILIAN_INTEL_NEEDED_TO_SHOW_CURRENT_FOCUS_PROGRESS**
  - Default: 0.7
  - Developer comment: min required intel to show current focus progress

- **CIVILIAN_MIN_INTEL_TO_SHOW_INDUSTRY_GRAPH**
  - Default: 0.30

- **CIVILIAN_MIN_INTEL_TO_SHOW_CONVOYS_GRAPH**
  - Default: 0.70

- **CIVILIAN_MIN_INTEL_TO_SHOW_BOMBERS_GRAPH**
  - Default: 0.8

- **CIVILIAN_MIN_INTEL_TO_SHOW_TRUCKS_GRAPH**
  - Default: 0.5

- **CIVILIAN_MIN_INTEL_TO_SHOW_TRAINS_GRAPH**
  - Default: 0.5

- **CIVILIAN_MIN_INTEL_TO_SHOW_RAIL_STAUS**
  - Default: 0.4
  - Developer comment: when mousing over supply map mode, shows damage/construction status

- **OLD_TECH_COUNT_NUM_DAYS**
  - Default: 180
  - Developer comment: num days after researched to consider a tech as "old"

- **INTEL_TO_SHOW_TECH_COUNT**
  - Default: { 0.5, 0.3, 0.3, 0.3 }
  - Developer comment: minimum value to show current tech count and current doctrine

- **INTEL_TO_SHOW_PREVIOUSLY_RESEARCHED**
  - Default: { 0.7, 0.7, 0.7, 0.7 }
  - Developer comment: minimum value to show previously researched tech

- **INTEL_TO_SHOW_CURRENTLY_RESEARCHED**
  - Default: { 0.8, 0.8, 0.8, 0.8 }
  - Developer comment: minimum value to show currently being researched tech

- **INTEL_TO_SHOW_IDEAS**
  - Default: { 0.0, 0.0, 0.0, 0.0 }

- **ARMY_ARMY_COUNT_RANGE_INTEL_MIN**
  - Default: 0.05

- **ARMY_ARMY_COUNT_RANGE_INTEL_MAX**
  - Default: 0.7

- **ARMY_ARMY_COUNT_RANGE_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.8

- **ARMY_SPECIAL_FORCES_COUNT_RANGE_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.7

- **ARMY_DEPLOYED_MANPOWER_COUNT_RANGE_INTEL_MIN**
  - Default: 0.1

- **ARMY_DEPLOYED_MANPOWER_COUNT_RANGE_INTEL_MAX**
  - Default: 0.7

- **ARMY_DEPLOYED_MANPOWER_COUNT_RANGE_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5

- **ARMY_MIN_INTEL_TO_SHOW_EQUIPMENT_RATIO**
  - Default: 0.7

- **ARMY_MIN_INTEL_TO_SHOW_BASIC_TEMPLATE_INFO**
  - Default: 0.3

- **ARMY_TEMPLATE_UNIT_COUNT_INTEL_MIN**
  - Default: 0.5

- **ARMY_TEMPLATE_UNIT_COUNT_INTEL_MAX**
  - Default: 0.7

- **ARMY_TEMPLATE_UNIT_COUNT_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 1.0

- **ARMY_MIN_INTEL_TO_SHOW_EXACT_TEMPLATE_INFO**
  - Default: 0.8

- **ARMY_STOCKPILE_COUNT_INTEL_MIN**
  - Default: 0.3

- **ARMY_STOCKPILE_COUNT_INTEL_MAX**
  - Default: 0.7

- **ARMY_STOCKPILE_COUNT_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5

- **ARMY_MIN_INTEL_TO_SHOW_EQUIPMENT_DESIGN_DETAILS**
  - Default: 0.8

- **ARMY_MIN_INTEL_RATIO_NEEDED_FOR_DISPLAYING_FAKE_ENEMY_INTEL_IN_LEDGER**
  - Default: 0.9

- **ARMY_MIN_INTEL_RATIO_NEEDED_FOR_REVEALING_FAKE_ENEMY_INTEL**
  - Default: 0.9

- **ARMY_INTEL_COMBAT_BONUS_MAX_BONUS**
  - Default: 0.15
  - Developer comment: max combat bonus that will apply when intel is high enough

- **ARMY_INTEL_COMBAT_BONUS_FACTOR_ATTACK**
  - Default: 1.0
  - Developer comment: multiplier for attack value of intel combat bonus

- **ARMY_INTEL_COMBAT_BONUS_FACTOR_DEFENSE**
  - Default: 1.0
  - Developer comment: multiplier for defense value of intel combat bonus

- **ARMY_INTEL_COMBAT_BONUS_MIN_INTEL_FOR_BONUS**
  - Default: 5
  - Developer comment: min intel needed to start applying ARMY_INTEL_COMBAT_BONUS_MAX_BONUS

- **ARMY_INTEL_COMBAT_BONUS_MAX_INTEL_FOR_BONUS**
  - Default: 50
  - Developer comment: intel needed to fully apply ARMY_INTEL_COMBAT_BONUS_MAX_BONUS

- **NAVAL_SUPREMACY_INTEL_LOW**
  - Default: 0.4
  - Developer comment: we need more intel than this to get any supremacy

- **NAVAL_SUPREMACY_INTEL_LOW_SUPREMACY_PENALTY_START**
  - Default: 0.1
  - Developer comment: supremacy is reduced to NAVAL_SUPREMACY_INTEL_LOW_SUPREMACY_MIN_PENALTY at or below this intel

- **NAVAL_SUPREMACY_INTEL_LOW_SUPREMACY_MIN_PENALTY**
  - Default: 0.5
  - Developer comment: you get this much supremacy at NAVAL_SUPREMACY_INTEL_LOW_SUPREMACY_PENALTY_START and scales up to 1 at NAVAL_SUPREMACY_INTEL_LOW

- **NAVY_FLEET_COUNT_INTEL_MIN**
  - Default: 0.1

- **NAVY_FLEET_COUNT_INTEL_MAX**
  - Default: 0.3

- **NAVY_FLEET_COUNT_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5

- **NAVY_TASKFORCE_COUNT_INTEL_MIN**
  - Default: 0.3

- **NAVY_TASKFORCE_COUNT_INTEL_MAX**
  - Default: 0.7

- **NAVY_TASKFORCE_COUNT_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5

- **NAVY_SHIP_COUNT_INTEL_MIN**
  - Default: 0.1

- **NAVY_SHIP_COUNT_INTEL_MAX**
  - Default: 0.8

- **NAVY_SHIP_COUNT_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5

- **NAVY_MIN_INTEL_TO_SHOW_EXISTING_CATEGORY_TYPES**
  - Default: 0.1
  - Developer comment: this is about disaplying ships by class category

- **NAVY_SHIP_TYPE_COUNT_INTEL_MIN**
  - Default: 0.3
  - Developer comment: this range is used both when for disaplying counts by class and counts by variant

- **NAVY_SHIP_TYPE_COUNT_INTEL_MAX**
  - Default: 0.7

- **NAVY_SHIP_TYPE_COUNT_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5

- **NAVY_MIN_INTEL_TO_SHOW_SHIP_CLASSES**
  - Default: 0.5
  - Developer comment: this unclocks the display of a given variant

- **NAVY_DEPLOYED_MANPOWER_COUNT_RANGE_INTEL_MIN**
  - Default: 0.05

- **NAVY_DEPLOYED_MANPOWER_COUNT_RANGE_INTEL_MAX**
  - Default: 0.7

- **NAVY_DEPLOYED_MANPOWER_COUNT_RANGE_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5

- **NAVY_MIN_INTEL_TO_SHOW_SHIP_DESIGN_DETAILS**
  - Default: 0.8

- **AIR_AIRWING_COUNT_INTEL_MIN**
  - Default: 0.0

- **AIR_AIRWING_COUNT_INTEL_MAX**
  - Default: 0.7

- **AIR_AIRWING_COUNT_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5

- **AIR_MIN_INTEL_TO_SHOW_AIRWING_CLASSES**
  - Default: 0.3

- **AIR_WING_TYPE_COUNT_INTEL_MIN**
  - Default: 0.5

- **AIR_WING_TYPE_COUNT_INTEL_MAX**
  - Default: 0.7

- **AIR_WING_TYPE_COUNT_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5

- **AIR_DEPLOYED_MANPOWER_COUNT_RANGE_INTEL_MIN**
  - Default: 0.1

- **AIR_DEPLOYED_MANPOWER_COUNT_RANGE_INTEL_MAX**
  - Default: 0.7

- **AIR_DEPLOYED_MANPOWER_COUNT_RANGE_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.5

- **CIVILIAN_MAPICON_INDUSTRY_COUNT_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: 0.7

- **MAP_INTEL_VISIBILITY_CUTOFFS**
  - Default: { 0.1, -50, 0.4, 0, 0.6, 50, 1.0, 100 }
  - Developer comment: how much map intel is gained with intel over a country. first number is threshold, second is amount of intel map intel gained

- **ARMY_AVG_ARMOR_INTEL_MIN**
  - Default: 0.0
  - Developer comment: these are used in some triggers

- **ARMY_AVG_ARMOR_INTEL_MAX**
  - Default: 0.5

- **ARMY_AVG_ARMOR_RANGE_AT_LOWEST_INTEL**
  - Default: 1.0

- **ARMY_MAX_ARMOR_INTEL_MIN**
  - Default: 0.0

- **ARMY_MAX_ARMOR_INTEL_MAX**
  - Default: 0.5

- **ARMY_MAX_ARMOR_RANGE_AT_LOWEST_INTEL**
  - Default: 1.0

- **ARMY_AVG_PIERCING_INTEL_MIN**
  - Default: 0.0

- **ARMY_AVG_PIERCING_INTEL_MAX**
  - Default: 0.5

- **ARMY_AVG_PIERCING_RANGE_AT_LOWEST_INTEL**
  - Default: 1.0

- **ARMY_MAX_PIERCING_INTEL_MIN**
  - Default: 0.0

- **ARMY_MAX_PIERCING_INTEL_MAX**
  - Default: 0.5

- **ARMY_MAX_PIERCING_RANGE_AT_LOWEST_INTEL**
  - Default: 1.0

- **NAVY_MAPICON_MISSION_COUNT_INTEL_MIN**
  - Default: 0.5
  - Developer comment:
    ```text
    ~
    min intel to show assigned naval missions
    ```

- **NAVY_MAPICON_MISSION_COUNT_INTEL_MAX**
  - Default: 0.8
  - Developer comment: min intel to show assigned naval missions with perfect accuracy, and taskforces count

- **NAVY_MAPICON_SHOW_ALL_NAVAL_PORTS**
  - Default: 0.3
  - Developer comment: min intel to show all naval ports (otherwise you will only see nearby ones)

- **NAVY_MAPICON_NAVAL_PORT_VISIBILITY_DETAIL_THRESHOLDS**
  - Default: { 0.0, 0.1, 0.3, 0.7, 0.8 }
  - Developer comment:
    ```text
    how detailed the post tooltips will be
    for no intel
    show port level
    show fuzzy taskforce count
    show full taskforce count
    show taskforce details
    ```

- **NAVY_MAPICON_NAVAL_PORT_TASKFORCE_FUZZY_THRESHOLD**
  - Default: 0.5

- **AIR_MAPICON_MISSION_COUNT_INTEL_MIN**
  - Default: { 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3 }
  - Developer comment:
    ```text
    AIR_SUPERIORITY
    CAS
    INTERCEPTION
    STRATEGIC_BOMBER
    NAVAL_BOMBER
    DROP_NUKE
    PARADROP
    NAVAL_KAMIKAZE
    PORT_STRIKE
    ATTACK_LOGISTICS
    AIR_SUPPLY
    TRAINING
    NAVAL_MINES_PLANTING
    NAVAL_MINES_SWEEPING
    RECON
    NAVAL_PATROL
    ```

- **AIR_MAPICON_MISSION_COUNT_INTEL_MAX**
  - Default: { 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6 }
  - Developer comment:
    ```text
    AIR_SUPERIORITY
    CAS
    INTERCEPTION
    STRATEGIC_BOMBER
    NAVAL_BOMBER
    DROP_NUKE
    PARADROP
    NAVAL_KAMIKAZE
    PORT_STRIKE
    ATTACK_LOGISTICS
    AIR_SUPPLY
    TRAINING
    NAVAL_MINES_PLANTING
    NAVAL_MINES_SWEEPING
    RECON
    NAVAL_PATROL
    ```

- **AIR_MAPICON_MISSION_COUNT_INTEL_RANGE_AT_LOWEST_INTEL**
  - Default: { 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5 }
  - Developer comment:
    ```text
    AIR_SUPERIORITY
    CAS
    INTERCEPTION
    STRATEGIC_BOMBER
    NAVAL_BOMBER
    DROP_NUKE
    PARADROP
    NAVAL_KAMIKAZE
    PORT_STRIKE
    ATTACK_LOGISTICS
    AIR_SUPPLY
    TRAINING
    NAVAL_MINES_PLANTING
    NAVAL_MINES_SWEEPING
    RECON
    NAVAL_PATROL
    ```

- **AIR_MAPICON_SHOW_ALL_AIR_PORTS**
  - Default: 0.3
  - Developer comment: min intel to show all air ports (otherwise you will only see nearby ones)

- **AIR_MAPICON_AIR_PORT_VISIBILITY_DETAIL_THRESHOLDS**
  - Default: { 0.0, 0.3, 0.7, 0.8 }
  - Developer comment:
    ```text
    how detailed the post tooltips will be
    for no intel
    show fuzzy air plane count
    show full air count
    show air plane details
    ```

- **AIR_MAPICON_AIR_PORT_PLANE_FUZZY_THRESHOLD**
  - Default: 0.5

- **AIR_MIN_INTEL_TO_SHOW_EQUIPMENT_DESIGN_DETAILS**
  - Default: 0.8
  - Developer comment: ~intel ledger defines

## NCharacter

- **OFFICER_CORP_ADVISOR_ENTRIES_IN_MENU**
  - Default: { "high_command", "theorist", "army_chief", "air_chief", "navy_chief" }

- **OFFICER_CORP_HIGH_COMMAND_SLOTS_IN_MENU**
  - Default: 3
  - Developer comment: For Alert manager to count the number of High Command Slots in the UI

- **POLITICAL_ADVISOR_SLOTS_IN_MENU**
  - Default: 3
  - Developer comment: For Alert manager to count the number of Political Advisor Slots in the UI

- **DEFAULT_PP_COST_FOR_MILITARY_ADVISOR**
  - Default: 50
  - Developer comment: When an advisor does not have cost assigned this is the default used

- **DEFAULT_PP_COST_FOR_POLITICAL_ADVISOR**
  - Default: 150

- **DEFAULT_CP_COST_FOR_ADVISOR**
  - Default: 0
  - Developer comment: For Starting Advisors

- **DEFAULT_CP_COST_FOR_DYNAMIC_ADVISORS**
  - Default: 0
  - Developer comment: For Advisors created during gameplay

- **ADVISOR_PROMOTION_COST**
  - Default: 5
  - Developer comment: Cost to promote someone to advisor

- **COUNTRY_LEADER_BASE_EXPIRE_YEAR_LENGTH**
  - Default: 5
  - Developer comment: When creating a dynamic country leader if an expire date is not set it will have 5 years as a base expiration date

- **COUNTRY_LEADER_BASE_RANDOM_MAX_YEAR_LENGTH**
  - Default: 15
  - Developer comment: Max random value added to COUNTRY_LEADER_BASE_EXPIRE_YEAR_LENGTH

- **SPECIALIST_ADVISOR_MIN_RANK**
  - Default: 4

- **EXPERT_ADVISOR_MIN_RANK**
  - Default: 6

- **GENIUS_ADVISOR_MIN_RANK**
  - Default: 8

## NSupply

- **MAX_RAILWAY_LEVEL**
  - Default: 5
  - Developer comment: update railway texture as well, each frame corresponds to a level

- **CAPITAL_SUPPLY_BASE**
  - Default: 5.0
  - Developer comment:
    ```text
    defines to calculate the capitals supply. This will be also used for max supply of other nodes depending on how well they are connected to capital. Using the formula:
    CapitalSupply = CAPITAL_SUPPLY_BASE + (NumberOfCivilianFactories * CAPITAL_SUPPLY_CIVILIAN_FACTORIES) + (NumberOfMilitaryFactories * CAPITAL_SUPPLY_MILITARY_FACTORIES) + (NumberOfDockyards * CAPITAL_SUPPLY_DOCKYARDS)
    base supply for capital
    ```

- **CAPITAL_SUPPLY_CIVILIAN_FACTORIES**
  - Default: 0.3
  - Developer comment: supply from one civilian factory

- **CAPITAL_SUPPLY_MILITARY_FACTORIES**
  - Default: 0.6
  - Developer comment: supply from one military factory

- **CAPITAL_SUPPLY_DOCKYARDS**
  - Default: 0.4
  - Developer comment: supply from one naval factory

- **CAPITAL_INITIAL_SUPPLY_FLOW**
  - Default: 5.0
  - Developer comment:
    ```text
    defines that are used for supply reach for capital
    supply flow will start from INITIAL_SUPPLY_FLOW and will be reduced by a penalty on each province it travels (which depends on how far we are from our origin, terrain etc)
    a supply reach >= 1.0 considered "perfect" and will be able to fully support units on that particular province (assuming you are not over capacity)
    starting supply from
    ```

- **CAPITAL_STARTING_PENALTY_PER_PROVINCE**
  - Default: 0.5
  - Developer comment: starting penalty that will be added as supply moves away from its origin (modified by stuff like terrain)

- **CAPITAL_ADDED_PENALTY_PER_PROVINCE**
  - Default: 1.2
  - Developer comment: added penalty as we move away from origin

- **NODE_INITIAL_SUPPLY_FLOW**
  - Default: 2.8
  - Developer comment: defines that are used for supply reach for built nodes

- **NODE_STARTING_PENALTY_PER_PROVINCE**
  - Default: 0.50

- **NODE_ADDED_PENALTY_PER_PROVINCE**
  - Default: 0.70

- **NAVAL_BASE_INITIAL_SUPPLY_FLOW**
  - Default: 3.3
  - Developer comment: defines that are used for supply reach for dockyards

- **NAVAL_BASE_STARTING_PENALTY_PER_PROVINCE**
  - Default: 0.84

- **NAVAL_BASE_ADDED_PENALTY_PER_PROVINCE**
  - Default: 1.1

- **NODE_FLOW_BONUS_PER_RAIL_LEVEL**
  - Default: 0.34
  - Developer comment: Node Flow (i.e. province caps) increase by this amount per railway level of the node's bottleneck

- **RIVER_RAILWAY_LEVEL**
  - Default: 1
  - Developer comment: rivers will transfer in between nodes as if they were this level

- **FLOATING_HARBOR_INITIAL_SUPPLY_FLOW**
  - Default: 2.6
  - Developer comment: defines that are used for supply reach for floating harbors

- **FLOATING_HARBOR_STARTING_PENALTY_PER_PROVINCE**
  - Default: 0.8

- **FLOATING_HARBOR_ADDED_PENALTY_PER_PROVINCE**
  - Default: 0.8

- **FLOATING_HARBOR_BASE_SUPPLY**
  - Default: 15.0
  - Developer comment: supply given by a floating harbor

- **FLOATING_HARBOR_BASE_DURATION**
  - Default: 21
  - Developer comment: duration of a full hp floating harbor

- **FLOATING_HARBOR_DURATION_RATIO_AT_MIN_HP**
  - Default: 0.0
  - Developer comment: duration mult for a harbor that was reduced to 0 hp

- **FLOATING_HARBOR_MIN_DECAY**
  - Default: 0.2
  - Developer comment: Always reduce Floating Harbor longevity by this many "hours" per hour

- **FLOATING_HARBOR_DECAY_MAX_AIR_BONUS**
  - Default: -0.1
  - Developer comment: At 100% Friendly Air superiourity, change decay rate by this many "hours" per hour

- **FLOATING_HARBOR_DECAY_MAX_AIR_PENALTY**
  - Default: 0.4
  - Developer comment: At 100% Enemy Air superiourity, change decay rate by this many "hours" per hour

- **FLOATING_HARBOR_DECAY_MAX_NAVAL_BONUS**
  - Default: -0.2
  - Developer comment: At 100% Friendly naval superiourity, change decay rate by this many "hours" per hour

- **FLOATING_HARBOR_DECAY_MAX_NAVAL_PENALTY**
  - Default: 0.5
  - Developer comment: At 100% Enemy Naval superiourity, change decay rate by this many "hours" per hour

- **FLOATING_HARBOR_DECAY_NO_CONTROL_PENALTY**
  - Default: 1.0
  - Developer comment: If adjacent land province is not held, change decay rate by this many "hours" per hour

- **SUPPLY_FLOW_DROP_REDUCTION_AT_MAX_INFRA**
  - Default: 0.30
  - Developer comment: max infrastructure level will reduce the supply flow drop off by this ratio

- **SUPPLY_FLOW_PENALTY_CROSSING_RIVERS**
  - Default: 0.20
  - Developer comment: crossing rivers introduces additional penalty

- **SUPPLY_FLOW_DIST_LOGISTICS_FALLOFF_K**
  - Default: 1.3
  - Developer comment:
    ```text
    node flow terrain falloff is scaled by logistics curve based on distance(d) (scalar / (1+e^(-k(d-midpoint))))
    How steep the curve is
    ```

- **SUPPLY_FLOW_DIST_LOGISTICS_FALLOFF_MIDPOINT**
  - Default: 2.3
  - Developer comment: sigmoid inflection point

- **SUPPLY_FLOW_DIST_LOGISTICS_FALLOFF_SCALAR**
  - Default: 0.9
  - Developer comment: Max Penalty adjustment due to distance

- **SUPPLY_FLOW_DIST_LOGISTICS_FALLOFF_MIN_PENALTY_SCALE**
  - Default: 0.25
  - Developer comment: Logistics curve never reduces penalty facor below this limit

- **SUPPLY_HUB_FULL_MOTORIZATION_BONUS**
  - Default: 2.2
  - Developer comment: The range bonus added to a fully motorized hub. This supply is added on top of the XXX_INITIAL_SUPPLY_FLOW defined above.

- **SUPPLY_HUB_FULL_MOTORIZATION_TRUCK_COST**
  - Default: 60.0
  - Developer comment: How many trucks does it cost to fully motorize a hub

- **SUPPLY_HUB_MOTORIZATION_MARGINAL_EFFECT_DECAY**
  - Default: 1.6
  - Developer comment: For each additional level of motorization on a hub (i.e. contry with set motoriazation) reduce max bonus for next level by this amount

- **RAILWAY_BASE_FLOW**
  - Default: 10.0
  - Developer comment:
    ```text
    used for calculating "flow" for railways.
    how much base flow railway gives when a node connected to its capital/a naval node by a railway
    ```

- **RAILWAY_FLOW_PER_LEVEL**
  - Default: 5.0
  - Developer comment: how much additional flow a railway level gives

- **RAILWAY_FLOW_PENALTY_PER_DAMAGED**
  - Default: 5.0
  - Developer comment: penalty to flow per damaged railway

- **RAILWAY_MIN_FLOW**
  - Default: 5.0
  - Developer comment: minimum railway flow can be reduced to

- **NAVAL_BASE_FLOW**
  - Default: 5.0
  - Developer comment:
    ```text
    used for calculating "flow" from a naval node to another naval node when it is connected via a convoy route
    NAVAL_BASE_MAX_SUPPLY_FLOW_FACTOR = 0.9, -- flow of the parent node is factored to this ratio (so at most it can transfer parent naval node flow * this define)
    max output/input of a naval node is limited by this base value + additional ratio for each level
    ```

- **NAVAL_FLOW_PER_LEVEL**
  - Default: 3.0
  - Developer comment: max output/input of a naval node is limited by previous base value + this define per its level

- **SUPPLY_NODE_MIN_SUPPLY_THRESHOLD**
  - Default: 1.0
  - Developer comment: if supply of a node is below this value it will be set to 0 -- Currently unused? This should happen when enough damage occurs

- **INFRA_TO_SUPPLY**
  - Default: 0.3
  - Developer comment: each level of infra gives this many supply

- **VP_TO_SUPPLY_BASE**
  - Default: 0.2
  - Developer comment: Bonus to supply from a VP, no matter the level

- **VP_TO_SUPPLY_BONUS_CONVERSION**
  - Default: 0.05
  - Developer comment: Bonus to supply local supplies from Victory Points, multiplied by this aspect and rounded to closest integer

- **SUPPLY_FROM_DAMAGED_INFRA**
  - Default: 0.15
  - Developer comment: damaged infrastructure counts as this in supply calcs

- **SUPPLY_BASE_MULT**
  - Default: 0.2
  - Developer comment: multiplier on supply base values

- **SUPPLY_DISRUPTION_DAILY_RECOVERY**
  - Default: 1.5
  - Developer comment: every day nodes recover this much of their accumulated disruption.

- **RAILWAY_CONVERSION_COOLDOWN**
  - Default: 10
  - Developer comment: railways will be put on cooldown when they are captured by enemy and will not be usable during the cooldown

- **RAILWAY_CONVERSION_COOLDOWN_CORE**
  - Default: 5

- **RAILWAY_CONVERSION_COOLDOWN_CIVILWAR**
  - Default: 0

- **DEFAULT_STARTING_TRUCK_RATIO**
  - Default: 1.5
  - Developer comment: countries get this ratio of starting truck in their buffers compared to their need

- **DEFAULT_STARTING_TRAIN_RATIO**
  - Default: 1
  - Developer comment: countries get this ratio of starting trains in their buffers compared to their need

- **SUPPLY_POINTS_PER_TRAIN**
  - Default: 1.0
  - Developer comment: old default 1.25 -- Amount of supply that can fit in a train. (Trains distribute supply from capital to a supply node.)

- **NUM_RAILWAYS_TRAIN_FACTOR**
  - Default: 0.03
  - Developer comment: the train usage is scaled by railway distance between the supply node and the capital multiplied by this factor

- **BASE_SUPPLY_MULT_FOR_TRUCK_DEFAULT_BUFFER**
  - Default: 1.0
  - Developer comment: initial value for wanted buffers over potential truck usage

- **BASE_SUPPLY_MULT_FOR_TRUCK_MIN_BUFFER**
  - Default: 0.0
  - Developer comment: min and max values for buffer ratio

- **BASE_SUPPLY_MULT_FOR_TRUCK_MAX_BUFFER**
  - Default: 100.0

- **TRUCK_ATTRITION**
  - Default: 0.003
  - Developer comment: base truck attrition

- **TRUCK_ATTRITION_FACTOR**
  - Default: 0.65
  - Developer comment: a scale on total truck attrition

- **BASE_TRUCK_HP**
  - Default: 100.0

- **TRUCK_HP_PER_ARMOR**
  - Default: 2

- **BASE_TRAIN_HP**
  - Default: 100.0

- **TRAIN_ARMOR_TARGETING_WEIGHT**
  - Default: 0.01
  - Developer comment: For each health point gained by armor_value, enemy bombers are this much more likely to target

- **TRAIN_ANTI_AIR_HIT_CHANCE**
  - Default: 0.07
  - Developer comment: Balancing value to determine the chance of train anti-air hitting an attacking airwing.

- **TRAIN_ANTI_AIR_HIT_ROLL_COUNT**
  - Default: 12
  - Developer comment: The air_attack of all attacked trains are accumulated, and then we do this many random rolls each with the hit chance set above to determine the fraction of the accumulated air_attack that hits.

- **TRAIN_ANTI_AIR_ATTACK_TO_AMOUNT**
  - Default: 0.001
  - Developer comment: Balancing value to convert the hitting air_attack to a percentage value of the attacking planes that are killed.

- **MIN_TRAIN_SUPPLY_FACTOR**
  - Default: 0.5
  - Developer comment: Having 0 trains in stockpile only applies this penalty factor, scaling up to 1.0 when need is met

- **MIN_TRAIN_REQUIREMENT**
  - Default: 2
  - Developer comment: If total train need <= this, then don't apply any supply penalty, even if stockpile is insufficient

- **SUPPLY_FLOW_REDUCTION_THRESHOLD**
  - Default: 0.1
  - Developer comment: if supply flow is lower than this, it is not applied

- **BASE_AIR_SUPPLY_MULT_FOR_TRUCK_BUFFER**
  - Default: 1.0
  - Developer comment:
    ```text
    following values are used for calculating potential truck usage
    generally potential is ~= current usage but as units moves along the map
    they are assigned to different nodes which adds slightly higher usage due to minimum truck needed being 1
    ```

- **BASE_ARMY_SUPPLY_MULT_FOR_TRUCK_BUFFER**
  - Default: 1.0

- **BASE_NAVY_SUPPLY_MULT_FOR_TRUCK_BUFFER**
  - Default: 1.0

- **CAPITAL_NODE_BASE_SUPPLY_ADD**
  - Default: 0

- **BUILT_NODE_BASE_SUPPLY_ADD**
  - Default: 0.6

- **LOCAL_NODE_BASE_SUPPLY_ADD**
  - Default: 0.5

- **NAVAL_NODE_BASE_SUPPLY_ADD**
  - Default: 0.3

- **ARMY_SUPPLY_RATIO_STARTING_GAIN**
  - Default: 0.0
  - Developer comment:
    ```text
    ~end
    armies slowly gains and buffers supply above >100% up to their supply grace if they have efficent supply flow
    otherwuse they will lose up to 100% supply every day depending on how bad supply flow is
    ```

- **ARMY_SUPPLY_RATIO_SPEED_GAIN_PER_HOUR**
  - Default: 0.01

- **ARMY_MAX_SUPPLY_RATIO_GAIN_PER_HOUR**
  - Default: 0.15

- **MIN_SURRENDER_LIMIT_TO_MOVE_SUPPLY_CAPITAL**
  - Default: 0.15
  - Developer comment: country needs to be above thos surrender ratio to be able to move its capital

- **COOLDOWN_DAYS_AFTER_MOVING_SUPPLY_CAPITAL**
  - Default: 30
  - Developer comment: cooldown for moving supply again after last move

- **DAYS_TO_START_GIVING_SUPPLY_AFTER_MOVING_SUPPLY_CAPITAL**
  - Default: 7
  - Developer comment: the country will start gaining supply after this many days moving its capital

- **DAYS_TO_START_GIVING_FULL_SUPPLY_AFTER_MOVING_SUPPLY_CAPITAL**
  - Default: 21
  - Developer comment: the country will reach max supply after this many days moving its capital

- **MIN_DIFF_FOR_AUTO_UPDATING_EXISTING_RAILWAYS**
  - Default: 5
  - Developer comment: while building railways, the system will prefer updating existing railway if new railway is close enough to existing one

- **SUPPLY_PATH_MAX_DISTANCE**
  - Default: 15
  - Developer comment:
    ```text
    reinforcements depends on distance to capital and following defines are used for calculating reinforcement time
    max time it can take
    ```

- **RAILWAY_DISTANCE_FACTOR_FOR_REINFORCEMENT_SPEED**
  - Default: 0.3
  - Developer comment: time factor for total railway distance

- **TRUCK_DISTANCE_FACTOR_FOR_REINFORCEMENT_SPEED**
  - Default: 0.01
  - Developer comment: time factor for total truck distance

- **NAVAL_DISTANCE_FACTOR_FOR_REINFORCEMENT_SPEED**
  - Default: 0.08
  - Developer comment: time factor for total naval distance

- **ALERT_VERY_LOW_SUPPLY_LEVEL**
  - Default: 0.2
  - Developer comment: At which point we show up the low and very low supply level alert. Value is in % of supplies supported vs required.

- **ALERT_LOW_SUPPLY_LEVEL**
  - Default: 0.5

- **AI_FRONT_MINIMUM_UNITS_PER_PROVINCE_FOR_SUPPLY_CALCULATIONS**
  - Default: 1
  - Developer comment: AI will try to keep this amount of divisions per province as a minimum when evaluating supply limitations for war fronts

- **AI_FRONT_DIVISIONS_PER_SUPPLY_POINT**
  - Default: 1.0
  - Developer comment: How many divisions should the AI consider it can supply per available supply point

- **AI_FRONT_MAX_UNITS_ENEMY_COUNT_FACTOR**
  - Default: 1.2
  - Developer comment: Make sure AI front MaxNrUnits is at least EnemyCount multiplied by this factor

- **SUPPLY_THRESHOLD_FOR_ARMY_ATTRITION**
  - Default: 0.35
  - Developer comment: armies will only get attrition below this supply

- **NUMBER_OF_SHOWN_SUPPLY_SOURCES_IN_SUPPLY_MAPMODE**
  - Default: 3
  - Developer comment: number of supply flow sources shown in breakdown tooltip

- **ESTIMATED_DIVISION_WEIGHT_FOR_SUPPLY_ESTIMATIONS_GUI**
  - Default: 1.0
  - Developer comment: Division supply consumption used for estimating frontline weight for order tooltips

- **AVAILABLE_MANPOWER_STATE_SUPPLY**
  - Default: 0.18
  - Developer comment: Factor for state supply from max manpower (population)

- **NON_CORE_MANPOWER_STATE_SUPPLY**
  - Default: 0.2
  - Developer comment: Factor for population sttate supply when controlled by an occupier (NO TAKE FOOD)

- **STORED_SUPPLY_CONSUMPTION_RATE_FACTOR**
  - Default: 0.75
  - Developer comment: Multiplies consumption rate of stored supply (more/less easement)

## NAITheatre

- **AI_THEATRE_GENERATION_HOME_THEATRE_DEPTH_RESTRICTION**
  - Default: 2
  - Developer comment: The home theatre is generated based off a initial depth restriction

- **AI_THEATRE_GENERATION_BORDER_SIZE_RESTRICTION**
  - Default: 7
  - Developer comment: Theatres are generated based off borders, Higher value means larger theatres

- **AI_THEATRE_GENERATION_DEPTH_TO_START_CONSIDERING_BORDERSTATES**
  - Default: 2
  - Developer comment: Distance from capital in terms of states

- **AI_THEATRE_GENERATION_MINIMUM_STATE_COUNT**
  - Default: 3
  - Developer comment: Small Theatres - Minimum state count for a theatre

- **AI_THEATRE_GENERATION_MAX_DISTANCE_TO_MERGE**
  - Default: 200
  - Developer comment: Small Theatres - Dont merge with too far away theatres, higher value means less merging will occur

- **AI_THEATRE_GENERATION_MAX_DISTANCE_TO_FILL**
  - Default: 350
  - Developer comment: Final generation step - Max distance to fill states, higher values means less theatres

- **AI_THEATRE_DISTRIBUTION_SAME_THEATRE_SCORE_MODIFIER**
  - Default: 0.25
  - Developer comment: Value that affects the score of units when distributing to fronts within the same theatre, its a percentage multiplier, the higher it is the higher the chance of units staying in close proximity

- **AI_THEATRE_DISTRIBUTION_MAX_SCORE**
  - Default: 250000
  - Developer comment: Max Score that a unit can have when being distributed to ai fronts, higher value means more granularity in score changes, lower values means less variation in where units can go

- **AI_THEATRE_DISTRIBUTION_PERCENTAGE_OF_MINIMUM_UNITS_TO_KEEP**
  - Default: 1.0
  - Developer comment: How much should a frontline adheer to its minimum unit demand, when removing/reassigning units

- **AI_THEATRE_DISTRIBUTION_MAX_PERCENT_UNMET_DEMAND_PER_FRONT**
  - Default: 0.5
  - Developer comment: Percentage of how much fronts should request from other lower priority fronts, 0 means once a front gets hold of a unit it stays there forever until its demand is reduced, controlls shuffling of units.

- **AI_THEATRE_STATE_UPDATE_MAX_STATE_COUNT_TO_EXPAND**
  - Default: 25
  - Developer comment: Max theatre size

- **AI_THEATRE_BREAKDOWN_MIN_STATE_COUNT**
  - Default: 3
  - Developer comment: Theatres below this size will break and merge with others

- **AI_THEATRE_BREAKDOWN_MAX_DISTANCE_TO_MERGE**
  - Default: 200
  - Developer comment: Dont merge with too far away theatres, higher value means less merging will occur

- **AI_THEATRE_PERCENTAGE_OF_UNITS_TO_KEEP_IN_NEIGHBOR_DEFENSIVE_ORDERS**
  - Default: 0.05
  - Developer comment: Percentage of units to keep in neighbor defensive orders from war fronts

- **AI_THEATRE_SEARCH_SUPPLY_NODE_MAX_DEPTH**
  - Default: 5
  - Developer comment: Max depth of breadth-first search while looking for supply nodes when out of supply

- **AI_THEATRE_SUPPLY_CRISIS_LIMIT**
  - Default: 0.1
  - Developer comment: If a unit is standing in an area with this supply ratio it will try to escape

- **AI_THEATRE_AI_FRONT_MIN_DESIRED_RATIO**
  - Default: 0.18
  - Developer comment: Fronts are sorted based on priority, we nudge unit demand based on this sorting, the higher the value the more units the most important front gets

## NIndustrialOrganisation

- **ASSIGN_DESIGN_TEAM_PP_COST_PER_DAY**
  - Default: 0.1
  - Developer comment: Cost in Political Power daily generation when one MIO is assigned to a research slot. If 0, cost is entirely disabled.

- **ASSIGN_INDUSTRIAL_MANUFACTURER_PP_COST_PER_DAY**
  - Default: 0.0
  - Developer comment: Cost in Political Power daily generation when one MIO is assigned to a production line. If 0, cost is entirely disabled.

- **FUNDS_FOR_SIZE_UP**
  - Default: 700
  - Developer comment: Funds needed for a MIO to increment its size and get points to unlock traits

- **FUNDS_FOR_SIZE_UP_LEVEL_FACTOR**
  - Default: 100
  - Developer comment: How much each level mutliplies the funds for size up

- **FUNDS_FOR_SIZE_UP_LEVEL_POW**
  - Default: 1.8
  - Developer comment: the power we applie to the mio size when calculating funds to level up.

- **UNLOCKED_TRAITS_PER_SIZE_UP**
  - Default: 1
  - Developer comment: Number of points for unlocking traits obtained when the MIO increments its size

- **DESIGN_TEAM_CHANGE_XP_COST**
  - Default: 0
  - Developer comment: Flat cost added to the XP cost of a new equipment design. If 0, cost is entirely disabled.

- **FUNDS_FOR_RESEARCH_COMPLETION_PER_RESEARCH_COST**
  - Default: 500
  - Developer comment: Funds added to MIO when the Design Team has completed a research, multiplied by research_cost in technology template

- **FUNDS_FOR_CREATING_EQUIPMENT_VARIANT**
  - Default: 0
  - Developer comment: Funds added to MIO when a new variant is created with the Design Team assigned to it

- **FUNDS_FROM_MANUFACTURER_PER_IC_PER_DAY**
  - Default: 0.1
  - Developer comment: Funds added to MIO when a manufacturer is attached to a production line. Added every day proportional to IC produced.

- **MAX_FUNDS_FROM_MANUFACTURER_PER_DAY**
  - Default: 100
  - Developer comment: Max funds generated per manufacturer per day. Set to 0 for no Maximum.

- **DESIGN_TEAM_RESEARCH_BONUS**
  - Default: 0.05
  - Developer comment: Research bonus for applying a Design Team that matches the technology

- **ENABLE_TASK_CAPACITY**
  - Default: false
  - Developer comment: Enable limited task capacity for MIOs

- **DEFAULT_INITIAL_TASK_CAPACITY**
  - Default: 0
  - Developer comment: Default start task capacity for each MIO (may be overriden in DB)

- **DEFAULT_INITIAL_POLICY_ATTACH_COST**
  - Default: 25
  - Developer comment: Default start attach cost in PP for policies

- **DEFAULT_INITIAL_ATTACH_POLICY_COOLDOWN**
  - Default: 180
  - Developer comment: Default start cooldown in days after attaching a policy

- **LEGACY_COST_FACTOR_SCALE**
  - Default: 1.0
  - Developer comment: Multiplier to use when legacy Designer cost factors is applied to MIOs (<IdeaGroup>_cost_factor)

## NProject

- **FACILITY_SUPPLY_WARNING_RED_RATIO**
  - Default: 0.66
  - Developer comment: When lacking supply for a facility it will be a yellow icon shown until the supply is less than this value, where it will turn red.

- **DEFAULT_COMPLEXITY**
  - Default: 100
  - Developer comment: Default special project prototype phase to only require one iteration.

- **DEFAULT_EMPTY_REWARD_WEIGHT**
  - Default: 1.0
  - Developer comment: The weight for no reward being given after a prototype iteration.

- **DEFAULT_STOP_PROJECT_DAYS**
  - Default: 10
  - Developer comment: The amount of days it takes for a cancelled project to be stopped.

- **DAYS_TO_REMOVE_SCIENTIST**
  - Default: 10
  - Developer comment: Amount of days needed for a scientist to be unassigned.

- **DISMANTLE_FACILITY_DAYS**
  - Default: 100
  - Developer comment: Amount of days needed to dismantle a facility.

- **PROTOTYPE_PHASE_MAX_PROGRESS**
  - Default: 100
  - Developer comment: the number of progress points needed to finish the prototype phase and complete the project

- **MINIMUM_PROJECT_SPEED_FACTOR_FROM_SUPPLY**
  - Default: 0.2
  - Developer comment: Minimum special project research speed based on supply

- **NEEDED_SUPPLY_FOR_FULL_SPEED_PROJECT**
  - Default: 3.0
  - Developer comment: Supply needed in province to get full research speed for special project

- **MINIMUM_PROJECT_SPEED_FACTOR_FROM_RESOURCE_SHORTAGE**
  - Default: 0.2
  - Developer comment: Minimum special project research speed factor based on resource shortage^M

- **ITERATION_REWARD_DEFAULT_WEIGHT**
  - Default: 1.0
  - Developer comment: If no weight is specified, set it to 1.0

- **DEFAULT_PROJECT_COMPLETION_SCIENTIST_EXPERIENCE_GAIN**
  - Default: 192.0
  - Developer comment: Default experience gain for assigned scientist when a project is completed

- **SCIENTIST_INJURED_FACTOR**
  - Default: 0.0
  - Developer comment: A factor to reduce the amount of progress gained in a program with attached injured scientist. E.g. 0.5 reduces the progress by 50%

- **RECRUIT_SCIENTIST_ONE_TRAIT_CHANCE**
  - Default: 0.35
  - Developer comment: Chance to get one trait when creating a scientist. E.g. 0.35 = 35% chance to get a trait

- **SCIENTIST_BASIC_RESEARCH_DAILY_XP_GAIN**
  - Default: 0.28
  - Developer comment: Daily experience gain for doing basic research

- **RECRUIT_SCIENTIST_COST**
  - Default:
    ```text
    {25,
    50, 
    75, 
    100}
    ```
  - Developer comment:
    ```text
    pp cost if no available scientist
    pp cost if 1 available scientist
    pp cost if 2 available scientist
    pp cost if more than 2 available scientist
    ```
  - Usage: Amount of pp to hire a scientist based on available scientist

- **SCIENTIST_SKILL_LEVEL_THRESHOLDS**
  - Default:
    ```text
    {100,
    100,
    300,
    700,
    1500}
    ```
  - Developer comment:
    ```text
    to go from level 0 to level 1
    to go from level 1 to level 2
    to go from level 2 to level 3
    ...
    Max level = Array size
    ```
  - Usage: Threshold for scientist to level up

- **SCIENTIST_SKILL_LEVEL_SPEED_MODIFIER**
  - Default:
    ```text
    {-1.0,
    -0.05,
    0.05,
    0.1,
    0.15,
    0.25|
    ```
  - Developer comment:
    ```text
    -1.0 means -100%         also name loc key is SCIENTIST_SKILL_LEVEL_NAME_0
    -0.05 means -5%            also name loc key is SCIENTIST_SKILL_LEVEL_NAME_1
    0 means no change        also name loc key is SCIENTIST_SKILL_LEVEL_NAME_2
    0.15 means +15%         ...
    -- Size MUST be SCIENTIST_SKILL_LEVEL_THRESHOLDS's size + 1
    ```
  - Usage: Bonus to apply to daily phase progress according to the skill level of the scientist

- **PROJECT_LOSS_FACTOR_ON_CAPTURE**
  - Default: 0.2
  - Developer comment: Factor of lost progress on project when facility is captured

- **PROJECT_CAPTURE_GAIN_RATIO**
  - Default: 0.2
  - Developer comment: Ratio of difference from captured facilities ongoing project to receive to the captors' progress

- **PROJECT_CAPTURE_BREAKTHROUGH_PROGRESS**
  - Default: 0.1
  - Developer comment: Ratio of breakthrough progress on capture to the captor for the facilities specialization

- **PROJECT_CAPTURE_DIMINISHING_RETURN**
  - Default: 0.6
  - Developer comment: Reduced amount of gain when capturing a facility with a project you already gained. Will apply the factor each time a capture occurs. 0.6 means a reduction of 60% on next project capture.

- **BASIC_RESEARCH_TECHNOLOGY_BONUS_FACTOR**
  - Default: 0.02
  - Developer comment: Bonus research factor applied to technologies per scientist skill level when performing basic research in a matching facility.

- **BASIC_RESEARCH_TECHNOLOGY_BONUS_DIMINISHING_RETURN_FACTOR**
  - Default: 0.5
  - Developer comment: Diminishing return on BASIC_RESEARCH_TECHNOLOGY_BONUS_FACTOR for each extra scientist performing basic research for multiple facilities.

- **BREAKTHROUGH_DAILY_TECHNOLOGY_GAIN**
  - Default: 12
  - Developer comment: Amount in 1/100th percentage. E.g. 25 = 0.25%

- **BREAKTHROUGH_DAILY_SCIENTIST_SKILL_GAIN**
  - Default: 5
  - Developer comment: Amount in 1/100th percentage gained per skill when doing basic research. E.g. 5 = 0.05% per skill level.

- **BREAKTHROUGH_DAILY_ROCKET_SITE_GAIN**
  - Default: 1
  - Developer comment: Amount in 1/100th percentage gained per rocket site level. E.g. 1 = 0.01% per rocket site level.

- **BREAKTHROUGH_DAILY_NUCLEAR_REACTOR_GAIN**
  - Default: 1
  - Developer comment: Amount in 1/100th percentage gained per nuclear reactor. E.g. 2 = 0.02% per nuclear reactor.

- **BREAKTHROUGH_GAIN_ANIMATION_SPEED_MAX**
  - Default: 1.0
  - Developer comment: The animation for gaining breakthrough progress is a ratio of this value and current daily gain.

## NRaids

- **BASE_DAYS_TO_PREPARE**
  - Default: 7
  - Developer comment: Base number of days required to complete raid preparation phase

- **MAX_STATE_TARGETS_TO_EVALUATE_PER_HOUR**
  - Default: 50
  - Developer comment: PERFORMANCE (HOURLY TICK) : higher number = faster state target re-evaulation + lower performance

- **RAID_TARGET_ITEM_POOL_SIZE**
  - Default: 512
  - Developer comment: PERFORMANCE (UI) : number of entries to reserve in the raid target item pool

- **RAID_TYPE_ICON_ITEM_POOL_SIZE**
  - Default: 512
  - Developer comment: PERFORMANCE (UI) : number of entries to reserve in the raid type icon item pool

- **RAID_LOW_RISK_SETTING_DISASTER_MODIFIER**
  - Default: 0
  - Developer comment: How much the disaster risk is modified when the dial is set to "low"

- **RAID_MEDIUM_RISK_SETTING_DISASTER_MODIFIER**
  - Default: 0.1
  - Developer comment: How much the disaster risk is modified when the dial is set to "medium"

- **RAID_HIGH_RISK_SETTING_DISASTER_MODIFIER**
  - Default: 0.25
  - Developer comment: How much the disaster risk is modified when the dial is set to "high"

- **RAID_SUCCESS_MODIFIER_THRESHOLD_BAD**
  - Default: -10.0
  - Developer comment: If a success chance modifier is below this value, it will be displayed in red

- **RAID_SUCCESS_MODIFIER_THRESHOLD_NEUTRAL**
  - Default: 0.0
  - Developer comment: If a success chance modifier is below this value, it will be displayed in yellow

- **MAX_DETECTED_TARGETS_PER_HOUR**
  - Default: 1
  - Developer comment: PERFORMANCE (HOURLY TICK) : max number of targets to be detected per hour, NOTE : keep this low because detection is checked against every country!

- **RAID_DEFAULT_TARGET_COOLDOWN_DAYS**
  - Default: 365
  - Developer comment: The default cooldown (in days) for raiding the same target, can be overriden for specific raid types through script

- **RAID_UNIT_SPEED_MULTIPLIER**
  - Default: 0.1
  - Developer comment: Global speed control

- **BASE_NAVAL_COMMANDO_RAID_DISTANCE**
  - Default: 1500
  - Developer comment: Max distance in kilometers

- **RAID_LOW_RISK_SETTING_SUCCESS_MODIFIER**
  - Default: 0.0
  - Developer comment: How much the success chance is modified when the dial is set to "low"

- **RAID_MEDIUM_RISK_SETTING_SUCCESS_MODIFIER**
  - Default: 0.1
  - Developer comment: How much the success chance is modified when the dial is set to "low"

- **RAID_HIGH_RISK_SETTING_SUCCESS_MODIFIER**
  - Default: 0.25
  - Developer comment: How much the success chance is modified when the dial is set to "low"

- **TARGET_DETECTION_INTEL_TRESHOLD**
  - Default: 20.0
  - Developer comment: How much intel is needed for a target to be detected?

- **TARGET_INTEL_PER_CIVILIAN_INTEL_OVER_COUNTRY**
  - Default: 0.5
  - Developer comment: Intel level over target country is scaled by this value

- **TARGET_INTEL_PER_ARMY_INTEL_OVER_COUNTRY**
  - Default: 0.5
  - Developer comment: Intel level over target country is scaled by this value

- **TARGET_INTEL_PER_NAVY_INTEL_OVER_COUNTRY**
  - Default: 0.5
  - Developer comment: Intel level over target country is scaled by this value

- **TARGET_INTEL_PER_AIRFORCE_INTEL_OVER_COUNTRY**
  - Default: 0.5
  - Developer comment: Intel level over target country is scaled by this value

- **TARGET_INTEL_PER_NETWORK_STRENGTH**
  - Default: 0.5
  - Developer comment: Intel network strength in target state is scaled by this value

- **TARGET_INTEL_FROM_CONTROLLED_NEIGHBOUR_STATES**
  - Default: 15.0
  - Developer comment: Flat bonus for having control over at least one neighbour state

- **TARGET_INTEL_PER_AIR_SUPERIORITY**
  - Default: 0.5
  - Developer comment: Air superiority over target region is scaled by this value

- **TARGET_INTEL_FROM_DECRYPTION**
  - Default: 25.0
  - Developer comment: Flat bonus for having fully decrypted their ciphers

- **TARGET_INTEL_PENALTY_PER_ENEMY_COUNTER_INTEL**
  - Default: 5.0
  - Developer comment: Enemy counter intel is scaled by this value

- **RAID_OUTCOME_REPORT_DAYS_TO_LIVE**
  - Default: 30
  - Developer comment: How many days after a raid has ended will the raid outcome report be visible on the map before being automatically dismissed

- **NUCLEAR_BOMB_PRODUCTION_SCALE**
  - Default: 2555.0
  - Developer comment: +1 nuclear_production gives 1 nuke per 7 years

- **THERMONUCLEAR_BOMB_PRODUCTION_SCALE**
  - Default: 2555.0
  - Developer comment: +1 nuclear_production gives 1 nuke per 7 years

- **NUCLEAR_BOMB_MIN_DAMAGE_PERCENT**
  - Default: 0.1
  - Developer comment: Minimum damage from nukes as a percentage of current strength/organisation

- **NUCLEAR_BOMB_MAX_DAMAGE_PERCENT**
  - Default: 0.9
  - Developer comment: Minimum damage from nukes as a percentage of current strength/organisation

- **THERMONUCLEAR_BOMB_MIN_DAMAGE_PERCENT**
  - Default: 0.6
  - Developer comment: Minimum damage from nukes as a percentage of current strength/organisation

- **THERMONUCLEAR_BOMB_MAX_DAMAGE_PERCENT**
  - Default: 0.9
  - Developer comment: Minimum damage from nukes as a percentage of current strength/organisation

- **NUCLEAR_RAID_CATEGORY_NAME**
  - Default: "nuclear_raids"
  - Developer comment: The raid category to activate when clicking on the "nuclear" mission button for a rocket

- **ARMY_TRANSFER_MOVE_SAFELY**
  - Default: true
  - Developer comment: Whether to move safely when transferring divisions to the raid source

- **ARMY_TRANSFER_AVOID_ENEMY**
  - Default: true
  - Developer comment: Whether to avoid enemy when transferring divisions to the raid source

- **MAX_TARGETS_TO_UPDATE_PER_FRAME**
  - Default: 100
  - Developer comment: PERFORMANCE (FRAME) : max raid targets to evaluate per frame (affects raid map icon refresh rate)

## NWiki

- **BASE_URL**
  - Default:
    ```text
    "
    https://hoi4.paradoxwikis.com/
    "
    ```

- **FORUM_URL**
  - Default:
    ```text
    "
    https://forum.paradoxplaza.com/forum/index.php?forums/hearts-of-iron-iv.844/
    "
    ```

## NMapMode

- **FABRICATE_CLAIM_SELECTED_SECONDARY_COLOR**
  - Default: { 0, 1, 0, 1 }

- **FABRICATE_CLAIM_TARGET_COUNTRY_SECONDARY_COLOR**
  - Default: { 0, 0, 0, 0 }

- **FABRICATE_CLAIM_NON_TARGET_COUNTRY_SECONDARY_COLOR**
  - Default: { 0, 0, 0, 0 }

- **FABRICATE_CLAIM_ALREADY_CLAIM_SECONDARY_COLOR**
  - Default: { 0.5, 0, 0, 1 }

- **FABRICATE_CLAIM_ALREADY_CORE_SECONDARY_COLOR**
  - Default: { 0.5, 0, 0, 1 }

- **CONSTRUCTION_MAP_MODE_BUILDING_DEFAULT_COLOR**
  - Default: { 0.43, 0.22, 0.22, 0.25 }
  - Developer comment: Color of states/provinces that can't be built on

- **CONSTRUCTION_MAP_MODE_BUILDING_MAX_LEVEL_COLOR**
  - Default: { 0.05, 0.1, 0.7, 0.4 }
  - Developer comment: Color of states/provinces where current building level is maxed out (max is current max level, not final max level) of a building type

- **CONSTRUCTION_MAP_MODE_BUILDING_LEVEL_LOW_COLOR**
  - Default: { 0.05, 0.22, 0.0, 0.4 }

- **CONSTRUCTION_MAP_MODE_BUILDING_LEVEL_HI_COLOR**
  - Default: { 0.4, 0.9, 0.0, 0.5 }

- **CONSTRUCTION_MAP_MODE_BUILDING_MAX_AMOUNT_QUEUED_COLOR**
  - Default: { 0.0, 0.0, 1.0 }
  - Developer comment: Color of states/provinces when building queue is maxed of a building type

- **CONSTRUCTION_MAP_MODE_BUILDING_QUEUED_COLOR**
  - Default: { 1.0, 0.85, 0.0 }
  - Developer comment: Color of states/provinces when building queue contains one or more of a building type.

- **MAP_MODE_MANPOWER_RANGE_MAX**
  - Default: 20000000
  - Developer comment: When a state has that much manpower, it will be colored with the color MAP_MODE_MANPOWER_RANGE_COLOR_TO. Everything below that will have an interpolated color.

- **MAP_MODE_MANPOWER_RANGE_COLOR_FROM**
  - Default: { 0.2, 0.2, 0.7, 0.18 }
  - Developer comment: Color range for manpower map mode.

- **MAP_MODE_MANPOWER_RANGE_COLOR_TO**
  - Default: { 1, 0.125, 0.0, 0.6 }

- **MAP_MODE_INFRA_RANGE_COLOR_FROM**
  - Default: { 1, 0.125, 0.0, 0.1 }
  - Developer comment: Color range for infrastructure map mode.

- **MAP_MODE_INFRA_RANGE_COLOR_TO**
  - Default: { 0.1, 0.9, 0.1, 0.6 }

- **MAP_MODE_IDEOLOGY_COLOR_TRANSPARENCY**
  - Default: 1
  - Developer comment: In the Ideology map mode, the colors on the map are taken from the scriptable file 00_ideologies.txt for each group. We use them in the interfaces (pie-charts) where transparency is not used, but 100% opaque looks bad on the map. This is a variable to control the transparency of the color.

- **CONSTRUCTION_MAP_MODE_TRANSPARENCY_OVERRIDE**
  - Default: 241
  - Developer comment: When you use gradient borders to defeat the purpose of gradient borders. Larger than 248 seems to make the transparency stronger?

- **PEACE_CONFERENCE_CURRENT_SELECTED_SECONDARY_COLOR**
  - Default: { 0, 0, 1, 0.25 }

- **PEACE_CONFERENCE_SELECTABLE_SECONDARY_COLOR**
  - Default: { 0, 1, 0, 0.25 }

- **PEACE_CONFERENCE_CONTESTED_SECONDARY_COLOR**
  - Default: { 1, 0, 0, 0.25 }

- **PEACE_CONFERENCE_CHANGE_TARGET_TAG_SECONDARY_COLOR**
  - Default: { 0, 0.8, 0.5, 0.25 }

- **PEACE_CONFERENCE_DIFFERENT_STACKABLE_SECONDARY_COLOR**
  - Default: { 1, 1, 0, 0.25 }

- **FACTIONS_COLOR_NOT_MEMBER**
  - Default: { 0.6, 0.6, 0.6, 0.25 }

- **FACTIONS_MEMBER_TRANSPARENCY**
  - Default: 1.0

- **PLAYER_MAPMODE_NOT_SELECTED_COUNTRY_TRANSPARENCY**
  - Default: 0.15
  - Developer comment: How much is the country colors faded out, for countries that are not occupied by the any player.

- **SELECTED_COUNTRY_HIGHLIGHT_THICKNESS_MULT**
  - Default: 1.5
  - Developer comment: When a country is selected (blinking/highlighted) it's borders becomes a bit thicker, to make stand out even more. 1.0 is default thickness.

- **STRATEGIC_MODE_COUNTRY_COLOR_STRIPES_TRANSP**
  - Default: 0.0

- **STRATEGIC_MODE_ENEMY_STRIPES_COLOR**
  - Default: { 0.827, 0.172, 0.184, 0.0 }

- **STRATEGIC_MODE_OUR_STRIPES_COLOR**
  - Default: { 0.427, 0.619, 0.858, 0.0 }

- **STRATEGIC_MODE_ALLY_STRIPES_COLOR**
  - Default: { 0.427, 0.619, 0.858, 0.0 }

- **RADAR_RANGE_STRIPES_COLOR**
  - Default: { 1.0, 1.0, 0.0, 0.14 }

- **RADAR_RANGE_COLOR**
  - Default: { 0.039, 0.627, 0.0, 1.0 }

- **RADAR_RANGE_ALLIED_COLOR**
  - Default: { 0.0, 0.647, 1.0, 1.0 }

- **RADAR_RANGE_SELECTED_COLOR**
  - Default: { 1.0, 1.0, 0.0, 1.0 }

- **RADAR_ROTATION_SPEED**
  - Default: 0.025

- **AIR_RANGE_CAN_ASSIGN_MISSION_STRIPES_COLOR**
  - Default: { 0, 0.8, 0, 0.0 }
  - Developer comment: Stripes over the regions indicating if the currently selected air wings can have assigned mission there or not.

- **AIR_RANGE_CANNOT_ASSIGN_MISSION_STRIPES_COLOR**
  - Default: { 0.8, 0, 0, 0.5 }

- **AIR_RANGE_INDICATOR_DEFAULT_COLOR**
  - Default: { 1.0, 1.0, 0, 1 }
  - Developer comment: On map circle indicating the air wings range.

- **AIR_RANGE_INDICATOR_NO_WINGS_COLOR**
  - Default: { 1.0, 0, 0, 1 }
  - Developer comment: Same as above, but for air wings with no airplanes.

- **AIR_RANGE_INDICATOR_ROTATION_SPEED**
  - Default: 0.001
  - Developer comment: How quickly is that indicator rotating

- **AIR_MISSION_ARROW_ACTIVE_COLOR**
  - Default: { 0, 1.0, 0, 0.5 }
  - Developer comment: Color of the arrow drawn in the strategic air map mode, between the air base and the region for the active missions

- **AIR_MISSION_ARROW_NONACTIVE_COLOR**
  - Default: { 1.0, 1.0, 1.0, 0.2 }
  - Developer comment: Same as above, but for non active missions (when no air wing has any mission active)

- **AIR_MISSION_ARROW_SELECTED_COLOR**
  - Default: { 1.0, 1.0, 0, 0.8 }
  - Developer comment: Same as above, but for currently selected air wings/air bases.

- **AIR_TRANSFER_ARROW_COLOR**
  - Default: { 1, 1, 0, 0.75 }
  - Developer comment: Same as above, but for the arrows drawn between airbases for current transfers

- **NAVAL_REGION_ACCESS_AVOID_COLOR**
  - Default: { 1, 1, 0, 0.35 }
  - Developer comment: Color for the map stripes on naval regions that has set an access level = AVOID

- **NAVAL_REGION_ACCESS_BLOCK_COLOR**
  - Default: { 1, 0, 0, 0.45 }
  - Developer comment: Color for the map stripes on naval regions that has set an access level = BLOCK

- **NAVAL_REGION_FADE_WHEN_FLEET_SELECTED**
  - Default: 0.25
  - Developer comment: How much all region borders (except those with mission assigned to it) are faded out, when a fleet is selected.

- **AIR_REGION_FADE_WHEN_WING_SELECTED**
  - Default: 0.15

- **UI_CONFIGURABLE_SLOT_FROM**
  - Default: 4
  - Developer comment: Mapmode slots range that may be configurable. Indices are 0-based (first slot is 0)

- **UI_CONFIGURABLE_SLOT_TO**
  - Default: 10

- **MAP_MODE_TERRAIN_TRANSPARENCY**
  - Default: 0.5
  - Developer comment: How much transparent are the province colors in the simplified terrain map mode

- **MAP_MODE_NAVAL_TERRAIN_TRANSPARENCY**
  - Default: 0.8
  - Developer comment: How much transparent are the SEA province colors in the simplified terrain map mode

- **MAP_MODE_INTEL_NETWORK_STRENGTH_COLOR_LOW**
  - Default: { 0.1, 0.1, 0.5, 0.2 }
  - Developer comment: Color of a state with the lowest intel network strength

- **MAP_MODE_INTEL_NETWORK_STRENGTH_COLOR_HIGH**
  - Default: { 0.4, 0.3, 0.9, 1.0 }
  - Developer comment: Color of a state with the lowest intel network strength

- **MAP_MODE_INTEL_NETWORK_STRENGTH_QUIET_COLOR_LOW**
  - Default: { 0.1, 0.5, 0.1, 0.2 }
  - Developer comment: Color of a state with the lowest intel network strength in a quiet network

- **MAP_MODE_INTEL_NETWORK_STRENGTH_QUIET_COLOR_HIGH**
  - Default: { 0.4, 0.9, 0.3, 1.0 }
  - Developer comment: Color of a state with the highest possible intel network strength in a quiet network

- **MAP_MODE_INTEL_MAX_HORIZONTAL_STACK**
  - Default: 3
  - Developer comment: How many intel icons can be shown before the More icon appears for Operations

- **RAILWAY_GUN_RANGE_INDICATOR_DEFAULT_COLOR**
  - Default: { 1.0, 1.0, 1.0, 1.0 }
  - Developer comment: On map circle indicating the railway gun bombardment range.

- **RAILWAY_GUN_RANGE_INDICATOR_ROTATION_SPEED**
  - Default: 0.001
  - Developer comment: How fast the indicator is rotating.

- **RAILWAY_GUN_RANGE_STRIPES_COLOR**
  - Default: { 1.0, 0.5, 0.0, 0.2 }
  - Developer comment: Color of the railway gun range stripes (when hovered)

- **OCCUPATION_MAP_MODE_COUNTRY_STRIPE_ALPHA**
  - Default: 0.3
  - Developer comment: alpha of occupied country stripes in occupation map mode

- **OPERATIVE_MAP_MODE_INVALID_COUNTRY_TARGET_TRANSPARENCY**
  - Default: 0.15
  - Developer comment: alpha of country which cannot be targeted by the selected operative mission

- **SUPPLY_MAP_MODE_COUNTRY_BORDER_CAMERA_DISTANCE**
  - Default: 1.0

- **SUPPLY_MAP_MODE_COUNTRY_BORDER_OUTLINE_CUTOFF**
  - Default: 0.973

- **GRADIENT_BORDERS_THICKNESS_SUPPLY_COUNTRY_BORDER**
  - Default: 10.0

- **SUPPLY_COUNTRY_BORDER_PLAYER_COLOR**
  - Default: { 0.1, 0.66, 0.1, 1.0 }

- **SUPPLY_COUNTRY_BORDER_FRIEND_COLOR**
  - Default: { 0.035, 0.426, 0.91, 1.0 }

- **SUPPLY_COUNTRY_BORDER_ACCESS_COLOR**
  - Default: { 0.1, 0.66, 0.1, 1.0 }

- **SUPPLY_MAP_MODE_REACH_COLOR**
  - Default: { 0.0, 0.6, 0.0, 0.4, 1.0, 0.02, 0.2, 0.17, 0.52, 1.0, 0.12, 0.04, 0.17, 0.6, 1.0, 0.2, 0.13, 0.36, 0.65, 1.0, 0.4, 0.11, 0.56, 0.75, 1.0, 0.6, 0.25, 0.71, 0.76, 1.0, 0.8, 0.47, 0.8, 0.73, 1.0, 1.0, 0.6, 0.82, 0.6, 1.0 }
  - Developer comment:
    ```text
    (last shown when supply flow is >= SUPPLY_MAP_MODE_BEST_FLOW_DISPLAY)
    #990066 dark purple
    #332B85 dark purple blue
    #0A2B99 dark blue
    #215CA6 blue
    #1C8FBF light blue
    #40B5C2 teal
    #78CCBA light teal
    #99D199 light green
    ```

- **SUPPLY_MAP_MODE_BEST_FLOW_DISPLAY**
  - Default: 12
  - Developer comment: Which supply cap availibility corresponds to best heatmap color

- **SUPPLY_MAP_MODE_STATUS_COLOR**
  - Default: { 0.0, 0.9, 0.0, 0.0, 1.0, 0.7, 0.98, 0.4, 0.1, 1.0, 1.0, 0.8, 0.64, 0.2, 1.0 }
  - Developer comment:
    ```text
    #E60000 red
    #FA661A orange
    #CCA333 mustard
    ```

- **SUPPLY_STATUS_DISPLAY_THRESHOLD**
  - Default: 0.9
  - Developer comment: at what average supply status we move to show status colors instead of flow

- **SUPPLY_HOVERED_STATE_COLOR_INDEX**
  - Default: 0
  - Developer comment: Border color of hovered state. Refers to the colors in BORDER_COLOR_CUSTOM_HIGHLIGHTS.

- **SUPPLY_HOVERED_PROVINCE_COLOR_INDEX**
  - Default: 4
  - Developer comment: Border color of hovered province. Refers to the colors in BORDER_COLOR_CUSTOM_HIGHLIGHTS.

- **PEACE_HOVERED_STATE_COLOR_INDEX**
  - Default: 3
  - Developer comment: Border color of hovered state in Peace conference. Refers to the colors in BORDER_COLOR_CUSTOM_HIGHLIGHTS.

- **PEACE_CLAIMED_STATE_COLOR_INDEX**
  - Default: 2
  - Developer comment: Border color of claimed states in Peace conference. Refers to the colors in BORDER_COLOR_CUSTOM_HIGHLIGHTS.

- **SELECTION_HOVERED_STATE_COLOR_INDEX_CONTROLLED**
  - Default: 5
  - Developer comment: Border color of hovered controlled states in various select mapmodes. Refers to the colors in BORDER_COLOR_CUSTOM_HIGHLIGHTS.

- **SELECTION_HOVERED_STATE_COLOR_INDEX_FOREIGN**
  - Default: 6
  - Developer comment: Border color of hovered foreign states in various select mapmodes. Refers to the colors in BORDER_COLOR_CUSTOM_HIGHLIGHTS.

## NMapIcons

- **TOP_MAP_ICON**
  - Default: 30

- **INTERPOLATION_SNAP_DISTANCE**
  - Default: 0.3

- **INTEL_MAP_MODE_MAP_ICON_OFFSET**
  - Default: { 12, 40 }
  - Developer comment: Control the offset of the intel map mode map icon (counterintelligence, operatives and operations)

- **COARSE_RAILWAY_GUN_POSITION_OFFSET**
  - Default: { -30, 0 }
  - Developer comment: Coarse railway gun icons will have their world centers offset by this offset

- **DEFAULT_PRIORITY_UNITS_STACK**
  - Default: 10

- **DEFAULT_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **DEFAULT_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **DEFAULT_PRIORITY_RESOURCE**
  - Default: 10

- **DEFAULT_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **DEFAULT_PRIORITY_AIR_BASE**
  - Default: 3

- **DEFAULT_PRIORITY_ROCKET_SITE**
  - Default: 3

- **DEFAULT_PRIORITY_NAVAL_BASE**
  - Default: 3

- **DEFAULT_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **DEFAULT_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **DEFAULT_PRIORITY_LAND_COMBAT**
  - Default: 20

- **DEFAULT_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **DEFAULT_PRIORITY_AIR_MISSION**
  - Default: 13

- **DEFAULT_PRIORITY_SUPPLY**
  - Default: 14

- **DEFAULT_PRIORITY_CAPITAL**
  - Default: 5

- **DEFAULT_PRIORITY_PEACE_COST**
  - Default: 3

- **DEFAULT_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **DEFAULT_PRIORITY_NAVAL_MINES**
  - Default: 13

- **DEFAULT_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **DEFAULT_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **STATES_PRIORITY_UNITS_STACK**
  - Default: 10

- **STATES_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **STATES_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **STATES_PRIORITY_RESOURCE**
  - Default: 10

- **STATES_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **STATES_PRIORITY_AIR_BASE**
  - Default: 3

- **STATES_PRIORITY_ROCKET_SITE**
  - Default: 3

- **STATES_PRIORITY_NAVAL_BASE**
  - Default: 3

- **STATES_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **STATES_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **STATES_PRIORITY_LAND_COMBAT**
  - Default: 20

- **STATES_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **STATES_PRIORITY_AIR_MISSION**
  - Default: 13

- **STATES_PRIORITY_SUPPLY**
  - Default: 14

- **STATES_PRIORITY_CAPITAL**
  - Default: 5

- **STATES_PRIORITY_PEACE_COST**
  - Default: 3

- **STATES_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **STATES_PRIORITY_NAVAL_MINES**
  - Default: 13

- **STATES_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **SUPPLY_AREAS_PRIORITY_UNITS_STACK**
  - Default: 10

- **SUPPLY_AREAS_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **SUPPLY_AREAS_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **SUPPLY_AREAS_PRIORITY_RESOURCE**
  - Default: 10

- **SUPPLY_AREAS_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **SUPPLY_AREAS_PRIORITY_AIR_BASE**
  - Default: 3

- **SUPPLY_AREAS_PRIORITY_ROCKET_SITE**
  - Default: 3

- **SUPPLY_AREAS_PRIORITY_NAVAL_BASE**
  - Default: 3

- **SUPPLY_AREAS_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **SUPPLY_AREAS_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **SUPPLY_AREAS_PRIORITY_LAND_COMBAT**
  - Default: 20

- **SUPPLY_AREAS_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **SUPPLY_AREAS_PRIORITY_AIR_MISSION**
  - Default: 13

- **SUPPLY_AREAS_PRIORITY_SUPPLY**
  - Default: 14

- **SUPPLY_AREAS_PRIORITY_CAPITAL**
  - Default: 5

- **SUPPLY_AREAS_PRIORITY_PEACE_COST**
  - Default: 3

- **SUPPLY_AREAS_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **SUPPLY_AREAS_PRIORITY_NAVAL_MINES**
  - Default: 13

- **SUPPLY_AREAS_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **STRATEGIC_AIR_PRIORITY_UNITS_STACK**
  - Default: 10

- **STRATEGIC_AIR_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **STRATEGIC_AIR_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **STRATEGIC_AIR_PRIORITY_RESOURCE**
  - Default: 10

- **STRATEGIC_AIR_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **STRATEGIC_AIR_PRIORITY_AIR_BASE**
  - Default: 30

- **STRATEGIC_AIR_PRIORITY_ROCKET_SITE**
  - Default: 3

- **STRATEGIC_AIR_PRIORITY_NAVAL_BASE**
  - Default: 3

- **STRATEGIC_AIR_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **STRATEGIC_AIR_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **STRATEGIC_AIR_PRIORITY_LAND_COMBAT**
  - Default: 20

- **STRATEGIC_AIR_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **STRATEGIC_AIR_PRIORITY_AIR_MISSION**
  - Default: 29

- **STRATEGIC_AIR_PRIORITY_SUPPLY**
  - Default: 14

- **STRATEGIC_AIR_PRIORITY_CAPITAL**
  - Default: 5

- **STRATEGIC_AIR_PRIORITY_PEACE_COST**
  - Default: 3

- **STRATEGIC_AIR_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **STRATEGIC_AIR_PRIORITY_NAVAL_MINES**
  - Default: 13

- **STRATEGIC_AIR_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **STRATEGIC_NAVY_PRIORITY_UNITS_STACK**
  - Default: 10

- **STRATEGIC_NAVY_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **STRATEGIC_NAVY_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **STRATEGIC_NAVY_PRIORITY_RESOURCE**
  - Default: 10

- **STRATEGIC_NAVY_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **STRATEGIC_NAVY_PRIORITY_AIR_BASE**
  - Default: 3

- **STRATEGIC_NAVY_PRIORITY_ROCKET_SITE**
  - Default: 3

- **STRATEGIC_NAVY_PRIORITY_NAVAL_BASE**
  - Default: 28

- **STRATEGIC_NAVY_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **STRATEGIC_NAVY_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **STRATEGIC_NAVY_PRIORITY_LAND_COMBAT**
  - Default: 20

- **STRATEGIC_NAVY_PRIORITY_NAVAL_MISSION**
  - Default: 29

- **STRATEGIC_NAVY_PRIORITY_AIR_MISSION**
  - Default: 13

- **STRATEGIC_NAVY_PRIORITY_SUPPLY**
  - Default: 14

- **STRATEGIC_NAVY_PRIORITY_CAPITAL**
  - Default: 5

- **STRATEGIC_NAVY_PRIORITY_PEACE_COST**
  - Default: 3

- **STRATEGIC_NAVY_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **STRATEGIC_NAVY_PRIORITY_NAVAL_MINES**
  - Default: 13

- **STRATEGIC_NAVY_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **RESISTANCE_PRIORITY_UNITS_STACK**
  - Default: 10

- **RESISTANCE_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **RESISTANCE_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **RESISTANCE_PRIORITY_RESOURCE**
  - Default: 10

- **RESISTANCE_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **RESISTANCE_PRIORITY_AIR_BASE**
  - Default: 3

- **RESISTANCE_PRIORITY_ROCKET_SITE**
  - Default: 3

- **RESISTANCE_PRIORITY_NAVAL_BASE**
  - Default: 3

- **RESISTANCE_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **RESISTANCE_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **RESISTANCE_PRIORITY_LAND_COMBAT**
  - Default: 20

- **RESISTANCE_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **RESISTANCE_PRIORITY_AIR_MISSION**
  - Default: 13

- **RESISTANCE_PRIORITY_SUPPLY**
  - Default: 14

- **RESISTANCE_PRIORITY_CAPITAL**
  - Default: 5

- **RESISTANCE_PRIORITY_PEACE_COST**
  - Default: 3

- **RESISTANCE_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **RESISTANCE_PRIORITY_NAVAL_MINES**
  - Default: 13

- **RESISTANCE_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **RESOURCES_PRIORITY_UNITS_STACK**
  - Default: 10

- **RESOURCES_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **RESOURCES_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **RESOURCES_PRIORITY_RESOURCE**
  - Default: 10

- **RESOURCES_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **RESOURCES_PRIORITY_AIR_BASE**
  - Default: 3

- **RESOURCES_PRIORITY_ROCKET_SITE**
  - Default: 3

- **RESOURCES_PRIORITY_NAVAL_BASE**
  - Default: 3

- **RESOURCES_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **RESOURCES_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **RESOURCES_PRIORITY_LAND_COMBAT**
  - Default: 20

- **RESOURCES_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **RESOURCES_PRIORITY_AIR_MISSION**
  - Default: 13

- **RESOURCES_PRIORITY_SUPPLY**
  - Default: 14

- **RESOURCES_PRIORITY_CAPITAL**
  - Default: 5

- **RESOURCES_PRIORITY_PEACE_COST**
  - Default: 3

- **RESOURCES_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **RESOURCES_PRIORITY_NAVAL_MINES**
  - Default: 13

- **RESOURCES_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **DIPLOMACY_PRIORITY_UNITS_STACK**
  - Default: 10

- **DIPLOMACY_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **DIPLOMACY_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **DIPLOMACY_PRIORITY_RESOURCE**
  - Default: 10

- **DIPLOMACY_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **DIPLOMACY_PRIORITY_AIR_BASE**
  - Default: 3

- **DIPLOMACY_PRIORITY_ROCKET_SITE**
  - Default: 3

- **DIPLOMACY_PRIORITY_NAVAL_BASE**
  - Default: 3

- **DIPLOMACY_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **DIPLOMACY_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **DIPLOMACY_PRIORITY_LAND_COMBAT**
  - Default: 20

- **DIPLOMACY_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **DIPLOMACY_PRIORITY_AIR_MISSION**
  - Default: 13

- **DIPLOMACY_PRIORITY_SUPPLY**
  - Default: 14

- **DIPLOMACY_PRIORITY_CAPITAL**
  - Default: 5

- **DIPLOMACY_PRIORITY_PEACE_COST**
  - Default: 3

- **DIPLOMACY_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **DIPLOMACY_PRIORITY_NAVAL_MINES**
  - Default: 13

- **DIPLOMACY_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **FACTIONS_PRIORITY_UNITS_STACK**
  - Default: 10

- **FACTIONS_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **FACTIONS_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **FACTIONS_PRIORITY_RESOURCE**
  - Default: 10

- **FACTIONS_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **FACTIONS_PRIORITY_AIR_BASE**
  - Default: 3

- **FACTIONS_PRIORITY_ROCKET_SITE**
  - Default: 3

- **FACTIONS_PRIORITY_NAVAL_BASE**
  - Default: 3

- **FACTIONS_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **FACTIONS_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **FACTIONS_PRIORITY_LAND_COMBAT**
  - Default: 20

- **FACTIONS_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **FACTIONS_PRIORITY_AIR_MISSION**
  - Default: 13

- **FACTIONS_PRIORITY_SUPPLY**
  - Default: 14

- **FACTIONS_PRIORITY_CAPITAL**
  - Default: 5

- **FACTIONS_PRIORITY_PEACE_COST**
  - Default: 3

- **FACTIONS_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **FACTIONS_PRIORITY_NAVAL_MINES**
  - Default: 13

- **FACTIONS_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **STRATEGIC_REGIONS_PRIORITY_UNITS_STACK**
  - Default: 10

- **STRATEGIC_REGIONS_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **STRATEGIC_REGIONS_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **STRATEGIC_REGIONS_PRIORITY_RESOURCE**
  - Default: 10

- **STRATEGIC_REGIONS_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **STRATEGIC_REGIONS_PRIORITY_AIR_BASE**
  - Default: 3

- **STRATEGIC_REGIONS_PRIORITY_ROCKET_SITE**
  - Default: 3

- **STRATEGIC_REGIONS_PRIORITY_NAVAL_BASE**
  - Default: 3

- **STRATEGIC_REGIONS_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **STRATEGIC_REGIONS_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **STRATEGIC_REGIONS_PRIORITY_LAND_COMBAT**
  - Default: 20

- **STRATEGIC_REGIONS_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **STRATEGIC_REGIONS_PRIORITY_AIR_MISSION**
  - Default: 13

- **STRATEGIC_REGIONS_PRIORITY_SUPPLY**
  - Default: 14

- **STRATEGIC_REGIONS_PRIORITY_CAPITAL**
  - Default: 5

- **STRATEGIC_REGIONS_PRIORITY_PEACE_COST**
  - Default: 3

- **STRATEGIC_REGIONS_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **STRATEGIC_REGIONS_PRIORITY_NAVAL_MINES**
  - Default: 13

- **STRATEGIC_REGIONS_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **DEPLOYMENT_AIR_PRIORITY_UNITS_STACK**
  - Default: 10

- **DEPLOYMENT_AIR_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **DEPLOYMENT_AIR_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **DEPLOYMENT_AIR_PRIORITY_RESOURCE**
  - Default: 10

- **DEPLOYMENT_AIR_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **DEPLOYMENT_AIR_PRIORITY_AIR_BASE**
  - Default: 3

- **DEPLOYMENT_AIR_PRIORITY_ROCKET_SITE**
  - Default: 3

- **DEPLOYMENT_AIR_PRIORITY_NAVAL_BASE**
  - Default: 3

- **DEPLOYMENT_AIR_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **DEPLOYMENT_AIR_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **DEPLOYMENT_AIR_PRIORITY_LAND_COMBAT**
  - Default: 20

- **DEPLOYMENT_AIR_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **DEPLOYMENT_AIR_PRIORITY_AIR_MISSION**
  - Default: 13

- **DEPLOYMENT_AIR_PRIORITY_SUPPLY**
  - Default: 14

- **DEPLOYMENT_AIR_PRIORITY_CAPITAL**
  - Default: 5

- **DEPLOYMENT_AIR_PRIORITY_PEACE_COST**
  - Default: 3

- **DEPLOYMENT_AIR_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **DEPLOYMENT_AIR_PRIORITY_NAVAL_MINES**
  - Default: 13

- **DEPLOYMENT_AIR_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **DEPLOYMENT_NAVY_PRIORITY_UNITS_STACK**
  - Default: 10

- **DEPLOYMENT_NAVY_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **DEPLOYMENT_NAVY_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **DEPLOYMENT_NAVY_PRIORITY_RESOURCE**
  - Default: 10

- **DEPLOYMENT_NAVY_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **DEPLOYMENT_NAVY_PRIORITY_AIR_BASE**
  - Default: 3

- **DEPLOYMENT_NAVY_PRIORITY_ROCKET_SITE**
  - Default: 3

- **DEPLOYMENT_NAVY_PRIORITY_NAVAL_BASE**
  - Default: 3

- **DEPLOYMENT_NAVY_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **DEPLOYMENT_NAVY_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **DEPLOYMENT_NAVY_PRIORITY_LAND_COMBAT**
  - Default: 20

- **DEPLOYMENT_NAVY_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **DEPLOYMENT_NAVY_PRIORITY_AIR_MISSION**
  - Default: 13

- **DEPLOYMENT_NAVY_PRIORITY_SUPPLY**
  - Default: 14

- **DEPLOYMENT_NAVY_PRIORITY_CAPITAL**
  - Default: 5

- **DEPLOYMENT_NAVY_PRIORITY_PEACE_COST**
  - Default: 3

- **DEPLOYMENT_NAVY_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **DEPLOYMENT_NAVY_PRIORITY_NAVAL_MINES**
  - Default: 13

- **DEPLOYMENT_NAVY_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **DEPLOYMENT_MILITARY_PRIORITY_UNITS_STACK**
  - Default: 10

- **DEPLOYMENT_MILITARY_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **DEPLOYMENT_MILITARY_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **DEPLOYMENT_MILITARY_PRIORITY_RESOURCE**
  - Default: 10

- **DEPLOYMENT_MILITARY_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **DEPLOYMENT_MILITARY_PRIORITY_AIR_BASE**
  - Default: 3

- **DEPLOYMENT_MILITARY_PRIORITY_ROCKET_SITE**
  - Default: 3

- **DEPLOYMENT_MILITARY_PRIORITY_NAVAL_BASE**
  - Default: 3

- **DEPLOYMENT_MILITARY_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **DEPLOYMENT_MILITARY_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **DEPLOYMENT_MILITARY_PRIORITY_LAND_COMBAT**
  - Default: 20

- **DEPLOYMENT_MILITARY_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **DEPLOYMENT_MILITARY_PRIORITY_AIR_MISSION**
  - Default: 13

- **DEPLOYMENT_MILITARY_PRIORITY_SUPPLY**
  - Default: 14

- **DEPLOYMENT_MILITARY_PRIORITY_CAPITAL**
  - Default: 5

- **DEPLOYMENT_MILITARY_PRIORITY_PEACE_COST**
  - Default: 3

- **DEPLOYMENT_MILITARY_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **DEPLOYMENT_MILITARY_PRIORITY_NAVAL_MINES**
  - Default: 13

- **DEPLOYMENT_MILITARY_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **PEACE_CONFERENCE_PRIORITY_UNITS_STACK**
  - Default: 10

- **PEACE_CONFERENCE_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **PEACE_CONFERENCE_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **PEACE_CONFERENCE_PRIORITY_RESOURCE**
  - Default: 10

- **PEACE_CONFERENCE_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **PEACE_CONFERENCE_PRIORITY_AIR_BASE**
  - Default: 3

- **PEACE_CONFERENCE_PRIORITY_ROCKET_SITE**
  - Default: 3

- **PEACE_CONFERENCE_PRIORITY_NAVAL_BASE**
  - Default: 3

- **PEACE_CONFERENCE_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **PEACE_CONFERENCE_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **PEACE_CONFERENCE_PRIORITY_LAND_COMBAT**
  - Default: 20

- **PEACE_CONFERENCE_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **PEACE_CONFERENCE_PRIORITY_AIR_MISSION**
  - Default: 13

- **PEACE_CONFERENCE_PRIORITY_SUPPLY**
  - Default: 14

- **PEACE_CONFERENCE_PRIORITY_CAPITAL**
  - Default: 5

- **PEACE_CONFERENCE_PRIORITY_PEACE_COST**
  - Default: 20

- **PEACE_CONFERENCE_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **PEACE_CONFERENCE_PRIORITY_NAVAL_MINES**
  - Default: 13

- **PEACE_CONFERENCE_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **INFRASTRUCTURE_PRIORITY_UNITS_STACK**
  - Default: 10

- **INFRASTRUCTURE_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **INFRASTRUCTURE_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **INFRASTRUCTURE_PRIORITY_RESOURCE**
  - Default: 10

- **INFRASTRUCTURE_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **INFRASTRUCTURE_PRIORITY_AIR_BASE**
  - Default: 3

- **INFRASTRUCTURE_PRIORITY_ROCKET_SITE**
  - Default: 3

- **INFRASTRUCTURE_PRIORITY_NAVAL_BASE**
  - Default: 3

- **INFRASTRUCTURE_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **INFRASTRUCTURE_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **INFRASTRUCTURE_PRIORITY_LAND_COMBAT**
  - Default: 20

- **INFRASTRUCTURE_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **INFRASTRUCTURE_PRIORITY_AIR_MISSION**
  - Default: 13

- **INFRASTRUCTURE_PRIORITY_SUPPLY**
  - Default: 14

- **INFRASTRUCTURE_PRIORITY_CAPITAL**
  - Default: 5

- **INFRASTRUCTURE_PRIORITY_PEACE_COST**
  - Default: 3

- **INFRASTRUCTURE_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **INFRASTRUCTURE_PRIORITY_NAVAL_MINES**
  - Default: 13

- **INFRASTRUCTURE_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_UNITS_STACK**
  - Default: 10

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_RESOURCE**
  - Default: 10

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_AIR_BASE**
  - Default: 3

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_ROCKET_SITE**
  - Default: 3

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_NAVAL_BASE**
  - Default: 3

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_LAND_COMBAT**
  - Default: 20

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_AIR_MISSION**
  - Default: 13

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_SUPPLY**
  - Default: 14

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_CAPITAL**
  - Default: 5

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_PEACE_COST**
  - Default: 3

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_NAVAL_MINES**
  - Default: 13

- **DIPLOMACY_FABRICATE_CLAIM_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **MANPOWER_PRIORITY_UNITS_STACK**
  - Default: 10

- **MANPOWER_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **MANPOWER_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **MANPOWER_PRIORITY_RESOURCE**
  - Default: 10

- **MANPOWER_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **MANPOWER_PRIORITY_AIR_BASE**
  - Default: 3

- **MANPOWER_PRIORITY_ROCKET_SITE**
  - Default: 3

- **MANPOWER_PRIORITY_NAVAL_BASE**
  - Default: 3

- **MANPOWER_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **MANPOWER_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **MANPOWER_PRIORITY_LAND_COMBAT**
  - Default: 20

- **MANPOWER_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **MANPOWER_PRIORITY_AIR_MISSION**
  - Default: 13

- **MANPOWER_PRIORITY_SUPPLY**
  - Default: 14

- **MANPOWER_PRIORITY_CAPITAL**
  - Default: 5

- **MANPOWER_PRIORITY_PEACE_COST**
  - Default: 3

- **MANPOWER_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **MANPOWER_PRIORITY_NAVAL_MINES**
  - Default: 13

- **MANPOWER_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **IDEOLOGY_PRIORITY_UNITS_STACK**
  - Default: 10

- **IDEOLOGY_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **IDEOLOGY_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **IDEOLOGY_PRIORITY_RESOURCE**
  - Default: 10

- **IDEOLOGY_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **IDEOLOGY_PRIORITY_AIR_BASE**
  - Default: 3

- **IDEOLOGY_PRIORITY_ROCKET_SITE**
  - Default: 3

- **IDEOLOGY_PRIORITY_NAVAL_BASE**
  - Default: 3

- **IDEOLOGY_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **IDEOLOGY_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **IDEOLOGY_PRIORITY_LAND_COMBAT**
  - Default: 20

- **IDEOLOGY_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **IDEOLOGY_PRIORITY_AIR_MISSION**
  - Default: 13

- **IDEOLOGY_PRIORITY_SUPPLY**
  - Default: 14

- **IDEOLOGY_PRIORITY_CAPITAL**
  - Default: 5

- **IDEOLOGY_PRIORITY_PEACE_COST**
  - Default: 3

- **IDEOLOGY_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **IDEOLOGY_PRIORITY_NAVAL_MINES**
  - Default: 13

- **IDEOLOGY_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **START_CONSTRUCTION_PRIORITY_UNITS_STACK**
  - Default: 10

- **START_CONSTRUCTION_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **START_CONSTRUCTION_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **START_CONSTRUCTION_PRIORITY_RESOURCE**
  - Default: 10

- **START_CONSTRUCTION_PRIORITY_CONSTRUCTION_INFO**
  - Default: 20

- **START_CONSTRUCTION_PRIORITY_AIR_BASE**
  - Default: 1

- **START_CONSTRUCTION_PRIORITY_ROCKET_SITE**
  - Default: 3

- **START_CONSTRUCTION_PRIORITY_NAVAL_BASE**
  - Default: 1

- **START_CONSTRUCTION_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **START_CONSTRUCTION_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **START_CONSTRUCTION_PRIORITY_LAND_COMBAT**
  - Default: 20

- **START_CONSTRUCTION_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **START_CONSTRUCTION_PRIORITY_AIR_MISSION**
  - Default: 13

- **START_CONSTRUCTION_PRIORITY_SUPPLY**
  - Default: 14

- **START_CONSTRUCTION_PRIORITY_CAPITAL**
  - Default: 5

- **START_CONSTRUCTION_PRIORITY_PEACE_COST**
  - Default: 3

- **START_CONSTRUCTION_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **START_CONSTRUCTION_PRIORITY_NAVAL_MINES**
  - Default: 13

- **START_CONSTRUCTION_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **PLAYERS_PRIORITY_UNITS_STACK**
  - Default: 10

- **PLAYERS_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **PLAYERS_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **PLAYERS_PRIORITY_RESOURCE**
  - Default: 10

- **PLAYERS_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **PLAYERS_PRIORITY_AIR_BASE**
  - Default: 3

- **PLAYERS_PRIORITY_ROCKET_SITE**
  - Default: 3

- **PLAYERS_PRIORITY_NAVAL_BASE**
  - Default: 3

- **PLAYERS_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **PLAYERS_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **PLAYERS_PRIORITY_LAND_COMBAT**
  - Default: 20

- **PLAYERS_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **PLAYERS_PRIORITY_AIR_MISSION**
  - Default: 13

- **PLAYERS_PRIORITY_SUPPLY**
  - Default: 14

- **PLAYERS_PRIORITY_CAPITAL**
  - Default: 5

- **PLAYERS_PRIORITY_PEACE_COST**
  - Default: 3

- **PLAYERS_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **PLAYERS_PRIORITY_NAVAL_MINES**
  - Default: 13

- **PLAYERS_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **OPERATIVES_PRIORITY_UNITS_STACK**
  - Default: 10

- **OPERATIVES_PRIORITY_UNITS_STACK_GROUP**
  - Default: 11

- **OPERATIVES_PRIORITY_VICTORY_POINTS**
  - Default: 5

- **OPERATIVES_PRIORITY_RESOURCE**
  - Default: 10

- **OPERATIVES_PRIORITY_CONSTRUCTION_INFO**
  - Default: 3

- **OPERATIVES_PRIORITY_AIR_BASE**
  - Default: 3

- **OPERATIVES_PRIORITY_ROCKET_SITE**
  - Default: 3

- **OPERATIVES_PRIORITY_NAVAL_BASE**
  - Default: 3

- **OPERATIVES_PRIORITY_NAVAL_COMBAT**
  - Default: 20

- **OPERATIVES_PRIORITY_NAVAL_COMBAT_RESULTS**
  - Default: 19

- **OPERATIVES_PRIORITY_LAND_COMBAT**
  - Default: 20

- **OPERATIVES_PRIORITY_NAVAL_MISSION**
  - Default: 13

- **OPERATIVES_PRIORITY_AIR_MISSION**
  - Default: 13

- **OPERATIVES_PRIORITY_SUPPLY**
  - Default: 14

- **OPERATIVES_PRIORITY_CAPITAL**
  - Default: 25

- **OPERATIVES_PRIORITY_PEACE_COST**
  - Default: 3

- **OPERATIVES_PRIORITY_ADJACENCY_RULE**
  - Default: 3

- **OPERATIVES_PRIORITY_NAVAL_MINES**
  - Default: 13

- **OPERATIVES_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **OPERATIVES_PRIORITY_NAVAL_ACCIDENTS**
  - Default: 13

- **OPERATION_PRIORITY_CAN_START**
  - Default: 1
  - Developer comment: The order of the operation map icons (lower in first)

- **OPERATION_PRIORITY_COMPLETED**
  - Default: 2
  - Developer comment: The order of the operation map icons (lower in first)

- **OPERATION_PRIORITY_IN_PROGRESS**
  - Default: 3
  - Developer comment: The order of the operation map icons (lower in first)

- **OPERATION_PRIORITY_PREPARED**
  - Default: 4
  - Developer comment: The order of the operation map icons (lower in first)

- **OPERATION_PRIORITY_DEFAULT**
  - Default: 5
  - Developer comment: The order of the operation map icons (lower in first)

## NAirGfx

- **AIRPLANES_ANIMATION_GLOBAL_SPEED_PER_GAMESPEED**
  - Default: { 0.22, 0.28, 0.32, 0.38, 0.44, 0.5 }
  - Developer comment: Speed factor for each game speed (begin with paused). Larger value = faster animation.

- **ROCKET_SPEED**
  - Default: 15.0
  - Developer comment: Speed of rockets launched from rocket sites

- **AIRPLANES_CURVE_POINT_DENSITY**
  - Default: 2.0
  - Developer comment: LOWER value = more midpoints in the flight path.

- **AIRPLANES_CURVE_MAX_EXTRAPOLATION**
  - Default: 20.0
  - Developer comment: It's the limit value that avoid making gigantic curves that may happen when flight path is very long.

- **AIRPLANES_CURVE_MIN_ELEVATION**
  - Default: 4.0
  - Developer comment: Minimum height above the ground that the curve will generate it's points. Excludes first and last point (takeoff/landing).

- **AIRPLANES_SCALE_TAKEOFF_DIST**
  - Default: 0.1
  - Developer comment: Until first x% of the flight path, the airplane will scale up.

- **AIRPLANES_SCALE_MIN**
  - Default: 0.1
  - Developer comment: Minimum airplane scale down when takeoff/landing.

- **AIRPLANES_SCALE_LANDING_DIST**
  - Default: 0.9
  - Developer comment: After last x% of the flight path, the airplane will scale down.

- **AIRPLANES_SMOOTH_INTERPOLATION_MOVE**
  - Default: 0.13
  - Developer comment: How smooth is the movement interpolation.

- **AIRPLANES_SMOOTH_INTERPOLATION_TURN**
  - Default: 0.12
  - Developer comment: How smooth is the turning interpolation.

- **AIRPLANES_BANK_STRENGTH**
  - Default: 210.0
  - Developer comment: Multiplier of how much the curve affects the wings banking. (angle limited by the following value)

- **AIRPLANES_BANK_ANGLE_LIMIT**
  - Default: 55.0
  - Developer comment: Bank angle limit.

- **AIRPLANES_GROUND_COLLISION_OFFSET_Y**
  - Default: 0.0
  - Developer comment: Set's the height (Y) offset before 3d airplanes disappear after going to the ground.

- **AIRPLANES_GROUND_EXPLOSION_TIME_DELAY**
  - Default: 0.6
  - Developer comment: Time in seconds to play explosion animation when plane hit ground before the plane entity is deleted

- **AIRPLANES_1_FIGHTER_PATROL_ANIM**
  - Default: 1
  - Developer comment: Number of fighters needed for a single instance of this animation

- **AIRPLANES_3_FIGHTER_PATROL_ANIM**
  - Default: 3
  - Developer comment: Number of fighters needed for a single instance of this animation

- **AIRPLANES_1_BOMBER_BOMBING_ANIM**
  - Default: 1
  - Developer comment: Number of bombers needed for a single instance of this animation

- **AIRPLANES_3_BOMBER_BOMBING_ANIM**
  - Default: 3
  - Developer comment: Number of bombers needed for a single instance of this animation

- **AIRPLANES_1_FIGHTER_VS_1_FIGHTER_ANIM**
  - Default: 1
  - Developer comment: Number of fighters needed per side for a single instance of this animation

- **AIRPLANES_3_FIGHTER_VS_3_FIGHTER_ANIM**
  - Default: 3
  - Developer comment: Number of bombers needed per side for a single instance of this animation

- **AIRPLANES_1_TRANSPORT_SUPPLY_ANIM**
  - Default: 1
  - Developer comment: Number of planes needed for a single instance of this animation

- **AIRPLANES_3_TRANSPORT_SUPPLY_ANIM**
  - Default: 3
  - Developer comment: Number of planes needed for a single instance of this animation

- **AIRPLANES_1_SCOUT_PLANE_PATROL_ANIM**
  - Default: 1

- **AIRPLANES_3_SCOUT_PLANE_PATROL_ANIM**
  - Default: 3

- **STRAT_BOMBER_FIREBOMB_THRESHOLD**
  - Default: 42.0
  - Developer comment: If a strategic bomber has a strat_bomber value >= this, then the firebombing animation will be used

- **STRAT_BOMBER_CARPETBOMB_THRESHOLD**
  - Default: 16.0
  - Developer comment: If a strategic bomber has a strat_bomber value >= this, then the carpet-bombing animation will be used

- **BOMBERS_DIVISION_FACTOR**
  - Default: 30
  - Developer comment: Number of bombers in a strategic region will be divided by this factor.

- **MISSILES_DIVISION_FACTOR**
  - Default: 60
  - Developer comment: Number of missiles shown in a strategic region will be divided by this factor.

- **FIGHTERS_DIVISION_FACTOR**
  - Default: 30
  - Developer comment: Number of missiles shown in a strategic region will be divided by this factor.

- **SCOUT_PLANE_DIVISION_FACTOR**
  - Default: 30
  - Developer comment: Number of missiles shown in a strategic region will be divided by this factor.

- **TRANSPORT_DIVISION_FACTOR**
  - Default: 30

- **MAX_MISSILE_BOMBING_SCENARIOS**
  - Default: 2
  - Developer comment: Max number of missile bombing scenarios in a strategic region.

- **MAX_PATROL_SCENARIOS**
  - Default: 2
  - Developer comment: Max number of patrol scenarios in a strategic region.

- **MAX_BOMBING_SCENARIOS**
  - Default: 2
  - Developer comment: Max number of bombings scenarios in a strategic region.

- **MAX_DOGFIGHTS_SCENARIOS**
  - Default: 3
  - Developer comment: Max number of dogfight scenarios in a strategic region.

- **MAX_TRANSPORT_SCENARIOS**
  - Default: 2
  - Developer comment: Max number of transport scenarios in a strategic region

- **MAX_TRAINING_SCENARIOS**
  - Default: 2
  - Developer comment: Max number of training scenarios in a strategic region

- **MAX_SCOUT_SCENARIOS**
  - Default: 2

## NGraphics

- **COUNTER_MODE_ALLEGIANCE_OURS**
  - Default: { 0.32, 0.71, 0.39, 1.0 }

- **COUNTER_MODE_ALLEGIANCE_ALLIED**
  - Default: { 0.31, 0.65, 0.94, 1.0 }

- **COUNTER_MODE_ALLEGIANCE_ENEMY**
  - Default: { 0.91, 0.3, 0.3, 1.0 }

- **COUNTER_MODE_ALLEGIANCE_OTHER**
  - Default: { 0.8, 0.8, 0.8, 1.0 }

- **MAX_NUMBER_OF_TEXTURES**
  - Default: 10000
  - Developer comment: increase if you have more than this textures

- **MIN_TRAIN_WAGON_COUNT**
  - Default: 3

- **MAX_TRAIN_WAGON_COUNT**
  - Default: 6

- **RAILWAY_BRIDGE_ENTITY**
  - Default: "bridge_railway_entity"

- **RAILWAY_BRIDGE_LARGE_ENTITY**
  - Default: "bridge_railway_large_entity"

- **RAILWAY_Y_OFFSET**
  - Default: 0.9
  - Developer comment: Railways are offset by this amount vertically from the map

- **RAILWAY_BRIDGE_Y_OFFSET**
  - Default: 0.6
  - Developer comment: Railway bridges are offset by this amount vertically from the map

- **RAILWAY_BRIDGE_WIDTH**
  - Default: 4.0
  - Developer comment: Railways will have straight segments of this length for regular bridges

- **RAILWAY_BRIDGE_LARGE_WIDTH**
  - Default: 4.5
  - Developer comment: Railways will have straight segments of this length for large bridges

- **RAILWAY_BRIDGE_GAP_WIDTH**
  - Default: 2.4
  - Developer comment: Railways will have gaps of this length for regular bridges

- **RAILWAY_BRIDGE_GAP_LARGE_WIDTH**
  - Default: 2.6
  - Developer comment: Railways will have gaps of this length for large bridges

- **TRAIN_MAP_SPEED**
  - Default: 3.0
  - Developer comment: Trains will move at this relative speed. This has no gameplay implications. Changing this value (originally 4.0) may cause audio effects to lose sync with animation.

- **TUNNELBANA_TIMETABLE**
  - Default: { 9200, 12000 }
  - Developer comment: Frequency range in milliseconds for regular train service. Adjust this if changing speed to avoid LONGTRAIN

- **MAX_MESHES_LOADED_PER_FRAME**
  - Default: 10

- **MESH_POPUP_SCALE_UP_SPEED**
  - Default: 5.0

- **MESH_POPUP_SCALE_DOWN_SPEED**
  - Default: 2.1

- **SHIP_POPUP_SCALE_DOWN_SPEED**
  - Default: 4.1

- **PORT_SHIP_OFFSET**
  - Default: 2.0

- **SHIP_IN_PORT_SCALE**
  - Default: 0.25

- **MAP_BUILDINGS_SHRINK_DISTANCE**
  - Default: 180

- **CITY_SPRAWL_SHRINK_DISTANCE**
  - Default: 220.0
  - Developer comment: Start shrinking at this distance

- **DRAW_MAP_OBJECTS_CUTOFF**
  - Default: 550.0
  - Developer comment: Remove map objects at this distance

- **PROVINCE_NAME_DRAW_DISTANCE**
  - Default: 500.0
  - Developer comment: Remove province names beyond this distance

- **DIRECTION_POINTER_DRAW_DISTANCE**
  - Default: 1200.0
  - Developer comment: Direction pointer arrow will not be drawn beyond this distance

- **DIRECTION_POINTER_INTERPOLATION_SPEED**
  - Default: 0.275
  - Developer comment: How fast the arrow is interpolating

- **DIRECTION_POINTER_SCREEN_AREA_MAX**
  - Default: 0.935
  - Developer comment: The moment when the arrow snaps to the province (value is in DOT PRODUCT) 0.9-0.99

- **DIRECTION_POINTER_SCREEN_AREA_MIN**
  - Default: 0.91
  - Developer comment: The moment when the arrow starts getting closer to the target before it snaps.

- **DIRECTION_POINTER_SIZE_MIN**
  - Default: 0.9
  - Developer comment: Size of the arrow interpolated dependly on camera distance

- **DIRECTION_POINTER_SIZE_MAX**
  - Default: 10.0

- **DIRECTION_POINTER_GROUND_OFFSET**
  - Default: 5.0
  - Developer comment: Offset Y above the ground for arrow to point at

- **LIGHT_DIRECTION_X**
  - Default: -1.0

- **LIGHT_DIRECTION_Y**
  - Default: -1.0

- **LIGHT_DIRECTION_Z**
  - Default: 0.5

- **LIGHT_SHADOW_DIRECTION_X**
  - Default: -5.0

- **LIGHT_SHADOW_DIRECTION_Y**
  - Default: -8.0

- **LIGHT_SHADOW_DIRECTION_Z**
  - Default: 5.0

- **LIGHT_HDR_RANGE**
  - Default: 1.0

- **BORDER_WIDTH**
  - Default: 1.5

- **PROVINCE_BORDER_FADE_NEAR**
  - Default: 200

- **PROVINCE_BORDER_FADE_FAR**
  - Default: 300

- **STATE_BORDER_FADE_NEAR**
  - Default: 400

- **STATE_BORDER_FADE_FAR**
  - Default: 500

- **LAND_UNIT_MOVEMENT_SPEED**
  - Default: 12

- **NAVAL_UNIT_MOVEMENT_SPEED**
  - Default: 12

- **ARROW_MOVEMENT_SPEED**
  - Default: 2

- **DRAW_COUNTRY_NAMES_CUTOFF**
  - Default: 260
  - Developer comment: Cutoff for drawing country names on the map

- **TRADEROUTE_SMOOTHNESS**
  - Default: 0.65

- **TRADEROUTE_SMOOTHEN_PASSES**
  - Default: 2

- **SUPPLYFLOW_SMOOTHNESS**
  - Default: 0.25

- **SUPPLYFLOW_SMOOTHEN_PASSES**
  - Default: 2

- **SNAPPED_OFF_FRONT_SMOOTHNESS**
  - Default: 0.5

- **SNAPPED_OFF_FRONT_SMOOTHEN_PASSES**
  - Default: 2

- **ROOT_FRONT_SMOOTHNESS**
  - Default: 0.5

- **ROOT_FRONT_SMOOTHEN_PASSES**
  - Default: 1

- **ROOT_FRONT_OFFSET**
  - Default: 1.5
  - Developer comment: How far the defensive line is offset from the front.

- **ROOT_FRONT_MAX_INTERSECTION_TESTS_FRONT**
  - Default: 30
  - Developer comment: How many points before the current one to check for intersections against (optimization)

- **ROOT_FRONT_MAX_INTERSECTION_TESTS_ORDER**
  - Default: 25
  - Developer comment: How many points before the current one to check for intersections against (optimization)

- **ORDER_FRONT_MAX_OFFSETS**
  - Default: 4
  - Developer comment: Max amount, the overlapping defensive lines can offset from the border.

- **ORDER_FRONT_SMOOTHNESS**
  - Default: 0.5

- **ORDER_FRONT_SMOOTHEN_PASSES**
  - Default: 2

- **ORDER_MOVE_SMOOTHNESS**
  - Default: 0.99

- **ORDER_MOVE_SMOOTHEN_PASSES**
  - Default: 2

- **UNIT_TURN_SPEED**
  - Default: 3

- **BORDER_COLOR_SELECTION_STATE_R**
  - Default: 1.0

- **BORDER_COLOR_SELECTION_STATE_G**
  - Default: 0.62

- **BORDER_COLOR_SELECTION_STATE_B**
  - Default: 0.33

- **BORDER_COLOR_SELECTION_STATE_A**
  - Default: 1.0

- **BORDER_COLOR_SELECTION_SUPPLY_AREA_R**
  - Default: 0.6

- **BORDER_COLOR_SELECTION_SUPPLY_AREA_G**
  - Default: 0.2

- **BORDER_COLOR_SELECTION_SUPPLY_AREA_B**
  - Default: 0.6

- **BORDER_COLOR_SELECTION_SUPPLY_AREA_A**
  - Default: 1.0

- **BORDER_COLOR_SELECTION_ADJACENCY_RULE_AREA_R**
  - Default: 0.0

- **BORDER_COLOR_SELECTION_ADJACENCY_RULE_AREA_G**
  - Default: 1.0

- **BORDER_COLOR_SELECTION_ADJACENCY_RULE_AREA_B**
  - Default: 1.0

- **BORDER_COLOR_SELECTION_ADJACENCY_RULE_AREA_A**
  - Default: 1.0

- **BORDER_COLOR_SELECTION_BUILDING_AREA_R**
  - Default: 1.0

- **BORDER_COLOR_SELECTION_BUILDING_AREA_G**
  - Default: 1.0

- **BORDER_COLOR_SELECTION_BUILDING_AREA_B**
  - Default: 1.0

- **BORDER_COLOR_SELECTION_BUILDING_AREA_A**
  - Default: 1.0

- **BORDER_COLOR_SELECTION_PROVINCE_R**
  - Default: 1.0

- **BORDER_COLOR_SELECTION_PROVINCE_G**
  - Default: 0.8

- **BORDER_COLOR_SELECTION_PROVINCE_B**
  - Default: 0.0

- **BORDER_COLOR_SELECTION_PROVINCE_A**
  - Default: 1.0

- **BORDER_COLOR_CUSTOM_HIGHLIGHTS**
  - Default: { 0.0, 0.61, 0.75, 1.0, 1.0, 0.06, 0.0, 1.0, 0.1, 0.6, 0.2, 1.0, 0.8, 0.3, 0.0, 1.0, 0.0, 0.4, 0.8, 1.0, 0.3, 0.9, 0.3, 0.8, 0.7, 0.7, 0.0, 1.0 }
  - Developer comment:
    ```text
    [[ Groups of 4 numbers are RGBA.
    If two colors are both active on a border, (because one province is
    part of a group using one color, and the other province is part
    of another group), then the color that comes first in this list
    is the color that will be used. ]]
    0: mouse hover
    1: bad, while active
    2: good, while active
    3: bad, while passive
    4: good, while passive
    5: controlled, neutral positive
    6: not ours, neutral negative
    ```

- **BORDER_COLOR_TUTORIAL_HIGHLIGHT_R**
  - Default: 0.0

- **BORDER_COLOR_TUTORIAL_HIGHLIGHT_G**
  - Default: 0.61

- **BORDER_COLOR_TUTORIAL_HIGHLIGHT_B**
  - Default: 0.75

- **BORDER_COLOR_TUTORIAL_HIGHLIGHT_A**
  - Default: 1.0

- **BORDER_COLOR_DEMILITARIZED_R**
  - Default: 1.0

- **BORDER_COLOR_DEMILITARIZED_G**
  - Default: 0.06

- **BORDER_COLOR_DEMILITARIZED_B**
  - Default: 0.0

- **BORDER_COLOR_DEMILITARIZED_A**
  - Default: 0.9

- **BORDER_COLOR_BORDER_CONFLICT_EDGE_R**
  - Default: 1.0

- **BORDER_COLOR_BORDER_CONFLICT_EDGE_G**
  - Default: 0.2

- **BORDER_COLOR_BORDER_CONFLICT_EDGE_B**
  - Default: 0.0

- **BORDER_COLOR_BORDER_CONFLICT_EDGE_A**
  - Default: 1.0

- **BORDER_COLOR_BORDER_CONFLICT_NON_EDGE_R**
  - Default: 0.7

- **BORDER_COLOR_BORDER_CONFLICT_NON_EDGE_G**
  - Default: 1.0

- **BORDER_COLOR_BORDER_CONFLICT_NON_EDGE_B**
  - Default: 0.0

- **BORDER_COLOR_BORDER_CONFLICT_NON_EDGE_A**
  - Default: 0.9

- **DRAW_REFRACTIONS_CUTOFF**
  - Default: 250

- **DRAW_SHADOWS_CUTOFF**
  - Default: 400

- **DRAW_SHADOWS_FADE_LENGTH**
  - Default: 50

- **DRAW_FOW_CUTOFF**
  - Default: 400

- **DRAW_FOW_FADE_LENGTH**
  - Default: 350

- **GRADIENT_BORDERS_FIELD_COUNTRY_REFRESH**
  - Default: 10
  - Developer comment: When country changes it's size by X provinces, then it refresh it's thickness and rebuilds all provinces

- **GRADIENT_BORDERS_FIELD_COUNTRY_LOW**
  - Default: 300.0
  - Developer comment: country area in sum of pixels ...

- **GRADIENT_BORDERS_FIELD_COUNTRY_HIGH**
  - Default: 9000.0
  - Developer comment: ... the value is squared, so fe. country of size 100x100pix = 10000

- **GRADIENT_BORDERS_THICKNESS_COUNTRY_LOW**
  - Default: 5.0
  - Developer comment: thickness in pixels

- **GRADIENT_BORDERS_COUNTRY_CENTER_THICKNESS**
  - Default: 2.0
  - Developer comment: The center gradient is linear 1/255 per pixel for this many pixels

- **GRADIENT_BORDERS_THICKNESS_COUNTRY_HIGH**
  - Default: 25.0

- **GRADIENT_BORDERS_THICKNESS_STATE**
  - Default: 5.0

- **GRADIENT_BORDERS_THICKNESS_RESISTANCE**
  - Default: 5.0

- **GRADIENT_BORDERS_THICKNESS_INTEL_LEDGER**
  - Default: 5.0

- **GRADIENT_BORDERS_THICKNESS_SUPPLY_AREA_A**
  - Default: 2.0

- **GRADIENT_BORDERS_THICKNESS_SUPPLY_AREA_B**
  - Default: 20.0

- **GRADIENT_BORDERS_THICKNESS_STRATEGIC_REGIONS**
  - Default: 150.0

- **GRADIENT_BORDERS_THICKNESS_DIPLOMACY**
  - Default: 12.0

- **GRADIENT_BORDERS_THICKNESS_DIPLOMACY_ON_INTEL_LEDGER**
  - Default: 3.0

- **GRADIENT_BORDERS_THICKNESS_PEACE_CONFERENCE_A**
  - Default: 3.0
  - Developer comment: transparency at 0 up until A

- **GRADIENT_BORDERS_THICKNESS_PEACE_CONFERENCE_B**
  - Default: 6.0
  - Developer comment: increasing transparency up to 100% when at B

- **GRADIENT_BORDERS_OUTLINE_CUTOFF_COUNTRY**
  - Default: 0.973
  - Developer comment: Magic number to balance cutoff on edges without neighbor

- **GRADIENT_BORDERS_OUTLINE_CUTOFF_DIPLOMACY**
  - Default: 0.973

- **GRADIENT_BORDERS_OUTLINE_CUTOFF_DIPLOMACY_ON_INTEL_LEDGER**
  - Default: 0.973

- **GRADIENT_BORDERS_OUTLINE_CUTOFF_STATE**
  - Default: 0.973

- **GRADIENT_BORDERS_OUTLINE_CUTOFF_SUPPLY_AREA**
  - Default: 0.973

- **GRADIENT_BORDERS_OUTLINE_CUTOFF_STRATEGIC_REGIONS**
  - Default: 0.98

- **GRADIENT_BORDERS_OUTLINE_CUTOFF_RESISTANCE**
  - Default: 0.973

- **GRADIENT_BORDERS_OUTLINE_CUTOFF_FACTIONS**
  - Default: 0.973

- **GRADIENT_BORDERS_OUTLINE_CUTOFF_INTEL_LEDGER**
  - Default: 0.973

- **GRADIENT_BORDERS_OUTLINE_CUTOFF_PEACE_CONFERENCE**
  - Default: 0.973

- **GRADIENT_BORDERS_CAMERA_DISTANCE_OVERRIDE_COUNTRY**
  - Default: 0.0
  - Developer comment: 0 to 1 value for override filling when camera zooms in/out. 0 = override disabled

- **GRADIENT_BORDERS_CAMERA_DISTANCE_OVERRIDE_STATE**
  - Default: 0.4

- **GRADIENT_BORDERS_CAMERA_DISTANCE_OVERRIDE_SUPPLY_AREA**
  - Default: 1.0

- **GRADIENT_BORDERS_CAMERA_DISTANCE_OVERRIDE_STRATEGIC_REGIONS**
  - Default: 1.0

- **GRADIENT_BORDERS_CAMERA_DISTANCE_OVERRIDE_RESISTANCE**
  - Default: 0.35

- **GRADIENT_BORDERS_CAMERA_DISTANCE_OVERRIDE_FACTIONS**
  - Default: 0.0

- **GRADIENT_BORDERS_CAMERA_DISTANCE_OVERRIDE_TERRAIN**
  - Default: 0.39

- **GRADIENT_BORDERS_CAMERA_DISTANCE_OVERRIDE_INTEL_LEDGER**
  - Default: 0.2

- **GRADIENT_BORDERS_CAMERA_DISTANCE_OVERRIDE_DIPLOMACY**
  - Default: 0.0

- **GRADIENT_BORDERS_CAMERA_DISTANCE_OVERRIDE_DIPLOMACY_ON_INTEL_LEDGER**
  - Default: 1.0

- **GRADIENT_BORDERS_CAMERA_DISTANCE_OVERRIDE_PEACE_CONFERENCE**
  - Default: 1.0

- **GRADIENT_BORDERS_ACTIVATE_FOR_PEACE_CONFERENCE**
  - Default: false

- **GRADIENT_BORDERS_ONE_COLOR_FOR_PEACE_CONFERENCE**
  - Default: { -1.0, -1.0, -1.0, -1.0 }
  - Developer comment: all gradient will have this color. if { -1.0, -1.0, -1.0, -1.0 } then use Negotiator MapColor

- **GRADIENT_BORDERS_OPTIMIZATION_RANGE**
  - Default: 30.0
  - Developer comment: smaller value = faster gradient borders but may have artifacts on large provinces (value to balance)

- **GRADIENT_BORDERS_REFRESH_FREQ**
  - Default: 0.12
  - Developer comment: how frequent is gradient borders repainting (optimization for high-speed gameplay)

- **STRATEGIC_AIR_COLOR_BAD**
  - Default: { 0.8, 0, 0, 1 }
  - Developer comment: rgb

- **STRATEGIC_AIR_COLOR_GOOD**
  - Default: { 0, 0.8, 0, 1 }

- **STRATEGIC_AIR_COLOR_AVERAGE**
  - Default: { 0.8, 0.8, 0, 1 }

- **STRATEGIC_AIR_COLOR_NEUTRAL**
  - Default: { 140.0/255, 131.0/255, 119.0/255, 1 }

- **STRATEGIC_AIR_COLOR_GOOD_WHILE_HIGHLIGHTING_HOLD**
  - Default: { 0, 0.8, 0, 1 }

- **STRATEGIC_AIR_COLOR_AVERAGE_WHILE_HIGHLIGHTING_HOLD**
  - Default: { 0.8, 0.8, 0, 1 }

- **STRATEGIC_AIR_COLOR_NEUTRAL_WHILE_HIGHLIGHTING_HOLD**
  - Default: { 140.0/255, 131.0/255, 119.0/255, 1 }

- **STRATEGIC_NAVY_COLOR_NEUTRAL**
  - Default: { 0.2, 0.25, 0.35, 0.5 }
  - Developer comment: zones without missions

- **STRATEGIC_NAVY_COLOR_ON_HOLD**
  - Default: { 0.2, 0.5, 0.6, 0.5 }
  - Developer comment: zones with only hold mission

- **STRATEGIC_NAVY_COLOR_ON_HOLD_HIGHLIGHTED**
  - Default: { 0.2, 0.6, 0.7, 0.5 }
  - Developer comment: zones with with only hold missions with taskforces selected

- **STRATEGIC_NAVY_COLOR_BAD**
  - Default: { 0.8, 0, 0, 1 }
  - Developer comment: zones has missions with bad suppremacy

- **STRATEGIC_NAVY_COLOR_GOOD**
  - Default: { 0, 0.8, 0, 1 }
  - Developer comment: zones has missions with good suppremacy

- **STRATEGIC_NAVY_COLOR_AVERAGE**
  - Default: { 0.8, 0.8, 0, 1 }
  - Developer comment: zones has missions with average suppremacy

- **STRATEGIC_NAVY_NO_TASKFORCES_ASSIGNED**
  - Default: { 0.9, 0.3, 0.3, 1 }
  - Developer comment: zones has fleets assigned to them but no no taskforce can reach it or not enough taskforce to cover that region

- **STRATEGIC_NAVY_COLOR_BAD_WHILE_HIGHLIGHTING_HOLD**
  - Default: { 0.7, 0.0, 0.4, 0.5 }
  - Developer comment: zones has missions with bad suppremacy on highlighted regions with a hold mission selected

- **STRATEGIC_NAVY_COLOR_GOOD_WHILE_HIGHLIGHTING_HOLD**
  - Default: { 0, 0.6, 0.5, 1 }
  - Developer comment: zones has missions with good suppremacy on highlighted regions with a hold mission selected

- **STRATEGIC_NAVY_COLOR_AVERAGE_WHILE_HIGHLIGHTING_HOLD**
  - Default: { 0.5, 0.5, 0.6, 1 }
  - Developer comment: zones has missions with average suppremacy on highlighted regions with a hold mission selected

- **RESISTANCE_COLOR_NONE**
  - Default: { 0.4, 0.4, 0.6, 0.5 }
  - Developer comment: rgba

- **RESISTANCE_COLOR_GOOD**
  - Default: { 0.8, 0.8, 0, 0.3 }
  - Developer comment: rgba

- **RESISTANCE_COLOR_AVERAGE**
  - Default: { 0.8, 0.4, 0, 0.5 }

- **RESISTANCE_COLOR_BAD**
  - Default: { 0.8, 0, 0, 0.9 }

- **CONSTRUCTION_CONVERSION_COLOR**
  - Default: { 0.9, 0.9, 0.3, 0.1 }

- **CONSTRUCTION_CONVERSION_IN_PROGRESS_COLOR**
  - Default: { 0.3, 0.3, 0.9, 0.1 }

- **VIRTUAL_BATTLEPLANS_COLOR**
  - Default: { 0.2, 1.0, 0.2, 1 }

- **ALLIED_BATTLEPLANS_COLOR**
  - Default: { 0.3, 0.4, 1.0, 1 }

- **OFFENSIVE_PING_CIRCLE_COLOR**
  - Default: { 0.64, 0.48, 0.35 }

- **DEFENSIVE_PING_CIRCLE_COLOR**
  - Default: { 0.4, 0.55, 0.66 }

- **GMT_OFFSET**
  - Default: 2793
  - Developer comment: X position on map, of Greenwitch GMT+0 (see also in shader daynight.fxh)

- **DAY_NIGHT_FEATHER**
  - Default: 0.024
  - Developer comment: Feather value between complete darkness and the day (see also in shader daynight.fxh)

- **SOUTH_POLE_OFFSET**
  - Default: 0.17
  - Developer comment: Our map is missing big parts of globe on north and south (see also in shader daynight.fxh)

- **NORTH_POLE_OFFSET**
  - Default: 0.93

- **COUNTRY_FLAG_TEX_WIDTH**
  - Default: 82
  - Developer comment: Expected texture size

- **COUNTRY_FLAG_TEX_HEIGHT**
  - Default: 52

- **COUNTRY_FLAG_TEX_MAX_SIZE**
  - Default: 256
  - Developer comment: Tweak dependly on amount of countries. Must be power of 2. No more then 2048.

- **COUNTRY_FLAG_MEDIUM_TEX_WIDTH**
  - Default: 41

- **COUNTRY_FLAG_MEDIUM_TEX_HEIGHT**
  - Default: 26

- **COUNTRY_FLAG_MEDIUM_TEX_MAX_SIZE**
  - Default: 1024
  - Developer comment: Tweak dependly on amount of countries. Must be power of 2. No more then 2048.

- **COUNTRY_FLAG_SMALL_TEX_WIDTH**
  - Default: 10

- **COUNTRY_FLAG_SMALL_TEX_HEIGHT**
  - Default: 7

- **COUNTRY_FLAG_SMALL_TEX_MAX_SIZE**
  - Default: 256
  - Developer comment: Tweak dependly on amount of countries. Must be power of 2. No more then 2048.

- **VICTORY_POINT_LEVELS**
  - Default: 3

- **VICTORY_POINT_MAP_ICON_AFTER**
  - Default: { 0, 9, 20 }
  - Developer comment: After this amount of VP the map icon becomes bigger dot.

- **VICTORY_POINT_MAP_ICON_CAPITAL_CUTOFF_MAX**
  - Default: 1000.0
  - Developer comment: Capitals are special snowflakes, they need their own number

- **VICTORY_POINT_MAP_ICON_TEXT_CUTOFF**
  - Default: { 150, 250, 500 }
  - Developer comment: At what camera distance the VP name text disappears.

- **VICTORY_POINT_MAP_ICON_TEXT_CUTOFF_MIN**
  - Default: 100.0
  - Developer comment: Min range for victory point text

- **VICTORY_POINT_MAP_ICON_TEXT_CUTOFF_MAX**
  - Default: 800.0
  - Developer comment: Max range for victory point text

- **VICTORY_POINT_MAP_ICON_DOT_CUTOFF_MIN**
  - Default: 100.0
  - Developer comment: Min range for victory point dot

- **VICTORY_POINT_MAP_ICON_DOT_CUTOFF_MAX**
  - Default: 1000.0
  - Developer comment: Max range for victory point text

- **VICTORY_POINT_MAP_ICON_MAX_VICTORY_POINTS_FOR_PERCENT**
  - Default: 22
  - Developer comment: Default max value for point on the above range. It doesn't matter much if the VP value exceeds this, it'll be treated as max.

- **AIRBASE_ICON_DISTANCE_CUTOFF**
  - Default: 900
  - Developer comment: At what distance air bases are hidden

- **NAVALBASE_ICON_DISTANCE_CUTOFF**
  - Default: 900
  - Developer comment: 1300, -- At what distance naval bases are hidden

- **RADAR_ICON_DISTANCE_CUTOFF**
  - Default: 1100
  - Developer comment: At what distance the radars are hidden

- **RESOURCE_MAP_ICON_TEXT_CUTOFF**
  - Default: 800
  - Developer comment: At what camera distance the resource name/amount text disappears.

- **RESISTANCE_MAP_ICON_MODIFIERS_DISTANCE_CUTOFF**
  - Default: 500
  - Developer comment: At what camera distance the resistance/compliance map icon modifiers are hidden

- **RESISTANCE_MAP_ICON_DISTANCE_CUTOFF**
  - Default: 1200
  - Developer comment: At what camera distance the resistance/compliance map icons are hidden

- **PROVINCE_ANIM_TEXT_DISTANCE_CUTOFF**
  - Default: 500

- **CAPITAL_ICON_CUTOFF**
  - Default: 1100
  - Developer comment: At what camera distance capital icons disappears

- **UNITS_DISTANCE_CUTOFF**
  - Default: 120

- **SHIPS_DISTANCE_CUTOFF**
  - Default: 240

- **UNIT_ARROW_DISTANCE_CUTOFF**
  - Default: 875

- **UNITS_ICONS_DISTANCE_CUTOFF**
  - Default: 900

- **NAVAL_COMBAT_DISTANCE_CUTOFF**
  - Default: 1500

- **ADJACENCY_RULE_DISTANCE_CUTOFF**
  - Default: 1700

- **LAND_COMBAT_DISTANCE_CUTOFF**
  - Default: 1500

- **PROV_CONSTRUCTION_ICON_DISTANCE_CUTOFF**
  - Default: 400

- **STATE_CONSTRUCTION_ICON_DISTANCE_CUTOFF**
  - Default: 800

- **DECISION_MAP_ICON_DISTANCE_CUTOFF**
  - Default: 1000

- **DECISION_MAP_ICON_DEPTH_PRIORITY**
  - Default: 50

- **NAVAL_MISSION_TASK_FORCES_GROUP_BY_ALLEGIANCE_CUTOFF**
  - Default: 500

- **NAVAL_MISSION_ICONS_DISTANCE_CUTOFF**
  - Default: 900
  - Developer comment: 1300,

- **NAVAL_MINES_DISTANCE_CUTOFF**
  - Default: 800

- **CRYPTOLOGY_MAP_ICON_DISTANCE_CUTOFF**
  - Default: 1000

- **PEACE_CONFERENCE_MAP_ICON_DISTANCE_CUTOFF**
  - Default: 500

- **NAVAL_MINES_CLUMPING**
  - Default: 58
  - Developer comment: The higher value, the more likely the 3d naval mines will clamp together

- **NAVAL_MINES_CLUMP_NEAR_TERRITORY**
  - Default: 25
  - Developer comment: Higher chance to spawn 3d naval mine near our territory

- **NAVAL_MINES_COUNT_TO_VISUAL_ASPECT**
  - Default: 0.1
  - Developer comment: How many in-game-naval-mines is one visual 3d naval mine?

- **MAP_ICONS_GROUP_CAM_DISTANCE**
  - Default: 90.0
  - Developer comment: camera distance at which the icons begin to group up

- **MAP_ICONS_STATE_GROUP_CAM_DISTANCE**
  - Default: 180.0
  - Developer comment: Camera distance at which the icons begin to group up on state level

- **MAP_ICONS_STRATEGIC_GROUP_CAM_DISTANCE**
  - Default: 350
  - Developer comment: second camera distance at which the icons begin to group up

- **MAP_ICONS_STRATEGIC_AREA_HUGE**
  - Default: 220

- **MAP_ICONS_STATE_HUGE**
  - Default: 100

- **MAPICON_GROUP_PASSES**
  - Default: 20
  - Developer comment: how many mapicons get processed per frame for grouping. more = quicker response, fewer = better performance

- **MAP_ICONS_GROUP_SPLIT_SELECTED_LIMIT**
  - Default: 12
  - Developer comment: Maximum number of units selected that will cause icon stacks to split

- **MAP_ICONS_COARSE_COUNTRY_GROUPING_DISTANCE**
  - Default: 350
  - Developer comment: Distance at which icon grouping becomes very coarse and merges different types of units

- **MAP_ICONS_COARSE_COUNTRY_GROUPING_DISTANCE_STRATEGIC**
  - Default: 350
  - Developer comment: Distance at which icon grouping becomes very coarse and merges different types of units for strategic mapmodes

- **RIVER_FADE_FROM**
  - Default: 20.0
  - Developer comment: the last river endings got faded out, X distance from the ending...

- **RIVER_FADE_TO**
  - Default: 3.0

- **TOOLTIP_DELAYED_DELAY**
  - Default: 1
  - Developer comment: How long before showing delayed tooltip.

- **TOOLTIP_SHOW_DELAY**
  - Default: 0.05
  - Developer comment: How long before showing delayed tooltip.

- **TOOLTIP_HIDE_DELAY**
  - Default: 0.05
  - Developer comment: How long before showing delayed tooltip.

- **INTEL_LEDGER_CIVILIAN_ICON_STATE_CUTOFF**
  - Default: 250.0

- **INTEL_LEDGER_CIVILIAN_ICON_REGION_CUTOFF**
  - Default: 700.0

- **RAILWAY_CAMERA_CUTOFF**
  - Default: 200.0
  - Developer comment: railways are cut off above this camera height

- **RAILWAY_CAMERA_CUTOFF_SPEED**
  - Default: 3.0
  - Developer comment: railways fade in/out speed

- **DIVISION_NAMES_GROUP_MAX_TOOLTIP_ENTRIES**
  - Default: 15
  - Developer comment: Max entries to display the names in the tooltip, when mouse over the division-names-group in the division template designer.

- **NAMES_GROUP_MAX_NAME_LIST_ENTRIES**
  - Default: 25
  - Developer comment: Max example name entries in ship and railway gun name list in production menu

- **WEATHER_DISTANCE_CUTOFF**
  - Default: 1500
  - Developer comment: At what distance weather effects are hidden

- **WEATHER_DISTANCE_FADE_LENGTH**
  - Default: 400
  - Developer comment: How far the fade out distance should be

- **WEATHER_ZOOM_IN_CUTOFF**
  - Default: 358
  - Developer comment: At what distance weather effects are faded out the most when zooming in

- **WEATHER_ZOOM_IN_FADE_LENGTH**
  - Default: 220
  - Developer comment: How far the zoom in fade out distance should be

- **WEATHER_ZOOM_IN_FADE_FACTOR**
  - Default: 0.0
  - Developer comment: How much the weather effects should fade out when maximum zoomed in

- **WEATHER_PLAYBACK_RATE**
  - Default: 0.15
  - Developer comment: Playback rate at maximum distance

- **WEATHER_PLAYBACK_RATE_CUTOFF**
  - Default: 500
  - Developer comment: Playback rate maximum distance

- **WEATHER_PLAYBACK_RATE_LENGTH**
  - Default: 200
  - Developer comment: For how long to fade between normal playback rate and maximum distance playback rate

- **POSTEFFECT_PER_PROVINCE_MIN_SNOW**
  - Default: 0.1

- **POSTEFFECT_PER_PROVINCE_MAX_SNOW**
  - Default: 0.2

- **POSTEFFECT_TOTAL_MIN_SNOW**
  - Default: 0.0

- **POSTEFFECT_TOTAL_MAX_SNOW**
  - Default: 0.05

- **POSTEFFECT_FEATHER_MIN_DISTANCE**
  - Default: 300.0

- **POSTEFFECT_FEATHER_MAX_DISTANCE**
  - Default: 2000.0

- **POSTEFFECT_FEATHER_AT_MIN**
  - Default: 0.03

- **POSTEFFECT_FEATHER_AT_MAX**
  - Default: 0.8

- **LAND_COMBAT_BALANCED_COLOR**
  - Default: { 1.0, 1.0, 0.0, 1.0 }

- **LAND_COMBAT_LOSING_COLOR**
  - Default: { 1.0, 0.0, 0.0, 1.0 }

- **LAND_COMBAT_WINNING_COLOR**
  - Default: { 0.0, 1.0, 0.0, 1.0 }

- **BLOOM_WIDTH**
  - Default: 1.5
  - Developer comment: bloom configuration

- **BLOOM_SCALE**
  - Default: 0.9
  - Developer comment: BLOOM_WIDTH = 1.0, -- night

- **BRIGHT_THRESHOLD**
  - Default: 0.4
  - Developer comment: BLOOM_SCALE = 3.0, -- night

- **EMISSIVE_BLOOM_STRENGTH**
  - Default: 1.0
  - Developer comment: BRIGHT_THRESHOLD = 0.9, -- night

- **MIN_HDR_ADJUSTMENT**
  - Default: 0.5
  - Developer comment: 0.18 0.7  är hur mkt den anpassar sig till mörka områden, mindre värde -> mer mörkerseen

- **MAX_HDR_ADJUSTMENT**
  - Default: 1.0
  - Developer comment: 0.8 0.8 jätte högt värde så ser du bra trots att du står inuti solen och tittar.

- **HDR_ADJUSTMENT_SPEED**
  - Default: 15.0
  - Developer comment: 6

- **TONE_MAP_MIDDLE_GREY**
  - Default: 0.5
  - Developer comment: 0.7

- **TONE_MAP_LUMINANCE_WHITE**
  - Default: 1.0

- **MOON_HEIGHT**
  - Default: 600
  - Developer comment: higher means softer shadows and more intense light

- **SUN_HEIGHT**
  - Default: 600
  - Developer comment: higher means softer shadows and more intense light

- **MOON_HEIGHT_WATER**
  - Default: 550
  - Developer comment: higher means softer shadows and more intense light

- **SUN_HEIGHT_WATER**
  - Default: 5000
  - Developer comment: higher means softer shadows and more intense light

- **MOON_LATITUDE**
  - Default: 0
  - Developer comment: NOT USED

- **SUN_LATITUDE**
  - Default: 848

- **SECOND_MOON_LATITUDE**
  - Default: 100
  - Developer comment: Used to put a "fake" sun/moon on the other side of the globe to hide the seem that would otherwise appear there

- **SECOND_SUN_LATITUDE**
  - Default: 100

- **AMBIENT_LIGHT_POS_X**
  - Default: { 0.2, 0.2, 0.2 }
  - Developer comment:
    ```text
    hsv color ambient light
    right
    ```

- **AMBIENT_LIGHT_NEG_X**
  - Default: { 0.4, 0.1, 0.6 }
  - Developer comment: left

- **AMBIENT_LIGHT_POS_Y**
  - Default: { 0.0, 0.0, 0.0 }
  - Developer comment: kills everything

- **AMBIENT_LIGHT_NEG_Y**
  - Default: { 0.35, 0.2, 0.0 }
  - Developer comment: from under

- **AMBIENT_LIGHT_POS_Z**
  - Default: { 0.6, 0.2, 0.924 }
  - Developer comment: top

- **AMBIENT_LIGHT_NEG_Z**
  - Default: { 0.55, 0.1, 0.9 }
  - Developer comment: bottom

- **SUN_DIFFUSE_COLOR**
  - Default: { 0.14, 0.0, 1.0 }

- **SUN_INTENSITY**
  - Default: 1.0
  - Developer comment: 0.4

- **SUN_SPECULAR_INTENSITY**
  - Default: 1.0

- **MOON_DIFFUSE_COLOR**
  - Default: { 0.58, 0.5, 1.0 }

- **MOON_INTENSITY**
  - Default: 2.5

- **CUBEMAP_INTENSITY**
  - Default: 1.0

- **TREE_FADE_NEAR**
  - Default: 250.0

- **TREE_FADE_FAR**
  - Default: 350.0

- **TRADE_ROUTE_NUM_CONVOYS_SCALE_FACTOR**
  - Default: 0.3

- **TRADE_ROUTE_MAX_NUM_CONVOYS**
  - Default: 4

- **TRADE_ROUTE_CONVOY_SPEED**
  - Default: 0.6

- **TRADE_ROUTE_CONVOY_SLEEP_TIME**
  - Default: 3.0

- **TRADE_ROUTE_CONVOY_ROUTE_OFFSET**
  - Default: 0.5

- **SHIP_IN_MISSION_SPEED**
  - Default: 2.5

- **SHIP_IN_MISSION_TURN_RADIUS**
  - Default: 5.0

- **SHIP_IN_MISSION_TARGET_SIZE**
  - Default: 0.5

- **SHIP_IN_MISSION_SCALE**
  - Default: 0.6

- **TRADE_ROUTE_LINE_OFFSET**
  - Default: 0.5

- **TRADE_ROUTE_MAX_LINES**
  - Default: 6

- **TRADE_ROUTE_BAD_EFFICIENCY_THRESHOLD**
  - Default: 0.8

- **TRADE_ROUTE_REGIONAL_BAD_EFFICIENCY_THRESHOLD**
  - Default: 0.9

- **TRADE_ROUTE_BAD_EFFICIENCY_ROUTE_COLOR**
  - Default: { 1.0, 0.7, 0.5, 0.75 }

- **TRADE_ROUTE_BAD_EFFICIENCY_HOTSPOT_COLOR**
  - Default: { 1.0, 0.0, 0.0, 0.75 }

- **TRADE_ROUTE_PRODUCTION_TRANSFER_COLOR**
  - Default: { 0.0, 0.5, 1.0, 0.75 }

- **TRADE_ROUTE_SUPPLIES_TRANSFER_COLOR**
  - Default: { 1.0, 1.0, 1.0, 0.75 }

- **TRADE_ROUTE_RESOURCE_EXPORT_COLOR**
  - Default: { 0.7, 1.0, 0.5, 0.75 }

- **TRADE_ROUTE_RESOURCE_IMPORT_COLOR**
  - Default: { 0.2, 0.9, 1.0, 0.75 }

- **TRADE_ROUTE_LEND_LEASE_EXPORT_COLOR**
  - Default: { 0.5, 1.0, 0.0, 0.75 }

- **TRADE_ROUTE_LEND_LEASE_IMPORT_COLOR**
  - Default: { 0.5, 1.0, 0.0, 0.75 }

- **TRADE_ROUTE_INTERNATIONAL_MARKET_COLOR**
  - Default: { 0.0, 1.0, 0.0, 0.75 }

- **TRAIT_GRID_COLUMN_OFFSET**
  - Default: 3

- **TRAIT_GRID_COLUMN_WIDTH**
  - Default: 208

- **TRAIT_GRID_ROW_SHIFT**
  - Default: 48

- **TRAIT_LINE_ASSIGNED_COLOR**
  - Default: { 0.47, 0.93, 0.65 }
  - Developer comment:
    ```text
    - Colors used for the trait trees (MIO and character trait trees)
    Color for parent dependency lines when the parent is assigned.
    ```

- **TRAIT_LINE_NON_ASSIGNED_COLOR**
  - Default: { 0.67, 0.75, 0.93 }
  - Developer comment: Color for parent dependency lines when the parent is not assigned assigned.

- **TRAIT_LINE_HIGHLIGHT_COLOR**
  - Default: { 1.0, 1.0, 0.0 }
  - Developer comment: Color for parent dependency lines to the parents when hovering over a trait.

- **TRAIT_INVALID_FOR_ASSIGNMENT_COLOR**
  - Default: { 0.8, 0.3, 0.3 }

- **PRIDE_OF_THE_FLEET_MODULATE**
  - Default: { 1.0, 0.95, 0.0, 1.0 }
  - Developer comment: pride of the fleet color

- **RAILWAY_MAP_ARROW_THIN_LEVEL_THRESHOLD**
  - Default: 1
  - Developer comment: Railway level 1 uses thin map arrow in supply map mode

- **RAILWAY_MAP_ARROW_MEDIUM_LEVEL_THRESHOLD**
  - Default: 3
  - Developer comment: Railway level 2-3 uses medium map arrow in supply map mode

- **RAILWAY_MAP_ARROW_THICK_LEVEL_THRESHOLD**
  - Default: 5
  - Developer comment: Railway level 4-5 uses thick map arrow in supply map mode

- **RAILWAY_MAP_ARROW_COLOR_DEFAULT**
  - Default: { 1.0, 1.0, 1.0, 1.0 }
  - Developer comment: white, default railway maparrow color

- **RAILWAY_MAP_ARROW_COLOR_CONSTRUCTION**
  - Default: { 1.0, 0.8, 0.0, 1.0 }
  - Developer comment: orange, railways that are currently under construction

- **RAILWAY_MAP_ARROW_COLOR_CONSTRUCTION_VALID**
  - Default: { 0.957, 0.871, 0.51, 1.0 }
  - Developer comment: yellow, in constructionmode, railways that are valid to build

- **RAILWAY_MAP_ARROW_COLOR_CONSTRUCTION_INVALID**
  - Default: { 1.0, 0.0, 0.0, 1.0 }
  - Developer comment: red, in constructionmode, railways that are invalid to build

- **RAILWAY_MAP_ARROW_COLOR_HIGHLIGHTED**
  - Default: { 0.957, 0.871, 0.51, 1.0 }
  - Developer comment: yellow, highlighted railways, e.g when selecting a hub and showing the route back to the capital

- **RAILWAY_MAP_ARROW_COLOR_HIGHLIGHTED_DAMAGED**
  - Default: { 1.0, 1.0, 0.2, 1.0 }
  - Developer comment: color of highlighted railways which were damaged

- **RAILWAY_MAP_ARROW_COLOR_HIGHLIGHTED_ONCOOLDOWN**
  - Default: { 1.0, 0.2, 1.0, 1.0 }
  - Developer comment: color of highlighted railways which are on cooldown (captured recently)

- **RAILWAY_MAP_ARROW_COLOR_HIGHLIGHTED_CONSTRUCTION**
  - Default: { 0.957, 0.871, 0.51, 1.0 }
  - Developer comment: orange, shown for highlighted railways that are under construction

- **RAILWAY_MAP_ARROW_COLOR_HIGHLIGHTED_BOTTLENECK**
  - Default: { 0.902, 0.38, 0.4, 1.0 }
  - Developer comment: red, shown for railways that are the bottleneck when highlighting

- **RAILWAY_MAP_ARROW_COLOR_HIGHLIGHTED_BOTTLENECK_MAXLEVEL**
  - Default: { 0.761, 0.647, 0.812, 1.0 }
  - Developer comment: purple, shown for maxlevel railways that are the bottleneck when highlighting

- **RAILWAY_MAP_ARROW_COLOR_DAMAGED**
  - Default: { 0.8, 0.8, 0.0, 1.0 }
  - Developer comment: color of railways which were damaged and gives penalty to move for railway guns

- **RAILWAY_MAP_ARROW_COLOR_ONCOOLDOWN**
  - Default: { 0.5, 0.5, 0.5, 1.0 }
  - Developer comment: color of railways which are on cooldown (captured recently)

- **RIVER_SUPPLY_MAP_ARROW_COLOR**
  - Default: { 0.8, 0.8, 1.0, 0.8 }

- **FLOWING_RIVER_SUPPLY_MAP_ARROW_COLOR**
  - Default: { 0.8, 0.8, 1.0, 0.8 }

- **SUPPLY_TO_CONSUMERS_MAP_ARROW_COLOR**
  - Default: { 1.0, 1.0, 1.0, 1.0 }
  - Developer comment: Currently overwritte in code...

- **SUPPLY_TO_CONSUMERS_MAP_ARROW_TRANSPARENCY**
  - Default: 0.8

- **NODE_FLOW_IN_CURRENT_RANGE_COLOR**
  - Default: { 0.68235, 0.0039, 0.4941, 0.55 }
  - Developer comment:
    ```text
    When holding shift in supply map mode with a node selected, color provinces which are in range of the node
    At current motorization level
    ```

- **NODE_FLOW_IN_HALF_RANGE_COLOR**
  - Default: { 0.9686, 0.4078, 0.6314, 0.6 }
  - Developer comment: At Half Motorization, if currently set to less than that

- **NODE_FLOW_IN_FULL_RANGE_COLOR**
  - Default: { 0.9843, 0.7059, 0.7255, 0.4 }
  - Developer comment: At Full Motorization, if currently set to less than that

- **RAILWAY_ICON_SHIFT**
  - Default: { 0.0, 0.0, 0.0 }

- **SUPPLY_ICON_SHIFT**
  - Default: { 0.0, 0.0, 0.0 }

- **SUPPLY_ICON_SWITCH**
  - Default: 200

- **SUPPLY_ICON_CUTOFF**
  - Default: 900.0
  - Developer comment: total supply icon cutoff distance for all

- **SUPPLY_ICON_UNUSED_CUTOFF**
  - Default: 400.0
  - Developer comment: where we stop showing unused nodes

- **SUPPLY_ICON_NUMBERS_CUTOFF**
  - Default: 400.0
  - Developer comment: where we stop showing numbers on hubs (ignored for selected and problem hubs)

- **SUPPLY_ICON_OK_CUTOFF**
  - Default: 750.0
  - Developer comment: where we stop showing nodes with no issues, e.g non-red

- **SUPPLY_ICON_DISCONNECTED_CUTOFF**
  - Default: 500.0
  - Developer comment: where we stop showing disconnected nodes

- **SUPPLY_ICON_END_CUTOFF**
  - Default: 200.0
  - Developer comment: where we stop showing line end icons

- **RAILWAY_ICON_CUTOFF**
  - Default: 900.0

- **SUPPLY_SELECTED_NODE_COLOR**
  - Default: { 0.0, 1.0, 1.0, 1.0 }

- **SUPPLY_CAPITAL_COLOR**
  - Default: { 1.0, 0.7, 0.0, 1.0 }

- **SUPPLY_NAVAL_NODE_COLOR**
  - Default: { 0.1, 0.6, 0.8, 1.0 }

- **SUPPLY_LAND_NODE_COLOR**
  - Default: { 0.5, 0.8, 0.5, 1.0 }

- **SUPPLY_CONSUMER_ARROW_HEIGHT_TO_LEN**
  - Default: 0.1

- **SUPPLY_CONSUMER_ARROW_HEIGHT_MAX**
  - Default: 4.0

- **SUPPLY_UNIT_COUNTER_SHOW_THRESHOLD**
  - Default: 0.5
  - Developer comment: At what supply threshold will the normal crate be shown on unit counters

- **SUPPLY_UNIT_COUNTER_LOW_THRESHOLD**
  - Default: 0.35
  - Developer comment: At what supply threshold will the orange crate be shown on unit counters

- **SUPPLY_UNIT_COUNTER_VERY_LOW_THRESHOLD**
  - Default: 0.2
  - Developer comment: At what supply threshold will the red crate with ! will be shown on unit counters

- **COUP_GREEN**
  - Default: { 0.0, 1.0, 0.0, 1.0 }

- **COUP_RED**
  - Default: { 1.0, 0.0, 0.0, 1.0 }

- **FRIEND_COLOR**
  - Default: { 0.7, 0.9, 0.7 }
  - Developer comment: unit on-map interface modulate colors

- **ENEMY_COLOR**
  - Default: { 1.0, 0.7, 0.7 }

- **NEUTRAL_COLOR**
  - Default: { 1.0, 1.0, 1.0 }

- **COUNTRY_COLOR_HUE_MODIFIER**
  - Default: 0.0

- **COUNTRY_COLOR_SATURATION_MODIFIER**
  - Default: 0.6

- **COUNTRY_COLOR_BRIGHTNESS_MODIFIER**
  - Default: 0.8

- **COUNTRY_UI_COLOR_HUE_MODIFIER**
  - Default: 0.0

- **COUNTRY_UI_COLOR_SATURATION_MODIFIER**
  - Default: 1.0

- **COUNTRY_UI_COLOR_BRIGHTNESS_MODIFIER**
  - Default: 1.0

- **COMMANDGROUP_PRESET_COLORS_HSV**
  - Default: { 90.0/360.0, 0.95, 0.86, 60.0/360.0, 0.95, 0.86, 30.0/360.0, 0.95, 0.86, 0.0/360.0, 0.95, 0.86, 330.0/360.0, 0.95, 0.86, 300.0/360.0, 0.95, 0.86, 270.0/360.0, 0.95, 0.86, 240.0/360.0, 0.95, 0.86, 210.0/360.0, 0.95, 0.86, 180.0/360.0, 0.95, 0.86 }

- **CAMERA_OUTSIDE_MAP_DISTANCE_TOP**
  - Default: 200.0

- **CAMERA_OUTSIDE_MAP_DISTANCE_BOTTOM**
  - Default: 200.0

- **CAMERA_ZOOM_SPEED**
  - Default: 50

- **CAMERA_ZOOM_KEY_SCALE**
  - Default: 0.02

- **CAMERA_ZOOM_SPEED_DISTANCE_MULT**
  - Default: 6.0
  - Developer comment: Zoom speed multiplier. When camera is max zoome out, the zooming in speed will get 100% of CAMERA_ZOOM_SPEED_DISTANCE_MULT zooming speed.

- **ORDERS_MOUSE_INTERSECT_DISTANCE_MULT**
  - Default: 2.6
  - Developer comment: For balancing the collision distance with painted arrows and fronts.

- **FRONTS_MOUSE_INTERSECT_DISTANCE_MULT**
  - Default: 6.6
  - Developer comment: For balancing the collision distance with painted arrows and fronts.

- **MOVE_ORDERS_MOUSE_INTERSECT_DISTANCE_MULT**
  - Default: 0.5
  - Developer comment: For balancing the collision distance with painted arrows and fronts.

- **TRADE_ROUTE_INTERSECT_DISTANCE_MULT**
  - Default: 10.0
  - Developer comment: For balancing the collision distance with painted arrows and trade routes.

- **RAILWAY_INTERSECT_DISTANCE_MULT**
  - Default: 3.0
  - Developer comment: For balancing the collision distance with painted arrows and railways.

- **MINIMUM_PROVINCE_SIZE_IN_PIXELS**
  - Default: 8
  - Developer comment: Provinces that are smaller than that are just making the game unplayable. It doesn't affect the game, just informs in the error.log

- **NATIONAL_FOCUS_SHINE_DISTANCE_SCALE**
  - Default: 0.03

- **NATIONAL_FOCUS_PULSE_BASE**
  - Default: 10.0

- **NATIONAL_FOCUS_PULSE_RANDOM**
  - Default: 10.0

- **POLITICAL_GRID_SMALL_BOX_LIMIT**
  - Default: 6
  - Developer comment: Limit for gridbox in political view before it will be replaced with extended gridbox

- **SETUP_SPIRIT_GRID_BOX_LIMIT**
  - Default: 3
  - Developer comment: Limit for gridbox in game setup before it will be replaced with extended gridbox

- **POLITICAL_PULSE_BASE**
  - Default: 10.0

- **POLITICAL_PULSE_RANDOM**
  - Default: 10.0

- **STRATEGIC_REGION_ZOOM_HEIGHT**
  - Default: 300.0
  - Developer comment: zooming to a strategic region will make you zoom this further from map

- **ARROW_PARADROP_HEIGHT_TO_LEN**
  - Default: 0.3

- **ARROW_PARADROP_HEIGHT_MAX**
  - Default: 11.0

- **ARROW_MIN_TEXT_POINTS_LIMIT**
  - Default: 10
  - Developer comment: Amount of points when arrow gets first detailed text

- **ARROW_EXT_TEXT_POINTS_LIMIT**
  - Default: 20
  - Developer comment: Amount of points when arrow gets extended detailed text

- **ARMY_DEFENSIVE_LINE_BUTTON_SIZE**
  - Default: 0.7
  - Developer comment: The size of the "edit" button drawn at the endings of the def.lines (for army)

- **ARMY_GROUP_DEFENSIVE_LINE_BUTTON_SIZE**
  - Default: 0.9
  - Developer comment: The size of the "edit" button drawn at the endings of the def.lines (for army group)

- **SHOW_FOREIGN_SUPPLY_BELOW**
  - Default: 300.0
  - Developer comment: Below this camera height all supply icons will be shown

- **SHOW_ONLY_PATH_ABOVE**
  - Default: 500.0
  - Developer comment: Above this only supply icons in the currently shown path are shown

- **ACCLIMATIZATION_CAMO_SHOW_AT**
  - Default: 0.5
  - Developer comment: The moment at which the division gains enough acclimatization to change it's model to the camouflage one.

- **ACCLIMATIZATION_CAMO_SHOW_WHEN_IN_STATE**
  - Default: 0.2
  - Developer comment: The troops camouflage can swap (to the one from acclim.) not only when snow/desert is in the location we are in, but also when % of provinces in current state has snow/desert.

- **INTEL_NETWORK_VALID_TARGET_STRIPE_COLOR**
  - Default: { 0.1, 0.5, 0.8, 1.0 }
  - Developer comment: Color of the stripes of painted over a valid state to start building an intel network

- **INTEL_NETWORK_VALID_COUNTRY_TARGET_STRIPE_COLOR**
  - Default: { 0.1, 0.8, 0.5, 0.5 }
  - Developer comment: Color of the stripes painted over valid countries

- **OCCUPATION_RESISTANCE_NON_INITIALIZED_COLOR**
  - Default: { 1.0, 1.0, 1.0, 0.05 }
  - Developer comment: player owned state color with no resistance

- **OCCUPATION_RESISTANCE_MAP_MODE_COLORS**
  - Default: { 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.1, 30.0, 1.0, 1.0, 0.0, 0.3, 100.0, 1.0, 0.0, 0.0, 0.3 }
  - Developer comment:
    ```text
    color that will be used in resistance/compliance map mode
    first value is resistance/compliance level, next 4 values are color rgba
    the color will be lerped in between two closest colors
    ```

- **OCCUPATION_COMPLIANCE_MAP_MODE_COLORS**
  - Default: { 0.0, 0.3, 0.6, 0.6, 0.05, 0.0, 0.3, 0.7, 1.0, 0.05, 10.0, 0.3, 0.7, 1.0, 0.2, 50.0, 0.3, 0.7, 1.0, 0.3, 100.0, 0.3, 0.9, 1.0, 0.5 }

- **INTEL_LEDGER_ARMY_FORT_LEVEL_COLORS**
  - Default: { 0.0, 0.3, 0.3, 0.3, 0.2, 0.0, 0.7, 0.7, 0.2, 0.3, 1.0, 0.7, 0.2, 0.2, 0.5 }

- **INTEL_LEDGER_NAVAL_FORT_LEVEL_COLORS**
  - Default: { 0.0, 0.3, 0.3, 0.3, 0.2, 0.0, 0.7, 0.7, 0.2, 0.3, 1.0, 0.7, 0.2, 0.2, 0.5 }

- **TEMPERATURE_MAP_MODE_COLORS**
  - Default: { -35.0, 0.0, 0.0, 0.5, 1.0, -25.0, 0.0, 0.0, 1.0, 1.0, -10.0, 0.0, 0.7, 1.0, 1.0, 0.0, 0.0, 1.0, 0.45, 0.45, 15.0, 1.0, 1.0, 0.0, 1.0, 25.0, 1.0, 0.65, 0.0, 1.0, 30.0, 1.0, 0.0, 0.0, 1.0, 35.0, 0.5, 0.0, 0.0, 1.0 }

- **RAILWAY_GUN_ASSIGNMENTS_MAP_MODE_COLORS**
  - Default: { 0.0, 1.0, 0.0, 0.0, 1.0, 0.25, 1.0, 0.65, 0.0, 1.0, 0.75, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.45, 0.45 }

- **INTEL_LEDGER_NAVY_REGION_COLOR_WITH_MISSION**
  - Default: { 0.7, 0.7, 0.7, 0.9 }

- **INTEL_LEDGER_NAVY_REGION_COLOR_WITH_MISSION_AND_TASKFORCES_IN_REGION**
  - Default: { 0.8, 0.8, 0.4, 0.9 }

- **INTEL_LEDGER_AIR_REGION_COLOR**
  - Default: { 0.8, 0.8, 0.4, 0.9 }

- **INTEL_LEDGER_GRAPH_RED**
  - Default: { 1.0, 0.0, 0.0, 1.0 }

- **INTEL_LEDGER_GRAPH_GREEN**
  - Default: { 0.0, 1.0, 0.0, 1.0 }

- **DEFAULT_NUDGE_FLOATING_HARBOR_DIST**
  - Default: 7.0
  - Developer comment: Default distance of floating harbors from the coast in pixels, for nudger

## NInterface

- **MAX_NO_FACTION_FILTER_BUTTONS**
  - Default: 40
  - Developer comment: Max number of faction filter buttons that can be generated in diplomacy view.

- **LOGISTICS_PAST_WEEK**
  - Default: 7
  - Developer comment: Number of days from the past (including current day) we want logistics data for (Max 30 days)

- **COMBAT_SOME_PIERCING**
  - Default: 0.25
  - Developer comment: How many % of enemy units the unit have to pierce in order for the some piercing icon to be displayed

- **COMBAT_GOOD_PIERCING**
  - Default: 0.6
  - Developer comment: How many % of enemy units the unit have to pierce in order for the good piercing icon to be displayed

- **COMBAT_SOME_ARMOR**
  - Default: 0.25
  - Developer comment: How many % of enemy units have to be unable to pierce the unit in order for the some armor icon to be displayed

- **COMBAT_GOOD_ARMOR**
  - Default: 0.6
  - Developer comment: How many % of enemy units have to be unable to pierce the unit in order for the good armor icon to be displayed

- **MIN_FOCUS_TREE_ZOOM**
  - Default: 0.2
  - Developer comment: min zoom in scale

- **MAX_FOCUS_TREE_ZOOM**
  - Default: 1.0
  - Developer comment: max zoom out scale

- **FOCUS_TREE_ZOOM_SPEED**
  - Default: 0.16
  - Developer comment: zooming speed

- **FOCUS_TREE_ZOOM_FACTOR**
  - Default: 0.5
  - Developer comment: zooming factor that will be factored while player scrolls too fast

- **TOOLTIP_SCREEN_LEFT_OFFSET_X**
  - Default: 0
  - Developer comment: Tooltip offset on x axis from left screen border

- **TOOLTIP_SCREEN_RIGHT_OFFSET_X**
  - Default: 0
  - Developer comment: Tooltip offset on x axis from right screen border

- **TOOLTIP_SCREEN_TOP_OFFSET_Y**
  - Default: 0
  - Developer comment: Tooltip offset on y axism from top screen border

- **TOOLTIP_SCREEN_BOTTOM_OFFSET_Y**
  - Default: 0
  - Developer comment: Tooltip offset on y axis from bottom screen border

- **NO_COMBATS_COLOR**
  - Default: { 0.0, 0.0, 0.8 }
  - Developer comment: Color for icons if all combats are successful

- **SUCCESFUL_COMBATS_COLOR**
  - Default: { 120.0/360.0, 0.95, 0.86 }
  - Developer comment: Color for icons if all combats are successful

- **MIN_NON_SUCCESSFUL_COMBAT_COLOR**
  - Default: { 100.0/360.0, 0.95, 0.86 }
  - Developer comment: Color for icons if some of combats are not successful

- **MID_NON_SUCCESSFUL_COMBAT_COLOR**
  - Default: { 50.0/360.0, 0.95, 0.86 }

- **MAX_NON_SUCCESSFUL_COMBAT_COLOR**
  - Default: { 0.0/360.0, 0.95, 0.86 }
  - Developer comment: Color for icons if all of combats are not successful

- **UNIT_SELECT_DOUBLE_CLICK_TIME**
  - Default: 0.1
  - Developer comment: Delay before double click event for unit selection

- **SHIP_SELECT_DOUBLE_CLICK_TIME**
  - Default: 1.0
  - Developer comment: Delay before double click event for ship selection

- **MINIMAP_TOGGLE_DURATION**
  - Default: 0.5
  - Developer comment: Delay for minimap toggle

- **MINIMAP_TOGGLE_SHIFT**
  - Default: 270
  - Developer comment: horizontal shift for minimap to close it

- **TIMED_MESSAGE_TIMEOUT**
  - Default: 0.35
  - Developer comment: Timeout for timed message

- **MINIMAP_PING_DURATION**
  - Default: 12.0
  - Developer comment: timeout for pings

- **MINIMAP_PING_SPEEDUP_ON_SCREEN**
  - Default: 2.0
  - Developer comment: speed up for timeout if ping is visible on screen

- **MINIMAP_PING_DELAY_BETWEEN_PINGS**
  - Default: 0.3
  - Developer comment: delay between consecative pings

- **DRAG_AND_DROP_SCROLLING_SENSITIVITY**
  - Default: 12.5
  - Developer comment: Speed multiplier for components scrolling while drag'n dropping elements

- **GRIDBOX_ELEMENTS_INTERPOLATION_SPEED**
  - Default: 0.5
  - Developer comment: A value used to determine how fast the elements within the gridbox are interpolating while drag'n dropping.

- **ARMY_GROUP_PORTRAIT_SPACING**
  - Default: 6
  - Developer comment: Extra space added between portraits of different army groups

- **ARMY_GROUP_FIRST_MEMBER_SPACING**
  - Default: 5
  - Developer comment: Extra spacing between the army group portrait and the first member of the army group

- **ARMY_GROUP_COLLAPSE_EXTRA_SPACING**
  - Default: 5
  - Developer comment: Extra spacing between the army group portrait when army group is collapsed

- **ARMY_LIST_BOTTOM_PADDING**
  - Default: 165
  - Developer comment: Bottom padding for army list on left

- **ARMY_LIST_BOTTOM_PADDING_WITH_EXPEDITIONARIES**
  - Default: 240
  - Developer comment: Bottom padding for army list on left when expeditionaries are open

- **MILITARY_FACTORIES_SCALE**
  - Default: { 1, 5, 10 }

- **FLEET_BOTTOM_BAR_HEIGHT**
  - Default: 110
  - Developer comment: Height of the list of fleet at the bottom of the screen

- **FLEET_BOTTOM_BAR_PADDING_RIGHT**
  - Default: 110
  - Developer comment: Width of the Rhs panel at the bottom of the screen where map mode are selected

- **PICKED_UP_NAVY_OFFSET_X**
  - Default: 26
  - Developer comment: Amount of pixels to shift the picked up navy window on the x axis

- **PICKED_UP_NAVY_OFFSET_Y**
  - Default: -14
  - Developer comment: Amount of pixels to shift the picked up navy window on the y axis

- **TASK_FORCE_ENTRY_OFFSET_Y**
  - Default: -2
  - Developer comment: Adjust the position of a task force entry. Added to the height of the background image.

- **TASK_FORCE_COMPOSITION_EDITOR_PADDING_TO_NAVIES_VIEW**
  - Default: 20
  - Developer comment: Padding on the x axis between the navies view and the task force composition editor window

- **FUEL_STOCKPILE_DURATION_MAX**
  - Default: 365*5
  - Developer comment: our max for stockpile duration display

- **SHIP_REFIT_TOOLTIP_MAX_DIFF_LINES**
  - Default: 20
  - Developer comment: Maximum number of lines to show in the tooltip describing stat differences from all the source equipment variants to the target being considered.

- **DEFAULT_TASKFORCE_ICON**
  - Default: 6
  - Developer comment: newly created taskforces will use this icon

- **DEFAULT_FLEET_ICON**
  - Default: 4
  - Developer comment: newly created fleets will use this icon

- **DEFAULT_NAVAL_EQUIPMENT_ROLE_ICON**
  - Default: 1
  - Developer comment: newly created naval equipment variants will use this icon, if the AI equipment designs do not propose a better one.

- **FUEL_GRAPH_COLOR**
  - Default: { 0.8, 0.8, 0.8, 0.8, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.8, 0.0, 0.8, 0.8, 0.8, 0.8, 0.0, 0.8, 0.8, 0.8 }
  - Developer comment:
    ```text
    stockpile
    total consumption
    army consumption
    navy consumption
    air consumption
    other consumption
    produced
    ```

- **PRODUCTION_SHIP_FILTERS_ROLE_SELECTION_WINDOW_OFFSET_X**
  - Default: 4
  - Developer comment: offset of the role icon selection window shown in the filters of ship design in the production tab

- **PRODUCTION_SHIP_FILTERS_ROLE_SELECTION_WINDOW_OFFSET_Y**
  - Default: -8

- **SHIP_FUEL_EFFICIENCY_WARNING_THRESHOLD**
  - Default: 60.0
  - Developer comment: Fuel usage threshold above which a ship is considered fuel inefficient for always on missions

- **NAVAL_STRIKE_FORCE_ATTACK_LIKELYHOOD_THR_VERY_LIKELY**
  - Default: 0.8
  - Developer comment: threshold above which to show that a strike force is "very likely" to engage an enemy

- **NAVAL_STRIKE_FORCE_ATTACK_LIKELYHOOD_THR_LIKELY**
  - Default: 0.6
  - Developer comment: same, for "likely"

- **NAVAL_STRIKE_FORCE_ATTACK_LIKELYHOOD_THR_UNLIKELY**
  - Default: 0.3
  - Developer comment: same, for "unlikely"

- **CONVOY_ESCORT_PRESENCE_WARNING_THRESHOLD**
  - Default: 0.95
  - Developer comment: Value for the Escort Presence below which a warning will be shown on the naval mission map icon

- **MISSION_PATROL_SOFT_REQ_THRESHOLD_SURFACE_DETECTION**
  - Default: 22
  - Developer comment: Value below which the mission icon for the patrol mission is showing a warning

- **MISSION_PATROL_SOFT_REQ_THRESHOLD_SPEED**
  - Default: 30
  - Developer comment: (kph) Same, but for Speed of the task force

- **MISSION_PATROL_SOFT_REQ_THRESHOLD_SURFACE_VISIBILITY**
  - Default: 1.4
  - Developer comment: Same, but for the surface visibility of the task force (lower means more fit for the mission for this one)

- **MISSION_CONVOY_ESCORT_SOFT_REQ_THRESHOLD_SUB_DETECTION**
  - Default: 2
  - Developer comment: Same, for convoy escort

- **MISSION_CONVOY_ESCORT_SOFT_REQ_THRESHOLD_DEPTH_CHARGES_AVG**
  - Default: 8
  - Developer comment: Average of the stat Depth Charges in the task force

- **MISSION_CONVOY_ESCORT_SOFT_REQ_THRESHOLD_DEPTH_CHARGES_SUM**
  - Default: 8
  - Developer comment: Sum of the stat Depth Charges in the task force

- **MISSION_NAVAL_INVASION_SUPPORT_SOFT_REQ_THRESHOLD_SHORE_BOMBARDMENT**
  - Default: 3
  - Developer comment: Same, for naval invasion. Sum of the stat Shore Bombardment in the task force

- **OPERATIVE_MISSION_EFFICIENCY_ANIMATION_TIME_MIN**
  - Default: 0.2
  - Developer comment: the minimum duration of a loop in seconds

- **OPERATIVE_MISSION_EFFICIENCY_ANIMATION_TIME_MAX**
  - Default: 3.0
  - Developer comment: the maximum duration of a loop in seconds

- **OPERATIVE_COUNTER_INTELLIGENCE_DEFENSE_TO_EFFICIENCY_FACTOR**
  - Default: 40.0
  - Developer comment: Factor multiplied to the defense provided by the operative while on counter intelligence mission to get a score in the range [0,100] that is then used to scale the animation speed

- **OPERATIVE_NETWORK_STRENGTH_GAIN_TO_EFFICIENCY_FACTOR**
  - Default: 12.0
  - Developer comment: Factor multiplied to the network strength the operative provides while on build network mission to get a score in the range [0,100] that is then used to scale the animation speed

- **OPERATIVE_PROPAGANDA_DRIFT_TO_EFFICIENCY_FACTOR**
  - Default: 130000.0
  - Developer comment: Factor multiplied to the war support and stability drift to obtain the efficiency score (expected to be in range [0,100])

- **OPERATIVE_BOOST_IDEOLOGY_DRIFT_TO_EFFICIENCY_FACTOR**
  - Default: 500.0
  - Developer comment: Factor multiplied to the ideology drift caused by the operative in order to get a score in the range [0,100] used to determine the speed of the animation

- **OPERATIVE_ROOT_OUT_RESISTANCE_EFFICIENCY_TO_EFFICIENCY_FACTOR**
  - Default: 80.0
  - Developer comment: Factor multiplied to the operative's efficiency at the RootOutResistance mission to determine the animation speed

- **OPERATIVE_TRADE_INFLUENCE_DRIFT_TO_EFFICIENCY_FACTOR**
  - Default: 135
  - Developer comment: Factor multiplied to the operative's trade influence drift to determine the animation speed

- **OPERATIVE_OPINION_DRIFT_TO_EFFICIENCY_FACTOR**
  - Default: 400
  - Developer comment: Factor multiplied to the operative's trade influence drift to determine the animation speed

- **OPERATIVE_TENSION_DRIFT_TO_EFFICIENCY_FACTOR**
  - Default: 400
  - Developer comment: Factor multiplied to the operative's trade influence drift to determine the animation speed

- **COUNTERINTELLIGENCE_ACTIVITY_LEVEL_THRESHOLD_VALUES**
  - Default: { 10, 20, 50, 100 }
  - Developer comment:
    ```text
    Used to convert the activity level to a color:
    ACTIVITY_LEVEL_THRESHOLD_COLOR[ i ] will be used if
    CurrentActivityLevel < ACTIVITY_LEVEL_THRESHOLD_VALUES[ i ]
    There can be one more color than threshold define which will
    be used when the CurrentActivityLevel is greater or equal to the
    last threshold.
    ```

- **COUNTERINTELLIGENCE_ACTIVITY_LEVEL_THRESHOLD_COLORS**
  - Default: { { 0.1, 0.9, 0.2, 1.0 }, { 0.6, 0.9, 0.2, 1.0 }, { 0.9, 0.7, 0.2, 1.0 }, { 1.0, 0.5, 0.0, 1.0 }, { 0.9, 0.1, 0.2, 1.0 } }

- **GARRISON_STRENGTH_TO_SHOW_RED**
  - Default: 0.25
  - Developer comment: If the garrison strength is lower than that, we color the number of divisions in red.

- **MAX_DECISIONS_IN_DECISION_ALERT_TOOLTIP**
  - Default: 5
  - Developer comment: Max number of available decisions we show in the alert tooltip

- **PIXEL_OFFSET**
  - Default: -3
  - Developer comment: Country army view tab pixel offset when clicking on division/navy/air tab or the army officer corp tab

- **ARMY_UNIT_LEADER_ICON_SPRITE_ID**
  - Default: 5

- **NAVY_UNIT_LEADER_ICON_SPRITE_ID**
  - Default: 3

- **POLITICAL_LEADER_ICON_SPRITE_ID**
  - Default: 13

- **EQUIPMENT_DESIGNER_SHOW_MODULE_FORBIDS_BASE_ROLE_ICON**
  - Default: 0
  - Developer comment:
    ```text
    When selecting a module in the tank designer, for each role the module forbids a role icon may be displayed.
    If this is set to 0 no icon will be displayed if the main tank role is forbidden. If set to 1 the icon will be displayed as normal.
    ```

- **EQUIPMENT_DESIGNER_SHOW_MODULE_FORBIDS_SPECIALIZED_ROLE_ICON**
  - Default: 0
  - Developer comment: If this is set to 0 no icons will be displayed for any forbidden specialized roles. If set to 1 the icons will be displayed as normal.

- **MIO_CENTRAL_TREE_HORIZONTAL_POSITION**
  - Default: 1
  - Developer comment: Horizontal position for auto-generated MIO traits

- **SLOW_INTERFACE_THRESHOLD**
  - Default: 5000
  - Developer comment: Show warning "SLOW INTERFACE" in debug when interface refresh takes more that this (in microseconds)

## NFrontend

- **CAMERA_LOOKAT_X**
  - Default: 2958.0
  - Developer comment: Rotation point in main menu

- **CAMERA_LOOKAT_Y**
  - Default: 0.0

- **CAMERA_LOOKAT_Z**
  - Default: 1519.0

- **CAMERA_START_X**
  - Default: 2958.0
  - Developer comment: Initial position in main menu

- **CAMERA_START_Y**
  - Default: 800
  - Developer comment: Y is height

- **CAMERA_START_Z**
  - Default: 1400.0

- **CAMERA_END_X**
  - Default: 2958.0
  - Developer comment: Move to position in main menu

- **CAMERA_END_Y**
  - Default: 900.0

- **CAMERA_END_Z**
  - Default: 1400.0

- **CAMERA_MIN_HEIGHT**
  - Default: 50.0
  - Developer comment: Minimum camera height

- **CAMERA_MAX_HEIGHT**
  - Default: 3000.0
  - Developer comment: Maximum camera height

- **CAMERA_SPEED_IN_MENUS**
  - Default: 0.1

- **CAMERA_INTERPOLATION_SPEED**
  - Default: 0.19

- **FRONTEND_POS_X**
  - Default: 2958.0

- **FRONTEND_POS_Y**
  - Default: 900.0

- **FRONTEND_POS_Z**
  - Default: 1500.0

- **FRONTEND_LOOK_X**
  - Default: 2958.0

- **FRONTEND_LOOK_Y**
  - Default: 0.0

- **FRONTEND_LOOK_Z**
  - Default: 1519.0

- **MP_OPTIONS_POS_X**
  - Default: 2958.0

- **MP_OPTIONS_POS_Y**
  - Default: 922.0

- **MP_OPTIONS_POS_Z**
  - Default: 848.0

- **MP_OPTIONS_LOOK_X**
  - Default: 2958.0

- **MP_OPTIONS_LOOK_Y**
  - Default: 0.0

- **MP_OPTIONS_LOOK_Z**
  - Default: 1519.0

- **NEW_GAME_BUTTON_DISABLE_DELAY_ON_INVALID_MAP_DATA**
  - Default: 10.0
  - Developer comment: amount of seconds to disable buttons leading to a game start for

- **SOCIALVIEW_CONTEXT_MENU_BUTTON_OFFSET**
  - Default: 10

- **SOCIALVIEW_CONTEXT_MENU_MARGIN**
  - Default: 2

## NSound

- **HEIGHT_SOUND_CATEGORY**
  - Default: "Atmosphere"
  - Developer comment:
    ```text
    The volume of sounds in this category vary with camera altitude.
    Name of the sound category
    ```

- **HEIGHT_SOUND_MIN_ALTITUDE**
  - Default: 100.0
  - Developer comment: Below this altitude the minimum volume will be used

- **HEIGHT_SOUND_MAX_ALTITUDE**
  - Default: 2000.0
  - Developer comment: Above this altitude the maximum volume will be used

- **HEIGHT_SOUND_MIN_VOLUME**
  - Default: 0.2

- **HEIGHT_SOUND_MAX_VOLUME**
  - Default: 1.0

- **BATTLE_SOUND_NAME**
  - Default: "amb_battle_distant"

- **BATTLE_SOUND_INIT_RADIUS**
  - Default: 9.0

- **BATTLE_SOUND_FALLOFF_DEFAULT**
  - Default: 100.0

- **BATTLE_SOUND_MIN_UNIT_COUNT**
  - Default: 6

- **VOICE_OVER_CATEGORY**
  - Default: "Voices"

- **VOICE_OVER_COOL_DOWN**
  - Default: 2.8
  - Developer comment: Wait for this many seconds before playing another vo

## NFriendGUI

- **OFFLINE_COLOR**
  - Default: { 0.7, 0.7, 0.7, 1.0 }
  - Developer comment: Text color of offline state

- **ONLINE_COLOR**
  - Default: { 0.56, 0.85, 0.56, 1.0 }
  - Developer comment: Text color of online state

## NCareerProfile

- **MOD_STATISTICS_GROUP**
  - Default: ""
  - Developer comment:
    ```text
    Mod defines
    Can be set by mods to collect statistics in a separate data set for the mod. Will also be used as the display name if MOD_STATISTICS_GROUP_NAME is not set.
    ```

- **MOD_STATISTICS_GROUP_NAME**
  - Default: ""
  - Developer comment: Can be set by mods as a display name for the mod's statistics data set. It can be a localized.

- **NAVAL_INVASION_MEDAL_MAX_DURATION**
  - Default: 96
  - Developer comment:
    ```text
    Statistics parameters
    Maximum duration in hours to finish naval invasion and get a Naval Invasion Medal
    ```

- **PARADROP_AWARD_DIVISION_MIN_BATTALION_COUNT**
  - Default: 5
  - Developer comment: Minimum count of battalions in the division required to count that division for paradrop awards ("Paradrop Medal" and "They came from Above")

- **NAVAL_INVASION_MEDAL_DIVISION_MIN_BATTALION_COUNT**
  - Default: 5
  - Developer comment: Minimum count of battalions in the division required to count that division for Naval Invasion Medal

- **TURNING_TIDE_MEDAL_DIVISION_MIN_BATTALION_COUNT**
  - Default: 5
  - Developer comment: Minimum count of battalions in the division required to count that division for Turning the Tide Medal

- **LORD_OF_THE_SEAS_MEDAL_MIN_SUPREMACY**
  - Default: 0.75
  - Developer comment: Minimum supremacy to count current naval region for Lord of the Seas Medal

- **STEEL_AT_HIGH_SPEED_RIBBON_TANK_SPEED**
  - Default: 12
  - Developer comment: Minimum speed to count deployed tanks for Steel at High Speed Ribbon

- **ORCHESTRA_OF_BOOM_RIBBON_SPECIAL_BATTALION_COUNT**
  - Default: 4
  - Developer comment: Amount of special battalion types(anti-air, anti-tank, artillery and rocket artillery) required for the division for Orchestra of Boom Ribbon

- **NEVERMINE_ME_MEDAL_MIN_SUPREMACY_EFFECT**
  - Default: 0.5
  - Developer comment: Minimum effect mines should have on the supremacy to count current naval region for Nevermine Me Medal

- **BLITZ_THIS_TACTIC_NAME**
  - Default: "tactic_elastic_defense"
  - Developer comment: The tactic required to be applied to a leader or a country for Blitz This Ribbon

- **ENGINEERING_BEHEMOTH_MEDAL_ARMOR_RATING_BRONZE**
  - Default: 100
  - Developer comment: The armor rating required for the tanks to get the Engineering The Behemoth Bronze Medal

- **ENGINEERING_BEHEMOTH_MEDAL_ARMOR_RATING_SILVER**
  - Default: 160
  - Developer comment: The armor rating required for the tanks to get the Engineering The Behemoth Silver Medal

- **ENGINEERING_BEHEMOTH_MEDAL_ARMOR_RATING_GOLD**
  - Default: 200
  - Developer comment: The armor rating required for the tanks to get the Engineering The Behemoth Gold Medal

- **CASTLES_IN_THE_AIR_MEDAL_AIR_DEFENSE_BRONZE**
  - Default: 20
  - Developer comment: The air defense required for the airplanes to get the Castles in the Air Bronze Medal

- **CASTLES_IN_THE_AIR_MEDAL_AIR_DEFENSE_SILVER**
  - Default: 50
  - Developer comment: The air defense required for the airplanes to get the Castles in the Air Silver Medal

- **CASTLES_IN_THE_AIR_MEDAL_AIR_DEFENSE_GOLD**
  - Default: 100
  - Developer comment: The air defense required for the airplanes to get the Castles in the Air Gold Medal

## NCareerProfileGUI

- **AWARD_POPUP_DURATION**
  - Default: 8000
  - Developer comment: Show an award popup for this many milliseconds

- **AWARD_POPUP_CONTENT_DELAY**
  - Default: 400
  - Developer comment: Show the content of the award popup after this many milliseconds

- **CAREER_POINTS_ANIMATION_DELAY**
  - Default: 950
  - Developer comment: Delay the career points count-up animation by this many milliseconds

- **CAREER_POINTS_ANIMATION_DURATION**
  - Default: 950
  - Developer comment: Count the career points up for this many milliseconds

- **PROFILE_PICTURE_BACKGROUND_OPACITY**
  - Default: 0.8
  - Developer comment: The opacity of the dark background square behind profile pictures

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
