# career.portfolio-work-samples — lab notes (R1b)

Date: 2026-08-22
Kind: `template` · `schema_id: career` · `launch: placeholder` · `refuse_node: false`
Output: [`career.portfolio-work-samples.json`](career.portfolio-work-samples.json)

---

## 1. Sources actually used

- **`planning/00-database-agent-product-design.md`** — read in full. Every quoted span in the node
  JSON was grep-verified verbatim against this file **before** it was written; a mechanical
  re-check after writing confirmed 42 of 42 quoted spans present (the one regex "miss" is an
  apostrophe artifact in `other schemas' rows`, not a quotation).
- **`planning/domains/CONNECTION.md`** — sections 2 (node test), 3 (no schema inheritance),
  4 (activation, never-alone), 5 (closed edge vocabulary + invariants), 6 (canonical fields,
  `destination_eligible`), 7 (four objects), plus PR-6 (career placeholder writes no field rows).
- **`planning/domains/CONNECTION-EXAMPLES.md`** — consulted for fixture shape; the `.ics` and
  no-EXIF fixtures are the pattern this node's screenshot and design-format never-alones copy.
- **`planning/domains/_CONTRACT.md`** — rules 5 (sensitivity phrase only), 6 (`residual_template`
  vs `domain`), 8 (snake_case; D6 ratified, academic key is `subject`), 10 (**no career field
  rows**), 11–15 (kind, `uses_schema`, browse-only `parent_id`, closed edges).
- **`planning/prompts/ALIGNMENT.md`** — the node test's "would only repeat its schema's fields and
  dimension_order" clause, and "work types are values".
- **`planning/domains/roster.json`** — confirmed id, kind, `schema_id: career`,
  `file_kind_owner: ["design_creative"]`, and every edge target id.
- **`planning/domains/ROSTER.md`** §4–§7 — the refused-creative-projects hole (§5 item 1) and
  NJ-R1a-1, which this row is the surviving face of; also the `file_kind_owner` mapping table
  (§3 item 4) that assigns `design_creative` here.
- **`planning/domains/canonical_fields.json`** — checked every key I considered
  (`project`, `artifact_type`, `client`, `our_firm`, `authored_by`, `venue`, `repository`) to
  confirm no new key is needed.
- **`src/evidence_shape/vocabulary.py` `SOURCE_TYPES`** — all twelve `source_type` values used
  across the file examples validated against the closed fourteen by script.
- **Sibling nodes already landed**: `career.json` (my schema), `research.project-workspace.json`
  (the refusal shape), `research.reading-library.json` / `research.conference-presentation.json` /
  `research.ethics-compliance.json` (the accepted-template shape, and the object form of
  `falls_through_to` and `collides_with`).
- **`planning/01-product-design-structured.md`** — not read beyond confirming it is the numbered
  rendering; `00` was read in full and wins on conflict, so no section number is cited as evidence
  anywhere in the node.
- **`planning/deferred-catalogues/`** — not consulted. This node's recognition consumes no existing
  catalogue: it names an organization gazetteer family and term-pattern families by *family*, and
  writes no gazetteer contents (R4's) and no regex (R2/R6's).

## 2. Why the node is NOT refused

The template node test refuses a row whose detection signals, recommended dimensions **and**
privacy rules are its schema's default. This row differs on two limbs cleanly and on the third in a
way worth stating precisely:

1. **Detection signals — genuinely different.** `career.json`'s deterministic list is
   resume-shape, offer/agreement-shape, recruiting email, calendar interview, packet manifest.
   None of them fires on a layered `.psd` with an export sibling, a caption-spread portfolio PDF, a
   case-study heading sequence, a showreel container, or a user-created showcase folder. The
   overlap is one item (an archive manifest), and even there the manifest contents differ
   (exports + showcase PDF vs transcript + certificate + form).
2. **Privacy rules — different, and this is the sharpest limb.** The schema row's sensitivity is
   "employment materials". This row adds a rule the schema does not have: a work sample routinely
   **embeds a third party's** confidential material, so sensitivity belongs to the bytes and a
   curated copy of a confidential deliverable is exactly as protected as the original. That rule is
   what the `Acme_Q3_Strategy_FINAL.pptx` fixture exists to state.
