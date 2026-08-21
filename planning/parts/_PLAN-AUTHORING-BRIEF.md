# Plan-authoring brief — read this before writing any P6 or P7 task

Date: 2026-08-22
For: every agent writing a section of `P6-facts-facets/PLAN.md` or `P7-privacy-consent-gate/PLAN.md`.

You are writing **one or two tasks** of an implementation plan. This file is the shared context so
you do not have to rediscover it, and so every section comes out consistent.

---

## 1. How to spend your time

You are writing a **plan document**. You are **not** implementing the part.

- **Create nothing under `src/` or `tests/`.** Do not build a prototype. Do not execute the
  implementation code you write. Four agents have already died doing this — one stalled ten minutes
  at *"let me write the Task 3 test and verify it runs"*, another at *"I'll build a runnable
  prototype to verify every line of code before writing the plan"*. The instinct is right and the
  budget will not survive it.
- **Write no preamble.** No title, no "what already exists", no "verified live" section, no shared
  rules. Start your file directly at `### Task N: <the skeleton's exact title>`. The assembled
  `PLAN.md` gets one shared preamble, written once, by the lead. Agents writing their own preamble
  is what has been eating the budget that should go into the task.
- **Write incrementally.** Write the first task, then append the second. A cut-off then costs one
  task instead of the file.

**Two things you SHOULD verify, because they are cheap and they matter:**

```bash
# 1. every P1-P5 signature you consume
cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -c "import inspect; from evidence_shape.store import observations_for_run; print(inspect.signature(observations_for_run))"
# 2. every design sentence you quote
grep -c "the exact words you are about to quote" planning/00-database-agent-product-design.md
```

Nothing else needs running.

---

## 2. Format — the standard is `P4-evidence-shape/PLAN.md`

Read two full tasks of it before you start. Every task you write needs:

- `**Files:**` — exact create / modify / test paths
- `**Interfaces:**` — `Consumes:` and `Produces:` with exact signatures
- `**Done-means:**` — which numbered Done-means items this task satisfies
- Numbered `- [ ] **Step N: ...**` steps, each 2–5 minutes
- **Complete runnable test code** in a fenced `python` block
- A step that RUNS the test and states the expected **FAILURE**
- **Complete implementation code** in a fenced `python` block
- A step that runs it again and states **PASS**
- A commit step with the exact `git commit -m` line

**NO PLACEHOLDERS, EVER.** No stubs, no ellipses, no "similar to Task N", no "add appropriate error
handling". A task that cannot be written out in full was decomposed wrong — say so in the file
rather than writing a stub.

The code must be complete and correct **as written text in the plan**. It is not executed by you.

---

## 3. Sources, in precedence order

1. **`planning/00-database-agent-product-design.md`** — Joseph's wording is authoritative.
   **Never invent a quotation.** Grep the exact string before you quote it. Fabricated quotations
   are this project's most-repeated defect: four were found and fixed this week, including one
   attributing to §0 a sentence the design does not contain.
2. The part's `SPEC.md`.
3. The part's `PLAN-SKELETON.md` — **read the "Ratified decisions" block at the top first**, then
   your task's block. **Each task's `Interfaces:` block is a CONTRACT** with the other agents
   writing in parallel. Honour those names and signatures exactly; rename nothing.

---

## 4. The ratified decisions — binding on every task

