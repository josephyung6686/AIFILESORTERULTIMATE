# creative.journalism-reporting — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: creative`, `launch: placeholder`, `parent_id: null`.
Output: [`creative.journalism-reporting.json`](creative.journalism-reporting.json).
Salvage: none — no prior draft of either file existed. Both files are new and owned by this pass.
Verdict: **node accepted**, on limbs one and three of the node test, with limb two conceded in
the open. `fields: []`. Two `proposed_fields`, one of which is a prohibition rather than a request.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped assignment
  (`make_prompt.py creative.journalism-reporting`) — the six depth requirements, the row metadata,
  `must_consider_neighbors` (`career`, `code`, `photos`), `must_consider_residuals` (Independent
  Records, Review Later), `inherited_field_keys: []`.
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted `grep -n` rather
  than streamed. **Every span in quote marks in both files was re-matched mechanically against it**
  — 23 spans, 23 exact matches, two corrections applied to get there (audit at the end).
- `planning/domains/nodes/creative.json` — the schema anchor this row is measured against. Read as
  structured extraction, not streamed. It declares **no field rows**, an **empty**
  `dimension_order`, and holds its default template as prose.
- `planning/domains/nodes/creative.book-manuscript.json` — the one landed row that had already
  argued a boundary against this id (one `grep -rl`). Its `also_holds_with` names this row and
  names the fixture; the edge is mirrored here with the same fixture.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the depth calibration named in the
  brief, read for structure and idiom.
- `planning/domains/roster.json` — every edge endpoint confirmed against `domain_id`.
  `government.public-records-foi` was found here, which is why the obtained-records boundary is
  argued against a real row rather than hand-waved at "government".
- `planning/domains/canonical_fields.json` — the 37 keys, all checked before anything was proposed.
  **No key was minted.** `people` already exists, which changed the shape of this row's privacy
  claim (below).
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — every `source_type` checked mechanically.

Not read, deliberately: other R1b rows "for context", and the `clinical_practice` /
`business_operations` / `construction_property` memos, which the brief classes as debt.

---

## THE CHARGE — the strongest case that this row should not exist

I put six attacks to the row before writing anything. Four of them are serious and two of them
nearly killed it.

**1. It is an occupation, not an organizational situation.** "Journalism" names who the person is,
and the 574's recorded failure was exactly this: professions dressed as filing worlds. A reporter's
disk is a writer's disk. — *The attack the row must beat, and beating it requires naming a
STRUCTURE, not a job.*

**2. It is a work_type value.** The `creative` schema's enum already holds `manuscript draft`,
`transcript` and `script`. An article is a short prose work; a reported article is a short prose
work about a fact. `work_type = article` does the whole job in a slot that already exists. —
*Serious.*

**3. It is a duplicate of neighbours, decomposing without residue.** The pitch is
`creative.creative-brief`; the drafts `creative.short-form-writing`; the recordings
`creative.podcast-episode`; the published piece `creative.periodical-issue` or
`career.portfolio-work-samples`; the obtained records `government.public-records-foi` or
`legal.practice-matter-file`. Every member has a better home and the row is a bag. — *The most
nearly fatal attack.*

**4. It is defined by the ABSENCE of something.** The roster hint states a prohibition: "the source
material must not be filed like the output." A rule saying *do not put these on the same level* is
a constraint on somebody else's template, not a node. — *Half right; this is why limb two is
conceded rather than argued.*

**5. It is an organisation name.** Guardian, ProPublica, a masthead — never-alone evidence, and 00
forbids an institution name as sole proof. — *Correct, and it sits on `never_alone` as the row's
commonest false positive. It is not what the row activates on.*

**6. It is a medium or a length.** Longform vs shortform, print vs broadcast. — *Correct and
conceded; none of them appear anywhere in the row's recognition.*

### The defence — three structures, none of which is a job title

The row survives only if it can name evidence that is present in this world and **absent from the
`creative` schema's own default detectors**, which are: linked-asset structure, layer/artboard
structure, revision-round structure, brief structure, delivery/handoff structure. Every one of
those is about an **authored working file**. That is the gap.

