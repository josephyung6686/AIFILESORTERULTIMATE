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
    """Each of the other six is seeded from the one place that answers it.

    Without this, raising one number in a loop over seven keys could raise all
    seven and nothing would say so -- `placement_limits` reads every one of them
    and refuses a non-positive value, which is not the same as noticing a change.

    `104` R-145: the two SPEND ceilings had the same second answer the dossier
    ceiling had. P11 replaces the observe purse's rate and cost ceiling with the
    stored numbers before every site-C call, and the stored numbers were
    `CEILING_VALUE`, so the purse `cli.observe_scan_budget` sized at one call per
    file was cut to ONE call on 199 files. They are seeded from the purse's own
    constants now, and the three neighbourhood ceilings keep `CEILING_VALUE`.
    """
    from placement.config import CEILINGS

    cli._bootstrap(conn)
    seeded_from = {
        "max_residual_files_per_batch": cli.FILES_PER_REVIEW_SCREEN,
        "max_llm_calls_per_thousand_files": cli.OBSERVE_CALLS_PER_1000_FILES,
        "max_cost_per_scan": int(cli.OBSERVE_CALLS_PER_SCAN_CEILING),
    }
    for name, key in CEILINGS.items():
        if name == "max_dossier_tokens":
            continue
        assert get_ceiling(conn, key) == seeded_from.get(name, cli.CEILING_VALUE), name


def test_p11s_override_leaves_the_observe_purse_one_call_per_file(conn):
    """`104` R-145's site-C half, measured the way r12's ledger showed it.

    `placement.pipeline._judge_with_model` rebuilds the scan budget with the two
    stored spend ceilings -- "a caller must not raise its own ceiling by echoing a
    larger one" -- so the purse site C actually reserves from is `observe_scan_
    budget`'s purse under P11's numbers. On r12 that was `max(floor(199 * 8 /
    1000), 1) == 1`, site B had settled the one call, and 60 files were refused
    at site C with `calls_reserved=1` on the ledger. The two numbers are one now,
    and the override changes nothing about how many calls a corpus is allowed.
    """
    from dataclasses import replace
    from decimal import Decimal

    from llm_harness.budgets import ScanBudget, allowed_calls
    from placement.config import placement_limits

    cli._bootstrap(conn)
    limits = placement_limits(conn)
    fact_purse = ScanBudget(
        scan_id="scan-r145", corpus_file_count=102,
        max_calls_per_1000_files=cli.FACT_CALLS_PER_1000_FILES,
        max_estimated_cost=cli.FACT_CALLS_PER_SCAN_CEILING,
        min_calls_per_scan=cli.FACT_MIN_CALLS_PER_SCAN)
    purse = cli.observe_scan_budget(fact_purse, corpus_file_count=199)
    as_p11_reserves = replace(
        purse,
        max_calls_per_1000_files=limits.max_llm_calls_per_thousand_files,
        max_estimated_cost=Decimal(limits.max_cost_per_scan))
    assert allowed_calls(purse) == 199
    assert allowed_calls(as_p11_reserves) == allowed_calls(purse)
    assert as_p11_reserves.max_estimated_cost == purse.max_estimated_cost


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


def _dependencies(conn, observations, anchors=None, name_characters=0,
                  unreduced=None):
    from facts.llm_seam import FactRequest
    from model_facts import _call_dependencies

    cli._bootstrap(conn)
    request = FactRequest(
        file_id="file-1", content_hash=_HASH, allowlist=("work_type",),
        citable_observations=tuple(observations), existing_facts=(),
        normalizers={})
    # `104` R-159: `name_characters` defaults to 0 HERE and nowhere in the product.
    # A call that offers no `Filename` item releases no name, and every test above
    # this line predates the third term and is about the other two.
    #
    # `104` §18.2 gap 5: `unreduced` defaults to `None`, which is the spelling for a
    # caller that never filled -- there the built list IS the whole offer and the two
    # questions have one answer, so every test above this line keeps the meaning it
    # was written with.
    return _call_dependencies(
        request, ("work_type",), folder_levels=(),
        authorities=_authorities(conn), observations=tuple(observations),
        name_characters=name_characters,
        anchor_observations=None if anchors is None else tuple(anchors),
        unreduced_observations=None if unreduced is None else tuple(unreduced))


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


