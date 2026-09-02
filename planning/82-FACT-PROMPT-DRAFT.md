# 82 — The A_fact prompt, drafted for ratification

Date: 2026-08-31. **Revised 2026-09-02 — v3.** Companion to
[`76-PROMPT-RESEARCH.md`](76-PROMPT-RESEARCH.md), which is the requirements half. This is the text
half. Revised on 2026-08-31 for [`83-MODEL-ROUTING.md`](83-MODEL-ROUTING.md) §3, and again on
2026-09-02 because **the owner ruled on `76` §10.1 and the field glossary has since shipped**
(`eec74a1`). **§8 is the revision log and is the first thing to read after §1** — it lists every
line that moved and what it traces to. Nothing was silently rewritten.

---

## 0. RATIFIED, 2026-09-02, as C2. Read this before §1.

**The owner ratified this text with `90` C2's delta applied.** §1 below still says DRAFT and is
left standing rather than rewritten, because it is the argument the ratification answers and a
reader who cannot see what was put to him cannot judge what he agreed to.

**What he ratified**, in `90` §3's terms: C0 — the text in §2 — with C2's one-sentence delta. In
`WHAT THE DOSSIER CONTAINS`, this sentence

> It is a definition and it is not evidence: nothing written in it may be quoted, and a word that
> appears only there is not a value you found.

becomes

> Read it to work out which key names the thing you found. It is a definition and it is not
> evidence, so no part of it may be cited as a span and a word that appears only there is not a
> value you found.

7,349 bytes, 1,242 words, sha256 `e4fe6d12…ae10`. **C1 and C3 were withdrawn before he saw them**
and he was told so: a twelfth numbered rule aimed at a hazard the machine now catches is `82` §7.4's
dilution worry, and `VALUE_NOT_IN_CITED_TEXT` had landed in the meantime.

**He was told the choice was close.** C0 is 60 bytes shorter, §6.7's shortest-ratifiable-text
argument is untouched, and the agent that recommended C2 said it would not argue against C0. What
C2 buys is separating three instructions C0 carries in one — USE the glossary to pick the key,
never CITE it as a span, never LIFT a value from it — where the machine now enforces the second,
and the third is the whole remaining defence. C0's weakest word is *"quoted"*, which names the thing
the machine already catches rather than the thing that goes wrong.

**The order was deliberate and it is why this is ratifiable at all.** `90` §5 ranked three things:
the value-to-evidence check, then R22, then the prompt — *"then, and only then, the prompt"*. The
check landed (`b91f6d6`, `src/llm_harness/value_grounding.py`); R22 landed (`6e6df83`, `76` §6.1).
This is the third.

**What ratifying does NOT do.** S1 and S2 stay prompt-only, and no wording closes them: S2's value
is genuinely present in the cited text and what is wrong with it is a judgement about meaning,
which no rule built on characters can reach. S16 is narrowed, not closed — where an enumerated word
also appears in the cited text, a lift and a find are byte-identical. Those are named here rather
than left for a reader to discover, because a ratification recorded without its limits reads as a
guarantee.

**Still not installed by this document.** The bytes are approved; wiring them into a
`PromptDefinition` is a separate change with its own tests, and `MODEL_CALL_SITES_WIRED` in
`src/cli.py` stays FALSE until that lands.

---

## 1. What this is, and its status

**This was a DRAFT when it was written. It is ratified as of §0 above.**

No `PromptDefinition` is constructed with this text. Nothing in `src/` was touched. No manifest, no
test, no vocabulary. The bytes below are inert until the owner ratifies them, and the owner ratifies
them by their own act — not by this document recommending it.

**Why the ratification is not ceremony.** `PromptDefinition.template_bytes`
(`src/llm_harness/records.py:79`) is hashed into every audit record the prompt produces
(`src/llm_harness/fingerprint.py:32-47`), written onto every fact row and into every cache key
(`src/facts/llm_seam.py:249-283`). The prompt's identity **is** its bytes. Change one word and it is
a different prompt with a different fingerprint, and every record already written under the old
fingerprint points at a digest whose text no longer exists anywhere in the system. There is no
migration for that and none can be written, because the whole point of the fingerprint is that it
cannot be re-pointed.

So this text is closer to a schema migration than to a copy edit. It is drafted here so the owner has
something concrete to reason about, and every line of it is traceable to a requirement in `76` (§3
below), so what is being ratified is reasoned text rather than an agent's taste.

**The model that will read this is now known, and it changed the draft.** `83` §3 routes A_fact to
the **Reasoning** tier, on the ground that *"the model most able to decline is the one worth paying
for"*. That is the same argument as this draft's hardest job, and knowing it sharpened the text
rather than relaxing it: a capable model does not fail the way a 3B model fails. It rarely wraps its
answer in a code fence; it reasons its way to a plausible value on thin evidence and then writes a
fluent justification for it. Three lines were added to address that specifically (§8), and none of
them names a model, a tier or a provider — §5.6 says why not.

**The one thing v1 and v2 decided for the owner, the owner has now decided for himself — the other
way.** `76` §10.1 recorded a glossary decision as owed and named three options. v1 and v2 took the
third (rule 2: *decline any field whose meaning is not plain from its key*) on the ground that it was
the only one a prompt could take, and §7.1 called it *"the single item most worth the owner's
disagreement."* **The owner disagreed and chose the second: the dossier carries the meanings.** That
shipped in `eec74a1` — `src/llm_harness/library/field_glossary.json` and
`llm_harness.dossier.field_glossary` (`dossier.py:67`), reaching the model as a fourteenth `_body`
key. The model is now **told** what each key of its own call means.

**v3 is what that ruling does to this text.** Rule 2 does not disappear; it narrows to the job it
still has. 55 of the 56 catalogue fields carry a transcribed meaning and one (`capture_date`) is in the
glossary's `owed` list, which means it reaches the model with **no entry at all**. For that field —
and for every field added to the catalogue before a meaning is transcribed for it — fail-closed is
still the only correct position, and rule 2 is what states it. What changes is that it no longer
fires on `subject`, `work_type`, `purpose`, `record_type`, `project` or `duplicate_family`, which is
the coverage the ruling was made to recover. Details and the full line-by-line in §5.1, §7.1 and §8.

---

## 2. The draft

The bytes proposed, complete and exact. It ends with a newline; the dossier's opening `{` is the
next byte (`records.py:70-73`).

~~~~
You are a fact extractor. A JSON dossier about one file follows this instruction. Read it and answer with one JSON object and nothing else.

OUTPUT

Think for as long as you need to before you answer. What you send is one JSON object and nothing else. No code fence. No backticks. No words before it and no words after it. The first character you send is { and the last character you send is }.

WHAT YOU ARE DOING

The dossier describes one file, named by "subject_ref". For each field key you can support, you propose one value for that field and you quote the evidence you took it from.

