# 3D quick start: from a picture to a unit in the game

You need no 3D knowledge. You choose what kind of model you want, give your agent a picture of it, click through Tripo with a card the kit writes for you, and the agent does the rest. The full guide is [3D units](3d-units.md).

**Before the first unit.** In HOI4 Mod Setup, tick **3D models workflow**. It installs the kit's 3D pipeline, Blender and the HOI4 mesh add-on. Make a [Tripo](https://studio.tripo3d.ai) account and sign in to it in your browser. A free account can try the route. A paid plan gives private models, commercial use and enough credits for a roster. Your agent never types your password.

## 1. Choose the type

Say "make a 3D unit from this picture" and give your agent the picture and a few words about it. It answers a few plain questions from the picture (what it is, how many legs, wings, a weapon and in which hand, its size, a rider) and `tripo/pick_preset.py` turns them into the preset by fixed rules. It then shows you one sentence to confirm, with the cost on the card and on the Canvas, for example: "A goblin with an axe: humanoid with a weapon (preset armed_humanoid). The card costs about 80 to 100 credits, the Canvas workflow Armed unit about 110 to 130, cap 120. Right?" Say yes, or correct it. The presets:

| You want | Preset | Credits |
| --- | --- | --- |
| A soldier or creature with empty hands (zombie, mage, rat man) | `humanoid` | 50 to 70 |
| A fighter with a weapon (orc with an axe, dwarf with a glaive) | `armed_humanoid` | 80 to 100 |
| A big two-legged creature (ogre, troll, giant, yeti) | `large_creature` | 70 to 100 |
| A winged demon, devil or angel | `winged_humanoid` | 50 to 70 |
| A dragon or griffin | `winged_quadruped` | 30 |
| A horse, camel or elephant with a rider | `mount_with_rider` | 80 to 100 for both |
| A four-legged beast (wolf, war beast) | `quadruped` | 30 |
| A tank, plane, ship, building or landmark | `tank`, `plane`, `ship`, `building`, `landmark` | 20 to 120 |

Each preset holds every Tripo setting, the clips to try, the checks and a credit cap, so you never set a value by hand. Your agent tells you the cap and asks you to approve it once. Some types are not proven yet (a dragon, a tank, buildings): the agent says so before you spend.

## 2. Make the picture from references

Tripo builds the model from one clean picture. That picture is made from references, never from a text prompt alone:

- The subject's own reference: your drawing, or the mod's art.
- For something real (a tank, a ship, a castle), real photos or drawings your agent finds, from public-domain or openly licensed sources.

Your agent writes the job with `tripo/new_job.py`, listing every reference. Then, in Tripo's free **Image** tool, you (or the agent) give it the references and the sentence from the card. The card asks for a pose Tripo can rig: arms a little away from the body, hands empty, full body, plain background. Compare the picture with your art detail by detail, and approve it. Nothing is simplified: every detail of the art stays.

## 3. Run the card, or the Canvas workflow

Your agent writes the card with `tripo/make_card.py`. It lists only the steps your type needs, with every setting and price filled in.

- **By hand.** Follow the card in Tripo: model, rig, the free preset clips, export. About ten minutes a model. Check the price on each button before you press it. Press each paid button once.
- **By agent.** The agent follows the same card in your Chrome through Claude in Chrome, while you stay signed in.
- **On Tripo's Agentic Canvas.** The same steps as nodes on one page, for accounts that have the Canvas. It costs 15 credits more a model. See [3D units on the Agentic Canvas](3d-canvas.md).

Save the export where the card says. The free steps then start.

## 4. Let the agent wire it in

The agent runs the rest on your PC, for free:

1. It picks the best clip for each role (idle, move, attack, defend, retreat, death) by measuring them and by how they read at the size the map shows them.
2. Blender turns the model into HOI4's `.mesh`, `.anim` and texture files at vanilla's size.
3. The checks run. A failed check names its free fix.
4. A reviewer that did not make the unit looks at renders at map size and close up.
5. The agent writes the entity and the unit's graphics into your mod.

Then start the game and look at your unit on the map. If something looks wrong, tell the agent what you see. [When something fails](3d-units.md#when-something-fails) lists the usual fixes.
