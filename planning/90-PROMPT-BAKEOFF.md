# 90 — The A_fact prompt, four candidates, measured

Date: 2026-09-02. Companion to [`82-FACT-PROMPT-DRAFT.md`](82-FACT-PROMPT-DRAFT.md) (the incumbent
text), [`76-PROMPT-RESEARCH.md`](76-PROMPT-RESEARCH.md) (the requirements) and
[`86-PROMPT-STRESS-RESULTS.md`](86-PROMPT-STRESS-RESULTS.md) (the fifteen, run).

**Nothing here is installed and nothing here is approved.** No `PromptDefinition` is constructed
anywhere in this work. `src/` is untouched. The one thing that landed is a test file
(`tests/p8/test_p8_glossary_as_value_source.py`, `60b7709`), which constructs no prompt and calls
no model. **No API call was made to any provider.** An agent may not author or adopt prompt text;
C1, C2 and C3 below are drafts prepared so the owner has alternatives to choose between, and the
choosing is his.

---

## 1. Read this before the tables: what a bake-off can and cannot measure here

`llm_harness.sites.dispatch` **never sees the prompt bytes**. A response is judged against the
dossier, the allowlist and this deployment's oracles, and against nothing that asked for it. So:

> **No candidate below changes a single `(outcome, reasons)` pair in the fifteen stress cases, or in
> the sixteenth this work adds.** A bake-off scored on the stress harness would rank every candidate
> identically, and reporting that as a result would be theatre.

`86` §1 is what makes this concrete: twelve of the fifteen are machine-defended, so for twelve the
prompt is belt-and-braces and any candidate scores the same. The two that are prompt-only — S1, S2 —
are prompt-only precisely *because* the machine is blind there, which means the machine cannot rank
two prompts on them either. **The cases where a bake-off would discriminate are exactly the cases
where nothing offline can discriminate.**

What does vary with the bytes, and is therefore what was measured:

| | |
|---|---|
| **Conformance** | Byte-level invariants traceable to `76` §6 and `82` §5.6, checked against `dossier._body`'s **source** and the **live** field catalogue, never against a count quoted in a document. (The source, not `_body`'s output: calling it needs a `PromptDefinition`, and constructing one is the line this work does not cross.) |
| **Shape executability** | The JSON objects a candidate *shows the model*, pulled out of its own bytes, instantiated with real values from a real Site A world, and run through the real dispatcher. A candidate that demonstrates a shape the machine rejects has taught the model to fail, and `76` R16 prices that at the whole response. |
| **Size, and overlap** | Bytes, words, and which glossary-enumerated value words appear in the template. |

What was **not** measured, and cannot be without a model: whether a model obeys any of it. The
recommendation in §6 rests on an argument, not on a score, and §6 says which argument.

**Where the harness lives.** `…/scratchpad/bakeoff/score.py` and `…/bakeoff/candidates/`. It is a
scratchpad tool, not a repo test, because it reads candidate bytes and candidate bytes are not the
project's to hold. Every check it makes is listed in §4 with its requirement, so it is reproducible
from this document alone.

---

## 2. The sixteenth case: a value lifted out of the glossary

`82` §4 closes with *"the fifteen do not cover the surface v3 opens"* and §7.1 calls it the draft's
most arguable line **because it is the newest and least tested**: *"There is no stress case for this
and no test."* There is now. `tests/p8/test_p8_glossary_as_value_source.py`, 29 tests, all passing,
by `76` §10.3's method — recorded response bytes plus an expected pair, through the real dispatcher,
no model.

### 2.1 The hazard, counted

Five glossary entries define a field by **listing what goes in it**. Between them they enumerate
**22 words**:

| field | schemas that carry it | words enumerated |
|---|---|---|
| `media_type` | photos | photo, screenshot, scan, video |
| `application_document_type` | college_applications | essay, transcript, form, portal record |
| `site` | logistics, manufacturing, resource_operations, retail_hospitality | plant, works, depot, store, field |
| `supplier` | business_operations, logistics | Carrier, Haulier, Forwarder, Shipping Line, Airline |
| `issuing_body` | business_operations | regulator, examining board, licensing authority, certifying body |

**22 of 22 survive check 3.** `normalize_for_model(field, word)` returns every one of them unchanged
— which is not a surprise given `82` §5.5, but it had not been measured for these fields and is now.

