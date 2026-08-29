# applications.graduate-professional — lab notes (R1b)

Node: `kind: template`, `schema_id: college_applications`, `launch: placeholder`, `provenance: inference`.
Output: [`applications.graduate-professional.json`](applications.graduate-professional.json).

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every span inside quote marks in the
  node file was grep-verified against this file before it was written (one exception, flagged in the
  node itself: the phrase quoted from the sibling node, attributed there as such).
- `planning/prompts/ALIGNMENT.md` — two roster kinds; work types are values; a template that only
  repeats its schema's default is not a node.
- `planning/domains/CONNECTION.md` + `CONNECTION-EXAMPLES.md` — node test (§2), closed edge
  vocabulary (§5), activation ≠ grouping (§4 step 9), `parent_id` browse-only, `shares_field` never
  authored. Fixture 2 (abstract carried by two schemas) is the pattern the writing-sample example
  reuses.
- `planning/domains/_CONTRACT.md` — entry shape, D6 snake_case, rule 8/12 (a template may branch
  only on fields its schema declares), rule 6 (`residual_template` vs `domain`), rule 5 (no handling
  classes).
- `planning/domains/canonical_fields.json` — every field name used or proposed was checked against
  this table. No field was minted.
- `planning/domains/roster.json` — confirmed id, kind, `schema_id`, neighbours; every
  `collides_with` target and the `role_split` neighbour is a real roster id.
- `planning/domains/nodes/college_applications.json` — the schema this template points at: the five
  declared fields (`target_university`, `application_cycle`, `application_document_type`, `purpose`,
  `school`) and their destination eligibility are the ceiling on what this row could recommend.
- `planning/domains/nodes/applications.undergraduate-packet.json` — landed sibling; it had already
  authored a collision edge against this id, so this node authors the reciprocal and answers its
  charge directly rather than inventing a different discriminator.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; every `file_examples.source_type` is a member.

## The node test — why this did not refuse

The sibling's collision edge states the hardest version of the case against this node: *identical
field set and identical dimension order*. Refusal was live. Three differences survive, and CONNECTION
§2 needs only one:

1. **Detection signals.** Near-disjoint vocabulary over one shared gazetteer. This situation fires on
   a statement-of-purpose / research-statement heading naming a degree programme, on a labelled
   degree-sought or programme-applied-to slot in a graduate or centralised professional application
   service, and on advisor/faculty language. The undergraduate signals — activities list, counselor
   recommendation, secondary transcript, early/regular decision — cannot produce any of those, and
   vice versa.
2. **Recommended dimensions.** This row recommends `target_university → application_document_type`
   and demotes `application_cycle` to an optional level, against the schema default's three. Reason,
   not decoration: the dossier files that dominate this situation (CV, writing sample, transcript,
   score report) carry no cycle at all, and `00` forbids a template that would "create meaningless
   one-child levels" or "produce empty branches when tested against the accepted group".
3. **Privacy.** Third-party recommendation letters about the applicant, financial certification and
   bank material for international admission, and immigration documents are routine here and rare in
   an undergraduate packet. That is a different protection default, expressed as a heavier
   `Protected Records` fallthrough and a stricter never-in-a-cloud-dossier note.

The failure mode I was watching for was manufacturing a dimension difference to justify the row. The
dimension difference above is one I would defend without the node test: a cycle level that most files
cannot fill is the empty-branch defect `00` names.

## Files considered and rejected

- **`Diploma.pdf` / degree certificate** — a credential, not an application document. It reaches an
  application only as a scanned supporting item, and `academic.transcripts-credentials` already owns
  the record situation. Rejected as an example because it would only restate the transcript case.
- **`NCBE Character and Fitness Questionnaire.pdf`** — kept out of the examples but kept as a
  collision (`career.credentials-licenses`). It is licensure, not admission; adding it as a file
  example would have implied this template should fire on it.
- **`Personal Statement.pdf` for a job** — folded into the `career.recruiting` collision instead of a
  second near-duplicate example; `CV_2026.pdf` already carries the shared-document lesson.
- **`.vcf` of a department contact list** — `00` says contact data "should normally be
  privacy-protected rather than used to create folder proposals", so it produces no application fact
  and would have been a filler example.
- **`orientation.ics` / matriculation calendar** — post-decision enrolment material. Arguably a
  different situation (enrolment, not application); left out rather than quietly widening this row.
  Noted below as a boundary, not raised as a NEEDS-JOSEPH because nothing depends on it yet.
- **A second archive fixture** — one (`grad_apps_2026.zip`) is enough to carry the routing lesson to
  `applications.purpose-packet`; the roster gives archive evidence to that row and this one does not
  claim it (`file_kinds.note`).

