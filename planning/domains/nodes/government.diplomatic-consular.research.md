# Research memo — `government.diplomatic-consular`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.diplomatic-consular.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accepted.** The node survives the charge, but only on one argument, and the argument is narrower than the row's name suggests. What makes a diplomatic mission a filing situation is not that it is a government body doing government things abroad — that would be an industry label. It is that a mission is a public authority of state A standing on the territory of state B, which produces (a) an artifact family whose structural spine is an *origin-post to addressed-capital* pair rather than a subject, (b) a drawer that is purpose-coherent and content-incoherent at the authority level, and (c) a privacy situation the `government` default does not carry, because the named persons in it are inside a foreign jurisdiction.

## The charge — the strongest case that this row should not exist

I put five kill arguments before writing anything. Four of them land partially and I have conceded ground to each.

**1. It is an organisation name.** "Embassy of X", "Consulate General", "Ministry of Foreign Affairs", a coat of arms, a bilingual letterhead — this is never-alone evidence by the schema anchor's own rule ("a government department, regulator, municipality, legislature, court, public school, archive, museum, or official-looking seal alone"). If the row's only discriminator were the name on the letterhead, it could never activate and would be a label.

*Status: conceded and encoded.* Every letterhead, seal, flag-pair, and country-code signal is in `never_alone`. The row does not activate on any of them. It activates on a role structure — an origin-post block plus an addressed capital, or a third-person note addressed to a host-state protocol department, or a case whose counterparty is a host-state detaining authority.

**2. It duplicates `government.public-authority-record`.** A post holds correspondence registers, meeting records, budget, procurement, estate, payroll, registry transfers. That is exactly the generic authority row. Rename the letterhead and nothing changes.

*Status: conceded for the administrative half, defeated for the rest.* I have authored the collision explicitly and named `Post registry transfer 2026 - retired consular files.zip` as the fixture that both rows want. But the note verbale is not a generic authority artifact and no domestic authority produces one: an outgoing note number, a third-person "presents its compliments" construction, a mission seal in place of a signature, and a quoted reciprocal incoming note number is a form that only exists between a mission and a host ministry. Nor does any domestic body produce a reporting despatch whose header is a *from-post / to-desk* pair with a distribution list — that artifact's organizing structure is a jurisdictional crossing, not a topic.

**3. Consular assistance is `government.constituent-casework` with the citizen in a different country.** Same case reference, same named person, same chase correspondence, same protected posture. "Abroad" is a value of a location field, not a node.

*Status: this is the hardest one, and I nearly refused on it.* What defeats it is that the counterparty changes kind, not value. In domestic constituent casework the office and the person sit under the same authority, and the office's leverage is administrative. In a consular protection case the counterparty is a *foreign* authority over which the post has no jurisdiction whatsoever, so the file's spine is notification, access, and welfare observation rather than resolution — and the case cannot be joined to any domestic administrative record. That produces a genuinely different recognition rule and a genuinely different privacy rule. It is close enough that I authored the collision reciprocally with a shared fixture rather than pretending the seam is clean.

**4. Visa and passport work is `identity.immigration-visa` inverted, i.e. a role split, not a node.** True of the artifact, and the roster does hold both sides.

*Status: conceded as a collision, and this is my largest live doubt.* I have claimed the issuing side here on the extraterritorial-post argument, but the honest alternative is that visa adjudication is simply `government.permit-licensing` (an authority deciding an application) with the post as venue. That alternative would leave this row holding reporting, protocol, instruments, protection, and post administration — still a node, but a smaller one. It is NJ-2 below because I cannot settle it from the design docs.

**5. "Diplomatic" is a work_type value on the `government` schema.** The anchor already lists "intergovernmental agreement, programme design, implementation, monitoring, evaluation, or public-accountability report" as a work_types value, which reads as international work.

*Status: defeated.* That value covers development-programme administration and I have ceded it to `government.international-development` by edge. A work_type is a value carried by one document. What this row recognizes is not one document type but a *drawer* whose members are content-incoherent — a reporting despatch, an accreditation register, a birth-abroad act, a guard-force lease, and a fee reconciliation cohere because one post produced them, not because they share a subject. `00` makes exactly that shape first class in a different setting: "The documents are content-incoherent but purpose-coherent." A value cannot express that; a template can.

**Verdict:** accept, with three edges conceded and one open question (NJ-2) that could shrink the row later.

## The node test, argued in three legs

