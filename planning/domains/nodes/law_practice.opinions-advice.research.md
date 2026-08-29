# Research memo — `law_practice.opinions-advice`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.opinions-advice.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accepted, and only just.** The row survives on one structural claim that took the whole
investigation to isolate: this is the only situation in the `law_practice` family whose evidence is a
**three-role, self-sufficient single artefact**. Everywhere else in the family the schema's default
precondition holds — an exact matter reference repeated across two or more artefacts, plus a separate
artefact whose slots split a practitioner role from a client role. A formal opinion satisfies the
professional-role separation **inside its own page** (author firm / client / addressee-entitled-to-rely)
and therefore fires on **one file with nothing around it**, which is exactly how opinions arrive: one
PDF in a closing binder, one advice in a folder with no surrounding apparatus.

Everything else about the row — that it holds letters, that they say "opinion", that lawyers write them —
is not evidence of anything and is argued away below.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full) and the stamped assignment from
  `make_prompt.py law_practice.opinions-advice`.
- `planning/domains/nodes/law_practice.json` — the schema anchor, read as the default template I am
  measured against.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — the depth calibration launch row.
- `planning/domains/nodes/law_practice.conflicts-check.{json,research.md}` — the only landed row that
  already argued a boundary against me (one grep: `grep -rl "law_practice.opinions-advice"`).
- `planning/domains/roster.json` — id confirmation for all eight edges.
- `planning/00-database-agent-product-design.md` — reached by targeted `grep -o` for each span I quote.
  **Every quotation below and in the JSON was grep-verified verbatim before it was written.** Verified
  spans: `Correct abstention is a successful outcome`; `The documents are content-incoherent but
  purpose-coherent.`; `Topic answers what a file is about, while purpose answers what the file was
  for.`; `A session should never be treated as proof of topic`; `It should avoid using authorship or
  creator identity as a destination dimension`; `The default posture must therefore be local-first and
  data-minimizing.`; `A file may validly belong to more than one accepted group`; `It should not form a
  supported group when there is no valid anchor`; `such as authored_by and target_school, or our_firm
  and client`. I dropped one intended quote (`a model that cannot cite sufficient evidence must return
  unknown`) because I could not verify it verbatim within budget, and paraphrased the abstention rule
  from the verified span instead. Provenance for the row is `inference`: it extends a named schema, and
  no span in `00` names opinions.

## THE CHARGE — the strongest case that this row should not exist

I state it at full strength before defending anything, because on first reading it is close to fatal.

**1. It is a work_type value, and the schema anchor says so in its own enum.** `law_practice.work_types`
contains `"legal research note, authorities list and opinion or advice record"`. The word is literally a
value in the schema's own list of values. The anchor also wrote the general rule against exactly this
move: a template justified only by holding a different legal document kind *is* the schema's default
template with a narrower filename filter. If "opinion" is a value of `work_type`, a row named
Opinions is a node minted from an enum member — the 574's original mistake.

**2. It is a duplicate of its own schema's default template.** The anchor's deterministic list already
contains: *"A COUNSEL-INSTRUCTION or OPINION structure: a brief or instructions document pairing an
INSTRUCTING slot with an INSTRUCTED or COUNSEL slot ... or an opinion whose own header names the party
advised and whose body separates questions asked from conclusions."* The schema **already fires on the
opinion structure**. The default's `dimension_order` is empty, its sensitivity posture is
`potentially_sensitive`, its residual is Protected Records. If I match all three, I am a filename filter.

**3. It is a document type — the format charge in its purest form.** "A letter on firm letterhead with
numbered paragraphs" describes engagement terms, a demand letter, a complaint response, a planning
submission and an insurance declinature. Letterhead-plus-numbered-paragraphs is a *medium*.

**4. It is a lifecycle stage.** Advice sits between instructions and action. "The advice phase of a
matter" is a stage of the schema's own workflow, not a filing world — the same way "draft" is not a node.

