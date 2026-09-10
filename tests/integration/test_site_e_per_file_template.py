# tests/integration/test_site_e_per_file_template.py
"""`104` §18.1 S6 and `00`:97 per file: a file the situation's one folder template
does not fit gets a template of its own, and the gate's §7.3 arm reads it.

**WHAT WAS MISSING, in the register's own words.** §18.1 S6: "the protected-records
template denial is unreachable: `template_for` defaults `None` and the composition
root never passes it." §18.6 deferred the wiring and said why -- "`template_for` has
no producer anywhere; the per-file template is site E's answer and E is unratified,
so wiring it today would pass a function that returns `None` for every file, which
is the same dead arm with a different spelling". The owner's ruling of 10 Sep 14:00
is to build the producer now, on the row the product observes today, and S6 goes
live with it.

So there are two claims here and they are pinned apart:

  * the SITE -- which files are asked, what they are asked WITH, where the call may
    go, and what the screen says about all of it. End to end through `cli.main`,
    over the same six-file corpus site A and site G are measured on.
  * the ARM -- `template_for` answers the per-file template for a file with an
    answer and the situation's own template for every other file, and the `Gate`
    the composition root builds is handed it. Pinned without a corpus, because
    "live for one file and inert for another" is a claim about one function and two
    inputs, and a run would measure it through five other decisions.

**NO OLLAMA AND NO NETWORK.** The stub HTTP server of `test_local_model_fact_pass`
speaks the one endpoint `readers.model_ollama` calls and answers from the dossier it
was handed; it is imported rather than copied, exactly as `test_site_g_end_to_end`
imports it, so two stubs cannot drift apart on one protocol.

**THE STUB ANSWERS BY COPYING**, which is the point at this site as at site G: P8
requires every dimension to cite a released reading and requires the quoted span to
appear inside the value the model was shown, so an answer invented here would be
rejected and the test would be measuring the validator instead of the wiring.
"""
from __future__ import annotations

import io
import json
import re
import sqlite3
from pathlib import Path

import pytest

import cli
from model_template import file_fits_its_situation
from privacy.denial import PROTECTED_RECORDS_TEMPLATE
from production import (
    folder_levels_for, group_level_fields_for, load_shipped_catalogue,
    read_packaged_library_file, template_id_for_situation,
)
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from test_local_model_fact_pass import (
    MODEL_ID, PROTECTED_NAME, StubOllama, _answer_for, _corpus, dossier_in,
)
from test_site_g_end_to_end import _situation_answer

SITUATION = "academic.coursework"
LABEL = "Coursework"

#: What the stub designs when it designs anything. A NAME THE RESIDUAL LIBRARY
#: ALREADY CARRIES, because it is the one name the gate's §7.3 arm reacts to: a
#: model that reads a passport and calls the shape it needs "Protected Records" is
#: exactly the case the arm exists for, and any other name would leave the arm
#: pinned only in the negative.
DESIGNED = PROTECTED_RECORDS_TEMPLATE


@pytest.fixture(scope="module")
def catalogue():
    return load_shipped_catalogue(read_packaged_library_file)


# --- the stub ------------------------------------------------------------------

def _template_answer(dossier: dict) -> str:
    """One claim: a template whose single dimension is cited out of released text.

    Deterministic on purpose. A stub that tried to design well would be a second,
    worse P10, and what these tests measure is whether an answer reaches the store
    and the gate -- not whether a language model designs well, which is what
    `tools/promptbench/suites/suite_e.py` measures against authored expectations.
    """
    released = [item for item in dossier.get("released_evidence", ())
                if isinstance(item, dict) and isinstance(item.get("value"), str)
                and item["value"].strip()]
    items = [item for item in dossier.get("evidence_items", ())
             if isinstance(item, dict) and item.get("evidence_ref")]
    vocabulary = [name for name in dossier.get("allowed_vocabulary", ())
                  if isinstance(name, str)]
    if not released or not items or not vocabulary:
        return _template_abstention(dossier)
    ref = items[0]["evidence_ref"]
    shown = next((item for item in released
                  if item.get("observation_key") == ref), released[0])
    name = vocabulary[0]
    payload = {
        "domain": DESIGNED,
        "allowed_fields": [name],
        "fragment_refs": [],
        "dimensions": [{"name": name, "scope": "schema-field",
                        "evidence_ref": shown["observation_key"],
                        "requirement": "required", "metadata_only": False,
                        "order_index": 0}],
        "levels": [{"dimension": name,
                    "retrieval_justification":
                        "this is the word the person would look for it under"}],
        "sensitivity_policy_ref": "policy.personal-default",
        "example_label_chains": [["Example"]],
    }
    return json.dumps({"claims": [{
        "claim_ref": "c1",
        "payload": payload,
        "citations": [{"evidence_ref": shown["observation_key"],
                       "cited_span": shown["value"].strip().splitlines()[0],
                       "why_it_supports": "the dimension rests on this reading"}],
    }]})


