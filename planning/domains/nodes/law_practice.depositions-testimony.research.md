# Research memo — `law_practice.depositions-testimony`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.depositions-testimony.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`
Absorbs the legacy row `law.witness-statements`

## Result

**Accept, with one leg of the acceptance argued harder than the other two, and one seam left open.**

The row survives the charge because its activation structure is not its schema's. The `law_practice`
default demands a matter reference plus an artefact whose labelled slots separate a **practitioner**
role from a **client** role. A certified deposition transcript has neither of those roles as its
anchor. Its anchoring slot is a **third professional role** — a reporter, notary, commissioner or
examining officer who attests that they administered an oath to a named individual and signs under
their own commission reference — and the person the file is *about* is usually neither the
practitioner nor the client, and frequently not a party at all. A transcript served by opposing
counsel can carry no reference belonging to the holder's firm anywhere in it and still be
unambiguously this row's material.

That is not a document-type argument. It is a different role structure, and it is why the row is a
node rather than a filename filter.

## The charge, stated at its strongest before it is answered

The case that this row should not exist is genuinely good, and it has six independent limbs. I set
them out fully because four of them survive partially and shape the row as written.

1. **It is a document-type word.** "Deposition", "transcript", "testimony", "witness statement" are
   document kinds. The schema's own `work_types` enum already contains, as a **single value**,
   `"witness statement, proof of evidence and deposition or hearing transcript"`. The schema itself
   wrote the rule that convicts this row if the row has nothing else: *"a template row justified only
   by holding a different legal document kind is the schema's default template with a narrower
   filename filter."*
2. **It duplicates `law_practice.hearing-transcripts`.** Both are reporter-produced verbatim Q-and-A
   with page-and-line numbering and a certificate-shaped block. The only apparent difference is
   *where the person was speaking* — a venue, which is a lifecycle/location value, not a structure.
3. **It duplicates `law_practice.discovery`.** In United States federal practice a deposition **is**
   discovery (the same rule set that governs interrogatories governs depositions). Discovery ceded
   it — but a cession is not proof the recipient deserves the coverage; it may only mean discovery
   correctly declined a document type.
4. **It duplicates `law_practice.evidence-exhibits`.** Deposition exhibits are exhibits, stickered
   and scheduled like any other.
5. **It is a medium.** A video deposition is `audio_video`; a transcript is `text_document`; a
   condensed rendering is a layout. Those are `SOURCE_TYPES` and page geometry, not nodes.
6. **Its evidence is never-alone all the way down.** The deponent's name is a person's name — struck
   by the schema's strictest rule. "Deposition" is legal vocabulary — struck. The caption is
   `legal`'s — struck. A reporting company's footer is an organisation name — struck. Apply the
   schema's own deletion test: delete every entity name and every document-type word. What is left?

### What survives the deletion test

Four slots, and the answer to limb 6 is that all four are structural and none of them is a name or a
document-type word:

- **An officer's oath certificate.** A non-party, non-counsel third person attests that they
  administered an oath to a named individual at a stated date and place, that the pages are a true
  record, and that they have no interest in the outcome — with their own commission or registration
  reference. Three labelled professional roles on one page (officer, examining counsel, defending
  counsel) plus a fourth non-professional role (the person examined) is a role structure no other
  roster row produces. Read through `00`'s direct-fact path, *a labeled form field*.
- **Page-and-line addressing.** A two-axis coordinate system with `Q.`/`A.` prefixes and surname-
  attributed colloquy. This is not formatting: it is what makes the artefact *quotable*, and it is
  why every downstream artefact in this family points *into* the file by coordinate rather than by
  paragraph. Numbered clauses, numbered paragraphs and numbered requests are other rows' structures.
- **An errata / read-and-sign sheet.** Columns for page, line, as-recorded wording, changed wording,
  reason — signed and dated **by the person whose words they are**. This is the decisive slot. It is
  a record of one individual amending a record of themselves, and **no other row in the roster
  produces it**: not a pleading, not an order, not an exhibit schedule, not an expert report, not a
  discovery response, not an investigation note, and specifically not a hearing transcript, because
  a court owns its own record and a witness cannot amend it. The signature-waiver line is the same
  slot in its negative form and counts equally.
