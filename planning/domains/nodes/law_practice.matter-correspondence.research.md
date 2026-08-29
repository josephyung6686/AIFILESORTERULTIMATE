# Research memo — `law_practice.matter-correspondence`

Depth: J-DEPTH
Date: 2026-08-26
Row: template on the `law_practice` schema, `parent_id: null`, `launch: placeholder`
Output: `planning/domains/nodes/law_practice.matter-correspondence.json`

## Result — REFUSED

`refuse_node: true`. "Matter correspondence and attendance notes" is a **medium plus a document type
plus the schema's own anchor**, and after those three are stripped nothing structural is left. Its
detection signals are the `law_practice` schema's deterministic signal 11 and needs_llm signal 5
restated; its `dimension_order` is the schema's empty order; its privacy posture is the schema's
third-party posture and is not stricter than the privilege-log rule the schema already carries. All
three legs of CONNECTION.md §2's node test return *identical to default*.

Refusing costs no coverage. The schema's first grouping reason already enumerates this material by
name, and the four correspondence classes that carry their own structure are already owned by
siblings that were given rows *for that structure*.

## The charge, stated at its strongest before anything else

The brief asks for the strongest case that the row should not exist. Here it is, and I could not
defeat it.

**It is a work_type value.** The `law_practice` schema's own `work_types` enum contains
`"client instructions, attendance note and matter correspondence"` and
`"counsel and third-party professional correspondence"`. My row's name is those two enum entries
concatenated. The schema wrote the enum precisely so this would not happen — its `work_type`
proposal says the enum is where document kinds belong, and that "a template row justified only by
holding a different legal document kind is the schema's default template with a narrower filename
filter."

**It is a medium.** Letters and emails are `text_document` and `email`. The schema strikes
"A SOURCE TYPE or EXTENSION ALONE, including text_document, email, archive…"

**It is a document type.** Attendance note, file note, telephone note, letter, memo — all
document-type words, and the schema strikes "A DOCUMENT-TYPE WORD, AND A DOCUMENT-TYPE WORD BESIDE
A FIRM OR CLIENT NAME."

**It is a drawer.** "Correspondence" is the name practitioners give a *section of a file*. A
directory name is an unlabelled position, not a fact — which is why the `Correspondence.zip` fixture
in the JSON is the refusal expressed as a single file.

**And the residue is defined by absence.** Strip medium, document type and anchor and what remains
is the attendance note: alone in this family it has *no labelled slot, no caption, no execution
block, no column set*. Its distinguishing property is that it lacks the structure every sibling has.
The charge lists "a row defined only by the ABSENCE of something" as a refusal ground, and this is
the textbook instance.

## The node test, argued in full

### The schema's default template, stated so the comparison is real

`law_practice` requires **both** legs before anything fires: (i) an exact matter, file or engagement
reference repeated across two or more artefacts, and (ii) at least one artefact whose own labelled
slots separate a practitioner or firm role from a client role. Its `dimension_order` is `[]` for
three independent reasons (contract under PR-6, safety co-activation with `legal`, disclosure by a
client-or-matter branch). Its `time_first` is `false` and it states that no sibling may claim
otherwise. Its sensitivity is `potentially_sensitive`, and its distinguishing privacy claim is that
it protects a third party "who never chose this filesystem and cannot consent."

### Leg 1 — detection signals. FAIL, and not narrowly.

The schema's deterministic list already contains, verbatim:

> "AN EMAIL or CALENDAR record whose structured slots tie it to an ALREADY EVIDENCED matter:
> labelled sender and recipient roles crossing the practitioner-client or counsel boundary, a
> subject carrying the exact matter reference, an organizer and attendee set separating
> practitioner, client, counsel and tribunal."

That is the correspondence half of my row, complete. And its needs_llm list already contains:

> "Recognising unlabelled practitioner prose - an attendance note, a file note of a telephone call,
> a strategy email in running text, a handwritten-then-scanned advice note."

That is the attendance-note half, complete, by name. I spent the research pass looking for a signal
the schema does not already carry and did not find one. The candidates I tested and rejected:

- *Direction across the practitioner/client boundary.* That IS the schema's second required leg.
- *A reply chain / thread identifier.* 00 grants that to every mail file regardless of domain:
  "EML, MBOX, MSG, and exported mail archives should yield sender, recipients, subject, sent date,
  thread identifiers, message body, attachment names, and reply-chain context, while treating
  addresses and message content as potentially sensitive." A universal extraction is not a node.