def test_a_context_line_over_the_ceiling_yields_to_the_preserved_anchors_rung(conn):
    """`104` R-145's site-A half. `00`:257's second remedy, "preserve anchor
    excerpts", is a shape this deployment CAN build since R-135: the context a
    neighbour supplies has a line reading and the code's own span, and the span
    is the excerpt.

    Measured on r12: one neighbour's "line" -- a newline-delimited segment of
    extracted text -- was 27,510 characters, and all 17 files in its folder
    family were deferred at site A, each recorded `BUDGET_EXHAUSTED` with no
    reservation made. The file's own readings here are 10 characters; nothing
    about the FILE is over any ceiling.
    """
    from llm_harness.budgets import plan_reduction
    from llm_harness.vocabulary import PRESERVED_ANCHORS

    own = [_reading("Homework 3", 1)]
    paragraph = [_reading("x" * 5000, 2)]
    code = [_reading("W3134", 3)]
    deps = _dependencies(conn, own + paragraph, anchors=own + code)
    assert deps.unreduced_fits is False
    assert deps.anchors_fit is True

    decision = plan_reduction(
        unreduced_fits=deps.unreduced_fits,
        summarized_fits=deps.summarized_fits,
        anchors_fit=deps.anchors_fit,
        split_shard_fits=deps.split_shard_fits,
        call_site="A_fact", subject_ref="file-1")
    assert decision.rung == PRESERVED_ANCHORS
    assert decision.abstention is None


def test_without_a_second_shape_the_ladder_is_what_it_was(conn):
    """A deployment that offers no excerpt shape keeps the rung honestly absent:
    `anchors_fit` is `False`, not a measurement of the wrong list."""
    own = [_reading("Homework 3", 1)]
    paragraph = [_reading("x" * 5000, 2)]
    deps = _dependencies(conn, own + paragraph)
    assert deps.unreduced_fits is False
    assert deps.anchors_fit is False


# --- `104` §18.2 gap 5: the cut is measured, and it refuses nothing --------

def test_a_trimmed_offer_is_not_unreduced_and_the_ladder_says_so(conn):
    """`104` §18.2 gap 5: "unreduced fits" was measured over the ALREADY-TRIMMED set.

    `model_facts.within_dossier_budget` drops the readings that do not fit and hands
    back the ones that do; `_call_dependencies` then asked whether THOSE fit, which
    is "does what fits fit" and could only ever answer yes. So every dossier this
    product has ever built recorded `reduction_rung = none`, including the ones that
    reached a model carrying a handful of a spreadsheet's readings, and §8.6's ladder
    was a decoration over a measurement that could not fail. The rung on the record
    was the one thing telling a person a reduction had happened, and it said none.

    Measured here as the stage measures it: forty readings offered, the ceiling
    admits some, and the first rung is asked about the OFFER rather than about the
    fill's output.

    SABOTAGE: pass `unreduced_observations=None` (which restores the old spelling --
    the first rung measured over `observations`) and `unreduced_fits` goes back to
    `True` beside a fill that dropped thirty-odd readings. Every other assertion in
    this file still passes, which is exactly why the defect survived R-159 and R-174.
    """
    from model_facts import within_dossier_budget

    offer = [_reading("y" * 300, index) for index in range(40)]
    fill = within_dossier_budget(offer, ceiling=cli.GROUPING_LIMITS.max_dossier_tokens)
    assert fill.dropped, "this fixture is only about a ceiling that actually cuts"

    deps = _dependencies(conn, fill.taken, unreduced=offer)
    assert deps.unreduced_fits is False
    # And the OLD spelling, side by side, so the claim is about the difference: the
    # built list fits, which is what the first rung used to be asked and is the
    # tautology the gap names.
    assert _dependencies(conn, fill.taken).unreduced_fits is True


def test_a_trimmed_offer_still_goes_out_at_the_preserved_anchors_rung(conn):
    """The owner's word on 9 Sep 2026: "files should not be refused; make sure all
    necessary information is processed and used."

    Making the first rung honest moves the ladder down one, and the rung below it
    must therefore be TRUE or the honest measurement would turn into a refusal --
    `plan_reduction`'s last rung is `DEFERRED`, a `PreCallAbstention` that sends
    nothing. `00`:257's second remedy is "preserve anchor excerpts", and preserving
    the readings that fit while dropping the rest is that remedy applied to the
    file's own evidence, so `PRESERVED_ANCHORS` is the rung the built shape earns.

    The call goes out. What changed is that the record now says a reduction happened.

    SABOTAGE: drop the `built_fits or` from `anchors_fit` in `_call_dependencies` and
    this rung becomes `DEFERRED` -- the file is refused for the sake of an honest
    number, which is the one outcome the owner's ruling forbids.
    """
    from llm_harness.budgets import plan_reduction
    from llm_harness.vocabulary import PRESERVED_ANCHORS
    from model_facts import within_dossier_budget

    offer = [_reading("y" * 300, index) for index in range(40)]
    fill = within_dossier_budget(offer, ceiling=cli.GROUPING_LIMITS.max_dossier_tokens)
    deps = _dependencies(conn, fill.taken, unreduced=offer)

    decision = plan_reduction(
        unreduced_fits=deps.unreduced_fits,
        summarized_fits=deps.summarized_fits,
        anchors_fit=deps.anchors_fit,
        split_shard_fits=deps.split_shard_fits,
        call_site="A_fact", subject_ref="file-1")
    assert decision.rung == PRESERVED_ANCHORS
    assert decision.abstention is None, (
        "a cut that is merely RECORDED must not become a cut that is refused")