The `government` schema's **default template** is what I am measured against. Read from `planning/domains/nodes/government.json`: `dimension_order: []` with the prose recommendation "authority-side function or bounded proceeding/case/programme first, then an exact reference or cycle, then work type; named people must not become the organizing dimension"; `time_first: false`; `sensitivity: potentially_sensitive`; and an activation rule that an "evidenced public body acts as legislature, regulator, decision-maker, programme administrator, records holder, statistical authority, election administrator, or citizen-casework office".

**Leg 1 — detection signals differ.** The schema default's twelve deterministic signals are all single-authority-internal: bill identifiers, agenda packs, rulemaking dockets, permit case files, FOI schedules, census manuals, count reconciliations. Not one of them requires a second state. Every signal I wrote requires a *pair*: origin post and addressed capital; mission and host-state ministry; national and host-state authority; sending-state instrument and counterpart delegation. This is not a longer list of the same kind; it is a different arity. The schema default cannot recognize a note verbale, because "presents its compliments" plus an outgoing note number plus a seal-not-signature is only meaningful when there are two states.

**Leg 2 — recommended dimensions differ.** Both orders are empty under PR-6, so the difference has to be argued in the prose that will become the order if PR-6 lifts. The default's first dimension is *function* ("authority-side function or bounded proceeding/case/programme first"). Mine cannot be, and that is the whole point of the row: a post drawer spans permit-licensing, casework, registry, and procurement functions at once, so function-first would shatter one mission across the tree. My recommended first dimension is the **post** — a sending-state authority at a named host-state location — with function second. That is a genuine reversal against the default, not a refinement of it. It also inherits the default's hard prohibition (a named person must never be an organizing dimension) and sharpens it: a *country* branch is also unsafe here, because "Consular / Country X" as a visible label can disclose that a national has a protection case in that country.

**Leg 3 — privacy rules differ.** Same `potentially_sensitive` value, materially different rule. The default's rationale is domestic: casework, submissions, unsuccessful bids, restricted statistics, ballots. Three rules are specific to this row. (i) The persons named are outside the sending state's jurisdiction, so the product cannot reason about what disclosure would cost them and must abstain harder. (ii) Handling captions and distribution markings — "Confidential", "Restricted", "For Official Use Only", a named distribution list — appear on these files far more densely than on domestic authority files, and they look exactly like a ready-made sensitivity taxonomy. The rule is that they are literal observations and must never be promoted into handling classes, which are P7's. (iii) Warden networks and locally engaged staff records mix private home addresses with an authority record in a way the domestic default does not anticipate; `00` already requires that contact formats "should normally be privacy-protected rather than used to create folder proposals", and here that is load-bearing rather than incidental.

Three legs, three real differences. The row is a template, not a relabelled default.

## Evidence base

Named artifact forms carrying this row, each a real document type rather than a shape I invented: the **note verbale**; the **reporting despatch or telegram**; the **demarche instruction and delivery report** pair; the **diplomatic list / accreditation register**; the **consular protection case** with detention notification and visit log; the **consular report of birth, marriage, or death abroad**; the **notarial and legalisation act book** and **apostille register**; the **emergency travel document issuance register**; the **visa adjudication and refusal-reasons record**; the **warden network** and evacuation-phase plan; the **exchange of letters**, **full powers**, and **depositary notification**; the **diplomatic bag / courier record**; the **post registry transfer schedule**. Twenty fixtures in the JSON instantiate these with their labelled slots, split into observations and prohibited conclusions.

Claims not traceable to a design quotation or a named document form are marked as inference. The strongest inference is Leg 1's arity argument — that the second state is what makes the signal set different — which follows from the artifact forms, not from a design statement.

Every quotation in the JSON was grep-verified verbatim against `planning/00-database-agent-product-design.md` (13 spans, each matching exactly once). No other span is inside quote marks in either file.

## Files considered and rejected

These are the tempting false positives. Each was considered as evidence for this row and rejected with a reason.