**(a) THE OBTAINED-RECORDS STRUCTURE.** A covering letter naming a disclosure statute and a
request reference number, followed by a bundle of documents the corpus owner plainly did not
author — other letterheads, other signatures, scan-origin pages that are OCR-only, visible
redaction. Run the schema's five detectors over `FOIA 2026-0412 response - City Water Dept.pdf`:
no linked assets, no layers, no revision family, no deliverables-and-deadline brief, no export
stem set. **Zero of five fire.** A schema whose detectors are all about making has no detector at
all for material that was *got*. That is not a work type and not an occupation; it is a shape.

**(b) THE ATTRIBUTED-CAPTURE RUN.** Not one named recording — a *run* of recordings whose stems
each pair a **different** person's name with a date and a role token, converging on one shared
non-person slug elsewhere in the folder. This distinction is what defeats attack 3's podcast
branch: a podcast episode interviews one person about several things; a story interviews several
people about one thing. The plurality-of-names-against-singularity-of-slug is a real, checkable
structure and no sibling has it.

**(c) THE VERIFICATION APPARATUS.** A table whose columns pair **assertions** with **citations**
and a small status vocabulary, whose rows reference a same-slug draft by paragraph. This is a
document whose structure *is the work indexed against its own evidence*. `research.manuscript-
publication` has a bibliography, which cites sources but does not enumerate claims;
`creative.book-manuscript` has notes and an apparatus, and that row already conceded the overlap
to this one. Nothing in `creative` files a claim-by-claim check.

**Against attack 2 specifically:** `work_type = article` describes the OUTPUT. None of (a), (b) or
(c) is an output. The row is not the article; it is the article plus everything that was obtained
to make it, held together against the format incoherence that would otherwise scatter it. 00's own
words for this shape are about applications, and they transfer exactly: "The documents are
content-incoherent but purpose-coherent. A content-similarity system will tend to split them; a
human may intentionally keep them together because they were submitted as one application
package." Substitute *story* for *application package* and that is this row's entire grouping
claim.

**Against attack 3 specifically:** the decomposition succeeds member by member and fails on the
set. Each neighbour can take one member and none can take the relation. `creative.short-form-
writing` would take the draft run and treat the recordings as attachments of a piece of writing —
which is precisely the filing the hint forbids. `government.public-records-foi` would take the
bundle from the authority's side. Nobody is left holding the fact that a `.m4a`, a `.xlsx`, a
scanned `.pdf` and a `.docx` are one thing. That relation is the node.

**Against attack 1 specifically:** none of (a), (b) or (c) mentions a journalist. A public-health
NGO's investigator, a due-diligence analyst and an academic oral historian produce the same three
structures, and this row would correctly claim their material. The row is named for the commonest
occupant of a shape; it activates on the shape.

---

## The node test, all three legs

CONNECTION.md's test: a template row exists only where its **detection signals**, its
**recommended dimensions**, or its **privacy rules** differ from its schema's default template.

### Leg 1 — detection signals: **DIFFERS.** Accepted.

The `creative` default template, held as prose on `creative.json`, detects **linked assets,
layers/artboards, revision rounds, briefs and delivery sets**. This row's three primary detectors
— obtained-records structure, attributed-capture run, verification apparatus — are absent from
that list, and the fixture test above (five detectors, zero fire) is the demonstration rather than
the assertion. Two further detectors are *narrowings* rather than novelties and are flagged as
such in the JSON: the slug-and-placeholder structure narrows the schema's revision-round detector
by requiring the stem to cross a **format** boundary (a `.docx` run bound to an `.m4a` set), and
the embargo structure narrows the schema's delivery detector by requiring a stated release moment
in the **future**. A row resting only on those two narrowings would be a degree difference and I
would have refused it. It rests on the three absences.

### Leg 2 — recommended dimensions: **CONCEDED.** Not expressible.

The `creative` schema declares no field rows, so `dimension_order` is `[]` on the anchor and must
be `[]` here — _CONTRACT rule 8: "a template may only branch on a field the same entry's schema declares"
(_CONTRACT rule 8, D6). In the literal contract sense this row **cannot** differ on dimensions,
and I say so in `template.why` rather than dressing prose as a difference.

