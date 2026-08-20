# Verification of the Wave-2 orchestrator SPEC

Date: 2026-08-20
Subject: [`18-wave2-orchestrator.md`](18-wave2-orchestrator.md) (287 lines) and its companion
[`18-p4-p5-prebuild.md`](18-p4-p5-prebuild.md)
Method: **executed**, not read. Repo baseline re-run: `python3 -m pytest -q` → **468 passed in 7.67s**.
The SPEC's call sequence was run against shipped P1/P2/P3 with P4/P5 stubbed
(`scratchpad/orchverify/run_spec_sequence.py`). Every claim below carries the output that produced it.

---

## Verdict

**Fix these first.** The seam is the right object and the page is right about what it must not own.
Its sequence *executes* — I ran it and it produced a sealed bundle with `source_scan_ref == scan_run_id`,
a populated `extraction_status_by_tier`, and zero events authored by the orchestrator. But **two of the
four things the page claims to own do not work as written**: the exception contract is unreachable from
the loop the page specifies — *both* rows, not just the dataless one — and Done-means 3 is unsatisfiable
in both of its branches, including the branch the page's own self-review recommends as the repair.

The repair is small and local (one extra iteration over `dataless_detections`, joined to `files` by path)
and does not change the page's shape. Fix D1–D5, then build.

**Confirmed defects: 7. Refuted claims: 3** (including one of the two the author raised against itself).

---

## Confirmed defects

### D1 — Done-means 3 is unsatisfiable in **both** branches. *Critical.*

The self-review (line 271) says a *first-sight* iCloud file cannot reach the loop, and prescribes the
"recorded while local and evicted since" fixture instead. **The prescribed fixture fails too.**
`src/scan_agent/scan.py:52-55`:

```python
            if item.dataless:
                record_dataless_detection(conn, scan_run_id, item.path)
                continue
```

The `continue` is unconditional on prior history. It fires **before** `prior_observation`,
`record_basic_record` *and* `record_cache_verdict`. A file that already has a `files` row from an
earlier local scan still gets no `stat_cache_verdicts` row when it comes back dataless — so it never
appears in `cache_verdicts(conn, scan_run_id)`, which is the roster the SPEC's loop iterates (line 72).

Executed, two fixtures, real `scan()`:

```
=== E3: dataless at FIRST SIGHT ===
   scan 2 (dataless) verdict rows: 0 | dataless_detections: 1 | files rows: 0
   -> extraction_runs the SPEC loop can write: 0

=== E4: recorded while LOCAL, dataless on re-scan (SPEC done-means 3) ===
   scan 1 (local) files rows: 1 | verdicts: 1
   scan 2 (dataless) verdict rows: 0 | dataless_detections: 1 | files rows: 1
   -> extraction_runs the SPEC loop can write: 0
```

E4 is the case Done-means 3 names. The `files` row exists; the loop still never sees it.

**Fix.** The identity is recoverable — the detection carries the path and the `files` row carries
`current_path`. This join returns both required NOT NULL columns and touches no bytes:

```
join detections -> files by path:
   {'path': '…/Thesis.pdf', 'file_id': '8dd7755c-…', 'content_hash': '3182d61d…'}
```

So the orchestrator needs a **second** iteration, after the `cache_verdicts` loop:
`for detection in dataless_detections(conn, scan_run_id)` → look up `files` by `current_path` → if a row
exists, write the one `dataless` run; if not, it is P3's count only. That is the "two counts" close the
self-review already reaches — but it needs this *loop*, which the page does not have. Adding
`dataless_result()` to P5 (OQ4) without adding this iteration produces a constructor with no caller.

### D2 — The `DatalessRefused` row of the exception contract is dead. *Critical.*

Follows from D1 and is worth stating separately because the page lists "the exception contract" as
thing #2 of the four it owns (line 19). No dataless file of any history reaches the loop, so
`admit()` is never called on one, so `DatalessRefused` is never raised inside this sequence and the
`except DatalessRefused` arm (line 86) can never execute. The page's central claim — that **this page**
is the catcher C4 named — is not implemented by the code the page sketches.

### D3 — `break` falls through to a forbidden write, and that row is unreachable too. *High.*

Two problems in the `ProtectedContainerRefused` arm (lines 84-95).

**(a) The sketch contradicts its own contract cell.** The exception table (line 114) promises
"no run row, no observation, **no status write for anything inside**". The sketch `break`s out of the
handler loop — and then falls straight into `set_extraction_status`, which is outside that loop.
Executed:

```
--- SPEC break-then-fallthrough, simulated ---
reached set_extraction_status after break? YES; runs = []
```

That is a P1 write, authored `"P5"`, on a file the product is forbidden to have touched. `break` must be
`continue` on the *outer* loop (or the status write must move inside a guard).

