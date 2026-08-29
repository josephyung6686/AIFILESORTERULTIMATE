# tests/p6/test_p6_budgets.py
"""§8.6 — the three ceilings, the degradation order, and what a ceiling may not do.

The rule under test is one sentence of §00: "Cost exhaustion must never turn into
lower-quality automatic classification." Its P6 form is that a ceiling SUBTRACTS the
LLM route and substitutes nothing for it, and that the subtraction is a row.

Fixture note: preamble §3.6 owns `p6_conn` (P1's schema, P4's tables, and Task 2's
catalogue rows). This file takes it rather than building a second one — the task
body's own `p6` fixture never called `create_schema`, so `set_ceiling` had no table.
"""
from __future__ import annotations

import inspect
from collections.abc import Mapping

import pytest

from database_agent.budget import CEILING_KEYS, set_ceiling

import facts.budgets as budgets_module
import facts.resolver as resolver_module
from evidence_shape.canonical import canonical_json
from facts.budgets import (
    CEILING_GATED_STAGES, DEGRADATION_ORDER, P6_CEILING_KEYS, UnknownCeiling,
    ceiling_values, deferred_counts, exhausted_ceilings,
)
from facts.resolver import REASON_BY_BAR, FactResolver, ResolveResult, StageSetInvalid
from facts.unresolved import (
    ATTEMPTED_PRODUCERS, BUDGET_DEFERRED, NOT_ABSTENTIONS, NO_CANDIDATE_EVIDENCE,
    PRIVACY_WITHHELD, unresolved_for_file, write_unresolved,
)

#: §3.8's role field, ratified into the catalogue by round 1's F-1 and required to
#: exist by Done-means 13 and 22. Used here only as a field key that is certain to be
#: in the catalogue, so `write_unresolved` has something legal to name.
FIELD = "authored_by"

FILE_ID = "file-01"
CONTENT_HASH = "042896dc1966b8a6214e5383aba5b8b931cfa049d17aafa37eb8a77c859b95da"
CACHE_KEY = "sha256:0000000000000000000000000000000000000000000000000000000000000001"


class Recorder:
    """A producer, recorded. The call ORDER is the thing under test, so the stages
    write their own names into one shared list rather than being asked afterwards."""

    def __init__(self) -> None:
        self.calls: list[str] = []
        self.passes: list[tuple[str, str]] = []

    def stage(self, name: str, *, produces: tuple[str, ...] = ()):
        def run(conn, file_id: str, content_hash: str) -> tuple[str, ...]:
            self.calls.append(name)
            return produces
        return run

    def record_pass(self, conn, file_id: str, content_hash: str) -> None:
        self.passes.append((file_id, content_hash))


def a_resolver(recorder: Recorder, *, llm=None, permitted=True, exhausted=(),
               pending=(FIELD,)) -> FactResolver:
    return FactResolver(
        stages={
            "direct": recorder.stage("direct", produces=("fact-direct",)),
            "rule": recorder.stage("rule"),
            "llm": llm,
        },
        pending_fields=lambda conn, file_id, content_hash: tuple(pending),
        budget_exhausted=lambda key: key in exhausted,
        model_route_permitted=lambda file_id: permitted,
        record_pass=recorder.record_pass,
        cache_key_for=lambda file_id, content_hash: CACHE_KEY,
        screen_metadata=lambda conn, file_id, content_hash: (),
    )


def resolve(resolver: FactResolver, conn) -> ResolveResult:
    return resolver.resolve(conn, file_id=FILE_ID, content_hash=CONTENT_HASH)


def a_barren_resolver() -> FactResolver:
    """Every stage returns no fact and writes no row — the only shape that reaches
    `_outcome_for`'s final branch."""
    def nothing(conn, file_id: str, content_hash: str) -> tuple[str, ...]:
        return ()
    return FactResolver(
        stages={"direct": nothing, "rule": nothing, "llm": nothing},
        pending_fields=lambda conn, file_id, content_hash: (),
        budget_exhausted=lambda key: False,
        model_route_permitted=lambda file_id: True,
        record_pass=lambda conn, file_id, content_hash: None,
        cache_key_for=lambda file_id, content_hash: CACHE_KEY,
        screen_metadata=lambda conn, file_id, content_hash: (),
    )


