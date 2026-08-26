# Research memo — `government.elections-administration`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.elections-administration.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`
Absorbed legacy id: `gov.elections-administration` (ROSTER.md line 868, one-to-one ROW carry, no folds)

## Result

**Accept.** `refuse_node: false`. The row survives a serious attempt to kill it, and it survives on two legs, not three. Its detection signals are genuinely different from the government default's — the operative evidence is *arithmetic reconciliation structure that must balance*, not the default's officer-block-plus-case-reference — and its privacy rule is different in kind, not degree: it is a prohibition on **joining two file classes**, which nothing in the government default expresses. Its dimension recommendation also differs in shape (poll event → contest → station → function, with function last), but under PR-6 that difference cannot be serialized, so I do not count it as load-bearing.

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `role_split: []`, `also_holds_with: []` are all deliberate and argued below.

## The charge — the strongest case that this row should not exist

I put five attacks to the row before writing anything. Two are fatal-looking.

**Attack 1 — it is a `work_type` value, and the schema already says so.** This is the strongest attack. `government.json` `work_types` contains, as *one* entry:

> `"election registration operations, nominations, polling logistics, ballot accounting, count reconciliation, declaration, or incident record"`

That is this row's entire lifecycle, already enumerated as an enum value on the parent schema. The dispatch prompt is explicit: "`work_types[]` is an enum of values for a `work_type` (or equivalent) field. Do not ask R1a for a child node per work type." On its face, `government.elections-administration` is a node minted from a comma-separated list item — precisely the 574's failure mode.

**Attack 2 — it is a duplicate of its own schema's default template.** Worse than attack 1: the government anchor already carries an election bullet in `recognition.deterministic` —

> `"an election-administration packet with an administering-office block and operational structures such as nomination receipt, polling-station allocation, ballot-account, count reconciliation, result declaration, or incident log; campaign material and a voter's registration confirmation are not authority-side records"`

— *and* it already carries a fixture named `Election Count Reconciliation - North District.csv`. The default template can already recognize an election packet and already routes one. A template row "exists only when its detection signals, recommended dimensions, or privacy rules differ from its schema's default"; here the default appears to have pre-empted all three.

**Attack 3 — it is an organisation name.** "Electoral Commission", "Board of Elections", "Returning Officer" are never-alone strings. If the row's real content is "files from the elections office", it can never activate.

**Attack 4 — it is a lifecycle stage / an event.** "Election day" is a date. A date is not a filing world.

**Attack 5 — it is a medium.** Ballots are a physical object; the digital residue is spreadsheets and PDFs, i.e. `SOURCE_TYPES`, not a node.

### Defeating the charge

Attacks 3, 4 and 5 fail quickly and are encoded rather than argued: the office name, the poll date, and the ballot vocabulary are all written into `never_alone` as things that cannot fire the row. If those were the row's content, `never_alone` would have consumed the row, and I would have refused.

Attacks 1 and 2 fail on the same finding, which is the substance of this research: **the work-type list and the default's election bullet are the *outputs* of the world, not the *evidence* of it.** The default bullet recognizes an election packet the way it recognizes every other government packet — by an office block plus operational nouns. That test is not what actually discriminates this world. What discriminates it is a document shape that occurs nowhere else in the government schema and nowhere else in the roster:

- A **ballot paper account** is a form whose labelled quantities exist *in order to reconcile*: received = issued + spoilt + tendered + unused + returned, per station, signed. There is no analogous must-balance artifact in rulemaking, planning, FOI, procurement, casework, or statistics. A rulemaking response-to-comments does not have to add up.
- A **marked register** is a whole-electorate roll with per-elector issue marks. It is not case material about a person; it is a census of everyone eligible, annotated with an act.
- A **statement of persons nominated** carries subscriber (proposer/seconder) names as a validity mechanism, not as correspondence.
- A **doubtful-ballot adjudication sheet** records a determination about an anonymous artifact — the only place in the schema where the authority decides something about a thing that must *never* be traceable to the person who made it.

