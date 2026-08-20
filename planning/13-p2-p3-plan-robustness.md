# P2 and P3 plan robustness

Date: 2026-08-20 (re-check)
Status: **not all good** — yesterday's three wave seams are mostly *named*; two of them are closed in SPECs and still open in the PLANs that would implement them. Do not execute wave 1 as a stack.
Scope: live P2 PLAN (6194 lines, 17 tasks) and P3 PLAN (5433 lines, 18 tasks) against live SPECs, [`11-ops-runtime.md`](11-ops-runtime.md), and the live P1 PLAN (mtime 2026-08-19 15:57 — **not updated overnight**). Prior pass: this file as of 2026-08-19 17:42.
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md)

---

## Resolved 2026-08-20 — all findings actioned, one correction to the report

Every blocking finding below is closed. The report's own headline is corrected:

| Finding | Status |
|---|---|
| **P3 PLAN Task 3** implements the OQ16-open reading | **Fixed.** Task 3 now mints `scan_run_id`, publishes it, calls P1's `start_scan(conn, *, scan_run_id)`, and samples §8.6's six counters. Title, header, consume table, file map, Task 17's mis-named guard, and the Self-Review's two stale claims all follow. **Assembled and run: 6 passed** (19 passed across Tasks 1–3). |
| **P2 SPEC** lists `source_scan_ref` twice | **Fixed.** The stale duplicate is deleted; one line, one meaning. |
| **P2 PLAN** comment says P3 "publishes to nobody" | **Fixed** — a survivor the report missed, stale in the *opposite* direction after OQ16 closed. |
| **P1 PLAN** is stale (`record_file` derives, `start_scan` mints) | **Real, and severity corrected — see below.** Marked superseded, with the complete divergence list. |

**The report's headline is wrong: P3 Task 10 was never blocked.** It reads the live P1 PLAN as "the substrate they call". The substrate is `src/database_agent/`, and P1 **shipped on 2026-08-19 with 152 tests**. The shipped `record_file` and `observe_path` already require all five §1.2 fields as keywords with no default, and the shipped `start_scan` already takes `scan_run_id` and mints nothing. P3 Task 10's call matches the shipped signature exactly. What is stale is `P1-storage-identity-provenance/PLAN.md` — the construction record, not the code.

That document was **not** rewritten to match the code: rewriting a build record to resemble what it produced destroys the history and still leaves every task's TDD steps inconsistent. It now carries a supersession header naming the divergences, verified by parsing all 42 of its `def`s against the shipped modules. **Exactly four differ** — `record_file`, `observe_path`, `start_scan`, and the private helper `_check` (parameter renamed). The other 38 shipped identically.

**What the report got right, and what it cost to miss.** P3 Task 3 was a genuine blocker and my prior "ready to implement" verdict missed it. My checker verified internal consistency, call-signature agreement, and invented values — it does not compare a PLAN's *open-question status* against its SPEC's *ratified status*. Task 3's defect was invisible to a call-site checker precisely because the defect was a **missing call plus a guard asserting it stay missing**. That is a new defect class, now named: **a plan that is internally consistent, correctly typed, and implements a superseded decision.**

---

**Verdict.** It is not all good. The plans got better: P2's shadow proof now snapshots every non-eval table; P3 no longer lists `scan_usage` as consumed; P3 now *passes* the §1.2 fields instead of hoping P1 will ignore them; P2 claims its own pytest blocks were actually run (154 passed). What is not good is that **the SPECs moved and the implementing plans did not move with them**, and **P3's PLAN describes a P1 that the P1 PLAN does not contain**.

An implementer who executes P1 PLAN then P3 PLAN will hit a signature mismatch on Task 10. An implementer who trusts P3 SPEC OQ16 (closed) then reads P3 PLAN Task 3 (still "OQ16 stays open") will ship two scan identities again.

| | P2 | P3 | P1 PLAN (the substrate they call) |
|---|---|---|---|
| Tasks | 17 + Self-Review | 18 + Self-Review | last write 2026-08-19 15:57 |
| SPEC overnight | `source_scan_ref` now "P3's published `scan_run_id`" — **and the old line is still there** | OQ16 **settled** 2026-08-20 | OQ19 **settled** 2026-08-20: `start_scan` takes P3's id |
| PLAN overnight | comment now says the fixture is **not** P3's scan_id | Task 3 still titled **"OQ16 stays open"**; still forbids `scan_usage` | `start_scan(conn) -> str` still **mints** an id; `record_file` still NFC-normalizes and re-stats |

A plan is robust if a later part can be built against it without inheriting a lie. Right now the lie is between documents dated the same morning.

---

## Re-check of yesterday's findings

