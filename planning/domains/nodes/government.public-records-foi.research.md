# Research memo — `government.public-records-foi`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.public-records-foi.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept the node.** It survives a charge that very nearly killed it. Its distinct job is the answering
authority's own file for one external request for recorded information — receipt, search, item-by-item
schedule, exemption reasoning, redacted release, withheld original, refusal, review, appeal. It passes
the template test on two of the three legs (detection signals and privacy rules), and honestly fails on
the third (dimensions) for a contract reason that applies to every government child equally.

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `also_holds_with: []`, `role_split: []`.
Five `collides_with`, six `falls_through_to`, 18 fixtures.

## Sources read

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — in full.
- The stamped assignment via `make_prompt.py government.public-records-foi`.
- `planning/00-database-agent-product-design.md` — **by targeted grep only**, per the token discipline.
  Every span I put in quote marks was grep-verified verbatim against the source before writing, and
  re-verified mechanically after writing (see Self-verification).
- `planning/domains/nodes/government.json` — my schema anchor, read as JSON. Its `.research.md` was
  **not** opened: the anchor's `recognition`, `work_types`, `template.why`, `grouping_reasons`,
  `sensitivity_why` and `open_question` settled the node test without ambiguity.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — the one launch row read for depth
  calibration. It is also the source of my `also_holds_with` / `role_split` reasoning pattern.
- `planning/domains/roster.json` — every edge endpoint confirmed against a real `domain_id`.
- One grep for landed rows naming my id, then a machine extraction of only the edge objects that
  named me. Four rows had already argued a boundary against this one.

Deliberately not read: other R1b rows "for context"; the `clinical_practice` /
`business_operations` / `construction_property` memos, which the brief classes as debt.

## The charge — the strongest case that this row should not exist

I put five arguments against my own id before writing anything. The first is much stronger than the
others and deserves stating in its sharpest form.

**1. It is a `work_type` value of its own schema, verbatim.** `government.json` already lists, in
`work_types[]`, the string *"information request, search record, disclosure schedule, redaction record,
refusal, review, or appeal response on the records-holder side."* That is not a paraphrase of this row;
it is this row, enumerated as a value on the schema I am a template of. The brief's own kill criterion
says work types are values, not nodes. On its face this row is a value that escaped its enum and
claimed a node.

**2. It is a lifecycle stage / a document-type pair.** "A request, and the response" is correspondence
in and out. Every other government row also has a receive-decide-answer arc. Naming the arc is not a
filing world.

**3. It is a duplicate of a neighbour.** `government.archives-recordkeeping` is also a records-holder
row that also issues access decisions with exemption reasoning. Two rows deciding who may see held
records is one row with two labels.

**4. It is defined by an absence.** Redaction and refusal are the absence of content. A row whose
signature is *what is missing from a page* is the classic non-node.

**5. Its only evidence is never-alone.** A statute name, an exemption clause, and a reference-shaped
token. `government.json`'s own `never_alone` already forbids *"legal, policy, regulatory, compliance,
public-interest, civic, election, procurement, permit, licence, grant, or statistical vocabulary
alone"* and forbids a public body's name alone. Strip those and there may be nothing left.

### Defeating the charge

**Against (1), the serious one.** The schema anchor's enum entry is evidence that this world exists on
the authority side, not that it is only a value. The test is whether the *recognition* differs, and it
does, structurally: this is the only government situation whose **organizing anchor is a stranger's
request rather than the authority's own programme**. Every other government row opens a case because
the body decided to act — to consult, to procure, to rule, to inspect, to run an election. This one
opens a case because an outsider sent an email, and the reference is minted *by* the authority *for*
that outsider. That inversion produces artifacts that exist in no other government row: the **schedule
of documents** (repeated item rows carrying description, date, per-item disposition, per-item exemption
— the signature structure), the **search record** (systems, custodians, terms, nil returns), and the
**disclosure log** (a register whose requester column is anonymised *by design*). None of those are
document types of a general authority record; they are the machinery of answering an outsider. A value
in an enum cannot carry its own artifact grammar. This one does.