None of those four are work types; they are structural fixtures with observable slot patterns, and the `deterministic` list is written against them rather than against the word "election". That is a real difference in detection signal, and it defeats attack 2's first leg.

Attack 2's remaining legs are defeated by the privacy finding, below, which the default cannot state. Attack 1 is defeated because the row is not "one work type"; it is the world in which eleven work types share a single anchor and a single secrecy constraint. I record the boundary against the default reciprocally rather than pretending the overlap does not exist — see the shared fixture, below.

## The node test, all three legs

**Leg 1 — detection signals differ.** Yes. Argued above. The default asks "is the holder an authority acting in a public function?" This row asks a narrower and answerable question: "does the corpus contain a reconciliation, nomination-receipt, register-issue, adjudication, or declaration structure produced by the office conducting the poll?" It also faces a false-positive population no other government row faces, because *four* different actors keep near-identical bytes: the administering office, the candidate/party, the observer/agent, and the voter. `never_alone` therefore names classes the schema default does not — internal associational elections, opinion polls, a candidate's own nomination pack, a voter's polling card — each of which is a specific tempting file, not a generic caution.

**Leg 2 — privacy rules differ.** Yes, and this is what carries the row. The government default's posture is "submissions and named-person case material are protected by default" — a *per-file* rule about subjects of proceedings. This world needs two rules that the per-file frame cannot express:

1. **A join prohibition.** Voter-identity evidence (register extracts, marked registers, absent-vote issue and verification records) and ballot evidence (ballot serial ranges, adjudication images, per-ballot records) are *both* legitimately retained by the same office, and the entire design of the world depends on their never being linked. A file organizer whose job is to co-locate related files is, by default, a machine for committing exactly this violation: both classes cite the same poll, the same station, the same date, and a naive grouper will put them in one folder or one summary prompt. I encode this as two PROHIBITED GROUPING entries in `grouping_reasons`, in `sensitivity_why`, and in the `must_not_conclude` of the marked-register, email and archive fixtures.
2. **Bulk rather than case sensitivity.** A marked register is sensitive because it is everyone, not because anyone is under investigation. The default's protection trigger (named-person case material) would under-protect it, since no elector is a case subject.

Both rules bear on the existing design floor rather than inventing one: “Privacy policy must be enforced before content reaches any model or external connector,” and “Protected material should not be included in cloud-model prompts by default, should not display raw content in general group summaries, and should not be moved automatically without a user policy that explicitly permits it.” Both spans grep verbatim out of `00`.

**Leg 3 — dimensions differ.** In shape, yes; in serialization, no. The default's prose order is authority-side function or bounded proceeding first. This world's natural order is poll event → contest → station or batch → **function last**, because a ballot account or adjudication sheet is unintelligible outside its station and contest — the design's own rule, “A work type such as Homework 3 is meaningful only after the course is known.” `time_first` is false despite the anchor being a date: a poll's registration, absent-vote, poll-day, count and retention phases straddle a year boundary, so “putting year first scatters related work across calendar folders” applies with unusual force here. Under PR-6 the array is empty, identical to the default's empty array, so I do not claim this leg. Legs 1 and 2 are sufficient.

## Files considered and rejected

Named tempting false positives, each with its discriminator:

- **`Nomination Pack - completed - J Rivera - signed.pdf`** — the authority's own blank form, filled in, with subscriber signatures. Rejected: the authority's *form layout* is the most-copied artifact in this world. Discriminator: receipt stamp, office file reference, validity determination. → `nonprofit.political-campaign`.
- **`North District poll - weighted crosstabs and turnout model.xlsx`** — rejected because "poll" here means opinion poll. Discriminator: sampling, weights, fieldwork dates, margins; an estimate has no issue total to reconcile against. → `business_operations.market-research`.
- **`Board Election Ballot and Scrutineer Report - Riverside Co-op 2026.pdf`** — rejected: every furniture item matches. Discriminator: the electorate's basis is membership, not registration on a public roll. → `nonprofit.member-association`.
- **`Poll card and postal ballot tracking notice - my household.pdf`** — rejected: issued by the same office, carries elector number and station. Discriminator: addressed *to* a named elector; recipient custody. → `identity.core-documents` / Protected Records.
- **Tender evaluation for a counting system** — rejected despite every sheet saying "election". Discriminator: buyer-side sourcing and award. → `government.public-procurement`.
- **A published turnout release, boundary map, or official post-election report** — rejected: publication by an election authority is not administering custody. → Reading Inbox.
- **An observer mission report or an agent's count tally** — rejected: same station identifiers, same timings, same disputes. Discriminator: no office appointment, no adjudicating mark, no signature under an officer role.
- **An election petition bundle** — rejected as a distinct edge; it is the schema-level Government/Legal collision already authored on `government.json`, and I do not duplicate it.
- **A public-sector employee's own poll-clerk appointment letter and payslip** — rejected: government as employer is a career/finance record. The staffing *schedule* held by the office is this row; the individual's copy is not.
- **`EMS results database backup 2026-05-08.bak`** — kept as a fixture but explicitly not read: no contents, contests, or elector data may be inferred from a filename. → Unsupported or Encrypted.

## The collision fixture — the same bytes on both sides

`Election Count Reconciliation - North District.csv` is not hypothetical: it is fixture 7 of the government schema anchor's own `file_examples`. Both sides claim it, so I state the boundary in both directions and name it on both:

- **Default → this row:** the default fires when the only evidence is an authority producing an administrative record that concerns an election — a policy paper on election funding, a committee report on turnout, a budget line for poll costs, a boundary review.
- **This row → default:** this row fires only when poll-operational structure is present — a form that must balance, a nomination or absent-vote register, station and seal logistics, an adjudication, or a declaration tied to an upstream contest identifier. Bare per-station issued/counted/variance columns with no office block do **not** clear that bar; the fixture routes to the default or to Review Later.

I have written this asymmetry into the fixture's own `must_not_conclude` ("that this row activates rather than the government default merely because the filename says election"), so the shared bytes are documented on my side. **Recommendation to R1c:** add the reciprocal clause to `government.json`'s `collides_with` if a schema is permitted to collide with its own child; I did not edit the anchor.

## Reciprocal boundaries

Six mutex edges, each stated in both directions in the JSON `signal` text. Summarized:

| Neighbour | This row holds | They hold | Shared fixture |
|---|---|---|---|
| `nonprofit.political-campaign` | receipt-stamped, determined, officer-signed | the candidate's completed copy, agent tallies, spending returns | the nomination pack |
| `government.public-authority-record` | poll-operational structure | election *policy/administration about* elections | the reconciliation CSV |
| `nonprofit.member-association` | public roll + statutory office | membership-based internal election | ballot + scrutineer report |
| `identity.core-documents` | office-side register/issue/verification record | the elector's polling card, confirmation, tracking notice | the elector number |
| `government.public-procurement` | operational use of what was bought (delivery vs allocation, seal logs, equipment tests) | sourcing, evaluation, award | counting-system evaluation workbook |
| `business_operations.market-research` | enumerated ballots reconciled to an issue total | sampled estimates with weights and margins | per-district numeric tables |

## Neighbours considered that got no edge

- **`legal.*`** — the election petition, the judicial review, the prosecution for a polling offence. Real same-bytes competition, but it is exactly the Government↔Legal collision already authored at schema level on `government.json`. Duplicating it here would be a second copy of the parent's edge, not new information.
- **`government.constituent-casework`** — a complaint about a polling station arrives as casework. I judged this a *sequencing* overlap rather than a same-evidence mutex: the incident log is written by poll staff during operations, the casework file is opened after. If landed sibling research shows a genuine reciprocal mutex, R1c can add it.
- **`government.statistical-programme`** — turnout and result statistics look like official statistics. No edge: a count is an enumeration, not a survey, and the statistical row's discriminators (methodology, disclosure control, microdata access) are absent from a ballot account.
- **`government.municipal-administration`** — very often the *same office* runs the poll. That is co-custody, not confusable evidence; the municipal row's furniture (agenda, papers, minute, resolution) is not this row's furniture.
- **`photos.screenshot-captures`** — a coactivation case on the dashboard screenshot fixture (`also_schema: "photos"`), not a mutex.
- **`nonprofit.advocacy-campaign`** — referendum campaigning. Already covered by the `political-campaign` edge; a second edge would be practice-area padding.

