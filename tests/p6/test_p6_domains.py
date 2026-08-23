# tests/p6/test_p6_domains.py
"""§3.11 domain activation -- Done-means 14, and §3.11's own worked case."""
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from facts.domains import (
    FIELD_LESS_SCHEMA_IDS, SCHEMA_IDS, UNIVERSAL_SCOPE, ActivationSignal,
    ActivationSignals, UnknownSchema, active_domains, active_field_allowlist,
    schema_fields,
)
from facts.fields import DOMAIN_FIELDS, FIELD_SCOPES, fields_in_scope, get_field
from facts.file_facts import facts_for_file, write_fact, RULE
from facts.states import VALIDATED
from facts.values import VALUE_ORIGINS, ensure_value

EVIDENCE_REF = "sha256:" + "a" * 64
CACHE_KEY = "sha256:" + "b" * 64


def _record(conn, tmp_path, *, name, body=b"one file, several facts"):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Applications", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _fact(conn, *, file_id, content_hash, field_key, value):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=EVIDENCE_REF,
                            origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=VALIDATED, origin=RULE,
                      evidence_refs=(EVIDENCE_REF,), cache_key=CACHE_KEY,
                      active=True)


def _when_field_present(schema_id, field_key):
    """An injected signal: this schema is plausible when this field is filled.

    The test's rule, not P6's -- "which evidence activates which domain is
    unauthored", so the plan holds the slot and the caller fills it.
    """
    return ActivationSignal(
        schema_id=schema_id,
        activates=lambda rows: any(row["field_key"] == field_key for row in rows))


