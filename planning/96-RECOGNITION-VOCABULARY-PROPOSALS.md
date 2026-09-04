# 96 — What the detector cannot do, and what only you can fix

**For the owner. Everything below was measured on your own files.** Seven decisions
are yours; nothing here has been implemented, because each one either adds a word to a
closed vocabulary or changes what the product is willing to claim.

## The seven decisions, shortest first

| # | The decision | Why it is yours | Evidence |
|---|---|---|---|
| **1** | **Author the missing SAFETY words.** `vaccination`, `vaccine`, `immunisation` (only the US `immunization` exists), `hkid`, `identity card`, `id card`, `national id`, `medical record`, `health record`, `patient record`, `credit card`, `bank statement` are authored by **no schema at all**. | Adding a member to a closed vocabulary is yours alone. | §14, §17 |
| **2** | **Author the everyday coursework words.** `HW` matches nothing while `homework` does — and `HW` is what actually appears in your filenames. | Same. | §10, §16, §18 |
| **3** | **Drop two words that block a right answer:** `construction_property:valuation` and `retail_hospitality:sessions`. They tie with `syllabus` on your own syllabus file and switch off the rule that would have classified it. | Removing an authored term is yours. | §9 |
| **4** | **Rule on `will` and `statement`** — single ordinary English words authored as safety work types. They lock innocent files (a volunteer schedule, a CS exam, four "statement" documents). There is **no safe code fix**: suppressing them releases `last will and testament` and `financial statement`. | A trade between over-protection and over-release. | §4, §5, §11 |
| **5** | **Should a software project be a place files can go?** `code.software-project` is not among the 208 situations. Today those files are *set aside by rule*, not misfiled. | Adding a situation is yours. | §2 |
| **6** | **Should the detector stop reading toolchain metadata?** `Producer = "iOS Version 18.5 (Build 22F76)…"` makes `build` the only word on a physics homework — 10 of 18 files on your live corpus. | The cure needs an authored list of field names. | §15 |
| **7** | **Should recognition require a file to NAME itself?** A stricter rule raises precision (9 right of 19, from ~6 right of 30) but stops labelling 96 of 111 files. | A trade only you can price. | §3 |

## The one thing to read if you read nothing else

**Recognition is wrong about roughly four files in five today, and the cause is
arithmetic.** A schema wins by how many authored words it matched, so a catalogue with
827 words beats one with 41 — `business_operations` and `creative` took 93 of 111 wins
on your Documents folder, while `academic` won 4 on a corpus of AP coursework and
`code` (41 words) can essentially never win. See §1.

**And 38.9% of the 8,429 authored words are prose that no file can ever match** —
including literal authoring notes such as *"proposed for r6, not design: accession
register, deaccession…"*. The four safety domains are the worst affected: 85% of
`legal`'s words and 65% of `medical`'s are unmatchable. See §7.

## What is NOT your problem, so you do not pay for it twice

- **Files that were never read.** Three PDFs of 1-2 MB on the live corpus yielded
  **zero text**. A file the detector is handed nothing about must abstain, and no word
  you author changes that. That is extraction's, not yours. See §18.
- **A file cannot be protected before it is opened.** Classification runs *after*
  extraction, by design, so the detector can only ever MARK a file, never prevent it
  being read. A pre-read guard is a different mechanism in a different part. See §14.
- **Vocabulary alone will not reach 99%.** A filename carrying one work word and no
  course code cannot be classified deterministically however good the words get,
  because the product refuses to act on a single signal. Those files need a declared
  situation, an answer from you, or a model. See §16.

## Two corrections this document makes to itself

§17 and §18 withdraw claims in §14 and §16 that were measured over files the extractor
had starved of text. **What survives is the half that never depended on extraction:**
the missing words are missing, and seven of the eight sensitive files match no safety
word *in their filename* — which is also the only signal available before a file is
opened.

---

## 1. Recognition is wrong about four files in five, and the cause is arithmetic

**This is the finding that matters most, and it is not a proposal — it is the
context for everything below.**

Of 413 files, 111 were recognised. Their labels:

| schema | wins | schema vocabulary size |
|---|---|---|
| `business_operations` | 72 | 818 terms |
| `creative` | 21 | 827 |
| `construction_property` | 9 | 1022 |
| `academic` | 4 | 248 |
| `clinical_practice` | 3 | 211 |
| `college_applications` | 1 | 121 |
| `retail_hospitality` | 1 | 514 |

93 of 111 wins go to the two largest ordinary vocabularies. The corpus is mostly
high-school coursework and software notes, and `academic` won 4 files.

The detector scores a schema by **how many distinct authored terms it matched**
(`explain`: `best = max(len(found) ...)`). A schema with 827 terms has twenty times
the chance to match than one with 41. **Counting matched terms measures vocabulary
size, not fit.** Real verdicts from the run:

- `AP World History 美国英文教材高中课本世界历史课程.pdf` → `clinical_practice`
- `Backup of Resume - Joseph Yung.docx` → `business_operations`
- `CommonApp Activity List and honors.xlsx` → `creative`
- `moses_liew_coffee_chat.md` → `construction_property`
- `master-setup-prompt.md` → `retail_hospitality`
- `CLAUDE.md`, `third_eye.md`, `pipeline.md`, `llm_grounded_narrator.md` →
  `business_operations`

Judged by filename alone (files were not opened), roughly **6 of a 30-file random
sample are right** — about 20%.

The catalogues are not balanced against each other and nothing in the detector
normalises for that. Any fix is a design decision, not a bug fix.

---

## 2. `code.software-project` does not exist among the 208 situations

Software projects on the owner's disk have no situation to be filed under. This
compounds item 1: the `code` schema carries **41 terms**, the fewest of the 23, so
even where `code` is the right reading it loses to `business_operations` on
arithmetic. `morphogenesis_vessel_notebook_prompt.md` was recognised
`construction_property`.

Note the run does not leave these files unhandled — it **sets 81 of them aside by
rule** as "software project root descendant" (detected on `library.properties`,
etc.), not read and not in the plan:

```
Set aside by rule: 81, not read and not in this plan
  Adafruit_BusIO_Register.cpp  (software project root descendant: library.properties)
  ...
```

So "no home" means *set aside*, not *misfiled*. The question for the owner is
whether a software project should be a destination the product can propose, or
should stay set aside. **Adding the situation is the owner's call and has not been
made here.**

## 3. `no_naming_term` — a proposed seventh abstention reason, and its cost

A previous agent's unlanded patch adds a **nomination gate**: a term may only
activate a schema when it says what the file IS (a `work_type_term`) *and* sits
where the file names itself (filename, title, metadata, or a page-one heading).
Everything else corroborates. Files nominating nothing abstain with a new reason,
`no_naming_term` — a seventh member of `ABSTENTION_REASONS`, which is a closed
vocabulary with a validator (`check_abstention_reason`).

**Measured on `~/Documents`, applying that patch in full:**

| | HEAD | with the gate |
|---|---|---|
| recognised | 111 | **19** |
| protected | 2 | 2 (the same two) |

- It **buys precision**: of the 19, **9 are clearly right, at most 2 clearly wrong,
  and 8 unknowable from the filename** (`PVA Project Data.xlsx`, `_index.md`-style
  names). Against HEAD's ~6 right in 30. It corrects real errors —
  `Backup of Resume - Joseph Yung.docx` `business_operations` → **`career`**;
  `000-考纲AP World History...pdf` → **`academic`**;
  `morphogenesis_vessel_notebook_prompt.md` `construction_property` → **`code`**.
- It **costs recall**: 96 files lose any label, including right ones —
  `Copy of Class of 2023 College Application Tracker.xlsx`, which HEAD labelled
  `college_applications` correctly, abstains.
- It **buys nothing on protection**: the same 2 files, including the same false
  lock (below).

So the gate is a real remedy for item 1 and it is expensive. **It was not adopted**:
it requires a closed-vocabulary addition, and the trade — 92 fewer labels for a
precision gain — is the owner's to make, not an implementer's.

---

## 4. `will` is a single-token `legal` work type, and it produces a false lock

`legal` ships 91 work types. Exactly two are a single token: `codicil` and **`will`**
— English's commonest modal verb.

The one false lock on the corpus:

```
PROT sensitive_personal safety_domain
     /Users/jy/Documents/Manage Drives_Drive Details_View Schedule.xlsx
     outcome: ambiguous
     work types: ['legal:will@table/pNone']
```

A volunteer drive schedule, sealed and withheld from placement because a spreadsheet
cell contains the word "will".

**There is no safe detector-side fix, and none was made.** The zone cut that catches
this on the winning-schema path cannot be applied to `_precaution`: that path exists
for the passport whose OCR body reads "Passport. X12345678.", and narrowing it by
zone would release exactly the material `00`:52 and `00`:185 require to be held.
Vetoing protection on `file_kind_plausible` would be a release with no basis in
`00`:185. The root cause is the authored vocabulary, and removing `will` would make a
genuine last will and testament unrecognisable — an over-release. **The owner's
call.**

An over-protection is the safe error, so leaving this lock in place is correct until
the owner rules.

---

## 5. Nine "statement" files are held, and only vocabulary can release them

Eleven real files on this disk have "statement" in the name. Nine carry
`finance:statement` as a **work type in the FILENAME** — a naming zone, so the zone
cut cannot reach it, and that is exactly what raises the lock on the winning-schema
path. Only one of the nine deserves it:

