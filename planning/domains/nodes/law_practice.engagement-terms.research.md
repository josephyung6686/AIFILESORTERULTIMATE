# Research memo — `law_practice.engagement-terms`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.engagement-terms.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, placeholder launch
Verdict: **`refuse_node: true`**

## Result

Refused. "Engagement letters, retainers and scope" is not an organisational situation on the `law_practice` schema — it is that schema's **activation precondition**, restated as a row. The schema's default requires an artefact "whose own labelled slots separate a PRACTITIONER OR FIRM role from a CLIENT role"; the client care letter *is* that artefact. A template whose detection signal is its own schema's precondition has no signal of its own, and the node test's refusal clause applies on all three legs at once.

The coverage does not vanish. It routes, on evidence each destination already owns, to `legal` (executed terms), the `law_practice` schema default (a named-client draft), `law_practice.precedent-bank` (the blank firm standard), `law_practice.time-and-billing` (the fee and costs structure), `law_practice.matter-correspondence` (the covering email), and `legal.personal-legal-matters` (terms the holder received as a client). Residuals are Protected Records, Review Later and Reading Inbox.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, read in full.
- The stamped assignment from `planning/domains/dispatch/make_prompt.py law_practice.engagement-terms`.
- `planning/domains/nodes/law_practice.json` — my schema anchor. Read for the default template: `recognition.deterministic[0]` (the precondition), the full `never_alone` list, `work_types`, `template.why`, `sensitivity_why`, `falls_through_to`, `file_examples`, and the `legal` / `legal.personal-legal-matters` collisions.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, read for depth calibration.
- `planning/domains/roster.json` — confirmed my id, `schema_id`, the 36 `law_practice` siblings, and every neighbour id I edge to.
- `planning/00-database-agent-product-design.md` — **grepped, not streamed.** Six spans verified verbatim before quoting (each `grep -c` returned 1): "a labeled form field"; "The default posture must therefore be local-first and data-minimizing."; "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."; "It should not form a supported group when there is no valid anchor…"; "…create meaningless one-child levels…"; "A work type such as Homework 3 is meaningful only after the course is known…". The two residual quotes in `falls_through_to` are carried from the schema anchor, which cites them as `design`.
- `grep -rl "law_practice.engagement-terms" planning/domains/nodes/` returned **nothing** — no landed row has yet argued a boundary against this id, so every boundary below is authored fresh and stated reciprocally for R1c to mirror.

## THE CHARGE — the strongest case that this row should not exist

I state it before the defence, as the brief requires, and I could not defeat it.

**1. It is a document-type word.** The row's name is three of them: engagement letter, retainer, scope. My own schema strikes exactly this shape — "A DOCUMENT-TYPE WORD, AND A DOCUMENT-TYPE WORD BESIDE A FIRM OR CLIENT NAME" — on the reasoning that "a document-type word is not a labelled party — it names no entity and resolves nothing about the first entity's role." Apply the schema's deletion test (delete every entity name and every document-type word; if nothing structural survives, nothing fires) to `Client Care Letter - Ellis and Co - scope and fees.pdf` and to `Statement of Work - Meridian - Market entry advisory.pdf`. What survives both is the same: two labelled party blocks, a scope section, a fee-basis section, an execution block. That is a professional-services agreement — a shape shared with consulting, vendor procurement, accountancy and architecture — not a legal-practice situation.

**2. It is already a value in its own schema's enum.** `law_practice.work_types` carries, verbatim, `"engagement terms, retainer, scope and funding-basis record"`. The dispatch rule is unambiguous: "`work_types[]` is an enum of values for a `work_type` (or equivalent) field. Do not ask R1a for a child node per work type." The schema's `proposed_context_terms` independently carries "client care letter", "engagement terms", "retainer" and "scope of instructions" — as terms that help the **schema** activate. The row's whole vocabulary is already spent upward.

