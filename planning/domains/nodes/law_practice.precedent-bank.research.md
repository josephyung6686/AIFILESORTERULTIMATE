# Research memo — `law_practice.precedent-bank`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.precedent-bank.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, placeholder launch

## Result

**Accept**, and accept it on the leg most rows fail: the privacy default. This row's material contains no
client, no matter and no third party, so its posture is `none` where the whole rest of the `law_practice`
family is `potentially_sensitive` — a difference that CONNECTION §2 names explicitly as sufficient for a
template to exist, and one the schema anchor itself already conceded in prose before this row was written.

The detection difference is equally sharp but needed more work to state honestly, because on its face it is
an *absence*, and a row that exists only because something is missing is the exact failure mode the brief
tells me to refuse. The argument below is that this row's signal is a **positive drafting apparatus**
(placeholder tokens across all party positions, a present-but-blank execution block, drafting notes
addressed to the drafter, optional-clause alternatives, a firm template-and-version marker) of which the
absence of a party is a *necessary condition* and never the trigger. Everything in the JSON is written so
that the necessary condition cannot fire alone.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment from `make_prompt.py`.
- `planning/domains/nodes/law_practice.json` — the schema anchor, read for its default template,
  recognition preconditions, work-type enum, grouping reasons and residual routing.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, read for
  calibration of structure and depth.
- Five landed siblings, read only at the point where each names this row in an edge:
  `law_practice.conflicts-check`, `law_practice.corporate-secretarial`, `law_practice.engagement-terms`,
  `law_practice.opinions-advice`, `law_practice.pleadings`. Also `law_practice.family-law`, which routes
  the blank court form here.
- `planning/00-database-agent-product-design.md`, reached by targeted grep. Every quotation in the node
  and in this memo was grep-verified against it verbatim before use; one candidate quote about the
  text-document extractor path did **not** verify in the form I first wrote it and was replaced with the
  verified wording (`"full text, headings, metadata, links, and structural information"`).
- `planning/domains/roster.json` — every edge id below was checked to exist. `career.job-search` does not
  exist and was not used; the roster carries `career` plus `career.recruiting`,
  `career.portfolio-work-samples` and others.
- `planning/domains/canonical_fields.json` — confirmed `file_type`, `creation_date`, `language`,
  `duplicate_family`, `version_family`, `sensitivity_status` as the universal keys used in `facts_legal`.

## THE CHARGE — the strongest case that this row should not exist

Stated at full strength first, then answered. Four of the brief's refusal grounds actually bite here; two
do not.

**(1) It is a work_type value on its own schema.** This is the hardest version and it is not hypothetical:
`law_practice.json`'s `work_types` array literally contains `"precedent, standard form and drafting-note
bank"`. A row whose name is an enumerated value of its own parent's field is the 574's original mistake in
its purest form.

**Answer.** The work_type says what the document *is*; this row is defined by a different *detector* and an
*inverted privacy default*, and it cuts across the enum rather than duplicating one entry. The evidence is
the five landed siblings, each of which independently found this row on a **different** work_type: a blank
claim form is a *pleading* (`law_practice.pleadings`), a model opinion letter is an *opinion*
(`law_practice.opinions-advice`), blank terms of business are *engagement terms*
(`law_practice.engagement-terms`), blank Articles are *corporate-secretarial*, a blank conflicts
questionnaire is a *conflicts screen*. Five work_types, one detector, one privacy posture. If this row were
a work_type value, those five rows would not have needed to write a boundary against it — they would each
have held their own blank case. They did not, and they each gave the same discriminator: filled versus
empty-by-design slots. That is a row, not a value.

**(2) It is a row defined only by the ABSENCE of something.** No matter reference, no client, no party pair,
no caption, no signature. The schema's own precondition demands both a repeated matter reference and a
practitioner/client role separation; this row has neither — so it does not merely differ from the default,
it fails the schema's activation gate.

