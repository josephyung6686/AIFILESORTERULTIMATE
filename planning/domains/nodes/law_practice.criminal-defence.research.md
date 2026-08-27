# Research memo — `law_practice.criminal-defence`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.criminal-defence.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accepted, narrowly, on leg three only.** The row does not survive because it holds criminal-shaped
documents — every one of those is already a `work_type` value on the anchor. It survives because it
carries three privacy rules the `law_practice` default template does not state, and one detection
structure the default cannot see. `fields: []`, `proposed_fields: []`, `dimension_order: []`,
`also_holds_with: []`, six `collides_with` entries, five residual homes.

The anchor pre-authorised exactly this and nothing more:

> "a practice-area row survives only if it changes the privacy rule, never
> because it changes the topic. Three plausibly do — `family-law`, `criminal-defence` and
> `immigration-casework`, where the *existence* of the file is disclosive about a child, an accused or
> an immigration status. Those three must argue **leg 3** explicitly and must not argue leg 1 or a
> document list."
> — `law_practice.research.md`

I argue leg 3 explicitly. I do not argue leg 1 as a stand, and I write no document list as a reason.

## THE CHARGE — the strongest case that this row should not exist

I built each of these as the best available prosecution of my own row before defending it.

**1. It is a `work_type` value, and the schema said so in its own vocabulary.** The anchor declares 24
work types. Read against a real criminal file, they already cover it end to end: *"investigation and
interview record conducted for a client"*, *"witness statement, proof of evidence and deposition or
hearing transcript"*, *"disclosure or discovery request, response, review log and production set"*,
*"evidence, exhibit and bundle index"*, *"pleading, application, submission and written case"*,
*"order, judgment, award and appeal record"*, *"settlement, mediation and negotiated-outcome record"*,
*"file closure, undertakings discharge, papers-returned, retention and transfer record"*. Nothing in
my world is unenumerated. The schema declared `work_types` precisely so document kinds do not become
rows, and "criminal defence" is a value of practice area in exactly the way `clinical_practice` ruled
specialties to be.

**2. It is a document-type row wearing a practice-area coat.** Charge sheet, indictment, custody
record, bail sheet, unused-material schedule, pre-sentence report. If I am kept because I hold those,
the row is a file-kind node and the 574's failure repeats.

**3. It is never-alone evidence all the way down.** Every token I would reach for is struck by the
schema's own deletion test: an `R v` caption, an offence name, a statutory section, a police force, a
prosecuting authority, a court, a custody reference, a firm letterhead, two surnames. Delete every
entity name and every document-type word and — on most of my fixtures — nothing structural survives.
That is a genuine finding, not a rhetorical one: it is why the row's recognition block leads with the
schema precondition rather than with anything of its own.

**4. It duplicates its own siblings on the document-function axis.** `law_practice.pleadings`,
`law_practice.discovery`, `law_practice.evidence-exhibits`, `law_practice.hearing-transcripts`,
`law_practice.court-filing-record` and `law_practice.appeals` already hold, respectively, my charging
document, my disclosure schedules, my exhibit bundle, my trial transcript, my filings and my appeal.
Subtract them and it is not obvious what is left.

**5. It duplicates the schema default.** Same matter-anchored two-role precondition, same one-matter
grouping, same empty dimension order, same `potentially_sensitive`, same Protected Records fallback.

**6. The 36-row problem, stated by `family-law` against me by name.** *"If family-law exists because
it holds disclosure forms, criminal-defence exists because it holds a charge sheet and conveyancing
because it holds a transfer. 36 rows, one default template."*

## Why the charge does not defeat the row

Charges 1, 2, 3, 4 and 6 all attack the same claim — that I hold distinctive *content*. I concede
that claim entirely. The row is not kept for its content. Charge 5 is the only one that matters, and
it is the one I defeat, with three privacy rules and one structure.

### Leg 3 — privacy. The rules the default does not state.

**Rule A — a served, use-restricted bundle about people who are not the subject of the file.** The
anchor's posture protects *"a THIRD PARTY's - a client, an adverse party, a witness, a deponent, an
accused, a child - who never chose this filesystem and cannot consent."* Note that it names "an
accused" — so the mere presence of an accused is *not* my difference, and I do not claim it. My
difference is a category of holding the default does not describe: material the practice possesses
**only because the accusing side served it**, about a complainant, a witness, a co-accused or a person
never charged, held for these proceedings and no other purpose. 00's corpus sentence describes the
pile precisely — a real collection *"can include identity documents, account statements, tax records,
medical information, legal records, credentials, private correspondence, GPS metadata, employment
materials, and educational records"* — and here every one of those items may be about a person who is
neither the holder nor the client.

