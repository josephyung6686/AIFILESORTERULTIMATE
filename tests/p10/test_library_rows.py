"""The 54 shipped applicability rows, loaded through the real loader.

`planning/51-LAUNCH-TEMPLATE-DRAFT.md` §5 ratifies 54 `TemplateApplicability`
records — 11 academic, 3 code, 5 college_applications, 18 finance, 9 photos,
8 research. Until this file existed the product shipped **two** `RoleBinding`s,
both fixtures, so `RoleBinding.label` — the string a person reads above their own
folders — had no authored value anywhere.

**What these tests are for.** Not that the JSON parses; that a JSON file exists
proves nothing. They exist to pin the two things the data can silently lose:

1. **A label that is its own key is the failure state, not a placeholder.**
   `59` §5c measured it on the neighbouring surface: of `facts/fields.py`'s 37
   `display_name` slots, 19 are byte-identical to the key and the other 18 are
   the key with the underscore replaced by a space — *"Zero of 37 differ from the
   key by anything else."* `test_no_shipped_label_is_the_key_it_replaces` makes
   that state unreachable here, and checks it case- and underscore-insensitively
   because `"Project"` for `project` is the same failure wearing a capital.
2. **The label lives on the ROW because one role reads differently per schema.**
   `RoleBinding`'s own docstring says so and `00` §5.1 asks labels to *"reflect
   the user's vocabulary rather than a universal corporate taxonomy"* — a
   statement about the AUDIENCE, and the audience is what the row selects.
   `test_one_definition_reaching_three_schemas_names_each_level_differently`
   fails if the labels were hoisted onto the definition instead.

The rows are loaded by `tree_design.catalogue.load_catalogue` — the real loader,
through the real `TemplateApplicability.__post_init__` — and never by hand, so a
record the live product would reject cannot pass here.
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter, defaultdict

import pytest

import tree_design
from facts.fields import DOMAIN_FIELDS, FIELD_ROWS
from tree_design.catalogue import load_catalogue
from tree_design.templates import MalformedTemplateRecord

#: The packaged library, addressed through the package rather than through the
#: working directory: this is shipped data, and a test that only finds it from
#: the repository root would pass on a tree where the file was never installed.
LIBRARY = pathlib.Path(tree_design.__file__).parent / "library"
ROWS_PATH = LIBRARY / "applicabilities.json"

#: `51` §9.7, and the arithmetic §1.1 derives: 358 node files, 23 of them
#: schemas, 278 gated on a schema declaring no live fields, 3 carrying
#: `refuse_node: true` — 54 bindable rows, 54 applicability records.
EXPECTED_PER_SCHEMA = {
    "academic": 11, "code": 3, "college_applications": 5,
    "finance": 18, "photos": 9, "research": 8,
}

REPO = pathlib.Path(__file__).resolve().parents[2]


def _manifest(rows) -> str:
    """One release carrying the shipped rows.

    `fragments` and `definitions` are empty because THIS file owns neither: the
    rows are the unit under test and `load_catalogue` keys the three collections
    independently. A cross-file reference check lives in
    `test_every_definition_this_file_names_is_published`, which skips rather than
    passes when the sibling file is not there — the one thing it must not do is
    look like it checked something it could not.
    """
    return json.dumps({
        "release_id": "rel-launch-54",
        "fragments": [],
        "definitions": [],
        "applicabilities": rows,
    })


@pytest.fixture(scope="module")
def raw() -> list[dict]:
    return json.loads(ROWS_PATH.read_text())["applicabilities"]


@pytest.fixture(scope="module")
def catalogue(raw):
    return load_catalogue(lambda: _manifest(raw))


@pytest.fixture(scope="module")
def rows(catalogue):
    return tuple(catalogue.applicabilities.values())


# --------------------------------------------------------------------------
# The rows load, through the real loader, and they are the ratified 54.
# --------------------------------------------------------------------------

def test_the_shipped_rows_load_through_the_real_loader(rows):
    """54 records resolve. Not "the JSON is well-formed" — every one has passed
    `TemplateApplicability.__post_init__`, which is what rejects a row whose
    bindings fall outside its own allow-list and a row with no provenance."""
    assert len(rows) == 54


def test_every_schema_carries_the_row_count_the_draft_ratified(rows):
    assert Counter(row.uses_schema for row in rows) == EXPECTED_PER_SCHEMA


def test_a_row_is_identified_once(raw):
    keys = [(r["applicability_id"], r["applicability_version"]) for r in raw]
    assert len(set(keys)) == len(keys) == 54


def test_the_top_level_shape_is_the_one_the_loader_reads(raw):
    """`load_catalogue` reads `manifest["applicabilities"]`, so the file's own
    top-level key is the seam. A file that nests the rows anywhere else loads as
    an empty release, and an empty release makes C1 pass by having nothing to
    resolve."""
    doc = json.loads(ROWS_PATH.read_text())
    assert list(doc) == ["applicabilities"]
    assert doc["applicabilities"] is not None and len(raw) == 54


# --------------------------------------------------------------------------
# The labels. This is the deliverable.
# --------------------------------------------------------------------------

def _normalise(value: str) -> str:
    """Fold the two ways a key gets shipped as a label: the key itself, and the
    key with its underscores opened out. `59` §5c measured that those two
    account for 37 of 37 `display_name` values in `facts/fields.py`."""
    return value.strip().casefold().replace("_", " ")


def test_no_shipped_label_is_the_key_it_replaces(rows):
    """The measured failure state, made unreachable.

    Byte-identity is checked because that is 19 of the 37; the normalised form
    is checked because the other 18 are the key with a space for the underscore,
    and because `"Project"` for `project` would otherwise slip through as new
    work while changing nothing a person reads.
    """
    identical = [(row.applicability_id, b.field_ref, b.label)
                 for row in rows for b in row.role_bindings
                 if b.label == b.field_ref]
    assert identical == []
    despaced = [(row.applicability_id, b.field_ref, b.label)
                for row in rows for b in row.role_bindings
                if _normalise(b.label) == _normalise(b.field_ref)]
    assert despaced == []


def test_no_shipped_label_is_the_role_name_either(rows):
    """`53` §4b failed eleven of the fifteen roles on the name-out-loud test —
    *"Nobody says 'occasion anchor.'"* A role is a cross-schema abstraction and
    must never be shown, so leaking it into the label is the same defect as
    leaking the field key."""
    leaked = [(row.applicability_id, b.role_ref, b.label)
              for row in rows for b in row.role_bindings
              if _normalise(b.label) == _normalise(b.role_ref)]
    assert leaked == []


def test_every_binding_carries_a_label(rows):
    """`RoleBinding.label` is required rather than optional, deliberately: *"An
    optional label is a label nobody authors."* The record enforces it; this
    asserts the shipped data actually exercised that requirement, which a file
    of zero rows would also satisfy."""
    bindings = [b for row in rows for b in row.role_bindings]
    assert len(bindings) == 123
    assert all(b.label.strip() for b in bindings)


def test_a_label_holding_a_path_separator_is_rejected_by_the_loader(raw):
    """P12 alone composes paths (resolution B3). Asserted through
    `load_catalogue` on a mutated copy of a REAL row rather than on a fixture,
    so it is this file's data that would be refused."""
    for separator in ("/", "\\"):
        mutated = json.loads(json.dumps(raw))
        mutated[0]["role_bindings"][0]["label"] = f"Homework{separator}Exams"
        with pytest.raises(MalformedTemplateRecord, match="path separator"):
            load_catalogue(lambda: _manifest(mutated))


