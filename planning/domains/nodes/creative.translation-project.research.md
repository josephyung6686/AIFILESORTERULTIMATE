# Research memo — `creative.translation-project`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/creative.translation-project.json`
Roster row: template on the field-less `creative` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept the node.** `refuse_node: false`. It survives a charge that very nearly killed it, and it
survives on three things the creative default template does not have: a **bilingual segment
structure**, an asset (**the translation memory**) whose value is that it crosses projects and which
the default's project-first order would destroy, and a **privacy posture whose working material is a
third party's protected record**. `fields: []`, `proposed_fields: []`, `dimension_order: []`,
`role_split: []` — all four empty by contract or by argument, none by omission.

---

## THE CHARGE — the strongest case that this row should not exist

I put five prosecutions to the row before writing anything. Two of them landed partially and are
now written into the node as abstentions; three were defeated.

### P1 — "It is a universal file fact wearing a costume." **The strongest one.**

`language` is canonical field key number three, and 00 puts it in the universal set by name:

> The product should have a small shared set of universal file facts, such as file type, creation
> date, language, duplicate family, version family, and sensitivity status.

Every file in the corpus already carries a language. A row cannot exist because its files have a
value in a field that every file has — that is a row for a *property*, which the charge list names
explicitly. Worse, the roster's own `one_line_hint` for this row says *"language is a first-class
fact rather than a property of the file"* — and that is simply **false as written**: language is
already a first-class universal fact, product-wide, for every row. The hint argues for the row on a
ground that does not exist.

**Defeated, and the defeat is the row's whole thesis.** `language` is *monadic*. It can record that
a file is in German. It cannot record that *this German file's content is determined by that English
file's content*. The unit here is not a file with a language; it is a **correspondence between two
files**, plus the instruments that make the correspondence repeatable. No universal fact, and no
existing canonical key, expresses a between-files relation of that kind.

And the charge inverts on itself. Two other universals — `duplicate_family` and `version_family` —
do not merely fail to help here, they **misfire**. 00's filesystem extractor runs on everything:

> Every file receives basic filesystem extraction, including path, filename, normalized filename,
> extension, MIME type, size, timestamps, content hash, duplicate and version-family signals, and
> parent-folder context.

Given `contract_EN.docx` and `contract_DE.docx` — same stem to within a token, comparable size,
often the same creation session — that extractor proposes a version family. That reading is not weak,
it is **backwards**: the two are contemporaneous siblings, not successive revisions. So part of what
this row exists to do is *suppress* a universal signal that fires wrongly on its material. A row
that must cancel a universal inference is not a costume for that inference.

### P2 — "It is a work_type value."

Translation is a service, like retouching or colour grading. `work_type` is a canonical key; the
anchor's enum is a list of values; add `translation` to an engagement and you are done.

**Landed, partially — and the concession is now binding.** Where the *only* evidence is the word
"translation" in a filename, a folder name, an invoice line or an engagement scope, this row **must
not activate**, and `creative.client-engagement` holds the material. That is written into
`never_alone` as its own entry and into the engagement collision. What survives the concession is
that no work-type value produces a *bilingual segment file*, a *memory* or a *termbase* — those are
structures with interiors, not labels. The anchor's own enum confirms the distinction: its values
(`working file`, `export or deliverable`, `proof`, `master`, `brief`) name **artefacts**, not jobs.

### P3 — "It is a duplicate of `creative.client-engagement` plus `creative.deliverable-handoff`."

A translation job is a client engagement that produces a handoff. Two landed rows already cover it.

**Defeated by the memory.** A `.tmx` whose units span years, subject areas and clients is the one
artefact in the entire 41-row creative family whose value is that it **belongs to no single project**.
File it under the job that exported it and it stops being findable by the next job — you have
destroyed the asset by filing it correctly under the default template. That is a *dimension*
difference, which is exactly leg two of the node test, and neither the engagement row nor the handoff
row has anything like it.

### P4 — "It is a file-format row — a row for `.xliff` and `.tmx`."

**Defeated.** Eleven of the sixteen fixtures are `.docx`, `.pdf`, `.xlsx`, `.jpg`, `.srt` or `.zip`.
The dedicated formats are two members of sixteen, and 00 forbids the extension reading outright:

> The engine should treat the file extension as a routing signal rather than an assumption about
> meaning

The strongest proof is the code collision: `mobile-app/src/strings/de.xliff` has this row's flagship
interior *exactly* and belongs to `code.software-project`. If the format were the row, that fixture
would be mine. It is not.