**3. It is a lifecycle stage.** Engagement terms are the *opening* of a matter. `Scope variation letter … countersigned.pdf` makes this visible: "variation" names *when* in a matter's life the artefact was made, not what structure it carries. A row defined by position in a workflow is a stage, and stages are values.

**4. It is a duplicate of its schema's default template.** This is the decisive leg. The schema's precondition requires both "(i) an exact matter, file or engagement reference repeated across two or more artefacts, and (ii) at least one artefact whose own labelled slots separate a PRACTITIONER OR FIRM role from a CLIENT role." Leg (ii) *is* the engagement letter. Every other `law_practice` template that survives is named in the schema as a **separate structure the precondition does not already describe** — an intake-and-conflicts form, a matter-opening record, a time-and-disbursement column set, a limitation-and-diary portfolio table, a disclosure-review or privilege log, a blank-slot precedent, an internal work-product section grammar, a counsel-instruction pairing. Engagement terms is conspicuously absent from that list. It is absent because it is the precondition itself.

**5. Its strongest fixture belongs to a safety neighbour, and its second-strongest to a sibling.** A *signed* retainer has a bound party pair and an execution block — `legal`'s executed-instrument signal — and my schema concedes the point in its own words: every file in a matter with that shape "is `legal`'s ON `legal`'S OWN EVIDENCE, and this schema does not displace it." An *unsigned* firm-standard terms document has bracketed placeholders and blank signature lines — the schema's inverse-recognition signal, which `law_practice.precedent-bank` owns. The row is squeezed from both ends, and what remains in the middle is a named-client draft, which is leg (ii) and nothing more.

## Attempts to defeat the charge, and why each failed

I made three honest rescue attempts before accepting the refusal.

**Rescue A — the fee basis is distinctive.** A conditional fee agreement has a success-fee and uplift structure; an hourly retainer has a rate schedule; a fixed-fee letter has a scope-and-price table. *Failed twice over.* A fee basis is a **value** — hourly, fixed, capped, conditional — exactly as my schema ruled that "A practice area is a VALUE, not a structure." And where fee information genuinely *is* structural, it is already owned: the schema's time-and-disbursement signal fires on "one exact matter reference with timekeeper or fee-earner, activity or task narrative, duration or units, rate, and disbursement or expense rows", and `law_practice.time-and-billing` is that situation. `Costs estimate and funding options - 41127-0006.xlsx` is the proof: a workbook of scope stages against estimated fees, with no party block and no signature anywhere, so the only structure present is the billing column set. What is left on the letter itself is a fee *paragraph* — prose inside a two-role document, i.e. the schema default.

**Rescue B — the scope-and-exclusions pair is distinctive.** *Failed on the neighbours.* A "services to be provided" section beside a "basis of charges" section is the ordinary shape of a consulting statement of work, a vendor master services agreement, an accountant's letter of engagement and an architect's appointment. Two entirely independent professional worlds — `career.consulting-client-engagement` and `business_operations.contract-administration` — file the same structure. When a shape appears in three worlds it is a document type, not a situation.

**Rescue C — the privacy rule is stricter.** *Failed, and inverted.* `potentially_sensitive` is the strictest value available at this row (P7 owns handling classes; this row assigns none), so there is no stricter posture to move to. Worse for the rescue, the schema's default already rests on a **wider** third-party argument than this material supports: a privilege log or a disclosure production exposes many non-consenting third parties at once, where an engagement letter exposes one client. This row's privacy claim is *weaker* than the default's, and a weaker claim cannot found a node.

## The node test, argued in full

**The schema's default template, stated first.** Detection: the two-leg precondition above, with a long never-alone list that strikes firm names, practising certificates, legal vocabulary, court captions, matter numbers, document-type words, confidentiality legends, practice areas, source types, filenames, authorship metadata, download sessions, cross-matter similarity, public availability and bare personal names. Dimensions: empty by contract, with a prose recommendation of client (only where genuinely multi-client and explicitly approved) → matter → document function → period, explicitly not time-first. Privacy: `potentially_sensitive`, argued on third-party exposure, bulk and disclosive existence.

