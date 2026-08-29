# Round 2 — buildability

Date: 2026-08-21 (overnight)
Lens: **could an engineer who has never seen this project execute these, task by task, without asking a question?**
Subjects: [`../../parts/P6-facts-facets/PLAN-SKELETON.md`](../../parts/P6-facts-facets/PLAN-SKELETON.md) (1,621 lines, 27 tasks) ·
[`../../parts/P7-privacy-consent-gate/PLAN-SKELETON.md`](../../parts/P7-privacy-consent-gate/PLAN-SKELETON.md) (1,370 lines, 22 tasks)
Standard: [`../../parts/P4-evidence-shape/PLAN.md`](../../parts/P4-evidence-shape/PLAN.md) · [`../../parts/P5-extractors/PLAN.md`](../../parts/P5-extractors/PLAN.md)
Prior round read and not repeated: [`round-1-fidelity.md`](round-1-fidelity.md)

Method: both plans' `Files:` and `Interfaces:` blocks parsed mechanically into a dependency graph
(89 internal edges, resolved against the module each name is created in). Every external surface
either plan cites imported and checked with `inspect.signature` / `dataclasses.fields` / `len()`.
Repo-wide claims checked by `ast` walk, never by scanning source text. **The Task 26 mechanism was
run**: the raising verdict and the loop-3 re-entry were both executed against the built orchestrator
with the live Wave-2 harness. Baseline confirmed this pass: `python3 -m pytest tests -q` →
**1,237 passed in 8.0s**. `src/` and `tests/` were not modified.

---

## Verdict

**An engineer can execute P7 essentially as written, and cannot execute P6 without four additions
and one rewrite.** That asymmetry is the headline and it is not a matter of taste: P7's 45 internal
dependency edges all point backwards, every file in its File Structure is created by a task, its
`conftest.py` and its schema module each have an owner, and each of its eight event types was
verified present in P1's registry. P6's 44 edges also resolve — there is **no undefined internal
name and no numeric forward reference among the named symbols in either plan**, which is a better
result than this project's history predicts — but P6's *file* graph does not close: `src/facts/schema.py`
is modified by five tasks and created by none, `tests/p6/conftest.py` is named in the File Structure
and created by no task, `ResolveResult` is consumed by two tasks and defined by none, and the two
injected seams the plan's own prose requires (P7's `handling_class`, P8's `propose`/`validate`)
appear in no task's `Interfaces` block at all — which leaves `privacy_withheld`, one of the SPEC's
thirteen `unresolved` reasons, with no writer anywhere in twenty-seven tasks.

**The single biggest blocker is P6 Task 26, and it is worse than under-specified — the mechanism it
states is wrong, and I proved it by running it.** Task 26 says loop 1 passes "a verdict that raises
`FactPassNotRun`". `orchestrator._extract_one` catches `Exception` and converts it to
`failed_result(...)`. Executed against the live harness, a raising verdict produced
`pdf.text · analysis_tier=native · completeness=failed`, with `FactPassNotRun` recorded as the
failure reason, and **the exception never propagated**. Every text-bearing PDF in a real corpus
becomes a failed native extraction, silently — and the test Task 26 states to catch exactly this
("injecting a verdict that raises `FactPassNotRun` and running a full corpus **without it firing**")
has no channel through which to observe the firing, because the swallow is upstream of it. The
second half fails the same way: `extractors.dispatch` publishes exactly two public functions,
`extract` and `current_versions` — `_ocr` is private and the orchestrator does not import it — so
loop 3 has **no targeted-OCR entry point**, and re-entering `extract()` (executed) produces a
duplicate `pdf.text` native run and zero OCR runs. The plan's claim that "with `readers.ocr_engine is
None` … loops 3 and 4 are no-ops and the restructure costs nothing" is false for precisely the files
the restructure exists to serve.

One caveat on scope, stated so the findings below are read at the right altitude: **the skeletons say
outright that they are not the plans** ("Every task below still needs its **complete** test code and
its **complete** implementation code"). I have therefore judged them as decompositions — could the
author of one task, seeing only that task's block, write the detail pass against neighbours they
cannot read? Where the answer is "yes, after opening the SPEC," that is not a finding, and I withdrew
two candidates on that basis (P7 Task 2's vocabularies and P6 Task 5's thirteen `unresolved` reasons
are both enumerated in their SPECs — `P7 SPEC:100-110` and `P6 SPEC:341-354` — and I confirmed both
before dropping them).

---

## Findings, most severe first

### B-1 (CRITICAL) — P6 Task 26's loop-1 mechanism converts every text-bearing PDF into a `failed` run, and the test that should catch it is blind

**Plan:** `PLAN-SKELETON.md:1207` (loop 1), `:1222` (the test), `:1532` (the shape table's "passes a
verdict that raises `FactPassNotRun` in loop 1").

**What an implementer hits.** The call chain is
`orchestrator._extract_one` (`src/orchestrator.py:131`) → `extractors.dispatch.extract`
(`src/extractors/dispatch.py:96`) → `ocr_policy.document_ocr_decision` (`:106`) →
`text_layer_state` (`:91`) → `no_usable_facts(file_id, content_hash)` (`:101`). Nothing in that
chain catches. `_extract_one` does:

```python
    except (ProtectedContainerRefused, DatalessRefused):
        raise
    except Exception as error:                       # noqa: BLE001 -- see docstring
        return (failed_result(...),), ()
```

`FactPassNotRun` is not in the re-raise tuple, so it lands in the blanket handler.

**Executed, against the live Wave-2 harness** (`tests/wave2/test_wave2_orchestrator.py`'s own `go()`,
reused verbatim, with `no_usable_facts` raising):

```text
  verdict consulted for: ['b7396e97-d887-456c-8156-48da4fe63e17']
  --- runs written ---
    filesystem.record      completeness=complete     tier=filesystem
    filesystem.record      completeness=complete     tier=filesystem
    pdf.text               completeness=failed       tier=native   FactPassNotRun: no recorded P6 pass for b7396…
    text.structured        completeness=complete     tier=native
  FAILED RUNS: 1 of 4
