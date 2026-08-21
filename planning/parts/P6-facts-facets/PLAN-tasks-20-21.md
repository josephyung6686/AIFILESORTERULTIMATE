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
      resolve(a_resolver(recorder, llm=recorder.stage("llm")), p6)
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
      # §8.6: "mark the deferred stage, and leave the file or group in review rather
      # than guessing", which "avoids the false impression that an unprocessed file
      # was understood and found unimportant". The row records which producers had
      # already run, so a reader can see the work stopped rather than concluded.
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
      # The producers arrive as injected `Stage` callables. Importing one here would
      # put a build-order edge inside a wave that has none, and would let a threshold,
      # a gazetteer or a regex catalogue reach this module through a sibling.
      allowed = {"facts.budgets", "facts.unresolved", "facts.resolver"}
      from_facts = {module for module in
                    (getattr(value, "__module__", None)
                     for value in vars(resolver_module).values())
                    if module and module.startswith("facts.")}
      assert from_facts <= allowed
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

  **Expected PASS:** 26 passed. Then confirm nothing else moved:

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q
  ```

- [ ] **Step 7: Commit.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && git add src/facts/budgets.py src/facts/resolver.py tests/p6/test_p6_budgets.py && git commit -m "feat(P6): §8.6's three model ceilings, the degradation order, and the resolver that subtracts rather than substitutes"
  ```

---

### Task 21: §8.5 / B7 — the `factual_validation` envelope, through P2's live writer

**Files:** create `src/facts/stage_output.py`; test `tests/p6/test_p6_stage_output.py`.

**Interfaces:**
- Consumes: `eval_harness.vocabulary.STAGE_IDS`, `OUTCOMES`, `BUDGET_STATES`, `DIMENSIONS`,
  `check_stage`, `check_dimension`; `eval_harness.replay.StageResult`;
  `eval_harness.stage_output.record_stage_output`, `DimensionValue`;
  `evidence_shape.store.runs_for_content`; `evidence_shape.canonical.canonical_json`;
  `facts.resolver.ResolveResult`.
- Produces: `STAGE_ID: str` (`"factual_validation"`), `DIMENSION: str` (`"fact"`),
  `ENVELOPE_FIELDS: tuple[str, ...]`, `UnsettledOutcome`,
  `fact_stage_output(*, result: ResolveResult) -> dict`,
  `fact_version_axes(conn, *, content_hash: str, model_identifier: str | None,
  prompt_fingerprint: str | None) -> dict`.

**Done-means:** 20 (the outcome half), 21.

---

**Two vocabularies that look like one, and the module exists partly to keep them apart.** P2 publishes
ten `STAGE_IDS` and ten `DIMENSIONS`, and they are **different lists**. Verified live:
`"factual_validation"` is `STAGE_IDS[1]`; `"fact"` is `DIMENSIONS[1]`. `check_stage("fact")` raises
`UnknownStage`; `check_dimension("factual_validation")` raises `UnknownDimension`. P6 spells each
once, in this module, and the test asserts the cross-substitution raises rather than silently
recording under the wrong name.

**The envelope is produced, not stored.** `eval_harness.replay.StageResult` is what a stage adapter
returns; P2 adds `run_id`, `stage_id` and `version_tuple_ref` from the run it is replaying. P5's
`extractors/stage_output.py` set this pattern and this module follows it, with one deliberate
difference: **P6 fills `values`**, and P5 does not. `StageResult`'s sixth field is
`values: Sequence[DimensionValue] = <factory>`, and §8.5's `fact` dimension is P6's to measure, so
`ENVELOPE_FIELDS` here is the **six** `StageResult` fields rather than P5's five.

