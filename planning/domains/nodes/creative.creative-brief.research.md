# Research memo — `creative.creative-brief`

Date: 2026-08-24
Output: `planning/domains/nodes/creative.creative-brief.json`
Roster row: template on the fieldless `creative` schema, `parent_id: null`, placeholder launch
Absorbs legacy row: `studio.creative-brief` (ROSTER.md Appendix A, line 754)

## Result

**Refused.** `refuse_node: true`. A creative brief is a document type inside one client engagement, not an organizational situation of its own. The row fails all three legs of the node test, and it fails them in the exact way the design documents already ruled on in the academic world.

The refusal is not a coverage loss. Everything the row was meant to catch is routed: the brief-shaped document is the anchor detection signal on `creative.client-engagement`; `brief` is a `work_type` VALUE that a later field ratification would place at the terminal level of that template; and Independent Records / Review Later / Reading Inbox are the broad homes for a brief that arrives with nothing to attach it to. The `falls_through_to` block carries all five residual routes with verbatim `00` definitions.

## Binding material read

- `planning/prompts/ALIGNMENT.md` — the alignment contract, in full.
- `planning/00-database-agent-product-design.md` — authoritative; every quotation below was grepped back out of it verbatim before this memo was written.
- `planning/domains/CONNECTION.md` §1–§5 — the four graphs, the node test, no schema-tree inheritance, the activation algorithm, the closed edge vocabulary.
- `planning/domains/_CONTRACT.md`, `planning/domains/canonical_fields.json`, `src/evidence_shape/vocabulary.py`.
- `planning/domains/roster.json` — this row, the `creative` schema row, and the four siblings named below.
- `planning/domains/ROSTER.md` §4, §7 and Appendix A — the 41 `creative.*` rows and their legacy sources.
- Calibration: `planning/domains/nodes/legal.practice-matter-file.research.md` (depth and idiom), `planning/domains/nodes/business_operations.organisational-records.json` (refusal shape).
- `planning/overnight/council/DECISION-BRIEF.md` — D1–D6 and J-IND as ratified; not re-debated here.

Controlling consequences for this row:

- `creative` is a J-IND / PR-6 fieldless placeholder schema. `fields`, `proposed_fields` and `dimension_order` are empty by contract, not by omission.
- Because the schema declares no fields, **no `creative` template can be distinguished by its dimensions.** Every `creative` sibling must therefore earn its row on detection signals or privacy rules alone. That raises the bar for this row specifically, and it is where the row fails.
- Activation is a set-valued function over schema ids. It never outputs template ids. A template row that never contributes a distinct signal contributes nothing to activation at all.

## The node test, argued in full

### Leg 1 — detection signals

The candidate signal is a document whose own labelled sections run background, objective, audience, proposition, deliverables, mandatories, timing, budget and approver, naming a commissioning organisation in one role slot and a producing person or studio in another. That signal is real and worth recognising. **It is also the single strongest piece of evidence that a client engagement exists.**

That is the problem, and it is structural rather than a matter of taste. CONNECTION.md §4 step 3 resolves collisions *per evidence item*: where one item supports two rows joined by `collides_with`, the item counts for the better-supported side only if it beats the other by the injected margin, otherwise it counts for neither. Authoring the brief document as constitutive of this row and as the anchor of `creative.client-engagement` puts one evidence item permanently on both sides of a pair that can never separate — the brief is not *better evidence* for one than the other, it is the *same* evidence. The margin rule would then zero it out for both, which is worse than not authoring it here at all.

Subtract the engagement evidence and audit what remains. The residue is: the token `brief` or `commission` in a filename; a document-type heading; a client name. Each is independently never-alone, and — the point that matters — combining them does not help, because all three are ambiguous *in the same direction*. `Brief.pdf`, `Creative Brief Template.docx`, `Appellant's Opening Brief.pdf` and a saved awards-entry case study all satisfy the whole residue. The organisation-name half of it is never-alone by `00`'s own reasoning:

> A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.

