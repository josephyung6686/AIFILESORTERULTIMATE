# Research memo — `nonprofit.religious-institution`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/nonprofit.religious-institution.json`
Roster row: template on the fieldless `nonprofit` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept, narrowed hard.** The roster hint describes a sector — "running a congregation or religious body
as an organisation — governance, membership and life-event registers, services and programmes, giving,
buildings and safeguarding." Six of those seven nouns are already owned by landed or claimed neighbours,
and if the row kept them it would be an organisation-type label wrapped around other rows' evidence: the
exact never-alone failure its own schema strikes first. The row survives on the seventh noun. What is
left after the cession is the **rite register** — a continuing, entry-numbered series recording baptisms,
confirmations, marriages, funerals, burials and interments, naming subject, officiant and witnesses, held
on the institution's side across generations — plus the certified extracts issued from it, the liturgical
cycle that schedules the rites, and the minister-to-congregant pastoral record.

The researched `name` and `one_line` state the narrowing explicitly rather than leaving the hint's scope
implied, because the hint's scope is the thing that would have made this row indefensible.

## Sources used

`RESEARCH-BRIEF.md`; the stamped assignment; `nonprofit.json` (the schema anchor, read in full — it is the
controlling document and is quoted below wherever this row must differ from it);
`legal.practice-matter-file.research.md` as the one launch-row depth calibration; `roster.json`;
`canonical_fields.json`; and `00-database-agent-product-design.md` reached by targeted `grep -c -F` only.
`grep -rl "religious-institution" planning/domains/nodes/` returned exactly one landed row that had already
argued a boundary against me — `government.archives-recordkeeping.research.md` — which is read and answered
below. Four ids I expected do **not** exist on the roster and are not used: `media.event-coverage`,
`photos.event-photography`, `business_operations.events-conferences`, `personal.family-records`; the
venue-side row is `retail_hospitality.event-production` and the facilities row is
`business_operations.facilities-workplace`.

## THE CHARGE — the strongest case that this row should not exist

Stated at full strength before it is answered, because on the hint as written the charge nearly wins.

