# tests/test_cli_cloud_consent.py
"""Turning the model on, once, and being able to see it and take it back.

The owner's ruling has three parts and the third is the one with teeth: consent
is recorded durably, every later run proceeds without re-asking, and *"consent
outlives the moment it was given"*. The first two are convenience. The third is a
person's files leaving their computer in September because of a sentence they read
in June, and the tests below are the three things that make that survivable --
revocable, visible, and scoped to what they could actually see when they decided.

`test_cloud_consent.py` proves the record. This file proves the COMPOSITION: that
the record reaches the operation mode, that the mode reaches P7's stored policy,
and that the person is told before anything is sent rather than after.
"""
from __future__ import annotations

import io

import pytest

import cli
from database_agent.cloud_consent import DISABLED, ENABLED, cloud_consent_for
from database_agent.db import open_database
from privacy.defaults import LOCAL_FIRST_MODES
from privacy.schema import POLICIES_TABLE
from privacy.vocabulary import OPERATION_MODES
from readers.model_deepseek import CREDENTIAL_NAME
from readers.model_routing import FAST, LOGIC, MODEL_NAME_OF_TIER, REASONING

ENV = {CREDENTIAL_NAME: "sk-not-a-real-key", "DEEPSEEK_BASE_URL": "https://api.example",
       MODEL_NAME_OF_TIER[REASONING]: "a-reasoner",
       MODEL_NAME_OF_TIER[LOGIC]: "a-logician",
       MODEL_NAME_OF_TIER[FAST]: "a-sprinter"}


@pytest.fixture(autouse=True)
def _no_ambient_key(monkeypatch, tmp_path):
    """The developer's own key must not decide whether these tests pass."""
    for name in (CREDENTIAL_NAME, "DEEPSEEK_BASE_URL", *MODEL_NAME_OF_TIER.values()):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")


@pytest.fixture()
def corpus(tmp_path):
    folder = tmp_path / "holder" / "coursework"
    folder.mkdir(parents=True)
    (folder / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026.\n")
    return folder


def _run(corpus, *extra, monkeypatch=None, env=None):
    for name, value in (env or {}).items():
        monkeypatch.setenv(name, value)
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(corpus.parent / "plan.sqlite"),
                     *extra], out=out)
    return code, out.getvalue()


def _database(corpus):
    return open_database(corpus.parent / "plan.sqlite", scan_roots=[corpus])


# --- the mode an enabled record selects, which is the owner's open question ----

def test_the_mode_is_hybrid_and_not_the_one_that_sounds_more_permissive():
    """`cloud_assisted` is the WEAKER mode and that is not obvious from its name.

    `privacy/denial.py`'s `protected_cloud_denies` lets a PROTECTED file reach a
    cloud target under exactly one condition -- `cloud_assisted` plus a grant
    naming its scope -- and returns True unconditionally under `hybrid`. So the
    mode whose sentence sounds like `--enable-cloud` is the one carrying a
    carve-out for the material this product promises never to open.
    """
    assert cli.CLOUD_ENABLED_MODE == "hybrid"
    assert cli.CLOUD_ENABLED_MODE in OPERATION_MODES
    assert cli.CLOUD_ENABLED_MODE not in LOCAL_FIRST_MODES


def test_the_weaker_mode_really_is_the_one_that_would_let_protected_material_out():
    """Not asserted from the docstring: asked of P7's own predicate. If this ever
    flips, the reasoning above is wrong and the choice has to be remade."""
    from privacy.denial import protected_cloud_denies

    asked = dict(protected=True, locality="cloud", scope="an-area",
                 granted_scopes=("an-area",))
    assert protected_cloud_denies(operation_mode="cloud_assisted", **asked) is False
    assert protected_cloud_denies(operation_mode=cli.CLOUD_ENABLED_MODE,
                                  **asked) is True


def test_no_decision_means_the_local_first_floor():
    """Absent is not ambiguous. The default is what happens by NOT choosing, which
    is `80` §8's first condition and the only arrangement in which forgetting is
    safe."""
    assert cli.operation_mode_for(None) == cli.OPERATION_MODE
    assert cli.OPERATION_MODE in LOCAL_FIRST_MODES


def test_a_withdrawn_decision_means_the_local_first_floor_too():
    from database_agent.cloud_consent import CloudConsent

    withdrawn = CloudConsent(corpus_root="/a", decision=DISABLED, user_id="jy",
                             decided_at="2026-01-01T00:00:00+00:00")
    assert cli.operation_mode_for(withdrawn) == cli.OPERATION_MODE


def test_an_enabled_decision_selects_the_cloud_mode():
    from database_agent.cloud_consent import CloudConsent

    enabled = CloudConsent(corpus_root="/a", decision=ENABLED, user_id="jy",
                           decided_at="2026-01-01T00:00:00+00:00")
    assert cli.operation_mode_for(enabled) == cli.CLOUD_ENABLED_MODE


