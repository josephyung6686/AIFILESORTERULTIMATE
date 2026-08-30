# 86 — The fifteen stress cases, run against the real validator

Date: 2026-08-31. Companion to [`76-PROMPT-RESEARCH.md`](76-PROMPT-RESEARCH.md) §7 (the cases) and
[`82-FACT-PROMPT-DRAFT.md`](82-FACT-PROMPT-DRAFT.md) §4 (what the draft predicts each produces).

`82` §7.7 admits that nothing in it was validated against a live model. `76` §10.3 records that it
does not have to be: all fifteen can be written as recorded response bytes plus an expected
`(outcome, reasons)` pair and run against the real validator with no model at all. That is what was
run.

**Suite:** `tests/p8/test_p8_prompt_stress_cases.py` — 22 tests, all passing. Every case goes
through `llm_harness.sites.dispatch` at `A_FACT` over a real P1 file, a real P4 observation, P6's own
`build_request`, and this deployment's own oracles (`cli.normalize_for_model`,
`cli.contradicts_stronger`). **No `PromptDefinition` is constructed and no model is called.** `82` is
unedited.

**What this does not answer.** Not "does the prompt work" — that needs a model. It answers the
sharper question: for each of the fifteen, does the MACHINE catch the wrong answer, or is the
PROMPT the only defence?

**Method note.** Every case carries a *control*: the near-identical response that produces the other
outcome. Fourteen of the fifteen are discriminating — swap the two expectations and the assertion
fails. S1 is not, and that is the finding rather than a gap in the test. Six expectations were also
mutated deliberately and all six failed, so the suite is not fifteen assertions that would pass
against any implementation.

---

## 1. The table

`Defence` is the deliverable. **machine** = the validator rejects the wrong answer on its own.
**prompt-only** = the wrong answer is `ACCEPT_DIRECT` and an `llm_supported` fact is written.
**neither** = the model answers correctly, the verdict is right, and the damage happens after it.

| # | What it tests | Observed verdict for the wrong answer | Defence |
|---|---|---|---|
| S1 | The whole released line proposed as the value (`"PHYS1401 Problem Set 4"` for `subject`) | `accept_direct`, no reasons — **and the correct minimal answer produces the identical pair** | **prompt-only** |
| S2 | A plausible value invented over prose that supports nothing | `accept_direct`, no reasons | **prompt-only** |
| S3 | Two claims about one field | `reject` / `SCHEMA_INVALID`, one verdict for the whole response | machine |
| S4 | A quotation in the store's raw text but not in any released `value` | `reject` / `CITATION_SPAN_MISMATCH` | machine |
| S5 | A field key outside `allowed_vocabulary` (`course_code`) | `reject` / `FIELD_NOT_IN_ACTIVE_SCHEMA` | machine |
| S6 | A second spelling of a value a stronger `direct` fact already carries | `accept_direct` — check 4 correctly does **not** fire | **neither** |
| S7 | A term proposed as a subject (`"Spring 2026"` for `subject`) | `reject` / `VALUE_NOT_NORMALIZABLE` | machine |
| S8 | A fluent quotation that is in no released value | `reject` / `CITATION_SPAN_MISMATCH` | machine |
| S9 | An `evidence_ref` in `evidence_items` with nothing released for it | `reject` / `CITATION_NOT_IN_DOSSIER` | machine |
| S10 | Both `cited_span` and `metadata_field_name` filled | `reject` / `SCHEMA_INVALID`, whole response | machine |
| S11 | `{"claims": []}` instead of an abstention | `reject` / `SCHEMA_INVALID` | machine |
| S12 | A preamble and a code fence around the JSON | `reject` / `SCHEMA_INVALID` | machine |
| S13 | `"unknown": false` alongside a real claim | `reject` / `SCHEMA_INVALID`, whole response | machine |
| S14 | A metadata citation whose field name is retyped rather than copied | `reject` / `CITATION_SPAN_MISMATCH` | machine |
| S15 | `"value": 2026` — a number, not a JSON string | `reject` / `VALUE_NOT_NORMALIZABLE` | machine |

**Twelve machine, two prompt-only, one neither.** Every reason `76` §7 predicted was the reason
observed. The fifteen behave exactly as `76` says they do; nothing in the research document was
found to be wrong.

---

## 2. The two lines of the draft that are the entire defence

These are the lines to read hardest before ratifying, because for S1 and S2 nothing downstream will
catch the model getting them wrong: the answer is stored as an `llm_supported` fact, and
`test_s1_the_over_quoted_value_becomes_a_real_llm_supported_fact` reads that row back out of P6's
own table to prove it.

**S1 — `82` §2 rule 4, in full:**

> *"The value is the smallest run of characters that identifies the thing, not the phrase that
> contains it. If a released value reads "A B C" and only "A" identifies the field, then the value is
> "A" and not "A B C". Everything you carry across beyond the identifying part becomes part of the
> recorded answer and is wrong."*

and the sentence added for it:

> *"A value you worked out is not a value you found."*

Nothing else stands between a model and a folder named `PHYS1401 Problem Set 4`. Confirmed live:
`normalize_for_model('subject', 'PHYS1401 Problem Set 4')` returns the string unchanged, and
`normalize_for_model('subject', 'a' * 300)` returns 300 characters.

