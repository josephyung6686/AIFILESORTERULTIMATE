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

**AND A LOCAL MODEL IS NOW PART OF THE DEPLOYMENT, `00` amendment 7(c).** This file
used to configure a cloud key and nothing else, and that stopped being a deployment
site A can run in: the gate, `cli.ask_the_gate`, reads every un-held file on this
device BEFORE anything about it may be sent, `cli.CLOUD_CLEARING_BASES` is what
`model_route_permitted` asks for a cloud target, and the rules' own word is no
longer among them. With no local model the gate has no destination, no file is
cleared, and site A is refused the cloud for every one of them -- measured here as
`calls_at(A_FACT) == 0` where every pin below says 2. So the local half is
`StubOllama`, `test_local_model_fact_pass`'s own server, and it answers the gate
`none_of_these` and DECLINES the situation. Both seams are stubs; neither is the
thing under test. `test_the_scoreboard_reuses_a_prior_runs_answers` carries the long
form of the same argument, including why the situation is declined rather than
answered: amendment 7(c) asks site G of the whole library, so naming an option would
be naming whichever the library lists first, and a protected one would hold the file
and route site A local -- emptying the socket this file counts.

**AND THE GATE RECORDS AN IDENTITY OF ITS OWN** (45d36ca0), so `llm_call_identity`
and `llm_call_reuse` are no longer site A's alone and the reads below that used to
need no call-site clause now need one. Every count in this file is site A's, stated
at site A.

**Everything here is real except the two model seams.**
`readers.model_routing.deepseek_invoke`
is the documented deployment seam and the stub is bound in its place, so the gate, the
release ledger, the transport, the validator, `apply_verdict` and the whole of
`cli.run` are the production path. Counting `invoke` calls counts model calls exactly:
`transport.issue` consumes one release per invoke and `harness.run_call` reserves one
budget slot per invoke -- but it counts EVERY site's, and since `104` §17.13 ruling 3
and R-170 that is no longer site A's alone. Every count below is taken at one call
site, and the argument for that is in `_Socket`.

**R-109 came back once, through the cache's own door, and this file is where it would
be caught.** `104` R-172a: `cli.standing_consent_grants` recorded §18.7's protected-
files ruling as a grant over the scan run id -- a fresh uuid every run -- and `policy`
is one of `store.CALL_IDENTITY_DIMENSIONS`, so every identity digest moved on every
run and no answer was ever reused again. It is fixed (`model_facts.
_consent_grants_content` records a standing grant under a stable scope), and the
evidence that it is fixed is `test_the_reuse_is_recorded_and_names_the_prior_dossier`
below: two identities on run 1 and two reuse rows on run 2, over a corpus nothing
about which changed.
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
    """Every model call this run makes, and the dossier each one carried.

    **COUNTED PER CALL SITE, `104` §17.13 ruling 3 and R-170.** When R-13 was measured
    this corpus produced one model call per file and nothing else, so a bare
    `len(self)` was a site-A total. §17.13 moved site C's `eliminate-v2` from
    `ratified_local` to `ratified` and R-170 made the route a per-FILE question, so a
    run now also sends a `C_placement` dossier for each file P11 proposes a folder
    for -- through this same stubbed `deepseek_invoke`, on the cloud run and on the
    plain one alike, because the route decides WHERE a call goes and not WHETHER
    there is one.

    R-13 is about a QUESTION ALREADY ANSWERED not being asked again, and the thing an
    answer is looked up by is an identity: `llm_call_identity` is written at site A and
    site C records none, so there is nothing of C's for `_reuse_is_current` to find and
    C repeats itself on every run by construction. Folding C into the totals would
    report this file's own defect -- a second run buying answers it already had -- when
    what moved was a site that was never given one. So every pin states site A's cache
    at `calls_at(A_FACT)` and site C's repetition on its own line: a placement that
    starts reusing, or stops calling, turns a line red instead of quietly moving a
    number the assertion above it reads as site A's.
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
            # SITE G ARRIVES HERE TOO since `00` amendment 7(c): G's row is
            # `ratified` and a file the gate CLEARED may have its situation asked
            # off the device, so the cloud seam sees a situation dossier whose
            # schema is not site A's. Declining it field by field below would be a
            # malformed claim the validator refuses -- the same silence, reached by
            # a fault -- so it is declined in the shape the ratified prompt asks
            # for, and the gate's clearance stands as this file's route.
            if body["call_site"] == cli.G_SITUATION_SENSITIVITY:
                return _decline(body).encode("utf-8")
            # DECLINE EVERYTHING. The R-13 case is the declined field: it settles
            # nothing, so `pending_fields_for` offers it again for ever.
            fields = body["allowed_vocabulary"]
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
    if site == cli.H_RESTRICTED_KIND:
        return _clear(dossier)
    if site == cli.G_SITUATION_SENSITIVITY:
        return _decline(dossier)
    return _answer_for(payload)


@pytest.fixture(autouse=True)
def _local_model(monkeypatch, _no_ambient_key):
    """A local model for the whole test, because a run now needs one to send.

    AUTOUSE AND PER TEST, beside `_no_ambient_key` and for its reason: this is what
    the deployment IS since amendment 7(c), not something one pin arranges. One
    server for the test rather than one per run -- every test here runs the product
    twice over one corpus, and a stub that came and went between them would give the
    second run a different base URL from the first.
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