def test_a_binding_outside_the_rows_own_allow_list_is_rejected(raw):
    """The guard that keeps reuse from turning a per-schema fact allow-list into
    a cross-domain union, exercised on shipped data."""
    mutated = json.loads(json.dumps(raw))
    mutated[0]["role_bindings"][0]["field_ref"] = "instructor"
    with pytest.raises(MalformedTemplateRecord, match="does not"):
        load_catalogue(lambda: _manifest(mutated))


# --------------------------------------------------------------------------
# Why the label lives on the row: one definition, three schemas, three names.
# --------------------------------------------------------------------------

def test_rows_for_schema_returns_that_schemas_rows_and_no_others(catalogue):
    """Finance carries eighteen — the largest set in the launch library, and the
    one where a leak from another schema would be least visible."""
    finance = catalogue.rows_for_schema("finance")
    assert len(finance) == 18
    assert {row.uses_schema for row in finance} == {"finance"}
    assert "ap.travel.bookings-confirmations" in {
        row.applicability_id for row in finance}
    # `travel.trip-photos` is the sibling row named for the same domain and
    # bound to a different schema (`51` Judgment Call 6). It must not appear.
    assert "ap.travel.trip-photos" not in {row.applicability_id for row in finance}
    assert len(catalogue.rows_for_schema("photos")) == 9
    assert catalogue.rows_for_schema("law_practice") == ()


