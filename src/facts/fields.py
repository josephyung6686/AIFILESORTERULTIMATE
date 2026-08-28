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
a research artifact. This table's content was READ from
`planning/domains/canonical_fields.json` (37 grep-verified canonical keys) when the
plan was written, with two changes forced by later rulings: `sensitivity_status` is
withheld (NEEDS-JOSEPH C5, open) and `capture_date` is added (Done-means 2(b), §3.2).
Nothing here loads a file at import time or at run time, and the adoption below did
not change that: `60`'s rulings were READ and written down, not imported.

**ADOPTED, 2026-08-28: `planning/60-VOCABULARY-RULINGS.md`.** J-1 widens the
recognised schemas 10 -> 23, §4 mints eighteen canonical keys (37 + 18 = 55), and §5
declares a field set for twenty of the twenty-three. Alongside the keys, `60` requires
three things the seven stored columns cannot hold — a `reliability_ceiling`, an alias
list, and a `notes` discriminator — plus reciprocal `role_split` pairs. They live on
`FieldRow` and are asserted in `tests/p6/test_p6_vocabulary_adoption.py`; they are not
stored, because `60` asks for no column and nothing in P6 reads one.

**The scope column records where a key is DECLARED; `DOMAIN_FIELDS` records which
schema REFERENCES it.** §3.11 names `project` and `artifact type` under both Research
and Code, and one concept gets one stored key (the tie-break rule), so those two are
declared at `research` and referenced by `code`. After `60` §5 that split is the rule
rather than the exception: `record_type` is declared at `finance` and referenced by
seven schemas, `project` by eight, and five schemas declare nothing at all. This is
why `facts.domains.active_field_allowlist` is built on `DOMAIN_FIELDS` and not on
declaration scopes — on declarations, an active `creative` could propose no field.

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
    """One row of the catalogue: the SPEC's seven columns, then `60`'s four.

    The first seven are the STORED columns, in the SPEC's own order. The last four
    are authored metadata `60` requires and the `fields` table has no column for:

    * `reliability_ceiling` — `domains/_CONTRACT.md` rule 4, one of §3.13's six states.
      A key claiming `validated` is claiming a RULE will confirm it.
    * `aliases` — strings that must NEVER become keys (`canonical_fields.json`'s own
      rule). Value-level aliases are the `values` table's, never listed here.
    * `role_split` — §3.8's "roles that happen to contain the same entity type",
      declared reciprocally. A one-way pair is a defect a test catches, not care.
    * `notes` — the discriminator that keeps two keys from being filled off one token.

    They are NOT stored. `60` asks for no new column, nothing in P6 reads one, and a
    column with no reader is a claim the product does not make. `create_fields` names
    its seven columns explicitly, so adding a field here cannot leak into the INSERT.
    """

    field_key: str
    display_name: str
    scope: str
    value_kind: str
    normalizer_id: str | None
    destination_eligible: bool
    multiplicity: str | None
    reliability_ceiling: str | None = None
    aliases: tuple[str, ...] = ()
    role_split: tuple[str, ...] = ()
    notes: str | None = None


#: The stored columns, asserted against `PRAGMA table_info(fields)`. Deliberately
#: SHORTER than `FieldRow`: see that class's docstring.
FIELDS_COLUMNS: tuple[str, ...] = (
    "field_key", "display_name", "scope", "value_kind",
    "normalizer_id", "destination_eligible", "multiplicity",
)


