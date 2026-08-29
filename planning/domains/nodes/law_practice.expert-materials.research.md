# Research memo — `law_practice.expert-materials`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.expert-materials.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept.** The row survives the node test on the first leg alone — its activation structure is not the
schema's default and, more sharply, **the schema's default template does not fire on this row's anchor
fixture at all**. It also carries a privacy rule the default cannot derive and a dimension prohibition
the default does not state. `fields: []`, `dimension_order: []`, `time_first: false`, one endorsed
`proposed_fields` entry (`subject_of_record`, no mint), nine `collides_with` objects, four NEEDS-JOSEPH.

## The charge — the strongest case that this row should not exist

Stated at full strength before it is answered, because four of the seven prosecution arguments are
correct as far as they go and are conceded in the JSON rather than argued away.

**1. It is a `work_type` value wearing a node's clothes.** The `law_practice` schema's own
`work_types` list contains, verbatim, `"expert instruction, expert report and expert correspondence"`.
The schema then wrote the indictment itself, in its `work_type` proposal: *a template row justified
only by holding a different legal document kind is the schema's default template with a narrower
filename filter.* On its face this row is that.

**2. It is a role name, and the schema already struck it.** `law_practice`'s `never_alone` list
strikes "A LAW-FIRM, CHAMBERS, PRACTITIONER, COURT, TRIBUNAL, REGULATOR, **EXPERT**, CLIENT or
ADVERSE-PARTY NAME ALONE", and rules that *a role name cannot carry a schema*. If a role name cannot
carry a schema, why may it carry a template? This is the strongest single argument against the row.

**3. It is a lifecycle stage.** Instruction → materials → draft → signed → served → questions →
joint statement is a sequence inside one matter, and a sequence is not a node.

**4. It is a duplicate of two landed neighbours and one unlanded sibling.**
`law_practice.depositions-testimony` already owns the specialist's examination.
`law_practice.evidence-exhibits` already owns enumerated attachment sets.
`law_practice.opinions-advice` will own reasoned professional documents inside a matter.
What is left over may be nothing.

**5. It is a row defined by an absence** — a report that is *not* counsel's advice, produced by
someone who is *not* the practitioner side. Rows defined by absence do not activate.

**6. Its evidence is never-alone all the way down.** A name, post-nominal letters, a discipline, a
professional body, and the word "expert" — every token this row would reach for is struck.

**7. Its material belongs to other schemas anyway.** The medical bundle is `medical`'s, the account
statements are `finance`'s, the site photographs are `photos`'s, the invoice is `finance`'s, the
permission order is `legal`'s. Strip those out and the row may hold only a PDF with a signature.

## The defeat

Charges 1, 2, 5 and 6 are conceded and written into the JSON as constraints. Charges 3, 4 and 7 are
answered. The row is not saved by the word "expert"; it is saved by four labelled slots.

### The deletion test, run explicitly

Delete every entity name and every document-type word from `Expert report - Dr M Patel - signed -
2026-05-14.pdf`. What survives is: **(i)** a section reciting who instructed the producer and what
questions were asked; **(ii)** a qualifications-and-experience section *about the producer*;
**(iii)** an enumerated list of material considered; **(iv)** a signed declaration whose printed
words state a duty owed to a court. Four labelled slots survive with every name removed. That is a
structure, and it is not the word "expert".

### Leg 1 — detection signals differ from the schema's default. They differ by *not firing*.

The `law_practice` default requires **both** legs of a matter-anchored two-role structure: an exact
matter reference repeated across artefacts, **and** at least one artefact whose own labelled slots
separate a practitioner-or-firm role from a client role.

The anchor fixture has **neither role of that pair**. Its role pair is *instructing side* and
*producer*, and the producer is expressly marked as **not** the practitioner side — which matters
because the default's internal-work-product signal requires, in its own words, "a producer marker for
the practitioner side". The client is frequently not named on the report at all; on a single joint
appointment there is no "our side" to name, and on an opposing party's served report the instructing
firm is someone else's. So the concrete under-fire is: **a served opposing expert report, arriving
with no matter reference belonging to the holder's firm and no client slot, activates nothing under
the default.** This row activates it on the declaration, the qualifications section and the materials
enumeration.

