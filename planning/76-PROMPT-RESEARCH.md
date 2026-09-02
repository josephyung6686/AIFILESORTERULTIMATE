# 76 — What the A_fact prompt must contain, and what it must never contain

Date: 2026-08-30. **Revised 2026-09-02 — R22 and S16 added; see §6.1 and §7's last row.**
**Research only. No prompt text is drafted here.**

`PromptDefinition.template_bytes` (`src/llm_harness/records.py:77`) is fingerprinted into every
audit record it produces (`src/llm_harness/fingerprint.py:32-47`), written onto every fact row and
into every cache key (`src/facts/llm_seam.py:249-283`). A word changed is a new prompt and a new
fingerprint; the old records keep pointing at a digest whose text no longer exists anywhere. It is
effectively permanent, so it is worth establishing first what it has to satisfy.

This document is the requirements half. It answers: what does a CORRECT model answer look like,
what does the machine on the other side actually accept, and which wrong answers does that machine
catch — and, more usefully, **which wrong answers it does not catch, where the prompt is the only
defence left.**

There are **22 requirements** and **16 stress cases**. §9 is the part to read if only one section
is read: three defects the prompt cannot fix, found while establishing what it must say.

**What 2026-09-02 changed.** R1–R21 and S1–S15 are as written on 2026-08-30 and none of them moved.
Added: **R22**, the rule that the value's characters must come from a released value the claim
cites, and **S16**, a value lifted out of `field_glossary` prose. Both were found after this
document was written — `86` §4 found the hole, `90` §2 measured it, and
`src/llm_harness/value_grounding.py` closed the part of it that a comparison of characters can
close. **R22 states a rule the code already enforces; it adds no policy.** §6.1 says exactly what it
does and does not close, because a requirement that hides its blind spot is worse than one that
names it.

---

## 1. What §3.5 and §3.6 require, quoted

### §3.5 — the closure, from `planning/00-database-agent-product-design.md:41`

> The LLM is not allowed to invent a new fact schema, create an unsupported field, or make a
> free-form filing decision. It can only propose facts that belong to the active domain schema, and
> it must cite exact supporting evidence already extracted from the file.

### §3.6 — the validation, from `planning/00-database-agent-product-design.md:42`

> Every LLM-produced fact must pass a validation step before it becomes active in the database. The
> validator checks that the proposed field exists in the relevant domain schema, that the model's
> cited quote or metadata field is actually present in the stored evidence, that the proposed value
> can be normalized safely, and that no stronger direct or rule-validated fact contradicts it. **A
> model that cannot cite sufficient evidence must return unknown.** A model output that is useful
> but too weak to establish a fact may remain a possible clue for review; it must not quietly become
> a folder proposal or an asserted file property.

### The same clause as the code reads it — `src/facts/llm_seam.py:1-20`

> ```
> """O6 -- what P6 hands P8, and the consequence of each verdict (§3.3, §3.5, §3.6).
>
> §3.6, and every clause of it binds here:
> ```
> …the quotation above, verbatim, then:
> ```
> **P6 supplies the four inputs and owns none of the checking.** `apply_verdict` takes a
> `Verdict` it did not compute. A PASSING verdict over a proposal citing a key that is
> not in the store therefore writes a fact -- deliberately…
> ```

And at `src/facts/llm_seam.py:21-27`:

> **One floor is not left to the verdict.** §3.5: the LLM "is not allowed to invent a new fact
> schema, create an unsupported field". The field catalogue is closed, so a passing verdict naming a
> field outside it raises `FieldNotInCatalogue` through the value and fact writers… **The ALLOWLIST
> is narrower than the catalogue** and is check 1's input, which is P8's.

---

## 2. The four checks, and what a correct answer must do to pass each

`FOUR_CHECKS` and `CHECK_REASONS`, `src/facts/llm_seam.py:70-90` — §3.6's own order, and the
mapping to the P6 `unresolved` reason each failure is written down as:

| # | `FOUR_CHECKS` | P6 reason on failure | P8 reason code | Runs at |
|---|---|---|---|---|
| 1 | `field_in_active_schema` | `field_not_in_active_schema` | `FIELD_NOT_IN_ACTIVE_SCHEMA` | `fact_validation.py:204` |
| 2 | `citation_present_in_evidence` | `citation_absent_from_evidence` | `CITATION_NOT_FOUND` / `CITATION_NOT_IN_DOSSIER` / `CITATION_SPAN_MISMATCH` / **`VALUE_NOT_IN_CITED_TEXT`** | `fact_validation.py:217-230`, `validation.py:143-175`, **`fact_validation.py:244-252`** |
| 3 | `value_normalizes_safely` | `normalization_failed` | `VALUE_NOT_NORMALIZABLE` | `fact_validation.py:231-239` |
| 4 | `no_stronger_fact_contradicts` | `contradicted_by_stronger_fact` | `CONTRADICTED_BY_STRONGER` | `fact_validation.py:240-250` |

