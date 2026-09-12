# tests/integration/test_site_h_gate.py
"""`00` amendment 7(c): the gate, and what its answer does to the run.

`104` §18.56 graded site G against the second corpus's answer key and found the
shape of the defect this site exists to end: 43 of 45 protection misses were never
put to any model, because the only site that asked about protection asked only
about files the rules could not settle -- and four health forms carrying basis
`detector` with `protected = 0` were cloud-eligible on the rules' word, whose
measured top-1 accuracy on that corpus was 32.2%.

So the question of whether a file may leave the device is its own site, asked of
every file the deterministic layers could not settle either way, over a short
dossier, on this machine and nowhere else. These tests hold that seam end to end
through `cli.main`: which files are asked, what the verdict writes, where the
situation call goes afterwards, and what happens when the prompt row is not there.

**NO OLLAMA AND NO NETWORK.** The stub HTTP server of
`test_local_model_fact_pass` speaks the one endpoint `readers.model_ollama` calls
and answers from the dossier it was handed; the answer function reads the
dossier's own `call_site` and answers the gate's schema, site G's, or site A's.
The stub answers by COPYING a span out of `released_evidence`, because the gate's
citation is checked like every other site's and an invented span would measure the
validator rather than the wiring.
"""
from __future__ import annotations

import io
import json
import sqlite3
from pathlib import Path

import pytest

import cli
from llm_harness.prompt_library import DraftNotInManifest
from model_gate import restricted_kind_vocabulary
from model_situation import NONE_OF_THESE
from privacy.vocabulary import (
    ALWAYS_LOCAL_KIND_RECEIPT, PRIVACY_CLASS_ALWAYS_LOCAL, PRIVACY_CLASS_ORDINARY,
    PROTECTED_KIND_MEDICAL_RECORD,
)
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from test_local_model_fact_pass import (
    MODEL_ID, StubOllama, _answer_for, _corpus, dossier_in,
)
from test_site_g_end_to_end import LABEL, SITUATION, _situation_answer

#: The corpus `_corpus` builds carries one protected file, which the rules hold on
#: a safety term. Named here because two tests are about it.
HELD_NAME = "passport scan.txt"


def _clear(dossier: dict) -> str:
    """The shape the ratified gate text asks for when the file is none of the ten.

    It is the `unknown` shape, which `validation._validate_claim` turns into an
    ABSTAIN verdict -- and at THIS site that is a positive clearance rather than a
    silence, which is what `cli.gate_kind_named_by_verdict` exists to read.
    """
    return json.dumps({"claims": [{
        "payload": {"restricted_kind": NONE_OF_THESE, "alternatives": []},
        "unknown": {"insufficiency_statement":
                    "the text shows coursework, not a record of any listed kind"}}]})


def _naming(kind: str):
    """A gate answer naming one kind, cited out of the dossier's own released text."""
    def answer(dossier: dict) -> str:
        released = [item for item in dossier.get("released_evidence", ())
                    if isinstance(item, dict) and isinstance(item.get("value"), str)
                    and item["value"].strip()]
        if not released:
            return _clear(dossier)
        item = released[0]
        return json.dumps({"claims": [{
            "payload": {"restricted_kind": kind, "alternatives": []},
            "citations": [{"evidence_ref": item["observation_key"],
                           "cited_span": item["value"].strip().splitlines()[0],
                           "why_it_supports": "this line shows the record itself"}],
        }]})
    return answer


def _refusing(dossier: dict) -> str:
    """A kind that is not on the list. The invention this site's validator catches."""
    released = [item for item in dossier.get("released_evidence", ())
                if isinstance(item, dict) and isinstance(item.get("value"), str)
                and item["value"].strip()]
    if not released:
        return _clear(dossier)
    item = released[0]
    return json.dumps({"claims": [{
        "payload": {"restricted_kind": "utility_bill", "alternatives": []},
        "citations": [{"evidence_ref": item["observation_key"],
                       "cited_span": item["value"].strip().splitlines()[0],
                       "why_it_supports": "a perfectly cited invention"}],
    }]})


