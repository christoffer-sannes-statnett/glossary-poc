#!/usr/bin/env python3
"""
generate.py — reads terms/*.yml, validates against schema/term.schema.json, emits:
  dist/terms.json          full term objects array
  dist/en.json             flat { slug: label } locale map
  dist/no.json             flat { slug: label } locale map
  dist/nn.json             flat { slug: label } locale map
  dist/index.html          self-contained searchable HTML table
"""

import json
import sys
from pathlib import Path

import yaml
import jsonschema

ROOT = Path(__file__).parent.parent
TERMS_DIR = ROOT / "terms"
SCHEMA_FILE = ROOT / "schema" / "term.schema.json"
DIST_DIR = ROOT / "dist"


def load_terms() -> list[dict]:
    with SCHEMA_FILE.open() as f:
        schema = json.load(f)

    terms = []
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

        # Infer status: deprecated if replaces is set, otherwise active
        if "status" not in data:
            data["status"] = "deprecated" if data.get("replaces") else "active"

        terms.append(data)

    # Second pass: validate parent slugs exist and no self-references
    for term in terms:
        for parent in term.get("parents", []):
            if parent == term["slug"]:
                errors.append(f"{term['slug']}.yml: slug cannot list itself as a parent")
            elif parent not in slugs_seen:
                errors.append(f"{term['slug']}.yml: parent slug '{parent}' does not exist")

    if errors:
        print("Validation errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    return terms


def emit_json(terms: list[dict]) -> None:
    DIST_DIR.mkdir(exist_ok=True)

    def clean(t: dict) -> dict:
        out = dict(t)
        for field in ("description_no", "description_en"):
            if field in out and out[field]:
                out[field] = out[field].strip()
        return out

    cleaned = [clean(t) for t in terms]

    (DIST_DIR / "terms.json").write_text(
        json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    for lang in ("en", "no", "nn"):
        locale = {t["slug"]: t[lang] for t in cleaned}
        (DIST_DIR / f"{lang}.json").write_text(
            json.dumps(locale, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # Reverse index: parent slug → list of child slugs
    children: dict[str, list[str]] = {}
    for t in cleaned:
        for parent in t.get("parents") or []:
            children.setdefault(parent, []).append(t["slug"])
    (DIST_DIR / "children.json").write_text(
        json.dumps(children, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def emit_html(terms: list[dict]) -> None:
    template_path = Path(__file__).parent / "template.html"
    template = template_path.read_text(encoding="utf-8")

    rows = []
    for t in terms:
        replaces_cell = ""
        if t.get("replaces"):
            replaces_cell = f'<span class="replaces">→ {t["replaces"]}</span>'

        parents_attr = ",".join(t.get("parents") or [])

        parents_pills = ""
        if t.get("parents"):
            parents_pills = "".join(
                f'<span class="parent-pill">{p}</span>' for p in t["parents"]
            )

        desc_no = (t.get("description_no") or "").strip().replace("\n", " ")
        desc_en = (t.get("description_en") or "").strip().replace("\n", " ")
        desc_cell = desc_no
        if desc_en:
            desc_cell += f'<span class="desc-en">{desc_en}</span>'

        rows.append(
            f'    <tr data-status="{t["status"]}" data-slug="{t["slug"]}" data-parents="{parents_attr}">\n'
            f'      <td class="slug">{t["slug"]}{replaces_cell}</td>\n'
            f'      <td>{t["no"]}</td>\n'
            f'      <td>{t["nn"]}</td>\n'
            f'      <td>{t["en"]}</td>\n'
            f'      <td class="desc">{desc_cell}</td>\n'
            f'      <td class="parents-cell">{parents_pills}</td>\n'
            f'    </tr>'
        )

    html = template.replace("<!-- ROWS_PLACEHOLDER -->", "\n".join(rows))
    (DIST_DIR / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    terms = load_terms()
    emit_json(terms)
    emit_html(terms)
    print(f"Generated {len(terms)} terms → dist/")


if __name__ == "__main__":
    main()