**5. It is never-alone evidence wearing a node's clothes.** The row's tempting signal is a firm name plus
the word "advice", which the schema's own `never_alone` strikes twice over.

**6. It is defined by an absence.** One reading of the row is "the legal documents that are not filings,
not instruments, not correspondence" — a residual dressed as a template, which is a refusal by another name.

## Defeating the charge

Charges 3, 4 and 6 fall to the same evidence and I take them first, because they are the cheap ones.

**Against 3 (format) and 4 (stage): the deletion test passes.** Delete every entity name, every
document-type word, the noun "opinion" and the noun "advice", and what survives is a co-occurring slot
set no other artefact in the family produces: a **DOCUMENTS EXAMINED** list, an **ASSUMPTIONS** section
stating facts taken as true and expressly *not verified*, a **QUALIFICATIONS / EXCEPTIONS** section, a
**SCOPE-OF-LAW** slot disclaiming every jurisdiction but one, an operative conclusion, and a date the
document **speaks as of**. That is a grammar, not a format, and it is not a stage: the bring-down and
reliance-extension letters below exist *after* the matter's action phase and maintain the opinion for
years. Against 6, the row is defined by that positive grammar, not by what it lacks.

**Against 5 (never-alone): conceded and encoded.** I did not defend the tempting signal; I struck it.
`never_alone` strikes the word `opinion` (headlined with the judicial case), the letterhead-plus-`advice`
pair, the modal word in free text, the numbered-paragraph letter, the bare addressee block, and — the one
I consider my most useful contribution — **a limitation-of-liability or no-third-party-responsibility
clause alone**, because that clause is one full half of my headline signal and it appears on every
consulting report, valuation, survey, actuarial certificate and audit deliverable ever written.

**Against 1 (work_type value): the row is not the word.** The row is the *addressed, reliance-bearing*
statement. The one_line_hint drew that line before I did — "*a client or a third party is entitled to
rely on*" — and it excludes most of what the enum member covers. The research note behind the advice is
`law_practice.legal-research`'s. The advice given in an email body is `law_practice.matter-correspondence`'s
(fixture `RE Can we terminate under clause 14 - advice.eml`, which I explicitly hand back). The blank
model opinion is `law_practice.precedent-bank`'s. What is left is not a document-type word's extension;
it is a narrower and structurally identifiable object, and I kept `work_types[]` as a list of *values*
inside it rather than asking for children.

**Against 2 (duplicate of the default) — the only one that matters, answered with three differences.**

- **Detection differs, and it differs by *relaxing* a leg of the default, which is the rarer and more
  honest kind of difference.** The default needs a matter reference repeated across two or more
  artefacts. An opinion letter routinely has no matter reference at all — it has an addressee block, a
  reliance clause and the assumptions grammar. Under the default's precondition, a single closing
  opinion sitting alone in a corpus **does not fire**, and that is a real hole, not a hypothetical.
  This row substitutes an intra-document structure for the cross-document one. It also adds a signal
  no row anywhere on the roster produces: the **bring-down / reliance-extension / withdrawal** letter,
  whose entire content is *another document's continuing validity*, identified by that document's date
  and addressee.
- **The role structure differs, and the default mis-describes it.** `law_practice`'s default is a
  **two-role** structure, practitioner against client. A formal opinion is routinely **three-role**, and
  the third party is neither: the addressees of a financing opinion are the lenders while the client is
  the borrower; the addressee of an auditor-response letter is the audit firm. The default cannot express
  the side, and the anchor built the whole schema on being able to.
- **The privacy rule differs in kind, not degree, and it survives every other change.** The rest of the
  family is protected because its contents are confidential. This row's characteristic document is
  *engineered to be handed to a named outsider* — and yet it carries a rule no sibling has: **the
  conclusion may never be stored, surfaced or summarised detached from the assumptions and qualifications
  that bound it**, because assumptions are load-bearing and a severed conclusion does not merely leak, it
  **misstates**. That is a redaction rule about *composition*, not about secrecy, and no other row on the
  roster states one. It is encoded in `sensitivity_why`, in the `never_alone` strike on detached
  conclusions, and in the screenshot fixture.

