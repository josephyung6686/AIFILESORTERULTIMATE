"""`--label ".."` is a route a person can type, and it stops at the freeze.

**The route is real and was driven end to end.** A run of
`--situation academic.coursework --label ".."` over a three-file corpus writes
`display_label='..'` onto four rows of `tree_nodes` and one of `groups`. The
label reaches a node because `--label` becomes the merged group's
`display_label` (`cli.py`), which becomes a `BranchCandidate.display_label`
(`tree_design/candidates.py`), which becomes a node's -- and
`mutation/resolution.py`:311-319 puts every ancestor's `display_label` through
`resolve_name` and appends the result to the destination directory.

So the question was never whether a `..` could reach path composition. It was
what happened when it did. Under the CLI's own table nothing had an opinion --
`prohibited_characters` is {'/', '\0', ':'} and `reserved_names` is empty -- so
`resolve_name` returned `..` unchanged and the composed destination climbed out
of the corpus.

`resolve_name` now refuses it. This test is about WHERE that refusal lands: on
one held file with a sentence, not as a traceback that ends the freeze over the
whole corpus. `freeze.py`:233 already had the catch; nothing had ever reached it
from this direction.
"""
from __future__ import annotations

import pytest

from apply_run.freeze import NO_SAFE_NAME
from mutation.constraints import FilesystemConstraints
from mutation.names import NameUnresolvable, resolve_name

from .conftest import NODES

#: The composition root's own table, copied here so the test asks the question a
#: real run asks. An empty `reserved_names` is the point.
CLI_TABLE = FilesystemConstraints(
    unicode_form="NFC", case_sensitive=False, max_component_bytes=255,
    max_path_bytes=1024, prohibited_characters=frozenset({"/", "\0", ":"}),
    reserved_names=frozenset(), replacement_character="_")


def test_the_labels_a_person_can_type_that_are_not_names(tmp_path):
    """Every traversal component, under the table a real run uses."""
    for typed in ("..", ".", "...", " .. "):
        with pytest.raises(NameUnresolvable) as refused:
            resolve_name(typed, constraints=CLI_TABLE,
                         directory_byte_length=len(str(tmp_path).encode()),
                         has_extension=False)
        assert "traversal" in str(refused.value)


def test_a_branch_labelled_dot_dot_holds_its_files_and_does_not_end_the_freeze(
        world, ids, clock):
    """The whole corpus still freezes; the escaping branch holds, and is named.

    The standing rule is that nothing is silently omitted. A `..` branch must
    not take the other branches down with it and must not vanish -- the person
    is told, per file, that no safe name could be made.
    """
    import dataclasses

    renamed = tuple(
        dataclasses.replace(node, display_label="..")
        if node.node_id == "n-course" else node
        for node in NODES)

    from apply_run.freeze import freeze

    from .conftest import COLLISION_POLICY, CONSTRAINTS, LEGAL, PROTECTED_CLASSES
    from .test_freeze import _no_approval

    proposal = freeze(
        world.conn, world.decisions, nodes=renamed, legal_destination_ids=LEGAL,
        cross_folder_moves=True, constraints=CONSTRAINTS,
        high_level_folders={"root_documents": world.documents},
        volume_of=lambda path: "vol-main",
        protected_handling_classes=PROTECTED_CLASSES,
        collision_policy=COLLISION_POLICY,
        expiration_state="no expiry configured",
        shown_file_ids=frozenset(world.sources),
        approve_reviewed=_no_approval,
        component_version="apply-test", now=clock, mint_id=ids)

    held_reasons = {item.reason for item in proposal.held}
    assert NO_SAFE_NAME in held_reasons, (
        "the escaping branch must be HELD and named, never dropped")
    for item in proposal.held:
        if item.reason == NO_SAFE_NAME:
            assert "traversal" in item.detail

    # And nothing frozen points outside the corpus.
    for plan in proposal.plans:
        assert ".." not in plan.resolved_destination_path

    # The disk is untouched either way: freeze is a promise, not an action.
    for source in world.sources.values():
        assert source.exists()
