# tests/p7/test_p7_items.py
"""§8.4's compact dossier: what a request may name, and what it may not.

Three of the assertions here are held open on purpose, and each says so in its own
docstring rather than in a comment a reader has to find.

`filename` is a SIXTH kind and §8.4's sentence names FIVE. §7.7 puts the filename in
the residual dossier and §7.3 forbids filenames in prompts only for Protected
Records. P7's SPEC adopts the reading that makes §7.3 non-vacuous and lists it as its
own Open question 2. NEEDS-JOSEPH B5d and C9a. The tests below prove the kind is
unadmittable without an explicit opt-in; they never prove the reading is right.

The always-local check over `MetadataField.name` is a VOCABULARY check against §8.4's
nine names, not a detector. `MetadataField(name="current_path")` is NOT caught and a
test says so by name, because a synonym list would be the gazetteer P7 is forbidden
to own.

`_normalise` is Task 2's transformation -- `word.lower().replace(" ", "_")` -- and a
test asserts it is the identity on every member of `ALWAYS_LOCAL`. If Task 2's
derivation ever changes, that test fails here rather than opening a hole.
"""
from __future__ import annotations

import dataclasses
import inspect

import pytest

from evidence_shape.location import TextSpan
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_run
from extractors.long_tail import (
    POTENTIALLY_SENSITIVE,
    SensitivitySignal,
    record_sensitivity_signals,
)

import privacy.items as items
from privacy.items import (
    FILENAME_OPEN_QUESTION,
    ITEM_FIELDS,
    RATIFIED_ITEM_KINDS,
    UNRATIFIED_ITEM_KINDS,
    AlwaysLocalRequested,
    CandidateLabel,
    EvidenceReference,
    Excerpt,
    Filename,
    MetadataField,
    ProtectedItemRequested,
    RedactedIdentifier,
    RequestedItem,
    UnratifiedItemKind,
    WholeDocumentRequested,
    check_item,
    is_whole_document,
    kind_of,
    sensitive_observation_keys,
)
from privacy.vocabulary import ALWAYS_LOCAL, ITEM_KINDS, OPEN_QUESTIONS, OutOfVocabulary

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
CONTENT_HASH = "a" * 64
KEY = "sha256:" + "b" * 64
OTHER_KEY = "sha256:" + "c" * 64
BODY_LENGTH = 39

#: The six kinds, constructed once, so every structural assertion runs over all six
#: rather than over whichever one the test author remembered.
ONE_OF_EACH: tuple[RequestedItem, ...] = (
    Excerpt(observation_key=KEY, span=TextSpan(16, 27), reason="the group's subject"),
    RedactedIdentifier(observation_key=KEY, span=TextSpan(16, 27),
                       identifier_class="passport_number"),
    CandidateLabel(label="Passport"),
    MetadataField(name="page_count"),
    EvidenceReference(observation_key=KEY),
    Filename(file_id="file-1"),
)

#: A permissive default for the three keywords a given test is not about. Every one
#: of them is REQUIRED on `check_item` (A11); this helper spells them so a test that
#: IS about one of them can override exactly that one and nothing else.
def admit(item, *, unit_length=None, protected=False, sensitive_keys=frozenset(),
          allow_unratified=True) -> None:
    check_item(item, unit_length=unit_length, protected=protected,
               sensitive_keys=sensitive_keys, allow_unratified=allow_unratified)


# --- the six kinds, and the five that §8.4 actually names ----------------------

def test_the_six_kinds_are_task_twos_six_and_split_five_plus_one():
    assert RATIFIED_ITEM_KINDS + UNRATIFIED_ITEM_KINDS == ITEM_KINDS
    assert len(RATIFIED_ITEM_KINDS) == 5
    assert UNRATIFIED_ITEM_KINDS == ("filename",)


def test_every_kind_has_a_dataclass_and_every_dataclass_has_a_kind():
    assert set(ITEM_FIELDS) == set(ITEM_KINDS)
    assert {kind_of(item) for item in ONE_OF_EACH} == set(ITEM_KINDS)


def test_kind_of_refuses_a_type_that_is_not_one_of_the_six():
    # A foreign object is not "an unknown kind" to be tolerated: §8.4's list is
    # closed and Task 2's `OutOfVocabulary` is the load error that says so.
    with pytest.raises(OutOfVocabulary):
        kind_of("excerpt")
    with pytest.raises(OutOfVocabulary):
        kind_of(TextSpan(0, 1))


