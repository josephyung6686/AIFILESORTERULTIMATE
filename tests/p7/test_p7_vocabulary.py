# tests/p7/test_p7_vocabulary.py
"""§8.4's closed vocabularies, and the five strings that share the stem "protected".

Two kinds of assertion live here. Most pin a tuple against the design's own words, in
the design's own order, so a later edit is a red test and not an editorial choice. The
rest pin the boundary: an out-of-vocabulary value is a load error that suggests no
neighbour, no member is a number, and nothing in this module is one of P3's strings
wearing P7's clothes.

Where a vocabulary can be DERIVED from a design sentence mechanically, it is. A test
that retypes the nine always-local items proves the author can retype; a test that
splits the design's sentence proves the identifiers are the design's words.
"""
import re
from collections.abc import Mapping

import pytest

from evidence_shape import vocabulary as p4_vocabulary
from scan_agent.exclusion import LABEL_UNTOUCHED_PROTECTED, REASON_PROTECTED_CONTAINER

import privacy.vocabulary as vocabulary
from privacy.vocabulary import (
    ALWAYS_LOCAL, AUDIT_OUTCOMES, CLASSIFICATION_BASES, CONSENT_OPTIONS,
    DENIAL_REASONS, DISPLAY_FACETS, HANDLING_CLASSES, HANDLING_CLASS_LABELS,
    ITEM_KINDS, MODE_SEMANTICS, OPEN_QUESTIONS, OPERATION_MODES, OutOfVocabulary,
    REDACTED, REDACTION_VALUES, REJECTED, RELIABILITY_STATES, SHOWN, USER,
    USER_CONFIRMED, DETECTOR,
    check_denial_reason, check_handling_class, check_item_kind, check_mode,
)

#: The design's line 50, verbatim. The six reliability states are derived from this
#: sentence run rather than retyped, which is what makes the tuple's ORDER the
#: design's and not an author's.
RELIABILITY_SENTENCES = (
    "A user confirmed fact has been explicitly accepted, entered, renamed, merged, "
    "or corrected by the user. A direct fact was read from a reliable and explicit "
    "source. A validated fact was found by a deterministic rule and passed "
    "contextual checks. An LLM-supported fact was proposed by a language model. "
    "A possible fact is a useful but insufficient clue. A rejected fact is a "
    "proposal that the user or validator marked as incorrect."
)

#: §8.4, verbatim. The nine names are derived from this sentence rather than retyped.
ALWAYS_LOCAL_SENTENCE = (
    "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, "
    "user edits, group memberships, and raw sensitive values should remain local."
)

#: §8.4, verbatim. The five facets are derived from this sentence.
DISPLAY_SENTENCE = (
    "The user can choose whether names, previews, thumbnails, OCR text, or "
    "location data are shown."
)

#: §8.4's compact dossier, verbatim. Five kinds; `filename` is not among them.
DOSSIER_SENTENCE = (
    "selected excerpts, redacted identifiers, candidate labels, non-sensitive "
    "metadata, and evidence references"
)


def _identifiers(listed: str) -> tuple[str, ...]:
    """Split a design list into P7's snake_case identifiers, mechanically."""
    out = []
    for part in listed.split(","):
        word = part.strip().removeprefix("and ").removeprefix("or ")
        out.append(word.lower().replace(" ", "_"))
    return tuple(out)


def _states(prose: str) -> tuple[str, ...]:
    """Pull `A <name> fact` / `An <name> fact` out of line 50, in order."""
    return tuple(
        match.group(1).strip().lower().replace("-", "_").replace(" ", "_")
        for match in re.finditer(r"\b(?:A|An) ((?:[\w-]+ )+?)fact\b", prose)
    )


# --- the five handling classes -----------------------------------------------

def test_the_five_classes_are_the_designs_five_in_the_designs_order():
    assert HANDLING_CLASSES == (
        "public_low", "personal_non_sensitive", "sensitive_personal",
        "highly_sensitive_credential_bearing", "unreadable_unclassified",
    )


def test_each_identifier_is_the_designs_own_line():
    # "The system should classify data into handling classes before LLM escalation:"
    # then five lines. Without this mapping the five identifiers are five words a P7
    # author chose; with it they are the design's, spelled in snake_case.
    assert tuple(HANDLING_CLASS_LABELS[name] for name in HANDLING_CLASSES) == (
        "Public or low sensitivity",
        "Personal but non-sensitive",
        "Sensitive personal",
        "Highly sensitive or credential-bearing",
        "Unreadable or unclassified",
    )
    assert tuple(HANDLING_CLASS_LABELS) == HANDLING_CLASSES


def test_no_sixth_class_was_added():
    assert len(HANDLING_CLASSES) == 5
    assert len(set(HANDLING_CLASSES)) == 5


