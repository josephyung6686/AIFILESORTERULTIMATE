"""`--shadow`: what the placement row would be if site C's verdicts were applied.

Against SYNTHETIC plan databases built here, and that is a deliberate choice rather
than a convenience. The thing under test is a reading of six situations that a real
run produces one at a time and only with a model configured -- an exact placement, a
right parent with the wrong leaf, a wrong folder, an abstention on a file whose right
answer is "ask the person", a gate refusal, a file site C was never asked about, and a
file labelled as a different situation that the verdict files anyway (spillover).
Waiting for a corpus that happened to produce all six would be waiting for the model
to be non-deterministic in a particular way. Every table here is created by the
PRODUCT's own DDL, so a column that moves breaks this test rather than silently
changing what it measures.

Nothing in this module reads, lists or runs anything under `.groundtruth/`: that is
the owner's own material, and the harness's whole reason for existing is that his
files are not test fixtures.
"""
from __future__ import annotations

# `tools/` is a sibling of `src/`, and `pyproject.toml` puts only `src` on the path.
# Done HERE rather than in a `conftest.py`, for the reason the sibling test modules
# spell out at length: with no `__init__.py` in the tests tree, a `conftest.py` in
# this directory would take the bare name `conftest` away from `tests/p5/conftest.py`,
# whose tests import from it by that name at call time.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import hashlib
import json
import sqlite3
import subprocess

import pytest

from database_agent.db import create_schema
from evidence_shape.schema import create_evidence_schema
from extractors.router import ROUTING_DDL
from facts.schema import create_facts_schema
from llm_harness.schema import create_llm_schema
from placement.schema import create_placement_schema
from privacy.schema import create_privacy_schema
from questions.schema import create_questions_schema
from scan_agent.exclusion import EXCLUSION_DDL
from tree_design.schema import create_tree_schema

from tools.groundtruth.labels import load_labels
from tools.groundtruth.measure import observe_run
from tools.groundtruth.report import per_file_table
from tools.groundtruth.score import (
    NOT_PLACED, PLACED_EXACT, PLACED_PARENT, PLACED_WRONG, score_situation,
    score_sorting,
)
from tools.groundtruth.shadow import (
    NEVER_ASKED, REFUSED, SUBSTITUTED, observed_placements, shadow_block,
    shadow_run, site_tallies,
)

ROOT = Path(__file__).resolve().parents[2]
SITUATION = "academic.coursework"
#: A second shipped situation, for the one measurement no per-file bucket sees:
#: a run answers ONE situation for every file in the folder, and spillover counts
#: what that costs. It has no run of its own here -- the point is what the
#: coursework run did to a file labelled as something else.
OTHER = "code.notebooks-experiments"
CLOCK = "2026-09-07T00:00:00Z"
PLAN = "plan-1"

#: A string that appears ONLY inside the places this instrument must never print:
#: a citation's quoted span, the dossier payload's released excerpt, and a failed
#: call's explanation. `test_groundtruth_payload.py`'s canary idiom, pointed at the
#: three columns `--shadow` touches.
CANARY = "MITOCHONDRIAL-CANARY-8823-DO-NOT-PRINT"

#: The seven labelled files, and what each is here to prove.
EXACT = "Coursework/PHYS 1403 homework 2.txt"
PARENT = "Coursework/PHYS 1403 syllabus.txt"
WRONG = "Coursework/PHYS 1401 exam equations.txt"
ASK = "Loose/logo.svg"
GATE = "Loose/page.html"
UNASKED = "Loose/LICENSE"
SPILL = "Project/main.py"

