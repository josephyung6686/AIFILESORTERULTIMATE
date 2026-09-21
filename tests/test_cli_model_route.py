# tests/test_cli_model_route.py
"""What the command says about the model, and what it does when there is none.

`model_route` is four sentences and one object, and every one of them is a claim
made to a person on a screen. `84` §6: what the screen tells a person to type has
to be true -- and so does what it tells them happened.
"""
from __future__ import annotations

import io
import json

import pytest

import cli
from llm_harness.vocabulary import A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE
from readers.model_deepseek import CLOUD, CREDENTIAL_NAME, PROVIDER
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    DISCOVERY_BYTES_CEILING,
    LOCAL,
    discover_local_models,
    MODEL_NAME as LOCAL_MODEL_NAME,
    PROVIDER as LOCAL_PROVIDER,
)
from readers.model_routing import FAST, LOGIC, MODEL_NAME_OF_TIER, REASONING

#: `104` SF-3. A group is a DRAFT until somebody decides it (see `test_cli.py`'s
#: own docstring for the ruling); this file's one end-to-end run has to type the
#: accept, same as a person does, to see the folders it is checking for.
ACCEPTS_THE_PROPOSAL: tuple[str, ...] = ("--accept-groups",)

ENV = {CREDENTIAL_NAME: "a-key", "DEEPSEEK_BASE_URL": "https://api.example",
       MODEL_NAME_OF_TIER[REASONING]: "a-reasoner",
       MODEL_NAME_OF_TIER[LOGIC]: "a-logician",
       MODEL_NAME_OF_TIER[FAST]: "a-sprinter"}


@pytest.fixture(autouse=True)
def _no_ambient_key(monkeypatch, tmp_path):
    """The developer's own `.env` and exported key must not reach these tests.

    Without this the suite passes on the machine that has a key and fails on the
    machine that does not, which is the failure mode `84` §4 records for corpora
    and is the same one here.
    """
    for name in (CREDENTIAL_NAME, "DEEPSEEK_BASE_URL", LOCAL_MODEL_NAME,
                 LOCAL_BASE_URL_NAME, *MODEL_NAME_OF_TIER.values()):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")


def _route(monkeypatch, env=None, file_text=None, tmp_path=None):
    for name, value in (env or {}).items():
        monkeypatch.setenv(name, value)
    if file_text is not None:
        # THIS FILE TESTS THE `.env` READER ITSELF, so it is the one place that
        # opts back into reading one. `tests/conftest.py` sets
        # `GRAPH_AGENT_NO_DOTENV` for the whole suite -- otherwise every test
        # inherits the developer's real credential and a `--enable-cloud` test
        # spends the owner's money on a paid API. A test about the parser must
        # switch that off deliberately, which is exactly the opt-in the
        # conftest note describes, and it points at a file under `tmp_path`
        # rather than the repository's own.
        monkeypatch.delenv("GRAPH_AGENT_NO_DOTENV", raising=False)
        path = tmp_path / ".env"
        path.write_text(file_text, encoding="utf-8")
        monkeypatch.setattr(cli, "ENV_FILE", path)
    out = io.StringIO()
    return cli.model_route(out=out), out.getvalue()


# --- no key is an ordinary state, not an error --------------------------------

def test_no_key_says_so_by_name_and_does_not_raise(monkeypatch):
    routing, printed = _route(monkeypatch)
    assert routing is None
    assert CREDENTIAL_NAME in printed
    assert ".env" in printed


def test_a_misspelled_model_name_is_a_sentence_and_not_a_traceback(monkeypatch):
    """`83` §1 says a wrong model name is meant to be rejected BY THE PROVIDER. A
    name that is simply absent never gets that far, and refusing the whole scan
    over it would take away the part of the run that needs no model at all."""
    routing, printed = _route(monkeypatch, dict(ENV, **{
        MODEL_NAME_OF_TIER[LOGIC]: ""}))
    assert routing is None
    assert MODEL_NAME_OF_TIER[LOGIC] in printed


def test_a_run_with_no_key_still_produces_a_plan(tmp_path, monkeypatch):
    """The whole point of refusing by name rather than refusing. This is the
    end-to-end shape: no key, and the person still gets folders, decisions, and
    the files that needed a model named as such."""
    for name in (CREDENTIAL_NAME, *MODEL_NAME_OF_TIER.values()):
        monkeypatch.delenv(name, raising=False)
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026.\n")
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(tmp_path / "holder" / "plan.sqlite"),
                     *ACCEPTS_THE_PROPOSAL],
                    out=out)
    printed = out.getvalue()
    assert code == 0
    assert CREDENTIAL_NAME in printed
    assert "Folders in this plan" in printed


# --- the environment wins over the file ---------------------------------------

def test_the_file_supplies_what_the_environment_has_not(monkeypatch, tmp_path):
    routing, _ = _route(monkeypatch, {}, "\n".join(
        f"{name}={value}" for name, value in ENV.items()), tmp_path)
    assert routing is not None
    # A_fact resolves through the LOGIC name since the row moved; what is under
    # test here is that the FILE supplied it, not which tier it came from.
    assert routing.model_id_for(A_FACT) == "a-logician"
    assert routing.model_id_for(D_RESIDUAL) == "a-sprinter"