- **A compulsion instrument aimed at a person.** A notice or subpoena directed at a *named natural
  person* to attend and answer orally at a stated time and place, naming the officer before whom.

Delete every name and every document-type word from a certified transcript and all four survive.
That is the row's whole existence claim.

### What the charge wins

Three concessions are written into the node rather than argued away:

- **Limb 2 is nearly fatal and is answered by a single discriminator, not by a theory.** The
  collision fixture below is real and the row concedes that surface signals are identical.
- **Limb 3's cession is recorded as a reciprocal mutex, not accepted as a gift.** The boundary is
  restated from this side in the terms `law_practice.discovery` used, so the two rows cannot contest
  transcripts by vocabulary later.
- **Limb 5 shapes `template.why`.** Because the medium argument is tempting, the node carries an
  explicit fourth placement rule: media segments must **not** be split from their transcript into a
  file-kind branch. That is precisely the placement a naive extension-driven tree produces first, and
  it would break the coordinate relationship the whole family rests on.

## The node test, all three legs

CONNECTION §2: a template exists only where its **detection signals**, **recommended dimensions**, or
**privacy rules** differ from its schema's default. All three differ here; any one would suffice.

**Leg 1 — detection signals. PASS, and this is the strongest leg.** The schema default is
*matter-reference-repeated-across-artefacts* **plus** *an artefact separating practitioner from
client*. This row fires on **officer-attestation plus person-anchor**, a role pair in which neither
member is the practitioner or the client. The two paths do not merely differ in strength; they use
different slots and can fire independently. A transcript with no matter reference and no
practitioner-side apparatus activates this row and not the schema default. Conversely, the schema
default fires cleanly on an intake screen, which has no attestation and no coordinate system.

**Leg 2 — recommended dimensions. PASS.** The schema default is *client (only if approved) → matter →
document function → period last*, with a standing ban on any named third party ever becoming a folder
level. Two of those four break here. First, this row's natural anchor **is** the banned thing — the
deponent, one named natural person. For every other template in the family the third-party ban is a
side constraint on an otherwise usable structure; here it lands on the row's own primary anchor, so
the row must state a substitute rather than inherit a recommendation. The substitute is *matter →
examination function (holding the whole package together) → examination date*, with the deponent kept
as a grouping key that is never written into a path. Second, that promotes period from last to third.
The row states plainly why rather than hiding it: the examination date is the attested date on the
officer's certificate, it is the only thing separating Volume II of a person's second examination from
Volume II of their first, and it is doing *within-matter* discrimination. `00`'s rule is about the top
level — *"For document and record domains, project, function, or subject usually comes before time
because putting year first scatters related work across calendar folders."* — and the matter still
comes first. `time_first` stays **false**, and NJ-DEP-3 records the fallback if R1c disagrees.

Function follows the matter for `00`'s stated reason: *"A work type such as Homework 3 is meaningful
only after the course is known, and a course code may require the school or term to disambiguate it."*
An errata sheet, a Volume II or a designation table is meaningless without its examination.

**Leg 3 — privacy rules. PASS, and the difference is specific rather than rhetorical.** The schema's
claim is that it protects a third party rather than the holder. This row narrows that to a *compelled
non-party* and then adds three rules the schema default does not have:

1. **The word index.** A certified transcript ships with an alphabetical concordance mapping every
   proper name and substantive term spoken to its page-and-line occurrences. It is simultaneously a
   strong structural signal and the most machine-extractable dossier on a private individual in the
   entire `law_practice` family. The node accepts it as a signal and refuses it as a source of
   entities, facts, prompt content or folder levels — in the same breath.
2. **The recording.** This is the only row in the family whose *primary* artefact set includes audio
   and video of a real person, which makes `00`'s clause live here and nowhere else in the family:
   *"Audio and video files should yield duration, container and codec metadata, creation time,
   embedded tags, subtitles or captions where present, and—only under an explicit privacy and compute
   policy—speech-to-text transcripts."* No transcription to improve classification.
