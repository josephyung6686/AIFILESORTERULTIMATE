# Research memo — `government.legislative-record`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.legislative-record.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, placeholder launch

## Result

Accept the node. It survives the charge on two of the three template legs — detection signals and
privacy rules — and it fails the third (dimension order) only because PR-6 leaves the schema
fieldless, which is a condition every government template shares and none can escape.

The one-sentence discriminator: **a legislature is the only public body whose central artefact is one
instrument re-published at named stages and amended by coordinate.** Everything else in government
files a *case* — an application, a licence, a rulemaking docket, a records request, a procurement —
where the members of the group are different documents sharing a reference. Here the members are
successive prints of the same text, and the amendment sheet does not point at the bill, it points at
*clause 4, page 3, line 17* of one named print. That is a recognition unit the schema default does
not have.

## The charge — the strongest case that this row should not exist

I put six charges against the row before writing anything. Four fail, one is conceded, one is the
real fight.

**Charge 1 — it is a document-type family.** "Bill, amendment, minutes, transcript, vote" is a list
of document types, and document types are values, not nodes. *Defeated.* The row's deterministic
signals are not the words. `Bill 42.pdf` with no stage endorsement does not fire; the enacted
`Housing Standards Act 2026 c.14 - consolidated text.pdf` does not fire even though it is the same
subject matter and the same legislature; a private board's minutes with a recorded vote do not fire.
What fires is structure — a stage endorsement line, a coordinate-addressed amendment instruction, a
roll call with per-member values, continuous column numbering across a topic-changing sitting. The
`work_types[]` array in the JSON is where the document-type words are correctly parked, as the design
requires: they are values of a field this schema does not yet declare.

**Charge 2 — it is an organisation name (never-alone evidence).** "Parliament", "Congress", "the
Council", "the Committee". *Defeated, and encoded.* The `never_alone` list refuses the legislature
name, the seal, the letterhead, the email domain, and the folder named `Bills/`. It also refuses the
whole vocabulary — bill, clause, amendment, reading, motion, division, quorum, hearing, session,
chair — because every one of those words is also in a company board pack, a union rule book, a
students' union constitution, and a standards committee. If this row's only evidence were the name of
a legislature it could never activate and I would have refused it.

**Charge 3 — it is a lifecycle stage.** First reading → committee → report → third reading → assent
is a lifecycle, and lifecycle stages are not nodes. *Defeated, and it produced the row's best
finding.* I refuse to make stage a dimension or a field. A bill's stages are an **authoritative
ordering on the universal version-family relation the engine already computes**, not a new fact.
Making stage a folder level would scatter one bill into `as-introduced/` and `as-amended/` branches —
the exact failure the row exists to prevent. That reasoning is written into `template.why`.

**Charge 4 — it is a medium, a length, or a file format.** *Defeated trivially.* The fixture list
spans `text_document`, `spreadsheet`, `email`, `calendar`, `image`, `ocr`, `archive`, and
`opaque_binary`; a division is a spreadsheet in one legislature and a PDF in the next.

**Charge 5 (conceded) — its dimension order is identical to the schema default: both empty.** True,
and I state it rather than dress it up. CONNECTION.md lists a template's properties as "detection
signals, recommended `dimension_order`, optional branch patterns, privacy rules, validation
constraints" — a disjunction, not a conjunction. Under PR-6 no government template can differ on
dimensions, so requiring that leg would delete all thirty-one government templates. The row must
therefore win on the other two, and it does.

**Charge 6 (the real fight) — it is a duplicate of its own schema's default template.** The
`government` anchor's deterministic list *already* contains: "a legislature-produced bill packet with
an official bill identifier repeated across a bill text, amendment sheet, committee paper, vote
record, or proceedings transcript, plus an issuing-legislature block or official publication
structure; a downloaded enacted law alone is excluded". If the schema already fires on my evidence,
what is left?

Three things, and they are why the row stands:

1. **Granularity of the signal.** The anchor's signal is packet-level: *these documents co-occur with
   a shared identifier*. That is a grouping observation. My signals are within-document structure —
   a stage endorsement line, `Clause 4, page 3, line 17, leave out … insert`, a per-member aye/no
   column with tellers, column numbers that run continuously through a topic change. Those fire on a
   **single** file with no packet at all, which the anchor's signal cannot. `Marshalled list of
   amendments - Bill 42 - Report Stage.pdf` arriving alone is invisible to the schema signal and
   decisive under mine.
2. **An inverted privacy rule.** The anchor's default is that "submissions and named-person case
   material are protected by default". Half this corpus is named-person material that is **published
   by design**: a division names every member's vote, a verbatim report names every speaker. The
   product must not re-privatise them as personal records. The other half is *stricter* than the
   default — an uncorrected transcript, an embargoed report draft, an anonymity request on a
   submission, pre-introduction drafting instructions. A schema default cannot hold a rule that is
   simultaneously looser and tighter than itself; a template can. This is the strongest leg.
3. **A grouping anchor the schema has no vocabulary for.** The anchor's grouping reasons key on "an
   exact bill, rulemaking, consultation, application, permit, case, request, procurement, election, or
   programme reference". Coordinate membership — an amendment belonging to *one print* rather than to
   the bill — is finer than any reference in that list, and it is the only anchor that survives when
   two prints of the same bill are both present.

Charge 6 defeated. No refusal.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped assignment from `make_prompt.py`.
- `planning/00-database-agent-product-design.md` — grepped, not streamed. Every quoted span in the
  JSON was `grep -c`-verified verbatim before use (residual library definitions; extension as
  "routing signal rather than an assumption about meaning"; "A session should never be treated as
  proof of topic"; "the system must not mistake the absence of EXIF for proof that an image is a
  screenshot"; "A model that cannot cite sufficient evidence must return unknown."; "The documents are
  content-incoherent but purpose-coherent."; the two privacy clauses).
- `planning/domains/CONNECTION.md` §2 — the node test and the template-properties clause.
- `planning/domains/nodes/government.json` — the schema anchor and its default template, read for
  recognition, work types, grouping reasons, residuals, and sensitivity.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — depth calibration.
- `planning/domains/roster.json` — every edge id below was confirmed present.
- `planning/domains/nodes/business_operations.meeting-record.research.md` — the one landed row that
  already argued a boundary against this id.

## The neighbour who already ruled on me

`business_operations.meeting-record` names this row in its deliberate non-edges:

> **`government.legislative-record`** — formally recorded proceedings, with genuinely different
> apparatus (a chamber, a motion, a division). `board-governance` already carries the
> formal-proceedings edge for this family and adding a second would duplicate it.

I accept that ruling and mirror it exactly: my `collides_with` names
`business_operations.board-governance`, **not** `meeting-record`. The reciprocal boundary is
therefore already closed on both sides without R1c having to reconcile anything, and the neighbour's
phrase "genuinely different apparatus" is the same discriminator I arrived at independently.

## Files considered and rejected

The tempting false positives, and why each is not this row's evidence:

- **`Housing Standards Act 2026 c.14 - consolidated text.pdf`** — the enacted law. This is the
  collision fixture (below). Rejected: an enacted text is the *end* of a proceeding, not a record of
  one. No stage endorsement, no coordinates, no division, no columns.
- **`Bill 42 - amendment tracker - our positions.xlsx`** — real amendment numbers, real bill
  identifier, and a "our position / lines to take / target members" column. Rejected: a positions
  column is authorship of advocacy, and there is no clerk-side issuer. It is
  `nonprofit.advocacy-campaign` and it stays there.
- **`Constituent letter re Bill 42 - Ms A Rahman.pdf`** — held in a member's office, carrying a
  correct bill identifier. Rejected: `government.constituent-casework`. The bill identifier in a
  subject line must never pull a named private person into a published bill group. This is the
  fixture I would most expect a naive classifier to get wrong.
- **`Members' register of interests - 2026 edition.pdf`** — a legislature publication about named
  members. Rejected: it is a statutory publication of a records-holder function, not a record of the
  chamber's business. `government.public-authority-record`.
- **`Model United Nations - resolution drafts.docx`** — full apparatus (draft resolutions, amendments,
  a roll call) and no state. Rejected at the *schema* level: no public authority, so `government`
  never activates. It falls to academic or personal material, and I did not author an edge because
  the failure is above this row.
- **`Committee on Standards - draft report on Member X - CONFIDENTIAL.pdf`** — genuinely mine by
  apparatus, but it is a named-person disciplinary record. Kept in scope, routed to Protected
  Records, and flagged: it is the sharpest case of the publicity inversion in NEEDS-JOSEPH 1.
