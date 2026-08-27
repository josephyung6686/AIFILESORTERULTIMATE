"""§8.7 -- a rejected destination is not resurfaced, and only at its own scope."""
from __future__ import annotations

import inspect

import pytest

from database_agent import learning as p1_learning
from database_agent.events import CORRECTION_SCOPES

from placement import events as placement_events
from placement import vocabulary as v
from placement.learning import (
    ACCEPT, PROPOSAL_CLASSES, REJECT, ScopeSubjectRequired, basis_key_for,
    record_correction, suppressed_nodes,
)

T0 = "2026-08-27T00:00:00Z"


def _action(conn, *, scope="file", subject_id="f1", node_id="n-course",
            polarity=REJECT, proposal_class=v.PLACEMENT,
            subject_ref="file:f1:h1", basis_key=None):
    """One user action, written through P11's OWN §8.2 writer.

    Calling `append_event` here instead would let this file agree with a shape
    `placement.events` does not produce, which is the whole failure the writer
    exists to prevent.
    """
    return placement_events.review_decision(
        conn, subject_ref=subject_ref, action="change_destination",
        component_version="P11-test", observed_at=T0, user_id="u1",
        correction_scope=scope, correction_subject=subject_id, polarity=polarity,
        proposal_class=proposal_class,
        basis_key=basis_key if basis_key is not None else basis_key_for(
            subject_id=subject_id, node_id=node_id),
        explanation="the user rejected this destination",
        file_id="f1", content_hash="h1")


# --- the live read ---------------------------------------------------------------

def test_the_live_read_takes_only_scope_and_subject():
    # The SPEC sentence reads as though the query is keyed on four things. It is
    # keyed on two, and the other two are columns filtered after the read.
    params = inspect.signature(p1_learning.learning_records).parameters
    assert list(params) == ["conn", "scope", "subject_id"]


def test_the_basis_key_pairs_the_subject_with_the_node_the_spec_pairs():
    # SPEC:753-755 keys the query on `(subject_id, node_id)` -- the SCOPE's
    # subject, not the versioned subject ref. A key carrying the content hash
    # would stop matching the moment the user edited the file, which is exactly
    # the un-deciding §8.7 forbids.
    assert basis_key_for(subject_id="f1", node_id="n-course") == "f1->n-course"


# --- suppression at the scope the user chose ---------------------------------------

def test_a_rejected_destination_is_suppressed_for_that_file(p11_conn):
    _action(p11_conn)
    hits = suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course", "n-course-alt"),
                            scopes=("file",))
    assert [hit.node_id for hit in hits] == ["n-course"]
    assert hits[0].scope == "file"
    assert hits[0].subject_id == "f1"
    assert hits[0].event_id > 0


def test_a_file_scoped_rejection_survives_an_edit_of_that_file(p11_conn):
    # §8.7 is about what the user decided, and editing a file does not un-decide
    # it. The subject is the file id, so a new content hash still matches.
    _action(p11_conn)
    hits = suppressed_nodes(p11_conn, subject_ref="file:f1:h2-after-edit",
                            node_ids=("n-course",), scopes=("file",))
    assert [hit.node_id for hit in hits] == ["n-course"]


def test_one_files_rejection_does_not_teach_the_corpus(p11_conn):
    # §8.7's own governing example: a user saying that ONE transcript belongs in
    # a Columbia packet must not teach the engine that ALL transcripts do.
    _action(p11_conn, scope="file", subject_id="f1")
    assert suppressed_nodes(p11_conn, subject_ref="file:f2:h2",
                            node_ids=("n-course",), scopes=("file",)) == ()


def test_a_corpus_scoped_rejection_applies_everywhere_it_was_scoped_to(p11_conn):
    _action(p11_conn, scope="corpus", subject_id="the-corpus")
    hits = suppressed_nodes(p11_conn, subject_ref="file:f9:h9",
                            node_ids=("n-course",), scopes=("corpus",),
                            corpus_subject_id="the-corpus")
    assert [hit.node_id for hit in hits] == ["n-course"]


