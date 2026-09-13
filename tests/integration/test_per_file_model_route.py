# tests/integration/test_per_file_model_route.py
"""`104` §17.13 ruling 3: the model target is chosen per FILE, not per site.

The owner's words, 9 September 2026: *"a protected file, and an unclassified file
until site G classifies it, goes to the local model; everything else goes to the
cloud."* Before this the local model took one call site's whole tier
(`ollama_routing(serves=A_FACT)`), so a deployment with both models asked a
provider every fact question or none of them -- and none was the answer, which
left every classified file answered on this machine while the cloud gate refused
half the corpus for being unclassified.

**The corpus here is three files and each one is a different answer.** One
classified and not protected, one the detector abstained on, one protected. They
are synthetic and tiny on purpose: what is under test is which destination each
one is given, which is a question about classification records and a routing, and
a real corpus would add nothing to it but minutes.

**What is NOT under test here.** Whether a model answers well, and what the gate
then releases into the dossier. Those have their own suites. What this pins is the
seam between them: the pair `cli.target_for` hands back is the pair
`FactCallAuthorities.route` returns, is the target `fact_call_stage` reads a
locality off, and is the `model_id` the call identity records.
"""
from __future__ import annotations

import json

import pytest

import cli
from llm_harness.transport import ModelClient
from llm_harness.vocabulary import (
    A_FACT, C_PLACEMENT, D_RESIDUAL, G_SITUATION_SENSITIVITY)
from privacy.release import ModelTarget
from readers.model_deepseek import CLOUD, PROVIDER
from readers.model_ollama import LOCAL, PROVIDER as LOCAL_PROVIDER
from readers.model_routing import FAST, LOGIC, REASONING, TierRouting

CLOUD_IDS = {REASONING: "a-reasoner", LOGIC: "a-logician", FAST: "a-sprinter"}
LOCAL_ID = "qwen3:8b"

#: `--enable-cloud` given. Without it `mode_forbids` drops the cloud candidate and
#: every file is answered on this machine, which is its own test at the bottom.
SENDING_ON = cli.CLOUD_ENABLED_MODE


def _client(target: ModelTarget) -> ModelClient:
    """A client that carries a target and could not reach a model if it tried.

    Nothing here calls one. `route_for` returns the client beside its target and
    every assertion below is about WHICH, so a transport would be a network
    dependency bought for nothing.
    """
    return ModelClient(model_target=target,
                       invoke=lambda payload: b'{"claims": []}')


def _cloud_clients() -> dict:
    return {tier: _client(ModelTarget(locality=CLOUD, model_id=model_id,
                                      provider=PROVIDER))
            for tier, model_id in CLOUD_IDS.items()}


def _local_clients() -> dict:
    one = _client(ModelTarget(locality=LOCAL, model_id=LOCAL_ID,
                              provider=LOCAL_PROVIDER, context_tokens=32768))
    return {tier: one for tier in (REASONING, LOGIC, FAST)}


def _both() -> TierRouting:
    """The deployment the ruling is about: a key AND a model on this machine."""
    return TierRouting(tier_of_call_site=cli.TIER_OF_CALL_SITE,
                       client_of_tier=_cloud_clients(),
                       local_client_of_tier=_local_clients())


def _cloud_only() -> TierRouting:
    return TierRouting(tier_of_call_site=cli.TIER_OF_CALL_SITE,
                       client_of_tier=_cloud_clients())


def _local_only() -> TierRouting:
    return TierRouting(tier_of_call_site=cli.TIER_OF_CALL_SITE,
                       client_of_tier=_local_clients())


