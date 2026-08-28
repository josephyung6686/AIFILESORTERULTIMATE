"""`64` — the user's own edits, and what a library upgrade may do to them.

The failure this file exists to prevent, in the owner's words: a person renames
*Course* to *Class* because that is what they call it, edits one unrelated
folder, and routing re-derives the label from the catalogue. The level is called
*Course* again, and nothing recorded that they had ever said otherwise.

**The principle is `64` §2 and it decides every case below: the catalogue is a
proposal, the user's edits are facts.** A proposal may be re-derived at any time;
a fact may not be overwritten by re-derivation. P7 already carries exactly this
precedence — `privacy.vocabulary.USER` is "the one basis P7 itself writes" and a
record on that basis outranks an inferred one of any reliability — so the overlay
reuses that basis rather than inventing a second word for it.

**The key is `64` §3 and it is the load-bearing choice.** `node_id` fails (§8.8
mints a new one per plan version, which is exactly the bug the seam pass found in
`learned_preferences_still_applicable`). `template_id@version` fails (it is the
packaging, and packaging is what an upgrade changes). `(schema, role_ref,
field_ref)` holds, because it is the VOCABULARY: "whatever level shows my
`subject` field in an `academic` context, I call it Class" stays true across a
re-route, a re-version and a library upgrade.

**Every guard here has its negative twin, deliberately.** An overlay that wins
everywhere has stopped being an overlay, so beside every "the rename survived"
there is a "the level the user never touched still takes the catalogue's label";
beside "an upgrade cannot revert a rename" there is "what the upgraded library
proposed is still recorded"; and beside "the frozen tree names its release" there
is "two different libraries produce different ids".
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from evidence_shape.schema import create_evidence_schema
from grouping.schema import create_grouping_schema
from tree_design.catalogue import load_catalogue
from tree_design.freeze import ReleaseNotRecorded, catalogue_release, frozen_tree
from tree_design.routing import evaluate_composition, route_branch
from tree_design.schema import create_tree_schema
from tree_design.templates import CompositionConflict, MalformedTemplateRecord
from tree_design.user_edits import (
    UserEditRefused,
    UserLevelEdit,
    record_user_level_edit,
    user_level_edits,
)
from tree_design.vocabulary import (
    ACTION_RENAMED,
    ACTION_SELECTED,
    C4,
    DIFF_REMOVED,
    DIFF_RENAMED,
    DIFF_RETEMPLATED,
    ACTION_REORDERED,
)

from p10.seam_corpus import (
    ORDINARY_CLASS, PLAN_0, PROTECTED_CLASS, ROOT_ANCHOR, SCHEMA,
    seed_seam_corpus, two_dimension_catalogue, two_dimension_manifest,
)
from p10.test_p10_pipeline import authorities, decisions, limits  # noqa: F401
from p10.test_p10_routing import (
    ALWAYS, KIND, RANK, SUBJECT, _catalogue, _context, _definition, _group, _row,
)

T0 = "2026-08-29T00:00:00Z"


# --------------------------------------------------------------------------
# Fixtures: one recipe, two levels, and one edit that names only vocabulary.
# --------------------------------------------------------------------------

def _two_level_catalogue(schema=SCHEMA, subject_label="Course",
                         kind_label="Assignment type"):
    from tree_design.templates import FragmentRef

    definition = _definition(
        "coursework", (FragmentRef("subject", 1), FragmentRef("artifact-kind", 1)),
        ("subject", "artifact_kind"))
    row = _row("a.coursework", "coursework", schema,
               (("subject", "subject", subject_label),
                ("artifact_kind", "work_type", kind_label)))
    return _catalogue((SUBJECT, KIND), (definition,), (row,))


def _rename(display_label="Class", *, schema=SCHEMA, role_ref="subject",
            field_ref="subject", proposed_label="Course"):
    return UserLevelEdit(
        uses_schema=schema, role_ref=role_ref, field_ref=field_ref,
        action=ACTION_RENAMED, display_label=display_label,
        proposed_label=proposed_label, user_id="jy", recorded_at=T0)


def _evaluate(conn, catalogue, *, edits=(), schema=SCHEMA):
    rows = catalogue.rows_for_schema(schema)
    context = _context((schema,), (_group("g1", schema, ("f1",)),))
    return evaluate_composition(
        conn, catalogue, context, rows, privacy_rank=RANK,
        satisfies_purpose_profile=ALWAYS, user_edits=edits)


def _by_role(candidate):
    return {d.role_ref: d for d in candidate.resolved_dimensions}


# --------------------------------------------------------------------------
# The record and its store. The key is the vocabulary, never the packaging.
# --------------------------------------------------------------------------

def test_an_edit_is_recorded_on_the_users_basis_and_not_on_an_inferred_one():
    """`64` §2, reusing P7's word rather than inventing a parallel one."""
    from privacy.vocabulary import CLASSIFICATION_BASES, USER

    edit = _rename()
    assert edit.basis == USER
    assert edit.basis in CLASSIFICATION_BASES


