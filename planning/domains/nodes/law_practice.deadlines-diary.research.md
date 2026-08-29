# Research memo — `law_practice.deadlines-diary`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.deadlines-diary.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, placeholder launch

## Result

**REFUSED.** `refuse_node: true`. There is no deadlines world to file.

The row fails all three legs of CONNECTION.md §2's template test, and it fails them against its own
schema anchor rather than against a distant neighbour — which is the strongest form of failure
available, because the evidence is a file I was required to read anyway.

The refusal costs no coverage. Unlike a refusal that orphans an artefact family, every file this row
would have held is already held: by `law_practice`'s own fifth deterministic signal, by
`law_practice`'s own fourth file fixture, and by the schema's default template. Nothing needs to move
and no sibling needs to absorb anything. That is stated up front because it is the fact that made the
refusal easy rather than agonising.

## The charge, stated at full strength before any defence

The brief asks for the strongest case that this row should not exist. Six independent cases were
available and five of them land.

1. **It is a `work_type` value.** `law_practice.work_types` — twenty-four values on the anchor —
   already contains, in these words, `"limitation, listing and key-date diary"`. The schema
   enumerated this row as a value of `work_type` before this row was researched.
2. **It is a value set *inside* a value.** Below the artefact, `limitation`, `service`, `response`,
   `listing`, `hearing`, `completion` and `filing` are an enum inside one spreadsheet column. The row
   is a value nested in a value.
3. **It is a lifecycle-stage / attribute row.** A deadline is a *state of an obligation* — when a
   step must be taken by. It is an attribute of a matter, in the same grammatical position as `-final`
   in a filename. The one_line_hint's own first clause concedes it: "the dated obligations **of a
   matter**".
4. **It is a document type.** The hint's second clause — "the record that they were diarised" — names
   a document kind, which the anchor's `work_type` proposal pre-emptively struck: "a template row
   justified only by holding a different legal document kind is the schema's default template with a
   narrower filename filter."
5. **It is a duplicate of its own schema's default template.** Argued in full below. This is the
   decisive case.
6. **It is a row defined by the absence of something** — this one does *not* land, and it is worth
   saying so rather than padding the list. The diary is a positively-shaped artefact with a real
   column set. It is not an absence row. Only five of the six charges apply.

## The node test, all three legs, each argued separately

CONNECTION.md §2, verbatim: "A **template** row exists only if its detection signals, recommended
dimensions, or privacy rules differ from its schema's default template. ALIGNMENT: a template that
would only repeat its schema's fields and dimension order **is not a node** — it is the schema's
default template."

**The schema's default template**, stated so the comparison is checkable: `law_practice` declares
`fields: []` and `template.dimension_order: []` under PR-6; its `template.why` argues the emptiness
three independent ways (contract, safety neighbour, disclosure) and sets `time_first: false`; its
default sensitivity is `potentially_sensitive` with a hard prohibition on client-named or
matter-named branches and on any named third party becoming a folder level; and its detection floor
is the two-leg requirement — an exact matter reference repeated across two or more artefacts, plus at
least one artefact whose own labelled slots separate a practitioner or firm role from a client role.

### Leg 1 — detection signals. They do not differ. They are the same text.

`law_practice`'s deterministic list, entry five, verbatim from the anchor JSON:

> "A LIMITATION-AND-DIARY structure: a table over MANY matters carrying one row per matter with a
> key-date column - limitation, service, response, listing, hearing, completion, filing - and an
> owning practitioner column. The portfolio shape is the signal, not the dates."

That is not an adjacent signal that this row could sharpen. It is this row's signal, already written
down, with this row's own boundary argument attached — the anchor goes on, in the same entry, to
separate the diary from `business_operations.contract-administration`'s register "by what the rows
are ABOUT, never by which profession keeps the table." The anchor also already carries the fixture
`Key dates - limitation and listing diary.xlsx` with its full observation set.

