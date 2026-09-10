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
from llm_harness.vocabulary import A_FACT, C_PLACEMENT  # noqa: E402
from tools.groundtruth.reuse import (  # noqa: E402
    ReuseRefused,
    prior_database,
    refuse_unless_seedable,
    seed,
    seeded_note,
    wire_handle_key_file,
    write_seeded,
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
    """Every model call these runs make, and the dossier each one carried.

    **COUNTED PER CALL SITE, `104` §17.13 ruling 3.** When this file was written
    the corpus produced one model call per file and nothing else, so a total was a
    site-A total. §17.13 moved site C's `eliminate-v2` from `ratified_local` to
    `ratified` and R-170 made the route per FILE, so a run with `--enable-cloud`
    now also sends a `C_placement` dossier for each file P11 proposes a folder for
    -- one, on this two-file corpus, through the same stubbed `deepseek_invoke`.

    R-123 is the reuse of ANSWERS, and an answer here is a fact: `reuse.seed`
    copies `llm_call_identity`, `llm_dossier`, `llm_response` and `llm_verdict`,
    and site C records no call identity at all, so there is nothing of C's for a
    seeding to hand on and nothing for `_reuse_is_current` to look up. Counting C
    in the totals would report the scoreboard buying an answer it was never given.
    Every pin that counts A's savings also states C's repetition, so a placement
    that starts reusing -- or stops calling -- turns a line red instead of quietly
    moving a number this file believes is site A's.
    """

    def __init__(self) -> None:
        self.payloads: list[bytes] = []

    def __len__(self) -> int:
        return len(self.payloads)

    def calls_at(self, call_site: str) -> int:
        """How many calls these runs made at ONE site."""
        return sum(1 for p in self.payloads
                   if self._body(p)["call_site"] == call_site)

    def subjects_at(self, call_site: str) -> list[str]:
        return [self._body(p)["subject_ref"] for p in self.payloads
                if self._body(p)["call_site"] == call_site]

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


def _a_fact_verdicts(database) -> list[dict]:
    """The verdicts of the pass this file is about, and no other site's.

    `llm_verdict` holds every site's judgements. Since `104` §17.13 ruling 3 a run
    of this corpus writes `C_placement` verdicts beside site A's, judged by P8's
    own validator and copied by no seeding, so an unscoped count says the seeder
    left answers behind when it left nothing behind at all. Joined on
    `llm_dossier.call_site`, which is the record of which site asked.
    """
    return _rows(
        database,
        "SELECT v.verdict_id AS verdict_id, v.validator_version AS "
        "validator_version, v.superseded_by AS superseded_by FROM llm_verdict v "
        "JOIN llm_dossier d ON d.dossier_id = v.dossier_id "
        f"WHERE d.call_site = '{A_FACT}'")


def _a_fact_addresses(database) -> set[str]:
    """The addresses of the dossiers a seeding can carry, and no others."""
    return {row["dossier_id"] for row in _rows(
        database,
        f"SELECT dossier_id FROM llm_dossier WHERE call_site = '{A_FACT}'")}


def _paths(database) -> dict[str, str]:
    return {row["file_id"]: pathlib.Path(row["current_path"]).name
            for row in _rows(database, "SELECT file_id, current_path FROM files")}


def _asked_again(database, seeded) -> set[str]:
    """The NAMES of the files this run built a dossier for rather than reusing one.

    Read from the database and not from the socket, because what the socket sees
    is a WIRE HANDLE: `privacy.gate` rotates the identifier before the dossier
    leaves, so `subject_ref` in the payload is `handle:<digest>` and names nothing
    a person can look up. `llm_dossier.subject_ref` is the local id.

    A dossier this run BUILT is one whose address is not among the addresses it
    was handed. It used to be one the prior database did not hold, and `104` R-137
    ended that: a seeded dossier is re-addressed for the file id THIS database
    gives it, so its address is new by design and comparing the two databases
    would report every reused file as freshly asked.

    Site A's dossiers ONLY (`104` §17.13 ruling 3). `seed` hands on what the four
    `llm_*` tables can be reused from, and site C records no `llm_call_identity`,
    so no C dossier is ever among `seeded.addresses` and every one of them would
    read as freshly asked -- under its own `file:<id>:<hash>` subject, which
    `_paths` cannot name and which would then be reported to a reader as a file
    the seeding failed to cover. C IS asked again, every run; the pins say so in
    their own line rather than through this set.
    """
    names = _paths(database)
    handed = set(seeded.addresses.values())
    return {names.get(row["subject_ref"], row["subject_ref"]) for row in
            _rows(database, "SELECT dossier_id, subject_ref FROM llm_dossier "
                            f"WHERE call_site = '{A_FACT}'")
            if row["dossier_id"] not in handed}


# --- the copier, against rows a real run wrote ------------------------------------


def test_the_seeded_rows_are_the_prior_runs_own_answers(corpus, socket, tmp_path):
    """The four tables, filled by the product rather than by a fixture.

    Counted at site A (`_Socket`): the run also makes site C's placement call, and
    the four tables carry no row of C's for the seeding to copy.
    """
    first, second = tmp_path / "one.sqlite", tmp_path / "two.sqlite"
    _run(corpus, first)
    assert socket.calls_at(A_FACT) == len(CORPUS), socket.subjects()

    given = seed(second, first, corpus=corpus)

    assert given.answers == len(CORPUS)
    assert given.rows["llm_call_identity"] == len(CORPUS)
    assert given.rows["llm_dossier"] == len(CORPUS)
    assert given.rows["llm_response"] == len(CORPUS)
    assert given.rows["llm_verdict"] == len(_a_fact_verdicts(first)) > 0
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
    """R-123 in one number: the second run of an unchanged corpus spends nothing.

    **The number the fix restored is this one.** `104` R-172a: §18.7's standing
    consent grant is scoped to `scan_run_id`, `policy` is a call-identity
    dimension, and a scan run id is a fresh `uuid4`, so every seeded identity sat
    under a digest the fresh run could never compute and this pin read 4 where it
    says 2 -- R-109's own closing sentence, *"No dimension carries a run id, a
    timestamp or a path"*, made false by a ruling that had no reason to know it.
    `model_facts._consent_grants_content` records the grant under its standing
    scope and the gate still matches the raw one, so §18.7 holds and R-123 pays
    nothing again. Site C's own call is counted on its own line, per `_Socket`.
    """
    first, second = tmp_path / "one.sqlite", tmp_path / "two.sqlite"
    _run(corpus, first)
    paid_for = socket.calls_at(A_FACT)
    placements = socket.calls_at(C_PLACEMENT)
    assert paid_for == len(CORPUS), socket.subjects()

    given = seed(second, first, corpus=corpus)
    _run(corpus, second)

    assert socket.calls_at(A_FACT) == paid_for, (
        f"the seeded run re-asked {socket.calls_at(A_FACT) - paid_for} questions "
        f"whose answers it had been handed: "
        f"{sorted(_asked_again(second, given))}")
    assert socket.calls_at(C_PLACEMENT) == placements * 2, (
        "site C is no longer asked once per run and the count above is measuring "
        "something other than the fact pass")
    assert len(_rows(second, "SELECT 1 FROM llm_call_reuse")) == paid_for


def test_only_the_file_whose_bytes_changed_is_asked_again(corpus, socket, tmp_path):
    """The safety half of R-123, and the reason the identity stays the key.

    A seeded answer must not survive a change to the thing it is an answer about.
    `content_hash` is a dimension, so a rewritten file is a different identity and
    is asked; its neighbour, untouched, is not.

    Site A's calls, per `_Socket`: the run's placement call is not an answer this
    seeding could have handed on, and counting it here would report a file asked
    that was not.
    """
    first, second = tmp_path / "one.sqlite", tmp_path / "two.sqlite"
    _run(corpus, first)
    paid_for = socket.calls_at(A_FACT)

    (corpus / "week two notes.txt").write_text(
        "Rewritten between the runs. Notes from the seminar on elasticity, with "
        "the essay the instructor set for the vacation.\n")
    given = seed(second, first, corpus=corpus)
    _run(corpus, second)

    assert socket.calls_at(A_FACT) - paid_for == 1, (
        socket.subjects_at(A_FACT)[paid_for:])
    assert _asked_again(second, given) == {"week two notes.txt"}
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
    reuse itself is unchanged: nothing was re-asked. Site A's calls, per `_Socket`.
    """
    prior_dir, fresh_dir = tmp_path / "prior", tmp_path / "fresh"
    prior_dir.mkdir()
    first, second = prior_dir / "one.sqlite", fresh_dir / "two.sqlite"
    _run(corpus, first)
    paid_for = socket.calls_at(A_FACT)
    assert paid_for == len(CORPUS), socket.subjects()

    given = seed(second, first, corpus=corpus)

    assert wire_handle_key_file(fresh_dir).read_bytes() == (
        wire_handle_key_file(prior_dir).read_bytes())
    _run(corpus, second)
    assert socket.calls_at(A_FACT) == paid_for, (
        f"the seeded run re-asked {socket.calls_at(A_FACT) - paid_for} questions "
        f"whose answers it had been handed: "
        f"{sorted(_asked_again(second, given))}")
    assert len(_rows(second, "SELECT 1 FROM llm_call_reuse")) == paid_for


def test_a_seeded_answer_is_re_judged_when_the_validator_moves(
        corpus, socket, tmp_path, monkeypatch):
    """`104` R-137, and it is the measure-fix-rerun loop that could not run.

    R-127 re-judges a stored response instead of buying the same answer again, and
    it could not do that for a SEEDED one: the seeder translated
    `llm_dossier.subject_ref`, the column, and left the payload, so the rebuilt
    dossier named the prior run's file and `validate_fact_proposal` refused to
    judge a dossier and a request that name different files. Measured on the
    owner's r5: `llm_call_reuse` 0, `llm_verdict_supersession` 0, every one of 199
    files bought again at about 100 seconds each -- and validators change every
    wave, so every rerun paid it.

    The payload's file id is translated now and the address recomputed with it, so
    the seeded dossier names THIS run's file, the stored response is re-judged
    under the new validator, and the number below is zero fresh calls.

    This test replaces one that pinned the old cost. It is the same setup with the
    conclusion the product now reaches.
    """
    prior_dir, fresh_dir = tmp_path / "prior", tmp_path / "fresh"
    prior_dir.mkdir()
    first, second = prior_dir / "one.sqlite", fresh_dir / "two.sqlite"
    _run(corpus, first)
    paid_for = socket.calls_at(A_FACT)
    seeded_verdicts = len(_a_fact_verdicts(first))
    assert seeded_verdicts

    monkeypatch.setattr(
        fact_validation, "VALIDATOR_VERSION",
        f"{fact_validation.VALIDATOR_VERSION}+r137")
    given = seed(second, first, corpus=corpus)
    _run(corpus, second)

    assert socket.calls_at(A_FACT) == paid_for, (
        f"the seeded run under a changed validator bought "
        f"{socket.calls_at(A_FACT) - paid_for} answers it had been handed: "
        f"{sorted(_asked_again(second, given))}")
    assert given.untranslated == 0, "an A_fact dossier was seeded unre-addressed"
    # Re-judged, not merely reused: every seeded conclusion was read again under
    # the new validator and superseded where it stood. Site A's verdicts, per
    # `_a_fact_verdicts`: site C's are written fresh by this run and were never
    # anybody's to re-judge.
    assert len(_supersessions(second)) == seeded_verdicts
    standing = [row for row in _a_fact_verdicts(second)
                if row["superseded_by"] is None]
    assert standing and all(
        row["validator_version"] == fact_validation.judgement_version(
            _deps(second))
        for row in standing), {row["validator_version"] for row in standing}
    assert len(_rows(second, "SELECT 1 FROM llm_call_reuse")) == paid_for


def _deps(database):
    """The three callbacks `cli` hands Site A, as `model_facts` bundles them.

    **`normalize` is a CLOSURE, `104` §18.2 gap 3.** This helper named
    `cli.normalize_for_model` from the day it was written, and the assertion that
    reads it could only be reached once the seeded reuse worked (R-172a); by then
    `cli.p1_p7_authorities` had stopped passing that function. Gap 3 gave check 3
    a second half -- `normalize_with_the_persons_own_values(conn)` asks the shipped
    library first and the person's confirmed spellings second -- and
    `judgement_version` digests the bundle, so the superseded spelling computes a
    version no run ever wrote. `_callable_version` digests the closure's module,
    qualname and source rather than the rows behind it, so the connection only has
    to be to a database of this schema.
    """
    conn = sqlite3.connect(database)
    try:
        return fact_validation.FactValidationDependencies(
            normalize=cli.normalize_with_the_persons_own_values(conn),
            contradicts=cli.contradicts_stronger,
            normalize_for_review=cli.normalize_for_review)
    finally:
        conn.close()


def test_the_seed_note_names_the_address_every_dossier_had_before(
        corpus, socket, tmp_path):
    """`104` R-137: an address that moved is written down, never moved in silence.

    A seeded dossier is filed under an address this run recomputed, and the one it
    had in the run it came from is how anybody checks the two against each other.
    The note beside the database carries the map.

    Site A's dossiers on both sides (`104` §17.13 ruling 3). The map is of what was
    SEEDED, and the seeding copies the four `llm_*` tables an identity can be
    reused from; site C records no identity, so a C dossier is in neither
    database's map and comparing against every row of `llm_dossier` would read the
    seeder as having dropped a file it was never given.
    """
    prior_dir, fresh_dir = tmp_path / "prior", tmp_path / "fresh"
    prior_dir.mkdir()
    fresh_dir.mkdir()
    first = prior_dir / f"{SITUATION.replace('.', '_')}.sqlite"
    second = prior_database(fresh_dir, SITUATION)
    _run(corpus, first)

    given = seed(second, first, corpus=corpus)
    write_seeded(fresh_dir, SITUATION, given, source=prior_dir)

    note = json.loads(
        seeded_note(fresh_dir, SITUATION).read_text(encoding="utf-8"))
    assert note["untranslated"] == 0
    addresses = note["addresses"]
    assert addresses
    # Every address the prior run used is a key, and every address this database
    # holds is the value it maps to.
    assert set(addresses) == _a_fact_addresses(first)
    assert set(addresses.values()) == _a_fact_addresses(second)
    assert all(old != new for old, new in addresses.items()), (
        "an A_fact dossier kept the prior run's address, so its bytes still name "
        "the prior run's file")


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


def test_a_changed_file_is_asked_fresh_even_when_the_validator_moved(
        corpus, socket, tmp_path, monkeypatch):
    """The safety half of `104` R-137, with re-judgement switched on.

    R-137 makes a seeded answer readable again, and the thing that must not follow
    is a seeded answer surviving a change to the file it is an answer ABOUT. It
    cannot: `content_hash` is a dimension of the identity, so a rewritten file is
    a different question and the prior is never looked up -- there is nothing to
    re-judge, and the file is asked. The neighbour, untouched, is re-judged from
    its stored response and costs nothing. Site A's calls, per `_Socket`.
    """
    prior_dir, fresh_dir = tmp_path / "prior", tmp_path / "fresh"
    prior_dir.mkdir()
    first, second = prior_dir / "one.sqlite", fresh_dir / "two.sqlite"
    _run(corpus, first)
    paid_for = socket.calls_at(A_FACT)

    (corpus / "week two notes.txt").write_text(
        "Rewritten between the runs. Notes from the seminar on elasticity, with "
        "the essay the instructor set for the vacation.\n")
    monkeypatch.setattr(
        fact_validation, "VALIDATOR_VERSION",
        f"{fact_validation.VALIDATOR_VERSION}+r137")
    given = seed(second, first, corpus=corpus)
    _run(corpus, second)

    assert socket.calls_at(A_FACT) - paid_for == 1, (
        socket.subjects_at(A_FACT)[paid_for:])
    assert _asked_again(second, given) == {"week two notes.txt"}
    assert len(_rows(second, "SELECT 1 FROM llm_call_reuse")) == 1


def test_a_seed_of_a_seed_pairs_every_answer_the_prior_held(
        corpus, socket, tmp_path, monkeypatch):
    """`104` R-141: a prior that was itself seeded is still a prior.

    Measured on the owner's r8, seeded from r6: `answers 0, skipped 238`, "238 not
    in this corpus", while the two `files` tables paired 199 of 199 by path and by
    content hash. A rerun of a rerun paid for everything, which is every rerun
    after the first.

    Site A's calls, per `_Socket`: `answers` counts what the seeding handed on, and
    site C hands on nothing, so the two numbers only compare at the site that
    records an identity.
    """
    a_dir, b_dir, c_dir = tmp_path / "a", tmp_path / "b", tmp_path / "c"
    a_dir.mkdir()
    first, second, third = (a_dir / "x.sqlite", b_dir / "x.sqlite",
                            c_dir / "x.sqlite")
    _run(corpus, first)
    paid_for = socket.calls_at(A_FACT)

    given_b = seed(second, first, corpus=corpus)
    _run(corpus, second)
    assert given_b.skipped == 0 and given_b.answers == paid_for

    monkeypatch.setattr(
        fact_validation, "VALIDATOR_VERSION",
        f"{fact_validation.VALIDATOR_VERSION}+r141")
    given_c = seed(third, second, corpus=corpus)
    _run(corpus, third)

    assert given_c.skipped == 0, (
        f"a seed of a seed left {given_c.skipped} answers behind")
    assert given_c.answers == given_b.answers
    assert socket.calls_at(A_FACT) == paid_for, (
        socket.subjects_at(A_FACT)[paid_for:])


def test_the_note_says_why_each_answer_was_left_behind(
        corpus, socket, tmp_path):
    """`104` R-141: a bare count cannot be diagnosed, and three faults wore one.

    The owner's r8 reported "238 not in this corpus" against a prior whose files
    paired 199 of 199, and the number could not say whether the prior did not know
    the subject, this corpus did not hold the file, or the path had moved.
    """
    prior_dir, fresh_dir = tmp_path / "prior", tmp_path / "fresh"
    prior_dir.mkdir()
    fresh_dir.mkdir()
    first = prior_dir / f"{SITUATION.replace('.', '_')}.sqlite"
    second = prior_database(fresh_dir, SITUATION)
    _run(corpus, first)

    (corpus / "week two notes.txt").rename(corpus / "renamed between runs.txt")
    given = seed(second, first, corpus=corpus)
    write_seeded(fresh_dir, SITUATION, given, source=prior_dir)

    assert given.skipped == 1
    assert given.skipped_reasons == {"path_moved_or_renamed": 1}
    note = json.loads(
        seeded_note(fresh_dir, SITUATION).read_text(encoding="utf-8"))
    assert note["skipped_reasons"] == {"path_moved_or_renamed": 1}