# --- once, and then never again -----------------------------------------------

def test_the_flag_records_the_decision_and_the_run_proceeds(corpus, monkeypatch):
    code, printed = _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    assert code == 0
    assert "Folders in this plan" in printed
    conn = _database(corpus)
    try:
        assert cloud_consent_for(conn, str(corpus.resolve())).permits_sending
    finally:
        conn.close()


def test_a_later_run_with_no_flag_still_sends(corpus, monkeypatch):
    """THE ruling, in one test. The friction budget is spent once."""
    _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    _, printed = _run(corpus, monkeypatch=monkeypatch, env=ENV)
    assert "Cloud sending is ON" in printed


def test_the_stored_policy_carries_the_mode_and_not_just_the_screen(
        corpus, monkeypatch):
    """The composition, not the sentence. `84` §5: the dominant defect class is
    wiring -- a notice that said "ON" while P7 was still handed `offline` would be
    the most dangerous version of this feature, because it would read as working.
    """
    _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    conn = _database(corpus)
    try:
        versions = [row["operation_mode"] for row in conn.execute(
            f"SELECT operation_mode FROM {POLICIES_TABLE} ORDER BY rowid")]
    finally:
        conn.close()
    assert versions and versions[-1] == cli.CLOUD_ENABLED_MODE


def test_a_run_nobody_enabled_stores_the_local_first_mode(corpus, monkeypatch):
    _run(corpus, monkeypatch=monkeypatch, env=ENV)
    conn = _database(corpus)
    try:
        versions = [row["operation_mode"] for row in conn.execute(
            f"SELECT operation_mode FROM {POLICIES_TABLE} ORDER BY rowid")]
    finally:
        conn.close()
    assert versions and set(versions) == {cli.OPERATION_MODE}


def test_the_replay_bundle_records_the_mode_the_run_actually_operated_under(
        corpus, monkeypatch):
    """P2's `bundle_manifest.policy_settings` is what §8.5's replay reads to find
    out what a run was ALLOWED to do. It reached this from a second wire --
    `p1_p7_authorities`, not `set_privacy_policy` -- and a mode threaded down one
    wire and not the other produces two records of one run that disagree, with the
    disagreement discoverable only by a person replaying it months later.
    """
    import json

    _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    conn = _database(corpus)
    try:
        settings = [json.loads(row["policy_settings"]) for row in conn.execute(
            "SELECT policy_settings FROM bundle_manifest ORDER BY rowid")]
    finally:
        conn.close()
    assert settings, "no replay bundle was written"
    assert {row.get("operation_mode") for row in settings} == {
        cli.CLOUD_ENABLED_MODE}


def test_the_two_records_of_one_run_agree(corpus, monkeypatch):
    """The pair, checked against each other rather than each against a constant.
    P7's stored policy and P2's replay bundle are the two places a later reader
    can learn what this run was permitted to do, and they are filled from two
    different arguments."""
    import json

    _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    conn = _database(corpus)
    try:
        policy_modes = {row["operation_mode"] for row in conn.execute(
            f"SELECT operation_mode FROM {POLICIES_TABLE}")}
        bundle_modes = {json.loads(row["policy_settings"]).get("operation_mode")
                        for row in conn.execute(
                            "SELECT policy_settings FROM bundle_manifest")}
    finally:
        conn.close()
    assert policy_modes == bundle_modes


def test_the_stored_reason_stops_saying_offline_when_the_run_is_not(
        corpus, monkeypatch):
    """The policy's own `reason` column said "offline run from the command line"
    unconditionally. Under a mode that sends, that is a policy whose stored reason
    contradicts the policy -- in the record §8.5's replay reads to find out what a
    run was allowed to do."""
    _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    conn = _database(corpus)
    try:
        reasons = " ".join(
            str(row["explanation"]) for row in conn.execute(
                "SELECT explanation FROM events WHERE event_type = 'policy_set'"))
    finally:
        conn.close()
    assert "offline run from the command line" not in reasons


# --- it can be taken back, by a gesture as small as the one that gave it -------

def test_disable_cloud_needs_nothing_but_the_folder(corpus, monkeypatch):
    """No situation, no label. A person who wants sending to stop should not have
    to answer two questions about how they want their files organised first."""
    _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    out = io.StringIO()
    code = cli.main([str(corpus), "--user", "jy",
                     "--database", str(corpus.parent / "plan.sqlite"),
                     "--disable-cloud"], out=out)
    assert code == 0
    assert "off" in out.getvalue()
    conn = _database(corpus)
    try:
        assert cloud_consent_for(conn, str(corpus.resolve())).decision == DISABLED
    finally:
        conn.close()


