import pytest

from database_agent.budget import CEILING_KEYS, all_ceilings, get_ceiling, set_ceiling
from database_agent.db import create_schema


def test_there_are_exactly_seventeen_keys():
    # §8.6's twelve, three of them namespaced across two owners (O10) = fifteen,
    # plus `evidence.context_window` ratified 2026-08-20, plus `tree.max_depth`
    # 2026-08-29 -- the second of the two numbers `00`:256 names on one line.
    assert len(CEILING_KEYS) == 17
    assert len(set(CEILING_KEYS)) == 17


def test_grouping_and_placement_resolve_independently(conn):
    # O10: two parts legitimately hold three ceilings on different graphs.
    create_schema(conn)
    set_ceiling(conn, "grouping.max_retrieved_neighbors", 25)
    set_ceiling(conn, "placement.max_retrieved_neighbors", 8)
    assert get_ceiling(conn, "grouping.max_retrieved_neighbors") == 25
    assert get_ceiling(conn, "placement.max_retrieved_neighbors") == 8


def test_all_seventeen_keys_are_readable(conn):
    create_schema(conn)
    for key in CEILING_KEYS:
        set_ceiling(conn, key, 1)
    assert set(all_ceilings(conn)) == set(CEILING_KEYS)


def test_p1_enforces_nothing(conn):
    # §8.6, G4: P1 holds and publishes values; enforcement belongs elsewhere.
    create_schema(conn)
    set_ceiling(conn, "ocr.max_pages_per_file", 1)
    # Reading a ceiling is not enforcing it — no operation is refused.
    assert get_ceiling(conn, "ocr.max_pages_per_file") == 1


def test_unknown_key_is_rejected(conn):
    create_schema(conn)
    with pytest.raises(KeyError):
        set_ceiling(conn, "made.up_ceiling", 5)


def test_the_sixteenth_key_is_the_evidence_context_window(conn):
    """B4, ratified 2026-08-20. §2.8 requires surrounding context be stored and §8.6
    forbids silent truncation, but none of §8.6's twelve ceilings — and none of the
    fifteen keys — was a context length, so the budget had no configuration surface
    to live on. P4 held `context_before`/`context_after` as caller-supplied and no
    number, which was honest and left the ceiling homeless."""
    from database_agent.budget import CEILING_KEYS, get_ceiling, set_ceiling
    assert "evidence.context_window" in CEILING_KEYS
    assert len(CEILING_KEYS) == 17
    set_ceiling(conn, "evidence.context_window", 400)
    assert get_ceiling(conn, "evidence.context_window") == 400


def test_the_seventeenth_key_is_the_tree_depth_ceiling(conn):
    """2026-08-29. `00`:256 reads "Maximum folder proposals and maximum depth" --
    two numbers on one line, where every other line in that list is one. P1
    published one key for both and P10 read the single value four times, two of
    them wanting opposite values: `00`:78's own recommended tree is five levels
    deep and a picker offering five options per branch is not a picker.

    Splitting publishes what §8.6 already names. It adds no ceiling the design
    does not state, which is the only reason it is not a contract act."""
    assert "tree.max_folder_proposals" in CEILING_KEYS
    assert "tree.max_depth" in CEILING_KEYS
    assert "tree.max_folder_proposals_and_depth" not in CEILING_KEYS
    set_ceiling(conn, "tree.max_folder_proposals", 4)
    set_ceiling(conn, "tree.max_depth", 5)
    assert get_ceiling(conn, "tree.max_folder_proposals") == 4
    assert get_ceiling(conn, "tree.max_depth") == 5


def test_an_eighteenth_key_is_still_rejected(conn):
    """The key set stays closed: adding one is a contract act, not a call."""
    from database_agent.budget import set_ceiling
    with pytest.raises(KeyError):
        set_ceiling(conn, "evidence.context_window_v2", 1)