# --- the three ceilings ------------------------------------------------------

def test_p6_holds_exactly_three_ceilings_and_all_three_are_p1s():
    assert len(P6_CEILING_KEYS) == 3
    assert set(P6_CEILING_KEYS) <= set(CEILING_KEYS)


def test_every_p6_ceiling_is_a_model_ceiling_which_is_why_degradation_cannot_substitute():
    # The whole of §8.6's "cost exhaustion must never turn into lower-quality
    # automatic classification" rests on this: the only route a P6 ceiling can close
    # is the LLM route, and `direct` and `rule` have already run.
    assert all(key.startswith("model.") for key in P6_CEILING_KEYS)
    assert {key for key in CEILING_KEYS if key.startswith("model.")} == set(P6_CEILING_KEYS)


def test_the_ceiling_values_come_from_p1s_store_and_never_from_this_package(p6_conn):
    assert ceiling_values(p6_conn) == {key: None for key in P6_CEILING_KEYS}
    set_ceiling(p6_conn, "model.max_cost_per_scan", 25)
    assert ceiling_values(p6_conn)["model.max_cost_per_scan"] == 25


def test_exhaustion_is_an_injected_predicate_asked_once_per_ceiling_in_order():
    asked: list[str] = []

    def budget_exhausted(key: str) -> bool:
        asked.append(key)
        return key == "model.max_cost_per_scan"

    assert exhausted_ceilings(budget_exhausted=budget_exhausted) == \
        ("model.max_cost_per_scan",)
    assert tuple(asked) == P6_CEILING_KEYS