- **`Country Human Rights Report 2026 - published.pdf`** — a foreign ministry published it, it is entirely about a host state, and it is written in the exact register of post reporting. Rejected: publication is not custody. It has no addressee, no origin-post block, no distribution list, and no reference number. → Reading Inbox.
- **`My Schengen visa - approved 2026.jpg`** — bears a consulate name, a machine-readable zone, and official security printing. Rejected: it is the holder's finished document with no issuing register, act number, officer marker, or reasoning. → `identity.immigration-visa`, else Protected Records. **This is the collision fixture** (below).
- **`UN side event - NGO delegation briefing and lobbying plan.pdf`** — session references, delegation lists, demarche-shaped asks. Rejected: the producer block names a charity. Diplomatic vocabulary is the most reusable vocabulary in the corpus.
- **`Trade mission to host market - participant pack and matchmaking schedule.pdf`** — carries an embassy commercial-section contact block. Rejected: a contact block is a counterparty, not a producer. The participating company holds this copy.
- **Consular appointment confirmations, fee receipts, and portal booking emails held by an applicant.** Rejected: transactional documents on the customer side of a counter. → Receipts and Confirmations.
- **A resume, contract, payslip, or LinkedIn export naming a foreign ministry as employer.** Rejected: diplomatic service as an employer or an industry is not this row. This is the schema anchor's own rule and it applies here unchanged.
- **Academic international-relations papers, treaty casebooks, and model-UN packs.** Rejected: research and reading material. They reproduce the register and none of the roles.
- **News coverage of an embassy, ambassadorial interviews, and press releases.** Rejected: about the post, not of the post.
- **A live consular case-management system, a mission mail account, or a registry database.** Rejected as not-one-file. Only a bounded export with a readable manifest is represented; live ingestion is a later connector and security decision.
- **`consular_case_system_export.dat`** — filename is the only evidence. Rejected as activation evidence and retained only as a fixture proving the filename cannot manufacture a post, a case, or a sensitivity result. → Unsupported or Encrypted.
- **Travel photographs, host-country maps, and language-learning material found in the same folder as post files.** Rejected: folder co-location is not evidence, and a shared download session "should never be treated as proof of topic".

## The collision fixture

`My Schengen visa - approved 2026.jpg` against `Visa refusal - decision and reasons - case NIV-88213.pdf`.

These are the same transaction photographed from opposite sides of one counter, and the naive signals are identical: a consulate name, a country pair, official printing, a person's name, immigration vocabulary. **What discriminates is issuing-side structure, and nothing else.** The post-side file carries a case number in a post's own series, an adjudicating-officer marker, an interview date, findings written against named provisions, and a review instruction — the apparatus of *making* a decision. The holder-side file carries a finished decision and nothing about how it was reached. A register row, an act number, an officer marker, or a fee-taken slot is the discriminator; the consulate's name is worthless. If a file shows only the finished document, this row must not fire even when the consulate is named twice on the page.

## Reciprocal boundaries

Seven collisions are authored, each stating the boundary in both directions and naming the same fixture on both sides. Summarised:

| Neighbour | Shared fixture | This row takes it when | Neighbour takes it when |
|---|---|---|---|
| `government.public-authority-record` | post registry transfer zip | the post/sending-state/host-state triangle is in the evidence | a body name and internal governance shape, no triangle |
| `government.constituent-casework` | consular protection case docx | national is extraterritorial, counterparty is a host-state authority | office and person share one jurisdiction |
| `identity.immigration-visa` | the visa (both fixtures above) | issuing-side structure present | finished document held by the person named on it |
| `government.international-development` | bilateral MOU + exchange of letters | representation and instrument side | evidenced portfolio, grant, or implementing-partner structure |
| `government.archives-recordkeeping` | post registry transfer zip | transferring post's schedule, up to transfer | accession, arrangement, description, or access review |
| `nonprofit.advocacy-campaign` | UN side-event briefing | evidenced public authority as producer or addressee | producer block evidences a civil-society organisation |
| `business_operations.go-to-market` | trade-mission participant pack | post-side reference, approval, or reporting slot | a company's own copy |

Note that `government.public-authority-record` and `government.archives-recordkeeping` compete over the *same bytes* — the transfer zip — from different directions, which is why both edges name it. That is a recommendation to R1c to check the three-way seam rather than a claim that I have resolved it.

## Neighbours considered that got no edge

- **`legal.personal-legal-matters` / `legal.practice-matter-file`** — a detained national has a legal matter, and the post's file references local lawyers. No edge: the post's protection file is not a representation, and the landed `legal.practice-matter-file` row already turns on practitioner-side representation evidence, which a consular officer does not have. The two rows do not want the same bytes.
- **`travel.bookings-confirmations`** — visas, passports, and consular appointments cluster with travel material. No edge: the row that actually competes for a visa is `identity.immigration-visa`, and adding a second claim would blur a boundary that is already sharp.
- **`government.emergency-management`** — evacuation planning and incident logs overlap. No edge at gist depth: domestic emergency management and consular evacuation share vocabulary but not counterparties. If landed sibling research finds a true same-evidence mutex over an evacuation-phase document, R1c can add it.
- **`government.public-procurement`** — a post buys guard services and leases property. No edge: mission procurement is procurement, and claiming it here would be exactly the overreach the charge warned about. The generic collisions already cover the administrative half.
- **`identity.core-documents`** — a passport inside a post's issuance file. Not a mutex; the same coactivation shape the landed legal row recorded, and it is expressed as a fixture-level `also_schema` note rather than an edge.
- **`nonprofit.political-campaign`, `career.employment-records`, `business_operations.contract-administration`** — each touches the post drawer at one point and none competes for the whole. Recorded here rather than as edges.