def _template_abstention(_dossier: dict) -> str:
    """The shape the drafted text asks for when the model designs nothing."""
    return json.dumps({"claims": [{
        "claim_ref": "c1",
        "unknown": {"insufficiency_statement":
                    "these readings do not say what this file is organised by"}}]})


def _dispatching(template_answer):
    """One answer function for three sites, picked off the dossier's own `call_site`.

    The key exists because `104` §17.1 put every site's name into the model-visible
    bytes; before that a stub could not tell one site's dossier from another's.
    """
    def answer(payload: str) -> str:
        dossier = dossier_in(payload)
        site = dossier.get("call_site")
        if site == cli.G_SITUATION_SENSITIVITY:
            return _situation_answer(dossier)
        if site == cli.E_TEMPLATE:
            return template_answer(dossier)
        return _answer_for(payload)
    return answer


class _Run:
    """One `cli.main` over the six-file corpus, kept so several tests read it.

    MODULE-SCOPED because a run is twenty-five seconds and every test below asks a
    different question of the SAME run; six corpora would let one test drift into
    measuring a different six files from its neighbour.
    """

    def __init__(self, database: Path, report: str, prompts: tuple[str, ...]):
        self.database = database
        self.report = report
        self.prompts = prompts

    def rows(self, sql: str, *params) -> list[sqlite3.Row]:
        conn = sqlite3.connect(f"file:{self.database}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    def dossiers_at(self, call_site: str) -> list[dict]:
        return [dossier for dossier in
                (dossier_in(prompt) for prompt in self.prompts)
                if dossier.get("call_site") == call_site]

    def roster(self) -> list[sqlite3.Row]:
        return self.rows("SELECT file_id, filename, content_hash FROM files")

    def subjects_at(self, call_site: str) -> set[str]:
        """The FILE IDS site `call_site` built a dossier about, read from the store.

        Off the stored row rather than off the model-visible bytes, because
        `subject_ref` crosses the wire as a handle (`104` R-14) and a test matching
        handles would be asserting about the digest rather than about the file.
        """
        return {row["subject_ref"] for row in self.rows(
            "SELECT subject_ref FROM llm_dossier WHERE call_site = ?", call_site)}


def _run(tmp_path_factory, template_answer, name: str) -> _Run:
    corpus = _corpus(tmp_path_factory.mktemp(name))
    database = corpus.parent / "plan.sqlite"
    with StubOllama(answer=_dispatching(template_answer)) as stub:
        import os

        previous = {key: os.environ.get(key)
                    for key in (LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME)}
        os.environ[LOCAL_MODEL_NAME] = MODEL_ID
        os.environ[LOCAL_BASE_URL_NAME] = stub.base_url
        try:
            out = io.StringIO()
            code = cli.main(
                [str(corpus), "--situation", SITUATION, "--label", LABEL,
                 "--user", "t", "--database", str(database)], out=out)
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    assert code == 0, out.getvalue()
    return _Run(database, out.getvalue(), tuple(stub.prompts()))


@pytest.fixture(scope="module")
def answered(tmp_path_factory) -> _Run:
    """The run where the model designs a template for every file it is asked about."""
    return _run(tmp_path_factory, _template_answer, "answered")


@pytest.fixture(scope="module")
def abstained(tmp_path_factory) -> _Run:
    """The same run with a model that designs nothing."""
    return _run(tmp_path_factory, _template_abstention, "abstained")


# --- which files are asked -----------------------------------------------------

def test_a_file_whose_facts_fit_its_situation_is_never_asked_for_a_template(
        answered, catalogue):
    """`00`:110 at this site: the model is not called for what the rules settled.

    A file whose accepted facts fill every required level the product asks it, and
    which states nothing that would need a folder the situation does not have, is
    already served by the template its situation names. Asking a model to design a
    second one for material the first already expresses is the level `00`:99 warns
    about -- a dimension that does not materially improve retrieval -- bought with a
    model call.

    THE FIT TEST IS ASKED OF THE PRODUCT'S OWN FUNCTION over the run's own database,
    not restated here. A predicate written twice is a predicate that can disagree
    with itself, and the assertion that matters is the one about the SITE: exactly
    the files that do not fit are the files site E built a dossier about.
    """
    asked = answered.subjects_at(cli.E_TEMPLATE)
    levels = folder_levels_for(catalogue, SITUATION)
    group_levels = group_level_fields_for(catalogue, SITUATION)

    conn = sqlite3.connect(f"file:{answered.database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        fitting = {row["file_id"] for row in answered.roster()
                   if file_fits_its_situation(
                       conn, file_id=row["file_id"],
                       content_hash=row["content_hash"], folder_levels=levels,
                       group_level_fields=group_levels)}
    finally:
        conn.close()

    assert fitting, (
        "no file in this corpus fits its situation, so this test would pass on a "
        "run that asked about everything and would be measuring nothing")
    assert not (fitting & asked), (
        f"{sorted(fitting & asked)} fit the situation's folders and were asked for "
        "a template of their own anyway")


def test_a_file_that_does_not_fit_is_asked_once_with_its_facts_and_the_levels(
        answered, catalogue):
    """The dossier a file that does not fit is asked FROM, read off the bytes sent.

    Three things have to be in it and each is a different failure if it is not: the
    situation's own folder levels, because a model cannot say what is missing
    without being shown what is there; the file's own readings, because `00`:97
    forbids a template invented from nothing; and the schema's closed vocabulary,
    which is what P8 classifies every proposed dimension name against.

    ONCE per file, and that is `00`:257's budget rather than a preference: this site
    asks one call per unfitting file and a second call about one file would be a
    slot another file needed.
    """
    dossiers = answered.dossiers_at(cli.E_TEMPLATE)
    assert dossiers, (
        "no dossier was built at site E, so no file was asked for a template of "
        "its own and `template_for` has the producer `104` §18.6 says it has not")
    assert len(dossiers) == len(answered.subjects_at(cli.E_TEMPLATE)), (
        "one file was asked twice at a site that asks one call per file")

    expected = [{"field": level.field, "label": level.label,
                 "requirement": level.requirement}
                for level in folder_levels_for(catalogue, SITUATION)]
    for dossier in dossiers:
        assert dossier["folder_levels"] == expected, (
            "the model was asked to design folders for a file without being shown "
            "the folders the situation already builds")
        assert dossier["evidence_items"], (
            "`00`:97 forbids a template invented from nothing, so a call with no "
            "reading to design from should never have been built")
        assert dossier["released_evidence"], (
            "every dimension has to cite a released reading and none was released")
        assert dossier["allowed_vocabulary"], (
            "P8 classifies a proposed dimension name against this closure, and an "
            "empty one makes every name template-local by default")


# --- the arm ------------------------------------------------------------------

def test_an_accepted_answer_is_the_template_that_file_is_held_under(catalogue):
    """`104` §18.1 S6, the live half: the arm reads the model's own answer.

    `Gate._template_for` is the §7.3 denial's only input and the composition root
    passed nothing, so the arm could not fire for any file however the run went.
    This is the resolver that answers it, and for a file site E designed a template
    for the answer is that template.
    """
    designed = cli.TemplatePass(chosen={"f-1": DESIGNED}, fits=0,
                                nothing_to_read=0, abstained=0, no_route=0)
    resolver = cli.template_resolver(
        catalogue, pass_of=lambda: designed,
        situation_of=lambda _file_id: SITUATION)

    assert resolver("f-1") == DESIGNED


def test_an_abstention_leaves_the_file_under_its_situations_own_template(
        catalogue):
    """`104` §18.1 S6, the inert half -- and INERT is not the same as absent.

    A file no model designed a template for is not a file with no template. It is a
    file under the one the person's situation builds, read off the same applicability
    row `folder_levels_for` reads its levels off. That is what makes the arm
    truthfully quiet rather than merely unwired: the resolver answers a real name,
    and no shipped situation is named `Protected Records`.
    """
    designed = cli.TemplatePass(chosen={"f-1": DESIGNED}, fits=0,
                                nothing_to_read=0, abstained=1, no_route=0)
    resolver = cli.template_resolver(
        catalogue, pass_of=lambda: designed,
        situation_of=lambda _file_id: SITUATION)

    assert resolver("f-2") == template_id_for_situation(catalogue, SITUATION)
    assert resolver("f-2") != DESIGNED

    nothing_asked = cli.template_resolver(
        catalogue, pass_of=lambda: cli._NO_TEMPLATE_ASKED,
        situation_of=lambda _file_id: SITUATION)
    assert nothing_asked("f-1") == template_id_for_situation(catalogue, SITUATION)


def _gate_for(conn, catalogue, template_for):
    """The composition root's OWN gate, built the way `cli.run` builds it.

    Through `fact_call_authorities` and not beside it, because §18.1 S6's finding is
    about that function: "the composition root never passes it". A `Gate` assembled
    here would pin a keyword nothing in the product supplies.
    """
    from llm_harness.transport import ModelClient
    from privacy.release import ModelTarget
    from readers.model_ollama import LOCAL as LOCAL_LOCALITY, PROVIDER
    from readers.model_routing import FAST, LOGIC, REASONING, TierRouting

    target = ModelTarget(locality=LOCAL_LOCALITY, model_id="qwen3:8b",
                         provider=PROVIDER, context_tokens=32768)
    client = ModelClient(model_target=target,
                         invoke=lambda payload: b'{"claims": []}')
    routing = TierRouting(
        tier_of_call_site=cli.TIER_OF_CALL_SITE,
        client_of_tier={tier: client for tier in (REASONING, LOGIC, FAST)})
    return cli.fact_call_authorities(
        conn, routing=routing, scan_run_id="scan", corpus_file_count=1,
        policy_version="policy", wire_handle_key=bytes(32), schema="academic",
        folder_levels=folder_levels_for(catalogue, SITUATION), user_id="t",
        now=lambda: "2026-09-10T00:00:00+00:00",
        template_for=template_for).gate


def test_the_release_every_site_goes_through_reads_the_per_file_template(
        catalogue):
    """S6, spent: the §7.3 denial is reachable, and it is reachable per file.

    **"The release and placement consult it" is ONE claim, because there is one
    door.** `fact_call_authorities` builds the only `Gate` this product has and
    every site is handed that object -- site A's stage, site B's observe call, site
    C's and D's placement injections (`cli.observe_placement_injections` passes
    `fact_authorities.gate`), site G's pass and site E's own. So handing the
    resolver to that gate is what puts the per-file template in front of every
    release any of them makes, and `src/placement/` reads nothing and needs no edit.

    Two files, two answers, one gate: the file site E designed `Protected Records`
    for is refused its own filename on a LOCAL target, and the file under its
    situation's own template is not refused for that reason. Before this the second
    answer was the only one possible, whatever a model had said.
    """
    from privacy.denial import Denied
    from privacy.items import Excerpt
    from privacy.policy import Policy, UNSET_POLICY_VERSION, set_policy
    from privacy.release import ModelTarget

    from p7.test_p7_release import SPAN, _classify, _evidence, _file, _request

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cli._bootstrap(conn)

    held = _file(conn, "passport.pdf", "hash-passport")
    ordinary = _file(conn, "homework.pdf", "hash-homework")
    held_key = _evidence(conn, held, "hash-passport")
    ordinary_key = _evidence(conn, ordinary, "hash-homework")
    # THE RUN'S OWN PLAN VERSION, because the gate reads the policy under the one it
    # was built with and `fact_call_authorities` builds it with `cli.PLAN_VERSION`.
    set_policy(conn, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="local_model",
        consent_grants=(), redaction_settings={},
        automatic_move_permissions={}, plan_version=cli.PLAN_VERSION,
        set_at="2026-09-10T00:00:00+00:00"),
        component_version=cli.COMPONENT_VERSION, user_id="t",
        reason="the arm's pin needs a policy in force")
    for file_id, digest in ((held, "hash-passport"), (ordinary, "hash-homework")):
        _classify(conn, file_id, digest,
                  handling_class="sensitive_personal", protected=False)

    designed = cli.TemplatePass(chosen={held: DESIGNED}, fits=1,
                                nothing_to_read=0, abstained=0, no_route=0)
    gate = _gate_for(conn, catalogue, cli.template_resolver(
        catalogue, pass_of=lambda: designed,
        situation_of=lambda _file_id: SITUATION))
    local = ModelTarget(locality="local", model_id="qwen3:8b",
                        provider="on-device")

    refused = gate.release(_request(
        items=(Excerpt(observation_key=held_key, span=SPAN, reason="heading"),),
        model_target=local, file_ids=(held,), stage="residual"))
    assert isinstance(refused, Denied), (
        "the model designed `Protected Records` for this file and the gate "
        "released a reading of it anyway, which is `104` §18.1 S6's dead arm")
    assert refused.reason == "protected_records_template"

    other = gate.release(_request(
        items=(Excerpt(observation_key=ordinary_key, span=SPAN,
                       reason="heading"),),
        model_target=local, file_ids=(ordinary,), stage="residual"))
    assert not (isinstance(other, Denied)
                and other.reason == "protected_records_template"), (
        "a file under its situation's own template was refused as though it were "
        "under the residual Protected Records template, so the arm is not inert "
        "for the files it should be inert for")
    conn.close()


