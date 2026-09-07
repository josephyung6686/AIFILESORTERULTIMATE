# tests/p9/test_p9_the_cap_cuts_by_content.py
"""`104` R-78. The graph's node cap must not choose by a per-run identifier.

`build_graph` keeps the first `max_graph_nodes` files it reaches and drops the
rest. WHICH files those are is a decision, and it was taken in `_rank`'s order —
`(anchor first, edge_id)`. An `edge_id` is `sha256(group_id, from, to, type,
bridge)` and a `file_id` is a `uuid4` P1 mints when it first indexes a path, so
two runs over one folder from an empty database sort the same neighbourhood into
two unrelated orders and keep two different sets of files. Everything after that
follows: which files anchor the group, what `anchor_count` says, which edges are
stored, and therefore how many edges the corpus has. Measured on a 63-file
synthetic corpus, two runs of identical code over identical bytes gave 574 and 573
edges; the owner's 199 files gave 511 and 510.

Every test here drives the real `build_graph` over the same CONTENT under two
different file-id assignments — which is exactly what two runs from an empty
database are — and asks for the same answer. The two assignments are literals, not
random, so a failure here is deterministic rather than a coin flip somebody
re-runs until it passes: `test_the_two_assignments_really_do_sort_differently`
holds that property, so the guard cannot quietly stop guarding.
"""
from __future__ import annotations

import hashlib

from grouping.config import GroupingLimits
from grouping.graph import anchoring_files, build_graph
from grouping.retrieval import Neighbor, Neighborhood
from grouping.seeds import Seed
from grouping.vocabulary import (
    DUPLICATE, EXISTING_RELATED_FOLDER, SHARED_VALIDATED_FACT,
    STRONGLY_IDENTIFIED_FILE,
)

T0 = "2026-09-07T00:00:00Z"

#: The corpus, as content: twelve neighbours in the order retrieval ranked them,
#: against a cap of five. Content hashes are what a run recomputes identically;
#: file ids are not.
CONTENT = tuple(f"h-{index:02d}" for index in range(12))
CAP = 5

#: Two runs' worth of minted ids for that same content, in the same order. A run
#: has no idea which is which — that is the whole point — and the fixed prefixes
#: make the disagreement below reproducible.
RUN_ONE = tuple(f"7f3a-{index:02d}" for index in range(12))
RUN_TWO = tuple(f"c19b-{index:02d}" for index in range(12))


def _limits(**overrides) -> GroupingLimits:
    values = dict(
        max_retrieved_neighbors=50, max_graph_nodes=CAP,
        max_candidate_members=10, max_dossier_tokens=4000,
        generic_hub_frequency=99, minimum_independent_anchors=1,
        max_excerpt_characters=240)
    values.update(overrides)
    return GroupingLimits(**values)


def _graph(file_ids, *, seed_file_id, anchors_up_to=0, channel=None,
           bridge=None, limits=None):
    """One graph over CONTENT, with `file_ids[i]` naming `CONTENT[i]`."""
    neighborhood = Neighborhood(
        seed=Seed(
            seed_kind=STRONGLY_IDENTIFIED_FILE, file_id=seed_file_id,
            content_hash="h-seed", field_key="subject", value="BUSIB4300",
            reliability_state="validated", observation_key="sha256:seed",
            basis=None),
        neighbors=tuple(
            Neighbor(
                file_id=file_id, content_hash=content,
                channel=channel or SHARED_VALIDATED_FACT,
                anchors=index < anchors_up_to,
                evidence_ref=f"sha256:{content}",
                detail="subject=BUSIB4300", bridge_entity=bridge)
            for index, (file_id, content) in enumerate(zip(file_ids, CONTENT))
        ),
    )
    return build_graph(
        group_id="group-1", neighborhood=neighborhood,
        limits=limits or _limits(), duplicate_or_version=lambda a, b: DUPLICATE,
        created_at=T0)


def _by_content(graph, file_ids) -> tuple[str, ...]:
    """The graph's answer, said in content terms rather than in minted ones."""
    content_of = dict(zip(file_ids, CONTENT))
    return tuple(content_of.get(file_id, "<seed>") for file_id in graph.file_ids)


# --- the property the guard rests on -------------------------------------------


def test_the_two_assignments_really_do_sort_differently_under_the_old_key():
    """The literals above must be a real disagreement, or every test here is inert.

    This is the old `_rank` key, spelled out: `sha256` over the same five fields
    `_edge_id` hashes. If a future edit to `_edge_id` made these two assignments
    agree, the guards below would pass over a pipeline that had gone back to
    choosing by a minted id, and nobody would know.
    """
    def order(file_ids):
        addressed = [
            (hashlib.sha256("\x1f".join(
                ("group-1", "seed", file_id, SHARED_VALIDATED_FACT, "")
            ).encode("utf-8")).hexdigest(), content)
            for file_id, content in zip(file_ids, CONTENT)]
        return tuple(content for _, content in sorted(addressed))

    assert order(RUN_ONE) != order(RUN_TWO), (
        "RUN_ONE and RUN_TWO address the same content into the SAME order, so "
        "nothing in this file can fail the way R-78 failed. Pick other literals.")
    assert set(order(RUN_ONE)[:CAP]) != set(order(RUN_TWO)[:CAP]), (
        "the two orders differ but the first "
        f"{CAP} are the same set, so the cap would keep the same files either "
        "way and the guards below are decorative. Pick other literals.")


