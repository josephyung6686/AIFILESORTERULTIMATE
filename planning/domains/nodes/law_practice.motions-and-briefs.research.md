# Research memo — `law_practice.motions-and-briefs`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/law_practice.motions-and-briefs.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`

## Result

**Keep the node — narrowly, on one leg of the three, and only after repairing its definition.**

The row as the roster states it ("documents asking a court to decide something short of the final
outcome") would fail. That is a **lifecycle position**, and the evidence falsifies it: a
summary-judgment motion disposes of the case, a post-trial motion follows the final outcome, and an
appellate extension application is interlocutory in exactly that sense yet belongs to a neighbour.
What survives is not a stage and not a document-type word but a **six-item apparatus** — a labelled
orders-sought slot, a self-referential table of authorities, a labelled length attestation, a
return-date slot, a briefing-sequence cross-reference, and an enclosed blank-execution proposed
order. The row is rewritten on that and the rename is NJ-MB-1.

The node test is passed on **detection signals only**. Dimensions and privacy are conceded outright
(§4). That is the honest shape of the finding, and it is stated rather than padded into three
apparent wins.

## The charge — the strongest case that this row should not exist

I put the case at its strongest before answering it, because a sibling on the same schema has
already lost the identical argument.

**(a) It is a `work_type` value.** The schema's own `proposed_fields` entry for `work_type` says so
in advance and names my document in the list: *"Pleading, motion, order, affidavit, exhibit,
opinion, undertaking - these are VALUES of `work_type`, not nodes"*, and *"a template row justified
only by holding a different legal document kind is the schema's default template with a narrower
filename filter."* Worse, the schema's `work_types` array bundles **"pleading, application,
submission and written case" as a single value** — so this row and `law_practice.pleadings` are one
value, and pleadings is refused.

**(b) It is a document type.** Motion, brief, memorandum, skeleton, opposition, reply. Delete the
document-type word and, on the face of it, a captioned numbered document remains — which is
`legal`'s.

**(c) It is a lifecycle stage.** "Interlocutory" means *during the proceeding, before final
judgment*. A row that only says *this happens in the middle* is a stage, not a world.

**(d) It is a length.** A brief is, in the profession's own idiom, the document with a word limit.
A certificate of compliance is a count. Counts are values.

**(e) It is a duplicate of a refused sibling.** `law_practice.pleadings` was refused on this
reasoning: its evidence — caption, bound party pair, numbered paragraphs, statement of truth — is
exhausted by the proceeding-record face, which `legal` already reads; nothing structural survived
the schema's deletion test. Its own `open_question` names me first: *"`law_practice.motions-and-briefs`,
`law_practice.appeals` and `law_practice.orders-and-judgments` rest on the same caption-plus-party-pair
structure separated only by a document-type word, so the argument that refuses this row appears to
reach them too."* That is a landed row arguing for my refusal, by id.

**(f) The schema disclaims proceeding records.** `law_practice`'s own `one_line`: it *"deliberately
does NOT hold the executed instruments and proceeding records inside a matter file (those stay
`legal`'s on `legal`'s own evidence, and `legal` is a safety domain whose protection runs first)."*
A filed motion is a proceeding record. On a literal reading the schema has already excluded me.

## 2. Defeating the charge

The pattern across landed `law_practice` siblings is decisive and I checked it before deciding.
Every row that **survived** owns *apparatus* and explicitly disclaims the substantive document:
`law_practice.discovery` owns the review log, the withholding schedule and the load file, not the
documents produced; `law_practice.court-filing-record` owns the transmission receipt and states in
its memo that the filed document is not its evidence — *"its evidence is its own body — caption,
numbered allegations, prayer for relief"*; `law_practice.appeals` owns the compilation and its index
and writes *"THIS ROW OWNS THE COMPILATION AND ITS INDEX, NEVER THE MEMBERS."* The row that
**failed** — pleadings — tried to own the document itself.

So the question is not whether a motion is a document type. It is whether there is apparatus around
the request that `legal` cannot read. There is, and it survives the schema's deletion test (*delete
every entity name and every document-type word*):