## Fields, proposed fields, and dimensions

`fields: []` and `proposed_fields: []` are deliberate under PR-6 and D1's standing deferral. Candidates were considered and **not** proposed:

- `poll_event`, `contest`, `polling_station`, `ballot_batch`, `returning_officer`, `electoral_roll_reference` — none is a canonical key, all would be minted by a placeholder child, and the anchor's own open question reserves any role-safe vocabulary for central adjudication rather than for children.
- `record_type` and `institution` exist canonically but are scoped to Finance; `work_type` is Academic's. Reusing them here would be a synonym raid, not reuse.
- Even if fields were ratified, `returning_officer` and any elector- or candidate-named key must be **non-destination-eligible**: an elector branch is a secrecy failure and a candidate branch imports campaign structure into an administrative file.

## Residual routing

Protected Records is the principal fallback (registers, marked registers, verification records, adjudications, staff data, mixed poll archives). Independent Records takes standalone published notices, nomination statements, declaration copies and polling cards — the assignment's two required residuals both carry real traffic. Review Later takes files that are plainly election-operational but whose administering role or public-body status is unresolved, including the shared reconciliation CSV. Unsupported or Encrypted takes the EMS backup. The screenshot fixture routes to Temporary Screenshots at the fixture level only; I did not add it to `falls_through_to`, since screen-capture residual routing is Photos' concern and not a fallback for this row's recognized material.

## NEEDS-JOSEPH

1. **NJ-1 — the join prohibition has no home in the contract.** Ballot secrecy is a constraint on *relationships between files*; `recognition`, `grouping_reasons` and `sensitivity` are all per-node. Alternatives: (a) P9 gains a first-class mutual-exclusion between named evidence classes, so a grouper is structurally prevented from co-locating them; (b) P7's handling policy absorbs it as a class-pair rule; (c) it stays advisory prose that an implementation may silently ignore. I have written (c) and flagged it in `open_question`, because (a) and (b) are not mine to invent. This is the single most consequential open item on the row.
2. **NJ-2 — bulk personal data has no posture distinct from case material.** A whole-electorate roll and a single named-person case file both land on `potentially_sensitive`. If P7's vocabulary never distinguishes scale, a marked register and a permit letter get the same handling. Decide whether scale is a P7 dimension or is simply out of scope for this phase.
3. **NJ-3 — publication asymmetry inside one packet.** A declaration is publishable; the marked register beside it is not. Decide whether packet posture is the maximum of its members (my assumption, written into `sensitivity_why`) or whether members may carry independent postures that a display label must respect.
4. **NJ-4 — jurisdiction variance.** Ballot accounts, tendered votes, subscriber lists, absent-vote personal identifiers and adjudication categories exist in some systems and not others; systems with electronic voting have no ballot-paper account at all. I wrote against structures that recur across systems and did not name any jurisdiction. Decide whether a later pass may carry jurisdiction-specific recognition, or whether abstention remains the rule.

## Self-verification

- `python3 -m json.tool` parses the node file.
- Key set is byte-identical to `government.json`'s (no missing, no extra keys).
- All six `collides_with` domains resolve against `roster.json` `domain_id`s.
- All 18 `file_examples.source_type` values are in `src/evidence_shape/vocabulary.py` `SOURCE_TYPES`.
- All eight quoted spans grep verbatim out of `planning/00-database-agent-product-design.md` (lines 42, 45, 95, 120, 177, 185).
- No thresholds, no handling classes, no folder paths as facts, `fields` and `proposed_fields` empty.
- Files written: only the two assigned. No neighbour, roster, canonical-fields, `src/`, or SPEC file touched.
