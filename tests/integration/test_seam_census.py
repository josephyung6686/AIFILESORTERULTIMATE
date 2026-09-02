# tests/integration/test_seam_census.py
"""Which parts actually talk to which, on a run of the product.

`84` §5.5: *"The suite tests PARTS. The defect lives in the WIRING."* Three
shipped defects had passing unit tests -- a residual library built and passed
`{}`, a learning guard with no caller, an egress guard nothing reached -- because
every test that touched them constructed BOTH sides itself. A seam test that
builds both ends proves the two shapes fit. It cannot prove they ever meet.

So nothing here builds a fixture for a part. Every assertion is made against
what `cli.main` actually did, or against the rows a run of `cli.main` actually
left in a database. The full census, with a verdict and its evidence for every
ordered pair, is `planning/86-SEAM-CENSUS.md`; this file is the half of it that
can go red.
"""
from __future__ import annotations

import io
import os
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(SRC))

import cli  # noqa: E402
from mutation.constraints import FilesystemConstraints  # noqa: E402
from mutation.plan import build_plan  # noqa: E402
from mutation.vocabulary import PRESERVE_BOTH_DETERMINISTIC_SUFFIX  # noqa: E402
from placement.store import decisions_for_plan  # noqa: E402
from privacy.vocabulary import HANDLING_CLASSES  # noqa: E402
from placement.vocabulary import PLACE  # noqa: E402
from tree_design.store import nodes_for_version  # noqa: E402

#: The top-level package under `src/` that owns each part. `02`'s thirteen, plus
#: the three units that are not parts: `src/questions/` is the onboarding
#: workstream `84` §3 says "P15" means in this repo, `src/readers/` is P5's
#: deployment layer (`02`, "not a fourteenth part either"), and
#: `src/recognition/` is the injected sensitivity rule set D2 leaves to a
#: deployment.
PART_OF_PACKAGE: dict[str, str] = {
    "database_agent": "P1", "eval_harness": "P2", "scan_agent": "P3",
    "evidence_shape": "P4", "extractors": "P5", "facts": "P6",
    "privacy": "P7", "llm_harness": "P8", "grouping": "P9",
    "tree_design": "P10", "placement": "P11", "mutation": "P12",
    "review_surface": "P13", "questions": "QUESTIONS", "readers": "READERS",
    "recognition": "RECOGNITION",
}

#: `84` §1: `src/cli.py` is the sole composition root. `production.py` and
#: `orchestrator.py` are the assemblies it calls, and they pick no policy of
#: their own, so a call made from either is the root's call.
ROOT_MODULES: frozenset[str] = frozenset({"cli.py", "production.py",
                                          "orchestrator.py"})
ROOT = "ROOT"


def _part_of(filename: str) -> str | None:
    """Which part owns the code in this frame, or `None` for anything outside."""
    prefix = str(SRC) + os.sep
    if not filename.startswith(prefix):
        return None
    head = filename[len(prefix):].split(os.sep)[0]
    if head.endswith(".py"):
        return ROOT if head in ROOT_MODULES else None
    return PART_OF_PACKAGE.get(head)


class _SeamRecorder:
    """Every cross-part call a run makes, by the part on each end.

    `sys.setprofile` rather than an import graph: an import proves a name is
    visible, and all three of `84` §5.5's defects had the import and no call.
    The caller is the NEAREST enclosing frame that a part owns, so a callback a
    part hands the root is attributed to the root that holds it -- which is what
    the composition rule means by the root picking the policy.
    """

    def __init__(self) -> None:
        self.edges: Counter = Counter()
        self.symbols: dict[tuple[str, str], set[str]] = {}

    def __call__(self, frame, event, arg) -> None:
        if event != "call":
            return
        callee = _part_of(frame.f_code.co_filename)
        if callee is None:
            return
        back, caller = frame.f_back, None
        while back is not None:
            caller = _part_of(back.f_code.co_filename)
            if caller is not None:
                break
            back = back.f_back
        if caller is None or caller == callee:
            return
        self.edges[(caller, callee)] += 1
        self.symbols.setdefault((caller, callee), set()).add(
            frame.f_code.co_name)

    def __enter__(self) -> "_SeamRecorder":
        sys.setprofile(self)
        return self

    def __exit__(self, *exc) -> None:
        sys.setprofile(None)


