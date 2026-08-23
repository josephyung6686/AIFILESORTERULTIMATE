# src/facts/fields.py
"""§3.12's closed field catalogue: values may auto-create, fields may not.

§3.12: "The system may create new values when it sees a new course, project, company,
university, or event, but it should not invent new fields automatically."
§3.5: "The LLM is not allowed to invent a new fact schema, create an unsupported
field, or make a free-form filing decision."

So the write path is this module-level authored table, loaded by `create_fields`.
There is no `add_field`, no `register_field`, and no path on which a producer — rules,
the LLM seam, or a user correction — inserts a `fields` row. `get_field` raises
`FieldNotInCatalogue` for an unknown key, which is what makes an unknown field a
refusal rather than a schema change.

**`planning/domains/` is not this catalogue and is never imported.** That directory is
a research artifact of 574 proposed entries. This table's content was READ from
`planning/domains/canonical_fields.json` (37 grep-verified canonical keys) when the
plan was written, with two changes forced by later rulings: `sensitivity_status` is
withheld (NEEDS-JOSEPH C5, open) and `capture_date` is added (Done-means 2(b), §3.2).
Nothing here loads a file at import time or at run time.

**The scope column records where a key is DECLARED; `DOMAIN_FIELDS` records which
§3.11 sentence REFERENCES it.** §3.11 names `project` and `artifact type` under both
Research and Code, and one concept gets one stored key (the tie-break rule), so those
two are declared at `research` and referenced by `code`.

**§3.8's four roles split on destination eligibility (D9).** §3.8: "It should avoid
using authorship or creator identity as a destination dimension" — so `authored_by`
and `our_firm`, the two authorship-side identities, are never destination-eligible.
`target_school` and `client` are targets rather than authorship, and §3.8 "places a
document's purpose, project, subject, or target above its authorship", so both ARE
eligible. D9 overrules the earlier reading in which all four were FALSE.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from evidence_shape.vocabulary import check

from database_agent.db import transaction

from facts.schema import create_facts_schema
from facts.vocabulary import FIELD_SCOPES, VALUE_KINDS

__all__ = [
    "DOMAIN_FIELDS", "FIELDS_COLUMNS", "FIELD_ROWS", "FIELD_SCOPES", "ROLE_FIELDS",
    "UNIVERSAL_FIELDS", "VALUE_KINDS", "FieldNotInCatalogue", "FieldRow",
    "create_fields", "fields_in_scope", "get_field",
]


class FieldNotInCatalogue(KeyError):
    """A producer named a field §3.12 does not let it create.

    Raised instead of inserting a row: "it should not invent new fields
    automatically" is enforced by there being no code that could.
    """


@dataclass(frozen=True, slots=True)
class FieldRow:
    """One row of the catalogue, in the SPEC's column order."""

    field_key: str
    display_name: str
    scope: str
    value_kind: str
    normalizer_id: str | None
    destination_eligible: bool
    multiplicity: str | None


#: The stored columns, asserted against `PRAGMA table_info(fields)`.
FIELDS_COLUMNS: tuple[str, ...] = (
    "field_key", "display_name", "scope", "value_kind",
    "normalizer_id", "destination_eligible", "multiplicity",
)


def _row(field_key: str, display_name: str, scope: str, value_kind: str,
         destination_eligible: bool) -> FieldRow:
    """One catalogue row. `normalizer_id` and `multiplicity` are NULL on every row:
    per-field normalizers are Deferred and multiplicity is open question 6."""
    return FieldRow(field_key=field_key, display_name=display_name, scope=scope,
                    value_kind=value_kind, normalizer_id=None,
                    destination_eligible=destination_eligible, multiplicity=None)


#: §3.11: "a small shared set of universal file facts, such as file type, creation
#: date, language, duplicate family, version family, and sensitivity status".
#:
#: FIVE of that six are here. `sensitivity_status` is WITHHELD: NEEDS-JOSEPH C5 is
#: open (P7's SPEC wants it first-class; D2 makes P7's ClassificationRecord
#: authoritative and `files.sensitivity_state` its projection; round 1 F-2 found the
#: field has no producer), and the instruction is to create no such row either way.
#: This is knowingly at odds with SPEC Done-means 2's "all six"; do not close it by
#: adding the row.
_UNIVERSAL_3_11: tuple[FieldRow, ...] = (
    _row("file_type", "file type", "universal", "string", False),
    _row("creation_date", "creation date", "universal", "date", False),
    _row("language", "language", "universal", "string", False),
    _row("duplicate_family", "duplicate family", "universal", "identifier", False),
    _row("version_family", "version family", "universal", "identifier", False),
)

