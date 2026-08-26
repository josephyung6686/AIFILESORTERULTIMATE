# Handoff — 2026-08-26, suite green at 3281

**Read this first. It is written to be the only thing you need to resume.**
Supersedes `26-handoff.md` (the P6/P7 planning era, now history). Updated in place
rather than replaced — one current handoff beats seven historical ones, and that
rule is §4.4 of this file's own list.

---

## 0. Resume in two minutes

```bash
cd "/Users/jy/GRAPH AGENT"
git log --oneline -5
python3 -m pytest -q            # expect: 3281 passed, ~2m10s
cat planning/33-P8-COMPLETION-AUDIT.md   # what P8 is and is not
cat planning/28-AUTOPILOT.md    # the domain-research loop, if that is your track
```

| | |
|---|---|
| Branch | `build/p6-p7-first-packages` |
| Tests | **3281 passed, 0 failed** (was 3121 at the start of this session) |
| Built | **P1–P8 complete.** P9 is Tasks 1–3 of 15. |
| Source | `src/database_agent`, `evidence_shape`, `extractors`, `scan_agent`, `readers`, `facts` (P6), `privacy` (P7), `llm_harness` (P8), `grouping` (P9, partial), `orchestrator.py`, `production.py` |
| Domain research | **291 node files** on disk; another team is driving that track — see §2B |

**Two teams are committing to this branch.** The domain-research track
(`fix(domains)`, `research(J-DEPTH)`) is not this one. Never stash, rebase, pull
or reset while either has uncommitted work, and never rewrite shared history.

---

## 1. What closed this session

### P8 is complete — all six repair tasks

`docs/superpowers/plans/2026-08-26-p8-live-composition-repair.md` listed five
release blockers. All are closed; `planning/33-P8-COMPLETION-AUDIT.md` is the
record, and it names the seven seams that remain external.

| Commit | Task |
|---|---|
| `1dd29ba` | R2 canonical post-release dossier (`llm_harness/dossier.py`) |
| `7ccec8f` | R3 built-in site dispatcher (`llm_harness/sites.py`) |
| `195da8c` | R4 release-bound citation validation |
| `911a3db` | R5 one connected consequence path |
| `001a34a` | R6 derived no-invention sweep |
| `8ac6f42` | the P6 consequence and the P8 verdict are one write |
| `e9eceb3` | the completion audit |

**Six defects, every one of which had shipped green.** Recorded here because the
shapes recur:

1. `run_call` sent `b"\n".join(released values)` as the dossier and synthesised
   `kind="excerpt"`, `basis=direct-anchor` for every reference. Consequence
   nobody had noticed: Site B reads `kind == "member"`, `run_call` never produced
   one, so **every member P9 proposed would have been rejected as invented**.
2. A caller could pass `site_validator=lambda *a, **k: None` on the public path
   and disable every site check while still getting a real-looking verdict. Every
   harness test did exactly that.
3. Citation spans matched against the injected resolver — the RAW stored text. A
   model quoting what it was shown failed; one quoting text it could not have
   seen passed.
4. `transport.issue` keyed stored responses by `release_id`. Once `dossier_id`
   became a content address, **replay could never find a response it had
   stored**. The P2 replay test passed only because it wrote the row by hand.
5. `verdict_id` was `file_id:field_key` on a PRIMARY KEY — two dossiers over one
   file collided on insert.
6. The P6 fact and the P8 verdict about it were separate transactions, so a
   failure between them left a fact with no verdict.

**Defects 4, 5 and 6 were only reachable once Site A was connected.** Before R3,
`run_call` reached P6 through nothing at all — the caller's callback stood where
the fact seam belongs. The connected path is where the bugs were.

### P9 started — Tasks 1–3 of 15

