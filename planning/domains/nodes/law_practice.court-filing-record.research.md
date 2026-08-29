# Research memo — `law_practice.court-filing-record`

Depth: J-DEPTH
Date: 2026-08-26
Output: `planning/domains/nodes/law_practice.court-filing-record.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`

## Result

Accept, `refuse_node: false` — but only after the charge was pressed to the point where refusal was the
expected outcome, and only on one argument. The row survives because its activation structure is a
**transmission event asserted by a third party to the representation**, and the `law_practice` default
template provably cannot recognise it.

## Sources read

- `RESEARCH-BRIEF.md` (full) and the stamped assignment from `make_prompt.py`.
- `planning/domains/nodes/law_practice.json` — the schema anchor, read as the default template I am
  measured against.
- `legal.practice-matter-file.research.md` — one landed launch row, for depth calibration.
- `planning/00-database-agent-product-design.md` — by targeted `grep` only, per the token rule. Every
  span quoted below was `grep -c`-verified verbatim first; the residual library paragraph at line 120
  supplies the Receipts and Confirmations, Protected Records and Review Later wording.
- `planning/domains/roster.json` — grepped for sibling and neighbour ids. All eight edge ids verified
  present.
- Neighbour check: `grep -rl "law_practice.court-filing-record" planning/domains/nodes/` returned
  nothing. **No landed row has argued a boundary against me**, so every boundary below is authored
  from my side and each is a recommendation to R1c for the reciprocal half.

## THE CHARGE — the strongest case that this row should not exist

Stated at full strength before anything was written, because the brief is right that inventing a filing
world to save an id is this project's recorded failure mode.

**1. It is a value of `work_type`, and the schema says so in its own enum.** `law_practice.json`'s
`work_types` contains, verbatim, `"court or tribunal filing record and electronic-filing notice"`. The
row is therefore a candidate for the exact failure the anchor names: *a template row justified only by
holding a different legal document kind is the schema's default template with a narrower filename
filter.* The schema wrote that sentence to kill rows like this one.

**2. It is four document types wearing one name.** The `one_line_hint` lists receipts, stamped copies,
docket extracts and proofs of service. Four document types is four values, not a node — and the
anchor already ruled that a practice area is a value, following `clinical_practice` on specialty.

**3. It is a lifecycle stage.** "Filed" is what happens to a pleading between drafted and decided. A
stage in a document's life is not an organisational situation; it is a property of the document, and
the document has a sibling.

**4. Its privacy posture looks identical to the default.** Protected Records, `potentially_sensitive`,
no legal-status conclusions. Same as every sibling.

**5. Its dimensions are identical to the default.** Empty, by the same PR-6 contract.

**6. It may be a duplicate of a residual.** 00's residual library already contains a home for exactly
this shape: *"Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking
records, boarding passes, purchase receipts, event tickets, and similar transactional documents."* A
filing confirmation is a delivery confirmation. A row whose job is to catch confirmations may be a
second copy of a residual template, which is worse than a duplicate node.

That is six independent grounds, and any one of them would be enough. Legs 4 and 5 of the charge I
concede outright — the privacy *class* and the dimension *list* are the schema's. The row has to
survive on detection signals, on a differing dimension *recommendation*, and on a privacy difference
that is about **whose** data, not about which class.

## Defeating the charge

**Against 1 and 2 — the row is not a document kind, it is a document's shadow.** Every sibling in this
schema is named for what a document *says*: a pleading pleads, an opinion advises, a privilege log
lists withheld documents. This row's artefacts say nothing about a matter's substance. Their entire
informational content is *that a document moved, at a moment, to a destination*. A notice of electronic
filing contains no legal content and no argument; strip the case caption and you have a timestamp, an
entry number and a recipient partition. That is a different **kind of assertion**, not a different kind
of document, and it is why the same fixture (`Complaint - CONFORMED.pdf`) can be simultaneously a
pleading and a filing record without either row being wrong — the pleading sibling owns the body, this
row owns the stamp layer.