def test_one_definition_reaching_three_schemas_names_each_level_differently(rows):
    """`51` §6.1's reuse point, and the whole argument for where the label lives.

    `def.subject-work-record@1` is referenced by rows in academic, research and
    code. `subject_anchor` resolves to `subject` for a student, `project` for a
    researcher and `project` for a coder — and the three audiences do not say the
    same word about it. A label on the DEFINITION would be one name for all
    three; these assertions are what would fail if it were moved there.
    """
    by_schema = {}
    for row in rows:
        if row.template_id == "def.subject-work-record":
            by_schema.setdefault(row.uses_schema, []).append(row)
    assert set(by_schema) == {"academic", "research", "code"}
    assert len(by_schema["academic"]) == 5   # 51 §6.1: 5 rows
    assert len(by_schema["research"]) == 1
    assert len(by_schema["code"]) == 1

    def label(row, role):
        return next(b.label for b in row.role_bindings if b.role_ref == role)

    anchors = {schema: label(rows_[0], "subject_anchor")
               for schema, rows_ in by_schema.items()}
    assert len(set(anchors.values())) == 3, anchors
    kinds = {schema: label(rows_[0], "artifact_kind")
             for schema, rows_ in by_schema.items()}
    assert len(set(kinds.values())) == 3, kinds


def test_one_role_and_one_field_still_read_differently_row_by_row(rows):
    """Reuse is not only across schemas. Eleven finance rows share
    `def.issuer-record@1` and bind the same `issuing_org -> institution`; the
    bank that issued a statement, the carrier that issued a policy and the seller
    that issued a receipt are not the same word to the person who reads them."""
    issuers = {row.applicability_id: b.label
               for row in rows for b in row.role_bindings
               if row.uses_schema == "finance" and b.field_ref == "institution"}
    assert len(issuers) == 13
    assert len(set(issuers.values())) >= 10, issuers
    assert issuers["ap.finance.receipts-expenses"] != \
        issuers["ap.finance.personal-records"]


def test_the_labels_are_not_one_name_per_field(rows):
    """The regression this whole file guards against is a library that authors
    one label per field key and calls the job done — which is `facts/fields.py`'s
    `display_name` with better words, and still one name for every audience."""
    per_field = defaultdict(set)
    for row in rows:
        for b in row.role_bindings:
            per_field[b.field_ref].add(b.label)
    assert sum(len(v) for v in per_field.values()) > 4 * len(per_field)
    # The keys `53` §4a and §4b singled out as failures each carry several names.
    assert len(per_field["artifact_type"]) >= 5   # 53: "FAIL" — nobody says it
    assert len(per_field["media_type"]) >= 3      # 53: "FAIL as a picker label"
    assert len(per_field["record_type"]) >= 8     # 53: "BORDERLINE-PASS"


# --------------------------------------------------------------------------
# The rest of the row: schema, fields, provenance.
# --------------------------------------------------------------------------

def test_a_row_names_exactly_one_schema(rows):
    """*"Exactly one `uses_schema`"* is the whole many-to-many seam: a definition
    may be referenced by rows for several schemas and stays safe because each row
    resolves against one."""
    assert all(isinstance(row.uses_schema, str) and row.uses_schema
               for row in rows)
    assert {row.uses_schema for row in rows} == set(EXPECTED_PER_SCHEMA)


def test_every_bound_field_is_one_its_schema_actually_declares(rows):
    """`60` §5 is the field contract and `facts.fields` is where it lives, so the
    rows are checked against the LIVE catalogue rather than against `51` §1.2 —
    which is stale on two schemas (it gives `college_applications` a `school` the
    catalogue does not declare, and `research` an `authored_by` for `60`'s
    `institution`). Neither difference reaches a binding, and this test is what
    says so rather than assuming it."""
    destination_eligible = {row.field_key for row in FIELD_ROWS
                            if row.destination_eligible}
    for row in rows:
        referenced = DOMAIN_FIELDS[row.uses_schema]
        for field in row.allowed_fields:
            assert field in referenced, (row.applicability_id, field)
            assert field in destination_eligible, (row.applicability_id, field)