**(b) The arm is unreachable for the same structural reason as D2.** Once P3 ships the
`protected_container` rule, the container is pruned in `traversal.py:120-122` before any `ObservedFile`
inside it is yielded — so no `files` row, no cache verdict, and the orchestrator never sees it.
Done-means 4 therefore passes **vacuously**: it asserts zero rows for something that can never arrive.
A vacuous assertion is not a test. Done-means 4 should assert the P3 exclusion verdict and the absence of
`files` rows (both real), and stop implying the `break` path was exercised.

*Confirmed unshipped, as the page states:* `src/scan_agent/exclusion.py` publishes exactly
`RULE_LITERAL_DIRECTORY_NAME`, `RULE_CATEGORY`, `RULE_PROJECT_ROOT_DESCENDANT` — no
`protected_container`. The page's line 135 is accurate.

### D4 — The §4b quotation is not verbatim. *High — it is load-bearing.*

SPEC lines 119-121 quote §4b as:

> *"P3 does not descend into one, does not stat its contents, does not hash a byte of it, and does not
> create a `files` row for anything inside it."*

`planning/11-ops-runtime.md:73` actually reads:

> location is a **protected container**: P3 does not descend into one and hashes nothing inside it,
> and P12 never moves one.

Three of the four clauses are the author's, presented inside quotation marks as the source's. The page
then builds its asymmetry argument on the invented clauses: *"A run row names a `file_id` and a
`content_hash` — both facts §4b forbids learning."* §4b forbids **descending** and **hashing inside**;
"does not create a `files` row" is an inference from that, not a rule §4b states. The **conclusion is
still correct** (you cannot have an identity for something you never descended into), but on a page whose
entire value is fidelity to the source, a fabricated quotation is the most corrosive possible defect —
it is the one thing a later reader will not re-check. Rewrite as: quote §4b's actual sentence, then state
the inference as an inference.

Nine other citations spot-checked and **all verbatim**: §8.2 "the responsible subsystem"
(`00:136`); §8.2 "Extraction status by extractor tier" (`00:147`); §8.6 "difference between completed work
and deferred work… false impression that an unprocessed file was understood and found unimportant"
(`00:259`); §8.6 "Cost exhaustion must never turn into lower-quality automatic classification"
(`00:258`); §8.8 "A new plan should never silently reclassify" (`00:281`); 11 §5 "Do **not** materialize,
hash, or extract" (`11:89`); 11 §7 "A second scan of an in-flight root is refused" (`11:122`); 11 §1
"Until it is granted, P3 does not traverse" (`11:23`); 02 "stays in the repository as the integration
test every later part must keep green" (`02:28`).

### D5 — It reassigns a role the ratified table assigns elsewhere, without saying so. *Medium.*

P5 SPEC's ratified table, C4 (`planning/parts/P5-extractors/SPEC.md:704`):

> The gate still raises and writes nothing… The run row naming the refusal is written by whoever
> **catches** `DatalessRefused` **(the router)**, which is the concrete follow-up.

The SPEC (lines 130-131, 267) quotes the first half of that sentence and overrides the parenthetical:
"**this page** is the catcher C4 named (not P5 Task 4)". It may well be the better design — but the
ratified table is Joseph's 2026-08-20 answer and beats a spec page's reasoning. This must go to Joseph as
an explicit "C4's parenthetical says router; I propose the orchestrator; confirm", not be settled in
prose. It is not cosmetic: if the router catches, the run is written inside P5, `dataless_result()` never
needs to be public (OQ4 dissolves), and the orchestrator's exception contract loses a row.

*Everything else the ratification tables freeze is respected.* The page honours the ninth value
`dataless`, passes `content_hash` from the `files` row (hash owns the observation), invents no
`analysis_tier`, never mentions `metadata_only` or `raw_value`, keeps `handling_class = None` pending
C2, and spells no reliability value. No settled question is re-opened other than D5.

### D6 — The page answers its own seven open questions twice, in conflict. *Medium.*

"Open questions" (lines 231-259) leaves OQ1–OQ7 open with reasoning. "Recommended closes"
(lines 275-286) then closes all seven — and in two cases contradicts the first pass: OQ2 is "unassigned…
**P5's call**" at line 240 and "**Overstated**" at line 280; OQ7 is "*Blocks:* the skeleton's bundle step.
**P2's call**" at line 259 and "Overstated" at line 285. One document must hold one position per question.
This is also where most of the length overrun lives.

### D7 — A false blocker was published, then propagated. *Low, but see below.*

Self-review item 2 (D-refuted, R1) is wrong, and `18-p4-p5-prebuild.md:99` repeats it as established
fact. A reader who trusts either will "fix" correct code. Both instances need striking together.

---

## Refuted claims

### R1 — "`file_row["path"]`. The sketch `KeyError`s on the first file." (line 273) — **false, twice over.**