# --- the cap keeps the same FILES, whatever they were called this run ----------


def test_the_cap_keeps_the_same_content_under_two_file_id_assignments():
    one = _graph(RUN_ONE, seed_file_id="seed")
    two = _graph(RUN_TWO, seed_file_id="seed")

    assert one.capped and two.capped, (
        "the neighbourhood no longer exceeds the cap, so nothing is being cut "
        "and this test is not exercising the decision it is about")
    assert _by_content(one, RUN_ONE) == _by_content(two, RUN_TWO), (
        "two runs over identical bytes kept different files, because the cap "
        "chose in an order derived from this run's minted file ids (`104` R-78)")
    assert _by_content(one, RUN_ONE) == ("<seed>",) + CONTENT[:CAP - 1], (
        "the cap no longer honours retrieval's own ranking; it keeps whichever "
        "files an address happened to sort first")


def test_the_edges_are_stored_in_the_same_content_order_by_both_runs():
    one = _graph(RUN_ONE, seed_file_id="seed")
    two = _graph(RUN_TWO, seed_file_id="seed")
    content_of_one = dict(zip(RUN_ONE, CONTENT))
    content_of_two = dict(zip(RUN_TWO, CONTENT))

    assert ([content_of_one[edge.to_file_id] for edge in one.edges]
            == [content_of_two[edge.to_file_id] for edge in two.edges]), (
        "the stored row order of one graph's edges is a different permutation "
        "every run, so no two runs can be compared row for row")


def test_the_dropped_files_are_named_in_the_same_content_order():
    one = _graph(RUN_ONE, seed_file_id="seed")
    two = _graph(RUN_TWO, seed_file_id="seed")
    content_of_one = dict(zip(RUN_ONE, CONTENT))
    content_of_two = dict(zip(RUN_TWO, CONTENT))

    def named(graph, content_of):
        return tuple(content_of[line.split(": ", 1)[1]] for line in graph.omissions)

    assert named(one, content_of_one) == named(two, content_of_two), (
        "the run says a different set of files was left out of the graph, and "
        "the dossier prints that list to the person")


def test_the_anchors_are_the_same_files_in_the_same_order():
    """`Group.anchor_facts` stores this list, so its ORDER is a stored row."""
    one = _graph(RUN_ONE, seed_file_id="seed", anchors_up_to=len(CONTENT))
    two = _graph(RUN_TWO, seed_file_id="seed", anchors_up_to=len(CONTENT))
    content_of_one = dict(zip(RUN_ONE, CONTENT), seed="<seed>")
    content_of_two = dict(zip(RUN_TWO, CONTENT), seed="<seed>")

    first = tuple(content_of_one[file_id]
                  for file_id in anchoring_files(one, seed_anchors=True))
    second = tuple(content_of_two[file_id]
                   for file_id in anchoring_files(two, seed_anchors=True))
    assert first == second, (
        "the same group's anchor list is written in a different order every "
        "run, because it was sorted by the per-run file ids")
    assert len(first) == CAP, (
        f"{len(first)} anchors for a graph capped at {CAP} nodes: the count P10 "
        "and P11 read is no longer a count of the files in the graph")


# --- the rule the old key existed for is still kept -----------------------------


def test_anchors_are_still_kept_before_every_other_edge():
    """The half of `_rank` that was a rule, not an address, and stays one."""
    # The anchors are the LAST four of the twelve, so keeping retrieval's order
    # alone would drop every one of them.
    neighborhood = Neighborhood(
        seed=Seed(
            seed_kind=STRONGLY_IDENTIFIED_FILE, file_id="seed",
            content_hash="h-seed", field_key="subject", value="BUSIB4300",
            reliability_state="validated", observation_key="sha256:seed",
            basis=None),
        neighbors=tuple(
            Neighbor(
                file_id=file_id, content_hash=content,
                channel=(SHARED_VALIDATED_FACT if index >= len(CONTENT) - 4
                         else EXISTING_RELATED_FOLDER),
                anchors=index >= len(CONTENT) - 4,
                evidence_ref=f"sha256:{content}", detail="subject=BUSIB4300",
                bridge_entity=None)
            for index, (file_id, content) in enumerate(zip(RUN_ONE, CONTENT))
        ),
    )
    graph = build_graph(
        group_id="group-1", neighborhood=neighborhood, limits=_limits(),
        duplicate_or_version=lambda a, b: DUPLICATE, created_at=T0)

    kept = set(_by_content(graph, RUN_ONE))
    assert set(CONTENT[-4:]) <= kept, (
        "an anchor was dropped to keep an ordinary edge, which leaves a graph "
        f"that reads as connected with its evidence gone; kept {sorted(kept)}")
