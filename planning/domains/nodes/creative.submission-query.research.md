# Research memo — `creative.submission-query`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/creative.submission-query.json`
Roster row: template on the fieldless `creative` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accepted, and narrowed.** The row survives as the purpose-coherent packet a maker assembles to **offer a made work to a party who has not commissioned it**, together with that party's reply and the ledger of the same work going to many markets. Its anchor is an **addressee in a submitted-to role**, which the creative schema has no key for and cannot get from `client`.

The row was accepted only after the charge below failed on evidence. It was narrowed twice in the process: it does not own the piece being submitted (that stays with `creative.book-manuscript` / `creative.short-form-writing`), and it does not own the downloaded guidelines document that provoked the packet (Reading Inbox).

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (full).
- The stamped assignment from `make_prompt.py creative.submission-query`.
- `planning/00-database-agent-product-design.md` — read by targeted `grep -n`, per the token discipline. Every span in quote marks in the node and in this memo was grep-verified verbatim against that file before use; the verification run is recorded at the end.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — depth calibration (one landed launch row, as instructed).
- `planning/domains/nodes/creative.json` — the schema anchor and its **default template**, which is what this row is measured against.
- `planning/domains/nodes/creative.book-manuscript.json` and `creative.creative-brief.{json,research.md}` — the two landed rows that already argued a boundary against this id (found by the single permitted `grep -rl`).
- `planning/domains/roster.json` — every neighbour id in the node was confirmed present on the roster.

Not read, deliberately: other creative siblings, `01-product-design-structured.md`, `CONNECTION.md` beyond what the anchor and the brief restate. Nothing in the node depends on them.

## THE CHARGE — the strongest case that this row should not exist

Stated before anything was written, in its most damaging form. There are six charges and they are not weak.

**C1 — it is a lifecycle stage.** The creative schema anchor lists `stage` values as "brief, concept, draft, review round, approved, delivered, published, archived". *Submitted* sits between draft and published as obviously as any of them. If "sending it out" is a stage, it is a **value** of an existing field, and the node test says values are not nodes.

**C2 — it is named after document types.** "Query" and "submission packet" are document-type words. `creative.creative-brief` was **refused on exactly this ground** by a landed row in this same directory. A row whose name contains a document type is presumptively the same mistake.

**C3 — it is `career.recruiting` in creative clothes.** 00's canonical example of purpose coherence *is* an application packet. A gallery submission and a design-job application both contain a covering letter, a CV and a portfolio PDF. If the archetype already has a home, this row is a second copy of it.

**C4 — it duplicates `creative.deliverable-handoff`.** Both are "an export set plus a covering note, going to a named organisation on a date". Same fixture shape, same source types, same signals.

**C5 — it is defined by an absence.** Its distinguishing feature looks like *no commission exists yet*. The schema anchor explicitly forbids that move: "the mere ABSENCE of a client read as proof the material is personal". A row whose only content is a missing counterparty can never activate.

**C6 — it is the schema's default template.** The default is client → project → stage → artifact_type. A submission is a project at a stage producing an artifact. Nothing new.

### How the charge was defeated

**Against C1 and C6 together — the fan-out.** A stage is a position on one work's timeline; it has one value at one time. This situation is **one-to-many and simultaneous**: the same partial goes to forty agents over two years, and the forty offers are contemporaneous, differently addressed, and separately resolved. Under the default template all forty collapse into a single `stage=submitted` folder and the only fact that distinguishes them — who it went to — has nowhere to live. The tracker fixture makes this concrete: `Submissions tracker.xlsx` is a table whose *rows* are the fan-out, and no other creative situation produces a table like it. A stage cannot have forty simultaneous values; an addressee can have forty simultaneous instances. **C1 fails, and C6 fails with it, because the difference is a dimension difference, not a signal difference.**

**Against C2 — the row was renamed away from the document.** The `creative.creative-brief` refusal is correct and is followed here, not evaded. The node's `name` is *"Sending a made work out to someone who may say no"* — a situation, not a document. The query letter is one fixture among seventeen, and it is explicitly **not sufficient**: `Cover_letter_TEMPLATE.docx` carries the entire letter apparatus with `[AGENT NAME]` unfilled and activates nothing. The row would survive with the letter deleted, because the response, the ledger, the entry form and the portal confirmation would still be there. That is the test a document-type row fails. Note that `creative.creative-brief`'s own memo names this row as "the outbound mirror" and its `open_question` routes the inbound-enquiry situation here as a candidate home — the landed refusal treats this id as real.

