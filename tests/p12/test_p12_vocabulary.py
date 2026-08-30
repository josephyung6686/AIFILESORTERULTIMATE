"""P12's closed vocabularies. One home each, named constant == string value.

The last two tests are the pair Wave C1 names: `66` §10 requires the refusal
messages to be DISTINCT, and distinctness is a property of the whole table rather
than of any one sentence. `_reads_alike` is the guard, and the negative twin runs
it against a deliberately sabotaged table so that "the guard found nothing" is
distinguishable from "the guard cannot find anything"
(`tests/p10/test_p10_no_invention.py:13-16` is the house pattern).
"""
from __future__ import annotations

import pytest

from mutation import vocabulary as v


def test_the_five_staleness_triggers_are_exactly_8_3s_five():
    assert v.STALENESS_TRIGGERS == (
        v.CONTENT_HASH_DIFFERS, v.SOURCE_PATH_CHANGED, v.DESTINATION_CHANGED,
        v.SOURCE_VANISHED, v.PERMISSION_LOST,
    )
    assert v.STALENESS_TRIGGERS == (
        "content_hash_differs", "source_path_changed", "destination_changed",
        "source_vanished", "permission_lost",
    )


def test_the_refusal_classes_are_exactly_the_specs_ten():
    assert v.REFUSAL_CLASSES == (
        "node_not_in_frozen_tree", "node_refuses_placement", "node_path_collision",
        "cross_folder_not_permitted", "review_policy_unsatisfied",
        "protected_without_policy", "source_or_destination_unavailable",
        "symlink_not_followed", "package_bundle_unapproved", "hash_unverifiable",
    )
    assert v.NODE_NOT_IN_FROZEN_TREE == "node_not_in_frozen_tree"
    assert v.HASH_UNVERIFIABLE == "hash_unverifiable"


def test_the_four_collision_behaviours_are_the_four_user_approved_ones():
    assert v.COLLISION_BEHAVIOURS == (
        "preserve_both_deterministic_suffix", "merge_only_if_hashes_identical",
        "retain_newer_older_to_version_family_review", "stop_and_ask",
    )
    assert v.COLLISION_KINDS == ("name_only", "content_hash_match")


def test_execution_modes_results_and_failures():
    assert v.EXECUTION_MODES == ("atomic_rename", "cross_volume_copy_and_delete")
    assert v.RESULT_KINDS == ("applied", "refused", "stale", "paused", "failed")
    assert v.FAILURE_CLASSES == ("v3_hash_mismatch", "v4_destination_unconfirmed")
    assert v.PAUSE_REASONS == ("cloud_sync_conflict", "awaiting_collision_decision")


def test_undo_verdicts_and_directory_reversal_outcomes():
    assert v.UNDO_VERDICTS == (
        "reversed", "conflict:destination_content_changed",
        "conflict:destination_missing_or_moved", "conflict:source_path_occupied",
        "refused:source_or_destination_unavailable",
    )
    assert v.DIRECTORY_REVERSAL_OUTCOMES == (
        "removed", "retained:not_empty", "retained:referenced_by_other_entry",
        "retained:not_created_by_this_entry",
    )


def test_the_remaining_closed_sets():
    assert v.CROSS_FOLDER_VERDICTS == (
        "within_root", "cross_root_permitted", "cross_root_refused")
    assert v.REVIEW_VERDICTS == ("approved", "rejected", "deferred", "refresh_required")
    assert v.NORMALIZATIONS == (
        "unicode_normalization", "case_folding",
        "prohibited_character_substitution", "reserved_name_avoidance",
        "length_truncation",
    )
    assert v.CHECKPOINTS == ("prepare", "pre_apply")
    assert v.JOURNAL_ENTRY_KINDS == ("applied", "reversal")


def test_p12_authors_six_event_types_and_all_six_are_already_reserved():
    from database_agent.events import RESERVED_EVENT_TYPES
    assert v.EVENT_TYPES == (
        "planned move", "executed move", "failed move",
        "filename-collision resolution", "external modification detection", "undo",
    )
    assert set(v.EVENT_TYPES) <= RESERVED_EVENT_TYPES


