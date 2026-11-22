"""The Tripo card comes from the job entry by rule, and an armed unit's grip commands come from the same entry.

Each test is one gap a Sonnet session found when it made the hobgoblin from a hand-copied card (2026-11-22): no weapon steps in the card,
no hand field (the drawing's weapon was on the viewer's right, the rig's LeftHand, and every tool defaults to RightHand), no sources row
filled, no record of the kit commit, and no attack decision before the Tripo tab was closed.
"""

from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(PIPELINE_ROOT / "tripo"))

from lib import tripo_card as C
import arm_unit
import clip_check
import make_card

TEMPLATE = (PIPELINE_ROOT / "tripo" / "CARD_TEMPLATE.md").read_text(encoding="utf-8")
FILLED = ("<asset_slug>", "<kit commit>", "<picture>", "<sources>", "<unit_type>", "<posture>", "<credit_budget>", "<job folder>",
          "<hand>", "<viewer side>", "<hand words>", "<weapon>", "<shield>")
ATTACK = "A heavy warrior raises the wooden mallet"
CLIPS = ["idle", "walk", "chop", "hit_to_stomach", "flee_01", "defeat_03", ATTACK + " in his own left hand high over his head, then smashes"]


def armed_spec(**weapon) -> dict:
    return {
        "provider": "tripo",
        "unit_type": "infantry_melee",
        "credit_budget": 120,
        "reference_path": "refs/original/hob.png",
        "reference_sources": ["the owner's drawing: refs/drawings/hob.jpg"],
        "tripo": {
            "posture": "upright",
            "roles": {"idle": "idle", "move": "walk", "attack": ATTACK, "defend": "hit_to_stomach", "retreat": "flee_01", "death": "defeat_03"},
            "weapon": {"part": "tripo_part_1", "bone": "Weapon", "source": "rigged", "release_roles": ["death"], "hand": "LeftHand",
                       "name": "wooden mallet", "grip_options": {"length_ratio": 0.62, "grip": 0.3}, **weapon},
        },
    }


def unarmed_spec() -> dict:
    spec = armed_spec()
    spec["unit_type"] = "infantry_unarmed"
    del spec["tripo"]["weapon"]
    return spec


def fill(spec: dict) -> str:
    return C.fill(TEMPLATE, spec, "hob", job_folder="docs/assets/hoi4_3d_model_jobs/models_3d/hob", kit_commit="abc123")


def write_glb(path: Path, names) -> None:
    doc = json.dumps({"asset": {"version": "2.0"}, "animations": [{"name": n, "channels": [], "samplers": []} for n in names]}).encode()
    doc += b" " * (-len(doc) % 4)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"glTF" + struct.pack("<II", 2, 20 + len(doc)) + struct.pack("<I", len(doc)) + b"JSON" + doc)


