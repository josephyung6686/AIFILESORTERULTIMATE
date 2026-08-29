# `creative` — lab notes (R1b, J-IND row written to J-DEPTH)

Row kind: **schema**. Launch: **placeholder** (`fields: []`). Verdict: **kept, not refused.**

This is the schema row for the largest family on the roster — 41 sibling templates measure their
node test against the default template stated here. The memo is written on the assumption that a
sibling author reads *this file* before writing theirs, so the posture, the vocabulary, and the
seams are stated explicitly rather than left to be inferred from the JSON.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the only source quoted. Every quotation in
  `creative.json` was grep-verified back out of this file verbatim after writing (see **Audits**).
  The spans that did the work here:
  - the template-library sentence, which is the row's `design_cite`: *"covering common
    organizational situations such as academic programs, university applications, recruiting
    processes, client engagements, research workflows, financial records, travel, legal matters,
    creative projects, software repositories, personal administration, and photo collections"*.
    This is the only place `00` names this world, and it names it as a **template situation**, not
    as a schema with fields. That asymmetry is the whole reason this row is `placeholder` and
    `provenance: inference` rather than `design`.
  - the creative-format extractor sentence, which is the source of this row's single most
    domain-specific detection signal: *"Design and creative formats such as PSD, AI, SVG, Figma
    exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas
    properties, embedded metadata, layers or artboards where accessible, linked asset names, and
    preview text; unsupported proprietary formats should be recorded as indexed-but-unreadable
    rather than silently treated as empty."*
  - the role-split paragraph, the source of `client` / `our_firm`.
  - the dimension-order rule and its two halves: *"For document and record domains, project,
    function, or subject usually comes before time"* and the photos exception *"time often belongs
    first because capture date is a defining aspect of the material."*
  - the template validator's prohibitions — *"create meaningless one-child levels"*, *"use an
    author or organization merely as a collector"* — which are what stop `client` from being an
    unconditional top level.
  - the authorship warning, which bites harder here than anywhere: *"It should avoid using
    authorship or creator identity as a destination dimension."*
  - the residual definitions in the residual-library paragraph, for all eight fallthroughs.
- `planning/domains/_CONTRACT.md` — rules 1–3 (provenance, no fabricated quotes, no numbers),
  8 (snake_case + a dimension may only branch on a declared field), 10 (no field rows on the
  deferred/placeholder schemas), 11–15 (`kind`, closed edge vocabulary, `is_safety_domain`).
- `planning/prompts/ALIGNMENT.md` — the sentence that decided the shape of this row: *"would only repeat its schema’s
  fields and dimension_order"* … *"it is the schema’s default template."* Stating the default template explicitly here is the service this row owes its
  41 siblings; without it their node test has nothing to be measured against.
- `planning/domains/canonical_fields.json` — the 37 keys. Confirmed `project`, `stage`,
  `artifact_type`, `client`, `our_firm` exist with the roles and destination-eligibility this row
  relies on. **No key minted.**
- `planning/domains/roster.json` + `ROSTER.md` §1b, §4 (slice 10), §5, §7 — confirmed the id, the
  41 sibling ids and their `one_line_hint`s, the absorbed legacy ids, and the exact wording of
  NJ-R1a-1's remainder.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked programmatically against every
  `file_examples.source_type` and every member of `file_kinds.source_types`.

### Landed neighbours read before writing (not rewritten)

- `photos.json` — the depth and idiom exemplar for a **schema** row, and the neighbour this row
  shares the most contested bytes with. Its `never_alone` list is the model for this row's.
- `code.json`, and its two honest refusals `code.software-project` and `code.scratch-prototypes`.
  Those two are the most instructive documents in the repo for this family, because they refuse for
  the reasons 41 creative siblings will face: *"The Code schema’s default situation"*, and *"What the roster leaves this id after its four
  named siblings take the unrooted situations"* … *"is nothing more than the condition that a
  repository root fires. That is the schema activating"* Several creative siblings — `creative.graphic-design-project`
  is the obvious one — are in exactly that position with respect to this row, which is why the
  default template below is stated in enough detail to make their refusal checkable.
