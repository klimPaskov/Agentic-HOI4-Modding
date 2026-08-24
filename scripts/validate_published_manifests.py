"""Validate the single published setup manifest."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

import generate_manifest_evidence as generator


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    manifest = json.loads((ROOT / "hoi4-mod-setup.manifest.json").read_text(encoding="utf-8-sig"))
    schema = json.loads(
        (ROOT / "schemas/hoi4-mod-setup.v2.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(manifest)
    if manifest.get("schema_version") != "2.0.0":
        raise SystemExit("published manifest has the wrong schema major")
    revision = manifest["generated_for_revision"]
    snapshot = generator.git_snapshot(ROOT, revision)
    for component in manifest["components"]:
        if component["expected_files"] != generator.git_evidence_for(component, snapshot):
            raise SystemExit(f"stale file evidence for component {component['id']}")
    print("Published canonical manifest is schema-valid and exact.")


if __name__ == "__main__":
    main()