def test_exhausted_ceilings_takes_its_predicate_as_a_required_keyword():
    parameter = inspect.signature(exhausted_ceilings).parameters["budget_exhausted"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty


# --- the degradation order ---------------------------------------------------

def test_the_order_is_direct_then_rule_then_llm(p6_conn):
    recorder = Recorder()
    resolve(a_resolver(recorder, llm=recorder.stage("llm")), p6_conn)
    # Asserted from the call sequence, not from a docstring.
    assert recorder.calls == ["direct", "rule", "llm"]
    assert DEGRADATION_ORDER == ("direct", "rule", "llm")


def test_the_producer_names_are_the_same_three_the_unresolved_row_records():
    # `rule` is the PRODUCER; `validated` is the reliability state it writes. The
    # `unresolved` row names the producer, so the two tuples must agree exactly.
    assert DEGRADATION_ORDER == ATTEMPTED_PRODUCERS


def test_only_the_llm_stage_is_ceiling_gated():
    assert CEILING_GATED_STAGES == frozenset({"llm"})
    assert CEILING_GATED_STAGES < set(DEGRADATION_ORDER)


def test_a_stage_map_that_is_not_exactly_the_three_is_refused():
    recorder = Recorder()
    with pytest.raises(StageSetInvalid):
        FactResolver(
            stages={"direct": recorder.stage("direct")},
            pending_fields=lambda conn, f, c: (FIELD,),
            budget_exhausted=lambda key: False,
            model_route_permitted=lambda file_id: True,
            record_pass=recorder.record_pass,
            cache_key_for=lambda f, c: CACHE_KEY,
            screen_metadata=lambda conn, f, c: (),
        )


def test_a_stage_map_with_a_fourth_producer_is_refused():
    # Screening is not a fourth producer (preamble §6), and neither is anything else
    # a later caller invents: the map must be exactly DEGRADATION_ORDER.
    recorder = Recorder()
    with pytest.raises(StageSetInvalid):
        FactResolver(
            stages={"direct": recorder.stage("direct"), "rule": recorder.stage("rule"),
                    "llm": None, "screen": recorder.stage("screen")},
            pending_fields=lambda conn, f, c: (FIELD,),
            budget_exhausted=lambda key: False,
            model_route_permitted=lambda file_id: True,
            record_pass=recorder.record_pass,
            cache_key_for=lambda f, c: CACHE_KEY,
            screen_metadata=lambda conn, f, c: (),
        )


def test_every_constructor_argument_is_a_required_keyword_with_no_default():
    for name, parameter in inspect.signature(FactResolver.__init__).parameters.items():
        if name == "self":
            continue
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, name
        assert parameter.default is inspect.Parameter.empty, name
    assert "screen_metadata" in inspect.signature(FactResolver.__init__).parameters


def test_screen_metadata_runs_before_any_stage(p6_conn):
    calls: list[str] = []

    def screen(conn, file_id, content_hash):
        calls.append("screen")
        return ()

    recorder = Recorder()
    resolver = FactResolver(
        stages={
            "direct": recorder.stage("direct", produces=("fact-direct",)),
            "rule": recorder.stage("rule"),
            "llm": None,
        },
        pending_fields=lambda conn, file_id, content_hash: (FIELD,),
        budget_exhausted=lambda key: False,
        model_route_permitted=lambda file_id: True,
        record_pass=recorder.record_pass,
        cache_key_for=lambda file_id, content_hash: CACHE_KEY,
        screen_metadata=screen,
    )
    resolve(resolver, p6_conn)
    assert calls == ["screen"]
    assert recorder.calls[0] == "direct"


def test_with_p8_absent_the_llm_route_does_not_exist_and_nothing_is_withheld(p6_conn):
    # Done-means 17's shape: `llm=None` is the ordinary path, not an error path. A
    # route that does not exist is not a route that was barred, so no `unresolved`
    # row is written and neither ceiling nor privacy is consulted.
    recorder = Recorder()
    result = resolve(a_resolver(recorder, llm=None, permitted=False,
                                exhausted=P6_CEILING_KEYS), p6_conn)
    assert recorder.calls == ["direct", "rule"]
    assert result.stages_run == ("direct", "rule")
    assert result.stages_barred == {}
    assert result.deferred_against == ()
    assert unresolved_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_an_absent_llm_route_never_asks_the_budget_or_the_privacy_predicate(p6_conn):
    # The stronger half of the test above: not merely "no row was written" but "the
    # question was never asked". A route that does not exist cannot be barred.
    asked: list[str] = []
    recorder = Recorder()
    resolver = FactResolver(
        stages={"direct": recorder.stage("direct"), "rule": recorder.stage("rule"),
                "llm": None},
        pending_fields=lambda conn, f, c: (FIELD,),
        budget_exhausted=lambda key: asked.append("budget:" + key) or True,
        model_route_permitted=lambda file_id: asked.append("privacy") or False,
        record_pass=recorder.record_pass,
        cache_key_for=lambda f, c: CACHE_KEY,
        screen_metadata=lambda conn, f, c: (),
    )
    resolve(resolver, p6_conn)
    assert asked == []


def test_the_pass_is_recorded_once_after_the_stages(p6_conn):
    recorder = Recorder()
    resolve(a_resolver(recorder), p6_conn)
    assert recorder.passes == [(FILE_ID, CONTENT_HASH)]


# --- what a ceiling is allowed to do -----------------------------------------

def test_a_reached_ceiling_defers_the_llm_route_and_substitutes_nothing(p6_conn):
    recorder = Recorder()
    llm = recorder.stage("llm", produces=("fact-llm",))
    result = resolve(
        a_resolver(recorder, llm=llm, exhausted=("model.max_cost_per_scan",)), p6_conn)

    # §8.6: the stronger route is subtracted; no weaker route takes its place. The
    # LLM stage was never entered, and no `possible` clue, below-margin candidate or
    # fuzzy date was promoted in its stead — `fact_ids` is exactly what `direct` and
    # `rule` returned.
    assert "llm" not in recorder.calls
    assert result.fact_ids == ("fact-direct",)
    assert result.stages_run == ("direct", "rule")
    assert result.stages_barred == {"llm": "budget"}
    assert result.deferred_against == ("model.max_cost_per_scan",)


def test_the_deferral_is_a_row_naming_the_field_that_stayed_unknown(p6_conn):
    recorder = Recorder()
    resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                       exhausted=("model.max_dossier_tokens_per_call",)), p6_conn)

    rows = unresolved_for_file(p6_conn, FILE_ID, CONTENT_HASH)
    assert len(rows) == 1
    assert rows[0]["field_key"] == FIELD
    assert rows[0]["reason"] == "budget_deferred"
    # §8.6: "mark the deferred stage, and leave the file or group in review rather
    # than guessing", which "avoids the false impression that an unprocessed file
    # was understood and found unimportant". The row records which producers had
    # already run, so a reader can see the work stopped rather than concluded.
    assert rows[0]["attempted_producers"] is not None


