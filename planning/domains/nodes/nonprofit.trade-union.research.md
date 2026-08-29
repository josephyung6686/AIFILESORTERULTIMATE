# Research memo — `nonprofit.trade-union`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/nonprofit.trade-union.json`
Roster row: template on the fieldless `nonprofit` schema, `parent_id: null`, `launch: placeholder`
Absorbed legacy id: `civic.trade-union` (ROSTER.md Appendix A)

## Result

**Accepted, narrowly.**

The row owns what a union or staff association does that no other membership body does: representation and casework for a named member against an **employer**, collective bargaining for a bargaining unit, a statutory industrial-action ballot with notice to the employer, and check-off of subscriptions through an employer's payroll.

It does not own a plain membership roll, an AGM, a union constitution, trustee minutes, budgets, LM/AR21 returns, an employer's grievance file, or a downloaded model CBA. Those already have owners.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped assignment from `make_prompt.py nonprofit.trade-union`.
- `planning/00-database-agent-product-design.md` — targeted `grep -F` only. Every quotation below was verified with `grep -c -F` (or an exact Python `in` check for spans containing a curly apostrophe) before it was written; all returned 1.
- `planning/domains/nodes/nonprofit.json` — schema anchor, read in full. Its eleven deterministic structures, default-template prose, never-alone array (which already strikes a union name), and privacy paragraph are what this row is measured against.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — depth calibration (~24 KB landed launch memo).
- Landed neighbour signal text only: `nonprofit.member-association` (already authors a one-way edge into this id), `government.school-district-administration` (already authors a CBA fixture naming this id), `hr.employee-relations` (claims employer-side grievance and lists collective bargaining; opens NJ-ER-1), `nonprofit.political-campaign` / `nonprofit.volunteer-management` (refusal idiom).
- `planning/domains/roster.json` for neighbour ids; `planning/domains/CONNECTION.md` §2 for the node test.

`00` says **nothing** about trade unions, shop stewards, check-off or industrial-action ballots — greps returned empty. Every substantive industry claim is therefore `inference`. `00` is quoted only for residuals, collector levels, dimension order, abstention, archives, privacy, and purpose.

## THE CHARGE — strongest case that this row should NOT exist

Stated at full strength first.

**(a) Organisation type / never-alone.** “Trade union” names a *kind of body*. The schema already strikes “A charity, union, church…” name alone and says tax status and industry labels are not structures. A row whose roster title is the body type is the schema wearing a hat — the same reasoning that refused `nonprofit.political-campaign`.

**(b) Duplicate of `nonprofit.member-association`.** That accepted sibling already owns the roll, subscription run, AGM, proxy and ballot. A union branch has exactly those artefacts. Its landed signal into this id even offers the union row the plain branch roll “whole.” If the roll is enough, this id is a synonym.

**(c) Duplicate of the schema default.** The schema already lists a MEMBERSHIP-REGISTER structure and a BENEFICIARY/SERVICE-USER case structure. Representation casework looks like a case; an industrial-action ballot looks like a members' meeting instrument; dues look like a subscription run. Context terms already include “collective bargaining” and “shop steward.” The template restates defaults.

**(d) Duplicate of `hr.employee-relations`.** That landed row's work types already include “union recognition, collective bargaining, and collective dispute record,” and its served-instrument signal includes the right to be accompanied by a trade union representative. Employer-facing disputes may already be owned.

**(e) Work-type / document-type padding.** Membership, casework, ballot, recognition, LM-2 — values and forms, not a situation. Branch “business” is `business_operations`.

**(f) Padding to save a legacy id.** `civic.trade-union` is in Appendix A. Inventing a filing world to keep it is the 574 failure the handoff forbids.

## Defeating it — node test, three legs

The schema's DEFAULT is: fire on any of eleven non-exchange structures; order by association → non-exchange counterparty or fund → period → document function; forbid naming a beneficiary, donor, member or safeguarded person as a folder level; privacy driven by third parties disclosed under need.

### Leg 1 — detection signals differ

The schema's gate is *what relation is evidenced*. This row adds a second gate the schema never states: an **employer (or employing authority) as counterparty** to the association's act.

That gate produces structures the schema default does not name:

1. **Representation against an employer.** A case reference, a member request for accompaniment, a workplace representative, and an employer as respondent or hearing addressee. This is not the schema's provider→non-paying-beneficiary service case; the third party across the table is an employer in an employment procedure.
2. **Collective-bargaining packet.** Recognition/facilities, pay claim for a bargaining unit, joint minutes with two sides, draft/signed collective agreement, ratification. No schema deterministic bullet describes this.
3. **Statutory industrial-action ballot.** Notice *addressed to the employer*, a question on industrial action, scrutineer return, subsequent action notice. Discriminated from member-association's AGM/officer ballot by employer addressee and question type — not by the word ballot.
4. **Check-off.** Authorisation naming member + association + employer payroll, or an employer remittance schedule payable to the association. Discriminated from hr payroll by *whose wages* are being run.

