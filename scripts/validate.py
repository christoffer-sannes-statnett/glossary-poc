#!/usr/bin/env python3
"""
validate.py — validates all terms/*.ttl against SKOS structural rules.
Exits non-zero on any error. Used by the PR check CI workflow.
"""

import re
import sys
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS

ROOT = Path(__file__).parent.parent
TERMS_DIR = ROOT / "terms"
SCHEME_IRI = URIRef("https://glossary.elhub.no/scheme/business-glossary")
ELHUB = Namespace("https://glossary.elhub.no/concept/")
SCREAMING_SNAKE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def main() -> None:
    errors: list[str] = []
    notations_seen: dict[str, str] = {}  # notation → filename
    concepts_seen: set[str] = set()      # notation strings

    term_files = sorted(TERMS_DIR.glob("*.ttl"))
    if not term_files:
        print("No term files found in terms/", file=sys.stderr)
        sys.exit(1)

    parsed: list[tuple[str, Graph, URIRef, str]] = []

    for path in term_files:
        g = Graph()
        try:
            g.parse(path, format="turtle")
        except Exception as e:
            errors.append(f"{path.name}: Turtle parse error — {e}")
            continue

        concepts = list(g.subjects(RDF.type, SKOS.Concept))
        if len(concepts) != 1:
            errors.append(
                f"{path.name}: expected exactly 1 skos:Concept, found {len(concepts)}"
            )
            continue

        concept = concepts[0]

        # notation must exist and match filename stem
        notations = list(g.objects(concept, SKOS.notation))
        if not notations:
            errors.append(f"{path.name}: missing skos:notation")
            continue
        notation = str(notations[0])

        if notation != path.stem:
            errors.append(
                f"{path.name}: skos:notation '{notation}' does not match filename '{path.stem}'"
            )
            continue

        if not SCREAMING_SNAKE.match(notation):
            errors.append(
                f"{path.name}: notation '{notation}' is not valid SCREAMING_SNAKE_CASE"
            )
            continue

        if notation in notations_seen:
            errors.append(
                f"{path.name}: duplicate notation '{notation}' (also in {notations_seen[notation]})"
            )
            continue

        # required: at least @en and @no prefLabel; no duplicate language tags allowed
        labels: dict[str, str] = {}
        for obj in g.objects(concept, SKOS.prefLabel):
            if not isinstance(obj, Literal) or not obj.language:
                errors.append(
                    f"{path.name}: skos:prefLabel must be a language-tagged literal, got: {obj!r}"
                )
                continue
            lang = str(obj.language)
            if lang in labels:
                errors.append(
                    f"{path.name}: duplicate skos:prefLabel for language @{lang}"
                )
            else:
                labels[lang] = str(obj)
        for lang in ("en", "no", "nn"):
            if lang not in labels:
                errors.append(f"{path.name}: missing skos:prefLabel @{lang}")

        # required: skos:inScheme pointing to the canonical scheme
        schemes = list(g.objects(concept, SKOS.inScheme))
        if SCHEME_IRI not in schemes:
            errors.append(
                f"{path.name}: missing skos:inScheme <{SCHEME_IRI}>"
            )

        notations_seen[notation] = path.name
        concepts_seen.add(notation)
        parsed.append((path.name, g, concept, notation))

    # Build broader graph for cycle detection: notation → set of broader notations
    broader_map: dict[str, set[str]] = {notation: set() for _, _, _, notation in parsed}
    for filename, g, concept, notation in parsed:
        for broader in g.objects(concept, SKOS.broader):
            broader_notation = str(broader).removeprefix(str(ELHUB))
            if broader_notation == notation:
                errors.append(f"{filename}: concept cannot be its own skos:broader")
            elif broader_notation not in concepts_seen:
                errors.append(
                    f"{filename}: skos:broader target '{broader_notation}' does not exist"
                )
            else:
                broader_map[notation].add(broader_notation)

    # Second pass: cycle detection via DFS
    def has_cycle(start: str, visited: set[str], path: set[str]) -> bool:
        if start in path:
            return True
        if start in visited:
            return False
        visited.add(start)
        path.add(start)
        for parent in broader_map.get(start, set()):
            if has_cycle(parent, visited, path):
                return True
        path.discard(start)
        return False

    visited: set[str] = set()
    for notation in broader_map:
        if has_cycle(notation, visited, set()):
            errors.append(f"{notation}.ttl: skos:broader cycle detected")

    if errors:
        print("Validation failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(f"All {len(concepts_seen)} terms valid.")


if __name__ == "__main__":
    main()
