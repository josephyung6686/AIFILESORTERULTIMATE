# tests/integration/test_sf3_a_group_is_a_draft_until_decided.py
"""`104` SF-3: an unreviewed group is a DRAFT, and two things may decide it.

SF-3's evidence line is three values written together -- `review_and_accept`,
`decided_by=RULES`, `COHERENT` -- and its treatment is one sentence: *"Keep draft
state until B judges or a person reviews."* What made it a safety flag rather than
a bug is what the acceptance is FOR. §5.3 builds the top level of the tree out of
accepted groups, so the row the rules wrote was the person's answer to the
question `00` calls the most important user-facing stage of the whole system --
*"show a small number of understandable, high-level organization proposals drawn
from their actual files, let them decide the major branches first"* -- and the
run answered it before drawing the screen.

Each guard here has the negative twin its own defect needs, because "a group is
accepted" is a monotone property and the positive half cannot tell a decision from
a default:

* a run where nobody decided places nothing AND says what it proposed;
* the person's gesture accepts it AND is on the audit trail as a gesture;
* site B's verdict accepts it only while B is RATIFIED -- an unratified B is the
  state the product ships in, and it must decide nothing;
* whatever decides it, `decided_by` names the decider, and `RULES` is not one of
  them for any group's acceptance.
"""
from __future__ import annotations

import io
import json
import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for _path in (str(_ROOT), str(_ROOT / "src")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import cli  # noqa: E402
from grouping.acceptance import group_state_as_of  # noqa: E402
from grouping.vocabulary import (  # noqa: E402
    ACCEPTED, PENDING_REVIEW, RULES, USER, USER_ACCEPTED, VALIDATOR,
)
from review_surface.vocabulary import (  # noqa: E402
    ACTION_ACCEPT, ACTION_ACCEPT_BULK, SURFACE_GROUP_PLAN,
)

SITUATION = "academic.coursework"
LABEL = "Coursework"


def _corpus(root: Path) -> Path:
    """One course, three files that name it and one that does not.

    Deliberately the shape `00`'s own worked example uses: two direct anchors and
    a sparse file that reaches the course through its neighbours. A group forms,
    so there is something to accept and something to refuse to accept.
    """
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    (corpus / "Lecture 08.txt").write_text(
        "Lecture 08 - Rotational Dynamics\nPHYS 1401\n"
        "Torque and angular momentum.\n")
    (corpus / "HW 3.txt").write_text(
        "Homework 3\n\nProblem 1. A ball is thrown upward...\n")
    return corpus


def _run(root: Path, *argv: str) -> tuple[int, str, Path]:
    corpus = root / "holder" / "corpus"
    if not corpus.exists():
        corpus = _corpus(root)
    database = root / "holder" / "plan.sqlite"
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                     "--user", "t", "--database", str(database), *argv],
                    out=out)
    return code, out.getvalue(), database


def _rows(database: Path, sql: str, *args) -> list[sqlite3.Row]:
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return [row for row in conn.execute(sql, args)]
    finally:
        conn.close()


def _standing_group_acceptances(database: Path) -> list[sqlite3.Row]:
    return _rows(
        database,
        "SELECT plan_version_id, group_id, acceptance, review_state, decided_by "
        "FROM group_acceptance WHERE membership_id IS NULL "
        "AND superseded_by IS NULL")


def _count(database: Path, table: str) -> int:
    return _rows(database, f"SELECT count(*) AS n FROM {table}")[0]["n"]


# --- a run nobody decided ------------------------------------------------------


