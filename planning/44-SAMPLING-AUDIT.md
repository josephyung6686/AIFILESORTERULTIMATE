# Sampling audit — where a conclusion outran its population

Date: 2026-08-27 · **All counts recomputed at 2026-08-27T12:59:23Z** against a frozen read-only copy of
`planning/domains/` (`roster.json`, `canonical_fields.json`, 668 files in `nodes/`). The swarm is writing
that directory live; nothing here wrote to it. `src/` was read at commit `b7c6e8f` via `git grep` /
`git ls-tree`, **not** from the working tree, which two build agents are actively editing.

Scope: one error family only — *a conclusion computed over a subset and presented as a property of the
whole*, plus its inverse (refusing a conclusion the data supports). Not a general review of these
documents.

Verdicts: **SOUND** (scoped correctly) · **OVERSTATED** (true of its sample, presented as general) ·
**WRONG** (false even of its sample) · **UNCHECKABLE** (the data to settle it does not exist).

Every quotation below was matched by exact substring against the file it is attributed to before being
written down. Misses: 0.

---

## 0. The answer, before the evidence

| | |
|---|---|
| **Known instance 1 — "cut Recipe 2"** | **CONFIRMED as a defect**, and the correction is **partly over-corrected**. The brief's arithmetic was right for its population; the imperative was not scoped. But "11 rows / 5 domains, zero counter-examples" is 4 bound + 7 prose, and the 7 propose a level that is either unminted or canonically `destination_eligible: false`. §1.1 |
| **Known instance 2 — "24 roles"** | **CONFIRMED.** The correction is right and is not over-corrected. Two small imprecisions: 28/22 are *distinct keys* (declarations are 31/24), and the honest band on "24" is 23–28. §1.2 |
| **New instances found** | **20.** Six are WRONG (arithmetic false of its own sample), eleven OVERSTATED, one UNCHECKABLE, two are inverse-error (§5). §2 |
| **"Roles grow sub-linearly"** | **Not evidenced.** Two points, measured by two different methods, the second bar-dependent to ±4, and §9 of `43` turns the growth rate into a *policy* rather than a measurement. The "fields grow linearly" half is loosely supported; the roles half is not. §4 |
| **The one claim to stop relying on** | `43` §8: *"Two independent readings agreeing within ~5% … means the prose layer is reproducible enough to cut recipes on."* It is the licence under which 216 hand-coded rows became evidence, and the two readings shared a codebook. §6 |

---

## 1. Task A — the two known instances, recomputed

### 1.1 Instance 1 — "If you want one cut, cut Recipe 2"

**The claim, verbatim** (`41-TEMPLATE-DECISION-BRIEF.md` §3):

> *"Recipe 2 is the weakest: only 4 rows, 3 of them academic. **If you want one cut, cut Recipe 2** — the
> cost is writing the same thing twice instead of once, and nothing else."*

**Recomputed mechanically over the 54 bound rows** (adjacent pairs; role map as published in `37` §2.1):

| Recipe | adjacent rows | domains | of which academic | relative-order (any distance) | counter-examples |
|---|---:|---:|---:|---|---:|
| 1 · `subject_anchor > artifact_kind` | 14 | 3 | 7 | 14 for / 0 against | 0 |
| 3 · `cycle_period > artifact_kind` | 4 | 2 | 2 | 7 for / 0 against | 0 |
| 2 · `holder_institution > subject_anchor` | 4 | 2 | **3** | 5 for / 0 against | 0 |

Recipe 2's four rows: `academic.continuing-education`, `academic.online-course`, `academic.study-abroad`,
`research.lab-notebook-protocols`. Recipe 3's four: `academic.k12-schooling`,
`academic.recommendation-letters-written`, `applications.scholarship-fellowship`,
`applications.undergraduate-packet`.

