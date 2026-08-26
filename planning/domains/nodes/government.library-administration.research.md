# government.library-administration — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: government`, `launch: placeholder`, `parent_id: null`.
Absorbed legacy id (ROSTER §4): `gov.library-administration` → ROW.
Output: [`government.library-administration.json`](government.library-administration.json).
Salvage: none. Both files are new; nothing pre-existed under this id.
Verdict: **node kept**, `refuse_node: false`, on two of the three node-test legs, argued below.
The third leg (dimensions) **cannot** be won under PR-6 and I say so rather than manufacture it.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief; the six depth requirements
  this memo is audited against.
- `python3 planning/domains/dispatch/make_prompt.py government.library-administration` — the
  stamped assignment: schema `government`, no inherited field keys, must-consider neighbours
  `legal`, `nonprofit`, `business_operations`, must-consider residuals Independent Records and
  Protected Records.
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted `grep -n` only.
  Five spans are quoted in the JSON; all five were re-matched against the file mechanically under
  whitespace and curly-quote normalisation before this memo was written. See the audit at the end.
- `planning/domains/ROSTER.md` §4 — the `gov.*` → `government.*` mapping block, which is how I
  confirmed which siblings exist and which legacy ids were folded rather than kept.
- `planning/domains/roster.json` — every edge endpoint resolved mechanically. All ten
  `collides_with` targets are roster ids; both `also_schema` values (`identity`, `photos`) are
  roster **schema** ids; all four `falls_through_to` names are §7.3 residual names.
- `planning/domains/nodes/government.json` — my schema anchor, read in full as structured data.
  This is the file my node test is measured against.
- `planning/domains/nodes/finance.crypto-assets.research.md` — read as the single depth calibration
  the brief allows. House idiom taken from it: observations split from facts, the refusal fixture,
  the "neighbours considered that did not get an edge" section, `proposed_fields` empty on purpose
  with the temptation parked in `open_question`.
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — checked mechanically against all thirteen
  file examples (13/13 legal).

**Not read, deliberately:** the `.research.md` of the government anchor (its JSON settled every
question my node test needed), and no other row's files. One `grep -rl` over
`planning/domains/nodes/` for `library-administration` returned nothing — **no landed row has yet
argued a boundary against me**, so every boundary below is stated first here and every one of them
is a RECOMMENDATION to R1c for reciprocation, not a claim already agreed.

### External, bottom-up reality checks

These establish that the named structures are real artifacts. They create no canonical field, no
gazetteer entry, no regex, and no threshold.

- **MARC 21 / ISO 2709 and MARCXML.** A bibliographic transfer record is a fixed-width leader, then
  a directory of three-digit numeric field tags with byte offsets, then variable fields separated by
  record and field terminators; MARCXML is the same model as `record` / `leader` / `controlfield` /
  `datafield` elements carrying numeric `tag` attributes and subfield codes. This is the evidence
  behind the BIBLIOGRAPHIC TRANSFER STRUCTURE signal, and it is why that signal names the
  *structure* and not any vendor's column spellings.
- **Integrated library system exports (Koha, Alma, Sierra/Polaris family).** Circulation reporting
  produces per-row records pairing an item barcode, a borrower barcode or name, and a loan-lifecycle
  slot (issue, due, return, renew, hold, reserve, overdue, fine). The lifecycle slot is the
  discriminator against an ordinary stock inventory, which has quantities and no borrower.
- **Item/holdings records.** A shelf classification (a Dewey-shaped decimal or an LC-shaped
  letter-plus-number string) sits beside an item barcode in a holdings record. Neither is usable
  alone, which is why both are `never_alone` lines.
- **Interlending.** A request record names a *requesting library* and a *supplying library* plus a
  request reference and a copyright declaration. The two-library pair is what separates it from a
  citation a researcher saved — this is the sharpest boundary against `research`.
- **Statutory public-library statistical returns.** Services file annual returns on service points,
  opening hours, visits, active borrowers, issues, additions and withdrawals. Real, labelled, and
  the reason SERVICE PERFORMANCE RETURN is written from the **respondent** side.

## THE CHARGE — the strongest case that this row should not exist

I wrote the prosecution first. Six ways this id could be a label rather than a node:

1. **It is an organisation type, i.e. never-alone evidence.** "Library" names a kind of building and
   a kind of body. `00` forbids a template that would "use an author or organization merely as a
   collector", and a row whose only evidence is a service's name in a letterhead can never activate.
2. **It is worse than that: the word is a filesystem trap.** `00` lists `Library` among directories
   the engine must skip — "The engine should ignore node_modules, .git, venv, build, dist, target,
   vendor, Pods, site-packages, Library, __pycache__, build artifacts, caches, auto-save folders,
   previews, and generated dependency trees." On the platform this product targets, the overwhelming
   majority of paths containing the token are application support data. A row keyed on the word
   would fire almost exclusively on excluded machine state.
3. **It is a duplicate of its own schema's default template.** The government anchor's default is
   role-structural: an evidenced public body acting as legislature, regulator, decision-maker,
   programme administrator, records holder, statistical authority, election administrator or
   casework office, with submissions and named-person material protected. A library service is a
   public body administering a public function. If that is all this row says, it is the schema.
4. **It is a duplicate of a neighbour.** Library committee papers are
   `government.municipal-administration`. Library supply frameworks are
   `government.public-procurement`. Library statistical returns are
   `government.statistical-programme`. Withdrawal lists are `government.archives-recordkeeping`.
   Special collections are `government.museum-collection`. Subtract all five and what remains may be
   nothing.
5. **It is a lifecycle stage or a work_type value.** "Cataloguing", "circulation", "weeding",
   "programming" read like stages of one process — values of a `work_type`-shaped field, exactly the
   mistake ALIGNMENT names, not nodes.
6. **It is a subject, not a filing world.** A sector report about libraries is reading material. A
   book is a book. Nothing about the *topic* libraries makes a file filable.

Points 1, 2, 5 and 6 are correct and are now **encoded as refusals inside the node** — they are
`never_alone` lines and a rejected fixture, not hand-waving. Point 4 is correct for exactly the
material it names and is now ten `collides_with` edges that hand that material away. What survives
is points 3's answer, below.

## The node test, argued in full

CONNECTION.md's test: a template exists only where its **detection signals**, **recommended
dimensions**, or **privacy rules** differ from its schema's default. Disjunctive. I take two legs
and concede one.

**Leg 1 — detection signals. DIFFER, and differ in kind.** The government schema's default detector
is *role-structural*: it asks whether an evidenced public body is acting in an authority-side role,
and its own precondition says a public body's name does not fire it. Every deterministic signal on
the anchor is a proceeding shape — a bill identifier across a packet, a rulemaking identifier across
notice and response, a decision record with labelled applicant and reasons slots. **None of those
shapes exists in a catalogue export or a circulation report.** A MARCXML file has no proceeding, no
applicant, no decision, no reasons; it has a leader, numeric field tags and subfield codes. An
overdue report has no docket; it has an item barcode, a borrower barcode, a due date and a lifecycle
column. This row therefore supplies a *content-structural* detector that the schema default cannot
express and would never fire on: the bibliographic transfer structure, the holdings/item slot pair,
and the circulation ledger triple. That is a real difference in the recogniser, not a re-labelling.
It is also the reason this row can activate on files where **no authority role is evidenced at all**
— an unheadered `.mrc` export names no body, and the schema default would abstain on it.

**Leg 2 — privacy rules. DIFFER, and the difference is a new rule, not a stronger dial.** The anchor
already protects named-person casework and submissions, so "there are people's names in it" is not a
difference. The difference is *what the pair discloses*. In casework the sensitive fact is that a
named person has a case; here the sensitive fact is the **link between a named person and a title**
— what someone read. That has two consequences the schema default does not state and could not
derive: (a) a borrower name may not be a display label **and neither may the item**, because a
folder or summary naming the book beside the person discloses the reading even when the person's
identity was already known; (b) the row's bibliographic half is genuinely public-facing (a catalogue
record is published), so this is the unusual government row where *some* of the material is
publishable and mixing it with the circulation half must not launder the posture downward. Both are
written into `sensitivity_why` and into `must_not_conclude` on three fixtures.