def test_a_run_that_accepts_nothing_places_nothing_and_prints_the_proposal(
        tmp_path):
    """The whole of SF-3's treatment in one run.

    The corpus is read, a group forms and is recorded -- so the person can see
    what was found -- and then the run stops, because the next thing it would do
    is build folders out of a claim nobody has agreed to. `design_tree` refuses
    over a version with no accepted group and that refusal is the product working:
    it reaches the screen as a proposal and an exit code of 0, not as a failure.
    """
    code, screen, database = _run(tmp_path)

    assert code == 0, screen
    assert "These groups are proposed, and nothing has been filed:" in screen
    assert "--accept-groups" in screen
    # The card `00` describes: a label and a file count, and no filenames.
    assert f"  {LABEL} -- " in screen

    # Recorded, so the person can act on it next time -- and undecided.
    assert _count(database, "groups") > 0
    assert _standing_group_acceptances(database) == []

    # Nothing was designed and nothing was placed. Not "placed and withheld":
    # a tree with no branch means P11 was never asked.
    assert _count(database, "frozen_trees") == 0
    assert _count(database, "tree_nodes") == 0
    assert _count(database, "placement_decisions") == 0
    # And no file was planned into a packet either, which is the second half of
    # what an accepted group buys: `run_corpus` is handed the groups that BECAME
    # branches, and a draft becomes none.
    assert _count(database, "placement_group_plans") == 0


def test_the_proposal_screen_says_what_a_typed_flag_did_not_do(tmp_path):
    """`--freeze` on an undecided run froze nothing and said nothing. `104` SF-7.

    Found by running it rather than by reading it: the run printed the proposal,
    exited 0, and the person who had asked for a frozen plan had no way to tell
    that from having got one. Every other line on this screen is about what WILL
    happen, which is exactly what makes silence here read as success -- and a
    screen whose silence is false is SF-7's own defect, on a screen SF-3 added.

    The flags are named one by one, so a person who typed two sees both.
    """
    code, screen, database = _run(tmp_path, "--freeze")

    assert code == 0, screen
    assert "--freeze did nothing on this run" in screen, screen
    assert "Accept the groups first" in screen, screen
    # And it really did not: no frozen tree, and nothing moved.
    assert _count(database, "frozen_trees") == 0
    assert _count(database, "placement_decisions") == 0


def test_a_draft_keeps_everything_the_engine_concluded_about_it(tmp_path):
    """What a draft group still IS, which is everything except decided.

    Not accepted is not discarded, and the difference matters in three places.
    The person is shown a card, so the LABEL and the CATEGORY the engine concluded
    have to survive. They type the gesture at the next invocation, so the group has
    to be on disk under the id that run will re-derive. And the typed graph P9 drew
    is the material site C's dossier carries as reference-only, uncitable evidence
    (`placement.pipeline._graph_items`) -- a channel that reads P9's edges and not
    P9's acceptance, so a relationship between two files is shown to the model
    whether or not the group holding them has been agreed to.

    What a draft does NOT get is in the test above: no branch, no packet. The one
    thing it also does not get is an `accepted_group` dossier item, because that
    item asserts `user_confirmed` -- `_accepted_group_items`' own docstring says
    the merely-retrieved case "has no producer at this seam and no item is written
    claiming otherwise", and SF-3 does not add one.
    """
    _, screen, database = _run(tmp_path)

    group = _rows(database,
                  "SELECT group_id, display_label, group_category, "
                  "coherence_verdict FROM groups WHERE display_label = ?",
                  LABEL)
    assert group, screen
    assert group[0]["group_category"], "the card says what kind of material"

    members = _rows(database, "SELECT group_id FROM memberships "
                              "WHERE group_id = ? AND superseded_by IS NULL",
                    group[0]["group_id"])
    assert members, "a draft holds its members; it is a proposal, not a blank"
    assert _count(database, "group_edges") > 0, (
        "P9's typed graph is drawn for a draft, which is what site C's dossier "
        "carries as reference-only material")


def test_the_rules_never_write_a_groups_acceptance_however_the_run_ends(tmp_path):
    """SF-3's literal measurement, asserted over both endings of a run.

    `decided_by=RULES` on a group-level row is the flag itself. It is gone from the
    run that stops at the proposal AND from the run that builds a whole plan -- the
    second matters more, because that is where `approve_plan` used to put it back
    on the frozen version after the review had already written it once.
    """
    _, _, drafted_only = _run(tmp_path / "a")
    assert [row["decided_by"] for row in
            _standing_group_acceptances(drafted_only)] == []

    _, screen, accepted = _run(tmp_path / "b", "--accept-groups")
    deciders = {row["decided_by"]
                for row in _standing_group_acceptances(accepted)}
    assert deciders == {USER}, screen
    assert RULES not in deciders