- *A matter reference in a subject line rather than a header.* 00's position weighting is real —
  "A course code or university name found in a filename, title, or page-one heading is more
  meaningful than the same text appearing once in a reference list on page eighteen" — but that
  weights an existing signal, it does not create a second one.
- *A "without prejudice" legend.* A legend is struck (the schema strikes without-prejudice
  explicitly), and where the offer traffic genuinely is the subject, `law_practice.settlement` has
  a structural anchor and I do not.

### Leg 2 — recommended dimensions. FAIL by contract, and the one difference is forbidden.

PR-6 leaves the schema fieldless, so `dimension_order` is `[]` on the default and `[]` here. Nothing
to compare.

The honest part is what happens if PR-6 lifts. The *only* order I could argue for is `time_first:
true`, and I think the practice argument is genuinely good: a correspondence file is a chronological
stream, practitioners read it forward, and a letter-book is ordered by date and nothing else. But
the schema forecloses it family-wide on 00's own words — "For document and record domains, project,
function, or subject usually comes before time because putting year first scatters related work
across calendar folders" — and adds that no sibling may claim the photos exception without the
photos evidence. So the one axis on which this row is not a duplicate is an axis it is not permitted
to occupy. I record that as a question for Joseph rather than smoothing it away (NJ-MC-3).

### Leg 3 — privacy rules. FAIL. Same posture, no new rule.

Correspondence bodies describe a third party's affairs — the exact interest the schema exists to
protect. But "more of the schema's own concern" is not "a different rule." The schema already
fixtures the privilege log, a table of thousands of *other people's* correspondence metadata, and
already states the bulk-sensitivity rule and the no-cloud-summary rule on it. A mail thread does not
exceed that. Sensitivity here is `potentially_sensitive`, identical to the default, and P7 owns
handling classes.

**Verdict: three legs, three identical-to-default results, one of them true three times over.**

## Bottom-up file set — nine real files, and what each one proves

The JSON carries the full observations, legal facts, prohibited conclusions and residual for each.
This memo records why each fixture exists — a refusal still has to show its working.

1. `RE 41127-0006 Hartley - your instructions on the without prejudice offer.eml` — the flagship.
   Every observation on it maps to schema deterministic signal 11 word for word. It is the proof
   that the schema already sees this file completely.
2. `Attendance note - telephone attendance on client 14.05.2026.docx` — free prose, no labelled
   slot anywhere. The absence fixture. It cannot supply the schema's required *structure plus
   labelled slot* and can only inherit membership from an anchor proved elsewhere — which is P9
   grouping, not template activation.
3. `Letter to Nash & Co - 41127-0006 - response to your letter of 2 May.pdf` — inter-solicitor
   letter. Shows that "correspondence with another professional" is signal 11's counsel boundary,
   and that the version of it which HAS a structure already belongs to a sibling.
4. `Scan_20260514_0003.pdf` — handwritten note, OCR'd, no reference, sitting beside matter files.
   The sparse-file case: it may join a candidate neighbourhood for review while nothing is written,
   because "The graph does not automatically copy those missing facts onto sparse files," and
   directory neighbours prove nothing — "A session should never be treated as proof of topic."
5. `Ellis and Co - letter re my divorce - 5 May.pdf` — the under-firing collision (below).
6. `Minutes - partners meeting 2026-05-14.docx` — the over-firing collision (below).
7. `Correspondence.zip` — the id's name appearing as a *directory* inside a matter export. The
   refusal in one file.
8. `Instructions to Counsel and enclosures - 41127-0006.pdf` — the structured correspondence that
   is already owned, by `law_practice.opinions-advice`, on the schema's three-slot signal 9.
9. `Employment law update - May 2026 - Ellis and Co.eml` — firm newsletter. Trips three tempting
   tokens at once (firm sender, legal vocabulary, regulated-profession footer) and is nothing.

The set covers labelled structure, unlabelled prose, OCR of handwriting, a mail archive manifest,
an inter-professional letter, two collisions in opposite directions, and a public-reading item.

## The collision fixture — and its mirror

The brief asks for one file that looks like my evidence and is not. This row has two, and they fail
in opposite directions, which is itself part of the refusal argument: a row named for a *medium*
cannot discriminate either one, because the medium is identical on both sides.

**Under-firing — `Ellis and Co - letter re my divorce - 5 May.pdf`.** Firm letterhead, a matter
reference allocated by that firm, a client recipient, professional prose. Every token a
correspondence row would key on is present, and the holder is the **client**. The discriminating
evidence is which side the holder is on and where the practitioner-side apparatus is — no time
record, no intake screen, no work product produced by the holder anywhere in the corpus.
`legal.personal-legal-matters` owns it, and `legal` is a safety domain whose protection runs first.

