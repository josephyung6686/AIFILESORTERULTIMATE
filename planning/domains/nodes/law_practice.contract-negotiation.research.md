# Research memo — `law_practice.contract-negotiation`

Depth: J-DEPTH
Date: 2026-08-27
Kind: template on the fieldless `law_practice` schema · `parent_id: null` · `launch: placeholder`
Output: `planning/domains/nodes/law_practice.contract-negotiation.json`
Team: OTHER-TEAM · Assignment neighbours: `legal`, `career`, `finance` · Residuals: Protected Records, Review Later

## Result

**Accept, narrowly.** The row survives as the **instrument-level** record of getting one contract agreed: document-comparison / blackline headers that name two source versions, clause-keyed issues lists with side-owned positions, playbooks whose columns encode preferred / fallback / walkaway, deviation-approval matrices, and turn / circulation logs. It **cedes** the deal-level spine to `law_practice.transactional-deal`, blank firm forms to `law_practice.precedent-bank`, the completion event to `law_practice.closing-binder`, dispute-ending offers to `law_practice.settlement`, live post-execution registers to `business_operations.contract-administration`, and every executed instrument to `legal`.

I expected to refuse. The charge below is strong. It survives on one structural fact that is not a document-type word and is not the schema default: a **clause-referenced negotiation apparatus over one named instrument whose parties are already filled and whose execution block is still open**.

## The charge, at its strongest, before any research

1. **It is a `work_type` value.** The schema already carries *"transaction document set…"* and *"settlement, mediation and negotiated-outcome record"*. Draft, redline, issues list and playbook look like values at the schema's own document-function level.
2. **It is a lifecycle stage.** First markup → turns → clean → signature pages. That is the middle of a matter, which the schema's prose already places after the matter anchor.
3. **It is a document-type cluster.** Redline, blackline, playbook, issues list — delete every entity name and every document-type word and ask what structure survives. If nothing does, the row fails the family's own deletion test.
4. **It duplicates `law_practice.transactional-deal`.** That landed sibling already lists *"unexecuted transaction instrument under negotiation, with issues list"* among its work types and groups by *"ONE ISSUE THREAD…"*. Closing-binder's prose even attributed drafts and issues lists to the deal row.
5. **It duplicates the schema default.** Matter reference + practitioner/client role pair already activates `law_practice`. A negotiation pack is just matter work product.
6. **It is never-alone evidence.** Version tokens, tracked-changes metadata, firm names and entity pairs are all struck tokens on the schema.

Charge 6 fails on inspection once a real column set is named (below). Charges 1–5 needed the node test argued in full.

## Binding material read

Stamped dispatch via `make_prompt.py law_practice.contract-negotiation`. Authority stack: `00`, ALIGNMENT, CONNECTION (+ examples), `_CONTRACT`, DECISION-BRIEF (D1–D6, J-IND), RESEARCH-BRIEF, roster row, `canonical_fields.json`, SOURCE_TYPES vocabulary. Schema anchor read as JSON only: `law_practice.json`. Depth calibration: `legal.practice-matter-file.research.md`. Sibling seam already authored in `law_practice.transactional-deal.json` (collides_with this id; NJ-TD-2). Also checked: `law_practice.precedent-bank.json`, `law_practice.closing-binder.json`, refused idiom in `law_practice.pleadings.json` / `law_practice.engagement-terms.json`.

Controlling constraints:

- D1 / PR-6: `fields: []`, `proposed_fields: []`, empty `dimension_order`.
- J-DEPTH: evidence, full node test, rejected files, reciprocal boundaries, collision fixture, open questions — not gist.
- `also_holds_with` is **schema ↔ schema only** (handoff §7). Template coactivation is recorded as collisions or as `also_schema` on fixtures, never as `also_holds_with`.
- Quotations from `00` are verbatim and grep-verified before write.

## External artifact shapes (existence only)

Used only to confirm that the proposed structures occur in real practice; no legal rule is imported.

- Document-comparison / blackline workflows in commercial drafting (Word comparison headers naming two source versions; clean vs redline pairs circulated between counsel).
- Negotiation issues lists keyed to clause numbers with open/closed status and owner side — ordinary M&A and commercial-contracts practice tooling.
- Contract playbooks with preferred / fallback / walkaway (or approve-if) columns — in-house and firm know-how used during live negotiation, distinct from blank precedents.
- Deviation-approval matrices recording which playbook breaches need GC or business-owner sign-off.
- Turn / circulation logs joining successive marked-up drafts across firm boundaries.