Two further structures have no analogue anywhere on the roster:

- **The joint statement.** Two *separately instructed, adversely aligned* producers signing one
  document that partitions itself into matters agreed and not agreed. The schema's two-role default
  cannot express two producers on opposite sides of one page. Nothing else in `law_practice` produces
  it, and nothing outside it does either.
- **The declaration slot.** A duty running to a party who instructed nobody and pays nothing. Every
  other professional document in this family runs its duty inward, to the retainer.

**Against the closest sibling, `law_practice.opinions-advice`:** counsel's advice has no
qualifications section, no materials-considered enumeration, and no duty declaration outside the
retainer, and it is produced *not* to be disclosed. This row's document has all three and is produced
in order to be handed over. Topic separates neither — 00: *"Topic answers what a file is about, while
purpose answers what the file was for."*

**Against the schema's counsel-instruction signal** (the sharpest intra-schema duplication risk, since
the default already recognises "an INSTRUCTING slot with an INSTRUCTED or COUNSEL slot ... enclosing a
numbered bundle index"): the default's third slot is a **named advisee** and the advice runs to the
instructing side; here the third slot is a **duty to a tribunal**, the enclosure schedule is a
*materials list scoped to a future report* rather than a bundle index, and the body is a question set
rather than a request for a position. Conceded honestly: this is the row's thinnest discrimination and
it is NJ-EXP-1.

### Leg 2 — privacy rules differ, and they differ in a direction the default cannot derive

The schema's privacy claim is a consent claim: it protects *a third party who never chose this
filesystem and cannot consent* — a client, an adverse party, a witness, a deponent, an accused, a
child. This row protects **three distinguishable people, and only one of them is that person**.

- **The instructing side's strategy.** An instruction letter states what the matter turns on. A
  commented draft shows what changed before signature. The existence of an instructed specialist
  whose report was **never served** is itself a strategic fact. The default's privacy rule is about
  someone else's identity; this is about the holder's own reasoning.
- **A fourth person.** The material behind an opinion is routinely another schema's primary record
  about someone who is neither the holder, nor the client, nor the specialist — a claimant's clinical
  bundle, a party's account statements, a child's assessment protocols. That material co-activates a
  **safety domain on its own evidence**, and 00 is explicit that *"Finance, identity, medical, and
  legal material should be implemented first as safety domains, meaning the system detects and
  protects them before any cloud or automated placement decision is allowed."* Membership of a
  materials list neither creates nor erases that. No other `law_practice` row routinely holds a
  fourth person's primary safety record as a *dependency* of its own artefact.
- **The specialist.** A named professional, not a vulnerable party — they consented to the
  engagement, so the schema's consent argument does not reach them. They are protected for a
  different reason: their file carries a fee schedule and a **prior-testimony list**, which is a
  cross-matter bridge *written inside a single file*. The schema suppresses cross-matter bridging as
  an inference rule across files; a self-declared index of other matters inside one file is a case
  its wording does not literally reach (NJ-EXP-3).

One correction the default never has to make: **a served report is not public.** Service on an
opponent is a professional act, not publication. The schema strikes "PUBLIC AVAILABILITY ... as proof
that the local copy or its surrounding matter context is low-sensitivity"; this row restates that for
the one artefact family where the mistake is most inviting, and adds that a served report says nothing
about the draft, the instruction, the correspondence, or the material behind it (NJ-EXP-4).

### Leg 3 — the recommended dimensions differ by adding a prohibition the default cannot derive

The schema's recommendation, held as prose: client (only where genuinely multi-client and explicitly
approved), then matter, then document function, then period; and *no named third party may ever be a
level*, for the consent reason above.

The natural first axis of an expert file is neither the client nor the function. **It is the
specialist** — that is how practitioners actually keep it, and it is the level a template author who
has not read this row will propose. The specialist is not covered by the schema's prohibition,
because they are a consenting paid professional. This row therefore forbids it for two reasons the
default does not state:

1. **Strategic disclosure.** A specialist-named branch publishes which discipline a matter turned on,
   which specialist the firm chose, and — worst — which specialists were instructed and *not* used.
