# tests/integration/test_a_fact_revalidates_under_a_new_validator.py
"""`104` R-127: a validator or normaliser change re-judges the answers it reuses.

`105` §14.7 in the owner's words: *"The reuse identity (`model_facts.py`) includes
the prompt and schema fingerprints; validator or normalisation changes must
re-evaluate cached responses rather than retain obsolete verdicts, and this must be
verified."* R-109 built the reuse and this is what it left open -- the identity is
computed from the question's context, and the code that READ the answer is not part
of that context, so a verdict recorded before R-119 taught the validator that an
empty value is an abstention went on suppressing the same question under a
conclusion the validator no longer reaches.

**Re-judged, never re-asked.** The stored response is the model's and it did not
change; only the reading of it did. So every test here counts model calls, and the
number after a validator change is zero. Widening `CALL_IDENTITY_DIMENSIONS` would
have bought the same answer again for every validator edit, which is why
`call_identity`'s own comment about what the key is for stays true.

**Everything is real except the two model seams**, as in
`test_a_fact_reuse_after_a_verdict.py`, whose corpus and plumbing this file reuses
deliberately: the same two files, the same rejecting answer, the same production
`cli.run`. The only thing these tests add is a change to the judge between two runs.

**AND A LOCAL MODEL IS NOW PART OF THE DEPLOYMENT, `00` amendment 7(c).** This file
configured a cloud key and nothing else, and that stopped being a deployment site A
can run in: the gate, `cli.ask_the_gate`, reads every un-held file on this device
BEFORE anything about it may be sent, `cli.CLOUD_CLEARING_BASES` is what
`model_route_permitted` asks for a cloud target, and the rules' own word is no
longer among them. With no local model the gate has no destination, no file is
cleared, and site A is refused the cloud for every one of them -- so this file's
first run recorded no verdicts at all and the pins about re-judging them had
nothing to re-judge. The local half is `StubOllama`, answering the gate
`none_of_these` and declining the situation, exactly as
`test_a_fact_reuse_after_a_verdict` does and for its reasons.

**THE GATE IS JUDGED BY THE SAME JUDGE, and that is what moved the counts.** A
`_bump` of `VALIDATOR_VERSION` re-judges every verdict the deployment's Site A
validator wrote, which since amendment 7(c) is the gate's as well as site A's. So
the supersession counts and the reuse counts below are read AT SITE A, through
`llm_dossier.call_site`, which `_A_FACT_VERDICTS` was already doing for site C's
sake one ruling earlier.
"""
from __future__ import annotations

