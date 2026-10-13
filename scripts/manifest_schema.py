"""Select an exact supported manifest schema without accepting unknown majors."""

import json
from pathlib import Path
import re

SCHEMA_FILES = {
    "3": "hoi4-mod-setup.v3.schema.json",
    "4": "hoi4-mod-setup.v4.schema.json",
    "5": "remote-manifest.v5.schema.json",
}


def load_manifest_schema(version: str, root: Path) -> dict:
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("Manifest schema version must be an exact semantic version.")
    name = SCHEMA_FILES.get(version.split(".")[0])
    if name is None:
        raise ValueError("Manifest schema major is unsupported.")
    return json.loads((root / "schemas" / name).read_text(encoding="utf-8"))