| | Ratified | Effect |
|---|---|---|
| **D6** | The academic field key is **`subject`**, and every stored field key is `snake_case`. | **P6 OQ4 is CLOSED.** The catalogue carries `subject` and **no** `course` row. §3.11's word "course" is the design's prose for the same field and survives inside quotations only. |
| **D2** | P7's **`ClassificationRecord`**, keyed `(file_id, content_hash)`, is **authoritative**. `files.sensitivity_state` is its **projection**, written through P1's published `set_sensitivity_state`. `Unreadable or unclassified` is a **gate outcome, not a file fact** — it never enters that column. | **P6 OQ11 is CLOSED.** P7 takes **no** `SensitivityStateWriter` and **no** injected `SensitivityFacts` protocol. |
| **D5** | **P6 Task 26 is CUT.** No `dispatch` split, no `run_wave2` restructure. | P6 touches **no file outside `src/facts/` and `tests/p6/`**. |
| **D1** | Narrowed: *"acquiring one fails the test"* is struck; no career fields authored. | §3.8's four role fields (`authored_by`, `target_school`, `our_firm`, `client`) **are** in P6's catalogue — Done-means 13 and 22 require `authored_by` to exist. |
| **D3** | `events` append-only forever; derived projections may be tombstoned; "derived" is a **literal enumerated list**; **no writer-less tombstone column**. | P7 Task 15's `delete_derived` raises because nothing is *built*, not because the semantics are *unratified*. |
| **D4** | `jurisdiction` is a **value, never a field name and never a destination dimension**. | No jurisdiction-specific field key anywhere. |

### Field-naming rulings, resolved 2026-08-22