Charge (c) fails because beneficiary-case and AGM-ballot vocabulary can appear inside these structures without being them. Charge (b) fails once the plain roll is **ceded** to member-association (see NJ-TU-1). Charge (d) fails on holder: hr owns the employer's personnel process; this row owns the association's file for the same dispute. Charge (a)/(f) fail only if the employer-counterparty gate is real and load-bearing — which the fixtures below test.

### Leg 2 — recommended dimensions differ (in prose)

`dimension_order` is empty under PR-6 — same as every nonprofit template. Difference must live in prose, as member-association argued.

Schema default counterparty slots include grant, fund, appeal, case, register. This row's human counterparty is often a named member (forbidden as a folder level) or a thin workplace unit (re-identification risk). The prose recommendation therefore collapses the person level and promotes an **opaque case/ballot/bargaining-unit token**, then period, then function — and keeps association only when the corpus spans more than one body (“use an author or organization merely as a collector” / “create meaningless one-child levels”). That is not the schema's grant/fund/appeal story and not member-association's “membership year into the vacated slot” story.

### Leg 3 — privacy rules differ

Schema posture: protect people disclosed under need. This row's ordinary bytes additionally disclose **affiliation**, **workplace allegations** (often with health/performance detail), and **intended industrial action** before it occurs. A member-named or steward-named path is forbidden for the same local-first reason: “The default posture must therefore be local-first and data-minimizing.” Sensitivity value stays `potentially_sensitive` (only legal value here); the *mechanism* is the difference.

## Bottom-up file set

Full observation/fact splits live in the JSON. Memo roles:

1. `Case CW-2026-0147 - representation request and employer response.pdf` — load-bearing accept fixture; employer respondent + case ref.
2. `Disciplinary hearing brief - J Patel - CW-2026-0147.docx` — union-side work product; must not become legal privilege.
3. `Pay claim 2026 - Local Authority Admin Unit - submitted.pdf` — bargaining claim apparatus.
4. `JNC minutes - 2026-03-12 - claim LA-ADMIN-2026.pdf` — two-sided negotiating minutes vs internal executive minutes.
5. `Collective Agreement - District 12 and Teachers Association 2026-2029.pdf` — reciprocal fixture already named by `government.school-district-administration`; also legal instrument.
6. `Notice of intention to ballot - industrial action - EmployerCo - 2026-04-02.pdf` — employer-addressed ballot notice.
7. `Industrial action ballot paper - EmployerCo Admin Unit - closing 2026-04-30.pdf` — IA question.
8. `Scrutineers return - IA ballot EmployerCo - 2026-05-02.pdf` — turnout figures as observations only (no catalogue thresholds).
9. `Check-off authorisation - M-4471 - signed.pdf` — payroll-mediated subscription.
10. `Employer remittance - union deductions - March 2026.xlsx` — association-side remittance, not own-staff payroll.
11. `Branch case export - CW-2026-0147.zip` — archive manifest; no unpack (“the normal scan should never extract archive contents to the filesystem”).
12. `RE CW-2026-0147 - hearing rearranged.eml` — email tied by case ref, not by domain.
13. `Staff handbook - disciplinary procedure - EmployerCo.pdf` — **collision fixture**: dense union vocabulary, addressed to nobody; hr/policy, not this row.
14. `Branch membership and check-off 2026.xlsx` — seam with member-association; plain standing columns without employer-mediated structure do not fire this row.
15. `Form LM-2 - Labor Organization Annual Report - FY2025.pdf` — rejected for this row; regulatory self-running return.
16. `National model recognition agreement - exemplar.pdf` — reading/exemplar false friend (“purpose answers what the file was for”).

## Files considered and rejected