The fifth outcome is not a check — `UNKNOWN_REASON = "model_returned_unknown"`
(`llm_seam.py:92-95`): *"the model declining before anything could be validated."*

**`VALUE_NOT_IN_CITED_TEXT` was added to check 2's row on 2026-09-02** and is R22's enforcement. It
is not a fifth check: `FOUR_CHECKS` still has four members and this refusal maps to
`FOUR_CHECKS[1]`, so P6 records it as `citation_absent_from_evidence`. **That mapping has a cost the
owner took knowingly** (recorded at the member, `vocabulary.py:274-280`): an `unresolved` row will
say the model mis-cited when what it did was mis-value. The alternative was a fifth member of P6's
`CHECK_REASONS` — a second closed vocabulary in another part — and one approval was taken over two.
It also runs *after* check 3, not inside check 2, so a value that does not normalize is refused as
`VALUE_NOT_NORMALIZABLE` and never reaches this comparison.

**What a correct answer must do, per check:**

**Check 1 — `field_key in request.allowlist`.** The allowlist is
`facts.domains.active_field_allowlist` (`src/facts/domains.py:137-176`): the six universal fields in
stored order, then each active schema's fields in `DOMAIN_FIELDS` order, deduplicated. The model
must name a key **verbatim from `allowed_vocabulary`** — not a display name, not an alias, not a
synonym. The catalogue has 56 rows across 20 schemas and each row carries `display_name`,
`aliases` and `value_kind` (`src/facts/fields.py`), **none of which reach the model**: the dossier
serialises `allowed_vocabulary` as a bare list of key strings (`dossier.py:119`). An academic file
gets `("file_type", "creation_date", "language", "duplicate_family", "version_family",
"download_session", "school", "term", "subject", "instructor", "work_type")` and no explanation of
what any of them means.

**Check 2 — two comparisons, two sources.** `validation._check_citation` (`validation.py:130-175`):
the `evidence_ref` must be in `dossier.evidence_items` (line 144), must have a matching
`released_evidence` entry (line 152), must resolve in the store through the injected
`evidence_resolver` (line 159), and then either `cited_span in released.value` (line 165) **or**
`metadata_field_name == released.address` (line 167). Site A adds a coarse pass first
(`fact_validation.py:217`): the key must be one of P6's observations for this file version at all.
The docstring at `validation.py:122-129` says why the store is never the span source: *"With
redaction on, the stored text is the raw value and the model was shown the redacted one; matching
against the store would accept a quotation the model could not have read and reject the one it
did."*

**Check 3 — `normalize(field_key, value) is not None`.** This deployment's implementation is
`cli.normalize_for_model` (`src/cli.py:465-505`). Its behaviour is narrower than its name and is the
single most important thing in this document — see §9.1.

**Check 4 — `contradicts(proposal, row)` over every stronger existing fact.**
`cli.contradicts_stronger` (`src/cli.py:507-535`) compares **after** canonicalisation, for the same
field only. `build_request` (`llm_seam.py:191-225`) supplies only facts already stronger than an LLM
conclusion — `user_confirmed`, `direct`, `validated`. The docstring names the failure it exists to
prevent: *"`PHYS 1401` and `PHYS1401` are one course. Comparing raw values would make the model's
own AGREEMENT read as a conflict."*

**There is no fifth outcome at Site A.** `_run_checks` returns `ACCEPT_DIRECT` or `REJECT` and
nothing else (`fact_validation.py:251-255`). `WEAK` and `ACCEPT_CONTEXT_SUPPORTED` are imported and
mapped (`fact_validation.py:50-57`) and never produced. §3.6's *"possible clue for review"* downgrade
and `SEARCH_HINT_ONLY` are unreachable here. **The model has no hedge.** Every claim it makes is
either a full-strength `llm_supported` fact or a rejection, so "say it or don't" is not a stylistic
preference in the prompt — it is the only shape the machine has.

---

## 3. The exact response shape the parser accepts

Two parsers exist. `validation.validate_response` documents the universal shape
(`validation.py:16-27`); **Site A does not use it.** `sites._fact_site` → `sites._claims` →
`sites._proposal` (`sites.py:108-230`) is the one that runs. Where they differ, Site A's is the
truth. Canonical example: `src/llm_harness/fixtures.py:172-184` (`_bytes`).