**The brief's arithmetic is exactly right for its population.** Recipes 2 and 3 tie on adjacent rows and
domains; Recipe 2 is more concentrated (3 of 4 on one schema vs 2 of 4) and weaker on relative order
(5 vs 7). Calling it the weakest *of the launch six* is defensible.

**The defect is the imperative, not the arithmetic.** "If you want one cut, cut Recipe 2" is an action on
the recipe library — an artefact intended to outlive launch — derived from six domains, with no scope
marker anywhere in the sentence or its paragraph. **Verdict on the original: OVERSTATED, confirmed.**

**Is the correction itself sound?** Partly. What I can verify, I confirm:

- The bound half is exactly as `42`/`43` report: 4 rows / 2 domains, zero reversals adjacent or at any
  distance, in either direction.
- `43` §4.2 #6 and `42` §2 row 10 both split the number into `F 4/2` + `P 7/3`. The documents are honest.

What I found that neither document records, and that materially weakens the correction:

**The 7 prose rows all propose the holder's *own organisation* as the top level, and that level is either
unminted or canonically forbidden as a destination.**

- `canonical_fields.json`: `our_firm` → `destination_eligible: **false**`, role *"the holder's own
  organization on an engagement; authorship-side identity, **never a collection point**"*. Compare the two
  keys the four bound rows actually use: `school` and `lab`, both `destination_eligible: true`.
- `career.consulting-client-engagement` — the row `43` §5.1 cites as proof that `holder_institution` is a
  distinct role — says: *"`our_firm` must NOT be a level, ever, even though it is the single most reliably
  extractable organization on these files."*
- `nonprofit.religious-institution`: *"The institution level is seeded ineligible"*;
  `nonprofit.fundraising-donor`: *"with the association level seeded ineligible"*;
  `nonprofit.member-association`: *"the ASSOCIATION only where the corpus genuinely spans more than one"*.
- `business_operations.board-governance`: *"An entity level only where the corpus genuinely spans more than
  one entity"*; `business_operations.vendor-management`: *"a supplier-first tree is precisely an
  ORGANISATION used as a collector, and 00 rules that out"*.
- The keys these rows would bind to do not exist. `organization` is a **proposed** field in
  `business_operations`, `construction_property`, `nonprofit`; `employer` is proposed by `career`. Neither
  is in `canonical_fields.json`.

**Verdict on the correction: direction right, strength OVERSTATED.** "Do not cut Recipe 2" is the correct
call — a recipe with zero counter-examples in 256 rows should not be cut to save an indirection. But the
number that carries it should be stated as **4 bound rows / 2 domains, plus 7 prose rows / 3 domains whose
top level is unminted or destination-ineligible**, not as "11 rows across 5 domains with zero
counter-examples". Stated flat, it repeats the original error with the populations swapped.

**One further slip in the lead's own summary of the correction:** *"it was weak only because five of the
domains using it were not in the sample."* Three domains were added (`business_operations`, `career`,
`nonprofit`); five is the *total*. The documents say "+ business_operations (5), career (1), nonprofit (1)
= 5", i.e. five domains in total. The summary inflates the delta.

### 1.2 Instance 2 — "24 roles"

Recomputed:

| Claim | My count | Verdict |
|---|---|---|
| 6 of 23 schemas declare any fields | `academic` 5, `code` 4, `college_applications` 5, `finance` 5, `photos` 6, `research` 6 — **6 of 23** | SOUND |
| 28 fields | **28 distinct keys**; **31 declarations** (`project`, `artifact_type`, `school` each declared by two schemas) | SOUND as *distinct keys*; say which |
| 22 destination-eligible | **22 distinct keys**; **24 declarations** | same |
| the other 17 declare zero | **17** | SOUND |
| 15 → 24 as the corpus went 6 → 23 domains | 15 roles cover all 22 dimension tokens on the 54 bound rows (unmapped: **0**); `43` §2.2 adds 9 | SOUND as counts |
| 3 roles named-but-not-adopted | `43` §2.4: `channel_locus`, `direction_role`, `provenance_role` | SOUND |