- Plain `Membership register 2026 - full roll.xlsx` with no employer/payroll column → `nonprofit.member-association`.
- Association AGM notice/proxy/scrutineer return with membership electorate and no employer addressee → member-association.
- Union constitution / rule book → `nonprofit.governance`.
- Trustee/executive minutes, branch budget, office lease → `business_operations`.
- Employer grievance investigation, invitation to disciplinary hearing, appeal outcome on employer letterhead → `hr.employee-relations`.
- Association's own staff payroll (organisers' wages) → `hr` / payroll administration.
- Member's personal bank statement or dues receipt → `finance` / Receipts and Confirmations.
- LM-2 / AR21 / Certification Officer return → `business_operations.corporate-regulatory-filings` (association) or government (authority).
- Downloaded national CBA or ACAS/NLRB guidance PDF → Reading Inbox.
- Campaign leaflet, picket selfie, news article about a strike → creative/advocacy/Reading Inbox; vocabulary never-alone.
- Password-protected case-management export → Unsupported or Encrypted; do not force open.
- Solicitor engagement letter on a tribunal claim → `legal` / `legal.practice-matter-file`; lay accompaniment alone is not that.

## Boundaries (both directions)

| Neighbour | This row owns | Neighbour owns | Shared fixture |
|---|---|---|---|
| `nonprofit.member-association` | Employer-facing union acts; check-off-backed structures | Plain roll, AGM, ordinary subscription life | `Branch membership and check-off 2026.xlsx` |
| `hr.employee-relations` | Association case file for the member | Employer personnel process | `Case CW-2026-0147…` |
| `hr` | Check-off remitted *to* the association | Association's own employee payroll | `Employer remittance - union deductions - March 2026.xlsx` |
| `government.school-district-administration` | CBA with association mandate/ratification context | CBA with district staffing/payroll context | `Collective Agreement - District 12…` |
| `business_operations` | Joint negotiating record with employer opposite | Union self-running minutes/budgets/policies | `JNC minutes…` |
| `business_operations.corporate-regulatory-filings` | Not LM tokens | LM/AR21-style returns | `Form LM-2…` |
| `legal` | Lay representation / bargaining packet | Executed instrument / practitioner matter | CBA + case PDF |
| `finance` | Association-side authorisation/remittance | Personal dues / bank headers | `Check-off authorisation…` |
| `government.elections-administration` | Private bargaining-unit IA ballot | Public electoral administration | `Scrutineers return…` |
| `nonprofit.governance` | Operation under the rules | The rules instrument | rule book vs case file |
| `business_operations.policy-handbook` | Not generally addressed handbooks | Employer procedure docs | `Staff handbook - disciplinary procedure…` |

`also_holds_with` is schema↔schema only: `legal`, `finance`, `hr`, `business_operations`, `government`.

## Fields and proposed_fields

`fields: []`, `proposed_fields: []`, `dimension_order: []` — intentional under PR-6 and the assignment hint. No synonym mint for `union`, `bargaining_unit`, or `case_ref`. If PR-6 lifts, opaque case/ballot/unit tokens are NJ-TU-3, not smuggled in here.

Reuses the schema's existing proposals only by reference (`organization`, etc.); this template does not re-list them.

## Neighbours considered without an edge

- `nonprofit.fundraising-donor` — dues are not gifts; member-association already holds that seam.
- `nonprofit.political-campaign` — refused; conference literature is not a live edge target.
- `nonprofit.advocacy-campaign` — external campaigning without employer-counterparty bargaining/case apparatus.
- `nonprofit.volunteer-management` — refused; rota absence-of-payroll is not this row's discriminator.
- `government` (schema) — covered via school-district + also_holds; no extra bare schema collision beyond LM routing.
- `career` — a steward's own CV mentioning union office is career material, not association records.

## Collision fixture (dispositive)

`Staff handbook - disciplinary procedure - EmployerCo.pdf` contains the right-to-be-accompanied sentence and the full sanction ladder — denser union vocabulary than many real case files — and is still **not** this row. It is addressed to employees generally, creates no case reference, and belongs with employer policy/hr. Vocabulary-only activation dies here.

## NEEDS-JOSEPH

- **NJ-TU-1** — plain branch roll vs `nonprofit.member-association` (this pass cedes plain rolls; that pass claimed them for the union row).
- **NJ-TU-2** — collective bargaining vs `hr.employee-relations` NJ-ER-1 (holder-side split vs move-all-collective).
- **NJ-TU-3** — if PR-6 lifts, destination eligibility of opaque case/ballot/unit keys given re-identification risk.

## Verification (self)

- Wrote only `nonprofit.trade-union.json` and `nonprofit.trade-union.research.md`.
- JSON parses; `fields` and `proposed_fields` are `[]`; `launch: placeholder`; `refuse_node: false`.
- Every `also_holds_with.domain` is a schema id.
- Every `collides_with` / `also_holds_with` entry is a `{domain, signal}` object with SAME FIXTURE BOTH SIDES.
- Quotes attributed to `00` grep-verified before write.
- No threshold numbers as product rules; no handling classes; no commit.