def test_the_seventh_event_type_refused_move_is_reserved_and_p12s_to_author():
    """`74` §5.2 — P12 authors SEVEN, not six. The seventh was minted on
    2026-08-29 and P12 is its only intended writer."""
    from database_agent.events import RESERVED_EVENT_TYPES
    assert v.REFUSED_MOVE == "refused move"
    assert v.REFUSED_MOVE in RESERVED_EVENT_TYPES
    assert v.AUTHORED_EVENT_TYPES == (*v.EVENT_TYPES, v.REFUSED_MOVE)


def test_check_rejects_a_value_outside_a_closed_set():
    assert v.check("applied", v.RESULT_KINDS, name="result") == "applied"
    with pytest.raises(v.OutOfVocabulary) as excinfo:
        v.check("succeeded", v.RESULT_KINDS, name="result")
    assert "result" in str(excinfo.value)
    assert "succeeded" not in str(excinfo.value)


def test_every_declinable_outcome_has_a_message_and_no_two_are_the_same():
    declinable = (
        *v.REFUSAL_CLASSES,
        *(f"stale:{trigger}" for trigger in v.STALENESS_TRIGGERS),
        *(f"paused:{reason}" for reason in v.PAUSE_REASONS),
        *(f"failed:{cls}" for cls in v.FAILURE_CLASSES),
        *v.UNDO_VERDICTS[1:],
    )
    assert set(v.DECLINE_MESSAGES) == set(declinable)
    assert len(set(v.DECLINE_MESSAGES.values())) == len(v.DECLINE_MESSAGES)


def test_the_five_sentences_66_supplies_verbatim_are_the_ones_used():
    assert v.decline_message("stale:content_hash_differs") == \
        "This file changed after the preview."
    assert v.decline_message(v.PROTECTED_WITHOUT_POLICY) == \
        "This item is protected by your privacy policy."
    assert v.decline_message(v.NODE_NOT_IN_FROZEN_TREE) == "No approved destination fits."


def test_a_message_for_an_unknown_outcome_raises_rather_than_returning_a_generic_one():
    with pytest.raises(v.OutOfVocabulary):
        v.decline_message("something_went_wrong")


# --------------------------------------------------------------------------
# `66` §10 — the distinct-refusal-language table, and the guard over it.
# The pair: the guard against the real table, then the guard against a sabotage
# table whose two entries read alike.
# --------------------------------------------------------------------------


def test_no_two_refusals_share_a_message():
    """`66` §10: *"The product should use distinct refusal messages."*

    Distinct is stronger than unequal. Two sentences that differ only in
    punctuation, capitalization or whitespace read alike to the person at the
    screen, and `66` §10's whole point is that the person can tell the outcomes
    apart. The comparison is therefore over `v.reading_key`, not over the string.
    """
    alike = v.messages_that_read_alike(v.DECLINE_MESSAGES)
    assert alike == (), f"these outcomes read alike to a person: {alike}"
    assert set(v.DECLINE_MESSAGES) == set(v.DECLINABLE_OUTCOMES)


def test_a_table_whose_two_entries_read_alike_is_rejected():
    """The negative twin. A guard tested only against a clean table passes just
    as well when it cannot find anything at all."""
    sabotage = {
        v.NODE_NOT_IN_FROZEN_TREE: "No approved destination fits.",
        # Differs only by its full stop and its capital. A person reading the two
        # lines cannot tell which refusal happened, which is the failure `66` §10
        # names, and equality alone would call these two distinct messages.
        v.NODE_REFUSES_PLACEMENT: "no approved destination fits",
        v.HASH_UNVERIFIABLE: "Something else entirely happened here.",
    }
    alike = v.messages_that_read_alike(sabotage)
    assert alike == ((v.NODE_NOT_IN_FROZEN_TREE, v.NODE_REFUSES_PLACEMENT),)

    identical = {
        v.SYMLINK_NOT_FOLLOWED: "The product left this alone.",
        v.PACKAGE_BUNDLE_UNAPPROVED: "The product left this alone.",
    }
    assert v.messages_that_read_alike(identical) == (
        (v.SYMLINK_NOT_FOLLOWED, v.PACKAGE_BUNDLE_UNAPPROVED),)