import io
import json
import pathlib
import sqlite3
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from llm_harness import fact_validation  # noqa: E402
from readers import model_routing  # noqa: E402
from readers.model_routing import MODEL_NAME_OF_TIER  # noqa: E402
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME  # noqa: E402
from llm_harness.vocabulary import (  # noqa: E402
    A_FACT, C_PLACEMENT, G_SITUATION_SENSITIVITY, H_RESTRICTED_KIND,
)
from readers.model_ollama import (  # noqa: E402
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
# The two local sites' answers come from the files that own them, imported rather
# than copied on `test_site_e_reuses_its_answer`'s own rule: one stub speaking one
# protocol, so this file and the gate's own pins cannot drift into describing two
# different gates.
from test_local_model_fact_pass import (  # noqa: E402
    MODEL_ID, StubOllama, _answer_for, dossier_in,
)
from test_site_g_end_to_end import _decline  # noqa: E402
from test_site_h_gate import _clear  # noqa: E402

SITUATION = "academic.coursework"

CORPUS = {
    "reading notes.txt":
        "Notes on the assigned reading for this seminar. The lecture covered the "
        "textbook chapters on momentum and energy, and the homework is due "
        "Thursday.\n",
    "week two notes.txt":
        "Second week of the course. Notes from the tutorial on aggregate demand, "
        "with the problem set questions the instructor assigned.\n",
}

ENV = {
    CREDENTIAL_NAME: "sk-not-a-real-key",
    BASE_URL_NAME: "https://api.example",
    MODEL_NAME_OF_TIER["reasoning"]: "a-reasoner",
    MODEL_NAME_OF_TIER["logic"]: "a-logician",
    MODEL_NAME_OF_TIER["fast"]: "a-sprinter",
}

#: A supported claim citing nothing: `CITATION_NOT_FOUND`, outcome `reject`. The
#: field stays open, so it is still in the second run's question and still what the
#: reuse decision is measured on.
UNCITED = "Something the evidence does not carry"


class _Socket:
    """Every model call this run makes. Counting `invoke` counts model calls.

    **COUNTED PER CALL SITE, and `104` §17.13 ruling 3 is why.** These tests were
    written when this corpus produced exactly one model call per file and a total
    was therefore an A_fact total. Site C was `ratified_local` then, this
    deployment configures no local model, and C reached no socket. §17.13 moved C
    `eliminate-v2` to `ratified` and R-170 made the route per FILE, so a run with
    `--enable-cloud` now sends a `C_placement` dossier for every file P11 proposes
    a folder for -- one call on this two-file corpus, through the same stubbed
    `deepseek_invoke`. A bare `len(socket)` counts it, and every pin here would
    then be measuring placement rather than the thing it names.

    R-127 and R-109 are about site A: the fact pass records an `llm_call_identity`
    per call and reuses an answer whose identity is unchanged. `C_placement`
    records no identity (`llm_call_identity` holds two rows to the dossier table's
    three), so it is outside that reuse and asks again on every run. That is not
    hidden here -- each test that counts A's savings also counts C's repetition,
    so the day placement joins the reuse the pin goes red and says so.
    """

    def __init__(self) -> None:
        self.payloads: list[bytes] = []

    def __len__(self) -> int:
        return len(self.payloads)

    def calls_at(self, call_site: str) -> int:
        """How many calls this run made at ONE site."""
        return sum(1 for payload in self.payloads
                   if self._body(payload)["call_site"] == call_site)

    def subjects_at(self, call_site: str) -> list[str]:
        return [self._body(payload)["subject_ref"] for payload in self.payloads
                if self._body(payload)["call_site"] == call_site]

    def subjects(self) -> list[str]:
        return [self._body(payload)["subject_ref"] for payload in self.payloads]

    @staticmethod
    def _body(payload: bytes) -> dict:
        text = payload.decode("utf-8")
        return json.loads(text.split("The dossier follows.", 1)[1])

    def factory(self, **_unused):
        def invoke(payload: bytes) -> bytes:
            self.payloads.append(payload)
            body = self._body(payload)
            # SITE G ARRIVES HERE TOO since `00` amendment 7(c): a file the gate
            # CLEARED may have its situation asked off the device, so the cloud seam
            # sees a situation dossier whose schema is not site A's. Answering it in
            # site A's shape would be a malformed claim the validator refuses -- the
            # same silence, reached by a fault -- so it is declined in the shape the
            # ratified prompt asks for.
            if body["call_site"] == G_SITUATION_SENSITIVITY:
                return _decline(body).encode("utf-8")
            return json.dumps({"claims": [
                {"payload": {"field": field, "value": UNCITED}, "citations": []}
                for field in body["allowed_vocabulary"]]}).encode("utf-8")
        return invoke


@pytest.fixture()
def socket(monkeypatch):
    recorder = _Socket()
    monkeypatch.setattr(model_routing, "deepseek_invoke", recorder.factory)
    return recorder


@pytest.fixture(autouse=True)
def _no_ambient_key(monkeypatch, tmp_path):
    """The developer's own key must not decide whether these tests pass.

    The local model's two names are cleared for the same reason and it is not a
    formality: a machine with ollama running would answer the gate with whatever it
    pulled, and these counts would then depend on a model nobody chose here.
    `_local_model` puts the stub's own names back.
    """
    for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values(),
                 LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")
    for name, value in ENV.items():
        monkeypatch.setenv(name, value)


def _local_answer(payload: str) -> str:
    """The local half of the deployment, dispatched on the dossier's own site.

    `test_site_h_gate._dispatching` in shape, with site G declined rather than
    answered for the reason in this file's own header.
    """
    dossier = dossier_in(payload)
    site = dossier.get("call_site")
    if site == H_RESTRICTED_KIND:
        return _clear(dossier)
    if site == G_SITUATION_SENSITIVITY:
        return _decline(dossier)
    return _answer_for(payload)


@pytest.fixture(autouse=True)
def _local_model(monkeypatch, _no_ambient_key):
    """A local model for the whole test, because a run now needs one to send.

    AUTOUSE AND PER TEST, beside `_no_ambient_key` and for its reason: this is what
    the deployment IS since amendment 7(c), not something one pin arranges. One
    server for the test rather than one per run -- every test here runs the product
    two or three times over one corpus, and a stub that came and went between them
    would give the later runs a different base URL from the first.
    """
    with StubOllama(answer=_local_answer) as stub:
        monkeypatch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
        monkeypatch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
        yield stub


@pytest.fixture()
def corpus(tmp_path):
    folder = tmp_path / "holder" / "corpus"
    folder.mkdir(parents=True)
    for name, body in CORPUS.items():
        (folder / name).write_text(body)
    return folder


def _run(corpus) -> str:
    out = io.StringIO()
    cli.main([str(corpus), "--situation", SITUATION, "--label", "Coursework",
              "--user", "jy", "--database", str(corpus.parent / "plan.sqlite"),
              "--accept-groups",
              "--enable-cloud"], out=out)
    return out.getvalue()


def _rows(corpus, sql, *params):
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, params)]
    finally:
        conn.close()


