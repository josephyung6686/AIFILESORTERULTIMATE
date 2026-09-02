"""What the run says about sending, measured against what it can actually do.

`94` F2: with a key and `--enable-cloud` the screen said, before the scan, that
files "may be sent to deepseek-reasoner (facts), deepseek-chat (checks) and
deepseek-chat (review sets)" -- while every model injection point in this file is
`None`, so nothing in `src/` can construct a model request at all.

A route is not a call site, and the difference is not pedantry on this screen. A
person who read that sentence and turned sending off was acting on a fear the
product had given them about something that could not happen. A person who read it
and left it on believed they had been told the truth about their files. `84` §6:
what the screen tells a person has to be true.

The load-bearing test here is the LAST one. The others check the sentences; that
one checks the flag against the injections, so `MODEL_CALL_SITES_WIRED` cannot
drift away from what is true without something going red.
"""
import ast
import io
import re
from pathlib import Path

import cli


class _Routing:
    """Enough of `TierRouting` to be announced. It is never called, which is the point."""

    def model_id_for(self, site):
        return f"model-for-{site}"


class _Consent:
    permits_sending = True
    user_id = "jy"
    decided_at = "2026-06-14"


def _announced(consent):
    out = io.StringIO()
    cli.announce_cloud_posture(
        _Routing(), consent, corpus_root=Path("/Users/jy/Desktop/Files"), out=out)
    return out.getvalue()


def _unwrapped(said: str) -> str:
    """The same text with line breaks collapsed.

    Sentence assertions run against this. Where a wrap falls is presentation, and
    a phrase spanning a line break is not a defect -- but a TOKEN spanning one is,
    which is what `test_nothing_a_person_must_type_is_broken_across_lines` holds
    against the raw text instead.
    """
    return " ".join(said.split())


def test_a_run_that_cannot_send_does_not_tell_the_person_it_may():
    said = _announced(_Consent())

    assert "may be sent" not in said
    assert "Nothing was sent and nothing could have been" in _unwrapped(said)
    # The reason, not just the denial: a person who is told nothing was sent and
    # not told why cannot tell a wired product from a broken one.
    assert "no part of this run can call one yet" in _unwrapped(said)
    assert "judged on this device" in _unwrapped(said)


def test_it_still_says_sending_is_on_and_how_to_turn_it_off():
    """The absent call site is not a reason to stop reporting durable consent.

    The owner accepted that consent outlives the moment it was given. That is
    survivable only because every run says the consent is there and how to end it,
    and it is MORE important while nothing sends, not less: this is the run where a
    person might otherwise conclude the setting does not matter.
    """
    said = _announced(_Consent())

    assert "Cloud sending is ON for this folder" in _unwrapped(said)
    assert "Turned on by jy on 2026-06-14" in _unwrapped(said)
    assert "/Users/jy/Desktop/Files" in said
    assert "--disable-cloud" in said
    assert "Sending stays ON for this folder until you turn it off" in _unwrapped(said)
    # NAMED, not "an external provider": a person told the name has been told more.
    # And the standing rule said where the person is deciding. Both were dropped by
    # a first version of this branch and both matter MORE once the wiring lands --
    # somebody reading today's notice is deciding about tomorrow's runs.
    for tier in ("model-for-A_fact", "model-for-C_placement", "model-for-D_residual"):
        assert tier in said
    assert "Protected material" in said


def test_the_consent_off_header_gives_both_reasons_nothing_is_sent():
    """Two independent reasons, and the person is given both.

    A first version of this branch returned early when the call sites were
    unwired, and in doing so dropped the whole consent explanation -- a person
    with sending OFF lost the sentence saying so and the command that turns it on.
    That traded one untruth for a worse silence, which is why the wiring sentence
    is ADDED to the consent one rather than replacing it.

    The two causes have different owners, which is why both have to be said. One
    is the person's choice and they can change it; the other is the product's
    state and they cannot. A notice giving only the second reads as "you need not
    have bothered"; a notice giving only the first lets them believe that turning
    it on tomorrow changes something about today.
    """
    said = _announced(None)

    said = _unwrapped(said)
    assert "None of them will be asked on this run" in said
    assert "Cloud sending is off for this folder" in said
    assert "--enable-cloud" in said
    assert "No part of this run can call a model yet either" in said


def test_the_flag_agrees_with_the_injections_rather_than_with_itself():
    """The one that cannot be satisfied by editing a sentence.

    `MODEL_CALL_SITES_WIRED` is a claim about five keyword arguments in this file.
    Asserting it against a constant would be a tautology -- flipping the constant
    would move the assertion with it, which is exactly how the length check on the
    wire handle key turned out vacuous. So this reads the arguments.
    """
    tree = ast.parse(Path(cli.__file__).read_text())
    injections = {"p8_run_call", "model_client", "gate", "prompt",
                  "call_dependencies"}
    passed_none = set()
    passed_something = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg not in injections:
                continue
            if isinstance(keyword.value, ast.Constant) and keyword.value.value is None:
                passed_none.add(keyword.arg)
            else:
                passed_something.add(keyword.arg)

    # Every one of the five appears, and appears as `None`. If that stops being
    # true the sentence above is a lie again and this is where it is caught.
    assert passed_none == injections, (
        f"expected all five model injections to be None; got {sorted(passed_none)}")
    assert cli.MODEL_CALL_SITES_WIRED is (not passed_none or bool(passed_something)), (
        "MODEL_CALL_SITES_WIRED disagrees with the injections in this file. If a "
        "call site was just wired, flip the flag -- but only once a prompt is "
        "ratified too, or the announcement becomes untrue one step later.")


def test_nothing_a_person_must_type_is_broken_across_lines():
    """`textwrap` split `--enable-cloud` into `--enable-` and `cloud`.

    The product was telling a person to type something that is not typeable, on
    the screen where it explains how to stop sending their files. `_role_lines`
    already carried the rule -- a command broken across two lines is a command
    that does not work -- and applied it by keeping pasteable lines out of the
    wrapper; a flag named INSIDE a sentence never reaches that escape.

    Model ids too: `model-for-D_residual` came out as `model-for-` then
    `D_residual`, leaving a name a person could not read or search for. Asserting
    the WHOLE token rather than a prefix is what caught it -- `85` §13.8 earning
    its keep on a defect nobody was looking for.
    """
    # `\w-+$` and not `endswith("-")`: a line ending in a standalone " --" is an
    # em-dash separator and a whole token in itself. What is a defect is a hyphen
    # welded to the word before it, which is a token the wrapper split.
    broken = re.compile(r"\w-+$")
    for said in (_announced(_Consent()), _announced(None)):
        for line in said.splitlines():
            assert not broken.search(line.rstrip()), (
                f"a token is broken across lines: {line!r}")
        joined = _unwrapped(said)
        assert "--enable-cloud" in joined or "--disable-cloud" in joined
        for tier in ("A_fact", "C_placement", "D_residual"):
            assert f"model-for-{tier}" in joined