### P5 — "It is defined by an absence: writing that is not original."

**Defeated.** Everything in the recognition block is a positive structure: paired segments with
per-segment state, mirrored stem runs of comparable size, governance columns on a term list, a price
computed on a **source** word count, identical timecodes across caption tracks, a signed attestation.
Nothing here is "and it lacks originality."

**Verdict: accept.** But the row is narrower than its roster hint promised, and the hint's stated
ground (language as a first-class fact) is not the ground it stands on.

---

## The node test, all three legs

CONNECTION §2: a template row exists only where its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. The creative
anchor holds that default as prose (`template.why`), so I state it before differing from it.

**The default template, as the anchor writes it:** `client` only where the corpus genuinely serves
more than one client, then `project`, then `stage`, then `artifact_type` as an optional deepest
level; **not time-first**, with the time-first exception granted to exactly two named siblings
(`creative.shoot-day-media`, `creative.raw-photo-catalogue`), neither of which is this one. Its
detection floor is the anchor's eight structures: linked-asset, layer/artboard, revision-round,
brief, delivery/handoff, production-paperwork, script, and the rest. Its privacy posture is four
reasons: unpublished work, releases carrying third-party identity, source material, client confidence.

### Leg 1 — detection signals: **differs.**

Ten signals are written and three of them are unreachable from the anchor's eight:

- **Bilingual segment structure.** A document interior of identified segments each carrying a source
  string and a target string with per-segment state. No anchor structure describes an interior whose
  unit is a *pair*. 00's structured-text extractor already reaches it — source and structured-data
  formats yield *"readable text plus format-specific structure such as language, imports, notebook
  cell types, package manifests, schema keys, repository markers, and project-root signals"* — and
  the same shape appears undeclared as a two-column table, where the spreadsheet extractor supplies
  *"sheet names, column headers, visible cell values, table-like regions, formulas only when useful,
  and dates or identifiers from labeled cells."*
- **Translation-memory structure.** Repeated units, two language variants each, own change dates,
  spanning a wider date and subject range than any project in the corpus. Nothing in the anchor.
- **Termbase structure**, discriminated by a **governance column** (approved-by, forbidden variant,
  do-not-translate) rather than by the language pair. The governance column is the whole
  discriminator and it is what the collision fixture below turns on.

Three more are anchor structures *bent* into a new shape rather than new ones, and I say so honestly:
the **source-count quote** is the anchor's brief/engagement shape with a price computed on the source
text; the **locale style guide** is the anchor's brief whose addressee is a locale rather than an
audience; the **linguistic review** is the anchor's revision round addressed by *segment* rather than
by page or timecode. The **mirrored-stem run** exists mostly to cancel a universal, per P1.

### Leg 2 — recommended dimensions: **differs, in two nameable ways.**

`dimension_order` is `[]` — empty by contract, because a dimension may only branch on a field its
schema declares and this schema declares none (D1 as narrowed, `_CONTRACT` rules 10 and 15,
CONNECTION PR-6). The *recommendation* is held as prose and it departs from the default twice:

1. **An exception above the project level.** The default is project-first for everything. The memory
   and the termbase are destroyed by it — see P3. This row recommends they sit at a **practice level
   above any project branch**, scoped by client or subject field. No other creative sibling has an
   artefact class that belongs above its own project.
2. **The locale is not a level.** The obvious deep branch here is target locale, and this row
   recommends **against** it. A locale branch scatters the two sides of one text into two subtrees —
   the exact harm 00 names for time: *"For document and record domains, project, function, or subject
   usually comes before time because putting year first scatters related work across calendar
   folders."* The parent-context test settles it: *"a parent dimension should provide the context
   required to understand the child."* `de-DE` is meaningless without the work, exactly as Homework 3
   is meaningless without the course — and the work is meaningless split across its languages.

`time_first: false`. This material is not capture-based and the anchor grants the exception by name
to two other rows. Whatever lands stays advisory: *"The system recommends an order based on the
domain template, but the user can reverse, remove, add, or flatten dimensions."*

### Leg 3 — privacy rules: **differs, and this is the cleanest leg.**

The anchor's four reasons all apply. A **fifth** exists here and nowhere else in the family: in the
certified and sworn branch, **the working material of the job is a third party's protected record** —
a passport, a birth or marriage certificate, a diploma, a court judgment, a medical report belonging
to a person who is not the corpus owner, who commissioned a translation and never consented to a
filing agent. The packet holds the original scan, its rendering and an attestation naming both
parties. The sensitive content is not incidental to the work; it **is** the work.

