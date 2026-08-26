# Research memo — `law_practice.closing-binder`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.closing-binder.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`
Neighbours named in the assignment: `legal`, `career`, `finance`. Residuals named: Protected Records, Review Later.

## Result

**Accept, narrowly.** The row survives as the **completion apparatus** — the agenda, the CP satisfaction
record, the detached counterpart signature pages and their release, the funds flow, the enumerated
closing index, the bible archive built from it, and the post-completion filing record. It **cedes the
executed instruments themselves** to `legal` on `legal`'s own evidence, the negotiation to
`law_practice.transactional-deal`, the title work to `law_practice.conveyancing`, and every
recipient-held pack to `legal.personal-legal-matters` / `finance.loans-mortgage`.

It survived a charge I expected it to lose.

## The charge, stated at its strongest before any research

Six disqualifiers apply to this id and four of them are live:

1. **It is a lifecycle stage.** "Signing, closing and completion" is the terminal phase of a
   transaction. Matters run intake → work → completion → closure, and the schema's own prose
   recommendation already orders by matter then *document function*; "closing" is a function value.
2. **It is a `work_type` value, and the schema said so itself.** `law_practice.json`'s `work_types`
   array contains, as **one** entry, *"transaction document set, due-diligence report, data-room index
   and completion or closing record"*. The anchor enumerated my row as a value inside another value.
3. **It is a document type.** "Closing binder", "closing bible", "completion statement" are
   document-type words, and the anchor's deletion test is explicit: strike every entity name and every
   document-type word and see what survives.
4. **It is a medium or a container.** A "binder" is a compilation format — a big bookmarked PDF or a
   numbered ZIP. That is a `SOURCE_TYPE` and an extension pattern, not a node.
5. **It duplicates a neighbour.** `law_practice.transactional-deal`, `law_practice.conveyancing`,
   `law_practice.settlement`, `law_practice.due-diligence` and `law_practice.corporate-secretarial`
   all touch it.
6. **It duplicates its own schema's default template.** matter → function → period, with the client
   level seeded ineligible. "Closing" is just function.

Charges 3 and 4 fail on inspection and I record why briefly: the roster row is not named after the
binder, it is named after **the act** ("Signing, closing and completion") plus the record of it, and the
row's evidence is a *column set* and a *manifest*, neither of which is a word or a container. Charges
1, 2, 5 and 6 needed real defeating. That is the rest of this memo.

