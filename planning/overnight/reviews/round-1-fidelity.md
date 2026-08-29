# Round 1 — contract fidelity

Date: 2026-08-21 (overnight)
Lens: **does the plan say what the SPEC says, and does the SPEC say what the design says?**
Subjects: [`../../parts/P6-facts-facets/PLAN-SKELETON.md`](../../parts/P6-facts-facets/PLAN-SKELETON.md) (1,621 lines) ·
[`../../parts/P7-privacy-consent-gate/PLAN-SKELETON.md`](../../parts/P7-privacy-consent-gate/PLAN-SKELETON.md) (1,370 lines)
Contracts: each part's `SPEC.md` · Source of truth: [`../../00-database-agent-product-design.md`](../../00-database-agent-product-design.md)
Settled seams (not re-opened): [`../../22-p1-p7-connection-contract.md`](../../22-p1-p7-connection-contract.md)

Method: every quotation in both plans extracted mechanically and matched against the source of
truth and the structured rendering, exact-first then punctuation-normalized, with the design's own
text printed beside any inexact match. Every closed vocabulary counted against the design's list.
Every Done-means item opened against the task the coverage table names. Every code claim executed —
`inspect.signature`, `dataclasses.fields`, `ast`, live imports — never read from a PLAN. Token
absence checked by AST walk, never by scanning source text.

---

## Verdict

**Both plans can be executed as faithful to the design, and neither invents a mechanism the design
does not warrant.** The quotation layer is in better shape than this project's history predicts:
across ~2,950 lines of plan, **every quotation attributed to the design is verbatim except three**,
and two of those three are punctuation. The plans' own SPEC-vs-design sections found real
divergences and got them right — P6's F2/F3/F4 naming family and P7's `filename` are all confirmed
against the design, as is P7's catch that the SPEC's "verbatim from §8.4" rendering is not verbatim.
The coverage tables are honest: all thirty P6 items and all thirteen P7 items appear, the five P6
items that are blocked say so, and the four P7 items that are not provable inside P7 say so and name
the downstream item that closes them. That is unusual and it should be said plainly.

**The single biggest fidelity risk is not a quotation — it is P6's `fields` catalogue.** Done-means 2
closes it to §3.11's table plus the six universal fields plus `download_session`, "and no field
outside them." §3.8 — a section P6's own slice table says it owns — names four role fields
(`authored_by`, `target_school`, `our_firm`, `client`) that appear in **no** §3.11 row. Done-means 13
and Done-means 22 both require `authored_by` to exist; Task 2's own test text requires
`destination_eligible = FALSE` "for every authorship and creator-identity field." **Task 2 as written
forbids the field that Tasks 9 and 24 are required to test.** This is the same defect the plan
already found three times (F2 `subject`, F3 `capture date`, F4 `document type`) — it is the fourth
and largest instance, it was missed, and unlike the other three it is not a question about which of
two design names wins: §3.8 states the fields outright and nothing in the plan lets them exist.

Second-largest: **four of the seven fields Task 2 creates have no producer anywhere in the plan.**
`file type` appears zero times in 1,621 lines. `language` appears only inside the negative guard that
forbids a language *heuristic*. `creation date` appears only inside the F3 discussion. `sensitivity
status` appears only inside the OQ11 row. The connection contract's §5 is explicit that "**Any part
added from here must carry a check that every column it publishes has a writer, or state plainly
that it does not yet**" — P6's plan carries neither. P7's plan does exactly the right thing on the
same seam (Task 4 injects a `SensitivityStateWriter` and reports that P1 publishes none), which is
what makes the P6 omission visible as an omission rather than a convention.

---

## Findings, most severe first

### F-1 (HIGH) — P6: §3.8's four role fields cannot exist under Done-means 2, and two Done-means items require one of them

**Plan:** `PLAN-SKELETON.md:571` (Task 2 `Produces`), `:584` (Task 2 test text), `:748` (Task 9
`AUTHORSHIP_FIELDS`), `:1276` (coverage row 13), `:1285` (coverage row 22).

**Design (§3.8), verbatim:**

> The agent should model these as distinct facets, such as `authored_by` and `target_school`, or
> `our_firm` and `client`.

**Design (§3.11)** gives six domain rows. `authored_by`, `target_school`, `our_firm` and `client`
appear in none of them:

| Domain | Fields |
|---|---|
| Academic | school, term, course, instructor, work type |
| College applications | target university, application cycle, application document type, purpose |
| Research | project, stage, artifact type, lab, venue |
| Finance | institution, account type, tax year, record type |
| Photos | capture year, event, location, people, camera information, media type |
| Code | project, repository, programming language, artifact type |

**What the plan says instead.** Task 2 (`:582-584`): "the catalogue is exactly the six §3.11 universal
fields, plus `download_session`, plus the six §3.11 domain rows verbatim — and **nothing else**."
Then, four lines later in the same paragraph: "That `destination_eligible` is `FALSE` for every
authorship and creator-identity field (§3.8)." A catalogue that contains nothing else contains no
authorship field. Task 9 must prove that a human author name "may populate an authorship role field
and **nothing else**"; Task 24 must prove "an `authored_by` value is never returned as
destination-eligible." Neither is constructible.

**Status:** CONFIRMED — read from §3.11's table and §3.8's sentence, and from the plan's own Task 2.

**What should change.** The catalogue must carry §3.8's four role fields, or Done-means 2's "no field
outside them" must be restated as "no field outside §3.11 **and §3.8**". This is not OQ4's question —
§3.8 names the fields directly and P6's design-slice table claims §3.8. It belongs beside F2/F3/F4 in
NEEDS JOSEPH 3 as the fourth (and only non-optional) member of that family.

---

### F-2 (HIGH) — P6: four of the seven fields Task 2 creates have no writer, and the plan carries no writer check

