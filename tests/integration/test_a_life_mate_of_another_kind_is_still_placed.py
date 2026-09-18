# tests/integration/test_a_life_mate_of_another_kind_is_still_placed.py
"""`00` amendment 12, the lead's condition of 18 Sep: **in a typed run, a file
site G named as a DIFFERENT KIND inside the SAME LIFE is still placed
somewhere.**

`--situation academic.coursework --label Coursework` over a folder that also
holds an application packet. Site G names the packet `college_applications`
and the level judge names `applications.undergraduate-packet`; its life is
Education, which is the typed situation's life. Before amendment 12 the packet
had a root of its own; `104` §17.2 forbids the rename costing it a home.

**WHAT MAKES IT TRUE, MEASURED.** `106`'s draft rule -- "a typed run keeps its
own LIFE at home" -- put the packet inside `Coursework`, its group was drafted
there in its own kind (`_grouped_by_branch`), and once P11's guard was widened
to what a branch HOLDS the essay was filed into `Coursework/Spring2026/
PHYS1401` because its text names the course: R-23, the thing R-37 exists to
stop. So the partition keeps only the run's own KIND at home
(`branch_situation.partition_by_branch`, `_stays_home`), and the packet is
under `Education` beside the typed branch -- the root of its own it had. That
rule is what this file pins; with it in place the guard's widening is not
load-bearing here (the `Education` branch is single-kind and settled, so the
one-situation map already held the packet), and its pin is
`tests/test_p11_guard_is_keyed_by_the_name_the_root_node_wears.py`. The
integration case the widening IS load-bearing for -- an UNTYPED run whose
`Education` holds coursework and a packet, two situations under one root --
is not written here.

The stubbed cloud is `test_the_judge_names_the_situation.py`'s, aimed by the
one released value that differs per file -- the file's own name.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cli  # noqa: E402
from readers import model_routing  # noqa: E402

from test_each_file_is_filed_under_its_own_situation import (  # noqa: E402
    _names, _released, _the_deterministic_winner,
)
from test_local_model_fact_pass import _answer_for  # noqa: E402
from test_the_judge_names_the_situation import (  # noqa: E402
    BASE_URL_NAME, CREDENTIAL_NAME, ENV, LOCAL_BASE_URL_NAME, LOCAL_MODEL_NAME,
    MODEL_NAME_OF_TIER, _Cloud, _decisions, _is_the_situation_question,
    _plan_version_in, _ratified,
)

SITUATION = "academic.coursework"
LABEL = "Coursework"

#: The word in the packet files' own names that aims the stub, the kind site G
#: names for them, and the situation the level judge names -- one life with
#: the typed coursework. IN THE CORPUS ROOT, not in a folder of their own: a
#: folder the person already made is adopted as a branch and P11's guard leaves
#: it alone, so a packet in one would never reach `Coursework`'s guard at all
#: (measured: with the packet in `Applications/`, every assertion below stayed
#: green with the guard sabotaged, and the chains read `Applications`).
APPLICATION = "application"
KIND = "college_applications"
CHOSEN = "applications.undergraduate-packet"

ROOT_FILES = {
    "PHYS 1401 syllabus.txt":
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n",
    "ECON 2010 syllabus.txt":
        "ECON 2010 Syllabus\n\nFall 2025. Instructor: Dr. Ruiz. Credits: 4.\n",
    "PHYS 1401 homework 3.txt":
        "PHYS 1401 Homework 3\n\nProblem set on projectile motion. Due week 6.\n",
}

#: None of these is a protected kind of record: a protected file is filed by
#: the person and abstains `privacy_blocked` by design, which is not what this
#: pin is about. (A "personal statement" is held by the rules as one.)
PACKET_FILES = {
    "State University application essay.txt":
        "Essay for the State University application.\n"
        "Why I want to study physics, and what the debate society taught me.\n",
    "State University application activities.txt":
        "Activities list for the State University application.\n"
        "Debate society, tutoring, summer research placement.\n",
    "State University application recommendation request.txt":
        "Request for a recommendation letter for the State University "
        "application.\nDr. Lee, PHYS 1401, Spring 2026.\n",
}


class _PacketCloud(_Cloud):
    """The judge names the packet's kind and situation by its folder."""

    def factory(self, **_unused):
        def invoke(payload: bytes) -> bytes:
            self.payloads.append(payload)
            body = self._body(payload)
            site = body["call_site"]
            if site == cli.G_SITUATION_SENSITIVITY:
                where = " ".join(item["value"] for item in _released(body))
                if not _is_the_situation_question(body):
                    return _names(KIND if APPLICATION in where.lower()
                                  else "academic", body).encode("utf-8")
                return _names(CHOSEN, body).encode("utf-8")
            if site == cli.C_PLACEMENT:
                return _the_deterministic_winner(body).encode("utf-8")
            return _answer_for(payload.decode("utf-8")).encode("utf-8")
        return invoke


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in {**ROOT_FILES, **PACKET_FILES}.items():
        (corpus / name).write_text(body)
    return corpus


