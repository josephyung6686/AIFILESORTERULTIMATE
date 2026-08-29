# Audit — multi-value facts, overrides and conflicts

Read-only diagnostic. Nothing under `src/` or `tests/` was changed. Every claim below
was produced by running code, not by reading a SPEC. The three throwaway probes live
in the session scratchpad (`.../scratchpad/probe_multivalue.py`,
`probe_placement.py`, `probe_agree.py`) and one end-to-end run of the shipped CLI
wrote `.../scratchpad/plan.sqlite`.

---

## Verdict

**Partly mitigated, and the unprotected part is worse than the critique describes.**

The imported failure — "the renderer files the document under both Georgetown and
WashU simultaneously" — **does not happen here**. Three separate downstream readers
refuse to choose between two live values rather than honouring both, so no file is
ever written into two folders and no file is ever placed twice.

What is unprotected is the other side of the same missing constraint:

1. `file_facts` has no uniqueness constraint on `(file_id, content_hash, field_key)`
   and **the shipped CLI produces violations of it on ordinary input, today, with no
   LLM, no user and no override path involved** (§2). Proven on a real run.
2. The one reader that resolves the slot, `preferred_fact`
   (`src/facts/supersede.py:180-209`), counts **rows**, not **distinct values**. So it
   returns `None` — "unresolvable" — for three situations that are not alike: two
   contradictory values, one strong value plus one deliberately-excluded weak clue,
   and **two facts that agree on the same value**. The third is the worst case in this
   audit (§7, F1). Agreement between the product's own two producers deletes the
   file's folder level.
3. The `preferred` column is **inert in production**: `supersede_fact`, its only
   writer, has zero callers in `src/` (§4). Nothing ever supersedes a file fact,
   so the one column that could distinguish an override from a multi-relationship
   is always NULL on real data. Verified against both plan databases: 0 non-null.
4. Nothing anywhere distinguishes case (a) "genuinely multi-valued" from case (c)
   "conflict". `fields.multiplicity` exists, is the declared home for that answer, and
   is `NULL` on all 56 catalogue rows (§6).

The override half of the critique is currently **not reachable**: no module in `src/`
writes a fact with origin `user_correction` or `user_approved_folder`, or with state
`user_confirmed`, so a user cannot override a fact at all yet. That is why this is
"partly mitigated" rather than "live defect": the schema hole is real and open, and
the traffic that would exploit it hardest has not been built.

---

## 1. Method

- P6 writers used directly (`facts.file_facts.write_fact`, `facts.values.ensure_value`),
  never raw SQL, so every result is what production would produce.
- Downstream reads called on the resulting database: `facts.read_surface`,
  `facts.supersede`, `tree_design.upstream`, `grouping.seeds`, `grouping.pipeline`,
  `placement.retrieval`, `placement.scoring`.
- One full run of the shipped CLI (`python3 -m cli <dir> --situation
  academic.coursework --label Coursework`) over a four-file corpus, one of whose files
  mentions two course codes.
- `python3` throughout; there is no `python` on PATH.

---

## 2. Q1 — Can one file version hold two active, unsuperseded facts for one field?

**Yes, and nothing refuses.**

`FILE_FACTS_DDL` (`src/facts/schema.py:117-145`) declares `fact_id` PRIMARY KEY, three
non-unique indexes (`:139-141`) and no `UNIQUE` clause of any kind. The identity that
governs idempotency is content-addressed over the whole conclusion —
`_fact_identity` (`src/facts/file_facts.py:163-170`) hashes `file_id, content_hash,
field_key, value_id, reliability_state, origin, cache_key, evidence_refs`. Change any
one of those and you get a second row at the same slot. `value_id` is in that tuple,
so two values are two rows by construction.

Probe 1 (`probe_multivalue.py`) wrote two `direct` facts for `institution` on one file
version through `write_fact`:

```
write_fact accepted BOTH.
  field_key='institution' value='Georgetown University'  state=direct active=1 superseded_by=None preferred=None
  field_key='institution' value='Washington University…' state=direct active=1 superseded_by=None preferred=None
```

**This is not a synthetic case.** The shipped CLI's only direct slot
(`src/cli.py:206-212`) maps every structured identifier found in `body#*` or
`heading*` to `subject`, and `direct_facts` writes one fact per distinct
`(field_key, canonical_value)` (`src/facts/direct.py:136`, `:140`, `:147`). A file that
names two course codes therefore produces two `subject` facts. Running the real CLI
over a corpus containing `Lab report.txt` ("PHYS 1401 Lab Report / Submitted for
BUSIB 4300 as well"):

```
file_facts: 11
  ('Lab report.txt', 'subject', 'BUSIB4300', 'direct', active=1, superseded_by=None, preferred=None)
  ('Lab report.txt', 'subject', 'PHYS1401',  'direct', active=1, superseded_by=None, preferred=None)
slots with >1 active unsuperseded fact:  ('c9c91cc6-…', 'subject', 2)
preferred non-null: 0
```

`src/facts/rules.py:155-167` has the same shape: one `validated` fact per matching
observation, so a rule matching twice with different captures writes two values too.
That stage is `None` in this deployment (`src/cli.py:324`) but is a supported route.

---

## 3. Q2 — What do the downstream parts do with it?

### 3.1 Tree design — safe, and it is deliberate

`materialise_branch` asks `preferred_value_for` per member per level
(`src/tree_design/materialise.py:212-217`); a `None` puts the file in `missing`, which
becomes `BranchEvidence.unresolved_by_field`. `preferred_value_for`
(`src/tree_design/upstream.py:365-399`) delegates to `preferred_fact`, which returns
`None` when the slot has more than one live row (`src/facts/supersede.py:201-209`).

Measured on the real CLI database:

```
Syllabus one.txt -> FieldValue(subject='PHYS1401')
Homework two.txt -> FieldValue(subject='PHYS1401')
Case study.txt   -> FieldValue(subject='BUSIB4300')
Lab report.txt   -> None                     <-- the two-value file
```

So the file gets **no branch at that level** — not two branches. `values_with_counts`
does count both values (`Georgetown 1`, `WashU 1` in probe 1), so the branch **preview**
promises the user two folders that this file will then not appear in; the preview and
the materialiser disagree. That is a reporting inconsistency, not a double-filing.

The repo already knows this: `tests/p10/test_p10_materialise.py:129` and
`tests/integration/test_ambiguity_cases.py:522` both assert exactly this behaviour and
name it correct-but-incomplete.

### 3.2 Placement — safe when the evidence is symmetric, **not safe when it is not**

`reachable_entries` treats `pairs` as a set of `(field, value)`, and suppression is
`if (field, value) in pairs: continue` (`src/placement/index.py:385`). With both values
held, **neither node contradicts the file**, so both become `direct_fact` candidates and
`conflicts_considered` is empty. Probe 2, driving the real `retrieve`/`assess` over the
§6.9 application tree:

```
(a) two live values, symmetric evidence
    n-columbia (direct_fact) 0.4286
    n-duke     (direct_fact) 0.4286
    verdict=weak  meets_margin=false  reason=multiple_supported_homes  requires_review=True
    conflicts recorded: []

(b) two live values, the Duke node ALSO reached by an accepted group
    n-duke     (direct_fact, accepted_group) 0.7143
    n-columbia (direct_fact)                 0.4286
    verdict=accept_context_supported  meets_margin=true  margin=0.286  reason=None  requires_review=True
    conflicts recorded: []
```

Case (a) is the good outcome the design intends: `multiple_supported_homes`
(`src/placement/scoring.py:110`) and the honest sentence at
`src/placement/pipeline.py:555-561`. **Case (b) is the hole.** The tie is only a tie
while the two values have identical channel sets. One extra channel on either side —
an accepted group, a graph relationship, a structural relationship — breaks it, the
margin clears, and P11 returns `PLACE` at **one** of two contradictory values with no
abstention and **no conflict record at all**. `requires_review=True` keeps it out of
`AUTO_ELIGIBLE` (`src/placement/records.py:461-465`), so a human still sees it — but
what they see is a single confident destination, with nothing on the screen saying the
file also claims a different one.

Two further placement issues found on the way:

- `src/placement/retrieval.py:119` — `held = next(fact for fact in usable if fact.field
  == field)` picks the **first** fact for a field when attributing suppression counts.
  With two values held, the whole suppressed count is attributed to whichever value
  sorted first, so `ConflictConsidered.conflicting_value` names a value that may not be
  the one that did the suppressing.
- `src/cli.py:685-703` — `evidence_for` selects `WHERE ff.file_id = ? AND ff.active = 1
  AND ff.superseded_by IS NULL` with **no `content_hash` filter**, so facts from an
  earlier version of an edited file join the current set and become extra values for
  one field. It also hard-codes `reliability=pv.DIRECT` (`:700`) for every row
  regardless of the row's real `reliability_state`, so a `possible` fact would reach
  P11 wearing `direct`. Both are CLI-layer defects, not P11's.

---

## 4. Q3 — Is `preferred` inert?

**Writers in `src/`:** exactly two statements, both inside `supersede_fact` —
`src/facts/supersede.py:174` (`SET preferred = 0`) and `:176` (`SET preferred = 1`).
`write_fact` inserts the literal `NULL` (`src/facts/file_facts.py:280`), and its
docstring says so at `src/facts/file_facts.py:34`: "This module does not set
`preferred` (Task 18)".

**Readers in `src/`:** exactly one — `src/facts/supersede.py:208`,
`pointed = [row for row in live if row["preferred"]]`.

**Callers of `supersede_fact` in `src/`: none.** `grep -rn "supersede_fact" src/`
returns only its own definition (`:145`) and one comment (`:227`). Every caller is in
`tests/`. Confirmed against data: both real plan databases hold `preferred IS NOT NULL
= 0` and `superseded_by IS NOT NULL = 0`.

**The decision that is therefore unmade.** `preferred_fact`'s third case — "among
several live rows, exactly one carrying `preferred` is the pointer"
(`src/facts/supersede.py:190`) — is unreachable in production. The only escape from a
multi-row slot is the `user_confirmed` case (`:203-205`), and nothing in `src/` writes
a `user_confirmed` file fact either (the `USER_CONFIRMED` at
`src/privacy/learning_seam.py:254` is a P7 classification in a different table). So on
real data `preferred_fact` has exactly two outcomes: **one row → that row**, or
**more than one row → `None`**. There is no mechanism by which any producer, resolver
or user says "this one, not that one". The resolver (`src/facts/resolver.py`) sequences
producers and never compares their conclusions; no §3.6 contradiction check over two
stored facts exists anywhere in `src/`.

---

## 5. Q4 — Which of the three cases can the schema tell apart?

| Case | Distinguishing column | Told apart today? |
|---|---|---|
| (b) one value supersedes the other | `supersedes` / `superseded_by` / `supersede_reason` (`src/facts/schema.py:134` via `supersede_ddl`) | **Structurally yes, practically no** — the columns exist and `mark_superseded` writes them, but nothing in `src/` ever calls the function that would. Always NULL on real data. |
| (a) a genuine multi-relationship | `fields.multiplicity` (`src/facts/schema.py:41`) | **No.** NULL on all 56 catalogue rows — `_row` hard-codes `multiplicity=None` (`src/facts/fields.py:121-126`), verified by query: `56 rows / 0 non-null`. |
| (c) two values that conflict | — none — | **No.** There is no conflict column, no conflict table, and no code path that writes one. |

So (a) and (c) are **structurally indistinguishable**, exactly as the imported critique
says. (b) is distinguishable in principle and indistinguishable in practice.

**But the product does not want (a) here.** `planning/66-FIND-FILE-AND-ONBOARDING.md`
§3 puts the legitimate multi-relationship in a different channel entirely. Its table
lists "Also related to" as "An accepted group, project, course, packet, event, or
other organizational relationship **that does not imply another physical copy**", and
its worked example is "A transcript may have one physical location in
`Applications/Shared Application Materials` and accepted relationships to more than one
university application packet" (`planning/66-FIND-FILE-AND-ONBOARDING.md:126`, `:135-137`).
The multi-purpose relationship the design protects is carried by **accepted groups and
the shared-material policy**, not by two values of one destination-eligible field.
A file holding two `institution` values is not the design's "also related to" case; it
is either a conflict or an unanswered OQ6. That narrows the fix: the schema does not
need to learn how to represent (a) at `file_facts`, it needs to stop conflating (c)
with "unresolvable".

---

## 6. Q5 — What does P9 do?

`_anchor_rows` (`src/grouping/seeds.py:133-147`) reads three P6 surfaces, filters to
`{direct, validated}`, and dedupes on `f"{row['field_key']}:{row['value_id']}"`
(`:146`). **That key is field-plus-value, so two different values for one field are two
distinct entries — it dedupes producers, never values.** Two active `subject` values
therefore produce two seeds:

```
seeds: [('subject', 'BUSIB4300'), ('subject', 'PHYS1401')]
```

`group_address` (`src/grouping/pipeline.py:224-260`) digests `(field_key, value)`, so
the two seeds address two different groups.

**But only one is ever used.** `group_subject` takes `seed = seeds[0]`
(`src/grouping/pipeline.py:405`) and `production._group_corpus` calls it once per file
(`src/production.py:540-550`). `_anchor_rows` returns `[seen[key] for key in
sorted(seen)]`, and `value_id` is a sha256, so **which of two conflicting values seeds
the file's group is decided by hash order** — deterministic, stable, and completely
unrelated to evidence strength, recency or count. On the real run, `Lab report.txt`
seeded `BUSIB4300` (`group:subject:54594e9f…`) because that value's id sorted first.

The effect on `group_address` is therefore not two groups but **one arbitrary group**.
One redeeming detail, measured: the PHYS1401 group's `anchor_count` is 7 on the real
run, which includes `Lab report.txt` — the file reaches the second group through the
neighbourhood graph rather than through its own seed. So it does end up related to
both, by a route nobody designed and nothing records as a relationship.

---

## 7. Findings, ranked

**F1 — HIGH — `preferred_fact` counts rows, not distinct values, so two facts that
AGREE erase the file's folder.** `src/facts/supersede.py:201-209`. Probe 3
(`probe_agree.py`) writes two facts for `subject`, both `PHYS 1401`, one `direct` from
the extractor and one `validated` from a rule, citing different observations — a legal
pair, since `_fact_identity` includes `reliability_state`, `origin` and
`evidence_refs`:

```
after 1 fact           -> FieldValue(subject='PHYS 1401')
after 2 AGREEING facts -> preferred_fact: None
                       -> preferred_value_for: None
```

The two producers §8.6 runs in order both concluded the same thing, and the product's
answer is "unresolvable". Not reachable through today's single-slot CLI, because
`direct_facts` collapses agreeing readings into one fact with several citations
(`src/facts/direct.py:104-107`, `:136-147`) — but it becomes reachable the moment the
`rule` or `llm` stage is enabled (`src/cli.py:324`), which is the whole point of
§8.6's degradation ladder. *Fix:* collapse `live` by `value_id` before counting; a
slot whose live rows all name one value has one answer.

**F2 — HIGH — no uniqueness constraint and no conflict record, so a real conflict is
reported as an evidence gap.** `src/facts/schema.py:117-145`. The user sees
"unresolved at this level" (P10) or "no destination cleared" (P11), never "this file
says two things". `planning/66` §4's rule that distinct causes may not share one
message is broken here by construction. *Fix:* either a `UNIQUE (file_id,
content_hash, field_key)` on fields whose `multiplicity` is single-valued, or an
explicit conflict record the review surface can read.

**F3 — HIGH — P11 can place at one of two contradictory values with no conflict
recorded.** `src/placement/index.py:385` + `src/placement/scoring.py:107-117`. Probe 2
case (b): `accept_context_supported`, margin 0.286 over a 0.2 threshold,
`abstention_reason=None`, `conflicts_considered=[]`. Review is required, so nothing
moves silently — but the reviewer is shown one destination and no sign of the other
claim. *Fix:* when a subject holds two values for one destination-eligible field, that
is a conflict at the subject, and it should reach `ConflictConsidered` before the
scoring runs.

**F4 — MEDIUM — `preferred` and `supersede_fact` are dead in production.**
`src/facts/supersede.py:145` has no `src/` caller; `preferred` is always NULL. The one
column designed to say "this value replaced that one" is unwritable by anything the
product ships. *Fix:* nothing to fix in P6 — the gap is that no producer, resolver or
review path calls it. This is the pre-condition for any user-override feature.

**F5 — MEDIUM — a single `possible` clue vetoes a `direct` fact.** Probe 1, §2b:

```
single direct subject fact                 -> FieldValue(subject='PHYS 1401')
after adding ONE `possible` subject fact   -> None
proposal_eligible subject rows             -> [('PHYS 1401', 'direct')]
```

`proposal_eligible` correctly drops the `possible` row (`src/facts/read_surface.py:166-169`),
but `preferred_fact` does not filter by state or by `active` at all — it says so
deliberately at `src/facts/supersede.py:197-199` ("`active` is a different axis"). So a
fact §3.6 explicitly says "must not quietly become a folder proposal" quietly destroys
one. A `rejected` or `active = 0` row does the same. *Fix:* `preferred_fact` should
restrict `live` to rows that could be an answer before it counts them.

**F6 — MEDIUM — the CLI's placement evidence read is unscoped and mislabels
reliability.** `src/cli.py:688-692` (no `content_hash` predicate — facts from a stale
version of an edited file join the live set) and `src/cli.py:700`
(`reliability=pv.DIRECT` hard-coded for every row).

**F7 — LOW — P9 picks the seed by hash order.** `src/grouping/pipeline.py:405` with
`src/grouping/seeds.py:147`. Deterministic but arbitrary; no record anywhere says the
other seed existed and was dropped.

**F8 — LOW — the branch preview and the materialiser disagree.**
`values_with_counts` (`src/facts/read_surface.py:183-219`) counts a two-value file
under both values; `materialise_branch` files it under neither. §5.5's "Option A would
create three schools" is therefore an over-count in exactly the cases this audit is
about.

---

## 8. What is not broken

Worth stating plainly, because the imported critique would predict otherwise:

- **No file is ever filed under two folders.** `preferred_value_for` returns `None`
  and `materialise_branch` records the file as unresolved at that level. Asserted in
  the suite at `tests/p10/test_p10_materialise.py:129`.
- **No file is ever placed twice.** One `group_subject` call per file, one placement
  decision per subject.
- **The symmetric two-homes case is handled well and honestly** — abstain with
  `multiple_supported_homes` and a sentence that tells the user it is their choice, not
  an evidence failure (`src/placement/pipeline.py:555-561`).
- **The refusal to pick is principled, not accidental.** Both `preferred_fact` and
  `preferred_value_for` document that choosing would close P6's OQ6 inside a reader.
  The defect is not that they refuse; it is that they refuse for three different
  reasons and say the same thing each time (F1, F5).