def test_an_exported_value_beats_the_file(monkeypatch, tmp_path):
    """A person who exports a key for one run means it for that run. A file that
    overrode them would send their files to a model they did not choose."""
    routing, _ = _route(
        monkeypatch, {MODEL_NAME_OF_TIER[LOGIC]: "the-one-i-typed"},
        "\n".join(f"{name}={value}" for name, value in ENV.items()), tmp_path)
    assert routing.model_id_for(A_FACT) == "the-one-i-typed"


def test_quotes_and_spacing_are_read_the_way_env_files_are(monkeypatch, tmp_path):
    """A person editing `.env` writes it the way every `.env` is written. A value
    that arrived as `\'a-reasoner\'` would be sent to the provider with the quotes
    on it and rejected as an unknown model -- `83` §1's intended failure, fired by
    our own parser rather than by anything the person got wrong."""
    routing, _ = _route(monkeypatch, {}, (
        "# a comment\n"
        "\n"
        f'{CREDENTIAL_NAME}="a-key"\n'
        f"DEEPSEEK_BASE_URL = https://api.example \n"
        f"{MODEL_NAME_OF_TIER[REASONING]}='a-reasoner'\n"
        f"{MODEL_NAME_OF_TIER[LOGIC]}=a-logician\n"
        f"{MODEL_NAME_OF_TIER[FAST]}=a-sprinter\n"), tmp_path)
    assert routing is not None
    # The quoted value is the REASONING one, and it is read back unquoted through
    # the tier that still carries it rather than through A_fact, whose row moved.
    assert routing.client_of_tier[REASONING].model_target.model_id == "a-reasoner"
    assert routing.model_id_for(C_PLACEMENT) == "a-logician"


def test_a_commented_out_line_is_not_a_setting(tmp_path):
    """`.env.example` is mostly comments, and commenting a name out is how a person
    turns one off. Asserted against `_dotenv` rather than through `model_route`,
    because through `model_route` it CANNOT FAIL: a `#` left on the name makes a key
    nothing looks up, so the bug hides behind a second accident. Guarding the parser
    where the rule lives is the difference between a guard and a decoration.
    """
    path = tmp_path / ".env"
    path.write_text(
        "# a comment\n"
        f"# {MODEL_NAME_OF_TIER[REASONING]}=the-one-i-commented-out\n"
        "\n"
        f"{MODEL_NAME_OF_TIER[REASONING]}=a-reasoner\n", encoding="utf-8")
    read = cli._dotenv(path)
    assert read == {MODEL_NAME_OF_TIER[REASONING]: "a-reasoner"}


def test_a_missing_env_file_is_not_an_error(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / "nothing-here")
    assert cli.model_route(out=io.StringIO()) is None


# --- `83` §3's table, checked against the sites that exist --------------------

def test_every_call_site_p8_publishes_is_routed_to_a_tier():
    """`83` §3's last row refuses an unrouted site, which is the right behaviour
    and a bad surprise: a site P8 already publishes and this table forgot would
    refuse forever and nothing would say why. So the SEVEN are checked here: the
    five of `83` §3, site G since `104` §17.1 (9 Sep 2026), and site H since `00`
    amendment 7(c) (12 Sep 2026), which asks the restricted-kind question on this
    device before site G and before any other site is asked.

    `F_role_shortlist` is deliberately absent and always has been: it is a
    `CALL_SITES` member with no prompt installed and nothing routes it."""
    from llm_harness.vocabulary import (
        G_SITUATION_SENSITIVITY, H_RESTRICTED_KIND,
    )

    assert set(cli.TIER_OF_CALL_SITE) == {
        A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE,
        G_SITUATION_SENSITIVITY, H_RESTRICTED_KIND}


def test_the_site_whose_errors_become_folders_gets_the_checkable_tier():
    """`83` §3 gave A_fact the REASONING tier, and MEASUREMENT ON REAL FILES TOOK IT
    AWAY. This is the record of that, kept beside the row it changed.

    The old rule read `A_FACT: REASONING` and this test defended it in these words:
    "if this row ever reads LOGIC or FAST, the tiering has been inverted -- the cheap
    model would be answering the expensive question". The premise was that the
    expensive model answers the question better. It does not answer it at all.

    Four real dossiers, built by this product from four of the owner's own files and
    replayed against both tiers:

      * `deepseek-v4-pro`, the REASONING tier: 0 of 4 produced any answer.
        `finish_reason == "length"`, `completion_tokens == 8192`, `content` empty --
        the whole ceiling went to reasoning and the model never began writing. ~110
        seconds each, and two of the four never returned at all: the provider closes
        an idle connection at sixty seconds.
      * `deepseek-chat`, non-reasoning: 4 of 4 answered, in 1.8 to 4.7 seconds. Each
        claim carried a citation into released evidence -- `subject = "PHYS 1401"`
        cited to the document's own title, `authored_by = "Eric Raymer"` cited to the
        PDF `Author` field -- and every field without evidence came back as an
        `insufficiency_statement` rather than a guess.

    THE DECLINE §3.6 ASKS FOR IS WHAT THE CHEAPER MODEL ACTUALLY DID. `83` §3 chose
    the reasoning tier because "the model most able to decline is the one worth
    paying for", and the model that declined honestly, field by field, is the one
    that costs less.

    **The cause is in the ratified template and cannot be fixed there.** `82`'s text
    says "Think for as long as you need to before you answer". A reasoning model whose
    budget is shared between thinking and answering takes that literally and spends
    all of it. A non-reasoning model reads the same sentence harmlessly. The template
    is the owner's and an agent may not edit it, so the tier is the end that moves.

    LOGIC rather than FAST, because `83`'s own words for LOGIC are "bounded,
    checkable, verification-shaped" and that is exactly what A_fact is: every claim
    is re-checked against evidence already extracted, and an uncited claim is
    refused. FAST is described as "low stakes, individually cheap to get wrong",
    which A_fact is not.

    Latency settles it even where accuracy might not. The owner's standing target is
    ten thousand files in under thirty minutes. At ~110 seconds a file the reasoning
    tier misses it by two orders of magnitude before a single answer is judged.
    """
    assert cli.TIER_OF_CALL_SITE[A_FACT] == LOGIC
    assert cli.TIER_OF_CALL_SITE[D_RESIDUAL] == FAST
    for checkable in (B_GROUP, C_PLACEMENT, E_TEMPLATE):
        assert cli.TIER_OF_CALL_SITE[checkable] == LOGIC