> **Measurement caveat.** `Statement.pdf` is a *measured* `protected=1` from the
> `~/Documents` run. The other ten live in `~/Downloads`, whose index build was
> killed (4,901 files, machine load 87), so for those the filename term match is
> shown and the end-to-end verdict is **inferred, not measured**.

| | file |
|---|---|
| held, right | `Statement.pdf` — a real brokerage statement |
| held, arguable | `2024-annual-report-proxy-statement.pdf`, `Johnson-Controls-…-proxy-statement-and-SEC-Form-10-K.pdf` — public SEC filings, not the owner's finances |
| **held, wrong** | `Chinese University Personal Statement.pdf` |
| **held, wrong** | `Penn Personal Statement.docx` |
| **held, wrong** | `Personal Information Collection Statement.pdf` — a privacy notice |
| **held, wrong** | `Research Interest Statement_ Garcia Research Program.pdf` (×2) |
| **held, wrong** | `Statement for research internship.pdf` |
| **held, wrong** | `exam2 2.pdf` — a Columbia CS exam, see §7 |
| open | `2025209423_Joseph_Yung_PersonalStatement.pdf` (×2) — one token, matches nothing |

**A code fix for this was written, measured, and reverted.** Refusing a term whose
tokens sit inside a longer matched term's tokens releases the two "Personal
Statement" files correctly. Enumerated over the whole shipped library it also
produces **210 pairs where no safety work type is left standing**, and these are
over-releases:

```
'will'      (legal)    suppressed by 'last will and testament'  (legal, CONTEXT term)
'will'      (legal)    suppressed by 'living will'              (legal, CONTEXT term)
'statement' (finance)  suppressed by 'financial statement'      (law_practice)
'statement' (finance)  suppressed by 'pay statement'            (finance, CONTEXT)
'statement' (finance)  suppressed by 'earnings statement'       (finance, CONTEXT)
'statement' (finance)  suppressed by 'statement period'         (finance, CONTEXT)
'invoice'   (finance)  suppressed by 'commercial invoice and customs valuation support'
'invoice'   (finance)  suppressed by 'invoice to'               (construction_property)
'receipt'   (finance)  suppressed by 'photographed receipt or slip' (photos)
'passport'  (identity) suppressed by 'passport citizenship or emergency travel …'
'visa'      (identity) suppressed by 'visa or entry permission application …'
'driver licence' (identity) suppressed by 'driver licence entitlement and …'
```

A file named `Last Will and Testament.docx` would lose `legal` protection **from its
own filename**. No rule separates these from `personal statement`, because the
difference is semantic: `personal statement` is a *different thing* that contains the
word; `last will and testament` is a *species of* will. An over-release is worse than
an over-protection, so the fix was reverted and the over-protection left standing.

**The cure is vocabulary, and it is the owner's.** Either author the missing terms
(`research interest statement`, `information collection statement`), or re-file
`last will and testament` / `living will` / `pay statement` / `earnings statement`
as work types so the covering term keeps protecting, or take the `no_naming_term`
gate in item 3.

## 6. `finance` carries no word for a bank

`/Users/jy/Documents/Bank reference letter.pdf` is **open, unprotected**. Its only
term match is `reference letter` (from the filename, owned by `academic` and
`career`); the two tie at one term each and it abstains `no_corroboration`.

The word **`bank` matches nothing at all**. Checked against the shipped library:

```
'bank'           ABSENT from finance
'bank statement' ABSENT
'account'        ABSENT
'iban'           ABSENT
'sort code'      ABSENT
'balance'        in finance
'deposit'        in finance
```

A bank reference letter states an account holder and their standing — finance
material under `00`:52 — and the detector cannot see it. This is an **over-release by
vocabulary gap**, distinct from the detector-logic over-releases (of which the
corpus showed none). Adding terms to `finance` is a closed-vocabulary change and has
not been made.


---

## 7. MEASURED ON THE LIVE 18-FILE COURSEWORK CORPUS — the real causal chain

Run on `scratchpad/live`, 18 of the owner's real coursework files,
`--situation academic.coursework`, no cloud. **5 of 18 recognised, 1 protected.**

**13 of the 18 abstain `no_corroboration`** — they matched exactly ONE authored
term, and `never_alone` requires two. That is the whole bottleneck, and it is not
the prose-description problem:

- **Prose-shaped terms can only fail to add signal.** They are too long for any
  file to carry, so they subtract nothing.
- **Single-token ordinary English is what subtracts.** It produces junk matches
  that TIE with the real term, and a tie switches off the corroboration path that
  `00`'s worked example depends on.

### The library, measured

**8,429 distinct authored terms** (the 8,925 figure counts cross-schema duplicates):

| shape | count | share |
|---|---|---|
| 2-5 tokens | 3,903 | 46.3% |
| **prose (≥6 tokens, or containing `or`/`and`/`with`/`the`)** | **3,276** | **38.9%** |
| single token | 1,250 | 14.8% |