`also_holds_with` is empty and `role_split` is empty. Both are schema-level constructs and the `government` schema declares no fields, so a template cannot author coactivation or split roles by field key. This follows the landed `legal.practice-matter-file` precedent, which left both empty "for the same fieldless reason". The coactivation cases that do exist (career for locally engaged staff payroll, finance for fee reconciliation, photos for the portal screenshot) are recorded as `also_schema` on the individual fixtures instead.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`. All four are deliberate and required: PR-6 leaves `government` fieldless, D1's deferral stands, and the row is `launch: placeholder`.

Candidates considered and **not** proposed, with the reason each fails:

- `post`, `mission`, `sending_state`, `host_state`, `accreditation_status` — the concepts the row actually needs. Not minted, because minting them here would put the row's structural spine into canonical fields ahead of the central adjudication PR-6 defers. They are raised in NJ-1 instead.
- `case_id` / `act_number` — attractive because they are the real grouping anchors, but a canonical case key would immediately be claimed by casework, permit-licensing, FOI, and legal alike. This belongs to R1c or to a central pass, not to one template.
- `country` — the single most tempting key, and the most dangerous. A country branch here can disclose where a national is detained. Rejected on privacy grounds independently of PR-6.
- `institution`, `record_type` (Finance-scoped), `purpose` (College Applications-scoped), `work_type` (Academic) — existing canonical keys that the `government` schema does not reference. Reusing a key across a schema that has not declared it is not available to a template.

`time_first` is false for the reason `00` gives directly: "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." A post's reporting thread, note exchange, and protection case each span calendar boundaries, and a year-first tree would separate a detention notification from the visit log that follows it.

## Recognition boundary in one paragraph

Strong evidence is always a **pair of roles plus a workflow**. Weak evidence stays weak in any combination when the second role is missing: letterheads, seals, flags, country names, handling captions, diplomatic vocabulary, folder names, download sessions, and the extension all fail alone, and they fail together. Where the holder role cannot be separated locally — post, capital desk, NGO delegation, participating company, applicant, or reader — the outcome is Review Later, not a guess.

## NEEDS-JOSEPH

- **NJ-1 — Can the post triangle ever be represented?** If PR-6 lifts, decide centrally whether a post or mission identifier, a sending-state role, and a host-state role may exist as `government` fields, and whether *any* of them may be destination-eligible. Alternatives: (a) keep all three as prose forever and let the row group only by exact reference; (b) allow a post identifier as a search-only field, never a dimension; (c) allow a post identifier as the first dimension with a redacted display label. My recommendation is (b) or (c), never a country-named branch, because a country label can itself disclose a protection case. This row proposes nothing.
- **NJ-2 — Who owns post-side issuance and adjudication?** Visa adjudication, passport and emergency-travel-document issuance, notarial and legalisation acts, and civil registration abroad are claimed by this row on the extraterritorial-post argument. The alternative is a function-first split sending them to `government.permit-licensing` as the general decision-making row, leaving this row with reporting, protocol, instruments, protection, and post administration. Alternative (a) preserves the purpose-coherent post drawer that justifies the node; alternative (b) is cleaner and makes both rows smaller. I could not settle it from the design docs and the row is written as (a). This is a recommendation to R1c to adjudicate reciprocally with `government.permit-licensing`, which has not yet argued back.
- **NJ-3 — Handling captions.** These files carry caption strings that look exactly like a sensitivity vocabulary. Decide whether they may be retained as literal source observations for local review, or must be dropped at extraction so they can never be mistaken for handling classes. This phase records only `potentially_sensitive` and P7 owns handling classes; the risk is that a caption survives as a string and is later read as policy.
- **NJ-4 — The three-way registry-transfer seam.** `government.public-authority-record`, `government.archives-recordkeeping`, and this row all name the same transfer manifest. R1c should confirm the accession line resolves it, or introduce a tiebreak.

## Final recommendation

Keep `government.diplomatic-consular` as a placeholder template with no fields, no dimensions, no coactivation edge, and no time-first hierarchy. Activate only on a two-role structure, never on a mission's name or on a document the mission issued to someone else. Keep the post — not the function, not the country, and never a person — as the recommended first dimension if PR-6 ever lifts, and route everything unresolved to Protected Records or Review Later rather than guessing which side of the counter a file came from.