def test_item_fields_are_read_from_the_dataclasses_and_never_retyped():
    for item in ONE_OF_EACH:
        expected = tuple(f.name for f in dataclasses.fields(item))
        assert ITEM_FIELDS[kind_of(item)] == expected


def test_the_four_reference_only_shapes_are_the_ones_spec_six_requires():
    # SPEC §6: "requested_items[] item kinds from §4 above -- references only, never
    # materialised content." A `value` on any of these four would make that false.
    assert ITEM_FIELDS["candidate_label"] == ("label",)
    assert ITEM_FIELDS["metadata_field"] == ("name",)
    assert ITEM_FIELDS["evidence_reference"] == ("observation_key",)
    assert ITEM_FIELDS["filename"] == ("file_id",)


def test_no_item_kind_has_a_field_that_could_carry_document_content():
    # The structural half of "not expressible": eight of §8.4's nine always-local
    # items have nowhere to live, because no kind has a content-bearing field.
    forbidden = {"value", "text", "content", "raw_value", "path", "current_path",
                 "excerpt", "ocr_text", "bytes", "content_hash", "filename"}
    for item in ONE_OF_EACH:
        assert not set(ITEM_FIELDS[kind_of(item)]) & forbidden, kind_of(item)


def test_evidence_reference_is_an_id_only_with_no_content_field():
    # SPEC §4: "evidence_reference   an id only -- no content". Checked with
    # `dataclasses.fields`, not by reading the class body.
    names = [f.name for f in dataclasses.fields(EvidenceReference)]
    assert names == ["observation_key"]


def test_every_item_is_frozen():
    # A request the gate has already decided on must not change under it.
    for item in ONE_OF_EACH:
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(item, ITEM_FIELDS[kind_of(item)][0], "anything else")


def test_the_two_addressed_kinds_accept_a_span_of_none():
    # Task 9's pin: `None` is the container-path form -- §2.3's cell and §2.8's EXIF
    # field, where `unit_for_observation` returns None and the address is the whole
    # citation. A non-optional span makes those unaddressable.
    assert Excerpt(observation_key=KEY, span=None, reason="the cell").span is None
    assert RedactedIdentifier(observation_key=KEY, span=None,
                              identifier_class="account_number").span is None


# --- the always-local nine: one test per name ---------------------------------
# §8.4: "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS,
# user edits, group memberships, and raw sensitive values should remain local."
# SPEC §3: "Nothing in this set can be named as a releasable item kind. The gate has
# no code path that materialises one."

@pytest.mark.parametrize("surface, key", [
    ("Paths", "paths"),
    ("complete extracted text", "complete_extracted_text"),
    ("OCR output", "ocr_output"),
    ("file hashes", "file_hashes"),
    ("image EXIF", "image_exif"),
    ("GPS", "gps"),
    ("user edits", "user_edits"),
    ("group memberships", "group_memberships"),
    ("raw sensitive values", "raw_sensitive_values"),
])
def test_an_always_local_name_is_not_expressible_as_an_item(surface, key):
    """Nine names, nine cases, refused at CONSTRUCTION.

    The skeleton's word is "not expressible", and Task 20 has already been written
    against it: "Task 7 makes the nine named kinds unconstructible, so a request
    holding 'OCR output' cannot be built and cannot be a fixture." So the refusal is
    in `__post_init__` and `check_item` does not repeat it.

    `MetadataField.name` is the only field that names a KIND OF DATA. The other five
    kinds carry an address, an id, or a destination label, and a test above proves
    none of them has a content-bearing field to smuggle one through.
    """
    assert key in ALWAYS_LOCAL
    with pytest.raises(AlwaysLocalRequested) as caught:
        MetadataField(name=surface)
    assert key in str(caught.value)


def test_normalise_is_task_twos_transformation_and_not_a_second_one():
    # Task 2 derived ALWAYS_LOCAL from §8.4's sentence with
    # `word.lower().replace(" ", "_")`. If that derivation ever changes, this fails
    # here rather than silently opening a hole in the check above.
    for key in ALWAYS_LOCAL:
        assert items._normalise(key) == key