# --- the person decides --------------------------------------------------------


def test_the_persons_gesture_flips_the_group_and_the_run_builds_from_it(tmp_path):
    """`--accept-groups`, and then a plan.

    The same command twice: the first run proposes, the second accepts what it
    proposed and is the run that designs the tree and places the files. The group
    id is content-derived and the review's plan version is fixed, so the draft the
    person read about is the draft they accepted.
    """
    first_code, first_screen, database = _run(tmp_path)
    assert first_code == 0
    assert _count(database, "placement_decisions") == 0, first_screen

    code, screen, database = _run(tmp_path, "--accept-groups")

    assert code == 0, screen
    assert "These groups are proposed, and nothing has been filed:" not in screen
    standing = _standing_group_acceptances(database)
    assert standing, screen
    for row in standing:
        assert row["acceptance"] == ACCEPTED
        assert row["decided_by"] == USER
        # The person accepted; nobody has reviewed the members one by one.
        assert row["review_state"] == USER_ACCEPTED
    assert _count(database, "placement_decisions") > 0


def test_the_next_run_builds_from_the_acceptance_without_repeating_the_gesture(
        tmp_path):
    """"The group flips and the NEXT run builds from it."

    Three runs of one command over one folder: propose, accept, and then a plain
    run with no flag at all. The third is the one that matters -- a decision is a
    record and not a mode, so the person types the accept once and every run after
    it has a plan. Nothing new is collected on that third run: re-collecting would
    be a second gesture recorded for one decision, and `accept_drafted_groups`
    skips a draft that is already accepted for exactly that reason.

    **IT HOLDS OVER AN UNCHANGED CORPUS**, which is a consequence of the address
    and not an oversight. The merged id is a digest over the P9 group ids it
    merges, which are themselves content-derived, so a folder that has not changed
    re-derives the group the person accepted. Add or delete a file and the digest
    moves: the next run proposes a new draft, and the person is asked about a group
    they have not seen before -- which is the right answer, because it is not the
    group they accepted.
    """
    _run(tmp_path)
    _run(tmp_path, "--accept-groups")
    gestures = _count(tmp_path / "holder" / "plan.sqlite", "review_actions")

    code, screen, database = _run(tmp_path)

    assert code == 0, screen
    assert "These groups are proposed, and nothing has been filed:" not in screen
    assert _count(database, "placement_decisions") > 0, screen
    assert _count(database, "review_actions") == gestures, (
        "a run that made no gesture recorded one")


def test_the_gesture_is_p13s_bulk_action_and_p9s_per_group_accept(tmp_path):
    """One typed word, two records, and neither invents the other's vocabulary.

    P13 owns the name of a gesture (`81` §14) and the batch is `accept_bulk`,
    which enumerates every member because "a filter expression cannot be re-read
    later to say which files a reversal applies to". P9's receiver is applied
    under the PER-GROUP word, so a person who later changes their mind about one
    group has a row of their own to supersede.
    """
    _, _, database = _run(tmp_path, "--accept-groups")

    actions = _rows(
        database,
        "SELECT surface, action, correction_scope, bulk_member_refs, "
        "presented_state_ref FROM review_actions")
    assert [(row["surface"], row["action"]) for row in actions] == [
        (SURFACE_GROUP_PLAN, ACTION_ACCEPT_BULK)]
    action = actions[0]
    assert action["correction_scope"] == cli.GROUP_ACCEPT_SCOPE
    members = json.loads(action["bulk_member_refs"])
    assert members, "a bulk acceptance enumerates its members"

    # The presentation the gesture was made against exists, which is what §8.7
    # requires and what `collect` refuses a gesture without.
    assert _rows(database,
                 "SELECT 1 FROM review_presentations WHERE presented_state_ref = ?",
                 action["presented_state_ref"])

    # And P9's own row, per group, under the per-group word.
    ids = [row["acceptance_id"] for row in _rows(
        database, "SELECT acceptance_id FROM group_acceptance "
                  "WHERE membership_id IS NULL AND superseded_by IS NULL")]
    for member in members:
        assert f"{cli.PLAN_VERSION}:{member}:{ACTION_ACCEPT}" in ids


