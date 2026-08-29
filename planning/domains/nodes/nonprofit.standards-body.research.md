# Research memo — `nonprofit.standards-body`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/nonprofit.standards-body.json`
Roster row: template on the fieldless `nonprofit` schema, `parent_id: null`, placeholder launch
Result: **REFUSED** (`refuse_node: true`)

## Result in one paragraph

The standards-development process is real, is unusually well-structured, and is not a node on this schema. Its distinctive evidence — a working draft, a ballot on a draft, a disposition-of-comments table, a designation-and-edition front matter — evidences no party at all, and the `nonprofit` schema's stated activation precondition is that every accepted signal must evidence a non-exchange relation between two labelled parties. The evidence that *does* clear that gate here — a committee roster, a members' ballot, a dues subscription, unpaid participation — is the schema's own default membership-register signal with the object of the vote changed. So the row is caught between two failures at once: what makes it distinctive cannot activate its schema, and what activates its schema is not distinctive. Refusing costs no coverage, because every fixture in the file set already has a landed home.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full) and the stamped R1b prompt from `make_prompt.py nonprofit.standards-body`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — the one landed launch row read for depth calibration.
- `planning/domains/nodes/nonprofit.json` — the schema anchor, read through targeted extraction of `recognition`, `template`, `work_types`, `grouping_reasons`, `collides_with`, `also_holds_with`, `falls_through_to`, `sensitivity_why`, `role_split`, `open_question`.
- `planning/domains/nodes/business_operations.organisational-records.json` — the named refusal exemplar, read for refusal shape and edge handling on a refused row.
- One grep across `planning/domains/nodes/` for `standards-body | standards development | SDO | ballot | comment resolution | working draft`, which surfaced the four neighbours that had already argued a boundary against this id: `engineering.standards-library`, `government.education-accreditation`, `government.public-consultation`, `government.regulatory-rulemaking`, plus `engineering.product-certification`.
- `planning/00-database-agent-product-design.md` — reached only by grep. Every one of the eight quotations in the JSON was verified verbatim against it by a script before this memo was written; all eight matched.
- `planning/domains/roster.json` — every id named in the JSON and this memo was confirmed present on the roster.

`planning/domains/CONNECTION.md` §2 (the node test), §5 (`also_holds_with` is schema ↔ schema only) and the `_CONTRACT` rules on fieldless schemas were applied as stated in the dispatch, not re-read in full.

## The charge — the strongest case that this row should not exist

Stated first, before any defence, as the brief requires. Six of the disqualifier categories land on this id, and three of them land hard.

**1. It is a lifecycle stage sequence.** The `one_line_hint` names the row's content as "committees, working drafts, ballots and comment resolution, publication and review". That is a pipeline of states through which one document type passes. `engineering.standards-library` has already ruled on exactly this and used it as a reason to *reject* a schema level: reading a gate word out of `Draft International Standard` would import the publisher's balloting stage as if it were the holder's design maturity, which it calls a fabricated fact. A stage is a value on a document, not a filing world.

**2. It is a document type.** "A standard" is a document type. `engineering.standards-library` already owns that document as its subject, and owns it well — its researched order is `issuing_body -> standard_designation` with edition as metadata.

**3. Its most tempting signal is an organisation name.** ISO, IEC, ASTM, IEEE, NFPA, W3C, BSI, ANSI. `engineering.standards-library` already bans the publisher's name as sole proof, extending 00's own role-ambiguity reasoning — "A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization." A row whose entire support is never-alone evidence can never clear activation, which is precisely why `business_operations.organisational-records` was refused.

**4. It is a duplicate of a neighbour.** `engineering.standards-library` lists *"standards-body draft circulated for comment"* among its own `work_types`. The single fixture most people would name first when asked what a standards body files is already claimed, by name, by a landed row.

**5. It is a duplicate of its own schema's default.** The `nonprofit` schema's default membership signal is a roll or register with one row per named member carrying a class and a join date, or a members' meeting instrument carrying a notice period, a motion, a proxy or ballot form and a member-vote count. A standards committee roster is the first of those verbatim. A standards ballot is the second of those with the object changed from the association's own rules to a technical document.

**6. It is defined by an absence.** The only thing separating a "standards body" from any other membership association in this schema is that its output happens to be a normative document rather than a service — i.e. the *absence* of a beneficiary. The nonprofit schema's own `open_question` already records the shape of that failure: it names `volunteer-programme` as WEAK "because its discriminator is an absence of payroll structure", and rules that where a proposed sibling's discriminator is an absence, "the three weak ones should be refused rather than invented."

## Defeating the charge — attempted, and it fails

The keep-case is not frivolous and deserves stating properly, because one part of it is true.