def test_the_always_local_check_is_exact_and_not_a_prefix_match():
    # "GPS Logs" normalises to "gps_logs", which is not "gps". A check that matched
    # loosely would be a keyword list, and §8.4 does not authorise one.
    assert MetadataField(name="GPS Logs").name == "GPS Logs"
    assert MetadataField(name="page_count").name == "page_count"


def test_a_candidate_label_naming_a_data_kind_is_not_refused():
    """§4.5 and §5.4 make a candidate label a DESTINATION name, not a data kind.

    The always-local set is a set of kinds of DATA. Applying the check to a label
    would refuse a legitimate folder called "GPS" while releasing nothing extra:
    the label carries no observation and no value.
    """
    assert CandidateLabel(label="GPS").label == "GPS"


def test_a_metadata_field_named_current_path_is_not_caught_and_that_is_deliberate():
    """The reported gap. `current_path` is not one of §8.4's nine names.

    Catching it would need a synonym list, and SPEC's constraint is that
    `src/privacy/` "contains no regex, no gazetteer, no filename pattern, no keyword
    list" -- Task 21 asserts that by introspection. A `metadata_field` is "a named
    non-sensitive field" whose name the CALLER declares; Task 13 decides on the
    declared name and P7 owns no detector that could second-guess it.

    This test exists so a later reader finds a decision instead of an oversight.
    """
    assert MetadataField(name="current_path").name == "current_path"
    assert "current_path" not in ALWAYS_LOCAL


def test_a_file_id_that_is_a_path_is_refused_as_the_first_always_local_name():
    # §8.4's first always-local word is "Paths". A `file_id` carrying a separator is
    # a path wearing an id's field name. One character, not a pattern catalogue.
    with pytest.raises(AlwaysLocalRequested) as caught:
        Filename(file_id="/Users/j/Documents/passport.pdf")
    assert "paths" in str(caught.value)
    assert Filename(file_id="file-1").file_id == "file-1"


def test_items_imports_no_mode_and_no_policy_so_the_nine_are_not_a_default():
    """Task 6's local-first posture is a DEFAULT; these nine are not.

    Task 6: "W1 binds the DEFAULT, never the choice" -- a stored `cloud_assisted`
    policy comes back unchanged. The always-local set is the opposite kind of rule:
    no mode, no policy, no consent option and no default makes one expressible. The
    structural statement of that is that this module has no branch a mode could
    change, so it binds neither `defaults` nor `policy`.
    """
    bound = {value.__name__ for value in vars(items).values()
             if inspect.ismodule(value)}
    bound |= {getattr(value, "__module__", "") for value in vars(items).values()}
    assert "privacy.defaults" not in bound
    assert "privacy.policy" not in bound
    assert not any(f.name == "operation_mode"
                   for item in ONE_OF_EACH
                   for f in dataclasses.fields(item))


# --- whole_document_requested -------------------------------------------------

def test_an_excerpt_covering_the_whole_unit_is_a_whole_document():
    # §8.4: "It should not send full documents where a short heading or OCR excerpt
    # is enough to resolve the question."
    whole = Excerpt(observation_key=KEY, span=TextSpan(0, BODY_LENGTH),
                    reason="all of it")
    assert is_whole_document(whole, unit_length=BODY_LENGTH) is True
    with pytest.raises(WholeDocumentRequested) as caught:
        admit(whole, unit_length=BODY_LENGTH)
    assert "0" in str(caught.value) and str(BODY_LENGTH) in str(caught.value)


def test_a_span_that_over_covers_the_unit_is_still_a_whole_document():
    # A span wider than the unit is not "outside the rule"; it is the same request
    # with worse arithmetic. `<= 0` and `>= unit_length`, not `== `.
    wide = Excerpt(observation_key=KEY, span=TextSpan(0, BODY_LENGTH + 400),
                   reason="all of it and then some")
    assert is_whole_document(wide, unit_length=BODY_LENGTH) is True


def test_a_bounded_excerpt_is_not_a_whole_document():
    short = Excerpt(observation_key=KEY, span=TextSpan(16, 27), reason="the number")
    assert is_whole_document(short, unit_length=BODY_LENGTH) is False
    admit(short, unit_length=BODY_LENGTH)