3. **Dimensions — both empty, but not for the same reason.** Every career template is forced to
   `dimension_order: []` because the schema declares no fields (D1 as narrowed). Read naively that
   makes all six career templates "identical in dimensions", which would refuse the whole shelf —
   an artifact of the deferral, not a finding about the situations. The honest statement, recorded
   in `template.why`: `00`'s recorded career order (**company → role or recruiting cycle →
   document type**) is the *recruiting* order and does **not** fit a showcase, because a portfolio
   routinely contains personal, academic and speculative work with no company at all. So the
   prose recommendation this row would make (**piece of work → artefact role**, showcase occasion
   optional) differs from the schema's even though both serialize as `[]` today.

I considered refusing on limb 3 alone and rejected it: refusing here would delete the only row that
can express `00`'s named "creative projects" situation and the only home for `design_creative`
files, which is a worse outcome than an honest placeholder with real detection signals.

## 3. Files considered and rejected

| Considered | Why it is not a fixture here |
|---|---|
| `Resume - Joseph Yung - 2026.pdf` | Already the lead fixture on `career.json`; re-using it would restate the schema row. It survives only as the `Resume.pdf` **member** inside `Selected Works.zip`, where it is the collision fixture against `career.recruiting`. |
| A LinkedIn/profile PDF export | A profile is a resume surface, not a curated sample; it belongs to `career.recruiting`. |
| A GitHub "pinned repo" README | Repository content — `code.software-project` by `00`'s structural precedence. Kept only as the `portfolio-site` fixture, which exists to show this row **losing**. |
| A thesis PDF used as a writing sample | The document is `research.thesis-dissertation`'s; using it as a sample is a group membership, not a second file. Left out to avoid implying a fact transfer. |
| A `.stl` / 3D-print file | ROSTER.md §5 item 6 refuses maker files outright; adding one would smuggle the refused world back in through a fixture. |
| A design system / brand guideline `.fig` export owned by an employer | Employer-owned working material, not the holder's sample — and it would have needed an ownership fact no schema declares. Recorded here rather than faked. |
| An `.indd` that yields nothing | Kept only as the `Unsupported or Encrypted` fallthrough example rather than a full fixture, because its entire evidence set is "unreadable", and `00` forbids inferring purpose from such a filename. |

Twelve fixtures were written, covering: labelled-structure document, unlabelled prose (case study),
proprietary-format-with-no-text (`.psd`, `.dwg`, `.ai`), archive manifest, OCR screenshot,
audio_video, code_structured, presentation, camera image, and the two seam cases (collision:
`portfolio-site/…`, `Sheet A-101…`, `IMG_2201.HEIC`; also-holds: `Portfolio - MArch application -
Columbia.pdf`).

## 4. `proposed_fields` — deliberately empty, with the reason

No new canonical key is needed and none is proposed. This row's two natural dimensions map to keys
that **already exist** in `canonical_fields.json`:

- the piece of work → `project` (currently referenced by the research and code schemas),
- source vs export vs case study → `artifact_type` (same two schemas),
- the commissioned case → `client` (the `our_firm ↔ client` role split).

