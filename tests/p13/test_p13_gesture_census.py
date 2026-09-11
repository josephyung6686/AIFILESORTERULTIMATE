"""The six approved gestures: where each ENTERS the product, and what APPLIES it.

`tests/p13/test_p13_unhomed_gestures.py` asks the vocabulary question -- does P13
publish a name for every §8.7 gesture -- and it has been green since 2026-09-02.
This module asks the other half, which the ruling that approved those names made
unavoidable and nobody had yet measured: **a name is not a gesture.** A member of
`ACTIONS` that no screen collects and no part applies is a word the product can
spell and cannot do, and until `104` R-41 all seven were exactly that -- zero
consumers anywhere outside `vocabulary.py`.

Two questions per gesture, and both must be answered or the gesture is not built:

* **COLLECTOR** -- the place a person's gesture enters. On this deployment that is
  a flag on the proposals screen, in the answer grammar `--confirm`, `--rename`,
  `--reject` and `--send-set` already use, and `review_gestures.py` is the seam
  that turns one into a stored `review_action` (`81` §13.1: a canvas gesture
  travels in the same audit trail as accepting a file).
* **RECEIVER** -- the part that applies it. `81` §3.3 traces each to the P9, P10
  or P11 word it was adopted from, and this module checks whether that part can
  actually DO anything with it, rather than whether it can spell it.

**A receiver is not invented to close a row.** Four of the seven members are
refused by name where they arrive, in sets their own modules spell out -- P10's
`ACTIONS_WITH_NO_WRITER` exists precisely so "a sixteenth member of
`TREE_EDIT_ACTIONS` cannot quietly inherit a refusal nobody decided on". Those get
a strict xfail naming the blocker, so the day the writer lands the marker comes
off under somebody who has read the reason.

**The method is `_sources_calling`'s**, and deliberately the same one
`tests/integration/test_composition_root.py` uses: a reference is not a call and
an import is not a use. It over-states reachability -- a bare name matches in
every namespace -- which is the direction that makes a NEGATIVE verdict safe: a
symbol this census calls uncalled is genuinely uncalled.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from review_surface import vocabulary as v

_SRC = Path(__file__).resolve().parents[2] / "src"


def _sources_calling(function_name: str) -> set[str]:
    """Modules anywhere in `src/` that CALL `function_name`, by AST, not by grep."""
    callers = set()
    for path in sorted(_SRC.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = (func.attr if isinstance(func, ast.Attribute)
                    else func.id if isinstance(func, ast.Name) else None)
            if name == function_name:
                callers.add(str(path.relative_to(_SRC)))
    return callers


def test_the_instrument_can_tell_a_caller_from_a_name():
    """The falsifying twin. Without it every assertion below could be vacuous.

    `collect` is called by the seam that exists; `unhomed_gestures` is a helper in
    a sibling TEST module, so no file under `src/` can call it and the instrument
    must say so. A checker that answered "called" to both would measure nothing,
    and a checker that answered "uncalled" to both would condemn the wiring that
    is really there.
    """
    assert _sources_calling("collect")
    assert not _sources_calling("unhomed_gestures")


# --- 1. rename -- WIRED (`104` R-41) -----------------------------------------

def test_rename_has_a_collector_and_a_receiver():
    """§8.7's "renaming a branch", collected on the canvas and applied by P10.

    COLLECTOR: `cli.apply_level_relabels`, behind `--rename-level
    SCHEMA:ROLE:FIELD=NAME`, through `review_gestures.collect_level_relabel` --
    which is `collect`, so the gesture is stored as a `review_action` on the
    `canvas` surface and `route` hands it to P10.

    RECEIVER: `tree_design.user_edits.record_user_level_edit`, whose overlay
    `route_branch` applies as the LAST step of composition (`64` §4), after the
    C1-C8 gates have judged the recipe. `tests/integration/test_cli_level_relabel.py`
    runs the whole loop through the shipped command.

    **P10 carries a SECOND receiver for this same P13 name, and it is not wired.**
    `tree_design.store.apply_review_action` writes `RENAME` against a NODE, which
    opens a new plan version and renames one folder of one tree. That is a
    different act from renaming a LEVEL -- one is this plan, the other is the
    vocabulary and outlives every plan -- and `81` §14's ruling that P13 owns the
    name is what puts both under one word. Only the level half is reachable today.
    """
    assert v.ACTION_RENAME in v.ACTIONS
    assert "cli.py" in _sources_calling("collect_level_relabel"), (
        "no screen collects a rename")
    assert _sources_calling("record_user_level_edit"), (
        "nothing applies a rename a person made")


# --- 2. exclude_from_packet -- NOT WIRED --------------------------------------

def test_exclude_from_packet_has_a_collector_and_a_receiver():
    """§8.7's "excluding one member from a packet". A packet is a purpose-defined
    GROUP -- `01` §5.6's `Chinese University Application Materials`, a course
    packet, an application packet -- so the gesture takes a file out of a group
    the product proposed.

    **BLOCKER 1, the receiver.** `81` §3.3 traces this to P9, and P9 does carry
    the word: `grouping.learning._ACTIONS` maps `exclude_from_packet` to
    `(rejected, user-excluded-from-packet, reject)` and
    `grouping.learning.apply_review_action` writes a `GroupAcceptance` row with
    that review state. **Nothing reads that state.** Its one reader is
    `grouping.acceptance.membership_review_state_as_of`, which no module in `src/`
    calls -- it is on the live unreachable census -- so an excluded member is
    still in the group on the next run. Recording is not applying, and a gesture
    that is recorded and never applied is the silent no-op every refusal in this
    codebase exists to prevent.

    There IS a live path to the same EFFECT and it is deliberately not used as a
    substitute: `grouping.store.record_membership` with `decision=EXCLUDED` is
    read by `tree_design.upstream.accepted_groups`, which drops excluded members
    from the branch, and `grouping.pipeline._retract_unsupported_memberships` is
    the worked example of writing that superseding row. Wiring a collector to it
    would make the gesture WORK and would leave P9's own record of it unread, so
    the audit trail and the tree would disagree about whether the person acted.

    **BLOCKER 2, the collector.** There is no group-review screen to collect it
    on. `104` SF-3 is the measurement: `review_and_accept` records every group as
    accepted and coherent with `decided_by=RULES`, so no person is shown a
    packet's members and none is presented -- and §8.7 refuses a gesture with no
    recorded presentation. `104` §7 Phase 5 schedules that screen separately, as
    "group review before design (R-23)".

    `xfail(strict=True)`: it states both blockers today and turns the suite RED
    the day either half lands, which forces the marker off under somebody who has
    read them.
    """
    assert v.ACTION_EXCLUDE_FROM_PACKET in v.ACTIONS
    assert _sources_calling("membership_review_state_as_of"), (
        "P9 records the exclusion and nothing in the product reads it back")


test_exclude_from_packet_has_a_collector_and_a_receiver = pytest.mark.xfail(
    strict=True,
    reason="P9 records `exclude_from_packet` as a review state whose only reader, "
           "`membership_review_state_as_of`, no module in src/ calls -- so the "
           "exclusion is stored and never applied. And there is no screen to "
           "collect it on: `review_and_accept` accepts every group with "
           "decided_by=RULES (104 SF-3), so no packet's members are presented and "
           "§8.7 refuses a gesture with no recorded presentation. R-23's group "
           "review is the owed screen. XPASSes the day the reader is wired.",
)(test_exclude_from_packet_has_a_collector_and_a_receiver)


# --- 3, 4, 5. merge, split, reorder -- NOT WIRED ------------------------------

def test_merge_and_split_have_a_receiver():
    """§8.7's "merging or splitting groups" -- one phrase, two gestures.

    **BLOCKER: P10 refuses both by name, before anything is written.**
    `tree_design.store.ACTIONS_WITH_NO_WRITER` names `merge` and `split`, and
    `apply_review_action` raises `ReviewActionRefused` on them ahead of every
    lookup -- "a silent no-op still opens a draft, and the user would see a new
    plan version that changed nothing". That set is spelled out rather than
    derived by subtraction precisely so this cannot be waved through.

    Neither is blocked on an upstream part: the module's own comment says "each is
    a canvas gesture whose semantics are §5.2's and §5.10's; none is blocked on an
    upstream part. They are the honest remaining scope." So the blocker is
    unwritten work in P10 and nothing else, and a collector built now would hand a
    person's gesture to a function that refuses it.

    Asserted on the SET rather than by calling the function: a refusal spelled in
    a module-level frozenset is the fact, and the day a writer lands the member
    leaves the set and this goes green.
    """
    from tree_design.store import ACTIONS_WITH_NO_WRITER
    from tree_design.vocabulary import MERGE, SPLIT

    assert MERGE not in ACTIONS_WITH_NO_WRITER
    assert SPLIT not in ACTIONS_WITH_NO_WRITER


test_merge_and_split_have_a_receiver = pytest.mark.xfail(
    strict=True,
    reason="`merge` and `split` are in tree_design.store.ACTIONS_WITH_NO_WRITER; "
           "apply_review_action refuses both by name before opening a draft. P10's "
           "own comment says neither is blocked on an upstream part -- it is "
           "unwritten work in P10. XPASSes the day a writer lands.",
)(test_merge_and_split_have_a_receiver)


def test_reorder_has_a_receiver():
    """§8.7's "changing template order", and it is refused in TWO places.

    **BLOCKER 1:** `reorder` is in `tree_design.store.ACTIONS_WITH_NO_WRITER`, so
    the canvas edit is refused before a draft opens, exactly as `merge` is.

    **BLOCKER 2, and it is the one that matters for `64`:** the label overlay --
    the only durable per-level record this product has -- holds any of
    `DIMENSION_ACTIONS` by design, so it is SHAPED to carry a reorder ("the
    overlay should be designed to hold them rather than retrofitted per action"),
    and `OVERLAY_ACTIONS_WITH_A_WRITER` is `(renamed,)`. `record_user_level_edit`
    refuses anything else before storing it, on its own stated ground: "an edit
    nothing can apply is a silent no-op that survives every future session, and
    the user would see their edit accepted and never honoured".

    So `104` R-41's wiring does NOT reach this one, and the shape of the refusal
    is why: the writer is the place that list grows, one action at a time, and
    growing it needs the applier that honours a reordered dimension in routing.
    """
    from tree_design.store import ACTIONS_WITH_NO_WRITER
    from tree_design.user_edits import OVERLAY_ACTIONS_WITH_A_WRITER
    from tree_design.vocabulary import ACTION_REORDERED, REORDER

    assert REORDER not in ACTIONS_WITH_NO_WRITER
    assert ACTION_REORDERED in OVERLAY_ACTIONS_WITH_A_WRITER


test_reorder_has_a_receiver = pytest.mark.xfail(
    strict=True,
    reason="`reorder` is refused twice: tree_design.store.ACTIONS_WITH_NO_WRITER "
           "names it, and the label overlay's OVERLAY_ACTIONS_WITH_A_WRITER is "
           "(renamed,) so record_user_level_edit refuses a reordered dimension "
           "rather than store one nothing applies. XPASSes when either writer lands.",
)(test_reorder_has_a_receiver)


# --- 6. create_custom_template -- NOT WIRED -----------------------------------

def test_create_custom_template_has_a_receiver():
    """§8.7's "creating a custom template", ruled a DISTINCT gesture on 2026-09-02.

    The owner's words are at the member: "a template is a reusable shape; a folder
    is one actual folder". `create_custom_folder` is a change to this plan;
    creating a template is a change to what the product will propose NEXT time.

    **BLOCKER 1:** P10's nearest word, `create-manually`, is in
    `ACTIONS_WITH_NO_WRITER`, so the canvas half is refused by name like `merge`.

    **BLOCKER 2, and it is the one that cannot be closed in P10 at all:** a custom
    template is an AUTHORED template, and authoring one is site E's output. `01`
    §5.7's library is the shipped, ratified set; a gesture that minted a
    `TemplateApplicability` from a person's canvas would be this deployment
    writing rows into the library P10 validates against. That is the "unratified
    site's output" case, and it is left unbuilt rather than invented.

    `route` already carries the gesture to P10 -- `ACTION_ROUTING` gives it the
    one row of the seven, because the gesture can be made on a residual surface
    that routes to P11 alone -- so the routing half is built and the writer is not.
    """
    from review_surface.routing import ACTION_ROUTING
    from tree_design.store import ACTIONS_WITH_NO_WRITER
    from tree_design.vocabulary import CREATE_MANUALLY

    assert ACTION_ROUTING[v.ACTION_CREATE_CUSTOM_TEMPLATE] == ("P10",)
    assert CREATE_MANUALLY not in ACTIONS_WITH_NO_WRITER


test_create_custom_template_has_a_receiver = pytest.mark.xfail(
    strict=True,
    reason="P10's `create-manually` is in ACTIONS_WITH_NO_WRITER, and a custom "
           "template is an authored template -- site E's output, which is "
           "unratified. A gesture that minted a TemplateApplicability from a "
           "canvas would write rows into the library P10 validates against. "
           "XPASSes the day P10 carries a writer.",
)(test_create_custom_template_has_a_receiver)


# --- 7. set_refinement_disposition -- NOT WIRED -------------------------------

def test_set_refinement_disposition_has_a_collector():
    """§8.7's "choosing a shallow fallback", and the one coined name of the seven.

    It is coined from the sentence recording its own absence -- `tree_design/
    pipeline.py`'s `_with_refinement`: "there is no `set-refinement-disposition`
    review action". §5.8 keeps `shallow-by-choice` and `refine-later` apart
    precisely so a deliberate design does not look like unfinished work, and
    today nobody can choose the first.

    **THE RECEIVER EXISTS**, which is what makes this different from the four
    above. `_with_refinement` applies whatever the injected `refinement_for`
    returns, stamps `refinement_disposition` and `refinement_reason` on the node,
    and the verdict reaches the frozen tree; `build_destination_index` refuses a
    tree that carries none. Nothing in P10 needs writing.

    **BLOCKER 1, the screen.** No surface prints a node's disposition or its
    reason -- `cli.report` never reads either field. §8.7 requires feedback to
    carry the evidence that produced it and `collect` refuses a gesture with no
    recorded presentation, so there is nothing a person was shown to answer. The
    run's own sentence even invites the gesture -- "Nobody was asked, so say so if
    you want it split" -- and that sentence goes into the frozen tree rather than
    onto the screen.

    **BLOCKER 2, the subject, and it is the harder one.** `refinement_for` is
    handed ONE `Node` at a time, and a `Node` carries `display_label` and
    `parent_node_id` and not its chain, so the only thing a flag could name is a
    bare label. Every node this gesture can reach has a parent and was not split
    -- `_with_refinement` answers `refined` for the rest -- so its whole domain is
    the levels below a branch, where `syllabus` under two courses is two folders
    of one name. `--reject` and `--send-set` both refuse that ambiguity by name
    rather than guess, and a gesture that stamped both would be acting on
    something other than what was named.

    Both are owed work rather than impossibilities, and neither is invented here.
    """
    assert "cli.py" in _sources_calling("collect_refinement_disposition")


test_set_refinement_disposition_has_a_collector = pytest.mark.xfail(
    strict=True,
    reason="The receiver exists -- `_with_refinement` applies whatever "
           "`refinement_for` returns and the verdict reaches the frozen tree -- and "
           "the collector cannot be built honestly yet: no screen prints a node's "
           "disposition or reason, so §8.7 has no presentation to record a gesture "
           "against; and `refinement_for` sees one Node with no chain, so the only "
           "nameable subject is a bare label, which is ambiguous across parents "
           "exactly where this gesture applies. XPASSes when a collector lands.",
)(test_set_refinement_disposition_has_a_collector)


# --- the census itself --------------------------------------------------------

#: Every member above, against the test that measures it. Written out rather than
#: discovered, because a discovery rule that found nothing would report full
#: coverage -- and the failure this file exists to catch is a member nobody
#: measured. The spellings are literals for
#: `test_the_seven_the_owner_approved_are_all_published`'s reason: these are the
#: strings the owner approved on 2026-09-02, and a table comparing the constants
#: to themselves would pass through any rename.
CENSUS: dict[str, object] = {
    "rename": test_rename_has_a_collector_and_a_receiver,
    "exclude_from_packet": test_exclude_from_packet_has_a_collector_and_a_receiver,
    "merge": test_merge_and_split_have_a_receiver,
    "split": test_merge_and_split_have_a_receiver,
    "reorder": test_reorder_has_a_receiver,
    "create_custom_template": test_create_custom_template_has_a_receiver,
    "set_refinement_disposition": test_set_refinement_disposition_has_a_collector,
}

#: The one of the seven that is WIRED. It was none of them until `104` R-41, and
#: this line is the count a later pass can move without reading the whole file.
WIRED: tuple[str, ...] = ("rename",)


def test_the_census_covers_every_member_p13_approved_on_2026_09_02():
    """A member the census forgot is a member nobody is measuring.

    Asserted against `ACTIONS` itself and in both directions: every approved
    member has a test here, and every name in the table is one P13 still
    publishes. Growing the tuple again therefore fails this file until somebody
    says where the new gesture enters and what applies it -- which is the question
    `81` §14.1 reserved to the owner for the NAME, asked one step later about the
    mechanism.
    """
    approved = {"exclude_from_packet", "rename", "merge", "split", "reorder",
                "create_custom_template", "set_refinement_disposition"}
    assert approved <= set(v.ACTIONS), sorted(approved - set(v.ACTIONS))
    assert set(CENSUS) == approved, sorted(set(CENSUS) ^ approved)
    assert set(WIRED) <= approved
    for name, test in CENSUS.items():
        assert callable(test), name
        assert (getattr(test, "pytestmark", None) or []) == [] or name not in WIRED, (
            f"{name} is listed as wired and its census test is still marked")
