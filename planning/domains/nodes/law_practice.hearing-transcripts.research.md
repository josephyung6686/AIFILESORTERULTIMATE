# Research memo — `law_practice.hearing-transcripts`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/law_practice.hearing-transcripts.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept, and the accepting argument is narrower than the row's name.** The row is not the word
"transcript", not the schema's listed work-type value, and not the medium. It is the one artefact
class in this family whose evidence is a **citation-address grid** — a page-and-line coordinate
imposed across the whole document, by which any passage becomes externally addressable and citable
by other documents — produced and attested by a **certifying third party** who is neither the
practitioner nor the client. Both legs survive the family's deletion test, both are absent from every
other row in the family, and the schema's own default signals **do not fire on this material at
all** — which is the decisive fact.

## Binding material read

The standing brief; the stamped assignment; `law_practice.json` read programmatically for
`recognition` / `template` / `work_types` / `falls_through_to` / `sensitivity_why` /
`proposed_fields` rather than streamed; `canonical_fields.json` (37 keys); `roster.json` for edge
validation; `legal.practice-matter-file.research.md` in full as launch-row calibration;
`law_practice.appeals.json` + `.research.md` at the spans naming this row, because that row had
already argued a boundary here and its concession had to be mirrored;
`law_practice.depositions-testimony.json` at its one reciprocal signal, which landed in parallel
during this pass; `07-law-legal-practice.md` §17, §18, §22 and the roster table. `00` was **not**
read whole — grepped only to verify the seven spans quoted in the JSON.

`CONNECTION.md` was not re-read; the dispatch's restatement of §5 was followed, and its consequence
is visible: **`also_holds_with` is empty** on this template row rather than carrying `legal`, because
that edge is schema ↔ schema only. The intent is recorded below for R1c. This is the defect
`law_practice.appeals` flagged as its NJ-3 and it is deliberately not recreated.

## THE CHARGE — the strongest case that this row should not exist

Stated at full strength before it is answered, because four of the five limbs are right about
something.

**1. It is a work_type value, and the schema says so in its own words.** `law_practice.work_types[]`
contains *"witness statement, proof of evidence and deposition or hearing transcript"*. The row's
name is sitting inside its schema's enum of values, and the brief's rule — *work types are values,
not nodes* — appears to dispose of the matter without further argument.

**2. It is a document type, and a document-type word is struck evidence.** The schema's precondition
strikes *"a document-type word beside any of them"*. "Transcript" is exactly that, and it is a
homonym across four unrelated worlds (grades, podcasts, meetings, proceedings) — normally a sign the
word is doing all the work.

**3. It is a medium.** A transcript is a rendering: speech turned into text. Under that reading the
row is `SOURCE_TYPES` in a costume — audio_video plus its text derivative.

**4. It is a duplicate of a neighbour, and the catalogue says so.** §22's collides table gives
`law.depositions` and concedes the pair is *"formally near-identical"*, separated by *"the court name
and the judge"*. Both are **values**: a court name is struck never-alone family-wide, a person's name
is struck by the deletion test. A row whose only stated difference from its neighbour is two struck
tokens is a `court` field value, not a node.

**5. It is a lifecycle stage.** `law_practice.trial-preparation` owns the hearing and its bundle. The
transcript is that same hearing, one day later.

### The answer

**Limbs 1 and 2 together — the schema's default cannot reach this material, so the row is not a
subdivision of the default; it is the default's blind spot.** The precondition requires **both** of
(i) an exact matter, file or engagement reference repeated across two or more artefacts and (ii) at
least one artefact whose labelled slots separate a **practitioner or firm role** from a **client
role**. A hearing transcript satisfies **neither**:

- Its heading carries a **court case identifier** allocated by the tribunal, not the firm's matter
  reference. The firm's reference appears on the reporter's invoice and the covering email — not on
  the record.
- Its **appearances block lists counsel for every side on equal footing**. That is not a two-role
  practitioner/client separation; it is the structural *opposite*, since the block exists to record
  adversaries symmetrically.