@pytest.fixture()
def corpus(conn, tmp_path):
    """Three files, three classification states, one database.

    Shared rather than built per test because every test below asserts about the
    SAME three files from a different site, and three corpora would let one drift
    into measuring a different file.
    """
    from database_agent.files_table import get_file, record_file
    from privacy.classification import ClassificationRecord
    from privacy.classification_store import ClassificationStore
    from privacy.schema import create_privacy_schema
    from privacy.vocabulary import DETECTOR

    create_privacy_schema(conn)
    store = ClassificationStore(conn)

    def _file(name: str, body: bytes) -> tuple[str, str]:
        path = tmp_path / name
        path.write_bytes(body)
        file_id = record_file(
            conn, path, filename=name, normalized_filename=name.lower(),
            extension=".pdf", observed_size=len(body),
            observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
            parent_folder_context="Downloads", mime_type="application/pdf",
            detected_format="pdf", scan_state="included", materialized=True)
        return file_id, get_file(conn, file_id)["content_hash"]

    def _classify(file_id: str, content_hash: str, *, protected: bool,
                  handling: str, basis: str = DETECTOR) -> None:
        store.write(ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=handling, protected=protected, basis=basis,
            evidence_refs=("sha256:" + "b" * 64,), reliability_state="validated",
            observed_at="2026-09-09T00:00:00Z"))

    # ORDINARY MEANS GATE-CLEARED (`00` amendment 7(c)): the local gate read the
    # file and named none of the ten restricted kinds. The rules' word alone
    # (`detector`, protected 0) no longer opens the cloud -- see
    # `test_the_rules_word_alone_keeps_a_file_local`.
    ordinary, ordinary_hash = _file("Lecture 08.pdf", b"work and energy")
    _classify(ordinary, ordinary_hash, protected=False,
              handling="personal_non_sensitive", basis=cli.LOCAL_MODEL_GATE)
    # NO RECORD AT ALL, which is what the detector abstaining leaves behind. It is
    # the common case on a real folder -- 95 of the owner's 199 files -- and it is
    # a sentence about the detector, not about the bytes.
    unclassified, _ = _file("HW 3.pdf", b"question one")
    protected, protected_hash = _file("HKID scan.pdf", b"identity document")
    _classify(protected, protected_hash, protected=True,
              handling="sensitive_personal")
    return {"ordinary": ordinary, "unclassified": unclassified,
            "protected": protected}


def _where(route, corpus) -> dict:
    """The locality each of the three files is routed to, or `None` for none."""
    return {name: (None if route(file_id) is None
                   else route(file_id)[1].locality)
            for name, file_id in corpus.items()}


# --- site A: the one site whose text may cross the internet -------------------

def test_site_a_sends_the_classified_file_to_the_cloud_and_the_rest_here(corpus,
                                                                        conn):
    """The ruling, in one assertion, at the only site it changes today.

    A_fact's text is `ratified` -- the one prompt in this deployment that may leave
    the device -- so it is the site that gets both destinations. The classified,
    unprotected file goes to the provider; the file nothing has classified stays
    here, because `unclassified_denies` refuses every cloud release of one and the
    route is asked the same question the gate will answer.
    """
    route = cli.target_for(conn, _both(), A_FACT, operation_mode=SENDING_ON)

    # `104` §18.7 (9 Sep 2026): the protected file keeps to the local model.
    assert _where(route, corpus) == {
        "ordinary": CLOUD, "unclassified": LOCAL, "protected": LOCAL}


def test_site_a_names_the_model_each_file_actually_goes_to(corpus, conn):
    """Not just the locality: the `model_id`, because that is what the call
    identity records and what a person is owed. `00`:44's cache key includes the
    model, so two files answered by different models must key their answers
    apart -- otherwise a file answered here reuses the provider's verdict."""
    route = cli.target_for(conn, _both(), A_FACT, operation_mode=SENDING_ON)

    assert route(corpus["ordinary"])[1].model_id == CLOUD_IDS[LOGIC]
    assert route(corpus["unclassified"])[1].model_id == LOCAL_ID


def test_the_pair_is_one_destination_and_not_two_descriptions_of_it(corpus, conn):
    """`FactCallAuthorities.__post_init__`'s rule, kept true per file: the gate is
    asked about the target and the transport sends to the client's own."""
    route = cli.target_for(conn, _both(), A_FACT, operation_mode=SENDING_ON)

    for name in ("ordinary", "unclassified"):
        client, target = route(corpus[name])
        assert client.model_target is target