The operational consequences are new and are not restatements of the default: this material may never
be copied for convenience, never de-duplicated or version-merged against an identical schedule sitting
in another matter, never synced; and the **served copy and the holder's own working copy of the same
document are not duplicates**. `family-law` reached a superficially similar rule (a redacted service
copy and its original are not duplicates) for a different reason and about different bytes — see the
NJ-FL-2 answer below.

**Rule B — self-incriminating client work product, which constrains *recognition*, not only display.**
A proof of evidence or an advice-on-plea attendance note records what a living person says happened,
in the first person, in a matter about their liberty. The schema's default permits recognition on a
minimum-necessary excerpt. This row does not. On those artefacts the product reads heading blocks,
section labels and reference lines and **never the narrative body** — no embedding, no summary, no
preview line, no group label, no snippet, no remote prompt, at any confidence. That is a change to how
the classifier is allowed to *look*, which is the strongest kind of leg-3 difference available, and it
is the operational form of 00's *"The default posture must therefore be local-first and
data-minimizing."*

**Rule C — sensitivity rises at closure instead of decaying.** Everywhere else in this family a closed
matter cools and becomes archivable. Here the outcome record — a discontinuance, an acquittal, a
caution, a disposal that may later be spent or expunged — is the single most disclosive artefact in the
matter and it arrives **last**. Every ordinary old-files-are-cold heuristic inverts for this row: the
2019 encrypted crown court archive is high-risk *because* it is old. No sibling states this, and it
binds archival, cold-storage, summarisation and preview behaviour rather than folder labels. Inference,
marked as such; it is the rule I would most like R1c to stress-test.

**And the filing rule that follows, which differs from the default at two levels rather than one.**
The default recommends: client (only where the corpus spans more than one *and* the user approves),
then matter, then function, then period. Like `family-law` I make the client level ineligible outright
rather than unlockable — but for a different reason, and I say so rather than borrowing theirs. My
addition is at the **function** level, and no other template in the family says it: suppressing the
client name and opacifying the matter reference is not sufficient here, because `mitigation`, `basis of
plea`, `previous convictions`, `pre-sentence report` and `fitness to plead` each publish the accusation
or the client's mental health *from the branch label alone, with no name anywhere in the path*. Not
time-first, on the design's own reasoning: *"For document and record domains, project, function, or
subject usually comes before time because putting year first scatters related work across calendar
folders."*

### Leg 1 — detection. Supplementary, and I do not stand on it.

One structure the default genuinely cannot see, and it is an *inversion* rather than an addition. The
schema's disclosure-review signal is a coding log **the holder authored** — the holder's reviewer, the
holder's decisions, produced to disclose outward. My structure is the same table received from the
other direction: one row per item, a per-item disclosability decision, and an **author-role slot naming
an officer of the opposing side**, with a service endorsement, arriving as a *pair* (served / unused)
and answered by the holder's own further-disclosure request. The holder cannot alter a row of it. That
is a photographic negative of the schema's own signal, in the same way the anchor's precedent-bank
signal is the negative of `legal`'s instrument signal. Second structure, weaker: a detained-person
record — a timed log with rights-advisement, adviser, appropriate-adult and disposition slots, carrying
a custody reference *distinct from* the matter reference, which is what allows an episode to be
recognised before a matter reference exists at all.

### Leg 2 — grouping. Mostly inherited; one group is genuinely new.

Charge-to-outcome and service-event groups are the schema default with different names. The new one is
**one third-party subject**, and it is the only group in the family whose purpose is *exclusion rather
than retrieval*: material about one named person who is not the client, gathered so it can be walled
off from previews, summaries, duplicate scans and prompts. Its label must not name the person. Bounded
by exact references only — *"It should not form a supported group when there is no valid anchor"* — and
cross-matter similarity is **suppressed** here, not merely deprioritised, because two matters sharing a
complainant, a set of facts or a co-accused are emphatically not one group.

## Files considered and rejected

- **A published criminal judgment** (`R v Hale - Court of Appeal judgment - 2024.pdf`). Densest
  concentration of my struck tokens in existence. No matter reference, no role pair, no service
  endorsement. Reading Inbox. This fixture is in the node specifically to prove that criminal
  vocabulary at any density is not an activation signal.