def test_the_deferral_row_names_the_producers_that_ran_and_the_stage_that_did_not(p6_conn):
    import json

    recorder = Recorder()
    resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                       exhausted=("model.max_cost_per_scan",)), p6_conn)
    rows = unresolved_for_file(p6_conn, FILE_ID, CONTENT_HASH)
    # "mark the deferred stage": the barred stage is named alongside the two that
    # completed, so the record says where the work stopped rather than only that it
    # stopped.
    assert json.loads(rows[0]["attempted_producers"]) == ["direct", "rule", "llm"]


def test_every_pending_field_gets_its_own_deferral_row(p6_conn):
    # An absent row is exactly "the false impression that an unprocessed file was
    # understood and found unimportant", so one row per field the barred route would
    # have attempted — not one row for the file.
    recorder = Recorder()
    result = resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                                pending=(FIELD, "target_school"),
                                exhausted=("model.max_cost_per_scan",)), p6_conn)
    rows = unresolved_for_file(p6_conn, FILE_ID, CONTENT_HASH)
    assert {row["field_key"] for row in rows} == {FIELD, "target_school"}
    assert result.reason_counts["budget_deferred"] == 2


def test_a_budget_deferral_is_not_an_abstention(p6_conn):
    recorder = Recorder()
    resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                       exhausted=("model.max_cost_per_scan",)), p6_conn)
    rows = unresolved_for_file(p6_conn, FILE_ID, CONTENT_HASH, reason="budget_deferred")
    assert len(rows) == 1
    assert rows[0]["reason"] in NOT_ABSTENTIONS


def test_a_deferral_and_an_abstention_are_distinguishable_from_the_records_alone(p6_conn):
    # Done-means 20's own words. An evidence-based refusal and a ceiling deferral
    # land in the same table, so the reason column plus `NOT_ABSTENTIONS` must be
    # enough to tell them apart with nothing else consulted.
    write_unresolved(p6_conn, file_id=FILE_ID, content_hash=CONTENT_HASH,
                     field_key="target_school", reason=NO_CANDIDATE_EVIDENCE,
                     attempted_producers=("direct", "rule"), evidence_refs=(),
                     cache_key=CACHE_KEY)
    recorder = Recorder()
    result = resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                                exhausted=("model.max_cost_per_scan",)), p6_conn)

    rows = unresolved_for_file(p6_conn, FILE_ID, CONTENT_HASH)
    deferred = [row for row in rows if row["reason"] in NOT_ABSTENTIONS]
    abstained = [row for row in rows if row["reason"] not in NOT_ABSTENTIONS]
    assert [row["reason"] for row in deferred] == [BUDGET_DEFERRED]
    assert [row["reason"] for row in abstained] == [NO_CANDIDATE_EVIDENCE]

    # Done-means 20 is satisfied by the three assertions above, which read the TABLE.
    # `reason_counts` is a different question -- "what did THIS pass do" -- and the
    # `no_candidate_evidence` row above was written before `resolve` was ever called.
    # Counting it here was the defect: the read was scoped to the file VERSION, so
    # every prior pass's refusals were reported as this pass's and the stage-output
    # payload stopped being byte-stable across two identical runs.
    assert result.reason_counts == {BUDGET_DEFERRED: 1}
    assert len(rows) == 2                      # both rows are on disk...
    assert len(result.unresolved_ids) == 1     # ...and one of them is this pass's