A template cannot differ in detection signals from a default that has already published its detection
signal. I looked for a signal the anchor had missed and found none: the calendar case is the anchor's
eleventh deterministic entry, the archive case its tenth, the email case its eleventh again.

### Leg 2 — recommended dimensions. Both empty, and necessarily so.

Under PR-6 the schema declares no field rows, and `_CONTRACT` permits a dimension only on a field the
same schema declares. `dimension_order: []` is the only contract-compliant recommendation available
to this row, and it is the same `[]` the anchor already justified three ways.

The interesting part is the one order this row *would* have been tempted to claim, because a diary is
a calendar and a calendar is time: `time_first: true`. `00` forbids exactly that for this material:

> "For document and record domains, project, function, or subject usually comes before time because
> putting year first scatters related work across calendar folders. Photos and capture-based media
> are the major exception: time often belongs first because capture date is a defining aspect of the
> material."

A limitation date is not a capture date. It is a date the file *talks about*, not a date the file
*was*. Filing by an obligation's due date would scatter one matter's opening, correspondence,
filings and closure across as many year folders as the matter has dates — the precise harm the
sentence names. So the row's only candidate distinction in dimensions is the one dimension the design
prohibits, which is not a distinction at all.

### Leg 3 — privacy rules. Identical, not stricter.

