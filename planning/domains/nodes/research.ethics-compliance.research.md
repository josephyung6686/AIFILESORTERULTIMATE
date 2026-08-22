# research.ethics-compliance — lab notes

Date: 2026-08-22
Kind: `template` · `schema_id: research` · `launch: placeholder` · `provenance: inference`
Output: [`research.ethics-compliance.json`](research.ethics-compliance.json)

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; the authority. Every span this
  node puts inside quote marks was matched mechanically against it before the JSON was written
  (38 distinct spans, all verbatim). Counted mechanically, `00` contains *IRB* zero times,
  *ethic* zero, *participant* zero, *human subject* zero, and *consent* five times — all five in
  the model-consent sense (a consent-aware audit record, model-consent policy), never informed
  consent. That is why `provenance` is `inference` and `design_cite` is `null`: this
  node extends a domain `00` names ("Research files may use project, stage, artifact type, lab,
  and venue") into a situation it does not.
- `planning/01-product-design-structured.md` — checked only for coverage of this area. Its four
  hits on *consent* are all §8.4's model-consent policy, i.e. a different sense of the word. It
  adds nothing to this node; `00` governs.
- `planning/domains/_CONTRACT.md` (entry shape, rules 11–15), `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md`.
- `planning/domains/canonical_fields.json` — every field name used here resolves to it.
- `planning/domains/roster.json` — confirmed the row, and confirmed all six collision targets
  exist as roster ids.
- `planning/domains/nodes/research.json` (the schema) and
  `planning/domains/nodes/research.manuscript-publication.json` (a landed sibling template) —
  read to align, not to rewrite. `research.json` already carries `also_holds_with medical` with
  an IRB protocol as its fixture, so this node does not restate it.
- `planning/domains/nodes/medical.json` — read for one sentence that changed this node's
  template recommendation (see below).
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — every `source_type` used is a member.

## Node test — why this is a node and not padding

The schema's default situation is `research.project-workspace` on `00`'s own order
(project → stage → artifact type). This row differs on all three axes, and it would still pass on
the third alone:

1. **Detection.** None of this node's signals fire on workspace material: a review-board
   letterhead over labelled approval slots; an informed-consent section sequence closing on a
   participant signature block; a board-issued protocol token repeated across a header zone and an
   email subject; an approval-lifecycle term; a human-subjects training certificate.
2. **Privacy.** This is the real reason the row exists. A study's working figures are ordinary
   research material. A stack of signed consent pages is a set of named people's signatures, and
   `00` puts material of that kind under protection before anything else happens to it.
3. **Dimensions.** `stage` drops out of the recommended order and the depth stops at two.

Refusal was considered and rejected: a template whose privacy rules differ from its schema's
default is explicitly a node under CONNECTION §2, and this one's privacy rules are the sharpest
in the Research family.

## Files considered and rejected

- **A grant proposal's human-subjects section.** Rejected as an example, kept as a collision with
  `research.grants-funding`. The document is addressed to a funder; the embedded approval letter
  is evidence about a different instrument.
- **A conference travel receipt for a study team.** Rejected outright — finance/travel material
  that happens to sit near a study. Nothing in it evidences this situation.
- **`Ravikumar_2019_NatureMethods.pdf`** (a downloaded paper whose Methods section describes its
  own ethics approval). Rejected: the approval described belongs to somebody else's study. It is
  already the schema row's Reading Inbox fixture and adding it here would double-count it.
- **A departmental ethics *policy* PDF** (the institution's standing rules, not a study's file).
  Rejected as an example because it is genuinely study-less reference material; it lands in
  Reading Inbox or Independent Records and adding it would have padded the list.
- **`.vcf` of the study team.** Rejected: `00` keeps contact data out of folder proposals
  outright, so it produces no facts here and would only have restated the schema row's rule.
- Kept instead: two files that look like this node and are not — `Protocol_v2_BenchAssay.docx`
  (the word *Protocol* without a board) and `Consent to Treat — Radiology.pdf` (the word *Consent*
  with the holder as the patient). Those two are what the `never_alone` list is written against.

## `proposed_fields` justification — `protocol_id`

Recorded, **not authored**. No canonical key holds the review-board-issued study token:

- `project` is the research project, and the relation is many-to-many both ways (one project can
  run a pilot and a main study under two protocols; one protocol can cover work filed as more than
  one project).
- `version_family` is the universal draft-family fact computed from content and stem; the token
  spans several version families (consent v1 and v4 are different families under one protocol).
- `artifact_type` names the kind of document, not which study it governs.

Without a key, the tie between the approval letter, the signed consent scan, the amendment and the
portal capture can only be expressed as retrieval similarity, which `00` never lets stand alone.
Two deliberate constraints on the proposal: `destination_eligible: false` (a level per study token
is the tiny-folder split `00` asks the canvas to warn about, and it would put an
institution-issued identifier into a visible folder name on protection-first material), and the
**jurisdiction-neutral spelling** — `protocol_id`, never `irb_protocol_id`, because the issuing
body is an IRB in one country and an ethics committee or board elsewhere, and `_CONTRACT` rule 9
(D4) forbids a jurisdiction-specific field *name* while allowing values to carry the local
flavour. If adopted, it belongs on the Research schema as a search-and-grouping field.

No second field was proposed. The reviewing-body gap below is real, but two proposals from one
template row starts rebuilding the 574.

## Neighbours considered that did **not** get an edge

- **`medical` / `legal` (the schemas named in `must_consider_neighbors`).** Not edged from here:
  `collides_with` joins same-kind pairs and `also_holds_with` joins schemas only, so a template row
  cannot point at a schema. Both were honoured at the template level instead —
  `medical.personal-health-records` and `legal.leases-agreements` — and the schema-level
  co-activation (`research also_holds_with medical`) already exists on `research.json`, recorded
  here as `also_schema` on two file examples.
- **`identity.core-documents`.** A participant's ID copy sitting in a study file is tempting. No
  edge: the discriminating evidence is whose document it is, and a stranger's ID in a research
  folder is protected content under this node, not an identity-domain record of the holder's. An
  edge would invite the engine to read participant identity as the holder's.
- **`academic.coursework`.** A student research-methods assignment can contain a mock consent
  form. Left unedged: the discriminator is already the schema-level `research ↔ academic`
  collision (course-code-plus-academic-context), and restating it per template adds noise.
- **`research.dataset-analysis`.** De-identified analysis data descends from consented collection,
  but the evidence differs completely (no board, no consent structure), so there is no evidence
  item to be mutex about. `participants_master_list.xlsx` is a register, not an analysis dataset.
- **`career.employment-records`.** Rejected in favour of `career.credentials-licenses`, which is
  where a training certificate actually lands.
- **`research.thesis-dissertation`.** A thesis appendix reproduces the approval letter. That is
  the same shape as the grants collision and the grants one carries it; a second copy would be
  redundant.

## Where CONNECTION overrode the dispatch prompt

The prompt's edge table describes `also_holds_with` as available to this row. CONNECTION §5 is
narrower — `also_holds_with` joins **schemas only** — and CONNECTION wins. The array is therefore
empty with a note, matching the landed sibling `research.manuscript-publication`. Same for
`parent_id`: never authored by R1b (PR-5).

## NEEDS-JOSEPH (this node only)

1. **The one in `open_question`: should completed, signed participant-facing documents get a
   folder level at all?** The recommendation `project → artifact_type` puts a *Consent Forms* leaf
   beside *Approval Letters*, and that leaf is where the signature pages land — a folder whose
   name is harmless but whose existence advertises, in the canvas and on any shared screen, that a
   named study's identifiable participant material sits at a known path. The alternative is the
   call `medical.json` already made for the same reason (a branch's own labels would publish in
   folder names what the protection exists to hide): study-facing documents branch normally,
   completed participant-bearing copies get no level and are represented under the protected
   surface. `00` supports both readings — it wants the branch legible *and* it wants protected
   material redacted in the canvas. This decides where someone's real consent forms live.
2. **No canonical field holds the reviewing body.** The Research schema has one organization key
   that means *producer* (`lab`) and one that means *publisher* (`venue`). The institutional
   review board is neither, and on this material the two organizations are routinely different
   (a study run in one lab, reviewed by another institution's board, under a third's data
   agreement). Recorded as a finding rather than an edge, because `role_split` lives in
   `canonical_fields.json` and widening that list is R1c's or Joseph's. Until then the approval
   letter's board is evidence, not a fact, and `lab` must not silently absorb it — the file
   examples say so explicitly.
3. **Does a placeholder-launch node still get a protection path at launch?** `00` names finance,
   identity, medical and legal as the safety domains; this situation holds comparable material
   under a *research* schema that is a `full`-launch, non-safety domain. PR-2 covers the four
   named domains and says nothing about a non-safety schema whose template is protection-first.
   This node assumes the co-activation with the medical safety placeholder carries the protection
   (that is what `also_schema: medical` on two examples means) and asserts nothing further.