**1. It is an organisation name — never-alone evidence.** "Religious institution" names a *kind of body*,
not a relation between two parties. The schema strikes the token in its own first never-alone clause ("A
charity, union, church, foundation, NGO, club, association or standards-body NAME alone"), grounded by
reading across from 00: "A university name alone should not create a group because Columbia can appear as
an authoring school, course provider, target institution, employer, research venue, or merely a cited
organization." A church name is worse than Columbia, not better — in one corpus it is employer, landlord,
wedding venue, charity, school governor, publisher, cited authority, historical subject, and the place a
photograph was taken.

**2. Every noun in the hint is another row's** — checked against the roster, not asserted.
`nonprofit.governance` holds "the constitutional and board-level record of a nonprofit — governing
document, registration, trustee or board business, policies, annual reporting and regulatory returns";
`nonprofit.member-association` holds membership; `nonprofit.fundraising-donor` holds "appeals and
campaigns, donor and gift records, tax-relief claims, events, and stewardship";
`nonprofit.volunteer-management` holds rotas, checks and training;
`business_operations.facilities-workplace` holds buildings; safeguarding is the schema's own deterministic
structure and is not denominational. Subtract all of them and the hint is an empty set plus an adjective.

**3. It duplicates its own schema's default.** The schema already fires on "A FAITH-INSTITUTION RITE
register: a bound or tabular register with one row per rite carrying an entry number, a date, the names of
the person and of officiant and witnesses, and a rite label"; already groups "one RITE REGISTER as a
continuing series rather than as a set of dated files."; and already lists "faith-institution rite register
and its certificates" as a `work_types` **value** — a value of a field, which the brief says can never be a
node. Fires on it, groups it, enumerates it: a template doing the same three things is a copy.

**4. What remains is a document type and a medium.** "Order of service", "sermon", "certificate", "hymn
sheet" are document types, not situations. A row assembled from them is a file-kind node.

**5. Absence-defined.** It could be read as "the nonprofit records that are *not* grant, fund, donor,
member, volunteer or safeguarding" — a residual dressed as a node.

## Defeating the charge — the node test, all three legs

CONNECTION §2: a template exists only where its **detection signals**, **recommended dimensions**, or
**privacy rules** differ from its schema's default. The row must win at least one leg on its own reasoning.
It wins all three, and legs 2 and 3 are the ones the charge cannot touch.

### Leg 1 — detection signals: partially conceded, and narrowed to what survives

Conceded: the register signal is on the schema, so this row's activation is not a *new* signal for it. What
differs is the **set**. The schema's deterministic list has eleven members; this row's has nine and **drops
seven of the schema's** — no grant lifecycle, no fund partition, no gift declaration, no membership roll, no
beneficiary case, no safeguarding form, no volunteer rota. Where the schema activates broadly and routes,
this row activates on one structure and refuses the rest by name.

It also adds three sub-structures the schema does not decompose, and each carries its own discriminator:

- the **certified-extract** structure — an extract distinguished from a certificate not by content but by
  the *issuance context* around it (a source-register citation plus an issuance log plus a sequential run);
- the **interment** structure — one row per plot carrying a **deceased subject and a living rights-holder
  in the same row**, a two-name shape that appears nowhere else in the nonprofit family;
- the **liturgical cycle** structure — dated occasions bound to a repeating calendar with a rite or
  lectionary column, where the *cycle* supplies the period. The schema has no repeating-calendar signal at
  all; every period it names (grant period, appeal, membership year, financial year) is bounded.

Whether this narrowing is enough to be a template *by itself* is honestly arguable, which is why it is not
relied on alone. It is NJ-RI-1 in the JSON.

### Leg 2 — recommended dimensions: differs in kind, and the charge cannot reach it

This is the leg that defeats the work_type reading. A work_type value cannot change a dimension
recommendation; a template can, and this one must.

The schema's prose recommendation is: the ASSOCIATION where the corpus spans more than one, then the
NON-EXCHANGE COUNTERPARTY OR FUND, then the PERIOD, then the DOCUMENT FUNCTION. Every counterparty it
names — "the grant, the restricted fund, the appeal, the membership class, the case, the register" — is a
**bounded engagement** with a beginning and an end, which is why a period level sits under it sensibly.

A rite register has no such shape. It is an unbounded series: volume 7 continues into volume 8, entries run
without gaps, and the dates inside one bound volume can span forty years. Putting a period level under it
splits a single physical volume across calendar folders and breaks the entry sequence that is the only way
an entry is ever found. So this row recommends INSTITUTION (seeded ineligible) → REGISTER SERIES → VOLUME
or ENTRY RANGE → DOCUMENT FUNCTION, and **deliberately drops the period level the schema recommends**.
That is a different recommendation, not a narrower one.

00 supports the dropping directly: "For document and record domains, project, function, or subject usually
comes before time because putting year first scatters related work across calendar folders." A generational
register is the sharpest instance of that sentence anywhere in this family, so `time_first: false` is not a
default here — it is a finding.

`dimension_order` is nonetheless `[]`, because the schema declares no fields and a dimension may only
branch on a declared field (D1 as narrowed, `_CONTRACT` rules 10 and 15, CONNECTION PR-6). The
recommendation is carried as prose in `template.why`, exactly as the schema and its siblings do.

### Leg 3 — privacy rules: differs from the schema default on three counts

The schema's posture is `potentially_sensitive` and its argument is that the exposed party is "a THIRD
PARTY who is neither the user, an employee, nor a customer, and who frequently disclosed under need, harm
or vulnerability." It also observes that "a congregation register" reveals belief. So the schema has
*noticed* this row's material. It has not written this row's rules, and three differences do real work:

1. **The disclosure is intrinsic, not incidental.** A beneficiary file discloses need because of what it
   *says*. A register entry discloses a named person's religious affiliation merely by **existing** —
   before any content is read, before any model sees it. The filing structure is itself the disclosure.
   No other row in this family produces that as a by-product of being filed.
2. **The exposed parties never transacted with the institution at all.** One marriage entry names two
   spouses, an officiant, two witnesses; one baptism entry names parents and sponsors. The schema's
   third-party argument reaches beneficiaries who came to the association; it does not reach people who are
   merely *mentioned*. A single file here routinely discloses affiliation for a household and three
   generations.
3. **The subjects include minors and the dead.** Neither can consent, and neither is contemplated by the
   schema. Age does not retire the exposure, because an interment entry names a living rights-holder beside
   a deceased subject.

Against that, and recorded rather than smoothed: **this is the family's one protected record whose lawful
purpose includes disclosure.** A person is entitled to an extract about themselves and the institution
issues one. So the rule this row writes is narrower and more precise than "protect it": *detection exists
to protect and to find, never to move or to expose* — the register may be recognised and grouped, and its
subject names may never become paths, prompts, or branch labels. The schema's ban on a named third party as
a folder level is inherited and tightened to cover the officiant, the witnesses, the person interred and
the rights-holder as well as the subject.

00 never mentions religion — I grepped for `religio|belief|protected characteristic|special categ` and got
**zero matches**. The entire privacy argument above is therefore marked **inference** in the JSON, and the
only design support claimed is the general posture, "The default posture must therefore be local-first and
data-minimizing.", plus the corpus sentence, which "can include identity documents, account statements, tax
records, medical information, legal records, credentials, private correspondence, GPS metadata, employment
materials, and educational records" — of which a certified rite extract is squarely an identity document.

### Verdict on the charge

Points 2, 4 and 5 of the charge are **conceded in full and acted on**: the row cedes governance, buildings,
giving, volunteers, membership and safeguarding by name in `collides_with`; it takes no document type as
evidence; and it is defined by a present structure, never by an absence. Point 1 is **answered by
striking the token** — the religious name, the clergy title, the devotional vocabulary and the liturgical
date are all in `never_alone`, and the row activates on none of them. Point 3 is **the live one** and is
answered by legs 2 and 3: a `work_types` value cannot drop a dimension level or rewrite a privacy rule, and
this row does both. It is recorded as NJ-RI-1 so R1c can reverse the call rather than inherit it.

## Files considered and rejected

Named because a row that lists only what it holds has not been researched.

- **`PCC minutes - 12 March 2026.pdf`** (parochial church council / vestry / session minutes). The single
  most tempting false positive: a religious body's own decision record, with clergy in the attendance list
  and a diocesan reference in the footer. It is `business_operations.board-governance`, on the schema's own
  concession that "a trustee board running a governance cycle is structurally identical to a company
  board." Kept as a fixture precisely so the refusal is on the record.
- **`Gift Aid declaration - J Okonkwo - signed.pdf`.** A gift-and-tax declaration naming a place of worship.
  `nonprofit.fundraising-donor`. The religious recipient is the never-alone token; nothing here is a rite.
- **Collection, plate, tithe and offering ledgers.** Same reasoning. Giving is giving.
- **`Order of Service - funeral - 4 November 2026.pdf`.** Rite word, officiant name, date, place of worship
  — and no entry number, no witness slot, no register citation. A produced keepsake; Independent Records.
  Retained as a fixture because it is the shape most likely to be mistaken for register evidence.
- **Sermons, homilies, lectionaries, hymn sheets, prayer books, denominational handbooks.** Authored or
  published works — Reading Inbox, or a writing row if the user is the author. Only purpose separates them
  from institutional records; topic never will.
- **A wedding photograph folder, `Wedding 12 June 2026/`.** A name beside a life-event word is the row's
  most seductive false signal and is almost always a personal life event: `photos.camera-events`.
- **Background-check records and safeguarding concern forms in a religious body.** The `nonprofit` schema's
  own safeguarding structure, and `hr`'s where an employee is named. Not denominational — this row does not
  compete for the family's most protected material on the strength of an adjective.
- **`Faculty application - reordering of the nave.pdf`, quinquennial inspections, fabric reports.**
  `business_operations.facilities-workplace`, with `legal` on the consent as an instrument.
- **Religious-studies papers, theology theses, another body's published history.** `research.reading-library`
  or `academic`. Subject matter is not a situation.
- **A church-management SaaS export (`.csv` of people, giving and attendance).** Rejected as a node: it is a
  *source system* whose members split across member-association, fundraising-donor and this row. Only a
  manifest-bearing bounded export is represented, and only where member paths encode registers.
- **Hall-hire bookings and invoices.** An exchange relation; `retail_hospitality.event-production` and
  `finance`. The schema's non-exchange test excludes them cleanly.

## Collision fixtures

The brief asks for at least one. Two are carried, because the second is the harder.

**Primary — `Marriage Certificate - Priya and Sam - 12 July 2019.pdf`.** It carries an entry number, a
register citation, an officiant, two witnesses, an attestation and a seal. It looks exactly like this row's
evidence and, held by the couple, it is not: it is their own status document and belongs to
`identity.core-documents`. **The bytes are identical in both hands and the register citation is on the page
in both cases.** What discriminates is entirely *around* the file — a source register, an issuance log, a
sequential run of extracts — which means this row must never activate from a certificate alone. That is why
"a single CERTIFICATE addressed to its subject" is a `never_alone` clause rather than a signal.

**Secondary — `Parish register scan 1881-1904 - page 044.jpg`.** A photographed ruled register page: entry
numbers, name columns, an officiant column. Structurally it *is* a register page. It is a family
historian's download from a subscription genealogy service and belongs to `photos.family-archive`, or
Reading Inbox if no family-history purpose is evidenced. Discriminated by a service watermark, a reference
number, and unrelated census siblings in the same folder — never by page structure, which cannot
discriminate. Note also what must not be inferred in the other direction: absent EXIF proves nothing about
origin, which 00 forbids in both directions.

## Reciprocal boundaries

Every entry in `collides_with` is an object naming **the same fixture on both sides**, per the edge-shape
repair. The ten, in short form:

| Neighbour | Same fixture | This row owns | Neighbour owns | Discriminator |
|---|---|---|---|---|
| `identity.core-documents` | the marriage certificate | the register + issued extracts in a run | the subject's own copy | issuance context, not the certificate |
| `business_operations.board-governance` | PCC/vestry minutes | nothing — ceded | the whole file | absence of register structure; religious tokens are never-alone |
| `nonprofit.member-association` | the congregation / electoral roll | only if entry-numbered rites with officiant + witnesses | the roll | a roll is revised in place; a register is only annotated |
| `nonprofit.fundraising-donor` | the Gift Aid declaration | nothing — ceded | gift + tax declaration | a giving record names a donor and an amount and no rite |
| `government.archives-recordkeeping` | the deposited register volume | while operative and institution-held | once accessioned by a record office | accession reference, transfer agreement, closure period |
| `photos.family-archive` | the scanned register page | only inside the institution's own digitisation batch | the genealogist's download | manifest + volume path vs watermark + research siblings |
| `clinical_practice` | pastoral visit notes | no clinician role, no diagnosis, no coding | the moment any clinical structure appears | a presence, not an absence — so reliable; stricter side wins |
| `business_operations.facilities-workplace` | the faculty / consent application | nothing — ceded | building, consents, maintenance | a works programme names a structure and no rite |
| `retail_hospitality.event-production` | the wedding run sheet | the officiant side: notice, entry, extract | the venue side: booking, catering, staffing, invoice | exchange vs non-exchange |
| `legal.estate-planning` | the deed of grant of right of burial | the institution's interment register and plot allocation | the individual's disposition wishes and the deed as an estate asset | allocation across many plots vs one person's intention |

Two need a note on direction. **`government.archives-recordkeeping`** already argued this seam against me
and declined an edge: "a diocesan, union, or charity archive behaves identically to a public one. This is
not a mutex but a **status question**" and "the discriminator is public-body status" (both verified
verbatim in that file). I agree the discriminator is custody, and have authored a **narrower** mutex — on
the deposited-register fixture only, not on archives in general. That is one-way; R1c owes the reciprocal
and should decide whether deposit is a mutex or a co-activation (NJ-RI-3). **`identity.core-documents`** is
likewise authored one-way from here; I did not touch that landed row.

