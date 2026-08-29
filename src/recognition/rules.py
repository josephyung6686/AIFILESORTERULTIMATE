# src/recognition/rules.py
"""RUNTIME. One compiled recognition release, parsed from bytes the caller supplies.

The shape is `tree_design.catalogue.load_catalogue`'s, copied deliberately: *"An
injected reader rather than a path keeps this module out of the filesystem entirely,
which is what makes the 'no repository scanning' guard checkable by import inspection
rather than by hope."* This module imports no `pathlib`, opens nothing, and reaches
`planning/` never. It also does not fall back to an empty rule set -- an empty
release would make every guard in this package pass by having nothing to recognise.
"""
from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from facts.domains import SCHEMA_IDS, UnknownSchema

from recognition.vocabulary import MANIFEST_VERSION


class RecognitionRulesRequired(ValueError):
    """The compiled rule set is the caller's. This package locates none."""


@dataclass(frozen=True, slots=True)
class SchemaRules:
    """Every compiled rule for one schema, and what was deferred rather than compiled.

    `deferred_readings` is the schema's `recognition.needs_llm` entries, verbatim.
    They are NOT implemented here: each one is a case the research recorded as
    unsettleable by a deterministic rule. They ride on an abstention so the reason
    is stated rather than lost, and so a later P8 stage can pick them up.
    """

    schema_id: str
    context_terms: tuple[str, ...]
    work_type_terms: tuple[str, ...]
    source_types: frozenset[str]
    extensions: frozenset[str]
    file_kind_never_alone: bool
    rows: tuple[str, ...]
    refused_rows: tuple[str, ...]
    deferred_readings: tuple[str, ...]

    @property
    def terms(self) -> tuple[str, ...]:
        """Every authored term, in one sequence. The arity rule counts these."""
        return self.context_terms + self.work_type_terms


@dataclass(frozen=True, slots=True)
class RecognitionRules:
    """One compiled release: the rules, and the identity of what produced them."""

    manifest_version: int
    compiled_rows: int
    refused_rows: int
    schemas: Mapping[str, SchemaRules]

    def schemas_owning(self, term: str) -> tuple[str, ...]:
        """Which schemas authored this exact term, in `SCHEMA_IDS` order.

        A term several schemas authored discriminates between none of them, and the
        detector needs no threshold to say so: it scores every owner equally, the
        candidates tie, and a tie is an abstention.
        """
        return tuple(schema_id for schema_id in SCHEMA_IDS
                     if schema_id in self.schemas
                     and term in self.schemas[schema_id].terms)


def _sequence(raw: object, *, what: str) -> tuple[str, ...]:
    if isinstance(raw, str) or not isinstance(raw, (list, tuple)):
        raise RecognitionRulesRequired(
            f"{what} is a sequence of strings in a compiled manifest, not {raw!r}")
    for value in raw:
        if not isinstance(value, str):
            raise RecognitionRulesRequired(f"{what} holds {value!r}, not a string")
    return tuple(raw)


def _schema(schema_id: str, raw: object) -> SchemaRules:
    if not isinstance(raw, Mapping):
        raise RecognitionRulesRequired(
            f"the entry for {schema_id!r} is not a compiled schema record")
    declared = raw.get("schema_id")
    if declared != schema_id:
        # Two names for one entry is two rule sets that can disagree about which
        # schema a term activates. Refused rather than resolved by preferring one.
        raise RecognitionRulesRequired(
            f"the manifest files this entry under {schema_id!r} and the entry calls "
            f"itself {declared!r}; a rule set cannot be keyed two ways")
    never_alone = raw.get("file_kind_never_alone")
    if not isinstance(never_alone, bool):
        raise RecognitionRulesRequired(
            f"{schema_id!r} carries no `file_kind_never_alone` flag; the compiler "
            "emits one for every schema")
    readings: list[str] = []
    for entry in raw.get("needs_llm", ()):
        if not isinstance(entry, Mapping):
            raise RecognitionRulesRequired(
                f"{schema_id!r}'s deferred readings are attributed to a row")
        readings.extend(_sequence(entry.get("readings", ()),
                                  what=f"{schema_id}.needs_llm.readings"))
    return SchemaRules(
        schema_id=schema_id,
        context_terms=_sequence(raw.get("context_terms", ()),
                                what=f"{schema_id}.context_terms"),
        work_type_terms=_sequence(raw.get("work_type_terms", ()),
                                  what=f"{schema_id}.work_type_terms"),
        source_types=frozenset(_sequence(raw.get("source_types", ()),
                                         what=f"{schema_id}.source_types")),
        extensions=frozenset(_sequence(raw.get("extensions", ()),
                                       what=f"{schema_id}.extensions")),
        file_kind_never_alone=never_alone,
        rows=_sequence(raw.get("rows", ()), what=f"{schema_id}.rows"),
        refused_rows=_sequence(raw.get("refused_rows", ()),
                               what=f"{schema_id}.refused_rows"),
        deferred_readings=tuple(readings),
    )


def load_rules(read_manifest: Callable[[], str]) -> RecognitionRules:
    """Parse one compiled release. The caller supplies the bytes."""
    if not callable(read_manifest):
        raise RecognitionRulesRequired(
            "the compiled recognition rule set is supplied by the caller; this "
            "package does not locate it, scan for it, or default to an empty one. "
            "A path is not a reader.")
    manifest = json.loads(read_manifest())
    if not isinstance(manifest, Mapping):
        raise RecognitionRulesRequired("a compiled manifest is a JSON object")
    version = manifest.get("manifest_version")
    if version != MANIFEST_VERSION:
        raise RecognitionRulesRequired(
            f"this release reads manifest_version {MANIFEST_VERSION}, and the "
            f"supplied manifest is {version!r}. A manifest whose shape has moved is "
            "a different rule set; reading it optimistically would produce a "
            "detector that silently recognises less than its release claims.")
    raw_schemas = manifest.get("schemas")
    if not isinstance(raw_schemas, Mapping) or not raw_schemas:
        raise RecognitionRulesRequired(
            "a compiled release names at least one schema; an empty rule set would "
            "make every recognition guard pass by having nothing to recognise")
    schemas: dict[str, SchemaRules] = {}
    for schema_id in raw_schemas:
        # `SCHEMA_IDS` is closed and is imported, never counted here: it is widening
        # 10 -> 23 and a number written in this package would go stale in one commit.
        if schema_id not in SCHEMA_IDS:
            raise UnknownSchema(
                f"the manifest carries rules for {schema_id!r}, which is not one of "
                f"the {len(SCHEMA_IDS)} schemas `facts.domains.SCHEMA_IDS` "
                "recognises. A rule that can never activate is a load error.")
        schemas[schema_id] = _schema(schema_id, raw_schemas[schema_id])
    for name in ("compiled_rows", "refused_rows"):
        if not isinstance(manifest.get(name), int):
            raise RecognitionRulesRequired(
                f"a compiled release records {name}; without it a rule set cannot "
                "say how much of the research it was built from")
    return RecognitionRules(
        manifest_version=version,
        compiled_rows=manifest["compiled_rows"],
        refused_rows=manifest["refused_rows"],
        schemas=MappingProxyType(schemas))