So this is a central, high-volume artefact of the world on which the schema's activation signals are
silent. A value inside an enum is by definition reachable by the schema declaring the enum; this
material is not. The enum entry is evidence the schema **anticipated** the material, not that it
**detects** it — and a template exists precisely to supply detection the default lacks.

**Limb 3 — the row is not the medium, and its own file list proves it.** The audio fixture
(`Court 4 recording 2026-03-14.m4a`) is written in as a file this row **does not activate on**, with
`00` §2.9 quoted as the reason. The two clearest members — the certified transcript and the
key-passages index — are both `text_document`, and the index contains no speech at all. A row that
refuses its medium's canonical file and accepts a table of coordinates is not a medium.

**Limb 4 — the catalogue's discriminator is rejected here and replaced.** This is the memo's most
substantive repair. "The court name and the judge" cannot separate the two rows because both tokens
are struck. What does separate them survives deleting every name:

| | this row | `law_practice.depositions-testimony` |
|---|---|---|
| cover slot | **BEFORE / CORAM**, naming a judicial **office by title** | **PLACE OF EXAMINATION**, naming an **address** |
| correction | corrected by producer or tribunal; no signed change sheet | **deponent-signed errata** — page-and-line reference, change, **stated reason**, signature |
| turn grammar | includes a **court-officer speaker label** carrying rulings and interventions | counsel and deponent labels only |

Delete every proper noun from either cover and both slots still read as labelled slots; delete every
proper noun from the errata sheet and its four columns still read. The JSON carries this with an
explicit rejection of the catalogue's version, so a later reader does not restore it.

**Limb 5 — different namespaces, and the direction of time is the tell.** `trial-preparation`'s
bundle index maps **whole member documents** to **tab numbers** in a set compiled **before** the
sitting; this row's index maps **passages** to **coordinates** inside a record that already exists.
The cross-examination plan that *cites* coordinates is wholly the neighbour's; the record page it
cites into is wholly this row's.

**Limb 4's residue is conceded.** Where the cover is missing, the two rows genuinely cannot be told
apart. That case is written into `needs_llm` and routed to Review Later rather than guessed.

## The node test, all three legs

**Leg 1 — detection signals differ. PASSES; it is the leg the row stands on.** Argued above: the
default's two legs are both absent, and the row substitutes its own (grid **plus** either a
certifying-producer block or a sitting cover). Three further signals exist nowhere else in the
family: the **certifying third producer** — the family's only three-role artefact, and since the
schema's entire default is a *two*-role structure a third authenticating role is not expressible in
it; the **day-or-session marker in an open-ended series**, a cardinality signal rather than a date;
and the **transcript index**, addressing a coordinate namespace no other row owns.

**Leg 2 — recommended dimensions differ. PASSES on the prose recommendation, all PR-6 permits.** The
schema recommends client (approved, multi-client only) → matter → document function → period. Under
that order a twelve-day hearing collapses: every day, every status of every day, the index and the
recording land in one flat function folder distinguished only by filename — and a filename sort puts
day 12 before day 2. The row inserts exactly **one** level, the **sitting**, named by the
proceeding's own identifier and never by a party, argued from `00`'s intelligibility principle,
*"A work type such as Homework 3 is meaningful only after the course is known"*: an index, a
correction, a key-passages note and a day-3 rough copy are meaningless without the sitting they
address. Three bans are stated because the natural axes here are the forbidden ones — **witness may
never be a level** (NJ-HT-1), **status may never be a level**, **day may never be a level**, the last
two producing the one-child folders `00` warns against. `time_first: false` is argued from this row
rather than inherited: this is the family's most time-shaped artefact and that is exactly the trap,
since a date-first tree interleaves unrelated matters' sitting days into shared month folders.

