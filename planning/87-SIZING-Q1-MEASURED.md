# 87 — Q1, the sizing question, measured

Date: 2026-09-02
Status: **A brief for the owner. It changes no code, no test, no manifest and no
vocabulary.** Every number in it comes from running the shipped command over four corpora
on this machine, offline, with no API call to any provider. The prototypes it describes
are unlanded and live under
`/private/tmp/claude-501/-Users-jy-GRAPH-AGENT/da9ffc7f-c259-4c21-8014-3a25650964d6/scratchpad/q1/`.

Q1 is `65` §2.2 and `68` F1, and `84` §3 calls it *"still the highest-value decision
available"*. The three options on the table are **widen the extractor**, **narrow the
detector**, and **ask the user**. This document does not choose between them. It exists
because nobody had the numbers, and a decision made without them would be a guess with
a paper trail.

**Read §1 and §7 if you read nothing else.** §1 is what the product actually does today
and it is not what `84` says. §7 is the recommendation and the one fact it turns on.

---

## 1. The headline, and why the question's premise has moved

`84` §3 states the problem as:

> *"Most files come back **needed a model** and every persona ends with zero files ready
> to file."*

Both halves were true when they were written. Neither is true now.

**74 files across four corpora. 5 are ready to file. 60 abstain.**

| corpus | who | files | ready to file |
|---|---|---|---|
| A | Dana — paralegal, part-time law student, single parent, her own custody matter, her kid's school, her taxes, her camera roll, her Downloads | 34 | **0** |
| B | Priya — full-time undergraduate, one university, one term | 12 | **5** |
| C | everyday life — memes, game saves, mods, fan fiction, a Downloads folder (`77` §3's own corpus, residual **by design**) | 14 | **0** |
| D | Tom — householder: an insurance claim, a tenancy, a council tax bill, an MOT, a GP letter | 14 | **0** |

Seven further files get a `place` decision that reads *"already in X — nothing to do"*.
They are counted honestly by the report and are not filing wins.

**What the 60 abstentions actually tell the person:**

| the sentence on screen | files | share |
|---|---|---|
| *"This file has not been classified — nothing has yet said what kind of material it is"* | **38** | 63% |
| *"This file is protected material (§8.4)"* | **13** | 22% |
| *"Deciding this file needed a model, and §8.4 did not clear this file for a model call"* | **9** | 15% |

So the model wall is the *smallest* of the three terminal states, not the largest. The
dominant one is `68` F1 — the file was never classified. Wiring DeepSeek addresses 9
files out of 74; it is not the symptom of the thing Q1 is about, it is a different and
smaller thing.

**Every one of the 60 abstentions is recorded as `privacy_blocked`**, whatever it says on
screen, because `placement/pipeline.py:505` asks `needs_model_call` *before* it consults
the assessment's own §6.10 reason. That matters for §5 and it matters for `83`: **with a
model wired and the privacy gate open, 60 of these 74 files would be sent to it** —
including 22 that carry no authored term of any schema and 47 that produced no fact at
all.

---

## 2. Where each file stops, by stage

### 2.1 The detector, over all 74 files

`Detector.explain` names its own reason. The command never prints it, so this was
recovered by rebuilding the same detector against the same databases.

| verdict | files | what it means |
|---|---|---|
| **Recognition** | 28 | a schema was concluded |
| **Abstention `no_evidence`** | 22 | the file carries no term any schema authored |
| **Abstention `no_corroboration`** | 16 | exactly **one** authored term matched, and every row carries `never_alone`: one signal never activates a schema |
| **Abstention `ambiguous`** | 8 | two or more schemas matched the same number of terms; `00` requires abstention rather than a winner |

**24 of the 46 unclassified files — the 16 plus the 8 — are files where the detector
found authored terms and stopped on a rule about counting signals.** They are not files
it had nothing to read. That is the largest single population in this document, and it
is bigger than everything options 1 and 3 touch put together.

The other 22 are photographs, game saves, mods, a `.mp4`, `.bin` scratch files and an
encrypted vault. `77` §2.3 rules that this material is residual **by design** — ROSTER
§5.6, and `00`:120 names "Memes" as a user-defined residual area. **Their not reaching a
domain is the design working.** They are counted here so the 46 is not read as 46
failures.

### 2.2 The 28 recognitions are not all right

Where the detector does conclude, it is often wrong, and the errors are not near misses:

| the file | what the detector concluded |
|---|---|
| a law-school `CONTRACTS 210` problem set | `construction_property` |
| a privilege log in a live discovery matter | `creative` |
| a family-law petition for modification of custody | `clinical_practice` |
| a passport scan | `clinical_practice` |
| a paralegal certificate assignment brief | `business_operations` |
| an MOT certificate | tied `academic` + `construction_property` + `finance` |

Four of the eight `ambiguous` ties pair `academic` with `construction_property`. This is
relevant to option 3: an answer only helps if the reading the person confirms is one the
file's own words actually raised.

### 2.3 The fact layer: two fields, and one refusal reason out of thirteen

| | files with the fact |
|---|---|
| `subject` | 26 |
| `term` | 13 |
| **no fact at all** | **47 of 74** |

Those two field keys are the entire vocabulary this deployment can fill. Every downstream
stage is keyed on them: P9's grouping anchor, P10's tree dimensions, P11's retrieval
channels, and the `DIRECT_FACT` channel that placement scores. A litigant's matter name,
a householder's insurer, a parent's child's school are not expressible, because no field
exists to hold them. Corpus D was run under `finance.household-property`, whose offered
dimension is *"Kind of home document"*, and **nothing in the product can fill it**.

The `unresolved` table holds 61 rows across the four databases. **Every one of them is
`term` / `no_candidate_evidence`.** `subject` never records a refusal at all, because
`cli.py`'s resolver passes `pending_fields=lambda conn, file_id, content_hash: ()` — the
sequencer is given no list of fields it was supposed to fill, so it has nothing to refuse
about. **Twelve of the thirteen `UNRESOLVED_REASONS` have never fired on a live run**,
and the product cannot tell you why a file has no subject.

That is worth stating plainly: **Q1 could not be answered from the product's own records.
It had to be instrumented from outside.**

### 2.4 What "ready to file" needs, in full

Measured, a file reaches `Ready to file` only if all six hold:

1. it has a fact;
2. that value is shared with enough other files that P10 builds a folder for it;
3. exactly **one** candidate node claims the value (`unique_direct_match`);
4. support ≥ 0.50 — a direct fact alone scores 3/7 = 0.43, so the accepted-group channel
   is doing required work;
5. margin ≥ 0.20 over the runner-up;
6. the file is not classified into one of the four safety domains.

Corpus B satisfies all six for 5 files. Corpus A satisfies (3) for nothing in the
Hendricks matter, because `Work/Hendricks matter` and `Downloads` both claim
`CV20264417` — the exhibits list was downloaded and never moved — so both score 0.714, the
margin is 0.00, and four good files stop.

---

## 3. Option one — widen the extractor

### 3.1 What was prototyped

`src/cli.py` ships one identifier pattern:

```python
_STRUCTURED = re.compile(r"\b[A-Z][A-Z0-9]*[ -]?[0-9]{3,}\b")
```

It requires a leading uppercase letter, so every purely numeric reference a real document
carries is invisible to it: an electricity account number, a council tax reference, an NHS
number, an EIN, an MOT test number. The prototype
(`prototypes/option1_widen.py`) adds the smallest widening that reaches that class —
`\b[0-9]{6,}\b` and `\b[0-9]{2}-[0-9]{7}\b` — and re-runs all four corpora.

Six digits is the floor because a year is four, a page number is one to three, and a sum
of money under 100,000 carries a comma or a point.

### 3.2 What it moved

**Nothing.**

| | before | after |
|---|---|---|
| ready to file | 5 | **5** |
| detector verdicts changed | — | **0** |
| placements changed | — | **0** |
| "needed a model" | 9 | 10 |

### 3.3 Why it moved nothing, which is the useful part

`65` §2.2 states the cause as *"the detector has almost nothing to match against"*. **That
is no longer true and the widening is what proves it.** P4 stores the whole of a text
document's body as one span-less `body` observation, and `Detector._matches` reads the
`raw_value` of every live observation. The detector already sees every word of the file.
`_STRUCTURED` never fed it. It feeds exactly two things: the `subject` direct slot, and
the corroboration seam — which can only fire when a single schema leads on exactly one
term, and only on an observation no term matched.

So widening the pattern cannot help classification, and classification is where 38 of the
60 abstentions stop.

### 3.4 What it costs, measured

Nine new readings entered P4's observations. One of them is a **passport number**
(`517204418`, from `Passport No. 517204418`). Two are EINs. One is `0088142`, a fragment
of `EFT-2026-0088142`.

The narrow pattern already does this. Measured on the current build, **5 of the 27
fact-bearing files hold a `subject` a human would not call the document's subject**:

| the file | the `subject` fact it holds |
|---|---|
| `Downloads/passport scan.txt` | `MAR1988` — read out of *"Date of birth 09 MAR 1988"* |
| `Work/Hendricks matter/efiling receipt.txt` | `EFT2026` — a fragment of the transaction id |
| `ECON 2105 syllabus.txt` | `IAB1022` — the professor's **office room number** |
| `AY 2024-25 fee statement.txt` | `ID88410277` — the student number |
| `Insurance/claim CLM88213 first notice.txt` | `HO4471902` — the **policy** number, on a document whose own heading is the **claim** number |

The direct path has no margin — `e050c41`'s own commit message says so, and it is why the
term slot was deleted and moved to the rule stage. A document carrying several identifiers
gets an arbitrary one. **Widening the pattern puts more identifiers into more documents
and supplies no rule for choosing between them, so it makes the wrong subject more likely,
not the right one.**

### 3.5 The repo's own counter-evidence, and what it actually shows

`e050c41` and `e20a39c` widened the **term** patterns — `Spring 2025`, `AY 2024-25`,
`Michaelmas Term 2024` — and that did move real files. Corpus B confirms it: all three
written forms produce a term fact, and 9 of 12 files carry one.

But that pair of commits is not an argument for this widening, and the difference is the
whole point. They did **not** loosen a pattern; they added *three named forms of one thing
the design already asks for by name* (`00` §3.10), each with its own canonicaliser, and
they moved the field off the direct path onto the ranked rule path **so that a tie
refuses**. The safety was not "narrow `subject` off terms" as a trade — it was that the
new field arrived with a margin. Widening `_STRUCTURED` has no such structure available:
`subject` is still on the direct path, and there is nothing to rank.

---

## 4. Option two — narrow what counts as needing a model

### 4.1 What was prototyped

`needs_model_call` returns True for any assessment that is not a unique direct match and
has at least one candidate. `prototypes/option2_narrow.py` measures two narrowings.

**2A — a `multiple_supported_homes` assessment does not need a model.** Two legal
destinations cleared §6.10's support condition and nothing separates them.
`_abstention_explanation` already holds the right sentence for this —
*"which one is its home is a choice about your material, not a gap in the evidence"* — and
today it is unreachable, because `run_file` asks `needs_model_call` before the reason.

**2B — 2A, plus: an assessment where no candidate clears the support threshold does not
need one either.** `needs_model_call`'s own docstring refuses the empty case because
*"there is nothing for a model to choose between, and asking one would be inviting it to
invent"*; a candidate set every member of which the evidence failed to support is that
situation with extra steps.

**Added 2026-09-03, from `9e7152e`, and it is a better argument for 2B than the one
above.** A corpus was measured whose three candidates tied at 2/7 — the accepted-group
channel alone, no direct fact anywhere — and `needs_model_call` sent all three to a model
as a bounded ambiguity. `materialise.branch_expectations` then gave the branch the
`subject` its files agree on, one candidate carried a direct fact, and the tie broke with
no call. **A tie between destinations none of which states anything is not a bounded
ambiguity, it is a tree with nothing to match against.** That is the same reasoning
`needs_model_call` already applies to the EMPTY candidate set, and 2B is where it belongs:
the question is not how many candidates there are, it is whether any of them said
anything the file could match. Written up against the shipped command, not a prototype —
`9e7152e` is landed and `tests/integration/test_cli_agreeing_corpus.py` holds the case.

### 4.2 What they moved

| | ready to file | files a wired model would receive | what the person is told |
|---|---|---|---|
| shipped | 5 | **60** | 38 unclassified / 13 protected / 9 model |
| 2A | **5** | 55 | 5 files get *"more than one supported home — you pick"* |
| 2B | **5** | **0** | **all 60 get one sentence** |

**Neither files a single additional file.** What option 2 buys is truthfulness and model
cost, not filing.

### 4.3 What they cost, measured

**2A leaks a protected file.** Two of the five `multiple_supported_homes` files are
classified into a safety domain. Narrowing `needs_model_call` in front of the privacy
check routes them past §8.4's sentence and into *"you pick which folder"*. The naive
ordering is wrong; the check has to stay first and only what is left may be narrowed.

**2B collapses three states into one message.** Under 2B all 60 abstentions read *"No
legal destination cleared §6.10's conditions (…)"*. *"This file has not been classified"*
and *"This file is protected material"* both disappear. That is precisely the collapse
`66` §4 forbids by name — "protected", "unreadable", "unsupported format", "still
indexing" and "no strong match" may never share one message — and it is the same defect
`classifier`'s docstring in `cli.py` records as a COLLAPSE from the other direction.

The honest reading of option 2 is that it is a correctness fix worth doing on its own
merits and **is not an answer to Q1**.

---

## 5. Option three — ask the user

### 5.1 It already ships

Nothing needed prototyping. `cli.run` builds the detector with
`settled_by_user=lambda: activated_schemas(conn)`; `Detector.explain` breaks a tie when
exactly one tied reading is a schema the person has confirmed; `_raise_blocked_questions`
prints a pasteable line for every tie. A real run already says:

```
Questions only you can answer:

  What kind of material is CLM88213?
    1 file mentions CLM88213, and its own words support 5 readings equally.
      --answer reading.organization:CLM88213=finance   finance material
      ...
    Answering will not move, rename or delete anything.
```

### 5.2 What it moves, measured

`prototypes/option3_ask.py` runs each corpus cold, reads every question it raises,
answers every one the way the person whose disk it is would answer it, and re-runs on the
same database.

| | cold | answered |
|---|---|---|
| questions asked, across 74 files | — | **5** |
| ready to file | 5 | **7** |
| abstentions | 60 | 59 |

**Five questions, two more files filed**, both of them in corpus B. Corpus C raises no
question at all. Corpora A and D raise three between them and gain nothing.

### 5.3 Why the reach is that small, and this is the finding

The question is raised only where **both** hold: the file has a `subject` fact
(`questions/triggers.py:137` skips a file with no subject), **and** two or more schemas
tied (`:142` requires `len(tied) >= 2`).

Measured against the 46 unclassified files:

- **12 of the 16 `no_corroboration` files have a single leader** — one authored term
  matched, one confirmation away from a classification, and the detector's own comment
  says *"the person's confirmation counts as the second signal for the schema it names"*.
- **None of those 12 has a `subject` fact.** They are screenshots, a whiteboard photo, an
  `.mp4`, `.bin` scratch files, a `.zip`, an SSH key. So the question mechanism, which is
  keyed on an extracted identifier, **cannot be asked about any of them**, and
  `Detector.explain` would not accept the answer if it were, because its
  `settled_by_user` branch is gated on `len(leaders) > 1`.

The friction arithmetic, if the question were keyed on the **folder** the files sit in
rather than on an identifier lifted out of them:

| | today | folder-keyed |
|---|---|---|
| questions | 5 | **21** |
| unclassified files reached | 5 | **46** |
| files per question | 1.0 | 2.2 |
| questions per corpus | 0–2 | 1–8 |

`80` R2 binds here: **the friction budget is spent ONCE, and a confirmation a person
learns to click through is not a safety mechanism.** A folder-keyed question survives that
test in a way a file-keyed one does not — *"everything in `Photos/Camera roll dump` — what
is this?"* is asked once, is answered once, and is a question about the person's own
filing rather than about a machine's reading. Six to eight of those at onboarding is a
different act from 46 confirmations.

---

## 6. Three things found while measuring that are not Q1

Reported here because they were found by running the product and nothing else would have
found them. None is fixed; `src/cli.py` belongs to the lead.

1. **A live crash.** `grouping/pipeline.py` returns a `GroupingResult` carrying a group a
   stop rule prevented from being recorded — deliberately: *"a group that cannot form
   should not cost either one"*. `cli.review_and_accept` keeps every result whose
   `group is not None` and sets `supersedes = grouped[0].group.group_id`, so **when the
   first result is a stop-ruled group the run dies with
   `grouping.store.RecordAbsent: … supersedes nothing`.** Corpus B triggers it. Corpus A
   does not, which is why it has not been seen. The proposed fix is one line — filter
   `results` to those with `stop_rule_outcome is None` before merging — and it is what the
   measurement harness monkeypatches so it could run at all.
   `prototypes/00-crash-stop-ruled-group.diff`.
2. **Every existing folder is minted as a tree node twice.** Corpus A's `tree_nodes` holds
   ids 1–18 and 20–37 for the same eighteen folders. Placement only ever sees the second
   set. Not chased.
3. **A `multiple_supported_homes` abstention is reported as "needed a model"** — §4.1
   above. Five files in corpus A, and the sentence they are owed already exists.

---

## 7. Recommendation

**Option 3, re-keyed from the identifier to the folder. Do not widen the pattern.**

**The deciding factor: option 3 is the only one of the three that moved a file in
measurement, and it is the only one that can supply a value no pattern can read.**

Option 1 moved zero files and put a passport number into the observation store. Option 2
moved zero files; it is a correctness fix and should be judged as one. Option 3 moved two
for five questions — thin, but non-zero, and its reach is small for a reason that is
fixable rather than fundamental: it is asked about the wrong thing.

The north star decides the tie-break between "re-key it" and "leave it". A student's
corpus is the one shape the deterministic path already handles — corpus B files 5 of 12
with no help at all. A litigant's, a householder's and a parent's do not, and they do not
fail for want of reading: **24 of their unclassified files carry authored terms the
detector found and then declined to act on alone.** An option that works for a student and
fails for a litigant has not solved Q1, and options 1 and 2 are both measured at zero for
the student *and* the litigant. Only the ask reaches the material where the answer is not
in the file at all — that this folder is a matter, that this one is the kid's school, that
this camera dump is family photographs. No pattern recovers that, because it was never
written down.

Two things would have to be true, and both are the owner's to rule on, not mine:

- the question is keyed on a **folder** (or another thing the person recognises), not on
  an identifier the product lifted out of a document;
- `Detector.explain`'s `settled_by_user` branch is opened to the single-leader case, so a
  confirmation can be the second signal `never_alone` demands. The code's own comment
  already argues for this: *"`never_alone` is a rule about the DETECTOR concluding from
  one signal; it was never a rule about what a person may tell the product."*

**Neither is a licence to ask more.** `80` R2 is the constraint, and 21 questions may
already be over budget — see §8.

---

## 8. What I am not sure about

- **Whether 21 questions is inside `80` R2's budget.** I measured the count; I did not
  measure whether a person answers 21 of anything. If the true budget is six, the
  folder-keyed question has to be asked about the top folders only, and the tail stays
  unclassified. I do not know where the line is and I do not think it can be settled by
  measurement — it is a judgement about a person.
- **Whether four corpora generalise.** They are hand-built and I built three of them,
  which means their file shapes are my guesses about a real disk. Corpus A came from
  another agent's persona work and is the least contaminated by this question. The
  headline `5 of 74` should be read as an order of magnitude, not a rate.
- **Whether an answered question sticks.** `academic` and `construction_property` tie four
  times, which suggests the recognition manifest has a systematic overlap. If a person
  answers `academic` and the manifest still hands `construction_property` two terms on the
  next file, the answer moves the error rather than removing it. I did not measure a
  second corpus after answering.
- **Whether option 2's model-cost number matters yet.** "60 of 74 files would be sent to a
  model" assumes the privacy gate opens, and `80` §2/§8's suspension is development-only.
  On today's `offline` deployment the number is 0 and stays 0.
- **The `no_evidence` 22.** I have counted them as correct — `77` rules them residual by
  design — but I have not tested whether a person agrees that a folder of memes and game
  saves being *"waiting for you to say what these are"* reads as care or as failure. `77`
  §2.5 records that the residual route those files need is built and reachable from
  nothing a person runs, which is a different open item.

---

## What this document did not do

It did not change `src/cli.py`, land a prototype, choose between the three options, or
spend a currency unit on any provider. The three prototypes are monkeypatches in a scratch
directory and are deleted by rebooting the machine.