def test_an_out_of_vocabulary_class_is_a_load_error_that_suggests_no_neighbour():
    # "A value outside this set is a load error, not a fallback." A suggestion is how
    # a misspelling becomes a silent downgrade, which is what §8.6 forbids by name.
    with pytest.raises(OutOfVocabulary) as caught:
        check_handling_class("public")
    assert "public_low" not in str(caught.value)
    with pytest.raises(OutOfVocabulary):
        check_handling_class("")
    with pytest.raises(OutOfVocabulary):
        check_handling_class(None)
    assert check_handling_class("unreadable_unclassified") == "unreadable_unclassified"


# --- the four operation modes ------------------------------------------------

def test_the_four_modes_are_the_designs_four_in_order():
    assert OPERATION_MODES == ("offline", "local_model", "hybrid", "cloud_assisted")


def test_mode_semantics_reproduces_8_4s_four_sentences_verbatim():
    # Verbatim so a later paraphrase is a failing test. "Sensitive files remain local"
    # is the whole of what `hybrid` promises; a reworded version could promise less.
    assert MODE_SEMANTICS == {
        "offline":
            "No content leaves the device; only local rules and local models may run.",
        "local_model":
            "Local extraction plus a user-installed local LLM for eligible dossiers.",
        "hybrid":
            "Sensitive files remain local; non-sensitive bounded dossiers may use a "
            "cloud LLM.",
        "cloud_assisted":
            "User explicitly permits selected corpus areas to use a cloud model.",
    }
    assert tuple(MODE_SEMANTICS) == OPERATION_MODES


def test_an_out_of_vocabulary_mode_is_refused():
    with pytest.raises(OutOfVocabulary):
        check_mode("cloud")
    assert check_mode("offline") == "offline"


# --- the always-local nine ---------------------------------------------------

def test_the_nine_always_local_items_are_the_designs_own_words():
    listed = ALWAYS_LOCAL_SENTENCE.split(" should remain local.")[0]
    assert ALWAYS_LOCAL == _identifiers(listed)
    assert len(ALWAYS_LOCAL) == 9


def test_nothing_in_the_always_local_set_is_a_releasable_item_kind():
    # "Nothing in this set can be named as a releasable item kind. The gate has no
    # code path that materialises one." The vocabulary makes it unnameable; Task 7
    # makes it a denial.
    assert set(ALWAYS_LOCAL).isdisjoint(ITEM_KINDS)


def test_paths_are_always_local_and_filename_is_a_separate_string():
    # Open question 2, and the SPEC's flagged reading: directory path is not filename.
    assert "paths" in ALWAYS_LOCAL
    assert "filename" in ITEM_KINDS
    assert "filename" not in ALWAYS_LOCAL


# --- the six releasable item kinds -------------------------------------------

def test_the_six_item_kinds_are_the_specs_six_in_order():
    assert ITEM_KINDS == (
        "excerpt", "redacted_identifier", "candidate_label", "metadata_field",
        "evidence_reference", "filename",
    )


def test_filename_is_the_only_kind_the_designs_own_sentence_does_not_list():
    # §8.4 permits five. P7 singularises each and spells "non-sensitive metadata" as
    # `metadata_field`, because the item carries ONE named field. The sixth kind
    # corresponds to no phrase in that sentence: it is the SPEC's flagged reading of
    # §7.3 versus §7.7, adopted because P8 and P11 cannot build without an answer,
    # and held open as Open question 2 rather than treated as settled.
    from_design = {
        "excerpt": "selected excerpts",
        "redacted_identifier": "redacted identifiers",
        "candidate_label": "candidate labels",
        "metadata_field": "non-sensitive metadata",
        "evidence_reference": "evidence references",
    }
    assert [k for k in ITEM_KINDS if k not in from_design] == ["filename"]
    for phrase in from_design.values():
        assert phrase in DOSSIER_SENTENCE, phrase
    assert "filename" not in DOSSIER_SENTENCE
    assert 2 in OPEN_QUESTIONS


def test_an_out_of_vocabulary_item_kind_is_refused():
    with pytest.raises(OutOfVocabulary):
        check_item_kind("whole_document")
    assert check_item_kind("excerpt") == "excerpt"


# --- the eight denial reasons and the five protected spellings ---------------

def test_the_eight_denial_reasons_are_the_specs_eight_in_order():
    assert DENIAL_REASONS == (
        "protected_cloud_target", "unclassified", "policy_revoked",
        "protected_records_template", "whole_document_requested",
        "dossier_over_budget", "always_local_item", "mode_forbids_target",
    )
    assert check_denial_reason("unclassified") == "unclassified"
    with pytest.raises(OutOfVocabulary):
        check_denial_reason("protected")