**Over-firing — `Minutes - partners meeting 2026-05-14.docx`.** A note of a meeting, produced by
lawyers, on law-firm letterhead. Every word of my row's name is satisfied. It is
`business_operations.meeting-record`'s file, because the subjects are the attendees themselves and
the firm is running *itself*. Discriminator: an exact matter reference plus a client role; neither
is present. The schema states this seam as needs_llm 4.

## Files considered and rejected as this row's evidence

- **`Client care letter - 41127-0006.pdf`** — it is a letter, it is addressed to a client, it is
  correspondence by any English reading. It is `law_practice.engagement-terms`', because it has
  labelled scope, rate, complaints and cancellation sections. Structure beats medium.
- **`Letter before action - Hartley to Nash.pdf`** — a letter with a demand, a deadline and a
  statement of claim. The pre-action structure is `law_practice.pleadings`'-adjacent; nothing about
  it being *a letter* routes it here.
- **`Instructions on opening - client email of 3 April.eml`** — first instructions arriving by
  mail. `law_practice.client-intake` owns the opening moment; my row would have taken it purely
  because it arrived as an `.eml`, which is the medium error in its purest form.
- **`Offer letter - without prejudice save as to costs.pdf`** — `law_practice.settlement`.
- **`Notice of Electronic Filing - Motion to Compel.eml`** — a court-system email.
  `law_practice.court-filing-record`. Mail is the carrier, the docket event is the artefact.
- **`Hearings and depositions.ics`** — a calendar file with matter attendees. Deliberately not
  claimed: it is the calendar half of signal 11, and `law_practice.deadlines-diary` has the
  portfolio-table structure that actually distinguishes something.
- **`Contacts export - matter contacts.vcf`** — `contacts` source type naming client, counsel,
  expert and court. Not activated by names. The schema strikes a person's name alone as
  simultaneously "the least discriminating evidence and the most dangerous."
- **`Matter Time and Billing - Acme Holdings.xlsx`** — narrative columns are prose about a client
  and read like correspondence in miniature. `law_practice.time-and-billing` on the column set;
  `finance` on an issuer-and-billed-to structure. Not mine on either reading.

## Reciprocal boundaries — stated in both directions, same fixture bytes on both sides

Because I refuse, these are boundaries the **`law_practice` schema** now holds directly. I state
them so R1c can see the seams are covered rather than dropped, and so no later author reopens this
id to hold them.

| Neighbour | Toward the neighbour | Toward `law_practice` (schema) | Shared fixture |
|---|---|---|---|
| `business_operations.meeting-record` | a meeting-shaped file whose subjects are the attendees themselves; a firm's own partnership, lease, hiring or billing-target meeting | an exact matter reference **plus** a client role in the artefact's own labelled slots — the schema's needs_llm 4 seam | `Minutes - partners meeting 2026-05-14.docx` |
| `legal.personal-legal-matters` | the holder is the addressee and the client; no practitioner-side apparatus exists in the corpus | the holder's firm allocated the reference, and an intake screen, time record or work product produced by the holder exists | `Ellis and Co - letter re my divorce - 5 May.pdf` |
| `law_practice.opinions-advice` | a front sheet pairing an INSTRUCTING block with an INSTRUCTED block, plus a named advisee — a three-slot structure | ordinary practitioner-client mail with no second professional role labelled | `Instructions to Counsel and enclosures - 41127-0006.pdf` |
| `law_practice.settlement` | without-prejudice offer traffic anchored by a settlement structure or an executed instrument | a legend alone, which is struck as never-alone on both sides | `RE 41127-0006 … without prejudice offer.eml` |
| `law_practice.client-intake` | the opening moment — first instructions, identification, matter allocation | mail after the matter is already evidenced | `Instructions on opening - client email of 3 April.eml` |
| `career.consulting-client-engagement` | prepared-for / prepared-by consulting roles, milestones, acceptance | explicit counsel, representation, legal-services or legal-work-product structure | an engagement letter between two organisations |

**Reciprocity debt I cannot discharge myself.** `business_operations.meeting-record` names this id
one-way, in its JSON (`"An attendance note of a client or counsel meeting is a meeting record inside
a legal matter…"`) and again in its memo's boundary table. That edge now dangles. I may not edit a
neighbour's file, so this is a **recommendation to R1c**: re-point it at the `law_practice` schema,
whose needs_llm 4 already states the identical seam from the other side. The discriminating evidence
that row names — "a matter or file reference, a client identifier, or a privilege marking" — needs
one correction when it moves: a privilege marking is struck as never-alone by the schema, so the
surviving discriminator is the reference plus a labelled client role.

