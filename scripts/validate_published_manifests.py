"""Validate both published setup-manifest compatibility routes."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

import generate_manifest_evidence as generator


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    v2 = json.loads((ROOT / "hoi4-mod-setup.v2.manifest.json").read_text(encoding="utf-8-sig"))
    legacy = json.loads((ROOT / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8-sig"))
    schema = json.loads(
        (ROOT / "schemas/hoi4-mod-setup.v2.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(v2)
    if v2.get("schema_version") != "2.0.0" or legacy.get("schema_version") != "1.0.0":
        raise SystemExit("published manifest schema routes have the wrong major")
    expected_legacy = json.loads(json.dumps(v2))
    expected_legacy["schema_version"] = "1.0.0"
    for component in expected_legacy["components"]:
        for validation in component.get("validation", []):
            validation.pop("parameters", None)
    if legacy != expected_legacy:
        raise SystemExit("schema-1 compatibility manifest is not the exact v2 projection")
    revision = v2["generated_for_revision"]
    snapshot = generator.git_snapshot(ROOT, revision)
    for component in v2["components"]:
        if component["expected_files"] != generator.git_evidence_for(component, snapshot):
            raise SystemExit(f"stale file evidence for component {component['id']}")
    print("Published schema-1 and schema-2 manifests are compatible and exact.")


if __name__ == "__main__":
    main()