# --- protected material --------------------------------------------------------

def test_a_protected_file_is_asked_on_this_device_or_not_asked_at_all(answered):
    """The standing rule, at a new site: nothing about a protected file leaves.

    `104` §18.7 routes a protected file to the LOCAL model and `target_for` asks the
    gate's own `protected_cloud_denies` for it, so the two outcomes open to one at
    this site are a call on this machine and no call. Site E's text is a draft
    besides, so `require_observe_locality` refuses any target off this device for
    every file, protected or not.

    Read off the model target the request was addressed to, which is the field the
    bytes actually followed.
    """
    protected = next(row["file_id"] for row in answered.roster()
                     if row["filename"] == PROTECTED_NAME)
    assert protected, "the corpus lost its protected file and this measures nothing"

    localities = {row["locality"] for row in answered.rows(
        "SELECT DISTINCT json_extract(model_target, '$.locality') AS locality "
        "FROM release_ledger")}
    assert localities and localities <= {"local"}, (
        f"something was released to {sorted(localities)} on a run whose only "
        "configured model is on this device")

    # Whether the protected file was asked or withheld, no site-E dossier may carry
    # a filename or a path: those are §8.4's always-local set, and at a site whose
    # whole subject is how a person's folders should be shaped they are the most
    # tempting evidence in the store.
    for dossier in answered.dossiers_at(cli.E_TEMPLATE):
        for item in dossier.get("released_evidence", ()):
            assert item.get("zone") not in ("filename", "path"), (
                "a template call carried the evidence about where a file already "
                "is, which may never leave the device")


