# tests/integration/test_cli_dossier_ceiling_is_measured.py
"""`104` SF-5 / R-07's second half, and `103` C7: the ceiling was asserted, never
measured, and there were two of it.

Three separate defects wore one number:

  * `cli._bootstrap` seeded EVERY `placement.config.CEILINGS` key with
    `CEILING_VALUE = 8`, and one of those keys is
    `model.max_dossier_tokens_per_call`. Every A_fact request carried
    `GROUPING_LIMITS.max_dossier_tokens = 4000`. Two answers to one question, four
    hundred times apart, and the smaller one is the one the gate reads.
  * `cli.fact_call_authorities` built the `Gate` without `measure_tokens`, which
    P7 takes with a `None` default because "P7 owns no tokenizer and inventing one
    would invent a number". With nothing measuring, `over_dossier_ceiling` never
    ran, so the ceiling above could not have denied anything even had it been
    right.
  * `model_facts._call_dependencies` passed `unreduced_fits=True` as a literal, so
    §8.6's reduction ladder answered "it fits" for every dossier ever built,
    including the 45,843-byte one `104` §5 measured on the owner's own files.

WHAT THE MEASUREMENT IS, and why it is honest. `00`:251 states the ceiling in
TOKENS. No tokenizer for the models this product talks to exists on the device --
`readers/embedding_minilm.py` carries one, and it belongs to the embedding model,
needs downloaded weights, and would answer a different question. So
`model_facts.dossier_tokens` counts CHARACTERS and is used as an UPPER BOUND on
tokens: every BPE and WordPiece token consumes at least one character, so a
payload of N characters is at most N tokens under any of them. It errs towards
refusing, never towards sending, and it does not degrade on CJK the way the
familiar `characters / 4` rule does -- which matters on this owner's corpus.
"""
from __future__ import annotations

import pytest

from database_agent.budget import get_ceiling
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation

import cli
from model_facts import dossier_tokens, measure_released_tokens

SITUATION = "academic.coursework"
_HASH = "a" * 64


def _authorities(conn):
    from production import (
        folder_levels_for, load_shipped_catalogue, read_packaged_library_file,
    )
    from readers.model_routing import FAST, LOGIC, REASONING, deepseek_routing

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    levels = folder_levels_for(catalogue, SITUATION)
    routing = deepseek_routing(
        api_key="not-a-key", base_url="https://example.invalid",
        model_id_of_tier={REASONING: "r", LOGIC: "l", FAST: "f"},
        tier_of_call_site=cli.TIER_OF_CALL_SITE,
        max_response_tokens=cli.MAX_RESPONSE_TOKENS, timeout_seconds=1.0)
    return cli.fact_call_authorities(
        conn, routing=routing, scan_run_id="scan", corpus_file_count=1,
        policy_version="policy", wire_handle_key=bytes(32), schema="academic",
        folder_levels=levels, user_id="t",
        now=lambda: "2026-09-05T00:00:00+00:00")


# --- one ceiling ------------------------------------------------------------

def test_one_ceiling_is_stored_and_it_is_the_one_the_requests_carry(conn):
    """The equality itself, which is the whole of the first defect."""
    cli._bootstrap(conn)
    assert get_ceiling(conn, "model.max_dossier_tokens_per_call") == \
        cli.GROUPING_LIMITS.max_dossier_tokens == 4000


def test_the_other_six_ceilings_are_untouched(conn):
    """The dossier ceiling is the only one that had a second answer elsewhere.

    Without this, raising one number in a loop over seven keys could raise all
    seven and nothing would say so -- `placement_limits` reads every one of them
    and refuses a non-positive value, which is not the same as noticing a change.
    """
    from placement.config import CEILINGS

    cli._bootstrap(conn)
    for name, key in CEILINGS.items():
        if name == "max_dossier_tokens":
            continue
        expected = (cli.FILES_PER_REVIEW_SCREEN
                    if name == "max_residual_files_per_batch"
                    else cli.CEILING_VALUE)
        assert get_ceiling(conn, key) == expected, name


# --- the measurement --------------------------------------------------------

def test_the_estimate_is_characters_and_is_an_upper_bound_on_tokens():
    """It counts, and it says what it counts. A tokenizer emitting more tokens than
    the payload has characters does not exist, so this can be relied on to refuse
    when the truth would refuse."""
    assert dossier_tokens(()) == 0
    assert dossier_tokens(("abc", "de")) == 5
    assert dossier_tokens(("香港身分證",)) == 5


class _Item:
    def __init__(self, value: str) -> None:
        self.value = value


def test_the_gate_binding_measures_what_would_be_released():
    """`Gate` calls `measure_tokens(request, resolved)` and `resolved` is what is
    about to leave. Reference-only items carry no value and add nothing."""
    assert measure_released_tokens(
        object(), (_Item("Homework 3"), _Item("PHYS 1401"))) == 19


def test_the_a_fact_gate_is_given_a_measurement(conn):
    """`103` C7's own sentence: with `measure_tokens=None` the ceiling cannot deny,
    however it is set."""
    cli._bootstrap(conn)
    authorities = _authorities(conn)
    assert authorities.gate._measure_tokens is not None
    assert authorities.max_dossier_tokens == \
        get_ceiling(conn, "model.max_dossier_tokens_per_call")


