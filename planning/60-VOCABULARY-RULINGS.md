# 60 — The vocabulary rulings, settled

Date: 2026-08-28. **This document is the contract.** It closes every open question that
blocked `canonical_fields.json` and `src/facts/`. Downstream agents bind to this file.

Authority order unchanged: `00-database-agent-product-design.md` → `domains/_CONTRACT.md`
→ `47`/`48`/`49` → `54` → `57` → **this document**. Where `57` and this document differ,
this document wins, and the reason is stated inline.

---

## 0. What changed since `57`

`57`'s §1 signature table was computed over **template rows only** and silently excluded
each schema's own **anchor row**. The anchor is the schema speaking for itself, so it is
the strongest signature there is. Recomputed with anchors included:

| schema | `57` said | actually signed (anchor included) |
|---|---|---|
| `clinical_practice` | proposes nothing | anchor signs **exactly one** — `subject_of_record` |
| `logistics` | 2 unsigned keys | anchor signs **5 of 6**; only `record_period` unsigned |
| `government` | 4 unsigned keys | anchor signs **none**; one template signs `programme` |

`57`'s blocker-1 *conclusions* survive; its *reasoning* for two of the three does not.
`clinical_practice` reduces to one key because its anchor asked for one — **not** because
it was silent. And `logistics` signed `consignment` and `carrier` **by name in its own
anchor**, which is independent support for blocker 2 below.

---

## 1. Ruled by Joseph, 2026-08-28

**J-1 — `SCHEMA_IDS` widens 10 → 23.** All 23 roster schemas become schemas the product
recognises. (`C1`, ratifying J-WIDE-1.)

**J-2 — The cycle family: TWO keys, declared as a `role_split` pair.**
- `recruiting_cycle` — **career** side. *The holder is a participant in the cycle.*
- `people_cycle` — **hr** side. *The holder runs the cycle.*
- Discriminator written reciprocally on both keys' `notes`.
- **`application_cycle` drops the bare alias `cycle`.**

This reverses `54`, which minted the spelling `00` never wrote and refused the one it did.
`00`:70 writes *"recruiting cycle"*; nothing in `00` writes *"people_cycle"*. Under D6's own
precedent the `00` word does not lose. `47` §2.2 already adjudicated `people_cycle` against
the whole period cluster and kept it separate, so `49` §1.6's condition is **satisfied and
closed** — `57` §5.1 is correct that `54` carried a closed question forward as open.

**J-3 — `career` declares BOTH `work_type` and `record_type`.**
Career's corpus is about half work-product (portfolio samples, tailored résumés, consulting
deliverables) and half record (employment records, credentials, licences). With only
`record_type`, a cover letter routes to `work_type`, finds it undeclared, and the extractor
must force it or abstain with nothing to say which. Both declared removes the forced route.