The sketch does not contain `file_row["path"]`. Line 77 reads:

```python
                     path=Path(file_row["current_path"]),          # live column name
```

`grep -n 'file_row\["path"\]' planning/18-wave2-orchestrator.md` returns exactly one hit — **line 273,
the self-review sentence itself**. The author fixed the sketch and left the finding behind.

The live column list confirms the sketch is right:

```
files columns: ('file_id', 'current_path', 'filename', 'normalized_filename', 'extension',
 'directory_position', 'volume_id', 'content_hash', 'hash_algorithm', 'observed_size',
 'observed_timestamps', 'mime_type', 'detected_format', 'scan_state',
 'extraction_status_by_tier', 'sensitivity_state')
```

And the predicted exception is the wrong one anyway — `get_file` returns a `sqlite3.Row`, not a dict:

```
   row['current_path'] -> …/corpus_e1/syllabus.pdf
   row['path'] raises:
   IndexError: No item with that key
```

### R2 — "OQ7 is overstated; `corpus_form="snapshot"` for the skeleton." (line 285) — **understated, not overstated.**

`snapshot` is the *more* expensive choice, and the page never names who pays. P2 enforces a body per
entry:

```
snapshot entry without payload_ref rejected:
  BodyMismatch  an entry carries exactly one body: payload_ref (snapshot) or metadata_only (metadata_safe)
```

The sketch's line 102 ("then `add_file_entry` / …  per file") passes no `payload_ref`, and neither the
page's "caller-supplied" list (line 106-108) nor its Contract in names where snapshot payload bytes come
from. I had to invent `payload_ref="ref"` to make the sequence run. OQ7 is a real open question with an
unowned input behind it, and closing it as "snapshot" adds an obligation the page does not carry.

### R3 — "the exception contract" as a thing this page owns and delivers. — **not delivered.**

Stated as owned property #2 (line 19); neither of its two rows is reachable from the sequence it
specifies (D2, D3b). The page owns the *question*; it does not yet own a working answer.

---

## What the page gets right — verified by execution, not by reading

Worth recording so nobody re-litigates these:

- **The sequence runs.** With P4/P5 stubbed, the P3 → P1 → P2 half is real and green:
  `done-means 2: True` (`get_bundle(…)["source_scan_ref"] == scan_run_id`), and
  `counts: {'files_indexed': 1, 'files_with_any_run': 1, 'files_fully_extracted': 1, 'runs_deferred': 0,
  'runs_unreadable': 0, 'runs_dataless': 0, 'files_requiring_model_review': None}`.
- **Done-means 5 holds.** `extraction_status_by_tier` reads `'{}'` before and
  `'{"filesystem": "complete", "zz": "made_up"}'` after — P1 stores an unknown key opaquely, exactly as
  the page claims (line 161).
- **M8 authorship is clean.** After the whole sequence, every event in the database is P3's:
  `[{'subsystem': 'P3', 'event_type': 'discovery'}, {'…': 'hashing'}, {'…': 'stat observation'}]`.
  The orchestrator authors nothing; the only P5-attributed writes take `extractors.authorship.SUBSYSTEM`.
- **Every cited surface exists.** `set_extraction_status` is `files_table.py:147` ✓ ·
  `runs_dataless` is `counts.py:66` ✓ · `budget.CEILING_KEYS` has 16 keys incl.
  `evidence.context_window` ✓ · `cache_verdicts`, `VERDICT_RECOMPUTE`, `VERDICT_REUSE`,
  `dataless_detections`, `scan_resource_usage` all present with the stated signatures ✓ ·
  `start_scan(conn, *, scan_run_id)` keys only on the run id, so OQ1's claim that nothing refuses a
  second scan is correct ✓.
- **OQ4 and OQ5 are real.** P5's PLAN publishes `unrouted_result()` (`PLAN.md:2910`) and
  `deferred_result()` (`:7235`) and **no** `dataless_result` — zero hits. P4 publishes
  `record_run_event(conn, run_id, *, author)` (`P4 PLAN:3434`) while P5 publishes `extraction_event()` +
  `append()` (`P5 PLAN:7537`): two writers for one concept, as OQ5 says.
- **No invented values.** `protected_container` and `untouched_protected` are P3 SPEC's
  (`SPEC.md:46,50`); the four tiers are I4's (`10-i4:36`); `snapshot` is a real member of P2's
  `CORPUS_FORMS`. I found no threshold, ceiling, event type or vocabulary member the design does not
  spell. Done-means 8's grep guard is the right instrument.

---

## Unverifiable

Stated plainly rather than guessed:

- **Everything P4/P5.** `route()`, `admit()`, `SafetyPolicy`, `ExtractionResult`, `EvidenceSink`,
  `extraction_status_by_tier(runs)`, `authorship.SUBSYSTEM` — the packages do not exist. I stubbed all of
  them. Their signatures come from PLAN.md prose only, and D1's repair assumes `record_run` will accept a
  run built from a `files` row without re-hashing. **Unconfirmed.**