def test_the_six_fields_that_are_never_a_level_reach_no_row(rows):
    """`00` §3.8: *"It should avoid using authorship or creator identity as a
    destination dimension."* `51` §1.2 applies it to five keys and adds one role
    separation — `college_applications` must never level on the applicant's own
    school, because the addressee is `target_university`."""
    everything = {f for row in rows for f in row.allowed_fields} | \
        {b.field_ref for row in rows for b in row.role_bindings}
    for forbidden in ("instructor", "authored_by", "people",
                      "camera_information", "programming_language", "school"):
        if forbidden == "school":
            assert not any(
                "school" in row.allowed_fields for row in rows
                if row.uses_schema == "college_applications")
            continue
        assert forbidden not in everything


def test_a_row_allows_exactly_what_it_binds(rows):
    """`allowed_fields` is not a per-schema constant copied onto every row.
    `allowed_vocabulary_for` unions it across the rows of one schema and hands
    the result to P8 as `Dossier.allowed_vocabulary`, which is also the
    placement-destination and target-node closure — so a field allowed here and
    bound nowhere widens five call sites for every row of the schema."""
    for row in rows:
        assert set(row.allowed_fields) == {b.field_ref for b in row.role_bindings}
        assert len(row.allowed_fields) == len(set(row.allowed_fields))


def test_the_per_schema_closure_is_the_twenty_two_destination_keys(catalogue):
    """`51` §1.2: 24 slots, 22 distinct keys, *"Every one of the 22
    destination-eligible keys is used by at least one of the 54 rows. None is
    unused, and no row uses anything else."* `project` and `artifact_type` each
    serve two schemas, which is the 24-to-22 difference."""
    from tree_design.template_schema import allowed_vocabulary_for
    closure = {schema: allowed_vocabulary_for(catalogue, uses_schema=schema)
               for schema in EXPECTED_PER_SCHEMA}
    assert closure == {
        "academic": ("school", "subject", "term", "work_type"),
        "code": ("artifact_type", "project", "repository"),
        "college_applications": ("application_cycle", "application_document_type",
                                 "purpose", "target_university"),
        "finance": ("account_type", "institution", "record_type", "tax_year"),
        "photos": ("capture_year", "event", "location", "media_type"),
        "research": ("artifact_type", "lab", "project", "stage", "venue"),
    }
    assert sum(len(v) for v in closure.values()) == 24
    assert len({key for v in closure.values() for key in v}) == 22


def test_a_role_binds_one_field_per_schema(rows):
    """`51` §2's role table, re-derived from the shipped rows. The three roles
    that must never collapse into one "organization" role — `holder_institution`
    (the school you attend), `addressed_org` (the university you apply to) and
    `issuing_org` (the bank that issued the statement) — are separate here
    because `00` says *"The system must separate roles that happen to contain the
    same entity type."*"""
    seen = defaultdict(set)
    for row in rows:
        for b in row.role_bindings:
            seen[(b.role_ref, row.uses_schema)].add(b.field_ref)
    assert all(len(fields) == 1 for fields in seen.values()), seen
    assert {role for role, _ in seen} == {
        "artifact_kind", "subject_anchor", "holder_institution", "cycle_period",
        "addressed_org", "issuing_org", "account_kind", "scope_period",
        "capture_time", "occasion_anchor", "capture_kind", "place",
        "lifecycle_stage", "repository_instance", "purpose_anchor",
    }
    assert seen[("holder_institution", "academic")] == {"school"}
    assert seen[("addressed_org", "college_applications")] == {"target_university"}
    assert seen[("issuing_org", "finance")] == {"institution"}


def test_every_row_traces_back_to_the_domain_row_that_justified_it(rows):
    """*"A compiled row nobody can trace back to the domain research that
    justified it cannot be reviewed or retired."* The record only requires
    provenance to be non-empty; this requires it to RESOLVE — the cited node file
    and research memo must exist on disk, which is what makes it a trace rather
    than a placeholder string."""
    for row in rows:
        cites = {c.split(":", 1)[0]: c.split(":", 1)[1]
                 for c in row.provenance if ":" in c}
        node_id = cites["row"]
        assert (REPO / "planning/domains/nodes" / f"{node_id}.json").is_file()
        assert (REPO / cites["memo"]).is_file()
        assert any("51-LAUNCH-TEMPLATE-DRAFT.md" in c for c in row.provenance)
    assert len({row.provenance[0] for row in rows}) == 54