def test_the_route_carries_the_provider_and_the_locality_the_transport_accepts(
        monkeypatch, tmp_path):
    routing, _ = _route(monkeypatch, ENV)
    for site in cli.TIER_OF_CALL_SITE:
        target = routing.client_for(site).model_target
        assert target.provider == PROVIDER
        assert target.locality == "cloud"


# --- the sentence about the mode ----------------------------------------------
#
# MOVED to `tests/test_cli_cloud_consent.py`. `model_route` no longer announces:
# whether these models will be ASKED is a question about this folder's consent,
# which this function does not read. Three tests moved with the sentence rather
# than being deleted, because each of them is still a promise made to a person --
# they are simply now made by the function that knows both halves.

def test_the_key_is_never_printed(monkeypatch):
    """It is read from the environment and put in a closure. Nothing about a
    refusal, an announcement or a model name has any reason to carry it, and a key
    on a terminal is a key in a scrollback buffer and a screenshot."""
    _, printed = _route(monkeypatch, dict(ENV, **{CREDENTIAL_NAME: "sk-secret"}))
    assert "sk-secret" not in printed
    _, refused = _route(monkeypatch, dict(
        ENV, **{CREDENTIAL_NAME: "sk-secret", MODEL_NAME_OF_TIER[FAST]: ""}))
    assert "sk-secret" not in refused


def _two_files(conn, tmp_path) -> tuple[str, str]:
    """One file the product read and the detector abstained on, one protected.

    Shared by the two tests below because they assert about the SAME pair from two
    directions -- what the route does with each, and what it does with each per
    locality -- and two corpora would let one drift into testing a different file.
    """
    from database_agent.files_table import get_file, record_file
    from privacy.classification import ClassificationRecord
    from privacy.vocabulary import DETECTOR
    from privacy.classification_store import ClassificationStore
    from privacy.schema import create_privacy_schema

    create_privacy_schema(conn)

    def _file(name: str, body: bytes) -> tuple[str, str]:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        file_id = record_file(
            conn, path, filename=name, normalized_filename=name.lower(),
            extension=".pdf", observed_size=len(body),
            observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
            parent_folder_context="Downloads", mime_type="application/pdf",
            detected_format="pdf", scan_state="included", materialized=True)
        return file_id, get_file(conn, file_id)["content_hash"]

    read_but_unclassified, _ = _file("Lecture 08.pdf", b"Work and energy, lecture 8")
    protected, protected_hash = _file("HKID scan.pdf", b"identity document")
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=protected, content_hash=protected_hash,
        handling_class="sensitive_personal", protected=True, basis=DETECTOR,
        evidence_refs=("sha256:" + "b" * 64,), reliability_state="validated",
        observed_at="2026-09-05T00:00:00Z"))
    return read_but_unclassified, protected


def test_a_file_that_was_read_reaches_the_model_even_with_no_classification(
        conn, tmp_path):
    """CONSTITUTION 2: a detector abstaining is not proof a file is unreadable.

    **Measured, 199 real files, 2026-09-05.** 95 of them carried no classification
    and were refused the model with `privacy_withheld` -- and every one of the 95 had
    evidence: ordinary lecture PDFs, `.py` files, a club logo. The written premise
    for refusing them, in `model_route_permitted`'s own docstring, was "an
    unclassified file is one nothing has read successfully". The run disproves it.
    Unclassified means the DETECTOR abstained, which is a different sentence.

    Protected files are unaffected and the standing rule is why: marked and counted,
    never opened. That half is asserted here beside this one so the widening cannot
    quietly take it with it.
    """
    read_but_unclassified, protected = _two_files(conn, tmp_path)

    on_device = cli.model_route_permitted(
        conn, locality=LOCAL,
        unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
        operation_mode=cli.OPERATION_MODE)

    assert on_device(read_but_unclassified) is True, (
        "a file the product read and the detector merely abstained on is not "
        "'unreadable'; refusing it keeps 95 of 199 files away from the engine")
    # `104` §18.7 (9 Sep 2026): protected material reaches the LOCAL model only.
    assert on_device(protected) is True, "protected material reaches the local model"