**Against C3 — what is offered.** This is the sharpest charge and it does not fail on structure; it fails on the ask. `career.recruiting` offers **the person's labour**, and the outcome is that a person is hired. This row offers **a made work**, and the outcome is that the work is published, exhibited, performed or sold. The letter is where that is readable, and only there — which is why the node marks it `needs_llm` and not `deterministic`. The two fixtures are deliberately built to be byte-confusable: `Query - Nightwork - Alderman Literary.docx` and `Cover letter - Senior Designer - Studio Kettle.docx` have identical structure and share their two enclosures. The genuinely-both case (a maker seeking **representation** from an agency) is filed as `also_holds_with: career`, not resolved by fiat.

**Against C4 — whether the recipient asked.** A handoff *fulfils*: it has a round history behind it, its note reconciles against an agreed scope, its counterparty is paying, and it cannot be declined. A submission *offers*: no round history, the note pitches, the enclosure is a sample rather than the whole of what was owed, and **a rejection letter can exist**. `RE Query - Nightwork.eml` is the fixture that cannot occur on the handoff side at all. This row is the only creative situation that routinely files a decision the holder did not make.

**Against C5 — the anchor is positive, not negative.** The row does not activate on a missing client. It activates on a **positively evidenced addressee in a submitted-to role plus an offer sentence**, and the node's `never_alone` list says so in terms: "THE ABSENCE OF A COMMISSION READ AS PROOF OF SUBMISSION. Absence selects nothing." Self-initiated work, personal experiments and abandoned drafts all lack a commissioner and none of them has been offered to anybody.

**Verdict: `refuse_node: false`.** The charge was real and cost the row two of its claims.

## The node test, all three legs

The default template it is measured against is the prose held in `creative.json`: *client only where the corpus genuinely serves more than one client, then project, then stage, then artifact_type; not time-first.* A creative template row exists only where its **detection signals**, its **dimensions**, or its **privacy rules** differ from that. All three differ here, which is more than the test requires.

**Leg 1 — detection signals differ.** The schema's deterministic signals are all *making* structures: linked assets, layers and artboards, revision rounds, briefs, delivery sets, production paperwork, script grammar, timelines and media, catalogue sidecars. **Not one of them is present in this row's core fixtures.** `Query - …docx`, `Submissions tracker.xlsx`, `RE Query….eml`, the entry form and the portal confirmation contain no linked assets, no layers, no version family and no media. This row's signals — addressee-plus-offer, enclosure-list-answering-a-requirement, response, ledger, submission-system, exclusivity — are disjoint from the schema's. That is the strongest possible form of leg 1, and it is also why the row cannot be folded upward: activating the schema's own signals on this material would find nothing.

**Leg 2 — dimensions differ, and the difference is the fan-out.** Argued above. Recorded as prose in `template.why` because `dimension_order` must stay empty on a fieldless schema. The sharp finding is that the difference **cannot be serialized even under option (b)** of NJ-R1a-1, because an agent, an editor and a jury are not `client`s. See NEEDS-JOSEPH 1.

**Leg 3 — privacy rules differ.** The schema's posture protects *the work and the client's confidence*. Three of this row's four reasons are its own: (a) the **maker's personal data travels in every packet** — postal address, telephone, bio, sometimes date of birth or nationality on an eligibility declaration, and a tax identification form on a sale packet; a delivery folder carries none of that; (b) **third-party confidential documents** — a reference letter is written *about* the corpus owner *by* someone else, often under a confidentiality legend, and the owner may not be entitled to circulate it at all; (c) **the ledger is a private record of refusal** — marked INFERENCE in the node, because it is a judgement about how people feel about their own files rather than anything 00 states. (d) exclusivity and reading-period status can carry real obligations. Governing sentence, verbatim: "Privacy policy must be enforced before content reaches any model or external connector."

## Files considered and rejected

Seventeen fixtures are in the node. These are the ones that were tempting and were **kept out**, or kept in only as negatives.