# ======================================================================================
# `104` R-35 -- the predicate over the ledger, and the sentence it earns
#
# R-35 names three `lambda: False` budget predicates. TWO OF THEM STAY, and are argued
# in the code beside them rather than here: `cli._resolver` wires `"llm": None` and
# `FactResolver` skips a `None` stage BEFORE the ceiling check, so its predicate cannot
# be reached at all; `scan_agent.traversal.walk` states in its own docstring that §8.6
# names no ceiling for traversal or hashing (SPEC Q15 open), so a real predicate there
# would be P3 enforcing a ceiling nobody published.
#
# The third -- the model pass -- is the one that could exhaust and never did. These
# pins drive the ledger through `reserve_call` ITSELF rather than writing the counters
# by hand, because the claim being pinned is agreement: the predicate must say
# "exhausted" exactly when the reserve is about to refuse. Hand-written counters would
# let both drift together and still pass.
# ======================================================================================

import sys
from decimal import Decimal
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402
from facts.budgets import (  # noqa: E402
    P6_CEILING_KEYS, UnknownCeiling, exhausted_ceilings,
)
from llm_harness.budgets import (  # noqa: E402
    BudgetExhausted, ScanBudget, allowed_calls, create_budget_schema, reserve_call,
)

#: One call's estimated cost, as the fact site injects it. Not a number chosen here:
#: `cli.FACT_CALL_COST` is what `fact_call_authorities` hands the harness and what
#: `reserve_call` actually spends, so a test that invented its own would be pinning
#: agreement between two things neither of which the product runs.
ONE_CALL = cli.FACT_CALL_COST


def _purse(conn, *, calls_per_1000: int, cost: Decimal, files: int = 1000):
    """A scan budget and the tables its ledger lives in."""
    create_budget_schema(conn)
    return ScanBudget(
        scan_id="scan:facts", corpus_file_count=files,
        max_calls_per_1000_files=calls_per_1000,
        max_estimated_cost=cost, min_calls_per_scan=0)


def test_a_scan_that_has_spent_nothing_is_not_exhausted(conn):
    """The reserve's INSERT arm, read from the other side.

    A scan with no ledger row has reserved nothing, which is not an error and not
    an exhaustion -- and reading `None` as "exhausted" would defer every first call
    of every run.
    """
    budget = _purse(conn, calls_per_1000=2, cost=Decimal("10"))
    exhausted = cli.budget_exhausted_for(conn, budget=budget, estimated_cost=ONE_CALL)
    assert exhausted_ceilings(budget_exhausted=exhausted) == ()


def test_the_call_arm_fires_exactly_when_the_reserve_would_refuse(conn):
    """Spend the allowance through `reserve_call`, then ask both.

    This is the whole of R-35's first half: the predicate and the refusal are two
    readings of one row, so the step that makes one true must make the other true.
    """
    budget = _purse(conn, calls_per_1000=2, cost=Decimal("1000"))
    allowed = allowed_calls(budget)
    exhausted = cli.budget_exhausted_for(conn, budget=budget, estimated_cost=ONE_CALL)

    for _ in range(allowed):
        # Not exhausted while a call remains: asked BEFORE the reservation that
        # uses it up, which is the order the resolver asks in.
        assert not exhausted(P6_CEILING_KEYS[0])
        reserve_call(conn, budget, estimated_cost=ONE_CALL)

    assert exhausted(P6_CEILING_KEYS[0])
    # And the refusal the predicate anticipated is the refusal that arrives.
    with pytest.raises(BudgetExhausted):
        reserve_call(conn, budget, estimated_cost=ONE_CALL)


def test_the_cost_arm_fires_on_the_estimate_the_next_call_would_add(conn):
    """`model.max_cost_per_scan`, with calls to spare.

    Exhausted means the NEXT call cannot be paid for, not that the last one could
    not be, so the arm adds this site's own `estimated_cost` before comparing --
    the same addition `_RESERVE_COUNTER_SQL` makes in its `WHERE`.
    """
    budget = _purse(conn, calls_per_1000=1000, cost=ONE_CALL)
    exhausted = cli.budget_exhausted_for(conn, budget=budget, estimated_cost=ONE_CALL)
    assert not exhausted(P6_CEILING_KEYS[1])

    reserve_call(conn, budget, estimated_cost=ONE_CALL)

    assert exhausted(P6_CEILING_KEYS[1])
    # The call arm is untouched: a thousand per thousand files leaves plenty.
    assert not exhausted(P6_CEILING_KEYS[0])
    assert exhausted_ceilings(budget_exhausted=exhausted) == (P6_CEILING_KEYS[1],)


