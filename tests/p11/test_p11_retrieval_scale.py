"""§6.2's index, asserted as an INDEX rather than as a stopwatch.

`planning/58-SCALE-STRESS.md` §2 measured the defect in milliseconds and its
harness (`tests/integration/test_scale_stress.py`) still owns that measurement.
This file asserts the same thing in units a loaded machine cannot move: how many
statements retrieval issues, and how many destination profiles it deserialises,
as the tree grows four-fold. A wall clock on a shared machine measures the other
agents; a statement count measures the product.

The second half of the file is the guard that matters more than either. A faster
placement that places differently is worse than the slow one it replaced, so
`test_the_narrowed_read_agrees_with_a_full_scan_on_every_shape` re-implements the
ORIGINAL whole-tree loop here, verbatim, and asserts the two produce the same
`Retrieval` -- the same candidates in the same order with the same channels and
the same facts, and the same `conflicts_considered` -- over every shape §6.3 has:
a direct match, a conflicting value, a group-only reach, a curated label, a
semantic neighbour, two facts on one field, a node carrying two values for one
field, and no facts at all. `assess` is then run over both and the scores and
verdicts compared, because `00`:105 is a promise about SPEED and §6.10 is a
promise about ANSWERS, and this change is only allowed to touch the first.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from placement import vocabulary as v
from placement.config import PlacementLimits, SupportPolicy
from placement.index import (
    IndexCountsUnavailable, build_destination_index, entries_for_plan,
    reachable_entries,
)
from placement.records import ConflictConsidered, MatchingFact, Subject
from placement.retrieval import (
    ACCEPTED_GROUP, CURATED_FOLDER, Candidate, DIRECT_FACT,
    NON_DECIDING_CHANNELS, Retrieval, SEMANTIC_NEIGHBOUR, retrieve,
)
from placement.scoring import assess
from placement.store import subject_ref_of
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FREEZE_RECORD, FROZEN_TREE, ExpectedValue, tree_with

LIMITS = PlacementLimits(
    max_retrieved_neighbors=4, max_local_graph_neighborhood=8,
    max_candidate_cluster_size=6, max_residual_files_per_batch=50,
    max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
    max_cost_per_scan=5,
)
POLICY = SupportPolicy(policy_id="scale-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.4, margin_threshold=0.2)
SUBJECT = Subject(kind=v.FILE, file_id="f1", content_hash="h1", group_id=None,
                  member_file_ids=())


def _fact(field="subject", value="PHYS1401", ref="obs-1"):
    return MatchingFact(file_fact_id=f"ff-{field}-{value}", field=field,
                        value=value, reliability=v.DIRECT, evidence_ref=ref)


# --------------------------------------------------------------------------
# 1. Shape: what retrieval costs as the tree grows, in load-immune units.
# --------------------------------------------------------------------------

def _wide_tree(node_count):
    """`node_count` legal course nodes, every one carrying the same field.

    Same shape as the scale harness's tree, and it is the WORST case on purpose:
    every node expects a `subject`, so every node is one §6.3 has an opinion
    about. A tree where most nodes carried some other field would make the
    narrowing look better than it is.
    """
    base = FROZEN_TREE.nodes[0]
    nodes = tuple(
        dataclasses.replace(
            base, node_id=f"n-course-{index}", origin_node_id=f"n-course-{index}",
            display_label=f"COURSE{index:05d}", ordinal=index,
            associated_group_ids=(f"g-course-{index}",), parent_node_id=None,
            expected_values=(ExpectedValue(field="subject",
                                           value=f"COURSE{index:05d}"),))
        for index in range(node_count))
    return tree_with(
        nodes=nodes,
        profiles=tuple(
            dataclasses.replace(
                FROZEN_TREE.profiles[0], node_id=node.node_id,
                display_label=node.display_label,
                expected_values=node.expected_values,
                accepted_group_ids=node.associated_group_ids,
                anchor_excerpts=())
            for node in nodes),
        freeze_record=dataclasses.replace(
            FREEZE_RECORD, node_ids=tuple(n.node_id for n in nodes),
            legal_destination_ids=frozenset(
                n.node_id for n in nodes if n.accepts_placement)))


def _counted_retrieve(conn, node_count, monkeypatch):
    """One retrieval over a `node_count` tree, with statements and payload
    deserialisations counted."""
    import placement.index as index_module

    build_destination_index(conn, _wide_tree(node_count),
                            component_version="scale", observed_at=FIXED_CLOCK)
    loads = {"n": 0}
    real_loads = json.loads

    def counting_loads(payload, *args, **kwargs):
        loads["n"] += 1
        return real_loads(payload, *args, **kwargs)

    monkeypatch.setattr(index_module.json, "loads", counting_loads)
    statements = {"n": 0}
    conn.set_trace_callback(lambda _sql: statements.__setitem__("n",
                                                               statements["n"] + 1))
    try:
        result = retrieve(
            conn, subject=SUBJECT, plan_version="plan-1", limits=LIMITS,
            facts=(_fact(value="COURSE00007"),), group_ids=(),
            curated_folder_labels=(), semantic_neighbours=(),
            component_version="scale", observed_at=FIXED_CLOCK)
    finally:
        conn.set_trace_callback(None)
    return result, statements["n"], loads["n"]


@pytest.mark.parametrize("node_count", [200, 800])
def test_retrieval_deserialises_no_destination_profile_at_all(
        p11_conn, monkeypatch, node_count):
    """`00`:105 -- "the engine retrieves the FEW MOST RELEVANT approved
    destination nodes, rather than searching the entire filesystem".

    Retrieval used to open with `entries_for_plan`, which issued one `SELECT` and
    one `json.loads` per legal node, and then looped over all of them, once per
    subject placed. Nothing a candidate needs lives in that payload: a
    `Candidate` carries a node id, its channels, the subject's own matching facts
    and the overlapping group ids, and the profile is read later, per candidate,
    by `build_node_local_graph`.
    """
    result, _, payloads = _counted_retrieve(p11_conn, node_count, monkeypatch)
    assert payloads == 0
    # And it did the §6.3 work: one direct match, every other course suppressed.
    assert [c.node_id for c in result.candidates] == ["n-course-7"]
    assert sum(c.suppressed_node_count
               for c in result.conflicts) == node_count - 1
    # Counted in full, named up to §8.6's `max_retrieved_neighbors`. Naming all
    # of them would be `node_count - 1` ids on the record of every file in the
    # corpus -- eight million on a 10,000-file disk -- and a sentence that lists
    # every folder the user owns.
    assert sum(len(c.suppressed_node_ids) for c in result.conflicts) == (
        LIMITS.max_retrieved_neighbors)


def test_the_payload_counter_would_notice_a_whole_tree_read(p11_conn, monkeypatch):
    # The negative twin. A counter that never increments would report a clean
    # retrieval over the very code the fix removed, so it is fired here against
    # the whole-tree read that is still on the module and still correct for the
    # callers in `versions.py` that genuinely want every entry.
    import placement.index as index_module

    build_destination_index(p11_conn, _wide_tree(200),
                            component_version="scale", observed_at=FIXED_CLOCK)
    loads = {"n": 0}
    real_loads = json.loads
    monkeypatch.setattr(index_module.json, "loads",
                        lambda payload, *a, **k: (loads.__setitem__("n", loads["n"] + 1),
                                                  real_loads(payload, *a, **k))[1])
    assert len(entries_for_plan(p11_conn, plan_version="plan-1")) == 200
    assert loads["n"] == 200


@pytest.fixture()
def p11_databases(tmp_path):
    """Two independent P11 databases, because the two trees are the same plan
    version and one connection cannot hold both."""
    from database_agent.db import create_schema, open_database
    from eval_harness.store import create_eval_schema
    from facts.fields import create_fields
    from grouping.schema import create_grouping_schema
    from placement.schema import create_placement_schema
    from privacy.schema import create_privacy_schema

    opened = []

    def make(name):
        conn = open_database(tmp_path / f"{name}.sqlite")
        for step in (create_schema, create_eval_schema, create_grouping_schema,
                     create_fields, create_privacy_schema,
                     create_placement_schema):
            step(conn)
        opened.append(conn)
        return conn

    yield make
    for conn in opened:
        conn.close()


def test_retrieval_issues_the_same_statements_at_200_nodes_and_at_800(
        p11_databases, monkeypatch):
    """The count is a constant of the EVIDENCE, not a function of the tree.

    This is the shape assertion `planning/58-SCALE-STRESS.md` §2 measured with a
    stopwatch, in a unit that does not move when the machine is busy. `retrieve`
    reads the index with one query per channel the subject actually uses plus one
    for the field it states, and writes one §8.2 event; a tree four times the
    size changes none of those numbers.
    """
    counts = {}
    results = {}
    for node_count in (200, 800):
        conn = p11_databases(f"tree-{node_count}")
        results[node_count], counts[node_count], _ = _counted_retrieve(
            conn, node_count, monkeypatch)
    assert counts[200] == counts[800], counts
    # The two trees really were different sizes, so the equality above is not
    # equality between two runs over the same tree. The COUNT is what grew:
    # suppression still sees every node it rules out, and the constant statement
    # count above is what says it no longer has to visit them to know.
    assert (results[800].conflicts[0].suppressed_node_count
            == 4 * results[200].conflicts[0].suppressed_node_count + 3)


# --------------------------------------------------------------------------
# 2. Semantics: the narrowed read agrees with the whole-tree read it replaced.
# --------------------------------------------------------------------------

def _retrieve_by_full_scan(conn, *, subject, plan_version, limits, facts,
                           group_ids, curated_folder_labels,
                           semantic_neighbours) -> Retrieval:
    """§6.3 as it was written BEFORE the narrowing: every legal node, every time.

    Kept verbatim, minus the §8.2 append, so it can be compared against the live
    implementation rather than trusted. If the two ever disagree this is the half
    that is right, because it is the half the whole suite was green against.
    """
    from facts.read_surface import is_destination_eligible
    from placement.index import entries_for_plan
    from placement.retrieval import CHANNELS

    entries = entries_for_plan(conn, plan_version=plan_version)
    usable = tuple(fact for fact in facts
                   if is_destination_eligible(conn, field_key=fact.field))
    by_field = {(fact.field, fact.value): fact for fact in usable}
    stated_fields = {fact.field for fact in usable}
    wanted_groups = set(group_ids)
    wanted_labels = {label.casefold() for label in curated_folder_labels}
    semantic = set(semantic_neighbours)

    matched: dict[str, dict] = {}
    conflicts: list[ConflictConsidered] = []
    suppressed_by_value: dict[tuple[str, str], list[str]] = {}

    for entry in entries:
        channels: list[str] = []
        entry_facts: list[MatchingFact] = []
        entry_groups: list[str] = []
        contradicted = False
        for field, value in entry.expected_values:
            fact = by_field.get((field, value))
            if fact is not None:
                channels.append(DIRECT_FACT)
                entry_facts.append(fact)
            elif field in stated_fields:
                contradicted = True
                held = next(f for f in usable if f.field == field)
                suppressed_by_value.setdefault(
                    (field, held.value), []).append(entry.node_id)
        if contradicted:
            continue
        overlap = wanted_groups & set(entry.accepted_group_ids)
        if overlap:
            channels.append(ACCEPTED_GROUP)
            entry_groups.extend(sorted(overlap))
        if entry.display_label.casefold() in wanted_labels:
            channels.append(CURATED_FOLDER)
        if entry.node_id in semantic:
            channels.append(SEMANTIC_NEIGHBOUR)
        if channels:
            matched[entry.node_id] = {
                "channels": tuple(dict.fromkeys(channels)),
                "facts": tuple(entry_facts), "groups": tuple(entry_groups),
            }

    for (field, value), node_ids in sorted(suppressed_by_value.items()):
        held = next(f for f in usable if f.field == field and f.value == value)
        conflicts.append(ConflictConsidered(
            kind=field, conflicting_value=value,
            suppressed_node_ids=tuple(sorted(node_ids)),
            evidence_ref=held.evidence_ref,
        ))

    def _rank(item):
        node_id, body = item
        strength = tuple(
            0 if channel in body["channels"] else 1 for channel in CHANNELS)
        return (strength, node_id)

    ordered = sorted(matched.items(), key=_rank)[:limits.max_retrieved_neighbors]
    candidates = tuple(
        Candidate(node_id=node_id, channels=body["channels"],
                  matching_facts=body["facts"], group_ids=body["groups"])
        for node_id, body in ordered)
    return Retrieval(
        subject_ref=subject_ref_of(subject), plan_version=plan_version,
        candidates=candidates, conflicts=tuple(conflicts),
        semantic_only_node_ids=frozenset(
            candidate.node_id for candidate in candidates
            if set(candidate.channels) <= set(NON_DECIDING_CHANNELS)),
    )


#: Every shape §6.3 distinguishes, as `(name, retrieve kwargs)`.
_SHAPES: tuple[tuple[str, dict], ...] = (
    ("a direct fact that matches one node", {}),
    ("a direct fact that contradicts one node",
     {"facts": (_fact(value="PHYS1402", ref="obs-2"),)}),
    ("a group with no fact at all",
     {"facts": (), "group_ids": ("g-shared",)}),
    ("a group whose node a fact contradicts",
     {"group_ids": ("g-phys1402",)}),
    ("a curated folder label the user typed",
     {"facts": (), "curated_folder_labels": ("shared course materials",)}),
    ("a curated label that names an ignored node",
     {"facts": (), "curated_folder_labels": ("Old Downloads",)}),
    ("a semantic neighbour and nothing else",
     {"facts": (), "semantic_neighbours": ("n-course",)}),
    ("a semantic neighbour that is not a legal node",
     {"facts": (), "semantic_neighbours": ("n-ignored", "n-not-a-node")}),
    ("two facts on one field, one matching each of two nodes",
     {"facts": (_fact(value="PHYS1401"), _fact(value="PHYS1402", ref="obs-2"))}),
    ("a fact on a field no node expects",
     {"facts": (_fact(field="work_type", value="Homework"),)}),
    ("no evidence of any kind",
     {"facts": (), "group_ids": (), "curated_folder_labels": (),
      "semantic_neighbours": ()}),
    ("every channel at once",
     {"facts": (_fact(),), "group_ids": ("g-shared", "g-phys1402"),
      "curated_folder_labels": ("general",), "semantic_neighbours": ("n-general",)}),
)


def _assert_same_decision(actual, expected, name, *, reached):
    """The live `Retrieval` against the whole-tree one, field by field.

    Everything a decision is made of must be IDENTICAL: the candidates, in order,
    with their channels, their matching facts and their group ids, and the
    semantic-only marking. Those are what `assess` scores and what P8 is shown.

    The conflicts differ in ONE stated way and in no other. The whole-tree loop
    named every node the conflicting value ruled out; the live one names the
    nodes a retrieval channel had reached -- `00`:107's Columbia branches, pulled
    at by the essays and ruled out by the Duke fact -- and COUNTS the rest. So
    `kind`, `conflicting_value` and `evidence_ref` are compared for equality, the
    count is compared against the length of the old list (which is the proof that
    nothing stopped being suppressed), and the named ids are compared against the
    reached set (which is the proof that the ones dropped from the list are
    exactly the ones nothing was pulling towards).
    """
    assert actual.candidates == expected.candidates, name
    assert actual.subject_ref == expected.subject_ref, name
    assert actual.plan_version == expected.plan_version, name
    assert actual.semantic_only_node_ids == expected.semantic_only_node_ids, name
    assert len(actual.conflicts) == len(expected.conflicts), name
    limit = LIMITS.max_retrieved_neighbors
    for live, whole in zip(actual.conflicts, expected.conflicts):
        assert live.kind == whole.kind, name
        assert live.conflicting_value == whole.conflicting_value, name
        assert live.evidence_ref == whole.evidence_ref, name
        # Nothing stopped being suppressed.
        assert live.suppressed_node_count == len(whole.suppressed_node_ids), name
        # Nothing was invented, and the list is bounded.
        assert set(live.suppressed_node_ids) <= set(whole.suppressed_node_ids), name
        assert len(live.suppressed_node_ids) <= limit, name
        # The nodes a channel was pulling this file towards are always named --
        # they are the ones the user is about to ask "why not that one?" about.
        assert (reached & set(whole.suppressed_node_ids)
                <= set(live.suppressed_node_ids)), name
        # And on a tree small enough for the whole list to fit, the record is
        # unchanged, node for node and repeat for repeat. This is the half that
        # says the bound is a bound and not a rewrite.
        if len(whole.suppressed_node_ids) <= limit:
            assert live.suppressed_node_ids == whole.suppressed_node_ids, name


def _reached_by_full_scan(conn, *, plan_version, facts, group_ids,
                          curated_folder_labels, semantic_neighbours):
    """Every node a §6.3 channel touches, read the slow way.

    Deliberately NOT `Reachable`: the point of the comparison is that the live
    narrowing agrees with a whole-tree walk, so the reference side walks the whole
    tree. Suppression is not applied here -- a contradicted node is still REACHED,
    and it is the intersection of the two that the record names.
    """
    from facts.read_surface import is_destination_eligible
    from placement.index import entries_for_plan

    usable = tuple(fact for fact in facts
                   if is_destination_eligible(conn, field_key=fact.field))
    pairs = {(fact.field, fact.value) for fact in usable}
    wanted_groups = set(group_ids)
    wanted_labels = {label.casefold() for label in curated_folder_labels}
    semantic = set(semantic_neighbours)
    reached = set()
    for entry in entries_for_plan(conn, plan_version=plan_version):
        if (pairs & set(entry.expected_values)
                or wanted_groups & set(entry.accepted_group_ids)
                or entry.display_label.casefold() in wanted_labels
                or entry.node_id in semantic):
            reached.add(entry.node_id)
    return reached


@pytest.mark.parametrize("name,overrides", _SHAPES, ids=[s[0] for s in _SHAPES])
def test_the_narrowed_read_agrees_with_a_full_scan_on_every_shape(
        p11_conn, name, overrides):
    """Same file -> same candidates, same channels, same facts, same conflicts.

    A faster wrong placement is worse than a slow right one, so the comparison is
    against the code that was replaced rather than against a list of expected
    values somebody wrote down.
    """
    build_destination_index(p11_conn, FROZEN_TREE, component_version="scale",
                            observed_at=FIXED_CLOCK)
    kwargs = dict(subject=SUBJECT, plan_version="plan-1", limits=LIMITS,
                  facts=(_fact(),), group_ids=(), curated_folder_labels=(),
                  semantic_neighbours=())
    kwargs.update(overrides)
    expected = _retrieve_by_full_scan(p11_conn, **kwargs)
    actual = retrieve(p11_conn, component_version="scale",
                      observed_at=FIXED_CLOCK, **kwargs)
    reached = _reached_by_full_scan(
        p11_conn, plan_version="plan-1",
        **{key: kwargs[key] for key in ("facts", "group_ids",
                                        "curated_folder_labels",
                                        "semantic_neighbours")})
    _assert_same_decision(actual, expected, name, reached=reached)


@pytest.mark.parametrize("name,overrides", _SHAPES, ids=[s[0] for s in _SHAPES])
def test_the_two_condition_rule_reaches_the_same_verdict_on_every_shape(
        p11_conn, name, overrides):
    # §6.10 is a promise about ANSWERS and `00`:105 is a promise about SPEED.
    # This change was allowed to touch the second only, so the scores, the
    # verdict, the margin and the abstention reason are compared too -- the
    # retrieval equality above does not by itself say the decision survived.
    build_destination_index(p11_conn, FROZEN_TREE, component_version="scale",
                            observed_at=FIXED_CLOCK)
    kwargs = dict(subject=SUBJECT, plan_version="plan-1", limits=LIMITS,
                  facts=(_fact(),), group_ids=(), curated_folder_labels=(),
                  semantic_neighbours=())
    kwargs.update(overrides)
    expected = assess(_retrieve_by_full_scan(p11_conn, **kwargs), {},
                      policy=POLICY)
    actual = assess(retrieve(p11_conn, component_version="scale",
                             observed_at=FIXED_CLOCK, **kwargs), {},
                    policy=POLICY)
    assert actual.scored == expected.scored, name
    assert actual.two_condition == expected.two_condition, name
    assert actual.abstention_reason == expected.abstention_reason, name
    assert actual.alternatives == expected.alternatives, name
    assert actual.unique_direct_match == expected.unique_direct_match, name


def test_a_node_carrying_two_values_for_one_field_is_suppressed_once_per_value(
        p11_conn):
    """The multiset edge the aggregate read had to preserve.

    §6.3's loop appended the node id inside the per-expected-value iteration, so
    a node stating two values for a field the subject holds a third value for was
    recorded twice. The narrowed read subtracts the MATCHED rows from the field's
    node list rather than the matched NODES, which is what keeps that true.
    """
    base = FROZEN_TREE.nodes[0]
    two_valued = dataclasses.replace(
        base, node_id="n-two-valued", origin_node_id="n-two-valued",
        display_label="Two Values", ordinal=5, associated_group_ids=(),
        expected_values=(ExpectedValue(field="subject", value="PHYS2001"),
                         ExpectedValue(field="subject", value="PHYS2002")))
    nodes = FROZEN_TREE.nodes + (two_valued,)
    tree = tree_with(
        nodes=nodes,
        profiles=FROZEN_TREE.profiles + (dataclasses.replace(
            FROZEN_TREE.profiles[0], node_id=two_valued.node_id,
            display_label=two_valued.display_label,
            expected_values=two_valued.expected_values,
            accepted_group_ids=(), anchor_excerpts=()),),
        freeze_record=dataclasses.replace(
            FREEZE_RECORD, node_ids=tuple(n.node_id for n in nodes),
            legal_destination_ids=frozenset(
                n.node_id for n in nodes if n.accepts_placement)))
    build_destination_index(p11_conn, tree, component_version="scale",
                            observed_at=FIXED_CLOCK)
    kwargs = dict(subject=SUBJECT, plan_version="plan-1", limits=LIMITS,
                  facts=(_fact(),), group_ids=(), curated_folder_labels=(),
                  semantic_neighbours=())
    expected = _retrieve_by_full_scan(p11_conn, **kwargs)
    actual = retrieve(p11_conn, component_version="scale",
                      observed_at=FIXED_CLOCK, **kwargs)
    reached = _reached_by_full_scan(
        p11_conn, plan_version="plan-1",
        **{key: kwargs[key] for key in ("facts", "group_ids",
                                        "curated_folder_labels",
                                        "semantic_neighbours")})
    _assert_same_decision(actual, expected, "two values on one field",
                          reached=reached)
    assert expected.conflicts[0].suppressed_node_ids.count("n-two-valued") == 2
    # The multiset survives in the COUNT, which is where it now lives: the node
    # states two values the subject does not hold, so it is ruled out twice, and
    # a count that de-duplicated it would report one branch ruled out where
    # §6.3's loop ruled out two.
    assert "n-two-valued" not in reached
    assert actual.conflicts[0].suppressed_node_count == len(
        expected.conflicts[0].suppressed_node_ids)

    # And the half of the same edge that must NOT double-count: a node whose
    # second value the subject DOES hold is not suppressed at all.
    both = _retrieve_by_full_scan(
        p11_conn, **{**kwargs,
                     "facts": (_fact(value="PHYS2001"), _fact(value="PHYS2002",
                                                              ref="obs-2"))})
    both_facts = (_fact(value="PHYS2001"), _fact(value="PHYS2002", ref="obs-2"))
    live = retrieve(p11_conn, component_version="scale",
                    observed_at=FIXED_CLOCK,
                    **{**kwargs, "facts": both_facts})
    _assert_same_decision(
        live, both, "both values held",
        reached=_reached_by_full_scan(
            p11_conn, plan_version="plan-1", facts=both_facts, group_ids=(),
            curated_folder_labels=(), semantic_neighbours=()))
    assert "n-two-valued" in {c.node_id for c in live.candidates}


def test_reachable_entries_reads_nothing_when_the_subject_states_nothing(p11_conn):
    # The degenerate narrowing, asserted because it is the one a caller hits on
    # a sparse file: no facts, no groups, no labels, no neighbours means no
    # query has anything to look up, and the answer is empty rather than the
    # whole tree.
    build_destination_index(p11_conn, _wide_tree(50), component_version="scale",
                            observed_at=FIXED_CLOCK)
    reachable = reachable_entries(
        p11_conn, plan_version="plan-1", pairs=frozenset(),
        group_ids=frozenset(), labels=frozenset(), node_ids=frozenset(),
        name_limit=LIMITS.max_retrieved_neighbors)
    assert reachable.candidate_node_ids == ()
    assert reachable.contradicted == {}
    assert reachable.contradicted_node_ids == frozenset()


# --------------------------------------------------------------------------
# 3. The two things that make the narrowing affordable, and their twins.
# --------------------------------------------------------------------------

def test_the_stored_term_counts_equal_a_live_count_of_the_table(p11_conn):
    """`placement_index_term_counts` is a materialised aggregate, which is the
    one shape `schema.py` otherwise refuses -- "a named column that disagreed
    with [the payload] would be unreachable rather than merely wrong".

    It is tolerable only because one function writes it, once, in the same
    transaction as the rows it counts, and because this test says so row for row.
    A suppression count read from a stale aggregate would under-report how many
    destinations were ruled out, which is exactly the silent omission the count
    exists to prevent.
    """
    build_destination_index(p11_conn, _wide_tree(120), component_version="scale",
                            observed_at=FIXED_CLOCK)
    stored = {
        (row["source_field"], row["term_key"]): row["row_count"]
        for row in p11_conn.execute(
            "SELECT source_field, term_key, row_count FROM "
            "placement_index_term_counts WHERE superseded_by IS NULL")
    }
    live = {
        (row["source_field"], row["term_key"]): row["n"]
        for row in p11_conn.execute(
            "SELECT source_field, term_key, COUNT(*) AS n FROM "
            "placement_index_terms WHERE superseded_by IS NULL "
            "GROUP BY source_field, term_key")
    }
    assert stored == live
    # And it really counted something: 120 courses each state one subject value,
    # so the aggregate over `expected_values` is not a table of ones.
    assert stored[("expected_values", "subject")] == 120


def test_a_wrong_stored_count_is_a_wrong_suppression_count(p11_conn):
    """The negative twin of the guard above, and of the count itself.

    An aggregate nothing reads is an aggregate nothing can be wrong about. This
    corrupts one row and watches the number the user would read move, which is
    what says the count is served from the aggregate and not recomputed.
    """
    build_destination_index(p11_conn, _wide_tree(120), component_version="scale",
                            observed_at=FIXED_CLOCK)
    honest = retrieve(
        p11_conn, subject=SUBJECT, plan_version="plan-1", limits=LIMITS,
        facts=(_fact(value="COURSE00007"),), group_ids=(),
        curated_folder_labels=(), semantic_neighbours=(),
        component_version="scale", observed_at=FIXED_CLOCK)
    assert honest.conflicts[0].suppressed_node_count == 119
    p11_conn.execute(
        "UPDATE placement_index_term_counts SET superseded_by = 'gone' "
        "WHERE source_field = 'expected_values' AND term_key = 'subject'")
    # With no aggregate to read, the count would fall back to the names -- and
    # the names are bounded, so the number would collapse from 119 to 4. That
    # collapse is a suppression under-reported by a factor of thirty, so it
    # refuses instead. A ceiling that under-reports is the omission the count
    # exists to prevent.
    with pytest.raises(IndexCountsUnavailable) as raised:
        retrieve(p11_conn, subject=SUBJECT, plan_version="plan-1", limits=LIMITS,
                 facts=(_fact(value="COURSE00007"),), group_ids=(),
                 curated_folder_labels=(), semantic_neighbours=(),
                 component_version="scale", observed_at=FIXED_CLOCK)
    assert "subject" in str(raised.value)


def test_the_index_build_leaves_no_log_for_the_next_writer_to_pay_for(
        p11_databases):
    """`open_database` runs WAL at `synchronous = FULL`, so every §8.2 event
    `retrieve` appends is an `F_FULLFSYNC` -- and until the log is checkpointed,
    that fsync is paid against whatever the index build left in it.

    Measured in FRAMES rather than milliseconds, because a wall clock on a shared
    machine measures the other agents. The frame count after one small write is a
    constant of that write; without the checkpoint it was 619 frames for a
    200-node tree and 935 for an 800-node one, which is the per-file tax the
    stopwatch was reading as "retrieval grew with the tree".
    """
    pending = {}
    for node_count in (200, 800):
        conn = p11_databases(f"wal-{node_count}")
        build_destination_index(conn, _wide_tree(node_count),
                                component_version="scale",
                                observed_at=FIXED_CLOCK)
        conn.execute(
            "INSERT INTO placement_index_term_counts (record_id, plan_version, "
            "source_field, term_key, row_count, created_at) "
            "VALUES (?, 'plan-9', 'expected_values', 'probe', 1, ?)",
            (f"probe-{node_count}", FIXED_CLOCK))
        pending[node_count] = conn.execute(
            "PRAGMA wal_checkpoint(PASSIVE)").fetchone()["log"]
    assert pending[200] == pending[800], pending
    # And the log really is the probe's own frames and not an empty answer from a
    # connection that was never in WAL mode at all.
    assert 0 < pending[800] < 20, pending
