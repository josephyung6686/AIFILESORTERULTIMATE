### Task 20: §8.6 — the three ceilings, the degradation order, and the resolver that enforces it

**Files:** create `src/facts/budgets.py`, `src/facts/resolver.py`; test `tests/p6/test_p6_budgets.py`.

**Interfaces:**
- Consumes: `database_agent.budget.CEILING_KEYS`, `database_agent.budget.get_ceiling`;
  `facts.unresolved.write_unresolved`, `facts.unresolved.unresolved_for_file`; every producer
  module, **through injected stage callables bound at the composition root** (see Step 1's note).
- Produces: `P6_CEILING_KEYS: tuple[str, str, str]` (`model.max_llm_calls_per_thousand_files`,
  `model.max_cost_per_scan`, `model.max_dossier_tokens_per_call`),
  `DEGRADATION_ORDER: tuple[str, str, str]` (`direct`, `rule`, `llm`),
  `CEILING_GATED_STAGES: frozenset[str]`, `UnknownCeiling`,
  `ceiling_values(conn) -> dict[str, int | None]`,
  `exhausted_ceilings(*, budget_exhausted: Callable[[str], bool]) -> tuple[str, ...]`,
  `deferred_counts(conn, *, results: Iterable[ResolveResult]) -> dict[str, int]`;
  `Stage`, `PassRecorder`, `REASON_BY_BAR: Mapping[str, str]`, `StageSetInvalid`,
  `ResolveResult(file_id, content_hash, fact_ids, reason_counts, stages_run, stages_barred,
  deferred_against, error)` with `ResolveResult.errored(*, file_id, content_hash, error)`,
  `FactResolver` — the one entry point, constructed with every injected strategy and threshold;
  `FactResolver.resolve(conn, *, file_id, content_hash) -> ResolveResult`.

**Done-means:** 20 (the `budget_deferred` half).

---

**The design sentences this task is accountable to, quoted from
`planning/00-database-agent-product-design.md` and verified by `grep` before they were written here:**

> *"The engine should degrade in a predictable order. Direct facts and high-precision rules run first
> because they are cheap and reliable. Full local extraction and OCR run within the configured
> budget. Graph retrieval activates only for files with meaningful incomplete evidence and a
> plausible anchor. LLM calls are reserved for bounded ambiguities, group coherence, custom-template
> generation, and residual interpretation. If the budget is exhausted, the product should retain
> extracted evidence, mark the deferred stage, and leave the file or group in review rather than
> guessing. Cost exhaustion must never turn into lower-quality automatic classification."*

> *"This makes the product's limitations legible and avoids the false impression that an unprocessed
> file was understood and found unimportant."*

Three consequences, and each is a test below rather than a paragraph:

1. **All three of P6's ceilings are `model.*` ceilings.** Checked against P1's live sixteen:
   `model.max_llm_calls_per_thousand_files`, `model.max_cost_per_scan`,
   `model.max_dossier_tokens_per_call`. The other thirteen are P5's, P9's, P10's, P11's, P13's and
   P4's. So the **only** producer a P6 ceiling can close is the LLM route — `direct` and `rule` have
   already run by the time any ceiling is consulted. That is what makes *"cost exhaustion must never
   turn into lower-quality automatic classification"* mechanically true here instead of aspirational:
   there is no cheaper producer to fall back **to**. Degradation in P6 is subtraction, never
   substitution.
2. **The bar is recorded, not inferred.** A barred field gets an `unresolved` row — `budget_deferred`
   for a ceiling, `privacy_withheld` for a handling class that forbids the model route — so the
   unfinished work is visible *as* unfinished. Neither reason is an abstention (P6 SPEC,
   `unresolved` rule 4).
3. **No number lives in `facts`.** P1 stores ceiling *values* and enforces nothing
   (`database_agent/budget.py`: *"P1 holds and publishes values; P1 enforces none of them. Reading a
   ceiling is not enforcing it."*), so exhaustion arrives as an injected predicate — P3's precedent,
   widened from `Callable[[], bool]` to `Callable[[str], bool]` because P6 must report per-ceiling
   deferral counts and therefore has to name which ceiling it asked about.

**Where the per-ceiling count durably lives.** `write_unresolved` has no ceiling-key column and P6
owns exactly four tables, so `deferred_counts` is a scan-scoped aggregate over the `ResolveResult`s
the caller collected, cross-checked against the `unresolved` rows actually written. The durable
per-ceiling record is Task 21's `stage_output.payload`, which carries `deferred_against` verbatim and
which P2 stores and never parses. Stated here so no one later adds a fifth P6 table for it.

---

- [ ] **Step 1: Read the seams this task binds to, and confirm the two names Wave A owes it.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -c "
  import inspect
  from database_agent.budget import CEILING_KEYS, get_ceiling, set_ceiling
  print('P1 ceilings:', len(CEILING_KEYS))
  print([k for k in CEILING_KEYS if k.startswith('model.')])
  print('get_ceiling:', inspect.signature(get_ceiling))
  from facts.unresolved import write_unresolved, unresolved_for_file, UNRESOLVED_REASONS, ATTEMPTED_PRODUCERS
  print('write_unresolved:', inspect.signature(write_unresolved))
  print('unresolved_for_file:', inspect.signature(unresolved_for_file))
  print('reasons:', UNRESOLVED_REASONS)
  print('producers:', ATTEMPTED_PRODUCERS)
  from facts.schema import create_facts_schema
  from facts.fields import create_fields
  print('schema entry point OK')
  "
  ```

  Expected: P1 publishes sixteen keys of which exactly three start with `model.`; `get_ceiling` is
  `(conn, key) -> int | None`; `UNRESOLVED_REASONS` contains `budget_deferred` and `privacy_withheld`;
  `ATTEMPTED_PRODUCERS` is `("direct", "rule", "llm")`.

  > **The one name this task assumes rather than reads from the skeleton.** Tasks 2–5 each *modify*
  > `src/facts/schema.py` but the skeleton's `Interfaces:` blocks never name its entry point. This
  > task, and Task 21, call it **`facts.schema.create_facts_schema(conn) -> None`**. If Wave A landed
  > a different spelling, change the two import lines and nothing else — no logic in this task
  > depends on it. Do not add a second creator.

  > **And the one contract this task reads as a binding, not as an import.** The skeleton's
  > `Consumes:` says *"every producer module"*. `resolver.py` imports **none** of them. It takes the
  > three producers as injected `Stage` callables of one uniform shape,
  > `Callable[[sqlite3.Connection, str, str], tuple[str, ...]]`, which the composition root binds:
  >
  > | `DEGRADATION_ORDER` entry | bound at the composition root to |
  > |---|---|
  > | `direct` | `partial(facts.direct.direct_facts, slots=<injected DirectSlots>)` |
  > | `rule` | `partial(facts.rules.apply_rules, rules=<injected Rule tuple>)` |
  > | `llm` | the P8 route, or **`None`** — and `None` is the ordinary case, because P8 does not exist |
  >
  > Three reasons, and they are the whole justification for not importing the producers here.
  > **(a)** It is what "constructed with every injected strategy and threshold" means: `DirectSlots`,
  > the `Rule` tuple, the score minimum and the margin minimum are bound *into* the stage callable by
  > the caller, so no strategy and no number can reach `resolver.py` at all — Task 25's
  > runtime-introspection guard then passes for a structural reason rather than by inspection luck.
  > **(b)** It is what makes *"the order is asserted from the call sequence rather than from a
  > docstring"* a test one can actually write: a recording stage appends its own name.
  > **(c)** Tasks 17 and 19 are being written in parallel with this one, in the same wave; a direct
  > import would put a build-order edge inside a wave that has none. `record_pass` is injected as a
  > `PassRecorder` for exactly that reason, and because the tier set it needs
  > (`analysis_tiers: frozenset[str]`) is a read over P4's runs that `resolve`'s fixed signature has
  > nowhere to carry.

- [ ] **Step 2: Write the test file, complete.**

  Create `tests/p6/test_p6_budgets.py`:

  ```python
  # tests/p6/test_p6_budgets.py
  """§8.6 — the three ceilings, the degradation order, and what a ceiling may not do.

  The rule under test is one sentence of §00: "Cost exhaustion must never turn into
  lower-quality automatic classification." Its P6 form is that a ceiling SUBTRACTS the
  LLM route and substitutes nothing for it, and that the subtraction is a row.
  """
  from __future__ import annotations

  import inspect
  from collections.abc import Mapping

  import pytest

  from database_agent.budget import CEILING_KEYS, set_ceiling

  import facts.budgets as budgets_module
  import facts.resolver as resolver_module
  from facts.budgets import (
      CEILING_GATED_STAGES, DEGRADATION_ORDER, P6_CEILING_KEYS, UnknownCeiling,
      ceiling_values, deferred_counts, exhausted_ceilings,
  )
  from facts.fields import create_fields
  from facts.resolver import REASON_BY_BAR, FactResolver, ResolveResult, StageSetInvalid
  from facts.schema import create_facts_schema
  from facts.unresolved import ATTEMPTED_PRODUCERS, NOT_ABSTENTIONS, unresolved_for_file

  #: §3.8's role field, ratified into the catalogue by round 1's F-1 and required to
  #: exist by Done-means 13 and 22. Used here only as a field key that is certain to be
  #: in the catalogue, so `write_unresolved` has something legal to name.
  FIELD = "authored_by"

  FILE_ID = "file-01"
  CONTENT_HASH = "042896dc1966b8a6214e5383aba5b8b931cfa049d17aafa37eb8a77c859b95da"
  CACHE_KEY = "sha256:0000000000000000000000000000000000000000000000000000000000000001"


  @pytest.fixture()
  def p6(conn):
      create_facts_schema(conn)
      create_fields(conn)
      return conn


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
      )


  def resolve(resolver: FactResolver, conn) -> ResolveResult:
      return resolver.resolve(conn, file_id=FILE_ID, content_hash=CONTENT_HASH)


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


  def test_the_ceiling_values_come_from_p1s_store_and_never_from_this_package(p6):
      assert ceiling_values(p6) == {key: None for key in P6_CEILING_KEYS}
      set_ceiling(p6, "model.max_cost_per_scan", 25)
      assert ceiling_values(p6)["model.max_cost_per_scan"] == 25


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

  def test_the_order_is_direct_then_rule_then_llm(p6):
      recorder = Recorder()
      resolve(a_resolver(recorder, llm=Recorder.stage(recorder, "llm")), p6)
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
          )


  def test_every_constructor_argument_is_a_required_keyword_with_no_default():
      for name, parameter in inspect.signature(FactResolver.__init__).parameters.items():
          if name == "self":
              continue
          assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, name
          assert parameter.default is inspect.Parameter.empty, name


  def test_with_p8_absent_the_llm_route_does_not_exist_and_nothing_is_withheld(p6):
      # Done-means 17's shape: `llm=None` is the ordinary path, not an error path. A
      # route that does not exist is not a route that was barred, so no `unresolved`
      # row is written and neither ceiling nor privacy is consulted.
      recorder = Recorder()
      result = resolve(a_resolver(recorder, llm=None, permitted=False,
                                  exhausted=P6_CEILING_KEYS), p6)
      assert recorder.calls == ["direct", "rule"]
      assert result.stages_run == ("direct", "rule")
      assert result.stages_barred == {}
      assert result.deferred_against == ()
      assert unresolved_for_file(p6, FILE_ID, CONTENT_HASH) == []


  def test_the_pass_is_recorded_once_after_the_stages(p6):
      recorder = Recorder()
      resolve(a_resolver(recorder), p6)
      assert recorder.passes == [(FILE_ID, CONTENT_HASH)]


  # --- what a ceiling is allowed to do -----------------------------------------

  def test_a_reached_ceiling_defers_the_llm_route_and_substitutes_nothing(p6):
      recorder = Recorder()
      llm = recorder.stage("llm", produces=("fact-llm",))
      result = resolve(
          a_resolver(recorder, llm=llm, exhausted=("model.max_cost_per_scan",)), p6)

      # §8.6: the stronger route is subtracted; no weaker route takes its place. The
      # LLM stage was never entered, and no `possible` clue, below-margin candidate or
      # fuzzy date was promoted in its stead — `fact_ids` is exactly what `direct` and
      # `rule` returned.
      assert "llm" not in recorder.calls
      assert result.fact_ids == ("fact-direct",)
      assert result.stages_run == ("direct", "rule")
      assert result.stages_barred == {"llm": "budget"}
      assert result.deferred_against == ("model.max_cost_per_scan",)


  def test_the_deferral_is_a_row_naming_the_field_that_stayed_unknown(p6):
      recorder = Recorder()
      resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                         exhausted=("model.max_dossier_tokens_per_call",)), p6)

      rows = unresolved_for_file(p6, FILE_ID, CONTENT_HASH)
      assert len(rows) == 1
      assert rows[0]["field_key"] == FIELD
      assert rows[0]["reason"] == "budget_deferred"
      # "visible as deferred, never as 'understood and found unimportant'": the row
      # records which producers had already run, so a reader can see the work stopped
      # rather than concluded.
      assert rows[0]["attempted_producers"] is not None


  def test_a_budget_deferral_is_not_an_abstention(p6):
      recorder = Recorder()
      resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                         exhausted=("model.max_cost_per_scan",)), p6)
      rows = unresolved_for_file(p6, FILE_ID, CONTENT_HASH, reason="budget_deferred")
      assert len(rows) == 1
      assert rows[0]["reason"] in NOT_ABSTENTIONS


  def test_multiple_exhausted_ceilings_are_all_attributed(p6):
      recorder = Recorder()
      result = resolve(a_resolver(
          recorder, llm=recorder.stage("llm"),
          exhausted=("model.max_cost_per_scan", "model.max_llm_calls_per_thousand_files")), p6)
      assert result.deferred_against == (
          "model.max_llm_calls_per_thousand_files", "model.max_cost_per_scan")


  # --- privacy is a prohibition, not a resource decision ------------------------

  def test_a_forbidden_model_route_withholds_and_does_not_defer(p6):
      recorder = Recorder()
      result = resolve(a_resolver(recorder, llm=recorder.stage("llm"), permitted=False), p6)

      assert "llm" not in recorder.calls
      assert result.stages_barred == {"llm": "privacy"}
      assert result.deferred_against == ()
      rows = unresolved_for_file(p6, FILE_ID, CONTENT_HASH)
      assert [row["reason"] for row in rows] == ["privacy_withheld"]


  def test_privacy_is_checked_before_the_ceiling_so_a_prohibition_is_never_reported_as_a_deferral(p6):
      # §8.4 is a prohibition — "enforced before content reaches any model or external
      # connector" — and a file that may NEVER go to a model is not a file waiting for
      # budget. Both bars at once must report the prohibition.
      recorder = Recorder()
      result = resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                                  permitted=False, exhausted=P6_CEILING_KEYS), p6)
      assert result.stages_barred == {"llm": "privacy"}
      assert result.deferred_against == ()
      assert [row["reason"] for row in unresolved_for_file(p6, FILE_ID, CONTENT_HASH)] \
          == ["privacy_withheld"]


  def test_the_two_bars_have_two_reasons_and_neither_is_shared():
      assert REASON_BY_BAR == {"privacy": "privacy_withheld", "budget": "budget_deferred"}
      assert set(REASON_BY_BAR.values()) == set(NOT_ABSTENTIONS)


  # --- reporting ---------------------------------------------------------------

  def test_deferred_counts_reports_against_each_of_the_three_ceilings(p6):
      recorder = Recorder()
      result = resolve(a_resolver(
          recorder, llm=recorder.stage("llm"), pending=(FIELD,),
          exhausted=("model.max_cost_per_scan",)), p6)

      counts = deferred_counts(p6, results=(result,))
      assert set(counts) == set(P6_CEILING_KEYS)
      assert counts["model.max_cost_per_scan"] == 1
      assert counts["model.max_dossier_tokens_per_call"] == 0
      assert counts["model.max_llm_calls_per_thousand_files"] == 0


  def test_deferred_counts_refuses_a_ceiling_outside_p6s_three(p6):
      forged = ResolveResult(file_id=FILE_ID, content_hash=CONTENT_HASH,
                             deferred_against=("ocr.max_pages_per_file",))
      with pytest.raises(UnknownCeiling):
          deferred_counts(p6, results=(forged,))


  def test_a_result_with_no_deferral_contributes_nothing(p6):
      recorder = Recorder()
      result = resolve(a_resolver(recorder), p6)
      assert deferred_counts(p6, results=(result,)) == \
          {key: 0 for key in P6_CEILING_KEYS}


  def test_an_errored_result_is_constructible_without_a_resolve(p6):
      # `resolve` never swallows: a producer that raises propagates, because P6's
      # failures are ContractViolations. The scan loop that catches one still owes P2
      # an envelope, so the error result is a named constructor rather than a branch.
      result = ResolveResult.errored(file_id=FILE_ID, content_hash=CONTENT_HASH,
                                     error="rules.apply_rules: boom")
      assert result.error == "rules.apply_rules: boom"
      assert result.fact_ids == ()
      assert result.stages_run == ()


  def test_a_raising_producer_propagates(p6):
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
      )
      with pytest.raises(RuntimeError):
          resolve(resolver, p6)
      assert recorder.passes == []


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
      # The producers arrive as injected `Stage` callables; importing one here would
      # put a build-order edge inside a wave that has none, and would let a strategy
      # reach this module.
      forbidden = {"direct", "rules", "facets", "dates", "domains", "llm_seam",
                   "discount", "usable", "cache"}
      imported = {name for name, value in vars(resolver_module).items()
                  if getattr(value, "__module__", "").startswith("facts.")}
      assert not {getattr(value, "__module__", "").split(".")[-1]
                  for value in vars(resolver_module).values()
                  if getattr(value, "__module__", "").startswith("facts.")} & forbidden
      assert imported <= {"write_unresolved", "unresolved_for_file", "exhausted_ceilings",
                          "ResolveResult", "FactResolver", "StageSetInvalid"}
  ```

- [ ] **Step 3: Run it and read the failure.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest tests/p6/test_p6_budgets.py -q
  ```

  **Expected FAILURE:** collection error —
  `ModuleNotFoundError: No module named 'facts.budgets'`. Nothing in the file is
  importable yet, so pytest reports one error and zero tests, not a failed assertion.