38.9%, not 46.5% — but the shape of the finding holds, and the examples are worse
than the number. These are **authoring notes compiled into the matchable
vocabulary**, verbatim:

```
proposed for r6, not design: accession register, deaccession, object entry, …
proposal note: none of these terms appears in 00. 00 names only the academic …
as-built or record survey — not claimed here as a situation: the deepened …
precondition: these are values of a work_type field, not rows, and — critically …
the design floor for academic context is unchanged: syllabus, lecture, credits, …
```

No filename or heading can ever match these. They are prose written to be read by
a person, sitting in the table the detector matches against.

### `00`'s own worked example fails, for TWO reasons, neither of them mine

`Syllabus BUSIB 4300 Spring 2026 Haran Segram.pdf` abstains. `00` says *"BUSIB 4300
becomes a course fact only when the engine finds a course-code pattern together
with academic context such as 'syllabus'"*. Measured:

```
all terms: academic:syllabus@filename
           construction_property:valuation@heading/p1
           retail_hospitality:sessions@heading/p6
identifier observations found: 0
```

1. **The course code is never seen.** `_identifier_observations` (`cli.py`) filters
   on `STRUCTURED_EXTRACTOR` + a `text_span`, and the structured pass is wired only
   into `macos_readers` — so a code in a **filename** is never an identifier.
   `_STRUCTURED` *would* match `BUSIB 4300`; nothing applies it there.
2. **Even with the code seen, it still abstains.** Two junk heading terms tie with
   `syllabus`, and the corroboration branch requires exactly one leader. Relaxing
   that is forbidden by a tested invariant —
   `test_a_structured_identifier_cannot_break_a_tie_between_two_schemas`: a
   schema-agnostic pattern "may second a schema a term already named and may never
   choose between two."

**Verified by simulation:** with identifiers forced on, the file still abstains.
**There is no fix for this file inside `src/recognition/`.**

### The fix is NOT vocabulary pruning — measured, and it goes backwards

| variant | recognised | protected |
|---|---|---|
| baseline (shipped) | 5/18 | 1 |
| A: every single-token term removed from all 15 non-safety schemas (1,186 terms; finance/identity/medical/legal untouched) | **2/18** | **2** |
| B: filename identifiers wired (simulated) | **11/18** | 1 |
| A + B | 2/18 | 2 |

**Pruning makes it worse on BOTH axes** — fewer right answers *and* one more locked
file, because safety domains start winning ties they used to lose. Many legitimate
terms are single tokens (`syllabus`, `lecture`, `exam`). "Delete the noisy words" is
not the cure.

**But B alone is not the cure either.** Of the 6 files it newly recognises, **4 are
wrong**: `HW 9.pdf`, `Hw 5 .pdf`, `Linear HW.pdf` and `PHYS1401_PracticeFinalExam.pdf`
all come back `retail_hospitality`. Why:

```
HW 9.pdf   all terms: retail_hospitality:build@metadata
           metadata:field=Producer = 'iOS Version 18.5 (Build 22F76) Quartz PDFContext'
```

The only authored term on a physics homework is the word **"Build"** in its iOS PDF
producer string. Corroborate that and `retail_hospitality` (514 terms) wins a physics
assignment. (B is also an upper bound — it was simulated by treating every
observation as an identifier; real wiring would be narrower.)

### What this means for the fix

Neither half works alone and pruning is actively harmful. The vocabulary needs
**authoring** — terms that are discriminative and that a real file can carry — not
deletion, and not more of the prose rows that make up 38.9% of it. Getting from 5/18
to 18/18 is authoring work across 23 catalogues, and it is the owner's.

## 8. `NAMING_ZONES` includes `metadata`, and P4's `metadata` is not a title slot

`NAMING_ZONES`' docstring says `metadata` is "the format's own title slot, a document
naming itself in its own words." **That is false as implemented.** P4 emits the whole
metadata dictionary into one zone:

```
metadata:field=extension     '.pdf'
metadata:field=mime_type     'application/pdf'
metadata:field=CreationDate  "D:20251116232424Z00'00'"
metadata:field=Producer      'iOS Version 18.5 (Build 22F76) Quartz PDFContext'
```

So a toolchain string counts as *where the file names itself*, and a safety work type
appearing in one could raise a lock. No file in any corpus measured here is protected
that way, so nothing was changed — narrowing a protection surface needs a reason, and
an over-release is worse than an over-protection. Separating the title slot from the
producer slot is P4's to do; the docstring should not claim it until it is true.


---

## 9. `00`'s WORKED EXAMPLE NOW EXECUTES — three links, three different owners

`Syllabus BUSIB 4300 Spring 2026 Haran Segram.pdf`, measured:

| | outcome |
|---|---|
| as shipped | `Abstention no_corroboration academic` |
| + detector co-location fix (**landed**) | `Abstention no_corroboration academic` |
| + Door 1 filename identifiers (`cli.py`) | `Abstention no_corroboration academic` |
| **+ drop `valuation` and `sessions`** (vocabulary) | **`Recognition academic`** |

**All three are necessary and none is sufficient.** The links:

1. **The co-location refusal — mine, fixed.** The corroboration gate required the
   identifier to sit in "an observation NO term matched". On a real file the course
   code and the word `syllabus` are in the SAME observation, because the filename is
   where both are written. Now refused only when the term IS the whole observation,
   which is the self-corroboration case the rule was actually written for.
2. **Filename identifiers — `cli.py`, owed.** `_identifier_observations` filters on
   `STRUCTURED_EXTRACTOR` + a `text_span`; the structured pass is wired only into
   `macos_readers`. A code in a filename is never an identifier.
3. **Two junk terms — the owner's.** `construction_property:valuation` (a page-1
   heading) and `retail_hospitality:sessions` (a page-6 heading) tie with
   `academic:syllabus`, and a tie switches corroboration off. Removing exactly those
   two is what completes the chain.

**Measured effect of the landed fix alone: none.** live 5/18, Documents 111/413,
protection 2 — all identical to before. It cannot act until link 2 exists. It is
landed because it is correct and it is the prerequisite, not because it moves a
number today.

## 10. FILENAME CLASSIFIABILITY — 11 of 18 filenames match nothing

The filename is the one signal that never leaves the device
(`privacy.vocabulary.ALWAYS_LOCAL` holds `path` and `filename`), so only on-device
code can use it. Matching the shipped library against the 18 filenames alone:

```
COMS 1004 Homework #2 2.pdf                  academic:homework
COMS 1004 Quiz #2 Practice Questions.pdf     academic:quiz, clinical_practice:practice
Op Ed essay Final--Joseph Yung.pdf           academic:essay
Python Notes.pdf / class23-notes.pdf         academic:notes
Syllabus BUSIB 4300 Spring 2026 ….pdf        academic:syllabus
YAB-Executive-Board-FY25-Application….pdf    business_operations:board, career:board
HW 9.pdf  Hw 5 .pdf  Linear HW.pdf  hw9.pdf  NOTHING
PHYS1401_Lecture08/10/11 ….pdf               NOTHING
PHYS1401_PracticeFinalExam.pdf               NOTHING
exam2 2.pdf                                  NOTHING
UNC final application.pdf                    NOTHING
Rivooo_K12_Hong_Kong_Market_Analysis….docx   NOTHING
```

**11 of 18 match no authored term at all**, and the causes split cleanly:

- **`HW` is not an authored term.** `homework` is. The commonest abbreviation in
  student filenames matches nothing — four files. **Vocabulary, owner's.**
- **A letter/digit boundary is not a word boundary.** `_tokens` separates only on
  non-alphanumerics, so `Lecture08` is one token and `lecture` — which `00` names
  as academic context — cannot match. Same for `exam2`, `class23`.

A tokeniser change adding a letter↔digit boundary was written and **measured
neutral**: it gains `academic:lecture` on the three PHYS1401 lectures and
`academic:exam` on `exam2`, but those terms already matched in the body, so arity
does not move. live 5/18 unchanged; Documents 111 → 112; protection unchanged. Only
14 authored terms re-tokenise (`3d asset`, `409a …`, `id ed25519`, `option1`) and
`_tokens` is applied to both sides at `Detector.__init__`, so they still match. **Not
landed** — a correctness improvement with no measured benefit is not worth changing a
core primitive for. Recorded here so the decision is not lost.

## 11. THE `exam2` LOCK: the disciplinary-prose theory is WRONG

Tested against the shipped library rather than assumed:

```
'certify'       NOTHING      'honesty'                  NOTHING
'unauthorized'  NOTHING      'academic honesty'         NOTHING
'violation'     NOTHING      'academic honesty statement' NOTHING
'name'          NOTHING      'uni'                      NOTHING
'policy'        business_operations
'exam'          academic
'statement'     finance   <-- SAFETY DOMAIN
'total'         finance   <-- SAFETY DOMAIN
```

No safety domain matches any disciplinary or integrity word. The lock is caused by
exactly two ordinary English words in page-one headings — "Academic Honesty
**Statement**:" and "**Total** Points: 100" — giving `finance` two terms against
`academic`'s one. A disciplinary-prose filter would not touch it.

The prediction that every exam and syllabus with an integrity clause is at risk is
**right in outcome and wrong in mechanism**: the risk is the word "Statement", which
is §5's problem, and the 210-pair proof there says no rule separates it. Left locked;
an over-protection is the safe error and the owner now knows about it.

## 12. THE `subject` SLOT ON A NON-COURSE FILE — `cli.py`'s, with the evidence