**J-4 — The 6-field cap: adopt the LOOSE reading of `00`:48.**
`00`:48 verbatim: *"usually three to six that may help build a future folder proposal **and
several additional fields used only for search, privacy protection, explanation, or later
review**."* The 3–6 band therefore caps **destination candidates**; `destination_eligible:
false` keys are the "additional fields" clause and do **not** count against it.
This is `54` §8(b)'s own reading and `57` §6 confirms `00` states it. (`C3`.)

**Consequence `57` §6 flagged and this ruling must answer:** under the loose reading the
band is a **floor** as well as a ceiling, and `hr` (2 dest) and `clinical_practice` (2 dest)
fall below three. See §2 — for `clinical_practice` the floor does not apply, and the reason
generalises.

---

## 2. `hr` — NJ-HR-1, answered from the corpus

Joseph's question, verbatim: *"I honestly don't think there's much of a difference between
business operations and hr? why are those not connected?"*

**They are already drawn apart, by `business_operations`' own defining sentence**, which
excludes HR by name: *"How an organisation runs ITSELF, **as opposed to what it sells or who
works there**."* But that alone is a boundary, not a justification, and Joseph is right that
the **vocabulary** distinction is weak — three of `hr`'s four proposed keys do fold into
generic keys, exactly as NJ-HR-1 feared.

**NJ-HR-1 was tested against the wrong half of its own condition.** Its text is an AND:

> *"The row survives only if `workforce_member`, `workforce_unit`, `people_cycle`, and
> `personnel_case` form a legal, distinct set **AND the protection-first default is
> schema-level behavior**."*

`54` and `57` both tested only the first conjunct. The second is independently true and is
the real distinction:

**Every `hr` row's subject is a person or a workforce population. No `business_operations`
row's is.** `business_operations`' 23 kept rows are about the organisation, its contracts,
products, suppliers, customers, risk, facilities and filings. `hr`'s 12 are about
compensation, grievances, DEI self-declaration, engagement responses, onboarding, payroll,
performance, health and safety — all of them keyed to people.

That is not a filing difference. It is a **P7 difference**, and the anchor says so:
*"employee-identifying content is protected before any cloud step."* That is schema-level
behaviour, which is precisely what the second conjunct asks for.

The two keys that folded are the two that carry the disclosure risk, and **both were
proposed `destination_eligible: false` for that exact reason**:
- `workforce_member` — *"A folder bearing an employee's name discloses personnel-record
  membership."*
- `personnel_case` — *"Even a pseudonymous case reference can disclose that a person has a
  grievance, capability, disciplinary, health, or injury file."*

**RULING J-5: `hr` ships — as a protection schema, not a filing schema.**

- Recognised in `SCHEMA_IDS`. Activation requires a personnel process, workforce population,
  or employee case structure — never "our firm is the employer".
- Destination candidates: **`people_cycle`** and **`workforce_unit`** (seeded `false`,
  template-time promotable, identically to `organization` — `48` grants promotion to one and
  not the other with no stated reason, and `57` §5.2 is right that there is none).
- Facts, never destinations: `workforce_member`, `personnel_case`, `subject_of_record`,
  `event`.
- **`work_type` is NOT declared on `hr`.** It has zero HR signature; it was borrowed from
  `law_practice`. `57` §3 is right that half of `hr`'s folder proposal was unearned.

**J-5a — the floor does not apply to a protection schema.** `00`:48's *"three to six that
may help build a future folder proposal"* describes schemas whose job is to propose folders.
A schema whose job is to keep a grievance file out of a named folder has fewer
destination-eligible keys **by design**, and two is the honest number. The same reasoning
covers `clinical_practice` at one. Recording this as a named exemption rather than letting
two schemas silently sit under a floor nobody restated.

**J-5b — NJ-HR-2 answered: no.** No employee or case key is destination-eligible at launch.
**NJ-HR-4 answered: yes.** Aggregated engagement / DEI / workforce-analytics material stays
protected by default; no de-identification threshold is invented here.
**NJ-HR-3 remains open** and is a P7 contract question, not a vocabulary one — it is carried,
not answered, and must not block this pass.

---

## 3. Adopted from `57`, with the blocker-1 correction

**B1 — Strip only the genuinely unsigned.** (Corrected per §0.)
- `clinical_practice` → **`subject_of_record` only** (`destination_eligible: false`). Its
  anchor signed one key; that key is it. Drop `record_type`, `record_period`, `authored_by`.
  `authored_by` is worse than unearned: the schema's defining sentence is that *the holder is
  the author*, so the value is identical on every file it activates and can separate nothing.
- `logistics` → strip **`record_period` only**. Its anchor signed the other five.
- `government` → **`project` only** (one signature, canonical key, zero mint cost). Drop
  `record_type`, `record_period`, `property`, `subject_of_record`. The schema's own
  `open_question` asks to stay field-less and to adjudicate *"centrally rather than in
  children"*; giving it four keys it never proposed overrules its own refusal.

**B2 — Reverse `consignment` → `event`. Mint `consignment`.**
`logistics.last-mile-pod`'s recorded order is *"consignment/parcel -> delivery event"* — fold
them and it reads `event > event`, which `00`:97's validator forbids by name. A consignment
is *"one described quantity of goods travelling under one carrier's undertaking"* — a thing,
not an occurrence, the same category as `asset`. And per §0 the anchor signed it by name.
`destination_eligible: true`, ceiling `validated`.

**B3 — `carrier` → `supplier` stands**, with the condition: `supplier`'s `notes` must carry
the labelled-slot rule (Carrier / Haulier / Forwarder / Shipping Line / Airline) and the
three-role warning — *a consignment note routinely names consignor, consignee and carrier in
three different roles on one page*. Without a discriminator the extractor picks one of three
org tokens at random.

**H5 — Reverse the `issuing_body` hold; declare it on `business_operations`.**
`54` held it because *"business_operations is at its 6-field ceiling"*, which is false under
J-4 — it sits at 5 destination candidates with one free. The hold strands
`business_operations.compliance-audit` (loses the only fact separating its own audits from
its suppliers' evidence packs) and `career.credentials-licenses` (whose recorded proposal is
*issuing authority → credential → document type*, and none of career's keys served any of the
three). One reversal fixes both.

**H6 — `record_type`'s `notes` carry all three halves**, not the one `54` proposed:
1. *Negative discriminator.* "If the file **is** the work product of a bounded engagement or
   course → `work_type`. If it is an **output of a making process** → `artifact_type`.
   `record_type` is what remains: the file evidences that a transaction, operation or
   decision occurred. Where two readings are both supported, `00` requires abstention, not
   the nearest declared key."
2. *Undeclared-route clause.* "A file whose routed type key is not declared by the active
   schema returns unknown; it is never re-routed to the nearest declared type key."
3. *Value-side scope.* `record_type` is schema-qualified. Ten schemas on one key otherwise
   put a bank statement, a production return, a proof of delivery and a grant report in one
   value namespace — and P9 groups on shared validated facts, so `record_type = "return"`
   would join a tax return to an oil-field production return.

**H7 — Alias collisions, fixed before they land.**
- **`tax_year` drops the alias `fiscal_year`.** Shipping `fiscal_year → tax_year` beside
  `fiscal_period → record_period` puts two genuinely different objects one character apart.
- **`application_cycle` drops the bare alias `cycle`.** (Also required by J-2.)

**H8 — `authorisation` → `authorization`.** `00` is 27–0 for the z spelling and uses the s
spelling zero times. Two orthographies in one snake_case namespace is two columns — the exact
defect D6 exists to kill, arriving as house style.

**H9 — `nonprofit`: restore the funder role.** Declare canonical **`institution`** on
`nonprofit` (and on `research`) per `48` §2, and **drop `project` and `record_type`**, which
nonprofit never proposed. Its row warned that without a funder role its strongest node —
restricted money with strings — has no key *"and a template author will mint one"*.
Final set: `organization`, `record_period`, `subject_of_record`, `institution`.

**M10 — Narrow `design_item` against `product`**, and write the sentence on both:
*"`design_item` is the controlled design configuration whose definition a file governs —
never a saleable or sold article, which is `product`."* `engineering`'s elimination checked
`project`, `subject`, `property` and `repository` and never checked `product`, because
`product` was minted in a different adjudication. A chiller model is a product model.

**M12 — State the `employer` ↔ `our_firm` discriminator on both keys.** For an employee the
employer *is* "the holder's own organization"; the keys differ only in role and eligibility,
and nothing in `48` or `54` says so. Without it, extractors fill both from one letterhead.

**M13 — Carry `finance.account_holder` into the pass** per `49` §4.1, with `institution` as
its `role_split` partner, `destination_eligible: false`. It was moved out of `finance.fields[]`
into `proposed_fields` mid-session and fell through; `finance` is a live `SCHEMA_IDS` member,
so this is a shipping schema losing a field with no replacement.

**Fence principle, adopted (`57` §5.3).** *A key is **fenced** when its role sentence cannot
be stated without naming its domain* — `media_type` ("kind of **capture**"),
`application_document_type` ("role inside an **application** packet"), `application_cycle`
("the **admissions** cycle"). *A key is **widenable** when its role is domain-neutral* —
`project`, `stage`, `artifact_type`, `work_type`, `record_type`, `event`. This replaces
`54` §11's double-naming diagnosis, which is wrong on the facts: `media_type` is not in
`00`:70 at all.

---

## 4. The mint list — 18 new canonical keys

37 live + 18 = **55**.

| key | scope declared | dest | ceiling | source |
|---|---|---|---|---|
| `site` | manufacturing | true | possible | `48` §1b |
| `asset` | manufacturing | true | possible | `48` |
| `product` | manufacturing | true | possible | `49` §1.5 |
| `supplier` | business_operations | true | possible | `48`, +B3 notes |
| `organization` | business_operations | **false** (promotable) | possible | `48` §3 |
| `issuing_body` | business_operations | true | possible | H5 |
| `record_period` | business_operations | true | validated | `47` |
| `property` | construction_property | true | possible | `57` §2 |
| `design_item` | engineering | true | possible | M10 |
| `subject_of_record` | law_practice | **false** (on the key, never per-template) | possible | `49` §1.7 |
| `authorization` | resource_operations | true | possible | H8 |
| `consignment` | logistics | true | validated | B2 |
| `people_cycle` | hr | true | possible | J-2 |
| `workforce_unit` | hr | **false** (promotable) | possible | J-5 |
| `recruiting_cycle` | career | true | possible | J-2 |
| `employer` | career | true | possible | `57` §2 |
| `target_employer` | career | true | possible | `00`:44 rule |
| `account_holder` | finance | **false** | possible | M13 |

`workforce_member` and `personnel_case` are **NOT minted.** They fold to `subject_of_record`
and `event` respectively (`54`, unchallenged), and J-5 keeps `hr` on the protection argument
rather than on those two keys.

**Reciprocal `role_split` pairs to declare:** `recruiting_cycle` ↔ `people_cycle` ·
`employer` ↔ `our_firm` · `account_holder` ↔ `institution` · `client` ↔ `our_firm` (live) ·
`school` ↔ `target_university` (live) · `employer` ↔ `target_employer`.

---

## 5. Per-schema field declarations — all 23

`†` = `destination_eligible: false`. Dest count is what J-4's 3–6 band measures.

| schema | fields | dest |
|---|---|---|
| academic | school · term · subject · work_type · instructor† | 4 |
| college_applications | target_university · application_cycle · application_document_type · purpose | 4 |
| research | project · stage · artifact_type · lab · venue · institution | 6 |
| finance | institution · account_type · tax_year · record_type · account_holder† | 4 |
| photos | capture_year · event · location · media_type · people† · camera_information† · capture_date† | 4 |
| code | repository · programming_language† | 1 |
| career | employer · target_employer · recruiting_cycle · work_type · record_type · job_title† | 5 |
| business_operations | organization† · record_period · project · client · supplier · record_type · issuing_body | 6 |
| law_practice | project · work_type · client · record_period · our_firm† · subject_of_record† | 4 |
| creative | project · artifact_type · stage · client · venue | 5 |
| construction_property | property · project · work_type · client · our_firm† | 4 |
| engineering | design_item · artifact_type · asset · project · stage | 5 |
| manufacturing | site · product · asset · event · record_period · record_type | 6 |
| retail_hospitality | site · event · record_type · record_period · product | 5 |
| resource_operations | site · asset · authorization · product · record_period · record_type | 6 |
| logistics | consignment · record_type · site · asset · supplier† | 4 |
| government | project | 1 |
| nonprofit | organization† · record_period · subject_of_record† · institution | 2 |
| hr | people_cycle · workforce_unit† · subject_of_record† · event† | 1–2 |
| clinical_practice | subject_of_record† | 0 |
| identity | — (safety domain, field-less) | 0 |
| medical | — (safety domain, field-less) | 0 |
| legal | — (safety domain, field-less) | 0 |

Schemas below the 3–6 band — `code`, `government`, `nonprofit`, `hr`, `clinical_practice`,
and the three safety domains — are **named exemptions under J-5a**, not oversights. `code` is
live today at 1 and has always been. The rest are protection schemas, deliberate minimal
declarations, or field-less by `PR-6`.

---

## 6. Still open, and explicitly NOT blocking this pass

- **NJ-HR-3** — member-level dual-schema handling for byte-identical payroll registers and
  investigation packs. A P7 contract question.
- **NJ-J-IND-3** — where an *organisation's* money lives (statutory→finance vs
  forward-looking→business_operations). Drawn by the roster pass, not by `00`.
- **NJ-NP-1** — whether `nonprofit` would rather be refused than kept to save an id.
- **`48` §2 refuses `carrier`; `48` §7 adopts it.** §7 is the stale line; fix in `48`.
- **`49` §1.6 cites PR-1 to justify the `people_cycle` mint. PR-1 pins `purpose`, not
  `application_cycle`.** The conclusion survives under §3's fence principle; the reasoning
  should be replaced rather than inherited.
- **`53` failed 11 of 15 launch roles on the *existing* vocabulary.** Nothing in this pass
  changes whether a real person says `record_period` or `subject_of_record` out loud. That
  test is owed again on the new keys, and `57` §5.3's value-side gap is where it bites first.

---

## 7. Signature justifications — the six §5 entries a signature census flags

A peer pass recomputed every §5 entry against what the rows actually signed, anchors
included, filtering out the deliberate merges. Six entries came back with no direct
signature. **One was wrong and is corrected above; five are correct and their merge paths
are recorded here, because an unexplained unsigned key is indistinguishable from the defect
`57` blocker 1 exists to catch.**

**CORRECTED — `logistics` drops `event`.** The peer is right. `event` sat on `logistics`
only as the *absorber* of `consignment`; with B2 reversing that merge it has no signature
left. And logistics did not merely fail to sign it — its anchor **eliminated it by name**:
*"`event` is the Photos capture-occasion."* §5 now reads `consignment · record_type · site ·
asset · supplier†`, 4 destination candidates. Declaring five keys where four do was the
exact over-assignment this pass exists to stop.

**`career · work_type` — J-3, and the asymmetry with `hr` is real and intended.**
Career's `proposed_fields` name `credential_expiry`, `employer` and `role` (→ `job_title`).
It never names `work_type`, so the peer's census is correct. J-5 struck `work_type` from
`hr` on exactly that ground, and the two must be told apart in writing:
- `hr`'s `work_type` had **no argument at all** beyond `law_practice` having it.
- `career`'s has `49` §3's routing rule, which is a *structural* signature rather than a
  proposal: a tailored résumé, cover letter or portfolio case study **is** the work, so the
  rule routes it to `work_type`. Half of career's corpus is that half.
Without the key, `49` §3(b) is a live failure in the shipping product: the file routes to
`work_type`, finds it undeclared, and the extractor must force it onto `record_type` or
abstain with nothing saying which. **A routing rule that names a key is a signature; a
sibling schema having a key is not.** That is the distinction, and it is what makes J-3 and
J-5 consistent rather than contradictory.

**`government · project` — merge path `programme` → `project`, per `49` §4.2(h).** Government
signed exactly one key across 32 rows and this is it, folded. Recording the fold explicitly
because the net reads oddly: the schema's only declared key is one it never spelled, while
the spelling it used is gone. That is what a fold looks like, and `49` §4.2(h) is where it
was decided.

**`nonprofit · institution` — merge path `sponsor` → `institution`, per `48` §2.** Nonprofit
signed `sponsor`; `48` §2 **refuses `sponsor` and directs that canonical `institution` be
declared on `research` and `nonprofit` instead**. `57` §3 quotes the instruction and records
that `54` carried neither the refusal nor its replacement, leaving nonprofit's grant-funding
node — *"restricted money with strings"* — unserved. §3 H9 restores it. The key is not
unsigned; its signature is `sponsor` and the adjudication redirected it.

**`hr · subject_of_record` — merge path `workforce_member` → `subject_of_record`**, per `54`,
unchallenged. J-5 keeps `hr` on the protection argument rather than on this key, so nothing
turns on it, but the path should be stated.

**`law_practice · record_period` — merge path `fiscal_period` → `record_period`**, per `47`.
Clean.

**Orthography, settled by census rather than by preference.** `00` writes `organization` 29
times and `organisation` **0**; it writes `authorized` once and `authorised` **0**. It never
writes either spelling of the noun. `00`'s orthography is therefore unambiguously American-z,
and H8's rename stands: **`authorization` is correct in `src/`, and the catalogue side moves
to match it.** The peer's concern is right in substance — one concept must not carry two
spellings across two stores — but the direction of the fix runs from `54`'s `authorisation`
toward `00`, not the other way.