- `career.json` — the neighbour that already owns the `design_creative` file-kind assignment via
  `career.portfolio-work-samples`, and, like this row, a launch domain that declares no field rows.
- `business_operations.json` — key set, `proposed_fields` shape, `falls_through_to` object shape,
  and the exemplary refusal idiom in `organisational-records`. Used for **shape and idiom only**;
  its depth is J-IND debt and was not the calibration target.
- `finance.crypto-assets.research.md`, `medical.personal-health-records.research.md` — the depth
  target for this memo.

### Contract conflicts noticed

`role_split` appears in the landed corpus in two shapes: `{domain, our_field, their_field, why}`
(`finance.json`) and `{field, other_field, other_domain, why, provenance}` (`business_operations.json`).
This row uses the **second**, because that is the shape the J-IND placeholder-schema siblings carry
and R1c will be normalising this family together. Flagged rather than silently chosen.

---

## Did this row survive the node test?

`kind: schema`, so the test is: *can you name a distinct 3–6 field set, or would you only repeat
another schema, or need a giant form?* The answer is complicated by the fact that the row declares
**no fields at all**, so the test has to be run against the field set the row would declare if
NJ-R1a-1's option (b) were taken. All three legs, argued separately:

### Leg 1 — a distinct field set

The candidate set is `project`, `stage`, `artifact_type`, `client`. Four keys, inside the 3–6
band, none of them minted. Three of the four are already `research`'s. **That overlap is the
strongest argument against this row existing at all, and it is the reason NJ-R1a-1 was opened in
the first place.** It is not enough to note the fourth key and move on, so:

- `client` is the discriminator that survives scrutiny. `research` declares no counterparty role of
  any kind — its outward-facing keys are `lab` (where the work was done) and `venue` (where it is
  going to be published). A commissioning organisation is neither. `00` gives the counterparty
  concept its own sentence and its own role-split partner precisely because entity-type collapse is
  the failure it is guarding against.
- `lab` and `venue` are dead keys in this world, and dead in a way that matters: a folder level
  built on either would produce empty branches for every graphic-design, film, music, fashion,
  games and advertising row in the family. A schema whose declared fields cannot be filled by most
  of its own templates is the 574's shape.
- The `stage` **values** differ completely (draft/review-round/approved/delivered versus
  literature/experiment/analysis/manuscript), but that is deliberately **not** offered as an
  argument. Values are values; a `creative_stage` key would be exactly the two-spellings-one-concept
  bug D6 exists to prevent. The row says so explicitly in `proposed_fields`.

Verdict on leg 1: **passes, narrowly and honestly.** The narrowness is recorded as open_question (1),
including the fold-into-research alternative, rather than smoothed away.

### Leg 2 — detection signals of its own

This is where the row is strongest, and it does not depend on the field question at all. Two
signals belong to no other schema in the roster:

1. **The linked-asset structure.** A working file that names media it does not contain, beside a
   folder that resolves those names. `00` requires the extractor to emit `linked asset names` for
   exactly these formats. No other schema has a fixture of this shape: `code` has manifests and
   lockfiles (a dependency graph, not a media graph), `research` has datasets and figures (siblings,
   not references), `photos` has sidecars (per-file, not cross-file).
2. **The indexed-but-unreadable state as a normal condition.** `00` names the state; in this world
   it is the majority case for source files, not an exception. A schema whose recognition has to
   work when the primary artefact's interior is unreadable is a genuinely different recognition
   problem, and it is why this row's signals lean on *structure around the file* rather than
   content inside it.

Verdict on leg 2: **passes cleanly.**

### Leg 3 — privacy rules of its own