def _run(corpus, *extra) -> str:
    out = io.StringIO()
    cli.main([str(corpus), "--situation", SITUATION, "--label", "Coursework",
              "--user", "jy", "--database", str(corpus.parent / "plan.sqlite"),
              "--accept-groups",
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


def _a_fact_abstentions(corpus) -> list[dict]:
    """The declined questions of the pass this file is about, and no other site's.

    `104` §17.13 ruling 3: `llm_verdict` carries every site's judgements and the
    dossier is where the site is written down, so the join is what makes "a declined
    FIELD" mean a field and not a placement that found no supported destination.
    """
    return _rows(
        corpus,
        "SELECT v.dossier_id AS dossier_id, v.claim_ref AS claim_ref "
        "FROM llm_verdict v JOIN llm_dossier d ON d.dossier_id = v.dossier_id "
        "WHERE v.outcome = 'abstain' AND d.call_site = ?", cli.A_FACT)


def _a_fact_policy_versions(corpus) -> set[str]:
    """The policy versions site A's dossiers were built under, and no other site's.

    Same reason and the same join. A second run that reuses every one of site A's
    answers builds no site-A dossier at all, so this set stays at one member -- while
    site C, which has no identity to reuse from, builds one under that run's own
    freshly minted `policy-{uuid4}` and would put a second member in an unscoped read.
    """
    return {row["policy_version"] for row in _rows(
        corpus,
        "SELECT DISTINCT policy_version FROM llm_dossier WHERE call_site = ?",
        cli.A_FACT)}


def _identities_at(corpus, call_site) -> list[dict]:
    """The answers ONE site recorded an identity for, and no other site's.

    `llm_call_identity` was site A's alone when this file was written, which is why
    the reads below carried no clause. Since `00` amendment 7(c) the gate records one
    per file too and reuses it (45d36ca0), so an unscoped count reads two sites'
    answers as site A's and doubles on a corpus nothing about which changed. Site C
    and site G record none, so they are in neither number.
    """
    return _rows(
        corpus,
        "SELECT i.* FROM llm_call_identity i JOIN llm_dossier d ON "
        "d.dossier_id = i.dossier_id WHERE d.call_site = ?", call_site)


def _reuses_at(corpus, call_site) -> list[dict]:
    """Questions this run did not ask again AT ONE SITE.

    `llm_call_reuse` carries its own `call_site`, and the scoping is the one
    `_identities_at` argues: the gate saves on the same rows, and site A's number
    must not move when another site starts saving.
    """
    return _rows(corpus, "SELECT * FROM llm_call_reuse WHERE call_site = ?",
                 call_site)


# --- the four the register asks for ---------------------------------------------


def test_an_unchanged_second_run_asks_no_model_at_all(corpus, socket):
    """The whole of R-13, in one number. Measured before the fix: 2, then 2 more.

    The number is site A's, per `_Socket`. Site C's placement is asked on both runs
    and is stated on its own line below.
    """
    _run(corpus, "--enable-cloud")
    first = socket.calls_at(cli.A_FACT)
    placements = socket.calls_at(cli.C_PLACEMENT)
    assert first == len(CORPUS), socket.subjects_at(cli.A_FACT)

    _run(corpus)

    assert socket.calls_at(cli.A_FACT) == first, (
        f"the second run asked {socket.calls_at(cli.A_FACT) - first} more questions "
        f"it already had answers to: {socket.subjects_at(cli.A_FACT)[first:]}")
    # Site C's own line. C records no `llm_call_identity`, so it has no prior answer
    # to be found and repeats what it did on run 1. If it ever stops, the line above
    # keeps its meaning and this one says the corpus changed under it.
    assert socket.calls_at(cli.C_PLACEMENT) == placements * 2, (
        "site C is no longer asked once per run and the count above is measuring "
        "something other than the fact pass")


def test_changing_only_the_prompt_re_asks_every_file(corpus, socket, monkeypatch):
    """`00`:44 wants "model or prompt changes auditable". A new prompt is a new
    question about the same evidence, and no prior answer speaks for it.

    Only `template_id` moves, so the ratified bytes and their digest are untouched
    and this changes nothing but the fingerprint -- which is exactly the dimension
    under test.

    And only site A's prompt moves, which is what makes the site split visible here
    rather than merely tidy: a second revision of A's text is no reason to buy a
    placement again, and site C is asked on the second run for its own reason (it has
    no identity to reuse) and not for this one. Both are stated (`104` §17.13 ruling
    3, and see `_Socket`).
    """
    _run(corpus, "--enable-cloud")
    first = socket.calls_at(cli.A_FACT)
    placements = socket.calls_at(cli.C_PLACEMENT)

    real = cli.a_fact_prompt()
    monkeypatch.setattr(cli, "a_fact_prompt", lambda: dataclasses.replace(
        real, template_id=f"{real.template_id}.a-second-revision"))
    _run(corpus)

    assert socket.calls_at(cli.A_FACT) - first == len(CORPUS), \
        socket.subjects_at(cli.A_FACT)[first:]
    assert socket.calls_at(cli.C_PLACEMENT) == placements * 2, (
        "site C is no longer asked once per run and the count above is measuring "
        "something other than the fact pass")


def test_changing_one_files_content_re_asks_that_file_alone(corpus, socket):
    """Invalidation is per dimension AND per subject: one file's hash is not the
    other's, so one edit costs one call and not a whole corpus.

    One call at site A, per `_Socket` -- and site C's placement is asked for both
    files again either way, which is exactly the repetition that would have been read
    as the untouched file being re-asked.
    """
    _run(corpus, "--enable-cloud")
    first = socket.calls_at(cli.A_FACT)
    placements = socket.calls_at(cli.C_PLACEMENT)

    (corpus / "reading notes.txt").write_text(
        "Rewritten notes for this seminar. The lecture now covers rotational "
        "motion, and the problem set is due the following Tuesday.\n")
    _run(corpus)

    assert socket.calls_at(cli.A_FACT) - first == 1, \
        socket.subjects_at(cli.A_FACT)[first:]
    assert socket.calls_at(cli.C_PLACEMENT) == placements * 2, (
        "site C is no longer asked once per run and the count above is measuring "
        "something other than the fact pass")
    asked = socket.subjects_at(cli.A_FACT)[first:]
    unchanged = _rows(
        corpus, "SELECT file_id FROM files WHERE current_path LIKE '%week two%'")
    assert asked[0] not in {row["file_id"] for row in unchanged}


def test_a_declined_field_is_not_re_asked_under_the_same_identity(corpus, socket):
    """The verdict rows are the evidence: 8 questions asked once, not twice.

    Before the fix this corpus produced 14 verdict rows over two runs, every one an
    `abstain`, and 6 of them were the same field being asked a second time.

    **Read at site A, `104` §17.13 ruling 3.** `llm_verdict` holds every site's
    judgements, and since C's `eliminate-v2` was ratified a run of this corpus writes
    `C_placement` abstentions beside site A's -- a placement with no supported
    destination abstains exactly as a declined field does, under a `claim-N` ref
    rather than a field name. An unscoped read would let the second run's placement
    look like a field being bought twice, which is the defect this pin exists to
    catch. Joined on `llm_dossier.call_site`, the record of which site asked.
    """
    _run(corpus, "--enable-cloud")
    after_first = _a_fact_abstentions(corpus)
    placements = socket.calls_at(cli.C_PLACEMENT)
    _run(corpus)
    after_second = _a_fact_abstentions(corpus)

    assert after_second == after_first
    assert len({(row["dossier_id"], row["claim_ref"]) for row in after_first}) == \
        len(after_first)
    assert socket.calls_at(cli.C_PLACEMENT) == placements * 2, (
        "site C is no longer asked once per run and the rows above are measuring "
        "something other than the fact pass")


# --- and the row that says a reuse happened --------------------------------------


def test_the_reuse_is_recorded_and_names_the_prior_dossier(corpus, socket):
    """"A recorded row that names the prior." Not an event: `events.EVENT_TYPES` is
    a closed set and `database_agent/events.py` says registration "is a spec-level
    act ... There is no run-time registration call", so a `model_call_reused` name
    is the owner's to approve. The row carries the provenance in the meantime.

    The rows read here are SITE A'S (`_identities_at`, `_reuses_at`). `llm_call_
    identity` and `llm_call_reuse` are written where an answer CAN be reused from --
    site C and site G record none -- and that used to make them site A's alone, which
    is why this pin carried no clause. Since `00` amendment 7(c) the gate records one
    per file as well, so an unscoped read is two sites' answers reported as site A's:
    it reads 4 on a two-file corpus and would go on reading 4 with site A's cache
    broken and the gate's working. That is exactly what this pin exists to notice.

    That is why the count is one per file and not one per call -- and why this pin is
    the evidence R-172a is fixed: a dimension that carried the run id would leave both
    tables empty on run 2.
    """
    _run(corpus, "--enable-cloud")
    assert _reuses_at(corpus, cli.A_FACT) == []
    identities = _identities_at(corpus, cli.A_FACT)
    assert len(identities) == 2

    _run(corpus)

    reuses = _reuses_at(corpus, cli.A_FACT)
    assert len(reuses) == 2
    priors = {row["dossier_id"] for row in identities}
    for reuse in reuses:
        assert reuse["prior_dossier_id"] in priors
        assert reuse["identity_id"] in {row["identity_id"] for row in identities}
        assert json.loads(reuse["reused_fields"])


def test_the_identity_row_says_what_it_was_keyed_on(corpus, socket):
    """A digest nobody can read back is a cache nobody can audit. The row carries
    the dimension mapping the digest was taken over, so a miss can be explained.

    `context_refs` is the tenth term, added for `104` R-135: the observation keys of
    readings of OTHER files the call was shown. It is `[]` for a file with no anchor
    near it, which is every file in this corpus, and the term exists because the nine
    above cannot tell a call that was shown a syllabus from one that was not --
    `extractor_versions` is a set of `(name, version)` pairs and a syllabus is read by
    the same extractor as the coursework beside it.

    SITE A'S ROWS (`_identities_at`), since `00` amendment 7(c): the gate records an
    identity too, and its dimensions are its own -- another `call_site`, the local
    model's id -- so the loop below would be asserting site A's ten terms of a row
    that was never site A's.
    """
    _run(corpus, "--enable-cloud")
    rows = _identities_at(corpus, cli.A_FACT)
    assert len(rows) == len(CORPUS)

    for row in rows:
        dimensions = json.loads(row["dimensions"])
        assert set(dimensions) == {
            "call_site", "content_hash", "context_refs", "extractor_versions",
            "max_dossier_tokens", "model_id", "plan_version", "policy",
            "prompt_fingerprint", "schema_id", "subject_ref"}
        assert dimensions["context_refs"] == []
        # The eleventh term (13 Sep 2026): the bound the dossier was built under.
        assert dimensions["max_dossier_tokens"] == cli.GROUPING_LIMITS.max_dossier_tokens
        assert dimensions["call_site"] == cli.A_FACT
        assert dimensions["model_id"] == "a-sprinter"
        assert len(dimensions["content_hash"]) == 64


def test_the_policy_dimension_is_the_policys_content_and_not_its_version(
        corpus, socket):
    """MEASURED, and it is why the design's own word could not be used as written.

    `00`:44 lists the policy among the cache key's terms and `privacy.policy.
    _persist` mints `policy-{uuid4}` on every call -- so two runs under an identical
    policy carry two version strings. Keyed on the string, the cache could never hit
    once; keyed on the policy's CONTENT, it hits exactly when the policy has not
    changed. Both runs below are under one unchanged policy and two version ids.

    The dossier count is read at site A (`104` §17.13 ruling 3, see
    `_a_fact_policy_versions`); the digests need no clause, because
    `llm_call_identity` is written where an answer can be reused from and site C
    records none. That asymmetry is what the middle assertion now rests on: the second
    run DID mint a second `policy-{uuid4}` and site C's dossier is built under it, so
    the string moved exactly as this pin says it does -- and site A's cache did not
    notice, which is the claim.
    """
    _run(corpus, "--enable-cloud")
    _run(corpus)

    assert len(_a_fact_policy_versions(corpus)) == 1, \
        "only the first run built a site-A dossier"
    # And the second run's own version DID reach a dossier, so the line above is a
    # cache hit and not a run that built nothing: site C has no identity to reuse
    # from, so it builds one under the freshly minted id every time. Two versions
    # over both sites, one over site A.
    every_version = {row["policy_version"] for row in _rows(
        corpus, "SELECT DISTINCT policy_version FROM llm_dossier")}
    assert len(every_version) == 2, every_version

    policies = _rows(corpus, "SELECT policy_version FROM privacy_policies")
    assert len({row["policy_version"] for row in policies}) > 1, policies
    # SITE A'S DIGESTS. The gate records an identity too since `00` amendment 7(c)
    # and its policy term is taken over the same content, so an unscoped read would
    # very likely still say 1 -- and would say it about a set this pin is not making
    # a claim about. Site A's cache is what did not notice the new version string.
    digests = {json.loads(row["dimensions"])["policy"]
               for row in _identities_at(corpus, cli.A_FACT)}
    assert len(digests) == 1


def test_the_judges_row_over_the_gates_does_not_close_the_cloud_to_a_cleared_file(
        corpus, socket, monkeypatch):
    """13 Sep 2026, measured on the owner's corpus: the situation judge's answer
    writes its own row over the gate's clearance row, and a door that read the
    current row's basis sent every cleared file's facts to the local model. The
    door asks the gate pass which files it cleared this run."""
    import test_a_fact_call_cache as here
    from test_site_g_end_to_end import _situation_answer

    monkeypatch.setattr(here, "_decline", _situation_answer)
    _run(corpus, "--enable-cloud")
    assert socket.calls_at(cli.G_SITUATION_SENSITIVITY) == len(CORPUS)
    rows = _rows(corpus, "SELECT basis, protected FROM classifications "
                         "WHERE superseded_by IS NULL")
    assert {row["basis"] for row in rows} == {cli.LOCAL_MODEL_SITUATION}, rows
    assert socket.calls_at(cli.A_FACT) == len(CORPUS), socket.subjects_at(cli.A_FACT)