**Against (2).** A lifecycle stage would share the surrounding world's evidence and differ only in
date. This row's evidence is *dual-object*: the case file about the request, and the disclosed records
that are the subject of the request, are two different corpora that must not merge. A released bundle
contains copies of a procurement evaluation, an inspection report, a mailbox extract — each of which
carries its own schema evidence. No lifecycle stage has that shape.

**Against (3).** The archives row itself supplied the discriminator, and I adopt it unchanged rather
than inventing my own: *custody workflow with an opening date* versus *request workflow with an
external requester and a response clock*. `Access Review for MS-0603-14 closed until 2059` is theirs;
`Disclosure Schedule for FOI Request 2026-118` is mine. Its memo also says a redaction record alone
decides nothing, which is exactly my position from the other side. Two rows that can hand each other
the same fixture and both give the same answer are not duplicates.

**Against (4).** The row is not defined by redaction. Redaction is in `never_alone` precisely because
litigation productions, published court exhibits, journalists' copies, and research anonymisation all
redact identically. What defines the row is the *pairing*: a redacted release and an unredacted source
of the same item set under one reference, held together, with opposite intended exposure.

**Against (5).** Correct, and encoded. Statute names, exemption clauses, reference tokens, black boxes,
FOI-named folders, and deadline cadence are all in `never_alone`, each because a specific fixture in my
list trips it. What activates is a *combination with a role*: a decision letter carrying all four of a
received date, a response-due date, a disposition and a review-rights paragraph, issued outward by the
holder — or one reference threading receipt, search, schedule, decision and review.

**Verdict: the charge fails, but only just, and only on the request-workflow inversion plus the
exposure split.** If R1c later finds those two arguments unpersuasive, this row should be folded into
`government.public-authority-record` and the coverage routed through Protected Records and Independent
Records. I would not contest that outcome; I record it as the honest alternative.

## The node test, all three legs

The test as the brief states it: a template exists only when its **detection signals**, **recommended
dimensions**, or **privacy rules** differ from its schema's default template.

**The government default template.** From `government.json`: activation requires evidence that the
holder or producer is a public body acting in an authority-side role; a bare government name, a
.gov domain, public-sector vocabulary, a downloaded publication, or an authority-issued document held
by its recipient are all excluded. Grouping is by an evidenced proceeding, decision lifecycle,
governance cycle, submissions packet, statistics cycle, case, or export manifest. Posture is
protected-by-default. `dimension_order` is empty because PR-6 leaves the schema fieldless.

**Leg 1 — detection signals: DIFFER.** The default's role precondition asks *is the holder the
authority?* Mine adds a second, independent question the default never asks: *is there an external
requester whose request opened this file?* Concretely, three of my deterministic signals cannot be
stated on the default at all — the per-item disposition-and-exemption schedule, the anonymised-requester
register, and the paired redacted/unredacted version family under one reference. My `never_alone` also
carries three entries the default does not: redaction-as-treatment, the request-reference token, and
statutory deadline cadence. These are not extensions of the default; they discriminate against
fixtures the default would happily accept.

**Leg 2 — recommended dimensions: DO NOT DIFFER.** Both are empty. I state this plainly rather than
manufacturing a difference. Under PR-6 no government template can differ here, so the leg is
uninformative for the whole schema rather than adverse to this row. The prose order I would recommend
if fields were ever ratified is in `template.why`: bounded request, then response stage, then item —
never the requester. Time is not first, because *"For document and record domains, project, function,
or subject usually comes before time because putting year first scatters related work across calendar
folders"*; a request received in December and answered in February would otherwise be split across two
year folders. Any such order stays editable: *"The system recommends an order based on the domain
template, but the user can reverse, remove, add, or flatten dimensions."*