There is one structure in this world that no landed row names: the **disposition-of-comments table**. One row per comment, keyed by member body or commenter, clause, paragraph and line, comment type, proposed change, and the committee's disposition with a reason, under a header naming the document under ballot and the closing date. It is a real artefact, it is machine-recognisable, it is unlike anything in the roster, and `engineering.standards-library`'s researched signals — a foreword naming a balloting technical committee, a mandatory normative-references clause — describe the *published* artefact and do not currently reach it. Its sibling, the **ballot record** (an enumerated approve / disapprove-with-comments / abstain per member body against a named document at a named stage, with a closing date and a comment-resolution obligation), is in the same position.

So: a genuinely distinctive structure, genuinely unowned. Is that a node?

No, and the reason is the whole finding of this pass. **"Nobody owns X" is not the node test.** The test (CONNECTION §2) asks whether a template's detection signals, recommended dimensions, or privacy rules differ from *its schema's* default. Run the distinctive structure against the schema it was assigned to and it does not merely fail to differ — it fails to activate. The `nonprofit` schema states its precondition and calls it "the whole schema": every accepted signal must evidence a non-exchange relation between two labelled parties — money or labour given without a commensurate return, or service given to a named person who is not paying for it. A comment table names commenters and clauses. It contains no gift, no restricted purpose, no subscription, no unpaid labour, no beneficiary. Neither does a working draft, a ballot tally, or a published standard.

A row whose distinctive evidence cannot activate its own schema is a row that never fires. That is a harder failure than the ordinary leg-1 failure ("same signals as the default"), and it is fatal on its own.

## The node test, all three legs

### Leg 1 — detection signals