def test_the_deferred_rung_is_reached_by_exactly_the_state_it_always_was(conn):
    """The safety half of gap 5, asserted as the boundary rather than as a rung.

    DEFERRED sends nothing, so the question the patch has to answer is not "is the
    rung honest" but "does any file reach DEFERRED that did not before". It does not.
    The fill's own ceiling is the dossier ceiling less the context and the name, so
    the built shape fits by construction whenever that remainder is not negative --
    which leaves one state where it does not fit: the context and the filename alone
    exceed the ceiling, so nothing of the file's own can travel. That is the state
    that reached DEFERRED before this patch, for the same arithmetic.

    Both halves are asserted here: the context-heavy file with no second shape still
    defers, and it defers whether the first rung is measured the old way or the new,
    which is what "the deferred set is unchanged" means.
    """
    from llm_harness.budgets import plan_reduction
    from llm_harness.vocabulary import BUDGET_EXHAUSTED, DEFERRED

    # A context reading alone over the ceiling, and no fill behind it: this is the
    # remainder-of-zero state, and no reading of the file's own is in the built list.
    paragraph = [_reading("x" * 5000, 1)]

    def rung(**extra):
        deps = _dependencies(conn, paragraph, **extra)
        return plan_reduction(
            unreduced_fits=deps.unreduced_fits,
            summarized_fits=deps.summarized_fits,
            anchors_fit=deps.anchors_fit,
            split_shard_fits=deps.split_shard_fits,
            call_site="A_fact", subject_ref="file-1")

    old_spelling = rung()
    new_spelling = rung(unreduced=paragraph)
    assert old_spelling.rung == new_spelling.rung == DEFERRED
    assert new_spelling.abstention.reason == BUDGET_EXHAUSTED


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

    # `104` R-159 renamed the left half. The stage now fills the file's own
    # readings TWICE -- once into the room the anchor LINES leave and once into the
    # room the preserved-anchor EXCERPTS leave -- because the two shapes leave
    # different remainders, so the lines rung is measured over `lines_readings` and
    # the anchors rung over `own_excerpts`. Passing the chosen shape's fill to both
    # would report a total for a dossier that was never built, which is the same
    # class of defect this pin exists for.
    measured = passed["observations"]
    if isinstance(measured, ast.BinOp):
        assert isinstance(measured.op, ast.Add)
        assert {named(measured.left), named(measured.right)} == {
            "lines_readings", "context"}
    else:
        assert named(measured) == "lines_readings"

    # `104` R-159's third term, pinned at the same call site and for the same
    # reason: the gate's `measure_released_tokens` counts the resolved filename
    # like any other released value, so a ladder that omitted it would pass a
    # dossier the door then denies `over_dossier_ceiling` -- after the budget slot
    # is reserved, which costs the file its call.
    assert "name_characters" in passed, (
        "the ladder must be measured against every value the door will count, and "
        "the filename is one of them since `104` R-06 put it in `NAME_BEARING`")
    assert named(passed["name_characters"]) == "name_characters"

    anchors = passed["anchor_observations"]
    assert isinstance(anchors, ast.IfExp), ast.dump(anchors)
    assert {named(anchors.orelse.left), named(anchors.orelse.right)} == {
        "own_excerpts", "excerpts"}, (
        "the preserved-anchors rung is measured over the fill THAT shape leaves")

    # `104` §18.2 gap 5's fourth term, pinned at the same call site and for this
    # file's own reason: measuring the wrong list is invisible to every assertion
    # about a rung, because a first rung asked about the trimmed set is never FALSE
    # and so never disagrees with anything. `offered` is what
    # `ordered_releasable_observations` returned before the fill spent the ceiling on
    # it; passing `lines_readings` here would restore the tautology with a new
    # keyword's name on it.
    assert "unreduced_observations" in passed, (
        "the first rung means UNREDUCED, which is a question about the offer and "
        "not about what survived the fill")
    unreduced = passed["unreduced_observations"]
    assert isinstance(unreduced, ast.BinOp) and isinstance(unreduced.op, ast.Add)
    assert {named(unreduced.left), named(unreduced.right)} == {"offered", "context"}


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
