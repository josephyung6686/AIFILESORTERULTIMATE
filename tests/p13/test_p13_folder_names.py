"""The tree a person reads, with P13's folder-name boundary actually applied.

`69` §3 blocker 3 is the case: a client's passport number became a group's
`display_label` and printed as a proposed FOLDER NAME. `review_surface`'s half of
closing that shipped as `redaction_boundary.proposed_folder_name` and was called
by nothing but its own test, so the boundary existed and the defect it names was
still reachable from a typed command.

These tests drive the SEAM -- the thing that answers
`derived_from_protected_material` from real records and turns P13's refusal into
the one string a tree may print. The boundary itself is tested next door in
`test_p13_redaction_boundary.py`; what is tested here is that a live group, a
live classification and a live node reach it.

The provenance answer is exact and is not a string search. `grouping.naming`'s
`label_for` is "the anchor values, deduplicated" -- so a group's label is derived
from protected material exactly when one of the anchor facts THAT COMPOSED IT
stands on a file P7 flagged, and `AnchorFact.file_ids` carries that join with
nothing to infer. A `carries_no_material` scan over the label would have been the
tempting shortcut and would be wrong: it refuses on any shared two-character run,
so "Columbia 2026" beside a protected observation reading "2026-01-01" strips a
person's own folder name off their tree.

**Amended by `94` F1.** "The anchor facts that composed it" used to read "the
anchor facts it holds", which is the same claim only for an ENGINE label -- and
`src/cli.py` accepts one group per `--label`, whose label is the person's own
word under `label_source = user-edited` and whose anchor facts are everything
underneath it. So `Coursework` came back derived from a passport it merely
contained, P12 read that as "this name IS protected material", and every ordinary
file in the folder became unfilable. The value test below is the fix and the last
test in this file is the case.
"""
from __future__ import annotations

import json

from privacy.vocabulary import HANDLING_CLASSES
from tree_design.records import Node

from review_run.structure import (
    ProtectedLabel,
    folder_label,
    protected_label_provenance,
)

#: Spelled here and immediately checked against P7's live tuple, the way
#: `review_surface.progress` spells P4's completeness states: if P7 renames one,
#: this file fails at import rather than testing a class nothing carries.
CREDENTIAL_BEARING = "highly_sensitive_credential_bearing"
PERSONAL = "personal_non_sensitive"
PUBLIC = "public_low"
assert {CREDENTIAL_BEARING, PERSONAL, PUBLIC} <= set(HANDLING_CLASSES)

PASSPORT = "A1234567"
VERSION = "plan-1"


def _node(node_id: str, label: str, *, groups=(), handling=PUBLIC) -> Node:
    return Node(
        node_id=node_id, plan_version_id=VERSION, node_type="proposed",
        display_label=label, parent_node_id=None, root_anchor="root",
        ordinal=0, associated_group_ids=tuple(groups), explanation="fixture",
        node_role="ordinary", accepts_placement=True,
        handling_class=handling, origin_node_id=node_id)


def _group(conn, group_id: str, *, label: str, file_ids: tuple[str, ...]) -> None:
    """One coherent group whose label is its anchor value, as `naming` mints it."""
    conn.execute(
        "INSERT INTO groups (group_id, seed_ref, seed_kind, proposed_basis, "
        "anchor_facts, pre_model_signals, anchor_count, coherence_verdict, "
        "coherence_citations, group_category, display_label, label_source, "
        "conflicts, stop_rule_hits, state, sensitivity_state, created_by, "
        "created_at) VALUES (?, 'seed', 'file', 'basis', ?, '[]', 1, "
        "'coherent', '[]', NULL, ?, 'engine', '[]', '[]', 'supported', "
        "'none', 'fixture', '2026-09-02T00:00:00Z')",
        (group_id,
         json.dumps([{"field": "record_type", "value": label,
                      "file_ids": list(file_ids),
                      "reliability_state": "validated",
                      "observation_key": f"obs-{group_id}"}]),
         label))


def _classify(conn, file_id: str, *, protected: bool, handling: str) -> None:
    conn.execute(
        "INSERT INTO classifications (fact_id, file_id, content_hash, "
        "handling_class, protected, basis, evidence_refs, reliability_state, "
        "observed_at) VALUES (?, ?, 'hash', ?, ?, 'detector', '[]', "
        "'validated', '2026-09-02T00:00:00Z')",
        (f"c-{file_id}", file_id, handling, 1 if protected else 0))


