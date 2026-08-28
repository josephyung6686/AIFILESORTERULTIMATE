# 67 — Handoff, 2026-08-29

Written because Joseph is restarting the machine. Two agents were mid-build and will not
survive the restart; §3 says exactly where each one stopped and how to resume it.

**Authority order, unchanged:** `00-database-agent-product-design.md` wins → part SPECs →
PLANs → live `src/`. `00` has been right in every dispute so far.

**Standing constraints, unchanged and non-negotiable:**

- **Security.** Reports, apps, system files and anything sensitive in that sense are **MARKED
  AND COUNTED, NEVER OPENED**. Present-but-untouched, with a reachable explanation, **never
  silently omitted**, never described as "understood and found unimportant." `66` §4 and §10
  extend this to search and to filing and do not weaken it.
- **North star.** Judge every decision by what a real, multi-role human would want. Not the
  lawyer OR the parent OR the researcher — the person who is several of those at once, whose
  research paper is also school homework, whose legal document is part of an application.
- **Manual approval** is required for templates and mechanisms.
- **Git.** Stage and commit in ONE shell invocation with EXPLICIT paths. Never `git add -A` —
  the index is shared with other sessions.
- **`python3`, not `python`.** There is no `python` on PATH; a run that reports mass failures
  is usually this.
- **`-p no:randomly` when a `thinc`/spaCy import is in the interpreter**, or every test errors
  in setup and teardown. Documented in `pyproject.toml`. This once produced 4501 phantom errors.

---

## 1. What this session did

### The new design landed

`66-FIND-FILE-AND-ONBOARDING.md` is Joseph's replacement design for Find, automatic filing and
onboarding, supplied 2026-08-29 and reproduced as written. Five spans arrived corrupted in
transit; `66` §24 lists every repair and marks the **one that required judgement** — §7's
sentence about what a wrong move costs the user. That one should be checked against what he
actually wrote.

`61` and `62` are marked superseded in place, with precise notes on what died and what survived,
so neither can be built from by accident.

### It reversed two rulings, and both reversals are right

