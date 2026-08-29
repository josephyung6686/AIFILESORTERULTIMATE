# business_operations.user-research — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the gist draft, 2026-08-25. The full node test reverses the gist
verdict: this row is **refused**. Refusal is the researched result, not missing coverage.

## Sources actually used

The authority stack was read in the required order: `planning/prompts/ALIGNMENT.md`,
`planning/00-database-agent-product-design.md`, `01-product-design-structured.md`,
`planning/domains/CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `_CONTRACT.md`,
`canonical_fields.json`, `roster.json`, `ROSTER.md`, the ratified council decision brief, and
`src/evidence_shape/vocabulary.py`. The stamped prompt came from
`python3 planning/domains/dispatch/make_prompt.py business_operations.user-research`.

The measuring stick was `business_operations.research.md`, not the old gist siblings. The required
neighbours were read without editing: `business_operations.product-requirements`,
`business_operations.meeting-record`, `business_operations.strategy-plan`, and the anchor itself.
Search named and therefore required reading of `business_operations.market-research`,
`business_operations.customer-account-management`, `research`, `research.ethics-compliance`,
`research.dataset-analysis`, `research.reading-library`, and `hr.engagement-survey`. The
`business_operations.organisational-records` refusal supplied the deletion-test precedent.

All quotation marks below contain exact spans from `00`; arguments not quoted are explicitly this
pass's inference. No external catalogue, detector regex, threshold, confidence score or handling
class was used.

## What the legacy label describes

The familiar practice is real. A product team plans a study, recruits participants, gathers consent,
runs interviews or usability sessions, collects survey or diary responses, synthesizes observations,
and carries recommendations into product work. Real artifacts include guides, screeners, signed
consent, recordings, transcripts, observation grids, response exports, affinity maps, personas,
journey maps and findings decks.

The mistake is the move from *real practice* to *distinct template*. The roster is not a taxonomy of
professions or techniques. A template must change detection, dimensions or privacy relative to its
schema default. `User` names whom evidence came from. `Interview`, `survey`, `diary study` and
`usability session` name methods. `Persona` and `findings readout` name outputs. Those are values and
work types. None is automatically a structural anchor.

## Node test, leg by leg

The schema anchor states the family default in prose:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* →
> the **governance body, project, contract, or account** the material belongs to → the **fiscal
> period** → the **document function**. Not time-first.

It also generalises the family rule: no sibling may rest on an entity name, business vocabulary word
or document shape alone; a surviving signal must pair structure with a labelled slot.

### Leg 1 — detection signals: fails

The gist draft listed impressive structures, but each recognizes an artifact or method rather than
this situation:

- A discussion guide's warm-up, prompts, probes, tasks and wrap-up occur in product interviews,
  academic fieldwork, market focus groups, sales discovery and journalism. `Moderator` or `user`
  does not change the structure; it supplies a role value.
- A consent form's recording, retention, withdrawal and signature slots reliably establish sensitive
  human-subject material. They do not establish product purpose. Academic, workforce and market
  studies use the same apparatus.
- A transcript or recording is even less specific. Support calls, sales calls, job interviews,
  standing meetings, depositions and podcasts generate identical containers and speaker labels.
- A survey export with respondent id, submitted timestamp and question columns is common to customer,
  employee, market-panel and academic samples. The table is legible evidence, but its legibility does
  not decide the respondents' organizational role.
- Affinity maps, personas, journey maps and findings/recommendation decks are synthesis work types.
  They are common outputs inside ordinary product projects and service-design engagements.

Purpose can distinguish some cases, but it does not rescue the node. `00` correctly says, “Topic answers what a file is about, while purpose answers what the file was for.” A product decision,
release or backlog reference can route an artifact into an accepted **product project**. That is the
schema's existing project anchor. It does not prove that all files made with the same method require
a new template.

The deletion test makes the failure operational. Delete `user`, `customer`, `participant`,
`research`, `interview`, `survey`, `usability`, product names, participant codes and document-type
words. What remains is a generic question list, meeting transcript, response table or recommendation
deck. Unlike a requirements sheet's fixed labelled relations or market research's competitor matrix,
no structure remains that is both true of this row and false of the listed neighbours. Leg 1 fails.

### Leg 2 — recommended dimensions: fails

The gist prose recommended study, then document function, with a possible fielding period. `Study` is
not a new dimension. It is the schema default's **project** anchor under domain vocabulary. Protocol,
raw session, synthesis and readout are document-function/work-type values. A fielding period is the
default period level. The recommendation therefore repeats the schema default rather than differing
from it.

The tempting participant level is specifically invalid. A participant folder would collect a named
third party's signed consent, face, voice and free text under their identity. `00` says, “A folder should not become a collection point for everything produced by the same person or organization.”
It also says authorship or creator identity should not be a destination. Rejecting participant-first
is correct safety practice, but after that rejection the row has no unique dimension left.

The JSON's `dimension_order` remains empty for the independent binding reason that the schema declares
no field rows. This is not used as a cheap refusal: every sibling shares the restriction. The
substantive comparison is the prose recommendation, and it is project → function, exactly the
default. Leg 2 fails.

### Leg 3 — privacy rules: fails, without weakening protection

The files are frequently sensitive. Signed consent carries identity and signature; recordings carry
face and voice; transcripts contain volunteered employers, cities, health facts or account names;
respondent exports can be bulk registers of identified opinions. “Privacy policy must be enforced before content reaches any model or external connector.” For protected files, “Protected material should not be included in cloud-model prompts by default, should not display raw content in general group summaries, and should not be moved automatically without a user policy that explicitly permits it.”

Those protections attach through P7 and file evidence. They are already the schema posture and do
not depend on this row. Refusing the row removes a proposed folder label; it removes no protection.
The JSON therefore retains `sensitivity: potentially_sensitive` and protective fallthroughs. Leg 3
fails because the rule is inherited, not because the material is harmless.

### Verdict

**Refused on all three legs.** This explicitly reverses the gist draft. The gist was right about the
practice, examples, false positives and protective posture, but it mistook a purpose-coherent bundle
for a distinct template. `00` says, “The documents are content-incoherent but purpose-coherent.” P9
may therefore group a guide, consent, recording, transcript, notes and readout around an accepted
product project. It need not promote the method or participant population into a node to do so.

## Files considered, including rejected evidence

The JSON carries ten concrete fixtures. Their evidentiary outcomes are:

- `Checkout study - discussion guide v2.docx`: real product work, but a guide work type inside the
  product project. Its method shape does not activate this row.
- `P04 consent signed.pdf`: reliable protected-material evidence; not reliable product-purpose
  evidence. Academic and employee studies are byte-identical at this layer.
- `P04_session_20260512.mp4`: sparse media may join an accepted group but must not acquire the
  neighbour's study facts. “The graph does not automatically copy those missing facts onto sparse files.”
- `transcript_P04.vtt`: the primary privacy fixture and a primary false positive. Speaker labels and
  timestamps belong to many domains.
- `survey_responses_may.csv`: the population is unknown from its table structure. Customer,
  employee, panel and academic readings remain live until cited evidence resolves them.
- `Checkout findings and recommendations.pptx`: a synthesis can feed requirements, but recommendation
  prose is not acceptance criteria and the deck is not a new filing world.
- `Spec review - checkout notes.docx`: minutes of a review of a named specification stay with the
  specification situation; a standing cross-project meeting stays with meeting-record.
- `Interview notes - P07.docx`: individual evidence about competitors can support a market study;
  its input provenance does not create a separate node.
- `Discovery call - Northwind Ltd.docx`: interview-shaped but account-anchored. The customer and sales
  owner slots route it toward customer-account-management.
- `Our 5 year plan.docx`: customer-interview evidence summarized inside a strategy plan does not
  transfer ownership of the plan.

Also considered and rejected from JSON examples to avoid redundant shapes: a diary-study app export
(survey/response-table logic), a tree-test CSV (method value), a card-sort export (method value), a
persona `.fig` file (synthesis work type), a highlight reel (recording/synthesis), a recruiting email
(supporting artifact with no unique structure), a blank screener (questionnaire), an academic IRB
approval (research ethics rather than product work), an employee pulse-survey export (HR), and a saved
article about customer behaviour (Reading Inbox absent an active project).

## Collision fixtures and reciprocal boundaries

Because the row is refused, the JSON does not author collision edges from a node that cannot activate.
The routing boundaries still matter and are stated in both directions here.

### Product requirements

Same bytes: `Checkout findings and recommendations.pptx`. The findings side contains observations,
quotes and recommendations supported by sessions. Product requirements takes intended behaviour,
acceptance criteria, non-goals or traceability relations. In the other direction, a PRD that cites a
user quotation remains a PRD. A findings deck that links to proposed backlog items does not become a
PRD until the intended/accepted requirement structure exists. The neighbour's memo names this same
fixture class and boundary.

### Meeting record

Same bytes: `Spec review - checkout notes.docx`. A standing team meeting with attendees, agenda,
decisions and actions belongs to meeting-record. Minutes whose organizing object is a named accepted
specification stay with that product situation. A user interview transcript is not made a meeting
record merely by two speakers; conversely, ordinary meeting minutes are not made research by a
customer-insight agenda item. Method vocabulary alone loses in both directions.

### Strategy plan

Same bytes: `Our 5 year plan.docx`. A strategy plan is anchored on horizons, objectives, initiatives,
owners and measures. Customer interviews are evidence within it. In the other direction, a study
readout mentioning strategic implications remains project evidence unless it actually adopts the
multi-horizon plan structure. Neither row steals the other's complete artifact on a cited paragraph.

### Market research

Same bytes: `Interview notes - P07.docx`. Market research takes aggregate market structure: competitor
sets, segments, price points, sizing ladders and commercial questions. Raw interview notes take
protection from their individual provenance but may support that project. In the other direction, a
competitive matrix does not become user research because one source was an interview. The existing
market-research row can stand on its own structure; this refused row cannot.

### Customer account management

Same bytes: `Discovery call - Northwind Ltd.docx`. Where a named provider/customer relationship,
account owner, opportunity or next-step apparatus is the anchor, customer-account-management owns the
group. Where a call is one input to a product project, P9 may group it there without asserting an
account fact absent from the file. `Customer` as a word cannot decide between those readings.

### Research and research ethics

Same bytes: `P04 consent signed.pdf` and a hypothetical `Interview - Dr Adeyemi - IRB 2026-114.docx`.
Protocol number, review-board approval, lab, venue and publication intent route toward research and
ethics-compliance. Product name, release decision and backlog context route toward a product project.
Consent itself chooses neither. If both purposes genuinely occur, the graph may represent both on
disjoint cited evidence; this refused row still does not activate.

### HR engagement survey

Same bytes: `survey_responses_may.csv`. Workforce population, department or employment-cycle context
routes toward HR; product/customer context routes toward a product or account project. The bare
response table belongs to neither until the population role is evidenced, and because it contains
named free text it remains protected while unresolved.

## Neighbours considered without edges

- `career`, `finance` and `hr` were mandatory schema neighbours. Career interviews and finance
  customer calls share transcript shape but have strong first-person/custodial anchors; no edge is
  justified from a refused row. HR's actual survey collision is documented above.
- `business_operations.support-operations`: a support transcript shares raw shape. Ticket/case id,
  queue, status and resolution structure route it there. Boundary only.
- `business_operations.customer-account-management`: account structure resolves the discovery-call
  fixture. Boundary only.
- `research.dataset-analysis`: survey-response analysis can be dataset work, but analysis stages and
  reproducible outputs are its structure. A raw export does not activate either by itself.
- `research.reading-library`: saved third-party reports without an accepted project route to Reading
  Inbox/reading-library. They are not evidence gathered from users merely because users are the topic.

No `collides_with` or `also_holds_with` edge is authored because the subject row is refused. Adding
edges would imply it can participate in activation. The memo preserves the reciprocal routing rules
for R1c without making that contradiction.

## Fields, work types and residual routing

`fields: []` is binding. `proposed_fields: []` is deliberate. `study` would duplicate canonical
`project`; `participant` would be a person-value collector and a privacy hazard; `method` and
`artifact_type` are work-type vocabulary questions rather than dimensions licensed here.

The previous `work_types` list was removed from the refused JSON because a refused node should not
own a vocabulary. The useful terms are not discarded conceptually: interview, usability session,
survey, diary study, screener, consent, transcript, observation notes, affinity synthesis, persona,
journey map and findings readout are candidates for a shared controlled work-type catalogue if one
is adjudicated.

Fallthrough is explicit. Durable unattached guides and readouts go to Independent Records; partly
understood research-shaped files go to Review Later; isolated consent, recordings, transcripts and
respondent tables can go to Protected Records; unreadable or encrypted media/archive material goes
to Unsupported or Encrypted. Reading Inbox remains appropriate for saved publications, but is not
authored in JSON because none of the retained ten examples is a publication.

## NEEDS-JOSEPH

**NJ-BO-UR-1 — controlled research-method vocabulary after refusal.** Alternatives:

1. Keep this roster node for discoverability. Cost: violates the node test and repeats the original
   catalogue mistake by promoting values/work types into structure.
2. Retire it and allow only free-form `work_type`. Cost: lean structure, but inconsistent naming and
   weaker cross-project search.
3. Retire the node and adjudicate shared controlled work-type values for interviews, usability
   sessions, surveys, diary studies and synthesis artifacts. Recommended; cost: D6/R1c must own a
   vocabulary used across business, HR, research and market contexts.

**NJ-BO-UR-2 — mixed-purpose human-subject material.** A university lab can run product usability
work for a commercial sponsor, yielding one consent form and transcript with both publication and
product-decision evidence. Alternatives: multi-schema facts on disjoint citations (faithful, but
more complex); force one dominant purpose (simple, but loses truth); or defer until the accepted
group supplies context (safe default). This row recommends defer, then permit both where independently
cited. Refusal does not settle the cross-schema join.

**NJ-BO-UR-3 — participant identity as search-only metadata.** A participant key is rejected as a
destination, but incident response and consent withdrawal may require finding every artifact for one
person. Alternatives: no normalized key (safer but operationally weak); a protected metadata-only
identity key (useful but creates dossier risk); or an opaque study-local participant token linked
locally to consent (best balance, but a new privacy mechanism). This row proposes no field.

## What changed in this pass

- Reversed `refuse_node: false` to `true` after testing all three legs against the deepened schema
  anchor.
- Replaced method-shaped deterministic signals with an explicit finding that none distinguishes the
  proposed situation.
- Removed the row-owned context-term and work-type catalogues; no refused node should own them.
- Preserved ten concrete fixtures, strengthened observation/fact separation and made all sparse-file
  joins non-propagating.
- Replaced activation edges with reciprocal boundary prose because a refused row cannot collide or
  also-hold as an active node.
- Preserved sensitivity and four safe fallthroughs so refusal removes no protection.
- Added three explicit NEEDS-JOSEPH decisions rather than silently choosing vocabulary, cross-schema
  joins or participant identity handling.

## Self-verification

JSON parsing, universal-key equality, source-type membership, edge/residual validity, quote checks,
J-DEPTH header, memo completion and claim agreement were run after writing. The result is recorded in
the agent return, not assumed here.

**Complete ending: the row is refused; its real files remain protected and routable through existing
projects, schemas and residuals, with no field or canonical key minted.**