- **A legislature's HR, payroll, estates, and IT files.** Rejected: the legislature as *employer* is
  `hr` / `business_operations`. The building is not the business.
- **A live legislative information system, bill-tracking database, or clerk's case system.** Rejected
  as a source system rather than a file node. Only a bounded export with a readable manifest is
  represented, and it is never unpacked to improve recognition.
- **`Committee hearing - full session.mp4`** — kept as plausible in `file_kinds`, but not written as a
  fixture, because recognition would rest on a transcript the product may only produce "under an
  explicit privacy and compute policy". Naming it as a fixture would imply that policy exists.
- **Statute-citation catalogues.** I checked whether `planning/deferred-catalogues/` was needed and
  concluded it is not: bill identifiers are formatted per legislature and recognising them from a
  gazetteer would be R4's job and would still be never-alone. This row never depends on a catalogue.

## The collision fixture

`Housing Standards Act 2026 c.14 - consolidated text.pdf`.

It has the legislature's name, the subject matter of an active bill in the corpus, statutory clause
numbering, a promulgation line, and the official seal. Every surface cue matches. It is not this
row's evidence.

What discriminates it: **the four apparatus markers are all absent.** No stage endorsement naming
the print, no amendment addressable by page and line, no division, no proceedings columns. A
consolidated text is a *destination* — the law as it now stands — and consolidation deliberately
erases the proceeding. Note the trap in the second order of evidence: it will often be downloaded in
the same browser session as the genuine bill prints, and the design forecloses that shortcut
explicitly — "A session should never be treated as proof of topic". It goes to Reading Inbox and
carries `also_schema: "legal"`.

## Reciprocal boundaries

Eight collisions are authored. Each names the same fixture on both sides.

| Neighbour | This row holds it when | The neighbour holds it when | Shared fixture |
|---|---|---|---|
| `government.public-authority-record` | the chamber apparatus is present in the bytes | authority-side custody with a case reference and no apparatus | `Committee papers export - Session 2025-26.zip` |
| `government.policy-development` | the response is held inside the proceedings, keyed to numbered recommendations | the department holds its own briefing, options paper, or response | `Government response to the Committee's Third Report - CP 1194.pdf` |
| `government.regulatory-rulemaking` | the scrutiny report, objection motion, and division on a laid instrument | the made instrument and its explanatory memorandum | a statutory instrument laid before the chamber |
| `government.public-consultation` | a numbered submission in an inquiry series held by a reporting body | a comment keyed to a consultation run by the deciding body | `Written evidence HSB0037 - anonymised at submitter request.pdf` |
| `government.municipal-administration` | ordinance readings and the roll call inside the packet | officer reports and service delivery in the same packet | `Council meeting packet 2026-03-11.pdf` |
| `government.constituent-casework` | the office's copy of proceedings material | named-person correspondence, even when it cites a bill | `Constituent letter re Bill 42 - Ms A Rahman.pdf` |
| `business_operations.board-governance` | the state-side apparatus with legislature custody | the same furniture in any privately governed body | a board pack with a resolution and a recorded vote |
| `nonprofit.advocacy-campaign` | the legislature's copy | the author's copy, or any document stating a position to take | `Bill 42 - amendment tracker - our positions.xlsx` |

The municipal boundary is the one I want R1c to look at hardest, because it is the only boundary
where the *same organisation* sits on both sides. My ruling is that membership must be evidenced
**per document**, not per packet: one council meeting packet legitimately splits between two rows.
That is a real cost — it means a packet is not automatically a group — and I record it rather than
paper over it.

## Deliberate non-edges

- `business_operations.meeting-record` — excluded on the neighbour's own reasoning, quoted above.
- `legal.*` and `law_practice.legal-research` — a legislative-history bundle assembled by a lawyer is
  legal research firing on its own evidence, a vocabulary overlap rather than contested bytes. The
  enacted-law fixture carries `also_schema: "legal"` instead of an edge.
- `research.reading-library` — the Reading Inbox residual already absorbs the reader's copy; a
  same-evidence mutex would double-count it.
- `nonprofit.political-campaign` and `nonprofit.trade-union` — campaign literature and conference
  motions never reach the chamber apparatus. The advocacy edge already carries the genuinely
  confusable bytes.