- **`extraction_status_by_tier([])`.** Whether it returns `{}` or raises decides how bad D3(a) is.
- **Done-means 4's P3 half.** The `protected_container` rule is spec-only; I confirmed its absence from
  shipped code but could not test the verdict it would produce.
- **Done-means 7.** No Wave-2 walking-skeleton test exists to keep green.
- **OQ7's `metadata_safe` characterisation** ("does not round-trip file identity, writes no `files` row
  on replay"). I tested `add_file_entry`'s body rule, not the replay path.
- **11 §7 concurrency.** I did not attempt two concurrent scans; the page disclaims the rule anyway.

---

## Open questions I would close differently, and why

| OQ | Page's close | Mine |
|---|---|---|
| **OQ3** | Two counts; Done-means 3 uses the hashed-then-evicted fixture | **Two counts, but the fixture is not enough — the loop is missing.** D1 shows the evicted file never enters `cache_verdicts` either. Close it as: *a second iteration over `dataless_detections`, joined to `files.current_path`; a hit writes the `dataless` run, a miss is P3's count alone.* Without that sentence the close is unimplementable. |
| **OQ4** | P5 adds `dataless_result()` | **Blocked on D5, not independent.** If C4's ratified "(the router)" stands, P5 writes the run internally and `dataless_result()` need never be public. Ask Joseph who catches *before* asking P5 for a constructor. |
| **OQ5** | One writer: P4's `record_run_event` | **Agree**, and note it strengthens D5: if P4 owns the only writer, the catcher must be able to call P4 — which the router can do as easily as the orchestrator. |
| **OQ7** | "Overstated"; `corpus_form="snapshot"` | **Understated** (R2). Either close it as `metadata_safe` for the Wave-2 skeleton, or name who produces `payload_ref` bytes. Still P2's call. |
| **OQ1, OQ2, OQ6** | P3's; overstated; no checkpoint | **Agree with all three**, and OQ6's "repeat work accepted for Wave 2" is well-reasoned given append-only + supersede. |

---

## On the two process questions the lead asked

**Is the extra file worth keeping?** *Yes, the content — no, as filed.* `18-p4-p5-prebuild.md` holds real,
checkable value that exists nowhere else: the "if a paragraph and a test disagree, the test is the
contract" reading rule, and the fixture warning at its line 65 (live hashes are 64 hex with no prefix and
the algorithm in `hash_algorithm` — confirmed: `'c5c2e8be6ad0825a56ded1f1a153ceaf11dc060ab44b120a94406a08207babc2'`).
Three things argue against keeping it as-is: it duplicates the P4/P5 ratification tables that are already
authoritative in their own SPECs; it propagates the false `file_row["path"]` claim (D7); and two files
sharing the `18-` prefix is a filing hazard the SPEC itself has to spend a sentence warning about
(line 265). **Recommend: keep, renumber, strike line 99's second clause.** It was not authorized, and
that is the lead's call — but deleting it would lose the hash-prefix warning, which is the kind of thing
that costs a day when it bites.

**Is the 287-line overrun substance or padding?** *Mostly substance, with one clear cut.* The body through
line 260 is 260 lines against a 150–250 ask — a 4% overrun on a page carrying a call sketch, an exception
table, an authorship table and seven open questions. That is fine. The **27-line appended self-review is
the overrun**, and it is the weakest part of the document: one of its two blockers is false (R1), the
other is right for the wrong reason (D1), and its "Recommended closes" table contradicts the open-questions
section it sits below (D6). Fold the surviving findings into the sections they belong to and the page
lands inside budget. A SPEC that names bugs in itself and ships them unfixed is a SPEC that has not
decided whether it is a spec or a review.

---

## Recommended order

1. Strike the self-review's item 2 here and at `18-p4-p5-prebuild.md:99` (D7, R1).
2. Take D5 to Joseph — who catches `DatalessRefused`? Everything about OQ4 and the exception table waits
   on that one answer.
3. Fix the §4b quotation (D4).
4. Add the `dataless_detections` iteration and rewrite Done-means 3 against it (D1).
5. `break` → `continue`, and rewrite Done-means 4 to assert what is actually observable (D3).
6. Collapse "Open questions" and "Recommended closes" into one section (D6).
7. Then build, in the page's own stated order: P4 → P5 → P3's protected-container rule → this caller →
   the skeleton.

*Nothing in the repository was modified, reverted, deleted or committed in the course of this review.
The only file written is this one. Scratch work is in
`/private/tmp/claude-501/-Users-jy-GRAPH-AGENT/48f6ea24-f9be-4201-aab1-f68980c524f4/scratchpad/orchverify/`.*