Four reasons, all in `sensitivity_why`, and none of them the generic "documents can be sensitive":
unpublished work (harm is disclosure, not identity theft), third-party identity on releases and
call sheets (people who never consented to a filing agent), journalistic source material (the
sharpest case, and unrecoverable if wrong — `00`: *"Revocation cannot necessarily retract data
already sent to an external provider, so the product must communicate that distinction clearly."*),
and the client's confidence (which the maker cannot waive on their behalf). `research` has none of
these; `career` has one of them for different reasons.

Verdict on leg 3: **passes.** The row does **not** carry `is_safety_domain` — that flag stays with
`00`'s four — and it assigns no handling class.

**Overall: kept.** Two of three legs pass cleanly; the first passes narrowly and its narrowness is
filed as an open question rather than resolved.

---

## The default template, stated for the 41 siblings

The row's `template.dimension_order` is **empty by contract** — a dimension may only branch on a
declared field and this placeholder declares none. The recommendation is therefore held as prose,
and this is the paragraph siblings must differ from:

> `client` **only where the corpus genuinely serves more than one client** → `project` → `stage` →
> `artifact_type` as the optional deepest level. Not time-first.

Why each level, and why in that order:

- **`client` is conditional, not default.** In a single-client or in-house corpus it is a one-child
  level naming the user's own employer above everything they have ever made — which is both of
  `00`'s named validator failures at once (*"create meaningless one-child levels"*, *"use an author
  or organization merely as a collector"*). This is a **template-time check against the accepted
  group**, not a field-time ban, which is why `client` stays destination-eligible.
- **`project` is the real top.** `00` puts project above authorship explicitly. In this world that
  sentence is doing the heaviest lifting anywhere in the catalogue, because the author of nearly
  every file *is the corpus owner*: an author dimension here collects the entire disk.
- **`stage` before `artifact_type`** by the parent-context rule. `Round 2` and `_v3` are
  meaningless without the work, exactly as `Homework 3` is meaningless without the course.
- **Not time-first**, and this is the rule siblings will be most tempted to break: creative folders
  are full of dates. `00` grants the time-first exception to *capture-based media only*. **Exactly
  two siblings may claim it** — `creative.shoot-day-media` and `creative.raw-photo-catalogue` —
  because their material genuinely is capture-based. Any other sibling claiming time-first is
  claiming the photos exception without the photos evidence, and R1c should reject it on sight.

A sibling therefore has a node only if it differs from **that** paragraph, or from this row's
detection signals, or from its privacy posture. Differing in *media form* is not a difference:
poster, showreel, stem, cut, plate, edition, atlas, sprite and lookbook are **values of
`artifact_type`**, which is the single most important sentence in this memo for the sibling authors.

---

## The professional-versus-hobby seam, drawn explicitly

The dispatch asked for this line to be drawn so siblings can apply it. Drawn:

**The seam is not the tool, the format, the subject, the resolution, or the skill.** A working
photographer's client job and a hobbyist's weekend shoot are the same camera, the same RAW format,
the same filename pattern, and often the same subject. A personal sketch and a paid illustration are
the same `.psd` from the same application. Any test built on format or quality will be wrong in both
directions.

**The seam is engagement evidence**, and it is a checklist of structures, not of vibes:

| Engagement evidence present | Reading |
|---|---|
| a brief, a counterparty in a role slot, a delivery/handoff set, a revision round addressed to someone, an invoice against the work, a release form, a schedule naming other people | professional practice — `creative`, and a client-bearing sibling |
| **none of the above**, but real project structure: a named work, working files, linked assets, an intentional version family, exports | still `creative` — `creative.self-initiated-work`. The roster licenses this row by name, and it is the reason the seam is drawn *within* the schema |
| **no project structure at all**: saved inspiration, downloaded references, loose stock, `Untitled-1.psd` in `New Folder 2` with no export and no family | **not this schema.** Reference Clips (`00`: *"does not belong to a current project"*), or Review Later where the material is real-looking but unresolved |
| finished exports curated for showing, ordered, beside a resume or a reel, with no working files | `career.portfolio-work-samples` |

The load-bearing consequence, and the one most likely to be got wrong by a sibling author: **absence
of a client does not deactivate this schema.** It selects a template. The row's `never_alone` list
carries this as an explicit entry so that it is checkable, not merely stated in prose.

---

## Files considered and rejected

The dispatch's own test — a row that only lists what it holds has not been researched. Named
tempting false positives, and what discriminates each:

| File | Why it is **not** this row's evidence |
|---|---|
| `kitchen-remodel-inspiration-14.jpg` (kept in the JSON as the primary collision fixture) | Saved inspiration in a bulk-download folder. Design-adjacent subject, zero project structure. Discriminator: no working file, no export, no counterparty, no version family — `00`'s Reference Clips clause *"does not belong to a current project"* is the exact test. |
| `Roboto-Regular.ttf` in `~/Library/Fonts` | An **installed asset**, not a typeface project. A designed typeface has sources, a build output and a specimen; a licensed font has a licence and an install path. Belongs to `creative.stock-asset-library` at most, and usually to nothing. |
| `Company Brand Guidelines.pdf` downloaded from a client's website | Ambiguous by construction, and left ambiguous: it is a designed artefact and a governing document. Filed as `also_holds_with: business_operations` rather than claimed. |
| `Invoice 2026-041 - Northwind Ltd.pdf` (kept as a fixture) | Shares the client's organisation name with the brief, which is the whole trap. Discriminator: the line-item/net-VAT-gross/remit-to structure is finance's, and a shared org name discriminates nothing — `00`'s university-name warning reads straight across. |
| `Contract - Northwind - signed.pdf` | Not rejected but not claimed exclusively; `also_holds_with: legal`. A clause set with a parties and execution block is a legal instrument that also happens to be this work's rights record. |
| `WWDC_keynote_notes.docx`, saved industry reports, a downloaded design-trends PDF | Reading material for a practitioner, not a making record. Reading Inbox. Deliberately **not** given a `falls_through_to` slot of its own on this row: the material has nothing creative-specific about it. |
| `node_modules/`, `.git/`, `dist/` inside a generative-art repo | Removed from organisation entirely by the exclusion rule; and where the repo root fires, `code` owns the layout and this schema must not propose re-filing anything inside it. |
| `Screenshot 2026-04-02 at 14.08.11.png` (kept as a fixture) | A reference frame beside a working file. Kept precisely because the right answer is *group without copying facts* — the neighbourhood may include it, no project fact may be written onto it. |
| A `.docx` of a school essay with tracked changes and six drafts | Version-family shape identical to a manuscript. Discriminator: academic context terms and a course-code-shaped token with academic context; `creative` has no claim on a draft merely because it has drafts. |
| `Family_Wedding_2025/` of 800 RAW files with sidecars | The hardest rejection in the list, and the one the reciprocal boundary with `photos` exists for. Identical archive structure to a commissioned shoot. Discriminator: the engagement structure around it — a brief, a call sheet, a selects/delivery set, a contract. Absent all of it, this is `photos`. |
| A voice memo of a song idea, `New Recording 4.m4a` | An `.m4a` alone is nothing — the same container is a lecture, a voice note, a podcast and a rough mix. Left to Review Later unless a session references it. |

---

## The collision fixture, named

**`Family_Wedding_2025/` versus a commissioned shoot's card dump.** Both are folders of camera-original
RAW files with same-stem sidecars and a catalogue database, both carry genuine EXIF make, model,
`DateTimeOriginal` and GPS, both are named for an occasion, and both were shot on the same body by
the same person. Nothing inside the image files discriminates them.

What discriminates: **engagement structure in the neighbourhood** — a brief, a call sheet, a
delivery or selects set, an invoice, a signed release. Where it is present, the material is a job
and both readings hold (`also_holds_with: photos` — the capture reading is not destroyed by the job
reading). Where it is absent, the capture reading stands alone and `creative` must not fire.

The reciprocal, which `photos` must carry when R1c makes the edges two-way: *a personal picture
never acquires a client or a project because a professional camera made it.* The same fixture bytes
— `A047_C013_0219AB.braw` and the RAW-plus-sidecar catalogue — are named on **both** sides.

---

## Reciprocal boundaries, both directions

| Neighbour | This row must not take | The neighbour must not take | Shared fixture |
|---|---|---|---|
| `career` | a curated set of finished exports ordered for showing, beside a resume or reel | a job's working files, brief, revision rounds or delivery set, merely because the output is showable | one exported poster PDF — the deliverable of a job and page 3 of a portfolio |
| `photos` | camera originals with no engagement structure around them | a shoot's originals as a "photo event", proposing a capture-year home for a job | `A047_C013_0219AB.braw`; the RAW+sidecar catalogue |
| `code` | anything inside a preserved repository root | an assets folder merely because a repository encloses it | a game project's `Assets/` directory |
| `research` | a lab-produced figure or a venue-targeted manuscript | a commissioned data visualisation or scientific illustration with a client and a brief | a documentary's research file; a commissioned infographic |
| `finance` | an invoice, a stock-licence purchase or a print order | the creative job itself because its invoice names the same organisation | `Invoice 2026-041 - Northwind Ltd.pdf` |
| `legal` | the operative clause structure of a contract | the rights record of a named work as merely another agreement | `Model Release - J. Okafor - signed.pdf` |
| `business_operations` | an approval chain, a budget or a controlled-document header | a campaign's working files and exports because a marketing programme commissioned them | a brand guideline PDF |

---

## `proposed_fields` — the full list, and why each is an *adoption*, not a mint

Four entries, and **all four are existing canonical keys**: `project`, `stage`, `artifact_type`,
`client`. They are filed as **adoption proposals for R1c under NJ-R1a-1 option (b)**, not as new
keys. The roster names these four itself, so reusing them rather than inventing variants is the
whole discipline being observed here. Each entry carries its own `destination_eligible` reasoning,
its `reliability_ceiling` (all four `possible`) and the reason the ceiling cannot be higher without
a rule family this row has no standing to name.

**No fifth key is proposed, and one deliberately is not.** `creative.licensing-rights`,
`creative.stock-asset-library` and `creative.typeface-font` all want to state a usage grant — what
may be used, where, for how long — and no canonical key holds it: `record_type` is finance's,
`purpose` is fenced to College applications by PR-1, `artifact_type` names the document rather than
the grant. That is a genuine field-shaped hole and it is recorded as such in `open_question` (2).
Minting a key for it here, on a schema that declares no fields, at the exact point of maximum
temptation, would be the 574's original mistake performed knowingly. It is left for R1c.

`proposed_context_terms` carries 37 practice terms (`brief`, `deliverables`, `revision`, `amends`,
`sign-off`, `press-ready`, `picture lock`, `call sheet`, `usage rights`, `model release`, …). These
are **proposals**, not `00`'s floor — `00`'s named context-term floor is the academic one
(`syllabus`, `lecture`, `credits`, `instructor`, `semester`) and this row does not pretend otherwise.

---

## Neighbours considered that did **not** get an edge

- **`academic`** — a student's design-school portfolio is coursework with a course code and academic
  context. That is `academic` firing on its own evidence, not a creative collision; no shared
  evidence item is contested.
- **`college_applications`** — a portfolio submitted with an art-school application is an
  application document type. The packet is `college_applications`; the works inside it are whatever
  they already were. No edge: the roles do not compete for the same evidence.
- **`identity`** — releases carry identifying details and one is a fixture with
  `also_schema: identity`, but the *schema-level* relationship is protection, not a shared reading.
  Handled through `sensitivity` and the Protected Records fallthrough rather than an edge, which is
  what `photos.json` does for the same situation.
- **`hr`** — freelance crew paperwork looks employer-shaped. Left alone: crew agreements are the
  engager's records, and reaching for `hr` from a creative row would claim a world this row cannot
  see.
- **`retail_hospitality`, `government`, `nonprofit`** — all three commission creative work. That
  makes them *values of `client`*, not neighbours. Naming them as edges would rebuild the industry
  forest ALIGNMENT.md removed.
- **`engineering`, `construction_property`** — genuinely close to `creative.interior-design` and
  `creative.architectural-visualisation` (a drawing set under revision is engineering's own anchor).
  Deliberately **not** edged from this row: the contested evidence sits at *template* level, on those
  two siblings, and R1c should place it there rather than have the schema row pre-empt it. Flagged
  here so it is not lost.

---

## Sparse-file discipline

Four of the thirteen fixtures carry `group_without_copying_facts: true`, and this world needs the
rule more than most, because its sparse files are the *normal* case rather than the ugly edge:
`Untitled-1.psd`, a reference screenshot sitting beside a working file, an unreadable
`.logicx` package, and a `submission.zip` whose members are never extracted. In each, the
neighbourhood may legitimately group the file while **no** project, stage or client fact is written
onto it. This is `00`'s `HW 3.pdf` rule applied to a world where nearly every working file is an
`HW 3.pdf`.

Every fixture also carries `"any creative fact - the schema declares none"` in `must_not_conclude`,
so the placeholder status is checkable file-by-file rather than only in the header.

---

## Audits run before returning

- `python3 -m json.tool planning/domains/nodes/creative.json` → parses.
- **Key set identical to the landed sibling** `business_operations.json`, in the same order —
  compared programmatically, empty symmetric difference.
- **Every quotation grep-verified verbatim** against `00-database-agent-product-design.md`
  (whitespace- and curly-quote-normalised), 42 quote-shaped spans checked. Two "unmatched" results
  were confirmed by hand to be regex artefacts spanning adjacent quotations, not bad quotes. Four
  real defects were found and fixed this way: an elided `...` inside one quotation (split into two
  separate quoted spans), a truncated `Revocation cannot…` sentence, a truncated
  `Correct abstention…` sentence, and an em-dash pair rewritten as spaced hyphens in the
  `Unsupported or Encrypted` definition. The one non-`00` quotation is from `ROSTER.md` §7 and is
  attributed there.
- **Every `file_examples.source_type` and every `file_kinds.source_types` member is in
  `SOURCE_TYPES`** — checked against `src/evidence_shape/vocabulary.py`'s list.
- **Every edge id exists in `roster.json`** (`career`, `photos`, `code`, `research`,
  `business_operations`, `legal`, `finance` as `also_schema` on a fixture) — checked
  programmatically against the roster's schema and node ids.
- **Every `falls_through_to` and every `falls_through_if_inactive` is one of the nine residual
  names.**
- **No numeric threshold, statistic or file count.** A first draft asserted a count of templates
  inside `open_question`; it was removed on this audit and replaced with named examples.
- `fields: []`; no canonical key minted; all four `proposed_fields` keys already exist in
  `canonical_fields.json`.
- **Files written: exactly two** — `planning/domains/nodes/creative.json` and this memo. Nothing
  else was touched.

---

## NEEDS-JOSEPH (this node only)

- **NJ-R1a-1 (remainder) · Does `creative` declare fields, fold, or stay field-less?**
  The roster records option (a) as taken and adds that *"If a later pass wants option (b), the
  candidate fields are still the existing keys `project`, `stage`, `artifact_type`, `client`;
  nothing here forecloses it."* This row **does not resolve the remainder** — this is the row where
  a silent resolution would be least visible and most consequential. Alternatives, with costs:
  **(a) stay field-less** — 41 templates recommend no dimensions and a creative corpus is grouped
  but never structured; costs the family its only folder shape and leaves `client` unavailable to
  the rows that most need it. **(b) declare the four existing keys** — mints nothing, leaves D6
  untouched, makes the default template real and gives the 41 siblings something to differ from;
  costs the D1 deferral its uniformity, since career/identity/medical/legal would remain field-less
  while creative would not, and Joseph would have to say why creative is the exception.
  **(c) fold into `research`** — saves a schema row; fails on the counterparty role, on the privacy
  posture, and on the majority of the family that `lab`/`venue` cannot describe.
  *This row's recommendation, offered and not taken: (b), narrowed so that only `project` and
  `artifact_type` open folder levels at launch.*
- **NJ · The rights-and-licence hole.** Three siblings need to state a usage grant and no canonical
  key holds it. No key proposed here, deliberately. R1c's call.
- **NJ · The serious-amateur middle of the professional seam.** A hobbyist with real project
  structure and no counterparty is indistinguishable from a professional's self-initiated work.
  `creative.self-initiated-work` currently holds both. Whether that is one template or two is a
  decision about someone's real filesystem.
- **NJ · Do 41 templates survive R1c on a field-less schema?** If the remainder resolves to (a),
  the dimensions leg of the node test is unavailable to all 41 equally, and each must justify itself
  on detection signals and privacy rules alone. Several — `creative.print-production`,
  `creative.motion-graphics`, `creative.sound-design` — may then be `artifact_type` values on a
  neighbour rather than rows.
