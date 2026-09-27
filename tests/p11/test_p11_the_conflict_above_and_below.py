"""`104` §18.2 gap 16: §6.3's suppression walks the chain and compares canonically.

`00`:107 states the rule this file pins: "Conflicting evidence should actively
suppress nodes... A file with a direct PHYS1401 term fact for Spring 2025 should
not be SENT TO a Spring 2026 node without a clear user-approved reason." Two
things were wrong with the implementation of that sentence and gap 16 names both.

**It asked the wrong nodes.** `reachable_entries` read each reached node's OWN
expected values, and a folder's own values are not what filing a file in it
commits the file to: `Spring2026/Homework` states a work type and says nothing
about a term, so a Spring 2025 file went into it and acquired the Spring 2026 the
folder above it stated. The conflict was one level up and invisible.

**It compared by exact string.** `CS 1006` on a heading and `CS1006` on a folder
were two values, so the folder built for the file's own course was RULED OUT by
the file's own course -- the most misleading possible thing to be wrong about,
because the record says the evidence disagreed when it agreed in another
spelling.

The fix is one canonicaliser, the deployment's, applied to the tree when the
index is built and to the subject's facts when it is read -- never a second
normaliser here and never an alias table.
"""
from __future__ import annotations

from dataclasses import replace

import pytest

from placement import vocabulary as v
from placement.config import PlacementLimits
from placement.index import build_destination_index
from placement.records import MatchingFact, Subject
from placement.retrieval import retrieve
from p11.conftest import FIXED_CLOCK, NO_CANONICAL_RULE
from p11.p10_fixtures import (
    ExpectedValue, FREEZE_RECORD, FROZEN_TREE, _node, _profile, tree_with,
)

LIMITS = PlacementLimits(
    max_retrieved_neighbors=6, max_local_graph_neighborhood=8,
    max_candidate_cluster_size=6, max_residual_files_per_batch=50,
    max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
    max_cost_per_scan=5,
)
SUBJECT = Subject(kind=v.FILE, file_id="f1", content_hash="h1", group_id=None,
                  member_file_ids=())


def _spacing_is_a_spelling(field_key: str, value: str) -> str | None:
    """A canonicaliser standing in for the deployment's, on one rule.

    `cli.normalize_for_model` is the real one and `tests/integration/
    test_one_canonicaliser_answers_both_sides.py` is where the product's own
    wiring is pinned. What THIS file needs is a rule small enough to read: two
    values are one value when they differ only in spacing and case, which is
    exactly the difference `CS 1006` and `CS1006` have. The `None` answer -- the
    deployment holds no rule for this field -- is exercised by the `subject`
    branch being the only one that answers.
    """
    if field_key != "subject":
        return None
    return "".join(value.split()).upper()


def _fact(field: str, value: str, ref: str = "obs-1") -> MatchingFact:
    return MatchingFact(file_fact_id=f"ff-{field}-{value}", field=field,
                        value=value, reliability=v.DIRECT, evidence_ref=ref)


def _tree(nodes):
    """A frozen tree of exactly these nodes, with P10's own profiles over them."""
    return tree_with(
        nodes=tuple(nodes),
        profiles=tuple(_profile(node) for node in nodes),
        freeze_record=replace(
            FREEZE_RECORD, node_ids=tuple(node.node_id for node in nodes),
            legal_destination_ids=frozenset(
                node.node_id for node in nodes if node.accepts_placement)))