def _accepted_group(conn, group_id: str, *, label: str, anchors) -> None:
    """The group `src/cli.py` accepts for `--label`: the person's word on top.

    `label_source` is `user-edited` and the anchors are every value under it, so
    the label is composed from NONE of them. That pairing is legal in P9's schema
    and is what `94` F1 turned on -- a group's own tests all mint an engine label,
    where the label IS the join, and the two readings agree.
    """
    conn.execute(
        "INSERT INTO groups (group_id, seed_ref, seed_kind, proposed_basis, "
        "anchor_facts, pre_model_signals, anchor_count, coherence_verdict, "
        "coherence_citations, group_category, display_label, label_source, "
        "conflicts, stop_rule_hits, state, sensitivity_state, created_by, "
        "created_at) VALUES (?, 'seed', 'file', 'basis', ?, '[]', 1, "
        "'coherent', '[]', NULL, ?, 'user-edited', '[]', '[]', 'supported', "
        "'none', 'fixture', '2026-09-02T00:00:00Z')",
        (group_id,
         json.dumps([{"field": "subject", "value": value,
                      "file_ids": list(file_ids),
                      "reliability_state": "direct",
                      "observation_key": f"obs-{value}"}
                     for value, file_ids in anchors]),
         label))

def test_a_branch_label_minted_from_a_protected_file_prints_as_an_aggregate(
        p13_conn):
    """The `69` §3 case, end to end, from records to the string on the screen.

    The whole assertion is the returned string. Asserting that it merely differs
    from the passport number would pass for a seam that returned the empty
    string, and a blank line in a tree is the silent omission the standing rule
    forbids as hard as it forbids the leak.
    """
    _group(p13_conn, "g-1", label=PASSPORT, file_ids=("f-1",))
    _classify(p13_conn, "f-1", protected=True, handling=CREDENTIAL_BEARING)

    provenance = protected_label_provenance(p13_conn, group_ids=("g-1",))
    assert provenance == {"g-1": ProtectedLabel(PASSPORT, CREDENTIAL_BEARING)}

    node = _node("n-1", PASSPORT, groups=("g-1",))
    assert folder_label(node, provenance=provenance) == (
        f"1 protected {CREDENTIAL_BEARING}")


def test_the_seam_a_permissive_tree_printer_would_have_used_lets_it_through(
        p13_conn):
    """The twin. The sabotage is the printer this repo shipped: print the label.

    `src/cli.py`'s `draw` prints `node.display_label` and nothing examines it, so
    this is not an invented failure mode -- it is the live one, written out. The
    two assertions are the same node through the two seams, and only one of them
    puts the number on the screen.
    """
    _group(p13_conn, "g-1", label=PASSPORT, file_ids=("f-1",))
    _classify(p13_conn, "f-1", protected=True, handling=CREDENTIAL_BEARING)
    provenance = protected_label_provenance(p13_conn, group_ids=("g-1",))
    node = _node("n-1", PASSPORT, groups=("g-1",))

    def permissive(one: Node) -> str:
        """The sabotage: take the label, ask nothing."""
        return one.display_label

    assert permissive(node) == PASSPORT
    assert PASSPORT not in folder_label(node, provenance=provenance)


def test_a_persons_own_words_survive_even_when_the_folder_holds_protected_files(
        p13_conn):
    """`redaction_boundary`'s own distinction, enforced at the seam that feeds it.

    "Passport Scans" is a perfectly good name for a folder full of protected
    documents. A seam that answered `derived_from_protected_material` from the
    folder's CONTENTS would strip the name off every protected folder a person
    already has -- their own words, taken away because of what is inside. The
    node here carries the credential-bearing handling class and its label is
    still its own, because the label came from no group.
    """
    node = _node("n-1", "Passport Scans", handling=CREDENTIAL_BEARING)
    assert folder_label(node, provenance={}) == "Passport Scans"