```jsonc
{
  "claims": [                       // REQUIRED. list. MUST be non-empty (sites.py:127).
                                    // Every element MUST be an object (sites.py:129).
    {
      "claim_ref": "c1",            // Optional at Site A: PARSED BY NOTHING. `_proposal`
                                    // never reads it; the verdict's claim_ref is the
                                    // field key (fact_validation.py:148). Harmless.

      "payload": {                  // REQUIRED in practice: `field` lives inside it.
        "field": "subject",         // REQUIRED. Non-empty string. Must be a member of
                                    // `allowed_vocabulary`. A missing / non-string /
                                    // empty `field` makes the WHOLE RESPONSE
                                    // SCHEMA_INVALID (sites.py:145-149, 206-207).
        "value": "PHYS1401"         // REQUIRED unless `unknown` is present. MUST be a
                                    // JSON string — anything else is
                                    // VALUE_NOT_NORMALIZABLE (fact_validation.py:232).
      },

      // EXACTLY ONE OF THE FOLLOWING TWO KEYS.

      "citations": [                // Non-empty list when the model is claiming.
        {
          "evidence_ref": "obs:…",  // REQUIRED, non-empty. A `released_evidence[]`
                                    // .observation_key from the dossier.
          "cited_span": "PHYS1401", // Exactly one of these two. `cited_span` must be a
          "metadata_field_name": null,  // SUBSTRING of that item's `value`;
                                    // `metadata_field_name` must EQUAL its `address`.
                                    // Supplying both, or neither, makes the WHOLE
                                    // RESPONSE SCHEMA_INVALID (records.py:286-294).
          "why_it_supports": "the heading names the course"
                                    // REQUIRED, non-empty. Empty → MalformedRecord →
                                    // whole response SCHEMA_INVALID (records.py:287).
        }
      ],

      "unknown": {                  // The refusal. Its PRESENCE is what abstains.
        "insufficiency_statement": "no observation names a course code"
      }
    }
  ]
}
```

**Rules the shape above does not show, all of them fatal:**

| Rule | Where |
|---|---|
| The response bytes must be **JSON and only JSON** — `json.loads` is given the whole byte string. A markdown fence, a preamble sentence, or a trailing note is `SCHEMA_INVALID`. | `sites.py:120-123` |
| `"unknown": false` is **not** an abstention and **not** ignored — it is not a Mapping, so `_proposal` returns `None` and the **whole response** is `SCHEMA_INVALID`. The key is present or absent; it is never a boolean. | `sites.py:150-157` |
| **Two claims naming the same field make the whole response `SCHEMA_INVALID`.** `claim_ref` at Site A is the field key, so two verdicts about one field are indistinguishable and P8 refuses to choose. | `sites.py:208-213` |
| **One bad claim rejects every claim.** `_claims`/`_proposal` failures return a single `schema_invalid_verdict` for the response, not a per-claim one. A five-field answer with one malformed citation loses all five. | `sites.py:203-207` |
| An `unknown` claim **still names its field**. `Proposal.__post_init__` refuses `field_key=None` — §3.6's refusal is per field and `write_unresolved` takes `field_key: str`. | `facts/llm_seam.py:148-157` |
| An `unknown` claim carries **no value and no citations**. | `facts/llm_seam.py:158-162` |
| At Site A an `unknown` with an empty `insufficiency_statement` still abstains — `_proposal` does not construct `Unknown` (`sites.py:158-160`). The universal parser would reject it (`records.py:301-303`). **The prompt must require the statement anyway**: the divergence is a Site A shortcut, not a permission. | `sites.py:158`, `records.py:298-303` |

---

## 4. What is actually in the dossier the model sees

`assemble(prompt_definition, canonical_dossier_bytes)` (`records.py:70-73`) is
**`template_bytes + canonical_dossier_bytes`, concatenated with no separator.** The dossier body is
`canonical_json` — key-sorted, `separators=(",", ":")`, no whitespace, UTF-8, never ASCII-escaped
(`src/evidence_shape/canonical.py:20-47`). So the byte after the prompt's last byte is `{`.

The body has exactly these keys, in this (sorted) order — `dossier._body`, `dossier.py:102-136`:

| Key | Content | Note for the prompt |
|---|---|---|
| `allowed_vocabulary` | `["creation_date","subject",…]` | Bare field keys. No display names, no descriptions, no value kinds. |
| `call_site` | `"A_fact"` | |
| `conflicts` | `[{"conflict_id":…,"kind":…}]` | **Ids and kinds only.** The model cannot see what the conflict says. |
| `eligibility_reason` | one of `remains_ambiguous`, `multiple_plausible_domains`, `language_requires_interpretation` | `vocabulary.py:92-100`. Why this file reached a model at all. |
| `evidence_items` | `[{basis, evidence_ref, excerpt_span, kind, location, reliability_state}]` | Reference metadata. **No text.** `basis` is `direct-anchor` or `context-supported` (`vocabulary.py:350-352`). |
| `max_dossier_tokens` | int | |
| `plan_version` | `null` at Site A | `records.py:62-66`. |
| `policy_version` | str | |
| `reduction_rung` | `none` \| `summarized_facts` \| `preserved_anchors` \| `split` \| `deferred` | A reduced dossier is a smaller world, not a different one. |
| `released_evidence` | `[{address, observation_key, value, zone}]` | **The only text the model gets, and the only quotable source.** |
| `response_schema` | the injected `response_schema_bytes`, decoded as UTF-8 | `dossier.py:131-134`. Must be text; hex was a real bug. |
| `shaping_policy` | the injected `shaping_policy_bytes`, decoded as UTF-8 | Same. |
| `subject_ref` | the file id | One file. Scope is `file`. |

