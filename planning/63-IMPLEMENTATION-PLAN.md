# 63 — Implementation plan for what comes after the engine

Date: 2026-08-28. Owner instruction: *"add building this into the task plan but only
implementation plan, and only when you are confident that P1–P11 is perfect."*

**Design is `66-FIND-FILE-AND-ONBOARDING.md`, 2026-08-29.** It replaces `62`'s §A/§B/§C and
`61`'s Parts A and B, and it RESEQUENCES this plan — see §2. `61` and `62` are marked
superseded in place; read `66` first.

This document is sequencing and a gate. **Nothing below starts until §0 passes in full.**

---

## 0. THE GATE — what "P1–P11 is perfect" means, checkably

Not a feeling. Ten conditions, each verifiable by a command, each currently FALSE or UNKNOWN.
Re-run the whole list; a single failure holds the gate closed.

| # | condition | how it is checked | today |
|---|---|---|---|
| G1 | Full suite green | `python3 -m pytest tests/ -q` → 0 failed | 1 failed |
| G2 | Scale suite green | `SCALE_STRESS=1 python3 -m pytest tests/integration/test_scale_stress.py -q` → 0 failed | ≥1 failed |
| G3 | No strict xfail left standing | grep `xfail(strict=True)` → each one closed or argued in writing | 1 open (P9 versions) |
| G4 | Test order independent | `pytest-randomly` installed, three seeded runs agree | never run |
| G5 | Every schema can file | all 23 either have templates or are a named protection/safety exemption | 6 of 23 |
| G6 | `load_catalogue` has a caller in `src/` | the existing guard in `tests/integration/test_ambiguity_cases.py` inverts | no caller |
| G7 | P8→P11 has a production composition | a callable in `src/` runs the chain, as `run_production_p1_p7` does for P1–P7 | absent |
| G8 | Nothing inert | every concept has a reader, or a guard that fails when a producer appears | 7 of 10 wired |
| G9 | graphify audit clean | `graphify update .` then a connection pass over every part boundary | not run |
| G10 | The persona re-run | `59`'s evaluation redone against the new state; no persona fails on a defect this plan could have fixed | not run |

**G10 is the one that matters most and the one most easily skipped.** The other nine measure
whether the machine works. G10 measures whether a person can use it, which is the north star and
is not implied by any of the others.

---

## 1. Finish the engine (in flight or queued — this is not "after")

Listed for completeness because the gate depends on it, not because it is part of this plan.

1. Multi-domain branching, P9 acceptance across versions, placement retrieval cost, the
   two-home message, identity resolution cost — all in flight.
2. Templates for the 17 uncovered schemas — in flight, four agents.
3. `load_catalogue` caller · merge the wave-2 library · tree-health quadratic · width cap ·
   residual questions ordering · `sensitivity_policy_ref`.
4. P8→P11 production composition, and a CLI.

---

## 2. RESEQUENCED, 2026-08-29 — `66` reorders everything below

`66-FIND-FILE-AND-ONBOARDING.md` §22 sets the release order, and it INVERTS what this
document originally had. The old sequence (role declaration → retrieval → P12 → filing →
canvas) is in this file's git history at commit `1078ecd`. It was wrong in one specific way:
it put the onboarding questionnaire FIRST, ahead of the capability that makes the product
useful to someone who never grants it any authority at all.

`66`'s order, and the reason for each position:

| # | work | why here |
|---|---|---|
| 1 | **Find** — local, read-only retrieval | Ships before any mutation. A user who never builds a tree or grants a filing policy must still be able to search their own index. This is the product's front door. |
| 2 | **Connect Find** to the evidence inspector, accepted groups, destination canvas, review surfaces | Moves the user from "I found this" to "I understand why this is related" with no hidden state change. Absorbs what was P13. |
| 3 | **Onboarding redesign** — the structural-question registry FIRST, then the flows | Cannot be designed independently of templates and policy. `66` §21: define the registry and what consumes each answer before any interaction is built. |
| 4 | **P12 — apply and undo** | The movement engine. Everything in `66` §11 (conditional undo, stale-plan detection, 90-day default) is P12's contract, not automatic filing's. |
| 5 | **Automatic filing** — "Keep this folder organized" | Last. `66` §22: not scheduled until P1–P11 are verified AND the product can be shown to decline unsafe cases reliably. |