**Leg 3 — recommended dimensions. DO NOT DIFFER, and cannot.** PR-6 leaves the government schema
fieldless; a template may only branch on a field its own schema declares; therefore
`dimension_order` is `[]` here exactly as it is on the anchor. I will not claim a difference I
cannot have. What I *can* record without minting anything is the shape the world wants in prose
(function or bounded lifecycle → exact collection/service point/programme/cycle → document
function) plus two affirmative exclusions that survive whatever R1c decides: **a borrower is never a
dimension** and **a title or shelf classification is never a dimension**. `time_first: false`,
because "For document and record domains, project, function, or subject usually comes before time
because putting year first scatters related work across calendar folders."

Two of three legs is a pass. Nothing was invented to reach it: `fields: []`, `proposed_fields: []`,
no new dimension, no new residual, and the one place a key was genuinely tempting is parked in
`open_question` instead.

## Files considered and REJECTED — the tempting false positives

A row that only lists what it holds has not been researched. These were all candidates and all were
thrown out, each for a stated reason:

- **`~/Library/Application Support/<vendor>/cache.db`** — the strongest false positive on the whole
  row and the one that would have made it worthless. The path token matches the row's name exactly.
  It is not evidence, it is excluded machine state under the `00` exclusion quote above. This is
  `never_alone` line one, and it is the reason the row is keyed on record structure and never on
  the word.
- **`The Future of Public Libraries - sector report.pdf`** — kept, but kept as the **collision
  fixture** (see below), not as holdings. Its correct home is a residual.
- **A downloaded catalogue record / `.ris` or `.bib` export a researcher pulled from a library
  catalogue** — byte-structurally the closest thing to my strongest signal, and the reason
  BIBLIOGRAPHIC TRANSFER STRUCTURE carries an explicit role precondition. Rejected: the corpus
  holder is reading, not running stock. It is `research`'s evidence, and I state the boundary
  reciprocally below.
- **An e-book or PDF of a borrowed title** — the content of the collection is not the record of the
  collection. Admitting it would have made this a reading-material row by the back door.
- **A library card in a wallet, or a "your item is due" notice a borrower received** — the
  *patron-side* artifact. It is the person's record, not the service's. This is the role split I
  wanted and could not encode (see `role_split`, below).
- **A staff payslip, rota or HR file from a library service** — `hr`'s world. Employment records do
  not become library records by being produced in a library.
- **A library-management-system software tender and its contract** — `government.public-procurement`
  entirely. The subject of a procurement is not the procurement's domain.
- **A local-studies photograph scan** — an image of a place. Without an accession register entry it
  is a picture, and with one it is the museum sibling's contested case, recorded as an open question
  rather than annexed.
- **A `.zip` of a website archive of the service's public catalogue** — bulk machine state; `00`
  routes that kind of material to metadata-only handling and it teaches this row nothing.

## The collision fixture

**`The Future of Public Libraries - sector report.pdf`.** It is *about* libraries; its cover names a
sector body; its subject vocabulary is denser in library terms than any real service record; and a
naive detector keyed on topic fires hardest on exactly this file. It is **not** this row's evidence.

What discriminates it: it carries **no service reference, no item identifiers, no borrower slots and
no return cycle** — none of the three structures this row requires. Its structure is an argued
report with endnotes, which is reading material. It routes to **Reading Inbox** — "Reading Inbox may
hold papers, articles, reports, and saved PDFs that appear to be reading material but have no active
research, course, or project association." The fixture is in `file_examples` with
`falls_through_if_inactive: "Reading Inbox"` and a `must_not_conclude` line saying the subject is
libraries and the evidence is reading material.

A second, harder collision is carried separately because it is intra-schema:
**`Libraries and Culture Committee - Agenda Pack - 12 May 2026.pdf`** — produced by the same
authority, about the library service, containing a branch closure appraisal. It belongs to
`government.municipal-administration`, and the discriminator is the governance cycle structure
(numbered items, officer reports, resolutions) versus operational structure.

## Reciprocal boundaries — both directions, same fixture on both sides

Each of these is a RECOMMENDATION to R1c. None is yet reciprocated by a landed row.