LABELS = {"files": [
    {"path": EXACT, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1403", "homework"]},
    {"path": PARENT, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1403", "syllabus"]},
    {"path": WRONG, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1401", "exam"]},
    {"path": ASK, "group": "fixture", "situation": SITUATION,
     "destination": None, "uncertain": "a logo with no course anywhere near it"},
    {"path": GATE, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1403", "homework"]},
    {"path": UNASKED, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1403", "homework"]},
    {"path": SPILL, "group": "fixture", "situation": OTHER,
     "destination": ["Project", "source file"]},
]}

#: The folders the run froze. `Coursework` is the top level the run supplies; the
#: labels name what is below it, which is what `score._ends_with` compares.
NODES = {
    "n-root": ("Coursework", None),
    "n-1403": ("PHYS1403", "n-root"),
    "n-1403-hw": ("homework", "n-1403"),
    "n-1403-syl": ("syllabus", "n-1403"),
    "n-1401": ("PHYS1401", "n-root"),
    "n-1401-exam": ("exam", "n-1401"),
}


def _corpus(root: Path) -> Path:
    """Seven empty files. The harness reads the DATABASE; the corpus decides which
    files exist, because a file the product dropped must still reach the card."""
    for relative in (EXACT, PARENT, WRONG, ASK, GATE, UNASKED, SPILL):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    return root


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    for create in (create_schema, create_evidence_schema, create_facts_schema,
                   create_privacy_schema, create_placement_schema,
                   create_tree_schema, create_questions_schema, create_llm_schema):
        create(conn)
    conn.executescript(EXCLUSION_DDL)
    conn.executescript(ROUTING_DDL)
    return conn


def _file_row(conn, file_id: str, corpus: Path, relative: str) -> None:
    conn.execute(
        "INSERT INTO files (file_id, current_path, filename, normalized_filename, "
        "extension, directory_position, volume_id, content_hash, hash_algorithm, "
        "observed_size, observed_timestamps, mime_type, detected_format, scan_state, "
        "extraction_status_by_tier, sensitivity_state) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'sha256', 0, '{}', 'text/plain', 'text', "
        "'included', '{}', 'unknown')",
        (file_id, str(corpus / relative), Path(relative).name,
         Path(relative).name.casefold(), Path(relative).suffix, "0",
         "vol-1", hashlib.sha256(file_id.encode()).hexdigest()))
    conn.execute(
        "INSERT INTO classifications (fact_id, file_id, content_hash, handling_class, "
        "protected, basis, evidence_refs, reliability_state, observed_at) "
        "VALUES (?, ?, ?, 'personal_non_sensitive', 0, 'rule', '[]', 'corroborated', ?)",
        (f"c-{file_id}", file_id, hashlib.sha256(file_id.encode()).hexdigest(), CLOCK))


def _decision(conn, file_id: str, *, outcome: str, node_id: str | None) -> None:
    """One live `placement_decisions` row -- what the run APPLIED."""
    content_hash = hashlib.sha256(file_id.encode()).hexdigest()
    conn.execute(
        "INSERT INTO placement_decisions (record_id, subject_ref, plan_version, "
        "origin_stage, outcome, node_id, created_at, payload) "
        "VALUES (?, ?, ?, 'placement', ?, ?, ?, ?)",
        (f"d-{file_id}", f"file:{file_id}:{content_hash}", PLAN, outcome, node_id,
         CLOCK, json.dumps({"ask": None})))


def _subject(file_id: str) -> str:
    return f"file:{file_id}:{hashlib.sha256(file_id.encode()).hexdigest()}"


def _dossier(conn, dossier_id: str, file_id: str, *, site: str = "C_placement") -> None:
    conn.execute(
        "INSERT INTO llm_dossier (dossier_id, call_site, subject_ref, "
        "eligibility_reason, plan_version, policy_version, reduction_rung, payload, "
        "observed_at) VALUES (?, ?, ?, 'bounded_ambiguity', ?, 'pol-1', 'unreduced', "
        "?, ?)",
        (dossier_id, site, _subject(file_id), PLAN,
         # The dossier payload carries the released excerpts. The canary rides here
         # so a reader of this instrument that widened its SELECT would be caught.
         json.dumps({"released": [{"value": CANARY}]}), CLOCK))


def _response(conn, dossier_id: str, destination: str) -> None:
    body = {"claims": [{
        "claim_ref": "claim-1",
        "payload": {"destination": destination, "per_dimension_support": [],
                    "alternatives": [], "conflicts_considered": [],
                    "support": 2, "next_support": 0,
                    "refinement": "not_applicable"},
        # `cited_span` quotes the file. It is here on purpose: the instrument must
        # take the destination and nothing else out of this object.
        "citations": [{"evidence_ref": "obs-1", "cited_span": CANARY,
                       "why_it_supports": CANARY}],
    }]}
    conn.execute(
        "INSERT INTO llm_response (response_id, dossier_id, response_bytes, model_id, "
        "prompt_fingerprint, release_audit_id, release_id, observed_at) "
        "VALUES (?, ?, ?, 'fixture-model', 'fp-1', 1, 'rel-1', ?)",
        (f"r-{dossier_id}", dossier_id,
         json.dumps(body).encode("utf-8"), CLOCK))


def _verdict(conn, dossier_id: str, *, outcome: str, reasons=()) -> None:
    payload = json.dumps({
        "verdict_id": f"v-{dossier_id}", "dossier_id": dossier_id,
        "claim_ref": "claim-1", "outcome": outcome, "disposition": "unresolved",
        "reasons": list(reasons), "may_propose": False, "requires_review": False,
        # `citations_checked` carries the span the validator matched.
        "citations_checked": [{"evidence_ref": "obs-1", "span": CANARY}],
        "scope": "single_claim", "validator_version": "v-1",
        "policy_version": "pol-1", "plan_version": PLAN}, sort_keys=True)
    conn.execute(
        "INSERT INTO llm_verdict (verdict_id, dossier_id, claim_ref, outcome, "
        "disposition, validator_version, policy_version, plan_version, payload, "
        "observed_at) VALUES (?, ?, 'claim-1', ?, 'unresolved', 'v-1', 'pol-1', ?, "
        "?, ?)",
        (f"v-{dossier_id}", dossier_id, outcome, PLAN, payload, CLOCK))


def _grounding(conn, dossier_id: str, *, site: str = "C_placement") -> None:
    """The row that attributes a REFUSAL to a site.

    A refused call never gets an `llm_dossier` row -- `record_dossier` fires after
    `gate.release` returned -- so this is the only table that can say which site the
    door turned away.
    """
    conn.execute(
        "INSERT INTO llm_grounding_report (report_id, dossier_id, call_site, "
        "model_id, prompt_fingerprint, validator_version, citations_total, "
        "claims_total, reduction_rung, payload, observed_at) "
        "VALUES (?, ?, ?, 'fixture-model', 'fp-1', 'v-1', 0, 0, 'unreduced', '{}', ?)",
        (f"g-{dossier_id}", dossier_id, site, CLOCK))


def _refusal(conn, file_id: str, reason: str) -> str:
    """A gate refusal, addressed the way `harness._persist_refusal` addresses one.

    A refused call never reached a dossier, so `report_for_refusal` addresses it
    `pre-call:{call_site}:{subject_ref}` -- the ONLY record of which file the door
    turned away. Building it any other way here would test a shape the product does
    not write.
    """
    address = f"pre-call:C_placement:{_subject(file_id)}"
    _grounding(conn, address)
    conn.execute(
        "INSERT INTO llm_refusal (refusal_id, dossier_id, payload, observed_at) "
        "VALUES (?, ?, ?, ?)",
        (f"x-{file_id}", address,
         json.dumps({"denied": {"reason": reason, "explanation": CANARY}}), CLOCK))
    return address


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """One corpus, one plan database, seven files, seven answers."""
    base = tmp_path_factory.mktemp("shadow")
    corpus = _corpus(base / "corpus")
    out = base / "out"
    out.mkdir()
    database = out / f"{SITUATION.replace('.', '_')}.sqlite"
    conn = _connect(database)

    for node_id, (label, parent) in NODES.items():
        conn.execute(
            "INSERT INTO tree_nodes (node_id, plan_version_id, origin_node_id, "
            "node_type, display_label, parent_node_id, root_anchor, ordinal, "
            "associated_group_ids, explanation, node_role, accepts_placement, "
            "handling_class) "
            "VALUES (?, ?, ?, 'folder', ?, ?, 'anchor', 0, '[]', '', 'ordinary', 1, "
            "'personal_non_sensitive')",
            (node_id, PLAN, node_id, label, parent))

    ids = {EXACT: "f1", PARENT: "f2", WRONG: "f3", ASK: "f4", GATE: "f5",
           UNASKED: "f6", SPILL: "f7"}
    for relative, file_id in ids.items():
        _file_row(conn, file_id, corpus, relative)

    # WHAT THE RUN APPLIED. Under an unratified prompt every site-C verdict is
    # rewritten to an abstention before P11 sees it, so the deterministic path
    # decided all six: it filed three at the top folder and abstained on three.
    for file_id in ("f1", "f2", "f3"):
        _decision(conn, file_id, outcome="place", node_id="n-root")
    for file_id in ("f4", "f5", "f6", "f7"):
        _decision(conn, file_id, outcome="abstain", node_id=None)

    # WHAT SITE C ANSWERED, and was not allowed to act on.
    _dossier(conn, "dos-1", "f1")
    _response(conn, "dos-1", "n-1403-hw")          # the labelled leaf: exact
    _verdict(conn, "dos-1", outcome="accept_direct")

    _dossier(conn, "dos-2", "f2")
    _response(conn, "dos-2", "n-1403")             # right parent, leaf missing
    _verdict(conn, "dos-2", outcome="accept_context_supported")

    _dossier(conn, "dos-3", "f3")
    _response(conn, "dos-3", "n-1403-syl")         # another course entirely: wrong
    _verdict(conn, "dos-3", outcome="accept_direct")

    _dossier(conn, "dos-4", "f4")                  # the ask-the-person file
    _verdict(conn, "dos-4", outcome="reject",
             reasons=("INVENTED_INSTITUTION", "GENERIC_HUB_ONLY"))

    _refusal(conn, "f5", "unclassified")           # refused at the door

    # f6 has no dossier at all: site C was never asked about it.

    # A file this run's situation does not describe, filed anyway -- what
    # SPILLOVER counts. The applied run abstained on it; the verdict does not.
    _dossier(conn, "dos-7", "f7")
    _response(conn, "dos-7", "n-1403-hw")
    _verdict(conn, "dos-7", outcome="accept_direct")

    conn.commit()
    conn.close()

    labels_path = base / "labels.json"
    labels_path.write_text(json.dumps(LABELS), encoding="utf-8")
    known = frozenset({SITUATION, OTHER})
    labels = load_labels(labels_path, known_situations=known)
    run = observe_run(database, corpus, situation=SITUATION, label="Coursework",
                      promised_levels=("Course", "Kind of work"))
    return {"corpus": corpus, "out": out, "database": database,
            "labels": labels, "labels_path": labels_path, "run": run}


# --- the six cases, one assertion each --------------------------------------

def test_the_run_applied_the_deterministic_answer_and_not_the_model_s(built):
    """The premise. Every applied placement is the top folder or an abstention, so
    any movement in the shadow row is the verdicts and nothing else."""
    run = built["run"]
    assert run.files[EXACT].destination == ("Coursework",)
    assert run.files[ASK].outcome == "abstain"


def test_an_accepted_leaf_reads_exact_in_the_shadow_and_flat_when_applied(built):
    labels, run = built["labels"], built["run"]
    observed = observed_placements(built["database"], built["corpus"])
    shadowed, sources = shadow_run(run, observed)
    assert sources[EXACT] == SUBSTITUTED
    assert shadowed.files[EXACT].destination == ("Coursework", "PHYS1403", "homework")
    assert score_sorting(labels[EXACT], shadowed.files[EXACT]) == PLACED_EXACT
    # And the applied row is unmoved: the shadow must never write back.
    assert run.files[EXACT].destination == ("Coursework",)


def test_an_accepted_parent_with_the_leaf_missing_gets_its_own_bucket(built):
    labels, run = built["labels"], built["run"]
    shadowed, _ = shadow_run(run, observed_placements(built["database"],
                                                      built["corpus"]))
    assert score_sorting(labels[PARENT], shadowed.files[PARENT]) == PLACED_PARENT


def test_an_accepted_node_in_the_wrong_course_is_wrong(built):
    labels, run = built["labels"], built["run"]
    shadowed, _ = shadow_run(run, observed_placements(built["database"],
                                                      built["corpus"]))
    assert score_sorting(labels[WRONG], shadowed.files[WRONG]) == PLACED_WRONG


def test_a_rejected_verdict_on_an_ask_the_person_file_is_the_pass(built):
    """`NOT PLACED` is the right answer for a file whose right answer is a question,
    and the shadow scores it by the same rule the applied row does."""
    labels, run = built["labels"], built["run"]
    shadowed, sources = shadow_run(run, observed_placements(built["database"],
                                                            built["corpus"]))
    assert sources[ASK] == SUBSTITUTED
    assert shadowed.files[ASK].outcome == "abstain"
    assert score_sorting(labels[ASK], shadowed.files[ASK]) == NOT_PLACED
    assert score_situation(shadowed, labels).confident_on_uncertain == 0


def test_a_gate_refusal_carries_the_applied_outcome_and_is_named(built):
    """R-74's direction: a file the door refused takes the deterministic placement
    rather than losing its home, so the shadow carries it and says why."""
    run = built["run"]
    shadowed, sources = shadow_run(run, observed_placements(built["database"],
                                                            built["corpus"]))
    assert sources[GATE] == REFUSED
    assert shadowed.files[GATE] == run.files[GATE]


def test_a_file_site_c_was_never_asked_about_carries_and_is_counted(built):
    run = built["run"]
    shadowed, sources = shadow_run(run, observed_placements(built["database"],
                                                            built["corpus"]))
    assert sources[UNASKED] == NEVER_ASKED
    assert shadowed.files[UNASKED] == run.files[UNASKED]


# --- the block, the table, and the two promises about what it may touch -----

def test_the_block_prints_both_rows_and_says_it_applied_nothing(built):
    block, shadow_runs, sources = shadow_block(
        [built["run"]], [score_situation(built["run"], built["labels"])],
        built["labels"], built["out"], built["corpus"])
    assert "SHADOW" in block
    assert "NOT APPLIED" in block
    assert "SHADOW SORT" in block
    assert "applied:" in block and "shadow:" in block
    # The applied row placed three files at the top folder; the shadow row turns
    # one of them into an exact placement and one into a wrong one.
    assert "0 / 0 / 3 / 0 / 2" in block          # applied: three flat, two abstained
    assert "1 / 1 / 0 / 1 / 2" in block          # shadow: exact, parent, wrong
    assert len(shadow_runs) == 1
    assert sources[EXACT] == SUBSTITUTED


def test_spillover_is_scored_by_the_same_rule_and_moves_with_the_verdicts(built):
    """A run answers one situation for EVERY file in the folder, and no per-file
    bucket notices what that costs. The applied run abstained on the file labelled
    as something else; the site-C verdict files it, so the shadow row shows the
    cost the applied row does not."""
    labels, run = built["labels"], built["run"]
    shadowed, _ = shadow_run(run, observed_placements(built["database"],
                                                      built["corpus"]))
    assert score_situation(run, labels).contaminated == 0
    shadow_score = score_situation(shadowed, labels)
    assert shadow_score.contaminated == 1
    assert shadow_score.contaminated_of == 1
    block, _, _ = shadow_block(
        [run], [score_situation(run, labels)], labels, built["out"],
        built["corpus"])
    assert "spillover 0" in block and "spillover 1" in block


def test_the_block_says_where_each_site_s_answers_died(built):
    block, _, _ = shadow_block(
        [built["run"]], [score_situation(built["run"], built["labels"])],
        built["labels"], built["out"], built["corpus"])
    assert "VERDICTS BY SITE" in block
    assert "C_placement" in block
    assert "accept_direct=3" in block
    assert "reject=1" in block
    assert "INVENTED_INSTITUTION=1" in block
    assert "unclassified=1" in block


def test_the_site_tally_counts_every_terminal_shape(built):
    tallies = {t.site: t for t in site_tallies(built["database"])}
    c = tallies["C_placement"]
    assert c.outcomes == {"accept_direct": 3, "accept_context_supported": 1,
                          "reject": 1}
    assert c.accepted == 4
    assert c.refusals == {"unclassified": 1}
    assert set(c.reasons) == {"INVENTED_INSTITUTION", "GENERIC_HUB_ONLY"}


def test_two_situation_runs_sum_their_site_tallies(built, tmp_path):
    """The shape the lead actually runs: one database per situation.

    A site asked in two runs genuinely produced two sets of answers, so the tally
    SUMS -- unlike every per-file line on the card, which picks one observation per
    file. Untested, this is the line that would quietly report one run's counts for
    a seventeen-run corpus.
    """
    out = tmp_path / "out"
    out.mkdir()
    for situation in (SITUATION, OTHER):
        (out / f"{situation.replace('.', '_')}.sqlite").write_bytes(
            built["database"].read_bytes())
    labels = built["labels"]
    runs = [observe_run(out / f"{s.replace('.', '_')}.sqlite", built["corpus"],
                        situation=s, label="Coursework")
            for s in (SITUATION, OTHER)]
    block, shadow_runs, _ = shadow_block(
        runs, [score_situation(run, labels) for run in runs], labels, out,
        built["corpus"])
    assert len(shadow_runs) == 2
    one = {t.site: t for t in site_tallies(built["database"])}["C_placement"]
    assert f"C_placement  {2 * one.total} answers, {2 * one.accepted} accepted" in block
    assert f"accept_direct={2 * one.outcomes['accept_direct']}" in block
    assert "unclassified=2" in block


def test_the_per_file_table_puts_the_observed_node_beside_the_applied_one(built):
    labels = built["labels"]
    block, shadow_runs, sources = shadow_block(
        [built["run"]], [score_situation(built["run"], labels)], labels,
        built["out"], built["corpus"])
    table = per_file_table([built["run"]], labels, shadow_runs, sources)
    header, *rows = table.splitlines()
    columns = header.split("\t")
    assert columns[-3:] == ["shadow_sorting", "shadow_got", "shadow_source"]
    by_path = {row.split("\t")[0]: row.split("\t") for row in rows}
    exact = by_path[EXACT]
    assert exact[columns.index("got")] == "Coursework"
    assert exact[columns.index("shadow_got")] == "Coursework/PHYS1403/homework"
    assert exact[columns.index("shadow_sorting")] == PLACED_EXACT
    assert by_path[GATE][columns.index("shadow_source")] == REFUSED


def test_without_the_flag_the_table_keeps_exactly_the_columns_it_had(built):
    """No `--shadow` cell reaches a table nobody passed the flag to.

    The last column is `decided_by` and not `family`: `104` R-151 appended
    `review_policy` and R-165 appended this one after it. What this test guards
    against is the FLAG adding columns, and both of those are there whether or not
    the flag is given. The three shadow names are refused BY NAME as well, so a
    column appended later cannot make this pass by accident -- which is why the
    positional assertion is a spelling this test is expected to be edited for
    rather than a promise the writer breaks.
    """
    columns = per_file_table(
        [built["run"]], built["labels"]).splitlines()[0].split("\t")
    assert columns[-1] == "decided_by"
    assert not {"shadow_sorting", "shadow_got", "shadow_source"} & set(columns)


def test_no_file_content_reaches_the_block_or_the_table(built):
    """The canary, in the three columns this instrument comes closest to: the
    dossier payload's released excerpt, a citation's quoted span, and a refusal's
    explanation. None of the three may be printed, and the destination -- one
    identifier out of `allowed_vocabulary` -- is all that may be read."""
    labels = built["labels"]
    block, shadow_runs, sources = shadow_block(
        [built["run"]], [score_situation(built["run"], labels)], labels,
        built["out"], built["corpus"])
    table = per_file_table([built["run"]], labels, shadow_runs, sources)
    assert CANARY not in block
    assert CANARY not in table
    # And the canary really is in the database, so the assertion above is a test.
    conn = sqlite3.connect(built["database"])
    stored = conn.execute("SELECT count(*) FROM llm_dossier WHERE payload LIKE ?",
                          (f"%{CANARY}%",)).fetchone()[0]
    refused = conn.execute("SELECT count(*) FROM llm_refusal WHERE payload LIKE ?",
                           (f"%{CANARY}%",)).fetchone()[0]
    conn.close()
    assert stored == 5 and refused == 1


def test_the_instrument_writes_nothing_to_the_database_it_reads(built):
    """Every connection is `mode=ro`. This is what says so."""
    before = hashlib.sha256(built["database"].read_bytes()).hexdigest()
    shadow_block([built["run"]], [score_situation(built["run"], built["labels"])],
                 built["labels"], built["out"], built["corpus"])
    assert hashlib.sha256(built["database"].read_bytes()).hexdigest() == before


def test_the_shadow_module_reaches_no_model_and_no_socket():
    """The cheapest honest form of "invokes no model, opens no socket": the module
    imports nothing that could. A transport, a client or a socket would have to be
    imported to be used, and this is checked over the source rather than over a run,
    because a run that happens not to call one proves nothing about the next."""
    import ast

    path = ROOT / "tools" / "groundtruth" / "shadow.py"
    source = path.read_text(encoding="utf-8")
    for forbidden in ("socket", "urllib", "http.client", "requests", "anthropic",
                      "openai", "llm_harness.transport", "model_placement",
                      "model_facts"):
        assert f"import {forbidden}" not in source
        assert f"from {forbidden}" not in source
    # `text_units.text` is `complete_extracted_text` and is ALWAYS_LOCAL: the
    # harness needs how many units there are and never what is in them, and this
    # module needs neither. Asserted over the module's own SQL rather than over its
    # prose, because the rule is about what it QUERIES and the docstring above says
    # the table's name in order to promise not to read it.
    statements = [node.value for node in ast.walk(ast.parse(source))
                  if isinstance(node, ast.Constant) and isinstance(node.value, str)
                  and "select " in node.value.lower()]
    assert statements, "no SQL found, so this assertion would pass vacuously"
    for statement in statements:
        assert "text_units" not in statement


def _offline(tmp_path, *, model_tables: bool):
    """A run that asked no model, with and without P8's tables on disk.

    The two are different databases and the difference is the point of the pair
    below: an offline run of TODAY's product has the tables and no rows in them,
    and a database written before P8's schema existed has neither. Both are runs
    a person may point `--score-only` at.
    """
    corpus = _corpus(tmp_path / "corpus")
    out = tmp_path / "out"
    out.mkdir()
    database = out / f"{SITUATION.replace('.', '_')}.sqlite"
    conn = _connect(database)
    if not model_tables:
        for table in ("llm_dossier", "llm_response", "llm_verdict", "llm_refusal",
                      "llm_pre_call_abstention", "llm_call_failure",
                      "llm_grounding_report"):
            # The triggers refuse a DELETE, never a DROP: this is a database that
            # never had the table, not one somebody emptied.
            conn.executescript(f'DROP TABLE IF EXISTS "{table}"')
    _file_row(conn, "f1", corpus, EXACT)
    _decision(conn, "f1", outcome="place", node_id=None)
    conn.commit()
    conn.close()
    labels_path = tmp_path / "labels.json"
    labels_path.write_text(json.dumps(LABELS), encoding="utf-8")
    labels = load_labels(labels_path,
                         known_situations=frozenset({SITUATION, OTHER}))
    run = observe_run(database, corpus, situation=SITUATION, label="Coursework")
    return run, labels, out, corpus


@pytest.mark.parametrize("model_tables", [True, False],
                         ids=["tables present, no rows", "no tables at all"])
def test_a_run_that_asked_no_model_says_so_instead_of_failing(tmp_path, model_tables):
    """An offline run asked site C nothing. That is a MEASUREMENT and not a
    failure, so the block prints it, every file carries, and nothing raises --
    whether P8's tables are there and empty or were never created at all."""
    run, labels, out, corpus = _offline(tmp_path, model_tables=model_tables)
    block, shadow_runs, sources = shadow_block(
        [run], [score_situation(run, labels)], labels, out, corpus)
    assert "0 labelled files carry a site-C verdict" in block
    assert "nothing was asked of any site in these databases" in block
    assert all(word == NEVER_ASKED for word in sources.values())
    assert shadow_runs[0].files == run.files
    assert observed_placements(out / f"{SITUATION.replace('.', '_')}.sqlite",
                               corpus) == {}
    assert site_tallies(out / f"{SITUATION.replace('.', '_')}.sqlite") == ()


def test_score_only_shadow_is_the_command_the_lead_types(built, tmp_path):
    """The whole flag, end to end, over databases a previous run left behind -- and
    with `--score-only`, because re-running the product is the slow part and the
    verdicts are already on disk."""
    out = tmp_path / "out"
    out.mkdir()
    (out / f"{SITUATION.replace('.', '_')}.sqlite").write_bytes(
        built["database"].read_bytes())
    completed = subprocess.run(
        [sys.executable, "-m", "tools.groundtruth",
         "--corpus", str(built["corpus"]), "--labels", str(built["labels_path"]),
         "--out", str(out), "--situation", SITUATION, "--score-only", "--shadow"],
        cwd=ROOT, capture_output=True, text=True)
    assert completed.returncode in (0, 1), completed.stderr
    card = (out / "scorecard.txt").read_text(encoding="utf-8")
    assert "GROUND TRUTH SCORECARD" in card
    assert "SHADOW      OBSERVED SITE-C VERDICTS, NOT APPLIED" in card
    assert "VERDICTS BY SITE" in card
    assert CANARY not in card
    table = (out / "per-file.tsv").read_text(encoding="utf-8")
    assert table.splitlines()[0].endswith("shadow_sorting\tshadow_got\tshadow_source")
    assert CANARY not in table
