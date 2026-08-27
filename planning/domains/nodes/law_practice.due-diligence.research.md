# Research memo — `law_practice.due-diligence`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.due-diligence.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`
Team: OTHER-TEAM · single id assignment

## Result

**Accepted, narrowly.** The row does not stand on the deal lifecycle stage called diligence, on the words due diligence / DD / data room, on a numbered demand list alone, or on a deal codename. It stands on the **examination apparatus**: buyer/lender-side request list with corporate-function categories and an in-data-room status vocabulary; virtual-data-room index whose columns are access and Q-and-A; Q-and-A tracker keyed to tabs; chaptered findings / red-flag report; specialist chapter reports that feed it; VDR access log. Everything ordinary speech also calls “disclosure” that flows the other way (seller warranty letter) or uses litigation grammar (discovery) or completion grammar (closing binder) is ceded by name.

## The charge — strongest case this row should NOT exist

Five arguments before writing anything. Four are serious.

**1. Diligence is a LIFECYCLE STAGE of `law_practice.transactional-deal`.** Strongest attack, and the brief names the category. Instruction → diligence → drafts → conditions → signing → completion is one arc. The schema anchor’s own `work_types` enum bundles *“transaction document set, due-diligence report, data-room index and completion or closing record”* into a single value. Read strictly, that value names this row, transactional-deal and closing-binder at once. A stage is not a node.

**2. It is a document-type list.** “Request list”, “data-room index”, “red-flag report”, “management questionnaire” are form-book titles. The schema strikes a document-type word — even beside a firm or client name — as never-alone. A row assembled from titles is a table of contents.

**3. It duplicates the schema default.** The schema’s sixth deterministic signal is already “A DISCLOSURE-REVIEW structure: a review or coding log… or a PRIVILEGE LOG…”. If examination is just review-coding under another name, the node test fails.

**4. It collides with `law_practice.discovery` on the same bytes.** Both own a consecutively numbered demand for another party’s documents with a per-item status column. Discovery already named the diligence request list as its existential false friend. If the discriminator is only vocabulary, one of the two rows is padding.

**5. Organisation / role shaped.** Weaker. The row does not depend on a law-firm name or a practising certificate, so the schema’s existential strike does not land.

### Why the charge is defeated (and how far)

Attack 1 is defeated by **conceding the lifecycle and keeping only the apparatus**. This row cedes the deal spine (working group list, CP tracker, disclosure letter, insider list) to `law_practice.transactional-deal`, the completion event to `law_practice.closing-binder`, and executed instruments to `legal`. What remains is not “files that exist during diligence months.” It is a set of **column grammars and a chapter grammar** testable on bytes, and three landed siblings already wrote edges assuming this id exists.

Attack 2 is defeated because the signals are not the titles. D1 does not fire on the filename “Due diligence request list”; it fires on buyer/seller roles + corporate-function categories + provided/outstanding/in-data-room status. The words are struck by name in `never_alone`, including the row’s own name.

Attack 3 is defeated by evidence the schema itself supplies. The schema’s disclosure-review signal is the litigation review-coding / privilege-log shape. It has **no** signal for a deal-side request list with corporate-function categories, **no** signal for an inspection index with access/Q-and-A columns, **no** signal for a Q-and-A tracker keyed to VDR tabs, **no** signal for a chaptered findings report, and **no** signal for a VDR access log. This row’s precondition also adds a buyer/seller (or lender/borrower) leg the default does not state.

Attack 4 is defeated on structure the discovery row already published: propounding/responding litigants + definitions-and-instructions + reproduce-then-answer (or certificate of service) versus buyer/seller + corporate-function categories + in-data-room status + data-room index (not a load file). Same fixture named both ways.

**Honest residue.** If R1c reads the schema `work_types` enum as binding, or judges examination a lifecycle stage of transactional-deal, the correct outcome is **refusal** (NJ-DD-1 / NJ-DD-2). I would rather this row be refused than kept to save an id.

## Node test — all three legs

**Leg 1 — detection signals differ from the schema default.** Yes. Eight signals authored. D1 (deal-side request list), D2 (inspection index), D3 (Q-and-A tracker), D4 (chaptered findings), D5 (specialist chapter report), D6 (answered management/vendor questionnaire), D7 (VDR access log) have no counterpart among the schema’s twelve. D8 re-anchors the schema’s email/calendar signal on a request-list item, Q-and-A number or tab reference. Twelve `never_alone` entries; the numbered-demand-list strike is this row’s own existential concession shared with discovery.

