# Research memo — `law_practice.transactional-deal`

Depth: J-DEPTH
Date: 2026-08-26
Kind: template on the fieldless `law_practice` schema · `parent_id: null` · `launch: placeholder`
Output: `planning/domains/nodes/law_practice.transactional-deal.json`
Assignment neighbours: `legal`, `career`, `finance`. Assignment residuals: Protected Records, Review Later.

## Result

**Accept, on a much narrower claim than the roster name suggests.** The row survives as the
**deal-level spine** of a negotiated corporate transaction: the codename, the working group list,
the steps plan, the conditions-precedent tracker *while conditions are open*, the disclosure letter
and its indexed bundle, the signing-authority pack, the insider list, the embargoed announcement.
It **cedes** diligence findings to `law_practice.due-diligence`, the redline life of one instrument
to `law_practice.contract-negotiation`, the completion event to `law_practice.closing-binder`, the
registered-parcel transaction to `law_practice.conveyancing`, the permanent register consequence to
`law_practice.corporate-secretarial`, and every executed instrument to `legal`.

I expected to refuse. It survives on one structural fact I could not explain away: this is the only
world in the family whose organising token is **pseudonymous and shared across several firms**, and
that fact moves all three legs of the node test at once.

## The charge, at its strongest, before any research

1. **It is a `work_type` value.** The schema anchor's own `work_types[]` carries *"transaction
   document set, due-diligence report, data-room index and completion or closing record"* as one
   value. "Transactional" = *the matters that are transactions rather than disputes*.
2. **It is a practice-area word.** The anchor struck it: *"A PRACTICE-AREA WORD ALONE — family,
   criminal, immigration, conveyancing, probate, employment, intellectual property, corporate. A
   practice area is a VALUE, not a structure."* My id is that struck token wearing a longer name.
3. **It is a lifecycle arc.** Instruction → diligence → drafts → conditions → signing → completion.
   That is a matter's lifecycle, which the schema's prose already handles at the *function* level.
4. **It duplicates six neighbours** — `due-diligence`, `contract-negotiation`, `closing-binder`,
   `conveyancing`, `corporate-secretarial`, `settlement`. Carve each out; ask what is left.
5. **It duplicates its own schema's default template** — matter → function → period, client level
   seeded ineligible. A deal is a matter.
6. **It is defined by absence** — the practitioner transactions that are neither conveyances nor
   litigation.
7. **It is never-alone evidence** — an entity pair plus transaction vocabulary plus a firm name is
   three struck tokens, and three struck tokens do not make a schema.

Charges 6 and 7 fail on inspection: the row has a positive anchor (below), and that anchor is a
**column set plus a role enumeration**, which survives the schema's own deletion test — strike
every entity name and every document-type word from a working group list and a *Role* column with
six distinct organisational sides is still standing. Charges 1–5 needed real work.

## The positive anchor

**A repeated codename-shaped token, plus at least one artefact whose own labelled slots enumerate
three or more organisations in separately named deal roles, one of which is the holder's
practitioner side.**

The load-bearing artefact is the **working group list**: columns *Organisation / Role / Name /
Title / Direct / Mobile / Email / Initials*, where *Role* carries Buyer, Seller, Target, Buyer's
counsel, Seller's counsel, Financial adviser, Lender's counsel, Tax adviser — and where the
*Initials* values reappear in the footers of the drafts. Read through 00's spreadsheet path:
*"Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file
metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when
useful, and dates or identifiers from labeled cells"*.

## Defeating charges 1–5

**Charge 1 — partly conceded**, recorded as **NJ-TD-1** rather than smoothed. The enum is a values
list for a field the schema does not declare, so it cannot settle which situations are templates;
read strictly it also folds `due-diligence` and `closing-binder` into one value, which R1c has not
done. What settles the row is the three legs below. If R1c reads the enum as binding, **refusal is
correct** and the JSON's `open_question` says so.