3. **Cross-examination bridging.** One person may be examined in several unrelated matters. Joining
   those files by their name assembles a testimony history nobody asked for, so name-based bridging
   is suppressed as a *privacy* rule and not only as an accuracy rule.

## Files considered and rejected

Named because each is a tempting false positive, not because it is exotic.

- **A hearing or trial transcript** (`Transcript - Hartley v Nash - Day 4`). The primary collision;
  see below. Rejected on the bench line plus the missing errata slot.
- **An affidavit.** Identical first-person numbered prose to a witness statement, identical exhibiting
  convention — and a **notarial jurat** at the foot. A notarial block is `legal`'s own deterministic
  signal and `legal` is a safety domain. Rejected to `legal`; one block, whole different owner.
- **An investigation interview note.** One person's account of events, which is the entire surface
  similarity. Rejected on *who attested it*: the investigator wrote it, in the third person, no oath,
  no coordinates, and the interviewee never signed.
- **A published or training exemplar transcript.** Complete certificate, complete appearances, real-
  looking page-and-line body — and fictional parties and marginal teaching annotations. Rejected on
  purpose, which is the only test that works; topic cannot separate them at all. Routed to Reading
  Inbox and *not* to Protected Records, because uniquely among this row's fixtures there is no real
  person's testimony inside.
- **A reporter's or transcription service's invoice.** Kept as a `work_type` value, rejected as
  evidence: an issuer-and-billed-to structure is finance's on finance's own evidence, and this row
  does not claim it.
- **A recorded webinar, recorded client meeting or recorded interview.** Identical to a container
  sniffer. Rejected: `file_kind_plausible` is constitutionally never-alone, and the media joins
  through the delivery's transcript and certificate, never through its own bytes.
- **A deposition summary written as free prose with no coordinates.** Genuinely borderline; treated
  as `law_practice.trial-preparation`'s working material unless it is keyed to page-and-line.
- **A contacts export listing reporters, videographers and interpreters.** Rejected outright: a
  relationship role needs evidence in an examination, and a name list is the row's struck token.
- **An expert's report and instruction letter.** Rejected by artefact, not by person — see the
  reciprocal boundary below.
- **A statement taken under caution in a criminal matter.** Structurally in scope (attested, verbatim,
  person-anchored) but `law_practice.criminal-defence` may hold the surrounding file; left as a
  co-activation observation rather than an edge, because I could not establish a same-fixture
  contest at placeholder depth without inventing procedure.

## The collision fixture

`Transcript - Hartley v Nash - Day 4 - 2026-06-02.pdf`.

It has every surface signal this row relies on: reporter-produced, verbatim, `Q.`/`A.` prefixed,
line-numbered, page-numbered, certificate-shaped stamp, legal caption, a reporting company's cover.
A filename filter, a vocabulary matcher and a layout matcher all place it here, wrongly.

**What discriminates it:** a **bench line** (`BEFORE THE HONOURABLE …`) plus in-line rulings on
objections, and the **absence of an errata or read-and-sign slot** — because a court owns its record
and a witness cannot amend it. Both halves are needed: the bench line alone could be recited in a
deposition's caption, and an absent errata sheet alone could just mean the sheet was filed
separately. `law_practice.hearing-transcripts` is the home. Neither the word *transcript*, nor the
reporting company's footer, nor the presence of witness testimony inside decides anything — all three
are true on both sides.

A second, quieter collision is worth naming because it is invisible: the **same certified transcript
in the deponent's own corpus**. Nothing inside the file changes. This row's activation structure is a
third-role attestation, which says nothing about whose filesystem the file landed in, so activation
here settles no holder role — stated in `needs_llm` for that reason, and boundaried against
`legal.personal-legal-matters` on the *surrounding corpus*.

## Reciprocal boundaries

Each is authored as an object with the same fixture named on both sides.

