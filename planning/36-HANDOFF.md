# Handoff — 2026-08-27

The only file a fresh session needs. Read this, then `git log --oneline -25`.

Branch `build/p6-p7-first-packages`. Suite **3618 passed**, `compileall` clean.
Two other sessions commit to this branch (`fix(domains)`, `research(J-DEPTH)`);
never rewrite shared history, never stash while either has uncommitted work.

---

## 1. What is built

| Part | Package | State |
|---|---|---|
| P1 | `src/database_agent` | built |
| P2 | `src/eval_harness` | built |
| P3 | `src/scan_agent` | built |
| P4 | `src/evidence_shape` | built |
| P5 | `src/extractors`, `src/readers` | built |
| P6 | `src/facts` | built |
| P7 | `src/privacy` | built |
| P8 | `src/llm_harness` | **built, and repaired this session** |
| P9 | `src/grouping` | **built this session, Tasks 1–15 complete** |
| P10 | — | not started; `PLAN.md` rewritten this session (10013 lines, 17 tasks) |
| P11 | — | not started; `PLAN.md` rewritten this session (8276 lines, 21 tasks) |
| P12, P13 | — | specification only |

**Start P10 Task 1.** Its plan is executable and its ordering gates are stated.

---

## 2. What changed in P8

Two independent reviews (`planning/33-P8-COMPLETION-AUDIT.md` plus the code and
spec reviews) found twenty-three defects in work that was green. Every HIGH and
every blocker is closed. The ones worth carrying forward as *shapes*:

- **Site A never ran the release-bound citation check.** It took its citable set
  from P6's `FactRequest` — every observation for the file version — and set
  `span_matched` to a copy of `resolved`. A model citing a key P7 withheld, with
  an invented span, got `accept_direct` and the fact was written.
- **Nothing bound the dossier's subject to the P6 request.** A dossier describing
  one file wrote a fact onto another.
- **Replay appended a second P6 consequence.** `write_unresolved` is always an
  INSERT; re-validating one stored abstention left P6 saying the model declined
  twice.
- **A second identical call crashed and leaked a reservation.** `dossier_id` is a
  content address and `record_dossier` was a bare INSERT against a PRIMARY KEY.
- **Four values meant the opposite of what they said**: an empty `cited_span`
  matched everything; `"unknown": false` became an abstention; `verdict_id` was
  the identity of a question rather than an answer; `CallFailed.request_identity`
  was a capability.
- **`run_call` reported by position** — `verdicts[-1]` — so a call whose first
  shard was rejected read `accept_direct`.

Still open in P8, named rather than fixed:

1. `supersede_verdict` has no production caller. A re-judgement of one
   (dossier, response, claim) is refused with a message naming supersession as
   the mechanism; nothing calls it yet.
2. `FactRequest.normalizers` crosses the P6→P8 seam and is discarded; P8 uses the
   separately injected `normalize`. The caller is expected to close over it.
3. `"field"` and `"value"` are wire-shape key names P8 authored, and
   `response_schema_bytes` is never parsed. Declaring the wire contract on
   `PromptDefinition` is the fix; it was not made.
4. The SPEC's per-site **Structure** and **Policy** rows have no dossier carrier,
   and `Conflict` reduces "known conflicting facts and suppressed candidates" to
   `conflict_id` + `kind`.
5. `ReleasedEvidence.address` doubles as the metadata field name.
6. `CallDependencies` carries one Site A `FactRequest` while `run_call` may issue
   a call per split shard. A shard naming another subject is now refused; the
   design question of per-shard authorities is open.

---

## 3. What P9 is

`src/grouping/`, fifteen modules, all fifteen plan tasks green.

The sequence: **seeds → bounded embeddings → bounded retrieval → graph and
pre-model stop rules → reference-only dossier → P8's `run_call` → mapped
disposition.**

Rules that cost the most if they move:

- **The stop rules run before the dossier.** A group that cannot form costs
  neither a dossier nor a call.