The role-ambiguity argument there is about *roles*, not about universities, and it transfers intact to a client, an agency, a studio or a brand. The document-type half is worse than a university name, because `brief` is a homonym across four unrelated worlds — an appellate brief, a design brief, a media-planning brief, a press briefing note. CONNECTION.md §4 step 2 strikes any schema whose entire support is never-alone evidence. A template whose entire distinct support is never-alone evidence is a row that can never fire.

### Leg 2 — recommended dimensions

Identical to the neighbour's, and empty in any case. But the interesting part is what the dimensions would be *if* the `creative` schema were later given fields, because that is where the row's real nature shows.

`00`:

> A work type such as Homework 3 is meaningful only after the course is known, and a course code may require the school or term to disambiguate it.

`Creative Brief.docx` is meaningless until the client and the job are known. By the design document's own ordering rule the brief therefore sits at the **terminal** level, as a value under the engagement — not as a branch above it. ALIGNMENT states the consequence for the parallel case outright: *Syllabus / Homework / Lectures are values of work type, not extra schemas*, and lists "a schema per work type (`acad.syllabus` vs `acad.homework`)" among the things the swarm must not rebuild. A creative brief is the creative world's syllabus: the document that opens the work and states what it must do, for whom, by when. The parallel is not loose; it is the same sentence with the nouns changed.

There is also a concrete trap this row would have walked into. Its natural dimension order is document-type-first — a folder called `Briefs` holding every brief for every client, across years. `00` requires the engine to validate that a proposed template does not

> use an author or organization merely as a collector

and the reasoning behind that clause — a level that gathers files by *what they are* rather than by *what they are for* defeats retrieval — applies identically to a document-type collector. The brief for the Northwind rebrand belongs next to the Northwind moodboards, schedule and deliverables, not next to eleven unrelated briefs.

### Leg 3 — privacy rules

Identical to the engagement's. Briefs do carry sensitive material: unreleased product and campaign information, embargo dates, pricing, fee and budget figures, named client contacts with their addresses, explicit NDA references. But every one of those sensitivities is a property of *the job being unreleased*, and it applies with exactly equal force to the artwork, the schedule, the invoice and the handoff package for the same job. A privacy posture the neighbour already carries in full is not a distinguishing privacy rule.

The refusal transfers the posture rather than dropping it: `sensitivity: potentially_sensitive` and `sensitivity_why` are recorded on the refused row and state explicitly that `creative.client-engagement` inherits them, and Protected Records is kept in `falls_through_to` for the embargoed and the homonym-legal cases.

CONNECTION.md §2 states the test: *a template row exists only when its detection signals, recommended dimensions, or privacy rules differ from its schema's default template.* None does.

## Files considered and rejected

Eleven fixtures are in the JSON with their observations, prohibited conclusions and residual routes. Why each exists:

1. `Creative Brief - Northwind Rebrand - v2.docx` — the happy case, the one that makes the row look plausible. Its two explicit role slots (`Client:` / `Prepared by:`) are the point: this is `00`'s consulting-role shape, and reading which organisation is in which slot is the work, not naming a row after the document.
2. `Northwind_Brief_APPROVED_FINAL_v3.pdf` — carries `APPROVED`, `FINAL` and `v3` at once. Shows the row competing with `creative.revision-round` and with the universal version-family fact over the same bytes. The signature block is the observation; the filename tokens are noise.
3. `RE Brief for the summer campaign.eml` — the brief *is* the message body. No document exists. A row named after a document type cannot recognise its own subject matter here.
4. `Brief.pdf` — the bare document-type word, and on its observations an appellate brief. This is the row's own name defeating it.
5. `Appellant's Opening Brief.pdf` — **the collision fixture proper.** Same word, no creative content at all. Discriminated by the tribunal caption and counsel block, which no creative brief carries. Routes to `legal` and Protected Records.
6. `Creative Brief Template.docx` — a blank agency template: the entire structural signal, none of the situation. The cleanest demonstration that the structure cannot be a row.
7. `Screenshot ... brief in Slack.png` — OCR of brief prose. Screen-origin metadata and window chrome prove screen origin; missing EXIF proves nothing. Co-activates `photos`.
8. `Northwind Kickoff Pack.zip` — manifest read without extraction, holding brief + moodboard + scope + schedule + logos. `00` on the packet shape: the LLM asks *"whether the files plausibly serve one shared workflow, whether the group is purpose-coherent despite topic diversity, which members appear to be supporting materials rather than unrelated records"*. The brief is the supporting material that names the workflow.
9. `Commission request - character illustration.eml` — the `and commissions` half of the row name, and the one genuinely unresolved case (see NEEDS-JOSEPH 1).
10. `Brand Guidelines - Northwind.pdf` — cited *by* the brief's Mandatories section. Being cited retrieves a candidate and copies nothing; it belongs to `creative.brand-identity`.
11. `Statement of Work - Northwind Rebrand - signed.pdf` — the engagement anchor, not a brief. Confusing the two is what makes the boundary visible.