#: `llm_verdict` holds every site's judgements and these tests are about ONE.
#: `104` §17.13 ruling 3 gave site C a cloud route, so a run of this corpus now
#: writes `C_placement` verdicts beside site A's -- judged by P8's own validator
#: (`P8/0.1.0`), untouched by R-127's re-judgement, and rewritten on every run
#: because placement records no `llm_call_identity` to reuse. Unfiltered, the
#: `after == {judgement_version(...)}` pin below reads two versions where the
#: fact pass has one, and `_standing(corpus) == before` compares a set that has a
#: fresh placement verdict in it. The join is to `llm_dossier.call_site`, which is
#: the record of which site asked, rather than to the validator version, which is
#: the thing under test.
_A_FACT_VERDICTS = (
    "SELECT v.verdict_id AS verdict_id, v.claim_ref AS claim_ref, "
    "v.outcome AS outcome, v.validator_version AS validator_version "
    "FROM llm_verdict v JOIN llm_dossier d ON d.dossier_id = v.dossier_id "
    "WHERE v.superseded_by IS NULL AND d.call_site = ? ORDER BY v.verdict_id")


def _standing(corpus):
    return _rows(corpus, _A_FACT_VERDICTS, A_FACT)


def _supersessions(corpus):
    return _rows(
        corpus,
        "SELECT s.* FROM llm_verdict_supersession s "
        "JOIN llm_verdict v ON v.verdict_id = s.old_verdict_id "
        "JOIN llm_dossier d ON d.dossier_id = v.dossier_id "
        "WHERE d.call_site = ?", A_FACT)


def _superseded_at(corpus, call_site):
    """The verdicts ONE site no longer stands behind.

    The same scoping `_A_FACT_VERDICTS` makes for site C, applied to the site `00`
    amendment 7(c) added: the gate's verdicts are written by the deployment's Site A
    validator too, so a `_bump` re-judges them beside site A's and an unscoped read
    of `superseded_by IS NOT NULL` counts two sites' corrections as the fact pass's.
    """
    return _rows(
        corpus,
        "SELECT v.verdict_id AS verdict_id, v.superseded_by AS superseded_by, "
        "v.supersede_reason AS supersede_reason FROM llm_verdict v "
        "JOIN llm_dossier d ON d.dossier_id = v.dossier_id "
        "WHERE v.superseded_by IS NOT NULL AND d.call_site = ?", call_site)