def test_a_redacted_identifier_over_the_whole_unit_is_also_refused():
    # The rule is about the SPAN, not about the kind. A redaction that covered the
    # whole unit would send the whole unit with one value starred out.
    whole = RedactedIdentifier(observation_key=KEY, span=TextSpan(0, BODY_LENGTH),
                               identifier_class="passport_number")
    with pytest.raises(WholeDocumentRequested):
        admit(whole, unit_length=BODY_LENGTH)


def test_a_container_path_address_is_never_a_whole_document():
    # Task 9: `unit_for_observation` returns None for §2.3's cell and §2.8's EXIF
    # field. There is no unit, so there is nothing for a span to cover, and a
    # `None` unit_length must not be read as "length zero" -- which would make every
    # cell a whole document.
    cell = Excerpt(observation_key=KEY, span=None, reason="the cell")
    assert is_whole_document(cell, unit_length=None) is False
    admit(cell, unit_length=None)


def test_a_kind_with_no_span_is_never_a_whole_document():
    for item in (CandidateLabel(label="Passport"), MetadataField(name="page_count"),
                 EvidenceReference(observation_key=KEY), Filename(file_id="file-1")):
        assert is_whole_document(item, unit_length=BODY_LENGTH) is False


# --- raw sensitive values: P5's signal, and the excerpt/identifier asymmetry ----

def test_an_excerpt_over_a_p5_signalled_key_is_always_local():
    """§8.4's ninth always-local name, and the only one that needs P5.

    P5 marks each located value it emits with POTENTIALLY_SENSITIVE, keyed on P4's
    `observation_key`. P7 owns no detector, so this signal is the only thing in the
    product that can recognise a "raw sensitive value" at all.
    """
    with pytest.raises(AlwaysLocalRequested) as caught:
        admit(Excerpt(observation_key=KEY, span=TextSpan(16, 27), reason="it"),
              unit_length=BODY_LENGTH, sensitive_keys=frozenset({KEY}))
    assert "raw_sensitive_values" in str(caught.value)


def test_a_redacted_identifier_over_the_same_key_is_permitted():
    # This asymmetry IS §8.4's "redacted identifiers" allowance. Task 8's transform
    # is injected with no default, so the permitted path cannot emit a raw value.
    admit(RedactedIdentifier(observation_key=KEY, span=TextSpan(16, 27),
                             identifier_class="passport_number"),
          unit_length=BODY_LENGTH, sensitive_keys=frozenset({KEY}))


def test_an_excerpt_over_an_unsignalled_key_is_permitted():
    admit(Excerpt(observation_key=OTHER_KEY, span=TextSpan(16, 27), reason="it"),
          unit_length=BODY_LENGTH, sensitive_keys=frozenset({KEY}))


def test_check_item_requires_every_one_of_its_four_keywords():
    # A11: none of the four has a default. A build that forgets one is a TypeError,
    # never a release. `sensitive_keys` in particular: a default of `frozenset()`
    # would mean "nothing is sensitive" for a caller who never wired P5.
    item = Excerpt(observation_key=KEY, span=TextSpan(16, 27), reason="it")
    for omit in ("unit_length", "protected", "sensitive_keys", "allow_unratified"):
        kwargs = dict(unit_length=BODY_LENGTH, protected=False,
                      sensitive_keys=frozenset(), allow_unratified=False)
        del kwargs[omit]
        with pytest.raises(TypeError):
            check_item(item, **kwargs)


def test_sensitive_observation_keys_walks_p4_runs_to_p5_signals(p7_conn):
    record_run(p7_conn, ExtractionRun(
        run_id="run-1", file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="long_tail", extractor_version="1.0.0",
        source_type="contacts", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, observation_count=2))
    record_sensitivity_signals(
        p7_conn, run_id="run-1",
        signals=(SensitivitySignal(observation_index=0,
                                   signal=POTENTIALLY_SENSITIVE,
                                   basis="every VCF value"),),
        observation_keys=(KEY, OTHER_KEY), now=FIXED_CLOCK)
    assert sensitive_observation_keys(p7_conn, "file-1") == frozenset({KEY})


def test_sensitive_observation_keys_is_empty_for_a_file_with_no_runs(p7_conn):
    # The honest v1 posture: nothing signalled is not "nothing sensitive". It is the
    # caller's job to know that, and the empty set says so without inventing a rule.
    assert sensitive_observation_keys(p7_conn, "file-404") == frozenset()