**Three things about this input that a prompt is likely to get wrong:**

1. **The two evidence lists are separate and joined by key.** `evidence_items[].evidence_ref` ==
   `released_evidence[].observation_key`. An item can appear in `evidence_items` with **no**
   released counterpart — P7 released nothing for it — and citing it is `CITATION_NOT_IN_DOSSIER`
   (`validation.py:152-157`).
2. **There are no context windows.** `context_before` / `context_after` / `context_truncated` were
   removed from `ReleasedEvidence`; the docstring records why (`records.py:248-254`): they were
   serialised into the model-visible bytes, nothing ever read them, and *"an 8-character span put
   its whole text unit in front of the model."* §8.4 keeps complete extracted text local. **The model
   sees `value` and nothing around it.** A prompt telling the model to "use the surrounding context"
   is describing an input that no longer exists.
3. **The model does not see the file's existing facts.** The P8 SPEC's Site A row promises *"the
   file's existing facts with reliability states"* (`planning/parts/P8-llm-harness-validator/SPEC.md:234`).
   `_body` does not serialise them. Check 4 compares against facts the model was never shown, so a
   `CONTRADICTED_BY_STRONGER` rejection is, from the model's side, unforeseeable. **The prompt must
   not promise the model it can see what it will be judged against.**

---

## 5. Refusal — how `unknown` is represented and what happens to it

`Proposal.unknown: bool` (`facts/llm_seam.py:141-147`); the wire form is the `unknown` object with
its `insufficiency_statement` (`records.py:298-303`). At Site A:

- `validate_fact_proposal` takes the unknown branch **before any check runs**
  (`fact_validation.py:306-311`) — outcome `ABSTAIN`, no reasons, no citations checked.
- `apply_verdict` takes it before reading the verdict at all (`llm_seam.py:262-264`), because
  *"the model declined, so there was nothing to validate and a verdict about it would be a
  statement nobody made."* It writes an `unresolved` row with reason `model_returned_unknown`.
- `P8Verdict.may_propose` is False and `disposition` is `abstain` — no fact, no value row, no
  folder proposal.
- Abstention is reported **separately from rejection** in every P8 metric and *"is never counted as
  a failure by P8"* (`SPEC.md:321-323`). §6.10's own words, quoted in the SPEC: *"correct abstention
  is a successful outcome."*

The cost of declining is one `unresolved` row that a person can see. The cost of guessing is an
`llm_supported` fact that becomes a folder name. **The prompt must make declining the cheap,
default, explicitly-approved move, and must say what it costs — which is nothing.**

---

## 6. The requirements table

