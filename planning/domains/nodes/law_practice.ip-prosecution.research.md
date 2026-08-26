# Research memo — `law_practice.ip-prosecution`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.ip-prosecution.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, placeholder launch
Verdict: **ACCEPT**, with one open seam (NJ-IPP-1) that could still merge the row away at R1c.

## Result in one paragraph

The row survives because of a structural fact that has nothing to do with the words *patent* or
*trademark*: the characteristic files of this world **fail the parent schema's second activation leg
and still belong to the family**. `law_practice`'s default requires an exact matter reference
repeated across artefacts **and** at least one artefact whose labelled slots separate a practitioner
role from a **client** role. The office's own forms — filing receipt, office action, reference
disclosure, notice of allowance, registration certificate — carry **no client slot at all**, because
the examination exchange is *ex parte* between a firm of record and an examiner. Under the default
template, most of this row's corpus would not activate. The row therefore supplies a substitute
second leg — an **office-issued right identifier in a labelled slot paired with the correspondent
firm's own docket reference in the office's correspondence-address block** — and that pairing is a
detection signal no sibling has, testable on real bytes, and not a practice-area word.

## Sources read

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full).
- The stamped assignment from `make_prompt.py law_practice.ip-prosecution`.
- `planning/domains/nodes/law_practice.json` — the schema anchor, and the thing this row is measured
  against. Read for its default template, its `never_alone` list, and its prose dimension paragraph.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — the landed launch row used as the
  depth calibration.
- `planning/domains/roster.json` — confirmed this id, its 36 `law_practice` siblings, and every
  neighbour id used on an edge.
- `planning/00-database-agent-product-design.md` — **by targeted `grep -n` only**, per the token
  discipline in the dispatch. Eighteen candidate spans were grep-verified verbatim before use; all
  eighteen returned exactly one match. No span is quoted here or in the JSON that was not verified.

Real-world artefact knowledge (form structures, claim status identifiers, recordal cover sheets,
annuity schedules, unofficial renewal solicitations) is **inference from the document types
themselves**, not from the design docs, and is marked as such wherever it carries weight. This row
imports no legal rule, no office list, no form-number catalogue and no jurisdiction logic.

## THE CHARGE — the strongest case that this row should not exist

I put the case at its highest before writing anything, and four of the six named failure modes have
real purchase here.

**1. It is a practice-area word, and the schema struck that word by name.** `law_practice`'s
`never_alone` reads: *"A PRACTICE-AREA WORD ALONE - family, criminal, immigration, conveyancing,
probate, employment, intellectual property, corporate. A practice area is a VALUE, not a structure."*
The row is literally named after a token its own parent strikes and names. A row whose entire content
is "the default template, but the matter happens to be an IP matter" is the default template with a
narrower filename filter, which the schema says is exactly the thing to refuse.

**2. It is a lifecycle stage.** *Prosecution* is precisely the phase between filing and grant.
Pre-filing is drafting, post-grant is enforcement and exploitation. A row bounded by a lifecycle
stage is one of the named failure modes and here the boundary is textbook.

**3. It is a duplicate of a sibling.** `law_practice.regulatory-submission` exists, and the parent
schema's own `work_types` list contains *"regulatory or registry submission made on a client's
behalf"*. An application to an IP office is a registry submission made on a client's behalf. On the
face of it this row is one enum value of its parent, promoted to a node.

**4. It is defined by an absence.** Its cleanest distinguishing feature — no adverse party, no
caption, no service — is a *negative*. Rows defined only by what is missing do not activate.

Two further charges I considered and found weak: it is not a document type (it spans a dozen
unrelated ones), and it is not an organisation name (the office is explicitly struck as never-alone
in the JSON).

### The defeat

Charges 1, 2 and 4 fall to the same evidence, and the evidence is positive, not negative.

Take an office action and ask what actually identifies it. Not the word *patent* — that word appears
in marketing decks, engineering write-ups and investor material constantly, and the JSON strikes it.
What identifies it is a **front-page slot block** in which the granting authority has printed an
application number, a filing date, a priority date, an examiner and an examining unit, **beside a
separate labelled correspondence-address block carrying the firm's own docket reference**. Neither
half fires alone and the JSON says so: the right identifier alone sits on every published register
document anybody can download, and a bare docket reference is an identifier the parent already
struck. It is the *pairing across two slots the office itself labelled* that says a firm is acting of
record. That is a structure, present in the bytes, and it is not a practice area, not a stage, and
not an absence.