These establish artifact existence and role seams. The node derives no retention period, authority, privilege status, or enforceability conclusion from them.

## Node-test analysis (three legs)

### Leg 1 — detection signals differ from the schema default

The schema default requires (i) an exact matter / file / engagement reference repeated across artefacts and (ii) at least one artefact whose labelled slots separate a practitioner/firm role from a client role. That pair activates the **family**. It does not describe what makes *this* organisational situation distinct.

This row's signals are a different structure:

- comparison / blackline header naming **two source versions of one instrument**;
- issues-list **column set**: clause × our position × their position × status × owner side;
- playbook **position grammar**: preferred / fallback / walkaway against clause topics;
- deviation-approval columns;
- turn log with from-side / to-side / version.

Strike every entity name and every document-type word from `SPA Issues List - Project Hartley - turn 7.xlsx` and a clause column, two position columns, a status column and an owner-side column are still standing. That is not the schema's intake form, time export, privilege log, or blank precedent.

### Leg 2 — recommended dimensions differ (as prose; serialised order stays empty)

By contract `dimension_order` is `[]` — no declared fields. The **prose recommendation** still differs from the schema's client → matter → function → period paragraph: here the first organising token is the **instrument stem**, then the **issue / clause thread**, then version / turn. An issues-list row is unintelligible without its instrument — the same intelligibility rule `00` states for homework after course: "A work type such as Homework 3 is meaningful only after the course is known". Instrument stems that embed party names remain destination-ineligible (disclosure). Not time-first: "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Leg 3 — privacy rules differ in kind, not only degree

The schema's privacy claim is third-party exposure (client, witness, deponent). This row adds **strategy exposure before execution**: walkaway lines, approved deviations, and side-owned concessions harm a client if leaked even when no witness list exists. Existence is disclosive — a counterparty-named SPA folder announces a live negotiation. Posture stays `potentially_sensitive` only (no handling class). "The default posture must therefore be local-first and data-minimizing."

## Defeat of the charge

1. **Work_type / document-type.** Values name members; they do not name the clause-referenced apparatus. The schema's own NJ-LP-3 logic cuts both ways: a row justified *only* by document kind fails; a row justified by a structure the default does not describe can stand. This is the latter.
2. **Lifecycle.** Draft→clean→executed is real, but the **executed** end-state is `legal`'s, the **blank** start-state is precedent-bank's, and the **middle** has its own labelled slots. Lifecycle alone would refuse the row; lifecycle plus distinct apparatus does not.
3. **Deal duplication.** `transactional-deal` already authored the seam with the shared fixture `Project Hartley - SPA - v12 (blackline vs v11 SC markup).docx` and ceded it here. Closing-binder's broader attribution of issues lists to the deal row is inconsistent with that seam; this memo aligns with the deal row's own collides_with entry, not with closing-binder's looser prose. Bilateral MSA/NDA packs **without** a codename-plus-N-sided working group are exactly the coverage the deal spine cannot see — see the archive fixture.
4. **Schema default.** Matter+role activates the schema; it does not recommend instrument-then-clause organisation or strategy-posture protection for playbooks.

## Bottom-up file set (accepted fixtures summarised)

Full observation / fact splits live in the JSON. The memo records why each exists.

1. Blackline SPA v12 vs v11 — centre positive fixture; open execution; matter footer.
2. Issues list turn 7 — clause × positions × status × owner side.
3. Vendor MSA playbook — standing position grammar; not a blank precedent.
4. Deviation-approval matrix — governance over playbook breaches.
5. Markup email — instrument stem + side-crossing + redline attachment.
6. Bilateral negotiation pack zip — coverage without deal spine.
7. Executed SPA — collision into `legal` (safety first).
8. Firm-standard SPA precedent — collision into precedent-bank.
9. Working group list — collision into transactional-deal.
10. Completion agenda v14 — collision into closing-binder (when delivery status populated).
11. Consulting SOW redline — collision into career consulting.
12. Part 36 offer — collision into settlement / legal, not commercial formation.
13. Contract register — collision into business_operations.contract-administration.
14. Personal signed NDA — under-firing collision into personal legal matters.
15. DocuSign screenshot — photos co-read; residual Temporary Screenshots if no neighbourhood.
16. LPC sample markup — training false friend; purpose test.
17. Password-protected pack — Unsupported or Encrypted; no purpose from filename.

