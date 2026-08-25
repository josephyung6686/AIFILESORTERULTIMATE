# creative.uiux-product-design — J-DEPTH research memo

## Verdict

Keep this as a placeholder template on the `creative` schema. It passes the node test because its
distinctive unit is a product-interface lifecycle, not a medium: research and requirements are
connected to flows and wireframes, an interactive prototype is evaluated against tasks, findings
drive revisions, and an identified approval or handoff closes the design loop. A `.fig`, `.png`,
wireframe word, product name, or design-system label alone cannot activate it.

The template still declares `fields: []`, `proposed_fields: []`, and an empty serialized dimension
order. The schema is deferred by the launch decision. Existing canonical proposals such as
`project`, `stage`, `artifact_type`, and `client` must be adjudicated once by R1c; this row must not
copy them or mint `product`, `screen_id`, `user_segment`, `usability_score`, `approval_status`, or
`design_system` synonyms. Work types such as wireframe, prototype, usability findings, and handoff
are values and artifacts within the lifecycle, not child nodes.

## Sources and authority

I used the stamped assignment from `make_prompt.py`, `00-database-agent-product-design.md`,
`ALIGNMENT.md`, `CONNECTION.md`, `_CONTRACT.md`, `canonical_fields.json`, `roster.json`,
`DECISION-BRIEF.md`, `creative.json`, `creative.client-engagement.json`,
`creative.deliverable-handoff.json`, `career.portfolio-work-samples`, `photos.screenshot-captures`,
and `code.software-project` as the local comparison set. The design authority controls the product
rules: a file is a record with many facts; extraction does not decide a permanent category; fields
remain small; templates are recommended dimensions populated from validated facts; and a template
must differ from its schema default in detection signals, dimensions, or privacy rules.

Concrete artifacts below are ordinary practitioner-file inferences, not claims that the product may
write facts from them. No thresholds, confidence scores, legal conclusions, usability statistics,
or external standards are imported. `source_type` values were checked against the repository's
fourteen-member `SOURCE_TYPES` vocabulary.

## Node test — all three legs

### Detection differs

The creative default recognises making records through linked assets, layers or artboards, revision
families, briefs, exports, production paperwork, and handoff structures. UI/UX design needs a
different relationship among those artifacts: a user problem or research synthesis points to a
flow; a flow is embodied in wireframes or prototype states; a test script and observed result cite
those states; a decision or revision answers the finding; and an implementation-facing handoff or
approval identifies the accepted design. This chain distinguishes product design from a generic
poster, illustration, video, or export even when every item lives in the same Figma or presentation
tool.

The discriminating evidence is positional and relational, not vocabulary. `Checkout Task Flow
v03.fig` plus `Usability Findings.csv` is stronger than either file alone. A prototype URL becomes
evidence only when its referenced states are named by a task, finding, review, or handoff. A design
system library qualifies when variants and usage guidance govern product screens; a downloaded UI
kit with identical component names does not.

### Dimensions

There is no serialized dimension difference at launch. `creative` declares no field rows, and the
contract forbids a template from branching on undeclared keys. If R1c adopts the existing creative
proposals, a conceptual order would be product/project → stage → artifact type, with screen, flow,
component, test round, and approval as values or retrieval facets. Time is not first: discovery,
prototype creation, testing, approval, implementation, and release are distinct clocks. A separate
`screen`, `feature`, `design_phase`, or `usability_round` field would be a one-template vocabulary
patch, not a justified schema change.

### Privacy differs

The UI/UX lifecycle concentrates risks not present in a generic visual export: interview notes and
participant references, unreleased product strategy, credentials accidentally placed in a prototype,
accessibility findings, internal critique, and implementation details. The row therefore retains
`potentially_sensitive` recognition. It does not assign P7 handling classes, assert that every screen
is private, or turn approval into legal acceptance. This privacy posture alone would support keeping
the template even where a future field decision leaves dimensions empty.

## Bottom-up file investigation

The JSON contains the twelve core fixtures. The first eight are the lifecycle spine; the remaining
four establish collisions, sparse evidence, archives, and implementation boundaries.