**Against 3 — a lifecycle stage would be a property of one document; this is an artefact class of its
own.** A notice of electronic filing, a docket extract and an affidavit of service are not versions of
anything. They are separate files, produced by separate issuers, and they outlive the document they
attest. The stamped copy is the only member that is also a lifecycle stage, and it is the member I
concede most of to `law_practice.pleadings`.

**Against 6 — and this is where the row earns its keep.** If this row is refused, an isolated notice of
electronic filing falls to Receipts and Confirmations, because that is where a delivery confirmation
with no accepted group goes. That is the wrong outcome for a specific and demonstrable reason: a filing
notice **names an adverse party in a caption and frequently names a sealed document**, and 00 puts that
class somewhere else — *"Protected Records may represent sensitive isolated material such as passport
scans, medical documents, account statements, visas, legal forms, or credentials; it should normally
remain local-only and must not cause filenames or content to be exposed in model prompts."* A generic
receipts bin would put a third party's proceeding next to a boarding pass and permit its filename into a
prompt. The row exists in part to route this class to Protected Records rather than the transactional
residual — and the JSON keeps Receipts and Confirmations as a residual **only** for the fee receipt and
the carrier card, which carry an amount or a tracking number and no caption.

**The decisive argument — leg 1 of the node test, below.**

## The node test, three legs, argued

The schema's **DEFAULT TEMPLATE**, stated so the difference is measurable, is the paragraph in
`law_practice.json`'s `template.why`: recognition requires *both* an exact matter reference repeated
across two or more artefacts *and* at least one artefact whose own labelled slots separate a
practitioner or firm role from a client role; the recommended prose order is client (approval-gated) →
matter → document function → period; `time_first` false; residual Protected Records;
`potentially_sensitive`.

**Leg 1 — detection signals differ. This is the leg the row wins on, and it is not a matter of degree.**
The default's second precondition is a practitioner/client role pair. **A notice of electronic filing
has no client role in it at all.** Nor does a docket extract, a stamp band, a rejection notice or a
carrier return receipt. The default template would refuse to fire on the entire artefact class. The
positive replacement I author is a two-legged structure of its own: (i) a moment asserted in a labelled
slot by an issuer who is *neither the holder nor the client* — a court e-filing system, a clerk, a
process server, a carrier; and (ii) a destination set — an accepting registry, or an enumerated
recipient list each paired with a method of delivery. Both legs required; a moment alone is a
timestamp, a destination alone is a distribution list. I state this positively on purpose: a row
defined by the *absence* of the role pair would be a row defined by absence, which is a refusal
category in this project, so the row is defined by the presence of a third-party authority instead.

The supporting signals are structural too, not lexical: the **stamp-zone overlay** is a positional and
layered observation (a band applied on top of the original layout, clipping text, repeated at identical
coordinates on every page) rather than a vocabulary one; the **docket** is a repeating dated row
register; the **proof of service** is a recipient × address × method × moment table. None of them is a
filename test, and the JSON strikes the words FILED, LODGED, SERVED, RECEIVED, ENTERED and CONFORMED as
never-alone in the first `never_alone` entry, precisely so the row cannot degrade into one.