#: `00`:107's own example as a tree: a term folder with a work-type folder inside
#: it. The leaf states a work type and NOTHING about the term, which is the whole
#: shape of the defect -- its own values cannot disagree with a term fact.
CHAIN = (
    _node(node_id="n-root", display_label="Coursework", parent_node_id=None,
          ordinal=0, associated_group_ids=(), dimension_role=None,
          dimension=None, expected_values=(),
          refinement_disposition="shallow-by-choice",
          refinement_reason="The top of this branch is flat by design."),
    _node(node_id="n-2025", display_label="Spring2025", parent_node_id="n-root",
          ordinal=1, associated_group_ids=(), dimension_role="period",
          dimension="term",
          expected_values=(ExpectedValue(field="term", value="Spring2025"),)),
    _node(node_id="n-2025-hw", display_label="Homework",
          parent_node_id="n-2025", ordinal=2, associated_group_ids=(),
          dimension_role="kind", dimension="work_type",
          expected_values=(ExpectedValue(field="work_type",
                                         value="homework"),)),
)


def _retrieve(conn, *, tree, facts, canonical=NO_CANONICAL_RULE, **overrides):
    build_destination_index(conn, tree, component_version="P11-test",
                            observed_at=FIXED_CLOCK, canonical=canonical)
    values = dict(subject=SUBJECT, plan_version=tree.plan_version_id,
                  limits=LIMITS, facts=facts, group_ids=(),
                  curated_folder_labels=(), semantic_neighbours=(),
                  canonical=canonical, component_version="P11-test",
                  observed_at=FIXED_CLOCK)
    values.update(overrides)
    return retrieve(conn, **values)


# --- the conflict above ------------------------------------------------------------


def test_a_conflicting_value_one_level_up_rules_the_child_out_and_says_where(
        p11_conn):
    """`00`:107's own sentence, on the node it is actually about.

    The file states `work_type = homework`, which is what `Spring2025/Homework`
    expects, so the leaf is reached on a direct fact. It also states
    `term = Spring2026`, which the leaf says nothing about and its PARENT
    contradicts -- and filing the file in the leaf files it in `Spring2025`,
    which is being "sent to" a term folder the evidence disagrees with.

    Measured: before this the leaf was a candidate with a support score and no
    conflict recorded at all, because the loop only ever read the leaf's own
    expected values.

    The record names WHERE, and that is the half a person cannot work out for
    themselves: told only that `Homework` was ruled out on a term, they would go
    looking for a term on a folder that states none.
    """
    result = _retrieve(p11_conn, tree=_tree(CHAIN),
                       facts=(_fact("work_type", "homework"),
                              _fact("term", "Spring2026", ref="obs-term")))

    assert "n-2025-hw" not in {c.node_id for c in result.candidates}
    by_kind = {conflict.kind: conflict for conflict in result.conflicts}
    assert "term" in by_kind, "the term fact suppressed nothing"
    conflict = by_kind["term"]
    assert conflict.conflicting_value == "Spring2026"
    assert "n-2025-hw" in conflict.suppressed_node_ids
    # The leaf was ruled out BY THE PARENT, and the pair says so.
    assert ("n-2025-hw", "n-2025") in conflict.found_on
    # And the parent is ruled out on its own account, by its own value.
    assert ("n-2025", "n-2025") in conflict.found_on