- `government.public-records-foi` — a disclosure bundle *about* proceedings is the records-holder's
  workflow. The anchor's `needs_llm` already owns that ambiguity at schema level.
- `photos.screenshot-captures` — a coactivation case on the screenshot fixture, not a mutex.

`also_holds_with` is empty and `role_split` is empty for the same reason as
`legal.practice-matter-file`: a template cannot author schema-level coactivation, and a fieldless
schema exposes no field keys to split a role across. The genuine dual cases are recorded at fixture
level as `also_schema` (`legal`, `photos`).

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`. Deliberate.

Candidates rejected rather than minted:

- `bill_id`, `stage`, `committee`, `sitting_date`, `member`, `division_id`, `inquiry_ref` — none is a
  canonical key and the schema declares no fields. Minting them here would pre-empt the anchor's own
  open question, which already defers "a bounded proceeding/programme/case reference" to a central
  decision.
- `record_type` is scoped to Finance; `work_type` has no government schema to attach to.
- **Stage specifically is not proposed even as a candidate**, because it is not a fact. It is a total
  order over an existing version family. This is the row's one substantive field-design opinion and
  it reduces rather than expands the eventual schema.

`time_first` is false despite one genuinely time-primary group (the sitting). A bill spans months and
its prints, amendments, and divisions are separated by exactly the intervals a date-first hierarchy
would use as boundaries; time-first would guarantee the scatter.

## Recognition boundary, restated

Strong evidence is always *apparatus + custody*. Apparatus alone gives a reader's copy; custody alone
gives a member's HR file. Weak evidence stays weak in combination: a legislature name, a bill-shaped
token, statutory vocabulary, meeting furniture, an official domain, a folder name, and a download
session do not activate this row in any quantity. A filename may surface a candidate for local review
— it may not create a bill, stage, committee, sitting, or member fact, and there are no such facts to
create.

Activation is not grouping. `Amendment 47.docx` with no bill identifier may join a candidate group
through a coordinate reference resolved locally, while this row does not activate from the filename
and no bill fact is copied onto it. Every fixture that behaves this way is marked
`group_without_copying_facts: true`.

## NEEDS-JOSEPH

1. **The publicity inversion.** A recorded vote and a speech are named-person data published by
   design, but the schema default protects named-person material. Alternatives: (a) a template may
   relax a schema-level privacy default when the material is published by design — flexible, but it
   opens a general precedent for weakening privacy from a leaf; (b) the mixed packet always dominates
   and everything stays `potentially_sensitive` — safe, but it means a public division list is
   handled like a citizen case file, and it makes the row's strongest node-test leg partly
   unenforceable. This row assumes (b) and argues for (a) being decided centrally. The sharpest test
   case is a standards committee's draft report naming a member.
2. **Embargo and correction status.** "Uncorrected — not yet approved by the witnesses" and "embargoed
   until 00:01" are time-bound restrictions the catalogue has no representation for. Alternatives:
   treat them as literal observations only and never act on them (this row's assumption); or admit a
   time-bound restriction concept, which is a P7 question and probably wider than government.
3. **The two-capacity body.** A council is one organisation acting legislatively and administratively.
   Alternatives: per-document evidence (this row's ruling, at the cost that a packet is not a group);
   or a packet-level owner rule that would put ordinance readings under municipal administration and
   lose the apparatus distinction entirely.
4. **If PR-6 lifts**, decide whether a bounded proceeding reference (bill or inquiry) may exist as a
   government field and whether it is destination-eligible — and please carry forward the finding that
   legislative stage should be an ordering on version-family, not a field and not a dimension.

## Self-verification

`python3 -m json.tool` parses the node. Key set matches the landed launch rows. Every `00` span in
quote marks was `grep -c`-verified verbatim (all returned 1). Every edge id
(`government.public-authority-record`, `government.policy-development`,
`government.regulatory-rulemaking`, `government.public-consultation`,
`government.municipal-administration`, `government.constituent-casework`,
`business_operations.board-governance`, `nonprofit.advocacy-campaign`) was confirmed present in
`roster.json`. Every `falls_through_to` name is one of `00`'s nine residuals. Every
`file_examples.source_type` is in `SOURCE_TYPES`. No fact is a folder path, no threshold number
appears, no handling class is assigned, and `fields`/`proposed_fields` are empty as PR-6 requires.
Only the two assigned files were written.