def test_the_protected_file_goes_local_and_never_to_the_cloud(corpus, conn):
    """`104` §18.7 (9 Sep 2026), the owner's ruling: protected material reaches the
    LOCAL model only. `model_route_permitted` now asks the gate's own
    `protected_cloud_denies`, so wherever a local target exists the protected file
    takes it, and where only a cloud target exists it takes nothing -- a `None`
    that is `privacy_withheld` on the file's row: nothing assembled, nothing sent,
    the file present in the report rather than missing from it.

    SABOTAGE: bar protected on every locality again and the `_both()` line goes
    red at every site.
    """
    for site in (A_FACT, C_PLACEMENT, G_SITUATION_SENSITIVITY):
        with_both = cli.target_for(conn, _both(), site, operation_mode=SENDING_ON)
        assert with_both(corpus["protected"])[1].locality == LOCAL
        local_only = cli.target_for(conn, _local_only(), site,
                                    operation_mode=SENDING_ON)
        assert local_only(corpus["protected"])[1].locality == LOCAL
        cloud_only = cli.target_for(conn, _cloud_only(), site,
                                    operation_mode=SENDING_ON)
        assert cloud_only(corpus["protected"]) is None


# --- sites C and G: their own text keeps them here ----------------------------

def test_site_c_splits_the_same_way_a_does_now_that_its_text_is_ratified(corpus,
                                                                        conn):
    """C's `eliminate-v2` was ratified for the cloud on the owner's 9 September
    ruling, so the site gained a cloud candidate and splits exactly as A does: the
    classified, unprotected file to the provider, the one nothing has classified
    kept here, the protected one kept here too (`104` §18.7).

    **This test read the other way one commit ago and the CODE did not change.**
    Under `ratified_local` the cloud candidate was dropped for the site and every
    file went local. `observe_locality_permits` reads the row's own word, so
    ratifying the text moved the route and no line of `target_for` moved with it --
    which is the property `104` R-05's seam exists to have.
    """
    route = cli.target_for(conn, _both(), C_PLACEMENT, operation_mode=SENDING_ON)

    assert _where(route, corpus) == {
        "ordinary": CLOUD, "unclassified": LOCAL, "protected": LOCAL}
    assert route(corpus["ordinary"])[1].model_id == CLOUD_IDS[LOGIC]
    assert route(corpus["unclassified"])[1].model_id == LOCAL_ID


def test_site_g_crosses_only_for_a_file_the_gate_cleared(corpus, conn):
    """`00` amendment 7(c) (12 Sep 2026) re-argues §17.1's "nothing leaves the
    device": the GATE (site H) is the site whose text never crosses, and site G's
    whole-library row is ratified for the cloud -- for a file the gate cleared and
    for no other. A gate-cleared file's situation goes to the provider; an
    unclassified or held file's stays here."""
    route = cli.target_for(conn, _both(), G_SITUATION_SENSITIVITY,
                           operation_mode=SENDING_ON)
    assert _where(route, corpus) == {
        "ordinary": CLOUD, "unclassified": LOCAL, "protected": LOCAL}

def test_the_sites_that_may_not_cross_are_still_on_with_both_models_configured(
        conn):
    """The other half of the regression: a site whose text keeps it here must
    still HAVE a destination when a local model is configured beside a key.
    H (the gate, local by its nature) and D_residual are those sites now -- G's
    whole-library row was ratified for the cloud on 12 Sep 2026 (`00` amendment
    7(c)) and belongs beside A and C.
    """
    from llm_harness.vocabulary import H_RESTRICTED_KIND
    both = _both()
    for site in (D_RESIDUAL, H_RESTRICTED_KIND):
        assert not cli.observe_locality_permits(site, CLOUD), (
            "this test is about sites whose own text keeps them here; if one of "
            "them was ratified for the cloud it belongs beside A and C instead")
        assert cli.site_has_a_destination(conn, both, site,
                                          operation_mode=SENDING_ON)

def test_a_cloud_key_alone_behaves_exactly_as_it_did(corpus, conn):
    """No local model, so a file the cloud may not see gets NO call rather than a
    cloud one. This is the assertion that stops `cloud_permitted=False` from being
    read as "went local": `route_for` answers with the configured client both ways,
    and `target_for` refuses the pair whose locality is not the one it asked
    about."""
    route = cli.target_for(conn, _cloud_only(), A_FACT,
                           operation_mode=SENDING_ON)

    assert _where(route, corpus) == {
        "ordinary": CLOUD, "unclassified": None, "protected": None}