**22 of 22 are accepted as values.** Each test builds a real world whose released evidence is
`"Prepared by the office in the autumn and filed under reference 88."` — prose containing none of
the 22 words — and sends a claim that cites the real span `"the office"` and proposes the glossary
word. Check 1 passes (the field is in `allowed_vocabulary`, from P6's own `build_request`). Check 2
passes (the span is copied exactly). Check 3 passes. Check 4 passes. **`accept_direct`, no reasons.**

The control — decline, which is what `82` §2 directs — returns `abstain`. The two responses are one
word apart and the machine ranks them equally well.

`test_s16_the_lifted_value_becomes_a_real_llm_supported_fact` runs the consequence and reads P6's
table back: `media_type = "screenshot"`, `active`, `llm_supported`, for a file whose evidence never
used the word, on the strength of a citation about an office.

### 2.2 Two findings the case produced that were not asked for

**S16 is indiscriminable the way S1 is.** `86` §1 records that S1's correct minimal answer and its
over-quoted one produce the identical pair. So do a lifted `"screenshot"` and a genuinely found one:
`test_s16_is_indiscriminable_the_way_s1_is` asserts the two `_judge` results are equal. This is
sharper than "unchecked". Several of the 22 are ordinary English — *form*, *field*, *store*, *scan*
— and will legitimately appear in real released text, so **even a check that compared the value to
the glossary could not separate a lift from a find.** The only check that could is one comparing the
value to the *released evidence*, which is §5's R22.

**The draft's answering sentence has one half machine-backed and one half not.** `82` §3's fourth
bullet asserts *"A quoted span from the glossary is caught (`CITATION_SPAN_MISMATCH`); a value is
not caught by anything."* Verified rather than asserted:
`test_a_glossary_sentence_quoted_as_a_span_is_caught` cites the glossary's own words as a span and
gets `CITATION_SPAN_MISMATCH`. So of C0's sentence —

> *"It is a definition and it is not evidence: nothing written in it may be quoted, and a word that
> appears only there is not a value you found."*

— the first clause restates something the machine already enforces, and **the second clause is the
whole of the defence.** They sit on opposite sides of the seam inside one sentence. That is the
single most useful thing this work found about the incumbent text, and it is what §6's
recommendation turns on.

### 2.3 The prompt-only set is now three, and S16 is not a variant of the other two

`86` §1's split stands for the fifteen and this work did not touch it. Alongside it:

| case | the value's relationship to the evidence | where the plausible word came from |
|---|---|---|
| S1 | contains the right characters **plus more** | the released evidence itself |
| S2 | **none** | the model's own head |
| S16 | **none** | **the dossier, which supplied it** |

S16 is the easiest of the three for a model to fall into, because it is the only one where the
system hands the model the word. That is the cost side of the owner's `76` §10.1 ruling, stated as a
measurement rather than as a worry — and it does **not** argue against the ruling: `82` §4's S5 row
is the coverage the ruling bought, and nothing here weakens it.

### 2.4 The per-call glossary cost, which `82` §7.3 said the owner never saw

Measured across all 23 schemas, single-schema activation, universal fields included:

| | |
|---|---|
| fields per call | 10 (the four field-less schemas) to 17 (photos) |
| `field_glossary` bytes per call | **970 to 1,791**, compact JSON |
| schemas exposing at least one enumerating entry | **7 of 23** |

Against 7,289 bytes of prompt, the glossary is 13–25% again per call. A file activating several
schemas carries the union, so these are floors, not ceilings. `82` §7.3's judgement — that cutting
prompt words to pay for glossary words would cut the S1 defences first — is unaffected; the numbers
are recorded because the ruling was made about coverage and this is the other column.

---

## 3. The candidates

All four are the same document with the same 21 requirements behind them. **C0 is `82` §2 exactly**,
extracted from the fenced block programmatically; the extraction reproduces `82`'s own count of
7,289 bytes / 1,226 words, which is how it is known to be faithful.

C1, C2 and C3 vary **only** the three doubts `82` §7.1 raises against itself, which is where `82`
asks to be disagreed with. Nothing else moves — not §7.2's abstract example, not §7.4's unbounded
rule 9, both of which `82` reasons about and settles. Every candidate is a stated delta from C0, so
the resulting bytes are fully determined by `82` §2 plus the delta.

| | delta from C0 | bytes | words | sha256 |
|---|---|---|---|---|
| **C0** | — the incumbent | 7,289 | 1,226 | `e4f92fba…c547` |
| **C1** | + a twelfth numbered rule | 7,560 | 1,277 | `9aabe356…c2f8` |
| **C2** | the glossary sentence reworded | 7,349 | 1,242 | `e4fe6d12…ae10` |
| **C3** | both | 7,620 | 1,293 | `dddb2ae6…b9e9` |
| *X1* | *negative control — not a candidate* | 7,442 | 1,238 | `a5f0ca4f…a369` |

**C1's delta** — inserted after rule 11, as rule 12 (§7.1 doubt 3: the sentence is in the dossier
description, where a model scanning the rules does not meet it; and doubt 1: one sentence against
55 sentences of vocabulary):