```

`run_wave2` returned normally. The `failed` completeness then flows into
`extraction_status_by_tier`, into `files.extraction_status_by_tier`, and into P2's bundle — so the
corpus records a failed native extraction for every text-bearing PDF and nothing raises.

**Why the stated test cannot see it.** Task 26 asserts the order "by injecting a verdict that raises
`FactPassNotRun` and running a full corpus without it firing, which is the mechanical check that
replaces a comment." The raise *does* fire, is caught two frames up, and is written into a column the
test does not read. The test passes green while the defect is live — which is the shape of the
`lambda f, h: False` stub the whole restructure exists to remove.

**What the plan must add.** Name the loop-1 mechanism and prove it cannot be swallowed. The three
candidates and their real costs:

| Option | Cost |
|---|---|
| Add `FactPassNotRun` to `_extract_one`'s re-raise tuple | the raise now aborts the whole scan out of `run_wave2` — one bad file ends the run |
| Give `dispatch` a public `extract_native(...)` with no `no_usable_facts` parameter, and a public `extract_targeted_ocr(...)` | contradicts "`extract()` keeps its signature" and "`dispatch.py` … does not change", but is the only shape that makes loop 1 *structurally* unable to consult the verdict |
| Loop 1 passes a verdict returning `False` | is the current stub, and the plan rejects it by name |

**Recommendation:** the second. Preamble rule 5's own argument — "a correctly-implemented P6 could
not answer even if the ordering were fixed by moving the call one line; the extract step has to
**split**" — is right, and splitting the *function* is what "the extract step has to split" means.
The plan draws the split at the orchestrator and then asks a raising callable to do the work the
split was for.

**Status:** CONFIRMED — executed.

---

### B-2 (HIGH) — P6 Task 26's loop 3 has no entry point, duplicates native extraction, and erases the tier map

**Plan:** `PLAN-SKELETON.md:1210-1211` (loop 3), `:1232-1234` ("loops 3 and 4 are no-ops … the
restructure costs nothing"), `:1536` ("What does **not** change: `extract()`'s signature,
`dispatch.py` …").

**Three things an implementer hits, in order.**

1. **There is no OCR-only public function.** `ast` over `src/extractors/dispatch.py`: top-level
   defs are `['_ocr', 'extract', 'current_versions']`. `_ocr` is private and `src/orchestrator.py`
   imports neither it nor anything from `ocr_policy`. Task 26's `Consumes` names
   `extractors.dispatch.extract` and `extractors.ocr_policy.OcrDecision` — neither runs OCR alone.

2. **Re-entering `extract()` re-runs native extraction.** Executed: calling `extract(...,
   no_usable_facts=lambda f, h: True)` on an already-extracted PDF returned
   `[('pdf.text', 'native', 'complete')]` — a **second** native run at the same tier, and no OCR run,
   because `readers.ocr_engine is None` makes `_ocr` return `None` (`dispatch.py:86-88`). So loop 3
   is not a no-op with no engine; it is a duplicate-extraction loop. The claim at `:1232` is false
   for exactly the files loop 3 selects.

3. **Loop 3's `set_extraction_status` erases loop 1's map.** `src/database_agent/files_table.py`
   executes `UPDATE files SET extraction_status_by_tier = ?` — a full replace, not a merge. Loop 3
   holds only the OCR run, so `extraction_status_by_tier([ocr_run])` is `{"ocr": …}` and the
   `{"filesystem": …, "native": …}` written in loop 1 is gone. Task 26's loop 3 line reads
   "targeted OCR → `_write` → `set_extraction_status`" and says nothing about merging.

**A fourth, smaller:** `record_sensitivity_signals` (`orchestrator.py:255-260`) fires on the first
`_write` whose result carries observations. A loop-3 `extract()` returns fresh `signals`, so P5's
sensitivity signals are recorded twice for one content hash.

**What the plan must add.** The exact loop-3 call, its arguments, what it does with the existing
tier map, and what it does with `signals`. If the answer is a new public function in `dispatch`, the
"`dispatch.py` does not change" line must go.

**Status:** CONFIRMED — `ast` for (1), executed for (2), source read for (3) and (4).

---

### B-3 (HIGH) — P7 Task 21's L2 guard is red the day it is written, and the plan says it "passes trivially today"

**Plan:** `PLAN-SKELETON.md:114-121` (layer L2), `:1130-1132` (Task 21's repo-wide assertion).

**Plan says:**

> Task 21 asserts by **runtime introspection of module namespaces** that exactly one module under
> `src/privacy/` binds any of them, and that the repo-wide set of packages binding them is
> `{evidence_shape, extractors, privacy}` and nothing else. **This guard passes trivially today.**

**Live, by `ast` walk over every file in `src/`** (imports, attribute access and bare-name use of
`raw_value_at`, `text_units_for_run`, `text_unit_at`, `unit_for_observation`):

| File | defines | binds |
|---|---|---|
| `src/evidence_shape/store.py` | `text_unit_at`, `text_units_for_run`, `unit_for_observation` | — |
| `src/evidence_shape/text_units.py` | `raw_value_at` | — |
| **`src/orchestrator.py`** | — | **`from evidence_shape.store import text_units_for_run`** (line 42), used at line 317 |

Two errors, in opposite directions. **`extractors` is in the allowlist and binds none** — a member
that can never fail. **`orchestrator` binds one and is not in the allowlist** — so the guard is red
on day one, for a file P7's own Global Constraints (`:206`) forbid it from touching. The
implementer's only exits are to add `orchestrator` to the allowlist (a silent weakening of the one
guard that makes L2 mean anything when P8 lands) or to edit a file P7 does not own.

There is a third exit and it is worse: `src/orchestrator.py` is a top-level *module*, not a package,
so an implementation that walks `src/*/` directories skips it and the guard passes — vacuously, and
for a reason nobody wrote down. The plan does not say whether "packages" includes top-level modules,
and that undefined word decides whether the assertion is red or green.

**What the plan must add.** The exact set, computed against the repo rather than assumed:
`{evidence_shape, orchestrator}` today, with `privacy` added by Task 9 and `extractors` **removed**.
And a sentence stating whether the walk covers top-level modules — the honest answer is yes, because
`orchestrator.py` is the file that would otherwise carry a second materialisation locus.

**Status:** CONFIRMED — `ast` walk, printed above.

---

### B-4 (HIGH) — P6: `src/facts/schema.py` is modified by five tasks and created by none, and no task publishes a schema entry point

**Plan:** `PLAN-SKELETON.md:455` (File Structure), Tasks 2 (`:565`), 3 (`:591`), 4 (`:614`),
5 (`:640`), 19 (`:988`) — every one of them says **modify** `src/facts/schema.py`.

**What an implementer hits.** Task 2 is the first task in Wave A after the package skeleton. Its
`Files:` line says "modify `src/facts/schema.py`". The file does not exist. Task 1 creates
`__init__.py`, `authorship.py` and `states.py` and nothing else.

Worse than the missing file: **no task produces a schema entry point at all.** Task 2 produces
`create_fields(conn) -> None`; Tasks 3, 4, 5 and 19 produce no `create_*` function; there is no
`create_facts_schema(conn)` anywhere in twenty-seven `Produces` blocks. So nothing in P6 can bring
its four tables into existence in one call, which is what every one of its own tests, and every
neighbour's test, will need. P4 gave this a task of its own — Task 9, "The three tables, inside P1's
database, with P1's file untouched" (`P4 PLAN.md:3014`) — and P7 folds it into Task 5, which creates
`src/privacy/schema.py` and produces `create_privacy_schema(conn) -> None`. P6 has neither.

**What the plan must add.** A Wave-A task that creates `src/facts/schema.py` and publishes
`create_facts_schema(conn) -> None`, before Task 2 — or Task 2's `Files:` changed to **create**, with
the entry point in its `Produces` and the later four tasks stated as adding DDL to it. Either way the
`record_id` VIRTUAL projection (`:266-269`, required for `mark_superseded`, verified: `supersede_ddl`
and `evidence_shape.schema.SUPERSEDE_ADAPTER_COLUMN == "record_id"` both live) belongs in that task,
not scattered across five.

**Status:** CONFIRMED — parsed every `Files:` block; `create` and `modify` counted separately.

---

### B-5 (HIGH) — P6: `tests/p6/conftest.py` is named in the File Structure and created by no task

**Plan:** `PLAN-SKELETON.md:481`.

> `tests/p6/conftest.py             P4 fixtures, a fixed clock, injected strategies, absent P7/P8`

Twenty-seven tasks; not one lists it under `Files:`. It is **the only file in P6's File Structure
with no creating task** (checked mechanically against all 59 entries). Every other P6 test file
depends on what it contains — the P4 fixture loading, the fixed clock, the injected strategies with
no defaults, and the absent-P7/P8 stand-ins that Done-means 17 turns on.

Both comparators do this explicitly. P4 Task 1: "Create: `tests/p4/conftest.py`"
(`P4 PLAN.md:162-166`). P7 Task 1: "create `src/privacy/__init__.py`, `src/privacy/authorship.py`,
**`tests/p7/conftest.py`**" (`P7 PLAN-SKELETON.md:555`).

P6 also inherits none of P7's warning about it. P7's Global Constraints (`:210-212`) state that under
pytest's default prepend import mode with no `__init__.py` under `tests/`, every `conftest.py` is
imported as the top-level module `conftest` and the last one wins — and
`tests/wave2/test_wave2_orchestrator.py:25-28` records that this collision "cost this project a whole-suite
outage once already, in `tests/eval/`". P6 adds a twenty-eighth `conftest` to that namespace with no
task, no contents contract, and no note.

**What the plan must add.** `tests/p6/conftest.py` to Task 1's `Files:`, its fixture names to Task 1's
`Produces`, and P7's shadowing constraint copied into P6's Global Constraints.

**Status:** CONFIRMED — parsed all 59 File Structure entries against all 27 `Files:` blocks.

---

### B-6 (HIGH) — P6: the P7 and P8 injection points exist only in a prose table, so `privacy_withheld` has no writer and Task 20 cannot be written

**Plan:** `PLAN-SKELETON.md:433` (the P7 row), `:434` (the P8 row), `:1043-1047` (Task 20's
`Produces`), `:649` (Task 5's `NOT_ABSTENTIONS`).

**Plan says**, in the "What P6 consumes from P7, P8, P9 and P13" table and nowhere else:

> **P7** (§8.4) — `handling_class(file_id) -> str` … A class that forbids the model route leaves the
> field `unknown` and writes `unresolved` with `reason = privacy_withheld`
>
> **P8** (§3.3, §3.6) — `propose(request) -> tuple[Proposal, ...]` and `validate(proposal, checks) -> Verdict`

Counted over all 1,621 lines: **`handling_class` appears at `:433` and `:1352` (an OQ11 quotation) and
nowhere else. `propose(` as an injected callable appears at `:434` and nowhere else.** Neither name
occurs in any task's `Consumes` or `Produces`.

**What an implementer hits.** Task 20 builds `FactResolver`, "the one entry point, constructed with
every injected strategy and threshold", and its stated obligation is that the resolver "always
attempts `direct`, then `validated`, and only then — **budget and privacy permitting** —
`llm_supported`". There is no privacy parameter in its `Produces`, no `handling_class` in its
`Consumes`, and no P8 callable in either. The author of Task 20, reading only Task 20, has no name to
write against for two of the three rungs the task exists to sequence.

**And it reproduces the exact defect the connection contract forbids.** `privacy_withheld` is one of
the SPEC's thirteen `unresolved` reasons (`P6 SPEC:353`, "P7's handling class forbids the model
route; the field stays `unknown`"). Task 5 creates it and asserts it is in `NOT_ABSTENTIONS`. **No
task writes it**, because the only task that could has no handle on the classification.
[`22-p1-p7-connection-contract.md`](../../22-p1-p7-connection-contract.md) §5 is explicit — "Any part
added from here must carry a check that every column it publishes has a writer, or state plainly that
it does not yet" — and this is the plan publishing a vocabulary member with no producer. Round 1's
F-2 found the same class on four `fields` rows; **this is the same omission on a `reason`, and it is
the one the SPEC assigns a writer for.**

**What the plan must add.** `handling_class: Callable[[str], str]` and the P8 pair as named,
no-default constructor parameters in Task 20's `Produces` (and in Task 17's `Consumes` for the P8
half), plus a Task 20 obligation that a forbidding class writes `privacy_withheld` and never a weaker
route. Task 25's guard list should gain "every `UNRESOLVED_REASONS` member has a writing call site",
which would have caught this mechanically.

**Status:** CONFIRMED — counted every occurrence of both names across the plan; read Task 17 and
Task 20 in place; the SPEC's reason table read at `SPEC.md:341-354`.

---

### B-7 (HIGH) — P7 Task 7's published signature cannot reach three of its own nine negative tests

**Plan:** `PLAN-SKELETON.md:728-731` (`Produces`), `:735-744` (the obligations), `:1199-1207` (the
nine negative-test rows).

**Task 7 produces exactly two functions:**

```text
check_item(item, *, unit_length) -> None
is_whole_document(item, *, unit_length) -> bool
```

`unit_length` is the only injected value. Against that signature:

| Obligation | Reachable? |
|---|---|
| `Excerpt` covering the whole unit → `WholeDocumentRequested` | **yes** — `unit_length` is exactly what it needs |
| `paths`, `OCR output`, `file hashes`, `image EXIF`, `GPS`, `user edits`, `group memberships` → `AlwaysLocalRequested` | needs a name-matching rule over `ALWAYS_LOCAL`'s nine strings. A `MetadataField(name="GPS")` is trivially constructible; refusing it is a *recognition* step, and P7's first Global Constraint is "**P7 owns no detection rule**" (`:162-166`) |
| `raw sensitive values` → `AlwaysLocalRequested`, where "the value set comes from P5's `extraction_sensitivity_signal`, not from a P7 rule" (`:1207`) | **no** — needs `conn` and a `run_id` to call `long_tail.sensitivity_signals_for`. `check_item` takes neither |
| `Filename` "permitted for non-protected files and denied for protected ones" (`:742-744`) | **no** — needs the `protected` flag. `check_item` takes neither a `file_id` nor a record |

Two of the four rows are unreachable from the published signature, and the middle row asks the task
to author the one thing the part is defined as not owning.

**Adversarial check.** The plan says at `:387` that "Task 7 uses it to decide which values are §8.4's
*raw sensitive values*" — "it" being P5's signal reader, described three sections earlier at `:370-392`.
So the *intent* is right and only the interface is missing; that is why this is HIGH and not
CRITICAL. But Task 7's `Consumes` names `extractors.long_tail.POTENTIALLY_SENSITIVE` (the string
constant) and **not** `sensitivity_signals_for` (the reader), so even the intent does not survive into
the block an implementer reads.

**What the plan must add.** Widen the signature — `check_item(item, *, unit_length, sensitive_values,
protected)` or equivalent — with `sensitive_values` supplied by the caller from P5's reader and
`protected` from `facts_seam`, both required and without defaults; add `sensitivity_signals_for` and
`store.runs_for_file` to Task 7's `Consumes`. That keeps the detection rule outside P7 (the caller
composes it) while making all nine rows reachable. Note that round 1's F-12 flags a related but
distinct problem on the same task — whether `always_local_item` can ever be a `Denied.reason` if the
item is unconstructible — and the widening above is compatible with either resolution of it.

**Status:** CONFIRMED — signature read from `Produces`; `long_tail.sensitivity_signals_for` verified
live; Task 7's `Consumes` read in place.

---

### B-8 (HIGH) — P6: `ResolveResult` is consumed by two tasks and defined by none

**Plan:** `PLAN-SKELETON.md:1046` (`FactResolver.resolve(conn, *, file_id, content_hash) -> ResolveResult`),
`:1069` (`fact_stage_output(*, result: ResolveResult) -> dict`).

Those are the only two occurrences in 1,621 lines. The name appears twice, both times inside a type
annotation, and **no task's `Produces` declares it** — no field list, no dataclass, nothing.

**What an implementer hits.** Task 21 must map "the four P6 results … to the four outcomes: facts
written → `produced`/`within_ceiling`; every attempted field ended in a non-budget `unresolved` →
`abstained`/`within_ceiling`; a ceiling stopped the work → `deferred`/`ceiling_reached`; the stage
failed → `error`", driven through P2's live `record_stage_output`, which raises on a wrong pairing
(verified: the pairing rule is enforced at P2's writer). To write that mapping the author needs to
know what `ResolveResult` carries — at minimum the facts written, the `unresolved` rows by reason,
and whether a ceiling fired. Task 21 is in the same wave as Task 20 and, per the plan, parallel with
it, so its author cannot read Task 20's implementation either.

**What the plan must add.** `ResolveResult(...)` with its fields, in Task 20's `Produces`, beside
`FactResolver`. It is the value the whole part returns and it is currently the least-specified name
in either plan.

**Status:** CONFIRMED — counted; both occurrences read in place.

---

### B-9 (MEDIUM) — P7: Task 11 creates a seven-method `Gate` facade whose five other methods are Tasks 15–18, and no task modifies `gate.py` afterwards

**Plan:** `PLAN-SKELETON.md:838` (`Files:`), `:846-847` (`Produces`).

> `Gate` (facade: `release`, `revoke`, `reclassify`, `delete_derived`, `may_move_automatically`,
> `display_policy`, `summarize_protected`)

Parsed across all 22 `Files:` blocks: **`src/privacy/gate.py` is named exactly once, by Task 11, as a
create.** Yet `revoke` and `delete_derived` are Task 15's `Produces`, `reclassify` is Task 16's,
`may_move_automatically` is Task 17's, and `display_policy` / `summarize_protected` are Task 18's.

**What an implementer hits.** Task 11's own test obligation is a whitelist — "`set(inspect.signature(Gate.release).parameters)`
equals exactly the published parameter names" — plus the `FORBIDDEN_PARAMETER_NAMES` blacklist. That
is writable for `release`. But the facade as declared cannot be constructed at Task 11, and no later
task is told to add to it, so five methods have no landing place. This is the one real ordering hole
in P7, and it is invisible to a name-level dependency check because `Gate` itself is produced by
Task 11.

**What the plan must add.** Either "modify `src/privacy/gate.py`" on Tasks 15, 16, 17 and 18, or a
final assembly task after 18 that composes the facade — with Task 11 producing only `release.py`'s
types plus a two-method `Gate`. The second is cleaner and would also relieve B-16's sibling problem
(Task 11 is P7's largest task by a wide margin: **30 produced names**, against a median of 9).

**Status:** CONFIRMED — every `Files:` block parsed; `gate.py` occurs once.

---

### B-10 (MEDIUM) — P6: Wave B and Wave D do not parallelise, and Task 10 forward-references Task 11

**Plan:** `PLAN-SKELETON.md:522-526` ("**Tasks 7–13, 14–16 and 17–23 parallelise within their wave**"),
`:772` (Task 10 consumes `facts.facets`), `:823` (Task 12 consumes `facts.facets.fill_or_abstain`).

Resolved against the module each name is created in:

**Wave B (7–13) is a three-level chain, not a flat set.**

```text
  7  evidence.py   ──┬──▶  8   direct.py
                     ├──▶  9   discount.py
                     ├──▶ 11   facets.py ──┬──▶ 10  rules.py     ← FORWARD (10 needs 11)
                     │                     └──▶ 12  dates.py
                     └──▶ 12
  13 domains.py — depends only on Wave A
```

**Task 10 consumes `facts.facets` (the word-boundary matcher) from Task 11.** Under the numeric
execution order every other plan in this project uses — P4 and P5 are both strictly sequential
1..N — Task 10 cannot be written. It is the only true numeric forward reference in either plan.

**Wave D (17–23) is also not flat.** Task 20 consumes "every producer module", which includes Task 17's
`llm_seam.py`; Task 21 consumes `ResolveResult` from Task 20 (see B-8). Wave C (14–16) genuinely does
parallelise, and Wave A is correctly declared sequential.

**What the plan must add.** Renumber so `facets` precedes `rules` (swap 10 and 11), and restate the
waves as the dependency levels they actually are: `7` → `{8, 9, 11, 13}` → `{10, 12}` for Wave B, and
`{17, 18, 19, 22, 23}` → `20` → `21` for Wave D. A wave label that overstates parallelism is worse
than none, because it is the thing a lead schedules against.

**Status:** CONFIRMED — 44 P6 edges resolved to creating tasks and grouped by the plan's own waves.

---

### B-11 (MEDIUM) — P7: `RELEASE_LEDGER_DDL` is produced by Task 12; the only task that creates the schema is Task 5

**Plan:** `PLAN-SKELETON.md:667` (Task 5 creates `src/privacy/schema.py`, produces
`create_privacy_schema(conn) -> None`), `:873` (Task 12 produces `RELEASE_LEDGER_DDL`), `:872`
(Task 12 consumes `schema.create_privacy_schema`), `:19` (P7 "owns the policy, consent-grant and
**release-ledger** tables").

`src/privacy/schema.py` is created by Task 5 and **modified by no task**. So `create_privacy_schema`
must either create the release-ledger table from a constant Task 12 has not yet written (a forward
reference), or not create it — in which case `RELEASE_LEDGER_DDL` has no caller and Task 12's
`Consumes` of `create_privacy_schema` is pointless, and P7 ships one of its three tables with two
possible homes for its DDL.

**What the plan must add.** One sentence in Task 5 saying `create_privacy_schema` creates two tables
and Task 12 adds the third (with "modify `src/privacy/schema.py`" on Task 12's `Files:`), or the
ledger DDL moved into Task 5 and `RELEASE_LEDGER_DDL` dropped from Task 12. This is small, but it is
the shape that produces two DDLs for one table.

**Status:** CONFIRMED — every `Files:` block parsed.

---

### B-12 (MEDIUM) — P6: Task 19's pass record is a fifth table in a part that declares four, and no task names or creates it

**Plan:** `PLAN-SKELETON.md:17` ("It owns **four** tables"), `:455` ("P6's four tables"), `:988`
(Task 19 modifies `src/facts/schema.py`), `:995` (`record_pass(conn, *, file_id, content_hash,
analysis_tiers: frozenset[str]) -> None`), `:1012` ("`record_pass` **writes a row**").

P6's four tables are `fields`, `values`, `file_facts` and `unresolved` — the four the Goal and the
File Structure name. The pass record is none of them: it is keyed on `(file_id, content_hash)` and
carries a tier set, and no fact or abstention row has that shape. Task 19 modifies `schema.py`
precisely because it needs one.

**Why this matters more than a count.** The pass record is what makes preamble rule 5 enforceable —
it is the row `FactPassNotRun` is raised from the absence of, and the row Task 26's termination
condition is "a lookup rather than a flag someone remembers to set". It has no name, no columns, no
DDL and no reader contract beyond `passes_for(...) -> tuple[frozenset[str], ...]`, whose return type
loses the tiers-to-pass association it needs to answer "have we already tried OCR for this content
hash".

**What the plan must add.** The table's name and columns in Task 19's `Produces`, and "**five**
tables" at `:17` and `:455` — or an explicit statement that the pass record rides on an existing
table, with which one.

**Status:** CONFIRMED — the four tables enumerated from the Goal and File Structure; Task 19 read in
place.

---

### B-13 (MEDIUM) — P7: Task 3 tells its author to build a fixture the product cannot produce, and the parameter cannot express the case

**Plan:** `PLAN-SKELETON.md:619` (`completeness_implies_unclassified(completeness) -> bool`),
`:629-632` (the obligation).

**Plan says:**

> the mapping from P4's nine `completeness` values to `unreadable_unclassified` is stated explicitly
> per value … including the case of a file with **no run row at all, which is what a dataless file has**.

**P7's own preamble, 200 lines earlier** (`:42`), says the opposite and is correct:

> | 2 | **Dataless file** (11 §5) | … | **One run row**, `completeness = dataless`, recording that the
> bytes are elsewhere. |

Verified in code: `extractors.filesystem.dataless_result` returns an `ExtractionResult` carrying a run
at `completeness = "dataless"`, `analysis_tier = "native"`, and `orchestrator.run_wave2` writes it in
stage 2b (`src/orchestrator.py:274-294`). The connection contract states the same at §2. A dataless
file **has** a run row; that is the entire reason C4 added the ninth `completeness` value.

**Two consequences.** An implementer building "a file with no run row, which is what a dataless file
has" constructs a state the pipeline never produces, and the test is green against a fiction. And the
published signature cannot express the real case anyway: `completeness_implies_unclassified` takes a
`completeness` value, and "no run row" is not one of the nine — it would need `None`, which the plan
does not mention.

The *case* is real (a `files` row whose extraction never ran), so this is not a dead test to delete —
it is a correct obligation with the wrong example and a signature one argument short.

**What the plan must add.** Drop "which is what a dataless file has"; state the real no-run case;
either widen the parameter to `str | None` and say what `None` means, or move the no-run case to
`resolve_class`, which already takes `ClassificationRecord | None`. Round 1's F-9 owns the separate
question of *who authors* the nine-value mapping; this is about whether Task 3 can be written at all.

**Status:** CONFIRMED — `dataless_result` read; the orchestrator's stage 2b read; P7's own preamble
read.

---

### B-14 (MEDIUM) — P6 Task 26 says the Wave-2 test file "stays green"; three of its tests must be deleted or inverted, and a live function must be removed

**Plan:** `PLAN-SKELETON.md:1231-1232` ("That `tests/wave2/test_wave2_orchestrator.py` stays green
with the new parameter and without the removed one").

Task 26 removes `run_wave2`'s `no_usable_facts` parameter (`:1194-1197`). Against the live file:

| Test | Line | What happens |
|---|---|---|
| `test_the_verdict_parameter_has_no_default` | `:492` | `inspect.signature(run_wave2).parameters["no_usable_facts"]` → **`KeyError`**, not a clean assertion failure |
| `test_a_real_verdict_is_still_accepted` | `:500` | asserts `assert asked, "the verdict was never consulted, so the seam is not wired at all"` — after Task 26 the verdict **must not** be consulted in loop 1, so the assertion **inverts** |
| `test_the_absent_p6_verdict_is_named_rather_than_faked` | `:486` | imports `TARGETED_OCR_UNAVAILABLE`, whose own docstring says "**When P6 lands this is deleted, not edited**" (`src/orchestrator.py:76`). Task 26 never mentions deleting it |
| `go(...)` helper | `:118` | `no_usable_facts=over.pop("no_usable_facts", TARGETED_OCR_UNAVAILABLE)` — the shared harness for all 22 tests in the file |

"Stays green" is the wrong instruction: three tests encode the *pre*-restructure contract as their
subject, and an implementer told to keep the file green has a standing incentive to keep the
parameter. Task 26's `Files:` correctly lists the file as modified; the obligation should say which
tests are deleted, which are inverted, and that `TARGETED_OCR_UNAVAILABLE` goes with them.

**Status:** CONFIRMED — file read; baseline 1,237 passing.

---

### B-15 (MEDIUM) — the two plans collide on `run_wave2`, and neither owns the `handling_class` wiring P7 Task 22 asserts

**Plan (P7):** `PLAN-SKELETON.md:1141` (Task 22 consumes "`src/orchestrator.py`'s Wave-2 path"),
`:1152-1153` (the `handling_class` assertion), `:206` (P7 modifies no other part's file).
**Plan (P6):** `PLAN-SKELETON.md:1188` (Task 26 modifies `src/orchestrator.py`), `:1534` (stage 4
"unchanged in structure").

**Two distinct problems, both new.**

1. **Signature collision.** Both plans state they are buildable alone, and both depend on
   `run_wave2`'s call contract. P7 Task 22 must call it (or a harness that does); P6 Task 26 removes
   one required keyword and adds another with no default. Whichever lands second breaks the other's
   skeleton test, and neither plan mentions the other's claim on the file. This is an ordering
   constraint between two supposedly independent parts and it is unstated in both.

2. **`handling_class=None` has no owner in either plan.** Round 1's F-7 established the citation
   error and named the consequence. What round 2 adds is the search for the owner: **P6 Task 26 is
   the only task in the wave that touches `src/orchestrator.py`, and its shape table says stage 4 —
   the loop containing `handling_class=None` at `src/orchestrator.py:311` — is "unchanged in
   structure".** So P7 Task 22 asserts a value non-null that P7 may not write and P6 does not write.
   Forty-nine tasks and no owner.

**What the plans must add.** One sentence in P6 Task 26 taking the `handling_class` line as part of
the orchestrator diff (it already owns the file, and the classification reader can be injected the
same way the resolver is), plus a note in P7 Task 22 that its bundle assertion depends on P6 Task 26
having landed. Or explicitly defer Done-means 13's bundle clause and say which part closes it.

**Status:** CONFIRMED — both plans' `Files:` blocks parsed; `orchestrator.py:311` read;
`grep -n handling_class src/orchestrator.py` returns one line.

---

### B-16 (MEDIUM) — P6 Task 20 fuses the budget ceilings with the resolver, and `resolver.py` gets no test file of its own

**Plan:** `PLAN-SKELETON.md:1039` (`create src/facts/budgets.py, src/facts/resolver.py; test
tests/p6/test_p6_budgets.py`), `:475` (File Structure: `resolver.py` — "the one entry point that
sequences the producers in §8.6's order").

`src/facts/resolver.py` is the single entry point of the entire part. It is constructed "with every
injected strategy and threshold", it sequences all ten producer modules, it owns `ResolveResult`
(B-8), and it is where the P7 and P8 seams land (B-6). It shares one task, and one test file named
for budgets, with a module whose job is to read three ceiling keys from P1.

The File Structure lists no `tests/p6/test_p6_resolver.py`. The comparator is P5, where the router —
the analogous single sequencing point — got its own task and its own test file (`P5 PLAN.md:1749`,
Task 4). P6's right-sizing rule ("a task is the smallest unit that carries its own red-green cycle
and is worth a reviewer's gate", `:528`) is not met here: budgets and the resolver are two red-green
cycles and two reviewer gates.

**What the plan must add.** Split Task 20 into "the three ceilings and the degradation order"
(`budgets.py`, `test_p6_budgets.py`) and "the resolver — the one sequencing entry point"
(`resolver.py`, `test_p6_resolver.py`, `ResolveResult`, the injected privacy and model seams).

*Right-sizing survey, for context.* Produced-name counts per task, median 5 (P6) and 9 (P7). The
outliers are P7 Task 11 (**30** names, 2 modules, 1 test file), P6 Task 2 (16 names, 3 modules),
P7 Task 5 (15 names, 2 modules) and P6 Task 20 (11 names, 2 modules). **No task in either plan is too
small to fail meaningfully** — the two test-only guard tasks (P6 25, P7 21) and the two skeleton
tasks (P6 27, P7 22) match the P4 Task 18/19 and P5 Task 20/21 pattern exactly.

**Status:** CONFIRMED — counts computed mechanically; File Structure read.

---

### B-17 (LOW) — three `Consumes` blocks name a category instead of a symbol

**Plan:** P6 `:1042` ("every producer module"), P6 `:1143` ("every table module"), P7 `:841`
("everything from Tasks 2–10").

The brief's test for an `Interfaces` block is whether an author who sees only their own task can
write against neighbours they cannot read. These three fail it by construction — they name a set the
author must reconstruct by reading the other twenty-something tasks. P6 Task 20 is the one where it
costs most, because "every producer module" is also where the missing privacy and model seams should
have been visible (B-6).

P4 and P5 have no equivalent; every `Consumes` there is a dotted name. **What the plan must add:** the
enumeration. It is four lines in each case.

**Status:** CONFIRMED.

---

### B-18 (LOW) — P7 publishes no execution order at all; the numeric order happens to work

P6 opens its task list with waves, a parallelisation claim and a right-sizing rule (`:520-531`). P7
has `## Tasks` and then Task 1. No ordering statement, no waves, no note on what may run in parallel.

I checked whether it matters: **all 45 of P7's internal dependency edges point to a lower-numbered
task**, so strict numeric order is a valid topological order. The one exception is the `Gate` facade
(B-9). So this is a documentation gap rather than a defect — but a lead scheduling P7 has nothing to
schedule against, and the fact that numeric order works is currently an accident nobody has written
down.

**What the plan must add.** One sentence: "Tasks run in numeric order; 6, 7, 8 and 9 are independent
of one another and of 5, and 15–18 may run in parallel once 11 lands." (Verified against the graph.)

**Status:** CONFIRMED.

---

### B-19 (LOW) — P6's orchestrator shape table cites five line numbers, and all five now land in the wrong place

**Plan:** `PLAN-SKELETON.md:1528-1534`.

| Table says | Actually |
|---|---|
| `run_wave2(...)` — line 138 | `def run_wave2` is **161**; `no_usable_facts` is **167**. Line 138 is inside `_extract_one`'s docstring |
| stage 2, lines 168–218 | the loop is **195–266**. Line 168 is a `run_wave2` parameter |
| `extract(..., no_usable_facts=...)` — line 119 | the call is **145–149** inside `_extract_one`. Line 119 is inside `_extraction_is_stale` |
| stage 2b (dataless), lines 219–245 | **268–294** |
| stage 4 (P2 bundle), lines 247–267 | **296–319** |

Round 1's F-19 flagged the same drift in the **F1** block (`:1364-1372`); this is a second, separate
block of citations and the drift is larger. Round 1 measured `run_wave2` at 135 and `handling_class`
at 285; they are now 161 and 311 — **the file moved ~26 lines during the same night**, so the plan's
numbers were probably right when written. The buildability consequence is what matters: an
implementer opening "stage 2, lines 168–218" to plan a four-loop restructure finds a parameter list.

**What the plan must add.** Anchor the table to symbol names (`_extract_one`, the `cache_verdicts`
loop, the `dataless_detections` loop, the `open_bundle` block) rather than to line numbers, since the
file has now drifted twice in one night.

**Status:** CONFIRMED — each line opened.

---

### B-20 (LOW) — P7 Task 5 does three unrelated things, one of which is P5's back-edge

**Plan:** `PLAN-SKELETON.md:667` (creates `policy.py` **and** `schema.py`), `:673-677` (15 produced
names), `:677` (`transcription_authorized_for(scope) -> Callable[[], bool]`).

Task 5 creates P7's entire database schema, the four-mode policy record with its versioning and
supersession, the consent-grant surface, the redaction settings, **and** the speech-to-text
authorization adapter for `extractors.dispatch.extract` — which the plan itself calls "a genuine seam
mismatch" (`:398`) because P5's predicate is zero-argument and every P7 surface is scoped. That last
item shares nothing with policy versioning and is the one a reviewer would most want to gate
separately.

**What the plan must add.** Move `transcription_authorized_for` to its own small task (it is the M10
back-edge and has its own consumer), and consider splitting the schema out as P6 needs to anyway
(B-4).

**Status:** CONFIRMED.

---

## Dependency table

Both plans' `Interfaces` blocks parsed and every internal name resolved to the task that produces it.
**89 edges. Zero undefined names among resolved symbols; zero numeric forward references among them.**
The failures are all in the *file* graph and in names that appear only in prose — which is why a
name-level check alone would have passed both plans.

**Summary**

| | P6 | P7 |
|---|---|---|
| Internal edges resolved | 44 | 45 |
| → OK (producer is a lower-numbered task) | 44 | 45 |
| → forward reference | 0 | 0 |
| → undefined | 0 | 0 |
| Files in File Structure with no creating task | **1** (`tests/p6/conftest.py`) | 0 |
| Files modified by a task and created by none | **1** (`src/facts/schema.py`, 5 tasks) | 0 |
| Names used in a signature but declared by no task | **1** (`ResolveResult`) | 0 |
| Seams named in prose but in no `Interfaces` block | **2** (`handling_class`, `propose`/`validate`) | 0 |
| Declared-parallel waves that are not parallel | **2** (B, D) | n/a |

**The rows that are not OK**

| Task | Consumes | Produced by | Verdict |
|---|---|---|---|
| P6 T2 | `src/facts/schema.py` (modify) | **no task** | **undefined file** — B-4 |
| P6 T3, T4, T5, T19 | `src/facts/schema.py` (modify) | **no task** | **undefined file** — B-4 |
| P6 all test tasks | `tests/p6/conftest.py` | **no task** | **undefined file** — B-5 |
| P6 T10 | `facts.facets` (word-boundary matcher) | **T11** | **forward reference** — B-10 |
| P6 T12 | `facts.facets.fill_or_abstain` | T11 | OK numerically; **breaks Wave B's parallel claim** — B-10 |
| P6 T8, T9, T10, T11, T12 | `facts.evidence` | T7 | OK numerically; **breaks Wave B's parallel claim** — B-10 |
| P6 T20 | `handling_class(file_id) -> str` (P7) | **no task; prose only (`:433`)** | **undefined** — B-6 |
| P6 T17, T20 | `propose(request)` / `validate(proposal, checks)` (P8) | **no task; prose only (`:434`)** | **undefined** — B-6 |
| P6 T21 | `ResolveResult` | **no task** (annotation only, `:1046`) | **undefined type** — B-8 |
| P6 T20 | "every producer module" | T8–T17 | **not a name** — B-17 |
| P6 T24 | "every table module" | T2–T5 | **not a name** — B-17 |
| P6 T19 | the pass-record table | **no task names or creates it** | **undefined table** — B-12 |
| P6 T26 | a loop-1 verdict that raises | mechanism is swallowed by `_extract_one` | **broken** — B-1 |
| P6 T26 | a targeted-OCR entry point | **`dispatch` publishes none** (`_ocr` is private) | **undefined** — B-2 |
| P7 T5 | the release-ledger DDL | **T12** (`RELEASE_LEDGER_DDL`) | **forward reference** — B-11 |
| P7 T11 | `Gate.revoke`, `.reclassify`, `.delete_derived`, `.may_move_automatically`, `.display_policy`, `.summarize_protected` | T15, T16, T17, T18 | **forward reference**, and no task modifies `gate.py` — B-9 |
| P7 T11 | "everything from Tasks 2–10" | T2–T10 | **not a name** — B-17 |
| P7 T7 | a sensitive-value set and a `protected` flag | not in `check_item`'s signature | **undefined** — B-7 |
| P7 T21 | `{evidence_shape, extractors, privacy}` as the materialiser allowlist | live set is `{evidence_shape, orchestrator}` | **wrong; guard is red** — B-3 |
| P7 T22 | a non-null `handling_class` in the Wave-2 bundle | **no task in either plan** | **undefined** — B-15 |

**Every external surface both plans cite was imported and checked and exists.** That includes the
counts, several of which are load-bearing: `CEILING_KEYS` = 16 (P6 correct at `:244`; P7 says fifteen
at `:243` — round 1's F-10, not repeated), `RESERVED_EVENT_TYPES` = 19, `REGISTERED_EVENT_TYPES` = 16
with **all eight of P7's names present and none colliding**, `EVENT_FIELDS` = 11,
`CORRECTION_FIELDS` = 5, `CORRECTION_SCOPES` = 6, `FILES_COLUMNS` = 16, `ZONES` = 15,
`SOURCE_TYPES` = 14, `COMPLETENESS` = 9, `CONFORMANCE_RULES` = 12, `RELIABILITY_STATES` = the six in
the stated order, `EXTRACTOR_RELIABILITY_STATES` = `("direct", "possible")`,
`STAGE_IDS[1] == "factual_validation"`, `"fact" in DIMENSIONS`, `SUPERSEDE_ADAPTER_COLUMN == "record_id"`,
and `evidence_shape.store.observations_for_content` correctly reported **absent** (P6 F12).
`files.sensitivity_state` confirmed to have no writer by `ast` — the only string occurrences in `src/`
are the DDL and `FILES_COLUMNS`.

---

## Missing tasks

What must be built that neither plan has a task for.

| # | Missing | What it must do | Where it belongs |
|---|---|---|---|
| 1 | **P6 schema creation** | Create `src/facts/schema.py`; publish `create_facts_schema(conn) -> None` creating all P6 tables; carry the `record_id` VIRTUAL projection for `mark_superseded` on `file_facts` and `unresolved` | new Wave-A task before Task 2, or fold into Task 2 as a **create** (B-4) |
| 2 | **P6 `tests/p6/conftest.py`** | P4 fixture loading, the fixed clock, the injected strategies with no defaults, the absent-P7/P8 stand-ins; plus the top-level-`conftest` shadowing rule P7 states and P6 omits | Task 1's `Files:` (B-5) |
| 3 | **P6 pass-record table** | Name, columns, DDL and a reader that preserves the tier-set-per-pass association `passes_for` currently flattens | Task 19's `Produces` (B-12) |
| 4 | **P6 `ResolveResult`** | The value the part returns: facts written, `unresolved` rows by reason, whether a ceiling fired — enough for Task 21's four-outcome mapping | Task 20's `Produces` (B-8) |
| 5 | **P6's privacy and model injection points** | `handling_class` and `propose`/`validate` as named, no-default constructor parameters, plus the `privacy_withheld` write path | Tasks 17 and 20 (B-6) |
| 6 | **P6's §3.2 walking-skeleton fixture** | The three-observation set Done-means 4 needs (`Syllabus BUSIB 4300 Spring 2026.pdf` / `BUSIB 4300 Syllabus` / `Spring 2026`) — the plan's F15 says P6 authors it with P4's builders, and no file in the File Structure is its home once the conftest gap (2) is closed | Task 1's conftest or a `tests/p6/fixtures.py` |
| 7 | **P6 no-invention guard: the writer check** | "Every `UNRESOLVED_REASONS` member has a writing call site" and "every `fields` row has a producer" — the check `22-p1-p7-connection-contract.md` §5 requires and Task 25's list omits. It would have caught B-6 and round 1's F-2 mechanically | Task 25 |
| 8 | **P6 targeted-OCR entry point** | A public function in `extractors.dispatch` that runs OCR without re-running native extraction, and a native-only entry that does not consult the verdict | Task 26, or a new P5-side task (B-1, B-2) |
| 9 | **P7 `Gate` facade assembly** | Compose the seven methods after Tasks 15–18, or add "modify `gate.py`" to each | new final task, or Tasks 15–18 (B-9) |
| 10 | **P7 always-local recognition inputs** | Widen `check_item` and add `sensitivity_signals_for` to Task 7's `Consumes`, keeping the rule in the caller | Task 7 (B-7) |
| 11 | **The `handling_class` bundle wiring** | Change `src/orchestrator.py:311` from a hard-coded `None` to a value read from a classification source | P6 Task 26 (it owns the file), with a note in P7 Task 22 (B-15) |

---

## P6 Task 26 — my honest read

**Not executable as written. Under-described in three places and wrong in one, and it needs
splitting into three tasks.**

The *diagnosis* in preamble rule 5 and finding F1 is correct and unusually well argued — the four
passes are the right shape, the "at the consult point the evidence does not exist yet" observation is
the sharp form of the defect, and the blast-radius analysis (PDF branch only, text-bearing only) is
accurate against the code. Task 19's `FactPassNotRun` is the right instrument. None of that is in
question.

What is wrong is the *implementation contract*, and it is wrong in a way that survives review because
it is stated at the level of a diagram:

- **The mechanism is refuted by execution.** Loop 1's raising verdict is swallowed by `_extract_one`
  and becomes a `failed` run per text-bearing PDF, and the stated test cannot observe it (B-1).
- **Loop 3 has no entry point**, and the only public path duplicates native extraction and erases the
  tier map (B-2).
- **"Stays green" is the wrong instruction** for a test file three of whose tests encode the
  pre-restructure contract, and it does not mention deleting `TARGETED_OCR_UNAVAILABLE`, which the
  source says must go (B-14).
- **The one line that closes the P7 seam** — `handling_class=None` — sits in the loop Task 26 declares
  "unchanged", and no other task in either plan owns it (B-15).
- **Every line citation in the shape table is stale** (B-19).

It is also mis-sized. Task 26 currently carries the P5-side surface change, the four-loop
orchestrator rewrite, the deletion of the old parameter and its three tests, and eight distinct test
obligations including the supersession and termination properties — in a task whose `Produces` block
is three lines. **Split it three ways:**

1. **P5 surface** — a public native-only entry and a public targeted-OCR entry in
   `extractors.dispatch`, with the existing `extract()` kept or expressed in terms of them. Its own
   red-green cycle, its own reviewer gate, and it is where the "`dispatch.py` does not change"
   constraint has to be renegotiated.
2. **The rewire** — four loops, the parameter swap, the tier-map merge, the `signals` guard, and the
   Wave-2 test file's deletions and inversions.
3. **The order proof** — `tests/p6/test_p6_pass_order.py`: the verdict is never consulted before
   `record_pass`; a fact-bearing PDF is never OCRed; a fact-less one is OCRed exactly once; loop 4
   supersedes; a second run does not re-OCR; and with `ocr_engine is None` the corpus resolves from
   native evidence with **no duplicate runs** — which is the assertion that would have caught B-2.

The plan's own scheduling note is right and should be kept: this is the only work in the wave that
touches a file P6 does not own, it belongs last, and it should be reviewable as a standalone diff
against a green suite. The recommendation in NEEDS JOSEPH 1 — build the four passes now, wire an
engine later — also survives all of the above unchanged. It is the *diff*, not the decision, that is
under-specified.

---

## NEEDS JOSEPH

Verbatim and unresolved. Round 1's six are not repeated; these are the ones buildability raises.

**1. Does `extractors.dispatch` gain two public entry points?** P6 Task 26 states "What does **not**
change: `extract()`'s signature, `dispatch.py`, `ocr_policy.py`, every P5 extractor" — and the
four-pass structure cannot be built without changing one of them, because `_extract_one` swallows a
raising verdict into a `failed` run and `dispatch` publishes no OCR-only function. **The question is
whether P5's published surface may grow a native-only entry and a targeted-OCR entry, or whether the
orchestrator is permitted to call `dispatch._ocr` directly.** The first is a P5 contract revision; the
second is a private call across a part boundary. **Recommendation: the first**, because §2.2's three
text-layer states are P5's and a route it cannot express separately is a route it does not really
own. Not answerable inside P6.

**2. Who writes `handling_class` into the Wave-2 bundle, and when?** P7's Done-means 13 asserts it is
non-null; P7 may not touch `src/orchestrator.py`; P6 Task 26 owns that file and declares the bundle
loop unchanged. The value is `None` at `src/orchestrator.py:311` and has no producer in forty-nine
tasks. **Options:** (a) P6 Task 26 takes the line as part of its diff, injecting a classification
reader the way it injects the resolver; (b) P7 gains a task that modifies the orchestrator,
coordinating with Task 26; (c) Done-means 13's bundle clause is explicitly deferred and named to a
later part. **Recommendation: (a)** — the file already has one owner in this wave and two would be
worse. This is downstream of your OQ11 decision (round 1's §3 / the connection contract's §3), and it
cannot be settled before it.

**3. Do P6 and P7 have a landing order?** Both plans state they are independently buildable and both
depend on `run_wave2`'s call contract — P6 Task 26 changes it, P7 Task 22 calls it. Neither mentions
the other. **Whichever lands second must absorb the first's change, and it should be said which.**
Not a design question, but it is a scheduling decision neither plan's author can make alone.

---

## What this round did not look at

Defect-class reproduction (round 3), whether P6 and P7 attach to built P1–P5 (round 4), and scope
(round 5). Where a finding here has a downstream consequence it is noted rather than resolved:
B-6's `privacy_withheld` is defect class 5 in miniature and belongs to round 3 as well; B-3's
allowlist and B-15's collision are both round 4's territory once the interfaces are fixed; and
B-9's, B-16's and B-20's splits are decompositions, not deletions, so round 5 should read them as
"this task does three things", not as "this task is overbuilt".