**Plan:** `PLAN-SKELETON.md:571` (Task 2 `UNIVERSAL_FIELDS`), and the absence throughout.

**Design (§3.11), verbatim:**

> The product should have a small shared set of universal file facts, such as file type, creation
> date, language, duplicate family, version family, and sensitivity status.

**Settled seam being violated** — [`22-p1-p7-connection-contract.md`](../../22-p1-p7-connection-contract.md) §5:

> Any part added from here must carry a check that every column it publishes has a writer, or state
> plainly that it does not yet.

and §6, check 2: "Every published column has a writer, or a named part that will write it."

**What the plan says instead.** Producers exist for `duplicate family` and `version family` (Task 14),
`download_session` (Task 15) and Photos `event` (Task 16). For the remaining four, counted over the
whole plan:

| Universal field | Occurrences in the plan | Producer task |
|---|---|---|
| `file type` | **0** | none |
| `creation date` | 3 — all inside the F3 `capture date` discussion | none |
| `language` | 3 — all inside Task 19's "no **language** check" guard and A10's `language_quality_heuristic` | none |
| `sensitivity status` | 2 — both inside the OQ11 row | none |

Task 25's guard list does not include "every published field has a producer."

**Status:** CONFIRMED — counted with `grep -c` over the plan, then each occurrence read in place.

**What should change.** Either name the producing task for each (`file type` and `creation date` are
plausibly Task 8's direct slots from P1's `mime_type` / `detected_format` / `observed_timestamps`),
or add the row to Deferred and say plainly that P6 publishes the field and does not yet write it —
which is exactly the discipline P7's Task 4 applies to `files.sensitivity_state`. Add the check to
Task 25.

---

### F-3 (HIGH) — P6: OQ10 is answered by omission — no legal `unresolved` reason can name an equal-rank refusal

**Plan:** `PLAN-SKELETON.md:645` (Task 5, the thirteen reasons), `:1351` (open-question row 10),
`:1042-1050` (Task 17's five verdicts and five reasons).

**SPEC (Open question 10), verbatim:**

> §3.13 orders the six states but does not define the comparison for two equal-rank contradicting
> facts — two `validated` facts asserting conflicting course codes on one file. Reject both, surface
> both as competing candidates, or defer to the internal score §3.13 permits but declines to make
> authoritative?

**What the plan says instead.** The open-question table marks OQ10 "**OPEN** — Task 17's contradiction
check refuses to decide and writes `unresolved`." But Task 5 fixes `UNRESOLVED_REASONS` at exactly
thirteen and its test must prove "a fourteenth is refused." The only contradiction reason among the
thirteen is `contradicted_by_stronger_fact` — which by its own name cannot describe two facts of
equal rank. Task 17's enumeration is explicit: "five verdicts, five reasons, no shared 'rejected'
bucket," and none of the five is an equal-rank case.

So the plan's stated OQ10 behaviour has no legal record to write. An implementer has two exits and
both answer the question: write `contradicted_by_stronger_fact` (asserting one of two equal-rank
facts is stronger — OQ10's third option, by fiat), or write nothing (violating B7, which exists
precisely so a refusal is never a missing row).

**Status:** CONFIRMED — the thirteen reasons enumerated from the SPEC and re-read in Task 5; Task 17's
five reasons read in place.

**What should change.** Say in the plan which record an equal-rank contradiction produces while OQ10
is open. The honest shape is a fourteenth reason that names the condition without ranking it
(`equal_rank_contradiction`) plus a Task 25 assertion that no code path picks a winner — that keeps
OQ10 open *and* satisfies B7. Whatever is chosen, it must be stated: this is currently the one place
where holding a question open and writing a required record are incompatible.

---

### F-4 (HIGH) — P6: OQ3 is answered by construction in Task 2, while Task 25 asserts it is open

**Plan:** `PLAN-SKELETON.md:571` (Task 2 `FIELD_SCOPES` / `DOMAIN_FIELDS`), `:1181` (Task 25's
open-question guards), `:1345` (open-question row 3).

**SPEC (Open question 3), verbatim:**

> Is `purpose` a universal field or an Applications-domain field? §3.9 requires it to be
> "first-class"; §3.11's universal list omits it and places it only under College applications.

**What the plan says instead.** Task 2 produces `FIELD_SCOPES` (`universal`, `academic`,
`college_applications`, …) and `DOMAIN_FIELDS: Mapping[str, tuple[str, ...]]` built from "the six
§3.11 domain rows verbatim." §3.11's College-applications row contains `purpose`; the universal list
does not. Every `FieldRow` carries a `scope`. So the moment Task 2 is written, `purpose` has
`scope = college_applications` — which is OQ3's second answer. Task 25 then asserts OQ3 is open. Both
tests cannot pass unless `scope` for `purpose` is left unset or parameterised, and the plan says
nothing about that anywhere.

**Status:** CONFIRMED as an internal contradiction between Task 2 and Task 25. PLAUSIBLE that a
nullable `scope` on that one row resolves it without a decision.

**What should change.** Say how `purpose` is carried while OQ3 is open — the pattern Task 2 already
uses for `multiplicity` ("present as a column and **unanswered**") applies directly.

---

### F-5 (HIGH) — P7: the plan writes "the design wins" about `filename` and then builds the SPEC's answer, with OQ2 absent from NEEDS JOSEPH

**Plan:** `PLAN-SKELETON.md:1335-1339` (SPEC vs §8.4, item 1), `:597` (Task 2 `ITEM_KINDS` (6)),
`:719-733` (Task 7), `:1259-1261` (open-question row 2), `:1345-1367` (NEEDS JOSEPH, seven items).

**Design (§8.4), verbatim — both halves:**

> Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group
> memberships, and raw sensitive values should remain local.

> When a cloud model is used, the engine should send only a compact dossier relevant to the current
> question: selected excerpts, redacted identifiers, candidate labels, non-sensitive metadata, and
> evidence references.

Five releasable kinds. `filename` is not among them.

**What the plan says instead.** Its own SPEC-vs-§8.4 section (`:1335`) states the divergence correctly
and concludes: "recorded here because **the design wins and the design does not name it**." Then
Task 2 fixes `ITEM_KINDS` at six and its test must prove the vocabulary "is exactly the SPEC's list in
the SPEC's order," and Task 7 builds a `Filename` dataclass and its permit/deny rule. The Global
Constraints add: "Adding a member is a P7 contract revision, not an implementation decision" — which
means removing one is too. And **OQ2 is the only one of the eleven open questions that does not
appear in the plan's NEEDS JOSEPH list**, despite being the one the plan itself says the design
decides against.

**Status:** CONFIRMED — the design's five counted from §8.4; the plan's six read from Task 2; the
NEEDS JOSEPH list read item by item.

**What should change.** Add OQ2 to NEEDS JOSEPH with the design text quoted, and state which task
changes under each answer. The SPEC's reason for resolving it (P8 and P11 cannot build without an
answer) is sound and the flagged reading is defensible — but a plan that says "the design wins" three
pages after building against the design is asserting two things at once.

