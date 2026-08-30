"""Node id -> directory. The tree is addressed by ID, never by a path string.

Amended by `74` §5.1: resolution walks to the NEAREST `existing` ancestor and
composes beneath its real `existing_path`. `root_anchor` is consulted only when no
ancestor on the chain is `existing` -- which is the case F1 leaves open, and only
that case.
"""
from __future__ import annotations

import itertools
import sqlite3
import unicodedata
from pathlib import Path

import pytest

from tree_design.records import Node

from mutation import vocabulary as v
from mutation.constraints import FilesystemConstraints
from mutation.resolution import (
    CyclicAncestorChain, MalformedChain, ResolutionRefused, RootAnchorUnresolved,
    record_resolution, resolution_by_id, resolve_destination,
)

CASE_FOLDING_VOLUME = FilesystemConstraints(
    unicode_form="NFC", case_sensitive=False, max_component_bytes=255,
    max_path_bytes=1024, prohibited_characters=frozenset({":"}),
    reserved_names=frozenset(), replacement_character="_")

CASE_KEEPING_VOLUME = FilesystemConstraints(
    unicode_form="NFC", case_sensitive=True, max_component_bytes=255,
    max_path_bytes=4096, prohibited_characters=frozenset(),
    reserved_names=frozenset(), replacement_character="_")

DOCUMENTS = Path("/Users/fixture/Documents")
DOWNLOADS = Path("/Users/fixture/Downloads")
FOLDERS = {"root_documents": DOCUMENTS, "root_downloads": DOWNLOADS}


def node(node_id, label, parent, *, node_type="proposed", anchor="root_documents",
         existing_path=None, ordinal=0, accepts=True, role="ordinary",
         disposition=None, handling_class="personal_non_sensitive"):
    return Node(
        node_id=node_id, plan_version_id="plan_1", node_type=node_type,
        display_label=label, parent_node_id=parent, root_anchor=anchor,
        ordinal=ordinal, associated_group_ids=(),
        explanation="fixture node", node_role=role, accepts_placement=accepts,
        handling_class=handling_class, origin_node_id=node_id,
        existing_path=existing_path, disposition=disposition)


#: A four-level chain whose SECOND level is `existing` -- the SPEC's own fixture
#: shape (Contract in, "Fixtures P12 publishes").
FOUR_LEVEL = (
    node("n_career", "Career", None),
    node("n_stripe", "Stripe", "n_career", node_type="existing",
         existing_path=str(DOCUMENTS / "Career" / "Stripe")),
    node("n_2026", "2026 Job Search", "n_stripe"),
    node("n_offers", "Offers", "n_2026"),
)

IDS = itertools.count()


def _mint():
    return f"res-{next(IDS)}"


def _volume(path: Path) -> str:
    """A fixture volume oracle. Resolution never stats a real path."""
    return "vol-downloads" if str(path).startswith(str(DOWNLOADS)) else "vol-main"


def _resolve(node_id, nodes=FOUR_LEVEL, *, source=DOCUMENTS / "Inbox" / "a.pdf",
             constraints=CASE_KEEPING_VOLUME, cross_folder_moves=True,
             folders=None):
    return resolve_destination(
        plan_version="plan_1", node_id=node_id, nodes=nodes, source_path=source,
        high_level_folders=FOLDERS if folders is None else folders,
        constraints=constraints,
        cross_folder_moves=cross_folder_moves, volume_of=_volume,
        mint_resolution_id=_mint)


# --------------------------------------------------------------------------
# The pair Wave C3 names.
# --------------------------------------------------------------------------


def test_a_node_resolves_beneath_its_nearest_existing_ancestors_real_path():
    """Done-means 16, as amended by `74` §5.1.

    `Node.existing_path` is the one real, observed path on the chain, and the
    nearest `existing` ancestor short-circuits the composition: its path is used
    verbatim and never recomposed from its `display_label` (§5.10 preserves
    existing folders as they are, and a user alias over one must not silently
    retarget the write). Every level below it is one normalized segment.
    """
    got = _resolve("n_offers")
    assert got.nearest_existing_ancestor == "n_stripe"
    assert got.nearest_existing_path == str(DOCUMENTS / "Career" / "Stripe")
    assert got.resolved_destination_directory == str(
        DOCUMENTS / "Career" / "Stripe" / "2026 Job Search" / "Offers")
    assert [segment.node_id for segment in got.segments_composed] == \
        ["n_2026", "n_offers"]
    # `Career` is an ancestor of the anchor, so its label is never composed --
    # the existing path already contains whatever that folder is really called.
    assert "n_career" not in [segment.node_id for segment in got.segments_composed]
    assert [item[0] for item in got.ancestor_chain] == [
        "n_career", "n_stripe", "n_2026", "n_offers"]