| Neighbour | Shared fixture | This row owns | Neighbour owns | Discriminator |
|---|---|---|---|---|
| `law_practice.hearing-transcripts` | `Transcript - Hartley v Nash - Day 4` | officer's oath certificate; appearances with no judicial presence; errata/read-and-sign slot | bench line; in-line rulings; approved-transcriber reference; no errata slot | bench line **and** errata slot together |
| `law_practice.discovery` | `Notice of Deposition … with Schedule A` | demands aimed at a **named natural person** to attend and answer orally, schedule riding along | demands aimed at a **party** to answer in writing or produce; review log; privilege log; production set | direction and object of the demand; on exhibits, production range vs sticker-plus-coordinate |
| `law_practice.evidence-exhibits` | `Exhibit 12 - Lee depo - text messages.pdf` | the exhibit marked on one deponent, and that examination's internal index | a schedule spanning several examinations, or joining a depo series to a trial series | scope of the closing schedule, not the sticker |
| `law_practice.trial-preparation` | `Designations and counter-designations … .xlsx` | tables keyed to **transcript coordinates**; summaries keyed to page-and-line | bundle indexes, chronologies, outlines, running orders, cross-examination plans | what the rows address: a coordinate or a document/event |
| `law_practice.expert-materials` | `Deposition of Dr Mira Patel - Volume I.pdf` | the **examination** of the expert, on its certificate | instruction letter, report, materials-considered list, CV, correspondence | the artefact, never the person — the shared name is the least useful evidence in the pair |
| `law_practice.investigation` | `Investigation interview note - A. Okafor` | a record attested by the person whose words they are | the investigator's own summary, terms of reference, evidence log, findings | who attested the record; contested case → abstain |
| `legal` | witness statement vs affidavit | statement of truth / declaration signed by the maker | notarial jurat with seal and commission reference | one attestation block; `legal`'s safety posture runs first |
| `legal.personal-legal-matters` | `Deposition Transcript - Jordan Lee - Vol II` | practitioner-side matter artefact | the holder's own testimony in the holder's own proceeding | the surrounding corpus, never the transcript |

The `law_practice.discovery` entry restates that row's own cession from this side, which its memo
explicitly asked for: *"`law_practice.depositions-testimony` should state the cession back."* Done.

## Neighbours considered that did *not* get an edge

- `law_practice.matter-correspondence` — scheduling and re-noticing emails are correspondence in form
  and examination apparatus in purpose. No same-evidence contest: the deciding artefact is the notice,
  which this row already holds, so an edge would be decorative.
- `law_practice.pleadings`, `.motions-and-briefs`, `.orders-and-judgments` — a motion to compel a
  deposition and a protective order about one are argument and instrument respectively, and neither
  is confusable with a certified examination. Vocabulary overlap only.
- `identity.core-documents` — a deponent's identification exhibited during an examination is a
  co-activation, not a mutex. Recorded here for R1c rather than forced into `also_holds_with`.
- `career`, `finance` (from `must_consider_neighbors`) — the only genuine finance contact is a
  reporter's invoice, which is finance's on the issuer-and-billed-to structure and which this row
  does not claim. No contest, no edge.
- `medical.personal-health-records` — a deponent's medical history is elicited verbatim inside the
  transcript, but the transcript is not a health record and the health record is not testimony.
  Co-activation at most, and only when a real record is exhibited.

## `also_holds_with` — deliberately empty, with intent recorded

`also_holds_with` is **schema ↔ schema only** (CONNECTION §5) and this row is a template, so it stays
empty. The intent for R1c: `law_practice` ↔ `legal` co-activation is real and constant in this row's
material — a caption on a transcript cover, a notarial jurat on a statement, a sealed legend on an
exhibit. Every fixture that meets it carries `also_schema: "legal"` instead. `role_split` is empty
because no field exists to split.

## `proposed_fields` — one entry, an endorsement rather than a mint

`subject_of_record`, endorsing the existing `clinical_practice` proposal already adopted by `nonprofit`
and by the `law_practice` schema. This row is recorded as the **paradigm case** so R1c can weigh the
strongest instance rather than the average one: a deponent is compelled, is frequently a non-party
with no relationship to the holder, to the holder's client, or to the litigation, and the entire
artefact is that one person's verbatim words. `client` cannot hold them; `our_firm` cannot; `subject`
is a topic key, not a person. The row explicitly declines to mint `deponent`, `witness`, `examinee`
or `affiant` — four names for one concept that already has one — and asks that
`destination_eligible: false` live on the key rather than on each template.

