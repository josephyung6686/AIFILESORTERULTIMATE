# research.reading-library — lab notes

Date: 2026-08-22
Roster row: `kind: template`, `schema_id: research`, `launch: placeholder`, `provenance: inference`
Verdict: **node kept** (`refuse_node: false`). The three-limb node test is argued in the JSON's
`node_test` block; the short version is below under "Why this is not the residual wearing a
template id".

## Sources used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node file
  was grep-matched against this file before it was written; the check script is in the session
  scratchpad and all thirty-eight candidate spans came back OK except one I then dropped
  (`"password-protected, malformed, nested, or oversized archives"` — the real sentence is worded
  differently, so no quote is used for the encrypted-archive point and it is marked `inference`).
- `planning/domains/_CONTRACT.md` (entry shape, rules 8/11–15), `planning/domains/CONNECTION.md`
  (node test §2, no inheritance §3, closed edges §5, field identity §6, owners §7),
  `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — confirmed the id, kind, `schema_id`, the ten research rows, and
  that `academic.coursework` and `research.manuscript-publication` are real roster ids before
  writing either collision edge.
- `planning/domains/canonical_fields.json` — every field named in this node (`project`, `stage`,
  `artifact_type`, `lab`, `venue`, `authored_by`) resolves to a canonical key. No key was minted.
- Landed neighbours, read to align and **not** rewritten: `planning/domains/nodes/research.json`
  (the schema; its `never_alone` list is the direct source of this row's inverted signal set, and
  its `Ravikumar_2019_NatureMethods.pdf` fixture is the same file this row is built around) and
  `planning/domains/nodes/research.project-workspace.json` (refused; its
  "paper saved into a project directory" fixture is the cross-fixture for my third `never_alone`).
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — all eleven fixture `source_type` values and
  all six `file_kinds.source_types` values are members.
- `planning/deferred-catalogues/06-citation-identifier-patterns.md` — consumed, not invented. This
  row's recognition genuinely rests on that list's `doi`, `arxiv`, `isbn`, `issn` kinds, on its
  rule that a shape match without a passing check digit is not a hit, on its rule that a bare
  number is never an identifier, and on its `ZONE_BY_STRUCTURED_KIND` mapping of the `citation`
  kind to the `reference_list` zone — which is the mechanism behind this node's constitutive
  `never_alone`. No pattern, regex or catalogue content is reproduced here (R2/R4/R6's, not mine).

## Why this is not the residual wearing a template id

The obvious refusal argument is: *00 already has a Reading Inbox; this row is that residual with a
schema pointer bolted on.* It fails on CONNECTION.md §5's fifth invariant, which says a residual
home that shadows a domain template must be joined to it by `falls_through_to` or it is a
duplicate rather than a fallback. The residual is 00's home for material with "no reliable deeper
association"; this template is the case where an association **is** evidenced on the file. Refusing
the id would not delete the situation — it would leave 00's own residual unattached to the domain
whose vocabulary defines it, and it would leave the research schema's default template
(`project → stage → artifact_type`) as the only thing P10 could fit to a reading set, which
recommends a `stage` level that somebody else's published paper can never fill.

The second and third limbs are independent of that argument: the detection signals are the schema's
`never_alone` list read positively (a DOI/masthead/citation structure recognises this situation and
is explicitly insufficient for the schema's), and the sensitivity value differs — this is the one
face of Research that carries no holder-personal content.

## The central finding, stated plainly

**The leading dimension of this template is the fact the situation usually cannot supply.** A paper
by other people supplies `artifact_type`, `venue` and `authored_by` from its own front matter, and
supplies `project` only when the holder's own use of it is evidenced *on that file*. A project
token in a filename prefix sits beside a **third party's** publication structure, not beside the
holder's own research-artifact context, so it reaches `possible` and no higher — the schema's
`validated` rule family does not fire. What that leaves is a reviewable P9 membership, exactly the
`HW 3.pdf` discipline: the paper joins the PVA/RDP neighbourhood without acquiring
`project = PVA/RDP`. P10 can still populate the branch, because 00 populates templates "from the
facts and accepted groups that already exist in the evidence database" — an accepted group, not a
copied fact. Everything else in the node follows from this: `stage` struck, `Reading Inbox` as the
expected outcome rather than a failure, and abstention as a correct result.

## Files considered and rejected

- **`.ics` for a journal-club or reading-group meeting.** Rejected. A calendar event about a
  reading group is a meeting record, not a reading item; `calendar` is a `SOURCE_TYPE` and the
  research schema row already carries the `Lab meeting — Chen Lab.ics` fixture for the
  never-alone lesson. Adding a second copy here would be format-as-schema by the back door.
- **`.vcf` of a co-author or a corresponding author.** Rejected outright — 00 says contact data
  "should normally be privacy-protected rather than used to create folder proposals".
- **A `Highlights and notes.md` export from a reading app.** Tempting, and dropped: the holder's
  own notes on a paper are the holder's artifact, and once notes accumulate a project context they
  are project-workspace material. Keeping it would have blurred the one line this row is built on
  (whose artifact is it).
- **A textbook PDF for a course.** Rejected as a fixture because it splits identically to
  `Reading list — Week 4.pdf` — the course-code-plus-academic-context pattern decides it — and one
  collision fixture per edge is enough.
- **The holder's own manuscript with a long reference list.** *Not* rejected — promoted. It is
  named inside the first `never_alone` as the tempting false file, because a masthead detector
  without the reference_list zone restriction would file the holder's own work as reading material.
  It is not repeated as a `file_examples` row because it is already the research schema row's
  fixture and rewriting a neighbour's fixture is not this node's job.

## `proposed_fields` — none, deliberately

Two candidates were considered and both refused.

- **A topic / reading-area field.** This is what users think a reading library is organized by
  ("immunology", "transformers"). There is no canonical key for it, and minting one would be the
  574's exact failure mode: a field with no rule family that can fill it, populated by free-form
  model labels, opening a folder level no deterministic evidence can ever justify. 00 keeps topic
  and purpose apart deliberately and names no topic field for any domain. The honest coverage is
  `project` when an association exists, and the residual when it does not.
- **A DOI / citation-identifier field.** Refused as unnecessary rather than wrong. The identifier
  is already an **observation** — 00 requires the extractor to preserve "DOI values, citations,
  identifiers" — and the injected catalogue's own rule is "P5 finds; P6 decides". Its useful jobs
  here (dedup a preprint against its published version, link a reading item to a manuscript's
  reference list) are served by the universal `duplicate_family` / `version_family` facts and by
  P9's typed `direct references` edge. A new field would add a column and no new capability.

Both are recorded here rather than in `proposed_fields` because neither is a proposal — they are
decisions not to propose.

## Neighbours considered that did not get an edge

- **`research` (the schema).** No edge authored. `uses_schema` is expressed by `schema_id` and is
  the roster's; a template never lists its schema's fields (CONNECTION §3 rule 1), which is why
  `fields` is empty with a note explaining that the reachability finding lives in the fixtures.
- **`academic` (the schema) — my `must_consider_neighbors` row.** No `also_holds_with` edge, and
  the reason is contractual, not substantive: `also_holds_with` **joins schemas only**
  (CONNECTION §5), and this is a template row. The relationship is real — the
  `PHYS1401_reading_Feynman1963.pdf` fixture carries academic evidence and reading evidence on
  disjoint page ranges — and it is already asserted where it belongs, on `research.json`'s
  `also_holds_with: academic`. The fixture records it via `also_schema: "academic"`. The
  template-level consequence I *could* author is the collision, and I did:
  `academic.coursework`.
- **`research.project-workspace`.** No edge. It is refused, and the relationship is a shared
  fixture rather than a collision: a downloaded paper sitting in a project directory is a
  never-alone case for both of us, and I cite it as such without pointing an edge at a refused row.
- **`research.dataset-analysis`, `research.grants-funding`, `research.ethics-compliance`,
  `research.lab-notebook-protocols`, `research.thesis-dissertation`.** No edges. None of them
  shares an evidence item with a third party's published paper; a supplementary dataset published
  *with* someone else's paper is the nearest miss, and it arrives as an archive member of the
  reading item rather than as a competing claim.
- **`research.conference-presentation`.** Considered and dropped. A downloaded conference paper is
  a reading item and a hosted proceedings deck is that row's, but the discriminator is the same
  whose-artifact-is-it question already carried by the `research.manuscript-publication` collision.
  Two collisions with one shared discriminator is the honest count; three would be padding.
- **`code`.** No edge. A `.bib` file is `code_structured` by routing only, and the routing signal
  proves nothing — 00's extension rule and the file-kind never-alone invariant both cover it.

## Also recorded

- `role_split` is empty. The split this situation raises — the paper's authors versus the holder —
  is already `authored_by`, whose canonical row is not destination-eligible, and the
  `venue ↔ lab` split is authored on the schema row. A copy here would duplicate a field-level
  edge that CONNECTION §6 says lives in the canonical list.
- `work_types` adds seven values (`review article`, `conference paper`, `book chapter`,
  `technical report`, `thesis by another author`, `bibliography file`, `annotated reading copy`)
  to the two the schema row already has. These are **values of `artifact_type`**, not fields and
  not nodes; folding them into the schema row's list is R1c's, not mine.
- `falls_through_to` carries four residual names, all spelled 00's way, and every
  `falls_through_if_inactive` in the fixtures resolves to one of them. (This is the gap
  `research.project-workspace` flagged against the schema row; it is not repeated here.)

## NEEDS-JOSEPH (this node only)

1. **Is there a holder-identity value?** This template's sharpest discriminator against
   `research.manuscript-publication` — whether the author list is the holder's or somebody else's —
   is not deterministically evaluable, because the product holds `authored_by` as a field but has
   no user-confirmed value naming *the user* and their name variants. Without one, whose-paper-is-
   this becomes an LLM role question on every publication-shaped PDF, which is expensive and
   abstains often; with one, it is a word-boundary comparison. Asking the user once for their own
   name and affiliations creates a **value**, not a field, so it does not touch the schema — but it
   is a product decision about onboarding and it is Joseph's.
2. **May a reading library branch on `venue`?** `venue` is destination-eligible on the canonical
   row and this template deliberately declines to branch on it, on 00's own warnings about a level
   that produces one child and about creating a large number of tiny folders. Some readers do
   organize by journal. Fork: is that a user-side reordering of this template (my assumption), or a
   second template on the same schema? It decides someone's real folder structure, so it is not
   resolved here.