1. **A labelled orders-sought / relief-sought slot** — an enumerated block whose own label announces
   that the tribunal is being asked to *order*, not that a party *alleges*. A labelled slot, read
   through 00's direct-fact path, *"a labeled form field"*. Not a word: a slot with requests in it.
2. **An enclosed proposed order with a blank judicial execution block under a live caption.** This
   is the strongest single item, because it is a *three-way inverse*. `legal` fires on a bound party
   pair **plus execution**; here execution is deliberately empty. `law_practice.orders-and-judgments`
   owns the same instrument the moment it is signed, dated, entered or sealed. `law_practice.precedent-bank`
   owns unexecuted instruments whose **party** recital is bracketed and which have no live
   proceeding. *Parties filled, tribunal empty, caption live* is a combination no other roster row
   produces.
3. **A table of authorities with page back-references** — a table whose rows are citations and whose
   right column points back into *the same document*. A self-referential index is a structure, not a
   subject. Bibliographies, reading lists and research memos cite; none indexes its own pages.
4. **A labelled length attestation.** Stated carefully because *a length* is on the refusal list:
   the row does not claim documents by how long they are, and a word count is a value. The evidence
   is the **attestation slot** — a labelled assertion made to a tribunal that a limit was observed —
   which nothing else in the family or its neighbours produces.
5. **A return-date slot on the document's own face.** An interlocutory application is the only filed
   artefact that *schedules its own determination*. Structurally unlike the schema's diary signal,
   which is a portfolio table over many matters with an owning-practitioner column.
6. **A briefing-sequence cross-reference** naming another filing by its own filing identifier. Two
   documents by **adversarial** authors bound into one operative exchange — a relation no
   version_family and no matter anchor expresses, and one no authorship signal can produce by
   accident.

None of the six is a caption, a party pair or a notarial block, which are `legal`'s three
deterministic signals. The evidence is therefore **disjoint** from `legal`'s on the same page: the
caption is conceded whole and `legal`'s safety protection runs first, and this row takes nothing
from it. That disjointness is exactly what pleadings lacked, and it is the whole of my answer to
charge (e) and (f).

Answering (a) directly: yes, "motion" is a `work_type` value, and the row does not rest on it — the
`never_alone` list strikes the words *motion, application, brief, memorandum, submission, petition,
opposition, response, reply, skeleton, order* **first**, before anything else. A row can share a
`work_type` value with the thing that names it and still be a node, provided the value is not the
evidence. Here it is not.

Answering (c) and (d): both are conceded as *descriptions* and rejected as *definitions*. The row is
redefined on the apparatus, and NJ-MB-1 hands the rename up. If R1c rejects the repair and keeps the
interlocutory framing, my recommendation is to **refuse the row** rather than run it on a lifecycle
stage — one apparatus split across two homes, with dispositive motions unowned, is worse than a
clean refusal.

## 3. The node test, all three legs

The schema's default template is stated at `law_practice.json` → `template`: `dimension_order: []`,
`time_first: false`, with the recommendation held as prose — *the client only where the corpus spans
more than one AND the user has explicitly approved a client-named branch, then the matter, then the
document function, then the period last*. Its default detection is the two-leg precondition: an
exact matter reference repeated across two or more artefacts, plus one artefact whose labelled slots
separate a practitioner-or-firm role from a client role. Its privacy default is stricter than
`legal`'s in one specific way — it protects a **third party**, not the holder.

**Leg 1 — detection signals. DIFFER. This is the whole node.** The schema declares eleven
deterministic signals: intake-and-conflicts, matter-opening, time-and-disbursement, limitation
diary, disclosure-review, precedent bank, internal work-product, counsel-instruction/opinion,
closure-and-retention, archive export, email/calendar. **Not one of them is a filed submission**, and
none of the six apparatus items appears anywhere in the schema's list. My signals are strictly
additive to the precondition (which I inherit whole and restate as such in `recognition.deterministic[0]`)
and are readable from bytes without any of the schema's defaults being present on the same file.