`UNC final application.pdf` gets `subject = BMME398`. Located:

```
extractor=pdf.text  zone=body           span=3231-3239  raw='BMME 398'
extractor=pdf.text  zone=header_footer  span=3350-3358  raw='BMME 396'
```

A **body** mention, and the slot took it. The zone rule in `src/recognition/` governs
RECOGNITION and not this fact slot (`cli.text.identifier`, `cli.py:1172`), so it does
not and cannot fix this. The mention-vs-identity cut is available — the slot could
require a naming zone — but the slot is `cli.py`'s. **Owed, not fixed.**

## 13. THE LEVEL DIVIDER IS NOT COLLAPSING VALUES

`SELECT DISTINCT canonical_value FROM "values" WHERE field_key='subject'` on the live
run returns **four** distinct values — `BMME398`, `BUSIB4300`, `E1006`, `PHYS1401` —
across six files. The fact layer is not collapsing anything.

Only 6 of 18 files carry a `subject` fact at all, and fewer are classified and so
placeable, which is consistent with the divider correctly seeing few distinct values
among the files that reach it. **Direction of causality confirmed: downstream of the
classification rate, not a separate accuracy bug.** Stated with the limit that the
divider's own code was not read — it is not this package's.


---

## 14. THE EIGHT OPENED SENSITIVE FILES — the mechanism is vocabulary, not thresholds

**REFUTED: it is not `never_alone`/`no_corroboration`.** Run against the eight files'
own FULL extracted content (baseline DB, not filenames):

| file | observations | safety terms in content | safety WORK TYPES |
|---|---|---|---|
| `2025209423_Joseph_Yung_HKID.pdf` | 20 | **NONE** | NONE |
| `joseph Yung Vaccination Records.pdf` | **118** | **NONE** | NONE |
| `Covid -19 vaccination record (1).pdf` | 26 | **NONE** | NONE |
| `Covid- 19 booster.jpeg` | 6 | **NONE** | NONE |
| `Screenshot 2025-10-22 …png` | 8 | **NONE** | NONE |
| `DisplayMedicalRecord.pdf` | 4 | **NONE** | NONE |
| `148268M000 FUND Trading OTC商品交易授權書…pdf` | 13 | **NONE** | NONE |
| `eWelcome_Pack_TC_BOC_Credit_Card_TPA.zip` | 37 | `finance:credit` | **NONE** (context term) |

Seven of eight carry **zero safety signal in their entire content** — a vaccination
record with 118 observations matches nothing. This is not one signal waiting for a
second. `_precaution` did not fire because there was nothing to fire on: it requires a
safety WORK TYPE in evidence, and there is none.

### The vocabulary has no word for the commonest sensitive documents

```
'vaccination'    NO SCHEMA AUTHORS THIS      'medical record'  NO SCHEMA AUTHORS THIS
'vaccine'        NO SCHEMA AUTHORS THIS      'health record'   NO SCHEMA AUTHORS THIS
'immunisation'   NO SCHEMA AUTHORS THIS      'patient record'  NO SCHEMA AUTHORS THIS
'immunization'   medical  (US spelling only) 'credit card'     NO SCHEMA AUTHORS THIS
'hkid'           NO SCHEMA AUTHORS THIS      'bank statement'  NO SCHEMA AUTHORS THIS
'identity card'  NO SCHEMA AUTHORS THIS      'id card'         NO SCHEMA AUTHORS THIS
'national id'    NO SCHEMA AUTHORS THIS      'passport'        identity
```

**And the safety domains have the least usable vocabulary of all 23 schemas**, because
the prose-description problem is worst exactly there:

| schema | work types | prose-shaped (unmatchable) | usable |
|---|---|---|---|
| `legal` | 91 | 78 (**85%**) | **13** |
| `medical` | 63 | 41 (**65%**) | **22** |
| `finance` | 285 | 168 (58%) | 117 |
| `identity` | 70 | 26 (37%) | 44 — many are PEM key headers (`begin rsa private key`) |

The four domains `00`:52 says must be protected FIRST can match 13-117 things between
them, and none of those things is a vaccination record or an identity card.

### The proposed cure would not have saved one of these eight

Measured on `~/Documents` (413 files):

| protection rule | files protected |
|---|---|
| today | **2** |
| one safety work type **in a naming zone** | 1 |
| **one safety work type ANYWHERE** (the "single signal" proposal) | **36 (8% of the corpus)** |

Single-signal protection costs **34 additional false locks** on 413 files — the
33-file collapse returning — and protects **0 of the 8**, because 7 have no signal at
all and the 8th has only a context term (`credit`), which is the exact word that
locked two university syllabi out of "credit hours". **The thresholds are not the
disease.**

### Marked and opened are two different failures with two different owners

