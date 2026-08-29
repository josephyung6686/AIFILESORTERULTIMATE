# Research memo — `creative.theatre-production`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/creative.theatre-production.json`
Roster row: template on the field-less `creative` schema, `parent_id: null`, `launch: placeholder`
Verdict: **ACCEPT** (`refuse_node: false`). Argued below against the strongest case for refusal.

## Result in one paragraph

The node survives, and it survives on **one** piece of evidence that no neighbour and no default
template can absorb: **the run**. Everywhere else in `creative`, a work is made once and delivered.
Here the finished work is performed *again*, on dated occasions, and each occasion generates its own
form. A forty-performance run produces forty near-identical dated documents whose bodies differ by
three lines. That is the exact shape a duplicate-and-version detector reads backwards, and getting it
right is a **detection** difference, not a taxonomy preference. Everything else this row claims —
cue-token joins, prompt copies, departmental grammar — is corroboration.

## Sources actually read

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (full).
- The stamped assignment via `make_prompt.py creative.theatre-production`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` (full) — the launch row used for
  depth calibration. Its "fieldless template that differs on evidence and posture rather than
  fields" argument is the structure this memo follows.
- `planning/domains/nodes/creative.json` (full) — the schema anchor and the **default template**
  this row is measured against.
- `planning/domains/nodes/creative.exhibition.{json,research.md}` — the only landed row that had
  already argued a boundary against me; located with one grep, read only at the matched spans.
- `planning/00-database-agent-product-design.md` — **by grep only**, per the token discipline. Every
  span in quote marks in the JSON and in this memo was `grep`-verified verbatim in `00` before use,
  including the curly apostrophes in `product’s` and `user’s` and the em dashes in the *Unsupported
  or Encrypted* sentence. Two candidate quotes (`Spreadsheets should yield`, `assume that time only
  moves forward`) returned **zero** matches and were **discarded rather than paraphrased into quote
  marks**.
- `planning/domains/roster.json` — id existence check for every edge target.

## THE CHARGE — the strongest case that this row should not exist

Stated at full strength before any defence, because a padded row is worth less than an honest
refusal.

**(a) It is a MEDIUM, and a medium is not a node.** "Theatre" names where a thing is shown. The
schema anchor is explicit that the media-form vocabulary of this family — "poster, showreel, stem,
mix, cut, plate, edition, atlas, sprite, lookbook" — are *values* of `artifact_type`, and that "no
sibling may ask for a node per media form." Stage is a venue for a script; screen is another.
`creative.screenplay`'s own roster hint already says "A script for screen **or stage**." So this row
is `creative.screenplay` plus a venue word.

**(b) It is `creative.film-production` minus the camera — a row defined by an ABSENCE.**
`creative.film-production` is "A production as an organising whole — its script, schedule, paperwork,
media and cuts." Delete "media and cuts" and you have this row. A row whose only distinguishing
feature is that something is *missing* is precisely the failure mode the charge names.

**(c) It is a duplicate of `creative.performing-practice`.** That row already holds "programmes,
parts, records" across "a career of dated performances." Dated performances *are* the run. The
performer side of theatre is landed; this row adds only the crew side, and crew paperwork is
scheduling, which `business_operations` and `creative.film-production` both already do.

**(d) It is a LIFECYCLE STAGE SET.** Read the hint's own words: "script, design, rehearsal,
technical, run." Those are five values of `stage` — the schema anchor's second adoption candidate,
whose `example` is literally "brief, concept, draft, review round, approved, delivered, published,
archived." Naming a domain after its own stage list is the 574's mistake in miniature.

**(e) It is an ORGANISATION NAME.** "The Royal Court", "Chichester Festival Theatre" — the thing that
would actually fire is a producing house's name, and a company or venue name is never-alone evidence
by the direct read-across of `00`'s university warning.

**(f) It is the union of neighbours already landed or rostered.** `creative.screenplay` holds the
script; `creative.performing-practice` holds the parts and programmes; `creative.print-production`
holds the programme going to press; `career.portfolio-work-samples` holds the production
photography; `creative.exhibition` holds the physical-install analogue and has *already written a
reciprocal edge against me*; `business_operations.project-delivery` holds the season, the budget and
the box office; `photos` holds the dress-rehearsal captures. Nothing may be left over.

## Why the charge fails

It fails on evidence that (a)–(f) cannot jointly absorb, and the evidence is not the script.

### 1. The run — and the fact that it breaks a universal signal

`00` collects "duplicate and version-family signals" **universally**. In every other creative row
that universal signal points the right way: a run of same-stem files with drifting tokens is a
version family, and the anchor even supplies the standing fixture, `logo_final_v3_FINAL.ai`.

Here the identical structure points the **wrong** way. `Show Report - Perf 26.pdf`,
`Show Report - Perf 27.pdf`, `Show Report - Perf 28.pdf` share a stem, share a layout, share ninety
percent of their text, and differ by an ordinal, a date, three running times and a note. A version
reading would keep the last and offer the rest for dedupe review. They are not versions. They are
**forty separate events** — the only accurate record of what happened on forty nights — and `00`'s
own guard is the operative sentence: "A content-hash match supports deduplication review; a filename
match alone does not."

No neighbour needs this. Film shoots each day once. A campaign delivers each cut once. A performer's
career file holds *their* dated engagements, not forty forms about one of them. **This is a
detection-signal difference from the creative default template, which is leg one of the node test,
and it is not available from any other row on the roster.** It defeats (b) and (c) directly: film
does not repeat, and the performer's row does not hold the series.

### 2. The cue token — a cross-document join key that is not a version number

`LX 42` appears in the margin column of the prompt copy, as a row of the LX cue sheet, and as the
target of a note on the show report. Three different document kinds, three different source types
(`ocr`, `spreadsheet`, `text_document`), joined by a short alphanumeric string that is neither a
date, nor a filename stem, nor a version. The creative family has no other such key. The anchor's
twelve deterministic signals contain nothing of the kind.

This is why the row is not a stage list (d): stages are ordered *labels on one file*; a cue token is
an *edge between files*, and edges are what a grouping engine can actually use.

### 3. The prompt copy — the script stops being the work

(a) says stage is a venue for a script. That is true of the script and false of the production. In
`creative.screenplay` the text **is** the work: it has a draft family, it moves toward acceptance, it
gets submitted. Here the text is an **input**, and the artefact is the same pages carrying a ruled
annotation column of standbys, cue tokens, entrances and blocking, paginated against one staging.
The unit of the work has changed from *the text* to *this staging of the text*, which is why a
transfer of the same play to a second venue produces a wholly new set of plots and a wholly new
prompt copy while the `.fdx` does not change at all.

The reciprocal is written on both sides in the JSON and stated again below.

### 4. Departmental grammar — a stable closed vocabulary, not an org name

(e) is right that a theatre's *name* is worthless. But the departments are not names, they are a
small stable set — Stage Management, LX, Sound, Wardrobe, Props, Set, Company — that recurs as
section headings inside reports, as note addressees, and as sibling folder names. Recurrence of a
closed vocabulary across unrelated document kinds in one neighbourhood is structural evidence; a
proper noun is not. The JSON's `never_alone` keeps the proper noun locked out and lets only the
vocabulary count.

### 5. On (f), the union argument

The union fails because the leftovers are the load-bearing parts. After screenplay takes the script,
performing-practice takes the performer's part, print-production takes the programme's press file,
career takes the work sample, exhibition takes the gallery install and business_operations takes the
season budget, what remains unhoused is: **the prompt copy, the cue sheets, the plots and hookups,
the running plots, the rehearsal calls, the report series, and the company paperwork** — which is
most of a production by document count, and is exactly what the hint means by "the paperwork
outnumbers the artefacts."

## The node test, all three legs

The creative schema declares **no fields**. Its default template is therefore held as prose on
`creative.json`: *client only where the corpus genuinely serves more than one client, then project,
then stage, then artifact_type*, not time-first, with two named time-first exceptions
(`creative.shoot-day-media`, `creative.raw-photo-catalogue`).

**Leg 1 — detection signals. DIFFER, decisively.** Four signals in this row are absent from the
anchor's twelve: the run-as-report-series; the cue-numbered cross-document join; the prompt-copy
annotation column; and the plot-and-schedule pair (a scaled drawing plus a table keyed to it by unit
number, where *neither half is decisive alone*). One anchor signal is also **inverted** here: the
revision-round signal must be actively *suppressed* against the report series. Leg 1 passes on its
own.

**Leg 2 — dimensions. UNAVAILABLE to this row, as to all 41 creative templates.** `dimension_order`
is `[]` by contract, not by judgement (D6, `_CONTRACT` rule 8, PR-6). This memo does **not** treat
that as a pass. It does record the prose difference from the default so R1c can adjudicate if D1 is
ever revisited: (i) the default's **client** level has no occupant, because a production is mounted
*by* the producing organisation rather than *for* a counterparty, so it would be exactly the level
`00`'s validator refuses — it must not "create meaningless one-child levels" and must not "use an
author or organization merely as a collector"; (ii) the default's **stage** progression ends at
handoff, whereas here everything after opening night is generated by a *finished* work repeating, so
a **date level under the production, for the run only**, is genuinely wanted; (iii) the deepest
useful level is a **department**, not an `artifact_type`. Not time-first at the top: "For document
and record domains, project, function, or subject usually comes before time because putting year
first scatters related work across calendar folders" — and a year-first order would split one
production's rehearsals from its own run whenever a run crosses a New Year. This row does **not**
claim the photos exception; "Photos and capture-based media are the major exception" is granted to
capture-based material, and this row's material is overwhelmingly paperwork.

**Leg 3 — privacy rules. DIFFER, on a mechanism the anchor does not state.** The anchor's posture
covers unpublished work, third-party identity on releases, source material and client confidence.
This row adds a *distribution* argument: **the report series is not bulk-safe**. Thirty-nine of forty
show reports are anodyne technical notes; the fortieth records that a named performer went off
injured in Act 2 and the understudy went on. Health-shaped information about a third party arrives
inside a series whose overwhelming statistical character is boilerplate, which is precisely the shape
that invites bulk summarisation. The series must therefore inherit the cautious posture rather than
the average — and "Privacy policy must be enforced before content reaches any model or external
connector." The second addition is the company contact sheet's **next-of-kin and guardian** rows for
children's ensembles: ordinary production paperwork by genre, protected by content.

**Two of three legs differ on their own merits; the third is closed to every sibling equally.
Accept.**

## Files considered and REJECTED

Naming what this row does not hold, which is the part a padded row omits.

| Considered | Why it is not this row's evidence |
|---|---|
| `Cherry Orchard - rehearsal draft 4.fdx` | On this evidence it is a writer's draft series and belongs to `creative.screenplay`. It becomes this row's only once a *cued* copy exists. Kept as a fixture precisely to record the rejection. |
| `Hamlet Act 3 annotated.pdf` | **Collision fixture.** A student's annotated set text: play pages plus dense handwriting, which is the prompt copy's silhouette exactly. Discriminated by *what the annotation is* — interpretive prose, not standbys, cue tokens or blocking — and by the total absence of cue-token recurrence and departmental vocabulary. Routes to Reading Inbox. |
| `Run Sheet - Q4 Sales Kickoff - Main Stage.xlsx` | **Collision fixture.** A corporate run-of-show: cue-shaped tokens, clock times, a caller, a rehearsal, a "Main Stage". Three discriminators: cue targets are agenda items and executives rather than scenes and characters; no script element grammar anywhere; the event happens **once**, so the run-as-report-series signal cannot fire. Belongs to `business_operations.project-delivery`. |
| A ticket confirmation / a theatre booking email | Transactional. `Receipts and Confirmations` — and attending a play is not mounting one. |
| A downloaded public-domain play PDF | Reading material with no staging around it. Reading Inbox. Play titles are the most reused strings in this domain. |
| A cast recording `.mp3`, an original-cast album | A published audio work, not a production record. Container evidence alone is never-alone anyway. |
| A director's or designer's **CV** | A list of production names — the sharpest never-alone case in the row, because it will *look* like a production register and contains no production. `career`. |
| A venue's seating plan / access statement / fire cert | The building's records, not the production's. `business_operations` or `Independent Records`. |
| A season budget, a box-office report, an Equity contract | Money, governance and employment. `business_operations.project-delivery`, `finance`, `legal`. |
| A drama-school lesson plan, an audition speech list | Training and career, not a staging. |
| A `.mus`/`.sib` score of a new musical | Composition, not production. It enters this row only as *parts distributed to a band call*, i.e. once the departmental structure claims it. |

## Reciprocal boundaries — both directions, same fixture named on both sides

Eight `collides_with` edges are authored. Every target id was checked to exist in
`planning/domains/roster.json`. The reciprocal half of each is stated inside the edge itself; here is
the fixture table.

| Neighbour | Same fixture on both sides | This row owns it when… | The neighbour owns it when… |
|---|---|---|---|
| `creative.screenplay` | `Cherry Orchard - rehearsal draft 4.fdx`; the pages inside the prompt copy | the pages carry an annotation column and the cue tokens recur elsewhere | it is the text as the work — draft family, submission trail, no cue column |
| `creative.performing-practice` | `Programme - Cherry Orchard - Nov 2026.pdf`; sides and parts | other departments are present in the neighbourhood (a plot, a hookup, an SM report series) | only one person's material is present, across *different* shows |
| `creative.film-production` | a dated departmental crew document; `Archive capture … cam A.mxf` | the dated document reports a completed repeat of finished material (ordinal + running times); the capture has no takes, no slate, no cut | the dated document schedules **future capture** (unit base, scenes to shoot, weather, nearest hospital); the media has take structure and bins |
| `creative.exhibition` | a performance staged in the gallery for one evening of the run | script grammar + cast list + rehearsal calls + report series | checklist + hang plan + condition reports |
| `photos` | `Dress Rehearsal 2026-11-03 - 0187.arw` + sidecar | the paperwork around the captures dates them to one occasion of one production | the capture reading, which must never be suppressed — but must not place the file by capture date, which would scatter one show across the nights of its own run |
| `career` | the same programme PDF; production photography | it sits beside the paperwork that made it | it sits beside a headshot, a CV and a credit list, ordered for showing |
| `code` | a show-control / projection-content folder | a cue-numbered document or opaque workspace keyed to the prompt copy | a repository root with manifest and preserved internal layout |
| `business_operations.project-delivery` | `Run Sheet - Q4 Sales Kickoff.xlsx`; the producing house's season | a staged work with script, characters, scenes and a repeat | a corporate event, or the season's budget, variance and board reporting |

`creative.exhibition` already wrote its half against me before I existed; my edge is worded to match
its discriminator exactly ("script + cast + call sheets" vs "checklist + plan + condition reports")
so R1c finds no drift between the two files.

**`also_holds_with` is empty, deliberately.** The `creative` schema carries schema-level co-activation
with `photos`, `legal`, `business_operations` and `career`. A template may not widen its schema's
`also_holds_with` — the precedent is set explicitly on `creative.exhibition`. The legitimate double
readings are therefore carried on the fixtures as `also_schema` (`photos` on the dress-rehearsal RAW,
`career` on the programme, `identity` on the company contact sheet) and the competing-evidence half
is carried as a collision. `role_split` is empty: the schema exposes no field to split, and the
`client`/`our_firm` split recorded on the anchor has no occupant here, which is itself part of this
row's argument.

## Neighbours considered that did NOT get an edge

- `creative.print-production` — genuinely competes for the programme's press-ready PDF, but the
  discriminator (`proof → press → run → delivery` chain vs. the show it serves) is already authored
  on `creative.exhibition` in the same words, and duplicating it here would create two rows saying
  the same thing about the same bytes. Recommended to R1c as a *possible* addition, not asserted.
- `creative.interior-design` / `creative.architectural-visualisation` — a groundplan is a scaled
  drawing of a physical space and looks like both. Not authored as an edge because the annotated
  objects discriminate cleanly and without judgement: lanterns, bars, rostra and sightlines versus
  furniture, finishes or a building. Recorded on the groundplan fixture's `must_not_conclude`
  instead.
- `creative.shoot-day-media` — handled inside the `creative.film-production` edge rather than
  separately; splitting them would state one boundary twice.
- `identity` — a co-activation on the company contact sheet, not a mutex. Carried as `also_schema`.
- `legal.leases-agreements` — venue hires and performance-rights licences are real, but they are
  `legal`'s instrument reading against `creative`'s schema-level `also_holds_with` with legal, not a
  template-level competition over the same evidence.

## proposed_fields

**Empty, deliberately.** `fields: []` and `proposed_fields: []`.

The row has exactly one genuinely field-shaped want — **department** (SM, LX, Sound, Wardrobe, Props,
Set) — and it declines to mint it. No canonical key holds it: `artifact_type` names the document kind
rather than the owning department, `stage` is the production's own progression, `client` has no
occupant, `project` is the production itself. Minting a key on a **field-less** schema, at the exact
point where the row most wants one, is the 574's mistake reproduced under pressure; the anchor makes
the same refusal for the rights-and-licence hole and this row follows it. The hole is recorded in
`open_question` and in NEEDS-JOSEPH below for R1c.

## NEEDS-JOSEPH

**NJ-THEATRE-1 — the department hole.** The recommended deepest dimension is a department, and no
canonical key holds it. Alternatives: **(a)** leave the hole; departmental folders are recognised
only as existing user vocabulary, which `00` already licenses — "Existing curated folders and
user-entered labels should influence retrieval because they represent the user’s vocabulary."
**(b)** treat department as a *value* of `artifact_type` — honest for a plot, wrong for a report,
because a report is one document addressed to six departments at once. **(c)** mint a key, only if
and when D1 is revisited. *This row recommends (a) at launch and proposes nothing.*

**NJ-THEATRE-2 — the run's date level versus the default's refusal of time.** The prose
recommendation wants a date level **under** the production, for the run only. No creative sibling
needs a mid-order date level; the schema's default is not time-first and this row explicitly does not
claim the photos exception. Alternatives: **(a)** one template, with the run's dates expressed only
as grouping and never as a level; **(b)** split into a production template and a run template, which
would double the row and risks being the medium-not-a-node error at one remove; **(c)** allow a
mid-order date level in the dimension grammar generally, which is a P-level design question, not this
row's. *Unresolved; (a) is the safe launch behaviour.*

**NJ-THEATRE-3 — where a touring production's venue leg sits.** The same production re-plotted for a
second stage produces a complete second set of plots, hookups and get-in schedules while sharing one
script, one cast and one report vocabulary. Either **(a)** one production with a venue level, or
**(b)** two productions of one work. No design doc settles it; it is a question about a real touring
company's filesystem.

**NJ-THEATRE-4 (inherited, not re-opened).** If NJ-R1a-1 resolves to option (a) — `creative` stays
permanently field-less — then leg 2 of the node test is closed to all 41 creative templates forever,
and this row's acceptance rests on legs 1 and 3 alone. It still passes on those two, which is why the
verdict does not change either way. Flagged so R1c can see that this row's survival is *not*
contingent on D1.

## Recommendations to R1c (cross-row; this agent changed nothing outside its two files)

1. Consider adding `creative.print-production` ↔ `creative.theatre-production` as a reciprocal pair
   over the programme's press-ready PDF, if R1c judges that a boundary already stated on
   `creative.exhibition` should be restated per-row rather than inherited.
2. `creative.exhibition` line 536 already carries the reciprocal edge to this row; no change needed
   there, and this row was written to match its wording rather than drift from it.
3. The **run-as-report-series versus version-family** discrimination is stated here as a
   theatre-specific signal, but it is probably a *general* P9 grouping concern (any repeating dated
   form — a daily standup note, a weekly status report — has the same shape). R1c may want it lifted
   somewhere more central rather than living only on this row.

## Self-verification

- `python3 -m json.tool` — **passes** (48,861 bytes).
- Every quoted span `grep`-verified verbatim in `00` *before* writing, including curly apostrophes
  and em dashes; two unverifiable candidates discarded rather than paraphrased.
- Every edge target confirmed present in `planning/domains/roster.json`: `creative.screenplay`,
  `creative.performing-practice`, `creative.film-production`, `creative.exhibition`, `photos`,
  `career`, `code`, `business_operations.project-delivery`.
- Every `falls_through_to` name is one of `00`'s residual homes: Review Later, Protected Records,
  Independent Records, Unsupported or Encrypted, One-Off Images, Temporary Screenshots, Reading
  Inbox, Reference Clips. Both `must_consider_residuals` (Independent Records, Review Later) are
  present.
- Every `file_examples.source_type` is in `SOURCE_TYPES`: `text_document`, `spreadsheet`,
  `design_creative`, `image`, `audio_video`, `ocr`, `opaque_binary`, `archive`.
- 15 fixtures, each splitting observations from facts; no fixture writes a folder path as a fact;
  sparse and unreadable fixtures carry `group_without_copying_facts: true`.
- `never_alone` entries are true of the tempting false files: the play title trips
  `Hamlet Act 3 annotated.pdf`, the lone cue token and the dated crew document trip
  `Run Sheet - Q4 Sales Kickoff.xlsx`, the credit block trips the programme, and the capture-metadata
  entry trips the dress-rehearsal RAW.
- `fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`, no threshold
  numbers, no handling classes, no `public_low`.
- Files written: **exactly two** — `creative.theatre-production.json` and this memo. The ownership
  register, the roster, `canonical_fields.json`, `check.py`, `src/`, the SPECs and every neighbour
  node were left untouched.