Charge 2 fails on a second ground once you look at grouping. The row's anchor is not the matter and
not `project`: it is an identifier **allocated by a third party, printed on that third party's forms,
which outlives the matter, transfers with the right between firms and proprietors, changes its own
form as the right progresses (application → publication → registration), and recurs on an annual
renewal cycle for decades.** A lifecycle stage cannot outlive the engagement that contains it. This
anchor routinely does, which is why the JSON's dimension recommendation inverts the schema's
(see below).

Charge 3 does **not** fall. I could not defeat it from the design docs, and I refused to smooth it.
It is written up as **NJ-IPP-1** with three named alternatives, including "merge this row away and
demote IP prosecution to a `work_type` value". If R1c takes that option, this memo's file set and
boundaries transfer intact to `law_practice.regulatory-submission`, and nothing is lost.

## The node test, all three legs

**Leg 1 — detection signals differ from the schema's default.** Yes, and this is the strongest leg.
The default's leg (ii) is a practitioner/client role pair in labelled slots. The office's forms have
no client slot, so the default under-fires on this row's core corpus. The substitute is the
dual-docket pairing. Three further signals exist nowhere else in the family: the **numbered objection
set joined to claim numbers with a stated reply period and no caption**; the **claim-amendment
listing with per-claim status identifiers** (original / currently amended / cancelled / new) whose
join to the office action is a **claim number** rather than a party or a date; and the **rights
portfolio table** whose rows are registered numbers with annually recurring due dates.

**Leg 2 — recommended dimensions differ.** `dimension_order` is `[]` for the schema's three
unchanged reasons (no declared field under PR-6; safety co-activation with `legal`; disclosure). But
the *prose* recommendation, which is what every sibling must differ from, is genuinely different in
two ways. The schema's prose is client → **matter** → function → period. This row asks for one
**inversion** — the **right** comes before the matter, because one right is prosecuted, renewed,
assigned and re-argued across several matters and several firms over decades, so a matter-first
branch scatters one right's own life exactly as 00 warns year-first branching does: *"For document
and record domains, project, function, or subject usually comes before time because putting year
first scatters related work across calendar folders."* Function still follows the right, for 00's
parent-intelligibility reason: *"A work type such as Homework 3 is meaningful only after the course is
known"* — a response or a renewal confirmation is unintelligible without the right it answers for.
And one **additional ban**: the right identifier is seeded ineligible *more strongly than the
schema's client level*, because an application-number-named folder discloses not just that a client
is in a matter but, via one public search, the technical content of what they are building — and
where the application has not yet published, it publishes the existence of the filing itself.
Jurisdiction, office and classification may never be levels; the schema's ban is inherited unchanged.

**Leg 3 — privacy rules differ.** Yes, but not in posture, and I want that stated honestly rather
than inflated. The posture (protect) is the same. What differs is the **exposure being guarded
against**. The schema's claim is that a named third party is exposed. Here there is a second
exposure the roster has nowhere else: **content leakage destroys the asset**. An unfiled specification
derives its entire value from not having been disclosed, so an excerpt in a remote prompt or a
summary on a shared screen can extinguish the client's property right. The corollary rule is one no
sibling needs: **publication state is a legal event that is not readable from the bytes**, and the
same text flips between maximally sensitive and freely downloadable on a date nobody wrote in the
file. The row's rule is to assume unpublished and never infer otherwise from a printed number.

Three legs, three differences, of which the first and third are unique in the family. Accept.

## Files considered and REJECTED — the tempting false positives

This is the part a listing-only row omits.

- **`US11234567B2.pdf`, a granted patent downloaded from a public register.** The row's primary false
  positive and its **collision fixture**. Every identifier the row recognises is present in labelled
  front-page slots — number, filing and priority dates, applicant, assignee, inventors, examiner,
  agent-or-firm line, classification. It is still not this row's evidence: it is a published register
  document that would look byte-identical on a stranger's disk. **The discriminating absence is the
  dual-docket pairing** — no correspondence-address block, no attorney docket slot — so the substitute
  second leg fails. Routes to Reading Inbox. A folder of forty of them is a download session, and
  *"A session should never be treated as proof of topic"*.