What is recorded for R1c is that the prose recommendation genuinely is not the default. The
default is `client → project → stage → artifact_type`. This row recommends **project (the story)
first, then a split on the PROVENANCE of the material, with `stage` demoted beneath the authored
branch only.** The reasoning is 00's own parent-context test — "a parent dimension should provide
the context required to understand the child" — and it cuts the opposite way here from everywhere
else in the family. `Round 2` is unintelligible without the project, which is why `stage` sits
under `project` on every sibling. But an interview recording and a draft are **not two stages of
one thing**: one is input, one is output. Putting them on a shared `stage` level files a source's
recording as though it were a revision of the story. That is attack 4's prohibition turned into a
positive recommendation, and it is why the row asks for `material_role` rather than asking for a
rule that forbids something.

Not time-first, and for a reason specific to this world rather than the generic one: a story's
material is *chronologically incoherent*. The records request was filed months before the
interview, which happened after the draft was started, which was published weeks later. 00: "For
document and record domains, project, function, or subject usually comes before time because
putting year first scatters related work across calendar folders."

### Leg 3 — privacy rules: **DIFFERS IN KIND.** Accepted, and this is the strongest leg.

The `creative` schema's posture protects **unpublished work** — a campaign before launch, a
manuscript before submission, a cut before release. That protection **expires at publication**.
Here it **inverts**: publication is the moment the source material becomes most dangerous, because
that is when the people named in it become findable, and it never expires. Three operational
consequences follow that no sibling needs:

1. **The filename is the sensitive value.** `Interview - <person> - <date>.m4a` discloses a source
   before any interior is read. 00 keeps paths local — "Paths, complete extracted text, OCR output,
   file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should
   remain local" — and Protected Records repeats it as "must not cause filenames or content to be
   exposed in model prompts". For every other creative sibling the filename is the *cheapest safe
   signal*; here it is the payload.
2. **Transcription is an act, not a read.** For most of this corpus, speech-to-text is the only
   way to see inside, and 00 gates it: transcripts are yielded "only under an explicit privacy and
   compute policy". The correct default here is an opaque, indexed, unread file.
3. **The error is irreversible.** "Revocation cannot necessarily retract data already sent to an
   external provider, so the product must communicate that distinction clearly." A leaked campaign
   is embarrassing; a burned source may be unemployed or prosecuted, and the maker cannot consent
   on their behalf.

