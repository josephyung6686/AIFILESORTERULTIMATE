# Lab notes — `academic.k12-schooling` (R1b, kind: template, schema_id: academic)

Date: 2026-08-22
Node: [`academic.k12-schooling.json`](academic.k12-schooling.json)
Verdict: **not refused.** The node test passes on all three grounds at once — detection signals,
recommended dimensions, and privacy rules all differ from the Academic schema's default template
(`academic.coursework`).

---

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; the only source quoted. Every
  span inside quote marks in the node JSON was grep-verified against this file before it was
  written (22 spans, 0 unverified; re-checked after the file was written).
- `planning/01-product-design-structured.md` — **not read.** Nothing in this node needed a section
  number, and `00` is the authority; citing `01`'s numbering would have added locators without
  adding evidence.
- `planning/domains/_CONTRACT.md` (entry shape, rules 8/11–15), `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md` (fixtures 6 and 7
  are the ones this node has to stay compatible with).
- `planning/domains/roster.json` — confirmed my row, and confirmed the ids of every neighbour I
  drew an edge to.
- `planning/domains/canonical_fields.json` — every `facts_legal` value and every
  `dimension_order` member resolves to a canonical key the Academic schema declares.
- `planning/domains/nodes/academic.json` — the schema this template points at; I aligned wording
  and reused its `never_alone` discipline rather than re-deriving it.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; all seven I list are members.

## The node test, argued rather than asserted

`academic.coursework` is the schema's default situation. This row earns its place because:

1. **Detection signals invert.** The Academic schema's primary deterministic rule is `00`'s
   course-code-plus-context pair. On K-12 material that pair almost never fires: schools name
   plain subjects ("Mathematics", "Reading"), not code-shaped tokens. What fires instead is
   report-card vocabulary, a grade-level-shaped token, a school-year-shaped term pattern, and
   labelled enrollment slots. I wrote that inversion into `recognition.deterministic` as an
   explicit negative entry so a later reader cannot mistake this template for coursework with a
   different name.
2. **The recommended dimensions are shorter, and short for a reason.** `subject` drops out. K-12
   records are whole-child, whole-year records — one report card covers every subject — and a
   plain subject name cannot pass the rule that makes `subject` a *validated* fact, so a subject
   level would open a tree level no fact can fill. `00`'s own canvas rule about one-child levels
   and large numbers of tiny folders is the design support.
3. **Privacy rules differ.** The holder is usually not the data subject. The child is a minor;
   report cards carry grades; enrollment and consent forms carry a date of birth, a home address
   and emergency contacts; and the documents that arrive on the *same* letterhead in the same
   month include health forms, IEP notices and custody paperwork, which are protect-first
   material. Coursework's default has none of that shape.

## Files considered and rejected

- **`Emma - Math Worksheet.pdf` as a core example.** Rejected as a *primary* fixture: a worksheet
  the child produced is `academic.coursework`'s artifact, not this template's institutional
  record. It survives only inside the `academic.coursework` collision signal, where it is the
  discriminator.
- **A yearbook photo / school picture-day JPEG.** Rejected: camera or scan evidence activates
  `photos`; nothing in the file evidences an enrolled-student record. Including it would have been
  the format-as-domain bug in miniature.
- **A standardized score report (state assessment).** Rejected as an example and as an edge:
  `academic.standardized-testing` already owns that situation on the roster, and duplicating its
  fixture here would have manufactured a collision that is really a roster overlap for R1c to
  reconcile.
- **A college-recommendation letter written by a high-school teacher.** Rejected:
  `academic.recommendation-letters-written` is a roster row of its own, and the file's own
  evidence is admissions-facing.
- **A school lunch-account top-up receipt.** Folded into the `finance.personal-records` collision
  signal instead of a fixture — it is a receipt with a school name on it, which is exactly the
  false-positive the collision entry exists to state.

## `proposed_fields` — one proposal, `student`, and why it is not in `dimension_order`

The roster's own hint for this row says the subject is not the holder. That is the real finding
here: **no canonical key names the person a record is about when the holder is someone else.**
`authored_by` is the producer, `instructor` is the teacher, `people` is photo-side and seeded
non-eligible, and `subject` in this catalogue means the *course* — overloading it would recreate
D6's two-spellings defect in a worse form, one key holding two concepts.

