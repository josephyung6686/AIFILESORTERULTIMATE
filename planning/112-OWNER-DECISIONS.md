# 112 — FOUR DECISIONS, RESEARCHED SO THEY CAN BE TAKEN IN ONE SITTING

19 September 2026. Written against `109-ACTION-PLAN.md`, `108-HANDOFF.md` §9 and
`00` amendment 24. Nothing in this document changes code.

**How to read this.** Amendment 24 draws the line this document is organised on: a
**PREFERENCE** is the person's and should be a setting, not a library ruling; a
**TRUTH** is a fact about the world the library must get right whoever runs it.
Each item says which it is *before* it gives the options, so a question that should
never have been asked can be closed with "make it a setting".

**Where the numbers come from.** Every count below was measured today, read-only,
against `~/.graph-agent/lead/corpus2-gate1/run12.sqlite` — the owner's cumulative
database, 371 files, last written 18 Sep. Grain is stated on every number.
`tools/groundtruth` was not run (only the lead runs it). No filename, folder name,
course code or key entry appears anywhere below; only counts, and the names of
library rules and fields, which are the library's own vocabulary.

**Four things measured here contradict the brief that asked for them.** They are
collected in the last section and flagged where they arise.

---

## 1. `work_type`'s glossary meaning

### PREFERENCE or TRUTH — already ruled, and it is a TRUTH

The owner settled this in amendment 24 itself, which lists *"that `work_type`'s
glossary entry describes no thing"* under **NOT a preference, and the library's to
get RIGHT**. So nothing about *whether* to fix it is owed. What is owed is the
TEXT, and text that goes to a model is the owner's alone by standing order. This
is a one-word decision, not a design question.

### The current text

`src/llm_harness/library/field_glossary.json`, `fields.work_type`:

```
meaning: "if the file IS the work product of a bounded engagement or course -> `work_type`"
source:  "facts.fields:record_type FIELD_ROWS notes, transcribed from `60`"
```

The source name is the diagnosis. It is `record_type`'s note, and `record_type`'s
own entry two keys away reads *"`record_type` is what remains: the file evidences
that a transaction, operation or decision occurred."* The `work_type` entry is the
**routing conditional that tells a router which of the two keys to use**. Read as
a definition it is circular — it tells a model that a work product is a work type
— and the fact template's own rule is *"propose only the thing that entry
describes"*. It describes a routing decision, so the honest response to it is to
decline, which is what happened 163 times.

### The proposed text, and it cannot be wired as written

From `d8dd85b1`'s message:

```
work_type.meaning: "what kind of coursework artifact this is; members are
values (syllabus, homework, lecture) discovered at runtime, never roster nodes"
source: planning/domains/canonical_fields.json fields[].role
```

**That exact string fails the gate.** `tests/p8/test_p8_field_glossary.py::
test_every_meaning_is_verbatim_from_its_cited_source` resolves a
`canonical_fields.json` citation with `how="equal"` — byte equality, not
substring (`_source_text`, line 221-224). The role string in the source
capitalises the word:

```
"what kind of coursework artifact this is; members are VALUES (syllabus,
homework, lecture) discovered at runtime, never roster nodes"
```

So the only transcription that can be wired is that one, verbatim, with
`source: "planning/domains/canonical_fields.json (fields[].role)"` — the same
citation shape `subject` and `term` already use.

### Judging it

It is a **definition** rather than a routing note, which is the whole of the
defect, and it is transcribed rather than authored, which is what the standing
order requires. That is enough to prefer it to what is there.

It is **not good prompt text**, and the owner should know that before saying yes.
The second half — *"members are VALUES … never roster nodes"* — is an instruction
to whoever authors a template about destination-eligibility. A model asked what a
document is does not need it and may read "never roster nodes" as a constraint on
its answer. The first clause alone would do the work.

That leaves two options and the difference between them is procedural:

| option | text | what it costs |
| --- | --- | --- |
| **(a) transcribe verbatim** | the role string above, unchanged | nothing; the gate test passes as-is, no new source needed |
| **(b) author a shorter sentence** | e.g. the first clause alone | needs a **new ratified source**, because the gate re-reads the citation and a clause that is not the whole role string is not `equal` to it |