| Commit | Task |
|---|---|
| `5db7f10` | 1 — `database_agent/vector_versions.py`, append-and-supersede embeddings |
| `921a2e2` | 2 — `grouping/vocabulary.py`, `records.py`, `schema.py` |
| `0a744de` | 2 — `CandidateGroupDossier` (the task was one record short) |
| `7d5aae8` | 3 — golden dossiers and the two stand-in fixtures |

Load-bearing decisions already made, so a later task does not re-open them:

- `plan_version_id` is on `group_acceptance` and no other P9 table. A test
  asserts it.
- `Membership` has no `review_state`, in record or table. The SPEC's displayed
  shape lists it and the sentence beside it says it is not stored there — the
  sentence wins.
- `tests/p9/p8_fixtures.py` builds the REAL `P8Verdict`, not the shape-alike the
  plan specified. The plan was written when P8 did not exist; a shape-alike now
  would be the second verdict vocabulary P9 is forbidden to have.

### The P8/P9 contract changed, and P9 builds the changed shapes

`planning/30-p8-p9-connection-contract.md` gained a section recording it
(`23f409d`). The eight frozen names are unchanged. `DossierRequest` now carries
builder-owned `evidence_items` and `conflicts` instead of `evidence_refs`;
`run_call` takes `SiteDependencies`, not a `site_validator`. **Read that section
before writing P9 Task 10.**

---

## 2. The two live tracks

### Track A — the product build (P1–P8 done, P9 in progress)

**Next: P9 Task 4.** `planning/parts/P9-grouping/PLAN.md` is the plan; 15 tasks,
3 done. Its "Authority and current-state ledger" (line 21) and "Dependency gates"
(line 48) are current and were written with P8 unbuilt — G-P8 is now satisfied,
so Task 10's live adapter is unblocked.

Required order: Tasks 1–8, then **9 before 10**, then 11–15. Task 10 must not
begin until Task 9's `record_context_review_pending` is green.

Audit and contract documents, in the order they were written:

| Doc | What it is |
|---|---|
| `28-p1-p7-design-conformance-audit.md` | P1–P7 against the original design |
| `30-p8-p9-connection-contract.md` | the P8↔P9 seam — **revised this session** |
| `31-DOMAIN-AUDIT.md` | domain map + cohesion audit |
| `33-P8-COMPLETION-AUDIT.md` | **new** — what P8 is, and the seven seams it is not |

**The signature-level seam sweep §3 used to ask for is done for P8** and found
the `dossier_id` / `release_id` confusion (defects 4 and 5 above). The same sweep
has not been run for P1–P7.

Use graphify for reference (`graphify query "<symbol>"`; rebuilt on every commit).

### Track B — the domain research dispatch (`28-AUTOPILOT.md`)

**Read `28-AUTOPILOT.md` §0 before dispatching anything.** Two teams write into
`planning/domains/nodes/` concurrently and collisions have already cost two stopped agents.

- Claim ids in `planning/29-DOMAIN-OWNERSHIP.md` before writing. Never touch a `CODEX`-claimed id,
  **including deleting a stray file inside their claim** — report it instead.
- **Never stash, rebase, pull or reset while either team has uncommitted work.**
- 4 agents at a time, one row each, depth `J-DEPTH`. Debt rows first, then unwritten; **schema rows
  before their templates.**
- Agents killed by usage limits are expected, not a failure — they write each file as it is ready.
  **Check for survivors before re-dispatching.** A partial file with no memo is an UNTRUSTED DRAFT:
  verify line-by-line, repair, own it. Never discard unread, never trust unverified.

---

## 3. Known open work, highest value first

1. **P9 Tasks 4–15.** `planning/parts/P9-grouping/PLAN.md`. Task 4 is next; see
   Track A for the ordering gate.
2. **Domain research** — another team's track. 291 node files on disk against a
   358-row roster. Do not call the forest complete before 358/358, and do not
   touch `planning/domains/` from this track.
3. **R1c merge gate** (`planning/prompts/01c-merge-and-gate.md`) — only after
   every row is present. It audits the whole forest.