**Leg 3 — privacy rules differ. PASSES, and the difference is an inversion rather than a degree.**
Every other member of this family is confidential by construction. A hearing record is the family's
**only** artefact whose default may be **public**, whose exceptions are **total** (in camera, closed,
youth, family, protected-witness, sealed portions) and **invisible on the face**. The schema's
default never reasons about openness, so the rule this row needs — *openness is never inferred in
either direction; a public-hearing observation never downgrades protection; an unresolved
closed-session marker protects the whole file* — is not a stricter default, it is a rule the default
cannot state. Two intensifiers compound it: the content is **compelled, involuntary speech** by
people including non-parties, complainants and children; and the grid makes any fragment a **precise
citable quotation** rather than an excerpt, which is why Protected Records' local-only constraint
binds harder here than for a static document.

## Files considered and rejected

- **`Errata sheet - examination of Jordan Lee - signed.pdf`** — carries page-and-line references, this
  row's own first leg. Wholly `depositions-testimony`'s: the deponent-signed change-and-reason table
  is that row's mechanism, and this row may not read the coordinate as its second leg.
- **`Hearing Bundle Index - Volume 2 of 4.pdf`** — a table, a case identifier, page numbers, the word
  "hearing". Wholly `trial-preparation`'s: bundle tabs over documents, compiled before the sitting.
- **`Board strategy call - Zoom - transcript.txt`** — the **structural** collision; see below.
- **`Transcript.pdf` (academic)** — the **lexical** collision fixture; see below.
- **`Court 4 recording 2026-03-14.m4a`** — a filename naming a court, a room and a date proves
  nothing, and transcribing to find out is gated by `00` §2.9.
- **`RE Transcript order - expedited daily copy.eml`** — an instruction to *produce* a record is not a
  record; it names sitting dates and contains nothing that was said. Its appellate cousin, the
  designation form, is conceded wholly to `law_practice.appeals`.
- **`scan transcript p214.jpg`** — an interior page: grid present, cover and certificate both absent.
  One leg is never enough; it groups without activating.
- **A transcription agency's invoice or quotation** — considered, not written as a fixture. Carries an
  issuer-and-billed-to block and belongs to `finance` on `finance`'s own evidence; the agency's
  letterhead is never-alone.
- **A published historical or legislative transcript, or a printed interview collection** —
  page-and-line numbering with no certifying producer and no proceeding. Reading Inbox.

## The collision fixture

**`Transcript.pdf` — an academic transcript of grades.** Named exactly as this row's material, and
the resemblance is *entirely in the filename*: the body is a term-by-term table of subjects, credits
and grades with a cumulative total, an institutional seal and a registrar block — no speaker turns,
no grid, no case identifier. The discriminator is that **neither row's structural leg appears on the
other side at all**, so the filename counts for **neither row and is discarded before either
evaluates**. The edge to `academic.transcripts-credentials` is carried deliberately even though the
collision is purely lexical, so that the "the word transcript" strike has a named target rather than
a rhetorical one — and because the failure it prevents is severe in one direction: routing a
student's academic record into a legal-practice corpus attaches a proceeding to a person who has
none.

The **structural** collision, harder and getting harder every year, is
`Board strategy call - Zoom - transcript.txt`: same turn grammar, same word. Discriminated by
**timecode vs page-and-line** addressing and by **participant list vs appearances block**. An
automated transcription disclaimer is not a certifying producer.

## Reciprocal boundaries

Every `collides_with` entry names the **same fixture on both sides** and states both directions.

| Neighbour | Shared fixture | This row owns | Neighbour owns |
|---|---|---|---|
| `law_practice.depositions-testimony` | one certificate-bearing, page-and-line, speaker-labelled sworn transcript | BEFORE/CORAM slot + court-officer turns | place-of-examination slot + deponent-signed errata |
| `law_practice.trial-preparation` | one table of page numbers beside a case identifier | passages → coordinates, retrospective | documents → tabs, prospective |
| `law_practice.appeals` | appellate oral argument; a first-instance day re-paginated into the record | **every verbatim record at either tier** | the transcript order / designation form and the record page-range index |
| `law_practice.orders-and-judgments` | one ruling delivered orally, existing twice | the artefact with transcript geometry, even when its content is a ruling | the artefact with decision geometry, even when its words were spoken |
| `legal.personal-legal-matters` | one certified transcript held by the person whose hearing it was | only where the **side** is separately evidenced | direct holder-role evidence; **this row abstains** where side cannot be cited |
| `business_operations.meeting-record` | a speaker-labelled file named "transcript" | page-and-line + certifying producer + appearances | timecode + participants + tool/secretary producer |
| `academic.transcripts-credentials` | a file named `Transcript.pdf` | speaker-turn body under a grid | term/credit/grade table with a registrar block |