def test_only_the_potentially_sensitive_signal_counts(p7_conn):
    record_run(p7_conn, ExtractionRun(
        run_id="run-2", file_id="file-2", content_hash=CONTENT_HASH,
        extractor_name="long_tail", extractor_version="1.0.0",
        source_type="contacts", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, observation_count=1))
    record_sensitivity_signals(
        p7_conn, run_id="run-2",
        signals=(SensitivitySignal(observation_index=0, signal="something else",
                                   basis="not P5's word"),),
        observation_keys=(KEY,), now=FIXED_CLOCK)
    assert sensitive_observation_keys(p7_conn, "file-2") == frozenset()


# --- filename: the unratified sixth kind -- NEEDS-JOSEPH B5d and C9a -----------

def test_filename_is_the_unratified_sixth_kind_needs_joseph_b5d_c9a():
    """SPEC Open question 2 -- the one place the contract resolved a conflict.

    §8.4 names FIVE releasable kinds and puts *paths* in the always-local set. §7.7
    puts *the filename* in the residual dossier. §7.3 forbids filenames in prompts
    ONLY for Protected Records, which is vacuous under any reading that forbade them
    everywhere. P7's SPEC reads directory path != filename, permits `filename` for
    non-protected files, denies it for protected ones, and lists the reading as its
    own Open question 2 for the reviewer.

    NEEDS-JOSEPH B5d and C9a. This test proves the kind is UNADMITTABLE without an
    explicit opt-in. It does not prove the reading is right, and nothing in P7 does.
    """
    assert UNRATIFIED_ITEM_KINDS == ("filename",)
    assert "filename" not in RATIFIED_ITEM_KINDS
    assert FILENAME_OPEN_QUESTION == OPEN_QUESTIONS[2]
    for section in ("8.4", "7.7", "7.3"):
        assert section in FILENAME_OPEN_QUESTION


def test_a_filename_cannot_be_admitted_without_the_explicit_opt_in():
    with pytest.raises(UnratifiedItemKind) as caught:
        check_item(Filename(file_id="file-1"), unit_length=None, protected=False,
                   sensitive_keys=frozenset(), allow_unratified=False)
    assert "filename" in str(caught.value)
    assert "B5d" in str(caught.value) and "C9a" in str(caught.value)


def test_the_five_ratified_kinds_need_no_opt_in():
    for item in ONE_OF_EACH:
        if kind_of(item) in UNRATIFIED_ITEM_KINDS:
            continue
        check_item(item, unit_length=None, protected=False,
                   sensitive_keys=frozenset(), allow_unratified=False)


def test_a_filename_is_permitted_for_a_non_protected_file():
    admit(Filename(file_id="file-1"), protected=False)


def test_a_filename_is_denied_for_a_protected_file():
    """§7.3: Protected Records "must not cause filenames or content to be exposed in
    model prompts" -- no locality qualifier, so this refuses for ANY target, which is
    the stricter of the two available readings. §8.4's "not included in cloud-model
    prompts BY DEFAULT" is what the consent path reopens, and that path is
    `NeedsConsent`, not a weaker check here.
    """
    with pytest.raises(ProtectedItemRequested) as caught:
        admit(Filename(file_id="file-1"), protected=True)
    assert "7.3" in str(caught.value)


def test_protected_does_not_refuse_the_other_five_kinds_here():
    # One rule, one home. §7.3's content half and §8.4's cloud-prompt half are the
    # gate's `protected_records_template` and `protected_cloud_target` denials, which
    # Task 13 builds and `release.DECISION_ORDER` sequences. A second copy here would
    # be a rule with two homes.
    for item in ONE_OF_EACH:
        if kind_of(item) in UNRATIFIED_ITEM_KINDS:
            continue
        admit(item, unit_length=None, protected=True)


def test_unratified_maps_to_no_denial_reason():
    # A caller naming an unratified kind has a BUILD defect, not a policy problem.
    # It must propagate to the developer rather than reach a user as a `Denied` they
    # could try to consent around. Task 13's eight builders are complete without a
    # ninth.
    from privacy.vocabulary import DENIAL_REASONS
    assert not any("unratified" in reason for reason in DENIAL_REASONS)
    assert len(DENIAL_REASONS) == 8