1. **`Checkout Discovery Synthesis.pdf`** — interview themes, user needs, checkout tasks, and open
   design questions point toward a flow. It is evidence of discovery only when a design artifact is
   linked; a research report with no interface lineage falls to Reading Inbox or Research.
2. **`Checkout Task Flow v03.fig`** — named frames, connectors, annotations, and error/success
   states are a strong authored flow. `v03` is version-family evidence, not proof of approval or
   implementation.
3. **`Mobile Checkout Wireframes.pdf`** — repeated screen/state identifiers and interaction notes
   survive a static export. It cannot prove the interactions work or that the depicted product is
   owned by the corpus maker.
4. **`Checkout Prototype Review - Round 2.pdf`** — annotations cite exact prototype states and
   test/review observations. An unattributed comment such as “make it clearer” remains unknown;
   the document does not prove that a change was implemented.
5. **`Usability Test Script - Checkout.docx`** — task prompts and expected observations reference
   prototype states. A script proves intended evaluation, not that sessions occurred or produced a
   finding.
6. **`Checkout Usability Findings.csv`** — task, observed result, issue, state reference, and
   disposition columns make the research-to-design relation machine-readable. A participant code is
   not a person fact, and disposition is not completion.
7. **`Checkout Components v2.fig`** — named variants, states, usage guidance, and screen links make
   this a candidate governed component library. The same file without consuming-screen links may be
   a stock asset or brand library.
8. **`Checkout Design Handoff - Approved.pdf`** — screen IDs, interaction states, accessibility
   notes, implementation references, and artifact-specific approval provide the terminal handoff
   signal. It does not establish that code shipped or that a signature has legal effect.
9. **`checkout-ui-assets.zip`** — a manifest mixes sources, exports, tokens, handoff PDF, and README.
   Member facts must not be copied from the archive name or adjacent files; without readable purpose,
   it is Unsupported or Encrypted or Review Later.
10. **`Screenshot 2026-08-18 at 14.20.png`** — OCR may show buttons and product branding but there is
    no positive capture metadata. It is the sharpest `photos.screenshot-captures` collision and is
    grouped without copying product or project facts.
11. **`Product App - UI Case Study.pdf`** — polished screens and retrospective narrative may be a
    career portfolio work sample. It is not the design lifecycle unless source, research, test, or
    handoff evidence is present.
12. **`src/components/Checkout/Button.tsx`** — source-tree and import structure establish code. A
    comment naming a design token does not turn implementation into a design artifact.

### Calendar, email, OCR, and archive edge cases

A kickoff `.ics` is transport/context evidence unless it identifies an accepted design study and
participants; it does not activate this template by date or meeting title. An email with a prototype
link qualifies only when the body identifies the review/test task, exact artifact, and response; a
generic “please see attached” does not. An OCR image of a usability markup can preserve screen IDs and
task comments, but OCR uncertainty remains possible and missing metadata proves nothing. An archive
is inspected through its manifest where possible; extraction does not license facts for every member.

## Neighbour boundaries and collision fixtures

### `code.software-project`

The shared fixture is the checkout product: Figma screen names, token names, and component names can
appear in both design files and a repository. UI/UX owns research, prototype states, interaction
specification, user-test findings, and design approval/handoff. Code owns source trees, build files,
dependencies, runtime behavior, tests, and implementation commits. A handoff may be grouped with a
repository without copying `project` or implementation facts to the design files. Conversely, a
TypeScript component is not design evidence merely because its comment says “matches Figma.”

### `career.portfolio-work-samples`

The shared fixture is `Product App - UI Case Study.pdf` or a polished screen export. Career owns a
retrospective presentation whose purpose is demonstrating the maker's capabilities, role, and
selected outcome. This template owns the working research/prototype/test/handoff record. A case study
may cite or depict the work without converting the source files into career records; a prototype does
not become a portfolio sample merely because it looks polished.

### `photos.screenshot-captures`

The shared fixture is `Screenshot 2026-08-18 at 14.20.png`. Photos owns positive evidence that a screen
was captured—capture metadata, screen-capture structure, or a photo chronology—not interface design
authorship. This template owns an authored flow or export only when lifecycle evidence exists. A
screen-shaped PNG may be grouped with a prototype but keeps only universal/image facts when its origin
is unresolved. Absence of EXIF is not screenshot proof.