| Neighbour | Shared fixture | Mine when | Theirs when |
|---|---|---|---|
| `government.municipal-administration` | `Libraries and Culture Committee - Agenda Pack - 12 May 2026.pdf` | operational service structure — stock, item, borrower, programme, performance slots | governance-cycle structure — agenda items, officer reports, minutes, resolutions, whatever the subject |
| `government.statistical-programme` | `Annual return - public library statistics 2025-26.xlsx` | the corpus holder is the **respondent** filing about its own service | the corpus holder is the **collecting authority** running the instruction, instrument, microdata and release |
| `government.archives-recordkeeping` | `Weeding list - withdrawn stock 2026-Q2.csv` | item barcodes with stock-condition or low-issue reasons | a retention/disposal schedule reference and a records series |
| `government.museum-collection` | an accession/deaccession list held by a library service | circulating-stock structure: copies, barcodes, shelf classification, loan lifecycle | an accession register entry with provenance and object description |
| `government.public-procurement` | `Stock selection meeting - approvals - August 2026.docx` | title-level selection against a fund, on the shelf-owning side | notice, specification, received bid, evaluation, award — including the LMS tender |
| `government.public-consultation` | `Library strategy consultation - responses export.zip` | the service's operational contribution (service-point data, hours schedules) | the response corpus grouped by a shared consultation identifier |
| `government.education-institution-governance` | a university library's catalogue export and circulation report | the holder is a standalone statutory public library service | the holder is the institution, and its library is one of its functions |
| `business_operations` | a barcoded stock take with supplier invoices | a public library service exercising a public function | a bookshop, publisher, or company knowledge centre — commercial holder, however book-shaped |
| `nonprofit` | a reading-campaign programme plan with an attendance register and a funder report | the statutory service running the programme | a charity or community-managed library accounting to its board and funders |
| `legal` | a copyright declaration on an interlending form; a request for borrowing history | the operational form the declaration sits on | the executed agreement, or the person's legal record — and a disclosure demand is legal's document while remaining my protected data |
| `research` *(no edge — see below)* | a bibliographic export | requesting/supplying library pair, or a service-side load report | a citation saved into a reference-manager workflow |

## Neighbours considered that did NOT get an edge

- **`research`** — genuinely close (bibliographic exports, ILL requests as research inputs) and
  deliberately left edgeless. The discriminating evidence never actually collides once the ILL
  two-library pair and the reference-manager workflow are the tests, and the boundary is already
  carried as a `needs_llm` line plus a `must_not_conclude` on the interlending fixture. Adding an
  eleventh collision would have given one evidence item a third claimant. Stated in the table above
  so R1c can promote it if `research` disagrees.
- **`government.school-district-administration`** — a school library sits under it, not beside it.
  Adding an edge would duplicate the education-institution-governance boundary with a different id.
- **`government.public-records-foi`** — an FOI request *about* library closures is FOI's, decided by
  FOI's own request/search/disclosure structure. No shared discriminating evidence with mine.
- **`identity` as `also_holds_with`** — rejected at the schema level. The contract restricts
  `also_holds_with` to schema rows, and the government anchor's own list is empty; a template must
  not widen its schema's edges. The membership application's identity dimension is expressed where
  it belongs, as `also_schema: "identity"` on the fixture, alongside a `must_not_conclude` saying
  the proof-of-address evidence is a slot on someone else's form and not an identity document.
  `also_holds_with` is therefore `[]` **by contract**, not by oversight.
- **`role_split` — empty, and this is the interesting refusal.** The split this world most obviously
  wants is *the service that lent an item* against *the borrower who holds the same loan*, which is
  a real same-entity/different-role pair: an overdue notice exists in both corpora. `role_split`
  requires naming the **different field keys** each side carries. Under PR-6 the government schema
  declares none, so there is no key to split against, and minting one to solve a single template's
  problem is precisely the move the overnight pass was censured for. Recorded here and in
  `open_question`, not encoded.

## Field decisions and `proposed_fields`

**`proposed_fields` is empty, deliberately.** `fields` is empty because the government schema
declares none under PR-6 and D1's deferral stands. The legal set on any file this row recognises is
the universals only — file type, creation date, language, duplicate family, version family,
sensitivity status — which is exactly what every `facts_legal` list in the JSON contains.

The two strings this material is saturated with are deliberately **not** proposed as keys:

- **an item / bibliographic identifier.** Tempting, labelled, stable, and exactly the wrong thing to
  mint, because minting it immediately raises whether it may become a folder level. The answer here
  is no: a directory named for a title, beside a borrower list, publishes what someone read on the
  filesystem.