**`inputs[]`, resolved against P5 as built rather than against a reading of the SPEC.** The SPEC says
`inputs[]` carries *"the `subject_ref`s of the `extraction` stage outputs it consumed"*.
`extractors.stage_output.extraction_stage_output` sets `"subject_ref": run["file_id"]` — read from
the live module, not inferred. So P6's `inputs` is `(file_id,)` while P6's own `subject_ref` is the
**content hash** (§8.2's identity for a file version). The two differ on purpose, and the test asserts
the P5 half rather than restating it, so a future change to P5's subject key breaks this test instead
of quietly mis-linking the two stages.

**No fact id goes in the payload.** §8.5 replays a bundle and diffs the stored forms. A `fact_id` is
minted per row and is not stable across two runs of the same corpus, so putting one in the payload
would make every replay report a divergence that is not one. The payload carries a **count** and the
reason histogram — everything §8.5's "Fact quality: did it abstain when evidence was absent?" needs,
and nothing that changes between two identical runs.

> **NEEDS-JOSEPH (new, found while writing this task): the §8.5 outcome table has no row for a
> privacy-only refusal, and P2's live writer makes the obvious candidates unreachable.**
>
> The SPEC's table has four reachable rows. Its `abstained` row is defined as *"every attempted field
> ended in an `unresolved` row with a **non-budget** reason"*, which would sweep `privacy_withheld`
> into `abstained`. But the SPEC's own `unresolved` rule 4 says the opposite in the same document:
> *"`budget_deferred` and `privacy_withheld` are **not** abstentions … conflating them would report a
> budget stop as a considered refusal."* And `deferred` is not available either: P2's
> `record_stage_output` raises `ValueError` unless `budget_state == "ceiling_reached"`, and a privacy
> stop reaches no ceiling.
>
> So a file that produced **zero** facts and whose only refusals are `privacy_withheld` has no
> representable outcome. That is a real gap between two ratified documents, not a choice this task
> may make, so it is **held open as a raise**: `UnsettledOutcome`, naming the question. Three things
> keep that from being reckless:
> - The case is narrow. `privacy_withheld` is written only when an LLM **stage exists** and a
>   handling class bars it. With P8 absent — Done-means 17's world, and today's — `stages["llm"]` is
>   `None`, the route does not exist, nothing is withheld, and this branch is unreachable.
> - Any field reachable by `direct` or `rule` is still answered, so a privacy bar with **any** fact
>   written reports `produced` and never reaches the raise.
> - Raising is this project's stated tie-break: *"the one that preserves more information, or that
>   makes a wrong outcome impossible rather than merely unlikely, wins"* — `planning/10-i4-learning-ops.md`,
>   verified by grep. (The skeleton's Task 19 attributes this sentence to `04-resolutions.md` **and**
>   `10-i4-learning-ops.md`; it is only in the latter. Reported, not fixed here — the skeleton is not
>   this task's file.) Recording a prohibition as a considered refusal is the wrong outcome the SPEC
>   names in words; a raise forces the decision instead of writing it.
>
> **Do not resolve this by picking an outcome.** Two candidate resolutions exist and both are
> Joseph's: add a `withheld` outcome to P2's five, or rule that `privacy_withheld` **is** an
> abstention for envelope purposes while remaining a non-abstention in the `unresolved` vocabulary.

---

- [ ] **Step 1: Read P2's live writer and P5's precedent — both, before writing anything.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -c "
  import inspect
  from eval_harness.vocabulary import STAGE_IDS, DIMENSIONS, OUTCOMES, BUDGET_STATES
  print('stage :', STAGE_IDS.index('factual_validation'), STAGE_IDS[1])
  print('dim   :', DIMENSIONS.index('fact'), DIMENSIONS[1])
  print('out   :', OUTCOMES); print('budget:', BUDGET_STATES)
  from eval_harness.replay import StageResult
  print('StageResult:', inspect.signature(StageResult))
  from eval_harness.stage_output import record_stage_output, DimensionValue
  print('record_stage_output:', inspect.signature(record_stage_output))
  print('DimensionValue:', inspect.signature(DimensionValue))
  from eval_harness.run import VERSION_AXES, VERSION_TUPLE_FIELDS
  print('axes:', VERSION_AXES); print('tuple:', VERSION_TUPLE_FIELDS)
  from extractors.stage_output import extraction_stage_output
  print('P5 subject_ref is the', 'file_id' if 'file_id' in inspect.getsource(extraction_stage_output) else '???')
  "
  ```

  Expected: `factual_validation` at index 1 of `STAGE_IDS`; `fact` at index 1 of `DIMENSIONS`;
  `OUTCOMES == ("produced","abstained","deferred","not_implemented","error")`;
  `BUDGET_STATES == ("within_ceiling","ceiling_reached")`;
  `StageResult(subject_ref, outcome, payload, inputs, budget_state, values=...)`;
  `VERSION_TUPLE_FIELDS` is seven, `VERSION_AXES` is six.

- [ ] **Step 2: Write the test file, complete.**

  Create `tests/p6/test_p6_stage_output.py`:

  ```python
  # tests/p6/test_p6_stage_output.py
  """§8.5 / B7 — P6's envelope, driven through P2's LIVE writer.

  Nothing here is asserted against a reconstruction of P2. Every outcome pairing goes
  into `eval_harness.stage_output.record_stage_output` and is read back out of the
  `stage_output` table, because B7's claim is that a budget stop and a considered
  refusal are "distinguishable from the records alone" — which is a claim about rows,
  not about a mapping table.
  """
  from __future__ import annotations

  import json

  import pytest

  from eval_harness.replay import StageResult
  from eval_harness.run import (
      VERSION_AXES, VERSION_TUPLE_FIELDS, record_version_tuple, start_run,
  )
  from eval_harness.stage_output import (
      DimensionValue, dimension_values, record_stage_output, stage_outputs,
  )
  from eval_harness.store import create_eval_schema
  from eval_harness.vocabulary import (
      BUDGET_STATES, DIMENSIONS, OUTCOMES, STAGE_IDS, UnknownDimension, UnknownStage,
      check_dimension, check_stage,
  )
  from evidence_shape.fixtures import by_number
  from evidence_shape.schema import create_evidence_schema
  from evidence_shape.store import record_run

  from extractors.stage_output import extraction_stage_output

  import facts.stage_output as stage_output_module
  from facts.resolver import ResolveResult
  from facts.stage_output import (
      DIMENSION, ENVELOPE_FIELDS, STAGE_ID, UnsettledOutcome, fact_stage_output,
      fact_version_axes,
  )

  FILE_ID = "file-01"
  #: Fixture 1's content hash, so the P4 half of this file uses the real one.
  CONTENT_HASH = "042896dc1966b8a6214e5383aba5b8b931cfa049d17aafa37eb8a77c859b95da"
  #: Three more file VERSIONS. P2's `stage_dimension_value` is keyed
  #: `(run_id, dimension, subject_ref)` — verified by execution, it raises
  #: `IntegrityError` on a second `fact` value for one subject in one run — so two
  #: results emitted into the same run must be two different subjects. That is P2
  #: enforcing "one envelope per subject P6 decides about", not a test convenience.
  CONTENT_HASH_B = "b" * 64
  CONTENT_HASH_C = "c" * 64
  CONTENT_HASH_D = "d" * 64


  def a_result(**overrides) -> ResolveResult:
      base = dict(file_id=FILE_ID, content_hash=CONTENT_HASH,
                  stages_run=("direct", "rule"))
      base.update(overrides)
      return ResolveResult(**base)


  PRODUCED = a_result(fact_ids=("fact-1",))
  ABSTAINED = a_result(content_hash=CONTENT_HASH_B,
                       reason_counts={"no_candidate_evidence": 2,
                                      "below_margin": 1})
  DEFERRED = a_result(content_hash=CONTENT_HASH_C,
                      reason_counts={"budget_deferred": 3},
                      stages_barred={"llm": "budget"},
                      deferred_against=("model.max_cost_per_scan",))
  ERRORED = ResolveResult.errored(file_id=FILE_ID, content_hash=CONTENT_HASH_D,
                                  error="rules.apply_rules: boom")


  @pytest.fixture()
  def p2_run(conn):
      """A live P2 run. Mirrors `tests/p5/test_p5_stage_output.py` exactly."""
      create_eval_schema(conn)
      ref = record_version_tuple(
          conn, extractor_versions={"pdf.text": "1.0.0"}, graph_algorithm_version=None,
          prompt_fingerprint=None, model_identifier=None,
          template_library_version=None, placement_scorer_version=None,
          analysis_tiers_enabled=["filesystem", "native"])
      run_id = start_run(conn, bundle_id="b-p6", run_kind="replay",
                         version_tuple_ref=ref, budget_ceilings={},
                         run_settings={"model_enabled": False,
                                       "embeddings_enabled": False},
                         pinned_plan_id=None, pinned_plan_version=None)
      return run_id, ref


  def emit(conn, p2_run, result: ResolveResult) -> int:
      run_id, ref = p2_run
      envelope = fact_stage_output(result=result)
      return record_stage_output(
          conn, run_id=run_id, stage_id=envelope["stage_id"],
          subject_ref=envelope["subject_ref"], outcome=envelope["outcome"],
          payload=envelope["payload"], version_tuple_ref=ref,
          inputs=envelope["inputs"], budget_state=envelope["budget_state"],
          dimension_values=envelope["values"])


  # --- two vocabularies that look like one --------------------------------------

  def test_the_stage_id_is_one_of_section_8_5s_ten():
      assert STAGE_ID == "factual_validation"
      assert STAGE_ID in STAGE_IDS
      assert check_stage(STAGE_ID) == STAGE_ID


  def test_the_dimension_is_fact_and_the_two_lists_are_not_interchangeable():
      assert DIMENSION == "fact"
      assert DIMENSION in DIMENSIONS
      assert DIMENSION not in STAGE_IDS
      assert STAGE_ID not in DIMENSIONS
      with pytest.raises(UnknownStage):
          check_stage(DIMENSION)
      with pytest.raises(UnknownDimension):
          check_dimension(STAGE_ID)


  # --- the envelope shape --------------------------------------------------------

  def test_the_envelope_is_exactly_p2s_stage_result_shape():
      envelope = fact_stage_output(result=PRODUCED)
      assert set(ENVELOPE_FIELDS) == set(envelope) - {"stage_id"}
      StageResult(**{k: v for k, v in envelope.items() if k != "stage_id"})


  def test_p6_fills_values_where_p5_does_not_because_the_fact_dimension_is_p6s():
      assert "values" in ENVELOPE_FIELDS
      envelope = fact_stage_output(result=PRODUCED)
      assert [value.dimension for value in envelope["values"]] == [DIMENSION]


  def test_subject_ref_is_the_content_hash_because_a_fact_is_per_file_version():
      assert fact_stage_output(result=PRODUCED)["subject_ref"] == CONTENT_HASH


  def test_inputs_carries_the_subject_refs_of_the_extraction_stage_outputs():
      # Asserted against P5 AS BUILT: `extraction_stage_output` keys its subject by
      # file id, so P6's `inputs[]` must be file ids even though P6's own subject is
      # the content hash. Reading P5's live envelope here means a change on that side
      # breaks this test instead of quietly mis-linking two stages.
      p5_envelope = extraction_stage_output(run={
          "file_id": FILE_ID, "content_hash": CONTENT_HASH,
          "extractor_name": "pdf.text", "extractor_version": "1.0.0",
          "source_type": "text_document", "analysis_tier": "native",
          "completeness": "complete", "observation_count": 3,
          "coverage": {"units": "pages", "processed": 1, "total": 1}})
      assert p5_envelope["subject_ref"] == FILE_ID
      assert fact_stage_output(result=PRODUCED)["inputs"] == (p5_envelope["subject_ref"],)


  # --- the four outcomes ---------------------------------------------------------

  def test_facts_written_is_produced_within_ceiling():
      envelope = fact_stage_output(result=PRODUCED)
      assert (envelope["outcome"], envelope["budget_state"]) == \
          ("produced", "within_ceiling")


  def test_evidence_based_refusal_is_abstained_within_ceiling():
      envelope = fact_stage_output(result=ABSTAINED)
      assert (envelope["outcome"], envelope["budget_state"]) == \
          ("abstained", "within_ceiling")


  def test_a_ceiling_is_deferred_ceiling_reached():
      envelope = fact_stage_output(result=DEFERRED)
      assert (envelope["outcome"], envelope["budget_state"]) == \
          ("deferred", "ceiling_reached")


  def test_a_ceiling_outranks_facts_because_deferred_work_must_be_visible_as_deferred():
      # §00: the product must avoid "the false impression that an unprocessed file was
      # understood and found unimportant". A run that wrote two facts AND hit a ceiling
      # reports `deferred`; reporting `produced` would hide the unfinished half.
      mixed = a_result(fact_ids=("fact-1", "fact-2"),
                       reason_counts={"budget_deferred": 1},
                       stages_barred={"llm": "budget"},
                       deferred_against=("model.max_dossier_tokens_per_call",))
      envelope = fact_stage_output(result=mixed)
      assert (envelope["outcome"], envelope["budget_state"]) == \
          ("deferred", "ceiling_reached")


  def test_the_stage_failed_is_error():
      envelope = fact_stage_output(result=ERRORED)
      assert envelope["outcome"] == "error"
      assert envelope["budget_state"] in BUDGET_STATES


  def test_every_outcome_p6_can_emit_is_one_of_p2s_five():
      for result in (PRODUCED, ABSTAINED, DEFERRED, ERRORED):
          assert fact_stage_output(result=result)["outcome"] in OUTCOMES


  # --- through P2's live writer --------------------------------------------------

  def test_produced_and_abstained_are_written_and_read_back(conn, p2_run):
      emit(conn, p2_run, PRODUCED)
      emit(conn, p2_run, ABSTAINED)
      rows = stage_outputs(conn, p2_run[0], stage_id=STAGE_ID)
      assert [row["outcome"] for row in rows] == ["produced", "abstained"]
      assert {row["budget_state"] for row in rows} == {"within_ceiling"}
      assert {row["subject_ref"] for row in rows} == {CONTENT_HASH, CONTENT_HASH_B}
      assert json.loads(rows[0]["inputs"]) == [FILE_ID]


  def test_the_two_are_distinguishable_from_the_records_alone(conn, p2_run):
      # Done-means 20. Nothing in this assertion consults P6: the reader has the
      # `stage_output` rows and only those.
      emit(conn, p2_run, ABSTAINED)
      emit(conn, p2_run, DEFERRED)
      rows = stage_outputs(conn, p2_run[0], stage_id=STAGE_ID)
      pairs = [(row["outcome"], row["budget_state"]) for row in rows]
      assert pairs == [("abstained", "within_ceiling"),
                       ("deferred", "ceiling_reached")]
      deferred_payload = json.loads(rows[1]["payload"])
      assert deferred_payload["unresolved_reasons"] == {"budget_deferred": 3}
      assert deferred_payload["deferred_against"] == ["model.max_cost_per_scan"]


  def test_p2s_writer_refuses_the_pairing_p6_must_never_emit(conn, p2_run):
      # P6 does not need to invent B7's rule; it needs to not fight it. Proof that the
      # rule is live rather than remembered.
      run_id, ref = p2_run
      with pytest.raises(ValueError):
          record_stage_output(conn, run_id=run_id, stage_id=STAGE_ID,
                              subject_ref=CONTENT_HASH, outcome="abstained",
                              payload=None, version_tuple_ref=ref, inputs=(FILE_ID,),
                              budget_state="ceiling_reached")
      with pytest.raises(ValueError):
          record_stage_output(conn, run_id=run_id, stage_id=STAGE_ID,
                              subject_ref=CONTENT_HASH, outcome="deferred",
                              payload=None, version_tuple_ref=ref, inputs=(FILE_ID,),
                              budget_state="within_ceiling")


  def test_an_envelope_is_emitted_for_a_file_that_produced_facts_and_for_one_that_did_not(conn, p2_run):
      # Done-means 21, both halves, in one run.
      emit(conn, p2_run, PRODUCED)
      emit(conn, p2_run, ABSTAINED)
      rows = stage_outputs(conn, p2_run[0], stage_id=STAGE_ID)
      assert len(rows) == 2
      assert all(row["version_tuple_ref"] == p2_run[1] for row in rows)


  def test_the_dimension_value_lands_under_fact_and_carries_its_own_outcome(conn, p2_run):
      emit(conn, p2_run, PRODUCED)
      values = dimension_values(conn, p2_run[0], dimension=DIMENSION)
      assert len(values) == 1
      assert values[0]["stage_id"] == STAGE_ID
      assert values[0]["subject_ref"] == CONTENT_HASH
      assert values[0]["outcome"] == "produced"
      assert json.loads(values[0]["value"]) == {"fact_count": 1, "unresolved_count": 0}


  def test_a_dimension_value_with_nothing_produced_is_null(conn, p2_run):
      emit(conn, p2_run, ABSTAINED)
      values = dimension_values(conn, p2_run[0], dimension=DIMENSION)
      assert values[0]["outcome"] == "abstained"
      assert values[0]["value"] is None


  # --- the payload ---------------------------------------------------------------

  def test_the_payload_is_p6s_own_and_carries_no_fact_id():
      # §8.5 diffs STORED FORMS across two runs. A `fact_id` is minted per row and is
      # not stable between two runs of the same corpus, so one in the payload would
      # report a divergence that is not one.
      payload = json.loads(fact_stage_output(result=PRODUCED)["payload"])
      assert payload["fact_count"] == 1
      assert "fact-1" not in fact_stage_output(result=PRODUCED)["payload"]
      assert set(payload) == {"fact_count", "unresolved_reasons", "stages_run",
                              "stages_barred", "deferred_against", "error"}


  def test_the_payload_is_byte_stable_for_the_same_result():
      first = fact_stage_output(result=DEFERRED)["payload"]
      second = fact_stage_output(result=a_result(
          content_hash=CONTENT_HASH_C, reason_counts={"budget_deferred": 3},
          stages_barred={"llm": "budget"},
          deferred_against=("model.max_cost_per_scan",)))["payload"]
      assert first == second


  # --- the two refusals this module makes ----------------------------------------

  def test_a_privacy_only_refusal_has_no_settled_outcome_and_is_held_open():
      # NEEDS-JOSEPH, stated in this task's preamble: the §8.5 table would call this
      # `abstained`, the SPEC's `unresolved` rule 4 forbids exactly that, and P2's
      # writer makes `deferred` unreachable without a ceiling. Held open as a raise.
      withheld = a_result(reason_counts={"privacy_withheld": 2},
                          stages_barred={"llm": "privacy"})
      with pytest.raises(UnsettledOutcome):
          fact_stage_output(result=withheld)


  def test_a_privacy_bar_that_still_produced_a_fact_reports_produced():
      # The raise is narrow: any field reachable by `direct` or `rule` is still
      # answered, and P8 absent means nothing is ever withheld at all.
      partial = a_result(fact_ids=("fact-1",),
                         reason_counts={"privacy_withheld": 1},
                         stages_barred={"llm": "privacy"})
      assert fact_stage_output(result=partial)["outcome"] == "produced"


  def test_a_result_with_no_record_at_all_is_refused():
      # B7's whole point: without the `unresolved` row, §3.6's "no fact" is a missing
      # row and P2 cannot tell a considered refusal from a crash or a skip. A result
      # with neither a fact nor a reason is that missing row, and it is a bug in the
      # producer, not an outcome to report.
      with pytest.raises(ValueError):
          fact_stage_output(result=a_result())


  # --- P6's slice of the version tuple -------------------------------------------

  @pytest.fixture()
  def p4_run(conn):
      create_evidence_schema(conn)
      record_run(conn, by_number(1).run)
      return by_number(1).run


  def test_fact_version_axes_supplies_p6s_three_and_assembles_no_tuple(conn, p4_run):
      axes = fact_version_axes(conn, content_hash=p4_run.content_hash,
                               model_identifier=None, prompt_fingerprint=None)
      assert set(axes) == {"extractor_versions", "model_identifier",
                           "prompt_fingerprint"}
      assert set(axes) < set(VERSION_AXES)
      assert axes["extractor_versions"] == {"pdf.text": "1.0.0"}


  def test_the_axes_merge_into_p2s_seven_field_tuple(conn, p4_run):
      create_eval_schema(conn)
      axes = fact_version_axes(conn, content_hash=p4_run.content_hash,
                               model_identifier="claude-x", prompt_fingerprint="sha256:ab")
      ref = record_version_tuple(
          conn, graph_algorithm_version=None, template_library_version=None,
          placement_scorer_version=None, analysis_tiers_enabled=["native"], **axes)
      assert ref.startswith("sha256:")
      assert set(axes) <= set(VERSION_TUPLE_FIELDS)


  def test_two_versions_of_one_extractor_are_refused_rather_than_resolved(conn):
      # §3.4's cache key is per (extractor, version) and a map cannot hold both, so a
      # caller comparing two extractor versions is comparing two runs. Same rule P5
      # states on its own half of this axis.
      import dataclasses
      create_evidence_schema(conn)
      run = by_number(1).run
      record_run(conn, run)
      record_run(conn, dataclasses.replace(run, run_id="run-01b",
                                           extractor_version="2.0.0"))
      with pytest.raises(ValueError):
          fact_version_axes(conn, content_hash=run.content_hash,
                            model_identifier=None, prompt_fingerprint=None)


  def test_the_module_defines_no_number():
      numbers = {name: value for name, value in vars(stage_output_module).items()
                 if not name.startswith("_") and not isinstance(value, bool)
                 and isinstance(value, (int, float))}
      assert numbers == {}
  ```

- [ ] **Step 3: Run it and read the failure.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest tests/p6/test_p6_stage_output.py -q
  ```

  **Expected FAILURE:** collection error —
  `ModuleNotFoundError: No module named 'facts.stage_output'`. One error, zero tests.

- [ ] **Step 4: Write `src/facts/stage_output.py`, complete.**

  ```python
  # src/facts/stage_output.py
  """§8.5 / B7 — P2's envelope, produced by P6 and stored by P2.

  "P6 emits a `stage_output` with `stage_id = factual_validation`, a populated
  `inputs[]`, and the version tuple, for a file that produced facts and for a file
  that produced none."

  Produced, not stored: `eval_harness.replay.StageResult` is the shape a stage adapter
  returns, and P2 adds `run_id`, `stage_id` and `version_tuple_ref` from the run it is
  replaying. P5's `extractors/stage_output.py` set this pattern; this module follows it
  with one deliberate difference — P6 fills `values`, because §8.5's `fact` dimension is
  P6's to measure and P5 has no dimension of its own to report here.

  TWO VOCABULARIES THAT LOOK LIKE ONE. P2 publishes ten `STAGE_IDS` and ten
  `DIMENSIONS` and they are different lists: P6's stage is `factual_validation`, P6's
  dimension is `fact`, and each raises under the other's checker. They are spelled here
  and nowhere else in `facts`.
  """
  from __future__ import annotations

  import sqlite3

  from evidence_shape.canonical import canonical_json
  from evidence_shape.store import runs_for_content

  from eval_harness.stage_output import DimensionValue
  from eval_harness.vocabulary import check_dimension, check_stage

  from facts.resolver import ResolveResult

  #: Stage 2 of §8.5's ten. Checked at import, so a P2 rename is a startup failure.
  STAGE_ID: str = check_stage("factual_validation")

  #: §8.5's `fact` dimension — NOT the stage id, and not interchangeable with it.
  DIMENSION: str = check_dimension("fact")

  #: `eval_harness.replay.StageResult`'s six fields, as P6 fills them. P5 fills five;
  #: the sixth is `values`, and it is P6's because the `fact` dimension is P6's.
  ENVELOPE_FIELDS: tuple[str, ...] = ("subject_ref", "outcome", "payload", "inputs",
                                      "budget_state", "values")


  class UnsettledOutcome(Exception):
      """A result whose §8.5 outcome the design does not settle.

      One case only: zero facts, at least one `privacy_withheld` refusal, and no
      ceiling. The §8.5 table would call it `abstained`; the SPEC's `unresolved`
      rule 4 says `privacy_withheld` is not an abstention; and P2's writer refuses
      `deferred` without `ceiling_reached`. NEEDS-JOSEPH — see this task's preamble.
      Unreachable while P8 is absent, because a route that does not exist is not a
      route that was barred.
      """


  def fact_stage_output(*, result: ResolveResult) -> dict:
      """One envelope for one `(file_id, content_hash)` P6 decided about.

      `subject_ref` is the CONTENT HASH — §8.2's identity for a file version, and the
      thing a fact is keyed by. `inputs` is the file id, because that is what P5's
      `extraction` stage keys its own subject by (`extractors.stage_output`), and
      §8.5 links the two stages by that ref.
      """
      unresolved_count = sum(result.reason_counts.values())
      outcome, budget_state = _outcome_for(result, unresolved_count=unresolved_count)
      payload = canonical_json({
          # No fact id: §8.5 diffs stored forms across runs and a minted id is not
          # stable between two runs of the same corpus.
          "fact_count": len(result.fact_ids),
          "unresolved_reasons": dict(result.reason_counts),
          "stages_run": list(result.stages_run),
          "stages_barred": dict(result.stages_barred),
          "deferred_against": list(result.deferred_against),
          "error": result.error,
      })
      value = ({"fact_count": len(result.fact_ids),
                "unresolved_count": unresolved_count}
               if outcome == "produced" else None)
      return {
          "stage_id": STAGE_ID,
          "subject_ref": result.content_hash,
          "outcome": outcome,
          "payload": payload,
          "inputs": (result.file_id,),
          "budget_state": budget_state,
          "values": (DimensionValue(dimension=DIMENSION,
                                    subject_ref=result.content_hash,
                                    outcome=outcome, value=value),),
      }


  def _outcome_for(result: ResolveResult, *, unresolved_count: int) -> tuple[str, str]:
      """The §8.5 table, in the one order that keeps unfinished work visible.

      The ceiling is checked BEFORE the facts. A run that wrote two facts and then hit
      a ceiling reports `deferred`: §8.6 says to "mark the deferred stage, and leave
      the file or group in review rather than guessing", and `produced` would hide the
      half that never ran. This is not a widening of the SPEC's first row — that row
      already reads `within_ceiling`.
      """
      if result.error is not None:
          return "error", ("ceiling_reached" if result.deferred_against
                           else "within_ceiling")
      if result.deferred_against:
          return "deferred", "ceiling_reached"
      if result.fact_ids:
          return "produced", "within_ceiling"
      if result.reason_counts.get("privacy_withheld"):
          raise UnsettledOutcome(
              "zero facts and a privacy-withheld refusal has no §8.5 outcome: the "
              "table would say 'abstained', the SPEC's unresolved rule 4 forbids it, "
              "and P2 refuses 'deferred' without a ceiling. NEEDS-JOSEPH."
          )
      if unresolved_count:
          return "abstained", "within_ceiling"
      raise ValueError(
          "a result with no fact and no `unresolved` row is the missing row B7 exists "
          "to forbid: P2 cannot tell a considered refusal from a crash or a skip"
      )


  def fact_version_axes(conn: sqlite3.Connection, *, content_hash: str,
                        model_identifier: str | None,
                        prompt_fingerprint: str | None) -> dict:
      """P6's three axes of §8.5's seven-field version tuple.

      P6 SUPPLIES axes; it does not assemble the tuple — the other four belong to P9,
      P10, P11 and the caller, and `eval_harness.run.record_version_tuple` refuses a
      partial one. The caller merges these three in.

      `extractor_versions` is P6's slice of P4's runs for this content hash. Two
      versions of one extractor in one tuple is refused rather than resolved: §3.4's
      cache key is per (extractor, version) and a map cannot hold both, so a caller
      comparing two extractor versions is comparing two runs.
      """
      versions: dict[str, str] = {}
      for run in runs_for_content(conn, content_hash):
          name, version = run.extractor_name, run.extractor_version
          if versions.get(name, version) != version:
              raise ValueError(
                  f"{name!r} appears at two versions, {versions[name]!r} and "
                  f"{version!r}; §8.5's tuple holds one version per extractor"
              )
          versions[name] = version
      return {
          "extractor_versions": versions,
          "model_identifier": model_identifier,
          "prompt_fingerprint": prompt_fingerprint,
      }
  ```

- [ ] **Step 5: Run it and read the pass.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest tests/p6/test_p6_stage_output.py -q
  ```

  **Expected PASS:** 27 passed. Then the whole suite, which must be unchanged apart from
  the two new files:

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q
  ```

- [ ] **Step 6: Commit.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && git add src/facts/stage_output.py tests/p6/test_p6_stage_output.py && git commit -m "feat(P6): the factual_validation envelope through P2's live writer, and the privacy-only outcome held open"
  ```