2. **Cross-matter bridging materialised as a path.** A specialist level places two unrelated matters
   under one parent in the filesystem, making the exact bridge the schema suppresses in facts into a
   permanent structure that every later process reads.

The within-engagement lifecycle (instruction → draft → signed → questions → joint statement) is also
refused as a level: it is a version series and a stage, and 00 resolves version differences as a fact.
Function still follows the matter for 00's own reason — *"A work type such as Homework 3 is meaningful
only after the course is known, and a course code may require the school or term to disambiguate
it."* Not time-first: *"For document and record domains, project, function, or subject usually comes
before time because putting year first scatters related work across calendar folders."* Instruction
date, inspection date, report date, service date and filesystem date mean five different things here.
Whatever lands stays a recommendation — *"The system recommends an order based on the domain template,
but the user can reverse, remove, add, or flatten dimensions."*

**Verdict: three legs, three independent differences. Accept.**

## Files considered and rejected

Named because each is a tempting false positive that a lazier version of this row would have claimed.

| File | Why it is not this row's evidence |
| --- | --- |
| `Order granting permission for expert evidence - Hartley v Nash.pdf` | Caption + operative paragraphs is `legal`'s deterministic signal; `legal` is a safety domain and runs first. The word "expert" appears four times *inside someone else's structure* — a document-type word, struck. |
| `Expert invoice - 41127-0006 - March 2026.pdf` | An issuer-and-billed-to block is `finance`'s discriminating structure. A matter-reference column on a disbursement ledger is the schema's own time-and-disbursement default, not this row. |
| `Firm panel list of approved experts.xlsx` | A portfolio table across many matters with no instruction, no report and no matter. It is a cross-matter index — the exact artefact this row's `never_alone` strikes. Routes to the schema default / Review Later. |
| `Peer-reviewed paper cited at para 4.12.pdf` | Published reading material. It becomes a candidate member only through a report's own materials enumeration naming it by exact reference; never by co-location or a shared author name. Otherwise Reading Inbox. |
| Practice guide / training-course specimen expert report | Carries the declaration wording *because that is what it is teaching*. `needs_llm` handles it; the discipline publishes its own exemplars unusually freely. |
| `Site inspection ... IMG_0417.jpg` | `photos` material until a report's own figure reference pulls it in. EXIF `DateTimeOriginal` is evidence, capture date is the fact; the folder name supplies no address. |
| `Instrument run export - batch 22-118.dat` | A readable header naming an operator and a method is not activation. Material *considered*, not *produced*; unattributed without a report. Unsupported or Encrypted. |
| An IME report obtained by an insurer, held by the injured person | The holder is the **subject**, not the practitioner. `legal.personal-legal-matters` / `medical`. This is the schema's own under-firing risk arriving through this row's door. |
| A CPD or accreditation certificate for the specialist | `career`. A professional's own credential record, not matter material. |

## Reciprocal boundaries

Every entry names the same fixture on both sides. Three of these are reciprocals **owed** to landed
rows that already argued against this one; all three are accepted in the neighbour's own terms.