- **SR1 and the support bar are different rules.** SR1 is zero anchors and stops
  the group existing; `minimum_independent_anchors` decides `supported`. They were
  one check and a one-anchor group vanished instead of waiting.
- **A seed anchors itself** when its own P6 fact is validated.
- **The eligible embedding set is cut before a single text is read.** Encoding is
  paid at read time. A duplicate costs no second encode but does cost a slot.
- **A context-supported membership and its `pending-review` row are one
  transaction.** A membership visible without its review is an uncertain guess
  wearing a decision.
- **Acceptance is the only plan-versioned record.** `accepted`/`rejected` are not
  in `GROUP_STATES`; they resolve through `group_state_as_of`.
- **P9 writes no fact.** A guard forbids `write_fact`, `ensure_value` and
  `apply_verdict` anywhere in the package — a membership says a file belongs with
  others, a fact says something is true of it.
- **`LocalEvidenceGraph.file_ids`, never `nodes`.** A graph node is a file
  version; a P10 node is a destination.

P9's open questions stay open: no cross-P11 edge enum, no protected-record
destination, no `tentative-discovery` visibility policy (P10 must not render it),
no member-role field.

---

## 4. What changed in the plans

`planning/34-P10-PLAN-AUDIT.md` and `planning/35-P11-PLAN-AUDIT.md` are the
evidence. Both PLAN.md files were prose restatements of their SPEC's chapter
titles — P10's audit counted 38 MISSING requirements, P11's found the record the
part exists to publish never specified. The replacements follow
`_PLAN-AUTHORING-BRIEF.md` in full.

`planning/parts/P10-*/PLAN.md` and `planning/parts/P11-*/PLAN.md` are **symlinks**
into `docs/superpowers/plans/`. Edit either path; commit the target.

Four things the audits surfaced:

- **Site E's fragment boundary is owned by nobody who can act.** `grep -rn
  fragment src/` returns one hit and it is about filesystem paths. P10 carries it
  now (Task 8), because P10 owns the published catalogue.
- **P11 was planning to rebuild ~25 validations P8 ships.** Its Task 12 names each
  check it is therefore not writing, with line numbers.
- **Three P10 SPEC names do not exist in live P9**: `label`, `membership_kind`,
  and `Group.state = rejected`. The plans use the live names and record the
  corrections in a `## SPEC corrections` section.
- **P11's eight §8.2 event names are unregistered**, and `append_event` refuses an
  unregistered type. Registering them is its Task 1.

---

## 5. How this session worked, and why

Standing constraints, unchanged:

> *"reports, apps and system files MUST NOT BE MOVED OR READ OR ANYTHING SYSTEM
> OR SENSITIVE IN THAT SENSE."*

A protected container is **marked and counted, never opened** — present-but-
untouched in the UI, with a reachable explanation, never silently omitted, and
never described as *"understood and found unimportant."* P9's dossier assembly
implements exactly this: an unclassified file is withheld AND named in
`omissions.privacy_redacted`.

- **Quote by grep, not by memory.** Fabricated quotations are this project's
  most-repeated defect.
- **Every guard gets sabotaged.** A test that stays green when the thing it
  guards is deleted is not a guard. Roughly seventy sabotage runs this session;
  eight came back SILENT and each one became a new test.
- **Write the test first.** Twice this session I wrote a module before its tests
  and deleted it to start over. Both times the tests came out different.
- Never append `Co-Authored-By`, `Generated with`, or any AI attribution.
- No summary markdown outside `planning/`.
- Backticks inside `git commit -m` shell-expand; use `git commit -F -`.

**Recurring defect shapes** — worth re-reading before P10:

a placeholder that satisfies a type · a column with no writer · a reserved name
with no producer · a capability used as an identity · a test that builds its own
record rather than going through the production builder · a contract asserted as
a literal in many places · two transactions where one is needed · a guard whose
banned word appears in its own docstring · a signature that documents an
exclusion by accepting the value.
