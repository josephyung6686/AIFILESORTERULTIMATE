# Handoff — 2026-08-26, suite green at 3121

**Read this first. It is written to be the only thing you need to resume.**
Supersedes `26-handoff.md` (which is from the P6/P7 planning era and is now history).

---

## 0. Resume in two minutes

```bash
cd "/Users/jy/GRAPH AGENT"
git log --oneline -3
python3 -m pytest -q            # expect: 3121 passed
cat planning/28-AUTOPILOT.md    # the domain-research loop, if that is your track
```

| | |
|---|---|
| Branch | `build/p6-p7-first-packages` |
| HEAD | `4746b7a fix(p8): verdict writers require provenance, and C/D verdicts are atomic` |
| Tests | **3121 passed, 0 failed** |
| Working tree | clean except `.planning/HANDOFF.json` (deleted, staged) and `.superpowers/` (untracked) |
| Built | **P1–P8.** `src/database_agent`, `evidence_shape`, `extractors`, `scan_agent`, `readers`, `facts` (P6), `privacy` (P7), `llm_harness` (P8), `orchestrator.py`, `production.py` |
| Domain research | **167 of 358** roster rows landed; 191 unwritten |

---

## 1. What just closed (this session)

A previous session left a **TDD cycle half-finished**: the tests demanded provenance the
implementation did not take. 14 tests were red. All are green now.

- `record_verdict`, `supersede_verdict`, `record_cd_verdict` now require **`model_id`,
  `prompt_fingerprint`, `release_audit_id`** — keyword-only, no defaults. They were being written as
  hardcoded `None` placeholders, so every verdict event shipped without provenance. **The three
  values were already in scope in `harness.py` three lines above the call** and were simply not
  threaded.
- `record_cd_verdict` **was not atomic**. `record_verdict` committed its own transaction and the
  identity insert ran outside it, so a failing identity insert left a C/D verdict row with no
  plan/snapshot identity — a row that cannot say which plan it judged. Both writes are now in one
  transaction (`transaction` is reentrant via SAVEPOINT).

### The one that is worth remembering

**The suite contradicted itself and I got it backwards on the first attempt.** Nine tests assert
P8's public surface: two said eight names, seven said six. I narrowed `__all__` to six. That was
wrong — `7049b2b` (the later commit) deliberately widened it, updated the SPEC's P2-envelope
section, and updated two of the nine assertions. It missed the other seven, which came from
`c31b359`, whose commit message literally says *"freeze the six-name public surface"*.

**Lesson, and it generalises:** when a suite contradicts itself, `git log -- <file>` on **both**
sides settles it. The later deliberate commit wins; the older frozen assertion is the stale one.
Do not pick the side with more tests.

---

## 2. The two live tracks

### Track A — the product build (P1–P8 done, P9+ next)

Audit and contract documents, in the order they were written:

| Doc | What it is |
|---|---|
| `28-p1-p7-design-conformance-audit.md` | P1–P7 against the original design |
| `30-p8-p9-connection-contract.md` | the P8↔P9 seam |
| `31-DOMAIN-AUDIT.md` | domain map + cohesion audit |

**P1→P8 CONNECTION AUDIT — DONE 2026-08-26. Result: connected, 0 breaks.**

Audited against `30-p8-p9-connection-contract.md`'s seam ledger, which is the authority.

- **All 8 built seams resolve** by import — every named producer and consumer symbol exists
  (P7→P8 ×2, P6→P8, P8→P6, P8→P2, P1→P8 ×2, P4→P8). The 3 remaining rows are P9, which does not
  exist; the contract correctly prefixes those symbols `eventual`.
- **Every seam the contract names an integration-test owner for has one, and they pass** —
  `test_p8_p7_egress.py`, `test_p8_p6_fact_seam.py`, `test_p8_p2_replay.py`, plus
  `test_p1_p7_live_assembly.py`, `test_p8_walking_skeleton.py`, `test_production_p1_p7.py`.
  **34 integration tests green.**
- **Invariant 1 holds — single egress.** `model_client.invoke` appears at exactly ONE site in all
  of `src/`: `llm_harness/transport.py:166`. `8edf835` added a product-wide test enforcing it.
- **Invariant 4 holds — D14.** `privacy/gate.py:510` writes `release_id=None` on the audit row.
- **`src/production.py` composes P1–P7 only, and P8's absence is deliberate**, stated in its own
  docstring: *"whether an LLM stage exists is a decision already frozen inside each supplied P6
  resolver."* P8 is an island in `src/` on purpose — reached through the P6 seam, not wired into
  the production composition root.

**Caveat, and it is the one that has bitten this project before:** this audit verifies that names
resolve and that the owned integration tests pass. It does **not** prove every signature matches at
every call site — a consumer can call a producer with a parameter it does not have and the *name*
still resolves. That defect class has appeared here twice (`set_policy(author=)`, and the P8
provenance placeholders closed this session). A signature-level sweep across seam call sites is the
natural next hardening step.

Use graphify for reference (`graphify query "<symbol>"`; the graph is rebuilt on every commit).

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

1. ~~P1→P8 connection audit~~ — **DONE, 0 breaks** (see Track A). Follow-up: a signature-level
   sweep across seam call sites, which name-resolution cannot cover.
2. **191 unwritten roster rows** (of 358). Do not call the forest complete before 358/358.
3. **R1c merge gate** (`planning/prompts/01c-merge-and-gate.md`) — only after every row is present.
   It audits the whole forest.
4. **Domain cohesion gaps** from `31-DOMAIN-AUDIT.md`: universal-key drift (57 rows omit
   `proposed_context_terms`, 46 carry extra keys), memo-depth marker drift (87 memos lack a literal
   `J-DEPTH` header). **Resolve by one migration pass with a chosen contract, not ad hoc row edits.**
5. `planning/domains/check.py` reports **566 legacy in-file problems, 0 cross-file** — mostly
   dimensions branching on undeclared fields. Deliberately not rewritten yet.

---

## 4. Improvements this session surfaced — worth doing, not yet done

These are process defects, not task items. Each one cost real time or shipped a real bug.

1. **The public surface is asserted as a literal list in nine places.** That is nine copies of one
   contract, and it is exactly how the eight-vs-six contradiction survived. **Publish the expected
   surface once** (a module constant or a conftest fixture) and have all nine assert against it.
   Then widening it is one edit and cannot go half-applied.

2. **Provenance placeholders passed review.** `audit_id=None, model_id=None,
   prompt_fingerprint=None` sat hardcoded in two writers, so every event shipped provenance-free
   and nothing failed. **Add a guard: no P8 event row may carry a null `model_id` or
   `prompt_fingerprint`.** A placeholder that satisfies the type is the failure mode this project
   keeps hitting — the same shape as "a column with no writer".

3. **`_ensure_identity_table` runs DDL inside a writer.** Schema creation belongs in
   `create_*_schema`, called once. A writer that may create its own table hides a missing schema
   step until the first call.

4. **Stale context is the single largest token cost.** This session opened ~195 commits behind and
   spent a large fraction of its budget re-orienting. **The fix is this file**: update §0 and §1 at
   the end of every working session, in place, rather than adding a new numbered handoff. One
   current handoff beats seven historical ones.

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