def test_disabling_does_not_run_a_scan(corpus, monkeypatch):
    """A person turning sending off is not asking to be scanned, and a scan that
    ran anyway would be the last thing they wanted at that moment."""
    out = io.StringIO()
    cli.main([str(corpus), "--user", "jy",
              "--database", str(corpus.parent / "plan.sqlite"),
              "--disable-cloud"], out=out)
    assert "Folders in this plan" not in out.getvalue()


def test_a_later_run_after_revoking_does_not_send(corpus, monkeypatch):
    _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    cli.main([str(corpus), "--user", "jy",
              "--database", str(corpus.parent / "plan.sqlite"),
              "--disable-cloud"], out=io.StringIO())
    _, printed = _run(corpus, monkeypatch=monkeypatch, env=ENV)
    assert "Cloud sending is ON" not in printed
    assert "None of them will be asked" in printed


def test_sending_can_be_withdrawn_for_a_folder_that_no_longer_exists(
        corpus, monkeypatch):
    """Deliberately no `is_dir` check on this path. A person tidying up after
    themselves must be able to turn sending off for a folder they have deleted --
    refusing would leave a record saying "enabled" with nothing able to change it,
    and consent that cannot be withdrawn is not consent."""
    _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    database = corpus.parent / "plan.sqlite"
    resolved = str(corpus.resolve())
    for child in corpus.iterdir():
        child.unlink()
    corpus.rmdir()
    out = io.StringIO()
    code = cli.main([str(corpus), "--user", "jy", "--database", str(database),
                     "--disable-cloud"], out=out)
    assert code == 0
    conn = open_database(database)
    try:
        assert cloud_consent_for(conn, resolved).decision == DISABLED
    finally:
        conn.close()


def test_disable_cloud_with_no_folder_says_why_rather_than_guessing(capsys):
    """There is no single switch, because consent is per folder. Saying that is
    better than throwing whichever switch happened to be nearest."""
    with pytest.raises(SystemExit):
        cli.main(["--disable-cloud", "--user", "jy"], out=io.StringIO())
    assert "per folder" in capsys.readouterr().err


def test_the_two_flags_together_stop_and_ask(corpus, capsys):
    """`84` §6: a gesture that acts on something other than what the person named
    is worse than one that stops and asks. Neither order of these two is more
    obviously right, and picking one would decide what leaves the device by
    argument order."""
    with pytest.raises(SystemExit):
        cli.main([str(corpus), "--situation", "academic.coursework",
                  "--label", "Coursework", "--enable-cloud", "--disable-cloud"],
                 out=io.StringIO())
    assert "opposite things" in capsys.readouterr().err


# --- THE SCOPE, end to end ----------------------------------------------------

def test_enabling_one_folder_does_not_enable_another(tmp_path, monkeypatch):
    """The failure the whole design is bent around, proved through the command
    rather than through the store. Two folders, one database -- which is what a
    person gets by running twice from the same directory."""
    holder = tmp_path / "holder"
    first = holder / "coursework"
    second = holder / "taxes"
    for folder in (first, second):
        folder.mkdir(parents=True)
        (folder / "a note.txt").write_text("PHYS 1401 Syllabus\n\nSpring 2026.\n")
    for name, value in ENV.items():
        monkeypatch.setenv(name, value)
    database = str(holder / "plan.sqlite")

    def go(folder, *extra):
        out = io.StringIO()
        cli.main([str(folder), "--situation", "academic.coursework",
                  "--label", "Coursework", "--user", "jy",
                  "--database", database, *extra], out=out)
        return out.getvalue()

    assert "Cloud sending is ON" in go(first, "--enable-cloud")
    assert "Cloud sending is ON" not in go(second)
    assert "None of them will be asked" in go(second)


# --- it stays visible, and the notice comes first -----------------------------

def test_the_notice_is_printed_before_the_scan_starts(corpus, monkeypatch):
    """`80` §8 and `88` §3, in the same words: a run that sends says so BEFORE
    sending. A notice at the end is a receipt, and a receipt is what a person gets
    instead of a choice. "Protected containers" is the first line `run` prints, so
    it marks where the scan begins."""
    _, printed = _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    assert printed.index("Cloud sending is ON") < printed.index(
        "Protected containers")


def test_the_notice_names_the_day_and_the_person(corpus, monkeypatch):
    """Because the consent is durable. "Cloud sending is on" is not enough to let
    somebody recognise a decision they have forgotten making; a date and a name
    are."""
    _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    conn = _database(corpus)
    try:
        consent = cloud_consent_for(conn, str(corpus.resolve()))
    finally:
        conn.close()
    _, printed = _run(corpus, monkeypatch=monkeypatch, env=ENV)
    assert consent.decided_at in printed
    assert "by jy" in printed