Option (b) is not blocked — the owner can author the shorter sentence and it
becomes its own ratified text — but it is a bigger gesture than it looks, because
the citation machinery is what keeps the lead from writing prompt text.

### What measurably changes

Measured today, file grain, `run12.sqlite`:

```
files declining work_type with reason=model_returned_unknown      163   (332 rows)
files with an active work_type fact                                46
  ... of those, also carrying a decline row (a later pass answered) 30
files where the deterministic RULE abstained (no_candidate_evidence) 332
```

`108` §5's 163 is confirmed exactly, at file grain.

`work_type` is a **folder level in 48 of the 208 shipped situations and REQUIRED in
30**, including `academic.coursework` (`school`, `term`, `subject`, **`work_type`**),
`academic.teaching` and `career.recruiting`. It is the third most frequently bound
level in the whole release, after `project` (94) and `record_type` (64). So this is
not a search field; it is a folder that does not get built.

The 163 decliners, by the situation their own fact carries:

```
75  academic        <- academic.coursework / .teaching make work_type REQUIRED
18  career          <- career.recruiting makes work_type REQUIRED
14  research
51  no situation fact at all
 5  everything else (nonprofit 4, medical 1, creative 1, business 1, government 1)
```

**93 of the 163 sit under a kind whose canonical situations make `work_type` a
required folder level.** That is the stake: up to 93 files whose destination folder
cannot be built, on a field whose definition tells the model nothing.

### CONTRADICTION FOUND while measuring this

**Not one file in the corpus carries a situation id.** All 231 files with an active
`situation` fact hold a **bare kind** — `academic` (82), `research` (55),
`nonprofit` (37), `photos` (26), `career` (18), and eight more. Twelve of the
thirteen distinct values are not names in the shipped release at all; only
`nonprofit` happens to collide with one.

Two consequences, both of which outrank this item:

1. The join from a file to the folder levels its situation would build **cannot be
   made on this database for any field**, not just `work_type`. My first pass
   returned "0 of 163 sit in a work_type-binding situation", which is true and
   means nothing; the 93 above is measured at the kind grain instead and is the
   honest figure.
2. `108` §5 says the 97.7 % may not be re-claimed *"until the grader prefers the
   fact's own value where it is already a situation id"*. On this database the fact
   is never a situation id. `106` Phase 2(b)'s change has not reached any stored
   fact, and `109` A3's third point — that the grader reads site G's raw response
   and is untouched by Phase 2(b) — is the nearer description.

### Recommendation

**Take option (a): ratify the verbatim role string.** It is the smallest gesture
that closes a defect the owner has already classified as the library's to fix, it
needs no new source, and the gate test proves the transcription rather than
trusting it. Say the word and it is one line.

**Then measure before believing the 93.** The sanctioned path already exists:
`tools/promptbench/drafts/field_glossary.<field>.v2.json` with
`_status: {"status": "unratified", …}` — two such drafts are already on disk for
`school` and `subject`. Nothing is drafted here, because the text is the owner's.

---

## 2. The EXIF year question

### PREFERENCE or TRUTH — mostly a TRUTH, and the code calls it the wrong thing

`src/cli.py:4995` and `:5025` both record this as *"the floor is a threshold, and a
threshold is the owner's number."* A floor would indeed be a preference. **But the
thing being defended against is not a low year; it is a known default VALUE.** A
camera whose clock was never set writes `1970:01:01 00:00:00` — first of January,
midnight — not `1970:07:14 15:32:11`. The discriminator is the whole string.

That reclassifies the question. *"`1970:01:01 00:00:00` is not evidence of when a
picture was taken"* is a **TRUTH** and needs no number from the owner. *"No photo
older than 2001 is real in my library"* is a **PREFERENCE** and should be a
setting, not a library constant — and it is the only option here that throws away
real data.

### Where the pattern is used — two patterns, two fields, two blast radii