def test_the_route_refuses_on_a_cloud_target_what_the_gate_would_have_refused(
        conn, tmp_path):
    """`104` R-02. The route answered `True` for an unclassified file whatever the
    destination, and `Gate.release` then refused every cloud release of one -- so
    the file was counted as routed, the refusal landed in `llm_refusal` instead of
    `unresolved`, and a number meaning "the route let N through" was read as "N
    reached a model". Measured at 19 withheld against 149 stopped.

    ONE ANSWER, NOT TWO THAT AGREE. `unclassified_denies` is the gate's own
    predicate, called here with the same locality and the same answer to Open
    question 5, which `UNCLASSIFIED_PERMITS_LOCAL` now names for both. A second
    spelling beside the first is how they came to disagree."""
    read_but_unclassified, protected = _two_files(conn, tmp_path)

    on_device = cli.model_route_permitted(
        conn, locality=LOCAL,
        unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
        operation_mode=cli.OPERATION_MODE)
    over_the_internet = cli.model_route_permitted(
        conn, locality=CLOUD,
        unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
        operation_mode=cli.CLOUD_ENABLED_MODE)

    assert on_device(read_but_unclassified) is True
    assert over_the_internet(read_but_unclassified) is False, (
        "the gate refuses every cloud release of an unclassified file, so a route "
        "that permits one is counting a file as routed that has no route")
    # AND ON PROTECTED MATERIAL THE ROUTE ASKS THE GATE'S OWN RULE (`104` §18.7,
    # 9 Sep 2026): `protected_cloud_denies` allows a protected file a LOCAL
    # target and refuses it a cloud one, and the route now says the same.
    # SABOTAGE: restore `return not record.protected` and the first line goes red.
    assert on_device(protected) is True
    assert over_the_internet(protected) is False


# --- `00`:189-193's second mode: a model on the person's own machine ----------
#
# D1's local half. `104` §7 Phase 0a. No ollama runs in any of these: `model_route`
# BUILDS clients, and every refusal it can make fires at build time, before a
# socket exists.

LOCAL_ENV = {LOCAL_MODEL_NAME: "qwen3:8b"}


def test_a_local_model_alone_is_a_model_and_the_run_has_one(monkeypatch):
    """The whole of Phase 0a in one assertion: a person who typed
    `ollama pull qwen3:8b` and set one name has a model, with no account, no key
    and nothing leaving their machine."""
    routing, printed = _route(monkeypatch, LOCAL_ENV)

    assert routing is not None
    assert routing.model_id_for(A_FACT) == "qwen3:8b"
    target = routing.client_for(A_FACT).model_target
    assert target.locality == LOCAL
    assert target.provider == LOCAL_PROVIDER
    # Nothing about a missing key: they are not missing anything.
    assert CREDENTIAL_NAME not in printed


def test_a_key_and_a_local_model_together_hold_both_at_every_site(monkeypatch):
    """`104` §17.13 ruling 3, at the composition root.

    **This replaces D1's per-SITE split and the assertion that pinned it.** That
    one read `routing.model_id_for(A_FACT) == "qwen3:8b"`: beside a cloud key the
    local model took site A's whole tier and the cloud kept the rest, so a run
    either asked a provider every fact question or none of them -- and none was the
    answer, which left every classified file answered by an 8b model on this
    machine while half the corpus was refused outright.

    The ruling is per FILE, and a site that is two destinations cannot be one
    client. So both are held, `client_for` still describes the cloud half for the
    screen and the observe gates, and `route_for` is where the second one lives.
    WHICH files go where is `cli.target_for`'s and is tested there; this is only
    that the root builds a routing that can answer both ways.
    """
    routing, _ = _route(monkeypatch, dict(ENV, **LOCAL_ENV))

    cloud_client, cloud_target = routing.route_for(A_FACT, cloud_permitted=True)
    local_client, local_target = routing.route_for(A_FACT, cloud_permitted=False)

    assert cloud_target.locality == "cloud"
    assert cloud_target.model_id == "a-logician"
    assert local_target.locality == LOCAL
    assert local_target.model_id == "qwen3:8b"
    assert cloud_client is not local_client
    # FAST is untouched and still describes the model the key paid for.
    assert routing.model_id_for(D_RESIDUAL) == "a-sprinter"
    assert routing.client_for(D_RESIDUAL).model_target.locality == "cloud"


def test_a_local_model_alone_is_unchanged_by_the_per_file_route(monkeypatch):
    """The deployment the ruling does not touch, pinned beside the one it does: one
    installed model is the destination for every site and both ways of asking."""
    routing, _ = _route(monkeypatch, LOCAL_ENV)

    for permitted in (True, False):
        client, target = routing.route_for(A_FACT, cloud_permitted=permitted)
        assert target.locality == LOCAL
        assert target.model_id == "qwen3:8b"
        assert client is routing.client_for(A_FACT)


def test_with_neither_name_the_sentence_offers_both_ways_to_have_a_model(monkeypatch):
    """The old sentence named only the key, which told a person the product needs
    a paid account to think at all. One of the two ways costs nothing and sends
    nothing, and a person who is not told about it cannot choose it."""
    routing, printed = _route(monkeypatch)

    assert routing is None
    assert CREDENTIAL_NAME in printed
    assert LOCAL_MODEL_NAME in printed
    assert "ollama pull" in printed