def test_multiple_exhausted_ceilings_are_all_attributed(p6_conn):
    recorder = Recorder()
    result = resolve(a_resolver(
        recorder, llm=recorder.stage("llm"),
        exhausted=("model.max_cost_per_scan", "model.max_llm_calls_per_thousand_files")), p6_conn)
    assert result.deferred_against == (
        "model.max_llm_calls_per_thousand_files", "model.max_cost_per_scan")


# --- privacy is a prohibition, not a resource decision ------------------------

def test_a_forbidden_model_route_withholds_and_does_not_defer(p6_conn):
    recorder = Recorder()
    result = resolve(a_resolver(recorder, llm=recorder.stage("llm"), permitted=False), p6_conn)

    assert "llm" not in recorder.calls
    assert result.stages_barred == {"llm": "privacy"}
    assert result.deferred_against == ()
    rows = unresolved_for_file(p6_conn, FILE_ID, CONTENT_HASH)
    assert [row["reason"] for row in rows] == ["privacy_withheld"]


def test_privacy_is_checked_before_the_ceiling_so_a_prohibition_is_never_reported_as_a_deferral(p6_conn):
    # §8.4 is a prohibition — "enforced before content reaches any model or external
    # connector" — and a file that may NEVER go to a model is not a file waiting for
    # budget. Both bars at once must report the prohibition.
    recorder = Recorder()
    result = resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                                permitted=False, exhausted=P6_CEILING_KEYS), p6_conn)
    assert result.stages_barred == {"llm": "privacy"}
    assert result.deferred_against == ()
    assert [row["reason"] for row in unresolved_for_file(p6_conn, FILE_ID, CONTENT_HASH)] \
        == ["privacy_withheld"]


def test_a_prohibited_route_never_even_asks_the_budget(p6_conn):
    # The prohibition short-circuits: asking the budget after a prohibition would
    # make a `deferred_against` available for a later reader to misreport.
    asked: list[str] = []
    recorder = Recorder()
    resolver = FactResolver(
        stages={"direct": recorder.stage("direct"), "rule": recorder.stage("rule"),
                "llm": recorder.stage("llm")},
        pending_fields=lambda conn, f, c: (FIELD,),
        budget_exhausted=lambda key: asked.append(key) or True,
        model_route_permitted=lambda file_id: False,
        record_pass=recorder.record_pass,
        cache_key_for=lambda f, c: CACHE_KEY,
        screen_metadata=lambda conn, f, c: (),
    )
    resolve(resolver, p6_conn)
    assert asked == []


def test_the_two_bars_have_two_reasons_and_neither_is_shared():
    assert REASON_BY_BAR == {"privacy": "privacy_withheld", "budget": "budget_deferred"}
    assert set(REASON_BY_BAR.values()) == set(NOT_ABSTENTIONS)


def test_the_two_bar_reasons_are_the_published_constants_not_second_copies():
    # Preamble §3.1: a bare literal is a second home for a published vocabulary.
    assert REASON_BY_BAR["privacy"] == PRIVACY_WITHHELD
    assert REASON_BY_BAR["budget"] == BUDGET_DEFERRED


# --- reporting ---------------------------------------------------------------

def test_deferred_counts_reports_against_each_of_the_three_ceilings(p6_conn):
    recorder = Recorder()
    result = resolve(a_resolver(
        recorder, llm=recorder.stage("llm"), pending=(FIELD,),
        exhausted=("model.max_cost_per_scan",)), p6_conn)

    counts = deferred_counts(p6_conn, results=(result,))
    assert set(counts) == set(P6_CEILING_KEYS)
    assert counts["model.max_cost_per_scan"] == 1
    assert counts["model.max_dossier_tokens_per_call"] == 0
    assert counts["model.max_llm_calls_per_thousand_files"] == 0


def test_deferred_counts_charges_every_ceiling_a_result_was_deferred_against(p6_conn):
    # §8.6 asks what each ceiling cost, not which one to blame, so a result exhausted
    # against two counts against both rather than against the first.
    recorder = Recorder()
    result = resolve(a_resolver(
        recorder, llm=recorder.stage("llm"),
        exhausted=("model.max_cost_per_scan",
                   "model.max_dossier_tokens_per_call")), p6_conn)
    counts = deferred_counts(p6_conn, results=(result,))
    assert counts["model.max_cost_per_scan"] == 1
    assert counts["model.max_dossier_tokens_per_call"] == 1
    assert counts["model.max_llm_calls_per_thousand_files"] == 0


