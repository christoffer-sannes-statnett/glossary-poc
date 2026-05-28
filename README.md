# Business Glossary

Single source of truth for business terms used across systems, teams, and languages (EN/NO/NN).

Terms are maintained as YAML files in this repo. On every merge to `main`, the CI pipeline validates all terms and publishes a searchable HTML page to GitHub Pages — which is also embedded in Confluence.

**[→ Browse the glossary](https://christoffer-sannes-statnett.github.io/glossary-poc/)**

---

## Contributing — no Git required

Use the GitHub issue forms to suggest changes. A reviewer will label your issue and a pull request is created automatically.

- **[New term](../../issues/new?template=new_term.yml)** — propose a term to add
- **[Edit term](../../issues/new?template=edit_term.yml)** — correct a label or description
- **[Deprecate term](../../issues/new?template=deprecate_term.yml)** — mark a term as replaced or removed

---

## Contributing — YAML

Each term is a single file in `terms/`. The filename must match the slug.

```yaml
# terms/MY_TERM.yml
slug: MY_TERM
en: My term
"no": Mitt begrep
nn: Mitt begrep
description_no: >
  Valgfri forklaring på norsk.
description_en: >
  Optional explanation in English.
```

**Rules:**
- `slug` is permanent — choose carefully (SCREAMING_SNAKE_CASE, ASCII only)
- Descriptions are optional for self-explanatory terms
- To deprecate, add `replaces: OTHER_SLUG` — status is inferred automatically
- The `"no"` key must be quoted (YAML 1.1 treats bare `no` as boolean)

**Local setup:**

```bash
uv sync --group dev
uv run pre-commit install   # runs checks on every commit
uv run python scripts/generate.py   # preview output in dist/
```

---

## How it works

```
terms/*.yml  →  validate  →  dist/terms.json
                              dist/{en,no,nn}.json   (locale maps)
                              dist/index.html        (GitHub Pages)
```

CI runs on every PR (validate only) and on every merge to `main` (validate + publish).