Two consequences the default template does not carry: **Protected Records becomes a live residual for
this row**, and a segment-level excerpt sent for interpretation may contain a named person's civil
data even when the filename is innocuous. Against both: *"Privacy policy must be enforced before
content reaches any model or external connector."*

A sixth, weaker reason worth recording: a memory accumulates fragments of every document ever run
through it, so one `.tmx` can hold sentences from unrelated clients' confidential material in a
single file. That is a second, independent reason it must not be treated as a project member.

**Three legs, three differences.** The row passes.

---

## Files considered and rejected

Sixteen fixtures are in the JSON with observations split from facts. These are the ones I looked at
and **did not** take, which is the part of the research the row would be worthless without.

- **`resume_JP.docx` beside `resume_EN.docx`.** A mirrored stem, comparable length, two languages —
  the row's signature observation, and it is **career**. There is no counterparty, no source-word
  count, no memory, no segment structure, and the subject of the document is the holder. Kept as a
  fixture precisely to make `never_alone` bite.
- **`Kaufvertrag_DE-EN_gegenueberstellend_executed.pdf`.** A dual-language contract in parallel
  columns. Rejected because there is **no source that preceded a target** — both columns were
  executed together and a prevailing-language clause usually says which governs. It is one instrument
  executed bilingually. Legal's.
- **`mobile-app/src/strings/de.xliff`.** My flagship interior, exactly, inside a repository. Rejected
  on the repository root, the manifest, and the fact that the unit under a `strings/` directory is a
  resource **key**, not a document. `.po` and `.json` appear in my extension list *only* so this
  boundary can be stated; I claim neither.
- **`AURA_Spring_RouteB_300x250_de_DE_v2.jpg`.** A locale token, and it is `creative.ad-campaign`'s —
  their row named it first and named me in the same breath. A locale **crossing a size grid** is a
  campaign coordinate; a locale naming the **target of a source document** is mine. Presence of a
  source text is the discriminator, not presence of a locale.
- **A lone `.srt` in any language.** Rejected: a single caption track is post-production's component
  of one cut. Only the *pair with identical timecodes* is mine.
- **A foreign-language article, paper or report saved to read.** The single most common reason a real
  corpus holds a document in another language, and it activates nothing — Reading Inbox.
- **A document that merely quotes two languages.** Rejected on 00's own restraint: *"The system
  should not use unreliable global language-quality checks that incorrectly punish multilingual or
  mathematics-heavy documents."* If multilinguality must not be read as a defect, it must not be read
  as a domain either.
- **A machine-translation output dropped into a folder.** Rejected — no job, no counterparty, no
  correspondence anyone maintains. Review Later.
- **A translator's contact list or an agency vendor roster.** Rejected: 00 says contacts *"should
  normally be privacy-protected rather than used to create folder proposals."*
- **A CAT-tool installation, licence file or project database.** A source system, not a file node.
  Metadata-only indexing; a bounded delivery archive with a readable manifest is represented instead.

---

## The collision fixture

**`HSK4_unit3_vocab_zh-en.xlsx`** — a language-learning vocabulary sheet. Two columns of paired
terms under two language headers: **structurally identical to a termbase**, my most distinctive
artefact after the memory. If two language columns were sufficient evidence, this row would swallow
every study sheet in every student's corpus.

**What discriminates it, in order of strength:**

1. **No governance column.** A termbase carries at least one column beyond the pair — approved-by, a
   forbidden variant, a do-not-translate flag. A study sheet carries only the pair, sometimes a
   pronunciation column.
2. **Row ordering.** Study sheets order by lesson or unit; termbases order by term or by domain.
3. **What is around it.** A termbase sits with a style guide, a memory or a job; a study sheet sits
   with course material and carries a course-shaped token, which 00's academic context floor then
   decides.

Reciprocal, both directions, same fixture: `academic.coursework` must not claim a client-approved
termbase because its subject happens to be a language; **this row must not claim a study glossary, a
graded translation exercise, or a language-class assignment.** Written into the JSON on both sides.

Two secondary collision fixtures carry the same job for other neighbours:
`Kaufvertrag_DE-EN_gegenueberstellend_executed.pdf` against legal, and
`Yilmaz_birth_certificate_TR_scan.jpg` against identity — which is the safety-critical one, because
the wrong direction there files the **holder's own passport** under a creative row.

---

## Reciprocal boundaries

Eleven `collides_with` edges, every id verified against `roster.json` `nodes[].domain_id`. Every one
states the boundary in both directions and names the same fixture on both sides. The four that carry
the most weight:

- **`creative.client-engagement`** — the load-bearing one, and the one that decides whether this row
  exists. Same fixture, `Quote_Nightwork_DE_18400_source_words.pdf`: mine when the priced quantity is
  a count of the **source** text (that quantity only exists because a source exists); theirs when the
  same document is priced per hour or per deliverable, and I must not pull it back by the
  target-language token in its stem.
- **`creative.book-manuscript`** — already argued against me from their side, and I accept their
  wording unchanged: *"translation must not absorb the source work's own draft family, and this row
  must not flatten a two-sided translation into one book's version family, because a source revision
  and a target revision are not members of one sequence."* Stated back: **I claim no draft family on
  either side.** The source's run is theirs; the target book's run is theirs once it has its own
  compile container; what is mine is the **relation** between the runs and the instruments that
  produced it.
- **`creative.ad-campaign`** — already argued against me from their side over the locale axis, and I
  accept their test verbatim in force. We *both* refused to mint a locale key, and they recorded
  NJ-ADCAMP-1 naming me by id. My NJ-TRANS-1 folds into it rather than competing with it.
- **`identity.core-documents`** — same bytes, and the only edge where getting the direction wrong is
  a safety failure rather than a filing failure. I see a civil record **only** when it belongs to a
  client and an attestation plus a target rendering sit beside it. Where the holder is uncertain,
  neither activates: *"Correct abstention is a successful outcome because the product’s goal is
  reliable organization, not maximum file movement."*

