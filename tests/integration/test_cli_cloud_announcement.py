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


def test_a_run_that_cannot_send_does_not_tell_the_person_it_may():
    said = _announced(_Consent())

    assert "may be sent" not in said
    assert "Nothing was sent and nothing could have been" in said
    # The reason, not just the denial: a person who is told nothing was sent and
    # not told why cannot tell a wired product from a broken one.
    assert "no part of this run can call one yet" in said
    assert "judged on this device" in said


def test_it_still_says_sending_is_on_and_how_to_turn_it_off():
    """The absent call site is not a reason to stop reporting durable consent.

    The owner accepted that consent outlives the moment it was given. That is
    survivable only because every run says the consent is there and how to end it,
    and it is MORE important while nothing sends, not less: this is the run where a
    person might otherwise conclude the setting does not matter.
    """
    said = _announced(_Consent())

    assert "Cloud sending is ON for this folder" in said
    assert "Turned on by jy on 2026-06-14" in said
    assert "/Users/jy/Desktop/Files" in said
    assert "--disable-cloud" in said
    assert "it stays\n  on for the next one" in said or "stays on for the next" in said


def test_the_consent_off_header_makes_no_claim_about_sending_either():
    """The quieter half of the branch carried the same untruth.

    Naming three models under the word "Model:" reads as a statement about what
    this run will do with them.
    """
    said = _announced(None)

    assert "for facts," not in said
    assert "no part of this run can call one yet" in said
    assert "judged on this device" in said


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