Deliberately not represented, and why:

- **A project-management or brief-authoring SaaS export** (a workspace dump, a form-builder submission) is a source system, not a file node. A bounded export with a readable manifest is already covered by fixture 8.
- **A pitch deck or proposal** is a different situation with its own row candidates; it argues for work rather than specifying it, and folding it in here would have padded the refusal into something that looked like a node.
- **Calendar and contact files.** A kickoff meeting `.ics` and a client's `.vcf` sit near a brief but never activate on it. `00` requires contact data to be *"privacy-protected rather than used to create folder proposals"*, and calendar is a `SOURCE_TYPE`.
- **Design source files** (PSD, AI, INDD, FIG). They are the engagement's output, not its opening document, and their formats prove nothing: `00` requires the engine to *"treat the file extension as a routing signal rather than an assumption about meaning"*.
- **A brief-shaped document in an academic or research corpus** — an assignment sheet, a grant call. Same structure, different world, resolved by the other domain's own context terms.

## `proposed_fields` — none, with the argument

Empty, and deliberately so. Two separate reasons:

1. The row is refused. Proposing fields for a row that does not exist would hand R1c a phantom.
2. Even if it survived, it would need no new key. ROSTER.md §7 records that if NJ-R1a-1's option (b) is ever taken, *"the candidate fields are still the existing keys `project`, `stage`, `artifact_type`, `client`; nothing here forecloses it."* A brief's organizing facts are exactly `client` and `project`, with `brief` as a value of a work-type-shaped key. Nothing about a brief motivates a key that does not exist. Minting `brief_type`, `deliverable`, `deadline` or `approver` would be the D6 violation and the 574's habit.

`proposed_context_terms` is also empty. The academic floor terms are `00`'s; this row does not get to invent a creative equivalent, and the terms it would want (`deliverables`, `mandatories`, `tone of voice`) are listed in `never_alone` instead, where they are honest.

## Reciprocal boundaries with the parallel siblings

These are stated in both directions. The four sibling rows were being written in parallel and had not landed when this memo was written; each boundary is stated here so its owner can accept or contest it, and none is assumed.

- **`creative.client-engagement`** — *takes* this row's whole subject. The brief-shaped document, with its two organisation role slots and its labelled deliverables section, is the engagement's anchor detection signal and should be authored there. In the other direction, engagement owes this refusal one thing: it must not treat every document *mentioning* a brief as engagement evidence, and it must read the role slots rather than assuming the holder is the supplier. **Same fixture bytes on both sides:** `Creative Brief - Northwind Rebrand - v2.docx` and `Northwind Kickoff Pack.zip`.
- **`creative.revision-round`** — owns what happens to the brief *after* it is issued: v1 → v2 → APPROVED, and the feedback that moved it. This row does not own the version family, and revision-round should not claim the initial issue as a round. **Same fixture bytes:** `Northwind_Brief_APPROVED_FINAL_v3.pdf`.
- **`creative.deliverable-handoff`** — the mirror at the other end of the job. A brief's Deliverables section *names* what a handoff package later *contains*, and the two documents can list identical items in identical words. The discriminator is direction and tense: a brief specifies what does not exist yet; a handoff note describes files that do, and travels with them. **Same fixture bytes:** the Deliverables section of fixture 1 versus a handoff manifest.
- **`creative` (the schema)** — its `one_line_hint` sets the family posture: a fieldless placeholder answering NJ-R1a-1, writing no field rows. The schema's own default template is where a brief-shaped document with no engagement anywhere in the corpus lands. This row asks the schema owner for nothing and constrains it in nothing.
- **`career.consulting-client-engagement`** — a non-creative consulting brief has the same section structure. The discriminator is whether the deliverables are creative artefacts. Not authored as an edge here because the edge belongs on `creative.client-engagement`, which is the row that actually competes.