`orchestrator.run_p1_p7` calls `classify` AFTER `resolve_native` **in the same loop**
— `cli.py`:1685 states it: *"during the first pass EVERY file is unclassified"*. The
detector reads P4 observations, which exist only after the file has been read. **The
detector cannot prevent a file being opened and never could.** It can only mark.

- **NOT MARKED** is the detector's + the vocabulary's failure. Root cause above.
- **OPENED** is extraction running unconditionally before classification. Preventing
  it needs a pre-read rule on the one signal available before opening — the filename
  — at P3/scan. That is not this package and no change here can deliver it.

## 15. `metadata` REMOVED FROM `NAMING_ZONES` (landed) — and what it does NOT fix

Landed with the reason §8 lacked. P4 already routes real titles to their own zone:
`extractors/pdf.py`:135 is `zone="title" if slot in TITLE_SLOTS else "metadata"`, so
`metadata` is by construction everything that is NOT the document naming itself.
Measured, what lands there is `extension`, `mime_type`, `language`, `Producer`,
`CreationDate`, `ModDate`, `Creator`, `format`, `pixel dimensions`, `Trapped`.

Test: a PDF written by "Statement Printer 3.0" was sealed
`sensitive_personal, protected=True`. It no longer is. `title` still protects, which
is the half that must not be lost.

**It does NOT unblock filename identifiers, and the expectation that it would is
wrong.** Recognition does not read zones at all — `TermMatch.zone`'s own docstring
says so — so `retail_hospitality:build` still nominates from a producer string.
Re-measured after landing: live 5/18 and Documents 111/413 under shipped wiring,
6/18 and 109/413 under variant B — unchanged, and `PHYS1401_PracticeFinalExam.pdf` is
still `retail_hospitality`.

**The real size of that problem:** **10 of the 18 live files** carry a term matched
ONLY from a toolchain metadata field, every one of them `retail_hospitality:build`
out of `iOS Version 18.5 (Build 22F76) Quartz PDFContext`. On Documents it is 16 of
413 (`construction_property:sheet` 8, `retail_hospitality:build` 5).

Fixing it means recognition ignoring toolchain metadata fields. There is a precedent
in this module — `_matches` already refuses `locator == "path"` because a directory
name is not the file's own words, and a producer string is the same category — but it
needs a list of field names, which is authored vocabulary. **Proposed, not taken.**


---

## 16. IF THE OWNER AUTHORS `HW`: what it fixes, and what it does not

Derived from the per-file evidence already recorded in §7 and §15, **not from a fresh
run** — the machine was reserved for speed measurement when this was written, so it
needs one confirming run.

The four `HW` files, with every authored term they currently carry:

| file | terms today | leader |
|---|---|---|
| `HW 9.pdf` | `retail_hospitality:build@metadata` — that is ALL | retail_hospitality |
| `Hw 5 .pdf` | `retail_hospitality:build@metadata` — that is ALL | retail_hospitality |
| `Linear HW.pdf` | `retail_hospitality:build@metadata` — that is ALL | retail_hospitality |
| `hw9.pdf` | one `academic` term (from content) | academic |

**Authoring `HW` alone fixes none of the four**, and the reason differs per file:

- `HW 9.pdf`, `Hw 5 .pdf`, `Linear HW.pdf` — `academic:hw` would make it **1 term
  against `build`'s 1**. A tie. `never_alone` refuses, and the tie also switches off
  the corroboration branch (§9 link 3). Adding a word to the vocabulary turns a wrong
  answer into an ambiguous one, which is better but is not a classification.
- Remove `build` as well and they carry **one term and nothing else** — still
  `no_corroboration`. There is no second signal available: `_STRUCTURED` needs three
  or more digits, so `HW 9` and `Hw 5` carry no course code either.

**`hw9.pdf` is the one that flips, and only WITH the tokeniser change.** It already
has one `academic` term from its content. `hw9` is a single token today, so `hw`
cannot match; with a letter/digit boundary the filename yields `hw`, `9`, giving
`academic` a **second distinct term** and an outright win.

**So the answer to "does the letter/digit boundary start to matter once `HW` is
authored" is yes, but narrowly** — it is what makes a filename-only abbreviation
reachable at all when the digit is fused to it (`hw9`, `exam2`, `Lecture08`,
`class23`). It converts terms that are *present but unreadable* into evidence. It
does not create the second signal these files need.

**The general shape, which matters more than the four files:** a filename carrying
ONE work word and no course code cannot be classified deterministically, however good
the vocabulary gets, because `never_alone` requires two signals and a short filename
has one. That is not a defect to fix — it is the honest floor of a rule that refuses
to guess. Those files need the declared situation, a user answer, or the model.


---

## 17. CORRECTION TO §14 — how much of it survives a starved baseline

The baseline DB §14 used was retired as stale: PDFs carried little or no body
evidence when it was built. Checked, per file, in that same DB
(`zone` counts and total characters of text-bearing evidence):