**Leg 2 — the dimension recommendation differs, in a way that survives PR-6 lifting.** Both orders are
empty by contract, so the difference lives in the prose (argued in full in the JSON's `template.why`),
in three places. (a) **The function level does not branch here** — every member has the same function,
it is a receipt, so a function level is 00's meaningless one-child level. The axis that varies is the
*filing event*, which is not a category but a pointer at another document; so the default's third level
inverts, and a filing record becomes a **leaf beside the document it evidences**, on 00's own argument
that a work type is *"meaningful only after the course is known"*. The named anti-pattern is a
corpus-wide `Filings/` folder. (b) **The client level is more strongly ineligible than in the default**,
because here the most salient token *is* a third party: a caption is `X v Y` and a service list is a
column of home addresses. (c) **Not time-first, for a row-specific reason** — one filing event carries
five distinct moments (submission, entered, stamped, served, filesystem), and branching on one silently
asserts which is operative. These are the most event-like artefacts in the schema, which makes
time-first the most tempting available error, so it is refused explicitly.

**Leg 3 — the privacy rule differs, on *whose* data rather than on class.** The class is the same
(`potentially_sensitive`; P7 owns handling). The subject is not. The schema's stated privacy claim is
that it protects a *third party — a client, an adverse party, a witness*. A proof of service protects
people one step further out: an occupant who answered a door, a co-resident who accepted substituted
service. They are third parties *to the third party*, with no relationship to the holder or the client,
and they appear here in a structured address list — bulk-sensitive as a whole even though each row is
short. Two further row-specific rules: a filing notice can be **more disclosive than the document it
points at** when the document is sealed; and this row is the corpus's strongest invitation to the
struck inference that public availability makes a local copy safe.

Three legs, three differences. The row passes.

## Files considered and rejected

Named because a row that only lists what it holds has not been researched.

- **The pleading, motion or brief itself, unstamped.** Tempting because it is the thing that gets filed.
  Rejected: its evidence is its own body — caption, numbered allegations, prayer for relief — and that
  is `law_practice.pleadings` / `law_practice.motions-and-briefs`. Nothing in it records a transmission.
- **A hearing or limitation diary.** Tempting because service dates drive response dates. Rejected: the
  schema's diary signal is a *portfolio table over many matters* with an owning-practitioner column;
  mine is a per-event receipt for one matter. Same reason kills the `.ics` for a hearing generated from
  a filing notice — an event is a date, not a transmission — which is why `calendar` is deliberately
  absent from `file_kinds.source_types`.
- **An email between practitioner and client attaching a stamped copy.** Rejected: labelled roles
  crossing the practitioner-client boundary is `law_practice.matter-correspondence`'s signal. The
  attachment may be mine; the message is not.
- **A discovery production load file or control-number manifest.** Genuinely close — a transmission to
  the other side with a bounded identifier range. Rejected as *primary* evidence because its structure
  is a review-and-coding apparatus `law_practice.discovery` owns end to end; recorded as
  `also_holds_with`, since a certificate of service for a production set is legitimately both.
- **A bank or client-account reconciliation.** Rejected on the anchor's own concession: an
  institution-and-account header is finance's discriminating structure.
- **A regulatory registry receipt or a tax e-file acknowledgement.** Same transmission shape, no court
  in either. Left to `law_practice.regulatory-submission`,
  `business_operations.corporate-regulatory-filings` and `finance.tax-filings`, and flagged in NJ-CFR-2
  rather than annexed — noted so a future author does not reason from shape alone.

## The collision fixtures

**Primary: `Order - Hartley v Nash - entered 2026-08-19.pdf`.** It satisfies every signal this row
accepts: an authority-asserted moment, an entry number, a registry stamp band in the same style as the
conformed complaint, and arrival as an attachment to a notice of electronic filing. It is not this
row's evidence. **The discriminator is what the document is about:** this row's artefacts record a
*transmission* — what moved, when, to whom, by what method; an order records a *decision*, and its
operative paragraphs and judicial signature block have no counterpart in any receipt. A stamp band is a
layer; the body underneath decides ownership. `law_practice.orders-and-judgments` holds it, the
covering notice stays here, and `legal` protects both first.

**Second: `Scan_2026-08-14_1603.pdf`.** A dated RECEIVED band across page one — and the issuer inside
the band is the holder's *own firm's* mailroom. A scanner header and a fax banner produce the same
shape. This is the cheapest available mistake in the row, and the discriminator is that the band's
issuer must be a *receiving authority external to the representation*, which is exactly the first leg
of the row's precondition. Underneath, the document is an unsigned draft with bracketed placeholders —
the schema's precedent-bank inverse signal — so nothing fires at all and it routes to Review Later:
*"Review Later may hold files whose meaning is partly understood but whose final location requires a
future decision."*

**Third (under-firing): `Summons and proof of service - my apartment.pdf`.** A complete, correct
transmission structure in which the holder is the person served, in their own life.
`legal.personal-legal-matters` owns it.

## Reciprocal boundaries — both directions, same fixture named on both sides

No neighbour has landed a boundary against me, so each of these is a recommendation to R1c for the
other half.

- **`law_practice.pleadings`** — fixture `Complaint - Hartley v Nash - CONFORMED.pdf`. *Toward me:* the
  stamp-zone overlay only — a band applied over the original layout with an external registry issuer.
  *Toward pleadings:* the caption, the numbered allegations, the prayer for relief, the counsel block,
  and the unstamped draft beside it. Where the two compete on one file, **pleadings wins the document
  and I win the layer**; a filename suffix decides nothing.
- **`law_practice.orders-and-judgments`** — fixture `Order - Hartley v Nash - entered.pdf`. *Toward me:*
  the covering notice of electronic filing and any proof of service of the order. *Toward orders:* the
  order itself, on operative paragraphs plus a judicial signature. Neither may claim the other from the
  shared entry number.
- **`law_practice.deadlines-diary`** — fixture `Affidavit of Service - Nash.pdf`. *Toward me:* the
  service event and its per-recipient method and moment. *Toward the diary:* any portfolio table over
  many matters carrying a key-date column and an owning fee-earner. I compute no deadline from a
  service date and assert no consequence.
- **`law_practice.matter-correspondence`** — fixture `Notice of Electronic Filing - Motion to
  Compel.eml`. *Toward me:* machine-generated notices from a court system or filing provider, whose
  recipient block is a *partition by service method*. *Toward correspondence:* human mail whose labelled
  roles cross the practitioner-client or counsel boundary. Being an `.eml` decides nothing.
- **`legal.personal-legal-matters`** — fixture `Summons and proof of service - my apartment.pdf`.
  *Toward me:* practitioner-side apparatus around the receipt — a filer account, a matter reference
  allocated by the holder's own firm, adjacent work product. *Toward personal:* the holder named in the
  served slot with none of that apparatus present.
- **`finance.receipts-expenses`** — fixture `Filing fee receipt - envelope 4471902.pdf`. *Toward me:*
  the envelope-and-case binding placing the payment inside a filing event. *Toward finance:* the issuer,
  amount, payment method and confirmation number, which are finance's own discriminating structure and
  which it keeps whether or not I also hold the file. Where the binding is absent I have **no claim at
  all**, and the residual is Receipts and Confirmations, not Protected Records.
- **`legal`** (`also_holds_with`) — fixture `Complaint - CONFORMED.pdf` again. A caption plus an
  execution or seal is `legal`'s own signal, `legal` is one of 00's safety domains — *"Finance,
  identity, medical, and legal material should be implemented first as safety domains"* — and its
  protection runs first. I co-activate and take nothing away.
- **`law_practice.discovery`** (`also_holds_with`) — fixture: a certificate of service for a production
  set. *Toward me:* the service certificate. *Toward discovery:* the review log, the coding decisions,
  the load file and the control-number range. *"A file may validly belong to more than one accepted
  group"*.

**Neighbours considered and deliberately given no edge:** `law_practice.appeals` (a notice of appeal's
*receipt* is mine, its substance the appeal sibling's — the pleadings boundary already states that rule);
`law_practice.evidence-exhibits` and `law_practice.hearing-transcripts` (a bundle index touches me only
through its registry acknowledgement); `law_practice.regulatory-submission` and
`business_operations.corporate-regulatory-filings` (NJ-CFR-2); `career.consulting-client-engagement`
(the anchor's consulting seam does not reach receipts); `photos.screenshot-captures` (a coactivation on
the screenshot fixture, not a mutex — recorded as `also_schema` there, following the landed launch row).

## Fields

`fields: []` and `proposed_fields: []`, both deliberate. `law_practice` declares no field rows under
PR-6, and a template may reuse only what its schema declares. Four candidates were considered and each
is refused **here** rather than deferred, so that no sibling reads this row as a licence:

- `filing_date` / `service_date` — these are content dates on a document, and the family already has a
  pending `fiscal_period` proposal for content periods; more importantly a single filing event carries
  five moments, so a single date key would have to pick one and thereby assert which is operative.
- `docket_number` / `case_number` — struck as never-alone identifiers by the schema's own recognition.
  An identifier that cannot activate anything should not become a field, and both are respellings of
  the anchor's pending `project` reuse (the anchor explicitly names `docket` as one of the variants
  that may not be minted).
- `court` / `registry` — this is `jurisdiction` under another name, and the anchor records that
  jurisdiction is unavailable as a field or a dimension under the current decision brief.
- `filing_type` / `service_method` — values of `work_type`, which the anchor already asks R1c to
  declare. Minting either would be the respelling the anchor asks R1c to refuse.

The row therefore adds nothing to the schema's six pending proposals and asks for nothing new.

## Residual routing

- **Protected Records** for anything carrying a caption, a party name or a service address with no
  accepted group — the default, on 00's protected-records sentence quoted above.
- **Review Later** for a partly-understood transmission-shaped artefact whose issuer or side is
  unresolved: the mailroom-stamped scan, the rejection notice with nothing around it.
- **Receipts and Confirmations** for the *narrow* case only — a fee receipt or a carrier card carrying
  an amount or a tracking number and **no** caption, party name or address. This is the one residual
  the assignment did not list among `must_consider_residuals`, and it is used deliberately and
  narrowly; the boundary against it is stated in the charge section above.
- No residual is a fact or a permanent destination.

## NEEDS-JOSEPH

- **NJ-CFR-1 — fold-back or keep.** The schema's `work_types` already contains a court-filing-record
  value, so R1c may judge this row a value rather than a node. The alternatives are: (a) keep it on the
  leg-1 argument, that an authority-asserted transmission with no practitioner/client role pair is a
  structure the default template cannot recognise; (b) fold it back into the default and accept that a
  lone notice of electronic filing falls to Receipts and Confirmations beside a boarding pass; (c) fold
  it back *and* add a residual-routing rule to the schema that caption-bearing confirmations go to
  Protected Records. If (b) or (c), this row should be refused outright, not narrowed — a narrower
  filename filter is the outcome the schema itself forbids.
- **NJ-CFR-2 — non-judicial registries.** A corporate registry receipt, an IP office filing receipt and
  a tax e-file acknowledgement have this row's exact structure with no court in them. Either this row
  is *court* filings only (and `law_practice.regulatory-submission`,
  `business_operations.corporate-regulatory-filings` and `finance.tax-filings` each carry their own
  receipt layer, duplicating the reasoning three times), or the row is renamed to the transmission
  concept and takes them. I did not decide this; the JSON stays court-and-tribunal scoped.
- **NJ-CFR-3 — the split seam.** Filing evidence (to a registry) and service evidence (to people) are
  two different transmissions, and only the second carries third-party addresses. They are one row
  because they arrive as one packet under one identifier. If a later pass gives the address-bearing
  half a stricter posture, the split runs along that seam and nowhere else.
- **NJ-CFR-4 — sealed-document notices.** A notice can be more disclosive than the sealed file it names.
  Whether such a notice may be excerpted for local interpretation at all is a P7 and user-policy
  question; this row abstains and records the observation only.

## Self-verification

- `python3 -m json.tool` parses the node file.
- Key set matches the landed siblings and the anchor (including `proposed_context_terms`).
- Every `file_examples.source_type` is in `SOURCE_TYPES`; no file example writes a folder path as a fact.
- Every edge id was taken from `planning/domains/roster.json`; every `falls_through_to` name is from
  00's residual library paragraph.
- Every quoted span was `grep -c`-verified verbatim against `00` before use. No thresholds, no
  handling classes, no confidence scores.
- Files written: only the two assigned. No neighbour, roster, canonical-fields, `check.py`, `src/` or
  SPEC file was touched.

## R1b — collides_with / also_holds_with signal pass

The defect: both edge lists were bare id strings. Under `_CONTRACT.md` and CONNECTION.md §5 an
entry must be `{"domain", "signal"}` (`design_cite` optional), because P6 activation step 3 and the
P8 validator read the `signal` to decide which side a shared evidence item counts toward. A bare
string records that two rows collide but not how to tell them apart, which is the only part the
engine can act on. All 8 entries (6 `collides_with`, 2 `also_holds_with`) now carry a named
fixture on both sides plus the discriminator. No `design_cite` was added anywhere: none of the
eight discriminations turned on a span of `00` that I could grep-verify as being *about* that pair,
and the contract makes the field optional. No new neighbours; no entry removed.

### The eight discriminators, in one line each

- **`law_practice.pleadings`** — the conformed complaint. Two layers, one file: this row takes the
  stamp overlay, the neighbour takes the body, and on conflict the body wins.
- **`law_practice.orders-and-judgments`** — the entered order that arrived by filing notice. Every
  signal here fires and the file is still not this row's: TRANSMISSION versus DECISION, with
  operative paragraphs and a judicial signature having no counterpart in any receipt.
- **`law_practice.deadlines-diary`** — the dated-row table. What one ROW is decides it: an already-
  occurred filing event in one proceeding here, one matter across a portfolio there.
- **`law_practice.matter-correspondence`** — the counsel email carrying a served document. Who
  asserts the moment and destination decides it: a third party to both holder and client, or not.
- **`legal.personal-legal-matters`** — the holder served at their own address. Whose name is in the
  SERVED slot, plus the total absence of practitioner-side apparatus.
- **`finance.receipts-expenses`** — the filing fee receipt. The neighbour's anchor (issuer +
  transaction identifier + total) is fully present; this row's whole claim is the proceeding
  binding, and without it the row concedes outright.