**The `depositions-testimony` pair converged independently, which is worth recording.** That row
landed in parallel during this pass and states its side as *"THE NEIGHBOUR OWNS the tribunal's own
record: a bench or presiding-officer line, in-line rulings on objections … and NO errata slot,
because a court owns its record and a witness cannot amend it,"* discriminated *"never by the word
transcript, never by the reporting company's footer."* Two agents with no contact reached the same
two-slot discriminator and both explicitly rejected the catalogue's court-name version. The pair is
already reciprocal; no repair is owed.

**The `appeals` boundary is a mirror, not a new claim.** That row landed first and conceded it
*"never owns a transcript on a transcript's own evidence — not even its own hearing's."* This row
accepts that and states the reverse concession in the same terms: the **transcript order and
record-designation form** and the **record index entry mapping an extract to a page range** are
wholly the appellate row's, because a designation names hearing dates and contains no testimony.

**The `legal.personal-legal-matters` boundary is the one where this row's headline signals do not
discriminate at all**, stated plainly rather than smoothed. A transcript is produced for whoever
orders it; cover, certificate, grid and turn grammar are byte-identical in a litigant in person's
folder and in a firm's. The side comes from the schema's precondition, elsewhere in the corpus, or
not at all — and the error is asymmetric, so where it cannot be cited the safety neighbour's
protection runs first and this row abstains.

## Neighbours considered that did NOT get an edge

- **`law_practice.evidence-exhibits`** — a transcript page marked as an exhibit carries two numbering
  layers, but `appeals` already authored the general two-layer discriminator (designator vs page
  range) and the same logic settles this pair. Flagged for R1c rather than duplicated.
- **`law_practice.matter-correspondence`** — the transcript-order email is correspondence and there is
  no contested fixture; this row simply declines it.
- **`law_practice.deadlines-diary`** — a sitting-day log with a status column resembles a diary
  register. Not edged: the diary's rows are about **many matters**, a sitting log's about **one
  sitting**, and the schema's limitation-and-diary signal already turns on that portfolio shape.
- **`creative.podcast-episode`** — the fourth "transcript" homonym. Not edged: one named lexical
  target is enough to make the strike concrete, and edge inflation would weaken it.
- **`photos.screenshot-captures`** — recorded as an `also_schema` note on the scanned-page fixture,
  following the landed launch row. A coactivation, not a mutex; a photograph of paper is not a
  screenshot.

## `also_holds_with` — deliberately empty, intent recorded for R1c

CONNECTION §5 scopes `also_holds_with` to **schema ↔ schema**, and this is a template. The entry that
would otherwise have been written:

> **`legal`** — named fixture: `Transcript - R v Okonkwo - Day 3 - 14 March 2026 - CERTIFIED.pdf`
> inside a matter. `legal` takes the tribunal caption and the proceeding identity, and its safety
> protection runs first; this row takes the certifying-producer block, the grid and the sitting/day
> structure, which `legal` claims none of. The caption is struck never-alone here, so it is never
> double-counted.

## Fields

`fields: []` — the schema declares none under PR-6 and a template may reuse only what its schema
declares. Catalogue §22's candidates are refused **here** rather than deferred, so no sibling reads
this row as a licence: `case_identifier` and `court` are the schema's own struck tokens, and giving
them field status would license as facts what is struck as evidence; `hearing_date` is a content date
the family already handles through universal facts; `hearing_day` is a real gap raised as NJ-HT-3, a
cardinality question, rather than minted.