@pytest.fixture()
def abstract(p6_conn, tmp_path):
    """§3.11's worked case, as facts: a research artifact submitted with an
    application. `project = PVA/RDP`, `artifact_type = abstract`,
    `purpose = university application`, `target_university = UChicago`."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="PVA-RDP abstract.pdf")
    for field_key, value in (("project", "PVA/RDP"),
                             ("artifact_type", "abstract"),
                             ("purpose", "university application"),
                             ("target_university", "UChicago")):
        _fact(p6_conn, file_id=file_id, content_hash=content_hash,
              field_key=field_key, value=value)
    return file_id, content_hash


# --- the ten schemas, and the four that carry no fields ----------------------

def test_the_ten_recognised_schemas_are_named_once():
    assert SCHEMA_IDS == ("academic", "college_applications", "research", "career",
                          "photos", "code", "finance", "identity", "medical",
                          "legal")
    assert len(set(SCHEMA_IDS)) == 10


def test_the_field_bearing_schemas_are_exactly_the_non_universal_field_scopes():
    # One vocabulary, two views: a scope is a field row's home, a schema id is what
    # activates. They cannot drift because the second is derived from the first.
    assert set(FIELD_SCOPES) - {UNIVERSAL_SCOPE} == set(SCHEMA_IDS) - set(
        FIELD_LESS_SCHEMA_IDS)
    assert UNIVERSAL_SCOPE not in SCHEMA_IDS


def test_career_identity_medical_and_legal_carry_no_field_rows(p6_conn):
    # D1 (narrowed): "Do not author career fields. Not in this task, not in the domain
    # catalogue as field rows. Career is owed before P10." Identity, medical and legal
    # are §3.15 safety domains that §3.11 gives no field row.
    assert FIELD_LESS_SCHEMA_IDS == ("career", "identity", "medical", "legal")
    for schema_id in FIELD_LESS_SCHEMA_IDS:
        assert schema_fields(schema_id) == ()
        assert schema_id not in DOMAIN_FIELDS


def test_the_catalogue_constant_and_the_loaded_table_are_the_same_data(p6_conn):
    # `DOMAIN_FIELDS` and the `fields` rows `create_fields` loaded must agree, or the
    # allowlist and the model's schema check would be reading two different lists.
    #
    # CONTRADICTION, reported and NOT resolved. The plan wrote this assertion as
    # equality --
    #     {row["field_key"] for row in fields_in_scope(conn, schema_id)} == set(keys)
    # -- and it is FALSE against the live Task 2 catalogue, whose own docstring says
    # so: "`project` and `artifact_type` are declared at `research` and referenced by
    # `code`, so `fields_in_scope(conn, "code")` returns two rows where
    # `DOMAIN_FIELDS["code"]` names four." A scope is where a key is DECLARED; a
    # DOMAIN_FIELDS entry is which §3.11 sentence REFERENCES it. What is true, and
    # what the allowlist actually needs, is the containment below plus every
    # referenced key being a real catalogue row.
    for schema_id, keys in DOMAIN_FIELDS.items():
        declared = {row["field_key"] for row in fields_in_scope(p6_conn, schema_id)}
        assert declared <= set(keys)
        for field_key in keys:
            assert get_field(p6_conn, field_key)["field_key"] == field_key
    # The divergence is exactly one entry, and it is the shared-field entry.
    diverging = {schema_id for schema_id, keys in DOMAIN_FIELDS.items()
                 if {row["field_key"] for row in fields_in_scope(p6_conn, schema_id)}
                 != set(keys)}
    assert diverging == {"code"}


def test_an_unrecognised_schema_is_refused_rather_than_created():
    with pytest.raises(UnknownSchema):
        ActivationSignal(schema_id="astrology", activates=lambda rows: True)
    with pytest.raises(UnknownSchema):
        schema_fields("astrology")


# --- activation: the universal set always, a domain only on evidence ---------

def test_the_universal_set_applies_to_every_file(p6_conn, tmp_path):
    # §3.11: "a small shared set of universal file facts" -- shared meaning every
    # file, with no signal required.
    file_id, content_hash = _record(p6_conn, tmp_path, name="anything.pdf")
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=ActivationSignals(()))
    universal = {row["field_key"] for row in fields_in_scope(p6_conn,
                                                             UNIVERSAL_SCOPE)}
    assert set(allowlist) == universal
    assert universal


def test_target_university_is_not_a_field_every_file_is_expected_to_have(
        p6_conn, tmp_path):
    # §3.11, verbatim: "This means target university is not a fact that every file is
    # expected to have. It is a field available only when the Applications domain is
    # plausibly active."
    file_id, content_hash = _record(p6_conn, tmp_path, name="plain.pdf")
    assert "target_university" not in active_field_allowlist(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=ActivationSignals(()))
    assert "target_university" in DOMAIN_FIELDS["college_applications"]


def test_no_signal_activates_no_domain(p6_conn, abstract):
    # "Domain activation signals ... Which evidence activates which domain is
    # unauthored." An empty signal set is the honest behaviour of an unauthored rule,
    # not a reason to guess.
    file_id, content_hash = abstract
    assert active_domains(p6_conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=ActivationSignals(())) == frozenset()


def test_the_module_authors_no_activation_signal():
    import facts.domains as module
    assert [name for name, value in vars(module).items()
            if isinstance(value, (ActivationSignal, ActivationSignals))] == []
    with pytest.raises(TypeError):
        ActivationSignals()


def test_a_duplicate_signal_for_one_schema_is_refused():
    signal = _when_field_present("research", "project")
    with pytest.raises(ValueError):
        ActivationSignals((signal, signal))


# --- Done-means 14: several domains on one file, none dropped ----------------

def test_one_file_holds_four_facts_across_two_domains(p6_conn, abstract):
    # Done-means 14, as F4 resolves its field names: `document type` is the design's
    # generic word for whichever specific field the active domain declares, and
    # §3.11's own worked case is a research artifact, so it is `artifact_type`.
    file_id, content_hash = abstract
    held = {(row["field_key"], row["canonical_value"])
            for row in facts_for_file(p6_conn, file_id, content_hash)}
    assert held == {("project", "PVA/RDP"), ("artifact_type", "abstract"),
                    ("purpose", "university application"),
                    ("target_university", "UChicago")}

    signals = ActivationSignals((_when_field_present("research", "project"),
                                 _when_field_present("college_applications",
                                                     "target_university")))
    assert active_domains(p6_conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=signals) == frozenset(
        {"research", "college_applications"})


def test_no_domain_is_forced_to_win(p6_conn, abstract):
    # §3.11: "the product does not need to decide which of those perspectives will
    # ultimately determine its physical location. It preserves both."
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("research", "project"),
                                 _when_field_present("college_applications",
                                                     "target_university")))
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    for field_key in ("project", "artifact_type", "purpose", "target_university"):
        assert field_key in allowlist
    assert set(DOMAIN_FIELDS["research"]) <= set(allowlist)
    assert set(DOMAIN_FIELDS["college_applications"]) <= set(allowlist)


def test_no_field_is_dropped_when_two_domains_share_one(p6_conn, abstract):
    # `project` and `artifact_type` belong to Research AND Code. Two active domains
    # must list each once and lose neither.
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("research", "project"),
                                 _when_field_present("code", "project")))
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    assert len(allowlist) == len(set(allowlist))
    assert set(DOMAIN_FIELDS["research"]) <= set(allowlist)
    assert set(DOMAIN_FIELDS["code"]) <= set(allowlist)
    assert allowlist.count("project") == 1
    assert allowlist.count("artifact_type") == 1


def test_code_alone_reaches_only_the_fields_the_code_scope_declares(p6_conn,
                                                                    abstract):
    # NOT IN THE PLAN. Added to make the contradiction above executable rather than
    # only written down.
    #
    # `active_field_allowlist` walks DECLARATION scopes (`fields_in_scope`), so
    # activating Code alone yields `repository` and `programming_language` but NOT
    # `project` or `artifact_type` -- which §3.11's own Code sentence names: "Code
    # files may use project, repository, programming language, and artifact type."
    # §3.5 makes the allowlist what the model may propose, so on the plan's
    # implementation a Code-only file cannot be proposed a `project`.
    #
    # The plan's own shared-field test sidesteps this by activating Research too.
    # This test pins the behaviour the plan specified; it is a tripwire, not an
    # endorsement. If the allowlist is later rebuilt on `DOMAIN_FIELDS`, this is the
    # test that says so.
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("code", "project"),))
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    assert {"repository", "programming_language"} <= set(allowlist)
    assert "project" not in allowlist
    assert "artifact_type" not in allowlist
    assert not set(DOMAIN_FIELDS["code"]) <= set(allowlist)


def test_an_inactive_domains_fields_stay_out_of_the_allowlist(p6_conn, abstract):
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("research", "project"),))
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    assert "target_university" not in allowlist
    assert "capture_year" not in allowlist
    assert set(DOMAIN_FIELDS["research"]) <= set(allowlist)


def test_a_field_less_schema_activates_and_contributes_nothing(p6_conn, abstract):
    # Activating `career` must not cause a career field to appear. S3's deferral holds
    # and P6 does not un-defer it by side effect.
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("career", "project"),))
    assert active_domains(p6_conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=signals) == frozenset({"career"})
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    assert set(allowlist) == {row["field_key"]
                              for row in fields_in_scope(p6_conn, UNIVERSAL_SCOPE)}


# --- the allowlist is a value, and it is deterministic -----------------------

def test_the_allowlist_is_deterministic_and_ordered_by_the_catalogue(
        p6_conn, abstract):
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("college_applications",
                                                     "target_university"),
                                 _when_field_present("research", "project")))
    first = active_field_allowlist(p6_conn, file_id=file_id,
                                   content_hash=content_hash,
                                   activation_signals=signals)
    reordered = ActivationSignals(tuple(reversed(signals.signals)))
    assert active_field_allowlist(p6_conn, file_id=file_id,
                                  content_hash=content_hash,
                                  activation_signals=reordered) == first
    universal = tuple(row["field_key"]
                      for row in fields_in_scope(p6_conn, UNIVERSAL_SCOPE))
    assert first[:len(universal)] == universal


def test_activation_is_per_file_version(p6_conn, tmp_path):
    # §3.4 and §8.2 make every P6 read per file VERSION, so a prior version's facts
    # cannot activate a domain on this one.
    file_id, content_hash = _record(p6_conn, tmp_path, name="v1.pdf")
    _fact(p6_conn, file_id=file_id, content_hash=content_hash,
          field_key="project", value="PVA/RDP")
    signals = ActivationSignals((_when_field_present("research", "project"),))
    assert active_domains(p6_conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=signals) == frozenset({"research"})
    assert active_domains(p6_conn, file_id=file_id, content_hash="f" * 64,
                          activation_signals=signals) == frozenset()


def test_domains_imports_nothing_from_the_research_domain_library():
    # `planning/domains/` is a 574-entry research artifact, not this catalogue.
    # Task 25 asserts the whole directory is imported nowhere in `facts`; this is the
    # module-local half of the same guard.
    import facts.domains as module
    assert module.__doc__ is not None
    imported = {value.__name__ for value in vars(module).values()
                if getattr(value, "__module__", None) is None
                and hasattr(value, "__name__")}
    assert not any(name.startswith("domains.") or name == "roster"
                   for name in imported)
    assert all(not getattr(value, "__module__", "").startswith("planning")
               for value in vars(module).values())