**Leg 1 — detection signals.** Identical, and not merely overlapping. Any signal this row could write ("two labelled role blocks with a scope section and a fee-basis section") re-states leg (ii) of the schema's activation precondition. There is no residue. The named-client draft, `Engagement letter - DRAFT for signature - Nash.docx`, activates `law_practice` directly and there is nothing more specific left for a child to recognise. Fail.

**Leg 2 — dimension order.** Identical, and would remain identical if D1 lifted. `fields: []` under PR-6, so `dimension_order` is empty here exactly as on the schema. Under the schema's prose recommendation, "engagement terms" is a **value of the function dimension**, sitting beside pleadings, correspondence and billing. Promoting a value to a level is what 00's template validation rejects: the engine "validates that the proposed template does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector, expose protected information, or produce empty branches when tested against the accepted group." A matter normally holds **one** engagement letter — the one-child case, exactly. Not time-first either: "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." Fail.

**Leg 3 — privacy rules.** Identical, per Rescue C. Fail.

Three legs, three failures, plus two independent grounds (document-type word; already an enum value). Refusal is not close.

## Files considered and rejected

Beyond the collision fixtures in the JSON, these were the tempting false positives:

- **`Matter opening form - 41127-0006.docx`** — the single most tempting theft, and it is my schema's **own** fixture. It carries a funding-or-fee-basis slot and a scope line, so a greedy engagement row would claim it. It stays where it is: the schema's matter-opening signal owns it because the discriminating structure is the **allocation of the matter reference** paired with a responsible fee-earner and an identity-verification section — the anchor that 00's grouping rules require, since a group "should not form … when there is no valid anchor". The fee-basis slot is one slot on somebody else's form.
- **`Conflict search - Hartley acquisition - CLEARED.pdf`** — also the schema's fixture, browse-adjacent to `law_practice.conflicts-check`. A clearance result is what permits an engagement, not the engagement. No party pair, no scope section, no fee basis.
- **A bar-association or law-society *model* engagement letter downloaded as a PDF** — pure specimen. No client, no matter, no third party; it is precedent-bank material at best and Reading Inbox otherwise. Filing it as somebody's record would be the expensive error in the wrong direction.
- **An accountant's or architect's letter of engagement in the same corpus** — structurally indistinguishable once the profession word is deleted. It reinforces the charge rather than the row.
- **A client's direct-debit mandate and identity scans travelling inside `Engagement pack - 41127-0006.zip`** — these keep their own schemas. Packet membership never copies a fact onto a member, and the archive is not unpacked solely to improve classification.
- **A termination-of-retainer letter** — the closing mirror of the opening letter; if the opening stage is not a node, neither is the closing one. Raised as NJ-LP-ET-2.
- **A folder literally named `01 Engagement`** — a folder name is an unlabelled position. It supports review only.

## Reciprocal boundaries

Each is stated in both directions and names the **same fixture bytes** on both sides. All five are authored as `collides_with` on the refused row so R1c can mirror them onto the surviving neighbours.