- **Sentencing guidelines, practitioner texts, precedent copies.** Same reason. The anchor's
  precedent-bank signal already owns unexecuted firm templates; public texts are reading.
- **A court listing or portal screenshot.** Positive screen-origin evidence activates photos on its own
  evidence; an OCR'd proceeding reference is the weakest possible anchor for a group whose members
  carry a use restriction. Temporary Screenshots.
- **A police report or crime report the holder obtained as a victim.** That is the holder's own record
  and belongs to `legal.personal-legal-matters`; no apparatus, no client role.
- **A criminal-records check or DBS-type certificate.** Identity's and `career`'s evidence about the
  holder, not a matter file. It carries an offence-shaped vocabulary and no matter anchor.
- **A firm's crime-team practising certificate, accreditation or duty-scheme roster.** The
  `law_practice.admission-cle` refusal already routed this correctly, and its reasoning applies
  verbatim: disclosive about a lawyer being a lawyer, which their own letterhead publishes.
- **A case-management system export.** A source system, not a file node. A bounded export with a
  readable manifest is representable; live ingestion is a connector decision.
- **Time entries and bills on a criminal matter.** `law_practice.time-and-billing` owns the column-set
  structure and this row does not compete for it; the matter-reference column is that row's evidence.
- **The charge sheet, the indictment, the trial transcript, the appeal notice.** Deliberately *not*
  claimed as this row's distinguishing evidence, because claiming them is charge 2 and charge 4.

## The collision fixture

`Interview transcript - 2026-03-04 - Rowan Pike.pdf`. A dated question-and-answer record of one person
being questioned, on a practice template, with a matter reference in the footer. It is my evidence, or
`law_practice.investigation`'s, or `hr.employee-relations`'s, and nothing on the filename decides.

What discriminates it is the **role trio on the opening block**: a caution or rights-advisement block
plus an attending-legal-adviser slot plus a custody or booking reference is this row; an
investigator-and-subject pair with an investigation instruction or engagement reference is
`law_practice.investigation`; an employee, manager and HR-representative trio with a disciplinary-policy
reference is `hr.employee-relations`. The seam is the **direction of questioning**, read off role slots
— who is asking and on whose behalf — never the word *interview*, never the offence vocabulary, and
never which profession the holder practises. Where the trio does not resolve, the file goes to Review
Later; the second collision fixture (the judgment) goes to Reading Inbox.

## Reciprocal boundaries

Six, each stated in both directions and naming the same fixture on both sides; full text in the node's
`collides_with`.

| Neighbour | Same fixture both sides | Discriminating evidence |
|---|---|---|
| `legal.personal-legal-matters` | `Bail conditions and PTPH listing - 41127-0011.ics` + covering letter | Where the apparatus is: the practice allocated the reference, wrote the attendance notes, received the served bundle — vs. the holder simply being the accused |
| `law_practice.discovery` | `Unused material schedule - served 2026-05-12 - 41127-0011.pdf` | Whose officer owns the decision column: the holder's reviewer (outward) vs. a foreign officer's, served inward, unalterable |
| `law_practice.family-law` | `Non-molestation order and statement of complainant - withheld address.pdf` | Charge/count structure + accused-role slot + custody or bail record — the client is the person the address is withheld *from* |
| `law_practice.investigation` | `Interview transcript - 2026-03-04 - Rowan Pike.pdf` | Direction of questioning: practice as questioner (instruction reference) vs. practice as adviser (caution block + adviser slot + custody reference) |
| `medical.personal-health-records` | `Psychiatric report - fitness to plead - re client - 41127-0011.pdf` | Instructing-party and court-addressee slots. Medical is a safety domain, its protection runs first, co-activation is correct — but `provider` and `record_type` stay unknown because the subject is not the holder |
| `law_practice.evidence-exhibits` | `Exhibit RP1 - CCTV - Station Rd 2026-02-11.mp4` + index | Service endorsement and serving-party slot. Flagged as an *orthogonality seam*, not a true mutex — see NJ-CD-3 |

Reciprocals are **owed to** this row from `legal.personal-legal-matters`, `law_practice.discovery`,
`law_practice.investigation` and `law_practice.evidence-exhibits`. I edited none of them.