- **`Trademark Renewal Notice - REGISTRATION 5,884,201 - AMOUNT DUE.pdf`** — the second collision
  fixture, and a real and common document type. Unofficial renewal solicitations are built by
  **scraping public registers**, so the registration number, the mark, the proprietor address and the
  renewal date are all correct. Every never-alone token the row strikes — official-looking crest,
  registry-sounding name, form-number-shaped reference — is deliberately imitated. Discriminator: an
  issuer-and-payment structure with **no correspondence-address block and no docket reference**.
  Routes to Receipts and Confirmations. The product records observations and takes no position on any
  sender's legitimacy.
- **A standalone `Logo_final.ai` or packaging photograph.** Looks like a specimen. Is
  `creative.brand-identity`'s asset until an enclosing submission's own slots label it a specimen
  against a class and a first-use date. A registered-mark symbol in the artwork is explicitly not the
  discriminator.
- **An executed patent or trade-mark licence, a royalty statement, an FTO opinion.** Same right
  identifier, opposite purpose: these exploit a right that already exists. `creative.licensing-rights`,
  `law_practice.transactional-deal`, `law_practice.opinions-advice`.
- **A cease-and-desist letter or an infringement complaint** carrying the patent number. Enforcement,
  not prosecution — `law_practice.matter-correspondence` and `law_practice.pleadings`.
- **A notice of opposition or a re-examination request.** Inside the same office, same identifier, but
  two named parties and a captioned style. Conceded to `law_practice.pleadings` in full.
- **The practitioner's own IP-bar registration certificate.** A person's credential, not a right's
  identifier — `career.credentials-licenses` / `law_practice.admission-cle`. This is the parent
  schema's struck practising-certificate token wearing a number, and it is dangerous here precisely
  because it sits next to real right identifiers and looks like corroboration.
- **An IP asset schedule inside a data room.** `law_practice.due-diligence`.
- **A lab-notebook page cited as evidence of conception.** `research.lab-notebook-protocols` unless
  enclosed in a submission.
- **A domain-name registration confirmation.** Looks like registering an IP-shaped right; it is a
  purchase confirmation. Receipts and Confirmations.
- **A prior-art search result set.** Rejected as this row's evidence: a list of patent numbers in a
  document body is a citation list, and the parent's `law_practice.legal-research` holds research
  output. Only the *office's own* cited-references sheet, attached to an objection set, is this row's.

## Reciprocal boundaries — both directions, same fixture named on both sides

Eight `collides_with` edges are authored in the JSON, each stating what this row keeps and what the
neighbour keeps, with one named fixture common to both. Summarised:

| Neighbour | This row keeps | Neighbour keeps | Shared fixture |
|---|---|---|---|
| `engineering.invention-disclosure` | disclosure transmitted to an instructed firm with an allocated docket | the form on employer-template, inventor-compensation and lab-notebook evidence | `Invention disclosure - IDF-2026-014 - Hartley R&D.docx` |
| `law_practice.regulatory-submission` | submissions creating/maintaining a **transferable registered right** | compliance/authorisation submissions producing no such identifier | `Office Action - Application 18-742-113 - our ref P4412-US.pdf` |
| `law_practice.pleadings` | the *ex parte* exchange with no other side | anything with a party pair, a caption and service | a notice of opposition on application 18-742-113 |
| `law_practice.deadlines-diary` | a table whose rows are **rights** with annually recurring dates | a table whose rows are **matters** with one-off procedural dates | `Annuity schedule 2027 - Hartley Group portfolio.xlsx` |
| `creative.brand-identity` | the image **only** inside a specimen submission | the standalone image, always | `Specimen of use - packaging - class 9.jpg` |
| `creative.licensing-rights` | the recordal cover sheet | the licensing and royalty terms | the eleven-identifier schedule in the recordation PDF |
| `research.reading-library` | register documents **with** the docket pairing | every register document arriving without it | `US11234567B2.pdf` |
| `legal.personal-legal-matters` | filings where a firm is of record | filings where the correspondence address is the holder's own | a filing receipt addressed to the applicant's home |