#: P6's one recorded addition to the universal list. §3.9: "It may be supported more
#: weakly by a tightly bounded download session." §4.2 requires it retrievable. It is
#: not `purpose` — the session names no purpose value — and it is never a folder
#: level, because a session is a clue and a review aid, not proof of topic.
_DOWNLOAD_SESSION: tuple[FieldRow, ...] = (
    _row("download_session", "download session", "universal", "identifier", False),
)

#: §3.8: "distinct facets, such as authored_by and target_school, or our_firm and
#: client" — the design's own spelling, underscores included, so `display_name` keeps
#: it rather than inventing English the design does not use.
#:
#: D9: authorship (`authored_by`, and `our_firm` as firm-side identity) is never
#: destination-eligible. `target_school` and `client` ARE — they are targets, not
#: authorship. D8: the stored key is `target_school`.
#:
#: They take `scope = "universal"`: no §3.11 domain sentence names any of them, and
#: FIELD_SCOPES has no eighth member to hold them. `authored_by` in particular is
#: produced from document metadata on any file, in any domain (§3.8's demotion tier).
_ROLES_3_8: tuple[FieldRow, ...] = (
    _row("authored_by", "authored_by", "universal", "string", False),
    _row("target_school", "target_school", "universal", "string", True),
    _row("our_firm", "our_firm", "universal", "string", False),
    _row("client", "client", "universal", "string", True),
)

#: §3.11: "Academic files may use school, term, course, instructor, and work type."
#: D6: the stored key is `subject`; "course" is the design's prose for the same field
#: and survives inside quotations only. §3.2: "the system can create facts such as
#: subject = BUSIB 4300."
#:
#: `instructor` is not destination-eligible: §3.11's Academic template is school →
#: term → course → work type, and §3.8 disfavours person-identity collectors.
_ACADEMIC: tuple[FieldRow, ...] = (
    _row("school", "school", "academic", "string", True),
    _row("term", "term", "academic", "string", True),
    _row("subject", "subject", "academic", "string", True),
    _row("instructor", "instructor", "academic", "string", False),
    _row("work_type", "work type", "academic", "enum", True),
)

#: §3.11: "College application files may use target university, application cycle,
#: application document type, and purpose."
#:
#: `purpose` stays exactly where that sentence puts it. No per-domain `purpose` clone
#: is minted; a purpose-coherent packet outside admissions activates the nearest
#: schema on its own evidence or falls through to residual.
#: D8 IS VIOLATED HERE, AND SAYING SO IS THE POINT (NEEDS-JOSEPH D8, open).
#: D8 rules that "`target_school` is the stored key; 'target university' (§3.11) is an
#: alias, never a second key" -- and the catalogue ships BOTH `target_school`
#: (`_UNIVERSAL`) and `target_university` below, so two live keys answer to one
#: concept and a fact can be written under either. Task 12's own ruling permits the
#: pair "with a NEEDS-JOSEPH note" pending Joseph, and this is that note; it was
#: missing, so the violation was silent rather than open.
#:
#: Closing it is Joseph's, not this task's: dropping the row changes the closed
#: catalogue's row count, and choosing which key survives decides whether stored
#: `college_applications` facts migrate.
_COLLEGE_APPLICATIONS: tuple[FieldRow, ...] = (
    _row("target_university", "target university", "college_applications", "string", True),
    _row("application_cycle", "application cycle", "college_applications", "string", True),
    _row("application_document_type", "application document type",
         "college_applications", "enum", True),
    _row("purpose", "purpose", "college_applications", "string", True),
)

#: §3.11: "Research files may use project, stage, artifact type, lab, and venue."
#: `project` and `artifact_type` are DECLARED here and REFERENCED by `code`.
_RESEARCH: tuple[FieldRow, ...] = (
    _row("project", "project", "research", "string", True),
    _row("stage", "stage", "research", "string", True),
    _row("artifact_type", "artifact type", "research", "enum", True),
    _row("lab", "lab", "research", "string", True),
    _row("venue", "venue", "research", "string", True),
)

#: §3.11: "Finance files may use institution, account type, tax year, and record type."
_FINANCE: tuple[FieldRow, ...] = (
    _row("institution", "institution", "finance", "string", True),
    _row("account_type", "account type", "finance", "string", True),
    _row("tax_year", "tax year", "finance", "string", True),
    _row("record_type", "record type", "finance", "enum", True),
)

#: §3.11: "Photos may use capture year, event, location, people, camera information,
#: and media type."
#:
#: Plus `capture_date`, which the design gives no scope. §3.2: "an EXIF field called
#: DateTimeOriginal is raw metadata; capture date = 2026-07-17 is the file fact
#: derived from it." Its only producer is an image-metadata observation, so it is
#: declared here rather than as an eighth universal field; the Photos template's time
#: dimension is `capture_year`, so the date itself is not destination-eligible.
#:
#: `people` and `camera_information` are not destination-eligible: §3.11's Photos
#: template is year → event, and person-folders are privacy-loaded (§8.4). Widening
#: either is Joseph's call, never a schema's.
_PHOTOS: tuple[FieldRow, ...] = (
    _row("capture_year", "capture year", "photos", "string", True),
    _row("event", "event", "photos", "string", True),
    _row("location", "location", "photos", "string", True),
    _row("people", "people", "photos", "string", False),
    _row("camera_information", "camera information", "photos", "string", False),
    _row("media_type", "media type", "photos", "enum", True),
    _row("capture_date", "capture date", "photos", "date", False),
)

