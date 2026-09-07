# tests/integration/test_a_fact_call_cache.py
"""R-13: a question already answered under the same identity is not asked again.

`104` R-13: *"Dossier rows dedupe by content; no prior-verdict lookup, so declined
fields are re-asked and re-spent; no invalidation on prompt, model, schema or policy
change."* `00`:44 states the cache the design wants -- *"The cache key includes
content hash, extractor version, analysis tier, model identifier when relevant, and
prompt fingerprint for model-derived results ... makes model or prompt changes
auditable."*

**Measured before anything was built**, two sparse coursework files through the real
`cli.main` with the socket replaced by a counting stub: run 1 made **2** model calls
and run 2 made **2 more**, for 14 `llm_verdict` rows over 8 distinct questions --
every one of them an `abstain` the model had already given. Nothing about the corpus,
the prompt, the model or the policy had changed.

**Everything here is real except the socket.** `readers.model_routing.deepseek_invoke`
is the documented deployment seam and the stub is bound in its place, so the gate, the
release ledger, the transport, the validator, `apply_verdict` and the whole of
`cli.run` are the production path. Counting `invoke` calls counts model calls exactly:
`transport.issue` consumes one release per invoke and `harness.run_call` reserves one
budget slot per invoke.
"""
from __future__ import annotations

import dataclasses
import io
import json
import pathlib
import sqlite3
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from readers import model_routing  # noqa: E402
from readers.model_routing import MODEL_NAME_OF_TIER  # noqa: E402
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME  # noqa: E402

SITUATION = "academic.coursework"

#: Two files with releasable text and NO deterministic course code. Both matter: a
#: file whose subject the rule stage settles has no open field left and never reaches
#: a model at all, so a corpus of syllabi would measure nothing here (it was tried:
#: zero calls, both runs).
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


class _Socket:
    """Every model call this run makes, and the dossier each one carried."""

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
            # DECLINE EVERYTHING. The R-13 case is the declined field: it settles
            # nothing, so `pending_fields_for` offers it again for ever.
            fields = self._body(payload)["allowed_vocabulary"]
            return json.dumps({"claims": [
                {"payload": {"field": field},
                 "unknown": {"insufficiency_statement":
                             "nothing in the released evidence names it"}}
                for field in fields]}).encode("utf-8")
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


def _run(corpus, *extra) -> str:
    out = io.StringIO()
    cli.main([str(corpus), "--situation", SITUATION, "--label", "Coursework",
              "--user", "jy", "--database", str(corpus.parent / "plan.sqlite"),
              *extra], out=out)
    return out.getvalue()


def _rows(corpus, sql, *params):
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, params)]
    finally:
        conn.close()


def _count(corpus, table) -> int:
    return _rows(corpus, f"SELECT count(*) AS n FROM {table}")[0]["n"]


# --- the four the register asks for ---------------------------------------------


def test_an_unchanged_second_run_asks_no_model_at_all(corpus, socket):
    """The whole of R-13, in one number. Measured before the fix: 2, then 2 more."""
    _run(corpus, "--enable-cloud")
    first = len(socket)
    assert first == 2, socket.subjects()

    _run(corpus)

    assert len(socket) == first, (
        f"the second run asked {len(socket) - first} more questions it already had "
        f"answers to: {socket.subjects()[first:]}")


def test_changing_only_the_prompt_re_asks_every_file(corpus, socket, monkeypatch):
    """`00`:44 wants "model or prompt changes auditable". A new prompt is a new
    question about the same evidence, and no prior answer speaks for it.

    Only `template_id` moves, so the ratified bytes and their digest are untouched
    and this changes nothing but the fingerprint -- which is exactly the dimension
    under test.
    """
    _run(corpus, "--enable-cloud")
    first = len(socket)

    real = cli.a_fact_prompt()
    monkeypatch.setattr(cli, "a_fact_prompt", lambda: dataclasses.replace(
        real, template_id=f"{real.template_id}.a-second-revision"))
    _run(corpus)

    assert len(socket) - first == 2