## Sources actually read

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (full).
- Stamped assignment via `make_prompt.py law_practice.closing-binder`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` (full) — depth calibration.
- `planning/domains/nodes/law_practice.json` — my schema anchor, read selectively:
  `recognition`, `template.why`, `work_types`, `grouping_reasons`, `collides_with`, `also_holds_with`,
  `falls_through_to`, `role_split`, `sensitivity_why`, `open_question`, first fixture.
- `planning/00-database-agent-product-design.md` — **by `grep -n` only**, per the token rule. Every
  quotation in the JSON was taken from a grep hit and is verbatim: archive inspection and the
  `submission.zip` manifest sentence (line 31), the spreadsheet extractor path (line 35), the
  multi-fact sentence (line 37), *"The documents are content-incoherent but purpose-coherent."*
  (line 45), *"Date extraction should be deliberately narrow."* (line 46), the dimension-order rule
  and the recommendation-not-freeze sentence (line 95), *"create meaningless one-child levels"* and
  *"use an author or organization merely as a collector"* (line 97), and the residual library
  sentences for Protected Records, Review Later, Unsupported or Encrypted, Receipts and
  Confirmations, Independent Records and Reading Inbox (line 120).
- `planning/domains/roster.json` — id existence check for every edge, by grep.
- One grep for landed rows arguing a boundary against me:
  `grep -rl "closing-binder\|closing binder" planning/domains/nodes/` returned **nothing**. No
  neighbour has yet claimed or ceded this seam, so every boundary below is stated one-way from my
  side and R1c owes the reciprocal. I did not edit any neighbour.

I did **not** open `law_practice.research.md`; the anchor JSON decided my node test without it.

## Real named documents this row is built from

Not "PDFs". Six real document types, with what is inside them:

- **Completion agenda / closing checklist.** A numbered table whose rows are documents and whose
  columns are Document, **Responsibility**, **Signatory**, **Status**, Tab. Status is a small closed
  vocabulary: *in agreed form*, *to be executed at completion*, *executed*, *delivered*, *outstanding*.
  The Responsibility cells carry party or firm abbreviations for **every side** — buyer's counsel,
  seller's counsel, lender's counsel, the company.
- **Conditions-precedent satisfaction checklist.** One row per condition with a **clause reference
  pointing into an instrument the file is not**, an evidencing-document column, satisfied/waived, date.
- **Detached counterpart signature pages held to undertaking.** Pages consisting of execution blocks —
  name, title, capacity, witness name, address, occupation — with **no operative body text above them**,
  plus a covering line that they are held to another firm's order pending release.
- **Funds flow / completion statement.** Payer-to-payee rows with account slots, amount, value date,
  purpose narrative, totalling to one completion figure, plus a retention/escrow tab.
- **Closing binder index / bible index.** A contiguous tab list (1..n, no gaps) under a section
  grammar — Corporate Authorisations, Transaction Documents, Ancillary, Post-Completion — with PDF
  bookmarks matching the numbering, and one completion date on the cover.
- **Post-completion filing receipts.** Authority letterhead, submission reference, filed-form
  identifier, timestamp, barcode region.

Everything in the node's fifteen fixtures traces to one of those six, to a neighbour that competes
with one of them, or to an ugly case (OCR scan, screenshot, encrypted archive) that must not be
allowed to fake one.

## The node test, all three legs

**The schema's default template**, stated so my differences are checkable. `law_practice.json`
declares no fields and no dimensions; its default is a **matter-anchored two-role structure** requiring
**both** (i) an exact matter reference repeated across two or more artefacts and (ii) at least one
artefact whose labelled slots separate a practitioner-or-firm role from a client role. Its grouping
anchor is one matter from opening to closure. Its prose dimension recommendation is *client (only with
explicit approval) → matter → document function → period last*, not time-first. Its privacy rule is
above all a **naming** rule: no client, matter or third-party name as a folder level.

**Leg 1 — detection signals differ.** The schema's deterministic list is intake-and-conflicts,
matter-opening, time-and-disbursement, limitation diary, disclosure-review/privilege log, precedent
bank, internal work product, counsel instruction. **A completion agenda is none of them**, and it fails
the schema's own leg (ii): its role structure is **N sides with a responsibility column**, not a firm
and its client. Two further signals are structurally new: the **CP table whose rows point into a clause
of an absent instrument**, and **detached signature pages**, which are the exact inverse of `legal`'s
signal (`legal` needs party pair *plus* execution block; here the execution block is present and the
instrument is removed by design). This leg is the strongest of the three.

**Leg 2 — the grouping anchor differs in kind.** The schema groups by an exact matter reference
repeated across an **open-ended** workflow. This row groups by a **self-declaring closed manifest**: a
contiguous tab index, or an archive manifest mirroring one, that **names its own members in order**.
Membership is asserted by a document rather than inferred from a recurring string — 00's archive path
licenses exactly this reading, since a ZIP's contents are *"meaningful evidence of a purpose-defined
application packet even when the outer archive name is vague."* And the set is **closed at the event**:
an artefact materially post-dating the completion is a post-completion item for review, not a silent
late member. No open-ended matter group has that property.

**Leg 3 — privacy rules differ.** The schema's hardest rule is a naming rule. This row adds a
**content** rule and a **publicity** rule that the default does not state: (a) two member classes are
exposures in themselves regardless of naming — the signature pages (reusable signature images plus
witnesses' names, addresses and occupations) and the funds flow (live account details); they may not be
excerpted into a prompt, previewed, or **split into a separately labelled branch**, because a branch
called *Signature Pages* or *Bank Details* advertises the two most exploitable items in the corpus;
(b) a completion set deliberately mixes members destined for the public record (registry filings,
stamped transfers) with members that never are, and **the public destination of one member lowers
nothing** about the file, its neighbours, or the set. There is also a role reversal the schema assumes
away — see NJ-CB-3.

**And the dimension recommendation differs, in two named places.** Not "differs in emphasis":
(1) **function is replaced by the parties' own agreed running order**, because a closing index is a
negotiated sequence with a section grammar, not a function taxonomy, and it already supplies the
intelligibility 00 demands of a parent level (*"A work type such as Homework 3 is meaningful only after
the course is known"* — Tab 34 is meaningless without its completion); (2) **the period level is
dropped entirely**, because every artefact in a completion set shares one operative date by
construction, so a period branch is precisely 00's named fault — it would *"create meaningless
one-child levels"* — and it would silently pick the wrong date from among signature, value,
registration, scan and filesystem dates. `time_first` stays false: a completion is a record event, not
a capture event, and 00 gives the photos exception to capture, not to having a timestamp.

## Defeating charges 1, 2, 5 and 6

**Charge 1 (lifecycle stage).** Defeated by *multiplicity*, not by denial. Signing-and-completion is
not the terminal stage of *one* workflow; it recurs, producing the **same six artefact types with the
same column sets**, across `transactional-deal` (corporate), `conveyancing` (property),
`estates-administration`, `settlement`, and financing work under `regulatory-submission`. A stage that
appears identically in five sibling workflows is not a stage of any one of them — it is a cross-cutting
organisational situation, which is exactly what a template is. Had it been unique to
`transactional-deal`, I would have refused.

**Charge 2 (the anchor called it a work_type).** Conceded in part and this is the row's honest weak
point, recorded as **NJ-CB-1**. The anchor's `work_types` entry bundles *transaction document set,
due-diligence report, data-room index and completion or closing record* into one value — which, read
strictly, also folds `law_practice.due-diligence` and `law_practice.transactional-deal` into a single
value. The list is a values enum for a field the schema does not declare; it cannot by itself settle
which situations are templates. What settles it is legs 1–3 above. If R1c reads the anchor's enum as
binding, the correct outcome is refusal and I say so in the JSON's `open_question`.

**Charge 5 (duplicates a neighbour).** Six reciprocal boundaries are authored in `collides_with`, each
naming **the same fixture on both sides**. The three that matter: against
`law_practice.transactional-deal` the shared fixture is `Completion Agenda - Project Hartley - v14
(clean).docx` — *as a versioned working draft in negotiation it is that row's, as the executed running
order with Status populated and a completion date it is mine, and the same document is genuinely both
at different times*, which is why neither row may claim it from a filename. Against `legal` the shared
fixture is `Project Hartley - Closing Bible - Tabs 01-87.zip` — the manifest and the index are mine,
the members are `legal`'s, and the archive is **not unpacked to settle the argument**
(*"Archives should be inspected without being unpacked to disk."*). Against
`finance.loans-mortgage` and `law_practice.conveyancing` the shared fixture is
`Completion Statement - 14 Mercer Row - buyer copy.pdf`.

**Charge 6 (duplicates the default template).** Answered by legs 1–3 and the two named dimension
departures. If those departures are rejected, the row collapses into the default and should be folded.

## The collision fixture

`Completion Statement - 14 Mercer Row - buyer copy.pdf`. Its structure is **identical** to my funds-flow
signal: a payer-and-payee completion table, amounts, a value date, a conveyancer's letterhead, a client
account reference. It is not my evidence. It is **addressed to the holder by name as the buyer**, with a
*balance due from you* line. The discriminator is the **addressee-and-role structure, never the document
shape**: addressed to the holder as a party → `legal.personal-legal-matters` for the transaction plus
`finance.loans-mortgage` for the money; compiled by the holder for someone else's transaction → mine.
Getting this backwards files the user's own house purchase as a stranger's confidential matter, which is
the most damaging single error available to this row.

A second, subtler collision: `Data Room Index - Project Hartley - Phase 2.xlsx`. Sectioned, numbered,
document-per-row — it looks like a closing index. Discriminated by **direction and tense**: its columns
are Uploaded by / Access level / Q-and-A reference and it describes documents **disclosed for
inspection** weeks before completion; a closing index describes documents **delivered at an event** and
carries execution status and tabs. Shared deal reference does not move it.

## Files considered and rejected

- **The executed SPA, deed, share transfer, guarantee.** Tempting because they are literally the
  binder's contents. Rejected: they carry a bound party pair and an execution block, which is `legal`'s
  signal, and `legal` is a safety domain whose protection runs first. I take the index, not the members.
- **`Precedent - Completion Agenda (firm standard, v6).docx`.** The agenda column set is present — and
  **empty**: bracketed placeholders, blank status cells, a template version marker, no deal reference,
  no date, no person in the file at all. Rejected: no completion event. It is the schema's precedent
  bank and routes to Reading Inbox. Kept as a fixture because it is the cleanest proof that my signal is
  the *populated* matrix, not the column headings.
- **`Scan_20260630_1601.pdf`.** OCR of wet-ink execution pages. Rejected as a member: a shared scan date
  and a shared name are precisely the evidence my `never_alone` rules reject. Protected Records.
- **`Hartley - completion documents - password protected.zip`.** Rejected: a filename cannot manufacture
  an event, a side, a sensitivity result or a membership, and it must not be forced open.
- **Deal task lists and project plans.** A responsibility-and-status table over deliverables is also
  `business_operations.project-delivery`'s ordinary shape. Rejected unless the rows are documents *for
  execution* with signatory slots.
- **A contract register with status and date columns.** Same table shape, different tense; it is
  `business_operations.contract-administration`'s, whose anchor is a live obligation and its notice
  calendar. Boundary authored.
- **Files named `... (closing version).docx`, and `Closing the loop - Q3 marketing.pptx`.** The word
  trap. Named in `never_alone` because it is the false positive most likely to fire in a real corpus.
- **A practice-management or document-management system export.** A source system, not one file node.
  Only a bounded export with a readable manifest is represented.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`. Deliberate. PR-6 leaves
