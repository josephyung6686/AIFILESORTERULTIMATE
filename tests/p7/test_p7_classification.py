# tests/p7/test_p7_classification.py
"""SPEC §2's record, and the one resolution the design states twice.

"Absence of a classification resolves to `unreadable_unclassified`, never to
`public_low`." §8.6 says why: "Cost exhaustion must never turn into lower-quality
automatic classification." The failure that sentence forbids is precisely defaulting
an unclassified file to public so the pipeline can continue, and the tests below are
written to fail if any input at all produces `public_low` without a record saying so.

The second thing proved here is D2's: `Unreadable or unclassified` is a GATE OUTCOME.
This module returns it to a caller and cannot write it anywhere, and the namespace
tests are what keep that true when someone later needs a shortcut.
"""
import dataclasses
import json
import re
import uuid

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.observation import observation_key
from evidence_shape.runs import COMPLETENESS, ExtractionRun
from evidence_shape.store import record_run
from evidence_shape.vocabulary import ZERO_OBSERVATION_COMPLETENESS

from extractors.long_tail import (
    POTENTIALLY_SENSITIVE, SensitivitySignal, record_sensitivity_signals,
)

import privacy.classification as classification
from privacy.classification import (
    CLASSIFICATION_FIELDS, COMPLETENESS_RULE, ClassificationRecord,
    UnbackedClassification, completeness_implies_unclassified, resolve_class,
    sensitivity_signal_keys,
)
from privacy.vocabulary import (
    CLASSIFICATION_BASES, HANDLING_CLASSES, OutOfVocabulary, USER, USER_CONFIRMED,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"


@pytest.fixture()
def file_id(p7_conn, tmp_path):
    """A real P1 row. The record is keyed on (file_id, content_hash) and a synthesized
    pair would not exercise the identity D2 makes authoritative."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "passport-scan.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    return record_file(
        p7_conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


@pytest.fixture()
def content_hash(p7_conn, file_id):
    return get_file(p7_conn, file_id)["content_hash"]


def a_key(content_hash, raw_value="Passport No. X", locator="zone=body/page=1"):
    return observation_key(content_hash=content_hash, extractor_name="pdf_text",
                           locator=locator, raw_value=raw_value)


def a_record(file_id, content_hash, **over):
    fields = dict(file_id=file_id, content_hash=content_hash,
                  handling_class="highly_sensitive_credential_bearing",
                  protected=True, basis="detector",
                  evidence_refs=(a_key(content_hash),),
                  reliability_state="validated", observed_at=FIXED_CLOCK)
    fields.update(over)
    return ClassificationRecord(**fields)


def a_run(file_id, content_hash, run_id="run-1", completeness="complete"):
    return ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf_text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native",
        config={"reader": "injected"}, completeness=completeness,
        started_at=FIXED_CLOCK, observation_count=1, finished_at=FIXED_CLOCK)


# --- SPEC §2's eight fields ---------------------------------------------------

def test_the_eight_fields_are_specs_eight_in_specs_order():
    assert CLASSIFICATION_FIELDS == (
        "file_id", "content_hash", "handling_class", "protected", "basis",
        "evidence_refs", "reliability_state", "observed_at",
    )
    assert tuple(f.name for f in dataclasses.fields(ClassificationRecord)) == \
        CLASSIFICATION_FIELDS


def test_the_record_is_frozen(file_id, content_hash):
    record = a_record(file_id, content_hash)
    with pytest.raises(dataclasses.FrozenInstanceError):
        record.handling_class = "public_low"


def test_the_record_is_keyed_on_bytes_not_on_a_path(file_id, content_hash):
    # D2: "keyed on the hash because a classification is about BYTES, and new bytes at
    # a path are a new file version that inherits nothing."
    old = a_record(file_id, content_hash)
    new = a_record(file_id, "0" * 64, evidence_refs=(a_key("0" * 64),))
    assert old.file_id == new.file_id
    assert old != new
    assert (old.file_id, old.content_hash) != (new.file_id, new.content_hash)


def test_a_sequence_of_refs_is_frozen_on_the_way_in(file_id, content_hash):
    record = a_record(file_id, content_hash, evidence_refs=[a_key(content_hash)])
    assert isinstance(record.evidence_refs, tuple)


def test_a_bare_string_is_not_a_sequence_of_refs(file_id, content_hash):
    # tuple("sha256:...") is 71 one-character refs. Refusing the string is the only
    # way that mistake is visible.
    with pytest.raises(UnbackedClassification):
        a_record(file_id, content_hash, evidence_refs=a_key(content_hash))


# --- evidence-backed (§8.4) ---------------------------------------------------

def test_a_detector_record_with_no_evidence_is_unbacked(file_id, content_hash):
    # §8.4: the classification "is itself evidence-backed". §3.1's principle: every
    # fact preserves where it came from.
    with pytest.raises(UnbackedClassification) as caught:
        a_record(file_id, content_hash, evidence_refs=())
    assert "detector" in str(caught.value)


def test_a_user_record_and_a_safety_domain_record_need_no_evidence(
        file_id, content_hash):
    # The SPEC scopes the rule to one basis: "evidence_refs is non-empty for any
    # basis = detector classification". The user's act is the evidence (§8.4's
    # "revised by the user"); a safety domain is §3.15's rule about a domain, not a
    # reading of a span. Requiring evidence here would invent a stricter rule.
    assert a_record(file_id, content_hash, basis=USER,
                    evidence_refs=(), reliability_state=USER_CONFIRMED)
    assert a_record(file_id, content_hash, basis="safety_domain", evidence_refs=())


def test_evidence_refs_must_be_observation_keys_and_not_observation_ids(
        file_id, content_hash):
    # M14: "The key, not the id, is what makes that durable." A per-row
    # observation_id dies on extractor upgrade, so a negative example recorded today
    # would silently stop resolving. `evidence_shape.store.new_id()` mints uuid4.
    with pytest.raises(UnbackedClassification) as caught:
        a_record(file_id, content_hash, evidence_refs=(str(uuid.uuid4()),))
    assert "observation_key" in str(caught.value)


def test_a_content_hash_is_not_an_observation_key(file_id, content_hash):
    # P1's content_hash carries no algorithm prefix; P4's key does. Introspected.
    assert ":" not in content_hash
    assert a_key(content_hash).startswith("sha256:")
    with pytest.raises(UnbackedClassification):
        a_record(file_id, content_hash, evidence_refs=(content_hash,))


def test_a_truncated_or_uppercased_key_is_refused(file_id, content_hash):
    real = a_key(content_hash)
    for bad in (real[:-1], real.upper(), real.replace("sha256", "sha512"), "", None):
        with pytest.raises(UnbackedClassification):
            a_record(file_id, content_hash, evidence_refs=(bad,))


def test_a_real_p4_key_is_accepted_and_survives_an_extractor_version_change(
        file_id, content_hash):
    # MINOR 8: `observation_key` deliberately excludes extractor_version, which is
    # what lets a classification survive an upgrade.
    key = a_key(content_hash)
    assert a_record(file_id, content_hash, evidence_refs=(key,)).evidence_refs == (key,)


# --- the closed vocabularies -------------------------------------------------

def test_an_out_of_vocabulary_handling_class_is_refused(file_id, content_hash):
    with pytest.raises(OutOfVocabulary):
        a_record(file_id, content_hash, handling_class="secret")


def test_p6s_origin_vocabulary_is_not_p7s_basis_vocabulary(file_id, content_hash):
    # P6's five §3.1 origins include "rule" and "LLM interpretation"; P7's basis is
    # three values. The two are never mapped onto one another.
    assert CLASSIFICATION_BASES == ("detector", "safety_domain", "user")
    with pytest.raises(OutOfVocabulary):
        a_record(file_id, content_hash, basis="rule")


def test_reliability_state_is_stored_and_not_validated_here(file_id, content_hash):
    # §3.13's six are P4's -- `evidence_shape.vocabulary.RELIABILITY_STATES`, which
    # Task 2 re-exports -- and Task 4 publishes the ordering. Two validators would be
    # two vocabularies. Non-empty is the only requirement this module makes.
    assert a_record(file_id, content_hash,
                    reliability_state="llm_supported").reliability_state == \
        "llm_supported"
    with pytest.raises(UnbackedClassification):
        a_record(file_id, content_hash, reliability_state="")


def test_protected_is_a_boolean_and_is_never_derived_from_the_class(
        file_id, content_hash):
    # Open question 1: "Is `protected` exactly the top two handling classes?" The
    # design lists five classes and, separately, five kinds of material that enter a
    # protected state, without stating the relation. Both combinations construct.
    assert a_record(file_id, content_hash,
                    handling_class="public_low", protected=True).protected is True
    assert a_record(file_id, content_hash,
                    handling_class="highly_sensitive_credential_bearing",
                    protected=False).protected is False
    with pytest.raises(UnbackedClassification):
        a_record(file_id, content_hash, protected="yes")


def test_no_function_here_maps_a_class_onto_the_protected_flag():
    names = [n for n in vars(classification) if not n.startswith("_")]
    assert not [n for n in names if "protect" in n.lower() and callable(
        getattr(classification, n))]


# --- resolve_class: the one resolution the design states twice ---------------

def test_absence_resolves_to_unreadable_unclassified():
    assert resolve_class(None) == "unreadable_unclassified"


def test_no_input_at_all_produces_public_low_without_a_record_saying_so(
        file_id, content_hash):
    # §8.6: "Cost exhaustion must never turn into lower-quality automatic
    # classification." There is no default-to-public code path anywhere.
    assert resolve_class(None) != "public_low"
    for name in HANDLING_CLASSES:
        record = a_record(file_id, content_hash, handling_class=name)
        assert resolve_class(record) == name
    produced = {resolve_class(None)} | {
        resolve_class(a_record(file_id, content_hash, handling_class=n))
        for n in HANDLING_CLASSES if n != "public_low"}
    assert "public_low" not in produced


def test_resolve_class_refuses_something_that_is_not_a_record():
    for wrong in ({"handling_class": "public_low"}, "public_low", 0, ()):
        with pytest.raises(TypeError):
            resolve_class(wrong)


# --- D2: a gate outcome, and therefore no writer in this module --------------

def test_this_module_contains_no_writer():
    # "Unreadable or unclassified is a GATE OUTCOME, not a file fact." It must never
    # reach `files.sensitivity_state`, and the durable guarantee is that the string is
    # produced by a decision function in a module that can reach no column.
    forbidden = ("set_", "write_", "record_", "mirror_", "update_", "insert_")
    for name, value in vars(classification).items():
        if name.startswith("_") or not callable(value):
            continue
        assert not name.startswith(forbidden), name
    assert "set_sensitivity_state" not in vars(classification)
    for name, value in vars(classification).items():
        assert getattr(value, "__module__", "") != "database_agent.files_table", name


def test_the_only_connection_taking_function_here_reads(p7_conn, file_id):
    assert "conn" not in resolve_class.__code__.co_varnames
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    sensitivity_signal_keys(p7_conn, file_id)
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None


# --- COMPLETENESS_RULE: stated per value, cross-checked against P4 -----------

def test_the_rule_names_p4s_nine_values_and_no_tenth():
    assert tuple(COMPLETENESS_RULE) == COMPLETENESS
    assert len(COMPLETENESS_RULE) == 9


def test_every_value_carries_the_sentence_that_decides_it():
    for name, (implies, reason) in COMPLETENESS_RULE.items():
        assert isinstance(implies, bool), name
        assert isinstance(reason, str) and reason.strip(), name


def test_the_six_that_imply_unclassified_are_p4s_five_plus_unreadable():
    # Grounded against P4's own tuple rather than against a set this author guessed:
    # ZERO_OBSERVATION_COMPLETENESS is where "nothing was opened, so nothing was
    # seen", and `unreadable` is §2.9's "indexed-but-unreadable", which the SPEC maps
    # to this class by name.
    implied = {n for n, (yes, _) in COMPLETENESS_RULE.items() if yes}
    assert implied == set(ZERO_OBSERVATION_COMPLETENESS) | {"unreadable"}
    assert len(implied) == 6


def test_the_three_that_do_not_are_the_ones_where_content_was_read():
    assert {n for n, (yes, _) in COMPLETENESS_RULE.items() if not yes} == \
        {"complete", "capped", "partial"}
    for name in ("complete", "capped", "partial"):
        assert completeness_implies_unclassified(name) is False


def test_a_dataless_run_row_implies_unclassified(p7_conn, file_id, content_hash):
    # 11 §5: "Do not materialize, hash, or extract." A dataless file gets ONE run row
    # recording that the bytes are elsewhere -- it is a file inside a protected
    # container that has no row at all, and no `files` row either, so the gate cannot
    # be asked about it. Both cases end at `unreadable_unclassified`, by two routes.
    record_run(p7_conn, a_run(file_id, content_hash, completeness="dataless"))
    assert completeness_implies_unclassified("dataless") is True
    assert resolve_class(None) == "unreadable_unclassified"


def test_an_unknown_completeness_value_is_refused():
    for wrong in ("indexed-but-unreadable", "empty", "", None, 1):
        with pytest.raises(OutOfVocabulary):
            completeness_implies_unclassified(wrong)


# --- sensitivity_signal_keys: a detector input, and not a detector -----------

def test_signal_keys_are_p4_keys_in_run_then_emit_order(
        p7_conn, file_id, content_hash):
    record_run(p7_conn, a_run(file_id, content_hash, run_id="run-1"))
    record_run(p7_conn, a_run(file_id, content_hash, run_id="run-2"))
    first = a_key(content_hash, raw_value="Passport No. X")
    second = a_key(content_hash, raw_value="a@b.example", locator="zone=body/page=2")
    record_sensitivity_signals(
        p7_conn, run_id="run-1",
        signals=(SensitivitySignal(0, POTENTIALLY_SENSITIVE, "vcf value"),),
        observation_keys=(first,), now=FIXED_CLOCK)
    record_sensitivity_signals(
        p7_conn, run_id="run-2",
        signals=(SensitivitySignal(0, POTENTIALLY_SENSITIVE, "email address"),),
        observation_keys=(second,), now=FIXED_CLOCK)
    assert sensitivity_signal_keys(p7_conn, file_id) == (first, second)


def test_a_file_with_every_value_marked_sensitive_still_has_no_classification(
        p7_conn, file_id, content_hash):
    # THE test for D2's open posture. P5's docstring: "P5 assigns no handling class:
    # section 8.4 gives classification to P7." The detector is unwritten, so a file
    # covered in signals is still unclassified and the gate still denies it.
    record_run(p7_conn, a_run(file_id, content_hash))
    record_sensitivity_signals(
        p7_conn, run_id="run-1",
        signals=(SensitivitySignal(0, POTENTIALLY_SENSITIVE, "vcf value"),),
        observation_keys=(a_key(content_hash),), now=FIXED_CLOCK)
    assert sensitivity_signal_keys(p7_conn, file_id)
    assert resolve_class(None) == "unreadable_unclassified"
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None


def test_signal_keys_deduplicates_across_runs(p7_conn, file_id, content_hash):
    # A re-run of the same extractor at the same content hash produces the same key
    # (MINOR 8). Listing it twice would make one observation look like two.
    same = a_key(content_hash)
    for run_id in ("run-1", "run-2"):
        record_run(p7_conn, a_run(file_id, content_hash, run_id=run_id))
        record_sensitivity_signals(
            p7_conn, run_id=run_id,
            signals=(SensitivitySignal(0, POTENTIALLY_SENSITIVE, "vcf value"),),
            observation_keys=(same,), now=FIXED_CLOCK)
    assert sensitivity_signal_keys(p7_conn, file_id) == (same,)


def test_signal_keys_is_empty_for_a_file_with_no_runs(p7_conn, file_id):
    assert sensitivity_signal_keys(p7_conn, file_id) == ()


def test_signal_keys_ignores_a_signal_that_is_not_p5s(
        p7_conn, file_id, content_hash):
    record_run(p7_conn, a_run(file_id, content_hash))
    key = a_key(content_hash)
    p7_conn.execute(
        "INSERT INTO extraction_sensitivity_signal (run_id, observation_key, signal, "
        "basis, observed_at) VALUES (?, ?, ?, ?, ?)",
        ("run-1", key, "something else", "unknown", FIXED_CLOCK))
    assert sensitivity_signal_keys(p7_conn, file_id) == ()


def test_this_module_publishes_no_detector():
    # SPEC Deferred: "The design states *what* is protected and never *how it is
    # recognised*." No regex, no gazetteer, no filename pattern, no keyword list.
    for name, value in vars(classification).items():
        if name.startswith("_"):
            continue
        assert not isinstance(value, re.Pattern), name
        assert "detect" not in name.lower(), name
        assert "classify" not in name.lower(), name