def _dispatching(gate_answer):
    def answer(payload: str) -> str:
        dossier = dossier_in(payload)
        site = dossier.get("call_site")
        if site == cli.H_RESTRICTED_KIND:
            return gate_answer(dossier)
        if site == cli.G_SITUATION_SENSITIVITY:
            return _situation_answer(dossier)
        return _answer_for(payload)
    return answer


def _run(tmp_path, monkeypatch, gate_answer, *extra: str):
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    with StubOllama(answer=_dispatching(gate_answer)) as stub:
        monkeypatch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
        monkeypatch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
        out = io.StringIO()
        code = cli.main(
            [str(corpus), "--situation", SITUATION, "--label", LABEL,
             "--user", "t", "--database", str(database), *extra], out=out)
    assert code == 0, out.getvalue()
    return database, out.getvalue(), stub


def _read(database: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _file_id(conn, name: str) -> str:
    (row,) = conn.execute(
        "SELECT file_id FROM files WHERE path LIKE ?", (f"%{name}",)).fetchall()
    return row["file_id"]


def _gate_dossiers(conn, subject_ref: str | None = None) -> list[dict]:
    sql = "SELECT payload FROM llm_dossier WHERE call_site = ?"
    params: tuple = (cli.H_RESTRICTED_KIND,)
    if subject_ref is not None:
        sql += " AND subject_ref = ?"
        params += (subject_ref,)
    return [json.loads(row["payload"])
            for row in conn.execute(sql, params).fetchall()]


def _protected_ids(conn) -> set[str]:
    return set(cli._protected_file_ids(conn))


# --- who is asked ----------------------------------------------------------------


def test_the_gate_asks_every_un_held_file_and_never_a_held_one(tmp_path,
                                                               monkeypatch):
    """THE POPULATION, which is the whole of what `104` §18.56 was about.

    Every file version in the roster is asked EXCEPT one a deterministic layer is
    already holding. Not "every file the rules could not settle", which is what
    site G asked and is how 43 of 45 protection misses came to be never put to any
    model; not "every file", which would spend a call per file to be told what a
    rule already knows.

    Measured on the wire: a dossier at this call site for every file but the held
    one, and none for it.

    SABOTAGE: drop the `current.protected and current.basis in SAFETY_DOMAIN_BASES`
    test and the held file gets a dossier -- one call spent to re-ask a decided
    question, on the site that runs over the whole roster. Or restore a
    `recognised is not None: continue` and the count falls to the files the rules
    could not settle, which is the state the amendment ended.
    """
    database, _said, _stub = _run(tmp_path, monkeypatch, _clear)
    conn = _read(database)

    asked = {dossier["subject_ref"] for dossier in _gate_dossiers(conn)}
    held = _file_id(conn, HELD_NAME)
    roster = {row["file_id"] for row in
              conn.execute("SELECT file_id FROM files").fetchall()}

    assert held not in asked, (
        "a file a rule is already holding was put to the gate; the gate is for "
        "the files the deterministic layers could not settle")
    assert held in _protected_ids(conn), "the held file's hold stands, untouched"
    unheld = roster - _protected_ids(conn)
    assert unheld, "the corpus has no un-held file, so this test measures nothing"
    assert unheld <= asked, (
        f"{sorted(unheld - asked)} were neither held nor asked, which is the "
        f"silence `104` §18.56 measured")


def test_the_gate_dossier_is_short_and_carries_no_frame_items(tmp_path,
                                                              monkeypatch):
    """THE SHAPE. `GATE_DOSSIER_TOKENS` bounds it, the eleven are its vocabulary,
    and the only items are the file's own readings.

    The ten kinds and what each one means are in the ratified template, which is
    byte-identical on every file, so an item repeating them would put the constant
    part of the prompt into the per-file part of the dossier -- the opposite of
    `104` R-58 -- on the one call this product makes about every file it scans.

    SABOTAGE: add candidate items to `build_gate_request` and the kinds assertion
    below goes red; raise the bound to `GROUPING_LIMITS.max_dossier_tokens` and the
    gate costs what site G costs on every file in the corpus.
    """
    database, _said, _stub = _run(tmp_path, monkeypatch, _clear)
    conn = _read(database)

    dossiers = _gate_dossiers(conn)
    assert dossiers, "no dossier was built at the gate"
    for dossier in dossiers:
        assert tuple(dossier["allowed_vocabulary"]) == restricted_kind_vocabulary()
        assert dossier["allowed_vocabulary"][-1] == NONE_OF_THESE
        assert len(dossier["allowed_vocabulary"]) == 11
        assert dossier["max_dossier_tokens"] == cli.GATE_DOSSIER_TOKENS
        assert cli.GATE_DOSSIER_TOKENS < cli.GROUPING_LIMITS.max_dossier_tokens
        kinds = {item["kind"] for item in dossier["evidence_items"]}
        assert kinds <= {"excerpt", "identifier"}, kinds
        assert dossier["released_evidence"], (
            "the gate was shown a menu and no text to read the answer out of")
        assert dossier["field_glossary"] == []
        assert dossier["folder_levels"] == []


def test_the_gate_is_answered_on_this_device_whatever_its_row_says(tmp_path,
                                                                   monkeypatch):
    """LOCAL ONLY, BY THE SITE'S NAME AND NOT BY ITS ROW'S WORD.

    Every other site is refused the cloud until its own text is ratified, and the
    day the owner ratifies it the site may send. The gate may not, ever: it is the
    site that decides whether a file may leave the device, so asking it off the
    device would answer the question by sending the file. That is `00`'s own
    sentence about the four safety domains and amendment 5's ruling read one step
    earlier.

    The row is `ratified_local` today, which would give the same answer -- so the
    test asserts the STRONGER thing directly, at the gate that decides it, with
    the row's own word out of the way.

    SABOTAGE: delete the `call_site == H_RESTRICTED_KIND` arm from
    `observe_locality_permits` and this goes red the day the owner writes
    `ratified` on the gate's row.
    """
    assert cli.observe_locality_permits(cli.H_RESTRICTED_KIND, cli.LOCAL)
    assert not cli.observe_locality_permits(cli.H_RESTRICTED_KIND, cli.CLOUD)
    # And it is not the row's word doing it: the same call with the row reading
    # `ratified` -- the word that opens the internet everywhere else -- still says
    # no. `_template_id_for` is what the row-reading path would consult.
    assert cli._template_id_for(cli.H_RESTRICTED_KIND) == cli.GATE_ROW[0]

    database, _said, _stub = _run(tmp_path, monkeypatch, _clear)
    conn = _read(database)
    localities = {row["locality"] for row in conn.execute(
        "SELECT DISTINCT locality FROM llm_release_audit WHERE stage = ?",
        ("restricted_kind_gate",)).fetchall()}
    assert localities <= {cli.LOCAL}, localities


# --- what the verdict writes -----------------------------------------------------


@pytest.mark.skipif(not cli.GATE_MAY_WRITE_A_CLASSIFICATION,
                    reason="P7 carries `local_model_gate`; this is the other arm")
def test_a_missing_basis_makes_the_site_record_only_rather_than_failing_the_run(
        tmp_path, monkeypatch):
    """THE STATE THIS BUILD IS IN, and it must not be a crash.

    The owner ratified the gate's text on 12 September, so the site applies its
    answers -- and `privacy.vocabulary.CLASSIFICATION_BASES` does not yet carry
    `local_model_gate`, so `ClassificationRecord` refuses the row. Left alone that
    is a `ValueError` from inside P7's constructor on the first cleared file of a
    scan of somebody's home directory: a fault reported in the one place a person
    cannot act on it, on the site that decides whether their files may be sent.

    `GATE_MAY_WRITE_A_CLASSIFICATION` asks the question once at import and makes
    the site record-only instead: dossier and verdict stored, counts saying what
    the gate would have decided, no row written. This test runs on the arm where
    the patch HAS landed; the arm where it has not is the one below it.
    """
    database, _said, _stub = _run(tmp_path, monkeypatch, _clear)
    conn = _read(database)
    assert _gate_dossiers(conn), "the record-only site records nothing"


def test_the_gate_records_its_verdict_and_writes_no_row_without_the_basis(
        tmp_path, monkeypatch):
    """The other arm of the same rule, and the one this build takes today.

    Record-only means RECORDED: the dossier is stored, the response is stored, the
    verdict is stored, and the screen says what the gate decided. What is not done
    is the act -- no classification row, so nothing is cleared for the cloud and
    nothing is protected on the model's word.

    SABOTAGE: drop `GATE_MAY_WRITE_A_CLASSIFICATION` from the guard in
    `ask_the_gate` and the run raises `ValueError` from P7's constructor on the
    first cleared file.
    """
    database, said, _stub = _run(tmp_path, monkeypatch, _clear)
    conn = _read(database)

    assert _gate_dossiers(conn), "no dossier at the gate"
    rows = conn.execute(
        "SELECT COUNT(*) AS n FROM classifications WHERE basis = ?",
        (cli.LOCAL_MODEL_GATE,)).fetchone()
    if cli.GATE_MAY_WRITE_A_CLASSIFICATION:
        pytest.skip("P7 carries the basis; the writing arm is tested above")
    assert rows["n"] == 0, (
        "a gate row was written under a basis P7's closed vocabulary does not "
        "carry, which the store refuses")
    assert "What may be sent" in said, (
        "record-only is still reported: a person is owed what the gate decided "
        "even on a run that acted on none of it")


def test_the_verdict_writes_the_row_the_amendment_describes(tmp_path, monkeypatch):
    """THE TWO ROWS, built directly, because the store cannot hold them yet.

    `gate_classification` is the one place a gate verdict becomes a record, and
    what it must produce is exactly what `00` amendment 7(c) names: a named kind is
    protected with the kind's own privacy class under `105` §14.3's precedence, and
    `none_of_these` with the deterministic layers silent is ordinary,
    `personal_non_sensitive`, `protected = 0` -- which is the row that lets a file
    reach a cloud model at all.

    Built here rather than read out of a run because
    `privacy.vocabulary.CLASSIFICATION_BASES` does not yet carry
    `local_model_gate`: the record is constructed with the vocabulary widened by
    the one line the patch adds, so this test measures the RECORD and the test
    above measures what the product does while the patch is missing. The
    monkeypatch is that single line and nothing else.

    SABOTAGE: pass `None` instead of `()` to `privacy_class_for` for a cleared file
    and the row reads `pending`, which refuses the cloud to every file the gate
    cleared -- the trade the owner declined.
    """
    import privacy.classification as classification
    from privacy.vocabulary import CLASSIFICATION_BASES

    monkeypatch.setattr(classification, "CLASSIFICATION_BASES",
                        CLASSIFICATION_BASES + (cli.LOCAL_MODEL_GATE,))
    question = cli.GateQuestion(
        file_id="f-1", content_hash="a" * 64, evidence_refs=("sha256:" + "c" * 64,))

    cleared = cli.gate_classification(
        question, NONE_OF_THESE, observed_at="2026-09-12T00:00:00Z",
        deterministic_layers_silent=True)
    assert cleared.basis == cli.LOCAL_MODEL_GATE
    assert cleared.protected is False
    assert cleared.handling_class == cli.ORDINARY_CLASS == "personal_non_sensitive"
    assert cleared.privacy_class == PRIVACY_CLASS_ORDINARY
    assert cleared.evidence_refs == question.evidence_refs

    named = cli.gate_classification(
        question, PROTECTED_KIND_MEDICAL_RECORD,
        observed_at="2026-09-12T00:00:00Z", deterministic_layers_silent=True)
    assert named.protected is True
    assert named.privacy_class == "protected"
    assert named.handling_class == cli.GATE_PROTECTED_CLASS

    always_local = cli.gate_classification(
        question, ALWAYS_LOCAL_KIND_RECEIPT, observed_at="2026-09-12T00:00:00Z",
        deterministic_layers_silent=True)
    assert always_local.privacy_class == PRIVACY_CLASS_ALWAYS_LOCAL
    assert always_local.protected is True

    # SILENCE WRITES NOTHING, and a clearance over a layer that spoke writes
    # nothing either: the model may not release what a deterministic layer caught.
    assert cli.gate_classification(
        question, None, observed_at="2026-09-12T00:00:00Z",
        deterministic_layers_silent=True) is None
    assert cli.gate_classification(
        question, NONE_OF_THESE, observed_at="2026-09-12T00:00:00Z",
        deterministic_layers_silent=False) is None


def test_a_kind_outside_the_eleven_clears_nothing_and_names_nothing(tmp_path,
                                                                    monkeypatch):
    """`recognition/_CONTRACT.md` rule 5's invention wearing a model's face, at the
    one site where believing it would send somebody's file.

    The answer cites perfectly and names `utility_bill`, which is not one of `105`
    §13.3's ten. P8's site hook refuses it (`gate_validation._gate_site`), the
    reader reads nothing off a refused verdict, and the file is neither cleared nor
    protected -- it stays unclassified, which keeps it local.

    SABOTAGE: return `None` from `_gate_site` instead of a `SCHEMA_INVALID`
    verdict, and an invented kind reaches `gate_kind_named_by_verdict`.
    """
    database, said, _stub = _run(tmp_path, monkeypatch, _refusing)
    conn = _read(database)

    assert _gate_dossiers(conn), "the answer never reached a verdict"
    rows = conn.execute(
        "SELECT COUNT(*) AS n FROM classifications WHERE basis = ?",
        (cli.LOCAL_MODEL_GATE,)).fetchone()
    assert rows["n"] == 0
    assert "asked and left alone" in " ".join(said.split())


# --- where the situation call goes afterwards ------------------------------------


def test_a_cleared_file_is_routed_to_the_cloud_and_a_held_one_is_not(tmp_path):
    """THE ROUTE, asked of the same predicate the run asks -- `target_for` over a
    real store, with two real classification rows in it.

    `00` amendment 7(c)'s whole point is what happens AFTER the gate: a file it
    cleared may have its situation asked of a model off this device, and a file
    anything is holding may not. This is that sentence as the router answers it,
    and the router is the door's own rule rather than a second spelling of it
    (`104` R-02).

    The cleared row is written under `local_model_situation` rather than
    `local_model_gate`, and the substitution is named here so it cannot be mistaken
    for the thing being tested: both are `llm_supported`, ordinary,
    `protected = 0`, and the route reads the FLAG and the class rather than the
    basis word -- so this measures the routing rule the gate's row will meet the
    day P7 carries its basis. `test_the_verdict_writes_the_row_the_amendment_
    describes` is where the basis itself is pinned.

    SABOTAGE: make `ask_the_situation` build one route for the whole pass instead
    of asking per file, and the held file takes the cleared file's target.
    """
    from privacy.classification import ClassificationRecord
    from privacy.classification_store import ClassificationStore

    database = tmp_path / "route.sqlite"
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cli._bootstrap(conn)
    store = ClassificationStore(conn)

    cleared, held = "file-cleared", "file-held"
    for file_id, protected, handling in ((cleared, False, cli.ORDINARY_CLASS),
                                         (held, True, cli.GATE_PROTECTED_CLASS)):
        conn.execute(
            "INSERT INTO files (file_id, path, content_hash, size_bytes) "
            "VALUES (?, ?, ?, ?)", (file_id, f"/c/{file_id}", "a" * 64, 1))
        store.write(ClassificationRecord(
            file_id=file_id, content_hash="a" * 64, handling_class=handling,
            protected=protected, basis="local_model_situation",
            evidence_refs=("sha256:" + "c" * 64,), reliability_state="llm_supported",
            observed_at="2026-09-12T00:00:00Z",
            privacy_class="protected" if protected else PRIVACY_CLASS_ORDINARY))
    conn.commit()

    routing = cli.TierRouting(clients=cli.two_target_clients_for_a_test()) \
        if hasattr(cli, "two_target_clients_for_a_test") else None
    if routing is None:
        pytest.skip("this deployment's routing fixture is not exposed for a "
                    "two-target test; the per-file predicate is pinned below")

    route_for = cli.target_for(conn, routing, cli.G_SITUATION_SENSITIVITY,
                               operation_mode="hybrid")
    assert route_for(cleared)[1].locality == cli.CLOUD
    assert route_for(held)[1].locality == cli.LOCAL


def test_the_predicate_that_routes_a_cleared_file_is_the_doors_own(tmp_path):
    """The same claim without a routing fixture: `model_route_permitted` is what
    `target_for` asks per file, and it answers on the ROW.

    A cleared file -- ordinary, `protected = 0` -- is permitted a cloud target; a
    file anything is holding is not; a file with no row at all is not, because
    `unclassified_denies` refuses every cloud release of one unconditionally, which
    is the rule that made 153 of the second corpus's files local-only and is
    exactly what the gate's clearance is for.

    SABOTAGE: respell the gate's rule here instead of calling it and the two drift,
    which is `104` R-02 measured once already.
    """
    from privacy.classification import ClassificationRecord
    from privacy.classification_store import ClassificationStore

    database = tmp_path / "predicate.sqlite"
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cli._bootstrap(conn)
    store = ClassificationStore(conn)

    for file_id, protected, handling in (("cleared", False, cli.ORDINARY_CLASS),
                                         ("held", True, cli.GATE_PROTECTED_CLASS)):
        conn.execute(
            "INSERT INTO files (file_id, path, content_hash, size_bytes) "
            "VALUES (?, ?, ?, ?)", (file_id, f"/c/{file_id}", "a" * 64, 1))
        store.write(ClassificationRecord(
            file_id=file_id, content_hash="a" * 64, handling_class=handling,
            protected=protected, basis="local_model_situation",
            evidence_refs=("sha256:" + "c" * 64,), reliability_state="llm_supported",
            observed_at="2026-09-12T00:00:00Z",
            privacy_class="protected" if protected else PRIVACY_CLASS_ORDINARY))
    conn.execute(
        "INSERT INTO files (file_id, path, content_hash, size_bytes) "
        "VALUES (?, ?, ?, ?)", ("unread", "/c/unread", "b" * 64, 1))
    conn.commit()

    to_cloud = cli.model_route_permitted(
        conn, locality=cli.CLOUD,
        unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
        operation_mode="hybrid")
    to_local = cli.model_route_permitted(
        conn, locality=cli.LOCAL,
        unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
        operation_mode="hybrid")

    assert to_cloud("cleared"), (
        "a file the gate cleared is refused the cloud, so the amendment buys "
        "nothing at all")
    assert not to_cloud("held")
    assert not to_cloud("unread"), (
        "a file nothing has read is cloud-eligible, which is the rule the gate "
        "exists to satisfy rather than to bypass")
    for file_id in ("cleared", "held", "unread"):
        assert to_local(file_id), (
            "the local route is unchanged: this amendment opens the cloud for a "
            "cleared file and closes nothing")


def test_the_situation_dossier_bound_is_the_targets(tmp_path):
    """`SITUATION_DOSSIER_TOKENS_CLOUD` for a cloud target, the shared ceiling for
    a local one, and the cloud bound is under P1's stored ceiling.

    The last clause is the one that would break silently: the door measures the
    released values against the STORED number and never the caller's echo (M9), so
    a cloud bound above the stored ceiling is a call routed, assembled, and then
    denied -- coverage lost with nothing on the screen naming the reason.

    SABOTAGE: raise `SITUATION_DOSSIER_TOKENS_CLOUD` over 4,000 and this goes red
    here rather than at a person's corpus.
    """
    database = tmp_path / "bound.sqlite"
    conn = sqlite3.connect(database)
    cli._bootstrap(conn)
    from database_agent.budget import get_ceiling

    stored = get_ceiling(conn, "model.max_dossier_tokens_per_call")
    assert stored == cli.GROUPING_LIMITS.max_dossier_tokens
    assert cli.SITUATION_DOSSIER_TOKENS_CLOUD <= stored, (
        "the cloud bound is above the ceiling the door measures against, so every "
        "cloud situation call would be denied after being paid for")
    assert cli.GATE_DOSSIER_TOKENS <= stored
    assert cli.SITUATION_DOSSIER_TOKENS_CLOUD < cli.GROUPING_LIMITS.max_dossier_tokens


# --- the prompt row --------------------------------------------------------------


def test_a_missing_gate_row_makes_the_site_ask_nothing_rather_than_crash(
        monkeypatch):
    """THE LOADER SHIM. A prompt row is the owner's act and this file invents none.

    `gate_prompt` answers `None` for a row the manifest does not carry, and
    `_model_fact_pass` reads that as a site that asks nothing: no dossier, no
    bytes, no verdict, and the run is the run it was before this site existed. A
    crash here would be the product refusing to scan a person's folder because a
    prompt the owner has not yet been shown is missing from the library.

    `prompt_for` is deliberately NOT tolerant: a caller that came for the bytes is
    asking a different question and is refused by name.

    SABOTAGE: let `DraftNotInManifest` out of `gate_prompt` and every run on a
    build without the row dies at the composition root.
    """
    monkeypatch.setattr(cli, "GATE_ROW", ("gate.unratified.not-a-row.2026-01-01",
                                          "no-such-candidate"))
    assert cli.gate_prompt() is None
    with pytest.raises(DraftNotInManifest):
        cli.prompt_for(cli.H_RESTRICTED_KIND)


def test_the_rows_status_is_read_off_the_manifest_and_never_assumed():
    """Both sites' permissions come from `draft_status`, which reads the row.

    `104` §15.1's two words are two permissions -- act on the answer, and let the
    bytes cross the internet -- and neither is a literal anywhere in this
    deployment. The gate carries the first and is refused the second by its own
    name; site G carries both since the owner's ratification of 12 September.

    SABOTAGE: hard-code `ratified=True` in `gate_prompt` and the site starts
    applying an answer nobody approved, on the site that decides whether files may
    be sent.
    """
    from llm_harness.prompt_library import draft_status

    assert draft_status(cli.GATE_ROW[0]) == "ratified_local"
    assert cli.gate_prompt().ratified is (
        draft_status(cli.GATE_ROW[0]) in cli.STATUS_APPLIES)
    assert draft_status(cli.SITUATION_ROW[0]) == "ratified"
    assert cli.situation_prompt().ratified is (
        draft_status(cli.SITUATION_ROW[0]) in cli.STATUS_APPLIES)
    # The gate's bytes may not cross whatever the row says; site G's may, now.
    assert not cli.observe_locality_permits(cli.H_RESTRICTED_KIND, cli.CLOUD)
    assert cli.observe_locality_permits(cli.G_SITUATION_SENSITIVITY, cli.CLOUD)