| # | Requirement | Source | How a prompt satisfies it |
|---|---|---|---|
| R1 | The template must supply its own terminator; the dossier's `{` follows its last byte with no separator. | `records.py:70-73` | End with a newline and an explicit "The dossier follows." line. |
| R2 | The prompt must describe the dossier as the exact key set of `_body`, in sorted order, as compact JSON. | `dossier.py:118-136`, `canonical.py:47` | Name the twelve keys. Do not describe a "context" or "document" the bytes do not contain. |
| R3 | The only quotable text is `released_evidence[].value`. | `validation.py:165`, `records.py:248-254` | Say it once, in those words, with the key path. |
| R4 | A citation carries **exactly one** of `cited_span` or `metadata_field_name`, plus a non-empty `why_it_supports`. | `records.py:280-294` | Show both citation forms and say "exactly one". |
| R5 | `cited_span` must be a **substring** of that item's `value`; `metadata_field_name` must **equal** its `address`. | `validation.py:165-167` | "Copy the characters. Do not retype, reformat, or translate them." |
| R6 | `evidence_ref` must be a `released_evidence[].observation_key`, and must also be one of P6's observations for this file version. | `validation.py:144-160`, `fact_validation.py:217` | "Cite only keys that appear in `released_evidence`." |
| R7 | `payload.field` must be a member of `allowed_vocabulary`, spelled verbatim. | `fact_validation.py:204`, `domains.py:137` | "Copy the key. Do not translate it into a display name." |
| R8 | At most one claim per field. | `sites.py:208-213` | State it as a hard rule with the consequence. |
| R9 | `claims` must be non-empty; silence is expressed as an `unknown` claim, never as `[]`. | `sites.py:127` | "If you can support nothing, return one `unknown` claim per field you considered." |
| R10 | `payload.value` must be a JSON string. | `fact_validation.py:232` | Show a string. Never show a number, list, or object as a value. |
| R11 | The value must be the **minimal identifying substring**, not the phrase containing it. | **Nothing checks this** — see §9.1 | The prompt is the only defence. Needs an explicit length/scope rule and a counter-example. |
| R12 | The value's spelling becomes the stored value identity. | `llm_seam.py:272-274`, `values.py:140` | "Use the spelling the evidence uses." |
| R13 | An `unknown` claim names its field, carries `insufficiency_statement`, and carries no value and no citations. | `llm_seam.py:148-162`, `records.py:298-303` | Show the exact object. |
| R14 | `"unknown"` is present or absent. `"unknown": false` destroys the whole response. | `sites.py:150-157` | State the prohibition explicitly; a model taught JSON will reach for the boolean. |
| R15 | The response is JSON and nothing else — no fence, no preamble, no trailing note. | `sites.py:120-123` | First and last instruction. |
| R16 | One malformed claim rejects every claim in the response. | `sites.py:203-213` | Tell the model, so it prefers fewer claims to more. |
| R17 | No timestamps, dates, run ids, paths, corpus names, or anything else that varies between runs. | `fingerprint.py:32-47`, `SPEC.md:30-33` | The text is a constant. Anything varying belongs in the dossier. |
| R18 | No worked example drawn from one domain. The template is shared by every file in every schema. | `domains.py:140-176` (20 schemas) | If examples are used, they must be schema-neutral or cover several. |
| R19 | The prompt must state that declining is a success and costs nothing. | `SPEC.md:321-323`, `llm_seam.py:262-264` | Say so in those terms, not as a fallback. |
| R20 | The prompt must not offer a hedge, confidence score, or "possible" tier — Site A cannot express one. | `fact_validation.py:251-255` | Two moves only: claim with citation, or `unknown`. |
| R21 | One file, named by `subject_ref`. No folder, no path, no filing decision, no grouping. | `dossier.py:135`, §3.5 | "You are not deciding where anything goes." |
| **R22** | **The value's characters must come from a released value THE CLAIM CITES.** `field_glossary` is not one. | `value_grounding.py`, called at `fact_validation.py:244-252`; refuses with `VALUE_NOT_IN_CITED_TEXT` | "If the characters you want to propose are not sitting inside a released value, then no amount of reasoning about the file makes them citable." |

### 6.1 R22, added 2026-09-02: what it says, and what it does not close

**Why it is a requirement of its own and not a clause of R3 or R11.** R3 governs what text is
*quotable*; R5 the *span*; R10 the value's *JSON type*; R11 the value's *length*. `86` §4 checked
all four against the running validator and found that **none of them says the value's characters
must come from a released value at all** — a real span copied exactly will carry any value, and
`90` §2 measured 22 glossary words accepted that way. R22 is that missing sentence, written down so
a future revision cannot drop it as redundant prose.

**Exactly what the shipped check enforces**, so the requirement and the code cannot drift apart:

> A value is grounded when its characters — casefolded, with every non-alphanumeric character
> dropped — occur as a **contiguous whole-token run** of at least one `released_evidence[].value`
> whose `observation_key` appears in **this claim's own citations**. Either the raw proposed value
> or `cli.normalize_for_model`'s canonical form may ground it. A claim citing nothing that was
> released, and a value with no alphanumeric characters, are **not** grounded — absent means refuse.

Three details in that sentence are load-bearing and each is there for a reason recorded at the code:

- **The claim's own citations, not the whole dossier.** A dossier can release several items. A value
  grounded in one the model did not cite is a value the model did not say where it got, and the
  citation is the only place it says.
- **A token RUN, not a substring.** `form` is inside `information`, `formal` and `performed`;
  `field` is inside `fields`. A substring test over folded text accepts every one of those — a check
  that passes the defect it was written for.
- **Separators dropped rather than matched.** `PHYS 1401`, `PHYS-1401` and `PHYS1401` are one course
  code. `65` §4.2 is this project's record of what happens when one identity arrives as several
  spellings; a comparison that did not fold them would reject a correct answer over the spelling of
  a space.

**A correction to `90` §5, which is where this requirement was first sketched.** That sketch said
*"the value's characters must come from a released value"* and it was loose in two ways the shipped
check is not: it did not bound grounding to the **cited** items, and "characters" read literally
would forbid the separator folding the code performs on purpose. The wording above is the code's,
not the sketch's. **Neither difference is a disagreement between the rule and the check** — the
sketch was one line in a recommendation and the code is more careful than it was.

**What R22 does NOT close, stated here rather than left to be discovered:**

1. **S16 is narrowed, not closed.** Where an enumerated glossary word *also appears in the cited
   released text*, a lift and a find are byte-identical and both are accepted.
   `test_a_lift_and_a_find_stay_indiscriminable_when_the_word_IS_in_the_evidence` pins that variant.
   Several of the 22 enumerated words — *form*, *field*, *store*, *scan* — are ordinary English and
   will appear in real evidence. **R22 removes the lift that has no cover; it cannot remove the one
   that does.**