**Answer, and it is the one that had to be got right.** The signal is not the absence. It is four marks that
are *present in the bytes* and are present on nothing else: (a) placeholder tokens across **all** party
positions rather than one schedule; (b) an execution block that is structurally complete but unnamed;
(c) a drafting/guidance layer — text that instructs the next drafter rather than binding a party, including
optional-clause alternatives labelled by whose interest they serve; (d) a firm template reference with a
version and usually an owner or last-reviewed slot. The test that the absence is not doing the work is the
**collision fixture**: `Form N1 Claim form.pdf`, an official blank court form downloaded and unmodified,
satisfies the absence completely and none of (a)–(d), and it is *not* this row's — it is 00's Independent
Records, "standalone certificates, notices, confirmations, forms, and PDFs that have a durable purpose but
no broader group." If absence were the signal, that file would activate. It does not.

On the schema-gate objection: the anchor does not treat this as a failure of its gate, it treats it as its
own fifth deterministic signal, naming it "the family's INVERSE-RECOGNITION signal, the mirror of
`clinical_practice.protocol-guideline`". The gate's two legs are the *default*; this signal is the anchor's
declared exception, and a template whose job is precisely the schema's declared exception is the textbook
case for a template row rather than an argument against one.

**(3) It is a lifecycle stage — the pre-execution draft of a document that will later be signed.** Every
instrument passes through an unexecuted state; a "stage" is not a node.

**Answer.** A precedent is not an earlier state of the same document — it is a document whose lifecycle
terminates in *copying*, never in signature. `law_practice.corporate-secretarial` drew the line from the
other side and I adopt it verbatim as the discriminator: a live draft has **one specific entity** in the
recitals with only the *execution* slots open; a precedent has entity slots blank **across all entities**,
and that blankness is its purpose. The second collision fixture, `SPA - Project Harrier - execution version
(clean).docx`, is the lifecycle case made concrete: real parties in the recitals, `[•]` still in three
schedules, unsigned. It is not this row's, and the JSON says why.

**(4) It is a duplicate of its schema's default template.** Answered in the node test below; it is the
schema's inverse on detection and its inverse on privacy.

**Two grounds that do not bite.** It is not an organisation name — the firm name in the footer or in DOCX
properties is precisely this row's canonical never-alone token, and it is the token *most* likely to appear
here because firms brand their own templates. And it is not a file format: the fixtures span `.docx`,
`.pdf`, `.xlsx`, `.zip` and an OCR screenshot, and `.dotx` is explicitly listed as never-alone because in
practice most genuine `.dotx` files are blank letterhead with no legal content at all.

## The node test, all three legs

**Leg 1 — detection signals differ from the schema's default.** The `law_practice` default requires **both**
"an exact matter, file or engagement reference repeated across two or more artefacts" and "at least one
artefact whose own labelled slots separate a PRACTITIONER OR FIRM role from a CLIENT role". This row
requires neither and instead requires the four positive marks above. The two detectors are not
subset-and-superset — they are **mutually exclusive on the same bytes**: a file that satisfies the default
cannot satisfy this row, because a matter reference disqualifies it. That is the strongest form leg 1 can
take.

**Leg 2 — privacy rules differ, and this is the decisive leg.** The schema's default is
`potentially_sensitive`, argued on four grounds of which the load-bearing one is that the exposed party is a
**third party** — a client, an adverse party, a witness, a child — "who never chose this filesystem and
cannot consent". That ground is absent here by construction. The anchor concedes it twice: its
precedent-bank recognition entry says the file "has no client, no matter and no third party in it at all,
which is also why it is the one part of this family that is not protected material", and its grouping
reason calls the precedent lineage "the one grouping in this family that is not protected material". So
this row is the *only* member of the family whose sensitivity is `none` and the only one whose first
residual is Reading Inbox rather than Protected Records. A template that inverts its schema's protection
default is not a padded row.

I did not leave that inversion unguarded. The posture is **conditional**: `none` applies only where the
no-party evidence was actually observed. Where the evidence is silent — encrypted pack, opaque binary,
one-page OCR, mixed archive — the row does not activate at all and the file routes to Review Later or
Protected Records rather than inheriting `none`. The Protected Records entry in `falls_through_to` states
that carve-out explicitly, and NJ-1 below records the residue I cannot close.