- **`Aperture Open Call 2026 - guidelines.pdf`** — rejected as evidence, retained as a fixture routed to Reading Inbox. It reads like a brief: deliverables, deadline, specification, rights clause. It is not, because **nobody addressed it to the holder** and it is identical for every applicant on earth. It becomes evidence only *paired* with a local set that answers it. This is the row's commonest false positive and the reason `GUIDELINES-ANSWERED` is written as a pairing rather than a document.
- **`Cover_letter_TEMPLATE.docx`** — the unfilled letter. Carries every structural signal this row has except the addressee. Kept as the fixture that defeats "addressee block alone".
- **`Artist Statement 500 words.docx`** — not rejected but explicitly refused a single owner. It is 00's shared-material case moved one world over ("A transcript may be part of several application packets"), and the node marks it `group_without_copying_facts: true` with the instruction to abstain rather than pick a packet: "It should abstain or ask the user to choose a primary home."
- **A DAM export, a Submittable account, an agency's own inbox** — source systems, not files. A bounded export with a readable manifest is representable; live connectors are a later decision.
- **The submitted work's own working files** — `.psd`, `.indd`, `.docx` drafts, session files. These belong to the making rows. Only the **cut** (`_partial`, `_excerpt`, `_10images`) is this row's material, and even it retains its version-family link home.
- **Fee receipts as the row's own evidence** — rejected. `FilmFreeway - entry receipt….pdf` is independently a finance record; a shared festival name does not bind it to a local packet.
- **Contest results pages, agent wish-lists, market databases** — reading material.
- **Work-type, medium and market taxonomies** (literary vs. visual vs. film vs. music submission) — deliberately not enumerated. They are values of `artifact_type` and of a market vocabulary, and enumerating them would turn a placeholder into the industry catalogue J-IND forbids this round.

## Reciprocal boundaries

Eight `collides_with` edges, each naming the same fixture on both sides. In brief, with the shared bytes:

| Neighbour | Shared fixture | This row claims when | They claim when |
|---|---|---|---|
| `career.recruiting` | covering letter + `CV.pdf` + `Portfolio_2026.pdf` | the ask offers a **made work** | the ask offers the **person's labour** |
| `career.portfolio-work-samples` | `Portfolio_2026.pdf` | it is an enclosure in **one addressed act** | it is the **standing** addressee-free artefact |
| `creative.deliverable-handoff` | dated zip + covering note | nobody asked; a decline is possible | it fulfils an existing commission |
| `creative.client-engagement` | cold pitch deck | the offer is of a work **already made** | the offer is of capability and work not yet made |
| `research.manuscript-publication` | `cover_letter_to_editor.docx` + decision letter | a work of authorship offered to a market | a research artifact with abstract, methods, references, venue |
| `creative.book-manuscript` | `Nightwork_partial_50pp.docx` | a packet member evidenced by letter + synopsis + ledger | a compiled state of the work, with its version_family link |
| `creative.short-form-writing` | an essay naming an outlet | the letter, response, receipt and ledger row | the piece itself |
| `photos.camera-events` | ten numbered JPEGs with full EXIF | image list + entry form + statement + letter | a capture event on its own evidence |

Every one is written in **both** directions in the node. Two are worth naming here as genuine constraints on this row rather than on the neighbour: the `creative.book-manuscript` edge is **already authored on that side** and this row adopts its wording verbatim rather than restating it in this row's favour; and the `career.portfolio-work-samples` edge concedes that the schema anchor assigns career the `design_creative` file_kind_owner role for "a curated set of finished exports … named for a submission" — a direct claim on this row's material, resolved by standing-versus-instance and by this row not re-filing the portfolio.

Neighbours considered and **not** given an edge:

- `creative.revision-round` — a requested revision after a submission is a round, but the seam is already carried by `creative.book-manuscript` and `creative.deliverable-handoff`; adding a third would be taxonomy, not a same-evidence mutex.
- `creative.exhibition` / `creative.publishing-title` / `creative.periodical-issue` — these are what an **accepted** submission becomes, which is a lifecycle succession, not a competition for the same bytes. Recorded as NEEDS-JOSEPH 2 instead.
- `research.grants-funding` — genuinely structurally identical for a residency or arts-council application. Not made a collision because the recommendation, if one row must hold both, runs the *other* way (widen the funding row); recorded as NEEDS-JOSEPH 3 rather than settled here.
- `code.software-project` — an app-store or game-jam submission packet is submission-shaped, but its members are a binary, screenshots and a privacy declaration, and it belongs to that project's release record. `code` was in `must_consider_neighbors`; this is the honest answer, and no edge is authored on it.
- `personal_admin`, `business_operations` — a tender or RFP response is business_operations' proposal world, not a creative offer; no same-evidence overlap with these fixtures.

## The collision fixture

Two, because the row has two independent ways of being wrong.

**`Portfolio_2026.pdf`** — twenty pages of finished exported work with a contents page and a contact page. It looks exactly like this row's evidence and it is `career.portfolio-work-samples`' material by default. What discriminates it: **standing versus instance**. The portfolio exists, is maintained, and is re-exported whether or not anyone is being written to; it has no addressee, no date sent and no reply. Enclosure in one addressed act does not move it, and this row may record it as a member without attaching a market fact to it.

