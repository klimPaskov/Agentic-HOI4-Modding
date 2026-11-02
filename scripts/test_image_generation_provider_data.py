from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import image_generation_provider_data as PROVIDERS
from image_generation_provider_data import build_image_generation_components, build_image_generation_table


class ImageGenerationProviderDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas/remote-manifest.v5.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)

    def test_catalog_matches_manifest_schema_and_has_the_requested_routes(self) -> None:
        table = build_image_generation_table(ROOT)
        instance = json.loads((ROOT / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8"))
        instance["schema_version"] = "5.0.0"
        instance["image_generation"] = table
        errors = list(Draft202012Validator(self.schema).iter_errors(instance))
        self.assertEqual(errors, [])
        ids = {item["id"] for item in table["providers"]}
        self.assertEqual(table["default_provider"], "hoi4_imagegen")
        self.assertTrue({
            "hoi4_imagegen", "openai_api", "gemini_api", "fal_ai", "replicate", "black_forest_labs",
            "stability_ai", "ideogram", "recraft", "leonardo", "adobe_firefly", "xai_grok",
            "together_ai", "openrouter", "comfyui_local", "automatic1111_local", "forge_local",
            "codex_native", "microsoft_foundry", "aws_bedrock",
            "huggingface_inference", "midjourney_manual", "none",
        }.issubset(ids))
        self.assertFalse({"gptimage", "vertex_imagen"} & ids, "the GPTImage and Vertex AI routes were removed")

    def test_every_provider_has_fallbacks_and_one_image_per_call(self) -> None:
        implemented_protocols = {
            "openai_images", "openai_compatible", "openrouter_images", "xai_imagine", "together_images", "huggingface_inference", "gemini_generate_content", "stability",
            "automatic1111", "fal_queue", "replicate_predictions", "bfl", "ideogram", "recraft",
            "leonardo", "adobe_firefly", "mcp_proxy", "comfyui", "aws_bedrock", "microsoft_foundry",
        }
        for item in build_image_generation_table(ROOT)["providers"]:
            with self.subTest(provider=item["id"]):
                capabilities = item["capabilities"]
                self.assertIs(capabilities["one_image_per_call"], True)
                self.assertTrue(capabilities["alpha_verification"])
                self.assertTrue(capabilities["fallback_if_no_alpha"])
                self.assertTrue(capabilities["fallback_if_no_edits"])
                self.assertTrue(item["supported_coding_environments"])
                if item["route"]["kind"] == "stdio_adapter":
                    self.assertIn(item["route"]["api_protocol"], implemented_protocols)

    def test_model_labels_match_the_adapter_allowlist(self) -> None:
        for provider in build_image_generation_table(ROOT)["providers"]:
            supported = provider["route"].get("supported_models", [])
            if supported:
                with self.subTest(provider=provider["id"]):
                    self.assertEqual(len(provider["models"]), len(supported))

    def test_hoi4_imagegen_is_the_default_route_and_midjourney_is_manual_only(self) -> None:
        providers = {item["id"]: item for item in build_image_generation_table(ROOT)["providers"]}
        route = providers["hoi4_imagegen"]["route"]
        self.assertEqual(route["kind"], "release_binary")
        self.assertEqual(route["auth_method"], "chatgpt_login")
        self.assertEqual(route["server_id"], "hoi4_imagegen")
        self.assertEqual(route["component_id"], "imagegen.hoi4_imagegen")
        self.assertEqual(route["source_repository"], "https://github.com/klimPaskov/hoi4-imagegen-mcp")
        for group in ("icon", "picture", "portrait", "flag", "unit", "interface"):
            self.assertEqual(route["tool_names"][group], f"hoi4.image_{group}")
        self.assertEqual(route["tool_names"]["families"], "hoi4.image_families")
        self.assertEqual(route["tool_arguments"]["family"], "family")
        self.assertNotIn("gpt-image-1", json.dumps(providers))
        self.assertEqual(providers["midjourney_manual"]["availability"], "manual_only")
        self.assertEqual(providers["midjourney_manual"]["route"]["kind"], "manual")
        self.assertEqual(providers["codex_native"]["route"]["requires_primary_coding_environment"], "codex")

    def test_codex_uses_its_native_tool_contract_and_provider_notes_are_honest(self) -> None:
        providers = {item["id"]: item for item in build_image_generation_table(ROOT)["providers"]}
        codex_args = providers["codex_native"]["route"]["tool_arguments"]
        self.assertEqual(codex_args["reference_images"], "referenced_image_paths")
        self.assertEqual(codex_args["transparent_background"], "transparent_background")
        self.assertIsNone(codex_args["output_path"])
        self.assertIsNone(codex_args["size"])
        self.assertEqual(providers["aws_bedrock"]["route"]["api_protocol"], "aws_bedrock")
        self.assertEqual(providers["aws_bedrock"]["capabilities"]["size_limits"]["maximum_pixels"], 2_359_296)
        self.assertIn("Stable Image Core is text-to-image only", providers["aws_bedrock"]["capabilities"]["reference_images"]["notes"])
        openrouter = providers["openrouter"]
        self.assertFalse(openrouter["capabilities"]["size_limits"]["accepts_dimensions"])
        self.assertIn("aspect ratios", openrouter["capabilities"]["size_limits"]["notes"])
        self.assertEqual(openrouter["route"]["tool_arguments"]["aspect_ratio"], "aspect_ratio")
        self.assertNotIn("width", openrouter["route"]["tool_arguments"])
        self.assertEqual(providers["xai_grok"]["reference_mcp"]["maintenance"], "community")

    def test_provider_markers_cover_every_asset_guidance_entrypoint(self) -> None:
        marker_start = "<!-- HOI4_MOD_SETUP:IMAGE_GENERATION_PROVIDER:START -->"
        marker_end = "<!-- HOI4_MOD_SETUP:IMAGE_GENERATION_PROVIDER:END -->"
        paths = [
            ROOT / "CLAUDE_template.md",
            ROOT / "AGENTS_template.md",
            ROOT / ".claude/skills/hoi4-feature-assets/SKILL.md",
            ROOT / ".claude/skills/hoi4-feature-assets/references/asset-source-rules.md",
            ROOT / ".claude/skills/hoi4-feature-assets/references/generation-and-review.md",
            ROOT / ".claude/agents/hoi4-generated-feature-art.md",
            ROOT / ".claude/agents/hoi4-icon-artist.md",
            ROOT / ".claude/agents/hoi4-portrait-creator.md",
            ROOT / ".claude/agents/hoi4-3d-model-pipeline.md",
        ]
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(text.count(marker_start), 1)
                self.assertEqual(text.count(marker_end), 1)
                self.assertLess(text.index(marker_start), text.index(marker_end))

    def test_hoi4_imagegen_release_binary_route_declares_the_five_verified_targets(self) -> None:
        providers = {item["id"]: item for item in build_image_generation_table(ROOT)["providers"]}
        route = providers["hoi4_imagegen"]["route"]
        self.assertEqual(route["package_version"], "0.2.1")
        self.assertEqual(
            [(field["id"], field["environment_name"]) for field in route["credential_fields"]],
            [("openai_api_key", "OPENAI_API_KEY"), ("gemini_api_key", "GEMINI_API_KEY"),
             ("fal_key", "FAL_KEY"), ("comfyui_api_key", "COMFYUI_API_KEY")])
        binary = route["release_binary"]
        self.assertEqual(binary["version"], route["package_version"])
        self.assertEqual(binary["install_root"], ".tools/image_generation/hoi4-imagegen")
        self.assertEqual(sorted(binary["targets"]), sorted([
            "x86_64-pc-windows-msvc", "aarch64-apple-darwin", "x86_64-apple-darwin",
            "x86_64-unknown-linux-gnu", "aarch64-unknown-linux-gnu"]))
        for triple, target in binary["targets"].items():
            with self.subTest(target=triple):
                archive = "zip" if "windows" in triple else "tar.gz"
                folder = f"hoi4-imagegen-v0.2.1-{triple}"
                self.assertEqual(target["archive"], archive)
                self.assertEqual(
                    target["url"],
                    f"https://github.com/klimPaskov/hoi4-imagegen-mcp/releases/download/v0.2.1/{folder}.{archive}")
                self.assertRegex(target["sha256"], r"^[0-9a-f]{64}$")
                self.assertGreater(target["size"], 0)
                suffix = ".exe" if "windows" in triple else ""
                self.assertEqual(target["entries"], {
                    "mcp": f"{folder}/hoi4-imagegen-mcp{suffix}", "cli": f"{folder}/hoi4-imagegen{suffix}"})
        windows = binary["targets"]["x86_64-pc-windows-msvc"]
        self.assertEqual((windows["size"], windows["sha256"]),
                         (17368464, "6d3cb51928654cb7b4ecd8004b1f91265ddfab9c76f6ef191ed86f29e47302b6"))
        self.assertEqual(providers["hoi4_imagegen"]["reference_mcp"]["version"], "0.2.1")
        self.assertNotIn("release_binary", providers["openai_api"]["route"], "only the hoi4-imagegen route installs a release binary")

    def test_hoi4_imagegen_component_is_a_generated_managed_mcp_component(self) -> None:
        components = {item["id"]: item for item in build_image_generation_components(ROOT)}
        component = components["imagegen.hoi4_imagegen"]
        self.assertEqual(component["category"], "mcp")
        self.assertTrue(component["optional"])
        self.assertEqual(component["source"], {"kind": "generated", "path": ".tools/image_generation/hoi4-imagegen"})
        self.assertNotIn("template_engine", component)
        self.assertEqual(component["destination"],
                         {"path": ".tools/image_generation/hoi4-imagegen/", "ownership": "managed", "outside_project": False})
        self.assertEqual(component["expected_files"], [])
        self.assertEqual(component["validation"], [])

    def test_the_runtime_component_is_the_only_project_local_image_component_besides_the_release_binary(self) -> None:
        components = {item["id"]: item for item in build_image_generation_components(ROOT)}
        self.assertEqual(list(components), ["imagegen.runtime", "imagegen.hoi4_imagegen"])
        self.assertEqual(components["imagegen.runtime"]["source"]["path"], ".tools/image_generation/runtime")
        self.assertFalse((ROOT / ".tools/image_generation/providers").exists(), "the vendored GPTImage provider was removed")
        for provider_component in components.values():
            self.assertEqual(provider_component["platforms"], ["windows", "macos", "linux"])

    def test_runtime_catalog_is_the_canonical_route_allowlist(self) -> None:
        expected = build_image_generation_table(ROOT)
        runtime = json.loads((ROOT / ".tools/image_generation/runtime/provider_catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(runtime["default_provider"], expected["default_provider"])
        self.assertEqual(runtime["model_profiles"], PROVIDERS.build_image_model_profiles())
        self.assertEqual(
            runtime["providers"],
            [
                {key: provider[key] for key in ("id", "display_name", "availability", "route", "capabilities")}
                for provider in expected["providers"]
            ],
        )

    def test_expanded_catalog_profiles_cover_each_selectable_model(self) -> None:
        providers = {item["id"]: item for item in build_image_generation_table(ROOT)["providers"]}
        profiles = PROVIDERS.build_image_model_profiles()
        self.assertEqual(len(profiles["fal_ai"]), 10)
        self.assertEqual(len(profiles["replicate"]), 3)
        self.assertEqual(len(profiles["together_ai"]), 4)
        for provider_id, models in profiles.items():
            self.assertEqual(list(models), providers[provider_id]["route"]["supported_models"])
            self.assertEqual([entry["display_name"] for entry in models.values()], providers[provider_id]["models"])
            self.assertIn(providers[provider_id]["route"]["default_model"], models)
            for model, entry in models.items():
                with self.subTest(provider=provider_id, model=model):
                    self.assertTrue(entry["documentation_urls"])
                    self.assertTrue(all(url.startswith("https://") for url in entry["documentation_urls"]))
                    self.assertTrue(entry["capabilities"]["one_image_per_call"])
        self.assertEqual(profiles["fal_ai"]["fal-ai/bytedance/seedream/v4.5/text-to-image"]["edit_endpoint"], "fal-ai/bytedance/seedream/v4.5/edit")
        self.assertIsNone(profiles["fal_ai"]["fal-ai/recraft/v4/text-to-image"]["edit_endpoint"])
        self.assertEqual(providers["fal_ai"]["route"]["result_format"], "model_defined")


if __name__ == "__main__":
    unittest.main()