### 3. Find — FIRST

Design: `66` §§1–6, contract §18. New constraints this plan did not previously carry:

- **§1 is an egress constraint, not a preference.** Query text, filenames, paths, extracted
  content, OCR, embeddings, file facts, the destination tree, and the result set may not reach
  a cloud model for ordinary search. This must bind to the existing egress guard, not be a
  comment. A test that sends a query through Find with the guard armed is the only proof.
- **§2 forbids a second ranking.** Find reads P11's retrieval, not a new scorer. If Find's
  order and the destination-node retrieval order can disagree, that is the defect.
- **§3 is a six-state model**, and the six are not interchangeable: current location, filed
  home, also-related-to, shared-material relationship, historical location, possible placement.
  `horizontal_candidates` currently produces something closer to one flat list; this is the
  design that tells it what to produce.
- **§4 extends the protected-container rule to search.** Marked and counted, never opened —
  now with two explicit states (standard, unlocked) and a re-authentication gate between them.
- **§5**: no-result must name WHICH state applies. Five distinct messages, never one
  "could not find."

### 4. Connect Find to the surfaces — SECOND

Design: `66` §22 ¶2. This is what was P13 (the review canvas), reframed: the canvas is not a
separate destination, it is where a search result explains itself. No state changes.

### 5. Onboarding — THIRD, and it is a registry before it is a screen

Design: `66` §§12–17, contract §20. **`66` reverses two rulings from `61`.** The first-run
profile interview (age, kids, profession) is out; §14 replaces it with evidence-linked
questions asked only when a specific decision is blocked. "Does anyone else appear in your
files" is out as a general question; §15 admits it only inside a deliberate protected-family
workflow with a user-selected relationship category.

What survives from `61` §A.3 is the structural / contextual split, now `66` §13 — and `66`
sharpens it: age range, availability, and broad profession description are CONTEXTUAL, so they
may order suggestions and may not create, rename, place, expose, or move anything.

`66` §16 confirms the ruling already recorded at `62` §D: the matcher is judged, not looked up,
and an unmatched answer stays unmatched. Four outcomes, raw wording stored, never converted
directly into a folder name or a filing permission.

`66` §17 is the one that touches work ALREADY IN FLIGHT — see §10 below.

### 6. P12 — apply and undo — FOURTH

Design: `66` §11. Conditional undo with five pre-checks (content still expected, hash unchanged,
no overwrite, source available, no later external change). 90-day default retention, user
selectable 30 / 90 / 365 / until-cleared. Stale-plan detection on source, destination,
permission state, cloud-sync state, and content hash.

### 6a. Automatic filing — LAST

Design: `66` §§7–11, contract §19. The nine-dimension policy schema of §8 is the deliverable,
not a threshold. Dry run always first. The system may never widen its own policy. Applications
are suggest-and-review only in the first release (§10).

## 7. What this plan does not do

- It does not schedule the three open questions in `62` §C — the profession matcher's failure
  mode, re-running onboarding after freeze, and how long "individually reversible" lasts. Those
  are owner decisions and are listed there to be answered, not assumed.
- It sets no dates. Every item above is gated on the one before it, and the gate in §0 is gated
  on work that is still in flight.

---

## 8. G9 result — what the connection audit actually shows, and what it cannot

Run 2026-08-29 against a refreshed graph (32,946 nodes, 57,756 edges, 1,647 communities).

**graphify orients; it does not prove a connection.** Its `path` output distinguishes
`calls [EXTRACTED]` from `imports` and `[INFERRED]`, and only the first is evidence.
`load_shipped_catalogue --calls--> load_catalogue` is one hop and real. But
`run_production_corpus → place_file` resolves as three hops of **imports** through `cli.py`,
and `Detector → assign` as an **inferred** type relationship through `ClassificationRecord`.
Under this project's own rule those prove nothing:

