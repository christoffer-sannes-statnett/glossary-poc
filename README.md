# Business Glossary

Single source of truth for business terms used across systems, teams, and languages (NO/NN/EN).

Terms are maintained as YAML files in this repo. On every merge to `main`, the CI pipeline validates all terms and publishes a searchable HTML page to GitHub Pages.

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
# yaml-language-server: $schema=../schema/term.schema.json
slug: MY_TERM
"no": Mitt begrep
nn: Mitt begrep
en: My term
description_no: >
  Valgfri forklaring på norsk.
description_en: >
  Optional explanation in English.
```

**Rules:**
- `slug` is permanent — choose carefully (SCREAMING_SNAKE_CASE, ASCII only)
- `"no"` must be quoted (YAML 1.1 treats bare `no` as boolean)
- Descriptions are optional for self-explanatory terms
- To deprecate, add `replaces: OTHER_SLUG` — status is inferred automatically

**Local setup:**

```bash
uv sync --group dev
uv run pre-commit install          # runs checks on every commit
uv run python scripts/generate.py  # preview output in dist/
```

---

## For developers

The pipeline publishes machine-readable JSON on every merge to `main`. Use these endpoints to integrate the glossary into your app or service.

| Endpoint | Description |
|---|---|
| [`/terms.json`](https://christoffer-sannes-statnett.github.io/glossary-poc/terms.json) | Full list of all terms with all fields |
| [`/no.json`](https://christoffer-sannes-statnett.github.io/glossary-poc/no.json) | Flat `slug → Bokmål label` map |
| [`/nn.json`](https://christoffer-sannes-statnett.github.io/glossary-poc/nn.json) | Flat `slug → Nynorsk label` map |
| [`/en.json`](https://christoffer-sannes-statnett.github.io/glossary-poc/en.json) | Flat `slug → English label` map |

**Runtime fetch** — always reflects the current glossary:
```js
const terms = await fetch('https://christoffer-sannes-statnett.github.io/glossary-poc/terms.json')
  .then(r => r.json())

const mp = terms.find(t => t.slug === 'MP')
// { slug: 'MP', no: 'Målepunkt', en: 'Metering Point', ... }
```

**Locale map** — useful for dropdown labels, enum display names, column headers:
```js
const labels = await fetch('https://christoffer-sannes-statnett.github.io/glossary-poc/no.json')
  .then(r => r.json())

labels['MP']  // → "Målepunkt"
```

**Build-time** — download `terms.json` in your CI pipeline and bundle it with your app to avoid a runtime dependency on this service.

---

## How it works

```
terms/*.yml  →  validate  →  dist/terms.json
                              dist/{no,nn,en}.json   (locale maps)
                              dist/index.html        (GitHub Pages)
```

CI runs on every PR (validate only) and on every merge to `main` (validate + publish).