def test_a_broken_local_setup_does_not_quietly_send_the_files_to_the_cloud(
        monkeypatch):
    """THE ONE DIRECTION THAT COSTS MONEY AND LEAVES THE DEVICE. A person who set
    `GRAPH_AGENT_LOCAL_MODEL` asked for the model on their own machine. Falling
    back to the provider because their endpoint is wrong would be the surprise
    `_dotenv` refuses in its own docstring, arrived at from the other side.

    So there is NO model for this run, and the sentence says which one failed."""
    routing, printed = _route(monkeypatch, dict(
        ENV, **{LOCAL_MODEL_NAME: "qwen3:8b",
                LOCAL_BASE_URL_NAME: "http://ollama.example.com:11434"}))

    assert routing is None
    assert "loopback" in printed


def test_an_endpoint_on_another_loopback_port_is_ordinary(monkeypatch):
    """Which is what a person running ollama on a second port needs, and what
    makes a stub server testable at all."""
    routing, _ = _route(monkeypatch, dict(
        LOCAL_ENV, **{LOCAL_BASE_URL_NAME: "http://127.0.0.1:54321"}))

    assert routing is not None


def test_a_broken_cloud_key_beside_a_working_local_model_still_leaves_a_model(
        monkeypatch):
    """The two halves are independent. A misspelled tier name is `83` §1's
    intended failure and it takes the cloud route with it; it does not take the
    model the person installed on their own machine."""
    routing, printed = _route(monkeypatch, dict(
        ENV, **LOCAL_ENV, **{MODEL_NAME_OF_TIER[FAST]: ""}))

    assert routing is not None
    assert routing.client_for(A_FACT).model_target.locality == LOCAL
    assert MODEL_NAME_OF_TIER[FAST] in printed


def test_the_local_model_is_read_from_the_env_file_like_every_other_name(
        monkeypatch, tmp_path):
    """It is documented in `.env.example` beside the key, so it has to be readable
    from where `.env.example` says to put it."""
    routing, _ = _route(monkeypatch, {},
                        f"{LOCAL_MODEL_NAME}=qwen3:8b\n", tmp_path)

    assert routing is not None
    assert routing.model_id_for(A_FACT) == "qwen3:8b"


# --- what the person is told before the scan ---------------------------------

def _posture(routing, tmp_path):
    out = io.StringIO()
    cli.announce_cloud_posture(routing, None, corpus_root=tmp_path, out=out)
    return out.getvalue()


def test_the_posture_names_the_local_model_and_says_nothing_leaves(
        monkeypatch, tmp_path):
    """The owner's condition on the guard change: a local call under `offline`
    must still be truthful. Every other sentence in this branch says nothing will
    be asked, and with a model on this machine something IS asked -- so a person
    reading "cloud sending is off" would otherwise conclude nothing was.

    Both halves have to be there. The MODEL, because "a person told that their
    sentence is going to 'an external provider' has been told less than a person
    told it is going to a named one", and that is no less true of a named local
    one. And that NOTHING LEAVES, because that is the difference that makes the
    first half acceptable."""
    routing, _ = _route(monkeypatch, LOCAL_ENV)

    printed = _posture(routing, tmp_path)

    assert "qwen3:8b" in printed
    assert "on this device" in printed
    assert "NOTHING LEAVES YOUR DEVICE" in printed
    # And it does NOT tell them nothing will be asked, which is the sentence the
    # cloud-only branch prints and which would now be false.
    assert "None of them will be asked on this run" not in printed


def test_the_posture_still_names_a_cloud_model_that_is_configured_beside_it(
        monkeypatch, tmp_path):
    """A person deciding about `--enable-cloud` tomorrow needs to know a cloud
    model is configured today, even while the fact question never reaches it."""
    routing, _ = _route(monkeypatch, dict(ENV, **LOCAL_ENV))

    printed = _posture(routing, tmp_path)

    assert "qwen3:8b" in printed
    assert "a-sprinter" in printed
    assert "--enable-cloud" in printed


def test_the_cloud_only_posture_is_word_for_word_what_it_was(monkeypatch, tmp_path):
    """THE UNCHANGED HALF, pinned. The local route widened this function and must
    not have moved it: with no local model the sentence a person sees is the one
    they saw before."""
    routing, _ = _route(monkeypatch, ENV)

    printed = _posture(routing, tmp_path)

    assert "Model: a-logician for facts, a-logician for checks, a-sprinter for" \
        in printed
    assert "None of them will be asked on this run" in printed
    assert "NOTHING LEAVES YOUR DEVICE" not in printed


def test_with_sending_on_the_facts_are_still_said_to_stay_on_the_device(
        monkeypatch, tmp_path):
    """The consent-ON branch, which the end-to-end tests cannot reach: driving
    `cli.main --enable-cloud` is exactly what must not happen in a suite. Called
    directly instead, because this is a sentence and not a send -- no client is
    invoked and no socket is opened by printing it.

    Without the clause, a person who turned cloud sending on would read "files ...
    may be sent to qwen3:8b" and be told a model on their own hard disk is a
    recipient of their files. Consent is about what LEAVES; the fact question no
    longer does."""
    from database_agent.cloud_consent import CloudConsent

    routing, _ = _route(monkeypatch, LOCAL_ENV)
    consent = CloudConsent(corpus_root=str(tmp_path), decision="enabled",
                           user_id="jy", decided_at="2026-09-05T00:00:00Z")
    out = io.StringIO()
    cli.announce_cloud_posture(routing, consent, corpus_root=tmp_path, out=out)
    printed = out.getvalue()

    assert "on this device and do not leave it" in printed
    assert "qwen3:8b" in printed


# --------------------------------------------------------------------------
# `104` R-121: open question 5 has ONE answer, in ONE place
# --------------------------------------------------------------------------