**S2 — the two-moves section and rule 7:**

> *"If you cannot cite evidence that already exists in `released_evidence`, you must decline."*
>
> *"…if the sentence has to do work the evidence does not do, decline the field instead."*
>
> *"Declining is a correct answer and it is recorded as one. It costs nothing. … When the two are
> close, decline."*

Rule 2 (decline any field whose meaning is not plain from its key) is load-bearing here too, which
is why `82` §5.1 is right to call it the item most worth the owner's disagreement: it is not a
stylistic choice, it is one of the two defences for a case with no other.

---

## 3. `82` §3's three not-fully-satisfied requirements, checked live

| Req | `82` §3 says | Confirmed? |
|---|---|---|
| **R6** | Half. The first clause is stated; the second — the coarse check against P6's observations for this file version — is invisible to the model. | **Confirmed, and it is stricter than `82` implies.** The coarse check is not just unforeseeable, it runs *first*: a key P6 never observed comes back `CITATION_NOT_FOUND`, not `CITATION_NOT_IN_DOSSIER` (`test_a_fabricated_evidence_ref_is_not_found_rather_than_not_in_dossier`). Both reach P6 as one word. The machine defends R6 completely; what the model cannot do is foresee it. |
| **R11** | *"Stated, never enforced."* | **Confirmed.** Both through the validator (S1 accepted) and directly against the oracle. For a field with no slot at all — `instructor`, and 54 of 56 catalogue rows — check 3 rejects only the empty string and the non-string. |
| **R12** | *"Mitigated, not fixed."* | **Confirmed, and measured.** `test_s6_one_course_becomes_two_value_rows`: the model copies the evidence's spelling exactly as rule 5 asks, check 4 correctly does not fire because `contradicts_stronger` canonicalises both sides, and the `values` table then holds `["PHYS 1401", "PHYS1401"]` for one field. Rule 5 asking for the evidence's spelling is what *produces* the split when the evidence's spelling is the loose one. |

---

## 4. One thing `82` §3 does not flag, and `76`'s 21 requirements do not cover

**The proposed `value` is never compared to the citation, or to any released text.**

Check 2 asks whether the *citation* holds. Check 3 asks whether the *value* normalizes. Nothing asks
whether the value has anything to do with the evidence cited for it. A real span copied exactly out
of `released_evidence` will carry any value at all —
`test_s2_the_value_is_never_compared_to_the_evidence_it_cites` cites the span `"the committee"` from
the released prose and proposes the value `"Dr Nobody"`, a string that appears nowhere in the
dossier, and gets `accept_direct`.

This is wider than R11. R11 is about a value that is *too big* — it contains the right characters
plus some. This is a value with **no** relationship to the evidence, and `76`'s 21 requirements have
no row for it: R3 governs what is quotable, R5 governs the span, R10 governs the value's JSON type,
R11 governs its length. None of them says the value's characters must come from a released value.

**The draft already covers it, in one sentence, and that sentence should not be edited away:**

> *"If the characters you want to propose are not sitting inside a released value, then no amount of
> reasoning about the file makes them citable."*

That line is doing more work than `82` §3 credits it with. It is the only text on either side of the
seam that binds the value to the evidence. **Recommendation (for the owner, not an edit):** `82` §3
could record it against a new requirement of its own rather than folding it into R19's row, so that
a future revision cannot drop it as redundant prose.

---

## 5. Where `76` leaves an outcome ambiguous

1. **S9's reason depends on a fact the row does not state.** `76` §7 gives S9 as
   `CITATION_NOT_IN_DOSSIER`, which is correct *only if* the cited key is a genuine P6 observation
   for this file version that P7 withheld. A key P6 never observed produces `CITATION_NOT_FOUND`
   from the coarse check, which runs before the released-evidence comparison. Both are now pinned by
   tests; `76` names only one of them.
2. **S2's expected pair is descriptive, not stated.** `76` gives the correct answer (one `unknown`
   per field considered → `abstain`) but expresses the wrong answer as prose — *"Nothing catches a
   plausible invented field-value pair beyond check 1"* — rather than as an expected pair. The suite
   records `accept_direct` with no reasons for it. That is the only reading consistent with the
   sentence, but it was inferred rather than read off.
3. **S6 is not a wrong answer at all.** `76` and `82` both classify it as a case; the model's answer
   is correct and the verdict is correct. Its control (a value that genuinely disagrees with the
   stronger fact) *is* rejected with `CONTRADICTED_BY_STRONGER`, so check 4 works. Classifying S6
   as "machine catches it" or "prompt-only" would both be wrong, which is why the suite carries a
   third label for it.

---

## 6. Not covered here

- **The empty `insufficiency_statement`.** `76` §3's rules table records that Site A abstains on it
  while the universal parser would reject it. It is not one of the fifteen and is not tested here.
- **Anything requiring a model.** Whether a model actually obeys rule 4 is unknown and stays unknown
  until one is called. This suite establishes only that if it disobeys, nothing will stop it.
- **`76` §9.3.** The suite sets `Dossier.allowed_vocabulary` equal to `FactRequest.allowlist`
  deliberately, so that it measures the prompt's problem and not a dossier builder's. The equality is
  still unasserted anywhere in `src/`.
