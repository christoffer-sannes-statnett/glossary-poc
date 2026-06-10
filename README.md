# Business Glossary

Single source of truth for business terms used across systems, teams, and languages (NO/NN/EN).

Terms are maintained as Turtle (`.ttl`) files in this repo, one file per concept. On every merge to `main`, the CI pipeline validates all terms and publishes a searchable HTML page and a merged `glossary.ttl` to GitHub Pages.

**[→ Browse the glossary](https://christoffer-sannes-statnett.github.io/glossary-poc/)**

---

## Contributing — no Git required

Use the GitHub issue forms to suggest changes. A reviewer will label your issue and a pull request is created automatically.

- **[New term](../../issues/new?template=new_term.yml)** — propose a term to add
- **[Edit term](../../issues/new?template=edit_term.yml)** — correct a label or description
- **[Deprecate term](../../issues/new?template=deprecate_term.yml)** — mark a term as replaced or removed

---

## Contributing — Turtle

Each term is a single `.ttl` file in `terms/`. The filename stem must match the `skos:notation`.

```turtle
@prefix adms: <http://www.w3.org/ns/adms#> .
@prefix elhub: <https://glossary.elhub.no/concept/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

elhub:MY_TERM a skos:Concept ;
    skos:notation "MY_TERM" ;
    skos:prefLabel "My term"@en,
        "Mitt begrep"@no ;
    skos:definition "Optional explanation in English."@en,
        "Valgfri forklaring på norsk."@no ;
    skos:inScheme <https://glossary.elhub.no/scheme/business-glossary> ;
    adms:status "active" .
```

**Rules:**
- Filename stem must be `SCREAMING_SNAKE_CASE`, ASCII only (no Æ/Ø/Å)
- `skos:notation` must match the filename stem exactly
- `@no` (Bokmål) and `@en` and `@nn` (Nynorsk) labels are required — a term is valid in all three languages even when `@no` and `@nn` are spelled identically
- Descriptions (`skos:definition`) are optional for self-explanatory terms
- Hierarchy is expressed via `skos:broader` on the narrower term only
- To deprecate, set `adms:status "deprecated"` and optionally add `owl:sameAs <replacement IRI>`

**Local setup:**

```bash
uv sync --group dev
uv run pre-commit install          # runs checks on every commit
uv run python scripts/generate.py  # preview output in dist/
```

---

## Repository structure

| Path | Description |
|---|---|
| `terms/<SLUG>.ttl` | One SKOS concept per file — source of truth |
| `rdf/scheme.ttl` | `skos:ConceptScheme` declaration |
| `rdf/domain.ttl` | Lightweight OWL ontology scaffold |
| `dist/` | Generated at CI time, not committed |

---

## For developers

The pipeline publishes machine-readable artefacts on every merge to `main`.

| Endpoint | Description |
|---|---|
| [`/glossary.ttl`](https://christoffer-sannes-statnett.github.io/glossary-poc/glossary.ttl) | Merged Turtle graph — all terms + scheme |
| [`/terms.json`](https://christoffer-sannes-statnett.github.io/glossary-poc/terms.json) | Full list of all terms with all fields |
| [`/no.json`](https://christoffer-sannes-statnett.github.io/glossary-poc/no.json) | Flat `slug → Bokmål label` map |
| [`/nn.json`](https://christoffer-sannes-statnett.github.io/glossary-poc/nn.json) | Flat `slug → Nynorsk label` map |
| [`/en.json`](https://christoffer-sannes-statnett.github.io/glossary-poc/en.json) | Flat `slug → English label` map |
| [`/children.json`](https://christoffer-sannes-statnett.github.io/glossary-poc/children.json) | Reverse index: `parent slug → [child slugs]` |

**Turtle / SPARQL** — load `glossary.ttl` directly into any triple store or RDF tool:
```bash
curl https://christoffer-sannes-statnett.github.io/glossary-poc/glossary.ttl
```

**Runtime fetch (JSON)** — always reflects the current glossary:
```js
const terms = await fetch('https://christoffer-sannes-statnett.github.io/glossary-poc/terms.json')
  .then(r => r.json())

// Look up a term
const mp = terms.find(t => t.slug === 'MP')
// { slug: 'MP', no: 'Målepunkt', en: 'Metering Point', ... }

// List parents of a term
mp.parents  // e.g. ['EAV']

// List children of a parent (client-side filter)
terms.filter(t => (t.parents ?? []).includes('PROD_GROUP'))
```

**Children index** — pre-built reverse lookup:
```js
const children = await fetch('https://christoffer-sannes-statnett.github.io/glossary-poc/children.json')
  .then(r => r.json())

children['PROD_GROUP']  // ['HYDRO', 'SOLAR', ...]
```

**Locale map** — useful for dropdown labels, enum display names:
```js
const labels = await fetch('https://christoffer-sannes-statnett.github.io/glossary-poc/no.json')
  .then(r => r.json())

labels['MP']  // → "Målepunkt"
```

**Build-time** — download `terms.json` in your CI pipeline and bundle it with your app to avoid a runtime dependency on this service.

---

## How it works

```
terms/*.ttl  ─┐
rdf/*.ttl    ─┴─  validate  →  (CI passes)
                  generate  →  dist/glossary.ttl      (merged Turtle graph)
                               dist/terms.json
                               dist/{no,nn,en}.json   (locale maps)
                               dist/index.html        (GitHub Pages)
```

CI runs on every PR (validate only) and on every merge to `main` (validate + publish).