# --- the ladder actually reduces -------------------------------------------

def _reading(raw: str, index: int) -> Observation:
    return Observation(
        file_id="file-1", content_hash=_HASH, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=raw, occurrence_count=1, observed_at="2026-09-05T00:00:00Z",
        reliability="possible", run_id="r-1",
        location=Location("heading", (Segment("field", label=f"h{index}"),),
                          TextSpan(0, len(raw))))


def _dependencies(conn, observations):
    from facts.llm_seam import FactRequest
    from model_facts import _call_dependencies

    cli._bootstrap(conn)
    request = FactRequest(
        file_id="file-1", content_hash=_HASH, allowlist=("work_type",),
        citable_observations=tuple(observations), existing_facts=(),
        normalizers={})
    return _call_dependencies(
        request, ("work_type",), folder_levels=(),
        authorities=_authorities(conn), observations=tuple(observations))


def test_a_dossier_inside_the_ceiling_still_fits(conn):
    deps = _dependencies(conn, [_reading("Homework 3", 1)])
    assert deps.unreduced_fits is True


def test_a_dossier_over_the_ceiling_does_not_fit_and_the_ladder_defers(conn):
    """`00`:259: a prompt over its token budget "should not truncate silently in a
    way that removes the decisive evidence. Instead, the system should summarize
    deterministic facts, preserve anchor excerpts, split the task, or defer the
    decision."

    This deployment can build none of the three smaller shapes -- `_call_
    dependencies` says so in its own comment and passes `summarized_fits=False`,
    `anchors_fit=False` and no shards -- so the honest rung is the last one, and
    `plan_reduction` names it `DEFERRED` with a `PreCallAbstention` carrying
    `BUDGET_EXHAUSTED`. That is the recorded reason. It is taken BEFORE
    `reserve_call` and before `gate.release`, so a deferred call spends no budget
    and mints no release.
    """
    from llm_harness.budgets import plan_reduction
    from llm_harness.vocabulary import BUDGET_EXHAUSTED, DEFERRED

    #: 12 observations is `FACT_CALL_MAX_RELEASED_OBSERVATIONS`, so this is the
    #: largest dossier site A can build, and each reading is 600 characters.
    over = [_reading("x" * 600, index) for index in range(12)]
    deps = _dependencies(conn, over)
    assert dossier_tokens(o.raw_value for o in over) == 7200
    assert deps.unreduced_fits is False

    decision = plan_reduction(
        unreduced_fits=deps.unreduced_fits,
        summarized_fits=deps.summarized_fits,
        anchors_fit=deps.anchors_fit,
        split_shard_fits=deps.split_shard_fits,
        call_site="A_fact", subject_ref="file-1")
    assert decision.rung == DEFERRED
    assert decision.abstention is not None
    assert decision.abstention.reason == BUDGET_EXHAUSTED
    assert decision.gate_releases == 0
    assert decision.reservations == 0
    assert decision.invocations == 0


def test_the_stage_hands_the_ladder_the_observations_it_is_about_to_send():
    """The call site, pinned, for `test_the_stage_asks_open_question_about_pending
    and_not_the_whole_allowlist`'s reason: measuring the wrong list is invisible to
    every test above, because both lists are non-empty on the happy path."""
    import ast
    import inspect

    import model_facts

    tree = ast.parse(inspect.getsource(model_facts))
    stage = next(node for node in ast.walk(tree)
                 if isinstance(node, ast.FunctionDef)
                 and node.name == "fact_call_stage")
    calls = [node for node in ast.walk(stage)
             if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name)
             and node.func.id == "_call_dependencies"]
    assert len(calls) == 1
    passed = {keyword.arg: keyword.value for keyword in calls[0].keywords}
    assert "observations" in passed, (
        "the ladder must be measured against the observations the request is "
        "built from; any other list is a different dossier")
    # `104` R-135: the request is built from the file's own readings AND the
    # context readings its folder's anchors supply, so the list the ladder
    # measures is that union -- `observations + context` -- and not the file's
    # readings alone. Measuring the smaller list would be the very defect this
    # pin exists for: a dossier the ladder never weighed.
    def named(node):
        """The name a list expression is about: `x`, or `tuple(x)` / `list(x)`,
        which only change the container and never the members measured."""
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in ("tuple", "list") and len(node.args) == 1):
            node = node.args[0]
        assert isinstance(node, ast.Name), ast.dump(node)
        return node.id

    measured = passed["observations"]
    if isinstance(measured, ast.BinOp):
        assert isinstance(measured.op, ast.Add)
        assert {named(measured.left), named(measured.right)} == {
            "observations", "context"}
    else:
        assert named(measured) == "observations"


# --- the door's own backstop ------------------------------------------------

def test_the_gate_denies_a_released_dossier_over_the_stored_ceiling(conn):
    """M9's backstop, reachable at last. The ladder above refuses to BUILD an
    oversized call; this is the door refusing to let one through if it ever did,
    and it is the reason both halves are wired rather than either alone."""
    from privacy.denial import over_dossier_ceiling

    cli._bootstrap(conn)
    ceiling = get_ceiling(conn, "model.max_dossier_tokens_per_call")
    assert over_dossier_ceiling(conn, measured_tokens=ceiling) is False
    assert over_dossier_ceiling(conn, measured_tokens=ceiling + 1) is True