def test_the_five_protected_spellings_coexist_and_no_two_are_equal():
    # P3's two are about READING and P7's three are about RELEASE. A file inside a
    # protected container has no `files` row, so the gate cannot be asked about it;
    # a protected file under `hybrid` has one and is denied a cloud target.
    spellings = (
        "protected",                     # P7's flag on ClassificationRecord (Task 3)
        "protected_cloud_target",        # P7's denial reason
        "protected_records_template",    # P7's denial reason (§7.3)
        LABEL_UNTOUCHED_PROTECTED,       # P3: "untouched_protected"
        REASON_PROTECTED_CONTAINER,      # P3: "protected_container"
    )
    assert len(set(spellings)) == 5
    assert all("protected" in s for s in spellings)
    assert LABEL_UNTOUCHED_PROTECTED == "untouched_protected"
    assert REASON_PROTECTED_CONTAINER == "protected_container"


def test_no_p7_vocabulary_contains_a_bare_protected():
    for closed in (HANDLING_CLASSES, OPERATION_MODES, ALWAYS_LOCAL, ITEM_KINDS,
                   DENIAL_REASONS, CONSENT_OPTIONS, DISPLAY_FACETS,
                   CLASSIFICATION_BASES, AUDIT_OUTCOMES, RELIABILITY_STATES,
                   REDACTION_VALUES):
        assert "protected" not in closed


def test_p7s_vocabulary_module_holds_none_of_p3s_strings():
    # The test imports P3 to pin the distinction; `src/privacy/` imports neither
    # constant and holds no copy of either literal.
    p3 = {LABEL_UNTOUCHED_PROTECTED, REASON_PROTECTED_CONTAINER, "protected container"}

    def strings_in(value):
        if isinstance(value, str):
            return {value}
        if isinstance(value, tuple):
            return {v for v in value if isinstance(v, str)}
        if isinstance(value, Mapping):
            return {v for v in value.values() if isinstance(v, str)}
        return set()

    for name, value in vars(vocabulary).items():
        if name.startswith("_"):
            continue
        assert not strings_in(value) & p3, name


# --- consent options, display facets, bases, outcomes ------------------------

def test_the_four_consent_options_are_8_4s_own_four():
    # "the user should see that requirement and choose whether to allow a local
    # model, a cloud model, a redacted prompt, or no model use" -- those four,
    # exactly, and in that order.
    assert CONSENT_OPTIONS == (
        "local_model", "cloud_model", "redacted_prompt", "no_model_use")


def test_local_model_is_both_a_mode_and_a_consent_option_and_that_is_not_a_bug():
    # §8.4 names it in both lists. Open question 6 asks whether a local call is a
    # consent event or only an audit event; the shared string is where that question
    # touches the code, and nothing here answers it.
    assert "local_model" in OPERATION_MODES
    assert "local_model" in CONSENT_OPTIONS
    assert 6 in OPEN_QUESTIONS


def test_the_five_display_facets_are_the_designs_own_words():
    listed = DISPLAY_SENTENCE.split("whether ")[1].split(" are shown.")[0]
    assert DISPLAY_FACETS == _identifiers(listed)
    assert DISPLAY_FACETS == (
        "names", "previews", "thumbnails", "ocr_text", "location_data")


def test_three_classification_bases_and_three_audit_outcomes():
    assert CLASSIFICATION_BASES == ("detector", "safety_domain", "user")
    assert AUDIT_OUTCOMES == ("released", "denied", "consent_requested")


def test_the_one_basis_p7_writes_has_a_named_constant():
    # Brief §11: never a bare string, never an index. `basis="user"` was written as a
    # literal in five sections before this constant existed.
    assert USER == "user"
    assert USER in CLASSIFICATION_BASES


# --- the six reliability states, imported from P4 and not retyped ------------

def test_the_six_states_are_p4s_tuple_and_not_a_second_copy():
    # Re-exported, not copied. `is` and not `==`: a second tuple with the same six
    # strings would pass equality and would be exactly the second home the rule
    # exists to prevent. D7 makes P7's Contract-in from P6 empty, so this is P4's
    # tuple -- `privacy` already binds `evidence_shape` -- and never P6's.
    assert RELIABILITY_STATES is p4_vocabulary.RELIABILITY_STATES


def test_the_states_are_the_designs_line_50_in_the_designs_order():
    # The order is the ranking Task 4 reads (§3.13), so it is derived from the
    # design's own sentence run rather than retyped: "A user confirmed fact ... A
    # direct fact ... A validated fact ... An LLM-supported fact ... A possible fact
    # ... A rejected fact."
    assert RELIABILITY_STATES == _states(RELIABILITY_SENTENCES)
    assert RELIABILITY_STATES == (
        "user_confirmed", "direct", "validated", "llm_supported", "possible",
        "rejected")


