"""`104` R-O: a refusal raised where a decision was expected ends one call, not the run.

Twice on a real corpus the product died with a traceback and printed no report:
`privacy.resolve.UnresolvableSpan` out of `gate.release` after thirty-seven minutes
of fact calls, and -- once that cause was fixed -- `privacy.release.MalformedRequest`
out of `ModelCallRequest.__post_init__` at the first group dossier. Both are the
same shape: a part of the product refusing to answer, raised through a seam whose
caller has no `except` for it, all the way to `main`.

`00` §8 and `104` §7 Phase 1 step 6 say what should happen instead -- the call is
recorded as refused, by reason; the subject falls back to what this device could
decide on its own; the run goes on and the report says how many calls were refused
and why. The gate's own comment agrees that these are not denials: *"this is a
request the gate cannot evaluate at all"*. It is still an outcome, and an outcome is
something a caller reads rather than something that unwinds the stack.

**The negative twin is the load-bearing half.** A `TypeError` inside the same call is
a programming error and must still surface: a catch wide enough to swallow one would
turn every future bug at this seam into a quiet "0 facts written".
"""
from __future__ import annotations

import io

import pytest

import cli
from llm_harness.authorship import CALL_REFUSED
from llm_harness.records import CallRefused, P8Verdict
from privacy.release import MalformedRequest
from privacy.resolve import UnresolvableSpan

from test_p8_walking_skeleton import (  # noqa: F401  (fixtures)
    OBSERVED_AT,
    _direct_bytes,
    _run,
    skeleton_conn,
    walk,
)


class _GateThatRaises:
    """P7's real gate, except that `release` raises instead of deciding.

    A wrapper rather than a stub: everything `run_call` reads off a gate other than
    `release` is the real object's, so the test cannot pass by accident on a seam
    that stopped calling the gate at all.
    """

    def __init__(self, inner, error: BaseException) -> None:
        self._inner = inner
        self._error = error
        self.calls = 0

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def release(self, request):
        self.calls += 1
        raise self._error


def _refused_events(conn) -> list[str]:
    return [
        row["explanation"]
        for row in conn.execute(
            "SELECT explanation FROM events WHERE event_type = ? ORDER BY event_id",
            (CALL_REFUSED,),
        )
    ]


@pytest.mark.parametrize(
    "error",
    [
        UnresolvableSpan(
            "observation 'sha256:3ea4' belongs to a file outside request.target"),
        MalformedRequest("a request with no items has nothing to release"),
    ],
    ids=["unresolvable-span", "malformed-request"],
)
def test_a_refusal_raised_at_the_gate_comes_back_as_an_outcome(walk, error):
    conn, file_id, key, digest, prompt, fingerprint, policy, request, deps = walk
    from test_p8_walking_skeleton import egress
    from llm_harness.harness import run_call
    from p8.test_p8_transport import Recorder

    gate = _GateThatRaises(egress._gate(conn), error)
    recorder = Recorder(reply=_direct_bytes(key))
    result = run_call(
        conn, request, gate=gate,
        model_client=egress.ModelClient(
            model_target=egress.CLOUD, invoke=recorder),
        prompt=prompt, validation_dependencies=deps,
        observed_at=lambda: OBSERVED_AT,
    )

    assert isinstance(result, CallRefused), result
    assert result.call_site == request.call_site
    assert result.subject_ref == request.subject_ref
    # THE TYPE AND NOTHING ELSE. `transport._client_exception_explanation` made the
    # same reduction for the same reason: §8.4 forbids a filename or a file id
    # reaching a durable record or a screen through an exception message, and the
    # message this refusal carries names both.
    assert result.refusal_class == type(error).__qualname__
    assert file_id not in result.refusal_class
    # Nothing was sent.
    assert recorder.calls == []
    # And the run has a durable record of the refusal.
    explanations = _refused_events(conn)
    assert explanations, "a refused call leaves no `call_refused` event"
    assert type(error).__qualname__ in explanations[-1]