Three differences, each in a different limb of CONNECTION §2's node test. The row stands.

## Files considered and rejected

Naming what I refused matters more than naming what I kept.

- **`Supreme Court Opinion - Example Holdings v Example Agency.pdf`** — rejected, and promoted to the
  headline collision fixture. Total word collision, published, mass-downloaded, present in enormous
  numbers in exactly the corpora where this row fires. Discriminator: it has no addressee block and
  structurally cannot have one — a judgment is addressed to the world. `law_practice.orders-and-judgments`
  or Reading Inbox.
- **`Hartley Group - Tax Structuring Report - Nash Advisory LLP.pdf`** — rejected, and the *harder* of
  the two collisions because it carries half my signal genuinely. Discriminator: **findings-from-work-
  performed versus conclusions-on-assumptions-not-verified.** A report has a scope of work and a
  methodology; an opinion has assumptions it declines to check and exceptions it declines to cover.
- **`PRECEDENT - Legal opinion (firm standard) - v3.docx`** — rejected. The addressee slot is empty *by
  design*, so my precondition cannot be satisfied. `law_practice.precedent-bank`.
- **`RE Can we terminate under clause 14 - advice.eml`** — rejected. Advice in the sense a person means
  it, none of the three structures. Handed back to `law_practice.matter-correspondence` explicitly, so
  that row is not stripped of its most common file by a vocabulary grab.
- **`Ellis and Co - Opinion on my redundancy claim.pdf`** — rejected as the under-firing fixture. Every
  structural signal present; the holder is the **advisee**. `legal.personal-legal-matters`.
- **A legal-research memo with a covering line naming a reader** — rejected as a boundary I could have
  taken and did not. Kept for `law_practice.legal-research`; recorded in `needs_llm` as genuinely hard.
- **A settlement advice, an opinion on quantum inside a mediation position paper, a due-diligence report's
  legal-issues section** — rejected. Each is a section of a neighbour's artefact, and claiming a *section*
  would be the row committing the exact stage-error it was charged with.
- **An engagement letter's scope paragraph** — rejected; `law_practice.engagement-terms` owns the
  instrument that creates the engagement, and scope is a slot on it.
- **Client alerts, published firm briefings and know-how bulletins** — rejected. Addressed to nobody,
  relied on by nobody, and their residual is Reading Inbox.

## Reciprocal boundaries, with the same fixture named on both sides

- **`law_practice.conflicts-check`** — the landed row named the fixture first and routed it to me in its
  own words: `Legal opinion - conflict of interest - Hartley board.docx`, *"the single easiest mistake to
  make on vocabulary alone."* **Their side:** a screening record is about whether the *practice* may act
  and carries a search table with a hit column, a decision slot and an approver. **My side:** this is
  about the *client's* legal position and carries an addressee, an analysis and recommendations, with
  none of those four slots. I authored `collides_with` back at them so the mutex is reciprocal in the
  graph, not only in prose.
- **`law_practice.legal-research`** — same fixture, `Advice on merits and quantum - Hartley v Nash -
  counsel.pdf`. **Their side:** the authorities survey and the internal analysis that produced the
  position. **My side:** the document a named reader may rely on. Where a research note carries a
  covering line naming a reader, the seam is genuinely blurred; recorded as `needs_llm`, not smoothed.
- **`law_practice.matter-correspondence`** — same fixture, `RE Can we terminate under clause 14 -
  advice.eml`, and separately the combined instructions-plus-advice PDF. **Their side:** everything
  exchanged in running text, including advice spoken and typed. **My side:** the addressed instrument
  with the assumptions grammar. NJ-OA-1 records the combined-PDF case, which neither of us can settle.