def test_the_one_state_p7_writes_has_a_named_constant():
    # Task 16's reclassification is the only classification P7 originates, and it
    # writes exactly these two values. The other five states are read, never written,
    # so they get membership and no constant.
    assert USER_CONFIRMED == "user_confirmed"
    assert USER_CONFIRMED in RELIABILITY_STATES
    assert RELIABILITY_STATES[0] == USER_CONFIRMED


def test_rejected_is_published_as_the_exclusion_not_a_second_spelling():
    # Task 4's store keeps rejected rows and never treats them as current. The
    # literal used to live in classification_store; that was a second home.
    assert REJECTED == "rejected"
    assert REJECTED in RELIABILITY_STATES
    assert REJECTED == RELIABILITY_STATES[-1]


def test_p7_publishes_no_second_spelling_of_a_state():
    # The failure this whole section exists to prevent: a module-level string in
    # `privacy.vocabulary` whose value happens to be one of P4's six, bound under a
    # name that is not a published constant.
    allowed = {"USER_CONFIRMED": USER_CONFIRMED, "REJECTED": REJECTED}
    for name, value in vars(vocabulary).items():
        if name.startswith("_") or not isinstance(value, str):
            continue
        if value in RELIABILITY_STATES:
            assert name in allowed, name
            assert value == allowed[name]


def test_detector_is_the_named_basis_constant():
    assert DETECTOR == "detector"
    assert DETECTOR in CLASSIFICATION_BASES


# --- SPEC §10's two display values, one home ---------------------------------

def test_the_two_display_values_are_spec_10s_two():
    # SPEC §10: `display_settings` is "each shown | redacted". Before this constant
    # existed the pair had three homes and three names -- `REDACTION_VALUES` in
    # `policy.py`, `SETTING_VALUES` in Task 18, `FACET_VALUES` in a third section.
    assert (SHOWN, REDACTED) == ("shown", "redacted")
    assert REDACTION_VALUES == (SHOWN, REDACTED)


def test_a_display_facet_maps_to_one_of_exactly_two_values():
    # The reason the pair belongs beside DISPLAY_FACETS: it is the value vocabulary
    # of that key vocabulary, and a facet list published without one is half a
    # contract. W1's "the more redacting option is the default" is Task 6's rule and
    # no default lives here.
    assert len(REDACTION_VALUES) == 2
    assert set(REDACTION_VALUES).isdisjoint(DISPLAY_FACETS)


def test_unreadable_unclassified_is_a_class_and_unclassified_is_a_denial_reason():
    # D2: "Unreadable or unclassified is a GATE OUTCOME, not a file fact." The class
    # is what `resolve_class` returns to a caller; the denial reason is what the gate
    # says when it has no classification to release against. Two strings, one idea,
    # and neither may be written into `files.sensitivity_state`.
    assert "unreadable_unclassified" in HANDLING_CLASSES
    assert "unclassified" in DENIAL_REASONS
    assert "unclassified" not in HANDLING_CLASSES
    assert "unreadable_unclassified" not in DENIAL_REASONS


# --- the boundary: eleven questions, and no numbers --------------------------

def test_all_eleven_open_questions_are_present_and_unanswered():
    assert set(OPEN_QUESTIONS) == set(range(1, 12))
    for number, question in OPEN_QUESTIONS.items():
        assert isinstance(question, str) and question.strip(), number


def test_the_module_holds_no_number_at_all():
    # "no numeric ceiling, no retention period" -- the SPEC's Deferred table puts
    # "Numeric values for every ceiling" outside this contract, and §8.6 gives none.
    # A number here would be the first invented value in the part.
    for name, value in vars(vocabulary).items():
        if name.startswith("_"):
            continue
        assert not isinstance(value, (int, float)), name


def test_every_vocabulary_is_a_tuple_of_unique_nonempty_strings():
    for closed in (HANDLING_CLASSES, OPERATION_MODES, ALWAYS_LOCAL, ITEM_KINDS,
                   DENIAL_REASONS, CONSENT_OPTIONS, DISPLAY_FACETS,
                   CLASSIFICATION_BASES, AUDIT_OUTCOMES, RELIABILITY_STATES,
                   REDACTION_VALUES):
        assert isinstance(closed, tuple)
        assert len(set(closed)) == len(closed)
        assert all(isinstance(v, str) and v and v == v.strip() for v in closed)


def test_the_mappings_are_read_only_so_a_caller_cannot_add_a_member():
    with pytest.raises(TypeError):
        MODE_SEMANTICS["air_gapped"] = "no"
    with pytest.raises(TypeError):
        HANDLING_CLASS_LABELS["top_secret"] = "no"
    with pytest.raises(TypeError):
        OPEN_QUESTIONS[12] = "no"