## Where the coverage goes

The row absorbed no legacy id that is left homeless. Routing, with the schema's own words:

- **Correspondence and notes inside an evidenced matter → the `law_practice` schema itself.** Its
  first grouping reason already names them: "ONE MATTER from opening to closure, joined by an exact
  repeated matter reference: the intake screen, the opening record, the engagement terms, **the
  correspondence**, the work product, the filings, the disclosure, the billing and the closure
  record." That group is licensed by 00's purpose clause — "The documents are content-incoherent but
  purpose-coherent" — and membership copies no fact onto any member.
- **Structured correspondence → the four siblings named above**, each on a structure I do not have.
- **No anchor at all → residuals.** `Protected Records` once any accepted matter group is active;
  `Review Later` for readable professional prose whose side or matter is unresolved;
  `Reading Inbox` for firm newsletters, commentary and published material; `Unsupported or
  Encrypted` for locked mail archives and unreadable exports. 00 licenses protection without a
  group: legal documents "may be surfaced as protected records even when they do not meet a normal
  group-size threshold."
- **Abstention is a legitimate outcome and I am relying on it deliberately:** "Correct abstention is
  a successful outcome because the product's goal is reliable organization, not maximum file
  movement," and "A model that cannot cite sufficient evidence must return unknown."

## proposed_fields

**Empty, deliberately.** PR-6 leaves the schema fieldless and a refused template proposes nothing.
The schema already carries the six proposals this world needs (`client`, `our_firm`, `project` as
the declined-to-mint matter anchor, `work_type`, `subject_of_record`, `fiscal_period`) and argues
each. Candidates I explicitly declined to raise, so no later author reads silence as an opening:
`correspondence_direction`, `sender_role`, `recipient_role`, `thread_id`, `note_type`. The first
three are `client`/`our_firm` respelled; `thread_id` is a universal mail extraction 00 already
grants every domain; `note_type` is `work_type`.

## Sources used

`planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment from
`planning/domains/dispatch/make_prompt.py`; `planning/domains/nodes/law_practice.json` (the schema
anchor — the decisive document, read in full through its file-example set);
`planning/domains/nodes/legal.practice-matter-file.research.md` (depth calibration and the
practitioner/personal seam); `planning/domains/roster.json` (every edge id verified present);
`planning/domains/nodes/business_operations.meeting-record.{json,research.md}` (the only landed row
that names this id — located by one grep). Every span in quote marks attributed to
`planning/00-database-agent-product-design.md` was grep-verified verbatim before it was written;
spans attributed to `law_practice.json` are quoted from that file directly.

## NEEDS-JOSEPH

- **NJ-MC-1 — reciprocity debt.** `business_operations.meeting-record` names this refused id in two
  places. Re-point it at the `law_practice` schema (needs_llm 4) and drop "privilege marking" from
  its discriminator list, since the schema strikes that label as never-alone. R1c action; I may not
  edit that file.
- **NJ-MC-2 — re-test after PR-6.** If PR-6 lifts and `project` is adopted as the matter anchor,
  run this node test once more rather than assuming it. Expected answer unchanged — a correspondence
  row would still be a `work_type` value — but the test should be executed, not inherited.
- **NJ-MC-3 — the chronology question, surfaced not smoothed.** A correspondence stream is the one
  artefact class in this family that is genuinely time-ordered in practice, and the schema bans
  `time_first` family-wide on 00's document-and-record rule. Alternatives: (a) keep the blanket ban
  and accept that a letter-book is filed by function; (b) permit a period level *below* an anchor
  level for stream-shaped members only; (c) leave it to the user, since "the user can reverse,
  remove, add, or flatten dimensions." This is a question about the schema, not about this id, and
  it is the only argument this row had that the schema does not already make.
- **NJ-MC-4 — residual for the unanchored attendance note.** A handwritten note of a call, with no
  reference, in a matter neighbourhood: `Protected Records` is protective but files an unproven
  association; `Review Later` is honest but leaves third-party prose outside the protected set. I
  recommend `Review Later` while unanchored and `Protected Records` once any accepted matter group
  is active, and flag that the two have different safety consequences for a person who is not the
  holder.

## Final recommendation

Keep `law_practice.matter-correspondence` refused. Do not resurrect it under a rename
(`matter-communications`, `client-correspondence`, `attendance-notes` are the same row). If a future
author believes this world needs a correspondence node, the bar is a *structure* no sibling has —
not a medium, not a document type, and not a drawer.