Stated above and not repeated. The schema's default signal set is: restricted-grant lifecycle, restricted-fund accounting, donation-and-gift declaration, membership register, and the beneficiary/safeguarding structures. Sorting this row's candidate evidence against that set gives two piles and no third: evidence that does not clear the precondition (draft, ballot, comment table, designation, normative references, publication notice), and evidence that clears it by being the membership-register default (roster, dues, members' ballot, unpaid participation). **Fails.**

### Leg 2 — recommended dimensions

Both the schema and this row have `dimension_order: []`, because the `nonprofit` schema declares no field rows under PR-6 and D1's deferral, and `_CONTRACT` rules 10 and 15 forbid branching on a field the schema does not declare. So the machine-readable comparison is vacuous and the real comparison must be against the schema's *prose* default, which the schema itself names as the paragraph every template in the family must differ from:

> association (seeded ineligible in a single-association corpus) → the **non-exchange counterparty or fund** — the grant, the restricted fund, the appeal, the membership class, the case → the period → the document function.

A standards-development corpus has no non-exchange counterparty and no fund. The schema's second and load-bearing level is unfillable here. What this corpus actually wants is `issuing_body -> standard_designation`, edition carried as metadata — which is `engineering.standards-library`'s researched recommendation, verbatim, arrived at independently.

That is worth stating as a general finding for R1c: **differing from your own schema's default by silently adopting a different schema's default order is evidence of being on the wrong schema, not evidence of being a node.** A "difference" that points away from the parent is not the difference leg 2 asks for. **Fails.**

### Leg 3 — privacy rules

The `nonprofit` schema's posture is stricter than `business_operations` on one argued ground: the exposed party is a third party who is neither the user, an employee, nor a customer, and who frequently disclosed under need, harm or vulnerability — a safeguarded child, a service user, a person seeking help. That is why the schema names Protected Records *first* among its residuals, against `business_operations`' ordering.

A standards-development record has none of that. There is no beneficiary, no safeguarded person, no service user anywhere in this world. Participants are named professionals acting in a declared public capacity; drafts exist in order to be circulated for comment; the output is published for sale or free download. The row's posture is **looser** than its schema's default, not different in kind.

Two fixtures do carry real exposure and are recorded rather than smoothed: a committee roster is a list of named people with affiliations and often contact columns, and an essential-patent disclosure is commercially sensitive to the declaring organisation. But neither is a *nonprofit-family* vulnerability — the roster is the schema's own membership default, and the patent disclosure is a legal and commercial instrument. The JSON therefore holds `potentially_sensitive` at the schema's level rather than arguing it down, because a refused row must not weaken its parent's posture. **Fails.**

Three legs, three failures. Refuse.

## Files considered and rejected

The tempting false positives, and why each is not this row's evidence:

- **`ISO_IEC_27001_2022(en).pdf`** — the published standard. `engineering.standards-library`'s subject. Present on the machine of any reader who bought one copy; nothing in it evidences participation, let alone a non-exchange party.
- **`SC27-N24118-WD-27001-rev3.docx`** — the circulated working draft. Named in `engineering.standards-library`'s `work_types` as "standards-body draft circulated for comment". Already owned.
- **`SC27-WG1-Meeting-Minutes-Bangkok-2026-04.docx`** — committee minutes. The `nonprofit` schema cedes the association's self-running record by name, and `business_operations.meeting-record` and `business_operations.board-governance` are landed and own it. Charitable or member-association status changes the tax treatment and the regulator, not the structure of a minute.
- **`ASTM-D20-Committee-Roster-2026.xlsx`** — the schema's own membership-register default. It fires the schema, which is exactly why it cannot support a child row.
- **`ASTM-Membership-Invoice-2026.pdf`** — a dues notice held by the paying member is that person's own money record and is `finance` by role, on the same reasoning the schema uses to exclude a donor-side receipt. Only the association's own subscription run is nonprofit, and then on the default.
- **`W3C-Patent-Disclosure-AB-Corp-2026-03-11.pdf`** — an essential-patent disclosure with a licensing commitment. `engineering.invention-disclosure` and the `legal` safety placeholder. The product must not decide whether a commitment is binding, current or enforceable.
- **`NFPA-70-2026-Public-Input-Report.pdf`** — public review of a draft standard. `government.public-consultation` names this exercise explicitly among those it must *separate itself from*, so it disclaims the fixture rather than claiming it; the document and its comment apparatus stay with `engineering.standards-library`. A disclaimer by a neighbour is not a grant of ownership to this row.
- **`ISO-9001-awareness-training-slides.pptx`** — the never_alone case made concrete: the densest possible concentration of standards-body names and designations, on internal training material owned by `business_operations`.
- **`Screenshot 2026-05-02 at 09.14.31 - ballot portal.png`** — OCR of a ballot portal establishes no vote, position or participation fact about the holder. `group_without_copying_facts: true`.
- **A committee's mailing-list archive or an SDO's document-register export** — a source system, not a file node. Not represented, as `legal.practice-matter-file` decided for practice-management databases.

## The collision fixture

`Accreditation-Standards-2026-Edition-and-Team-Report.pdf` — a numbered standards edition with criteria, findings keyed to individual criteria by a visiting peer-review team, and an institution-facing decision letter with a reaffirmation term.

This is the strongest surface match this row could have: a *numbered standards edition*, issued by a *private membership association*, containing *criterion-keyed findings from a volunteer committee*. Both halves of the row's name are present on the file.

It is not this row's. **What discriminates it is the review cycle, not the standards edition.** `government.education-accreditation` has already claimed it and stated the boundary against this id in that direction; this memo accepts the placement and states it back.

A secondary collision worth recording: `EN-62368-1_2014.pdf` sitting inside a certification folder. `engineering.product-certification` and `engineering.standards-library` have already settled it between themselves — the file that *is* the rule is standards-library's even when it lives in a certification folder, and citing it in a declaration's applied-standards list does not convert it into conformity evidence. This row adds nothing and takes nothing.

## Reciprocal boundaries, stated in both directions

A refused row authors no edges, so `collides_with` and `also_holds_with` are empty in the JSON, following `business_operations.organisational-records`. The boundaries are recorded here for R1c instead, each naming the same fixture on both sides.

- **`engineering.standards-library`.** Same fixture both sides: `SC27-N24118-WD-27001-rev3.docx`. Standards-library owns it in both directions — it already names "standards-body draft circulated for comment" among its own work types, and this row cannot take it because a draft evidences no non-exchange party. Nothing is owed back except NJ-SB-1 below.
- **`business_operations` (`meeting-record`, `board-governance`).** Same fixture both sides: `SC27-WG1-Meeting-Minutes-Bangkok-2026-04.docx`. business_operations owns it in both directions; the `nonprofit` schema has already ceded the self-running record by name in its own `collides_with`, and this row's refusal simply removes the last claim on it.
- **`government.education-accreditation`.** Same fixture both sides: `Accreditation-Standards-2026-Edition-and-Team-Report.pdf`. That row owns it, discriminated by the institutional review cycle. In the reverse direction it had reserved to this id everything *without* a review cycle — writing standards, certifying products or management systems, accrediting companies — and this refusal declines that reservation and sends it to `engineering.standards-library` and `engineering.product-certification`. See NJ-SB-2; the neighbour needs to know.
- **`government.public-consultation`.** Same fixture both sides: `NFPA-70-2026-Public-Input-Report.pdf`. Neither row claims it. That row disclaims it explicitly; this row is refused. It goes to `engineering.standards-library`, or to Reading Inbox.
- **`government.regulatory-rulemaking`.** Same fixture both sides: a delegated standards body's notice-and-comment record where the standard is incorporated by reference into law. Rulemaking is the better home when a delegated power is evidenced; this row would have been the private-association branch and no longer exists. See NJ-SB-3.
- **`engineering.product-certification`.** Same fixture both sides: a management-system certificate issued by a body that also writes standards. Certification owns the file that measures a named entity against a rule; nothing about the issuer's association status moves it here.

## Neighbours considered that got no boundary

- **`finance`** — only through the dues invoice, and the role rule (payer side is the payer's money record) is the schema's, already written, not this row's to restate as an edge.
- **`research.grants-funding`** — no contact. Standards development is not grant-funded in its characteristic artefacts, and the schema's own NJ-NP-2 grant fork does not reach here.
- **`business_operations.corporate-regulatory-filings`** — an SDO files regulator returns like any other association, and the schema has already ruled that relation is that row's and not nonprofit's.
- **`hr`, `clinical_practice`, `identity`** — no fixture in this world touches them.

## Fields

`fields: []` and `proposed_fields: []`. Nothing is proposed and nothing is minted. `issuing_body` and `standard_designation` are the two keys this corpus wants, and they are already `engineering.standards-library`'s proposals awaiting R1c; proposing them again from a refused row would create the duplicate-variant problem the brief warns against. The schema's `role_split` pairs (`sponsor`/`organization`, `organization`/`subject_of_record`) have no application here — there is no funder, no grantee, and no subject of record.

## NEEDS-JOSEPH

**NJ-SB-1 — the orphaned comment table.** The disposition-of-comments table and the ballot record are distinctive, unowned structures. This refusal routes them to `engineering.standards-library` on the grounds that they are apparatus of the document rather than of an association, but that row's researched signals describe the published artefact and do not currently name them. Alternatives: (a) add the comment-table and ballot-record structures to `engineering.standards-library`'s signals — this row's recommendation, and an edit this row did not make; (b) leave them unowned, so participant-side files land in Review Later, which is defensible and cheap; (c) build a standards-development row on the **engineering** schema rather than nonprofit, where the consensus-process fingerprint and the `issuing_body -> standard_designation` order already live. Option (c) is the only version of this id that could survive a node test, and it would not be a nonprofit row.

**NJ-SB-2 — a neighbour's escape hatch just closed.** `government.education-accreditation`'s own open question asks whether it belongs on the `government` schema at all, since most education accreditors are private membership associations, and it names *this id* as the alternative home. This row is refused, so that alternative no longer exists. R1c must resolve the neighbour's NJ-1 knowing its named escape hatch is gone: keep it on `government`, or split assessor-side education review by the reviewer's own public-body status. This row did not edit the neighbour.

**NJ-SB-3 — the delegated-power branch.** `government.regulatory-rulemaking` flags as unresolved whether a delegated standards body or self-regulatory organisation is exercising a delegated rulemaking power or acting as a private association. This refusal removes the private-association branch from the nonprofit side without answering it. Where a standard is incorporated by reference into law, the notice-and-comment record is rulemaking-shaped — but the discriminator, incorporation by reference, is a legal fact the product must not decide. R1c should state whether that branch is simply abstention.

**NJ-SB-4 — a general finding, offered beyond this row.** Two leg-2 patterns showed up here that R1c may want as a standing rule, because other J-IND placeholder rows on fieldless schemas will hit them: first, a row whose distinctive evidence cannot satisfy its *schema's* activation precondition fails leg 1 more decisively than one that merely shares the default's signals, and should be refused without further argument; second, a row whose natural dimension order is another schema's researched default is on the wrong schema, and "differs from my parent's default" should not count as passing leg 2 when the difference points at a sibling schema.

## Self-verification

- `python3 -m json.tool` parses the JSON.
- All **8** quotations embedded in the JSON were extracted by script and matched verbatim against `planning/00-database-agent-product-design.md`; 8/8 OK, 0 FAIL.
- Every id named in the JSON and this memo (`engineering`, `engineering.standards-library`, `engineering.product-certification`, `engineering.invention-disclosure`, `business_operations`, `business_operations.meeting-record`, `business_operations.board-governance`, `business_operations.corporate-regulatory-filings`, `government`, `government.regulatory-rulemaking`, `government.education-accreditation`, `government.public-consultation`, `finance`, `legal`, `nonprofit`) is present on `planning/domains/roster.json`.
- Every `file_examples.source_type` is in `SOURCE_TYPES`: `text_document`, `spreadsheet`, `presentation`, `image`.
- Every `falls_through_to.residual_template` is one of 00's nine residual homes.
- `fields: []`, `proposed_fields: []`, `collides_with: []`, `also_holds_with: []`, `role_split: []` — no bare-string edges written, and no schema placed in `also_holds_with` from a template row (CONNECTION §5).
- No threshold numbers, no confidence scores, no handling classes, no `public_low`.
- No folder path is written as a fact in any file example.
- Only the two assigned files were written. No neighbour node, roster, `canonical_fields.json`, `check.py`, `src/`, SPEC or shared file was touched.