| site | pattern | writes | where it lands |
| --- | --- | --- | --- |
| `cli.py:4999` `_CAPTURE_YEAR` | `[12]\d{3}` anchored to EXIF `YYYY:MM:DD HH:MM:SS` | `capture_year` from `DateTimeOriginal` | the **first folder level** of 8 of the library's 10 photo situations, **required in 7** |
| `cli.py:5026` `_CALENDAR_YEAR` | `(?<!\d)[12]\d{3}(?!\d)` | `year`, derived from `creation_date` by `year_of` | bound as a folder level on Current work and Career applications (amendment 22) |

`_CAPTURE_YEAR` already refuses `0000:00:00 00:00:00` — the commonest unset-clock
string — because `0` is not `[12]`. The three the owner is being asked about are
the ones that slip past that same guard.

### Measured exposure on the owner's corpus: ZERO files

```
EXIF DateTimeOriginal observations                      3   on   3 files
  ... whose year is 1970 / 1980 / 2000                  0
  ... year histogram (observation grain)         2022 x2, 2023 x1
files with an active capture_year fact                  4   (2022 x2, 2023 x2)
  ... in 1970 / 1980 / 2000                             0

active creation_date facts                             47   on  47 files
  ... derived year histogram             2014 x1, 2022 x2, 2023 x1
  ... in 1970 / 1980 / 2000                             0
  ... outside 1990-2026                                 0
active `year` facts                                     0   (the producer postdates this database)
```

**Not one value in the corpus is a clock default, and not one is otherwise
implausible.** So the decision is free to take in the safe direction.

**And this corpus cannot decide the question**, which the owner should know before
reading the zero as reassurance. Only 20 of 371 files carry any EXIF-prefixed
metadata; only 3 carry a capture time; 33 files are jpeg/jpg/png. The
`image.metadata` reader produced 933 observations across 64 files and almost none
of them is a camera timestamp — these are screenshots, downloaded images and
graphics, not a photo library. The corpus where this matters is the one the product
has not met yet, and there `capture_year` is the TOP folder level.

### The options, with their costs