## Neighbours considered that got no edge

**`nonprofit.governance`** — the obvious candidate, deliberately omitted: its territory is ceded via
`business_operations.board-governance`, where the fixture actually lands, and a second edge for the same
concession would record the cession twice and the discriminator zero times.
**`nonprofit.volunteer-management`** — the discriminator lives inside the service-plan fixture (a rota with
no rite column is theirs); once the rite column is the test it is not a same-evidence mutex.
**`hr`** — a religious body's paid staff are `hr`'s outright, with nothing to discriminate.
**`finance`** — fee income for a rite is a payment, and the schema already owns the accounting fork.
**`academic`** — a faith school's records are academic; the trust's religious character does not reach the
school's files and no fixture is shared.
**`creative.music-session`** — a choir recording is a creative artefact and this row claims no audio.

## Fields and dimensions

`fields: []` and `proposed_fields: []`, both deliberate. `role_split: []`, `also_holds_with: []`.

`proposed_fields` is **empty by choice, not by omission.** The two keys a template author would be tempted
to mint here are `rite` and `register_series`, and both are refused: `rite` is a *value* of a work-type
field, which is precisely what the brief says can never be a node or a key of its own, and
`register_series` is a grouping anchor rather than a fact about a file. The role this row genuinely needs —
the person a register entry is *about* — is already proposed on the schema as `subject_of_record`
(borrowed from `clinical_practice`, not minted), and minting a `congregant` or `register_subject` synonym
would be the mint-a-variant failure. **Recommendation to R1c, not an edit:** when `subject_of_record` is
adjudicated, its destination-ineligibility for this family must be recorded as covering *deceased persons
and minors*, and the register's non-transacting third parties (officiant, witnesses, sponsors,
rights-holder) need either the same key or an explicit statement that they are never stored at all. The
schema's NJ-NP-5 asks whether per-schema eligibility differences are even expressible; this row is the
strongest case that they must be.

