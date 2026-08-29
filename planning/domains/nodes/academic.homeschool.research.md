# academic.homeschool — R1b lab notes

Row: `kind: template`, `schema_id: academic`, `launch: placeholder`, `provenance: proposal`.
Verdict: **node accepted** (not refused). Reasons below.

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node
  JSON was `grep -F`-verified against this file **before** it was written; 40 candidate spans were
  checked, all 40 matched, and no span was written from memory.
- `planning/domains/_CONTRACT.md` — entry shape; rules 8 (snake_case + a template may only branch
  on a field its schema declares), 11–14 (kind, uses_schema, browse-only parent, closed edges).
- `planning/prompts/ALIGNMENT.md` — the schema/template/value/group/residual split; work types are
  values; a template that only repeats its schema's default is not a node.
- `planning/domains/CONNECTION.md` §§2–7 and `CONNECTION-EXAMPLES.md` fixtures 1, 5, 6, 7, 8.
  CONNECTION wins over the dispatch prompt where they differ; no divergence was found in practice.
- `planning/domains/roster.json` — confirmed the row, and confirmed every edge target id exists.
- `planning/domains/canonical_fields.json` — no new key minted; `subject` (not `course`), D6 as
  ratified.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` (14) and `RELIABILITY_STATES` (6);
  `EXTRACTOR_RELIABILITY_STATES` is `direct` | `possible`, which is what forced the `subject`
  finding below.
- Neighbour nodes already landed: `academic.json`, `academic.coursework.json`,
  `academic.teaching.json`, `academic.k12-schooling.json`. Read to align edges and to avoid
  re-deriving a second spelling of the same proposal. None was modified.

Mechanical checks run on the emitted JSON: parses; all 14 `file_examples.source_type` ∈
`SOURCE_TYPES`; all `file_kinds.source_types` ∈ `SOURCE_TYPES`; all `collides_with.domain` and
`role_split.neighbor` ids on the roster; all `falls_through_to` and every
`falls_through_if_inactive` one of §7.3's nine names, spelled 00's way; every
`template.dimension_order` entry canonical **and** declared by the `academic` schema row; every
`facts_legal` key declared by that schema; no number in the file that is not a filename token, a
year inside a worked example, or part of a verified quotation. `planning/domains/check.py` was run
before and after and reports the unchanged legacy baseline (14 files, 574 entries, 566 in-file
problems, 0 cross-file) — it does not scan `nodes/`, so this node adds nothing to it either way.

## Why this is a node and not padding

The node test (CONNECTION §2) asks whether detection signals, recommended dimensions, or privacy
rules differ from the schema's default template (`academic.coursework`). All three do, and the
first is the load-bearing one:

1. **Detection signals differ at the root.** The Academic schema's headline rule is 00's
   course-code-plus-context pair. That rule fires on essentially **nothing** in a homeschooling
   corpus: this material names plain subjects (Math, Reading) and curriculum titles, never
   code-shaped tokens. A template that waited for a course code would activate on zero files in
   this household. The signals that do work — home-instruction compliance vocabulary, a labelled
   lesson-plan table, a curriculum-title token, an attendance-log column shape, a parent
   attestation without a registrar line — are not in coursework's set and are not in K-12's set.
2. **Recommended dimensions differ.** `school` is dropped from the default order because in a
   household-run situation there is usually no institution to fill it (details below).
3. **Privacy rules differ.** The records are about a minor who is not the holder *and* part of the
   corpus is a filing to a government education authority, which sits beside the protect-first
   legal set rather than inside ordinary coursework.

## The two findings worth a reviewer's attention

**Finding 1 — `subject` in this situation cannot be produced by the design's own rule for it.**
00 makes `subject` a *validated* fact via a course-code pattern plus academic context. Homeschool
`subject` values are plain words. Under P4 D11 an extractor may write only `direct` or `possible`,
so the honest reliability picture here is: `direct` when read from a **labelled Subject slot** in a
lesson-plan or record-keeping table (which is why the labelled-table signal is listed second, not
last), and `possible` from a filename or free text — with `validated` reachable only through a
different rule family, a curriculum-title gazetteer matched at word boundaries plus
home-instruction context (contents are R4's; no gazetteer content and no regex is written here).
This is not a defect in the schema — it is a template-level fact about which evidence exists in
this situation — but it does mean a `subject` branch is thinner here than in coursework, and the
node's `template.why` says so rather than hiding it.

**Finding 2 — three different institutions compete for `school`, and only one is legitimate.**
The regulator that receives a notice of intent (ruled out here — it is neither attended nor
applied to, and it has no field), an umbrella or cover school (genuinely institutional,
gazetteer-confirmable, present for only some households), and a household-invented home-school
name on a parent-issued transcript (`possible` forever; no gazetteer will confirm it). Accepting
the third puts a value the holder made up into the same field as Columbia; refusing it leaves the
homeschool transcript — the document that matters most when this corpus meets an admissions
office — with no school fact. That fork is the node's `open_question`; the recommendation
(drop `school` from the default order, offer it as an optional branch on umbrella-school evidence)
is what R1 builds on meanwhile.

## Dimension order

Recommended `["term", "subject", "work_type"]`, `time_first: false`.

`term` leads because a homeschool year is the unit the household plans, logs and reports in, and
because the compliance set is per-year. This coincides with `academic.teaching`'s order, which is
fine — the node test compares a template against **its schema's default**, not against a sibling,
and the two differ everywhere else. `time_first` stays false deliberately: `term` here is an
academic-year fact read from dedicated term patterns, not a capture date, so this is not the
photos exception 00 carves out.

The level this household actually files by **first** is the child, and no declared field names it.
That is stated in `template.why` and in `proposed_fields`, and it is not smuggled into
`dimension_order` — a template may only branch on a field its schema declares.

## Files considered and rejected

- **A curriculum publisher's teacher guide with no household marks** — rejected as a *file
  example* of this template's own set but kept as the `never_alone` case and promoted to a full
  collision fixture (`Sonlight 2026 Catalog.pdf`). It is the strongest tempting false file this
  template has: saturated with the exact vocabulary, owned by nobody in the household.
- **An immunization or medical-exemption record** — a real part of many homeschool filing sets,
  rejected because `academic.k12-schooling` already carries that fixture against
  `medical.dependant-child-health` and duplicating it would restate a neighbour's collision rather
  than add one. This template's medical adjacency is covered by the protect-first note in
  `sensitivity_why`.
- **A public-library reading-programme log** — rejected: it evidences reading, not schooling, and
  a reading log only becomes this template's when it sits inside the household's own record set.
  It would have been an example of exactly the invented association 00 warns against for isolated
  files.
- **A `.vcf` of co-op families** — rejected outright. CONNECTION fixture 6: contact data "should
  normally be privacy-protected rather than used to create folder proposals". It is not in
  `file_kinds` either.
- **A tuition receipt on its own** — rejected as an example; it is finance's, and the co-holding
  case is carried by the archive fixture and the `finance.receipts-expenses` collision instead.

## proposed_fields justification

One key, `student`, and it is **deliberately the same key `academic.k12-schooling` already
proposes**, not a second spelling of the same idea. That neighbour's node was read first precisely
to avoid minting `child`, `data_subject` or `pupil` beside it — 2,295 field names for one
vocabulary is the 574's defining failure and the parallel swarm is where it would recur. R1c
should merge these into one canonical row with a `role_split` against `authored_by`, or reject it
once; either outcome is fine, two rows is not.

The homeschool case strengthens the argument rather than repeating it: the parent is *both* the
author and the keeper, so `authored_by` is filled by the one person the record is never about, and
`instructor` is filled by that same person too. Every per-child artifact in the corpus —
worksheet, portfolio, attendance log, evaluation letter, transcript — is unseparable without it in
a multi-child household. It is **not** placed in `dimension_order`.

## Neighbours considered that did not get an edge

- **`legal` (the schema row, and the roster's `must_consider_neighbors` entry for this node).**
  No edge authored, for a shape reason, not a judgement one: `collides_with` joins same-kind pairs
  only and `also_holds_with` joins schemas only (CONNECTION §5), so a `kind: template` row cannot
  point at a schema with either. The real confusion was routed to the template that holds it,
  `legal.personal-legal-matters`, with the discriminating evidence named. If the schema-level
  relation matters (a compliance filing that is genuinely both), it belongs as
  `also_holds_with` on the `academic` and `legal` **schema rows**, which is R1c's to reconcile.
- **`applications.k12-admission`** — a homeschooling family re-enrolling a child in a school is a
  real confusion, but `academic.k12-schooling` already carries that collision and the
  role-split it implies. Adding a second copy from here would be noise; the role split this node
  does carry points at `applications.undergraduate-packet`, where the homeschool transcript makes
  both roles appear **on one page**, which is the sharper and unclaimed case.
- **`academic.iep-accommodation-plans`** — homeschooling a child with a service plan is real, but
  the discriminating evidence is identical to the one that node's neighbour already states
  (accommodation-plan vocabulary and its dominating privacy rules), so an edge from here would add
  a link without adding a discriminator.
- **`photos.scanned-documents`** — every portfolio sample is a scan or a phone photo of a paper
  page, and the temptation to author an edge was real. Rejected: the relation is already carried
  correctly as `also_schema: "photos"` plus `group_without_copying_facts: true` on the HEIC
  example, which is the fact-level truth (two schemas, disjoint evidence). A template-to-template
  collision would assert a confusion that does not exist — nobody mistakes a photo *of* a
  worksheet for a photo event.
- **`finance.student-financial-aid`** — no plausible overlap at the K-12 scale this situation
  mostly occupies.

## Prompt vs CONNECTION

No divergence encountered. Where the dispatch prompt said "if present" of `CONNECTION.md` and
`CONNECTION-EXAMPLES.md`, both are present and were treated as binding. D6/D2 followed as
ratified: snake_case keys, the academic key is `subject`. `parent_id` is `null` and was not
authored (PR-5: R1b never authors it). `shares_field` is not authored anywhere.

## NEEDS-JOSEPH (this node only)

**NJ-homeschool-1 — may `school` hold a household-invented home-school name?**
Full statement is the node's `open_question`. The fork in one line: a parent-issued transcript's
"Torres Family Academy" is either a legitimate `school` value that can never rise above
`possible`, or it is a self-issued label the product should hold as prose and never propose as a
folder level. Deciding it also decides whether a homeschool transcript reaching an admissions
office carries a school fact at all. This is a decision about someone's real filing life and about
whether the product treats an invented institution as an institution — not a decision this node
may resolve.

Deliberately **not** re-filed here: the missing field for the child a record is about. It is
already `academic.k12-schooling`'s open question, the same proposed key appears in this node's
`proposed_fields`, and filing it twice would put one question in two places for Joseph to answer
twice.
