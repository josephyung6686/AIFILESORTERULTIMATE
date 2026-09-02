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
    assert routing.model_id_for(A_FACT) == "a-reasoner"


def test_an_exported_value_beats_the_file(monkeypatch, tmp_path):
    """A person who exports a key for one run means it for that run. A file that
    overrode them would send their files to a model they did not choose."""
    routing, _ = _route(
        monkeypatch, {MODEL_NAME_OF_TIER[REASONING]: "the-one-i-typed"},
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
    assert routing.model_id_for(A_FACT) == "a-reasoner"
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


def test_the_site_whose_errors_become_folders_gets_the_reasoning_tier():
    """`83` §3: A_fact "is the one that becomes folder structure, and a person
    finds out months later". If this row ever reads LOGIC or FAST, the tiering has
    been inverted -- the cheap model would be answering the expensive question."""
    assert cli.TIER_OF_CALL_SITE[A_FACT] == REASONING
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

def test_a_configured_route_still_says_it_will_not_be_asked(monkeypatch):
    """THE sentence this whole change exists for. With a key, a route and no
    prompt, `OPERATION_MODE = "offline"` means P7 denies every cloud target -- and
    the file-level message a person then reads ("§8.4 did not clear this file for a
    model call") sounds like a fact about their file. It is a fact about this
    deployment, and the header has to say which."""
    routing, printed = _route(monkeypatch, ENV)
    assert routing is not None
    assert cli.OPERATION_MODE in printed
    assert "None of them will be asked" in printed
    assert "Nothing was sent" in printed


def test_the_mode_sentence_is_the_designs_own_words(monkeypatch):
    """§8.4's four sentences are pinned in `privacy.vocabulary.MODE_SEMANTICS`
    precisely so a paraphrase cannot promise less than the original. The screen
    quotes them rather than restating them."""
    from privacy.vocabulary import MODE_SEMANTICS

    _, printed = _route(monkeypatch, ENV)
    assert MODE_SEMANTICS[cli.OPERATION_MODE].split(";")[0] in printed


def test_the_named_models_are_the_ones_the_route_would_call(monkeypatch):
    """A person told "a model was consulted" has been told less than a person told
    WHICH -- `questions/proposal.py` makes the same argument for the sentence a
    person's own typed self-description gets."""
    _, printed = _route(monkeypatch, ENV)
    for model_id in ("a-reasoner", "a-logician", "a-sprinter"):
        assert model_id in printed


def test_the_key_is_never_printed(monkeypatch):
    """It is read from the environment and put in a closure. Nothing about a
    refusal, an announcement or a model name has any reason to carry it, and a key
    on a terminal is a key in a scrollback buffer and a screenshot."""
    _, printed = _route(monkeypatch, dict(ENV, **{CREDENTIAL_NAME: "sk-secret"}))
    assert "sk-secret" not in printed
    _, refused = _route(monkeypatch, dict(
        ENV, **{CREDENTIAL_NAME: "sk-secret", MODEL_NAME_OF_TIER[FAST]: ""}))
    assert "sk-secret" not in refused