**Charge 2 — defeated by the anchor being structural, not topical.** A practice-area reading would
fire on the word "corporate", on a department's letterhead, on any share purchase agreement. This
row's test fires on none of those, and *would* fire on a codenamed multi-side pack with no
practice-area word anywhere on it. I struck the practice-area token in `never_alone` in the
anchor's own words so the row cannot be re-read that way later.

**Charge 3 — defeated by not claiming the arc.** Every phase is given away to a sibling in
`collides_with`. What remains is what is about the transaction *as a whole* and belongs to no
single phase or instrument. A row holding only the cross-phase spine is not a stage of anything.

**Charge 4 — answered with seven reciprocal boundaries, each naming the same fixture on both
sides.** See below.

**Charge 5** is the one that matters, and it is the node test.

## Node test — three legs

**Leg 1 — detection differs, and the schema default would *under-fire* here.** The anchor's default
requires *both* (i) an exact matter/file/engagement reference repeated across two or more
artefacts, and (ii) one artefact whose labelled slots separate a **practitioner or firm** role from
a **client** role. Neither describes a deal file. (i) fails because the token common to a deal
corpus is usually **not** the holder's matter reference — most documents arrived from other firms
under *their* references, and the codename is what is on all of them. (ii) fails because the
characteristic artefact separates **three or more organisational sides**, not two roles; a working
group list has no client column at all. Applying the default unchanged leaves most of a real deal
folder unrecognised. That is a detection-signal difference, not a restatement.