def test_approve_plan_carries_the_decider_rather_than_making_one(tmp_path):
    """The frozen version says who decided, and does not say it was this command.

    §8.8 mints a new plan version for the frozen tree, so an acceptance has to be
    carried across or §6.8 refuses every group. What is carried is the standing
    row: its acceptance, its review state and its DECIDER, with the row it came
    from named. Before SF-3 this wrote `ACCEPTED`/`RULES` unconditionally, which
    would have put the bypass back one stage later even after the review stopped.
    """
    _, screen, database = _run(tmp_path, "--accept-groups")

    by_version = {row["plan_version_id"]: row
                  for row in _standing_group_acceptances(database)}
    assert cli.PLAN_VERSION in by_version, screen
    frozen = [version for version in by_version if version != cli.PLAN_VERSION]
    assert frozen, "the frozen plan version carries the acceptance forward"
    for version in frozen:
        assert by_version[version]["decided_by"] == USER
        assert by_version[version]["acceptance"] == ACCEPTED

    carried = _rows(
        database,
        "SELECT plan_version_id, review_decision_ref FROM group_acceptance "
        "WHERE plan_version_id <> ? AND membership_id IS NULL "
        "AND superseded_by IS NULL", cli.PLAN_VERSION)
    for row in carried:
        assert row["review_decision_ref"], (
            "the carried row names the standing row it repeats")


# --- site B decides, once the owner has ratified it ----------------------------


@pytest.fixture()
def p9_conn(tmp_path):
    from database_agent.db import create_schema, open_database
    from grouping.schema import create_grouping_schema

    conn = open_database(tmp_path / "p9.sqlite")
    create_schema(conn)
    create_grouping_schema(conn)
    try:
        yield conn
    finally:
        conn.close()


def _b_group(conn, dossier):
    from grouping.records import Group
    from grouping.store import record_group
    from grouping.vocabulary import CANDIDATE, STRONGLY_IDENTIFIED_FILE

    group = Group(
        group_id=dossier.group_id, seed_ref="lecture-08",
        seed_kind=STRONGLY_IDENTIFIED_FILE, proposed_basis=dossier.proposed_basis,
        anchor_facts=dossier.key_facts, pre_model_signals={},
        anchor_count=len(dossier.key_facts), coherence_verdict=None,
        coherence_citations=(), group_category=None, display_label=None,
        label_source=None, conflicts=(), stop_rule_hits=(), state=CANDIDATE,
        sensitivity_state="none", dossier_id=dossier.dossier_id,
        llm_response_ref=None, validation_verdict_ref=None, created_by=RULES,
        created_at="2026-09-11T00:00:00Z")
    record_group(conn, group)
    return group


def _b_answer():
    from grouping.p8_seam import MemberDecision, ModelAnswer
    from grouping.vocabulary import COHERENT, INCLUDED

    return ModelAnswer(
        coherent=COHERENT, category=None, label=None,
        members=(MemberDecision(file_id="lecture-08", decision=INCLUDED,
                                why="states the course code in its heading"),))