def test_the_key_is_the_schema_the_role_and_the_field_and_nothing_else():
    edit = _rename()
    assert edit.key() == (SCHEMA, "subject", "subject")
    # `64` §3: the two keys that FAIL are not on the record at all, so no later
    # reader can quietly start filtering on one.
    for absent in ("node_id", "plan_version_id", "template_id",
                   "template_version", "binding_id"):
        assert not hasattr(edit, absent), absent


def test_one_key_holds_one_answer_and_the_newest_wins(conn):
    create_tree_schema(conn)
    record_user_level_edit(conn, _rename("Class"))
    record_user_level_edit(conn, _rename("Module"))

    stored = user_level_edits(conn)
    assert len(stored) == 1
    assert stored[0].display_label == "Module"


def test_an_edit_for_one_schema_is_not_returned_for_another(conn):
    create_tree_schema(conn)
    record_user_level_edit(conn, _rename(schema="academic"))
    record_user_level_edit(conn, _rename("Project", schema="research"))

    assert {e.uses_schema for e in user_level_edits(conn)} == {
        "academic", "research"}
    assert [e.display_label
            for e in user_level_edits(conn, schemas=("research",))] == ["Project"]


def test_a_renamed_level_is_a_display_label_never_a_path_fragment(conn):
    """`templates.py`'s rule, preserved literally at the point of RECORDING.

    `ResolvedDimension` already refuses a label with a separator, but by then the
    edit is in the database and every route raises. The overlay refuses it where
    the user typed it.
    """
    create_tree_schema(conn)
    with pytest.raises(MalformedTemplateRecord):
        record_user_level_edit(conn, _rename("Class/2026"))


def test_an_action_with_no_overlay_writer_is_refused_by_name(conn):
    """`64` §6: ten of the fifteen edit actions still have no writer.

    The record HOLDS them — `action` is checked against `DIMENSION_ACTIONS`, so
    the overlay is shaped to carry a reorder the day one is built — and the
    writer refuses them by name, before anything is stored, exactly as
    `apply_review_action` refuses its twelve. A stored edit nothing can apply is
    a silent no-op that survives every future session.
    """
    create_tree_schema(conn)
    reorder = dataclasses.replace(_rename(), action=ACTION_REORDERED)
    with pytest.raises(UserEditRefused) as refusal:
        record_user_level_edit(conn, reorder)
    assert ACTION_REORDERED in str(refusal.value)
    assert user_level_edits(conn) == ()


# --------------------------------------------------------------------------
# §4 — where the overlay applies, and the pair that says it is an OVERLAY.
# --------------------------------------------------------------------------

def test_a_rename_survives_a_reroute(conn):
    candidate = _evaluate(conn, _two_level_catalogue(), edits=(_rename(),))
    subject = _by_role(candidate)["subject"]

    assert subject.display_label == "Class"
    assert subject.action == ACTION_RENAMED


def test_a_level_the_user_never_touched_still_takes_the_catalogues_label(conn):
    """The negative twin. An overlay that wins everywhere is not an overlay."""
    candidate = _evaluate(conn, _two_level_catalogue(), edits=(_rename(),))
    kind = _by_role(candidate)["artifact_kind"]

    assert kind.display_label == "Assignment type"
    assert kind.action == ACTION_SELECTED


def test_a_rename_changes_the_name_and_nothing_else(conn):
    """`64` §4: the user's edit is the last word about PRESENTATION.

    Not about which field a level resolved to, not about where it nests, and not
    about the tier it was resolved at — a rename that moved any of those would be
    a structural change wearing a label's clothes.
    """
    plain = _by_role(_evaluate(conn, _two_level_catalogue()))["subject"]
    renamed = _by_role(
        _evaluate(conn, _two_level_catalogue(), edits=(_rename(),)))["subject"]

    assert (renamed.field_ref, renamed.order_index, renamed.scope) == (
        plain.field_ref, plain.order_index, plain.scope)