So the gap is **not** vocabulary; it is that the career schema references no keys at all (D1 as
narrowed, PR-6). Minting `work_sample_type` or `portfolio_project` beside `artifact_type` and
`project` would be precisely failure mode 5 in CONNECTION §9 ("a second field named `course_name`
beside `subject`"), at a moment when the real blocker is a deferral. Recorded as `open_question`
instead.

Note also `authored_by`: a portfolio is by definition one person's own output, which makes it the
single most tempting place to use authorship as a folder level. `00` forbids it and
`canonical_fields.json` already has `authored_by` `destination_eligible: false`. Written into
`never_alone` so the temptation is on the record.

## 5. Neighbours considered that did NOT get an edge

- **`code.notebooks-experiments` / `code.scratch-prototypes`** — a demo notebook can be a sample,
  but the discriminating evidence is identical to the `code.software-project` edge already written
  (repo markers / structural precedence). A second edge would restate one signal; edges cost
  reciprocity work at R1c.
- **`research.manuscript-publication`** — a published paper shown as a work sample is a group
  membership, not an evidence confusion; the poster case (`research.conference-presentation`)
  is where a single evidence item genuinely supports both, so only that edge was written.
- **`academic.coursework`** — a student portfolio of course projects is real, but the discriminator
  is `00`'s own course-code-plus-academic-context floor, which activates academic on its own
  evidence; nothing here would confuse the two evidence items. Left unwritten rather than padded.
- **`photos.screenshot-captures`** — the platform screenshot is handled by the `Temporary
  Screenshots` fallthrough plus the no-EXIF never-alone; a collision edge would duplicate the
  photos schema's own screenshot rules.
- **`legal.leases-agreements` / `finance.*`** — the confidentiality footer on a client deliverable
  is a *sensitivity* fact, not an evidence collision. Handled in `sensitivity_why`.
- **`career.employment-records`** — performance-review material that quotes work samples. Same
  schema, but no shared evidence item: reviews carry review structure. No edge.

**`also_holds_with` is empty, and that is CONNECTION winning over the dispatch prompt.** The prompt
lists `also_holds_with` in this node's available edges; CONNECTION §5 restricts it to
**schema ↔ schema** pairs, and every landed template node (`research.*`) leaves it empty. The two
genuine two-schema cases this node found therefore belong on schema rows:

- **career ↔ college_applications** — already authored on `career.json`; the `Portfolio - MArch
  application - Columbia.pdf` fixture is fresh evidence for it.
- **career ↔ research** — **not** on `career.json` today, and the `Poster_PVA-RDP_ASCB2026_48x36.ai`
  fixture is a real instance (a research artifact that is also a showcased sample). Flagged for
  R1c below rather than authored here, since I may not edit another node.

## 6. NEEDS-JOSEPH (this node only)

- **NJ-PWS-1 · Is a work sample a career object at all?** This is ROSTER.md's NJ-R1a-1 seen from
  its only surviving face. `00` names "creative projects" as an organizational situation; the
  roster has no creative schema, so the portfolio face was attached to `career` and handed
  `design_creative` ownership. If a creative schema lands, this row's `schema_id`, its dimensions
  (`project` → `artifact_type` on real fields) and its `design_creative` ownership all move with
  it. **R1c should treat `schema_id: career` on this row as provisional.**
- **NJ-PWS-2 · Which canonical keys the career schema may reference** when S3/D1's deferral lifts
  (inherited from `career.json`'s open question, made concrete above: `project`, `artifact_type`,
  `client` all exist and none is career's today). Until answered, this template can legitimise
  **no** fact beyond the universals, which is worth Joseph seeing plainly — a placeholder that
  detects well and extracts nothing.

## 7. Findings handed to R1c (not fixes, and no other file was touched)

1. **Reciprocity owed** on all five `collides_with` edges: `code.software-project`,
   `research.conference-presentation`, `career.consulting-client-engagement`, `career.recruiting`,
   `photos.camera-events`. None of those five node files exists yet, so each will need this id on
   its own side.
2. **`career ↔ research` `also_holds_with` is missing** from `career.json` (§5 above). Schema-level
   edge, schema-level fix.
3. **`file_kind_owner` semantics remain unsettled** — the same question `research.project-workspace`
   raised. This row owns `design_creative`, yet two of its own fixtures (`Poster_…​.ai` →
   `research.conference-presentation`, `Sheet A-101…​.dwg` → live production, no situation) carry
   that source type and do **not** belong here. If a later reader treats `file_kind_owner` as
   exclusivity rather than primary interest, both are mis-shelved. Written into the node's
   `never_alone` as a defence; the roster-level clarification is R1c's.
4. **`career.json`'s `falls_through_to`** omits `One-Off Images`, `Unsupported or Encrypted` and
   `Reference Clips`, all three of which this situation reaches with fixtures. Schema-row question,
   noted not edited.