- **`law_practice.precedent-bank`** — same fixture, `PRECEDENT - Legal opinion (firm standard) - v3.docx`.
  **Their side:** party and execution slots deliberately empty. **My side:** an addressee block with a
  real name in it. The schema anchor already reserved blank-slot instruments to them; I take nothing back.
- **`law_practice.orders-and-judgments`** — same fixture, the Supreme Court opinion. **Their side:** a
  tribunal caption, a bench and an operative disposition. **My side:** an author firm, an addressee and
  a reliance clause. The word is shared; not one slot is.
- **`career.consulting-client-engagement`** — same fixture, the Nash Advisory report. **Their side:**
  prepared-for and prepared-by roles, milestones and acceptance, which `legal.practice-matter-file`
  already stated from its side and I restate identically rather than re-litigate. **My side:**
  assumptions-not-verified plus qualifications plus a scope-of-law slot.
- **`legal.personal-legal-matters`** — same fixture, the Ellis and Co opinion. **Their side:** the holder
  is the addressee and no practitioner-side apparatus exists. **My side:** the holder authored it.
- **`finance` (`also_holds_with`, not a collision)** — same fixture, `Response to auditors request for
  information - Hartley Group - FY2026.pdf`. It is audit evidence on finance's own evidence *and* an
  addressed reliance-bearing statement on mine: `A file may validly belong to more than one accepted
  group`. Also relevant to the tax opinion, where the reciprocal is sharper — **`finance.tax-filings`
  owns the filed return**, a form issued by a taxing authority with schedules; **I own the opinion
  supporting the position taken in it**, a letter with assumptions. Neither converts into the other.

**Neighbours considered and deliberately not given an edge:** `law_practice.due-diligence` (a legal-issues
schedule per document reviewed is a different structure, and claiming it would be claiming a section);
`law_practice.regulatory-submission` (a submission asks; an opinion states — and a regulator-addressed
opinion is mine only when the assumptions grammar is present); `law_practice.settlement` (advice on
settlement is a member of its episode, not a copy of my artefact); `research.reading-library` (I route
published material to Reading Inbox rather than claim a mutex with a schema whose evidence is a
bibliography); `identity` (an opinion names people but is never identity evidence).

## Fields and dimensions

`fields: []` — mandatory: `law_practice` declares none under PR-6 and a template may only reuse its
schema's fields. `dimension_order: []` and `time_first: false` follow.

`proposed_fields` contains exactly one entry, **`addressee`**, and I attached its own defeat argument
rather than advocating for it. The hole is real — the addressee is neither `client` (the document
distinguishes them, often in terms), nor `our_firm` (the author half), nor `subject_of_record` (the
person a record is *about*; on an enforceability opinion the subject is an instrument and the addressee
is a bank, two slots on one page). But an addressee is a slot on ordinary correspondence too, so a key
named for it risks becoming a roster-wide synonym for `recipient`. **My stated preference is that R1c
DECLINE and keep the addressee a literal observation that never becomes a fact** — which is what the row
does today and can do forever. I minted nothing and I reused nothing I did not need: the anchor's six
proposals (`client`, `our_firm`, `project`, `work_type`, `subject_of_record`, `fiscal_period`) cover
everything else this row would ever want, and I add no seventh beyond the one above.