**Leg 3 — privacy rules: DIFFER, and this is the decisive leg.** The government default is uniformly
protected. This row is the one government situation with a **deliberately split exposure inside one
packet**: the redacted release is prepared *for publication* and often is published in the disclosure
log, while the unredacted source, the schedule describing withheld material, the exemption rationale,
and the requester's identity are among the most protected material the authority holds. That produces
a rule the schema default does not contain and could not contain: **the released and withheld copies
are a version family whose members have opposite intended exposure, and release status must never
propagate across it.** Ordinary version-family reasoning — treat versions alike, inherit status from
the newest or the most-shared — leaks the original here. A second rule follows: the requester is a
named private individual whose interest is normally irrelevant to the answer, so their name must never
become a display label, a group key, or a dimension. In casework the person *is* the subject; here they
are a stranger with no stake in the record. The design's constraint applies with unusual force:
*"Privacy policy must be enforced before content reaches any model or external connector."*

Two legs of three differ, one of them decisively. The node stands.

## Files considered and rejected

The tempting false positives, and why each is not this row's evidence.

- **`FOIA response - City Water Dept - obtained 2026-05.pdf`** in a story folder — byte-identical to my
  own fixture, same reference, same exemption codes. Rejected: the holder is the requester. Discriminated
  by the absence of receipt, search, schedule, or outward-issuing structure and by the presence of a
  draft and fact-check apparatus alongside. This is the primary collision fixture (below).
- **`Access Review - MS-0603-14 - closed until 2059.pdf`** — exemption-shaped reasoning, restriction,
  a reference. Rejected: an accession reference and an opening date, not a request reference and a
  response clock. Archives.
- **`Privilege Log - Acme v Beta - Set One.xlsx`** — a per-item withholding table, columnar shape
  indistinguishable from my signature schedule. Rejected: caption and party in the header instead of a
  request reference and an authority; litigation withholding is not an access exemption.
- **`Request for my own file - response - Council.pdf`** — a personal-data request where requester and
  subject are the same person, held by that person. Rejected: it is the individual's own record, on
  authority letterhead. Authority letterhead is never-alone evidence.
- **A published transparency report or open-data release** — an authority's own output, downloaded.
  Rejected on the schema's own ground that publication by government is not authority-side custody;
  routes to Reading Inbox.
- **A campaigning site's template request letter, or a "how to make an FOI request" guide** — dense
  access vocabulary, no case. Rejected; Reading Inbox.
- **A redaction-tool project file or a scanned bundle with burned-in black boxes and no text layer** —
  redaction as treatment. Rejected; Unsupported or Encrypted rather than forced OCR.
- **A live case-management system, mailbox, or portal account** — a source system, not a file node.
  Only a bounded export with a readable manifest is represented, and it stays shallow.
- **Contact exports containing requester, officer, or oversight-body addresses** — not activated by
  names. `contacts` is deliberately absent from `file_kinds.source_types` for that reason, unlike the
  schema anchor which permits it.
- **The records inside a released bundle** — a disclosed procurement evaluation is *not* this row's
  evidence in its own right; it is a member that retains its own schema evidence. Treating bundle
  members as FOI evidence would let one disclosure rewrite how an authority's own source record is held.

## Reciprocal boundaries

Each states the boundary in both directions and names the same fixture on both sides. Three were
already authored against me by landed rows; I adopt their wording rather than competing with it.

1. **`creative.journalism-reporting`** — fixture `FOIA response - City Water Dept.pdf` and the request
   bundle archive. Theirs: the requester's side, resolved by a story slug, draft, or fact-check
   apparatus. Mine: the authority's own process around the release. Reciprocal in their words and mine:
   this row must not claim a reporter's obtained bundle merely because it carries a statute and a
   reference number; that row must not claim an authority's own disclosure file. Where neither
   structure is present, Independent Records.
2. **`government.archives-recordkeeping`** — fixture: a document naming a reference and refusing or
   deferring access. Theirs: custody workflow, accessioned item, opening date. Mine: request workflow,
   external requester, response clock, answer sent outward. Both sides agree a redaction record alone
   decides nothing.