**Leg 2 — recommended dimensions. DO NOT DIFFER, and the row says so.** `dimension_order: []` for
the schema's three reasons — no declared field to branch on (D1, PR-6, `_CONTRACT` 10 and 15);
safety co-activation, since 00 states *"Finance, identity, medical, and legal material should be
implemented first as safety domains"* and no deep template unlocks from safety activation; and the
disclosure cost of the only natural dimensions. Held as prose, my recommendation is the schema's
recommendation unchanged, and **this row is one value at the function level, not a level of its own** —
which is the honest reading of 00's *"A work type such as Homework 3 is meaningful only after the
course is known"*: an opposition is unintelligible without the request it opposes, and the request
without the matter. Not time-first: filing time, hearing time, document date and filesystem time
mean four different things here and nothing is capture-based. The two things I would add if fields
ever landed are **prohibitions, not dimensions**: never a hearing-date level (it is the one date the
product is most likely to be asked to act on, and must not be structurally privileged) and never a
named-third-party level (an emergency application names a child).

**Leg 3 — privacy rules. DO NOT DIFFER, and the row says so.** The material is
`potentially_sensitive`, exactly as the schema is. Emergency-residence, in-limine and sealing
applications narrate a third party's intimate circumstances — but that is the schema's own
third-party rule at its sharpest, not a new rule, and inventing a distinction here to win a second
leg would be padding. Two row-specific *observations* are recorded in `sensitivity_why` without
being dressed as differences: this is the most **public-looking** material in the schema (most of it
sits on a docket, and public availability is never-alone), and the most sensitive documents here are
the ones **asking for protection** — a motion to seal must recite in full the material it asks the
tribunal to withhold, so sensitivity is frequently inverse to the relief sought.

Verdict: the test is disjunctive; one leg differing is sufficient, and only one does.

## 4. Files considered and rejected

Tempting false positives, each with the reason it is not this row's evidence:

- **The e-filing stamp, the submission identifier and the certificate of service** printed on my own
  page-one and last page. Genuinely on the same bytes. Rejected: they record a *transmission*, not a
  request, and `law_practice.court-filing-record` owns them even when they sit on my document. A
  filed stamp never promotes a draft.
- **The exhibits tabbed behind a supporting declaration.** Rejected on the firewall
  `law_practice.appeals` drew for record members: the compilation is one row's, the members are
  their own. I own the declaration's *binding header* ("in support of ...") and nothing past it. An
  exhibited invoice keeps its own finance evidence.
- **The `.ics` for the hearing named in my return-date slot.** Rejected for the reason
  `court-filing-record` gives against the same temptation — *an event is a date, not a
  transmission*; here, an event is a date, not a request. `calendar` is deliberately absent from
  `file_kinds.source_types`.
- **The internal research memo that became the brief**, ~90% identical text. Rejected: the
  discriminator is the **absence of the entire apparatus**, not topic. Were topic sufficient this
  row would swallow every research memo in the corpus. `law_practice.legal-research` owns it.
- **The docket sheet listing my motion as entry 143.** Rejected: a docket is a portfolio of events
  over a proceeding; it contains no request and no argument. It is `legal`'s proceeding record.
- **A published or downloaded opinion deciding the same question.** Rejected: no relief slot, no
  return date, no attestation, no proposed order; and no matter reference. Reading Inbox.
- **A `-final` or `PROPOSED` filename.** Rejected as constitutionally never-alone. A firm routinely
  names its file copy of the *signed* order after the draft it submitted.
- **A word-count or page-count value anywhere.** Rejected: the count is a value; only the labelled
  attestation slot is evidence, and only beside a captioned proceeding identifier.

## 5. Reciprocal boundaries — same fixture named on both sides

Eight edges are authored in `collides_with`, every one an object carrying its discriminator. The
four that matter most:

- **`law_practice.pleadings`** — fixture: *a court-captioned, numbered-paragraph, counsel-signed
  document filed in `Hartley v Nash`, in the same folder as the amended statement of case*, which is
  the neighbour's own wording of the fixture. **Mine** where the apparatus is present. **Theirs**
  where numbered paragraphs assert the parties' allegations and close on a prayer — *except that the
  row is refused*, so that pattern counts toward `legal`, not toward them. Where neither is legible,
  the caption supports `legal` alone.
- **`law_practice.appeals`** — fixture: *`Motion for extension of time to file opening brief -
  24-1187.pdf`*, and any submission with a table of authorities plus a certificate of compliance.
  The neighbour authored this edge first and I adopt its discriminator without weakening it:
  **theirs** on the two-tier proceeding-identifier pair or a labelled standard-of-review section;
  **mine** at a single tier. The hard half is conceded, in their words — an appellate stay,
  extension or expedition application carries my complete apparatus and is still theirs. Second
  competition, resolved the other way: a first-instance motion reproduced inside a record on appeal
  stays **mine**, because appendix membership lives on the index, not the member — which is the
  neighbour's own rule, quoted from their fixture.
- **`law_practice.orders-and-judgments`** — fixture: *`[PROPOSED] Order Granting Motion to Compel`*
  and the signed order that issues from it, same caption, same decretal paragraphs, often the same
  byte lineage. **Mine** while the execution block is blank; **theirs** the moment signature,
  judicial name, entry date or seal appears. Discriminated by the execution block, never the
  filename.
- **`law_practice.discovery`** — fixture: *`Motion to Compel Production - FILED 2026-08-20.pdf`*,
  named by the neighbour from its side. **Mine**: the argument-and-relief apparatus, and I own the
  motion whole even though most of its page count is quoted demands. **Theirs**: the demand
  instrument, the responses, the review log, the withholding schedule, the load file.

Also authored: `law_practice.court-filing-record` (request vs transmission),
`law_practice.legal-research` (apparatus vs research grammar), `law_practice.precedent-bank`
(*where is the empty slot* — tribunal's place vs parties' place; residuals differ with it), and
`legal` (disjoint evidence on one fixture, safety first, nothing taken).

**Deliberate non-edge**, argued rather than omitted: `law_practice.evidence-exhibits`. It is not a
same-evidence mutex because the two never compete for the *same item* — I stop at the binding
header, each exhibit is theirs on its own tab. Recorded here for R1c in case they see it
differently from their side.

`also_holds_with` is **empty**: it is schema-to-schema only under CONNECTION §5 and this row is a
template. The coactivation I would have recorded is the disjoint-evidence relation with `legal`,
which lives in `collides_with` instead. NJ-MB-3 flags that the landed sibling `law_practice.pleadings`
— also a template — puts the schema `legal` in `also_holds_with`; one of us is wrong and only R1c
may normalise it.

## 6. The collision fixture

`Sample Motion in Limine - Trial Advocacy Institute - annotated model.pdf`.

It carries a full caption, an orders-sought block, a numbered argument, a table of authorities with
page back-references, and a certificate of compliance. **Every structural item this row claims, all
six, perfect.** It is not this row's evidence.

What discriminates it is not the apparatus but the **schema precondition failing entirely**: no
matter reference recurring across artefacts, and no artefact separating a practitioner role from a
client role. The signature block reads *Instructor*; the party names are fictional; the case
identifier is a placeholder format; margin callouts explain why each drafting choice was made. Only
00's purpose test separates it — *"purpose answers what the file was for"* — and here the callouts
state that purpose out loud.

This is the schema's own named risk (*"this family's exemplars are unusually convincing because the
profession publishes its own templates"*) and it is why the row's `deterministic[0]` is the
precondition and not a signal. Residual: **Reading Inbox**, not Protected Records — there is no
client, no matter and no third party in the file.

A second, under-firing collision is carried as a fixture too: `Motion for extension of time -
24-1187.pdf`, structurally a motion in every respect, conceded to `law_practice.appeals` on the tier
pair.