## Files considered and rejected

- Live DMS / contract-lifecycle databases — source systems, not file nodes; only bounded exports with readable manifests are in scope.
- Pure email threads with no instrument stem and no apparatus attachment — never-alone subject lines.
- Public form agreements and regulator specimens — Reading Inbox unless firm playbook apparatus is present.
- Pricing schedules alone — finance's on finance's structure; may also_hold when packed with negotiation members.
- Settlement term sheets ending litigation — settlement sibling, even when they contain tracked changes.
- Employment offer letters the holder received as candidate — career / personal, absent practitioner apparatus produced by the holder.

## Edges (reciprocal boundaries)

| Neighbour | This row owns | Neighbour owns | Shared fixture |
|---|---|---|---|
| `law_practice.transactional-deal` | One instrument's redline life | Deal-level spine (WGL, CP, disclosure, insider) | `Project Hartley - SPA - v12 (blackline vs v11 SC markup).docx` |
| `law_practice.precedent-bank` | Filled parties + open execution + apparatus | Blank parties/execution + drafting notes | `PRECEDENT - Share purchase agreement (firm standard) v7.docx` |
| `law_practice.closing-binder` | Pre-execution negotiation apparatus | Completion delivery-status matrix | `Completion Agenda - Project Hartley - v14 (clean).docx` |
| `law_practice.settlement` | Commercial formation playbooks / issues lists | Dispute-ending offers / settlement instruments | `Without prejudice - Part 36 offer - Hartley claim.pdf` |
| `legal` | Unexecuted negotiated drafts | Executed bound instruments (safety first) | `Share Purchase Agreement - Hartley v Nash - EXECUTED.pdf` |
| `legal.personal-legal-matters` | Holder-as-counsel apparatus | Holder-as-party personal contracts | `NDA - my startup and BigCo - signed scan.pdf` |
| `career.consulting-client-engagement` | Counsel / legal playbook / legal issues list | Consulting SOW markup | `Acme Market Entry - Statement of Work - redline v3.docx` |
| `business_operations.contract-administration` | Unexecuted bargaining positions | Live executed-contract register | `Contract register - renewals and notice dates - 2026.xlsx` |
| `finance` | Pack membership via instrument stem | Issuer/account or consideration structure | draft consideration annex in a pack |

`also_holds_with` (schemas only): `legal`, `finance`, `business_operations`. No template ids.

Deliberate non-edges: `law_practice.due-diligence` (inward findings vs outward bargaining — direction differs; no same-fixture mutex authored without that sibling's text); `photos` / `academic` coactivation only via fixtures; Code not activated by `.docx` comparison tool formats.

## Fields and proposals

`fields: []`, `proposed_fields: []`. The schema already proposes `client`, `our_firm`, `project`, `work_type`, `subject_of_record`, `fiscal_period` for R1c. This template mints nothing. Rejected local mints: `instrument`, `clause`, `negotiation_turn`, `playbook_rule` — all values or grouping anchors, not licensed fields.

## Residual routing

Protected Records first for stray blacklines, issues lists and playbooks. Review Later when side or legal-vs-consulting is unresolved ("Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement."). Unsupported or Encrypted for locked packs. Reading Inbox for published models. Independent Records for orphan clean drafts. Temporary Screenshots for portal captures without a neighbourhood.

## NEEDS-JOSEPH

1. **NJ-CN-1 — The deal fold.** Keep both deal-spine and instrument-negotiation; fold this into transactional-deal (losing bilateral MSA coverage); or fold transactional-deal into this (losing pseudonymous multi-firm anchor). Prefer keep-both; prefer refusal over a split R1c rejects.
2. **NJ-CN-2 — Standing playbook home.** Position grammar here vs matter-free know-how in precedent-bank vs refuse playbooks as a document type. Prefer here on position grammar.
3. **NJ-CN-3 — Instrument-named branches.** If PR-6 lifts, can a party-free instrument short name be destination-eligible? Same disclosure problem as client/matter labels.

## Final recommendation

Keep `law_practice.contract-negotiation` as a placeholder template with no fields, no serialised dimensions, and `potentially_sensitive` posture. Recognise by clause-referenced negotiation apparatus over one filled-party, still-unexecuted instrument. Align the deal seam with the fixture transactional-deal already named. Route executed bytes to `legal` first. Do not invent fields to save the id.