## Neighbours considered that got no edge

`collides_with`, `also_holds_with` and `role_split` are all empty, which is correct for a refused row: a refused row must not leave live mutex edges pointing at it, because R1c would then have to author reciprocals into a node that does not exist. The competitions described above are real and are recorded in prose and in the fixtures so their owners can author them on the surviving side.

Specifically not edged:

- **`legal.practice-matter-file`** — the appellate-brief homonym is a *word* collision, not an evidence collision. No shared observation beyond a filename token, and the tribunal caption separates them instantly. A `collides_with` on a homonym would be the format-as-schema bug wearing a different hat.
- **`photos`** — the Slack screenshot co-activates on its own screen-origin evidence. Co-activation, not competition, and it is recorded as `also_schema` on the fixture.
- **`code`** (a `must_consider_neighbors` entry) — a brief for a software project routes to code by repository and project-root markers, none of which a brief carries. No shared evidence.
- **`creative.brand-identity`** — cited-by is not membership.

## Open questions surfaced

### NEEDS-JOSEPH 1 — the `and commissions` half of the row name

The roster names this row *Creative briefs and commissions*. The brief half is refused above with confidence. The commission half is genuinely less settled, and the refusal should not silently swallow it.

An **inbound commission approach** — an unsolicited request to make a piece of work, arriving before any relationship exists, with no scope document, no fee agreement, no project and frequently no outcome — is arguably a different situation from a brief inside a live engagement. Its evidence is an unattached enquiry rather than an anchored document; its privacy exposure is a stranger's contact details rather than an embargoed campaign; and its usual correct outcome is that nothing was ever made.

Alternatives, stated rather than chosen:

- (a) Leave it refused, as here. The enquiry falls to Review Later, which is what `00` designed Review Later to do, and no row is minted for a situation whose commonest outcome is nothing.
- (b) Mint a new row named for the enquiry situation — but note its nearest home may be `career` or `creative.submission-query` (which already owns the outbound mirror: the holder querying a publisher) rather than a creative-production row at all.
- (c) Fold it into `creative.client-engagement` as that row's earliest stage.

This row does not decide. It records the fork in `open_question` and mints nothing.

### NEEDS-JOSEPH 2 — the fieldless-schema consequence, noted upward

NJ-R1a-1 is recorded in ROSTER.md §7 as **answered** by J-IND (2026-08-22): option (a), a field-less placeholder schema, 41 templates, no field rows. The dispatch message described it as OPEN; the roster is the later authority and this memo follows it, recording the discrepancy rather than resolving it silently.

The dependency worth surfacing for R1c: because `creative` declares no fields, *no* `creative` template can be distinguished by `dimension_order`, so the node test collapses to two legs for all 41 rows. That is a fair bar for rows like `creative.raw-photo-catalogue` whose detection signals are genuinely their own. It is a harsh one for rows whose distinctness was always going to live in the folder shape. If option (b) is ever taken and `project` / `stage` / `artifact_type` / `client` become `creative` fields, **this refusal should be re-examined but not automatically reversed** — under those fields the brief becomes a terminal `stage` or work-type value, which strengthens the refusal rather than weakening it.

## Final recommendation

Keep `creative.creative-brief` refused. Route the brief-shaped document to `creative.client-engagement` as its anchor detection signal, and to the `creative` schema's own default template for the unattached case. Treat `brief` as a value, not a row. Preserve the sensitivity posture on the engagement. Hold the `and commissions` question open for Joseph rather than minting a row to cover it.