**One `proposed_fields` entry: `transcript_status`** — a request for a *constraint* before it is a
request for a name. The tempting existing canonical key is **`version_family`**, and it is **actively
wrong** here: rough / uncertified / certified / corrected of the *same sitting day* are four
near-identical files with ascending dates that every generic version heuristic will collapse,
preferring the newest. They are not a version family — the rough copy is what counsel worked from
overnight and what a contemporaneous note cites into; both remain authoritative *for different
purposes*, and collapsing them destroys the earlier one's citability. No canonical key expresses a
coexisting-authoritative set (`version_family` asserts supersession, `stage` asserts progression,
`record_type` is finance-scoped, `file_type` is a format). Minting `transcript_version` or
`certification_state` would be the synonym mint the brief forbids. If canonical-fields can express
*"`version_family` must not be formed over this evidence class"*, the key should be withdrawn and
only the suppression kept.

## NEEDS-JOSEPH

1. **NJ-HT-1 — a live conflict; neither row may decide it unilaterally.** Catalogue §17's template for
   out-of-court examinations is `client → matter → proceeding → deponent → document type`, putting a
   **named witness in a filesystem path**. This row's sensitivity rule and the schema's third-party
   naming rule both forbid exactly that. *Alternatives:* (a) strike the deponent level from §17 and
   let both rows order by witness without a folder level; (b) permit it only behind explicit user
   approval, as the client level already is; (c) a local-only alias layer supplies witness grouping
   without writing the name to disk. Only (c) keeps the grouping and loses the disclosure, and it is
   a P9 question rather than a catalogue one.
2. **NJ-HT-2 — `transcript_status`, or a `version_family` suppression?** *Alternatives:* (a) adopt the
   key on `law_practice` if PR-6 lifts, `destination_eligible: false`; (b) add a declarable
   suppression of `version_family` over a named evidence class and drop the key; (c) neither, and
   accept that the product will silently prefer the certified copy. (c) is a data-loss outcome and
   should be rejected explicitly rather than by default.
3. **NJ-HT-3 — can a sitting-day ordinal be expressed with no fields declared?** Day ordering is the
   one piece of structure this row is confident about and the one a filename sort reliably gets wrong
   (day 12 before day 2). *Alternatives:* (a) a universal-fact ordering property outside the schema;
   (b) mint `hearing_day` if PR-6 lifts; (c) leave ordering to the grouping layer.
4. **NJ-HT-4 — openness policy ownership.** This row refuses to infer sealing, reporting restrictions,
   anonymity or publication status in either direction, and refuses to let a public-hearing
   observation lower protection. Defensible as a catalogue posture, but it means a genuinely public
   transcript stays protected forever. P7 and explicit user policy should own the escalation path.
5. **NJ-HT-5 — reciprocity backlog.** Seven `collides_with` entries authored. Two are already
   reciprocal (`depositions-testimony`, `appeals`); five targets must carry the mirrored signal when
   they land. This row edited no neighbour.

## Self-verification

- `python3 -m json.tool` → parses. Key set compared programmatically against
  `law_practice.appeals.json` → identical.
- All 7 `collides_with` entries are **objects** with `domain` / `signal` / `provenance`; every signal
  opens `SAME FIXTURE BOTH SIDES` and names one real file. `also_holds_with: []` per CONNECTION §5.
- Every edge id validated against `roster.json` → 0 unknown. Every `source_type` validated against
  `SOURCE_TYPES` → 0 invalid. Every residual name validated against `00` §7.3's nine → 0 invalid.
- All 7 quoted spans grep back **verbatim** out of `00`, checked by substring test including the two
  em dashes in the §2.9 audio span. No quotation was written that was not first verified.
- `fields: []`; one `proposed_fields` entry, argued against the named existing key it replaces.
- 12 file examples; observations split from facts; no folder path written as a fact; three marked
  `group_without_copying_facts: true`.
- No threshold numbers, no confidence scores, no handling classes, no invented statistics.
- Files written: exactly the two assigned. No neighbour, roster, canonical-fields, `src/`, SPEC or
  shared file was touched.