def _row(field_key: str, display_name: str, scope: str, value_kind: str,
         destination_eligible: bool, *, ceiling: str | None = None,
         aliases: tuple[str, ...] = (), role_split: tuple[str, ...] = (),
         notes: str | None = None) -> FieldRow:
    """One catalogue row. `normalizer_id` and `multiplicity` are NULL on every row:
    per-field normalizers are Deferred and multiplicity is open question 6."""
    return FieldRow(field_key=field_key, display_name=display_name, scope=scope,
                    value_kind=value_kind, normalizer_id=None,
                    destination_eligible=destination_eligible, multiplicity=None,
                    reliability_ceiling=ceiling, aliases=aliases,
                    role_split=role_split, notes=notes)


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
    _row("file_type", "file type", "universal", "string", False,
         aliases=("file type", "format", "mime_type")),
    _row("creation_date", "creation date", "universal", "date", False,
         aliases=("creation date", "created", "date_created")),
    _row("language", "language", "universal", "string", False,
         aliases=("content language",)),
    _row("duplicate_family", "duplicate family", "universal", "identifier", False,
         aliases=("duplicate family", "dupe_group")),
    _row("version_family", "version family", "universal", "identifier", False,
         aliases=("version family", "version_stem")),
)

#: P6's one recorded addition to the universal list. §3.9: "It may be supported more
#: weakly by a tightly bounded download session." §4.2 requires it retrievable. It is
#: not `purpose` — the session names no purpose value — and it is never a folder
#: level, because a session is a clue and a review aid, not proof of topic.
_DOWNLOAD_SESSION: tuple[FieldRow, ...] = (
    _row("download_session", "download session", "universal", "identifier", False,
         aliases=("session", "download session")),
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
_OUR_FIRM_NOTES = (
    "`60` M12: for an employee the employer IS the holder's own organization, so "
    "`employer` and `our_firm` differ only in role and eligibility. `our_firm` is the "
    "firm-side AUTHORSHIP identity (§3.8) and is never a destination dimension; "
    "`employer` is the organization the holder works or worked for, named from the "
    "holder's own side, and IS eligible. Do not fill both from one letterhead."
)

_ROLES_3_8: tuple[FieldRow, ...] = (
    # `creator` is NOT among the aliases, though `canonical_fields.json` lists it:
    # it is one of catalogue 01's producer strings, and P6 receives that list as
    # injected data, never as a module-level literal.
    _row("authored_by", "authored_by", "universal", "string", False,
         aliases=("author", "produced_by"),
         role_split=("target_school",)),
    _row("target_school", "target_school", "universal", "string", True,
         aliases=("addressed school",), role_split=("authored_by",)),
    _row("our_firm", "our_firm", "universal", "string", False,
         aliases=("own firm", "my_company"),
         role_split=("client", "employer"), notes=_OUR_FIRM_NOTES),
    _row("client", "client", "universal", "string", True,
         aliases=("customer", "client organization"), role_split=("our_firm",)),
)

#: §3.11: "Academic files may use school, term, course, instructor, and work type."
#: D6: the stored key is `subject`; "course" is the design's prose for the same field
#: and survives inside quotations only. §3.2: "the system can create facts such as
#: subject = BUSIB 4300."
#:
#: `instructor` is not destination-eligible: §3.11's Academic template is school →
#: term → course → work type, and §3.8 disfavours person-identity collectors.
_ACADEMIC: tuple[FieldRow, ...] = (
    _row("school", "school", "academic", "string", True,
         aliases=("current school", "authoring school", "institution_attended"),
         role_split=("target_university",)),
    _row("term", "term", "academic", "string", True,
         aliases=("semester", "academic term", "quarter")),
    # The bare alias `course` is dropped, though `canonical_fields.json` carries it.
    # D6: the stored key is `subject` and "'course' is the design's prose for the same
    # field"; P6's own guard requires the word to survive inside quotations and nowhere
    # else, and an alias tuple is not a quotation. Same shape as H7's `cycle` drop.
    _row("subject", "subject", "academic", "string", True,
         aliases=("course_name", "course_code", "class"),
         notes="D6: this is the stored key. \u0022course\u0022 is `00`'s prose for it "
               "(§3.11's list, §5.4's template order) and is never a second key; "
               "§3.2 writes the fact itself as `subject = BUSIB 4300`."),
    _row("instructor", "instructor", "academic", "string", False,
         aliases=("teacher", "professor", "lecturer")),
    _row("work_type", "work type", "academic", "enum", True,
         aliases=("work type", "worktype")),
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
#:
#: `60` §3 H7 and J-2: `application_cycle` DROPS the bare alias `cycle`. Three keys now
#: end in `_cycle` -- `application_cycle`, `recruiting_cycle`, `people_cycle` -- and an
#: unqualified "cycle" token would resolve across all three. §5.3's fence principle is
#: why the drop does not also mean a merge: `application_cycle`'s role sentence cannot
#: be stated without naming admissions, so it stays fenced to this schema.
_COLLEGE_APPLICATIONS: tuple[FieldRow, ...] = (
    _row("target_university", "target university", "college_applications", "string",
         True, aliases=("target university", "target institution", "applying_to"),
         role_split=("school",)),
    _row("application_cycle", "application cycle", "college_applications", "string",
         True, aliases=("application cycle", "admissions cycle")),
    _row("application_document_type", "application document type",
         "college_applications", "enum", True,
         aliases=("application document type", "document type")),
    _row("purpose", "purpose", "college_applications", "string", True,
         aliases=("file purpose",)),
)

#: §3.11: "Research files may use project, stage, artifact type, lab, and venue."
#: `project` and `artifact_type` are DECLARED here and REFERENCED by `code`.
_RESEARCH: tuple[FieldRow, ...] = (
    _row("project", "project", "research", "string", True,
         aliases=("project name", "project_id")),
    _row("stage", "stage", "research", "string", True,
         aliases=("phase", "workflow stage")),
    _row("artifact_type", "artifact type", "research", "enum", True,
         aliases=("artifact type", "artefact_type")),
    _row("lab", "lab", "research", "string", True,
         aliases=("research group", "laboratory")),
    _row("venue", "venue", "research", "string", True,
         aliases=("journal", "conference")),
)

#: `60` §3 H6 — all THREE halves, not the one `54` proposed. `record_type` is now shared
#: by seven schemas, so the sentence that keeps it apart from `work_type` and
#: `artifact_type` has to travel with the key rather than sit in a document.
_RECORD_TYPE_NOTES = (
    "H6.1 negative discriminator: if the file IS the work product of a bounded "
    "engagement or course -> `work_type`; if it is an OUTPUT OF A MAKING PROCESS -> "
    "`artifact_type`. `record_type` is what remains: the file evidences that a "
    "transaction, operation or decision occurred. Where two readings are both "
    "supported, `00` requires abstention, not the nearest declared key. "
    "H6.2 undeclared route: a file whose routed type key is not declared by the active "
    "schema returns unknown; it is never re-routed to the nearest declared type key. "
    "H6.3 value side: values are schema-qualified. Seven schemas share this key, and P9 "
    "groups on shared validated facts, so an unqualified `record_type = \"return\"` "
    "would join a tax return to an oil-field production return."
)

#: §3.11: "Finance files may use institution, account type, tax year, and record type."
#:
#: Plus `account_holder` (`60` M13, per `49` §4.1): it was moved out of `finance.fields[]`
#: into `proposed_fields` mid-session and fell through, and `finance` is a live schema, so
#: the omission was a SHIPPING schema losing a field with no replacement. Its `role_split`
#: partner is `institution` — §3.8's own example is "a finance document may mention an
#: account holder and an issuing bank" — and it is never destination-eligible.
#:
#: `tax_year` DROPS the alias `fiscal_year` (`60` §3 H7). `record_period` records
#: `fiscal_period`; shipping both put two genuinely different objects one character
#: apart, which is what `business_operations` minted `record_period` to avoid.
_FINANCE: tuple[FieldRow, ...] = (
    _row("institution", "institution", "finance", "string", True,
         aliases=("bank", "issuer", "provider"), role_split=("account_holder",)),
    _row("account_type", "account type", "finance", "string", True,
         aliases=("account type",)),
    _row("tax_year", "tax year", "finance", "string", True, aliases=("tax year",)),
    _row("record_type", "record type", "finance", "enum", True,
         aliases=("record type",), notes=_RECORD_TYPE_NOTES),
    _row("account_holder", "account holder", "finance", "string", False,
         ceiling="possible", aliases=("account holder",), role_split=("institution",),
         notes="`60` M13 / `49` §4.1. §3.8: 'A finance document may mention an account "
               "holder and an issuing bank.' The holder is a person or entity identity, "
               "so it is a fact and never a folder level; `institution` is its "
               "`role_split` partner and is the eligible half of the pair."),
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
    _row("capture_year", "capture year", "photos", "string", True,
         aliases=("capture year", "year_taken")),
    _row("event", "event", "photos", "string", True,
         aliases=("occasion", "photo event", "trip"),
         notes="`57` §5.3's fence test makes `event` WIDENABLE: its role -- the bounded "
               "occurrence a set of records is about -- can be stated without naming "
               "photography, so `manufacturing`, `retail_hospitality` and `hr` "
               "reference it. `logistics` does NOT: `60` §7 records that `event` sat "
               "there only as the absorber of `consignment`, and with B2 reversing that "
               "merge the schema's own anchor eliminates it by name -- 'event is the "
               "Photos capture-occasion'. Time-primacy belongs to `00`:70's Photos template "
               "order, not to the key, so a non-photo schema does not inherit it. `60` "
               "§5 marks it dagger on `hr` alone; eligibility is a property of the KEY "
               "(`48`, carried by `60` §4 on `subject_of_record`), and the Photos "
               "template branches year -> event, so the key stays eligible."),
    _row("location", "location", "photos", "string", True, aliases=("place", "geo")),
    _row("people", "people", "photos", "string", False, aliases=("persons", "who")),
    _row("camera_information", "camera information", "photos", "string", False,
         aliases=("camera information", "camera", "exif_camera")),
    _row("media_type", "media type", "photos", "enum", True,
         aliases=("media type",),
         notes="FENCED (`57` §5.3, adopted by `60` §3): its role sentence -- the kind of "
               "CAPTURE -- cannot be stated without naming its domain, so it is never "
               "widened to another schema. `54` §11's double-naming diagnosis is wrong "
               "on the facts: `media_type` is in `00`:48's Photos field sentence only."),
    _row("capture_date", "capture date", "photos", "date", False),
)

#: §3.11: "Code files may use project, repository, programming language, and artifact
#: type." `project` and `artifact_type` are declared under Research.
#:
#: `programming_language` is not destination-eligible: the design treats code projects
#: as structural units whose existing layout is preserved, and scattering a project by
#: language would break that.
_CODE: tuple[FieldRow, ...] = (
    _row("repository", "repository", "code", "string", True,
         aliases=("repo", "repository name")),
    _row("programming_language", "programming language", "code", "string", False,
         aliases=("programming language", "language_code")),
)

# ---------------------------------------------------------------------------
# `60` §4 — the eighteen minted keys, grouped by the scope that DECLARES each
# ---------------------------------------------------------------------------
#
# J-1 widens `SCHEMA_IDS` 10 -> 23. Fifteen of the thirteen new professional schemas
# plus `career` and `finance` declare at least one key here; five more
# (`creative`, `retail_hospitality`, `government`, `nonprofit`, `clinical_practice`)
# declare a field SET in `DOMAIN_FIELDS` and mint nothing, which is `60` §5 working as
# intended: a schema earns a key only when the corpus signed for one.

#: J-3: career declares BOTH `work_type` and `record_type` (referenced, not declared
#: here). Career's corpus is about half work-product and half record; with only
#: `record_type` a cover letter routes to `work_type`, finds it undeclared, and the
#: extractor must force it or abstain with nothing to say which.
#:
#: `job_title` arrived in `60` §4 by §8.1's correction: §5 had marked it dagger with no
#: source, and `00`:70 puts it in a template order in so many words -- "a Career template
#: may define company -> ROLE or recruiting cycle -> document type". A key `00` puts in a
#: template order cannot be non-destination. Career sits at six destination candidates,
#: exactly at `00`:48's ceiling under J-4.
_CAREER: tuple[FieldRow, ...] = (
    _row("employer", "employer", "career", "string", True, ceiling="possible",
         role_split=("our_firm", "target_employer"), notes=_OUR_FIRM_NOTES),
    _row("target_employer", "target employer", "career", "string", True,
         ceiling="possible", aliases=("target employer",), role_split=("employer",),
         notes="`00`:44's own rule, mirroring the live `school` <-> `target_university` "
               "split: 'An application essay can mention the author's current school and "
               "the university to which the essay is addressed. Those are not the same "
               "field.' The employer the holder HAS is `employer`; the employer the "
               "holder is ADDRESSING is this key."),
    _row("recruiting_cycle", "recruiting cycle", "career", "string", True,
         ceiling="possible", aliases=("recruiting cycle",),
         role_split=("people_cycle",),
         notes="`60` J-2, career side: the holder is a PARTICIPANT in the cycle. Its "
               "`role_split` partner `people_cycle` is the hr side, where the holder "
               "runs the cycle. `00`:70 writes 'recruiting cycle' by name and writes "
               "`people_cycle` nowhere, so under D6's precedent the `00` word does not "
               "lose. Never `application_cycle`, which is fenced to admissions."),
    _row("job_title", "job title", "career", "string", True, ceiling="possible",
         aliases=("job title", "role"),
         notes="`60` §8.1. `00`:70's Career template is 'company -> role or recruiting "
               "cycle -> document type', so `role` is the middle level of `00`'s own "
               "order and the key cannot be non-destination; "
               "`career.employment-records` proposed it eligible too. The stored key is "
               "`job_title` and `role` is `00`'s prose for it, kept as an alias. It is "
               "the POSITION held, never the person (`subject_of_record`) and never the "
               "organization (`employer`, `target_employer`)."),
)

#: `60` H5 reverses `54`'s `issuing_body` hold: it was held because
#: "business_operations is at its 6-field ceiling", which is false under J-4's loose
#: reading of `00`:48. One reversal serves two stranded rows --
#: `business_operations.compliance-audit` (the only fact separating its own audits from
#: its suppliers' evidence packs) and `career.credentials-licenses` (whose recorded
#: proposal is issuing authority -> credential -> document type).
_BUSINESS_OPERATIONS: tuple[FieldRow, ...] = (
    _row("organization", "organization", "business_operations", "string", False,
         ceiling="possible",
         notes="`48` §3, seeded destination-INELIGIBLE and template-time promotable. "
               "`00`:44's 'produced by' is authorship and its 'merely' is a "
               "template-time test, so a folder of everything one company produced is "
               "the collection point §3.8 forbids -- while `00`:70 still puts a company "
               "first in a folder template. Seeded false is the only reading that "
               "satisfies both. `workforce_unit` is seeded the same way for the same "
               "reason."),
    _row("record_period", "record period", "business_operations", "string", True,
         ceiling="validated", aliases=("record period", "fiscal_period"),
         notes="`47`: the bounded interval a record COVERS. Not `tax_year` (a statutory "
               "filing year: an entity's fiscal year routinely does not coincide with "
               "it, and reusing the key would quietly assert that it does), not "
               "`capture_year`, and NOT `people_cycle`, which answers which instance of "
               "a recurring process. `47` §2.2 kept those apart deliberately: merging "
               "would put an onboarding checklist and an oil-field production return on "
               "one folder level. `tax_year` drops `fiscal_year` so that this key's "
               "`fiscal_period` alias is not one character from another column (H7)."),
    _row("supplier", "supplier", "business_operations", "string", True,
         ceiling="possible", aliases=("carrier", "vendor"),
         notes="`60` B3. LABELLED SLOT ONLY -- Carrier / Haulier / Forwarder / Shipping "
               "Line / Airline, or the equivalent supplier label on the document. A "
               "consignment note routinely names consignor, consignee and carrier in "
               "three different roles on one page, so without the label the extractor "
               "picks one of three organization tokens at random. `carrier` folds here "
               "and is an ALIAS, never a second key. `60` §5 marks it dagger on "
               "`logistics`; eligibility is a property of the KEY, and "
               "`business_operations` needs it eligible to reach §5's dest count of 6."),
    _row("issuing_body", "issuing body", "business_operations", "string", True,
         ceiling="possible", aliases=("issuing body", "issuing authority"),
         notes="`60` H5. The authority that ISSUED the instrument -- a regulator, "
               "examining board, licensing authority or certifying body. Never the "
               "holder (`our_firm`), never the counterparty (`client`, `supplier`), and "
               "never the bank on a statement (`institution`)."),
)

_CONSTRUCTION_PROPERTY: tuple[FieldRow, ...] = (
    _row("property", "property", "construction_property", "string", True,
         ceiling="possible",
         notes="`57` §2: earned by `construction_property` and `finance.household-"
               "property`. A PLACE, not an author, so `00`:44's authorship bar does not "
               "reach it. `60` B1 strips it from `government`, which never proposed it "
               "and two of whose nine candidate rows object to it as a folder level."),
)

_ENGINEERING: tuple[FieldRow, ...] = (
    _row("design_item", "design item", "engineering", "string", True,
         ceiling="possible", aliases=("design item",),
         notes="`60` M10: `design_item` is the controlled design configuration whose "
               "definition a file governs -- never a saleable or sold article, which is "
               "`product`. `engineering`'s own elimination checked `project`, `subject`, "
               "`property` and `repository` and never checked `product`, because "
               "`product` was minted in a different adjudication; a chiller model is a "
               "product model. `49` §4.2(b) already drew the type-vs-instance line "
               "against `asset`."),
)

_MANUFACTURING: tuple[FieldRow, ...] = (
    _row("site", "site", "manufacturing", "string", True, ceiling="possible",
         notes="`48` §1b: the operating place -- plant, works, depot, store, field. Ten "
               "proposing rows across four schemas all eliminated `location` "
               "identically, so this is not a respelling of the Photos key."),
    _row("asset", "asset", "manufacturing", "string", True, ceiling="possible",
         notes="`48`. An enduring identified physical thing carrying a reference. "
               "`manufacturing.asset-register`'s own restriction travels with the key: a "
               "MULTI-asset register export has no single value and sits at `site`."),
    _row("product", "product", "manufacturing", "string", True, ceiling="possible",
         aliases=("sku", "menu_item", "commodity"),
         notes="`49` §1.5: an article or formulation made through transformation, "
               "widened to a neutral output key. `60` M10: `design_item` is the "
               "controlled design configuration whose definition a file governs -- never "
               "a saleable or sold article, which is `product`."),
)

_RESOURCE_OPERATIONS: tuple[FieldRow, ...] = (
    _row("authorization", "authorization", "resource_operations", "string", True,
         ceiling="possible", aliases=("authorisation", "permit"),
         notes="`60` H8 spells it with a z. `00` uses 'organization' 27 times and "
               "'organisation' zero times; shipping `organization` beside "
               "`authorisation` would put two orthographies in one snake_case namespace, "
               "which is the defect D6 exists to kill arriving as house style. The s "
               "spelling is an ALIAS so it resolves rather than becoming a second column. "
               "The value is the instrument, never a regulator's name "
               "(`manufacturing.environmental-compliance`); the regulator is "
               "`issuing_body`."),
)

_LOGISTICS: tuple[FieldRow, ...] = (
    _row("consignment", "consignment", "logistics", "identifier", True,
         ceiling="validated",
         notes="`60` B2 reverses `49`'s fold into `event`. One described quantity of "
               "goods travelling under one carrier's undertaking -- a THING, the same "
               "ontological category as `asset`, not an occurrence. "
               "`logistics.last-mile-pod` records the order 'consignment/parcel -> "
               "delivery event'; folded, that reads `event > event`, which `00`:97's "
               "validator forbids by name. Ceiling `validated` because the rule family "
               "is a labelled slot: Consignment / Waybill / AWB / B/L / Container / "
               "Booking / Tracking. It identifies goods, never a person."),
)

#: `60` J-5: `hr` ships as a PROTECTION schema, not a filing schema. NJ-HR-1 was tested
#: against the wrong half of its own condition -- the second conjunct ("the
#: protection-first default is schema-level behavior") is the real distinction, and it
#: is independently true: every `hr` row's subject is a person or a workforce
#: population, and no `business_operations` row's is. J-5a records that the 3-6 band's
#: FLOOR does not apply here: a schema whose job is to keep a grievance file out of a
#: named folder has fewer destination-eligible keys by design.
#:
#: `work_type` is deliberately NOT declared on `hr` (`57` §3): zero hr signature, it was
#: borrowed from `law_practice`, and half of `hr`'s folder proposal was unearned.
_HR: tuple[FieldRow, ...] = (
    _row("people_cycle", "people cycle", "hr", "string", True, ceiling="possible",
         aliases=("people cycle",), role_split=("recruiting_cycle",),
         notes="`60` J-2, hr side: the holder RUNS the cycle -- an intake, onboarding "
               "or review round the organization operates. Its `role_split` partner "
               "`recruiting_cycle` is the career side, where the holder is a "
               "participant in it. `47` §2.2 keeps this key out of the period cluster: a "
               "'2026 graduate intake' answers which instance of a recurring process, "
               "not what interval the content covers."),
    _row("workforce_unit", "workforce unit", "hr", "string", False, ceiling="possible",
         aliases=("workforce unit",),
         notes="`60` J-5 / `57` §5.2: seeded destination-INELIGIBLE and template-time "
               "promotable, identically to `organization`. `48` grants promotion to one "
               "and not the other with no stated reason. The proposing row asks for "
               "eligibility 'only after a real multi-unit corpus is established', which "
               "is exactly what template-time promotion means."),
)

#: `49` §1.7, carried by `60` §4: `destination_eligible: false` ON THE KEY, never
#: per-template. Nine refused synonyms across three families folded here and none was
#: minted; `law_practice` declares it, and `nonprofit`, `hr` and `clinical_practice`
#: reference it.
_LAW_PRACTICE: tuple[FieldRow, ...] = (
    _row("subject_of_record", "subject of record", "law_practice", "string", False,
         ceiling="possible", aliases=("subject of record",),
         notes="The person or entity a record is ABOUT, as distinct from its author "
               "(`authored_by`), its holder (`our_firm`) and its counterparty "
               "(`client`). Never destination-eligible, on the key rather than per "
               "template: a folder bearing the subject's name discloses membership of a "
               "matter, personnel, grant or clinical file. `60` B1 makes it the ONE key "
               "`clinical_practice` carries -- its anchor signed exactly this and "
               "nothing else."),
)

#: The catalogue, in declaration order. Fifty-six rows: `60` §4's "37 live + 19 = 56".
#: The live thirty-seven keep their positions, so a row's ordinal is stable and
#: `fields_in_scope`'s `ORDER BY rowid` still returns the SPEC's order for them.
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
    *_CAREER,
    *_BUSINESS_OPERATIONS,
    *_CONSTRUCTION_PROPERTY,
    *_ENGINEERING,
    *_MANUFACTURING,
    *_RESOURCE_OPERATIONS,
    *_LOGISTICS,
    *_HR,
    *_LAW_PRACTICE,
)

#: §3.11's universal list (five of six, C5) plus §3.9's download session.
UNIVERSAL_FIELDS: tuple[str, ...] = tuple(
    row.field_key for row in (*_UNIVERSAL_3_11, *_DOWNLOAD_SESSION)
)

#: §3.8's four role fields.
ROLE_FIELDS: tuple[str, ...] = tuple(row.field_key for row in _ROLES_3_8)

#: Which keys each schema REFERENCES — §3.11's six sentences, literal, and `60` §5's
#: table for the rest. Not the same question as which scope DECLARES a key: `project`
#: and `artifact_type` are declared at `research` and referenced by seven more schemas,
#: and five schemas here declare nothing at all.
#:
#: The three §3.15 safety domains are ABSENT rather than empty, so
#: `FIELD_LESS_SCHEMA_IDS` stays derived and `schema_fields` keeps returning `()` for
#: them without a special case.
#:
#: One departure from `60` §5, recorded rather than silently taken:
#:
#: * `code` keeps `00`'s four. `60` §5's `code` row ("repository · programming_language",
#:   dest 1) counts the keys DECLARED at scope `code`; `00` §3.11 names four for Code and
#:   `60` drops nothing — contrast B1, which drops by name. `00` is the higher authority.
#: * `career` gains `job_title` under `60` §8.1, which reverses §5's unsourced dagger:
#:   `00`:70 makes `role` a level of its own Career template.
DOMAIN_FIELDS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    # §3.11's six sentences. `research` gains `institution` (`60` H9, per `48` §2:
    # nonprofit's row warned that without a funder role its strongest node has no key
    # "and a template author will mint one"); `finance` gains `account_holder` (M13).
    "academic": tuple(row.field_key for row in _ACADEMIC),
    "college_applications": tuple(row.field_key for row in _COLLEGE_APPLICATIONS),
    "research": (*(row.field_key for row in _RESEARCH), "institution"),
    "finance": tuple(row.field_key for row in _FINANCE),
    "photos": tuple(row.field_key for row in _PHOTOS),
    "code": ("project", "repository", "programming_language", "artifact_type"),
    # `60` §5, the remaining fourteen. J-3 gives career BOTH type keys.
    "career": ("employer", "target_employer", "recruiting_cycle", "work_type",
               "record_type", "job_title"),
    "business_operations": ("organization", "record_period", "project", "client",
                            "supplier", "record_type", "issuing_body"),
    "law_practice": ("project", "work_type", "client", "record_period", "our_firm",
                     "subject_of_record"),
    "creative": ("project", "artifact_type", "stage", "client", "venue"),
    "construction_property": ("property", "project", "work_type", "client", "our_firm"),
    "engineering": ("design_item", "artifact_type", "asset", "project", "stage"),
    "manufacturing": ("site", "product", "asset", "event", "record_period",
                      "record_type"),
    "retail_hospitality": ("site", "event", "record_type", "record_period", "product"),
    "resource_operations": ("site", "asset", "authorization", "product",
                            "record_period", "record_type"),
    # `60` §7 CORRECTED: `logistics` drops `event`. It had no signature once B2 reversed
    # the `consignment` -> `event` fold, and the anchor eliminated it by name.
    "logistics": ("consignment", "record_type", "site", "asset", "supplier"),
    # B1: stripped to what each schema's own anchor actually signed. `government` asked
    # in its own words to stay field-less and to adjudicate "centrally rather than in
    # children"; one signature (`programme` -> `project`) is what it gets.
    "government": ("project",),
    "nonprofit": ("organization", "record_period", "subject_of_record", "institution"),
    "hr": ("people_cycle", "workforce_unit", "subject_of_record", "event"),
    "clinical_practice": ("subject_of_record",),
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