| | `61` said | `66` says |
|---|---|---|
| First run | Ask age range, kids, profession, purpose (§A.0, Joseph's own verbatim framing) | Ask **nothing**. Choose folders, review privacy defaults, start searching (§14, §6) |
| Other people | "Does anyone else appear in your files?" as an onboarding question (§A.4 q2) | Only inside a deliberate protected-family workflow, with a user-selected relationship category (§15) |

What survived is `61` §A.3's structural / contextual split, now `66` §13 — and it is sharpened
rather than merely carried: age range, time availability and broad profession description are
explicitly **CONTEXTUAL**, so they may order suggestions and may **not** create, remove, rename,
place, expose or move anything. That is a demotion of Joseph's original questions from "we use
that for everything else" to "these may change what we offer you first."

### It resequenced the plan

`63` §2 is rewritten. The old order is in git at `1078ecd`.

| | old | new |
|---|---|---|
| 1 | corpus role declaration | **Find** — local, read-only |
| 2 | retrieval | connect Find to inspector / groups / canvas (absorbs P13) |
| 3 | P12 apply+undo | onboarding — the question **registry** before any screen |
| 4 | automatic filing | P12 apply+undo |
| 5 | P13 review canvas | automatic filing |

The old order put the questionnaire first. The new order puts first the one capability a person
can use on day one having granted no authority at all. That is the north star test, and the old
order failed it.

### It settled the sizing question

`65` asked whether `cli.py`'s single `_STRUCTURED` pattern — `\b[A-Z][A-Z0-9]*[0-9]{3,}\b`,
which matches `PHYS1401` and misses `PHYS 1401` — should be answered by reading more or by
asking the user.

**Ruling: widen the extractor. Do not add a question.** `66` §14 scopes questions to what
evidence *cannot safely determine* — the user's role, their relationship to a person or
institution, their purpose. A course code with a space in it is none of those; it is a **reading**
failure. `66` §4 requires "unreadable" and "unsupported format" to stay distinct, visible states
precisely so reading failures are not laundered into interrogations of the person.

Full reasoning: `63` §10.

### It gave `sensitivity_policy_ref` a purpose

G8's one genuinely inert concept — all 30 definitions carry the field, nothing in `src/` reads
it. `66` §4's protected-display and protected-search policies are what it is for: **how much a
protected result may say about itself on a shared screen.** Still inert until Find is built, but
no longer unexplained.

---

## 2. Is `66` a better document than `61` + `62`?

Yes, substantially. Four things it does that they did not:

1. **It catches the profiling failure.** A person opening the product to find a document should
   not have to disclose their age, family and profession first. `61` had that backwards and had
   it backwards in Joseph's own words, which is exactly the kind of ruling that survives review
   because nobody wants to contradict the owner. `66` contradicts it correctly.
2. **The release order follows from the north star** instead of from the engine's dependency
   graph. Find first is a statement about who the product is for.
3. **§3's six-state model is new and load-bearing.** Current location · filed home · also-related-to ·
   shared-material · historical · possible placement. Nothing in `61`/`62` was this precise, and
   this is the design that tells `horizontal_candidates` what to produce instead of a flat list.
   It is also the answer to "a research paper that is also school homework": that is *two accepted
   relationships and one physical location*, not a confidence failure.
4. **§8 replaces a threshold with nameable authority.** Nine dimensions the user actually
   understands — source scope, destination scope, eligibility, evidence standard, cadence,
   exclusions, collisions, undo period, revocation. `62` §C was a paragraph.

Three places it is weaker, which are worth knowing before building:

1. **§2 says "one retrieval model, not two rankings" without saying what happens when the one
   model is bad at one of the two jobs.** P11's retrieval is tuned for scoring a file against a
   *destination node*. Text search is a different question. The principle is right — two rankings
   that disagree is the defect — but the doc does not say which way to resolve it when the shared
   model serves search badly. This is the first real engineering risk in item 1 of the sequence.
2. **§16 is honest that the profession matcher is an open problem**, which means the thing gating
   onboarding is undesigned. Consistent with what Joseph said he would explain later; just do not
   mistake §16 for a specification.
3. **§22 gates everything on "P1–P11 verified" but does not say what subset Find actually needs.**
   Find needs the index, evidence, retrieval and privacy. It does not obviously need frozen trees
   or placement. Find may be shippable earlier than the full gate — worth asking rather than
   assuming.

And one thing it does not settle: **why four files sharing `PHYS1401` became four groups rather
than one.** §3 governs how multiple relationships are *presented*; it says nothing about how the
grouping engine decides cardinality. Still open (`65`).

---

## 3. The two agents that died on the restart

Neither had committed. Both were working from an approved design. **Check the working tree
before resuming — partial edits may be on disk.**

### `build-edit-durability` — doc `64`, approved "build it as designed"

**Where it got to:** past RED into GREEN. On disk at restart:

- `tests/p10/test_p10_user_edits.py` — written (~20 KB)
- `src/tree_design/user_edits.py` — created
- `src/tree_design/freeze.py` — modified (+52 lines)
- `tests/p10/seam_corpus.py` — modified (+30 lines)
- a stray `src/tree_design/freeze.py.tmp.*` may exist — **delete it**, it is a half-written
  atomic-write temp file

**To resume:** run `python3 -m pytest tests/p10/ -q -p no:randomly` and read what fails. The
task was `64` as designed: an overlay keyed on the stable triple `(schema, role_ref, field_ref)`
so it survives `00` §8.8 minting a new `node_id` per plan version, applied at the **END** of
routing so a rename cannot smuggle a broken recipe past the gates. `64` §5a first, because
everything blocks on it.

**Carry this forward — it is new since the agent was dispatched.** `66` §17 adds a requirement
`64` §7 explicitly scoped out:

> Existing approved structure remains stable unless the user explicitly adopts the new plan.

`64` builds the storage half (the user's edit is a fact that outranks re-derivation). `66` §17
is the consent half: an edited structural answer opens a **draft** the user adopts, with a
visible diff, never a silently applied change. Not a contradiction, and **not a reason to stop
the build** — but `64`'s overlay must be readable as "what the user asserted" independently of
whether the plan version carrying it has been adopted. Verify that property when it lands.

### `fix-cli-output` — the readability defects from `65`

**Where it got to:** `src/cli.py` +186 lines, `tests/test_cli.py` +250 lines. Uncommitted.

**What it was fixing,** from judging a real run as a user would:

- files identified by UUID (`74ce335f-110b-42c0-8a50-ecdc8f8734b7`) — you cannot tell which of
  your files that is
- the same paragraph printed four times verbatim
- `Plan version_2` leaking internal versioning into a person's screen
- `Files: 4 decided, 0 placed` duplicating `For review: Not yet placed (4 files)`

**The one instruction that must not be lost:** the protected-containers block is **never**
summarised away. Marked, counted, explained, never silently omitted — even when tidying output
is the whole point of the task.

**To resume:** `python3 -m pytest tests/test_cli.py -q -p no:randomly`, then re-run the live
demo and read the output as a person, not as a developer.

---

## 4. Gate status — `63` §0

| | condition | state |
|---|---|---|
| G1 | full suite green | ✅ **5185 passed, 19 skipped, 1 xfailed, 0 failed** (4640 at session start) — **re-run after the two agents' work lands** |
| G2 | scale suite green | ⚠️ **2 of 19 failing** (was 13) |
| G3 | no strict xfail standing | ✅ one stands, correctly argued — `64` §8 |
| G4 | order independent | ✅ 5185 passed randomised |
| G5 | every schema can file | ✅ 19 of 23 + 4 named protection exemptions |
| G6 | `load_catalogue` has a caller | ✅ |
| G7 | P8→P11 production composition | ✅ `run_production_corpus` + `src/cli.py` |
| G8 | nothing inert | ✅ 1 genuine (`sensitivity_policy_ref`) — **now explained by `66` §4** |
| G9 | connection audit | ✅ 3 findings recorded rather than a tick — `63` §8 |
| G10 | **the persona re-run** | ❌ **open, and it is the one that matters** |

**G2, the two that remain.** Scan is still superlinear on unique files — 2,681 files/s at 1,000,
1,326 at 4,000, per-file cost ×2.0. The transaction-boundary fix moved the *constant* from 69
files/s to ~1,700 and did not change the *shape*. And `model.max_dossier_tokens_per_call` is
unset in one config test; `fix-canvas` independently found that this one key answers four
different questions, so the test is probably right that the shape is wrong.

**G10 is the north star condition.** The other nine measure whether the machine works. G10 asks
whether a person can use it. It is not implied by any of the others and it is the easiest to
skip. `59`'s persona evaluation redone against the current state — the lawyer, the parent, the
researcher, and the person who is all three.

---

## 5. What to do next, in order

1. **Delete `src/tree_design/freeze.py.tmp.*` if present.**
2. **Finish `build-edit-durability`** — §3 above. Then verify `66` §17's draft-not-applied
   property against what it built.
3. **Finish `fix-cli-output`** — §3 above. Protected block stays.
4. **Full suite**, and it must return to zero: `python3 -m pytest tests/ -q --tb=short -p no:randomly`
5. **Widen the extractor** — the `66` §14 ruling. `_STRUCTURED` in `src/cli.py` is one pattern
   and a course code with a space defeats it. Read `65` for the sizing evidence and `63` §10 for
   why this is a reading fix and not a question.
6. **G2's two scale failures.**
7. **G10 — the persona re-run.** The gate does not close without it.
8. Only then: item 1 of `66` §22's sequence, which is Find.

---

## 6. Open — needs Joseph, do not guess

1. **`66` §24's judgement repair.** §7's sentence about the cost of a wrong move was
   reconstructed from §7's own opening. Confirm or replace it.
2. **The role declaration guidance he still owes.** *"I'll explain everything much more when
   needed."* `66` §16 confirms the matcher is judged rather than looked up and that an unmatched
   answer stays unmatched, but the matcher itself is explicitly an open problem. **Nothing in
   §16 should be built until that arrives.**
3. **What subset of P1–P11 does Find actually need?** §2 above. Find may not need frozen trees
   or placement, in which case it ships earlier than the full gate.
4. **Grouping cardinality** — four files, one course code, four groups. Not settled by `66`.