`00` gives the general rule (roles that share an entity type get separate facets) and puts a
document's subject/target on the *informative* side of the same sentence that excludes authorship
from destinations, so this is not the authorship prohibition.

I deliberately did **not** put it in `dimension_order`. A template may only branch on fields its
schema declares, and the Academic schema declares no such field; branching on a proposed key would
be exactly the "invent a field to make the tree look complete" failure. So the node recommends
`school → term → work_type` — a legal order — and records the missing level as a proposal plus the
`open_question`. A household with two children is currently inexpressible in this template's
recommended order, and saying so plainly is more useful than a green-looking node that hides it.

## Contract conflict: the prompt's neighbours vs CONNECTION's edge rules

My ASSIGNMENT's `must_consider_neighbors` are `medical` and `legal` — both **schemas**. But
CONNECTION.md §5 closes `collides_with` to same-kind pairs and closes `also_holds_with` to
schema↔schema only. This row is a template, so:

- I discharged both neighbours by colliding with their **template** rows —
  `medical.dependant-child-health` and `legal.personal-legal-matters`, both real roster ids —
  rather than with the schemas. CONNECTION wins over the prompt, as the prompt itself instructs.
- `also_holds_with` is therefore **empty** even though this situation has a genuine two-schema
  file (the private-school enrollment agreement: school + school-year evidence *and* tuition,
  payment-plan and billing-institution evidence, disjoint, in one document). I recorded it as a
  `file_examples` entry with `also_schema: "finance"` and named it inside the
  `finance.personal-records` collision signal. **R1c: if the academic↔finance co-holding is worth
  an edge, it belongs on the `academic` and `finance` schema rows, not here.**
- `parent_id` stays `null` — R1b never authors it (PR-5), and I never authored `shares_field`.
- Reciprocity is R1c's: all seven collisions I wrote are currently one-way, and the neighbours
  they name have not landed as node files yet.

## Neighbours considered that got no edge

- **`academic.transcripts-credentials`** — a K-12 transcript exists, but the transcript template's
  discriminator (registrar language, seals, verification codes) is the same evidence I would have
  had to cite, so an edge would have asserted a confusion that the two signal sets already
  separate. Left to R1c, which sees both rows.
- **`academic.standardized-testing`**, **`academic.recommendation-letters-written`** — roster
  overlap rather than evidence confusion (see rejected files).
- **`identity`** — an enrollment form carries a minor's date of birth and address, which is
  tempting. But `00`'s identity material is passports, visas and credentials; a DOB slot on a
  school form is not an identity document, and asserting the edge would have licensed
  identity activation from a date field. I encoded the refusal as a `must_not_conclude` on the
  enrollment-form example instead.
- **`photos`** — the photographed report card genuinely co-holds, but that is a schema-level
  relation (`academic` ↔ `photos` already carry it on the schema row) and would be a duplicate
  here. Recorded as `also_schema` on the fixture only.
- **`finance.student-financial-aid`** — K-12 tuition assistance sits closer to that row than to
  `finance.personal-records`, but its one-liner scopes it to aid applications and loan servicing;
  a plain tuition invoice is ordinary personal finance. Chose the narrower, more defensible id.

## Gazetteer note for R4 (not resolved here, and not invented)

The `school` fact's rule family is a schools-gazetteer hit plus role context. For universities
that is workable; for K-12 it is materially harder — a district's individual schools are numerous,
name-collide across districts ("Lincoln Elementary" exists in many states), and often appear only
as letterhead. **I did not invent gazetteer contents.** The finding for R4 is that the `schools`
gazetteer needs a K-12/district tier with a name-collision policy, and that until it exists the
`school` fact on this template will more often be `possible` than `validated`. `00`'s
word-boundary rule applies unchanged.

## NEEDS-JOSEPH (this node only)

- **NJ-k12-1 — the child as a folder dimension.** Copied verbatim from the node's
  `open_question`: should the Academic schema declare a data-subject field (destination-eligible,
  role-split against `authored_by`) so a multi-child household can branch on it, or does a
  per-child folder stay purely the user's own existing structure that the product attaches
  beneath and never proposes? It is a privacy decision as much as a filing one — person-shaped
  folders for minors — and `00` is silent, so this node recommends neither.
