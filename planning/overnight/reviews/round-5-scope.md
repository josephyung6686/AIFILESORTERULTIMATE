# Round 5 — simplification and scope

Lens: **what should not be built at all.** The ceiling is
[`00-database-agent-product-design.md`](../../00-database-agent-product-design.md) (read here through
its sectioned twin, `01-product-design-structured.md`, which is the same text). Every task in both
skeletons was traced back to a design sentence; where none exists the task is a candidate for
deletion, and where one exists but a later part already claims it, the task is a candidate for
reassignment.

**Round 4 (connection) had not been written when this round ran** — `planning/overnight/reviews/`
contains rounds 1, 2 and 3 only, at 03:12, 03:38 and 03:36 on 2026-08-21. Its recommendations are
therefore judged below only where rounds 1–3 anticipated them (B-3, B-15, A9, A17 are all
connection-shaped and are treated). If round 4 lands after this, its additions have not been through
this filter.

Substrate as of this round: `pytest tests/ -q` → **1244 passed in 6.9s.**

---

## Verdict

**These are not the simplest thing that satisfies the design, but the gap is narrower than the raw
sizes suggest: about 8% of the published surface, and — measured against the plans *after* they
absorb rounds 1–3 — about 14% of the tasks.** The measurement:

| | P4 (shipped) | P5 (shipped) | **P6 (planned)** | **P7 (planned)** |
|---|---|---|---|---|
| Tasks | 19 | 21 | **27** | **22** |
| Source modules | 14 | 23 | **29** | **23** |
| Test files | 24 | 28 | **30** | **25** |
| Distinct symbols in `Produces:` blocks | 98 | 117 | **135** | **197** |
| Source lines actually written | 2,465 | 3,536 | — | — |

P4 and P5 together are 40 tasks and 215 published symbols. P6 and P7 together are **49 tasks and 332
published symbols** — 22% more tasks carrying 54% more surface. P6 is the largest part yet planned by
every measure. Some of that is real: P6 owns fourteen design sections (§3.1–3.14) against P4's one
(§2.8), and P7's §8.4 is the densest single section in the document. But not all of it is.

**The arithmetic of the cut list, so the headline is checkable.** Rounds 1–3 as written add **+7
tasks** (a P6 schema task, Task 26 splitting three ways, a P7 `Gate`-assembly task, a P5 dispatch
task, and two endorsed splits), taking the wave to **56**. This round cuts three tasks outright,
merges two, keeps two splits, and rejects four of round 2's seven additions — landing at **48**, or
**−14% against the post-review plan and −2% against the plans as they stand.** On surface it removes
**~25 of 332 published symbols (≈8%)**, one table, one P5 contract revision and one P1 change. The
larger effect is not the count: **twelve findings and three "missing tasks" from rounds 1–3 stop
existing rather than needing fixes.**

The concentration is worth naming. **P7 Task 11 alone produces 30 symbols** — more than any task in
P4 or P5 — and 6 of the 7 methods on the `Gate` facade it builds are implemented by four *later*
tasks that no task then wires in (round 2 B-9). **P6 declares four tables and needs five** (round 2
B-12): the fifth exists only to make an ordering guard checkable, and the guard was proven inert by
execution in round 3.

Three things are genuinely overbuilt, and they share a shape: **each is a mechanism built to prove a
property, where the property belongs to a part that does not exist yet.** P6's four-pass orchestrator
restructure proves an OCR ordering for an OCR engine nobody has chosen. P7's `transport_guard.py`
proves a transport property for a transport P8 owns — and P8's own Done-means 1 states its own
verification method and never names P7's instrument. P6's `plan_versions.py` builds a plan-versioned
label store for a §8.8 line that **P10's SPEC already assigns to P10, by name.** Those three are the
cut list's top entries and they account for most of the saving.

The rest of both plans is tighter than the numbers suggest. Neither plan invents a numeric threshold,
a gazetteer, a regex catalogue or a default operation mode; both hold their open questions open with
named guards; both report their own SPEC-vs-design divergences rather than smoothing them. P7's
"Fully provable inside P7?" column is the most honest artifact in the wave. **Where these plans are
big, they are big because the design is, not because the authors were.**

One counter-finding, stated up front because it matters more than any single cut: **I attempted two
deletions and withdrew both after checking the design.** They are in the keep list. Cutting the wrong
thing here would have been worse than keeping a spare one, and both were well-reasoned enough to
survive a review that was not looking for the specific sentence.

---

## Cut list, ranked by size of saving

### CUT 1 — P6 Task 26 (the four-pass orchestrator restructure) and the pass-record half of Task 19