def test_a_group_on_an_unprotected_file_is_absent_from_the_provenance(p13_conn):
    """Absence means safe HERE, and it is the only place in this seam it may.

    `protected_label_provenance` returns the groups it found a live protected
    classification for, so a group with none is simply not a key. That is the one
    reading that keeps `folder_label` total over a tree: a node naming a group
    nobody classified prints its label. The refusal lives one level up, in
    `proposed_folder_name`, which takes the answer as a required keyword and has
    no default at all.
    """
    _group(p13_conn, "g-1", label="Coursework", file_ids=("f-1",))
    _classify(p13_conn, "f-1", protected=False, handling=PERSONAL)

    assert protected_label_provenance(p13_conn, group_ids=("g-1",)) == {}
    node = _node("n-1", "Coursework", groups=("g-1",))
    assert folder_label(node, provenance={}) == "Coursework"


def test_a_node_whose_label_is_not_the_groups_is_not_stripped_by_association(
        p13_conn):
    """A template branch that happens to hold a protected group keeps its name.

    P10 copies `candidate.display_label` onto the node, so a node label that came
    FROM a group is equal to that group's label. A node under a template carries
    the template's word -- "Records" -- and the association is about membership,
    not about provenance. Refusing on association alone would blank out the
    template branches of anybody whose corpus contains one protected file, which
    is most people's, and the tree would be unreadable for the wrong reason.
    """
    _group(p13_conn, "g-1", label=PASSPORT, file_ids=("f-1",))
    _classify(p13_conn, "f-1", protected=True, handling=CREDENTIAL_BEARING)
    provenance = protected_label_provenance(p13_conn, group_ids=("g-1",))

    node = _node("n-1", "Records", groups=("g-1",))
    assert folder_label(node, provenance=provenance) == "Records"


def test_a_superseded_protected_classification_does_not_answer_for_the_group(
        p13_conn):
    """P7's flag is read live, so a retracted one stops speaking.

    A classification that has been superseded is the record of a claim that was
    withdrawn, and reading it would keep a person's folder name stripped for as
    long as the row exists -- with nothing on the screen to say why, because the
    aggregate names a class and never a reason. `superseded_by` is the whole
    difference between the two provenances asserted here.
    """
    _group(p13_conn, "g-1", label=PASSPORT, file_ids=("f-1",))
    _classify(p13_conn, "f-1", protected=True, handling=CREDENTIAL_BEARING)
    assert protected_label_provenance(p13_conn, group_ids=("g-1",)) == {
        "g-1": ProtectedLabel(PASSPORT, CREDENTIAL_BEARING)}

    p13_conn.execute(
        "UPDATE classifications SET superseded_by = 'c-later', "
        "supersede_reason = 'the detector was wrong' WHERE fact_id = 'c-f-1'")
    assert protected_label_provenance(p13_conn, group_ids=("g-1",)) == {}


def test_a_persons_own_label_is_not_derived_from_a_passport_it_merely_contains(
        p13_conn):
    """`94` F1's root cause, on P13's side of it.

    `src/cli.py` accepts ONE group per `--label`, so the group carrying the
    person's own word `Coursework` also carries the anchor facts of every file
    under it -- including the passport's. Its label was composed from none of
    them: `label_source` is `user-edited` and the word came off the command line.

    The old join asked whether the group HELD a protected anchor file and
    answered yes, and P12 then refused to compose a path through `Coursework`,
    which is every destination in the tree. The join now asks whether a protected
    anchor fact's VALUE is one of the label's own components.

    Both halves are asserted on one fixture: the same group, the same protected
    file, and the engine-labelled group beside it that IS named after the
    passport and still refuses. A test that only showed `Coursework` surviving
    would pass for a join that had been switched off.
    """
    _accepted_group(p13_conn, "g-label", label="Coursework", anchors=(
        ("PHYS1401", ("f-ordinary",)), (PASSPORT, ("f-passport",))))
    _group(p13_conn, "g-passport", label=PASSPORT, file_ids=("f-passport",))
    _classify(p13_conn, "f-ordinary", protected=False, handling=PERSONAL)
    _classify(p13_conn, "f-passport", protected=True,
              handling=CREDENTIAL_BEARING)

    provenance = protected_label_provenance(
        p13_conn, group_ids=("g-label", "g-passport"))
    assert provenance == {
        "g-passport": ProtectedLabel(PASSPORT, CREDENTIAL_BEARING)}

    branch = _node("n-course", "Coursework", groups=("g-label",))
    assert folder_label(branch, provenance=provenance) == "Coursework"
    named = _node("n-pass", PASSPORT, groups=("g-label", "g-passport"))
    assert folder_label(named, provenance=provenance) == (
        f"1 protected {CREDENTIAL_BEARING}")
