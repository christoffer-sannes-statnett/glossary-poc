#!/usr/bin/env python3
"""
validate.py — validates all terms/*.yml against schema/term.schema.json.
Exits non-zero on any error. Used by the PR check CI workflow.
"""

import json
import sys
from pathlib import Path

import yaml
import jsonschema

ROOT = Path(__file__).parent.parent
TERMS_DIR = ROOT / "terms"
SCHEMA_FILE = ROOT / "schema" / "term.schema.json"


def main() -> None:
    with SCHEMA_FILE.open() as f:
        schema = json.load(f)

    errors = []
    slugs_seen = set()

    for path in sorted(TERMS_DIR.glob("*.yml")):
        with path.open() as f:
            data = yaml.safe_load(f)

        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as e:
            errors.append(f"{path.name}: {e.message}")
            continue

        slug = data["slug"]
        if slug != path.stem:
            errors.append(f"{path.name}: slug '{slug}' does not match filename '{path.stem}'")
            continue

        if slug in slugs_seen:
            errors.append(f"{path.name}: duplicate slug '{slug}'")
            continue

        slugs_seen.add(slug)

    if errors:
        print("Validation failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(f"All {len(slugs_seen)} terms valid.")


if __name__ == "__main__":
    main()