def test_detection_signals_are_references_and_never_patterns(rows):
    """`51` §5: they point at the node's own `recognition` block, and §9.5: *"R2
    owns the regexes and gazetteers. No pattern is written here."*"""
    for row in rows:
        assert len(row.detection_signal_refs) == 1
        ref = row.detection_signal_refs[0]
        assert ref.startswith("recognition:")
        node_id = ref.removeprefix("recognition:")
        node = json.loads(
            (REPO / "planning/domains/nodes" / f"{node_id}.json").read_text())
        assert node["recognition"]["deterministic"]
        assert node["refuse_node"] is False


def test_the_one_purpose_scoped_row_carries_an_authored_profile(rows):
    """`51` §5.3: `applications.purpose-packet` is the only row in the launch set
    with a `purpose_profile_ref`. The namespace is what keeps it distinct from a
    P6 `purpose` field VALUE and from a runtime P9 group id — a recipe pinned to
    either would be pinned to one user's run."""
    profiled = [row for row in rows if row.purpose_profile_ref is not None]
    assert len(profiled) == 1
    assert profiled[0].applicability_id == "ap.applications.purpose-packet"
    assert profiled[0].purpose_profile_ref.purpose_profile_id == \
        "pp.application-submission"
    assert profiled[0].purpose_profile_ref.purpose_profile_version == 1


def test_the_iep_row_records_the_level_it_refuses_to_open(rows):
    """`51` §5.1. The plan is about a named child's accommodations; splitting it
    by `work_type` would open a folder level over material the row exists to keep
    together, so the refusal is stated on the row rather than left to be inferred
    from an absence."""
    row = next(r for r in rows if r.applicability_id == "ap.academic.iep-plans")
    assert row.exclusions == ("work_type as a folder level",)
    assert "work_type" not in row.allowed_fields


def test_no_row_lowers_a_floor_it_does_not_state(rows):
    """`privacy_floor` is `None` on every shipped row, and that is authored
    rather than skipped. `51` §9.4: the floor vocabulary is P7's, *"injected per
    deployment"*, and this wave writes only a placeholder symbol on fragments;
    the only ranking in the repository is fixture-local. A row naming a symbol
    the injected `privacy_rank` does not know would fail at C7 for a row that
    ships today. `None` is the record's own marker for "this row adds no floor of
    its own", so the composition floor stays the strongest of the fragments' and
    the definition's — which a row may raise later and may never lower."""
    assert {row.privacy_floor for row in rows} == {None}


def test_every_definition_this_file_names_is_published(rows):
    """The cross-file reference check. It SKIPS when the sibling library file is
    absent rather than passing, because a green test that checked nothing is the
    failure this suite is about."""
    definitions_path = LIBRARY / "definitions.json"
    if not definitions_path.is_file():
        pytest.skip("definitions.json is authored by a sibling; nothing to check")
    published = {(d["template_id"], d["template_version"])
                 for d in json.loads(definitions_path.read_text())["definitions"]}
    missing = sorted({(row.template_id, row.template_version) for row in rows}
                     - published)
    assert missing == []


def test_the_rows_reference_the_twenty_nine_ratified_definitions(rows):
    """`51` §4 cuts 29 definitions and §5 points all 54 rows at them. Counted
    here so that a definition quietly dropped, or a row re-pointed at a
    collapsed one, is visible as a number rather than as a reference error much
    later in the composition path."""
    referenced = {(row.template_id, row.template_version) for row in rows}
    assert len(referenced) == 29
    assert all(version == 1 for _, version in referenced)
    assert all(template_id.startswith("def.") for template_id, _ in referenced)
    counts = Counter(row.template_id for row in rows)
    assert counts["def.subject-work-record"] == 7      # 51 §6.1: 5 + 1 + 1
    assert counts["def.issuer-record"] == 11           # 51 §6.2: the finance spine
    assert counts["def.addressee-packet"] == 3
    assert counts["def.capture-time-events.third-party"] == 4