**`Cover letter - Senior Designer - Studio Kettle.docx`** — the harder one, because it is byte-shaped *identically* to the anchor fixture: addressee block, salutation, offer paragraph, enclosure line, and the same two enclosures. What discriminates it is a single readable clause: it offers availability and experience, not an enclosed work. Nothing structural separates them, which is why the node routes this to `needs_llm` and refuses to let filenames decide.

## proposed_fields

**Empty, deliberately.** The row has a real, argued field-shaped hole — the submitted-to role — and mints nothing for it. The reasoning is the schema anchor's own, applied to this row: minting a key on a fieldless schema at the point of maximum temptation is the 574's mistake. `client` is not reused because it is a commissioning role carrying `role_split_with: our_firm`, and recording an agent or a jury as `client` would assert a paid relationship that does not exist. `role_split` is likewise empty: a split needs a key on this side, and there is none. The hole is escalated to R1c as NEEDS-JOSEPH 1 with three alternatives spelled out.

## Recommendations to R1c (this row did not make these changes)

1. `creative.book-manuscript` already carries the reciprocal on `Nightwork_partial_50pp.docx`; no change needed there, and this row matched its wording so the pair reads consistently.
2. `career.portfolio-work-samples`, `career.recruiting`, `creative.deliverable-handoff`, `creative.client-engagement`, `creative.short-form-writing`, `research.manuscript-publication` and `photos.camera-events` will each need the reciprocal half of the edges authored above added on their side. This row wrote none of them.
3. `creative.creative-brief`'s `open_question` proposes routing the **inbound unsolicited enquiry** here. This row declines it: an inbound approach asking the holder to *make* something is the mirror image of this situation, not a member of it — the direction of the offer is the whole discriminator. If a row is minted for it, `career` or `creative.client-engagement` is the better home.

## NEEDS-JOSEPH

**NJ-1 — the addressee has no key, and `client` is the wrong one.** This row's organizing anchor is an organisation in a *submitted-to* role. Alternatives: (a) leave it unkeyed, as here — the row detects, protects and groups but can never branch on the only fact that distinguishes its members, a real functional loss; (b) widen `client` into a general counterparty key with a role value — risks collapsing the very distinction 00 requires be modelled as distinct facets; (c) mint a third counterparty key beside `client` and `our_firm`, reusable by `career.recruiting`'s employer and `research.manuscript-publication`'s venue. This row proposes none and recommends (c) only if the same key can serve all three.

**NJ-2 — the acceptance boundary.** When an offer is accepted the situation ends and another begins (`creative.publishing-title`, `creative.periodical-issue`, `creative.client-engagement`, `creative.exhibition`). Whether the historical packet stays here, migrates, or is retained in both places determines whether a *successful* submission is findable years later. This row cannot decide it alone.

**NJ-3 — artistic open calls versus research funding.** A residency, fellowship or arts-council application is submission-shaped but `research.grants-funding` holds the structurally identical academic case. This row claims the artist's side on the evidence that its enclosures are samples of finished work, a statement and a CV, while a research grant carries a principal investigator, an institutional signature, a budget justification and a programme code. If one row must hold both, widen `research.grants-funding` — the funding world's structure is the more specific.

**NJ-4 — whether the ledger is a creative file at all.** `Submissions tracker.xlsx` is this row's most distinctive artefact and it is a spreadsheet about correspondence, not about a work. An alternative reading files it as personal administration and leaves this row holding only packets. Recorded rather than smoothed, because it is the fixture the whole fan-out argument rests on.

## Self-verification

- `python3 -m json.tool planning/domains/nodes/creative.submission-query.json` → parses.
- Every `00` span in quote marks in both files was checked with `grep -cF` against `planning/00-database-agent-product-design.md` and returned a non-zero count. Nothing is paraphrased inside quote marks.
- Every `file_examples.source_type` is drawn from `SOURCE_TYPES` (`text_document`, `spreadsheet`, `email`, `archive`, `image`).
- Every edge id was confirmed present in `planning/domains/roster.json`; every `falls_through_to` name is one of 00's nine residual homes.
- `fields: []`, `proposed_fields: []`, `dimension_order: []`, `role_split: []`, `time_first: false`.
- No threshold number, no confidence score, no handling class appears anywhere in either file.
- No folder path is written as a fact in any fixture.
- Only the two assigned files were written. `29-DOMAIN-OWNERSHIP.md`, the roster, `canonical_fields.json`, `check.py`, `src/` and every neighbour node are untouched.