class CardTests(unittest.TestCase):
    def test_the_template_blocks_are_balanced(self) -> None:
        for kind in ("armed", "unarmed", "shield", "winged"):
            self.assertEqual(TEMPLATE.count(f"<!-- {kind} -->"), TEMPLATE.count(f"<!-- /{kind} -->"), kind)

    def test_an_armed_card_has_the_weapon_steps_with_the_hand_and_the_file_names(self) -> None:
        card = fill(armed_spec())
        for wanted in ("## 1. Weapon picture", "Redraw only the wooden mallet", "Remove the wooden mallet completely",
                       "armed/hob_weapon__model.glb", "armed/hob__body.glb", "--hand LeftHand", "tripo/arm_unit.py",
                       "the viewer's right", "his own left hand", "abc123", "the owner's drawing: refs/drawings/hob.jpg",
                       "## 6. Before you leave Tripo", "--attack chop", "not visible, do not add"):
            self.assertIn(wanted, card)
        self.assertNotIn("--unarmed", card)
        self.assertNotIn("box_01,", card)
        self.assertNotIn("<!--", card)
        for placeholder in FILLED:
            self.assertNotIn(placeholder, card, placeholder)

    def test_a_winged_card_has_the_wing_note_the_rig_dialog_and_a_standing_burn_death(self) -> None:
        spec = unarmed_spec()
        spec["anatomy"] = {"wings": True}
        spec["tripo"].update({"chains": [{"region": "wings"}], "death_kind": "burn"})
        card = fill(spec)
        for wanted in ("**The wings.**", "Not Ready for Auto-Rigging", "Do not press **Retry** to make sure", "| death | `hit_to_stomach` |"):
            self.assertIn(wanted, card)
        self.assertNotIn("<!--", card)
        plain = fill(unarmed_spec())
        self.assertNotIn("**The wings.**", plain)
        self.assertNotIn("Not Ready for Auto-Rigging", plain)

    def test_wings_without_their_chains_are_refused(self) -> None:
        spec = unarmed_spec()
        spec["anatomy"] = {"wings": True}
        self.assertTrue(any("tripo.chains" in item for item in C.problems(spec)))

    def test_an_unarmed_card_has_no_weapon_steps(self) -> None:
        card = fill(unarmed_spec())
        self.assertIn("inbox/hob__rigged.glb", card)
        self.assertIn("--unarmed", card)
        self.assertIn("--attack box_01", card)
        for absent in ("Weapon picture", "arm_unit.py", "_weapon__model", "--hand ", "<!--"):
            self.assertNotIn(absent, card)

    def test_a_shield_adds_its_own_picture_and_model(self) -> None:
        spec = armed_spec()
        spec["tripo"]["shield"] = {"name": "crescent shield"}
        card = fill(spec)
        self.assertIn("Redraw only the crescent shield", card)
        self.assertIn("armed/hob_shield__model.glb", card)

    def test_a_weapon_without_its_hand_is_refused_with_the_side_rule(self) -> None:
        for hand in (None, "right", "Right", "left_hand"):
            with self.subTest(hand=hand):
                spec = armed_spec(hand=hand)
                found = C.problems(spec)
                self.assertTrue(any("rig's side, not the viewer's" in item and "viewer's right" in item for item in found), found)
                with self.assertRaisesRegex(ValueError, "not ready for a card"):
                    fill(spec)

    def test_the_other_open_steps_are_refused(self) -> None:
        cases = {
            "reference_sources is empty": lambda s: s.update(reference_sources=[" "]),
            "needs tripo.weapon": lambda s: s["tripo"].pop("weapon"),
            "tripo.weapon.name": lambda s: s["tripo"]["weapon"].pop("name"),
            "grip_options.length_ratio": lambda s: s["tripo"]["weapon"]["grip_options"].pop("length_ratio"),
            "grip_options.grip": lambda s: s["tripo"]["weapon"].pop("grip_options"),
            "tripo.posture": lambda s: s["tripo"].pop("posture"),
            "other hand": lambda s: s["tripo"].update(shield={"hand": "LeftHand"}),
            "part tripo_part_1 on bone Weapon": lambda s: s["tripo"]["weapon"].update(bone="LeftHand"),
        }
        for message, change in cases.items():
            with self.subTest(message):
                spec = armed_spec()
                change(spec)
                self.assertTrue(any(message in item for item in C.problems(spec)), C.problems(spec))
        self.assertEqual(C.problems(armed_spec()), [])
        self.assertEqual(C.problems(unarmed_spec()), [])

    def test_make_card_writes_the_card_or_lists_what_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / "3d_jobs.json"
            out = root / "CARD.md"
            config.write_text(json.dumps({"jobs": {"hob": armed_spec(), "bad": armed_spec(hand=None)}}), encoding="utf-8")
            self.assertEqual(make_card.main(["--jobs-config", str(config), "hob", "--out", str(out)]), 0)
            self.assertIn("--hand LeftHand", out.read_text(encoding="utf-8"))
            self.assertEqual(make_card.main(["--jobs-config", str(config), "bad", "--out", str(root / "bad.md")]), 2)
            self.assertFalse((root / "bad.md").exists())


class ArmTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.files = C.armed_files(self.root, "hob")

    def test_the_grip_command_holds_fades_drops_and_clears_by_role(self) -> None:
        write_glb(self.files["body"], CLIPS)
        self.files["weapon"].write_bytes(b"glTF")
        grip, = arm_unit.plan(armed_spec(grip_options={"length_ratio": 1.4, "grip": 0.3, "hold_hand": [0.26, 0.07, 0.69]}), "hob", "blender", self.root)
        arg = lambda flag: grip[grip.index(flag) + 1]
        self.assertEqual(arg("--hand"), "LeftHand")
        self.assertIn("--weapon-bone", grip)
        self.assertEqual(arg("--hold-clips"), "idle,walk,hit_to_stomach,flee_01")
        self.assertEqual(arg("--hold-fade-clips"), CLIPS[-1])
        self.assertEqual(arg("--release-clips"), "defeat_03")
        self.assertEqual(arg("--clearance-clips").split(",")[-1], "defeat_03")
        self.assertEqual(arg("--out"), str(self.files["rigged"]))
        self.assertEqual(arg("--length-ratio"), "1.4")
        self.assertEqual(arg("--grip"), "0.3")
        self.assertEqual(arg("--hold-hand"), "0.26,0.07,0.69")

    def test_a_shield_goes_in_the_other_hand_and_writes_the_inbox_file(self) -> None:
        write_glb(self.files["body"], CLIPS)
        for key in ("weapon", "shield"):
            self.files[key].write_bytes(b"glTF")
        spec = armed_spec()
        spec["tripo"]["shield"] = {}
        grip, shield = arm_unit.plan(spec, "hob", "blender", self.root)
        self.assertEqual(grip[grip.index("--out") + 1], str(self.files["gripped"]))
        self.assertEqual(shield[shield.index("--hand") + 1], "RightHand")
        self.assertEqual(shield[shield.index("--out") + 1], str(self.files["rigged"]))

    def test_missing_exports_and_unclear_roles_are_refused(self) -> None:
        with self.assertRaisesRegex(FileNotFoundError, "hob__body.glb"):
            arm_unit.plan(armed_spec(), "hob", "blender", self.root)
        write_glb(self.files["body"], CLIPS)
        self.files["weapon"].write_bytes(b"glTF")
        spec = armed_spec()
        spec["tripo"]["roles"]["attack"] = "A heavy warrior raises the wooden mallet, then"
        with self.assertRaisesRegex(ValueError, "before the first comma"):
            arm_unit.plan(spec, "hob", "blender", self.root)
        spec["tripo"]["roles"]["attack"] = "swing"
        with self.assertRaisesRegex(ValueError, "matches no clip"):
            arm_unit.plan(spec, "hob", "blender", self.root)
        with self.assertRaisesRegex(ValueError, "no tripo.weapon"):
            arm_unit.plan(unarmed_spec(), "hob", "blender", self.root)


class AttackLineTests(unittest.TestCase):
    RESULT = {"clips": {"chop": {"verdict": "fail", "reasons": ["stretch 8.90% > 5%"]}, "box_01": {"verdict": "pass", "reasons": []},
                        ATTACK + " high": {"verdict": "pass", "reasons": []}}}

    def test_a_failing_only_candidate_says_to_make_the_clip_before_leaving(self) -> None:
        line, ok = clip_check.attack_line(self.RESULT, ["chop", "smash"])
        self.assertFalse(ok)
        self.assertTrue(line.startswith("attack: none passes"))
        self.assertIn("chop (stretch 8.90% > 5%)", line)
        self.assertIn("not in the file: smash", line)
        self.assertIn("before you leave Tripo", line)

    def test_a_passing_candidate_is_named_by_its_first_words(self) -> None:
        line, ok = clip_check.attack_line(self.RESULT, ["chop", "A heavy warrior"])
        self.assertTrue(ok)
        self.assertTrue(line.startswith(f"attack: pass {ATTACK} high"), line)


if __name__ == "__main__":
    unittest.main()