The other seven — `creative.post-production` (the caption pair), `code.software-project` (the XLIFF),
`creative.uiux-product-design` (localised string exports), `academic.coursework` (the study sheet),
`legal.leases-agreements` (the dual-language instrument), `career.portfolio-work-samples` (the
translator's sample pack and the bilingual CV), `creative.deliverable-handoff` (the delivery zip) —
are written to the same standard in the JSON.

**`also_holds_with`: five** — `identity`, `medical`, `academic`, `legal`, `finance`. All schema-level,
all on disjoint evidence, per *"One file may hold facts from more than one domain without losing
information."* `identity` appears as both a collision and a coactivation deliberately: the collision
entry carries the discriminator for the wrong claim, this entry carries the legitimate double reading.

### Neighbours considered and given no edge

- **`creative.publishing-title`** — a translated edition is a title with an ISBN of its own, but a
  title row and this row compete for nothing: they hold the published object, I hold the job. No
  same-evidence mutex, so no edge.
- **`creative.revision-round`** — tempting, because the LQA table is a review artefact. Not an edge:
  the revision-round row is the anchor's generic round and mine is *segment-addressed*, which is a
  detection difference inside my own row, not a competition for the same bytes.
- **`creative.journalism-reporting`** — translated source material is real, but the reporting row's
  sensitivity is source protection and mine is third-party civil data. Different harms, no shared
  fixture. Recorded rather than edged.
- **`creative.periodical-issue`, `creative.short-form-writing`, `creative.screenplay`** — all can be
  translated. Being translatable is not a boundary; every text is translatable. Adding edges for all
  of them would turn this row into a list of things that have language, which is the P1 charge
  re-entering through the edge list.
- **`photos.scanned-documents`** — a certified source scan *is* a scanned document, but the identity
  boundary already carries the safety-critical direction and duplicating it here would weaken it.
- **`business_operations.contract-administration`** — a translated contract in a corporate corpus.
  The legal edge covers the confusable bytes; adding this one is category, not evidence.

**`role_split`: empty, and argued.** The genuine split here is **source versus target**, and it fails
the edge's own definition twice: it is not two entity *types* in two roles but one text in two states,
and it points at no neighbour holding the other role — both sides live here. The anchor's
`client`/`our_firm` split already covers the commissioning seam and a template repeating it would be
padding. The real hole goes to NJ-TRANS-2 instead.

---

## proposed_fields — empty, and why

Two keys were genuinely tempting and both were refused.

1. **A source-language / target-language pair.** Canonical holds one `language` key and it is
   monadic. A pair would be the honest model of this world. It is still not a template row's to mint:
   minting on a field-less schema is the 574's mistake at the point of maximum temptation, and it
   would immediately raise whether a folder may be named for a language.
2. **A locale key.** Same objection, plus `creative.ad-campaign` refused the identical key first and
   named me as a co-claimant. Two template rows minting two spellings of one idea is the recorded
   overnight failure mode.

Both fold into **NJ-TRANS-1**. Nothing was minted. If NJ-R1a-1 option (b) is ever taken, the anchor's
four parked keys (`project`, `stage`, `artifact_type`, `client`) cover everything in this row **except
the source/target relation**, which no existing key expresses.

Eleven **work-type values** are proposed — values, not fields, not nodes. Three of them
(`bilingual working file`, `translation memory`, `termbase or glossary`) are artefact classes no
other creative sibling can produce. Sixteen **context terms** are proposed as the analogous floor to
00's academic context example (*"academic context such as “syllabus,” “lecture,” “credits,”
“instructor,” or “semester.”"*). **None of them is a language name**, deliberately — a language name
is exactly what must never fire alone. No regex, no score, no threshold.

---

## NEEDS-JOSEPH

1. **NJ-TRANS-1 — the locale key, and who mints it.** Folds into NJ-ADCAMP-1. (a) No key — the locale
   stays detection evidence and never becomes a folder level; what this row recommends today, and
   what stops a directory being named `de-DE`. (b) One shared key minted **on the anchor** and
   adjudicated once for `creative.ad-campaign`, `creative.translation-project`,
   `creative.deliverable-handoff` and `creative.print-production` together. (c) Per-row keys, which
   guarantees two spellings of one idea. **Recorded, not resolved.** A template row may not edit the
   anchor, so the two must be updated together — a recommendation to R1c, not an edit.
2. **NJ-TRANS-2 — the source/target relation has no key and no edge.** `language` is monadic, and the
   closed edge vocabulary is entirely between *nodes*, not between *files*. So this row's defining
   structure is currently expressible only as a detection signal and a grouping reason, never as a
   stored fact. (a) Leave it as grouping only — sufficient for placement, lost on retrieval. (b) A
   paired key set if NJ-R1a-1 goes to option (b) — records direction, still not the partner. (c) Treat
   it as a **P9 relationship type alongside duplicate family and version family**, which is where it
   structurally belongs and which is wholly outside this row's authority. **This row recommends (c)
   and decides nothing.**
3. **NJ-TRANS-3 — is the certified branch one row or two?** The literary/commercial branch and the
   certified/sworn branch share the pairing test and share almost nothing else: different artefacts
   (memory and termbase versus attestation and scan), different counterparties (a publisher versus a
   private individual), different residuals (Review Later versus Protected Records), materially
   different privacy postures. Split, the certified row would arguably sit nearer `identity` than
   `creative` and might warrant a **safety** launch rather than a placeholder. Kept together here
   because the pairing test genuinely is the same test, and splitting would put the strictest posture
   on the smaller row — but `sensitivity_why` is currently doing the work of a second row.
4. **The roster hint is wrong and should be corrected by R1c.** `one_line_hint` justifies the row on
   *"language is a first-class fact rather than a property of the file."* Language is **already** a
   first-class universal fact for every row in the product. The row stands on the correspondence and
   its instruments, not on that. A recommendation, not an edit — I touched no shared file.

---

## Self-verification

- `python3 -m json.tool` parses `creative.translation-project.json`. Key set matches the landed
  siblings (`creative.ad-campaign`, `creative.book-manuscript`), including their `fields_note` /
  `proposed_fields_note` / `proposed_context_terms` idiom.
- Every quotation above and in the JSON was grepped verbatim out of
  `planning/00-database-agent-product-design.md` before use (lines 35, 39, 47, 48, 63, 95, 114, 120,
  177, plus 28 for the multilingual-quality-check clause). Curly quotes and em dashes reproduced as
  they appear. No fabricated span.
- Every `collides_with` / `also_holds_with` id resolves against `roster.json` `nodes[].domain_id`.
  Every `falls_through_to` name is one of 00's nine residual templates, quoted from line 120.
- Every `file_examples.source_type` is in `SOURCE_TYPES`. No file example writes a folder path as a
  fact. `facts_legal` is `[]` on all sixteen, correctly — the schema declares no fields.
- Five `never_alone` entries are true of tempting false files actually in the fixture list
  (`resume_JP.docx`, `HSK4_unit3_vocab_zh-en.xlsx`, `mobile-app/src/strings/de.xliff`,
  `AURA_Spring_RouteB_300x250_de_DE_v2.jpg`, the mirrored `contract_EN`/`contract_DE` pair).
- No thresholds, no counts, no confidence scores, no handling classes. `sensitivity` is
  `potentially_sensitive`; `is_safety_domain` is not claimed.
- Files written: exactly the two assigned. `29-DOMAIN-OWNERSHIP.md`, the roster, `canonical_fields.json`,
  `check.py`, `src/`, the anchor and every neighbour node were read only, never edited.
