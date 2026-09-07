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

**Everything is real except the socket**, as in
`test_a_fact_reuse_after_a_verdict.py`, whose corpus and plumbing this file reuses
deliberately: the same two files, the same rejecting answer, the same production
`cli.run`. The only thing these tests add is a change to the judge between two runs.
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
    """Every model call this run makes. Counting `invoke` counts model calls."""

    def __init__(self) -> None:
        self.payloads: list[bytes] = []

    def __len__(self) -> int:
        return len(self.payloads)

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
    """The developer's own key must not decide whether these tests pass."""
    for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values()):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")
    for name, value in ENV.items():
        monkeypatch.setenv(name, value)


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
              "--enable-cloud"], out=out)
    return out.getvalue()


def _rows(corpus, sql, *params):
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, params)]
    finally:
        conn.close()


def _standing(corpus):
    return _rows(
        corpus,
        "SELECT verdict_id, claim_ref, outcome, validator_version FROM llm_verdict "
        "WHERE superseded_by IS NULL ORDER BY verdict_id")


def _supersessions(corpus):
    return _rows(corpus, "SELECT * FROM llm_verdict_supersession")


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
    """R-127 in one number: two calls, a new validator, and still two calls.

    Before the fix the second run reused the first validator's rejections as they
    stood; there was no supersession row in the database and no way to tell a
    verdict this validator would reach from one it would not.
    """
    _run(corpus)
    first = len(socket)
    assert first == 2, socket.subjects()
    before = _standing(corpus)
    assert before, "the first run recorded no verdicts to re-judge"
    assert {row["outcome"] for row in before} == {"reject"}
    old_version = before[0]["validator_version"]
    assert not _supersessions(corpus)

    _bump(monkeypatch, "r127")
    _run(corpus)

    assert len(socket) == first, (
        f"re-validating bought {len(socket) - first} model answers it already "
        f"had: {socket.subjects()[first:]}")
    after = _standing(corpus)
    assert {row["validator_version"] for row in after} == {
        fact_validation.judgement_version(_deps())}
    assert all(row["validator_version"] != old_version for row in after)
    # Append-only: the old conclusions are still readable, linked, and carry the
    # reason they stopped standing.
    superseded = _rows(
        corpus, "SELECT verdict_id, superseded_by, supersede_reason FROM "
        "llm_verdict WHERE superseded_by IS NOT NULL")
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
    # rather than re-asking it.
    assert len(_rows(corpus, "SELECT * FROM llm_call_reuse")) == first


def test_a_re_judged_answer_is_not_judged_again_on_the_next_run(
        corpus, socket, monkeypatch):
    """The second re-validation would be a loop, not a correction.

    A run that left any verdict standing under the old version would find it
    stale again next time and append a supersession per run for ever.
    """
    _run(corpus)
    first = len(socket)
    _bump(monkeypatch, "r127")
    _run(corpus)
    once = len(_supersessions(corpus))
    assert once > 0

    _run(corpus)

    assert len(_supersessions(corpus)) == once
    assert len(socket) == first, socket.subjects()[first:]


def test_the_same_validator_re_judges_nothing(corpus, socket):
    """No change, no re-judgement: the prior's verdicts are reused as they stand.

    R-109's reuse is untouched by R-127 when nothing about the judge moved, and
    the cost of the check is a read of `llm_verdict`, not a second reading of the
    response.
    """
    _run(corpus)
    first = len(socket)
    before = _standing(corpus)

    _run(corpus)

    assert len(socket) == first, socket.subjects()[first:]
    assert not _supersessions(corpus)
    assert _standing(corpus) == before
    assert len(_rows(corpus, "SELECT * FROM llm_call_reuse")) == first


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
    first = len(socket)
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    try:
        conn.execute("DROP TRIGGER llm_response_no_delete")
        conn.execute("DELETE FROM llm_response")
        conn.commit()
    finally:
        conn.close()

    _bump(monkeypatch, "r127")
    _run(corpus)

    assert len(socket) == first * 2, (
        "a validator change over a response nobody kept reused the old verdict "
        "instead of asking")
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
    first = len(socket)
    before = _standing(corpus)

    def normalize_for_review_v2(field_key, raw_value):
        """A second review normaliser, refusing everything the first accepted."""
        return None

    monkeypatch.setattr(cli, "normalize_for_review", normalize_for_review_v2)
    _run(corpus)

    assert len(socket) == first, socket.subjects()[first:]
    links = _supersessions(corpus)
    assert len(links) == len(before), (
        "a normaliser this deployment swapped did not re-judge the answers the "
        "old one judged")
    assert all(link["reason"].startswith("re-validated under ") for link in links)
    after = _standing(corpus)
    assert {row["validator_version"] for row in after} != {
        row["validator_version"] for row in before}


def _deps():
    """The three callbacks `cli` hands Site A, as `model_facts` bundles them."""
    return fact_validation.FactValidationDependencies(
        normalize=cli.normalize_for_model,
        contradicts=cli.contradicts_stronger,
        normalize_for_review=cli.normalize_for_review)


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
    first = len(socket)

    def drop_an_evidence_item(body):
        if body.get("released_evidence"):
            body["released_evidence"] = body["released_evidence"][:-1]

    _rewrite_dossier_body(corpus, drop_an_evidence_item)
    _bump(monkeypatch, "r142")
    _run(corpus)

    assert len(socket) == first * 2, socket.subjects()[first:]
    assert not _supersessions(corpus)