### Creative default and adjacent creative templates

The same layered file can be a generic creative work, client engagement, deliverable handoff, or UI/UX
product design. The boundary is the lifecycle evidence. A client brief with no user problem, screen
state, or usability lineage remains client engagement or creative default. A package with manifest,
recipient, and receipt evidence is deliverable handoff even if it contains UI screens. A research plan
or test script is not a separate child node: it is a work type/value inside this lifecycle.

## Files considered and rejected

- `Figma Community UI Kit.fig`: component names and variants are stock-asset evidence, not product
  design. It may fall through to Independent Records or Reference Clips.
- `Design System Guidelines.pdf`: a downloaded or public brand manual may be reference material;
  governing product components require links to product screens and ownership context.
- `App Store screenshot.png`: screen content is not authored design. Photos or Career may own it based
  on capture or portfolio purpose.
- `Product Roadmap 2026.pptx`: product strategy and dates are not interface design without flows,
  prototype states, or test/handoff linkage.
- `Jira Export - Checkout.csv`: tickets and statuses belong to software/project delivery unless
  individual rows cite a design artifact and user task.
- `User Interviews.docx`: research is not UI/UX merely because participants mention an app; the design
  lifecycle requires a linked interface artifact.
- `Logo.svg` and `Brand Tokens.json`: brand identity or implementation assets are not product design
  without screen/flow and lifecycle evidence.
- `Final Prototype.zip`: archive name, FINAL token, and transport are never-alone signals.
- `Analytics Dashboard.xlsx`: behavioural metrics are not usability findings; a linked task/state
  analysis may be grouped, but metrics do not silently create design facts.
- `Accessibility Audit.pdf`: an audit may support this template when it cites exact screens and
  proposed design changes; a site compliance report alone may belong to engineering or governance.

## Fields, edges, and residual routing

No fields are proposed. Existing `project`, `stage`, `artifact_type`, and `client` remain proposals
on the schema, not copied into this template. `screen_id`, `flow`, `feature`, `design_phase`,
`participant`, `usability_score`, `approval_status`, `component`, and `handoff_date` were rejected as
either values, universal observations, privacy-sensitive operational data, or cross-domain concepts.
No `also_holds_with` edge is asserted: design and code can be grouped around one product, but a code
file does not thereby acquire the design schema's facts. The three collisions in JSON use concrete
shared evidence and reciprocal boundaries; R1c must enforce reciprocity.

Residual routes are intentionally broad. Durable standalone specs and exports go to Independent
Records. Ambiguous feedback or prototypes go to Review Later. Sparse screen captures go to Temporary
Screenshots. General UX reading and reusable test templates go to Reading Inbox. Opaque proprietary
archives go to Unsupported or Encrypted. None of these routes creates a UI/UX child schema.

## NEEDS-JOSEPH

**NJ-UIUX-1 — shared creative fields.** Should R1c adopt `project`, `stage`, `artifact_type`, and
`client` for the deferred creative schema? Recommended: adopt the canonical shared keys, keep screen,
flow, component, test round, and approval as values/retrieval facets, and preserve an empty dimension
order until facts are legal. Alternative: leave creative recognition-only through placement.

**NJ-UIUX-2 — research ownership seam.** A product discovery synthesis may be both a research artifact
and evidence for this template. Recommended: allow co-membership/grouping only when each schema has
independent evidence; never copy research project or venue facts into Creative. Alternative: keep
research files in Research and use only the design artifacts here.

**NJ-UIUX-3 — governed design-system scope.** Decide whether a component library with product-screen
links is part of this template or a separate future creative template. Recommended: keep it here as an
`artifact_type` value unless its detection/privacy/dimension rules demonstrably diverge.

## Self-verification

- JSON parses with `python3 -m json.tool`.
- All twelve examples use allowed `SOURCE_TYPES`; all `facts_legal` arrays are empty because the
  launch schema is deferred.
- The JSON and memo agree on: keep verdict, placeholder launch, no fields, no dimensions, lifecycle
  recognition, three collisions, five residual routes, potentially sensitive posture, and three
  NEEDS-JOSEPH items.
- No file paths, thresholds, confidence scores, handling classes, or invented canonical fields were
  added. Only the assigned JSON and research memo were written.