4. **Domain cohesion gaps** from `31-DOMAIN-AUDIT.md`: universal-key drift,
   memo-depth marker drift. **Resolve by one migration pass with a chosen
   contract, not ad hoc row edits.**
5. `planning/domains/check.py` legacy in-file problems — deliberately not
   rewritten yet.
6. **Signature-level seam sweep for P1–P7.** Done for P8 this session and it
   found two real defects. The same sweep has never been run on the earlier
   seams, and name resolution cannot cover it.
7. **Site E's fragment boundary is enforced nowhere** — `fragment` appears zero
   times in `src/llm_harness/`. Deferred on purpose (the published-fragment
   registry is P10's), now written down in `33-P8-COMPLETION-AUDIT.md` §3.

---

## 4. Improvements surfaced — worth doing, not yet done

Process defects, not task items. Each one cost real time or shipped a real bug.

1. **The public surface is asserted as a literal list in nine places.** Nine
   copies of one contract, and exactly how the eight-vs-six contradiction
   survived. **Publish the expected surface once** and have all nine assert
   against it. Still open.

2. **Provenance placeholders passed review.** Closed for the two writers that had
   them, but the guard asked for — *no P8 event row may carry a null `model_id`
   or `prompt_fingerprint`* — is still not written. A placeholder that satisfies
   the type is this project's most-repeated failure. Two more instances were
   found this session (`_evidence_items` synthesising builder metadata,
   `conflicts=()` hardcoded).

3. **`_ensure_identity_table` runs DDL inside a writer.** Schema creation belongs
   in `create_*_schema`, called once. Still open.

4. **Stale context is the largest token cost.** The fix is this file: update §0
   and §1 in place at the end of every session. Done for this one.

5. **A test that constructs its own record does not exercise the code that builds
   it.** New this session, and it is the root of defect 1 above: Site B's
   validator tests were green for weeks while the only production path that could
   feed them produced a dossier they would have rejected. **Where a record has one
   production builder, at least one test must go through it.**

6. **Derived registries beat listed ones.** The no-invention sweep had silently
   fallen behind by four callables and two bundles before `001a34a` made it
   derive from the package. Improvement 1 above is the same fix, unapplied.

7. **A capability is not an identity.** `release_id` was used as a dossier id and
   again as a response key. Both type-correct, both wrong.

8. **Subagent reports did not come back this session.** Three review agents ran to
   completion and none of their findings reached the parent session; only idle
   notifications arrived. If you delegate, **have the agent write its findings to
   a file** and read the file, rather than relying on the return path.

---

## 5. Standing constraints — do not lose these

**Safety, in Joseph's words:**
> *"reports, apps and system files MUST NOT BE MOVED OR READ OR ANYTHING SYSTEM OR SENSITIVE IN
> THAT SENSE."*

A protected container is **marked and counted, never opened** — present-but-untouched in the UI,
with a reachable explanation, never silently omitted, and never described as *"understood and found
unimportant"*.

**Other:**
- **Never** append `Co-Authored-By`, `Generated with`, or any AI attribution to a commit or PR.
- No summary/status markdown outside `planning/` unless asked. (This file is inside it and is the
  one Joseph asked for.)
- Don't overbuild. No extra files, config options, fallbacks or abstractions not asked for.
- Test-driven. Never report done on code that merely compiled.
- Backticks inside `git commit -m` shell-expand — use `git commit -F -` with a quoted heredoc.
- **Quote by grep, not by memory.** Fabricated quotations are this project's most-repeated defect;
  four were found and removed in one week. `grep -c "the exact string"` before quoting the design.

**Vocabulary that must not drift:** `ContractViolation` is about the **call** and always
propagates · `failed` is about the **bytes** · `unsupported` (§2.4) means **no reader exists** ·
`observation_key` (M14) is the content-addressed citation handle that survives extractor upgrade ·
P4's `Region` is `(x, y, w, h, unit)` and `norm` means **top-left** (D10).