2. **S2 is not closed, and no rule built on characters can close it.** `the committee` IS in the
   cited prose. What is wrong with proposing it for `instructor` is that a committee is not an
   instructor — a judgement about *meaning*. R22 is a comparison of *characters* and says so in as
   many words, so that nobody later reads a passing value as a grounded one.
   `test_s2_the_value_is_never_compared_to_the_evidence_it_cites` now asserts both halves: the value
   from nowhere is refused, and S2 itself is still accepted.
3. **S1 is narrowed to the over-quotation case**, which is R11's business and not R22's. The whole
   released line contains the right characters, so it is grounded and always will be. R11 remains
   prompt-only.
4. **Three classes of correct answer are refused**, and a prompt cannot talk a model out of two of
   them: a morphological variant of a word that is on the page, a value proposed only in this
   deployment's canonical spelling when the raw one was never written, and any script that does not
   separate words with a character (Han, Kana, Thai) — where the whole run is one token. All three
   are asserted in `tests/p8/test_p8_value_grounding.py` rather than left as a caveat.

**The known gap, in the terms `90` §7 stated it.** Nothing detects a glossary entry that *starts*
enumerating. `tests/p8/test_p8_glossary_as_value_source.py` re-reads the shipped glossary and fails
if a listed word leaves an entry, so the recorded hazard cannot rot — but a sixth entry that begins
listing its own candidate values tomorrow enters silently, and R22 will narrow it exactly as far as
it narrows the other five and no further.

---

## 7. Stress cases

Each row: the input the model faces → what a correct answer is → which check catches a wrong one.