| | option | cost on this corpus | cost in general |
| --- | --- | --- | --- |
| **A** | Refuse the three **default strings** — `1970:01:01 00:00:00`, `1980:01:01 00:00:00`, `2000:01:01 00:00:00` — and nothing else | **0 files** | a genuine photograph taken at exactly midnight on 1 January of one of those three years |
| **B** | Accept those three years only with **corroboration** (a filesystem timestamp in the same year, a year in the file's own name, a sibling photo's capture year) | 0 files | needs a corroborating fact that does not exist yet; nothing to build against today |
| **C** | Accept them as they stand | 0 files | a photo library silently grows a `1970` folder at the **top** level of 7 photo situations, which is where the wrongness is most visible and hardest to explain |
| **D** | A year floor (the owner's number) | 0 files | throws away every real photograph before the floor, permanently, with no way for the person to tell |

### Recommendation

**A, and it needs no number from the owner.** It is fail-closed on exactly the
values that are known lies and costs nothing measurable. **B is the better second
step** once a corroborating fact exists — and it is the shape the owner already
ratified elsewhere: amendment 1 of 13 Sep turned "holds the file" into
"corroborates" for exactly this reason.

**D is the only preference here**, and if the owner wants a floor it should be a
setting the person can change — amendment 24's own point — not a constant in
`cli.py`.

### A BIGGER DEFECT FOUND WHILE MEASURING THIS, not asked for

**`year_of` refuses 43 of the 47 active `creation_date` facts, and the year floor
has nothing to do with it.** Masked value shapes (every digit shown as `9`, every
letter as `a`, so nothing is readable):

```
18  years=0  a:99999999999999+99'99'
17  years=0  a:99999999999999-99'99'
 5  years=0  a:99999999999999a99'99'
 2  years=0  a:99999999999999a
 1  years=0  a:99999999999999
 3  years=1  aaa 99, 9999
 1  years=1  99 aaaaaaaa 9999
```

Forty-three of the forty-seven are **PDF `D:` timestamps**, and
`_CALENDAR_YEAR`'s `(?<!\d)…(?!\d)` guard cannot see a year inside
`20240115143000` — the digits are in a longer run, which is exactly what that
guard exists to reject. So amendment 22's `year` folder level would be **blank on
roughly 91 % of the files that have a creation_date**, and the cause is a date
FORMAT the pattern does not parse, not a floor.

This is TRUTH-shaped, needs no owner input, and is worth more than the year floor.
It is named here and not built, because this document changes no code.

---

## 3. The 25 over-protected files — DIAGNOSIS ONLY

**No code was changed and none is proposed as a fix. This is the escalation.**
Every option below widens what leaves the device, which is the gated class.

### PREFERENCE or TRUTH — three separate things, and only one is open

* *"Medical records reach no model"* — **TRUTH**, settled, amendment 24 names it.
* *"An ordinary file is not held. MUST NOT BE HELD"* — the owner's **ratified
  ruling** of 13 Sep. Not open. The product is failing it, 20 to 25 times.
* **Which instrument to use to stop failing it** — the **owner's**, and not because
  it is taste. Every option sends more material off-device, and the privacy
  classifier gates exactly that class of change.

### Reproducing the number, and the number has a problem

Current classification rows only (no `superseded_by`); 371 files, **each with
exactly one current row**, joined to the answer key by path:

```
graded against labels2.json   (key protected 52)   over-protected 25   missed 38   unmatched 6
graded against answerkey2.json (key protected 20)  over-protected 20   missed  1   unmatched 6
```

**`108` §9's "25" is graded against the pre-ruling key.** `104` §18 records the
owner's ruling of 14:20 — résumés, club rosters, application essays and forms and
report cards are ORDINARY — and 36 key entries were flipped. `answerkey2.json`
carries 20 protected, which is that corrected shape; `labels2.json` still carries
52. Against the corrected key the over-protection is **20**, and the **missed count
collapses from 38 to 1**.

**Which key is of record is itself an owner question**, and it is the first one to
answer, because the two keys disagree about 32 files and every number below
depends on it.

### The shape, in aggregate — and it inverts the brief's premise

Every current classification row, by basis (file grain):

```
basis                    protected   cleared
safety_domain  (RULES)          17         0
local_model_gate                16        39
local_model_situation            6       279
user  (the person)               0        14
```

All 25 over-protected rows carry `handling_class = sensitive_personal`. All 17
`safety_domain` rows carry `privacy_class = ordinary`.

**Two-sided cost of each narrowing, against the corrected key (`answerkey2`):**

| narrow this | frees (over-protected) | ALSO frees files the key calls PROTECTED |
| --- | ---: | ---: |
| `safety_domain` — the deterministic rules | **1** | **16** |
| `local_model_gate` — the local model's gate call | **15** | **1** |
| `local_model_situation` — the local model's situation call | **4** | **2** |

*(Against the uncorrected `labels2` key the same table reads safety_domain 4 / 13,
gate 15 / 1, situation 6 / 0. The conclusion does not move.)*

**CONTRADICTION: the gate is not the problem.** `108` §9 and `109` both frame this
as "narrowing the gate". Measured, the deterministic rule is the part that works —
it is right on 16 of 17 files and is responsible for **one** of the twenty
over-protections. **Nineteen of twenty are the local MODEL's verdicts**, on its
gate call and its situation call. Narrowing the rule would be narrowing the
component that is carrying the safety story, to free one file, at the cost of
sixteen the owner's own key calls protected.

### What the hold actually costs those files — measured, and it is not nothing but it is not much

```
                          with a situation fact   in a group
the 20 over-protected        12  (60%)              6  (30%)
all 39 held files            12  (31%)             13  (33%)
the 332 unheld files        215  (65%)            122  (37%)
```

A held file is read locally rather than in the cloud; it is not abandoned. The
over-protected twenty reach a situation at 60 % against the unheld corpus's 65 %.
The cost is real — the cloud model is the better reader and these files never see
it — but "these files get nothing" would be false.

### The options the owner is being asked to choose between

| | option | frees of the 20 | also frees key-protected | note |
| --- | --- | ---: | ---: | --- |
| **1** | Narrow / retire `safety_domain` | 1 | **16** | recommend REFUSING |
| **2** | Override `local_model_gate` holds | 15 | 1 | the model's gate stops being final |
| **3** | Override `local_model_situation` holds | 4 | 2 | same, for the situation call |
| **4** | A model-only hold must be **corroborated** by a second finding before it stands (13 Sep's own rule, turned on the model instead of the rules) | ≤ 19 | ≤ 3 | systemic; needs a corroborating signal designed |
| **5** | Change nothing in the gate; let the **person release a named file** | any the person names | **0** | the mechanism already exists and already holds 14 files at `basis=user` |

### Recommendation

**Option 5 now, option 4 as the systemic follow-up, option 1 refused.**

Option 5 sends nothing off-device that the person has not named, file by file,
which is the only narrowing that is not a widening. It is already built — fourteen
files on this database already carry `basis = user` — and a user-confirmed fact
already outranks anything a model says (amendment 12a(iii)). It turns a library
ruling into a person's gesture, which is amendment 24's whole point.

Option 1 must be refused on its own numbers: one file gained, sixteen protected
files sent to the cloud.

---

## 4. Whether an approval was considered

### PREFERENCE or TRUTH — the measurement is a TRUTH; what to do about it is the person's

Whether the person's approval was a considered act is a **fact about the world**,
and the whole safety story rests on it, so measuring it is the library's. What
should HAPPEN when an approval turns out to be instant — warn, wait, do nothing —
is the **person's** and must never be decided by the library. That split is the
whole of the design below.

### The record shape already exists, and it is empty

```
review_presentations   presented_state_ref, surface, subject_ref, plan_version,
                       session_id, redaction_policy, evidence_refs, user_id, rendered_at
review_approvals       approval_id, plan_id, placement_decision_ref, plan_version,
                       required_review_policy, verdict, presented_state_ref, user_id, decided_at
```

`presented_state_ref` is a digest of what was on the screen, and it links the two
tables. That is exactly the join the question needs. On the owner's database:

```
review_approvals      0 rows
review_presentations 18 rows   (canvas 16, group_plan 2)
review_actions        2 rows   (both: group_plan / accept_bulk)
group_acceptance     22 rows
frozen_trees          3 rows
move_plans            0 rows
```

### The measurement is ZERO BY CONSTRUCTION, and that is the finding

**`src/apply_run/approval.py::approval_writer.write(plan, at)` writes both rows
with the same `at`:**

```python
shown = record_presentation(conn, …, rendered_at=at)
record_approval(conn, approve(conn, …, presented_state_ref=shown.presented_state_ref,
                              decided_at=at))
```

`decided_at - rendered_at == 0` in every row that will ever be written. The
elapsed time thedrive.ai's post-mortem is about cannot be computed from this
record, and never will be, however many rows accumulate.

**And the approval happens in the same breath as the screen.** `src/cli.py:26323`
calls `report(…, invite_freeze=not args.freeze)` and then, in the **same
invocation**, freezes with `shown_file_ids=frozenset(shown)` (`:26491`). So
`graph-agent run … --freeze` prints the proposal and approves it microseconds
later, in one process, with no human step in between. `shown` means "what this
very process printed a moment ago".

**What DOES exist is good and answers a different question.**
`apply_run/freeze.py:179` holds any placement whose file was not NAMED by the
report (`NOT_SHOWN`), and `apply_run/approval.py`'s own docstring is explicit:
*"the guard that makes the approval informed is therefore not the timestamp; it is
`shown_file_ids`."* That is a guard about **scope** — a file the run did not name
is not approved by this run — and it is sound. It says nothing about whether a
person read anything.

### "A control that has never said no" — measured

```
group_acceptance   22 rows   acceptance='accepted'  decided_by='user'  review_state='user-accepted'
                             DECLINED: 0     EDITED: 0
review_actions      2 rows   both accept_bulk   (2 gestures produced all 22 acceptances)
```

Twenty-two groups accepted, zero declined, zero corrected, by two bulk gestures.
That is the competitor's sentence, on this product's own database.

### The smallest honest measurement

Three records, no new table, no new screen.

**(a) Make the two timestamps mean different things.** Split `at` in
`approval_writer` into the moment `report()` returned (already available at
`cli.py:26323`) and the moment the gesture was taken. `rendered_at` and
`decided_at` already exist and already sit in the schema; today they are the same
value. Cost: one parameter. This alone makes every future row honest.

**(b) Record whether the approved state had been printed before.**
`presented_state_ref` is already a digest of the displayed state, and
`review_surface/store.presentation_exists` already looks one up by that digest. A
freeze whose digest first appears in this same process is a **same-breath
approval**; a freeze whose digest was printed in an **earlier invocation** is a
considered one. This needs no clock and no trust in one — it is the measurement
that survives a person who leaves the terminal open.

**(c) Count the verdicts per corpus.** Approvals, declines, and edits made between
the first print and the approval. *"A control that has never said no"* is exactly
`count(verdict != approved) == 0`, and it is one query.

**What it would show, today, on this database:** three freezes, zero approval
rows, twenty-two acceptances and zero declines, every approval same-breath. The
number the competitor's post-mortem warns about is not "under three seconds" here;
it is zero.

**Where it is shown:** one line, past tense, in the freeze's own summary, as a
fact and not a warning. *"Approved 3 folders. This plan was first printed by this
same command."* Nothing else, nowhere else.

### What it must NOT become

* **Not a minimum dwell time.** No "you have not looked at this long enough".
* **Not a confirmation.** No second prompt, no "are you sure", no typed word.
* **Not a blocker.** A same-breath `--freeze` stays legal: the owner ruled on
  2 Sep that `--freeze` IS the review surface, and an expert who knows their
  corpus is entitled to it.
* **Not a nag.** It is never repeated, never escalated, and never mentioned on a
  later run.
* **Not per-file re-approval.** `shown_file_ids` already scopes the approval;
  asking again file by file would be the dark pattern in its purest form.

The measurement records what happened. It never argues with it. If the owner later
wants the product to behave differently when approvals are instant, that is a
**setting** — which is amendment 24 applied to this item too.

---

## What contradicts the brief

Reported because the brief asked for the diagnosis even where it contradicts.

1. **The "25" is graded against the wrong key.** `108` §9's figure comes from
   `labels2.json` (52 protected), not from the key `104` §18 records the owner
   correcting (`answerkey2.json`, 20 protected). Against the corrected key it is
   **20 over-protected and 1 missed**, not 25 and 38. Which key is of record is an
   owner question this brief did not know it was asking, and it must be answered
   first.

2. **Item 3 is not a gate-narrowing problem.** `108` §9, `109` and this brief all
   frame it as narrowing a gate. Measured, the deterministic `safety_domain` rule
   is right on 16 of its 17 files and causes **one** of the twenty over-protections.
   **Nineteen of twenty are the local model's verdicts.** Narrowing the rule would
   free one file and send sixteen key-protected files to the cloud.

3. **Item 2 is not a threshold question, and the exposure is zero.** `cli.py`'s own
   comments call it *"a threshold, and a threshold is the owner's number"*. The
   defaults an unset clock writes are whole strings (`YYYY:01:01 00:00:00`), not
   low years, so refusing them costs nothing and needs no number. And no file in
   the owner's corpus carries a clock default, an implausible year, or — with 3
   capture timestamps across 371 files — enough EXIF to decide the question at all.

4. **Item 1's premise cannot be checked on this database, for a reason that
   outranks item 1.** No file carries a situation id: all 231 active `situation`
   facts hold a bare **kind**, and twelve of the thirteen distinct values are not
   names in the shipped release. So `106` Phase 2(b)'s change has reached no stored
   fact, and `108` §5's stated reason for not re-claiming 97.7 % describes a state
   this database is not in. The 93-of-163 figure above is measured at the kind
   grain instead, and is stated as such.

5. **A found defect larger than the question that found it.** `year_of` cannot read
   a PDF `D:` timestamp, so amendment 22's `year` folder level would be blank on 43
   of the 47 files that have a `creation_date`. Nothing about the year floor
   changes that, and it needs no owner input.

6. **A join I could not make, stated so nobody reads it as a finding.**
   `placement_decisions.subject_ref` is not a file id, so the item-3 cost table's
   "in a placement decision" row read 0 % for every group including the unheld one.
   That is the join failing, not files missing from placement. Not chased.
