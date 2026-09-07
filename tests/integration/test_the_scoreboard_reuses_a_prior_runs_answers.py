# tests/integration/test_the_scoreboard_reuses_a_prior_runs_answers.py
"""`104` R-123 against the real product, and the one thing standing in its way.

R-109 closed the reuse for the product's OWN database: an identical question under
an identical identity is answered from the record and no call is made. R-123 is that
same saving under the scoreboard, which deletes each situation's database at the top
of its run so that no answer, plan version or consent reaches the next situation.
`--reuse-answers-from` gives the fresh database back the four tables a reuse can be
decided from, and nothing else. `tests/tools/test_groundtruth_reuse_answers.py`
measures the copier; this measures whether the product then reuses.

**A copy alone could not do it, and one term is why.**
`store.CALL_IDENTITY_DIMENSIONS` includes `subject_ref`, and
`model_facts.call_identity_dimensions` fills it with the `file_id`. That id is a
UUID `database_agent.files_table.observe_path` mints the first time a path is seen,
so it is per-DATABASE and not per-file: two databases over one unchanged corpus give
one file two ids and therefore two identities, and a verbatim copy of the prior's
identity rows sits under a digest this run will never compute. Measured before the
translation was written: 2 calls, seed, 2 calls again, `llm_call_reuse` empty.
`test_two_databases_over_one_corpus_agree_on_every_dimension_but_the_subject_ref`
is that measurement, kept: every other term, `content_hash` and `prompt_fingerprint`
and `model_id` and the policy included, is identical, so `subject_ref` alone is what
the seeder has to translate. It is a guard as much as a record -- the day `file_id`
becomes derivable from the file, it goes red and the translation can come out.

So `reuse.seed` runs the product's own P3 scan into the fresh database first, learns
what THIS database calls each file, rewrites that one term and asks the product's own
`call_identity` for the digest. The run then scans again and finds those rows
unchanged, so its own work is neither skipped nor repeated.

**Everything is real except the socket**, exactly as in
`test_a_fact_reuse_after_a_verdict.py`, whose `_Socket` this borrows in shape:
`readers.model_routing.deepseek_invoke` is the documented deployment seam, and the
gate, the release ledger, the transport, the validator and the whole of `cli.run`
are the production path. Counting `invoke` calls counts model calls exactly.

Two DATABASES rather than two runs against one, because that is what the scoreboard
does and it is the whole of R-123: the second run's database is created by
`tools.groundtruth.reuse.seed`, which is the code under test.
"""
from __future__ import annotations

import io
import json
import pathlib
import sqlite3
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT))

import cli  # noqa: E402
from readers import model_routing  # noqa: E402
from readers.model_routing import MODEL_NAME_OF_TIER  # noqa: E402
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME  # noqa: E402
from llm_harness import fact_validation  # noqa: E402
from tools.groundtruth.reuse import (  # noqa: E402
    ReuseRefused,
    refuse_unless_seedable,
    seed,
    wire_handle_key_file,
)

SITUATION = "academic.coursework"

#: R-13's own corpus, and for R-13's own reason: two files with releasable text and
#: no deterministic course code, so the rule stage settles nothing and both files
#: reach a model.
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

#: A supported claim citing nothing: `CITATION_NOT_FOUND`, and the verdict is
#: `reject`. R-109's own answer, and the outcome that most needs reusing -- the
#: model answered, the validator refused, the field is open again, and asking twice
#: buys the identical rejection twice.
UNCITED = "Something the evidence does not carry"


class _Socket:
    """Every model call these runs make, and the dossier each one carried."""

    def __init__(self) -> None:
        self.payloads: list[bytes] = []

    def __len__(self) -> int:
        return len(self.payloads)

    def subjects(self) -> list[str]:
        return [self._body(p)["subject_ref"] for p in self.payloads]

    @staticmethod
    def _body(payload: bytes) -> dict:
        return json.loads(payload.decode("utf-8").split("The dossier follows.", 1)[1])

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


def _run(corpus, database) -> None:
    """One scoreboard run: this corpus, this situation, its own database.

    `--enable-cloud` on BOTH runs, so the second is fully able to call and is
    measured not calling rather than measured unable to.
    """
    out = io.StringIO()
    cli.main([str(corpus), "--situation", SITUATION, "--label", "Coursework",
              "--user", "groundtruth", "--database", str(database),
              "--enable-cloud"], out=out)


def _rows(database, sql: str) -> list[dict]:
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql)]
    finally:
        conn.close()


def _paths(database) -> dict[str, str]:
    return {row["file_id"]: pathlib.Path(row["current_path"]).name
            for row in _rows(database, "SELECT file_id, current_path FROM files")}