| # | Input shape | Correct answer | What catches a wrong answer |
|---|---|---|---|
| S1 | Released value is `"PHYS1401 Problem Set 4"`; `subject` is allowed; no stronger `subject` fact exists. **The observed `qwen2.5:3b` failure.** | `{"field":"subject","value":"PHYS1401"}` citing span `PHYS1401`. | **Nothing.** `normalize_for_model("subject", "PHYS1401 Problem Set 4")` returns the string unchanged (verified, §9.1); the span is a substring of the value; no stronger fact exists. It is `ACCEPT_DIRECT` and becomes a folder name. **Prompt-only (R11).** |
| S2 | Released evidence is a page of prose supporting nothing in `allowed_vocabulary`. | One `unknown` claim per field considered, each with an `insufficiency_statement`. | Nothing catches a *plausible* invented field-value pair beyond check 1, and check 1 only fires if the field is outside the list. Prompt-only (R19). |
| S3 | Two released items support two different values for `subject` — `"PHYS1401"` and `"ASTR1002"`. | Pick the better-supported one and cite it, **or** `unknown` with a statement naming the ambiguity. Never two claims. | Two claims about one field → `SCHEMA_INVALID` for the **whole response** (`sites.py:208-213`). Catches it loudly and destructively. |
| S4 | The value the model wants is in the store's raw text but not inside any `released_evidence[].value` (redaction, or a narrower span). | `unknown`. | `CITATION_SPAN_MISMATCH` (`validation.py:165`). The old `context_before` framing of this case is now impossible: the windows are gone from the record (`records.py:248-254`), so there is no visible-but-uncitable text left. |
| S5 | The model names `course_code`, which is not in `allowed_vocabulary` (the key is `subject`). | Use `subject`, or `unknown`. | `FIELD_NOT_IN_ACTIVE_SCHEMA` → reject (`fact_validation.py:204`). Clean. Note the model has no glossary telling it that `subject` means a course code. |
| S6 | Released value reads `"PHYS 1401"`; a stronger `direct` fact already says `subject = PHYS1401`. | `{"field":"subject","value":"PHYS 1401"}` is *correct against the evidence* and check 4 passes — `contradicts_stronger` canonicalises both to `PHYS1401` (`cli.py:507-535`). | Check 4 correctly does **not** fire. But `apply_verdict` then stores `"PHYS 1401"` raw as the canonical value (§9.2) — two value rows for one course, which is `65` §4.2's defect reappearing one layer up. Prompt mitigates (R12); code must fix. |
| S7 | The model proposes `{"field":"subject","value":"Spring 2026"}`. | `{"field":"term","value":"Spring 2026"}`, if `term` is allowed. | `VALUE_NOT_NORMALIZABLE` — the `subject` slot's `matches` predicate rejects a term (`cli.py:502`, verified: returns `None`). One of the few wrong-field cases check 3 actually catches. |
| S8 | The model writes a fluent quotation that is not in any released value. | `unknown`, or a real substring. | `CITATION_SPAN_MISMATCH` (`validation.py:165`). Reliable. |
| S9 | The model cites an `evidence_ref` present in `evidence_items` but with no `released_evidence` entry. | Cite a released key, or `unknown`. | `CITATION_NOT_IN_DOSSIER` (`validation.py:152-157`). |
| S10 | The model fills both `cited_span` and `metadata_field_name` "to be safe". | Exactly one. | `Citation.__post_init__` raises → `parse_citation` returns `None` → **whole response** `SCHEMA_INVALID` (`records.py:286-294`, `sites.py:167`). |
| S11 | The model returns `{"claims": []}` because it found nothing. | One `unknown` claim per field considered. | `SCHEMA_INVALID` (`sites.py:127`). A model that declines the *wrong way* is scored identically to one that emitted garbage. |
| S12 | The model wraps the JSON in ` ```json ` or prefixes "Here is my answer:". | Bare JSON. | `SCHEMA_INVALID` (`sites.py:120-123`). The most likely 3B failure of all. |
| S13 | The model emits `"unknown": false` alongside a real claim. | Omit the key entirely. | **Whole response** `SCHEMA_INVALID` (`sites.py:150-157`). The code comment records that this used to be worse: the old guard read every falsey value as an abstention and threw the payload away. |
| S14 | The evidence is an EXIF/metadata observation, not body text. | `metadata_field_name` **equal to** that item's `address`, `cited_span` null. | `CITATION_SPAN_MISMATCH` if the model retypes the address or invents a field name (`validation.py:167`). Exact equality, not substring. |
| S15 | `value` is emitted as a number or a list — `{"field":"creation_date","value":2026}`. | A string. | `VALUE_NOT_NORMALIZABLE` (`fact_validation.py:232`). |

| **S16** | A value lifted out of `field_glossary` prose: the model cites a real span and proposes a word that appears only in the glossary's own enumeration of what a field contains — `media_type` is *"photo, screenshot, scan, video"*. **Added 2026-09-02**; `86`'s fifteen are unchanged. | `unknown`, or a value that is in the cited released text. | `VALUE_NOT_IN_CITED_TEXT` (R22), **where the word is not also in the cited text**. Where it is, nothing catches it and nothing can — §6.1. Measured in `90` §2: 22 enumerated words across five entries, 7 of 23 schemas exposing at least one. |

**The three most likely to break a 3B model**, in order: **S12** (prose or a code fence around the
JSON — a formatting failure, not a reasoning one, and it costs the entire response), **S1** (the
whole line as the value — no check stops it, and it is the failure already observed on this
machine), and **S11/S13** (declining in a shape that is scored as garbage rather than as the correct
abstention it was meant to be).

---

## 8. What the prompt must NOT say

| Must not | Why |
|---|---|
| Anything that varies between runs — a date, a time, a run id, a file path, a corpus name, a machine name. | The fingerprint is the prompt's identity (`fingerprint.py:32-47`) and §8.5's replay compares two runs of the same one (`SPEC.md:30-33`). A varying prompt makes every run its own experiment and every historical audit record unresolvable. |
| "Today is…", "the current date", or any instruction to reason about now. | Same, and the model has no clock in the dossier. |
| A worked example from one domain (academic, finance, photos). | 20 schemas share this template (`fields.py: DOMAIN_FIELDS`). A PHYS1401 example biases every household, contractor, and clinic corpus toward reading its evidence as coursework. |
| Any glossary of field meanings that goes beyond what `allowed_vocabulary` carries. | 56 catalogue rows and 20 schemas cannot fit, and a partial glossary teaches the model that the fields it was taught are the real ones. If a glossary is needed, it belongs in the dossier per file, not in the permanent template — which is a **decision for the owner, not a research finding.** |
| Any promise that the model can see the file's existing facts, its folder, its path, or its neighbours. | `_body` serialises none of them (`dossier.py:118-136`). Check 4 judges against facts the model was never shown. |
| Any reference to `context_before`, surrounding text, or "the rest of the document". | Removed from the record (`records.py:248-254`). The model sees `value` and nothing else. |
| Any offer of a confidence score, a "possible" tier, a "maybe", or a hedge field. | Site A produces `accept_direct`, `reject`, `abstain` and nothing else (`fact_validation.py:251-255`). A hedge the machine cannot express becomes either an unwarranted fact or a schema violation. |
| Any invitation to propose a folder, path, category, or grouping. | §3.5: *"or make a free-form filing decision."* Site A's scope is `file` and its output is one field-value pair. |
| Any instruction to "be helpful", "do your best", "make a reasonable guess", or "if unsure, choose the most likely". | This is the sentence that produces S1. §3.6's requirement is the opposite: a model that cannot cite sufficient evidence **must** return unknown. |
| Any claim that passing validation means the answer is right. | The validator checks grounding, not truth. Telling the model what the checks are so it can answer correctly is necessary; telling it that satisfying them is the goal turns the checks into a target. |
| Any output format other than one JSON object — no explanation, no fence, no trailing summary. | `json.loads` over the whole byte string (`sites.py:120-123`). |

---

## 9. Three things the prompt cannot fix

These are code findings, established while researching the above. They belong in `72`'s ledger, not
in a prompt.

### 9.1 Check 3 does not bound a value, and for most fields it does nothing at all

`cli.normalize_for_model` (`src/cli.py:465-505`) looks up a `DirectSlot` for the field. Only two
slots exist in this deployment — `subject` and `term` (`cli.py:302-325`). **A field with no slot
gets whitespace collapsed and is returned**, which the docstring defends on §3.5 grounds: inventing
a rule at the model's boundary is what §3.5 forbids. The consequence is that for 54 of 56 catalogue
fields, check 3 rejects only the empty string and the non-string.

Run against the live function:

```
normalize_for_model('subject', 'PHYS1401 Problem Set 4') -> 'PHYS1401 Problem Set 4'
normalize_for_model('subject', 'PHYS 1401')              -> 'PHYS1401'
normalize_for_model('subject', 'Spring 2026')            -> None
normalize_for_model('term',    'PHYS1401')               -> None
normalize_for_model('purpose', 'university application') -> 'university application'
normalize_for_model('subject', 'a' * 300)                -> 'a' * 300
```

The exact failure that prompted this research — the whole line as the value for `subject` — **passes
check 3.** It is caught only by check 4, and only if a stronger `subject` fact already exists, in
which case the record reads `CONTRADICTED_BY_STRONGER` — which says the evidence disagreed, when in
fact the model agreed and over-quoted. If no stronger fact exists, it is `ACCEPT_DIRECT`. The prompt
is the only thing standing between a 3B model and a folder named `PHYS1401 Problem Set 4`.

### 9.2 The model's own spelling becomes the stored value identity

`apply_verdict` writes `ensure_value(..., canonical_value=proposal.value, ...)`
(`facts/llm_seam.py:272-274`) — the **raw** model string, not `normalize_for_model`'s output. The
value id is derived from that string (`facts/values.py:140`). So `PHYS 1401` and `PHYS1401` become
two value rows for one course, which is exactly the identity-splitting defect `65` §4.2 recorded
four files falling into. `contradicts_stronger` was written specifically to canonicalise before
comparing; the writer one line later does not. The prompt can ask the model to copy the evidence's
spelling (R12); it cannot make two spellings one value.

### 9.3 Nothing in `src/` builds a Site A dossier, so nothing sets `allowed_vocabulary`

`A_FACT` appears only inside `llm_harness` (`harness.py`, `sites.py`, `validation.py`,
`vocabulary.py`). No caller constructs a Site A `DossierRequest`. When one is written, it must set
`Dossier.allowed_vocabulary` to **the same tuple** that `FactRequest.allowlist` carries: the model
reads `allowed_vocabulary` (`dossier.py:119`) and check 1 judges against `request.allowlist`
(`fact_validation.py:204`), and nothing asserts they are equal. `domains.active_field_allowlist`'s
docstring already anticipates this — *"Task 17 hands this exact tuple to P8, so the allowlist is one
computation and not two"* (`domains.py:143-144`) — but the equality is documented, not enforced.
Two lists here means the model is measured against one and validated against another, and every
correct answer to the list it was shown is rejected.

The oracles themselves are no longer missing: `72`'s R7 records `normalize`/`contradicts` as OPEN,
and both now exist at `src/cli.py:465` and `src/cli.py:507`. That row is stale.

---

## 10. What is still owed before a prompt can be approved

**Status as of 2026-09-02**, because a list that says "still owed" about settled things misleads the
decision it exists to serve. **Item 1 is settled** — the owner ruled for the second option and
`src/llm_harness/library/field_glossary.json` shipped (`eec74a1`); the cost of that ruling is S16
and §6.1. **Item 3 is done** — `86` ran all fifteen against the real validator with no model, and
`90` added the sixteenth. **Item 2 is still open**: R11 remains prompt-only. R22 narrowed the
neighbouring hole but did not touch R11, because the over-quoted value contains the right characters
and is grounded. The list below is the original text and is not rewritten.

1. **A glossary decision.** 56 field keys reach the model as bare strings. Either the template
   carries meanings (and cannot, at 20 schemas), the dossier carries them per file (a `_body`
   change, and a new `dossier_id` for every existing dossier), or the prompt tells the model to
   decline any field whose meaning is not obvious from its key. All three are the owner's call.
2. **A value-scope rule with teeth.** R11 is prompt-only today. §9.1 says why that is fragile.
   Whether check 3 should bound a value's length or shape is a P6/deployment decision.
3. **The stress suite.** The 15 cases in §7 are recorded response bytes plus an expected
   `(outcome, reasons)` pair. They can be written against `fixtures._bytes` and run without a model,
   which means the prompt can be stress-tested before it is ever fingerprinted.