def test_a_node_scoped_rejection_is_keyed_on_the_node_itself(p11_conn):
    _action(p11_conn, scope="node", subject_id="n-course")
    hits = suppressed_nodes(p11_conn, subject_ref="file:f9:h9",
                            node_ids=("n-course", "n-other"), scopes=("node",))
    assert [hit.node_id for hit in hits] == ["n-course"]


def test_a_group_scoped_rejection_is_keyed_on_the_group(p11_conn):
    _action(p11_conn, scope="group", subject_id="g1", subject_ref="group:g1")
    hits = suppressed_nodes(p11_conn, subject_ref="group:g1",
                            node_ids=("n-course",), scopes=("group",))
    assert [hit.node_id for hit in hits] == ["n-course"]


def test_a_scope_p11_has_no_subject_for_refuses_rather_than_finding_nothing(p11_conn):
    # `template` and `domain` are two of §8.7's six and P11 cannot know which
    # template or domain a user meant. Returning `()` would report "the user
    # rejected nothing" for a scope that was never queried at all.
    _action(p11_conn, scope="template", subject_id="t1")
    with pytest.raises(ScopeSubjectRequired):
        suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                         node_ids=("n-course",), scopes=("template",))


def test_a_corpus_scope_asked_without_its_subject_refuses(p11_conn):
    with pytest.raises(ScopeSubjectRequired):
        suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                         node_ids=("n-course",), scopes=("corpus",))


def test_a_scope_outside_p1s_six_is_a_load_error(p11_conn):
    # Refused for being outside P1's vocabulary, which is a different fault from
    # being inside it and unaddressable. Sharing one exception type would let the
    # vocabulary check be deleted with this file staying green.
    with pytest.raises(ValueError) as raised:
        suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                         node_ids=("n-course",), scopes=("folder",))
    assert not isinstance(raised.value, ScopeSubjectRequired)


def test_the_file_scope_refuses_a_group_subject_rather_than_reading_its_id(p11_conn):
    # `group:g1` and `file:g1:h1` would both yield "g1" to a naive split, and one
    # user's decision about a group would answer a question about a file.
    _action(p11_conn, scope="file", subject_id="g1", subject_ref="group:g1")
    with pytest.raises(ScopeSubjectRequired):
        suppressed_nodes(p11_conn, subject_ref="group:g1",
                         node_ids=("n-course",), scopes=("file",))


def test_the_group_scope_refuses_a_file_subject(p11_conn):
    _action(p11_conn, scope="group", subject_id="f1:h1")
    with pytest.raises(ScopeSubjectRequired):
        suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                         node_ids=("n-course",), scopes=("group",))


# --- what does NOT suppress --------------------------------------------------------

def test_an_acceptance_suppresses_nothing(p11_conn):
    _action(p11_conn, polarity=ACCEPT)
    assert suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course",), scopes=("file",)) == ()


def test_a_rejection_recorded_against_another_proposal_class_does_not_apply(p11_conn):
    _action(p11_conn, proposal_class="grouping")
    assert suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course",), scopes=("file",)) == ()


def test_a_placement_rejection_does_not_suppress_a_residual_proposal(p11_conn):
    _action(p11_conn, proposal_class=v.PLACEMENT)
    assert suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course",), scopes=("file",),
                            proposal_class=v.RESIDUAL) == ()


def test_a_rejection_of_another_node_leaves_this_one_alone(p11_conn):
    _action(p11_conn, node_id="n-other")
    assert suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course",), scopes=("file",)) == ()


def test_a_reset_lifts_the_suppression_without_deleting_the_record(p11_conn):
    _action(p11_conn)
    p1_learning.reset_preferences(p11_conn, "file", "f1", author="P11-test",
                                  component_version="P11-test", user_id="u1")
    assert suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course",), scopes=("file",)) == ()
    rows = p11_conn.execute(
        "SELECT count(*) AS c FROM events WHERE polarity = 'reject'").fetchone()
    assert rows["c"] == 1


# --- shape ------------------------------------------------------------------------

def test_the_two_proposal_classes_are_the_specs_two():
    assert PROPOSAL_CLASSES == ("placement", "residual")