---

### F-6 (MEDIUM) — P6: a fabricated §8.6 quotation, previously audited, carried into the plan

**Plan:** `PLAN-SKELETON.md:89`. **SPEC:** `SPEC.md:366`.

**Plan says:**

> §8.6: deferred work must be *"visible as deferred, never as 'understood and found unimportant'"*.

**§8.6 says** (00 and 01 identical in substance):

> The user interface should show the difference between completed work and deferred work. […] This
> makes the product's limitations legible and avoids the false impression that an unprocessed file
> was understood and found unimportant.

The string `visible as deferred` does not occur in either design document. The quotation compresses
two sentences and coins the first half.

**This was already found.** [`06-citation-audit.md:125`](../../06-citation-audit.md) flags exactly this
line of the SPEC: "Compresses two separate §8.6 sentences […] into one quotation." The SPEC was not
corrected and the plan inherited the compression verbatim.

**Status:** CONFIRMED — `str.find` over both design documents, whitespace-normalized.

**What should change.** Quote §8.6's two sentences, or drop the quotation marks. The obligation is
real either way; the citation is not. Note that the P7 plan quotes both halves of the same passage
correctly at `:55-56`, so the correct rendering already exists in this wave.

---

### F-7 (MEDIUM) — P7: a source-code quotation that is not in the source, at a line that is not the line, asserting a value that is not the value

**Plan:** `PLAN-SKELETON.md:469-471`, and again at `:1153` and `:1303`.

**Plan says:**

> `src/orchestrator.py:259` already passes `handling_class=file_row["sensitivity_state"]` with the
> comment *"P7's, and P7 is unbuilt. P1's column is the only source and it is NULL until a gate
> writes it."* Task 4 is what stops that being NULL.

**`src/orchestrator.py` says** (line 285, with the comment at 277-284):

```python
                       # §8.4's, and P7 is unbuilt. This passed P1's
                       # `sensitivity_state` -- a DIFFERENT field on a different
                       # record. Both are NULL on a live scan, so nothing failed and
                       # the name was still wrong: one concept wearing two names one
                       # column apart. The honest value is None because the class is
                       # unknown, not because another column happened to be empty.
                       handling_class=None,
```

Three errors in one citation: the line is 285, not 259 (259 is inside the dataless loop's `route`
call); the value is `None`, not `file_row["sensitivity_state"]`; and the quoted comment text does not
appear in the file. The change is the one
[`22-p1-p7-connection-contract.md`](../../22-p1-p7-connection-contract.md) §1 records — "**was being
fed P1's `sensitivity_state`, fixed this pass to `None`**" — i.e. a settled seam the round brief says
not to re-open, which the plan is describing in its pre-fix state.

**Consequence, not just a citation error.** Task 22 must assert "after classification the Wave-2
bundle's `handling_class` is non-null, closing the loop `src/orchestrator.py:259` left open." With
`handling_class=None` hard-coded, that assertion cannot pass without an edit to `src/orchestrator.py`
— a file the plan's Global Constraints say P7 does not touch ("P7 creates and modifies no file owned
by another part"), and which appears in no task's `Files:` line. P6's Task 26 is the only task in the
wave that claims the orchestrator.

**Status:** CONFIRMED — file read, line numbers checked, `grep -n handling_class` returns only 285.

**What should change.** Restate the three citations against the current file, and either give P7 a
task that changes the orchestrator (coordinating with P6 Task 26, which already owns that file) or
restate Done-means 13's bundle clause as belonging to whoever wires the classification writer.

---

### F-8 (MEDIUM) — both plans: "§3.1's five" origins — §3.1 names twelve provenance sources, and the five are a reconstruction

**Plan (P6):** `PLAN-SKELETON.md:621` (Task 4 `Produces`). **Plan (P7):** `PLAN-SKELETON.md:497`
(the reproduced P6 shape).

**Plan says:**

> `FACT_ORIGINS: tuple[str, ...]` (§3.1's five: deterministic extractor · rule · LLM interpretation ·
> user correction · user-approved folder)

**§3.1 says, verbatim:**

> Every fact preserves where it came from: a filename, document title, heading, table cell, page of
> extracted text, EXIF field, OCR region, archive manifest, user-approved folder, deterministic rule,
> LLM interpretation, or explicit user correction.