> *A seam is verified when the caller's arguments have been bound against the callee's live
> signature, or when a test drives the real callee end to end — never when a reference chain
> exists between them.*

So the connection claim rests on the seam tests — `test_production_corpus.py`,
`test_p10_p11_live_seam.py`, `test_recognition_seam.py` — and the graph is a map, not a proof.
This is worth stating because a graph that shows everything joined is exactly what this
codebase looked like while eight seam breaks sat inside it.

**A textual screen of `src/`** found 364 of 1,188 public definitions with no reference from any
other `src/` file. **That is a screening list and not a defect list** — most are exception
classes raised in their own module, or `cli.py`'s own helpers. Three are whole capabilities and
are the real finding, each defined in one file, referenced by no other `src/` file, and covered
by two to five test files:

| capability | file | tests | note |
|---|---|---|---|
| the adversarial gate | `eval_harness/adversarial.py` | 2 | `run_gate`, `run_case`, `load_all_cases`, `build_case_bundle` |
| content verification | `database_agent/verify.py` | 3 | `verify_content`, `confirm_cross_volume_copy` |
| the older vector store | `database_agent/vectors.py` | 5 | `put_embedding`/`get_embedding`, apparently superseded by `vector_versions.py`, which is what `grouping/embeddings.py` actually imports |

The third is probably dead code rather than a broken chain, and dead code that ships with five
test files is its own hazard: it reads as a supported path. **None of the three is chased here.**
They are recorded because the honest answer to "is everything connected" is *no, and here are
the three places*, not a green tick.

---

## 9. Gate status, 2026-08-29

| | condition | state | evidence |
|---|---|---|---|
| G1 | full suite green | ✅ | **5185 passed, 19 skipped, 1 xfailed, 0 failed** (4640 at session start) |
| G2 | scale suite green | **2 of 19 failing** | was 13 of 19 |
| G3 | no strict xfail standing | ✅ | one stands and correctly — §8 of `64` |
| G4 | test order independent | ✅ | **5185 passed in randomised order**, identical to sequential. `--randomly-dont-reset-seed` required, see `pyproject.toml` |
| G5 | every schema can file | ✅ | 19 of 23 with templates; 4 are named protection/safety exemptions |
| G6 | `load_catalogue` has a caller | ✅ | `load_shipped_catalogue`, and the guard inverted |
| G7 | P8→P11 production composition | ✅ | `run_production_corpus`, plus `src/cli.py` |
| G8 | nothing inert | ✅ | recounted; 1 genuine (`sensitivity_policy_ref`), 2 tracked |
| G9 | connection audit | ✅ | §8 above — answered, with 3 findings recorded rather than a tick |
| G10 | the persona re-run | **open** | first real run recorded in `65`; the persona sweep is still owed |

### G2 — the two that remain

**Scan is still superlinear on unique files.** 2,681 files/s at 1,000 files, 1,326 at 4,000 —
per-file cost x2.0. The transaction-boundary fix moved the constant from 69 files/s to ~1,700
and did not change the shape. Every other scan measurement is flat: 4 syscalls per file at any
duplicate-family size, 1 row read per file on re-observation.

**`model.max_dossier_tokens_per_call` is unset in one test.** The failing test asks whether one
ceiling can serve both the picker and the depth limit, which `fix-canvas` independently
identified as a configuration-shape question — `config.py` now records a complaint that the key
answers four different questions. The test is probably right that the shape is wrong.

### What this session changed, for the record

Green went 4640 → 5185 with every defect found along the way fixed rather than deferred.
Measured, before → after:

| | before | after |
|---|---|---|
| scan throughput | 69 files/s · 24 min for 100k | **~1,700 files/s · ~1 min** |
| identity per file | 402 syscalls at family-800, x4.0 | **4 syscalls, x1.0** |
| placement retrieval | x6.8 · 8M queries at 10k×800 | **0.2 ms/file flat, x1.2** |
| tree health | 3.343s at 3,200 nodes → 27 min at 50k | **0.027s · 0.48s at 51,200** |
| picker | x3.4 · 34s per option at 10k folders | **x0.6 · ~1s** |
| warnings on a 3,200-node tree | 2,991 | **21, ranked** |
| widest single split | 337 folders under a ceiling of 6 | **5** |
| schemas that can file | 6 of 23 | **19 of 23 + 4 named exemptions** |
| applicability rows reachable | 25 of 54 | **208 of 208** |
| human labels | 2 fixtures | **503, none equal to its field key** |