Neighbours considered and given no edge: `law_practice.appeals` (an appeal against conviction is the
same matter continued, not a competitor — the schema's own work-type list holds it);
`law_practice.hearing-transcripts` and `law_practice.pleadings` (same orthogonality argument as
evidence-exhibits, and one representative entry is enough to state it);
`law_practice.immigration-casework` (a real seam exists where a conviction drives an immigration
consequence, but it is the third leg of NJ-FL-2 and should be authored once, reciprocally, after R1c
rules — I raise it rather than author it); `identity.core-documents` and `finance.personal-records`
(co-activation cases inside a served bundle, not mutexes); `research.reading-library` (public judgments
are routed by residual, which is cheaper than an edge).

## Fields and dimensions

`fields: []` and `proposed_fields: []` are correct and not a shortcut. The anchor already carries the
`client` proposal and a `subject_of_record` proposal; minting a variant here is exactly the synonym
mint the brief forbids. I **endorse** `subject_of_record` and add the one observation no other proposer
has made: this row needs it to distinguish a subject who is the **client** from a subject who is an
**adverse third party** *within a single matter*, and that distinction is what decides whether the use
restriction attaches. Candidates I considered and rejected outright: `charge`, `offence`, `count`,
`disposal`, `custody_reference`, `proceeding_id`, `plea` — every one is a legal characterisation this
product must never compute, and several would write an accusation into a stored fact.

## NEEDS-JOSEPH

- **NJ-CD-1 — the practice-area charge, answered as a narrow yes, recorded so it can be reversed.** If
  R1c judges that the use-restriction and non-subject rules belong on the `law_practice` *schema*
  rather than on one template — defensible, since `law_practice.investigation`, `law_practice.discovery`
  and `law_practice.immigration-casework` can each hold third-party material under a restriction — then
  the correct outcome is **refusal**, the rules move up, and coverage routes to the schema default plus
  Protected Records. This row would rather be refused than kept for its topic.
- **NJ-CD-2 — answering `family-law`'s NJ-FL-2, which asked this row two questions by name.** (a) Is a
  protected-witness-address slot this row's rule or the schema's? **The schema's** — it appears in
  family, criminal and investigation material alike and no row should own it; it should move up to the
  anchor. (b) Are the three allowed practice-area rows one privacy rule or three? **Not one.**
  `family-law`'s rule is an internal boundary between two people who are both its subjects; this row's
  is a restriction on material about people who are not its subject at all — and on the *same*
  protective order the two rules point in opposite directions, because here the client is the person
  the address is withheld from. R1c should either move the address slot up and keep the rows distinct,
  or merge all three into one protected-natural-persons template with the practice areas as `work_type`
  values. It should not do half of each.
- **NJ-CD-3 — the orthogonality problem, and it is bigger than this row.** The 36 templates on this
  schema mix a *document-function* axis (pleadings, discovery, evidence-exhibits, hearing-transcripts,
  court-filing-record) with a *practice-area* axis (this row, family-law, immigration-casework). A
  criminal exhibit bundle sits on both. Alternatives: (a) one function row plus one practice-area row
  may co-activate, in which case two of my collisions become co-activation notes; (b) force a winner
  per file, which I believe loses the use restriction; (c) collapse the function rows into `work_type`
  values and let the practice-area rows carry the privacy differences. `also_holds_with` is
  schema-to-schema only under CONNECTION §5, so no template can express (a) as an edge — R1c must settle
  it. Recorded, nothing edited.
- **NJ-CD-4 — Rule C needs an owner.** "Sensitivity rises at closure" binds archival, cold-storage and
  summarisation behaviour, none of which this row controls. Alternatives: (a) a per-domain flag that
  suppresses age-based cooling; (b) a universal rule that a matter's terminal artefact inherits the
  matter's maximum sensitivity rather than its own; (c) leave it to user review, which I believe is
  unsafe because the file is invisible to the user until something surfaces it.

## Self-verification

- `python3 -m json.tool` parses the node; key set is identical to `law_practice.family-law.json`.
- Every neighbour id in `collides_with` confirmed present in `planning/domains/roster.json`
  (`legal.personal-legal-matters`, `law_practice.discovery`, `law_practice.family-law`,
  `law_practice.investigation`, `medical.personal-health-records`, `law_practice.evidence-exhibits`).
- Every `collides_with` entry is an object with `domain` / `signal` / `provenance` and a
  SAME-FIXTURE-BOTH-SIDES signal; `also_holds_with` is empty because this is a template.
- All five 00 quotations grep back verbatim out of `planning/00-database-agent-product-design.md`;
  `design_cite` is `null` because no single span carries the row's argument and a decorative cite is
  worse than none.
- Wrote only the two assigned files. No roster, canonical-field, neighbour, `src/` or SPEC edit.