- **`legal`** (also_holds) — same file, caption to `legal` and safety first, overlay to this row.
- **`law_practice.discovery`** (also_holds) — the production transmittal: corpus apparatus to the
  neighbour, transmission layer to this row.

### Nothing was removed — and why I checked each one

I tested every edge against "would these two ever contest ONE evidence item?" rather than "are
these topically near?". All six survived, and four of them survive on a fixture this row's own
`file_examples` already carries (the conformed complaint, the order, the fee receipt, the
holder-served summons), which is the strongest form of the test. The two I scrutinised hardest
were the REFUSED neighbours:

- `law_practice.deadlines-diary` — a refused row holds nothing, so I nearly cut it. Kept, because
  the contest is real at the artefact level: a single-matter key-dates export and a docket extract
  are the same shape on the surface, and the edge's operative effect is to stop a portfolio diary
  being absorbed into a filing-event group. The signal says so explicitly.
- `law_practice.matter-correspondence` — same reasoning; the counsel email with a certificate of
  service attached is a genuinely contested single item.

### Cross-row recommendations for R1c (I edited no neighbour)

- **`law_practice.orders-and-judgments` is rostered but not authored.** `grep -c` finds it three
  times in `planning/domains/roster.json`; there is no
  `planning/domains/nodes/law_practice.orders-and-judgments.json`. The edge is therefore valid
  against the roster but currently unreciprocable. When that row is written it should reciprocate
  this edge with the mirror signal (it takes the operative paragraphs and the judicial signature;
  the covering notice of electronic filing stays here), and its own fixture should be the same
  entered order so the pair is anchored on one file from both directions.
- **Reciprocity generally.** `finance.receipts-expenses`, `legal.personal-legal-matters`,
  `legal` and `law_practice.discovery` are all authored rows; R1c should check each carries the
  mirror entry naming the same fixture. The finance pair is the one most worth mirroring, because
  the concession runs strongly one way (no proceeding binding → this row has no claim) and the
  neighbour should record the reciprocal (no amount and no labelled total → not finance's).
- **Kind mismatch on `also_holds_with`.** This row is `kind: "template"`, and its
  `also_holds_with` list mixes a SCHEMA (`legal`) with a TEMPLATE (`law_practice.discovery`).
  CONNECTION.md's edge table constrains `collides_with` to same-kind pairs; whether
  `also_holds_with` carries the same constraint is not something I resolved from the §5 grep, and
  I did not change either entry. Flagging it rather than silently normalising it.
- **No change requested to `law_practice.pleadings`.** It is refused and routes its transmission
  layer here explicitly in its own `one_line`, which is already the reciprocal in prose.