def test_changing_one_files_content_re_asks_that_file_alone(corpus, socket):
    """Invalidation is per dimension AND per subject: one file's hash is not the
    other's, so one edit costs one call and not a whole corpus."""
    _run(corpus, "--enable-cloud")
    first = len(socket)

    (corpus / "reading notes.txt").write_text(
        "Rewritten notes for this seminar. The lecture now covers rotational "
        "motion, and the problem set is due the following Tuesday.\n")
    _run(corpus)

    assert len(socket) - first == 1
    asked = socket.subjects()[first:]
    unchanged = _rows(
        corpus, "SELECT file_id FROM files WHERE current_path LIKE '%week two%'")
    assert asked[0] not in {row["file_id"] for row in unchanged}


def test_a_declined_field_is_not_re_asked_under_the_same_identity(corpus, socket):
    """The verdict rows are the evidence: 8 questions asked once, not twice.

    Before the fix this corpus produced 14 verdict rows over two runs, every one an
    `abstain`, and 6 of them were the same field being asked a second time.
    """
    _run(corpus, "--enable-cloud")
    after_first = _rows(
        corpus,
        "SELECT dossier_id, claim_ref FROM llm_verdict WHERE outcome = 'abstain'")
    _run(corpus)
    after_second = _rows(
        corpus,
        "SELECT dossier_id, claim_ref FROM llm_verdict WHERE outcome = 'abstain'")

    assert after_second == after_first
    assert len({(row["dossier_id"], row["claim_ref"]) for row in after_first}) == \
        len(after_first)


# --- and the row that says a reuse happened --------------------------------------


def test_the_reuse_is_recorded_and_names_the_prior_dossier(corpus, socket):
    """"A recorded row that names the prior." Not an event: `events.EVENT_TYPES` is
    a closed set and `database_agent/events.py` says registration "is a spec-level
    act ... There is no run-time registration call", so a `model_call_reused` name
    is the owner's to approve. The row carries the provenance in the meantime."""
    _run(corpus, "--enable-cloud")
    assert _count(corpus, "llm_call_reuse") == 0
    identities = _rows(corpus, "SELECT * FROM llm_call_identity")
    assert len(identities) == 2

    _run(corpus)

    reuses = _rows(corpus, "SELECT * FROM llm_call_reuse")
    assert len(reuses) == 2
    priors = {row["dossier_id"] for row in identities}
    for reuse in reuses:
        assert reuse["prior_dossier_id"] in priors
        assert reuse["identity_id"] in {row["identity_id"] for row in identities}
        assert json.loads(reuse["reused_fields"])


def test_the_identity_row_says_what_it_was_keyed_on(corpus, socket):
    """A digest nobody can read back is a cache nobody can audit. The row carries
    the dimension mapping the digest was taken over, so a miss can be explained."""
    _run(corpus, "--enable-cloud")
    rows = _rows(corpus, "SELECT * FROM llm_call_identity")

    for row in rows:
        dimensions = json.loads(row["dimensions"])
        assert set(dimensions) == {
            "call_site", "content_hash", "extractor_versions", "model_id",
            "plan_version", "policy", "prompt_fingerprint", "schema_id",
            "subject_ref"}
        assert dimensions["call_site"] == cli.A_FACT
        assert dimensions["model_id"] == "a-logician"
        assert len(dimensions["content_hash"]) == 64


def test_the_policy_dimension_is_the_policys_content_and_not_its_version(
        corpus, socket):
    """MEASURED, and it is why the design's own word could not be used as written.

    `00`:44 lists the policy among the cache key's terms and `privacy.policy.
    _persist` mints `policy-{uuid4}` on every call -- so two runs under an identical
    policy carry two version strings. Keyed on the string, the cache could never hit
    once; keyed on the policy's CONTENT, it hits exactly when the policy has not
    changed. Both runs below are under one unchanged policy and two version ids.
    """
    _run(corpus, "--enable-cloud")
    _run(corpus)

    versions = {row["policy_version"] for row in _rows(
        corpus, "SELECT DISTINCT policy_version FROM llm_dossier")}
    assert len(versions) == 1, "only the first run built a dossier"

    policies = _rows(corpus, "SELECT policy_version FROM privacy_policies")
    assert len({row["policy_version"] for row in policies}) > 1, policies
    digests = {json.loads(row["dimensions"])["policy"]
               for row in _rows(corpus, "SELECT dimensions FROM llm_call_identity")}
    assert len(digests) == 1