def _src_root():
    import pathlib

    import privacy
    return pathlib.Path(privacy.__file__).parent.parent


def _binding_sites(name: str) -> list[str]:
    """Every module under `src/` that ASSIGNS this name at module level.

    AST, not `read_text()`, and `tests/p3/test_p3_no_invention.py` records why: a
    comment or a docstring explaining why a value is absent matches a text scan for
    that value, and this fix leaves several such comments behind on purpose. An
    `ImportFrom` is not a binding site -- importing the one answer is the fix.
    """
    import ast

    found: list[str] = []
    for path in sorted(_src_root().rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in tree.body:
            targets = []
            if isinstance(node, ast.Assign):
                targets = [t for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                targets = [node.target]
            if any(target.id == name for target in targets):
                found.append(str(path.relative_to(_src_root())))
    return found


def test_r121_open_question_5_is_answered_in_exactly_one_place():
    """`104` R-121. The tree answered it twice and the two answers disagreed.

    `cli.UNCLASSIFIED_PERMITS_LOCAL` said `True`, documented as read by both the
    gate and the route "so they cannot answer differently";
    `placement.privacy.LOCAL_CALLS_ON_UNCLASSIFIED` said `False`, so P11 refused a
    dossier to all 86 unclassified files of the owner's local run before
    `Gate.release` was ever asked. `104` §15.3 rules one answer under one name.

    A grep for a second pin, which is this repo's own technique for "there is
    exactly one of these", made over the AST so the comments the fix leaves behind
    do not satisfy it.
    """
    assert _binding_sites("UNCLASSIFIED_PERMITS_LOCAL") == ["privacy/denial.py"]
    # The retired second spelling is gone everywhere, not merely repointed.
    assert _binding_sites("LOCAL_CALLS_ON_UNCLASSIFIED") == []


def test_r121_the_three_readers_all_reach_that_one_definition():
    """Every reader resolves the name, and none of them holds a spelling of its own.

    THIS TEST CANNOT PROVE THERE IS ONE DEFINITION and does not claim to. The
    answer is a bool and `True` is a singleton, so two modules each pinning their
    own `True` would satisfy `is` here exactly as they satisfy `==`. What proves
    the single definition is `test_r121_open_question_5_is_answered_in_exactly_one
    _place` above, which walks the AST for a second binding site. This one proves
    the complementary half: each reader reaches the name at all, and the gate takes
    it as a keyword with no default rather than deciding it for itself.
    """
    import placement.privacy as p11_privacy
    from privacy.denial import UNCLASSIFIED_PERMITS_LOCAL as the_answer

    assert cli.UNCLASSIFIED_PERMITS_LOCAL is the_answer
    assert p11_privacy.UNCLASSIFIED_PERMITS_LOCAL is the_answer
    # THE GATE IS THE THIRD READER, and it reads through its keyword rather than
    # through an import: `unclassified_permits_local` has no default anywhere, so
    # nothing clears §8.4 by omission. What R-121 requires is that the value the
    # gate is handed comes from the one definition, which is what `cli.py`'s two
    # call sites do -- asserted by the two route tests above and by the gate's own
    # `tests/p7/test_p7_release.py`.
    import inspect

    from privacy.denial import unclassified_denies
    from privacy.gate import Gate

    assert "unclassified_permits_local" in inspect.signature(Gate.__init__).parameters
    assert inspect.signature(Gate.__init__).parameters[
        "unclassified_permits_local"].default is inspect.Parameter.empty
    assert inspect.signature(unclassified_denies).parameters[
        "local_calls_on_unclassified"].default is inspect.Parameter.empty


def test_r121_the_answer_is_that_a_local_model_may_be_asked_and_a_cloud_one_may_not():
    """The ruling itself (`104` §15.3), asserted through P7's own predicate.

    "An unclassified file MAY reach a LOCAL model and never a cloud one" -- the
    design's "only local rules and local models may run" under the local-only
    modes, and a local model sees nothing that leaves the device.
    """
    from privacy.denial import UNCLASSIFIED_PERMITS_LOCAL, unclassified_denies

    assert UNCLASSIFIED_PERMITS_LOCAL is True
    assert unclassified_denies(
        locality=LOCAL, local_calls_on_unclassified=UNCLASSIFIED_PERMITS_LOCAL) is False
    assert unclassified_denies(
        locality=CLOUD, local_calls_on_unclassified=UNCLASSIFIED_PERMITS_LOCAL) is True


def test_only_the_gates_word_or_the_persons_opens_the_cloud():
    """13 Sep 2026: the local situation judge lifted two key-protected holds on the
    second corpus; its word is recorded and asked under, and opens no door."""
    assert cli.CLOUD_CLEARING_BASES == (cli.LOCAL_MODEL_GATE, "user")
    assert cli.LOCAL_MODEL_SITUATION not in cli.CLOUD_CLEARING_BASES


# --- asking the device what it has, instead of assuming it has nothing --------
#
# THE DEFECT, MEASURED ON THE OWNER'S MACHINE, 20 Sep 2026. `ollama` was running
# with three models pulled, and the screen said "there is no model on this device
# to fall back to". The sentence was false, and the reason it was false is that
# nothing ever looked: `model_route` read `GRAPH_AGENT_LOCAL_MODEL` and, finding
# it unset, concluded the device had nothing. A person with a working model was
# told they had none because they did not know an environment variable's name.
#
# `84` §6 -- what the screen tells a person has to be true -- is the whole of it.
# The fix is to ASK, and the fix is not to CHOOSE: which of a person's models
# reads their files is their decision, so a discovered model is named on the
# screen and is not used. `test_a_discovered_model_is_named_on_the_screen_and_is
# _not_used` is that ruling, asserted.
#
# `discover_local_models` IS THE REAL FUNCTION, reached WHERE IT LIVES rather than
# through `cli._discover_local_models`, the alias `tests/conftest.py` replaces for
# the whole suite -- the same argument `_no_ambient_key` makes above, applied to a
# model server instead of a key: a suite whose screens depend on whether the
# developer happens to be running ollama passes on one machine and fails on the
# next. The tests below that end in `_for_real` hold the original function and talk
# to a real endpoint; every other test here injects an answer.
#: The provider's own attribute, which the suite-wide neutralisation does not
#: touch: it replaces `cli`'s name for the function, never the function.
_REAL_DISCOVERY = discover_local_models


def _found(*names: str):
    """A discovery that answers without a server, and records that it was asked."""
    calls: list[str] = []

    def discover(base_url: str) -> tuple[str, ...]:
        calls.append(base_url)
        return names

    discover.calls = calls  # type: ignore[attr-defined]
    return discover


def _route_with(monkeypatch, discover, env=None):
    for name, value in (env or {}).items():
        monkeypatch.setenv(name, value)
    out = io.StringIO()
    return cli.model_route(out=out, discover=discover), out.getvalue()


def test_with_no_name_set_the_device_is_asked_what_it_has(monkeypatch):
    """The whole defect in one assertion: nothing ever looked, and now it does."""
    discover = _found("qwen3:8b", "qwen2.5:3b")
    _route_with(monkeypatch, discover)

    assert discover.calls, (
        "no name was set, so the one thing that could have found a model on this "
        "device is asking the device -- and it was not asked")


def test_a_discovered_model_is_named_on_the_screen_and_is_not_used(monkeypatch):
    """NAMED, NOT CHOSEN. The conservative half of the ruling: the run still does
    not use a model it was not told to use, because which of a person's models
    reads their files is theirs to decide. What changes is that the screen stops
    telling them there is nothing there."""
    routing, printed = _route_with(monkeypatch, _found("qwen3:8b", "qwen2.5:3b"))

    assert routing is None, "a discovered model is named, never silently used"
    assert "qwen3:8b" in printed and "qwen2.5:3b" in printed
    assert LOCAL_MODEL_NAME in printed
    # The false half of the old sentence, gone: a device with two models is not
    # told to go and install one.
    assert "ollama pull" not in printed


def test_a_key_with_sending_off_still_hears_about_the_models_on_the_device(
        monkeypatch):
    """THE OWNER'S OWN RUN. A key is configured, this folder's sending is not on,
    and three models sit idle on the device -- the run where the false sentence
    was read. `model_route` returned the cloud route here and said nothing at all
    about local, so the only sentence the person got was the false one."""
    routing, printed = _route_with(monkeypatch, _found("qwen3:4b"), dict(ENV))

    assert routing is not None
    assert "qwen3:4b" in printed
    assert LOCAL_MODEL_NAME in printed


def test_a_named_model_is_never_second_guessed_by_a_probe(monkeypatch):
    """It must not slow an ordinary run: one request at most, and only when no
    model was named. A deployment that named its model has already answered the
    question the probe asks."""
    discover = _found("qwen3:8b")
    routing, _ = _route_with(monkeypatch, discover, dict(LOCAL_ENV))

    assert routing is not None
    assert not discover.calls, (
        "a model was named, so there was nothing to discover and no reason to "
        "spend a request finding out")


def test_finding_nothing_leaves_the_old_sentence_exactly_as_it_was(monkeypatch):
    """The refusal when there is GENUINELY no model stays exactly as true as it
    was. A person with no model installed is told what to install, in the words
    they were told before."""
    _, unchanged = _route_with(monkeypatch, _found())

    assert unchanged == (
        "No model was consulted: neither DEEPSEEK_API_KEY nor "
        "GRAPH_AGENT_LOCAL_MODEL\nis set, so this run used only what it could "
        "read and decide on this device.\nFiles that needed a judgement are "
        "named below and say so. To enable one,\neither install a local model "
        "(`ollama pull qwen3:8b`) and set\nGRAPH_AGENT_LOCAL_MODEL to its id, "
        "which sends nothing anywhere, or copy\n`.env.example` to `.env` and "
        "put a key in it.\n")


def test_the_coverage_line_no_longer_claims_to_know_what_is_on_the_device():
    """The sentence the owner read. It said "there is no model on this device to
    fall back to" -- a claim about the DEVICE, made by code that had only ever
    looked at an environment variable. What was actually checked is whether a
    model was NAMED, and that is what it may say. The cloud half is untouched:
    sending still needs this folder's consent."""
    sentence = cli.COVERAGE_SENTENCE[cli.NOT_RUN_NO_DESTINATION]

    assert "there is no model on this device to fall back to" not in sentence
    # What WAS checked, and all that may be claimed from it.
    assert "named" in sentence
    # The cloud half, unchanged: sending still needs this folder's consent.
    assert "this folder's sending turned on" in sentence


def test_a_discovery_that_cannot_reach_anything_is_not_a_failed_run_for_real():
    """A file organiser that cannot run because a model server is absent is worse
    than one that says so. REAL: a port nothing is listening on, no injection."""
    assert _REAL_DISCOVERY("http://127.0.0.1:1") == ()


def test_discovery_talks_to_loopback_or_it_does_not_happen_for_real():
    """`model_ollama.LOOPBACK_HOSTS` is the line between a local claim and a cloud
    call wearing a local target, and it holds for the PROBE as much as for the
    call. REAL: no connection is attempted at all."""
    assert _REAL_DISCOVERY("http://example.com:11434") == ()
    assert _REAL_DISCOVERY("https://api.deepseek.com") == ()
    assert _REAL_DISCOVERY("") == ()


def test_what_is_actually_installed_on_this_machine_for_real():
    """REAL, and skipped where there is no server: the half of this proof that no
    injection can give. The names are whatever this machine has -- nothing here
    knows or asserts which, because `qwen3:8b` is what one laptop happens to hold
    and the next holds something else."""
    found = _REAL_DISCOVERY(cli.LOCAL_DEFAULT_BASE_URL)
    if not found:
        pytest.skip("no local model server is listening; the injected half stands")
    assert all(isinstance(name, str) and name for name in found)


def _a_server_on_loopback(handle):
    """A real HTTP server on a real loopback port, for the two things no
    injection can prove: that a redirect is not followed, and that a listing is
    read off the wire. Torn down by the caller."""
    import http.server
    import threading

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            handle(self)

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}"


def test_a_redirect_is_declined_rather_than_followed_for_real():
    """A REDIRECT IS A CLOUD CALL WEARING A LOCAL TARGET, and this is what makes
    the host check mean anything. The named endpoint really is loopback, so the
    check passes -- and then the server answers `302` somewhere else. `urlopen`
    follows redirects by default, so without the guard the probe would make a
    request to a host nothing had checked, as the one call nobody thinks of as a
    send.

    **BOTH SERVERS ARE ON LOOPBACK, and that is what makes this decisive rather
    than decorative.** A test that redirected to a real outside host would pass
    with the guard REMOVED -- `example.com` answers with HTML, the parse fails,
    and the empty tuple comes back for the wrong reason. Here the redirect target
    is a second local server serving a perfectly good listing: follow it and the
    names come back, decline it and they cannot. The assertion is that the second
    server was never asked at all.
    """
    followed: list[str] = []

    def a_real_listing(request):
        followed.append(request.path)
        body = json.dumps({"models": [{"name": "followed:1b"}]}).encode()
        request.send_response(200)
        request.send_header("Content-Length", str(len(body)))
        request.end_headers()
        request.wfile.write(body)

    target, target_endpoint = _a_server_on_loopback(a_real_listing)
    asked: list[str] = []

    def redirect_there(request):
        asked.append(request.path)
        request.send_response(302)
        request.send_header("Location", target_endpoint + "/api/tags")
        request.end_headers()

    server, endpoint = _a_server_on_loopback(redirect_there)
    try:
        assert _REAL_DISCOVERY(endpoint) == ()
    finally:
        for stopping in (server, target):
            stopping.shutdown()
            stopping.server_close()
    assert asked, "the named endpoint was never asked, so nothing was proven"
    assert not followed, (
        "the redirect was followed: a request reached a host the loopback check "
        "never saw, which is the whole thing that check exists to prevent")


def test_a_listing_is_read_off_the_wire_and_a_broken_one_is_not_a_failure_for_real():
    """REAL, and on a port this test owns rather than on whatever this laptop
    happens to be running. The four bodies are the four ways a real endpoint
    answers: a listing, a listing of the wrong shape, something that is not JSON
    at all, and a body far past the ceiling. None of them may raise."""
    body: list[bytes] = [b""]

    def answer(request):
        request.send_response(200)
        request.send_header("Content-Length", str(len(body[0])))
        request.end_headers()
        request.wfile.write(body[0])

    server, endpoint = _a_server_on_loopback(answer)
    try:
        body[0] = json.dumps({"models": [
            {"name": "second:1b"}, {"name": "first:2b"}, {"name": "second:1b"},
            {"name": "   "}, {"nothing": "useful"}, "not even an object"]}).encode()
        # Sorted and de-duplicated, and the entries with no usable name dropped.
        assert _REAL_DISCOVERY(endpoint) == ("first:2b", "second:1b")

        body[0] = json.dumps({"models": "not a list"}).encode()
        assert _REAL_DISCOVERY(endpoint) == ()

        body[0] = b"<html>a proxy said hello</html>"
        assert _REAL_DISCOVERY(endpoint) == ()

        # VALID JSON, and that is what makes the assertion decisive. A body with
        # a trailing comma would fail to parse whether the ceiling existed or
        # not, and the empty tuple would come back for the wrong reason -- the
        # same trap the redirect test above had to be rewritten to escape. This
        # parses cleanly to one name if it is read whole, so an empty tuple can
        # only mean the read stopped at the ceiling.
        body[0] = (b'{"models": ['
                   + b'{"name": "x"},' * 200_000
                   + b'{"name": "x"}]}')
        assert json.loads(body[0])["models"][0] == {"name": "x"}
        assert len(body[0]) > DISCOVERY_BYTES_CEILING
        assert _REAL_DISCOVERY(endpoint) == ()
    finally:
        server.shutdown()
        server.server_close()
