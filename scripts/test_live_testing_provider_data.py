from pathlib import Path
import json
import unittest
from unittest import mock
from live_testing_provider_data import build_live_testing_table, build_live_testing_components, CLAUSEWITZ_REVISION
import test_live_bootstrap_contract as contract
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]

class LiveTestingContractTests(unittest.TestCase):
    def test_table_routes_and_support_limits(self):
        table=build_live_testing_table()
        self.assertEqual(table["default_provider"], "clausewitz_mcp")
        rows={r["id"]:r for r in table["providers"]}
        self.assertEqual(set(rows), {"clausewitz_mcp", "hoi4_live_tools", "none"})
        cw=rows["clausewitz_mcp"]
        self.assertEqual(cw["route"]["source_revision"], CLAUSEWITZ_REVISION)
        self.assertEqual(cw["route"]["server_id"], "clausewitz_linux")
        self.assertEqual(cw["attribution"]["author"], "smerss")
        self.assertEqual(cw["attribution"]["license"], "MIT")
        self.assertIn("1.19.2", cw["supported_game_version"])
        self.assertTrue(any("Linux game and server are ready" in x for x in cw["guidance"]))
        self.assertEqual(rows["hoi4_live_tools"]["supported_platforms"], ["windows"])
        self.assertTrue(rows["hoi4_live_tools"]["experimental"])
        self.assertEqual(rows["none"]["display_name"], "None")
        self.assertIsNone(rows["none"]["route"]["server_id"])
        self.assertIsNone(rows["none"]["route"]["component_id"])

    def test_components_are_idempotent_and_ownership_is_disjoint(self):
        manifest=contract.manifest()
        components=build_live_testing_components(manifest["components"])
        by_id={c["id"]:c for c in components}
        self.assertEqual(components, build_live_testing_components(manifest["components"]))
        common=by_id["workflow.live_testing"]
        specific=by_id["workflow.live_tools"]
        self.assertEqual(common["platforms"], ["windows", "macos", "linux"])
        provider_file="hoi4-live-playtest/references/hoi4-live-tools.md"
        self.assertIn(provider_file,common["source"]["exclude"])
        self.assertEqual(specific["source"]["include"],[provider_file])
        self.assertIn("workflow.live_testing",specific["dependencies"])
        self.assertIn("workflow.live_testing",by_id["runtime.codex.live_tools_skill"]["dependencies"])

    def test_markers_and_neutral_guidance(self):
        for name in ["CLAUDE_template.md","AGENTS_template.md",".claude/skills/hoi4-live-playtest/SKILL.md",".claude/skills/hoi4-debug-playtest/SKILL.md"]:
            text=(ROOT/name).read_text(encoding="utf-8")
            self.assertEqual(text.count("<!-- HOI4_MOD_SETUP:LIVE_TESTING_PROVIDER:START -->"),1,name)
            self.assertEqual(text.count("<!-- HOI4_MOD_SETUP:LIVE_TESTING_PROVIDER:END -->"),1,name)
            self.assertIn("qualified tool",text,name)

    def test_schema_optional_catalog_and_rejects_unknown_route(self):
        schema=json.loads((ROOT/"schemas/remote-manifest.v5.schema.json").read_text())
        validator=Draft202012Validator(schema)
        manifest=contract.manifest()
        validator.validate(manifest)
        manifest.pop("live_testing")
        validator.validate(manifest)
        manifest["live_testing"]=build_live_testing_table()
        manifest["live_testing"]["providers"][0]["route"]["kind"]="invented"
        self.assertTrue(list(validator.iter_errors(manifest)))

    def test_bootstrap_installs_without_user_registration(self):
        bootstrap=contract.bootstrap
        result=mock.Mock(stdout=b"", returncode=0)
        with mock.patch.object(bootstrap.subprocess,"run",return_value=result) as run:
            self.assertEqual(bootstrap.run_installer(Path("install.py"),True,"none"),0)
        args=run.call_args.args[0]
        self.assertEqual(args[args.index("--register")+1],"none")
        self.assertIn("--quiet",args)
        with mock.patch.object(bootstrap.subprocess,"run",return_value=result) as run:
            bootstrap.run_installer(Path("install.py"),False)
        args=run.call_args.args[0]
        self.assertEqual(args[args.index("--register")+1],"auto")

if __name__=="__main__": unittest.main()