Fifteen examples are written. Two are collision fixtures (`Michigan PHIL 5200 Seminar Syllabus.pdf`
for `academic.coursework`; `GRE Score Report.pdf` for `academic.standardized-testing`), one is the
also-holds case (`Writing Sample - Thesis Ch3 (trimmed).pdf`, research + applications on disjoint
evidence), four are hub / sparse / no-fact cases where the honest answer is that nothing activates
(`CV_2026.pdf`, `SOP draft 2.docx`, `Program Deadlines and Fee Waivers.xlsx`,
`Re Prospective PhD student inquiry - Prof Alvarez.eml`).

`group_without_copying_facts: true` is set on the `HW 3`-shaped cases — `SOP draft 2.docx` above all,
which sits in an institution's folder, retrieves to that institution's statements, and still gets no
`target_university`.

## proposed_fields — justification and self-check

One proposal: **`target_program`** (string, `direct` ceiling, destination-eligible), and it is
deliberately **not** used in `dimension_order`.

The finding is real: a graduate applicant routinely files two separate applications to two programmes
at the same university — separate statements, separate deadlines, separate decisions — and no field
the active schema declares can separate them. `target_university` merges them; `subject` is the
enrolled-study role on the academic schema (the applicant's own side, and not declared by this
schema); `application_document_type` describes what a document does, not what was applied to.

I did not treat that as licence to mint a key. The node records three cheaper resolutions and asks
R1c or Joseph to pick: keep the programme as an accepted-group label only (`00` already lets a group
carry a display label); declare the existing `subject` key on the `college_applications` schema as a
target-side role with a `role_split`; or widen `target_university` in role, which is already the
schema row's own open question and `applications.scholarship-fellowship`'s. Because the recommended
dimension order branches on neither, nothing in this node breaks whichever way it goes — that was the
design constraint I held myself to.

Everything else references existing canonical keys. No synonym was minted; `subject`/`course`,
`work_type`, and `target_university`/`target_school` spellings were checked against
`canonical_fields.json` rather than guessed.

## Divergence from the dispatch prompt (CONNECTION wins)

The prompt offers `also_holds_with` to any node. CONNECTION §5 joins `also_holds_with`
**between schemas only**, and the `college_applications` schema row already carries the co-holding
edges this situation needs (research, academic, identity). So `also_holds_with` is empty here and the
per-file co-holding is expressed as `also_schema` on the file examples (research on the writing
sample, academic on the score report, finance on the financial certification). The node file states
this in `also_holds_note`. The landed sibling made the same call, which is a second reason not to
diverge.

`falls_through_to` is serialized as objects with a `residual_template` key (contract rule 6 and the
sibling's shape) rather than as bare names.

`parent_id` is left `null` and was never authored (PR-5: R1b never authors it).

## Neighbours considered that got no edge

- **`research.project-workspace`, `research.manuscript-publication`** — the writing sample's research
  reading is already carried by the `research.thesis-dissertation` collision and by `also_schema` on
  the fixture. Adding two more research edges would restate one discriminator three times.
- **`identity.core-documents`, `identity.immigration-visa`** — a passport scan or an I-20 inside a
  packet is a safety activation on its own evidence, not a confusion with this template. `00` puts an
  identification document inside a packet and the schema row already records the identity
  co-holding; a template-level collision would misread co-activation as mutex.
- **`finance.student-financial-aid`** — the undergraduate sibling authored this one, and rightly: aid
  profiles and award letters are its fixture (`CSS Profile Summary.pdf`). The graduate analogue here
  is funding and financial certification, which I routed to
  `applications.scholarship-fellowship` (award-vs-admission framing) and to the sensitivity rule
  instead of duplicating the sibling's edge.
- **`academic.recommendation-letters-written`** — that row is the *writer's* side of a letter; this
  row's fixture is the *applicant's* received copy. The pair is a role difference at the holder
  level, and `academic.teaching` has already authored an edge into that node from its own side. I
  left it to R1c to decide whether an applicant-side/writer-side collision is worth an edge, rather
  than authoring a one-way edge into a node I cannot see.
- **`applications.k12-admission`** — the sibling covers that discriminator (applicant is a minor, the
  holder is a guardian). Nothing in the graduate situation is confusable with it.

## NEEDS-JOSEPH — this node only

1. **The programme dimension.** The level this situation wants under the institution is the programme
   applied to, and no legal field can hold it. Three resolutions are listed in `proposed_fields`;
   picking one is above this node. Until then, the recommended tree is one level shallower than the
   material, which is the honest state, not a bug.
2. **Funding inside an admissions submission.** An assistantship or departmental funding application
   filed as part of an admission is legitimately both this situation and
   `applications.scholarship-fellowship`. The collision edge records the discriminator
   (award-and-eligibility framing vs admission-and-enrolment framing), but a single submission that
   is genuinely both needs a policy decision, not a sharper signal.
3. **Boundary noted, not opened:** enrolment and matriculation material (deposit forms, orientation
   records, visa issuance after an offer) sits just past this template's edge. It is left out rather
   than absorbed. If it recurs in a real corpus it is a template question, never a schema one.

Inherited from above and not re-opened here: whether `purpose` stays Applications-scoped (NJ-3 /
PR-1), and whether `target_school` folds into `target_university` (ROSTER.md).