def test_a_local_model_alone_behaves_exactly_as_it_did(corpus, conn):
    """D1's deployment, untouched: one installed model answers every file it may,
    including the unclassified one that no provider may be asked about."""
    route = cli.target_for(conn, _local_only(), A_FACT,
                           operation_mode=SENDING_ON)

    assert _where(route, corpus) == {
        "ordinary": LOCAL, "unclassified": LOCAL, "protected": LOCAL}


def test_with_sending_off_both_models_configured_still_sends_nothing(corpus,
                                                                    conn):
    """`--enable-cloud` unset is `offline`, and this is the starvation the mode
    check exists to prevent. Without it the classified file would be routed to the
    cloud client, reach the gate, be denied for the mode and get NO answer -- where
    the same file used to be answered on this machine. The route is asked the same
    question the gate will answer, which is `104` R-02's whole rule."""
    route = cli.target_for(conn, _both(), A_FACT,
                           operation_mode=cli.OPERATION_MODE)

    assert _where(route, corpus) == {
        "ordinary": LOCAL, "unclassified": LOCAL, "protected": LOCAL}
    assert route(corpus["ordinary"])[1].model_id == LOCAL_ID


def test_the_mode_default_is_the_local_first_floor(corpus, conn):
    """Absent means refuse. A caller that has not said this folder's consent
    permits sending gets a route that does not send, and the cost of the default
    being wrong is a local answer instead of a cloud one -- never a file leaving
    someone's device under a permission they did not give."""
    stated = cli.target_for(conn, _both(), A_FACT,
                            operation_mode=cli.OPERATION_MODE)
    defaulted = cli.target_for(conn, _both(), A_FACT)

    assert (_where(defaulted, corpus) == _where(stated, corpus)
            == {"ordinary": LOCAL, "unclassified": LOCAL, "protected": LOCAL})


# --- the seam: what the authorities carry and what the record says ------------

def test_the_call_identity_records_the_model_each_file_was_routed_to():
    """`00`:44's cache key, per file. `call_identity_dimensions` used to read one
    `authorities.model_target`, which under a per-file route would key two
    destinations' answers under one dimension -- a file answered on this machine
    reusing the provider's cached verdict, and "makes model or prompt changes
    auditable" false in the one direction that matters.

    A `SimpleNamespace` rather than real authorities: what is under test is that
    the identity asks the ROUTE, and a real fact pass would prove the same thing
    through four other moving parts.
    """
    from types import SimpleNamespace

    import model_facts

    cloud = ModelTarget(locality=CLOUD, model_id=CLOUD_IDS[LOGIC],
                        provider=PROVIDER)
    local = ModelTarget(locality=LOCAL, model_id=LOCAL_ID,
                        provider=LOCAL_PROVIDER, context_tokens=32768)
    routed = {"f-cloud": (None, cloud), "f-local": (None, local)}
    authorities = SimpleNamespace(route=lambda file_id: routed[file_id])

    assert model_facts._routed_target(authorities, "f-cloud") is cloud
    assert model_facts._routed_target(authorities, "f-local") is local


def test_an_identity_for_a_file_with_no_route_refuses_rather_than_inventing_one():
    """A call identity written without a model would key a file's answers under a
    destination nothing sent them to."""
    from types import SimpleNamespace

    import model_facts

    authorities = SimpleNamespace(route=lambda _file_id: None)

    with pytest.raises(ValueError, match="routed to no model"):
        model_facts._routed_target(authorities, "f-protected")