def test_the_overlay_is_per_schema_and_renames_nothing_in_another_context(conn):
    """`64` §3's stated consequence, and the reason the label lives on the row."""
    research = _two_level_catalogue(schema="research", subject_label="Project")
    candidate = _evaluate(conn, research, edits=(_rename(schema="academic"),),
                          schema="research")

    assert _by_role(candidate)["subject"].display_label == "Project"


def test_the_gates_judge_the_recipe_and_not_the_recipe_as_the_user_rewrote_it(conn):
    """`64` §4: compose, GATE, then apply. Never the other way round.

    Two rows name one role two ways, which is C4's refusal. A rename of that very
    role must not make the broken composition look valid — if the overlay ran
    first, the two names would collapse into the user's one and a composition
    that resolves a level two ways would ship.
    """
    from tree_design.templates import FragmentRef

    definition = _definition(
        "coursework", (FragmentRef("subject", 1),), ("subject",))
    student = _row("a.student", "coursework", SCHEMA,
                   (("subject", "subject", "Course"),))
    teacher = _row("a.teacher", "coursework", SCHEMA,
                   (("subject", "subject", "Class group"),))
    catalogue = _catalogue((SUBJECT,), (definition,), (student, teacher))

    with pytest.raises(CompositionConflict) as conflict:
        _evaluate(conn, catalogue, edits=(_rename(),))
    assert conflict.value.gate == C4


# --------------------------------------------------------------------------
# §5c — a structural conflict is SURFACED, not resolved, in §5d's vocabulary.
# --------------------------------------------------------------------------

def test_an_edit_naming_a_level_this_recipe_no_longer_has_is_surfaced(conn):
    """The library removed the level the user renamed. That is a question."""
    candidate = _evaluate(
        conn, _two_level_catalogue(),
        edits=(_rename(role_ref="term", field_ref="term", proposed_label="Term"),))

    assert [u.edit.role_ref for u in candidate.unapplied_user_edits] == ["term"]
    assert candidate.unapplied_user_edits[0].kind == DIFF_REMOVED
    # ...and nothing was invented to satisfy it.
    assert "term" not in _by_role(candidate)


def test_an_edit_whose_role_now_resolves_to_another_field_is_surfaced(conn):
    """`re-templated`, in `diff.py`'s own word (§5d)."""
    moved = _two_level_catalogue()
    candidate = _evaluate(
        conn, moved,
        edits=(_rename(field_ref="course_code", proposed_label="Course"),))

    assert [u.kind for u in candidate.unapplied_user_edits] == [DIFF_RETEMPLATED]


def test_an_edit_belonging_to_another_schema_is_not_reported_as_a_conflict(conn):
    """The negative twin. A `research` rename is not this composition's business,
    and reporting it would make every user's every past edit a standing question
    on every branch they own."""
    candidate = _evaluate(
        conn, _two_level_catalogue(),
        edits=(_rename(schema="research", role_ref="term", field_ref="term"),))

    assert candidate.unapplied_user_edits == ()


def test_the_explanation_uses_diffs_vocabulary_for_the_edit_it_applied(conn):
    candidate = _evaluate(conn, _two_level_catalogue(), edits=(_rename(),))

    assert DIFF_RENAMED in candidate.explanation
    assert "Class" in candidate.explanation
    # The two vocabularies are ONE, which is why "what changed when I updated"
    # and "what changed when I edited" read the same way (§5d).
    assert ACTION_RENAMED == DIFF_RENAMED


def test_two_of_the_users_own_edits_disagreeing_about_one_level_refuse(conn):
    """One question, two answers, no answer — C4's shape applied to the overlay.

    Reachable only when one recipe serves two schemas the branch is both in and
    the user renamed the same field differently in each. Picking one would make
    the shipped name depend on the order the rows were listed in.
    """
    from tree_design.templates import FragmentRef

    definition = _definition(
        "coursework", (FragmentRef("subject", 1),), ("subject",))
    rows = (_row("a.academic", "coursework", "academic",
                 (("subject", "subject", "Course"),)),
            _row("a.research", "coursework", "research",
                 (("subject", "subject", "Course"),)))
    catalogue = _catalogue((SUBJECT,), (definition,), rows)
    context = _context(("academic", "research"),
                       (_group("g1", "academic", ("f1",)),))

    with pytest.raises(UserEditRefused):
        evaluate_composition(
            conn, catalogue, context, rows, privacy_rank=RANK,
            satisfies_purpose_profile=ALWAYS,
            user_edits=(_rename("Class", schema="academic"),
                        _rename("Project", schema="research")))