**Leg 3 — recommended dimensions differ.** `dimension_order` is `[]`, as it must be under PR-6, so the
difference is in the prose recommendation, and it differs in *substance* rather than in ordering. The
anchor recommends CLIENT → MATTER → DOCUMENT FUNCTION → period, with the client level seeded ineligible on
disclosure grounds. Here the first two levels are not disclosure-restricted, they are **structurally
absent** — there is nothing on the bytes to branch on — so the recommendation begins at document or
instrument function, with version lineage sitting *below* it rather than as a level, because versions of one
precedent are a version family, not a folder generation. A second, subtler difference: the anchor reaches
empty dimensions by three reasons and this row reaches it by only **two** of them, because the disclosure
reason ("A visible client or matter label can itself disclose the existence and subject of a
representation", from `legal.practice-matter-file`) is silent where there is no client and no matter to
disclose. Saying which of the parent's reasons *fails* here is part of how the row differs.

Not time-first: "For document and record domains, project, function, or subject usually comes before time
because putting year first scatters related work across calendar folders." A precedent's dates — drafted,
last reviewed, superseded — mean different things and none is a capture date. And the practice or
department must not become the top level by default: that would "use an author or organization merely as a
collector" and in a single-practice corpus would "create meaningless one-child levels".

## Files considered and rejected

Named because each is a tempting false positive, not because each is evidence.

- **`Form N1 Claim form.pdf` — an official blank court form, downloaded, unmodified.** The primary
  collision fixture; kept in the JSON as a `must_not_conclude` case. Absence complete, apparatus absent
  → Independent Records. This is the file that proves absence is not the signal.
- **`SPA - Project Harrier - execution version (clean).docx`.** Second collision: real parties, surviving
  `[•]` placeholders in schedules, unsigned execution block, matter reference in the footer. Placeholders
  are present but not across all party positions. Not this row's.
- **A published practice note, textbook precedent, regulator's specimen form or seminar paper.** Rejected
  as evidence and recorded as a `needs_llm` limit rather than a signal, because the anchor is right that
  the profession publishes its own templates and the surfaces are indistinguishable. A publisher and an
  official form code point away from this row; neither is reliably present.
- **A `.dotx` letterhead stationery file.** Rejected: a template file type with no legal content. It is why
  the template extension is on `never_alone`.
- **A blank invoice or fee-quote template with `[CLIENT]` and `[AMOUNT]` slots.** Rejected as *this
  family's* evidence entirely — see the `finance` non-edge below.
- **A scan of an executed original whose signature page was not captured.** Rejected, and it is the reason
  the never-alone list names "the absence of a signature, a party name or a matter number" in terms. This
  file and a genuine precedent are indistinguishable on the absence alone.
- **A folder named `Precedents/`.** Rejected outright. Folder context is not evidence this phase may rely
  on, and it is the shortcut that would have made this row trivially and wrongly easy.

## Reciprocal boundaries

Eight edges, all objects carrying a same-fixture signal in both directions. Five were already argued from
the other side by landed rows and I adopted their fixtures unchanged rather than inventing parallel ones,
so that the pair reads identically from both files:

| Neighbour | Same fixture | This row owns it when | They own it when |
|---|---|---|---|
| `legal` | one SPA DOCX | party recitals bracketed throughout, execution block present but unnamed, drafting notes in body | a bound party pair plus a completed execution block; `legal` is a safety domain and runs first on ties |
| `law_practice.pleadings` | `Claim Form N1 - blank - firm precedent v3.docx` | placeholder party slots, empty statement of truth, coloured drafting notes, no case number | populated party pair and a live case identifier |
| `law_practice.opinions-advice` | one model opinion letter | addressee/date/party/conclusion slots unfilled, guidance-note block | addressee names an actual body, a date it speaks as of, reliance restriction binding named parties |
| `law_practice.engagement-terms` | `TERMS OF BUSINESS (firm standard) v11 - CLEAN.docx` | bracketed client/matter/fee slots, blank acceptance block, template version marker | those slots carry a named client, a scope line, a signature or acceptance |
| `law_practice.corporate-secretarial` | an `Articles of Association` DOCX | `[COMPANY NAME]` throughout, blank across all entities | one entity's name and registration number in the recitals, only execution slots open |
| `law_practice.conflicts-check` | a conflicts questionnaire | its labelled slots empty by design across the whole document | those slots carry values (and the artefact then names third parties and becomes protected) |
| `business_operations.contract-administration` | `Precedents index.xlsx` vs a contract register | rows are ABOUT DOCUMENTS HELD FOR REUSE: precedent name, version, last-reviewed, internal owner, no counterparty column | rows are about LIVE OBLIGATIONS: counterparty, term, renewal or notice date |
| `career` | a reusable placeholder-slot document (`CV master.docx`, a cover-letter skeleton) | the reusable document is a professional instrument held for a future client matter | the reusable document is about the holder's own candidacy — the blank slots are waiting for the holder's identity, not a third party's |

The `business_operations.contract-administration` row deserves its own note: the same discrimination —
*what the rows are about* — also separates this row's index from the schema anchor's own limitation-and-diary
signal, which is the identical portfolio-table-with-a-date-column shape over matters. Three rows compete
for one spreadsheet shape and none of them may win it on shape.

## Neighbours considered that did not get an edge

- **`finance`** (a must-consider neighbour). Considered on the blank-invoice and fee-quote-template case,
  and rejected as a non-edge in both directions. `finance` needs an issuer-and-billed-to pair and amounts;
  a blank invoice template has neither, so `finance` does not fire and there is nothing to collide with.
  Symmetrically, a blank invoice is not *this* row's either — it carries no legal-instrument or practice
  apparatus, and its home is `business_operations` or Independent Records. Writing a collision here would
  have recorded a competition that does not exist.
- **`legal.practice-matter-file`.** Considered and deliberately omitted, because the boundary is already
  fully carried by the `legal` edge and by `law_practice.pleadings`. A third edge over the same fixture
  would add an id without adding a discriminator.
- **`law_practice.discovery` / `law_practice.transactional-deal`.** No edge. The blank
  completion-checklist case is handled inside the `Completion checklist - share sale - MASTER.xlsx` fixture's
  `must_not_conclude`, which states the transactional-deal boundary without claiming a mutex; the deal row
  needs a deal or matter reference and filled owners and dates, which the master has by definition not got.
- **`academic`.** Considered because a law-school precedent exercise or a bar-course specimen bundle has
  the same blank-slot surface. Not an edge: the anchor already lists that class under its own `needs_llm`
  entry for study copies, and duplicating it here would move a schema-level problem into a template row.

## `also_holds_with` — deliberately empty, and the reason is substantive

Two reasons, and they point the same way. Procedurally, `also_holds_with` is schema ↔ schema only
(CONNECTION §5), and this row is a template — so where the landed siblings put `legal` in
`also_holds_with` from a template row (`law_practice.opinions-advice`, `law_practice.pleadings`,
`law_practice.engagement-terms` all do), I did not follow them; **recommendation for R1c**: those three
entries are template→schema and should be reviewed against §5 when the family is reconciled.

Substantively, this row is the one member of the family where `legal` co-activation is *wrong* rather than
merely misplaced. Every sibling co-activates `legal` because its artefacts sit beside executed instruments
in a live matter. Here `legal`'s signals do not fire **by design** — that is the row's whole identity — so
there is no second schema that legitimately holds these bytes. An empty `also_holds_with` on this row is a
finding, not an omission.

## `proposed_fields` — deliberately empty

Three keys were tempting and all three were rejected rather than proposed, which is the economical answer
and I believe the correct one.

- **`template_version` / `precedent_version`.** Rejected: 00 already makes versioning a *universal* file
  fact — "The product should have a small shared set of universal file facts, such as file type, creation
  date, language, duplicate family, version family, and sensitivity status" — and the precedent-lineage
  grouping is served by `version_family` without any new key. Minting a domain synonym for a universal fact
  is exactly the variant-minting the brief forbids.
- **`instrument_type`.** Rejected: it is a *value* of the schema's `work_type`-shaped enum, not a field.
  This is the same error the row itself is accused of at charge (1), and it would be a poor look to defeat
  the charge and then commit it.
- **`precedent_owner` / `last_reviewed`.** Rejected: these appear only on the index fixture, they are
  internal role holders rather than parties, and authorship is never a destination under 00. A field that
  can never become a folder level and appears on one fixture is not worth a canonical key.

The schema declares no fields under PR-6 and this row adds none. `facts_legal` on every fixture is
restricted to the universal keys.

## Grouping without copying facts

Two fixtures are marked `group_without_copying_facts: true` and both are cases where membership is
plausible and *facts* are not. The OCR clause screenshot may sit in a precedent neighbourhood without this
row activating — one placeholder plus one marginal note is not the two-leg signal, and the fragment could
equally have been cropped from a live draft. The mixed archive `precedents-pack-2026.zip` may be inspected
at the manifest without its character transferring to the executed member inside it; that member's own
evidence — a bound party pair and an execution block — puts it with `legal`, whose protection runs first.
The general rule is stated as a grouping reason: a precedent must never be pulled into a matter group by
shared instrument type, shared subject or shared vocabulary, because that would write a matter fact onto a
document that contains none. 00's instruction for that situation is the one the row follows: "It must
return unknown where support is insufficient."

## NEEDS-JOSEPH

**NJ-1 — Derived precedents and metadata leakage.** *This is the item that decides whether the row is safe
as written.* Firms build precedents by stripping real transactions, and the stripped copy routinely retains
the original client in tracked changes, comments, a footer file path or DOCX document properties. The row's
`none` default is right about the visible body and wrong about those bytes. Alternatives: **(a)** `none`
conditional on a revision-and-properties check forming part of the activation evidence — what the node
currently assumes; **(b)** `potentially_sensitive` for the whole row, which is safe but discards the row's
principal contribution and would reduce its difference from the schema default to detection alone;
**(c)** `none` for the body plus a separate observation recording that unexamined revision metadata exists.
The node cannot settle this because P4 owns whether revision metadata is extracted at all.

**NJ-2 — Firm-confidential know-how.** A precedent bank exposes no *person* but is commercial property, and
under `sensitivity: none` it becomes the one `law_practice` class a cloud model could be shown in full. If
the product's sensitivity axis is only about personal exposure, `none` is right; if it is about disclosure
generally, it is wrong. The phase vocabulary has only `none` | `potentially_sensitive` and no third value,
so the real question is whether this belongs to P7's handling classes instead. Recorded, not guessed.

**NJ-3 — The blank official form.** `law_practice.family-law` routes a blank downloaded court form to this
row **or** to Reading Inbox and does not decide between them. This node's position is that the
kept-for-reuse apparatus decides it — a pristine official form is Independent Records, a form carrying a
firm marker and drafting notes is this row's — but a blank form with no marks at all, sitting in a firm's
precedent folder, is genuinely undecidable from the bytes, and folder context is not evidence this phase
may use. Alternatives: accept the apparatus test and let unmarked forms fall to Independent Records
(current), or allow approved parent-folder context as corroborating evidence for this row only (which would
open a door the rest of the family keeps shut).

## Recommendations for R1c (cross-row, not applied here)

1. Review the template→schema `also_holds_with` entries on `law_practice.opinions-advice`,
   `law_practice.pleadings` and `law_practice.engagement-terms` against CONNECTION §5.
2. The reciprocal of this row's `business_operations.contract-administration` and `career` edges is not yet
   written on those rows; both are inference-provenance and should be mirrored.
3. `law_practice.family-law`'s blank-form routing (NJ-3) names this row as one of two destinations and
   should be reconciled with whatever Joseph decides.

## Self-verification

- `python3 -m json.tool` parses the node file. Key set matches the landed `law_practice` template siblings
  exactly (27 keys, including `proposed_context_terms`).
- Every 00 quotation used in the node and this memo was grep-verified verbatim; the one that failed
  verification was corrected rather than kept.
- Every edge id checked against `planning/domains/roster.json`; all eight exist. Every
  `falls_through_to.residual_template` is one of 00's nine residual homes.
- Every `file_examples.source_type` is in `SOURCE_TYPES`. No file example writes a folder path as a fact.
- `fields: []`, `proposed_fields: []`, `dimension_order: []`. No thresholds, no handling classes, no
  `public_low`.
- Wrote only the two assigned files; no roster, canonical-field, sibling, `src/` or SPEC edits.