~~~~
12. "field_glossary" tells you what a key means. It never tells you what this file's value is. If the characters you want to propose appear in a glossary entry and in no released value, that is not a value you found, and proposing it is the same error as inventing one.
~~~~

**C2's delta** — the sentence in `WHAT THE DOSSIER CONTAINS` replaced (§7.1 doubt 2: whether *"nothing
written in it may be quoted"* invites a model to under-use the glossary and hand back the S5
coverage the ruling bought). From:

~~~~
It is a definition and it is not evidence: nothing written in it may be quoted, and a word that appears only there is not a value you found.
~~~~

to:

~~~~
Read it to work out which key names the thing you found. It is a definition and it is not evidence, so no part of it may be cited as a span and a word that appears only there is not a value you found.
~~~~

C2 separates three instructions that C0 carries in one: **use it** to pick the key, **never cite it**
as a span (the half the machine already enforces — §2.2), **never lift a value** from it (the half
that is the whole defence). C0's *"nothing written in it may be quoted"* is the sentence's weakest
word, because "quoted" is the thing the machine catches and is not the thing that happens in S16.

**C3** is C1's rule 12 and C2's rewording together.

**X1 is a negative control and is not a candidate.** It is C0 with four deliberate injuries — a code
fence in `OUTPUT`, a concrete worked example naming `"subject"` and `"PHYS1401"`, a date and a
provider name in the first line, and a shape carrying both `cited_span` and `metadata_field_name`.
It exists for the same reason `86` mutated six expectations: a scorer that has never failed anything
is not known to be able to.

---

## 4. The conformance table

Every check, its requirement, and the result. `PASS`/`FAIL` are the scorer's, run 2026-09-02.

Twenty-two checks run; the table collapses the eight literal-phrase checks into four rows.

| check | requirement | C0 | C1 | C2 | C3 | *X1* |
|---|---|---|---|---|---|---|
| ends with exactly one newline, no trailing space | R1 | PASS | PASS | PASS | PASS | PASS |
| one line names all **14** of `_body`'s keys | R2 | PASS | PASS | PASS | PASS | PASS |
| that line lists them in sorted order | R2 | PASS | PASS | PASS | PASS | PASS |
| quotes no snake_case key the dossier does not carry | R2 | PASS | PASS | PASS | PASS | PASS |
| contains no backtick | R15 | PASS | PASS | PASS | PASS | **FAIL** |
| contains nothing that varies between runs | R17 | PASS | PASS | PASS | PASS | **FAIL** |
| quotes no catalogue field key | R18 | PASS | PASS | PASS | PASS | **FAIL** |
| names no provider, model or tier | `82` §5.6 | PASS | PASS | PASS | PASS | **FAIL** |
| states "exactly one", both citation key names, `why_it_supports` | R4 | PASS | PASS | PASS | PASS | PASS |
| states `insufficiency_statement` | R13 | PASS | PASS | PASS | PASS | PASS |
| states `"unknown": false` and `null` | R14 | PASS | PASS | PASS | PASS | PASS |
| states "costs nothing" | R19 | PASS | PASS | PASS | PASS | PASS |
| shows at least two shapes; each parses as JSON | shape | PASS | PASS | PASS | PASS | PASS |
| **support shape, instantiated, is `accept_direct`** | shape | PASS | PASS | PASS | PASS | **FAIL** |
| **decline shape, instantiated, is `abstain`** | shape | PASS | PASS | PASS | PASS | PASS |
| | **failures** | **0** | **0** | **0** | **0** | *5* |

**The four candidates tie: 22 checks each, zero failures each.** X1 fails five, including the shape check, which comes
back `(('reject', ('SCHEMA_INVALID',)),)` — a template that demonstrated that shape would cost the
whole response every time a model copied it. So the scorer discriminates; it just does not
discriminate *these four*, and that is the honest result rather than a failure of the harness.

Two things the scorer establishes about C0 that were previously assertions:

- `_body`'s key set is **fourteen**, read out of `dossier.py:172-194` by the scorer rather than
  taken from a document, and C0 names all fourteen in sorted order on one line. `82` §5.8's
  correction to `76` R2's "twelve" is confirmed against the module.
- **C0's two shown shapes both execute.** Instantiated with real values against a real world, the
  support shape is `accept_direct` and the decline shape is `abstain`. `claim_ref` is absent from
  both and that is safe — `validation.py:325-329` defaults it to `claim-<index>`.