def test_the_notice_names_the_models_that_would_receive_the_files(
        corpus, monkeypatch):
    """A person told their files go to "an external provider" has been told less
    than a person told the name. `questions/proposal.py` makes the same argument
    for the self-description notice.

    IT NAMES THE MODELS A CALL SITE ACTUALLY ROUTES TO, and that is now two of the
    three rather than all three. `TIER_OF_CALL_SITE` no longer sends any site to the
    REASONING tier -- A_fact was the only one that did, and measurement on the
    owner's real files moved it to LOGIC -- so a run configured with all three names
    has a reasoning model that nothing can reach.

    Naming it anyway would be the same untruth `WIRED_CALL_SITES` was made a set to
    stop telling: a person reading this notice is deciding what may leave their
    machine, and a model listed there that no route reaches makes the decision look
    larger than it is. The negative assertion is the point of the test, so it is
    asserted and not merely implied by dropping the name from the loop.
    """
    _, printed = _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    for model_id in ("a-logician", "a-sprinter"):
        assert model_id in printed
    assert "a-reasoner" not in printed, (
        "the notice names a model no call site routes to:\n" + printed)


def test_the_notice_says_protected_material_is_not_among_them(corpus, monkeypatch):
    """THE standing rule, said where a person is deciding about sending. It is
    true -- `protected_cloud_denies` is unconditional under this mode -- and a
    notice that left it out would let a person believe they had just authorised
    more than they had."""
    _, printed = _run(corpus, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    assert "Protected material" in printed


def test_the_off_sentence_uses_the_designs_own_words(corpus, monkeypatch):
    """MOVED here from `test_cli_model_route.py`, which used to own this sentence
    when `model_route` printed it. §8.4's four mode sentences are pinned in
    `privacy.vocabulary.MODE_SEMANTICS` precisely so a paraphrase cannot promise
    less than the original, so the screen quotes them rather than restating them.
    """
    from privacy.vocabulary import MODE_SEMANTICS

    _, printed = _run(corpus, monkeypatch=monkeypatch, env=ENV)
    assert MODE_SEMANTICS[cli.OPERATION_MODE].split(";")[0] in printed
    assert cli.OPERATION_MODE in printed


def test_every_sending_run_says_how_to_turn_it_off(corpus, monkeypatch):
    """Consent that cannot be withdrawn is not consent, and a withdrawal a person
    has to go and look up is one they will not make."""
    for extra in (("--enable-cloud",), ()):
        _, printed = _run(corpus, *extra, monkeypatch=monkeypatch, env=ENV)
        assert "--disable-cloud" in printed


def test_the_line_it_tells_you_to_type_is_pasteable(tmp_path, monkeypatch):
    """`84` §6, applied again: what the screen tells a person to type has to be
    true. The folders this product is for have spaces in their names, and an
    unquoted path is a command that names a different folder -- or two."""
    import shlex

    folder = tmp_path / "holder" / "my course work"
    folder.mkdir(parents=True)
    (folder / "a note.txt").write_text("PHYS 1401 Syllabus\n\nSpring 2026.\n")
    _, printed = _run(folder, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    line = next(row for row in printed.splitlines() if "--disable-cloud" in row)
    parsed = shlex.split(line)
    assert parsed[1] == str(folder.resolve())
    assert parsed[2] == "--disable-cloud"


def test_the_path_is_never_broken_across_lines(tmp_path, monkeypatch):
    """`textwrap` breaks a long unbroken token in half. Half a path on each of two
    lines is a path a person cannot read and must not copy, and the deep nested
    folders this product is for produce exactly that."""
    folder = tmp_path / "holder" / ("a" * 60) / "coursework"
    folder.mkdir(parents=True)
    (folder / "a note.txt").write_text("PHYS 1401 Syllabus\n\nSpring 2026.\n")
    _, printed = _run(folder, "--enable-cloud", monkeypatch=monkeypatch, env=ENV)
    # On a line of its OWN, and asserted that way: the pasteable turn-off command
    # further down also carries the whole path, so `path in printed` is satisfied
    # by that line and cannot see the broken one above it. That is precisely the
    # shape of a guard that has quietly stopped guarding.
    assert any(line.strip() == str(folder.resolve())
               for line in printed.splitlines()), printed


def test_enabled_with_no_key_says_nothing_was_sent(corpus, monkeypatch):
    """The state a person can most easily be wrong about: they turned sending on,
    so they believe it is sending. It is not, and the header says so rather than
    letting them assume."""
    _, printed = _run(corpus, "--enable-cloud", monkeypatch=monkeypatch)
    assert "Cloud sending is ON" in printed
    assert "no model is configured" in printed
    assert "nothing could have been" in printed


def test_the_key_never_reaches_the_screen(corpus, monkeypatch):
    for extra in (("--enable-cloud",), ()):
        _, printed = _run(corpus, *extra, monkeypatch=monkeypatch, env=ENV)
        assert ENV[CREDENTIAL_NAME] not in printed
