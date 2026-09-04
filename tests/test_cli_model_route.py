# tests/test_cli_model_route.py
"""What the command says about the model, and what it does when there is none.

`model_route` is four sentences and one object, and every one of them is a claim
made to a person on a screen. `84` §6: what the screen tells a person to type has
to be true -- and so does what it tells them happened.
"""
from __future__ import annotations

import io

import pytest

import cli
from llm_harness.vocabulary import A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE
from readers.model_deepseek import CREDENTIAL_NAME, PROVIDER
from readers.model_routing import FAST, LOGIC, MODEL_NAME_OF_TIER, REASONING

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
    for name in (CREDENTIAL_NAME, "DEEPSEEK_BASE_URL", *MODEL_NAME_OF_TIER.values()):
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
                     "--database", str(tmp_path / "holder" / "plan.sqlite")],
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
    refuse forever and nothing would say why. So the five are checked here."""
    assert set(cli.TIER_OF_CALL_SITE) == {
        A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE}


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