### 4.1 Structural facts, reported and deliberately not scored

Where a sentence sits is measurable; it is not evidence, and putting it in a scored column would
make it look like measurement. So:

| | C0 | C1 | C2 | C3 |
|---|---|---|---|---|
| numbered rules | 11 | 12 | 11 | 12 |
| a value-binding directive is reachable inside `THE RULES` | no | **yes** | no | **yes** |
| the glossary sentence separates "use it" from "do not lift from it" | no | no | **yes** | **yes** |
| glossary-enumerated words appearing in the template itself | `field`, `form` | same | same | same |

That last row is a curiosity worth one line and no more: the word *field* appears throughout every
candidate meaning a schema field, and it is also one of `site`'s five enumerated values; *form*
appears once and is one of `application_document_type`'s. Measured because it is measurable. There
is no mechanism by which either would become a value, and it is not a reason to prefer any candidate.

---

## 5. What a prompt cannot fix, stated before the recommendation

`86` §4 found that **the proposed `value` is never compared to the citation or to any released
text**, and `82` §3 records it as owed back to `76` as a 22nd requirement. This work does not narrow
that; it widens it. **All four candidates leave all 22 glossary lifts accepted.** Every one of them
still produces `media_type = "screenshot"` as an active `llm_supported` fact on a citation about an
office.

So the honest ranking of what would help, in order:

1. **A check comparing `payload.value` to the released text it cites.** Not a prompt change. It
   ~~would close S2 and S16 outright and~~ **closes S16 and** narrows S1 to the over-quotation case,
   which is what R11 is for. Nothing in `src/` does this and no wording substitutes for it.

   > **Correction, 2026-09-02.** The struck words were wrong and this document said them without
   > measuring them. **The check does not close S2.** S2's value is `"the committee"` over released
   > prose reading *"Prepared for the committee in the autumn, with notes."* — the characters ARE in
   > the cited text, so any comparison of characters grounds it. What is wrong with S2 is that a
   > committee is not an instructor, which is a judgement about meaning and is invisible to this
   > check or to any other one built on text. **S2 remains prompt-only.**
   >
   > The check was built, and the corrected claim is: **closes S16, narrows S1 to over-quotation,
   > leaves S2 prompt-only.** `tests/p8/test_p8_prompt_stress_cases.py::test_the_value_is_now_
   > compared_to_the_evidence_it_cites_and_s2_survives_it` asserts both halves rather than either.
   >
   > Two further corrections this document owes, from the same work:
   >
   > - §2.2's *"even a check that compared the value to the glossary could not separate a lift from
   >   a find"* generalises correctly to the check that was built. Where an enumerated word also
   >   appears in the cited released text, a lift and a find are byte-identical and both are
   >   accepted. **The check narrows S16 rather than closing it**, and
   >   `test_a_lift_and_a_find_stay_indiscriminable_when_the_word_IS_in_the_evidence` pins that.
   > - §6's *"What would change this recommendation"* holds, with one qualification. With the check
   >   landed, S16 is machine-defended and `82` §2's sentence becomes belt-and-braces for it — but
   >   **S1 and S2 stay prompt-only either way**, so the argument for prominence weakens rather than
   >   disappears. The order still matters more than the choice, and the check has now gone first.