def test_the_per_call_dossier_ceiling_is_never_a_scan_wide_exhaustion(conn):
    """`model.max_dossier_tokens_per_call` bounds ONE call and no scan spends it down.

    §8.6's ladder refuses an over-ceiling dossier per call, with its own reason, in
    `model_facts.fact_call_stage`. Reporting it here would tell a person that
    waiting or raising a budget frees work that no budget was holding.
    """
    budget = _purse(conn, calls_per_1000=0, cost=Decimal("0"))
    exhausted = cli.budget_exhausted_for(conn, budget=budget, estimated_cost=ONE_CALL)
    # Both spend arms are exhausted on this purse; the third still answers False.
    assert exhausted(P6_CEILING_KEYS[0])
    assert exhausted(P6_CEILING_KEYS[1])
    assert not exhausted(P6_CEILING_KEYS[2])


def test_a_ceiling_p8_keeps_no_counter_for_raises_rather_than_answering(conn):
    """A fourth key means a contract moved, and `False` would record it as "fine"."""
    budget = _purse(conn, calls_per_1000=2, cost=Decimal("10"))
    exhausted = cli.budget_exhausted_for(conn, budget=budget, estimated_cost=ONE_CALL)
    with pytest.raises(UnknownCeiling):
        exhausted("ocr.max_time_per_scan")


def _fact_pass_block(**kwargs) -> str:
    out = StringIO()
    cli._print_fact_pass(
        written=0, withheld={}, files=4, outcomes=(), model_id="a-model",
        out=out, **kwargs)
    return out.getvalue()


def test_the_deferral_sentence_names_the_ceiling_that_stopped_the_work():
    """`104` R-35's second half. The bucket was counted and never said out loud.

    §00, verbatim: "If the budget is exhausted, the product should retain extracted
    evidence, mark the deferred stage, and leave the file or group in review rather
    than guessing." The sentence is where a person is told that happened.
    """
    block = _fact_pass_block(deferred={P6_CEILING_KEYS[0]: 3})
    assert "3 of 4 files were deferred" in block
    assert P6_CEILING_KEYS[0] in block
    # The promise, not just the count.
    assert "budget_deferred" in block
    assert "review" in block


def test_two_ceilings_that_both_fired_are_both_named_in_published_order():
    """`exhausted_ceilings` never short-circuits, for §8.6's own reason, so two
    ceilings can defer one file and the screen must not blame whichever sorts
    first. Printed in `P6_CEILING_KEYS`' order rather than the mapping's, so two
    runs of one corpus read the same way."""
    block = _fact_pass_block(
        deferred={P6_CEILING_KEYS[1]: 1, P6_CEILING_KEYS[0]: 1})
    assert block.index(P6_CEILING_KEYS[0]) < block.index(P6_CEILING_KEYS[1])


def test_a_pass_that_deferred_nothing_prints_no_deferral_line():
    """Behaviour unchanged where nothing was stopped. "0 files were deferred
    against a limit you may not have set" is a statistics line nobody asked for,
    and this block exists to say what happened."""
    assert "deferred" not in _fact_pass_block(deferred={})
    # And the default is the same as saying nothing: the argument is optional so
    # that no caller is forced to pass an empty mapping to keep its old screen.
    assert "deferred" not in _fact_pass_block()


def test_no_deferral_sentence_quotes_a_ceiling_VALUE():
    """The sentence says WHICH ceiling and never WHAT it is set to.

    Two reasons, and the second is R-35's own. (1) `00`:243 calls these
    configurable and states no number, so two of P5's are unset and a sentence
    quoting one would be quoting nothing -- which is what `_DEFERRED_BY_SOURCE_TYPE`
    already decided for the per-scan OCR and image ceilings. (2) For P6's, the purse
    a fact call spends from is the injected `ScanBudget` while P1 stores its own
    value for the same key, and `104` R-145 is what printing one of two answers to
    one ceiling already cost. A person who set a budget knows what they set.
    """
    for sentence in cli.DEFERRED_CEILING_SENTENCE.values():
        assert not any(character.isdigit() for character in sentence), sentence
    for sentence in cli._DEFERRED_BY_SOURCE_TYPE.values():
        assert not any(character.isdigit() for character in sentence), sentence