`law_practice` fieldless, a dimension may only branch on a field the same schema declares, and a
template may not mint a second copy of its schema's fields. The anchor already proposed `client`,
`our_firm` and `subject_of_record` for R1c; I reuse that proposal rather than minting a variant, and I
request both `client` and `our_firm` **destination-ineligible** for this row on the disclosure ground.
Facts written on fixtures are universal only — `file_type`, `creation_date`, `language`,
`version_family`, `capture_date`, `sensitivity_status`.

One key I wanted and did **not** mint: a **completion / operative event date**, distinct from creation,
signature, value, registration, scan and filesystem dates. It is the one fact that would make this row's
recommendation checkable. Minting a date-key variant is exactly what the brief forbids, so it is
NJ-CB-4 instead.

## Neighbours considered that got no edge

- `career.consulting-client-engagement` — the schema's role-split partner, but a consulting SOW has no
  completion agenda, no counterpart mechanics and no enumerated delivered set. Not a same-evidence mutex
  here; adding it would be inherited noise.
- `law_practice.due-diligence` — genuinely competes on the enumerated index, but the competition is an
  *interpretation* problem, not a same-evidence mutex: the column sets differ. Recorded as NJ-CB-2 with
  a proposed discriminator rather than as a collision, so R1c can settle it with that row's author.