def test_a_ratified_site_b_verdict_accepts_the_group_it_judged(p9_conn):
    """The seam SF-3 asks for: B's ACCEPTED verdict is what flips the state.

    Nothing here ratifies B -- that is the owner's act and this branch does not
    make it. What it pins is that the wiring exists and reads the one flag: an
    `Answered` result only ever reaches `apply_p8_verdict` from
    `cli.observed_run_call`, and that function returns `Answered` exactly when
    `prompt.ratified` is true. The twin below holds the other side.

    `decided_by=VALIDATOR` because `DECIDED_BY` has three members and the model is
    not one of them: `accept_direct` is P8's validator's outcome over the model's
    claim, reached only once every citation resolved and no stronger fact
    contradicted it.
    """
    from grouping.fixtures import course_dossier_fixture
    from grouping.p8_seam import Answered, apply_p8_verdict
    from p9.p8_fixtures import accepted_direct_verdict

    dossier = course_dossier_fixture()
    group = _b_group(p9_conn, dossier)
    verdict = accepted_direct_verdict(dossier_id=dossier.dossier_id)

    apply_p8_verdict(
        p9_conn, group=group, dossier=dossier,
        result=Answered(result=verdict, answer=_b_answer()),
        plan_version_id="plan_0", created_at="2026-09-11T00:00:00Z")

    row = p9_conn.execute(
        "SELECT acceptance, review_state, decided_by, review_decision_ref "
        "FROM group_acceptance WHERE group_id = ? AND membership_id IS NULL "
        "AND superseded_by IS NULL", (group.group_id,)).fetchone()
    assert row is not None, "a ratified accepting verdict decides the group"
    assert row["acceptance"] == ACCEPTED
    assert row["decided_by"] == VALIDATOR
    # Accepted by the model's judged verdict, and still unseen by a person.
    assert row["review_state"] == PENDING_REVIEW
    assert row["review_decision_ref"] == verdict.verdict_id
    assert group_state_as_of(p9_conn, group_id=group.group_id,
                             plan_version_id="plan_0") == ACCEPTED


def test_an_unratified_site_b_decides_nothing(p9_conn):
    """The state the product ships in, and the twin that makes the test above mean
    something. An observe-only site records its call and applies nothing -- so the
    group keeps the state P9's engine gave it and no version has an opinion."""
    from grouping.fixtures import course_dossier_fixture
    from grouping.p8_seam import ObservedOnly, apply_p8_verdict
    from p9.p8_fixtures import accepted_direct_verdict

    dossier = course_dossier_fixture()
    group = _b_group(p9_conn, dossier)

    apply_p8_verdict(
        p9_conn, group=group, dossier=dossier,
        result=ObservedOnly(accepted_direct_verdict(
            dossier_id=dossier.dossier_id)),
        plan_version_id="plan_0", created_at="2026-09-11T00:00:00Z")

    assert p9_conn.execute(
        "SELECT 1 FROM group_acceptance WHERE group_id = ? "
        "AND membership_id IS NULL", (group.group_id,)).fetchone() is None
    assert group_state_as_of(p9_conn, group_id=group.group_id,
                             plan_version_id="plan_0") != ACCEPTED


def _a_part_b_accepted(conn, group_id: str, *, decided_by: str = VALIDATOR):
    from grouping.acceptance import record_acceptance
    from grouping.records import GroupAcceptance

    record_acceptance(conn, GroupAcceptance(
        acceptance_id=f"acc:{group_id}", plan_version_id=cli.PLAN_VERSION,
        group_id=group_id, membership_id=None, acceptance=ACCEPTED,
        review_state=PENDING_REVIEW, user_edited_label=None, aliases=(),
        review_decision_ref="v-1", decided_by=decided_by,
        created_at="2026-09-11T00:00:00Z"))


def test_site_b_accepts_a_merged_draft_only_when_it_accepted_every_part(p9_conn):
    """The merge is one card to the person, so the answer about it is unanimous.

    B judges the groups P9 proposed; the draft is a merge P9 never proposed, so B
    has no verdict about it and never will. `_carry_site_bs_acceptance` is the
    carry: every part accepted by B, and the merge is accepted too. Three of four
    is not a majority to round up -- it is B declining to say that this group holds
    together, and accepting it anyway would file the fourth part's files into a
    branch on a judgement nobody made about them.
    """
    _a_part_b_accepted(p9_conn, "part-a")
    _a_part_b_accepted(p9_conn, "part-b")

    cli._carry_site_bs_acceptance(
        p9_conn, merged_id="merged-1", parts=("part-a", "part-b"),
        created_at="2026-09-11T00:00:00Z")

    row = p9_conn.execute(
        "SELECT acceptance, decided_by FROM group_acceptance "
        "WHERE group_id = 'merged-1' AND superseded_by IS NULL").fetchone()
    assert row is not None, "every part was B's, so the merge is B's"
    assert (row["acceptance"], row["decided_by"]) == (ACCEPTED, VALIDATOR)