def test_the_bootstrap_sets_gap_22s_two_per_scan_ceilings(tmp_path):
    """`104` §18.2 gap 22's remaining half: the two VALUES.

    Gap 22 built the enforcement -- `orchestrator.run_p1_p7` keeps a whole-scan OCR
    clock and an image-operation count, and a file arriving past either is recorded
    `deferred` rather than read short -- and `_no_extractor_cause` already has the
    sentence for a person. What is missing is the only part no agent may supply:
    `00`:243 states no number for either, so both stay `None`, both scans stay
    unbounded, and the run behaves exactly as every run this product has made.

    Asserted in the direction that XPASSES the day the owner chooses them, which is
    the only event that should turn this marker off.
    """
    conn = cli.open_database(tmp_path / "agent.sqlite")
    try:
        cli._bootstrap(conn)
        unset = sorted(key for key in
                       ("ocr.max_time_per_scan", "image.max_analysis_ops_per_scan")
                       if get_ceiling(conn, key) is None)
        assert not unset, (
            f"{unset} carry no value, so nothing bounds a whole scan's OCR time or "
            f"its image operations. The values are the owner's: `00`:243 names the "
            f"ceilings and states no number, and one invented here would read as a "
            f"bound somebody chose.")
    finally:
        conn.close()


test_the_bootstrap_sets_gap_22s_two_per_scan_ceilings = pytest.mark.xfail(
    strict=True,
    reason="`104` §18.2 gap 22's two VALUES are the owner's. The enforcement and "
           "the person's sentence are both built; `_bootstrap` deliberately sets "
           "neither number, so both scans are unbounded. XPASSes -- and fails the "
           "suite, forcing this marker off -- the day the owner chooses them.",
)(test_the_bootstrap_sets_gap_22s_two_per_scan_ceilings)


def test_a_spent_purse_bars_the_llm_stage_and_names_the_ceiling(conn, tmp_path):
    """`104` R-35 END TO END: the predicate, the resolver, and the tuple the screen
    iterates.

    The two pins above prove the predicate agrees with `reserve_call`, and the
    printer pins prove a mapping handed to `_print_fact_pass` becomes a sentence.
    This is the seam between them, and it had never fired: while
    `budget_exhausted` was `lambda ceiling: False` no resolve on any run could reach
    `BUDGET_BAR`, so `deferred_against` was an empty tuple everywhere and the loop
    in `_model_fact_pass` that reads it had nothing to read.

    `model_route_permitted` is True on purpose. §8.4 is asked FIRST and a file that
    may never reach a model is barred `privacy`, not `budget` -- "reporting it as a
    deferral would promise work that will never be done" -- so a test that left the
    route shut would pass on the wrong bar.
    """
    from facts.budgets import LLM_ROUTE
    from facts.resolver import BUDGET_BAR, FactResolver
    from facts.fields import create_fields
    from facts.schema import create_facts_schema

    create_facts_schema(conn)
    # The catalogue, because `_write_bars` writes one `unresolved` row per pending
    # field and §3.12 forbids inventing a field to write it against.
    create_fields(conn)
    budget = _purse(conn, calls_per_1000=0, cost=Decimal("1000"))

    def _never_called(*args, **kwargs):
        raise AssertionError(
            "the llm stage ran on a scan whose purse was already spent")

    resolver = FactResolver(
        stages={"direct": None, "rule": None, "llm": _never_called},
        pending_fields=lambda db, file_id, content_hash: ("work_type",),
        budget_exhausted=cli.budget_exhausted_for(
            conn, budget=budget, estimated_cost=ONE_CALL),
        model_route_permitted=lambda file_id: True,
        record_pass=lambda db, file_id, content_hash: None,
        cache_key_for=lambda file_id, content_hash: f"test:{content_hash}",
        screen_metadata=lambda db, file_id, content_hash: ())

    result = resolver.resolve(conn, file_id="file-1", content_hash="b" * 64)

    assert result.stages_barred[LLM_ROUTE] == BUDGET_BAR
    # The exact tuple `_model_fact_pass` iterates to tally `deferred_by_ceiling`.
    assert result.deferred_against == (P6_CEILING_KEYS[0],)