- `law_practice.corporate-secretarial` — owns the company's own registers and filings continuously; my
  claim is only on the tab-stamped copies delivered at one event. Expressed through
  `also_holds_with: business_operations.board-governance` instead, which is where the same fixture
  actually co-activates.
- `law_practice.contract-negotiation` — subsumed by the `transactional-deal` boundary; adding both would
  restate one seam twice.
- `photos.*` — the e-signature screenshot co-activates on positive screen-origin evidence, which is a
  fixture note, not a mutex.
- `research.*`, `code`, `medical` — no evidence path.

## Grouping without copied facts

A candidate group is bounded by **one exact deal or transaction reference plus one operative completion
date**, or by an index or manifest that names its own members. Membership copies nothing: an indexed
member acquires no deal, party, date or status fact, and 00's fact model already contemplates a file
being *"included in an application package"* while remaining whatever else it is. Explicit non-anchors,
stated so this row does not quietly recreate the deal: a shared party name across two transactions, a
shared firm, a shared completion date, a shared registry, a download or scan session, a folder called
*Completion*, and semantic similarity between two agendas — which are near-identical documents by
drafting convention and would bridge unrelated deals if allowed.

## NEEDS-JOSEPH

1. **NJ-CB-1 — the fold question.** Is this a lifecycle stage of `transactional-deal` / `conveyancing`
   rather than a node? Answered *no* on multiplicity plus three differing legs. Alternatives: (a) keep as
   written; (b) fold into `transactional-deal` with `conveyancing` taking the property variant, routing
   executed members to `legal`, the funds flow to `finance` and strays to Protected Records; (c) keep,
   but merge `settlement`'s execution mechanics in here. **This row would rather be folded than padded.**