- **`capture_date` and `capture_year` are two different fields.** `capture_date` is the EXIF-derived
  fact (§3.2: *"an EXIF field called DateTimeOriginal is raw metadata; capture date = 2026-07-17 is
  the file fact derived from it"*); `capture_year` is the Photos **destination dimension** (§3.11).
  Neither is `creation_date`, which §3.2 separates by name. Both exist.
- **`document type` is never a key.** It is the design's generic word (12 uses) for whichever
  specific field the active domain declares — `application_document_type` (College applications) or
  `artifact_type` (Research/Code).
- **The tie-break rule is not "prose wins".** It is: **one stored key per concept; every other word
  the design uses for it becomes an alias, never a second key.** Which word becomes the key is
  decided per concept on the evidence.
- **Suppression vs demotion.** A generic TOOL string (`python-docx`, `Mozilla/5.0`, a browser
  producer string) is §2.2's **suppression** tier — *no fact in any field*, plus one `unresolved`
  row with reason `discounted_tool_metadata`. A HUMAN name is §3.8's **demotion** tier — it becomes
  `authored_by`, retained as supporting evidence, **never destination-eligible**. Different
  outcomes; Done-means 22 asserts both halves.

---

## 5. The one thing that must not be built (P6)

Task 19 has P6 raise `FactPassNotRun`, which inherits `extractors.failure.ContractViolation` and
therefore **always propagates**, when the verdict is consulted for a `(file_id, content_hash)` whose
deterministic pass has not been recorded. That is correct.

But **Task 26 is cut**, so nothing rewires `src/orchestrator.py`, and
`extractors.ocr_policy.text_layer_state` consults `no_usable_facts` for **every text-bearing PDF**
inside the caller's single loop, before any deterministic pass could have run.

> **If P6's resolver is ever passed to `run_wave2` as `no_usable_facts`, the first text-bearing PDF
> ends the scan.**

The caller keeps passing `orchestrator.TARGETED_OCR_UNAVAILABLE`. P6 publishes
`no_usable_facts_for(conn, *, usable_threshold)` as a **read surface its own tests exercise**.
Wiring it into the caller is separate later work and must not be done as "integration".

---

## 6. Hard constraints

- **Python 3.12, stdlib only** in `src/facts/` and `src/privacy/`. Third-party libraries live in
  `src/readers/` behind the `readers` extra, and neither part may import one.
- **No invented thresholds, weights, gazetteers, regex catalogues or producer strings** as
  module-level constants. Every threshold is injected with no default. Both parts' guard tasks
  assert this **by runtime introspection**, not by source-text search — a text search matches
  comments and docstrings, and scanning text for a token has produced a false result nine times on
  this project.
- **P6** writes only `src/facts/` and `tests/p6/`; mints **no new §8.2 event type**; no module
  branches on `source_type` or `extractor_name`; `subsystem = "P6"` appears in exactly one place.
- **P7** creates and owns its own tables inside P1's single database; modifies no P1–P5 file;
  invents no handling class; imports **none** of `extractors`' three refusals
  (`ProtectedContainerRefused`, `DatalessRefused`, `ContractViolation`).
- **`planning/domains/` is NOT P6's field catalogue** and `src/facts/` must never import it. It is a
  separate research artifact. P6's `FIELD_ROWS` is a small authored module-level table; its content
  comes from `planning/domains/canonical_fields.json` (37 canonical keys), which is a **source to
  read**, not a runtime dependency.
- **Do not edit anything under `planning/domains/` or `planning/deferred-catalogues/`.** Another
  agent owns those and is working right now. Read only.

---

## 7. What is still open — hold these open, do not resolve them

- **NEEDS-JOSEPH C24** (renumbered from C5, which was already taken) — whether P6 keeps a `sensitivity_status` field row. P7's SPEC Contract-in
  says *"P6 must accept `sensitivity` as a first-class universal field"*; D2 makes P7's record
  authoritative; round 1 found the field has no producer. **Create no such row either way.**
- **NEEDS-JOSEPH C22** (renumbered from C3, which was already taken) — P4's `norm` region unit does not say which corner it measures from. Vision
  is bottom-left, most tooling is top-left. Redaction reads these boxes. Assume no origin.
- **`filename` as a sixth releasable kind** — §8.4 names five and puts *paths* in the always-local
  set; P7's SPEC adds a sixth and flags it itself (NEEDS-JOSEPH B5d/C9a).
- **Round 4's C-5** — P8's Contract-in names `normalize(field, raw_value)` and
  `contradicts(claim, existing_fact)` as P6's; P6 Task 17 disowns both. Each part hands them to the
  other, so neither builds them. Name the gap; do not invent them into P6.
- **The detector does not exist.** D2 puts P7's rule set behind an injection and no task produces
  one, so on a real corpus **every file resolves to `Denied(unclassified)`**. Build that as the
  ordinary path. Never default an absent classification to a public/low class.

---

## 8. Substrate you are planning against

P1–P5 and the Wave-2 caller are shipped and green: **1300 tests**. P4's 19 golden fixtures
(`evidence_shape.fixtures`) mean P6 is buildable with **no extractor present** — use them. Plan
against live signatures, never against a reconstructed stub: doing the latter cost this project a
whole class of defects in P4/P5.

---

## 9. Round 5's seven cuts — one ratified, six NOT. Write the task; flag the cut.

`planning/overnight/reviews/round-5-scope.md` recommends deleting seven things. **Joseph has ruled
on exactly one.** The rest are live recommendations against tasks this brief tells you to write, and
an author who does not know that will produce a confident plan for work that may be deleted.

| Cut | Target | Status |
|---|---|---|
| **CUT 1** | P6 Task 26 — the four-pass orchestrator restructure | **RATIFIED (D5). Do not write it.** |
| **CUT 2** | P7 Task 19 — `transport_guard.py`, `assert_single_egress` | **NOT ruled.** §8.4 states a property, not a static analyser; no sentence asks for one. |
| **CUT 3** | P6 Task 23 — `plan_versions.py` | **NOT ruled.** |
| **CUT 4** | P7's `Gate` facade as a seven-method object | **NOT ruled.** Touches Task 11. |
| **CUT 5** | P7 Task 4's `SensitivityStateWriter` and `mirror_state` | **Resolved by D2** — the injected writer is gone; P1 publishes `set_sensitivity_state`. |
| **CUT 6** | P6's `STRENGTH_ORDER` / `strength()` / `is_stronger()` five-rank ladder | **NOT ruled.** Touches §3.13 ordering wherever it appears. |
| **CUT 7** | P6 read surface — `event_facts`, `session_facts`, `family_facts` | **NOT ruled.** Touches Task 24. |

**What to do if your task is a cut target.** Write it in full, to the same standard as any other
task — an unratified recommendation is not a decision, and a half-written task is worth nothing to
either outcome. Then add a short, prominent callout at the top of that task naming the cut, its
argument in one sentence, and the fact that it is unratified. Assembly needs to find these; a
reader deciding the cut needs the plan in front of them to decide against.

**Do not silently comply with a cut, and do not silently ignore one.** Both are the same failure:
a decision made by an author instead of by Joseph.

## 10. The `SensitivityFacts` rename applies to EVERY task that names it

The settled D2 paragraph in P7's skeleton names Tasks 4, 12, 13 and 14. That list is incomplete —
**Tasks 17 and 18 also carry `facts_seam.SensitivityFacts` in their `Consumes`.** The rule is not a
list of task numbers; it is: wherever `facts_seam.SensitivityFacts` appears, read
`classification_store.ClassificationStore` — a concrete store over a table P7 owns, no injection,
no protocol, no fixture standing in for P6.

---

## 11. The six reliability states — NAMED CONSTANTS, ruled 2026-08-22

A cross-section conflict, caught by a Task 7–9 author reading a sibling section. Both halves were
wrong, in opposite directions:

- `PLAN-tasks-14-15.md` writes `reliability_state="direct"` and `="possible"` as **string literals**
  (four sites). That is a second home for a vocabulary Task 1 publishes — the defect class that has
  cost this project the most.
- The Task 7–9 author avoided the literal by writing **`STATES[1]` / `STATES[4]`**, which is
  single-homed and unreadable, and silently couples every consumer to the tuple's ORDER. Reordering
  the tuple would then change meanings with no test failing.

**The ruling, and it is the repo's own precedent, not a new invention.** P5 publishes
`POTENTIALLY_SENSITIVE = "potentially sensitive"`; P1 publishes `SUPERSEDED_CONTENT =
"superseded_content"`. So:

> **Task 1 publishes the six states BOTH ways: `STATES: tuple[str, ...]` for iteration and
> membership, AND one named constant per state (`DIRECT`, `POSSIBLE`, `VALIDATED`, `LLM_SUPPORTED`,
> `USER_CONFIRMED`, `REJECTED`). Every other module imports the NAMED CONSTANT.** Never a bare
> string, never an index.

Task 1's guard becomes: **no string literal spelling a state name appears anywhere in `facts`
outside the module that publishes them.** A named constant passes it and reads correctly; an index
passes it and does not. Authors of Tasks 14 and 15 — this supersedes the literals already written
there; the assembled PLAN will carry the constant form.

The same rule applies to every closed vocabulary either part publishes, P7's handling classes and
denial reasons included.

## 12. Two gaps reported by authors — carry them, do not close them

- **§3.5's content-hash slot has no producer.** `src/extractors/filesystem.py` deliberately emits no
  content-hash observation, so a content-hash fact has nothing to cite, and P6's rule 1 forbids an
  uncited fact. Task 8 supports the slot when a caller supplies one and passes an empty tuple in
  production. The fact the hash actually supports is Task 14's duplicate family. **Consumer with no
  producer** — the class round 4 was built to find.
- **Catalogue `12-academic-capture-patterns/04-narrow-date-families.json`** (another agent, authored
  2026-08-22) supplies the EXIF and labeled-date slot families and names *"Task 8's direct-fact slot
  list"* in its own `owner` field. That is a real cross-agent join and it half-closes F8. Title and
  content-hash slots still have no catalogue. Read it; do not edit it.


---

## 13. The L2 guard set is WRONG in the skeleton — measured, 2026-08-22

P7's skeleton says the packages binding a P4 text materialiser are
`{evidence_shape, extractors, privacy}`. Two independent agents flagged it and I confirmed it by
introspection:

- **`extractors` binds NONE of them.** A guard that names a package binding nothing passes forever
  while checking nothing — the same shape as a column with no writer.
- **`orchestrator` binds `text_units_for_run`** (the bundle copy), and the skeleton omits it.

The true set is **`{evidence_shape, orchestrator, privacy}`**. Task 21 must assert that, with a
stated reason per binder, and must **refuse to rule on the orchestrator's binding** — whether the
caller may materialise text into a bundle is P7's own OQ8, which is open.

## 14. Cite NEEDS-JOSEPH by its CURRENT labels

My earlier additions to `planning/overnight/NEEDS-JOSEPH.md` were numbered C1–C6 and collided with
the pre-existing C1–C14. They are now **C20–C25**. In particular:

| Question | Correct label |
|---|---|
| Does P6 keep a `sensitivity_status` field row? | **C24** (was cited as C5; C5 is "is `protected` exactly the top two handling classes?") |
| P4's `norm` has no origin | **C22** (was cited as C3; C3 is "what is a corpus area?") |
| `SensitivityFacts` has nothing on the other side | **C25** |
| `filename` as a sixth releasable kind | **B5d** and **C9a** — these were always right |

If a citation and a substantive question disagree, **follow the substance and quote the passage that
actually contains it**, as one author correctly did rather than propagating my wrong label.

---

## 15. Cross-task demands raised by finished sections — binding on the tasks named

These came from authors discovering that a neighbour's published surface cannot carry what their own
task needs. Each names a task someone else owns. **Honour them; do not renegotiate them silently.**

| Demanded of | What, and why |
|---|---|
| **P7 Task 10** | `append_audit` needs one new keyword, `extra: Mapping \| None`, merged into the same `explanation` JSON. SPEC §7 enumerates a **release** record and has no field for a **denial's** reason, so Task 13 cannot record why it denied. |
| **P7 Task 10** | `audit_records_for(file_id=…)` must match the `explanation` too, not only the `file_id` column. `events` has ONE `file_id` column, so a group-scoped release stores its ids in the explanation — otherwise Task 15's `prior_releases` under-reports every group release, and §8.4's retraction limit stops being "truthful and specific". |
| **P7 Task 11** | `Denied` needs a fourth field, **`evidence_refs`**. The skeleton's own `deny(...)` takes them and SPEC §6 requires an evidence-referenced explanation, but Task 11's `Produces` omits the field. |
| **P7 Task 11** | The import direction is fixed: `release.py` imports only `consent`; `binding` uses `TYPE_CHECKING`; `gate.py` holds the logic. Tasks 12–14 all need Task 11's branch types while `Gate.release` needs all three, so without this rule the four tasks form a cycle. |
| **P7 Task 5** | `policy.grant_consent` **appends no event** — the exact mirror of the already-written ruling for `revoke_consent`. Task 5's `Produces` spells the signature with an ellipsis; pin it. |
| **P7, any table** | Add **no `BEFORE DELETE` trigger** to a P7 table. Task 15 asserts exactly **thirteen** tables refuse a delete; a fourteenth fails a sibling's test. |
| **P6 Task 25** | The no-import guard must permit exactly one edge: `facts` imports `ContractViolation` from `extractors`. `FactPassNotRun` must inherit it or the orchestrator's catch-all swallows the guard into a `failed` run and it stops guarding. |
| **P6 Task 6** | `facts.cache` is Task 6's and **no other task may add to it**. Two cache-key rules currently exist across sibling sections — one keying a fact on its cited observations, one keying the pass on the file version's whole evidence set. Task 6 publishes one helper; the abstention case forces the pass-level rule, because an `unresolved` row with no citations still needs a key. |
| **P6 Task 11** | `fill_or_abstain` must treat an absent second-best as score zero. A sibling wrote that as a test rather than prose, so a disagreement fails `test_a_missing_signal_contributes_nothing_to_either_candidate` instead of merging silently. |