That is **twelve** sources, not five. Three of the five (`user-approved folder`, `LLM interpretation`,
`user correction`) are §3.1's; `deterministic extractor` and `rule` are a split of §3.1's single
`deterministic rule` borrowed from §3.5's three producers ("Deterministic extractors", "Rules", "The
LLM"). The other seven §3.1 sources — filename, document title, heading, table cell, page of extracted
text, EXIF field, OCR region, archive manifest — are P4's `source_type` / `zone` vocabulary, which is
why they drop out. The reconstruction is reasonable; the attribution is not.

**Status:** CONFIRMED — §3.1's list counted item by item in both design documents.

**What should change.** Attribute it as "§3.5's three producers plus §3.1's two user-side origins," or
cite both sections. As written, a reader checking §3.1 for five origins finds twelve sources and
concludes the plan or the design is wrong.

---

### F-9 (MEDIUM) — P7: `completeness_implies_unclassified` is a nine-value decision table with no design source and no Deferred row

**Plan:** `PLAN-SKELETON.md:619` (Task 3 `Produces`), `:630-633` (its test obligation).

**Plan says:**

> And that the mapping from P4's nine `completeness` values to `unreadable_unclassified` is stated
> explicitly per value rather than by an `in`-check over a set the author guessed — including the case
> of a file with **no run row at all**, which is what a dataless file has.

**SPEC (Contract in, from P5)** states exactly one of the nine:

> An unreadable extraction result maps to handling class `unreadable_unclassified`, and is distinct
> from an empty one — §2.4: "an empty extraction result is different from an extractor that does not
> yet exist."

**§8.4 states none of them.** It names five handling classes and never mentions extraction
completeness. The other eight values — `complete`, `capped`, `partial`, `metadata_only`, `deferred`,
`unsupported`, `failed`, `dataless` — have no stated mapping anywhere in the design or the SPEC, and
the mapping decides whether a real file is releasable. That is a classification rule, in a part whose
first Global Constraint is "**P7 owns no detection rule**" and whose Deferred table's first row is
"The sensitivity detection rules themselves."

**Status:** CONFIRMED — nine values read from `evidence_shape.runs.COMPLETENESS`; §8.4 read in full in
both design documents; the SPEC's Contract-in row read in place.

**What should change.** Add a Deferred row ("which `completeness` values imply `unreadable_unclassified`")
and hold the table as an injected mapping with no default, the same way every other unauthored P7
value is held. Task 3's instruction to state it "explicitly per value" is right about the *form* and
silent about who authors it.

---

### F-10 (MEDIUM) — P7: `CEILING_KEYS` is stated as fifteen; it is sixteen, and the sixteenth is a ratified decision

**Plan:** `PLAN-SKELETON.md:243` and `:280-281`.

**Plan says:**

> `database_agent.budget  CEILING_KEYS: tuple[str, ...]  (fifteen)`

and

> **`budget.CEILING_KEYS` holds `model.max_dossier_tokens_per_call`** and `set_ceiling` raises
> `KeyError` on a sixteenth key.

**Live:** `len(database_agent.budget.CEILING_KEYS) == 16`. The sixteenth is `evidence.context_window`,
added by **B4** (ratified 2026-08-20, recorded in
[`16-p4-p5-catalogue-recheck.md:39`](../../16-p4-p5-catalogue-recheck.md)): "Context window = P1 16th
key **`evidence.context_window`** and in run `config` (fingerprinted). P4 holds no number —
**Shipped:** `src/database_agent/budget.py` (16 keys)." `set_ceiling` raises on a *seventeenth*.

P6's plan states sixteen and is correct (`PLAN-SKELETON.md:239`).

**Status:** CONFIRMED — executed `len()` against the live module.

**What should change.** Sixteen, and the raise is on a seventeenth key. Nothing else in P7 turns on
it, but a ratified decision reaching one plan and not its neighbour is defect class 3 in miniature.

---

### F-11 (MEDIUM) — P7: Task 14 adds a field to a B2-adopted shape that P8's SPEC publishes with two

**Plan:** `PLAN-SKELETON.md:453-457`, `:920` (Task 14 `Produces`).

**Plan says:**

> Task 14 therefore adds `consent_request_id` to `NeedsConsent` and to the `consent_requested` audit
> record. **This is a Contract-out gap, reported; the field name is P13's, not invented here.**

**P7 SPEC §6** publishes `NeedsConsent { requirement, options }`. **P8 SPEC:93** publishes it the same
way: `NeedsConsent  requirement · options: local_model | cloud_model | redacted_prompt | no_model_use`.
**B2** ([`04-resolutions.md`](../../04-resolutions.md)) is the reason both spell it identically: "P7's
shape is adopted verbatim."

The reasoning is right — Done-means 7 requires the audit log to show "a `consent_requested` event and
no `model_release` for that request until a choice is recorded," which needs a join key, and P13's
`subject_ref` is a `consent_request_id`. But the change lands in a plan, not in the two SPECs that
publish the shape, and it is not in NEEDS JOSEPH.

**Status:** CONFIRMED — both SPECs read; B2 read.

**What should change.** Amend P7 SPEC §6 and P8's reproduction of it, or route the field to P8 as a
seam item. A shape adopted verbatim on both sides cannot gain a field on one side only.

---

### F-12 (MEDIUM) — P7: Task 7 makes the always-local kinds unconstructible; Task 13 must reach `Denied(always_local_item)` "exactly"

**Plan:** `PLAN-SKELETON.md:719-733` (Task 7), `:905-913` (Task 13), `:1176` (coverage row 6),
`:1199-1207` (negative-tests table, nine rows).

**SPEC Done-means 6** requires denials "for at minimum: […] an always-local item (§8.4)."