#: §3.11: "Code files may use project, repository, programming language, and artifact
#: type." `project` and `artifact_type` are declared under Research.
#:
#: `programming_language` is not destination-eligible: the design treats code projects
#: as structural units whose existing layout is preserved, and scattering a project by
#: language would break that.
_CODE: tuple[FieldRow, ...] = (
    _row("repository", "repository", "code", "string", True),
    _row("programming_language", "programming language", "code", "string", False),
)

#: The catalogue, in declaration order. Thirty-seven rows.
FIELD_ROWS: tuple[FieldRow, ...] = (
    *_UNIVERSAL_3_11,
    *_DOWNLOAD_SESSION,
    *_ROLES_3_8,
    *_ACADEMIC,
    *_COLLEGE_APPLICATIONS,
    *_RESEARCH,
    *_FINANCE,
    *_PHOTOS,
    *_CODE,
)

#: §3.11's universal list (five of six, C5) plus §3.9's download session.
UNIVERSAL_FIELDS: tuple[str, ...] = tuple(
    row.field_key for row in (*_UNIVERSAL_3_11, *_DOWNLOAD_SESSION)
)

#: §3.8's four role fields.
ROLE_FIELDS: tuple[str, ...] = tuple(row.field_key for row in _ROLES_3_8)

#: §3.11's six domain sentences, literal — the keys each REFERENCES, which is not the
#: same question as which scope declares them. `project` and `artifact_type` appear
#: under two domains and are one row each.
DOMAIN_FIELDS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "academic": tuple(row.field_key for row in _ACADEMIC),
    "college_applications": tuple(row.field_key for row in _COLLEGE_APPLICATIONS),
    "research": tuple(row.field_key for row in _RESEARCH),
    "finance": tuple(row.field_key for row in _FINANCE),
    "photos": tuple(row.field_key for row in _PHOTOS),
    "code": ("project", "repository", "programming_language", "artifact_type"),
})


def create_fields(conn: sqlite3.Connection) -> None:
    """Load the authored catalogue. Idempotent, and the only writer of this table.

    There is deliberately no counterpart that adds a row (§3.12, §3.5). A drifted
    row raises `NotInVocabulary` through P4's `check` rather than being stored.
    """
    create_facts_schema(conn)
    with transaction(conn):
        for row in FIELD_ROWS:
            check(row.scope, FIELD_SCOPES, name="field scope")
            check(row.value_kind, VALUE_KINDS, name="value_kind")
            conn.execute(
                "INSERT OR IGNORE INTO fields (field_key, display_name, "
                "scope, value_kind, normalizer_id, destination_eligible, "
                "multiplicity) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (row.field_key, row.display_name, row.scope,
                 row.value_kind, row.normalizer_id,
                 1 if row.destination_eligible else 0, row.multiplicity),
            )


def get_field(conn: sqlite3.Connection, field_key: str) -> sqlite3.Row:
    """The catalogue row for `field_key`.

    Raises `FieldNotInCatalogue` for anything the catalogue does not carry —
    including `course` (D6: the design's prose, not a key) and `sensitivity_status`
    (D7: P7's `ClassificationRecord` is the sole home and `files.sensitivity_state`
    its projection, so P6 creates no such row; NEEDS-JOSEPH C5 is the open question
    behind it).
    """
    row = conn.execute(
        "SELECT * FROM fields WHERE field_key = ?", (field_key,)
    ).fetchone()
    if row is None:
        raise FieldNotInCatalogue(
            f"{field_key!r} is not in the field catalogue. §3.12: the system 'should "
            f"not invent new fields automatically'; §3.5: the LLM may not 'create an "
            f"unsupported field'. Adding one is a design decision, not a write."
        )
    return row


def fields_in_scope(conn: sqlite3.Connection, scope: str) -> list[sqlite3.Row]:
    """The rows DECLARED at `scope`, in catalogue order.

    Not the same question as `DOMAIN_FIELDS[scope]`, which is the §3.11 sentence's
    own list: `project` and `artifact_type` are declared at `research` and referenced
    by `code`, so `fields_in_scope(conn, "code")` returns two rows where
    `DOMAIN_FIELDS["code"]` names four.
    """
    check(scope, FIELD_SCOPES, name="field scope")
    return list(conn.execute(
        "SELECT * FROM fields WHERE scope = ? ORDER BY rowid", (scope,)
    ))