- **a borrower identifier.** It is the protected half of the disclosure pair. Proposing it as a key
  would be proposing to write the sensitive fact.

`proposed_context_terms` carries ten candidates for R6, marked PROPOSED and explicitly not design;
`00` lists none of them and the entry says so. Each is proposed only as a term that must co-occur
with a labelled slot structure.

## Sparse-file discipline

Two fixtures carry `group_without_copying_facts: true`. `Class visit - Year 4 - Tuesday.ics` is the
`HW 3.pdf` of this node: a bare calendar event whose only suggestion of a domain is the programme
plan sitting next to it, so it joins the neighbourhood and receives nothing — "An isolated file
should normally remain high in the tree because there is no evidence that it deserves a deep
project-specific path" is the posture. `Library strategy consultation - responses export.zip` is the
archive case: the manifest is read without unpacking, its members are content-incoherent, and the
shared identifier that binds them belongs to a sibling, so nothing is copied onto the members.
`Screenshot ... fulfilment queue.png` carries the media-type discipline line: missing capture
metadata is not proof of a screenshot, and the borrower-to-title pairs visible in OCR are not facts.

## Audits run before returning

- `python3 -m json.tool` — parses.
- All five curly-quoted spans in the JSON were extracted mechanically and matched against
  `planning/00-database-agent-product-design.md` under whitespace/curly-quote normalisation.
  **5/5 VERBATIM.** All four `falls_through_to.design_cite` values likewise: **4/4 VERBATIM.**
  No `00` quotation in this node is fabricated or paraphrased inside quote marks.
- Every `file_examples.source_type` is in `SOURCE_TYPES` (13/13).
- Every `collides_with.domain` is a roster id (10/10, resolved against `roster.json`); every
  `also_schema` is a roster schema id (2/2); every `falls_through_to.residual_template` is one of
  §7.3's nine names (4/4).
- `fields`, `proposed_fields`, `also_holds_with`, `role_split` and `template.dimension_order` are all
  empty, each with a stated reason in the JSON or this memo.
- No number in either file is a threshold, a score, or a count of evidence; the digits present are
  filenames, years inside fixture names, and prose references.
- No handling class assigned; `sensitivity` is `potentially_sensitive` only.
- Only the two assigned files were written. `planning/29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `check.py`, `src/` and every neighbour node are untouched.

## NEEDS-JOSEPH (this node only)

- **NJ-LIB-1 — the two facts this world is made of are unproposable under PR-6.** An item /
  bibliographic identifier and a borrower identifier are the row's whole vocabulary and neither was
  proposed. Three answers, three different products: (a) stay fieldless, which is what the row does
  today and what keeps it safe; (b) adjudicate an item-side identifier centrally as
  search-only and never destination-eligible, which makes stock lifecycles groupable without
  publishing titles; (c) adjudicate both, which requires deciding in the same breath that a borrower
  may never be a level — a decision about the shared field table that one template must not make.
  **Recorded, not resolved. No field was proposed.**
- **NJ-LIB-2 — is this row holder-scoped to statutory public services, or a cross-schema
  situation?** Academic, corporate and charity-run libraries emit byte-identical catalogue and
  circulation records. The row currently reads as holder-scoped to public services and collides the
  others out to `government.education-institution-governance`, `business_operations` and
  `nonprofit`. The alternative is that library administration is a *situation* several schemas share
  and government merely hosts the row — in which case three of my ten collisions should be
  re-expressed. Roster placement alone does not settle it.
- **NJ-LIB-3 — who owns a rare-books or local-studies collection held inside a library service?**
  Candidates: this row (it is on the service's shelves), `government.museum-collection` (it has an
  accession register and provenance), `government.archives-recordkeeping` (it is a records series
  under a retention schedule). The three sibling detectors will all half-fire on the same
  accession-and-condition list. I state a preference — follow the register structure, not the
  building — but the row does not have the standing to bind two siblings to it.
- **NJ-LIB-4 — the lender/borrower `role_split` has no key to split against.** The same overdue
  notice exists in the service's corpus and the person's. Until the government schema declares a
  field, `role_split` must stay empty here; if PR-6 lifts, this pair is the first one worth encoding.