| file | text-bearing observations | chars |
|---|---|---|
| `DisplayMedicalRecord.pdf` | **0** — filename, path, metadata only | **0** |
| `Covid- 19 booster.jpeg` | **0** | **0** |
| `Screenshot 2025-10-22 …png` | 1 (ocr) | **8** |
| `148268M000 FUND Trading OTC…pdf` | 7 | 72 |
| `2025209423_Joseph_Yung_HKID.pdf` | 13 | 241 |
| `Covid -19 vaccination record (1).pdf` | 20 | 270 |
| `joseph Yung Vaccination Records.pdf` | 110 | 1,685 |
| `eWelcome_Pack_TC_BOC_Credit_Card_TPA.zip` | 31 (manifest) | — |

**So §14's sentence "seven of eight carry zero safety signal in their entire
content" is NOT SAFE and is withdrawn as stated.** Two files had no text at all and
a third had eight characters: for those the detector was **starved**, not
out-vocabulary. The rest carried 72-1,685 characters, which is a fragment of a real
document, and the lead's own run reports higher counts (32 text units for the HKID,
122 for the vaccination records) than this DB holds — so this DB is a thinner
extraction than what now exists.

### What survives, because it never depended on extraction

1. **The vocabulary gap.** Measured against the shipped library, not any database:
   `vaccination`, `vaccine`, `immunisation`, `hkid`, `identity card`, `id card`,
   `national id`, `medical record`, `health record`, `patient record`,
   `credit card`, `bank statement` are authored by **no schema**, and only the US
   `immunization` exists. Unchanged.
2. **The FILENAME result.** A filename is always present and never starved.
   **Seven of the eight filenames match no safety term** — including
   `joseph Yung Vaccination Records.pdf`, whose name says what it is in plain
   English. This is extraction-independent and it is the stronger half.
3. **The prose-shape measurement:** `legal` 85%, `medical` 65% of work types
   unmatchable. Library-only.
4. **The +34 false locks** from single-signal protection: measured on `~/Documents`,
   a different corpus that was not starved.

### What is now conditional and needs the re-baseline

**"The single-signal proposal saves 0 of 8."** That conclusion rested on the files
carrying no safety term, and for two or three of them the truth is that they carried
nothing at all. If full prose changes the term picture, the count could change.

My prediction, recorded now so it is falsifiable: **it will not change much**, because
the missing words are the ones a vaccination record actually contains — a Hong Kong
record says "vaccination" or "immunisation", and neither is authored. But that is a
prediction, not a measurement, and the re-baseline is what decides it.


---

## 18. CORRECTION TO §16 — the `HW` analysis rests on starved evidence too

Same check as §17, applied to `live.sqlite`, which I built tonight with current code:

| file | size on disk | text-bearing observations | chars |
|---|---|---|---|
| `HW 9.pdf` | 937 KB | **0** | **0** |
| `Hw 5 .pdf` | 1.0 MB | **0** | **0** |
| `Linear HW.pdf` | 2.0 MB | **0** | **0** |
| `hw9.pdf` | 92 KB | 1 | **10** |
| `exam2 2.pdf` | 82 KB | 10 | 135 |
| `PHYS1401_Lecture08_Template.pdf` | 313 KB | 27 | 517 |

**Three multi-megabyte PDFs produced ZERO text.** Their only zones are `filename`,
`path` and `metadata`. So §16's premise — "`HW 9.pdf` carries
`retail_hospitality:build@metadata` and NOTHING else" — is true of the database and
**false as a statement about the file**. The detector never saw a word of it.

### What §16 got right, and what is withdrawn

**Withdrawn:** that authoring `HW` leaves these three files at a 1-1 tie with `build`.
That followed only from their carrying no other term, which is starvation. Once they
are read they may carry several academic terms, in which case `HW` is unnecessary for
them and they classify on content alone.

**Stands, because it is arithmetic and not evidence:** a file whose ONLY signal is one
work word in its filename, with no course code, cannot be classified deterministically
— `never_alone` requires two signals and one word is one signal. That is a property of
the rule. What is NOT established is that these four files are examples of it.

**Stands:** `hw9` is a single token, so `hw` cannot match it without a letter/digit
boundary. That is tokeniser arithmetic and no amount of extraction changes it.

### The finding this turns into, which is bigger than `HW`

**Three PDFs of 937 KB, 1.0 MB and 2.0 MB yielded no text at all.** That is not a
recognition defect and not a vocabulary gap — it is extraction. Most likely they are
scanned or image-only PDFs whose text needs OCR. On the live 18 that is 3 files, and
the classification rate cannot rise above the extraction rate: a file the detector is
handed nothing about is a file it must abstain on, correctly.

**This is owed to whoever owns extraction, not to the owner as authoring work.**