def test_deferred_counts_refuses_a_ceiling_outside_p6s_three(p6_conn):
    forged = ResolveResult(file_id=FILE_ID, content_hash=CONTENT_HASH,
                           deferred_against=("ocr.max_pages_per_file",))
    with pytest.raises(UnknownCeiling):
        deferred_counts(p6_conn, results=(forged,))


def test_a_result_with_no_deferral_contributes_nothing(p6_conn):
    recorder = Recorder()
    result = resolve(a_resolver(recorder), p6_conn)
    assert deferred_counts(p6_conn, results=(result,)) == \
        {key: 0 for key in P6_CEILING_KEYS}


def test_a_privacy_withholding_is_not_counted_as_a_deferral(p6_conn):
    # A prohibition is not work waiting on budget, so it must not appear in a report
    # of what the ceilings cost.
    recorder = Recorder()
    result = resolve(a_resolver(recorder, llm=recorder.stage("llm"), permitted=False),
                     p6_conn)
    assert deferred_counts(p6_conn, results=(result,)) == \
        {key: 0 for key in P6_CEILING_KEYS}


def test_an_errored_result_is_constructible_without_a_resolve(p6_conn):
    # `resolve` never swallows: a producer that raises propagates, because P6's
    # failures are ContractViolations. The scan loop that catches one still owes P2
    # an envelope, so the error result is a named constructor rather than a branch.
    result = ResolveResult.errored(file_id=FILE_ID, content_hash=CONTENT_HASH,
                                   error="rules.apply_rules: boom")
    assert result.error == "rules.apply_rules: boom"
    assert result.fact_ids == ()
    assert result.stages_run == ()


def test_a_raising_producer_propagates(p6_conn):
    recorder = Recorder()

    def boom(conn, file_id, content_hash):
        raise RuntimeError("boom")

    resolver = FactResolver(
        stages={"direct": recorder.stage("direct"), "rule": boom, "llm": None},
        pending_fields=lambda conn, f, c: (FIELD,),
        budget_exhausted=lambda key: False,
        model_route_permitted=lambda file_id: True,
        record_pass=recorder.record_pass,
        cache_key_for=lambda f, c: CACHE_KEY,
        screen_metadata=lambda conn, f, c: (),
    )
    with pytest.raises(RuntimeError):
        resolve(resolver, p6_conn)
    # Preamble rule 5's recorded pass means a pass that COMPLETED, so Task 19's
    # `no_usable_facts` still raises rather than answering from a half-written table.
    assert recorder.passes == []


def test_a_resolve_result_is_frozen_and_its_mappings_are_not_writable(p6_conn):
    recorder = Recorder()
    result = resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                                exhausted=("model.max_cost_per_scan",)), p6_conn)
    with pytest.raises(Exception):
        result.fact_ids = ()
    with pytest.raises(TypeError):
        result.stages_barred["llm"] = "privacy"
    with pytest.raises(TypeError):
        result.reason_counts["budget_deferred"] = 99


# --- the no-invention guard, by runtime introspection -------------------------

def _numeric_constants(module) -> dict:
    """Every module-level name bound to a number, or to a collection containing one.

    Runtime introspection, not a source-text search: a text search matches comments
    and docstrings, and that false result has broken three tasks on this project.
    """
    found: dict = {}
    for name, value in vars(module).items():
        if name.startswith("_") or isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            found[name] = value
        elif isinstance(value, Mapping):
            if any(isinstance(v, (int, float)) and not isinstance(v, bool)
                   for v in value.values()):
                found[name] = value
        elif isinstance(value, (tuple, list, set, frozenset)):
            if any(isinstance(v, (int, float)) and not isinstance(v, bool)
                   for v in value):
                found[name] = value
    return found