`also_holds_with`: `legal` (a recordal cover sheet stapled to an executed deed — the deed is `legal`'s
on its own party-pair-plus-execution evidence, and `legal` is a safety domain whose protection runs
first); `research.manuscript-publication` (00's abstract-and-application case in this world, where the
dual life is unusually consequential because publishing the manuscript can destroy the specification's
novelty); and `engineering.invention-disclosure` **again**, deliberately in both lists — with the
transmission evidence it is genuinely both records, without it this row simply loses. R1c should keep
both edges rather than collapse them.

`role_split` is empty: the schema exposes no field, so there is no key to split a role on.

## Neighbours considered that got NO edge

- `finance.small-business-bookkeeping` — an annuity **invoice** from a renewal agent is finance's on
  finance's own issuer-and-billed-to evidence, and this row does not claim it. The annuity *schedule*
  has no institution-and-account header, so there is no same-evidence mutex to author.
- `law_practice.time-and-billing`, `law_practice.matter-correspondence`, `law_practice.precedent-bank`
  — real overlap, but it is the *parent's* overlap, already argued on the anchor. Duplicating it here
  would inflate the row without adding a discrimination.
- `government.permit-licensing` — a licence or permit is not a transferable registered property right
  with a renewable official identifier, and it is the holder's own. The seam that matters is with
  `law_practice.regulatory-submission`, and doubling it would obscure NJ-IPP-1.
- `identity` — no identity documents are characteristic here; inventor declarations are not identity
  evidence.

## proposed_fields

One entry, `record_type`, and it is raised in order to argue **against** minting anything. The row's
real anchor — the office-issued right identifier — is held by no canonical key: `project` (which the
schema proposes for the matter) cannot hold it, because one right spans many matters and one matter
covers many rights. My preferred resolution is **option (a): no key at all** — the identifier stays a
literal observation used for linkage during local review and is never stored or written into a path,
because it resolves in one public search to a named proprietor and a technical disclosure. It is
recorded so that `patent_number`, `application_number`, `registration_number`, `official_number`,
`right_id`, `ip_family` and `docket_number` are named once as variants of a single concept and no
sibling mints a spelling of it. No other field is proposed; `fields: []` per PR-6.

## NEEDS-JOSEPH

- **NJ-IPP-1 (blocking, reciprocal).** The seam with `law_practice.regulatory-submission`. An
  application to an IP office *is* a registry submission on a client's behalf, and that phrase is a
  `work_type` value on the parent. Proposed discriminator: the persistent, transferable, renewable
  office-issued right identifier. Alternatives: (a) keep both rows on that seam; (b) **merge this row
  away** and demote IP prosecution to a `work_type` value on the sibling; (c) merge the sibling into
  this row. R1c must choose reciprocally. This memo transfers intact under (b).
- **NJ-IPP-2.** Whether the right identifier may ever be a stored fact. This row says no; `record_type`
  is raised so the question is adjudicated once rather than thirty-six times.
- **NJ-IPP-3.** Publication state is a legal event, unreadable from the bytes, that flips identical
  text between maximally sensitive and freely downloadable. This row assumes unpublished and never
  infers otherwise. Confirm that a conservative rule which will over-protect large numbers of freely
  downloadable register PDFs is the intended trade.
- **NJ-IPP-4 (recommendation to R1c, cross-row — not applied here).** If R1c ratifies the
  right-before-matter inversion, the schema anchor's prose dimension paragraph should record that one
  named exception, so the two documents do not disagree. I did not edit the anchor.

## Self-verification

- `python3 -m json.tool` on the node JSON: **passes**.
- All ten edge ids and all four `also_schema` schema ids: **each returns exactly one `domain_id` match
  in `roster.json`**.
- Eighteen quoted spans grep-verified against `00` before use: **each returned exactly one match**.
  No quotation appears that was not verified.
- `fields: []`; one `proposed_fields` entry, arguing for no mint. `dimension_order: []`;
  `time_first: false`. Sensitivity is `potentially_sensitive` only; no handling class, no threshold,
  no count, no score anywhere.
- Twelve `file_examples`, every `source_type` drawn from `SOURCE_TYPES`, observations split from
  facts, no folder path written as a fact, four `falls_through_to` names all from 00's residual list.
- Files written: **only** `planning/domains/nodes/law_practice.ip-prosecution.json` and this memo.
  No roster, schema, sibling, canonical-fields, `src/` or shared file was touched.