- [ ] **Step 4: Write `src/facts/budgets.py`, complete.**

  ```python
  # src/facts/budgets.py
  """§8.6 — the three ceilings P6 holds, and the one thing a ceiling may not change.

  §00, verbatim: "If the budget is exhausted, the product should retain extracted
  evidence, mark the deferred stage, and leave the file or group in review rather than
  guessing. Cost exhaustion must never turn into lower-quality automatic
  classification."

  Every one of P6's three ceilings is a `model.*` ceiling. That is not a coincidence to
  note in passing — it is what makes the sentence above mechanical here. By the time
  any ceiling is consulted, `direct` and `rule` have already run, so the only route a
  ceiling can close is the LLM route and there is no cheaper producer to fall back to.
  Degradation in P6 is subtraction, never substitution.

  P1 holds the ceiling VALUES and enforces none of them, so exhaustion arrives as an
  injected predicate — P3's precedent, widened from `Callable[[], bool]` to
  `Callable[[str], bool]` because §8.6's reporting requirement is per ceiling. No
  number is defined in this module.
  """
  from __future__ import annotations

  import sqlite3
  from typing import TYPE_CHECKING, Callable, Iterable

  from database_agent.budget import CEILING_KEYS, get_ceiling

  from facts.unresolved import unresolved_for_file

  if TYPE_CHECKING:  # `resolver` imports this module; the annotation must not.
      from facts.resolver import ResolveResult

  #: §8.6's three model ceilings, spelled with P1's keys. P1 publishes sixteen; the
  #: other thirteen belong to P4, P5, P9, P10, P11 and P13.
  P6_CEILING_KEYS: tuple[str, str, str] = (
      "model.max_llm_calls_per_thousand_files",
      "model.max_cost_per_scan",
      "model.max_dossier_tokens_per_call",
  )

  #: §8.6: "Direct facts and high-precision rules run first because they are cheap and
  #: reliable ... LLM calls are reserved for bounded ambiguities". P6's three producers
  #: in that order. These are PRODUCER names and they are deliberately the same three
  #: strings as `facts.unresolved.ATTEMPTED_PRODUCERS`, so an abstention row can name
  #: what ran. `rule` is the producer; `validated` is the reliability state it writes.
  DEGRADATION_ORDER: tuple[str, str, str] = ("direct", "rule", "llm")

  #: The only producer a ceiling can close, held as data so the resolver's gate is
  #: readable from this module rather than from an `if` buried in a loop.
  CEILING_GATED_STAGES: frozenset[str] = frozenset({"llm"})


  class UnknownCeiling(Exception):
      """A ceiling key outside P6's three was attributed a deferral."""


  def ceiling_values(conn: sqlite3.Connection) -> dict[str, int | None]:
      """P6's three ceilings as P1 currently holds them.

      Returned for reporting and for a caller assembling its own predicate. P6 does
      not compare against these numbers: comparing would put the enforcement here,
      and P1's own docstring is explicit that reading a ceiling is not enforcing it.
      """
      return {key: get_ceiling(conn, key) for key in P6_CEILING_KEYS}


  def exhausted_ceilings(*, budget_exhausted: Callable[[str], bool]) -> tuple[str, ...]:
      """Which of P6's three the caller reports exhausted, asked in published order.

      All of them are asked, not just the first: §8.6 requires P6 to report how much
      work it deferred against EACH ceiling, and a short-circuit would attribute a
      simultaneous exhaustion to whichever key happened to sort first.
      """
      return tuple(key for key in P6_CEILING_KEYS if budget_exhausted(key))


  def deferred_counts(conn: sqlite3.Connection, *,
                      results: Iterable["ResolveResult"]) -> dict[str, int]:
      """How many fact-resolution requests were deferred against each ceiling.

      Scan-scoped, and cross-checked against the records: the count for a result is
      the number of `budget_deferred` rows that result actually wrote, so the report
      cannot drift from the table. A result exhausted against two ceilings counts
      against both — §8.6 asks what each ceiling cost, not which one to blame.

      There is no per-ceiling column on `unresolved` and P6 owns exactly four tables,
      so the DURABLE per-ceiling record is Task 21's `stage_output.payload`, which
      carries `deferred_against` verbatim and which P2 stores and never parses.
      """
      counts: dict[str, int] = {key: 0 for key in P6_CEILING_KEYS}
      for result in results:
          if not result.deferred_against:
              continue
          rows = unresolved_for_file(conn, result.file_id, result.content_hash,
                                     reason="budget_deferred")
          for key in result.deferred_against:
              if key not in P6_CEILING_KEYS:
                  raise UnknownCeiling(
                      f"{key!r} is not one of P6's three model ceilings "
                      f"{P6_CEILING_KEYS}; P1 publishes it, another part holds it"
                  )
              counts[key] += len(rows)
      return counts


  # Asserted at import so a P1 rename is a startup failure rather than a silent
  # miscount: P6 names three of P1's sixteen keys and owns none of them.
  assert set(P6_CEILING_KEYS) <= set(CEILING_KEYS)
  ```