`role_split` is empty because the schema declares no fields to split and the schema has already authored
the two role pairs this family needs (`sponsor`/`organization`, `organization`/`subject_of_record`).
Duplicating them here would be a second copy of the schema's work.

`also_holds_with` is empty because CONNECTION §5 makes it **schema ↔ schema only** and this row is a
template. The co-activations this row would otherwise author are recorded here for R1c and belong on the
`nonprofit` schema row if wanted: `nonprofit` with `identity` on a certified extract; with `government` on
a deposited register; with `clinical_practice` on a chaplaincy note; with `photos` on a digitisation batch.
The fixtures instead carry these as per-file `also_schema` values, which is how `legal.practice-matter-file`
handles the same constraint.

## Residual routing

Protected Records is named **first**, ahead of the schema's own ordering, because this row's characteristic
isolated file is a register page or certificate that discloses a private person's affiliation. Independent
Records takes the standalone certificate or order of service; Review Later takes the row's defining failure,
which is unresolved **custody**; Reading Inbox takes the sermons, lectionaries and downloaded
transcriptions that make up most of the row's false positives; Unsupported or Encrypted takes
church-management exports and password-protected register backups without forcing them open.

## NEEDS-JOSEPH

1. **NJ-RI-1 — existence.** Answered as a narrow YES on legs 2 and 3 of the node test. If R1c judges the
   rite register to be a `work_types` value on the `nonprofit` schema rather than a template — arguable,
   since the anchor already lists it as one — the correct outcome is **refusal**, and coverage routes to the
   schema's own register signal plus `identity.core-documents` plus `government.archives-recordkeeping`.
   This row would rather be refused than kept to save an id. It notes the anchor's own NJ-NP-4 lists
   `faith-rite-register` among the seven defensible templates, which is consistent with acceptance but is
   not by itself an argument.
