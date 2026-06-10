# Copilot Review Instructions — Business Glossary

This repo is a business glossary for Elhub. Terms are defined as Turtle (`.ttl`) files in `terms/`, one file per concept. PRs are either hand-authored by developers or auto-generated from GitHub issue forms submitted by non-technical staff.

If everything looks correct, do not leave any comments. Approve silently. Only comment when you have a specific, actionable concern.

## Repository structure

- `terms/<SLUG>.ttl` — one SKOS concept per file, the source of truth
- `rdf/scheme.ttl` — the `skos:ConceptScheme` declaration
- `rdf/domain.ttl` — lightweight OWL ontology scaffold
- `dist/` — generated at CI time (not committed); includes `glossary.ttl`, `index.html`, JSON locale files

## What to focus on

### Slug / notation (`terms/<SLUG>.ttl`)
- Filename stem must be `SCREAMING_SNAKE_CASE`, ASCII only (no Æ/Ø/Å)
- `skos:notation` must match the filename stem exactly
- Should reflect how the term is actually used internally — short internal shorthands (e.g. `RECON`, `MP`) are preferred over verbose full names when the team has an established abbreviation
- Flag slugs that are ambiguous, overly generic (e.g. `VALUE`, `TYPE`), or clash with existing terms

### Norwegian labels (`skos:prefLabel @no`, `@nn`)
- `@no` is Norwegian Bokmål, `@nn` is Norwegian Nynorsk
- Both `@no` and `@nn` are required — a term is valid in both languages even when spelled identically
- If `@nn` differs from `@no`, verify it is genuine Nynorsk (not Bokmål with minor changes)
- Check spelling and grammar; domain terms should match official Norwegian energy sector terminology where possible

### English label (`skos:prefLabel @en`)
- Should be a concise, accurate English equivalent
- Check against established IEC/CIM terminology or Elhub's English documentation where relevant

### Descriptions (`skos:definition @no`, `@en`)
- Both are optional — self-explanatory terms do not need one
- If present: is it clear, concise, and accurate? 1–3 sentences is the target
- Should define the term in a business context, not describe a system implementation
- Must not contain internal system references (DB table names, CIM class names, API paths)

### Hierarchy (`skos:broader`)
- Asserted on the narrower term only — do not add `skos:narrower` on the parent
- Verify the referenced concept IRI exists in `terms/`
- No cycles allowed

### Deprecated terms (`adms:status "deprecated"`)
- If `adms:status "deprecated"` is set, check whether `owl:sameAs` points to a replacement concept
- Verify the replacement IRI exists in `terms/`
- Check that the replacement is a genuine semantic successor, not just a rename

## What NOT to flag

- Absent `skos:definition` — optional for self-explanatory terms
- Turtle formatting (blank lines, prefix order) — pre-commit handles this automatically
- `skos:inScheme` pointing to `<https://glossary.elhub.no/scheme/business-glossary>` — required boilerplate, not a concern
- `adms:status "active"` — expected on all active terms

## Approval criteria

Approve if:
- Slug/notation is unambiguous, follows conventions, and matches the filename
- Norwegian labels are correct and `@nn` is genuine Nynorsk where provided
- English label is accurate
- Description (if present) is clear and free of internal system details
- `skos:broader` targets exist and no cycles are introduced
- No conceptual overlap with existing terms without a deprecation relationship

Request changes if any of the above are not met, or if the term appears to be a duplicate of an existing entry.