- [ ] **Step 5: Write `src/facts/resolver.py`, complete.**

  ```python
  # src/facts/resolver.py
  """The one entry point, sequencing P6's producers in §8.6's order.

  The order is a contract, not an implementation detail, which is why it is a
  sequencer and not three calls scattered through a caller: §00 says "The engine
  should degrade in a predictable order. Direct facts and high-precision rules run
  first because they are cheap and reliable."

  The producers arrive as injected `Stage` callables. This module imports none of
  them, so no threshold, gazetteer, regex catalogue or producer-string list can reach
  it — the caller binds those into the stage it hands over. It also means Tasks 17 and
  19, written in the same wave, are not build-order dependencies of this one.

  `resolve` never swallows an exception. P6's failures are ContractViolations and must
  propagate; a caller that catches one still owes P2 an envelope, and constructs it
  with `ResolveResult.errored`.
  """
  from __future__ import annotations

  import sqlite3
  from dataclasses import dataclass, field
  from types import MappingProxyType
  from typing import Callable, Mapping

  from facts.budgets import (
      CEILING_GATED_STAGES, DEGRADATION_ORDER, exhausted_ceilings,
  )
  from facts.unresolved import unresolved_for_file, write_unresolved

  #: One producer, one shape. The caller binds every strategy and every threshold into
  #: the callable before handing it over, so this module sees neither.
  Stage = Callable[[sqlite3.Connection, str, str], "tuple[str, ...]"]

  #: `facts.usable.record_pass`, bound by the caller to supply the tier set it needs.
  #: Injected rather than imported because `resolve`'s signature is fixed by the
  #: skeleton and has nowhere to carry `analysis_tiers`, and because determining which
  #: tiers a pass covered is a read over P4's runs that belongs to Task 19's owner.
  PassRecorder = Callable[[sqlite3.Connection, str, str], None]

  #: Why a ceiling-gated stage did not run, and the `unresolved` reason each produces.
  #: Two bars, two reasons, no shared bucket — and neither reason is an abstention.
  REASON_BY_BAR: Mapping[str, str] = MappingProxyType({
      "privacy": "privacy_withheld",
      "budget": "budget_deferred",
  })


  class StageSetInvalid(Exception):
      """The stage map is not exactly §8.6's three producers."""


  @dataclass(frozen=True)
  class ResolveResult:
      """What one pass over one file version did, in the terms §8.5 measures.

      `fact_ids` is what the producers returned. `reason_counts` is read back from the
      `unresolved` table rather than accumulated in memory, so Done-means 20's "the two
      are distinguishable from the records alone" is true by construction rather than
      by care.
      """
      file_id: str
      content_hash: str
      fact_ids: tuple[str, ...] = ()
      reason_counts: Mapping[str, int] = field(default_factory=dict)
      stages_run: tuple[str, ...] = ()
      stages_barred: Mapping[str, str] = field(default_factory=dict)
      deferred_against: tuple[str, ...] = ()
      error: str | None = None

      def __post_init__(self) -> None:
          object.__setattr__(self, "reason_counts",
                             MappingProxyType(dict(self.reason_counts)))
          object.__setattr__(self, "stages_barred",
                             MappingProxyType(dict(self.stages_barred)))

      @classmethod
      def errored(cls, *, file_id: str, content_hash: str,
                  error: str) -> "ResolveResult":
          """The stage failed. §8.5's fourth outcome still needs an envelope."""
          return cls(file_id=file_id, content_hash=content_hash, error=error)


  class FactResolver:
      """P6's single entry point. Constructed with every injected strategy; holds none.

      `stages` maps each of `DEGRADATION_ORDER` to a `Stage` or to `None`. `None` means
      the route does not exist — which is the ordinary case for `llm`, because P8 does
      not exist. A route that does not exist is NOT a route that was barred: nothing is
      withheld, nothing is deferred, and no `unresolved` row is written for it.
      """

      def __init__(self, *, stages: Mapping[str, Stage | None],
                   pending_fields: Callable[[sqlite3.Connection, str, str],
                                            "tuple[str, ...]"],
                   budget_exhausted: Callable[[str], bool],
                   model_route_permitted: Callable[[str], bool],
                   record_pass: PassRecorder,
                   cache_key_for: Callable[[str, str], str]) -> None:
          if set(stages) != set(DEGRADATION_ORDER):
              raise StageSetInvalid(
                  f"stages must be exactly {DEGRADATION_ORDER}, got "
                  f"{tuple(sorted(stages))}"
              )
          self._stages = dict(stages)
          self._pending_fields = pending_fields
          self._budget_exhausted = budget_exhausted
          self._model_route_permitted = model_route_permitted
          self._record_pass = record_pass
          self._cache_key_for = cache_key_for

      def resolve(self, conn: sqlite3.Connection, *, file_id: str,
                  content_hash: str) -> ResolveResult:
          stages_run: list[str] = []
          barred: dict[str, str] = {}
          deferred_against: tuple[str, ...] = ()
          fact_ids: list[str] = []

          for name in DEGRADATION_ORDER:
              stage = self._stages[name]
              if stage is None:
                  continue
              if name in CEILING_GATED_STAGES:
                  # §8.4 first: a handling class that forbids the model route is a
                  # PROHIBITION, and a file that may never reach a model is not a file
                  # waiting for budget to free up. Reporting it as a deferral would
                  # promise work that will never be done.
                  if not self._model_route_permitted(file_id):
                      barred[name] = "privacy"
                      continue
                  exhausted = exhausted_ceilings(
                      budget_exhausted=self._budget_exhausted)
                  if exhausted:
                      barred[name] = "budget"
                      deferred_against = exhausted
                      continue
              fact_ids.extend(stage(conn, file_id, content_hash))
              stages_run.append(name)

          if barred:
              self._write_bars(conn, file_id=file_id, content_hash=content_hash,
                               barred=barred, attempted=tuple(stages_run))

          # Only now: preamble rule 5's recorded pass means a pass that COMPLETED. A
          # producer that raised skipped this line, so `no_usable_facts` still raises
          # `FactPassNotRun` for that content hash rather than answering from a
          # half-written table.
          self._record_pass(conn, file_id, content_hash)

          counts: dict[str, int] = {}
          for row in unresolved_for_file(conn, file_id, content_hash):
              counts[row["reason"]] = counts.get(row["reason"], 0) + 1

          return ResolveResult(
              file_id=file_id, content_hash=content_hash,
              fact_ids=tuple(fact_ids), reason_counts=counts,
              stages_run=tuple(stages_run), stages_barred=barred,
              deferred_against=deferred_against,
          )

      def _write_bars(self, conn: sqlite3.Connection, *, file_id: str,
                      content_hash: str, barred: Mapping[str, str],
                      attempted: "tuple[str, ...]") -> None:
          """The unfinished work, recorded AS unfinished.

          §00: the product must avoid "the false impression that an unprocessed file
          was understood and found unimportant". An absent row gives exactly that
          impression, so every field the barred route would have attempted gets one.

          `evidence_refs` is empty and that is correct rather than lazy: the barred
          route never looked at an observation, and the SPEC's own column note says
          the refs are "the observation keys considered, where any were (may be
          empty)". The extracted evidence is retained where it always was — in P4's
          `evidence` table, which P6 never writes and which P4's
          `evidence_never_overwritten` trigger makes unfalsifiable.
          """
          cache_key = self._cache_key_for(file_id, content_hash)
          for stage_name, bar in barred.items():
              reason = REASON_BY_BAR[bar]
              for field_key in self._pending_fields(conn, file_id, content_hash):
                  write_unresolved(
                      conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, reason=reason,
                      attempted_producers=attempted + (stage_name,),
                      evidence_refs=(), cache_key=cache_key,
                  )
  ```

- [ ] **Step 6: Run it and read the pass.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest tests/p6/test_p6_budgets.py -q
  ```

  **Expected PASS:** 22 passed. Then confirm nothing else moved:

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q
  ```

- [ ] **Step 7: Commit.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && git add src/facts/budgets.py src/facts/resolver.py tests/p6/test_p6_budgets.py && git commit -m "feat(P6): §8.6's three model ceilings, the degradation order, and the resolver that subtracts rather than substitutes"
  ```

---