**No over-correction.** Two refinements worth carrying:

1. The honest band on "24" is **23–28**, not 24. `variant_axis` is adopted *provisionally* on 2 rows
   (`43` O10); `function_area` is flagged as possibly owed (`43` §7.3, three `government` rows mapped to
   `org_unit` as *"the least-wrong option"*); three more are named and held. Move the 2-domain adoption bar
   by one row and the count moves.
2. **`37` and `40-HANDOFF` say "16 of 23 schemas declare zero fields". It is 17.** `37`'s own §1.3 table
   lists 17 names and `41` says 17 — so `37` contradicts itself and `40-HANDOFF` propagates the wrong half.
   See §2 item 5.

---

## 2. Task B — every other instance

Numbered, with the population each was computed over.

| # | Doc | Claim | Real population / real value | Verdict |
|---:|---|---|---|---|
| 1 | `37` §2.1 | `issuing_org` … "Rows **11**" | `institution` appears in **13** of the 54 bound rows | **WRONG** |
| 2 | `37` §2.1 | `addressed_org` … "Rows **8**" | `target_university` (4) + `venue` (2) = **6** rows | **WRONG** |
| 3 | `37` §3.0 | `issuing_org → artifact_kind` "**11 for / 1 against**, n=12" | **12 for / 1 against, n=13** | **WRONG** |
| 4 | `37` §3; `41` §7.5 | "54 rows collapse to **31** distinct role sequences" / "24 templates instead of 31" | **32** distinct role sequences | **WRONG** |
| 5 | `37` exec §4, §6 B1; `40-HANDOFF` §6 | "**16** of 23 schemas declare zero fields" | **17**. `37`'s own §1.3 table lists 17; `41` §8 says 17 | **WRONG** |
| 6 | `37` §7.1 | "a **13**-role vocabulary" | its own §2.1 table has 14 rows; with the `container` merge rejected it is **15**, which is what `41` §2.3 publishes | **WRONG** |
| 7 | `40-HANDOFF` §6 | "not finishing the remaining **~66** research rows" | `37` §1.1 counted **46** owed at its snapshot; **25** at mine. No document supports 66 | **WRONG** |
| 8 | `40-HANDOFF` §7; `39` §1 | "**17 basenames** collide across the ten `src/` packages" | **16** at `b7c6e8f` (`__init__`, `schema`, `vocabulary`, `authorship`, `stage_output`, `store`, `fixtures`, `learning`, `budgets`, `events`, `supersede`, `replay`, `run`, `runs`, `dossier`, `records`) | **WRONG** |
| 9 | `41` §3 | "**there is no fourth**" | computed over the 54 bound rows; `42` §8 item 2 states plainly that it "is false at full corpus" | **OVERSTATED** |
| 10 | `42` §0 | "Recipe 1 … **Zero counter-examples in 270 rows**" | 14 rows are machine-derived; for the other 216 the absence of a counter-example is absence *in the coder's own transcription*. The §2 table splits F/P; the §0 headline does not | **OVERSTATED** |
| 11 | `43` §8 | "**Two independent readings** agreeing within ~5% … the prose layer is **reproducible enough to cut recipes on**" | `43` adopts `42`'s nine role names verbatim, its definitions in substance, and cross-references its four judgement calls (`43` O7 = *"42's judgement call 3"*). A shared codebook makes the two coders correlated; agreement measures **codebook stability**, not reproducibility. No blind re-code is reported | **OVERSTATED** — see §6 |
| 12 | `43` §4.2 | section header "**FREEZE NOW** — 11 pairs" | `43` §9 O3 simultaneously records as OPEN: *"Do prose-derived orders bind at all …? **8 of the 11** freeze-now recipes are prose-only, including the largest."* The table's "Carried by: PROSE ONLY" column is scoped; the section verb is not | **OVERSTATED** |
| 13 | `43` §5.1 | "Are all four genuinely distinct? Yes — **and each has row evidence**" | The `issuing_org` cell quotes `manufacturing.field-service-report` on `site` and `client`, then admits *"The row reaches for `client`, not for the issuer"*. `42` §6.1 uses the same quote as `counterparty_org` evidence. That cell carries no evidence for `issuing_org` | **OVERSTATED** (conclusion independently true) |
| 14 | `43` §0 | "of which 4 have zero counter-examples … and **2 are field-backed**" | **3** of the 11 have a field-derived half (#2 14/3, #3 4/2, #6 4/2). "2" is true only of the 4-clean subset | **OVERSTATED** (understated — see §5) |
| 15 | `39` verdict table (P3) | "the strongest work in the repository — **zero silent guards**" | **10** hand-picked invariant deletions against a 1,708-line package. §6's own header is scoped ("10 of 10 sabotages caught"); the verdict line is not. §1 concedes mechanical coverage exists for one part only, which makes the unqualified form worse | **OVERSTATED** |
| 16 | `39` verdict table (P6) | "**Every guard fired**" | **9** sabotages against a 5,624-line package | **OVERSTATED** |
| 17 | `39` §Seams inv. 2 | "**No part writes another part's table** … All ~150 write statements land in the owning package" | Probe = SQL **in literal strings**. At `b7c6e8f`, `src/facts/supersede.py:174,176` build `UPDATE {FACT_TABLE} …` as f-strings and `src/eval_harness/bundle.py:418,497` concatenate. Whether the walk captured `JoinedStr`/`BinOp` is not stated. An absolute ("no part") resting on an approximate ("~150") | **OVERSTATED** |
| 18 | `39` §Seams | "**306 direct cross-part call sites in `src/`, none of which would raise**" | `inspect.signature().bind()` proves no *binding* TypeError, not that a call cannot raise. The adjacent claim is correctly scoped by contrast: "48 of 48 `Callable` seams **with a declared arity** match their invocation" | **OVERSTATED** |
| 19 | `39` §7 (1471) | "P11 uses `FrozenTree`/`FrozenNode` **21 times**" | `38` §1 obtained it with `grep -c`, which counts matching **lines**. The zero side is exact, so the conclusion (no vocabulary overlap) is unaffected | **OVERSTATED** (harmless) |
| 20 | `40-HANDOFF` §3 | "**207 upstream imports resolve, 0 missing. 39 record constructions bound, 0 real defects**", per `scratchpad/verify_plans.py`, `verify_ctors.py` | There is **no `scratchpad/` directory** in the repo at my write time. The reproduction path is dead | **UNCHECKABLE** — re-running the two scripts would settle it; they do not exist |

### 2.1 Claims I checked and found SOUND — the positive control

These are listed because an audit that reports only failures is itself a biased sample.

- **The census.** 333 complete / 270 kept template rows across 23 schemas / **54 bound** across 6 /
  216 prose across 17. Reproduces `42` §1.1 and `43` §1.1 exactly, eight hours later.
- **`41`'s zero-violation check.** Folder levels with no declared field on their own schema: **0**. Levels
  declared but not `destination_eligible`: **0**. Both reproduced.
- **The 22 tokens.** 22 distinct dimension tokens across the 54 bound rows, **0 unmapped** by the published
  15-role map. Every role count in `41` §2.3 (`artifact_kind` 40, `subject_anchor` 17, `issuing_org` 13,
  `holder_institution` 8, `cycle_period` 8, `capture_time` 8, `addressed_org` 6, `occasion_anchor` 6,
  `account_kind` 5, `lifecycle_stage` 4, `capture_kind` 3, `scope_period` 2, `purpose_anchor` 1, `place` 1,
  `repository_instance` 1) is exact. *(This is where `37` §2.1's 11 and 8 were silently repaired — item 1–2.)*
- **24 definitions / 54 bindings.** `37` §5.1's table sums to exactly 54 and every per-definition row
  assignment is reconstructible from `dimension_order` alone. Per schema: finance 18, academic 11,
  photos 9, research 8, applications 5, code 3.
- **`frag.subject-then-artifact`.** 14 rows / 3 schemas, 14 for / 0 against adjacent *and* at any distance.
  Four definitions import it (10 + 1 + 2 + 1 = 14), which is `41` §5's stated reason the fragment reaches
  14 rows while its biggest definition reaches 10.
- **The launch set is closed.** `37` §1.1's strongest claim — *"no owed row can ever add a live dimension"* —
  **still holds at my write time**: 25 rows owed, distributed `law_practice` 7, `manufacturing` 5,
  `retail_hospitality` 5, `logistics` 4, `nonprofit` 3, `creative` 1, and **zero** on the six launch schemas.
- **`41` §4.1's P10 citations.** Lines 3702, 3685, 3737 of the P10 plan still resolve to
  `class TemplateDefinition`, `class TemplateDimension` and the `order_index` uniqueness check, in both
  `docs/superpowers/plans/…` and `planning/parts/P10-…/PLAN.md` (same 12,305-line file).
- **`39`'s egress evidence.** At `b7c6e8f`, `git grep "\.invoke("` returns **exactly one** line,
  `src/llm_harness/transport.py:178`, and `git grep "def invoke"` is empty; **no** network library
  (`requests`, `httpx`, `urllib`, `http`, `socket`, `anthropic`, `openai`, `aiohttp`) is imported anywhere
  in `src/`. My first probe of the *working tree* returned two lines — because a build agent has since
  edited `src/privacy/transport_guard.py`. **The audit's quote was correct at the commit it named.**
- **`43` §5.3 R4.** The narrowing from "single-domain role" to "single-domain pair" is exactly right:
  `career.credentials-licenses` — *"the ISSUING AUTHORITY first, then the CREDENTIAL, then the DOCUMENT
  TYPE"*; `engineering.standards-library` — *"issuing_body -> standard_designation"*.

---

## 3. Task C — the standing recommendations

| Recommendation | Verdict | What it should say instead |
|---|---|---|
| **"3 fragments, 24 definitions, 54 bindings" as the launch set** | **SOUND** | Nothing. Reproduced exactly; every binding traces to a declared, destination-eligible field on its own schema; the set is closed against future research. This is the best-evidenced conclusion in the whole chain. |
| **"11 pairs safe to freeze, 6 to hold, 2 contested"** | **OVERSTATED** | "3 pairs safe to freeze **on bindable evidence**; 8 more safe to freeze **conditional on R1c admitting prose-derived orders**, which `43` O3 records as open; 6 to hold; 2 contested." The 8 cannot be frozen and held-open at the same time. |
| **"all four org roles survive as distinct"** | conclusion **SOUND**, evidence **OVERSTATED** | Drop the "each has row evidence" claim for `issuing_org` (item 13) and lead with the argument that actually carries it, which is `43`'s own: *`holder_institution > subject_anchor` already reaches 5 domains unaided, so the merge adds one domain and destroys a distinction 00 forbids losing.* That argument needs no per-role quotation. |
| **"zero of the 54 bound rows uses any new role" → "nothing changes for launch"** | **SOUND** | Confirmed mechanically by me: all 22 tokens map to the original 15 roles; unmapped 0. One unstated dependency: the thing that makes Recipe 2 an *11-row* recipe is widening `holder_institution` to cover the holder's own **organisation** (`our_firm`-shaped, `destination_eligible: false`). If that widening is ratified, `frag.holder-affiliation-prefix@1.0.0` changes meaning and needs a version bump. Nothing *shipped* changes; the fragment's semantics might. |
| **"launch on the 6 field-declaring schemas; the other 17 are wave 2"** | **SOUND** | Nothing — except that `37` and `40-HANDOFF` say **16**, and that is the number a reader of the handoff will carry away (item 5). |
| **"roles grow sub-linearly while fields grow linearly"** | **not evidenced** | §4. |

---

## 4. The sub-linear claim, scrutinised

The claim appears in **no document** — `grep -rn "sub-linear\|sublinear\|linearly" planning/ docs/` returns
nothing. It was asserted in conversation. That is itself part of the finding: it is the least-checkable
statement in the chain and it was delivered with the most confidence.

The two data points are: **15 roles at 6 domains / 54 rows**, and **24 roles at 23 domains / 256 rows**.
Domains ×3.83, rows ×4.74, roles ×1.60; roles-per-domain 2.50 → 1.04.

Five reasons that is not a rate:

1. **The two points were produced by different instruments.** The 15 is *capped by construction*: the six
   schemas declare 28 distinct field keys, 22 destination-eligible, and only 22 tokens are used as
   dimensions. You cannot extract more than 22 roles from 22 tokens, and 15 is 22 collapsed by merging.
   The 24 is capped by one reader's adoption bar applied to prose. A mechanically-capped count and a
   judgment-capped count are not two samples of one process.
2. **The second point is not closed.** 25 rows are still owed. `43` names 3 roles adopted-not-named,
   1 provisional at 2 rows, and 1 possibly owed. The honest band is **23–28** — a ±4 on a 24, against a
   ×3.83 change in domains. No rate survives that.
3. **Two points cannot separate sub-linear from linear.** `roles = 12.6 + 0.49·domains` passes through both
   points exactly and is linear; so does `roles = 15·(domains/6)^0.34`. There is no third point and there
   can be no third point: 23 domains **is the whole roster**.
4. **At the margin the mechanism runs the other way.** All 9 new roles came from the 17 field-less schemas,
   and **77 distinct `proposed_fields` keys** already sit across the corpus. Every merge tested has been
   refused — all four org roles, `matter`≠`subject`, `component`≠`subject`, `place`≠`site`,
   `account_kind`≠`repository_instance`, `capture_kind`≠`artifact_kind`. A vocabulary that has refused
   every proposed merge is not obviously one that is saturating.
5. **`43` §9 makes the growth rate a policy, not a measurement.** It requires `allowed_vocabulary` to carry
   canonical roles *plus template-local dimension names*, and requires promotion to canonical to be *"a
   human-reviewed pass, never automatic and never a model's decision."* Under that rule the canonical role
   count grows at whatever rate a human promotes. "Roles grow sub-linearly" then becomes true by
   construction and carries no information about what the product can organize — which is exactly the
   reassurance it was offered as.

**The "fields grow linearly" half is loosely supported and should be kept:** 28 distinct keys across
6 schemas ≈ 4.7 per schema; **77** distinct *proposed* keys already sit across the other 17 ≈ 4.5 per
schema. That is close to linear on real data.

**Verdict: UNCHECKABLE as a rate; the roles half is not evidenced. What is defensible:** *"Roles went 15 → 24
while domains went 6 → 23. Whether that is a rate or an artefact of two different counting methods cannot be
determined from this corpus — there are only two points, the second is bar-dependent to ±4, and the design
deliberately makes further growth a human-review decision rather than a corpus property."*

---

## 5. Task D — under-confidence

Three real instances. The first is the costly one.

1. **`40-HANDOFF` §6 — "Templates — do not start building yet."** The stated reason is that
   *"16 of 23 schemas declare zero fields, so 199 of 253 kept rows carry `dimension_order: []` and cannot
   express a folder dimension at all"*, and *"All three of the handoff's hypothesized reuse shapes are
   unsupported by the corpus."* Both facts are about the **199**. The same session's `37` had already
   produced a launch set — 3 fragments, 24 definitions, 54 bindings — that I have verified is complete,
   internally consistent, fully field-backed and **closed against future research**. A property of the 199
   was applied to the 54. This is the Recipe 2 error run backwards, and it costs a wave of work rather than
   a recipe.
2. **`43` §0 — "2 are field-backed."** Three of the eleven are (#2, #3, #6). The stronger, true statement
   was available.
3. **`41` §3 — "research and code use literally the same two underlying fields, so you could argue it spans
   two domains, not three — still passes, but by less than it looks."** The bar the brief itself states is
   *domains*, not fields; and `academic`'s pair (`subject`/`work_type`) is disjoint from research/code's
   (`project`/`artifact_type`), so on purely mechanical evidence Recipe 1 already spans 3 schemas and 2
   disjoint field pairs. The hedge was unnecessary, and `42` §3.1 then spent a paragraph "dissolving" it on
   *prose* evidence that was never required.

**The template for a correctly-confident claim is `37` §1.1**, which proves the 54-row base is closed by
showing the owed rows all sit on zero-field schemas — a strong claim, stated strongly, and still true
eight hours later. That is the standard the rest should be held to.

---

## 6. The single claim to stop relying on

> `43` §8: *"**Two independent readings agreeing within ~5% on a 216-row manual pass is the useful result
> here** — it means the prose layer is reproducible enough to cut recipes on, which was not previously
> known."*

This is the load-bearing sentence of the whole chain. Everything prose-derived — the fourth recipe, the
nine new roles, the eleven freezable pairs, and the reversal of "cut Recipe 2" — is admitted as evidence on
its authority.

The two readings were not independent in the sense the claim needs. `43` adopts `42`'s nine role names
verbatim, its role definitions in substance, and cross-references its judgement calls by number
(`43` O7: *"= 42's judgement call 3"*; O1: *"= 42's F2"*; O2: *"= 42's F3"*; O3: *"= 42's F4"*). Two coders
applying one codebook to one corpus will agree; what their agreement measures is that **the codebook is
stable**, not that the coding decision is reproducible. Nothing in either document reports a blind re-code —
a second pass with the role list withheld — which is the only design that would support the conclusion drawn.

The ~5% agreement is a real and useful result about codebook stability. It is not a licence to treat 216
hand-assigned sequences as interchangeable with 54 machine-derived ones. **Recommendation: keep the prose
layer as corroboration and as a wave-2 map — which is exactly what `43` §6 concludes — and stop citing §8
as the reason a prose-only pair may be frozen.**

---

## 7. What I could not check, and what would settle it

| | Item | What would settle it |
|---|---|---|
| U1 | The role sequence assigned to each of the 216 prose rows. It is a human reading and the assignment table (`prose_seqs.py`) is not in the repo — `scratchpad/` does not exist. | Commit the assignment table next to the document, one row per node id, so a third party can diff it. Without it, every prose-derived number in `42` and `43` is unauditable in principle, not just in practice. |
| U2 | `40-HANDOFF` §3's "207 upstream imports resolve, 0 missing. 39 record constructions bound, 0 real defects". | The scripts named (`scratchpad/verify_plans.py`, `verify_ctors.py`) are gone. Re-write and commit them, or drop the numbers. |
| U3 | "3621 passed". | The working tree is dirty (`src/database_agent/events.py`, eight `src/extractors/*`, `src/privacy/transport_guard.py` and more are modified by concurrent agents). Re-running now would measure a different tree. Re-run from a clean `git archive` of the commit under test. |
| U4 | `39`'s "no test reaches this" claims for eight of nine parts. | `39` §1 already declares this limit honestly (`pytest-cov` absent; only P9 has a real tracer). Install coverage, or keep the limit stated wherever the claims are used. |
| U5 | Whether `holder_institution` may cover the holder's own **organisation** at all. | A canonical decision on `our_firm` (`destination_eligible: false`) and on the proposed `organization` / `employer` keys. This is what actually decides how big Recipe 2 is — §1.1. |

---

## Appendix — reproduction

```bash
cd "/Users/jy/GRAPH AGENT"

# census + the 54 bound rows + role map + every pair count in this document
python3 - <<'PY'
import json, os, collections
N='planning/domains/nodes/'; r=json.load(open('planning/domains/roster.json'))
f=set(os.listdir(N))
rows=[json.load(open(N+n['domain_id']+'.json')) for n in r['nodes']
      if n['domain_id']+'.json' in f and n['domain_id']+'.research.md' in f]
kept=[d for d in rows if d['kind']=='template' and not d.get('refuse_node')]
bound=[d for d in kept if d['template'].get('dimension_order')]
print('complete',len(rows),'kept',len(kept),'bound',len(bound),
      'schemas',len({d['schema_id'] for d in bound}))
M={'work_type':'artifact_kind','artifact_type':'artifact_kind','record_type':'artifact_kind',
'application_document_type':'artifact_kind','project':'subject_anchor','subject':'subject_anchor',
'institution':'issuing_org','target_university':'addressed_org','venue':'addressed_org',
'term':'cycle_period','application_cycle':'cycle_period','school':'holder_institution',
'lab':'holder_institution','capture_year':'capture_time','event':'occasion_anchor',
'account_type':'account_kind','repository':'repository_instance','stage':'lifecycle_stage',
'media_type':'capture_kind','tax_year':'scope_period','purpose':'purpose_anchor','location':'place'}
S={d['id']:(d['schema_id'],[M[t] for t in d['template']['dimension_order']]) for d in bound}
print('role uses:', collections.Counter(x for _,q in S.values() for x in q))
print('distinct sequences:', len({tuple(q) for _,q in S.values()}))
def pair(a,b):
    adj=[(i,s) for i,(s,q) in S.items() for k in range(len(q)-1) if q[k]==a and q[k+1]==b]
    rev=[i for i,(s,q) in S.items() if a in q and b in q and q.index(b)<q.index(a)]
    return len(adj), len({s for _,s in adj}), len(rev)
for p in [('subject_anchor','artifact_kind'),('holder_institution','subject_anchor'),
          ('cycle_period','artifact_kind'),('issuing_org','artifact_kind')]:
    print(p, 'adj rows/dom, rel-reverse =', pair(*p))
PY

# 6 of 23 declare fields; 28 distinct keys, 22 destination-eligible
python3 - <<'PY'
import json, collections
N='planning/domains/nodes/'; r=json.load(open('planning/domains/roster.json'))
keys=collections.defaultdict(set); dest=set(); n=0
for s in [x['domain_id'] for x in r['nodes'] if x['kind']=='schema']:
    fl=json.load(open(N+s+'.json')).get('fields') or []
    if fl: n+=1
    for x in fl:
        keys[x['field']].add(s)
        if x['destination_eligible']: dest.add(x['field'])
print('schemas with fields', n, '| distinct keys', len(keys), '| dest-eligible keys', len(dest))
PY

# the launch set is closed: zero owed rows on the six field-declaring schemas
python3 -c "
import json,os
r=json.load(open('planning/domains/roster.json')); f=set(os.listdir('planning/domains/nodes/'))
six={'academic','code','college_applications','finance','photos','research'}
owed=[n for n in r['nodes'] if not (n['domain_id']+'.json' in f and n['domain_id']+'.research.md' in f)]
print(len(owed),'owed;', [n['domain_id'] for n in owed if n.get('schema_id') in six],'on the six')"

# src/ claims must be read at the audited commit, not the working tree
git grep -n "\.invoke(" b7c6e8f -- src/
git ls-tree -r --name-only b7c6e8f src/ | python3 -c "
import sys,collections,os
d=collections.defaultdict(set)
for l in sys.stdin:
    p=l.strip().split('/')
    if len(p)>=3: d[os.path.basename(l.strip())].add(p[1])
print('colliding basenames:', len({k for k,v in d.items() if len(v)>1}))"
```