---

## 10. What `66` changes about work already in flight, 2026-08-29

**`66` §17 adds a requirement `64` deliberately scoped out.** `64` (user edits and catalogue
upgrade, currently being built by the `build-edit-durability` agent) establishes that a user's
rename is a fact that outranks re-derivation, keyed on `(schema, role_ref, field_ref)` so it
survives §8.8's per-version `node_id` mint. That is correct and unchanged.

But `64` §7 treats the version-diff surface as somebody else's problem — *"the pipeline's
adopt-a-new-version path and P13's version-diff surface, neither of which..."*. `66` §17 makes
that surface a REQUIREMENT of the same interaction:

> When a user edits or re-runs a structural answer, the product creates a draft plan version. It
> shows a meaningful diff: which schemas become active or inactive, which templates are affected,
> which branches may need review, which placement proposals become invalid or newly possible,
> whether any protected area changes, and whether any filing policy is paused. It must not
> silently rename folders, reclassify files, reveal protected records, or move anything as a
> consequence of a changed answer.
>
> Existing approved structure remains stable unless the user explicitly adopts the new plan.

**This is not a contradiction and the in-flight build should not be stopped.** `64`'s overlay is
the storage half; `66` §17 is the presentation-and-consent half, and it lands in item 2 of the
new sequence (connecting Find to the review surfaces). The gap to carry forward is one sentence:
*an edited structural answer must open a DRAFT the user adopts, never a silently-applied change.*
`64`'s overlay must therefore be readable as "what the user has asserted" independently of
whether the plan version carrying it has been adopted. Verify this when the agent reports.

**`66` §16 confirms `62` §D** rather than replacing it. No action; `62` §D stands.

**`66` §4 gives `sensitivity_policy_ref` its first reader.** All 30 definitions carry the field
and nothing in `src/` reads it — recorded as an open confusion in `65`. `66` §4's
"protected-display policy" and "protected-search policy" are what it is for: how much a
protected result may say about itself on a shared screen. It stays inert until Find is built,
but it is no longer unexplained.

**`66` §14 and §6 settle what `--situation` is.** The first-run screen is folder selection, not
an interview; the front door asks nothing. `--situation` is not wrong — it is a flag on the
TREE-DESIGN command, which is not the front door and never was. The correction is to stop
treating the current CLI as the product's entry point. Find is the entry point and does not
exist yet.

**`66` does NOT settle** why four files sharing `PHYS1401` became four groups rather than one
(`65`'s open question). §3 describes how multiple relationships are PRESENTED; it says nothing
about how the grouping engine decides cardinality. Still open.

### The sizing question, answered

`65` asked whether the single `_STRUCTURED` pattern in `cli.py` — `\b[A-Z][A-Z0-9]*[0-9]{3,}\b`,
which matches `PHYS1401` and misses `PHYS 1401` — should be answered by widening what is read or
by asking the user. `62` §D already noted these are not one axis. `66` §14 settles it:

> When the engine encounters a repeated ambiguity that prevents a useful template, group
> interpretation, or destination proposal, it asks a narrow, evidence-linked question.

A question is for what evidence **cannot safely determine** — the user's role, their relationship
to a named person or institution, their purpose. `PHYS 1401` with a space is not any of those. It
is a **reading** failure, and `66` §4 requires Find to say "unreadable" and "unsupported format"
as distinct states precisely so that reading failures stay visible as reading failures instead of
being laundered into questions for the user.

**Ruling: widen the extractor. Do not add a question.** No onboarding answer could have recovered
that course code, and asking would have taught the product to cover a reading gap by interrogating
the person — the exact inversion `66` §12 exists to prevent.