def test_route_branch_carries_the_edits_through_to_every_candidate(conn):
    catalogue = _two_level_catalogue()
    report = route_branch(
        conn, catalogue,
        _context((SCHEMA,), (_group("g1", SCHEMA, ("f1",)),)),
        limits=None, privacy_rank=RANK, satisfies_purpose_profile=ALWAYS,
        rank_candidates=list, user_edits=(_rename(),))

    assert [d.display_label for d in report.candidates[0].resolved_dimensions
            if d.role_ref == "subject"] == ["Class"]


# --------------------------------------------------------------------------
# The live chain. §5a first, because everything else waits on it.
# --------------------------------------------------------------------------

@pytest.fixture()
def corpus(conn, tmp_path):
    create_evidence_schema(conn)
    create_grouping_schema(conn)
    create_tree_schema(conn)
    return seed_seam_corpus(conn, tmp_path)


def _packaged(**over):
    """The seam recipe through the PACKAGED loader, so `release_id` is DERIVED.

    `production.shipped_catalogue_manifest` digests exactly the bytes it read —
    "a library that changed moves it" — so two libraries that differ by one
    authored label get two ids without any test choosing either.
    """
    from production import shipped_catalogue_manifest

    document = two_dimension_manifest(**over)
    files = {
        "fragments.json": json.dumps({"fragments": document["fragments"]}),
        "definitions.json": json.dumps({"definitions": document["definitions"]}),
        "applicabilities.json": json.dumps(
            {"applicabilities": document["applicabilities"]}),
    }
    return load_catalogue(
        lambda: shipped_catalogue_manifest(lambda name: files.get(name, "{}")))


def _design(corpus, *, catalogue=None, run="a", **over):
    """One whole chain over the seam corpus.

    `run` names the id space. `authorities` mints `n_0`, `plan_0`... from a
    counter that starts fresh on every call, so a test that designs the SAME
    corpus twice — which is what an upgrade is — would collide on the first
    plan version id and never reach the question it was asking.
    """
    from tree_design.pipeline import design_tree

    counter = iter(range(10_000))
    auth = authorities(
        corpus,
        mint_node_id=lambda: f"n{run}_{next(counter)}",
        mint_version_id=lambda: f"plan{run}_{next(counter)}",
        **({"catalogue": catalogue} if catalogue else {}))
    return design_tree(corpus.conn, authorities=auth, decisions=decisions(**over))


def test_a_frozen_tree_names_the_catalogue_release_that_built_it(corpus):
    """§5a. Without it a library upgrade is not merely unhandled — it is
    undetectable, and every other clause of §5 is impossible."""
    result = _design(corpus, catalogue=two_dimension_catalogue())

    assert result.tree.freeze_record.catalogue_release_id == "rel_seam"
    assert catalogue_release(result.tree) == "rel_seam"


def test_two_different_libraries_produce_different_release_ids(corpus, conn,
                                                               tmp_path):
    """The negative twin: an id that never moves records nothing."""
    before = _packaged(subject_label="Course")
    after = _packaged(subject_label="Module")
    assert before.release_id != after.release_id

    result = _design(corpus, catalogue=before)
    assert catalogue_release(result.tree) == before.release_id


def test_a_frozen_tree_names_the_template_versions_it_used(corpus):
    result = _design(corpus, catalogue=two_dimension_catalogue())

    assert result.tree.freeze_record.template_versions == (("t.coursework", 1),)


def test_a_tree_frozen_without_a_release_refuses_to_name_one():
    """A record that cannot answer says so. `None` reported as a release id
    would make one library indistinguishable from another, which is the state
    §5a exists to end."""
    from tree_design.fixtures import frozen_tree_fixture

    tree = frozen_tree_fixture()
    with pytest.raises(ReleaseNotRecorded):
        catalogue_release(tree)


def test_a_rename_survives_the_whole_version_chain(corpus):
    """§8.8 mints a new `node_id` per plan version and this chain runs several.

    The edit names no node and no plan version, so there is nothing for the
    version chain to invalidate — which is the whole reason `64` §3 rejects
    `node_id` as the key.
    """
    record_user_level_edit(corpus.conn, _rename("Class"))
    result = _design(corpus, catalogue=two_dimension_catalogue())

    assert len(result.plan_version_ids) > 1
    explanations = " ".join(node.explanation for node in result.tree.nodes)
    assert "Class" in explanations
    assert "Course" not in explanations