def _reuses_at(corpus, call_site):
    """Questions this run did not ask again AT ONE SITE.

    `llm_call_reuse` is every site's savings in one table, and since `00` amendment
    7(c) the gate saves in it too (45d36ca0). An unscoped count would move when the
    gate started reusing without site A having reused anything at all -- which is
    precisely the reading R-127's pins must not make.
    """
    return _rows(corpus, "SELECT * FROM llm_call_reuse WHERE call_site = ?",
                 call_site)


def _bump(monkeypatch, marker: str) -> None:
    """Change the validator's version the way a validator change changes it.

    `VALIDATOR_VERSION` is a digest of the three modules that decide a Site A
    verdict, so an edit to any of them moves it. A test cannot edit its own
    source mid-run, and patching the module global is the same event: both the
    stamp `validate_fact_proposal` writes and the comparison
    `model_facts._reuse_is_current` makes read this one name at call time, so the
    two never disagree about what the current version is. Patching only one of
    them would test a fixture, not the rule.
    """
    monkeypatch.setattr(
        fact_validation, "VALIDATOR_VERSION",
        f"{fact_validation.VALIDATOR_VERSION}+{marker}")


# --- the defect itself ------------------------------------------------------------


def test_a_validator_change_re_judges_the_stored_response_without_a_call(
        corpus, socket, monkeypatch):
    """R-127 in one number: two fact calls, a new validator, and still two.

    Before the fix the second run reused the first validator's rejections as they
    stood; there was no supersession row in the database and no way to tell a
    verdict this validator would reach from one it would not.

    **The number is site A's, per `104` §17.13 ruling 3** -- see `_Socket`. Site C
    sends a placement dossier of its own on every run under `--enable-cloud`, and
    it is counted here rather than folded into a total that would then move
    whenever placement did.
    """
    _run(corpus)
    first = socket.calls_at(A_FACT)
    assert first == len(CORPUS), socket.subjects()
    placements = socket.calls_at(C_PLACEMENT)
    before = _standing(corpus)
    assert before, "the first run recorded no verdicts to re-judge"
    assert {row["outcome"] for row in before} == {"reject"}
    old_version = before[0]["validator_version"]
    assert not _supersessions(corpus)

    _bump(monkeypatch, "r127")
    _run(corpus)

    assert socket.calls_at(A_FACT) == first, (
        f"re-validating bought {socket.calls_at(A_FACT) - first} model answers it "
        f"already had: {socket.subjects_at(A_FACT)[first:]}")
    # Site C asked again, because it records no `llm_call_identity` and therefore
    # has nothing R-109 could reuse. Stated rather than absorbed into a total: the
    # day placement joins the reuse this line is the one that goes red.
    assert socket.calls_at(C_PLACEMENT) == placements * 2, (
        "site C's per-run placement call is no longer once per run and the pins "
        "below are counting something else")
    after = _standing(corpus)
    assert {row["validator_version"] for row in after} == {
        fact_validation.judgement_version(_deps(corpus))}
    assert all(row["validator_version"] != old_version for row in after)
    # Append-only: the old conclusions are still readable, linked, and carry the
    # reason they stopped standing.
    superseded = _superseded_at(corpus, A_FACT)
    assert len(superseded) == len(before)
    assert {row["verdict_id"] for row in superseded} == {
        row["verdict_id"] for row in before}
    assert all(row["supersede_reason"].startswith("re-validated under ")
               for row in superseded)
    links = _supersessions(corpus)
    assert len(links) == len(before)
    assert {link["old_verdict_id"] for link in links} == {
        row["verdict_id"] for row in before}
    # And the answer is still reused, which is the whole point of re-judging it
    # rather than re-asking it. Site A's own saving (`_reuses_at`): the gate saves
    # on the same two files and in the same table.
    assert len(_reuses_at(corpus, A_FACT)) == first


