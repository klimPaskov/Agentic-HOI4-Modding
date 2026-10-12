"""Validate the single published setup manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

import generate_manifest_evidence as generator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from live_testing_provider_data import build_live_testing_components, build_live_testing_table
from image_generation_provider_data import build_image_generation_components, build_image_generation_table


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    manifest = json.loads((ROOT / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8-sig"))
    schema = json.loads(
        (ROOT / "schemas/hoi4-mod-setup.v4.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(manifest)
    if not str(manifest.get("schema_version", "")).startswith("4."):
        raise SystemExit("published manifest has the wrong schema major")
    if manifest.get("image_generation") != build_image_generation_table(ROOT):
        raise SystemExit("published image-generation provider table is stale")
    expected_provider_components = {item["id"]: item for item in build_image_generation_components(ROOT)}
    published_provider_components = {
        item["id"]: item for item in manifest["components"] if item["id"].startswith("imagegen.")
    }
    if set(published_provider_components) != set(expected_provider_components):
        raise SystemExit("published image-generation component list is stale")
    for component_id, expected in expected_provider_components.items():
        published = dict(published_provider_components[component_id])
        published.pop("expected_files", None)
        expected.pop("expected_files", None)
        if published != expected:
            raise SystemExit(f"stale image-generation component declaration: {component_id}")
    component_ids = {component["id"] for component in manifest["components"]}
    environment_ids = {environment["id"] for environment in manifest["coding_environments"]}
    provider_ids = {provider["id"] for provider in manifest["image_generation"]["providers"]}
    if manifest["image_generation"]["default_provider"] not in provider_ids:
        raise SystemExit("the default image-generation provider is not declared")
    for provider in manifest["image_generation"]["providers"]:
        route = provider["route"]
        component_id = route.get("component_id")
        if component_id and component_id not in component_ids:
            raise SystemExit(f"undeclared image-generation component for {provider['id']}: {component_id}")
        primary = route.get("requires_primary_coding_environment")
        if primary and primary not in environment_ids:
            raise SystemExit(f"unsupported primary coding environment for {provider['id']}: {primary}")
    if manifest.get("live_testing") != build_live_testing_table():
        raise SystemExit("published live-testing provider table is stale")
    for expected in build_live_testing_components(manifest["components"]):
        actual = next(c for c in manifest["components"] if c["id"] == expected["id"])
        expected.pop("expected_files", None)
        actual = dict(actual)
        actual.pop("expected_files", None)
        if actual != expected:
            raise SystemExit("stale live-testing component: " + expected["id"])
    revision = manifest["generated_for_revision"]
    snapshot = generator.git_snapshot(ROOT, revision)
    for component in manifest["components"]:
        if component["expected_files"] != generator.git_evidence_for(component, snapshot):
            raise SystemExit(f"stale file evidence for component {component['id']}")
    print("Published canonical manifest is schema-valid and exact.")


if __name__ == "__main__":
    main()