**What to cut.** `src/orchestrator.py`'s split into four loops; the `no_usable_facts` parameter
removal and `resolver` parameter addition; `record_pass`, `passes_for`, `FactPassNotRun`, and the
pass-record table (P6's undeclared fifth); `tests/p6/test_p6_pass_order.py`; and the P5 contract
revision round 2 says the restructure requires (two new public entry points in
`extractors.dispatch`).

**What stays.** `facts/usable.py` keeps `no_usable_facts_for(conn, *, usable_threshold) ->
Callable[[str, str], bool]` and every test Done-means 28 names — computed from the fact tables, no
text-quality heuristic, threshold a required keyword. That is the whole of the SPEC's read-surface
obligation. What goes is the machinery that *sequences* it.

**The design sentence, and why it does not carry the weight.** §2.2, verbatim:

> The system should also distinguish between a PDF with **no** text layer and one with a **broken**
> text layer. A file with no text should route directly to OCR; a file that technically produces text
> but yields no usable facts **may** receive targeted OCR as a fallback, because scanned PDFs can
> contain unreadable or corrupted extracted text.

`may`. The `text_layer_absent` route is a `should` and is already built and unaffected. The
`text_layer_broken` route — the only route the restructure exists to serve — is the one clause in
§2.2 written as permissive, and it is the one that cannot do anything in v1 because no OCR engine is
chosen. Verified with `ast`, not by reading: `src/extractors/dispatch.py` declares
`Readers.ocr_engine: Callable[..., Any] | None = None`, `_ocr` returns `None` when it is unset, and
**the only `ocr_engine` values anywhere in the repo are `None` and six test lambdas.** P5's own
NEEDS JOSEPH 1 (*which* engine) is open.

**The v1 posture already exists and is already tested.** `src/orchestrator.py:59` defines
`TARGETED_OCR_UNAVAILABLE(file_id, content_hash) -> bool`, whose docstring says:

> P6 has not run, so §2.2's `text_layer_broken` route cannot be evaluated. […] Callers passed
> `lambda f, h: False` for this, and that is not the same statement. `False` from P6 means *"I
> examined this file's stored facts and the text layer is fine."*

That is the correct v1 statement with one word changed — *no OCR engine is wired*, rather than *P6
has not run*. It is a docstring edit. Round 2 B-14 notes Task 26 forgets to delete this function;
the simplification is that it should not be deleted.

**Downstream consumers checked.** `no_usable_facts`, `record_pass`, `passes_for` and `FactPassNotRun`
appear in **no** SPEC for P8, P9, P10, P11, P12 or P13 — checked across all six. The only downstream
reference in the whole planning tree is P2's adversarial case A10, and round 1 F-22 established A10
is `dimension: extraction`, i.e. P5's gate, not P6's. P5's `extract()` signature requires the
callable, and `TARGETED_OCR_UNAVAILABLE` already satisfies it with the two P5 tests that assert it
has no default (`tests/p5/test_p5_no_invention.py`, `tests/p5/test_p5_ocr_policy.py`) still green.

**What breaks if I am wrong.** If v1 ships an OCR engine, `text_layer_broken` is never acted on and
the corpus's corrupted-text-layer PDFs resolve from native evidence alone. That is P6's own NEEDS
JOSEPH 1 option (b), which the plan already lists. Re-adding is round 2's three-task split —
**against a live engine**, which is strictly better than building it now: round 3 A1 proved by
execution that with no engine the guard is green and inert, because `orchestrator.py:157`'s blanket
`except Exception` converts `FactPassNotRun` into `completeness = failed` and Task 26's own
acceptance test cannot observe the firing. Building a guard now that can only be tested against a
synthesised input is §2.7's dead-path defect, which is defect class 4 on this project's own list.

**Saving.** 1 task as written (3 after round 2's mandated split), 1 table, 4 published symbols, 1
test file, 1 P5 contract revision, 1 orchestrator ownership collision. **It also deletes rather than
fixes:** round 2 B-1 (CRITICAL), B-2, B-12, B-14, B-19 and missing-tasks 3 and 8; round 3 A1
(CRITICAL) and A12(a); and half of A17.

---

### CUT 2 — P7 Task 19 (`transport_guard.py` and `assert_single_egress`)

**What to cut.** `src/privacy/transport_guard.py`, `tests/p7/transport_fixtures.py`,
`tests/p7/test_p7_transport.py`, `assert_single_egress`, `egress_functions`,
`CONTENT_PARAMETER_TYPES`, `MultipleEgressPoints`, `UnreleasedContentParameter`, and the row in P7's
Contract-out table that offers the instrument to P8.

**The design sentence it lacks.** §8.4's opening — *"Privacy policy must be enforced **before**
content reaches any model or external connector"* — states a **property**. It does not ask for a
static analyser, and no sentence anywhere in §8.4 or §8.6 does.

**Downstream consumer checked, and this is the decisive part.** P8's SPEC Done-means 1 reads:

> **One egress.** Exactly one function in the codebase constructs a model request, and its only
> parameter type is P7's `Released`. A call without a release is not constructible. **Verified by
> inspection plus a test that the un-released path does not type-check / does not exist.**

P8 states its own verification method and it is not P7's checker. `assert_single_egress` appears
nowhere in P8's SPEC — grepped in full. P7 is building an instrument its only stated consumer did not
ask for and has already decided how to do without.

**What breaks if I am wrong.** Done-means 3 loses its L3 layer inside P7. L1 (the ledger, Task 12)
and L2 (the single materialisation locus, Tasks 9 + 21) both stay and are what P7 can actually prove.
P7's coverage table already says Done-means 3 is *"**No — and this is a finding**"* and names P8
Done-means 1 as the item that closes it; cutting the instrument makes that honest sentence complete
rather than hedged. Cost to add later: writing the same checker in P8 — where round 3 A15 proves it
must AST-walk the function **body** (to require a `consume_release` call) and not the signature, and
where "the body" only exists once P8's transport does.

**Saving.** 1 task, 1 module, 2 test files, 10 published symbols, and round 3 A15's addition (a fifth
non-conforming fixture plus an AST body-walk) does not need to be built.

---

### CUT 3 — P6 Task 23 (`plan_versions.py`)

**What to cut.** `src/facts/plan_versions.py`, `tests/p6/test_p6_plan_versions.py`, `PLAN_VERSIONED`,
`SHARED_ACROSS_PLAN_VERSIONS`, `display_label(conn, *, value_id, plan_version)`,
`set_display_label(...)`. P6 then has **no plan-version awareness at all**, which is the simpler and
more faithful position.

**The design sentence, and who owns it.** Task 23's positive warrant is §8.8's plan-version capture
list, one line of which is *"User labels and aliases."* **P10's SPEC assigns that exact line to P10,
by name:**

> | User labels and aliases | **P10** | §8.8 |

and P10's node record carries `display_label` described as *"the intended display name; may be a user
alias over a normalised value | §5.12, §2.8, §8.8 ('User labels and aliases')"*. §8.8's own worked
diff — *"Applications was renamed to Admissions"* — is a **branch** rename, which is a tree edit, not
a value rendering. P9 likewise carries its own per-plan-version `user_edited_label` on
`group_acceptance`. Three parts do not need three plan-versioned label stores.

Task 23's *negative* warrant — §8.8's *"The evidence database remains shared across plan versions"* —
is quoted correctly by the plan and is an argument that P6 needs none of this machinery. The task
quotes the sentence that makes it unnecessary.

**What P6 keeps.** §2.8's actual sentence is about the value, not the plan: *"If a document says `U
Chicago`, the raw observation remains exactly that wording, while a resolver may normalize it to
`University of Chicago` and **the user may later choose to display it as `UChicago`**."* One user
choice, one column, no version dimension. `values.display_label` and `values.aliases` stay exactly
where Task 3 puts them.

**What breaks if I am wrong.** If a later part needs a *value*-level label that differs between plan
versions — as distinct from a node label, which is P10's — it adds a `plan_version` column to a
P6-owned table and moves the reader. One migration, one column. Nothing in P8–P13 reads a
`display_label` keyed by `value_id`; every downstream `display_label` found is a node's (P10, P11,
P12, P13) or a group's (P9).

**Saving.** 1 task, 1 module, 1 test file, 4 symbols. It also deletes round 3 A11 (`display_label`
has two homes and one has no writer) rather than resolving it — A11's recommended fix was to move the
columns *to* Task 23; the simpler fix is that Task 23 does not exist.

---

### CUT 4 — P7's `Gate` facade as a seven-method object

**What to cut.** Six of the seven methods. Keep `Gate.release` — the one door §8.4 and B2 require —
and publish `revoke`, `reclassify`, `delete_derived`, `may_move_automatically`, `display_policy` and
`summarize_protected` as module functions in the modules that already implement them (Tasks 15–18).

**The design sentence it lacks.** §8.4 requires that policy be enforced before content reaches a
model. That is one door for **release**. Nothing in §8.4 asks for one object holding revocation, the
move predicate and the display policy; those are three unrelated reads that happen to consult the
same policy row. A facade with six one-line delegations is an abstraction with one implementation.

**Why it costs more than it looks.** Round 2 B-9: Task 11 declares all seven, four later tasks
implement six of them, and **no task modifies `gate.py` afterwards** — so round 2's missing-task 9 is
"a new final task to compose the facade." Deleting the facade deletes that task instead of adding it.

**What breaks if I am wrong.** P13 and P11 import six names from `privacy.revocation`,
`privacy.moves`, `privacy.display` and `privacy.learning_seam` instead of from one object. P7's
Contract-out table already lists them by module-shaped name (`Gate.revoke`, `Gate.reclassify`, …), so
the table needs six edits. If a facade is later wanted for ergonomics, it is fifteen lines written
once against six finished modules — which is the only order in which it can be written without
forward references.

**Saving.** ~8 symbols, 1 round-2 task avoided, and Task 11 drops from 30 produced symbols to about
22 — still the largest task in either plan, but no longer larger than anything P4 or P5 shipped.

---

### CUT 5 — P7 Task 4's `SensitivityStateWriter` injected protocol and `mirror_state`

**What to cut.** The injected protocol and the mapper. Replace with a request to P1 for
`set_sensitivity_state(conn, file_id, *, state, author, component_version)` — one function, and the
precedent is exact.

**Why this is a parameter pretending to be a policy.** An injected value earns its injection when it
has more than one possible source. This one has exactly one: P1, which owns `files`. P7's own plan
says so — *"injected, because P1 publishes no such writer"* — and names the precedent in the same
breath: *"the same position P5's plan took on `extraction_status_by_tier` before P1 published
`set_extraction_status`, and the gap is reported rather than patched."* P5 reported it and **P1 then
published the setter.** Repeating the report without repeating the outcome is the part that does not
follow.

**Why it is not merely redundant but active.** Round 3 A10: once `mirror_state` exists,
`handling_class = file_row["sensitivity_state"]` becomes the shortest edit that makes Task 22's
assertion pass — and that is precisely the line the 2026-08-21 pass removed and replaced with
`handling_class=None` and a six-line comment explaining why. The injection makes the ratified fix and
its regression the same edit. Verified with `ast`: `files.sensitivity_state` occurs in `src/` only in
the DDL and in `FILES_COLUMNS`; it has no writer today.

**What breaks if I am wrong.** If P1 declines, P7 is blocked on a one-function P1 change instead of
shipping a protocol — a scheduling cost, not a design one. Note that this cut also removes the need
for the plan to state `files.sensitivity_state`'s vocabulary (round 3's NEEDS JOSEPH 5), because a
P1-published setter validates against `HANDLING_CLASSES` at the point of write, where a mapper would
have had to translate.

**Saving.** 2 symbols, 1 protocol, and round 3 A10 disappears.

---

### CUT 6 — P6's `STRENGTH_ORDER` / `strength()` / `is_stronger()` five-rank ladder

**What to cut.** The total order. Replace with the predicate §3.6 actually names.

**The design sentence it lacks.** §3.13 is a flat six-row table with no ordering claim — round 1 F-20
established this and I re-read §3.13 to confirm: `direct > validated` is stated **nowhere** in the
design. §3.6's only comparison is *"no stronger direct or rule-validated fact contradicts it"* —
which groups `direct` and `validated` together against an LLM proposal, exactly as §8.6 does
(*"Direct facts and high-precision rules run first"* — one rung, which is round 1 F-21's point about
`DEGRADATION_ORDER` arriving from the other side).

**What to build instead.** `contradicts_stronger(candidate_state, existing_state) -> bool`,
implementing §3.6's sentence and nothing more: a `llm_supported` or `possible` proposal is refused by
an existing `direct` or `validated` fact; a `user_confirmed` fact outranks everything (§3.13 states
that one relation outright).

**Why this is a simplification and not a loss.** A five-rank ladder is *more precise than its source*,
and the excess precision is exactly where OQ10 lives: "two equal-rank contradicting facts" is only a
hole if you have committed to ranks. Under §3.6's predicate, two contradicting `validated` facts are
the ordinary case the design does not resolve, and P6 refuses both — which is what the plan already
says it does.

**What breaks if I am wrong.** If OQ10 is later settled as "defer to the internal score," a ladder
returns. Note it would return alongside `file_facts.internal_score`, which round 3 A16 found has no
writer today — so the two arrive together or not at all.

**Saving.** 2 symbols, and it closes round 1 F-20 by deletion. It also defuses round 1 F-3 (see the
verdict on rounds 1–4 below).

---

### CUT 7 — P6 read surface: `event_facts`, `session_facts`, `family_facts`

Three published reads that are `facts_for(conn, file_id, content_hash, field_key=…)` with a literal
argument. `facts_for` already takes `states` and `domain` filters. Add `field_key` and delete the
three. **Saving:** 3 symbols, 3 test obligations. **If wrong:** a downstream part that wants a
convenience name adds one line in its own module.

---

## Keep list — things that look like overbuilding and are not

**These matter as much as the cut list.** Two of them I began to cut and withdrew.

**`Filename` as a sixth releasable item kind (P7 Task 7) — KEEP, and round 1 F-5 should be closed
without asking Joseph.** I opened this as a cut: §8.4 names five releasable kinds
(*"selected excerpts, redacted identifiers, candidate labels, non-sensitive metadata, and evidence
references"*), puts *"Paths"* in the always-local set, and P7's own plan writes *"the design wins and
the design does not name it."* But **§7.7 names it**, in the design, verbatim:

> The model receives a compact residual dossier for each file or small homogeneous batch. **The
> dossier includes the filename**, file type, creation date, extracted text or OCR, metadata,
> sensitivity state, …

A filename is not a path. §8.4's always-local list says *"Paths"*, and §7.3's Protected-Records rule
forbids filenames only for that one template — which is exactly what P7's flagged reading builds.
The design answers OQ2 and answers it in the SPEC's favour. Round 1 F-5's remedy ("add OQ2 to NEEDS
JOSEPH") should instead be "cite §7.7 in Task 7 and close OQ2."

**`always_local_item` and `whole_document_requested` as `Denied.reason` members — KEEP.** I opened
this as a cut on round 1 F-12's second option (Task 7 makes them unconstructible, so `Gate.release`
can never return them — drop the reasons). The SPEC's own Done-means 6 decides it with one word:

> Denials are produced, with reasons, for at minimum: … **an item that resolves to a whole document**
> where a heading or excerpt exists (§8.4); … an always-local item (§8.4)

*Resolves to.* A `RequestedItem` typed `Excerpt` is constructible; whether its span resolves to the
whole unit, and whether its value resolves to one of §8.4's always-local nine, are **resolution-time**
facts that Task 9 discovers, not construction-time facts Task 7 can refuse. Round 3 A2 is the same
point from the attack side: a raw sensitive value is only recognisable through P5's signal at
resolution. Round 1 F-12's *first* option is right and the SPEC already contains the word that
settles it: Task 7 refuses the typed case, Task 9 raises the resolved case, and both reasons stay.

**P6's `unresolved` table and its thirteen reasons — KEEP.** Not in the design as a table, but §8.5's
Fact-quality measure is unambiguous — *"Did it abstain when evidence was absent?"* — and §8.5's
bundle contents include *"expected placement or abstention outcomes."* An absent row cannot answer
either. B7 is a correct derivation.

**P7's release ledger, `release_id` and single use (Task 12) — KEEP, with the honest note that §8.4
does not require it.** §8.4 requires the audit record and requires enforcement before egress; it says
nothing about capability tokens, binding tuples or replay. This is the SPEC's addition. It survives
because round 3's gate-hole attempt found it is the only thing standing between a hand-constructed
`Released` and a model call, and because it is genuinely cheap: one table, three functions. Do not
cut it. The *reducible* part is that all three binding terms get three separate `BindingMismatch`
tests where `prompt_fingerprint` plus single-use carries most of the value — but that is a test-count
argument, not a scope one, and three tests for a three-term tuple is the correct discipline.

**P6's three handed-down fact families — `families.py`, `session.py`, `photo_event.py` — KEEP as
three.** Every parameter that makes them *produce* anything is Deferred (lineage rule, session
boundary, clustering, tier weights), so in v1 they can only produce their refusals. That looked like
three modules delivering nothing. It is not: the SPEC is explicit that *"the refusal is the
load-bearing half"* — `report (1).pdf` and `invoice (1).pdf` sharing no family, a session fact never
exceeding `possible`, a missing EXIF signal contributing nothing — and §2.6, §3.9 and §8.3 each state
one of those refusals directly. **Downstream check: P9's SPEC consumes all three** (*"Universal facts
including duplicate family, version family and sensitivity status (§3.11) supply the …"* and *"Two
further P6 outputs close channels P9 could not previously source: the **bounded download session**,
…"*). Keep them separate for the same reason P5's six extractors are separate: no imports between
siblings, so one can be rejected in review without touching its neighbours.

**P6's `sensitivity status` field row — KEEP the row, assign the writer to P7.** §3.11 names it in
the universal set literally. Round 1 F-2 is right that no P6 task writes it; the scope answer is not
to delete the row but to state that **P7 writes it and P6 reads it**, which also collapses round 3
A9's arity mismatch (P6 injects `handling_class(file_id)`, P7 publishes
`SensitivityFacts.current(file_id, content_hash)` — P7's shape is the correct one, keyed to the file
*version* as §8.2 requires).

**P6's `language` universal field — KEEP.** Round 1 F-2 counted it as producerless. It is not:
§2.4 requires text-bearing extraction to store *"language where relevant"* and §2.7 requires OCR to
preserve *"languages"*, and `src/extractors/structured_text.py:64` already emits
`LANGUAGE_FIELD = 'language'` — verified with `ast`, not by scanning. The gap is that no P6 task
names the derivation, which is a one-line assignment, not a deletion.

**Both no-invention guards (P6 Task 25, P7 Task 21) — KEEP, and they are the cheapest insurance in
either plan.** They are the mechanism that makes the two Deferred tables true rather than aspirational.

---

## Merge and split recommendations

Round 2 sized tasks for buildability. This sizes them for whether a reviewer would gate on the
deliverable separately.

| Change | Tasks | Why |
|---|---|---|
| **SPLIT** P6 Task 20 into `budgets.py` and `resolver.py` | 20 → 20a, 20b | `resolver.py` is the part's single entry point and the thing every other task feeds. A reviewer gates on it independently of three ceiling keys. Round 2 B-16 reached the same conclusion from buildability; it is right from both directions. |
| **MERGE** P6 Task 1's `states.py` into `vocabulary.py` | 1 | After CUT 6, `states.py` is a re-export of a P4 tuple plus one predicate. `authorship.py` stays separate — P4 and P5 both have one and the precedent is worth keeping. |
| **MERGE** P6 Tasks 2 and the schema-creation task round 2 wants to add | 2 | Round 2's missing-task 1 proposes a new Wave-A task for `create_facts_schema`. Fold it into Task 2 as a **create** instead: `schema.py` is DDL with no logic, and a table module that cannot create its own table is the gap, not a missing task. Saves the added task. |
| **MERGE** P7 Tasks 17 and 18 (`moves.py`, `display.py`) | 17+18 → 17 | Two 2-to-4-symbol modules, both pure reads over `current_policy` + `SensitivityFacts`, both consumed only by P11/P12/P13. Neither would be gated separately. §8.4's last two paragraphs are one obligation ("do not move it, do not show it"). |
| **SPLIT** P7 Task 5 | 5 → 5a (policy + schema), 5b (`transcription_authorized_for`) | Round 2 B-20 is right: the P5 back-edge is unrelated to policy storage, is the one surface with a known arity mismatch (P5's predicate takes no scope), and belongs in its own reviewable diff. |

Net from this table: **−1 from the merges, +2 from the splits, +1 overall**, against **−3** from the
cut list — and **−4 more** from the round-2 additions the merges make unnecessary (its schema task
and its `Gate`-assembly task) and the cuts make unnecessary (its three-way split of Task 26, counted
in CUT 1).

---

## Verdict on rounds 1–4's additions

Round 4 does not exist yet. On rounds 1–3:

**Round 1 (24 findings) is almost entirely corrections, not additions, and that is the right shape
for a fidelity round.** Eighteen of twenty-four cost nothing to build: fix a citation, drop a
quotation mark, restate a count, move a fixture reference. Its build-cost additions:

| Addition | Verdict |
|---|---|
| F-1: add §3.8's four role fields (`authored_by`, `target_school`, `our_firm`, `client`) to the catalogue | **Earns its place.** §3.8 names them outright and Done-means 13 and 22 both require `authored_by` to exist. Not optional — two tests are unwritable without it. |
| F-2: add a "every published field has a producer" check to Task 25 | **Earns its place, and it is one test.** The connection contract §5 already requires it. Round 3 A16 proposes the same thing a third time, which is itself evidence it should exist. |
| F-3: add a fourteenth `unresolved` reason, `equal_rank_contradiction` | **Rejected.** After CUT 6 removes the five-rank ladder, "equal rank" is not a state the code can be in: §3.6's predicate has two tiers, and two contradicting `validated` facts are refused by `contradicted_by_stronger_fact` failing, which is `no_candidate_evidence`'s territory or a plain refusal to fill. F-3 is a real hole *in the ladder*; deleting the ladder is cheaper than adding a vocabulary member to patch it. |
| F-9: injected `completeness → unreadable_unclassified` mapping + a Deferred row | **Earns its place.** Eight of nine values have no stated mapping and the mapping decides whether a real file is releasable, in a part whose first constraint is that it owns no detection rule. This is the correct application of the plan's own discipline. |
| F-12: drop `always_local_item` from `DENIAL_REASONS`, or state the split | **Half rejected.** The drop is wrong (see keep list — Done-means 6 says *resolves to*). The split is right and needs one sentence. |
| F-14, F-23: pin `field_key` spelling; pin `unclassified` vs `unreadable_unclassified` | **Earn their place.** Both are defect class 1, both are one edit. |
| F-5: add P7 OQ2 to NEEDS JOSEPH | **Rejected — §7.7 answers it.** See keep list. |

**Round 2 (20 findings, 11 "missing tasks") is where the bloat enters, and about half of its
additions are downstream of one decision this round reverses.** Missing-tasks 3 (pass-record table)
and 8 (two new public entry points in `extractors.dispatch`), plus the three-way split of Task 26 and
findings B-1, B-2, B-12, B-14 and B-19, all exist because Task 26 exists. **CUT 1 deletes seven
findings and two missing tasks in one move.** Of the rest:

- Missing-tasks 1, 2, 4, 5, 6 (schema creation, `conftest.py`, `ResolveResult`, the P7/P8 injection
  points, the §3.2 fixture home) — **all earn their place, and none is a new task.** Each is a
  `Files:` line or a `Produces:` line that was omitted. Fold them in; do not spawn tasks for them.
- Missing-task 7 (the writer check) — earns its place, same as round 1 F-2.
- Missing-task 9 (a task to assemble the `Gate` facade) — **rejected; CUT 4 deletes the facade
  instead.** This is the clearest case of a review adding a task to serve an abstraction that should
  not exist.
- Missing-tasks 10, 11 — earn their place; 11 becomes trivial under CUT 1, since the orchestrator's
  `handling_class=None` is then the only line in play and P6's resolve loop is its natural owner.
- B-9, B-16, B-20's splits — B-16 and B-20 endorsed above; B-9 dissolved by CUT 4.

Round 2's own closing note asks round 5 to read its splits as *"this task does three things", not as
"this task is overbuilt"*. Fair, and mostly honoured. The exception is Task 26, where the task doing
three things and the task being unnecessary are the same finding seen from two angles.

**Round 3 (17 findings) is the most valuable of the three and its additions are the smallest.** Its
executed proofs — the `vars(module)` demonstration under A6, the `FactPassNotRun` → `failed` trace
under A1, the sensitivity-signal mis-keying under A2 — are each worth more than a page of argument.
Its additions:

| Addition | Verdict |
|---|---|
| A6: one shared `code_tokens()`-style AST helper, imported by both no-invention tests | **Earns its place, and it is a net simplification.** It replaces *nine* separate obligations that the specified instrument cannot enforce with one helper written once. The brief for this round says "never assert a token is absent by scanning source text"; A6 is the finding that both plans specified an instrument that cannot do the job the ban requires. |
| A8: a fourteenth reason `producer_unavailable` | **Rejected as stated, but the question is real.** Note that **round 1 F-3 and round 3 A8 propose two *different* fourteenth reasons** — if both land, Task 5's test ("exactly thirteen; a fourteenth is refused") becomes "exactly fifteen," and the closed vocabulary has been opened twice by two reviews that did not read each other on this point. That is the bloat mechanism in miniature. The underlying question — *what does P6 write for an LLM-only field when no model is configured* — is genuine and belongs in NEEDS JOSEPH, not in a vocabulary member added by a reviewer. |
| A13: one `basis_key` serializer, owned by P1 | **Earns its place, emphatically.** Two parts serializing one key with a reader that fails **open** is the highest-damage small defect in the wave. One function in P1, beside the column. |
| A9: P6 consumes `SensitivityFacts.current(file_id, content_hash)`; P7 adds the Contract-out row | **Earns its place.** Two-line edit each side, and it fixes a version-keying error, not just a name. |
| A14: `audit_records_for` queries the JSON explanation, plus a group fixture | **Earns its place.** `EVENT_FIELDS` has one `file_id`; a group release of twelve files writes one row; the consumer is the retraction limit. A user told their file was never sent, when it was, is the exact failure §8.4's audit exists to prevent. |
| A15: `assert_single_egress` AST-walks the body; a fifth fixture | **Rejected — CUT 2 removes the instrument.** A15 is correct that the checker as specified proves the wrong thing; the conclusion is that P7 should not ship it. |
| A11: move `display_label`/`aliases` off `values` into Task 23's table | **Rejected — CUT 3 removes Task 23.** A11 correctly identifies the contradiction and picks the more expensive resolution. |
| A10: state the `sensitivity_state` vocabulary; assert the value not non-nullness | **Half earns its place.** The value-not-nullness assertion is right and costs nothing. The vocabulary statement is dissolved by CUT 5. |
| A12: `passes_for` reads a union; `first_evidence_ref` is `min(observation_key)` | **First half dissolved by CUT 1. Second half earns its place** — `first_evidence_ref` is write-order-dependent today and the plan's own sort-before-you-decide rule already covers it everywhere else. |
| A16: the writer check | **Earns its place** (third proposal of the same test). |
| A3, A4, A5: `ModelCallRequest` has no `content_hash`, no group expansion; the current-row rule; `protected_records_template` has no input | **All earn their place.** Three of the four successful gate-hole attacks. Adding `content_hash` to a seven-field request and stating a group-expansion rule is the smallest possible fix for the largest possible hole. |

**Net across three rounds, after this round's filter:** roughly **+6 field rows and vocabulary
members, +4 injected or published symbols, +3 shared test helpers, +2 P1 functions, and zero new
tasks** — against the **+6 tasks, +1 table and +1 P5 contract revision** the rounds proposed as
written.

---

## Deferrable past v1

Neither breaks the walking skeleton (`02-segmentation-map.md`'s P6 step is *"resolve it to ONE
validated fact (course = X) with its evidence link"*, which needs Tasks 1–13 and 27 only) nor any
§8.4 guarantee.

| Deferrable | What it costs to add later |
|---|---|
| **The whole targeted-OCR path** (CUT 1) — the four passes, the pass record, `FactPassNotRun`, the P5 dispatch surface | Round 2's three-task split, built against a live engine. **Cheaper later than now**, because the tests can observe a real OCR run instead of a synthesised exception. |
| **P6 Task 22's write half** (`record_correction`) | §8.7's corrections arrive through P13's `review_action`, and P13 does not exist. Keep the **read** (`is_suppressed` + `basis_key`) — §8.7's *"Rejected … must be stored"* binds now and the query-before-propose guard must exist before any fact is written. Defer the writer to P13's wave, and let P1 own `basis_key` per A13. Cost later: one function, in the part that collects the gesture. |
| **P7 Task 15's `delete_derived`** | Shipping a symbol whose only behaviour is to raise `UnratifiedResolution` reserves a name in code for a decision (I6) that Joseph has not made. Nothing consumes it. `revoke`, `retraction_limit` and `prior_releases` — the parts §8.4 requires — stay. Cost later: the function, once I6 is ratified, which is when its semantics exist. |
| **`file_facts.internal_score` and `cited_quote_refs[]`** | Both are columns with no writer in a P8-absent deployment (round 3 A16). §3.13 permits internal scores (*"may calculate"*) and does not require them; `cited_quote_refs` is the LLM path only. Declare them in the Deferred table rather than in the DDL. Cost later: two `ALTER TABLE`s, or simply declaring them now with a Deferred row — which is what the connection contract §5 asks for and is the cheaper of the two. |

---

## NEEDS JOSEPH

Verbatim, unresolved, and not answered here. Only what this round adds or re-scopes.

**1. Does targeted OCR ship in v1?** This is P6's own NEEDS JOSEPH 1 and this round changes the
recommendation. P6's plan recommends *(a) build the four passes now and wire an engine when P5's
question is settled — the restructure is free and the seam is proven*, on the argument that *"with
`readers.ocr_engine is None` … loops 3 and 4 are no-ops and the restructure costs nothing until an
OCR engine is actually wired."* **Round 2 proved by execution that this claim is false** (loop 1's
raising verdict becomes `completeness = failed` on every text-bearing PDF; loop 3 has no entry
point), and **round 3 proved the guard is green and inert.** The restructure is not free and it
cannot be tested without an engine. **This round recommends (b): ship v1 with no engine, keep
`TARGETED_OCR_UNAVAILABLE` as the honest statement of that posture, and build the four passes in the
phase that chooses an engine.** The decision is downstream of P5's still-open NEEDS JOSEPH 1 (*Apple
Vision only; macOS-only for v1*), and it should be made at the same time as that one.

**2. Does P10 own §8.8's "User labels and aliases", or does P6 also?** P10's SPEC assigns the row to
P10 by name and gives its node record a `display_label`; P9 keeps its own `user_edited_label` per
plan version; P6's Task 23 builds a third. **Confirming P10 as the sole owner deletes a P6 task.**
The narrow residue: is §2.8's *"the user may later choose to display it as `UChicago`"* — a rendering
of a **value** — the same thing as §8.8's plan-versioned user label, or a different one? This round
reads them as different and P6 keeps the un-versioned value rendering.

**3. Is P7 shipping an instrument for P8's Done-means 1?** P7's Contract-out offers
`assert_single_egress` to P8; **P8's SPEC never names it** and states its own method (*"Verified by
inspection plus a test that the un-released path does not type-check / does not exist"*). One of the
two SPECs should change. This round recommends P7 drop the offer and P8 keep its own method — which
is also the only version that can check the function *body*, and round 3 A15 proved the body is where
the hole is.

**4. Will P1 publish `set_sensitivity_state`?** P5 reported the identical gap for
`extraction_status_by_tier` and P1 published `set_extraction_status`. P7's plan injects a writer
instead of asking. The injection is what lets `handling_class = file_row["sensitivity_state"]` become
the shortest edit that passes Task 22 — restoring exactly the line the 2026-08-21 pass removed.

**5. What does P6 write for a field only the LLM could fill, when no model is configured?** Carried
forward from round 3's item 1 unchanged, because it is Joseph's and not a reviewer's. It is a real
question and it should be answered as a SPEC sentence, **not by a fourteenth `unresolved` reason
added by a review** — two rounds have now proposed two different fourteenth reasons for two different
holes, and Task 5's own test says a fourteenth is refused.

**6. Are §3.8's four role fields in the catalogue?** Round 1 F-1, carried forward because it is the
one member of the F2/F3/F4 naming family where the design states the field outright rather than
stating two names for one thing, and because two Done-means items are unwritable without it. It is
the only round 1 addition that is strictly required to build.

---

## What this round did not look at

Contract fidelity (round 1), buildability (round 2), defect-class reproduction (round 3), and
connection to built P1–P5 (round 4, unwritten). Where a cut here removes a finding from an earlier
round, that is said in the cut's own entry, so a reader reconciling the five rounds can see which
findings were fixed and which were deleted.