def test_site_as_authorities_carry_the_route_and_hold_no_single_pair(corpus,
                                                                    conn):
    """Deliverable 4's seam, on the object the fact pass actually runs against.

    `fact_call_authorities` used to set `model_client` and `model_target` from
    `routing.client_for(A_FACT)`. It sets neither now: the two spellings must not
    both be in force, because a single pair beside a per-file route describes a
    destination that is only sometimes the one used, and a reader trusting it would
    be right about some files and silently wrong about the rest.
    """
    from production import (
        folder_levels_for, load_shipped_catalogue, read_packaged_library_file,
    )

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    authorities = cli.fact_call_authorities(
        conn, routing=_both(), scan_run_id="scan", corpus_file_count=3,
        policy_version="policy", wire_handle_key=bytes(32), schema="academic",
        folder_levels=folder_levels_for(catalogue, "academic.coursework"),
        user_id="t", now=lambda: "2026-09-09T00:00:00+00:00",
        operation_mode=SENDING_ON)

    assert authorities.model_client is None
    assert authorities.model_target is None
    assert authorities.route(corpus["ordinary"])[1].locality == CLOUD
    assert authorities.route(corpus["unclassified"])[1].locality == LOCAL
    # `104` §18.7: the protected file keeps to the local model.
    assert authorities.route(corpus["protected"])[1].locality == LOCAL


def test_the_authorities_refuse_to_hold_both_spellings_at_once():
    """The guard behind the test above, asked directly: a route AND a pair is two
    answers to one question, and this project has paid for that twice."""
    from types import SimpleNamespace

    import model_facts
    from production import (
        folder_levels_for, load_shipped_catalogue, read_packaged_library_file,
    )

    levels = folder_levels_for(
        load_shipped_catalogue(read_packaged_library_file), "academic.coursework")
    target = ModelTarget(locality=LOCAL, model_id=LOCAL_ID,
                         provider=LOCAL_PROVIDER, context_tokens=32768)
    client = _client(target)
    with pytest.raises(ValueError, match="State one or the other"):
        model_facts.FactCallAuthorities(
            gate=SimpleNamespace(), model_client=client,
            prompt=SimpleNamespace(), model_target=target,
            activation_signals=SimpleNamespace(signals=()),
            folder_levels=levels, normalizers={}, normalize=lambda *a: None,
            normalize_for_review=lambda *a: None, contradicts=lambda *a: False,
            evidence_resolver=lambda key: None, scan_budget=SimpleNamespace(),
            estimated_cost=1, actual_cost=1, policy_version="p",
            wire_handle_key=bytes(32), max_released_observations=1,
            max_dossier_tokens=1, observed_at=lambda: "T", on_result=None,
            route_for=lambda _file_id: (client, target))


# --- the guards OUTSIDE the passes, which read the routing too -----------------
#
# Every one of these decides whether a pass runs at all, and each read
# `routing.locality_for(site)` -- the CLOUD half's answer on a two-target routing.
# A per-file route inside a pass that never runs is a per-file route nobody
# reaches, so the guards are pinned here beside the choice they gate.

def test_the_fact_pass_runs_with_both_models_configured_and_sending_off(conn):
    """THE STARVATION THIS ALMOST SHIPPED. The fact pass returned early when
    `locality_for(A_FACT) == CLOUD` and the mode was not `hybrid`. Under the old
    per-site split A_fact was LOCAL, so that was False and a person with both
    models and sending off had every file answered on their own machine. On a
    two-target routing it is True -- and the whole pass would have returned,
    answering nothing at all."""
    assert cli.site_has_a_destination(conn, _both(), A_FACT,
                                      operation_mode=cli.OPERATION_MODE)
    assert cli.site_has_a_destination(conn, _both(), A_FACT,
                                      operation_mode=SENDING_ON)
    # And the half that must NOT move: a cloud key alone, with sending off, has
    # nowhere to send and the pass is right to stop.
    assert not cli.site_has_a_destination(conn, _cloud_only(), A_FACT,
                                          operation_mode=cli.OPERATION_MODE)


def test_site_gs_guard_lets_the_pass_run_on_a_two_target_deployment(conn):
    """`104` §17.1 said nothing leaves the device at site G, and the guard used to
    enforce that by reading `locality_for(G)`. The site is asked whether it has a
    DESTINATION, and on a two-target routing it has one. `00` amendment 7(c): G's
    row is ratified for the cloud, so a cloud key alone is a destination for G too
    -- the gate-cleared files reach it and the rest get no call rather than a
    cloud one. The site whose text never crosses is the GATE, and a cloud key
    alone leaves it with nowhere to ask."""
    from llm_harness.vocabulary import H_RESTRICTED_KIND
    for mode in (cli.OPERATION_MODE, SENDING_ON):
        assert cli.site_has_a_destination(conn, _both(),
                                          G_SITUATION_SENSITIVITY,
                                          operation_mode=mode)
    assert cli.site_has_a_destination(conn, _cloud_only(),
                                      G_SITUATION_SENSITIVITY,
                                      operation_mode=SENDING_ON)
    assert not cli.site_has_a_destination(conn, _cloud_only(), H_RESTRICTED_KIND,
                                          operation_mode=SENDING_ON)