You are not choosing a folder, a path, a category, a group or a name for anything. You are not deciding what the file is for. You know nothing about the person whose file this is, and nothing in the dossier tells you: do not reason about who they are, what they do, or what they were doing when they made this file.

WHAT THE DOSSIER CONTAINS

The dossier has these keys and no others: allowed_vocabulary, call_site, conflicts, eligibility_reason, evidence_items, field_glossary, max_dossier_tokens, plan_version, policy_version, reduction_rung, released_evidence, response_schema, shaping_policy, subject_ref.

Five of them are yours.

"allowed_vocabulary" is the complete list of field keys you may propose. There are no others.

"field_glossary" says what those keys mean. It maps a field key to one sentence describing what that field is. Every key means the same thing on every file, so nothing there describes this file, this person or this evidence. It is a definition and it is not evidence: nothing written in it may be quoted, and a word that appears only there is not a value you found. A key with no entry in it has not been explained to you.

"released_evidence" is a list of objects, each with "observation_key", "address", "value" and "zone". The "value" strings are the only text you have been given. There is no document, no page, no filename, no surrounding sentence, no rest of the file. Text that is not inside one of those "value" strings does not exist for you.

"evidence_items" is reference metadata about observations. It carries no text, and some of its entries have no counterpart in "released_evidence". Cite only keys that appear in "released_evidence".

"subject_ref" names the one file you are describing.

The rest is bookkeeping and you do not need it. You cannot see this file's existing facts, its folder, its neighbours, or any answer anyone else has given about it. You may be judged against facts you were never shown.

THE TWO MOVES

For each field you consider, there are exactly two things you may do.

Support it: name the field, give the value, and cite the released evidence you took the value from.

Decline it: name the field and say in one sentence what was missing.

There is no third move. There is no "probably", no confidence score, no partial answer, no hedge, no note explaining yourself. If you cannot cite evidence that already exists in "released_evidence", you must decline.

A value you worked out is not a value you found. If the characters you want to propose are not sitting inside a released value, then no amount of reasoning about the file makes them citable. Reason as much as you need to; propose only what you can point at.

Declining is a correct answer and it is recorded as one. It costs nothing. It is not a failure and it is not counted as one. A field you decline stays open and can be settled later by other means. A field you get wrong becomes a permanent property of someone's file. When the two are close, decline.

THE SHAPE

To support a field:

{"claims":[{"payload":{"field":"a key copied from allowed_vocabulary","value":"the value, as a JSON string"},"citations":[{"evidence_ref":"an observation_key from released_evidence","cited_span":"characters copied exactly from that item's value","why_it_supports":"one short sentence"}]}]}

To decline a field:

{"claims":[{"payload":{"field":"a key copied from allowed_vocabulary"},"unknown":{"insufficiency_statement":"one short sentence naming what was missing"}}]}

"claims" is a list. Put one entry in it for each field you considered, whether you supported it or declined it.

THE RULES

1. "field" must be copied character for character from "allowed_vocabulary". Not a display name, not a translation, not a similar word, not a plural. If the field you want is not in that list, it is not available to you.

2. Read a field's entry in "field_glossary" before you propose it, and propose only the thing that entry describes. If a key has no entry there, decline that field: nobody has told you what it means and you must not decide for yourself what it means in order to fill it.

3. "value" must be a JSON string, in quotes. Never a number, a list, an object, true, false or null.

4. The value is the smallest run of characters that identifies the thing, not the phrase that contains it. If a released value reads "A B C" and only "A" identifies the field, then the value is "A" and not "A B C". Everything you carry across beyond the identifying part becomes part of the recorded answer and is wrong.

5. Spell the value the way the evidence spells it. Do not tidy it, expand it, abbreviate it, correct it, capitalise it differently or translate it. Two spellings of one thing become two different things.

6. A citation carries "evidence_ref" and exactly one of "cited_span" or "metadata_field_name". Leave the other one out entirely. Supplying both, or neither, destroys your whole answer.
   "cited_span" must appear inside that item's "value" exactly as it is written there. Copy it across; do not retype it from memory.
   "metadata_field_name" must equal that item's "address" exactly, character for character. Use this form when the evidence is a metadata field rather than text.

7. "why_it_supports" is required and must not be empty. One short sentence saying how that evidence carries that value. It is not a place to argue for a value the evidence does not carry: if the sentence has to do work the evidence does not do, decline the field instead.

8. At most one claim per field. If two pieces of evidence point at two different values for one field, either choose the one the evidence supports better and cite that one, or decline the field and say in the statement that the evidence pointed two ways. Never send two claims about the same field: that destroys your whole answer.

9. "claims" must never be empty. If you can support nothing at all, send one declining claim for each field you considered.

10. The key "unknown" is present when you decline and absent when you do not. Never write "unknown": false and never write "unknown": null. A claim carries either "citations" or "unknown", never both and never neither. A declining claim carries no value and no citations.

11. One malformed claim destroys every claim in the answer, including the good ones. Send the claims you are sure of and no others. Fewer claims is safer than more.

Satisfying these rules is not the same as being right. They check that your answer is anchored in the evidence you were given; they do not check that it is true. Do not shape an answer to get past them.

Your entire reply is one JSON object. No fence. No preamble. No trailing note.

The dossier follows.
~~~~

7,289 bytes / 1,226 words, measured on the block above. (v2 was 6,757 / 1,130.)

---

## 3. Requirement by requirement

All 21 from `76` §6. "Draft line" quotes the governing text.