def _corpus(root: Path) -> Path:
    """Two files a course code groups, and one that names nothing.

    Both halves are needed: the identified pair is what reaches P9's grouping and
    P11's placement, and the anonymous file is what reaches P7 with no
    classification, which is the branch `privacy/denial.py` says the audit log
    will be full of.
    """
    corpus = root / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor.\n")
    (corpus / "PHYS 1401 problem set 3.txt").write_text(
        "PHYS 1401 Problem Set 3\n\nDue 2026-03-14. Spring 2026.\n")
    (corpus / "notes about nothing.txt").write_text(
        "Some free text with no identifiers at all.\n")
    return corpus


def _argv(corpus: Path, database: Path) -> list[str]:
    return [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy",
            "--database", str(database)]


#: The seams a run of the product must exercise. Each entry is (from, to, why),
#: and the "why" is the design sentence that says the two must meet -- not a
#: description of what the code happens to do, which is how a census becomes a
#: whitelist.
LIVE_SEAMS: tuple[tuple[str, str, str], ...] = (
    ("P3", "P1", "`02`: P3 publishes a populated `files`, which is P1's table"),
    ("P4", "P1", "`P4 SPEC` Contract in: P4 appends its runs through P1"),
    ("P5", "P4", "`02` §2.8: six extractors emit the ONE frozen observation "
                 "shape -- the reason P4 precedes P5"),
    ("P5", "P3", "`P5 SPEC` Contract in: an excluded path never reaches an "
                 "extractor"),
    ("P5", "READERS", "`02`: the libraries a deployment chooses fill P5's "
                      "shapes from outside the part"),
    ("P6", "P4", "`22` §1: P6 reads `Observation` and the P4 store, by "
                 "`observation_key`"),
    ("P7", "P4", "`22` §1: the three context fields exist so §8.4 can redact a "
                 "value without dropping its context"),
    ("P7", "P1", "`02` D2: P7 authors its §8.4 audit record and P1 stores it"),
    ("P9", "P6", "`30` seam ledger P6->P9: `facts.read_surface."
                 "proposal_eligible` and the active fact reads are what seed a "
                 "group"),
    ("P9", "P4", "`P9 SPEC` Contract in: P9 cites `observation_key`"),
    ("P9", "P7", "`P9 SPEC` Contract in: §3.11's sensitivity status reaches "
                 "grouping"),
    ("P10", "P6", "`38` §4: a node's `ExpectedValue` is a P6 fact, and "
                  "`is_destination_eligible` is P6's"),
    ("P10", "P7", "`38` §11.5: `handling_class` arrives from P7 through P10"),
    ("P10", "P3", "`P10 SPEC` Contract in: the person's existing folders come "
                  "from the scan"),
    ("P11", "P9", "`P11 SPEC` Contract in §6.8: a group plan is placed as one "
                  "subject"),
    ("P11", "P6", "`P11 SPEC` Contract in: a destination matches on facts"),
    ("P11", "P7", "`38` §11.5: P11 never re-classifies; it carries P7's class "
                  "and asks P7's own denial predicates"),
    ("RECOGNITION", "P7", "`02` D2: the sensitivity rule set is a deployment's, "
                          "injected into P7, and without one every file is "
                          "`Denied(unclassified)`"),
)

#: The seams the design names that a run does NOT exercise, with the reason each
#: is dark. Asserted ABSENT so that the day one is wired this test goes red and
#: the census in `planning/86-SEAM-CENSUS.md` is updated with it rather than
#: quietly falling out of date. `85` §3 measures the same two causes from the
#: other side -- a mechanism count rather than a seam list.
DARK_SEAMS: tuple[tuple[str, str, str], ...] = (
    ("P7", "P8", "no model transport is wired: `cli.py` passes "
                 "`gate=None, model_client=None, prompt=None` and "
                 "`p8_run_call=None`, so `Gate.release` is never called and "
                 "P8 is reached only to create its tables"),
    ("P8", "P7", "the same absence from the other side"),
    ("P6", "P8", "`30` seam ledger P6->P8: `facts.llm_seam.build_request` has "
                 "no caller while no prompt is ratified"),
    ("P9", "P8", "`30` seam ledger P9->P8: `grouping.p8_seam` is guarded by "
                 "`if p8_run_call is None`"),
    ("P11", "P8", "`38` §6: Site C placement validation needs the same "
                  "transport"),
    ("P11", "P12", "nothing in the product applies a plan: `cli.py` reaches "
                   "`mutation` only for `create_mutation_schema`, and the "
                   "report ends `Nothing was moved.` unconditionally"),
    ("P12", "P13", "P12's execution records reach no review surface because no "
                   "execution happens"),
    ("P13", "P11", "`cli.py` imports only `review_surface.schema` and "
                   "`review_surface.vocabulary`; `report()` stands in for P13 "
                   "(`74` §9)"),
    ("P8", "P2", "`30` seam ledger P8->P2: no stage output is emitted because "
                 "no stage runs a model"),
    ("P9", "P2", "P9 emits no stage output on a live run"),
    ("P11", "P2", "P11 emits no stage output on a live run"),
)