`fields: []` and `dimension_order: []` under PR-6, as the schema requires.

## NEEDS-JOSEPH

1. **NJ-DEP-1 — the absorption seam, and the row's weakest joint.** The roster directs absorption of
   `law.witness-statements`, and the row performs it on the argument that a deposition and a signed
   witness statement are both *one named individual's own attested evidence, anchored on the person*,
   with the statement of truth standing where the oath certificate stands. The honest counter: a
   statement is **drafted by the practitioner** and only signed, so it is work product with a
   signature. Alternatives — (a) keep the absorption (this row's recommendation, because the
   attestation slot and person-anchor are what activation actually uses); (b) split statements into
   their own row (opposed: a document-type split); (c) route them to `law_practice.trial-preparation`
   (leaves the legacy id homeless where no hearing is in prospect).
2. **NJ-DEP-2 — the examination anchor has no key.** The primary grouping anchor is an *examination*
   (one person, one sitting, several volumes and media segments) and no canonical key names it. The
   row declines to mint `examination_id`, `deposition_id`, `proceeding_ref` or `transcript_id`.
   Alternatives — (a) an instance of the schema's `project` reuse at finer grain; (b) a grouping-only
   construct needing no key, which is this row's reading under PR-6; (c) a genuine gap. It must not
   be resolved by 36 template authors independently.
3. **NJ-DEP-3 — the period level.** The recommendation promotes the examination date above the schema
   default's period-last rule. If R1c judges that this contradicts `00`'s ordering sentence, the
   fallback is to drop the date level and let `version_family` and explicit volume markers carry the
   separation. The row does **not** ask for `time_first: true` under any reading.
4. **NJ-DEP-4 — the word index as a product-wide problem.** An artefact shipping a machine-readable
   concordance of the people named inside it is a category no design document addresses, and the same
   shape occurs on a privilege log, a bundle index and a transcript. Alternatives — (a) a corpus-wide
   rule that a concordance-shaped structure is never an entity source (this row assumes it and cannot
   enact it alone); (b) a P7 handling decision; (c) leave it per-row, which will produce eleven
   inconsistent versions.

## Cross-row recommendations for R1c (not edits — this row touched no other file)

- `law_practice.hearing-transcripts` should state the bench-line-plus-errata discriminator back from
  its side, in these words, or the pair will contest transcripts by vocabulary.
- `law_practice.investigation` should state the *who-attested-the-record* discriminator back, and
  should adopt the same abstention rule for a signed verbatim interview.
- The `law_practice` schema's `work_types` value `"witness statement, proof of evidence and deposition
  or hearing transcript"` bundles two rows' material into one enum value. Splitting it into a
  deposition/examination value and a hearing-transcript value would remove the strongest textual
  support for the charge against this row.

## Sources used

`planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment from
`planning/domains/dispatch/make_prompt.py`; `planning/00-database-agent-product-design.md` (targeted,
every quotation grep-verified verbatim before use); `planning/domains/roster.json` (every edge id
confirmed present); `planning/domains/nodes/law_practice.json` (the schema anchor and its default
template); `planning/domains/nodes/legal.practice-matter-file.research.md` (depth calibration);
boundary claims already written against this row in `law_practice.discovery.json`,
`law_practice.discovery.research.md`, `law_practice.evidence-exhibits.json` and
`law_practice.evidence-exhibits.research.md`.

## Self-verification

- `python3 -m json.tool` parses the node file.
- All eight `collides_with` ids confirmed present in `planning/domains/roster.json`.
- Every `source_type` in `file_examples` and `file_kinds` is in `SOURCE_TYPES`.
- Every `00` quotation grep-verified verbatim (exact-string `grep -c` = 1 for each).
- Four `falls_through_to` names are §7.3 residual names.
- `fields: []`; one `proposed_fields` entry, an endorsement of an existing key.
- `also_holds_with: []` (template row, CONNECTION §5); `role_split: []`.
- No threshold numbers, no handling classes, no invented ids, no folder paths as facts.
- Only the two assigned files were written.