| # | Requirement | Where the draft satisfies it | Satisfied? |
|---|---|---|---|
| R1 | Template supplies its own terminator; the dossier's `{` follows with no separator. | Final line `The dossier follows.` plus a trailing newline. | Yes |
| R2 | Describe the dossier as the exact key set of `_body`, sorted, compact JSON. | `WHAT THE DOSSIER CONTAINS` names all **fourteen** keys in sorted order, then narrows to the five that matter. No "document", "context" or "page" is described anywhere; the draft says those do not exist. | Yes — but see §5.8: `76` R2 says "twelve", v2 of this draft said thirteen, and `_body` (`dossier.py:158-195`) now serialises fourteen. |
| R3 | The only quotable text is `released_evidence[].value`. | *"The `value` strings are the only text you have been given… Text that is not inside one of those `value` strings does not exist for you."* | Yes |
| R4 | Exactly one of `cited_span` / `metadata_field_name`, plus non-empty `why_it_supports`. | Rule 6 first sentence; rule 7, which now also bounds what the sentence may do: *"It is not a place to argue for a value the evidence does not carry."* Both citation forms shown. | Yes |
| R5 | `cited_span` a substring of `value`; `metadata_field_name` equal to `address`. | Rule 6 bullets — *"must appear inside that item's `value` exactly as it is written there. Copy it across; do not retype it from memory"* / *"must equal that item's `address` exactly, character for character."* | Yes |
| R6 | `evidence_ref` must be a `released_evidence[].observation_key` **and** a P6 citable observation. | *"Cite only keys that appear in `released_evidence`."* | **Half.** The first clause is stated. The second (`fact_validation.py:217`, the coarse check against P6's observations for this file version) is **invisible to the model** — nothing in the dossier lists P6's observation set, so no wording can direct the model at it. In a correctly built dossier it is implied by the first; if it is not, the rejection is unforeseeable. Not a wording gap — a dossier-construction obligation, related to §9.3 of `76`. |
| R7 | `payload.field` a verbatim member of `allowed_vocabulary`. | Rule 1. Rule 2 now also points the model at the glossary entry for the key it is about to name, which is what turns "copy a key from the list" into "name the key that means the thing you found". | Yes |
| R8 | At most one claim per field. | Rule 8, with the consequence stated. | Yes |
| R9 | `claims` non-empty; silence is an `unknown` claim, never `[]`. | Rule 9. | Yes |
| R10 | `payload.value` must be a JSON string. | Rule 3. No example anywhere shows a non-string value. | Yes |
| R11 | The value must be the **minimal identifying substring**, not the containing phrase. | Rule 4, with the `"A B C"` → `"A"` counter-example. | **Stated, never enforced.** `76` §9.1 is verified live (§5.5 below): `normalize_for_model('subject','PHYS1401 Problem Set 4')` returns the string unchanged. The prompt is the only defence and remains so after ratification. |
| R12 | The value's spelling becomes the stored value identity. | Rule 5. | **Mitigated, not fixed.** `apply_verdict` stores `proposal.value` raw (`facts/llm_seam.py:272-274`), so two spellings still make two value rows. `76` §9.2. Wording cannot close it. |
| R13 | An `unknown` claim names its field, carries `insufficiency_statement`, carries no value and no citations. | The decline shape, plus rule 10's last sentence. | Yes |
| R14 | `"unknown"` present or absent; `"unknown": false` destroys the response. | Rule 10, explicitly, including `null`. | Yes |
| R15 | JSON and nothing else — no fence, no preamble, no trailing note. | `OUTPUT` is the first section; the last two lines repeat it. "No backticks" is stated rather than shown, so the template itself contains no fence characters. *"Think for as long as you need to before you answer"* licenses the reasoning and separates it from what is sent, at the point where that distinction matters. | Yes |
| R16 | One malformed claim rejects every claim. | Rule 11, with *"Fewer claims is safer than more."* | Yes |
| R17 | No timestamps, dates, run ids, paths, corpus names, or anything that varies between runs. | Nothing in the draft varies. There is no date, no path, no machine name, no corpus name, no "today". | Yes |
| R18 | No worked example drawn from one domain. | The only structural example is `"A B C"` → `"A"`, which names no domain. No field key from any of the 23 schemas appears in the draft. The shapes use descriptive placeholders, not real keys or values. | Yes — see §7.2, this is the cost. |
| R19 | Declining is a success and costs nothing. | *"Declining is a correct answer and it is recorded as one. It costs nothing. It is not a failure and it is not counted as one."* Then the asymmetry: a declined field stays open, a wrong field becomes permanent. Preceded by the line that makes declining reachable for a reasoning model: *"A value you worked out is not a value you found."* | Yes |
| R20 | No hedge, confidence score, or "possible" tier. | *"There is no third move. There is no 'probably', no confidence score, no partial answer, no hedge."* | Yes |
| R21 | One file. No folder, path, filing decision or grouping. | *"You are not choosing a folder, a path, a category, a group or a name for anything."* | Yes |

**Summary: 18 of 21 satisfied by wording. R6 half (its second clause is not addressable by wording).
R11 stated but unenforced by any check. R12 mitigated but defeated one layer down.** None of the
three is a defect in the draft; all three are the code findings `76` §9 already recorded, and the
draft does not paper over any of them. **All three have since been confirmed against the running
validator** — [`86-PROMPT-STRESS-RESULTS.md`](86-PROMPT-STRESS-RESULTS.md) §3 — and R6 was found to
be *stricter* than this table said: the coarse P6 check runs first, so a fabricated key returns
`CITATION_NOT_FOUND` rather than `CITATION_NOT_IN_DOSSIER`. The machine defends R6 completely; what
the model cannot do is foresee it. The word "half" in that row is about foreseeability, not about
coverage.

**Four requirements the draft adds beyond `76`'s 21**, all traceable:

- *"do not reason about who they are, what they do, or what they were doing"* — from the RULING at
  `privacy/vocabulary.py:161`, dated 2026-08-31: a person's typed self-description is a `user_edits`
  item and never leaves the device. The model therefore never has it, and inviting it to infer the
  person's roles is inviting it to invent them. This is also the direct wording defence against the
  recorded product failure: a graduate student who also teaches, whose whole disk was filed as
  coursework.
- *"You may be judged against facts you were never shown."* — from `76` §4.3: `_body` serialises no
  existing facts, so a `CONTRADICTED_BY_STRONGER` rejection is unforeseeable from the model's side.
  Saying so is honest and discourages the model from assuming its answer is the only one.
- *"If the characters you want to propose are not sitting inside a released value, then no amount of
  reasoning about the file makes them citable."* — added in v2 for S1, and `86` §4 found it is
  carrying more than v2 credited it with. **Nothing anywhere compares the proposed `value` to the
  citation, or to any released text.** Check 2 asks whether the citation holds; check 3 asks whether
  the value normalizes; no check asks whether the two have anything to do with each other.
  `test_s2_the_value_is_never_compared_to_the_evidence_it_cites` cites a real span and proposes a
  value that appears nowhere in the dossier, and gets `accept_direct`. `76`'s R3 governs what is
  quotable, R5 the span, R10 the value's JSON type, R11 the value's length — **none of them says the
  value's characters must come from a released value.** `86` §4 recommends recording this as a
  requirement in its own right so a future revision cannot drop it as redundant prose. **This
  document does so here and it is owed back to `76` as a 22nd requirement.**
- *"It is a definition and it is not evidence: nothing written in it may be quoted, and a word that
  appears only there is not a value you found."* — **new in v3, and it exists because the glossary
  created the hole it fills.** `76` R3's *"the only quotable text is `released_evidence[].value"*
  was written when the dossier's only prose was released evidence. The glossary puts fluent English
  in front of the model that in several entries **enumerates plausible values** — `media_type` is
  *"photo, screenshot, scan, video"*, `application_document_type` is *"essay, transcript, form,
  portal record"*, `site` is *"plant, works, depot, store, field"*. A model that cites a real span
  and lifts its value out of that prose passes every check, by the bullet above. A quoted *span* from
  the glossary is caught (`CITATION_SPAN_MISMATCH`); a *value* is not caught by anything.

---

## 4. The fifteen stress cases

From `76` §7. What this draft produces, and whether that is correct.

**All fifteen have since been run against the real validator** — `86`, suite
`tests/p8/test_p8_prompt_stress_cases.py`, 22 tests passing, no `PromptDefinition` constructed and
no model called. It answers a different and sharper question than this table does: not *what does the
draft direct*, but *if the model disobeys, does the machine catch it*. The answer is **twelve
machine, two prompt-only (S1, S2), one neither (S6)**, and every reason `76` §7 predicted was the
reason observed. Read the two tables together: this one says what the text asks for, `86` says what
happens when the text is ignored. Where they touch, `86`'s "Defence" column is quoted into the rows
below.

| # | Input | What the draft directs | Correct? |
|---|---|---|---|
| S1 | Released value `"PHYS1401 Problem Set 4"`; the wanted value is `PHYS1401`. The observed `qwen2.5:3b` failure. | Rule 4: the smallest run of characters that identifies the thing. Value `"PHYS1401"`, span `"PHYS1401"`. | Correct — **and unverifiable.** Nothing downstream checks it. If the model ignores rule 4, the answer is `ACCEPT_DIRECT` and becomes a folder name. This case is the reason the draft exists and it remains the draft's weakest point, and at the routed tier it is now the **first**-ranked risk rather than the second (§5.7). *"A value you worked out is not a value you found"* was added for it. **`86` confirms it is not merely unchecked but indiscriminable: the correct minimal answer and the over-quoted one produce the identical `(outcome, reasons)` pair,** so S1 is the one case of the fifteen whose test cannot be made to fail by swapping its expectations. **The glossary helps here and does not solve it.** *"the course or study subject the material belongs to"* tells the model which part of `"PHYS1401 Problem Set 4"` the field is about — the course, not the exercise — which is more than it had. It does not say whether a course *code* or a course *name* is wanted, and rule 4 remains the only line that bounds how much of the line comes across. |
| S2 | Prose supporting nothing in `allowed_vocabulary`. | Rule 9 and the two-moves section: one declining claim per field considered, each with a statement. **v3 changes the weighting here.** Rule 2 used to carry part of this case — a model that could not read a key declined it, and prose supporting nothing was declined partly by accident. Now the model knows what every key means, so the only thing standing between it and a plausible invention is *"if you cannot cite evidence that already exists in `released_evidence`, you must decline"* and rule 7's last clause. | Correct, and **prompt-only** (`86`): the invented pair is `accept_direct` with no reasons. |
| S3 | Two released items support two different values for one field. | Rule 8: pick the better-supported one and cite it, or decline naming the ambiguity. Never two claims. | Correct |
| S4 | The wanted value is in the store but not inside any released `value`. | *"Text that is not inside one of those `value` strings does not exist for you"* plus *"If you cannot cite evidence that already exists in `released_evidence`, you must decline."* | Correct |
| S5 | The model reaches for `course_code`; the key is `subject`. | Rule 1 refuses the invented key. **v3 is where this case changes most.** Under v2, rule 2 then bit — `subject` did not read as "plain from the key itself", so the model was told to decline rather than map, and `76` §7's own note on this row is *"the model has no glossary telling it that `subject` means a course code."* It now has one: `subject` is *"the course or study subject the material belongs to"*. The model maps `course_code` onto `subject` instead of declining. | **Was correct-but-costly; is now correct and free.** This row is the coverage the owner's ruling bought, stated as concretely as it can be. Machine-defended either way (`FIELD_NOT_IN_ACTIVE_SCHEMA`), so the glossary converts a rejection into a fact rather than a wrong answer into a right one. |
| S6 | Released value `"PHYS 1401"`; a stronger `direct` fact says `subject = PHYS1401`. | Rule 5: use the evidence's spelling, so `"PHYS 1401"`. Check 4 correctly passes (`contradicts_stronger` canonicalises both). | Correct answer, **wrong storage.** `apply_verdict` then writes `"PHYS 1401"` raw as the canonical value (`76` §9.2), producing two value rows for one course. The draft cannot fix this and does not pretend to. |
| S7 | `{"field":"subject","value":"Spring 2026"}`. | Rule 2 should stop it before it starts; if not, check 3 rejects it (`normalize_for_model('subject','Spring 2026') -> None`, verified). | Correct, and the one wrong-field case check 3 genuinely catches. |
| S8 | A fluent quotation that is in no released value. | Rule 6: *"Copy it across; do not retype it from memory."* If the model does it anyway, `CITATION_SPAN_MISMATCH`. | Correct, and enforced |
| S9 | An `evidence_ref` present in `evidence_items` with no `released_evidence` entry. | *"some of its entries have no counterpart in `released_evidence`. Cite only keys that appear in `released_evidence`."* Stated in exactly those terms because this is a trap the input shape sets. | Correct, and enforced |
| S10 | Both `cited_span` and `metadata_field_name` filled "to be safe". | Rule 6 first sentence, with the consequence attached to it rather than left implicit. | Correct |
| S11 | `{"claims": []}` because nothing was found. | Rule 9. The decline shape is shown so the model has a form to copy rather than inventing one. | Correct |
| S12 | The JSON wrapped in a code fence or prefaced with "Here is my answer:". | `OUTPUT` is the first section and is repeated as the last two lines. The template itself contains no backticks, so nothing in front of the model demonstrates a fence. | Correct. This is the most likely 3B failure and the draft spends its two most valuable positions on it. |
| S13 | `"unknown": false` alongside a real claim. | Rule 10, naming `false` and `null` explicitly rather than describing the rule abstractly. | Correct |
| S14 | The evidence is a metadata/EXIF observation, not body text. | Rule 6 second bullet: `metadata_field_name` equal to `address`, character for character, and the other key left out. | Correct |
| S15 | `"value": 2026` — a number. | Rule 3, naming every wrong JSON type. | Correct |

**Survives all fifteen by wording.** Two carry a caveat that is not the wording's: **S1** is directed
correctly and checked by nothing, and **S6** is answered correctly and then stored wrongly. Both are
`76` §9 findings, named here rather than hidden, and `86` §3 confirmed and measured both —
`test_s6_one_course_becomes_two_value_rows` reads `["PHYS 1401", "PHYS1401"]` back out of the
`values` table for one field. **Rule 5 asking for the evidence's spelling is what produces the split
when the evidence's spelling is the loose one**, which is worth seeing plainly: ratifying rule 5 buys
a correct answer and a duplicated value row, and the second half is the code's to fix.

**The fifteen do not cover the surface v3 opens.** `76` §7 was written before the glossary existed,
so none of the fifteen tests a model lifting a value out of glossary prose. That case is the fourth
bullet in §3 above and it has no stress row, no test, and no check. **It is the one thing in v3 that
would most benefit from a sixteenth case before ratification**, and `76` §10.3's method — recorded
response bytes plus an expected pair, no model — is enough to write it.

---

## 5. What the draft deliberately does not say

### 5.1 No glossary in the template — because the dossier now carries one

**Superseded by the owner's ruling. v2's text is quoted below so the change is legible.**

`76` §10.1 named three options: the template carries meanings (impossible at 23 schemas and 56
catalogue rows), the dossier carries them per file (a `_body` change, and a new `dossier_id` for
every dossier already built), or the prompt tells the model to decline any field whose meaning is not
plain from its key. **v2 took the third**, as rule 2, *"because it is the only one a prompt can take
and because the project's rule everywhere else is fail-closed"*, and flagged it as the one thing in
the document most worth overruling.

**The owner overruled it and took the second.** `eec74a1` ships
`src/llm_harness/library/field_glossary.json` and `llm_harness.dossier.field_glossary`, and `_body`
carries a `field_glossary` key built from `allowed_vocabulary` **and nothing else**
(`dossier.py:184`). What that buys and what it costs:

- **55 of 56 catalogue fields carry a meaning; `capture_date` does not** and sits in the file's
  `owed` list. `test_the_library_covers_the_catalogue_exactly` asserts that defined and owed
  partition the closed catalogue exactly, so a field can be neither invented nor silently dropped.
- **Every meaning is transcribed, not authored.** Each entry names the source it was quoted from and
  `test_every_meaning_is_verbatim_from_its_cited_source` re-reads that source and fails if the quote
  is not there. That is the mechanism by which a glossary — text that goes to a model, and so close
  to prompt text — did not require the owner to author 55 sentences.
- **A meaning defines a field, never a file.** `field_glossary(allowed_vocabulary)` takes one
  argument and `test_the_glossary_builder_is_given_the_vocabulary_and_nothing_else` asserts the
  signature, so no per-file, per-person or per-corpus content has a route in and nothing in §8.4's
  always-local set can leak through it. This is structural rather than promised, which is the only
  reason the glossary is not a new egress surface.

**What survives in the prompt is rule 2, narrowed to the one job it still has**: a key that reaches
the model with no entry is declined. Today that is `capture_date` and nothing else. Tomorrow it is
every field added to the catalogue before a meaning is transcribed for it — and there will be some,
because the catalogue grows and the glossary is a separate act. The fail-closed position is worth
keeping for exactly that gap. **It is no longer this document's most arguable line; §7.1 now names
what is.**

### 5.2 No `eligibility_reason`, `conflicts`, `reduction_rung`, `zone` or `policy_version` guidance

All are in the dossier and all are named in the key list, so R2 holds. None is explained.
`eligibility_reason` says why this file reached a model at all — telling the model "you are here
because the evidence remains ambiguous" is an invitation to resolve the ambiguity, which is the S1
failure with a licence attached. `conflicts` carries ids and kinds and no content, so there is
nothing the model could do with it but speculate. `zone` is P4 vocabulary the model has no key to.
The draft calls all of them bookkeeping and moves on.

### 5.3 No "be helpful", no "do your best", no "choose the most likely"

`76` §8 names this as the sentence that produces S1. The draft's nearest neighbour is its opposite:
*"When the two are close, decline."*

### 5.4 No claim that passing validation means the answer is right

The penultimate paragraph says the opposite in as many words. `76` §8 requires telling the model the
rules so it can answer correctly, while not letting the rules become the target. Whether one sentence
achieves that separation is a judgement call — §7.5.

### 5.5 No attempt to work around `76` §9's three defects

Repeated plainly because hiding them behind wording is the specific failure mode to avoid here.

1. **Check 3 does not bound a value** (`76` §9.1). Re-verified live against `src/cli.py:558`:
   `normalize_for_model('subject','PHYS1401 Problem Set 4')` → `'PHYS1401 Problem Set 4'`;
   `('subject','PHYS 1401')` → `'PHYS1401'`; `('subject','Spring 2026')` → `None`;
   `('term','PHYS1401')` → `None`; `('purpose','university application')` → unchanged;
   `('subject', 'a'*300)` → unchanged. Two slots exist in this deployment. For every other field the
   check rejects only the empty string and the non-string. **Rule 4 is prompt-only and stays
   prompt-only after ratification.**
2. **The model's spelling becomes the stored value identity** (`76` §9.2). Rule 5 asks; the writer at
   `facts/llm_seam.py:272-274` ignores `normalize_for_model` and stores the raw string. Ratifying
   rule 5 does not close `65` §4.2's identity split.
3. **Nothing in `src/` builds a Site A dossier** (`76` §9.3). Whoever writes that builder must set
   `Dossier.allowed_vocabulary` to the same tuple as `FactRequest.allowlist`. Nothing asserts the
   equality. If they diverge, the model is shown one list, judged against another, and every correct
   answer to the list it was shown is rejected — and no wording in the prompt can detect that.

### 5.6 No provider, no model name, no tier

The draft contains no occurrence of a provider name, a model name, a tier name, a context-window
size, a token budget or any other deployment fact — checked mechanically, not by eye. `83` §3 routes
this site to the Reasoning tier today; `83` §1 already warns that the names in it *"are not verified
against the provider's catalogue by anyone in this project"*, and `83`'s own status line calls the
whole document deployment policy that lives in `src/cli.py` and `.env`.

Routing is a line in a composition root and changes when the owner changes it. **The prompt bytes are
near-permanent.** A prompt that said "you are a DeepSeek model" would be wrong the first day the tier
moved, and the fingerprint would carry that wrongness into every record already written under it —
unfixable, because fixing it is a new prompt. So the draft addresses whatever model reads it, and the
three lines added for the Reasoning tier (§8) are written as properties of careful answering rather
than as accommodations for one vendor.

### 5.7 Which of `76`'s 21 requirements assume a particular model

Asked directly, because a requirement written against one model's quirks ages badly inside text that
cannot be revised.

**None of the 21 do.** Every one of them cites a code line — a parser branch, a check, a dataclass
invariant — and holds for any model that produces bytes. R14 is the closest call, since its *"a model
taught JSON will reach for the boolean"* is an observation about models rather than about code; but
the requirement itself is `sites.py:150-157`, which rejects `"unknown": false` no matter who sends it.

**`76`'s ranking does, and it is now stale.** §7's closing paragraph names *"the three most likely to
break a 3B model"* — S12, then S1, then S11/S13 — and ranks them for `qwen2.5:3b`, the model observed
failing on this machine. That is a rationale ordering, not a requirement, and at the Reasoning tier it
inverts:

| | `76`'s 3B ranking | at the routed tier |
|---|---|---|
| **S12** — fence or preamble | most likely | unlikely; still catastrophic when it happens, so the bookends stay |
| **S11 / S13** — declining in a malformed shape | joint second | unlikely; the shapes are shown, which is cheap |
| **S1** — the containing phrase as the value | second | **first, and by a distance.** It is a judgement about scope, not about formatting, and capability does not help — a better model produces a *more convincing* over-quotation with a *better-written* `why_it_supports`. Nothing downstream checks it (§5.5). |

The practical consequence: the draft's defences against formatting failure are now cheap insurance,
and its defences against confident over-reach are the ones carrying the weight. That is why the three
lines in §8 are all aimed at the second group.

### 5.8 A correction to `76`, and a correction to v2

`76` R2 says "the twelve keys". v2 of this draft corrected that to thirteen. **Both are now wrong:
`_body` (`dossier.py:158-195`) serialises fourteen**, because `eec74a1` added `field_glossary`
between `evidence_items` and `max_dossier_tokens` in sorted order:

`allowed_vocabulary`, `call_site`, `conflicts`, `eligibility_reason`, `evidence_items`,
**`field_glossary`**, `max_dossier_tokens`, `plan_version`, `policy_version`, `reduction_rung`,
`released_evidence`, `response_schema`, `shaping_policy`, `subject_ref`.

`76`'s original miscount was a slip in the requirement line — its own §4 table listed all thirteen
that then existed. The draft names fourteen.

**This is the failure mode R2 exists to prevent, demonstrated once for free.** A prompt that names a
key set is coupled to `_body`, and `_body` gained a key two days after v1 of this draft was written.
After ratification that coupling is one-way: `_body` can gain a key and the bytes cannot follow it.
See §6.7.

---

## 6. What ratification would commit the owner to

Stated plainly, because these are one-way doors.

1. **These exact bytes become an identity.** The fingerprint is over the bytes. Trailing whitespace,
   a changed comma, a reordered rule — each is a different prompt.
2. **Every record produced under it references that digest forever.** Fact rows, audit records and
   cache keys carry the fingerprint (`facts/llm_seam.py:249-283`). Revising the text later does not
   revise them; it strands them. They will point at a digest whose text exists nowhere, and §8.5's
   replay comparison across two runs of "the same prompt" stops meaning anything across the boundary.
3. **So a revision is a new prompt, not an edit**, and the sane way to make one is a new
   `template_id` alongside the old, with the old kept readable for the records that reference it.
   Nothing in the code does that today; it is a convention the owner would be adopting.
4. **Rule 2 becomes policy — a much narrower one than v2 asked for.** `76` §10.1 is already settled
   by the owner in favour of the dossier carrying meanings, so ratifying rule 2 no longer settles
   that. What it settles is the residue: **a field the glossary has not explained gets no coverage
   from the model, ever, silently.** Today that is `capture_date` alone. The cost lands in the
   future, not now: whoever adds a field to the catalogue and does not transcribe a meaning for it
   has removed that field from the model's reach without touching the model, the prompt or any
   test that fails. `test_the_library_covers_the_catalogue_exactly` forces the new field into
   `fields` or into `owed`; **nothing forces the choice to be the useful one.**
5. **Two sibling artifacts fall due.** `response_schema_bytes` and `shaping_policy_bytes` are
   separate injected byte strings, both shown to the model inside the same dossier
   (`dossier.py:190-193`). If they describe a different shape from `THE SHAPE` above, the model sees
   two schemas and picks one. Ratifying this template obliges authoring those two to agree with it —
   and they are the owner's text on the same grounds.
6. **R11 stays unenforced.** Ratifying rule 4 does not make anything check rule 4. If check 3 is
   later given teeth (`76` §10.2), that is a code change, not a prompt change, and this prompt
   survives it unchanged.
7. **The bytes become coupled to `_body`'s key set, one-way.** The draft says *"The dossier has these
   keys and no others"* and then names fourteen, and it names `field_glossary` as a thing the model
   should read. If `_body` later gains a fifteenth key, the prompt is asserting something false to
   every model that reads it and **cannot be corrected** — correcting it is a new fingerprint and
   strands every record written under the old one. If `field_glossary` were ever removed from
   `_body`, the prompt would direct the model at a key that is not there and rule 2 would decline
   every field. Nothing in `src/` asserts that `_body`'s keys match any prompt's description of
   them, and no test can, because the prompt is not in `src/`. **`_body` gained a key two days after
   v1 of this draft was written** (`665cddd` 2026-08-31, `eec74a1` 2026-09-02 — §5.8). That is the
   argument for ratifying late rather than early, and it is the strongest one in this document.
8. **It does NOT commit the tier, and the tier does not commit it.** `83` §3's routing lives in
   `src/cli.py` and `.env` and can be changed in an afternoon; these bytes cannot. The draft names no
   model, so re-routing A_fact tomorrow leaves it correct and leaves every record under its
   fingerprint still resolvable. The reverse also holds: ratifying this does not endorse
   `DeepSeek-V4-Pro`, whose name `83` §1 records as unverified against the provider's catalogue.

---

## 7. What to look hardest at

In the order worth the owner's attention.

**7.1 — The glossary is now a source of plausible words, and nothing binds a value to evidence.**
This replaces v2's 7.1 (rule 2 as the glossary substitute), which the owner's ruling settled. It is
the draft's most arguable line **because it is the newest and the least tested.**

The glossary was built to tell the model what a field is, and it does. It also, unavoidably, puts
fluent English in front of the model, and several entries define a field by listing what goes in it:
`media_type` is *"photo, screenshot, scan, video"*; `application_document_type` is *"essay,
transcript, form, portal record"*; `site` is *"plant, works, depot, store, field"*. Put that beside
`86` §4 — **the proposed value is never compared to the citation, or to any released text** — and a
model can cite a real span from real evidence, propose `"screenshot"` because the glossary told it
that is what a `media_type` looks like, and get `accept_direct`. The value never appeared in the
evidence. Nothing checks that it did.

The draft's answer is one sentence — *"It is a definition and it is not evidence: nothing written in
it may be quoted, and a word that appears only there is not a value you found"* — sitting next to
the sentence that already does the same job for reasoning, *"A value you worked out is not a value
you found."* **Three things about that are worth the owner's doubt:**

1. Whether one sentence is enough against fifty-five sentences of vocabulary in the same dossier.
2. Whether saying *"nothing written in it may be quoted"* invites a model to under-use the glossary
   — to treat the meanings as untrusted rather than as definitions — which would give back the S5
   coverage the ruling was made to buy.
3. Whether this belongs in the dossier's description at all, or as a twelfth numbered rule where a
   model scanning rules would meet it. It is placed with `released_evidence`'s exclusivity because
   that is the same claim; it is the only v3 line placed on a judgement rather than a requirement.

**There is no stress case for this and no test.** §4's closing note says one could be written
without a model, and it should be, before ratification.

**7.2 — Rule 4's abstract example.** `"A B C"` → `"A"` is schema-neutral, which R18 requires, and it
is also the least vivid way to teach the one failure that no check catches. A concrete example
(`"PHYS1401 Problem Set 4"` → `"PHYS1401"`) would land harder, and would bias every household,
contractor and clinic corpus toward reading its evidence as coursework, permanently, across 23
schemas.

**The routed tier moves this argument, and in the draft's favour.** Vividness is a crutch for a small
model; abstraction is the cheaper half of the trade for a model chosen for reasoning. The R18 cost of
a concrete example is unchanged and permanent, while its benefit shrinks. The draft keeps the abstract
form, and the owner should ratify or reject that on those grounds rather than on how the sentence
reads to a person — a person is not the reader.

**The glossary moves it further in the same direction.** R18's real objection to a concrete example
was never that concreteness is bad; it was that a *permanent* concrete example biases every corpus
forever. The glossary supplies concreteness **per call, for the fields of that call only** — an
academic file gets academic sentences and a clinic file does not see them. So the thing a concrete
example was for is now delivered by a channel that can vary, and the template keeps the half that
must not.

**7.3 — Length, re-argued for the routed tier.** 1,226 words, 7,289 bytes — v3 added 96 words and
532 bytes on top of v2's 6,757. **v1 of this document
recommended candidates for cutting; that advice was written for a 3B model and is withdrawn.** When
the likeliest failure was an attention failure, every word competed with the first and last lines. At
the Reasoning tier the likeliest failure is S1 — confident over-reach — and the words that guard
against it are the ones a shorter prompt would lose first. The draft got longer rather than shorter
(§8), deliberately.

What remains true: length is not free forever. Each call sends these bytes, and A_fact is both the
expensive tier and the highest-volume site (`83` §5). 7,289 bytes is small against any real dossier,
but it is the owner's call whether it is small against the bill.

**And the prompt is no longer the only fixed cost.** The glossary rides in every dossier, one
sentence per allowed field. An academic file's eleven fields carry eleven sentences; the widest
schemas carry more. That is a per-call cost the owner did not see when he ruled, because the ruling
was about coverage. It is small and it is real, and it belongs beside these bytes rather than
against them: cutting prompt words to pay for glossary words would cut the S1 defences first
(§5.7), which is the wrong end.

**7.4 — Rule 9's unbounded volume.** *"one declining claim for each field you considered"* is `76`
R9's own wording, and "considered" is doing quiet work. A model that reads it as "every field in
`allowed_vocabulary`" will emit eleven declining claims for an academic file, and each one writes an
`unresolved` row (`facts/llm_seam.py`, `write_unresolved` is always an INSERT and never
de-duplicated). That is correct per §3.6 and may still be more rows than a person wants to look at.
**The draft does not bound it and the code does not either.**

**v3 makes this worse, not better.** Under v2 a model that could not read a key declined it without
having considered it seriously; now every key comes with a sentence explaining it, which is an
invitation to consider all of them. A model that reads rule 9's "considered" generously will now emit
one declining claim per *explained* field, and there are eleven of those on an academic file. The
right fix is a bound in the wording or a de-duplicating writer, and **v3 adds neither**, because
either would be a change the owner has not asked for.

**7.5 — The anti-gaming sentence.** *"Satisfying these rules is not the same as being right."* `76`
§8 requires the distinction. Whether one abstract sentence helps a 3B model or merely confuses it
after eleven concrete rules is untestable without running it — which, per `76` §10.3, can be done
against `fixtures._bytes` before the prompt is ever fingerprinted.

**7.6 — Tone and person.** Second person throughout, short declaratives, consequences attached to the
rules that carry them rather than gathered at the end. That is a style choice that becomes permanent
with the fingerprint. It is worth reading once purely as prose, out loud, before agreeing to keep it
forever.

**7.7 — The stress suite has been run; it did not test the prompt.** `86` did what `76` §10.3
described: all fifteen cases as recorded response bytes plus an expected `(outcome, reasons)` pair,
through `llm_harness.sites.dispatch` at `A_FACT` over real P1/P4/P6 inputs and this deployment's own
oracles, with no `PromptDefinition` constructed and no model called. 22 tests, all passing; every
reason `76` predicted was the reason observed; fourteen of the fifteen are discriminating and six
deliberately mutated expectations all failed, so the suite is not fifteen assertions that would pass
against anything.

**What it establishes is the machine's half, not this document's.** It says that if the model
disobeys, twelve of the fifteen are caught and two are not. It says nothing about whether a model
obeys. **The honest reading of §4 above is still "what the draft directs", not "what a model was
observed to do"** — and it will stay that way until a `PromptDefinition` exists, which is the line
this draft does not cross.

What `86` adds to the ratification decision is a sharper statement of where the bytes are
load-bearing: **S1 and S2 are the only two cases with no machine behind them**, and `86` §2 quotes
the exact lines of §2 that stand alone there. Those are the lines to read hardest and the ones a
future revision must not lose. `86` §4's finding — the value is never compared to anything — widens
that from two cases to a class.

---

## 8. Change log

The draft has no fingerprint yet, so it has no versions in the system's sense. It has been written
twice, and the difference is worth seeing because the second pass was caused by learning which model
would read it.

**v1** — commit `665cddd`. Written against `76` alone, with `76` §7's ranking of 3B failure modes
carrying most of the weight.

**v2** — this document. `83` §3 routes A_fact to the Reasoning tier, *"because the model most able to
decline is the one worth paying for."* A capable model fails differently: it does not garble the
envelope, it reasons to a plausible value on thin evidence and then justifies it well. Three lines
were added, all aimed at that, and none naming a model:

| Where | Added | Why, and to what it traces |
|---|---|---|
| `OUTPUT` | *"Think for as long as you need to before you answer. What you send is one JSON object and nothing else."* | R15 unchanged in substance. It separates thinking from sending at the moment that distinction matters, rather than forbidding the reasoning a Reasoning-tier model was chosen for. `json.loads` is given the whole byte string (`sites.py:120-123`), so what is *sent* is the only thing that has ever been constrained. |
| `THE TWO MOVES` | *"A value you worked out is not a value you found. If the characters you want to propose are not sitting inside a released value, then no amount of reasoning about the file makes them citable. Reason as much as you need to; propose only what you can point at."* | §3.5's *"must cite exact supporting evidence already extracted"* and §3.6's *"a model that cannot cite sufficient evidence must return unknown"*, aimed at the one failure a better model makes **more** convincingly, not less. Hardens S1, S2 and S8 at the point where reasoning turns into a claim. |
| Rule 7 | *"…saying how that evidence carries that value. It is not a place to argue for a value the evidence does not carry: if the sentence has to do work the evidence does not do, decline the field instead."* | `why_it_supports` is required and never checked for content (`records.py:287` checks only that it is non-empty). A fluent justification for a thin citation is the capable model's version of guessing, and this is the only place in the response where that fluency has room to live. |

Net: +102 words, +518 bytes. Nothing was removed. Every requirement row in §3 still holds and three
were re-quoted to reflect the new lines; §4's fifteen verdicts are unchanged.

**v3** — this revision, 2026-09-02. Caused by an owner ruling, not by a change of mind:
`76` §10.1's glossary decision was settled the other way from v2's guess, and the glossary shipped
(`eec74a1`). v3 makes the draft describe the dossier that now exists.

### 8.1 The three changes to the bytes

| Where | v2 | v3 | Traces to |
|---|---|---|---|
| `WHAT THE DOSSIER CONTAINS`, key list | thirteen keys; *"Four of them are yours"* | fourteen keys, `field_glossary` inserted in sorted position; *"Five of them are yours"* | `76` R2 — *"describe the dossier as the exact key set of `_body`, in sorted order"*. `_body` is `dossier.py:158-195`; the key is added at line 184. A prompt that named thirteen keys and said *"and no others"* would be false the day it was ratified. |
| `WHAT THE DOSSIER CONTAINS`, new paragraph | — | *"`field_glossary` says what those keys mean. It maps a field key to one sentence describing what that field is. Every key means the same thing on every file, so nothing there describes this file, this person or this evidence. It is a definition and it is not evidence: nothing written in it may be quoted, and a word that appears only there is not a value you found. A key with no entry in it has not been explained to you."* | Sentences 1–2: `76` R2 and R7 — a key the model is told to use must be described. Sentence 3: `field_glossary`'s own bound, asserted by `test_the_glossary_cannot_vary_between_two_files` and `test_no_always_local_content_reaches_the_glossary`; telling the model the meanings do not describe its file is what stops it reading them as evidence. Sentence 4: **`76` R3 extended to a key that did not exist when R3 was written**, plus `86` §4 — the value is never compared to anything, so glossary prose is a live value source. Sentence 5: sets up rule 2. |
| Rule 2 | *"If a key's meaning is not plain from the key itself, decline that field. You have not been told what these keys mean and you must not guess what one means in order to fill it."* | *"Read a field's entry in `field_glossary` before you propose it, and propose only the thing that entry describes. If a key has no entry there, decline that field: nobody has told you what it means and you must not decide for yourself what it means in order to fill it."* | The owner's ruling on `76` §10.1. The first sentence is new work the glossary makes possible: **for 54 of 56 fields check 3 does nothing at all** (`76` §9.1, confirmed by `86` §3), so wrong-field errors like S7 are undetectable outside `subject` and `term` — the glossary entry is the only thing that can prevent one. The second sentence is v2's rule 2, kept for the fields the glossary does not cover (`capture_date` today) and for fields added to the catalogue before a meaning is transcribed. |

**Nothing else in the bytes was touched.** Rules 1 and 3–11 are v2's, character for character, and so
are `OUTPUT`, `WHAT YOU ARE DOING`, `THE TWO MOVES`, `THE SHAPE` and the closing lines. In
particular the three sentences v2 added for the Reasoning tier are unchanged, and `86` §4 is a
direct argument for never editing one of them.

Net: **+96 words, +532 bytes** (6,757 → 7,289; 1,130 → 1,226). Nothing was removed.

### 8.2 The changes to the reasoning around the bytes

| Section | What changed |
|---|---|
| Header, §1 | The status paragraph said this draft decided `76` §10.1 for the owner. It now records that the owner decided it, the other way, and what that leaves rule 2 doing. |
| §3, R2 | thirteen → fourteen keys; the "see §5.6" pointer was wrong and now points at §5.8. |
| §3, R7 | Notes that rule 2 now points at the glossary entry, which is what turns "copy a key" into "name the right key". |
| §3, summary | Records that `86` confirmed all three not-fully-satisfied requirements live, and that R6 is **stricter** than v2 said — the coarse P6 check runs first, so a fabricated key is `CITATION_NOT_FOUND`. |
| §3, additions beyond `76`'s 21 | Two became four. Added: the value↔evidence binding sentence, which `86` §4 found is the only text on either side of the seam doing that job and recommends recording as a requirement of its own — **owed back to `76` as a 22nd**; and the glossary-is-not-evidence sentence, new in v3. |
| §4 | Preamble now points at `86`'s twelve-machine / two-prompt-only / one-neither result. **S5 changed materially** — the glossary is exactly what `76` §7 said this row lacked, so the model maps instead of declining, and that row is the coverage the ruling bought. **S2 changed in weighting** — rule 2 used to carry part of it by accident and no longer does. **S1 gained two findings**: `86` shows it is indiscriminable, not merely unchecked, and the glossary helps it without solving it. A closing note records that **the fifteen do not cover the surface v3 opens** and that a sixteenth case could be written without a model. |
| §5.1 | Rewritten. v2's position is quoted rather than deleted; the shipped glossary's three guarantees (partition, transcription-not-authorship, one-argument signature) are recorded because they are why it is not a new egress surface. |
| §5.8 | thirteen → fourteen, with the point that `_body` changed twice in three days and the prompt cannot follow it after ratification. |
| §6 | Item 4 narrowed and its cost moved into the future — a field added without a meaning loses model coverage silently. **New item 7**: the bytes become one-way coupled to `_body`'s key set, and nothing can assert that coupling because the prompt is not in `src/`. The tier item became 8. |
| §7.1 | **Replaced.** v2's 7.1 (rule 2 as glossary substitute) is settled. The new 7.1 is the glossary-as-value-source risk, with three specific doubts about the one sentence answering it. |
| §7.2 | Strengthened, not changed: R18's objection was to *permanent* concreteness, and the glossary supplies per-call concreteness through a channel that can vary. |
| §7.3 | Recounted, and records that the glossary is now a second per-call fixed cost the owner did not see when he ruled. |
| §7.4 | **v3 makes this worse.** Explaining every key invites the model to consider every key, and each considered field is an INSERT. Neither the wording nor the code bounds it, and v3 deliberately does not add a bound. |
| §7.7 | The suite exists (`86`). Rewritten to say what it does and does not establish: the machine's half, not the prompt's. |

### 8.3 What v3 does not do

- **It installs nothing.** No `PromptDefinition` is constructed anywhere. `src/` is untouched. No
  test asserts any of this text. `records.py:89` still refuses an empty `template_bytes`, so no P8
  call site can fire until the owner acts, and that is the intended state.
- **It does not fix `76` §9.1, §9.2 or §9.3.** All three are code, all three remain open, and `86`
  §3 confirmed all three against the running system. §9.3 in particular — nothing asserts
  `Dossier.allowed_vocabulary == FactRequest.allowlist` — now matters more than it did, because the
  glossary is built from `allowed_vocabulary` (`dossier.py:184`). If the two lists diverge, the model
  is shown meanings for one set of fields and judged against another.
- **It does not re-run the fifteen.** `86` ran them against v2's predictions; every §4 verdict v3
  changes is a change in *what the draft directs*, not in what the validator does, so no recorded
  `(outcome, reasons)` pair moves. The one case v3 would need a new test for is the sixteenth that
  does not exist yet (§7.1).
- **It does not ratify anything.** An agent may not author or adopt prompt text. This is a document
  prepared for the owner to accept, amend or reject.