def _asked_again(first, second) -> set[str]:
    """The NAMES of the files the second run built a dossier for that the first did.

    Read from the databases and not from the socket, because what the socket sees
    is a WIRE HANDLE: `privacy.gate` rotates the identifier before the dossier
    leaves, so `subject_ref` in the payload is `handle:<digest>` and names nothing
    a person can look up. `llm_dossier.subject_ref` is the local id, and a dossier
    the second run built is one whose address the first run's database does not
    hold -- a seeded dossier keeps the id it was given.
    """
    def dossiers(database):
        return {row["dossier_id"]: row["subject_ref"] for row in
                _rows(database, "SELECT dossier_id, subject_ref FROM llm_dossier")}

    before, after = dossiers(first), dossiers(second)
    names = _paths(second)
    return {names.get(subject, subject) for address, subject in after.items()
            if address not in before}


# --- the copier, against rows a real run wrote ------------------------------------


def test_the_seeded_rows_are_the_prior_runs_own_answers(corpus, socket, tmp_path):
    """The four tables, filled by the product rather than by a fixture."""
    first, second = tmp_path / "one.sqlite", tmp_path / "two.sqlite"
    _run(corpus, first)
    assert len(socket) == 2, socket.subjects()

    given = seed(second, first, corpus=corpus)

    assert given.answers == 2
    assert given.rows["llm_call_identity"] == 2
    assert given.rows["llm_dossier"] == 2
    assert given.rows["llm_response"] == 2
    assert given.rows["llm_verdict"] == len(
        _rows(first, "SELECT 1 FROM llm_verdict")) > 0
    # The run has not started, so nothing about placement or consent is there and
    # the reuse ledger is empty. What the fresh database exists to keep out is out.
    assert not _rows(second, "SELECT 1 FROM llm_call_reuse")
    assert not _rows(second, "SELECT 1 FROM cloud_consent")


def test_two_databases_over_one_corpus_agree_on_every_dimension_but_the_subject_ref(
        corpus, socket, tmp_path):
    """Why the seeding is inert today, in the only term that moves.

    `observe_path` mints `file_id` as a UUID the first time it sees a path, so it
    identifies a file WITHIN a database and nothing across two. `subject_ref` is
    that id, and it is one of `CALL_IDENTITY_DIMENSIONS`, so the digest a fresh run
    computes for an unchanged file can never equal the one a prior run recorded --
    however carefully the row is copied.

    Kept after the translation was written, because it is what justifies the
    translation: the day `file_id` is derivable from the file rather than minted
    per database, this goes red and `reuse.seed` can stop scanning.
    """
    first, second = tmp_path / "one.sqlite", tmp_path / "two.sqlite"
    _run(corpus, first)
    _run(corpus, second)

    def by_name(database):
        names = _paths(database)
        return {names[row["subject_ref"]]: json.loads(row["dimensions"])
                for row in _rows(database,
                                 "SELECT subject_ref, dimensions FROM "
                                 "llm_call_identity")
                if row["subject_ref"] in names}

    one, two = by_name(first), by_name(second)
    assert set(one) == set(CORPUS) == set(two)
    for name in one:
        differing = sorted(term for term in one[name]
                           if one[name][term] != two[name][term])
        assert differing == ["subject_ref"], (
            f"{name}: expected the file id alone to move between two databases, "
            f"and these moved: {differing}")


# --- R-123's own acceptance tests -------------------------------------------------


def test_a_seeded_fresh_database_asks_nothing_the_prior_run_answered(
        corpus, socket, tmp_path):
    """R-123 in one number: the second run of an unchanged corpus spends nothing."""
    first, second = tmp_path / "one.sqlite", tmp_path / "two.sqlite"
    _run(corpus, first)
    paid_for = len(socket)
    assert paid_for == 2, socket.subjects()

    seed(second, first, corpus=corpus)
    _run(corpus, second)

    assert len(socket) == paid_for, (
        f"the seeded run re-asked {len(socket) - paid_for} questions whose answers "
        f"it had been handed: {sorted(_asked_again(first, second))}")
    assert len(_rows(second, "SELECT 1 FROM llm_call_reuse")) == paid_for


def test_only_the_file_whose_bytes_changed_is_asked_again(corpus, socket, tmp_path):
    """The safety half of R-123, and the reason the identity stays the key.

    A seeded answer must not survive a change to the thing it is an answer about.
    `content_hash` is a dimension, so a rewritten file is a different identity and
    is asked; its neighbour, untouched, is not.
    """
    first, second = tmp_path / "one.sqlite", tmp_path / "two.sqlite"
    _run(corpus, first)
    paid_for = len(socket)

    (corpus / "week two notes.txt").write_text(
        "Rewritten between the runs. Notes from the seminar on elasticity, with "
        "the essay the instructor set for the vacation.\n")
    seed(second, first, corpus=corpus)
    _run(corpus, second)

    assert len(socket) - paid_for == 1, socket.subjects()[paid_for:]
    assert _asked_again(first, second) == {"week two notes.txt"}
    # And the one that did not change was answered from the record.
    assert len(_rows(second, "SELECT 1 FROM llm_call_reuse")) == 1