@pytest.fixture(scope="module")
def _census(tmp_path_factory) -> tuple[Counter, dict, str]:
    """One traced run of the whole product, shared by every assertion below.

    Module-scoped because the run is the expensive part and every test here asks
    a different question of the SAME run -- two runs would let two tests
    disagree about what the product did.
    """
    root = tmp_path_factory.mktemp("holder")
    corpus = _corpus(root)
    out = io.StringIO()
    with _SeamRecorder() as recorder:
        code = cli.main(_argv(corpus, root / "plan.sqlite"), out=out)
    assert code == 0, out.getvalue()
    return recorder.edges, recorder.symbols, out.getvalue()


def test_every_seam_the_design_requires_carries_traffic_on_a_real_run(_census):
    """The wiring map, asserted against a run rather than against imports.

    This is the guard `22` §6's six checks could not be: all six read the source
    in one direction, and the seam that actually broke every time was a consumer
    whose producer was never called.
    """
    edges, _symbols, _text = _census
    missing = [f"{a} -> {b}: {why}" for a, b, why in LIVE_SEAMS
               if (a, b) not in edges]
    assert not missing, (
        "a seam the design requires carried no traffic on a real run of "
        "`cli.main`:\n  " + "\n  ".join(missing))


def test_the_dark_seams_are_still_the_ones_the_census_says_they_are(_census):
    """Asserted absent, so wiring one is a red test and not a silent drift.

    A census is only worth writing if it stays true. `planning/86-SEAM-CENSUS.md`
    names each of these and why it is dark; when one lights up, the entry there
    is what has to change, and this is what says so.
    """
    edges, _symbols, _text = _census
    lit = [f"{a} -> {b}: recorded as dark because {why}"
           for a, b, why in DARK_SEAMS if (a, b) in edges]
    assert not lit, (
        "a seam recorded as dark now carries traffic. That is good news and a "
        "stale census: update `planning/86-SEAM-CENSUS.md` and move the entry "
        "into LIVE_SEAMS.\n  " + "\n  ".join(lit))


def test_the_only_thing_a_live_run_asks_of_p8_p12_and_p13_is_a_table(_census):
    """The three parts that are built and connected to nothing.

    Named as its own assertion rather than left inside the dark-seam list
    because the shape matters: these are not parts with a missing edge, they are
    parts whose ONLY contact with a person's run is `CREATE TABLE`. `85` §3
    reaches the same conclusion by counting unreachable mechanisms; this reaches
    it by watching a run.
    """
    _edges, symbols, _text = _census
    assert symbols.get((ROOT, "P8")) is not None, (
        "P8 is not reached at all -- even its schema. That is a different "
        "defect from the one this guards.")
    for part, expected in ((("P8"), {"create_llm_schema", "create_budget_schema",
                                     "__post_init__"}),
                           (("P12"), {"create_mutation_schema"}),
                           (("P13"), {"create_review_schema"})):
        reached = symbols.get((ROOT, part), set())
        assert reached <= expected, (
            f"{part} now does something on a live run beyond creating its "
            f"tables: {sorted(reached - expected)}. Good news and a stale "
            f"census -- update `planning/86-SEAM-CENSUS.md`.")


# --- the dark seams, proved against the records a real run leaves -------------
#
# A dark seam cannot be exercised end to end -- that is what makes it dark. What
# CAN be done, and is worth more than a fixture, is to take the records the
# product actually wrote and hand them to the part that was supposed to receive
# them. That proves the contract holds over real data and localises the fault to
# the missing caller, which is the whole difference between "P12 is broken" and
# "nothing calls P12".