2. **NJ-RI-2 — custody vs protection, unresolved tension.** Unresolved-custody files currently route to
   Review Later, but a register page of unknown custody is simultaneously the most disclosive file in the
   row. Alternatives: (a) Review Later as written; (b) Protected Records for anything carrying rite-register
   structure until custody is confirmed, accepting that it becomes harder for the user to find. Stated
   rather than picked.
3. **NJ-RI-3 — the deposit seam.** `government.archives-recordkeeping` recorded diocesan archives as a
   status question and declined an edge; this row authored a one-way mutex on the deposited fixture only.
   R1c owes the reciprocal and must decide: mutex on custody, or co-activation.
4. **NJ-RI-4 — the safety-domain gap, inherited at higher stakes.** 00's four safety domains are named and
   closed — "Finance, identity, medical, and legal material should be implemented first as safety domains,
   meaning the system detects and protects them before any cloud or automated placement decision is
   allowed." A rite register is none of them, yet a certified extract *is* an identity document by 00's own
   corpus sentence, and the register names minors and the dead. This is the anchor's NJ-NP-3 with a sharper
   edge: the substitute mechanism that forces P7 ahead of any model path still has no name.
5. **NJ-RI-5 — the English-and-Christian bias of the deterministic list.** The rite labels, the
   officiant/witness vocabulary and the volume-and-entry convention in `recognition.deterministic` are drawn
   from one tradition's register form. The *structure* generalises; the *labels* do not, and R4 gazetteer
   work is not this row's to do. The row handles it by requiring abstention (a `needs_llm` clause) rather
   than by inventing multilingual term lists it cannot source.

## Self-verification

JSON parses. Every `00` quotation in the JSON returned exactly **1** under `grep -c -F`, as did both
quotations lifted from `government.archives-recordkeeping.research.md`. Every neighbour id in
`collides_with` was confirmed present in `roster.json`; every `facts_legal` key was confirmed canonical,
and the schema's four proposed keys were confirmed *absent* from canonical, consistent with their status.
Every `file_examples.source_type` is in `SOURCE_TYPES`; no file example writes a folder path as a fact. The
`never_alone` clauses are true of the fixtures — the certificate clause of fixture 2, the life-event clause
of fixture 8, the religious-name clause of fixtures 6 and 9. No threshold numbers, no handling classes, no
`is_safety_domain`, no invented quotations. Files written: exactly the two assigned; no neighbour node,
roster, `canonical_fields.json`, `check.py`, `src/` or SPEC file was touched.