# --- the sentences -------------------------------------------------------------

def test_the_report_says_how_many_files_were_asked_answered_and_abstained(
        answered):
    """`104` §18.2 gap 9's rule at a new site: a counter no screen prints is a
    number this product silently drops.

    The block names how many files were asked and how many were given a template,
    then gives every counter its own line with its own reason -- and the five lines
    are an arithmetic a person can check against the roster, which is why the zeros
    print too.
    """
    report = answered.report
    assert "Templates of their own:" in report, (
        "the per-file template site ran and no line of the report says so")
    for phrase in ("already fit", "not asked, nothing to read",
                   "asked and left alone", "no target", "out of time"):
        assert phrase in report, f"no line of the report says {phrase!r}"

    block = report.split("Templates of their own:", 1)[1]
    counts = [int(line.split()[0]) for line in block.splitlines()
              if line.startswith("  ") and line.strip()[:1].isdigit()][:5]
    assert len(counts) == 5, (
        f"the block prints {len(counts)} counters and the record has five")

    # Flattened before it is read, because `textwrap.fill` decides where the
    # header's own words break and a regex that depended on that would be a test
    # of the terminal width.
    flat = " ".join(report.split())
    header = re.search(r"Templates of their own: (\d+) of (\d+) file", flat)
    given = re.search(r"and (\d+) (?:was|were) given one", flat)
    assert header and given, f"the header does not name its own numbers: {flat[:400]}"
    asked, walked = int(header.group(1)), int(header.group(2))
    answered_count = int(given.group(1))

    assert walked == len(answered.roster())
    # THE ARITHMETIC A PERSON CAN CHECK. The five counters and the files that were
    # given a template partition the roster, so a file that is in none of them is a
    # file this run decided nothing about and said nothing about either.
    assert sum(counts) + answered_count == walked, (
        f"{counts} + {answered_count} != {walked}; a file the pass walked is on no "
        "line of the block")
    assert asked == answered_count + counts[2], (
        "the header says a different number of files were asked than the answered "
        "and abstained lines account for")


def test_a_model_that_designs_nothing_leaves_every_file_where_it_was(abstained):
    """`00`: "Correct abstention is a successful outcome."

    A run where the model designs no template writes no per-file template at all, so
    every file stays under the one its situation names and the gate's arm stays
    inert for the whole corpus. The site still ran, and the screen still says so --
    which is the difference `_NO_TEMPLATE_ASKED` exists to keep: a run where site E
    was not asked and a run where it was asked and designed nothing must not read
    the same.
    """
    assert abstained.dossiers_at(cli.E_TEMPLATE), (
        "the site was never asked, so nothing abstained and this measures nothing")
    accepted = abstained.rows(
        "SELECT v.outcome FROM llm_verdict v JOIN llm_dossier d "
        "ON d.dossier_id = v.dossier_id WHERE d.call_site = ? "
        "AND v.outcome LIKE 'accept%'", cli.E_TEMPLATE)
    assert accepted == [], (
        "a model that designed nothing produced an accepted template")
    assert "Templates of their own:" in abstained.report