| ID | Yesterday | Today |
|---|---|---|
| **P2-A** `source_scan_ref` treated as P3's scan_id | Live in PLAN comment | **Closed in P2 PLAN** (comment now says no part publishes one). **Reopened as a SPEC defect:** P2 SPEC Contract out §3 lists `source_scan_ref` twice — once as "P3's published `scan_run_id` (P3 OQ16, closed 2026-08-20)" and once as the old opaque "P3 scan and exclusion set". Two lines, two meanings. |
| **P2-B** shadow empties only check P2's own columns | Blocking | **Closed.** `foreign_table_counts` snapshots every table not in `EVAL_TABLES` before the adapter runs and diffs after. P10/P12 tables are covered by subtraction the day they appear. Honour-system columns remain as a second check. |
| **P2-C** `run_gate` does not block | Advisory, SPEC OQ9 | Still true. Still correctly deferred. Not a reason to refuse P2. |
| **P2-D** `inputs[]` ambiguous | Recorded | Still recorded. Still a recommended SPEC change, not made. |
| **P2-E** "files indexed" two definitions | Recorded | Still both reported, neither picked. |
| **P2-F** P2's own §8.6 ceilings | Missing | Still missing. |
| **P2-G** NULL verdict / `unverdicted` | Honest | Sharpened: P2 now says the four unpublished strings (`stage_error`, `expectation_not_applicable`, `unverdicted`, gate `pass`/`fail`) **cross into P13** and must be published in the P2 SPEC before P13 invents names. Still not published. |
| **P3-A** P1 re-derives R2 fields | Blocking Task 10 | **P3 PLAN claims this was fixed 2026-08-20.** Live P1 PLAN was **not** updated. `record_file` still does `path.stat()`, `unicodedata.normalize("NFC", path.name)`, and hashes from the path. `observe_path` *Produces* line still has no `filename=` / `normalized_filename=` / `observed_size=` keywords. P3 Task 10 calls those keywords. **The claim is false against the live P1 PLAN.** |
| **P3-B** three unjoined scan identities | Wave defect | **SPECs closed it** (P3 OQ16, P1 OQ19, P2 `source_scan_ref`). **P3 PLAN and P1 PLAN did not.** P3 Task 3 still publishes to nobody and asserts `database_agent.scan_usage` is absent. P1 PLAN `start_scan(conn)` still mints `scan_id`. |
| **P3-C** P1 NFC answers P3 Q1 | Live | **P3 PLAN** now passes `normalized_filename=path.name` unchanged and greps out Unicode-form names. **P1 PLAN** still NFC-normalizes. Same split as P3-A. |
| **P3-I** stale consume-table `scan_usage` lines | Implementer trap | **Closed.** Header now says P3 consumes nothing from `scan_usage`, deliberately, and explains why. |
| Graphify path-check | Absent | Still absent. |
| `.app` descent, `.icloud` placeholders, metadata-safe no `files` row, two modification events, no FDA fake | Known gaps | Still correctly carried. New known gap: **11 §7 "two scans do not run on the same root" is unimplemented** and unassigned (P3 SPEC runtime paragraph never bound §7). |

New since yesterday, P2's own honesty:

- **`evidence_ref = NULL` on every machine-written assertion.** Contract out §6 requires it; the stage envelope has no field to carry one; payload is opaque. Reconstruction obligation unmet. Recommended SPEC change, not made.
- **A08 and A11 pin one of several legal outcomes.** Exact equality will `fail` a system that takes the other legal option. Recorded.
- Self-review claims the code blocks were extracted and **`pytest tests/eval -q` → 154 passed**. That is a real upgrade from "runnable on paper." It does not make the SPEC/PLAN desync go away.

---

## The actual blocker: SPECs closed seams the PLANs still implement as open

This is the one finding that matters more than the rest.