def test_the_refused_call_does_not_take_the_budget_slot_with_it(walk):
    """The reservation is released, so the next subject can still be asked.

    `run_call` reserves before it releases, and only the gate's own terminal
    decisions gave the slot back. An `UnresolvableSpan` is in neither set today, so
    the refusal that ended the run also spent a call that never happened -- and on a
    scan budget of one, the file after it would have been refused for a reason that
    was not about it.
    """
    conn, file_id, key, digest, prompt, fingerprint, policy, request, deps = walk
    from test_p8_walking_skeleton import egress
    from llm_harness.harness import run_call
    from p8.test_p8_transport import Recorder

    refused = run_call(
        conn, request,
        gate=_GateThatRaises(egress._gate(conn), UnresolvableSpan("no reading")),
        model_client=egress.ModelClient(
            model_target=egress.CLOUD, invoke=Recorder(reply=b"{}")),
        prompt=prompt, validation_dependencies=deps,
        observed_at=lambda: OBSERVED_AT,
    )
    assert isinstance(refused, CallRefused)

    # The same budget, the same scan: one call is all it allows.
    verdict, recorder = _run(
        conn, request, deps, prompt=prompt, reply=_direct_bytes(key),
    )
    assert isinstance(verdict, P8Verdict), verdict
    assert len(recorder.calls) == 1


def test_a_programming_error_at_the_same_seam_still_surfaces(walk):
    conn, file_id, key, digest, prompt, fingerprint, policy, request, deps = walk
    from test_p8_walking_skeleton import egress
    from llm_harness.harness import run_call
    from p8.test_p8_transport import Recorder

    with pytest.raises(TypeError):
        run_call(
            conn, request,
            gate=_GateThatRaises(
                egress._gate(conn), TypeError("'Dossier' object is not subscriptable")),
            model_client=egress.ModelClient(
                model_target=egress.CLOUD, invoke=Recorder(reply=b"{}")),
            prompt=prompt, validation_dependencies=deps,
            observed_at=lambda: OBSERVED_AT,
        )


def test_the_report_counts_a_refused_call_and_says_why():
    """The person's screen. `_print_fact_pass` already names four outcomes by their
    own reason; a refusal was the fifth and had no line, because it never returned."""
    out = io.StringIO()
    cli._print_fact_pass(
        written=3, withheld={}, files=5,
        outcomes=[
            ("file-1", CallRefused(
                call_site="A_fact", subject_ref="file-1",
                refusal_class="UnresolvableSpan")),
            ("file-2", CallRefused(
                call_site="A_fact", subject_ref="file-2",
                refusal_class="UnresolvableSpan")),
        ],
        model_id="qwen3:8b", out=out)
    printed = out.getvalue()
    assert "2 refused" in printed
    assert "UnresolvableSpan" in printed


# --- the run itself, end to end ------------------------------------------------


def test_a_refusal_in_the_fact_pass_still_prints_the_report(tmp_path, monkeypatch):
    """The defect as the person met it: a traceback where the report should be.

    Driven through `cli.main` over the local-model harness, with the one seam that
    raised on the owner's corpus made to raise here: `build_fact_request`
    constructs the `ModelCallRequest`, which is where `MalformedRequest` came from,
    and it builds the spans the gate then resolves, which is where
    `UnresolvableSpan` came from. Neither is reachable from `run_call`'s own `try`,
    because the expression that raises is an ARGUMENT to it.

    The assertion is not that the refusal is silent. It is that the run reaches its
    end, the person sees the plan the deterministic half already earned, and the
    screen says how many calls were refused and what refused them.
    """
    import model_facts
    from test_local_model_fact_pass import (
        LOCAL_BASE_URL_NAME,
        LOCAL_MODEL_NAME,
        MODEL_ID,
        StubOllama,
        _corpus,
        _run,
    )

    real_build = model_facts.build_fact_request
    refused_for: list[str] = []

    def _refuse_the_first_file(request, observations, **kwargs):
        if not refused_for:
            refused_for.append(request.file_id)
            raise UnresolvableSpan(
                f"observation 'sha256:3ea4' belongs to file {request.file_id!r}, "
                f"outside request.target.file_ids")
        return real_build(request, observations, **kwargs)

    monkeypatch.setattr(model_facts, "build_fact_request", _refuse_the_first_file)
    with StubOllama() as stub:
        monkeypatch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
        monkeypatch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
        corpus = _corpus(tmp_path)
        database = tmp_path / "holder" / "plan.sqlite"
        code, report = _run(corpus, database)

    assert refused_for, "the seam under test never ran"
    assert code == 0, report
    # The report the run had already earned.
    assert "Files:" in report
    assert "Facts from a model:" in report
    # Said, not swallowed.
    assert "refused" in report and "UnresolvableSpan" in report, report
    # And the files after the refused one were still asked about.
    assert len(stub.requests) >= 1
