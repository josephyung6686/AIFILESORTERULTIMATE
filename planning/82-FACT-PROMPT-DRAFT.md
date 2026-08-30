# 82 — The A_fact prompt, drafted for ratification

Date: 2026-08-31. Companion to [`76-PROMPT-RESEARCH.md`](76-PROMPT-RESEARCH.md), which is the
requirements half. This is the text half. Revised the same day for
[`83-MODEL-ROUTING.md`](83-MODEL-ROUTING.md) §3 — see §8.

---

## 1. What this is, and its status

**This is a DRAFT. It is not installed anywhere and it is not approved.**

No `PromptDefinition` is constructed with this text. Nothing in `src/` was touched. No manifest, no
test, no vocabulary. The bytes below are inert until the owner ratifies them, and the owner ratifies
them by their own act — not by this document recommending it.

**Why the ratification is not ceremony.** `PromptDefinition.template_bytes`
(`src/llm_harness/records.py:77`) is hashed into every audit record the prompt produces
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

**One thing this draft decides that `76` left open, and says so loudly.** `76` §10.1 records a
glossary decision as owed and names three options, only one of which a prompt can implement. This
draft implements that one (rule 2). See §5.1 and §7.1 — it is the single item most worth the owner's
disagreement.

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

The dossier has these keys and no others: allowed_vocabulary, call_site, conflicts, eligibility_reason, evidence_items, max_dossier_tokens, plan_version, policy_version, reduction_rung, released_evidence, response_schema, shaping_policy, subject_ref.

Four of them are yours.

"allowed_vocabulary" is the complete list of field keys you may propose. There are no others.

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

2. If a key's meaning is not plain from the key itself, decline that field. You have not been told what these keys mean and you must not guess what one means in order to fill it.

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

6,757 bytes / 1,130 words, measured on the block above.

---

## 3. Requirement by requirement

All 21 from `76` §6. "Draft line" quotes the governing text.