#: The one filesystem answer set that is not P12's to choose (`P12 SPEC`,
#: "Contract in"): a real volume's, supplied here by the test acting as the
#: composition root it does not have. APFS on the machine this runs on.
SENSITIVE_PERSONAL, HIGHLY_SENSITIVE = HANDLING_CLASSES[2], HANDLING_CLASSES[3]

_CONSTRAINTS = FilesystemConstraints(
    unicode_form="NFC", case_sensitive=False, max_component_bytes=255,
    max_path_bytes=1024, prohibited_characters=frozenset({"/", "\x00"}),
    reserved_names=frozenset(), replacement_character="_")


def test_the_place_decisions_a_real_run_writes_are_ones_p12_can_plan(tmp_path):
    """P11 -> P12, over the decisions the product actually made.

    `--send-set` is the one gesture that reaches `outcome = place` with no model
    at all: the answer names the destination, so nothing has to be judged. The
    run then prints *"Ready for you to approve, then file into Reading Inbox"*
    and there is no gesture that files them -- `cli.py` reaches `mutation` only
    for `create_mutation_schema`. This is the seam whose absence a person feels
    most directly, and this test is what says the fault is the missing caller
    and not the contract: every field P12 reads is present and correct on the
    records P11 really wrote.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    first = io.StringIO()
    assert cli.main(_argv(corpus, database), out=first) == 0, first.getvalue()
    second = io.StringIO()
    assert cli.main(_argv(corpus, database)
                    + ["--residual", "Reading Inbox",
                       "--send-set", "Not yet placed=Reading Inbox"],
                    out=second) == 0, second.getvalue()
    report = second.getvalue()
    assert "then file into Reading Inbox" in report, report

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    # The plan version the LAST run minted -- `--send-set` acts on the sets of
    # the run it was typed in (`cli.py`), so an earlier version's decisions are
    # not the ones the person was shown.
    plan_version = conn.execute(
        "SELECT plan_version FROM placement_decisions "
        "ORDER BY rowid DESC LIMIT 1").fetchone()[0]
    decisions = decisions_for_plan(conn, plan_version=plan_version)
    placed = [d for d in decisions if d.outcome == PLACE]
    assert placed, (
        "the run reported files ready to file into a residual area but wrote no "
        "`place` decision, so there is nothing for P12 to plan and the report "
        "is describing something that did not happen")

    nodes = nodes_for_version(conn, plan_version)
    legal = frozenset(node.node_id for node in nodes if node.accepts_placement)
    plans = []
    for decision in placed:
        built = build_plan(
            conn, decision, nodes=nodes, legal_destination_ids=legal,
            cross_folder_moves=True, constraints=_CONSTRAINTS,
            # The anchor map is the composition root's; a run that never applies
            # has never had to supply one, which is part of what is missing.
            high_level_folders={node.root_anchor: corpus.parent
                                for node in nodes if node.root_anchor},
            volume_of=lambda path: "vol-main",
            # §8.4's two sensitive classes, spelled from P7's own vocabulary.
            # P12 refuses a set that is not P7's, which is why this is imported
            # and not typed -- `02` D2: P7 owns the classification.
            protected_handling_classes=frozenset({
                SENSITIVE_PERSONAL, HIGHLY_SENSITIVE}),
            collision_policy=PRESERVE_BOTH_DETERMINISTIC_SUFFIX,
            expiration_state="no expiry configured",
            now=lambda: "2026-09-02T00:00:00Z",
            mint_id=lambda: f"plan-{len(plans)}")
        assert built is not None, (
            f"P12 refused to plan a `place` decision P11 really wrote: "
            f"{decision.decision_id}")
        plans.append(built[0])
    conn.close()

    assert len(plans) == len(placed)
    for plan in plans:
        # §5.12 / §6.2: the decision names a node, never a path, and P12 is the
        # part that composes one. A plan whose destination is not under the
        # anchor would mean the seam had carried a path across it.
        assert plan.resolved_destination_path.startswith(str(corpus.parent))
        assert "Reading Inbox" in plan.resolved_destination_path
        # And nothing was created on disk: building a plan is not applying one.
        assert not (corpus.parent / "Reading Inbox").exists()