**Leg 2 — recommended dimensions differ.** `dimension_order` is `[]` (fieldless schema under PR-6), so the difference is in prose. Schema prose: client → matter → function → period. This row’s prose: **deal / diligence exercise → chapter (corporate function)**; permanently seed **target-name** and **data-room-folder** levels ineligible (MNPI disclosure; meaningless one-child levels; third-party filing tree). Those two exclusions are peculiar to this row.

**Leg 3 — privacy rules differ.** Yes, and on different grounds. Schema claim: matter files hold documents *about* named third parties. This row’s claim: a data room is the **wholesale commercial contents of a going concern** before announcement (MNPI about legal persons), a VDR access log is a **multi-subject surveillance list**, and a folder named for the target publishes that the named company is under examination. Different mechanism, different failure mode.

Verdict: three legs, three differences. `refuse_node: false`.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md`; stamped assignment from `make_prompt.py law_practice.due-diligence`.
- `planning/42-HANDOFF-FINISH-THE-CATALOGUE.md` §6–§7.
- `planning/00-database-agent-product-design.md` — grepped, not streamed. Every span in quote marks below was substring-verified before finalising.
- `planning/domains/nodes/law_practice.json` — schema anchor (signals, work_types, template.why, edges, sensitivity).
- `planning/domains/nodes/legal.practice-matter-file.research.md` — depth calibration.
- Landed siblings already naming this id: `law_practice.discovery`, `law_practice.transactional-deal`, `law_practice.closing-binder` (read for edge reciprocity; not edited).
- `planning/domains/roster.json` — confirmed neighbour ids exist before edge authorship.

External artefact shapes (existence only; no legal rules imported): virtual data room indexes and Q-and-A trackers as ordinary M&A practice artefacts; buyer-side information request lists; chaptered legal due-diligence / red-flag reports; specialist title / IP / tax / employment chapters; VDR user-activity exports. Used only to confirm the structures occur in real practice.

## Files considered and rejected

Tempting false positives — naming them is the research.

- **`Project Hartley - Disclosure Bundle - Index and Tabs 001-140.zip`** — collision fixture with transactional-deal. Seller outward warranty-indexed qualification, not buyer inspection.
- **`Requests for Production - Set One - Acme v Beta.docx`** — collision fixture with discovery. Propounding/responding litigants + definitions block; no corporate-function / in-data-room grammar.
- **`Closing Binder Index - Project Hartley - Tabs 1-47.pdf`** — collision fixture with closing-binder. Execution/delivery columns against a completion date.
- **`Audit PBC list - FY2025 year-end - Acme Holdings.xlsx`** — collision fixture with `business_operations.compliance-audit`. Auditor/auditee + fiscal period; no deal-side roles.
- **`Commercial diligence memo - Target Co growth thesis.pptx`** — consulting commercial diligence without legal apparatus → `career.consulting-client-engagement`.
- **`Report on Title` for a single residential purchase** — `law_practice.conveyancing`; only the multi-parcel portfolio chapter inside a corporate acquisition stays here.
- **A data-room bulk download folder with no index columns** — session membership; 00: *“A session should never be treated as proof of topic”*.
- **A blank firm diligence questionnaire template** — empty slots → schema precedent-bank inverse-recognition / Reading Inbox.
- **Published sample red-flag memo / LPC training index** — purpose, not topic; Reading Inbox.
- **Holder selling their own company** — every diligence token present, holder is the party → `legal.personal-legal-matters`.
- **Password-protected split DD dump** — Unsupported or Encrypted; filename manufactures nothing.
- **VDR platform invoice alone** — Receipts and Confirmations / finance on issuer structure; not the examination apparatus.

## Collision fixture of record

**`Due diligence request list - Project Hartley - v4.xlsx`.**

Shared with `law_practice.discovery`: consecutively numbered demands for another organisation’s documents, per-item status column, professional letterhead. Everything an unsophisticated signal would want is present.

What discriminates toward this row: labelled buyer-side and seller-side counsel blocks; corporate-function category column; status vocabulary *provided / outstanding / in data room / not applicable*; data-room tab column; **absence** of a definitions-and-instructions block and of a reproduce-then-answer counterpart.

What discriminates toward discovery: propounding/responding litigant pair; definitions-and-instructions; reproduce-then-answer (or certificate of service); load file rather than VDR index.

Neither side may claim the fixture from the words request, production, disclosure or index.

## Reciprocal boundaries

| Neighbour | Shared fixture | Toward this row | Toward the neighbour |
|---|---|---|---|
| `law_practice.discovery` | request list xlsx | buyer/seller + corporate-function + in-data-room | propounding/responding + reproduce-then-answer / CoS |
| `law_practice.transactional-deal` | Disclosure Bundle zip | inward findings / inspection index | outward warranty-indexed disclosure letter |
| `law_practice.closing-binder` | enumerated index | access / Q-and-A; inspection tense | signatory / execution / delivery; completion date |
| `law_practice.conveyancing` | Report on Title portfolio | diligence chapter over many parcels in a deal | single registered-parcel conveyance |
| `business_operations.compliance-audit` | Audit PBC list | deal-side roles + VDR tabs | auditor/auditee + fiscal period |
| `career.consulting-client-engagement` | commercial diligence deck | counsel / matter apparatus | consulting prepared-for / milestones |
| `legal.personal-legal-matters` | findings memo for holder’s own sale | practitioner apparatus for a client | holder is the party |
| `legal` | executed SPA beside diligence pack | request list / findings grammar | bound parties + execution block (safety first) |

`also_holds_with` is **schema ↔ schema only**: `legal`, `finance`, `identity`, `medical`, `business_operations`. Template ids are mutex or non-edges, never co-activation edges.

## Neighbours considered without an edge

- `law_practice.contract-negotiation` — redline life of one instrument; no shared fixture that both would claim as primary evidence.
- `law_practice.opinions-advice` / `law_practice.legal-research` — advice and authorities reading; a findings report is examination of a target, not counsel’s opinion structure.
- `government.public-records-foi` — discovery already owns that seam on the exemption-schedule fixture; this row’s false friend is the audit PBC list, not the citizen request.
- `finance` alone as mutex — co-activation on embedded account statements is the honest reading; the issuer/account structure is finance’s, not a collision.
- `photos.screenshot-captures` — co-activation on screen-origin evidence via `also_schema` on the screenshot fixture; not a mutex.
- `construction_property.sale-purchase` — roster-adjacent; parcel-level conveyancing seam already carried via `law_practice.conveyancing`.

## Fields and proposed_fields

`fields: []`, `proposed_fields: []`, `dimension_order: []` — intentional. PR-6 / D1: the schema declares none; a template may not mint a second copy. Candidates this situation might want (`project` for the deal, `client` / `our_firm` for side, `work_type` for chapter function, `subject_of_record` for target employees in an employment chapter) are already proposed on `law_practice.json`. Reuse, do not re-propose. No new keys.

## NEEDS-JOSEPH

1. **NJ-DD-1 — work_type enum fold.** Schema bundles this row with transactional-deal and closing-binder. Keep on three differing legs, or refuse and route.
2. **NJ-DD-2 — disclosure-letter direction seam.** Keep direction split with transactional-deal; fold letter into this row; or fold this row into transactional-deal as a stage.
3. **NJ-DD-3 — lending / investment scope.** Admit lender- and investor-side examination on the same structures, or park under a finance/funds template.
4. **NJ-DD-4 — safety-ordering residue.** Characteristic files (request list, VDR index, findings, access log) do not fire `legal` and still need protect-before-model ordering (schema NJ-LP-6 restated).

## Self-verification

- Wrote only `planning/domains/nodes/law_practice.due-diligence.json` and `.research.md`.
- JSON parses; `fields` empty; `refuse_node: false`.
- Memo carries `Depth: J-DEPTH`.
- Every `collides_with` / `also_holds_with` entry is `{"domain","signal"}` with SAME FIXTURE BOTH SIDES wording; `also_holds_with` is schema↔schema only.
- Edge domain ids confirmed on the roster.
- Quote spans grepped against `00` before shipping (see verification block in the return).
- No shared files touched; no commit.
