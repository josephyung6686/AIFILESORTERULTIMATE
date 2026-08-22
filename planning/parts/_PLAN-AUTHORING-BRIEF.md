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

P1–P5 and the Wave-2 caller are shipped and green: **1302 tests** (1300 until D10's two landed in `87016b0`). P4's 19 golden fixtures
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

---

## 16. Two more corrections, and one that needs Joseph

**My skeleton is wrong against live P4.** Task 1's spec says `validate_observation` raises
`NonConforming` on a bad `reliability`. It raises **`NotInVocabulary`** — verified by execution, and
the two classes are unrelated. Write tests to the live behaviour, not to my sentence.

**A guard I specified would have broken three sibling tasks.** Task 1's "no string literal spelling
a state name" guard, read literally, also forbids `VERSION_FAMILY_STATES`, `SESSION_STATE`,
`EVENT_STATE` and `LLM_STATES` — collections siblings legitimately publish inside `src/facts/`. The
guard's real target is narrower: **no module other than the one publishing them may bind a
collection whose members ARE the six states.** By runtime introspection, as always.

**A trap worth carrying forward:** `FORBIDDEN_COLUMN_SUBSTRINGS` must not be run against the
`fields` table — the legitimate column `destination_eligible` contains the substring `destination`.

### NEEDS JOSEPH — `destination_eligible` for `target_school` and `client`

My skeleton says **all four** of §3.8's role fields are `destination_eligible = FALSE`.
`planning/domains/canonical_fields.json` (the other session's R1a catalogue) says `target_school`
and `client` are **TRUE**. A P6 author resolved it toward the skeleton on precedence and recorded
the reasoning rather than burying it — correctly.

**I think the catalogue is right and my skeleton over-applied the rule.** §3.8's sentence is
*"It should avoid using authorship or creator identity as a destination dimension."* `authored_by`
and `our_firm` are authorship and creator identity. `target_school` — the school you are applying
TO — and `client` — whom the work is FOR — are the **other side** of the role split, and a client
folder is an ordinary destination.

This is not mine to settle: it decides whether P10 can build a folder template on those two keys.
**Both readings are written down; a P6 author is currently building the stricter one.**

---

## 17. Two lead rulings, 2026-08-22

### `field_key`, not `field_id`. One name, one meaning.

The SPEC's `fields` table publishes **`field_key`** as its stable identifier and declares no
surrogate key. The SPEC's `values` / `file_facts` shapes and the skeleton's `ValueRow` name the
foreign key **`field_id`**. Two authors independently resolved it the same way — keep the column
named `field_id` and store the field *key* in it.

**That is the worst of the three options and I am overruling it.** A column named `_id` holding a
key is a name that lies about its content, and this project's most expensive defect class is one
concept wearing two names. It cost us `subject`/`course`, spaced-vs-snake keys, and `capture
date`/`capture year`.

> **The column is `field_key` and it holds the field key, in `values`, in `file_facts`, and in
> every signature that takes one.** The skeleton's `field_id` is the error, not the SPEC.

Sections already written against `field_id` — including a read of `old["field_id"]` — are corrected
at assembly. Whether `fields.field_key` is declared PRIMARY KEY is still Task 2's, and it matters:
`PRAGMA foreign_keys` is ON and an FK to a non-PK/UNIQUE parent raises `foreign key mismatch` at
INSERT, not at DDL.

### `tests/p6/conftest.py` belongs to Task 1

Nobody owned it. Two sections assume `p6_conn` exists and no task's `Files:` line creates it — a
fixture with no producer, in the plan for the part whose guard task exists to catch exactly that.

> **Task 1 creates `tests/p6/conftest.py` and publishes `p6_conn`.** It is the package-skeleton
> task, it runs first, and every later task consumes it. Any other task carrying a copy becomes
> *verify it exists, do not duplicate it*.

### Carried, not ruled

- **`content_hash` is missing from the SPEC's `file_facts` shape**, and `facts_for_file(conn,
  file_id, content_hash)` — the skeleton's own published signature — is unimplementable without it.
  Added by its author and flagged. The SPEC owes the column.
- **`CREATE TABLE values` is a SQL syntax error.** `values` is a reserved word; every statement must
  quote it `"values"`. One unquoted statement breaks `create_facts_schema` and therefore every later
  P6 task. Found by execution, not by reading.
- **`display_label` had no writer** — the SPEC's `values` shape carries it and no published function
  sets it. Same no-producer defect as `sensitivity_status`. A `set_display_label` was added as a
  named addition; its §8.8 plan-version scoping is deliberately NOT built.

---

## 18. Late findings, and a second duplicate

**Tasks 8 and 9 exist twice** — in `PLAN-tasks-07-09.md` and `PLAN-tasks-08-09.md`. Same cause as the
P7 15–22 overlap: I dispatched from an inventory that was stale because the first author was still
writing. Reconcile at assembly; neither is wrong.

**Only two of §3.5's four direct slots can reach a fact today.** `extractors.filesystem.METADATA_SLOTS`
is `("normalized_filename", "extension", "mime_type")` — **no timestamp**, so §3.13's filesystem-timestamp
slot has no publisher. And §3.5's **content-hash** slot cannot produce a fact at all: M14 admits no
citation that is not an `observation_key`, and P1's `files.content_hash` is a column, not evidence.
Consumer with no producer, twice, in the design's own worked list.

**Catalogue 01's `boundary_rule` is English prose with no machine-readable form**, and 102 of its 115
entries are `prefix` or `regex`. Task 9 correctly takes *compiled predicates* so `facts` holds no
regex catalogue — which means **something must compile 115 entries and no task in P6's plan does**.
It belongs with the loader, beside the flattening of `property_names`.

**`target_school` (§3.8) and `target university` (§3.11) are one concept with two keys**, and
Done-means 2 requires both. That is the `subject`/`course` shape again, unresolved, and it should be
settled by §17's rule: one stored key per concept, the other word an alias.

**The §3.4 cache-key rule is now copied seven times across sections.** One helper in `facts.cache`
(Task 6's module) taking `(conn, content_hash, observations)` deletes all seven.

---

## 19. A gate bypass in the written Task 11 — fix before any P7 code is written

Raised by the Task 7 author, reading Task 11's already-written implementation.

`Gate._materialise` does:

```python
if not isinstance(item, TEXT_BEARING): continue   # <-- BEFORE the check
check_item(item, unit_length=…)
```

**Every non-text-bearing item skips `check_item` entirely** — `MetadataField`,
`CandidateLabel`, `EvidenceReference` and `Filename` are never checked at all.
`PLAN-tasks-15-22.md`'s own fixture 7 is *"GPS requested as an item"*, and under this ordering it
would be **released unchecked**. §8.4's whole requirement is that the gate is the only door; a door
that inspects only the items it expects to be dangerous is not one.

Second, smaller, same function: the call is `check_item(item, unit_length=…)` positionally, which is
a `TypeError` under the published `check_item(item, *, unit_length, protected, sensitive_keys,
allow_unratified)`.

**Check every item first; filter by kind afterwards, if at all.**

## 20. Task 7 exists twice, and the two versions conflict on field shapes

`PLAN-tasks-04-07.md` (line 2414) and `PLAN-tasks-07.md` both carry a `### Task 7`. My overlap
again. They disagree on three shapes, and **the 04-07 version is unbuildable**:

| | 04-07 | 07 | Which is right |
|---|---|---|---|
| `MetadataField` | `(name, value)` | `(name)` | **07.** SPEC §6: `requested_items[]` are *"references only, never materialised content"*. A `value` IS materialised content. |
| `Filename` | `(file_id, value)` | `(file_id)` | **07**, same reason. |
| `span` | non-optional | `TextSpan \| None` | **07.** Task 9 pins it optional for the container-path form; its own test fails on construction otherwise. |

**Take `PLAN-tasks-07.md`'s field lists.** The rest of the two sections agree.

## 21. One more reported contradiction, not resolved

`PLAN-tasks-20-22.md` reaches `Denied(always_local_item)` via an `Excerpt` in the `ocr` **zone**. But
§8.4 permits *"a short heading or OCR excerpt"* in the same sentence that makes OCR output
always-local, so `items.py` does not branch on zone and will not deny it. The fixture should stand on
a P5-signalled key instead. Reported by its author rather than patched into either file.

---

## 22. Task 11: take `PLAN-tasks-11.md`. It does not have the bypass.

Both files carry a `### Task 11`. Verified by reading both:

- **`PLAN-tasks-08-11.md`** filters `if not isinstance(item, TEXT_BEARING): continue` **before** its
  only `check_item` call — §19's bypass. GPS-as-an-item is released unchecked.
- **`PLAN-tasks-11.md`** runs a **precheck over every item with no filter**, catching
  `AlwaysLocalRequested` and `ProtectedItemRequested`, and then a separate `_postcheck_items` where
  the `TEXT_BEARING` filter is correct, because only text-bearing items have a resolved
  `unit_length` and its only catch is `WholeDocumentRequested`.

**Take `PLAN-tasks-11.md`.** It also honours the four cross-task demands verbatim.

### Three things it raises that are still open

- **Task numbering is not a build order for 11–14.** The module graph is acyclic
  (`consent → release → denial/binding → gate`), but Tasks 12/13/14 are Create-only and each says
  the wiring is Task 11's, while `denial.py` imports `release.Denied` at run time. Executable order
  is **14, 11-a, 13, 12, 11-b**, so Task 11 lands in two commits.
- **SPEC §6 and §7 cannot both hold for `release_id`.** §6 puts the audit append strictly before the
  release exists, `mint_release` takes the `audit_id`, and `events` is append-only — so
  `AuditRecord.release_id` is `None` on a release record and the join must run ledger → events.
  A Contract-out mismatch, not an implementation choice.
- **Task 20 pins `Gate.__init__` to ten keywords and two denials are unreachable without two more**
  (`measure_tokens` — P7 owns no tokenizer; `template_for` — §7.3's residual library is unbuilt).
  Added as optional defaulting to `None`, so with the default the denial cannot fire — the same
  shape as "an unset ceiling cannot deny". Task 20's fixtures 4 and 16 need one more line to replay.

**Good discipline worth copying:** `SENSITIVE_CLASSES` was *removed* from that author's own earlier
draft, because publishing it would have answered NEEDS-JOSEPH C24 in code. The consent branch reads
`ClassificationRecord.protected` per SPEC §2 instead.

---

## 23. FOUR RULINGS FROM JOSEPH, 2026-08-22 — binding, and they close four open labels

Put to Joseph with the evidence assembled; all four taken as recommended. These are now ratified
alongside D1–D6 and are binding on assembly and on any source written afterwards.

| | Ruling | Closes | Status |
|---|---|---|---|
| **D7** | **P6 creates no `sensitivity_status` field row.** P7's `ClassificationRecord` is the sole home. | **C24**, and **C25** with it | apply at assembly |
| **D8** | **`target_school` is the stored key.** "target university" (§3.11) becomes an alias, never a second key. | the §3.8/§3.11 two-key split | apply at assembly |
| **D9** | **`destination_eligible = TRUE` for `target_school` and `client`**; FALSE for `authored_by` and `our_firm`. | brief §16's open question | apply at assembly |
| **D10** | **P4's `norm` means TOP-LEFT.** The Vision adapter converts. | **C22** | **DONE** — `87016b0`, 1302 tests |

### D7 — no P6 `sensitivity_status` row

The deciding factor: the reconciliation (P6 carries the row, P7 writes it) would have made a
**third** home for one concept — P7's record, P1's `files.sensitivity_state` column, and a P6 fact
row — which is the shape OQ11 was opened to prevent and this project's most expensive defect class.

**Three things assembly must do, and none of them is optional:**

1. **Amend P7's SPEC Contract-in.** The sentence *"P6 must accept `sensitivity` as a first-class
   universal field (§3.11) rather than a domain-scoped one"* is wrong under D2 + D7. It should name
   P7's own `ClassificationRecord`. This is a SPEC edit, not a plan edit.
2. **Rewrite P7's Done-means 2** against `ClassificationRecord`. It is currently *knowingly
   unsatisfied* — the only one in either part in that state — and D7 is what lets it be satisfied
   honestly rather than deleted.
3. **Create no catalogue row**, which is what every task already does. Round 1's F-2 (`sensitivity
   status` has no producer) is closed **by deletion**, not by inventing a writer.

The P7 Task 11 author who removed `SENSITIVE_CLASSES` from their own draft rather than answer this
in code was right, and the ruling vindicates the instinct: it was Joseph's to make.

### D8 — `target_school`, and "target university" is an alias

Same shape as D6's `subject`/`course`, decided the same way and by §17's rule: **one stored key per
concept; every other word the design uses for it becomes an alias, never a second key.**
`target_school` wins on three grounds — it is already in the catalogue as one of §3.8's four role
fields beside `authored_by`, it is `snake_case` per D6, and it is the more general word (a school
that is not a university still fits). "target university" is §3.11's prose and survives inside
quotations only.

Done-means 2 requires both words to resolve; an alias satisfies that, a second key does not.

### D9 — `destination_eligible` splits §3.8's four roles two and two

My skeleton said all four were FALSE and I over-applied the rule; `planning/domains/canonical_fields.json`
was right. §3.8's actual sentence is *"It should avoid using authorship or creator identity as a
destination dimension."* That is `authored_by` and `our_firm` — **who made it**. `target_school`
(who you apply TO) and `client` (who the work is FOR) are the other side of the role split, and a
client folder is an ordinary destination.

| field | `destination_eligible` |
|---|---|
| `authored_by` | FALSE — authorship |
| `our_firm` | FALSE — creator identity |
| `target_school` | **TRUE** |
| `client` | **TRUE** |

This unblocks P10 building folder templates on those two keys. It also **aligns P6's catalogue with
the other agent's `canonical_fields.json`** rather than diverging from it — worth stating, because a
P6 author is currently building the stricter reading and must be corrected at assembly.

Note the trap from §16 still stands: `FORBIDDEN_COLUMN_SUBSTRINGS` must not be run against the
`fields` table, because the legitimate column `destination_eligible` contains `destination`.

### D10 — `norm` is top-left, and the adapter converts. ALREADY DONE.

Committed as `87016b0`. `readers.ocr_vision._box` returns `1.0 - (origin.y + height)`.

This was a **live latent defect, not a planning question.** Vision reports bottom-left; P7's
redaction and all image tooling assume top-left; a stored `norm` region read by redaction would have
blacked out a band mirrored about the horizontal axis — a §8.4 failure that looks like a working
redaction. The adapter had documented the trap and left it open.

Closed at the adapter rather than in P4 because it is the **only live producer** of a `norm` region,
so P4's shipped `Region`, `REGION_UNITS` and all nineteen fixtures are untouched and the suite did
not move. The top edge is summed before the subtraction — `1.0 - (y + h)`, not `1.0 - y - h` —
because the two-step form leaves a box flush with the top of the page at `-5.6e-17`, and a box a
hair outside 0..1 is exactly what a range check exists to catch. Clamping was rejected for hiding a
genuinely out-of-range rectangle just as quietly.

**Still open from C22's second half:** `evidence_shape.location.location()` accepts any `region`
mapping without validating it. That check belongs in P4, and P7 Task 8's redaction is its first real
consumer.

### What is still NOT ruled

The five unratified round-5 cuts — **CUT 2** (P7 Task 19, the transport guard), **CUT 3** (P6 Task
23, `plan_versions`), **CUT 4** (P7's `Gate` facade), **CUT 6** (§3.13's five-rank ladder), **CUT 7**
(P6's read surface). Deliberately deferred until the assembled plans exist, because round 5's own
argument is that *"a reader deciding the cut needs the plan in front of them to decide against"*.
Write them; keep the callouts; do not silently comply and do not silently ignore.