| Neighbour | Shared fixture | This side would claim it because | That side owns it because |
|---|---|---|---|
| `legal.personal-legal-matters` | `Ellis and Co - Client Care Letter - my divorce.pdf` | firm name, allocated matter reference, scope section, rate section — every token an engagement row has | the holder is the *addressee* and the signature is the client's; no intake screen, time record or holder-produced work product exists in the corpus |
| `career.consulting-client-engagement` | `Statement of Work - Meridian - Market entry advisory - executed.pdf` | two party blocks, scope, exclusions, fee basis, confidentiality, execution block | prepared-for / prepared-by consulting roles plus deliverables, milestones and acceptance criteria, and no practitioner-side apparatus anywhere |
| `business_operations.contract-administration` | `Master Services Agreement - Northbridge IT - Schedule 2 fees.pdf` | a services schedule plus a charges schedule is a retainer with different nouns | its anchor is a live obligation and a notice/renewal register, and its party pair is buyer-and-supplier |
| `law_practice.precedent-bank` | `TERMS OF BUSINESS (firm standard) v11 - CLEAN.docx` | it is the most "engagement terms"-named artefact a practice holds | bracketed placeholders, blank signature lines, drafting notes and a version marker are the schema's inverse-recognition signal; no client, no matter, no third party |
| `law_practice.time-and-billing` | `Costs estimate and funding options - 41127-0006.xlsx`; the rate schedule inside the executed retainer | the fee basis is the most-cited reason this row should exist | where fee information is structural — matter-reference column beside timekeeper, units, rate, disbursement — the schema's time-and-disbursement signal already fires |

`also_holds_with: legal` is the one non-contest edge: a signed client care letter legitimately carries **both** schemas — `legal` on its own executed-instrument evidence, `law_practice` on the two role blocks — and neither writes a field row, so the co-activation costs nothing. That is the second half of the refusal: two schemas already see the file, and the child template proposed to sit between them recognises nothing neither of them can see.

`role_split` is empty. It requires two field keys pointing at different roles, and this schema declares none.

## The collision fixture