3. **`government.constituent-casework`** — fixture `RE Case 8841 - third chase.eml`, named identically
   on both sides. Theirs: an intermediary asking about one named person's own matter, where the
   person's identity is the basis of the request. Mine: the holder's disclosure process, where the
   requester's identity is normally irrelevant to the answer. Chase cadence alone decides nothing.
4. **`government.public-authority-record`** — fixture `FOI-2026-0412-export.zip` and the bundle inside
   it. Theirs: the body's own function — the evaluation, inspection, or briefing that the bundle
   discloses. Mine: the request wrapper. Reciprocal: disclosed copies keep their own authority-side
   evidence and acquire no request or release facts from membership here; and this row does not absorb
   a source record because a disclosure once quoted it. Wrapper absent, source present → theirs.
5. **`legal.practice-matter-file`** — fixture: the per-item withholding table, `Privilege Log` against
   `Schedule of Documents`. Theirs: representation plus tribunal or discovery process. Mine: an
   external information request answered by a public body. Reciprocal: neither row may claim the
   other's table from columnar shape alone.

## The collision fixture

`FOIA response - City Water Dept - obtained 2026-05.pdf`, sitting beside `lead-pipes-draft-v3.docx`.
It is the hardest case in the catalogue because the bytes are **identical** to my strongest fixture —
same reference, same exemption codes, same signature block. Nothing inside the file discriminates it.

What discriminates it is entirely outside the file: the **presence of the answering apparatus**. The
authority's copy sits with a receipt email, a search record, a schedule, and a version-family sibling
that is unredacted. The requester's copy sits with a draft and a fact-check sheet and has no unredacted
sibling — it cannot, because the requester never held the withheld material. **The absence of an
unredacted sibling is the cheapest available discriminator, and it is asymmetric: its presence proves
the authority side; its absence proves nothing on its own** (an authority may release in full). Where
neither apparatus resolves it, both rows abstain and the file is a standalone document with a durable
purpose and no group — Independent Records.

## Fields and dimensions

`fields: []` and `proposed_fields: []` are deliberate and I want the reasoning on record, because a
request reference is an obvious candidate and I chose not to propose it.

PR-6 leaves `government` fieldless and D1's deferral stands; the anchor's own `open_question` already
routes any minimal role-safe vocabulary to **central** adjudication rather than to children. Proposing
a request-reference key here would pre-empt that adjudication from inside one child, and would create
exactly the variant-minting the brief forbids — `request_ref` competing with whatever the schema-level
decision names. Candidates I considered and did not propose: a request reference, a requester role, a
response disposition, an exemption basis, a release status. Every one of them is dangerous as a
destination even if ratified: a folder named for a requester discloses that a person asked and what
they asked about, and a folder named for a release status hard-codes a legal conclusion this system
must not draw.

`time_first: false`, argued above.

## Recognition boundary, in one paragraph

Strong evidence is a combination of an authority-side role and a request workflow: one reference
threading receipt, search, schedule, decision and review; an item-level disposition-and-exemption
schedule; a decision letter with received date, due date, disposition and review rights; an anonymised
request register; a paired redacted/unredacted version family; an oversight case reference beside the
authority's own. Weak evidence stays weak in any combination without the role and the request: statute
names, exemption clauses, reference tokens, black boxes, transparency vocabulary, deadline cadence,
FOI-named folders, download sessions, and public-body branding. A filename may retrieve a candidate for
local review; it cannot create a request. Activation is not grouping: a bare `Public Interest Test -
FOI 2026-0455.docx` or a chase email may join a request neighbourhood through an exact reference while
this row does not activate from the file itself, and those fixtures are marked
`group_without_copying_facts: true`.

## Deliberate non-edges

- **`government.public-consultation`** — also receives material from outsiders, but a consultation is
  the authority's own initiative with a published call; the requester-opened inversion is absent. If a
  landed consultation row later claims the same fixture, R1c should add the pair.
- **`business_operations.corporate-regulatory-filings`** — the landed row already declined to edge me,
  reasoning that the which-side discriminator is carried by `government.public-authority-record` and
  tripling it adds nothing. I accept that and do not add the reverse edge.
