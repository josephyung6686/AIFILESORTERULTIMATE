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


def test_a_run_that_can_send_says_exactly_which_question_leaves_the_device():
    """The other half of the same rule, and the half that arrived on 2026-09-03.

    This test used to require "Nothing was sent and nothing could have been",
    because no injection point in `cli.py` carried a model and the sentence was
    the truth. `A_fact` is wired now, so that sentence would be the untruth --
    and the fix is not to delete the assertion but to invert it: the notice has to
    say what CAN leave, and it has to be as specific as what can leave is.

    `C_placement` and `D_residual` are still unwired (`placement_inputs` passes
    `gate=None, model_client=None, prompt=None, call_dependencies=None`, and P9
    still gets `p8_run_call=None`), so a notice that said "files may be sent to
    three models" would frighten a person about two things that cannot happen.
    One wired site, one named recipient, and the other two said to be unreachable.
    """
    said = _unwrapped(_announced(_Consent()))

    assert "may be sent to model-for-A_fact" in said
    assert "That is the only question this run can ask a model" in said
    # The two that are configured and cannot be reached, said to be unreachable
    # rather than left out: a person who sees only one name cannot tell a wired
    # product from a misconfigured one.
    assert "are configured and no part of this run can reach them yet" in said
    assert "nothing goes to either" in said
    # And the old sentence is GONE from the branch it was true in.
    assert "Nothing was sent and nothing could have been" not in said


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
    # a first version of this branch and both matter MORE now that the wiring has
    # landed -- somebody reading today's notice is deciding about tomorrow's runs.
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
    # WHAT TURNING IT ON WOULD DO, which replaced "still send nothing" when
    # `A_fact` was wired. The two causes still have different owners and both are
    # still said; what changed is that the second one now has a consequence, and a
    # person deciding needs the SIZE of the thing they would be turning on.
    assert "If you turned it on" in said
    assert "would be sent to model-for-A_fact" in said
    assert "the checks and the review sets are not wired to anything yet" in said
    assert "No part of this run can call a model yet either" not in said


def _keywords_of(call_name: str) -> dict[str, ast.expr]:
    """The keyword arguments of every call to `call_name` in `cli.py`, merged.

    Read from the source rather than from a constant, for the reason this file has
    always given: asserting a flag against itself is a tautology, and the flag is
    the thing that goes stale.
    """
    tree = ast.parse(Path(cli.__file__).read_text())
    found: dict[str, ast.expr] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        name = getattr(target, "id", None) or getattr(target, "attr", None)
        if name != call_name:
            continue
        for keyword in node.keywords:
            if keyword.arg:
                found[keyword.arg] = keyword.value
    return found


def _is_none(value: ast.expr | None) -> bool:
    return isinstance(value, ast.Constant) and value.value is None


def test_the_wired_set_agrees_with_the_injections_rather_than_with_itself():
    """The one that cannot be satisfied by editing a sentence.

    `WIRED_CALL_SITES` is a claim about which injection points in `cli.py` carry a
    model, and it is now a SET because the answer differs per site. Asserting it
    against a constant would be a tautology -- changing the constant would move the
    assertion with it, which is exactly how the length check on the wire handle key
    turned out vacuous. So this reads the arguments at each site.

    It is stricter than the boolean version it replaces: that one could be
    satisfied by ANY site being wired, so wiring `A_fact` and then announcing that
    placement questions may be sent would have passed it.
    """
    fact = _keywords_of("FactCallAuthorities")
    placement = _keywords_of("PipelineInputs")
    grouping = _keywords_of("CorpusAuthorities")

    # A -- wired. Every one of `run_call`'s four is a real expression.
    for name in ("gate", "model_client", "prompt"):
        assert name in fact and not _is_none(fact[name]), (
            f"A_fact's {name} is absent or None, so `WIRED_CALL_SITES` claims a "
            "site that cannot construct a request")
    assert cli.A_FACT in cli.WIRED_CALL_SITES

    # C and D -- NOT wired, and the announcement says so. `model_path_available`
    # reads these as a set: with them `None` a file that needs a judgement abstains.
    for name in ("gate", "model_client", "prompt", "call_dependencies"):
        assert _is_none(placement.get(name)), (
            f"placement's {name} is no longer None. If C_placement was just "
            "wired, add it to WIRED_CALL_SITES -- but only once a prompt is "
            "ratified for it too, or the announcement becomes untrue one step "
            "later.")
    assert cli.C_PLACEMENT not in cli.WIRED_CALL_SITES
    for name in ("p8_run_call", "p8_authorities"):
        assert _is_none(grouping.get(name)), f"P9's {name} is no longer None"
    assert cli.B_GROUP not in cli.WIRED_CALL_SITES
    assert cli.D_RESIDUAL not in cli.WIRED_CALL_SITES

    # And the derived flag is derived, not written beside the set.
    assert cli.MODEL_CALL_SITES_WIRED is bool(cli.WIRED_CALL_SITES)


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
