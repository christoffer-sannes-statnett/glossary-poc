# Copilot Review Instructions — Business Glossary

This repo is a business glossary for Elhub. Terms are defined as YAML files in `terms/`. PRs are either hand-authored by developers or auto-generated from GitHub issue forms submitted by non-technical staff.

If everything looks correct, do not leave any comments. Approve silently. Only comment when you have a specific, actionable concern.

## What to focus on

### Slug (`terms/<SLUG>.yml`)
- Must be `SCREAMING_SNAKE_CASE`, ASCII only (no Æ/Ø/Å)
- Must match the filename exactly
- Should reflect how the term is actually used internally — short internal shorthands (e.g. `RECON`, `MP`) are preferred over verbose full names when the team has an established abbreviation
- Flag slugs that are ambiguous, overly generic (e.g. `VALUE`, `TYPE`), or clash with existing terms

### Norwegian labels (`no`, `nn`)
- `no` is Norwegian Bokmål, `nn` is Norwegian Nynorsk — verify these are distinct where applicable, not just the same word copy-pasted
- Check spelling and grammar; domain terms should match official Norwegian energy sector terminology where possible
- If `nn` differs from `no`, verify it is genuine Nynorsk (not Bokmål with minor changes)

### English label (`en`)
- Should be a concise, accurate English equivalent
- Check against established IEC/CIM terminology or Elhub's English documentation where relevant

### Descriptions (`description_no`, `description_en`)
- Both are optional — self-explanatory terms do not need one
- If present: is it clear, concise, and accurate? 1–3 sentences is the target
- Should define the term in a business context, not describe a system implementation
- Must not contain internal system references (DB table names, CIM class names, API paths)

### Deprecated terms (`replaces`)
- If `replaces` is set, verify the referenced slug actually exists in `terms/`
- Check that the replacement term is a genuine semantic successor, not just a rename

## What NOT to flag

- The `"no":` key being quoted — this is intentional (YAML 1.1 boolean workaround)
- Absent `status` field — terms are implicitly `active` if no status is set; this is by design
- Absent `replaces` field — it is optional
- YAML formatting (indentation, trailing newlines) — pre-commit handles this automatically
- The `# yaml-language-server: $schema=` comment line — intentional editor hint

## Approval criteria

Approve if:
- Slug is unambiguous, follows conventions, and matches the filename
- Norwegian labels are correct and Nynorsk is genuinely distinct where provided
- English label is accurate
- Description (if present) is clear and free of internal system details
- No conceptual overlap with existing terms without a `replaces` relationship

Request changes if any of the above are not met, or if the term itself appears to be a duplicate of an existing entry.