**Scan identity (yesterday's wave defect).**

- P3 SPEC OQ16: settled 2026-08-20. P3 publishes `scan_run_id`; P1 `start_scan(conn, *, scan_run_id)` takes it; P3 may sample the six §8.6 counters.
- P1 SPEC OQ19: settled the same day. P1 mints nothing.
- P2 SPEC: `source_scan_ref` is that published id — plus a leftover duplicate line with the old meaning.
- P3 PLAN Task 3 title: *"The scan-run handle — local, and OQ16 stays open."* Still forbids importing `scan_usage`. Header: *"OQ16 is closed in the SPEC or it stays open; until then P3's run identifier is P3's alone."*
- P1 PLAN Task for `scan_usage`: `start_scan(conn) -> str` still mints.

If you execute the PLANs, you re-create the three-identity hole the SPECs just closed. If you execute the SPECs, Task 3 and P1's `start_scan` have to be rewritten first.

**R2 field ownership (yesterday's P3-A).**

- P3 PLAN Task 10 and Task 17: P1 `record_file` / `observe_path` take `filename`, `normalized_filename`, `extension`, `observed_size`, `observed_timestamps` as required keywords; P1 stats nothing and normalizes nothing; only the content hash stays P1's.
- Live P1 PLAN `record_file`: still `path.name`, NFC, `path.suffix`, `stat.st_size`, `_timestamps(path)`. No those keywords.

P3's "Divergence resolved — P1 changed, 2026-08-20" is a note about a P1 that is not in `P1-storage-identity-provenance/PLAN.md`. Do not execute P3 Task 10 against the live P1 PLAN. Either patch P1 PLAN to match P3's call, or patch P3's call to match P1 PLAN. The SPEC Contract in already says P1 *stores* what P3 hands it — the P1 PLAN is the document that is behind.

**P2 SPEC mechanical defect.** Contract out §3's `bundle_manifest` block contains `source_scan_ref` twice. Do not freeze that page.

---

## What is actually good now

Do not re-open these. They were real holes yesterday and they are fixed in the live plans.

- P2 shadow proof is no longer self-referential. Foreign-table snapshot by subtraction is the right shape.
- P2 `source_scan_ref` *comment* no longer pretends P3 published an id. (The SPEC still does, twice.)
- P3 consume table no longer tells an implementer to import `scan_usage`.
- P3 authorship rule, registration-nothing, caller-supplied MIME/scan_state/budget, dataless-before-hash, FDA-as-PermissionError, watch-without-faking-FSEvents, replay-re-fires-rules, curation=`undetermined` — all still hold.
- P2 still keeps stages and dimensions apart, never folds `not_run` into `pass`, never scores deferral as divergence, never authors `events`.
- Neither plan invents thresholds, gazetteers, or templates.
- 11 form-factor and Application Support location are now marked ratified. Irrelevant to execute-order except P1 `open_database(scan_roots=…)` already knew it.

---

## Still not perfect (and not pretending to be)

These are honest known gaps. They do not block a walking skeleton. They block a first real Mac scan or a first P13 eval view.

- Q7: `.app` bundles descended.
- Legacy `.icloud` placeholders undetected.
- Metadata-safe replay writes no `files` row (now also in P2 SPEC as ratified 2026-08-20 — that half is aligned).
- Two `external modification detection` rows on content change.
- 11 §7 concurrency (two scans, same root) unowned.
- P2 `evidence_ref` NULL; four unpublished verdict-adjacent strings; A08/A11 single-valued; no P2 storage ceiling; `inputs[]` ambiguous; "files indexed" dual; `tree` dimension pass/fail on user behaviour (OQ4).
- Graphify standing rule still has no home.
- `create_scan_schema` still not called from `open_database`.

---

## Execute?

**No, not the stack.**

| Document | Execute? |
|---|---|
| P2 PLAN Tasks 1–17 | Yes, against rewritten P1, **if** you treat `source_scan_ref` as an opaque fixture string until OQ16 is implemented the SPEC's way. Do not wire it to P3's unpublished handle. |
| P3 PLAN Tasks 1–9, 11–14, 16–18 | Yes, against rewritten P1. |
| P3 PLAN Task 3 as written | **No.** SPEC closed OQ16; this task still implements the open reading. Rewrite to publish `scan_run_id` and pass it to P1 `start_scan`, *after* P1 PLAN grows that keyword. |
| P3 PLAN Task 10 as written | **No**, until P1 PLAN's `record_file` / `observe_path` actually take the observed fields. As of this re-check they do not. |
| P3 PLAN Task 15 | Exclusion/cache/curation only. Do not claim `files` round-trip from `metadata_safe`. P2 SPEC now agrees. |
| P1 PLAN `start_scan` / `record_file` | Must be edited to match the 2026-08-20 SPEC settlements **before** P3 Tasks 3 and 10. |

---

## Edit order (revised)

Yesterday's order 1–2–3 is now: SPECs already did 2; PLANs did 3; nobody did 1 or the P1 half of 2.

| Order | Owner | Change |
|---|---|---|
| 1 | P1 PLAN | `record_file` / `observe_path` take the §1.2 fields as required keywords; stop NFC; stop re-statting. `start_scan(conn, *, scan_run_id)` takes P3's id; mint nothing. Match P1 SPEC OQ19 and Contract in. |
| 2 | P3 PLAN Task 3 | Stop saying OQ16 is open. Publish `scan_run_id`. Call P1 `start_scan`. Sample the six counters. Delete the "forbids scan_usage" test or invert it. |
| 3 | P2 SPEC | Delete the duplicate `source_scan_ref` line. Keep the closed-OQ16 reading. |
| 4 | P2 SPEC | Publish `no_verdict_reason`, `unverdicted`, and the gate's `pass`/`fail`/`not_run` before P13. Give `stage_output` a channel for `evidence_ref`, or drop the reconstruction sentence. |
| 5 | Lead | Place 11 §7 (two scans, same root). P3 already refused to invent it. |
| 6 | Lead | Graphify hook. Still unpaid. |

Then: P1 PLAN green against the 2026-08-20 SPECs → P2 1–17 → P3 1–18 including 3 and 10.