def test_a_chain_with_no_existing_ancestor_and_no_root_anchor_path_refuses_rather_than_composing_one():
    """The negative twin. F1 is real and it is not closed by inventing a rule
    that turns `"root_desktop"` into a path: that would put a filesystem
    destination nobody approved into P12's source, which §5.12 and §6.12 forbid.

    Both halves are asserted, because a guard that refuses everything is as
    useless as one that refuses nothing: the same chain resolves the moment the
    injected landscape carries the anchor.
    """
    all_proposed = (
        node("n_desk", "Side Projects", None, anchor="root_desktop"),
        node("n_2026", "2026", "n_desk", anchor="root_desktop"),
    )
    with pytest.raises(RootAnchorUnresolved) as excinfo:
        _resolve("n_2026", all_proposed)
    assert "root_desktop" in str(excinfo.value)

    desktop = Path("/Users/fixture/Desktop")
    got = _resolve("n_2026", all_proposed,
                   folders={**FOLDERS, "root_desktop": desktop})
    assert got.nearest_existing_ancestor is None
    assert got.resolved_destination_directory == str(
        desktop / "Side Projects" / "2026")


def test_an_existing_ancestor_rescues_a_chain_whose_root_anchor_has_no_path():
    """`74` §5.1's narrowing, stated as a test. On the four corpora `68`
    measured, every adopted branch has an `existing` ancestor because `cli.py`
    adopts the person's own folders as `existing` nodes carrying their real
    paths -- so F1 bites only the all-proposed chain above."""
    unmapped = tuple(
        node(item.node_id, item.display_label, item.parent_node_id,
             node_type=item.node_type, anchor="root_desktop",
             existing_path=item.existing_path)
        for item in FOUR_LEVEL)
    got = _resolve("n_offers", unmapped)
    assert got.root_anchor == "root_desktop"
    assert got.root_anchor_path is None
    assert got.resolved_destination_directory == str(
        DOCUMENTS / "Career" / "Stripe" / "2026 Job Search" / "Offers")


# --------------------------------------------------------------------------
# P12 PLAN Task 3.
# --------------------------------------------------------------------------


def test_every_composed_segment_keeps_its_intended_label_beside_its_safe_form():
    nodes = (*FOUR_LEVEL, node("n_q3", "Q3: Offers", "n_2026"))
    got = _resolve("n_q3", nodes, constraints=CASE_FOLDING_VOLUME)
    last = got.segments_composed[-1]
    assert last.intended_display_label == "Q3: Offers"
    assert last.filesystem_safe_segment == "Q3_ Offers"
    assert v.PROHIBITED_CHARACTER_SUBSTITUTION in last.normalizations_applied
    assert got.resolved_destination_directory.endswith("Q3_ Offers")


def test_an_existing_ancestors_path_is_used_verbatim_not_recomposed():
    relabelled = tuple(
        node("n_stripe", "Stripe Inc (my alias)", "n_career", node_type="existing",
             existing_path=str(DOCUMENTS / "Career" / "Stripe"))
        if item.node_id == "n_stripe" else item
        for item in FOUR_LEVEL)
    got = _resolve("n_offers", relabelled)
    assert "Stripe Inc (my alias)" not in got.resolved_destination_directory
    assert got.resolved_destination_directory.startswith(
        str(DOCUMENTS / "Career" / "Stripe"))


def test_the_same_frozen_node_resolves_to_the_same_directory_on_both_volumes():
    folding = _resolve("n_offers", constraints=CASE_FOLDING_VOLUME)
    keeping = _resolve("n_offers", constraints=CASE_KEEPING_VOLUME)
    assert folding.resolved_destination_directory == \
        keeping.resolved_destination_directory
    assert folding.segments_composed[-1].filesystem_safe_segment == \
        keeping.segments_composed[-1].filesystem_safe_segment


def test_two_sibling_labels_normalizing_to_one_name_are_refused_never_merged():
    nodes = (*FOUR_LEVEL,
             node("n_a", "Offers Q1", "n_2026", ordinal=1),
             node("n_b", "offers q1", "n_2026", ordinal=2))
    with pytest.raises(ResolutionRefused) as excinfo:
        resolve_destination(
            plan_version="plan_1", node_id="n_a", nodes=nodes,
            source_path=DOCUMENTS / "Inbox" / "a.pdf",
            high_level_folders=FOLDERS, constraints=CASE_FOLDING_VOLUME,
            cross_folder_moves=True, volume_of=_volume, mint_resolution_id=_mint)
    refusal = excinfo.value
    assert refusal.refusal_class == v.NODE_PATH_COLLISION
    assert set(refusal.detail["labels"]) == {"Offers Q1", "offers q1"}
    assert refusal.detail["colliding_name"] == "offers q1"
    assert set(refusal.detail["node_ids"]) == {"n_a", "n_b"}