def test_one_undecided_part_leaves_the_whole_merge_a_draft(p9_conn):
    """The twin. Without it the test above cannot tell unanimity from "any"."""
    _a_part_b_accepted(p9_conn, "part-a")

    cli._carry_site_bs_acceptance(
        p9_conn, merged_id="merged-2", parts=("part-a", "part-b"),
        created_at="2026-09-11T00:00:00Z")

    assert p9_conn.execute(
        "SELECT 1 FROM group_acceptance WHERE group_id = 'merged-2'"
    ).fetchone() is None


def test_a_part_the_person_accepted_is_not_site_bs_answer(p9_conn):
    """The second twin, and it is about the COLUMN rather than the state.

    `group_state_as_of` answers `accepted` for a person's row as readily as for
    B's, so a carry that asked only "is this part accepted" would report a group
    as judged coherent by the model when what actually happened is that somebody
    accepted one of its parts by hand. Two different sentences; one of them is not
    B's to say.
    """
    _a_part_b_accepted(p9_conn, "part-a")
    _a_part_b_accepted(p9_conn, "part-b", decided_by=USER)

    cli._carry_site_bs_acceptance(
        p9_conn, merged_id="merged-3", parts=("part-a", "part-b"),
        created_at="2026-09-11T00:00:00Z")

    assert p9_conn.execute(
        "SELECT 1 FROM group_acceptance WHERE group_id = 'merged-3'"
    ).fetchone() is None


def test_a_standing_decision_about_the_merge_is_left_alone(p9_conn):
    """Whatever a person decided about the merge outlives the model's answer.

    Either way round: a merge they accepted is not re-accepted under a different
    decider, and a merge they REJECTED is not quietly accepted by the next run's
    model verdict, which is the direction that would cost something.
    """
    from grouping.acceptance import record_acceptance
    from grouping.records import GroupAcceptance
    from grouping.vocabulary import REJECTED, USER_REJECTED

    _a_part_b_accepted(p9_conn, "part-a")
    record_acceptance(p9_conn, GroupAcceptance(
        acceptance_id="the-person-said-no", plan_version_id=cli.PLAN_VERSION,
        group_id="merged-4", membership_id=None, acceptance=REJECTED,
        review_state=USER_REJECTED, user_edited_label=None, aliases=(),
        review_decision_ref=None, decided_by=USER,
        created_at="2026-09-11T00:00:00Z"))

    cli._carry_site_bs_acceptance(
        p9_conn, merged_id="merged-4", parts=("part-a",),
        created_at="2026-09-11T02:00:00Z")

    rows = [dict(row) for row in p9_conn.execute(
        "SELECT acceptance_id, acceptance FROM group_acceptance "
        "WHERE group_id = 'merged-4' AND superseded_by IS NULL")]
    assert rows == [{"acceptance_id": "the-person-said-no",
                     "acceptance": REJECTED}]