def test_the_placement_evidence_is_gathered_under_the_destination_it_will_go_to(
        corpus, conn):
    """Site C's evidence was gathered under one locality for the whole run, and it
    has to follow the FILE: the classified file's dossier goes to a provider and
    the unclassified file's to the model here, and cloud and local release
    different sets. Gathering both under one answer offers the model a reading the
    other call refuses, or withholds one it was entitled to see."""
    route = cli.target_for(conn, _both(), C_PLACEMENT, operation_mode=SENDING_ON)

    assert route(corpus["ordinary"])[1].locality == CLOUD
    assert route(corpus["unclassified"])[1].locality == LOCAL


def test_site_c_asks_nobody_over_the_internet_when_sending_is_off(corpus, conn):
    """C's text may cross the internet; this folder's consent is what says whether
    it does. With sending off the mode drops the cloud candidate and every file is
    answered here -- and the injections must be told the mode for that to be true,
    because the evidence gathered for the call reads it and a default would have
    collected readings for a destination the call never used."""
    route = cli.target_for(conn, _both(), C_PLACEMENT,
                           operation_mode=cli.OPERATION_MODE)

    assert _where(route, corpus) == {
        "ordinary": LOCAL, "unclassified": LOCAL, "protected": LOCAL}


def test_the_rules_word_alone_keeps_a_file_local(corpus, conn, tmp_path):
    """`00` amendment 7(c): a cloud route needs the gate's clearance or the
    person's own word. A `detector` row with `protected = 0` is the rules' word,
    and the rules released two health forms on the second corpus (`104` §18.56),
    so under a cloud-sending mode that file takes the LOCAL target."""
    from database_agent.files_table import get_file, record_file
    from privacy.classification import ClassificationRecord
    from privacy.classification_store import ClassificationStore
    path = tmp_path / "Lecture 09.pdf"; path.write_bytes(b"rules only")
    file_id = record_file(
        conn, path, filename=path.name, normalized_filename=path.name.lower(),
        extension=".pdf", observed_size=10,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=get_file(conn, file_id)["content_hash"],
        handling_class="personal_non_sensitive", protected=False, basis="detector",
        evidence_refs=("sha256:" + "c" * 64,), reliability_state="validated",
        observed_at="2026-09-12T00:00:00Z"))
    for site in (A_FACT, G_SITUATION_SENSITIVITY):
        route = cli.target_for(conn, _both(), site, operation_mode=SENDING_ON)
        assert route(file_id)[1].locality == LOCAL
    assert cli.target_for(conn, _both(), A_FACT, operation_mode=SENDING_ON)(
        corpus["ordinary"])[1].locality == CLOUD


def test_site_gs_route_is_built_under_the_runs_mode_not_the_offline_default():
    """Measured 12 Sep 2026 on the second corpus: the gate cleared 181 files and
    every one of their situation calls went to the local model, because site G
    built its route with `target_for`'s default mode, `offline`, under which
    `mode_forbids` drops the cloud candidate before any file is asked. Sites A and
    C pass the run's mode; G does now too, and the run's call site hands it over."""
    import inspect
    import re
    assert "operation_mode" in inspect.signature(cli.ask_the_situation).parameters
    source = inspect.getsource(cli)
    site = source[source.index("def ask_the_situation("):]
    site = site[:site.index("\ndef ", 1)]
    # The route may carry more than the mode (the run's own clearances since 13
    # Sep); the pin is that it carries the mode.
    assert re.search(r"target_for\(conn, routing, G_SITUATION_SENSITIVITY,\s*operation_mode=operation_mode[,)]", site)
    call = source[source.index("            ask_the_situation(\n"):]
    call = call[:call.index(")\n", call.index("user_id=user_id")) + 1]
    assert "operation_mode=operation_mode" in call