def test_one_node_suppressed_at_two_scopes_is_reported_once(p11_conn):
    _action(p11_conn, scope="file", subject_id="f1")
    _action(p11_conn, scope="corpus", subject_id="the-corpus")
    hits = suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course",), scopes=("file", "corpus"),
                            corpus_subject_id="the-corpus")
    assert len(hits) == 1


def test_the_hits_come_back_in_the_order_the_candidates_were_offered(p11_conn):
    _action(p11_conn, node_id="n-b")
    _action(p11_conn, node_id="n-a")
    hits = suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-a", "n-b"), scopes=("file",))
    assert [hit.node_id for hit in hits] == ["n-a", "n-b"]


# --- the writer -------------------------------------------------------------------

def test_a_correction_carries_its_scope_and_its_evidence(p11_conn):
    from p11.test_p11_records import _decision

    record_correction(
        p11_conn, decision=_decision(), action="change_destination",
        polarity=REJECT, scope="node", subject_id="n-course",
        basis_key=basis_key_for(subject_id="n-course", node_id="n-course"),
        user_id="u1", component_version="P11-test", observed_at=T0,
        explanation="this belongs under the other term")
    row = p11_conn.execute(
        "SELECT correction_scope, correction_subject, polarity, proposal_class, "
        "basis_key, user_id FROM events ORDER BY event_id DESC LIMIT 1").fetchone()
    assert row["correction_scope"] == "node"
    assert row["correction_subject"] == "n-course"
    assert row["polarity"] == REJECT
    assert row["proposal_class"] == "placement"
    assert row["user_id"] == "u1"
    assert "n-course" in row["basis_key"]


def test_a_correction_p11_wrote_is_a_correction_p11_can_read_back(p11_conn):
    # The one end-to-end property that matters: what `record_correction` writes,
    # `suppressed_nodes` finds. Two halves agreeing about a basis key by
    # inspection is not the same as one round trip.
    from p11.test_p11_records import _decision

    record_correction(
        p11_conn, decision=_decision(), action="change_destination",
        polarity=REJECT, scope="file", subject_id="f1",
        basis_key=basis_key_for(subject_id="f1", node_id="n-course"),
        user_id="u1", component_version="P11-test", observed_at=T0,
        explanation="not this folder")
    hits = suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course",), scopes=("file",))
    assert [hit.node_id for hit in hits] == ["n-course"]


def test_a_polarity_outside_accept_and_reject_is_refused(p11_conn):
    from p11.test_p11_records import _decision

    with pytest.raises(ValueError):
        record_correction(
            p11_conn, decision=_decision(), action="change_destination",
            polarity="maybe", scope="file", subject_id="f1",
            basis_key="f1->n-course", user_id="u1",
            component_version="P11-test", observed_at=T0, explanation="x")


def test_a_proposal_class_outside_p11s_two_is_refused(p11_conn):
    from p11.test_p11_records import _decision

    with pytest.raises(ValueError):
        record_correction(
            p11_conn, decision=_decision(), action="change_destination",
            polarity=REJECT, scope="file", subject_id="f1",
            basis_key="f1->n-course", user_id="u1",
            component_version="P11-test", observed_at=T0, explanation="x",
            proposal_class="grouping")


def test_a_correction_scope_outside_p1s_six_is_refused(p11_conn):
    from p11.test_p11_records import _decision

    with pytest.raises(ValueError):
        record_correction(
            p11_conn, decision=_decision(), action="change_destination",
            polarity=REJECT, scope="folder", subject_id="f1",
            basis_key="f1->n-course", user_id="u1",
            component_version="P11-test", observed_at=T0, explanation="x")


def test_p11_adds_no_second_learning_store(p11_conn):
    # §8.7's records live in P1's `events` and nowhere else. A P11 table would be
    # a second copy with its own reset semantics and its own drift.
    import ast
    from pathlib import Path

    source = (Path(__file__).resolve().parents[2]
              / "src" / "placement" / "learning.py").read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert "CREATE TABLE" not in node.value.upper()
            assert "INSERT INTO" not in node.value.upper()


def test_the_six_scopes_are_p1s_six():
    assert CORRECTION_SCOPES == ("file", "group", "node", "template", "domain",
                                 "corpus")