def test_the_whole_chain_flips_a_group_only_when_bs_prompt_is_ratified(
        p9_conn, monkeypatch):
    """`observed_run_call` -> `apply_p8_verdict` -> an acceptance, or not.

    The seam end to end, with `prompt.ratified` as the only thing that differs
    between the two halves -- simulated the way `tests/test_cli_observe_sites.py`
    simulates it, by replacing the field on the prompt the product itself loads.
    Nothing here ratifies anything on disk; the manifest still says `unratified`
    and the run this checkout ships still decides nothing.
    """
    import dataclasses

    from llm_harness.schema import create_llm_schema
    from llm_harness.store import record_response
    from llm_harness.vocabulary import B_GROUP
    from grouping.fixtures import course_dossier_fixture
    from grouping.p8_seam import Answered, ObservedOnly, apply_p8_verdict
    from p9.p8_fixtures import accepted_direct_verdict

    create_llm_schema(p9_conn)
    dossier = course_dossier_fixture()
    verdict = accepted_direct_verdict(dossier_id=dossier.dossier_id)
    record_response(
        p9_conn, dossier_id=dossier.dossier_id,
        response_bytes=json.dumps({"claims": [{"payload": {
            "coherent": "yes", "basis": "direct-anchor", "category": None,
            "label": None,
            "members": [{"file_id": "lecture-08", "decision": "include",
                         "why": "states the course code", "evidence_refs": []}],
            "outliers": [], "merge_terms": []}}]}).encode("utf-8"),
        model_id="fixture", prompt_fingerprint="fp", release_audit_id=1,
        release_id="rel-1", observed_at="2026-09-11T00:00:00Z")
    monkeypatch.setattr(cli, "run_call", lambda *_a, **_k: verdict)

    @dataclasses.dataclass
    class _Deps:
        """The two `CallDependencies` fields B's wrapper fills in per group.
        A dataclass because `observed_run_call` `replace`s them."""

        basis_key: str = "group"
        learning_subject_id: str = "group"

    def ask(*, ratified: bool):
        from types import SimpleNamespace
        return cli.observed_run_call(
            p9_conn, SimpleNamespace(subject_ref=f"group:{dossier.group_id}"),
            gate=None, model_client=None,
            prompt=dataclasses.replace(cli.observe_prompt(B_GROUP),
                                       ratified=ratified),
            validation_dependencies=_Deps(),
            observed_at="2026-09-11T00:00:00Z")

    observed = ask(ratified=False)
    assert isinstance(observed, ObservedOnly), (
        "an unratified site must not hand the seam an answer to apply")

    answered = ask(ratified=True)
    assert isinstance(answered, Answered)

    group = _b_group(p9_conn, dossier)
    apply_p8_verdict(p9_conn, group=group, dossier=dossier, result=answered,
                     plan_version_id=cli.PLAN_VERSION,
                     created_at="2026-09-11T00:00:00Z")

    row = p9_conn.execute(
        "SELECT acceptance, decided_by FROM group_acceptance "
        "WHERE group_id = ? AND membership_id IS NULL AND superseded_by IS NULL",
        (group.group_id,)).fetchone()
    assert row is not None, "the ratified chain decided nothing"
    assert (row["acceptance"], row["decided_by"]) == (ACCEPTED, VALIDATOR)


def test_a_persons_acceptance_outranks_the_models_and_is_never_superseded(
        p9_conn):
    """`104` R-80's rule, now that the rules no longer write an acceptance.

    `_a_person_accepted` used to take ANY standing `accepted` row as the person's
    word, which was only readable while the rules wrote one nobody had made. It
    reads `decided_by` now, and both halves of that matter: a person's row stops
    the model, and the model's own row from a previous run does not.
    """
    from grouping.fixtures import course_dossier_fixture
    from grouping.p8_seam import Answered, _a_person_accepted, apply_p8_verdict
    from grouping.records import GroupAcceptance
    from grouping.acceptance import record_acceptance
    from p9.p8_fixtures import accepted_direct_verdict

    dossier = course_dossier_fixture()
    group = _b_group(p9_conn, dossier)

    apply_p8_verdict(
        p9_conn, group=group, dossier=dossier,
        result=Answered(result=accepted_direct_verdict(
            dossier_id=dossier.dossier_id), answer=_b_answer()),
        plan_version_id="plan_0", created_at="2026-09-11T00:00:00Z")
    # B's own row is not a person's, so B is not silenced by itself.
    assert _a_person_accepted(p9_conn, group.group_id) is False

    standing = p9_conn.execute(
        "SELECT acceptance_id FROM group_acceptance WHERE group_id = ? "
        "AND membership_id IS NULL AND superseded_by IS NULL",
        (group.group_id,)).fetchone()["acceptance_id"]
    record_acceptance(p9_conn, GroupAcceptance(
        acceptance_id="the-person", plan_version_id="plan_0",
        group_id=group.group_id, membership_id=None, acceptance=ACCEPTED,
        review_state=USER_ACCEPTED, user_edited_label=LABEL, aliases=(),
        review_decision_ref=None, decided_by=USER,
        created_at="2026-09-11T01:00:00Z", supersedes=standing,
        supersede_reason="the person read the proposal and accepted it"))

    assert _a_person_accepted(p9_conn, group.group_id) is True