**What the plan says.** Task 7: "each of the nine always-local names […] is **not expressible** as any
of the six item kinds, asserted by attempting to construct one and catching `AlwaysLocalRequested`,
one test per name, nine tests." Task 13: "One test per reason, eight tests, each reaching **exactly**
that reason and no other." `always_local_item` is one of the eight `DENIAL_REASONS`. If the item
cannot be constructed, no `ModelCallRequest` can carry it, and `Gate.release` can never return that
`Denied`. Coverage row 6 maps the reason to both tasks without noticing they use incompatible
mechanisms.

**Status:** CONFIRMED as a stated inconsistency between two tasks and the coverage row that joins
them. PLAUSIBLE that the intended split is "typed always-local item → unconstructible; an item that
*resolves* to always-local content → `Denied`" — the plan does not say so.

**What should change.** State the split, or drop `always_local_item` from `DENIAL_REASONS` and let
Task 7's construction-time refusal be the whole mechanism. Task 13's "eight tests, each reaching
exactly that reason" is the assertion that will fail first.

---

### F-13 (MEDIUM) — P6: coverage row 10 and Task 12 cite A03, which tests a `course` refusal, not a date refusal

**Plan:** `PLAN-SKELETON.md:832` (Task 12), `:462` (test-file map, `test_p6_dates.py … A03`),
`:1273` (coverage row 10).

**SPEC Done-means 10:** "`v2024`, a build number, and a ZIP code produce no date fact; `Spring 2025`,
`AY 2024-25`, and `Michaelmas Term 2024` each produce exactly one term fact (§3.10)."

**A03 as built** (`tests/eval/fixtures/adversarial/A03.json`) has two subjects and both forbid a
**course** fact:

```json
{"subject_ref": "A03::zip::course", "expected_outcome_kind": "abstained",
 "forbidden_value": {"field": "course", "value": "MA 02139"}, "text": "Ship to Cambridge MA 02139 by Friday."}
{"subject_ref": "A03::device::course", "expected_outcome_kind": "abstained",
 "forbidden_value": {"field": "course", "value": "XPS 13"}, "text": "Receipt for one XPS 13 laptop."}
```

Its `sections` are `["§3.5 (pattern plus \"syllabus\", …)", "§3.10"]` — it straddles both, but every
assertion it makes is Task 10's §3.5 context check. Task 12 (`dates.py`) has no A03 assertion to
inherit; Task 10 (`rules.py`) does.

**Status:** CONFIRMED — fixture read in full.

**What should change.** Move A03 to Task 10's test file, or note in Task 12 that A03 covers the
course-code half of §3.10's warning and that the date half has no fixture. The design's §3.10 sentence
covers both — "numbers that look like years but are course identifiers, version numbers, build
numbers, ZIP codes" — so the *obligation* is real; the fixture is not the one that proves it.

---

### F-14 (MEDIUM) — P6: the `field_key` spelling is unpinned, and the SPEC and the Done-means use different conventions

**Plan:** `PLAN-SKELETON.md:571-573` (Task 2 `FieldRow(field_key, …)`), `:1268` and `:1279`
(coverage rows 4 and 14).