2. **R22, worded to survive the glossary.** `76` R3 says *"the only quotable text is
   `released_evidence[].value"*, written when released evidence was the dossier's only prose. It is
   now not. R22 should be worded as *the value's characters must come from a released value*, and
   should say explicitly that the glossary is not one — otherwise a future reader will notice the
   glossary is inside the dossier and reason that it counts.
3. **Then, and only then, the prompt.** Which of C0–C3 is chosen matters less than either of the
   above, and this document would be misleading if it implied otherwise.

`76` §9.1, §9.2 and §9.3 are untouched by all of this and all three remain open.

**Item 1 was built on 2026-09-02.** `src/llm_harness/value_grounding.py`, wired at Site A behind
`VALUE_NOT_IN_CITED_TEXT` — a fourth Site A reason code, added with the owner's approval recorded at
the member. All 22 of §2.1's glossary lifts are refused; no legitimate value in the suite is. The
check also refused something this document did not anticipate: the product's own walking skeleton
proved its accept path with a claim that proposed the text P7's gate had redacted, cited to the span
`[redacted]`, and that had been an active `llm_supported` fact.

---

## 6. Recommendation: C3. The deciding factor is placement, not volume

**Recommended: C3.** With the caveat that the recommendation rests on an argument, because §1 says
no score is available, and the argument is this:

**Neither delta adds a policy.** C1's rule 12 restates, inside `THE RULES`, a claim C0 already makes
in `WHAT THE DOSSIER CONTAINS`. C2 splits a sentence that currently carries three instructions into
three that do not pull against each other. Ratifying C3 commits the owner to nothing he has not
already committed to by shipping the glossary and by `82` §2's existing sentence. That matters
because `82` §6 is right that these bytes are a one-way door: a delta that adds a *position* is
recoverable reasoning; a delta that adds a *rule* is a new permanent policy, and neither of these is.

**The deciding factor is §2.2.** C0's answering sentence has two clauses, and the first
(*"nothing written in it may be quoted"*) is the one the machine already enforces —
`CITATION_SPAN_MISMATCH`, now pinned by a test. The second clause is the entire defence and it is
the subordinate half of a sentence in a descriptive paragraph. **The load-bearing half of the
load-bearing sentence is the least prominent thing in it.** C2 fixes that inside the sentence; C1
puts it where a model reading eleven numbered rules will meet it; C3 does both. Against a hazard
that `86` §1's method cannot see at all, prominence is the only lever the text has.

**And S16 is the case that most deserves it.** Of the three prompt-only cases, S16 is the one where
the *system itself* supplies the plausible word — 22 of them, and 7 of 23 schemas carry at least one
enumerating entry. `82` §5.7 argues that at the routed tier the defences against confident over-reach
are the ones carrying the weight and the formatting defences are cheap insurance. S16 is that same
failure class with the system helping, so the same argument applies with more force, and +331 bytes
(4.5%) is the cheaper half of the trade.

**What would change this recommendation.** If check 1 in §5 is written first, C0 becomes the right
answer: the machine would then defend S16, the sentence would become belt-and-braces like the twelve
machine-defended cases, and `82` §6.7's argument for the shortest ratifiable text would win
unopposed. **The order matters more than the choice.**

---

## 7. What I am not sure about

Stated plainly, because a document that recommends without this is worth less.

1. **Whether a model does any of this.** Nobody has observed a glossary lift. S16 proves the machine
   would not catch one, not that one happens. `82` §7.7's line still stands over all of §6: this is
   what the draft *directs*, never what a model was observed to do.
2. **Whether rule 12 helps or dilutes.** `82` §7.4 warns that explaining every key invites a model to
   consider every key, and each considered field is an INSERT into `unresolved`. A twelfth rule about
   the glossary may pull attention the same way. I cannot tell, and it is the weakest part of the C3
   recommendation. **If the owner wants one delta rather than two, take C2** — it is 60 bytes, it
   changes no policy, and it fixes the clause-order problem §2.2 measured, which is the finding I am
   most confident in.
3. **Whether C2's opening — *"Read it to work out which key names the thing you found"* — could be
   read as licence to infer a key from the glossary rather than to match one.** That would be S5
   inverted. C0's wording does not have this exposure because it does not invite use at all; C0 pays
   for that with §7.1 doubt 2. This is a real trade and I have not measured either side.
4. **Whether the 22-word count is the whole hazard.** Five entries enumerate values because I read 55
   sentences and judged which ones do. A sixth that enumerates less obviously would not be in the
   list. The test re-reads the shipped glossary and fails if a listed word leaves an entry, but
   nothing detects an entry that *starts* enumerating.
5. **Whether the conformance tie means the candidates are equivalent or the checks are too coarse.**
   I believe the former — the checks are the requirements, and four candidates that all satisfy 21
   requirements *should* tie — but a scorer that passes everything it is shown except a control I
   built to fail is a scorer whose sensitivity is unknown in the middle of the range.

---

## 8. What landed, and what did not

**Landed:** `tests/p8/test_p8_glossary_as_value_source.py` (`60b7709`) — 29 tests, all passing;
`tests/p8` 612 passing. It constructs no `PromptDefinition`, calls no model, and adds no case to
`test_p8_prompt_stress_cases.py`'s fifteen, whose `PROMPT_ONLY == {"S1", "S2"}` assertion is a claim
about `86` and stays true.

**Did not land, deliberately:** the scorer and the candidate bytes. They live in the session
scratchpad. Candidate bytes in the repository would be prompt text sitting in the project, which is
the thing `82` §1 is careful not to do, and a scorer in `tests/` would be a repo test whose subject
is a file that does not exist.

**Owed back:** `76` gains **R22** (the value's characters must come from a released value; the
glossary is not one) and a **sixteenth stress case** in §7. Both are the owner's to accept; this
document records them as owed rather than writing them into `76`.