def test_a_re_judged_answer_is_not_judged_again_on_the_next_run(
        corpus, socket, monkeypatch):
    """The second re-validation would be a loop, not a correction.

    A run that left any verdict standing under the old version would find it
    stale again next time and append a supersession per run for ever.

    Three runs, so site C's own count is three times its per-run one (`_Socket`,
    `104` §17.13 ruling 3): the fact pass buys nothing after the first run and
    placement asks every time.
    """
    _run(corpus)
    first = socket.calls_at(A_FACT)
    placements = socket.calls_at(C_PLACEMENT)
    _bump(monkeypatch, "r127")
    _run(corpus)
    once = len(_supersessions(corpus))
    assert once > 0

    _run(corpus)

    assert len(_supersessions(corpus)) == once
    assert socket.calls_at(A_FACT) == first, socket.subjects_at(A_FACT)[first:]
    assert socket.calls_at(C_PLACEMENT) == placements * 3


def test_the_same_validator_re_judges_nothing(corpus, socket):
    """No change, no re-judgement: the prior's verdicts are reused as they stand.

    R-109's reuse is untouched by R-127 when nothing about the judge moved, and
    the cost of the check is a read of `llm_verdict`, not a second reading of the
    response.

    **This is the pin `104` R-172a's defect showed up on first.** R-109 closed with
    the sentence *"No dimension carries a run id, a timestamp or a path (two runs
    of one checkout over unchanged files: two identity ids, both stable)"*, and
    §18.7's standing consent grant put one back: `cli.standing_consent_grants`
    scopes the owner's local-model permission to `scan_run_id`, a fresh `uuid4` per
    run, and `policy` is one of `store.CALL_IDENTITY_DIMENSIONS`. So a second run
    of an unchanged corpus computed a different digest for every file and bought
    every answer again -- three calls, then three more. `model_facts.
    _consent_grants_content` records that grant under `STANDING_GRANT_SCOPE` and
    the gate still matches the raw scope, so §18.7's ruling holds and the identity
    is stable again.
    """
    _run(corpus)
    first = socket.calls_at(A_FACT)
    placements = socket.calls_at(C_PLACEMENT)
    before = _standing(corpus)

    _run(corpus)

    assert socket.calls_at(A_FACT) == first, socket.subjects_at(A_FACT)[first:]
    assert socket.calls_at(C_PLACEMENT) == placements * 2
    assert not _supersessions(corpus)
    assert _standing(corpus) == before
    assert len(_reuses_at(corpus, A_FACT)) == first


def test_a_missing_stored_response_is_asked_again(corpus, socket, monkeypatch):
    """Nothing to re-read is not permission to keep the old reading.

    A database can hold an identity whose response it does not have -- a seeding
    that copied verdicts and not responses, a row from before responses were
    kept. The honest answer is the question, and it costs a call.

    The trigger is dropped rather than worked around: `llm_response` is
    append-only by design and this test needs the state that design forbids,
    which is a fixture built in the open rather than a hole left in the schema.
    """
    _run(corpus)
    first = socket.calls_at(A_FACT)
    placements = socket.calls_at(C_PLACEMENT)
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    try:
        conn.execute("DROP TRIGGER llm_response_no_delete")
        conn.execute("DELETE FROM llm_response")
        conn.commit()
    finally:
        conn.close()

    _bump(monkeypatch, "r127")
    _run(corpus)

    assert socket.calls_at(A_FACT) == first * 2, (
        "a validator change over a response nobody kept reused the old verdict "
        "instead of asking")
    assert socket.calls_at(C_PLACEMENT) == placements * 2
    assert not _supersessions(corpus)


def test_a_normaliser_change_is_detected_the_same_way(corpus, socket, monkeypatch):
    """§14.7 names two things and they are one string. `104` R-127.

    The validator's own bytes are untouched here; what moves is the deployment's
    review normaliser, which `104` R-98 made half of check 3. Nothing tells the
    reuse decision about it -- it reads the same `validator_version` column -- and
    that is the design: one column, one version, no second record of the same
    thing free to disagree with the first.
    """
    _run(corpus)
    first = socket.calls_at(A_FACT)
    placements = socket.calls_at(C_PLACEMENT)
    before = _standing(corpus)

    def normalize_for_review_v2(field_key, raw_value):
        """A second review normaliser, refusing everything the first accepted."""
        return None

    monkeypatch.setattr(cli, "normalize_for_review", normalize_for_review_v2)
    _run(corpus)

    assert socket.calls_at(A_FACT) == first, socket.subjects_at(A_FACT)[first:]
    assert socket.calls_at(C_PLACEMENT) == placements * 2
    links = _supersessions(corpus)
    assert len(links) == len(before), (
        "a normaliser this deployment swapped did not re-judge the answers the "
        "old one judged")
    assert all(link["reason"].startswith("re-validated under ") for link in links)
    after = _standing(corpus)
    assert {row["validator_version"] for row in after} != {
        row["validator_version"] for row in before}