**Leg 2 — the recommendation differs, and it inverts the schema's privacy rule.** Dimensions are
empty by contract (PR-6; no declared field to branch on; no deep template unlocks from a safety
co-activation, since *"Finance, identity, medical, and legal material should be implemented first
as safety domains"*). But the anchor is explicit that its **prose** recommendation is the paragraph
every template must differ from. The schema seeds the client level ineligible because a client name
is a disclosure. **Here the first level is the codename, and a codename names nobody** — it exists
to conceal the parties. So this row asks for its organising token to be seeded
destination-*eligible* where the schema seeds its equivalent ineligible, under 00's *"local-first
and data-minimizing"* posture. Two riders: the codename may never be co-displayed with a party name
in the same tree (the *mapping* is the leak, not either half), and function still follows the deal,
because a work type *"is meaningful only after the course is known"* — a CP tracker or a signature
page is meaningless without its transaction. Not time-first: for document and record domains,
project, function or subject *"usually comes before time because putting year first scatters"*
related work across calendar folders, and signing, completion, document, circulation and filesystem
times all mean different things here.

**Leg 3 — the privacy rule differs in kind.** The schema protects a third party who cannot consent;
true here too, plus two additions. First, **the protected thing is the existence of the
transaction**, not only a person's identity: an unannounced deal is material non-public information
about legal persons, and leaking the codename-to-party mapping harms without naming anyone. That
produces a rule no sibling has — *the pseudonym may be shown, the mapping may not* — which makes
the working group list and the announcement draft the **most** protected files in the folder rather
than the most administrative. Second, the **insider list** is a register of named natural persons
with home addresses and national identifiers, compiled about people the holder usually does not
employ. 00's own corpus sentence describes the folder directly: a real collection *"can include
identity documents, account statements, tax records, medical information, legal records,
credentials, private correspondence, GPS metadata, employment materials, and educational records"*
— one deal file holds signatory identity documents, funds-flow account statements, disclosed
private correspondence and key-employee schedules at once.

Three legs differ. Template, not a relabelled default.

## Files considered and **rejected**

| File | Why it is not this row's evidence | Where it goes |
|---|---|---|
| **`Project Sunrise - Strategy Offsite.pptx`** | Codename token in the filename and on the title slide; attendees from **one** organisation; no role column, no clause references. Codenames are used for reorganisations, product launches, redundancy programmes and offsites. This is the `never_alone` strike made concrete. | Review Later. Kept as a fixture. |
| **`Acme Capital - M&A Opportunity - Project Hartley - pitch.pptx`** | Codename + transaction vocabulary + valuation range + fee proposal, and **no practitioner apparatus**. An adviser's pitch is not evidence that a mandate exists. | Review Later / `career.consulting-client-engagement`. Fixture. |
| **`Share Purchase Agreement - executed and dated.pdf`** | Bound party pair plus completed execution blocks — `legal`'s signal, and `legal`'s safety protection runs first. This row keeps the *unexecuted* draft; `version_family` spans the seam. | `legal`. |
| **A firm's precedent SPA and specimen disclosure letter** | Every context term this row lists, plus the warranty numbering — but **no parties, no side, no codename**, party slots deliberately open. The schema's inverse-recognition case, and the reason the Reading Inbox residual is unusually large here. | Reading Inbox / `law_practice.precedent-bank`. |
| **A contacts export or firm distribution list** | Names, titles, phones, emails — every WGL column *except the role column*. The role enumeration is the whole signal; contact data is not. | Not activated; contacts are privacy-protected, not folder-proposal material. |
| **A data-room bulk download folder** | Arrived together, official-looking, numbered. A session is not a deal: *"never be treated as proof of topic"*. The room's folder structure is the room's. | Review Later. |
| **A founder's own sale pack** | Codename, WGL, CP tracker, disclosure letter — held as *recipient*, no matter reference of the holder's own firm, no work product the holder produced. Treating this as a client file would be the row's worst error. | `legal.personal-legal-matters` / `business_operations`. |
| **A law firm's own partnership merger papers** | A correctly codenamed deal, but the firm running *itself*. A firm name on letterhead is the anchor's never-alone token. | `business_operations` / `finance`. |
| **A news report or market study of deal terms** | Real parties, real transaction, published. No side, no client, no third party in it. | Reading Inbox. |
| **`Project Hartley - Bible - password protected.zip`** | The filename cannot manufacture a deal, a party, a sensitivity result or membership. Not forced open — *"the normal scan should never extract archive contents to the filesystem"*. | Unsupported or Encrypted. Fixture. |
| **`Report on Title - Project Harbour property portfolio.pdf`** | `conveyancing`'s declared collision fixture; identical phrase, real title numbers, but a portfolio schedule and a corporate addressee. | Boundary case. Fixture. |

## The collision fixture

**`Completion Agenda - Project Hartley - v14 (clean).docx`.** The file that looks exactly like my
evidence and is only sometimes mine. `law_practice.closing-binder` declared it from its side first
and I reciprocate in its terms: **as a versioned working draft with an empty `Status` column and no
stated completion date it is mine; with `Status` populated against an operative completion date, or
bound into a contiguous tab-numbered closing index, it is the neighbour's.** The same document is
genuinely both at different times — which is why **neither row may claim it from a filename**, and
the filename is identical in both states. What discriminates is the population state of one column
plus the presence of an operative date. Nothing else.

## Reciprocal boundaries (both directions, same fixture on both sides)

- **`law_practice.closing-binder`** ↔ this row. *Completion Agenda*, as above. Back the other way:
  the document-status matrix with signatory and delivery columns, the counterpart-signature
  release, the funds flow and the bible manifest leave my scope entirely. That row wrote the same
  seam with the same fixture.
- **`law_practice.due-diligence`** ↔ this row. *Disclosure bundle / data-room index*: findings
  flowing **inward** (buyer-side report, red-flag summary, index enumerated for inspection) →
  theirs; the seller's structured qualification of its **own** statements flowing **outward**,
  indexed to another document's warranty paragraph numbering, plus the bundle it declares → mine.
  Direction and tense, never the word *index*.
- **`law_practice.contract-negotiation`** ↔ this row. *`SPA - v12 (blackline vs v11 SC markup)`*:
  the redline life of **one** instrument, its comparison headers, its issues list, its turn record
  → theirs; deal-level artefacts belonging to no single instrument → mine. `version_family` spans
  the seam without either row copying a fact. **My finest seam, flagged as possibly too fine —
  NJ-TD-2.**
- **`law_practice.conveyancing`** ↔ this row. *Report on Title*: one parcel, third-party returns
  keyed to it, an apportionment at a completion date, a registry application → theirs; deal
  codename, entity pair, CP checklist, disclosure letter, property as a diligence **chapter** over
  many parcels → mine. A corporate acquisition owning freeholds is a deal that owns land; a
  residential purchase by a company is a conveyance with a corporate buyer. That row asked R1c for
  this reciprocal — **here it is.**
- **`law_practice.corporate-secretarial`** ↔ this row. *Signing protocol and board approvals pack*:
  resolutions and powers of attorney assembled **for one signing event**, unexecuted and bounded by
  the deal → mine while the deal is live; the permanent register entries those acts cause, which
  exist before the deal and outlive it → theirs. That row wrote this reciprocal too.
- **`business_operations.contract-administration`** ↔ this row. *CP Checklist*: conditions of **one
  unclosed transaction**, clause-cross-referenced into a single named agreement → mine; live
  obligations across **many unrelated contracts** with renewal and notice dates → theirs. Never
  decided by which profession keeps the table — the anchor named this generic trap and I answer it.
- **`legal`** ↔ this row. *The share purchase agreement*: unexecuted with an open execution page →
  mine; executed and dated with a bound party pair → `legal`'s, whose safety protection runs first.
  I never reclaim it because a deal group contains it.

## Neighbours considered that did **not** get an edge

- **`law_practice.matter-correspondence`** — correspondence is a *function within* a matter, not
  competing evidence. An edge would begin a taxonomy.
- **`law_practice.settlement`** — negotiated and executed like a deal, but its anchor is a dispute
  being resolved: no codename, no WGL, no CP tracker. `closing-binder` already carries the
  execution-mechanics seam against it.
- **`law_practice.regulatory-submission`** — merger-control filings arrive inside a deal, but the
  authority-side submission record is that row's. My CP tracker *row referencing* a clearance is
  mine; the filing is not.
- **`career.consulting-client-engagement`** — named in the assignment; the adviser pitch deck is a
  fixture here, but the discriminator is the schema's existing one. Restating it at template level
  would duplicate the schema's seam.
- **`finance.loans-mortgage`** — acquisition financing sits beside a deal, but the lender's offer to
  the borrower is the neighbour's on its own evidence. No shared discriminating item at this level.
- **`business_operations.corporate-regulatory-filings`** — reached through `corporate-secretarial`;
  two edges for one seam would be padding.
- **`photos.screenshot-captures`** — the data-room screenshot co-activates on positive screen-origin
  evidence. A fixture note (`also_schema: photos`), not a mutex.
- **`research.*`, `code`, `medical`** — no evidence path. Native-format productions do not activate
  Code; disclosed medical records keep their own schema's evidence and protection.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`, `role_split: []`.
PR-6 leaves `law_practice` fieldless, so a template has nothing to reuse and nothing to branch on,
and `role_split` needs two field keys the schema does not expose.

**I mint nothing.** The one candidate is the codename. The anchor has already proposed `project`
for this schema and the brief says reuse an existing proposal rather than mint a variant, so
`deal_reference` is **not** proposed — it would be exactly the synonym the contract forbids. The
strain is real and recorded as **NJ-TD-3**: a codename is a concealment token rather than a body of
work, and `project` is destination-eligible in Research and Code for reasons that do not transfer.
`version_family`, `file_type`, `creation_date`, `language`, `authored_by` and `sensitivity_status`
are the universal facts the fixtures actually carry; none is this schema's, none needs proposing.

## Grouping without copied facts

A candidate group is bounded by **one codename plus one role enumeration**, or by an exact clause /
CP / tab / version reference. A valid anchor supports membership and writes nothing onto its
members — an indexed bundle member acquires no deal, party, price, date or status fact.
*"It should not form a supported group when there is no valid anchor"*, and the converse holds too.
Sparse members (a marked-up schedule page, a signature-page scan, an attendance note) join via
`group_without_copying_facts` rather than inheriting.

What may **not** bridge, stated so the row does not recreate the deal from noise: matching party
names across two transactions, a shared adviser, a shared completion date, a download or scan
session, a folder called *Deal*, and **semantic similarity between two agreements** — which are
near-identical by drafting convention, so similarity would bridge unrelated confidential deals.
That last is a privacy rule before it is an accuracy rule.

## Sources

The standing brief and the stamped assignment; `legal.practice-matter-file.research.md` as depth
calibration; the schema anchor `law_practice.json` (recognition, template prose, sensitivity,
`work_types`, `proposed_fields`); the four landed neighbours that had already argued a boundary
against this id, found with one grep — `closing-binder` (.json + memo), `conveyancing` (.json +
memo), `corporate-secretarial` (.json); `canonical_fields.json`; `roster.json` for every edge id;
and targeted greps into `00`. Every span in quote marks, in the JSON and here, was grep-verified
verbatim against `00` before use.

## NEEDS-JOSEPH

1. **NJ-TD-1 — the work_type charge.** The anchor's enum bundles this row, `due-diligence` and
   `closing-binder` into one value. Answered *no* on three differing legs, **not** on the enum.
   Alternatives: (a) keep as written; (b) read the enum as binding → **refuse**, routing drafts to
   `contract-negotiation`, indexes to `due-diligence`, completion to `closing-binder`, executed
   instruments to `legal`, strays to Protected Records. *This row would rather be folded than
   padded.*
2. **NJ-TD-2 — the contract-negotiation fold.** The deal-level / instrument-level split is real but
   fine. (a) keep both as authored; (b) fold `contract-negotiation` in here as a drafting function;
   (c) fold this row into it — which loses the codename anchor, the loss this memo argues matters.
3. **NJ-TD-3 — the codename as a field.** Reuse the anchor's already-proposed `project`, mint one
   key later, or leave the codename search-only. Nothing minted here.
4. **NJ-TD-4 — the codename branch.** This row asks for the codename to be seeded
   destination-*eligible* where a client name is not, because a pseudonym names nobody. Counter: in
   a single-deal corpus the codename resolves to one client anyway and the branch discloses by
   inference. Alternatives: eligible with user approval; eligible only where the corpus provably
   spans more than one deal; search-only.
5. **NJ-TD-5 — the mapping rule needs an owner.** "The pseudonym may be shown, the mapping may not"
   is a display rule this catalogue can state but not enforce. P7 and P9 must decide whether a
   group label, a proposal preview or a model dossier may ever carry both halves.

## Recommendations to R1c (no file outside this node was touched)

1. `law_practice.contract-negotiation` and `law_practice.due-diligence` owe the reciprocals — both
   are named here with the fixture on both sides, and neither has landed, so their authors can take
   the seam as written or contest it.
2. `closing-binder`, `conveyancing` and `corporate-secretarial` each asked R1c for this row's
   reciprocal; all three are now authored here in their own fixtures and terms. Nothing in their
   files needs changing.
3. `finance.cap-table-equity`, `business_operations.board-governance` and
   `business_operations.contract-administration` owe return edges.
4. Do **not** add `matter-correspondence`, `settlement` or `regulatory-submission` edges; the
   reasons are above and adding them would begin the practice-area taxonomy the anchor forbids.

## Self-verification

`python3 -m json.tool` parses. Key set matches the landed siblings (the anchor's
`proposed_context_terms` included; `conveyancing` carries the same field as `null`). All ten edge
ids confirmed present in `roster.json`. Every `file_examples.source_type` is in `SOURCE_TYPES`;
every residual name is one of 00's nine. No file example writes a folder path as a fact. Every
quotation greps back out of `00` verbatim. No threshold number, no confidence score, no handling
class. Two files written, nothing else touched.
