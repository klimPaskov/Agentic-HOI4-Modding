"""The Meshy pin, the reviewed tool contract and the captured schema lock agree with each other."""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import bootstrap_3d_workflow as bootstrap
from meshy_client import MOTION_TOOL_ARGUMENTS, refuse_forbidden_arguments, rig_arguments


def read(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class PinTests(unittest.TestCase):
    def test_every_pin_names_the_bootstrap_version(self) -> None:
        version = bootstrap.MESHY_VERSION
        package = read("meshy_runtime/package.json")
        lock = read("meshy_runtime/package-lock.json")
        self.assertEqual(package["dependencies"][bootstrap.MESHY_PACKAGE], version)
        self.assertEqual(lock["packages"][f"node_modules/{bootstrap.MESHY_PACKAGE}"]["version"], version)
        self.assertEqual(lock["packages"][f"node_modules/{bootstrap.MESHY_PACKAGE}"]["integrity"], bootstrap.MESHY_INTEGRITY)
        self.assertEqual(read("config/meshy_tool_schema.lock.json")["server_version"], version)
        self.assertEqual(
            read("config/dependencies.lock.json")["sources"]["meshy_mcp"],
            f"npm:{bootstrap.MESHY_PACKAGE}@{version}",
        )

    def test_runtime_lock_files_match_the_bootstrap_evidence(self) -> None:
        for name, expected in (
            ("package.json", bootstrap.MESHY_RUNTIME_PACKAGE_SHA256),
            ("package-lock.json", bootstrap.MESHY_RUNTIME_LOCK_SHA256),
        ):
            digest = hashlib.sha256((ROOT / "meshy_runtime" / name).read_bytes()).hexdigest()
            self.assertEqual(digest, expected, name)

    def test_upstream_head_is_a_full_commit_id(self) -> None:
        head = read("config/meshy_tool_schema.lock.json")["server_git_head"]
        self.assertRegex(head, r"^[0-9a-f]{40}$")


class ContractAgainstLockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = read("config/meshy_tool_contract.json")
        self.lock = read("config/meshy_tool_schema.lock.json")
        self.locked = {**self.lock["required_tools"], **self.lock["optional_tools"]}

    def contract_tool_names(self) -> set:
        names = set(self.contract["required_tools"])
        for capability in self.contract["optional_capabilities"].values():
            names.update(capability["tool_names"])
        return names

    def test_every_contract_tool_is_in_the_schema_lock(self) -> None:
        self.assertEqual(sorted(self.contract_tool_names() - set(self.locked)), [])

    def test_contract_arguments_exist_in_the_locked_schemas(self) -> None:
        for name, tool in self.contract["required_tools"].items():
            properties = self.locked[name]["input_schema"]["properties"]
            wanted = set(tool.get("required_arguments", []))
            for group in tool.get("required_argument_groups", []):
                wanted.update(group)
            wanted.update(tool.get("input_exclusivity", []))
            wanted.update(tool.get("forbidden_arguments", []))
            with self.subTest(tool=name):
                self.assertEqual(sorted(wanted - set(properties)), [])

    def test_contract_and_lock_agree_on_what_is_paid(self) -> None:
        for name, tool in self.contract["required_tools"].items():
            with self.subTest(tool=name):
                self.assertEqual(tool["paid"], self.locked[name]["paid"])

    def test_motion_tools_are_the_ones_0_6_7_registers(self) -> None:
        names = set(self.contract["optional_capabilities"]["text_to_motion"]["tool_names"])
        self.assertEqual(
            names,
            {
                "meshy_text_to_motion",
                "meshy_list_animations",
                "meshy_get_task_status",
                "meshy_list_tasks",
                "meshy_download_model",
            },
        )
        self.assertEqual(names, set(MOTION_TOOL_ARGUMENTS))
        for name, arguments in MOTION_TOOL_ARGUMENTS.items():
            with self.subTest(tool=name):
                self.assertTrue(arguments <= set(self.locked[name]["input_schema"]["properties"]))

    def test_animate_takes_exactly_one_of_the_action_sources(self) -> None:
        group = [["action_id", "action_ids", "motion_task_id"]]
        self.assertEqual(self.contract["required_tools"]["meshy_animate"]["required_argument_groups"], group)
        self.assertEqual(self.locked["meshy_animate"]["required_argument_groups"], group)
        self.assertEqual(self.locked["meshy_animate"]["required_arguments"], ["rig_task_id"])

    def test_lock_accepts_no_retired_model_or_model_type(self) -> None:
        image = self.lock["required_tools"]["meshy_image_to_3d"]
        retired = set(self.contract["provider_policy"]["retired_generation_models"])
        self.assertEqual(sorted(retired & set(image["accepted_ai_models"])), [])
        self.assertIn("meshy-t2.5", image["accepted_ai_models"])
        model_types = image["input_schema"]["properties"]["model_type"]["enum"]
        self.assertEqual(sorted(set(self.contract["provider_policy"]["retired_model_types"]) & set(model_types)), [])

    def test_lock_keeps_the_verified_action_ids_and_holds_no_prices(self) -> None:
        animate = self.locked["meshy_animate"]
        self.assertEqual(animate["verified_action_ids"], {"idle": 0, "attack": 4, "death": 8})
        for name, tool in self.locked.items():
            self.assertNotIn("estimate_credits", tool, name)


class RigDeprecatedArgumentTests(unittest.TestCase):
    def test_rig_request_never_carries_texture_image_url(self) -> None:
        for kwargs in ({"input_task_id": "task", "model_url": None}, {"input_task_id": None, "model_url": "https://x/m.glb"}):
            arguments = rig_arguments(height_meters=1.8, **kwargs)
            self.assertNotIn("texture_image_url", arguments)

    def test_contract_forbids_the_deprecated_argument(self) -> None:
        self.assertIn("texture_image_url", self.forbidden("meshy_rig"))
        self.assertIn("texture_image_url", read("config/meshy_tool_schema.lock.json")["required_tools"]["meshy_rig"]["deprecated_arguments"])
        with self.assertRaisesRegex(ValueError, "texture_image_url"):
            refuse_forbidden_arguments("meshy_rig", {"input_task_id": "task", "texture_image_url": "https://x/t.png"})

    def test_forbidden_flags_may_be_present_when_false(self) -> None:
        refuse_forbidden_arguments("meshy_image_to_3d", {"multi_view_thumbnails": False})
        with self.assertRaises(ValueError):
            refuse_forbidden_arguments("meshy_image_to_3d", {"multi_view_thumbnails": True})

    @staticmethod
    def forbidden(tool: str) -> list:
        return read("config/meshy_tool_contract.json")["required_tools"][tool]["forbidden_arguments"]


if __name__ == "__main__":
    unittest.main()