**Dimensions I refused, and this is where I differ from the anchor's held-as-prose recommendation.** The
axis this situation most obviously offers is the **addressee**, and it must be refused *harder* than the
client axis the anchor already refused: a client-named branch discloses that a named person is in a
matter, but an addressee-named branch discloses a named bank, auditor or regulator **and the transaction
they are party to**, to a reader who is not the client and never consented — against `The default posture
must therefore be local-first and data-minimizing.` The second refusal is subtler and I would not have
caught it without writing the row: the **reliance level** looks harmlessly non-identifying and is worse
than it looks, because a folder named for a graded legal confidence sorts a corpus by how weak its
positions are, and every later process reads it. Not time-first: four unrelated dates sit on one page
(speaks-as-of, the instrument's date, delivery, filesystem), nothing here is capture-based, and a
time-first order would scatter one bring-down lineage across calendar folders.

## Grouping

The characteristic group is a **lineage**, which is unusual in this family: one opinion across draft,
executed, bring-down, reliance extension and withdrawal, joined by the later documents' **own explicit
reference** to the earlier one's date and addressee — never a `-final` suffix. Then the closing set from
several author firms under one transaction reference, which is `The documents are content-incoherent but
purpose-coherent` in its most literal form: a capacity opinion, a tax opinion and a foreign-law opinion
say entirely different things and exist for one event. `It should not form a supported group when there
is no valid anchor`, and a lone opinion with nothing around it is a complete, protected, ungrouped file.

The non-grouping reason I want on the record because this row invites it: **never group by shared
addressee.** One agent bank is the addressee of hundreds of unrelated opinions, and that folder would
name a financial institution and enumerate every deal it is in.

## NEEDS-JOSEPH

- **NJ-OA-1 — the combined instructions-and-advice PDF.** The schema anchor's COUNSEL-INSTRUCTION signal
  and this row's advice structure fire on the same bytes when a front sheet and the returned advice are
  bound into one file. Alternatives: (a) `law_practice.matter-correspondence` holds the combined artefact
  and this row holds only free-standing advice; (b) this row holds it and correspondence holds only the
  transmitting note; (c) it is a legitimate two-template candidate and P9 shows both. I did not guess.
- **NJ-OA-2 — `addressee`.** Decline and keep it an observation (my preference), or adjudicate it once
  roster-wide with `destination_eligible` seeded false. Do not permit `relying_party`, `recipient_role`,
  `opinion_addressee` or `reliance_party` as variants.
- **NJ-OA-3 — the detached-conclusion rule needs a home above this row.** "A conclusion travels with its
  assumptions and qualifications or it does not travel" is a *composition* constraint on dossier
  building, and it generalises well beyond opinions (a diagnosis without its differential, a valuation
  without its basis). It is stated here because this row found it, but a per-template rule will not bind
  the summariser. P7 or the dossier contract should own it.
- **NJ-OA-4 — reliance level as a stored fact.** A document that grades its own confidence is unusual and
  genuinely useful for retrieval, and I judged it too disclosive to file on. Whether it may be *stored*
  as an observation while being barred from any dimension is a decision above this row.

## Self-verification

`python3 -m json.tool` parses the node. Key set matches the landed siblings' shape. All eight edge ids
were confirmed against `roster.json` / existing node files (`law_practice.legal-research`,
`.precedent-bank`, `.orders-and-judgments`, `.matter-correspondence`, `.conflicts-check`,
`career.consulting-client-engagement`, `legal.personal-legal-matters`, `finance`); all five
`falls_through_to` names are §7.3 residuals. Every `file_examples.source_type` is in `SOURCE_TYPES`.
No file example writes a folder path as a fact. No thresholds, no counts, no handling classes. Every
quotation was grep-verified verbatim before use, and the one I could not verify was dropped rather than
paraphrased inside quote marks. I wrote only my two assigned files.

## R1b — edge-signal repair

`collides_with` and `also_holds_with` were landed as bare id strings. Per `_CONTRACT.md` and
CONNECTION.md's edge table (`collides_with` … *"Must carry `signal`: the discriminating evidence"*,
read by P6 activation step 3 and the P8 validator), a bare id records *that* two rows collide but not
*how to tell them apart*, which is the only part the engine can act on. All eight entries are now
`{"domain", "signal"}` objects. No neighbour was added and no entry was dropped.

Each signal names the ONE evidence item both rows would claim, then states the boundary in both
directions. The fixtures, and the reason each shared item is *not* self-discriminating:

- **`law_practice.legal-research`** — one memorandum answering a legal question with a covering line
  naming a reader. A named reader, a citation list and the word `advice` sit on both sides; only the
  addressee-and-reliance pair plus assumptions/qualifications/scope-of-law is mine.