# --- R-127: the key travels with the answers --------------------------------------


def _supersessions(database) -> list[dict]:
    return _rows(database, "SELECT * FROM llm_verdict_supersession")


def test_a_seeded_run_in_its_own_directory_is_given_the_prior_runs_key(
        corpus, socket, tmp_path):
    """`104` R-127. Every other test here writes both databases into one directory.

    A real rerun cannot: `--out` and `--reuse-answers-from` are refused if they are
    the same directory, so the fresh run would mint its own `.wire-handle-key`. A
    wire handle is a digest under that key and `dossier_id` is the content address
    of the bytes the handles sit in, so a seeded dossier under a fresh key is filed
    at an address this run cannot compute -- and anything that reads those bytes
    back, R-127's re-judgement first among them, would resolve every handle to
    nothing, reject every citation, and reuse that instead.

    The key is copied with the answers, and this is the number that says so. The
    reuse itself is unchanged: nothing was re-asked.
    """
    prior_dir, fresh_dir = tmp_path / "prior", tmp_path / "fresh"
    prior_dir.mkdir()
    first, second = prior_dir / "one.sqlite", fresh_dir / "two.sqlite"
    _run(corpus, first)
    paid_for = len(socket)
    assert paid_for == 2, socket.subjects()

    seed(second, first, corpus=corpus)

    assert wire_handle_key_file(fresh_dir).read_bytes() == (
        wire_handle_key_file(prior_dir).read_bytes())
    _run(corpus, second)
    assert len(socket) == paid_for, (
        f"the seeded run re-asked {len(socket) - paid_for} questions whose "
        f"answers it had been handed: {sorted(_asked_again(first, second))}")
    assert len(_rows(second, "SELECT 1 FROM llm_call_reuse")) == paid_for


def test_a_seeded_answer_is_asked_again_when_the_validator_moves(
        corpus, socket, tmp_path, monkeypatch):
    """THE MEASURED LIMIT of seeding under `104` R-127, pinned rather than assumed.

    R-127 re-judges a stored response instead of re-asking it, and it cannot do
    that for a SEEDED one. The seeder translates `llm_dossier.subject_ref` -- the
    column -- to this database's file id, and leaves the payload alone because the
    payload is the bytes the address was taken over and rewriting it would move the
    address. So the rebuilt dossier still names the prior run's file id, and
    `validate_fact_proposal` refuses a dossier and a request that name different
    files: "a dossier describing one file wrote a fact onto another, cited to
    observations that file never had". That refusal is right, and the honest answer
    to it is the question.

    **What it costs, so that whoever reads this can price it:** a scoreboard rerun
    across a validator change pays for every seeded answer again. R-123's flag
    still saves everything on a rerun that changes nothing else, which is the case
    it was built for. Closing this one means translating the dossier payload and
    recomputing its content address the way the seeder already recomputes the
    identity digest, and rewriting the four foreign keys that name it -- R-123's
    change, not R-127's.
    """
    prior_dir, fresh_dir = tmp_path / "prior", tmp_path / "fresh"
    prior_dir.mkdir()
    first, second = prior_dir / "one.sqlite", fresh_dir / "two.sqlite"
    _run(corpus, first)
    paid_for = len(socket)

    monkeypatch.setattr(
        fact_validation, "VALIDATOR_VERSION",
        f"{fact_validation.VALIDATOR_VERSION}+r127")
    seed(second, first, corpus=corpus)
    _run(corpus, second)

    assert len(socket) == paid_for * 2, socket.subjects()[paid_for:]
    # Asked, not re-judged: no conclusion was drawn from bytes this run could not
    # attribute to the file it is about.
    assert not _supersessions(second)


def test_a_prior_without_a_wire_handle_key_is_refused_before_anything_runs(
        corpus, socket, tmp_path):
    """The refusal is a sentence, and it arrives before a database is deleted.

    A directory whose key has been removed still READS -- every row is there -- and
    every answer in it is unusable. Saying so is the difference between a rerun
    that costs nothing and one that silently costs everything.
    """
    prior_dir, fresh_dir = tmp_path / "prior", tmp_path / "fresh"
    prior_dir.mkdir()
    _run(corpus, prior_dir / f"{SITUATION.replace('.', '_')}.sqlite")
    wire_handle_key_file(prior_dir).unlink()

    with pytest.raises(ReuseRefused) as refusal:
        refuse_unless_seedable(
            prior_dir, [SITUATION], out_dir=fresh_dir, score_only=False)

    assert "wire-handle-key" in str(refusal.value)
    assert "Nothing has been run" in str(refusal.value)