- **`research.reading-library`** — not a same-evidence mutex; a downloaded disclosure with no accepted
  purpose falls to Reading Inbox, which is already a residual here.
- **`nonprofit.advocacy-campaign`** — campaigners file requests in volume, but that is the requester
  side and is already covered by the journalism boundary's reasoning. Flagged for R1c rather than
  duplicated.
- **`photos.screenshot-captures`** and **`legal`** — handled as fixture-level `also_schema`
  coactivation, not as edges. `also_holds_with` is empty for the same reason the landed
  `legal.practice-matter-file` row left it empty: a template cannot author schema-level coactivation,
  and the fieldless `government` schema exposes nothing to split. `role_split` is empty for a stricter
  reason — the requester/holder split is a genuine role split and would be the natural place to use
  that edge, but `role_split` requires different **field keys** on each side and neither side has any.
  This is the cleanest example in the catalogue of a real role seam that the contract cannot express
  while PR-6 stands, and I record it rather than faking an edge.

## NEEDS-JOSEPH

1. **NJ-1 — request reference as a field.** If PR-6 is lifted, decide centrally whether a bounded
   request reference may exist as a government field, and whether it is destination-eligible.
   Alternatives: (a) no field, prose only, as now; (b) a field that is searchable but never a
   destination; (c) a destination-eligible field with redacted display labels. This row proposes none
   so as not to pre-empt the anchor's own deferral.
2. **NJ-2 — opposite-exposure version families.** Decide how P9 represents a version family whose
   members have deliberately opposite intended exposure, so released status can never propagate from a
   redacted copy to its unredacted source. Alternatives: (a) suppress version linking entirely when a
   member is protected — safe but loses a true relationship; (b) link but mark the family as
   exposure-heterogeneous and forbid status inheritance; (c) treat redacted and unredacted as unrelated
   documents. I recommend (b) but cannot settle it from the design docs.
3. **NJ-3 — disclosed records inside a bundle.** Decide whether bundle members are represented as
   members of the request with their own schema evidence intact, as duplicates of corpus originals, or
   both. The choice determines whether a disclosure can retroactively change how the authority's own
   source record is displayed — and (b) alone would let a release relabel an internal original.
4. **NJ-4 — scope of "public authority".** Hybrid, arms-length, contracted-out and quasi-public bodies
   are in scope of access regimes in some jurisdictions and not others. Alternatives: deployment-specific
   gazetteer, user confirmation, or permanent abstention. The anchor raises the same question; it should
   be answered once, at the schema, not here.

## Self-verification

- `python3 -m json.tool` on the node: **passes**.
- All six `falls_through_to.design_cite` spans and all five in-prose `00` quotations grep back
  **verbatim** against `planning/00-database-agent-product-design.md` (mechanical check, all OK).
- Every `file_examples.source_type` is in `SOURCE_TYPES`; no example writes a folder path as a fact.
- All five `collides_with` endpoints exist as `domain_id` in `planning/domains/roster.json`; all six
  `falls_through_to` names are `00` residual templates.
- `never_alone` entries are each true of a named fixture in the list (redaction → the privilege log and
  the journalist's copy; reference token → the journalist's copy; authority letterhead → the personal
  subject-access response; deadline cadence → the chase email).
- Key set matches `government.json`, including `proposed_context_terms`.
- No threshold numbers, no confidence scores, no handling classes, no `public_low`.
- Files written: exactly the two assigned. No roster, canonical-field, `src/`, `check.py`, SPEC, or
  neighbour file was touched.

## Final recommendation

Keep `government.public-records-foi` as a placeholder template with no fields, no dimensions, no
coactivation edge, and no role split. Recognize it by the request-workflow inversion — an external
requester opened this file, not the authority — and by the answering apparatus of schedule, search
record and register. Enforce the exposure split as the row's defining privacy rule: released and
withheld are one version family with opposite exposure, and status never crosses it. Never let a
requester's name become a label. Where the apparatus is absent, abstain and route conservatively.