`Statement of Work - Meridian - Market entry advisory - executed.pdf` is the primary one, and it is chosen deliberately over the more obvious personal-legal fixture because it attacks the *structure* rather than the *side*. Two organisation blocks, a scope section, an exclusions section, a fee basis, a confidentiality clause, deliverables, milestones, an execution block — it satisfies every structural feature this row would have claimed, and it is a consulting file. What discriminates it: the consulting prepared-for / prepared-by role pair with acceptance milestones, and the absence anywhere in the corpus of a practitioner-side apparatus (an intake screen, a matter reference allocated by the holder's own firm, a time-and-disbursement record, legal work product the holder produced). The discriminator is never a word inside the scope section.

The second fixture, `Ellis and Co - Client Care Letter - my divorce.pdf`, is the under-firing one and matters more for safety: it is the single most engagement-shaped file an ordinary person holds, and it is the holder's own record. It is named identically in the `law_practice` schema's own file list, on the same reasoning — a rare case where both sides of a boundary already agree in writing.

## Fields, dimensions and vocabulary

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `work_types: []`, `proposed_context_terms: []`. The row proposes **no** canonical field keys and mints no synonyms. Candidates considered and rejected: `client` and `our_firm` (canonical engagement-role keys, but `law_practice` references neither, and PR-6 forbids adding them here); `work_type` (the coverage is a *value* of it, which is the refusal); `record_type` and `institution` (scoped to Finance); `purpose` (scoped to College Applications). `fee_basis`, `scope`, `engagement_date` and `matter_id` were all considered and none is proposed — minting a key to justify a refused node would be the same mistake in a different file.

`work_types` is left empty rather than restating the single value, because the value already lives on the schema and duplicating it downward is precisely the error this row is refusing to commit.

## Residual routing

- **Protected Records** — personalised engagement documents with no accepted matter group: client care letters, signed retainers, engagement packs. 00 places this material there directly.
- **Review Later** — the side-unresolved case, which is this row's characteristic failure: practitioner or client, legal or consulting; plus the scanned `Engagement letter.pdf` with no readable slots.
- **Reading Inbox** — unpersonalised specimens: firm-standard terms with bracketed placeholders, downloaded model retainers, bar-association samples. Filing an empty template as somebody's record would be the wrong error, and the schema already reasons this way for the precedent bank.

## Neighbours considered that did NOT get an edge

- `law_practice.client-intake` and `law_practice.conflicts-check` — browse-adjacent siblings and genuinely earlier in the same workflow, but they compete for *no* fixture with this row: intake pairs a prospective-client slot with a conflict search result, and neither carries a scope-and-fee pair. Sequence is not collision.
- `law_practice.matter-correspondence` — named in a fixture's `must_not_conclude` (the covering email is correspondence, judged on its own evidence) but not edged: a message *about* a document is not the same evidence as the document.
- `finance.small-business-bookkeeping` — an engagement letter is not financial evidence; the invoice raised under it is, and that seam belongs to `law_practice.time-and-billing`, which already holds the edge.
- `legal.leases-agreements` and `legal.estate-planning` — practice-content categories, not same-evidence mutexes with an engagement instrument.
- `career.employment-records` — an employment contract is a two-party signed instrument with a fee basis, so it is structurally tempting, but it is `legal`'s executed instrument on one side and an employment record on the other; adding it would expand the row's argument without changing the verdict.

## NEEDS-JOSEPH

**NJ-LP-ET-1 — where does the refused coverage live if D1 and PR-6 lift?** Alternatives: (a) it returns as the `work_type` VALUE already in the schema's enum, `"engagement terms, retainer, scope and funding-basis record"` — this row's recommendation, because the artefact is the schema's activation precondition and a value is what a function slot holds; or (b) a field pass silently resurrects the id as a template once `scope` or `fee_basis` keys exist. R1c should choose (a) explicitly rather than let (b) happen by omission.

**NJ-LP-ET-2 — the variation and termination letters.** A countersigned scope-variation letter and a termination-of-retainer letter become `legal`'s instruments on execution, but they are also matter members. R1c should decide whether they sit in the matter's opening function slot beside the original terms or in `law_practice.matter-correspondence`. This row is not surviving to hold them, so the question must be routed rather than assumed.

**NJ-LP-ET-3 — a systemic warning for the other 35 siblings.** The argument that killed this row — *a template cannot be its own schema's activation precondition* — is not specific to engagement terms. R1c should apply it to every `law_practice` sibling whose evidence is one of the schema's two precondition legs rather than one of the schema's separately named structures. My reading of the anchor is that the surviving siblings each map to a *named* deterministic structure; I have not audited all 35 and I am not authorised to, so this is a recommendation, not a finding.

## Cross-row recommendations for R1c (no neighbour file was touched)

1. Mirror the five `collides_with` edges above onto `legal.personal-legal-matters`, `career.consulting-client-engagement`, `business_operations.contract-administration`, `law_practice.precedent-bank` and `law_practice.time-and-billing`, using the same named fixtures.
2. Record on the `law_practice` schema that the engagement letter is the worked example of precondition leg (ii), so the next agent does not re-propose this row.
3. Do not add `scope`, `fee_basis` or `engagement_date` to `canonical_fields.json` on this row's account.

## Self-verification

- `python3 -m json.tool` parses the node JSON.
- Key set matches the landed `law_practice` anchor exactly (including `proposed_context_terms`), and `file_examples` items carry the anchor's eight keys.
- Every `file_examples.source_type` is in `SOURCE_TYPES`: `text_document`, `ocr`, `spreadsheet`, `archive`, `email`.
- Every edge id exists on the roster: `legal`, `legal.personal-legal-matters`, `career.consulting-client-engagement`, `business_operations.contract-administration`, `law_practice.precedent-bank`, `law_practice.time-and-billing`. Every `falls_through_to` name is one of 00's nine residual homes.
- Six `00` spans grep-verified verbatim before quoting; the two residual quotes are carried from the anchor's own `design`-cited text. No fabricated quotation, no threshold number, no handling class, no `public_low`.
- `fields: []` and `proposed_fields: []`; no canonical key minted. Observations are split from facts in every fixture; no fixture writes a folder path as a fact; sparse fixtures carry `group_without_copying_facts: true`.
- Files written: exactly the two assigned. `planning/29-DOMAIN-OWNERSHIP.md`, the roster, `canonical_fields.json`, `check.py`, `src/` and every neighbour node were left untouched.
