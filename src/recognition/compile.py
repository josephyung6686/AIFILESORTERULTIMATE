# src/recognition/compile.py
"""BUILD TIME. Ratified node rows in, one versioned manifest out.

This is the "later deterministic compiler" `src/tree_design/catalogue.py` names and
`src/facts/fields.py` promises: *"`planning/domains/` is a research and authorship
surface, not a runtime import target. A later deterministic compiler consumes
ratified records and emits a versioned manifest."* Nothing at runtime imports this
module, and `tests/recognition/test_boundaries.py` is the guard that says so.

**What is compilable, and what is not.** Each of the 358 rows carries
`recognition.deterministic` and `recognition.needs_llm`. Both are PROSE -- English
sentences describing a rule, addressed to a human or to a model, quoting `00` inline.
They are not predicates and no compiler can turn them into one. What the same rows
also carry, and what IS machine-readable, is the lexical evidence those sentences
name: `proposed_context_terms`, `work_types`, and `file_kinds`. Those compile.

So this compiler emits the co-occurrence rule the prose states over and over, in
`00`'s own words -- *"BUSIB 4300 becomes a course fact only when the engine finds a
course-code pattern together with academic context such as 'syllabus,' 'lecture,'
'credits,' 'instructor,' or 'semester.'"* -- and records the rest as what it is:
readings deferred to a stage that does not exist yet. It never pretends a sentence
became a matcher.

**A refused row compiles nothing.** 44 rows carry `refuse_node: true`; the research
decided the node does not exist, and one says so inside its own `never_alone`:
"STATED FOR THE REFUSAL RECORD, NOT AS THIS ROW'S RECOGNITION". Compiling its terms
would resurrect a node an adjudication killed. It is named in the manifest anyway --
marked and counted, never silently omitted.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from facts.domains import SCHEMA_IDS, UnknownSchema

from recognition.vocabulary import MANIFEST_VERSION


class MalformedNodeRow(ValueError):
    """A row whose shape the compiler cannot read. Refused, never repaired."""


def _terms(values: object) -> list[str]:
    """Normalise one authored term list. Case and padding are not signal."""
    if values is None:
        return []
    if isinstance(values, str) or not isinstance(values, Sequence):
        raise MalformedNodeRow(
            f"an authored term list is a sequence of strings, not {values!r}; a bare "
            "string would compile into one rule per character")
    out = []
    for value in values:
        if not isinstance(value, str):
            raise MalformedNodeRow(f"{value!r} is not an authored term")
        normalised = " ".join(value.split()).casefold()
        if normalised:
            out.append(normalised)
    return out


def _file_kinds(raw: object) -> tuple[list[str], list[str], bool]:
    if not isinstance(raw, Mapping):
        raise MalformedNodeRow(
            "`file_kinds` is rule 14's `file_kind_plausible` edge, serialised; a row "
            f"without one states no plausible kind at all, not {raw!r}")
    source_types = [value.casefold() for value in _list(raw.get("source_types"))]
    extensions = [value.casefold() for value in _list(raw.get("extensions"))]
    never_alone = raw.get("never_alone")
    if not isinstance(never_alone, bool):
        raise MalformedNodeRow(
            f"`file_kinds.never_alone` is a flag, not {never_alone!r}. All 358 rows "
            "set it true; it is compiled rather than assumed so a row that ever "
            "turns it off becomes visible instead of silently widening the rule.")
    return source_types, extensions, never_alone


def _list(values: object) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str) or not isinstance(values, Sequence):
        raise MalformedNodeRow(f"expected a sequence of strings, got {values!r}")
    for value in values:
        if not isinstance(value, str):
            raise MalformedNodeRow(f"{value!r} is not a string")
    return list(values)


def _empty_schema(schema_id: str) -> dict[str, Any]:
    return {
        "schema_id": schema_id,
        "context_terms": set(),
        "work_type_terms": set(),
        "source_types": set(),
        "extensions": set(),
        "file_kind_never_alone": True,
        "rows": [],
        "refused_rows": [],
        "needs_llm": [],
        "never_alone_rows": [],
    }


def compile_rules(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """One manifest from any iterable of ratified node rows.

    Pure and order-independent: every collection is a set while it accumulates and
    is sorted on the way out, so two runs over the same rows in any order produce
    byte-identical JSON. A release identity that changed when a directory listing
    changed would make two identical rule sets look like two rule sets.
    """
    schemas: dict[str, dict[str, Any]] = {}
    compiled_rows = 0
    refused = 0

    for raw in rows:
        compiled_rows += 1
        row_id = raw.get("id")
        if not isinstance(row_id, str) or not row_id:
            raise MalformedNodeRow(f"a node row carries an id; got {row_id!r}")
        schema_id = raw.get("schema_id")
        # The closed vocabulary, checked before anything else is read. `SCHEMA_IDS`
        # is imported rather than counted: it is widening 10 -> 23 underneath this
        # package and a number written here would go stale in one commit.
        if schema_id not in SCHEMA_IDS:
            raise UnknownSchema(
                f"{row_id!r} names schema {schema_id!r}, which is not one of the "
                f"{len(SCHEMA_IDS)} schemas `facts.domains.SCHEMA_IDS` recognises. A "
                "rule for an unrecognised schema can never activate, so it is a load "
                "error rather than an unreachable entry.")
        schema = schemas.setdefault(schema_id, _empty_schema(schema_id))

        recognition = raw.get("recognition")
        if not isinstance(recognition, Mapping):
            raise MalformedNodeRow(
                f"{row_id!r} carries no `recognition` object; all 358 rows do")

        if raw.get("refuse_node"):
            refused += 1
            schema["refused_rows"].append(row_id)
            continue

        schema["rows"].append(row_id)

        context = set(_terms(raw.get("proposed_context_terms")))
        context |= set(_terms(recognition.get("proposed_context_terms")))
        work_types = set(_terms(raw.get("work_types")))
        schema["context_terms"] |= context
        schema["work_type_terms"] |= work_types

        source_types, extensions, never_alone = _file_kinds(raw.get("file_kinds"))
        schema["source_types"].update(source_types)
        schema["extensions"].update(extensions)
        schema["file_kind_never_alone"] = (
            schema["file_kind_never_alone"] and never_alone)

        readings = _list(recognition.get("needs_llm"))
        if readings:
            # Verbatim and attributed. These are NOT implemented: they are the cases
            # the research recorded as unsettleable by a deterministic rule, carried
            # so an abstention can state WHICH reading it could not make.
            schema["needs_llm"].append({"row": row_id, "readings": list(readings)})

        cautions = _list(recognition.get("never_alone"))
        if cautions:
            # Counted and attributed, never copied. The never-alone DISCIPLINE is
            # compiled into the arity rule `detector.py` applies -- one matched term
            # never activates a schema. Carrying the 3,245 sentences here as well
            # would be a second, non-executable home for a rule already enforced,
            # and a second home for one rule is this project's named defect.
            schema["never_alone_rows"].append(
                {"row": row_id, "cautions": len(cautions)})

    compiled: dict[str, Any] = {
        "manifest_version": MANIFEST_VERSION,
        "compiled_rows": compiled_rows,
        "refused_rows": refused,
        "schemas": {},
    }
    for schema_id in sorted(schemas):
        schema = schemas[schema_id]
        work_type_terms = schema["work_type_terms"]
        # ONE HOME PER TERM, AND THE HOME IS `work_types`. The arity rule counts
        # distinct terms, so a term filed twice would be one match wearing two
        # roles -- but WHICH role it keeps is not arbitrary, because the roles are
        # not symmetrical. `detector.says_what_the_file_is` reads work types and
        # nothing else, and it is the whole of the guard that decides whether one
        # of `00`'s four safety domains may protect a file.
        #
        # Subtracting the other way round is what shipped, and it meant any row
        # proposing a word as CONTEXT erased that word's work-type role for the
        # entire schema -- including when the schema's OWN row had authored it as
        # a work type. Measured over the 358 shipped rows: 171 authored work types
        # lost their role, 21 of them in the four safety domains. `finance` lost
        # `statement`, `invoice` and `receipt`; `legal` lost `power of attorney`;
        # `medical` lost `discharge summary`. Run against the shipped manifest, a
        # power of attorney and a discharge summary both came back UNPROTECTED --
        # the guard could not see the terms that say what those files are.
        #
        # So a term the research authored as a work type stays one, and a sibling
        # row's context proposal for the same word no longer disarms it.
        compiled["schemas"][schema_id] = {
            "schema_id": schema_id,
            "context_terms": sorted(schema["context_terms"] - work_type_terms),
            "work_type_terms": sorted(work_type_terms),
            "source_types": sorted(schema["source_types"]),
            "extensions": sorted(schema["extensions"]),
            "file_kind_never_alone": schema["file_kind_never_alone"],
            "rows": sorted(schema["rows"]),
            "refused_rows": sorted(schema["refused_rows"]),
            "needs_llm": sorted(schema["needs_llm"], key=lambda e: e["row"]),
            "never_alone_rows": sorted(schema["never_alone_rows"],
                                       key=lambda e: e["row"]),
        }
    return compiled


if __name__ == "__main__":                                    # pragma: no cover
    # The build step, spelled out rather than hidden in a shell one-liner so that
    # regenerating `library/recognition.json` is reproducible. This is the ONLY
    # filesystem access in the package, and it is not on any runtime path.
    import json
    import pathlib
    import sys

    nodes = pathlib.Path(sys.argv[1])
    manifest = compile_rules(
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(nodes.glob("*.json")))
    sys.stdout.write(json.dumps(manifest, indent=1, sort_keys=True,
                                ensure_ascii=False) + "\n")