2. **NJ-CB-2 — the diligence-index seam.** Data-room index vs closing index. Proposed discriminator:
   direction and tense. Alternatives: confirm the discriminator with `law_practice.due-diligence`'s
   author, or assign both index types to one row.
3. **NJ-CB-3 — the holder-direction problem**, which no other row in this family has as acutely: the
   closing binder is the family's only artefact **delivered outward by design**, so a corpus can hold one
   with no practitioner-side evidence at all. (a) Activate on the completion-event anchor alone and
   accept recipient-held packs, overlapping `legal` and `legal.personal-legal-matters`; (b) require
   practitioner-side evidence and cede every recipient-held pack. **This row takes (b)** and routes the
   ambiguous case to Review Later, but the choice is Joseph's and it decides most real instances.
4. **NJ-CB-4 — the missing date key.** Whether an existing canonical date key can carry a
   completion/operative event date, or whether the concept is a `work_type` detail. Nothing minted here.

## Recommendations to R1c (I edited no neighbour)

- `law_practice.transactional-deal` owes the reciprocal: a document-status matrix with signatory and
  delivery columns, and a contiguous closing index, leave its scope.
- `law_practice.conveyancing` owes the reciprocal: the exchange-and-completion apparatus is shared;
  title, searches, enquiries and the report on title are not mine.
- `law_practice.settlement` owes the reciprocal: transaction-completion agendas and closing indexes are
  not its evidence.
- `finance.loans-mortgage` owes the reciprocal: a practitioner-compiled completion set for someone
  else's transaction is not its evidence.
- `legal`, `finance`, `business_operations.board-governance`, `government` and `identity` owe the
  reciprocal `also_holds_with` entries.

## Self-verification

`python3 -m json.tool` parses. Key set is byte-for-byte the same as `law_practice.json`'s (checked
programmatically: no missing keys, no extra keys). Fifteen file examples, each splitting observations
from facts, none writing a folder path as a fact; three mark `group_without_copying_facts` where
membership must not copy an anchor label. Every `source_type` is in `SOURCE_TYPES`. Every edge id was
grep-confirmed present in `roster.json`; every `falls_through_to` names one of 00's nine residual homes.
Every quotation was taken from a `grep -n` hit on `00` and pasted verbatim. No thresholds, no
statistics, no handling classes, no `public_low`. I wrote only my two assigned files.