def test_an_existing_folders_own_files_do_not_rule_out_the_folder_inside_it(
        p11_conn):
    """A pile's loose files are not a claim about the folders inside it.

    The pile expects `work_type = resume` because the files sitting directly
    in it agree. A lecture in a course folder inside that pile states
    `work_type = lecture`, which is what the lecture child expects. Filing
    the lecture there does not file it as a resume, so the pile's value
    rules the pile out and leaves the course and the lecture standing.

    A proposed ancestor is the other case, and the test above this one still
    pins it: Spring 2025 rules out the homework child for a Spring 2026 file,
    because that term was composed for the branch.
    """
    tree = _tree((
        _node(node_id="n-pile", display_label="Inbox", parent_node_id=None,
              ordinal=0, associated_group_ids=(), dimension_role=None,
              dimension=None, node_type="existing",
              existing_path="/Inbox",
              expected_values=(ExpectedValue(field="work_type", value="resume"),),
              refinement_disposition="shallow-by-choice",
              refinement_reason="The top of this branch is flat by design."),
        _node(node_id="n-course", display_label="Course",
              parent_node_id="n-pile", ordinal=1,
              associated_group_ids=("g-course",), dimension_role=None,
              dimension=None, node_type="existing",
              existing_path="/Inbox/Course", expected_values=(),
              refinement_disposition="shallow-by-choice",
              refinement_reason="The folder the person made."),
        _node(node_id="n-lecture", display_label="lecture",
              parent_node_id="n-course", ordinal=2, associated_group_ids=(),
              dimension_role=None, dimension=None,
              expected_values=(ExpectedValue(field="work_type",
                                             value="lecture"),)),
    ))
    result = _retrieve(
        p11_conn, tree=tree, facts=(_fact("work_type", "lecture"),),
        group_ids=("g-course",))
    chosen = {candidate.node_id for candidate in result.candidates}
    ruled_out = {node_id for conflict in result.conflicts
                 for node_id in conflict.suppressed_node_ids}
    assert "n-lecture" in chosen
    assert "n-course" in chosen
    assert "n-lecture" not in ruled_out
    assert "n-course" not in ruled_out


def test_a_conflict_below_a_reached_node_is_named_and_leaves_it_standing(
        p11_conn):
    """Down is what EXPLAINS; only up SUPPRESSES.

    A Spring 2026 file whose course matches `PHYS1401` belongs in `PHYS1401`
    perfectly well, even though a `Spring2025` folder sits inside it: nothing
    about filing a file in a parent files it in that parent's children. So the
    reached node stands.

    It is still named, because "which folder under this one is not for this file"
    is the other half of the answer the person is owed -- and naming it is free:
    the walk that found the conflict above found this one in the same statement.
    """
    tree = _tree((
        CHAIN[0],
        _node(node_id="n-course", display_label="PHYS1401",
              parent_node_id="n-root", ordinal=1, associated_group_ids=(),
              dimension_role="course", dimension="subject",
              expected_values=(ExpectedValue(field="subject",
                                             value="PHYS1401"),)),
        _node(node_id="n-course-2025", display_label="Spring2025",
              parent_node_id="n-course", ordinal=2, associated_group_ids=(),
              dimension_role="period", dimension="term",
              expected_values=(ExpectedValue(field="term",
                                             value="Spring2025"),)),
    ))
    result = _retrieve(p11_conn, tree=tree,
                       facts=(_fact("subject", "PHYS1401"),
                              _fact("term", "Spring2026", ref="obs-term")))

    assert [c.node_id for c in result.candidates] == ["n-course"]
    conflict = next(one for one in result.conflicts if one.kind == "term")
    assert conflict.suppressed_node_ids == ("n-course-2025",)
    assert conflict.found_on == (("n-course-2025", "n-course-2025"),)


def test_the_walk_is_the_only_reason_the_child_is_ruled_out(p11_conn):
    """The control: the same leaf, the same file, no conflicting term.

    Without this the test above could pass because the leaf was never a candidate
    at all -- an assertion about a suppression that never happened.
    """
    result = _retrieve(p11_conn, tree=_tree(CHAIN),
                       facts=(_fact("work_type", "homework"),
                              _fact("term", "Spring2025", ref="obs-term")))

    assert "n-2025-hw" in {c.node_id for c in result.candidates}
    assert not [one for one in result.conflicts if one.kind == "term"]


# --- and the spelling --------------------------------------------------------------