def test_the_same_two_siblings_coexist_on_a_case_keeping_volume():
    nodes = (*FOUR_LEVEL,
             node("n_a", "Offers Q1", "n_2026", ordinal=1),
             node("n_b", "offers q1", "n_2026", ordinal=2))
    got = resolve_destination(
        plan_version="plan_1", node_id="n_b", nodes=nodes,
        source_path=DOCUMENTS / "Inbox" / "a.pdf", high_level_folders=FOLDERS,
        constraints=CASE_KEEPING_VOLUME, cross_folder_moves=True,
        volume_of=_volume, mint_resolution_id=_mint)
    assert got.resolved_destination_directory.endswith("offers q1")


def test_two_siblings_differing_only_by_unicode_form_also_collide():
    composed = unicodedata.normalize("NFC", "Café")
    decomposed = unicodedata.normalize("NFD", "Café")
    nodes = (*FOUR_LEVEL,
             node("n_a", composed, "n_2026", ordinal=1),
             node("n_b", decomposed, "n_2026", ordinal=2))
    assert nodes[-2].display_label != nodes[-1].display_label
    with pytest.raises(ResolutionRefused) as excinfo:
        _resolve("n_a", nodes)
    assert excinfo.value.refusal_class == v.NODE_PATH_COLLISION


def test_a_node_absent_from_the_tree_is_refused():
    with pytest.raises(ResolutionRefused) as excinfo:
        _resolve("n_invented")
    assert excinfo.value.refusal_class == v.NODE_NOT_IN_FROZEN_TREE


def test_a_source_under_the_same_high_level_folder_is_within_root():
    got = _resolve("n_offers", source=DOCUMENTS / "Inbox" / "a.pdf")
    assert got.cross_folder_verdict == v.WITHIN_ROOT


def test_a_source_under_another_folder_is_permitted_when_the_setting_is_on():
    got = _resolve("n_offers", source=DOWNLOADS / "a.pdf", cross_folder_moves=True)
    assert got.cross_folder_verdict == v.CROSS_ROOT_PERMITTED


def test_a_source_under_another_folder_is_refused_when_the_setting_is_off():
    with pytest.raises(ResolutionRefused) as excinfo:
        _resolve("n_offers", source=DOWNLOADS / "a.pdf", cross_folder_moves=False)
    assert excinfo.value.refusal_class == v.CROSS_FOLDER_NOT_PERMITTED
    assert excinfo.value.detail["source_high_level_folder"] == "root_downloads"
    assert excinfo.value.detail["destination_root_anchor"] == "root_documents"


def test_a_source_under_no_named_folder_crosses_one_when_the_setting_is_off():
    """F11 — a READING, not a design sentence. §1.1 says nothing about a source
    under none of the folders the user named; refusing is the declining reading,
    and the opposite one would make the permission bypassable by staging a file
    outside the named landscape."""
    with pytest.raises(ResolutionRefused) as excinfo:
        _resolve("n_offers", source=Path("/tmp/staging/a.pdf"),
                 cross_folder_moves=False)
    assert excinfo.value.refusal_class == v.CROSS_FOLDER_NOT_PERMITTED
    assert excinfo.value.detail["source_high_level_folder"] is None


def test_a_cycle_in_the_parent_links_raises_rather_than_looping():
    cyclic = (node("n_x", "X", "n_y"), node("n_y", "Y", "n_x"))
    with pytest.raises(CyclicAncestorChain):
        _resolve("n_x", cyclic)


def test_an_existing_node_without_a_path_is_malformed_not_refused():
    broken = tuple(
        node("n_stripe", "Stripe", "n_career", node_type="existing")
        if item.node_id == "n_stripe" else item for item in FOUR_LEVEL)
    with pytest.raises(MalformedChain):
        _resolve("n_offers", broken)


def test_directories_that_must_be_created_is_the_composed_chain():
    got = _resolve("n_offers")
    assert got.directories_that_must_be_created == (
        str(DOCUMENTS / "Career" / "Stripe" / "2026 Job Search"),
        str(DOCUMENTS / "Career" / "Stripe" / "2026 Job Search" / "Offers"),
    )


def test_resolution_reads_no_filesystem():
    got = _resolve("n_offers")
    assert not Path(got.resolved_destination_directory).exists()
    assert got.target_volume == "vol-main"


def test_a_resolution_round_trips_through_its_table_and_cannot_be_overwritten(p12_conn):
    got = _resolve("n_offers")
    record_resolution(p12_conn, got, created_at="2026-08-29T00:00:00Z",
                      record_id="rec-1")
    back = resolution_by_id(p12_conn, got.resolution_id)
    assert back == got
    with pytest.raises(sqlite3.IntegrityError):
        p12_conn.execute("UPDATE path_resolutions SET payload = ?", ("{}",))