def test_a_level_the_user_never_touched_keeps_its_authored_name_in_the_tree(corpus):
    """The negative twin, through the live chain."""
    record_user_level_edit(corpus.conn, _rename("Class"))
    result = _design(corpus, catalogue=two_dimension_catalogue())

    assert any("Assignment type" in node.explanation
               for node in result.tree.nodes)


def test_an_upgrade_cannot_silently_revert_a_rename(corpus):
    """§5b. The user wins, and this is the failure `64` was written about."""
    record_user_level_edit(corpus.conn, _rename("Class"))
    upgraded = _packaged(subject_label="Module")

    result = _design(corpus, catalogue=upgraded)
    subject = next(d for d in result.branches[0].routing.candidates[0]
                   .resolved_dimensions if d.role_ref == "subject")

    assert subject.display_label == "Class"


def test_what_the_upgraded_library_proposed_is_recorded_not_discarded(corpus):
    """The negative twin. "The user wins" is only half of §5b; a proposal that
    vanished cannot be offered back, and the upgrade could not be explained."""
    record_user_level_edit(corpus.conn, _rename("Class"))
    result = _design(corpus, catalogue=_packaged(subject_label="Module"))
    subject = next(d for d in result.branches[0].routing.candidates[0]
                   .resolved_dimensions if d.role_ref == "subject")

    assert subject.proposed_label == "Module"


def test_nothing_moves_because_of_an_upgrade(corpus):
    """§5e. A library update changes proposals. It does not move a file, and it
    does not silently re-freeze a tree."""
    record_user_level_edit(corpus.conn, _rename("Class"))
    first = _design(corpus, catalogue=two_dimension_catalogue())
    before = frozen_tree(corpus.conn, plan_version=first.tree.plan_version_id)

    _design(corpus, catalogue=_packaged(subject_label="Module"), run="b")
    after = frozen_tree(corpus.conn, plan_version=first.tree.plan_version_id)

    assert after == before
    assert after.freeze_record.catalogue_release_id == "rel_seam"


def test_a_second_route_over_the_same_library_re_derives_nothing_the_user_said(
        corpus):
    """The failure `64` opens with, run twice: rename, then edit anything else.

    A re-route is not an upgrade — the library has not moved at all — and it was
    the cheaper half of the bug: `display_label` was assigned from the catalogue
    during routing and the rename landed afterwards on the binding, so the second
    route reassigned the library's word over the user's. Both runs are asked, and
    the level nobody touched is asked in both too, because an overlay that won on
    the second pass and everywhere else would not be an overlay.
    """
    record_user_level_edit(corpus.conn, _rename("Class"))
    catalogue = two_dimension_catalogue()

    for run in ("a", "b"):
        result = _design(corpus, catalogue=catalogue, run=run)
        levels = {d.role_ref: d.display_label
                  for d in result.branches[0].routing.candidates[0]
                  .resolved_dimensions}
        assert levels["subject"] == "Class", run
        assert levels["work_type"] == "Assignment type", run


def test_an_edit_is_readable_as_the_users_own_assertion_before_any_plan_adopts_it(
        corpus):
    """`66` §17, verified against what `64` built, as `63` §10 asked.

    `64` is the STORAGE half of the interaction and `66` §17 is the consent half:

        Existing approved structure remains stable unless the user explicitly
        adopts the new plan. ... It must not silently rename folders, reclassify
        files, reveal protected records, or move anything as a consequence of a
        changed answer.

    `63` §10 turned that into one property to check when `64` landed: the overlay
    must be readable as "what the user has asserted" INDEPENDENTLY of whether the
    plan version carrying it has been adopted. Two halves, both here.

    The presentation half -- a draft the user adopts, with a diff -- is P13's and
    is not built. This test is the part `64` owes and can keep.
    """
    first = _design(corpus)
    before = frozen_tree(corpus.conn, plan_version=first.tree.plan_version_id)

    record_user_level_edit(corpus.conn, _rename("Class"))

    # 1. Readable as the user's assertion, keyed on nothing a plan version owns.
    stored = user_level_edits(corpus.conn)
    assert [edit.display_label for edit in stored] == ["Class"]
    assert stored[0].key() == (SCHEMA, "subject", "subject")

    # 2. And the approved structure did not move because the answer changed. The
    #    edit is stored; the frozen tree is untouched until something designs
    #    again and the user adopts what comes back.
    assert frozen_tree(corpus.conn,
                       plan_version=first.tree.plan_version_id) == before