@pytest.fixture(scope="module")
def typed(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("life_mate")
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    cloud = _PacketCloud()
    out = io.StringIO()
    with pytest.MonkeyPatch.context() as patch:
        for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values(),
                     LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME):
            patch.delenv(name, raising=False)
        patch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")
        for name, value in ENV.items():
            patch.setenv(name, value)
        patch.setattr(model_routing, "deepseek_invoke", cloud.factory)
        _ratified(patch)
        code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                         "--user", "t", "--database", str(database),
                         "--enable-cloud", "--accept-groups"], out=out)
    assert code == 0, out.getvalue()
    return {"corpus": corpus, "database": database, "cloud": cloud,
            "said": out.getvalue(), "plan": _plan_version_in(out.getvalue())}


def _roots(state) -> list[str]:
    conn = sqlite3.connect(f"file:{state['database']}?mode=ro", uri=True)
    try:
        return [row[0] for row in conn.execute(
            "SELECT display_label FROM tree_nodes WHERE plan_version_id = ? "
            "AND parent_node_id IS NULL AND node_type = 'proposed' "
            "ORDER BY ordinal", (state["plan"],))]
    finally:
        conn.close()


def test_the_judge_named_the_packet_another_kind_of_the_same_life(typed):
    """The premise, asserted so the test cannot pass on a corpus where the
    packet was never named: site G was asked and named the packet's kind."""
    kinds = typed["cloud"].kind_calls()
    assert len(kinds) == len(ROOT_FILES) + len(PACKET_FILES), typed["said"]
    assert f"Which of these is {KIND}?" not in typed["said"], typed["said"]


def test_the_packet_is_still_placed_somewhere(typed):
    """THE CONDITION. Not "no exception": every packet file has a destination.

    SABOTAGE: keep every file of the typed LIFE at home in `_stays_home`
    (`106`'s draft rule). Measured with P11's guard at the one-situation grain:
    the packet sits inside `Coursework`, `_only_this_files_own_branch` drops
    every candidate under the only root it has, and the activities file
    abstains `no_supported_destination` -- a file that had a home before the
    rename. Measured with the guard widened instead: the essay is filed into
    `Coursework/Spring2026/PHYS1401` (`test_where_the_six_files_landed`).
    """
    placed, abstained = _decisions(typed)
    for name in PACKET_FILES:
        assert name in placed, (name, abstained.get(name), typed["said"])


def test_the_coursework_files_are_still_placed_too(typed):
    placed, abstained = _decisions(typed)
    for name in ROOT_FILES:
        assert name in placed, (name, abstained.get(name), typed["said"])


def _chain_of_each_file(state) -> dict[str, str]:
    """corpus-relative name -> the destination chain it was placed under."""
    from placement.store import decisions_for_plan
    from tree_design.store import nodes_for_version
    conn = sqlite3.connect(f"file:{state['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        named = {row["file_id"]: str(Path(row["current_path"])
                                     .relative_to(state["corpus"]))
                 for row in conn.execute("SELECT file_id, current_path FROM files")}
        nodes = {node.node_id: node
                 for node in nodes_for_version(conn, state["plan"])}

        def chain(node_id: str) -> str:
            parts: list[str] = []
            while node_id in nodes:
                parts.append(nodes[node_id].display_label)
                node_id = nodes[node_id].parent_node_id
            return "/".join(reversed(parts))

        return {named[d.subject.file_id]: chain(d.destination.node_id)
                for d in decisions_for_plan(conn, plan_version=state["plan"])
                if d.subject.kind == "file" and d.outcome == "place"}
    finally:
        conn.close()


def test_where_the_six_files_landed(typed):
    """WHERE, not only whether. Two bad outcomes `in placed` cannot tell apart:
    a typed `Coursework` FLATTENED by the presence of one packet (a folded area
    with two buildable coverages waits for the person, `nesting_chooser`), or
    a packet file filed INTO a course folder -- R-23, the thing R-37 exists to
    stop. Measured before the partition gave the packet its own branch: the
    essay went to `Coursework/Spring2026/PHYS1401` because its text names the
    course. The chains are printed so the report can quote them."""
    chains = _chain_of_each_file(typed)
    print("CHAINS", sorted(chains.items()))
    for name in ROOT_FILES:
        assert chains.get(name, "").startswith(LABEL), (name, chains)
    # The two syllabi carry a term and a course, so they are the witnesses
    # that the levels were built; the homework names no term and sits at the
    # branch itself, as it does on every run of this shape.
    for name in ("PHYS 1401 syllabus.txt", "ECON 2010 syllabus.txt"):
        assert chains[name].startswith(LABEL + "/"), (
            "the typed coursework branch was flattened", name, chains)
    for name in PACKET_FILES:
        assert name in chains, (name, chains)
        assert not chains[name].startswith(LABEL + "/"), (
            "an application packet was filed inside a course", name, chains)
    assert not any(APPLICATION in chain.lower() for chain in chains.values()), (
        "a packet file's name became a folder", chains)


def test_one_root_wears_the_typed_label(typed):
    """Phase 4's gate at the typed branch: two drafts of one label -- the
    coursework kind's and the packet kind's -- are ONE area, never two roots
    called `Coursework`."""
    roots = _roots(typed)
    assert roots.count(LABEL) == 1, (roots, typed["said"])