The row does **not** claim `is_safety_domain` (that stays with 00's four) and assigns no handling
class (P7's vocabulary).

---

## Files considered and rejected

Named tempting false positives, and why each is not this row's evidence.

- **`Guardian_opinion_2024-11-03.pdf`, saved by a reader.** Masthead, byline, dateline, column
  layout — every surface feature of this row's published fixture. It is somebody else's article,
  saved to read. → **Reading Inbox**: "papers, articles, reports, and saved PDFs that appear to be
  reading material but have no active research, course, or project association." This is why an
  outlet name is on `never_alone`: a reporter's disk holds far more *saved* journalism than *made*
  journalism, so the masthead detector would be wrong far more often than right.
- **`interview prep - Acme PM role.docx`.** Contains `interview`, contains a named organisation,
  contains questions. It is about *being* interviewed. → `career.recruiting`.
- **`Ross, Alan - resume.pdf`.** A person's name in a filename, which is this row's densest
  evidence type and is worthless alone. → `career.recruiting`.
- **`2026-03-04 Weekly Standup transcript.txt`.** Kept as a *file example* rather than merely
  rejected, because it is the second collision fixture: speaker labels and timecodes, identical to
  an interview transcript. Discriminated by apparatus and cadence — agenda, attendee roster,
  action items with owners, a seven-day interval. → `business_operations.meeting-record`.
- **A redacted bank statement.** Black bars are the surface of the obtained-records detector.
  Redaction proves sensitivity, never provenance. → `finance` / Protected Records.
- **`Voice Memo 47.m4a`.** An audio file with a creation time and nothing else. No name, no run,
  no slug. The extension proves nothing — 00: the engine "should treat the file extension as a
  routing signal rather than an assumption about meaning". → Review Later, or left in place.
- **An afternoon of news PDFs downloaded in one session.** The tempting inference is "research for
  a story". 00 forbids it: "A session should never be treated as proof of topic, and it should not
  carry the same confidence as a hash match or a directly extracted document fact." → Reading Inbox.
- **A press release from a company's comms team.** Embargo language, an outlet-shaped addressee, a
  contact name and number. It is *received* marketing, not obtained material. → Reading Inbox, or
  `creative.content-marketing` from the sender's side.
- **A subscriber's clippings folder of their own bylines and nothing else.** No working files, no
  material set, ordered for showing. → `career.portfolio-work-samples`, argued reciprocally below.

## THE COLLISION FIXTURE

**`Interview - Dr. Alan Ross - 2026-01-18.m4a`.**

Byte-for-byte and stem-for-stem indistinguishable from this row's primary fixture: a person-shaped
name, an ISO date, the role token `Interview`, an `.m4a` container, duration and creation-time
metadata, no readable interior. There is **no signal on the file itself** that separates them.

What discriminates it is the neighbourhood, and specifically whether the named identity appears in
a **published** artifact. Beside this file sit `episode_047_master.wav`, `ep047_shownotes.md` and
`cover_art_ep047.png`; the guest's name is inside the show notes. The identity is the **product** —
it is put on the artwork on purpose. In this row's case the identity appears only in working
material and the published piece either omits it or generalises it ("a city engineer who asked not
to be named"). So the two rows want **opposite** things from the same evidence: one publishes the
name, the other exists to withhold it. That is why this is a `collides_with` and not an
`also_holds_with`, and why the discriminator sits in `needs_llm` and not in `deterministic` —
nothing deterministic can settle it, and pretending otherwise would be the dangerous kind of
confidence. It is carried in the JSON as a full `file_examples` entry so the ambiguity is visible
in the fixture set, not only in prose.

## Reciprocal boundaries

Each states the boundary in both directions and names the same fixture on both sides.

| Neighbour | Shared fixture | This row claims it when | The neighbour claims it when |
|---|---|---|---|
| `creative.podcast-episode` | `Interview - Dr. Alan Ross - 2026-01-18.m4a` | inside an attributed-capture run converging on a non-person slug, with obtained material or a fact-check present | an episode-numbered master, show notes, cover art or a feed export publishes the guest's identity |
| `creative.short-form-writing` | `vega-water-01_draft_v4.docx` | an obtained material set resolves the same slug | the corpus is entirely authored — drafts, marks, export |
| `creative.creative-brief` | `pitch - lead pipes - Vega.docx` | it is the head of a material set that already exists | it is a standalone commissioning instrument with deliverables and a deadline |
| `career.portfolio-work-samples` | `Guardian_lead-pipes_published_2026-05-02.pdf` | the slug binds it to a draft run and a fact-check | it sits in a curated set of finished pieces with no working files, beside a resume or clips list |
| `creative.periodical-issue` | same PDF | the neighbourhood holds ONE byline and one slug | the neighbourhood holds MANY bylines, a flatplan, a contents list |
| `government.public-records-foi` | `FOIA 2026-0412 response - City Water Dept.pdf` | requester-side, resolved by a slug/draft/fact-check | authority-side: the request log, the exemption reasoning, the response as an administrative act |
| `legal.practice-matter-file` | the redacted pages in that PDF | a story slug and an authored output are present | a matter reference, parties, a court identifier, correspondence between representatives |
| `business_operations.meeting-record` | `2026-03-04 Weekly Standup transcript.txt` | one date, two voices, one asking, no apparatus | agenda + attendee roster + action items + recurring cadence token |
| `photos.scanned-documents` | `IMG_4471.HEIC` | OCR content resolves against a request reference or slug already present | scanner/capture-origin evidence and the repeated-frame structure — and its capture facts are never dropped |

Neither direction is permitted to strip the other's facts. `photos` keeps EXIF, GPS and camera
information on `IMG_4471.HEIC` whatever this row concludes; this row does not manufacture a story
from a hand-held photograph of a sheet of paper.

**`also_holds_with`**, where a file legally carries both rather than competing:

- `creative.book-manuscript` — **mirrors the edge that row already wrote against this one**, using
  the fixture it named: `Interview - Marisol Vega - 2026-03-04.m4a`. Disjoint evidence (compile
  container + chapter run + book apparatus | attributed-capture run + obtained records +
  fact-check + outlet relationship). That row frames the protective difference as *sources who
  spoke under an expectation* versus *subjects who never took part at all*; this row accepts the
  framing and adds only that where a file is both, the **stricter posture governs**. Their NJ-BM-1
  flags that the two postures may be indistinguishable; my NJ-JR-5 answers it from this side.
- `legal` — source agreements, contributor contracts, a pre-publication legal read, a
  right-of-reply letter, a correction demand. On the `creative` schema's own `also_holds_with`, so
  this is inherited and narrowed, not a widening.
- `photos` — likewise inherited, narrowed to `IMG_4471.HEIC`.

## Neighbours considered that did NOT get an edge

- **`code`** (named in `must_consider_neighbors`). Data journalism produces notebooks and scrapers,
  but there is no competing fixture: a `.ipynb` with imports and a repo marker is
  `code.notebooks-experiments` outright. Where a scraper's **output CSV** becomes a story dataset,
  `code` claims the notebook and this row claims the export — they never want the same bytes.
- **`research.project-workspace` / `research.reading-library`.** Both worlds gather other people's
  documents. Rejected: the research rows are discriminated by a protocol, a dataset and a
  bibliography-keyed citation apparatus, and the real overlap (background reading) is a *residual*
  question that goes to Reading Inbox from either side. Handled by the fallthrough, not an edge.
- **`creative.client-engagement`.** The outlet relationship is genuinely a client engagement, but
  it is not a competition — this row's `role_split` already carries `client`/`our_firm` and the
  engagement row operates a level up, across several stories.
- **`identity.core-documents`.** An obtained bundle can contain a third party's ID scan. Rejected
  deliberately: this row must never *claim* such a page, it must route it, which is what Protected
  Records is for. An edge would have read as a claim.

## proposed_fields — justification

Two entries, and only one of them is a request.

1. **`material_role`** (enum: `obtained` | `authored` | `published`) — the axis the row's whole
   dimension recommendation needs. I checked all 37 canonical keys before proposing. `work_type`
   and `record_type` answer *what a document is* and both an interview transcript and a draft are
   legitimate values of either, so neither separates them. `stage` answers where the *work* is in
   its revision history and is orthogonal — a recording and a published piece can both be final.
   `purpose` answers what a file was *for*, and both halves are for the same story. `artifact_type`
   describes the output. **Strictly contingent:** while `creative` declares no field rows this key
   cannot be declared or branched on, so it is filed for R1c against option (b) of NJ-R1a-1, not
   requested now.
2. **`people` — a PROHIBITION, not a mint.** `people` is already canonical and is exactly the key
   an extractor would reach for here, because named people are this corpus's densest evidence: a
   source in a recording stem, a signatory on an obtained record, a name beside a phone number in
   a notes file. It must **never** be destination-eligible on this row. A folder named for a
   confidential source publishes that source to anyone who opens the disk, to every backup, and to
   any future dossier that carries paths. I record it in `proposed_fields` because there is no
   other slot in the entry shape for a negative claim about an existing key; R1c should record the
   prohibition and not the field.

No other key was proposed and none was minted.

## Recommendations to R1c (cross-row — this pass changed no neighbour file)

1. `creative.book-manuscript` already names this row in `also_holds_with`; the edge is now
   reciprocated with the same fixture. No change needed there, only confirmation.
2. The nine neighbours in the table above should, when they land or are revisited, use the **same
   fixture names** in their reciprocal wording.
3. If NJ-JR-4 resolves toward option (b), the `people` prohibition belongs on `creative.json` and
   should be dropped from this row's `proposed_fields`.

## NEEDS-JOSEPH

- **NJ-JR-1 — limb two is conceded and the provenance level is unexpressible.** The row's only
  dimension claim needs `material_role`, which needs `creative` to declare fields at all.
  (a) keep the row on limbs one and three and hold the recommendation as prose, as written;
  (b) if option (b) of NJ-R1a-1 lands, adjudicate `material_role` as a template-level key;
  (c) decide the obtained/authored split is a residual-routing rule rather than a dimension, in
  which case Protected Records carries it and the template says nothing.
- **NJ-JR-2 — the podcast discriminator is an LLM judgement, not a signal.**
  `Interview - <name> - <date>.m4a` is byte-for-byte ambiguous. (a) accept the LLM judgement with
  abstention as the default, as written; (b) make the attributed-capture RUN a hard precondition so
  a single named recording can never activate this row; (c) route all lone named recordings to
  Protected Records unconditionally and let the user pull them back. (c) is the safest and the most
  annoying; my own inclination is (b), but the safety argument for (c) is not weak.
- **NJ-JR-3 — who owns the obtained bundle.** `government.public-records-foi` and
  `legal.practice-matter-file` both have real claims on the FOIA fixture. This row's discriminator
  is requester-side-with-a-story, which is a claim about *context*, not about the document. If
  either of those rows asserts an unconditional claim, this row narrows: the obtained-records
  detector drops from `deterministic` to `needs_llm` and the node then rests on the
  attributed-capture run and the verification apparatus alone. It would still survive, but less
  comfortably.
- **NJ-JR-4 — is `people` prohibited here or everywhere?** The same argument plausibly applies to
  `creative.commissioned-shoot` (model releases), `creative.film-production` (cast lists) and
  `creative.theatre-production`. (a) record it on this row only; (b) raise it to the `creative`
  schema, binding all 41 siblings; (c) treat it as a P7 handling question, out of scope here. This
  row does not decide it.
- **NJ-JR-5 — the overlap with `creative.book-manuscript`'s NJ-BM-1.** That row flagged that its
  subject-protection argument may be indistinguishable from this row's source-protection argument.
  My position: they are distinguishable — a source *chose* to speak under an expectation and can
  therefore be betrayed; a subject never took part. But that is an **inference** from the material,
  not a design quote, and I mark it as such. If R1c judges them the same, this row keeps the node
  on limb one and the inversion argument in `sensitivity_why` reduces to the strongest instance of
  an inherited posture rather than a difference in kind. The node survives either way.

## Self-verification

- `python3 -m json.tool` parses; key set matches `creative.json` exactly (checked programmatically,
  including `proposed_context_terms`, which the anchor also carries).
- All 23 quoted spans re-matched mechanically against `00`. Two failures were found and fixed: the
  audio/video sentence had been reproduced with hyphens where `00` uses em dashes (split into two
  shorter exact spans), and "Correct abstention…" had a straight apostrophe where `00` has a curly
  one. One illustrative construction that had been sitting inside quote marks — an anonymisation
  line — was de-quoted and labelled. No paraphrase is presented as a quote anywhere.
- Checked programmatically: every `source_type` is in `SOURCE_TYPES`; every edge id resolves to a
  `domain_id` in `roster.json` (9 collisions, 3 co-holdings, 1 role split); every residual name is
  one of 00's nine.
- `fields: []` as required for a placeholder row. No canonical key minted. No threshold number, no
  confidence score, no handling class, no folder path written as a fact.
- Thirteen file examples, two of which are collision fixtures carried as examples rather than only
  described. Every one splits observations from facts. Four are marked
  `group_without_copying_facts: true` — the sparse recording, the photographed document, the source
  list and the archive — which is the `HW 3.pdf` discipline applied to this world.
- `never_alone` entries are true of tempting false files: the outlet-name entry trips
  `Guardian_opinion_2024-11-03.pdf`, the person-name entry trips the collision fixture.
- Files written: exactly the two assigned. No neighbour node, roster, canonical_fields, check.py,
  `src/` or SPEC was touched.