def test_neither_module_defines_a_number():
    assert _numeric_constants(budgets_module) == {}
    assert _numeric_constants(resolver_module) == {}


def test_the_resolver_imports_no_producer_module():
    # The producers arrive as injected `Stage` callables. Importing one here would
    # put a build-order edge inside a wave that has none, and would let a threshold,
    # a gazetteer or a regex catalogue reach this module through a sibling.
    allowed = {"facts.budgets", "facts.unresolved", "facts.resolver"}
    from_facts = {module for module in
                  (getattr(value, "__module__", None)
                   for value in vars(resolver_module).values())
                  if module and module.startswith("facts.")}
    assert from_facts <= allowed


def test_two_identical_passes_report_the_same_counts_and_the_same_payload(p6_conn):
    """The divergence Task 21's payload design says it exists to prevent, pinned.

    `reason_counts` read `unresolved_for_file`, which is scoped to the file VERSION
    and not to a pass, so a second resolve of one version reported the first pass's
    rows as its own. That reached `fact_stage_output`'s payload and made it differ
    across two identical runs — "every replay report[ing] a divergence that is not
    one". Task 21's own guard compares two in-memory `ResolveResult`s, so it could
    never catch this: the divergence is created by the database, not by the dataclass.
    """
    from facts.stage_output import fact_stage_output

    def one_pass():
        recorder = Recorder()
        return resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                                  exhausted=("model.max_cost_per_scan",)), p6_conn)

    first, second = one_pass(), one_pass()

    assert first.reason_counts == second.reason_counts == {BUDGET_DEFERRED: 1}
    assert len(first.unresolved_ids) == len(second.unresolved_ids) == 1
    assert set(first.unresolved_ids).isdisjoint(second.unresolved_ids)

    # two rows on disk, one charged to each pass
    assert p6_conn.execute(
        "SELECT count(*) c FROM unresolved").fetchone()["c"] == 2
    assert deferred_counts(p6_conn, results=(first, second)) == {
        "model.max_cost_per_scan": 2,
        "model.max_llm_calls_per_thousand_files": 0,
        "model.max_dossier_tokens_per_call": 0,
    }

    assert (canonical_json(fact_stage_output(result=first)["payload"])
            == canonical_json(fact_stage_output(result=second)["payload"]))


def test_a_warm_re_resolve_reports_abstained_and_does_not_accuse_b7(p6_conn):
    """Scoping the counts to one pass must not turn a warm re-resolve into a false
    accusation.

    `_outcome_for` raises "a result with no fact and no `unresolved` row is the missing
    row B7 exists to forbid" — a statement about a producer that refused silently.
    After the counts became pass-scoped, a second resolve that wrote nothing new hit
    that raise with the row sitting on disk from the first pass. Two different
    questions were being answered by one number: what THIS pass did, which must be
    pass-scoped or the payload stops being byte-stable, and what the VERSION's state
    is, which is what the outcome reports.
    """
    from facts.stage_output import fact_stage_output

    write_unresolved(p6_conn, file_id=FILE_ID, content_hash=CONTENT_HASH,
                     field_key="target_school", reason=NO_CANDIDATE_EVIDENCE,
                     attempted_producers=("direct",), evidence_refs=(),
                     cache_key=CACHE_KEY)
    result = resolve(a_barren_resolver(), p6_conn)

    assert result.reason_counts == {}          # this pass wrote nothing...
    assert result.version_has_unresolved       # ...but the version carries a row
    envelope = fact_stage_output(result=result)
    assert envelope["outcome"] == "abstained"
    # and the payload still reports the PASS, so replay sees no false divergence
    assert '"unresolved_reasons":{}' in envelope["payload"]


def test_a_pass_with_no_row_anywhere_still_accuses_b7(p6_conn):
    """The guard must keep its teeth: a genuinely empty pass over a version with
    nothing on disk is still the missing row B7 forbids."""
    from facts.stage_output import fact_stage_output

    result = resolve(a_barren_resolver(), p6_conn)
    assert result.reason_counts == {}
    assert not result.version_has_unresolved
    with pytest.raises(ValueError, match="B7"):
        fact_stage_output(result=result)