- **`law_practice.precedent-bank`** — one model opinion letter carrying the *full* opinion grammar.
  This is the collision where my headline signal is worthless: the precedent bank's most-used member
  IS a stripped opinion. Filled-versus-blank addressee/date/conclusion slots is the whole test.
- **`law_practice.orders-and-judgments`** — one PDF titled `opinion`. Discriminated by who issued it
  (tribunal caption and binding effect vs. practitioner letterhead, addressee and reliance clause),
  never by topic. The one design span I quote is grep-verified verbatim at line 45 of
  `planning/00-database-agent-product-design.md`: *"Topic answers what a file is about, while purpose
  answers what the file was for."* I did not attach a `design_cite` because that file carries no
  section headings, and inventing a `§N.N` to satisfy the exemplar's format would be a fabrication.
- **`law_practice.matter-correspondence`** — one advice letter to the client. The advice *content* is
  common to both, so it is evidence for neither; labelled opinion structure vs. running prose decides.
- **`law_practice.conflicts-check`** — `Legal opinion - conflict of interest - Hartley board.docx`,
  named identically in both memos. The phrase `conflict of interest` is the shared item and decides
  nothing; the four screen slots (prospective-client, searched-parties, search-result, approver) vs.
  the addressee-and-reliance pair decides.
- **`career.consulting-client-engagement`** — one professional deliverable with an addressee block and
  a use-limitation clause. The clause is universal across professional deliverables, so my *primary*
  signal is explicitly disqualified against this neighbour; the two-organization producer/recipient
  pair vs. the assumptions/qualifications/scope-of-law co-occurrence decides.
- **`legal.personal-legal-matters`** — literally the same bytes in two files. Every content signal is
  identical; only the holder's ROLE on the page discriminates, and abstention is correct when that
  side cannot be cited.
- **`also_holds_with` → `finance`** — the auditor-request response, legitimately held by both as an
  opinion artefact and as audit evidence. Coactivation, not a mutex.

Nothing was removed. I twice reached for `law_practice.conflicts-check` as a candidate deletion
(an opinion has no searched-parties list; a screen has no addressee block) and was wrong both times:
the collision is not structural but *lexical*, and the landed conflicts-check memo names the exact
fixture and routes it here. Recording that reasoning because the next reviewer will have the same
instinct.

### For R1c — cross-row, not editable from here

1. **`law_practice.conflicts-check` does not reciprocate.** Its `collides_with` lists
   `client-intake`, `legal`, `career.consulting-client-engagement`,
   `business_operations.organisational-records`, `hr.employee-relations`, `precedent-bank` — not this
   row — even though its own memo names the shared fixture and routes it here in prose. My earlier
   "I authored `collides_with` back at them so the mutex is reciprocal in the graph" was true only of
   my side. Under CONNECTION.md's post-migration reciprocity gate this is a directed-only edge and
   will fail. The neighbour should add `law_practice.opinions-advice`.
2. **`law_practice.matter-correspondence` is `refuse_node: true`** with empty `collides_with`, so it
   can never reciprocate. The evidence-item competition is real, so I did not delete the edge, but
   R1c must decide whether it retargets to the `law_practice` schema (which absorbed that row's
   coverage) or is dropped as pointing at a refused destination.
3. **`also_holds_with` may be schema-only.** CONNECTION.md's edge table and `_CONTRACT.md` rule 173-177
   say `also_holds_with` *"joins schemas only"*, but this row is a `template` and its coactivation
   partner `finance` is a `schema`. The coactivation itself is real (the auditor-request response).
   Whether a template may carry the edge at all, or whether it must be lifted to the `law_practice`
   schema, is above this row.
4. **Three collision targets have no node file yet** — `law_practice.legal-research`,
   `.precedent-bank`, `.orders-and-judgments` exist as `roster.json` rows only. Their signals here are
   written against their roster `one_line_hint`s; when those rows land, their authors should be handed
   these fixture names so the reciprocal signal is the same fixture and not a second invented one.