def test_two_spellings_of_one_value_are_one_value(p11_conn):
    """`CS 1006` on a heading and `CS1006` on a folder are one course.

    Both sides go through the SAME callable -- the tree's when the index was
    built, the file's when it is read -- so the folder built for this course is
    the folder this course reaches, whichever way either was written.
    """
    tree = _tree((
        CHAIN[0],
        _node(node_id="n-cs", display_label="CS1006", parent_node_id="n-root",
              ordinal=1, associated_group_ids=(), dimension_role="course",
              dimension="subject",
              expected_values=(ExpectedValue(field="subject",
                                             value="CS1006"),)),
    ))
    result = _retrieve(p11_conn, tree=tree, canonical=_spacing_is_a_spelling,
                       facts=(_fact("subject", "CS 1006"),))

    assert [c.node_id for c in result.candidates] == ["n-cs"]
    assert result.conflicts == ()
    # The candidate carries the fact AS THE FILE STATES IT. The canonical form
    # decides identity; it never rewrites the evidence shown to the person.
    assert [fact.value for fact in result.candidates[0].matching_facts] \
        == ["CS 1006"]


def test_the_same_two_spellings_are_two_values_without_the_canonicaliser(
        p11_conn):
    """The measurement, from the other side: this is what gap 16 cost.

    With a deployment that holds no rule for the field -- which is what every
    field got before the canonicaliser was threaded through -- the folder built
    for this file's own course is RULED OUT by this file's own course.
    """
    tree = _tree((
        CHAIN[0],
        _node(node_id="n-cs", display_label="CS1006", parent_node_id="n-root",
              ordinal=1, associated_group_ids=(), dimension_role="course",
              dimension="subject",
              expected_values=(ExpectedValue(field="subject",
                                             value="CS1006"),)),
    ))
    result = _retrieve(p11_conn, tree=tree, canonical=NO_CANONICAL_RULE,
                       facts=(_fact("subject", "CS 1006"),))

    assert result.candidates == ()
    assert result.conflicts[0].suppressed_node_ids == ("n-cs",)


def test_a_value_that_differs_after_canonicalisation_is_a_conflict(p11_conn):
    """And the canonicaliser does not make everything agree.

    `CS 1006` and `CS1007` are two courses under the same rule that makes
    `CS 1006` and `CS1006` one, so the suppression §6.3 asks for still happens.
    A canonicaliser that collapsed real differences would be an alias table, and
    the gap's ruling forbids one in as many words.
    """
    tree = _tree((
        CHAIN[0],
        _node(node_id="n-cs7", display_label="CS1007", parent_node_id="n-root",
              ordinal=1, associated_group_ids=(), dimension_role="course",
              dimension="subject",
              expected_values=(ExpectedValue(field="subject",
                                             value="CS1007"),)),
    ))
    result = _retrieve(p11_conn, tree=tree, canonical=_spacing_is_a_spelling,
                       facts=(_fact("subject", "CS 1006"),))

    assert result.candidates == ()
    conflict = result.conflicts[0]
    assert conflict.kind == "subject"
    # What the FILE says, in the file's own spelling.
    assert conflict.conflicting_value == "CS 1006"
    assert conflict.found_on == (("n-cs7", "n-cs7"),)


def test_the_index_keeps_the_persons_spelling_for_the_screen(p11_conn):
    """Identity is canonicalised; the folder's own words are not.

    `node_profile` describes a candidate to the model out of `expected_values`,
    and the review surface prints them. A canonical form there would put the
    engine's spelling of the person's folder in front of the person.
    """
    from placement.index import entry_for

    tree = _tree((
        CHAIN[0],
        _node(node_id="n-cs", display_label="CS 1006", parent_node_id="n-root",
              ordinal=1, associated_group_ids=(), dimension_role="course",
              dimension="subject",
              expected_values=(ExpectedValue(field="subject",
                                             value="CS 1006"),)),
    ))
    build_destination_index(p11_conn, tree, component_version="P11-test",
                            observed_at=FIXED_CLOCK,
                            canonical=_spacing_is_a_spelling)
    entry = entry_for(p11_conn, plan_version=tree.plan_version_id,
                      node_id="n-cs")
    assert entry.expected_values == (("subject", "CS 1006"),)