| # | Requirement | Where the draft satisfies it | Satisfied? |
|---|---|---|---|
| R1 | Template supplies its own terminator; the dossier's `{` follows with no separator. | Final line `The dossier follows.` plus a trailing newline. | Yes |
| R2 | Describe the dossier as the exact key set of `_body`, sorted, compact JSON. | `WHAT THE DOSSIER CONTAINS` names all thirteen keys in sorted order, then narrows to the four that matter. No "document", "context" or "page" is described anywhere; the draft says those do not exist. | Yes — but see §5.6, `76` R2 says "twelve" and `_body` has thirteen. |
| R3 | The only quotable text is `released_evidence[].value`. | *"The `value` strings are the only text you have been given… Text that is not inside one of those `value` strings does not exist for you."* | Yes |
| R4 | Exactly one of `cited_span` / `metadata_field_name`, plus non-empty `why_it_supports`. | Rule 6 first sentence; rule 7, which now also bounds what the sentence may do: *"It is not a place to argue for a value the evidence does not carry."* Both citation forms shown. | Yes |
| R5 | `cited_span` a substring of `value`; `metadata_field_name` equal to `address`. | Rule 6 bullets — *"must appear inside that item's `value` exactly as it is written there. Copy it across; do not retype it from memory"* / *"must equal that item's `address` exactly, character for character."* | Yes |
| R6 | `evidence_ref` must be a `released_evidence[].observation_key` **and** a P6 citable observation. | *"Cite only keys that appear in `released_evidence`."* | **Half.** The first clause is stated. The second (`fact_validation.py:217`, the coarse check against P6's observations for this file version) is **invisible to the model** — nothing in the dossier lists P6's observation set, so no wording can direct the model at it. In a correctly built dossier it is implied by the first; if it is not, the rejection is unforeseeable. Not a wording gap — a dossier-construction obligation, related to §9.3 of `76`. |
| R7 | `payload.field` a verbatim member of `allowed_vocabulary`. | Rule 1. | Yes |
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
draft does not paper over any of them.

**Two requirements the draft adds beyond `76`'s 21**, both traceable:

- *"do not reason about who they are, what they do, or what they were doing"* — from the RULING at
  `privacy/vocabulary.py:161`, dated 2026-08-31: a person's typed self-description is a `user_edits`
  item and never leaves the device. The model therefore never has it, and inviting it to infer the
  person's roles is inviting it to invent them. This is also the direct wording defence against the
  recorded product failure: a graduate student who also teaches, whose whole disk was filed as
  coursework.
- *"You may be judged against facts you were never shown."* — from `76` §4.3: `_body` serialises no
  existing facts, so a `CONTRADICTED_BY_STRONGER` rejection is unforeseeable from the model's side.
  Saying so is honest and discourages the model from assuming its answer is the only one.

---

## 4. The fifteen stress cases

From `76` §7. What this draft produces, and whether that is correct.

| # | Input | What the draft directs | Correct? |
|---|---|---|---|
| S1 | Released value `"PHYS1401 Problem Set 4"`; the wanted value is `PHYS1401`. The observed `qwen2.5:3b` failure. | Rule 4: the smallest run of characters that identifies the thing. Value `"PHYS1401"`, span `"PHYS1401"`. | Correct — **and unverifiable.** Nothing downstream checks it. If the model ignores rule 4, the answer is `ACCEPT_DIRECT` and becomes a folder name. This case is the reason the draft exists and it remains the draft's weakest point, and at the routed tier it is now the **first**-ranked risk rather than the second (§5.7). *"A value you worked out is not a value you found"* was added for it. |
| S2 | Prose supporting nothing in `allowed_vocabulary`. | Rules 2 and 9 and the two-moves section: one declining claim per field considered, each with a statement. | Correct |
| S3 | Two released items support two different values for one field. | Rule 8: pick the better-supported one and cite it, or decline naming the ambiguity. Never two claims. | Correct |
| S4 | The wanted value is in the store but not inside any released `value`. | *"Text that is not inside one of those `value` strings does not exist for you"* plus *"If you cannot cite evidence that already exists in `released_evidence`, you must decline."* | Correct |
| S5 | The model reaches for `course_code`; the key is `subject`. | Rule 1 refuses the invented key. Rule 2 then bites: `subject` may not read as "plain from the key itself" to a small model, so it may decline rather than map. | Correct but **costly** — see §7.1. Declining is a valid outcome here; it is also a missed fact the code could not have got another way. |
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
`76` §9 findings, named here rather than hidden.

---

## 5. What the draft deliberately does not say

### 5.1 No glossary of field meanings — and a fail-closed clause instead

`76` §10.1 leaves this open and names three options: the template carries meanings (impossible at 23
schemas and 56 catalogue rows), the dossier carries them per file (a `_body` change, and a new
`dossier_id` for every dossier already built), or the prompt tells the model to decline any field
whose meaning is not plain from its key.

**This draft takes the third**, as rule 2, because it is the only one a prompt can take and because
the project's rule everywhere else is fail-closed. **It is a decision, not a finding, and it is the
one thing in this document most worth the owner overruling.** If the owner prefers option 1 or 2,
rule 2 comes out and the draft is re-fingerprinted before it is ever used. See §7.1 for what rule 2
costs.

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

### 5.8 A correction to `76`

`76` R2 says "the twelve keys". `_body` (`dossier.py:118-136`) serialises **thirteen**:
`allowed_vocabulary`, `call_site`, `conflicts`, `eligibility_reason`, `evidence_items`,
`max_dossier_tokens`, `plan_version`, `policy_version`, `reduction_rung`, `released_evidence`,
`response_schema`, `shaping_policy`, `subject_ref`. `76`'s own §4 table lists all thirteen, so it is
a miscount in the requirement line rather than a disagreement about the input. The draft names
thirteen.

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
4. **Rule 2 becomes policy.** Ratifying it settles `76` §10.1 in favour of "decline what you cannot
   read", and every field whose key is not self-explanatory gets systematically less coverage from
   the model. That is a product decision about recall, made in a prompt.
5. **Two sibling artifacts fall due.** `response_schema_bytes` and `shaping_policy_bytes` are
   separate injected byte strings, both shown to the model inside the same dossier
   (`dossier.py:131-134`). If they describe a different shape from `THE SHAPE` above, the model sees
   two schemas and picks one. Ratifying this template obliges authoring those two to agree with it —
   and they are the owner's text on the same grounds.
6. **R11 stays unenforced.** Ratifying rule 4 does not make anything check rule 4. If check 3 is
   later given teeth (`76` §10.2), that is a code change, not a prompt change, and this prompt
   survives it unchanged.
7. **It does NOT commit the tier, and the tier does not commit it.** `83` §3's routing lives in
   `src/cli.py` and `.env` and can be changed in an afternoon; these bytes cannot. The draft names no
   model, so re-routing A_fact tomorrow leaves it correct and leaves every record under its
   fingerprint still resolvable. The reverse also holds: ratifying this does not endorse
   `DeepSeek-V4-Pro`, whose name `83` §1 records as unverified against the provider's catalogue.

---

## 7. What to look hardest at

In the order worth the owner's attention.

**7.1 — Rule 2, the glossary substitute.** *"If a key's meaning is not plain from the key itself,
decline that field."* This is the draft's biggest lever and its most arguable line. Keys like
`school`, `instructor` and `language` are plain. Keys like `subject`, `record_type`, `work_type`,
`purpose`, `project` and `duplicate_family` are not — a small model asked what `subject` means may
answer "the topic of the document" rather than "the course code", and rule 2 tells it to stop rather
than to guess. That is deliberately fail-closed and it will cost real coverage on exactly the fields
that matter most. The alternative is a per-file glossary in the dossier, which is a `_body` change.
**If the owner wants recall over safety on these fields, rule 2 is the line to cut, and cutting it
before ratification is free.**

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

**7.3 — Length, re-argued for the routed tier.** 1,130 words, 6,757 bytes. **v1 of this document
recommended candidates for cutting; that advice was written for a 3B model and is withdrawn.** When
the likeliest failure was an attention failure, every word competed with the first and last lines. At
the Reasoning tier the likeliest failure is S1 — confident over-reach — and the words that guard
against it are the ones a shorter prompt would lose first. The draft got longer rather than shorter
(§8), deliberately.

What remains true: length is not free forever. Each call sends these bytes, and A_fact is both the
expensive tier and the highest-volume site (`83` §5). 6,757 bytes is small against any real dossier,
but it is the owner's call whether it is small against the bill.

**7.4 — Rule 9's unbounded volume.** *"one declining claim for each field you considered"* is `76`
R9's own wording, and "considered" is doing quiet work. A model that reads it as "every field in
`allowed_vocabulary`" will emit eleven declining claims for an academic file, and each one writes an
`unresolved` row (`facts/llm_seam.py`, `write_unresolved` is always an INSERT and never
de-duplicated). That is correct per §3.6 and may still be more rows than a person wants to look at.
**The draft does not bound it and the code does not either.**

**7.5 — The anti-gaming sentence.** *"Satisfying these rules is not the same as being right."* `76`
§8 requires the distinction. Whether one abstract sentence helps a 3B model or merely confuses it
after eleven concrete rules is untestable without running it — which, per `76` §10.3, can be done
against `fixtures._bytes` before the prompt is ever fingerprinted.

**7.6 — Tone and person.** Second person throughout, short declaratives, consequences attached to the
rules that carry them rather than gathered at the end. That is a style choice that becomes permanent
with the fingerprint. It is worth reading once purely as prose, out loud, before agreeing to keep it
forever.

**7.7 — Run the stress suite first.** `76` §10.3 notes all fifteen cases can be written as recorded
response bytes plus an expected `(outcome, reasons)` pair and run with no model at all. Nothing in
this document was validated against a live model, because doing so would require constructing a
`PromptDefinition` — the line this draft does not cross. **The honest reading of §4 above is "what
the draft directs", not "what a model was observed to do."**

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