A multi-matter key-date register is bulk-sensitive: one sheet states that a list of named clients are
each in a named proceeding with a date approaching. That is a real and serious disclosure — but it is
word for word the posture the anchor already fixed for the privilege log ("A MULTI-SUBJECT LOG IS
BULK-SENSITIVE AS A WHOLE"), and the same `potentially_sensitive`, the same no-client-branch rule,
the same refusal to send a sheet or a summary of it to a cloud model.

Further, the anchor already prohibits the *only* deadline-specific behaviour a reader would expect
from a row with this name: "that the product calculates, validates, interprets or acts on any legal
deadline, or treats a date as operative, satisfied, missed or jurisdictionally valid." The row's
apparent value is a capability the design forbids.

**Verdict: nothing differs on any leg. Refuse.**

## The evidence that settles it

`00` contains **no occurrence of `deadline` or `due date`, in any casing, anywhere.** I grepped for
both (`grep -n -i "deadline\|due date"` over `planning/00-database-agent-product-design.md`) and the
match set is empty. The authority defines no temporal-obligation concept — no watching, no reminding,
no expiry, no approaching-date surface — on which a node could be hung.

This is not an argument from silence about a minor term. The document is exhaustive about dates in
every other register: it constrains date extraction ("Date extraction should be deliberately narrow…
numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes,
or other unrelated values"), it specifies what a calendar file yields ("Calendar formats such as ICS
should yield event title, start and end time, location, organizer, attendees, and recurrence
metadata"), and it rules on time as a folder level. It has plenty to say about dates and nothing
whatever to say about things being *due*. The product is a catalogue of files, not a tickler system.

## Rescue attempts, and why each failed

I did not want to refuse a row before testing it properly. Three defences were available.

**(a) The portfolio artefact breaks the schema's own anchor.** This is the strongest defence and it is
genuinely true: the diary spans many matters, so it satisfies neither leg of `law_practice`'s
matter-anchored default — no single repeated matter reference, no two-role artefact. A row that holds
the schema's own exception looks like a real node. It fails for two reasons. First, CONNECTION
separates activation from grouping, and the three legs are detection, dimensions and privacy — a
grouping consequence is not one of them. Second, the anchor already recorded both the observation and
its consequence, in its own fixture's own words ("the workbook spans many unrelated matters"). Even
the exception is not this row's to contribute.

**(b) The calendar source type.** A court diary arriving as `.ics` is a different medium from every
other artefact in the family, and media differences feel like nodes. They are not: `calendar` is
already in the anchor's `file_kinds`, the anchor's eleventh deterministic entry already covers
calendar records, and the anchor's never-alone list already strikes "A SOURCE TYPE or EXTENSION
ALONE… file_kind_plausible is constitutionally never-alone." A file format is not a filing world.

**(c) Stricter privacy.** Covered in leg 3. The register is bulk-sensitive; so is the privilege log
the anchor already holds. Same posture, therefore no difference.

## Files considered and rejected

Eight fixtures are in the JSON with full observation and prohibition lists. What each one was doing
in the research, and why it is not this row's evidence:

1. `Key dates - limitation and listing diary.xlsx` — **the proof fixture.** Identical filename,
   identical observations and identical boundary argument to file_example four on `law_practice.json`.
   A template whose central fixture is verbatim its schema's is the schema's default template.
2. `Contract renewal and notice dates register.xlsx` — **the collision fixture** (see below).
3. `Limitation periods by cause of action - practice note.pdf` — a document entirely *about*
   limitation dates, containing not one obligation belonging to anyone. It uses every context term the
   row would have proposed. Discriminator: a diary carries **dates**; this carries **periods** — a
   rule, not an instance. → Reading Inbox.
4. `Notice of Hearing - 41127-0006.pdf` — the family's most date-defined document, whose entire
   content is one future date a step must be taken by. It belongs to `law_practice.court-filing-record`
   on a tribunal caption plus a court-office issuing stamp. That the most deadline-shaped artefact in
   the family belongs to a *function* row is the argument compressed into one file.
5. `Court diary - Michaelmas listings.ics` — rescue attempt (b) as a fixture. Several events carry an
   exact matter reference; several carry only a party surname, which is three struck tokens and joins
   nothing.
6. `Matter management dashboard export - 2026-08.xlsx` — **the un-carvable fixture.** WIP, unbilled
   disbursements and next-key-date sit in the same row of the same export. Splitting a date row out of
   a money row would produce two half-documents from one table. `law_practice.time-and-billing` reads
   the whole thing and carries the date column as one more observation.
7. `CLE compliance deadlines - reporting period 2026.pdf` — the charge from the other direction. The
   word `deadline` appears in a labelled slot on a legal-profession document and activates nothing
   here: no client, no matter, no third party. It is `law_practice.admission-cle`'s, co-activating
   `career.credentials-licenses`. A word that crosses four unrelated roster families unchanged is an
   attribute, not a domain.
8. `Screenshot 2026-08-19 at 09.14.22 - diary reminder.png` — the row's worst mis-fire risk. OCR
   yields a date-type word, a bare date and a surname, which is the *entire* evidence a deadlines node
   would have been built to accept, and which is three consecutive never-alone strikes. Correct
   outcome: abstain. "A model that cannot cite sufficient evidence must return unknown." → Review Later.

Also considered and rejected without becoming fixtures:

- **A practice-management system's tickler/reminder database.** A live source system is not one file
  node; the bounded export (fixture 6) represents it. Live ingestion is a later connector and
  security decision.
- **An email reminder from a court e-filing system.** Covered by the anchor's eleventh deterministic
  entry; a legal-sounding subject with a date never fires alone.
- **A statute-of-limitations gazetteer.** R4 owns gazetteer contents and this row invents none. There
  is no catalogue of jurisdictional periods here and there must not be one — the anchor states
  jurisdiction is never a field and never a dimension in this family.

## The collision fixture

`Contract renewal and notice dates register.xlsx` versus `Key dates - limitation and listing diary.xlsx`.

Shape-for-shape they are the same document: a portfolio table over many items, one obligation-date
column, one proximity flag, one internal-owner column, no per-item narrative. Nothing in the
*structure* separates them.

**What discriminates them is what the rows are about — agreements versus matters — and nothing else.**
Not the date column. Not the flag. Not the owner column. Not the profession that maintains the file;
a lawyer maintaining a contract register does not make it practice material, per the never-alone
strike on a practitioner role name.

That the discriminator is never the date is the demonstration in miniature: if the date column cannot
distinguish this row's central artefact from a neighbour's central artefact, the date column cannot
found a node.

## Reciprocal boundaries

Six are authored on the JSON despite the refusal, because the collisions survive the refusal and the
sibling on the other side needs to know not to concede an artefact to a row that does not exist. Each
names the same fixture on both sides.

| Neighbour | Shared fixture | This side | That side |
|---|---|---|---|
| `business_operations.contract-administration` | the two registers above | rows are matters → `law_practice`'s own signal 5 | rows are agreements under a live obligation → theirs, lawyer or not |
| `law_practice.court-filing-record` | `Notice of Hearing - 41127-0006.pdf` | must not claim it as a deadline artefact | holds it on caption + issuing stamp; a prominent future date is not evidence against their claim |
| `law_practice.time-and-billing` | `Matter management dashboard export - 2026-08.xlsx` | cannot split a date column out of a money row | reads the whole export; needs no boundary against a row that does not exist and should not author one |
| `career.credentials-licenses` | `CLE compliance deadlines… .pdf` | no client, no matter, no third party — unreachable | holds it on credential structure; must not release it because a legal regulator issued it |
| `legal.personal-legal-matters` | `Court date - my hearing.ics` | a hearing event is not practitioner-side evidence | holds the holder's own listing; discriminator is the practitioner apparatus, never the event or the date |
| `finance.small-business-bookkeeping` | a receivables ageing schedule | the diary's exact shape, none of its substance — and this row would have had no principled way to refuse it | holds it on financial-slot structure; an exact matter reference supports membership without converting it |

`also_holds_with` is empty: this row authors no schema-level coactivation, and `law_practice` exposes
no role field to split, so `role_split` is empty for the same fieldless reason. Fixture-level
coactivation is recorded per-file as `also_schema` (`legal`, `finance`, `business_operations`,
`career`).

**Deliberate non-edges.** `legal.practice-matter-file` is not given an edge: it is the landed
gist-depth row for the same professional world and this refusal takes nothing from it and gives it
nothing. `law_practice.discovery`, `law_practice.pleadings`, `law_practice.appeals` and the other
function siblings are not given edges merely because their artefacts carry dates — a shared date is
the one piece of evidence this memo exists to disqualify, and authoring thirty edges on it would
re-import the error at edge level.

## Residual routing

Four residuals, all `00` §7.3 names, all quote-verified:

- **Protected Records** — the principal fallback: the register, the diary, the hearing notice, the
  dashboard export. `00`: it "may represent sensitive isolated material such as passport scans,
  medical documents, account statements, visas, legal forms, or credentials; it should normally remain
  local-only and must not cause filenames or content to be exposed in model prompts."
- **Review Later** — date-shaped artefacts whose world is unresolved (the OCR screenshot). `00`: "may
  hold files whose meaning is partly understood but whose final location requires a future decision."
- **Reading Inbox** — published limitation tables and calendar guidance: documents about deadlines
  containing nobody's deadline. `00`: "may hold papers, articles, reports, and saved PDFs that appear
  to be reading material but have no active research, course, or project association."
- **Independent Records** — a standalone dated notice with a durable purpose and no register around
  it. `00`: "may live under Personal/Independent Records and hold standalone certificates, notices,
  confirmations, forms, and PDFs that have a durable purpose but no broader group."

Both `must_consider_residuals` from the assignment (Protected Records, Review Later) are used.

## proposed_fields

**Empty, deliberately.** A refused row proposes no fields. The temptation was `key_date`, `due_date`,
`limitation_date` or `diary_date`, and all four are refused for the same reason: they are not fields,
they are *one* field's values plus a date. The anchor already reserves `fiscal_period` for this
family's one period concept and already tells template authors to reuse rather than mint. Adding a
date key here would have been a mint in service of a node that does not exist.

## Recommendations to R1c (cross-row — this row changed nothing)

1. **No change is required to `law_practice.json`.** Its signal 5 and its fixture 4 already hold this
   coverage correctly. Recording this explicitly so R1c does not "repair" a gap that is not there.
2. **`law_practice.court-filing-record` and `law_practice.time-and-billing`** should be told that this
   id was refused, so neither author writes a boundary against a non-existent row or concedes the
   hearing notice / dashboard export to it.
3. **The date-attribute strike is reusable.** Six other rosters plausibly host a deadlines-shaped
   sibling (renewal registers, compliance calendars, filing calendars). The test that worked here —
   *delete every date and every date-type word; if only a register of items survives, the node is the
   register's, not the date's* — is offered to R1c as a general instrument.

## NEEDS-JOSEPH

- **NJ-LPDD-1 — where does the refused coverage formally live?** The anchor holds it, but a schema's
  deterministic signal is not a template. Alternatives: (a) leave it as-is, the coverage is real and
  the signal is written — recommended; (b) fold the register explicitly into a matter-management
  sibling's scope; (c) accept that portfolio registers across every schema are systematically
  homeless and commission one cross-schema "register" treatment. Do not resolve this by reviving this
  id.
- **NJ-LPDD-2 — the load-bearing one. If a future phase commissions a temporal-obligation
  capability** — watching, reminding, or surfacing an approaching date — that capability needs a home,
  and this id is the name it would want. The refusal is correct for a *catalogue of files* and should
  be revisited **only if that capability is actually commissioned**, never to accommodate the
  possibility of it. Alternatives: (a) keep refused until commissioned — recommended; (b) hold the id
  reserved-but-inactive as a name squat, which the roster has no vocabulary for; (c) revive now, which
  is the 574's original mistake.
- **NJ-LPDD-3 — bulk-disclosure posture for portfolio registers.** The register discloses more than
  the sum of its rows, and `potentially_sensitive` is a per-file flag with no aggregation concept.
  Alternatives: (a) P7 owns aggregate disclosure and this catalogue says nothing further —
  recommended; (b) a bulk-sensitivity marker is added to the node vocabulary, which would touch every
  schema; (c) leave the observation in prose only, where it is today.
- **NJ-LPDD-4 — the un-carvable table, generally.** Fixture 6 shows a single exported row carrying
  billing evidence and date evidence in one grain. If the roster ever wants both to be separately
  filed, the design needs a position on sub-file granularity, which `00` does not currently take.
  Alternatives: (a) one file, one set of active domains, coactivation handles it — recommended and
  consistent with the allow-list union in CONNECTION §3.4; (b) sub-file regions become addressable,
  which is a P4/P9 change far beyond this row.

## Self-verification

- `python3 -m json.tool` parses the JSON.
- Every quoted span attributed to `00` was grep-verified verbatim before use (lines 46, 63, 35, 42,
  95, 120 of `planning/00-database-agent-product-design.md`); the CONNECTION §2 span was read from the
  file directly.
- The `deadline` / `due date` absence claim was established by grep returning an empty match set, not
  by recollection.
- Every edge id was confirmed present in `planning/domains/roster.json` by grep:
  `business_operations.contract-administration`, `career.credentials-licenses`,
  `finance.small-business-bookkeeping`, `law_practice.court-filing-record`,
  `law_practice.time-and-billing`, `legal.personal-legal-matters`. All four `falls_through_to` names
  are `00` §7.3 residuals.
- Every `file_examples.source_type` is in `SOURCE_TYPES` (`spreadsheet`, `text_document`, `calendar`,
  `image`).
- No file example writes a folder path as a fact; no threshold numbers, statistics or file counts
  appear anywhere; no handling class is assigned.
- `fields: []` and `proposed_fields: []` as required for a placeholder row, and doubly as required for
  a refusal.
- Only the two assigned files were written. `planning/29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `law_practice.json`, `check.py`, `src/` and every neighbour node were read
  or grepped only, never modified.
