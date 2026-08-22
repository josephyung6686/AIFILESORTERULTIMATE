# `research` — lab notes (R1b)

Roster row: `kind: schema`, `domain_id: research`, `launch: full`, `provenance: design`.
Node test: **passed, not refused.** Output: [`research.json`](research.json).

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node
  JSON was grep-checked against this file before it was written; the final check reports
  **43 quoted spans, all verbatim, 0 unverified**.
- `planning/01-product-design-structured.md` — only the sections covering this domain area:
  §2.2 (PDF/DOI evidence), §3.5 (how facts are produced), §3.8 (roles, not just entity types),
  §3.9 (purpose), §3.11 (domain-scoped schemas — the Research field sentence), §3.15 (launch
  scope), §4.2 (seeds — the research seed sentence), §4.9 (stop rules — the PVA/RDP dual group),
  §5.4 (the template dimension table), §5.5 (project-before-time), §7.2–7.3 (residual library).
  Used only as a locator; every claim is quoted from `00`.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md` (examples 2, 3, 5,
  6, 7, 8 all bear on this node), `planning/domains/roster.json`,
  `planning/domains/canonical_fields.json`, `src/evidence_shape/vocabulary.py`.
- Neighbour node files: **none existed** when this ran (`planning/domains/nodes/` held only
  `.gitkeep`). Edges here are authored one-sided; R1c owns reciprocity.
- `planning/deferred-catalogues/` — not consumed. Two rule families here *will* consume R4
  gazetteers (organizations for `lab`, venues for `venue`), and this node names the family
  without inventing a single gazetteer member or a regex (R4 is R4's, R2 is R2's).

## Why the node was not refused

The refusal test asks whether the field set is genuinely distinct. It is: `stage`, `lab` and
`venue` are referenced by no other roster schema, and the two shared keys (`project`,
`artifact_type`) are shared with `code` **by canonical reference**, which is precisely what makes
`shares_field` a derived edge rather than an argument for merging the two schemas. Five fields
sits inside `00`'s "usually three to six that may help build a future folder proposal". `00` also
names the domain outright, twice — the field sentence and the launch list — so this row is
`provenance: design` rather than inference.

The one thing that could have made this a padding node is the temptation to mint a schema per
artifact type (manuscript / protocol / dataset). Those are values of `artifact_type`; the roster
already carries them as **templates** on this schema (`research.manuscript-publication`,
`research.lab-notebook-protocols`, `research.dataset-analysis`, …), which is where detection
signals and dimension order legitimately differ.

## Files considered and rejected

Sixteen file examples survived into the JSON, chosen so every `source_type` claimed on
`file_kinds` is backed by a real file. What did **not** make it, and why:

- **`interview_participant_04.m4a`** (`audio_video`). Real for qualitative research, and `00`
  supports the extractor. Dropped from `file_kinds.source_types` because transcripts arrive only
  "under an explicit privacy and compute policy", so claiming the source type would assert a
  capability this node cannot demonstrate. If it lands, it lands via `research.ethics-compliance`.
- **`contacts.vcf` of a collaborator list** (`contacts`). Excluded deliberately: `00` says VCF
  data "should normally be privacy-protected rather than used to create folder proposals", and
  CONNECTION example 6 already fixes the answer at `{}` for placement purposes.
- **A `filesystem`-only row.** Every file has filesystem evidence; listing it as a plausible
  file kind for this schema would assert the one thing the never-alone rule forbids.
- **`Poster_v2.pdf`** — folded into `artifact_type` values rather than given a file row; it
  behaves identically to the abstract for detection and would have padded the list.
- **A second collision fixture against `college_applications`** (a transcript inside a research
  packet). Dropped: the pair's real relationship here is `also_holds_with`, and `00`'s own
  abstract case covers it better than an invented one.

## `proposed_fields` — deliberately empty, and why

Nothing was proposed. The candidates I worked through and rejected:

- **`doi`.** `00` extracts "DOI values, citations, identifiers" as *evidence*, not as a fact
  field. A DOI is an identifier for a value (this venue, this artifact), which is the values
  table's job; minting a field for it would be the 574's failure mode in miniature — a private
  key for something the shared vocabulary already reaches. Left as evidence supporting `venue`
  and `artifact_type`.
- **`instrument`, `sample_id`, `run_id`.** Values and evidence. Also the exact shapes `00`'s
  narrow-date rule warns about ("numbers that look like years but are course identifiers, version
  numbers, build numbers, ZIP codes, or other unrelated values").
- **`funder` / `sponsor`.** The grant situation needs it, but `institution` already carries an
  organization-with-a-role in the canonical list and `research.grants-funding` is a template row
  belonging to another agent. Recorded here rather than minted.
- **`purpose`.** PR-1 holds it inside College-applications. A purpose-coherent research packet
  activates this schema on its own evidence or falls through to residual. No clone minted.

The one **field-level finding** recorded instead of a proposal is in `role_split[]`: the canonical
row for `lab` carries an empty `role_split_with`, yet `lab` versus `school` is the same
organization string in two roles — `00`'s Columbia sentence names "research venue" and "authoring
school" side by side. Widening the canonical list belongs to R1c or to Joseph; this node records
the finding and does not touch `canonical_fields.json`.

## Reliability ceilings — the two that took work

- **`stage` is the awkward one.** It is a destination dimension in `00`'s own recommended order,
  yet it is almost never a labelled slot. I set the ceiling to `validated` on one honest path — a
  submission-lifecycle term (cover letter, response to reviewers, proof) co-occurring with
  manuscript or venue evidence, including in an archive manifest — and put the ordinary prose case
  into `needs_llm`. The consequence worth flagging to P10: a `stage` branch will often be filled
  by `llm_supported` facts, so that level deserves review rather than automatic placement. A `v7`
  suffix is **not** stage evidence; it is a `version_family` signal.
- **`venue` is zone-restricted, not context-restricted.** The failure is a journal name appearing
  once in a bibliography, which `00` addresses directly in its positional-weighting sentence about
  a reference list on page eighteen. So the rule family names the zones (filename, title,
  page-one heading, cover-letter salutation, editorial subject line) instead of naming context
  terms — the opposite shape to `lab`, which is context-restricted because a bare organization
  name carries no role.

## Neighbours considered that got no edge

- **`photos`** — a research figure is an image, and `media_type` is a photos field. No edge: the
  overlap is a `source_type`, not evidence, and `file_kind_plausible` is never-alone by
  construction. Adding a collision here would encode format-as-schema.
- **`career`** — a CV lists publications and venues, so a venue gazetteer hit could support both.
  Left unauthored because career is a field-less placeholder (D1 as narrowed, PR-6): there is no
  field set to collide over yet, and asserting the edge now would prejudge the deferred schema.
  Flagged for R1c to revisit **when the career schema lands before P10**.
- **`identity`, `legal`** — an ethics or data-transfer agreement touches both, but that situation
  is the `research.ethics-compliance` template's, not this schema's; the schema-level medical edge
  is the only safety join with a file behind it here.
- **`finance`** got an edge only because a concrete fixture demanded it
  (`PVA-RDP_budget_FY26_sponsor.xlsx`); `academic`, `code`, `college_applications` and `medical`
  each carry at least one fixture too. No edge in the JSON is asserted without a file that shows it.

## Where CONNECTION overrode the dispatch prompt

- The prompt says "D6 is unset". CONNECTION §6 and `_CONTRACT` rule 8 record D6 as **ratified**;
  keys here are snake_case and the academic key referenced in the collision signal is `subject`.
- `shares_field` between `research` and `code` (via `project`, `artifact_type`) is real and is
  **not authored** — it is derived from the canonical references. The `also_holds_with code` edge
  says something different (both schemas active on one file) and is authored on purpose.
- `parent_id` stays `null`; PR-5 leaves browse shelving to R1c.
- No `related_to`, no invented edge key, no numeric threshold anywhere in the node.

## NEEDS-JOSEPH (this node only)

1. **Is a PI-named `lab` an organization or creator identity?** `lab` is `destination_eligible` on
   the canonical row, but most labs are named after their principal investigator, so a `lab`
   folder level can quietly become the authorship collector `00` forbids ("It should avoid using
   authorship or creator identity as a destination dimension"). The default template here sidesteps
   it by branching only on project → stage → artifact_type, but a lab-shared-protocol template
   legitimately would branch on `lab`. This decides someone's real folder structure, so it is not
   resolved here. Carried in the node's `open_question`.
2. **Should `lab ↔ school` and `venue ↔ lab` become authored `role_split` pairs in
   `canonical_fields.json`?** `00` supplies the ambiguity but names only three role pairs
   explicitly. Recorded in `role_split[]`, not written into the canonical file.
3. **`stage` as a folder level filled mostly by `llm_supported` facts** — acceptable, or should
   the Research template's default order flatten to project → artifact_type until a rule can
   confirm stage? `00` recommends the three-level order; this is a policy question about how much
   an unreviewed model-derived dimension may shape a tree.