def test_a_value_the_canonicaliser_declines_is_kept_as_written(p11_conn):
    """`None` means "this deployment holds no rule", not "drop the value".

    `normalize_for_model` answers `None` for a value no pattern claims, and
    `00`:298 makes such a value a PROPOSAL rather than a rejection. Dropping it
    from the index would make a folder unreachable and unsuppressible at once;
    inventing a form for it would be P11 authoring the rule it just declined to
    hold. So the value is compared exactly as it was written, which is what §6.3
    did for every field before the canonicaliser existed.
    """
    result = _retrieve(p11_conn, tree=_tree(CHAIN),
                       canonical=_spacing_is_a_spelling,
                       facts=(_fact("work_type", "homework"),))

    assert "n-2025-hw" in {c.node_id for c in result.candidates}


# --- and the count the suppression is still allowed to make -------------------------


def test_the_count_is_never_smaller_than_the_names_the_walk_added(p11_conn):
    """`ConflictConsidered`'s own invariant, over a list the walk lengthened.

    A node ruled out by its ANCESTOR states nothing for the field itself, so it
    is named without a term row of its own to count. The record refuses a count
    below its own list, and the retrieval has to keep that true rather than
    letting the walk produce a record that cannot be built.
    """
    result = _retrieve(p11_conn, tree=_tree(CHAIN),
                       facts=(_fact("work_type", "homework"),
                              _fact("term", "Spring2026", ref="obs-term")))

    for conflict in result.conflicts:
        assert conflict.suppressed_node_count >= len(
            conflict.suppressed_node_ids)


def test_a_reason_for_a_node_the_conflict_does_not_claim_is_refused():
    """The record's own guard on the new field.

    `found_on` is a reason for a loss, so a reason about a node the conflict does
    not say it suppressed is a sentence about a folder nobody was shown. It is
    refused at construction rather than printed.
    """
    from placement.records import ConflictConsidered, MalformedPlacementRecord

    with pytest.raises(MalformedPlacementRecord):
        ConflictConsidered(kind="term", conflicting_value="Spring2026",
                           suppressed_node_ids=("n-a",), evidence_ref="obs-1",
                           found_on=(("n-b", "n-parent"),))


def test_a_conflict_built_from_a_list_alone_still_builds(p11_conn):
    """The default is a truthful record, not a missing one.

    Every caller that built a conflict before this field existed said nothing
    about where a value was found, and none of them was lying: the value was on
    the node. An empty `found_on` is that silence, and it is legal.
    """
    from placement.records import ConflictConsidered

    conflict = ConflictConsidered(kind="term", conflicting_value="Spring2026",
                                  suppressed_node_ids=("n-a",),
                                  evidence_ref="obs-1")
    assert conflict.found_on == ()
    assert conflict.suppressed_node_count == 1


def test_the_walk_reads_nothing_when_the_subject_states_nothing(p11_conn):
    """No stated field, no conflict, and therefore no walk.

    The chain is walked to answer a question about the subject's own values. A
    file that states none has no question, and the reads that would answer it are
    reads of somebody else's tree.
    """
    import placement.index as index_module

    build_destination_index(p11_conn, _tree(CHAIN),
                            component_version="P11-test",
                            observed_at=FIXED_CLOCK, canonical=NO_CANONICAL_RULE)
    walked = {"n": 0}
    real = index_module._chain_around

    def counting(*args, **kwargs):
        walked["n"] += 1
        return real(*args, **kwargs)

    index_module._chain_around = counting
    try:
        result = retrieve(
            p11_conn, subject=SUBJECT, plan_version=FROZEN_TREE.plan_version_id,
            limits=LIMITS, facts=(), group_ids=(), curated_folder_labels=(),
            semantic_neighbours=("n-2025-hw",), canonical=NO_CANONICAL_RULE,
            component_version="P11-test", observed_at=FIXED_CLOCK)
    finally:
        index_module._chain_around = real

    assert walked["n"] == 0
    assert result.conflicts == ()