| Neighbour | Same fixture both sides | This row owns | Neighbour owns | Discriminated by |
| --- | --- | --- | --- | --- |
| `law_practice.depositions-testimony` *(owed, landed)* | `Deposition of Dr Mira Patel - expert - Volume I.pdf` | instruction letter, report, materials list, CV, correspondence | the **examination**, on its officer's certificate and errata slot | the artefact, never the person — the shared name is the least useful evidence in the pair |
| `law_practice.evidence-exhibits` *(owed, landed)* | `Appendix 3 - materials considered - Dr Patel.pdf` | an enumeration scoped to **one report** and headed by it | a designator series across documents the producer did not create, closed by a schedule outside any report | whether the list is authored inside the report or applied from outside; foreign control numbers in entries do not move it |
| `construction_property.survey-valuation` *(owed, landed)* | `Building condition report - 14 Priory Road - for Mr and Mrs Hartley.pdf` | the same surveyor's report **with** an instructing-solicitor block, matter reference, materials enumeration or duty declaration | a client-addressed report under the surveyor's own professional basis | those three slots — never the discipline, letterhead or professional-body line |
| `law_practice.opinions-advice` *(unlanded)* | `Advice on quantum - 41127-0006.pdf` | the document with qualifications + materials enumeration + duty declaration, produced to be disclosed | counsel's/the firm's advice to the instructing side, practitioner-side producer marker, none of those three | the declaration slot plus the qualifications section, not the reasoning or the word "opinion" |
| `medical.personal-health-records` | `Claimant medical records bundle - indexed - provided to expert.pdf` | only the enclosure relationship and the report built on it | the clinical record on its own evidence; **safety runs first** | nothing on the bundle itself — the discriminator is the *direction of the claim*; this row co-activates and takes nothing |
| `career.consulting-client-engagement` | `Terms of engagement and fee estimate - Patel Consulting.pdf` | the same shape when scope is a question set for an opinion, or a duty paragraph appears | consulting prepared-for / prepared-by roles, deliverables, milestones, acceptance | the question-set-and-duty structure, not that a consultancy was retained. Same rule sends a bare CV to `career` |
| `legal.practice-matter-file` | `Expert Report - Dr Mira Patel.pdf` (that row's own listed fixture) | the engagement *around* the report, plus activation when it arrives with no representation anchor at all | the report as one member of a practitioner-side matter packet; broader safety-side row, not narrowed here | whether recognition runs through a practitioner-and-client representation or the report's own duty declaration |
| `finance.small-business-bookkeeping` | `Loss calculation model - Patel report appendix.xlsx` | assumption / input / source-reference / calculated-output columns reconciling to a named report | anything with an institution-and-account header, an issuer-and-billed-to block, or a real ledger — including the specialist's invoice | the institution-and-account header, exactly as the schema states the test from its side |
| `research.reading-library` | `Peer-reviewed paper cited at para 4.12 - Patel report.pdf` | the paper only where a materials enumeration names it by exact reference | published reading material with no accepted purpose anchor | the enumeration, never co-location, topic match or a shared author name |

`also_holds_with` is **empty**: CONNECTION §5 makes it schema ↔ schema only and this row is a
template. The intended coactivations (`medical`, `finance`, `photos`, `legal`, `identity`) are
recorded per-fixture as `also_schema` and flagged here for R1c.

## The collision fixtures

Two, because they fail in opposite directions.

**Over-firing — `Building condition report - 14 Priory Road - for Mr and Mrs Hartley.pdf`.** Every
superficial marker of an expert report is present: a professional-body line, a qualifications
paragraph, an inspection date, a methodology and extent-of-inspection section, limitations,
assumptions, reasoned conclusions, a signature, a costed schedule. It is not this row's.
**Discriminated by three absences that are structural, not lexical:** no instructing-side block, no
materials-considered enumeration, no declaration whose duty runs outside the retainer. It is
addressed to the occupiers on the surveyor's own terms. `construction_property.survey-valuation`
owns it and said so first. The same surveyor writing the same building up *for proceedings*, on a
solicitor's instruction with a duty declaration, produces this row's file instead — so the discipline
decides nothing.

**Never-alone — `Expert Witness CV and Testimony History - Dr M Patel.pdf`.** A person's name plus two
document-type words, which is the row-defined-by-a-name trap in its purest form. A CV is `career`
material by default and becomes this row's evidence only as an appendix to, or enclosure of, a
separately evidenced instruction or report. Its prior-engagement table is a ready-made cross-matter
bridge and reading it is forbidden regardless of how well it would work.

## Grouping without copied facts

The row's distinctive anchor is the **materials-considered enumeration**: a list authored *inside*
the file by its own producer, which makes it an explicit reference rather than a similarity — what
00 requires, since *"It should not form a supported group when there is no valid anchor, when the
graph is connected only by embeddings, when one high-frequency entity acts as the only bridge"*. It
supports candidate membership over items the producer did not create; those items keep their own
schema's facts, and several are protected records in their own right — *"A file may validly belong to
more than one accepted group"*. One engagement within one matter is content-incoherent and
purpose-coherent, 00's own licence: *"The documents are content-incoherent but purpose-coherent."*

Four things that are **not** grouping reasons here, listed because this row's own content invites all
four: a shared specialist name across matters; the prior-testimony or publications list inside the
file; a shared discipline, method or test facility; and a download session — *"A session should never
be treated as proof of topic"*.

## Fields

`fields: []` — the schema owns the fields and declares none under PR-6. One `proposed_fields` entry,
and it is an **endorsement, not a mint**: `subject_of_record`, already proposed by
`clinical_practice`, adopted by `nonprofit` and adopted by the `law_practice` schema. This row adds a
case none of the three faces — the producing non-party, who is neither holder, client, adverse party
nor subject. `expert` and `author_role` are refused explicitly so no sibling reaches for them: both
encode a role name in a key, which is the charge this row spent its first section answering.

## NEEDS-JOSEPH

- **NJ-EXP-1 — the `opinions-advice` seam** (weakest joint; neighbour unlanded). A firm's internal
  memorandum obtaining a technical view, and a specialist's preliminary letter before formal
  instruction, carry neither a duty declaration nor a practitioner-side producer marker. Alternatives:
  (a) this row takes anything whose producer is expressly not the practitioner side — simple, drags in
  every consultancy note; (b) the neighbour takes everything without a duty declaration and this row
  narrows to declared evidence — clean, loses the instruction letter, which is this row's *first*
  artefact; (c) both stay under the schema default until the neighbour lands. The JSON implements
  (b)'s discriminator in its edge; this memo prefers (c) as the adjudication.
- **NJ-EXP-2 — the fourth person.** May a materials enumeration create a reviewable candidate edge
  *onto* a protected medical or finance record, when the enumeration could then be used to enumerate
  protected files? Alternatives: allow the edge but never surface the member list; allow it only on
  explicit user approval; forbid it and leave the enumeration as unlinked text. The row assumes the
  middle and says so rather than assuming silently.
- **NJ-EXP-3 — a cross-matter index inside one file.** The schema's suppression is written as a rule
  about inference *across* files. A prior-testimony list is a self-declared index of other matters
  *within* one. This row strikes it in `never_alone`, but the rule belongs at schema or contract level
  rather than being re-argued by every template that happens to hold one.
- **NJ-EXP-4 — served but not public.** Nothing in the design docs distinguishes
  deliberately-disclosed-to-one-party from publicly-available, and P7 owns handling. Alternatives:
  treat every served document as ordinary protected material (this row's assumption), or add a
  disclosed-to-a-named-counterparty observation — a new observation kind, which a placeholder template
  must not mint.

## Recommendations for R1c (cross-row, not actioned here)

1. Three landed rows owe/are owed reciprocals with this one and now have them from this side:
   `depositions-testimony`, `evidence-exhibits`, `survey-valuation`. No neighbour file was edited.
2. `law_practice.pro-bono` sets `also_schema: "law_practice.expert-materials"` on one fixture. That
   field takes a **schema** id elsewhere in the family, not a template id; flagged for R1c as a
   probable defect in that row. Not touched.
3. When `law_practice.opinions-advice` is written, it must answer NJ-EXP-1 in the same fixture terms.
4. `also_holds_with` intent for R1c: `law_practice` ↔ `medical`, `finance`, `photos`, `identity` —
   raised from this row's fixtures, to be authored schema-side if at all.

## Self-verification

- `python3 -m json.tool` parses the node file.
- Key set and key **order** match the landed sibling `law_practice.depositions-testimony.json` exactly.
- Every `collides_with` / `also_holds_with` entry is an object with `domain`, `signal`, `provenance`;
  every `signal` names one shared fixture and both sides of the discrimination.
- All nine neighbour ids verified present in `planning/domains/roster.json`.
- Every quotation `grep -F`-verified verbatim against `planning/00-database-agent-product-design.md`
  before use; `design_cite` left `null` because no span was verified *as a citation span*.
- `falls_through_to` uses four of 00's residual homes; `fields: []`; no thresholds; no handling class;
  sensitivity is `potentially_sensitive` only.
- Only the two assigned files were written. No roster, schema, canonical-fields, neighbour, `src/`,
  `check.py` or SPEC file was touched.