def _deps(corpus):
    """The three callbacks `cli` hands Site A, as `model_facts` bundles them.

    **`normalize` is a CLOSURE now, and `104` §18.2 gap 3 is why.** This helper
    named `cli.normalize_for_model` from the day it was written, and the pin that
    reads it -- "every standing verdict carries the version this deployment's
    judge computes" -- could only ever have been reached once the reuse worked
    (R-172a); by then `cli.p1_p7_authorities` had stopped passing that function.
    Gap 3 gave check 3 a second half: `normalize_with_the_persons_own_values(conn)`
    asks the shipped library first and the person's own confirmed spellings second,
    so a value confirmed once stops being proposed for ever. It is the deployment's
    answer to C-5 exactly as the plain function was, and `judgement_version`
    digests the bundle, so naming the superseded spelling here computes a version
    no run ever wrote.

    The connection is the plan database this corpus ran against, because that is
    the vocabulary the closure reads; `_callable_version` digests the closure's
    module, qualname and source and not the rows behind it, so any connection to
    the same schema gives the same version -- which the stated limit in
    `_callable_version` says out loud.
    """
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    try:
        return fact_validation.FactValidationDependencies(
            normalize=cli.normalize_with_the_persons_own_values(conn),
            contradicts=cli.contradicts_stronger,
            normalize_for_review=cli.normalize_for_review)
    finally:
        conn.close()


# --- `104` R-142: an unreadable prior costs one file, never the run ---------------


def _rewrite_dossier_body(corpus, change) -> None:
    """Edit the stored dossier bodies the way an older record shape left them.

    The table is append-only by trigger and the state this needs is one no current
    checkout can write: a row recorded before a field existed. The trigger is
    dropped in the open, because a fixture that needs a forbidden state should say
    so where a reader can see it.
    """
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    conn.row_factory = sqlite3.Row
    try:
        for trigger in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'trigger' AND "
                "tbl_name = 'llm_dossier'").fetchall():
            conn.execute(f"DROP TRIGGER {trigger['name']}")
        for row in conn.execute(
                "SELECT dossier_id, payload FROM llm_dossier").fetchall():
            body = json.loads(row["payload"])
            change(body)
            conn.execute("UPDATE llm_dossier SET payload = ? WHERE dossier_id = ?",
                         (json.dumps(body, sort_keys=True), row["dossier_id"]))
        conn.commit()
    finally:
        conn.close()


def test_a_dossier_that_truly_will_not_rebuild_costs_one_file_and_not_the_run(
        corpus, socket, monkeypatch):
    """The other half: the guard still refuses, and the run still finishes.

    A field the model SAW that the rebuild would drop is a real fault and
    `load_dossier` still raises on it. What must not follow is r10: the reuse
    decision answers "not current", the file is asked fresh, and every other file
    is unaffected. One bad row is one file's cost.
    """
    _run(corpus)
    first = socket.calls_at(A_FACT)
    placements = socket.calls_at(C_PLACEMENT)

    def drop_an_evidence_item(body):
        if body.get("released_evidence"):
            body["released_evidence"] = body["released_evidence"][:-1]

    _rewrite_dossier_body(corpus, drop_an_evidence_item)
    _bump(monkeypatch, "r142")
    _run(corpus)

    assert socket.calls_at(A_FACT) == first * 2, (
        socket.subjects_at(A_FACT)[first:])
    assert socket.calls_at(C_PLACEMENT) == placements * 2
    assert not _supersessions(corpus)