**SPEC's `fields` example (`SPEC.md:201-202`):** `course, term, work_type, target_university,
authored_by, target_school, our_firm, client, purpose, project, event` — snake_case.

**SPEC's Done-means 4 and 14, and §3.11's table:** `work type`, `document type`, `target university`,
`capture year`, `media type`, `application document type` — spaced.

**Plan:** Task 2 requires "the six §3.11 domain rows **verbatim**" (spaced) and produces
`download_session` (snake). Across 1,621 lines the plan writes `work type` three times and `work_type`
zero times, so it has implicitly chosen spaced keys — while carrying `download_session`,
`authored_by` and `target_school` in snake. No task decides.

**Status:** CONFIRMED — counted over the plan; both conventions read in the SPEC.

**What should change.** One rule in Task 2: the `field_key` is snake_case and `display_name` is
§3.11's wording, or the reverse. This is defect class 1 in the plan's own list, one edit from being
closed, and it is the kind that is invisible until P9 or P10 reads a key that does not resolve.

---

### F-15 (LOW) — P7: §0 does not say "Each part owns its own tables within it"

**Plan:** `PLAN-SKELETON.md:18` (Architecture).

**Plan says:**

> inside P1's single local SQLite database (§0: *"Each part owns its own tables within it"*)

**§0 in full** says only:

> A local SQLite database acts as the durable working memory of the product. It records file
> identity, file state, extracted content, facets, evidence locations, structural relationships,
> destination nodes, taxonomy aliases, movement plans, user corrections, and undo history. […]

Neither design document contains the string, and §0 never mentions parts or table ownership. The
sentence is a project convention that originates in P1's SPEC (`P1 SPEC:298`, unquoted) and acquired
quotation marks in P2's and P4's PLANs, from which P7's plan inherited it. It is a good convention;
it is not §0.

**Status:** CONFIRMED — §0 read in full in both documents; `grep` over all of `planning/` finds the
string only in P1/P2/P4/P7 planning files.

**What should change.** Drop the quotation marks and cite P1's SPEC. Also worth correcting in P2's and
P4's PLANs, where it has been shipping unchallenged.

---

### F-16 (LOW) — P6: §5.5's quotation drops a word

**Plan:** `PLAN-SKELETON.md:1160`. **SPEC:** `SPEC.md:565`.

| | Text |
|---|---|
| **Plan / SPEC** | "three schools, five terms, twelve course branches" |
| **Design §5.5** | "three schools, five terms, **and** twelve course branches" |

An elision inside quotation marks with no ellipsis. Same class as the P10 finding at
[`06-citation-audit.md`](../../06-citation-audit.md) ("an item dropped mid-quote with no ellipsis").
**Status:** CONFIRMED.

---

### F-17 (LOW) — P6: two count errors in the preamble

**Plan:** `PLAN-SKELETON.md:96-97`.

> **Ten questions are open** in P6's SPEC (OQ1 and OQ12 closed; …). […] **Twenty-two rows are
> Deferred.**

The first sentence contradicts its own parenthesis: the SPEC lists ten numbered entries of which two
are closed, so **eight** are open — which is what Task 25 (`:1181`) actually guards, naming OQ3, OQ4,
OQ5, OQ6, OQ8, OQ9, OQ10, OQ11. The Deferred table carries the SPEC's twenty rows plus three new =
**twenty-three**, counted row by row. **Status:** CONFIRMED — both tables enumerated.

---

### F-18 (LOW) — P7: the green-substrate precondition is stale

**Plan:** `PLAN-SKELETON.md:214`: "`pytest tests/ -q` → **1231 passed**, confirmed 2026-08-21."

Run this pass: **1237 collected, 1237 passed in 41.3s.** Six tests have been added since the plan was
written and the substrate is green, so the precondition holds — but the number a reader would check
against no longer matches. **Status:** CONFIRMED — suite executed.

---

### F-19 (LOW) — P6: line citations into `src/orchestrator.py` have drifted

**Plan:** `PLAN-SKELETON.md:1364-1372` (F1). `run_wave2:138` — the `def` is at 135 and the
`no_usable_facts` parameter at 141. `orchestrator.py:211` for `_write(sink, result, written)` — the
call is at ~219. `dispatch.py:118-125`, `:131-133`, `:86-88` and `long_tail.py:204` are exact or
within one line. Every underlying claim is true; only the offsets moved. **Status:** CONFIRMED —
each line opened. Contrast with F-7, where the drift changed the claim.

---

### F-20 (LOW) — P6: the six states are given a strength ordering the design does not state, and `rejected`'s rule is cited to the wrong section

**Plan:** `PLAN-SKELETON.md:530-536` (Task 1's test obligations).

**Plan says:**

> That the strength order is `user_confirmed > direct > validated > llm_supported > possible` and that
> `rejected` has **no** strength — asking for it raises rather than returning a number, because §3.13
> makes it an exclusion, not a rank.

**§3.13 in the source of truth** is a flat description with no ordering claim:

> A user confirmed fact has been explicitly accepted… A direct fact was read from a reliable and
> explicit source… A validated fact was found by a deterministic rule and passed contextual checks…
> An LLM-supported fact was proposed by a language model… A possible fact is a useful but insufficient
> clue… A rejected fact is a proposal that the user or validator marked as incorrect.

Three of the four relations are supported elsewhere — §3.6's fourth check names "no stronger direct or
rule-validated fact," and §3.6 puts `possible` below everything — but **`direct` > `validated` is
stated nowhere**, and the "exclusion that must persist" property is §8.7's ("Rejected groups,
rejected destination matches, rejected labels… must be stored with the evidence that produced them.
Otherwise the system will repeatedly resurface the same attractive but incorrect grouping"), not
§3.13's. The plan turns a table's row order into a tested contract while OQ10 keeps equal-rank
comparison open. **Status:** CONFIRMED.

---

### F-21 (LOW) — P6: `DEGRADATION_ORDER` splits a rung the design keeps whole, and mixes two vocabularies

**Plan:** `PLAN-SKELETON.md:1035-1041` (Task 20).

`DEGRADATION_ORDER: tuple[str, str, str]` is `(direct, rule, llm)` — producer names — while the same
task's prose is "always attempts `direct`, then `validated`, and only then […] `llm_supported`" —
reliability-state names. Two vocabularies for one order, in one task.

**§8.6** puts the first two in **one** rung: "Direct facts and high-precision rules run first because
they are cheap and reliable." The design orders rules-and-direct *before* LLM; it does not order
direct before rules. Task 20 requires "the order is asserted from the call sequence rather than from a
docstring," which makes an unstated ordering a test. **Status:** CONFIRMED.

---

### F-22 (LOW) — P6: A10 is `dimension: extraction`, so it is not P6's gate either

**Plan:** `PLAN-SKELETON.md:456` (test-file map: `test_p6_usable.py … A10`), `:1009` (Task 19).

The plan correctly withholds A06 from P6's claims — coverage row 23: "A06 is filed under
`dimension: grouping`, so P6 cannot claim it as its own gate." A10 is `dimension: extraction` by the
same rule and gets no such caveat. Task 19's substantive use of A10 is sound (`forbidden_value:
{"triggered_by": "language_quality_heuristic"}` is verified present), but the case belongs to P5's
routing, not P6's fact stage. **Status:** CONFIRMED — all twelve fixtures' `dimension` fields read.

---

### F-23 (LOW) — P7: `unclassified` and `unreadable_unclassified` are one stem apart and Task 2 pins the other four, not these

**Plan:** `PLAN-SKELETON.md:591-599` (Task 2's `DENIAL_REASONS` and `HANDLING_CLASSES`), `:605-611`
(the four `protected` spellings).

Task 2 goes to real trouble over `protected`: "five strings, one stem, and no code that treats any two
as the same." The same hazard exists one vocabulary over — the handling class is
`unreadable_unclassified` and the denial reason is `unclassified` — and is not pinned. They are
genuinely different concepts (a state vs. a reason), which is exactly why the pinning test exists for
`protected`. **Status:** CONFIRMED.

---

### F-24 (LOW, SPEC only) — P6 SPEC misquotes §2.2's producer-metadata rule by one word

**SPEC:** `SPEC.md:471`: "Any other producer/creator/author metadata value is *supporting evidence,
not truth* (§2.2)."

**§2.2:** "PDF metadata should be treated as **supporting evidence, not as truth**."

The plan does not inherit it — Task 9 quotes only "should not be mistaken for meaningful content,"
which is exact. **Status:** CONFIRMED.

---

## Coverage verification table

Every item opened against the task the coverage table names, and the task's stated test obligations
read to confirm it proves the item.

### P6 — 30 Done-means items

| Verdict | Count | Items |
|---|---|---|
| **Verified** — the named task's stated test proves the item | **23** | 1, 2, 3, 6, 7, 8, 9, 11, 12, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 28, 29, 30 |
| **Blocked by a naming decision, and the plan says so** | **5** | 4 (F2), 5 (F3), 14 (F4), 22 (F5), 27 (F6) |
| **Mis-mapped** | **1** | 10 → Task 12 cites A03, which tests a `course` refusal (F-13). The §3.10 obligation is still provable; the fixture named does not prove it |
| **Unprovable as the catalogue is written** | **1** | 13 → requires `authored_by`, which Task 2's catalogue forbids (F-1) |

Task-header vs coverage-table consistency: every task's own `Done-means:` line agrees with the
coverage table except item 1, which the table maps to Tasks 2, 3 and 4 while only Task 4 declares it.
Tasks 2 and 3 do create the tables item 1 names, so the mapping is right and the task headers are
under-declared. Not a finding.

### P7 — 13 Done-means items

| Verdict | Count | Items |
|---|---|---|
| **Verified — fully provable inside P7** | **8** | 1, 2, 4, 5, 6, 8, 10, 12 |
| **Partial, and the plan names the downstream item that closes it** | **4** | 3 (→ P8 DM1), 7 (→ P8 DM13, P13 DM16), 9 (→ P11/P12), 11 (→ P8's own run) |
| **Verified with a caveat** | **1** | 13 — path one provable; path two is two clauses of four, stated |
| **Internally inconsistent within item 6** | — | the `always_local_item` reason (F-12) |

**Both coverage tables are honest.** No item is claimed that is absent, and no item is mapped to a
task that silently does not test it — the one mis-mapping (P6 item 10) is a wrong *fixture* inside a
task that does carry the obligation, and the two unprovable ones are both consequences of F-1, which
the plan did not know about. P7's "Fully provable inside P7?" column, in particular, is the more
useful of the two: it is a column most plans would not have written.

---

## Quotation audit

**Every quotation in both plans was extracted mechanically** (regex over `"…"`, `*"…"*` and `**"…"**`,
including multi-line spans) and matched against `00-database-agent-product-design.md` first, then
`01-product-design-structured.md`, then the SPEC set and the resolution documents. Loose matches were
re-printed beside the design's own text, character for character.

**Result: of every quotation attributed to the design across both plans, exactly three are not
verbatim, and one of those three is a fabrication.**

| Plan | Line | Quoted as | Design says | Class |
|---|---|---|---|---|
| P6 | 89 | §8.6: "visible as deferred, never as 'understood and found unimportant'" | "The user interface should show the difference between completed work and deferred work." + "avoids the false impression that an unprocessed file was understood and found unimportant" | **Fabrication** — `visible as deferred` occurs in neither design document. Already flagged in `06-citation-audit.md`; F-6 |
| P6 | 1160 | §5.5: "three schools, five terms, twelve course branches" | "three schools, five terms, **and** twelve course branches" | Elision with no ellipsis; F-16 |
| P7 | 18 | §0: "Each part owns its own tables within it" | §0 says nothing about parts or table ownership | **Fabrication** — a P1 convention quoted as design; F-15 |

**Everything else matched.** The only remaining divergences my matcher surfaced are, without
exception, one of three benign transformations, each verified individually against the design text:

- **sentence-final period added to a mid-sentence elision** — P6 `:33` ("Every fact preserves where it
  came from**.**", design has a colon), `:1127` and P7 `:685` ("The evidence database remains shared
  across plan versions**.**", design continues ", but the destination tree…"), P7 `:913` ("Every
  significant event affecting a file**.**", design continues "should be preserved in an append-only
  provenance log");
- **first letter lowercased to embed in a sentence** — P6 `:1056` and P7 `:178`/`:624` ("cost
  exhaustion must never turn into lower-quality automatic classification", design capitalises), P6
  `:1561` ("the validator then checks…"), P7 `:99` ("Enforced before content reaches any model");
- **curly quotation marks rendered as straight or single** — P6 `:1571` (§3.5's five context terms),
  P7 `:1049` and P7 SPEC `:34` (§8.4's "11 protected identity records" example).

Quotations of the SPECs, of `02-segmentation-map.md`, of `04-resolutions.md`, of
`10-i4-learning-ops.md`, of `11-ops-runtime.md`, of the P3/P4/P5/P8/P13 SPECs and of the catalogue
files were checked the same way and are exact, with one near-miss: P6 `:1591` renders P5's NEEDS
JOSEPH 1 as "Apple Vision only, macOS-only v1" where P5's SPEC B1 reads "**Apple Vision only;
macOS-only for v1.**"

**Ratification identifiers.** Every `Bn` / `Mn` / `Gn` / `Sn` / `On` / `MINOR n` / `A1`–`A4` / `B4` /
`B6` / `B8` / `C1` / `C4` / `D7` / `D11` / `N-6` / `I4` / `I6` / `W1` cited by either plan was resolved
to its defining document. **None is invented.** One is worth naming: **W1 is a finding in
`07-fidelity-audit.md`, not a Joseph ratification** — its own text is headed "Nearest faithful fix
(**not applied**)". P7's SPEC adopted the audit's recommendation word for word and the plan now writes
"the two-member floor W1 binds" and "§8.4's `must`, W1" alongside genuinely ratified identifiers. The
underlying `must` **is** the design's; the derived rule "where the design is silent on a redaction
default, the more redacting option is the default" is the audit's, and it is tested as hard contract
by Done-means 12. Worth Joseph's explicit sign-off rather than inheritance from an audit.

**Converse check — does either plan assert a ratification that does not exist?** No. The nearest thing
runs the other way: [`04-resolutions.md`](../../04-resolutions.md) **G7** says "P9 consumes it as
§4.2's fourth seed kind," and §4.2 says "A seed may be a strongly identified file, a validated shared
fact, a structural family, or a user-created starting point" — the photo event is not among them.
P6's SPEC corrects this explicitly ("**They are not '§4.2's fourth seed kind'** — an earlier draft
said so, and the design does not"), which is what 04's own closing rule requires ("where it and the
design differ, **the design wins**"). `06-citation-audit.md` reached the same conclusion
independently. The plan inherits the correction silently and asserts nothing false.

---

## Open questions the plan answered

The highest-severity category in this round. Three, plus one that is answered honestly.

| # | Question | Where the plan answers it | Severity |
|---|---|---|---|
| **P6 OQ3** | "Is `purpose` a universal field or an Applications-domain field?" | Task 2 (`:571`) builds `DOMAIN_FIELDS` from §3.11's rows verbatim; §3.11 places `purpose` under College applications and every `FieldRow` carries a `scope`. Task 25 (`:1181`) then asserts OQ3 is open. | **HIGH** — F-4 |
| **P6 OQ10** | "…does not define the comparison for two equal-rank contradicting facts" | Task 5 (`:645`) closes `UNRESOLVED_REASONS` at thirteen and refuses a fourteenth; none of the thirteen can name an equal-rank refusal. Any implementation of the plan's stated behaviour picks one of OQ10's three answers. | **HIGH** — F-3 |
| **P7 OQ2** | "Filename vs. path." | Task 2 (`:597`) closes `ITEM_KINDS` at six including `filename`; Task 7 builds the permit/deny rule. The plan's own SPEC-vs-§8.4 section says "the design wins and the design does not name it," and OQ2 is the only one of eleven missing from NEEDS JOSEPH. | **HIGH** — F-5 |
| **P6 OQ4** | "Are `subject` and `course` the same field…?" | Task 2's catalogue carries `course` and no `subject`, which is an answer — **but the plan states this outright** (F2), marks Done-means 4 "partly blocked," and puts it first in NEEDS JOSEPH 3. | **Not a finding** — this is how an answered-but-unavoidable question should be handled, and it is the model the other three should follow |

Everything else is genuinely held. P6 OQ5, OQ6, OQ8, OQ9, OQ11 and P7 OQ1, OQ3, OQ5, OQ6, OQ7, OQ8,
OQ9, OQ10, OQ11 each have a named guard, an injected strategy with no default, or an explicit refusal.
P7's Task 15 shipping `delete_derived` as a function that raises `UnratifiedResolution` naming **I6**
is the strongest example of the pattern in either plan.

---

## NEEDS JOSEPH

Verbatim and unresolved. Items 1–7 are already in the plans' own lists and are not repeated here;
these are the ones this round adds or re-scopes.

**1. §3.8's four role fields — do they exist?** §3.8: *"The agent should model these as distinct
facets, such as `authored_by` and `target_school`, or `our_firm` and `client`."* §3.11's table
contains none of the four. P6 Done-means 2 closes the catalogue to §3.11's rows "and no field outside
them"; P6 Done-means 13 and 22 both require `authored_by`. **This belongs with F2/F3/F4 as the fourth
member of the same family and it is the only one where the design states the field outright rather
than stating two names for one thing.** (F-1)

**2. P6 OQ10's record.** *"§3.13 orders the six states but does not define the comparison for two
equal-rank contradicting facts — two `validated` facts asserting conflicting course codes on one
file. Reject both, surface both as competing candidates, or defer to the internal score §3.13 permits
but declines to make authoritative?"* Independent of the answer, **what row does P6 write while the
question is open?** None of the thirteen `unresolved` reasons can name it, and B7 forbids writing
nothing. (F-3)

**3. P7 OQ2 — `filename`.** *"§8.4 puts paths in the always-local set; §7.7 puts the filename in the
residual dossier; §7.3 forbids filenames in prompts only for Protected Records."* §8.4's releasable
list is five and does not name `filename`. The SPEC resolves it deliberately and the plan builds the
resolution; the plan also writes that the design wins. **It is the only P7 open question absent from
the plan's own NEEDS JOSEPH list.** (F-5)

**4. Which `completeness` values imply `unreadable_unclassified`?** §8.4 names five handling classes
and never mentions extraction completeness. The SPEC states one mapping (`unreadable`); P7's Task 3
requires a stated mapping for all nine, in a part whose first constraint is that it owns no detection
rule. The eight unstated ones decide whether a real file is releasable. (F-9)

**5. Was W1 ratified?** `07-fidelity-audit.md`'s W1 is headed *"Nearest faithful fix (not applied)"*.
P7's SPEC adopted it verbatim and P7's Done-means 12 now tests it as contract, including the half the
design does not state: *"Where the design is silent on a redaction default, the more redacting option
is the default."* §8.4's `must` is real; **the derivation from it to a per-facet default table is the
audit's, not the design's**, and it constrains what ships.

**6. P6 `field_key` spelling.** §3.11's table writes `work type`, `target university`, `media type`;
the SPEC's own `fields` example writes `work_type`, `target_university`. The plan uses the spaced form
throughout and snake_case for `download_session` and `authored_by`. One rule closes it. (F-14)

---

## What this round did not look at

Buildability (round 2), defect-class reproduction (round 3), whether P6 and P7 attach to built P1–P5
(round 4), and scope (round 5). Where a finding here has a downstream consequence — F-1's effect on
Tasks 9 and 24, F-7's effect on Task 22's orchestrator dependency, F-12's effect on Task 13 — it is
noted so the later rounds can pick it up, not resolved.