## 7. Fields

`fields: []` (the schema owns them and declares none under PR-6) and **`proposed_fields: []`**. The
schema already proposes `client`, `our_firm`, `project`, `work_type`, `subject_of_record` and
`fiscal_period`; this row asks for nothing beyond them and deliberately declines four candidates:

- `relief_sought` / `motion_type` — values of the existing `work_type` enum. Minting either is the
  respelling R1c is asked to refuse.
- `hearing_date` / `return_date` — refused on principle, not on economy. It is the one date in this
  family the product could be tempted to act on, and a field is a step toward a dimension. The
  schema's diary signal already covers key dates as observations.
- `docket_entry` / `filing_id` — a linkage identifier whose own labelled role is established
  elsewhere; `law_practice.court-filing-record` is the right place to raise it if anyone does.
- `tribunal` / `jurisdiction` — explicitly unavailable as a field or dimension under the current
  decision brief, per the landed `legal.practice-matter-file` record.

## 8. Recommendations for R1c (cross-row; not made here)

1. Rename/redefine the row on the apparatus and drop "short of the final outcome" (NJ-MB-1).
2. Adjudicate the family-wide test proposed in NJ-MB-2 — *is the evidence exhausted by the
   proceeding-record face?* — rather than deciding pleadings, appeals, motions and orders one at a
   time.
3. Normalise the `also_holds_with` convention for templates (NJ-MB-3).
4. Redirect the pleadings half of `law_practice.court-filing-record`'s deferral (NJ-MB-4).
5. Settle who owns an unexecuted instrument (NJ-MB-5).

## NEEDS-JOSEPH

All five are serialised verbatim in the JSON's `open_question`. In brief:

- **NJ-MB-1** The roster hint defines the row by a lifecycle position and the evidence falsifies it.
  (a) redefine on the apparatus — this row's recommendation; (b) keep the interlocutory framing,
  splitting one apparatus and orphaning dispositive motions; (c) refuse, forfeiting the apparatus to
  `legal`'s caption and dangling two landed neighbours' edges.
- **NJ-MB-2** Sibling symmetry, raised against this row **by name** in `law_practice.pleadings`'
  open question. My answer is offered for adjudication, not asserted as settled.
- **NJ-MB-3** `also_holds_with` contract inconsistency between this row and the landed sibling.
- **NJ-MB-4** `law_practice.court-filing-record`'s deferral now points half at a refused row.
- **NJ-MB-5** Ownership of an unexecuted instrument, across three rows; my test is an inference.

## Self-verification

- `python3 -m json.tool` parses the JSON; key set matches `law_practice.appeals.json` exactly
  (27 keys, including `falls_through_to`).
- Every quotation used was grep-verified in `planning/00-database-agent-product-design.md` before
  writing (each returned exactly one match): *"purpose answers what the file was for"*, *"A work
  type such as Homework 3 is meaningful only after the course is known"*, *"It should not form a
  supported group when there is no valid anchor"*, *"Finance, identity, medical, and legal material
  should be implemented first as safety domains"*, *"a labeled form field"*, *"The documents are
  content-incoherent but purpose-coherent"*, *"It should avoid using authorship or creator identity
  as a destination dimension"*. Quotations attributed to neighbour rows are quoted from those files,
  not from `00`, and are labelled as such.
- Every `collides_with` entry is an object with `domain`, `signal`, `provenance`, and every signal
  names the same fixture on both sides plus the discriminating item.
- Every neighbour id was confirmed present in `planning/domains/roster.json`
  (note: the roster id is `law_practice.depositions-testimony`, not `.depositions`).
- All four `falls_through_to` values are residual homes already in use by the landed sibling.
- No thresholds, no counts, no handling classes, no regexes, no gazetteer contents.
- Files written: only `law_practice.motions-and-briefs.json` and
  `law_practice.motions-and-briefs.research.md`. Nothing else was created or edited.
